# Experimental analysis
In this section, we first evaluate the effectiveness and transferability of the mutation strategies produced after distillation.
Establishing transfer is essential before interpreting these strategies as general failure mechanisms of the judge, rather than artifacts specific to the proofs used during discovery.
This is assessed by testing them on an evaluation set of proofs, that are disjoint from the proofs used in the discovery phase. 
We compare the ability of an unguided agent and a strategy-guided agent to produce zero-shot mutations on evaluation proofs.
The unguided agent is provided the same prompt as during the discovery phase and is asked to produce one mutation on a proof.
The strategy-guided agent is additionally given access to the strategy file.
We provide each with several independent attempts at mutating each proof.
Then all these mutated proofs are similarly passed to the error checker agent followed by three independent judge agents, and finally the judge error checker.

All bar charts report 95% confidence intervals. Judge-miss proportions use Wilson
score intervals for the displayed numerator and denominator; continuous-outcome
means use percentile bootstrap intervals over valid candidates. The Wilson intervals
are descriptive and treat review slots as Bernoulli observations, without adjusting
for clustering of reviews within mutations or mutations within proofs.

### Datasets.

We study four datasets spanning short competition solutions, graduate-level
mathematical exposition, theoretical-computer-science manuscripts, and recent
research papers. In every dataset, the proofs used to discover and distill mutation
strategies are disjoint from those used for frozen evaluation.

**Olympiad.** Forty correct, text-only solutions from OlympiadBench, balanced across
algebra, combinatorics, geometry, and number theory and divided evenly between
discovery and evaluation.

**GraduateCourses.** Twenty long, proof-rich dossiers extracted from
official MIT graduate course materials in algebra and number theory, analysis, and
geometry and topology, with matched subject distributions in the discovery and
evaluation splits.

**OpenAI-TCS.** Ten chapter-length mathematical and theoretical-computer-
science manuscripts from *Ten Advances in Mathematics and Theoretical Computer
Science*, divided into five discovery manuscripts and five held-out manuscripts.

**ArXivMath.** Ten mechanically cleaned arXiv manuscripts,
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
fresh session without feedback from earlier candidates. Error bars are 95% Wilson
score intervals.

![Grouped bar plot of Claude Opus 5 judge miss rates during discovery, unguided
evaluation, and strategy-guided evaluation across the four datasets.](./figures/opus5_transfer_judge_miss_rates.png)

**Figure: Claude Opus 5 judge miss rates across discovery and held-out evaluation.** The
percentages use the same denominators as the GPT-5.6-sol figure: independently
assessed mutations for discovery and individual blind-review slots over valid
mutations for held-out evaluation. The OpenAI-TCS discovery value is the
resource-limited 120-attempt snapshot from which its strategy library was frozen.
Error bars are 95% Wilson score intervals. ArXivMath had the highest
Claude miss rate in discovery (30/125, 24.0%) and in both held-out arms: 13/75
(17.3%) for unguided mutations and 28/75 (37.3%) for strategy-guided mutations.

| Claude Opus 5 evaluation dataset | Unguided proof successes | Strategy-guided proof successes | Paired risk difference | Exact one-sided p value |
|---|---:|---:|---:|---:|
| Olympiad | 0 / 20 | 3 / 20 | +0.15 | 0.125 |
| GraduateCourses | 0 / 10 | 6 / 10 | +0.60 | 0.015625 |
| OpenAI-TCS | 0 / 5 | 3 / 5 | +0.60 | 0.125 |
| ArXivMath | 2 / 5 | 4 / 5 | +0.40 | 0.25 |

A proof-arm succeeds at this strict endpoint when at least one valid candidate is
missed by all three blind judges. All four Claude evaluations favor the frozen
strategy arm descriptively, but none meets the preregistered familywise threshold
of $\alpha=0.01$. The OpenAI-TCS evaluation completed all 50 candidates; 24 of
25 unguided and 22 of 25 strategy-guided candidates were valid. Its manifest records
two post-launch amendments: unresolved jobs were relaunched with Claude Code's
output-token ceiling raised from 64,000 to 128,000, and reviews still unresolved
after two retries were labeled resource-limit misses. The rule affected three
candidates and is included in the plotted 4/72 unguided and 20/66 strategy-guided
counts. The ArXivMath evaluation completed all 50 candidates, all
of which passed the independent validity check. Its manifest records two
post-launch amendments: the 20-minute call timeout was removed after 29 candidates,
and the final candidate was adjudicated under the user-specified rule that an
independent judge returning no usable verdict after exceeding Claude Code's
64,000-output-token limit counts as a miss. All three judges for that candidate hit
the limit, making it a three-of-three miss; this resource-limit adjudication is
therefore included in the plotted 28/75 strategy-guided count and in the 4/5 strict
proof endpoint.

