# Notable "Do not" rules from distilled strategy libraries

Qualitative summary of the "Do not" sections of the distilled mutation-strategy
libraries across the four headline datasets and both mutator models (Claude Opus 5
and GPT-5.6 Sol). Quotes are verbatim from the libraries; grouping and commentary are
ours.

## Sources

Local run artifacts under `logs/` (ignored; not available on a fresh clone) plus the
tracked audited TCS library:

| Dataset | Mutator | Library |
| --- | --- | --- |
| Olympiad | Opus 5 | `logs/by_dataset/olympiad/olympiad_20_discovery_claude_opus5_default_20260921/distillation/strategies.md` |
| Olympiad | GPT-5.6 Sol | `logs/by_dataset/olympiad/olympiad_20_discovery_gpt56sol_medium_25x_20260924/distillation/strategies.md` |
| GraduateCourses | Opus 5 | `logs/by_dataset/graduate_course/graduate_course_10_discovery_claude_opus5_medium_25x_20260922/distillation/strategies.md` |
| GraduateCourses | GPT-5.6 Sol | `logs/by_dataset/graduate_course/graduate_course_10_discovery_gpt56sol_medium_25x_20260923/distillation/strategies.md` |
| ArXivMath | Opus 5 | `logs/by_dataset/recent_math/runs/recent_math_5_discovery_claude_opus5_medium_25x_20260923/distillation/strategies.md` |
| ArXivMath | GPT-5.6 Sol | `logs/by_dataset/recent_math/runs/recent_math_research_clean_all5_distillation_v1_gpt56sol_medium/distillation/strategies.md` |
| OpenAI-TCS | Opus 5 | `logs/by_dataset/tcs_open_problems/opus5_discovery/distillation_preview_120/strategies.md` (preview distillation, 2026-09-25) |
| OpenAI-TCS | audited | `src/proof_fuzzer/data/audited_persistent_strategies_20260909.md` |

## 1. Internal inconsistency is the dominant detection signal

The most consistent theme across the Opus 5 libraries.

- **TCS:** "Do not leave untouched text that states the now-false consequence." When a
  preserved sentence a line or two later contradicts the edit, "the reviewer then only
  has to read locally."
- **TCS:** "Do not edit a construction the manuscript performs correctly somewhere
  else." A correct parallel instance gives the reviewer a reference point.
- **GraduateCourses:** "Do not introduce a flaw contradicting something else stated in
  the document; internal inconsistency is the most reliable detection signal."
- **ArXivMath:** "Do not leave a statement and its justification, provenance sentence,
  or dependent restatement in disagreement, and do not create a visible clash between
  two cases of the same argument."

## 2. Break the justification, not the conclusion

- **TCS:** "Do not strengthen the conclusion or make the theorem statement false.
  Missed edits keep the conclusion true and merely break its support; a false
  conclusion invites a counterexample hunt." This mirrors the library's core strategy
  (S0): every mutated sentence is true in isolation, and only the implication fails.
- **ArXivMath:** "Do not weaken a statement in a way that breaks a *later* step's
  formal validity; the mutated claim should still imply everything downstream that was
  used."
- **Olympiad:** "Do not change the final answer, the main theorem, or a load-bearing
  inequality that drives the conclusion."
- **GraduateCourses:** "Do not let the conclusion become false in any case the
  document instantiates or computes."

## 3. Reviewers check claims against memory, not only against the proof

- **GraduateCourses:** "Do not insert a claim that is false about a standard, widely
  known object (a homology functor being contravariant, free modules being injective,
  a classical space having a given Euler characteristic or only even cells ...). These
  were caught at once: reviewers check such claims against memory, not against the
  proof."
- **GraduateCourses:** "Do not weaken the hypothesis of a famous theorem when the
  counterexample is itself famous."
- **TCS:** "Do not insert a recognisably false general principle, classification, or
  uniqueness-up-to-a-group statement. Reviewers detect invented structure theory
  quickly. Prefer deleting a hypothesis and substituting a *true* adjacent fact."

## 4. Stylistic tells

- **GraduateCourses:** "Do not make the mutated sentence longer, more formal, or more
  careful than its neighbours." Also: "Do not leave orphaned cross-references,
  renumbered results, or a changed line count."
- **TCS:** "Do not add striking new quantitative claims. ... the missed edits
  preserved all displayed quantities."
- **ArXivMath:** "Do not introduce new notation, new lemmas with new names, changed
  numbering, or changes in prose register."
- **Olympiad:** "Do not put the mutation next to an already-weak or obviously gappy
  section. Reviewers read those closely."

## 5. Error categories that are essentially always caught

- **ArXivMath (Opus 5)** lists mechanisms "caught essentially always", including:
  - hard-analysis manipulation: reversed inequalities, the wrong norm slot in a
    duality estimate, interchange of iterated limits, cross-terms declared to vanish
    ("Reviewers recompute chains of estimates");
  - deleted cases, ill-founded induction measures, circular witnesses, and
    pigeonhole / distinct-representative overreach.
- **TCS:** "Do not aim at steps whose failure is visible from the displayed formulas
  alone (arithmetic slips, sign errors, misapplied standard inequalities)."
- **Olympiad:** "Do not add a lemma whose false claim is then used to skip cases the
  reader naturally rechecks, such as dismissing small cases that a direct check
  handles."

## 6. Model contrast

GPT-5.6 Sol's "Do not" lists are mostly about evidence accounting (e.g. "Do not count
invalid, ambiguous, or failed attempts as demonstrated misses"), whereas Opus 5's
lists are mostly about evading detection. A few Sol items do name conceptual traps:

- **ArXivMath:** "Do not conflate distinctness with disjointness, infinitude with
  dynamical largeness, simple connectivity with acyclicity, or projectivity of a kernel
  with injectivity."
- **ArXivMath:** "Do not infer global structure from checks on generators, selected
  representatives, or one convenient lift."
- **GraduateCourses:** "Do not 'repair' every downstream use. The intended test is
  often whether an unchanged later inference still depends on the original condition."

## 7. Process and meta rules

- **Olympiad:** "Do not assume a whole category is exhausted because one
  implementation was caught. Change the placement or subtlety instead."
- **ArXivMath:** "Do not re-run a mechanism that was already caught in the same
  setting hoping the wording saves it; and do not re-run a mechanism already banked
  with only a change of object, location, citation, or counterexample."

Together these say: retry a caught category with a different mechanism, not the same
mechanism with new wording.

## Caveat

The Opus 5 TCS library is a preview distillation from 2026-09-25. The audited TCS
library tracked in git is older and shorter, and its "Do not" list mainly covers
validity (e.g. "Count a stronger bound as erroneous if unchanged slack ... already
proves it") rather than evading detection.
