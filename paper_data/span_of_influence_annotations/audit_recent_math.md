# ArXivMath span audit

Audited against the annotation protocol, the canonical combined frozen-evaluation
`results.json`, and the held-out proofs in
`local_datasets/recent_math_research_dossiers_clean_v1.json`.

## Mechanical checks

- All 50 result entries are valid and have exactly one annotation, in canonical
  one-based candidate order 1--50.
- Candidate index, proof ID, and arm agree for all 50 entries. Coverage is 10
  candidates for each of the five papers and 25 candidates in each arm.
- `missed_reviews` agrees with the number of canonical reviews whose detection is
  `missed` for all 50 entries. Consequently, all 50 `successful` labels agree with
  the protocol definition (at least one missed review).
- All required fields are present; all endpoints are at or after their starts; and
  every point span lies within its recorded lower and upper bounds.
- Every `mutation_start_line` agrees with the first added line in the canonical
  unified diff. The ArXivMath diffs preserve line numbering.
- I recounted every inclusive start--endpoint interval in the diff-applied dossier,
  excluding blank lines, comments, and purely structural TeX/figure markup as the
  protocol requires. All 50 `span_lines` values are consistent with those intervals.

## Semantic checks

I re-read every candidate with span at least 75: candidates 1, 3, 5, 10, 26, and
28. Candidates 1, 3, 5, and 10 are four independently evaluated instances of the
same gcd mutation. Their changed factor is consumed throughout all three cases of
the representation construction; line 744 is the final directly dependent case
conclusion, giving span 77. Candidate 26 is a genuine multi-hunk strengthening
beginning in the abstract and propagated through the theorem, degree-bound proof,
and appendix; lines 1311--1312 finish the final changed corollary, giving span 624.
Candidate 28 weakens equality of curve classes at line 326; the last direct use is
the cancellation concluding `Cont_T` is Laurent polynomial at line 553, giving span
122. All six endpoints and spans are confirmed.

I also sampled six shorter candidates across both outcomes, both arms, and all five
papers:

| Candidate | Paper | Arm / outcome | Confirmed endpoint and span |
|---:|---|---|---|
| 2 | `arxiv_2405_19197` | generic / successful | The sharper slope-count assertion and its finiteness consequence are entirely on line 571; span 1. |
| 12 | `arxiv_2406_16806` | generic / unsuccessful | The changed algebra invalidates the inverse used through the final splitting-property check on line 280; span 9. |
| 22 | `arxiv_2501_05622` | generic / successful | The shifted index set is last reopened as the “possibilities discussed above” on line 1304; span 7. |
| 34 | `arxiv_2505_05324` | generic / unsuccessful | The enlarged equivariance group is consumed by the false self-duality assertion on line 333; span 8. |
| 41 | `arxiv_2507_21862` | generic / successful | The non-cofinal ideal powers feed the invariant projections through the finite-index contradiction on line 741; span 16. |
| 46 | `arxiv_2507_21862` | strategies / unsuccessful | The broadened kernel hypothesis is consumed by the finite-quotient embedding argument ending on line 943; span 7. |

## Disposition

No corrections are proposed. The audited metadata, outcomes, endpoints, spans, and
confidence levels are consistent with the protocol and canonical artifacts.
