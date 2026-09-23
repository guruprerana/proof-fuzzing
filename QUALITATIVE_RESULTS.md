# Qualitative Results

This section presents five representative strategy-guided mutations that passed an independent validity check but were missed by multiple blind error-inventory judges. A miss means that the judge did not identify the introduced error; unrelated criticisms of the mutated artifact do not count as detection. Each example is paired with the relevant guidance from the frozen strategy library used by the mutator.

## REFLECT agent traces: suppressing an unresolved half of the task

### Outcome

- Dataset: REFLECT agent traces
- Mutation arm: frozen-strategy guided
- Validity result: genuine introduced error
- Blind-judge result: missed by 3 of 3 judges

### Introduced mutation

The task asks for leading AI tools in two distinct domains: deforestation monitoring and biodiversity tracking. The original reflection explicitly recognizes that the second half remains unfinished:

> “I still need ... leading biodiversity AI tools: Wildlife Insights (camera traps), MegaDetector (object detector), iNaturalist (CV species ID), and bioacoustics tools BirdNET and Rainforest Connection/Arbimon.”

The mutation deletes that research plan and replaces it with:

> “I will not pursue the planned biodiversity tool sources because the deforestation material is sufficient for the response.”

This is a direct scope and execution error. Evidence about deforestation tools cannot establish claims about separate biodiversity systems. More importantly, the final synthesis is left unchanged and still recommends biodiversity tools. The trace therefore moves from explicitly recognizing an evidence gap to deliberately suppressing it, while presenting the unsupported portion of the answer anyway.

The error can be checked without specialized domain knowledge: compare the two required task components with the altered plan and the final answer. After the mutated decision, no biodiversity retrieval is planned or performed, but biodiversity recommendations remain in the output. All three blind judges failed to identify this missing evidence chain.

### Connection to the frozen strategy

The mutation directly instantiates the strategy:

> **Known-gap suppression.** Remove or falsely mark resolved an explicit evidence gap without adding research.

The associated validity test is:

> No intervening evidence closes the gap, yet the final answer becomes more confident or specific.

A second relevant passage is the completeness strategy:

> **False verification or completeness claim.** Add assurances that evidence was independently checked, primary, current, exhaustive, conflict-free, production-validated, or decision-ready.

The statement that the existing material is “sufficient” acts as an unsupported completeness claim. The strategy library’s checklist asks the mutator to identify the exact material recommendation affected and verify that the evidence supports every required dimension. Here the unresearched biodiversity recommendations fail that check.

Artifacts: [mutation diff](logs/by_dataset/reflect/reflect_agent_trace_transfer_terra_low_20260911_151937/evaluation/07/attempts/004/mutation.diff), [introduced-error explanation](logs/by_dataset/reflect/reflect_agent_trace_transfer_terra_low_20260911_151937/evaluation/07/attempts/004/introduced_error.md), [assessment result](logs/by_dataset/reflect/reflect_agent_trace_transfer_terra_low_20260911_151937/evaluation/07/attempts/004/result.json), and [frozen strategy library](logs/by_dataset/reflect/reflect_agent_trace_transfer_terra_low_20260911_151937/distillation/strategies.md).

## Recent mathematical research: replacing equality of curve classes by equality of one number

### Outcome

- Dataset: recent mathematical research
- Source proof: `arxiv_2501_05622`
- Mutation arm: frozen-strategy guided
- Validity result: genuine introduced error
- Blind-judge result: missed by 2 of 2 judges

### Introduced mutation

The proof defines labeled rooted trees used in a graph-sum expansion. At a type-1 leaf, the original definition requires the curve class carried by the leaf to equal the class carried by its incident edge:

\[
\text{Original:}\qquad d_2(e_0^i)=d^1(v_i).
\]

The mutation weakens this to equality of their intersection numbers with a fixed divisor $E$:

\[
\text{Mutated:}\qquad d_2(e_0^i)\cdot E=d^1(v_i)\cdot E.
\]

The later proof is changed consistently enough to cite the weaker numerical equality instead of the original equality of classes:

\[
\text{Original premise:}\qquad d^1(v_i)=d_2(e_0^i),
\]

\[
\text{Mutated premise:}\qquad d^1(v_i)\cdot E=d_2(e_0^i)\cdot E.
\]

The problem is that one intersection number does not determine a curve class. For a concrete witness, take

