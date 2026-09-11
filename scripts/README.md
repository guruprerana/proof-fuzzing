# Scripts

Run these entry points from the repository root with `python scripts/<name>.py`.
Each executable Python script supports `--help` for its inputs and model options.
Shared experiment logic belongs in `src/proof_fuzzer/`.

## Dataset preparation

- `fetch_medprmbench_paper_examples.py`: download the paper source and extract
  its appendix examples, including source provenance.

## Evolution runs

- `run_imo_gradebench_evolution.py`: fuzz correct IMO-GradeBench proofs.
- `run_openai_ten_advances_codex_evolution.py`: fuzz the ten-advances proofs with Codex.
- `run_proof_bench_judge_codex_evolution.py`: fuzz ProofBenchJudge with Codex.
- `_codex_evolution_cli.py`: shared argument handling for the two Codex evolution
  runners; this is an internal helper, not a standalone command.

## Prompt and strategy experiments

- `run_mechanism_strategy_transfer.py`: adaptive Olympiad transfer experiment that
  scores discovery attempts for distinct, validated error mechanisms. It runs one
  persistent session per proof, feeds validity/detection/novelty assessments back
  after every attempt, deduplicates mechanisms during distillation, and compares
  persistent generic and strategy-guided sessions on the held-out split. Discovery
  and evaluation budgets are configurable; defaults are 25 and 5 attempts per
  proof/arm. All prompts, responses, event streams, diffs, assessments, and summaries
  are stored below `--storage-dir`.

- `run_olympiad_strategy_transfer.py`: end-to-end problem-disjoint transfer experiment.
  Select five `--discovery-folders` and five `--heldout-folders` under `--dataset-root`.
  A selector such as `000184:1` chooses solution entry 1 rather than concatenating
  alternative proofs. The loader rejects repeated problem IDs/questions and image-dependent
  sources. Five persistent agents each make 25 discovery attempts, followed by fresh-agent
  validity/matching audits, discovery-only strategy distillation, and a frozen 50-attempt
  matched evaluation on held-out problems. All stages are logged under `--storage-dir`;
  `status.json` tracks the active phase. `--dry-run` snapshots the split without model calls.
  Budgets are adjustable with `--discovery-attempts` and `--evaluation-attempts-per-proof`.
  This uses reference `original_data.solution` entries, not generated reasoning traces.
  Fresh review/check calls have a 600-second streaming deadline, a long-repetitive-output
  guard, and at most one technical retry; mathematical verdicts and schema failures do
  not trigger retries. `--resume` supports interrupted discovery with an identical split
  and budget: completed attempts are reused, a saved pending candidate is rejudged once,
  and an ephemeral mutator restart is explicitly reconstructed from saved feedback/notes.
  `--resume` also recovers a failed distillation from its latest saved response, checking
  that discovery/audit evidence is unchanged and evaluation has not already started.
  Plain and Markdown section headings are accepted; no new distillation call is needed
  for a heading-format mismatch.

Strategy libraries are local experiment inputs, not bundled source code. The local
audited guidance from the persistent-agent runs can be found in
`src/proof_fuzzer/data/audited_persistent_strategies_20260909.jsonl` (10 loader-compatible
strategies, with validity checks and per-attempt provenance) and the companion `.md`
(a standalone mutation-policy prompt, suitable for the 20k policy budget).
For runners exposing strategy seeding, pass `--seed-mined-strategies --mined-strategy-path
src/proof_fuzzer/data/audited_persistent_strategies_20260909.jsonl`, or set the equivalent
`EvolutionConfig` fields. The standalone persistent runner does not currently load this
library automatically. No existing run or default strategy bank is changed by adding it.
Observed audit counts are stored in metadata; runtime strategy scores start at zero.

For the persistent runner, pass `--strategies-file src/proof_fuzzer/data/audited_persistent_strategies_20260909.md`
to provide the library as a separate mutation-agent input. Use `--proof-ids ID1 ID2 ...`
to make exactly one attempt on each listed manuscript in the same persistent session.
The judge does not receive the strategy file or introduced-error explanation.

