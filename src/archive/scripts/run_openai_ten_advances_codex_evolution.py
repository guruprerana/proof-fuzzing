#!/usr/bin/env python3
"""Run evolutionary fuzzing on OpenAI's ten-advances proofs with Codex."""

from pathlib import Path
import sys


REPO_ROOT = Path(__file__).resolve().parents[3]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.archive.proof_fuzzer import (
    DEFAULT_OPENAI_TEN_ADVANCES_ROOT,
    OpenAITenAdvancesEvolutionRunConfig,
    run_openai_ten_advances_evolution,
)
from scripts._codex_evolution_cli import (
    CodexEvolutionDefaults,
    run_codex_evolution_cli,
)


def main() -> None:
    run_codex_evolution_cli(
        description=__doc__ or "",
        defaults=CodexEvolutionDefaults(
            root=DEFAULT_OPENAI_TEN_ADVANCES_ROOT,
            run_name_prefix="openai_ten_advances_codex",
            run_name_suffix="_no_mined",
            num_attempts=200,
            max_workers=10,
            max_tokens=32_000,
            strategy_probability=0.7,
            strategy_selection_mode="retrieval",
            run_pre_mutation_judge=False,
            evolution_threshold=10,
            correctness_selection_mode="false_proof",
            false_proof_probability=1.0,
            max_proof_chars=300_000,
            max_problem_chars=12_000,
            continue_on_error=True,
            objective_prefix=(
                "Codex evolutionary fuzzing of recently published open-problem proofs; introduce "
                "subtle invalid proof errors that may fool the blind judge."
            ),
        ),
        config_type=OpenAITenAdvancesEvolutionRunConfig,
        run_evolution=run_openai_ten_advances_evolution,
    )


if __name__ == "__main__":
    main()
