# Frozen-evaluation success counts by model

These counts pool the four held-out evaluation sets: Olympiad (20 proofs),
GraduateCourses (10), OpenAI-TCS (5), and ArXivMath (5), for 40 proofs per model.
Each model has 200 candidates per arm. Every valid candidate received three blind
reviews. Invalid candidates are excluded. A review counts as a miss only when its
detection label is `missed`; ambiguous reviews are not counted as misses.

A proof counts as successful in an arm when at least one valid candidate for that
proof reaches the stated threshold. Mutation-level counts pool candidates, so
candidates from the same proof are not independent. The proof-level all-three
threshold is the preregistered strict endpoint.

## Combined counts

| Model | Arm | Valid mutations | Mutations ≥1 missed | Mutations ≥2 missed | Mutations all 3 missed | Missed reviews | Proofs ≥2 missed (of 40) | Proofs all 3 missed (of 40) |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| GPT-5.6-sol | Unguided | 195 | 26 | 11 | 7 | 44 / 585 (7.5%) | 7 | 6 |
| GPT-5.6-sol | Guided | 197 | 33 | 22 | 10 | 65 / 591 (11.0%) | 13 | 7 |
| Claude Opus 5 | Unguided | 199 | 25 | 13 | 2 | 40 / 597 (6.7%) | 9 | 2 |
| Claude Opus 5 | Guided | 195 | 57 | 36 | 26 | 119 / 585 (20.3%) | 20 | 16 |

## Proof-level overlap between arms

| Model | Threshold | Either arm | Both | Guided only | Unguided only |
|---|---|---:|---:|---:|---:|
| GPT-5.6-sol | All 3 missed | 8 | 5 | 2 | 1 |
| GPT-5.6-sol | ≥2 missed | 13 | 7 | 6 | 0 |
| Claude Opus 5 | All 3 missed | 16 | 2 | 14 | 0 |
| Claude Opus 5 | ≥2 missed | 21 | 8 | 12 | 1 |

## Per-dataset breakdown

Mutation counts are given as ≥1 / ≥2 / all 3 judges missed.

| Dataset | GPT unguided | GPT guided | Claude unguided | Claude guided |
|---|---|---|---|---|
| Olympiad | 2 / 0 / 0 | 2 / 0 / 0 | 5 / 3 / 0 | 14 / 6 / 4 |
| GraduateCourses | 9 / 5 / 2 | 9 / 7 / 2 | 12 / 3 / 0 | 22 / 15 / 10 |
| OpenAI-TCS | 5 / 1 / 1 | 10 / 7 / 3 | 2 / 2 / 0 | 7 / 7 / 6 |
| ArXivMath | 10 / 5 / 4 | 12 / 8 / 5 | 6 / 5 / 2 | 14 / 8 / 6 |

Proof counts are given as ≥2 / all 3 judges missed, unguided vs guided.

| Dataset | Proofs | GPT unguided | GPT guided | Claude unguided | Claude guided |
|---|---:|---|---|---|---|
| Olympiad | 20 | 0 / 0 | 0 / 0 | 2 / 0 | 5 / 3 |
| GraduateCourses | 10 | 3 / 2 | 7 / 2 | 3 / 0 | 7 / 6 |
| OpenAI-TCS | 5 | 1 / 1 | 2 / 2 | 1 / 0 | 4 / 3 |
| ArXivMath | 5 | 3 / 3 | 4 / 3 | 3 / 2 | 4 / 4 |

## Sources

Counts were computed from each run's `results.json` (the logs are not tracked in
Git):

| Dataset | GPT-5.6-sol run | Claude Opus 5 run |
|---|---|---|
| Olympiad | `logs/by_dataset/olympiad/olympiad_20_frozen_eval_gpt56sol_medium_5x3_20260924` | `logs/by_dataset/olympiad/olympiad_20_frozen_eval_claude_opus5_default_5x3_20260922` |
| GraduateCourses | `logs/by_dataset/graduate_course/graduate_course_10_frozen_eval_gpt56sol_medium_5x3_20260923` | `logs/by_dataset/graduate_course/graduate_course_10_frozen_eval_claude_opus5_medium_5x3_20260923_amended` |
| OpenAI-TCS | `logs/by_dataset/tcs_open_problems/ten_matched_50_gpt-5.6-sol_medium_20260909_202502` | `logs/by_dataset/tcs_open_problems/opus5_snapshot120_frozen_eval_5x3_20260925` |
| ArXivMath | `logs/by_dataset/recent_math/runs/recent_math_clean_all5_v1_gpt56sol_medium_25perarm_3judges_combined_20260923` | `logs/by_dataset/recent_math/runs/recent_math_5_frozen_eval_claude_opus5_medium_5x3_20260924` |

The Claude OpenAI-TCS and ArXivMath counts include the resource-limit adjudications
recorded in those runs' manifests.
