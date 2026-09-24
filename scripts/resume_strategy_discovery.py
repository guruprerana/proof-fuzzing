#!/usr/bin/env python3
"""Resume quota-interrupted Claude discovery, then distill it."""

from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
import difflib
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.proof_fuzzer.agent_cli_client import ClaudePersistentSession
from src.proof_fuzzer.codex_client import _read_file_mutation
from src.proof_fuzzer.datasets.json_split import load_json_split
from src.proof_fuzzer.judging import BlindErrorFinder, parse_judge_result, usage_limit_reached
from src.proof_fuzzer.openai_ten_advances import load_openai_ten_advances_split
from src.proof_fuzzer.persistent_fuzzing import run_attempts, write_summary
from src.proof_fuzzer.strategy_transfer import (
    MechanismAssessor,
    NOVELTY_GUIDANCE,
    client,
    digest,
    distill,
    example_metadata,
    proof_key,
    save,
)


def load_records(session_root: Path) -> list[dict[str, object]]:
    path = session_root / "attempts.jsonl"
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def usable_attempt(session_root: Path, record: dict[str, object]) -> bool:
    """An attempt has a mutation, a blind report, and a completed assessment."""
    archive = session_root / "attempts" / f"{int(record['attempt']):03d}"
    if not all((archive / name).is_file() for name in (
        "mutated_proof.md", "introduced_error.md", "judge_response.txt",
    )):
        return False
    assessment = record.get("assessment")
    if not isinstance(assessment, dict) or assessment.get("assessment_error"):
        return False
    if assessment.get("valid") is False:
        return True
    return (
        assessment.get("valid") is True
        and bool(assessment.get("mechanism_id"))
        and assessment.get("detection") in {"caught", "missed"}
    )


def restore_assessor(session_root: Path, assessor: MechanismAssessor) -> None:
    bank_path = session_root / "assessments" / "mechanisms.json"
    if bank_path.exists():
        assessor.bank = json.loads(bank_path.read_text())
    for result_path in sorted((session_root / "assessments").glob("*/result.json")):
        result = json.loads(result_path.read_text())
        mechanism_id = result.get("mechanism_id")
        mutation_hash = result.get("mutation_sha256")
        if mechanism_id and mutation_hash:
            assessor.hashes[mutation_hash] = mechanism_id


def persist_reassessment(
    session_root: Path,
    records: list[dict[str, object]],
    record: dict[str, object],
    assessment: dict[str, object],
) -> None:
    record["assessment"] = assessment
    record.pop("assessment_error", None)
    record["verified_success"] = (
        assessment.get("valid") is True and assessment.get("detection") == "missed"
    )
    archive = session_root / "attempts" / f"{int(record['attempt']):03d}"
    result_path = archive / "result.json"
    result_path.write_text(json.dumps(record, indent=2, ensure_ascii=False) + "\n")
    feedback_path = archive / "feedback.json"
    feedback = json.loads(feedback_path.read_text()) if feedback_path.exists() else {}
    feedback["assessment"] = assessment
    feedback["interpretation"] = (
        "Use the independent validity, detection and novelty assessments below; "
        "these are automated checks, not mathematical ground truth."
    )
    feedback_path.write_text(json.dumps(feedback, indent=2, ensure_ascii=False) + "\n")
    workspace_feedback = session_root / "mutator_workspace" / "feedback" / f"{int(record['attempt']):03d}.json"
    workspace_feedback.write_text(json.dumps(feedback, indent=2, ensure_ascii=False) + "\n")
    (session_root / "attempts.jsonl").write_text(
        "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in records)
    )


