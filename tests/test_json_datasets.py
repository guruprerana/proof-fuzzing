import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from src.proof_fuzzer.datasets.json_split import load_json_split
from src.proof_fuzzer.strategy_transfer import run_strategy_transfer


class JSONDatasetTest(unittest.TestCase):
    def test_portable_split(self):
        with TemporaryDirectory() as temporary:
            path = Path(temporary) / "split.json"
            path.write_text(json.dumps({
                "discovery": [{"example_id": "a", "problem": "P", "proof": "A"}],
                "heldout": [{"example_id": "b", "problem": "Q", "proof": "B"}],
            }))
            discovery, heldout = load_json_split(path)
            self.assertEqual(discovery[0].proof, "A")
            self.assertEqual(heldout[0].example_id, "b")

    def test_discovery_only_split_can_have_no_heldout_examples(self):
        with TemporaryDirectory() as temporary:
            path = Path(temporary) / "split.json"
            path.write_text(json.dumps({
                "discovery": [{"example_id": "a", "problem": "P", "proof": "A"}],
                "heldout": [],
            }))
            with self.assertRaisesRegex(ValueError, "nonempty list"):
                load_json_split(path)
            discovery, heldout = load_json_split(path, allow_empty_heldout=True)
            self.assertEqual([example.example_id for example in discovery], ["a"])
            self.assertEqual(heldout, [])

    def test_discovery_dry_run_records_claude_roles(self):
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            path = root / "split.json"
            path.write_text(json.dumps({
                "discovery": [{"example_id": "a", "problem": "P", "proof": "A"}],
                "heldout": [{"example_id": "b", "problem": "Q", "proof": "B"}],
            }))
            discovery, heldout = load_json_split(path)
            output = root / "run"
            run_strategy_transfer(
                discovery=discovery,
                heldout=heldout,
                storage_dir=output,
                discovery_attempts=2,
                provider="claude-code",
                model="claude-opus-5",
                dry_run=True,
            )
            manifest = json.loads((output / "manifest.json").read_text())
            self.assertEqual(manifest["run_mode"], "discovery_and_distillation_only")
            self.assertEqual(manifest["model"], "claude-opus-5")
            self.assertEqual(set(manifest["role_providers"].values()), {"claude-code"})


if __name__ == "__main__":
    unittest.main()
