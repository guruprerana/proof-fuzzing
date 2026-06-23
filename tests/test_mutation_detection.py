import json
from pathlib import Path
import tempfile
import threading
import unittest

from src.proof_fuzzer import (
    MutationDetectionExperimentConfig,
    blind_detection_prompt,
    mutation_aware_detection_prompt,
    run_mutation_detection_experiment,
    select_detection_attempts,
)


class FakeLLM:
    def __init__(self, responses):
        self.responses = list(responses)
        self.prompts = []
        self.lock = threading.Lock()

    def complete(self, prompt: str) -> str:
        with self.lock:
            self.prompts.append(prompt)
            if not self.responses:
                raise AssertionError("No fake LLM response is available.")
            return self.responses.pop(0)


class MutationDetectionTest(unittest.TestCase):
    def test_select_detection_attempts_requires_completed_mutation_attempts(self) -> None:
        attempts = [
            _attempt("kept", status="success"),
            _attempt("failed", status="failed"),
            _attempt("missing", mutations=[]),
        ]

        selected = select_detection_attempts(attempts)

        self.assertEqual([attempt["attempt_id"] for attempt in selected], ["kept"])

    def test_detection_prompts_keep_blind_condition_blind(self) -> None:
        attempt = _attempt("a1")

        blind_prompt = blind_detection_prompt(
            attempt,
            max_problem_chars=1000,
            max_rubric_chars=1000,
            max_proof_chars=1000,
        )
        aware_prompt = mutation_aware_detection_prompt(
            attempt,
            max_problem_chars=1000,
            max_rubric_chars=1000,
            max_proof_chars=1000,
        )

        self.assertIn("Submitted proof:", blind_prompt)
        self.assertNotIn("mutation", blind_prompt.lower())
        self.assertNotIn("introduced", blind_prompt.lower())
        self.assertNotIn("Original correct proof", blind_prompt)
        self.assertIn("introduced mutation/error", aware_prompt)
        self.assertIn("Mutated proof:", aware_prompt)
        self.assertNotIn("Original correct proof", aware_prompt)

    def test_run_experiment_writes_two_conditions_and_summary(self) -> None:
        detector = FakeLLM([
            '{"verdict": "incorrect", "detected_flaw": "bad parity step"}',
            '{"verdict": "incorrect", "detected_flaw": "bad parity step"}',
        ])
        adjudicator = FakeLLM([
            '{"detected_correct_error": true, "match_level": "exact", "specificity": 1.0, "localization": 1.0}',
            '{"detected_correct_error": true, "match_level": "exact", "specificity": 1.0, "localization": 1.0}',
        ])

        with tempfile.TemporaryDirectory() as tmp_dir:
            source = Path(tmp_dir) / "source"
            output = Path(tmp_dir) / "output"
            source.mkdir()
            _write_jsonl(source / "attempts.jsonl", [_attempt("a1")])

            result = run_mutation_detection_experiment(
                MutationDetectionExperimentConfig(
                    source_run_dir=source,
                    output_dir=output,
                    target_attempts=1,
                    wait_for_target_attempts=False,
                    max_workers=1,
                ),
                detector_llm=detector,
                adjudicator_llm=adjudicator,
            )

            rows = [
                json.loads(line)
                for line in (output / "detection_results.jsonl").read_text(encoding="utf-8").splitlines()
            ]
            summary = json.loads((output / "detection_summary.json").read_text(encoding="utf-8"))

            self.assertEqual(result.result_rows, 2)
            self.assertEqual({row["condition"] for row in rows}, {"blind", "mutation_aware"})
            self.assertEqual({row["metadata"]["math_topic"] for row in rows}, {"algebra"})
            self.assertEqual(summary["summary"]["by_condition"]["blind"]["correct"], 1)
            self.assertTrue((output / "detection_summary.md").is_file())
            self.assertTrue((output / "traces" / "a1_blind.json").is_file())
            self.assertTrue((output / "traces" / "a1_mutation_aware.json").is_file())


def _attempt(attempt_id: str, *, status: str = "success", mutations=None) -> dict[str, object]:
    if mutations is None:
        mutations = [{"summary": "Change even to odd.", "target": "S2"}]
    return {
        "attempt_id": attempt_id,
        "status": status,
        "success": True,
        "original_proof_text": "Original correct proof. Let n = 2k.",
        "mutated_proof_text": "Assume n is even. Then n = 2k + 1. Therefore n is odd.",
        "mutation_instructions": {
            "rationale": "Introduce a parity representation slip.",
            "mutations": mutations,
        },
        "mutation_check_result": {
            "detected_flaw": "An even integer cannot be represented as 2k + 1.",
        },
        "strategy_ids": ["s1"],
        "metadata": {
            "example_id": "ex1",
            "sample_index": 0,
            "llm_category": "algebra",
            "problem": "Prove that the square of an even integer is even.",
            "rubric": "Award credit for correctly using n=2k.",
            "strategy_selection": {
                "selected_strategy_sources": ["mined"],
            },
        },
    }


def _write_jsonl(path: Path, rows: list[dict[str, object]]) -> None:
    path.write_text(
        "".join(json.dumps(row, sort_keys=True) + "\n" for row in rows),
        encoding="utf-8",
    )


if __name__ == "__main__":
    unittest.main()
