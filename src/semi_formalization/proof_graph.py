"""Dependency graph and update planning for semi-formalized proofs."""

from __future__ import annotations

from collections import defaultdict, deque
from dataclasses import dataclass
from typing import Iterable

from .parser import Claim, LemmaModule, SemiFormalProof


GLOBAL_CONTEXT = "global_context"


@dataclass(frozen=True)
class UpdatePlan:
    """Breadth-first update plan after one or more proof blocks change."""

    changed: tuple[str, ...]
    frontiers: tuple[tuple[str, ...], ...]
    reasons: dict[str, tuple[str, ...]]

    @property
    def impacted(self) -> tuple[str, ...]:
        return tuple(block for frontier in self.frontiers for block in frontier)

    def to_dict(self) -> dict[str, object]:
        return {
            "changed": list(self.changed),
            "frontiers": [list(frontier) for frontier in self.frontiers],
            "impacted": list(self.impacted),
            "reasons": {block: list(reasons) for block, reasons in self.reasons.items()},
        }


class ProofGraph:
    """A syntactic dependency graph built from ``allowed_references``.

    Edges point from dependency to dependent. For example, if ``C7`` has
    ``allowed_references`` containing ``C3``, then ``C3 -> C7``.

    Global context is intentionally conservative: changing it marks every
    parsed block as impacted.
    """

    def __init__(self, proof: SemiFormalProof):
        self.proof = proof
        self.nodes: tuple[str, ...] = self._collect_nodes(proof)
        self.node_kinds: dict[str, str] = self._collect_node_kinds(proof)
        self.document_order: dict[str, int] = {node: i for i, node in enumerate(self.nodes)}
        self.dependencies: dict[str, set[str]] = {node: set() for node in self.nodes}
        self.reverse_dependencies: dict[str, set[str]] = {node: set() for node in self.nodes}
        self.lemma_aliases: dict[str, tuple[str, ...]] = self._collect_lemma_aliases(proof)
        self._build_edges()

    @classmethod
    def from_proof(cls, proof: SemiFormalProof) -> "ProofGraph":
        return cls(proof)

    def dependents(self, block_id: str) -> tuple[str, ...]:
        """Return direct dependents of ``block_id`` in document order."""

        seeds = self.normalize_block_ids([block_id])
        direct: set[str] = set()
        for seed in seeds:
            if seed == GLOBAL_CONTEXT:
                direct.update(self.nodes)
            else:
                direct.update(self.reverse_dependencies.get(seed, set()))
        return self.sort_nodes(direct)

    def impact_frontiers(
        self,
        changed: Iterable[str],
        *,
        include_changed: bool = False,
    ) -> tuple[tuple[str, ...], ...]:
        """Return breadth-first frontiers of blocks impacted by ``changed``.

        If ``global_context`` is changed, all parsed blocks are returned as a
        single frontier unless ``include_changed`` is true, in which case the
        first frontier is ``("global_context",)`` and the second is all blocks.
        """

        seeds = self.normalize_block_ids(changed)
        if not seeds:
            return ()

        if GLOBAL_CONTEXT in seeds:
            all_blocks = self.sort_nodes(self.nodes)
            if include_changed:
                return ((GLOBAL_CONTEXT,), all_blocks)
            return (all_blocks,)

        seen = set(seeds)
        queue: deque[tuple[str, int]] = deque((seed, 0) for seed in seeds)
        levels: dict[int, set[str]] = defaultdict(set)

        if include_changed:
            levels[0].update(seeds)

        while queue:
            current, depth = queue.popleft()
            for dependent in self.sort_nodes(self.reverse_dependencies.get(current, set())):
                if dependent in seen:
                    continue
                seen.add(dependent)
                next_depth = depth + 1
                levels[next_depth].add(dependent)
                queue.append((dependent, next_depth))

        return tuple(
            self.sort_nodes(levels[level])
            for level in sorted(levels)
            if levels[level]
        )

    def impacted_blocks(
        self,
        changed: Iterable[str],
        *,
        include_changed: bool = False,
    ) -> tuple[str, ...]:
        """Return a flattened breadth-first impact order."""

        return tuple(
            block
            for frontier in self.impact_frontiers(changed, include_changed=include_changed)
            for block in frontier
        )

    def plan_update(
        self,
        changed: Iterable[str],
        *,
        include_changed: bool = False,
    ) -> UpdatePlan:
        """Return an ``UpdatePlan`` with BFS frontiers and reason edges."""

        seeds = self.normalize_block_ids(changed)
        frontiers = self.impact_frontiers(seeds, include_changed=include_changed)
        impacted = {block for frontier in frontiers for block in frontier}
        reasons: dict[str, tuple[str, ...]] = {}

        for block in impacted:
            if block == GLOBAL_CONTEXT:
                reasons[block] = ()
                continue
            if GLOBAL_CONTEXT in seeds:
                reasons[block] = (GLOBAL_CONTEXT,)
                continue
            parents = self.dependencies.get(block, set()) & (set(seeds) | impacted)
            reasons[block] = self.sort_nodes(parents)

        return UpdatePlan(changed=seeds, frontiers=frontiers, reasons=reasons)

    def block_text(self, block_id: str) -> str:
        """Return the parseable text for an existing proof block."""

        canonical = self.canonical_block_id(block_id)
        if canonical == GLOBAL_CONTEXT:
            return _format_section("global context", self.proof.global_context)

        claim = self.proof.claim_map().get(canonical)
        if claim is not None:
            return claim.raw_text or _format_claim(claim)

        statement = self._statement_text(canonical)
        if statement:
            return statement

        lemma = self.proof.lemma_map().get(canonical)
        if lemma is not None:
            return lemma.raw_text

        raise KeyError(f"Unknown proof block id: {block_id}")

    def normalize_block_ids(self, changed: Iterable[str]) -> tuple[str, ...]:
        normalized: list[str] = []
        for block_id in changed:
            canonical = self.canonical_block_id(block_id)
            if canonical == GLOBAL_CONTEXT:
                normalized.append(GLOBAL_CONTEXT)
                continue
            if canonical in self.lemma_aliases:
                normalized.extend(self.lemma_aliases[canonical])
                continue
            if canonical not in self.node_kinds:
                raise KeyError(f"Unknown proof block id: {block_id}")
            normalized.append(canonical)
        return _dedupe_preserving_order(normalized)

    def canonical_block_id(self, block_id: str) -> str:
        stripped = block_id.strip()
        lowered = stripped.lower().replace(" ", "_")
        if lowered in {"global_context", "global", "__global_context__"}:
            return GLOBAL_CONTEXT
        return stripped.rstrip(".")

    def sort_nodes(self, nodes: Iterable[str]) -> tuple[str, ...]:
        return tuple(
            sorted(
                nodes,
                key=lambda node: self.document_order.get(node, len(self.document_order) + 1),
            )
        )

    def sort_reason_ids(self, reason_ids: Iterable[str]) -> tuple[str, ...]:
        return tuple(
            sorted(
                reason_ids,
                key=lambda reason: (
                    self.document_order.get(reason, len(self.document_order) + 1),
                    reason,
                ),
            )
        )

    def _build_edges(self) -> None:
        for lemma in self.proof.lemmas:
            for claim in lemma.proof_claims:
                for ref in claim.allowed_references:
                    self._add_edge(ref.ref, claim.claim_id)

            final_claim = self._lemma_final_claim(lemma)
            if final_claim is not None:
                for statement_id in self._lemma_statement_ids(lemma):
                    self._add_edge(final_claim.claim_id, statement_id)

        for claim in self.proof.claims:
            for ref in claim.allowed_references:
                self._add_edge(ref.ref, claim.claim_id)

    def _add_edge(self, dependency: str, dependent: str) -> None:
        if dependent not in self.dependencies:
            return
        self.dependencies[dependent].add(dependency)
        self.reverse_dependencies.setdefault(dependency, set()).add(dependent)

    def _statement_text(self, statement_id: str) -> str:
        for lemma in self.proof.lemmas:
            statement_ids = self._lemma_statement_ids(lemma)
            if statement_id not in statement_ids:
                continue
            return _format_section(f"{statement_id}", lemma.statement)
        return ""

    @staticmethod
    def _collect_nodes(proof: SemiFormalProof) -> tuple[str, ...]:
        nodes: list[str] = []
        for lemma in proof.lemmas:
            nodes.extend(claim.claim_id for claim in lemma.proof_claims)
            nodes.extend(ProofGraph._lemma_statement_ids(lemma))
        nodes.extend(claim.claim_id for claim in proof.claims)
        return _dedupe_preserving_order(nodes)

    @staticmethod
    def _collect_node_kinds(proof: SemiFormalProof) -> dict[str, str]:
        kinds: dict[str, str] = {}
        for lemma in proof.lemmas:
            for claim in lemma.proof_claims:
                kinds[claim.claim_id] = "lemma_claim"
            for statement_id in ProofGraph._lemma_statement_ids(lemma):
                kinds[statement_id] = "lemma_statement"
        for claim in proof.claims:
            kinds[claim.claim_id] = "claim"
        return kinds

    @staticmethod
    def _collect_lemma_aliases(proof: SemiFormalProof) -> dict[str, tuple[str, ...]]:
        aliases: dict[str, tuple[str, ...]] = {}
        for lemma in proof.lemmas:
            block_ids = [claim.claim_id for claim in lemma.proof_claims]
            block_ids.extend(ProofGraph._lemma_statement_ids(lemma))
            aliases[lemma.lemma_id] = _dedupe_preserving_order(block_ids)
        return aliases

    @staticmethod
    def _lemma_statement_ids(lemma: LemmaModule) -> tuple[str, ...]:
        exports = [export.rstrip(".") for export in lemma.exports if export.rstrip(".")]
        if exports:
            return _dedupe_preserving_order(exports)

        prefix = lemma.lemma_id.split("_", 1)[0]
        return (f"{prefix}.statement",)

    @staticmethod
    def _lemma_final_claim(lemma: LemmaModule):
        for claim in lemma.proof_claims:
            if claim.claim_id.endswith(".final"):
                return claim
        if lemma.proof_claims:
            return lemma.proof_claims[-1]
        return None


