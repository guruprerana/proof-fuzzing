# proof-fuzzing

The active experimental pipeline has two deliberately separated stages:

1. persistent discovery agents find diverse judge-miss mechanisms, which are
   validated and distilled into a strategy library; and
2. a frozen evaluator compares that library with generic guidance on untouched
   held-out examples, using a fresh mutation session for every candidate and no
   feedback between evaluation candidates.

Keeping evaluation separate prevents held-out results from changing the strategy
library or influencing later mutations.

## Repository layout

- `src/proof_fuzzer/`: active pipeline, model clients, benchmark loaders, and adapters.
- `src/proof_fuzzer/datasets/`: adapters from source datasets to the generic
  `ProofExample` contract.
- `scripts/run_strategy_transfer.py`: discovery and distillation entry point; use
  `--discovery-only` for the current experimental pipeline.
- `scripts/run_frozen_strategy_evaluation.py`: preregistered, fresh-session held-out
  evaluation for a frozen strategy library.
- `tests/`: active unit and pipeline tests.
- `src/archive/`: superseded pipelines, semiformalization, historical commands,
  and historical tests retained for reproducibility.
- `local_datasets/` and `logs/`: ignored local inputs and generated artifacts.

The discovery and distillation API is dataset-agnostic:

```python
from pathlib import Path
from src.proof_fuzzer import run_strategy_transfer

run_strategy_transfer(
    discovery=discovery_examples,
    heldout=[],
    storage_dir=Path("logs/my_run"),
    model="gpt-5.6-terra",
    reasoning_effort="medium",
    run_evaluation=False,
)
```

The resulting frozen library is `logs/my_run/distillation/strategies.md`. Evaluate
it in a separate run with `src.proof_fuzzer.frozen_evaluation.run_frozen_evaluation`
or `scripts/run_frozen_strategy_evaluation.py`. The latter creates one fresh session
per candidate, exposes no evaluation feedback to other candidates, and reports the
paired proof-level endpoint.

`run_strategy_transfer` still supports its original integrated persistent-session
evaluation when `run_evaluation=True`. That mode is retained for reproduction and
adaptive exploratory experiments; it is not the current frozen-evaluation protocol.

Each example supplies `example_id`, `problem`, and `proof`; optional `metadata()` or
`to_metadata()` methods add provenance to the run manifest. This contract allows the
same pipeline to consume OlympiadBench, OpenAI Ten, IMO-GradeBench, ProofBenchJudge,
REFLECT, MedPRMBench, or new datasets through small adapters.

`src.proof_fuzzer.datasets.adapt_examples` handles records whose proof text uses a
different attribute, such as `response` in IMO-GradeBench. The existing benchmark
loaders and provider clients remain active; only their superseded orchestration was
archived.

## Command-line agent clients

Claude Code and Gemini CLI use the same `complete` / `complete_with_files`
protocol as the Codex client. Every call starts a fresh, non-persistent process in
a new `call_XXXXXX` directory. The agent can read and write files inside that
directory; shell, web, MCP, extension, and subagent tools are not exposed.

```python
from pathlib import Path
from src.proof_fuzzer import (
    ClaudeCodeProofFuzzerClient,
    GeminiCLIProofFuzzerClient,
)

claude = ClaudeCodeProofFuzzerClient(
    workspace_root=Path("logs/run/claude_workspaces"),
    model="sonnet",
    reasoning_effort="medium",
    log_events=True,
    call_timeout_seconds=600,
    detect_repetitive_output=True,
    technical_retries=1,
)
gemini = GeminiCLIProofFuzzerClient(
    workspace_root=Path("logs/run/gemini_workspaces"),
    model="gemini-3.5-flash",
    log_events=True,
    call_timeout_seconds=600,
    detect_repetitive_output=True,
    technical_retries=1,
)

response = claude.complete_with_files(
    "Read proof.md and return the requested audit.",
    {"proof.md": "..."},
)
```

The corresponding `claude` or `gemini` executable must be installed and already
authenticated. `metadata.json`, `response.txt`, failure/retry records, and optional
JSONL event traces are retained with the experiment artifacts. Each completed
call records locally measured wall-clock time plus normalized input, cached,
cache-write, output, reasoning, and total token counts. Provider duration, cost,
and turn count are included when exposed by the CLI or SDK. The same information
is available as `client.last_result.usage`. Set
`mutation_file_editing=True` to use the existing full-proof file mutation protocol.

See [scripts/README.md](scripts/README.md) for the current CLI. Run tests with:

```bash
.venv/bin/python -m unittest discover -s tests
```
