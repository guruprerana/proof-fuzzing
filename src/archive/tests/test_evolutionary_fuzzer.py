import json
import tempfile
import unittest
from pathlib import Path

from src.archive.proof_fuzzer import (
    BlindProofCorrectnessJudge,
    EvolutionConfig,
    EvolutionaryProofFuzzer,
    FuzzAttempt,
    FuzzStrategy,
    JudgeResult,
    load_mined_strategies,
    NaturalLanguageProofFuzzerLLMInterface,
    ProofFuzzAttemptStore,
    ProofFuzzJudge,
    fuzz_attempt_succeeded,
    parse_judge_error_detection_result,
    parse_judge_result,
    parse_mutation_instructions,
    parse_successful_mutation_novelty_result,
    parse_strategy_evolution_response,
)


def write_strategy_fixture(directory):
    """Synthetic seed bank; tests must not depend on local experiment data."""
    path = Path(directory) / "seed.jsonl"
    rows = [dict(
        strategy_id=f"mined_{topic}_fixture", fuzzer_kind="natural_language",
        title=f"{topic} fixture", guidance=f"Check a {topic} inference.",
        target_correctness=False, math_topic=topic,
        metadata={"source": "mined", "pinned": True, "topic": topic},
    ) for topic in ("algebra", "geometry")]
    path.write_text("\n".join(json.dumps(row) for row in rows))
    return path


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

