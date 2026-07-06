"""ProofBenchJudge helpers for evolutionary proof fuzzing."""

from __future__ import annotations

from concurrent.futures import FIRST_COMPLETED, ThreadPoolExecutor, wait
from dataclasses import asdict, dataclass, replace
from datetime import datetime
import hashlib
import json
from pathlib import Path
import random
import re
from typing import Iterable

from src.proof_fuzzer.evolution import (
    EvolutionConfig,
    EvolutionaryProofFuzzer,
    FUZZER_KIND_NATURAL_LANGUAGE,
    FuzzAttempt,
    ProofFuzzAttemptStore,
    truncate_text_head_tail,
    usage_limit_reached,
)
from src.proof_fuzzer.llm_interface import LLMClient, NaturalLanguageProofFuzzerLLMInterface
from src.proof_fuzzer.reporting import write_standard_source_reports
from src.proof_fuzzer.vllm_client import (
    DEFAULT_BASE_URL,
    GPT_OSS_120B,
    VLLMProofFuzzerClient,
)


DEFAULT_PROOF_BENCH_JUDGE_ROOT = Path(
    "~/common-data/reasoning-dataset/proof_bench_judge/proof_bench_judge/proofbenchjudgemodel"
).expanduser()


@dataclass(frozen=True)
class ProofBenchJudgeEvolutionRunConfig:
    """Hyperparameters for a complete ProofBenchJudge evolutionary fuzzing run."""

    root: str | Path = DEFAULT_PROOF_BENCH_JUDGE_ROOT
    limit: int | None = None
    attempts_per_example: int = 1
    num_attempts: int | None = None
    sample_offset: int = 0
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
    max_previous_successful_attempts_in_prompt: int = 3
    max_previous_successful_attempt_chars: int = 4_000
    reject_duplicate_successful_mutations: bool = False
    duplicate_successful_mutation_retries: int = 1
    duplicate_successful_mutation_reject_policy: str = "duplicate_or_variant"
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
class ProofBenchJudgeEvolutionRunResult:
    """Summary for a complete ProofBenchJudge evolutionary fuzzing run."""

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
class ProofBenchJudgeExample:
    """One ProofBenchJudge proof example."""

    example_id: str
    path: Path
    prompt: str
    response: str
    ground_truth: str
    correctness: bool
    metadata: dict[str, object]

    @property
    def original_data(self) -> dict[str, object]:
        value = self.metadata.get("original_data")
        return value if isinstance(value, dict) else {}

    @property
    def problem(self) -> str:
        return str(self.original_data.get("problem", ""))

    @property
    def proof(self) -> str:
        return str(self.original_data.get("proof", self.metadata.get("full_response", "")))

    @property
    def rubric(self) -> str:
        return str(self.original_data.get("rubric", ""))

    @property
    def problem_id(self) -> str:
        return str(self.original_data.get("problem_id", ""))

    @property
    def llm_category(self) -> str:
        return infer_math_topic(" ".join((self.problem_id, self.problem, self.rubric, self.proof)))

    def to_metadata(self) -> dict[str, object]:
        metadata = {
            "dataset": "proof_bench_judge",
            "example_id": self.example_id,
            "example_path": str(self.path),
            "problem_id": self.problem_id,
            "problem": self.problem,
            "rubric": self.rubric,
            "correctness": self.correctness,
        }
        if self.llm_category:
            metadata["llm_category"] = self.llm_category
        return metadata


