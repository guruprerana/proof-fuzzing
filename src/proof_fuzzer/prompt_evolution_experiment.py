"""Train/test experiments for the single-prompt evolution pipeline."""

from __future__ import annotations

from collections import Counter
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import asdict, dataclass, field, replace
import json
from pathlib import Path
import random

from src.proof_fuzzer.evolution import (
    EvolutionConfig,
    FUZZER_KIND_NATURAL_LANGUAGE,
    FuzzAttempt,
)
from src.proof_fuzzer.llm_interface import LLMClient
from src.proof_fuzzer.openai_ten_advances import (
    DEFAULT_OPENAI_TEN_ADVANCES_ROOT,
    OpenAITenAdvancesProof,
    load_openai_ten_advances_proofs,
)
from src.proof_fuzzer.prompt_evolution import (
    DEFAULT_MUTATION_POLICY,
    MutationPromptVersion,
    PromptEvolutionConfig,
    PromptEvolutionaryProofFuzzer,
    _run_generation_batch,
)
from src.proof_fuzzer.proof_bench_judge import (
    format_natural_language_proof_objective,
)


@dataclass(frozen=True)
class PromptEvolutionExperimentConfig:
    """Protocol for training on one proof split and evaluating on another."""

    storage_dir: str | Path = "logs/prompt_evolution_experiments"
    proof_root: str | Path = DEFAULT_OPENAI_TEN_ADVANCES_ROOT
    model: str = "gpt-5.6-sol"
    reasoning_effort: str = "medium"
    codex_sandbox: str = "read_only"
    codex_service_tier: str | None = None
    train_problem_count: int = 5
    training_generations: int = 3
    test_attempts_per_problem: int = 3
    split_seed: int = 20260902
    evaluation_seed: int = 20260903
    max_workers: int = 5
    training_attempts_per_problem_per_generation: int = 1
    initial_prompt: str = DEFAULT_MUTATION_POLICY
    max_prompt_chars: int = 5_000
    max_prompt_growth_chars: int = 400
    max_prompt_length_multiplier: float = 2.0
    max_attempt_summary_chars: int = 1_200
    max_evolution_context_chars: int = 40_000
    evolution_retries: int = 1
    objective_prefix: str = (
        "Generate a subtle invalid mutation of a recently published theoretical "
        "computer-science proof."
    )
    dataset_name: str = "OpenAI ten-advances"
    proof_source: str = "Markdown manuscript"

    def __post_init__(self) -> None:
        if self.train_problem_count < 1:
            raise ValueError("train_problem_count must be at least 1.")
        if self.training_generations < 1:
            raise ValueError("training_generations must be at least 1.")
        if self.training_attempts_per_problem_per_generation < 1:
            raise ValueError(
                "training_attempts_per_problem_per_generation must be at least 1."
            )
        if self.test_attempts_per_problem < 1:
            raise ValueError("test_attempts_per_problem must be at least 1.")
        if self.max_workers < 1:
            raise ValueError("max_workers must be at least 1.")
        if self.evolution_retries < 0:
            raise ValueError("evolution_retries must be non-negative.")


@dataclass(frozen=True)
class PromptEvolutionExperimentResult:
    """Artifacts and measurements from one prompt-learning experiment."""

    storage_dir: Path
    train_example_ids: tuple[str, ...]
    test_example_ids: tuple[str, ...]
    training_attempts: tuple[FuzzAttempt, ...]
    baseline_attempts: tuple[FuzzAttempt, ...]
    learned_attempts: tuple[FuzzAttempt, ...]
    initial_prompt: MutationPromptVersion
    learned_prompt: MutationPromptVersion
    metrics: dict[str, object] = field(default_factory=dict)

    def summary(self) -> str:
        comparison = self.metrics.get("comparison", {})
        delta = (
            comparison.get("success_rate_delta", 0.0)
            if isinstance(comparison, dict)
            else 0.0
        )
        return (
            f"Trained for {self.learned_prompt.version} prompt updates on "
            f"{len(self.train_example_ids)} proofs; evaluated "
            f"{len(self.baseline_attempts)} baseline and {len(self.learned_attempts)} "
            f"learned-prompt attempts on {len(self.test_example_ids)} held-out proofs; "
            f"success-rate delta={float(delta):+.3f}; storage={self.storage_dir}"
        )