### Judges become less reliable with ArXivMath-level math.

ArXivMath has the highest held-out review-level miss rate for
both completed models and in both mutation arms. For GPT-5.6-sol, judges missed
19/75 reviews (25.3%) in the unguided arm and 25/75 (33.3%) in the strategy-guided
arm. For Claude Opus 5, the corresponding counts are 13/75 (17.3%) and 28/75
(37.3%); on OpenAI-TCS they are 4/72 (5.6%) and 20/66 (30.3%). The discovery pattern is less uniform: ArXivMath is highest for
Claude (24.0%), while the GPT-5.6-sol rates for ArXivMath (28.4%) and OpenAI-TCS
(29.0%) are nearly equal. These are descriptive comparisons across
different source proofs and independently generated mutations; they do not isolate
mathematical level from proof length, exposition, subject, mutation mix, or
provider-specific behavior.

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
| GraduateCourses | 98 | 293 | 4,947 | 16.88 |
| OpenAI-TCS | 44 | 131 | 27 | 0.21 |
| ArXivMath | 50 | 150 | 907 | 6.05 |

Separating reviews by whether they detected the planted error does not reveal a
uniform association between larger error inventories and misses. ArXivMath
reviews that missed the planted error reported more other errors on average, but the
GraduateCourses pattern runs in the opposite direction and the OpenAI-TCS means are nearly
identical.

| Evaluation dataset | Reviews catching planted error | Mean other-error flags, caught reviews | Reviews missing planted error | Mean other-error flags, missed reviews |
|---|---:|---:|---:|---:|
| Olympiad | 596 | 1.62 | 4 | 2.00 |
| GraduateCourses | 245 | 17.19 | 34 | 15.74 |
| OpenAI-TCS | 98 | 0.19 | 27 | 0.22 |
| ArXivMath | 104 | 5.50 | 44 | 7.14 |

The following table focuses only on individual blind reviews that missed the
planted error. Because the target was not detected in these reviews, every reported
error is an other-error flag. “Total errors reported” is the sum of inventory
entries across the missed reviews, and the average uses the number of missed
reviews as its denominator.

| Evaluation dataset | Blind reviews missing planted error | Total errors reported in missed reviews | Mean total errors per missed review |
|---|---:|---:|---:|
| Olympiad | 4 | 8 | 2.00 |
| GraduateCourses | 34 | 535 | 15.74 |
| OpenAI-TCS | 27 | 6 | 0.22 |
| ArXivMath | 44 | 314 | 7.14 |

One GraduateCourses review and one OpenAI-TCS review returned no judge response because of
provider-capacity failures and are excluded from the means. Counts are report-level
flags, not deduplicated logical errors: the same underlying issue flagged by several
judges or in several mutated copies is counted each time. Reviews with ambiguous
detection outcomes are included in the overall table but excluded from the two
outcome-specific tables. Under this measure, the GraduateCourses judges flagged far
more non-planted issues than judges in the other datasets, while the OpenAI-TCS judges
flagged almost none; 22 of the 27 OpenAI-TCS missed reviews reported no error at all.

### Cross model evaluation of mutations.

We next test whether strong strategy-guided mutations transfer across judge model
families. Within each dataset and mutation-source model, we rank unique valid
strategy-guided candidates by the number of original blind reviews that missed the
planted error and retain the top ten. Ties are resolved deterministically by proof,
candidate, session, and mutation hash. We then submit the candidate's exact archived
blind-judge prompt to the other model at medium reasoning effort and use a separate
fresh call from that model to match the resulting error inventory against the
planted error.

![Grouped bar plot of cross-model judge miss rates for Olympiad, GraduateCourses,
OpenAI-TCS, and ArXivMath mutations. Each dataset has one bar for GPT-5.6-sol judging
Claude Opus 5 mutations and one for Claude Opus 5 judging GPT-5.6-sol
mutations.](./figures/cross_model_judge_miss_rates.png)

