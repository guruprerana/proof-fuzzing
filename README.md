# proof-fuzzing

## Repository layout

- `src/proof_fuzzer/`: model clients, benchmark loaders, experiment pipelines,
  and shared reporting.
- `src/semi_formalization/`: proof parsing, dependency graphs, mutation logic,
  and prompts.
- `scripts/`: reusable command-line entry points; see the [script guide](scripts/README.md).
- `tests/`: unit and pipeline tests, using mocked model clients.
- `local_datasets/` and `logs/`: local datasets and generated run artifacts,
  both ignored by Git.

Run the test suite from the repository root:

```bash
python -m unittest discover -s tests
```

## File-backed Codex calls

Codex experiments use an isolated directory for every model call. The inline
turn only asks Codex to read that directory; the actual inputs are stored as:

- `prompt.txt`: task instructions and output schema
- `strategy.txt`: the current mutation strategy for generation and evolution
- `trace.json`: the benchmark trace or candidate comparison
- `outcomes.json`: bounded training evidence used during strategy evolution

Checker and judge calls do not receive `strategy.txt`. Each call directory also
records `response.txt` and `metadata.json`. Non-file-aware LLM clients retain a
compatible inline fallback for tests and alternative providers.

## Blind error detection in evolution runs

The blind target reviewer is not asked for a score or a correct/incorrect
verdict. It sees only the problem and submitted reasoning trace and returns a
structured inventory of independent, consequential root-cause errors. Repeated
manifestations and downstream symptoms are grouped; style preferences, generic
requests for detail, and broad completeness criticism are excluded.

The same blind review is run on the unmodified artifact as a control. A separate
isolated model call receives both artifacts, the mutation record, and both error
inventories. It counts the planted bug as detected only when the mutated-artifact
inventory explicitly identifies the changed premise, fact, calculation,
inference, evidence relationship, or an equivalent uniquely identifying failure.
Partial, generic downstream, and pre-existing-error matches are misses. An
invalid mutation is counted as a successful attack only when this exact-only
matcher says the introduced bug was not found.

Mutation validators also require one minimally exposed independent root-cause
failure. Prompt evolution is evidence-regularized: successful generations may
add only success-supported strategies within a bounded growth allowance, while
zero-success generations may only remove, merge, shorten, or clarify existing
instructions and cannot increase prompt length.

Initial mutation policies encourage coherent downstream propagation: dependent
claims, calculations, tool conclusions, or clinical steps may be updated when
needed to follow the planted error naturally. Such companion edits must all be
consequences of the same root cause; they cannot introduce independent defects
or gratuitous clues.

The inventory prompt is task-specific: mathematics checks proof validity,
REFLECT checks research-agent reasoning/tool/evidence failures, and MedPRMBench
checks clinical facts, dependencies, applicability, safety, time, and quantity.
All three share the same root-cause grouping, clean-control, and exact-match
evaluation rules.

## MedPRMBench medical-reasoning benchmark

The MedPRMBench v1 paper ([arXiv:2604.17282](https://arxiv.org/abs/2604.17282))
describes a 6,500-question evaluation set and names `test_benchmark.jsonl`, but
does not currently link a public data repository. The repository can still run
an evaluation on the 14 representative clean/corrupted reasoning traces printed
in the paper appendix:

```bash
python scripts/fetch_medprmbench_paper_examples.py
python scripts/run_medprmbench_codex_prompt_experiment.py \
  --train-examples 5 \
  --test-examples 5 \
  --training-generations 3
```

The first command downloads the arXiv source, extracts one example for each of
the paper's 14 medical error types, and records the source archive hash. Dataset
files stay under the git-ignored `local_datasets/` directory because the paper
does not state a dataset redistribution license.

To use the full release once it is available, pass its JSONL directly:

```bash
python scripts/run_medprmbench_codex_prompt_experiment.py \
  --dataset-file /path/to/test_benchmark.jsonl \
  --train-examples 50 \
  --test-examples 100
```

The loader accepts the repository's canonical schema as well as common
process-reward aliases (`original_steps`/`modified_steps`,
`positive`/`negative`, and binary `step_labels`). Training and held-out data are
split by original clinical case ID, so two corrupted variants of the same case
cannot cross the boundary. For a small medical-safety smoke test, use
`--error-types R-5 E-1 E-5 --train-examples 1 --test-examples 1`.
