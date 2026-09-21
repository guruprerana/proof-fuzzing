from pathlib import Path
import unittest

from src.archive.semi_formalization.mutation import MutationPlanner, ProofMutation
from src.archive.semi_formalization.parser import parse_file, parse_text, validate_references
from src.archive.semi_formalization.proof_graph import GLOBAL_CONTEXT, ProofGraph


SIMPLE_ARTIFACT = """global context:
  x is a real number.

claim C1:
check_type: definition
variables:
  none
hypotheses:
  x = 1.
allowed_references:
  none
conclusion:
  x is positive.

claim C2:
check_type: final assembly
variables:
  none
hypotheses:
  x = 1.
allowed_references:
  - ref: C1
    instantiation: current x
conclusion:
  The result follows.
"""


CHAIN_ARTIFACT = """global context:
  x is a real number.

claim C1:
check_type: definition
variables:
  none
hypotheses:
  x = 1.
allowed_references:
  none
conclusion:
  x is positive.

claim C2:
check_type: consequence
variables:
  none
hypotheses:
  x = 1.
allowed_references:
  - ref: C1
    instantiation: current x
conclusion:
  x is nonzero.

claim C3:
check_type: final assembly
variables:
  none
hypotheses:
  x = 1.
allowed_references:
  - ref: C2
    instantiation: current x
conclusion:
  The result follows.
"""


LEMMA_ARTIFACT = """global context:
  H is a tree.

lemma L1_tree:
  statement:
    Every tree has a vertex.
  dependencies:
    global context only.
  proof_claims:
    claim L1.C1:
      check_type: graph theory
      variables:
        H is a tree.
      hypotheses:
        H is nonempty.
      allowed_references:
        none
      conclusion:
        H has a vertex.

    claim L1.final:
      check_type: final assembly
      variables:
        H is a tree.
      hypotheses:
        H is nonempty.
      allowed_references:
        - ref: L1.C1
          instantiation: H = current H
      conclusion:
        Every tree has a vertex.
  exports:
    L1.statement.

main proof claims:
  claim C1:
    check_type: final assembly
    variables:
      H is a tree.
    hypotheses:
      H is nonempty.
    allowed_references:
      - ref: L1.statement
        instantiation: H = current H
    conclusion:
      H has a vertex.
"""


