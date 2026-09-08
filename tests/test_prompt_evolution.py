from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import tempfile
import threading
import unittest

from src.proof_fuzzer import (
    DEFAULT_MUTATION_POLICY,
    EvolutionConfig,
    MutationPromptStore,
    MutationPromptVersion,
    NaturalLanguageProofFuzzerLLMInterface,
    PromptEvolutionConfig,
    run_prompt_evolutionary_pipeline,
)


MUTATION_RESPONSE = """{
  "maintain_correctness": false,
  "rationale": "Break an indispensable parity representation.",
  "mutations": [{
    "kind": "modify",
    "target": "S2",
    "summary": "Replace the even representation with an odd one.",
    "new_text": "Then n = 2k + 1 for some integer k.",
    "affected_blocks": [],
    "propagate_downstream": false
  }]
}"""

JUDGE_INCORRECT_RESPONSE = """{
  "verdict": "incorrect",
  "confidence": 0.9,
  "rationale": "The mutated parity representation is invalid.",
  "detected_flaw": "An even integer was represented as odd."
}"""

JUDGE_CORRECT_RESPONSE = """{
  "verdict": "correct",
  "confidence": 0.8,
  "rationale": "The proof appears acceptable.",
  "detected_flaw": ""
}"""

JUDGE_ERROR_REPORTED_RESPONSE = """{
  "introduced_error_found": true,
  "matching_report_indices": [0],
  "matching_error_indices": [{"report_index": 0, "error_index": 0}],
  "match_level": "exact",
  "rationale": "The planted parity error was explicitly identified."
}"""

EVOLVED_POLICY = """Goal:
Create a coherent but invalid proof.

Strategies:
- Attack an indispensable bridge between two otherwise plausible steps.

Do not:
- Make notation inconsistent or reveal the intended error.

Before returning:
1. Confirm that the broken inference is necessary.
2. Confirm that the remaining proof does not repair it."""


class FakeLLM:
    def __init__(self, responses):
        self.responses = list(responses)
        self.prompts: list[str] = []
        self.lock = threading.Lock()

    def complete(self, prompt: str) -> str:
        with self.lock:
            self.prompts.append(prompt)
            if not self.responses:
                raise AssertionError("No fake LLM response is available.")
            response = self.responses.pop(0)
        if isinstance(response, Exception):
            raise response
        return response


@dataclass(frozen=True)
class Example:
    example_id: str = "example"
    problem: str = "Prove that the square of an even integer is even."
    proof: str = (
        "Let n be even.\n\n"
        "Then n = 2k for some integer k.\n\n"
        "Therefore n squared is even."
    )

    def to_metadata(self) -> dict[str, object]:
        return {
            "dataset": "test",
            "example_id": self.example_id,
            "problem": self.problem,
            "llm_category": "algebra",
        }