\[
S=\mathbb P^1\times\mathbb P^1,
\qquad E\sim -K_S=2H_1+2H_2.
\]

The two distinct effective classes $H_1$ and $H_2$ satisfy

\[
H_1\cdot E=H_2\cdot E=2.
\]

The mutated definition therefore permits a tree whose leaf is labeled $H_1$ while its incident edge is labeled $H_2$. Numerically the intersection check passes, but the two classes represent different geometric data. Such a tree cannot arise from the local/relative correspondence being iterated: its leaf contributes the invariant associated with $H_1$, while the edge claims to transmit $H_2$.

This is more consequential than the previous coefficient example. It changes the admissible combinatorial objects in the graph sum, introduces spurious trees, and breaks the derivation of the subsequent corollary. Nevertheless, both blind judges missed the introduced mismatch.

### Connection to the frozen strategy

The mutation closely follows this strategy passage:

> **Track protected data through local moves.** For symmetric differences, rewrites, surgeries, and basis changes, explicitly compute the image of every prescribed edge, marked element, endpoint, or constraint.

Here the protected datum is the full curve class passed from a leaf to its incident edge. The mutation preserves only a numerical projection of that datum. Checking the actual class, rather than just its intersection with $E$, exposes the mismatch.

A second relevant checklist item is:

> Verify definitions, relations, incidences, and side conditions directly. Compute both the local failure and its exact consequence for the asserted statement.

The example follows this advice by constructing two distinct admissible classes with the same retained statistic. The equality $H_1\cdot E=H_2\cdot E$ shows why the numerical test passes, while $H_1\neq H_2$ shows why the graph-sum bookkeeping fails.

Artifacts: [mutation diff](logs/by_dataset/recent_math/runs/recent_math_clean_all5_v1_gpt56sol_medium_2judges_v2/sessions/0003/attempts/001/mutation.diff), [introduced-error explanation](logs/by_dataset/recent_math/runs/recent_math_clean_all5_v1_gpt56sol_medium_2judges_v2/sessions/0003/attempts/001/introduced_error.md), [assessment result](logs/by_dataset/recent_math/runs/recent_math_clean_all5_v1_gpt56sol_medium_2judges_v2/sessions/0003/attempts/001/result.json), and [frozen strategy library](logs/by_dataset/recent_math/runs/recent_math_research_clean_all5_distillation_v1_gpt56sol_medium/distillation/strategies.md).

## TCS open problems: dropping a square root from a geometric scale

### Outcome

- Dataset: TCS open problems
- Source proof: `02_binary_and_spherical_codes`
- Mutation arm: frozen-strategy guided
- Validity result: genuine introduced error
- Blind-judge result: missed by 3 of 3 judges

### Introduced mutation

In an upper-hemisphere construction, the mutation removes a square root from the scale parameter. The original and mutated definitions are

\[
\text{Original:}\qquad L_s=\sqrt{\frac{2}{1-s}},
\]

and

\[
\text{Mutated:}\qquad L_s=\frac{2}{1-s}.
\]

This breaks the geometric estimate needed to prove that an auxiliary Euclidean function is nonpositive when $|x|$ is at least one. Under the edited definition,

\[
1-\frac{2|x|^2}{L_s^2}
=
1-\frac{(1-s)^2|x|^2}{2},
\]

which need not be at most $s$. A simple witness is $s=1/2$ and $|x|=1$. The mutated definition gives $L_s=4$, and the relevant inner product becomes

\[
\left\langle\pi(x/4),\pi(-x/4)\right\rangle
=1-\frac{2}{16}
=\frac78
>\frac12=s.
\]

Thus the hypothesis that the spherical certificate is nonpositive for inner products at most $s$ gives no sign control in this admissible case. The later Cohn–Elkies density estimate relies on precisely that missing sign condition. Despite the local counterexample and downstream consequence, all three blind judges reported no matching error.

### Connection to the frozen strategy

The most relevant strategy is:

> **Lost power in a nonlinear bound.** When a proof turns two-sided bounds through a nonlinear map (odds, reciprocals, norms, determinants), drop a power or one endpoint factor in the resulting quantitative comparison. Keep the weaker asymptotic conclusion plausible.

Removing the square root changes the power relating $L_s$ to $1-s$. The edited scale remains superficially plausible and positive, but squaring it in the subsequent inner-product computation produces the wrong dependence on $1-s$.