**Figure: Cross-model judge miss rates on selected strategy-guided mutations.** Each
bar summarizes ten mutations. GPT-5.6-sol missed 3/10 Claude mutations in Olympiad,
5/10 in GraduateCourses, 7/10 in OpenAI-TCS, and 7/10 in ArXivMath. Claude Opus 5
missed 2/10 GPT mutations in Olympiad, 1/10 in GraduateCourses, 5/10 in OpenAI-TCS,
and 2/10 in ArXivMath. Error bars are 95% Wilson score intervals.

| Evaluation dataset | GPT-5.6-sol judge / Claude Opus 5 mutations, caught | GPT-5.6-sol judge / Claude Opus 5 mutations, missed | Claude Opus 5 judge / GPT-5.6-sol mutations, caught | Claude Opus 5 judge / GPT-5.6-sol mutations, missed |
|---|---:|---:|---:|---:|
| Olympiad | 7 | 3 | 8 | 2 |
| GraduateCourses | 5 | 5 | 9 | 1 |
| OpenAI-TCS | 3 | 7 | 5 | 5 |
| ArXivMath | 3 | 7 | 8 | 2 |
| **Total** | **18** | **22** | **30** | **10** |

Across these selected candidates, GPT-5.6-sol missed 22/40 Claude-generated
mutations (55.0%), whereas Claude Opus 5 missed 10/40 GPT-generated mutations
(25.0%). OpenAI-TCS is the only dataset in which Claude Opus 5 missed half of the
selected GPT-generated mutations. This difference is descriptive rather than a controlled comparison of
judge quality: the two judges saw different mutations, and selection was conditional
on success against the mutation source model's original judges. In particular, the
GPT-5.6-sol Olympiad strategy arm contained only two candidates with an original
miss, so eight of its ten selected candidates had zero original misses; likewise,
the Claude Opus 5 OpenAI-TCS strategy arm contained seven candidates with an
original miss, so three of its ten selected candidates had zero original misses. The
other cells contain different mixtures of one-, two-, and three-review original
misses. One ArXivMath Claude judgment of a GPT-generated mutation returned no usable
verdict after exceeding Claude Code's 64,000-output-token limit and is counted as a
miss under the recorded resource-limit adjudication. The OpenAI-TCS cells were run
separately with Claude Code's output-token ceiling raised to 128,000; all 20 of its
judgments returned usable inventories, so no resource-limit adjudication was needed.
The complete manifests, candidate records, responses, matching results, usage data,
and adjudication are in
`logs/by_dataset/cross_model/top10_first3_medium_20260925/` and
`logs/by_dataset/cross_model/top10_tcs_medium_20260925/`.

### Higher reasoning catches some, but not all, selected misses.

We conducted a targeted higher-reasoning stress test on twelve GPT-5.6-sol
strategy-guided mutations: six from OpenAI-TCS and six from ArXivMath. The initial
batch contained the three strongest mutations
from each dataset, all missed by all three original medium-reasoning judges. The
extension used the next three per dataset; five had been missed by two of three
medium judges and one by all three. We submitted the same archived blind-judge
prompt for each mutation to one fresh GPT-5.6-sol judge at ultra reasoning effort,
with no timeout.

We separately selected the six strongest valid strategy-guided mutations from the
Claude Opus 5 ArXivMath evaluation and submitted the same archived prompts to fresh
Opus 5 judges at max effort. All six had been missed by all three original
medium-effort reviews. A first launch produced no verdicts because every call
exhausted Claude Code's default 64,000-output-token ceiling. A clean rerun changed
only that ceiling to 128,000 tokens and produced six usable inventories. We applied
the same design, with the 128,000-token ceiling, to the six strongest valid
strategy-guided mutations from the Claude Opus 5 OpenAI-TCS evaluation, all of which
had also been missed by all three original medium-effort reviews. The first launch
stopped after two calls had completed; the four unfinished candidates were relaunched
with identical settings. Of these four, one returned a usable inventory, two exceeded
the 128,000-token ceiling without a verdict and are counted as resource-limit misses
under the user-specified rule, and one failed with a request timeout after ten API
retries and is excluded as a technical failure.

![Grouped bar plot of higher-reasoning judge miss rates for OpenAI-TCS, ArXivMath,
and both datasets combined. Each group has one bar for GPT-5.6-sol at ultra effort
and one for Claude Opus 5 at max effort.](./figures/higher_reasoning_judge_miss_rates.png)

