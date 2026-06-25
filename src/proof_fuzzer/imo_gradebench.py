"""IMO-GradeBench helpers for evolutionary proof fuzzing."""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import asdict
from dataclasses import dataclass
from dataclasses import replace
from datetime import datetime
import hashlib
import json
from pathlib import Path
import random
from typing import Iterable

from src.proof_fuzzer.evolution import (
    EvolutionConfig,
    EvolutionaryProofFuzzer,
    FUZZER_KIND_NATURAL_LANGUAGE,
    FuzzAttempt,
    ProofFuzzAttemptStore,
    truncate_text_head_tail,
)
from src.proof_fuzzer.llm_interface import LLMClient, NaturalLanguageProofFuzzerLLMInterface
from src.proof_fuzzer.reporting import write_standard_source_reports
from src.proof_fuzzer.vllm_client import (
    DEFAULT_BASE_URL,
    GPT_OSS_120B,
    VLLMProofFuzzerClient,
)


DEFAULT_IMO_GRADEBENCH_ROOT = Path(
    "~/common-data/reasoning-dataset/imo_gradebench/imo-gradebench/gradebench-model"
).expanduser()


@dataclass(frozen=True)
class IMOGradeBenchEvolutionRunConfig:
    """Hyperparameters for a complete IMO-GradeBench evolutionary fuzzing run."""

    root: str | Path = DEFAULT_IMO_GRADEBENCH_ROOT
    limit: int | None = None
    attempts_per_example: int = 1
    num_attempts: int | None = None
    sample_without_replacement: bool = False
    max_workers: int = 1
    storage_dir: str | Path | None = None
    run_name: str = ""
    base_url: str = DEFAULT_BASE_URL
    model: str = GPT_OSS_120B
    reasoning_effort: str = "high"
    temperature: float = 0.7
    max_tokens: int = 100_000
    strategy_probability: float = 0.5
    seed_mined_strategies: bool = False
    strategy_selection_mode: str = "random"
    mined_strategy_path: str | Path | None = None
    target_judge_samples: int = 1
    target_judge_success_policy: str = "all"
    judge_error_detection_check: bool = False
    max_previous_failed_attempts_in_prompt: int = 3
    max_previous_failed_attempt_chars: int = 4_000
    run_pre_mutation_judge: bool = True
    evolution_threshold: int = 20
    correctness_selection_mode: str = "adaptive"
    false_proof_probability: float = 0.7
    max_proof_chars: int = 24_000
    max_problem_chars: int = 4_000
    llm_retries: int = 3
    retry_backoff_seconds: float = 1.0
    context_fallbacks: int = 2
    continue_on_error: bool = False
    random_seed: int | None = None
    objective_prefix: str = ""


@dataclass(frozen=True)
class IMOGradeBenchEvolutionRunResult:
    """Summary for a complete IMO-GradeBench evolutionary fuzzing run."""

    attempts: tuple[FuzzAttempt, ...]
    storage_dir: Path

    @property
    def successes(self) -> int:
        return sum(1 for attempt in self.attempts if attempt.success)

    @property
    def failures(self) -> int:
        return sum(1 for attempt in self.attempts if attempt.status == "failed")

    def summary(self) -> str:
        return (
            f"Ran {len(self.attempts)} attempts; "
            f"successes={self.successes}; failures={self.failures}; storage={self.storage_dir}"
        )


@dataclass(frozen=True)
class IMOGradeBenchExample:
    """One IMO-GradeBench proof example with a correct model response."""

    example_id: str
    path: Path
    prompt: str
    response: str
    ground_truth: str
    correctness: bool
    metadata: dict[str, object]

    @property
    def problem(self) -> str:
        original_data = self.metadata.get("original_data")
        if isinstance(original_data, dict):
            return str(original_data.get("Problem", ""))
        return ""

    @property
    def grading_id(self) -> str:
        original_data = self.metadata.get("original_data")
        if isinstance(original_data, dict):
            return str(original_data.get("Grading ID", ""))
        return ""

    @property
    def llm_category(self) -> str:
        category = self.metadata.get("llm_category")
        if category:
            return str(category)
        original_data = self.metadata.get("original_data")
        if isinstance(original_data, dict):
            for key in ("llm_category", "category", "Category"):
                category = original_data.get(key)
                if category:
                    return str(category)
        return ""

    def to_metadata(self) -> dict[str, object]:
        metadata = {
            "dataset": "imo_gradebench",
            "example_id": self.example_id,
            "example_path": str(self.path),
            "grading_id": self.grading_id,
            "problem": self.problem,
            "correctness": self.correctness,
        }
        if self.llm_category:
            metadata["llm_category"] = self.llm_category
        return metadata