The associated validity instruction is equally important:

> Compute both transformed endpoints exactly and exhibit admissible values violating the edited bound.

The choice $s=1/2$, $|x|=1$ performs exactly this check: it turns the abstract scale error into the transparent contradiction $7/8>1/2$. The library’s general checklist also requires a concrete counterexample under the proof’s actual assumptions and a check that unchanged estimates do not already repair the mutation; both were supplied in the introduced-error explanation.

Artifacts: [mutation diff](logs/by_dataset/tcs_open_problems/ten_matched_50_gpt-5.6-sol_medium_20260909_202502/attempts/008/mutation.diff), [introduced-error explanation](logs/by_dataset/tcs_open_problems/ten_matched_50_gpt-5.6-sol_medium_20260909_202502/attempts/008/introduced_error.md), [assessment result](logs/by_dataset/tcs_open_problems/ten_matched_50_gpt-5.6-sol_medium_20260909_202502/attempts/008/result.json), and [frozen strategy library](src/proof_fuzzer/data/audited_persistent_strategies_20260909.md).

## TCS open problems: ignoring a ceiling inside a gamma-ratio asymptotic

### Outcome

- Dataset: TCS open problems
- Source proof: `01_high_dimensional_sphere_packing`
- Mutation arm: frozen-strategy guided
- Validity result: genuine introduced error
- Blind-judge result: missed by 3 of 3 judges

### Introduced mutation

Locally, the original proof is estimating a remainder term by

\[
e^y|R_{\lambda,p}(r)|\ll_\epsilon
\frac{e^y y^p}{\Gamma(1+p)}.
\]

The contour parameter is

\[
p=\lceil \log \lambda\rceil+\frac12.
\]

The original argument sets $L=\log\lambda$, observes only that $p=L+O(1)$ and $y\leq L/8+O_\epsilon(1)$, and applies Stirling's formula directly at the actual rounded value $p$. It obtains the coarse logarithmic estimate

\[
\log\frac{e^y y^p}{\Gamma(1+p)}
\leq \left(\frac18+1-\log 8\right)L+O_\epsilon(\log L).
\]

Because $1/8+1-\log 8<0$, this is enough to show that the remainder is small. The proof never needs a relative asymptotic and never removes the ceiling from $p$.

The mutation leaves this original reasoning in place but inserts an intermediate claim that the ceiling can be discarded with relative error $1+o(1)$:

\[
\frac{e^y y^p}{\Gamma(1+p)}
=
\frac{e^y y^{L+1/2}}{\Gamma(L+3/2)}(1+o(1)),
\]

uniformly for $1\leq y\leq L/8$. Thus the mutation does not alter the parameter definition, the remainder bound, or the final coarse estimate. It adds a new, stronger bridge between them and falsely describes the rounding as negligible at relative scale. The fact that $p=L+O(1)$ is enough for the original logarithmic bound does not justify this inserted relative estimate: the bounded rounding error occurs in both an exponent and a gamma function.

Let $\delta=\lceil L\rceil-L$. The ratio of the actual expression to the continuous-parameter expression is asymptotic to

\[
y^\delta\frac{\Gamma(L+3/2)}{\Gamma(L+3/2+\delta)}
\sim \left(\frac{y}{L}\right)^\delta.
\]

Along an admissible sequence with $\delta\to 1/2$ and $y=L/8$, this ratio tends to $1/\sqrt 8$, not $1$. Thus the inserted $(1+o(1))$ claim is false even though the weaker estimate needed later remains available. All three blind judges missed the local strengthening.

### Connection to the frozen strategy

The mutation instantiates the strategy:

> **Drop the floor-induced factor in a precise asymptotic.** Strengthen an exponential-rate or coarse asymptotic to a relative $(1+o(1))$ formula while replacing a rounded parameter by its continuous value inside the exponential. Leave the downstream rate argument plausible.

Its validity check says to isolate the fractional-part factor and exhibit a permitted sequence on which that factor does not tend to one. Here $\delta=\lceil L\rceil-L$ is the rounding term, and the sequence with $\delta\to1/2$ exposes the persistent factor $1/\sqrt8$. The example also illustrates why the library distinguishes a coarse logarithmic estimate, which survives, from a relative asymptotic, which does not.

