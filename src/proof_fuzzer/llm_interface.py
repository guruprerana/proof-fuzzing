"""Structured LLM interface for proof fuzzing.

This module does not bind to a specific model provider. Callers can pass any
object with a ``complete(prompt: str) -> str`` method, or use the prompt and
parser functions directly with their own LLM stack.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime, timezone
import json
from pathlib import Path
import re
from typing import Protocol

from src.semi_formalization.mutation import (
    GLOBAL_CONTEXT,
    LLMBlockUpdatePrompt,
    MutationImpactPlan,
    MutationPlanner,
    ProgressiveMutationSession,
    ProofMutation,
)
from src.semi_formalization.parser import ParseError, parse_text
from src.semi_formalization.proof_graph import ProofGraph


PROPAGATION_MODES = {"conditional", "naive"}
NO_CHANGE_NEEDED = "NO CHANGE NEEDED"


class LLMClient(Protocol):
    """Minimal protocol for model clients used by the proof fuzzer."""

    def complete(self, prompt: str) -> str:
        """Return a text completion for ``prompt``."""


@dataclass(frozen=True)
class LLMCompletionTrace:
    """Text, reasoning, and raw provider result for one LLM completion."""

    response: str
    reasoning: str = ""
    raw_result: object | None = None


class LLMTraceLogger:
    """Writes prompts, reasoning tokens, and responses for proof-fuzzer calls."""

    def __init__(self, log_dir: str | Path):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self._counter = 0

    def log_call(
        self,
        *,
        call_kind: str,
        prompt: str,
        response: str = "",
        reasoning: str = "",
        metadata: dict[str, object] | None = None,
    ) -> Path:
        self._counter += 1
        call_dir = self._next_call_dir(call_kind)
        call_dir.mkdir(parents=True, exist_ok=False)

        (call_dir / "prompt.txt").write_text(prompt, encoding="utf-8")
        (call_dir / "reasoning_tokens.txt").write_text(reasoning, encoding="utf-8")
        (call_dir / "response.txt").write_text(response, encoding="utf-8")

        meta = {
            "call_kind": call_kind,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "prompt_file": "prompt.txt",
            "reasoning_tokens_file": "reasoning_tokens.txt",
            "response_file": "response.txt",
        }
        if metadata:
            meta.update(metadata)
        (call_dir / "metadata.json").write_text(json.dumps(meta, indent=2, sort_keys=True), encoding="utf-8")
        return call_dir

    def _next_call_dir(self, call_kind: str) -> Path:
        slug = _slugify_call_kind(call_kind)
        while True:
            candidate = self.log_dir / f"{self._counter:06d}_{slug}"
            if not candidate.exists():
                return candidate
            self._counter += 1


@dataclass(frozen=True)
class FuzzerMutationInstructions:
    """Structured mutation instructions returned by a proof-fuzzer LLM."""

    maintain_correctness: bool
    mutations: tuple[ProofMutation, ...]
    rationale: str = ""
    raw_response: str = ""

    def to_dict(self) -> dict[str, object]:
        return {
            "maintain_correctness": self.maintain_correctness,
            "rationale": self.rationale,
            "mutations": [mutation.to_dict() for mutation in self.mutations],
            "raw_response": self.raw_response,
        }


@dataclass(frozen=True)
class BlockUpdateResult:
    """Parsed response from an LLM asked to update one proof block."""

    block_id: str
    changed: bool
    revised_text: str = ""
    raw_response: str = ""

    def to_dict(self) -> dict[str, object]:
        return {
            "block_id": self.block_id,
            "changed": self.changed,
            "revised_text": self.revised_text,
            "raw_response": self.raw_response,
        }


@dataclass(frozen=True)
class MutationValidationIssue:
    """Structural issue in parsed mutation instructions."""

    mutation_index: int
    message: str
    field: str = ""
    severity: str = "error"

    def to_dict(self) -> dict[str, object]:
        return {
            "mutation_index": self.mutation_index,
            "field": self.field,
            "severity": self.severity,
            "message": self.message,
        }


@dataclass(frozen=True)
class SuccessorUpdateWorkflow:
    """Successor-update state after mutation instructions are parsed."""

    mode: str
    maintain_correctness: bool
    static_plan: MutationImpactPlan | None = None
    progressive_session: ProgressiveMutationSession | None = None

    @property
    def active(self) -> bool:
        if not self.maintain_correctness:
            return False
        if self.mode == "naive":
            return self.static_plan is not None and bool(self.static_plan.affected_blocks)
        if self.mode == "conditional":
            return self.progressive_session is not None and not self.progressive_session.done
        return False


@dataclass(frozen=True)
class NaturalLanguageProofSegment:
    """A targetable natural-language proof segment."""

    segment_id: str
    text: str

    def to_dict(self) -> dict[str, object]:
        return {
            "segment_id": self.segment_id,
            "text": self.text,
        }


class ProofFuzzerLLMInterfaceBase(ABC):
    """Shared LLM-facing interface for proof fuzzing strategies."""

    def __init__(
        self,
        llm: LLMClient | None = None,
        *,
        log_dir: str | Path | None = None,
        trace_logger: LLMTraceLogger | None = None,
    ):
        self.llm = llm
        self.trace_logger = trace_logger or (LLMTraceLogger(log_dir) if log_dir is not None else None)

    @abstractmethod
    def mutation_instruction_prompt(
        self,
        *,
        objective: str = "",
        strategy_guidance: tuple[str, ...] = (),
        prior_attempt_guidance: tuple[str, ...] = (),
    ) -> str:
        """Build a prompt asking an LLM for structured mutation instructions."""

    @abstractmethod
    def correctness_preserving_mutation_instruction_prompt(
        self,
        *,
        objective: str = "",
        strategy_guidance: tuple[str, ...] = (),
        prior_attempt_guidance: tuple[str, ...] = (),
    ) -> str:
        """Build a mutation prompt where the proof must remain correct."""

    @abstractmethod
    def false_proof_mutation_instruction_prompt(
        self,
        *,
        objective: str = "",
        strategy_guidance: tuple[str, ...] = (),
        prior_attempt_guidance: tuple[str, ...] = (),
    ) -> str:
        """Build a mutation prompt where the proof should become false."""

    @abstractmethod
    def validate_mutation_instructions(
        self,
        instructions: FuzzerMutationInstructions,
    ) -> tuple[MutationValidationIssue, ...]:
        """Return structural validation issues for parsed mutations."""

    def request_mutation_instructions(self, *, objective: str = "") -> FuzzerMutationInstructions:
        """Query the configured LLM and parse mutation instructions."""

        if self.llm is None:
            raise ValueError("No LLM client was provided.")
        response = self._complete_with_logging(
            self.mutation_instruction_prompt(objective=objective),
            call_kind="mutation_instructions_choose_correctness",
        )
        instructions = parse_mutation_instructions(response)
        self._raise_for_invalid_mutation_instructions(instructions)
        return instructions

    def request_correctness_preserving_mutation_instructions(
        self,
        *,
        objective: str = "",
    ) -> FuzzerMutationInstructions:
        """Query the LLM for mutations after deciding the proof must stay true."""

        if self.llm is None:
            raise ValueError("No LLM client was provided.")

        response = self._complete_with_logging(
            self.correctness_preserving_mutation_instruction_prompt(objective=objective),
            call_kind="mutation_instructions_correctness_preserving",
        )
        instructions = parse_mutation_instructions(response)
        _validate_fixed_correctness(instructions, expected=True)
        self._raise_for_invalid_mutation_instructions(instructions)
        return instructions

    def request_false_proof_mutation_instructions(
        self,
        *,
        objective: str = "",
    ) -> FuzzerMutationInstructions:
        """Query the LLM for mutations after deciding the proof should be false."""

        if self.llm is None:
            raise ValueError("No LLM client was provided.")

        response = self._complete_with_logging(
            self.false_proof_mutation_instruction_prompt(objective=objective),
            call_kind="mutation_instructions_false_proof",
        )
        instructions = parse_mutation_instructions(response)
        _validate_fixed_correctness(instructions, expected=False)
        self._raise_for_invalid_mutation_instructions(instructions)
        return instructions

    def _complete_with_logging(
        self,
        prompt: str,
        *,
        call_kind: str,
        metadata: dict[str, object] | None = None,
    ) -> str:
        if self.llm is None:
            raise ValueError("No LLM client was provided.")

        try:
            result = _complete_llm(self.llm, prompt)
        except Exception as exc:
            if self.trace_logger is not None:
                failure_metadata = dict(metadata or {})
                failure_metadata["error"] = repr(exc)
                self.trace_logger.log_call(
                    call_kind=call_kind,
                    prompt=prompt,
                    metadata=failure_metadata,
                )
            raise

        if self.trace_logger is not None:
            self.trace_logger.log_call(
                call_kind=call_kind,
                prompt=prompt,
                response=result.response,
                reasoning=result.reasoning,
                metadata=metadata,
            )
        return result.response

    def _raise_for_invalid_mutation_instructions(self, instructions: FuzzerMutationInstructions) -> None:
        issues = self.validate_mutation_instructions(instructions)
        errors = [issue for issue in issues if issue.severity == "error"]
        if not errors:
            return

        details = "; ".join(
            f"mutation {issue.mutation_index} {issue.field or 'mutation'}: {issue.message}"
            for issue in errors
        )
        raise ValueError(f"Mutation instructions failed validation: {details}")


class SemiFormalProofFuzzerLLMInterface(ProofFuzzerLLMInterfaceBase):
    """Coordinates semi-formal proof-fuzzer prompts with graph update planning."""

    def __init__(
        self,
        graph: ProofGraph,
        llm: LLMClient | None = None,
        *,
        propagation_mode: str = "conditional",
        log_dir: str | Path | None = None,
        trace_logger: LLMTraceLogger | None = None,
    ):
        if propagation_mode not in PROPAGATION_MODES:
            allowed = ", ".join(sorted(PROPAGATION_MODES))
            raise ValueError(f"Unknown propagation mode {propagation_mode!r}; expected one of: {allowed}")

        super().__init__(llm, log_dir=log_dir, trace_logger=trace_logger)
        self.graph = graph
        self.propagation_mode = propagation_mode
        self.mutation_planner = MutationPlanner(graph)

    def mutation_instruction_prompt(
        self,
        *,
        objective: str = "",
        strategy_guidance: tuple[str, ...] = (),
        prior_attempt_guidance: tuple[str, ...] = (),
    ) -> str:
        """Build the prompt asking an LLM for structured mutation instructions."""

        objective_text = objective.strip() or "Find an interesting proof mutation."
        block_ids = ", ".join(self.graph.nodes)
        proof_text = self.graph.proof.raw_text or str(self.graph.proof.to_dict(include_raw=False))

        return f"""You are acting as a proof fuzzer for a semi-formalized mathematical proof.

