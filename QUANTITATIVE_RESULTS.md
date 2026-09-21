# Quantitative Results

## Strategy-discovery results

| Discovery dataset | Mutation model | Source proofs / traces | Mutations generated per proof / trace | Planned attempts | Completed attempts | Independently assessed attempts | Verified misses | Miss rate among assessed | Distinct successful mechanisms within sessions | Distilled strategies |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Graduate classical mathematics | GPT-5.6-sol (medium) | 5 | 25 | 125 | 125 | 125 | 8 | 6.4% | 8 | 7 |
| Olympiad | GPT-5.6-terra (medium) | 5 | 25 | 125 | 125 | 125 | 10 | 8.0% | 10 | 9 |
| REFLECT agent traces | GPT-5.6-terra (low) | 5 | 25 | 125 | 125 | 122 | 24 | 19.7% | 20 | 14 |
| Recent mathematical research | GPT-5.6-sol (medium) | 5 | 23.0 average (25 planned) | 125 | 115 | 91 | 27 | 29.7% | 26 | 24 |
| TCS open problems | GPT-5.6-sol (medium) | 4 | 25 | 100 | 100 | 100 audited | 29 | 29.0% | 10 audited groups | 10 |

## Frozen-strategy evaluation

| Evaluation dataset | Mutation model | Proofs / traces | Mutations generated per proof / trace (generic / strategy) | Completed candidates (generic / strategy) | Judges per valid mutation | Valid mutations (generic / strategy) | Judges missing error, generic, mean (SD) | Judges missing error, strategy, mean (SD) | Change in mean |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Graduate classical mathematics* | GPT-5.6-sol (medium) | 5 | 3 / 3 | 15 / 15 | 3 | 15 / 15 | 0.00 (0.00) | **0.20 (0.77)** | **+0.20** |
| Olympiad (partial) | GPT-5.6-terra (medium) | 20 | 2.55 / 2.70 average (3 / 3 planned) | 51 / 54 | 3 | 47 / 51 | **0.49 (1.02)** | 0.45 (0.83) | −0.04 |
| REFLECT agent traces* | GPT-5.6-terra (low) | 5 | 5 / 5 | 25 / 25 | 3 | 15 / 17 | 1.73 (1.10) | **1.82 (1.38)** | **+0.09** |
| TCS open problems | GPT-5.6-sol (medium) | 5 | 5 / 5 | 25 / 25 | 3 | 21 / 23 | 0.33 (0.73) | **0.87 (1.14)** | **+0.54** |
| Recent mathematical research | GPT-5.6-sol (medium) | 5 | 3 / 3 | 15 / 15 | 2 | 15 / 15 | 0.40 (0.74) | **0.93 (0.96)** | **+0.53** |

Discovery mechanisms are counted within source sessions and may be merged during cross-source distillation, so the two rightmost discovery columns need not match. The TCS discovery row is reconstructed from four retrospectively audited persistent runs; the other discovery rows used independent validity and matching during the run.

Every run compares a generic mutator with a frozen-strategy-guided mutator, independently checks whether the introduced error is genuine, and sends each valid mutation to multiple blind error-inventory judges. A separate matcher determines whether each judge report identified the introduced error. The mean is the total number of blind reviews that missed the introduced error divided by the number of valid mutations in that arm. Parentheses report the candidate-level sample standard deviation (SD) of the number of missed judges. Invalid mutations are excluded. The maximum is three judges except for recent mathematical research, where it is two. The Olympiad run planned 60 candidates per arm across 20 proofs but stopped after 51 generic and 54 strategy-guided candidates; only 11 proofs had all six planned candidates, so its results are partial. The reported results should be presented as exploratory.

\* Graduate classical mathematics and REFLECT used one persistent mutation session per proof and arm, producing 3 and 5 adaptive mutations respectively. The other evaluations used a fresh session for every mutation attempt and returned no evaluation feedback to later mutators.

## Appendix: Additional strategy-discovery results

| Discovery dataset | Mutation model | Source proofs / traces | Mutations generated per proof / trace | Planned attempts | Completed attempts | Independently assessed attempts | Verified misses | Miss rate among assessed | Distinct successful mechanisms within sessions | Distilled strategies |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Dependent-theorem dossier | GPT-5.6-sol (medium) | 1 | 30 | 30 | 30 | 30 | 1 | 3.3% | 1 | 1 |
| Internet-sourced proof dossiers | GPT-5.6-sol (medium) | 2 | 25 | 50 | 50 | 50 | 2 | 4.0% | 2 | 2 |

## Appendix: Result artifact index

The paths below are relative to the repository root.

