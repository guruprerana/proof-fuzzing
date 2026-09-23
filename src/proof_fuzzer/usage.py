"""Normalized usage accounting shared by model clients."""

from __future__ import annotations

from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class LLMUsage:
    """Comparable timing, token, and cost fields for one model call.

    ``elapsed_seconds`` is measured locally with a monotonic clock. The provider
    duration is retained separately because it can exclude client-side startup,
    transport, and cleanup time.
    """

    elapsed_seconds: float
    provider_elapsed_seconds: float | None = None
    input_tokens: int | None = None
    cached_input_tokens: int | None = None
    cache_write_input_tokens: int | None = None
    output_tokens: int | None = None
    reasoning_output_tokens: int | None = None
    total_tokens: int | None = None
    cost_usd: float | None = None
    turns: int | None = None

    def to_dict(self) -> dict[str, int | float | None]:
        return asdict(self)
