#!/usr/bin/env python3
"""Run discovery, distillation, and held-out transfer on individual REFLECT traces."""

import argparse
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.proof_fuzzer.agent_trace import AgentTraceProfile
from src.proof_fuzzer.datasets.reflect import load_process_traces, select_diverse_split
from src.proof_fuzzer.strategy_transfer import run_strategy_transfer


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset-root", required=True, type=Path)
    parser.add_argument("--storage-dir", required=True, type=Path)
    parser.add_argument("--model", default="gpt-5.6-terra")
    parser.add_argument("--reasoning-effort", default="medium")
    parser.add_argument("--seed", type=int, default=20260911)
    parser.add_argument("--discovery-traces", type=int, default=5)
    parser.add_argument("--heldout-traces", type=int, default=5)
    parser.add_argument("--discovery-attempts", type=int, default=25)
    parser.add_argument("--evaluation-attempts-per-trace", type=int, default=5)
    parser.add_argument("--max-trace-characters", type=int, default=100_000)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    examples = load_process_traces(args.dataset_root.resolve())
    discovery, heldout = select_diverse_split(
        examples, discovery_count=args.discovery_traces, heldout_count=args.heldout_traces,
        seed=args.seed, max_characters=args.max_trace_characters)
    run_strategy_transfer(
        discovery=discovery, heldout=heldout, storage_dir=args.storage_dir,
        model=args.model, reasoning_effort=args.reasoning_effort, seed=args.seed,
        discovery_attempts=args.discovery_attempts,
        evaluation_attempts_per_proof=args.evaluation_attempts_per_trace,
        dry_run=args.dry_run, profile=AgentTraceProfile())


if __name__ == "__main__":
    main()
