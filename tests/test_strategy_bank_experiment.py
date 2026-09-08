from __future__ import annotations

import json
from pathlib import Path
import tempfile
import threading
import unittest

from src.proof_fuzzer import (
    EvolutionConfig,
    OpenAITenAdvancesProof,
    StrategyBankExperimentConfig,
    run_openai_ten_advances_strategy_bank_experiment,
)


MUTATION_RESPONSE = json.dumps(
    {
        "maintain_correctness": False,
        "rationale": "Break an indispensable parity representation.",
        "mutations": [
            {
                "kind": "modify",
                "target": "S2",
                "summary": "Replace an even representation with an odd one.",
                "new_text": "Then n = 2k + 1 for some integer k.",
                "affected_blocks": [],
                "propagate_downstream": False,
            }
        ],
    }
)
INCORRECT = json.dumps(
    {
        "verdict": "incorrect",
        "confidence": 0.9,
        "rationale": "The parity representation is invalid.",
        "detected_flaw": "An even integer was represented as odd.",
    }
)
CORRECT = json.dumps(
    {
        "verdict": "correct",
        "confidence": 0.8,
        "rationale": "The proof appears acceptable.",
        "detected_flaw": "",
    }
)
STRATEGY_RESPONSE = json.dumps(
    {
        "strategies": [
            {
                "strategy_id": "parity_bridge",
                "title": "Hidden parity bridge",
                "guidance": "Alter an indispensable representation while preserving downstream form.",
                "math_topic": "algebra",
                "target_correctness": False,
                "successes": 0,
                "failures": 0,
                "provenance_attempt_ids": [],
                "metadata": {"source": "evolved", "keywords": ["parity"]},
            }
        ]
    }
)


class FakeLLM:
    def __init__(self, responses: list[str]):
        self.responses = list(responses)
        self.prompts: list[str] = []
        self.lock = threading.Lock()

    def complete(self, prompt: str) -> str:
        with self.lock:
            self.prompts.append(prompt)
            if not self.responses:
                raise AssertionError("No fake response remains.")
            return self.responses.pop(0)


def _example(index: int) -> OpenAITenAdvancesProof:
    return OpenAITenAdvancesProof(
        example_id=f"proof_{index}",
        path=Path(f"proof_{index}.md"),
        title=f"Polynomial theorem {index}",
        abstract="A polynomial and parity theorem.",
        proof="Let n be even.\n\nThen n = 2k.\n\nTherefore n squared is even.",
    )


class StrategyBankExperimentTest(unittest.TestCase):
    def test_trains_freezes_and_injects_assigned_strategy(self) -> None:
        attempt_responses = [MUTATION_RESPONSE, INCORRECT, CORRECT]
        # Two training attempts, one bank rewrite, and four evaluation attempts.
        llm = FakeLLM(attempt_responses * 2 + [STRATEGY_RESPONSE] + attempt_responses * 4)
        examples = tuple(_example(index) for index in range(4))
        with tempfile.TemporaryDirectory() as tmp_dir:
            result = run_openai_ten_advances_strategy_bank_experiment(
                llm=llm,
                examples=examples,
                config=StrategyBankExperimentConfig(
                    storage_dir=tmp_dir,
                    train_problem_count=2,
                    training_rounds=1,
                    training_attempts_per_problem_per_round=1,
                    test_attempts_per_problem=1,
                    max_workers=1,
                    strategy_evolution_retries=0,
                ),
                attempt_config=EvolutionConfig(
                    storage_dir=tmp_dir,
                    run_pre_mutation_judge=False,
                    trace_llm_calls=False,
                ),
            )

            self.assertEqual(len(result.training_attempts), 2)
            self.assertEqual(len(result.frozen_bank), 1)
            self.assertEqual(len(result.baseline_attempts), 2)
            self.assertEqual(len(result.learned_attempts), 2)
            self.assertTrue(all(not attempt.strategy_ids for attempt in result.baseline_attempts))
            self.assertTrue(
                all(attempt.strategy_ids == ("parity_bridge",) for attempt in result.learned_attempts)
            )
            self.assertTrue(
                all(
                    attempt.metadata["strategy_assignment_frozen"]
                    for attempt in result.learned_attempts
                )
            )
            self.assertTrue(
                any("Hidden parity bridge" in prompt for prompt in llm.prompts)
            )
            self.assertTrue((Path(tmp_dir) / "frozen_strategy_bank.json").is_file())
            self.assertTrue((Path(tmp_dir) / "heldout_strategy_assignments.json").is_file())


if __name__ == "__main__":
    unittest.main()
