# Experimental analysis
In this section, we first evaluate the effectiveness and transferability of the mutation strategies produced after distillation.
Establishing transfer is essential before interpreting these strategies as general failure mechanisms of the judge, rather than artifacts specific to the proofs used during discovery.
This is assessed by testing them on an evaluation set of proofs, that are disjoint from the proofs used in the discovery phase. 
We compare the ability of an unguided agent and a strategy-guided agent to produce zero-shot mutations on evaluation proofs.
The unguided agent is provided the same prompt as during the discovery phase and is asked to produce one mutation on a proof.
The strategy-guided agent is additionally given access to the strategy file.
We provide each with several independent attempts at mutating each proof.
Then all these mutated proofs are similarly passed to the error checker agent followed by three independent judge agents, and finally the judge error checker.

### Datasets.

We study four datasets spanning short competition solutions, graduate-level
mathematical exposition, theoretical-computer-science manuscripts, and recent
research papers. In every dataset, the proofs used to discover and distill mutation
strategies are disjoint from those used for frozen evaluation.

**Olympiad.** Forty correct, text-only solutions from OlympiadBench, balanced across
algebra, combinatorics, geometry, and number theory and divided evenly between
discovery and evaluation.

**Graduate course dossiers.** Twenty long, proof-rich dossiers extracted from
official MIT graduate course materials in algebra and number theory, analysis, and
geometry and topology, with matched subject distributions in the discovery and
evaluation splits.

**TCS open problems.** Ten chapter-length mathematical and theoretical-computer-
science manuscripts from *Ten Advances in Mathematics and Theoretical Computer
Science*, divided into five discovery manuscripts and five held-out manuscripts.

**Recent mathematical research.** Ten mechanically cleaned arXiv manuscripts,
organized as five area-matched, paper-disjoint discovery/evaluation pairs covering
algebra and number theory, geometry and topology, analysis and PDE, probability and
combinatorics, and logic and dynamics.

### Learned mutation strategies transfer to unseen proofs.

![Grouped bar plot of GPT-5.6-sol judge miss rates during discovery, unguided
evaluation, and strategy-guided evaluation across the four datasets.](./figures/gpt56sol_transfer_judge_miss_rates.png)

**Figure: GPT-5.6-sol judge miss rates across discovery and held-out evaluation.**
The discovery percentage is the number of verified blind-judge misses divided by
the number of independently assessed discovery mutations. Each valid evaluation
mutation received three blind reviews, so the two evaluation percentages are the
number of reviews that missed the introduced error divided by all review slots for
valid mutations in that arm. Invalid mutations are excluded. The strategy library
was frozen before evaluation, and every evaluation candidate was generated in a
fresh session without feedback from earlier candidates.

![Grouped bar plot of Claude Opus 5 judge miss rates during discovery, unguided
evaluation, and strategy-guided evaluation on the two datasets with completed
results.](./figures/opus5_transfer_judge_miss_rates.png)

**Figure: Claude Opus 5 judge miss rates on the two completed datasets.** The
percentages use the same denominators as the GPT-5.6-sol figure: independently
assessed mutations for discovery and individual blind-review slots over valid
mutations for held-out evaluation. Results are currently available for Olympiad and
graduate course dossiers.

### Judges become less reliable with recent research-level math.

### How many other errors were flagged?

Across the frozen GPT-5.6-sol evaluations, we counted every error entry in each
completed blind-judge inventory and removed one entry when the matcher determined
that the inventory caught the planted error. The remainder are *other-error flags*:
they may identify genuine pre-existing problems, but they were not independently
validated for this analysis. The mean is calculated per completed blind review,
pooling the unguided and strategy-guided arms.

| Evaluation dataset | Valid mutations | Completed blind reviews | Other-error flags | Mean other-error flags per review |
|---|---:|---:|---:|---:|
| Olympiad | 200 | 600 | 974 | 1.62 |
| Graduate course dossiers | 98 | 293 | 4,947 | 16.88 |
| TCS open problems | 44 | 131 | 27 | 0.21 |
| Recent mathematical research | 50 | 150 | 907 | 6.05 |

