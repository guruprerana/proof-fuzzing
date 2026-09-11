import unittest
from types import SimpleNamespace

from src.archive.proof_fuzzer.prompt_evolution import (
    _evolved_prompt_char_limit, _validate_mutation_policy, training_prompt_config,
)


class TrainingPromptConfigTests(unittest.TestCase):
    def test_plain_and_markdown_section_headings(self):
        for prefix in ('', '# ', '## ', '###### '):
            policy = '\n'.join(prefix + heading + ':\nContent.'
                               for heading in ('Strategies', 'Do not', 'Before returning'))
            self.assertEqual(_validate_mutation_policy(policy, max_chars=1000), policy)
        for policy in ('# Strategies:\n# Do not:',
                       'Strategies are useful.\nDo not:\nBefore returning:',
                       '#Strategy:\nDo not:\nBefore returning:'):
            with self.assertRaises(ValueError):
                _validate_mutation_policy(policy, max_chars=1000)

    def test_full_20k_budget_available_even_without_successes(self):
        config = training_prompt_config("unused")
        for size in (len(config.initial_prompt), 10_000, 20_000):
            for successes in (0, 3):
                self.assertEqual(_evolved_prompt_char_limit(
                    current=SimpleNamespace(prompt_text="x" * size),
                    successes=successes, config=config,
                ), 20_000)
        policy = config.initial_prompt.ljust(20_000, "x")
        _validate_mutation_policy(policy, max_chars=config.max_prompt_chars)
        with self.assertRaises(ValueError):
            _validate_mutation_policy(policy + "x", max_chars=config.max_prompt_chars)
