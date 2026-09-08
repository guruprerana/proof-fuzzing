"""Generation-based evolution of one reusable natural-language mutation policy."""

from __future__ import annotations

from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field, replace
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import threading

from src.proof_fuzzer.evolution import (
    EvolutionConfig,
    EvolutionaryProofFuzzer,
    FUZZER_KIND_NATURAL_LANGUAGE,
    FuzzAttempt,
    ProofFuzzAttemptStore,
    truncate_text_head_tail,
    usage_limit_reached,
)
from src.proof_fuzzer.llm_interface import (
    LLMClient,
    NaturalLanguageProofFuzzerLLMInterface,
    _load_json_object as _load_llm_json_object,
)
from src.proof_fuzzer.proof_bench_judge import (
    NaturalLanguageProofExample,
    format_natural_language_proof_objective,
    sample_natural_language_proof_work_items,
)


DEFAULT_MUTATION_POLICY = """Goal:
Produce a subtle, mathematically consequential error while leaving the proof plausible
enough to be accepted by the target judge.

Strategies:
- Find an indispensable dependency and weaken, omit, or misuse it.
- Prefer hidden quantifier, scope, boundary-case, hypothesis, or implication errors.
- Propagate the changed premise or inference through dependent equations, claims, and notation
  when leaving them untouched would create an unnatural contradiction. Every companion edit must
  be a consequence of the same planted root error.
- Target steps whose failure is difficult to notice from the surrounding prose alone.

Do not:
- Make cosmetic edits or introduce harmless false statements.
- Introduce an error that another part of the proof repairs or bypasses.
- Use self-incriminating words such as "incorrect", "mistake", "flaw", or "omitted" in the mutated proof.
- Change the conclusion directly without leaving a plausible argument for it.
- Produce inconsistent notation that reveals the mutation mechanically.
- Treat propagation as permission to add a second independent error or gratuitous clues.

Before returning:
1. Identify the first indispensable step that becomes invalid.
2. Verify that no alternate argument in the mutated proof still proves the conclusion.
3. Verify that the proof remains natural and internally consistent apart from the intended error.
4. Trace the affected dependencies and propagate the error wherever coherence requires it.
5. If any check fails, choose a different mutation."""


@dataclass(frozen=True)
class PromptEvolutionConfig:
    """Configuration for evolving one mutation policy between attempt batches."""

    storage_dir: str | Path = "logs/proof_fuzzer_prompt_evolution"
    generation_size: int = 20
    evolution_window: int = 60
    max_prompt_chars: int = 5_000
    max_prompt_growth_chars: int = 400
    max_prompt_length_multiplier: float = 2.0
    max_attempt_summary_chars: int = 1_200
    max_evolution_context_chars: int = 40_000
    initial_prompt: str = DEFAULT_MUTATION_POLICY
    continue_on_evolution_error: bool = True
    evolution_retries: int = 1
    random_seed: int | None = None

    def __post_init__(self) -> None:
        if self.generation_size < 1:
            raise ValueError("generation_size must be at least 1.")
        if self.evolution_window < 1:
            raise ValueError("evolution_window must be at least 1.")
        if self.max_prompt_chars < 1:
            raise ValueError("max_prompt_chars must be at least 1.")
        if self.max_prompt_growth_chars < 0:
            raise ValueError("max_prompt_growth_chars must be non-negative.")
        if self.max_prompt_length_multiplier < 1.0:
            raise ValueError("max_prompt_length_multiplier must be at least 1.0.")
        if self.max_attempt_summary_chars < 400:
            raise ValueError("max_attempt_summary_chars must be at least 400.")
        if self.max_evolution_context_chars < 1:
            raise ValueError("max_evolution_context_chars must be at least 1.")
        if self.max_evolution_context_chars < self.max_attempt_summary_chars:
            raise ValueError(
                "max_evolution_context_chars must be at least max_attempt_summary_chars."
            )
        if self.evolution_retries < 0:
            raise ValueError("evolution_retries must be non-negative.")
        _validate_mutation_policy(self.initial_prompt, max_chars=self.max_prompt_chars)


