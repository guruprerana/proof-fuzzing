"""Evolutionary attempt library and strategy guidance for proof fuzzing."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
import json
import math
from pathlib import Path
import random
import re
import threading
import time
import uuid
from typing import Iterable

from src.proof_fuzzer.llm_interface import (
    FuzzerMutationInstructions,
    LLMClient,
    NaturalLanguageProofFuzzerLLMInterface,
    ProofFuzzerLLMInterfaceBase,
    SemiFormalProofFuzzerLLMInterface,
    parse_mutation_instructions,
    split_natural_language_proof,
)
from src.semi_formalization.mutation import ProofMutation


FUZZER_KIND_SEMIFORMAL = "semiformal"
FUZZER_KIND_NATURAL_LANGUAGE = "natural_language"
JUDGE_VERDICTS = {"correct", "incorrect", "uncertain"}
CORRECTNESS_SELECTION_MODES = {
    "adaptive",
    "model",
    "random",
    "fixed_probability",
    "false_proof",
    "correctness_preserving",
}


@dataclass(frozen=True)
class EvolutionConfig:
    """Configuration for evolutionary fuzzing storage and strategy use."""

    storage_dir: str | Path = "logs/proof_fuzzer_evolution"
    strategy_injection_probability: float = 0.5
    evolution_threshold: int = 20
    max_strategies_injected: int = 3
    max_bank_size: int = 50
    random_seed: int | None = None
    correctness_selection_mode: str = "adaptive"
    correctness_exploration_weight: float = 1.0
    false_proof_probability: float = 0.5
    max_proof_chars: int = 24_000
    max_problem_chars: int = 4_000
    llm_retries: int = 0
    retry_backoff_seconds: float = 1.0
    context_fallbacks: int = 0
    continue_on_error: bool = True

    def __post_init__(self) -> None:
        if self.correctness_selection_mode not in CORRECTNESS_SELECTION_MODES:
            allowed = ", ".join(sorted(CORRECTNESS_SELECTION_MODES))
            raise ValueError(
                "Unknown correctness selection mode "
                f"{self.correctness_selection_mode!r}; expected one of: {allowed}"
            )
        if not 0.0 <= self.false_proof_probability <= 1.0:
            raise ValueError("false_proof_probability must be between 0 and 1.")
        if self.max_proof_chars < 1:
            raise ValueError("max_proof_chars must be at least 1.")
        if self.max_problem_chars < 1:
            raise ValueError("max_problem_chars must be at least 1.")
        if self.llm_retries < 0:
            raise ValueError("llm_retries must be non-negative.")
        if self.retry_backoff_seconds < 0:
            raise ValueError("retry_backoff_seconds must be non-negative.")
        if self.context_fallbacks < 0:
            raise ValueError("context_fallbacks must be non-negative.")


@dataclass(frozen=True)
class JudgeResult:
    """Parsed result from judging a fuzzed proof attempt."""

    verdict: str
    confidence: float = 0.0
    rationale: str = ""
    detected_flaw: str = ""
    raw_response: str = ""

    def __post_init__(self) -> None:
        normalized = self.verdict.strip().lower()
        if normalized not in JUDGE_VERDICTS:
            allowed = ", ".join(sorted(JUDGE_VERDICTS))
            raise ValueError(f"Unknown judge verdict {self.verdict!r}; expected one of: {allowed}")
        object.__setattr__(self, "verdict", normalized)
        object.__setattr__(self, "confidence", float(self.confidence))

    def to_dict(self) -> dict[str, object]:
        return {
            "verdict": self.verdict,
            "confidence": self.confidence,
            "rationale": self.rationale,
            "detected_flaw": self.detected_flaw,
            "raw_response": self.raw_response,
        }

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "JudgeResult":
        return cls(
            verdict=str(data.get("verdict", "")),
            confidence=float(data.get("confidence", 0.0) or 0.0),
            rationale=str(data.get("rationale", "")),
            detected_flaw=str(data.get("detected_flaw", "")),
            raw_response=str(data.get("raw_response", "")),
        )


class LLMStageError(RuntimeError):
    """Wraps an LLM or parser failure with the pipeline stage that failed."""

    def __init__(self, stage: str, cause: Exception):
        self.stage = stage
        self.cause = cause
        super().__init__(f"{stage} failed: {cause!r}")


@dataclass(frozen=True)
class FuzzStrategy:
    """Reusable proof-fuzzing guidance distilled from attempt history."""

    strategy_id: str
    fuzzer_kind: str
    title: str
    guidance: str
    target_correctness: bool | None = None
    successes: int = 0
    failures: int = 0
    provenance_attempt_ids: tuple[str, ...] = ()
    created_at: str = field(default_factory=lambda: _utc_now())
    updated_at: str = field(default_factory=lambda: _utc_now())
    metadata: dict[str, object] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "fuzzer_kind", _normalize_fuzzer_kind(self.fuzzer_kind))
        object.__setattr__(self, "provenance_attempt_ids", tuple(self.provenance_attempt_ids))

    def to_dict(self) -> dict[str, object]:
        return {
            "strategy_id": self.strategy_id,
            "fuzzer_kind": self.fuzzer_kind,
            "title": self.title,
            "guidance": self.guidance,
            "target_correctness": self.target_correctness,
            "successes": self.successes,
            "failures": self.failures,
            "provenance_attempt_ids": list(self.provenance_attempt_ids),
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "metadata": dict(self.metadata),
        }

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "FuzzStrategy":
        return cls(
            strategy_id=str(data.get("strategy_id") or data.get("id") or _new_id("strategy")),
            fuzzer_kind=str(data.get("fuzzer_kind", FUZZER_KIND_SEMIFORMAL)),
            title=str(data.get("title", "")),
            guidance=str(data.get("guidance", "")),
            target_correctness=_parse_optional_bool(data.get("target_correctness")),
            successes=int(data.get("successes", 0) or 0),
            failures=int(data.get("failures", 0) or 0),
            provenance_attempt_ids=_string_tuple(data.get("provenance_attempt_ids", ())),
            created_at=str(data.get("created_at") or _utc_now()),
            updated_at=str(data.get("updated_at") or _utc_now()),
            metadata=dict(data.get("metadata", {}) if isinstance(data.get("metadata"), dict) else {}),
        )


@dataclass(frozen=True)
class FuzzAttempt:
    """One judged proof-fuzzing attempt."""

    attempt_id: str
    fuzzer_kind: str
    objective: str
    maintain_correctness: bool
    original_proof_text: str
    mutation_instructions: FuzzerMutationInstructions
    judge_result: JudgeResult | None
    success: bool
    mutated_proof_text: str = ""
    strategy_ids: tuple[str, ...] = ()
    status: str = "success"
    failure_stage: str = ""
    error: str = ""
    pre_mutation_judge_result: JudgeResult | None = None
    mutation_check_result: JudgeResult | None = None
    created_at: str = field(default_factory=lambda: _utc_now())
    metadata: dict[str, object] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "fuzzer_kind", _normalize_fuzzer_kind(self.fuzzer_kind))
        object.__setattr__(self, "strategy_ids", tuple(self.strategy_ids))
        if self.status not in {"success", "failed"}:
            raise ValueError("FuzzAttempt status must be 'success' or 'failed'.")

    def to_dict(self) -> dict[str, object]:
        return {
            "attempt_id": self.attempt_id,
            "fuzzer_kind": self.fuzzer_kind,
            "objective": self.objective,
            "maintain_correctness": self.maintain_correctness,
            "original_proof_text": self.original_proof_text,
            "mutated_proof_text": self.mutated_proof_text,
            "mutation_instructions": self.mutation_instructions.to_dict(),
            "judge_result": self.judge_result.to_dict() if self.judge_result is not None else None,
            "success": self.success,
            "strategy_ids": list(self.strategy_ids),
            "status": self.status,
            "failure_stage": self.failure_stage,
            "error": self.error,
            "pre_mutation_judge_result": (
                self.pre_mutation_judge_result.to_dict()
                if self.pre_mutation_judge_result is not None
                else None
            ),
            "mutation_check_result": (
                self.mutation_check_result.to_dict()
                if self.mutation_check_result is not None
                else None
            ),
            "created_at": self.created_at,
            "metadata": dict(self.metadata),
        }

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "FuzzAttempt":
        return cls(
            attempt_id=str(data.get("attempt_id", "")),
            fuzzer_kind=str(data.get("fuzzer_kind", FUZZER_KIND_SEMIFORMAL)),
            objective=str(data.get("objective", "")),
            maintain_correctness=bool(data.get("maintain_correctness", False)),
            original_proof_text=str(data.get("original_proof_text", "")),
            mutated_proof_text=str(data.get("mutated_proof_text", "")),
            mutation_instructions=_instructions_from_dict(data.get("mutation_instructions", {})),
            judge_result=(
                JudgeResult.from_dict(_dict_value(data.get("judge_result")))
                if isinstance(data.get("judge_result"), dict)
                else None
            ),
            success=bool(data.get("success", False)),
            strategy_ids=_string_tuple(data.get("strategy_ids", ())),
            status=str(data.get("status") or "success"),
            failure_stage=str(data.get("failure_stage", "")),
            error=str(data.get("error", "")),
            pre_mutation_judge_result=(
                JudgeResult.from_dict(_dict_value(data.get("pre_mutation_judge_result")))
                if isinstance(data.get("pre_mutation_judge_result"), dict)
                else None
            ),
            mutation_check_result=(
                JudgeResult.from_dict(_dict_value(data.get("mutation_check_result")))
                if isinstance(data.get("mutation_check_result"), dict)
                else None
            ),
            created_at=str(data.get("created_at") or _utc_now()),
            metadata=dict(data.get("metadata", {}) if isinstance(data.get("metadata"), dict) else {}),
        )


class ProofFuzzAttemptStore:
    """JSONL-backed storage for fuzz attempts and evolved strategies."""

    def __init__(self, root_dir: str | Path):
        self.root_dir = Path(root_dir)
        self.root_dir.mkdir(parents=True, exist_ok=True)
        self.attempts_path = self.root_dir / "attempts.jsonl"
        self.state_path = self.root_dir / "evolution_state.json"
        self.lock = threading.RLock()

    def append_attempt(self, attempt: FuzzAttempt) -> None:
        with self.lock:
            with self.attempts_path.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(attempt.to_dict(), sort_keys=True) + "\n")

    def load_attempts(
        self,
        *,
        fuzzer_kind: str | None = None,
        limit: int | None = None,
    ) -> tuple[FuzzAttempt, ...]:
        with self.lock:
            if not self.attempts_path.exists():
                return ()
            normalized_kind = _normalize_fuzzer_kind(fuzzer_kind) if fuzzer_kind else None
            attempts: list[FuzzAttempt] = []
            for line in self.attempts_path.read_text(encoding="utf-8").splitlines():
                if not line.strip():
                    continue
                attempt = FuzzAttempt.from_dict(json.loads(line))
                if normalized_kind is not None and attempt.fuzzer_kind != normalized_kind:
                    continue
                attempts.append(attempt)
            if limit is not None:
                attempts = attempts[-limit:]
            return tuple(attempts)

    def count_attempts(self, fuzzer_kind: str) -> int:
        return len(self.load_attempts(fuzzer_kind=fuzzer_kind))

    def load_strategies(self, fuzzer_kind: str) -> tuple[FuzzStrategy, ...]:
        with self.lock:
            path = self._strategy_path(fuzzer_kind)
            if not path.exists():
                return ()
            strategies: list[FuzzStrategy] = []
            for line in path.read_text(encoding="utf-8").splitlines():
                if line.strip():
                    strategies.append(FuzzStrategy.from_dict(json.loads(line)))
            return tuple(strategies)

    def save_strategies(self, fuzzer_kind: str, strategies: Iterable[FuzzStrategy]) -> None:
        with self.lock:
            path = self._strategy_path(fuzzer_kind)
            tmp_path = path.with_suffix(path.suffix + ".tmp")
            with tmp_path.open("w", encoding="utf-8") as handle:
                for strategy in strategies:
                    handle.write(json.dumps(strategy.to_dict(), sort_keys=True) + "\n")
            tmp_path.replace(path)

    def last_evolved_attempt_count(self, fuzzer_kind: str) -> int:
        with self.lock:
            state = self._load_state()
            return int(state.get(_normalize_fuzzer_kind(fuzzer_kind), 0) or 0)

    def set_last_evolved_attempt_count(self, fuzzer_kind: str, count: int) -> None:
        with self.lock:
            state = self._load_state()
            state[_normalize_fuzzer_kind(fuzzer_kind)] = int(count)
            self.state_path.write_text(json.dumps(state, indent=2, sort_keys=True), encoding="utf-8")

    def _strategy_path(self, fuzzer_kind: str) -> Path:
        return self.root_dir / f"strategies_{_normalize_fuzzer_kind(fuzzer_kind)}.jsonl"

    def _load_state(self) -> dict[str, object]:
        if not self.state_path.exists():
            return {}
        return json.loads(self.state_path.read_text(encoding="utf-8"))


class ProofFuzzJudge:
    """White-box checker for whether mutation instructions have the intended effect."""

    def __init__(self, llm: LLMClient):
        self.llm = llm

    def judge(
        self,
        *,
        original_proof_text: str,
        mutation_instructions: FuzzerMutationInstructions,
        mutated_proof_text: str = "",
        fuzzer_kind: str = FUZZER_KIND_SEMIFORMAL,
        objective: str = "",
    ) -> JudgeResult:
        response = self.llm.complete(
            self.judge_prompt(
                original_proof_text=original_proof_text,
                mutation_instructions=mutation_instructions,
                mutated_proof_text=mutated_proof_text,
                fuzzer_kind=fuzzer_kind,
                objective=objective,
            )
        )
        return parse_judge_result(response)

    def judge_prompt(
        self,
        *,
        original_proof_text: str,
        mutation_instructions: FuzzerMutationInstructions,
        mutated_proof_text: str = "",
        fuzzer_kind: str = FUZZER_KIND_SEMIFORMAL,
        objective: str = "",
    ) -> str:
        proof_block = (
            f"Mutated proof:\n```text\n{mutated_proof_text}\n```"
            if mutated_proof_text.strip()
            else "No full mutated proof text is available. Judge the intended mutated proof from the mutation instructions."
        )
        return f"""You are judging a fuzzed mathematical proof.