def run_imo_gradebench_evolution(
    run_config: IMOGradeBenchEvolutionRunConfig | None = None,
    *,
    llm: LLMClient | None = None,
) -> IMOGradeBenchEvolutionRunResult:
    """Run the full IMO-GradeBench evolutionary loop from hyperparameters."""

    active_run_config = run_config or IMOGradeBenchEvolutionRunConfig()
    storage_dir = resolve_imo_gradebench_evolution_storage_dir(
        active_run_config.storage_dir,
        run_name=active_run_config.run_name,
    )
    storage_dir.mkdir(parents=True, exist_ok=True)

    active_llm = llm or VLLMProofFuzzerClient(
        base_url=active_run_config.base_url,
        model=active_run_config.model,
        reasoning_effort=active_run_config.reasoning_effort,
        temperature=active_run_config.temperature,
        max_tokens=active_run_config.max_tokens,
    )
    evolution_config = EvolutionConfig(
        storage_dir=storage_dir,
        strategy_injection_probability=active_run_config.strategy_probability,
        evolution_threshold=active_run_config.evolution_threshold,
        random_seed=active_run_config.random_seed,
        correctness_selection_mode=active_run_config.correctness_selection_mode,
        false_proof_probability=active_run_config.false_proof_probability,
        max_proof_chars=active_run_config.max_proof_chars,
        max_problem_chars=active_run_config.max_problem_chars,
        llm_retries=active_run_config.llm_retries,
        retry_backoff_seconds=active_run_config.retry_backoff_seconds,
        context_fallbacks=active_run_config.context_fallbacks,
        continue_on_error=active_run_config.continue_on_error,
        seed_mined_strategies=active_run_config.seed_mined_strategies,
        strategy_selection_mode=active_run_config.strategy_selection_mode,
        mined_strategy_path=active_run_config.mined_strategy_path,
        target_judge_samples=active_run_config.target_judge_samples,
        target_judge_success_policy=active_run_config.target_judge_success_policy,
        judge_error_detection_check=active_run_config.judge_error_detection_check,
        max_previous_failed_attempts_in_prompt=active_run_config.max_previous_failed_attempts_in_prompt,
        max_previous_failed_attempt_chars=active_run_config.max_previous_failed_attempt_chars,
        run_pre_mutation_judge=active_run_config.run_pre_mutation_judge,
    )
    write_imo_gradebench_evolution_run_config(storage_dir, active_run_config)
    attempts = run_imo_gradebench_evolutionary_pipeline(
        llm=active_llm,
        root=active_run_config.root,
        limit=active_run_config.limit,
        config=evolution_config,
        objective_prefix=active_run_config.objective_prefix,
        max_workers=active_run_config.max_workers,
        attempts_per_example=active_run_config.attempts_per_example,
        num_attempts=active_run_config.num_attempts,
        sample_without_replacement=active_run_config.sample_without_replacement,
    )
    write_standard_source_reports(storage_dir)
    return IMOGradeBenchEvolutionRunResult(
        attempts=attempts,
        storage_dir=storage_dir,
    )


def load_correct_imo_gradebench_examples(
    root: str | Path = DEFAULT_IMO_GRADEBENCH_ROOT,
    *,
    limit: int | None = None,
) -> tuple[IMOGradeBenchExample, ...]:
    """Load examples whose ``correctness.txt`` is true."""

    examples: list[IMOGradeBenchExample] = []
    for example_dir in _iter_example_dirs(Path(root).expanduser()):
        example = load_imo_gradebench_example(example_dir)
        if not example.correctness:
            continue
        examples.append(example)
        if limit is not None and len(examples) >= limit:
            break
    return tuple(examples)