def recover_interrupted_attempt(
    session_root: Path,
    proof,
    records: list[dict[str, object]],
    judge,
    assessor: MechanismAssessor,
    thread_id: str,
) -> bool:
    """Finish an artifact left between creation and the JSONL checkpoint."""
    index = len(records) + 1
    archive = session_root / "attempts" / f"{index:03d}"
    candidate = session_root / "mutator_workspace" / "attempts" / f"{index:03d}"
    if not archive.is_dir() and not candidate.is_dir():
        return False
    if not candidate.is_dir():
        raise RuntimeError(f"Interrupted attempt {index} has no mutation workspace")
    _read_file_mutation(candidate, proof.proof)
    mutated = (candidate / "mutated_proof.md").read_text()
    explanation = (candidate / "introduced_error.md").read_text()
    archive.mkdir(parents=True, exist_ok=True)
    (archive / "original_proof.md").write_text(proof.proof)
    (archive / "problem.txt").write_text(proof.problem)
    (archive / "mutated_proof.md").write_text(mutated)
    (archive / "introduced_error.md").write_text(explanation)
    (archive / "mutation.diff").write_text("".join(difflib.unified_diff(
        proof.proof.splitlines(keepends=True), mutated.splitlines(keepends=True),
        fromfile="original_proof.md", tofile="mutated_proof.md",
    )))
    if not (archive / "judge_response.txt").exists():
        prompt = BlindErrorFinder(judge).prompt(problem=proof.problem, proof=mutated)
        (archive / "judge_prompt.txt").write_text(prompt)
        response = judge.complete(prompt)
        (archive / "judge_response.txt").write_text(response)
    report = parse_judge_result((archive / "judge_response.txt").read_text())
    if report.response_kind != "error_inventory":
        raise ValueError(f"Interrupted attempt {index} judge response is not an error inventory")
    assessment = assessor(proof, archive)
    if usage_limit_reached(assessment.get("assessment_error", "")):
        raise RuntimeError(assessment["assessment_error"])
    record: dict[str, object] = {
        "attempt": index,
        "started_at": datetime.now(timezone.utc).isoformat(),
        "mutator_thread_id": thread_id,
        "verified_success": (
            assessment.get("valid") is True and assessment.get("detection") == "missed"
        ),
        "proof_id": proof.example_id,
        "status": "judged",
        "reported_errors": len(report.detected_errors),
        "assessment": assessment,
        "elapsed_seconds": 0,
        "recovered_after_process_interruption": True,
    }
    records.append(record)
    feedback = {
        "attempt": index,
        "judge_report": (archive / "judge_response.txt").read_text(),
        "assessment": assessment,
        "interpretation": (
            "Recovered after a process interruption. Use the independent validity, "
            "detection and novelty assessment below."
        ),
    }
    (archive / "feedback.json").write_text(json.dumps(feedback, indent=2, ensure_ascii=False) + "\n")
    workspace_feedback = session_root / "mutator_workspace/feedback" / f"{index:03d}.json"
    workspace_feedback.write_text(json.dumps(feedback, indent=2, ensure_ascii=False) + "\n")
    (archive / "result.json").write_text(json.dumps(record, indent=2, ensure_ascii=False) + "\n")
    with (session_root / "attempts.jsonl").open("a") as stream:
        stream.write(json.dumps(record, ensure_ascii=False) + "\n")
    return True


def resume_session(
    session_root: Path,
    proof,
    *,
    target: int,
    provider: str,
    model: str,
    effort: str,
) -> list[dict[str, object]]:
    records = load_records(session_root)
    thread_data = json.loads((session_root / "thread.json").read_text())
    mutator = client(session_root / "mutator", model, effort, provider=provider, safeguards=False)
    judge = client(session_root / "judge", model, effort, provider=provider)
    auditor = client(session_root / "assessments", model, effort, provider=provider)
    assessor = MechanismAssessor(session_root / "assessments", auditor, 1, None)
    restore_assessor(session_root, assessor)
    thread = ClaudePersistentSession(
        thread_data["thread_id"],
        (session_root / "mutator_workspace").resolve(),
        started=True,
    )
    recovery = session_root / "mutator_workspace" / "recovery_context.md"
    recovery.write_text(
        "This session is resuming after provider quota exhaustion. Attempts already containing "
        "complete feedback remain authoritative. Quota-failed attempt directories are technical "
        "artifacts, not submitted mutations. Continue seeking new mechanisms.\n"
    )
    try:
        # A process can be killed after creating the next attempt but before
        # appending its record. Preserve and finish that mutation in place.
        recover_interrupted_attempt(
            session_root, proof, records, judge, assessor, thread.id,
        )
        # Finish assessments for already-generated mutations before requesting more.
        for record in records:
            if usable_attempt(session_root, record):
                continue
            archive = session_root / "attempts" / f"{int(record['attempt']):03d}"
            if not all((archive / name).is_file() for name in (
                "mutated_proof.md", "introduced_error.md", "mutation.diff", "judge_response.txt",
            )):
                continue
            assessment = assessor(proof, archive)
            persist_reassessment(session_root, records, record, assessment)
            if usage_limit_reached(assessment.get("assessment_error", "")):
                raise RuntimeError(assessment["assessment_error"])

        while sum(usable_attempt(session_root, row) for row in records) < target:
            next_total = len(records) + 1
            records = run_attempts(
                root=session_root,
                proof=proof,
                total=next_total,
                mutator=mutator,
                thread=thread,
                sdk=None,
                judge=judge,
                initial_records=records,
                recovery_context=True,
                assessor=assessor,
                extra_guidance=NOVELTY_GUIDANCE,
            )
            latest = records[-1]
            if usage_limit_reached(latest.get("error", "")) or usage_limit_reached(
                latest.get("assessment_error", "")
            ):
                raise RuntimeError(latest.get("error") or latest.get("assessment_error"))
        write_summary(session_root, records, len(records))
        return records
    finally:
        mutator.close()
        judge.close()
        auditor.close()


