import unittest

from src.proof_fuzzer.judging import (
    MutationValidator, load_json_object, parse_judge_result, parse_match_result,
    usage_limit_reached,
)
from src.proof_fuzzer.models import FuzzerMutationInstructions


class JudgingTests(unittest.TestCase):
    def test_fenced_inventory_parses(self):
        result = parse_judge_result('```json\n{"errors": [], "review_summary": "checked"}\n```')
        self.assertEqual(result.verdict, "correct")
        self.assertEqual(result.response_kind, "error_inventory")

    def test_plain_markdown_inventory_parses(self):
        result = parse_judge_result(
            "- **Lemma 2:** The claimed inequality reverses the order.\n"
            "  Consequently the induction does not close.\n"
            "- **Theorem 4:** The endpoint case is omitted."
        )
        self.assertEqual(result.verdict, "incorrect")
        self.assertEqual(result.response_kind, "error_inventory")
        self.assertEqual(len(result.detected_errors), 2)
        self.assertTrue(result.detected_errors[0]["unstructured"])

    def test_plain_no_error_response_parses_as_empty_inventory(self):
        result = parse_judge_result("I found no concrete mathematical errors.")
        self.assertEqual(result.verdict, "correct")
        self.assertEqual(result.detected_errors, ())

    def test_malformed_json_is_not_reclassified_as_plaintext(self):
        for response in ("", "[]", '{"errors": [}'):
            with self.subTest(response=response), self.assertRaises(ValueError):
                parse_judge_result(response)

    def test_only_exact_match_counts(self):
        partial = parse_match_result('{"introduced_error_found":true,"match_level":"partial"}')
        exact = parse_match_result('{"introduced_error_found":true,"match_level":"exact"}')
        self.assertFalse(partial["introduced_error_found"])
        self.assertTrue(exact["introduced_error_found"])

    def test_missing_json_is_rejected(self):
        with self.assertRaises(ValueError):
            load_json_object("no structured response")

    def test_unescaped_latex_backslashes_are_repaired_without_model_retry(self):
        result = load_json_object(r'{"rationale":"x \ge 0 and \frac{1}{2}"}')
        self.assertEqual(result["rationale"], r"x \ge 0 and \frac{1}{2}")

    def test_validator_verdict_polarity_matches_pipeline(self):
        prompt = MutationValidator(None).prompt(original="valid", mutated="invalid",
            instructions=FuzzerMutationInstructions(False, (), "new flaw"), problem="P")
        self.assertIn('Return "incorrect" exactly when', prompt)
        self.assertIn('Return "correct" when the alleged flaw is absent', prompt)

    def test_claude_session_limit_is_a_usage_limit(self):
        self.assertTrue(usage_limit_reached("You've hit your session limit"))


if __name__ == "__main__":
    unittest.main()