def split_openai_ten_advances_proofs(
    examples: tuple[OpenAITenAdvancesProof, ...],
    *,
    train_problem_count: int = 5,
    split_seed: int = 20260902,
) -> tuple[tuple[OpenAITenAdvancesProof, ...], tuple[OpenAITenAdvancesProof, ...]]:
    """Return a deterministic randomized train/test partition."""

    if not 0 < train_problem_count < len(examples):
        raise ValueError("train_problem_count must leave at least one held-out proof.")
    shuffled = sorted(examples, key=lambda example: example.example_id)
    random.Random(split_seed).shuffle(shuffled)
    return (
        tuple(shuffled[:train_problem_count]),
        tuple(shuffled[train_problem_count:]),
    )


def run_openai_ten_advances_prompt_evolution_experiment(
    *,
    llm: LLMClient,
    config: PromptEvolutionExperimentConfig | None = None,
    attempt_config: EvolutionConfig | None = None,
    examples: tuple[OpenAITenAdvancesProof, ...] | None = None,
    progress: Callable[[str], None] | None = None,
) -> PromptEvolutionExperimentResult:
    """Train a mutation prompt and compare it with its initial held-out baseline."""

    active = config or PromptEvolutionExperimentConfig()
    storage_dir = Path(active.storage_dir)
    storage_dir.mkdir(parents=True, exist_ok=True)
    all_examples = examples or load_openai_ten_advances_proofs(active.proof_root)
    train_examples, test_examples = split_openai_ten_advances_proofs(
        all_examples,
        train_problem_count=active.train_problem_count,
        split_seed=active.split_seed,
    )
    _write_json(
        storage_dir / "experiment_config.json",
        _jsonable(asdict(active)),
    )
    _write_json(
        storage_dir / "split.json",
        {
            "split_seed": active.split_seed,
            "train_example_ids": [example.example_id for example in train_examples],
            "test_example_ids": [example.example_id for example in test_examples],
        },
    )

    base_attempt_config = attempt_config or EvolutionConfig(
        storage_dir=storage_dir,
        run_pre_mutation_judge=False,
        run_original_error_control=True,
        max_proof_chars=300_000,
        max_problem_chars=12_000,
        llm_retries=1,
        context_fallbacks=1,
        continue_on_error=True,
    )
    training_dir = storage_dir / "training"
    attempts_per_generation = (
        len(train_examples) * active.training_attempts_per_problem_per_generation
    )
    prompt_config = PromptEvolutionConfig(
        storage_dir=training_dir,
        generation_size=attempts_per_generation,
        evolution_window=attempts_per_generation,
        max_prompt_chars=active.max_prompt_chars,
        max_prompt_growth_chars=active.max_prompt_growth_chars,
        max_prompt_length_multiplier=active.max_prompt_length_multiplier,
        max_attempt_summary_chars=active.max_attempt_summary_chars,
        max_evolution_context_chars=active.max_evolution_context_chars,
        initial_prompt=active.initial_prompt,
        evolution_retries=active.evolution_retries,
        random_seed=active.split_seed,
    )
    training_controller = PromptEvolutionaryProofFuzzer(
        llm,
        config=prompt_config,
        attempt_config=replace(base_attempt_config, storage_dir=training_dir),
    )
    prompt_history = training_controller.prompt_store.load_history()
    if not prompt_history:
        raise RuntimeError("Training prompt history was not initialized.")
    initial_prompt = prompt_history[0]
    learned_prompt = training_controller.current_prompt
    while learned_prompt.version < active.training_generations:
        generation = learned_prompt.version
        existing_for_prompt = training_controller.attempts_for_prompt(learned_prompt)
        _notify(progress, f"Training generation {generation + 1}/{active.training_generations}")
        if len(existing_for_prompt) == attempts_per_generation:
            _notify(progress, "Retrying the pending prompt evolution from persisted attempts")
            learned_prompt = training_controller.evolve_prompt(learned_prompt)
        else:
            persisted_keys = {
                (
                    str(attempt.metadata.get("example_id", "")),
                    int(attempt.metadata.get("example_attempt_index", 0)),
                )
                for attempt in existing_for_prompt
            }
            work_items = [
                (example_index * active.training_attempts_per_problem_per_generation + attempt_index,
                 example,
                 attempt_index)
                for example_index, example in enumerate(train_examples)
                for attempt_index in range(
                    active.training_attempts_per_problem_per_generation
                )
                if (example.example_id, attempt_index) not in persisted_keys
            ]
            _notify(
                progress,
                f"Resuming generation with {len(work_items)}/"
                f"{attempts_per_generation} attempts remaining",
            )
            if work_items:
                _run_generation_batch(
                    controller=training_controller,
                    prompt_version=learned_prompt,
                    work_items=work_items,
                    objective_prefix=active.objective_prefix,
                    dataset_name=f"{active.dataset_name} training",
                    proof_source=active.proof_source,
                    max_workers=active.max_workers,
                )
            completed = training_controller.attempts_for_prompt(learned_prompt)
            if len(completed) != attempts_per_generation:
                raise RuntimeError(
                    f"Training generation {generation + 1} persisted "
                    f"{len(completed)}/{attempts_per_generation} attempts."
                )
            learned_prompt = training_controller.evolve_prompt(learned_prompt)
        _notify(
            progress,
            f"Completed generation {generation + 1}; prompt version is {learned_prompt.version}",
        )

    training_attempts = training_controller.attempt_store.load_attempts(
        fuzzer_kind=FUZZER_KIND_NATURAL_LANGUAGE,
    )
    (storage_dir / "initial_prompt.txt").write_text(
        initial_prompt.prompt_text + "\n", encoding="utf-8"
    )
    (storage_dir / "learned_prompt.txt").write_text(
        learned_prompt.prompt_text + "\n", encoding="utf-8"
    )

    _notify(progress, "Starting shuffled held-out baseline/learned evaluation")
    baseline_attempts, learned_attempts = _run_heldout_evaluation(
        llm=llm,
        config=active,
        attempt_config=base_attempt_config,
        test_examples=test_examples,
        initial_prompt=initial_prompt,
        learned_prompt=learned_prompt,
        storage_dir=storage_dir,
        progress=progress,
    )
    metrics = _experiment_metrics(
        baseline_attempts=baseline_attempts,
        learned_attempts=learned_attempts,
    )
    summary_payload = {
        "train_example_ids": [example.example_id for example in train_examples],
        "test_example_ids": [example.example_id for example in test_examples],
        "training_attempt_count": len(training_attempts),
        "initial_prompt": initial_prompt.to_dict(),
        "learned_prompt": learned_prompt.to_dict(),
        "metrics": metrics,
    }
    _write_json(storage_dir / "summary.json", summary_payload)
    _notify(progress, "Experiment complete")
    return PromptEvolutionExperimentResult(
        storage_dir=storage_dir,
        train_example_ids=tuple(example.example_id for example in train_examples),
        test_example_ids=tuple(example.example_id for example in test_examples),
        training_attempts=training_attempts,
        baseline_attempts=baseline_attempts,
        learned_attempts=learned_attempts,
        initial_prompt=initial_prompt,
        learned_prompt=learned_prompt,
        metrics=metrics,
    )


