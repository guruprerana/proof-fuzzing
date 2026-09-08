"""Evolutionary proof fuzzing for OpenAI's 2026 ten-advances manuscripts."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re

from src.proof_fuzzer.evolution import EvolutionConfig, FuzzAttempt
from src.proof_fuzzer.llm_interface import LLMClient
from src.proof_fuzzer.proof_bench_judge import (
    ProofBenchJudgeEvolutionRunConfig,
    infer_math_topic,
    resolve_proof_bench_judge_evolution_storage_dir,
    run_natural_language_proof_examples_evolutionary_pipeline,
    write_proof_bench_judge_evolution_run_config,
)
from src.proof_fuzzer.reporting import write_standard_source_reports
from src.proof_fuzzer.vllm_client import VLLMProofFuzzerClient


DEFAULT_OPENAI_TEN_ADVANCES_ROOT = Path(
    "logs/openai_ten_advances_2026/proofs_markdown"
)


@dataclass(frozen=True)
class OpenAITenAdvancesEvolutionRunConfig(ProofBenchJudgeEvolutionRunConfig):
    """Hyperparameters for fuzzing the ten OpenAI proof manuscripts."""

    root: str | Path = DEFAULT_OPENAI_TEN_ADVANCES_ROOT
    num_attempts: int | None = 200
    max_proof_chars: int = 300_000
    max_problem_chars: int = 12_000
    run_pre_mutation_judge: bool = False
    evolution_threshold: int = 10
    correctness_selection_mode: str = "false_proof"
    false_proof_probability: float = 1.0
    judge_error_detection_check: bool = True
    seed_mined_strategies: bool = False


@dataclass(frozen=True)
class OpenAITenAdvancesEvolutionRunResult:
    """Summary of one ten-advances evolutionary run."""

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
class OpenAITenAdvancesProof:
    """One natural-language proof manuscript and its extracted claim summary."""

    example_id: str
    path: Path
    title: str
    abstract: str
    proof: str

    @property
    def problem(self) -> str:
        return f"{self.title}\n\nAbstract. {self.abstract}".strip()

    @property
    def llm_category(self) -> str:
        return infer_math_topic(f"{self.title}\n{self.abstract}\n{self.proof}")

    def to_metadata(self) -> dict[str, object]:
        metadata: dict[str, object] = {
            "dataset": "openai_ten_advances_2026",
            "example_id": self.example_id,
            "example_path": str(self.path),
            "problem_id": self.example_id,
            "problem": self.problem,
            "title": self.title,
            "correctness": True,
        }
        if self.llm_category:
            metadata["llm_category"] = self.llm_category
        return metadata


def load_openai_ten_advances_proofs(
    root: str | Path = DEFAULT_OPENAI_TEN_ADVANCES_ROOT,
    *,
    limit: int | None = None,
) -> tuple[OpenAITenAdvancesProof, ...]:
    """Load each Markdown manuscript and extract its title and abstract."""

    path = Path(root).expanduser()
    if not path.is_dir():
        raise FileNotFoundError(
            f"OpenAI ten-advances proof directory does not exist: {path}"
        )
    files = sorted(path.glob("*.md"))
    if limit is not None:
        files = files[:limit]
    return tuple(_load_proof(file_path) for file_path in files)


def run_openai_ten_advances_evolution(
    run_config: OpenAITenAdvancesEvolutionRunConfig | None = None,
    *,
    llm: LLMClient | None = None,
) -> OpenAITenAdvancesEvolutionRunResult:
    """Run the full evolutionary loop on the ten proof manuscripts."""

    active_run_config = run_config or OpenAITenAdvancesEvolutionRunConfig()
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
    examples = load_openai_ten_advances_proofs(
        active_run_config.root,
        limit=active_run_config.limit,
    )
    attempts = run_natural_language_proof_examples_evolutionary_pipeline(
        examples=examples,
        llm=active_llm,
        config=evolution_config,
        objective_prefix=active_run_config.objective_prefix,
        max_workers=active_run_config.max_workers,
        attempts_per_example=active_run_config.attempts_per_example,
        num_attempts=active_run_config.num_attempts,
        sample_offset=active_run_config.sample_offset,
        sample_without_replacement=active_run_config.sample_without_replacement,
        dataset_name="OpenAI ten-advances",
        proof_source="Markdown manuscript",
    )
    write_standard_source_reports(storage_dir)
    return OpenAITenAdvancesEvolutionRunResult(
        attempts=attempts,
        storage_dir=storage_dir,
    )


def _load_proof(path: Path) -> OpenAITenAdvancesProof:
    text = path.read_text(encoding="utf-8")
    title_match = re.search(r"^#\s+(.+?)\s*$", text, flags=re.MULTILINE)
    if title_match is None:
        raise ValueError(f"Proof Markdown has no level-one title: {path}")
    abstract_match = re.search(
        r"\bAbstract\.\s*(.*?)(?=\n\s*Contents\s*$)",
        text,
        flags=re.DOTALL | re.MULTILINE,
    )
    if abstract_match is None:
        raise ValueError(f"Proof Markdown has no extractable abstract: {path}")
    return OpenAITenAdvancesProof(
        example_id=path.stem,
        path=path,
        title=title_match.group(1).strip(),
        abstract=abstract_match.group(1).strip(),
        proof=text,
    )
