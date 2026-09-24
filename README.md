# proof-fuzzing

This repository contains the main proof-fuzzing experiments reported in
`QUANTITATIVE_RESULTS.md` for two model families—GPT-5.6-sol through Codex and Claude
Opus 5 through Claude Code—on four datasets:

1. Olympiad
2. Graduate course dossiers
3. TCS open problems
4. Recent mathematical research

## Experimental design

The pipeline has two deliberately separate stages:

1. Persistent discovery agents find diverse judge-miss mechanisms. Independent model
   calls validate the mutations, match blind-judge reports, classify novelty, and
   distill a strategy library.
2. A frozen evaluator compares generic and strategy-guided mutation on held-out
   proofs, using a fresh mutation session for every candidate and no feedback between
   evaluation candidates.

Keeping evaluation separate prevents held-out evidence from changing the strategy
library or influencing later candidates.

## Repository layout

- `src/proof_fuzzer/`: the active discovery, evaluation, model-client, and dataset
  loading code.
- `scripts/run_strategy_transfer.py`: discovery and distillation entry point.
- `scripts/run_frozen_strategy_evaluation.py`: fresh-session held-out evaluation.
- `scripts/resume_strategy_discovery.py`: resume support for interrupted Claude
  discovery runs.
- `tests/`: tests for the active pipeline only.
- `src/archive/`: unsupported historical code retained outside the active surface.
- `local_datasets/`: version-controlled inputs for the four datasets.
- `logs/`: ignored, machine-local run state and generated artifacts.

The canonical dataset paths and artifact boundaries are recorded in `MEMORY.md`.

## Installation

Create a Python environment and install:

```bash
python -m pip install -r requirements.txt
```

`openai-codex` supplies the Codex integration used for GPT-5.6-sol. Claude Opus 5
requires the separate `claude` executable to be installed and authenticated.

## Programmatic API

The discovery API consumes objects with `example_id`, `problem`, and `proof` fields:

```python
from pathlib import Path
from src.proof_fuzzer import run_strategy_transfer

run_strategy_transfer(
    discovery=discovery_examples,
    heldout=heldout_examples,
    storage_dir=Path("logs/my_run"),
    provider="codex",
    model="gpt-5.6-sol",
    reasoning_effort="medium",
)
```

The resulting frozen library is `logs/my_run/distillation/strategies.md`. Evaluate it
with `src.proof_fuzzer.frozen_evaluation.run_frozen_evaluation` or the frozen-evaluation
script.

Claude Code is exposed through `ClaudeCodeProofFuzzerClient`. Fresh calls run in
isolated `call_XXXXXX` directories with file operations only; shell, web, MCP,
extension, and subagent tools are disabled. Persistent sessions are used only for the
within-proof discovery loop.

See [scripts/README.md](scripts/README.md) for commands. Run the active tests with:

```bash
.venv/bin/python -m unittest discover -s tests
```
