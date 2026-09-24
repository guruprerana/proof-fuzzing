import json
from pathlib import Path
import stat
import sys
from tempfile import TemporaryDirectory
import textwrap
import unittest

from src.proof_fuzzer.agent_cli_client import (
    AgentCLICallTechnicalError,
    ClaudeCodeProofFuzzerClient,
    GeminiCLIProofFuzzerClient,
)


FAKE_CLI = r'''#!{python}
import json
import os
from pathlib import Path
import sys
import time

provider = Path(sys.argv[0]).name
prompt = sys.stdin.read()
cwd = Path.cwd()
task = (cwd / "prompt.txt").read_text()
model = sys.argv[sys.argv.index("--model") + 1]
if "TIMEOUT_FIRST" in task and cwd.name == "call_000001":
    time.sleep(1)
if "File-based mutation task" in task:
    source = (cwd / "original_proof.md").read_text()
    (cwd / "mutated_proof.md").write_text(source.replace("n=2k", "n=2k+1"))
    (cwd / "introduced_error.md").write_text("The even integer is represented as odd.")
    answer = "Done"
elif "REPEAT" in task:
    answer = "x" * 1500
elif "input.txt" in prompt:
    answer = "FILE:" + (cwd / "input.txt").read_text()
elif "WRITE_OUTPUT" in task:
    (cwd / "made.txt").write_text("written")
    answer = "WROTE"
else:
    answer = "ANSWER:" + task

if "claude" in provider:
    print(json.dumps({{"type": "system", "subtype": "init", "cwd": str(cwd), "argv": sys.argv[1:], "received_prompt": prompt}}), flush=True)
    print(json.dumps({{"type": "assistant", "message": {{"content": [{{"type": "thinking", "thinking": "brief reason"}}, {{"type": "text", "text": answer}}]}}}}), flush=True)
    print(json.dumps({{"type": "result", "subtype": "success", "terminal_reason": "completed", "is_error": False, "result": answer, "duration_api_ms": 1250, "total_cost_usd": 0.0123, "num_turns": 2, "usage": {{"input_tokens": 100, "cache_read_input_tokens": 20, "cache_creation_input_tokens": 5, "output_tokens": 30, "output_tokens_details": {{"thinking_tokens": 7}}}}}}), flush=True)
else:
    settings = cwd / ".gemini" / "settings.json"
    print(json.dumps({{"type": "init", "cwd": str(cwd), "argv": sys.argv[1:], "settings": str(settings), "received_prompt": prompt}}), flush=True)
    print(json.dumps({{"type": "message", "role": "assistant", "content": answer, "delta": True}}), flush=True)
    used_model = "different-model" if "MODEL_MISMATCH" in task else model
    print(json.dumps({{"type": "result", "status": "success", "stats": {{"input_tokens": 90, "output_tokens": 25, "cached": 15, "total_tokens": 115, "duration_ms": 750, "models": {{used_model: {{"input_tokens": 90}}}}}}}}), flush=True)
'''


