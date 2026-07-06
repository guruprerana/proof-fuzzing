import json
from pathlib import Path
import tempfile
import threading
import unittest

from src.proof_fuzzer import (
    EvolutionConfig,
    ProofBenchJudgeEvolutionRunConfig,
    infer_math_topic,
    load_correct_proof_bench_judge_examples,
    run_proof_bench_judge_evolution,
    run_proof_bench_judge_evolutionary_pipeline,
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
            response = self.responses.pop(0)
            if isinstance(response, Exception):
                raise response
            return response


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


class ProofBenchJudgePipelineTest(unittest.TestCase):
    def test_load_correct_examples_filters_yes_answers(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            _write_example(root / "000000", answer="Yes", proof="Correct proof.")
            _write_example(root / "000001", answer="No", proof="Incorrect proof.")

            examples = load_correct_proof_bench_judge_examples(root)

            self.assertEqual([example.example_id for example in examples], ["000000"])
            self.assertEqual(examples[0].proof, "Correct proof.")
            self.assertEqual(examples[0].problem, "Prove the claim.")

    def test_topic_inference_uses_problem_text(self) -> None:
        self.assertEqual(infer_math_topic("triangle angle circle cyclic"), "geometry")
        self.assertEqual(infer_math_topic("polynomial coefficient monic roots"), "algebra")

    def test_complete_run_entrypoint_uses_metadata_proof(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir) / "dataset"
            storage = Path(tmp_dir) / "storage"
            _write_example(root / "000000", answer="Yes", proof="First step.\n\nSecond step.")
            llm = FakeLLM([JUDGE_RESPONSE, MUTATION_RESPONSE, JUDGE_RESPONSE])

            result = run_proof_bench_judge_evolution(
                ProofBenchJudgeEvolutionRunConfig(
                    root=root,
                    storage_dir=storage,
                    num_attempts=1,
                    correctness_selection_mode="false_proof",
                    evolution_threshold=0,
                    strategy_probability=0.0,
                ),
                llm=llm,
            )

            self.assertEqual(len(result.attempts), 1)
            self.assertEqual(result.attempts[0].metadata["dataset"], "proof_bench_judge")
            self.assertEqual(result.attempts[0].metadata["proof_source"], "metadata.original_data.proof")
            self.assertTrue((storage / "run_config.json").is_file())

    def test_pipeline_stops_after_usage_limit_failure(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir) / "dataset"
            storage = Path(tmp_dir) / "storage"
            for index in range(3):
                _write_example(root / f"{index:06d}", answer="Yes", proof=f"Proof {index}.")
            llm = FakeLLM([
                JUDGE_RESPONSE,
                RuntimeError("You've hit your usage limit. Visit settings to purchase more credits."),
                JUDGE_RESPONSE,
                MUTATION_RESPONSE,
                JUDGE_RESPONSE,
            ])
            config = EvolutionConfig(
                storage_dir=storage,
                strategy_injection_probability=0.0,
                evolution_threshold=0,
                correctness_selection_mode="false_proof",
                continue_on_error=True,
            )

            attempts = run_proof_bench_judge_evolutionary_pipeline(
                llm=llm,
                root=root,
                config=config,
                max_workers=1,
                num_attempts=3,
            )

            self.assertEqual(len(attempts), 1)
            self.assertEqual(attempts[0].status, "failed")
            self.assertIn("usage limit", attempts[0].error.lower())
            self.assertEqual(len((storage / "attempts.jsonl").read_text(encoding="utf-8").splitlines()), 1)


def _write_example(path: Path, *, answer: str, proof: str, problem: str = "Prove the claim.") -> None:
    path.mkdir(parents=True)
    metadata = {
        "idx": int(path.name),
        "original_data": {
            "problem_id": f"PBJ-{path.name}",
            "problem": problem,
            "proof": proof,
            "rubric": "Award full credit for a correct proof.",
        },
        "ground_truth": {"answer": answer},
    }
    (path / "metadata.json").write_text(json.dumps(metadata), encoding="utf-8")
    (path / "prompt.txt").write_text(problem, encoding="utf-8")
    (path / "response.txt").write_text(f"Judgement: {answer}", encoding="utf-8")
    (path / "ground_truth.txt").write_text(answer, encoding="utf-8")


if __name__ == "__main__":
    unittest.main()
