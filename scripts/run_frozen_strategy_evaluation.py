#!/usr/bin/env python3
"""Evaluate a frozen strategy library on fresh held-out proofs."""

import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.proof_fuzzer.datasets.json_split import load_json_split
from src.proof_fuzzer.frozen_evaluation import run_frozen_evaluation
from src.proof_fuzzer.openai_ten_advances import load_openai_ten_advances_split


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--split-json", type=Path)
    source.add_argument("--tcs-root", type=Path)
    parser.add_argument("--strategy-path", required=True, type=Path)
    parser.add_argument("--storage-dir", required=True, type=Path)
    parser.add_argument("--model")
    parser.add_argument("--provider", choices=("codex", "claude-code"),
                        default="codex")
    parser.add_argument("--reasoning-effort", default="medium")
    parser.add_argument("--seed", type=int, default=20260913)
    parser.add_argument("--attempts-per-arm", type=int, default=3)
    parser.add_argument("--alpha", type=float, default=0.01)
    parser.add_argument("--workers", type=int, default=5)
    parser.add_argument("--reviews-per-valid-candidate", type=int, default=3)
    parser.add_argument(
        "--no-call-timeout", action="store_true",
        help="Allow judge and assessment calls to run without a hard wall-clock timeout",
    )
    parser.add_argument(
        "--required-missed-reviews", type=int,
        help="Successful candidate threshold; defaults to all blind reviews missing the error",
    )
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--strategy-assignments", type=Path,
        help="JSON object mapping every held-out selector to one directive per candidate")
    args = parser.parse_args()
    default_models = {
        "codex": "gpt-5.6-sol",
        "claude-code": "claude-opus-5",
    }
    model = args.model or default_models[args.provider]
    if args.tcs_root:
        _, heldout = load_openai_ten_advances_split(args.tcs_root.resolve())
    else:
        _, heldout = load_json_split(args.split_json.resolve())
    assignments = (json.loads(args.strategy_assignments.read_text())
                   if args.strategy_assignments else None)
    run_frozen_evaluation(heldout=heldout, strategy_path=args.strategy_path,
        storage_dir=args.storage_dir, model=model,
        provider=args.provider,
        reasoning_effort=args.reasoning_effort, seed=args.seed,
        attempts_per_arm=args.attempts_per_arm, alpha=args.alpha,
        workers=args.workers, dry_run=args.dry_run,
        reviews_per_valid_candidate=args.reviews_per_valid_candidate,
        required_missed_reviews=args.required_missed_reviews,
        strategy_assignments=assignments,
        disable_call_timeout=args.no_call_timeout)


if __name__ == "__main__":
    main()