def run_proof_bench_judge_evolution(
    run_config: ProofBenchJudgeEvolutionRunConfig | None = None,
    *,
    llm: LLMClient | None = None,
) -> ProofBenchJudgeEvolutionRunResult:
    """Run the full ProofBenchJudge evolutionary loop from hyperparameters."""

    active_run_config = run_config or ProofBenchJudgeEvolutionRunConfig()
    storage_dir = resolve_proof_bench_judge_evolution_storage_dir(
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
        max_previous_successful_attempts_in_prompt=active_run_config.max_previous_successful_attempts_in_prompt,
        max_previous_successful_attempt_chars=active_run_config.max_previous_successful_attempt_chars,
        reject_duplicate_successful_mutations=active_run_config.reject_duplicate_successful_mutations,
        duplicate_successful_mutation_retries=active_run_config.duplicate_successful_mutation_retries,
        duplicate_successful_mutation_reject_policy=active_run_config.duplicate_successful_mutation_reject_policy,
        run_pre_mutation_judge=active_run_config.run_pre_mutation_judge,
    )
    write_proof_bench_judge_evolution_run_config(storage_dir, active_run_config)
    attempts = run_proof_bench_judge_evolutionary_pipeline(
        llm=active_llm,
        root=active_run_config.root,
        limit=active_run_config.limit,
        config=evolution_config,
        objective_prefix=active_run_config.objective_prefix,
        max_workers=active_run_config.max_workers,
        attempts_per_example=active_run_config.attempts_per_example,
        num_attempts=active_run_config.num_attempts,
        sample_offset=active_run_config.sample_offset,
        sample_without_replacement=active_run_config.sample_without_replacement,
    )
    write_standard_source_reports(storage_dir)
    return ProofBenchJudgeEvolutionRunResult(attempts=attempts, storage_dir=storage_dir)


def load_correct_proof_bench_judge_examples(
    root: str | Path = DEFAULT_PROOF_BENCH_JUDGE_ROOT,
    *,
    limit: int | None = None,
) -> tuple[ProofBenchJudgeExample, ...]:
    """Load examples whose ground-truth judgement says the proof is correct."""

    examples: list[ProofBenchJudgeExample] = []
    for example_dir in _iter_example_dirs(Path(root).expanduser()):
        example = load_proof_bench_judge_example(example_dir)
        if not example.correctness:
            continue
        examples.append(example)
        if limit is not None and len(examples) >= limit:
            break
    return tuple(examples)


def load_proof_bench_judge_example(example_dir: str | Path) -> ProofBenchJudgeExample:
    """Load one ProofBenchJudge example directory."""

    path = Path(example_dir)
    prompt_path = path / "prompt.txt"
    response_path = path / "response.txt"
    ground_truth_path = path / "ground_truth.txt"
    metadata_path = path / "metadata.json"
    missing = [
        file_path.name
        for file_path in (prompt_path, response_path, ground_truth_path, metadata_path)
        if not file_path.is_file()
    ]
    if missing:
        raise FileNotFoundError(f"{path} is missing required files: {', '.join(missing)}")

    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    return ProofBenchJudgeExample(
        example_id=path.name,
        path=path,
        prompt=prompt_path.read_text(encoding="utf-8"),
        response=response_path.read_text(encoding="utf-8"),
        ground_truth=ground_truth_path.read_text(encoding="utf-8"),
        correctness=_parse_correctness(metadata, ground_truth_path.read_text(encoding="utf-8")),
        metadata=metadata,
    )


