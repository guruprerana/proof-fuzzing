#!/usr/bin/env python3
"""Train and evaluate an evolving mutation prompt on MedPRMBench traces."""

from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path
import sys


REPO_ROOT = Path(__file__).resolve().parents[3]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.archive.proof_fuzzer import (
    CodexProofFuzzerClient,
    DEFAULT_MEDPRMBENCH_ROOT,
    MEDPRM_ERROR_TYPE_BY_CODE,
    MedPRMBenchPromptExperimentConfig,
    load_medprmbench_traces,
    run_medprmbench_prompt_evolution_experiment,
)


def main() -> None:
    args = _parse_args()
    source_path = args.dataset_file or args.dataset_root
    traces = load_medprmbench_traces(source_path)
    run_name = args.run_name or _default_run_name(args)
    storage_dir = args.storage_dir / run_name
    codex_workspace = storage_dir / "codex_workspace"
    codex_workspace.mkdir(parents=True, exist_ok=True)
    print(
        f"Loaded {len(traces)} variants from "
        f"{len({trace.case_id for trace in traces})} clinical cases; "
        f"error types={sorted({code for trace in traces for code in trace.error_types})}",
        flush=True,
    )
    print(f"Experiment storage: {storage_dir}", flush=True)
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
            "This is a file-backed medical reasoning benchmark call. Read prompt.txt and "
            "only the input files it names in the current call workspace. Do not inspect "
            "any other filesystem location. Return the requested JSON. Do not present "
            "benchmark text as medical advice."
        ),
    )
    config = MedPRMBenchPromptExperimentConfig(
        storage_dir=storage_dir,
        dataset_root=args.dataset_root,
        dataset_file=str(args.dataset_file) if args.dataset_file else "",
        model=args.model,
        reasoning_effort=args.reasoning_effort,
        error_types=tuple(args.error_types),
        train_case_fraction=args.train_case_fraction,
        train_examples=args.train_examples,
        test_examples=args.test_examples,
        test_attempts_per_example=args.test_attempts_per_example,
        training_generations=args.training_generations,
        split_seed=args.split_seed,
        evaluation_seed=args.evaluation_seed,
        max_workers=args.max_workers,
        max_trace_chars=args.max_trace_chars,
        max_question_chars=args.max_question_chars,
        max_prompt_chars=args.max_prompt_chars,
        max_prompt_growth_chars=args.max_prompt_growth_chars,
        max_prompt_length_multiplier=args.max_prompt_length_multiplier,
        llm_retries=args.llm_retries,
        evolution_retries=args.evolution_retries,
    )
    try:
        result = run_medprmbench_prompt_evolution_experiment(
            llm=llm,
            config=config,
            traces=traces,
            progress=lambda message: print(message, flush=True),
        )
    finally:
        llm.close()
    print(result.summary(), flush=True)


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset-root", type=Path, default=DEFAULT_MEDPRMBENCH_ROOT)
    parser.add_argument("--dataset-file", type=Path)
    parser.add_argument(
        "--storage-dir", type=Path, default=Path("logs/medprmbench_prompt_evolution")
    )
    parser.add_argument("--run-name", default="")
    parser.add_argument("--model", default="gpt-5.6-sol")
    parser.add_argument(
        "--reasoning-effort", choices=("low", "medium", "high", "xhigh"), default="medium"
    )
    parser.add_argument(
        "--error-types",
        nargs="+",
        choices=tuple(MEDPRM_ERROR_TYPE_BY_CODE),
        default=tuple(MEDPRM_ERROR_TYPE_BY_CODE),
    )
    parser.add_argument("--sandbox", choices=("read_only",), default="read_only")
    parser.add_argument("--approval-mode", choices=("deny_all",), default="deny_all")
    parser.add_argument("--service-tier", default=None)
    parser.add_argument("--persist-codex-threads", action="store_true")
    parser.add_argument("--train-case-fraction", type=float, default=0.5)
    parser.add_argument("--train-examples", type=int, default=5)
    parser.add_argument("--test-examples", type=int, default=5)
    parser.add_argument("--test-attempts-per-example", type=int, default=1)
    parser.add_argument("--training-generations", type=int, default=3)
    parser.add_argument("--split-seed", type=int, default=20260903)
    parser.add_argument("--evaluation-seed", type=int, default=20260904)
    parser.add_argument("--max-workers", type=int, default=5)
    parser.add_argument("--max-trace-chars", type=int, default=24_000)
    parser.add_argument("--max-question-chars", type=int, default=8_000)
    parser.add_argument("--max-prompt-chars", type=int, default=6_000)
    parser.add_argument("--max-prompt-growth-chars", type=int, default=400)
    parser.add_argument("--max-prompt-length-multiplier", type=float, default=2.0)
    parser.add_argument("--llm-retries", type=int, default=1)
    parser.add_argument("--evolution-retries", type=int, default=3)
    return parser.parse_args()


def _default_run_name(args: argparse.Namespace) -> str:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    model = args.model.replace("/", "_")
    error_scope = "all" if len(args.error_types) == 14 else "-".join(args.error_types)
    return f"medprmbench_{error_scope}_{model}_{args.reasoning_effort}_{timestamp}"


if __name__ == "__main__":
    main()
