#!/usr/bin/env python3
"""Rejudge six strong GPT-5.6-sol misses at ultra reasoning effort."""

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

from src.proof_fuzzer.codex_client import CodexProofFuzzerClient
from src.proof_fuzzer.judging import parse_judge_result


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
TCS_RUN = Path(
    "logs/by_dataset/tcs_open_problems/"
    "ten_matched_50_gpt-5.6-sol_medium_20260909_202502"
)
RECENT_BASE_RUN = Path(
    "logs/by_dataset/recent_math/runs/"
    "recent_math_clean_all5_v1_gpt56sol_medium_2judges_v2"
)
RECENT_EXTENSION_RUN = Path(
    "logs/by_dataset/recent_math/runs/"
    "recent_math_clean_all5_v1_gpt56sol_medium_25perarm_3judges_extension_20260923"
)
RECENT_COMBINED_RESULTS = Path(
    "logs/by_dataset/recent_math/runs/"
    "recent_math_clean_all5_v1_gpt56sol_medium_25perarm_3judges_combined_20260923/"
    "results.json"
)


@dataclass(frozen=True)
class Candidate:
    key: str
    dataset: str
    proof_id: str
    mutation_sha256: str
    prompt_path: Path
    mutated_proof_path: Path
    introduced_error_path: Path
    results_path: Path
    original_missed_reviews: int


def tcs_candidate(
    attempt: int,
    proof_id: str,
    mutation_sha256: str,
    original_missed_reviews: int = 3,
) -> Candidate:
    folder = TCS_RUN / "attempts" / f"{attempt:03d}"
    return Candidate(
        key=f"tcs_attempt_{attempt:03d}",
        dataset="TCS open problems",
        proof_id=proof_id,
        mutation_sha256=mutation_sha256,
        prompt_path=folder / "judge_1_prompt.txt",
        mutated_proof_path=folder / "mutated_proof.md",
        introduced_error_path=folder / "introduced_error.md",
        results_path=TCS_RUN / "results.json",
        original_missed_reviews=original_missed_reviews,
    )


def recent_candidate(
    key: str,
    run: Path,
    session: int,
    proof_id: str,
    mutation_sha256: str,
    original_missed_reviews: int = 3,
) -> Candidate:
    folder = run / "sessions" / f"{session:04d}" / "attempts" / "001"
    return Candidate(
        key=key,
        dataset="Recent mathematical research",
        proof_id=proof_id,
        mutation_sha256=mutation_sha256,
        prompt_path=folder / "judge_prompt.txt",
        mutated_proof_path=folder / "mutated_proof.md",
        introduced_error_path=folder / "introduced_error.md",
        results_path=RECENT_COMBINED_RESULTS,
        original_missed_reviews=original_missed_reviews,
    )


INITIAL_CANDIDATES = (
    tcs_candidate(
        4,
        "01_high_dimensional_sphere_packing",
        "978d5109a38a3b3b0836c09a6baec03e80f102ef1068c3f1b4b6fb0ec540f473",
    ),
    tcs_candidate(
        8,
        "02_binary_and_spherical_codes",
        "192a338fcbbfba2320b9deeb4ac1bc8eb2d5e7f5a6951906563def028d3ddb64",
    ),
    tcs_candidate(
        19,
        "02_binary_and_spherical_codes",
        "9df37afa681c3a8d511fdc2e8bc8606ce257dfe8fb12f1bdbbeb690d6a1e92b3",
    ),
    recent_candidate(
        "recent_arxiv_2501_05622",
        RECENT_EXTENSION_RUN,
        3,
        "arxiv_2501_05622",
        "4a61bf6e2d3728166d962b9825abf0cd659ec6f8ccf41b283ed36b9b2d06ee5e",
    ),
    recent_candidate(
        "recent_arxiv_2505_05324",
        RECENT_BASE_RUN,
        14,
        "arxiv_2505_05324",
        "ad4f02320a3d88769edb88ad2efdba45e43ccded746460ba305748d74924e0ea",
    ),
    recent_candidate(
        "recent_arxiv_2507_21862",
        RECENT_BASE_RUN,
        15,
        "arxiv_2507_21862",
        "428262b7c4c7fd852dff85723bb36ce84cfc9a2242dcc318dd46daa403d278ce",
    ),
)