def run_proof_bench_judge_evolutionary_pipeline(
    *,
    llm: LLMClient,
    root: str | Path = DEFAULT_PROOF_BENCH_JUDGE_ROOT,
    limit: int | None = None,
    config: EvolutionConfig | None = None,
    store: ProofFuzzAttemptStore | None = None,
    objective_prefix: str = "",
    max_workers: int = 1,
    attempts_per_example: int = 1,
    num_attempts: int | None = None,
    sample_offset: int = 0,
    sample_without_replacement: bool = False,
) -> tuple[FuzzAttempt, ...]:
    """Run natural-language evolutionary fuzzing on correct ProofBenchJudge proofs."""

    if max_workers < 1:
        raise ValueError("max_workers must be at least 1.")
    if attempts_per_example < 1:
        raise ValueError("attempts_per_example must be at least 1.")
    if num_attempts is not None and num_attempts < 1:
        raise ValueError("num_attempts must be at least 1 when provided.")
    if sample_offset < 0:
        raise ValueError("sample_offset must be non-negative.")

    active_config = config or EvolutionConfig(
        storage_dir="logs/proof_fuzzer_evolution/proof_bench_judge",
    )
    active_store = store or ProofFuzzAttemptStore(active_config.storage_dir)
    examples = load_correct_proof_bench_judge_examples(root, limit=limit)
    work_items = _sample_work_items(
        examples,
        attempts_per_example=attempts_per_example,
        num_attempts=num_attempts,
        sample_offset=sample_offset,
        sample_without_replacement=sample_without_replacement,
        random_seed=active_config.random_seed,
    )
    if max_workers == 1:
        attempts: list[FuzzAttempt] = []
        for index, example, attempt_index in work_items:
            attempt = _run_one_proof_bench_judge_attempt(
                example,
                llm=llm,
                store=active_store,
                config=active_config,
                objective_prefix=objective_prefix,
                attempt_index=attempt_index,
                sample_index=index,
            )
            attempts.append(attempt)
            if usage_limit_reached(attempt):
                break
        return tuple(attempts)

    attempts_by_index: dict[int, FuzzAttempt] = {}
    work_iter = iter(work_items)
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {}

        def submit_next() -> bool:
            try:
                index, example, attempt_index = next(work_iter)
            except StopIteration:
                return False
            future = executor.submit(
                _run_one_proof_bench_judge_attempt,
                example,
                llm=llm,
                store=active_store,
                config=active_config,
                objective_prefix=objective_prefix,
                attempt_index=attempt_index,
                sample_index=index,
            )
            futures[future] = index
            return True

        for _ in range(min(max_workers, len(work_items))):
            submit_next()

        stop_for_usage_limit = False
        while futures:
            done, _ = wait(futures, return_when=FIRST_COMPLETED)
            for future in done:
                index = futures.pop(future)
                try:
                    attempt = future.result()
                except Exception as exc:
                    if usage_limit_reached(exc):
                        stop_for_usage_limit = True
                    for pending in futures:
                        pending.cancel()
                    raise
                attempts_by_index[index] = attempt
                if usage_limit_reached(attempt):
                    stop_for_usage_limit = True
            if stop_for_usage_limit:
                for pending in futures:
                    pending.cancel()
                break
            while len(futures) < max_workers and submit_next():
                pass
    return tuple(attempts_by_index[index] for index in sorted(attempts_by_index))


def infer_math_topic(text: str) -> str:
    """Infer a coarse math topic from problem/rubric/proof text."""

    lowered = text.lower()
    scores = {
        "geometry": _keyword_score(
            lowered,
            "triangle", "circle", "angle", "collinear", "concurrent", "tangent", "altitude", "cyclic",
            "perpendicular", "parallel", "midpoint", "circumcircle", "incenter",
        ),
        "number_theory": _keyword_score(
            lowered,
            "modulo", "congruence", "divisible", "divisibility", "prime", "gcd", "coprime",
            "integer", "residue", "valuation", "factorization",
        ),
        "combinatorics": _keyword_score(
            lowered,
            "count", "subsets", "graph", "sequence", "pigeonhole", "probability", "permutation",
            "tableaux", "coloring", "combinatorial", "partition",
        ),
        "algebra": _keyword_score(
            lowered,
            "polynomial", "coefficient", "equation", "roots", "monic", "quadratic", "identity",
            "factor", "function", "real numbers",
        ),
        "analysis": _keyword_score(
            lowered,
            "limit", "continuous", "derivative", "integral", "converges", "sequence", "epsilon",
            "maximum", "minimum", "supremum",
        ),
    }
    topic, score = max(scores.items(), key=lambda item: item[1])
    return topic if score > 0 else ""


def resolve_proof_bench_judge_evolution_storage_dir(
    storage_dir: str | Path | None,
    *,
    run_name: str = "",
) -> Path:
    base = Path("logs/proof_fuzzer_evolution")
    name = run_name.strip() or f"proof_bench_judge_oss120b_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    if storage_dir is None:
        return base / name
    path = Path(storage_dir)
    if path == Path("logs") or path == base:
        return path / name
    if path.name in {"logs", "proof_fuzzer_evolution"}:
        return path / name
    return path


