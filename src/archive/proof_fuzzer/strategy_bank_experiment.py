"""Matched train/test experiments for the strategy-bank evolution pipeline."""

from __future__ import annotations

from collections import Counter
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import asdict, dataclass, replace
import json
from pathlib import Path
import random
import re

from src.archive.proof_fuzzer.evolution import (
    EvolutionConfig,
    EvolutionaryProofFuzzer,
    FUZZER_KIND_NATURAL_LANGUAGE,
    FuzzAttempt,
    FuzzStrategy,
    ProofFuzzAttemptStore,
    StrategyEvolver,
    truncate_text_head_tail,
)
from src.archive.proof_fuzzer.llm_interface import LLMClient, NaturalLanguageProofFuzzerLLMInterface
from src.proof_fuzzer.openai_ten_advances import (
    DEFAULT_OPENAI_TEN_ADVANCES_ROOT,
    OpenAITenAdvancesProof,
    load_openai_ten_advances_proofs,
)
from src.archive.proof_fuzzer.prompt_evolution_experiment import split_openai_ten_advances_proofs
from src.proof_fuzzer.proof_bench_judge import (
    format_natural_language_proof_objective,
    run_natural_language_proof_examples_evolutionary_pipeline,
)


@dataclass(frozen=True)
class StrategyBankExperimentConfig:
    storage_dir: str | Path = "logs/archive/strategy_bank_pipeline/experiments"
    proof_root: str | Path = DEFAULT_OPENAI_TEN_ADVANCES_ROOT
    model: str = "gpt-5.6-sol"
    reasoning_effort: str = "medium"
    codex_sandbox: str = "read_only"
    codex_service_tier: str | None = None
    train_problem_count: int = 5
    training_rounds: int = 5
    training_attempts_per_problem_per_round: int = 2
    test_attempts_per_problem: int = 3
    strategies_per_test_attempt: int = 1
    max_strategies_per_topic: int = 10
    strategy_evolution_retries: int = 1
    strategy_evolution_window_per_topic: int = 30
    split_seed: int = 20260902
    evaluation_seed: int = 20260903
    max_workers: int = 5
    objective_prefix: str = (
        "Generate a subtle invalid mutation of a recently published theoretical "
        "computer-science proof."
    )

    def __post_init__(self) -> None:
        for name in (
            "train_problem_count",
            "training_rounds",
            "training_attempts_per_problem_per_round",
            "test_attempts_per_problem",
            "strategies_per_test_attempt",
            "max_strategies_per_topic",
            "strategy_evolution_window_per_topic",
            "max_workers",
        ):
            if int(getattr(self, name)) < 1:
                raise ValueError(f"{name} must be at least 1.")
        if self.strategy_evolution_retries < 0:
            raise ValueError("strategy_evolution_retries must be non-negative.")


@dataclass(frozen=True)
class StrategyBankExperimentResult:
    storage_dir: Path
    train_example_ids: tuple[str, ...]
    test_example_ids: tuple[str, ...]
    training_attempts: tuple[FuzzAttempt, ...]
    baseline_attempts: tuple[FuzzAttempt, ...]
    learned_attempts: tuple[FuzzAttempt, ...]
    frozen_bank: tuple[FuzzStrategy, ...]
    metrics: dict[str, object]

    def summary(self) -> str:
        comparison = self.metrics.get("comparison", {})
        delta = comparison.get("success_rate_delta", 0.0) if isinstance(comparison, dict) else 0.0
        return (
            f"Trained {len(self.training_attempts)} attempts over "
            f"{len(self.train_example_ids)} proofs; froze {len(self.frozen_bank)} strategies; "
            f"evaluated {len(self.baseline_attempts)} baseline and "
            f"{len(self.learned_attempts)} bank-guided attempts on "
            f"{len(self.test_example_ids)} held-out proofs; "
            f"success-rate delta={float(delta):+.3f}; storage={self.storage_dir}"
        )


