#!/usr/bin/env python3
"""Cross-judge the strongest strategy-guided mutations with the other model."""

from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import shutil
import sys
import time

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.proof_fuzzer.judging import IntroducedErrorMatcher, parse_judge_result, parse_match_result
from src.proof_fuzzer.models import FuzzerMutationInstructions, ProofMutation
from src.proof_fuzzer.strategy_transfer import client, save


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class SourceRun:
    dataset_key: str
    dataset: str
    source_provider: str
    source_model: str
    results_path: Path
    artifact_roots: tuple[Path, ...]


@dataclass(frozen=True)
class SelectedCandidate:
    key: str
    dataset_key: str
    dataset: str
    source_provider: str
    source_model: str
    target_provider: str
    target_model: str
    target_reasoning_effort: str
    rank: int
    proof_id: str
    candidate: int
    session_index: int
    mutation_sha256: str
    original_missed_reviews: int
    original_review_count: int
    source_results_path: Path
    artifact_dir: Path
    prompt_path: Path
    original_proof_path: Path
    mutated_proof_path: Path
    introduced_error_path: Path


OLYMPIAD_GPT = Path(
    "logs/by_dataset/olympiad/"
    "olympiad_20_frozen_eval_gpt56sol_medium_5x3_20260924"
)
OLYMPIAD_CLAUDE = Path(
    "logs/by_dataset/olympiad/"
    "olympiad_20_frozen_eval_claude_opus5_default_5x3_20260922"
)
GRADUATE_GPT = Path(
    "logs/by_dataset/graduate_course/"
    "graduate_course_10_frozen_eval_gpt56sol_medium_5x3_20260923"
)
GRADUATE_CLAUDE = Path(
    "logs/by_dataset/graduate_course/"
    "graduate_course_10_frozen_eval_claude_opus5_medium_5x3_20260923_amended"
)
GRADUATE_CLAUDE_SOURCE = Path(
    "logs/by_dataset/graduate_course/"
    "graduate_course_10_frozen_eval_claude_opus5_medium_10x3_20260923"
)
RECENT_GPT = Path(
    "logs/by_dataset/recent_math/runs/"
    "recent_math_clean_all5_v1_gpt56sol_medium_25perarm_3judges_combined_20260923"
)
RECENT_GPT_BASE = Path(
    "logs/by_dataset/recent_math/runs/"
    "recent_math_clean_all5_v1_gpt56sol_medium_2judges_v2"
)
RECENT_GPT_EXTENSION = Path(
    "logs/by_dataset/recent_math/runs/"
    "recent_math_clean_all5_v1_gpt56sol_medium_25perarm_3judges_extension_20260923"
)
RECENT_CLAUDE = Path(
    "logs/by_dataset/recent_math/runs/"
    "recent_math_5_frozen_eval_claude_opus5_medium_5x3_20260924"
)


SOURCE_RUNS = (
    SourceRun("olympiad", "Olympiad", "codex", "gpt-5.6-sol",
              OLYMPIAD_GPT / "results.json", (OLYMPIAD_GPT,)),
    SourceRun("olympiad", "Olympiad", "claude-code", "claude-opus-5",
              OLYMPIAD_CLAUDE / "results.json", (OLYMPIAD_CLAUDE,)),
    SourceRun("graduate_course", "GraduateCourses", "codex", "gpt-5.6-sol",
              GRADUATE_GPT / "results.json", (GRADUATE_GPT,)),
    SourceRun("graduate_course", "GraduateCourses", "claude-code", "claude-opus-5",
              GRADUATE_CLAUDE / "results.json", (GRADUATE_CLAUDE, GRADUATE_CLAUDE_SOURCE)),
    SourceRun("recent_math", "ArXivMath", "codex", "gpt-5.6-sol",
              RECENT_GPT / "results.json", (RECENT_GPT_BASE, RECENT_GPT_EXTENSION)),
    SourceRun("recent_math", "ArXivMath", "claude-code", "claude-opus-5",
              RECENT_CLAUDE / "results.json", (RECENT_CLAUDE,)),
)