Fuzzer kind: {_normalize_fuzzer_kind(fuzzer_kind)}
Objective: {objective.strip() or "not specified"}

Original proof:
```text
{original_proof_text}
```

Mutation instructions:
```json
{json.dumps(mutation_instructions.to_dict(), indent=2, sort_keys=True)}
```

{proof_block}

Decide whether the mutated proof would be accepted as mathematically correct by a careful proof judge.
Return exactly one JSON object with no prose outside JSON.
Schema:
```json
{{
  "verdict": "correct | incorrect | uncertain",
  "confidence": 0.0,
  "rationale": "brief justification",
  "detected_flaw": "empty if no flaw was detected"
}}
```
"""


class BlindProofCorrectnessJudge:
    """Uses an LLM as the target judge that only sees the problem and submitted proof."""

    def __init__(self, llm: LLMClient):
        self.llm = llm

    def judge(
        self,
        *,
        problem_text: str = "",
        proof_text: str,
        fuzzer_kind: str = FUZZER_KIND_SEMIFORMAL,
    ) -> JudgeResult:
        response = self.llm.complete(
            self.judge_prompt(
                problem_text=problem_text,
                proof_text=proof_text,
                fuzzer_kind=fuzzer_kind,
            )
        )
        return parse_judge_result(response)

    def judge_prompt(
        self,
        *,
        problem_text: str = "",
        proof_text: str,
        fuzzer_kind: str = FUZZER_KIND_SEMIFORMAL,
    ) -> str:
        problem_block = problem_text.strip() or "not specified"
        return f"""You are grading a submitted mathematical proof.

