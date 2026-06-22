"""LLM-guided mutation planning for semi-formalized proofs."""

from __future__ import annotations

from collections import defaultdict, deque
from dataclasses import dataclass, field
from typing import Iterable

from .proof_graph import GLOBAL_CONTEXT, ProofGraph


MUTATION_KINDS = {"modify", "remove", "add", "global_context"}


@dataclass(frozen=True)
class ProofMutation:
    """A proposed edit to a semi-formal proof.

    ``affected_blocks`` is for non-local edits the current graph cannot infer,
    especially adding a new block that existing downstream blocks should start
    using.
    """

    kind: str
    target: str = ""
    summary: str = ""
    new_text: str = ""
    affected_blocks: tuple[str, ...] = ()
    propagate_downstream: bool = True
    metadata: dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.kind not in MUTATION_KINDS:
            allowed = ", ".join(sorted(MUTATION_KINDS))
            raise ValueError(f"Unknown mutation kind {self.kind!r}; expected one of: {allowed}")
        object.__setattr__(self, "affected_blocks", tuple(self.affected_blocks))

    @classmethod
    def modify(
        cls,
        target: str,
        *,
        summary: str = "",
        new_text: str = "",
        affected_blocks: Iterable[str] = (),
        propagate_downstream: bool = True,
    ) -> "ProofMutation":
        return cls(
            kind="modify",
            target=target,
            summary=summary,
            new_text=new_text,
            affected_blocks=tuple(affected_blocks),
            propagate_downstream=propagate_downstream,
        )

    @classmethod
    def remove(
        cls,
        target: str,
        *,
        summary: str = "",
        affected_blocks: Iterable[str] = (),
        propagate_downstream: bool = True,
    ) -> "ProofMutation":
        return cls(
            kind="remove",
            target=target,
            summary=summary,
            affected_blocks=tuple(affected_blocks),
            propagate_downstream=propagate_downstream,
        )

    @classmethod
    def add(
        cls,
        target: str,
        *,
        summary: str = "",
        new_text: str = "",
        affected_blocks: Iterable[str] = (),
        propagate_downstream: bool = True,
    ) -> "ProofMutation":
        return cls(
            kind="add",
            target=target,
            summary=summary,
            new_text=new_text,
            affected_blocks=tuple(affected_blocks),
            propagate_downstream=propagate_downstream,
        )

    @classmethod
    def global_context(
        cls,
        *,
        summary: str = "",
        new_text: str = "",
        propagate_downstream: bool = True,
    ) -> "ProofMutation":
        return cls(
            kind="global_context",
            target=GLOBAL_CONTEXT,
            summary=summary,
            new_text=new_text,
            propagate_downstream=propagate_downstream,
        )

    def to_dict(self) -> dict[str, object]:
        return {
            "kind": self.kind,
            "target": self.target,
            "summary": self.summary,
            "new_text": self.new_text,
            "affected_blocks": list(self.affected_blocks),
            "propagate_downstream": self.propagate_downstream,
            "metadata": dict(self.metadata),
        }


@dataclass(frozen=True)
class MutationImpactPlan:
    """A static BFS update plan induced by one or more proof mutations."""

    mutations: tuple[ProofMutation, ...]
    directly_changed: tuple[str, ...]
    frontiers: tuple[tuple[str, ...], ...]
    reasons: dict[str, tuple[str, ...]]

    @property
    def affected_blocks(self) -> tuple[str, ...]:
        return tuple(block for frontier in self.frontiers for block in frontier)

    def to_dict(self) -> dict[str, object]:
        return {
            "mutations": [mutation.to_dict() for mutation in self.mutations],
            "directly_changed": list(self.directly_changed),
            "frontiers": [list(frontier) for frontier in self.frontiers],
            "affected_blocks": list(self.affected_blocks),
            "reasons": {block: list(reasons) for block, reasons in self.reasons.items()},
        }


@dataclass(frozen=True)
class LLMBlockUpdatePrompt:
    """A prompt asking an LLM to update one affected proof block."""

    block_id: str
    frontier_index: int
    reasons: tuple[str, ...]
    current_text: str
    prompt: str

    def to_dict(self) -> dict[str, object]:
        return {
            "block_id": self.block_id,
            "frontier_index": self.frontier_index,
            "reasons": list(self.reasons),
            "current_text": self.current_text,
            "prompt": self.prompt,
        }