Objective:
{objective_text}

Choose whether the resulting proof should remain correct.
- If maintain_correctness is true, later steps will update downstream blocks.
- If maintain_correctness is false, decide whether to propagate local changes to downstream blocks based on what makes the false proof most coherent and judge-convincing while preserving the underlying flaw.

Judge-fuzzing goal:
- For an incorrect-proof mutation, try to make the proof plausibly trick an LLM judge into thinking it is correct.
- For a correctness-preserving mutation, try to make the proof plausibly trick an LLM judge into thinking it is incorrect.

Mutation quality:
{_mutation_quality_guidance(maintain_correctness=None)}
{_format_strategy_guidance(strategy_guidance)}
{_format_prior_attempt_guidance(prior_attempt_guidance)}

Available block ids:
{block_ids}

Current proof:
```text
{proof_text}
```

Return exactly one JSON object. Do not include prose outside the JSON.
Schema:
```json
{{
  "maintain_correctness": true,
  "rationale": "short reason for the chosen fuzzing direction",
  "mutations": [
    {{
      "kind": "modify | remove | add | global_context",
      "target": "block id, lemma id, exported statement id, or global_context",
      "summary": "one elementary mutation",
      "new_text": "replacement or inserted parseable text, empty for remove when appropriate",
      "affected_blocks": ["optional existing blocks that should be reconsidered, especially for add"],
      "propagate_downstream": true
    }}
  ]
}}
```

