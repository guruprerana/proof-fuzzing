from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

from src.proof_fuzzer import (
    DEFAULT_REFLECT_MUTATION_POLICY,
    ReflectPromptExperimentConfig,
    load_reflect_examples,
    run_reflect_prompt_evolution_experiment,
    select_reflect_examples,
    split_reflect_examples_by_trace,
)
from src.proof_fuzzer.reflect_prompt_evolution import (
    _parse_checker,
    _parse_error_match,
)


EVOLVED_POLICY = """Goal:
Create a subtle research-agent degradation.

Strategies:
- Break one evidence-dependent relationship while preserving presentation.

Do not:
- Reveal the edit or damage unrelated content.

Before returning:
1. Confirm the failure is material.
2. Confirm the artifact remains plausible."""


class AdaptiveFakeLLM:
    def __init__(self) -> None:
        self.prompts: list[str] = []

    def complete(self, prompt: str) -> str:
        self.prompts.append(prompt)
        if "Rewrite the complete prompt" in prompt:
            return json.dumps(
                {
                    "prompt_text": EVOLVED_POLICY,
                    "change_summary": "Retain presentation while targeting evidence.",
                }
            )
        if "strict white-box validator" in prompt:
            return json.dumps(
                {
                    "valid": True,
                    "minimal": True,
                    "independent_failure_count": 1,
                    "exposure_count": 1,
                    "severity": "material",
                    "detected_failure": "The evidence relationship is now wrong.",
                    "rationale": "The change is plausible but materially degrades support.",
                }
            )
        if "strict white-box matcher" in prompt:
            return json.dumps(
                {
                    "introduced_error_found": False,
                    "matching_error_indices": [],
                    "match_level": "none",
                    "rationale": "The inventory did not identify the planted failure.",
                }
            )
        if "error finder" in prompt:
            return json.dumps(
                {
                    "errors": [],
                    "review_summary": "Checked the submitted artifact.",
                }
            )
        if "controlled failure cases" in prompt:
            trace_text = prompt.split("--- BEGIN trace.json ---\n", 1)[1].split(
                "\n--- END trace.json ---", 1
            )[0]
            clean = json.loads(trace_text)["clean_editable_unit"]
            if "Return mutated_unit as a JSON object" in prompt:
                step = json.loads(clean)
                step["content"] = {"think": "A polished but unsupported inference."}
                unit: object = step
            else:
                unit = clean + "\n\nA polished but unsupported conclusion."
            return json.dumps(
                {
                    "mutated_unit": unit,
                    "rationale": "Add an unsupported inference.",
                    "expected_failure": "The conclusion lacks evidence.",
                }
            )
        raise AssertionError("Unexpected prompt type.")


class FileAwareAdaptiveFakeLLM(AdaptiveFakeLLM):
    def __init__(self) -> None:
        super().__init__()
        self.file_calls: list[tuple[str, dict[str, str]]] = []

    def complete_with_files(self, prompt: str, files: dict[str, str]) -> str:
        self.file_calls.append((prompt, dict(files)))
        rendered = prompt + "\n\nWorkspace file contents:"
        for filename, content in files.items():
            rendered += (
                f"\n--- BEGIN {filename} ---\n{content}"
                f"\n--- END {filename} ---"
            )
        return super().complete(rendered)


class InterruptAfterFirstAttemptLLM(AdaptiveFakeLLM):
    def complete(self, prompt: str) -> str:
        if len(self.prompts) == 5:
            raise KeyboardInterrupt("simulated process interruption")
        return super().complete(prompt)


class FlakyEvolutionLLM(AdaptiveFakeLLM):
    def __init__(self) -> None:
        super().__init__()
        self.evolution_calls = 0

    def complete(self, prompt: str) -> str:
        if "Rewrite the complete prompt" in prompt:
            self.prompts.append(prompt)
            self.evolution_calls += 1
            if self.evolution_calls == 1:
                overlong = EVOLVED_POLICY + "\n" + ("x" * 6_000)
                return json.dumps(
                    {"prompt_text": overlong, "change_summary": "Too long."}
                )
            if self.evolution_calls == 2:
                raise RuntimeError("simulated Codex transport closure")
            return json.dumps(
                {
                    "prompt_text": EVOLVED_POLICY,
                    "change_summary": "Recovered after validation and transport errors.",
                }
            )
        return super().complete(prompt)


def _write_jsonl(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8"
    )


