"""Preregistered, fresh-session evaluation of a frozen strategy library."""

from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
import json
from math import comb
from pathlib import Path
import random

from .strategy_transfer import (
    SAFEGUARDED_CALL_TIMEOUT_SECONDS, digest, example_metadata, proof_key, run_session,
    save, _validate_strategy,
)


def selector_for(proof) -> str:
    return str(getattr(proof, "selector", proof.example_id))


def exact_mcnemar_one_sided(strategy_only: int, generic_only: int) -> float:
    """Exact P[X >= strategy_only] for discordant pairs under p=1/2."""
    if min(strategy_only, generic_only) < 0:
        raise ValueError("Discordant counts must be nonnegative")
    discordant = strategy_only + generic_only
    if not discordant:
        return 1.0
    return sum(comb(discordant, k) for k in range(strategy_only, discordant + 1)) / 2**discordant


def _candidate_success(row: dict, required_missed_reviews: int) -> bool:
    return (row.get("valid") is True and
            sum(review.get("detection") == "missed" for review in row.get("reviews", ()))
            >= required_missed_reviews)


def summarize_frozen(rows: list[dict], proofs: list, attempts_per_arm: int, alpha: float,
                     required_missed_reviews: int = 2,
                     reviews_per_valid_candidate: int = 3) -> dict:
    outcomes = {}
    for proof in proofs:
        arms = {}
        for arm in ("generic", "strategies"):
            selected = [row for row in rows
                        if row["proof_id"] == proof.example_id and row["arm"] == arm]
            arms[arm] = {
                "completed_candidates": len(selected),
                "valid_candidates": sum(row.get("valid") is True for row in selected),
                "successful_candidates": sum(
                    _candidate_success(row, required_missed_reviews) for row in selected),
                "success": any(_candidate_success(row, required_missed_reviews)
                               for row in selected),
            }
        outcomes[proof.example_id] = arms

    complete_proofs = [proof.example_id for proof in proofs if all(
        outcomes[proof.example_id][arm]["completed_candidates"] == attempts_per_arm
        for arm in ("generic", "strategies"))]
    pairs = [outcomes[proof_id] for proof_id in complete_proofs]
    strategy_only = sum(p["strategies"]["success"] and not p["generic"]["success"] for p in pairs)
    generic_only = sum(p["generic"]["success"] and not p["strategies"]["success"] for p in pairs)
    both = sum(p["generic"]["success"] and p["strategies"]["success"] for p in pairs)
    neither = len(pairs) - strategy_only - generic_only - both
    p_value = exact_mcnemar_one_sided(strategy_only, generic_only)
    strategy_successes = strategy_only + both
    generic_successes = generic_only + both
    return {
        "complete": len(complete_proofs) == len(proofs),
        "completed_candidates": len(rows),
        "planned_candidates": 2 * len(proofs) * attempts_per_arm,
        "primary_endpoint": (
            "proof has >=1 valid candidate missed by >="
            f"{required_missed_reviews} of {reviews_per_valid_candidate} reviews"),
        "independent_unit": "proof",
        "alpha": alpha,
        "test": "exact one-sided paired McNemar/binomial test",
        "complete_proofs": len(complete_proofs),
        "strategy_successes": strategy_successes,
        "generic_successes": generic_successes,
        "strategy_only": strategy_only,
        "generic_only": generic_only,
        "both": both,
        "neither": neither,
        "paired_risk_difference": ((strategy_successes - generic_successes) / len(pairs)
                                   if pairs else None),
        "p_value": p_value,
        "significant_strategy_transfer": bool(
            len(complete_proofs) == len(proofs) and strategy_only > generic_only
            and p_value <= alpha),
        "proof_outcomes": outcomes,
    }


