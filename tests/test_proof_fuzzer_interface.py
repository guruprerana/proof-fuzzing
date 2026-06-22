from pathlib import Path
import tempfile
import unittest

from src.proof_fuzzer import (
    LLMCompletionTrace,
    NaturalLanguageProofFuzzerLLMInterface,
    ProofFuzzerLLMInterface,
    SemiFormalProofFuzzerLLMInterface,
    parse_block_update_response,
    parse_mutation_instructions,
    split_natural_language_proof,
)
from src.semi_formalization.parser import parse_text
from src.semi_formalization.proof_graph import ProofGraph


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


class FakeLLM:
    def __init__(self, responses):
        self.responses = list(responses)
        self.prompts = []

    def complete(self, prompt: str) -> str:
        self.prompts.append(prompt)
        if not self.responses:
            raise AssertionError("No fake LLM response is available.")
        return self.responses.pop(0)


class FakeReasoningLLM:
    def __init__(self, responses):
        self.responses = list(responses)
        self.prompts = []

    def complete_with_reasoning(self, prompt: str) -> LLMCompletionTrace:
        self.prompts.append(prompt)
        if not self.responses:
            raise AssertionError("No fake LLM response is available.")
        response, reasoning = self.responses.pop(0)
        return LLMCompletionTrace(response=response, reasoning=reasoning)


