"""Evolutionary attempt library and strategy guidance for proof fuzzing."""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
import random
import re
import threading
import time
import uuid
from typing import Iterable

from src.archive.proof_fuzzer.llm_interface import (
    FuzzerMutationInstructions,
    LLMClient,
    LLMTraceLogger,
    NaturalLanguageProofFuzzerLLMInterface,
    ProofFuzzerLLMInterfaceBase,
    SemiFormalProofFuzzerLLMInterface,
    _load_json_object as _load_llm_json_object,
    parse_mutation_instructions,
    split_natural_language_proof,
)
from src.archive.semi_formalization.mutation import ProofMutation


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
STRATEGY_SELECTION_MODES = {"random", "retrieval"}
TARGET_JUDGE_SUCCESS_POLICIES = {"any", "majority", "all"}
DUPLICATE_SUCCESSFUL_MUTATION_REJECT_POLICIES = {"duplicate", "duplicate_or_variant"}


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
    seed_mined_strategies: bool = False
    strategy_selection_mode: str = "random"
    mined_strategy_path: str | Path | None = None
    target_judge_samples: int = 1
    target_judge_success_policy: str = "all"
    judge_error_detection_check: bool = False
    run_original_error_control: bool = False
    original_proof_may_be_incorrect: bool = False
    full_proof_mutation_output: bool = False
    max_previous_failed_attempts_in_prompt: int = 3
    max_previous_failed_attempt_chars: int = 4_000
    max_previous_successful_attempts_in_prompt: int = 3
    max_previous_successful_attempt_chars: int = 4_000
    reject_duplicate_successful_mutations: bool = False
    duplicate_successful_mutation_retries: int = 1
    duplicate_successful_mutation_reject_policy: str = "duplicate_or_variant"
    run_pre_mutation_judge: bool = True
    trace_llm_calls: bool = True
    trace_dir: str | Path | None = None

    def __post_init__(self) -> None:
        if self.correctness_selection_mode not in CORRECTNESS_SELECTION_MODES:
            allowed = ", ".join(sorted(CORRECTNESS_SELECTION_MODES))
            raise ValueError(
                "Unknown correctness selection mode "
                f"{self.correctness_selection_mode!r}; expected one of: {allowed}"
            )
        if self.strategy_selection_mode not in STRATEGY_SELECTION_MODES:
            allowed = ", ".join(sorted(STRATEGY_SELECTION_MODES))
            raise ValueError(
                "Unknown strategy selection mode "
                f"{self.strategy_selection_mode!r}; expected one of: {allowed}"
            )
        if self.target_judge_success_policy not in TARGET_JUDGE_SUCCESS_POLICIES:
            allowed = ", ".join(sorted(TARGET_JUDGE_SUCCESS_POLICIES))
            raise ValueError(
                "Unknown target judge success policy "
                f"{self.target_judge_success_policy!r}; expected one of: {allowed}"
            )
        if not 0.0 <= self.strategy_injection_probability <= 1.0:
            raise ValueError("strategy_injection_probability must be between 0 and 1.")
        if self.max_strategies_injected < 0:
            raise ValueError("max_strategies_injected must be non-negative.")
        if self.max_bank_size < 1:
            raise ValueError("max_bank_size must be at least 1.")
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
        if self.target_judge_samples < 1:
            raise ValueError("target_judge_samples must be at least 1.")
        if self.max_previous_failed_attempts_in_prompt < 0:
            raise ValueError("max_previous_failed_attempts_in_prompt must be non-negative.")
        if self.max_previous_failed_attempt_chars < 0:
            raise ValueError("max_previous_failed_attempt_chars must be non-negative.")
        if self.max_previous_successful_attempts_in_prompt < 0:
            raise ValueError("max_previous_successful_attempts_in_prompt must be non-negative.")
        if self.max_previous_successful_attempt_chars < 0:
            raise ValueError("max_previous_successful_attempt_chars must be non-negative.")
        if self.duplicate_successful_mutation_retries < 0:
            raise ValueError("duplicate_successful_mutation_retries must be non-negative.")
        if self.duplicate_successful_mutation_reject_policy not in DUPLICATE_SUCCESSFUL_MUTATION_REJECT_POLICIES:
            allowed = ", ".join(sorted(DUPLICATE_SUCCESSFUL_MUTATION_REJECT_POLICIES))
            raise ValueError(
                "Unknown duplicate_successful_mutation_reject_policy "
                f"{self.duplicate_successful_mutation_reject_policy!r}; expected one of: {allowed}"
            )


