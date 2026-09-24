# Archived pipelines

This directory preserves superseded experimental implementations for reproducibility.
They are not part of the supported proof-fuzzing API and receive no compatibility
guarantees.

- `proof_fuzzer/` contains the earlier evolutionary, prompt-evolution, matched-pilot,
  mutation-detection, robustness, dataset-specific orchestration, Gemini, and vLLM
  code.
- `data/` contains strategy data that is not used by the supported experiments.
- `semi_formalization/` contains the discontinued parser, proof graph, mutation planner,
  and autoformalization prompts.
- `scripts/` contains the corresponding historical launchers.
- `tests/` contains historical tests that document those implementations but are not
  included in the active test suite.

The supported pipeline lives in `src/proof_fuzzer/strategy_transfer.py`, with frozen
evaluation in `src/proof_fuzzer/frozen_evaluation.py`. It supports only Codex with
GPT-5.6 and Claude Code with Opus 5 over the four canonical datasets documented in
the repository root. Archived modules and tests are retained as historical source,
not as a maintained or independently runnable package.
