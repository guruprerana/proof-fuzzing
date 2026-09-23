import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from scripts.resume_strategy_discovery import load_records, usable_attempt


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


if __name__ == "__main__":
    unittest.main()
