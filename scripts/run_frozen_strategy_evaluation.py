#!/usr/bin/env python3
"""Evaluate a frozen strategy library on fresh OlympiadBench proofs."""

import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.proof_fuzzer.datasets.olympiadbench import load_examples, load_split_manifest
from src.proof_fuzzer.datasets.json_split import load_json_split
from src.proof_fuzzer.frozen_evaluation import run_frozen_evaluation


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--dataset-root", type=Path)
    source.add_argument("--split-json", type=Path)
    parser.add_argument("--strategy-path", required=True, type=Path)
    parser.add_argument("--storage-dir", required=True, type=Path)
    selection = parser.add_mutually_exclusive_group()
    selection.add_argument("--heldout-folders", nargs="+")
    selection.add_argument("--olympiad-split-manifest", type=Path)
    parser.add_argument("--model")
    parser.add_argument("--provider", choices=("codex", "claude-code", "gemini-cli"),
                        default="codex")
    parser.add_argument("--reasoning-effort", default="medium")
    parser.add_argument("--seed", type=int, default=20260913)
    parser.add_argument("--attempts-per-arm", type=int, default=3)
    parser.add_argument("--alpha", type=float, default=0.01)
    parser.add_argument("--workers", type=int, default=5)
    parser.add_argument("--reviews-per-valid-candidate", type=int, default=3)
    parser.add_argument(
        "--required-missed-reviews", type=int,
        help="Successful candidate threshold; defaults to all blind reviews missing the error",
    )
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--strategy-assignments", type=Path,
        help="JSON object mapping every held-out selector to one directive per candidate")
    args = parser.parse_args()
    default_models = {
        "codex": "gpt-5.6-luna",
        "claude-code": "sonnet",
        "gemini-cli": "gemini-3.5-flash",
    }
    model = args.model or default_models[args.provider]
    if args.split_json:
        if args.heldout_folders or args.olympiad_split_manifest:
            parser.error("--split-json cannot be combined with Olympiad folder selectors")
        _, heldout = load_json_split(args.split_json.resolve())
    elif args.olympiad_split_manifest:
        _, heldout = load_split_manifest(
            args.dataset_root.resolve(), args.olympiad_split_manifest.resolve())
    elif args.heldout_folders:
        heldout = load_examples(
            args.dataset_root.resolve(), args.heldout_folders,
            proof_artifact="model_response", require_correct=True)
    else:
        parser.error("--dataset-root requires --heldout-folders or --olympiad-split-manifest")
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
        strategy_assignments=assignments)


if __name__ == "__main__":
    main()
