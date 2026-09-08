#!/usr/bin/env python3
"""Train and evaluate one evolving mutation prompt on OpenAI's ten proofs."""

from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path
import sys


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.proof_fuzzer import (
    DEFAULT_OPENAI_TEN_ADVANCES_ROOT,
    CodexProofFuzzerClient,
    EvolutionConfig,
    PromptEvolutionExperimentConfig,
    run_openai_ten_advances_prompt_evolution_experiment,
)


def main() -> None:
    args = _parse_args()
    run_name = args.run_name or _default_run_name(args)
    storage_dir = args.storage_dir / run_name
    llm = CodexProofFuzzerClient(
        model=args.model,
        reasoning_effort=args.reasoning_effort,
        sandbox=args.sandbox,
        workspace_root=storage_dir / "codex_workspace",
        approval_mode=args.approval_mode,
        service_tier=args.service_tier,
        fresh_thread_per_call=True,
        ephemeral_threads=not args.persist_codex_threads,
    )
    experiment_config = PromptEvolutionExperimentConfig(
        storage_dir=storage_dir,
        proof_root=args.root,
        model=args.model,
        reasoning_effort=args.reasoning_effort,
        codex_sandbox=args.sandbox,
        codex_service_tier=args.service_tier,
        train_problem_count=args.train_problem_count,
        training_generations=args.training_generations,
        training_attempts_per_problem_per_generation=(
            args.training_attempts_per_problem_per_generation
        ),
        test_attempts_per_problem=args.test_attempts_per_problem,
        split_seed=args.split_seed,
        evaluation_seed=args.evaluation_seed,
        max_workers=args.max_workers,
        max_prompt_chars=args.max_prompt_chars,
        max_prompt_growth_chars=args.max_prompt_growth_chars,
        max_prompt_length_multiplier=args.max_prompt_length_multiplier,
        max_attempt_summary_chars=args.max_attempt_summary_chars,
        max_evolution_context_chars=args.max_evolution_context_chars,
        evolution_retries=args.evolution_retries,
        objective_prefix=args.objective_prefix,
    )
    attempt_config = EvolutionConfig(
        storage_dir=storage_dir,
        run_pre_mutation_judge=False,
        run_original_error_control=True,
        max_proof_chars=args.max_proof_chars,
        max_problem_chars=args.max_problem_chars,
        llm_retries=args.llm_retries,
        retry_backoff_seconds=args.retry_backoff_seconds,
        context_fallbacks=args.context_fallbacks,
        continue_on_error=True,
        target_judge_samples=1,
        target_judge_success_policy="all",
        judge_error_detection_check=True,
        trace_llm_calls=not args.no_trace_llm_calls,
        random_seed=args.split_seed,
    )
    print(f"Experiment storage: {storage_dir}", flush=True)
    print(
        f"Model: {args.model}; effort: {args.reasoning_effort}; "
        f"train generations: {args.training_generations}; "
        f"test attempts/problem/arm: {args.test_attempts_per_problem}",
        flush=True,
    )
    try:
        result = run_openai_ten_advances_prompt_evolution_experiment(
            llm=llm,
            config=experiment_config,
            attempt_config=attempt_config,
            progress=lambda message: print(message, flush=True),
        )
    finally:
        llm.close()
    print(result.summary(), flush=True)


def _default_run_name(args: argparse.Namespace) -> str:
    model = args.model.replace("/", "_")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"ten_proofs_prompt_evolution_{model}_{args.reasoning_effort}_{timestamp}"


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=DEFAULT_OPENAI_TEN_ADVANCES_ROOT)
    parser.add_argument(
        "--storage-dir",
        type=Path,
        default=Path("logs/prompt_evolution_experiments"),
    )
    parser.add_argument("--run-name", default="")
    parser.add_argument("--model", default="gpt-5.6-sol")
    parser.add_argument(
        "--reasoning-effort",
        choices=("low", "medium", "high", "xhigh"),
        default="medium",
    )
    parser.add_argument(
        "--sandbox",
        choices=("read_only",),
        default="read_only",
        help="Dedicated Codex workspaces require the read-only sandbox.",
    )
    parser.add_argument(
        "--approval-mode",
        choices=("deny_all",),
        default="deny_all",
        help="Dedicated Codex workspaces deny all approval escalation.",
    )
    parser.add_argument("--service-tier", default=None)
    parser.add_argument("--persist-codex-threads", action="store_true")
    parser.add_argument("--train-problem-count", type=int, default=5)
    parser.add_argument("--training-generations", type=int, default=3)
    parser.add_argument(
        "--training-attempts-per-problem-per-generation",
        type=int,
        default=1,
    )
    parser.add_argument("--test-attempts-per-problem", type=int, default=3)
    parser.add_argument("--split-seed", type=int, default=20260902)
    parser.add_argument("--evaluation-seed", type=int, default=20260903)
    parser.add_argument("--max-workers", type=int, default=5)
    parser.add_argument("--max-proof-chars", type=int, default=300_000)
    parser.add_argument("--max-problem-chars", type=int, default=12_000)
    parser.add_argument("--max-prompt-chars", type=int, default=5_000)
    parser.add_argument("--max-prompt-growth-chars", type=int, default=400)
    parser.add_argument("--max-prompt-length-multiplier", type=float, default=2.0)
    parser.add_argument("--max-attempt-summary-chars", type=int, default=1_200)
    parser.add_argument("--max-evolution-context-chars", type=int, default=40_000)
    parser.add_argument("--evolution-retries", type=int, default=1)
    parser.add_argument("--llm-retries", type=int, default=1)
    parser.add_argument("--retry-backoff-seconds", type=float, default=1.0)
    parser.add_argument("--context-fallbacks", type=int, default=1)
    parser.add_argument("--no-trace-llm-calls", action="store_true")
    parser.add_argument(
        "--objective-prefix",
        default=(
            "Generate a subtle invalid mutation of a recently published theoretical "
            "computer-science proof."
        ),
    )
    return parser.parse_args()


if __name__ == "__main__":
    main()
