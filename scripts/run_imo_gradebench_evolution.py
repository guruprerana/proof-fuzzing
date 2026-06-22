#!/usr/bin/env python3
"""Run evolutionary proof fuzzing over correct IMO-GradeBench examples."""

from __future__ import annotations

import argparse
from datetime import datetime
import json
from pathlib import Path
import sys


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.proof_fuzzer import (
    DEFAULT_BASE_URL,
    DEFAULT_IMO_GRADEBENCH_ROOT,
    EvolutionConfig,
    GPT_OSS_120B,
    VLLMProofFuzzerClient,
    run_imo_gradebench_evolutionary_pipeline,
)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=DEFAULT_IMO_GRADEBENCH_ROOT)
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--attempts-per-example", type=int, default=1)
    parser.add_argument("--num-attempts", type=int, default=None)
    parser.add_argument("--sample-without-replacement", action="store_true")
    parser.add_argument("--max-workers", type=int, default=1)
    parser.add_argument("--storage-dir", type=Path, default=None)
    parser.add_argument("--run-name", default="")
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL)
    parser.add_argument("--model", default=GPT_OSS_120B)
    parser.add_argument("--reasoning-effort", choices=("low", "medium", "high"), default="high")
    parser.add_argument("--temperature", type=float, default=0.7)
    parser.add_argument("--max-tokens", type=int, default=100_000)
    parser.add_argument("--strategy-probability", type=float, default=0.5)
    parser.add_argument("--evolution-threshold", type=int, default=20)
    parser.add_argument(
        "--correctness-selection-mode",
        choices=("adaptive", "model", "random", "fixed_probability", "false_proof", "correctness_preserving"),
        default="adaptive",
    )
    parser.add_argument("--false-proof-probability", type=float, default=0.7)
    parser.add_argument("--max-proof-chars", type=int, default=24_000)
    parser.add_argument("--max-problem-chars", type=int, default=4_000)
    parser.add_argument("--llm-retries", type=int, default=3)
    parser.add_argument("--retry-backoff-seconds", type=float, default=1.0)
    parser.add_argument("--context-fallbacks", type=int, default=2)
    parser.add_argument("--continue-on-error", action="store_true")
    parser.add_argument("--random-seed", type=int, default=None)
    parser.add_argument("--objective-prefix", default="")
    args = parser.parse_args()
    storage_dir = _resolve_storage_dir(args.storage_dir, run_name=args.run_name)
    storage_dir.mkdir(parents=True, exist_ok=True)

    llm = VLLMProofFuzzerClient(
        base_url=args.base_url,
        model=args.model,
        reasoning_effort=args.reasoning_effort,
        temperature=args.temperature,
        max_tokens=args.max_tokens,
    )
    config = EvolutionConfig(
        storage_dir=storage_dir,
        strategy_injection_probability=args.strategy_probability,
        evolution_threshold=args.evolution_threshold,
        random_seed=args.random_seed,
        correctness_selection_mode=args.correctness_selection_mode,
        false_proof_probability=args.false_proof_probability,
        max_proof_chars=args.max_proof_chars,
        max_problem_chars=args.max_problem_chars,
        llm_retries=args.llm_retries,
        retry_backoff_seconds=args.retry_backoff_seconds,
        context_fallbacks=args.context_fallbacks,
        continue_on_error=args.continue_on_error,
    )
    _write_run_config(storage_dir, args)
    attempts = run_imo_gradebench_evolutionary_pipeline(
        llm=llm,
        root=args.root,
        limit=args.limit,
        config=config,
        objective_prefix=args.objective_prefix,
        max_workers=args.max_workers,
        attempts_per_example=args.attempts_per_example,
        num_attempts=args.num_attempts,
        sample_without_replacement=args.sample_without_replacement,
    )

    successes = sum(1 for attempt in attempts if attempt.success)
    failures = sum(1 for attempt in attempts if attempt.status == "failed")
    print(f"Ran {len(attempts)} attempts; successes={successes}; failures={failures}; storage={storage_dir}")


def _resolve_storage_dir(storage_dir: Path | None, *, run_name: str = "") -> Path:
    base = Path("logs/proof_fuzzer_evolution")
    name = run_name.strip() or f"imo_gradebench_oss120b_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    if storage_dir is None:
        return base / name
    if storage_dir == Path("logs") or storage_dir == base:
        return storage_dir / name
    if storage_dir.name in {"logs", "proof_fuzzer_evolution"}:
        return storage_dir / name
    return storage_dir


def _write_run_config(storage_dir: Path, args: argparse.Namespace) -> None:
    config = {
        key: str(value) if isinstance(value, Path) else value
        for key, value in vars(args).items()
    }
    config["resolved_storage_dir"] = str(storage_dir)
    (storage_dir / "run_config.json").write_text(
        json.dumps(config, indent=2, sort_keys=True),
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