**Figure: Higher-reasoning judge miss rates on selected prior misses.** Each bar is
the fraction of higher-reasoning judges that missed the planted error, with the
underlying counts in each label. Each model judged its own mutations, so the two
bars in a group cover different mutations. The GPT-5.6-sol selection includes
next-ranked candidates with two-of-three original misses, whereas every Claude Opus 5
candidate had been missed by all three medium-effort reviews. The Claude OpenAI-TCS
bar counts two token-limit misses and excludes one timed-out call.

| Judge model / effort | Dataset | Selected mutations | Medium-reasoning reviews that missed | Higher-reasoning judges that caught | Higher-reasoning judges that missed |
|---|---|---:|---:|---:|---:|
| GPT-5.6-sol / ultra | OpenAI-TCS | 6 | 15 / 18 | 2 / 6 | 4 / 6 |
| GPT-5.6-sol / ultra | ArXivMath | 6 | 16 / 18 | 3 / 6 | 3 / 6 |
| **GPT-5.6-sol / ultra** | **Overall** | **12** | **31 / 36** | **5 / 12** | **7 / 12** |
| Claude Opus 5 / max | OpenAI-TCS | 6 | 18 / 18 | 0 / 5 | 5 / 5 |
| Claude Opus 5 / max | ArXivMath | 6 | 18 / 18 | 0 / 6 | 6 / 6 |
| **Claude Opus 5 / max** | **Overall** | **12** | **36 / 36** | **0 / 11** | **11 / 11** |

Exact manual matching found that the ultra judge caught five of the twelve planted
errors: two OpenAI-TCS errors and three ArXivMath errors. All six mutations in the
initial, strongest batch remained undetected, whereas five of the six next-ranked
mutations were caught. Thus additional reasoning recovered some prior misses but did
not eliminate them. Exact manual matching found that the six ArXivMath max-effort
Claude judges also missed all six planted errors. Two reported an unrelated order-versus-degree sign
issue at the location of the generic-versus-special-fiber mutation, which does not
count as detection under the exact-match policy. On OpenAI-TCS, none of the five
adjudicated max-effort Claude judges caught its planted error: the three usable
inventories reported only unrelated issues, and two of the five misses are
resource-limit misses. Two OpenAI-TCS judges independently flagged the same
pre-existing construction issue in the introduction of the Ramsey chapter, and one
reviewer's summary explicitly restated the unmutated rate estimate as verified.
The OpenAI-TCS higher-effort denominator is five because the timed-out candidate is
excluded. These results should not be read as
a general estimate of the effect of reasoning effort: the cases were chosen post hoc
conditional on prior medium-reasoning misses, and each candidate received only one
higher-reasoning review.

### Span of influence of mutations.

To test whether a mutation's downstream reach predicts judge failure, we manually
annotated all 192 valid GPT-5.6-sol candidates from the GraduateCourses, OpenAI-TCS, and
ArXivMath frozen evaluations. We define a mutation's *span of influence*
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
unsuccessful GPT-5.6-sol mutations in the GraduateCourses, OpenAI-TCS, and
ArXivMath frozen evaluations, with pooled results.](./figures/gpt56sol_span_of_influence.png)

**Figure: Mean span of influence by mutation outcome.** Bars show arithmetic means;
error bars are percentile 95% bootstrap confidence intervals over valid candidates.
The distributions are strongly right-skewed because several coordinated multi-hunk
mutations propagate through hundreds of lines, so medians are reported below as a
robust descriptive companion. These candidate-level intervals are descriptive and
do not adjust for clustering by source proof or repeated mutation mechanisms.

| Evaluation data | Successful, mean lines (95% CI); median; n | Unsuccessful, mean lines (95% CI); median; n |
|---|---:|---:|
| GraduateCourses | 10.0 (7.3--12.7); 8.5; 18 | 34.5 (16.3--63.4); 9; 80 |
| OpenAI-TCS | 164.5 (16.8--372.4); 16; 15 | 266.3 (127.7--420.6); 41; 29 |
| ArXivMath | 41.0 (6.6--102.3); 7.5; 22 | 19.2 (11.1--29.1); 9; 28 |
| **Pooled** | **64.5 (14.3--130.2); 8; 55** | **80.5 (45.6--121.3); 11; 137** |