class SemiFormalizationParserTest(unittest.TestCase):
    def test_parse_simple_claims(self) -> None:
        proof = parse_text(SIMPLE_ARTIFACT)

        self.assertEqual(proof.global_context, ("x is a real number.",))
        self.assertEqual(len(proof.lemmas), 0)
        self.assertEqual([claim.claim_id for claim in proof.claims], ["C1", "C2"])
        self.assertEqual(proof.claims[0].allowed_references, ())
        self.assertEqual(proof.claims[1].allowed_references[0].ref, "C1")
        self.assertEqual(proof.claims[1].allowed_references[0].instantiation, "current x")
        self.assertEqual(validate_references(proof), [])

    def test_parse_lemma_and_exported_reference(self) -> None:
        proof = parse_text(LEMMA_ARTIFACT)

        self.assertEqual(len(proof.lemmas), 1)
        lemma = proof.lemmas[0]
        self.assertEqual(lemma.lemma_id, "L1_tree")
        self.assertEqual([claim.claim_id for claim in lemma.proof_claims], ["L1.C1", "L1.final"])
        self.assertEqual(lemma.exports, ("L1.statement.",))
        self.assertEqual(proof.claims[0].allowed_references[0].ref, "L1.statement")
        self.assertEqual(validate_references(proof), [])

    def test_unknown_reference_is_reported(self) -> None:
        artifact = SIMPLE_ARTIFACT.replace("- ref: C1", "- ref: C99")
        proof = parse_text(artifact)

        issues = validate_references(proof)
        self.assertEqual(len(issues), 1)
        self.assertIn("C99", issues[0].message)

    def test_parse_generated_artifact_when_available(self) -> None:
        path = Path("logs/archive/proof_semiformalization/imo_gradebench/000125/verification_autoformalization_parseable.txt")
        if not path.exists():
            self.skipTest("generated semi-formalization fixture is not available")

        proof = parse_file(path)
        self.assertGreaterEqual(len(proof.lemmas), 1)
        self.assertGreaterEqual(len(proof.claims), 1)
        self.assertIn("L1.statement", {ref.ref for claim in proof.claims for ref in claim.allowed_references})

    def test_proof_graph_orders_claim_updates_breadth_first(self) -> None:
        graph = ProofGraph(parse_text(SIMPLE_ARTIFACT))

        self.assertEqual(graph.dependents("C1"), ("C2",))
        self.assertEqual(graph.impact_frontiers(["C1"]), (("C2",),))

        plan = graph.plan_update(["C1"])
        self.assertEqual(plan.changed, ("C1",))
        self.assertEqual(plan.impacted, ("C2",))
        self.assertEqual(plan.reasons["C2"], ("C1",))
        self.assertEqual(
            plan.to_dict(),
            {
                "changed": ["C1"],
                "frontiers": [["C2"]],
                "impacted": ["C2"],
                "reasons": {"C2": ["C1"]},
            },
        )

    def test_proof_graph_propagates_lemma_internal_changes_to_exports(self) -> None:
        graph = ProofGraph(parse_text(LEMMA_ARTIFACT))

        self.assertEqual(
            graph.impact_frontiers(["L1.C1"]),
            (("L1.final",), ("L1.statement",), ("C1",)),
        )

        plan = graph.plan_update(["L1.C1"])
        self.assertEqual(plan.reasons["L1.final"], ("L1.C1",))
        self.assertEqual(plan.reasons["L1.statement"], ("L1.final",))
        self.assertEqual(plan.reasons["C1"], ("L1.statement",))

    def test_proof_graph_tracks_export_and_lemma_alias_updates(self) -> None:
        graph = ProofGraph(parse_text(LEMMA_ARTIFACT))

        self.assertEqual(graph.impact_frontiers(["L1.statement"]), (("C1",),))
        self.assertEqual(graph.impacted_blocks(["L1_tree"]), ("C1",))
        self.assertEqual(
            graph.impact_frontiers(["L1_tree"], include_changed=True),
            (("L1.C1", "L1.final", "L1.statement"), ("C1",)),
        )

    def test_proof_graph_treats_global_context_as_all_blocks(self) -> None:
        graph = ProofGraph(parse_text(LEMMA_ARTIFACT))

        self.assertEqual(
            graph.impact_frontiers([GLOBAL_CONTEXT]),
            (("L1.C1", "L1.final", "L1.statement", "C1"),),
        )
        self.assertEqual(
            graph.impact_frontiers(["global"], include_changed=True),
            ((GLOBAL_CONTEXT,), ("L1.C1", "L1.final", "L1.statement", "C1")),
        )
        self.assertEqual(graph.plan_update(["global"]).reasons["C1"], (GLOBAL_CONTEXT,))

    def test_proof_graph_rejects_unknown_changed_blocks(self) -> None:
        graph = ProofGraph(parse_text(SIMPLE_ARTIFACT))

        with self.assertRaises(KeyError):
            graph.impact_frontiers(["C99"])

    def test_mutation_plan_for_modified_claim_tracks_downstream_prompts(self) -> None:
        graph = ProofGraph(parse_text(SIMPLE_ARTIFACT))
        planner = MutationPlanner(graph)
        mutation = ProofMutation.modify(
            "C1",
            summary="Strengthen the conclusion to x is strictly positive.",
            new_text="claim C1:\nconclusion:\n  x is strictly positive.",
        )

        plan = planner.plan_mutations([mutation])
        self.assertEqual(plan.directly_changed, ("C1",))
        self.assertEqual(plan.frontiers, (("C2",),))
        self.assertEqual(plan.affected_blocks, ("C2",))
        self.assertEqual(plan.reasons["C2"], ("C1",))

        prompt = planner.mutation_update_prompts(plan)[0]
        self.assertEqual(prompt.block_id, "C2")
        self.assertIn("modify C1", prompt.prompt)
        self.assertIn("overall proof remains correct", prompt.prompt)
        self.assertIn("Update only this affected block: C2", prompt.prompt)
        self.assertIn("x is strictly positive", prompt.prompt)
        self.assertIn("Return only the revised block text", prompt.prompt)

    def test_mutation_plan_for_added_block_uses_explicit_affected_blocks(self) -> None:
        graph = ProofGraph(parse_text(LEMMA_ARTIFACT))
        planner = MutationPlanner(graph)
        mutation = ProofMutation.add(
            "L2.statement",
            summary="Add a sharper lemma that main claim C1 should use.",
            new_text="L2.statement:\n  H has a leaf.",
            affected_blocks=("C1",),
        )

        plan = planner.plan_mutations([mutation])
        self.assertEqual(plan.directly_changed, ())
        self.assertEqual(plan.frontiers, (("C1",),))
        self.assertEqual(plan.reasons["C1"], ("L2.statement",))

        prompt = planner.mutation_update_prompts(plan)[0]
        self.assertIn("add L2.statement", prompt.prompt)
        self.assertIn("L2.statement", prompt.prompt)
        self.assertIn("H has a leaf", prompt.prompt)

    def test_mutation_plan_can_include_direct_changes_as_first_frontier(self) -> None:
        graph = ProofGraph(parse_text(SIMPLE_ARTIFACT))
        planner = MutationPlanner(graph)
        mutation = ProofMutation.remove("C1", summary="Remove redundant claim C1.")

        plan = planner.plan_mutations([mutation], include_direct_changes=True)
        self.assertEqual(plan.frontiers, (("C1",), ("C2",)))
        self.assertEqual(plan.reasons["C2"], ("C1",))

    def test_mutation_can_disable_downstream_propagation(self) -> None:
        graph = ProofGraph(parse_text(SIMPLE_ARTIFACT))
        planner = MutationPlanner(graph)
        mutation = ProofMutation.modify(
            "C1",
            summary="Make C1 false without repairing dependent claims.",
            new_text="claim C1:\nconclusion:\n  x is negative.",
            propagate_downstream=False,
        )

        plan = planner.plan_mutations([mutation])
        self.assertEqual(plan.directly_changed, ("C1",))
        self.assertEqual(plan.frontiers, ())
        self.assertEqual(plan.affected_blocks, ())

    def test_non_propagating_mutation_can_prompt_only_the_direct_change(self) -> None:
        graph = ProofGraph(parse_text(SIMPLE_ARTIFACT))
        planner = MutationPlanner(graph)
        mutation = ProofMutation.modify(
            "C1",
            summary="Make C1 false without repairing dependent claims.",
            new_text="claim C1:\nconclusion:\n  x is negative.",
            propagate_downstream=False,
        )

        plan = planner.plan_mutations([mutation], include_direct_changes=True)
        self.assertEqual(plan.frontiers, (("C1",),))

        prompt = planner.mutation_update_prompts(plan)[0]
        self.assertEqual(prompt.block_id, "C1")
        self.assertIn("Do not update downstream blocks", prompt.prompt)
        self.assertNotIn("Update only this affected block: C2", prompt.prompt)

    def test_global_context_mutation_impacts_every_block(self) -> None:
        graph = ProofGraph(parse_text(LEMMA_ARTIFACT))
        planner = MutationPlanner(graph)
        mutation = ProofMutation.global_context(
            summary="Assume H is a finite tree.",
            new_text="global context:\n  H is a finite tree.",
        )

        plan = planner.plan_mutations([mutation])
        self.assertEqual(plan.directly_changed, (GLOBAL_CONTEXT,))
        self.assertEqual(plan.frontiers, (("L1.C1", "L1.final", "L1.statement", "C1"),))
        self.assertEqual(plan.reasons["L1.C1"], (GLOBAL_CONTEXT,))

    def test_progressive_mutation_stops_when_frontier_does_not_change(self) -> None:
        graph = ProofGraph(parse_text(CHAIN_ARTIFACT))
        planner = MutationPlanner(graph)
        mutation = ProofMutation.modify(
            "C1",
            summary="Change C1 and only continue if successors actually change.",
        )

        session = planner.start_progressive_mutations([mutation])
        self.assertEqual(session.current_frontier, ("C2",))
        self.assertEqual(session.reasons["C2"], ("C1",))
        self.assertFalse(session.done)

        stopped = session.advance([])
        self.assertEqual(stopped.current_frontier, ())
        self.assertTrue(stopped.done)
        self.assertEqual(stopped.affected_blocks, ("C2",))
        self.assertEqual(stopped.changed_blocks, ("C1",))

    def test_progressive_mutation_advances_only_from_actually_changed_blocks(self) -> None:
        graph = ProofGraph(parse_text(CHAIN_ARTIFACT))
        planner = MutationPlanner(graph)
        mutation = ProofMutation.modify("C1", summary="Change C1.")

        session = planner.start_progressive_mutations([mutation])
        self.assertEqual(session.current_prompts()[0].block_id, "C2")

        session = session.advance(["C2"])
        self.assertEqual(session.current_frontier, ("C3",))
        self.assertEqual(session.reasons["C3"], ("C2",))
        self.assertEqual(session.changed_blocks, ("C1", "C2"))

        done = planner.advance_progressive_session(session, [])
        self.assertEqual(done.current_frontier, ())
        self.assertEqual(done.affected_blocks, ("C2", "C3"))

    def test_progressive_mutation_can_wait_for_direct_change_result(self) -> None:
        graph = ProofGraph(parse_text(CHAIN_ARTIFACT))
        planner = MutationPlanner(graph)
        mutation = ProofMutation.modify(
            "C1",
            summary="Prompt the target first before deciding whether to propagate.",
        )

        session = planner.start_progressive_mutations([mutation], include_direct_changes=True)
        self.assertEqual(session.current_frontier, ("C1",))

        stopped = session.advance([])
        self.assertEqual(stopped.current_frontier, ())

        session = planner.start_progressive_mutations([mutation], include_direct_changes=True)
        continued = session.advance(["C1"])
        self.assertEqual(continued.current_frontier, ("C2",))


if __name__ == "__main__":
    unittest.main()
