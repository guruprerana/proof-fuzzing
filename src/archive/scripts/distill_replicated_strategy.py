#!/usr/bin/env python3
"""Distill a strategy library from complete frozen runs' replicated misses."""

import argparse
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.proof_fuzzer.robust_distillation import distill_replicated_library


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-roots", nargs="+", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--model", default="gpt-5.6-terra")
    parser.add_argument("--reasoning-effort", default="medium")
    parser.add_argument("--required-misses", type=int, default=2)
    parser.add_argument(
        "--allow-incomplete-discovery",
        action="store_true",
        help="Allow stopped partial runs as exploratory discovery evidence",
    )
    args = parser.parse_args()
    distill_replicated_library(
        run_roots=args.run_roots,
        output_dir=args.output_dir,
        model=args.model,
        reasoning_effort=args.reasoning_effort,
        required_misses=args.required_misses,
        allow_incomplete_discovery=args.allow_incomplete_discovery,
    )


if __name__ == "__main__":
    main()
