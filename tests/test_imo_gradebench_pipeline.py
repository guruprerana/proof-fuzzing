import json
from pathlib import Path
import threading
import tempfile
import unittest

from src.proof_fuzzer import (
    EvolutionConfig,
    load_correct_imo_gradebench_examples,
    run_imo_gradebench_evolutionary_pipeline,
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


MUTATION_RESPONSE = """{
  "maintain_correctness": false,
  "rationale": "Introduce a subtle invalid inference.",
  "mutations": [
    {
      "kind": "modify",
      "target": "S1",
      "summary": "Make the first step invalid.",
      "new_text": "Assume the desired conclusion immediately.",
      "affected_blocks": [],
      "propagate_downstream": false
    }
  ]
}"""

JUDGE_RESPONSE = """{
  "verdict": "correct",
  "confidence": 0.7,
  "rationale": "The proof appears acceptable.",
  "detected_flaw": ""
}"""


class IMOGradeBenchPipelineTest(unittest.TestCase):
    def test_load_correct_examples_filters_by_correctness_txt(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            _write_example(root / "000001", correctness="TRUE", response="Correct proof.")
            _write_example(root / "000002", correctness="FALSE", response="Incorrect proof.")

            examples = load_correct_imo_gradebench_examples(root)

            self.assertEqual([example.example_id for example in examples], ["000001"])
            self.assertEqual(examples[0].problem, "Prove the claim.")
            self.assertEqual(examples[0].response, "Correct proof.")

    def test_runner_records_attempt_metadata_for_correct_examples_only(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir) / "dataset"
            storage = Path(tmp_dir) / "storage"
            _write_example(root / "000001", correctness="TRUE", response="First step.\n\nSecond step.")
            _write_example(root / "000002", correctness="FALSE", response="Should not run.")
            llm = FakeLLM([JUDGE_RESPONSE, MUTATION_RESPONSE, JUDGE_RESPONSE])
            config = EvolutionConfig(
                storage_dir=storage,
                strategy_injection_probability=0.0,
                evolution_threshold=0,
                correctness_selection_mode="false_proof",
            )

            attempts = run_imo_gradebench_evolutionary_pipeline(
                llm=llm,
                root=root,
                config=config,
            )

            self.assertEqual(len(attempts), 1)
            self.assertEqual(attempts[0].metadata["dataset"], "imo_gradebench")
            self.assertEqual(attempts[0].metadata["example_id"], "000001")
            self.assertIn("Problem:\n```text\nProve the claim.", llm.prompts[0])

    def test_runner_parallelizes_multiple_attempts(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir) / "dataset"
            storage = Path(tmp_dir) / "storage"
            _write_example(root / "000001", correctness="TRUE", response="First proof step.")
            _write_example(root / "000002", correctness="TRUE", response="Second proof step.")
            responses = []
            for _ in range(4):
                responses.extend([JUDGE_RESPONSE, MUTATION_RESPONSE, JUDGE_RESPONSE])
            llm = FakeLLM(responses)
            config = EvolutionConfig(
                storage_dir=storage,
                strategy_injection_probability=0.0,
                evolution_threshold=0,
                correctness_selection_mode="false_proof",
            )

            attempts = run_imo_gradebench_evolutionary_pipeline(
                llm=llm,
                root=root,
                config=config,
                max_workers=2,
                attempts_per_example=2,
            )

            self.assertEqual(len(attempts), 4)
            self.assertEqual([attempt.metadata["example_id"] for attempt in attempts], ["000001", "000001", "000002", "000002"])
            self.assertEqual([attempt.metadata["example_attempt_index"] for attempt in attempts], [0, 1, 0, 1])
            self.assertEqual(len((storage / "attempts.jsonl").read_text(encoding="utf-8").splitlines()), 4)

    def test_runner_randomly_samples_total_attempt_count_from_natural_language_proofs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir) / "dataset"
            storage = Path(tmp_dir) / "storage"
            _write_example(root / "000001", correctness="TRUE", response="First proof step.")
            _write_example(root / "000002", correctness="TRUE", response="Second proof step.")
            _write_example(root / "000003", correctness="FALSE", response="Should not run.")
            responses = []
            for _ in range(5):
                responses.extend([JUDGE_RESPONSE, MUTATION_RESPONSE, JUDGE_RESPONSE])
            llm = FakeLLM(responses)
            config = EvolutionConfig(
                storage_dir=storage,
                strategy_injection_probability=0.0,
                evolution_threshold=0,
                correctness_selection_mode="false_proof",
                random_seed=7,
            )

            attempts = run_imo_gradebench_evolutionary_pipeline(
                llm=llm,
                root=root,
                config=config,
                max_workers=2,
                num_attempts=5,
            )

            self.assertEqual(len(attempts), 5)
            self.assertTrue(all(attempt.metadata["example_id"] in {"000001", "000002"} for attempt in attempts))
            self.assertEqual([attempt.metadata["sample_index"] for attempt in attempts], list(range(5)))
            self.assertTrue(all(attempt.metadata["proof_source"] == "response.txt" for attempt in attempts))
            self.assertTrue(all(attempt.metadata["fuzzer_kind"] == "natural_language" for attempt in attempts))

    def test_runner_truncates_long_proof_and_problem_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir) / "dataset"
            storage = Path(tmp_dir) / "storage"
            _write_example(
                root / "000001",
                correctness="TRUE",
                response="A" * 200,
                problem="P" * 200,
            )
            llm = FakeLLM([JUDGE_RESPONSE, MUTATION_RESPONSE, JUDGE_RESPONSE])
            config = EvolutionConfig(
                storage_dir=storage,
                strategy_injection_probability=0.0,
                evolution_threshold=0,
                correctness_selection_mode="false_proof",
                max_proof_chars=80,
                max_problem_chars=60,
            )

            attempts = run_imo_gradebench_evolutionary_pipeline(
                llm=llm,
                root=root,
                config=config,
                num_attempts=1,
            )

            self.assertTrue(attempts[0].metadata["prompt_truncated"])
            self.assertEqual(attempts[0].metadata["proof_chars_original"], 200)
            self.assertLessEqual(attempts[0].metadata["proof_chars_used"], 80)
            self.assertIn("[... truncated for context budget ...]", llm.prompts[0])

    def test_runner_uses_distinct_seed_for_each_sampled_attempt(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir) / "dataset"
            storage = Path(tmp_dir) / "storage"
            _write_example(root / "000001", correctness="TRUE", response="First proof step.")
            responses = []
            for _ in range(8):
                responses.extend([JUDGE_RESPONSE, MUTATION_RESPONSE, JUDGE_RESPONSE])
            llm = FakeLLM(responses)
            config = EvolutionConfig(
                storage_dir=storage,
                strategy_injection_probability=0.0,
                evolution_threshold=0,
                correctness_selection_mode="fixed_probability",
                false_proof_probability=0.7,
                random_seed=20260616,
            )

            attempts = run_imo_gradebench_evolutionary_pipeline(
                llm=llm,
                root=root,
                config=config,
                num_attempts=8,
            )

            targets = {attempt.metadata["correctness_selection"]["selected"] for attempt in attempts}
            self.assertEqual(targets, {True, False})


def _write_example(path: Path, *, correctness: str, response: str, problem: str = "Prove the claim.") -> None:
    path.mkdir(parents=True)
    (path / "correctness.txt").write_text(correctness, encoding="utf-8")
    (path / "prompt.txt").write_text("Grade this proof.", encoding="utf-8")
    (path / "response.txt").write_text(response, encoding="utf-8")
    (path / "ground_truth.txt").write_text("", encoding="utf-8")
    (path / "metadata.json").write_text(
        json.dumps(
            {
                "idx": int(path.name),
                "original_data": {
                    "Grading ID": f"GB-{path.name}",
                    "Problem": problem,
                },
            }
        ),
        encoding="utf-8",
    )


if __name__ == "__main__":
    unittest.main()
