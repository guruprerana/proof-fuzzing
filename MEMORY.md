# Project memory

## Analysis exclusions

- Do not include the TORA dataset in future quantitative tables, comparisons, summaries, or analyses unless the user explicitly asks to restore it.

## Current best proof-fuzzing pipeline — 2026-09-10

The user identifies the following as the **best pipeline we have discovered so far** and wants it retained as the default experimental direction:

1. **Discover through repeated agent attempts.** Run persistent proof-fuzzing agents on several source proofs. Each agent iteratively introduces mathematical errors, observes blind target-judge feedback, and adapts subsequent attempts.
2. **Validate and distill.** Audit whether the mutations really introduce new logical errors and whether the judge actually misses those errors. Distill successful mechanisms into a reusable strategy library, including applicability conditions and concrete validity checks. Repeated instances of the same mechanism are not independent discoveries.
3. **Freeze and evaluate transfer.** Give the frozen strategies to fresh mutation agents on separate evaluation proofs. Compare against identical generic instructions without the strategy library, with matched attempt budgets. Do not expose evaluation feedback to later mutation sessions or evolve the library during evaluation.

This is a working project conclusion and preferred pipeline, not a claim of statistically established superiority or universal generalization.

### Evaluation protocol used in the latest pilot

- `gpt-5.6-sol`, medium reasoning; full proofs provided through files without truncation. Mutators copy the original and edit the copy, saving the introduced-error explanation separately.
- Each evaluation mutation is generated in a fresh session. Validity, blind judging, and matching also use fresh sessions.
- The validity checker sees the original proof, mutated proof, and introduced-error explanation. A genuine new local error counts even when dispensable to the final theorem.
- Each valid candidate receives three blind error-inventory reviews. Judges are instructed to find all concrete errors and do not see the original proof or private introduced-error explanation.
- A separate matcher receives both proofs, the introduced-error details, and the judge report. Exact or uniquely equivalent detection counts; unrelated complaints do not. Malformed non-detection is ambiguous, not a confirmed miss.
- Log prompts, full artifacts and diffs, responses, exposed intermediate tool events, per-session token usage, timings, and failures.
- Report validity yield; mutations missed in at least one, at least two, and all three reviews; missed-review rates; ambiguity; and duplicates. Independently audit apparent successes before stronger claims.

### Reference artifacts

- Frozen strategies: `src/proof_fuzzer/data/audited_persistent_strategies_20260909.md` and companion `.jsonl`.
- Persistent discovery runner: `scripts/run_persistent_proof_fuzzing.py`.
- Discovery validity audits: `logs/persistent_validity_audit_20260909/`.
- Matched evaluation runner: `scripts/run_matched_strategy_pilot.py`.
- Completed 50-attempt evaluation: `logs/prompt_evolution_experiments/ten_matched_50_gpt-5.6-sol_medium_20260909_202502/`.
- That directory's `results_snapshot_48.md` is an interim snapshot only; `results.json` and `summary.json` hold the completed run.

### Evidence and caveats

The completed pilot used five proofs, five mutation attempts per proof per arm (50 total). Generic instructions produced 21 validated mutations and 7 missed reviews out of 63 valid review slots; learned strategies produced 23 validated mutations and 20 missed reviews out of 69 slots. Five generic and ten strategy-guided submissions had at least one confirmed miss. Ambiguous or missing reviews count as non-misses in these conservative rates.

These are automated validity/matching results pending independent audit. The evaluation proofs had previous strategy-guided exposure, so they are not a pristine holdout. There are duplicate submissions and clustered reviews; do not interpret raw review counts as independent proof-level evidence.
