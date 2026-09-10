import json
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
import unittest

from src.proof_fuzzer.persistent_fuzzing import run_attempts


class PersistentFuzzingTests(unittest.TestCase):
    def test_strategy_guided_one_attempt_per_proof(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            workspace = root / "mutator_workspace"
            workspace.mkdir()
            proofs = [SimpleNamespace(example_id=str(i), proof=f"Original {i}", problem=f"Problem {i}")
                      for i in (1, 2)]
            turns, judge_calls = [], []
            thread = SimpleNamespace(id="one-thread")

            def mutate(received, sdk, prompt, **kwargs):
                self.assertIs(received, thread)
                index = len(turns) + 1
                turns.append(index)
                candidate = workspace / "attempts" / f"{index:03d}"
                self.assertEqual((candidate / "original_proof.md").read_text(), f"Original {index}")
                self.assertEqual((workspace / "problem.txt").read_text(), f"Problem {index}")
                self.assertEqual((workspace / "strategies.md").read_text(), "PRIVATE STRATEGIES")
                self.assertIn("exactly one candidate submission per proof", (workspace / "prompt.txt").read_text())
                (candidate / "mutated_proof.md").write_text(f"Mutation {index}")
                (candidate / "introduced_error.md").write_text("PRIVATE explanation")
                return SimpleNamespace(final_response="Done")

            def judge(prompt):
                index = len(judge_calls) + 1
                judge_calls.append(index)
                self.assertIn(f"Mutation {index}", prompt)
                self.assertIn(f"Problem {index}", prompt)
                self.assertNotIn("PRIVATE", prompt)
                return '{"errors": [], "review_summary": "Reviewed"}'

            records = run_attempts(root=root, proof=proofs[0], proofs=proofs, total=2,
                                   strategy_text="PRIVATE STRATEGIES", thread=thread, sdk=None,
                                   mutator=SimpleNamespace(_run_thread=mutate),
                                   judge=SimpleNamespace(complete=judge))
            self.assertEqual([r["proof_id"] for r in records], ["1", "2"])
            self.assertEqual(turns, [1, 2])
            self.assertEqual(judge_calls, [1, 2])

    def test_same_thread_feedback_and_blind_judge(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            workspace = root / "mutator_workspace"
            workspace.mkdir()
            proof = SimpleNamespace(proof="Original proof.\nUnchanged ending.", problem="Problem")
            thread = SimpleNamespace(id="persistent-thread")
            calls, prompts = [], []

            def mutate(received_thread, sdk, prompt, **kwargs):
                self.assertIs(received_thread, thread)
                index = len(calls) + 1
                calls.append(kwargs["trace_dir"])
                if index == 2:
                    feedback = json.loads((workspace / "feedback/001.json").read_text())
                    self.assertIn("judge_report", feedback)
                candidate = workspace / "attempts" / f"{index:03d}"
                (candidate / "mutated_proof.md").write_text(f"Mutation {index}.\nUnchanged ending.")
                (candidate / "introduced_error.md").write_text("PRIVATE explanation")
                return SimpleNamespace(final_response="Saved")

            def judge(prompt):
                prompts.append(prompt)
                self.assertNotIn("PRIVATE", prompt)
                self.assertNotIn("Original proof.", prompt)
                return '{"errors": [], "review_summary": "No errors found"}'

            records = run_attempts(root=root, proof=proof, total=2,
                                   mutator=SimpleNamespace(_run_thread=mutate), thread=thread,
                                   sdk=None, judge=SimpleNamespace(complete=judge))
            self.assertEqual(len(set(calls)), 2)
            self.assertEqual(len(prompts), 2)
            self.assertTrue(all(r["verified_success"] is None for r in records))
            self.assertTrue((root / "attempts/002/mutation.diff").exists())
            summary = json.loads((root / "summary.json").read_text())
            self.assertTrue(summary["complete"])
            self.assertIsNone(summary["verified_misses"])


if __name__ == "__main__":
    unittest.main()
