#!/usr/bin/env python3
"""Replay successful proof-fuzzer attacks through an alternate grading prompt."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.proof_fuzzer import (
    DEFAULT_GEMINI_MODEL,
    DEFAULT_GEMINI_THINKING_LEVEL,
    CompetitionJudgeRobustnessConfig,
    run_competition_judge_robustness_evaluation,
)


def main() -> None:
    args = parse_args()
    config = CompetitionJudgeRobustnessConfig(
        source_run_dir=args.source_run_dir,
        output_dir=args.output_dir,
        max_workers=args.max_workers,
        model=args.model,
        thinking_level=args.thinking_level,
        temperature=args.temperature,
        max_tokens=args.max_tokens,
        max_problem_chars=args.max_problem_chars,
        max_proof_chars=args.max_proof_chars,
        limit=args.limit,
    )
    result = run_competition_judge_robustness_evaluation(config)
    print(result.summary())


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source_run_dir", type=Path)
    parser.add_argument("--output-dir", type=Path, default=None)
    parser.add_argument("--max-workers", type=int, default=4)
    parser.add_argument("--model", default=DEFAULT_GEMINI_MODEL)
    parser.add_argument("--thinking-level", default=DEFAULT_GEMINI_THINKING_LEVEL)
    parser.add_argument("--temperature", type=float, default=0.0)
    parser.add_argument("--max-tokens", type=int, default=32000)
    parser.add_argument("--max-problem-chars", type=int, default=4000)
    parser.add_argument("--max-proof-chars", type=int, default=12000)
    parser.add_argument("--limit", type=int, default=None)
    return parser.parse_args()


if __name__ == "__main__":
    main()