def _make_dataset(root: Path, trace_count: int = 4) -> None:
    reasoning = []
    tool_use = []
    chunks = []
    holistic = []
    for index in range(trace_count):
        trace_id = f"trace-{index}"
        step = {
            "step_type": "reasoning",
            "position": 1,
            "content": {"think": f"Grounded reasoning {index}."},
        }
        common = {
            "trace_id": trace_id,
            "query": f"Research question {index}?",
            "original_steps": [
                {
                    "step_type": "planning",
                    "position": 0,
                    "content": {"think": "Plan."},
                },
                step,
            ],
            "perturbed_steps": [],
            "perturbed_step_index": 1,
        }
        reasoning.append({**common, "perturbation_type": "shallow_reflection"})
        tool_use.append({**common, "perturbation_type": "argument_corruption"})
        chunk_id = f"doc-{index}:sec1"
        unit = f"Grounded answer section {index}."
        output_common = {
            "trace_id": trace_id,
            "query": f"Research question {index}?",
            "perturbation_type": "fabrication",
            "chunk_id": chunk_id,
            "source_dataset": "fixture",
        }
        chunks.append(
            {
                **output_common,
                "original_answer": unit,
                "perturbed_answer": "Reference corruption.",
                "method": "fixture",
                "expected_metric_drop": ["factual_grounding"],
                "metadata": {},
            }
        )
        holistic.append(
            {
                **output_common,
                "doc_id": f"doc-{index}",
                "whole_original_answer": f"Intro {index}.\n\n{unit}\n\nConclusion {index}.",
                "whole_perturbed_answer": "Unused reference corruption.",
            }
        )
    _write_jsonl(
        root
        / "process-level-baselines/evaluation/reasoning/reasoning_dataset.jsonl",
        reasoning,
    )
    _write_jsonl(
        root / "process-level-baselines/evaluation/tool_use/tool_use_dataset.jsonl",
        tool_use,
    )
    _write_jsonl(
        root / "output-level-baselines/data/chunk_200cases.jsonl", chunks
    )
    _write_jsonl(
        root / "output-level-baselines/data/holistic_200cases.jsonl", holistic
    )


