# Main experiment workflow

The supported pipeline has two separate stages:

1. `run_strategy_transfer.py` runs persistent discovery agents,
   independent validation and matching, and strategy distillation.
2. `run_frozen_strategy_evaluation.py` compares generic and strategy-guided mutation
   on held-out proofs with a fresh session for every candidate.

The supported providers are Codex with GPT-5.6-sol and Claude Code with Claude Opus 5.
Both must already be authenticated. Python dependencies are listed in
`requirements.txt`; Claude additionally requires the `claude` executable.

## Dataset inputs

Three datasets use self-contained JSON splits:

- `local_datasets/olympiadbench_balanced_40_v1.json`
- `local_datasets/graduate_course_dossiers_v1.json`
- `local_datasets/recent_math_research_dossiers_clean_v1.json`

TCS uses the ten Markdown proofs under:

- `local_datasets/openai_ten_advances_2026/proofs_markdown/`

The TCS loader reproduces the reported five-proof discovery partition
(`03`, `04`, `05`, `08`, and `10`) and uses the other five proofs for evaluation.

## Discovery and distillation

For a JSON dataset with GPT-5.6-sol:

```bash
.venv/bin/python scripts/run_strategy_transfer.py \
  --split-json local_datasets/graduate_course_dossiers_v1.json \
  --storage-dir logs/by_dataset/graduate_course/gpt56sol_discovery \
  --provider codex \
  --model gpt-5.6-sol \
  --reasoning-effort medium \
  --discovery-attempts 25 \
  --discovery-workers 10
```

For TCS with Claude Opus 5:

```bash
.venv/bin/python scripts/run_strategy_transfer.py \
  --tcs-root local_datasets/openai_ten_advances_2026/proofs_markdown \
  --storage-dir logs/by_dataset/tcs_open_problems/opus5_discovery \
  --provider claude-code \
  --model claude-opus-5 \
  --reasoning-effort medium \
  --discovery-attempts 25 \
  --discovery-workers 5
```

Judge, assessment, and distillation calls normally have a 20-minute wall-clock
timeout. Pass `--no-call-timeout` to let those calls finish without a hard time
limit. The same flag is available on `resume_strategy_discovery.py` when resuming
an interrupted Claude discovery run.

Each proof gets one persistent mutation conversation during discovery. Blind judges,
validators, matchers, novelty classifiers, and the distiller use fresh calls. All run
artifacts are written below `--storage-dir`. Use `--dry-run` to validate and snapshot
the split without model calls.

If a Claude discovery run is interrupted by quota exhaustion, resume it with
`resume_strategy_discovery.py` and the same `--split-json` or `--tcs-root` input.
Provider-native session state must still be available on that machine.

## Frozen evaluation

```bash
.venv/bin/python scripts/run_frozen_strategy_evaluation.py \
  --split-json local_datasets/graduate_course_dossiers_v1.json \
  --strategy-path logs/by_dataset/graduate_course/gpt56sol_discovery/distillation/strategies.md \
  --storage-dir logs/by_dataset/graduate_course/gpt56sol_frozen_eval \
  --provider codex \
  --model gpt-5.6-sol \
  --reasoning-effort medium \
  --attempts-per-arm 5 \
  --reviews-per-valid-candidate 3
```

Judge and assessment calls normally have a 20-minute wall-clock timeout. Pass
`--no-call-timeout` to allow those calls to finish without a hard time limit. The
selected policy is frozen in the evaluation manifest as `call_timeout_seconds`.

For TCS, replace `--split-json ...` with:

```text
--tcs-root local_datasets/openai_ten_advances_2026/proofs_markdown
```

The evaluator freezes the strategy hash and job order before model calls. Evaluation
feedback is never returned to later mutation candidates.