TARGETS = {
    "gpt-5.6-sol": ("claude-code", "claude-opus-5", "medium"),
    "claude-opus-5": ("codex", "gpt-5.6-sol", "medium"),
}


def repository_path(path: Path) -> Path:
    return path if path.is_absolute() else REPOSITORY_ROOT / path


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def safe_key(value: object) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]+", "_", str(value)).strip("_")


def select_rows(rows: list[dict[str, object]], top_k: int) -> list[dict[str, object]]:
    eligible = []
    for row in rows:
        if row.get("arm") != "strategies" or row.get("valid") is not True:
            continue
        mutation_hash = str(row.get("mutation_sha256", ""))
        if not re.fullmatch(r"[0-9a-f]{64}", mutation_hash):
            continue
        reviews = row.get("reviews", [])
        reviews = reviews if isinstance(reviews, list) else []
        enriched = dict(row)
        enriched["original_missed_reviews"] = sum(
            review.get("detection") == "missed"
            for review in reviews if isinstance(review, dict)
        )
        enriched["original_review_count"] = len(reviews)
        eligible.append(enriched)
    eligible.sort(key=lambda row: (
        -int(row["original_missed_reviews"]),
        str(row.get("proof_id", "")),
        int(row.get("candidate", 0)),
        int(row.get("session_index", 0)),
        str(row["mutation_sha256"]),
    ))
    unique = []
    seen_hashes = set()
    for row in eligible:
        mutation_hash = str(row["mutation_sha256"])
        if mutation_hash in seen_hashes:
            continue
        seen_hashes.add(mutation_hash)
        unique.append(row)
        if len(unique) == top_k:
            break
    if len(unique) != top_k:
        raise ValueError(f"Only {len(unique)} unique valid strategy candidates; need {top_k}")
    return unique


def candidate_artifact_dirs(root: Path):
    sessions = repository_path(root) / "sessions"
    if not sessions.is_dir():
        return
    for mutated in sessions.glob("*/attempts/001/mutated_proof.md"):
        yield mutated.parent


def resolve_artifacts(source: SourceRun, hashes: set[str]) -> dict[str, Path]:
    resolved: dict[str, Path] = {}
    for root in source.artifact_roots:
        for artifact_dir in candidate_artifact_dirs(root):
            mutation_hash = digest(artifact_dir / "mutated_proof.md")
            if mutation_hash in hashes and mutation_hash not in resolved:
                resolved[mutation_hash] = artifact_dir
    missing = sorted(hashes - resolved.keys())
    if missing:
        raise FileNotFoundError(
            f"Could not resolve {len(missing)} selected mutation artifacts for "
            f"{source.dataset}/{source.source_model}: {missing}"
        )
    return resolved


def judge_prompt_path(artifact_dir: Path) -> Path:
    for name in ("judge_prompt.txt", "judge_1_prompt.txt"):
        path = artifact_dir / name
        if path.is_file():
            return path
    raise FileNotFoundError(f"No archived blind-judge prompt in {artifact_dir}")


