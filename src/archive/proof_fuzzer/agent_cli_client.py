"""Isolated, programmatic clients for Claude Code and Gemini CLI."""

from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import queue
import subprocess
import threading
import time
from typing import Mapping, Sequence
import uuid

from .codex_client import (
    OutputRepetitionGuard,
    _file_mutation_task,
    _read_file_mutation,
    _validate_workspace_files,
    _workspace_bootstrap,
)
from .usage import LLMUsage


DEFAULT_CLAUDE_MODEL = "sonnet"
DEFAULT_GEMINI_CLI_MODEL = "gemini-3.5-flash"
VALID_CLAUDE_EFFORTS = {"low", "medium", "high", "xhigh", "max"}

ISOLATED_CLI_INSTRUCTIONS = """This agent call runs in a dedicated per-call workspace.
Treat the current working directory and its descendants as the entire available filesystem.
Do not inspect parent or sibling directories, follow paths outside this workspace, or use
absolute paths outside it. Do not use network or internet resources. Task instructions are stored
in prompt.txt; any supplemental task inputs named there are separate files in the same directory.
Read those files directly and use only files inside this workspace to complete the task."""


@dataclass(frozen=True)
class AgentCLIChatResult:
    """Normalized result returned by either command-line agent."""

    content: str
    reasoning: str = ""
    finish_reason: str = ""
    raw_response: object | None = None
    usage: LLMUsage | None = None


@dataclass
class ClaudePersistentSession:
    """A resumable Claude Code conversation rooted in one mutation workspace."""

    id: str
    workspace: Path
    started: bool = False


@dataclass
class GeminiPersistentSession:
    """A resumable Gemini CLI conversation rooted in one mutation workspace."""

    id: str
    workspace: Path
    started: bool = False


class AgentCLICallError(RuntimeError):
    """A command-line agent exited without a successful result."""


class AgentCLICallTechnicalError(AgentCLICallError):
    """A local timeout or output guard stopped an otherwise valid call."""


