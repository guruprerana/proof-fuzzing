import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from src.proof_fuzzer.robust_distillation import collect_replicated_evidence


class RobustDistillationTests(unittest.TestCase):
    def test_requires_complete_run_and_collects_only_replicated_valid_unique_misses(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "status.json").write_text(json.dumps({"complete": True}))
            (root / "summary.json").write_text(json.dumps({"complete": True}))
            reviews = lambda n: ([{"detection": "missed"}] * n
                                 + [{"detection": "caught"}] * (3 - n))
            rows = [
                {"proof_id": "p1", "valid": True, "mutation_sha256": "a",
                 "reviews": reviews(2), "introduced_error": "good"},
                {"proof_id": "p2", "valid": True, "mutation_sha256": "b",
                 "reviews": reviews(1), "introduced_error": "single"},
                {"proof_id": "p3", "valid": False, "mutation_sha256": "c",
                 "reviews": reviews(3), "introduced_error": "invalid"},
                {"proof_id": "p1", "valid": True, "mutation_sha256": "a",
                 "reviews": reviews(3), "introduced_error": "duplicate"},
            ]
            (root / "results.json").write_text(json.dumps(rows))
            evidence = collect_replicated_evidence([root])
            self.assertEqual(len(evidence), 1)
            self.assertEqual(evidence[0]["introduced_error"], "good")

            (root / "status.json").write_text(json.dumps({"complete": False}))
            with self.assertRaisesRegex(ValueError, "incomplete"):
                collect_replicated_evidence([root])
            self.assertEqual(len(collect_replicated_evidence(
                [root], allow_incomplete=True)), 1)


if __name__ == "__main__":
    unittest.main()