def build_selection(top_k: int = 10) -> list[SelectedCandidate]:
    selected: list[SelectedCandidate] = []
    for source in SOURCE_RUNS:
        results_path = repository_path(source.results_path)
        if not results_path.is_file():
            raise FileNotFoundError(results_path)
        rows = json.loads(results_path.read_text())
        chosen = select_rows(rows, top_k)
        artifacts = resolve_artifacts(
            source, {str(row["mutation_sha256"]) for row in chosen}
        )
        target_provider, target_model, target_effort = TARGETS[source.source_model]
        for rank, row in enumerate(chosen, 1):
            mutation_hash = str(row["mutation_sha256"])
            artifact_dir = artifacts[mutation_hash]
            required = {
                "original_proof_path": artifact_dir / "original_proof.md",
                "mutated_proof_path": artifact_dir / "mutated_proof.md",
                "introduced_error_path": artifact_dir / "introduced_error.md",
            }
            missing = [str(path) for path in required.values() if not path.is_file()]
            if missing:
                raise FileNotFoundError(f"Missing source artifacts: {missing}")
            proof_id = str(row["proof_id"])
            key = "__".join((
                source.dataset_key,
                "from_gpt56sol" if source.source_model == "gpt-5.6-sol" else "from_opus5",
                f"rank_{rank:02d}",
                safe_key(proof_id),
                f"candidate_{int(row.get('candidate', 0)):02d}",
            ))
            selected.append(SelectedCandidate(
                key=key,
                dataset_key=source.dataset_key,
                dataset=source.dataset,
                source_provider=source.source_provider,
                source_model=source.source_model,
                target_provider=target_provider,
                target_model=target_model,
                target_reasoning_effort=target_effort,
                rank=rank,
                proof_id=proof_id,
                candidate=int(row.get("candidate", 0)),
                session_index=int(row.get("session_index", 0)),
                mutation_sha256=mutation_hash,
                original_missed_reviews=int(row["original_missed_reviews"]),
                original_review_count=int(row["original_review_count"]),
                source_results_path=source.results_path,
                artifact_dir=artifact_dir.relative_to(REPOSITORY_ROOT),
                prompt_path=judge_prompt_path(artifact_dir).relative_to(REPOSITORY_ROOT),
                original_proof_path=required["original_proof_path"].relative_to(REPOSITORY_ROOT),
                mutated_proof_path=required["mutated_proof_path"].relative_to(REPOSITORY_ROOT),
                introduced_error_path=required["introduced_error_path"].relative_to(REPOSITORY_ROOT),
            ))
    if len({candidate.mutation_sha256 for candidate in selected}) != len(selected):
        raise ValueError("Selected mutations must be unique across all source cells")
    return selected


def serializable_candidate(candidate: SelectedCandidate) -> dict[str, object]:
    value = asdict(candidate)
    for key, item in tuple(value.items()):
        if isinstance(item, Path):
            value[key] = str(item)
    return value


def latest_metadata(root: Path) -> dict[str, object] | None:
    paths = list((root / "workspaces").glob("call_*/metadata.json"))
    if not paths:
        return None
    return json.loads(max(paths, key=lambda path: path.stat().st_mtime_ns).read_text())


def matcher_prompt(candidate: SelectedCandidate, report) -> str:
    original = repository_path(candidate.original_proof_path).read_text()
    mutated = repository_path(candidate.mutated_proof_path).read_text()
    explanation = repository_path(candidate.introduced_error_path).read_text()
    instructions = FuzzerMutationInstructions(
        False,
        (ProofMutation(
            kind="global_context",
            target="whole_proof",
            new_text=mutated,
            summary=explanation,
            propagate_downstream=False,
        ),),
        rationale=explanation,
    )
    prompt = IntroducedErrorMatcher(None).prompt(
        instructions=instructions,
        reports=(report,),
        original=original,
        mutated=mutated,
    )
    return (
        prompt
        + "\nFor raw_report, accept explicit detection in verbatim prose. "
          "No original review was run; compare the original text directly.\n"
    )