@dataclass(frozen=True)
class ProgressiveMutationSession:
    """State for conditional BFS mutation propagation.

    Only blocks in ``current_frontier`` should be prompted now. After the caller
    runs those prompts, call ``advance(changed_blocks)`` with the subset that
    actually changed; only successors of that subset are scheduled next.
    """

    graph: ProofGraph
    mutations: tuple[ProofMutation, ...]
    directly_changed: tuple[str, ...]
    current_frontier: tuple[str, ...]
    frontier_index: int = 0
    reasons: dict[str, tuple[str, ...]] = field(default_factory=dict)
    changed_blocks: tuple[str, ...] = ()
    prompted_blocks: tuple[str, ...] = ()

    @property
    def done(self) -> bool:
        return not self.current_frontier

    @property
    def affected_blocks(self) -> tuple[str, ...]:
        return _dedupe_preserving_order(self.prompted_blocks + self.current_frontier)

    def current_prompts(self) -> tuple[LLMBlockUpdatePrompt, ...]:
        return MutationPlanner(self.graph).progressive_update_prompts(self)

    def advance(self, changed_blocks: Iterable[str]) -> "ProgressiveMutationSession":
        return MutationPlanner(self.graph).advance_progressive_session(self, changed_blocks)

    def to_dict(self) -> dict[str, object]:
        return {
            "mutations": [mutation.to_dict() for mutation in self.mutations],
            "directly_changed": list(self.directly_changed),
            "current_frontier": list(self.current_frontier),
            "frontier_index": self.frontier_index,
            "affected_blocks": list(self.affected_blocks),
            "changed_blocks": list(self.changed_blocks),
            "prompted_blocks": list(self.prompted_blocks),
            "reasons": {block: list(reasons) for block, reasons in self.reasons.items()},
            "done": self.done,
        }


