import unittest

from src.proof_fuzzer.codex_client import CodexProofFuzzerClient


class FakeSDK:
    Codex = None
    CodexConfig = None
    Sandbox = None
    ApprovalMode = None


class FakeSandbox:
    read_only = "read-only"
    workspace_write = "workspace-write"
    full_access = "full-access"


class FakeApprovalMode:
    deny_all = "deny_all"
    auto_review = "auto_review"


class FakeCodexConfig:
    def __init__(self, *, cwd=None):
        self.cwd = cwd


class FakeTurnResult:
    final_response = "final answer"
    status = "completed"


class FakeThread:
    def __init__(self):
        self.run_kwargs = None
        self.prompt = None

    def run(self, prompt, **kwargs):
        self.prompt = prompt
        self.run_kwargs = kwargs
        return FakeTurnResult()


class FakeCodexContext:
    last_instance = None

    def __init__(self, config=None):
        self.config = config
        self.thread = FakeThread()
        self.thread_start_kwargs = None
        self.entered = False
        self.exited = False
        FakeCodexContext.last_instance = self

    def __enter__(self):
        self.entered = True
        return self

    def __exit__(self, exc_type, exc, tb):
        self.exited = True

    def thread_start(self, **kwargs):
        self.thread_start_kwargs = kwargs
        return self.thread


class CodexClientTest(unittest.TestCase):
    def setUp(self) -> None:
        FakeSDK.Codex = FakeCodexContext
        FakeSDK.CodexConfig = FakeCodexConfig
        FakeSDK.Sandbox = FakeSandbox
        FakeSDK.ApprovalMode = FakeApprovalMode

    def test_complete_runs_fresh_codex_thread_with_medium_effort(self) -> None:
        client = CodexProofFuzzerClient(
            model="gpt-5.5",
            reasoning_effort="medium",
            sandbox="read_only",
            cwd="/repo",
            codex_factory=FakeCodexContext,
            sdk=FakeSDK,
        )

        result = client.complete_with_reasoning("Hello")

        context = FakeCodexContext.last_instance
        self.assertIsNotNone(context)
        self.assertTrue(context.entered)
        self.assertTrue(context.exited)
        self.assertEqual(context.config.cwd, "/repo")
        self.assertEqual(context.thread_start_kwargs["model"], "gpt-5.5")
        self.assertEqual(context.thread_start_kwargs["sandbox"], "read-only")
        self.assertEqual(context.thread_start_kwargs["approval_mode"], "deny_all")
        self.assertIs(context.thread_start_kwargs["ephemeral"], True)
        self.assertEqual(context.thread.prompt, "Hello")
        self.assertEqual(context.thread.run_kwargs["effort"], "medium")
        self.assertEqual(context.thread.run_kwargs["model"], "gpt-5.5")
        self.assertEqual(result.content, "final answer")
        self.assertEqual(result.finish_reason, "completed")
        self.assertIs(client.last_result, result)

    def test_persistent_threads_can_be_requested_explicitly(self) -> None:
        client = CodexProofFuzzerClient(
            ephemeral_threads=False,
            codex_factory=FakeCodexContext,
            sdk=FakeSDK,
        )

        self.assertEqual(client.complete("Keep this thread"), "final answer")

        context = FakeCodexContext.last_instance
        self.assertIs(context.thread_start_kwargs["ephemeral"], False)

    def test_reused_thread_stays_open_until_close(self) -> None:
        client = CodexProofFuzzerClient(
            fresh_thread_per_call=False,
            codex_factory=FakeCodexContext,
            sdk=FakeSDK,
        )

        self.assertEqual(client.complete("First"), "final answer")
        context = FakeCodexContext.last_instance
        self.assertFalse(context.exited)
        self.assertEqual(client.complete("Second"), "final answer")
        self.assertIs(FakeCodexContext.last_instance, context)

        client.close()

        self.assertTrue(context.exited)


if __name__ == "__main__":
    unittest.main()