def run_openai_ten_advances_strategy_bank_experiment(
    *,
    llm: LLMClient,
    config: StrategyBankExperimentConfig | None = None,
    attempt_config: EvolutionConfig | None = None,
    examples: tuple[OpenAITenAdvancesProof, ...] | None = None,
    progress: Callable[[str], None] | None = None,
) -> StrategyBankExperimentResult:
    active = config or StrategyBankExperimentConfig()
    storage_dir = Path(active.storage_dir)
    storage_dir.mkdir(parents=True, exist_ok=True)
    all_examples = examples or load_openai_ten_advances_proofs(active.proof_root)
    train_examples, test_examples = split_openai_ten_advances_proofs(
        all_examples,
        train_problem_count=active.train_problem_count,
        split_seed=active.split_seed,
    )
    _write_json(storage_dir / "experiment_config.json", _jsonable(asdict(active)))
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
        max_proof_chars=300_000,
        max_problem_chars=12_000,
        llm_retries=1,
        context_fallbacks=1,
        continue_on_error=True,
    )
    training_dir = storage_dir / "training"
    training_store = ProofFuzzAttemptStore(training_dir)
    expected_per_round = (
        len(train_examples) * active.training_attempts_per_problem_per_round
    )
    for round_index in range(active.training_rounds):
        round_number = round_index + 1
        attempt_manifest = training_dir / f"round_{round_number:02d}_attempts.json"
        bank_snapshot = training_dir / f"round_{round_number:02d}_bank.json"
        _notify(progress, f"Training round {round_number}/{active.training_rounds}")
        if attempt_manifest.is_file():
            attempt_ids = tuple(_read_json(attempt_manifest)["attempt_ids"])
            round_attempts = _attempts_by_ids(training_store, attempt_ids)
            if len(round_attempts) != expected_per_round:
                raise RuntimeError(f"Training round {round_number} manifest is incomplete.")
        else:
            existing_count = len(
                training_store.load_attempts(fuzzer_kind=FUZZER_KIND_NATURAL_LANGUAGE)
            )
            if existing_count != round_index * expected_per_round:
                raise RuntimeError(
                    f"Cannot safely resume training round {round_number}: found "
                    f"{existing_count} attempts, expected {round_index * expected_per_round}."
                )
            round_config = replace(
                base_attempt_config,
                storage_dir=training_dir,
                strategy_injection_probability=1.0,
                max_strategies_injected=1,
                evolution_threshold=0,
                seed_mined_strategies=False,
                strategy_selection_mode="retrieval",
                correctness_selection_mode="false_proof",
                false_proof_probability=1.0,
                max_previous_failed_attempts_in_prompt=0,
                max_previous_successful_attempts_in_prompt=0,
                reject_duplicate_successful_mutations=False,
                random_seed=active.split_seed + round_number,
            )
            round_attempts = run_natural_language_proof_examples_evolutionary_pipeline(
                examples=train_examples,
                llm=llm,
                config=round_config,
                store=training_store,
                objective_prefix=active.objective_prefix,
                max_workers=active.max_workers,
                attempts_per_example=active.training_attempts_per_problem_per_round,
                dataset_name="OpenAI ten-advances strategy-bank training",
                proof_source="Markdown manuscript",
            )
            if len(round_attempts) != expected_per_round:
                raise RuntimeError(
                    f"Training round {round_number} produced "
                    f"{len(round_attempts)}/{expected_per_round} attempts."
                )
            _write_json(
                attempt_manifest,
                {
                    "round": round_number,
                    "attempt_ids": [attempt.attempt_id for attempt in round_attempts],
                },
            )
        if bank_snapshot.is_file():
            frozen_round = tuple(
                FuzzStrategy.from_dict(item)
                for item in _read_json(bank_snapshot)["strategies"]
            )
            training_store.save_strategies(FUZZER_KIND_NATURAL_LANGUAGE, frozen_round)
        else:
            accumulated = training_store.load_attempts(
                fuzzer_kind=FUZZER_KIND_NATURAL_LANGUAGE
            )
            evolved = _evolve_strategy_bank(
                llm=llm,
                attempts=accumulated,
                existing=training_store.load_strategies(FUZZER_KIND_NATURAL_LANGUAGE),
                config=active,
            )
            training_store.save_strategies(FUZZER_KIND_NATURAL_LANGUAGE, evolved)
            _write_json(
                bank_snapshot,
                {
                    "round": round_number,
                    "training_attempt_ids": [attempt.attempt_id for attempt in accumulated],
                    "strategies": [strategy.to_dict() for strategy in evolved],
                },
            )
        _notify(
            progress,
            f"Completed training round {round_number}; bank has "
            f"{len(training_store.load_strategies(FUZZER_KIND_NATURAL_LANGUAGE))} strategies",
        )

    training_attempts = training_store.load_attempts(
        fuzzer_kind=FUZZER_KIND_NATURAL_LANGUAGE
    )
    frozen_bank = training_store.load_strategies(FUZZER_KIND_NATURAL_LANGUAGE)
    if not frozen_bank:
        raise RuntimeError("Training completed without producing any strategies.")
    frozen_path = storage_dir / "frozen_strategy_bank.json"
    _write_json(frozen_path, {"strategies": [strategy.to_dict() for strategy in frozen_bank]})
    assignments = _load_or_create_assignments(
        path=storage_dir / "heldout_strategy_assignments.json",
        test_examples=test_examples,
        bank=frozen_bank,
        attempts_per_problem=active.test_attempts_per_problem,
        strategies_per_attempt=active.strategies_per_test_attempt,
        objective_prefix=active.objective_prefix,
    )
    _notify(progress, "Starting shuffled held-out baseline/strategy-bank evaluation")
    baseline_attempts, learned_attempts = _run_heldout_evaluation(
        llm=llm,
        config=active,
        attempt_config=base_attempt_config,
        test_examples=test_examples,
        bank=frozen_bank,
        assignments=assignments,
        storage_dir=storage_dir,
        progress=progress,
    )
    metrics = _experiment_metrics(
        training_attempts=training_attempts,
        baseline_attempts=baseline_attempts,
        learned_attempts=learned_attempts,
        bank=frozen_bank,
    )
    _write_json(
        storage_dir / "summary.json",
        {
            "train_example_ids": [example.example_id for example in train_examples],
            "test_example_ids": [example.example_id for example in test_examples],
            "training_attempt_count": len(training_attempts),
            "frozen_strategy_count": len(frozen_bank),
            "metrics": metrics,
        },
    )
    _notify(progress, "Experiment complete")
    return StrategyBankExperimentResult(
        storage_dir=storage_dir,
        train_example_ids=tuple(example.example_id for example in train_examples),
        test_example_ids=tuple(example.example_id for example in test_examples),
        training_attempts=training_attempts,
        baseline_attempts=baseline_attempts,
        learned_attempts=learned_attempts,
        frozen_bank=frozen_bank,
        metrics=metrics,
    )


