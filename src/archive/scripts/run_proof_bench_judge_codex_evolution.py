#!/usr/bin/env python3
"""Run ProofBenchJudge evolutionary fuzzing through the Codex Python SDK."""

from pathlib import Path
import sys


REPO_ROOT = Path(__file__).resolve().parents[3]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.archive.proof_fuzzer import (
    DEFAULT_PROOF_BENCH_JUDGE_ROOT,
    ProofBenchJudgeEvolutionRunConfig,
    run_proof_bench_judge_evolution,
)
from scripts._codex_evolution_cli import (
    CodexEvolutionDefaults,
    run_codex_evolution_cli,
)


def main() -> None:
    run_codex_evolution_cli(
        description=__doc__ or "",
        defaults=CodexEvolutionDefaults(
            root=DEFAULT_PROOF_BENCH_JUDGE_ROOT,
            run_name_prefix="proof_bench_judge_codex",
            num_attempts=500,
            max_workers=1,
            max_tokens=32_000,
            strategy_probability=0.7,
            strategy_selection_mode="retrieval",
            run_pre_mutation_judge=False,
            evolution_threshold=10,
            correctness_selection_mode="false_proof",
            false_proof_probability=1.0,
            max_proof_chars=24_000,
            max_problem_chars=2_000,
            continue_on_error=True,
            objective_prefix=(
                "Codex GPT-5.5 medium-reasoning ProofBenchJudge evolutionary fuzzing run on "
                "correct proofs; introduce subtle invalid proof errors that may fool the blind judge."
            ),
        ),
        config_type=ProofBenchJudgeEvolutionRunConfig,
        run_evolution=run_proof_bench_judge_evolution,
    )


if __name__ == "__main__":
    main()
