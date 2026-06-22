import tempfile
import unittest

from src.proof_fuzzer import (
    EvolutionConfig,
    EvolutionaryProofFuzzer,
    FuzzAttempt,
    FuzzStrategy,
    JudgeResult,
    NaturalLanguageProofFuzzerLLMInterface,
    ProofFuzzAttemptStore,
    fuzz_attempt_succeeded,
    parse_judge_result,
    parse_mutation_instructions,
    parse_strategy_evolution_response,
)


class FakeLLM:
    def __init__(self, responses):
        self.responses = list(responses)
        self.prompts = []
        self.last_result = None

    def complete(self, prompt: str) -> str:
        self.prompts.append(prompt)
        if not self.responses:
            raise AssertionError("No fake LLM response is available.")
        response = self.responses.pop(0)
        if isinstance(response, Exception):
            raise response
        return response


class FinishReason:
    def __init__(self, finish_reason: str):
        self.finish_reason = finish_reason


class FinishReasonLLM(FakeLLM):
    def __init__(self, responses, finish_reasons):
        super().__init__(responses)
        self.finish_reasons = list(finish_reasons)

    def complete(self, prompt: str) -> str:
        response = super().complete(prompt)
        finish_reason = self.finish_reasons.pop(0) if self.finish_reasons else "stop"
        self.last_result = FinishReason(finish_reason)
        return response


MUTATION_RESPONSE = """{
  "maintain_correctness": false,
  "rationale": "Make a locally plausible parity mistake.",
  "mutations": [
    {
      "kind": "modify",
      "target": "S2",
      "summary": "Switch even to odd representation.",
      "new_text": "Then n = 2k + 1 for some integer k.",
      "affected_blocks": [],
      "propagate_downstream": false
    }
  ]
}"""

JUDGE_CORRECT_RESPONSE = """{
  "verdict": "correct",
  "confidence": 0.82,
  "rationale": "The argument appears to preserve the conclusion.",
  "detected_flaw": ""
}"""

EVOLUTION_RESPONSE = """{
  "strategies": [
    {
      "strategy_id": "",
      "title": "Plausible representation slip",
      "guidance": "Change an intermediate representation while keeping the prose locally fluent.",
      "target_correctness": false,
      "successes": 1,
      "failures": 0,
      "provenance_attempt_ids": []
    }
  ]
}"""

CORRECTNESS_PRESERVING_MUTATION_RESPONSE = """{
  "maintain_correctness": true,
  "rationale": "Use an equivalent representation.",
  "mutations": [
    {
      "kind": "modify",
      "target": "S2",
      "summary": "Use a renamed integer witness.",
      "new_text": "Then n = 2m for some integer m.",
      "affected_blocks": [],
      "propagate_downstream": true
    }
  ]
}"""

JUDGE_INCORRECT_RESPONSE = """{
  "verdict": "incorrect",
  "confidence": 0.75,
  "rationale": "The proof appears to have a gap.",
  "detected_flaw": "missing justification"
}"""


