import json
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
import unittest

from src.archive.proof_fuzzer.matched_strategy_pilot import run, schedule, summarize


class MatchedPilotTests(unittest.TestCase):
    def test_balanced_reproducible_schedule(self):
        proofs = [SimpleNamespace(example_id=str(i)) for i in range(5)]
        plan = schedule(proofs, 9)
        self.assertEqual(plan, schedule(proofs, 9))
        self.assertEqual(len(plan), 50)
        for proof in proofs:
            for arm in ('generic', 'strategies'):
                self.assertEqual(sum(p['proof_id'] == proof.example_id and
                    p['arm'] == arm for p in plan), 5)

    def test_full_flow_and_blinding(self):
        prompts = []
        class Client:
            def complete(self, prompt):
                prompts.append(prompt)
                if prompt.startswith('You are introducing'):
                    return '## Mutated proof\nClaim 2=3.\n## Introduced error\nChanged equality is false.'
                if prompt.startswith('You are checking'):
                    return json.dumps(dict(verdict='incorrect', rationale='2 is not 3'))
                if prompt.startswith('You are reviewing'):
                    return json.dumps(dict(errors=[], review_summary='Checked all.'))
                return json.dumps(dict(introduced_error_found=False, match_level='none'))
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            proof = SimpleNamespace(example_id='p', proof='Claim 2=2.', problem='Equality')
            run(root, [proof], 'SECRET_STRATEGY',
                [dict(proof_id='p', arm='strategies', repeat=1)], Client())
            result = json.loads((root / 'results.json').read_text())[0]
            self.assertTrue(result['valid'])
            self.assertEqual([r['detection'] for r in result['reviews']], ['missed']*3)
            self.assertEqual(len(prompts), 8)
            self.assertIn('SECRET_STRATEGY', prompts[0])
            self.assertTrue(all('SECRET_STRATEGY' not in p for p in prompts[1:]))
            for prompt in prompts:
                if prompt.startswith('You are reviewing'):
                    self.assertNotIn('Changed equality is false', prompt)
                    self.assertNotIn('Claim 2=2.', prompt)

    def test_failed_attempt_in_denominator(self):
        result = summarize([dict(arm='generic', valid=False)])
        self.assertEqual(result['arms']['generic']['conservative_miss_yield'], 0)

    def test_cumulative_miss_thresholds(self):
        rows = [dict(arm='generic', valid=True, mutation_sha256=str(n),
                     reviews=[dict(detection='missed')]*n +
                             [dict(detection='caught')]*(3-n)) for n in (0, 1, 2, 3)]
        result = summarize(rows, planned_attempts=4)
        arm = result['arms']['generic']
        self.assertEqual(result['planned_attempts'], 4)
        self.assertEqual(arm['candidates_with_confirmed_miss'], 3)
        self.assertEqual(arm['candidates_with_at_least_two_misses'], 2)
        self.assertEqual(arm['candidates_with_three_misses'], 1)

    def test_custom_attempt_budget(self):
        proof = SimpleNamespace(example_id='p')
        self.assertEqual(len(schedule([proof], 1, attempts_per_proof=2)), 4)
        with self.assertRaises(ValueError):
            schedule([proof], 1, attempts_per_proof=0)

    def test_malformed_reports_and_failed_reviews_are_not_misses(self):
        for raw, found, expected in [('[]', False, 'ambiguous'),
                                     ('The edited equality 2=3 is false.', True, 'caught'),
                                     (None, False, 'ambiguous')]:
            with self.subTest(raw=raw), TemporaryDirectory() as tmp:
                class Client:
                    def complete(self, prompt):
                        if prompt.startswith('You are introducing'):
                            return '## Mutated proof\n2=3\n## Introduced error\nFalse equality.'
                        if prompt.startswith('You are checking'):
                            return '{"verdict":"incorrect"}'
                        if prompt.startswith('You are reviewing'):
                            if raw is None:
                                raise RuntimeError('Model unavailable')
                            return raw
                        return json.dumps(dict(introduced_error_found=found,
                                               match_level='exact' if found else 'none'))
                root = Path(tmp)
                run(root, [SimpleNamespace(example_id='p', proof='2=2', problem='Equality')],
                    '', [dict(proof_id='p', arm='generic', repeat=1)], Client())
                result = json.loads((root / 'results.json').read_text())[0]
                self.assertEqual([r['detection'] for r in result['reviews']], [expected]*3)
                self.assertEqual(json.loads((root / 'summary.json').read_text())['planned_attempts'], 1)

    def test_invalid_mutation_skips_judging(self):
        calls = []
        class Client:
            def complete(self, prompt):
                calls.append(prompt)
                if prompt.startswith('You are introducing'):
                    return '## Mutated proof\n2=1+1\n## Introduced error\nAllegation.'
                return '{"verdict":"correct"}'
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            run(root, [SimpleNamespace(example_id='p', proof='2=2', problem='Equality')],
                '', [dict(proof_id='p', arm='generic', repeat=1)], Client())
            self.assertEqual(len(calls), 2)
            self.assertEqual(json.loads((root / 'results.json').read_text())[0]['reviews'], [])


if __name__ == '__main__':
    unittest.main()
