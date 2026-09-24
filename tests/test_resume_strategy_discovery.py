import json
import hashlib
from pathlib import Path
from types import SimpleNamespace
from tempfile import TemporaryDirectory
import unittest

from scripts.resume_strategy_discovery import (
    load_records,
    recover_interrupted_attempt,
    usable_attempt,
)
from src.proof_fuzzer.agent_cli_client import AgentCLICallTechnicalError
from src.proof_fuzzer.judging import BlindErrorFinder


class ResumeStrategyDiscoveryTests(unittest.TestCase):
    def test_only_fully_assessed_mutation_is_usable(self):
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            archive = root / "attempts/001"
            archive.mkdir(parents=True)
            for name in ("mutated_proof.md", "introduced_error.md", "judge_response.txt"):
                (archive / name).write_text("x")
            record = {
                "attempt": 1,
                "assessment": {
                    "valid": True,
                    "mechanism_id": "M001",
                    "detection": "caught",
                },
            }
            self.assertTrue(usable_attempt(root, record))
            record["assessment"]["mechanism_id"] = None
            self.assertFalse(usable_attempt(root, record))

    def test_load_records_preserves_append_order(self):
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "attempts.jsonl").write_text(
                json.dumps({"attempt": 1}) + "\n" + json.dumps({"attempt": 2}) + "\n"
            )
            self.assertEqual([row["attempt"] for row in load_records(root)], [1, 2])

    def test_recovery_timeout_is_recorded_without_retrying(self):
        class TimeoutJudge:
            calls = 0

            def complete(self, _prompt):
                self.calls += 1
                raise AgentCLICallTechnicalError("Call exceeded 1200 seconds")

        class Assessor:
            def __call__(self, _proof, _archive):
                return {
                    "valid": True,
                    "detection": "ambiguous",
                    "mechanism_id": "M001",
                }

        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            candidate = root / "mutator_workspace/attempts/001"
            candidate.mkdir(parents=True)
            (candidate / "original_proof.md").write_text("original\n")
            (candidate / "mutated_proof.md").write_text("mutated\n")
            (candidate / "introduced_error.md").write_text("explanation\n")
            proof = SimpleNamespace(
                proof="original\n", problem="problem", example_id="proof-1"
            )
            records = []
            judge = TimeoutJudge()

            self.assertTrue(recover_interrupted_attempt(
                root, proof, records, judge, Assessor(), "thread-1"
            ))

            self.assertEqual(judge.calls, 1)
            self.assertEqual(records[0]["status"], "failed")
            self.assertEqual(records[0]["failure_stage"], "target_judge")
            self.assertIn("Call exceeded 1200 seconds", records[0]["error"])
            self.assertFalse(usable_attempt(root, records[0]))
            self.assertEqual(load_records(root), records)
            feedback = json.loads((root / "attempts/001/feedback.json").read_text())
            self.assertEqual(feedback["status"], "failed")

    def test_incomplete_interrupted_mutation_is_checkpointed(self):
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "mutator_workspace/attempts/001").mkdir(parents=True)
            proof = SimpleNamespace(
                proof="original\n", problem="problem", example_id="proof-1"
            )
            records = []

            self.assertTrue(recover_interrupted_attempt(
                root, proof, records, object(), object(), "thread-1"
            ))

            self.assertEqual(records[0]["status"], "failed")
            self.assertEqual(records[0]["failure_stage"], "mutation_recovery")
            self.assertFalse(usable_attempt(root, records[0]))
            self.assertTrue((root / "attempts/001/result.json").is_file())

    def test_prior_terminal_timeout_is_not_called_again(self):
        class Judge:
            def __init__(self, workspace_root):
                self.workspace_root = workspace_root
                self.calls = 0

            def complete(self, _prompt):
                self.calls += 1
                raise AssertionError("prior timeout must not be retried")

        class Assessor:
            def __call__(self, _proof, _archive):
                return {
                    "valid": True,
                    "detection": "ambiguous",
                    "mechanism_id": "M001",
                }

        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            candidate = root / "mutator_workspace/attempts/001"
            candidate.mkdir(parents=True)
            (candidate / "original_proof.md").write_text("original\n")
            (candidate / "mutated_proof.md").write_text("mutated\n")
            (candidate / "introduced_error.md").write_text("explanation\n")
            proof = SimpleNamespace(
                proof="original\n", problem="problem", example_id="proof-1"
            )
            judge = Judge(root / "judge/workspaces")
            prompt = BlindErrorFinder(judge).prompt(
                problem=proof.problem, proof="mutated\n"
            )
            retry = judge.workspace_root / "call_000001/technical_retry.json"
            retry.parent.mkdir(parents=True)
            retry.write_text(json.dumps({
                "attempt": 1,
                "retry_scheduled": False,
                "error": "Call exceeded 1200 seconds",
                "prompt_sha256": hashlib.sha256(prompt.encode()).hexdigest(),
            }))
            records = []

            self.assertTrue(recover_interrupted_attempt(
                root, proof, records, judge, Assessor(), "thread-1"
            ))

            self.assertEqual(judge.calls, 0)
            self.assertEqual(records[0]["status"], "failed")
            self.assertIn("Call exceeded 1200 seconds", records[0]["error"])


if __name__ == "__main__":
    unittest.main()