def _evolve_strategy_bank(
    *,
    llm: LLMClient,
    attempts: tuple[FuzzAttempt, ...],
    existing: tuple[FuzzStrategy, ...],
    config: StrategyBankExperimentConfig,
) -> tuple[FuzzStrategy, ...]:
    topics = sorted(
        {
            str(attempt.metadata.get("llm_category", ""))
            for attempt in attempts
            if attempt.metadata.get("llm_category")
        }
    )
    evolved_bank: list[FuzzStrategy] = []
    evolver = StrategyEvolver(llm)
    for topic in topics:
        topic_attempts = tuple(
            attempt
            for attempt in attempts
            if attempt.metadata.get("llm_category") == topic
        )[-config.strategy_evolution_window_per_topic :]
        topic_existing = tuple(
            strategy for strategy in existing if strategy.math_topic == topic
        )
        last_error: Exception | None = None
        for retry_index in range(config.strategy_evolution_retries + 1):
            try:
                replacements = evolver.evolve(
                    fuzzer_kind=FUZZER_KIND_NATURAL_LANGUAGE,
                    attempts=topic_attempts,
                    existing_strategies=topic_existing,
                    max_bank_size=config.max_strategies_per_topic,
                )
                break
            except Exception as exc:
                last_error = exc
                if retry_index >= config.strategy_evolution_retries:
                    raise
        else:
            raise last_error or RuntimeError("Strategy evolution failed.")
        evolved_bank.extend(
            _with_observed_strategy_counts(
                tuple(
                    replace(
                        strategy,
                        math_topic=topic,
                        target_correctness=False,
                        metadata={**strategy.metadata, "math_topic": topic},
                    )
                    for strategy in replacements
                ),
                attempts,
            )
        )
    return tuple(evolved_bank)


