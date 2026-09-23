# Supported workflow

The current experimental pipeline uses two separate commands:

1. persistent discovery agents make repeated mutation attempts;
2. independent agents validate errors, measure judge detection, and classify novelty;
3. discovery mechanisms are deduplicated into a frozen strategy library; and
4. a separate evaluator compares generic and strategy-guided mutation on held-out
   examples, with one fresh session per candidate and no feedback between candidates.

Run `run_strategy_transfer.py --discovery-only` for steps 1–3, then pass its
`distillation/strategies.md` artifact to `run_frozen_strategy_evaluation.py` for
step 4. This separation prevents evaluation evidence from changing the library or
influencing later evaluation candidates.

The orchestration function `src.proof_fuzzer.run_strategy_transfer` accepts any objects
implementing the small `ProofExample` protocol (`example_id`, `problem`, and `proof`).
This is the integration point for OpenAI Ten, IMO-GradeBench, ProofBenchJudge, REFLECT,
MedPRMBench, and future datasets. Dataset-specific loading and splitting stay outside the
pipeline. The CLI accepts either the OlympiadBench adapter or a dataset-neutral `--split-json`;
additional adapters belong in `src/proof_fuzzer/datasets/`, without duplicating the pipeline.

```bash
.venv/bin/python scripts/run_strategy_transfer.py \
  --dataset-root /path/to/olympiadbench \
  --storage-dir logs/strategy_discovery/run_name \
  --olympiad-split-manifest local_datasets/generated_proof_datasets/olympiadbench_balanced_40_v1_manifest.json \
  --model gpt-5.6-terra \
  --reasoning-effort medium \
  --discovery-only
```

The local Olympiad manifest selects 40 unique text-only problem IDs. Discovery
and evaluation each contain exactly five Algebra, Combinatorics, Geometry, and Number
Theory examples. The adapter submits each selected `full_response`, requires its
`correctness.txt` label to be `TRUE`, and rejects duplicate IDs or normalized problem
statements. Explicit `--discovery-folders` and `--heldout-folders` remain available,
but each must contain 20 selectors and pass the same balance and correctness checks.

To run discovery and distillation entirely through restricted Claude Code processes:

```bash
.venv/bin/python scripts/run_strategy_transfer.py \
  --split-json local_datasets/generated_proof_datasets/olympiadbench_balanced_40_v1.json \
  --storage-dir logs/by_dataset/olympiad/claude_discovery_run \
  --provider claude-code \
  --model sonnet \
  --reasoning-effort medium \
  --discovery-attempts 25 \
  --discovery-workers 20 \
  --discovery-only
```

Each proof gets one resumable Claude conversation across its mutation attempts. The
blind judge, validity checker, introduced-error matcher, novelty classifier, and
distiller are fresh Claude processes. The manifest records Claude Code for every role.

Gemini CLI can be selected in the same way:

```bash
.venv/bin/python scripts/run_strategy_transfer.py \
  --split-json local_datasets/generated_proof_datasets/olympiadbench_balanced_40_v1.json \
  --storage-dir logs/by_dataset/olympiad/gemini_discovery_run \
  --provider gemini-cli \
  --model gemini-3.5-flash \
  --discovery-attempts 25 \
  --discovery-workers 20 \
  --discovery-only
```

This routes every model role to restricted Gemini CLI processes and uses one resumable
Gemini conversation per proof. Gemini CLI currently has no reasoning-effort option, so
its manifests record `reasoning_effort: null`, the requested value separately, and
`provider_supports_reasoning_effort: false`.

All prompts, responses, event streams, full mutations, explanations, diffs,
assessments, feedback, and distilled strategies are saved below `--storage-dir`.
Use `--dry-run` to validate and snapshot a split without model calls.

Without `--discovery-only`, `run_strategy_transfer.py` also runs its original
persistent-session evaluation. That integrated mode is retained for reproduction and
adaptive exploratory experiments, but it is not the current frozen-evaluation
protocol.

The REFLECT process-level trace adapter currently exposes the original integrated,
adaptive workflow through its trace profile:

```bash
.venv/bin/python scripts/run_agent_trace_strategy_transfer.py \
  --dataset-root local_datasets/REFLECT \
  --storage-dir logs/prompt_evolution_experiments/reflect_run \
  --model gpt-5.6-terra \
  --reasoning-effort medium \
  --discovery-traces 5 \
  --heldout-traces 5 \
  --discovery-attempts 25 \
  --evaluation-attempts-per-trace 5
```

This adapter splits by `trace_id`, submits one complete trace at a time, and never gives
the blind judge an original/reference trace or mutation explanation. A structural guard
requires each candidate to preserve the full JSON trace and alter the content of exactly
one existing step. The original-trace control is used only by the independent matcher.
It does not yet provide the separate fresh-candidate frozen-evaluation stage described
above, so use it for reproduction or exploratory trace experiments rather than as an
implementation of the current evaluation protocol.

For the held-out stage, run independent generic and strategy-guided candidates with
three blind reviews per valid mutation:

```bash
.venv/bin/python scripts/run_frozen_strategy_evaluation.py \
  --split-json local_datasets/generated_proof_datasets/olympiadbench_balanced_40_v1.json \
  --strategy-path logs/strategy_discovery/run_name/distillation/strategies.md \
  --storage-dir logs/frozen_evaluation/run_name \
  --provider claude-code \
  --model claude-opus-5 \
  --attempts-per-arm 3
```

This command freezes the strategy hash and job order in its manifest before model
calls. Every candidate receives a fresh mutation session, evaluation feedback is not
returned to later candidates, and the primary comparison is paired at the proof level.

`distill_replicated_strategy.py` can build a subsequent library from valid mutations
missed by at least two of three independent reviews. By default it rejects incomplete
source runs; allowing partial runs is explicitly marked as exploratory.

Historical commands are under `src/archive/scripts/` and are unsupported.

For any other benchmark, `--split-json` accepts:

```json
{
  "discovery": [{"example_id": "train-1", "problem": "...", "proof": "...", "metadata": {}}],
  "heldout": [{"example_id": "test-1", "problem": "...", "proof": "...", "metadata": {}}]
}
```
