# Independent audit of OpenAI-TCS span annotations

Audited against the canonical OpenAI-TCS `results.json`, each candidate's
`attempts/NNN/mutated_proof.md`, and the annotation protocol in this directory.
No annotation JSON was edited.

## Mechanical checks

- All 44 and only the 44 valid candidates are present (indices 1, 2, 3--6, 8--10,
  12--34, 36--37, and 41--50), with no duplicate indices.
- For every record, `proof_id`, `arm`, `missed_reviews`, and `successful` agree
  with the canonical result. In particular, success is exactly the presence of
  at least one `detection == "missed"` review.
- Endpoint bounds are inside their mutated proof and all required fields are
  populated.
- I recounted nonblank physical lines using newline boundaries (not Python's
  broader `splitlines()`, because these PDF-derived files contain form-feed
  characters). The documented standalone-page-number exclusions reconcile
  candidates 32, 33, 34, and 36. All remaining counts agree except candidates 3
  and 4.

## Proposed corrections

| Candidate | Recorded | Corrected | Reason |
| --- | ---: | ---: | --- |
| 3 | 605 | **606** | Lines 740--1395 contain 606 nonblank physical lines. The endpoint remains line 1395 (the completed contour shift); the discrepancy is a count error caused by treating an embedded form feed as a line boundary. |
| 4 | 15 | **16** | Lines 1457--1472 are all nonblank physical lines. The endpoint remains line 1472 (the packaged positivity conclusion (82)); the same form-feed-sensitive counting error dropped one line. |

The corresponding `span_lower` and `span_upper` should change with
`span_lines` (to 606 for candidate 3 and 16 for candidate 4).

## Semantic checks

I independently re-evaluated every required long or non-high-confidence case:

- spans at least 300: **3, 6, 16, 21, 22, 27, 33, 34, 43, 44**;
- confidence below high: **8**.

I also checked six additional candidates spanning both arms and both outcomes:
**1, 2, 4, 14, 25, 45**.

For candidates 3, 6, 16, 21, 22, 27, 33, 34, 43, and 44, the stated endpoint
is the last direct consumer or derivation of the changed object before the
result is packaged and later cited opaquely. Candidate 8's broader endpoint is
defensible: the changed scale is explicitly reinstantiated as `L_T`; the
recorded medium confidence and lower/upper bounds appropriately preserve the
narrower interpretation that stops after the first construction. The six
additional spot checks likewise agree with their stated endpoints. I found no
semantic endpoint disagreement in the checked set.

## Disposition

The two mechanical corrections above were applied after the independent audit. No
semantic endpoint changes were required.
