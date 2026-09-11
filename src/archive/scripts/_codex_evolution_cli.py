"""Shared command-line plumbing for Codex evolutionary-fuzzing runners."""

from __future__ import annotations

import argparse
from collections.abc import Callable
from dataclasses import dataclass, fields
from datetime import datetime
from pathlib import Path
from typing import Protocol

from src.archive.proof_fuzzer import (
    DEFAULT_CODEX_MODEL,
    DEFAULT_CODEX_REASONING_EFFORT,
    CodexProofFuzzerClient,
    ProofBenchJudgeEvolutionRunConfig,
)
from src.proof_fuzzer.proof_bench_judge import (
    resolve_proof_bench_judge_evolution_storage_dir,
)


class EvolutionRunResult(Protocol):
    def summary(self) -> str: ...


@dataclass(frozen=True)
class CodexEvolutionDefaults:
    root: Path
    run_name_prefix: str
    num_attempts: int | None
    max_workers: int
    max_tokens: int
    strategy_probability: float
    strategy_selection_mode: str
    run_pre_mutation_judge: bool
    evolution_threshold: int
    correctness_selection_mode: str
    false_proof_probability: float
    max_proof_chars: int
    max_problem_chars: int
    continue_on_error: bool
    objective_prefix: str
    seed_mined_strategies: bool = False
    run_name_suffix: str = ""


def run_codex_evolution_cli(
    *,
    description: str,
    defaults: CodexEvolutionDefaults,
    config_type: type[ProofBenchJudgeEvolutionRunConfig],
    run_evolution: Callable[..., EvolutionRunResult],
) -> None:
    args = _parse_args(description, defaults)
    run_name = args.run_name or _default_run_name(args, defaults)
    resolved_storage_dir = resolve_proof_bench_judge_evolution_storage_dir(
        args.storage_dir,
        run_name=run_name,
    )
    ephemeral_threads = not args.persist_codex_threads
    llm = CodexProofFuzzerClient(
        model=args.model,
        reasoning_effort=args.reasoning_effort,
        sandbox=args.sandbox,
        workspace_root=resolved_storage_dir / "codex_workspace",
        approval_mode=args.approval_mode,
        service_tier=args.service_tier,
        ephemeral_threads=ephemeral_threads,
        fresh_thread_per_call=True,
    )
    try:
        config_values = vars(args)
        config_kwargs = {
            field.name: config_values[field.name]
            for field in fields(config_type)
            if field.name in config_values
        }
        config_kwargs.update(
            run_name=run_name,
            base_url="codex-sdk",
        )
        result = run_evolution(
            config_type(**config_kwargs),
            llm=llm,
        )
    finally:
        llm.close()
    print(result.summary(), flush=True)


def _default_run_name(
    args: argparse.Namespace,
    defaults: CodexEvolutionDefaults,
) -> str:
    attempt_count = args.num_attempts if args.num_attempts is not None else "all"
    model = args.model.replace("/", "_")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return (
        f"{defaults.run_name_prefix}_{model}_{args.reasoning_effort}_"
        f"{attempt_count}{defaults.run_name_suffix}_{timestamp}"
    )


def _parse_args(
    description: str,
    defaults: CodexEvolutionDefaults,
) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("--root", type=Path, default=defaults.root)
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--attempts-per-example", type=int, default=1)
    parser.add_argument("--num-attempts", type=int, default=defaults.num_attempts)
    parser.add_argument("--sample-offset", type=int, default=0)
    parser.add_argument("--sample-without-replacement", action="store_true")
    parser.add_argument("--max-workers", type=int, default=defaults.max_workers)
    parser.add_argument(
        "--storage-dir",
        type=Path,
        default=Path("logs/proof_fuzzer_evolution"),
    )
    parser.add_argument("--run-name", default="")
    parser.add_argument("--model", default=DEFAULT_CODEX_MODEL)
    parser.add_argument(
        "--reasoning-effort",
        choices=("low", "medium", "high", "xhigh"),
        default=DEFAULT_CODEX_REASONING_EFFORT,
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
    parser.add_argument(
        "--persist-codex-threads",
        action="store_true",
        help="Save proof-fuzzer threads in Codex history; the default is ephemeral.",
    )
    parser.add_argument("--temperature", type=float, default=0.7)
    parser.add_argument("--max-tokens", type=int, default=defaults.max_tokens)
    parser.add_argument(
        "--strategy-probability",
        type=float,
        default=defaults.strategy_probability,
    )
    parser.add_argument(
        "--seed-mined-strategies",
        action=argparse.BooleanOptionalAction,
        default=defaults.seed_mined_strategies,
    )
    parser.add_argument(
        "--strategy-selection-mode",
        choices=("random", "retrieval"),
        default=defaults.strategy_selection_mode,
    )
    parser.add_argument("--mined-strategy-path", type=Path, default=None)
    parser.add_argument("--target-judge-samples", type=int, default=1)
    parser.add_argument(
        "--target-judge-success-policy",
        choices=("any", "majority", "all"),
        default="all",
    )
    parser.add_argument("--judge-error-detection-check", action="store_true")
    parser.add_argument("--max-previous-failed-attempts-in-prompt", type=int, default=3)
    parser.add_argument("--max-previous-failed-attempt-chars", type=int, default=4_000)
    parser.add_argument("--max-previous-successful-attempts-in-prompt", type=int, default=3)
    parser.add_argument("--max-previous-successful-attempt-chars", type=int, default=4_000)
    parser.add_argument("--reject-duplicate-successful-mutations", action="store_true")
    parser.add_argument("--duplicate-successful-mutation-retries", type=int, default=1)
    parser.add_argument(
        "--duplicate-successful-mutation-reject-policy",
        choices=("duplicate", "duplicate_or_variant"),
        default="duplicate_or_variant",
    )
    parser.add_argument(
        "--run-pre-mutation-judge",
        action=argparse.BooleanOptionalAction,
        default=defaults.run_pre_mutation_judge,
    )
    parser.add_argument("--evolution-threshold", type=int, default=defaults.evolution_threshold)
    parser.add_argument(
        "--correctness-selection-mode",
        choices=(
            "adaptive",
            "model",
            "random",
            "fixed_probability",
            "false_proof",
            "correctness_preserving",
        ),
        default=defaults.correctness_selection_mode,
    )
    parser.add_argument(
        "--false-proof-probability",
        type=float,
        default=defaults.false_proof_probability,
    )
    parser.add_argument("--max-proof-chars", type=int, default=defaults.max_proof_chars)
    parser.add_argument("--max-problem-chars", type=int, default=defaults.max_problem_chars)
    parser.add_argument("--llm-retries", type=int, default=1)
    parser.add_argument("--retry-backoff-seconds", type=float, default=1.0)
    parser.add_argument("--context-fallbacks", type=int, default=1)
    parser.add_argument(
        "--continue-on-error",
        action=argparse.BooleanOptionalAction,
        default=defaults.continue_on_error,
    )
    parser.add_argument("--random-seed", type=int, default=20260622)
    parser.add_argument("--objective-prefix", default=defaults.objective_prefix)
    return parser.parse_args()