def write_proof_bench_judge_evolution_run_config(
    storage_dir: str | Path,
    run_config: ProofBenchJudgeEvolutionRunConfig,
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


def _run_one_proof_bench_judge_attempt(
    example: ProofBenchJudgeExample,
    *,
    llm: LLMClient,
    store: ProofFuzzAttemptStore,
    config: EvolutionConfig,
    objective_prefix: str = "",
    attempt_index: int = 0,
    sample_index: int = 0,
) -> FuzzAttempt:
    proof_text = truncate_text_head_tail(example.proof, config.max_proof_chars)
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
    evolutionary = EvolutionaryProofFuzzer(fuzzer, store=store, config=attempt_config)
    metadata = {
        **example.to_metadata(),
        "example_attempt_index": attempt_index,
        "sample_index": sample_index,
        "proof_source": "metadata.original_data.proof",
        "fuzzer_kind": FUZZER_KIND_NATURAL_LANGUAGE,
        "proof_chars_original": len(example.proof),
        "proof_chars_used": len(proof_text),
        "prompt_truncated": len(proof_text) < len(example.proof),
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
    example: ProofBenchJudgeExample,
    *,
    objective_prefix: str = "",
    max_problem_chars: int | None = None,
) -> str:
    prefix = objective_prefix.strip()
    pieces = []
    if prefix:
        pieces.append(prefix)
    pieces.append("Fuzz this correct ProofBenchJudge proof.")
    if example.problem:
        problem = (
            truncate_text_head_tail(example.problem, max_problem_chars)
            if max_problem_chars is not None
            else example.problem
        )
        pieces.append(f"Problem:\n{problem}")
    return "\n\n".join(pieces)


def _sample_work_items(
    examples: tuple[ProofBenchJudgeExample, ...],
    *,
    attempts_per_example: int,
    num_attempts: int | None,
    sample_offset: int,
    sample_without_replacement: bool,
    random_seed: int | None,
) -> list[tuple[int, ProofBenchJudgeExample, int]]:
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
    total_samples = num_attempts + sample_offset
    if sample_without_replacement:
        if total_samples > len(examples):
            raise ValueError("num_attempts cannot exceed available examples when sampling without replacement.")
        sampled = rng.sample(list(examples), k=total_samples)
    else:
        sampled = [rng.choice(examples) for _ in range(total_samples)]
    seen: dict[str, int] = {}
    work_items = []
    for sample_index, example in enumerate(sampled):
        attempt_index = seen.get(example.example_id, 0)
        seen[example.example_id] = attempt_index + 1
        if sample_index < sample_offset:
            continue
        work_items.append((sample_index, example, attempt_index))
    return work_items


def _iter_example_dirs(root: Path) -> Iterable[Path]:
    if not root.is_dir():
        raise FileNotFoundError(f"ProofBenchJudge root does not exist or is not a directory: {root}")
    return (
        path
        for path in sorted(root.iterdir())
        if path.is_dir() and (path / "metadata.json").is_file()
    )


def _parse_correctness(metadata: dict[str, object], ground_truth_text: str) -> bool:
    answer = metadata.get("ground_truth")
    if isinstance(answer, dict):
        parsed = _parse_yes_no(answer.get("answer"))
        if parsed is not None:
            return parsed
    parsed = _parse_yes_no(ground_truth_text)
    if parsed is not None:
        return parsed
    raise ValueError("ProofBenchJudge example does not contain a Yes/No ground-truth answer.")


def _parse_yes_no(value: object) -> bool | None:
    text = str(value or "").strip().lower()
    if text.startswith("judgement:"):
        text = text.split(":", 1)[1].strip()
    if text in {"yes", "true", "correct", "1"}:
        return True
    if text in {"no", "false", "incorrect", "0"}:
        return False
    return None


def _derive_attempt_seed(
    seed: int | None,
    *,
    sample_index: int,
    example_id: str,
    attempt_index: int,
) -> int | None:
    if seed is None:
        return None
    payload = f"{seed}:{sample_index}:{example_id}:{attempt_index}".encode("utf-8")
    return int.from_bytes(hashlib.sha256(payload).digest()[:8], "big")


def _keyword_score(text: str, *keywords: str) -> int:
    score = 0
    for keyword in keywords:
        score += len(re.findall(rf"\b{re.escape(keyword)}\b", text))
    return score
