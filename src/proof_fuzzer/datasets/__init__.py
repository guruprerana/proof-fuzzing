"""Dataset adapters for the active strategy-transfer pipeline."""

from dataclasses import dataclass, field
from typing import Iterable


@dataclass(frozen=True)
class TextProofExample:
    """Canonical adapter accepted by ``run_strategy_transfer``."""

    example_id: str
    problem: str
    proof: str
    provenance: dict[str, object] = field(default_factory=dict)

    def metadata(self) -> dict[str, object]:
        return {"example_id": self.example_id, **self.provenance}


def adapt_examples(examples: Iterable[object], *, proof_attribute: str = "proof",
                   problem_attribute: str = "problem") -> tuple[TextProofExample, ...]:
    """Adapt benchmark records without coupling the pipeline to their classes.

    For example, IMO-GradeBench uses ``response`` as its proof field, while
    OpenAI Ten and ProofBenchJudge already use ``proof``.
    """
    adapted = []
    for example in examples:
        metadata = getattr(example, "metadata", {})
        if callable(metadata):
            metadata = metadata()
        converter = getattr(example, "to_metadata", None)
        if callable(converter):
            metadata = converter()
        adapted.append(TextProofExample(
            example_id=str(getattr(example, "example_id")),
            problem=str(getattr(example, problem_attribute)),
            proof=str(getattr(example, proof_attribute)),
            provenance=dict(metadata) if isinstance(metadata, dict) else {},
        ))
    return tuple(adapted)


__all__ = ["TextProofExample", "adapt_examples"]
