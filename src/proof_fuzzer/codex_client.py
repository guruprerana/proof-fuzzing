"""Codex SDK client helpers for proof fuzzing."""

from __future__ import annotations

from dataclasses import dataclass, fields, is_dataclass
from datetime import datetime, timezone
from enum import Enum
import hashlib
import json
import os
import queue
from pathlib import Path
import threading
import time
from typing import Any, Mapping

from .usage import LLMUsage


DEFAULT_CODEX_MODEL = "gpt-5.5"
DEFAULT_CODEX_REASONING_EFFORT = "medium"
DEFAULT_CODEX_SANDBOX = "read_only"
VALID_CODEX_REASONING_EFFORTS = {"low", "medium", "high", "xhigh"}
VALID_CODEX_SANDBOXES = {"read_only", "workspace_write", "full_access"}
ISOLATED_WORKSPACE_INSTRUCTIONS = """This Codex call runs in a dedicated per-call workspace.
Treat the current working directory and its descendants as the entire available filesystem.
Do not inspect parent or sibling directories, follow paths outside this workspace, or use
absolute paths outside it. Do not use network or internet resources. Task instructions are stored
in prompt.txt; any supplemental task inputs named there are separate files in the same directory.
Read those files directly and use only files inside this workspace to complete the task."""

_RESERVED_WORKSPACE_FILES = {"error.txt", "metadata.json", "prompt.txt", "response.txt"}


@dataclass(frozen=True)
class CodexChatResult:
    """Result from a Codex SDK run."""

    content: str
    reasoning: str = ""
    finish_reason: str = ""
    raw_response: object | None = None
    usage: LLMUsage | None = None


class CodexCallTechnicalError(RuntimeError):
    """A local timeout/output guard stopped a call, independent of its verdict."""


