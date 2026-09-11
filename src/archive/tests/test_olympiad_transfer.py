import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import MagicMock, patch

from src.archive.proof_fuzzer.olympiad_transfer import load_split, main, distill, recover_pending_review, discover, recover_distillation


class OlympiadTransferTests(unittest.TestCase):
    def test_saved_distillation_recovery_is_offline_and_checks_evidence(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            train, test = self.fixture(root / 'dataset')
            discovery, _ = load_split(root / 'dataset', train, test)
            evidence = root / 'distillation/workspaces/call_000002'
            evidence.mkdir(parents=True)
            response = '# Strategies:\nCheck hypotheses.\n# Do not:\nInvent flaws.\n# Before returning:\nVerify.'
            (root / 'distillation/response_2.md').write_text(response)
            (evidence / 'response.txt').write_text(response)
            for proof in discovery:
                (root / 'discovery' / proof.folder).mkdir(parents=True)
                (root / 'audits' / proof.folder).mkdir(parents=True)
                (root / 'discovery' / proof.folder / 'summary.json').write_text(
                    json.dumps(dict(complete=True, completed_attempts=1)))
                audit = json.dumps([dict(attempt='001', valid=True, detection='missed')])
                (root / 'audits' / proof.folder / 'results.json').write_text(audit)
                (evidence / f'proof_{proof.folder}.md').write_text(proof.proof)
                (evidence / f'audit_{proof.folder}.json').write_text(audit)
            with patch('src.archive.proof_fuzzer.olympiad_transfer.client') as factory:
                self.assertEqual(recover_distillation(root, discovery, 1), response)
                factory.assert_not_called()
            self.assertEqual((root / 'distillation/strategies.md').read_text(), response)
            (evidence / f'proof_{discovery[0].folder}.md').write_text('Changed')
            with self.assertRaisesRegex(ValueError, 'evidence changed'):
                recover_distillation(root, discovery, 1)
            (root / 'evaluation').mkdir()
            with self.assertRaisesRegex(ValueError, 'Evaluation already exists'):
                recover_distillation(root, discovery, 1)

    def test_completed_discovery_is_not_rerun_on_resume(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / 'mutator_workspace').mkdir()
            rows = [dict(attempt=i, status='judged') for i in range(1, 26)]
            (root / 'attempts.jsonl').write_text('\n'.join(json.dumps(r) for r in rows))
            with patch('src.archive.proof_fuzzer.olympiad_transfer.client') as factory:
                self.assertEqual(discover(root, None, 25, 'model', 'medium', resume=True), rows)
                factory.assert_not_called()

    def test_recovery_reuses_candidate_and_returns_feedback(self):
        from types import SimpleNamespace
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / 'attempts/023'
            source.mkdir(parents=True)
            candidate = root / 'mutator_workspace/attempts/023'
            candidate.mkdir(parents=True)
            (root / 'mutator_workspace/feedback').mkdir()
            (root / 'thread.json').write_text('{"thread_id":"old-thread"}')
            for p in (source, candidate):
                (p / 'original_proof.md').write_text('Original')
                (p / 'mutated_proof.md').write_text('Changed')
                (p / 'introduced_error.md').write_text('Error')
            (source / 'judge_prompt.txt').write_text('Exact original judge prompt')
            judge = MagicMock(technical_retries=1)
            judge.complete.return_value = '{"errors":[],"review_summary":"Checked"}'
            record = recover_pending_review(root, source,
                SimpleNamespace(proof='Original', example_id='p'), judge)
            judge.complete.assert_called_once_with('Exact original judge prompt')
            self.assertEqual(judge.technical_retries, 1)
            self.assertEqual(record['status'], 'judged')
            self.assertTrue(record['recovered_from_saved_mutation'])
            feedback = json.loads((root / 'mutator_workspace/feedback/023.json').read_text())
            self.assertEqual(feedback['judge_report'], judge.complete.return_value)
            self.assertEqual((source / 'mutated_proof.md').read_text(), 'Changed')

    def fixture(self, root):
        for i in range(10):
            folder = root / f'{i:06d}'
            folder.mkdir(parents=True)
            (folder / 'metadata.json').write_text(json.dumps({'original_data': dict(
                id=i, question=f'Problem {i}', solution=[f'Proof {i}', f'Alternative {i}'],
                subfield='Algebra')}))
        return [f'{i:06d}' for i in range(5)], [f'{i:06d}' for i in range(5, 10)]

    def test_individual_solution_and_disjoint_split(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            train, test = self.fixture(root)
            train[0] += ':1'
            discovery, heldout = load_split(root, train, test)
            self.assertEqual(discovery[0].proof, 'Alternative 0')
            self.assertEqual(discovery[0].metadata()['artifact'], 'original_data.solution[1]')
            self.assertFalse({p.example_id for p in discovery} & {p.example_id for p in heldout})
            test[0] = '000000'
            with self.assertRaisesRegex(ValueError, 'Duplicate problem'):
                load_split(root, train, test)

    def test_reject_same_question_different_id_and_image_placeholder(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            train, test = self.fixture(root)
            path = root / test[0] / 'metadata.json'
            data = json.loads(path.read_text())
            data['original_data']['question'] = ' problem  0 '
            path.write_text(json.dumps(data))
            with self.assertRaisesRegex(ValueError, 'Duplicate problem'):
                load_split(root, train, test)
            data['original_data']['question'] = 'Unique'
            data['original_data']['solution'] = ['See <img_1>']
            path.write_text(json.dumps(data))
            with self.assertRaisesRegex(ValueError, 'text-only'):
                load_split(root, train, test)

    def test_distillation_receives_discovery_only(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            train, test = self.fixture(root)
            discovery, heldout = load_split(root, train, test)
            llm = MagicMock()
            llm.complete_with_files.return_value = 'Strategies:\nCheck bounds.\nDo not:\nInvent errors.\nBefore returning:\nCheck validity.'
            with patch('src.archive.proof_fuzzer.olympiad_transfer.client', return_value=llm):
                distill(root / 'distill', discovery, {p.folder: [] for p in discovery}, 'model', 'medium')
            files = llm.complete_with_files.call_args.args[1]
            for p in heldout:
                self.assertNotIn(f'proof_{p.folder}.md', files)
            self.assertEqual(len(files), 10)
            llm.close.assert_called_once()

    def test_pipeline_orders_stages_and_uses_heldout_for_evaluation(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            train, test = self.fixture(root / 'dataset')
            output = root / 'run'
            args = ['run', '--dataset-root', str(root / 'dataset'), '--storage-dir', str(output),
                    '--discovery-folders', *train, '--heldout-folders', *test]
            events = []
            def discover(*args):
                events.append('discover')
                return []
            def audit(*args):
                self.assertEqual(events.count('discover'), 5)
                events.append('audit')
                return [dict(valid=True, detection='caught')]
            def distill(*args):
                self.assertEqual(events.count('audit'), 5)
                events.append('distill')
                return 'Frozen strategies'
            def evaluate(target, proofs, strategy, plan, llm):
                self.assertEqual(events[-1], 'distill')
                self.assertEqual({p.folder for p in proofs}, set(test))
                self.assertEqual(len(plan), 50)
                self.assertEqual(strategy, 'Frozen strategies')
                events.append('evaluate')
            with patch('sys.argv', args), \
                 patch('src.archive.proof_fuzzer.olympiad_transfer.discover', side_effect=discover), \
                 patch('src.archive.proof_fuzzer.olympiad_transfer.audit', side_effect=audit), \
                 patch('src.archive.proof_fuzzer.olympiad_transfer.distill', side_effect=distill), \
                 patch('src.archive.proof_fuzzer.olympiad_transfer.evaluate', side_effect=evaluate), \
                 patch('src.archive.proof_fuzzer.olympiad_transfer.client', return_value=MagicMock()):
                main()
            self.assertTrue(json.loads((output / 'status.json').read_text())['complete'])


if __name__ == '__main__':
    unittest.main()
