# Supported command

`run_strategy_transfer.py` runs the active proof-fuzzing workflow:

1. persistent discovery agents make repeated mutation attempts;
2. independent agents validate errors, measure judge detection, and classify novelty;
3. discovery mechanisms are deduplicated into a strategy library; and
4. generic and strategy-guided persistent agents are compared on held-out examples.

The orchestration function `src.proof_fuzzer.run_strategy_transfer` accepts any objects
implementing the small `ProofExample` protocol (`example_id`, `problem`, and `proof`).
This is the integration point for OpenAI Ten, IMO-GradeBench, ProofBenchJudge, REFLECT,
MedPRMBench, and future datasets. Dataset-specific loading and splitting stay outside the
pipeline. The CLI accepts either the OlympiadBench adapter or a dataset-neutral `--split-json`;
additional adapters belong in `src/proof_fuzzer/datasets/`, without duplicating the pipeline.

```bash
.venv/bin/python scripts/run_strategy_transfer.py \
  --dataset-root /path/to/olympiadbench \
  --storage-dir logs/strategy_transfer/run_name \
  --discovery-folders 000013 000078 000231 000240 000184:1 \
  --heldout-folders 000112 000226 000273 000067 000255 \
  --model gpt-5.6-terra \
  --reasoning-effort medium
```

All prompts, responses, event streams, full mutations, explanations, diffs,
assessments, feedback, strategies, and evaluation summaries are saved below
`--storage-dir`. Use `--dry-run` to validate and snapshot a split without model calls.

Historical commands are under `src/archive/scripts/` and are unsupported.

For any other benchmark, `--split-json` accepts:

```json
{
  "discovery": [{"example_id": "train-1", "problem": "...", "proof": "...", "metadata": {}}],
  "heldout": [{"example_id": "test-1", "problem": "...", "proof": "...", "metadata": {}}]
}
```