def _with_observed_strategy_counts(
    strategies: tuple[FuzzStrategy, ...],
    attempts: tuple[FuzzAttempt, ...],
) -> tuple[FuzzStrategy, ...]:
    return tuple(
        replace(
            strategy,
            successes=sum(
                strategy.strategy_id in attempt.strategy_ids and attempt.success
                for attempt in attempts
            ),
            failures=sum(
                strategy.strategy_id in attempt.strategy_ids and not attempt.success
                for attempt in attempts
            ),
        )
        for strategy in strategies
    )


def _load_or_create_assignments(
    *,
    path: Path,
    test_examples: tuple[OpenAITenAdvancesProof, ...],
    bank: tuple[FuzzStrategy, ...],
    attempts_per_problem: int,
    strategies_per_attempt: int,
    objective_prefix: str,
) -> dict[str, list[list[str]]]:
    if path.is_file():
        data = _read_json(path)
        return {
            str(key): [[str(item) for item in group] for group in value]
            for key, value in data["assignments"].items()
        }
    assignments: dict[str, list[list[str]]] = {}
    for example in test_examples:
        candidates = [
            strategy
            for strategy in bank
            if strategy.math_topic == example.llm_category
            and strategy.target_correctness in (None, False)
        ]
        if not candidates:
            raise RuntimeError(
                f"No frozen strategy applies to held-out proof {example.example_id}."
            )
        objective = format_natural_language_proof_objective(
            example,
            objective_prefix=objective_prefix,
            dataset_name="OpenAI ten-advances held-out",
        )
        ranked = _rank_strategies(candidates, objective=objective, proof=example.proof)
        proof_assignments = []
        for attempt_index in range(attempts_per_problem):
            selected = [
                ranked[(attempt_index * strategies_per_attempt + offset) % len(ranked)]
                for offset in range(strategies_per_attempt)
            ]
            proof_assignments.append([strategy.strategy_id for strategy in selected])
        assignments[example.example_id] = proof_assignments
    _write_json(
        path,
        {
            "assignments": assignments,
            "selection": "deterministic relevance ranking with round-robin coverage",
        },
    )
    return assignments


def _rank_strategies(
    strategies: list[FuzzStrategy],
    *,
    objective: str,
    proof: str,
) -> list[FuzzStrategy]:
    query = set(_tokens(objective + "\n" + proof))

    def score(strategy: FuzzStrategy) -> tuple[float, str]:
        keywords = " ".join(str(item) for item in strategy.metadata.get("keywords", ()))
        overlap = len(query & set(_tokens(f"{strategy.title} {strategy.guidance} {keywords}")))
        uses = strategy.successes + strategy.failures
        observed_rate = (strategy.successes + 1) / (uses + 2)
        return overlap + observed_rate, strategy.strategy_id

    return sorted(strategies, key=score, reverse=True)


