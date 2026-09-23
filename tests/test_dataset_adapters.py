import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from src.proof_fuzzer.datasets import adapt_examples
from src.proof_fuzzer.datasets.olympiadbench import load_examples, load_split, load_split_manifest
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

    def test_discovery_only_json_split_requires_explicit_opt_in(self):
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "split.json"
            path.write_text(json.dumps({
                "discovery": [{"example_id": "a", "problem": "P", "proof": "A"}],
                "heldout": [],
            }))
            with self.assertRaisesRegex(ValueError, "nonempty list"):
                load_json_split(path)
            discovery, heldout = load_json_split(path, allow_empty_heldout=True)
            self.assertEqual([example.example_id for example in discovery], ["a"])
            self.assertEqual(heldout, [])

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
        topics = ("Algebra", "Combinatorics", "Geometry", "Number Theory")
        discovery, heldout = [], []
        for index in range(40):
            folder = root / f"{index:06d}"
            folder.mkdir(parents=True)
            topic = topics[index // 10]
            (folder / "metadata.json").write_text(json.dumps({
                "full_response": f"Model proof {index}", "original_data": {
                "id": index, "question": f"Problem {index}",
                "solution": [f"Proof {index}", f"Alternative {index}"],
                "subfield": topic}}))
            (folder / "correctness.txt").write_text("TRUE\n")
            (discovery if index % 10 < 5 else heldout).append(f"{index:06d}")
        return discovery, heldout

    def test_individual_solution_and_disjoint_split(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            discovery, heldout = self.fixture(root)
            train, test = load_split(root, discovery, heldout)
            alternate = load_examples(root, [discovery[0] + ":1"])[0]
            self.assertEqual(alternate.proof, "Alternative 0")
            self.assertEqual(alternate.metadata()["artifact"], "original_data.solution[1]")
            self.assertEqual(train[0].proof, "Model proof 0")
            self.assertEqual(train[0].metadata()["artifact"], "full_response")
            self.assertIs(train[0].metadata()["correctness"], True)
            self.assertEqual(train[0].metadata()["correctness_label"], "TRUE")
            self.assertFalse({p.example_id for p in train} & {p.example_id for p in test})

    def test_load_more_than_five_evaluation_examples(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            discovery, heldout = self.fixture(root)
            loaded = load_examples(root, discovery + heldout)
            self.assertEqual(len(loaded), 40)

    def test_balanced_split_rejects_incorrect_and_topic_imbalance(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            discovery, heldout = self.fixture(root)
            (root / discovery[0] / "correctness.txt").write_text("FALSE\n")
            with self.assertRaisesRegex(ValueError, "does not mark.*correct"):
                load_split(root, discovery, heldout)
            (root / discovery[0] / "correctness.txt").write_text("TRUE\n")
            metadata_path = root / discovery[0] / "metadata.json"
            metadata = json.loads(metadata_path.read_text())
            metadata["original_data"]["subfield"] = "Geometry"
            metadata_path.write_text(json.dumps(metadata))
            with self.assertRaisesRegex(ValueError, "per Olympiad topic"):
                load_split(root, discovery, heldout)

    def test_balanced_manifest_loads_twenty_unique_correct_proofs_per_split(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            discovery, heldout = self.fixture(root)
            topics = ("Algebra", "Combinatorics", "Geometry", "Number Theory")
            manifest = {"proof_artifact": "full_response", "correctness_label": "TRUE",
                        "proofs_per_topic_per_split": 5, "discovery": {}, "heldout": {}}
            for offset, topic in enumerate(topics):
                manifest["discovery"][topic] = discovery[offset * 5:(offset + 1) * 5]
                manifest["heldout"][topic] = heldout[offset * 5:(offset + 1) * 5]
            path = root / "split.json"
            path.write_text(json.dumps(manifest))
            train, test = load_split_manifest(root, path)
            self.assertEqual((len(train), len(test)), (20, 20))
            self.assertEqual(len({example.example_id for example in train + test}), 40)
            self.assertTrue(all(example.correctness for example in train + test))

    def test_generic_pipeline_dry_run_accepts_adapter_examples(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            discovery, heldout = self.fixture(root / "dataset")
            train, test = load_split(root / "dataset", discovery, heldout)
            output = root / "run"
            run_strategy_transfer(discovery=train, heldout=test, storage_dir=output,
                                  discovery_attempts=2, evaluation_attempts_per_proof=3,
                                  provider="claude-code", model="sonnet", dry_run=True)
            manifest = json.loads((output / "manifest.json").read_text())
            self.assertEqual(manifest["provider"], "claude-code")
            self.assertEqual(manifest["model"], "sonnet")
            self.assertEqual(set(manifest["role_providers"].values()), {"claude-code"})
            self.assertEqual(manifest["discovery_attempts_per_proof"], 2)
            self.assertEqual(manifest["evaluation_attempts_per_proof_per_arm"], 3)

    def test_gemini_pipeline_manifest_records_all_roles_and_effort_limitation(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            discovery, heldout = self.fixture(root / "dataset")
            train, test = load_split(root / "dataset", discovery, heldout)
            output = root / "run"
            run_strategy_transfer(
                discovery=train, heldout=test, storage_dir=output,
                provider="gemini-cli", model="gemini-3.5-flash",
                reasoning_effort="medium", dry_run=True,
            )
            manifest = json.loads((output / "manifest.json").read_text())
            self.assertEqual(manifest["provider"], "gemini-cli")
            self.assertEqual(set(manifest["role_providers"].values()), {"gemini-cli"})
            self.assertIsNone(manifest["reasoning_effort"])
            self.assertEqual(manifest["requested_reasoning_effort"], "medium")
            self.assertFalse(manifest["provider_supports_reasoning_effort"])


if __name__ == "__main__":
    unittest.main()
