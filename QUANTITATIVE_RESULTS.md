# Quantitative Results

## Strategy-discovery results

### GPT models

| Discovery dataset | Mutation model | Source proofs / traces | Mutations generated per proof / trace | Planned attempts | Completed attempts | Independently assessed attempts | Verified misses | Miss rate among assessed | Distinct successful mechanisms within sessions | Distilled strategies |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Olympiad | GPT-6-sol (medium) | 20 | 25 | 500 | 500 | 489 | 8 | 1.6% | 8 | 8 |
| Graduate course dossiers | GPT-5.6-sol (medium) | 10 | 25 | 250 | 250 | 250 | 46 | 18.4% | 45 | 25 |
| TCS open problems | GPT-5.6-sol (medium) | 5 | 25 | 125 | 125 | 100 audited | 29 | 29.0% | 10 audited groups | 10‡ |
| Recent mathematical research | GPT-5.6-sol (medium) | 5 | 25 | 125 | 125 | 102 | 29 | 28.4% | 29 | 24† |

### Claude Opus 5

| Discovery dataset | Mutation model | Source proofs / traces | Mutations generated per proof / trace | Planned attempts | Completed attempts | Independently assessed attempts | Verified misses | Miss rate among assessed | Distinct successful mechanisms within sessions | Distilled strategies |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Olympiad (Claude Code) | Claude Opus 5 (medium) | 20 | 25 | 500 | 500 | 494 | 29 | 5.9% | 28 | 14 |
| Graduate course dossiers (Claude Code) | Claude Opus 5 (medium) | 10 | 25 | 250 | 250 | 250 | 28 | 11.2% | 27 | 16 |

## Frozen-strategy evaluation

### GPT models

| Evaluation dataset | Mutation model | Proofs / traces | Mutations generated per proof / trace (generic / strategy) | Completed candidates (generic / strategy) | Judges per valid mutation | Valid mutations (generic / strategy) | Judges missing error, generic, mean (SD) | Judges missing error, strategy, mean (SD) | Change in mean |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Olympiad | GPT-6-sol (medium) | 20 | 5 / 5 | 100 / 100 | 3 | 100 / 100 | 0.02 (0.14) | 0.02 (0.14) | 0.00 |
| Graduate course dossiers | GPT-5.6-sol (medium) | 10 | 5 / 5 | 50 / 50 | 3 | 49 / 49 | 0.33 (0.77) | **0.37 (0.83)** | **+0.04** |
| TCS open problems | GPT-5.6-sol (medium) | 5 | 5 / 5 | 25 / 25 | 3 | 21 / 23 | 0.33 (0.73) | **0.87 (1.14)** | **+0.54** |
| Recent mathematical research | GPT-5.6-sol (medium) | 5 | 5 / 5 | 25 / 25 | 3 | 25 / 25 | 0.76 (1.13) | **1.00 (1.22)** | **+0.24** |

### Claude Opus 5

| Evaluation dataset | Mutation model | Proofs / traces | Mutations generated per proof / trace (generic / strategy) | Completed candidates (generic / strategy) | Judges per valid mutation | Valid mutations (generic / strategy) | Judges missing error, generic, mean (SD) | Judges missing error, strategy, mean (SD) | Change in mean |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Olympiad (Claude Code) | Claude Opus 5 (medium) | 20 | 5 / 5 | 100 / 100 | 3 | 100 / 99 | 0.08 (0.37) | **0.24 (0.69)** | **+0.16** |
| Graduate course dossiers (Claude Code) | Claude Opus 5 (medium) | 10 | 5 / 5 | 50 / 50 | 3 | 50 / 49 | 0.30 (0.58) | **0.96 (1.22)** | **+0.66** |

Discovery mechanisms are counted within source sessions and may be merged during cross-source distillation, so the two rightmost discovery columns need not match. The TCS discovery row combines four retrospectively audited persistent runs with one completed but not yet independently assessed run; the other discovery rows used independent validity and matching during the run.