Each item in mutations must be one elementary mutation. Use multiple items for compound edits.
"""

    def correctness_preserving_mutation_instruction_prompt(
        self,
        *,
        objective: str = "",
        strategy_guidance: tuple[str, ...] = (),
        prior_attempt_guidance: tuple[str, ...] = (),
    ) -> str:
        """Build a mutation prompt where the proof must remain correct."""

        objective_text = objective.strip() or "Find an interesting correctness-preserving proof mutation."
        return self._fixed_correctness_mutation_instruction_prompt(
            objective_text=objective_text,
            maintain_correctness=True,
            strategy_guidance=strategy_guidance,
            prior_attempt_guidance=prior_attempt_guidance,
        )

    def false_proof_mutation_instruction_prompt(
        self,
        *,
        objective: str = "",
        strategy_guidance: tuple[str, ...] = (),
        prior_attempt_guidance: tuple[str, ...] = (),
    ) -> str:
        """Build a mutation prompt where the proof should become false."""

        objective_text = objective.strip() or "Find an interesting mutation that makes the proof false."
        return self._fixed_correctness_mutation_instruction_prompt(
            objective_text=objective_text,
            maintain_correctness=False,
            strategy_guidance=strategy_guidance,
            prior_attempt_guidance=prior_attempt_guidance,
        )

    def request_mutation_instructions(self, *, objective: str = "") -> FuzzerMutationInstructions:
        """Query the configured LLM and parse mutation instructions."""

        if self.llm is None:
            raise ValueError("No LLM client was provided.")
        response = self._complete_with_logging(
            self.mutation_instruction_prompt(objective=objective),
            call_kind="mutation_instructions_choose_correctness",
        )
        instructions = parse_mutation_instructions(response)
        self._raise_for_invalid_mutation_instructions(instructions)
        return instructions

    def request_correctness_preserving_mutation_instructions(
        self,
        *,
        objective: str = "",
    ) -> FuzzerMutationInstructions:
        """Query the LLM for mutations after deciding the proof must stay true."""

        if self.llm is None:
            raise ValueError("No LLM client was provided.")

        response = self._complete_with_logging(
            self.correctness_preserving_mutation_instruction_prompt(objective=objective),
            call_kind="mutation_instructions_correctness_preserving",
        )
        instructions = parse_mutation_instructions(response)
        _validate_fixed_correctness(instructions, expected=True)
        self._raise_for_invalid_mutation_instructions(instructions)
        return instructions

    def request_false_proof_mutation_instructions(
        self,
        *,
        objective: str = "",
    ) -> FuzzerMutationInstructions:
        """Query the LLM for mutations after deciding the proof should be false."""

        if self.llm is None:
            raise ValueError("No LLM client was provided.")

        response = self._complete_with_logging(
            self.false_proof_mutation_instruction_prompt(objective=objective),
            call_kind="mutation_instructions_false_proof",
        )
        instructions = parse_mutation_instructions(response)
        _validate_fixed_correctness(instructions, expected=False)
        self._raise_for_invalid_mutation_instructions(instructions)
        return instructions

    def validate_mutation_instructions(
        self,
        instructions: FuzzerMutationInstructions,
    ) -> tuple[MutationValidationIssue, ...]:
        """Return graph-aware structural validation issues for mutations."""

        issues: list[MutationValidationIssue] = []
        for index, mutation in enumerate(instructions.mutations):
            issues.extend(self._validate_mutation(index, mutation))
        return tuple(issues)

    def build_successor_update_workflow(
        self,
        instructions: FuzzerMutationInstructions,
        *,
        propagation_mode: str | None = None,
        include_direct_changes: bool = False,
    ) -> SuccessorUpdateWorkflow:
        """Create a successor-update workflow for parsed mutation instructions."""

        mode = propagation_mode or self.propagation_mode
        if mode not in PROPAGATION_MODES:
            allowed = ", ".join(sorted(PROPAGATION_MODES))
            raise ValueError(f"Unknown propagation mode {mode!r}; expected one of: {allowed}")

        if not instructions.maintain_correctness:
            return SuccessorUpdateWorkflow(mode=mode, maintain_correctness=False)

        if mode == "naive":
            plan = self.mutation_planner.plan_mutations(
                instructions.mutations,
                include_direct_changes=include_direct_changes,
            )
            return SuccessorUpdateWorkflow(mode=mode, maintain_correctness=True, static_plan=plan)

        session = self.mutation_planner.start_progressive_mutations(
            instructions.mutations,
            include_direct_changes=include_direct_changes,
        )
        return SuccessorUpdateWorkflow(mode=mode, maintain_correctness=True, progressive_session=session)

    def current_update_prompts(
        self,
        workflow: SuccessorUpdateWorkflow,
    ) -> tuple[LLMBlockUpdatePrompt, ...]:
        """Return prompts for the current workflow state."""

        if not workflow.maintain_correctness:
            return ()
        if workflow.mode == "naive":
            if workflow.static_plan is None:
                return ()
            return self.mutation_planner.mutation_update_prompts(workflow.static_plan)
        if workflow.progressive_session is None:
            return ()
        return self.mutation_planner.progressive_update_prompts(workflow.progressive_session)

    def advance_conditional_workflow(
        self,
        workflow: SuccessorUpdateWorkflow,
        results: tuple[BlockUpdateResult, ...] | list[BlockUpdateResult],
    ) -> SuccessorUpdateWorkflow:
        """Advance a conditional workflow using parsed LLM update results."""

        if workflow.mode != "conditional":
            raise ValueError("Only conditional workflows can be advanced.")
        if workflow.progressive_session is None:
            return workflow

        changed = [result.block_id for result in results if result.changed]
        session = self.mutation_planner.advance_progressive_session(workflow.progressive_session, changed)
        return SuccessorUpdateWorkflow(
            mode=workflow.mode,
            maintain_correctness=workflow.maintain_correctness,
            progressive_session=session,
        )

    def query_current_updates(
        self,
        workflow: SuccessorUpdateWorkflow,
    ) -> tuple[BlockUpdateResult, ...]:
        """Query the LLM for the current update prompts and parse responses."""

        if self.llm is None:
            raise ValueError("No LLM client was provided.")

        results: list[BlockUpdateResult] = []
        for prompt in self.current_update_prompts(workflow):
            response = self._complete_with_logging(
                prompt.prompt,
                call_kind=f"successor_update_{prompt.block_id}",
                metadata={
                    "block_id": prompt.block_id,
                    "frontier_index": prompt.frontier_index,
                    "reasons": list(prompt.reasons),
                },
            )
            results.append(parse_block_update_response(prompt.block_id, response))
        return tuple(results)

    def _complete_with_logging(
        self,
        prompt: str,
        *,
        call_kind: str,
        metadata: dict[str, object] | None = None,
    ) -> str:
        if self.llm is None:
            raise ValueError("No LLM client was provided.")

        try:
            result = _complete_llm(self.llm, prompt)
        except Exception as exc:
            if self.trace_logger is not None:
                failure_metadata = dict(metadata or {})
                failure_metadata["error"] = repr(exc)
                self.trace_logger.log_call(
                    call_kind=call_kind,
                    prompt=prompt,
                    metadata=failure_metadata,
                )
            raise

        if self.trace_logger is not None:
            self.trace_logger.log_call(
                call_kind=call_kind,
                prompt=prompt,
                response=result.response,
                reasoning=result.reasoning,
                metadata=metadata,
            )
        return result.response

    def _raise_for_invalid_mutation_instructions(self, instructions: FuzzerMutationInstructions) -> None:
        issues = self.validate_mutation_instructions(instructions)
        errors = [issue for issue in issues if issue.severity == "error"]
        if not errors:
            return

        details = "; ".join(
            f"mutation {issue.mutation_index} {issue.field or 'mutation'}: {issue.message}"
            for issue in errors
        )
        raise ValueError(f"Mutation instructions failed validation: {details}")

    def _validate_mutation(self, index: int, mutation: ProofMutation) -> tuple[MutationValidationIssue, ...]:
        issues: list[MutationValidationIssue] = []

        if not mutation.target:
            return (MutationValidationIssue(index, "Mutation target is required.", field="target"),)

        canonical_target = self.graph.canonical_block_id(mutation.target)
        if mutation.kind in {"modify", "remove"}:
            try:
                self.graph.normalize_block_ids([canonical_target])
            except KeyError:
                issues.append(
                    MutationValidationIssue(
                        index,
                        f"Unknown target block {mutation.target!r}.",
                        field="target",
                    )
                )

        if mutation.kind == "global_context" and canonical_target != GLOBAL_CONTEXT:
            issues.append(
                MutationValidationIssue(
                    index,
                    "Global-context mutations must target global_context.",
                    field="target",
                )
            )

        if mutation.kind in {"modify", "add", "global_context"}:
            if not mutation.new_text.strip():
                issues.append(
                    MutationValidationIssue(
                        index,
                        f"{mutation.kind} mutations must include non-empty new_text.",
                        field="new_text",
                    )
                )
            else:
                issues.extend(self._validate_mutation_text(index, mutation, canonical_target))

        for affected_block in mutation.affected_blocks:
            try:
                self.graph.normalize_block_ids([affected_block])
            except KeyError:
                issues.append(
                    MutationValidationIssue(
                        index,
                        f"Unknown affected block {affected_block!r}.",
                        field="affected_blocks",
                    )
                )

        return tuple(issues)

    def _validate_mutation_text(
        self,
        index: int,
        mutation: ProofMutation,
        canonical_target: str,
    ) -> tuple[MutationValidationIssue, ...]:
        issues: list[MutationValidationIssue] = []

        try:
            parsed = parse_text(mutation.new_text)
        except (ParseError, ValueError) as exc:
            return (
                MutationValidationIssue(
                    index,
                    f"new_text is not parseable semi-formal text: {exc}",
                    field="new_text",
                ),
            )

        if mutation.kind == "global_context":
            if parsed.claims or parsed.lemmas:
                issues.append(
                    MutationValidationIssue(
                        index,
                        "Global-context replacement text must contain only a global context section.",
                        field="new_text",
                    )
                )
            return tuple(issues)

        parsed_graph = ProofGraph(parsed)
        parsed_ids = set(parsed_graph.nodes)
        if canonical_target in self.graph.node_kinds and canonical_target not in parsed_ids:
            issues.append(
                MutationValidationIssue(
                    index,
                    f"new_text does not define the target block {canonical_target!r}.",
                    field="new_text",
                )
            )

        if mutation.kind == "add" and canonical_target not in parsed_ids:
            issues.append(
                MutationValidationIssue(
                    index,
                    f"new_text for add does not define the requested target {canonical_target!r}.",
                    field="new_text",
                )
            )

        for claim in parsed.all_claims():
            for ref in claim.allowed_references:
                if ref.ref in parsed_ids:
                    continue
                try:
                    self.graph.normalize_block_ids([ref.ref])
                except KeyError:
                    issues.append(
                        MutationValidationIssue(
                            index,
                            f"{claim.claim_id}: Unknown reference {ref.ref!r}.",
                            field="new_text",
                        )
                    )

        return tuple(issues)

    def _fixed_correctness_mutation_instruction_prompt(
        self,
        *,
        objective_text: str,
        maintain_correctness: bool,
        strategy_guidance: tuple[str, ...] = (),
        prior_attempt_guidance: tuple[str, ...] = (),
    ) -> str:
        block_ids = ", ".join(self.graph.nodes)
        proof_text = self.graph.proof.raw_text or str(self.graph.proof.to_dict(include_raw=False))
        correctness_json = "true" if maintain_correctness else "false"
        propagation_json = "true" if maintain_correctness else "true | false"
        direction = (
            "The resulting proof must remain mathematically correct. Choose mutations whose downstream "
            "consequences can be repaired by later update steps."
            if maintain_correctness
            else "The resulting proof should become mathematically false or invalid for fuzzing. Prefer a "
            "subtle mutation, and decide whether downstream propagation will make the false proof more coherent."
        )
        judge_goal = (
            "Generate a correctness-preserving mutation that could plausibly trick an LLM judge into "
            "thinking the proof is incorrect."
            if maintain_correctness
            else "Generate an incorrect-proof mutation that could plausibly trick an LLM judge into "
            "thinking the proof is correct."
        )
        propagation_guidance = (
            "Set propagate_downstream to true for mutations whose dependent blocks should be repaired."
            if maintain_correctness
            else "For false-proof mutations, choose propagate_downstream true or false based on which makes the "
            "resulting proof more convincing: propagate notation and downstream inferences when consistency helps, "
            "but preserve the core mathematical flaw."
        )

        return f"""You are acting as a proof fuzzer for a semi-formalized mathematical proof.