| Dataset | Phase | Primary result artifacts |
|---|---|---|
| Graduate classical mathematics | Discovery and distillation | [Run directory](logs/by_dataset/graduate_math/graduate_classics_pilot_v1_gpt56sol_medium/) · [Run manifest](logs/by_dataset/graduate_math/graduate_classics_pilot_v1_gpt56sol_medium/manifest.json) · [Discovery summaries](logs/by_dataset/graduate_math/graduate_classics_pilot_v1_gpt56sol_medium/discovery/) · [Distilled strategies](logs/by_dataset/graduate_math/graduate_classics_pilot_v1_gpt56sol_medium/distillation/strategies.md) |
| Graduate classical mathematics | Frozen evaluation (persistent mutation sessions*) | [Evaluation manifest](logs/by_dataset/graduate_math/graduate_classics_pilot_v1_gpt56sol_medium/evaluation/manifest.json) · [Evaluation summary](logs/by_dataset/graduate_math/graduate_classics_pilot_v1_gpt56sol_medium/evaluation/summary.json) · [Candidate-level results](logs/by_dataset/graduate_math/graduate_classics_pilot_v1_gpt56sol_medium/evaluation/results.json) |
| Olympiad | Discovery and distillation | [Run directory](logs/by_dataset/olympiad/olympiad_distinct_terra_medium_20260910_225705/) · [Run manifest](logs/by_dataset/olympiad/olympiad_distinct_terra_medium_20260910_225705/manifest.json) · [Discovery summaries](logs/by_dataset/olympiad/olympiad_distinct_terra_medium_20260910_225705/discovery/) · [Distilled strategies](logs/by_dataset/olympiad/olympiad_distinct_terra_medium_20260910_225705/distillation/strategies.md) |
| Olympiad | Frozen evaluation (partial) | [Run manifest](logs/by_dataset/olympiad/olympiad_frozen_transfer_terra_medium_v1_clean_20260913/manifest.json) · [Run summary](logs/by_dataset/olympiad/olympiad_frozen_transfer_terra_medium_v1_clean_20260913/summary.json) · [Candidate-level results](logs/by_dataset/olympiad/olympiad_frozen_transfer_terra_medium_v1_clean_20260913/results.json) |
| REFLECT agent traces | Discovery and distillation | [Run directory](logs/by_dataset/reflect/reflect_agent_trace_transfer_terra_low_20260911_151937/) · [Run manifest](logs/by_dataset/reflect/reflect_agent_trace_transfer_terra_low_20260911_151937/manifest.json) · [Discovery summaries](logs/by_dataset/reflect/reflect_agent_trace_transfer_terra_low_20260911_151937/discovery/) · [Distilled strategies](logs/by_dataset/reflect/reflect_agent_trace_transfer_terra_low_20260911_151937/distillation/strategies.md) |
| REFLECT agent traces | Frozen evaluation (persistent mutation sessions*) | [Evaluation manifest](logs/by_dataset/reflect/reflect_agent_trace_transfer_terra_low_20260911_151937/evaluation/manifest.json) · [Evaluation summary](logs/by_dataset/reflect/reflect_agent_trace_transfer_terra_low_20260911_151937/evaluation/summary.json) · [Candidate-level results](logs/by_dataset/reflect/reflect_agent_trace_transfer_terra_low_20260911_151937/evaluation/results.json) |
| Recent mathematical research | Discovery | [Pilot-three run](logs/by_dataset/recent_math/runs/recent_math_research_clean_pilot3_v1_gpt56sol_medium/) · [Extension-two run](logs/by_dataset/recent_math/runs/recent_math_research_clean_extension2_v1_gpt56sol_medium/) |
| Recent mathematical research | Distillation | [Distillation run](logs/by_dataset/recent_math/runs/recent_math_research_clean_all5_distillation_v1_gpt56sol_medium/) · [Distilled strategies](logs/by_dataset/recent_math/runs/recent_math_research_clean_all5_distillation_v1_gpt56sol_medium/distillation/strategies.md) |
| Recent mathematical research | Frozen evaluation | [Run summary](logs/by_dataset/recent_math/runs/recent_math_clean_all5_v1_gpt56sol_medium_2judges_v2/summary.json) · [Candidate-level results](logs/by_dataset/recent_math/runs/recent_math_clean_all5_v1_gpt56sol_medium_2judges_v2/results.json) |
| TCS open problems | Discovery and audit | [Nonsofic-groups run](logs/by_dataset/tcs_open_problems/ten_persistent_25train_03_nonsofic_groups_gpt-5.6-sol_medium_20260908_235224/) · [Connes-rigidity run](logs/by_dataset/tcs_open_problems/ten_persistent_25train_04_connes_rigidity_conjecture_gpt-5.6-sol_medium_20260908_235224/) · [Ehrhart-volume run](logs/by_dataset/tcs_open_problems/ten_persistent_25train_08_ehrhart_volume_conjecture_gpt-5.6-sol_medium_20260908_235224/) · [Extremal-number run](logs/by_dataset/tcs_open_problems/ten_persistent_25train_10_extremal_number_conjectures_gpt-5.6-sol_medium_20260908_235224/) |
| TCS open problems | Distillation | [Audited strategy library](src/proof_fuzzer/data/audited_persistent_strategies_20260909.md) · [Machine-readable strategies](src/proof_fuzzer/data/audited_persistent_strategies_20260909.jsonl) |
| TCS open problems | Frozen evaluation | [Evaluation summary](logs/by_dataset/tcs_open_problems/ten_matched_50_gpt-5.6-sol_medium_20260909_202502/summary.json) · [Candidate-level results](logs/by_dataset/tcs_open_problems/ten_matched_50_gpt-5.6-sol_medium_20260909_202502/results.json) |
| Dependent-theorem dossier | Discovery and distillation | [Run directory](logs/by_dataset/dependent_theorems/dependency_range_learning/) · [Run manifest](logs/by_dataset/dependent_theorems/dependency_range_learning/manifest.json) · [Discovery summaries](logs/by_dataset/dependent_theorems/dependency_range_learning/discovery/) · [Distilled strategies](logs/by_dataset/dependent_theorems/dependency_range_learning/distillation/strategies.md) |
| Internet-sourced proof dossiers | Discovery and distillation | [Run directory](logs/by_dataset/internet_dossiers/discovery/) · [Run manifest](logs/by_dataset/internet_dossiers/discovery/manifest.json) · [Discovery summaries](logs/by_dataset/internet_dossiers/discovery/discovery/) · [Distilled strategies](logs/by_dataset/internet_dossiers/discovery/distillation/strategies.md) |
