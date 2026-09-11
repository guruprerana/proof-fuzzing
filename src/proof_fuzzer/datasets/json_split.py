"""Portable JSON input adapter for strategy-transfer experiments."""

import json
from pathlib import Path

from . import TextProofExample


def load_json_split(path: Path) -> tuple[list[TextProofExample], list[TextProofExample]]:
    """Load ``{"discovery": [...], "heldout": [...]}`` proof records."""
    data = json.loads(path.read_text())

    def convert(split: str) -> list[TextProofExample]:
        rows = data.get(split)
        if not isinstance(rows, list) or not rows:
            raise ValueError(f"JSON split {split!r} must be a nonempty list")
        result = []
        for row in rows:
            if not isinstance(row, dict) or not all(str(row.get(k, "")).strip()
                                                   for k in ("example_id", "problem", "proof")):
                raise ValueError(f"Each {split} row requires example_id, problem, and proof")
            metadata = row.get("metadata", {})
            if not isinstance(metadata, dict):
                raise ValueError(f"{split} metadata must be an object")
            result.append(TextProofExample(str(row["example_id"]), str(row["problem"]),
                                           str(row["proof"]), metadata))
        return result

    discovery, heldout = convert("discovery"), convert("heldout")
    if {p.example_id for p in discovery} & {p.example_id for p in heldout}:
        raise ValueError("Discovery and held-out IDs must be disjoint")
    return discovery, heldout
