#!/usr/bin/env python3
"""Run mutation-detection comparison over stored proof-fuzzer attempts."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[3]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.archive.proof_fuzzer import (
    DEFAULT_BASE_URL,
    GPT_OSS_120B,
    MutationDetectionExperimentConfig,
    run_mutation_detection_experiment,
)


def main() -> None:
    args = parse_args()
    config = MutationDetectionExperimentConfig(
        source_run_dir=args.source_run_dir,
        output_dir=args.output_dir,
        target_attempts=args.target_attempts,
        wait_for_target_attempts=not args.no_wait,
        poll_interval_seconds=args.poll_interval_seconds,
        max_workers=args.max_workers,
        reasoning_effort=args.reasoning_effort,
        temperature=args.temperature,
        max_tokens=args.max_tokens,
        base_url=args.base_url,
        model=args.model,
        max_problem_chars=args.max_problem_chars,
        max_rubric_chars=args.max_rubric_chars,
        max_proof_chars=args.max_proof_chars,
        include_unsuccessful_completed_mutations=not args.only_successful_fuzz_mutations,
    )
    result = run_mutation_detection_experiment(config)
    print(result.summary())


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source_run_dir", type=Path)
    parser.add_argument("--output-dir", type=Path, default=None)
    parser.add_argument("--target-attempts", type=int, default=1000)
    parser.add_argument("--no-wait", action="store_true")
    parser.add_argument("--poll-interval-seconds", type=float, default=60.0)
    parser.add_argument("--max-workers", type=int, default=4)
    parser.add_argument("--reasoning-effort", default="high")
    parser.add_argument("--temperature", type=float, default=0.0)
    parser.add_argument("--max-tokens", type=int, default=16000)
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL)
    parser.add_argument("--model", default=GPT_OSS_120B)
    parser.add_argument("--max-problem-chars", type=int, default=2000)
    parser.add_argument("--max-rubric-chars", type=int, default=3000)
    parser.add_argument("--max-proof-chars", type=int, default=8000)
    parser.add_argument(
        "--only-successful-fuzz-mutations",
        action="store_true",
        help="Restrict to mutations that already fooled the proof judge.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    main()