class MutationPlanner:
    """Plans static and conditional LLM-guided proof mutations."""

    def __init__(self, graph: ProofGraph):
        self.graph = graph

    def plan_mutations(
        self,
        mutations: Iterable[ProofMutation],
        *,
        include_direct_changes: bool = False,
    ) -> MutationImpactPlan:
        """Return a static BFS update plan for proof mutations.

        Modifying or removing an existing block propagates through the graph
        unless ``propagate_downstream`` is false. Adding a new block does not
        have known dependents yet, so callers can use ``affected_blocks`` on
        the mutation to seed blocks that should be rewritten to use the
        addition.
        """

        mutation_tuple, direct, seeds, forced, explicit_reasons = self._mutation_inputs(mutations)
        frontiers = self._mutation_frontiers(
            seeds,
            forced,
            direct=direct,
            include_direct_changes=include_direct_changes,
        )
        affected = {block for frontier in frontiers for block in frontier}
        reasons = self._mutation_reasons(seeds, affected, explicit_reasons)

        return MutationImpactPlan(
            mutations=mutation_tuple,
            directly_changed=direct,
            frontiers=frontiers,
            reasons=reasons,
        )

    def iter_mutation_frontier_prompts(
        self,
        plan: MutationImpactPlan,
    ) -> Iterable[tuple[LLMBlockUpdatePrompt, ...]]:
        """Yield LLM prompts one BFS frontier at a time."""

        for frontier_index, frontier in enumerate(plan.frontiers):
            yield tuple(
                self.mutation_update_prompt(plan, block_id, frontier_index=frontier_index)
                for block_id in frontier
            )

    def mutation_update_prompts(
        self,
        plan: MutationImpactPlan,
    ) -> tuple[LLMBlockUpdatePrompt, ...]:
        """Return flattened LLM update prompts for all affected blocks."""

        prompts: list[LLMBlockUpdatePrompt] = []
        for frontier_prompts in self.iter_mutation_frontier_prompts(plan):
            prompts.extend(frontier_prompts)
        return tuple(prompts)

    def mutation_update_prompt(
        self,
        plan: MutationImpactPlan,
        block_id: str,
        *,
        frontier_index: int = 0,
    ) -> LLMBlockUpdatePrompt:
        """Build a focused prompt for updating one affected block."""

        current_text = self.graph.block_text(block_id)
        reasons = plan.reasons.get(block_id, ())
        prompt = self._format_mutation_prompt(plan, block_id, frontier_index, reasons, current_text)
        return LLMBlockUpdatePrompt(
            block_id=block_id,
            frontier_index=frontier_index,
            reasons=reasons,
            current_text=current_text,
            prompt=prompt,
        )

    def start_progressive_mutations(
        self,
        mutations: Iterable[ProofMutation],
        *,
        include_direct_changes: bool = False,
    ) -> ProgressiveMutationSession:
        """Start conditional BFS propagation for LLM-guided mutations.

        Unlike ``plan_mutations``, this does not schedule all transitive
        successors immediately. Call ``advance`` with the blocks that actually
        changed after each LLM frontier.
        """

        mutation_tuple, direct, seeds, forced, explicit_reasons = self._mutation_inputs(mutations)

        if include_direct_changes:
            current_frontier = self.graph.sort_nodes(direct + forced)
            reasons = self._initial_progressive_reasons(current_frontier, seeds, explicit_reasons)
            changed_blocks: tuple[str, ...] = ()
        else:
            current_frontier = self._next_frontier_from_changed(seeds, already_seen=forced)
            current_frontier = self.graph.sort_nodes(current_frontier + forced)
            reasons = self._initial_progressive_reasons(current_frontier, seeds, explicit_reasons)
            changed_blocks = seeds

        return ProgressiveMutationSession(
            graph=self.graph,
            mutations=mutation_tuple,
            directly_changed=direct,
            current_frontier=current_frontier,
            frontier_index=0,
            reasons=reasons,
            changed_blocks=changed_blocks,
            prompted_blocks=(),
        )

    def advance_progressive_session(
        self,
        session: ProgressiveMutationSession,
        changed_blocks: Iterable[str],
    ) -> ProgressiveMutationSession:
        """Advance a progressive session from the subset that actually changed."""

        changed = self._normalize_frontier_results(changed_blocks, session.current_frontier)
        prompted = _dedupe_preserving_order(session.prompted_blocks + session.current_frontier)
        all_changed = _dedupe_preserving_order(session.changed_blocks + changed)
        next_frontier = self._next_frontier_from_changed(changed, already_seen=prompted)
        next_reasons = dict(session.reasons)

        if next_frontier:
            next_reasons.update(self._frontier_reasons_from_changed(next_frontier, changed))

        return ProgressiveMutationSession(
            graph=self.graph,
            mutations=session.mutations,
            directly_changed=session.directly_changed,
            current_frontier=next_frontier,
            frontier_index=session.frontier_index + 1,
            reasons=next_reasons,
            changed_blocks=all_changed,
            prompted_blocks=prompted,
        )

    def progressive_update_prompts(
        self,
        session: ProgressiveMutationSession,
    ) -> tuple[LLMBlockUpdatePrompt, ...]:
        """Return prompts for the session's current conditional frontier."""

        return tuple(
            self.progressive_update_prompt(session, block_id)
            for block_id in session.current_frontier
        )

    def progressive_update_prompt(
        self,
        session: ProgressiveMutationSession,
        block_id: str,
    ) -> LLMBlockUpdatePrompt:
        """Build one prompt for a progressive conditional frontier."""

        current_text = self.graph.block_text(block_id)
        reasons = session.reasons.get(block_id, ())
        plan = MutationImpactPlan(
            mutations=session.mutations,
            directly_changed=session.directly_changed,
            frontiers=(session.current_frontier,),
            reasons=session.reasons,
        )
        prompt = self._format_mutation_prompt(
            plan,
            block_id,
            session.frontier_index,
            reasons,
            current_text,
        )
        return LLMBlockUpdatePrompt(
            block_id=block_id,
            frontier_index=session.frontier_index,
            reasons=reasons,
            current_text=current_text,
            prompt=prompt,
        )

    def _mutation_inputs(
        self,
        mutations: Iterable[ProofMutation],
    ) -> tuple[tuple[ProofMutation, ...], tuple[str, ...], tuple[str, ...], tuple[str, ...], dict[str, set[str]]]:
        mutation_tuple = tuple(mutations)
        direct_changes: list[str] = []
        propagation_seeds: list[str] = []
        explicit_affected: list[str] = []
        explicit_reasons: dict[str, set[str]] = defaultdict(set)

        for mutation in mutation_tuple:
            target = mutation.target or GLOBAL_CONTEXT
            if mutation.kind == "global_context":
                direct_changes.append(GLOBAL_CONTEXT)
                if mutation.propagate_downstream:
                    propagation_seeds.append(GLOBAL_CONTEXT)
            elif mutation.kind in {"modify", "remove"}:
                normalized_target = self.graph.normalize_block_ids([target])
                direct_changes.extend(normalized_target)
                if mutation.propagate_downstream:
                    propagation_seeds.extend(normalized_target)
            elif mutation.kind == "add" and target in self.graph.node_kinds:
                normalized_target = self.graph.normalize_block_ids([target])
                direct_changes.extend(normalized_target)
                if mutation.propagate_downstream:
                    propagation_seeds.extend(normalized_target)

            for affected in mutation.affected_blocks:
                normalized_affected = self.graph.normalize_block_ids([affected])
                explicit_affected.extend(normalized_affected)
                reason = mutation.target or mutation.kind
                for block_id in normalized_affected:
                    explicit_reasons[block_id].add(reason)

        return (
            mutation_tuple,
            _dedupe_preserving_order(direct_changes),
            _dedupe_preserving_order(propagation_seeds),
            _dedupe_preserving_order(explicit_affected),
            explicit_reasons,
        )

    def _mutation_frontiers(
        self,
        seeds: tuple[str, ...],
        forced: tuple[str, ...],
        *,
        direct: tuple[str, ...],
        include_direct_changes: bool,
    ) -> tuple[tuple[str, ...], ...]:
        if GLOBAL_CONTEXT in seeds:
            all_blocks = self.graph.sort_nodes(self.graph.nodes)
            if include_direct_changes:
                return ((GLOBAL_CONTEXT,), all_blocks)
            return (all_blocks,)

        levels: dict[int, set[str]] = defaultdict(set)
        seen = set(seeds) | set(forced)
        if include_direct_changes:
            seen.update(direct)
        queue: deque[tuple[str, int]] = deque()

        for block_id in direct:
            if include_direct_changes:
                levels[0].add(block_id)

        seed_level = 0 if include_direct_changes else -1
        for block_id in seeds:
            queue.append((block_id, seed_level))

        forced_level = 1 if include_direct_changes and direct else 0
        for block_id in forced:
            if block_id in direct and not include_direct_changes:
                continue
            levels[forced_level].add(block_id)
            queue.append((block_id, forced_level))

        while queue:
            current, depth = queue.popleft()
            for dependent in self.graph.sort_nodes(self.graph.reverse_dependencies.get(current, set())):
                if dependent in seen:
                    continue
                seen.add(dependent)
                next_depth = depth + 1
                levels[next_depth].add(dependent)
                queue.append((dependent, next_depth))

        return tuple(
            self.graph.sort_nodes(levels[level])
            for level in sorted(levels)
            if level >= 0 and levels[level]
        )

    def _mutation_reasons(
        self,
        direct: tuple[str, ...],
        affected: set[str],
        explicit_reasons: dict[str, set[str]],
    ) -> dict[str, tuple[str, ...]]:
        reasons: dict[str, tuple[str, ...]] = {}
        direct_or_affected = set(direct) | affected

        for block_id in affected:
            if GLOBAL_CONTEXT in direct:
                reasons[block_id] = (GLOBAL_CONTEXT,)
                continue

            reason_ids = set(explicit_reasons.get(block_id, set()))
            reason_ids.update(self.graph.dependencies.get(block_id, set()) & direct_or_affected)
            reasons[block_id] = self.graph.sort_reason_ids(reason_ids)

        return reasons

    def _initial_progressive_reasons(
        self,
        frontier: tuple[str, ...],
        seeds: tuple[str, ...],
        explicit_reasons: dict[str, set[str]],
    ) -> dict[str, tuple[str, ...]]:
        reasons: dict[str, tuple[str, ...]] = {}
        seed_set = set(seeds)

        for block_id in frontier:
            if GLOBAL_CONTEXT in seed_set and block_id != GLOBAL_CONTEXT:
                reasons[block_id] = (GLOBAL_CONTEXT,)
                continue
            reason_ids = set(explicit_reasons.get(block_id, set()))
            reason_ids.update(self.graph.dependencies.get(block_id, set()) & seed_set)
            reasons[block_id] = self.graph.sort_reason_ids(reason_ids)

        return reasons

    def _frontier_reasons_from_changed(
        self,
        frontier: tuple[str, ...],
        changed: tuple[str, ...],
    ) -> dict[str, tuple[str, ...]]:
        reasons: dict[str, tuple[str, ...]] = {}
        changed_set = set(changed)

        for block_id in frontier:
            if GLOBAL_CONTEXT in changed_set:
                reasons[block_id] = (GLOBAL_CONTEXT,)
                continue
            reason_ids = self.graph.dependencies.get(block_id, set()) & changed_set
            reasons[block_id] = self.graph.sort_reason_ids(reason_ids)

        return reasons

    def _next_frontier_from_changed(
        self,
        changed: tuple[str, ...],
        *,
        already_seen: tuple[str, ...],
    ) -> tuple[str, ...]:
        if not changed:
            return ()

        seen = set(already_seen) | set(changed)
        if GLOBAL_CONTEXT in changed:
            return self.graph.sort_nodes(node for node in self.graph.nodes if node not in seen)

        candidates: set[str] = set()
        for block_id in changed:
            candidates.update(self.graph.reverse_dependencies.get(block_id, set()))
        candidates.difference_update(seen)
        return self.graph.sort_nodes(candidates)

    def _normalize_frontier_results(
        self,
        changed_blocks: Iterable[str],
        current_frontier: tuple[str, ...],
    ) -> tuple[str, ...]:
        normalized = self.graph.normalize_block_ids(changed_blocks)
        frontier_set = set(current_frontier)
        outside = [block_id for block_id in normalized if block_id not in frontier_set]
        if outside:
            raise ValueError(f"Changed blocks are not in the current frontier: {outside}")
        return normalized

    def _format_mutation_prompt(
        self,
        plan: MutationImpactPlan,
        block_id: str,
        frontier_index: int,
        reasons: tuple[str, ...],
        current_text: str,
    ) -> str:
        mutation_lines = "\n".join(f"- {_describe_mutation(mutation)}" for mutation in plan.mutations)
        reason_text = ", ".join(reasons) if reasons else "the mutation plan"
        upstream_text = self._format_reason_blocks(plan, reasons)

        return f"""You are updating one block in a semi-formalized mathematical proof.

This update is being requested so the overall proof remains correct after the mutations.

The proof has been changed by these mutations:
{mutation_lines}

You are processing breadth-first frontier {frontier_index}.
Update only this affected block: {block_id}
Reason this block is affected: {reason_text}

Current block text:
```text
{current_text}
```

Changed or relevant upstream blocks:
{upstream_text}

Task:
- Rewrite only block {block_id} so it remains correct after the mutations.
- Preserve the block id unless the mutation explicitly requires a different id.
- Keep the same parseable semi-formal format: check_type, variables, hypotheses, allowed_references, and conclusion for claims.
- If an upstream block was removed, remove or replace any invalid allowed_references to it.
- If an upstream block was modified or added, update hypotheses, instantiations, allowed_references, and conclusion as needed.
- Do not silently use a claim in hypotheses unless it is listed in allowed_references, and do not list unused allowed_references.
- Return only the revised block text. If no edit is needed, return exactly: NO CHANGE NEEDED
"""

    def _format_reason_blocks(self, plan: MutationImpactPlan, reasons: tuple[str, ...]) -> str:
        sections: list[str] = []
        mutation_by_target = {mutation.target: mutation for mutation in plan.mutations if mutation.target}

        for reason in reasons:
            mutation = mutation_by_target.get(reason)
            if mutation is not None and mutation.new_text:
                sections.append(f"### {reason} ({mutation.kind}, proposed text)\n```text\n{mutation.new_text}\n```")
                continue

            try:
                text = self.graph.block_text(reason)
            except KeyError:
                text = ""
            if text:
                sections.append(f"### {reason}\n```text\n{text}\n```")
            else:
                sections.append(f"### {reason}\nNo current text is available for this block.")

        if sections:
            return "\n\n".join(sections)
        return "No specific upstream block was identified; use the mutation summary above."


def _describe_mutation(mutation: ProofMutation) -> str:
    target = mutation.target or "(no target)"
    summary = f": {mutation.summary}" if mutation.summary else ""
    affected = ""
    if mutation.affected_blocks:
        affected = f" Explicitly affected blocks: {', '.join(mutation.affected_blocks)}."
    propagation = "" if mutation.propagate_downstream else " Do not update downstream blocks."
    return f"{mutation.kind} {target}{summary}{affected}{propagation}"


def _dedupe_preserving_order(items: Iterable[str]) -> tuple[str, ...]:
    seen: set[str] = set()
    result: list[str] = []
    for item in items:
        if item in seen:
            continue
        seen.add(item)
        result.append(item)
    return tuple(result)
