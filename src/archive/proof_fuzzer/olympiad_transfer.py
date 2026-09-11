"""Problem-disjoint Olympiad discovery, audit, distillation, and matched transfer."""
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from datetime import datetime, timezone
import argparse
import hashlib
import json
from pathlib import Path
import re

from src.proof_fuzzer.codex_client import CodexProofFuzzerClient, _load_codex_sdk
from src.archive.proof_fuzzer.evolution import (
    ImperfectProofMutationJudge, IntroducedErrorMatcher, JudgeResult,
    parse_judge_result, parse_judge_error_detection_result,
)
from src.archive.proof_fuzzer.llm_interface import FuzzerMutationInstructions, ProofMutation
from src.archive.proof_fuzzer.matched_strategy_pilot import run as evaluate, schedule, save, digest, POLICY
from src.proof_fuzzer.persistent_fuzzing import run_attempts, write_summary
from src.archive.proof_fuzzer.prompt_evolution import _validate_mutation_policy


@dataclass(frozen=True)
class OlympiadProof:
    example_id: str
    problem: str
    proof: str
    path: Path
    topic: str
    folder: str
    solution_index: int

    def metadata(self):
        return dict(problem_id=self.example_id, folder=self.folder, topic=self.topic,
                    source=str(self.path), source_sha256=hashlib.sha256(self.path.read_bytes()).hexdigest(),
                    problem_sha256=digest(normalize_problem(self.problem)),
                    proof_sha256=digest(self.proof), proof_chars=len(self.proof),
                    artifact=f'original_data.solution[{self.solution_index}]', problem=self.problem)


def normalize_problem(text):
    return re.sub(r'\s+', '', text).casefold()


def load_split(dataset_root, discovery_folders, heldout_folders):
    """Reject repeated source problem IDs or normalized questions across both arms."""
    if len(discovery_folders) != 5 or len(heldout_folders) != 5:
        raise ValueError('Select exactly five discovery and five held-out proofs')
    proofs, ids, questions = [], set(), set()
    for selector in [*discovery_folders, *heldout_folders]:
        if not re.fullmatch(r'\d{6}(?::\d+)?', selector):
            raise ValueError(f'Expected folder or folder:solution_index: {selector}')
        folder, _, index = selector.partition(':')
        solution_index = int(index or 0)
        path = dataset_root / folder / 'metadata.json'
        data = json.loads(path.read_text())['original_data']
        question = data['question'].strip()
        solution = data['solution']
        if isinstance(solution, list):
            proof = solution[solution_index]
        elif solution_index == 0:
            proof = solution
        else:
            raise ValueError(f'No solution index {solution_index}: {folder}')
        problem_id = str(data['id'])
        normalized = normalize_problem(question)
        if problem_id in ids or normalized in questions:
            raise ValueError(f'Duplicate problem in split: {folder} / {problem_id}')
        if (not proof.strip() or not question or any(data.get(f'image_{i}') for i in range(1, 10))
                or re.search(r'<img|!\[.*?\]\(', proof, flags=re.IGNORECASE)):
            raise ValueError(f'Expected a complete text-only solution: {folder}')
        ids.add(problem_id)
        questions.add(normalized)
        proofs.append(OlympiadProof(problem_id, question, proof, path,
                                    data.get('subfield', 'unspecified'), folder, solution_index))
    return proofs[:5], proofs[5:]


def client(root, model, effort, *, editing=False, safeguards=True):
    return CodexProofFuzzerClient(model=model, reasoning_effort=effort,
                                 workspace_root=root / 'workspaces', log_events=True,
                                 mutation_file_editing=editing,
                                 call_timeout_seconds=600 if safeguards else None,
                                 detect_repetitive_output=safeguards,
                                 technical_retries=1 if safeguards else 0)


