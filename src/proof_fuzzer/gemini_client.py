"""Google Gemini client helpers for proof fuzzing."""

from __future__ import annotations

from dataclasses import dataclass
import os
from typing import Any, Iterable, Mapping


DEFAULT_GEMINI_MODEL = "gemini-3.5-flash"
DEFAULT_GEMINI_THINKING_LEVEL = "medium"


@dataclass(frozen=True)
class GeminiChatResult:
    """Result from a Gemini interaction call."""

    content: str
    reasoning: str = ""
    finish_reason: str = ""
    raw_response: object | None = None


class GeminiProofFuzzerClient:
    """Small Gemini client matching the proof-fuzzer LLM protocol."""

    def __init__(
        self,
        *,
        api_key: str | None = None,
        model: str = DEFAULT_GEMINI_MODEL,
        max_tokens: int = 65_536,
        temperature: float = 0.7,
        system_instruction: str = "",
        thinking_level: str = DEFAULT_GEMINI_THINKING_LEVEL,
        thinking_summaries: str = "auto",
        client: Any | None = None,
    ):
        self.model = model
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.system_instruction = system_instruction
        self.thinking_level = thinking_level
        self.thinking_summaries = thinking_summaries
        if client is None:
            client = _make_gemini_client(api_key=api_key)
        self.client = client
        self.last_result: GeminiChatResult | None = None
        self.last_reasoning = ""

    def complete(self, prompt: str) -> str:
        """Return only final content, matching the proof-fuzzer LLM protocol."""

        return self.complete_with_reasoning(prompt).content

    def complete_with_reasoning(self, prompt: str) -> GeminiChatResult:
        """Return final content plus available Gemini thought text."""

        return self.interact(prompt)

    def chat(
        self,
        messages: Iterable[Mapping[str, str]],
        *,
        max_tokens: int | None = None,
        temperature: float | None = None,
        system_instruction: str | None = None,
    ) -> GeminiChatResult:
        """Generate from chat-style messages by flattening them into Gemini contents."""

        prompt = _messages_to_prompt(messages)
        return self.interact(
            prompt,
            max_tokens=max_tokens,
            temperature=temperature,
            system_instruction=system_instruction,
        )

    def generate_content(
        self,
        prompt: str,
        *,
        max_tokens: int | None = None,
        temperature: float | None = None,
        system_instruction: str | None = None,
    ) -> GeminiChatResult:
        """Compatibility alias for older call sites; uses the Interactions API."""

        return self.interact(
            prompt,
            max_tokens=max_tokens,
            temperature=temperature,
            system_instruction=system_instruction,
        )

    def interact(
        self,
        prompt: str,
        *,
        max_tokens: int | None = None,
        temperature: float | None = None,
        system_instruction: str | None = None,
    ) -> GeminiChatResult:
        """Run ``interactions.create`` with Gemini thinking enabled."""

        generation_config = _make_generation_config(
            max_tokens=max_tokens if max_tokens is not None else self.max_tokens,
            temperature=temperature if temperature is not None else self.temperature,
            thinking_level=self.thinking_level,
            thinking_summaries=self.thinking_summaries,
        )
        request_input = _apply_system_instruction(
            prompt,
            self.system_instruction if system_instruction is None else system_instruction,
        )
        response = self.client.interactions.create(
            model=self.model,
            input=request_input,
            generation_config=generation_config,
        )
        result = GeminiChatResult(
            content=_interaction_content(response),
            reasoning=_interaction_reasoning(response),
            finish_reason=_interaction_finish_reason(response),
            raw_response=response,
        )
        self.last_result = result
        self.last_reasoning = result.reasoning
        return result


def _make_generation_config(
    *,
    max_tokens: int,
    temperature: float,
    thinking_level: str,
    thinking_summaries: str,
) -> dict[str, object]:
    config: dict[str, object] = {
        "max_output_tokens": max_tokens,
        "temperature": temperature,
        "thinking_level": thinking_level,
    }
    if thinking_summaries:
        config["thinking_summaries"] = thinking_summaries
    return config


def _apply_system_instruction(prompt: str, system_instruction: str) -> str:
    if not system_instruction.strip():
        return prompt
    return f"SYSTEM:\n{system_instruction.strip()}\n\nUSER:\n{prompt}"


def _messages_to_prompt(messages: Iterable[Mapping[str, str]]) -> str:
    parts: list[str] = []
    for message in messages:
        role = str(message.get("role", "user")).strip() or "user"
        content = str(message.get("content", ""))
        parts.append(f"{role.upper()}:\n{content}")
    return "\n\n".join(parts)


def _interaction_content(interaction: object) -> str:
    output_text = getattr(interaction, "output_text", None)
    if output_text:
        return str(output_text)
    text = getattr(interaction, "text", None)
    if text:
        return str(text)
    return "\n".join(_interaction_parts_text(interaction, step_type="model_output")).strip()


def _interaction_reasoning(interaction: object) -> str:
    return "\n".join(_interaction_parts_text(interaction, step_type="thought")).strip()


def _interaction_parts_text(interaction: object, *, step_type: str) -> list[str]:
    texts: list[str] = []
    for step in getattr(interaction, "steps", ()) or ():
        if str(getattr(step, "type", "")) != step_type:
            continue
        blocks = getattr(step, "summary", None) if step_type == "thought" else getattr(step, "content", None)
        for block in blocks or ():
            if str(getattr(block, "type", "text")) != "text":
                continue
            text = getattr(block, "text", None)
            if text:
                texts.append(str(text))
    return texts


def _interaction_finish_reason(interaction: object) -> str:
    status = getattr(interaction, "status", None)
    return "" if status is None else str(status)


def _make_gemini_client(*, api_key: str | None = None) -> object:
    try:
        from google import genai
    except ImportError as exc:
        raise ImportError(
            "The google-genai package is required to create a real GeminiProofFuzzerClient. "
            "Install requirements into the active environment first."
        ) from exc

    resolved_api_key = api_key or os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if not resolved_api_key:
        raise ValueError("Gemini API key is required. Set GEMINI_API_KEY or GOOGLE_API_KEY.")
    return genai.Client(api_key=resolved_api_key)