def validate_manifest(manifest: dict[str, object], discovery) -> None:
    if manifest.get("run_mode") != "discovery_and_distillation_only":
        raise ValueError("Only discovery-and-distillation runs can be resumed")
    expected = {row["example_id"]: row for row in manifest["discovery"]}
    actual = {proof.example_id: example_metadata(proof) for proof in discovery}
    if set(expected) != set(actual):
        raise ValueError("Discovery IDs differ from the frozen run manifest")
    for example_id in expected:
        for field in ("proof_sha256", "problem_sha256"):
            if field in expected[example_id] and expected[example_id][field] != actual[example_id].get(field):
                raise ValueError(f"Frozen {field} differs for {example_id}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", required=True, type=Path)
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--split-json", type=Path)
    source.add_argument("--tcs-root", type=Path)
    parser.add_argument("--target-usable-attempts", type=int, default=25)
    parser.add_argument("--workers", type=int, default=10)
    args = parser.parse_args()
    if args.target_usable_attempts < 1 or args.workers < 1:
        parser.error("--target-usable-attempts and --workers must be positive")

    root = args.run_dir.resolve()
    manifest = json.loads((root / "manifest.json").read_text())
    if args.tcs_root:
        discovery, _ = load_openai_ten_advances_split(args.tcs_root.resolve())
    else:
        discovery, _ = load_json_split(args.split_json.resolve(), allow_empty_heldout=True)
    validate_manifest(manifest, discovery)
    provider = manifest["provider"]
    model = manifest["model"]
    effort = manifest["requested_reasoning_effort"]
    if provider != "claude-code":
        raise ValueError("This resume command requires the Claude Code provider")

    state = json.loads((root / "status.json").read_text())
    state.update(
        phase="discovery_resume",
        complete=False,
        resumed_at=datetime.now(timezone.utc).isoformat(),
    )
    state.pop("error", None)
    state.pop("failed_phase", None)
    save(root / "status.json", state)
    try:
        completed: dict[str, list[dict[str, object]]] = {}
        with ThreadPoolExecutor(max_workers=min(args.workers, len(discovery))) as pool:
            futures = {
                pool.submit(
                    resume_session,
                    root / "discovery" / proof_key(proof),
                    proof,
                    target=args.target_usable_attempts,
                    provider=provider,
                    model=model,
                    effort=effort,
                ): proof
                for proof in discovery
            }
            for future in as_completed(futures):
                proof = futures[future]
                completed[proof_key(proof)] = future.result()

        evidence: dict[str, list[dict[str, object]]] = {}
        for proof in discovery:
            key = proof_key(proof)
            session_root = root / "discovery" / key
            usable = [row for row in completed[key] if usable_attempt(session_root, row)]
            if len(usable) < args.target_usable_attempts:
                raise RuntimeError(f"Only {len(usable)}/{args.target_usable_attempts} usable attempts for {key}")
            evidence[key] = [row["assessment"] for row in usable[:args.target_usable_attempts]]
            bank = json.loads((session_root / "assessments/mechanisms.json").read_text())
            evidence[key].append({
                "mechanism_bank": bank,
                "instruction": "Weight each mechanism once, not by repeated wins; merge cross-proof equivalents.",
            })

        state["phase"] = "distillation"
        save(root / "status.json", state)
        strategy = distill(
            root / "distillation", discovery, evidence, model, effort,
            provider=provider,
        )
        state.update(phase="distilled", complete=True, strategy_sha256=digest(strategy))
    except Exception as error:
        state.update(phase="failed", failed_phase=state["phase"], error=repr(error))
        raise
    finally:
        save(root / "status.json", state)


if __name__ == "__main__":
    main()