def _run_heldout_evaluation(
    *,
    llm: LLMClient,
    config: StrategyBankExperimentConfig,
    attempt_config: EvolutionConfig,
    test_examples: tuple[OpenAITenAdvancesProof, ...],
    bank: tuple[FuzzStrategy, ...],
    assignments: dict[str, list[list[str]]],
    storage_dir: Path,
    progress: Callable[[str], None] | None,
) -> tuple[tuple[FuzzAttempt, ...], tuple[FuzzAttempt, ...]]:
    stores = {
        "baseline": ProofFuzzAttemptStore(storage_dir / "heldout_baseline"),
        "learned": ProofFuzzAttemptStore(storage_dir / "heldout_strategy_bank"),
    }
    bank_by_id = {strategy.strategy_id: strategy for strategy in bank}
    jobs = [
        (arm, example, attempt_index)
        for example in test_examples
        for attempt_index in range(config.test_attempts_per_problem)
        for arm in ("baseline", "learned")
    ]
    completed_keys = {
        arm: {
            (str(attempt.metadata.get("example_id")), int(attempt.metadata.get("example_attempt_index", -1)))
            for attempt in store.load_attempts(fuzzer_kind=FUZZER_KIND_NATURAL_LANGUAGE)
        }
        for arm, store in stores.items()
    }
    jobs = [
        job
        for job in jobs
        if (job[1].example_id, job[2]) not in completed_keys[job[0]]
    ]
    random.Random(config.evaluation_seed).shuffle(jobs)
    eval_config = replace(
        attempt_config,
        evolution_threshold=0,
        seed_mined_strategies=False,
        correctness_selection_mode="false_proof",
        false_proof_probability=1.0,
        max_previous_failed_attempts_in_prompt=0,
        max_previous_successful_attempts_in_prompt=0,
        reject_duplicate_successful_mutations=False,
    )

    def run_job(job: tuple[str, OpenAITenAdvancesProof, int]) -> tuple[str, FuzzAttempt]:
        arm, example, attempt_index = job
        proof_text = truncate_text_head_tail(example.proof, eval_config.max_proof_chars)
        strategy_ids = assignments[example.example_id][attempt_index] if arm == "learned" else []
        fixed = tuple(bank_by_id[strategy_id] for strategy_id in strategy_ids)
        fuzzer = NaturalLanguageProofFuzzerLLMInterface(proof_text, llm)
        runner = EvolutionaryProofFuzzer(
            fuzzer,
            store=stores[arm],
            config=replace(
                eval_config,
                storage_dir=stores[arm].root_dir,
                strategy_injection_probability=0.0 if arm == "baseline" else 1.0,
                max_strategies_injected=len(fixed),
            ),
            fixed_strategies=fixed if arm == "learned" else None,
        )
        attempt = runner.run_false_proof_attempt(
            objective=format_natural_language_proof_objective(
                example,
                objective_prefix=config.objective_prefix,
                max_problem_chars=eval_config.max_problem_chars,
                dataset_name="OpenAI ten-advances held-out",
            ),
            metadata={
                **example.to_metadata(),
                "experiment_phase": "heldout_evaluation",
                "experiment_arm": arm,
                "held_out": True,
                "example_attempt_index": attempt_index,
                "assigned_strategy_ids": strategy_ids,
                "strategy_assignment_frozen": True,
                "proof_source": "Markdown manuscript",
                "fuzzer_kind": FUZZER_KIND_NATURAL_LANGUAGE,
                "proof_chars_original": len(example.proof),
                "proof_chars_used": len(proof_text),
                "prompt_truncated": len(proof_text) < len(example.proof),
            },
        )
        return arm, attempt

    total_jobs = len(jobs)
    if config.max_workers == 1:
        for completed, job in enumerate(jobs, start=1):
            run_job(job)
            _notify(progress, f"Held-out attempt {completed}/{total_jobs} complete")
    else:
        with ThreadPoolExecutor(max_workers=config.max_workers) as executor:
            futures = [executor.submit(run_job, job) for job in jobs]
            for completed, future in enumerate(as_completed(futures), start=1):
                future.result()
                _notify(progress, f"Held-out attempt {completed}/{total_jobs} complete")
    return (
        stores["baseline"].load_attempts(fuzzer_kind=FUZZER_KIND_NATURAL_LANGUAGE),
        stores["learned"].load_attempts(fuzzer_kind=FUZZER_KIND_NATURAL_LANGUAGE),
    )


