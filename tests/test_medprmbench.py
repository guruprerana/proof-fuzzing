from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

from src.proof_fuzzer import (
    DEFAULT_MEDPRMBENCH_MUTATION_POLICY,
    MEDPRM_ERROR_TYPES,
    MedPRMBenchPromptExperimentConfig,
    extract_medprmbench_paper_examples,
    load_medprmbench_traces,
    normalize_medprmbench_row,
    run_medprmbench_prompt_evolution_experiment,
)


EVOLVED_POLICY = """Goal:
Create a subtle clinical reasoning degradation.

Strategies:
- Break one medically important dependency while preserving presentation.

Do not:
- Reveal the edit or introduce unrelated errors.

Before returning:
1. Confirm the requested failure is real and material."""


class FakeMedicalLLM:
    def __init__(self) -> None:
        self.prompts: list[str] = []

    def complete(self, prompt: str) -> str:
        self.prompts.append(prompt)
        if "Rewrite the complete prompt" in prompt:
            return json.dumps(
                {"prompt_text": EVOLVED_POLICY, "change_summary": "Target dependencies."}
            )
        if "strict white-box validator" in prompt:
            return json.dumps(
                {
                    "valid": True,
                    "minimal": True,
                    "independent_failure_count": 1,
                    "exposure_count": 1,
                    "severity": "material",
                    "detected_failure": "The changed step applies the wrong clinical rule.",
                    "rationale": "The clean chain does not contain that error.",
                }
            )
        if "strict white-box matcher" in prompt:
            return json.dumps(
                {
                    "introduced_error_found": False,
                    "matching_error_indices": [],
                    "match_level": "none",
                    "rationale": "The inventory missed the planted clinical error.",
                }
            )
        if "medical-reasoning error finder" in prompt:
            return json.dumps(
                {
                    "errors": [],
                    "review_summary": "Checked every clinical reasoning step.",
                }
            )
        if "controlled failure cases for clinical-reasoning" in prompt:
            trace_text = prompt.split("--- BEGIN trace.json ---\n", 1)[1].split(
                "\n--- END trace.json ---", 1
            )[0]
            clean = json.loads(trace_text)["clean_editable_unit"]
            return json.dumps(
                {
                    "mutated_unit": clean.replace("supports", "rules out", 1),
                    "rationale": "Reverse an important clinical inference.",
                    "expected_failure": "A finding is interpreted in the wrong direction.",
                }
            )
        raise AssertionError("Unexpected prompt type")


def _canonical_row(index: int, code: str = "R-1") -> dict[str, object]:
    return {
        "variant_id": f"variant-{index}:{code}",
        "case_id": f"case-{index}",
        "question": f"Clinical question {index}?",
        "original_steps": ["Finding A supports diagnosis B.", "Therefore choose treatment C."],
        "modified_steps": ["Finding A rules out diagnosis B.", "Therefore choose treatment C."],
        "error_step_indices": [0],
        "index_base": 0,
        "error_types": [code],
        "severity": "Major",
        "source_dataset": "fixture",
        "split": "paper",
    }


