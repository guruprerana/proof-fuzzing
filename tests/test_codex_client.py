import json
from pathlib import Path
from tempfile import TemporaryDirectory
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

    def test_isolated_workspace_contains_prompt_response_and_scoped_thread(self) -> None:
        with TemporaryDirectory() as tmp_dir:
            workspace_root = Path(tmp_dir) / "codex_workspace"
            client = CodexProofFuzzerClient(
                workspace_root=workspace_root,
                developer_instructions="Return JSON only.",
                codex_factory=FakeCodexContext,
                sdk=FakeSDK,
            )

            self.assertEqual(client.complete("Proof text"), "final answer")

            workspace = workspace_root / "call_000001"
            context = FakeCodexContext.last_instance
            self.assertEqual(context.config.cwd, str(workspace))
            self.assertEqual(context.thread_start_kwargs["cwd"], str(workspace))
            self.assertEqual(context.thread_start_kwargs["sandbox"], "read-only")
            self.assertEqual(context.thread.run_kwargs["sandbox"], "read-only")
            thread_config = context.thread_start_kwargs["config"]
            self.assertEqual(thread_config["agents"]["enabled"], False)
            self.assertEqual(thread_config["web_search"], "disabled")
            self.assertEqual((workspace / "prompt.txt").read_text(encoding="utf-8"), "Proof text")
            self.assertNotIn("Proof text", context.thread.prompt)
            self.assertIn("prompt.txt", context.thread.prompt)
            self.assertEqual((workspace / "response.txt").read_text(encoding="utf-8"), "final answer")
            metadata = json.loads((workspace / "metadata.json").read_text(encoding="utf-8"))
            self.assertEqual(metadata["status"], "completed")
            self.assertEqual(metadata["network_access"], False)
            self.assertEqual(metadata["filesystem_policy"], "sandbox_read_only")
            self.assertEqual(metadata["permission_profile"], "")
            self.assertEqual(metadata["web_search"], "disabled")
            self.assertEqual(metadata["input_files"], ["prompt.txt"])
            instructions = context.thread_start_kwargs["developer_instructions"]
            self.assertIn("Return JSON only.", instructions)
            self.assertIn("Treat the current working directory", instructions)
            self.assertIn("Do not use network or internet resources", instructions)

    def test_isolated_workspace_uses_one_directory_per_call(self) -> None:
        with TemporaryDirectory() as tmp_dir:
            workspace_root = Path(tmp_dir) / "codex_workspace"
            client = CodexProofFuzzerClient(
                workspace_root=workspace_root,
                codex_factory=FakeCodexContext,
                sdk=FakeSDK,
            )

            client.complete("First")
            client.complete("Second")

            self.assertEqual(
                (workspace_root / "call_000001" / "prompt.txt").read_text(encoding="utf-8"),
                "First",
            )
            self.assertEqual(
                (workspace_root / "call_000002" / "prompt.txt").read_text(encoding="utf-8"),
                "Second",
            )

    def test_file_backed_completion_separates_strategy_and_trace(self) -> None:
        with TemporaryDirectory() as tmp_dir:
            workspace_root = Path(tmp_dir) / "codex_workspace"
            client = CodexProofFuzzerClient(
                workspace_root=workspace_root,
                codex_factory=FakeCodexContext,
                sdk=FakeSDK,
            )

            result = client.complete_with_files(
                "Use strategy.txt to mutate trace.json. Return JSON only.",
                {
                    "strategy.txt": "Preserve fluency.",
                    "trace.json": '{"trace": "secret benchmark content"}',
                },
            )

            workspace = workspace_root / "call_000001"
            context = FakeCodexContext.last_instance
            self.assertEqual(result, "final answer")
            self.assertEqual(
                (workspace / "strategy.txt").read_text(encoding="utf-8"),
                "Preserve fluency.",
            )
            self.assertEqual(
                (workspace / "trace.json").read_text(encoding="utf-8"),
                '{"trace": "secret benchmark content"}',
            )
            self.assertIn("strategy.txt", context.thread.prompt)
            self.assertIn("trace.json", context.thread.prompt)
            self.assertNotIn("Preserve fluency", context.thread.prompt)
            self.assertNotIn("secret benchmark content", context.thread.prompt)
            metadata = json.loads((workspace / "metadata.json").read_text())
            self.assertEqual(
                metadata["input_files"],
                ["prompt.txt", "strategy.txt", "trace.json"],
            )

    def test_file_backed_completion_rejects_unsafe_filenames(self) -> None:
        with TemporaryDirectory() as tmp_dir:
            client = CodexProofFuzzerClient(
                workspace_root=Path(tmp_dir) / "codex_workspace",
                codex_factory=FakeCodexContext,
                sdk=FakeSDK,
            )

            for filename in ("../trace.json", "/tmp/trace.json", "prompt.txt"):
                with self.subTest(filename=filename), self.assertRaises(ValueError):
                    client.complete_with_files("Instructions", {filename: "content"})

    def test_isolated_workspace_rejects_unsafe_thread_settings(self) -> None:
        unsafe_settings = (
            {"sandbox": "workspace_write"},
            {"approval_mode": "auto_review"},
            {"fresh_thread_per_call": False},
            {"cwd": "/repo"},
        )
        for settings in unsafe_settings:
            with self.subTest(settings=settings), self.assertRaises(ValueError):
                CodexProofFuzzerClient(workspace_root="/tmp/codex-workspaces", **settings)


if __name__ == "__main__":
    unittest.main()
