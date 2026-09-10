from __future__ import annotations

import json
from pathlib import Path
import tempfile
import threading
import unittest

from src.proof_fuzzer import (
    DEFAULT_MUTATION_POLICY,
    EvolutionConfig,
    OpenAITenAdvancesProof,
    PromptEvolutionExperimentConfig,
    run_openai_ten_advances_prompt_evolution_experiment,
    split_openai_ten_advances_proofs,
)


MUTATION_RESPONSE = json.dumps(
    {
        "maintain_correctness": False,
        "rationale": "Break an indispensable parity representation.",
        "mutations": [
            {
                "kind": "modify",
                "target": "S2",
                "summary": "Replace the even representation with an odd one.",
                "new_text": "Then n = 2k + 1 for some integer k.",
                "affected_blocks": [],
                "propagate_downstream": False,
            }
        ],
    }
)
JUDGE_INCORRECT_RESPONSE = json.dumps(
    {
        "verdict": "incorrect",
        "confidence": 0.9,
        "rationale": "The parity representation is invalid.",
        "detected_flaw": "An even integer was represented as odd.",
    }
)
JUDGE_CORRECT_RESPONSE = json.dumps(
    {
        "verdict": "correct",
        "confidence": 0.8,
        "rationale": "The proof appears acceptable.",
        "detected_flaw": "",
    }
)
EVOLVED_POLICY = """Goal:
Create a coherent but invalid proof.

Strategies:
- Attack an indispensable bridge between two plausible steps.

Do not:
- Reveal the intended error or introduce inconsistent notation.

Before returning:
1. Confirm that the broken inference is necessary.
2. Confirm that no later step repairs it."""


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
        title=f"Theorem {index}",
        abstract="A parity theorem.",
        proof=(
            "Let n be even.\n\n"
            "Then n = 2k for some integer k.\n\n"
            "Therefore n squared is even."
        ),
    )


class PromptEvolutionExperimentTest(unittest.TestCase):
    def test_split_is_seeded_disjoint_and_exhaustive(self) -> None:
        examples = tuple(_example(index) for index in range(10))

        first = split_openai_ten_advances_proofs(
            examples,
            train_problem_count=5,
            split_seed=41,
        )
        second = split_openai_ten_advances_proofs(
            tuple(reversed(examples)),
            train_problem_count=5,
            split_seed=41,
        )

        self.assertEqual(first, second)
        train_ids = {example.example_id for example in first[0]}
        test_ids = {example.example_id for example in first[1]}
        self.assertFalse(train_ids & test_ids)
        self.assertEqual(train_ids | test_ids, {example.example_id for example in examples})

    def test_experiment_trains_then_compares_frozen_prompts_on_holdout(self) -> None:
        attempt_responses = [
            MUTATION_RESPONSE,
            JUDGE_INCORRECT_RESPONSE,
            JUDGE_CORRECT_RESPONSE,
        ]
        evolution_response = json.dumps(
            {
                "prompt_text": EVOLVED_POLICY,
                "change_summary": "Prefer indispensable bridges.",
            }
        )
        # Two training attempts, one evolution, then four held-out attempts.
        llm = FakeLLM(
            attempt_responses * 2
            + [evolution_response]
            + attempt_responses * 4
        )
        examples = tuple(_example(index) for index in range(4))

        with tempfile.TemporaryDirectory() as tmp_dir:
            result = run_openai_ten_advances_prompt_evolution_experiment(
                llm=llm,
                examples=examples,
                config=PromptEvolutionExperimentConfig(
                    storage_dir=tmp_dir,
                    train_problem_count=2,
                    training_generations=1,
                    test_attempts_per_problem=1,
                    split_seed=7,
                    evaluation_seed=8,
                    max_workers=1,
                ),
                attempt_config=EvolutionConfig(
                    storage_dir=tmp_dir,
                    # Legacy caps must not truncate training or held-out proofs.
                    max_proof_chars=1,
                    run_pre_mutation_judge=False,
                    trace_llm_calls=False,
                ),
            )

            self.assertEqual(len(result.training_attempts), 2)
            self.assertEqual(len(result.baseline_attempts), 2)
            self.assertEqual(len(result.learned_attempts), 2)
            source_proofs = {example.example_id: example.proof for example in examples}
            for attempt in (*result.training_attempts, *result.baseline_attempts,
                            *result.learned_attempts):
                expected = source_proofs[attempt.metadata["example_id"]]
                self.assertEqual(attempt.original_proof_text, expected)
                self.assertEqual(attempt.metadata["proof_chars_used"], len(expected))
                self.assertEqual(attempt.metadata["proof_chars_original"], len(expected))
            self.assertEqual(result.learned_prompt.version, 1)
            self.assertEqual(result.learned_prompt.prompt_text, EVOLVED_POLICY)
            self.assertFalse(set(result.train_example_ids) & set(result.test_example_ids))
            self.assertTrue(
                all(
                    attempt.metadata["mutation_prompt_sha256"]
                    == result.initial_prompt.prompt_sha256
                    for attempt in result.baseline_attempts
                )
            )
            self.assertTrue(
                all(
                    attempt.metadata["mutation_prompt_sha256"]
                    == result.learned_prompt.prompt_sha256
                    for attempt in result.learned_attempts
                )
            )
            self.assertTrue(
                all(
                    attempt.metadata["example_id"] in result.test_example_ids
                    for attempt in (*result.baseline_attempts, *result.learned_attempts)
                )
            )
            self.assertEqual(
                result.metrics["comparison"]["success_rate_delta"],  # type: ignore[index]
                0.0,
            )
            summary = json.loads(
                (Path(tmp_dir) / "summary.json").read_text(encoding="utf-8")
            )
            self.assertEqual(summary["learned_prompt"]["version"], 1)
            self.assertEqual(
                (Path(tmp_dir) / "initial_prompt.txt").read_text(encoding="utf-8").strip(),
                DEFAULT_MUTATION_POLICY,
            )
            self.assertEqual(
                (Path(tmp_dir) / "learned_prompt.txt").read_text(encoding="utf-8").strip(),
                EVOLVED_POLICY,
            )


if __name__ == "__main__":
    unittest.main()
