# Repository agent instructions

## Start here

- Read `MEMORY.md` before substantive work. It records the current project scope,
  experimental protocol, artifact boundaries, and standing analysis decisions.
- Read `README.md` and `scripts/README.md` before changing orchestration code.
- Treat `QUANTITATIVE_RESULTS.md` and `QUALITATIVE_RESULTS.md` as the reporting
  sources of truth. Do not copy numerical results into other files unless needed.

## Current scope

The active headline study covers exactly four datasets:

1. Olympiad
2. Graduate course dossiers
3. TCS open problems
4. Recent mathematical research

Canonical run inputs are version-controlled under `local_datasets/`. The original
graduate-course, recent-research, and TCS PDFs approved for provenance are tracked
there as well. Do not add other raw downloads, generated walkthroughs, extraction
workspaces, cloned benchmark repositories, caches, or superseded datasets. The exact
tracked paths are documented in `MEMORY.md` and allowlisted in `.gitignore`.

Historical adapters and results for other datasets may remain in code or appendices,
but they are not part of the current headline study. Do not restore their local data
unless the user explicitly asks.

## Experimental workflow

- Use `scripts/run_strategy_transfer.py` for discovery and distillation.
- Use `scripts/run_frozen_strategy_evaluation.py` for held-out evaluation.
- Keep evaluation sessions fresh and independent. Do not feed evaluation feedback
  into later candidates or modify a frozen strategy library during evaluation.
- `src/archive/` contains unsupported historical workflows; prefer active code under
  `src/proof_fuzzer/` and `scripts/`.

## Artifact and Git boundaries

- `logs/` contains local run state, transcripts, feedback, assessments, manifests,
  and generated strategy libraries. It is intentionally ignored and is not available
  on a fresh clone unless transferred separately.
- `src/proof_fuzzer/data/` tracks only the audited TCS strategy library used by the
  headline evaluation; other generated libraries remain ignored.
- Never commit `.env`, credentials, provider session stores, caches, or machine-local
  absolute paths.
- Repository-level coding-agent context belongs in this file and `MEMORY.md`; keep
  both version-controlled and update them when durable project decisions change.

## Change discipline

- Preserve unrelated user changes and do not commit unless explicitly requested.
- Update path references, documentation, and tests together when moving canonical
  inputs or entry points.
- Run targeted tests and `git diff --check` after changes. If a required test tool is
  unavailable, report that explicitly.
