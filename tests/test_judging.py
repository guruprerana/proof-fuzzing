import unittest

from src.proof_fuzzer.judging import (
    MutationValidator, load_json_object, parse_judge_result, parse_match_result,
)
from src.proof_fuzzer.models import FuzzerMutationInstructions


class JudgingTests(unittest.TestCase):
    def test_fenced_inventory_parses(self):
        result = parse_judge_result('```json\n{"errors": [], "review_summary": "checked"}\n```')
        self.assertEqual(result.verdict, "correct")
        self.assertEqual(result.response_kind, "error_inventory")

    def test_only_exact_match_counts(self):
        partial = parse_match_result('{"introduced_error_found":true,"match_level":"partial"}')
        exact = parse_match_result('{"introduced_error_found":true,"match_level":"exact"}')
        self.assertFalse(partial["introduced_error_found"])
        self.assertTrue(exact["introduced_error_found"])

    def test_missing_json_is_rejected(self):
        with self.assertRaises(ValueError):
            load_json_object("no structured response")

    def test_validator_verdict_polarity_matches_pipeline(self):
        prompt = MutationValidator(None).prompt(original="valid", mutated="invalid",
            instructions=FuzzerMutationInstructions(False, (), "new flaw"), problem="P")
        self.assertIn('Return "incorrect" exactly when', prompt)
        self.assertIn('Return "correct" when the alleged flaw is absent', prompt)


if __name__ == "__main__":
    unittest.main()