class AgentCLIClientTest(unittest.TestCase):
    def setUp(self):
        self.temporary = TemporaryDirectory()
        self.root = Path(self.temporary.name)
        for name in ("fake-claude", "fake-gemini"):
            path = self.root / name
            path.write_text(textwrap.dedent(FAKE_CLI.format(python=sys.executable)))
            path.chmod(path.stat().st_mode | stat.S_IXUSR)

    def tearDown(self):
        self.temporary.cleanup()

    def client(self, provider, **kwargs):
        cls = ClaudeCodeProofFuzzerClient if provider == "claude" else GeminiCLIProofFuzzerClient
        return cls(
            workspace_root=self.root / f"{provider}-workspaces",
            executable=str(self.root / f"fake-{provider}"),
            **kwargs,
        )

    def test_claude_uses_fresh_restricted_writable_workspace(self):
        client = self.client("claude", model="sonnet", reasoning_effort="high", log_events=True)
        result = client.complete_with_reasoning("WRITE_OUTPUT")

        workspace = client.last_workspace
        self.assertEqual(result.content, "WROTE")
        self.assertEqual(result.reasoning, "brief reason")
        self.assertEqual((workspace / "made.txt").read_text(), "written")
        self.assertEqual((workspace / "response.txt").read_text(), "WROTE")
        init = result.raw_response[0]
        self.assertEqual(init["cwd"], str(workspace))
        argv = init["argv"]
        for option in ("--restricted", "--strict-mcp-config", "--safe-mode", "--no-session-persistence"):
            self.assertIn(option, argv)
        self.assertEqual(argv[argv.index("--tools") + 1], "Read,Write,Edit,Glob,Grep")
        self.assertEqual(argv[argv.index("--permission-mode") + 1], "acceptEdits")
        metadata = json.loads((workspace / "metadata.json").read_text())
        self.assertEqual(metadata["filesystem_policy"], "workspace_read_write")
        self.assertFalse(metadata["network_access"])
        self.assertFalse(metadata["shell_access"])
        self.assertGreater(metadata["elapsed_seconds"], 0)
        self.assertEqual(metadata["usage"]["input_tokens"], 100)
        self.assertEqual(metadata["usage"]["cached_input_tokens"], 20)
        self.assertEqual(metadata["usage"]["cache_write_input_tokens"], 5)
        self.assertEqual(metadata["usage"]["output_tokens"], 30)
        self.assertEqual(metadata["usage"]["reasoning_output_tokens"], 7)
        self.assertEqual(metadata["usage"]["total_tokens"], 155)
        self.assertEqual(metadata["usage"]["provider_elapsed_seconds"], 1.25)
        self.assertEqual(metadata["usage"]["cost_usd"], 0.0123)
        self.assertEqual(metadata["usage"]["turns"], 2)
        self.assertEqual(result.usage.to_dict(), metadata["usage"])
        self.assertTrue((self.root / "claude_code_traces/call_000001/events.jsonl").exists())

    def test_gemini_uses_workspace_settings_and_filesystem_only_policy(self):
        client = self.client("gemini", model="gemini-3.5-flash", log_events=True)
        result = client.complete_with_reasoning("WRITE_OUTPUT")

        workspace = client.last_workspace
        self.assertEqual(result.content, "WROTE")
        self.assertEqual((workspace / "made.txt").read_text(), "written")
        init = result.raw_response[0]
        settings_path = Path(init["settings"])
        self.assertEqual(settings_path, workspace / ".gemini/settings.json")
        settings = json.loads(settings_path.read_text())
        self.assertEqual(settings["context"]["memoryBoundaryMarkers"], [])
        self.assertNotIn("run_shell_command", settings["tools"]["core"])
        self.assertNotIn("google_web_search", settings["tools"]["core"])
        argv = init["argv"]
        policy = Path(argv[argv.index("--policy") + 1]).read_text()
        self.assertIn('toolName = "*"', policy)
        self.assertIn('decision = "deny"', policy)
        self.assertIn("priority = 999", policy)
        self.assertEqual(argv[argv.index("--approval-mode") + 1], "auto_edit")
        metadata = json.loads((workspace / "metadata.json").read_text())
        self.assertGreater(metadata["elapsed_seconds"], 0)
        self.assertEqual(metadata["usage"]["input_tokens"], 90)
        self.assertEqual(metadata["usage"]["cached_input_tokens"], 15)
        self.assertEqual(metadata["usage"]["output_tokens"], 25)
        self.assertEqual(metadata["usage"]["total_tokens"], 115)
        self.assertEqual(metadata["usage"]["provider_elapsed_seconds"], 0.75)
        self.assertEqual(result.usage.to_dict(), metadata["usage"])

    def test_file_backed_calls_do_not_duplicate_inputs_in_transport_prompt(self):
        for provider in ("claude", "gemini"):
            with self.subTest(provider=provider):
                client = self.client(provider)
                result = client.complete_with_files("Use input.txt", {"input.txt": "secret contents"})
                self.assertEqual(result, "FILE:secret contents")
                init = client.last_result.raw_response[0]
                self.assertNotIn("secret contents", init["received_prompt"])
                self.assertIn("input.txt", init["received_prompt"])
                metadata = json.loads((client.last_workspace / "metadata.json").read_text())
                self.assertEqual(metadata["input_files"], ["input.txt", "prompt.txt"])

    def test_each_call_gets_a_new_directory(self):
        client = self.client("gemini")
        client.complete("first")
        client.complete("second")
        root = self.root / "gemini-workspaces"
        self.assertEqual((root / "call_000001/prompt.txt").read_text(), "first")
        self.assertEqual((root / "call_000002/prompt.txt").read_text(), "second")

    def test_claude_persistent_turns_resume_one_restricted_session(self):
        client = self.client("claude", log_events=True)
        mutation_workspace = self.root / "persistent-mutation"
        mutation_workspace.mkdir()
        session = client.start_persistent_session(mutation_workspace)
        (mutation_workspace / "prompt.txt").write_text("WRITE_OUTPUT")

        first = client.run_persistent_turn(session, "Read prompt.txt")
        first_init = first.raw_response[0]
        self.assertEqual(Path(first_init["cwd"]), mutation_workspace)
        self.assertIn("--session-id", first_init["argv"])
        self.assertNotIn("--no-session-persistence", first_init["argv"])
        self.assertTrue((mutation_workspace / "made.txt").exists())

        second = client.run_persistent_turn(session, "Read prompt.txt again")
        second_init = second.raw_response[0]
        self.assertEqual(Path(second_init["cwd"]), mutation_workspace)
        self.assertIn("--resume", second_init["argv"])
        self.assertIn(session.id, second_init["argv"])
        self.assertEqual(
            sorted(p.name for p in (self.root / "claude-workspaces").iterdir()),
            ["call_000001", "call_000002"],
        )

    def test_gemini_persistent_turns_resume_one_restricted_session(self):
        client = self.client("gemini", log_events=True)
        mutation_workspace = self.root / "persistent-gemini-mutation"
        mutation_workspace.mkdir()
        session = client.start_persistent_session(mutation_workspace)
        (mutation_workspace / "prompt.txt").write_text("WRITE_OUTPUT")

        first = client.run_persistent_turn(session, "Read prompt.txt")
        first_init = first.raw_response[0]
        self.assertEqual(Path(first_init["cwd"]), mutation_workspace)
        self.assertIn("--session-id", first_init["argv"])
        self.assertTrue((mutation_workspace / "made.txt").exists())

        second = client.run_persistent_turn(session, "Read prompt.txt again")
        second_init = second.raw_response[0]
        self.assertEqual(Path(second_init["cwd"]), mutation_workspace)
        self.assertIn("--resume", second_init["argv"])
        self.assertIn(session.id, second_init["argv"])
        self.assertEqual(
            sorted(
                p.name
                for p in (self.root / "gemini-workspaces").iterdir()
                if p.name.startswith("call_")
            ),
            ["call_000001", "call_000002"],
        )

    def test_mutation_file_mode_returns_complete_mutation_and_explanation(self):
        prompt = """You are introducing a subtle mathematical error into a proof.
Original proof:
<original_proof>
Let n be even, so n=2k. The rest stays unchanged.
</original_proof>
Return the complete proof, followed by:
## Introduced error
Explain the error.
"""
        for provider in ("claude", "gemini"):
            with self.subTest(provider=provider):
                client = self.client(provider, mutation_file_editing=True)
                response = client.complete(prompt)
                self.assertIn("n=2k+1", response)
                self.assertIn("The rest stays unchanged", response)
                self.assertIn("## Introduced error", response)
                self.assertIn("represented as odd", response)
                metadata = json.loads((client.last_workspace / "metadata.json").read_text())
                self.assertGreater(metadata["elapsed_seconds"], 0)
                self.assertIsNotNone(metadata["usage"]["input_tokens"])
                self.assertEqual(
                    (client.last_workspace / "original_proof.md").read_text(),
                    "Let n be even, so n=2k. The rest stays unchanged.",
                )

    def test_unsafe_file_names_are_rejected(self):
        for provider in ("claude", "gemini"):
            client = self.client(provider)
            for filename in ("../outside", "/tmp/outside", "prompt.txt"):
                with self.subTest(provider=provider, filename=filename), self.assertRaises(ValueError):
                    client.complete_with_files("task", {filename: "data"})

    def test_timeout_is_logged_and_retried_in_a_fresh_workspace(self):
        client = self.client(
            "claude",
            log_events=True,
            call_timeout_seconds=0.1,
            technical_retries=1,
        )
        self.assertEqual(client.complete("TIMEOUT_FIRST"), "ANSWER:TIMEOUT_FIRST")
        root = self.root / "claude-workspaces"
        retry = json.loads((root / "call_000001/technical_retry.json").read_text())
        self.assertTrue(retry["retry_scheduled"])
        self.assertTrue((root / "call_000001/error.txt").exists())
        self.assertTrue((root / "call_000002/response.txt").exists())

    def test_repetition_guard_terminates_agent(self):
        client = self.client("gemini", log_events=True, detect_repetitive_output=True)
        with self.assertRaises(AgentCLICallTechnicalError):
            client.complete("REPEAT")
        self.assertIn("repetitive", (client.last_workspace / "error.txt").read_text())

    def test_gemini_rejects_silent_model_fallback(self):
        client = self.client("gemini", model="gemini-3.5-flash", log_events=True)
        with self.assertRaisesRegex(AgentCLICallTechnicalError, "model mismatch"):
            client.complete("MODEL_MISMATCH")
        self.assertIn("model mismatch", (client.last_workspace / "error.txt").read_text())

    def test_safeguards_require_event_logging(self):
        with self.assertRaises(ValueError):
            self.client("claude", call_timeout_seconds=1)


if __name__ == "__main__":
    unittest.main()