class MedPRMBenchTest(unittest.TestCase):
    def test_initial_medical_policy_encourages_single_cause_propagation(self) -> None:
        self.assertIn("Propagate the altered fact", DEFAULT_MEDPRMBENCH_MUTATION_POLICY)
        self.assertIn("same medical reasoning error", DEFAULT_MEDPRMBENCH_MUTATION_POLICY)
        self.assertIn("wherever coherence requires it", DEFAULT_MEDPRMBENCH_MUTATION_POLICY)

    def test_normalizes_canonical_and_release_style_rows(self) -> None:
        canonical = normalize_medprmbench_row(_canonical_row(1))
        self.assertEqual(canonical.error_step_indices, (0,))
        self.assertEqual(canonical.primary_error_type, "R-1")

        release_style = normalize_medprmbench_row(
            {
                "id": "variant-2",
                "instance_id": "case-2",
                "query": "Which diagnosis is most likely?",
                "positive": {"steps": [{"text": "Clue supports A."}, {"text": "Choose A."}]},
                "negative": {"steps": [{"text": "Clue supports B."}, {"text": "Choose A."}]},
                "step_labels": [-1, 1],
                "primary_error_type": "R-3 Contextual Applicability",
                "dataset_type": "MedQA-USMLE",
            }
        )
        self.assertEqual(release_style.case_id, "case-2")
        self.assertEqual(release_style.error_step_indices, (0,))
        self.assertEqual(release_style.error_types, ("R-3",))

        one_based = normalize_medprmbench_row(
            {
                **_canonical_row(3),
                "error_step_indices": None,
                "error_steps": [1],
                "index_base": None,
            }
        )
        self.assertEqual(one_based.error_step_indices, (0,))

    def test_loads_jsonl_and_preserves_case_grouping(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "paper_examples.jsonl"
            rows = [_canonical_row(1), _canonical_row(2, "E-1")]
            path.write_text("".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8")

            traces = load_medprmbench_traces(path)

            self.assertEqual(len(traces), 2)
            self.assertEqual(traces[0].split, "paper")
            example = traces[0].to_prompt_evolution_example()
            self.assertEqual(example.trace_id, "case-1")
            self.assertIn("Evidence-Based Soundness", example.perturbation_type)
            self.assertIn("Step 2:", example.original_candidate)

    def test_extracts_all_fourteen_appendix_boxes(self) -> None:
        boxes = []
        for error_type in MEDPRM_ERROR_TYPES:
            boxes.append(
                rf"""
\begin{{tcolorbox}}[examplebox, title={{{error_type.code}: {error_type.name} \hfill \texttt{{case\_1}}}}]
\textbf{{Question:}} A clinical question?
\tcblower
\textbf{{1. Original Process}}
\textbf{{Step 1:}} A finding supports the diagnosis.
\textbf{{Step 2:}} The conclusion follows.
\smallskip
\textbf{{2. Modified Process}}
\colorbox{{red!8}}{{\parbox[t]{{x}}{{\textbf{{Step 1:}} A finding rules out the diagnosis. \hfill$\leftarrow$ \textit{{error}}}}}}
\textbf{{Step 2:}} The conclusion follows.
\smallskip
\textbf{{3. Reason}}
The inference is reversed.
\end{{tcolorbox}}
"""
            )
        tex = r"\section{Error Type Examples}" + "".join(boxes)

        rows = extract_medprmbench_paper_examples(tex)

        self.assertEqual(len(rows), 14)
        self.assertEqual(rows[0]["case_id"], "case_1")
        self.assertEqual(rows[0]["error_step_indices"], [0])

    def test_runs_case_disjoint_prompt_evolution_experiment(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            dataset = Path(tmp) / "paper_examples.jsonl"
            rows = [_canonical_row(index, ("R-1", "R-3", "E-1", "E-4")[index % 4]) for index in range(8)]
            dataset.write_text(
                "".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8"
            )
            llm = FakeMedicalLLM()
            result = run_medprmbench_prompt_evolution_experiment(
                llm=llm,
                config=MedPRMBenchPromptExperimentConfig(
                    storage_dir=Path(tmp) / "run",
                    dataset_file=str(dataset),
                    train_examples=2,
                    test_examples=2,
                    test_attempts_per_example=2,
                    training_generations=1,
                    split_seed=3,
                    evaluation_seed=4,
                    max_workers=1,
                ),
            )

            inner = result.experiment
            self.assertEqual(len(inner.training_attempts), 2)
            self.assertEqual(len(inner.baseline_attempts), 4)
            self.assertEqual(len(inner.learned_attempts), 4)
            self.assertTrue(all(not a.introduced_error_found for a in inner.baseline_attempts))
            self.assertTrue(
                all(len(a.original_judge_results) == 1 for a in inner.baseline_attempts)
            )
            self.assertFalse(set(inner.train_trace_ids) & set(inner.test_trace_ids))
            self.assertEqual(inner.learned_prompt.prompt_text, EVOLVED_POLICY)
            manifest = json.loads((Path(tmp) / "run/dataset_manifest.json").read_text())
            self.assertEqual(manifest["paper_url"], "https://arxiv.org/abs/2604.17282")
            self.assertIn("clinical reasoning", "\n".join(llm.prompts).lower())


if __name__ == "__main__":
    unittest.main()
