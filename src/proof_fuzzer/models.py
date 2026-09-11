"""Small data contracts used by the active proof-fuzzing pipeline."""

from dataclasses import dataclass, field
from typing import Protocol


class LLMClient(Protocol):
    def complete(self, prompt: str) -> str: ...


class ProofExample(Protocol):
    example_id: str
    problem: str
    proof: str

    # Dataset adapters may expose additional provenance fields.


@dataclass(frozen=True)
class ProofMutation:
    kind: str
    target: str = ""
    summary: str = ""
    new_text: str = ""
    affected_blocks: tuple[str, ...] = ()
    propagate_downstream: bool = True
    metadata: dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class FuzzerMutationInstructions:
    maintain_correctness: bool
    mutations: tuple[ProofMutation, ...]
    rationale: str = ""
    raw_response: str = ""


@dataclass(frozen=True)
class JudgeResult:
    verdict: str
    confidence: float = 0.0
    rationale: str = ""
    detected_flaw: str = ""
    detected_errors: tuple[dict[str, object], ...] = ()
    response_kind: str = "verdict"
    raw_response: str = ""

    def to_dict(self) -> dict[str, object]:
        return {
            "verdict": self.verdict,
            "confidence": self.confidence,
            "rationale": self.rationale,
            "detected_flaw": self.detected_flaw,
            "detected_errors": [dict(error) for error in self.detected_errors],
            "response_kind": self.response_kind,
            "raw_response": self.raw_response,
        }