@dataclass(frozen=True)
class MutationPromptVersion:
    """One immutable version of the evolved mutation policy."""

    version: int
    prompt_text: str
    parent_version: int | None = None
    training_attempt_ids: tuple[str, ...] = ()
    change_summary: str = "Initial mutation policy."
    created_at: str = field(default_factory=lambda: _utc_now())
    metrics: dict[str, int | float] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.version < 0:
            raise ValueError("Mutation prompt version must be non-negative.")
        object.__setattr__(self, "prompt_text", self.prompt_text.strip())
        object.__setattr__(self, "training_attempt_ids", tuple(self.training_attempt_ids))
        object.__setattr__(self, "metrics", dict(self.metrics))

    @property
    def prompt_sha256(self) -> str:
        return hashlib.sha256(self.prompt_text.encode("utf-8")).hexdigest()

    def to_dict(self) -> dict[str, object]:
        return {
            "version": self.version,
            "prompt_text": self.prompt_text,
            "prompt_sha256": self.prompt_sha256,
            "parent_version": self.parent_version,
            "training_attempt_ids": list(self.training_attempt_ids),
            "change_summary": self.change_summary,
            "created_at": self.created_at,
            "metrics": dict(self.metrics),
        }

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "MutationPromptVersion":
        version = cls(
            version=int(data.get("version", 0)),
            prompt_text=str(data.get("prompt_text", "")),
            parent_version=(
                int(data["parent_version"])
                if data.get("parent_version") is not None
                else None
            ),
            training_attempt_ids=_string_tuple(data.get("training_attempt_ids", ())),
            change_summary=str(data.get("change_summary", "")),
            created_at=str(data.get("created_at") or _utc_now()),
            metrics=_numeric_dict(data.get("metrics")),
        )
        expected_hash = str(data.get("prompt_sha256", ""))
        if expected_hash and expected_hash != version.prompt_sha256:
            raise ValueError("Stored mutation prompt hash does not match its text.")
        return version


class MutationPromptStore:
    """Persists the active policy and its append-only version history."""

    def __init__(self, root_dir: str | Path):
        self.root_dir = Path(root_dir)
        self.root_dir.mkdir(parents=True, exist_ok=True)
        self.current_path = self.root_dir / "mutation_prompt_current.json"
        self.history_path = self.root_dir / "mutation_prompt_history.jsonl"
        self.error_path = self.root_dir / "mutation_prompt_evolution_errors.jsonl"
        self.lock = threading.RLock()

    def initialize(self, prompt_text: str, *, max_chars: int) -> MutationPromptVersion:
        with self.lock:
            current = self.load_current()
            if current is not None:
                _validate_mutation_policy(current.prompt_text, max_chars=max_chars)
                return current
            _validate_mutation_policy(prompt_text, max_chars=max_chars)
            initial = MutationPromptVersion(version=0, prompt_text=prompt_text)
            self._append_history(initial)
            self._write_current(initial)
            return initial

    def load_current(self) -> MutationPromptVersion | None:
        with self.lock:
            if not self.current_path.is_file():
                return None
            data = json.loads(self.current_path.read_text(encoding="utf-8"))
            if not isinstance(data, dict):
                raise ValueError("Current mutation prompt must be a JSON object.")
            return MutationPromptVersion.from_dict(data)

    def load_history(self) -> tuple[MutationPromptVersion, ...]:
        with self.lock:
            if not self.history_path.is_file():
                return ()
            versions = []
            for line in self.history_path.read_text(encoding="utf-8").splitlines():
                if not line.strip():
                    continue
                data = json.loads(line)
                if not isinstance(data, dict):
                    raise ValueError("Mutation prompt history entries must be JSON objects.")
                versions.append(MutationPromptVersion.from_dict(data))
            return tuple(versions)

    def save(self, version: MutationPromptVersion, *, max_chars: int) -> None:
        with self.lock:
            _validate_mutation_policy(version.prompt_text, max_chars=max_chars)
            current = self.load_current()
            if current is None:
                raise ValueError("Initialize the mutation prompt store before saving a new version.")
            if version.parent_version != current.version:
                raise ValueError("New mutation prompt must name the current version as its parent.")
            if version.version != current.version + 1:
                raise ValueError("New mutation prompt version must increment the current version by one.")
            if version.prompt_sha256 == current.prompt_sha256:
                raise ValueError("Evolved mutation prompt must differ from its parent.")
            self._append_history(version)
            self._write_current(version)

    def record_error(
        self,
        *,
        version: MutationPromptVersion,
        attempt_ids: tuple[str, ...],
        error: Exception,
    ) -> None:
        payload = {
            "version": version.version,
            "prompt_sha256": version.prompt_sha256,
            "attempt_ids": list(attempt_ids),
            "error": repr(error),
            "created_at": _utc_now(),
        }
        with self.lock:
            with self.error_path.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(payload, sort_keys=True) + "\n")

    def _append_history(self, version: MutationPromptVersion) -> None:
        with self.history_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(version.to_dict(), sort_keys=True) + "\n")

    def _write_current(self, version: MutationPromptVersion) -> None:
        temporary = self.current_path.with_suffix(".json.tmp")
        temporary.write_text(
            json.dumps(version.to_dict(), indent=2, sort_keys=True),
            encoding="utf-8",
        )
        temporary.replace(self.current_path)