def run_candidate(
    candidate_spec: SelectedCandidate,
    output_root: Path,
    disable_call_timeout: bool,
) -> dict[str, object]:
    target = output_root / "candidates" / candidate_spec.key
    target.mkdir(parents=True, exist_ok=True)
    result_path = target / "result.json"
    if result_path.is_file():
        existing = json.loads(result_path.read_text())
        if existing.get("status") == "completed":
            return existing

    for source, name in (
        (candidate_spec.prompt_path, "judge_prompt.txt"),
        (candidate_spec.original_proof_path, "original_proof.md"),
        (candidate_spec.mutated_proof_path, "mutated_proof.md"),
        (candidate_spec.introduced_error_path, "introduced_error.md"),
    ):
        destination = target / name
        if not destination.exists():
            shutil.copyfile(repository_path(source), destination)
    if digest(target / "mutated_proof.md") != candidate_spec.mutation_sha256:
        raise ValueError(f"Copied mutation hash mismatch for {candidate_spec.key}")

    record: dict[str, object] = {
        **serializable_candidate(candidate_spec),
        "status": "running",
    }
    started = time.monotonic()
    try:
        judge_response_path = target / "judge_response.txt"
        judge_root = target / "judge"
        if judge_response_path.is_file():
            response = judge_response_path.read_text()
        else:
            judge = client(
                judge_root,
                candidate_spec.target_model,
                candidate_spec.target_reasoning_effort,
                provider=candidate_spec.target_provider,
                disable_call_timeout=disable_call_timeout,
            )
            try:
                response = judge.complete((target / "judge_prompt.txt").read_text())
            finally:
                judge.close()
            judge_response_path.write_text(response)
        report = parse_judge_result(response)
        if report.response_kind != "error_inventory":
            raise ValueError("Cross-model judge did not return an error inventory")
        save(target / "parsed_report.json", report.to_dict())

        match_response_path = target / "matcher_response.txt"
        match_prompt_path = target / "matcher_prompt.txt"
        prompt = matcher_prompt(candidate_spec, report)
        match_prompt_path.write_text(prompt)
        if match_response_path.is_file():
            match_response = match_response_path.read_text()
        else:
            matcher_root = target / "matcher"
            matcher = client(
                matcher_root,
                candidate_spec.target_model,
                candidate_spec.target_reasoning_effort,
                provider=candidate_spec.target_provider,
                disable_call_timeout=disable_call_timeout,
            )
            try:
                match_response = matcher.complete(prompt)
            finally:
                matcher.close()
            match_response_path.write_text(match_response)
        match = parse_match_result(match_response)
        save(target / "match.json", match)
        record.update(
            status="completed",
            detection="caught" if match["introduced_error_found"] else "missed",
            errors_reported=len(report.detected_errors),
            match=match,
            judge_metadata=latest_metadata(judge_root),
            matcher_metadata=latest_metadata(target / "matcher"),
        )
    except Exception as error:
        (target / "error.txt").write_text(f"{type(error).__name__}: {error}\n")
        record.update(
            status="failed",
            error_type=type(error).__name__,
            error=str(error),
            judge_metadata=latest_metadata(target / "judge"),
            matcher_metadata=latest_metadata(target / "matcher"),
        )
    record["elapsed_seconds"] = round(time.monotonic() - started, 3)
    save(result_path, record)
    return record


def summarize(results: list[dict[str, object]], planned: int) -> dict[str, object]:
    completed = [row for row in results if row.get("status") == "completed"]
    cells: dict[str, dict[str, object]] = {}
    for row in completed:
        key = f"{row['dataset_key']}__from_{row['source_model']}"
        cell = cells.setdefault(key, {
            "dataset": row["dataset"],
            "source_model": row["source_model"],
            "judge_model": row["target_model"],
            "completed": 0,
            "caught": 0,
            "missed": 0,
        })
        cell["completed"] += 1
        cell[str(row["detection"])] += 1
    return {
        "complete": len(results) == planned and len(completed) == planned,
        "planned": planned,
        "finished": len(results),
        "completed": len(completed),
        "failed": sum(row.get("status") == "failed" for row in results),
        "caught": sum(row.get("detection") == "caught" for row in completed),
        "missed": sum(row.get("detection") == "missed" for row in completed),
        "cells": cells,
    }