Problem:
```text
{problem_block}
```

Submitted proof:
```text
{proof_text}
```

Decide whether the submitted proof is mathematically correct for the problem.
Return exactly one JSON object with no prose outside JSON.
Schema:
```json
{{
  "verdict": "correct | incorrect | uncertain",
  "confidence": 0.0,
  "rationale": "brief justification",
  "detected_flaw": "empty if no flaw was detected"
}}
```
"""


class StrategyEvolver:
    """Distills successful and unsuccessful attempts into strategy guidance."""

    def __init__(self, llm: LLMClient):
        self.llm = llm

    def evolve(
        self,
        *,
        fuzzer_kind: str,
        attempts: Iterable[FuzzAttempt],
        existing_strategies: Iterable[FuzzStrategy] = (),
        max_bank_size: int = 50,
    ) -> tuple[FuzzStrategy, ...]:
        normalized_kind = _normalize_fuzzer_kind(fuzzer_kind)
        response = self.llm.complete(
            self.evolution_prompt(
                fuzzer_kind=normalized_kind,
                attempts=attempts,
                existing_strategies=existing_strategies,
                max_bank_size=max_bank_size,
            )
        )
        return parse_strategy_evolution_response(
            response,
            fuzzer_kind=normalized_kind,
            max_bank_size=max_bank_size,
        )

    def evolution_prompt(
        self,
        *,
        fuzzer_kind: str,
        attempts: Iterable[FuzzAttempt],
        existing_strategies: Iterable[FuzzStrategy] = (),
        max_bank_size: int = 50,
    ) -> str:
        attempt_dicts = [_summarize_attempt(attempt) for attempt in attempts]
        strategy_dicts = [strategy.to_dict() for strategy in existing_strategies]
        return f"""You are evolving a reusable bank of proof-fuzzing strategies.