class MutationPromptEvolver:
    """Rewrites the complete mutation policy using judged attempt outcomes."""

    def __init__(self, llm: LLMClient):
        self.llm = llm

    def evolve(
        self,
        *,
        current: MutationPromptVersion,
        attempts: tuple[FuzzAttempt, ...],
        config: PromptEvolutionConfig,
    ) -> MutationPromptVersion:
        if not attempts:
            raise ValueError("At least one attempt is required to evolve the mutation prompt.")
        outcomes = Counter(_attempt_outcome(attempt) for attempt in attempts)
        successes = outcomes.get("success", 0)
        allowed_prompt_chars = _evolved_prompt_char_limit(
            current=current,
            successes=successes,
            config=config,
        )
        prompt = self.evolution_prompt(current=current, attempts=attempts, config=config)
        last_error: Exception | None = None
        data: dict[str, object] = {}
        prompt_text = ""
        for retry_index in range(config.evolution_retries + 1):
            response = self.llm.complete(prompt)
            try:
                data = _load_llm_json_object(response)
                prompt_text = str(data.get("prompt_text", "")).strip()
                _validate_mutation_policy(prompt_text, max_chars=allowed_prompt_chars)
                if prompt_text == current.prompt_text:
                    raise ValueError("Evolved mutation prompt must differ from its parent.")
                break
            except (TypeError, ValueError) as exc:
                last_error = exc
                if retry_index >= config.evolution_retries:
                    raise
                prompt = (
                    self.evolution_prompt(current=current, attempts=attempts, config=config)
                    + "\nYour previous replacement was rejected by the validator for this reason:\n"
                    + f"{exc}\nReturn a corrected JSON object that strictly satisfies every constraint.\n"
                )
        if not prompt_text:
            raise last_error or ValueError("No evolved mutation prompt was produced.")
        metrics: dict[str, int | float] = {
            "attempts": len(attempts),
            "successes": successes,
            "success_rate": successes / len(attempts),
            "prompt_char_limit": allowed_prompt_chars,
        }
        metrics.update({f"outcome_{key}": value for key, value in outcomes.items()})
        return MutationPromptVersion(
            version=current.version + 1,
            parent_version=current.version,
            prompt_text=prompt_text,
            training_attempt_ids=tuple(attempt.attempt_id for attempt in attempts),
            change_summary=str(data.get("change_summary", "")).strip(),
            metrics=metrics,
        )

    def evolution_prompt(
        self,
        *,
        current: MutationPromptVersion,
        attempts: tuple[FuzzAttempt, ...],
        config: PromptEvolutionConfig,
    ) -> str:
        summaries = _attempt_summaries(attempts, config=config)
        successes = sum(attempt.success for attempt in attempts)
        allowed_prompt_chars = _evolved_prompt_char_limit(
            current=current,
            successes=successes,
            config=config,
        )
        evidence_rule = (
            "Successful attempts exist. New strategies must be directly supported by those "
            "successes; failures may justify only concise prohibitions or self-checks."
            if successes
            else "No successful attempts exist in this generation. Do not add any new strategy "
            "or rule. Only remove, merge, shorten, or clarify existing instructions, and do not "
            "increase the policy length."
        )
        outcome_rule = (
            "- Turn patterns from successful attempts into concise, general strategies.\n"
            "- Use failures only for concise prohibitions or self-checks."
            if successes
            else "- Use failed attempts only to decide what to remove, merge, shorten, or "
            "clarify. Do not turn failures into new rules."
        )
        return f"""You are improving one reusable policy for generating adversarial mutations of mathematical proofs.

Current mutation policy (version {current.version}):
```text
{current.prompt_text}
```

Recent judged outcomes produced with this exact policy:
```json
{json.dumps(summaries, indent=2, sort_keys=True)}
```

Rewrite the complete mutation policy.
Evidence rule: {evidence_rule}
{outcome_rule}
- Generalize across proofs. Do not mention particular problems, proof text, attempt ids,
  strategy ids, or model responses in the policy.
- Remove redundant, obsolete, conflicting, and overly specific instructions.
- Preserve exactly these three section headings: "Strategies:", "Do not:", and "Before returning:".
- Keep the policy at or below {allowed_prompt_chars} characters. This evidence-based limit is
  stricter than the absolute {config.max_prompt_chars}-character storage limit.
- Return a complete replacement, not a patch or commentary about the old policy.

Return exactly one JSON object with no prose outside JSON:
```json
{{
  "prompt_text": "complete replacement mutation policy",
  "change_summary": "brief explanation of evidence-based changes",
  "evidence_attempt_ids": ["attempt ids used as evidence"]
}}
```
"""