Objective:
{objective_text}

Correctness target:
{direction}

Judge-fuzzing goal:
{judge_goal}

The JSON field maintain_correctness must be exactly {correctness_json}.
{propagation_guidance}

Mutation quality:
{_mutation_quality_guidance(maintain_correctness=maintain_correctness)}
{_format_strategy_guidance(strategy_guidance)}
{_format_prior_attempt_guidance(prior_attempt_guidance)}

Available block ids:
{block_ids}

Current proof:
```text
{proof_text}
```

Return exactly one JSON object. Do not include prose outside the JSON.
Schema:
```json
{{
  "maintain_correctness": {correctness_json},
  "rationale": "short reason for the chosen fuzzing direction",
  "mutations": [
    {{
      "kind": "modify | remove | add | global_context",
      "target": "block id, lemma id, exported statement id, or global_context",
      "summary": "one elementary mutation",
      "new_text": "replacement or inserted parseable text, empty for remove when appropriate",
      "affected_blocks": ["optional existing blocks that should be reconsidered, especially for add"],
      "propagate_downstream": {propagation_json}
    }}
  ]
}}
```

Each item in mutations must be one elementary mutation. Use multiple items for compound edits.
"""


class NaturalLanguageProofFuzzerLLMInterface(ProofFuzzerLLMInterfaceBase):
    """Directly fuzzes a natural-language proof without semi-formalization."""

    def __init__(
        self,
        proof_text: str,
        llm: LLMClient | None = None,
        *,
        log_dir: str | Path | None = None,
        trace_logger: LLMTraceLogger | None = None,
    ):
        super().__init__(llm, log_dir=log_dir, trace_logger=trace_logger)
        self.proof_text = proof_text
        self.segments = split_natural_language_proof(proof_text)

    def mutation_instruction_prompt(
        self,
        *,
        objective: str = "",
        strategy_guidance: tuple[str, ...] = (),
        prior_attempt_guidance: tuple[str, ...] = (),
    ) -> str:
        """Build the prompt asking an LLM for direct natural-language mutations."""

        objective_text = objective.strip() or "Find an interesting direct natural-language proof mutation."
        return self._mutation_instruction_prompt(
            objective_text=objective_text,
            maintain_correctness=None,
            strategy_guidance=strategy_guidance,
            prior_attempt_guidance=prior_attempt_guidance,
        )

    def correctness_preserving_mutation_instruction_prompt(
        self,
        *,
        objective: str = "",
        strategy_guidance: tuple[str, ...] = (),
        prior_attempt_guidance: tuple[str, ...] = (),
    ) -> str:
        """Build a mutation prompt where the proof must remain correct."""

        objective_text = objective.strip() or "Find an interesting correctness-preserving proof mutation."
        return self._mutation_instruction_prompt(
            objective_text=objective_text,
            maintain_correctness=True,
            strategy_guidance=strategy_guidance,
            prior_attempt_guidance=prior_attempt_guidance,
        )

    def false_proof_mutation_instruction_prompt(
        self,
        *,
        objective: str = "",
        strategy_guidance: tuple[str, ...] = (),
        prior_attempt_guidance: tuple[str, ...] = (),
    ) -> str:
        """Build a mutation prompt where the proof should become false."""

        objective_text = objective.strip() or "Find an interesting mutation that makes the proof false."
        return self._mutation_instruction_prompt(
            objective_text=objective_text,
            maintain_correctness=False,
            strategy_guidance=strategy_guidance,
            prior_attempt_guidance=prior_attempt_guidance,
        )

    def validate_mutation_instructions(
        self,
        instructions: FuzzerMutationInstructions,
    ) -> tuple[MutationValidationIssue, ...]:
        """Return text-level structural validation issues for natural-language mutations."""

        issues: list[MutationValidationIssue] = []
        segment_ids = {segment.segment_id for segment in self.segments}

        for index, mutation in enumerate(instructions.mutations):
            target = mutation.target.strip()
            if not target:
                issues.append(MutationValidationIssue(index, "Mutation target is required.", field="target"))
                continue

            if mutation.kind in {"modify", "remove"} and target not in segment_ids:
                issues.append(
                    MutationValidationIssue(
                        index,
                        f"Unknown natural-language proof segment {target!r}.",
                        field="target",
                    )
                )

            if mutation.kind == "add" and not self._valid_insert_target(target, segment_ids):
                issues.append(
                    MutationValidationIssue(
                        index,
                        "Add target must be 'start', 'end', 'before:<segment id>', or 'after:<segment id>'.",
                        field="target",
                    )
                )

            if mutation.kind == "global_context" and target.lower().replace(" ", "_") not in {
                GLOBAL_CONTEXT,
                "whole_proof",
            }:
                issues.append(
                    MutationValidationIssue(
                        index,
                        "Whole-proof natural-language mutations must target global_context or whole_proof.",
                        field="target",
                    )
                )

            if mutation.kind in {"modify", "add", "global_context"} and not mutation.new_text.strip():
                issues.append(
                    MutationValidationIssue(
                        index,
                        f"{mutation.kind} mutations must include non-empty new_text.",
                        field="new_text",
                    )
                )

        return tuple(issues)

    def apply_mutations(self, instructions: FuzzerMutationInstructions) -> str:
        """Apply validated text-level mutations to the original natural-language proof."""

        self._raise_for_invalid_mutation_instructions(instructions)

        segments = [(segment.segment_id, segment.text) for segment in self.segments]
        for mutation in instructions.mutations:
            if mutation.kind == "global_context":
                segments = [("S1", mutation.new_text.strip())]
                continue

            if mutation.kind == "modify":
                segments = [
                    (segment_id, mutation.new_text.strip() if segment_id == mutation.target else text)
                    for segment_id, text in segments
                ]
                continue

            if mutation.kind == "remove":
                segments = [(segment_id, text) for segment_id, text in segments if segment_id != mutation.target]
                continue

            if mutation.kind == "add":
                segments = self._insert_segment(segments, mutation.target, mutation.new_text.strip())

        return "\n\n".join(text for _, text in segments if text.strip())

    def _mutation_instruction_prompt(
        self,
        *,
        objective_text: str,
        maintain_correctness: bool | None,
        strategy_guidance: tuple[str, ...] = (),
        prior_attempt_guidance: tuple[str, ...] = (),
    ) -> str:
        segment_text = "\n\n".join(
            f"### {segment.segment_id}\n{segment.text}"
            for segment in self.segments
        )
        correctness_line = (
            "Choose whether the resulting proof should remain correct."
            if maintain_correctness is None
            else (
                "The resulting proof must remain mathematically correct."
                if maintain_correctness
                else "The resulting proof must become mathematically incorrect as written."
            )
        )
        correctness_schema = "true | false" if maintain_correctness is None else ("true" if maintain_correctness else "false")
        propagation_schema = "true | false" if maintain_correctness is False else ("true" if maintain_correctness is True else "true | false")
        fixed_instruction = (
            ""
            if maintain_correctness is None
            else f"\nThe JSON field maintain_correctness must be exactly {correctness_schema}."
        )
        judge_goal = (
            "- For an incorrect-proof mutation, try to make the proof plausibly trick an LLM judge into thinking it is correct.\n"
            "- For a correctness-preserving mutation, try to make the proof plausibly trick an LLM judge into thinking it is incorrect."
            if maintain_correctness is None
            else (
                "Generate a correctness-preserving mutation that could plausibly trick an LLM judge into thinking the proof is incorrect."
                if maintain_correctness
                else "Generate an actually incorrect-proof mutation that could plausibly trick an LLM judge into thinking the proof is correct."
            )
        )

        return f"""You are acting as a proof fuzzer for a natural-language mathematical proof.