Span of influence does not separate successful from unsuccessful mutations in these
evaluations. Successful mutations are shorter on average in GraduateCourses and OpenAI-TCS
sets but longer in ArXivMath, where one 624-line successful multi-hunk
mutation strongly affects the mean. In GraduateCourses the bootstrap intervals for
the two means do not overlap, but the medians are nearly identical (8.5 and 9 lines)
and a single 971-line unsuccessful standing-definition mutation strongly raises the
unsuccessful mean. The intervals overlap in OpenAI-TCS, ArXivMath, and the pooled
analysis. Exploratory two-sided permutation tests give no evidence of a difference
(GraduateCourses $p=0.240$, OpenAI-TCS $p=0.436$, ArXivMath $p=0.625$, pooled
$p=0.670$). The typical successful mutation is short in all three datasets, but
short span is also common among unsuccessful mutations.

The candidate-level annotations, endpoint rationales, uncertainty bounds, audit
reports, and reproducible plotting code are in
[`span_of_influence_annotations/`](./span_of_influence_annotations/),
[`span_of_influence_annotations.csv`](./span_of_influence_annotations.csv), and
[`plot_span_of_influence.py`](./plot_span_of_influence.py). The reviewed GraduateCourses
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
and unsuccessful GPT-5.6-sol mutations in the GraduateCourses, OpenAI-TCS, and
ArXivMath frozen evaluations, with pooled results.](./figures/gpt56sol_mutated_characters.png)

**Figure: Mean number of characters mutated by outcome.** Bars show arithmetic
means and error bars show percentile 95% bootstrap confidence intervals over valid
candidates. As in the span analysis, these intervals are descriptive and do not
adjust for clustering by source proof or repeated mutation mechanisms.

| Evaluation data | Successful, mean characters (95% CI); median; n | Unsuccessful, mean characters (95% CI); median; n |
|---|---:|---:|
| GraduateCourses | 24.0 (9.1--43.7); 11.5; 18 | 47.6 (29.1--70.7); 13; 80 |
| OpenAI-TCS | 94.3 (43.5--151.3); 33; 15 | 119.0 (46.7--208.4); 12; 29 |
| ArXivMath | 25.4 (12.1--41.1); 6.5; 22 | 31.6 (19.1--45.5); 15.5; 28 |
| **Pooled** | **43.7 (26.4--64.0); 14; 55** | **59.4 (39.5--83.4); 13; 137** |

Successful mutations use fewer character edits on average in all three datasets, but
mutation size again does not cleanly separate outcomes. The confidence intervals
overlap, and exploratory two-sided permutation tests provide no evidence of a
difference (GraduateCourses $p=0.312$, OpenAI-TCS $p=0.712$, ArXivMath $p=0.550$,
pooled $p=0.419$). The OpenAI-TCS median points in the opposite direction from its means
because a few very large unsuccessful edits pull up the unsuccessful mean. Thus the
data do not support the claim that judge misses are explained simply by making
smaller textual changes.

The candidate-level counts and reproducible analysis are in
[`mutated_character_counts.csv`](./mutated_character_counts.csv),
[`mutated_character_summary.json`](./mutated_character_summary.json), and
[`plot_mutated_characters.py`](./plot_mutated_characters.py).

### Trends within datasets.

#### GPT-5.6-sol

The following comparison uses only the frozen GPT-5.6-sol evaluation runs; discovery
mutations are not included. We count individual blind-judge reviews marked as
missed, pooling the unguided and strategy-guided evaluation arms. Invalid mutations
are excluded, and ambiguous reviews remain review opportunities but do not count as
misses. Each label reports the total misses divided by the available review slots
for that area. We pool the two evaluation arms rather than distinguishing guided
from unguided mutations. GraduateCourses is grouped into its three
canonical broad areas; the other corpora use their available subject-area taxonomy.

![Four-panel horizontal bar plot of missed blind-judge reviews by mathematical area
in the Olympiad, GraduateCourses, OpenAI-TCS, and ArXivMath frozen
GPT-5.6-sol evaluations.](./figures/gpt56sol_eval_judge_misses_by_subtopic.png)

**Figure: Evaluation judge misses by mathematical area.** Olympiad misses were
rare across all four subjects: number theory had two, algebra and geometry one each,
and combinatorics none. Within GraduateCourses, algebra and number theory had
17 misses, geometry and topology had ten, and analysis had seven. The OpenAI-TCS misses
were concentrated in coding theory (14) and discrete geometry/sphere packing (nine).
ArXivMath misses were highest in algebra and number theory (19), probability
and combinatorics (11), and logic and dynamics (10), while analysis and PDE had
none. Bars show miss rates, labels retain the underlying miss/review counts, and
error bars are 95% Wilson score intervals. These are descriptive estimates from
small area samples, not evidence that subject area itself causes judge failure.

