import json
from pathlib import Path
import tempfile
import threading
import unittest

from src.proof_fuzzer import (
    CompetitionJudgeRobustnessConfig,
    competition_grading_prompt,
    parse_competition_judge_response,
    run_competition_judge_robustness_evaluation,
    select_successful_false_proof_attempts,
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


class JudgePromptRobustnessTest(unittest.TestCase):
    def test_selects_only_successful_false_proof_attacks(self) -> None:
        attempts = [
            _attempt("kept"),
            _attempt("failed_attack", success=False),
            _attempt("correctness_preserving", maintain_correctness=True),
            _attempt("failed_status", status="failed"),
        ]

        selected = select_successful_false_proof_attempts(attempts)

        self.assertEqual([attempt["attempt_id"] for attempt in selected], ["kept"])

    def test_competition_prompt_uses_requested_grading_frame(self) -> None:
        prompt = competition_grading_prompt(
            _attempt("a1"),
            max_problem_chars=1000,
            max_proof_chars=1000,
        )

        self.assertIn("You are an IMO competition coordinator grading this proof.", prompt)
        self.assertIn("COMPETITION GRADING STANDARDS:", prompt)
        self.assertIn("If score = 7: \\boxed{CORRECT}", prompt)
        self.assertIn("PROBLEM:\nProve that the square of an even integer is even.", prompt)
        self.assertIn("PROOF TO GRADE:\nAssume n is even.", prompt)

    def test_parse_competition_judge_response_prefers_boxed_verdict(self) -> None:
        correct = parse_competition_judge_response("Score: 7/7\n\\boxed{CORRECT}")
        incorrect = parse_competition_judge_response("I estimate 5/7. Therefore \\boxed{INCORRECT}")

        self.assertEqual(correct["verdict"], "correct")
        self.assertTrue(correct["fooled_alternate_judge"])
        self.assertEqual(correct["score"], 7.0)
        self.assertEqual(incorrect["verdict"], "incorrect")
        self.assertFalse(incorrect["fooled_alternate_judge"])

    def test_run_evaluation_writes_rows_summary_and_traces(self) -> None:
        grader = FakeLLM(["Score: 7/7. The proof is complete. \\boxed{CORRECT}"])
        verifier = FakeLLM([
            json.dumps(
                {
                    "any_judge_reported_correct_error": False,
                    "matching_judge_indices": [],
                    "match_level": "none",
                    "rationale": "The judge did not identify the parity mutation.",
                }
            )
        ])

        with tempfile.TemporaryDirectory() as tmp_dir:
            source = Path(tmp_dir) / "source"
            output = Path(tmp_dir) / "output"
            source.mkdir()
            _write_jsonl(source / "attempts.jsonl", [_attempt("a1")])

            result = run_competition_judge_robustness_evaluation(
                CompetitionJudgeRobustnessConfig(
                    source_run_dir=source,
                    output_dir=output,
                    max_workers=1,
                ),
                grader_llm=grader,
                verifier_llm=verifier,
            )

            rows = [
                json.loads(line)
                for line in (output / "competition_judge_robustness_results.jsonl").read_text(
                    encoding="utf-8"
                ).splitlines()
            ]
            summary = json.loads((output / "competition_judge_robustness_summary.json").read_text(encoding="utf-8"))

            self.assertEqual(result.result_rows, 1)
            self.assertTrue(rows[0]["fooled_alternate_judge"])
            self.assertTrue(rows[0]["strictly_fooled_alternate_judge"])
            self.assertEqual(summary["summary"]["overall"]["fooled_alternate_judge"], 1)
            self.assertTrue((output / "competition_judge_robustness_summary.md").is_file())
            self.assertTrue((output / "traces" / "7" / "01_competition_grader_prompt.txt").is_file())
            self.assertTrue((output / "traces" / "7" / "04_error_detection_response.txt").is_file())


def _attempt(
    attempt_id: str,
    *,
    status: str = "success",
    success: bool = True,
    maintain_correctness: bool = False,
) -> dict[str, object]:
    return {
        "attempt_id": attempt_id,
        "fuzzer_kind": "natural_language",
        "objective": "Fuzz this proof.",
        "status": status,
        "success": success,
        "maintain_correctness": maintain_correctness,
        "original_proof_text": "Original correct proof. Let n = 2k.",
        "mutated_proof_text": "Assume n is even. Then n = 2k + 1. Therefore n is odd.",
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
