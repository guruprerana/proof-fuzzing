import hashlib
import json
import re
import unittest
import unicodedata
from collections import Counter
from pathlib import Path

from scripts.build_graduate_course_dossiers import DATASET, build


ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = ROOT / "local_datasets/graduate_course_dossiers_v1_sources"
DATASET_PATH = ROOT / "local_datasets/graduate_course_dossiers_v1.json"


class GraduateCourseDossiersTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.payload = build(SOURCE_DIR)

    def test_balanced_splits_and_unique_records(self):
        expected = Counter({"algebra and number theory": 4, "analysis": 3, "geometry and topology": 3})
        all_rows = self.payload["discovery"] + self.payload["heldout"]
        self.assertEqual(len(self.payload["discovery"]), 10)
        self.assertEqual(len(self.payload["heldout"]), 10)
        for split in ("discovery", "heldout"):
            self.assertEqual(Counter(row["metadata"]["broad_area"] for row in self.payload[split]), expected)
        self.assertEqual(len({row["example_id"] for row in all_rows}), 20)
        self.assertEqual(len({row["metadata"]["source_text_sha256"] for row in all_rows}), 20)
        self.assertEqual(Counter(row["metadata"]["pair"] for row in all_rows), Counter({f"nt-{i}": 2 for i in range(1, 5)} | {f"analysis-{i}": 2 for i in range(1, 4)} | {f"topology-{i}": 2 for i in range(1, 4)}))

    def test_lengths_provenance_and_hashes(self):
        for row in self.payload["discovery"] + self.payload["heldout"]:
            metadata = row["metadata"]
            self.assertEqual(metadata["dataset"], DATASET)
            self.assertTrue(metadata["correctness"])
            self.assertTrue(metadata["internet_sourced"])
            self.assertGreaterEqual(metadata["actual_word_count"], 6000)
            self.assertLessEqual(metadata["actual_word_count"], 13500)
            self.assertEqual(metadata["actual_word_count"], len(row["proof"].split()))
            self.assertGreater(metadata["theorem_like_marker_count"], 0)
            self.assertGreater(metadata["proof_marker_count"], 0)
            self.assertEqual(metadata["source_text_sha256"], hashlib.sha256(row["proof"].encode()).hexdigest())
            self.assertIn(metadata["license"], {"CC BY-NC-SA 4.0", "MIT", "No explicit license located"})
            for source in metadata["source_files"]:
                self.assertEqual(source["sha256"], hashlib.sha256((SOURCE_DIR / source["path"]).read_bytes()).hexdigest())

    def test_clean_model_readable_text(self):
        forbidden_fragments = (
            "\ufffd", "\f", "\u00ad", "7→", "7−→", "−→",
            "Lecture by Andrew V. Sutherland", "18.785 Fall 2025, Lecture #",
        )
        for row in self.payload["discovery"] + self.payload["heldout"]:
            proof = row["proof"]
            self.assertFalse(
                any(unicodedata.category(char) == "Cc" and char not in "\n\t" for char in proof),
                row["example_id"],
            )
            for fragment in forbidden_fragments:
                self.assertNotIn(fragment, proof, f"{row['example_id']}: {fragment!r}")
            for line in proof.splitlines():
                running_head = re.fullmatch(r"\s*(\d+\.\s+.+?)\s{2,}(\d+)\s*", line)
                if running_head:
                    letters = "".join(char for char in running_head.group(1) if char.isalpha())
                    self.assertFalse(letters and letters.isupper(), f"{row['example_id']}: {line!r}")

    def test_committed_dataset_is_reproducible(self):
        self.assertEqual(json.loads(DATASET_PATH.read_text()), self.payload)

    def test_no_long_text_reused_from_existing_internet_dossiers(self):
        old_path = ROOT / "local_datasets/archive/superseded_proof_datasets_2026-09-21/generated_proof_datasets/internet_sourced_dossiers_v1.json"
        old = json.loads(old_path.read_text())
        old_tokens = " ".join(row["proof"] for row in old["discovery"]).split()
        old_shingles = {tuple(old_tokens[index:index + 100]) for index in range(len(old_tokens) - 99)}
        for row in self.payload["discovery"] + self.payload["heldout"]:
            tokens = row["proof"].split()
            self.assertFalse(any(tuple(tokens[index:index + 100]) in old_shingles for index in range(len(tokens) - 99)))


if __name__ == "__main__":
    unittest.main()
