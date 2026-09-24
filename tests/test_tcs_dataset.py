from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from src.proof_fuzzer.openai_ten_advances import (
    DISCOVERY_IDS,
    load_openai_ten_advances_proofs,
    load_openai_ten_advances_split,
)


class TCSOpenProblemsDatasetTest(unittest.TestCase):
    def test_canonical_dataset_has_reported_five_five_split(self):
        root = Path("local_datasets/openai_ten_advances_2026/proofs_markdown")
        discovery, heldout = load_openai_ten_advances_split(root)
        self.assertEqual(tuple(proof.example_id for proof in discovery), DISCOVERY_IDS)
        self.assertEqual(len(heldout), 5)
        self.assertFalse({proof.example_id for proof in discovery} &
                         {proof.example_id for proof in heldout})
        self.assertTrue(all(proof.proof.startswith("# ") for proof in discovery + heldout))

    def test_loader_extracts_title_abstract_and_full_proof(self):
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "01_example.md").write_text(
                "# A New Theorem\n\nSource note.\n\n"
                "Abstract. We prove the desired result.\n\n"
                "Contents\n1. Proof\n\nProof details.\n"
            )
            proof = load_openai_ten_advances_proofs(root)[0]
            self.assertEqual(proof.title, "A New Theorem")
            self.assertEqual(proof.abstract, "We prove the desired result.")
            self.assertIn("Proof details.", proof.proof)
            self.assertNotIn("Contents", proof.problem)


if __name__ == "__main__":
    unittest.main()
