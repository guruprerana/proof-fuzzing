#!/usr/bin/env python3
"""Run the preregistered clean recent-math held-out evaluation."""

import argparse
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.proof_fuzzer.datasets.json_split import load_json_split
from src.proof_fuzzer.frozen_evaluation import run_frozen_evaluation


DEFAULT_SPLIT = Path("local_datasets/recent_math_research_dossiers_clean_v1.json")
DEFAULT_STRATEGY = Path(
    "logs/by_dataset/recent_math/runs/recent_math_research_clean_all5_distillation_v1_gpt56sol_medium/"
    "distillation/strategies.md"
)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--split-json", type=Path, default=DEFAULT_SPLIT)
    parser.add_argument("--strategy-path", type=Path, default=DEFAULT_STRATEGY)
    parser.add_argument("--storage-dir", required=True, type=Path)
    parser.add_argument("--model", default="gpt-5.6-sol")
    parser.add_argument("--reasoning-effort", default="medium")
    parser.add_argument("--seed", type=int, default=20260920)
    parser.add_argument("--attempts-per-arm", type=int, default=3)
    parser.add_argument("--reviews-per-valid-candidate", type=int, default=2)
    parser.add_argument("--required-missed-reviews", type=int, default=2)
    parser.add_argument("--workers", type=int, default=5)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    _, heldout = load_json_split(args.split_json.resolve())
    run_frozen_evaluation(
        heldout=heldout,
        strategy_path=args.strategy_path.resolve(),
        storage_dir=args.storage_dir,
        model=args.model,
        reasoning_effort=args.reasoning_effort,
        seed=args.seed,
        attempts_per_arm=args.attempts_per_arm,
        workers=args.workers,
        dry_run=args.dry_run,
        reviews_per_valid_candidate=args.reviews_per_valid_candidate,
        required_missed_reviews=args.required_missed_reviews,
    )


if __name__ == "__main__":
    main()