class _AgentCLIClient:
    provider = "agent"

    def __init__(
        self,
        *,
        workspace_root: str | Path,
        model: str,
        executable: str,
        log_events: bool = False,
        mutation_file_editing: bool = False,
        call_timeout_seconds: float | None = None,
        detect_repetitive_output: bool = False,
        technical_retries: int = 0,
        environment: Mapping[str, str] | None = None,
    ) -> None:
        if call_timeout_seconds is not None and call_timeout_seconds <= 0:
            raise ValueError("call_timeout_seconds must be positive")
        if technical_retries < 0:
            raise ValueError("technical_retries must be nonnegative")
        if (call_timeout_seconds is not None or detect_repetitive_output or technical_retries) and not log_events:
            raise ValueError("Call safeguards require event logging")
        self.workspace_root = Path(workspace_root).resolve()
        self.model = model
        self.executable = executable
        self.log_events = log_events
        self.mutation_file_editing = mutation_file_editing
        self.call_timeout_seconds = call_timeout_seconds
        self.detect_repetitive_output = detect_repetitive_output
        self.technical_retries = technical_retries
        self.environment = dict(environment or {})
        self.last_result: AgentCLIChatResult | None = None
        self.last_reasoning = ""
        self.last_workspace: Path | None = None
        self._workspace_counter = 0
        self._workspace_lock = threading.Lock()

    def complete(self, prompt: str) -> str:
        return self.complete_with_reasoning(prompt).content

    def complete_with_reasoning(self, prompt: str) -> AgentCLIChatResult:
        mutation_source = None
        files = None
        task = prompt
        if self.mutation_file_editing and prompt.startswith(
            "You are introducing a subtle mathematical error into a proof."
        ):
            task, mutation_source = _file_mutation_task(prompt)
            files = {"original_proof.md": mutation_source}
        return self._complete(task, files=files, mutation_source=mutation_source)

    def complete_with_files(self, prompt: str, files: Mapping[str, str]) -> str:
        return self.complete_with_reasoning_files(prompt, files).content

    def complete_with_reasoning_files(
        self, prompt: str, files: Mapping[str, str]
    ) -> AgentCLIChatResult:
        return self._complete(prompt, files=_validate_workspace_files(files))

    def close(self) -> None:
        """Compatibility no-op: every call is a fresh, non-persistent process."""

    def _complete(
        self,
        prompt: str,
        *,
        files: Mapping[str, str] | None = None,
        mutation_source: str | None = None,
    ) -> AgentCLIChatResult:
        for attempt in range(self.technical_retries + 1):
            workspace = self._create_workspace(prompt, files or {})
            attempt_started = time.monotonic()
            try:
                result = self._invoke(workspace, _workspace_bootstrap(files or {}))
                if mutation_source is not None:
                    content = _read_file_mutation(workspace, mutation_source)
                    result = AgentCLIChatResult(
                        content=content,
                        reasoning=result.reasoning,
                        finish_reason=result.finish_reason,
                        raw_response=result.raw_response,
                        usage=result.usage,
                    )
                self._record_success(workspace, result)
                self.last_result = result
                self.last_reasoning = result.reasoning
                return result
            except AgentCLICallTechnicalError as error:
                self._record_failure(
                    workspace, error,
                    usage=LLMUsage(elapsed_seconds=time.monotonic() - attempt_started),
                )
                (workspace / "technical_retry.json").write_text(
                    json.dumps(
                        {
                            "attempt": attempt + 1,
                            "retry_scheduled": attempt < self.technical_retries,
                            "error": str(error),
                            "prompt_sha256": hashlib.sha256(prompt.encode()).hexdigest(),
                        },
                        indent=2,
                    )
                    + "\n",
                    encoding="utf-8",
                )
                if attempt >= self.technical_retries:
                    raise
            except Exception as error:
                self._record_failure(
                    workspace, error,
                    usage=LLMUsage(elapsed_seconds=time.monotonic() - attempt_started),
                )
                raise
        raise AssertionError("unreachable")

    def _create_workspace(self, prompt: str, files: Mapping[str, str]) -> Path:
        self.workspace_root.mkdir(parents=True, exist_ok=True)
        with self._workspace_lock:
            while True:
                self._workspace_counter += 1
                workspace = self.workspace_root / f"call_{self._workspace_counter:06d}"
                try:
                    workspace.mkdir(exist_ok=False)
                    break
                except FileExistsError:
                    continue
            self.last_workspace = workspace
        (workspace / "prompt.txt").write_text(prompt, encoding="utf-8")
        for name, content in files.items():
            (workspace / name).write_text(content, encoding="utf-8")
        # Stop Gemini's upward .env search before it can reach an experiment repository.
        (workspace / ".env").write_text("", encoding="utf-8")
        self._write_metadata(workspace, status="running")
        return workspace

    def _invoke(
        self,
        workspace: Path,
        prompt: str,
        *,
        cwd: Path | None = None,
        command_and_environment: tuple[list[str], dict[str, str]] | None = None,
    ) -> AgentCLIChatResult:
        execution_workspace = cwd or workspace
        command, environment = (
            command_and_environment or self._command(execution_workspace)
        )
        trace_dir = self.workspace_root.parent / f"{self.provider}_traces" / workspace.name
        if self.log_events:
            trace_dir.mkdir(parents=True, exist_ok=False)
        started = time.monotonic()
        process = subprocess.Popen(
            command,
            cwd=execution_workspace,
            env={**os.environ, **self.environment, **environment},
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            errors="replace",
            bufsize=1,
            start_new_session=True,
        )
        assert process.stdin is not None
        process.stdin.write(prompt)
        process.stdin.close()
        events, stderr = self._collect_process(process, trace_dir if self.log_events else None)
        result = self._parse_result(events, stderr, process.returncode)
        usage = result.usage or LLMUsage(elapsed_seconds=0)
        return replace(
            result,
            usage=replace(usage, elapsed_seconds=time.monotonic() - started),
        )

    def _collect_process(
        self, process: subprocess.Popen[str], trace_dir: Path | None
    ) -> tuple[list[dict[str, object]], str]:
        output: queue.Queue[tuple[str, str | None]] = queue.Queue()

        def read_stream(name: str, stream) -> None:
            try:
                for line in iter(stream.readline, ""):
                    output.put((name, line))
            finally:
                stream.close()
                output.put((name, None))

        assert process.stdout is not None and process.stderr is not None
        threading.Thread(target=read_stream, args=("stdout", process.stdout), daemon=True).start()
        threading.Thread(target=read_stream, args=("stderr", process.stderr), daemon=True).start()
        deadline = (
            time.monotonic() + self.call_timeout_seconds
            if self.call_timeout_seconds is not None
            else None
        )
        active = {"stdout", "stderr"}
        events: list[dict[str, object]] = []
        stderr_parts: list[str] = []
        repetition = OutputRepetitionGuard()
        event_log = (trace_dir / "events.jsonl").open("w", encoding="utf-8") if trace_dir else None
        stderr_log = (trace_dir / "stderr.txt").open("w", encoding="utf-8") if trace_dir else None
        try:
            while active:
                timeout = None if deadline is None else max(0.0, deadline - time.monotonic())
                if timeout == 0:
                    self._stop_process(process)
                    raise AgentCLICallTechnicalError(
                        f"Call exceeded {self.call_timeout_seconds:g} seconds"
                    )
                try:
                    stream_name, line = output.get(timeout=timeout)
                except queue.Empty:
                    self._stop_process(process)
                    raise AgentCLICallTechnicalError(
                        f"Call exceeded {self.call_timeout_seconds:g} seconds"
                    ) from None
                if line is None:
                    active.discard(stream_name)
                    continue
                if stream_name == "stderr":
                    stderr_parts.append(line)
                    if stderr_log:
                        stderr_log.write(line)
                        stderr_log.flush()
                    continue
                try:
                    event = json.loads(line)
                except json.JSONDecodeError as error:
                    self._stop_process(process)
                    raise AgentCLICallError(f"{self.provider} emitted invalid JSON: {line.rstrip()}") from error
                if not isinstance(event, dict):
                    self._stop_process(process)
                    raise AgentCLICallError(f"{self.provider} emitted a non-object JSON event")
                events.append(event)
                if event_log:
                    event_log.write(json.dumps(event, ensure_ascii=False) + "\n")
                    event_log.flush()
                delta = self._event_text(event)
                if self.detect_repetitive_output and delta and repetition.update("assistant", delta):
                    self._stop_process(process)
                    raise AgentCLICallTechnicalError("Sustained repetitive agent output detected")
            process.wait()
        finally:
            if process.poll() is None:
                self._stop_process(process)
            if event_log:
                event_log.close()
            if stderr_log:
                stderr_log.close()
        return events, "".join(stderr_parts)

    @staticmethod
    def _stop_process(process: subprocess.Popen[str]) -> None:
        process.terminate()
        try:
            process.wait(timeout=2)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=2)

    def _record_success(self, workspace: Path, result: AgentCLIChatResult) -> None:
        (workspace / "response.txt").write_text(result.content, encoding="utf-8")
        self._write_metadata(
            workspace, status=result.finish_reason or "completed", usage=result.usage
        )

    def _record_failure(
        self, workspace: Path, error: Exception, *, usage: LLMUsage | None = None
    ) -> None:
        (workspace / "error.txt").write_text(
            f"{type(error).__name__}: {error}\n", encoding="utf-8"
        )
        self._write_metadata(
            workspace, status="failed", error_type=type(error).__name__, usage=usage
        )

    def _write_metadata(
        self, workspace: Path, *, status: str, error_type: str = "",
        usage: LLMUsage | None = None,
    ) -> None:
        metadata = {
            "provider": self.provider,
            "model": self.model,
            "status": status,
            "error_type": error_type,
            "created_or_updated_at": datetime.now(timezone.utc).isoformat(),
            "fresh_process_per_call": True,
            "filesystem_policy": "workspace_read_write",
            "network_access": False,
            "web_search": "disabled",
            "shell_access": False,
            "event_logging": self.log_events,
            "call_timeout_seconds": self.call_timeout_seconds,
            "detect_repetitive_output": self.detect_repetitive_output,
            "technical_retries": self.technical_retries,
            "elapsed_seconds": usage.elapsed_seconds if usage is not None else None,
            "usage": usage.to_dict() if usage is not None else None,
            "input_files": sorted(
                path.name
                for path in workspace.iterdir()
                if path.is_file()
                and path.name
                not in {
                    ".env",
                    "error.txt",
                    "metadata.json",
                    "response.txt",
                    "mutated_proof.md",
                    "introduced_error.md",
                    "technical_retry.json",
                }
            ),
            "event_trace_dir": str(
                self.workspace_root.parent / f"{self.provider}_traces" / workspace.name
            )
            if self.log_events
            else None,
        }
        (workspace / "metadata.json").write_text(
            json.dumps(metadata, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )

    def _command(self, workspace: Path) -> tuple[list[str], dict[str, str]]:
        raise NotImplementedError

    def _parse_result(
        self, events: Sequence[dict[str, object]], stderr: str, returncode: int | None
    ) -> AgentCLIChatResult:
        raise NotImplementedError

    def _event_text(self, event: Mapping[str, object]) -> str:
        raise NotImplementedError


class ClaudeCodeProofFuzzerClient(_AgentCLIClient):
    """Run Claude Code headlessly in a fresh, restricted workspace per call."""

    provider = "claude_code"

    def __init__(
        self,
        *,
        workspace_root: str | Path,
        model: str = DEFAULT_CLAUDE_MODEL,
        reasoning_effort: str = "medium",
        executable: str = "claude",
        **kwargs,
    ) -> None:
        if reasoning_effort not in VALID_CLAUDE_EFFORTS:
            allowed = ", ".join(sorted(VALID_CLAUDE_EFFORTS))
            raise ValueError(f"Unknown Claude effort {reasoning_effort!r}; expected one of: {allowed}")
        self.reasoning_effort = reasoning_effort
        super().__init__(
            workspace_root=workspace_root, model=model, executable=executable, **kwargs
        )

    def _command(self, workspace: Path) -> tuple[list[str], dict[str, str]]:
        return [
            self.executable,
            "--print",
            "--output-format",
            "stream-json",
            "--verbose",
            "--model",
            self.model,
            "--effort",
            self.reasoning_effort,
            "--no-session-persistence",
            "--restricted",
            "--strict-mcp-config",
            "--safe-mode",
            "--tools",
            "Read,Write,Edit,Glob,Grep",
            "--permission-mode",
            "acceptEdits",
            "--permission-prompts",
            "none",
            "--append-system-prompt",
            ISOLATED_CLI_INSTRUCTIONS,
        ], {"NO_COLOR": "1", "CLAUDE_CODE_SKIP_PROMPT_HISTORY": "1"}

    def start_persistent_session(self, workspace: str | Path) -> ClaudePersistentSession:
        """Create an explicit resumable conversation confined to ``workspace``."""
        root = Path(workspace).resolve()
        root.mkdir(parents=True, exist_ok=True)
        return ClaudePersistentSession(str(uuid.uuid4()), root)

    def run_persistent_turn(
        self,
        session: ClaudePersistentSession,
        prompt: str,
    ) -> AgentCLIChatResult:
        """Run one logged turn and retain Claude context for the next turn."""
        for attempt in range(self.technical_retries + 1):
            call_workspace = self._create_workspace(prompt, {})
            started = time.monotonic()
            try:
                command, environment = self._command(session.workspace)
                command.remove("--no-session-persistence")
                environment = dict(environment)
                environment.pop("CLAUDE_CODE_SKIP_PROMPT_HISTORY", None)
                command.extend(
                    ["--resume", session.id]
                    if session.started
                    else ["--session-id", session.id]
                )
                result = self._invoke(
                    call_workspace,
                    prompt,
                    cwd=session.workspace,
                    command_and_environment=(command, environment),
                )
                session.started = True
                self._record_success(call_workspace, result)
                self.last_result = result
                self.last_reasoning = result.reasoning
                return result
            except AgentCLICallTechnicalError as error:
                self._record_failure(
                    call_workspace,
                    error,
                    usage=LLMUsage(elapsed_seconds=time.monotonic() - started),
                )
                (call_workspace / "technical_retry.json").write_text(
                    json.dumps(
                        {
                            "attempt": attempt + 1,
                            "retry_scheduled": attempt < self.technical_retries,
                            "error": str(error),
                            "prompt_sha256": hashlib.sha256(prompt.encode()).hexdigest(),
                        },
                        indent=2,
                    )
                    + "\n",
                    encoding="utf-8",
                )
                if attempt >= self.technical_retries:
                    raise
            except Exception as error:
                self._record_failure(
                    call_workspace,
                    error,
                    usage=LLMUsage(elapsed_seconds=time.monotonic() - started),
                )
                raise
        raise AssertionError("unreachable")

    def _event_text(self, event: Mapping[str, object]) -> str:
        if event.get("type") != "assistant":
            return ""
        message = event.get("message")
        if not isinstance(message, dict):
            return ""
        return "".join(
            str(block.get("text", ""))
            for block in message.get("content", [])
            if isinstance(block, dict) and block.get("type") == "text"
        )

    def _parse_result(
        self, events: Sequence[dict[str, object]], stderr: str, returncode: int | None
    ) -> AgentCLIChatResult:
        final = next((event for event in reversed(events) if event.get("type") == "result"), None)
        if returncode != 0 or final is None or final.get("is_error") is True:
            detail = str(final.get("result", "")) if final else stderr.strip()
            raise AgentCLICallError(
                f"Claude Code failed with exit code {returncode}: {detail or 'no result event'}"
            )
        reasoning: list[str] = []
        for event in events:
            if event.get("type") != "assistant":
                continue
            message = event.get("message")
            if not isinstance(message, dict):
                continue
            for block in message.get("content", []):
                if isinstance(block, dict) and block.get("type") == "thinking" and block.get("thinking"):
                    reasoning.append(str(block["thinking"]))
        return AgentCLIChatResult(
            content=str(final.get("result", "")),
            reasoning="\n".join(reasoning),
            finish_reason=str(final.get("terminal_reason") or final.get("subtype") or "completed"),
            raw_response=list(events),
            usage=_claude_usage(final),
        )


class GeminiCLIProofFuzzerClient(_AgentCLIClient):
    """Run Gemini CLI headlessly with only workspace-rooted file tools."""

    provider = "gemini_cli"

    def __init__(
        self,
        *,
        workspace_root: str | Path,
        model: str = DEFAULT_GEMINI_CLI_MODEL,
        executable: str = "gemini",
        **kwargs,
    ) -> None:
        super().__init__(
            workspace_root=workspace_root, model=model, executable=executable, **kwargs
        )

    def _command(self, workspace: Path) -> tuple[list[str], dict[str, str]]:
        config_root = self.workspace_root / ".gemini_cli_config"
        config_root.mkdir(parents=True, exist_ok=True)
        # Gemini treats GEMINI_CLI_SYSTEM_SETTINGS_PATH as an administrator-owned
        # override and rejects files below a user-owned experiment directory. Use
        # the documented workspace settings scope instead.
        workspace_config = workspace / ".gemini"
        workspace_config.mkdir(parents=True, exist_ok=True)
        settings = workspace_config / "settings.json"
        policy = config_root / "filesystem-only.toml"
        if not settings.exists():
            settings.write_text(
                json.dumps(
                    {
                        "context": {
                            "fileName": ".proof-fuzzer-no-context",
                            "includeDirectoryTree": False,
                            "memoryBoundaryMarkers": [],
                            "includeDirectories": [],
                        },
                        "tools": {
                            "core": [
                                "read_file",
                                "read_many_files",
                                "list_directory",
                                "glob",
                                "grep_search",
                                "write_file",
                                "replace",
                            ]
                        },
                        "mcp": {"allowed": [], "excluded": ["*"]},
                        "security": {"blockGitExtensions": True},
                        "useWriteTodos": False,
                    },
                    indent=2,
                )
                + "\n",
                encoding="utf-8",
            )
        if not policy.exists():
            policy.write_text(
                """[[rule]]
toolName = ["read_file", "read_many_files", "list_directory", "glob", "grep_search", "write_file", "replace"]
decision = "allow"
priority = 999

[[rule]]
toolName = "*"
decision = "deny"
priority = 900
denyMessage = "Only file operations inside this experiment workspace are available."
""",
                encoding="utf-8",
            )
        return [
            self.executable,
            "--prompt",
            "",
            "--output-format",
            "stream-json",
            "--model",
            self.model,
            "--approval-mode",
            "auto_edit",
            "--skip-trust",
            "--policy",
            str(policy),
        ], {
            "NO_COLOR": "1",
            "GEMINI_CLI_TRUST_WORKSPACE": "true",
        }

    def _event_text(self, event: Mapping[str, object]) -> str:
        if event.get("type") == "message" and event.get("role") == "assistant":
            return str(event.get("content", ""))
        return ""

    def start_persistent_session(self, workspace: str | Path) -> GeminiPersistentSession:
        """Create an explicit resumable conversation confined to ``workspace``."""
        root = Path(workspace).resolve()
        root.mkdir(parents=True, exist_ok=True)
        return GeminiPersistentSession(str(uuid.uuid4()), root)

    def run_persistent_turn(
        self,
        session: GeminiPersistentSession,
        prompt: str,
    ) -> AgentCLIChatResult:
        """Run one logged Gemini turn and retain context for the next turn."""
        for attempt in range(self.technical_retries + 1):
            call_workspace = self._create_workspace(prompt, {})
            started = time.monotonic()
            try:
                command, environment = self._command(session.workspace)
                command.extend(
                    ["--resume", session.id]
                    if session.started
                    else ["--session-id", session.id]
                )
                result = self._invoke(
                    call_workspace,
                    prompt,
                    cwd=session.workspace,
                    command_and_environment=(command, environment),
                )
                session.started = True
                self._record_success(call_workspace, result)
                self.last_result = result
                self.last_reasoning = result.reasoning
                return result
            except AgentCLICallTechnicalError as error:
                self._record_failure(
                    call_workspace,
                    error,
                    usage=LLMUsage(elapsed_seconds=time.monotonic() - started),
                )
                (call_workspace / "technical_retry.json").write_text(
                    json.dumps(
                        {
                            "attempt": attempt + 1,
                            "retry_scheduled": attempt < self.technical_retries,
                            "error": str(error),
                            "prompt_sha256": hashlib.sha256(prompt.encode()).hexdigest(),
                        },
                        indent=2,
                    )
                    + "\n",
                    encoding="utf-8",
                )
                if attempt >= self.technical_retries:
                    raise
            except Exception as error:
                self._record_failure(
                    call_workspace,
                    error,
                    usage=LLMUsage(elapsed_seconds=time.monotonic() - started),
                )
                raise
        raise AssertionError("unreachable")

    def _parse_result(
        self, events: Sequence[dict[str, object]], stderr: str, returncode: int | None
    ) -> AgentCLIChatResult:
        final = next((event for event in reversed(events) if event.get("type") == "result"), None)
        if returncode != 0 or final is None or final.get("status") != "success":
            detail = stderr.strip()
            if final and final.get("error"):
                detail = str(final["error"])
            raise AgentCLICallError(
                f"Gemini CLI failed with exit code {returncode}: {detail or 'no successful result event'}"
            )
        stats = final.get("stats")
        stats = stats if isinstance(stats, dict) else {}
        models = stats.get("models")
        if not isinstance(models, dict) or not models:
            raise AgentCLICallTechnicalError(
                "Gemini CLI did not report the model used for this call"
            )
        if self.model not in models:
            used = ", ".join(sorted(str(model) for model in models))
            raise AgentCLICallTechnicalError(
                f"Gemini CLI model mismatch: requested {self.model!r}, used {used or 'unknown'}"
            )
        content = "".join(
            str(event.get("content", ""))
            for event in events
            if event.get("type") == "message" and event.get("role") == "assistant"
        )
        return AgentCLIChatResult(
            content=content,
            finish_reason=str(final.get("status", "completed")),
            raw_response=list(events),
            usage=_gemini_usage(final),
        )


def _optional_int(value: object) -> int | None:
    if value is None or isinstance(value, bool):
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _optional_float(value: object) -> float | None:
    if value is None or isinstance(value, bool):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _claude_usage(result: Mapping[str, object]) -> LLMUsage:
    usage = result.get("usage")
    usage = usage if isinstance(usage, dict) else {}
    details = usage.get("output_tokens_details")
    details = details if isinstance(details, dict) else {}
    duration_ms = _optional_float(result.get("duration_api_ms") or result.get("duration_ms"))
    input_tokens = _optional_int(usage.get("input_tokens"))
    cached_tokens = _optional_int(usage.get("cache_read_input_tokens"))
    cache_write_tokens = _optional_int(usage.get("cache_creation_input_tokens"))
    output_tokens = _optional_int(usage.get("output_tokens"))
    token_parts = (input_tokens, cached_tokens, cache_write_tokens, output_tokens)
    total_tokens = sum(value or 0 for value in token_parts) if any(
        value is not None for value in token_parts
    ) else None
    return LLMUsage(
        elapsed_seconds=0,
        provider_elapsed_seconds=duration_ms / 1000 if duration_ms is not None else None,
        input_tokens=input_tokens,
        cached_input_tokens=cached_tokens,
        cache_write_input_tokens=cache_write_tokens,
        output_tokens=output_tokens,
        reasoning_output_tokens=_optional_int(details.get("thinking_tokens")),
        total_tokens=total_tokens,
        cost_usd=_optional_float(result.get("total_cost_usd")),
        turns=_optional_int(result.get("num_turns")),
    )


def _gemini_usage(result: Mapping[str, object]) -> LLMUsage:
    stats = result.get("stats")
    stats = stats if isinstance(stats, dict) else {}
    duration_ms = _optional_float(stats.get("duration_ms"))
    return LLMUsage(
        elapsed_seconds=0,
        provider_elapsed_seconds=duration_ms / 1000 if duration_ms is not None else None,
        input_tokens=_optional_int(stats.get("input_tokens") or stats.get("input")),
        cached_input_tokens=_optional_int(stats.get("cached")),
        output_tokens=_optional_int(stats.get("output_tokens")),
        total_tokens=_optional_int(stats.get("total_tokens")),
    )