def load_imo_gradebench_example(example_dir: str | Path) -> IMOGradeBenchExample:
    """Load one IMO-GradeBench example directory."""

    path = Path(example_dir)
    correctness_path = path / "correctness.txt"
    response_path = path / "response.txt"
    prompt_path = path / "prompt.txt"
    ground_truth_path = path / "ground_truth.txt"
    metadata_path = path / "metadata.json"

    missing = [
        file_path.name
        for file_path in (correctness_path, response_path, prompt_path, ground_truth_path, metadata_path)
        if not file_path.is_file()
    ]
    if missing:
        raise FileNotFoundError(f"{path} is missing required files: {', '.join(missing)}")

    return IMOGradeBenchExample(
        example_id=path.name,
        path=path,
        prompt=prompt_path.read_text(encoding="utf-8"),
        response=response_path.read_text(encoding="utf-8"),
        ground_truth=ground_truth_path.read_text(encoding="utf-8"),
        correctness=_parse_correctness(correctness_path.read_text(encoding="utf-8")),
        metadata=json.loads(metadata_path.read_text(encoding="utf-8")),
    )


def run_imo_gradebench_evolutionary_pipeline(
    *,
    llm: LLMClient,
    root: str | Path = DEFAULT_IMO_GRADEBENCH_ROOT,
    limit: int | None = None,
    config: EvolutionConfig | None = None,
    store: ProofFuzzAttemptStore | None = None,
    objective_prefix: str = "",
    max_workers: int = 1,
    attempts_per_example: int = 1,
    num_attempts: int | None = None,
    sample_without_replacement: bool = False,
) -> tuple[FuzzAttempt, ...]:
    """Run natural-language evolutionary fuzzing on correct IMO-GradeBench proofs."""

    if max_workers < 1:
        raise ValueError("max_workers must be at least 1.")
    if attempts_per_example < 1:
        raise ValueError("attempts_per_example must be at least 1.")
    if num_attempts is not None and num_attempts < 1:
        raise ValueError("num_attempts must be at least 1 when provided.")

    active_config = config or EvolutionConfig(
        storage_dir="logs/proof_fuzzer_evolution/imo_gradebench",
    )
    active_store = store or ProofFuzzAttemptStore(active_config.storage_dir)
    examples = load_correct_imo_gradebench_examples(root, limit=limit)
    work_items = _sample_work_items(
        examples,
        attempts_per_example=attempts_per_example,
        num_attempts=num_attempts,
        sample_without_replacement=sample_without_replacement,
        random_seed=active_config.random_seed,
    )
    if max_workers == 1:
        return tuple(
            _run_one_imo_gradebench_attempt(
                example,
                llm=llm,
                store=active_store,
                config=active_config,
                objective_prefix=objective_prefix,
                attempt_index=attempt_index,
                sample_index=index,
            )
            for index, example, attempt_index in work_items
        )

    attempts_by_index: dict[int, FuzzAttempt] = {}
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(
                _run_one_imo_gradebench_attempt,
                example,
                llm=llm,
                store=active_store,
                config=active_config,
                objective_prefix=objective_prefix,
                attempt_index=attempt_index,
                sample_index=index,
            ): index
            for index, example, attempt_index in work_items
        }
        for future in as_completed(futures):
            attempts_by_index[futures[future]] = future.result()
    return tuple(attempts_by_index[index] for index in sorted(attempts_by_index))


def _run_one_imo_gradebench_attempt(
    example: IMOGradeBenchExample,
    *,
    llm: LLMClient,
    store: ProofFuzzAttemptStore,
    config: EvolutionConfig,
    objective_prefix: str = "",
    attempt_index: int = 0,
    sample_index: int = 0,
) -> FuzzAttempt:
    proof_text = truncate_text_head_tail(example.response, config.max_proof_chars)
    fuzzer = NaturalLanguageProofFuzzerLLMInterface(proof_text, llm)
    attempt_config = replace(
        config,
        random_seed=_derive_attempt_seed(
            config.random_seed,
            sample_index=sample_index,
            example_id=example.example_id,
            attempt_index=attempt_index,
        ),
    )
    evolutionary = EvolutionaryProofFuzzer(
        fuzzer,
        store=store,
        config=attempt_config,
    )
    metadata = {
        **example.to_metadata(),
        "example_attempt_index": attempt_index,
        "sample_index": sample_index,
        "proof_source": "response.txt",
        "fuzzer_kind": FUZZER_KIND_NATURAL_LANGUAGE,
        "proof_chars_original": len(example.response),
        "proof_chars_used": len(proof_text),
        "prompt_truncated": len(proof_text) < len(example.response),
    }
    return evolutionary.run_mutation_attempt(
        objective=_format_objective(
            example,
            objective_prefix=objective_prefix,
            max_problem_chars=config.max_problem_chars,
        ),
        metadata=metadata,
    )