† The recent-mathematical-research discovery budget was completed on 2026-09-23 by adding the ten previously missing attempts (attempts 21–25 for each extension manuscript). All ten new attempts received independent validity and matching assessments. The 24-strategy distillation predates those attempts and has not been rerun. The frozen evaluation was subsequently extended, without changing that frozen strategy library, from three to five candidates per proof and arm and from two to three judges per valid candidate.

‡ The fifth TCS source, “Circuit and Formula Lower Bounds for the Permanent,” completed all 25 discovery attempts on 2026-09-23. All 25 received blind error-inventory judgments, but they have not yet received the retrospective independent validity, error-matching, and mechanism audit used for the original four sources. Consequently, the 29 verified misses, 29.0% miss rate, 10 mechanism groups, and 10 distilled strategies remain based on the audited 100-attempt snapshot and exclude this new run.

Every run compares a generic mutator with a frozen-strategy-guided mutator, independently checks whether the introduced error is genuine, and sends each valid mutation to multiple blind error-inventory judges. A separate matcher determines whether each judge report identified the introduced error. The mean is the total number of blind reviews that missed the introduced error divided by the number of valid mutations in that arm. Parentheses report the candidate-level sample standard deviation (SD) of the number of missed judges. Invalid mutations are excluded. The maximum is three judges.

The completed Claude Code Olympiad rerun uses the frozen selector manifest
`local_datasets/generated_proof_datasets/olympiadbench_balanced_40_v1_manifest.json`.
This corpus has 20
discovery and 20 evaluation proofs, with five each of Algebra, Combinatorics,
Geometry, and Number Theory in both splits. All 40 problem IDs and normalized problem
statements are distinct. The submitted proof artifact is the OlympiadBench run's
`full_response`, and every selected folder has `correctness.txt=TRUE`. The Gemini
discovery rerun using this same protocol remains in progress and is not included above.
The complete Claude frozen evaluation had a +0.15 proof-level paired risk difference
(3 strategy-only versus 0 generic-only successes), but did not meet its preregistered
one-sided significance threshold (exact p = 0.125, alpha = 0.01).

The completed GPT-6-sol Olympiad rerun used the same balanced 20/20 discovery and
evaluation split and the same 25-attempt discovery and 5-per-arm frozen-evaluation
budgets. Discovery generated all 500 planned mutations; 489 completed the blind
judgment and independent matching pipeline, yielding 8 verified misses and 8
within-proof mechanisms, which were distilled into 8 frozen strategies. The 11
technical failures were 5 false-positive prompt filters and 6 blind-judge parse
failures and were excluded from the assessed denominator. The prompt received only
a math-only intent clarification; the experimental objective and protocol were
otherwise unchanged. In frozen evaluation, all 100 candidates in each arm were valid
and received three blind reviews. Each arm had two candidates missed by exactly one
judge, and no candidate was missed by all three. Thus neither arm succeeded on any
of the 20 evaluation proofs: 0 strategy-only, 0 generic-only, 0 both, and 20 neither
(paired risk difference 0.00; exact one-sided p = 1.0; alpha = 0.01).

The completed Claude Code graduate-course discovery run uses
`local_datasets/generated_proof_datasets/graduate_course_dossiers_v1.json`.
This corpus has ten discovery and ten evaluation dossiers; each split contains
four algebra/number-theory, three analysis, and three geometry/topology
dossiers. The 20 disjoint source ranges are 6,542–12,926 words long and use
deterministically cleaned, checksum-verified official MIT course materials.
Discovery used the ten discovery dossiers and produced 25 usable, independently
assessed mutations per dossier. Provider session-limit failures and interrupted
orchestration records were excluded from the attempt budget; recovery restored
the same persistent Claude Code threads and continued their feedback histories.
The 28 misses represent 27 distinct within-dossier mechanisms and were distilled
into 16 cross-dossier strategies. These automated validity and matching labels
have not yet received an independent human audit.

The completed GPT-5.6-sol graduate-course discovery run used the same ten
discovery dossiers, 25-attempt budget, and seed as the Claude Code run. It
produced 250 independently assessed mutations, of which 244 were valid. The 46
blind-judge misses represent 45 distinct within-dossier mechanisms and were
distilled into 25 cross-dossier strategies. These automated validity, matching,
and mechanism labels have not yet received an independent human audit.