Separating reviews by whether they detected the planted error does not reveal a
uniform association between larger error inventories and misses. Recent-mathematics
reviews that missed the planted error reported more other errors on average, but the
graduate-course pattern runs in the opposite direction and the TCS means are nearly
identical.

| Evaluation dataset | Reviews catching planted error | Mean other-error flags, caught reviews | Reviews missing planted error | Mean other-error flags, missed reviews |
|---|---:|---:|---:|---:|
| Olympiad | 596 | 1.62 | 4 | 2.00 |
| Graduate course dossiers | 245 | 17.19 | 34 | 15.74 |
| TCS open problems | 98 | 0.19 | 27 | 0.22 |
| Recent mathematical research | 104 | 5.50 | 44 | 7.14 |

The following table focuses only on individual blind reviews that missed the
planted error. Because the target was not detected in these reviews, every reported
error is an other-error flag. “Total errors reported” is the sum of inventory
entries across the missed reviews, and the average uses the number of missed
reviews as its denominator.

| Evaluation dataset | Blind reviews missing planted error | Total errors reported in missed reviews | Mean total errors per missed review |
|---|---:|---:|---:|
| Olympiad | 4 | 8 | 2.00 |
| Graduate course dossiers | 34 | 535 | 15.74 |
| TCS open problems | 27 | 6 | 0.22 |
| Recent mathematical research | 44 | 314 | 7.14 |

One graduate-course review and one TCS review returned no judge response because of
provider-capacity failures and are excluded from the means. Counts are report-level
flags, not deduplicated logical errors: the same underlying issue flagged by several
judges or in several mutated copies is counted each time. Reviews with ambiguous
detection outcomes are included in the overall table but excluded from the two
outcome-specific tables. Under this measure, the graduate-course judges flagged far
more non-planted issues than judges in the other datasets, while the TCS judges
flagged almost none; 22 of the 27 TCS missed reviews reported no error at all.

### Cross model evaluation of mutations.

### Higher reasoning catches some, but not all, selected misses.

We conducted a targeted higher-reasoning stress test on twelve GPT-5.6-sol
strategy-guided mutations: six from TCS open problems and six from recent
mathematical research. The initial batch contained the three strongest mutations
from each dataset, all missed by all three original medium-reasoning judges. The
extension used the next three per dataset; five had been missed by two of three
medium judges and one by all three. We submitted the same archived blind-judge
prompt for each mutation to one fresh GPT-5.6-sol judge at ultra reasoning effort,
with no timeout.

| Dataset | Selected mutations | Medium-reasoning reviews that missed | Ultra judges that caught | Ultra judges that missed |
|---|---:|---:|---:|---:|
| TCS open problems | 6 | 15 / 18 | 2 / 6 | 4 / 6 |
| Recent mathematical research | 6 | 16 / 18 | 3 / 6 | 3 / 6 |
| **Overall** | **12** | **31 / 36** | **5 / 12** | **7 / 12** |

Exact manual matching found that the ultra judge caught five of the twelve planted
errors: two TCS errors and three recent-research errors. All six mutations in the
initial, strongest batch remained undetected, whereas five of the six next-ranked
mutations were caught. Thus additional reasoning recovered some prior misses but did
not eliminate them. These results should not be read as a general estimate of the
effect of reasoning effort: the cases were chosen post hoc conditional on prior
medium-reasoning misses, and each candidate received only one ultra-reasoning review.

### Span of influence of mutations.

To test whether a mutation's downstream reach predicts judge failure, we manually
annotated all 192 valid GPT-5.6-sol candidates from the graduate-course, TCS, and
recent-mathematics frozen evaluations. We define a mutation's *span of influence*
as the number of nonblank physical proof lines from the first changed line through
the last line that explicitly refers to the changed mathematical object or directly
consumes it in an inference. The span stops when the affected claim is packaged as
a lemma, theorem, case conclusion, or other subresult and later text only cites that
result opaquely.
For coordinated multi-hunk edits, it extends through the last directly dependent
changed component. A valid mutation is successful if at least one of its three blind
reviews missed the introduced error; an ambiguous review does not itself count as a
miss.