class OutputRepetitionGuard:
    """Detect long periodic suffixes in agent output, across streaming deltas."""

    def __init__(self):
        self.item_id = None
        self.tail = ''
        self.unchecked = 0

    def update(self, item_id, delta):
        if item_id != self.item_id:
            self.item_id, self.tail, self.unchecked = item_id, '', 0
        self.tail = (self.tail + delta)[-4096:]
        self.unchecked += len(delta)
        if len(self.tail) < 1024 or self.unchecked < 128:
            return False
        self.unchecked = 0
        for width in range(1, 129):
            repeats = max(32, 1024 // width + 1)
            if self.tail.endswith(self.tail[-width:] * repeats):
                return True
        return False


def _timed_events(turn, timeout_seconds):
    """Use a reader thread so a silent stream cannot defeat the wall-clock limit."""
    events = queue.Queue()
    stopped = threading.Event()

    def read():
        stream = None
        try:
            stream = turn.stream()
            for event in stream:
                if stopped.is_set():
                    break
                events.put(('event', event))
        except Exception as error:
            events.put(('error', error))
        finally:
            try:
                close = getattr(stream, 'close', None)
                if close is not None:
                    close()
            finally:
                events.put(('end', None))

    reader = threading.Thread(target=read, daemon=True)
    reader.start()
    deadline = time.monotonic() + timeout_seconds
    try:
        while True:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise CodexCallTechnicalError(f'Call exceeded {timeout_seconds:g} seconds')
            try:
                kind, value = events.get(timeout=remaining)
            except queue.Empty:
                raise CodexCallTechnicalError(f'Call exceeded {timeout_seconds:g} seconds') from None
            if kind == 'end':
                return
            if kind == 'error':
                raise value
            yield value
    finally:
        stopped.set()


class CodexProofFuzzerClient:
    """Small Codex SDK client matching the proof-fuzzer LLM protocol.

    By default, every ``complete`` call creates a fresh Codex thread. That keeps
    mutation, blind judging, mutation checking, and judge-error checking isolated
    when this client is used by the evolutionary loop. Threads are ephemeral by
    default so proof-fuzzer calls are not materialized in Codex chat history.

    When ``workspace_root`` is set, each call runs from a new child directory
    containing only that call's prompt and bookkeeping files. It uses Codex's
    built-in read-only sandbox, denied approvals, disabled web search, and
    fresh-thread behavior. The task instructions additionally restrict the model
    to the current call directory.
    """

    def __init__(
        self,
        *,
        model: str = DEFAULT_CODEX_MODEL,
        reasoning_effort: str = DEFAULT_CODEX_REASONING_EFFORT,
        sandbox: str = DEFAULT_CODEX_SANDBOX,
        cwd: str | None = None,
        workspace_root: str | Path | None = None,
        approval_mode: str = "deny_all",
        service_tier: str | None = None,
        base_instructions: str | None = None,
        developer_instructions: str | None = None,
        fresh_thread_per_call: bool = True,
        ephemeral_threads: bool = True,
        log_events: bool = False,
        mutation_file_editing: bool = False,
        call_timeout_seconds: float | None = None,
        detect_repetitive_output: bool = False,
        technical_retries: int = 0,
        codex_factory: Any | None = None,
        sdk: Any | None = None,
    ):
        if reasoning_effort not in VALID_CODEX_REASONING_EFFORTS:
            allowed = ", ".join(sorted(VALID_CODEX_REASONING_EFFORTS))
            raise ValueError(f"Unknown Codex reasoning effort {reasoning_effort!r}; expected one of: {allowed}")
        if sandbox not in VALID_CODEX_SANDBOXES:
            allowed = ", ".join(sorted(VALID_CODEX_SANDBOXES))
            raise ValueError(f"Unknown Codex sandbox {sandbox!r}; expected one of: {allowed}")
        if workspace_root is not None and sandbox != "read_only":
            raise ValueError("Per-call Codex workspaces require sandbox='read_only'.")
        if workspace_root is not None and approval_mode != "deny_all":
            raise ValueError("Per-call Codex workspaces require approval_mode='deny_all'.")
        if workspace_root is not None and not fresh_thread_per_call:
            raise ValueError("Per-call Codex workspaces require fresh_thread_per_call=True.")
        if workspace_root is not None and cwd is not None:
            raise ValueError("Set either workspace_root or cwd for Codex, not both.")
        if log_events and workspace_root is None:
            raise ValueError("Event logging requires isolated per-call workspaces.")
        if mutation_file_editing and workspace_root is None:
            raise ValueError("Mutation file editing requires isolated per-call workspaces.")
        self.mutation_file_editing = mutation_file_editing
        if call_timeout_seconds is not None and call_timeout_seconds <= 0:
            raise ValueError('call_timeout_seconds must be positive')
        if technical_retries < 0:
            raise ValueError('technical_retries must be nonnegative')
        if (call_timeout_seconds is not None or detect_repetitive_output or technical_retries) and not log_events:
            raise ValueError('Call safeguards require event logging')
        self.call_timeout_seconds = call_timeout_seconds
        self.detect_repetitive_output = detect_repetitive_output
        self.technical_retries = technical_retries

        self.model = model
        self.reasoning_effort = reasoning_effort
        self.sandbox = sandbox
        self.cwd = cwd
        self.workspace_root = Path(workspace_root).resolve() if workspace_root is not None else None
        self.approval_mode = approval_mode
        self.service_tier = service_tier
        self.base_instructions = base_instructions
        self.developer_instructions = developer_instructions
        self.fresh_thread_per_call = fresh_thread_per_call
        self.ephemeral_threads = ephemeral_threads
        self.log_events = log_events
        self.codex_factory = codex_factory
        self.sdk = sdk
        self._codex_context: Any | None = None
        self._thread: Any | None = None
        self.last_result: CodexChatResult | None = None
        self.last_reasoning = ""
        self.last_workspace: Path | None = None
        self._workspace_counter = 0
        self._workspace_lock = threading.Lock()

    def complete(self, prompt: str) -> str:
        """Return only final content, matching the proof-fuzzer LLM protocol."""

        return self.complete_with_reasoning(prompt).content

    def complete_with_reasoning(self, prompt: str) -> CodexChatResult:
        """Return final content plus available raw Codex turn data."""

        started = time.monotonic()
        effective_sandbox = self.sandbox
        if self.fresh_thread_per_call:
            if self.mutation_file_editing and prompt.startswith(
                "You are introducing a subtle mathematical error into a proof."
            ):
                instructions, source = _file_mutation_task(prompt)
                effective_sandbox = "workspace_write"
                result = self._run_fresh_thread(
                    instructions, files={"original_proof.md": source}, mutation_source=source,
                )
            else:
                result = self._run_fresh_thread(prompt)
        else:
            result = self._run_reused_thread(prompt)
        usage = _codex_usage(result, elapsed_seconds=time.monotonic() - started)
        chat_result = CodexChatResult(
            content=str(getattr(result, "final_response", None) or ""),
            reasoning="",
            finish_reason=str(getattr(result, "status", "") or ""),
            raw_response=result,
            usage=usage,
        )
        if self.last_workspace is not None and self.workspace_root is not None:
            self._write_workspace_metadata(
                self.last_workspace,
                status=chat_result.finish_reason or "completed",
                sandbox=effective_sandbox,
                usage=usage,
            )
        self.last_result = chat_result
        self.last_reasoning = chat_result.reasoning
        return chat_result

    def complete_with_files(self, prompt: str, files: Mapping[str, str]) -> str:
        """Complete a task whose instructions and inputs live in separate files.

        ``prompt`` is written to ``prompt.txt`` and each mapping entry is written
        beside it. The inline Codex turn contains only a short instruction to read
        those files, so large traces and evolving strategies are not duplicated in
        the transport message.
        """

        return self.complete_with_reasoning_files(prompt, files).content

    def complete_with_reasoning_files(
        self, prompt: str, files: Mapping[str, str]
    ) -> CodexChatResult:
        """Return a result for an isolated, file-backed task."""

        if self.workspace_root is None:
            raise ValueError("File-backed completions require workspace_root.")
        normalized_files = _validate_workspace_files(files)
        started = time.monotonic()
        result = self._run_fresh_thread(prompt, files=normalized_files)
        usage = _codex_usage(result, elapsed_seconds=time.monotonic() - started)
        chat_result = CodexChatResult(
            content=str(getattr(result, "final_response", None) or ""),
            reasoning="",
            finish_reason=str(getattr(result, "status", "") or ""),
            raw_response=result,
            usage=usage,
        )
        if self.last_workspace is not None:
            self._write_workspace_metadata(
                self.last_workspace,
                status=chat_result.finish_reason or "completed",
                sandbox=self.sandbox,
                usage=usage,
            )
        self.last_result = chat_result
        self.last_reasoning = chat_result.reasoning
        return chat_result

    def close(self) -> None:
        """Close the reused Codex context, if one was opened."""

        context = self._codex_context
        self._codex_context = None
        self._thread = None
        if context is not None:
            context.__exit__(None, None, None)

    def _run_fresh_thread(
        self, prompt: str, *, files: Mapping[str, str] | None = None,
        mutation_source: str | None = None,
    ) -> object:
        for attempt in range(self.technical_retries + 1):
            try:
                return self._run_fresh_thread_once(prompt, files=files, mutation_source=mutation_source)
            except CodexCallTechnicalError as error:
                # Never retry based on mathematical verdict or schema parsing.
                if self.last_workspace is not None:
                    (self.last_workspace / 'technical_retry.json').write_text(json.dumps({
                        'attempt': attempt + 1, 'retry_scheduled': attempt < self.technical_retries,
                        'error': str(error), 'prompt_sha256': hashlib.sha256(prompt.encode()).hexdigest(),
                    }, indent=2))
                if attempt >= self.technical_retries:
                    raise

    def _run_fresh_thread_once(
        self, prompt: str, *, files: Mapping[str, str] | None = None,
        mutation_source: str | None = None,
    ) -> object:
        started = time.monotonic()
        sdk = self.sdk or _load_codex_sdk()
        call_cwd = self.cwd
        workspace = None
        run_prompt = prompt
        sandbox = "workspace_write" if mutation_source is not None else self.sandbox
        if self.workspace_root is not None:
            workspace = self._create_call_workspace(prompt, files=files)
            self._write_workspace_metadata(workspace, status="running", sandbox=sandbox)
            call_cwd = str(workspace)
            run_prompt = _workspace_bootstrap(files or {})
        try:
            with self._make_codex_context(sdk, cwd=call_cwd) as codex:
                thread = self._start_thread(codex, sdk, cwd=call_cwd, sandbox=sandbox)
                result = self._run_thread(thread, sdk, run_prompt, workspace=workspace, sandbox=sandbox)
            if workspace is not None:
                self._record_workspace_result(
                    workspace, result, sandbox=sandbox,
                    usage=_codex_usage(result, elapsed_seconds=time.monotonic() - started),
                )
            if mutation_source is not None:
                from types import SimpleNamespace
                content = _read_file_mutation(workspace, mutation_source)
                result = SimpleNamespace(final_response=content, status=result.status, agent_result=result)
        except Exception as exc:
            if workspace is not None:
                self._record_workspace_failure(
                    workspace, exc, sandbox=sandbox,
                    usage=LLMUsage(elapsed_seconds=time.monotonic() - started),
                )
            raise
        return result

    def _run_reused_thread(self, prompt: str) -> object:
        sdk = self.sdk or _load_codex_sdk()
        if self._codex_context is None:
            context = self._make_codex_context(sdk, cwd=self.cwd)
            codex = context.__enter__()
            self._codex_context = context
            self._thread = self._start_thread(codex, sdk, cwd=self.cwd)
        return self._run_thread(self._thread, sdk, prompt)

    def _make_codex_context(self, sdk: "_CodexSDK", *, cwd: str | None) -> object:
        factory = self.codex_factory or sdk.Codex
        codex_bin = os.environ.get("PROOF_FUZZER_CODEX_BIN")
        config = sdk.CodexConfig(cwd=cwd, codex_bin=codex_bin) if cwd or codex_bin else None
        if config is not None:
            return factory(config=config)
        return factory()

    def _start_thread(self, codex: object, sdk: "_CodexSDK", *, cwd: str | None, sandbox: str | None = None) -> object:
        kwargs: dict[str, object] = {
            "approval_mode": _approval_mode_value(sdk, self.approval_mode),
            "ephemeral": self.ephemeral_threads,
            "model": self.model,
            "sandbox": _sandbox_value(sdk, sandbox or self.sandbox),
        }
        if self.workspace_root is not None:
            if cwd is None:
                raise RuntimeError("An isolated Codex workspace requires a working directory.")
            kwargs["config"] = _isolated_thread_config()
            if sandbox == "workspace_write":
                kwargs["config"]["sandbox_workspace_write"] = {
                    "writable_roots": [cwd], "network_access": False,
                    "exclude_tmpdir_env_var": True, "exclude_slash_tmp": True,
                }
        if cwd:
            kwargs["cwd"] = cwd
        if self.service_tier:
            kwargs["service_tier"] = self.service_tier
        if self.base_instructions:
            kwargs["base_instructions"] = self.base_instructions
        developer_instructions = self.developer_instructions
        if self.workspace_root is not None:
            developer_instructions = _join_instructions(
                developer_instructions,
                ISOLATED_WORKSPACE_INSTRUCTIONS,
            )
        if developer_instructions:
            kwargs["developer_instructions"] = developer_instructions
        return codex.thread_start(**kwargs)

    def _run_thread(self, thread: object, sdk: "_CodexSDK", prompt: str, *, workspace: Path | None = None, sandbox: str | None = None, trace_dir: Path | None = None) -> object:
        kwargs: dict[str, object] = {
            "effort": self.reasoning_effort,
            "model": self.model,
            # Inherit the precisely scoped thread policy for writable calls.
            # The SDK's workspace-write turn preset drops explicit roots/tmp exclusions.
            "sandbox": None if sandbox == "workspace_write" else _sandbox_value(sdk, sandbox or self.sandbox),
            "service_tier": self.service_tier,
        }
        if not self.log_events:
            return thread.run(prompt, **kwargs)
        # Use the SDK's own collector so status/error/final-response semantics
        # remain identical to Thread.run while preserving the intermediate stream.
        from openai_codex._run import _collect_turn_result

        assert workspace is not None
        trace_dir = trace_dir or self.workspace_root.parent / "codex_traces" / workspace.name
        trace_dir.mkdir(parents=True, exist_ok=False)
        with (trace_dir / "events.jsonl").open("w", encoding="utf-8") as events, \
                (trace_dir / "transcript.md").open("w", encoding="utf-8") as transcript:
            def record(method, payload):
                entry = {"recorded_at": datetime.now(timezone.utc).isoformat(),
                         "method": method, "payload": _event_jsonable(payload)}
                events.write(json.dumps(entry, ensure_ascii=False) + "\n")
                events.flush()
                if method in {"client/turnStart", "item/completed", "turn/completed", "client/error"}:
                    transcript.write(f"\n## {entry['recorded_at']} — {method}\n\n")
                    transcript.write(json.dumps(entry["payload"], ensure_ascii=False, indent=2) + "\n")
                    transcript.flush()

            record("client/turnStart", {"input": prompt, "model": self.model,
                                        "reasoning_effort": self.reasoning_effort})
            stream = None
            turn = None
            try:
                turn = thread.turn(prompt, **kwargs)
                stream = (_timed_events(turn, self.call_timeout_seconds)
                          if self.call_timeout_seconds is not None else turn.stream())
                repetition = OutputRepetitionGuard()

                def logged_events():
                    for event in stream:
                        record(event.method, event.payload)
                        if self.detect_repetitive_output and event.method == 'item/agentMessage/delta':
                            payload = _event_jsonable(event.payload)
                            if repetition.update(payload.get('itemId'), str(payload.get('delta', ''))):
                                raise CodexCallTechnicalError('Sustained repetitive agent output detected')
                        yield event

                result = _collect_turn_result(logged_events(), turn_id=turn.id)
                (trace_dir / "result.json").write_text(
                    json.dumps(_event_jsonable(result), ensure_ascii=False, indent=2), encoding="utf-8")
                return result
            except Exception as exc:
                record("client/error", {"type": type(exc).__name__, "message": str(exc)})
                if isinstance(exc, CodexCallTechnicalError) and turn is not None:
                    record('client/guardInterrupt', {'turn_id': turn.id, 'reason': str(exc)})
                    # Do not let an unresponsive interrupt RPC prevent context cleanup.
                    def interrupt():
                        try:
                            turn.interrupt()
                        except Exception:
                            pass
                    cancellation = threading.Thread(target=interrupt, daemon=True)
                    cancellation.start()
                    cancellation.join(timeout=2)
                raise
            finally:
                if stream is not None:
                    stream.close()

    def _create_call_workspace(
        self, prompt: str, *, files: Mapping[str, str] | None = None
    ) -> Path:
        if self.workspace_root is None:
            raise RuntimeError("No Codex workspace root was configured.")
        self.workspace_root.mkdir(parents=True, exist_ok=True)
        with self._workspace_lock:
            while True:
                self._workspace_counter += 1
                workspace = self.workspace_root / f"call_{self._workspace_counter:06d}"
                try:
                    workspace.mkdir(exist_ok=False)
                except FileExistsError:
                    continue
                break
            self.last_workspace = workspace
        (workspace / "prompt.txt").write_text(prompt, encoding="utf-8")
        for name, content in (files or {}).items():
            (workspace / name).write_text(content, encoding="utf-8")
        self._write_workspace_metadata(workspace, status="running")
        return workspace

    def _record_workspace_result(
        self, workspace: Path, result: object, *, sandbox: str | None = None,
        usage: LLMUsage | None = None,
    ) -> None:
        response = str(getattr(result, "final_response", None) or "")
        (workspace / "response.txt").write_text(response, encoding="utf-8")
        self._write_workspace_metadata(
            workspace,
            status=str(getattr(result, "status", None) or "completed"),
            sandbox=sandbox,
            usage=usage,
        )

    def _record_workspace_failure(
        self, workspace: Path, exc: Exception, *, sandbox: str | None = None,
        usage: LLMUsage | None = None,
    ) -> None:
        (workspace / "error.txt").write_text(
            f"{type(exc).__name__}: {exc}\n",
            encoding="utf-8",
        )
        self._write_workspace_metadata(
            workspace,
            status="failed",
            error_type=type(exc).__name__,
            sandbox=sandbox,
            usage=usage,
        )

    def _write_workspace_metadata(
        self,
        workspace: Path,
        *,
        status: str,
        error_type: str = "",
        sandbox: str | None = None,
        usage: LLMUsage | None = None,
    ) -> None:
        metadata = {
            "approval_mode": self.approval_mode,
            "created_or_updated_at": datetime.now(timezone.utc).isoformat(),
            "ephemeral_thread": self.ephemeral_threads,
            "error_type": error_type,
            "filesystem_policy": "sandbox_" + (sandbox or self.sandbox),
            "input_files": sorted(
                path.name
                for path in workspace.iterdir()
                if path.is_file()
                and path.name not in {"error.txt", "metadata.json", "response.txt", "mutated_proof.md", "introduced_error.md"}
            ),
            "model": self.model,
            "network_access": False,
            "permission_profile": "",
            "reasoning_effort": self.reasoning_effort,
            "sandbox_compatibility_setting": sandbox or self.sandbox,
            "status": status,
            "event_logging": self.log_events,
            "call_timeout_seconds": self.call_timeout_seconds,
            "detect_repetitive_output": self.detect_repetitive_output,
            "technical_retries": self.technical_retries,
            "elapsed_seconds": usage.elapsed_seconds if usage is not None else None,
            "usage": usage.to_dict() if usage is not None else None,
            "event_trace_dir": str(self.workspace_root.parent / "codex_traces" / workspace.name)
            if self.log_events else None,
            "web_search": "disabled",
        }
        (workspace / "metadata.json").write_text(
            json.dumps(metadata, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )


def _event_jsonable(value):
    """Preserve structured SDK payloads, including unknown notification fields."""
    if isinstance(value, Enum):
        return _event_jsonable(value.value)
    if callable(getattr(value, "model_dump", None)):
        return value.model_dump(mode="json", by_alias=True)
    if is_dataclass(value):
        return {field.name: _event_jsonable(getattr(value, field.name)) for field in fields(value)}
    if isinstance(value, dict):
        return {key: _event_jsonable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_event_jsonable(item) for item in value]
    return value


def _usage_number(value: object, *, integer: bool = True):
    if value is None or isinstance(value, bool):
        return None
    try:
        return int(value) if integer else float(value)
    except (TypeError, ValueError):
        return None


def _codex_usage(result: object, *, elapsed_seconds: float) -> LLMUsage:
    """Normalize the cumulative usage exposed by a Codex turn result."""

    underlying = getattr(result, "agent_result", result)
    data = _event_jsonable(underlying)
    if not isinstance(data, dict):
        data = {
            "duration_ms": getattr(underlying, "duration_ms", None),
            "usage": getattr(underlying, "usage", None),
        }
    usage = data.get("usage")
    if not isinstance(usage, dict):
        usage = _event_jsonable(usage)
    usage = usage if isinstance(usage, dict) else {}
    total = usage.get("total", usage)
    if not isinstance(total, dict):
        total = _event_jsonable(total)
    total = total if isinstance(total, dict) else {}

    def token(*names: str) -> int | None:
        for name in names:
            if name in total:
                return _usage_number(total[name])
        return None

    duration_ms = _usage_number(data.get("duration_ms"), integer=False)
    return LLMUsage(
        elapsed_seconds=elapsed_seconds,
        provider_elapsed_seconds=duration_ms / 1000 if duration_ms is not None else None,
        input_tokens=token("inputTokens", "input_tokens"),
        cached_input_tokens=token("cachedInputTokens", "cached_input_tokens"),
        cache_write_input_tokens=token("cacheWriteInputTokens", "cache_write_input_tokens"),
        output_tokens=token("outputTokens", "output_tokens"),
        reasoning_output_tokens=token("reasoningOutputTokens", "reasoning_output_tokens"),
        total_tokens=token("totalTokens", "total_tokens"),
    )


@dataclass(frozen=True)
class _CodexSDK:
    Codex: object
    CodexConfig: object
    Sandbox: object
    ApprovalMode: object


def _load_codex_sdk() -> _CodexSDK:
    try:
        from openai_codex import ApprovalMode, Codex, CodexConfig, Sandbox
    except ImportError as exc:
        raise ImportError(
            "The openai-codex package is required to use CodexProofFuzzerClient. "
            "Install it into the active environment first."
        ) from exc
    return _CodexSDK(
        Codex=Codex,
        CodexConfig=CodexConfig,
        Sandbox=Sandbox,
        ApprovalMode=ApprovalMode,
    )


def _sandbox_value(sdk: _CodexSDK, name: str) -> object:
    return getattr(sdk.Sandbox, name)


def _approval_mode_value(sdk: _CodexSDK, name: str) -> object:
    return getattr(sdk.ApprovalMode, name)


def _join_instructions(*instructions: str | None) -> str:
    return "\n\n".join(item.strip() for item in instructions if item and item.strip())


def _validate_workspace_files(files: Mapping[str, str]) -> dict[str, str]:
    normalized: dict[str, str] = {}
    for name, content in files.items():
        path = Path(name)
        if (
            not name
            or path.is_absolute()
            or path.name != name
            or name in _RESERVED_WORKSPACE_FILES
        ):
            raise ValueError(f"Unsafe or reserved workspace filename: {name!r}")
        if not isinstance(content, str):
            raise TypeError(f"Workspace file {name!r} must contain text.")
        normalized[name] = content
    return normalized


def _workspace_bootstrap(files: Mapping[str, str]) -> str:
    names = ["prompt.txt", *sorted(files)]
    listed = ", ".join(names)
    return (
        f"Read the task instructions and inputs from these workspace files: {listed}. "
        "Follow prompt.txt, then return only the requested final response."
    )


def _file_mutation_task(prompt: str) -> tuple[str, str]:
    """Adapt only the full-proof mutation protocol; fail closed if it changes."""
    prefix, marker, rest = prompt.partition("Original proof:\n<original_proof>\n")
    source, closing, output = rest.rpartition("\n</original_proof>\n")
    if not marker or not closing or "## Introduced error" not in output:
        raise ValueError("Unrecognized full-proof mutation prompt for file editing.")
    explanation = output.split("## Introduced error", 1)[1].strip()
    return prefix + """File-based mutation task:
The complete original proof is in original_proof.md. Read it in full.
Copy original_proof.md to mutated_proof.md, then use targeted filesystem edits on that copy.
Preserve all unchanged text; do not rewrite or summarize the entire manuscript, omit sections,
or insert placeholders. Do not modify original_proof.md or prompt.txt.
Write only the complete revised proof in mutated_proof.md, without mutation commentary.
Write the introduced-error explanation separately in introduced_error.md:
""" + explanation + """

Inspect the diff against original_proof.md to check that only intended changes were made.
Do not print the whole proof in your final response. After saving both output files, reply Done.
""", source


def _read_file_mutation(workspace: Path, original: str) -> str:
    import stat

    def read(name):
        path = workspace / name
        info = path.lstat()
        if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1:
            raise ValueError(f"Mutation artifact must be a regular, unlinked file: {name}")
        content = path.read_text(encoding="utf-8")
        if not content.strip():
            raise ValueError(f"Empty mutation artifact: {name}")
        return content

    if read("original_proof.md") != original:
        raise ValueError("Mutation agent modified the original proof input.")
    mutated = read("mutated_proof.md")
    explanation = read("introduced_error.md")
    if mutated == original:
        raise ValueError("Mutation agent left the proof unchanged.")
    return f"## Mutated proof\n{mutated}\n\n## Introduced error\n{explanation}"


def _isolated_thread_config() -> dict[str, object]:
    return {
        "agents": {"enabled": False},
        "features": {"skill_mcp_dependency_install": False},
        "project_root_markers": [],
        "web_search": "disabled",
    }
