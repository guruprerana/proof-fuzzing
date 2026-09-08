#!/usr/bin/env python3
"""Train and evaluate one evolving mutation prompt on the REFLECT benchmark."""

from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path
import sys


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.proof_fuzzer import (
    CodexProofFuzzerClient,
    DEFAULT_REFLECT_ROOT,
    ReflectPromptExperimentConfig,
    load_reflect_examples,
    run_reflect_prompt_evolution_experiment,
)


def main() -> None:
    args = _parse_args()
    run_name = args.run_name or _default_run_name(args)
    storage_dir = args.storage_dir / run_name
    codex_workspace = storage_dir / "codex_workspace"
    codex_workspace.mkdir(parents=True, exist_ok=True)
    examples = load_reflect_examples(args.dataset_root)
    print(f"Experiment storage: {storage_dir}", flush=True)
    print(
        f"Loaded {len(examples)} rows across four REFLECT views; "
        f"unique traces={len({example.trace_id for example in examples})}",
        flush=True,
    )
    print(
        f"Model: {args.model}; effort: {args.reasoning_effort}; "
        f"datasets={','.join(args.datasets)}; "
        f"train={args.train_examples_per_dataset}/view x "
        f"{args.training_generations} generations; "
        f"test={args.test_examples_per_dataset}/view/arm",
        flush=True,
    )
    llm = CodexProofFuzzerClient(
        model=args.model,
        reasoning_effort=args.reasoning_effort,
        sandbox=args.sandbox,
        workspace_root=codex_workspace,
        approval_mode=args.approval_mode,
        service_tier=args.service_tier,
        fresh_thread_per_call=True,
        ephemeral_threads=not args.persist_codex_threads,
        developer_instructions=(
            "This is a file-backed benchmark call. Read prompt.txt and only the input "
            "files it names in the current call workspace. Do not inspect any other "
            "filesystem location. Return the requested JSON."
        ),
    )
    config = ReflectPromptExperimentConfig(
        storage_dir=storage_dir,
        dataset_root=args.dataset_root,
        model=args.model,
        reasoning_effort=args.reasoning_effort,
        datasets=tuple(args.datasets),
        train_trace_fraction=args.train_trace_fraction,
        train_examples_per_dataset=args.train_examples_per_dataset,
        test_examples_per_dataset=args.test_examples_per_dataset,
        test_attempts_per_example=args.test_attempts_per_example,
        training_generations=args.training_generations,
        split_seed=args.split_seed,
        evaluation_seed=args.evaluation_seed,
        max_workers=args.max_workers,
        max_unit_chars=args.max_unit_chars,
        max_candidate_chars=args.max_candidate_chars,
        max_context_chars=args.max_context_chars,
        max_query_chars=args.max_query_chars,
        max_prompt_chars=args.max_prompt_chars,
        max_prompt_growth_chars=args.max_prompt_growth_chars,
        max_prompt_length_multiplier=args.max_prompt_length_multiplier,
        max_attempt_summary_chars=args.max_attempt_summary_chars,
        max_evolution_context_chars=args.max_evolution_context_chars,
        llm_retries=args.llm_retries,
        evolution_retries=args.evolution_retries,
    )
    try:
        result = run_reflect_prompt_evolution_experiment(
            llm=llm,
            config=config,
            examples=examples,
            progress=lambda message: print(message, flush=True),
        )
    finally:
        llm.close()
    print(result.summary(), flush=True)


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset-root", type=Path, default=DEFAULT_REFLECT_ROOT)
    parser.add_argument(
        "--storage-dir", type=Path, default=Path("logs/reflect_prompt_evolution")
    )
    parser.add_argument("--run-name", default="")
    parser.add_argument("--model", default="gpt-5.6-sol")
    parser.add_argument(
        "--datasets",
        nargs="+",
        choices=("reasoning", "tool_use", "chunk", "holistic"),
        default=("reasoning", "tool_use", "chunk", "holistic"),
        help="Benchmark views to optimize together; use one value for an independent run.",
    )
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
    parser.add_argument("--train-trace-fraction", type=float, default=0.5)
    parser.add_argument("--train-examples-per-dataset", type=int, default=5)
    parser.add_argument("--test-examples-per-dataset", type=int, default=5)
    parser.add_argument("--test-attempts-per-example", type=int, default=1)
    parser.add_argument("--training-generations", type=int, default=3)
    parser.add_argument("--split-seed", type=int, default=20260903)
    parser.add_argument("--evaluation-seed", type=int, default=20260904)
    parser.add_argument("--max-workers", type=int, default=5)
    parser.add_argument("--max-unit-chars", type=int, default=24_000)
    parser.add_argument("--max-candidate-chars", type=int, default=60_000)
    parser.add_argument("--max-context-chars", type=int, default=20_000)
    parser.add_argument("--max-query-chars", type=int, default=6_000)
    parser.add_argument("--max-prompt-chars", type=int, default=6_000)
    parser.add_argument("--max-prompt-growth-chars", type=int, default=400)
    parser.add_argument("--max-prompt-length-multiplier", type=float, default=2.0)
    parser.add_argument("--max-attempt-summary-chars", type=int, default=1_600)
    parser.add_argument("--max-evolution-context-chars", type=int, default=48_000)
    parser.add_argument("--llm-retries", type=int, default=1)
    parser.add_argument("--evolution-retries", type=int, default=3)
    return parser.parse_args()


def _default_run_name(args: argparse.Namespace) -> str:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    model = args.model.replace("/", "_")
    datasets = "-".join(args.datasets)
    return (
        f"reflect_{datasets}_prompt_evolution_{model}_"
        f"{args.reasoning_effort}_{timestamp}"
    )


if __name__ == "__main__":
    main()