![Grouped bar plot comparing the mean span of influence of successful and
unsuccessful GPT-5.6-sol mutations in the graduate-course, TCS, and
recent-mathematics frozen evaluations, with pooled results.](./figures/gpt56sol_span_of_influence.png)

**Figure: Mean span of influence by mutation outcome.** Bars show arithmetic means;
error bars are percentile 95% bootstrap confidence intervals over valid candidates.
The distributions are strongly right-skewed because several coordinated multi-hunk
mutations propagate through hundreds of lines, so medians are reported below as a
robust descriptive companion. These candidate-level intervals are descriptive and
do not adjust for clustering by source proof or repeated mutation mechanisms.

| Evaluation data | Successful, mean lines (95% CI); median; n | Unsuccessful, mean lines (95% CI); median; n |
|---|---:|---:|
| Graduate course dossiers | 10.0 (7.3--12.7); 8.5; 18 | 34.5 (16.3--63.4); 9; 80 |
| TCS open problems | 164.5 (16.8--372.4); 16; 15 | 266.3 (127.7--420.6); 41; 29 |
| Recent mathematical research | 41.0 (6.6--102.3); 7.5; 22 | 19.2 (11.1--29.1); 9; 28 |
| **Pooled** | **64.5 (14.3--130.2); 8; 55** | **80.5 (45.6--121.3); 11; 137** |

Span of influence does not separate successful from unsuccessful mutations in these
evaluations. Successful mutations are shorter on average in the graduate and TCS
sets but longer in recent mathematics, where one 624-line successful multi-hunk
mutation strongly affects the mean. In the graduate set the bootstrap intervals for
the two means do not overlap, but the medians are nearly identical (8.5 and 9 lines)
and a single 971-line unsuccessful standing-definition mutation strongly raises the
unsuccessful mean. The intervals overlap in TCS, recent mathematics, and the pooled
analysis. Exploratory two-sided permutation tests give no evidence of a difference
(graduate $p=0.240$, TCS $p=0.436$, recent mathematics $p=0.625$, pooled
$p=0.670$). The typical successful mutation is short in all three datasets, but
short span is also common among unsuccessful mutations.

The candidate-level annotations, endpoint rationales, uncertainty bounds, audit
reports, and reproducible plotting code are in
[`span_of_influence_annotations/`](./span_of_influence_annotations/),
[`span_of_influence_annotations.csv`](./span_of_influence_annotations.csv), and
[`plot_span_of_influence.py`](./plot_span_of_influence.py). The reviewed graduate
endpoint map and annotation builder are in
[`build_graduate_span_annotations.py`](./build_graduate_span_annotations.py).

### Number of characters mutated.

We also measure mutation size directly. For each of the same 192 valid evaluation
mutations, we compute the character-level Levenshtein distance between the removed
and added text in each changed diff block, then sum across blocks. A one-character
insertion, deletion, or substitution costs one; line breaks also count as one
character. This measures the minimum textual edit rather than charging for every
character on a replaced line. Diff headers and unchanged context do not count.

![Grouped bar plot comparing the mean number of characters mutated in successful
and unsuccessful GPT-5.6-sol mutations in the graduate-course, TCS, and
recent-mathematics frozen evaluations, with pooled results.](./figures/gpt56sol_mutated_characters.png)

**Figure: Mean number of characters mutated by outcome.** Bars show arithmetic
means and error bars show percentile 95% bootstrap confidence intervals over valid
candidates. As in the span analysis, these intervals are descriptive and do not
adjust for clustering by source proof or repeated mutation mechanisms.

| Evaluation data | Successful, mean characters (95% CI); median; n | Unsuccessful, mean characters (95% CI); median; n |
|---|---:|---:|
| Graduate course dossiers | 24.0 (9.1--43.7); 11.5; 18 | 47.6 (29.1--70.7); 13; 80 |
| TCS open problems | 94.3 (43.5--151.3); 33; 15 | 119.0 (46.7--208.4); 12; 29 |
| Recent mathematical research | 25.4 (12.1--41.1); 6.5; 22 | 31.6 (19.1--45.5); 15.5; 28 |
| **Pooled** | **43.7 (26.4--64.0); 14; 55** | **59.4 (39.5--83.4); 13; 137** |

