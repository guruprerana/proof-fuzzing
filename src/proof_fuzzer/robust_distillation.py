"""Distill strategies only from independently replicated judge misses."""

from datetime import datetime, timezone
import json
from pathlib import Path

from .strategy_transfer import _validate_strategy, client, digest, save


def collect_replicated_evidence(run_roots: list[Path], required_misses: int = 2,
                                allow_incomplete: bool = False) -> list[dict]:
    """Collect arm-blind evidence from complete frozen evaluations."""
    if not run_roots:
        raise ValueError("At least one source run is required")
    evidence = []
    seen_hashes = set()
    for root in run_roots:
        status = json.loads((root / "status.json").read_text())
        summary = json.loads((root / "summary.json").read_text())
        if (not status.get("complete") or not summary.get("complete")) and not allow_incomplete:
            raise ValueError(f"Source evaluation is incomplete: {root}")
        for row in json.loads((root / "results.json").read_text()):
            misses = sum(review.get("detection") == "missed"
                         for review in row.get("reviews", ()))
            mutation_hash = row.get("mutation_sha256")
            if (row.get("valid") is not True or misses < required_misses
                    or not mutation_hash or mutation_hash in seen_hashes):
                continue
            seen_hashes.add(mutation_hash)
            evidence.append({
                "proof_id": row["proof_id"],
                "replicated_misses": misses,
                "introduced_error": row.get("introduced_error", ""),
                "mutation_diff": row.get("mutation_diff", ""),
                "validity_rationale": row.get("validity", {}).get("rationale", ""),
                "blind_review_detections": [review.get("detection")
                                             for review in row.get("reviews", ())],
            })
    return evidence


def distill_replicated_library(*, run_roots: list[Path], output_dir: Path,
                               model: str = "gpt-5.6-terra",
                               reasoning_effort: str = "medium",
                               required_misses: int = 2,
                               allow_incomplete_discovery: bool = False) -> Path:
    """Create a frozen library aligned to the replicated-miss endpoint."""
    roots = [root.resolve() for root in run_roots]
    evidence = collect_replicated_evidence(
        roots, required_misses, allow_incomplete=allow_incomplete_discovery)
    if not evidence:
        raise ValueError("No independently replicated misses were found")
    output = output_dir.resolve()
    output.mkdir(parents=True, exist_ok=False)
    evidence_text = json.dumps(evidence, indent=2, ensure_ascii=False)
    (output / "replicated_evidence.json").write_text(evidence_text)
    prompt = f"""Distill a reusable mathematical proof-fuzzing strategy library from
replicated_evidence.json. Every included mutation was independently validated as genuine and
missed by at least {required_misses} of 3 blind reviews. Merge semantically equivalent mechanisms;
do not weight repeats as independent ideas. Preserve the subtle implementation details that likely
made a flaw hard to detect, plus applicability conditions and concrete validity checks. Exclude
dataset IDs, proof-specific names and constants, experimental-arm labels, and instructions to the
judge. Return only Markdown of at most 20,000 characters with headings Strategies:, Do not:, and
Before returning:."""
    (output / "prompt.txt").write_text(prompt)
    llm = client(output / "model", model, reasoning_effort)
    try:
        response = llm.complete_with_files(prompt, {"replicated_evidence.json": evidence_text})
        (output / "response.md").write_text(response)
        strategy = _validate_strategy(response)
        strategy_path = output / "strategies.md"
        strategy_path.write_text(strategy)
        save(output / "manifest.json", {
            "created_at": datetime.now(timezone.utc).isoformat(),
            "model": model,
            "reasoning_effort": reasoning_effort,
            "source_runs": [str(root) for root in roots],
            "source_result_sha256": {
                str(root): digest((root / "results.json").read_text()) for root in roots},
            "required_missed_reviews": required_misses,
            "source_runs_complete": all(json.loads((root / "status.json").read_text())
                                        .get("complete") for root in roots),
            "exploratory_incomplete_sources_allowed": allow_incomplete_discovery,
            "inference_policy": "Source evidence is discovery-only; no inferential claim is made from it. Any transfer claim requires a fresh frozen evaluation.",
            "evidence_candidates": len(evidence),
            "strategy_sha256": digest(strategy),
            "arm_labels_withheld_from_distillation": True,
        })
        return strategy_path
    finally:
        llm.close()
