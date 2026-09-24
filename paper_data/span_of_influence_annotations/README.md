# Span-of-influence annotation protocol

This directory contains manual annotations for every valid GPT-5.6-sol mutation in
the frozen graduate-course, TCS, and recent-mathematics evaluations.

## Unit and endpoint

The **mutated object** is the mathematical object, assertion, bound, definition, or
inference changed by the mutation. Starting at the first changed line, follow its
direct forward dependency chain inside the enclosing proof or argument. The
**last-influence line** is the last line that explicitly refers to that object or
whose inference directly consumes it. Stop when the resulting claim is packaged as
an opaque lemma, proposition, theorem, case conclusion, or other subresult and later
text merely cites that subresult without reopening the mutated object.

The reported span is the number of **nonblank physical lines**, inclusive, from the
first changed line through the last-influence line in the mutated proof. Thus a
mutation with no downstream direct use has span 1. Comments and purely structural
markup are not counted. When a display is split across several nonblank source
lines, each line counts; this records the amount of proof text a reader must track,
not the number of logical inferences.

For a multi-line or multi-hunk edit, the start is the first changed line and the end
is the last line on the direct dependency chain of any changed component. If the
endpoint is genuinely uncertain, annotators record the most defensible endpoint,
lower and upper plausible spans, and low confidence rather than silently choosing a
different unit.

## Outcome

A valid candidate is **successful** when at least one of its three blind reviews has
`detection == "missed"`. It is **unsuccessful** when none is missed. An ambiguous
review is not itself counted as a miss.

Candidate indices are one-based positions in each canonical `results.json`. TCS
proof text comes from the candidate's `attempts/NNN/mutated_proof.md`; recent-math
proof text is the held-out dossier in
`local_datasets/recent_math_research_dossiers_clean_v1.json` with the recorded diff
applied. Graduate-course proof text is the held-out dossier in
`local_datasets/graduate_course_dossiers_v1.json`, also with the recorded diff
applied. The graduate endpoint map and reconstruction logic are retained in
`paper_data/build_graduate_span_annotations.py`.

## Required fields

Each annotation records `dataset`, `candidate_index`, `proof_id`, `arm`,
`successful`, `missed_reviews`, `mutation_start_line`, `influence_end_line`,
`span_lines`, `span_lower`, `span_upper`, `confidence`, `mutated_object`,
`endpoint_rationale`, and `annotator`.
