# Scripts

Run these entry points from the repository root with `python scripts/<name>.py`.
Each executable Python script supports `--help` for its inputs and model options.
Shared experiment logic belongs in `src/proof_fuzzer/`.

## Dataset preparation

- `fetch_medprmbench_paper_examples.py`: download the paper source and extract
  its appendix examples, including source provenance.

## Evolution runs

- `run_imo_gradebench_evolution.py`: fuzz correct IMO-GradeBench proofs.
- `run_openai_ten_advances_codex_evolution.py`: fuzz the ten-advances proofs with Codex.
- `run_proof_bench_judge_codex_evolution.py`: fuzz ProofBenchJudge with Codex.
- `_codex_evolution_cli.py`: shared argument handling for the two Codex evolution
  runners; this is an internal helper, not a standalone command.

## Prompt and strategy experiments

- `run_medprmbench_codex_prompt_experiment.py`: train and evaluate a mutation
  prompt on medical reasoning traces.
- `run_reflect_codex_prompt_experiment.py`: train and evaluate a mutation prompt
  on REFLECT research-agent traces.
- `run_openai_ten_advances_codex_prompt_experiment.py`: train and evaluate a
  single mutation prompt on the ten-advances proofs.
- `run_openai_ten_advances_codex_strategy_bank_experiment.py`: train and evaluate
  a bank of mutation strategies on the ten-advances proofs.

## Evaluation of existing runs

- `run_competition_judge_robustness.py`: replay successful attacks with an
  alternate grading prompt.
- `run_mutation_detection_experiment.py`: compare mutation detection on stored attempts.
- `run_pre_mutation_baseline_judge.py`: judge the original proofs from successful attacks.

## Run artifacts and reports

Prompt experiments persist `summary.json`, configuration, splits, and detailed
attempt records in their run directories. Use those artifacts for ad hoc analysis
and presentation-specific reports. Reusable reporting code lives in
`src/proof_fuzzer/reporting.py`; standalone report formatters and generic shell
retry wrappers are not maintained here.
