import unittest
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from src.proof_fuzzer.frozen_evaluation import (
    exact_mcnemar_one_sided, run_frozen_evaluation, summarize_frozen,
)


class Example:
    def __init__(self, example_id):
        self.example_id = example_id
        self.selector = example_id
        self.problem = f"Problem {example_id}"
        self.proof = f"Proof {example_id}"


def row(proof_id, arm, misses, valid=True):
    return {"proof_id": proof_id, "arm": arm, "valid": valid,
            "reviews": [{"detection": "missed" if index < misses else "caught"}
                        for index in range(3)]}


class FrozenEvaluationTests(unittest.TestCase):
    def test_exact_one_sided_p_value(self):
        self.assertEqual(exact_mcnemar_one_sided(0, 0), 1.0)
        self.assertEqual(exact_mcnemar_one_sided(6, 0), 1 / 64)
        self.assertAlmostEqual(exact_mcnemar_one_sided(7, 1), 9 / 256)

    def test_summary_uses_proof_level_replicated_misses(self):
        proofs = [Example(str(index)) for index in range(8)]
        rows = []
        for proof in proofs:
            rows.extend((row(proof.example_id, "generic", 1),
                         row(proof.example_id, "strategies", 2)))
        summary = summarize_frozen(rows, proofs, attempts_per_arm=1, alpha=0.01)
        self.assertTrue(summary["complete"])
        self.assertEqual(summary["generic_successes"], 0)
        self.assertEqual(summary["strategy_successes"], 8)
        self.assertEqual(summary["p_value"], 1 / 256)
        self.assertTrue(summary["significant_strategy_transfer"])

    def test_incomplete_run_cannot_be_significant(self):
        proofs = [Example("a"), Example("b")]
        rows = [row("a", "generic", 0), row("a", "strategies", 2)]
        summary = summarize_frozen(rows, proofs, attempts_per_arm=1, alpha=0.5)
        self.assertFalse(summary["complete"])
        self.assertFalse(summary["significant_strategy_transfer"])

    def test_summary_supports_configurable_review_threshold(self):
        proofs = [Example("a")]
        rows = [
            {"proof_id": "a", "arm": "generic", "valid": True,
             "reviews": [{"detection": "missed"}, {"detection": "caught"}]},
            {"proof_id": "a", "arm": "strategies", "valid": True,
             "reviews": [{"detection": "missed"}, {"detection": "missed"}]},
        ]
        summary = summarize_frozen(
            rows, proofs, attempts_per_arm=1, alpha=0.5,
            required_missed_reviews=2, reviews_per_valid_candidate=2,
        )
        self.assertEqual(summary["strategy_successes"], 1)
        self.assertEqual(
            summary["primary_endpoint"],
            "proof has >=1 valid candidate missed by >=2 of 2 reviews",
        )

    def test_duplicate_heldout_ids_are_rejected(self):
        strategy = "# Strategies:\n\n- Check.\n\n# Do not:\n\n- Guess.\n\n# Before returning:\n\n- Verify.\n"
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            strategy_path = root / "strategy.md"
            strategy_path.write_text(strategy)
            with self.assertRaisesRegex(ValueError, "must be unique"):
                run_frozen_evaluation(
                    heldout=[Example("duplicate"), Example("duplicate")],
                    strategy_path=strategy_path,
                    storage_dir=root / "run",
                    dry_run=True,
                )

    def test_dry_run_can_resume_exact_preregistration(self):
        strategy = "# Strategies:\n\n- Check a claim.\n\n# Do not:\n\n- Guess.\n\n# Before returning:\n\n- Verify.\n"
        fake_record = {"attempt": 1, "status": "judged", "assessment": {"valid": True,
            "reviews": [{"detection": "caught"}] * 3}, "elapsed_seconds": 0}
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            strategy_path = root / "strategy.md"
            strategy_path.write_text(strategy)
            output = root / "run"
            kwargs = dict(heldout=[Example("a")], strategy_path=strategy_path,
                storage_dir=output, attempts_per_arm=1, workers=1,
                provider="claude-code", model="claude-opus-5")
            run_frozen_evaluation(**kwargs, dry_run=True)
            with patch("src.proof_fuzzer.frozen_evaluation.run_session",
                       return_value=[fake_record]) as mocked:
                run_frozen_evaluation(**kwargs)
            self.assertEqual(mocked.call_count, 2)
            self.assertTrue(all(call.kwargs["provider"] == "claude-code"
                                for call in mocked.call_args_list))
            manifest = json.loads((output / "manifest.json").read_text())
            self.assertEqual(manifest["provider"], "claude-code")
            self.assertEqual(manifest["model"], "claude-opus-5")
            self.assertEqual(manifest["call_timeout_seconds"], 20 * 60)
            self.assertTrue(json.loads((output / "status.json").read_text())["complete"])

    def test_no_call_timeout_is_preregistered_and_forwarded(self):
        strategy = "# Strategies:\n\n- Check.\n\n# Do not:\n\n- Guess.\n\n# Before returning:\n\n- Verify.\n"
        fake_record = {"attempt": 1, "status": "judged", "assessment": {"valid": True,
            "reviews": [{"detection": "caught"}] * 3}, "elapsed_seconds": 0}
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            strategy_path = root / "strategy.md"
            strategy_path.write_text(strategy)
            output = root / "run"
            kwargs = dict(heldout=[Example("a")], strategy_path=strategy_path,
                storage_dir=output, attempts_per_arm=1, workers=1,
                disable_call_timeout=True)
            run_frozen_evaluation(**kwargs, dry_run=True)
            manifest = json.loads((output / "manifest.json").read_text())
            self.assertIsNone(manifest["call_timeout_seconds"])
            with patch("src.proof_fuzzer.frozen_evaluation.run_session",
                       return_value=[fake_record]) as mocked:
                run_frozen_evaluation(**kwargs)
            self.assertTrue(all(call.kwargs["disable_call_timeout"]
                                for call in mocked.call_args_list))

    def test_resume_uses_fresh_retry_names_after_prior_slots_exist(self):
        strategy = "# Strategies:\n\n- Check a claim.\n\n# Do not:\n\n- Guess.\n\n# Before returning:\n\n- Verify.\n"
        fake_record = {"attempt": 1, "status": "judged", "assessment": {"valid": True,
            "reviews": [{"detection": "caught"}] * 3}, "elapsed_seconds": 0}
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            strategy_path = root / "strategy.md"
            strategy_path.write_text(strategy)
            output = root / "run"
            kwargs = dict(heldout=[Example("a")], strategy_path=strategy_path,
                storage_dir=output, attempts_per_arm=1, workers=1)
            run_frozen_evaluation(**kwargs, dry_run=True)
            for index in (1, 2):
                for retry in range(5):
                    suffix = "" if retry == 0 else f"_retry{retry}"
                    (output / "sessions" / f"{index:04d}{suffix}").mkdir(parents=True)
            with patch("src.proof_fuzzer.frozen_evaluation.run_session",
                       return_value=[fake_record]) as mocked:
                run_frozen_evaluation(**kwargs)
            self.assertEqual(mocked.call_count, 2)
            retry_paths = {call.args[0].name for call in mocked.call_args_list}
            self.assertEqual(retry_paths, {"0001_retry5", "0002_retry5"})

    def test_strategy_assignment_is_preregistered_and_only_sent_to_treatment(self):
        strategy = "# Strategies:\n\n- Check a claim.\n\n# Do not:\n\n- Guess.\n\n# Before returning:\n\n- Verify.\n"
        fake_record = {"attempt": 1, "status": "judged", "assessment": {"valid": True,
            "reviews": [{"detection": "caught"}] * 3}, "elapsed_seconds": 0}
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            strategy_path = root / "strategy.md"
            strategy_path.write_text(strategy)
            output = root / "run"
            with patch("src.proof_fuzzer.frozen_evaluation.run_session",
                       return_value=[fake_record]) as mocked:
                run_frozen_evaluation(heldout=[Example("a")], strategy_path=strategy_path,
                    storage_dir=output, attempts_per_arm=1, workers=1,
                    strategy_assignments={"a": ["Apply the hypothesis-mismatch strategy."]})
            manifest = json.loads((output / "manifest.json").read_text())
            self.assertEqual(manifest["strategy_assignments"]["a"][0],
                             "Apply the hypothesis-mismatch strategy.")
            calls = mocked.call_args_list
            generic = next(call for call in calls if call.args[5] is None)
            treatment = next(call for call in calls if call.args[5] is not None)
            self.assertEqual(generic.kwargs["extra_guidance"], "")
            self.assertIn("hypothesis-mismatch", treatment.kwargs["extra_guidance"])
            rows = json.loads((output / "results.json").read_text())
            self.assertIsNone(next(row for row in rows if row["arm"] == "generic")
                              ["strategy_assignment"])
            self.assertIn("hypothesis-mismatch",
                          next(row for row in rows if row["arm"] == "strategies")
                          ["strategy_assignment"])


if __name__ == "__main__":
    unittest.main()