def _evolved_prompt_char_limit(
    *,
    current: MutationPromptVersion,
    successes: int,
    config: PromptEvolutionConfig,
) -> int:
    """Return the evidence-regularized maximum length for the next prompt."""

    initial_cap = max(
        len(config.initial_prompt),
        int(len(config.initial_prompt) * config.max_prompt_length_multiplier),
    )
    hard_cap = min(config.max_prompt_chars, initial_cap)
    growth_cap = (
        len(current.prompt_text) + config.max_prompt_growth_chars
        if successes > 0
        else len(current.prompt_text)
    )
    return max(1, min(hard_cap, growth_cap))


@dataclass(frozen=True)
class PromptEvolutionRunResult:
    attempts: tuple[FuzzAttempt, ...]
    storage_dir: Path
    current_prompt: MutationPromptVersion

    @property
    def successes(self) -> int:
        return sum(1 for attempt in self.attempts if attempt.success)

    def summary(self) -> str:
        return (
            f"Ran {len(self.attempts)} attempts; successes={self.successes}; "
            f"prompt_version={self.current_prompt.version}; storage={self.storage_dir}"
        )


class PromptEvolutionaryProofFuzzer:
    """Runs false-proof attempts under one versioned mutation policy."""

    def __init__(
        self,
        llm: LLMClient,
        *,
        config: PromptEvolutionConfig | None = None,
        attempt_config: EvolutionConfig | None = None,
        attempt_store: ProofFuzzAttemptStore | None = None,
        prompt_store: MutationPromptStore | None = None,
        evolver: MutationPromptEvolver | None = None,
    ):
        self.llm = llm
        self.config = config or PromptEvolutionConfig()
        self.storage_dir = Path(self.config.storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        active_attempt_config = attempt_config or EvolutionConfig(
            storage_dir=self.storage_dir,
            correctness_selection_mode="false_proof",
        )
        self.attempt_config = replace(
            active_attempt_config,
            storage_dir=self.storage_dir,
            strategy_injection_probability=0.0,
            evolution_threshold=0,
            max_strategies_injected=0,
            seed_mined_strategies=False,
            correctness_selection_mode="false_proof",
            false_proof_probability=1.0,
            max_previous_failed_attempts_in_prompt=0,
            max_previous_successful_attempts_in_prompt=0,
            reject_duplicate_successful_mutations=False,
        )
        self.attempt_store = attempt_store or ProofFuzzAttemptStore(self.storage_dir)
        self.prompt_store = prompt_store or MutationPromptStore(self.storage_dir)
        self.evolver = evolver or MutationPromptEvolver(llm)
        self.prompt_store.initialize(
            self.config.initial_prompt,
            max_chars=self.config.max_prompt_chars,
        )

    @property
    def current_prompt(self) -> MutationPromptVersion:
        current = self.prompt_store.load_current()
        if current is None:
            raise RuntimeError("Mutation prompt store was not initialized.")
        return current

    def run_false_proof_attempt(
        self,
        *,
        proof_text: str,
        objective: str = "",
        metadata: dict[str, object] | None = None,
        prompt_version: MutationPromptVersion | None = None,
    ) -> FuzzAttempt:
        version = prompt_version or self.current_prompt
        attempt_metadata = {
            **dict(metadata or {}),
            "mutation_prompt_version": version.version,
            "mutation_prompt_sha256": version.prompt_sha256,
            "prompt_evolution_pipeline": True,
        }
        fuzzer = NaturalLanguageProofFuzzerLLMInterface(
            proof_text,
            self.llm,
            mutation_policy=version.prompt_text,
        )
        runner = EvolutionaryProofFuzzer(
            fuzzer,
            store=self.attempt_store,
            config=self.attempt_config,
        )
        return runner.run_false_proof_attempt(
            objective=objective,
            metadata=attempt_metadata,
        )

    def attempts_for_prompt(
        self,
        version: MutationPromptVersion,
    ) -> tuple[FuzzAttempt, ...]:
        return tuple(
            attempt
            for attempt in self.attempt_store.load_attempts(
                fuzzer_kind=FUZZER_KIND_NATURAL_LANGUAGE,
            )
            if attempt.metadata.get("mutation_prompt_sha256") == version.prompt_sha256
        )

    def evolve_prompt(self, version: MutationPromptVersion) -> MutationPromptVersion:
        attempts = self.attempts_for_prompt(version)[-self.config.evolution_window :]
        evolved = self.evolver.evolve(
            current=version,
            attempts=attempts,
            config=self.config,
        )
        self.prompt_store.save(evolved, max_chars=self.config.max_prompt_chars)
        return evolved


def run_prompt_evolutionary_pipeline(
    *,
    examples: tuple[NaturalLanguageProofExample, ...],
    llm: LLMClient,
    config: PromptEvolutionConfig | None = None,
    attempt_config: EvolutionConfig | None = None,
    max_workers: int = 1,
    attempts_per_example: int = 1,
    num_attempts: int | None = None,
    sample_offset: int = 0,
    sample_without_replacement: bool = False,
    objective_prefix: str = "",
    dataset_name: str = "natural-language",
    proof_source: str = "source file",
) -> PromptEvolutionRunResult:
    """Run examples in frozen-prompt generations and evolve once per full batch."""

    if max_workers < 1:
        raise ValueError("max_workers must be at least 1.")
    if attempts_per_example < 1:
        raise ValueError("attempts_per_example must be at least 1.")
    if num_attempts is not None and num_attempts < 1:
        raise ValueError("num_attempts must be at least 1 when provided.")
    if sample_offset < 0:
        raise ValueError("sample_offset must be non-negative.")

    active_config = config or PromptEvolutionConfig()
    controller = PromptEvolutionaryProofFuzzer(
        llm,
        config=active_config,
        attempt_config=attempt_config,
    )
    work_items = sample_natural_language_proof_work_items(
        examples,
        attempts_per_example=attempts_per_example,
        num_attempts=num_attempts,
        sample_offset=sample_offset,
        sample_without_replacement=sample_without_replacement,
        random_seed=active_config.random_seed,
    )
    attempts: list[FuzzAttempt] = []
    cursor = 0
    stop_for_usage_limit = False
    while cursor < len(work_items) and not stop_for_usage_limit:
        version = controller.current_prompt
        existing_count = len(controller.attempts_for_prompt(version))
        remaining_in_generation = active_config.generation_size - (
            existing_count % active_config.generation_size
        )
        batch_items = work_items[cursor : cursor + remaining_in_generation]
        batch_attempts = _run_generation_batch(
            controller=controller,
            prompt_version=version,
            work_items=batch_items,
            objective_prefix=objective_prefix,
            dataset_name=dataset_name,
            proof_source=proof_source,
            max_workers=max_workers,
        )
        attempts.extend(batch_attempts)
        cursor += len(batch_items)
        stop_for_usage_limit = any(usage_limit_reached(attempt) for attempt in batch_attempts)
        prompt_attempt_count = existing_count + len(batch_attempts)
        generation_completed = (
            len(batch_attempts) == len(batch_items)
            and prompt_attempt_count % active_config.generation_size == 0
        )
        if generation_completed and not stop_for_usage_limit:
            try:
                controller.evolve_prompt(version)
            except Exception as exc:
                controller.prompt_store.record_error(
                    version=version,
                    attempt_ids=tuple(attempt.attempt_id for attempt in batch_attempts),
                    error=exc,
                )
                if usage_limit_reached(exc):
                    stop_for_usage_limit = True
                elif not active_config.continue_on_evolution_error:
                    raise

    return PromptEvolutionRunResult(
        attempts=tuple(attempts),
        storage_dir=controller.storage_dir,
        current_prompt=controller.current_prompt,
    )


def _run_generation_batch(
    *,
    controller: PromptEvolutionaryProofFuzzer,
    prompt_version: MutationPromptVersion,
    work_items: list[tuple[int, NaturalLanguageProofExample, int]],
    objective_prefix: str,
    dataset_name: str,
    proof_source: str,
    max_workers: int,
) -> tuple[FuzzAttempt, ...]:
    def run_item(item: tuple[int, PromptEvolutionExample, int]) -> FuzzAttempt:
        sample_index, example, attempt_index = item
        proof_text = truncate_text_head_tail(
            example.proof,
            controller.attempt_config.max_proof_chars,
        )
        metadata = {
            **example.to_metadata(),
            "example_attempt_index": attempt_index,
            "sample_index": sample_index,
            "proof_source": proof_source,
            "fuzzer_kind": FUZZER_KIND_NATURAL_LANGUAGE,
            "proof_chars_original": len(example.proof),
            "proof_chars_used": len(proof_text),
        }
        return controller.run_false_proof_attempt(
            proof_text=proof_text,
            objective=format_natural_language_proof_objective(
                example,
                objective_prefix=objective_prefix,
                max_problem_chars=controller.attempt_config.max_problem_chars,
                dataset_name=dataset_name,
            ),
            metadata=metadata,
            prompt_version=prompt_version,
        )

    if max_workers == 1:
        return tuple(run_item(item) for item in work_items)

    attempts_by_index: dict[int, FuzzAttempt] = {}
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(run_item, item): item[0]
            for item in work_items
        }
        for future in as_completed(futures):
            attempts_by_index[futures[future]] = future.result()
    return tuple(attempts_by_index[index] for index in sorted(attempts_by_index))