def reconcile_manifest(
    recorded: dict[str, object],
    requested: dict[str, object],
    completed_candidates: int,
) -> tuple[dict[str, object], bool]:
    ignored = {"created_at", "protocol_amendments", "call_timeout_seconds"}
    core = lambda value: {key: item for key, item in value.items() if key not in ignored}
    if core(recorded) != core(requested):
        raise ValueError("Existing cross-model manifest does not match this invocation")
    old_timeout = recorded.get("call_timeout_seconds")
    new_timeout = requested.get("call_timeout_seconds")
    if old_timeout == new_timeout:
        return recorded, False
    if old_timeout != 1200 or new_timeout is not None:
        raise ValueError(
            f"Unsupported call-timeout amendment: {old_timeout!r} to {new_timeout!r}"
        )
    amended = dict(recorded)
    amended["call_timeout_seconds"] = None
    amendments = list(amended.get("protocol_amendments", []))
    amendments.append({
        "amended_at": datetime.now(timezone.utc).isoformat(),
        "field": "call_timeout_seconds",
        "from": 1200,
        "to": None,
        "reason": "User requested that the three timed-out cross-model judge calls resume without a hard timeout.",
        "completed_candidates_before_amendment": completed_candidates,
    })
    amended["protocol_amendments"] = amendments
    return amended, True


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--workers", type=int, default=40)
    parser.add_argument("--top-k", type=int, default=10)
    parser.add_argument("--no-call-timeout", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    if args.workers < 1 or args.top_k < 1:
        raise ValueError("--workers and --top-k must be positive")
    candidates = build_selection(args.top_k)
    if args.dry_run:
        for candidate_spec in candidates:
            print(json.dumps(serializable_candidate(candidate_spec), sort_keys=True))
        return

    output_root = args.output_dir.resolve()
    output_root.mkdir(parents=True, exist_ok=True)
    manifest_path = output_root / "manifest.json"
    manifest = {
        "created_at": datetime.now(timezone.utc).isoformat(),
        "design": "cross-model rejudging of strongest valid strategy-guided mutations",
        "selection": (
            "Within each dataset/source-model cell, rank unique valid strategy-guided "
            "mutations by descending original missed-review count, then proof ID, candidate "
            "index, session index, and mutation hash; retain the first top_k."
        ),
        "datasets": ["olympiad", "graduate_course", "recent_math"],
        "source_models": ["gpt-5.6-sol", "claude-opus-5"],
        "cross_judges": {
            "gpt-5.6-sol mutations": "claude-opus-5 medium via Claude Code",
            "claude-opus-5 mutations": "gpt-5.6-sol medium via Codex",
        },
        "top_k_per_dataset_model_pair": args.top_k,
        "judge_queries": len(candidates),
        "matcher_queries": len(candidates),
        "workers": args.workers,
        "call_timeout_seconds": None if args.no_call_timeout else 1200,
        "fresh_judge_and_matcher_session_per_candidate": True,
        "prompt_policy": "byte-for-byte copy of each candidates archived blind-judge prompt",
        "matcher_policy": "exact or logically equivalent causal diagnosis; exact_only parser",
        "candidates": [serializable_candidate(candidate_spec) for candidate_spec in candidates],
    }
    if manifest_path.is_file():
        recorded = json.loads(manifest_path.read_text())
        existing_results = (
            json.loads((output_root / "results.json").read_text())
            if (output_root / "results.json").is_file() else []
        )
        recorded, changed = reconcile_manifest(
            recorded,
            manifest,
            sum(row.get("status") == "completed" for row in existing_results),
        )
        if changed:
            save(manifest_path, recorded)
    else:
        save(manifest_path, manifest)

    results_path = output_root / "results.json"
    existing = json.loads(results_path.read_text()) if results_path.is_file() else []
    by_key = {str(row["key"]): row for row in existing}
    pending = [candidate_spec for candidate_spec in candidates
               if by_key.get(candidate_spec.key, {}).get("status") != "completed"]
    with ThreadPoolExecutor(max_workers=min(args.workers, len(pending) or 1)) as pool:
        futures = {
            pool.submit(run_candidate, candidate_spec, output_root, args.no_call_timeout): candidate_spec
            for candidate_spec in pending
        }
        for future in as_completed(futures):
            record = future.result()
            by_key[str(record["key"])] = record
            ordered = [by_key[candidate_spec.key] for candidate_spec in candidates
                       if candidate_spec.key in by_key]
            save(results_path, ordered)
            save(output_root / "summary.json", summarize(ordered, len(candidates)))
            print(record["key"], record["status"], record.get("detection", ""), flush=True)
    ordered = [by_key[candidate_spec.key] for candidate_spec in candidates
               if candidate_spec.key in by_key]
    save(results_path, ordered)
    save(output_root / "summary.json", summarize(ordered, len(candidates)))


if __name__ == "__main__":
    main()
