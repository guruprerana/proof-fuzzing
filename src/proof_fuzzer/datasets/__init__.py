"""Dataset adapters for the active strategy-transfer pipeline."""

from dataclasses import dataclass, field


@dataclass(frozen=True)
class TextProofExample:
    """Canonical adapter accepted by ``run_strategy_transfer``."""

    example_id: str
    problem: str
    proof: str
    provenance: dict[str, object] = field(default_factory=dict)

    def metadata(self) -> dict[str, object]:
        return {"example_id": self.example_id, **self.provenance}


__all__ = ["TextProofExample"]