class ProofFuzzerInterfaceTest(unittest.TestCase):
    def test_legacy_interface_name_is_semiformal_fuzzer(self) -> None:
        self.assertIs(ProofFuzzerLLMInterface, SemiFormalProofFuzzerLLMInterface)

    def test_parse_mutation_instructions_from_fenced_json(self) -> None:
        response = """```json
{
  "maintain_correctness": false,
  "rationale": "Create a deliberately false proof.",
  "mutations": [
    {
      "kind": "modify",
      "target": "C1",
      "summary": "Flip the sign conclusion.",
      "new_text": "claim C1:\\nconclusion:\\n  x is negative.",
      "affected_blocks": [],
      "propagate_downstream": false
    }
  ]
}
```"""

        instructions = parse_mutation_instructions(response)

        self.assertFalse(instructions.maintain_correctness)
        self.assertEqual(len(instructions.mutations), 1)
        self.assertEqual(instructions.mutations[0].target, "C1")
        self.assertFalse(instructions.mutations[0].propagate_downstream)

    def test_parse_mutation_instructions_accepts_missing_affected_blocks(self) -> None:
        response = """{
  "maintain_correctness": false,
  "mutations": [
    {
      "kind": "modify",
      "target": "C1",
      "summary": "Flip the conclusion.",
      "new_text": "claim C1:\\nconclusion:\\n  x is negative.",
      "propagate_downstream": false
    }
  ]
}"""

        instructions = parse_mutation_instructions(response)

        self.assertEqual(instructions.mutations[0].affected_blocks, ())

    def test_parse_mutation_instructions_normalizes_double_escaped_newlines(self) -> None:
        response = r"""{
  "maintain_correctness": false,
  "mutations": [
    {
      "kind": "modify",
      "target": "C1",
      "summary": "Flip the conclusion.",
      "new_text": "claim C1:\\nconclusion:\\n  x is negative.",
      "affected_blocks": "C2",
      "propagate_downstream": false
    }
  ]
}"""

        instructions = parse_mutation_instructions(response)

        self.assertIn("\nconclusion:", instructions.mutations[0].new_text)
        self.assertEqual(instructions.mutations[0].affected_blocks, ("C2",))

    def test_request_mutation_instructions_queries_llm(self) -> None:
        graph = ProofGraph(parse_text(CHAIN_ARTIFACT))
        llm = FakeLLM(
            [
                """{
  "maintain_correctness": true,
  "rationale": "Strengthen the first claim.",
  "mutations": [
    {
      "kind": "modify",
      "target": "C1",
      "summary": "Strengthen C1.",
      "new_text": "claim C1:\\nconclusion:\\n  x is strictly positive.",
      "affected_blocks": [],
      "propagate_downstream": true
    }
  ]
}"""
            ]
        )
        interface = ProofFuzzerLLMInterface(graph, llm)

        instructions = interface.request_mutation_instructions(objective="Try a small correctness-preserving edit.")

        self.assertTrue(instructions.maintain_correctness)
        self.assertIn("Available block ids", llm.prompts[0])
        self.assertIn("incorrect-proof mutation", llm.prompts[0])
        self.assertIn("correctness-preserving mutation", llm.prompts[0])
        self.assertIn("Prefer meaningful mathematical mutations over surface edits", llm.prompts[0])
        self.assertEqual(instructions.mutations[0].kind, "modify")

    def test_request_mutation_instructions_logs_prompt_reasoning_and_response(self) -> None:
        graph = ProofGraph(parse_text(CHAIN_ARTIFACT))
        response = """{
  "maintain_correctness": false,
  "rationale": "Make a subtle false proof.",
  "mutations": [
    {
      "kind": "modify",
      "target": "C1",
      "summary": "Flip the sign.",
      "new_text": "claim C1:\\nconclusion:\\n  x is negative.",
      "affected_blocks": [],
      "propagate_downstream": false
    }
  ]
}"""
        llm = FakeReasoningLLM([(response, "I should make a local contradiction.")])

        with tempfile.TemporaryDirectory() as tmp_dir:
            interface = ProofFuzzerLLMInterface(graph, llm, log_dir=tmp_dir)
            interface.request_false_proof_mutation_instructions()

            call_dirs = sorted(Path(tmp_dir).iterdir())
            self.assertEqual(len(call_dirs), 1)
            self.assertTrue((call_dirs[0] / "prompt.txt").is_file())
            self.assertTrue((call_dirs[0] / "reasoning_tokens.txt").is_file())
            self.assertTrue((call_dirs[0] / "response.txt").is_file())
            self.assertIn("maintain_correctness must be exactly false", (call_dirs[0] / "prompt.txt").read_text())
            self.assertEqual((call_dirs[0] / "reasoning_tokens.txt").read_text(), "I should make a local contradiction.")
            self.assertEqual((call_dirs[0] / "response.txt").read_text(), response)

    def test_request_correctness_preserving_mutation_instructions_fixes_target(self) -> None:
        graph = ProofGraph(parse_text(CHAIN_ARTIFACT))
        llm = FakeLLM(
            [
                """{
  "maintain_correctness": true,
  "rationale": "Keep the proof true.",
  "mutations": [
    {
      "kind": "modify",
      "target": "C1",
      "summary": "Strengthen C1.",
      "new_text": "claim C1:\\nconclusion:\\n  x is strictly positive.",
      "affected_blocks": [],
      "propagate_downstream": true
    }
  ]
}"""
            ]
        )
        interface = ProofFuzzerLLMInterface(graph, llm)

        instructions = interface.request_correctness_preserving_mutation_instructions()

        self.assertTrue(instructions.maintain_correctness)
        self.assertIn("maintain_correctness must be exactly true", llm.prompts[0])
        self.assertIn("trick an LLM judge into thinking the proof is incorrect", llm.prompts[0])
        self.assertIn("alternative valid lemmas", llm.prompts[0])
        self.assertNotIn("Choose whether", llm.prompts[0])

    def test_request_false_proof_mutation_instructions_fixes_target(self) -> None:
        graph = ProofGraph(parse_text(CHAIN_ARTIFACT))
        llm = FakeLLM(
            [
                """{
  "maintain_correctness": false,
  "rationale": "Make a small false mutation.",
  "mutations": [
    {
      "kind": "modify",
      "target": "C1",
      "summary": "Flip the sign.",
      "new_text": "claim C1:\\nconclusion:\\n  x is negative.",
      "affected_blocks": [],
      "propagate_downstream": false
    }
  ]
}"""
            ]
        )
        interface = ProofFuzzerLLMInterface(graph, llm)

        instructions = interface.request_false_proof_mutation_instructions()

        self.assertFalse(instructions.maintain_correctness)
        self.assertIn("maintain_correctness must be exactly false", llm.prompts[0])
        self.assertIn("trick an LLM judge into thinking the proof is correct", llm.prompts[0])
        self.assertIn("do not repair downstream blocks", llm.prompts[0])
        self.assertIn("proof-gap mutations", llm.prompts[0])

    def test_fixed_correctness_request_rejects_contradictory_response(self) -> None:
        graph = ProofGraph(parse_text(CHAIN_ARTIFACT))
        llm = FakeLLM(
            [
                """{
  "maintain_correctness": true,
  "mutations": [
    {
      "kind": "modify",
      "target": "C1",
      "summary": "Contradicts the requested false-proof target.",
      "new_text": "claim C1:\\nconclusion:\\n  x is positive.",
      "affected_blocks": [],
      "propagate_downstream": true
    }
  ]
}"""
            ]
        )
        interface = ProofFuzzerLLMInterface(graph, llm)

        with self.assertRaisesRegex(ValueError, "fixed correctness target"):
            interface.request_false_proof_mutation_instructions()

    def test_validate_mutation_instructions_rejects_unknown_target(self) -> None:
        graph = ProofGraph(parse_text(CHAIN_ARTIFACT))
        interface = ProofFuzzerLLMInterface(graph)
        instructions = parse_mutation_instructions(
            """{
  "maintain_correctness": true,
  "mutations": [
    {
      "kind": "modify",
      "target": "C99",
      "summary": "Unknown block.",
      "new_text": "claim C99:\\nconclusion:\\n  done.",
      "affected_blocks": [],
      "propagate_downstream": true
    }
  ]
}"""
        )

        issues = interface.validate_mutation_instructions(instructions)

        self.assertTrue(any("Unknown target block" in issue.message for issue in issues))

    def test_validate_mutation_instructions_rejects_mismatched_new_text_id(self) -> None:
        graph = ProofGraph(parse_text(CHAIN_ARTIFACT))
        interface = ProofFuzzerLLMInterface(graph)
        instructions = parse_mutation_instructions(
            """{
  "maintain_correctness": true,
  "mutations": [
    {
      "kind": "modify",
      "target": "C1",
      "summary": "Wrong replacement id.",
      "new_text": "claim C2:\\nconclusion:\\n  x is positive.",
      "affected_blocks": [],
      "propagate_downstream": true
    }
  ]
}"""
        )

        issues = interface.validate_mutation_instructions(instructions)

        self.assertTrue(any("does not define the target block" in issue.message for issue in issues))

    def test_false_mutation_does_not_create_successor_update_workflow(self) -> None:
        graph = ProofGraph(parse_text(CHAIN_ARTIFACT))
        interface = ProofFuzzerLLMInterface(graph)
        instructions = parse_mutation_instructions(
            """{
  "maintain_correctness": false,
  "mutations": [
    {
      "kind": "modify",
      "target": "C1",
      "summary": "Make C1 false.",
      "new_text": "claim C1:\\nconclusion:\\n  x is negative.",
      "affected_blocks": [],
      "propagate_downstream": false
    }
  ]
}"""
        )

        workflow = interface.build_successor_update_workflow(instructions)

        self.assertFalse(workflow.active)
        self.assertEqual(interface.current_update_prompts(workflow), ())

    def test_conditional_correctness_workflow_advances_only_after_actual_change(self) -> None:
        graph = ProofGraph(parse_text(CHAIN_ARTIFACT))
        interface = ProofFuzzerLLMInterface(graph, propagation_mode="conditional")
        instructions = parse_mutation_instructions(
            """{
  "maintain_correctness": true,
  "mutations": [
    {
      "kind": "modify",
      "target": "C1",
      "summary": "Change C1.",
      "new_text": "claim C1:\\nconclusion:\\n  x is strictly positive.",
      "affected_blocks": [],
      "propagate_downstream": true
    }
  ]
}"""
        )

        workflow = interface.build_successor_update_workflow(instructions)
        prompts = interface.current_update_prompts(workflow)
        self.assertEqual([prompt.block_id for prompt in prompts], ["C2"])

        workflow = interface.advance_conditional_workflow(workflow, [parse_block_update_response("C2", "NO CHANGE NEEDED")])
        self.assertFalse(workflow.active)

        workflow = interface.build_successor_update_workflow(instructions)
        changed = parse_block_update_response("C2", "claim C2:\nconclusion:\n  x is nonzero.")
        workflow = interface.advance_conditional_workflow(workflow, [changed])
        self.assertEqual([prompt.block_id for prompt in interface.current_update_prompts(workflow)], ["C3"])

    def test_query_current_updates_logs_each_successor_prompt(self) -> None:
        graph = ProofGraph(parse_text(CHAIN_ARTIFACT))
        llm = FakeReasoningLLM([("NO CHANGE NEEDED", "C2 still works.")])
        instructions = parse_mutation_instructions(
            """{
  "maintain_correctness": true,
  "mutations": [
    {
      "kind": "modify",
      "target": "C1",
      "summary": "Change C1.",
      "new_text": "claim C1:\\nconclusion:\\n  x is strictly positive.",
      "affected_blocks": [],
      "propagate_downstream": true
    }
  ]
}"""
        )

        with tempfile.TemporaryDirectory() as tmp_dir:
            interface = ProofFuzzerLLMInterface(graph, llm, propagation_mode="conditional", log_dir=tmp_dir)
            workflow = interface.build_successor_update_workflow(instructions)
            results = interface.query_current_updates(workflow)

            self.assertEqual(len(results), 1)
            call_dirs = sorted(Path(tmp_dir).iterdir())
            self.assertEqual(len(call_dirs), 1)
            self.assertIn("Update only this affected block: C2", (call_dirs[0] / "prompt.txt").read_text())
            self.assertEqual((call_dirs[0] / "reasoning_tokens.txt").read_text(), "C2 still works.")
            self.assertEqual((call_dirs[0] / "response.txt").read_text(), "NO CHANGE NEEDED")

    def test_naive_correctness_workflow_prompts_all_successors(self) -> None:
        graph = ProofGraph(parse_text(CHAIN_ARTIFACT))
        interface = ProofFuzzerLLMInterface(graph, propagation_mode="naive")
        instructions = parse_mutation_instructions(
            """{
  "maintain_correctness": true,
  "mutations": [
    {
      "kind": "modify",
      "target": "C1",
      "summary": "Change C1.",
      "new_text": "claim C1:\\nconclusion:\\n  x is strictly positive.",
      "affected_blocks": [],
      "propagate_downstream": true
    }
  ]
}"""
        )

        workflow = interface.build_successor_update_workflow(instructions)
        prompts = interface.current_update_prompts(workflow)

        self.assertEqual([prompt.block_id for prompt in prompts], ["C2", "C3"])

    def test_parse_block_update_response_handles_fenced_text(self) -> None:
        result = parse_block_update_response("C2", "```text\nclaim C2:\nconclusion:\n  done.\n```")

        self.assertTrue(result.changed)
        self.assertEqual(result.revised_text, "claim C2:\nconclusion:\n  done.")

    def test_split_natural_language_proof_creates_targetable_segments(self) -> None:
        proof = "First, let n be even.\n\nThen n = 2k for some integer k.\n\nThus n^2 is even."

        segments = split_natural_language_proof(proof)

        self.assertEqual([segment.segment_id for segment in segments], ["S1", "S2", "S3"])
        self.assertEqual(segments[1].text, "Then n = 2k for some integer k.")

    def test_natural_language_fuzzer_requests_direct_mutation(self) -> None:
        proof = "Let n be even.\n\nThen n = 2k.\n\nTherefore n^2 is even."
        llm = FakeLLM(
            [
                """{
  "maintain_correctness": false,
  "rationale": "Introduce a plausible algebraic gap.",
  "mutations": [
    {
      "kind": "modify",
      "target": "S2",
      "summary": "Use an unsupported representation.",
      "new_text": "Then n = 2k + 1 for some integer k.",
      "affected_blocks": [],
      "propagate_downstream": false
    }
  ]
}"""
            ]
        )
        interface = NaturalLanguageProofFuzzerLLMInterface(proof, llm)

        instructions = interface.request_false_proof_mutation_instructions()

        self.assertFalse(instructions.maintain_correctness)
        self.assertEqual(instructions.mutations[0].target, "S2")
        self.assertIn("natural-language mathematical proof", llm.prompts[0])
        self.assertIn("### S2", llm.prompts[0])
        self.assertIn("maintain_correctness must be exactly false", llm.prompts[0])
        self.assertNotIn("semi-formalized", llm.prompts[0])

    def test_natural_language_fuzzer_applies_text_mutations(self) -> None:
        proof = "Step one.\n\nStep two.\n\nStep three."
        interface = NaturalLanguageProofFuzzerLLMInterface(proof)
        instructions = parse_mutation_instructions(
            """{
  "maintain_correctness": false,
  "mutations": [
    {
      "kind": "modify",
      "target": "S2",
      "summary": "Change the middle step.",
      "new_text": "Mutated step two.",
      "affected_blocks": [],
      "propagate_downstream": false
    },
    {
      "kind": "add",
      "target": "after:S2",
      "summary": "Insert a hidden assumption.",
      "new_text": "Assume the desired conclusion.",
      "affected_blocks": [],
      "propagate_downstream": false
    },
    {
      "kind": "remove",
      "target": "S1",
      "summary": "Remove setup.",
      "new_text": "",
      "affected_blocks": [],
      "propagate_downstream": false
    }
  ]
}"""
        )

        mutated = interface.apply_mutations(instructions)

        self.assertEqual(mutated, "Mutated step two.\n\nAssume the desired conclusion.\n\nStep three.")

    def test_natural_language_fuzzer_rejects_unknown_segment(self) -> None:
        proof = "Step one.\n\nStep two."
        interface = NaturalLanguageProofFuzzerLLMInterface(proof)
        instructions = parse_mutation_instructions(
            """{
  "maintain_correctness": false,
  "mutations": [
    {
      "kind": "modify",
      "target": "S99",
      "summary": "Unknown step.",
      "new_text": "Replacement.",
      "affected_blocks": [],
      "propagate_downstream": false
    }
  ]
}"""
        )

        issues = interface.validate_mutation_instructions(instructions)

        self.assertTrue(any("Unknown natural-language proof segment" in issue.message for issue in issues))


if __name__ == "__main__":
    unittest.main()