class EvolutionaryFuzzerTest(unittest.TestCase):
    def test_parse_judge_result_and_success_rules(self) -> None:
        result = parse_judge_result(JUDGE_CORRECT_RESPONSE)

        self.assertEqual(result.verdict, "correct")
        self.assertTrue(fuzz_attempt_succeeded(False, result))
        self.assertFalse(fuzz_attempt_succeeded(True, result))
        self.assertTrue(fuzz_attempt_succeeded(True, JudgeResult(verdict="uncertain")))

    def test_jsonl_store_persists_attempts_and_separate_strategy_banks(self) -> None:
        instructions = parse_mutation_instructions(MUTATION_RESPONSE)
        attempt = FuzzAttempt(
            attempt_id="attempt_1",
            fuzzer_kind="natural_language",
            objective="test",
            maintain_correctness=False,
            original_proof_text="original",
            mutated_proof_text="mutated",
            mutation_instructions=instructions,
            judge_result=JudgeResult(verdict="correct", confidence=0.5),
            success=True,
            strategy_ids=("strategy_1",),
        )
        natural_strategy = FuzzStrategy(
            strategy_id="strategy_nl",
            fuzzer_kind="natural_language",
            title="NL",
            guidance="Use prose-level slips.",
        )
        semiformal_strategy = FuzzStrategy(
            strategy_id="strategy_sf",
            fuzzer_kind="semiformal",
            title="SF",
            guidance="Use dependency slips.",
        )

        with tempfile.TemporaryDirectory() as tmp_dir:
            store = ProofFuzzAttemptStore(tmp_dir)
            store.append_attempt(attempt)
            store.save_strategies("natural_language", [natural_strategy])
            store.save_strategies("semiformal", [semiformal_strategy])

            reloaded = ProofFuzzAttemptStore(tmp_dir)
            attempts = reloaded.load_attempts(fuzzer_kind="natural_language")

            self.assertEqual(len(attempts), 1)
            self.assertEqual(attempts[0].attempt_id, "attempt_1")
            self.assertEqual(reloaded.load_strategies("natural_language")[0].strategy_id, "strategy_nl")
            self.assertEqual(reloaded.load_strategies("semiformal")[0].strategy_id, "strategy_sf")

    def test_evolutionary_fuzzer_records_judged_natural_language_attempt(self) -> None:
        proof = "Let n be even.\n\nThen n = 2k for some integer k.\n\nTherefore n^2 is even."
        llm = FakeLLM([JUDGE_CORRECT_RESPONSE, MUTATION_RESPONSE, JUDGE_CORRECT_RESPONSE, JUDGE_INCORRECT_RESPONSE])

        with tempfile.TemporaryDirectory() as tmp_dir:
            config = EvolutionConfig(
                storage_dir=tmp_dir,
                strategy_injection_probability=0.0,
                evolution_threshold=0,
            )
            fuzzer = NaturalLanguageProofFuzzerLLMInterface(proof, llm)
            evolutionary = EvolutionaryProofFuzzer(fuzzer, config=config)

            attempt = evolutionary.run_false_proof_attempt(objective="fool the judge")

            self.assertTrue(attempt.success)
            self.assertEqual(attempt.pre_mutation_judge_result.verdict, "correct")
            self.assertIn("2k + 1", attempt.mutated_proof_text)
            self.assertEqual(attempt.judge_result.verdict, "correct")
            self.assertEqual(attempt.mutation_check_result.verdict, "incorrect")
            self.assertIn("Submitted proof:", llm.prompts[0])
            self.assertIn("Submitted proof:", llm.prompts[2])
            self.assertNotIn("Fuzzer kind:", llm.prompts[2])
            self.assertNotIn("Original proof:", llm.prompts[2])
            self.assertNotIn("Mutation instructions:", llm.prompts[2])
            self.assertIn("Original proof:", llm.prompts[3])
            self.assertIn("Mutation instructions:", llm.prompts[3])
            self.assertEqual(len(evolutionary.store.load_attempts(fuzzer_kind="natural_language")), 1)

    def test_generic_attempt_algorithmically_selects_false_proof_on_cold_start(self) -> None:
        proof = "Let n be even.\n\nThen n = 2k for some integer k.\n\nTherefore n^2 is even."
        llm = FakeLLM([JUDGE_CORRECT_RESPONSE, MUTATION_RESPONSE, JUDGE_CORRECT_RESPONSE])

        with tempfile.TemporaryDirectory() as tmp_dir:
            config = EvolutionConfig(
                storage_dir=tmp_dir,
                strategy_injection_probability=0.0,
                evolution_threshold=0,
                correctness_selection_mode="adaptive",
            )
            fuzzer = NaturalLanguageProofFuzzerLLMInterface(proof, llm)
            evolutionary = EvolutionaryProofFuzzer(fuzzer, config=config)

            attempt = evolutionary.run_mutation_attempt()

            self.assertFalse(attempt.maintain_correctness)
            self.assertFalse(attempt.metadata["correctness_selection"]["selected"])
            self.assertIn("maintain_correctness must be exactly false", llm.prompts[1])
            self.assertNotIn("Choose whether", llm.prompts[1])

    def test_success_requires_pre_mutation_proof_to_be_judged_correct(self) -> None:
        proof = "Let n be even.\n\nThen n = 2k for some integer k.\n\nTherefore n^2 is even."
        llm = FakeLLM([JUDGE_INCORRECT_RESPONSE, MUTATION_RESPONSE, JUDGE_CORRECT_RESPONSE])

        with tempfile.TemporaryDirectory() as tmp_dir:
            config = EvolutionConfig(
                storage_dir=tmp_dir,
                strategy_injection_probability=0.0,
                evolution_threshold=0,
                correctness_selection_mode="false_proof",
            )
            fuzzer = NaturalLanguageProofFuzzerLLMInterface(proof, llm)
            evolutionary = EvolutionaryProofFuzzer(fuzzer, config=config)

            attempt = evolutionary.run_mutation_attempt()

            self.assertEqual(attempt.pre_mutation_judge_result.verdict, "incorrect")
            self.assertEqual(attempt.judge_result.verdict, "correct")
            self.assertFalse(attempt.success)

    def test_fixed_probability_selects_false_or_preserving_from_seeded_sample(self) -> None:
        proof = "Let n be even.\n\nThen n = 2k for some integer k.\n\nTherefore n^2 is even."

        with tempfile.TemporaryDirectory() as tmp_dir:
            false_llm = FakeLLM([JUDGE_CORRECT_RESPONSE, MUTATION_RESPONSE, JUDGE_CORRECT_RESPONSE])
            false_config = EvolutionConfig(
                storage_dir=tmp_dir,
                strategy_injection_probability=0.0,
                evolution_threshold=0,
                correctness_selection_mode="fixed_probability",
                false_proof_probability=0.7,
                random_seed=1,
            )
            false_fuzzer = NaturalLanguageProofFuzzerLLMInterface(proof, false_llm)
            false_attempt = EvolutionaryProofFuzzer(false_fuzzer, config=false_config).run_mutation_attempt()

            true_llm = FakeLLM([JUDGE_CORRECT_RESPONSE, CORRECTNESS_PRESERVING_MUTATION_RESPONSE, JUDGE_INCORRECT_RESPONSE])
            true_config = EvolutionConfig(
                storage_dir=tmp_dir,
                strategy_injection_probability=0.0,
                evolution_threshold=0,
                correctness_selection_mode="fixed_probability",
                false_proof_probability=0.7,
                random_seed=2,
            )
            true_fuzzer = NaturalLanguageProofFuzzerLLMInterface(proof, true_llm)
            true_attempt = EvolutionaryProofFuzzer(true_fuzzer, config=true_config).run_mutation_attempt()

            self.assertFalse(false_attempt.maintain_correctness)
            self.assertTrue(true_attempt.maintain_correctness)
            self.assertEqual(false_attempt.metadata["correctness_selection"]["false_proof_probability"], 0.7)

    def test_generic_attempt_adaptive_selection_uses_success_history(self) -> None:
        proof = "Let n be even.\n\nThen n = 2k for some integer k.\n\nTherefore n^2 is even."
        llm = FakeLLM([JUDGE_CORRECT_RESPONSE, CORRECTNESS_PRESERVING_MUTATION_RESPONSE, JUDGE_INCORRECT_RESPONSE])
        false_instructions = parse_mutation_instructions(MUTATION_RESPONSE)
        true_instructions = parse_mutation_instructions(CORRECTNESS_PRESERVING_MUTATION_RESPONSE)

        with tempfile.TemporaryDirectory() as tmp_dir:
            store = ProofFuzzAttemptStore(tmp_dir)
            for index in range(3):
                store.append_attempt(
                    FuzzAttempt(
                        attempt_id=f"false_{index}",
                        fuzzer_kind="natural_language",
                        objective="false failed",
                        maintain_correctness=False,
                        original_proof_text=proof,
                        mutation_instructions=false_instructions,
                        judge_result=JudgeResult(verdict="incorrect"),
                        success=False,
                    )
                )
                store.append_attempt(
                    FuzzAttempt(
                        attempt_id=f"true_{index}",
                        fuzzer_kind="natural_language",
                        objective="true succeeded",
                        maintain_correctness=True,
                        original_proof_text=proof,
                        mutation_instructions=true_instructions,
                        judge_result=JudgeResult(verdict="incorrect"),
                        success=True,
                    )
                )

            config = EvolutionConfig(
                storage_dir=tmp_dir,
                strategy_injection_probability=0.0,
                evolution_threshold=0,
                correctness_selection_mode="adaptive",
                correctness_exploration_weight=0.0,
            )
            fuzzer = NaturalLanguageProofFuzzerLLMInterface(proof, llm)
            evolutionary = EvolutionaryProofFuzzer(fuzzer, store=store, config=config)

            attempt = evolutionary.run_mutation_attempt()

            self.assertTrue(attempt.maintain_correctness)
            self.assertTrue(attempt.metadata["correctness_selection"]["selected"])
            self.assertIn("maintain_correctness must be exactly true", llm.prompts[1])

    def test_strategy_injection_adds_guidance_to_future_prompt(self) -> None:
        proof = "Let n be even.\n\nThen n = 2k for some integer k.\n\nTherefore n^2 is even."
        llm = FakeLLM([JUDGE_CORRECT_RESPONSE, MUTATION_RESPONSE, JUDGE_CORRECT_RESPONSE])

        with tempfile.TemporaryDirectory() as tmp_dir:
            store = ProofFuzzAttemptStore(tmp_dir)
            store.save_strategies(
                "natural_language",
                [
                    FuzzStrategy(
                        strategy_id="strategy_1",
                        fuzzer_kind="natural_language",
                        title="Representation slip",
                        guidance="Mutate a representation before the final conclusion.",
                        target_correctness=False,
                    )
                ],
            )
            config = EvolutionConfig(
                storage_dir=tmp_dir,
                strategy_injection_probability=1.0,
                evolution_threshold=0,
                random_seed=1,
            )
            fuzzer = NaturalLanguageProofFuzzerLLMInterface(proof, llm)
            evolutionary = EvolutionaryProofFuzzer(fuzzer, store=store, config=config)

            attempt = evolutionary.run_false_proof_attempt()

            self.assertEqual(attempt.strategy_ids, ("strategy_1",))
            self.assertIn("Evolved strategy guidance", llm.prompts[1])
            self.assertIn("Representation slip", llm.prompts[1])

    def test_evolution_runs_after_threshold_and_saves_strategy_bank(self) -> None:
        proof = "Let n be even.\n\nThen n = 2k for some integer k.\n\nTherefore n^2 is even."
        llm = FakeLLM([JUDGE_CORRECT_RESPONSE, MUTATION_RESPONSE, JUDGE_CORRECT_RESPONSE, JUDGE_INCORRECT_RESPONSE, EVOLUTION_RESPONSE])

        with tempfile.TemporaryDirectory() as tmp_dir:
            config = EvolutionConfig(
                storage_dir=tmp_dir,
                strategy_injection_probability=0.0,
                evolution_threshold=1,
            )
            fuzzer = NaturalLanguageProofFuzzerLLMInterface(proof, llm)
            evolutionary = EvolutionaryProofFuzzer(fuzzer, config=config)

            evolutionary.run_false_proof_attempt()
            strategies = evolutionary.store.load_strategies("natural_language")

            self.assertEqual(len(strategies), 1)
            self.assertEqual(strategies[0].title, "Plausible representation slip")
            self.assertIn("Recent judged attempts", llm.prompts[4])
            self.assertEqual(evolutionary.store.last_evolved_attempt_count("natural_language"), 1)

    def test_truncated_completion_is_retried_before_parsing(self) -> None:
        proof = "Let n be even.\n\nThen n = 2k for some integer k.\n\nTherefore n^2 is even."
        llm = FinishReasonLLM(
            [JUDGE_CORRECT_RESPONSE, MUTATION_RESPONSE, MUTATION_RESPONSE, JUDGE_CORRECT_RESPONSE],
            ["stop", "length", "stop", "stop"],
        )

        with tempfile.TemporaryDirectory() as tmp_dir:
            config = EvolutionConfig(
                storage_dir=tmp_dir,
                strategy_injection_probability=0.0,
                evolution_threshold=0,
                correctness_selection_mode="false_proof",
                llm_retries=1,
            )
            fuzzer = NaturalLanguageProofFuzzerLLMInterface(proof, llm)
            attempt = EvolutionaryProofFuzzer(fuzzer, config=config).run_mutation_attempt()

            self.assertEqual(attempt.status, "success")
            self.assertEqual(len(llm.prompts), 6)

    def test_context_failure_shrinks_natural_language_prompt_and_retries(self) -> None:
        proof = "\n\n".join(f"Step {index}: this is a long proof paragraph." for index in range(80))
        llm = FakeLLM([JUDGE_CORRECT_RESPONSE, RuntimeError("context length exceeded"), MUTATION_RESPONSE, JUDGE_CORRECT_RESPONSE])

        with tempfile.TemporaryDirectory() as tmp_dir:
            config = EvolutionConfig(
                storage_dir=tmp_dir,
                strategy_injection_probability=0.0,
                evolution_threshold=0,
                correctness_selection_mode="false_proof",
                context_fallbacks=1,
            )
            fuzzer = NaturalLanguageProofFuzzerLLMInterface(proof, llm)
            attempt = EvolutionaryProofFuzzer(fuzzer, config=config).run_mutation_attempt()

            self.assertEqual(attempt.status, "success")
            self.assertLess(len(llm.prompts[2]), len(llm.prompts[1]))

    def test_failed_llm_attempt_is_recorded_when_continue_on_error_is_enabled(self) -> None:
        proof = "Let n be even.\n\nThen n = 2k for some integer k.\n\nTherefore n^2 is even."
        llm = FakeLLM([RuntimeError("context length exceeded")])

        with tempfile.TemporaryDirectory() as tmp_dir:
            config = EvolutionConfig(
                storage_dir=tmp_dir,
                strategy_injection_probability=0.0,
                evolution_threshold=0,
                correctness_selection_mode="false_proof",
                continue_on_error=True,
            )
            fuzzer = NaturalLanguageProofFuzzerLLMInterface(proof, llm)
            evolutionary = EvolutionaryProofFuzzer(fuzzer, config=config)

            attempt = evolutionary.run_mutation_attempt()
            stored = evolutionary.store.load_attempts(fuzzer_kind="natural_language")

            self.assertEqual(attempt.status, "failed")
            self.assertEqual(attempt.failure_stage, "pre_mutation_judge")
            self.assertEqual(stored[0].status, "failed")

    def test_parse_strategy_evolution_response_preserves_existing_ids(self) -> None:
        strategies = parse_strategy_evolution_response(
            """{
  "strategies": [
    {
      "strategy_id": "strategy_existing",
      "title": "Known move",
      "guidance": "Reuse a known mutation pattern.",
      "target_correctness": null,
      "successes": 2,
      "failures": 1,
      "provenance_attempt_ids": ["attempt_1"]
    }
  ]
}""",
            fuzzer_kind="semiformal",
        )

        self.assertEqual(strategies[0].strategy_id, "strategy_existing")
        self.assertIsNone(strategies[0].target_correctness)
        self.assertEqual(strategies[0].provenance_attempt_ids, ("attempt_1",))


if __name__ == "__main__":
    unittest.main()