Successful mutations use fewer character edits on average in all three datasets, but
mutation size again does not cleanly separate outcomes. The confidence intervals
overlap, and exploratory two-sided permutation tests provide no evidence of a
difference (graduate $p=0.312$, TCS $p=0.712$, recent mathematics $p=0.550$,
pooled $p=0.419$). The TCS median points in the opposite direction from its means
because a few very large unsuccessful edits pull up the unsuccessful mean. Thus the
data do not support the claim that judge misses are explained simply by making
smaller textual changes.

The candidate-level counts and reproducible analysis are in
[`mutated_character_counts.csv`](./mutated_character_counts.csv),
[`mutated_character_summary.json`](./mutated_character_summary.json), and
[`plot_mutated_characters.py`](./plot_mutated_characters.py).

### Trends within datasets.

The following comparison uses only the frozen GPT-5.6-sol evaluation runs; discovery
mutations are not included. We count individual blind-judge reviews marked as
missed, pooling the unguided and strategy-guided evaluation arms. Invalid mutations
are excluded, and ambiguous reviews remain review opportunities but do not count as
misses. Each label reports the total misses divided by the available review slots
for that area. We pool the two evaluation arms rather than distinguishing guided
from unguided mutations. The graduate dossiers are grouped into their three
canonical broad areas; the other corpora use their available subject-area taxonomy.

![Four-panel horizontal bar plot of missed blind-judge reviews by mathematical area
in the Olympiad, graduate-course, TCS, and recent-mathematics frozen
GPT-5.6-sol evaluations.](./figures/gpt56sol_eval_judge_misses_by_subtopic.png)

**Figure: Evaluation judge misses by mathematical area.** Olympiad misses were
rare across all four subjects: number theory had two, algebra and geometry one each,
and combinatorics none. Within the graduate dossiers, algebra and number theory had
17 misses, geometry and topology had ten, and analysis had seven. The TCS misses
were concentrated in coding theory (14) and discrete geometry/sphere packing (nine).
Recent-research misses were highest in algebra and number theory (19), probability
and combinatorics (11), and logic and dynamics (10), while analysis and PDE had
none. These are descriptive raw counts from small area samples, not evidence that
subject area itself causes judge failure.

The plotted counts are in
[`eval_judge_misses_by_subtopic.csv`](./eval_judge_misses_by_subtopic.csv),
[`eval_judge_misses_by_subtopic.json`](./eval_judge_misses_by_subtopic.json), and
[`plot_eval_judge_misses_by_subtopic.py`](./plot_eval_judge_misses_by_subtopic.py).

### Uniqueness of mutations.

For the four frozen GPT-5.6-sol evaluations, we measure uniqueness at the level of
the planted logical error rather than by comparing the mutated proof strings. Two
valid candidates are counted as the same error when they introduce the same false
assertion or inference in the same source proof, even if they use different wording,
counterexamples, dependent edits, or proof hashes. Analogous mistakes in different
source proofs count separately, as do materially different false claims within one
proof. Candidates rejected by the validity judge or lost before validity assessment
are excluded because they do not establish a valid planted logical error.

| Evaluation data | Generated candidates | Valid mutations | Distinct logical errors (% of valid) | Singleton mutations (% of valid) |
|---|---:|---:|---:|---:|
| Olympiad | 200 | 200 | 132 (66.0%) | 102 (51.0%) |
| Graduate course dossiers | 100 | 98 | 70 (71.4%) | 52 (53.1%) |
| TCS open problems | 50 | 44 | 36 (81.8%) | 31 (70.5%) |
| Recent mathematical research | 50 | 50 | 32 (64.0%) | 21 (42.0%) |
| **Total** | **400** | **392** | **270 (68.9%)** | **206 (52.6%)** |