def discover(root, proof, attempts, model, effort, resume=False):
    root.mkdir(parents=True, exist_ok=resume)
    workspace = root / 'mutator_workspace'
    workspace.mkdir(exist_ok=resume)
    existing = []
    if resume and (root / 'attempts.jsonl').exists():
        existing = [json.loads(line) for line in (root / 'attempts.jsonl').read_text().splitlines()]
        if [r['attempt'] for r in existing] != list(range(1, len(existing) + 1)):
            raise ValueError('Discovery checkpoint is not a contiguous attempt sequence')
    if len(existing) == attempts:
        return existing
    if not resume:
        save(root / 'source.json', proof.metadata())
    # Persistent mutation state is not retried blindly; guard fresh review/check calls.
    mutator = client(root / 'mutator', model, effort, safeguards=False)
    judge = client(root / 'judge', model, effort)
    try:
        if resume:
            pending = root / 'attempts' / f'{len(existing) + 1:03d}'
            if pending.exists():
                existing.append(recover_pending_review(root, pending, proof, judge))
                write_summary(root, existing, attempts)
            previous_thread = json.loads((root / 'thread.json').read_text())
            context = dict(reason='Technical restart; previous session was ephemeral',
                           previous_thread=previous_thread, completed_attempts=existing,
                           history=[dict(attempt=r['attempt'],
                               introduced_error=(root / 'attempts' / f"{r['attempt']:03d}" / 'introduced_error.md').read_text(),
                               feedback=json.loads((workspace / 'feedback' / f"{r['attempt']:03d}.json").read_text()))
                               for r in existing])
            save(workspace / 'recovery_context.md', context)
            save(root / 'recovery.json', context)
        sdk = _load_codex_sdk()
        with mutator._make_codex_context(sdk, cwd=str(workspace)) as codex:
            thread = mutator._start_thread(codex, sdk, cwd=str(workspace), sandbox='workspace_write')
            save(root / ('recovered_thread.json' if resume else 'thread.json'), dict(thread_id=thread.id))
            records = run_attempts(root=root, proof=proof, total=attempts, mutator=mutator,
                                   thread=thread, sdk=sdk, judge=judge,
                                   initial_records=existing, recovery_context=resume)
        if len(records) != attempts:
            raise RuntimeError(f'Discovery ended early: {len(records)}/{attempts}')
        return records
    finally:
        mutator.close()
        judge.close()


def recover_pending_review(root, source, proof, judge):
    """Retry a saved candidate once, never generate a replacement mutation."""
    from src.proof_fuzzer.codex_client import _read_file_mutation
    index = int(source.name)
    workspace = root / 'mutator_workspace'
    candidate = workspace / 'attempts' / source.name
    _read_file_mutation(candidate, proof.proof)
    if (source / 'mutated_proof.md').read_text() != (candidate / 'mutated_proof.md').read_text():
        raise ValueError('Pending candidate differs from archived proof')
    if (source / 'judge_response.txt').exists():
        raise ValueError('Pending attempt already has a response; manual reconciliation required')
    record = dict(attempt=index, proof_id=proof.example_id, verified_success=None,
                  recovered_from_saved_mutation=True,
                  technical_retry_reason='Interrupted runaway review',
                  mutator_thread_id=json.loads((root / 'thread.json').read_text())['thread_id'])
    retries = judge.technical_retries
    judge.technical_retries = 0  # The interrupted original already consumed the first call.
    try:
        raw = judge.complete((source / 'judge_prompt.txt').read_text())
        (source / 'judge_response.txt').write_text(raw)
        report = parse_judge_result(raw)
        if report.response_kind != 'error_inventory':
            raise ValueError('Recovered review is not an error inventory')
        record.update(status='judged', reported_errors=len(report.detected_errors))
        feedback = dict(attempt=index, judge_report=raw,
                        interpretation='Fresh review after technical cancellation; not independently validated.')
    except Exception as error:
        record.update(status='failed', failure_stage='target_judge_recovery', error=repr(error))
        feedback = dict(record, interpretation='Technical review failure, not evidence of a judge miss.')
        if (source / 'judge_response.txt').exists():
            feedback['judge_report'] = (source / 'judge_response.txt').read_text()
    finally:
        judge.technical_retries = retries
    save(source / 'result.json', record)
    save(source / 'recovery.json', record)
    save(source / 'feedback.json', feedback)
    save(workspace / 'feedback' / f'{index:03d}.json', feedback)
    with (root / 'attempts.jsonl').open('a') as stream:
        stream.write(json.dumps(record) + '\n')
    return record