def _format_objective(
    example: IMOGradeBenchExample,
    *,
    objective_prefix: str = "",
    max_problem_chars: int | None = None,
) -> str:
    prefix = objective_prefix.strip()
    pieces = []
    if prefix:
        pieces.append(prefix)
    pieces.append("Fuzz this correct IMO-GradeBench proof.")
    if example.problem:
        problem = (
            truncate_text_head_tail(example.problem, max_problem_chars)
            if max_problem_chars is not None
            else example.problem
        )
        pieces.append(f"Problem:\n{problem}")
    return "\n\n".join(pieces)


def _sample_work_items(
    examples: tuple[IMOGradeBenchExample, ...],
    *,
    attempts_per_example: int,
    num_attempts: int | None,
    sample_without_replacement: bool,
    random_seed: int | None,
) -> list[tuple[int, IMOGradeBenchExample, int]]:
    if not examples:
        return []
    if num_attempts is None:
        return [
            (index, example, attempt_index)
            for index, (example, attempt_index) in enumerate(
                (example, attempt_index)
                for example in examples
                for attempt_index in range(attempts_per_example)
            )
        ]

    rng = random.Random(random_seed)
    if sample_without_replacement:
        if num_attempts > len(examples):
            raise ValueError("num_attempts cannot exceed available examples when sampling without replacement.")
        sampled = rng.sample(list(examples), k=num_attempts)
    else:
        sampled = [rng.choice(examples) for _ in range(num_attempts)]
    seen: dict[str, int] = {}
    work_items = []
    for sample_index, example in enumerate(sampled):
        attempt_index = seen.get(example.example_id, 0)
        seen[example.example_id] = attempt_index + 1
        work_items.append((sample_index, example, attempt_index))
    return work_items


def resolve_imo_gradebench_evolution_storage_dir(
    storage_dir: str | Path | None,
    *,
    run_name: str = "",
) -> Path:
    base = Path("logs/proof_fuzzer_evolution")
    name = run_name.strip() or f"imo_gradebench_oss120b_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    if storage_dir is None:
        return base / name
    path = Path(storage_dir)
    if path == Path("logs") or path == base:
        return path / name
    if path.name in {"logs", "proof_fuzzer_evolution"}:
        return path / name
    return path


def write_imo_gradebench_evolution_run_config(
    storage_dir: str | Path,
    run_config: IMOGradeBenchEvolutionRunConfig,
) -> Path:
    config = {
        key: str(value) if isinstance(value, Path) else value
        for key, value in asdict(run_config).items()
    }
    config["resolved_storage_dir"] = str(storage_dir)
    path = Path(storage_dir) / "run_config.json"
    path.write_text(
        json.dumps(config, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    return path


def _iter_example_dirs(root: Path) -> Iterable[Path]:
    if not root.is_dir():
        raise FileNotFoundError(f"IMO-GradeBench root does not exist or is not a directory: {root}")
    return (
        path
        for path in sorted(root.iterdir())
        if path.is_dir() and (path / "correctness.txt").is_file()
    )


def _parse_correctness(text: str) -> bool:
    value = text.strip().lower()
    if value in {"true", "t", "1", "yes"}:
        return True
    if value in {"false", "f", "0", "no"}:
        return False
    raise ValueError(f"Unknown correctness value: {text!r}")


def _derive_attempt_seed(
    seed: int | None,
    *,
    sample_index: int,
    example_id: str,
    attempt_index: int,
) -> int | None:
    if seed is None:
        return None
    material = f"{seed}:{sample_index}:{example_id}:{attempt_index}".encode("utf-8")
    return int.from_bytes(hashlib.sha256(material).digest()[:8], "big")
