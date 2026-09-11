import unittest

from src.proof_fuzzer.mechanism_transfer import assign_reward


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


if __name__ == '__main__':
    unittest.main()
