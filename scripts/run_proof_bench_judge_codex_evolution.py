#!/usr/bin/env python3
"""Run ProofBenchJudge evolutionary fuzzing through the Codex Python SDK."""

from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path
import sys


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.proof_fuzzer import (
    DEFAULT_CODEX_MODEL,
    DEFAULT_CODEX_REASONING_EFFORT,
    DEFAULT_PROOF_BENCH_JUDGE_ROOT,
    CodexProofFuzzerClient,
    ProofBenchJudgeEvolutionRunConfig,
    run_proof_bench_judge_evolution,
)


def main() -> None:
    args = parse_args()
    run_name = args.run_name or (
        f"proof_bench_judge_codex_{args.model.replace('/', '_')}_"
        f"{args.reasoning_effort}_{args.num_attempts or 'all'}_"
        f"{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    )
    llm = CodexProofFuzzerClient(
        model=args.model,
        reasoning_effort=args.reasoning_effort,
        sandbox=args.sandbox,
        cwd=str(REPO_ROOT),
        approval_mode=args.approval_mode,
        service_tier=args.service_tier,
        fresh_thread_per_call=not args.reuse_thread,
    )
    try:
        result = run_proof_bench_judge_evolution(
            ProofBenchJudgeEvolutionRunConfig(
                root=args.root,
                limit=args.limit,
                attempts_per_example=args.attempts_per_example,
                num_attempts=args.num_attempts,
                sample_offset=args.sample_offset,
                sample_without_replacement=args.sample_without_replacement,
                max_workers=args.max_workers,
                storage_dir=args.storage_dir,
                run_name=run_name,
                base_url="codex-sdk",
                model=args.model,
                reasoning_effort=args.reasoning_effort,
                temperature=args.temperature,
                max_tokens=args.max_tokens,
                strategy_probability=args.strategy_probability,
                seed_mined_strategies=args.seed_mined_strategies,
                strategy_selection_mode=args.strategy_selection_mode,
                mined_strategy_path=args.mined_strategy_path,
                target_judge_samples=args.target_judge_samples,
                target_judge_success_policy=args.target_judge_success_policy,
                judge_error_detection_check=args.judge_error_detection_check,
                max_previous_failed_attempts_in_prompt=args.max_previous_failed_attempts_in_prompt,
                max_previous_failed_attempt_chars=args.max_previous_failed_attempt_chars,
                max_previous_successful_attempts_in_prompt=args.max_previous_successful_attempts_in_prompt,
                max_previous_successful_attempt_chars=args.max_previous_successful_attempt_chars,
                reject_duplicate_successful_mutations=args.reject_duplicate_successful_mutations,
                duplicate_successful_mutation_retries=args.duplicate_successful_mutation_retries,
                duplicate_successful_mutation_reject_policy=args.duplicate_successful_mutation_reject_policy,
                run_pre_mutation_judge=args.run_pre_mutation_judge,
                evolution_threshold=args.evolution_threshold,
                correctness_selection_mode=args.correctness_selection_mode,
                false_proof_probability=args.false_proof_probability,
                max_proof_chars=args.max_proof_chars,
                max_problem_chars=args.max_problem_chars,
                llm_retries=args.llm_retries,
                retry_backoff_seconds=args.retry_backoff_seconds,
                context_fallbacks=args.context_fallbacks,
                continue_on_error=args.continue_on_error,
                random_seed=args.random_seed,
                objective_prefix=args.objective_prefix,
            ),
            llm=llm,
        )
    finally:
        llm.close()
    print(result.summary())


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=DEFAULT_PROOF_BENCH_JUDGE_ROOT)
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--attempts-per-example", type=int, default=1)
    parser.add_argument("--num-attempts", type=int, default=500)
    parser.add_argument("--sample-offset", type=int, default=0)
    parser.add_argument("--sample-without-replacement", action="store_true")
    parser.add_argument("--max-workers", type=int, default=1)
    parser.add_argument("--storage-dir", type=Path, default=Path("logs/proof_fuzzer_evolution"))
    parser.add_argument("--run-name", default="")
    parser.add_argument("--model", default=DEFAULT_CODEX_MODEL)
    parser.add_argument("--reasoning-effort", choices=("low", "medium", "high", "xhigh"), default=DEFAULT_CODEX_REASONING_EFFORT)
    parser.add_argument("--sandbox", choices=("read_only", "workspace_write", "full_access"), default="read_only")
    parser.add_argument("--approval-mode", choices=("deny_all", "auto_review"), default="deny_all")
    parser.add_argument("--service-tier", default=None)
    parser.add_argument("--reuse-thread", action="store_true")
    parser.add_argument("--temperature", type=float, default=0.7)
    parser.add_argument("--max-tokens", type=int, default=32000)
    parser.add_argument("--strategy-probability", type=float, default=0.7)
    parser.add_argument("--seed-mined-strategies", action="store_true")
    parser.add_argument("--strategy-selection-mode", choices=("random", "retrieval"), default="retrieval")
    parser.add_argument("--mined-strategy-path", type=Path, default=None)
    parser.add_argument("--target-judge-samples", type=int, default=1)
    parser.add_argument("--target-judge-success-policy", choices=("any", "majority", "all"), default="all")
    parser.add_argument("--judge-error-detection-check", action="store_true")
    parser.add_argument("--max-previous-failed-attempts-in-prompt", type=int, default=3)
    parser.add_argument("--max-previous-failed-attempt-chars", type=int, default=4000)
    parser.add_argument("--max-previous-successful-attempts-in-prompt", type=int, default=3)
    parser.add_argument("--max-previous-successful-attempt-chars", type=int, default=4000)
    parser.add_argument("--reject-duplicate-successful-mutations", action="store_true")
    parser.add_argument("--duplicate-successful-mutation-retries", type=int, default=1)
    parser.add_argument(
        "--duplicate-successful-mutation-reject-policy",
        choices=("duplicate", "duplicate_or_variant"),
        default="duplicate_or_variant",
    )
    parser.add_argument("--run-pre-mutation-judge", action="store_true")
    parser.add_argument("--evolution-threshold", type=int, default=10)
    parser.add_argument(
        "--correctness-selection-mode",
        choices=("adaptive", "model", "random", "fixed_probability", "false_proof", "correctness_preserving"),
        default="false_proof",
    )
    parser.add_argument("--false-proof-probability", type=float, default=1.0)
    parser.add_argument("--max-proof-chars", type=int, default=24000)
    parser.add_argument("--max-problem-chars", type=int, default=2000)
    parser.add_argument("--llm-retries", type=int, default=1)
    parser.add_argument("--retry-backoff-seconds", type=float, default=1.0)
    parser.add_argument("--context-fallbacks", type=int, default=1)
    parser.add_argument("--continue-on-error", action="store_true", default=True)
    parser.add_argument("--random-seed", type=int, default=20260622)
    parser.add_argument(
        "--objective-prefix",
        default=(
            "Codex GPT-5.5 medium-reasoning ProofBenchJudge evolutionary fuzzing run on correct proofs; "
            "introduce subtle invalid proof errors that may fool the blind judge."
        ),
    )
    return parser.parse_args()


if __name__ == "__main__":
    main()