The plotted counts are in
[`eval_judge_misses_by_subtopic.csv`](./eval_judge_misses_by_subtopic.csv),
[`eval_judge_misses_by_subtopic.json`](./eval_judge_misses_by_subtopic.json), and
[`plot_eval_judge_misses_by_subtopic.py`](./plot_eval_judge_misses_by_subtopic.py).

#### Claude Opus 5

We apply the same counting rule to the four completed Claude Opus 5 frozen
evaluations. As in the GPT-5.6-sol figure, the two evaluation arms are pooled, invalid
mutations are excluded, and each label gives missed reviews divided by all review
slots for valid mutations in that area.

![Four-panel horizontal bar plot of missed blind-judge reviews by mathematical area
in the Olympiad, GraduateCourses, OpenAI-TCS, and ArXivMath frozen Claude Opus 5
evaluations.](./figures/opus5_eval_judge_misses_by_subtopic.png)

**Figure: Claude Opus 5 evaluation judge misses by mathematical area.** In Olympiad,
algebra had ten misses, combinatorics and number theory eight each, and geometry six.
Within GraduateCourses, algebra and number theory had 33 misses, analysis had 22,
and geometry and topology had seven. Within OpenAI-TCS, coding theory had 13 misses,
Ramsey theory six, quantum information three, lattice complexity two, and sphere
packing none. ArXivMath misses were highest in probability
and combinatorics (15) and geometry and topology (14), followed by analysis and PDE
(seven), algebra and number theory (three), and logic and dynamics (two). These are
plotted as miss rates with the underlying counts retained in each label; error bars
are 95% Wilson score intervals. These descriptive estimates from small area samples
do not establish an effect of subject area.

The Opus 5 plotted counts are in
[`opus5_eval_judge_misses_by_subtopic.csv`](./opus5_eval_judge_misses_by_subtopic.csv),
[`opus5_eval_judge_misses_by_subtopic.json`](./opus5_eval_judge_misses_by_subtopic.json),
and
[`plot_opus5_eval_judge_misses_by_subtopic.py`](./plot_opus5_eval_judge_misses_by_subtopic.py).

### Uniqueness of mutations.

#### GPT-5.6-sol

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
| GraduateCourses | 100 | 98 | 70 (71.4%) | 52 (53.1%) |
| OpenAI-TCS | 50 | 44 | 36 (81.8%) | 31 (70.5%) |
| ArXivMath | 50 | 50 | 32 (64.0%) | 21 (42.0%) |
| **Total** | **400** | **392** | **270 (68.9%)** | **206 (52.6%)** |

Here, “distinct logical errors” is the number of semantic equivalence classes;
“singleton mutations” counts candidates whose class appears exactly once. Thus, for
example, the 50 ArXivMath candidates contain 32 different errors, but only
21 candidates are unrepeated singletons. OpenAI-TCS has the highest observed distinct-error
rate, while ArXivMath has the most repetition. Across the four evaluations,
122 of the 392 valid candidates are repetitions beyond the first representative of
their logical-error class. These are manual semantic judgments rather than an
automated string-similarity statistic; the released assignments make every grouping
inspectable.

The candidate-level cluster assignments and the auditable list of non-singleton
groups are in
[`mutation_uniqueness_annotations.json`](./mutation_uniqueness_annotations.json),
[`mutation_uniqueness_annotations.csv`](./mutation_uniqueness_annotations.csv), and
[`analyze_mutation_uniqueness.py`](./analyze_mutation_uniqueness.py).

#### Claude Opus 5

Applying the same candidate-level semantic audit gives the following results for
the three previously annotated Claude Opus 5 evaluations. The now-complete
OpenAI-TCS evaluation is not included because its 46 valid mutations have not yet
received the manual semantic-cluster annotation required for this analysis.

| Evaluation data | Generated candidates | Valid mutations | Distinct logical errors (% of valid) | Singleton mutations (% of valid) |
|---|---:|---:|---:|---:|
| Olympiad | 200 | 199 | 110 (55.3%) | 79 (39.7%) |
| GraduateCourses | 100 | 99 | 79 (79.8%) | 63 (63.6%) |
| ArXivMath | 50 | 50 | 36 (72.0%) | 28 (56.0%) |
| **Total** | **350** | **348** | **225 (64.7%)** | **170 (48.9%)** |

