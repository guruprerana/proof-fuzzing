#!/usr/bin/env python3
"""Prepare and independently audit ten recent research-paper candidates."""

from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
import json
from pathlib import Path
import tarfile

from src.proof_fuzzer.codex_client import CodexProofFuzzerClient
from src.proof_fuzzer.judging import load_json_object


SHORTLIST = (
    "2507.04819", "2208.09962",  # algebra and number theory
    "2211.03918", "2411.16620",  # geometry and topology
    "2412.18436", "2507.06076",  # analysis and PDE
    "2505.12810", "2208.09131",  # probability and combinatorics
    "2412.13499", "2503.13728",  # logic and dynamics
)

PROMPT = r'''You are performing an unchanged-source baseline audit of a recent mathematical
research paper before it can enter a proof-mutation dataset. Read candidate_metadata.json and the complete
LaTeX source bundle paper_source.txt.

Audit the central theorem/proof chains, including definitions, hypotheses, lemma dependencies,
quantifiers, exceptional cases, signs, indices, well-definedness, compactness/limit transitions,
and conclusions stronger than established. A finding must identify a concrete false statement or
invalid inference and explain its mathematical consequence. Give a counterexample or explicit
failure mechanism whenever feasible.

Do not report style, density, missing pedagogical background, a routine calculation merely left to
the reader, use of a clearly cited standard theorem, or inability to verify a long argument as an
error. Do not browse. Treat the supplied source as the complete evidence. If source ordering or
macros make a point impossible to resolve, mark it uncertain rather than inventing a defect.

Return exactly one JSON object:
{
  "verdict": "pass | minor_findings | major_findings | uncertain",
  "confidence": 0.0,
  "central_results_checked": ["specific theorem or chain"],
  "findings": [
    {
      "location": "theorem/lemma/section and source locator",
      "severity": "minor | major | critical",
      "confidence": 0.0,
      "claim": "claim being assessed",
      "error": "concrete false statement or invalid inference",
      "witness_or_failure_mechanism": "counterexample or exact broken dependency",
      "consequence": "local and downstream effect"
    }
  ],
  "dataset_recommendation": "accept | reject | specialist_review",
  "summary": "concise evidence-based assessment"
}'''


def source_bundle(path: Path) -> str:
    parts = []
    with tarfile.open(path, "r:*") as archive:
        for member in sorted(archive.getmembers(), key=lambda item: item.name):
            if not member.isfile() or not member.name.lower().endswith((".tex", ".ltx")):
                continue
            if member.size > 8_000_000:
                continue
            handle = archive.extractfile(member)
            if handle is None:
                continue
            content = handle.read().decode("utf-8", errors="replace")
            parts.append(f"\n\n===== BEGIN SOURCE FILE: {member.name} =====\n\n{content}"
                         f"\n\n===== END SOURCE FILE: {member.name} =====\n")
    if not parts:
        raise ValueError(f"No TeX source in {path}")
    return "".join(parts)