Objective:
{objective_text}

Correctness target:
{correctness_line}{fixed_instruction}

Judge-fuzzing goal:
{judge_goal}

Mutation quality:
{_natural_language_mutation_quality_guidance(maintain_correctness=maintain_correctness)}
{_format_strategy_guidance(strategy_guidance)}
{_format_prior_attempt_guidance(prior_attempt_guidance)}

Targetable proof segments:
{segment_text}

Return exactly one JSON object. Do not include prose outside the JSON.
Schema:
```json
{{
  "maintain_correctness": {correctness_schema},
  "rationale": "short reason for the chosen fuzzing direction; for maintain_correctness=false, name the first indispensable broken step and why the mutated proof does not repair it",
  "mutations": [
    {{
      "kind": "modify | remove | add | global_context",
      "target": "segment id for modify/remove, start/end/before:S1/after:S1 for add, or whole_proof for global_context",
      "summary": "one elementary mutation",
      "new_text": "replacement or inserted natural-language proof text, empty for remove when appropriate",
      "affected_blocks": [],
      "propagate_downstream": {propagation_schema}
    }}
  ]
}}
```

Each item in mutations must be one elementary mutation. Use multiple items for compound edits.
"""

    @staticmethod
    def _valid_insert_target(target: str, segment_ids: set[str]) -> bool:
        if target in {"start", "end"}:
            return True
        if ":" not in target:
            return False
        position, segment_id = target.split(":", 1)
        return position in {"before", "after"} and segment_id in segment_ids

    @staticmethod
    def _insert_segment(
        segments: list[tuple[str, str]],
        target: str,
        new_text: str,
    ) -> list[tuple[str, str]]:
        new_segment = (f"S{len(segments) + 1}", new_text)
        if target == "start":
            return [new_segment] + segments
        if target == "end":
            return segments + [new_segment]

        position, target_id = target.split(":", 1)
        result: list[tuple[str, str]] = []
        inserted = False
        for segment in segments:
            if position == "before" and segment[0] == target_id:
                result.append(new_segment)
                inserted = True
            result.append(segment)
            if position == "after" and segment[0] == target_id:
                result.append(new_segment)
                inserted = True
        if not inserted:
            result.append(new_segment)
        return result


ProofFuzzerLLMInterface = SemiFormalProofFuzzerLLMInterface


def split_natural_language_proof(proof_text: str) -> tuple[NaturalLanguageProofSegment, ...]:
    """Split natural-language proof text into stable, targetable segments."""

    paragraphs = [part.strip() for part in re.split(r"\n\s*\n", proof_text.strip()) if part.strip()]
    if len(paragraphs) <= 1:
        paragraphs = [line.strip() for line in proof_text.splitlines() if line.strip()]
    if not paragraphs and proof_text.strip():
        paragraphs = (proof_text.strip(),)
    return tuple(
        NaturalLanguageProofSegment(segment_id=f"S{index}", text=paragraph)
        for index, paragraph in enumerate(paragraphs, start=1)
    )


def _natural_language_mutation_quality_guidance(*, maintain_correctness: bool | None) -> str:
    shared = """Prefer meaningful mathematical mutations over surface edits.