def audit(root, discovery_root, proof, model, effort):
    """Fresh validity and matching agents; discovery feedback remains untouched."""
    root.mkdir(parents=True)
    llm = client(root, model, effort)
    checker, matcher = ImperfectProofMutationJudge(llm), IntroducedErrorMatcher(llm)
    records = []
    try:
        for source in sorted((discovery_root / 'attempts').iterdir()):
            record = dict(attempt=source.name, valid=None, detection='ambiguous')
            folder = root / source.name
            folder.mkdir()
            try:
                mutated = (source / 'mutated_proof.md').read_text()
                explanation = (source / 'introduced_error.md').read_text()
                instructions = FuzzerMutationInstructions(False, (ProofMutation(
                    kind='global_context', target='whole_proof', new_text=mutated,
                    summary=explanation, propagate_downstream=False),), rationale=explanation)
                record.update(introduced_error=explanation, mutation_sha256=digest(mutated))
                record['mutation_diff'] = (source / 'mutation.diff').read_text()
                prompt = checker.judge_prompt(original_proof_text=proof.proof,
                    mutated_proof_text=mutated, mutation_instructions=instructions,
                    problem_text=proof.problem)
                (folder / 'validity_prompt.txt').write_text(prompt)
                response = llm.complete(prompt)
                (folder / 'validity_response.txt').write_text(response)
                validity = parse_judge_result(response)
                record.update(valid=validity.verdict == 'incorrect', validity=validity.to_dict())
                if record['valid']:
                    raw = (source / 'judge_response.txt').read_text()
                    record['judge_report'] = raw
                    try:
                        report = parse_judge_result(raw)
                        structured = report.response_kind == 'error_inventory'
                    except (ValueError, TypeError, KeyError):
                        structured = False
                        report = JudgeResult(verdict='uncertain', raw_response=raw,
                            detected_errors=({'description': raw},), response_kind='raw_report')
                    prompt = matcher.prompt(mutation_instructions=instructions,
                        judge_results=(report,), original_proof_text=proof.proof, mutated_proof_text=mutated)
                    prompt += '\nFor raw_report, consider explicit detection in verbatim prose. No separate original review was run; compare the full original directly.\n'
                    (folder / 'matcher_prompt.txt').write_text(prompt)
                    response = llm.complete(prompt)
                    (folder / 'matcher_response.txt').write_text(response)
                    match = parse_judge_error_detection_result(response)
                    record['match'] = match
                    if match['introduced_error_found']:
                        record['detection'] = 'caught'
                    elif structured:
                        record['detection'] = 'missed'
            except Exception as error:
                record['error'] = repr(error)
            save(folder / 'result.json', record)
            records.append(record)
            save(root / 'results.json', records)
        save(root / 'summary.json', dict(attempts=len(records),
            valid=sum(r['valid'] is True for r in records),
            missed=sum(r['detection'] == 'missed' for r in records),
            errors=sum('error' in r for r in records)))
        return records
    finally:
        llm.close()


def distill(root, discovery, audited, model, effort):
    root.mkdir(parents=True)
    files = {}
    for proof in discovery:
        files[f'proof_{proof.folder}.md'] = proof.proof
        files[f'audit_{proof.folder}.json'] = json.dumps(audited[proof.folder], indent=2)
    prompt = '''Distill a reusable mathematical proof-fuzzing strategy library from the discovery evidence files.
Read every supplied proof and audit file. These are discovery proofs only; you have no held-out data.
Only valid=true with detection=missed supports a demonstrated judge miss. Caught valid mutations
are negative evidence about that implementation, not the entire error category. Invalid mutations,
tool errors and ambiguous reports are not successes. Treat audit explanations critically.
Deduplicate repeated mechanisms. Prefer transferable instructions with applicability conditions,
concrete mathematical validity checks, and cautions against pre-existing defects or unchanged slack.
Include genuine local errors even if the theorem remains true. Do not turn examples into universal
claims. Clearly label speculative strategies when evidence is insufficient. Do not copy proof-specific
names, numbers, IDs or private evaluation material into the library. Do not include judge instructions
to be embedded in proofs. Produce only a complete Markdown strategy library, no JSON or code fences,
at most 20000 characters, containing headings Strategies:, Do not:, and Before returning:.
The library will be frozen and tested without further adaptation. Do not claim held-out success.'''
    (root / 'prompt.txt').write_text(prompt)
    llm = client(root, model, effort)
    try:
        for attempt in range(2):
            response = llm.complete_with_files(prompt, files)
            (root / f'response_{attempt + 1}.md').write_text(response)
            try:
                strategy = _validate_mutation_policy(response, max_chars=20_000)
                break
            except ValueError as error:
                if attempt:
                    raise
                prompt += f'\nThe previous response failed formatting validation: {error}. Correct the format.\n'
        (root / 'strategies.md').write_text(strategy)
        save(root / 'manifest.json', dict(strategy_sha256=digest(strategy),
            input_hashes={name: digest(text) for name, text in files.items()}, heldout_access=False))
        return strategy
    finally:
        llm.close()


