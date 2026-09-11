import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from src.proof_fuzzer.datasets import adapt_examples
from src.proof_fuzzer.datasets.olympiadbench import load_split
from src.proof_fuzzer.datasets.json_split import load_json_split
from src.proof_fuzzer.strategy_transfer import run_strategy_transfer


class OlympiadAdapterTests(unittest.TestCase):
    def test_portable_json_split(self):
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "split.json"
            path.write_text(json.dumps({
                "discovery": [{"example_id": "a", "problem": "P", "proof": "A"}],
                "heldout": [{"example_id": "b", "problem": "Q", "proof": "B"}],
            }))
            discovery, heldout = load_json_split(path)
            self.assertEqual(discovery[0].proof, "A")
            self.assertEqual(heldout[0].example_id, "b")

    def test_generic_field_adapter(self):
        class Record:
            example_id = "imo-1"
            problem = "Show that..."
            response = "Proof."
            metadata = {"dataset": "imo"}

        adapted = adapt_examples([Record()], proof_attribute="response")[0]
        self.assertEqual((adapted.example_id, adapted.problem, adapted.proof),
                         ("imo-1", "Show that...", "Proof."))
        self.assertEqual(adapted.metadata()["dataset"], "imo")

    def fixture(self, root: Path):
        for index in range(10):
            folder = root / f"{index:06d}"
            folder.mkdir(parents=True)
            (folder / "metadata.json").write_text(json.dumps({"original_data": {
                "id": index, "question": f"Problem {index}",
                "solution": [f"Proof {index}", f"Alternative {index}"],
                "subfield": "Algebra"}}))
        return [f"{i:06d}" for i in range(5)], [f"{i:06d}" for i in range(5, 10)]

    def test_individual_solution_and_disjoint_split(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            discovery, heldout = self.fixture(root)
            discovery[0] += ":1"
            train, test = load_split(root, discovery, heldout)
            self.assertEqual(train[0].proof, "Alternative 0")
            self.assertEqual(train[0].metadata()["artifact"], "original_data.solution[1]")
            self.assertFalse({p.example_id for p in train} & {p.example_id for p in test})

    def test_generic_pipeline_dry_run_accepts_adapter_examples(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            discovery, heldout = self.fixture(root / "dataset")
            train, test = load_split(root / "dataset", discovery, heldout)
            output = root / "run"
            run_strategy_transfer(discovery=train, heldout=test, storage_dir=output,
                                  discovery_attempts=2, evaluation_attempts_per_proof=3,
                                  dry_run=True)
            manifest = json.loads((output / "manifest.json").read_text())
            self.assertEqual(manifest["discovery_attempts_per_proof"], 2)
            self.assertEqual(manifest["evaluation_attempts_per_proof_per_arm"], 3)


if __name__ == "__main__":
    unittest.main()
