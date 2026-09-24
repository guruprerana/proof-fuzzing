import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch
from types import SimpleNamespace

from src.proof_fuzzer.codex_client import CodexProofFuzzerClient
from src.proof_fuzzer.codex_client import CodexCallTechnicalError, OutputRepetitionGuard, _timed_events


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
    def __init__(self, *, cwd=None, codex_bin=None):
        self.cwd = cwd
        self.codex_bin = codex_bin


class FakeTurnResult:
    final_response = "final answer"
    status = "completed"
    duration_ms = 2500
    usage = {
        "total": {
            "inputTokens": 120,
            "cachedInputTokens": 40,
            "cacheWriteInputTokens": 10,
            "outputTokens": 35,
            "reasoningOutputTokens": 12,
            "totalTokens": 155,
        }
    }


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
    def test_repetition_guard_handles_split_deltas_but_not_regular_text(self):
        guard = OutputRepetitionGuard()
        detected = False
        for _ in range(400):
            for delta in ('\\u', '000', '0'):
                detected = guard.update('message', delta) or detected
        self.assertTrue(detected)
        self.assertFalse(guard.update('new-message', 'A normal mathematical conclusion.'))
        guard = OutputRepetitionGuard()
        self.assertFalse(guard.update('message', ''.join(f'Step {n}: value={n*n}. ' for n in range(400))))

    def test_silent_stream_times_out(self):
        import threading
        released = threading.Event()
        def stream():
            released.wait(timeout=2)
            yield SimpleNamespace(method='done')
        try:
            with self.assertRaises(CodexCallTechnicalError):
                list(_timed_events(SimpleNamespace(stream=stream), 0.02))
        finally:
            released.set()

    def test_only_guard_failures_are_retried_once(self):
        with TemporaryDirectory() as tmp:
            client = CodexProofFuzzerClient(workspace_root=tmp, log_events=True, technical_retries=1)
            with patch.object(client, '_run_fresh_thread_once', side_effect=[
                CodexCallTechnicalError('timeout'), FakeTurnResult()]) as calls:
                self.assertEqual(client.complete('unchanged prompt'), 'final answer')
                self.assertEqual(calls.call_count, 2)
                self.assertEqual(calls.call_args_list[0], calls.call_args_list[1])
            with patch.object(client, '_run_fresh_thread_once', side_effect=ValueError('schema')) as calls:
                with self.assertRaises(ValueError):
                    client.complete('prompt')
                self.assertEqual(calls.call_count, 1)
            with patch.object(client, '_run_fresh_thread_once', side_effect=CodexCallTechnicalError('timeout')) as calls:
                with self.assertRaises(CodexCallTechnicalError):
                    client.complete('prompt')
                self.assertEqual(calls.call_count, 2)

    def test_repetitive_stream_is_logged_and_interrupted(self):
        from openai_codex.models import Notification
        interrupted = []
        def turn(thread, prompt, **kwargs):
            return SimpleNamespace(id='turn', interrupt=lambda: interrupted.append(True),
                stream=lambda: iter([Notification('item/agentMessage/delta',
                                                  {'itemId': 'msg', 'delta': '\\u0000' * 400})]))
        with TemporaryDirectory() as tmp, patch.object(FakeThread, 'turn', turn, create=True):
            root = Path(tmp)
            client = CodexProofFuzzerClient(workspace_root=root / 'workspaces',
                log_events=True, detect_repetitive_output=True, call_timeout_seconds=1,
                sdk=FakeSDK, codex_factory=FakeCodexContext)
            with self.assertRaises(CodexCallTechnicalError):
                client.complete('Review')
            self.assertEqual(interrupted, [True])
            trace = (root / 'codex_traces/call_000001/events.jsonl').read_text()
            self.assertIn('client/guardInterrupt', trace)
            self.assertIn('item/agentMessage/delta', trace)

    def test_file_mutation_outputs_and_permissions_are_call_local(self):
        source = "Let n be even. Then n=2k.\nThe remaining text is unchanged."
        prompt = f"""You are introducing a subtle mathematical error into a proof.
Original proof:
<original_proof>
{source}
</original_proof>
Return the complete proof, followed by:
## Introduced error
Explain the error.
"""
        with TemporaryDirectory() as tmp_dir:
            client = CodexProofFuzzerClient(workspace_root=tmp_dir, mutation_file_editing=True,
                                           sdk=FakeSDK, codex_factory=FakeCodexContext)
            def run(thread, prompt, **kwargs):
                context = FakeCodexContext.last_instance
                workspace = Path(context.config.cwd)
                self.assertIsNone(kwargs["sandbox"])
                self.assertEqual(context.thread_start_kwargs["sandbox"], "workspace-write")
                policy = context.thread_start_kwargs["config"]["sandbox_workspace_write"]
                self.assertEqual(policy["writable_roots"], [str(workspace)])
                self.assertFalse(policy["network_access"])
                self.assertTrue(policy["exclude_slash_tmp"])
                self.assertEqual((workspace / "original_proof.md").read_text(), source)
                task = (workspace / "prompt.txt").read_text()
                self.assertNotIn(source, task)
                self.assertIn("targeted filesystem edits", task)
                (workspace / "mutated_proof.md").write_text(source.replace("2k.", "2k+1."))
                (workspace / "introduced_error.md").write_text("An even number is represented as odd.")
                return FakeTurnResult()
            with patch.object(FakeThread, "run", run):
                response = client.complete(prompt)
            self.assertIn("An even number", response)
            self.assertIn("remaining text is unchanged", response)
            workspace = client.last_workspace
            metadata = json.loads((workspace / "metadata.json").read_text())
            self.assertEqual(metadata["filesystem_policy"], "sandbox_workspace_write")
            self.assertNotIn("introduced_error.md", metadata["input_files"])
            self.assertEqual((workspace / "response.txt").read_text(), "final answer")
            client.complete("Review this proof")
            self.assertEqual(FakeCodexContext.last_instance.thread_start_kwargs["sandbox"], "read-only")

    def test_file_mutation_rejects_missing_unchanged_and_linked_outputs(self):
        from src.proof_fuzzer.codex_client import _read_file_mutation
        with TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            (root / "original_proof.md").write_text("Original")
            with self.assertRaises(FileNotFoundError):
                _read_file_mutation(root, "Original")
            (root / "mutated_proof.md").write_text("Original")
            (root / "introduced_error.md").write_text("Explanation")
            with self.assertRaisesRegex(ValueError, "unchanged"):
                _read_file_mutation(root, "Original")
            (root / "mutated_proof.md").unlink()
            (root / "mutated_proof.md").symlink_to(root / "original_proof.md")
            with self.assertRaisesRegex(ValueError, "regular"):
                _read_file_mutation(root, "Original")
            with self.assertRaisesRegex(ValueError, "modified"):
                _read_file_mutation(root, "Different input")

    def test_event_stream_logs_tool_output_and_preserves_final_response(self):
        from openai_codex.models import Notification
        from openai_codex.generated.v2_all import ItemCompletedNotification, TurnCompletedNotification

        with TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            def stream():
                yield Notification("item/started", {"item": {"type": "commandExecution", "command": "pwd"}})
                yield Notification("item/commandExecution/outputDelta", {"delta": "/workspace\n"})
                # The log must be readable while the turn is still in progress.
                self.assertIn("/workspace", (root / "codex_traces/call_000001/events.jsonl").read_text())
                yield Notification("item/completed", ItemCompletedNotification.model_validate({
                    "threadId": "thread", "turnId": "turn", "completedAtMs": 1,
                    "item": {"id": "msg", "type": "agentMessage", "text": "final answer", "phase": "final_answer"},
                }))
                yield Notification("turn/completed", TurnCompletedNotification.model_validate({
                    "threadId": "thread", "turn": {"id": "turn", "status": "completed", "items": [], "itemsView": "full"},
                }))

            def turn(thread, prompt, **kwargs):
                thread.prompt, thread.run_kwargs = prompt, kwargs
                return SimpleNamespace(id="turn", stream=stream)

            with patch.object(FakeThread, "turn", turn, create=True):
                client = CodexProofFuzzerClient(workspace_root=root / "codex_workspace",
                    log_events=True, sdk=FakeSDK, codex_factory=FakeCodexContext)
                self.assertEqual(client.complete("Proof"), "final answer")
            trace = root / "codex_traces/call_000001"
            entries = [json.loads(line) for line in (trace / "events.jsonl").read_text().splitlines()]
            self.assertEqual(entries[2]["payload"]["delta"], "/workspace\n")
            self.assertIn("final answer", (trace / "transcript.md").read_text())
            self.assertEqual(json.loads((trace / "result.json").read_text())["final_response"], "final answer")
            workspace = root / "codex_workspace/call_000001"
            self.assertFalse((workspace / "events.jsonl").exists())
            self.assertEqual(json.loads((workspace / "metadata.json").read_text())["input_files"], ["prompt.txt"])

    def test_event_stream_keeps_partial_output_on_failure(self):
        from openai_codex.models import Notification
        def stream():
            yield Notification("item/agentMessage/delta", {"delta": "Partial commentary"})
            raise RuntimeError("stream disconnected")
        with TemporaryDirectory() as tmp_dir, patch.object(FakeThread, "turn", create=True,
                return_value=SimpleNamespace(id="turn", stream=stream)):
            client = CodexProofFuzzerClient(workspace_root=Path(tmp_dir) / "codex_workspace",
                log_events=True, sdk=FakeSDK, codex_factory=FakeCodexContext)
            with self.assertRaisesRegex(RuntimeError, "stream disconnected"):
                client.complete("Proof")
            events = (Path(tmp_dir) / "codex_traces/call_000001/events.jsonl").read_text()
            self.assertIn("Partial commentary", events)
            self.assertIn("client/error", events)

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
        self.assertGreater(result.usage.elapsed_seconds, 0)
        self.assertEqual(result.usage.provider_elapsed_seconds, 2.5)
        self.assertEqual(result.usage.input_tokens, 120)
        self.assertEqual(result.usage.cached_input_tokens, 40)
        self.assertEqual(result.usage.cache_write_input_tokens, 10)
        self.assertEqual(result.usage.output_tokens, 35)
        self.assertEqual(result.usage.reasoning_output_tokens, 12)
        self.assertEqual(result.usage.total_tokens, 155)
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
            self.assertGreater(metadata["elapsed_seconds"], 0)
            self.assertEqual(metadata["usage"]["input_tokens"], 120)
            self.assertEqual(metadata["usage"]["cached_input_tokens"], 40)
            self.assertEqual(metadata["usage"]["output_tokens"], 35)
            self.assertEqual(metadata["usage"]["reasoning_output_tokens"], 12)
            self.assertEqual(metadata["usage"]["total_tokens"], 155)
            self.assertEqual(metadata["usage"]["provider_elapsed_seconds"], 2.5)
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
