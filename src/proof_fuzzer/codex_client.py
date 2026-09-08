"""Codex SDK client helpers for proof fuzzing."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import json
from pathlib import Path
import threading
from typing import Any, Mapping


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

        if self.fresh_thread_per_call:
            result = self._run_fresh_thread(prompt)
        else:
            result = self._run_reused_thread(prompt)
        chat_result = CodexChatResult(
            content=str(getattr(result, "final_response", None) or ""),
            reasoning="",
            finish_reason=str(getattr(result, "status", "") or ""),
            raw_response=result,
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
        result = self._run_fresh_thread(prompt, files=normalized_files)
        chat_result = CodexChatResult(
            content=str(getattr(result, "final_response", None) or ""),
            reasoning="",
            finish_reason=str(getattr(result, "status", "") or ""),
            raw_response=result,
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
        self, prompt: str, *, files: Mapping[str, str] | None = None
    ) -> object:
        sdk = self.sdk or _load_codex_sdk()
        call_cwd = self.cwd
        workspace = None
        run_prompt = prompt
        if self.workspace_root is not None:
            workspace = self._create_call_workspace(prompt, files=files)
            call_cwd = str(workspace)
            run_prompt = _workspace_bootstrap(files or {})
        try:
            with self._make_codex_context(sdk, cwd=call_cwd) as codex:
                thread = self._start_thread(codex, sdk, cwd=call_cwd)
                result = self._run_thread(thread, sdk, run_prompt)
        except Exception as exc:
            if workspace is not None:
                self._record_workspace_failure(workspace, exc)
            raise
        if workspace is not None:
            self._record_workspace_result(workspace, result)
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
        config = None
        if cwd:
            config = sdk.CodexConfig(cwd=cwd)
        if config is not None:
            return factory(config=config)
        return factory()

    def _start_thread(self, codex: object, sdk: "_CodexSDK", *, cwd: str | None) -> object:
        kwargs: dict[str, object] = {
            "approval_mode": _approval_mode_value(sdk, self.approval_mode),
            "ephemeral": self.ephemeral_threads,
            "model": self.model,
            "sandbox": _sandbox_value(sdk, self.sandbox),
        }
        if self.workspace_root is not None:
            if cwd is None:
                raise RuntimeError("An isolated Codex workspace requires a working directory.")
            kwargs["config"] = _isolated_thread_config()
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

    def _run_thread(self, thread: object, sdk: "_CodexSDK", prompt: str) -> object:
        kwargs: dict[str, object] = {
            "effort": self.reasoning_effort,
            "model": self.model,
            "sandbox": _sandbox_value(sdk, self.sandbox),
            "service_tier": self.service_tier,
        }
        return thread.run(prompt, **kwargs)

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

    def _record_workspace_result(self, workspace: Path, result: object) -> None:
        response = str(getattr(result, "final_response", None) or "")
        (workspace / "response.txt").write_text(response, encoding="utf-8")
        self._write_workspace_metadata(
            workspace,
            status=str(getattr(result, "status", None) or "completed"),
        )

    def _record_workspace_failure(self, workspace: Path, exc: Exception) -> None:
        (workspace / "error.txt").write_text(
            f"{type(exc).__name__}: {exc}\n",
            encoding="utf-8",
        )
        self._write_workspace_metadata(
            workspace,
            status="failed",
            error_type=type(exc).__name__,
        )

    def _write_workspace_metadata(
        self,
        workspace: Path,
        *,
        status: str,
        error_type: str = "",
    ) -> None:
        metadata = {
            "approval_mode": self.approval_mode,
            "created_or_updated_at": datetime.now(timezone.utc).isoformat(),
            "ephemeral_thread": self.ephemeral_threads,
            "error_type": error_type,
            "filesystem_policy": "sandbox_read_only",
            "input_files": sorted(
                path.name
                for path in workspace.iterdir()
                if path.is_file()
                and path.name not in {"error.txt", "metadata.json", "response.txt"}
            ),
            "model": self.model,
            "network_access": False,
            "permission_profile": "",
            "reasoning_effort": self.reasoning_effort,
            "sandbox_compatibility_setting": self.sandbox,
            "status": status,
            "web_search": "disabled",
        }
        (workspace / "metadata.json").write_text(
            json.dumps(metadata, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
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


def _isolated_thread_config() -> dict[str, object]:
    return {
        "agents": {"enabled": False},
        "features": {"skill_mcp_dependency_install": False},
        "project_root_markers": [],
        "web_search": "disabled",
    }