def _dedupe_preserving_order(items: Iterable[str]) -> tuple[str, ...]:
    seen: set[str] = set()
    result: list[str] = []
    for item in items:
        if item in seen:
            continue
        seen.add(item)
        result.append(item)
    return tuple(result)


def _format_section(name: str, lines: Iterable[str]) -> str:
    content = tuple(lines)
    if not content:
        return f"{name}:\n  none"
    return "\n".join([f"{name}:"] + [f"  {line}" for line in content])


def _format_claim(claim: Claim) -> str:
    lines = [f"claim {claim.claim_id}:"]
    lines.extend(_format_field("check_type", (claim.check_type or "unspecified",)))
    lines.extend(_format_field("variables", claim.variables))
    lines.extend(_format_field("hypotheses", claim.hypotheses))
    lines.append("allowed_references:")
    if claim.allowed_references:
        for ref in claim.allowed_references:
            lines.append(f"  - ref: {ref.ref}")
            if ref.instantiation:
                lines.append(f"    instantiation: {ref.instantiation}")
    else:
        lines.append("  none")
    lines.extend(_format_field("conclusion", claim.conclusion))
    return "\n".join(lines)


def _format_field(name: str, values: Iterable[str]) -> list[str]:
    value_tuple = tuple(values)
    lines = [f"{name}:"]
    if value_tuple:
        lines.extend(f"  {value}" for value in value_tuple)
    else:
        lines.append("  none")
    return lines
