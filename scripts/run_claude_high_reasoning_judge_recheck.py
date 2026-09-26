#!/usr/bin/env python3
"""Rejudge the six strongest Opus 5 evaluation misses at max effort."""

from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil
import sys
import time

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.proof_fuzzer.agent_cli_client import ClaudeCodeProofFuzzerClient
from src.proof_fuzzer.judging import parse_judge_result


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
SOURCE_RUNS = {
    "arxiv_math": (
        "ArXivMath",
        "arxiv",
        Path(
            "logs/by_dataset/recent_math/runs/"
            "recent_math_5_frozen_eval_claude_opus5_medium_5x3_20260924"
        ),
    ),
    "tcs_open_problems": (
        "OpenAI-TCS",
        "tcs",
        Path(
            "logs/by_dataset/tcs_open_problems/"
            "opus5_snapshot120_frozen_eval_5x3_20260925"
        ),
    ),
}


@dataclass(frozen=True)
class Candidate:
    key: str
    dataset: str
    proof_id: str
    session_index: int
    mutation_sha256: str
    prompt_path: Path
    mutated_proof_path: Path
    introduced_error_path: Path
    original_missed_reviews: int


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n")


def locate_attempt(
    source_run: Path,
    session_index: int,
    mutation_sha256: str,
) -> Path:
    pattern = f"sessions/{session_index:04d}*/attempts/001/mutated_proof.md"
    matches = [
        path.parent
        for path in (REPOSITORY_ROOT / source_run).glob(pattern)
        if digest(path) == mutation_sha256
    ]
    if len(matches) != 1:
        raise ValueError(
            f"Expected one artifact for session {session_index}, found {len(matches)}"
        )
    return matches[0]


def select_candidates(dataset_key: str) -> tuple[Candidate, ...]:
    dataset, key_prefix, source_run = SOURCE_RUNS[dataset_key]
    results_path = REPOSITORY_ROOT / source_run / "results.json"
    rows = json.loads(results_path.read_text())
    ranked = sorted(
        (
            row
            for row in rows
            if row.get("arm") == "strategies" and row.get("valid") is True
        ),
        key=lambda row: (
            -sum(review.get("detection") == "missed" for review in row.get("reviews", ())),
            int(row["session_index"]),
        ),
    )[:6]
    candidates = []
    for row in ranked:
        missed = sum(
            review.get("detection") == "missed" for review in row.get("reviews", ())
        )
        if missed != 3:
            raise ValueError("The top six candidates must each be a three-of-three miss")
        session_index = int(row["session_index"])
        mutation_sha256 = str(row["mutation_sha256"])
        attempt = locate_attempt(source_run, session_index, mutation_sha256)
        candidates.append(
            Candidate(
                key=f"opus5_{key_prefix}_session_{session_index:04d}",
                dataset=dataset,
                proof_id=str(row["proof_id"]),
                session_index=session_index,
                mutation_sha256=mutation_sha256,
                prompt_path=attempt / "judge_prompt.txt",
                mutated_proof_path=attempt / "mutated_proof.md",
                introduced_error_path=attempt / "introduced_error.md",
                original_missed_reviews=missed,
            )
        )
    if len(candidates) != 6 or len({item.mutation_sha256 for item in candidates}) != 6:
        raise ValueError("Selection must contain six unique mutations")
    return tuple(candidates)


def relative(path: Path) -> str:
    return str(path.relative_to(REPOSITORY_ROOT))


