"""OpenAI-compatible vLLM client helpers for proof fuzzing."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable, Mapping

GPT_OSS_120B = "openai/gpt-oss-120b"
DEFAULT_BASE_URL = "http://localhost:8080/v1"
VALID_REASONING_EFFORTS = {"low", "medium", "high"}


@dataclass(frozen=True)
class VLLMChatResult:
    """Result from a vLLM OpenAI-compatible chat completion."""

    content: str
    reasoning: str = ""
    finish_reason: str = ""
    raw_response: object | None = None


class VLLMProofFuzzerClient:
    """Small vLLM client that enables gpt-oss reasoning by default.

    For gpt-oss, reasoning effort is represented in the Harmony-formatted
    system prompt as ``Reasoning: <low|medium|high>``. vLLM can additionally
    expose parsed reasoning when the server is launched with
    ``--reasoning-parser openai_gptoss``; this client also sends
    ``reasoning_effort`` for vLLM/OpenAI-compatible endpoints that support it.
    """

    def __init__(
        self,
        *,
        base_url: str = DEFAULT_BASE_URL,
        api_key: str = "EMPTY",
        model: str = GPT_OSS_120B,
        reasoning_effort: str = "high",
        max_tokens: int = 100_000,
        temperature: float = 0.7,
        client: Any | None = None,
    ):
        if reasoning_effort not in VALID_REASONING_EFFORTS:
            allowed = ", ".join(sorted(VALID_REASONING_EFFORTS))
            raise ValueError(f"Unknown reasoning effort {reasoning_effort!r}; expected one of: {allowed}")

        self.base_url = base_url
        self.model = model
        self.reasoning_effort = reasoning_effort
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.client = client or _make_openai_client(base_url=base_url, api_key=api_key)
        self.last_result: VLLMChatResult | None = None
        self.last_reasoning = ""

    def complete(self, prompt: str) -> str:
        """Return only final content, matching the proof-fuzzer LLM protocol."""

        return self.complete_with_reasoning(prompt).content

    def complete_with_reasoning(self, prompt: str) -> VLLMChatResult:
        """Return final content plus parsed reasoning for trace logging."""

        return self.chat([{"role": "user", "content": prompt}])

    def chat(
        self,
        messages: Iterable[Mapping[str, str]],
        *,
        reasoning_effort: str | None = None,
        max_tokens: int | None = None,
        temperature: float | None = None,
    ) -> VLLMChatResult:
        """Run a chat completion with gpt-oss reasoning enabled."""

        effort = reasoning_effort or self.reasoning_effort
        if effort not in VALID_REASONING_EFFORTS:
            allowed = ", ".join(sorted(VALID_REASONING_EFFORTS))
            raise ValueError(f"Unknown reasoning effort {effort!r}; expected one of: {allowed}")

        response = self.client.chat.completions.create(
            model=self.model,
            messages=build_gpt_oss_reasoning_messages(messages, reasoning_effort=effort),
            max_tokens=max_tokens if max_tokens is not None else self.max_tokens,
            temperature=temperature if temperature is not None else self.temperature,
            reasoning_effort=effort,
        )
        message = response.choices[0].message
        choice = response.choices[0]
        result = VLLMChatResult(
            content=_message_field(message, "content"),
            reasoning=_message_field(message, "reasoning_content") or _message_field(message, "reasoning"),
            finish_reason=str(getattr(choice, "finish_reason", "") or ""),
            raw_response=response,
        )
        self.last_result = result
        self.last_reasoning = result.reasoning
        return result


def build_gpt_oss_reasoning_messages(
    messages: Iterable[Mapping[str, str]],
    *,
    reasoning_effort: str = "high",
    system_prompt: str = "",
) -> list[dict[str, str]]:
    """Return messages with the gpt-oss Harmony reasoning line installed."""

    if reasoning_effort not in VALID_REASONING_EFFORTS:
        allowed = ", ".join(sorted(VALID_REASONING_EFFORTS))
        raise ValueError(f"Unknown reasoning effort {reasoning_effort!r}; expected one of: {allowed}")

    normalized = [dict(message) for message in messages]
    reasoning_line = f"Reasoning: {reasoning_effort}"

    if normalized and normalized[0].get("role") == "system":
        content = normalized[0].get("content", "")
        normalized[0]["content"] = _merge_reasoning_system_prompt(
            content,
            reasoning_line=reasoning_line,
            extra_system_prompt=system_prompt,
        )
        return normalized

    system_content = _merge_reasoning_system_prompt(
        "",
        reasoning_line=reasoning_line,
        extra_system_prompt=system_prompt,
    )
    return [{"role": "system", "content": system_content}] + normalized


def _merge_reasoning_system_prompt(
    existing: str,
    *,
    reasoning_line: str,
    extra_system_prompt: str,
) -> str:
    lines: list[str] = []
    stripped_existing = existing.strip()

    if stripped_existing:
        existing_lines = [
            line
            for line in stripped_existing.splitlines()
            if not line.strip().lower().startswith("reasoning:")
        ]
        lines.extend(existing_lines)

    if extra_system_prompt.strip():
        lines.append(extra_system_prompt.strip())

    lines.insert(0, reasoning_line)
    return "\n".join(lines)


def _message_field(message: object, field_name: str) -> str:
    value = getattr(message, field_name, None)
    if value is not None:
        return str(value)

    if hasattr(message, "model_dump"):
        data = message.model_dump()
        value = data.get(field_name)
        if value is not None:
            return str(value)

    if isinstance(message, dict):
        value = message.get(field_name)
        if value is not None:
            return str(value)

    return ""


def _make_openai_client(*, base_url: str, api_key: str) -> object:
    try:
        from openai import OpenAI
    except ImportError as exc:
        raise ImportError(
            "The openai package is required to create a real VLLMProofFuzzerClient. "
            "Install requirements into the active environment first."
        ) from exc
    return OpenAI(base_url=base_url, api_key=api_key)