def _run_heldout_evaluation(
    *,
    llm: LLMClient,
    config: PromptEvolutionExperimentConfig,
    attempt_config: EvolutionConfig,
    test_examples: tuple[OpenAITenAdvancesProof, ...],
    initial_prompt: MutationPromptVersion,
    learned_prompt: MutationPromptVersion,
    storage_dir: Path,
    progress: Callable[[str], None] | None,
) -> tuple[tuple[FuzzAttempt, ...], tuple[FuzzAttempt, ...]]:
    controllers = {
        "baseline": PromptEvolutionaryProofFuzzer(
            llm,
            config=PromptEvolutionConfig(
                storage_dir=storage_dir / "heldout_baseline",
                initial_prompt=initial_prompt.prompt_text,
                max_prompt_chars=config.max_prompt_chars,
            ),
            attempt_config=replace(
                attempt_config,
                storage_dir=storage_dir / "heldout_baseline",
            ),
        ),
        "learned": PromptEvolutionaryProofFuzzer(
            llm,
            config=PromptEvolutionConfig(
                storage_dir=storage_dir / "heldout_learned",
                initial_prompt=learned_prompt.prompt_text,
                max_prompt_chars=config.max_prompt_chars,
            ),
            attempt_config=replace(
                attempt_config,
                storage_dir=storage_dir / "heldout_learned",
            ),
        ),
    }
    versions = {"baseline": initial_prompt, "learned": learned_prompt}
    all_jobs = [
        (arm, example, attempt_index)
        for example in test_examples
        for attempt_index in range(config.test_attempts_per_problem)
        for arm in ("baseline", "learned")
    ]
    random.Random(config.evaluation_seed).shuffle(all_jobs)

    existing_by_arm = {
        arm: controllers[arm].attempt_store.load_attempts(
            fuzzer_kind=FUZZER_KIND_NATURAL_LANGUAGE,
        )
        for arm in ("baseline", "learned")
    }

    def persisted_key(attempt: FuzzAttempt) -> tuple[str, int, str]:
        return (
            str(attempt.metadata.get("example_id", "")),
            int(attempt.metadata.get("example_attempt_index", 0)),
            str(attempt.metadata.get("mutation_prompt_sha256", "")),
        )

    persisted = {
        arm: {persisted_key(attempt): attempt for attempt in attempts}
        for arm, attempts in existing_by_arm.items()
    }
    jobs = [
        job
        for job in all_jobs
        if (
            job[1].example_id,
            job[2],
            versions[job[0]].prompt_sha256,
        ) not in persisted[job[0]]
    ]
    _notify(
        progress,
        f"Held-out evaluation: {len(all_jobs) - len(jobs)}/{len(all_jobs)} "
        "attempts already persisted",
    )

    def run_job(
        job: tuple[str, OpenAITenAdvancesProof, int],
    ) -> tuple[str, FuzzAttempt]:
        arm, example, attempt_index = job
        # Match training: always supply the complete source proof.
        proof_text = example.proof
        attempt = controllers[arm].run_false_proof_attempt(
            proof_text=proof_text,
            objective=format_natural_language_proof_objective(
                example,
                objective_prefix=config.objective_prefix,
                max_problem_chars=controllers[arm].attempt_config.max_problem_chars,
                dataset_name=f"{config.dataset_name} held-out",
            ),
            metadata={
                **example.to_metadata(),
                "experiment_phase": "heldout_evaluation",
                "experiment_arm": arm,
                "held_out": True,
                "example_attempt_index": attempt_index,
                "proof_source": config.proof_source,
                "fuzzer_kind": FUZZER_KIND_NATURAL_LANGUAGE,
                "proof_chars_original": len(example.proof),
                "proof_chars_used": len(proof_text),
                "prompt_truncated": len(proof_text) < len(example.proof),
            },
            prompt_version=versions[arm],
        )
        return arm, attempt

    attempts_by_arm: dict[str, list[FuzzAttempt]] = {
        "baseline": [],
        "learned": [],
    }
    if config.max_workers == 1:
        for completed, job in enumerate(jobs, start=1):
            arm, attempt = run_job(job)
            attempts_by_arm[arm].append(attempt)
            _notify(progress, f"Held-out attempt {completed}/{len(jobs)} complete")
    else:
        with ThreadPoolExecutor(max_workers=config.max_workers) as executor:
            futures = [executor.submit(run_job, job) for job in jobs]
            for completed, future in enumerate(as_completed(futures), start=1):
                arm, attempt = future.result()
                attempts_by_arm[arm].append(attempt)
                _notify(progress, f"Held-out attempt {completed}/{len(jobs)} complete")
    for arm in ("baseline", "learned"):
        for attempt in attempts_by_arm[arm]:
            persisted[arm][persisted_key(attempt)] = attempt

    def ordered(arm: str) -> tuple[FuzzAttempt, ...]:
        return tuple(
            persisted[arm][
                (example.example_id, attempt_index, versions[arm].prompt_sha256)
            ]
            for example in test_examples
            for attempt_index in range(config.test_attempts_per_problem)
        )

    return ordered("baseline"), ordered("learned")