def _attempt_summaries(
    attempts: tuple[FuzzAttempt, ...],
    *,
    config: PromptEvolutionConfig,
) -> list[dict[str, object]]:
    selected: list[dict[str, object]] = []
    used_chars = 0
    for attempt in reversed(attempts[-config.evolution_window :]):
        summary = _attempt_summary(
            attempt,
            max_chars=config.max_attempt_summary_chars,
        )
        encoded = json.dumps(summary, sort_keys=True)
        if selected and used_chars + len(encoded) > config.max_evolution_context_chars:
            break
        selected.append(summary)
        used_chars += len(encoded)
    selected.reverse()
    return selected


def _attempt_summary(attempt: FuzzAttempt, *, max_chars: int) -> dict[str, object]:
    summary: dict[str, object] = {
        "attempt_id": attempt.attempt_id,
        "outcome": _attempt_outcome(attempt),
        "success": attempt.success,
        "status": attempt.status,
        "failure_stage": attempt.failure_stage,
        "error": _bounded(attempt.error, 300),
        "math_topic": attempt.metadata.get("math_topic")
        or attempt.metadata.get("llm_category"),
        "mutation_rationale": _bounded(attempt.mutation_instructions.rationale, 400),
        "mutations": [
            {
                "kind": mutation.kind,
                "target": mutation.target,
                "summary": _bounded(mutation.summary, 240),
                "propagate_downstream": mutation.propagate_downstream,
            }
            for mutation in attempt.mutation_instructions.mutations
        ],
        "mutation_check": (
            attempt.mutation_check_result.to_dict()
            if attempt.mutation_check_result is not None
            else None
        ),
        "target_error_reports": attempt.metadata.get(
            "target_error_reports",
            attempt.metadata.get("target_judge_results", []),
        ),
        "introduced_error_match": attempt.metadata.get(
            "introduced_error_match",
            attempt.metadata.get("judge_error_detection_check"),
        ),
    }
    encoded = json.dumps(summary, sort_keys=True)
    if len(encoded) <= max_chars:
        return summary
    summary["mutation_check"] = _compact_judge(summary.get("mutation_check"))
    summary["target_error_reports"] = [
        _compact_judge(value)
        for value in summary.get("target_error_reports", [])
        if isinstance(value, dict)
    ]
    summary["introduced_error_match"] = None
    encoded = json.dumps(summary, sort_keys=True)
    if len(encoded) <= max_chars:
        return summary
    summary["mutations"] = summary["mutations"][:1]  # type: ignore[index]
    summary["mutation_rationale"] = _bounded(str(summary["mutation_rationale"]), 160)
    if len(json.dumps(summary, sort_keys=True)) > max_chars:
        summary["target_error_reports"] = []
        summary["mutation_check"] = None
    return summary


