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
)


FAKE_CLAUDE = r'''#!{python}
import json
from pathlib import Path
import sys
import time

prompt = sys.stdin.read()
cwd = Path.cwd()
task = (cwd / "prompt.txt").read_text()
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

print(json.dumps({{"type": "system", "subtype": "init", "cwd": str(cwd), "argv": sys.argv[1:], "received_prompt": prompt}}), flush=True)
print(json.dumps({{"type": "assistant", "message": {{"content": [{{"type": "thinking", "thinking": "brief reason"}}, {{"type": "text", "text": answer}}]}}}}), flush=True)
print(json.dumps({{"type": "result", "subtype": "success", "terminal_reason": "completed", "is_error": False, "result": answer, "duration_api_ms": 1250, "total_cost_usd": 0.0123, "num_turns": 2, "usage": {{"input_tokens": 100, "cache_read_input_tokens": 20, "cache_creation_input_tokens": 5, "output_tokens": 30, "output_tokens_details": {{"thinking_tokens": 7}}}}}}), flush=True)
'''


class ClaudeCodeClientTest(unittest.TestCase):
    def setUp(self):
        self.temporary = TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.executable = self.root / "fake-claude"
        self.executable.write_text(textwrap.dedent(FAKE_CLAUDE.format(python=sys.executable)))
        self.executable.chmod(self.executable.stat().st_mode | stat.S_IXUSR)

    def tearDown(self):
        self.temporary.cleanup()

    def client(self, **kwargs):
        return ClaudeCodeProofFuzzerClient(
            workspace_root=self.root / "claude-workspaces",
            executable=str(self.executable),
            **kwargs,
        )

    def test_fresh_restricted_writable_workspace_and_usage(self):
        client = self.client(model="claude-opus-5", reasoning_effort="high", log_events=True)
        result = client.complete_with_reasoning("WRITE_OUTPUT")
        workspace = client.last_workspace
        self.assertEqual(result.content, "WROTE")
        self.assertEqual(result.reasoning, "brief reason")
        self.assertEqual((workspace / "made.txt").read_text(), "written")
        argv = result.raw_response[0]["argv"]
        for option in ("--restricted", "--strict-mcp-config", "--safe-mode", "--no-session-persistence"):
            self.assertIn(option, argv)
        metadata = json.loads((workspace / "metadata.json").read_text())
        self.assertFalse(metadata["network_access"])
        self.assertFalse(metadata["shell_access"])
        self.assertEqual(metadata["usage"]["total_tokens"], 155)
        self.assertEqual(metadata["usage"]["reasoning_output_tokens"], 7)

    def test_file_backed_call_does_not_duplicate_input(self):
        client = self.client()
        result = client.complete_with_files("Use input.txt", {"input.txt": "secret contents"})
        self.assertEqual(result, "FILE:secret contents")
        init = client.last_result.raw_response[0]
        self.assertNotIn("secret contents", init["received_prompt"])
        self.assertIn("input.txt", init["received_prompt"])

    def test_each_call_gets_a_new_directory(self):
        client = self.client()
        client.complete("first")
        client.complete("second")
        root = self.root / "claude-workspaces"
        self.assertEqual((root / "call_000001/prompt.txt").read_text(), "first")
        self.assertEqual((root / "call_000002/prompt.txt").read_text(), "second")

    def test_persistent_turns_resume_one_restricted_session(self):
        client = self.client(log_events=True)
        workspace = self.root / "persistent-mutation"
        workspace.mkdir()
        session = client.start_persistent_session(workspace)
        (workspace / "prompt.txt").write_text("WRITE_OUTPUT")
        first = client.run_persistent_turn(session, "Read prompt.txt")
        self.assertIn("--session-id", first.raw_response[0]["argv"])
        second = client.run_persistent_turn(session, "Read prompt.txt again")
        self.assertIn("--resume", second.raw_response[0]["argv"])
        self.assertIn(session.id, second.raw_response[0]["argv"])

    def test_mutation_file_mode_returns_complete_artifacts(self):
        prompt = """You are introducing a subtle mathematical error into a proof.
Original proof:
<original_proof>
Let n be even, so n=2k. The rest stays unchanged.
</original_proof>
Return the complete proof, followed by:
## Introduced error
Explain the error.
"""
        client = self.client(mutation_file_editing=True)
        response = client.complete(prompt)
        self.assertIn("n=2k+1", response)
        self.assertIn("represented as odd", response)

    def test_unsafe_file_names_are_rejected(self):
        client = self.client()
        for filename in ("../outside", "/tmp/outside", "prompt.txt"):
            with self.subTest(filename=filename), self.assertRaises(ValueError):
                client.complete_with_files("task", {filename: "data"})

    def test_timeout_is_logged_and_retried(self):
        client = self.client(log_events=True, call_timeout_seconds=0.1, technical_retries=1)
        self.assertEqual(client.complete("TIMEOUT_FIRST"), "ANSWER:TIMEOUT_FIRST")
        root = self.root / "claude-workspaces"
        retry = json.loads((root / "call_000001/technical_retry.json").read_text())
        self.assertTrue(retry["retry_scheduled"])

    def test_repetition_guard_terminates_agent(self):
        client = self.client(log_events=True, detect_repetitive_output=True)
        with self.assertRaises(AgentCLICallTechnicalError):
            client.complete("REPEAT")

    def test_safeguards_require_event_logging(self):
        with self.assertRaises(ValueError):
            self.client(call_timeout_seconds=1)


if __name__ == "__main__":
    unittest.main()
