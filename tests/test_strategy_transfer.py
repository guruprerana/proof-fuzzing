import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from src.proof_fuzzer.strategy_transfer import (
    SAFEGUARDED_CALL_TIMEOUT_SECONDS,
    assign_reward,
    client,
)


class MechanismRewardTests(unittest.TestCase):
    def test_reward_first_miss_once(self):
        mechanism = {}
        self.assertEqual(assign_reward(mechanism, 'novel', 'missed'), 1.0)
        self.assertTrue(mechanism['success_rewarded'])
        self.assertEqual(assign_reward(mechanism, 'variant', 'missed'), 0.0)

    def test_reward_novel_caught_then_first_miss(self):
        mechanism = {}
        self.assertEqual(assign_reward(mechanism, 'novel', 'caught'), 0.25)
        self.assertEqual(assign_reward(mechanism, 'variant', 'missed'), 1.0)

    def test_no_reward_for_ambiguous_or_caught_variant(self):
        mechanism = {}
        self.assertEqual(assign_reward(mechanism, 'novel', 'ambiguous'), 0.0)
        self.assertEqual(assign_reward(mechanism, 'variant', 'caught'), 0.0)


class CallTimeoutTests(unittest.TestCase):
    def test_discovery_client_can_disable_call_timeout(self):
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            guarded = client(root / "guarded", "claude-opus-5", "medium",
                             provider="claude-code")
            unbounded = client(root / "unbounded", "claude-opus-5", "medium",
                               provider="claude-code", disable_call_timeout=True)
            try:
                self.assertEqual(
                    guarded.call_timeout_seconds,
                    SAFEGUARDED_CALL_TIMEOUT_SECONDS,
                )
                self.assertIsNone(unbounded.call_timeout_seconds)
            finally:
                guarded.close()
                unbounded.close()


if __name__ == '__main__':
    unittest.main()
