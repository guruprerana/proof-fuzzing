# Project memory

Last updated: 2026-09-24.

## Current project scope

The headline study covers exactly four datasets:

1. Olympiad
2. Graduate course dossiers
3. TCS open problems
4. Recent mathematical research

Do not add other datasets to the headline quantitative tables, comparisons, summaries,
active code, or bundled inputs unless the user explicitly changes the scope.

The current planned extension is to run Claude Opus 5 on the TCS open-problems setup
used for the GPT-5.6-sol headline result, including discovery and frozen evaluation as
appropriate. Work may be parallelized across machines.

## Canonical version-controlled inputs

Only self-contained inputs needed by the current runs belong in Git:

- `local_datasets/olympiadbench_balanced_40_v1.json`
- `local_datasets/olympiadbench_balanced_40_v1_manifest.json`
- `local_datasets/graduate_course_dossiers_v1.json`
- `local_datasets/recent_math_research_dossiers_clean_v1.json`
- `local_datasets/openai_ten_advances_2026/proofs_markdown/*.md`

The three split JSON files contain both discovery and held-out examples. The TCS
directory contains the ten Markdown proofs; the reported GPT-5.6-sol study used five
of them. Do not reintroduce raw PDFs, downloaded source archives, extraction and
cleaning workspaces, nested benchmark repositories, caches, or superseded splits.

## Preferred proof-fuzzing pipeline

This remains the default experimental direction:

1. **Discover through repeated attempts.** Persistent mutation agents work on source
   proofs, observe blind-judge feedback, and adapt within each discovery session.
2. **Validate and distill.** Independently check that mutations introduce genuine new
   errors, determine whether blind judges detected them, classify mechanisms, and
   distill distinct successful mechanisms into a reusable strategy library.
3. **Freeze and evaluate transfer.** Compare generic guidance with the frozen strategy
   library on held-out proofs using matched budgets and a fresh mutation session for
   every candidate. Never return evaluation feedback to later candidates and never
   evolve the library during evaluation.

This is the preferred protocol, not a claim of universal or statistically established
superiority.

### Evaluation requirements

- Supply full proofs through files without truncation. Mutators copy the original,
  edit the copy, and save the introduced-error explanation separately.
- Use fresh sessions for evaluation mutation, validity checking, blind judging, and
  matching.
- A genuine new local mathematical error may be valid even if it is dispensable to
  the final theorem.
- Give each valid candidate three blind error-inventory reviews. Blind judges do not
  see the original proof or the private introduced-error explanation.
- Use a separate matcher to decide whether a review found the introduced error. An
  exact or uniquely equivalent identification counts; unrelated complaints do not.
  Treat malformed non-detection as ambiguous rather than a confirmed miss.
- Report validity yield, candidate-level missed-review counts, proof-level paired
  outcomes, ambiguity, duplicates, and failures. Independently audit apparent
  successes before making stronger claims.

## Active entry points and reporting sources

- Discovery and distillation: `scripts/run_strategy_transfer.py`
- Frozen evaluation: `scripts/run_frozen_strategy_evaluation.py`
- Resume interrupted CLI-provider discovery: `scripts/resume_strategy_discovery.py`
- Workflow documentation: `README.md` and `scripts/README.md`
- Numerical source of truth: `QUANTITATIVE_RESULTS.md`
- Worked examples and interpretation: `QUALITATIVE_RESULTS.md`

Use the result documents rather than duplicating numerical snapshots here; they are
updated more frequently than this memory file.

## Artifact boundaries

- `logs/` stores prompts, mutations, feedback, assessments, manifests, transcripts,
  session metadata, usage, results, and distilled libraries. It is intentionally
  ignored by Git and is machine-local unless transferred separately.
- `src/proof_fuzzer/data/` tracks the audited TCS strategy library used by the
  headline evaluation. Other generated strategy libraries remain ignored.
- Provider-native session stores and resumable conversation state are machine-local.
  A thread ID or run directory alone may not make a provider session portable.
- Never commit `.env`, credentials, tokens, caches, or machine-specific session data.
- `AGENTS.md` and this file are the version-controlled repository context for coding
  agents. Update them whenever a durable project decision changes.

Historical result links may point into ignored local `logs/` directories. Do not
assume those artifacts exist on a fresh clone, and do not confuse their presence on
one workstation with Git tracking.