The Claude Code graduate-course frozen evaluation was reduced after launch from ten to five
candidates per dossier and arm. Before continuing, completed attempts were retained
within each dossier-arm cell using only original candidate index and session index,
never validity or judge outcomes; 65 of 67 completed attempts were retained and the
two excess generic attempts were excluded. The complete mapping is recorded in the
run's `import_provenance.json`. In the final 100-candidate evaluation, the strict
proof-level endpoint occurred for six of ten strategy-guided dossiers and zero of ten
generic dossiers (paired risk difference +0.60; exact one-sided p = 0.015625), which
did not meet the preregistered alpha = 0.01 threshold.

The completed GPT-5.6-sol graduate-course frozen evaluation used the 25-strategy
library distilled from the GPT-5.6-sol discovery run. It completed five fresh-session
candidates per evaluation dossier and arm; 49 of 50 candidates were valid in each
arm, and every valid candidate received three blind reviews. At the strict proof-level
endpoint, both arms succeeded on two of ten dossiers: one dossier was strategy-only,
one was generic-only, one succeeded in both arms, and seven succeeded in neither.
The paired risk difference was 0.00 and the exact one-sided p value was 0.75, so the
run did not meet the preregistered alpha = 0.01 threshold.

## Appendix: Additional strategy-discovery results

| Discovery dataset | Mutation model | Source proofs / traces | Mutations generated per proof / trace | Planned attempts | Completed attempts | Independently assessed attempts | Verified misses | Miss rate among assessed | Distinct successful mechanisms within sessions | Distilled strategies |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Graduate classical mathematics | GPT-5.6-sol (medium) | 5 | 25 | 125 | 125 | 125 | 8 | 6.4% | 8 | 7 |
| Olympiad | GPT-5.6-terra (medium) | 5 | 25 | 125 | 125 | 125 | 10 | 8.0% | 10 | 9 |
| REFLECT agent traces | GPT-5.6-terra (low) | 5 | 25 | 125 | 125 | 122 | 24 | 19.7% | 20 | 14 |
| Dependent-theorem dossier | GPT-5.6-sol (medium) | 1 | 30 | 30 | 30 | 30 | 1 | 3.3% | 1 | 1 |
| Internet-sourced proof dossiers | GPT-5.6-sol (medium) | 2 | 25 | 50 | 50 | 50 | 2 | 4.0% | 2 | 2 |

## Appendix: Additional frozen-strategy evaluation results

| Evaluation dataset | Mutation model | Proofs / traces | Mutations generated per proof / trace (generic / strategy) | Completed candidates (generic / strategy) | Judges per valid mutation | Valid mutations (generic / strategy) | Judges missing error, generic, mean (SD) | Judges missing error, strategy, mean (SD) | Change in mean |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Graduate classical mathematics* | GPT-5.6-sol (medium) | 5 | 3 / 3 | 15 / 15 | 3 | 15 / 15 | 0.00 (0.00) | **0.20 (0.77)** | **+0.20** |
| Olympiad (partial) | GPT-5.6-terra (medium) | 20 | 2.55 / 2.70 average (3 / 3 planned) | 51 / 54 | 3 | 47 / 51 | **0.49 (1.02)** | 0.45 (0.83) | −0.04 |
| REFLECT agent traces* | GPT-5.6-terra (low) | 5 | 5 / 5 | 25 / 25 | 3 | 15 / 17 | 1.73 (1.10) | **1.82 (1.38)** | **+0.09** |

The historical GPT-5.6-terra Olympiad evaluation planned 60 candidates per arm
across 20 proofs but stopped after 51 generic and 54 strategy-guided candidates.
Only 11 proofs had all six planned candidates, so its results are partial and
should be treated as exploratory.

\* Graduate classical mathematics and REFLECT used one persistent mutation session
per proof and arm, producing 3 and 5 adaptive mutations respectively. The other
evaluations used a fresh session for every mutation attempt and returned no
evaluation feedback to later mutators.

## Appendix: Result artifact index

The paths below are relative to the repository root.

