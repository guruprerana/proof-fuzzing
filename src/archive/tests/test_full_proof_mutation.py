import unittest
import json
import tempfile
from types import SimpleNamespace
from src.archive.proof_fuzzer.evolution import ImperfectProofMutationJudge
from src.archive.proof_fuzzer.llm_interface import FuzzerMutationInstructions, NaturalLanguageProofFuzzerLLMInterface
from src.archive.proof_fuzzer.evolution import EvolutionConfig
from src.archive.proof_fuzzer.prompt_evolution import PromptEvolutionConfig, PromptEvolutionaryProofFuzzer
from src.proof_fuzzer.proof_bench_judge import format_natural_language_proof_objective


class FullProofMutationTests(unittest.TestCase):
    def test_plaintext_generation_and_explanation_isolation(self):
        response = "## Mutated proof\nLet n be even. Then n=2k+1.\n\n## Introduced error\nPRIVATE: replaces even with odd."
        replies = iter([
            response,
            json.dumps({"verdict": "incorrect", "confidence": 1, "rationale": "New parity error"}),
            json.dumps({"errors": [], "review_summary": "Original review"}),
            json.dumps({"errors": [], "review_summary": "Mutated review"}),
            json.dumps({"introduced_error_found": False, "match_level": "none"}),
        ])
        prompts = []

        class Client:
            def complete(self, prompt):
                prompts.append(prompt)
                return next(replies)

        with tempfile.TemporaryDirectory() as tmp:
            controller = PromptEvolutionaryProofFuzzer(
                Client(), config=PromptEvolutionConfig(storage_dir=tmp),
                attempt_config=EvolutionConfig(
                    full_proof_mutation_output=True, original_proof_may_be_incorrect=True,
                    run_pre_mutation_judge=False, run_original_error_control=True,
                    judge_error_detection_check=True,
                ),
            )
            result = controller.run_false_proof_attempt(
                proof_text="Let n be even. Then n=2k.", objective="Problem:\nProve parity.",
                metadata={"problem": "Prove parity."},
            )
        self.assertTrue(result.success)
        self.assertEqual(result.mutated_proof_text, "Let n be even. Then n=2k+1.")
        self.assertNotIn("maintain_correctness", prompts[0])
        self.assertNotIn("JSON", prompts[0])
        self.assertNotIn("Targetable proof segments", prompts[0])
        self.assertIn("## Mutated proof", prompts[0])
        self.assertIn("PRIVATE:", prompts[1])
        self.assertIn("<mutated_proof>\nLet n be even. Then n=2k+1.", prompts[1])
        self.assertIn("<introduced_error>\nPRIVATE: replaces even with odd.", prompts[1])
        self.assertNotIn("maintain_correctness", prompts[1])
        self.assertNotIn("PRIVATE:", prompts[2])
        self.assertNotIn("PRIVATE:", prompts[3])
        self.assertEqual(
            prompts[2].replace("Let n be even. Then n=2k.", "<PROOF>"),
            prompts[3].replace("Let n be even. Then n=2k+1.", "<PROOF>"),
        )
        for review_prompt in prompts[2:4]:
            self.assertIn("even when the final conclusion is true", review_prompt)
            self.assertIn("another argument establishes it", review_prompt)
        self.assertIn("PRIVATE:", prompts[4])
        self.assertIn("<introduced_error>\nPRIVATE: replaces even with odd.\n</introduced_error>", prompts[4])
        self.assertIn("Let n be even. Then n=2k.", prompts[4])
        self.assertIn("Let n be even. Then n=2k+1.", prompts[4])
        self.assertIn("Original review", prompts[4])
        self.assertIn("Mutated review", prompts[4])
        self.assertNotIn("maintain_correctness", prompts[4])

    def test_plaintext_parser_rejects_ambiguous_or_empty_sections(self):
        fuzzer = NaturalLanguageProofFuzzerLLMInterface("Original", full_proof_mutation_output=True)
        for response in (
            "A proof with no separator", "## Mutated proof\nChanged",
            "## Mutated proof\n\n## Introduced error\nExplanation",
            "## Mutated proof\nChanged\n## Introduced error\n",
            "## Mutated proof\nOriginal\n## Introduced error\nExplanation",
            "## Mutated proof\nChanged\n## Introduced error\nExplanation\n## Introduced error\nMore",
        ):
            with self.subTest(response=response), self.assertRaises(ValueError):
                fuzzer.parse_full_proof_mutation_response(response)

    def test_imperfect_validator_requires_new_error(self):
        prompt = ImperfectProofMutationJudge(None).judge_prompt(
            original_proof_text="Existing gap.", mutated_proof_text="Existing gap plus new error.",
            mutation_instructions=FuzzerMutationInstructions(False, ()),
        )
        self.assertNotIn("reference proof is believed to be correct", prompt)
        self.assertIn("Global invalidity alone never validates a mutation", prompt)
        self.assertIn("Reject rewordings or downstream manifestations", prompt)
        self.assertIn("The error need not be essential to the overall proof", prompt)
        self.assertIn("another argument\nestablishes it", prompt)
        self.assertIn("Do not audit unrelated parts", prompt)
        self.assertNotIn("first indispensable broken step", prompt)
        self.assertNotIn("salvaged/irrelevant", prompt)
        self.assertNotIn("minimally exposed", prompt)

    def test_imperfect_source_objective(self):
        example = SimpleNamespace(example_id="example", problem="Prove parity.",
                                  original_proof_may_be_incorrect=True)
        objective = format_natural_language_proof_objective(example, dataset_name="Synthetic")
        self.assertNotIn("Fuzz this correct", objective)
        self.assertIn("may already contain errors", objective)


if __name__ == "__main__":
    unittest.main()
