# Archived pipelines

This directory preserves superseded experimental implementations for reproducibility.
They are not part of the supported proof-fuzzing API and receive no compatibility
guarantees.

- `proof_fuzzer/` contains the earlier evolutionary, prompt-evolution, matched-pilot,
  mutation-detection, robustness, baseline, and Olympiad-specific orchestration code.
- `semi_formalization/` contains the discontinued parser, proof graph, mutation planner,
  and autoformalization prompts.
- `scripts/` contains the corresponding historical launchers.
- `tests/` contains historical tests that document those implementations but are not
  included in the active test suite.

The supported pipeline lives in `src/proof_fuzzer/strategy_transfer.py`. It consumes
the `ProofExample` protocol and is therefore not tied to OlympiadBench. Dataset adapters
belong in `src/proof_fuzzer/datasets/`.

The archived tests remain runnable with
`.venv/bin/python -m unittest discover -s src/archive/tests`.
