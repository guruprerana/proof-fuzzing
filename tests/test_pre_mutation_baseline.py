import json
from pathlib import Path
import tempfile
import threading
import unittest

from src.proof_fuzzer import (
    GeminiChatResult,
    PreMutationBaselineJudgeConfig,
    pre_mutation_blind_judge_prompt,
    run_pre_mutation_baseline_judge,
)


class FakeReasoningLLM:
    def __init__(self, responses):
        self.responses = list(responses)
        self.prompts = []
        self.lock = threading.Lock()

    def complete_with_reasoning(self, prompt: str) -> GeminiChatResult:
        with self.lock:
            self.prompts.append(prompt)
            if not self.responses:
                raise AssertionError("No fake LLM response is available.")
            return GeminiChatResult(content=self.responses.pop(0), reasoning="fake reasoning")


class PreMutationBaselineJudgeTest(unittest.TestCase):
    def test_prompt_uses_original_proof_blindly(self) -> None:
        prompt = pre_mutation_blind_judge_prompt(
            _attempt("a1"),
            max_problem_chars=1000,
            max_proof_chars=1000,
        )

        self.assertIn("reviewing a mathematical reasoning trace for errors", prompt)
        self.assertIn("PROBLEM:", prompt)
        self.assertIn("REASONING TRACE TO REVIEW:", prompt)
        self.assertIn('"errors": [', prompt)
        self.assertNotIn('"verdict":', prompt)
        self.assertIn("Original correct proof.", prompt)
        self.assertNotIn("Mutated bad proof.", prompt)
        self.assertNotIn("mutation", prompt.lower())

    def test_run_replay_writes_rows_summary_and_traces(self) -> None:
        llm = FakeReasoningLLM([
            json.dumps(
                {
                    "verdict": "correct",
                    "confidence": 0.9,
                    "rationale": "The original proof is sound.",
                    "detected_flaw": "",
                }
            )
        ])

        with tempfile.TemporaryDirectory() as tmp_dir:
            source = Path(tmp_dir) / "source"
            output = Path(tmp_dir) / "output"
            source.mkdir()
            _write_jsonl(source / "attempts.jsonl", [_attempt("a1")])

            result = run_pre_mutation_baseline_judge(
                PreMutationBaselineJudgeConfig(
                    source_run_dir=source,
                    output_dir=output,
                    max_workers=1,
                ),
                judge_llm=llm,
            )

            rows = [
                json.loads(line)
                for line in (output / "pre_mutation_baseline_judge_results.jsonl").read_text(
                    encoding="utf-8"
                ).splitlines()
            ]
            summary = json.loads(
                (output / "pre_mutation_baseline_judge_summary.json").read_text(encoding="utf-8")
            )

            self.assertEqual(result.result_rows, 1)
            self.assertTrue(rows[0]["baseline_judged_original_correct"])
            self.assertEqual(summary["summary"]["overall"]["original_judged_correct"], 1)
            self.assertTrue((output / "pre_mutation_baseline_judge_summary.md").is_file())
            self.assertTrue((output / "traces" / "7" / "01_pre_mutation_blind_judge_prompt.txt").is_file())
            self.assertTrue((output / "traces" / "7" / "02_pre_mutation_blind_judge_response.txt").is_file())


def _attempt(attempt_id: str) -> dict[str, object]:
    return {
        "attempt_id": attempt_id,
        "fuzzer_kind": "natural_language",
        "objective": "Fuzz this proof.",
        "status": "success",
        "success": True,
        "maintain_correctness": False,
        "original_proof_text": "Original correct proof. Let n = 2k.",
        "mutated_proof_text": "Mutated bad proof. Let n = 2k + 1.",
        "mutation_instructions": {
            "maintain_correctness": False,
            "rationale": "Introduce a parity representation slip.",
            "mutations": [
                {
                    "kind": "modify",
                    "summary": "Change even representation to odd.",
                    "target": "S2",
                    "new_text": "Then n = 2k + 1.",
                }
            ],
        },
        "judge_result": {"verdict": "correct", "confidence": 1.0},
        "strategy_ids": ["s1"],
        "metadata": {
            "example_id": "ex1",
            "sample_index": 0,
            "llm_category": "algebra",
            "trace_dir_name": "7",
            "problem": "Prove that the square of an even integer is even.",
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