@dataclass(frozen=True)
class JudgeResult:
    """Parsed result from judging a fuzzed proof attempt."""

    verdict: str
    confidence: float = 0.0
    rationale: str = ""
    detected_flaw: str = ""
    detected_errors: tuple[dict[str, object], ...] = ()
    response_kind: str = "verdict"
    raw_response: str = ""

    def __post_init__(self) -> None:
        normalized = self.verdict.strip().lower()
        if normalized not in JUDGE_VERDICTS:
            allowed = ", ".join(sorted(JUDGE_VERDICTS))
            raise ValueError(f"Unknown judge verdict {self.verdict!r}; expected one of: {allowed}")
        object.__setattr__(self, "verdict", normalized)
        object.__setattr__(self, "confidence", float(self.confidence))
        object.__setattr__(
            self,
            "detected_errors",
            tuple(dict(error) for error in self.detected_errors),
        )

    def to_dict(self) -> dict[str, object]:
        return {
            "verdict": self.verdict,
            "confidence": self.confidence,
            "rationale": self.rationale,
            "detected_flaw": self.detected_flaw,
            "detected_errors": [dict(error) for error in self.detected_errors],
            "response_kind": self.response_kind,
            "raw_response": self.raw_response,
        }

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "JudgeResult":
        return cls(
            verdict=str(data.get("verdict", "")),
            confidence=float(data.get("confidence", 0.0) or 0.0),
            rationale=str(data.get("rationale", "")),
            detected_flaw=str(data.get("detected_flaw", "")),
            detected_errors=_error_inventory(data.get("detected_errors", ())),
            response_kind=str(data.get("response_kind") or "verdict"),
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
    math_topic: str = ""
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
        topic = _normalize_topic(
            self.math_topic
            or self.metadata.get("math_topic")
            or self.metadata.get("topic")
        )
        metadata = dict(self.metadata)
        if topic:
            metadata["math_topic"] = topic
            metadata["topic"] = topic
        object.__setattr__(self, "math_topic", topic)
        object.__setattr__(self, "metadata", metadata)

    def to_dict(self) -> dict[str, object]:
        return {
            "strategy_id": self.strategy_id,
            "fuzzer_kind": self.fuzzer_kind,
            "title": self.title,
            "guidance": self.guidance,
            "math_topic": self.math_topic,
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
        metadata = dict(data.get("metadata", {}) if isinstance(data.get("metadata"), dict) else {})
        return cls(
            strategy_id=str(data.get("strategy_id") or data.get("id") or _new_id("strategy")),
            fuzzer_kind=str(data.get("fuzzer_kind", FUZZER_KIND_SEMIFORMAL)),
            title=str(data.get("title", "")),
            guidance=str(data.get("guidance", "")),
            math_topic=str(data.get("math_topic") or data.get("topic") or metadata.get("math_topic") or metadata.get("topic") or ""),
            target_correctness=_parse_optional_bool(data.get("target_correctness")),
            successes=int(data.get("successes", 0) or 0),
            failures=int(data.get("failures", 0) or 0),
            provenance_attempt_ids=_string_tuple(data.get("provenance_attempt_ids", ())),
            created_at=str(data.get("created_at") or _utc_now()),
            updated_at=str(data.get("updated_at") or _utc_now()),
            metadata=metadata,
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

    def seed_strategies(self, fuzzer_kind: str, strategies: Iterable[FuzzStrategy]) -> tuple[FuzzStrategy, ...]:
        """Insert strategies with new ids into the existing bank."""

        normalized_kind = _normalize_fuzzer_kind(fuzzer_kind)
        with self.lock:
            existing = list(self.load_strategies(normalized_kind))
            existing_ids = {strategy.strategy_id for strategy in existing}
            seeded = [
                strategy
                for strategy in strategies
                if _normalize_fuzzer_kind(strategy.fuzzer_kind) == normalized_kind
                and strategy.strategy_id not in existing_ids
            ]
            if seeded:
                self.save_strategies(normalized_kind, [*existing, *seeded])
            return tuple(seeded)

    def last_evolved_attempt_count(self, fuzzer_kind: str) -> int:
        with self.lock:
            state = self._load_state()
            return int(state.get(_normalize_fuzzer_kind(fuzzer_kind), 0) or 0)

    def set_last_evolved_attempt_count(self, fuzzer_kind: str, count: int) -> None:
        with self.lock:
            state = self._load_state()
            state[_normalize_fuzzer_kind(fuzzer_kind)] = int(count)
            self.state_path.write_text(json.dumps(state, indent=2, sort_keys=True), encoding="utf-8")

    def last_evolved_attempt_count_for_topic(self, fuzzer_kind: str, math_topic: str) -> int:
        with self.lock:
            state = self._load_state()
            key = _topic_state_key(fuzzer_kind=fuzzer_kind, math_topic=math_topic)
            return int(state.get(key, 0) or 0)

    def set_last_evolved_attempt_count_for_topic(self, fuzzer_kind: str, math_topic: str, count: int) -> None:
        with self.lock:
            state = self._load_state()
            state[_topic_state_key(fuzzer_kind=fuzzer_kind, math_topic=math_topic)] = int(count)
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
        problem_text: str = "",
    ) -> JudgeResult:
        response = self.llm.complete(
            self.judge_prompt(
                original_proof_text=original_proof_text,
                mutation_instructions=mutation_instructions,
                mutated_proof_text=mutated_proof_text,
                fuzzer_kind=fuzzer_kind,
                objective=objective,
                problem_text=problem_text,
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
        problem_text: str = "",
    ) -> str:
        del fuzzer_kind
        problem = problem_text.strip() or _extract_problem_text_from_objective(objective) or "not specified"
        proof_block = (
            mutated_proof_text
            if mutated_proof_text.strip()
            else "not available; judge only the visible mutation record and return uncertain if correctness cannot be verified"
        )
        return f"""You are a mathematical proof auditor checking a modified proof.

Task: decide whether the submitted mutated proof is mathematically correct for the problem. The
reference proof is believed to be correct; the mutation record is untrusted context describing an
intended edit. Do not treat the mutation record as evidence that the proof is wrong.

Problem:
```text
{problem}
```

Reference original proof:
```text
{original_proof_text}
```

Mutation record:
```json
{json.dumps(mutation_instructions.to_dict(), indent=2, sort_keys=True)}
```

Submitted mutated proof:
```text
{proof_block}
```

Use these verdict rules:
- Return "incorrect" only when the mutated proof contains an unrepaired mathematical error, missing
  case, invalid inference, or unsupported dependency that is actually needed for the proof as written.
- For an intentionally incorrect mutation, return "incorrect" only when the edit introduces one
  independent root-cause error and remains minimally exposed. Multiple edits are allowed only when
  they consistently propagate that one semantic change; do not penalize companion edits needed to
  keep dependent reasoning natural and internally coherent. Return "uncertain" when the mutation is
  mathematically wrong but also introduces a second independent defect, an avoidable contradiction,
  malformed notation, or repeated conspicuous clues that make the planted error non-minimal.
- Return "correct" when the mutation rationale describes a suspicious step but the proof still has a
  valid route to the conclusion, the omitted case is impossible, or a later/earlier argument repairs
  the gap.
- Return "correct" when a local statement is stronger, weaker, or oddly phrased but the displayed
  equations still justify the conclusion.
- Return "incorrect" when the proof proves only a congruence/residue/average but then treats it as an
  exact equality or actual value without a bounding/range argument.
- Return "incorrect" when a geometric argument proves only distance, parallelism, radical-axis
  membership, or a center/perpendicular fact but then identifies a specific point, midpoint, foot,
  tangent point, side, or chord membership without proving the required incidence.
- Return "incorrect" when a recurrence, induction, periodicity, or case split is used outside the
  range where the hypotheses define it, unless the proof explicitly conditions on that larger range.
- If the original or mutated proof contains an omitted-text marker such as "[... truncated for context
  budget ...]", do not infer what the omitted portion says. Return "incorrect" only for a visible
  local flaw that cannot be repaired by omitted context; return "correct" only when the visible proof
  is complete enough to verify; otherwise return "uncertain".
- Do not mark a proof incorrect merely because the original proof used a more detailed argument.
  The mutated proof may use a different valid shortcut.
- Do not mark a proof incorrect merely because the mutation record claims a flaw. If the alleged
  flaw is harmless or impossible under the preceding equations, say so and return "correct".

In the rationale, explicitly state whether the alleged mutation flaw is necessary to the proof or is
salvaged/irrelevant. If incorrect, name the first indispensable broken step.
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


class ImperfectProofMutationJudge(ProofFuzzJudge):
    """Check the described introduced flaw in its mathematical context."""

    def judge_prompt(
        self, *, original_proof_text: str,
        mutation_instructions: FuzzerMutationInstructions,
        mutated_proof_text: str = "", fuzzer_kind: str = FUZZER_KIND_SEMIFORMAL,
        objective: str = "", problem_text: str = "",
    ) -> str:
        del fuzzer_kind
        problem = problem_text.strip() or _extract_problem_text_from_objective(objective) or "not specified"
        explanation = mutation_instructions.rationale.strip() or "\n".join(
            mutation.summary for mutation in mutation_instructions.mutations
        )
        return f"""You are checking a described error introduced into a mathematical proof.

Task: determine whether the introduced-error explanation identifies a real logical or
mathematical flaw in the mutated proof. Inspect the claimed step and the context needed to
assess it. Treat the explanation as a claim to verify, not as evidence that an error exists.

The original proof is supplied only to distinguish the introduced flaw from existing defects.
It may already be wrong. Do not audit unrelated parts of either proof or judge the overall
theorem. Global invalidity alone never validates a mutation.

Problem:
<problem>
{problem}
</problem>

Original proof (comparison context):
<original_proof>
{original_proof_text}
</original_proof>

Mutated proof:
<mutated_proof>
{mutated_proof_text}
</mutated_proof>

Introduced-error explanation:
<introduced_error>
{explanation}
</introduced_error>

Verdict rules (these refer only to the described introduced flaw):
- "incorrect": the described edit introduces a genuine false assertion, invalid inference,
  calculation error, or other logical flaw in the proof's stated context.
- "correct": the alleged flaw is actually valid in context, the claimed change is absent,
  or the same defect was already present. Reject rewordings or downstream manifestations
  of pre-existing errors as evidence of a new flaw.
- "uncertain": the supplied text is insufficient to establish whether the described flaw
  is real and newly introduced. Do not invent missing hypotheses or context.

A real erroneous step still counts when the final conclusion is true or another argument
establishes it. The error need not be essential to the overall proof. Conversely, an explicitly
retracted intermediate claim or a claim justified by the applicable hypotheses is not a flaw
merely because the explanation calls it one. Subtlety, stylistic plausibility, and the number
of textual edits are not criteria for this check.

In the rationale, identify the described step and explain why it is logically flawed or
valid under the applicable hypotheses. Address the supplied explanation directly.
Return exactly one JSON object with no prose outside JSON:
{{
  "verdict": "correct | incorrect | uncertain",
  "confidence": 0.0,
  "rationale": "assessment of the described introduced error",
  "detected_flaw": "the verified introduced flaw, or empty if none was verified"
}}
"""


class BlindProofErrorFinder:
    """Uses an LLM to inventory errors without revealing the planted mutation."""

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
        del fuzzer_kind
        problem_block = problem_text.strip() or "not specified"
        return f"""You are reviewing a mathematical reasoning trace for errors.

ERROR-FINDING TASK:
Read the entire trace closely and report every concrete mathematical or logical error you find.
Include erroneous assertions and invalid inferences even when the final conclusion is true or
another argument establishes it. Identify the affected step and explain the error under the
applicable hypotheses. Check cases and dependencies, false claims, invalid or
circular inferences, hidden assumptions, algebraic or computational mistakes,
sign/indexing/quantifier errors, unsupported changes of scope, and conclusions stronger than the
reasoning establishes.

Do not assign a score and do not return a binary correct/incorrect verdict. Your job is to
produce an error inventory. Include an item only when you can identify a specific erroneous
assertion or reasoning step and explain why it is wrong. Group multiple downstream symptoms,
repeated occurrences, and consequences of the same root cause into one item. Do not list generic
requests for more detail, optional improvements, style concerns, harmless wording differences,
extraction/formatting artifacts, or explicitly retracted claims. Report an omission only when
you can identify a specific unsupported inference, rather than a broad completeness complaint.
If you find no concrete error, return an empty list. Do not assume the trace contains an error.

PROBLEM:
```text
{problem_block}
```

REASONING TRACE TO REVIEW:
```text
{proof_text}
```

Return exactly one JSON object with no prose outside JSON. Preserve genuinely independent root
causes as distinct items, but do not split one root cause into several symptoms.
Schema:
```json
{{
  "errors": [
    {{
      "location": "step, equation, quotation, or other precise locator",
      "root_cause": "one-sentence statement of the independent root error",
      "description": "specific mathematical or logical error",
      "consequence": "effect on the affected step and any downstream reasoning; state if local only",
      "severity": "minor | major | critical",
      "confidence": 0.0
    }}
  ],
  "review_summary": "brief description of what was checked"
}}
```
"""


# Backward-compatible import name for callers created before blind reviews became
# error inventories. The class no longer asks for a correctness verdict.
BlindProofCorrectnessJudge = BlindProofErrorFinder


class IntroducedErrorMatcher:
    """Checks whether blind error inventories identified the planted mutation."""

    def __init__(self, llm: LLMClient):
        self.llm = llm

    def prompt(
        self,
        *,
        mutation_instructions: FuzzerMutationInstructions,
        judge_results: Iterable[JudgeResult],
        original_judge_results: Iterable[JudgeResult] = (),
        original_proof_text: str = "",
        mutated_proof_text: str = "",
    ) -> str:
        judge_payload = [result.to_dict() for result in judge_results]
        original_judge_payload = [
            result.to_dict() for result in original_judge_results
        ]
        explanation = mutation_instructions.rationale.strip() or "\n".join(
            mutation.summary for mutation in mutation_instructions.mutations
        )
        return f"""You are auditing blind error-finder reports for a proof-fuzzing run.

The blind error finders saw only the problem and submitted reasoning trace. They did not see the
original trace or introduced-error explanation. You receive both proofs, the explanation of the
introduced error, and both error inventories. Use the explanation to identify the specific planted
error, verify its location against the proofs, and decide whether any reported error explicitly or
uniquely identified that error. The explanation itself is not evidence that the blind reviewer
detected it; detection must be supported by an entry in the mutated-proof inventory.

Original proof:
```text
{original_proof_text}
```

Introduced-error explanation:
<introduced_error>
{explanation}
</introduced_error>

Mutated proof:
```text
{mutated_proof_text}
```

Blind error-finder reports:
```json
{json.dumps(judge_payload, indent=2, sort_keys=True)}
```

Control error-finder reports on the unmodified original proof:
```json
{json.dumps(original_judge_payload, indent=2, sort_keys=True)}
```

Evaluate the individual entries in each mutated-proof report's `detected_errors` list. Count the
introduced error as found only when an entry explicitly identifies the changed premise, fact,
quantifier, calculation, or inference, or states a logically equivalent and uniquely identifying
failure with the correct causal connection. A generic downstream complaint, topic overlap,
generic caution, broad incompleteness claim, unrelated doubt, or wrong diagnosis is not a match.
Do not count an issue that was already present in the original proof. Use the control reports as
evidence of pre-existing issues, and verify against the original and mutated text yourself.

There is no partial-credit detection: borderline or merely suggestive overlap is a miss. Set
`introduced_error_found` to true if and only if `match_level` is `exact`.
Return exactly one JSON object with no prose outside JSON.
Schema:
```json
{{
  "introduced_error_found": false,
  "matching_report_indices": [0],
  "matching_error_indices": [{{"report_index": 0, "error_index": 1}}],
  "match_level": "none | exact",
  "rationale": "brief justification"
}}
```
"""

    def check(
        self,
        *,
        mutation_instructions: FuzzerMutationInstructions,
        judge_results: Iterable[JudgeResult],
        original_judge_results: Iterable[JudgeResult] = (),
        original_proof_text: str = "",
        mutated_proof_text: str = "",
    ) -> dict[str, object]:
        response = self.llm.complete(
            self.prompt(
                mutation_instructions=mutation_instructions,
                judge_results=judge_results,
                original_judge_results=original_judge_results,
                original_proof_text=original_proof_text,
                mutated_proof_text=mutated_proof_text,
            )
        )
        result = parse_judge_error_detection_result(response)
        result["raw_response"] = response
        return result


# Backward-compatible name for existing callers and stored configuration.
JudgeErrorDetectionChecker = IntroducedErrorMatcher


class SuccessfulMutationNoveltyChecker:
    """Checks whether a proposed mutation repeats prior successes on the same proof."""

    def __init__(self, llm: LLMClient):
        self.llm = llm

    def prompt(
        self,
        *,
        previous_successful_attempts: Iterable[FuzzAttempt],
        proposed_mutation_instructions: FuzzerMutationInstructions,
        original_proof_text: str = "",
    ) -> str:
        previous_payload = [
            _attempt_novelty_payload(attempt)
            for attempt in previous_successful_attempts
        ]
        return f"""You are checking novelty for a proof-fuzzing mutation.

The fuzzer already found successful mutations on this same original proof. Decide whether the new proposed mutation is substantively different.

Original proof:
```text
{original_proof_text}
```

Previous successful mutations on this proof:
```json
{json.dumps(previous_payload, indent=2, sort_keys=True)}
```

New proposed mutation:
```json
{json.dumps(proposed_mutation_instructions.to_dict(), indent=2, sort_keys=True)}
```

Classify the new mutation:
- "duplicate": same target/dependency and same mathematical error mechanism as a prior success.
- "variant": minor wording or propagation variation of a prior success; not substantively new.
- "novel": different target dependency or clearly different mathematical error mechanism.

Return exactly one JSON object with no prose outside JSON.
Schema:
```json
{{
  "novelty": "duplicate | variant | novel",
  "matching_attempt_ids": ["prior attempt ids that are repeated or varied"],
  "rationale": "brief explanation",
  "suggested_retry_guidance": "one sentence telling the fuzzer what attack surface to avoid next"
}}
```
"""

    def check(
        self,
        *,
        previous_successful_attempts: Iterable[FuzzAttempt],
        proposed_mutation_instructions: FuzzerMutationInstructions,
        original_proof_text: str = "",
    ) -> dict[str, object]:
        response = self.llm.complete(
            self.prompt(
                previous_successful_attempts=previous_successful_attempts,
                proposed_mutation_instructions=proposed_mutation_instructions,
                original_proof_text=original_proof_text,
            )
        )
        result = parse_successful_mutation_novelty_result(response)
        result["raw_response"] = response
        return result


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
      "math_topic": "algebra | number_theory | geometry | combinatorics | analysis",
      "target_correctness": true,
      "successes": 0,
      "failures": 0,
      "provenance_attempt_ids": ["attempt ids that support this strategy"],
      "metadata": {{"source": "evolved", "keywords": ["compact retrieval keyword"]}}
    }}
  ]
}}
```
Use null for target_correctness when a strategy applies to both correctness targets.
Every strategy must include a math_topic matching the topic of the attempts it applies to.
"""


class EvolutionaryProofFuzzer:
    """Runs fuzzing attempts with judged outcomes and evolved strategy guidance."""

    def __init__(
        self,
        fuzzer: ProofFuzzerLLMInterfaceBase,
        *,
        store: ProofFuzzAttemptStore | None = None,
        judge: BlindProofErrorFinder | None = None,
        mutation_checker: ProofFuzzJudge | None = None,
        judge_error_checker: IntroducedErrorMatcher | None = None,
        successful_mutation_novelty_checker: SuccessfulMutationNoveltyChecker | None = None,
        evolver: StrategyEvolver | None = None,
        config: EvolutionConfig | None = None,
        fixed_strategies: Iterable[FuzzStrategy] | None = None,
    ):
        self.fuzzer = fuzzer
        self.config = config or EvolutionConfig()
        self.store = store or ProofFuzzAttemptStore(self.config.storage_dir)
        if judge is None:
            if fuzzer.llm is None:
                raise ValueError("A judge or fuzzer LLM client is required for evolutionary fuzzing.")
            judge = BlindProofErrorFinder(fuzzer.llm)
        if mutation_checker is None:
            if fuzzer.llm is None:
                raise ValueError("A mutation checker or fuzzer LLM client is required for evolutionary fuzzing.")
            mutation_checker = (
                ImperfectProofMutationJudge(fuzzer.llm)
                if self.config.original_proof_may_be_incorrect
                else ProofFuzzJudge(fuzzer.llm)
            )
        if judge_error_checker is None:
            if fuzzer.llm is None:
                raise ValueError("An introduced-error matcher or fuzzer LLM client is required for evolutionary fuzzing.")
            judge_error_checker = IntroducedErrorMatcher(fuzzer.llm)
        if successful_mutation_novelty_checker is None:
            if fuzzer.llm is None:
                raise ValueError("A novelty checker or fuzzer LLM client is required for evolutionary fuzzing.")
            successful_mutation_novelty_checker = SuccessfulMutationNoveltyChecker(fuzzer.llm)
        if evolver is None:
            if fuzzer.llm is None:
                raise ValueError("An evolver or fuzzer LLM client is required for evolutionary fuzzing.")
            evolver = StrategyEvolver(fuzzer.llm)
        self.judge = judge
        self.mutation_checker = mutation_checker
        self.judge_error_checker = judge_error_checker
        self.successful_mutation_novelty_checker = successful_mutation_novelty_checker
        self.evolver = evolver
        self.fixed_strategies = (
            tuple(fixed_strategies) if fixed_strategies is not None else None
        )
        self.rng = random.Random(self.config.random_seed)
        self.fuzzer_kind = infer_fuzzer_kind(fuzzer)
        if self.config.seed_mined_strategies:
            self.seed_mined_strategies()

    def seed_mined_strategies(self) -> tuple[FuzzStrategy, ...]:
        """Seed the common strategy bank with mined proof-mistake strategies."""

        return self.store.seed_strategies(
            self.fuzzer_kind,
            load_mined_strategies(self.config.mined_strategy_path),
        )

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
        original_text = proof_text_for_fuzzer(self.fuzzer)
        base_metadata = {
            **dict(metadata or {}),
            "correctness_selection": selection_metadata,
        }
        base_metadata["original_proof_sha256"] = _sha256_text(original_text)
        base_metadata["proof_identity"] = _proof_identity(base_metadata, original_text)
        trace_dir = self._prepare_attempt_trace_dir(base_metadata)
        strategies = self._sample_strategies(
            maintain_correctness=selected_correctness,
            objective=objective,
            proof_text=original_text,
            metadata=base_metadata,
        )
        base_metadata["strategy_selection"] = _strategy_selection_metadata(
            mode=(
                "fixed"
                if self.fixed_strategies is not None
                else self.config.strategy_selection_mode
            ),
            strategies=strategies,
        )
        strategy_guidance = tuple(f"{strategy.title}: {strategy.guidance}" for strategy in strategies)
        previous_failed_attempts = self._previous_failed_attempts_for_proof(
            metadata=base_metadata,
            original_proof_text=original_text,
            maintain_correctness=selected_correctness,
        )
        previous_successful_attempts = self._previous_successful_attempts_for_proof(
            metadata=base_metadata,
            original_proof_text=original_text,
            maintain_correctness=selected_correctness,
        )
        failed_attempt_guidance = _format_previous_failed_attempt_guidance(
            previous_failed_attempts,
            max_chars=self.config.max_previous_failed_attempt_chars,
        )
        successful_attempt_guidance = _format_previous_successful_attempt_guidance(
            previous_successful_attempts,
            max_chars=self.config.max_previous_successful_attempt_chars,
        )
        prior_attempt_guidance = (*failed_attempt_guidance, *successful_attempt_guidance)
        base_metadata["previous_failed_attempts_in_prompt"] = [
            attempt.attempt_id for attempt in previous_failed_attempts
        ]
        base_metadata["previous_successful_attempts_in_prompt"] = [
            attempt.attempt_id for attempt in previous_successful_attempts
        ]
        problem_text = _problem_text_from_attempt(objective=objective, metadata=base_metadata)
        try:
            pre_mutation_judge_result = None
            if self.config.run_pre_mutation_judge:
                pre_mutation_judge_result = self._with_retries(
                    lambda: self._run_blind_judge(
                        call_kind="pre_mutation_judge",
                        problem_text=problem_text,
                        proof_text=original_text,
                        fuzzer_kind=self.fuzzer_kind,
                        metadata={"attempt_stage": "pre_mutation_judge"},
                    ),
                    stage="pre_mutation_judge",
                    check_truncation=True,
                )
            else:
                base_metadata["pre_mutation_judge_skipped"] = True
            instructions: FuzzerMutationInstructions | None = None
            duplicate_retry_guidance: tuple[str, ...] = ()
            novelty_checks: list[dict[str, object]] = []
            duplicate_retry_limit = (
                self.config.duplicate_successful_mutation_retries
                if self.config.reject_duplicate_successful_mutations
                else 0
            )
            for duplicate_retry_index in range(duplicate_retry_limit + 1):
                active_prior_attempt_guidance = (
                    *prior_attempt_guidance,
                    *duplicate_retry_guidance,
                )
                instructions = None
                for fallback_index in range(self.config.context_fallbacks + 1):
                    prompt = self._mutation_prompt(
                        objective=objective,
                        maintain_correctness=selected_correctness,
                        strategy_guidance=strategy_guidance,
                        prior_attempt_guidance=active_prior_attempt_guidance,
                    )
                    try:
                        response = self._with_retries(
                            lambda: self.fuzzer._complete_with_logging(
                                prompt,
                                call_kind="evolutionary_mutation_instructions",
                                metadata={
                                    "strategy_ids": [strategy.strategy_id for strategy in strategies],
                                    "strategy_sources": [_strategy_source(strategy) for strategy in strategies],
                                    "strategy_topics": [_strategy_topic(strategy) for strategy in strategies],
                                    "context_fallback_index": fallback_index,
                                    "duplicate_retry_index": duplicate_retry_index,
                                    "attempt_stage": "mutation_llm",
                                },
                            ),
                            stage="mutation_llm",
                            check_truncation=True,
                        )
                        instructions = self._with_retries(
                            lambda: (
                                self.fuzzer.parse_full_proof_mutation_response(response)
                                if getattr(self.fuzzer, "full_proof_mutation_output", False)
                                else parse_mutation_instructions(response)
                            ),
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

                novelty_check = self._run_successful_mutation_novelty_check(
                    previous_successful_attempts=previous_successful_attempts,
                    original_proof_text=original_text,
                    proposed_mutation_instructions=instructions,
                    metadata=base_metadata,
                )
                if novelty_check is None:
                    break
                novelty_check = {
                    **novelty_check,
                    "duplicate_retry_index": duplicate_retry_index,
                }
                novelty_checks.append(novelty_check)
                if not _successful_mutation_novelty_rejected(
                    novelty_check,
                    policy=self.config.duplicate_successful_mutation_reject_policy,
                ):
                    break
                if duplicate_retry_index >= duplicate_retry_limit:
                    if novelty_checks:
                        base_metadata["successful_mutation_novelty_checks"] = novelty_checks
                    raise ValueError(
                        "Proposed mutation repeated a previous successful mutation on this proof: "
                        f"{novelty_check.get('novelty', 'unknown')}"
                    )
                duplicate_retry_guidance = (
                    _format_duplicate_success_retry_guidance(novelty_check),
                )
            if novelty_checks:
                base_metadata["successful_mutation_novelty_checks"] = novelty_checks

            mutated_text = materialize_mutated_proof(self.fuzzer, instructions)
            mutation_check_result = self._run_mutation_check(
                original_proof_text=original_text,
                mutation_instructions=instructions,
                mutated_proof_text=mutated_text,
                fuzzer_kind=self.fuzzer_kind,
                objective=objective,
                metadata=base_metadata,
            )
            target_judge_results: list[JudgeResult] = []
            original_control_judge_results: list[JudgeResult] = []
            judge_error_detection_result: dict[str, object] | None = None
            if mutation_check_result is not None and _mutation_check_allows_target_judge(
                instructions.maintain_correctness,
                mutation_check_result,
            ):
                if (
                    self.config.run_original_error_control
                    and not instructions.maintain_correctness
                ):
                    for sample_index in range(self.config.target_judge_samples):
                        call_kind = (
                            "original_error_control"
                            if self.config.target_judge_samples == 1
                            else f"original_error_control_{sample_index + 1}"
                        )
                        original_control_judge_results.append(
                            self._with_retries(
                                lambda call_kind=call_kind, sample_index=sample_index: self._run_blind_judge(
                                    call_kind=call_kind,
                                    problem_text=problem_text,
                                    proof_text=original_text,
                                    fuzzer_kind=self.fuzzer_kind,
                                    metadata={
                                        "attempt_stage": "original_error_control",
                                        "target_judge_sample_index": sample_index,
                                        "target_judge_samples": self.config.target_judge_samples,
                                    },
                                ),
                                stage=call_kind,
                                check_truncation=True,
                            )
                        )
                    base_metadata["original_error_control_reports"] = [
                        result.to_dict()
                        for result in original_control_judge_results
                    ]
                else:
                    base_metadata["original_error_control_reports"] = []
                    base_metadata["original_error_control_skipped"] = True
                for sample_index in range(self.config.target_judge_samples):
                    call_kind = (
                        "target_judge"
                        if self.config.target_judge_samples == 1
                        else f"target_judge_{sample_index + 1}"
                    )
                    judge_result_sample = self._with_retries(
                        lambda call_kind=call_kind, sample_index=sample_index: self._run_blind_judge(
                            call_kind=call_kind,
                            problem_text=problem_text,
                            proof_text=mutated_text,
                            fuzzer_kind=self.fuzzer_kind,
                            metadata={
                                "attempt_stage": "target_judge",
                                "target_judge_sample_index": sample_index,
                                "target_judge_samples": self.config.target_judge_samples,
                            },
                        ),
                        stage=call_kind,
                        check_truncation=True,
                    )
                    target_judge_results.append(judge_result_sample)
                judge_result = target_judge_results[0]
                target_reports = [result.to_dict() for result in target_judge_results]
                base_metadata["target_error_reports"] = target_reports
                # Compatibility alias for older artifact readers.
                base_metadata["target_judge_results"] = target_reports
                base_metadata["target_judge_success_policy"] = self.config.target_judge_success_policy
                judge_error_detection_result = self._run_judge_error_detection_check(
                    original_proof_text=original_text,
                    mutation_instructions=instructions,
                    mutated_proof_text=mutated_text,
                    judge_results=tuple(target_judge_results),
                    original_judge_results=tuple(original_control_judge_results),
                    metadata=base_metadata,
                )
                if judge_error_detection_result is not None:
                    base_metadata["introduced_error_match"] = judge_error_detection_result
                    base_metadata["judge_error_detection_check"] = judge_error_detection_result
            else:
                expected_verdict = "correct" if instructions.maintain_correctness else "incorrect"
                actual_verdict = (
                    mutation_check_result.verdict
                    if mutation_check_result is not None
                    else "missing"
                )
                base_metadata["target_judge_skipped"] = True
                base_metadata["target_judge_skip_reason"] = (
                    "mutation_check_verdict_"
                    f"{actual_verdict}_expected_{expected_verdict}"
                )
                base_metadata["target_error_reports"] = []
                base_metadata["target_judge_results"] = []
                base_metadata["target_judge_success_policy"] = self.config.target_judge_success_policy
                base_metadata["original_error_control_reports"] = []
                base_metadata["original_error_control_skipped"] = True
                judge_result = JudgeResult(
                    verdict="uncertain",
                    confidence=1.0,
                    rationale=(
                        "Target judge skipped because the mutation checker did not "
                        f"confirm the required {expected_verdict} proof status."
                    ),
                    detected_flaw=(
                        mutation_check_result.detected_flaw
                        if mutation_check_result is not None
                        else ""
                    ),
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
            self._write_attempt_trace_artifacts(trace_dir, attempt)
            if self.config.continue_on_error:
                return attempt
            raise

        success = fuzz_attempt_succeeded(
            instructions.maintain_correctness,
            judge_result,
            pre_mutation_judge_result=pre_mutation_judge_result,
            target_judge_results=tuple(target_judge_results),
            target_judge_success_policy=self.config.target_judge_success_policy,
            judge_error_detection_result=judge_error_detection_result,
            mutation_check_result=mutation_check_result,
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
        self._write_attempt_trace_artifacts(trace_dir, attempt)
        self._maybe_evolve()
        return attempt

    def _prepare_attempt_trace_dir(self, metadata: dict[str, object]) -> Path | None:
        if not self.config.trace_llm_calls:
            return None
        root = Path(self.config.trace_dir) if self.config.trace_dir is not None else self.store.root_dir / "source_attempt_traces"
        trace_dir = _unique_trace_dir(root, _trace_directory_name(metadata))
        trace_dir.mkdir(parents=True, exist_ok=True)
        metadata["trace_dir"] = str(trace_dir)
        metadata["trace_dir_name"] = trace_dir.name
        self.fuzzer.trace_logger = LLMTraceLogger(trace_dir / "llm_calls")
        _write_text_file(
            trace_dir / "00_trace_note.txt",
            "Raw LLM prompts, responses, and reasoning are recorded under llm_calls/ during the run.\n",
        )
        return trace_dir

    def _run_blind_judge(
        self,
        *,
        call_kind: str,
        problem_text: str,
        proof_text: str,
        fuzzer_kind: str,
        metadata: dict[str, object] | None = None,
    ) -> JudgeResult:
        prompt = self.judge.judge_prompt(
            problem_text=problem_text,
            proof_text=proof_text,
            fuzzer_kind=fuzzer_kind,
        )
        response = self.fuzzer._complete_with_logging(
            prompt,
            call_kind=call_kind,
            metadata=metadata,
        )
        return parse_judge_result(response)

    def _run_proof_mutation_check(
        self,
        *,
        original_proof_text: str,
        mutation_instructions: FuzzerMutationInstructions,
        mutated_proof_text: str,
        fuzzer_kind: str,
        objective: str,
        metadata: dict[str, object] | None = None,
    ) -> JudgeResult:
        problem_text = ""
        if metadata is not None:
            problem = metadata.get("problem")
            if isinstance(problem, str):
                problem_text = problem
        prompt = self.mutation_checker.judge_prompt(
            original_proof_text=original_proof_text,
            mutation_instructions=mutation_instructions,
            mutated_proof_text=mutated_proof_text,
            fuzzer_kind=fuzzer_kind,
            objective=objective,
            problem_text=problem_text,
        )
        response = self.fuzzer._complete_with_logging(
            prompt,
            call_kind="mutation_check",
            metadata=metadata,
        )
        return parse_judge_result(response)

    def _run_judge_error_detection_check(
        self,
        *,
        original_proof_text: str,
        mutation_instructions: FuzzerMutationInstructions,
        mutated_proof_text: str,
        judge_results: tuple[JudgeResult, ...],
        original_judge_results: tuple[JudgeResult, ...],
        metadata: dict[str, object],
    ) -> dict[str, object] | None:
        inventory_response = any(
            result.response_kind == "error_inventory"
            for result in judge_results
        )
        if not self.config.judge_error_detection_check and not inventory_response:
            return None
        if mutation_instructions.maintain_correctness:
            return None
        try:
            return self._with_retries(
                lambda: self._run_judge_error_detection_check_once(
                    original_proof_text=original_proof_text,
                    mutation_instructions=mutation_instructions,
                    mutated_proof_text=mutated_proof_text,
                    judge_results=judge_results,
                    original_judge_results=original_judge_results,
                ),
                stage="judge_error_detection_check",
                check_truncation=True,
            )
        except Exception as exc:
            metadata["judge_error_detection_check_error"] = repr(exc)
            return {
                "introduced_error_found": False,
                "any_judge_reported_correct_error": False,
                "matching_report_indices": [],
                "matching_judge_indices": [],
                "matching_error_indices": [],
                "match_level": "unknown",
                "rationale": f"judge-error detection check failed: {exc!r}",
                "check_failed": True,
            }

    def _run_judge_error_detection_check_once(
        self,
        *,
        original_proof_text: str,
        mutation_instructions: FuzzerMutationInstructions,
        mutated_proof_text: str,
        judge_results: tuple[JudgeResult, ...],
        original_judge_results: tuple[JudgeResult, ...],
    ) -> dict[str, object]:
        prompt = self.judge_error_checker.prompt(
            original_proof_text=original_proof_text,
            mutation_instructions=mutation_instructions,
            mutated_proof_text=mutated_proof_text,
            judge_results=judge_results,
            original_judge_results=original_judge_results,
        )
        response = self.fuzzer._complete_with_logging(
            prompt,
            call_kind="introduced_error_match",
            metadata={"attempt_stage": "introduced_error_match"},
        )
        result = parse_judge_error_detection_result(response)
        result["raw_response"] = response
        return result

    def _write_attempt_trace_artifacts(self, trace_dir: Path | None, attempt: FuzzAttempt) -> None:
        if trace_dir is None:
            return
        _write_json_file(trace_dir / "attempt.json", attempt.to_dict())
        _write_json_file(trace_dir / "mutation_instructions.json", attempt.mutation_instructions.to_dict())
        target_judge_results = attempt.metadata.get("target_judge_results")
        if isinstance(target_judge_results, list):
            _write_json_file(trace_dir / "target_judge_results.json", target_judge_results)
        target_error_reports = attempt.metadata.get("target_error_reports")
        if isinstance(target_error_reports, list):
            _write_json_file(trace_dir / "target_error_reports.json", target_error_reports)
        original_error_control_reports = attempt.metadata.get(
            "original_error_control_reports"
        )
        if isinstance(original_error_control_reports, list):
            _write_json_file(
                trace_dir / "original_error_control_reports.json",
                original_error_control_reports,
            )
        judge_error_detection_check = attempt.metadata.get("judge_error_detection_check")
        if isinstance(judge_error_detection_check, dict):
            _write_json_file(trace_dir / "judge_error_detection_check.json", judge_error_detection_check)
        introduced_error_match = attempt.metadata.get("introduced_error_match")
        if isinstance(introduced_error_match, dict):
            _write_json_file(trace_dir / "introduced_error_match.json", introduced_error_match)
        _write_text_file(trace_dir / "mutations_produced.txt", _format_mutations_text(attempt.mutation_instructions))
        _write_text_file(trace_dir / "original_proof.txt", attempt.original_proof_text)
        _write_text_file(trace_dir / "mutated_proof.txt", attempt.mutated_proof_text)
        _write_json_file(
            trace_dir / "trace_metadata.json",
            {
                "attempt_id": attempt.attempt_id,
                "status": attempt.status,
                "success": attempt.success,
                "fuzzer_kind": attempt.fuzzer_kind,
                "maintain_correctness": attempt.maintain_correctness,
                "created_at": attempt.created_at,
                "trace_dir": str(trace_dir),
                "trace_dir_name": trace_dir.name,
                "strategy_ids": list(attempt.strategy_ids),
                "example_id": attempt.metadata.get("example_id"),
                "sample_index": attempt.metadata.get("sample_index"),
                "problem_id": attempt.metadata.get("problem_id"),
                "math_topic": attempt.metadata.get("math_topic") or attempt.metadata.get("llm_category"),
            },
        )

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
                lambda: self._run_proof_mutation_check(
                    original_proof_text=original_proof_text,
                    mutation_instructions=mutation_instructions,
                    mutated_proof_text=mutated_proof_text,
                    fuzzer_kind=fuzzer_kind,
                    objective=objective,
                    metadata={"attempt_stage": "mutation_check"},
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
        prior_attempt_guidance: tuple[str, ...],
    ) -> str:
        if maintain_correctness is True:
            return self.fuzzer.correctness_preserving_mutation_instruction_prompt(
                objective=objective,
                strategy_guidance=strategy_guidance,
                prior_attempt_guidance=prior_attempt_guidance,
            )
        if maintain_correctness is False:
            return self.fuzzer.false_proof_mutation_instruction_prompt(
                objective=objective,
                strategy_guidance=strategy_guidance,
                prior_attempt_guidance=prior_attempt_guidance,
            )
        return self.fuzzer.mutation_instruction_prompt(
            objective=objective,
            strategy_guidance=strategy_guidance,
            prior_attempt_guidance=prior_attempt_guidance,
        )

    def _previous_failed_attempts_for_proof(
        self,
        *,
        metadata: dict[str, object],
        original_proof_text: str,
        maintain_correctness: bool | None,
    ) -> tuple[FuzzAttempt, ...]:
        limit = self.config.max_previous_failed_attempts_in_prompt
        if limit <= 0:
            return ()
        attempts = self.store.load_attempts(fuzzer_kind=self.fuzzer_kind)
        matching = [
            attempt
            for attempt in attempts
            if not attempt.success
            and attempt.status == "success"
            and (maintain_correctness is None or attempt.maintain_correctness == maintain_correctness)
            and _same_proof_attempt(attempt, metadata, original_proof_text)
        ]
        return tuple(matching[-limit:])

    def _previous_successful_attempts_for_proof(
        self,
        *,
        metadata: dict[str, object],
        original_proof_text: str,
        maintain_correctness: bool | None,
    ) -> tuple[FuzzAttempt, ...]:
        limit = self.config.max_previous_successful_attempts_in_prompt
        if limit <= 0:
            return ()
        attempts = self.store.load_attempts(fuzzer_kind=self.fuzzer_kind)
        matching = [
            attempt
            for attempt in attempts
            if attempt.success
            and attempt.status == "success"
            and (maintain_correctness is None or attempt.maintain_correctness == maintain_correctness)
            and _same_proof_attempt(attempt, metadata, original_proof_text)
        ]
        return tuple(matching[-limit:])

    def _run_successful_mutation_novelty_check(
        self,
        *,
        previous_successful_attempts: tuple[FuzzAttempt, ...],
        original_proof_text: str,
        proposed_mutation_instructions: FuzzerMutationInstructions,
        metadata: dict[str, object],
    ) -> dict[str, object] | None:
        if not self.config.reject_duplicate_successful_mutations:
            return None
        if not previous_successful_attempts:
            return None
        try:
            return self._with_retries(
                lambda: self._run_successful_mutation_novelty_check_once(
                    previous_successful_attempts=previous_successful_attempts,
                    original_proof_text=original_proof_text,
                    proposed_mutation_instructions=proposed_mutation_instructions,
                ),
                stage="successful_mutation_novelty_check",
                check_truncation=True,
            )
        except Exception as exc:
            metadata["successful_mutation_novelty_check_error"] = repr(exc)
            return {
                "novelty": "unknown",
                "matching_attempt_ids": [],
                "rationale": f"novelty check failed: {exc!r}",
                "suggested_retry_guidance": "",
                "check_failed": True,
            }

    def _run_successful_mutation_novelty_check_once(
        self,
        *,
        previous_successful_attempts: tuple[FuzzAttempt, ...],
        original_proof_text: str,
        proposed_mutation_instructions: FuzzerMutationInstructions,
    ) -> dict[str, object]:
        prompt = self.successful_mutation_novelty_checker.prompt(
            previous_successful_attempts=previous_successful_attempts,
            original_proof_text=original_proof_text,
            proposed_mutation_instructions=proposed_mutation_instructions,
        )
        response = self.fuzzer._complete_with_logging(
            prompt,
            call_kind="successful_mutation_novelty_check",
            metadata={"attempt_stage": "successful_mutation_novelty_check"},
        )
        result = parse_successful_mutation_novelty_result(response)
        result["raw_response"] = response
        return result

    def _sample_strategies(
        self,
        *,
        maintain_correctness: bool | None,
        objective: str = "",
        proof_text: str = "",
        metadata: dict[str, object] | None = None,
    ) -> tuple[FuzzStrategy, ...]:
        if self.fixed_strategies is not None:
            return self.fixed_strategies
        if self.config.strategy_injection_probability <= 0:
            return ()
        if self.rng.random() > self.config.strategy_injection_probability:
            return ()

        strategies = [
            strategy
            for strategy in self.store.load_strategies(self.fuzzer_kind)
            if strategy.target_correctness is None or maintain_correctness is None or strategy.target_correctness == maintain_correctness
        ]
        strategies = _filter_strategies_by_attempt_topic(strategies, metadata or {})
        if self.config.strategy_selection_mode == "retrieval":
            return self._retrieve_strategies(
                strategies,
                objective=objective,
                proof_text=proof_text,
                metadata=metadata or {},
            )
        self.rng.shuffle(strategies)
        return tuple(strategies[: self.config.max_strategies_injected])

    def _retrieve_strategies(
        self,
        strategies: list[FuzzStrategy],
        *,
        objective: str,
        proof_text: str,
        metadata: dict[str, object],
    ) -> tuple[FuzzStrategy, ...]:
        if self.config.max_strategies_injected <= 0:
            return ()
        query_tokens = _strategy_query_tokens(
            objective=objective,
            proof_text=proof_text,
            metadata=metadata,
        )
        query_topic = _topic_from_metadata(metadata)
        scored = [
            (
                _strategy_retrieval_score(
                    strategy,
                    query_tokens=query_tokens,
                    query_topic=query_topic,
                ),
                self.rng.random(),
                strategy,
            )
            for strategy in strategies
        ]
        scored.sort(key=lambda item: (item[0], item[1]), reverse=True)
        return tuple(strategy for _, _, strategy in scored[: self.config.max_strategies_injected])

    def _maybe_evolve(self) -> None:
        threshold = self.config.evolution_threshold
        if threshold <= 0:
            return
        with self.store.lock:
            successful_attempts = tuple(
                attempt
                for attempt in self.store.load_attempts(fuzzer_kind=self.fuzzer_kind)
                if attempt.status == "success"
            )
            attempts_by_topic = _attempts_by_topic(successful_attempts)
            if not attempts_by_topic:
                return

            bank = self.store.load_strategies(self.fuzzer_kind)
            updated_bank = list(bank)
            evolved_any = False
            evolved_counts: dict[str, int] = {}

            for topic in sorted(attempts_by_topic):
                topic_attempt_count = len(attempts_by_topic[topic])
                last_evolved = self.store.last_evolved_attempt_count_for_topic(self.fuzzer_kind, topic)
                if topic_attempt_count - last_evolved < threshold:
                    continue

                topic_attempts = attempts_by_topic[topic][-max(threshold * 3, threshold):]
                topic_bank = tuple(strategy for strategy in updated_bank if _strategy_topic(strategy) == topic)
                pinned = tuple(strategy for strategy in topic_bank if _strategy_is_pinned(strategy))
                try:
                    strategies = self._with_retries(
                        lambda topic_attempts=topic_attempts, topic_bank=topic_bank: self.evolver.evolve(
                            fuzzer_kind=self.fuzzer_kind,
                            attempts=topic_attempts,
                            existing_strategies=topic_bank,
                            max_bank_size=self.config.max_bank_size,
                        ),
                        stage=f"strategy_evolution_{topic}",
                        check_truncation=True,
                    )
                except Exception:
                    continue
                strategies = _force_strategy_topic(
                    _fill_missing_strategy_topics(strategies, topic_attempts),
                    topic,
                )
                topic_replacement = _merge_pinned_strategies(strategies, pinned)
                updated_bank = [
                    strategy
                    for strategy in updated_bank
                    if _strategy_topic(strategy) != topic
                ] + list(topic_replacement)
                evolved_any = True
                evolved_counts[topic] = topic_attempt_count

            if not evolved_any:
                return
            self.store.save_strategies(self.fuzzer_kind, updated_bank)
            for topic, count in evolved_counts.items():
                self.store.set_last_evolved_attempt_count_for_topic(self.fuzzer_kind, topic, count)


def load_mined_strategies(path: str | Path | None = None) -> tuple[FuzzStrategy, ...]:
    """Load a local JSONL strategy library (not distributed with the source)."""

    strategy_path = Path(path) if path is not None else Path(__file__).with_name("data") / "mined_strategies.jsonl"
    if not strategy_path.is_file():
        raise FileNotFoundError(
            f"Mined strategy seed file does not exist: {strategy_path}. "
            "Strategy data is local; supply mined_strategy_path / --mined-strategy-path."
        )
    strategies: list[FuzzStrategy] = []
    for line in strategy_path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            strategies.append(FuzzStrategy.from_dict(json.loads(line)))
    return tuple(strategies)


def parse_judge_result(text: str) -> JudgeResult:
    try:
        data = _load_json_object(text)
    except (ValueError, json.JSONDecodeError):
        cleaned = text.strip()
        if not cleaned or cleaned.startswith(("{", "[")):
            raise
        if re.fullmatch(
            r"(?is)(?:[#>*_\s-]*)(?:i\s+(?:found|identify|see)\s+)?"
            r"(?:no|none)(?:\s+concrete)?\s+(?:mathematical\s+|logical\s+)?"
            r"errors?(?:\s+(?:were\s+)?found|\s+identified)?[.!\s]*",
            cleaned,
        ):
            errors = ()
        else:
            items = [part.strip() for part in re.split(
                r"(?m)(?=^\s*(?:[-*+]\s+|\d+[.)]\s+))", cleaned) if part.strip()]
            if len(items) == 1:
                items = [cleaned]
            errors = tuple({
                "location": f"unstructured report item {index}",
                "root_cause": "",
                "description": re.sub(
                    r"^\s*(?:[-*+]\s+|\d+[.)]\s+)", "", item).strip(),
                "consequence": "",
                "severity": "major",
                "confidence": 0.0,
                "unstructured": True,
            } for index, item in enumerate(items, 1))
        return JudgeResult(
            verdict="incorrect" if errors else "correct",
            confidence=0.0,
            rationale="Parsed from a non-JSON error inventory.",
            detected_flaw="; ".join(str(error["description"]) for error in errors),
            detected_errors=errors,
            response_kind="error_inventory",
            raw_response=text,
        )
    if "errors" in data and "verdict" not in data:
        errors = _error_inventory(data.get("errors"))
        descriptions = [
            str(error.get("description", "")).strip()
            for error in errors
            if str(error.get("description", "")).strip()
        ]
        confidences = [
            float(error.get("confidence", 0.0) or 0.0)
            for error in errors
            if isinstance(error.get("confidence", 0.0), (int, float))
        ]
        # `verdict` is a compatibility projection for existing artifacts only. Attack
        # success is decided by the separate introduced-error matcher below.
        return JudgeResult(
            verdict="incorrect" if errors else "correct",
            confidence=max(confidences, default=0.0),
            rationale=str(data.get("review_summary", "")),
            detected_flaw="; ".join(descriptions),
            detected_errors=errors,
            response_kind="error_inventory",
            raw_response=text,
        )
    return JudgeResult(
        verdict=str(data.get("verdict", "")),
        confidence=float(data.get("confidence", 0.0) or 0.0),
        rationale=str(data.get("rationale", "")),
        detected_flaw=str(data.get("detected_flaw", "")),
        raw_response=text,
    )


def parse_judge_error_detection_result(text: str) -> dict[str, object]:
    data = _load_json_object(text)
    reported_found = bool(
        data.get(
            "introduced_error_found",
            data.get("any_judge_reported_correct_error", False),
        )
    )
    raw_indices = data.get(
        "matching_report_indices",
        data.get("matching_judge_indices", ()),
    )
    matching_indices: list[int] = []
    if isinstance(raw_indices, list):
        for index in raw_indices:
            try:
                matching_indices.append(int(index))
            except (TypeError, ValueError):
                continue
    match_level = str(data.get("match_level", "none")).strip().lower()
    if match_level not in {"none", "partial", "exact"}:
        match_level = "none"
    # Partial or suggestive overlap is deliberately treated as a miss. This also
    # normalizes older matcher responses that used the legacy `partial` level.
    introduced_error_found = reported_found and match_level == "exact"
    raw_error_indices = data.get("matching_error_indices", ())
    matching_error_indices = [
        {
            "report_index": int(item.get("report_index", 0)),
            "error_index": int(item.get("error_index", 0)),
        }
        for item in raw_error_indices
        if isinstance(item, dict)
        and str(item.get("report_index", "")).lstrip("-").isdigit()
        and str(item.get("error_index", "")).lstrip("-").isdigit()
    ] if isinstance(raw_error_indices, list) else []
    return {
        "introduced_error_found": introduced_error_found,
        # Retain the old key so existing analysis code can read new runs.
        "any_judge_reported_correct_error": introduced_error_found,
        "matching_report_indices": matching_indices,
        "matching_judge_indices": matching_indices,
        "matching_error_indices": matching_error_indices,
        "match_level": match_level,
        "matcher_policy": "exact_only",
        "reported_introduced_error_found": reported_found,
        "rationale": str(data.get("rationale", "")),
    }


def parse_successful_mutation_novelty_result(text: str) -> dict[str, object]:
    data = _load_json_object(text)
    novelty = str(data.get("novelty", "")).strip().lower()
    if novelty not in {"duplicate", "variant", "novel", "unknown"}:
        novelty = "unknown"
    raw_ids = data.get("matching_attempt_ids", ())
    matching_ids: list[str] = []
    if isinstance(raw_ids, list):
        matching_ids = [str(item) for item in raw_ids if str(item).strip()]
    return {
        "novelty": novelty,
        "matching_attempt_ids": matching_ids,
        "rationale": str(data.get("rationale", "")),
        "suggested_retry_guidance": str(data.get("suggested_retry_guidance", "")),
    }


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
                math_topic=str(raw_strategy.get("math_topic") or raw_strategy.get("topic") or ""),
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
    target_judge_results: Iterable[JudgeResult] | None = None,
    target_judge_success_policy: str = "all",
    judge_error_detection_result: dict[str, object] | None = None,
    mutation_check_result: JudgeResult | None = None,
) -> bool:
    if pre_mutation_judge_result is not None and pre_mutation_judge_result.verdict != "correct":
        return False
    if mutation_check_result is not None and not _mutation_check_allows_target_judge(
        maintain_correctness,
        mutation_check_result,
    ):
        return False
    if target_judge_success_policy not in TARGET_JUDGE_SUCCESS_POLICIES:
        allowed = ", ".join(sorted(TARGET_JUDGE_SUCCESS_POLICIES))
        raise ValueError(
            "Unknown target judge success policy "
            f"{target_judge_success_policy!r}; expected one of: {allowed}"
        )
    if not maintain_correctness and judge_error_detection_result is not None:
        return not (
            bool(judge_error_detection_result.get("check_failed"))
            or bool(
                judge_error_detection_result.get(
                    "introduced_error_found",
                    judge_error_detection_result.get(
                        "any_judge_reported_correct_error",
                        False,
                    ),
                )
            )
        )
    judge_results = tuple(target_judge_results or (judge_result,))
    if not judge_results:
        judge_results = (judge_result,)
    per_judge_success = tuple(
        _single_judge_success(maintain_correctness, result)
        for result in judge_results
    )
    if target_judge_success_policy == "all":
        accepted_by_target = all(per_judge_success)
    elif target_judge_success_policy == "majority":
        accepted_by_target = sum(1 for value in per_judge_success if value) > len(per_judge_success) / 2
    else:
        accepted_by_target = any(per_judge_success)
    if not accepted_by_target:
        return False
    return True


def _mutation_check_allows_target_judge(
    maintain_correctness: bool,
    mutation_check_result: JudgeResult,
) -> bool:
    expected_verdict = "correct" if maintain_correctness else "incorrect"
    return mutation_check_result.verdict == expected_verdict


def _single_judge_success(maintain_correctness: bool, judge_result: JudgeResult) -> bool:
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


def _strategy_selection_metadata(*, mode: str, strategies: tuple[FuzzStrategy, ...]) -> dict[str, object]:
    return {
        "mode": mode,
        "selected_strategy_ids": [strategy.strategy_id for strategy in strategies],
        "selected_strategy_sources": [_strategy_source(strategy) for strategy in strategies],
        "selected_strategy_topics": [_strategy_topic(strategy) for strategy in strategies],
    }


def _strategy_source(strategy: FuzzStrategy) -> str:
    source = strategy.metadata.get("source")
    return str(source) if source is not None else "evolved"


def _strategy_topic(strategy: FuzzStrategy) -> str:
    return _normalize_topic(strategy.math_topic or strategy.metadata.get("math_topic") or strategy.metadata.get("topic"))


def _strategy_is_pinned(strategy: FuzzStrategy) -> bool:
    return bool(strategy.metadata.get("pinned"))


def _merge_pinned_strategies(
    strategies: Iterable[FuzzStrategy],
    pinned_strategies: Iterable[FuzzStrategy],
) -> tuple[FuzzStrategy, ...]:
    pinned_by_id = {strategy.strategy_id: strategy for strategy in pinned_strategies}
    merged: list[FuzzStrategy] = []
    seen: set[str] = set()
    for strategy in strategies:
        replacement = pinned_by_id.get(strategy.strategy_id, strategy)
        if replacement.strategy_id in seen:
            continue
        merged.append(replacement)
        seen.add(replacement.strategy_id)
    for strategy in pinned_by_id.values():
        if strategy.strategy_id not in seen:
            merged.append(strategy)
            seen.add(strategy.strategy_id)
    return tuple(merged)


def _filter_strategies_by_attempt_topic(
    strategies: Iterable[FuzzStrategy],
    metadata: dict[str, object],
) -> list[FuzzStrategy]:
    topic = _topic_from_metadata(metadata)
    if not topic:
        return list(strategies)
    return [strategy for strategy in strategies if _strategy_topic(strategy) == topic]


def _attempts_by_topic(attempts: Iterable[FuzzAttempt]) -> dict[str, list[FuzzAttempt]]:
    attempts_by_topic: dict[str, list[FuzzAttempt]] = {}
    for attempt in attempts:
        topic = _topic_from_metadata(attempt.metadata)
        if not topic:
            continue
        attempts_by_topic.setdefault(topic, []).append(attempt)
    return attempts_by_topic


def _fill_missing_strategy_topics(
    strategies: Iterable[FuzzStrategy],
    attempts: Iterable[FuzzAttempt],
) -> tuple[FuzzStrategy, ...]:
    default_topic = _common_attempt_topic(attempts)
    filled: list[FuzzStrategy] = []
    for strategy in strategies:
        if _strategy_topic(strategy) or not default_topic:
            filled.append(strategy)
            continue
        metadata = dict(strategy.metadata)
        metadata["source"] = metadata.get("source", "evolved")
        metadata["math_topic"] = default_topic
        metadata["topic"] = default_topic
        filled.append(replace(strategy, math_topic=default_topic, metadata=metadata))
    return tuple(filled)


def _force_strategy_topic(
    strategies: Iterable[FuzzStrategy],
    topic: str,
) -> tuple[FuzzStrategy, ...]:
    normalized_topic = _normalize_topic(topic)
    forced: list[FuzzStrategy] = []
    for strategy in strategies:
        metadata = dict(strategy.metadata)
        metadata["math_topic"] = normalized_topic
        metadata["topic"] = normalized_topic
        metadata["source"] = metadata.get("source", "evolved")
        forced.append(replace(strategy, math_topic=normalized_topic, metadata=metadata))
    return tuple(forced)


def _common_attempt_topic(attempts: Iterable[FuzzAttempt]) -> str:
    topics = {
        topic
        for topic in (_topic_from_metadata(attempt.metadata) for attempt in attempts)
        if topic
    }
    return next(iter(topics)) if len(topics) == 1 else ""


def _strategy_query_tokens(
    *,
    objective: str,
    proof_text: str,
    metadata: dict[str, object],
) -> set[str]:
    pieces = [objective, proof_text]
    for key in ("problem", "grading_id", "llm_category", "category", "topic"):
        value = metadata.get(key)
        if value is not None:
            pieces.append(str(value))
    return set(_tokenize("\n".join(pieces)))


def _strategy_retrieval_score(
    strategy: FuzzStrategy,
    *,
    query_tokens: set[str],
    query_topic: str,
) -> float:
    metadata = strategy.metadata
    score = 0.0
    if query_topic and _strategy_topic(strategy) == query_topic:
        score += 6.0

    keyword_tokens = set()
    for keyword in _string_tuple(metadata.get("keywords", ())):
        keyword_tokens.update(_tokenize(keyword))
    precondition_tokens = set()
    for precondition in _string_tuple(metadata.get("preconditions", ())):
        precondition_tokens.update(_tokenize(precondition))
    strategy_tokens = set(_tokenize(f"{strategy.title} {strategy.guidance}"))

    score += 2.0 * len(query_tokens & keyword_tokens)
    score += 0.5 * len(query_tokens & precondition_tokens)
    score += 0.15 * len(query_tokens & strategy_tokens)

    attempts = strategy.successes + strategy.failures
    if attempts:
        score += (strategy.successes + 1.0) / (attempts + 2.0)
    return score


def _topic_from_metadata(metadata: dict[str, object]) -> str:
    for key in ("topic", "llm_category", "category"):
        topic = _normalize_topic(metadata.get(key))
        if topic:
            return topic
    original_data = metadata.get("original_data")
    if isinstance(original_data, dict):
        for key in ("llm_category", "category", "Category", "Problem Source"):
            topic = _normalize_topic(original_data.get(key))
            if topic:
                return topic
    return ""


def _normalize_topic(value: object) -> str:
    topic = str(value or "").strip().lower()
    if not topic:
        return ""
    topic = re.sub(r"[^a-z0-9]+", "_", topic).strip("_")
    aliases = {
        "number_theory": "number_theory",
        "nt": "number_theory",
        "combinatorics": "combinatorics",
        "combinatorial": "combinatorics",
        "geometry": "geometry",
        "algebra": "algebra",
        "analysis": "analysis",
    }
    return aliases.get(topic, topic)


def _tokenize(text: str) -> tuple[str, ...]:
    return tuple(token for token in re.findall(r"[a-zA-Z][a-zA-Z0-9_]{2,}", text.lower()))


def _topic_state_key(*, fuzzer_kind: str, math_topic: str) -> str:
    return f"{_normalize_fuzzer_kind(fuzzer_kind)}::{_normalize_topic(math_topic)}"


def _summarize_attempt(attempt: FuzzAttempt) -> dict[str, object]:
    if attempt.status == "failed":
        return {
            "attempt_id": attempt.attempt_id,
            "objective": attempt.objective,
            "math_topic": _topic_from_metadata(attempt.metadata),
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
        "math_topic": _topic_from_metadata(attempt.metadata),
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
    return _extract_problem_text_from_objective(objective)


def _extract_problem_text_from_objective(objective: str) -> str:
    marker = "Problem:\n"
    if marker not in objective:
        return ""
    problem = objective.split(marker, 1)[1].strip()
    for next_marker in ("\n\nRubric:", "\n\nOriginal proof:", "\n\nReference proof:"):
        if next_marker in problem:
            problem = problem.split(next_marker, 1)[0].strip()
            break
    return problem


def _format_previous_failed_attempt_guidance(
    attempts: tuple[FuzzAttempt, ...],
    *,
    max_chars: int,
) -> tuple[str, ...]:
    if max_chars <= 0:
        return ()
    guidance: list[str] = []
    remaining = max_chars
    for index, attempt in enumerate(attempts, start=1):
        if remaining <= 0:
            break
        item = truncate_text_head_tail(
            _summarize_failed_attempt_for_prompt(attempt, index=index),
            remaining,
        )
        guidance.append(item)
        remaining -= len(item)
    return tuple(guidance)


def _format_previous_successful_attempt_guidance(
    attempts: tuple[FuzzAttempt, ...],
    *,
    max_chars: int,
) -> tuple[str, ...]:
    if max_chars <= 0:
        return ()
    guidance: list[str] = []
    remaining = max_chars
    for index, attempt in enumerate(attempts, start=1):
        if remaining <= 0:
            break
        item = truncate_text_head_tail(
            _summarize_successful_attempt_for_prompt(attempt, index=index),
            remaining,
        )
        guidance.append(item)
        remaining -= len(item)
    return tuple(guidance)


def _summarize_failed_attempt_for_prompt(attempt: FuzzAttempt, *, index: int) -> str:
    target = "preserve correctness" if attempt.maintain_correctness else "make a false proof look correct"
    mutations = _mutation_summaries_for_prompt(attempt.mutation_instructions, limit=3)

    judge_parts = []
    target_judge_results = attempt.metadata.get(
        "target_error_reports",
        attempt.metadata.get("target_judge_results"),
    )
    if isinstance(target_judge_results, list) and target_judge_results:
        inventory_reports = [
            _dict_value(result)
            for result in target_judge_results
            if _dict_value(result).get("response_kind") == "error_inventory"
        ]
        if inventory_reports:
            inventories = [result.get("detected_errors", ()) for result in inventory_reports]
            counts = [len(value) if isinstance(value, list) else 0 for value in inventories]
            judge_parts.append(
                "blind error-finder report counts: "
                + ", ".join(str(count) for count in counts)
            )
        else:
            verdicts = [
                str(_dict_value(result).get("verdict", "")).strip()
                for result in target_judge_results
            ]
            verdicts_text = ", ".join(verdict for verdict in verdicts if verdict)
            if verdicts_text:
                judge_parts.append(f"target judge verdicts: {verdicts_text}")
    elif attempt.judge_result is not None:
        judge_parts.append(f"target judge verdict: {attempt.judge_result.verdict}")
    if attempt.judge_result is not None and attempt.judge_result.detected_flaw:
        label = (
            "blind error-finder reported"
            if attempt.judge_result.response_kind == "error_inventory"
            else "target judge detected flaw"
        )
        judge_parts.append(f"{label}: {attempt.judge_result.detected_flaw}")

    mutation_check = attempt.mutation_check_result
    if mutation_check is not None:
        judge_parts.append(f"mutation-check verdict: {mutation_check.verdict}")
        if mutation_check.detected_flaw:
            judge_parts.append(f"mutation-check flaw: {mutation_check.detected_flaw}")

    reveal_check = attempt.metadata.get(
        "introduced_error_match",
        attempt.metadata.get("judge_error_detection_check"),
    )
    if isinstance(reveal_check, dict):
        if reveal_check.get(
            "introduced_error_found",
            reveal_check.get("any_judge_reported_correct_error"),
        ):
            judge_parts.append("failure reason: a blind error-finder report identified the planted error")
        elif reveal_check.get("check_failed"):
            judge_parts.append("failure reason: introduced-error matcher failed")
    if not judge_parts:
        judge_parts.append("failure reason: did not satisfy the fuzzing success criteria")

    strategy_ids = ", ".join(attempt.strategy_ids)
    strategy_part = f"; strategies: {strategy_ids}" if strategy_ids else ""
    return (
        f"Attempt {index} ({attempt.attempt_id}): target={target}{strategy_part}. "
        f"Tried mutation(s): {mutations}. "
        f"Outcome: {'; '.join(judge_parts)}. "
        "Prefer a materially different mutation route unless there is a clear reason to revisit it."
    )


def _summarize_successful_attempt_for_prompt(attempt: FuzzAttempt, *, index: int) -> str:
    target = "preserved correctness" if attempt.maintain_correctness else "made a false proof look correct"
    mutations = _mutation_summaries_for_prompt(attempt.mutation_instructions, limit=5)
    rationale = truncate_text_head_tail(attempt.mutation_instructions.rationale, 700).strip()
    if not rationale:
        rationale = "no rationale recorded"
    trace_name = str(attempt.metadata.get("trace_dir_name") or attempt.metadata.get("trace_dir") or "")
    trace_part = f"; trace: {trace_name}" if trace_name else ""
    strategy_ids = ", ".join(attempt.strategy_ids)
    strategy_part = f"; strategies: {strategy_ids}" if strategy_ids else ""
    return (
        f"AVOID repeating successful attempt {index} ({attempt.attempt_id}{trace_part}; "
        f"target={target}{strategy_part}). "
        f"Prior mutation mechanism/rationale: {rationale}. "
        f"Prior mutation targets/summaries: {mutations}. "
        "Choose a different proof step, mathematical dependency, or error mechanism; do not merely reword or "
        "minorly vary this attack."
    )


def _mutation_summaries_for_prompt(instructions: FuzzerMutationInstructions, *, limit: int) -> str:
    mutations = "; ".join(
        truncate_text_head_tail(
            f"{mutation.kind} {mutation.target}: {mutation.summary or mutation.new_text}",
            320,
        )
        for mutation in instructions.mutations[:limit]
    )
    if len(instructions.mutations) > limit:
        mutations += f"; ... ({len(instructions.mutations)} mutations total)"
    return mutations or "no concrete mutation was recorded"


def _attempt_novelty_payload(attempt: FuzzAttempt) -> dict[str, object]:
    return {
        "attempt_id": attempt.attempt_id,
        "trace_dir_name": attempt.metadata.get("trace_dir_name", ""),
        "strategy_ids": list(attempt.strategy_ids),
        "rationale": attempt.mutation_instructions.rationale,
        "mutations": [
            {
                "kind": mutation.kind,
                "target": mutation.target,
                "summary": mutation.summary,
                "affected_blocks": list(mutation.affected_blocks),
                "propagate_downstream": mutation.propagate_downstream,
            }
            for mutation in attempt.mutation_instructions.mutations
        ],
    }


def _format_duplicate_success_retry_guidance(novelty_check: dict[str, object]) -> str:
    matching = ", ".join(str(item) for item in novelty_check.get("matching_attempt_ids", []) or [])
    matching_part = f" Matching prior attempts: {matching}." if matching else ""
    retry = str(novelty_check.get("suggested_retry_guidance", "")).strip()
    rationale = str(novelty_check.get("rationale", "")).strip()
    detail = retry or rationale or "Choose a different proof step and a different mathematical error mechanism."
    return (
        "The previous proposed mutation was rejected as too similar to an earlier successful mutation on this "
        f"same proof (novelty={novelty_check.get('novelty', 'unknown')}).{matching_part} "
        f"Retry guidance: {detail}"
    )


def _successful_mutation_novelty_rejected(result: dict[str, object], *, policy: str) -> bool:
    if bool(result.get("check_failed")):
        return False
    novelty = str(result.get("novelty", "")).strip().lower()
    if policy == "duplicate":
        return novelty == "duplicate"
    return novelty in {"duplicate", "variant"}


def _same_proof_attempt(
    attempt: FuzzAttempt,
    metadata: dict[str, object],
    original_proof_text: str,
) -> bool:
    expected_identity = _proof_identity(metadata, original_proof_text)
    attempt_identity = str(attempt.metadata.get("proof_identity", "")).strip()
    if attempt_identity and attempt_identity == expected_identity:
        return True

    expected_dataset = str(metadata.get("dataset", "")).strip()
    attempt_dataset = str(attempt.metadata.get("dataset", "")).strip()
    if expected_dataset and expected_dataset == attempt_dataset:
        for key in ("example_id", "example_path", "problem_id"):
            expected = str(metadata.get(key, "")).strip()
            actual = str(attempt.metadata.get(key, "")).strip()
            if expected and actual and expected == actual:
                return True

    expected_hash = str(metadata.get("original_proof_sha256") or _sha256_text(original_proof_text))
    attempt_hash = str(attempt.metadata.get("original_proof_sha256", "")).strip()
    if attempt_hash and attempt_hash == expected_hash:
        return True
    if attempt.original_proof_text and _sha256_text(attempt.original_proof_text) == expected_hash:
        return True
    return False


def _proof_identity(metadata: dict[str, object], original_proof_text: str) -> str:
    dataset = str(metadata.get("dataset", "")).strip()
    for key in ("example_id", "example_path", "problem_id"):
        value = str(metadata.get(key, "")).strip()
        if dataset and value:
            return f"{dataset}:{key}:{value}"
    return f"proof_sha256:{_sha256_text(original_proof_text)}"


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _trace_directory_name(metadata: dict[str, object]) -> str:
    sample_index = metadata.get("sample_index")
    if isinstance(sample_index, int) or (isinstance(sample_index, str) and sample_index.isdigit()):
        return str(sample_index)
    example_id = str(metadata.get("example_id", "")).strip()
    attempt_index = metadata.get("example_attempt_index", "")
    if example_id:
        suffix = f"_{attempt_index}" if attempt_index != "" else ""
        return f"{_safe_filename(example_id)}{suffix}"
    return _new_id("attempt_trace")


def _unique_trace_dir(root: Path, name: str) -> Path:
    root.mkdir(parents=True, exist_ok=True)
    base = _safe_filename(name)
    candidate = root / base
    if not candidate.exists():
        return candidate
    index = 1
    while True:
        candidate = root / f"{base}_{index}"
        if not candidate.exists():
            return candidate
        index += 1


def _safe_filename(value: object) -> str:
    slug = re.sub(r"[^A-Za-z0-9_.-]+", "_", str(value).strip())
    return slug.strip("_") or "trace"


def _write_json_file(path: Path, data: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _write_text_file(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text if text.endswith("\n") else text + "\n", encoding="utf-8")


def _format_mutations_text(instructions: FuzzerMutationInstructions) -> str:
    lines = [
        f"maintain_correctness: {instructions.maintain_correctness}",
        f"rationale: {instructions.rationale}",
        "",
        "mutations:",
    ]
    for index, mutation in enumerate(instructions.mutations, start=1):
        lines.extend(
            [
                f"{index}. kind: {mutation.kind}",
                f"   target: {mutation.target}",
                f"   summary: {mutation.summary}",
                f"   affected_blocks: {list(mutation.affected_blocks)}",
                f"   propagate_downstream: {mutation.propagate_downstream}",
                "   new_text:",
                "   " + mutation.new_text.replace("\n", "\n   "),
                "",
            ]
        )
    return "\n".join(lines)


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


def usage_limit_reached(value: object) -> bool:
    """Return true when a failed attempt/exception is caused by account usage limits."""

    if isinstance(value, FuzzAttempt):
        return (
            _text_mentions_usage_limit(value.error)
            or _text_mentions_usage_limit(value.failure_stage)
            or _text_mentions_usage_limit(json.dumps(value.metadata, sort_keys=True, default=str))
        )
    if isinstance(value, LLMStageError):
        return usage_limit_reached(value.cause) or _text_mentions_usage_limit(repr(value))
    if isinstance(value, BaseException):
        return _text_mentions_usage_limit(repr(value))
    return _text_mentions_usage_limit(str(value))


def _text_mentions_usage_limit(text: str) -> bool:
    lowered = text.lower()
    return "usage limit" in lowered or "purchase more credits" in lowered


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
    return _load_llm_json_object(text)


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


def _error_inventory(value: object) -> tuple[dict[str, object], ...]:
    if not isinstance(value, (list, tuple)):
        return ()
    errors: list[dict[str, object]] = []
    for item in value:
        if not isinstance(item, dict):
            continue
        errors.append(
            {
                "location": str(item.get("location", "")),
                "root_cause": str(item.get("root_cause", "")),
                "description": str(item.get("description", "")),
                "consequence": str(item.get("consequence", "")),
                "severity": str(item.get("severity", "")),
                "confidence": float(item.get("confidence", 0.0) or 0.0),
            }
        )
    return tuple(errors)


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