def audit_one(*, row: dict[str, object], audit_index: int, root: Path,
              model: str, effort: str) -> dict[str, object]:
    paper_root = root / str(row["arxiv_id"]) / f"audit_{audit_index}"
    paper_root.mkdir(parents=True, exist_ok=True)
    archive = Path(str(row["source_archive"]))
    bundle = source_bundle(archive)
    metadata = json.dumps(row, indent=2, ensure_ascii=False)
    (paper_root / "prompt.txt").write_text(PROMPT)
    (paper_root / "candidate_metadata.json").write_text(metadata)
    (paper_root / "paper_source.txt").write_text(bundle)
    llm = CodexProofFuzzerClient(
        model=model,
        reasoning_effort=effort,
        workspace_root=paper_root / "workspace",
        log_events=True,
        call_timeout_seconds=900,
        detect_repetitive_output=True,
        technical_retries=1,
    )
    try:
        response = llm.complete_with_files(
            PROMPT,
            {"candidate_metadata.json": metadata, "paper_source.txt": bundle},
        )
        (paper_root / "response.txt").write_text(response)
        try:
            parsed = load_json_object(response)
            status = "parsed"
        except Exception as error:
            parsed = {"verdict": "technical_failure", "parse_error": repr(error)}
            status = "parse_failed"
        result = {
            "arxiv_id": row["arxiv_id"],
            "audit_index": audit_index,
            "status": status,
            "model": model,
            "reasoning_effort": effort,
            "result": parsed,
        }
        (paper_root / "result.json").write_text(
            json.dumps(result, indent=2, ensure_ascii=False) + "\n"
        )
        return result
    finally:
        llm.close()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--manifest", type=Path,
        default=Path("local_datasets/recent_math_candidates_v1/manifest.json"),
    )
    parser.add_argument(
        "--output-dir", type=Path,
        default=Path("logs/by_dataset/recent_math/audits/recent_math_shortlist_v1"),
    )
    parser.add_argument("--model", default="gpt-5.6-sol")
    parser.add_argument("--reasoning-effort", default="high")
    parser.add_argument("--audits-per-paper", type=int, default=2)
    parser.add_argument("--workers", type=int, default=5)
    parser.add_argument("--ids", nargs="+", help="Override the default ten-paper shortlist")
    args = parser.parse_args()

    manifest = json.loads(args.manifest.read_text())
    ids = tuple(args.ids) if args.ids else SHORTLIST
    rows_by_id = {row["arxiv_id"]: row for row in manifest["selected"] + manifest["reserve"]}
    missing = [arxiv_id for arxiv_id in ids if arxiv_id not in rows_by_id]
    if missing:
        raise ValueError(f"Shortlist IDs absent from source-screened manifest: {missing}")
    shortlist = [rows_by_id[arxiv_id] for arxiv_id in ids]
    if not all(row.get("source_readable") for row in shortlist):
        raise ValueError("Every shortlisted paper must have readable TeX source")

    args.output_dir.mkdir(parents=True, exist_ok=False)
    shortlist_payload = {
        "created_at": datetime.now(timezone.utc).isoformat(),
        "status": "baseline_audit_in_progress",
        "model": args.model,
        "reasoning_effort": args.reasoning_effort,
        "audits_per_paper": args.audits_per_paper,
        "selection_rule": "explicit source-screened CC BY shortlist; default is two published papers per area",
        "papers": shortlist,
    }
    (args.output_dir / "shortlist.json").write_text(
        json.dumps(shortlist_payload, indent=2, ensure_ascii=False) + "\n"
    )

    jobs = [
        (row, audit_index)
        for row in shortlist
        for audit_index in range(1, args.audits_per_paper + 1)
    ]
    results = []
    with ThreadPoolExecutor(max_workers=min(args.workers, len(jobs))) as pool:
        futures = {
            pool.submit(
                audit_one,
                row=row,
                audit_index=audit_index,
                root=args.output_dir,
                model=args.model,
                effort=args.reasoning_effort,
            ): (row["arxiv_id"], audit_index)
            for row, audit_index in jobs
        }
        for future in as_completed(futures):
            arxiv_id, audit_index = futures[future]
            try:
                result = future.result()
            except Exception as error:
                result = {
                    "arxiv_id": arxiv_id,
                    "audit_index": audit_index,
                    "status": "technical_failure",
                    "error": repr(error),
                }
            results.append(result)
            print(arxiv_id, audit_index, result["status"], flush=True)
            (args.output_dir / "results.partial.json").write_text(
                json.dumps(results, indent=2, ensure_ascii=False) + "\n"
            )

    results.sort(key=lambda row: (ids.index(str(row["arxiv_id"])), row["audit_index"]))
    (args.output_dir / "results.json").write_text(
        json.dumps(results, indent=2, ensure_ascii=False) + "\n"
    )
    shortlist_payload["status"] = "baseline_audit_complete"
    shortlist_payload["completed_at"] = datetime.now(timezone.utc).isoformat()
    (args.output_dir / "shortlist.json").write_text(
        json.dumps(shortlist_payload, indent=2, ensure_ascii=False) + "\n"
    )


if __name__ == "__main__":
    main()