def _experiment_metrics(
    *,
    training_attempts: tuple[FuzzAttempt, ...],
    baseline_attempts: tuple[FuzzAttempt, ...],
    learned_attempts: tuple[FuzzAttempt, ...],
    bank: tuple[FuzzStrategy, ...],
) -> dict[str, object]:
    baseline = _arm_metrics(baseline_attempts)
    learned = _arm_metrics(learned_attempts)
    strategy_results = {}
    for strategy in bank:
        selected = tuple(
            attempt for attempt in learned_attempts if strategy.strategy_id in attempt.strategy_ids
        )
        strategy_results[strategy.strategy_id] = {
            "title": strategy.title,
            "math_topic": strategy.math_topic,
            "training_successes": strategy.successes,
            "training_failures": strategy.failures,
            "heldout_attempts": len(selected),
            "heldout_successes": sum(attempt.success for attempt in selected),
        }
    return {
        "training": _arm_metrics(training_attempts),
        "baseline": baseline,
        "learned": learned,
        "comparison": {
            "success_rate_delta": learned["success_rate"] - baseline["success_rate"],
            "valid_mutation_rate_delta": learned["valid_mutation_rate"] - baseline["valid_mutation_rate"],
            "fool_rate_given_valid_delta": learned["fool_rate_given_valid"] - baseline["fool_rate_given_valid"],
        },
        "strategies": strategy_results,
    }


def _arm_metrics(attempts: tuple[FuzzAttempt, ...]) -> dict[str, object]:
    total = len(attempts)
    successful = sum(attempt.success for attempt in attempts)
    valid = sum(
        attempt.mutation_check_result is not None
        and attempt.mutation_check_result.verdict == "incorrect"
        for attempt in attempts
    )
    by_problem = {}
    for problem_id in sorted({str(a.metadata.get("example_id")) for a in attempts}):
        selected = tuple(a for a in attempts if str(a.metadata.get("example_id")) == problem_id)
        by_problem[problem_id] = {
            "attempts": len(selected),
            "successes": sum(a.success for a in selected),
            "success_rate": _rate(sum(a.success for a in selected), len(selected)),
            "valid_mutations": sum(
                a.mutation_check_result is not None and a.mutation_check_result.verdict == "incorrect"
                for a in selected
            ),
        }
    outcomes = Counter(
        "pipeline_failure"
        if attempt.status == "failed"
        else "invalid_mutation"
        if attempt.mutation_check_result is None or attempt.mutation_check_result.verdict != "incorrect"
        else "fooled_target"
        if attempt.success
        else "caught_by_target"
        for attempt in attempts
    )
    return {
        "attempts": total,
        "successes": successful,
        "success_rate": _rate(successful, total),
        "valid_mutations": valid,
        "valid_mutation_rate": _rate(valid, total),
        "fool_rate_given_valid": _rate(successful, valid),
        "failed_attempts": sum(attempt.status == "failed" for attempt in attempts),
        "outcomes": dict(sorted(outcomes.items())),
        "by_problem": by_problem,
    }


def _attempts_by_ids(
    store: ProofFuzzAttemptStore,
    attempt_ids: tuple[str, ...],
) -> tuple[FuzzAttempt, ...]:
    by_id = {
        attempt.attempt_id: attempt
        for attempt in store.load_attempts(fuzzer_kind=FUZZER_KIND_NATURAL_LANGUAGE)
    }
    return tuple(by_id[attempt_id] for attempt_id in attempt_ids if attempt_id in by_id)


def _tokens(text: str) -> tuple[str, ...]:
    return tuple(re.findall(r"[a-zA-Z][a-zA-Z0-9_]{2,}", text.lower()))


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
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _read_json(path: Path) -> dict[str, object]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"Expected a JSON object in {path}.")
    return value


def _notify(progress: Callable[[str], None] | None, message: str) -> None:
    if progress is not None:
        progress(message)