class PromptEvolutionTest(unittest.TestCase):
    def test_initial_math_policy_encourages_single_cause_propagation(self) -> None:
        self.assertIn("Propagate the changed premise or inference", DEFAULT_MUTATION_POLICY)
        self.assertIn("same planted root error", DEFAULT_MUTATION_POLICY)
        self.assertIn("wherever coherence requires it", DEFAULT_MUTATION_POLICY)

    def test_mutation_policy_replaces_fixed_and_strategy_guidance(self) -> None:
        policy = """Strategies:
- Use the unique evolved tactic.
Do not:
- Use the unique forbidden tactic.
Before returning:
1. Run the unique final check."""
        interface = NaturalLanguageProofFuzzerLLMInterface(
            Example().proof,
            mutation_policy=policy,
        )

        prompt = interface.false_proof_mutation_instruction_prompt(
            strategy_guidance=("legacy strategy",),
            prior_attempt_guidance=("legacy attempt",),
        )

        self.assertIn("Mutation policy:\n" + policy, prompt)
        self.assertNotIn("legacy strategy", prompt)
        self.assertNotIn("legacy attempt", prompt)
        self.assertNotIn("High-value direct mutations", prompt)
        self.assertIn("Targetable proof segments:", prompt)
        self.assertIn('"maintain_correctness": false', prompt)

    def test_prompt_store_persists_current_and_history(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            store = MutationPromptStore(tmp_dir)
            initial = store.initialize(DEFAULT_MUTATION_POLICY, max_chars=5_000)
            evolved = MutationPromptVersion(
                version=1,
                parent_version=0,
                prompt_text=EVOLVED_POLICY,
                training_attempt_ids=("attempt_1",),
                change_summary="Prefer indispensable bridges.",
            )

            store.save(evolved, max_chars=5_000)

            reloaded = MutationPromptStore(tmp_dir)
            self.assertEqual(reloaded.load_current(), evolved)
            self.assertEqual(reloaded.load_history(), (initial, evolved))
            self.assertEqual(reloaded.load_current().prompt_sha256, evolved.prompt_sha256)

    def test_pipeline_freezes_prompt_for_generation_then_evolves(self) -> None:
        evolution_response = json.dumps(
            {
                "prompt_text": EVOLVED_POLICY,
                "change_summary": "Prefer indispensable proof bridges.",
                "evidence_attempt_ids": [],
            }
        )
        llm = FakeLLM(
            [
                MUTATION_RESPONSE,
                JUDGE_INCORRECT_RESPONSE,
                JUDGE_CORRECT_RESPONSE,
                MUTATION_RESPONSE,
                JUDGE_INCORRECT_RESPONSE,
                JUDGE_CORRECT_RESPONSE,
                evolution_response,
            ]
        )

        with tempfile.TemporaryDirectory() as tmp_dir:
            result = run_prompt_evolutionary_pipeline(
                examples=(Example(),),
                llm=llm,
                config=PromptEvolutionConfig(
                    storage_dir=tmp_dir,
                    generation_size=2,
                    random_seed=7,
                ),
                attempt_config=EvolutionConfig(
                    storage_dir=tmp_dir,
                    run_pre_mutation_judge=False,
                    trace_llm_calls=False,
                ),
                num_attempts=2,
                dataset_name="test",
            )

            self.assertEqual(len(result.attempts), 2)
            self.assertTrue(all(attempt.success for attempt in result.attempts))
            self.assertEqual(result.current_prompt.version, 1)
            self.assertEqual(result.current_prompt.prompt_text, EVOLVED_POLICY)
            prompt_hashes = {
                attempt.metadata["mutation_prompt_sha256"]
                for attempt in result.attempts
            }
            self.assertEqual(
                prompt_hashes,
                {hashlib.sha256(DEFAULT_MUTATION_POLICY.encode("utf-8")).hexdigest()},
            )
            self.assertTrue(all(attempt.strategy_ids == () for attempt in result.attempts))
            self.assertIn(DEFAULT_MUTATION_POLICY, llm.prompts[0])
            self.assertIn(DEFAULT_MUTATION_POLICY, llm.prompts[3])
            self.assertIn("Recent judged outcomes", llm.prompts[6])
            self.assertFalse((Path(tmp_dir) / "strategies_natural_language.jsonl").exists())
            self.assertEqual(len(MutationPromptStore(tmp_dir).load_history()), 2)

    def test_second_run_completes_a_partial_generation(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            config = PromptEvolutionConfig(
                storage_dir=tmp_dir,
                generation_size=2,
                random_seed=3,
            )
            attempt_config = EvolutionConfig(
                storage_dir=tmp_dir,
                run_pre_mutation_judge=False,
                trace_llm_calls=False,
            )
            first_llm = FakeLLM(
                [MUTATION_RESPONSE, JUDGE_INCORRECT_RESPONSE, JUDGE_CORRECT_RESPONSE]
            )
            first = run_prompt_evolutionary_pipeline(
                examples=(Example(),),
                llm=first_llm,
                config=config,
                attempt_config=attempt_config,
                num_attempts=1,
            )
            self.assertEqual(first.current_prompt.version, 0)

            evolution_response = json.dumps(
                {
                    "prompt_text": EVOLVED_POLICY,
                    "change_summary": "Use a stronger self-check.",
                }
            )
            second_llm = FakeLLM(
                [
                    MUTATION_RESPONSE,
                    JUDGE_INCORRECT_RESPONSE,
                    JUDGE_CORRECT_RESPONSE,
                    evolution_response,
                ]
            )
            second = run_prompt_evolutionary_pipeline(
                examples=(Example(),),
                llm=second_llm,
                config=config,
                attempt_config=attempt_config,
                num_attempts=1,
            )

            self.assertEqual(second.current_prompt.version, 1)
            self.assertEqual(len(second.current_prompt.training_attempt_ids), 2)

    def test_invalid_evolved_policy_keeps_current_version_and_records_error(self) -> None:
        invalid_evolution_response = json.dumps(
            {
                "prompt_text": "A policy without the required sections.",
                "change_summary": "Invalid update.",
            }
        )
        llm = FakeLLM(
            [
                MUTATION_RESPONSE,
                JUDGE_INCORRECT_RESPONSE,
                JUDGE_CORRECT_RESPONSE,
                invalid_evolution_response,
            ]
        )

        with tempfile.TemporaryDirectory() as tmp_dir:
            result = run_prompt_evolutionary_pipeline(
                examples=(Example(),),
                llm=llm,
                config=PromptEvolutionConfig(
                    storage_dir=tmp_dir,
                    generation_size=1,
                    evolution_retries=0,
                ),
                attempt_config=EvolutionConfig(
                    storage_dir=tmp_dir,
                    run_pre_mutation_judge=False,
                    trace_llm_calls=False,
                ),
                num_attempts=1,
            )

            self.assertEqual(result.current_prompt.version, 0)
            error_path = Path(tmp_dir) / "mutation_prompt_evolution_errors.jsonl"
            self.assertTrue(error_path.is_file())
            self.assertIn("required", error_path.read_text(encoding="utf-8"))

    def test_zero_success_generation_cannot_grow_the_policy(self) -> None:
        longer_policy = DEFAULT_MUTATION_POLICY + "\nDo not add unsupported tactics."
        evolution_response = json.dumps(
            {
                "prompt_text": longer_policy,
                "change_summary": "Added a rule despite having no success evidence.",
            }
        )
        llm = FakeLLM(
            [
                MUTATION_RESPONSE,
                JUDGE_INCORRECT_RESPONSE,
                JUDGE_CORRECT_RESPONSE,
                JUDGE_ERROR_REPORTED_RESPONSE,
                evolution_response,
            ]
        )

        with tempfile.TemporaryDirectory() as tmp_dir:
            result = run_prompt_evolutionary_pipeline(
                examples=(Example(),),
                llm=llm,
                config=PromptEvolutionConfig(
                    storage_dir=tmp_dir,
                    generation_size=1,
                    evolution_retries=0,
                    max_prompt_growth_chars=1_000,
                ),
                attempt_config=EvolutionConfig(
                    storage_dir=tmp_dir,
                    run_pre_mutation_judge=False,
                    judge_error_detection_check=True,
                    trace_llm_calls=False,
                ),
                num_attempts=1,
            )

            self.assertEqual(result.current_prompt.version, 0)
            self.assertFalse(result.attempts[0].success)
            evolution_prompt = llm.prompts[-1]
            self.assertIn("No successful attempts exist", evolution_prompt)
            self.assertIn("do not increase the policy length", evolution_prompt)
            error_path = Path(tmp_dir) / "mutation_prompt_evolution_errors.jsonl"
            self.assertIn("maximum is", error_path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