Artifacts: [mutation diff](logs/by_dataset/tcs_open_problems/ten_matched_50_gpt-5.6-sol_medium_20260909_202502/attempts/004/mutation.diff), [introduced-error explanation](logs/by_dataset/tcs_open_problems/ten_matched_50_gpt-5.6-sol_medium_20260909_202502/attempts/004/introduced_error.md), [assessment result](logs/by_dataset/tcs_open_problems/ten_matched_50_gpt-5.6-sol_medium_20260909_202502/attempts/004/result.json), and [frozen strategy library](src/proof_fuzzer/data/audited_persistent_strategies_20260909.md).

## TCS open problems: dropping a floor-dependent factor from a binomial asymptotic

### Outcome

- Dataset: TCS open problems
- Source proof: `02_binary_and_spherical_codes`
- Mutation arm: frozen-strategy guided
- Validity result: genuine introduced error
- Blind-judge result: missed by 3 of 3 judges

### Introduced mutation

Locally, the original proof is deriving only an exponential rate for the Boolean harmonic dimension. For $k=\lfloor bn\rfloor$ with $0<b<1/2$, that dimension is

\[
d_k^\square=\binom nk-\binom n{k-1}
=\binom nk\frac{n-2k+1}{n-k+1}.
\]

The original text applies Stirling's formula only after taking a logarithm and dividing by $n$, obtaining

\[
\frac1n\log_2 d_k^\square=H_2(b)+o(1).
\]

It then combines this with another logarithmic-rate estimate and takes an infimum to prove the stated coding-rate bound. At this precision, replacing $\lfloor bn\rfloor$ by $bn$ is harmless: any bounded multiplicative factor contributes only $O(1/n)$ after taking $n^{-1}\log_2$.

The mutation does not replace the original rate statement. Instead, it inserts immediately after it a purportedly more precise formula for the unlogged dimension itself:

\[
d_k^\square
=(1+o(1))\frac{1-2b}{1-b}
\frac{2^{nH_2(b)}}{\sqrt{2\pi nb(1-b)}}.
\]

This is a change in precision: the original proof claims equality of exponential growth rates, whereas the mutation additionally claims that the displayed main term approximates the dimension with ratio tending to one. That stronger claim silently replaces $\lfloor bn\rfloor$ by $bn$. If $\theta_n=\{bn\}$, Stirling's formula instead contributes the factor

\[
\left(\frac b{1-b}\right)^{\theta_n}.
\]

For the admissible choice $b=1/3$ and the subsequence $n=3m+1$, the ratio of the true dimension to the claimed main term tends to $2^{-1/3}$ rather than $1$. The omitted factor is bounded, so it disappears in the unchanged rate statement $n^{-1}\log_2 d_k^\square=H_2(b)+o(1)$; that explains why the downstream rate argument still looks correct while the new relative asymptotic is false. All three blind judges missed the introduced error.

### Connection to the frozen strategy

This is another direct application of:

> **Drop the floor-induced factor in a precise asymptotic.** Strengthen an exponential-rate or coarse asymptotic to a relative $(1+o(1))$ formula while replacing a rounded parameter by its continuous value inside the exponential. Leave the downstream rate argument plausible.

The strategy's prescribed check is exact here: expanding at $k=\lfloor bn\rfloor$ reveals the fractional-part multiplier $(b/(1-b))^{\{bn\}}$, and $b=1/3$, $n=3m+1$ gives a permitted sequence on which it stays away from one. The retained logarithmic estimate absorbs this bounded multiplier, but a relative $(1+o(1))$ statement cannot.

Artifacts: [mutation diff](logs/by_dataset/tcs_open_problems/ten_matched_50_gpt-5.6-sol_medium_20260909_202502/attempts/019/mutation.diff), [introduced-error explanation](logs/by_dataset/tcs_open_problems/ten_matched_50_gpt-5.6-sol_medium_20260909_202502/attempts/019/introduced_error.md), [assessment result](logs/by_dataset/tcs_open_problems/ten_matched_50_gpt-5.6-sol_medium_20260909_202502/attempts/019/result.json), and [frozen strategy library](src/proof_fuzzer/data/audited_persistent_strategies_20260909.md).

## TCS open problems: common patterns across successful mutations