Thus 123 of the 348 valid Opus 5 candidates repeat a logical error already present
in another candidate from the same source proof. GraduateCourses has the highest
observed distinct-error and singleton rates, while Olympiad has the most repetition.
As above, these are manual semantic judgments rather than string-similarity results.

The Opus 5 candidate-level assignments and reproducible aggregation are in
[`opus5_mutation_uniqueness_annotations.json`](./opus5_mutation_uniqueness_annotations.json),
[`opus5_mutation_uniqueness_annotations.csv`](./opus5_mutation_uniqueness_annotations.csv),
and
[`analyze_opus5_mutation_uniqueness.py`](./analyze_opus5_mutation_uniqueness.py).

### Judge runtime.

We measure the wall-clock runtime of each completed blind-judge call in the canonical
frozen evaluations, pooling the unguided and strategy-guided arms. Calls are
restricted to sessions whose mutated proof matches a valid candidate in the
canonical results, so superseded retries are excluded; imported and supplemental
components of the combined evaluations are included. Runtime is the recorded call
duration; for the earlier GPT-5.6-sol OpenAI-TCS run, which did not record it, we
use the span of the call's event trace, which agrees with the recorded duration to
within about one second on later runs.

![Grouped bar plot of mean blind-judge runtime in minutes for GPT-5.6-sol and
Claude Opus 5 across the Olympiad, GraduateCourses, OpenAI-TCS, and ArXivMath frozen
evaluations.](./figures/judge_eval_runtime.png)

**Figure: Mean blind-judge runtime by dataset and model.** Bars show mean minutes per
completed blind-judge call; error bars are percentile 95% bootstrap confidence
intervals over calls. All eight evaluations used medium reasoning effort.

| Evaluation dataset | Model | Completed judge calls | Mean minutes (95% CI) | Median minutes | Max minutes | Excluded failed or unfinished calls |
|---|---|---:|---:|---:|---:|---:|
| Olympiad | GPT-5.6-sol | 600 | 0.61 (0.59--0.64) | 0.56 | 2.1 | 0 |
| Olympiad | Claude Opus 5 | 597 | 0.37 (0.36--0.38) | 0.36 | 0.8 | 0 |
| GraduateCourses | GPT-5.6-sol | 301 | 3.11 (3.03--3.19) | 3.10 | 8.0 | 5 |
| GraduateCourses | Claude Opus 5 | 293 | 4.73 (4.61--4.84) | 4.67 | 7.7 | 8 |
| OpenAI-TCS | GPT-5.6-sol | 131 | 5.49 (5.20--5.81) | 5.02 | 11.5 | 1 |
| OpenAI-TCS | Claude Opus 5 | 116 | 13.42 (11.67--15.29) | 10.71 | 43.4 | 22 |
| ArXivMath | GPT-5.6-sol | 154 | 3.72 (3.54--3.90) | 3.54 | 6.4 | 1 |
| ArXivMath | Claude Opus 5 | 142 | 9.61 (8.58--10.81) | 7.55 | 50.3 | 25 |

Judge runtime grows from well under a minute on Olympiad solutions to several
minutes on the long manuscripts. Claude Opus 5 is faster than GPT-5.6-sol on
Olympiad but slower on the three long-form datasets, most markedly on OpenAI-TCS
and ArXivMath. The Claude means for those two datasets are underestimates of the
time a judge needs: every excluded Claude call there had already run for 20 to 101
minutes before hitting the 20-minute call timeout used for the first ArXivMath
candidates or Claude Code's output-token ceiling. Excluded calls in the other cells
are mostly immediate provider or capacity errors. Wall-clock time also reflects
provider latency and run concurrency, which differed across runs, so these are
operational measurements rather than controlled comparisons of model speed.

The call-level durations, summary statistics, and reproducible analysis are in
[`judge_runtime_calls.csv`](./judge_runtime_calls.csv),
[`judge_runtime_summary.json`](./judge_runtime_summary.json), and
[`plot_judge_runtime.py`](./plot_judge_runtime.py).

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

### GraduateCourses

The GraduateCourses corpus contains 20 cohesive excerpts from official MIT faculty course
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

### OpenAI-TCS

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

### ArXivMath

The ArXivMath corpus contains ten full, proof-bearing arXiv manuscripts, with
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