EXTENSION_CANDIDATES = (
    tcs_candidate(
        14,
        "01_high_dimensional_sphere_packing",
        "9606981a359f0017b51f54ef46a1fde966028dfa3bff06374e9acef712beaaf3",
        2,
    ),
    tcs_candidate(
        31,
        "02_binary_and_spherical_codes",
        "e3c293eda672eab5a5ef3de8d67789245a76666543799121055ac6f9d9b41235",
        2,
    ),
    tcs_candidate(
        41,
        "01_high_dimensional_sphere_packing",
        "e9642e1184abe3512c6e290763b9af810cb9284edc12835487267e620a0cf66f",
        2,
    ),
    recent_candidate(
        "recent_arxiv_2501_05622_candidate_3",
        RECENT_BASE_RUN,
        3,
        "arxiv_2501_05622",
        "3f686370d9bec17fbf195e021680b0233c0708ae006b88ef7fe51dd766717664",
        3,
    ),
    recent_candidate(
        "recent_arxiv_2405_19197_candidate_2",
        RECENT_BASE_RUN,
        6,
        "arxiv_2405_19197",
        "8204aed06afbf51eeec9ddd4851a9056b63fcae9a3a6b3fca8bd90400c7194a5",
        2,
    ),
    recent_candidate(
        "recent_arxiv_2505_05324_candidate_2",
        RECENT_BASE_RUN,
        28,
        "arxiv_2505_05324",
        "11d74af69e74f32d5a07d8fd594b3fea7bcdb790a06e1b80fb2aabdca0a8bba4",
        2,
    ),
)

BATCHES = {
    "initial": INITIAL_CANDIDATES,
    "extension": EXTENSION_CANDIDATES,
}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n")


def repo_path(path: Path) -> Path:
    return REPOSITORY_ROOT / path


def validate_candidate(candidate: Candidate) -> None:
    required = (
        candidate.prompt_path,
        candidate.mutated_proof_path,
        candidate.introduced_error_path,
        candidate.results_path,
    )
    missing = [str(path) for path in required if not repo_path(path).is_file()]
    if missing:
        raise FileNotFoundError(f"Missing source artifacts for {candidate.key}: {missing}")
    actual_hash = digest(repo_path(candidate.mutated_proof_path))
    if actual_hash != candidate.mutation_sha256:
        raise ValueError(
            f"Mutation hash mismatch for {candidate.key}: {actual_hash}"
        )
    rows = json.loads(repo_path(candidate.results_path).read_text())
    matching = [
        row
        for row in rows
        if row.get("mutation_sha256") == candidate.mutation_sha256
        and row.get("proof_id") == candidate.proof_id
        and row.get("arm") == "strategies"
        and row.get("valid") is True
        and sum(
            review.get("detection") == "missed"
            for review in row.get("reviews", ())
        )
        == candidate.original_missed_reviews
    ]
    if not matching:
        raise ValueError(
            f"{candidate.key} is not a valid strategy-guided "
            f"{candidate.original_missed_reviews}-of-three miss"
        )


def run_candidate(candidate: Candidate, output_root: Path) -> dict[str, object]:
    target = output_root / "candidates" / candidate.key
    target.mkdir(parents=True, exist_ok=False)
    prompt = repo_path(candidate.prompt_path).read_text()
    shutil.copyfile(repo_path(candidate.prompt_path), target / "judge_prompt.txt")
    shutil.copyfile(repo_path(candidate.mutated_proof_path), target / "mutated_proof.md")
    shutil.copyfile(
        repo_path(candidate.introduced_error_path), target / "introduced_error.md"
    )
    started = time.monotonic()
    client = CodexProofFuzzerClient(
        model="gpt-5.6-sol",
        reasoning_effort="ultra",
        workspace_root=target / "workspaces",
        log_events=True,
        call_timeout_seconds=None,
        detect_repetitive_output=False,
        technical_retries=0,
    )
    record: dict[str, object] = {
        "key": candidate.key,
        "dataset": candidate.dataset,
        "proof_id": candidate.proof_id,
        "mutation_sha256": candidate.mutation_sha256,
        "status": "running",
    }
    try:
        response = client.complete(prompt)
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
    parser.add_argument("--workers", type=int, default=6)
    parser.add_argument("--batch", choices=tuple(BATCHES), default="initial")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    if args.workers < 1:
        raise ValueError("--workers must be positive")
    candidates = BATCHES[args.batch]
    for candidate in candidates:
        validate_candidate(candidate)
    if len({candidate.mutation_sha256 for candidate in candidates}) != len(candidates):
        raise ValueError("Selected mutations must have six unique hashes")
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
            prompt_path=str(candidate.prompt_path),
            mutated_proof_path=str(candidate.mutated_proof_path),
            introduced_error_path=str(candidate.introduced_error_path),
            results_path=str(candidate.results_path),
        )
        manifest_candidates.append(item)
    save(
        output_root / "manifest.json",
        {
            "created_at": datetime.now(timezone.utc).isoformat(),
            "design": "rejudge six high-performing valid strategy-guided misses",
            "batch": args.batch,
            "selection": (
                "three unique highest remaining GPT-5.6-sol misses per dataset; "
                "recent-research selections prefer distinct source papers when tied"
            ),
            "provider": "codex",
            "model": "gpt-5.6-sol",
            "reasoning_effort": "ultra",
            "fresh_thread_per_candidate": True,
            "judge_queries": len(candidates),
            "call_timeout_seconds": None,
            "technical_retries": 0,
            "prompt_policy": "byte-for-byte copy of the candidate's archived blind-judge prompt",
            "candidates": manifest_candidates,
        },
    )

    results = []
    with ThreadPoolExecutor(max_workers=min(args.workers, len(candidates))) as pool:
        futures = {
            pool.submit(run_candidate, candidate, output_root): candidate
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