DIFFERENT_MUTATION_RESPONSE = """{
  "maintain_correctness": false,
  "rationale": "Attack a different dependency with a missing case split.",
  "mutations": [
    {
      "kind": "modify",
      "target": "S3",
      "summary": "Remove the final parity justification by skipping an odd case.",
      "new_text": "Therefore the conclusion follows for all integers.",
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

NOVELTY_DUPLICATE_RESPONSE = """{
  "novelty": "duplicate",
  "matching_attempt_ids": ["attempt_prior"],
  "rationale": "The proposed mutation repeats the same even-to-odd representation slip.",
  "suggested_retry_guidance": "Avoid S2 and try a different proof dependency."
}"""

NOVELTY_NOVEL_RESPONSE = """{
  "novelty": "novel",
  "matching_attempt_ids": [],
  "rationale": "The proposed mutation targets a different step and mechanism.",
  "suggested_retry_guidance": ""
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

JUDGE_CORRECT_WITH_REVEALED_FLAW_RESPONSE = """{
  "verdict": "correct",
  "confidence": 0.55,
  "rationale": "Although the proof writes n = 2k + 1, it still seems to establish the parity claim.",
  "detected_flaw": "the proof changed an even number to an odd representation"
}"""

ERROR_INVENTORY_RESPONSE = """{
  "errors": [
    {
      "location": "second sentence",
      "description": "An even integer is represented as 2k + 1.",
      "consequence": "The parity argument starts from a false representation.",
      "confidence": 0.98
    },
    {
      "location": "final sentence",
      "description": "The conclusion is asserted without expanding the square.",
      "consequence": "The displayed reasoning does not explicitly establish the conclusion.",
      "confidence": 0.4
    }
  ],
  "review_summary": "Checked each parity inference and the conclusion."
}"""

EMPTY_ERROR_INVENTORY_RESPONSE = """{
  "errors": [],
  "review_summary": "Checked the complete trace and found no concrete error."
}"""

JUDGE_ERROR_NOT_REPORTED_RESPONSE = """{
  "introduced_error_found": false,
  "matching_report_indices": [],
  "matching_error_indices": [],
  "match_level": "none",
  "rationale": "The judge reports do not identify the parity representation mutation."
}"""

JUDGE_ERROR_REPORTED_RESPONSE = """{
  "introduced_error_found": true,
  "matching_report_indices": [1],
  "matching_error_indices": [{"report_index": 1, "error_index": 0}],
  "match_level": "exact",
  "rationale": "Judge 1 explicitly identifies the even-to-odd representation mutation."
}"""


class EvolutionaryFuzzerTest(unittest.TestCase):
    def test_target_judge_prompt_requests_error_inventory_without_verdict(self) -> None:
        prompt = BlindProofCorrectnessJudge(FakeLLM([])).judge_prompt(
            problem_text="Prove that n^2 is even.",
            proof_text="Let n = 2k. Then n^2 = 4k^2.",
            fuzzer_kind="natural_language",
        )

        self.assertIn("reviewing a mathematical reasoning trace for errors", prompt)
        self.assertIn("ERROR-FINDING TASK:", prompt)
        self.assertIn("PROBLEM:", prompt)
        self.assertIn("REASONING TRACE TO REVIEW:", prompt)
        self.assertIn('"errors": [', prompt)
        self.assertIn("do not return a binary correct/incorrect verdict", prompt)
        self.assertIn("every concrete mathematical or logical error", prompt)
        self.assertIn("even when the final conclusion is true", prompt)
        self.assertIn("another argument establishes it", prompt)
        self.assertIn("explicitly retracted claims", prompt)
        self.assertIn("If you find no concrete error, return an empty list", prompt)
        self.assertIn('"severity": "minor | major | critical"', prompt)
        self.assertNotIn("materially weakens", prompt)
        self.assertNotIn("required inference", prompt)
        self.assertIn("Group multiple downstream symptoms", prompt)
        self.assertIn("style concerns", prompt)
        self.assertNotIn('"verdict":', prompt)
        self.assertNotIn("Score:", prompt)
        self.assertNotIn("Fuzzer kind:", prompt)
        self.assertNotIn("Submitted proof:", prompt)

    def test_parse_error_inventory_preserves_every_reported_error(self) -> None:
        result = parse_judge_result(ERROR_INVENTORY_RESPONSE)

        self.assertEqual(result.response_kind, "error_inventory")
        self.assertEqual(len(result.detected_errors), 2)
        self.assertEqual(result.detected_errors[0]["location"], "second sentence")
        self.assertEqual(result.confidence, 0.98)

        empty = parse_judge_result(EMPTY_ERROR_INVENTORY_RESPONSE)
        self.assertEqual(empty.response_kind, "error_inventory")
        self.assertEqual(empty.detected_errors, ())

    def test_parse_plaintext_error_inventory(self) -> None:
        result = parse_judge_result(
            "- **Lemma 9.1:** The claimed degrees collide.\n"
            "- **Theorem 1.2:** The lower bound therefore does not follow."
        )
        self.assertEqual(result.response_kind, "error_inventory")
        self.assertEqual(result.verdict, "incorrect")
        self.assertEqual(len(result.detected_errors), 2)

        empty = parse_judge_result("No concrete mathematical errors found.")
        self.assertEqual(empty.verdict, "correct")
        self.assertEqual(empty.detected_errors, ())

    def test_mutation_checker_prompt_requires_independent_proof_audit(self) -> None:
        instructions = parse_mutation_instructions(MUTATION_RESPONSE)
        prompt = ProofFuzzJudge(FakeLLM([])).judge_prompt(
            original_proof_text="Original proof proves the theorem.",
            mutation_instructions=instructions,
            mutated_proof_text="Mutated proof still has an alternate valid argument.",
            fuzzer_kind="natural_language",
        )

        self.assertIn("mathematical proof auditor", prompt)
        self.assertIn("Problem:", prompt)
        self.assertIn("Reference original proof:", prompt)
        self.assertIn("Mutation record:", prompt)
        self.assertIn("Submitted mutated proof:", prompt)
        self.assertIn("untrusted context", prompt)
        self.assertIn("Do not treat the mutation record as evidence", prompt)
        self.assertIn("valid route to the conclusion", prompt)
        self.assertIn("omitted case is impossible", prompt)
        self.assertIn("proves only a congruence/residue/average", prompt)
        self.assertIn("distance, parallelism, radical-axis", prompt)
        self.assertIn("recurrence, induction, periodicity, or case split", prompt)
        self.assertIn("truncated for context", prompt)
        self.assertIn("do not infer what the omitted portion says", prompt)
        self.assertIn("not mark a proof incorrect merely because the mutation record claims a flaw", prompt)
        self.assertIn("one\n  independent root-cause error", prompt)
        self.assertIn("minimally exposed", prompt)
        self.assertNotIn("Fuzzer kind:", prompt)
        self.assertNotIn("Fuzz this", prompt)

    def test_false_proof_generation_prompt_requires_actual_incorrectness(self) -> None:
        proof = "Let n be even.\n\nThen n = 2k for some integer k.\n\nTherefore n^2 is even."
        fuzzer = NaturalLanguageProofFuzzerLLMInterface(proof, FakeLLM([]))

        prompt = fuzzer.false_proof_mutation_instruction_prompt(
            objective="fool the judge",
        )

        self.assertIn("must become mathematically incorrect as written", prompt)
        self.assertIn("not enough to introduce awkward wording", prompt)
        self.assertIn("first indispensable proof step", prompt)
        self.assertIn("no alternate route in the mutated proof", prompt)
        self.assertIn("choose a different mutation", prompt)

    def test_parse_judge_result_and_success_rules(self) -> None:
        result = parse_judge_result(JUDGE_CORRECT_RESPONSE)

        self.assertEqual(result.verdict, "correct")
        self.assertTrue(
            fuzz_attempt_succeeded(
                False,
                result,
                mutation_check_result=JudgeResult(verdict="incorrect"),
            )
        )
        self.assertFalse(
            fuzz_attempt_succeeded(
                False,
                result,
                mutation_check_result=JudgeResult(verdict="correct"),
            )
        )
        self.assertFalse(fuzz_attempt_succeeded(True, result))
        self.assertTrue(
            fuzz_attempt_succeeded(
                True,
                JudgeResult(verdict="uncertain"),
                mutation_check_result=JudgeResult(verdict="correct"),
            )
        )
        self.assertFalse(
            fuzz_attempt_succeeded(
                False,
                result,
                judge_error_detection_result={"any_judge_reported_correct_error": True},
                mutation_check_result=JudgeResult(verdict="incorrect"),
            )
        )
        self.assertFalse(
            fuzz_attempt_succeeded(
                False,
                result,
                target_judge_results=(result, JudgeResult(verdict="incorrect")),
                target_judge_success_policy="all",
                mutation_check_result=JudgeResult(verdict="incorrect"),
            )
        )
        self.assertTrue(
            fuzz_attempt_succeeded(
                False,
                result,
                target_judge_results=(result, JudgeResult(verdict="incorrect")),
                target_judge_success_policy="any",
                mutation_check_result=JudgeResult(verdict="incorrect"),
            )
        )

    def test_parse_judge_error_detection_result(self) -> None:
        result = parse_judge_error_detection_result(JUDGE_ERROR_REPORTED_RESPONSE)

        self.assertTrue(result["any_judge_reported_correct_error"])
        self.assertTrue(result["introduced_error_found"])
        self.assertEqual(result["matching_judge_indices"], [1])
        self.assertEqual(result["matching_report_indices"], [1])
        self.assertEqual(
            result["matching_error_indices"],
            [{"report_index": 1, "error_index": 0}],
        )
        self.assertEqual(result["match_level"], "exact")
        self.assertEqual(result["matcher_policy"], "exact_only")

    def test_partial_match_is_normalized_to_a_miss(self) -> None:
        result = parse_judge_error_detection_result(
            """{
  "introduced_error_found": true,
  "matching_report_indices": [0],
  "matching_error_indices": [{"report_index": 0, "error_index": 0}],
  "match_level": "partial",
  "rationale": "The report only makes a generic downstream complaint."
}"""
        )

        self.assertFalse(result["introduced_error_found"])
        self.assertTrue(result["reported_introduced_error_found"])
        self.assertEqual(result["matcher_policy"], "exact_only")

    def test_matcher_is_authoritative_for_false_proof_success(self) -> None:
        inventory = parse_judge_result(ERROR_INVENTORY_RESPONSE)

        self.assertTrue(
            fuzz_attempt_succeeded(
                False,
                inventory,
                judge_error_detection_result={"introduced_error_found": False},
                mutation_check_result=JudgeResult(verdict="incorrect"),
            )
        )
        self.assertFalse(
            fuzz_attempt_succeeded(
                False,
                inventory,
                judge_error_detection_result={"introduced_error_found": True},
                mutation_check_result=JudgeResult(verdict="incorrect"),
            )
        )

    def test_parse_successful_mutation_novelty_result(self) -> None:
        result = parse_successful_mutation_novelty_result(NOVELTY_DUPLICATE_RESPONSE)

        self.assertEqual(result["novelty"], "duplicate")
        self.assertEqual(result["matching_attempt_ids"], ["attempt_prior"])
        self.assertIn("Avoid S2", result["suggested_retry_guidance"])

    def test_parse_judge_result_repairs_raw_latex_json_escapes(self) -> None:
        result = parse_judge_result(
            r"""{
  "verdict": "incorrect",
  "confidence": 0.8,
  "rationale": "The step using \frac{x}{y} and \theta is invalid.",
  "detected_flaw": "Wrong inference from \(s n\equiv 1\)."
}"""
        )

        self.assertEqual(result.verdict, "incorrect")
        self.assertIn(r"\frac{x}{y}", result.rationale)
        self.assertIn(r"\theta", result.rationale)
        self.assertIn(r"\(", result.detected_flaw)

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
        llm = FakeLLM([JUDGE_CORRECT_RESPONSE, MUTATION_RESPONSE, JUDGE_INCORRECT_RESPONSE, JUDGE_CORRECT_RESPONSE])

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
            self.assertIn("REASONING TRACE TO REVIEW:", llm.prompts[0])
            self.assertIn("Reference original proof:", llm.prompts[2])
            self.assertIn("Mutation record:", llm.prompts[2])
            self.assertIn("REASONING TRACE TO REVIEW:", llm.prompts[3])
            self.assertNotIn("Fuzzer kind:", llm.prompts[3])
            self.assertNotIn("Original proof:", llm.prompts[3])
            self.assertNotIn("Mutation instructions:", llm.prompts[3])
            self.assertEqual(len(evolutionary.store.load_attempts(fuzzer_kind="natural_language")), 1)

    def test_evolutionary_fuzzer_can_skip_pre_mutation_judge(self) -> None:
        proof = "Let n be even.\n\nThen n = 2k for some integer k.\n\nTherefore n^2 is even."
        llm = FakeLLM([MUTATION_RESPONSE, JUDGE_INCORRECT_RESPONSE, JUDGE_CORRECT_RESPONSE])

        with tempfile.TemporaryDirectory() as tmp_dir:
            config = EvolutionConfig(
                storage_dir=tmp_dir,
                strategy_injection_probability=0.0,
                evolution_threshold=0,
                run_pre_mutation_judge=False,
            )
            fuzzer = NaturalLanguageProofFuzzerLLMInterface(proof, llm)
            evolutionary = EvolutionaryProofFuzzer(fuzzer, config=config)

            attempt = evolutionary.run_false_proof_attempt(objective="fool the judge")

            self.assertTrue(attempt.success)
            self.assertIsNone(attempt.pre_mutation_judge_result)
            self.assertTrue(attempt.metadata["pre_mutation_judge_skipped"])
            self.assertIn("Targetable proof segments:", llm.prompts[0])
            self.assertIn("Mutation record:", llm.prompts[1])
            self.assertIn("REASONING TRACE TO REVIEW:", llm.prompts[2])

    def test_false_proof_attempt_skips_target_judge_when_mutation_checker_says_correct(self) -> None:
        proof = "Let n be even.\n\nThen n = 2k for some integer k.\n\nTherefore n^2 is even."
        llm = FakeLLM([JUDGE_CORRECT_RESPONSE, MUTATION_RESPONSE, JUDGE_CORRECT_RESPONSE])

        with tempfile.TemporaryDirectory() as tmp_dir:
            config = EvolutionConfig(
                storage_dir=tmp_dir,
                strategy_injection_probability=0.0,
                evolution_threshold=0,
            )
            fuzzer = NaturalLanguageProofFuzzerLLMInterface(proof, llm)
            evolutionary = EvolutionaryProofFuzzer(fuzzer, config=config)

            attempt = evolutionary.run_false_proof_attempt(objective="fool the judge")

            self.assertFalse(attempt.success)
            self.assertEqual(attempt.mutation_check_result.verdict, "correct")
            self.assertTrue(attempt.metadata["target_judge_skipped"])
            self.assertEqual(attempt.metadata["target_judge_results"], [])
            self.assertEqual(attempt.judge_result.verdict, "uncertain")
            self.assertEqual(len(llm.prompts), 3)

    def test_multiple_target_judges_and_reveal_check_can_accept_attempt(self) -> None:
        proof = "Let n be even.\n\nThen n = 2k for some integer k.\n\nTherefore n^2 is even."
        llm = FakeLLM(
            [
                JUDGE_CORRECT_RESPONSE,
                MUTATION_RESPONSE,
                JUDGE_INCORRECT_RESPONSE,
                JUDGE_CORRECT_RESPONSE,
                JUDGE_CORRECT_RESPONSE,
                JUDGE_CORRECT_RESPONSE,
                JUDGE_ERROR_NOT_REPORTED_RESPONSE,
            ]
        )

        with tempfile.TemporaryDirectory() as tmp_dir:
            config = EvolutionConfig(
                storage_dir=tmp_dir,
                strategy_injection_probability=0.0,
                evolution_threshold=0,
                target_judge_samples=3,
                target_judge_success_policy="all",
                judge_error_detection_check=True,
            )
            fuzzer = NaturalLanguageProofFuzzerLLMInterface(proof, llm)
            evolutionary = EvolutionaryProofFuzzer(fuzzer, config=config)

            attempt = evolutionary.run_false_proof_attempt(objective="fool the judge")

            self.assertTrue(attempt.success)
            self.assertEqual(len(attempt.metadata["target_judge_results"]), 3)
            self.assertFalse(attempt.metadata["judge_error_detection_check"]["any_judge_reported_correct_error"])
            self.assertIn("Blind error-finder reports:", llm.prompts[6])
            trace_dir = attempt.metadata["trace_dir"]
            self.assertTrue((Path(trace_dir) / "target_judge_results.json").is_file())
            self.assertTrue((Path(trace_dir) / "judge_error_detection_check.json").is_file())

    def test_error_inventory_automatically_runs_separate_matcher(self) -> None:
        proof = "Let n be even.\n\nThen n = 2k for some integer k.\n\nTherefore n^2 is even."
        llm = FakeLLM(
            [
                MUTATION_RESPONSE,
                JUDGE_INCORRECT_RESPONSE,
                ERROR_INVENTORY_RESPONSE,
                JUDGE_ERROR_NOT_REPORTED_RESPONSE,
            ]
        )

        with tempfile.TemporaryDirectory() as tmp_dir:
            config = EvolutionConfig(
                storage_dir=tmp_dir,
                strategy_injection_probability=0.0,
                evolution_threshold=0,
                run_pre_mutation_judge=False,
                judge_error_detection_check=False,
            )
            fuzzer = NaturalLanguageProofFuzzerLLMInterface(proof, llm)
            attempt = EvolutionaryProofFuzzer(fuzzer, config=config).run_false_proof_attempt(
                objective="fool the error finder"
            )

            self.assertTrue(attempt.success)
            self.assertEqual(len(llm.prompts), 4)
            self.assertIn("REASONING TRACE TO REVIEW:", llm.prompts[2])
            self.assertIn("Blind error-finder reports:", llm.prompts[3])
            self.assertIn("detected_errors", llm.prompts[3])
            self.assertFalse(
                attempt.metadata["judge_error_detection_check"]["introduced_error_found"]
            )

    def test_original_artifact_control_is_passed_to_exact_matcher(self) -> None:
        proof = "Let n be even.\n\nThen n = 2k for some integer k.\n\nTherefore n^2 is even."
        llm = FakeLLM(
            [
                MUTATION_RESPONSE,
                JUDGE_INCORRECT_RESPONSE,
                EMPTY_ERROR_INVENTORY_RESPONSE,
                ERROR_INVENTORY_RESPONSE,
                JUDGE_ERROR_REPORTED_RESPONSE,
            ]
        )

        with tempfile.TemporaryDirectory() as tmp_dir:
            config = EvolutionConfig(
                storage_dir=tmp_dir,
                strategy_injection_probability=0.0,
                evolution_threshold=0,
                run_pre_mutation_judge=False,
                run_original_error_control=True,
            )
            fuzzer = NaturalLanguageProofFuzzerLLMInterface(proof, llm)
            attempt = EvolutionaryProofFuzzer(fuzzer, config=config).run_false_proof_attempt(
                objective="fool the error finder"
            )

            self.assertFalse(attempt.success)
            self.assertEqual(len(llm.prompts), 5)
            self.assertIn("REASONING TRACE TO REVIEW:", llm.prompts[2])
            self.assertIn(proof, llm.prompts[2])
            self.assertIn("Control error-finder reports", llm.prompts[4])
            self.assertEqual(len(attempt.metadata["original_error_control_reports"]), 1)
            trace_dir = Path(attempt.metadata["trace_dir"])
            self.assertTrue((trace_dir / "original_error_control_reports.json").is_file())

    def test_mutation_prompt_includes_previous_failed_attempts_on_same_proof(self) -> None:
        proof = "Let n be even.\n\nThen n = 2k for some integer k.\n\nTherefore n^2 is even."
        llm = FakeLLM(
            [
                JUDGE_CORRECT_RESPONSE,
                MUTATION_RESPONSE,
                JUDGE_INCORRECT_RESPONSE,
                JUDGE_INCORRECT_RESPONSE,
                JUDGE_CORRECT_RESPONSE,
                MUTATION_RESPONSE,
                JUDGE_INCORRECT_RESPONSE,
                JUDGE_CORRECT_RESPONSE,
            ]
        )

        with tempfile.TemporaryDirectory() as tmp_dir:
            config = EvolutionConfig(
                storage_dir=tmp_dir,
                strategy_injection_probability=0.0,
                evolution_threshold=0,
            )
            fuzzer = NaturalLanguageProofFuzzerLLMInterface(proof, llm)
            evolutionary = EvolutionaryProofFuzzer(fuzzer, config=config)

            first_attempt = evolutionary.run_false_proof_attempt(
                objective="fool the judge",
                metadata={"dataset": "unit", "example_id": "same-proof"},
            )
            second_attempt = evolutionary.run_false_proof_attempt(
                objective="fool the judge",
                metadata={"dataset": "unit", "example_id": "same-proof"},
            )

            self.assertFalse(first_attempt.success)
            self.assertTrue(second_attempt.success)
            self.assertEqual(second_attempt.metadata["previous_failed_attempts_in_prompt"], [first_attempt.attempt_id])
            self.assertEqual(second_attempt.metadata["proof_identity"], "unit:example_id:same-proof")
            self.assertIn("Previous attempts on this same proof:", llm.prompts[5])
            self.assertIn("target judge verdicts: incorrect", llm.prompts[5])
            self.assertIn("Switch even to odd representation", llm.prompts[5])

    def test_mutation_prompt_includes_previous_successful_attempts_on_same_proof(self) -> None:
        proof = "Let n be even.\n\nThen n = 2k for some integer k.\n\nTherefore n^2 is even."
        llm = FakeLLM(
            [
                JUDGE_CORRECT_RESPONSE,
                MUTATION_RESPONSE,
                JUDGE_INCORRECT_RESPONSE,
                JUDGE_CORRECT_RESPONSE,
                JUDGE_CORRECT_RESPONSE,
                DIFFERENT_MUTATION_RESPONSE,
                JUDGE_INCORRECT_RESPONSE,
                JUDGE_CORRECT_RESPONSE,
            ]
        )

        with tempfile.TemporaryDirectory() as tmp_dir:
            config = EvolutionConfig(
                storage_dir=tmp_dir,
                strategy_injection_probability=0.0,
                evolution_threshold=0,
                max_previous_successful_attempts_in_prompt=2,
            )
            fuzzer = NaturalLanguageProofFuzzerLLMInterface(proof, llm)
            evolutionary = EvolutionaryProofFuzzer(fuzzer, config=config)

            first_attempt = evolutionary.run_false_proof_attempt(
                objective="fool the judge",
                metadata={"dataset": "unit", "example_id": "same-proof"},
            )
            second_attempt = evolutionary.run_false_proof_attempt(
                objective="fool the judge",
                metadata={"dataset": "unit", "example_id": "same-proof"},
            )

            self.assertTrue(first_attempt.success)
            self.assertTrue(second_attempt.success)
            self.assertEqual(second_attempt.metadata["previous_successful_attempts_in_prompt"], [first_attempt.attempt_id])
            self.assertIn("Previous attempts on this same proof:", llm.prompts[5])
            self.assertIn("AVOID repeating successful attempt", llm.prompts[5])
            self.assertIn("Switch even to odd representation", llm.prompts[5])
            self.assertIn("different proof step", llm.prompts[5])

    def test_duplicate_successful_mutation_gate_retries_before_judging(self) -> None:
        proof = "Let n be even.\n\nThen n = 2k for some integer k.\n\nTherefore n^2 is even."
        llm = FakeLLM(
            [
                JUDGE_CORRECT_RESPONSE,
                MUTATION_RESPONSE,
                JUDGE_INCORRECT_RESPONSE,
                JUDGE_CORRECT_RESPONSE,
                JUDGE_CORRECT_RESPONSE,
                MUTATION_RESPONSE,
                NOVELTY_DUPLICATE_RESPONSE,
                DIFFERENT_MUTATION_RESPONSE,
                NOVELTY_NOVEL_RESPONSE,
                JUDGE_INCORRECT_RESPONSE,
                JUDGE_CORRECT_RESPONSE,
            ]
        )

        with tempfile.TemporaryDirectory() as tmp_dir:
            config = EvolutionConfig(
                storage_dir=tmp_dir,
                strategy_injection_probability=0.0,
                evolution_threshold=0,
                reject_duplicate_successful_mutations=True,
                duplicate_successful_mutation_retries=1,
            )
            fuzzer = NaturalLanguageProofFuzzerLLMInterface(proof, llm)
            evolutionary = EvolutionaryProofFuzzer(fuzzer, config=config)

            first_attempt = evolutionary.run_false_proof_attempt(
                objective="fool the judge",
                metadata={"dataset": "unit", "example_id": "same-proof"},
            )
            second_attempt = evolutionary.run_false_proof_attempt(
                objective="fool the judge",
                metadata={"dataset": "unit", "example_id": "same-proof"},
            )

            self.assertTrue(first_attempt.success)
            self.assertTrue(second_attempt.success)
            self.assertEqual(second_attempt.mutation_instructions.mutations[0].target, "S3")
            novelty_checks = second_attempt.metadata["successful_mutation_novelty_checks"]
            self.assertEqual([check["novelty"] for check in novelty_checks], ["duplicate", "novel"])
            self.assertIn("checking novelty for a proof-fuzzing mutation", llm.prompts[6])
            self.assertIn("rejected as too similar", llm.prompts[7])

    def test_reveal_check_rejects_attempt_when_judge_report_identifies_mutation(self) -> None:
        proof = "Let n be even.\n\nThen n = 2k for some integer k.\n\nTherefore n^2 is even."
        llm = FakeLLM(
            [
                JUDGE_CORRECT_RESPONSE,
                MUTATION_RESPONSE,
                JUDGE_INCORRECT_RESPONSE,
                JUDGE_CORRECT_RESPONSE,
                JUDGE_CORRECT_WITH_REVEALED_FLAW_RESPONSE,
                JUDGE_ERROR_REPORTED_RESPONSE,
            ]
        )

        with tempfile.TemporaryDirectory() as tmp_dir:
            config = EvolutionConfig(
                storage_dir=tmp_dir,
                strategy_injection_probability=0.0,
                evolution_threshold=0,
                target_judge_samples=2,
                target_judge_success_policy="all",
                judge_error_detection_check=True,
            )
            fuzzer = NaturalLanguageProofFuzzerLLMInterface(proof, llm)
            evolutionary = EvolutionaryProofFuzzer(fuzzer, config=config)

            attempt = evolutionary.run_false_proof_attempt(objective="fool the judge")

            self.assertFalse(attempt.success)
            self.assertTrue(attempt.metadata["judge_error_detection_check"]["any_judge_reported_correct_error"])
            self.assertEqual(attempt.metadata["judge_error_detection_check"]["matching_judge_indices"], [1])

    def test_generic_attempt_algorithmically_selects_false_proof_on_cold_start(self) -> None:
        proof = "Let n be even.\n\nThen n = 2k for some integer k.\n\nTherefore n^2 is even."
        llm = FakeLLM([JUDGE_CORRECT_RESPONSE, MUTATION_RESPONSE, JUDGE_INCORRECT_RESPONSE, JUDGE_CORRECT_RESPONSE])

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
        llm = FakeLLM([JUDGE_INCORRECT_RESPONSE, MUTATION_RESPONSE, JUDGE_INCORRECT_RESPONSE, JUDGE_CORRECT_RESPONSE])

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
            false_llm = FakeLLM([JUDGE_CORRECT_RESPONSE, MUTATION_RESPONSE, JUDGE_INCORRECT_RESPONSE, JUDGE_CORRECT_RESPONSE])
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

            true_llm = FakeLLM([JUDGE_CORRECT_RESPONSE, CORRECTNESS_PRESERVING_MUTATION_RESPONSE, JUDGE_CORRECT_RESPONSE, JUDGE_INCORRECT_RESPONSE])
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
        llm = FakeLLM([JUDGE_CORRECT_RESPONSE, CORRECTNESS_PRESERVING_MUTATION_RESPONSE, JUDGE_CORRECT_RESPONSE, JUDGE_INCORRECT_RESPONSE])
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
        llm = FakeLLM([JUDGE_CORRECT_RESPONSE, MUTATION_RESPONSE, JUDGE_INCORRECT_RESPONSE, JUDGE_CORRECT_RESPONSE])

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
            self.assertIn("Strategy guidance", llm.prompts[1])
            self.assertIn("Representation slip", llm.prompts[1])

    def test_mined_strategy_seeding_is_idempotent(self) -> None:
        proof = "A proof about polynomial identities."

        with tempfile.TemporaryDirectory() as tmp_dir:
            config = EvolutionConfig(
                storage_dir=tmp_dir,
                seed_mined_strategies=True,
                mined_strategy_path=str(write_strategy_fixture(tmp_dir)),
                evolution_threshold=0,
            )

            EvolutionaryProofFuzzer(NaturalLanguageProofFuzzerLLMInterface(proof, FakeLLM([])), config=config)
            EvolutionaryProofFuzzer(NaturalLanguageProofFuzzerLLMInterface(proof, FakeLLM([])), config=config)

            store = ProofFuzzAttemptStore(tmp_dir)
            strategies = store.load_strategies("natural_language")
            strategy_ids = [strategy.strategy_id for strategy in strategies]

            self.assertEqual(len(strategies), 2)
            self.assertEqual(len(strategy_ids), len(set(strategy_ids)))
            self.assertTrue(all(strategy.metadata.get("source") == "mined" for strategy in strategies))
            self.assertTrue(all(strategy.metadata.get("pinned") for strategy in strategies))
            self.assertTrue(all(strategy.math_topic for strategy in strategies))

    def test_retrieval_selects_topic_relevant_strategy_from_common_bank(self) -> None:
        proof = "We prove two triangles are similar, then use cyclic angle chasing in the circle."
        llm = FakeLLM([JUDGE_CORRECT_RESPONSE, MUTATION_RESPONSE, JUDGE_INCORRECT_RESPONSE, JUDGE_CORRECT_RESPONSE])

        with tempfile.TemporaryDirectory() as tmp_dir:
            store = ProofFuzzAttemptStore(tmp_dir)
            store.save_strategies("natural_language", load_mined_strategies(write_strategy_fixture(tmp_dir)))
            config = EvolutionConfig(
                storage_dir=tmp_dir,
                strategy_injection_probability=1.0,
                strategy_selection_mode="retrieval",
                max_strategies_injected=1,
                evolution_threshold=0,
                random_seed=1,
            )
            fuzzer = NaturalLanguageProofFuzzerLLMInterface(proof, llm)
            evolutionary = EvolutionaryProofFuzzer(fuzzer, store=store, config=config)

            attempt = evolutionary.run_false_proof_attempt(metadata={"llm_category": "Geometry"})

            self.assertEqual(len(attempt.strategy_ids), 1)
            self.assertTrue(attempt.strategy_ids[0].startswith("mined_geometry_"))
            self.assertIn("Strategy guidance", llm.prompts[1])
            self.assertIn("geometry", attempt.metadata["strategy_selection"]["selected_strategy_topics"])

    def test_retrieval_uses_mined_and_evolved_strategies_from_common_bank(self) -> None:
        proof = "Compare polynomial coefficients after expanding an identity."
        llm = FakeLLM([JUDGE_CORRECT_RESPONSE, MUTATION_RESPONSE, JUDGE_INCORRECT_RESPONSE, JUDGE_CORRECT_RESPONSE])

        with tempfile.TemporaryDirectory() as tmp_dir:
            store = ProofFuzzAttemptStore(tmp_dir)
            store.save_strategies(
                "natural_language",
                [
                    FuzzStrategy(
                        strategy_id="mined_test_algebra",
                        fuzzer_kind="natural_language",
                        title="Mined coefficient mistake",
                        guidance="Miscompare polynomial coefficients in a plausible identity.",
                        target_correctness=False,
                        metadata={
                            "source": "mined",
                            "topic": "algebra",
                            "keywords": ["polynomial", "coefficient", "identity"],
                            "pinned": True,
                        },
                    ),
                    FuzzStrategy(
                        strategy_id="evolved_test_algebra",
                        fuzzer_kind="natural_language",
                        title="Learned algebra slip",
                        guidance="Use a coefficient comparison that nearly matches the target identity.",
                        target_correctness=False,
                        successes=3,
                        metadata={
                            "source": "evolved",
                            "topic": "algebra",
                            "keywords": ["polynomial", "coefficient"],
                        },
                    ),
                ],
            )
            config = EvolutionConfig(
                storage_dir=tmp_dir,
                strategy_injection_probability=1.0,
                strategy_selection_mode="retrieval",
                max_strategies_injected=2,
                evolution_threshold=0,
                random_seed=1,
            )
            fuzzer = NaturalLanguageProofFuzzerLLMInterface(proof, llm)
            evolutionary = EvolutionaryProofFuzzer(fuzzer, store=store, config=config)

            attempt = evolutionary.run_false_proof_attempt(metadata={"llm_category": "Algebra"})

            self.assertEqual(set(attempt.strategy_ids), {"mined_test_algebra", "evolved_test_algebra"})
            self.assertEqual(
                set(attempt.metadata["strategy_selection"]["selected_strategy_sources"]),
                {"mined", "evolved"},
            )

    def test_random_strategy_selection_only_uses_matching_math_topic(self) -> None:
        proof = "Compare polynomial coefficients in an algebraic identity."
        llm = FakeLLM([JUDGE_CORRECT_RESPONSE, MUTATION_RESPONSE, JUDGE_INCORRECT_RESPONSE, JUDGE_CORRECT_RESPONSE])

        with tempfile.TemporaryDirectory() as tmp_dir:
            store = ProofFuzzAttemptStore(tmp_dir)
            store.save_strategies(
                "natural_language",
                [
                    FuzzStrategy(
                        strategy_id="algebra_strategy",
                        fuzzer_kind="natural_language",
                        title="Algebra strategy",
                        guidance="Mutate a coefficient comparison.",
                        math_topic="algebra",
                        target_correctness=False,
                    ),
                    FuzzStrategy(
                        strategy_id="geometry_strategy",
                        fuzzer_kind="natural_language",
                        title="Geometry strategy",
                        guidance="Mutate an angle chase.",
                        math_topic="geometry",
                        target_correctness=False,
                    ),
                    FuzzStrategy(
                        strategy_id="untagged_strategy",
                        fuzzer_kind="natural_language",
                        title="Untagged strategy",
                        guidance="This legacy strategy has no topic.",
                        target_correctness=False,
                    ),
                ],
            )
            config = EvolutionConfig(
                storage_dir=tmp_dir,
                strategy_injection_probability=1.0,
                strategy_selection_mode="random",
                max_strategies_injected=3,
                evolution_threshold=0,
                random_seed=1,
            )
            fuzzer = NaturalLanguageProofFuzzerLLMInterface(proof, llm)
            evolutionary = EvolutionaryProofFuzzer(fuzzer, store=store, config=config)

            attempt = evolutionary.run_false_proof_attempt(metadata={"llm_category": "Algebra"})

            self.assertEqual(attempt.strategy_ids, ("algebra_strategy",))
            self.assertEqual(attempt.metadata["strategy_selection"]["selected_strategy_topics"], ["algebra"])

    def test_evolution_runs_after_threshold_and_saves_strategy_bank(self) -> None:
        proof = "Let n be even.\n\nThen n = 2k for some integer k.\n\nTherefore n^2 is even."
        llm = FakeLLM([JUDGE_CORRECT_RESPONSE, MUTATION_RESPONSE, JUDGE_INCORRECT_RESPONSE, JUDGE_CORRECT_RESPONSE, EVOLUTION_RESPONSE])

        with tempfile.TemporaryDirectory() as tmp_dir:
            config = EvolutionConfig(
                storage_dir=tmp_dir,
                strategy_injection_probability=0.0,
                evolution_threshold=1,
            )
            fuzzer = NaturalLanguageProofFuzzerLLMInterface(proof, llm)
            evolutionary = EvolutionaryProofFuzzer(fuzzer, config=config)

            evolutionary.run_false_proof_attempt(metadata={"llm_category": "Algebra"})
            strategies = evolutionary.store.load_strategies("natural_language")

            self.assertEqual(len(strategies), 1)
            self.assertEqual(strategies[0].title, "Plausible representation slip")
            self.assertEqual(strategies[0].math_topic, "algebra")
            self.assertIn("Recent judged attempts", llm.prompts[4])
            self.assertEqual(evolutionary.store.last_evolved_attempt_count_for_topic("natural_language", "algebra"), 1)

    def test_pinned_mined_strategies_survive_evolution_replacement(self) -> None:
        proof = "Let n be even.\n\nThen n = 2k for some integer k.\n\nTherefore n^2 is even."
        llm = FakeLLM([JUDGE_CORRECT_RESPONSE, MUTATION_RESPONSE, JUDGE_INCORRECT_RESPONSE, JUDGE_CORRECT_RESPONSE, EVOLUTION_RESPONSE])

        pinned_strategy = FuzzStrategy(
            strategy_id="mined_test_pinned",
            fuzzer_kind="natural_language",
            title="Pinned mined strategy",
            guidance="Keep this mined prior in the bank.",
            target_correctness=False,
            metadata={"source": "mined", "topic": "algebra", "pinned": True},
        )

        with tempfile.TemporaryDirectory() as tmp_dir:
            store = ProofFuzzAttemptStore(tmp_dir)
            store.save_strategies("natural_language", [pinned_strategy])
            config = EvolutionConfig(
                storage_dir=tmp_dir,
                strategy_injection_probability=0.0,
                evolution_threshold=1,
            )
            fuzzer = NaturalLanguageProofFuzzerLLMInterface(proof, llm)
            evolutionary = EvolutionaryProofFuzzer(fuzzer, store=store, config=config)

            evolutionary.run_false_proof_attempt(metadata={"llm_category": "Algebra"})
            strategies = evolutionary.store.load_strategies("natural_language")
            strategy_ids = {strategy.strategy_id for strategy in strategies}

            self.assertIn("mined_test_pinned", strategy_ids)
            self.assertTrue(any(strategy.title == "Plausible representation slip" for strategy in strategies))

    def test_evolution_replaces_only_matching_topic_slice(self) -> None:
        proof = "Let n be even.\n\nThen n = 2k for some integer k.\n\nTherefore n^2 is even."
        llm = FakeLLM([JUDGE_CORRECT_RESPONSE, MUTATION_RESPONSE, JUDGE_INCORRECT_RESPONSE, JUDGE_CORRECT_RESPONSE, EVOLUTION_RESPONSE])

        geometry_strategy = FuzzStrategy(
            strategy_id="geometry_keep",
            fuzzer_kind="natural_language",
            title="Geometry keep",
            guidance="Keep this geometry strategy untouched.",
            math_topic="geometry",
            target_correctness=False,
        )
        algebra_old_strategy = FuzzStrategy(
            strategy_id="algebra_replace",
            fuzzer_kind="natural_language",
            title="Old algebra",
            guidance="This algebra strategy can be replaced.",
            math_topic="algebra",
            target_correctness=False,
        )

        with tempfile.TemporaryDirectory() as tmp_dir:
            store = ProofFuzzAttemptStore(tmp_dir)
            store.save_strategies("natural_language", [geometry_strategy, algebra_old_strategy])
            config = EvolutionConfig(
                storage_dir=tmp_dir,
                strategy_injection_probability=0.0,
                evolution_threshold=1,
            )
            fuzzer = NaturalLanguageProofFuzzerLLMInterface(proof, llm)
            evolutionary = EvolutionaryProofFuzzer(fuzzer, store=store, config=config)

            evolutionary.run_false_proof_attempt(metadata={"llm_category": "Algebra"})
            strategies = evolutionary.store.load_strategies("natural_language")
            strategies_by_id = {strategy.strategy_id: strategy for strategy in strategies}

            self.assertIn("geometry_keep", strategies_by_id)
            self.assertEqual(strategies_by_id["geometry_keep"].title, "Geometry keep")
            self.assertNotIn("algebra_replace", strategies_by_id)
            self.assertTrue(any(strategy.title == "Plausible representation slip" for strategy in strategies))
            self.assertTrue(all(strategy.math_topic in {"algebra", "geometry"} for strategy in strategies))

    def test_truncated_completion_is_retried_before_parsing(self) -> None:
        proof = "Let n be even.\n\nThen n = 2k for some integer k.\n\nTherefore n^2 is even."
        llm = FinishReasonLLM(
            [JUDGE_CORRECT_RESPONSE, MUTATION_RESPONSE, MUTATION_RESPONSE, JUDGE_INCORRECT_RESPONSE, JUDGE_CORRECT_RESPONSE],
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
            self.assertEqual(len(llm.prompts), 5)

    def test_context_failure_shrinks_natural_language_prompt_and_retries(self) -> None:
        proof = "\n\n".join(f"Step {index}: this is a long proof paragraph." for index in range(80))
        llm = FakeLLM([JUDGE_CORRECT_RESPONSE, RuntimeError("context length exceeded"), MUTATION_RESPONSE, JUDGE_INCORRECT_RESPONSE, JUDGE_CORRECT_RESPONSE])

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
