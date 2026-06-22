import unittest

from src.proof_fuzzer.vllm_client import (
    VLLMProofFuzzerClient,
    build_gpt_oss_reasoning_messages,
)


class FakeMessage:
    content = "final answer"
    reasoning_content = "hidden reasoning"


class FakeChoice:
    message = FakeMessage()


class FakeResponse:
    choices = [FakeChoice()]


class FakeCompletions:
    def __init__(self):
        self.kwargs = None

    def create(self, **kwargs):
        self.kwargs = kwargs
        return FakeResponse()


class FakeChat:
    def __init__(self):
        self.completions = FakeCompletions()


class FakeOpenAIClient:
    def __init__(self):
        self.chat = FakeChat()


class VLLMClientTest(unittest.TestCase):
    def test_build_gpt_oss_messages_adds_reasoning_system_prompt(self) -> None:
        messages = build_gpt_oss_reasoning_messages(
            [{"role": "user", "content": "Mutate this proof."}],
            reasoning_effort="high",
        )

        self.assertEqual(messages[0]["role"], "system")
        self.assertTrue(messages[0]["content"].startswith("Reasoning: high"))
        self.assertEqual(messages[1]["role"], "user")

    def test_existing_system_prompt_has_reasoning_replaced(self) -> None:
        messages = build_gpt_oss_reasoning_messages(
            [
                {"role": "system", "content": "Reasoning: low\nBe terse."},
                {"role": "user", "content": "Hello"},
            ],
            reasoning_effort="medium",
            system_prompt="Use JSON.",
        )

        self.assertEqual(messages[0]["content"], "Reasoning: medium\nBe terse.\nUse JSON.")

    def test_client_sends_reasoning_effort_and_extracts_reasoning(self) -> None:
        fake_client = FakeOpenAIClient()
        client = VLLMProofFuzzerClient(client=fake_client, reasoning_effort="high")

        result = client.chat([{"role": "user", "content": "Hello"}])

        kwargs = fake_client.chat.completions.kwargs
        self.assertEqual(kwargs["reasoning_effort"], "high")
        self.assertIn("Reasoning: high", kwargs["messages"][0]["content"])
        self.assertEqual(result.content, "final answer")
        self.assertEqual(result.reasoning, "hidden reasoning")

    def test_complete_with_reasoning_tracks_last_result(self) -> None:
        fake_client = FakeOpenAIClient()
        client = VLLMProofFuzzerClient(client=fake_client, reasoning_effort="high")

        result = client.complete_with_reasoning("Hello")

        self.assertEqual(result.content, "final answer")
        self.assertEqual(result.reasoning, "hidden reasoning")
        self.assertIs(client.last_result, result)
        self.assertEqual(client.last_reasoning, "hidden reasoning")


if __name__ == "__main__":
    unittest.main()
