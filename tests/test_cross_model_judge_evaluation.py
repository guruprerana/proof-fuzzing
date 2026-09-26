import hashlib
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from scripts.run_cross_model_judge_evaluation import (
    SourceRun,
    candidate_index,
    reconcile_manifest,
    resolve_artifacts,
    select_rows,
    session_index,
    summarize,
)


def row(*, mutation_hash, misses, proof_id="proof", candidate=1, session=1,
        arm="strategies", valid=True):
    return {
        "arm": arm,
        "valid": valid,
        "mutation_sha256": mutation_hash,
        "proof_id": proof_id,
        "candidate": candidate,
        "session_index": session,
        "reviews": [
            {"detection": "missed" if index < misses else "caught"}
            for index in range(3)
        ],
    }


class CrossModelSelectionTests(unittest.TestCase):
    def test_select_rows_ranks_misses_and_deduplicates_hashes(self):
        hashes = [f"{number:064x}" for number in range(1, 8)]
        rows = [
            row(mutation_hash=hashes[0], misses=1, proof_id="b"),
            row(mutation_hash=hashes[1], misses=3, proof_id="z"),
            row(mutation_hash=hashes[2], misses=2, proof_id="a"),
            row(mutation_hash=hashes[1], misses=3, proof_id="z", candidate=2),
            row(mutation_hash=hashes[3], misses=3, proof_id="a"),
            row(mutation_hash=hashes[4], misses=3, arm="generic"),
            row(mutation_hash=hashes[5], misses=3, valid=False),
            {**row(mutation_hash=hashes[6], misses=3), "mutation_sha256": "bad"},
        ]
        selected = select_rows(rows, 4)
        self.assertEqual(
            [item["mutation_sha256"] for item in selected],
            [hashes[3], hashes[1], hashes[2], hashes[0]],
        )
        self.assertEqual(
            [item["original_missed_reviews"] for item in selected],
            [3, 3, 2, 1],
        )

    def test_select_rows_requires_requested_number(self):
        with self.assertRaisesRegex(ValueError, "need 2"):
            select_rows([row(mutation_hash=f"{1:064x}", misses=3)], 2)

    def test_resolve_artifacts_uses_archive_not_mutator_workspace(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            archive = root / "run/sessions/0001/attempts/001"
            workspace = root / "run/sessions/0001/mutator_workspace/attempts/001"
            archive.mkdir(parents=True)
            workspace.mkdir(parents=True)
            content = "mutated proof"
            (archive / "mutated_proof.md").write_text(content)
            (workspace / "mutated_proof.md").write_text(content)
            mutation_hash = hashlib.sha256(content.encode()).hexdigest()
            source = SourceRun(
                "dataset", "Dataset", "codex", "gpt-5.6-sol",
                Path("run/results.json"), (Path("run"),),
            )
            with patch(
                "scripts.run_cross_model_judge_evaluation.REPOSITORY_ROOT", root
            ):
                resolved = resolve_artifacts(source, {mutation_hash})
            self.assertEqual(resolved[mutation_hash], archive)

    def test_resolve_artifacts_supports_legacy_flat_attempts(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            archive = root / "run/attempts/019"
            archive.mkdir(parents=True)
            content = "legacy mutated proof"
            (archive / "mutated_proof.md").write_text(content)
            mutation_hash = hashlib.sha256(content.encode()).hexdigest()
            source = SourceRun(
                "dataset", "Dataset", "codex", "gpt-5.6-sol",
                Path("run/results.json"), (Path("run"),),
            )
            with patch(
                "scripts.run_cross_model_judge_evaluation.REPOSITORY_ROOT", root
            ):
                resolved = resolve_artifacts(source, {mutation_hash})
            self.assertEqual(resolved[mutation_hash], archive)

    def test_legacy_candidate_and_session_indices(self):
        legacy = {"repeat": 4, "attempt": 19}
        self.assertEqual(candidate_index(legacy), 4)
        self.assertEqual(session_index(legacy), 19)

    def test_summarize_groups_cross_judge_outcomes(self):
        results = [
            {
                "key": "a", "status": "completed", "detection": "caught",
                "dataset_key": "olympiad", "dataset": "Olympiad",
                "source_model": "gpt-5.6-sol", "target_model": "claude-opus-5",
            },
            {
                "key": "b", "status": "completed", "detection": "missed",
                "dataset_key": "olympiad", "dataset": "Olympiad",
                "source_model": "gpt-5.6-sol", "target_model": "claude-opus-5",
            },
            {
                "key": "c", "status": "failed", "dataset_key": "recent_math",
                "dataset": "ArXivMath",
                "source_model": "claude-opus-5", "target_model": "gpt-5.6-sol",
            },
        ]
        summary = summarize(results, 3)
        self.assertFalse(summary["complete"])
        self.assertEqual(summary["completed"], 2)
        self.assertEqual(summary["failed"], 1)
        self.assertEqual(summary["caught"], 1)
        self.assertEqual(summary["missed"], 1)
        self.assertEqual(
            summary["cells"]["olympiad__from_gpt-5.6-sol"]["completed"], 2
        )

    def test_reconcile_manifest_records_timeout_removal(self):
        recorded = {"created_at": "old", "workers": 40, "call_timeout_seconds": 1200}
        requested = {"created_at": "new", "workers": 40, "call_timeout_seconds": None}
        amended, changed = reconcile_manifest(recorded, requested, 57)
        self.assertTrue(changed)
        self.assertIsNone(amended["call_timeout_seconds"])
        self.assertEqual(
            amended["protocol_amendments"][-1]["completed_candidates_before_amendment"],
            57,
        )

    def test_reconcile_manifest_rejects_other_changes(self):
        recorded = {"workers": 40, "call_timeout_seconds": 1200}
        requested = {"workers": 20, "call_timeout_seconds": None}
        with self.assertRaisesRegex(ValueError, "does not match"):
            reconcile_manifest(recorded, requested, 57)


if __name__ == "__main__":
    unittest.main()