def run_candidate(
    candidate: Candidate,
    output_root: Path,
    max_output_tokens: int,
) -> dict[str, object]:
    target = output_root / "candidates" / candidate.key
    target.mkdir(parents=True, exist_ok=False)
    for source, name in (
        (candidate.prompt_path, "judge_prompt.txt"),
        (candidate.mutated_proof_path, "mutated_proof.md"),
        (candidate.introduced_error_path, "introduced_error.md"),
    ):
        shutil.copyfile(source, target / name)

    record: dict[str, object] = {
        "key": candidate.key,
        "dataset": candidate.dataset,
        "proof_id": candidate.proof_id,
        "session_index": candidate.session_index,
        "mutation_sha256": candidate.mutation_sha256,
        "original_missed_reviews": candidate.original_missed_reviews,
        "status": "running",
    }
    started = time.monotonic()
    client = ClaudeCodeProofFuzzerClient(
        model="claude-opus-5",
        reasoning_effort="max",
        workspace_root=target / "workspaces",
        log_events=True,
        call_timeout_seconds=None,
        detect_repetitive_output=False,
        technical_retries=0,
        environment={"CLAUDE_CODE_MAX_OUTPUT_TOKENS": str(max_output_tokens)},
    )
    try:
        response = client.complete((target / "judge_prompt.txt").read_text())
        (target / "judge_response.txt").write_text(response)
        report = parse_judge_result(response)
        save(target / "parsed_report.json", report.to_dict())
        record.update(
            status="completed",
            response_kind=report.response_kind,
            errors_reported=len(report.detected_errors),
        )
    except Exception as error:
        (target / "error.txt").write_text(f"{type(error).__name__}: {error}\n")
        record.update(
            status="failed",
            error_type=type(error).__name__,
            error=str(error),
        )
    finally:
        client.close()
        record["elapsed_seconds"] = round(time.monotonic() - started, 3)
        save(target / "result.json", record)
    return record


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument(
        "--dataset",
        choices=sorted(SOURCE_RUNS),
        default="arxiv_math",
    )
    parser.add_argument("--workers", type=int, default=6)
    parser.add_argument("--max-output-tokens", type=int, default=128_000)
    parser.add_argument(
        "--keys",
        nargs="+",
        help="Run only these selected candidate keys, e.g. to relaunch interrupted calls.",
    )
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    if args.workers < 1:
        raise ValueError("--workers must be positive")
    if args.max_output_tokens < 1:
        raise ValueError("--max-output-tokens must be positive")

    candidates = select_candidates(args.dataset)
    selected_candidates = candidates
    if args.keys:
        unknown = sorted(set(args.keys) - {candidate.key for candidate in candidates})
        if unknown:
            raise ValueError(f"unknown candidate keys: {', '.join(unknown)}")
        candidates = [
            candidate for candidate in candidates if candidate.key in set(args.keys)
        ]
    if args.dry_run:
        for candidate in candidates:
            print(
                candidate.key,
                candidate.proof_id,
                candidate.original_missed_reviews,
                candidate.mutation_sha256,
            )
        return

    output_root = args.output_dir.resolve()
    output_root.mkdir(parents=True, exist_ok=False)
    manifest_candidates = []
    for candidate in candidates:
        item = asdict(candidate)
        item.update(
            prompt_path=relative(candidate.prompt_path),
            mutated_proof_path=relative(candidate.mutated_proof_path),
            introduced_error_path=relative(candidate.introduced_error_path),
        )
        manifest_candidates.append(item)
    save(
        output_root / "manifest.json",
        {
            "created_at": datetime.now(timezone.utc).isoformat(),
            "design": (
                f"rejudge the six strongest Opus 5 {selected_candidates[0].dataset} "
                "evaluation misses"
            ),
            "selection": (
                "top six valid strategy-guided mutations ranked by original missed "
                "reviews, then session index; all six were missed three of three times"
            ),
            "dataset_key": args.dataset,
            "dataset": candidates[0].dataset,
            "source_run": str(SOURCE_RUNS[args.dataset][2]),
            "provider": "claude-code",
            "model": "claude-opus-5",
            "reasoning_effort": "max",
            "fresh_thread_per_candidate": True,
            "key_subset": sorted(args.keys) if args.keys else None,
            "judge_queries": len(candidates),
            "workers": min(args.workers, len(candidates)),
            "call_timeout_seconds": None,
            "claude_code_max_output_tokens": args.max_output_tokens,
            "technical_retries": 0,
            "prompt_policy": "byte-for-byte copy of the archived blind-judge prompt",
            "candidates": manifest_candidates,
        },
    )

    results: list[dict[str, object]] = []
    with ThreadPoolExecutor(max_workers=min(args.workers, len(candidates))) as pool:
        futures = {
            pool.submit(
                run_candidate,
                candidate,
                output_root,
                args.max_output_tokens,
            ): candidate
            for candidate in candidates
        }
        for future in as_completed(futures):
            record = future.result()
            results.append(record)
            results.sort(key=lambda value: str(value["key"]))
            save(output_root / "results.json", results)
            print(record["key"], record["status"], flush=True)
    save(
        output_root / "summary.json",
        {
            "complete": len(results) == len(candidates),
            "completed": sum(row["status"] == "completed" for row in results),
            "failed": sum(row["status"] == "failed" for row in results),
            "results": results,
        },
    )


if __name__ == "__main__":
    main()