Fuzzer kind: {_normalize_fuzzer_kind(fuzzer_kind)}
Maximum strategies to return: {max_bank_size}

Existing strategies:
```json
{json.dumps(strategy_dicts, indent=2, sort_keys=True)}
```

Recent judged attempts:
```json
{json.dumps(attempt_dicts, indent=2, sort_keys=True)}
```

Distill what worked and what failed into compact, actionable strategies for future mutation prompts.
Return the complete replacement strategy bank, not a patch.
Return exactly one JSON object with no prose outside JSON.
Schema:
```json
{{
  "strategies": [
    {{
      "strategy_id": "reuse an existing id when revising, otherwise leave empty",
      "title": "short name",
      "guidance": "actionable instruction to include in a future fuzzer prompt",
      "target_correctness": true,
      "successes": 0,
      "failures": 0,
      "provenance_attempt_ids": ["attempt ids that support this strategy"]
    }}
  ]
}}
```
Use null for target_correctness when a strategy applies to both correctness targets.
"""


class EvolutionaryProofFuzzer:
    """Runs fuzzing attempts with judged outcomes and evolved strategy guidance."""

    def __init__(
        self,
        fuzzer: ProofFuzzerLLMInterfaceBase,
        *,
        store: ProofFuzzAttemptStore | None = None,
        judge: BlindProofCorrectnessJudge | None = None,
        mutation_checker: ProofFuzzJudge | None = None,
        evolver: StrategyEvolver | None = None,
        config: EvolutionConfig | None = None,
    ):
        self.fuzzer = fuzzer
        self.config = config or EvolutionConfig()
        self.store = store or ProofFuzzAttemptStore(self.config.storage_dir)
        if judge is None:
            if fuzzer.llm is None:
                raise ValueError("A judge or fuzzer LLM client is required for evolutionary fuzzing.")
            judge = BlindProofCorrectnessJudge(fuzzer.llm)
        if mutation_checker is None:
            if fuzzer.llm is None:
                raise ValueError("A mutation checker or fuzzer LLM client is required for evolutionary fuzzing.")
            mutation_checker = ProofFuzzJudge(fuzzer.llm)
        if evolver is None:
            if fuzzer.llm is None:
                raise ValueError("An evolver or fuzzer LLM client is required for evolutionary fuzzing.")
            evolver = StrategyEvolver(fuzzer.llm)
        self.judge = judge
        self.mutation_checker = mutation_checker
        self.evolver = evolver
        self.rng = random.Random(self.config.random_seed)
        self.fuzzer_kind = infer_fuzzer_kind(fuzzer)

    def run_mutation_attempt(
        self,
        *,
        objective: str = "",
        metadata: dict[str, object] | None = None,
    ) -> FuzzAttempt:
        return self._run_attempt(objective=objective, maintain_correctness=None, metadata=metadata)

    def run_correctness_preserving_attempt(
        self,
        *,
        objective: str = "",
        metadata: dict[str, object] | None = None,
    ) -> FuzzAttempt:
        return self._run_attempt(objective=objective, maintain_correctness=True, metadata=metadata)

    def run_false_proof_attempt(
        self,
        *,
        objective: str = "",
        metadata: dict[str, object] | None = None,
    ) -> FuzzAttempt:
        return self._run_attempt(objective=objective, maintain_correctness=False, metadata=metadata)

    def _run_attempt(
        self,
        *,
        objective: str,
        maintain_correctness: bool | None,
        metadata: dict[str, object] | None = None,
    ) -> FuzzAttempt:
        selected_correctness, selection_metadata = self._resolve_correctness_target(maintain_correctness)
        strategies = self._sample_strategies(maintain_correctness=selected_correctness)
        strategy_guidance = tuple(f"{strategy.title}: {strategy.guidance}" for strategy in strategies)
        original_text = proof_text_for_fuzzer(self.fuzzer)
        base_metadata = {
            **dict(metadata or {}),
            "correctness_selection": selection_metadata,
        }
        problem_text = _problem_text_from_attempt(objective=objective, metadata=base_metadata)
        try:
            pre_mutation_judge_result = self._with_retries(
                lambda: self.judge.judge(
                    problem_text=problem_text,
                    proof_text=original_text,
                    fuzzer_kind=self.fuzzer_kind,
                ),
                stage="pre_mutation_judge",
                check_truncation=True,
            )
            instructions: FuzzerMutationInstructions | None = None
            for fallback_index in range(self.config.context_fallbacks + 1):
                prompt = self._mutation_prompt(
                    objective=objective,
                    maintain_correctness=selected_correctness,
                    strategy_guidance=strategy_guidance,
                )
                try:
                    response = self._with_retries(
                        lambda: self.fuzzer._complete_with_logging(
                            prompt,
                            call_kind="evolutionary_mutation_instructions",
                            metadata={
                                "strategy_ids": [strategy.strategy_id for strategy in strategies],
                                "context_fallback_index": fallback_index,
                            },
                        ),
                        stage="mutation_llm",
                        check_truncation=True,
                    )
                    instructions = self._with_retries(
                        lambda: parse_mutation_instructions(response),
                        stage="mutation_parse",
                    )
                    break
                except Exception as exc:
                    if fallback_index >= self.config.context_fallbacks or not _likely_context_or_truncation_failure(exc):
                        raise
                    if not _shrink_natural_language_fuzzer(self.fuzzer):
                        raise
            if instructions is None:
                raise RuntimeError("No mutation instructions were produced.")
            if selected_correctness is not None and instructions.maintain_correctness != selected_correctness:
                expected = "true" if selected_correctness else "false"
                actual = "true" if instructions.maintain_correctness else "false"
                raise ValueError(f"Mutation response contradicted the requested target: expected {expected}, got {actual}.")
            self.fuzzer._raise_for_invalid_mutation_instructions(instructions)

            mutated_text = materialize_mutated_proof(self.fuzzer, instructions)
            judge_result = self._with_retries(
                lambda: self.judge.judge(
                    problem_text=problem_text,
                    proof_text=mutated_text,
                    fuzzer_kind=self.fuzzer_kind,
                ),
                stage="target_judge",
                check_truncation=True,
            )
            mutation_check_result = self._run_mutation_check(
                original_proof_text=original_text,
                mutation_instructions=instructions,
                mutated_proof_text=mutated_text,
                fuzzer_kind=self.fuzzer_kind,
                objective=objective,
                metadata=base_metadata,
            )
        except Exception as exc:
            attempt = self._failed_attempt(
                objective=objective,
                maintain_correctness=selected_correctness,
                original_proof_text=original_text,
                strategy_ids=tuple(strategy.strategy_id for strategy in strategies),
                metadata=base_metadata,
                failure_stage=_failure_stage(exc),
                error=repr(exc),
            )
            self.store.append_attempt(attempt)
            if self.config.continue_on_error:
                return attempt
            raise

        success = fuzz_attempt_succeeded(
            instructions.maintain_correctness,
            judge_result,
            pre_mutation_judge_result=pre_mutation_judge_result,
        )
        attempt = FuzzAttempt(
            attempt_id=_new_id("attempt"),
            fuzzer_kind=self.fuzzer_kind,
            objective=objective,
            maintain_correctness=instructions.maintain_correctness,
            original_proof_text=original_text,
            mutated_proof_text=mutated_text,
            mutation_instructions=instructions,
            judge_result=judge_result,
            success=success,
            strategy_ids=tuple(strategy.strategy_id for strategy in strategies),
            status="success",
            pre_mutation_judge_result=pre_mutation_judge_result,
            mutation_check_result=mutation_check_result,
            metadata=base_metadata,
        )
        self.store.append_attempt(attempt)
        self._maybe_evolve()
        return attempt

    def _run_mutation_check(
        self,
        *,
        original_proof_text: str,
        mutation_instructions: FuzzerMutationInstructions,
        mutated_proof_text: str,
        fuzzer_kind: str,
        objective: str,
        metadata: dict[str, object],
    ) -> JudgeResult | None:
        try:
            return self._with_retries(
                lambda: self.mutation_checker.judge(
                    original_proof_text=original_proof_text,
                    mutation_instructions=mutation_instructions,
                    mutated_proof_text=mutated_proof_text,
                    fuzzer_kind=fuzzer_kind,
                    objective=objective,
                ),
                stage="mutation_check",
                check_truncation=True,
            )
        except Exception as exc:
            metadata["mutation_check_error"] = repr(exc)
            return None

    def _failed_attempt(
        self,
        *,
        objective: str,
        maintain_correctness: bool | None,
        original_proof_text: str,
        strategy_ids: tuple[str, ...],
        metadata: dict[str, object],
        failure_stage: str,
        error: str,
    ) -> FuzzAttempt:
        return FuzzAttempt(
            attempt_id=_new_id("attempt"),
            fuzzer_kind=self.fuzzer_kind,
            objective=objective,
            maintain_correctness=bool(maintain_correctness),
            original_proof_text=original_proof_text,
            mutation_instructions=_empty_mutation_instructions(maintain_correctness=bool(maintain_correctness)),
            judge_result=None,
            success=False,
            strategy_ids=strategy_ids,
            status="failed",
            failure_stage=failure_stage,
            error=error,
            metadata=metadata,
        )

    def _with_retries(self, call, *, stage: str, check_truncation: bool = False):
        attempts = self.config.llm_retries + 1
        last_exc: Exception | None = None
        for index in range(attempts):
            try:
                value = call()
                if check_truncation and _last_completion_was_truncated(self.fuzzer.llm):
                    raise RuntimeError("LLM completion was truncated before the response finished.")
                return value
            except Exception as exc:
                last_exc = exc
                if index >= attempts - 1:
                    break
                if self.config.retry_backoff_seconds:
                    time.sleep(self.config.retry_backoff_seconds * (index + 1))
        assert last_exc is not None
        raise LLMStageError(stage, last_exc) from last_exc

    def _resolve_correctness_target(
        self,
        requested: bool | None,
    ) -> tuple[bool | None, dict[str, object]]:
        if requested is not None:
            return requested, {"mode": "explicit", "selected": requested}

        mode = self.config.correctness_selection_mode
        if mode == "model":
            return None, {"mode": mode, "selected": None}
        if mode == "false_proof":
            return False, {"mode": mode, "selected": False}
        if mode == "correctness_preserving":
            return True, {"mode": mode, "selected": True}
        if mode == "fixed_probability":
            sample = self.rng.random()
            selected = False if sample < self.config.false_proof_probability else True
            return selected, {
                "mode": mode,
                "selected": selected,
                "false_proof_probability": self.config.false_proof_probability,
                "sample": sample,
            }
        if mode == "random":
            selected = bool(self.rng.getrandbits(1))
            return selected, {"mode": mode, "selected": selected}

        selected, scores = self._select_adaptive_correctness_target()
        return selected, {"mode": mode, "selected": selected, "scores": scores}

    def _select_adaptive_correctness_target(self) -> tuple[bool, dict[str, object]]:
        attempts = self.store.load_attempts(fuzzer_kind=self.fuzzer_kind)
        false_score = self._correctness_target_score(attempts, maintain_correctness=False)
        true_score = self._correctness_target_score(attempts, maintain_correctness=True)
        selected = True if true_score["score"] > false_score["score"] else False
        return selected, {
            "false_proof": false_score,
            "correctness_preserving": true_score,
        }

    def _correctness_target_score(
        self,
        attempts: tuple[FuzzAttempt, ...],
        *,
        maintain_correctness: bool,
    ) -> dict[str, object]:
        matching = [attempt for attempt in attempts if attempt.maintain_correctness == maintain_correctness]
        successes = sum(1 for attempt in matching if attempt.success)
        count = len(matching)
        total = len(attempts)
        smoothed_success_rate = (successes + 1.0) / (count + 2.0)
        exploration = math.sqrt(
            self.config.correctness_exploration_weight * math.log(total + 2.0) / (count + 1.0)
        )
        return {
            "attempts": count,
            "successes": successes,
            "smoothed_success_rate": smoothed_success_rate,
            "exploration_bonus": exploration,
            "score": smoothed_success_rate + exploration,
        }

    def _mutation_prompt(
        self,
        *,
        objective: str,
        maintain_correctness: bool | None,
        strategy_guidance: tuple[str, ...],
    ) -> str:
        if maintain_correctness is True:
            return self.fuzzer.correctness_preserving_mutation_instruction_prompt(
                objective=objective,
                strategy_guidance=strategy_guidance,
            )
        if maintain_correctness is False:
            return self.fuzzer.false_proof_mutation_instruction_prompt(
                objective=objective,
                strategy_guidance=strategy_guidance,
            )
        return self.fuzzer.mutation_instruction_prompt(
            objective=objective,
            strategy_guidance=strategy_guidance,
        )

    def _sample_strategies(self, *, maintain_correctness: bool | None) -> tuple[FuzzStrategy, ...]:
        if self.config.strategy_injection_probability <= 0:
            return ()
        if self.rng.random() > self.config.strategy_injection_probability:
            return ()

        strategies = [
            strategy
            for strategy in self.store.load_strategies(self.fuzzer_kind)
            if strategy.target_correctness is None or maintain_correctness is None or strategy.target_correctness == maintain_correctness
        ]
        self.rng.shuffle(strategies)
        return tuple(strategies[: self.config.max_strategies_injected])

    def _maybe_evolve(self) -> None:
        threshold = self.config.evolution_threshold
        if threshold <= 0:
            return
        with self.store.lock:
            attempt_count = self.store.count_attempts(self.fuzzer_kind)
            last_evolved = self.store.last_evolved_attempt_count(self.fuzzer_kind)
            if attempt_count - last_evolved < threshold:
                return

            attempts = tuple(
                attempt
                for attempt in self.store.load_attempts(fuzzer_kind=self.fuzzer_kind, limit=max(threshold * 3, threshold))
                if attempt.status == "success"
            )
            if not attempts:
                return
            existing = self.store.load_strategies(self.fuzzer_kind)
            try:
                strategies = self._with_retries(
                    lambda: self.evolver.evolve(
                        fuzzer_kind=self.fuzzer_kind,
                        attempts=attempts,
                        existing_strategies=existing,
                        max_bank_size=self.config.max_bank_size,
                    ),
                    stage="strategy_evolution",
                    check_truncation=True,
                )
            except Exception:
                return
            self.store.save_strategies(self.fuzzer_kind, strategies)
            self.store.set_last_evolved_attempt_count(self.fuzzer_kind, attempt_count)


def parse_judge_result(text: str) -> JudgeResult:
    data = _load_json_object(text)
    return JudgeResult(
        verdict=str(data.get("verdict", "")),
        confidence=float(data.get("confidence", 0.0) or 0.0),
        rationale=str(data.get("rationale", "")),
        detected_flaw=str(data.get("detected_flaw", "")),
        raw_response=text,
    )


def parse_strategy_evolution_response(
    text: str,
    *,
    fuzzer_kind: str,
    max_bank_size: int = 50,
) -> tuple[FuzzStrategy, ...]:
    data = _load_json_object(text)
    raw_strategies = data.get("strategies")
    if not isinstance(raw_strategies, list):
        raise ValueError("Strategy evolution response must contain a list field named 'strategies'.")

    strategies: list[FuzzStrategy] = []
    for raw_strategy in raw_strategies[:max_bank_size]:
        if not isinstance(raw_strategy, dict):
            raise ValueError("Each evolved strategy must be an object.")
        now = _utc_now()
        strategy_id = str(raw_strategy.get("strategy_id") or raw_strategy.get("id") or _new_id("strategy"))
        strategies.append(
            FuzzStrategy(
                strategy_id=strategy_id,
                fuzzer_kind=fuzzer_kind,
                title=str(raw_strategy.get("title", "")).strip(),
                guidance=str(raw_strategy.get("guidance", "")).strip(),
                target_correctness=_parse_optional_bool(raw_strategy.get("target_correctness")),
                successes=int(raw_strategy.get("successes", 0) or 0),
                failures=int(raw_strategy.get("failures", 0) or 0),
                provenance_attempt_ids=_string_tuple(raw_strategy.get("provenance_attempt_ids", ())),
                created_at=str(raw_strategy.get("created_at") or now),
                updated_at=now,
                metadata=dict(raw_strategy.get("metadata", {}) if isinstance(raw_strategy.get("metadata"), dict) else {}),
            )
        )
    return tuple(strategy for strategy in strategies if strategy.title and strategy.guidance)


def fuzz_attempt_succeeded(
    maintain_correctness: bool,
    judge_result: JudgeResult,
    *,
    pre_mutation_judge_result: JudgeResult | None = None,
) -> bool:
    if pre_mutation_judge_result is not None and pre_mutation_judge_result.verdict != "correct":
        return False
    if maintain_correctness:
        return judge_result.verdict in {"incorrect", "uncertain"}
    return judge_result.verdict == "correct"


def infer_fuzzer_kind(fuzzer: ProofFuzzerLLMInterfaceBase) -> str:
    if isinstance(fuzzer, NaturalLanguageProofFuzzerLLMInterface):
        return FUZZER_KIND_NATURAL_LANGUAGE
    if isinstance(fuzzer, SemiFormalProofFuzzerLLMInterface):
        return FUZZER_KIND_SEMIFORMAL
    return _normalize_fuzzer_kind(getattr(fuzzer, "fuzzer_kind", FUZZER_KIND_SEMIFORMAL))


def proof_text_for_fuzzer(fuzzer: ProofFuzzerLLMInterfaceBase) -> str:
    if isinstance(fuzzer, NaturalLanguageProofFuzzerLLMInterface):
        return fuzzer.proof_text
    if isinstance(fuzzer, SemiFormalProofFuzzerLLMInterface):
        return fuzzer.graph.proof.raw_text or str(fuzzer.graph.proof.to_dict(include_raw=False))
    return str(getattr(fuzzer, "proof_text", ""))


def materialize_mutated_proof(
    fuzzer: ProofFuzzerLLMInterfaceBase,
    instructions: FuzzerMutationInstructions,
) -> str:
    apply_mutations = getattr(fuzzer, "apply_mutations", None)
    if callable(apply_mutations):
        return str(apply_mutations(instructions))
    return ""


def _summarize_attempt(attempt: FuzzAttempt) -> dict[str, object]:
    if attempt.status == "failed":
        return {
            "attempt_id": attempt.attempt_id,
            "objective": attempt.objective,
            "maintain_correctness": attempt.maintain_correctness,
            "success": False,
            "status": attempt.status,
            "failure_stage": attempt.failure_stage,
            "error": attempt.error,
            "strategy_ids": list(attempt.strategy_ids),
        }
    judge = attempt.judge_result.to_dict() if attempt.judge_result is not None else {}
    return {
        "attempt_id": attempt.attempt_id,
        "objective": attempt.objective,
        "maintain_correctness": attempt.maintain_correctness,
        "success": attempt.success,
        "status": attempt.status,
        "pre_mutation_judge": (
            attempt.pre_mutation_judge_result.to_dict()
            if attempt.pre_mutation_judge_result is not None
            else None
        ),
        "judge": judge,
        "mutation_check": (
            attempt.mutation_check_result.to_dict()
            if attempt.mutation_check_result is not None
            else None
        ),
        "rationale": attempt.mutation_instructions.rationale,
        "mutations": [
            {
                "kind": mutation.kind,
                "target": mutation.target,
                "summary": mutation.summary,
                "propagate_downstream": mutation.propagate_downstream,
            }
            for mutation in attempt.mutation_instructions.mutations
        ],
        "strategy_ids": list(attempt.strategy_ids),
    }


def _instructions_from_dict(value: object) -> FuzzerMutationInstructions:
    data = _dict_value(value)
    mutations = []
    for item in data.get("mutations", ()):
        if not isinstance(item, dict):
            continue
        mutations.append(
            ProofMutation(
                kind=str(item.get("kind", "")),
                target=str(item.get("target", "")),
                summary=str(item.get("summary", "")),
                new_text=str(item.get("new_text", "")),
                affected_blocks=_string_tuple(item.get("affected_blocks", ())),
                propagate_downstream=bool(item.get("propagate_downstream", True)),
                metadata=dict(item.get("metadata", {}) if isinstance(item.get("metadata"), dict) else {}),
            )
        )
    return FuzzerMutationInstructions(
        maintain_correctness=bool(data.get("maintain_correctness", False)),
        mutations=tuple(mutations),
        rationale=str(data.get("rationale", "")),
        raw_response=str(data.get("raw_response", "")),
    )


def _problem_text_from_attempt(*, objective: str, metadata: dict[str, object]) -> str:
    problem = metadata.get("problem")
    if isinstance(problem, str) and problem.strip():
        return problem.strip()
    marker = "Problem:\n"
    if marker in objective:
        return objective.split(marker, 1)[1].strip()
    return ""


def _empty_mutation_instructions(*, maintain_correctness: bool) -> FuzzerMutationInstructions:
    return FuzzerMutationInstructions(
        maintain_correctness=maintain_correctness,
        mutations=(),
        rationale="No mutation instructions were produced because the attempt failed.",
        raw_response="",
    )


def _failure_stage(exc: Exception) -> str:
    if isinstance(exc, LLMStageError):
        return exc.stage
    return "attempt"


def _likely_context_or_truncation_failure(exc: Exception) -> bool:
    if isinstance(exc, LLMStageError):
        return _likely_context_or_truncation_failure(exc.cause)
    text = repr(exc).lower()
    return any(
        marker in text
        for marker in (
            "context",
            "maximum context",
            "context length",
            "too many tokens",
            "maximum tokens",
            "token limit",
            "finish_reason",
            "truncated",
            "no json object",
            "unterminated string",
            "expecting value",
            "expecting ',' delimiter",
        )
    )


def _shrink_natural_language_fuzzer(fuzzer: ProofFuzzerLLMInterfaceBase) -> bool:
    if not isinstance(fuzzer, NaturalLanguageProofFuzzerLLMInterface):
        return False
    current = fuzzer.proof_text
    target = max(1_000, len(current) // 2)
    if len(current) <= target:
        return False
    fuzzer.proof_text = truncate_text_head_tail(current, target)
    fuzzer.segments = split_natural_language_proof(fuzzer.proof_text)
    return True


def _last_completion_was_truncated(llm: object | None) -> bool:
    if llm is None:
        return False
    result = getattr(llm, "last_result", None)
    finish_reason = _object_field(result, "finish_reason")
    if not finish_reason:
        raw_response = getattr(result, "raw_response", None)
        choices = getattr(raw_response, "choices", None)
        if choices:
            finish_reason = str(getattr(choices[0], "finish_reason", "") or "")
    return finish_reason.strip().lower() == "length"


def truncate_text_head_tail(text: str, max_chars: int) -> str:
    if max_chars < 1:
        raise ValueError("max_chars must be at least 1.")
    if len(text) <= max_chars:
        return text
    marker = "\n\n[... truncated for context budget ...]\n\n"
    if max_chars <= len(marker) + 2:
        return text[:max_chars]
    remaining = max_chars - len(marker)
    head = remaining // 2
    tail = remaining - head
    return text[:head].rstrip() + marker + text[-tail:].lstrip()


def _object_field(value: object, field_name: str) -> str:
    if value is None:
        return ""
    field_value = getattr(value, field_name, None)
    if field_value is not None:
        return str(field_value)
    if hasattr(value, "model_dump"):
        data = value.model_dump()
        field_value = data.get(field_name)
        if field_value is not None:
            return str(field_value)
    if isinstance(value, dict):
        field_value = value.get(field_name)
        if field_value is not None:
            return str(field_value)
    return ""


def _normalize_fuzzer_kind(fuzzer_kind: str | None) -> str:
    value = (fuzzer_kind or "").strip().lower().replace("-", "_").replace(" ", "_")
    if value in {"natural", "nl", "natural_language"}:
        return FUZZER_KIND_NATURAL_LANGUAGE
    if value in {"semi_formal", "semi", "semiformal"}:
        return FUZZER_KIND_SEMIFORMAL
    if not value:
        return FUZZER_KIND_SEMIFORMAL
    return value


def _load_json_object(text: str) -> dict[str, object]:
    candidate = _extract_json_candidate(text)
    data = json.loads(candidate)
    if not isinstance(data, dict):
        raise ValueError("Expected a JSON object.")
    return data


def _extract_json_candidate(text: str) -> str:
    fenced = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, flags=re.DOTALL)
    if fenced:
        return fenced.group(1)
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1 or end < start:
        raise ValueError("No JSON object was found in the LLM response.")
    return text[start : end + 1]


def _dict_value(value: object) -> dict[str, object]:
    return value if isinstance(value, dict) else {}


def _parse_optional_bool(value: object) -> bool | None:
    if value is None:
        return None
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        lowered = value.strip().lower()
        if lowered in {"", "none", "null"}:
            return None
        if lowered == "true":
            return True
        if lowered == "false":
            return False
    raise ValueError("Expected a boolean or null value.")


def _string_tuple(value: object) -> tuple[str, ...]:
    if value is None:
        return ()
    if isinstance(value, str):
        stripped = value.strip()
        return (stripped,) if stripped else ()
    if isinstance(value, (list, tuple)):
        return tuple(str(item).strip() for item in value if str(item).strip())
    return ()


def _new_id(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex}"


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()