- High-value direct mutations alter a hypothesis, quantifier, case split, construction, dependency, hidden exception, inequality threshold, modular condition, or the logical bridge between sentences.
- Preserve the local writing style and plausibility of the original proof, so the mutated proof still reads naturally.
- Avoid cosmetic rewording. The changed text should materially change what can be inferred.
- Do not put self-incriminating language in new_text or the mutated proof, such as "incorrectly", "this is false", "invalid", "mistake", "flaw", "omitted", or comments that reveal a term was deliberately dropped. Explain the intended flaw only in the rationale or summary fields.
- In the rationale and summary, name the intended failure mechanism or alternate valid proof route."""
    if maintain_correctness is True:
        return (
            shared
            + "\n- For correctness-preserving mutations, prefer valid alternate arguments, reorganized steps, "
            "or stronger/weaker statements that remain sufficient."
        )
    if maintain_correctness is False:
        return (
            shared
            + "\n- For incorrect-proof mutations, prefer subtle proof gaps: omit a necessary case, weaken a "
            "premise, overgeneralize a claim, or make an inference that is locally plausible but invalid."
            "\n- The mutated proof must be mathematically incorrect as written. It is not enough to introduce "
            "awkward wording, remove nonessential detail, make a harmless local false claim, or create a gap "
            "that an earlier/later argument repairs."
            "\n- Before returning, audit your own mutation: identify the first indispensable proof step that "
            "becomes invalid, verify that no alternate route in the mutated proof still proves the conclusion, "
            "and explain this in the rationale or mutation summaries. If you cannot find such an unrepairable "
            "broken step, choose a different mutation."
            "\n- You may decide to propagate a local change into later sentences when doing so makes the "
            "mutated proof more coherent and convincing to a judge. Use additional downstream mutations to "
            "keep notation, references, and claimed conclusions consistent, while preserving the underlying "
            "mathematical flaw."
        )
    return (
        shared
        + "\n- If choosing the correctness target yourself, choose the direction that creates the most "
        "informative nontrivial mutation for this proof."
    )


def _format_strategy_guidance(strategy_guidance: tuple[str, ...]) -> str:
    guidance = tuple(item.strip() for item in strategy_guidance if item.strip())
    if not guidance:
        return ""
    lines = "\nStrategy guidance:"
    lines += "\n" + "\n".join(f"- {item}" for item in guidance)
    return lines


def _format_prior_attempt_guidance(prior_attempt_guidance: tuple[str, ...]) -> str:
    guidance = tuple(item.strip() for item in prior_attempt_guidance if item.strip())
    if not guidance:
        return ""
    lines = "\nPrevious attempts on this same proof:"
    lines += (
        "\nUse failed attempts to avoid repeating failure modes. Use successful attempts marked AVOID to choose "
        "a genuinely different target line, proof dependency, or error mechanism."
    )
    lines += "\n" + "\n".join(f"- {item}" for item in guidance)
    return lines


def _mutation_quality_guidance(*, maintain_correctness: bool | None) -> str:
    shared = """Prefer meaningful mathematical mutations over surface edits.
