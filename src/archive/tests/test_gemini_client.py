import unittest

from src.proof_fuzzer.gemini_client import (
    DEFAULT_GEMINI_MODEL,
    DEFAULT_GEMINI_THINKING_LEVEL,
    GeminiProofFuzzerClient,
)


class FakeContentBlock:
    type = "text"

    def __init__(self, text: str):
        self.text = text


class FakeThoughtStep:
    type = "thought"
    summary = [FakeContentBlock("private thought summary")]


class FakeModelOutputStep:
    type = "model_output"
    content = [FakeContentBlock("final answer")]


class FakeInteraction:
    output_text = "final answer"
    steps = [FakeThoughtStep(), FakeModelOutputStep()]
    status = "completed"


class FakeInteractions:
    def __init__(self):
        self.kwargs = None

    def create(self, **kwargs):
        self.kwargs = kwargs
        return FakeInteraction()


class FakeGeminiClient:
    def __init__(self):
        self.interactions = FakeInteractions()


class GeminiClientTest(unittest.TestCase):
    def test_complete_with_reasoning_sends_interaction_config_and_extracts_thoughts(self) -> None:
        fake_client = FakeGeminiClient()
        client = GeminiProofFuzzerClient(
            client=fake_client,
            model="gemini-test",
            max_tokens=123,
            temperature=0.2,
            thinking_level="low",
        )

        result = client.complete_with_reasoning("Hello")

        kwargs = fake_client.interactions.kwargs
        self.assertEqual(kwargs["model"], "gemini-test")
        self.assertEqual(kwargs["input"], "Hello")
        self.assertEqual(kwargs["generation_config"]["max_output_tokens"], 123)
        self.assertEqual(kwargs["generation_config"]["temperature"], 0.2)
        self.assertEqual(kwargs["generation_config"]["thinking_level"], "low")
        self.assertEqual(kwargs["generation_config"]["thinking_summaries"], "auto")
        self.assertEqual(result.content, "final answer")
        self.assertEqual(result.reasoning, "private thought summary")
        self.assertEqual(result.finish_reason, "completed")
        self.assertIs(client.last_result, result)
        self.assertEqual(client.last_reasoning, "private thought summary")

    def test_defaults_use_gemini_flash_with_medium_thinking(self) -> None:
        fake_client = FakeGeminiClient()
        client = GeminiProofFuzzerClient(client=fake_client)

        client.complete("Hello")

        kwargs = fake_client.interactions.kwargs
        self.assertEqual(kwargs["model"], DEFAULT_GEMINI_MODEL)
        self.assertEqual(DEFAULT_GEMINI_MODEL, "gemini-3.5-flash")
        self.assertEqual(kwargs["generation_config"]["thinking_level"], DEFAULT_GEMINI_THINKING_LEVEL)
        self.assertEqual(DEFAULT_GEMINI_THINKING_LEVEL, "medium")

    def test_chat_flattens_messages(self) -> None:
        fake_client = FakeGeminiClient()
        client = GeminiProofFuzzerClient(client=fake_client)

        client.chat(
            [
                {"role": "system", "content": "Use JSON."},
                {"role": "user", "content": "Mutate this proof."},
            ]
        )

        prompt = fake_client.interactions.kwargs["input"]
        self.assertIn("SYSTEM:\nUse JSON.", prompt)
        self.assertIn("USER:\nMutate this proof.", prompt)


if __name__ == "__main__":
    unittest.main()
