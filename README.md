# proof-fuzzing

The active pipeline discovers diverse judge-miss mechanisms, distills them into a
strategy library, and evaluates that library against generic guidance on held-out
examples.

## Repository layout

- `src/proof_fuzzer/`: active pipeline, model clients, benchmark loaders, and adapters.
- `src/proof_fuzzer/datasets/`: adapters from source datasets to the generic
  `ProofExample` contract.
- `scripts/run_strategy_transfer.py`: supported command-line entry point.
- `tests/`: active unit and pipeline tests.
- `src/archive/`: superseded pipelines, semiformalization, historical commands,
  and historical tests retained for reproducibility.
- `local_datasets/` and `logs/`: ignored local inputs and generated artifacts.

The orchestration API is dataset-agnostic:

```python
from pathlib import Path
from src.proof_fuzzer import run_strategy_transfer

run_strategy_transfer(
    discovery=discovery_examples,
    heldout=heldout_examples,
    storage_dir=Path("logs/my_run"),
    model="gpt-5.6-terra",
    reasoning_effort="medium",
)
```

Each example supplies `example_id`, `problem`, and `proof`; optional `metadata()` or
`to_metadata()` methods add provenance to the run manifest. This contract allows the
same pipeline to consume OlympiadBench, OpenAI Ten, IMO-GradeBench, ProofBenchJudge,
REFLECT, MedPRMBench, or new datasets through small adapters.

`src.proof_fuzzer.datasets.adapt_examples` handles records whose proof text uses a
different attribute, such as `response` in IMO-GradeBench. The existing benchmark
loaders and provider clients remain active; only their superseded orchestration was
archived.

See [scripts/README.md](scripts/README.md) for the current CLI. Run tests with:

```bash
.venv/bin/python -m unittest discover -s tests
```
