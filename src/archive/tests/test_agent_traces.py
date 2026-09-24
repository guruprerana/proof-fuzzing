import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from src.proof_fuzzer.agent_trace import AgentTraceProfile
from src.proof_fuzzer.datasets.reflect import iter_json_objects
from src.proof_fuzzer.datasets import TextProofExample


def trace(*contents):
    return json.dumps([{"step_type": "planning", "position": index,
                        "content": {"think": content}, "reward_attach_token": "</think>"}
                       for index, content in enumerate(contents)], indent=2)


class AgentTraceTests(unittest.TestCase):
    def setUp(self):
        self.profile = AgentTraceProfile()
        self.example = TextProofExample("t", "Find reliable evidence", trace("plan", "answer"))

    def test_multiline_json_objects_are_loaded(self):
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "rows.jsonl"
            path.write_text('{\n  "a": 1\n}\n{"b": 2}\n')
            self.assertEqual(list(iter_json_objects(path)), [{"a": 1}, {"b": 2}])

    def test_structural_guard_accepts_one_content_edit(self):
        candidate = json.loads(self.example.proof)
        candidate[1]["content"]["think"] = "unsupported answer"
        self.profile.validate_candidate(self.example, json.dumps(candidate))

    def test_structural_guard_rejects_multiple_edits_and_metadata_edit(self):
        candidate = json.loads(self.example.proof)
        candidate[0]["content"]["think"] = "bad plan"
        candidate[1]["content"]["think"] = "bad answer"
        with self.assertRaisesRegex(ValueError, "exactly one"):
            self.profile.validate_candidate(self.example, json.dumps(candidate))
        candidate = json.loads(self.example.proof)
        candidate[0]["position"] = 9
        with self.assertRaisesRegex(ValueError, "identity metadata"):
            self.profile.validate_candidate(self.example, json.dumps(candidate))

    def test_blind_prompt_contains_only_submitted_trace(self):
        submitted = trace("candidate-only")
        prompt = self.profile.blind_prompt(self.example, submitted)
        self.assertIn("candidate-only", prompt)
        self.assertNotIn('"think": "plan"', prompt)
        self.assertNotIn("introduced error", prompt.lower())
        self.assertIn("single recorded", prompt)

    def test_validity_uses_direct_boolean_without_label_inversion(self):
        prompt = self.profile.validity_prompt(self.example, trace("plan", "bad"), "new flaw")
        self.assertIn('"introduced_error_is_genuine":true', prompt)
        self.assertNotIn('"verdict"', prompt)
        genuine = self.profile.parse_validity(
            '{"introduced_error_is_genuine":true,"confidence":0.9,"rationale":"real flaw"}')
        harmless = self.profile.parse_validity(
            '{"introduced_error_is_genuine":false,"confidence":0.8,"rationale":"harmless"}')
        uncertain = self.profile.parse_validity(
            '{"introduced_error_is_genuine":null,"confidence":0.2,"rationale":"unclear"}')
        self.assertEqual((genuine.verdict, harmless.verdict, uncertain.verdict),
                         ("incorrect", "correct", "uncertain"))


if __name__ == "__main__":
    unittest.main()