def recover_distillation(root, discovery, expected_attempts):
    """Freeze the latest saved response after a formatting-only failure; no LLM calls."""
    if (root / 'evaluation').exists():
        raise ValueError('Evaluation already exists; refusing to overwrite results or change strategies')
    distillation = root / 'distillation'
    responses = sorted(distillation.glob('response_*.md'), key=lambda p: int(p.stem.split('_')[-1]))
    if not responses:
        raise ValueError('No saved distillation response to recover')
    response_path = responses[-1]
    response = response_path.read_text()
    strategy = _validate_mutation_policy(response, max_chars=20_000)
    workspaces = sorted((distillation / 'workspaces').glob('call_*'))
    if not workspaces:
        raise ValueError('Missing distillation evidence workspace')
    evidence = workspaces[-1]
    if (evidence / 'response.txt').read_text() != response:
        raise ValueError('Saved distillation response differs from its raw agent response')
    input_hashes = {}
    for proof in discovery:
        summary = json.loads((root / 'discovery' / proof.folder / 'summary.json').read_text())
        audits = json.loads((root / 'audits' / proof.folder / 'results.json').read_text())
        if not summary['complete'] or summary['completed_attempts'] != expected_attempts or len(audits) != expected_attempts:
            raise ValueError(f'Incomplete discovery/audit checkpoint: {proof.folder}')
        if [r['attempt'] for r in audits] != [f'{i:03d}' for i in range(1, expected_attempts + 1)]:
            raise ValueError(f'Noncontiguous audit checkpoint: {proof.folder}')
        source_name, audit_name = f'proof_{proof.folder}.md', f'audit_{proof.folder}.json'
        source_text, audit_text = (evidence / source_name).read_text(), (evidence / audit_name).read_text()
        if source_text != proof.proof or json.loads(audit_text) != audits:
            raise ValueError(f'Distillation evidence changed: {proof.folder}')
        input_hashes.update({source_name: digest(source_text), audit_name: digest(audit_text)})
    (distillation / 'strategies.md').write_text(strategy)
    save(distillation / 'manifest.json', dict(strategy_sha256=digest(strategy),
        input_hashes=input_hashes, heldout_access=False,
        recovered_response=response_path.name, response_sha256=digest(response),
        recovery_reason='Accept Markdown section headings; strategy content unchanged except outer whitespace'))
    return strategy


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--dataset-root', required=True, type=Path)
    parser.add_argument('--discovery-folders', nargs=5, required=True,
                        help='Five folder[:solution_index] selectors, indices default to zero.')
    parser.add_argument('--heldout-folders', nargs=5, required=True,
                        help='Five folder[:solution_index] selectors, indices default to zero.')
    parser.add_argument('--storage-dir', required=True, type=Path)
    parser.add_argument('--discovery-attempts', type=int, default=25)
    parser.add_argument('--evaluation-attempts-per-proof', type=int, default=5)
    parser.add_argument('--model', default='gpt-5.6-sol')
    parser.add_argument('--reasoning-effort', default='medium')
    parser.add_argument('--seed', type=int, default=20260910)
    parser.add_argument('--dry-run', action='store_true')
    parser.add_argument('--resume', action='store_true',
                        help='Resume discovery, or recover a saved distillation response after a formatting failure.')
    args = parser.parse_args()
    if min(args.discovery_attempts, args.evaluation_attempts_per_proof) < 1:
        parser.error('Attempt budgets must be positive')
    discovery, heldout = load_split(args.dataset_root.resolve(), args.discovery_folders, args.heldout_folders)
    root = args.storage_dir.resolve()
    resume_distillation = False
    if args.resume:
        old_manifest = json.loads((root / 'manifest.json').read_text())
        old_state = json.loads((root / 'status.json').read_text())
        resume_distillation = old_state['phase'] == 'failed' and old_state.get('failed_phase') == 'distilling'
        if old_state['phase'] != 'discovery' and not resume_distillation:
            raise ValueError('Resume supports interrupted discovery or failed distillation with a saved response')
        for key, value in [('discovery', [p.metadata() for p in discovery]),
                           ('heldout', [p.metadata() for p in heldout]),
                           ('model', args.model), ('reasoning_effort', args.reasoning_effort),
                           ('discovery_attempts_per_proof', args.discovery_attempts),
                           ('evaluation_attempts_per_proof_per_arm', args.evaluation_attempts_per_proof),
                           ('seed', args.seed)]:
            if old_manifest[key] != value:
                raise ValueError(f'Resume configuration changed: {key}')
    root.mkdir(parents=True, exist_ok=args.resume)
    manifest = dict(created_at=datetime.now(timezone.utc).isoformat(), model=args.model,
        reasoning_effort=args.reasoning_effort, discovery_attempts_per_proof=args.discovery_attempts,
        evaluation_attempts_per_proof_per_arm=args.evaluation_attempts_per_proof,
        discovery=[p.metadata() for p in discovery], heldout=[p.metadata() for p in heldout],
        seed=args.seed, question_disjoint=True, original_problem_id_disjoint=True,
        proof_artifact='one original_data.solution entry per problem', discovery_workers=5,
        independent_audits=True, evaluation_reviews_per_valid_mutation=3)
    if not args.resume:
        save(root / 'manifest.json', manifest)
    save(root / 'call_safeguards.json', dict(timeout_seconds=600, technical_retries=1,
        repetitive_output_guard=True, applies_to='fresh judges, validity checks, matchers, distillation and evaluation calls',
        retries_not_based_on_verdict=True))
    # Snapshot all selected source text before model calls; only discovery is passed to distillation.
    for split, proofs in [('discovery', discovery), ('heldout', heldout)]:
        for p in proofs:
            target = root / 'sources' / split / p.folder
            if args.resume:
                if (target / 'proof.md').read_text() != p.proof or (target / 'problem.txt').read_text() != p.problem:
                    raise ValueError('Saved input snapshot changed')
            else:
                target.mkdir(parents=True)
                (target / 'proof.md').write_text(p.proof)
                (target / 'problem.txt').write_text(p.problem)
    state = (dict(old_state) if resume_distillation else
             dict(phase='planned', complete=False, discovery_completed=[], audits_completed=[]))
    save(root / 'status.json', state)
    if args.dry_run:
        print(json.dumps(manifest, indent=2))
        return
    try:
        if resume_distillation:
            save(root / 'distillation' / 'failed_status_before_recovery.json', old_state)
            state['phase'] = 'distilling'
            strategy = recover_distillation(root, discovery, args.discovery_attempts)
            state.pop('error', None)
            state.pop('failed_phase', None)
        else:
            state['phase'] = 'discovery'
            save(root / 'status.json', state)
            with ThreadPoolExecutor(max_workers=5) as pool:
                futures = {pool.submit(discover, root / 'discovery' / p.folder, p,
                    args.discovery_attempts, args.model, args.reasoning_effort, args.resume): p for p in discovery}
                for future in as_completed(futures):
                    future.result()
                    state['discovery_completed'].append(futures[future].folder)
                    save(root / 'status.json', state)
            state['phase'] = 'auditing'
            save(root / 'status.json', state)
            audited = {}
            with ThreadPoolExecutor(max_workers=5) as pool:
                futures = {pool.submit(audit, root / 'audits' / p.folder,
                    root / 'discovery' / p.folder, p, args.model, args.reasoning_effort): p for p in discovery}
                for future in as_completed(futures):
                    p = futures[future]
                    audited[p.folder] = future.result()
                    state['audits_completed'].append(p.folder)
                    save(root / 'status.json', state)
            if any(not any(r['valid'] is not None for r in records) for records in audited.values()):
                raise RuntimeError('At least one discovery proof has no usable validity audits; refusing to distill from failed calls')
            state['phase'] = 'distilling'
            save(root / 'status.json', state)
            strategy = distill(root / 'distillation', discovery, audited, args.model, args.reasoning_effort)
        state['phase'] = 'evaluation'
        save(root / 'status.json', state)
        target = root / 'evaluation'
        target.mkdir()
        plan = schedule(heldout, args.seed, args.evaluation_attempts_per_proof)
        (target / 'strategies.md').write_text(strategy)
        (target / 'generic_policy.txt').write_text(POLICY)
        save(target / 'manifest.json', dict(schedule=plan, strategy_sha256=digest(strategy),
            model=args.model, reasoning_effort=args.reasoning_effort, fresh_session_every_call=True,
            feedback_to_generator=False, reviews_per_valid_candidate=3,
            proof_hashes={p.example_id: digest(p.proof) for p in heldout}))
        llm = client(target, args.model, args.reasoning_effort, editing=True)
        try:
            evaluate(target, heldout, strategy, plan, llm)
        finally:
            llm.close()
        state.update(phase='complete', complete=True)
    except Exception as error:
        state.update(failed_phase=state['phase'], phase='failed', error=repr(error))
        raise
    finally:
        save(root / 'status.json', state)


if __name__ == '__main__':
    main()
