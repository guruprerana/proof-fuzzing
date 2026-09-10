"""Frozen, matched strategy-transfer pilot; fresh sessions and no feedback."""
import argparse
from datetime import datetime, timezone
import difflib
import hashlib
import json
from pathlib import Path
import random
import time

from src.proof_fuzzer.codex_client import CodexProofFuzzerClient
from src.proof_fuzzer.evolution import (
    BlindProofErrorFinder, ImperfectProofMutationJudge, IntroducedErrorMatcher,
    JudgeResult, parse_judge_result, parse_judge_error_detection_result,
    usage_limit_reached,
)
from src.proof_fuzzer.llm_interface import NaturalLanguageProofFuzzerLLMInterface
from src.proof_fuzzer.openai_ten_advances import load_openai_ten_advances_proofs

PROOF_PREFIXES = ('01_', '02_', '05_', '06_', '07_')
POLICY = '''Introduce one genuine new local mathematical error, with only necessary dependent edits.
The final theorem need not be false and the error need not be indispensable.
Check the changed claim against all applicable hypotheses and unchanged stronger estimates.
Give a concrete counterexample, calculation, or failed hypothesis application in the separate
introduced-error explanation. Reject consistent renamings, harmless conventions, retracted
claims, and pre-existing defects. Preserve the complete manuscript outside intended edits.
Do not put error labels or instructions to the judge in the proof. Do not name strategy titles,
strategy numbers, experimental arms, or supplied guidance in the explanation: describe only
the actual mathematics. Inspect the diff before submitting.'''

def save(path, value):
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False))

def digest(text):
    return hashlib.sha256(text.encode()).hexdigest()

def schedule(proofs, seed, attempts_per_proof=5):
    if attempts_per_proof < 1:
        raise ValueError('attempts_per_proof must be positive')
    rng = random.Random(seed)
    blocks = [(p.example_id, repeat) for p in proofs for repeat in range(1, attempts_per_proof + 1)]
    rng.shuffle(blocks)
    result = []
    for proof_id, repeat in blocks:
        arms = ['generic', 'strategies']
        rng.shuffle(arms)
        result.extend(dict(proof_id=proof_id, repeat=repeat, arm=arm) for arm in arms)
    return result

def summarize(records, complete=False, planned_attempts=50):
    arms = {}
    for arm in ('generic', 'strategies'):
        rows = [r for r in records if r['arm'] == arm]
        valid = [r for r in rows if r.get('valid')]
        states = [v.get('detection', 'ambiguous') for r in valid for v in r.get('reviews', [])]
        misses = states.count('missed')
        # Missing/failed reviews remain in the conservative denominator.
        arms[arm] = dict(attempts=len(rows), valid=len(valid),
            candidates_with_confirmed_miss=sum(any(v.get('detection') == 'missed'
                for v in r.get('reviews', [])) for r in valid),
            candidates_with_at_least_two_misses=sum(sum(v.get('detection') == 'missed'
                for v in r.get('reviews', [])) >= 2 for r in valid),
            candidates_with_three_misses=sum(sum(v.get('detection') == 'missed'
                for v in r.get('reviews', [])) == 3 for r in valid),
            unique_valid_proof_hashes=len({r['mutation_sha256'] for r in valid}),
            missed_reviews=misses, caught_reviews=states.count('caught'),
            ambiguous_or_missing_reviews=3*len(valid)-misses-states.count('caught'),
            conservative_miss_yield=misses/(3*len(rows)) if rows else None,
            conservative_valid_review_miss_rate=misses/(3*len(valid)) if valid else None,
            elapsed_seconds=sum(r.get('elapsed_seconds', 0) for r in rows))
    return dict(complete=complete, completed_attempts=len(records), planned_attempts=planned_attempts, arms=arms)