- High-value mutations change a dependency, quantifier, hypothesis strength, hidden case split, lemma scope, construction choice, extremal choice, divisibility/modular condition, inequality threshold, or use of an allowed reference.
- Aim for a mutation whose effect is nonlocal or conceptually important: downstream blocks should become subtly unsupported, need a real repair, or have to use a different route.
- Avoid cheap symbol-only edits such as merely changing a sign, swapping + and -, changing one constant, or negating a conclusion unless the rationale explains why this creates a genuinely subtle dependency failure.
- Avoid cosmetic rewording. The new_text should materially change what can be inferred from the block.
- Prefer mutations that preserve semi-formal parseability and local plausibility, so a shallow judge may accept the mutated block in isolation.
- Do not put self-incriminating language in new_text or any materialized proof text, such as "incorrectly", "this is false", "invalid", "mistake", "flaw", "omitted", or comments that reveal a term was deliberately dropped. Explain the intended flaw only in the rationale or summary fields.
- In the rationale and summary, name the intended failure mechanism and the downstream dependency or proof obligation it affects."""
    if maintain_correctness is True:
        return (
            shared
            + "\n- For correctness-preserving mutations, prefer alternative valid lemmas, weaker-but-sufficient "
            "statements, stronger hypotheses with downstream repairs, or reorganized intermediate claims over "
            "trivial restatements."
        )
    if maintain_correctness is False:
        return (
            shared
            + "\n- For incorrect-proof mutations, prefer proof-gap mutations: remove a necessary hypothesis, "
            "weaken a lemma below what successors use, change a quantifier/domain, invalidate a case split, or "
            "alter a referenced construction."
            "\n- The mutated proof must be mathematically incorrect as written. It is not enough to introduce "
            "awkward wording, remove nonessential detail, make a harmless local false claim, or create a gap "
            "that an earlier/later argument repairs."
            "\n- Before returning, audit your own mutation: identify the first indispensable proof step that "
            "becomes invalid, verify that no alternate route in the mutated proof still proves the conclusion, "
            "and explain this in the rationale or mutation summaries. If you cannot find such an unrepairable "
            "broken step, choose a different mutation."
            "\n- You may decide whether to propagate a local change to subsequent inferences. If propagation "
            "makes the false proof more locally coherent and judge-convincing, include companion mutations or "
            "set propagate_downstream accordingly so notation, references, and later claims stay consistent "
            "while the core mathematical flaw remains."
        )
    return (
        shared
        + "\n- If choosing the correctness target yourself, choose the direction that allows the most informative "
        "nontrivial mutation for this proof."
    )


def _complete_llm(llm: LLMClient, prompt: str) -> LLMCompletionTrace:
    complete_with_reasoning = getattr(llm, "complete_with_reasoning", None)
    if callable(complete_with_reasoning):
        return _coerce_completion_trace(complete_with_reasoning(prompt))

    response = llm.complete(prompt)
    reasoning = str(getattr(llm, "last_reasoning", "") or "")
    raw_result = getattr(llm, "last_result", None)
    if raw_result is not None and not reasoning:
        reasoning = _object_field(raw_result, "reasoning")
    return LLMCompletionTrace(response=str(response), reasoning=reasoning, raw_result=raw_result)


def _coerce_completion_trace(result: object) -> LLMCompletionTrace:
    if isinstance(result, LLMCompletionTrace):
        return result
    if isinstance(result, str):
        return LLMCompletionTrace(response=result)
    if isinstance(result, dict):
        return LLMCompletionTrace(
            response=str(result.get("content", result.get("response", ""))),
            reasoning=str(result.get("reasoning", result.get("reasoning_content", "")) or ""),
            raw_result=result,
        )

    return LLMCompletionTrace(
        response=_object_field(result, "content") or _object_field(result, "response"),
        reasoning=_object_field(result, "reasoning") or _object_field(result, "reasoning_content"),
        raw_result=result,
    )


def _object_field(value: object, field_name: str) -> str:
    field_value = getattr(value, field_name, None)
    if field_value is not None:
        return str(field_value)
    if hasattr(value, "model_dump"):
        dumped = value.model_dump()
        if isinstance(dumped, dict) and dumped.get(field_name) is not None:
            return str(dumped[field_name])
    return ""


def _slugify_call_kind(call_kind: str) -> str:
    slug = re.sub(r"[^A-Za-z0-9_.-]+", "_", call_kind.strip())
    return slug.strip("_") or "llm_call"


def parse_mutation_instructions(text: str) -> FuzzerMutationInstructions:
    """Parse a structured proof-fuzzer mutation response."""

    data = _load_json_object(text)
    maintain_correctness = _parse_bool(data.get("maintain_correctness"), field_name="maintain_correctness")
    rationale = str(data.get("rationale", ""))

    raw_mutations = data.get("mutations", data.get("elementary_mutations"))
    if not isinstance(raw_mutations, list):
        raise ValueError("Mutation response must contain a list field named 'mutations'.")

    mutations = tuple(_parse_mutation(item) for item in raw_mutations)
    return FuzzerMutationInstructions(
        maintain_correctness=maintain_correctness,
        mutations=mutations,
        rationale=rationale,
        raw_response=text,
    )


def parse_block_update_response(block_id: str, text: str) -> BlockUpdateResult:
    """Parse an LLM response to a block-update prompt."""

    stripped = text.strip()
    if stripped == NO_CHANGE_NEEDED:
        return BlockUpdateResult(block_id=block_id, changed=False, raw_response=text)

    revised_text = _strip_single_fenced_block(stripped)
    if revised_text.strip() == NO_CHANGE_NEEDED:
        return BlockUpdateResult(block_id=block_id, changed=False, raw_response=text)

    return BlockUpdateResult(
        block_id=block_id,
        changed=True,
        revised_text=revised_text,
        raw_response=text,
    )


def _validate_fixed_correctness(instructions: FuzzerMutationInstructions, *, expected: bool) -> None:
    if instructions.maintain_correctness != expected:
        expected_text = "true" if expected else "false"
        actual_text = "true" if instructions.maintain_correctness else "false"
        raise ValueError(
            "Mutation response contradicted the fixed correctness target: "
            f"expected maintain_correctness={expected_text}, got {actual_text}."
        )


def _parse_mutation(data: object) -> ProofMutation:
    if not isinstance(data, dict):
        raise ValueError("Each mutation must be an object.")

    kind = str(data.get("kind", "")).strip().lower()
    target = str(data.get("target", "")).strip()
    summary = str(data.get("summary", ""))
    new_text = _normalize_new_text(str(data.get("new_text", "")))
    affected_blocks = _normalize_string_tuple(data.get("affected_blocks", ()), field_name="affected_blocks")
    propagate_downstream = _parse_bool(data.get("propagate_downstream", True), field_name="propagate_downstream")

    return ProofMutation(
        kind=kind,
        target=target,
        summary=summary,
        new_text=new_text,
        affected_blocks=affected_blocks,
        propagate_downstream=propagate_downstream,
    )


def _load_json_object(text: str) -> dict[str, object]:
    candidate = _extract_json_candidate(text)
    try:
        data = json.loads(candidate)
    except json.JSONDecodeError:
        data = json.loads(
            _repair_llm_json_backslashes(candidate),
            strict=False,
        )
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


_COMMON_LATEX_COMMANDS = (
    "begin",
    "boxed",
    "cdot",
    "cos",
    "delta",
    "Delta",
    "displaystyle",
    "end",
    "epsilon",
    "frac",
    "gamma",
    "Gamma",
    "ge",
    "geq",
    "infty",
    "lambda",
    "Lambda",
    "left",
    "le",
    "leq",
    "log",
    "mathbb",
    "mathbf",
    "mathrm",
    "neq",
    "not",
    "omega",
    "Omega",
    "overline",
    "phi",
    "Phi",
    "pi",
    "Pi",
    "prod",
    "right",
    "sin",
    "sqrt",
    "sum",
    "tau",
    "text",
    "theta",
    "Theta",
    "times",
    "to",
    "varepsilon",
    "varphi",
)


def _repair_llm_json_backslashes(candidate: str) -> str:
    """Escape common raw-LaTeX backslashes that make LLM JSON invalid.

    Models often emit JSON strings containing LaTeX such as ``\frac`` or
    ``\theta``. JSON treats several of these as invalid escapes, and a few
    others as valid-but-wrong escapes like form feed or tab. This repair keeps
    ordinary JSON escapes intact while turning common LaTeX commands into
    literal backslashes before parsing.
    """

    command_pattern = re.compile(
        r"(?<!\\)\\("
        + "|".join(re.escape(command) for command in sorted(_COMMON_LATEX_COMMANDS, key=len, reverse=True))
        + r")(?=\b|[^A-Za-z])"
    )
    repaired = command_pattern.sub(lambda match: "\\\\" + match.group(1), candidate)
    return re.sub(r'(?<!\\)\\(?!["\\/bfnrtu])', r"\\\\", repaired)


def _parse_bool(value: object, *, field_name: str) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        lowered = value.strip().lower()
        if lowered == "true":
            return True
        if lowered == "false":
                return False
    raise ValueError(f"Field {field_name!r} must be a boolean.")


def _normalize_string_tuple(value: object, *, field_name: str) -> tuple[str, ...]:
    if value is None:
        return ()
    if isinstance(value, str):
        stripped = value.strip()
        return (stripped,) if stripped else ()
    if isinstance(value, (list, tuple)):
        return tuple(str(item).strip() for item in value if str(item).strip())
    raise ValueError(f"Mutation field {field_name!r} must be a list, string, or null when present.")


def _normalize_new_text(text: str) -> str:
    stripped = _strip_single_fenced_block(text.strip())
    if "\\n" in stripped and "\n" not in stripped:
        stripped = stripped.replace("\\n", "\n")
    return stripped


def _strip_single_fenced_block(text: str) -> str:
    fenced = re.fullmatch(r"```(?:text)?\s*(.*?)\s*```", text, flags=re.DOTALL)
    if fenced:
        return fenced.group(1)
    return text
