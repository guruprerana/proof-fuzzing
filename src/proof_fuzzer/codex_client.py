"""Codex SDK client helpers for proof fuzzing."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


DEFAULT_CODEX_MODEL = "gpt-5.5"
DEFAULT_CODEX_REASONING_EFFORT = "medium"
DEFAULT_CODEX_SANDBOX = "read_only"
VALID_CODEX_REASONING_EFFORTS = {"low", "medium", "high", "xhigh"}
VALID_CODEX_SANDBOXES = {"read_only", "workspace_write", "full_access"}


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
    """

    def __init__(
        self,
        *,
        model: str = DEFAULT_CODEX_MODEL,
        reasoning_effort: str = DEFAULT_CODEX_REASONING_EFFORT,
        sandbox: str = DEFAULT_CODEX_SANDBOX,
        cwd: str | None = None,
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

        self.model = model
        self.reasoning_effort = reasoning_effort
        self.sandbox = sandbox
        self.cwd = cwd
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

    def close(self) -> None:
        """Close the reused Codex context, if one was opened."""

        context = self._codex_context
        self._codex_context = None
        self._thread = None
        if context is not None:
            context.__exit__(None, None, None)

    def _run_fresh_thread(self, prompt: str) -> object:
        sdk = self.sdk or _load_codex_sdk()
        with self._make_codex_context(sdk) as codex:
            thread = self._start_thread(codex, sdk)
            return self._run_thread(thread, sdk, prompt)

    def _run_reused_thread(self, prompt: str) -> object:
        sdk = self.sdk or _load_codex_sdk()
        if self._codex_context is None:
            context = self._make_codex_context(sdk)
            codex = context.__enter__()
            self._codex_context = context
            self._thread = self._start_thread(codex, sdk)
        return self._run_thread(self._thread, sdk, prompt)

    def _make_codex_context(self, sdk: "_CodexSDK") -> object:
        factory = self.codex_factory or sdk.Codex
        config = None
        if self.cwd:
            config = sdk.CodexConfig(cwd=self.cwd)
        if config is not None:
            return factory(config=config)
        return factory()

    def _start_thread(self, codex: object, sdk: "_CodexSDK") -> object:
        kwargs: dict[str, object] = {
            "approval_mode": _approval_mode_value(sdk, self.approval_mode),
            "ephemeral": self.ephemeral_threads,
            "model": self.model,
            "sandbox": _sandbox_value(sdk, self.sandbox),
        }
        if self.cwd:
            kwargs["cwd"] = self.cwd
        if self.service_tier:
            kwargs["service_tier"] = self.service_tier
        if self.base_instructions:
            kwargs["base_instructions"] = self.base_instructions
        if self.developer_instructions:
            kwargs["developer_instructions"] = self.developer_instructions
        return codex.thread_start(**kwargs)

    def _run_thread(self, thread: object, sdk: "_CodexSDK", prompt: str) -> object:
        return thread.run(
            prompt,
            effort=self.reasoning_effort,
            model=self.model,
            sandbox=_sandbox_value(sdk, self.sandbox),
            service_tier=self.service_tier,
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