Here, “distinct logical errors” is the number of semantic equivalence classes;
“singleton mutations” counts candidates whose class appears exactly once. Thus, for
example, the 50 recent-mathematics candidates contain 32 different errors, but only
21 candidates are unrepeated singletons. TCS has the highest observed distinct-error
rate, while recent mathematics has the most repetition. Across the four evaluations,
122 of the 392 valid candidates are repetitions beyond the first representative of
their logical-error class. These are manual semantic judgments rather than an
automated string-similarity statistic; the released assignments make every grouping
inspectable.

The candidate-level cluster assignments and the auditable list of non-singleton
groups are in
[`mutation_uniqueness_annotations.json`](./mutation_uniqueness_annotations.json),
[`mutation_uniqueness_annotations.csv`](./mutation_uniqueness_annotations.csv), and
[`analyze_mutation_uniqueness.py`](./analyze_mutation_uniqueness.py).

## Appendix: Dataset details

### Olympiad

The Olympiad corpus is the version-controlled
`olympiadbench_balanced_40_v1` subset of the English text-only competition-math
portion of OlympiadBench. The proof artifact is the `full_response` from the
associated gpt-oss-120b run, and every selected response has a `TRUE` correctness
label. The corpus contains 40 distinct problem IDs and normalized problem
statements. Its fixed discovery and held-out splits each contain 20 solutions: five
each in algebra, combinatorics, geometry, and number theory. This construction keeps
the topic mixture identical across phases while ensuring that no problem or solution
appears in both.

### Graduate course dossiers

The graduate corpus contains 20 cohesive excerpts from official MIT faculty course
materials. Each dossier is a long sequence of definitions, propositions, theorems,
and proofs rather than a single isolated exercise; dossier lengths range from 6,542
to 12,926 words. The source courses cover number theory, measure and integration,
differential analysis, algebraic topology, and geometry of manifolds. Source text was
extracted deterministically from the course PDFs or commit-pinned LaTeX, with
page furniture and presentation artifacts removed but no new proof prose authored.
The 57 cited source PDFs are retained for provenance and verified by checksums.

The fixed split contains ten discovery and ten held-out dossiers. Each side has four
algebra-and-number-theory dossiers, three analysis dossiers, and three
geometry-and-topology dossiers. The paired subject design makes the two phases
comparable while keeping their source ranges disjoint. The experiment consumes the
cleaned dossier text; the original files are provenance artifacts rather than model
inputs.

### TCS open problems

This corpus consists of the ten complete Markdown chapters extracted from OpenAI's
253-page volume *Ten Advances in Mathematics and Theoretical Computer Science*.
The chapters range across sphere packing and coding theory, group theory and operator
algebras, arithmetic circuit complexity, quantum information, lattice complexity,
convex geometry, Ramsey theory, and extremal graph theory. The extraction preserves
the chapter text and layout as closely as practical, while the original PDF is kept
as the authoritative source for equation rendering.

The five discovery chapters concern nonsofic groups, Connes's rigidity conjecture,
circuit and formula lower bounds for the permanent, Ehrhart's volume conjecture,
and extremal-number conjectures. The other five chapters—on sphere packing, binary
and spherical codes, quantum parallel repetition, the closest vector problem, and
multicolor Ramsey numbers—form the held-out evaluation split. Thus strategy
distillation and evaluation use different manuscripts from the same broad source
collection.

### Recent mathematical research

The recent-research corpus contains ten full, proof-bearing arXiv manuscripts, with
one discovery paper and one held-out paper in each of five areas: algebra and number
theory, geometry and topology, analysis and PDE, probability and combinatorics, and
logic and dynamics. The papers are 7,370--16,688 words long. The split was fixed as
five area-matched, paper-disjoint pairs before mutation feedback was observed.

The runtime dossiers are mechanically cleaned versions of the authors' TeX: wrapper,
package, front-matter, layout, comment, and bibliography material was removed;
author-defined mathematical notation and proof prose were retained; and figures were
replaced by text markers while captions and labels remained. No mathematical proof
prose was newly authored during cleaning. Each manuscript underwent two baseline
audits before acceptance. The audits permitted only localized, unambiguous source
issues that did not undermine the main proof chains; provenance metadata and the ten
corresponding source PDFs are retained with the dataset.