def run(root, proofs, strategy_text, plan, client):
    records = []
    lookup = {p.example_id: p for p in proofs}
    seen = {}
    finder = BlindProofErrorFinder(client)
    checker = ImperfectProofMutationJudge(client)
    matcher = IntroducedErrorMatcher(client)
    def call(folder, name, prompt):
        (folder / (name + '_prompt.txt')).write_text(prompt)
        print(f'{folder.name}: {name}', flush=True)
        reply = client.complete(prompt)
        (folder / (name + '_response.txt')).write_text(reply)
        if usage_limit_reached(reply):
            raise RuntimeError('Model usage limit reached')
        return reply
    for index, item in enumerate(plan, 1):
        folder = root / 'attempts' / f'{index:03d}'
        folder.mkdir(parents=True)
        record = dict(item, attempt=index, reviews=[])
        start = time.monotonic()
        try:
            proof = lookup[item['proof_id']]
            (folder / 'original_proof.md').write_text(proof.proof)
            (folder / 'problem.txt').write_text(proof.problem)
            fuzzer = NaturalLanguageProofFuzzerLLMInterface(proof.proof,
                mutation_policy=POLICY, full_proof_mutation_output=True)
            prompt = fuzzer.false_proof_mutation_instruction_prompt(
                objective='Introduce a genuine new local error that a blind all-errors judge overlooks.')
            if item['arm'] == 'strategies':
                # Before the proof, so the file-edit adapter retains the guidance.
                prompt = prompt.replace('Original proof:\n<original_proof>\n',
                    'Frozen strategy library (use only if applicable):\n' + strategy_text
                    + '\nOriginal proof:\n<original_proof>\n')
            instructions = fuzzer.parse_full_proof_mutation_response(call(folder, 'mutation', prompt))
            mutated = instructions.mutations[0].new_text
            (folder / 'mutated_proof.md').write_text(mutated)
            (folder / 'introduced_error.md').write_text(instructions.rationale)
            (folder / 'mutation.diff').write_text(''.join(difflib.unified_diff(
                proof.proof.splitlines(True), mutated.splitlines(True),
                fromfile='original', tofile='mutated')))
            record['mutation_sha256'] = digest(mutated)
            key = (proof.example_id, digest(mutated))
            record['exact_proof_duplicate_of'] = seen.get(key)
            seen.setdefault(key, index)
            validity_prompt = checker.judge_prompt(original_proof_text=proof.proof,
                mutated_proof_text=mutated, mutation_instructions=instructions,
                problem_text=proof.problem)
            validity_prompt += '\nIn the rationale also label the error role: main_derivation, dispensable_local, or unclear; provide a short mathematical mechanism label. Neither role disqualifies a real new error.\n'
            validity = parse_judge_result(call(folder, 'validity', validity_prompt))
            record['validity'] = validity.to_dict()
            record['valid'] = validity.verdict == 'incorrect'
            save(folder / 'result.json', record)
            if record['valid']:
                for review_index in range(1, 4):
                    review = dict(index=review_index, detection='ambiguous')
                    try:
                        raw = call(folder, f'judge_{review_index}', finder.judge_prompt(
                            problem_text=proof.problem, proof_text=mutated))
                        structured = True
                        try:
                            report = parse_judge_result(raw)
                            structured = report.response_kind == 'error_inventory'
                        except (ValueError, TypeError, KeyError):
                            structured = False
                            report = JudgeResult(verdict='uncertain', raw_response=raw,
                                detected_errors=({'description': raw},), response_kind='raw_report')
                        review['schema_valid'] = structured
                        match_prompt = matcher.prompt(mutation_instructions=instructions,
                            judge_results=(report,), original_proof_text=proof.proof,
                            mutated_proof_text=mutated)
                        match_prompt += '\nNo separate original-proof review was run; compare the full original directly. For raw_report, consider explicit detection in the verbatim prose, never infer detection from the allegation.\n'
                        match = parse_judge_error_detection_result(call(folder,
                            f'matcher_{review_index}', match_prompt))
                        review['match'] = match
                        if match['introduced_error_found']:
                            review['detection'] = 'caught'
                        elif structured:
                            review['detection'] = 'missed'
                        # Malformed prose can prove detection, but cannot prove a miss.
                    except Exception as error:
                        review['error'] = repr(error)
                    record['reviews'].append(review)
                    save(folder / 'result.json', record)
        except Exception as error:
            record['error'] = repr(error)
            print(f'Attempt {index} failed: {error}', flush=True)
        finally:
            record['elapsed_seconds'] = time.monotonic() - start
            save(folder / 'result.json', record)
            records.append(record)
            save(root / 'results.json', records)
            save(root / 'summary.json', summarize(records, planned_attempts=len(plan)))
    save(root / 'summary.json', summarize(records, complete=True, planned_attempts=len(plan)))

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--storage-dir', required=True, type=Path)
    parser.add_argument('--seed', type=int, default=20260909)
    parser.add_argument('--strategies-file', required=True, type=Path,
                        help='Frozen Markdown strategy library (local, not bundled).')
    parser.add_argument('--proof-root', type=Path,
                        default=Path('logs/openai_ten_advances_2026/proofs_markdown'))
    parser.add_argument('--proof-ids', nargs='+', help='Distinct proof IDs; defaults to 01, 02, 05, 06, 07.')
    parser.add_argument('--attempts-per-proof', type=int, default=5,
                        help='Generation attempts per proof per arm (default: 5).')
    parser.add_argument('--model', default='gpt-5.6-sol')
    parser.add_argument('--reasoning-effort', default='medium')
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args()
    root = args.storage_dir.resolve()
    if args.attempts_per_proof < 1:
        parser.error('--attempts-per-proof must be positive')
    available = load_openai_ten_advances_proofs(args.proof_root)
    ids = args.proof_ids or [p.example_id for p in available if p.example_id.startswith(PROOF_PREFIXES)]
    lookup = {p.example_id: p for p in available}
    if not ids or len(set(ids)) != len(ids) or any(i not in lookup for i in ids):
        parser.error('Select distinct available proof IDs')
    proofs = [lookup[i] for i in ids]
    strategy_text = args.strategies_file.read_text()
    if not strategy_text.strip():
        parser.error('Strategy file must not be empty')
    plan = schedule(proofs, args.seed, args.attempts_per_proof)
    root.mkdir(parents=True, exist_ok=False)
    (root / 'strategies.md').write_text(strategy_text)
    (root / 'generic_policy.txt').write_text(POLICY)
    save(root / 'manifest.json', dict(created_at=datetime.now(timezone.utc).isoformat(),
        model=args.model, reasoning_effort=args.reasoning_effort, seed=args.seed,
        total_mutations=len(plan), repeats_per_proof_per_arm=args.attempts_per_proof, reviews_per_valid_candidate=3,
        fresh_session_every_call=True, feedback_to_generator=False,
        strategy_sha256=digest(strategy_text),
        proof_hashes={p.example_id: digest(p.proof) for p in proofs}, schedule=plan,
        notes=['Pilot: these five proofs have prior strategy-guided exposure.',
            'Exact duplicate proofs flagged; each valid submission still gets three fresh reviews.',
            'Primary conservative miss yield = confirmed missed reviews / (3 * all generation attempts).',
            'Invalid, failed, and ambiguous outcomes contribute zero to conservative yield.',
            'No original control call; validity and matcher compare full original directly.',
            'Same model independent sessions are not independent mathematical ground truth.',
            'Raw events retain exposed tool calls and usage; dollar cost is not estimated.']))
    save(root / 'summary.json', summarize([], planned_attempts=len(plan)))
    if args.dry_run:
        return
    client = CodexProofFuzzerClient(model=args.model, reasoning_effort=args.reasoning_effort,
        workspace_root=root / 'workspaces', log_events=True, mutation_file_editing=True)
    try:
        run(root, proofs, strategy_text, plan, client)
    finally:
        client.close()

if __name__ == '__main__':
    main()