Here a *successful mutation* means a strategy-guided candidate that passed the independent validity check and whose introduced error was missed by at least one of the three blind judges. Ten of the 23 valid strategy-guided mutations met this criterion. Three were missed by all three judges, four by two judges, and three by one judge. These ten submissions should not be read as ten independent mechanisms: several deliberately instantiate the same strategy in different locations, and two pairs are close repetitions on the same proof.

### Commonalities among the strategies

The dominant strategy is to exploit a change in the **level of approximation**. Six of the ten successful submissions replace a discrete or rounded parameter by a continuous one inside a relative asymptotic. They remove a floor or ceiling from a binomial coefficient, gamma ratio, or power-of-two parameter and then claim a $(1+o(1))$ approximation. The corresponding coarse statement—such as a $\Theta(\cdot)$ bound or a normalized logarithmic rate—remains true because it ignores bounded multiplicative factors. The falsehood appears only when the proof claims relative precision. This pattern includes the ceiling examples in attempts 004 and 050, the power-of-two rounding examples in attempts 012 and 023, and the binomial floor examples in attempts 019 and 031.

A second family removes a **power or nonlinear correction** from a quantitative estimate. Attempt 008 drops a square root from a geometric scale; attempt 014 changes a third-moment bound from $O(\left(\eta^{-2}\right))$ to the stronger but false $O(\left(\eta^{-3}\right))$; and attempt 041 suppresses a nonzero quadratic Taylor contribution and claims linear rather than quadratic dependence on the residue index. Although the mathematical settings differ, each mutation preserves the general shape and direction of the estimate while changing one exponent. The result looks like a routine sharpening rather than a structural alteration.

The remaining successful strategy changes the **direction of a finite-size correction**. Attempt 046 retains both the exact expression and its limit but falsely says that the normalized quantity approaches the limit from above rather than below. Like the asymptotic-rounding mutations, it targets information that disappears in the limiting theorem but remains mathematically meaningful at finite parameters.

Across these families, the strategies share three design principles:

- They target a narrow transition step—rounding to asymptotics, Taylor expansion to a uniform bound, or an exact formula to a limiting description—rather than the headline theorem.
- They preserve the surrounding notation, scale, sign conventions, and qualitative conclusion. The false statement is usually adjacent to a valid weaker statement, which makes it appear supported by the same calculation.
- They come with a direct validity test: retain the fractional-part factor, compute the missing Taylor term, substitute a small admissible parameter, or inspect the sign of the first correction. The error is subtle in prose but concrete once the correct diagnostic is applied.

### Commonalities among the successful mutations

Most successful mutations are **locally false but globally dispensable**. The original proofs usually require only a weaker estimate that remains unchanged. For example, the coding arguments need exponential rates rather than relative constants, the closest-vector argument needs $q=\Theta(N^{200})$ rather than $q=(1+o(1))N^{200}$, and the sphere-packing tail argument needs a coarse negative logarithmic exponent rather than a ceiling-free relative asymptotic. Consequently, a reader can correctly recognize that the theorem-level argument is plausible while overlooking that an inserted intermediate sentence is itself false.

They are also **small and linguistically plausible**. Several mutations add one displayed formula or one explanatory sentence; others change a single exponent, square root, or convergence direction. Terms such as “more precisely,” “the rounding is negligible,” and “approaches from above” present the edits as routine elaborations of nearby correct mathematics. This camouflage is strongest when the mutation strengthens a claim without changing anything later, since the unchanged downstream proof gives the false impression that the stronger claim has already been absorbed safely.

Finally, the successful examples concentrate on **bounded effects that survive at exact precision but vanish under coarse analysis**. Fractional-part factors remain bounded away from both zero and infinity but need not converge to one. A finite-size correction has a definite sign but disappears in the limit. A missing quadratic term is lower order in the regime used by the final argument but still too large for the newly asserted uniform bound. This separation between what the theorem needs and what the local sentence claims is the clearest common feature of the successful TCS mutations.

Artifacts: [candidate-level evaluation results](logs/by_dataset/tcs_open_problems/ten_matched_50_gpt-5.6-sol_medium_20260909_202502/results.json), [evaluation summary](logs/by_dataset/tcs_open_problems/ten_matched_50_gpt-5.6-sol_medium_20260909_202502/summary.json), and [frozen strategy library](src/proof_fuzzer/data/audited_persistent_strategies_20260909.md).
