from pathlib import Path
import tempfile
import unittest

from src.proof_fuzzer import (
    OpenAITenAdvancesEvolutionRunConfig,
    load_openai_ten_advances_proofs,
)


class OpenAITenAdvancesTest(unittest.TestCase):
    def test_loader_keeps_full_markdown_and_extracts_problem(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            source = root / "01_example.md"
            source.write_text(
                "# A New Theorem\n\nSource note.\n\n"
                "Abstract. We prove the desired sharp result.\n\n"
                "Contents\n1. Proof\n\nProof details.\n",
                encoding="utf-8",
            )

            proofs = load_openai_ten_advances_proofs(root)

            self.assertEqual(len(proofs), 1)
            self.assertEqual(proofs[0].example_id, "01_example")
            self.assertEqual(proofs[0].title, "A New Theorem")
            self.assertEqual(proofs[0].abstract, "We prove the desired sharp result.")
            self.assertIn("Proof details.", proofs[0].proof)
            self.assertNotIn("Contents", proofs[0].problem)
            self.assertEqual(proofs[0].to_metadata()["dataset"], "openai_ten_advances_2026")

    def test_run_defaults_disable_mined_strategy_seeding(self) -> None:
        config = OpenAITenAdvancesEvolutionRunConfig()

        self.assertEqual(config.num_attempts, 200)
        self.assertFalse(config.seed_mined_strategies)
        self.assertIsNone(config.mined_strategy_path)
        self.assertEqual(config.correctness_selection_mode, "false_proof")
        self.assertEqual(config.max_proof_chars, 300_000)


if __name__ == "__main__":
    unittest.main()