- `run_persistent_proof_fuzzing.py --storage-dir <new-directory>`: 25 attempts with
  one persistent file-editing mutator thread and fresh blind judges. No separate
  evolution, mutation-validity, original-control, or error-matcher calls. Saves full
  candidates, explanations, diffs, judge reports, prompts, timings and errors under
  `attempts/`; streams mutator events under `mutator_traces/` and judge events under
  `codex_traces/`. `summary.json` reports progress but deliberately does not claim
  verified misses. The original full manuscript is retained without truncation.

- `run_matched_strategy_pilot.py`: compare generic mutation instructions with a
  frozen Markdown strategy library. Each mutation, validity check, blind review,
  and matcher uses a fresh session. No evaluation feedback goes to the mutators.
  Each valid submission gets three blind reviews, including duplicate submissions
  (duplicates are flagged). Reports include ≥1, ≥2, and all-three missed reviews.
  Defaults to five attempts per arm on proofs 01, 02, 05, 06, and 07: 50 attempts.
  `--strategies-file` is required; `--proof-root`, `--proof-ids`,
  `--attempts-per-proof`, `--model`, and `--reasoning-effort` are configurable.
  Use `--dry-run` to save the manifest and schedule without model calls.

```bash
python scripts/run_matched_strategy_pilot.py \
  --storage-dir logs/matched_strategy_transfer_new \
  --strategies-file /path/to/frozen_strategies.md \
  --attempts-per-proof 5
```

Both agent runners preserve full proofs, exposed tool events, and token usage in
`codex_traces/call_*/{events.jsonl,result.json}`. Partial event logs survive failed
calls. Persistent mutator events are in `mutator_traces/`. Raw judge responses are
retained; malformed non-detection is ambiguous in the matched runner, not a miss.

- `run_medprmbench_codex_prompt_experiment.py`: train and evaluate a mutation
  prompt on medical reasoning traces.
- `run_reflect_codex_prompt_experiment.py`: train and evaluate a mutation prompt
  on REFLECT research-agent traces.
- `run_openai_ten_advances_codex_prompt_experiment.py`: train and evaluate a
  single mutation prompt on the ten-advances proofs.
- `run_openai_ten_advances_codex_strategy_bank_experiment.py`: train and evaluate
  a bank of mutation strategies on the ten-advances proofs.

## Evaluation of existing runs

- `run_competition_judge_robustness.py`: replay successful attacks with an
  alternate grading prompt.
- `run_mutation_detection_experiment.py`: compare mutation detection on stored attempts.
- `run_pre_mutation_baseline_judge.py`: judge the original proofs from successful attacks.

## Run artifacts and reports

Prompt experiments persist `summary.json`, configuration, splits, and detailed
attempt records in their run directories. Use those artifacts for ad hoc analysis
and presentation-specific reports. Reusable reporting code lives in
`src/proof_fuzzer/reporting.py`; standalone report formatters and generic shell
retry wrappers are not maintained here.

## Local data and historical launchers

`local_datasets/`, `logs/`, and `src/proof_fuzzer/data/` are intentionally ignored.
Provide your own proof datasets and strategy files. Strategy seeding is opt-in;
`--mined-strategy-path` selects a JSONL library. The legacy default seed path still
works when populated locally, and gives an actionable error when absent.

The hard-coded TORA, three-proof Olympiad, and single-ten-proof pilot launchers
were archived locally under `logs/archived_launchers_20260910/`, rather than
maintained as supported commands. Historical run artifacts remain untouched.
Reusable full-proof mutation, imperfect-original validation, and prompt-budget
behavior are covered by dataset-independent tests.

For programmatic prompt-evolution training, use `run_prompt_evolutionary_pipeline`
and `training_prompt_config` from `src.proof_fuzzer.prompt_evolution`. The latter
provides a 20,000-character absolute policy budget, including after failed attempts.