def run_frozen_evaluation(*, heldout: list, strategy_path: Path, storage_dir: Path,
                          model: str = "gpt-5.6-luna", reasoning_effort: str = "medium",
                          provider: str = "codex",
                          seed: int = 20260913, attempts_per_arm: int = 3,
                          alpha: float = 0.01, workers: int = 5,
                          dry_run: bool = False,
                          reviews_per_valid_candidate: int = 3,
                          required_missed_reviews: int | None = None,
                          strategy_assignments: dict[str, list[str]] | None = None,
                          disable_call_timeout: bool = False) -> None:
    if not heldout:
        raise ValueError("Held-out examples must be nonempty")
    proof_ids = [proof.example_id for proof in heldout]
    selectors = [selector_for(proof) for proof in heldout]
    if len(set(proof_ids)) != len(proof_ids) or len(set(selectors)) != len(selectors):
        raise ValueError("Held-out example IDs and selectors must be unique")
    if attempts_per_arm < 1 or workers < 1 or reviews_per_valid_candidate < 1:
        raise ValueError("Attempt, worker, and review counts must be positive")
    if provider not in {"codex", "claude-code"}:
        raise ValueError("Provider must be 'codex' or 'claude-code'")
    if required_missed_reviews is None:
        required_missed_reviews = reviews_per_valid_candidate
    if not 1 <= required_missed_reviews <= reviews_per_valid_candidate:
        raise ValueError("Required missed reviews must be between one and the review count")
    if not 0 < alpha < 1:
        raise ValueError("alpha must be between zero and one")
    strategy = _validate_strategy(strategy_path.resolve().read_text())
    assignments = strategy_assignments or {}
    expected_selectors = set(selectors)
    if assignments:
        if set(assignments) != expected_selectors:
            raise ValueError("Strategy assignments must cover exactly the held-out selectors")
        if any(len(values) != attempts_per_arm or not all(
                isinstance(value, str) and value.strip() for value in values)
                for values in assignments.values()):
            raise ValueError("Each proof needs one nonempty assignment per strategy candidate")
    root = storage_dir.resolve()
    jobs = [dict(proof=proof, arm=arm, candidate=candidate)
            for proof in heldout for arm in ("generic", "strategies")
            for candidate in range(1, attempts_per_arm + 1)]
    random.Random(seed).shuffle(jobs)
    manifest = {
        "created_at": datetime.now(timezone.utc).isoformat(),
        "design": "frozen strategy, paired fresh-proof evaluation",
        "provider": provider,
        "model": model,
        "reasoning_effort": reasoning_effort,
        "requested_reasoning_effort": reasoning_effort,
        "provider_supports_reasoning_effort": True,
        "role_providers": {role: provider for role in (
            "mutator", "blind_judge", "validity_checker",
            "introduced_error_matcher", "novelty_classifier")},
        "seed": seed,
        "strategy_source": str(strategy_path.resolve()),
        "strategy_sha256": digest(strategy),
        "heldout": [example_metadata(proof) for proof in heldout],
        "attempts_per_proof_per_arm": attempts_per_arm,
        "fresh_session_per_candidate": True,
        "evaluation_feedback_between_candidates": False,
        "reviews_per_valid_candidate": reviews_per_valid_candidate,
        "call_timeout_seconds": (
            None if disable_call_timeout else SAFEGUARDED_CALL_TIMEOUT_SECONDS
        ),
        "required_missed_reviews": required_missed_reviews,
        "primary_endpoint": (
            "proof has >=1 valid candidate missed by >="
            f"{required_missed_reviews} of {reviews_per_valid_candidate} reviews"
        ),
        "independent_unit": "proof",
        "primary_test": "exact one-sided paired McNemar/binomial test",
        "alpha": alpha,
        "familywise_plan": "at most five strategy versions at alpha=0.01 each",
        "strategy_assignments": assignments,
        "jobs": [{"proof_id": job["proof"].example_id, "arm": job["arm"],
                  "candidate": job["candidate"]} for job in jobs],
    }
    if root.exists():
        if dry_run:
            raise FileExistsError(root)
        recorded = json.loads((root / "manifest.json").read_text())
        comparable = lambda value: {k: v for k, v in value.items()
                                    if k not in ("created_at", "protocol_amendments")}
        if comparable(recorded) != comparable(manifest):
            raise ValueError("Existing preregistration does not match requested evaluation")
        if digest((root / "strategies.md").read_text()) != digest(strategy):
            raise ValueError("Frozen strategy artifact changed after preregistration")
        state = json.loads((root / "status.json").read_text())
        if state.get("complete"):
            return
    else:
        root.mkdir(parents=True)
        (root / "strategies.md").write_text(strategy)
        save(root / "manifest.json", manifest)
        for proof in heldout:
            target = root / "sources" / proof_key(proof)
            target.mkdir(parents=True)
            (target / "proof.md").write_text(proof.proof)
            (target / "problem.txt").write_text(proof.problem)
        state = {"phase": "planned", "complete": False, "sessions_completed": []}
        save(root / "status.json", state)
    if dry_run:
        return
    results_path = root / "results.json"
    loaded_rows = json.loads(results_path.read_text()) if results_path.exists() else []
    # Older interrupted runs may contain a row for a technical non-submission. The
    # immutable session log remains on disk, but it is not an experimental outcome.
    rows = [row for row in loaded_rows if row.get("pipeline_status") == "judged"
            and row.get("valid") is not None]
    completed_indices = {row["session_index"] for row in rows}

    def execute(index, job):
        errors = []
        retry = 0
        fresh_attempts = 0
        while fresh_attempts < 5:
            suffix = "" if retry == 0 else f"_retry{retry}"
            retry += 1
            session = root / "sessions" / f"{index:04d}{suffix}"
            if session.exists():
                continue
            fresh_attempts += 1
            try:
                record = run_session(session, job["proof"], 1, model, reasoning_effort,
                    strategy if job["arm"] == "strategies" else None,
                    reviews_per_valid_candidate,
                    provider=provider,
                    disable_call_timeout=disable_call_timeout,
                    extra_guidance=("\nAssigned strategy for this candidate:\n"
                        + assignments[selector_for(job["proof"])][job["candidate"] - 1]
                        + "\nImplement this assigned mechanism when mathematically applicable. "
                          "Do not substitute an unrelated generic arithmetic or typographical error.\n"
                        if job["arm"] == "strategies" and assignments else ""))[0]
                assessment = record.get("assessment", {})
                if (record.get("status") != "judged" or assessment.get("valid") is None
                        or (assessment.get("valid") is True
                            and len(assessment.get("reviews", ()))
                            != reviews_per_valid_candidate)):
                    raise RuntimeError(f"Technical non-submission: {record.get('error', record)}")
                return record
            except Exception as error:
                errors.append(repr(error))
        raise RuntimeError(f"Job {index} failed all available fresh retries: {errors}")

    try:
        state.pop("error", None)
        state["phase"] = "evaluation"
        save(root / "status.json", state)
        with ThreadPoolExecutor(max_workers=min(workers, len(jobs))) as pool:
            futures = {}
            for index, job in enumerate(jobs, 1):
                if index in completed_indices:
                    continue
                future = pool.submit(execute, index, job)
                futures[future] = (index, job)
            for future in as_completed(futures):
                index, job = futures[future]
                record = future.result()
                row = dict(record.get("assessment", {}), arm=job["arm"],
                           proof_id=job["proof"].example_id, candidate=job["candidate"],
                           session_index=index,
                           strategy_assignment=(
                               assignments[selector_for(job["proof"])][job["candidate"] - 1]
                               if job["arm"] == "strategies" and assignments else None),
                           pipeline_status=record.get("status"),
                           elapsed_seconds=record.get("elapsed_seconds", 0))
                rows.append(row)
                rows.sort(key=lambda value: value["session_index"])
                save(root / "results.json", rows)
                save(root / "summary.json", summarize_frozen(
                    rows, heldout, attempts_per_arm, alpha, required_missed_reviews,
                    reviews_per_valid_candidate))
                state["sessions_completed"].append(index)
                save(root / "status.json", state)
        state.update(phase="complete", complete=True)
    except Exception as error:
        state.update(phase="failed", error=repr(error))
        raise
    finally:
        save(root / "status.json", state)