| Dataset | Phase | Primary result artifacts |
|---|---|---|
| Graduate classical mathematics | Discovery and distillation | [Run directory](logs/by_dataset/graduate_math/graduate_classics_pilot_v1_gpt56sol_medium/) · [Run manifest](logs/by_dataset/graduate_math/graduate_classics_pilot_v1_gpt56sol_medium/manifest.json) · [Discovery summaries](logs/by_dataset/graduate_math/graduate_classics_pilot_v1_gpt56sol_medium/discovery/) · [Distilled strategies](logs/by_dataset/graduate_math/graduate_classics_pilot_v1_gpt56sol_medium/distillation/strategies.md) |
| Graduate classical mathematics | Frozen evaluation (persistent mutation sessions*) | [Evaluation manifest](logs/by_dataset/graduate_math/graduate_classics_pilot_v1_gpt56sol_medium/evaluation/manifest.json) · [Evaluation summary](logs/by_dataset/graduate_math/graduate_classics_pilot_v1_gpt56sol_medium/evaluation/summary.json) · [Candidate-level results](logs/by_dataset/graduate_math/graduate_classics_pilot_v1_gpt56sol_medium/evaluation/results.json) |
| Olympiad | Discovery and distillation | [Run directory](logs/by_dataset/olympiad/olympiad_distinct_terra_medium_20260910_225705/) · [Run manifest](logs/by_dataset/olympiad/olympiad_distinct_terra_medium_20260910_225705/manifest.json) · [Discovery summaries](logs/by_dataset/olympiad/olympiad_distinct_terra_medium_20260910_225705/discovery/) · [Distilled strategies](logs/by_dataset/olympiad/olympiad_distinct_terra_medium_20260910_225705/distillation/strategies.md) |
| Olympiad | Frozen evaluation (partial) | [Run manifest](logs/by_dataset/olympiad/olympiad_frozen_transfer_terra_medium_v1_clean_20260913/manifest.json) · [Run summary](logs/by_dataset/olympiad/olympiad_frozen_transfer_terra_medium_v1_clean_20260913/summary.json) · [Candidate-level results](logs/by_dataset/olympiad/olympiad_frozen_transfer_terra_medium_v1_clean_20260913/results.json) |
| Olympiad (Claude Code) | Discovery and distillation | [Run directory](logs/by_dataset/olympiad/olympiad_20_discovery_claude_opus5_default_20260921/) · [Run manifest](logs/by_dataset/olympiad/olympiad_20_discovery_claude_opus5_default_20260921/manifest.json) · [Discovery summaries](logs/by_dataset/olympiad/olympiad_20_discovery_claude_opus5_default_20260921/discovery/) · [Distilled strategies](logs/by_dataset/olympiad/olympiad_20_discovery_claude_opus5_default_20260921/distillation/strategies.md) |
| Olympiad (Claude Code) | Frozen evaluation | [Evaluation manifest](logs/by_dataset/olympiad/olympiad_20_frozen_eval_claude_opus5_default_5x3_20260922/manifest.json) · [Evaluation summary](logs/by_dataset/olympiad/olympiad_20_frozen_eval_claude_opus5_default_5x3_20260922/summary.json) · [Candidate-level results](logs/by_dataset/olympiad/olympiad_20_frozen_eval_claude_opus5_default_5x3_20260922/results.json) |
| Olympiad | Discovery and distillation (GPT-6-sol) | [Run directory](logs/by_dataset/olympiad/olympiad_20_discovery_gpt6sol_medium_25x_20260924/) · [Run manifest](logs/by_dataset/olympiad/olympiad_20_discovery_gpt6sol_medium_25x_20260924/manifest.json) · [Discovery records](logs/by_dataset/olympiad/olympiad_20_discovery_gpt6sol_medium_25x_20260924/discovery/) · [Distillation manifest](logs/by_dataset/olympiad/olympiad_20_discovery_gpt6sol_medium_25x_20260924/distillation/manifest.json) · [Distilled strategies](logs/by_dataset/olympiad/olympiad_20_discovery_gpt6sol_medium_25x_20260924/distillation/strategies.md) |
| Olympiad | Frozen evaluation (GPT-6-sol) | [Evaluation manifest](logs/by_dataset/olympiad/olympiad_20_frozen_eval_gpt6sol_medium_5x3_20260924/manifest.json) · [Evaluation summary](logs/by_dataset/olympiad/olympiad_20_frozen_eval_gpt6sol_medium_5x3_20260924/summary.json) · [Candidate-level results](logs/by_dataset/olympiad/olympiad_20_frozen_eval_gpt6sol_medium_5x3_20260924/results.json) |
| Graduate course dossiers (Claude Code) | Discovery and distillation | [Run directory](logs/by_dataset/graduate_course/graduate_course_10_discovery_claude_opus5_medium_25x_20260922/) · [Run manifest](logs/by_dataset/graduate_course/graduate_course_10_discovery_claude_opus5_medium_25x_20260922/manifest.json) · [Discovery records](logs/by_dataset/graduate_course/graduate_course_10_discovery_claude_opus5_medium_25x_20260922/discovery/) · [Distillation manifest](logs/by_dataset/graduate_course/graduate_course_10_discovery_claude_opus5_medium_25x_20260922/distillation/manifest.json) · [Distilled strategies](logs/by_dataset/graduate_course/graduate_course_10_discovery_claude_opus5_medium_25x_20260922/distillation/strategies.md) |
| Graduate course dossiers (Claude Code) | Frozen evaluation (amended to 5 per arm) | [Evaluation manifest](logs/by_dataset/graduate_course/graduate_course_10_frozen_eval_claude_opus5_medium_5x3_20260923_amended/manifest.json) · [Protocol/import provenance](logs/by_dataset/graduate_course/graduate_course_10_frozen_eval_claude_opus5_medium_5x3_20260923_amended/import_provenance.json) · [Evaluation summary](logs/by_dataset/graduate_course/graduate_course_10_frozen_eval_claude_opus5_medium_5x3_20260923_amended/summary.json) · [Candidate-level results](logs/by_dataset/graduate_course/graduate_course_10_frozen_eval_claude_opus5_medium_5x3_20260923_amended/results.json) |
| Graduate course dossiers | Discovery and distillation (GPT-5.6-sol) | [Run directory](logs/by_dataset/graduate_course/graduate_course_10_discovery_gpt56sol_medium_25x_20260923/) · [Run manifest](logs/by_dataset/graduate_course/graduate_course_10_discovery_gpt56sol_medium_25x_20260923/manifest.json) · [Discovery records](logs/by_dataset/graduate_course/graduate_course_10_discovery_gpt56sol_medium_25x_20260923/discovery/) · [Distillation manifest](logs/by_dataset/graduate_course/graduate_course_10_discovery_gpt56sol_medium_25x_20260923/distillation/manifest.json) · [Distilled strategies](logs/by_dataset/graduate_course/graduate_course_10_discovery_gpt56sol_medium_25x_20260923/distillation/strategies.md) |
| Graduate course dossiers | Frozen evaluation (GPT-5.6-sol) | [Evaluation manifest](logs/by_dataset/graduate_course/graduate_course_10_frozen_eval_gpt56sol_medium_5x3_20260923/manifest.json) · [Evaluation summary](logs/by_dataset/graduate_course/graduate_course_10_frozen_eval_gpt56sol_medium_5x3_20260923/summary.json) · [Candidate-level results](logs/by_dataset/graduate_course/graduate_course_10_frozen_eval_gpt56sol_medium_5x3_20260923/results.json) |
| REFLECT agent traces | Discovery and distillation | [Run directory](logs/by_dataset/reflect/reflect_agent_trace_transfer_terra_low_20260911_151937/) · [Run manifest](logs/by_dataset/reflect/reflect_agent_trace_transfer_terra_low_20260911_151937/manifest.json) · [Discovery summaries](logs/by_dataset/reflect/reflect_agent_trace_transfer_terra_low_20260911_151937/discovery/) · [Distilled strategies](logs/by_dataset/reflect/reflect_agent_trace_transfer_terra_low_20260911_151937/distillation/strategies.md) |
| REFLECT agent traces | Frozen evaluation (persistent mutation sessions*) | [Evaluation manifest](logs/by_dataset/reflect/reflect_agent_trace_transfer_terra_low_20260911_151937/evaluation/manifest.json) · [Evaluation summary](logs/by_dataset/reflect/reflect_agent_trace_transfer_terra_low_20260911_151937/evaluation/summary.json) · [Candidate-level results](logs/by_dataset/reflect/reflect_agent_trace_transfer_terra_low_20260911_151937/evaluation/results.json) |
| Recent mathematical research | Discovery | [Pilot-three run](logs/by_dataset/recent_math/runs/recent_math_research_clean_pilot3_v1_gpt56sol_medium/) · [Extension-two run](logs/by_dataset/recent_math/runs/recent_math_research_clean_extension2_v1_gpt56sol_medium/) |
| Recent mathematical research | Distillation | [Distillation run](logs/by_dataset/recent_math/runs/recent_math_research_clean_all5_distillation_v1_gpt56sol_medium/) · [Distilled strategies](logs/by_dataset/recent_math/runs/recent_math_research_clean_all5_distillation_v1_gpt56sol_medium/distillation/strategies.md) |
| Recent mathematical research | Frozen evaluation | [Combined manifest](logs/by_dataset/recent_math/runs/recent_math_clean_all5_v1_gpt56sol_medium_25perarm_3judges_combined_20260923/manifest.json) · [Combined summary](logs/by_dataset/recent_math/runs/recent_math_clean_all5_v1_gpt56sol_medium_25perarm_3judges_combined_20260923/summary.json) · [Candidate-level results](logs/by_dataset/recent_math/runs/recent_math_clean_all5_v1_gpt56sol_medium_25perarm_3judges_combined_20260923/results.json) |
| TCS open problems | Discovery and audit | [Nonsofic-groups run](logs/by_dataset/tcs_open_problems/ten_persistent_25train_03_nonsofic_groups_gpt-5.6-sol_medium_20260908_235224/) · [Connes-rigidity run](logs/by_dataset/tcs_open_problems/ten_persistent_25train_04_connes_rigidity_conjecture_gpt-5.6-sol_medium_20260908_235224/) · [Arithmetic-circuit run (unaudited)](logs/by_dataset/tcs_open_problems/ten_persistent_25train_05_arithmetic_circuit_complexity_gpt-5.6-sol_medium_20260923/) · [Ehrhart-volume run](logs/by_dataset/tcs_open_problems/ten_persistent_25train_08_ehrhart_volume_conjecture_gpt-5.6-sol_medium_20260908_235224/) · [Extremal-number run](logs/by_dataset/tcs_open_problems/ten_persistent_25train_10_extremal_number_conjectures_gpt-5.6-sol_medium_20260908_235224/) |
| TCS open problems | Distillation | [Audited strategy library](src/proof_fuzzer/data/audited_persistent_strategies_20260909.md) · [Machine-readable strategies](src/proof_fuzzer/data/audited_persistent_strategies_20260909.jsonl) |
| TCS open problems | Frozen evaluation | [Evaluation summary](logs/by_dataset/tcs_open_problems/ten_matched_50_gpt-5.6-sol_medium_20260909_202502/summary.json) · [Candidate-level results](logs/by_dataset/tcs_open_problems/ten_matched_50_gpt-5.6-sol_medium_20260909_202502/results.json) |
| Dependent-theorem dossier | Discovery and distillation | [Run directory](logs/by_dataset/dependent_theorems/dependency_range_learning/) · [Run manifest](logs/by_dataset/dependent_theorems/dependency_range_learning/manifest.json) · [Discovery summaries](logs/by_dataset/dependent_theorems/dependency_range_learning/discovery/) · [Distilled strategies](logs/by_dataset/dependent_theorems/dependency_range_learning/distillation/strategies.md) |
| Internet-sourced proof dossiers | Discovery and distillation | [Run directory](logs/by_dataset/internet_dossiers/discovery/) · [Run manifest](logs/by_dataset/internet_dossiers/discovery/manifest.json) · [Discovery summaries](logs/by_dataset/internet_dossiers/discovery/discovery/) · [Distilled strategies](logs/by_dataset/internet_dossiers/discovery/distillation/strategies.md) |
