"""Leakage-safe adapter for REFLECT process-level agent traces."""

from __future__ import annotations

from dataclasses import dataclass, field
import hashlib
import json
from pathlib import Path
from typing import Iterator
from collections import Counter


@dataclass(frozen=True)
class ReflectTraceExample:
    example_id: str
    problem: str
    proof: str
    trace_id: str
    view: str
    failure_types: tuple[str, ...] = ()
    provenance: dict[str, object] = field(default_factory=dict)

    def metadata(self) -> dict[str, object]:
        return {"example_id": self.example_id, "trace_id": self.trace_id, "view": self.view,
                "failure_types": list(self.failure_types), **self.provenance}


def iter_json_objects(path: Path) -> Iterator[dict[str, object]]:
    """Read JSONL whose logical objects may span multiple physical lines."""
    decoder = json.JSONDecoder()
    text = path.read_text(encoding="utf-8")
    offset = 0
    while offset < len(text):
        while offset < len(text) and text[offset].isspace():
            offset += 1
        if offset >= len(text):
            break
        value, end = decoder.raw_decode(text, offset)
        if not isinstance(value, dict):
            raise ValueError(f"Expected JSON object in {path} at character {offset}")
        yield value
        offset = end


def _path(root: Path, view: str) -> Path:
    names = {"reasoning": ("reasoning", "reasoning"),
             "tool_use": ("tool_use", "tool_use")}
    if view not in names:
        raise ValueError(f"Unknown REFLECT process view: {view}")
    folder, stem = names[view]
    return root / "process-level-baselines" / "evaluation" / folder / f"{stem}_dataset.jsonl"


def load_process_traces(root: Path, views: tuple[str, ...] = ("reasoning", "tool_use")) -> list[ReflectTraceExample]:
    """Load clean traces only; perturbed reference traces never enter examples."""
    examples = []
    trace_indices: dict[str, int] = {}
    for view in views:
        path = _path(root, view)
        grouped: dict[str, list[dict[str, object]]] = {}
        labels: dict[str, set[str]] = {}
        for row in iter_json_objects(path):
            trace_id = str(row.get("trace_id", "")).strip()
            query = str(row.get("query", "")).strip()
            steps = row.get("original_steps")
            failure_type = str(row.get("perturbation_type",
                                   row.get("failure_type", row.get("error_type", "")))).strip()
            if not trace_id or not query or not isinstance(steps, list) or not steps:
                raise ValueError(f"Malformed REFLECT row in {path}")
            grouped.setdefault(trace_id, []).append({"query": query, "steps": steps})
            if failure_type:
                labels.setdefault(trace_id, set()).add(failure_type)
        for trace_id, variants in grouped.items():
            encodings = [json.dumps(value, sort_keys=True, ensure_ascii=False) for value in variants]
            counts = Counter(encodings)
            canonical_encoding, canonical_count = counts.most_common(1)[0]
            if list(counts.values()).count(canonical_count) > 1:
                raise ValueError(f"No unique modal clean trace for {trace_id} in {path}")
            value = json.loads(canonical_encoding)
            serialized = json.dumps(value["steps"], indent=2, ensure_ascii=False)
            failure_types = tuple(sorted(labels.get(trace_id, ())))
            source = {"path": str(path.resolve()), "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                      "rows": len(variants), "canonical_rows": canonical_count,
                      "variant_count": len(counts), "view": view}
            if trace_id in trace_indices:
                index = trace_indices[trace_id]
                prior = examples[index]
                examples[index] = ReflectTraceExample(
                    example_id=prior.example_id, problem=prior.problem, proof=prior.proof,
                    trace_id=trace_id, view=f"{prior.view}+{view}",
                    failure_types=tuple(sorted(set(prior.failure_types) | set(failure_types))),
                    provenance={**prior.provenance,
                        "sources": [*prior.provenance.get("sources", []), source],
                        "alternate_clean_trace_sha256": hashlib.sha256(serialized.encode()).hexdigest(),
                        "alternate_matches_canonical": serialized == prior.proof})
                continue
            trace_indices[trace_id] = len(examples)
            examples.append(ReflectTraceExample(
                example_id=f"reflect:{trace_id}", problem=str(value["query"]), proof=serialized,
                trace_id=trace_id, view=view, failure_types=failure_types,
                provenance={"dataset": "REFLECT", "artifact": "original_steps",
                    "sources": [source],
                    "trace_sha256": hashlib.sha256(serialized.encode()).hexdigest(),
                    "step_count": len(value["steps"]), "character_count": len(serialized),
                    "source_rows": len(variants), "canonical_source_rows": canonical_count,
                    "source_variant_count": len(counts)}))
    return examples


def select_diverse_split(examples: list[ReflectTraceExample], *, discovery_count: int = 5,
                         heldout_count: int = 5, seed: int = 20260911,
                         max_characters: int = 100_000) -> tuple[list[ReflectTraceExample], list[ReflectTraceExample]]:
    """Deterministically spread selections across views, sizes, and failure-label sets."""
    import random
    eligible = [e for e in examples if len(e.proof) <= max_characters]
    if len(eligible) < discovery_count + heldout_count:
        raise ValueError("Not enough eligible unique traces for the requested split")
    rng = random.Random(seed)
    combined = [e for e in eligible if "+" in e.view]
    single = [e for e in eligible if "+" not in e.view]
    total = discovery_count + heldout_count
    combined_count = (total + 1) // 2
    single_count = total - combined_count

    def quantiles(pool, count):
        rng.shuffle(pool)
        pool.sort(key=lambda e: len(e.proof))
        if len(pool) < count:
            raise ValueError("Not enough traces in a REFLECT view stratum")
        return [pool[min(len(pool) - 1, int((i + 0.5) * len(pool) / count))]
                for i in range(count)]

    a, b = quantiles(combined, combined_count), quantiles(single, single_count)
    chosen = []
    while a or b:
        if a:
            chosen.append(a.pop(0))
        if b:
            chosen.append(b.pop(0))
    discovery = chosen[:discovery_count]
    heldout = chosen[discovery_count:discovery_count + heldout_count]
    if {e.trace_id for e in discovery} & {e.trace_id for e in heldout}:
        raise AssertionError("REFLECT split leaked a trace ID")
    return discovery, heldout