def _attempt_outcome(attempt: FuzzAttempt) -> str:
    if attempt.status == "failed":
        lowered = f"{attempt.failure_stage} {attempt.error}".lower()
        if "duplicate" in lowered or "repeated a previous" in lowered:
            return "duplicate"
        return "generation_failure"
    if (
        attempt.mutation_check_result is None
        or attempt.mutation_check_result.verdict != "incorrect"
    ):
        return "invalid_mutation"
    error_check = attempt.metadata.get(
        "introduced_error_match",
        attempt.metadata.get("judge_error_detection_check"),
    )
    if isinstance(error_check, dict) and error_check.get(
        "introduced_error_found",
        error_check.get("any_judge_reported_correct_error"),
    ):
        return "error_identified"
    if attempt.success:
        return "success"
    return "caught_by_target"


def _validate_mutation_policy(prompt_text: str, *, max_chars: int) -> str:
    prompt = prompt_text.strip()
    if not prompt:
        raise ValueError("Mutation policy cannot be empty.")
    if len(prompt) > max_chars:
        raise ValueError(
            f"Mutation policy has {len(prompt)} characters; maximum is {max_chars}."
        )
    for heading in ("Strategies", "Do not", "Before returning"):
        if re.search(rf"(?im)^\s*{re.escape(heading)}\s*:\s*$", prompt) is None:
            raise ValueError(f"Mutation policy is missing the required {heading!r} section.")
    return prompt


def _compact_judge(value: object) -> dict[str, object] | None:
    if not isinstance(value, dict):
        return None
    return {
        "verdict": value.get("verdict"),
        "response_kind": value.get("response_kind"),
        "detected_errors": list(value.get("detected_errors", []))[:3]
        if isinstance(value.get("detected_errors"), list)
        else [],
        "rationale": _bounded(str(value.get("rationale", "")), 180),
        "detected_flaw": _bounded(str(value.get("detected_flaw", "")), 180),
    }


def _bounded(value: str, max_chars: int) -> str:
    if len(value) <= max_chars:
        return value
    return value[: max(0, max_chars - 3)].rstrip() + "..."


def _string_tuple(value: object) -> tuple[str, ...]:
    if isinstance(value, (list, tuple)):
        return tuple(str(item) for item in value)
    return ()


def _numeric_dict(value: object) -> dict[str, int | float]:
    if not isinstance(value, dict):
        return {}
    return {
        str(key): number
        for key, number in value.items()
        if isinstance(number, (int, float)) and not isinstance(number, bool)
    }


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()