class ReflectPromptEvolutionTest(unittest.TestCase):
    def test_initial_reflect_policy_encourages_single_cause_propagation(self) -> None:
        self.assertIn("Propagate the changed fact", DEFAULT_REFLECT_MUTATION_POLICY)
        self.assertIn("same root failure", DEFAULT_REFLECT_MUTATION_POLICY)
        self.assertIn("where the artifact's coherence requires it", DEFAULT_REFLECT_MUTATION_POLICY)

    def test_nonminimal_mutation_is_invalid_and_partial_match_is_a_miss(self) -> None:
        checker = _parse_checker(
            json.dumps(
                {
                    "valid": True,
                    "minimal": False,
                    "independent_failure_count": 2,
                    "exposure_count": 3,
                    "severity": "material",
                    "detected_failure": "Two unrelated failures were introduced.",
                    "rationale": "The mutation is overexposed.",
                }
            )
        )
        match = _parse_error_match(
            json.dumps(
                {
                    "introduced_error_found": True,
                    "matching_error_indices": [0],
                    "match_level": "partial",
                    "rationale": "Only generic downstream overlap was present.",
                }
            )
        )
        coherent_propagation = _parse_checker(
            json.dumps(
                {
                    "valid": True,
                    "minimal": True,
                    "independent_failure_count": 1,
                    "exposure_count": 4,
                    "severity": "material",
                    "detected_failure": "One failure was propagated through four dependencies.",
                    "rationale": "Every companion edit follows the same root cause.",
                }
            )
        )

        self.assertFalse(checker["valid"])
        self.assertTrue(coherent_propagation["valid"])
        self.assertFalse(match["introduced_error_found"])
        self.assertTrue(match["reported_introduced_error_found"])
        self.assertEqual(match["matcher_policy"], "exact_only")

    def test_loads_all_views_and_reinserts_holistic_chunk(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _make_dataset(root, trace_count=2)

            examples = load_reflect_examples(root)

            self.assertEqual(len(examples), 8)
            self.assertEqual(
                {example.dataset for example in examples},
                {"reasoning", "tool_use", "chunk", "holistic"},
            )
            holistic = next(e for e in examples if e.dataset == "holistic")
            self.assertEqual(
                holistic.materialize("Changed section."),
                "Intro 0.\n\nChanged section.\n\nConclusion 0.",
            )

    def test_split_is_deterministic_and_prevents_cross_view_leakage(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _make_dataset(root, trace_count=8)
            examples = load_reflect_examples(root)

            first = split_reflect_examples_by_trace(
                examples, train_trace_fraction=0.5, split_seed=19
            )
            second = split_reflect_examples_by_trace(
                tuple(reversed(examples)), train_trace_fraction=0.5, split_seed=19
            )

            train_ids = {example.trace_id for example in first[0]}
            test_ids = {example.trace_id for example in first[1]}
            self.assertFalse(train_ids & test_ids)
            self.assertEqual(train_ids, {example.trace_id for example in second[0]})
            selected = select_reflect_examples(
                first[0],
                per_dataset=2,
                seed=4,
                max_unit_chars=10_000,
                max_candidate_chars=10_000,
            )
            self.assertEqual(len(selected), 8)
            self.assertEqual(
                dict((name, sum(e.dataset == name for e in selected)) for name in {
                    "reasoning", "tool_use", "chunk", "holistic"
                }),
                {"reasoning": 2, "tool_use": 2, "chunk": 2, "holistic": 2},
            )

    def test_runs_training_and_frozen_heldout_comparison(self) -> None:
        llm = FileAwareAdaptiveFakeLLM()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "dataset"
            storage = Path(tmp) / "run"
            _make_dataset(root)

            result = run_reflect_prompt_evolution_experiment(
                llm=llm,
                config=ReflectPromptExperimentConfig(
                    storage_dir=storage,
                    dataset_root=root,
                    train_examples_per_dataset=1,
                    test_examples_per_dataset=1,
                    test_attempts_per_example=2,
                    training_generations=1,
                    split_seed=5,
                    evaluation_seed=6,
                    max_workers=1,
                ),
            )

            self.assertEqual(len(result.training_attempts), 4)
            self.assertEqual(len(result.baseline_attempts), 8)
            self.assertEqual(len(result.learned_attempts), 8)
            self.assertEqual(result.learned_prompt.prompt_text, EVOLVED_POLICY)
            self.assertFalse(set(result.train_trace_ids) & set(result.test_trace_ids))
            self.assertTrue(all(attempt.valid_mutation for attempt in result.training_attempts))
            self.assertTrue(
                all(len(attempt.original_judge_results) == 1 for attempt in result.training_attempts)
            )
            self.assertTrue(all(attempt.success for attempt in result.baseline_attempts))
            self.assertTrue(
                all(not attempt.introduced_error_found for attempt in result.baseline_attempts)
            )
            self.assertTrue((storage / "dataset_manifest.json").is_file())
            self.assertTrue((storage / "results.md").is_file())
            split = json.loads((storage / "split.json").read_text())
            self.assertEqual(split["unit"], "trace_id")
            mutation_calls = [
                files
                for prompt, files in llm.file_calls
                if "controlled failure cases" in prompt
            ]
            self.assertTrue(mutation_calls)
            self.assertTrue(
                all(
                    set(files) == {"strategy.txt", "trace.json"}
                    for files in mutation_calls
                )
            )
            evolution_calls = [
                files
                for prompt, files in llm.file_calls
                if "Rewrite the complete prompt" in prompt
            ]
            self.assertEqual(len(evolution_calls), 1)
            self.assertEqual(
                set(evolution_calls[0]), {"strategy.txt", "outcomes.json"}
            )

    def test_resume_runs_only_missing_jobs_after_interruption(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "dataset"
            storage = Path(tmp) / "run"
            _make_dataset(root)
            config = ReflectPromptExperimentConfig(
                storage_dir=storage,
                dataset_root=root,
                train_examples_per_dataset=1,
                test_examples_per_dataset=1,
                training_generations=1,
                split_seed=5,
                evaluation_seed=6,
                max_workers=1,
            )

            with self.assertRaises(KeyboardInterrupt):
                run_reflect_prompt_evolution_experiment(
                    llm=InterruptAfterFirstAttemptLLM(), config=config
                )
            self.assertEqual(
                len((storage / "attempts.jsonl").read_text().splitlines()), 1
            )

            result = run_reflect_prompt_evolution_experiment(
                llm=AdaptiveFakeLLM(), config=config
            )

            self.assertEqual(len(result.training_attempts), 4)
            self.assertEqual(len(result.baseline_attempts), 4)
            self.assertEqual(len(result.learned_attempts), 4)
            self.assertEqual(
                len((storage / "attempts.jsonl").read_text().splitlines()), 12
            )

    def test_evolution_recovers_from_overlength_and_transport_errors(self) -> None:
        llm = FlakyEvolutionLLM()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "dataset"
            _make_dataset(root)

            result = run_reflect_prompt_evolution_experiment(
                llm=llm,
                config=ReflectPromptExperimentConfig(
                    storage_dir=Path(tmp) / "run",
                    dataset_root=root,
                    datasets=("reasoning",),
                    train_examples_per_dataset=1,
                    test_examples_per_dataset=1,
                    training_generations=1,
                    split_seed=5,
                    evaluation_seed=6,
                    max_workers=1,
                    llm_retries=0,
                    evolution_retries=3,
                ),
            )

            self.assertEqual(llm.evolution_calls, 3)
            self.assertEqual(result.learned_prompt.prompt_text, EVOLVED_POLICY)
            self.assertEqual(len(result.training_attempts), 1)
            self.assertEqual(len(result.baseline_attempts), 1)
            self.assertEqual(len(result.learned_attempts), 1)


if __name__ == "__main__":
    unittest.main()