def _experiment_metrics(
    *,
    baseline_attempts: tuple[FuzzAttempt, ...],
    learned_attempts: tuple[FuzzAttempt, ...],
) -> dict[str, object]:
    baseline = _arm_metrics(baseline_attempts)
    learned = _arm_metrics(learned_attempts)
    return {
        "baseline": baseline,
        "learned": learned,
        "comparison": {
            "success_rate_delta": learned["success_rate"] - baseline["success_rate"],
            "valid_mutation_rate_delta": (
                learned["valid_mutation_rate"] - baseline["valid_mutation_rate"]
            ),
            "fool_rate_given_valid_delta": (
                learned["fool_rate_given_valid"] - baseline["fool_rate_given_valid"]
            ),
        },
    }


def _arm_metrics(attempts: tuple[FuzzAttempt, ...]) -> dict[str, object]:
    total = len(attempts)
    successful = sum(attempt.success for attempt in attempts)
    valid = sum(
        attempt.mutation_check_result is not None
        and attempt.mutation_check_result.verdict == "incorrect"
        for attempt in attempts
    )
    failed = sum(attempt.status == "failed" for attempt in attempts)
    outcomes = Counter(_evaluation_outcome(attempt) for attempt in attempts)
    by_problem: dict[str, dict[str, object]] = {}
    problem_ids = sorted(
        {str(attempt.metadata.get("example_id", "unknown")) for attempt in attempts}
    )
    for problem_id in problem_ids:
        selected = tuple(
            attempt
            for attempt in attempts
            if str(attempt.metadata.get("example_id", "unknown")) == problem_id
        )
        by_problem[problem_id] = {
            "attempts": len(selected),
            "successes": sum(attempt.success for attempt in selected),
            "success_rate": _rate(sum(attempt.success for attempt in selected), len(selected)),
            "valid_mutations": sum(
                attempt.mutation_check_result is not None
                and attempt.mutation_check_result.verdict == "incorrect"
                for attempt in selected
            ),
        }
    return {
        "attempts": total,
        "successes": successful,
        "success_rate": _rate(successful, total),
        "valid_mutations": valid,
        "valid_mutation_rate": _rate(valid, total),
        "fool_rate_given_valid": _rate(successful, valid),
        "failed_attempts": failed,
        "outcomes": dict(sorted(outcomes.items())),
        "by_problem": by_problem,
    }


def _evaluation_outcome(attempt: FuzzAttempt) -> str:
    if attempt.status == "failed":
        return "pipeline_failure"
    if (
        attempt.mutation_check_result is None
        or attempt.mutation_check_result.verdict != "incorrect"
    ):
        return "invalid_mutation"
    return "fooled_target" if attempt.success else "caught_by_target"


def _rate(numerator: int, denominator: int) -> float:
    return numerator / denominator if denominator else 0.0


def _jsonable(value: object) -> object:
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, dict):
        return {str(key): _jsonable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_jsonable(item) for item in value]
    return value


def _write_json(path: Path, payload: object) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _notify(progress: Callable[[str], None] | None, message: str) -> None:
    if progress is not None:
        progress(message)
