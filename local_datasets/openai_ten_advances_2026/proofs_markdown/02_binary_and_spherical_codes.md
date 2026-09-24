# Improved Bounds for Binary and Spherical Codes

> Source: OpenAI, *Ten Advances in Mathematics and Theoretical Computer Science*, Chapter 2, PDF pages 31–81. Layout-preserving text extraction; consult the source PDF for authoritative equation rendering.

                                   Chapter 2

Improved Bounds for Binary and Spherical
                Codes
    Abstract. We construct two-point linear-programming certiﬁcates that im-
    prove the high-dimensional bounds for unrestricted binary and spherical codes.
    For every ﬁxed relative distance 0 < δ < 1/2, our binary-code bound strictly im-
    proves the optimized McEliece–Rodemich–Rumsey–Welch exponent. For every
    ﬁxed maximum inner product 0 < s < 1, our spherical-code bound strictly im-
    proves the optimized Kabatianskii–Levenshtein exponent, including its spherical-
    cap optimization. These are the ﬁrst improvements to the respective general high-
    dimensional exponents since 1977 and 1978. In the limit s → 1, the spherical
    construction also recovers the optimal sphere-packing exponent of the Euclidean
    Cohn–Elkies linear program, obtained independently in a companion paper in
    Chapter 1.



                                      Contents
1. Introduction
2. The ﬁrst binary bound
3. The optimized binary bound
4. Representation graphs for spherical codes
5. Spherical harmonics and stabilizer representations
6. The spherical transition graph
7. Asymptotic spherical-code bounds
8. Sphere packings
Appendix A. Orthogonal representations and asymptotic dimensions
Appendix B. The spherical-to-Euclidean limit
References




                                           27
                                       1. Introduction
   A binary code C ⊆ {0, 1}n has Hamming distance dH (x, y), the number of coordinates in
which two words diﬀer; its minimum distance is the smallest such value for distinct codewords.
Let A2 (n, d) denote the largest code size with minimum distance at least d. A spherical code
C ⊆ Sn−1 has maximum inner product at most s when hx, yi ≤ s for distinct points; let A(n, s)
denote its largest size. For ﬁxed relative distance 0 < δ < 1/2 and maximum inner product
0 < s < 1, the corresponding asymptotic rates are
                               1                                           1
             R2 (δ) = lim sup log2 A2 (n, dδne),       Rsph (s) = lim sup log2 A(n, s).
                        n→∞    n                                      n→∞  n
   The best previous general bounds on these rates are due to McEliece, Rodemich, Rumsey, and
Welch (MRRW) for unrestricted binary codes and to Kabatianskii and Levenshtein for spherical
codes [MRRW77, KL78]. Both arise from Delsarte’s two-point programs [Del72, Del73, DGS77].
                                                 P
A Delsarte certiﬁcate is a polynomial F (t) = M    j=0 fj Pj (t) in the Krawtchouk, Hahn, or Gegen-
bauer basis associated with the code space, with P0 = 1. If f0 > 0, fj ≥ 0 for 1 ≤ j ≤ M ,
and F (t) ≤ 0 at every normalized inner product allowed by the distance constraint, then
|C| ≤ F (1)/f0 . Our constructions verify positivity directly through projection Gram factoriza-
tions, without requiring explicit orthogonal-polynomial formulas or a converse characterization
of positive-deﬁnite kernels.
   In the classical spectral construction, each retained harmonic space contributes a single vector
associated with a code point [BN06]. We instead associate a dE -dimensional subspace with each
point x, inside a common D-dimensional ambient space. The subspaces move with the points:
a symmetry carrying x to y carries the subspace at x to the subspace at y. If Px denotes
the corresponding orthogonal projection, the overlap tr(Px Py ) is still a scalar function of the
distance. Write s for the largest permitted normalized inner product and Λ for the largest
eigenvalue of the associated weighted transition matrix. If Λ > s, the projection bound (52)
gives
                                                  1−s D
                                           |C| ≤           .
                                                 Λ − s dE
Thus an exponentially large projection rank improves the rate provided Λ remains bounded away
from the threshold s. For binary codes, the transition matrices are tridiagonal; for spherical
codes, the full construction uses weighted graphs with several degree indices.
   Bachoc and Vallentin also exploit higher harmonics of the rotations ﬁxing a point [BV08,
§3]. Their ﬁxed base point yields matrix-valued, three-point semideﬁnite programs. Here the
subspace moves with each code point, giving scalar two-point certiﬁcates whose bounds contain
its dimension through D/dE .
1.1. Binary codes: statement of the result. We ﬁrst recall the classical binary-code bounds
and then state the two constructions needed to improve the fully optimized second MRRW
bound. The whole-cube construction improves the ﬁrst MRRW bound, while the constant-
weight construction handles parameter ranges where optimization over layers gives a stronger
classical bound.
   With 0 log2 0 = 0, deﬁne the binary entropy function H2 and an auxiliary function g on [0, 1]
by                                                                       √      !
                                                                     1− 1−v
            H2 (u) = −u log2 u − (1 − u) log2 (1 − u),   g(v) = H2                .
                                                                          2
The ﬁrst MRRW bound is [MRRW77]
                                                           
                                                1 q
                                M1 (δ) = H2       − δ(1 − δ) .                              (1)
                                                2
In particular, R2 (δ) ≤ M1 (δ). To state the whole-cube improvement, introduce normalized
degree parameters 0 ≤ b < a ≤ 1/2. In the ﬁnite construction, a = L/n records the largest
retained Fourier degree, meaning the number of coordinates in a Fourier monomial, and b = k/n




                                                28
records the degree of the Boolean harmonic subspace attached to each code point. The spaces
are constructed in §2. Set
                                             2(a − b)(1 − a − b)
                                 ΓH (a, b) =     p               .
                                                   a(1 − a)
The whole-cube construction gives the tridiagonal matrix (22), whose limiting largest eigenvalue
is ΓH (a, b) by Lemma 2.2. Its resulting exponent is
                                                                          
                                κH (δ) =       inf         H2 (a) − H2 (b) .                      (2)
                                            0≤b<a≤1/2
                                           ΓH (a,b)>1−2δ

Here H2 (a) and H2 (b) are the dimension exponents of the retained ambient space and attached
harmonic subspace, respectively. Theorem 2.3 proves that, for every 0 < δ < 1/2,
                                      R2 (δ) ≤ κH (δ) < M1 (δ).
   The second MRRW bound optimizes the classical construction over constant-weight lay-
ers [MRRW77]. Its scalar parameter τ reparametrizes the polynomial       p degree: on the classical
spectral boundary, a largest retained degree un corresponds to τ = 2 u(1 − u). The objective
is
                  Fδ (τ ) = 1 + g(τ 2 ) − g(τ 2 + 2δτ + 2δ),     0 ≤ τ ≤ 1 − 2δ.
The endpoints are
                           Fδ (1 − 2δ) = M1 (δ),      Fδ (0) = 1 − g(2δ),
and the second MRRW bound is the full optimized exponent
                                      M2 (δ) =       min      Fδ (τ ).                            (3)
                                                  0≤τ ≤1−2δ

Thus R2 (δ) ≤ M2 (δ) ≤ min{M1 (δ), Fδ (0)}. The minimum over all τ can occur in the interior
and be strictly smaller than both endpoint values. Therefore, improving M1 alone need not
improve M2 , so we reﬁne the constant-weight construction as well.
   A weight-w layer of the binary cube consists of all binary words having exactly w coordinates
equal to 1. Fixing one such word partitions the coordinates into its w-element support and its
(n−w)-element complement. The construction attaches the tensor product of Boolean harmonic
spaces of degrees p and q on these two coordinate sets and retains layer degrees up to L. Write
α = w/n, β = p/n, γ = q/n, and u = L/n for the normalized layer weight, harmonic degrees,
and largest retained layer degree, respectively. §3 constructs these spaces and an associated
tridiagonal matrix. The parameter ranges are
                        δ        1                α                1−α
                           <α< ,        0≤β< ,            0≤γ<          ,                    (4)
                        2        2                2                  2
and
                         β + γ < u < min{α, α − β + γ, 1 − α + β − γ}.                       (5)
The following function determines which parameter choices yield a code bound; its origin is
explained in Lemma 3.5. Introduce the aﬃne coordinates
         z = 1 − 2u,        m = 1 − 2α,         ζ = 1 − 2β − 2γ,         ξ = 1 − 2α + 2β − 2γ.
Deﬁne
                                        (ζξ − mz 2 )2        (z 2 − ξ 2 )(ζ 2 − z 2 )
                       Λα,β,γ (u) =                       +                √          .            (6)
                                   z 2 (1 − m2 )(1 − z 2 ) z 2 (1 − m2 ) 1 − z 2
Two weight-αn words at Hamming distance δn have normalized layer-distance coordinate 1 −
δ/(2α(1 − α)); see (30). The construction applies when the preceding function exceeds this
coordinate:
                                                            δ
                                     Λα,β,γ (u) > 1 −              .                               (7)
                                                        2α(1 − α)
Let Dδ be the set of all (α, β, γ, u) in the ranges (4)–(5) that also satisfy (7). The resulting
unrestricted-code exponent from constant-weight (CW) layers is
                                                                                          
                                                                  β                        γ
        κCW (δ) =      inf       1 − H2 (α) + H2 (u) − αH2             − (1 − α)H2               . (8)
                  (α,β,γ,u)∈Dδ                                    α                       1−α


                                                     29
The four terms have a direct dimension interpretation. Passing from the whole cube to a weight-
αn layer costs 1 − H2 (α), since that layer has 2(H2 (α)+o(1))n words. The retained ambient space
has dimension 2(H2 (u)+o(1))n , while the subspace attached to a code point has dimension
                               2(αH2 (β/α)+(1−α)H2 (γ/(1−α))+o(1))n .
Dividing the ambient dimension by this subspace dimension produces the two entropy subtrac-
tions in (8). Finally, set
                              κbin (δ) = min{κH (δ), κCW (δ)}.
Theorem 1.1. For every ﬁxed 0 < δ < 1/2,
                                    R2 (δ) ≤ κbin (δ) < M2 (δ).
   The classical MRRW constructions are boundary subfamilies of the enlarged variational prob-
lems: b = 0 recovers M1 , and β = γ = 0 recovers Fδ . Theorem 2.3 and Proposition 3.7 show
that introducing positive harmonic degrees strictly improves the ﬁrst MRRW bound and the
classical constant-weight objective at every interior optimizing layer.
   If the endpoint τ = 1 − 2δ minimizes (3), then M2 = M1 and the whole-cube construction
gives the strict improvement. Otherwise, the constant-weight construction strictly improves a
minimizing layer. Theorem 3.8 combines these cases to prove Theorem 1.1.
1.2. Spherical codes: statement of the result. Fix a maximum inner product 0 < s <
1. We ﬁrst recall the classical spherical-code bound and its spherical-cap optimization, then
illustrate our improvement using harmonics on the directions orthogonal to a code point. Finally,
we state the full hierarchy; its sphere-packing consequence follows in the next subsection.
   For u ≥ 0, deﬁne the spherical harmonic dimension exponent by
                   Hsph (u) = (1 + u) log2 (1 + u) − u log2 u,       Hsph (0) = 0.             (9)
Indeed, the space of degree-un + o(n) spherical harmonics has dimension 2(Hsph (u)+o(1))n ; the
exact formula is recorded in (61). Applying the Kabatianskii–Levenshtein bound directly to the
whole sphere gives
                                                                 1                  
                  A(n, s) ≤ 2(Hsph (a0 (s))+o(1))n ,   a0 (s) =     (1 − s2 )−1/2 − 1 .
                                                                 2
   A stronger classical bound ﬁrst restricts the code to a suﬃciently populated spherical cap and
projects that cap onto a lower-dimensional sphere. Sidelnikov’s spherical-slice inequality replaces
the original inner-product threshold s by a smaller threshold 0 ≤ t ≤ s, at an exponential cost
2 log2 ((1 − t)/(1 − s)) [Sid74]. Combining this spherical-cap reduction with the Kabatianskii–
1

Levenshtein construction gives the optimized classical exponent [KL78, Thm. 4]
                                                                           
                                                               1      1−t
                             BKL (s) = inf Hsph (a0 (t)) + log2               .                (10)
                                        0≤t≤s                  2      1−s
Thus Rsph (s) ≤ BKL (s).
   For x ∈ Sn−1 , let Ek,x = Hk (x⊥ ) be the space of degree-k spherical harmonics on the unit
sphere in x⊥ . For k = 0, this is the classical space of constants; for k = 1, it consists of
linear functions on x⊥ . Every ambient harmonic space Hi (Rn ) with i ≥ k contains a naturally
associated copy of Ek,x ; see §5.2 for the construction.
   Retain these copies for k ≤ i ≤ L, and write a = L/n, b = k/n, with 0 ≤ b < a. Coordi-
nate multiplication connects consecutive ambient harmonic spaces, giving a tridiagonal matrix
indexed by i = k, . . . , L. Deﬁne
                              (a − b)(1 + a + b)
               Γrow (a, b) =           p             ,  Φrow (a, b) = Hsph (a) − Hsph (b).     (11)
                              (1 + 2a) a(1 + a)
This construction gives, whenever 2Γrow (a, b) > s,
                                   A(n, s) ≤ 2(Φrow (a,b)+o(1))n .




                                                 30
Since dim Ek,x = 2(Hsph (b)+o(1))n , the projection rank subtracts Hsph (b) from the ambient expo-
nent Hsph (a). Optimizing over b > 0 strictly improves both the direct Kabatianskii–Levenshtein
bound and, after spherical-cap reduction, its optimized version.
   For the full hierarchy, ﬁx an integer r ≥ 0 and choose vectors a = (a1 , . . . , ar+1 ) and b =
(b1 , . . . , br ) satisfying
                                a1 > b1 > a2 > · · · > br > ar+1 ≥ 0.
For r = 0, the chain means simply a1 ≥ 0. The relevant orthogonal-group representations
are indexed by Young diagrams, and aℓ and bm are their row lengths divided by n. The
hierarchy level r counts the rows of the subspace associated with each code point; the ambient
representation has one additional row. Their representation-theoretic meaning and the resulting
weighted adjacency matrices are developed in §§5.3 and 7. Level r = 0 recovers the classical
construction; when r = 1, setting a2 = 0 gives the harmonics on x⊥ in (11). Introduce the
quadratic coordinates and scalar function
                                                p
                                        u(1 + u)
            A(u) = u(1 + u),         q(u) =       ,     xℓ = A(aℓ ),    ym = A(bm ).
                                        1 + 2u
For 1 ≤ ℓ, j ≤ r + 1 and 1 ≤ m ≤ r, deﬁne Rℓ , Γr = Γr (a, b), and Φr = Φr (a, b) by
           Qr
                (xℓ − ym )                      X
                                                r+1                          X
                                                                             r+1                  X
                                                                                                  r
      Rℓ = Qm=1            ,             Γr =         Rℓ q(aℓ ),      Φr =         Hsph (aℓ ) −         Hsph (bm ).
                j6=ℓ (xℓ − xj )                 ℓ=1                          ℓ=1                  m=1
The
P
     displayed strict inequalities make every Rℓ positive, and Lagrange interpolation gives
  ℓ Rℓ = 1; see (83). The spectral calculation and dimension estimate giving 2Γr and Φr
appear in Lemmas 7.2 and A.1. Empty products and sums take their usual values, so the
deﬁnitions include r = 0.
Theorem 1.2. Fix r ∈ Z≥0 , 0 < s < 1, and nonnegative vectors a = (a1 , . . . , ar+1 ) and
b = (b1 , . . . , br ) satisfying aℓ > bℓ > aℓ+1 for 1 ≤ ℓ ≤ r. Then
                           2Γr (a, b) > s        =⇒        A(n, s) ≤ 2(Φr (a,b)+o(1))n .
Here o(1) → 0 as n → ∞ with r, s, a, b ﬁxed. Consequently,
                              Rsph (s) ≤ inf                    inf          Φr (a, b).
                                           r∈Z≥0 a1 >b1 >···>br >ar+1 ≥0
                                                       2Γr (a,b)≥s

   The non-strict constraint 2Γr ≥ s follows by approximating its equality boundary with pa-
rameters satisfying 2Γr > s. Write κr (s) for the inner inﬁmum in Theorem 1.2, taken over a, b
at the ﬁxed hierarchy level r, and set κr (0) = 0. Applying the spherical-cap reduction from (10)
gives                                                            
                                                      1       1−t
                              κr (s) = inf κr (t) + log2            .                        (12)
                                      0≤t≤s           2       1−s
Consequently,
                                       Rsph (s) ≤ inf κr (s).
                                                             r≥0
  Level 0 recovers the classical Kabatianskii–Levenshtein construction [KL78], so κ0 = BKL by
(10). The one-row construction (11) is obtained from level 1 by setting a2 = 0; write κrow for its
spherical-cap-optimized exponent. The full strict hierarchy, including this intermediate one-row
improvement, is proved in Corollary 7.6.
Corollary 1.3. For every 0 < s < 1 and every r ≥ 0,
                                  κr+1 (s) < κr (s),            κr+1 (s) < κr (s).
Moreover,
                     Rsph (s) ≤ inf κr (s) < κ1 (s) < κrow (s) < κ0 (s) = BKL (s).
                                   r≥0




                                                           31
1.3. Sphere-packing consequence. Let ∆n denote the maximal packing density in Rn . For
−1 < s < 1, projection from the upper hemisphere gives [Sid74, KL78, CZ14]
                                                  n/2
                                             1−s
                                  ∆n ≤                    A(n + 1, s).
                                              2
Consequently, if A(n, s) ≤ 2(B(s)+o(1))n , then
                                                    1      2
                                   ∆n ≤ 2(B(s)− 2 log2 1−s +o(1))n .                          (13)
For spherical codes at a ﬁxed threshold s, passing to a spherical cap can improve the exponent
by replacing s with some t ≤ s. The packing transfer behaves diﬀerently: the cost of passing to
that cap exactly oﬀsets the change in its geometric packing factor. Indeed, at hierarchy level r,
                   1       2      1      1−t             1        2
                     log2      − log2          − κr (t) = log2        − κr (t).
                   2      1−s 2          1−s             2      1−t
Thus transferring a cap-improved spherical bound at threshold s gives exactly the packing
exponent obtained by transferring the direct spherical bound at threshold t; see (95). Optimizing
over the hierarchy and the threshold therefore requires no additional cap optimization.
Corollary 1.4. As n → ∞,
                                                         1      2π
                             ∆n ≤ 2−(λ∗ +o(1))n ,         λ∗ =
                                                           log2    .
                                                         2       e
   This improves the classical Kabatianskii–Levenshtein sphere-packing exponent [KL78, Lev79]
and attains the Cohn–Elkies rate conjectured in [AJCHLT20, Conjs. 3.1–3.2]. The exact hier-
archy limit and the order of the dimension, hierarchy-depth, and small-angle limits are proved
in Theorem 8.3. Figure 1 illustrates the successive spherical improvements and their sphere-
packing consequences.
Remark 1.5. Gorbachev and, independently, Cohn and Elkies developed the Euclidean Fourier-
analytic linear program for sphere packing [Gor00, CE03]; optimizing its auxiliary functions is
called the Cohn–Elkies linear program. The companion paper in Chapter 1 gives an independent,
self-contained determination of its optimal exponent by proving a lower bound for every auxiliary
function satisfying the Cohn–Elkies Fourier-positivity and sign conditions and constructing
matching Euclidean witnesses. If LPn denotes the optimal density bound of that program, its
result is                                           r
                                               1/n      e
                                        lim LPn =         .
                                       n→∞             2π
Cohn and Zhao’s upper-hemisphere construction also converts our spherical certiﬁcates into fea-
sible Euclidean auxiliary functions [CZ14, Thm. 3.4 and subsequent discussion]. The subsequent
discussion covers s > 1/2, as required in the limit s ↑ 1. §B further identiﬁes the main weight
in the companion paper’s Euclidean construction with the small-angle limit of our spherical
certiﬁcates.
Remark 1.6. The spherical and binary constructions diﬀer in the multiplicities that can arise
when an ambient representation is restricted to a point stabilizer. This distinction is expressed
by Gelfand pairs and strong Gelfand pairs [Kra76, CST08]. For a compact group G and a
point stabilizer H, the pair (G, H) is a Gelfand pair when dimC HomH (1, V ) ≤ 1 for every
irreducible complex G-representation V . Thus each ambient representation contains at most
one stabilizer-ﬁxed line, as in the classical constructions. The pair is a strong Gelfand pair when
dimC HomH (E, V ) ≤ 1 for every irreducible complex H-representation E. This stronger condi-
tion permits nontrivial stabilizer representations while retaining scalar transition coeﬃcients.
   The spherical pair (SO(n), SO(n − 1)) is strong by the multiplicity-free branching rule
(74) [GW09, Thms. 8.1.3–8.1.4]. For the Hamming cube and a weight-w layer, the respective
pairs are
                       (Bn , Sn ),   (Sn , Sw × Sn−w ),     Bn = {±1}n ⋊ Sn .
Both are Gelfand pairs but need not be strong. For example, the Littlewood–Richardson coef-
        (3,2,1)
ﬁcient c(2,1),(2,1) = 2 produces multiplicity two in both restrictions. Nevertheless, the Fourier


                                                   32
Successive improvement (bits per dimension)           (a) Spherical-code improvements                                                                     (b) Derived sphere-packing bounds

                                              10−3                                                                                                 0.60




                                                                                                                          Packing exponent G(s)
                                              10−5
                                                                                                                                                   0.58



                                              10−7
                                                                                                                                                   0.56



                                              10−9                                                                                                                                Classical KL
                                                                                          0 < B3 < B2 < B1 < Brow < BKL                            0.54                           One-row restriction
                                                                                                      BKL − Brow
                                                                                                                                                                                  Full level r = 1
                                                                                                      Brow − B1                                                                   Level r = 2
                                              10−11                                                   B1 − B2                                                                     Level r = 3
                                                                                                      B2 − B3                                      0.52                           Hierarchy limit λ * (r → ∞, s → 1)


                                                             0.2        0.4         0.6                 0.8                                                     0.2       0.4       0.6              0.8
                                                                        Inner product s                                                                                  Inner product s



                                                      Figure 1. Spherical-code improvements and sphere-packing optimization. In
                                                      panel (a), BKL = κ0 and Br = κr are the spherical-code growth exponents de-
                                                      ﬁned in (10) and (12); Brow = κrow comes from (11). Thus A(n, s) ≤ 2(B(s)+o(1))n ,
                                                      and 0 < B3 < B2 < B1 < Brow < BKL . Their successive positive diﬀerences are
                                                      shown on a logarithmic scale, with values at most 5×10−13 omitted. The rapidly
                                                      decreasing diﬀerences suggest convergence toward the inﬁnite-level bound. Strict
                                                      improvement is proved in Corollary 1.3. Panel (b) plots the packing objective
                                                      GF (s) = 21 log2 (2/(1 − s)) − κF (s) for the unlocalized classical, one-row, and
                                                      level-r certiﬁcate families; the corresponding sphere-packing density satisﬁes
                                                      ∆n ≤ 2−(GF (s)+o(1))n by (13). Circles mark the numerically estimated optimizing
                                                      angles, the horizontal dashed line is λ∗ , and the dotted vertical line marks the
                                                      kissing angle s = 1/2. The clustering of the ﬁnite-level curves near λ∗ reﬂects
                                                      the same rapid numerical convergence. All plotted values are numerical.

spaces in §2.1 and the two-row Johnson spaces in Lemma 3.1 contain the selected stabilizer
types with multiplicity one. Consequently, both binary arguments remain scalar. More general
binary stabilizer types can require matrix-valued transitions, but they are unnecessary for the
all-distance improvement proved here.
Remark 1.7. Our bounds concern unrestricted codes with ﬁxed relative distance or ﬁxed max-
imum inner product in dimensions tending to inﬁnity. Previous spherical constructions in the
same high-dimensional, ﬁxed-angle setting improve the direct Kabatianskii–Levenshtein bound
for some angles. Relative to the classical bound after spherical-cap optimization, however,
those results improve the bound by constant multiplicative factors rather than its exponential
rate [SZ24, Z24]. Other results address restricted code families, diﬀerent asymptotic regimes,
or speciﬁc dimensions. The Cohn–Elkies bound is sharp in dimensions 8 and 24, where the
E8 and Leech lattice packings are optimal, respectively [Via17, CKMRV17]. The n-dimensional
kissing number is τn = A(n, 1/2). Already hierarchy level 2 gives τn ≤ 2(0.39661+o(1))n , compared
with the optimized classical exponent 0.400944 . . .. Its values are known exactly in dimensions
3 [SvdW53], 4 [Mus08], 8 [Lev79], and 24 [OS79]. Semideﬁnite programs improve further ﬁnite-
dimensional binary and spherical bounds [Sch05, BV08]. MacWilliams’s weight-transform iden-
tities and subsequent spectral and higher-order methods apply to the restricted class of linear
codes [Mac63, FT05, CJJ22, √ LL23, CJJLL26], while another binary-code improvement concerns
the regime d = n/2 − Θ( n), rather than ﬁxed relative distance [PMP23]. Constructions of
Delsarte dual certiﬁcates, limitations of particular spectral methods, and lower bounds on spher-
ical, Hamming, and constant-weight linear-programming optima provide additional context but
do not exclude the certiﬁcates constructed here [Sam01, Sam04, NS05, CD25, Sam25].




                                                                                                                     33
                                2. The first binary bound
  We ﬁrst improve the ﬁrst MRRW bound at every relative distance by working directly on
the Hamming cube. The construction uses Fourier levels, elementary Boolean addition and
deletion maps, and a symmetric tridiagonal matrix indexed by consecutive Fourier degrees. Its
new feature is that every degree carries a copy of the same higher-dimensional harmonic space.
In this section, the superscript □ identiﬁes whole-cube representation spaces and dimensions.
Later sections use J and S for the Johnson-layer and spherical constructions, respectively.
2.1. Fourier levels and Boolean harmonics. The classical ﬁrst MRRW bound comes from a
symmetric tridiagonal matrix whose indices are Fourier degrees and whose nonzero oﬀ-diagonal
entries connect consecutive degrees. To improve that bound, we attach a larger Boolean har-
monic space to every selected degree. Identify the binary alphabet with {±1}, and write
Xn = {±1}n . The normalized inner product records Hamming distance:
                              x                                  2dH (x, y)
                        ℓx = √ ,      t(x, y) = hℓx , ℓy i = 1 −            .
                               n                                     n
Give real-valued
         Q
                 functions on Xn the uniform-probability inner product. The Fourier characters
χS (x) = r∈S xr , indexed by S ⊆ [n], form an orthonormal basis; write eS = χS for its basis
vectors. Their degree-i subspace is
                                                                                         !
                                                                                        n
                     Vi□ = span{eS : |S| = i},                Di□ = dim Vi□ =             .
                                                                                        i
At a word x, the classical spectral construction [BN06, §3.1] uses the unit vector
                                                 !−1/2
                                             n                X
                                 vi,x =                           χS (x)eS .
                                             i            |S|=i

It is unchanged by every symmetry of the cube ﬁxing x. The inner products hvi,x , vi,y i are
normalized Krawtchouk polynomials [Del73, MRRW77], but their explicit formulas will not be
needed: we use the Fourier spaces and their coordinate transitions (19)–(20) instead. Multi-
plication by t(x, ·) connects only consecutive Fourier levels.
                                                         p     On the lines spanned by vi,x , its
oﬀ-diagonal coeﬃcient between degrees i and i + 1 is (i + 1)(n − i)/n. Thus the classical
construction is governed by the symmetric tridiagonal matrix with these neighboring-degree
entries.
   To replace each ﬁxed line by a larger subspace, introduce the Boolean addition and deletion
operators [Sri11, Fei12]:
                                    X                                 X
                           U eS =         eS∪{r} ,            DeS =          eS\{r} .
                                    r∈S
                                     /                                r∈S
                                                                                              L
These formulas deﬁne U and D on the Fourier basis and extend linearly to ni=0 Vi□ . Since
adding an element to S is equivalent to deleting the same element from the resulting set, their
matrix coeﬃcients satisfy
                                   hU eS , eT i = heS , DeT i.
               ∗
Consequently, U = D. Counting additions and deletions in the two possible orders also gives
                                (DU − U D)|V □ = (n − 2i)idV □ .                                  (14)
                                                     i                       i
                                                                  □ = 0, by
For 0 ≤ k ≤ n/2, deﬁne the degree-k Boolean harmonic space, with V−1
                                    Ek = ker(D : Vk□ → Vk−1
                                                         □
                                                            ).
Thus a coeﬃcient vector on the k-element subsets belongs to Ek when its coeﬃcients sum to
zero over all subsets containing any speciﬁed (k − 1)-element subset. In particular, E0 is the
constant line, and                    (                     )
                                           X
                                           n                  X
                                                              n
                                E1 =             ar e{r} :          ar = 0
                                           r=1                r=1




                                                         34
has dimension n − 1. More generally, for 1 ≤ k ≤ n/2, (14) implies
                                                                                  □
                       kU f k2 = kDf k2 + (n − 2k + 2)kf k2                (f ∈ Vk−1 ).
            □ → V □ is injective, and its adjoint D : V □ → V □ is surjective. Rank–nullity
Thus U : Vk−1    k                                     k      k−1
therefore gives                                   !        !
                                                n        n
                              d□
                               k = dim Ek =         −       ,
                                                k      k−1
        n 
where −1   = 0. For h ∈ Ek , induction using (14) yields the following identities, valid for
1 ≤ r ≤ n − 2k and 0 ≤ r ≤ n − 2k, respectively:
                                                                 (n − 2k)!
            DU r h = r(n − 2k − r + 1)U r−1 h,   kU r hk2 = r!               khk2 .     (15)
                                                               (n − 2k − r)!
The norm formula in (15) follows by repeatedly applying U ∗ = D. Consequently, for every
k ≤ i ≤ n − k, the normalized addition map
                                             U i−k h
                       φi h = p                                               (h ∈ Ek )              (16)
                                  (i − k)!(n − 2k)!/(n − i − k)!
has kφi hk = khk and therefore embeds Ek isometrically into Vi□ . If Rx eS = χS (x)eS , then
φi,x = Rx φi transports this copy from the all-ones word to x. For k = 0, its image is precisely
the classical ﬁxed line Rvi,x . For k > 0, every retained Fourier level instead carries a copy of the
same d□k -dimensional space; when k is proportional to n, that dimension grows exponentially.
   The coordinate transitions have an elementary explicit form. For neighboring levels, deﬁne
isometric addition and deletion maps by
                                  1    X
                 Ci,i+1 eT = √             er ⊗ eT \{r} ,               |T | = i + 1,            (17)
                                 i + 1 r∈T
                                  1    X
                 Ci+1,i eT = √             er ⊗ eT ∪{r} ,                          |T | = i.         (18)
                                 n − i r∈T
                                        /
                                                            □ → Rn ⊗ V □ , and C
Here er is the rth standard basis vector of Rn , Ci,i+1 : Vi+1                              □
                                                                         i        i+1,i : Vi →
        □
R ⊗ Vi+1 . Each map is an isometry: the displayed summands are distinct orthonormal basis
  n

tensors, and inputs to the two maps have i + 1 and n − i summands, respectively. At a common
output level Vi□ , the deletion map Ci,i+1 is supported on tensors er ⊗ eS with r ∈
                                                                                  / S, whereas
the addition map Ci,i−1 is supported on tensors with r ∈ S. Their supports are disjoint, so
their ranges are orthogonal. Set
                                      Qi = (i − k + 1)(n − i − k).
For f ∈ Vi□ and g ∈ Vi+1
                      □ , the deﬁning basis formulas give

                ∗                     Rx U f                 ∗                          Rx Dg
               Ci,i+1 (ℓx ⊗ Rx f ) = p          ,           Ci+1,i (ℓx ⊗ Rx g) = p               .
                                       n(i + 1)                                         n(n − i)
By (15) and (16), the normalized Boolean harmonic embeddings satisfy
                                      p                                  p
                           U φi h =       Qi φi+1 h,        Dφi+1 h =        Qi φi h.
Combining these identities gives
                                                            s
                                ∗                                  Qi
                               Ci,i+1 (ℓx ⊗ φi,x h) =                    φi+1,x h,                   (19)
                                                                n(i + 1)
                                                            s
                             ∗                                    Qi
                            Ci+1,i (ℓx ⊗ φi+1,x h) =                     φi,x h.                     (20)
                                                                n(n − i)
Thus the squared forward and reverse transition coeﬃcients are
                                      Qi                    Qi
                          pi,i+1 =          ,    pi+1,i =          .
                                   n(i + 1)               n(n − i)




                                                       35
For k = 0, all outgoing coeﬃcients at each Fourier degree sum to one on the full path. For
k > 0, they generally do not, because coordinate multiplication also reaches representations
outside the selected path. The coeﬃcients of the two orientations of a given edge are likewise
generally unequal, but they satisfy the dimension-weighted balance identity
                                                !                          !
                                               n                       n
                                                 pi,i+1 =                 pi+1,i .                                        (21)
                                               i                      i+1
This identity will convert the directed transitions into a real symmetric matrix, whose largest
eigenvalue controls the code bound.
2.2. The ﬁnite whole-cube bound. We now symmetrize the directed Fourier-degree transi-
tions and combine their largest eigenvector with the Boolean coordinate maps to construct
a scalar positive-deﬁnite kernel. This gives a bound for codes of ﬁxed ﬁnite length. Fix
0 ≤ k < L ≤ n − k, and select the Fourier levels Vk□ , . . . , VL□ . Their symmetric transition
matrix JH = JH (n, k, L) has zero diagonal and oﬀ-diagonal entries
                                                            (k)         (i − k + 1)(n − i − k)
                           (JH )i,i+1 = (JH )i+1,i = ci,H :=                p                  .                          (22)
                                                                           n (i + 1)(n − i)
Indeed, (21) says that the directed transition matrix is diagonally similar to a symmetric ma-
trix. The resulting symmetric edge weight is the geometric mean of the coeﬃcients in its two
directions:
                                √                      Qi
                                  pi,i+1 pi+1,i = p               .
                                                 n (i + 1)(n − i)
For k = 0, JH is the classical Krawtchouk matrix underlying the ﬁrst MRRW bound [MRRW77];
its tridiagonal spectral formulation appears in [BN06, §3.1]. For positive k, JH is still indexed
by consecutive Fourier degrees and connects only neighboring degrees, but every degree carries
a copy of the d□k -dimensional harmonic space. The resulting weighted path is shown in Figure 2.

                    (k)                                          (k)                                      (k)
                    ck,H                                     ci,H                                     cL−1,H

           Vk□                □
                            Vk+1        ···        Vi□                     □
                                                                         Vi+1        ···
                                                                                                 □
                                                                                               VL−1              VL□
          φk,x Ek          φk+1,x Ek              φi,x Ek              φi+1,x Ek              φL−1,x Ek         φL,x Ek

                                Every vertex carries the same harmonic space Ek .

        Figure 2. The whole-cube representation path at ﬁxed Boolean harmonic de-
        gree k. Each Fourier level contains the isometric copy φi,x Ek , and neighboring
                                           (k)
        levels have symmetric edge weight ci,H from (22). The classical path corresponds
        to the one-dimensional ﬁber E0 .

Theorem 2.1. Let n, d, k, L be integers with 1 ≤ d ≤ n and 0 ≤ k < L ≤ n−k. Set s = 1−2d/n
and λ = λmax (JH (n, k, L)). If λ > s, then
                                                                           !            !
                                                            1−s      XL
                                                                         n
                                       A2 (n, d) ≤         □
                                                                           .                                              (23)
                                                          dk (λ − s) i=k i
Proof. We ﬁrst construct a positive-deﬁnite projection kernel from the Boolean coordinate maps
and the Perron eigenvector of JH . Let I = {k, . . . , L} index the vertices of JH (n, k, L), and put
                                       M                                               X
                                 V=           Vi□ ,       Damb = dim V =                     Di□ .
                                       i∈I                                             i∈I
Since the oﬀ-diagonal entries in (22) are strictly positive, its largest eigenvalue λ = λmax (JH ) > 0
has a strictly positive unit eigenvector v = (vi )i∈I . Write
                                                  q                            X
                                        wi =          Di□ vi ,          Z=           wi .
                                                                               i∈I




                                                                 36
The dimension balance (21) and JH v = λv imply
                                   X
                                            pi,j wi = λwj               (j ∈ I).                          (24)
                                   i∈I
                                 |i−j|=1

For each j, dividing by λwj therefore turns the incoming weights into a probability distribution
on its retained neighbors. The square roots of these normalized weights are the coeﬃcients in
the coordinate isometry below.
  For each word x ∈ Xn , combine its copies of the Boolean harmonic space Ek into the isometric
embedding                                                 r
                                                      M wi
                           Ψx : Ek −→ V,       Ψx h =         φi,x h.
                                                      i∈I
                                                            Z
Let Px = Ψx Ψ∗x be the orthogonal projection onto its image. Thus every Px has rank d□
                                                                                     k , and
its scalar overlap with another projection is
                 K(x, y) = tr(Px Py ) = kPx Py k2HS ≥ 0,                        kAk2HS = tr(A∗ A).
As a Hilbert–Schmidt Gram kernel, K is positive deﬁnite. Coordinate permutations and sign
changes transport Px to the projection associated with the transformed word, so K(x, y) depends
only on dH (x,
           L
               y).
  For f = j∈I fj ∈ V, the concrete coordinate maps (17) and (18) deﬁne an operator between
the corresponding direct sums:
                                                                M
                               B : V −→ Rn ⊗ V =                      (Rn ⊗ Vi□ ),
                                                                i∈I
                                                            s
                                           M X                  pi,j wi
                                 Bf =                                   Ci,j fj .
                                            i∈I     j∈I
                                                                 λwj
                                                  |i−j|=1

For each i, the images of Ci,i−1 and Ci,i+1 in Rn ⊗ Vi□ are orthogonal: their respective basis
tensors er ⊗ eS satisfy r ∈ S and r ∈
                                    / S. Therefore (24) gives
                                           X kfj k2         X
                            kBf k2 =                                  pi,j wi = kf k2 .
                                           j∈I
                                               λwj       i∈I
                                                       |i−j|=1

Thus B is an isometry and B ∗ B = idV . For a harmonic vector h ∈ Ek , the explicit contractions
(19) and (20) likewise give
                                                                                        s
                                   M φj,x h             X                        M          λwj
                 B ∗ (ℓx ⊗ Ψx h) =  p                             pi,j wi =                     φj,x h.
                                     j∈I
                                             λwj Z       i∈I                      j∈I
                                                                                             Z
                                                       |i−j|=1

Consequently,                                      √
                                  B ∗ (ℓx ⊗ Ψx h) = λ Ψx h.                                               (25)
  To expose the positivity needed for the code bound, set
                                                                                             √
                   Lx = (ℓx ⊗ id)Px ,             Gx = BPx ,              Θx = Lx −              λ Gx .
These are maps from V to Rn ⊗ V. Their Hilbert–Schmidt pairings are
                   hLx , Ly iHS = tr [Px (ℓx ⊗ id)∗ (ℓy ⊗ id)Py ] = t(x, y)K(x, y),
                  hGx , Gy iHS = tr(Px B ∗ BPy ) = tr(Px Py ) = K(x, y).
Since im Px = im Ψx , (25) implies
                                                                  √
                                      B ∗ (ℓx ⊗ id)Px =                λ Px .                             (26)




                                                       37
Taking the adjoint of (26), and then applying the same identity at y, yields both mixed pairings:
                                                                 √
                        hLx , Gy iHS = tr [Px (ℓx ⊗ id)∗ BPy ] = λ K(x, y),
                                                                 √
                        hGx , Ly iHS = tr [Px B ∗ (ℓy ⊗ id)Py ] = λ K(x, y).
                  √              √
Expanding hLx − λ Gx , Ly − λ Gy iHS now gives
                                                                    
                                  hΘx , Θy iHS = t(x, y) − λ K(x, y).                        (27)
In particular, for every s < λ,
                                    
                       t(x, y) − s K(x, y) = (λ − s)K(x, y) + hΘx , Θy iHS .
Both summands are positive-deﬁnite Gram kernels, so (t − s)K is a scalar two-point Delsarte
certiﬁcate.
   Let C ⊆ Xn have minimum Hamming distance at least d, and put NC = |C|. The projection
kernel constructed above satisﬁes K(x, y) ≥ 0. Hence (t(x, y) − s)K(x, y) ≤ 0 for distinct
x, y ∈ C, whereas its diagonal value is (1 − s)d□                      2
                                                k . Summing (27) over C gives
                                                       2
                                            X
                                  (λ − s)         Px        ≤ NC (1 − s)d□
                                                                         k.
                                            x∈C
                                           HS
                         □            PL      
Since every Px has rank dk and Damb = i=k ni , trace Cauchy–Schwarz gives
                                         2
                                  X             N 2 (d□ )2
                                      Px    ≥ LC k ! .
                                  x∈C
                                                X n
                                         HS
                                                             i=k
                                                                    i
Combining these estimates proves (23).                                                         □
2.3. Asymptotic improvement over the ﬁrst MRRW bound. To compare the ﬁnite
bound with M1 , take both the harmonic degree and the largest retained Fourier degree pro-
portional to n. The largest eigenvalue of the explicitly deﬁned tridiagonal matrix JH (n, k, L)
determines whether the spectral condition λmax (JH (n, k, L)) > 1 − 2d/n in Theorem 2.1 holds,
while the dimension of Ek gives the exponential saving. Recall the binary entropy H2 , the
asymptotic rate R2 , the ﬁrst MRRW exponent M1 , and the whole-cube exponent κH from the
introduction. The spectral calculations use the Rayleigh–Ritz principle: for every real symmet-
ric matrix J,
                                                     ha, Jai
                                    λmax (J) = max           .                             (28)
                                                a6=0 ha, ai

Lemma 2.2. Suppose 0 ≤ b < a ≤ 1/2, and let kn < Ln ≤ bn/2c satisfy kn /n → b and
Ln /n → a. Then                                  
                        lim λmax JH (n, kn , Ln ) = ΓH (a, b).
                              n→∞

Proof. For a degree i with i/n → x > 0, the neighboring-degree entry of JH (n, kn , Ln ) satisﬁes
                (k )                 (x − b)(1 − x − b) q            b(1 − b)
               ci,Hn −→ gb (x) :=        p             = x(1 − x) − p          .
                                           x(1 − x)                   x(1 − x)
The ﬁnite entries are increasing through the selected degrees. Indeed, put Yi = (i + 1)(n − i)
and Tk = kn (n + 1 − kn ). Then
                                        (k )   Yi − Tk
                                      nci,Hn = √       .
                                                   Yi
                                          √
Both Yi and the function Y 7→ (Y − Tk )/ Y increase for kn ≤ i < Ln ≤ n/2. Consequently,
the largest row sum gives
                                                            (k )
                          λmax JH (n, kn , Ln ) ≤ 2cLnn−1,H −→ 2gb (a).




                                                       38
  Choose integers mn → ∞ with mn = o(n), and deﬁne a vector supported on the last mn
Fourier degrees by
                                              πr
                          fLn −mn +r = sin               (1 ≤ r ≤ mn ).
                                            mn + 1
Although the entries vary across the full Fourier-degree path, they converge uniformly to gb (a)
on these last mn = o(n) degrees. The restricted matrix therefore becomes a constant-weight
nearest-neighbor adjacency operator. Its ﬁrst discrete sine vector and (28) give
                                                            π
                       λmax JH (n, kn , Ln ) ≥ 2gb (a) cos        + o(1).
                                                           mn + 1
Taking n → ∞ and recalling ΓH (a, b) = 2gb (a) proves the claim.                              □
Theorem 2.3. For every ﬁxed 0 < δ < 1/2,
                                       R2 (δ) ≤ κH (δ) < M1 (δ).
Proof. Fix 0 ≤ b < a ≤ 1/2 with ΓH (a, b) > 1 − 2δ, as in (2), and take k = bbnc, L = banc,
and dn = dδne. The ﬁnite distance threshold is sn = 1 − 2dn /n → 1 − 2δ. By Lemma 2.2,
λmax (JH (n, k, L)) → ΓH (a, b). Stirling’s formula gives
                                !
                 1      XL
                            n                            1
                   log2             = H2 (a) + o(1),       log2 d□
                                                                 k = H2 (b) + o(1).
                 n      i=k
                            i                            n
Strict feasibility in (2) gives λmax (JH (n, k, L)) − sn > 0, bounded away from zero for large n, so
the prefactor in (23) stays bounded. Taking logarithmic rates and then the inﬁmum over (a, b)
gives R2 (δ) ≤ κH (δ).                                            p
   At the classical ﬁxed-line spectral boundary, put a0 = 12 − δ(1 − δ) and b = 0. Then
                             q
               ΓH (a0 , 0) = 2 a0 (1 − a0 ) = 1 − 2δ,      H2 (a0 ) − H2 (0) = M1 (δ).
At this boundary point,
                                                ∂b ΓH       2
                                 ∂a ΓH > 0,      −    =         .
                                                ∂a ΓH   1 − 2a0
Thus every c > 2/(1 − 2a0 ) gives strictly feasible parameter pairs a = a0 + cb for suﬃciently
small b > 0. The ambient entropy H2 (a) increases by Oδ (b), whereas H2 (b) = b log2 (1/b) + O(b).
The harmonic-space entropy therefore dominates the spectral cost as b ↓ 0, proving κH (δ) <
M1 (δ).                                                                                        □

                               3. The optimized binary bound
   The ﬁrst MRRW exponent is not always the smallest classical bound. To improve the op-
timized second MRRW exponent M2 , we adapt the whole-cube projection argument of Theo-
rem 2.1 to a constant-weight layer and then transfer the resulting estimate back to unrestricted
binary codes. Johnson degrees replace Fourier degrees, and two Boolean harmonic spaces, on
the support and its complement, replace the single whole-cube harmonic space.
3.1. Constant-weight layers and their harmonic spaces. To improve the constant-weight
part of the second MRRW bound, we ﬁrst reduce an unrestricted code to words with a common
                                                                        
weight. Identify such words with their supports, and write Xw = [n]   w for the weight-w layer.
Let AJ (n, w, d) be the largest size of a code in Xw with minimum Hamming distance at least
d. Averaging the intersection of an unrestricted binary code with all translates of the weight-w
layer gives the Bassalygo–Elias inequality [Bas65, MRRW77]:
                                                2n
                                    A2 (n, d) ≤ n  AJ (n, w, d).                           (29)
                                                  w
When w/n → α, its prefactor has exponential rate 1 − H2 (α). It therefore suﬃces to con-
struct a constant-weight bound that improves the classical Hahn-polynomial construction after
accounting for this reduction.




                                                  39
   A base word x ∈ Xw partitions the coordinates into x and xc , of sizes w and N = n − w,
respectively. Complementation preserves Hamming distance, so we assume 1 ≤ w < n/2; the
middle layer follows by taking w/n → 1/2.
   Coordinate permutations preserve the layer, and those ﬁxing x separately permute its support
and complement. The distance between two words in the layer is even: half their Hamming
distance is the number of coordinates removed from one support to obtain the other. For
x, y ∈ Xw , put
                                         1                            n r(x, y)
                  r(x, y) = w − |x ∩ y| = dH (x, y),    t(x, y) = 1 −           .          (30)
                                         2                              wN
                        p
The unit vectors ℓx = n/(wN )(1x − (w/n)1) satisfy hℓx , ℓy i = t(x, y).
   Give functions on Xw the uniform-probability inner product. The standard Johnson harmonic
decomposition, indexed by degrees 0 ≤ j ≤ w, is the constant-weight analogue of the Fourier
decomposition [Del73]:
                                                                       !               !
                                   M
                                   w
                                                                      n    n
                      R   Xw
                               =         VjJ ,   DjJ = dim VjJ =        −     .               (31)
                                   j=0
                                                                      j   j−1

As a representation of the coordinate permutation group Sn , the space VjJ is the Specht module
indexed by the two-row partition (n−j, j) [Del73, Sri11]. In particular, these spaces are pairwise
inequivalent and irreducible. In the classical construction, the permutations ﬁxing x ﬁx a single
line in VjJ , whose overlap kernel is a Hahn polynomial in r(x, y). Neither its explicit polynomial
formula nor the adjacency eigenvalues will be needed: the argument uses the Johnson harmonic
spaces and the associated Hahn recurrence coeﬃcients (37). We replace the ﬁxed line by a
product of Boolean harmonic spaces, one on the support and one on its complement, extending
                                                                           (A)
the degree-k Boolean harmonics of §2.1. For a ﬁnite set A, identify R p with real functions
                                                                                   (A)       (A)
on its p-element subsets. For 0 ≤ p ≤ |A|/2, let Ep (A) = ker ∂, where ∂ : R p → R p−1 is
                                         P                           A
the Boolean lowering map (∂f )(T ) =             f (T ∪ {a}), with R(−1) = 0. Thus f is harmonic
                                                 a∈A\T
precisely when its values sum to zero over the p-subsets extending each (p − 1)-subset. Its
harmonic dimension is
                                                      !         !
                                                   |A|      |A|
                          dp (|A|) := dim Ep (A) =      −        .                     (32)
                                                    p      p−1
For 0 ≤ p ≤ w/2 and 0 ≤ q ≤ N/2, deﬁne the attached harmonic space and its dimension by
                           Exp,q = Ep (x) ⊗ Eq (xc ),         dJp,q = dp (w)dq (N ).
Thus p and q are harmonic degrees on the support and its complement, not dimensions. These
Boolean harmonic spaces are the Specht modules indexed by (w − p, p) and (N − q, q), respec-
tively [Sri11]. The two-row Littlewood–Richardson restriction rule for Sn ↓ Sw × SN determines
exactly which Johnson degrees contain their tensor product Exp,q , and shows that each such
degree contains it with multiplicity one [GW09, §9.3.5].
Lemma 3.1. Let n, w, p, q be integers with 1 ≤ w < n/2, 0 ≤ p ≤ w/2, and 0 ≤ q ≤ (n − w)/2.
Put N = n − w, and ﬁx x ∈ Xw . The Johnson space VjJ contains a copy of Exp,q preserved by
the permutations ﬁxing x precisely when
                     j− = p + q ≤ j ≤ j+ := min{w, w − p + q, N + p − q}.                     (33)
This copy occurs once, and its isometric embedding φj,x : Exp,q → VjJ , commuting with those
permutations, is unique up to sign.
3.2. The associated Hahn tridiagonal matrix. To adapt the projection argument of The-
orem 2.1 to the layer Xw , we need the coordinate transitions between the copies of Exp,q in
successive Johnson degrees. These transitions are governed by an associated Hahn recurrence.




                                                         40
For ﬁxed x, let Mx denote multiplication by y 7→ t(x, y). Its action on the Johnson harmonic
spaces satisﬁes the degree-one product rule [BCV23, (90)]:
                                     Mx VjJ ⊆ Vj−1
                                                J
                                                   ⊕ VjJ ⊕ Vj+1
                                                             J
                                                                .                                 (34)
Because Mx commutes with all permutations ﬁxing x, Lemma 3.1 reduces its action on the
copies of Exp,q to a scalar three-term recurrence. Its coeﬃcients are conveniently expressed using
six standard Hahn-recurrence parameters:
         w               N             n                 n
   ȷ1 = − p, ȷ2 =           − q, ȷ = − j, m0 = − w, Σ = ȷ1 + ȷ2 , ∆J = ȷ2 − ȷ1 . (35)
          2               2            2                 2
Here ȷ1 , ȷ2 depend on the two Boolean harmonic degrees, ȷ depends on the Johnson degree, and
m0 depends only on the layer weight. Write
                                    m0 ȷ2 (ȷ2 + 1) − ȷ1 (ȷ1 + 1)
                             µp,q
                              j =                                ,
                                     2         ȷ(ȷ + 1)
                                     q
                                         (ȷ2 − m20 )(ȷ2 − ∆2J )((Σ + 1)2 − ȷ2 )
                           νjp,q =                p                               .               (36)
                                               2ȷ (2ȷ − 1)(2ȷ + 1)
Only j− ≤ j < j+ require νjp,q . Deﬁne the diagonal and oﬀ-diagonal recurrence coeﬃcients by

                                p,q nµp,q
                                      j − m0
                                           2
                                                              p,q nνjp,q
                               bj =          ,               cj =        .                         (37)
                                               wN                   wN
   The numbers bp,q            p,q
                     j and cj are the associated Hahn recurrence coeﬃcients [BCV23, (91)–(92)],
with (j1 , j2 , j, m) = (ȷ2 , ȷ1 , ȷ, m0 ) and with the operator normalized to act by multiplication
by t(x, ·). Their identiﬁcation with Hahn polynomials is classical [Koo81, §4]. Setting p =
q = 0 recovers the ordinary Hahn recurrence on the stabilizer-ﬁxed lines, while positive p or q
introduces a higher-dimensional harmonic space.
   We now ﬁx the embeddings in Lemma 3.1 unambiguously. Suppose j− ≤ j+ ; otherwise
no Johnson harmonic space contains Exp,q . Choose a reference support x0 and an isometric
stabilizer-equivariant embedding φj− ,x0 : Exp,q    0
                                                      → VjJ− . Write ΠJj for orthogonal projection onto
VjJ . For each successive degree, choose the sign of its isometric embedding so that, for every
Y ∈ Exp,q ,
        0                                      
                        ΠJj+1 t(x0 , ·)φj,x0 Y = cp,qj φj+1,x0 Y,    j− ≤ j < j + .                (38)
The associated Hahn coeﬃcients cp,q j are positive throughout this range, so this condition deter-
mines each successive sign. For every support x = gx0 , transport all the resulting embeddings
by φj,x = gφj,x0 g −1 . This deﬁnition is independent of the permutation g: two choices diﬀer by
a permutation ﬁxing x0 , and every φj,x0 intertwines their actions.
Proposition 3.2. Let n, w, p, q be integers with 1 ≤ w < n/2, 0 ≤ p ≤ w/2, and 0 ≤ q ≤
(n − w)/2. Put N = n − w, and set j− = p + q and j+ = min{w, w − p + q, N + p − q}. Suppose
j− ≤ j+ . For every x ∈ Xw , Y ∈ Exp,q , and j− ≤ j ≤ j+ , the embeddings ﬁxed in (38) satisfy
                      t(x, ·)φj,x Y = cp,q             p,q         p,q
                                       j−1 φj−1,x Y + bj φj,x Y + cj φj+1,x Y,                    (39)
where the degree-(j − 1) term is omitted when j = j− , and the degree-(j + 1) term is omitted
when j = j+ . Every retained oﬀ-diagonal coeﬃcient satisﬁes cp,q
                                                             j > 0 for j− ≤ j < j+ .

Proof. Let Hx = Sx × Sxc ≤ Sn be the stabilizer of the support x; its two factors permute
x and xc , respectively. Multiplication by t(x, ·) and each projection ΠJi commute with Hx .
Consequently,
                                      ΠJi Mx φj,x : Exp,q −→ ViJ
is Hx -equivariant. By Lemma 3.1, its image is zero unless j− ≤ i ≤ j+ , and otherwise it lies
in the unique copy φi,x Exp,q . The Johnson product rule (34) further restricts i to j − 1, j, j + 1.
Since Exp,q is the outer tensor product of two absolutely irreducible real Specht modules, every
Hx -equivariant endomorphism of Exp,q is a real scalar. Therefore each surviving component is a
scalar multiple of φi,x .



                                                      41
   The associated Hahn recurrence and coeﬃcient formulas [BCV23, (90)–(92)], with the param-
eters and coordinate normalization in (35)–(37), give the diagonal scalar bp,q
                                                                           j and the absolute
       p,q
value cj of the degree-(j + 1) scalar. For j− ≤ j < j+ ,
                                       0 < max{m0 , |∆J |} < ȷ ≤ Σ.
Indeed, j ≥ j− = p + q gives ȷ ≤ Σ, while
                                     n
                                       − j+ = max{m0 , |∆J |}
                                     2
and j < j+ give the strict lower inequality. Therefore all three radicand factors in (36) are
positive, as is its denominator, proving cp,q
                                           j > 0. The orientation (38) ﬁxes the degree-(j + 1)
component at x0 . Since t(gx0 , gy) = t(x0 , y), transporting the embeddings gives cp,q
                                                                                    j φj+1,x for
every x.
  If j > j− , self-adjointness of Mx and the isometry of the embeddings give, for Y, Z ∈ Exp,q ,
                     φj−1,x Z, Mx φj,x Y = Mx φj−1,x Z, φj,x Y = cp,q
                                                                  j−1 hZ, Y i.
Thus the degree-(j − 1) component is cp,q
                                        j−1 φj−1,x Y , proving (39). At the lower endpoint, the
formal preceding index j− − 1 gives ȷ = Σ + 1, making (Σ + 1)2 − ȷ2 = 0. At the upper endpoint,
ȷ = max{m0 , |∆J |}; hence ȷ2 − m20 = 0 if j+ = w, and ȷ2 − ∆2J = 0 if j+ = w − p + q or
j+ = N + p − q. These are precisely the missing transitions beyond the branching range. When
j− = j+ , both oﬀ-diagonal terms are absent.                                                 □
   Write b0j = bj0,0 and c0j = cj0,0 for the classical ﬁxed-line coeﬃcients. The ﬁxed-line diagonal
satisﬁes b00 = 0 and, for 1 ≤ j ≤ w,
                                                 m20 j(n − j + 1)
                                         b0j =                    > 0,
                                                  wN ȷ(ȷ + 1)
and c0j > 0 for 0 ≤ j < w.
   The associated Hahn coeﬃcients describe multiplication by the scalar distance coordinate
t(x, ·). The projection construction instead requires isometric maps between Johnson spaces
and their tensor products with the coordinate space W = 1⊥ ⊆ Rn . Their normalization is
determined by the ﬁxed-line case of (39).
   For Johnson degrees i, j in (33) with |i − j| ≤ 1, set
                        ( p,q                                            (
                p,q      bi ,        i = j,                    0           b0i ,       i = j,
               ri,j =     p,q                                 ri,j =
                         cmin{i,j} , |i − j| = 1,                          cmin{i,j} , |i − j| = 1.
                                                                             0

       p,q
Thus ri,j  is the scalar coeﬃcient connecting the copies of Exp,q in ViJ and VjJ , whereas ri,j
                                                                                            0 is

the corresponding coeﬃcient for the classical ﬁxed lines. Except when i = j = 0, the ﬁxed-line
coeﬃcient is strictly positive.
Lemma 3.3. Let i, j be Johnson degrees in (33) with |i − j| ≤ 1 and (i, j) 6= (0, 0). There is
an Sn -equivariant isometry
                                     Ci,j : VjJ −→ W ⊗ ViJ
whose contraction onto the selected harmonic spaces is
                                                                                          v
                                                                                 p,q 2 u Ju
                     ∗                         √                               (ri,j ) t Dj
                    Ci,j (ℓx ⊗ φi,x Y ) =          pi,j φj,x Y,         pi,j =    0          ,        (40)
                                                                                 ri,j    DiJ
for every x ∈ Xw and Y ∈ Exp,q . Consequently,
                                                                                p,q 2
                                                              √               (ri,j )
                                DiJ pi,j = DjJ pj,i ,             pi,j pj,i =    0    .               (41)
                                                                                ri,j




                                                         42
Proof. Write σ for uniform probability measure on Xw , and let Ki and Kj be the reproducing
kernels of ViJ and VjJ . Permutations act transitively on Xw , so these kernels have constant
diagonal values Ki (x, x) = DiJ and Kj (x, x) = DjJ . Hence
                                      Ki (x, ·)                       Kj (x, ·)
                                zi,x = q        ,               zj,x = q
                                          DiJ                             DjJ
are the unit stabilizer-ﬁxed vectors positive at x. Their ordinary Hahn recurrence, the p = q = 0
case of (39), says that                             
                                     ΠJj t(x, ·)zi,x = ri,j
                                                        0
                                                            zj,x .                           (42)
  Deﬁne the coordinate-multiplication map by
                                                                                          
                    Mi,j : W ⊗ ViJ −→ VjJ ,                 Mi,j (v ⊗ f ) = ΠJj hv, ℓ· if .
It commutes with coordinate permutations, so the positive operator Mi,j M∗i,j on the irreducible
Johnson space VjJ is a scalar multiple of the identity. To identify that scalar, expand the
Hilbert–Schmidt norm in orthonormal bases. The coordinate identity following (30), together
with permutation invariance and the ﬁxed-line recurrence (42), gives
                                     ZZ
                      kMi,j k2HS =             t(y, z)Ki (y, z)Kj (y, z) dσ(y) dσ(z)
                                           2
                                          Xw
                                     Z
                                 =          t(x, y)Ki (x, y)Kj (x, y) dσ(y)
                                       Xw
                                          q
                                    0
                                 = ri,j        DiJ DjJ .
Taking the trace on the DjJ -dimensional output space now yields
                                                                             v
                                                                             u J
                                                                             u
                                                                           0 t Di
                           Mi,j M∗i,j = mi,j idV J ,              mi,j = r i,j    .
                                                       j                          DjJ
                     p,q
  Let εi,j = 1 when ri,j ≥ 0 and εi,j = −1 otherwise. Then
                                               εi,j
                                       Ci,j = √     M∗
                                                mi,j i,j
is an equivariant isometry. By (39), its contraction on Exp,q is
                                                        p,q
                                 ∗
                                                      |ri,j |
                               Ci,j (ℓx ⊗ φi,x Y ) = √        φj,x Y.
                                                        mi,j
                                            p,q     p,q        0 = r 0 , applying the same formula
Squaring this coeﬃcient gives (40). Since ri,j  = rj,i  and ri,j      j,i
in the reverse direction proves (41).                                                                □
   By Lemma 3.3, the symmetric matrix entry associated with a Johnson transition is the square
of its associated Hahn coeﬃcient divided by the corresponding ordinary Hahn coeﬃcient. For
j− < L ≤ j+ , retain the consecutive Johnson degrees j− , . . . , L. Their coordinate-transition ma-
trix is tridiagonal: its oﬀ-diagonal entries connect neighboring Johnson degrees, and a diagonal
entry is allowed at each degree. Write Jb = J(n,
                                               b w, p, q, L) for the symmetric matrix
                                                       (
                                                           (bp,q
                                                              j ) /bj , j ≥ 1,
                                                                 2 0
                                 Jbj,j = bbp,q :=
                                               j                                                   (43)
                                                           0,           j = 0,
                                                                    (cp,q
                                                                      j )
                                                                          2
                               Jbj,j+1 = Jbj+1,j = cbp,q := j               .                      (44)
                                                                      c0j
With the Johnson dimensions DjJ from (31), the squared directed contraction coeﬃcients in
Lemma 3.3 are
                                v                                 v
                                u J                               u
                                u
                            p,q t Dj+1
                                                                  u
                                                              p,q t Dj
                                                                      J
                 pj,j+1 = cbj       J
                                       ,           pj+1,j = cbj     J
                                                                        ,           pj,j = bbp,q
                                                                                             j .
                                  Dj                                   Dj+1


                                                           43
For p = q = 0, the diagonal and oﬀ-diagonal coeﬃcients sum to one over the complete Johnson-
degree path. For higher harmonic types, or after truncating that path, the retained coeﬃcients
need not have this normalization. Consequently, the Johnson dimensions satisfy
                                        DjJ pj,j+1 = Dj+1
                                                      J
                                                          pj+1,j .                                          (45)
The geometric means of the forward and reverse coeﬃcients are exactly the oﬀ-diagonal entries
   b Since j− < L, the Johnson matrix Jb has a positive largest eigenvalue λ = λmax (J),
of J.                                                                                  b so
λ > s implies λ > max{s, 0}.
Theorem 3.4. Let n, w, p, q, L, d be integers with 1 ≤ w < n/2, 0 ≤ p ≤ w/2, 0 ≤ q ≤ (n−w)/2,
and
                         p + q < L ≤ min{w, w − p + q, n − w + p − q}.
Suppose d is even and 2 ≤ d ≤ 2w. Put
                                            nd                               
                 N = n − w,        s=1−         ,               b w, p, q, L) ,
                                                      λ = λmax J(n,
                                           2wN
where Jb is given by (43)–(44). If λ > s, then
                                                                      !                    !!
                                                         X
                                                         L
                                                                      n    n
                                                                        −
                                    1−s                 j=p+q
                                                                      j   j−1
                 AJ (n, w, d) ≤                     !                 !!               !             !! .   (46)
                                    λ−s           w    w                         N            N
                                                    −                                      −
                                                  p   p−1                        q           q−1
Proof. Let I = {p + q, . . . , L}, let v = (vj )j∈I be the positive unit Perron eigenvector of the
Johnson matrix Jb in (43)–(44), and put
                                              q                           X
                                     ωj =         DjJ vj ,        Z=            ωj .
                                                                          j∈I

The Johnson dimension balance (45) gives
                                               X
                                                        pi,j ωi = λωj .                                     (47)
                                                i∈I
                                              |i−j|≤1

As in the whole-cube identity (24), dividing by λωj normalizes the incoming transition weights
to sum to one. Combine the copies of Exp,q in the selected Johnson spaces by setting
                                               r
                                        M          ωj
                              Ψx Y =                  φj,x Y,          Px = Ψx Ψ∗x .
                                        j∈I
                                                   Z
                                                                                L
These projections have rank dJp,q on the ambient space V = j∈I VjJ .
   Write W = 1⊥ ⊆ Rn , and let Ci,j : VjJ → W ⊗ ViJ be the normalized Johnson coordinate
isometries constructed in Lemma 3.3 for (i, j) 6= (0, 0); set C0,0 = 0, consistently with p0,0 = 0.
For ﬁxed i, the nonzero images for distinct j are orthogonal: they are invariant irreducible
subspaces of W ⊗ ViJ carrying pairwise inequivalent permutation representations VjJ . Their
                                    √
contraction coeﬃcients on Exp,q are pi,j , by Lemma 3.3. Deﬁne B : V → W ⊗ V by
                                              s
                              M X                 pi,j ωi                          M
                       Bf =                               Ci,j fj ,        f=              fj ∈ V.
                              i∈I     j∈I
                                                   λωj                               j∈I
                                    |i−j|≤1
                                                                              ∗
Orthogonality
√                                             √ that B is an isometry and B (ℓx ⊗ Ψx Y ) =
               and the Perron identity (47) show
  λ Ψx Y . Consequently, if Θx = (ℓx ⊗ id)Px − λ BPx , direct expansion gives
                                                                      
                               hΘx , Θy iHS = t(x, y) − λ tr(Px Py ).




                                                             44
For a constant-weight code C of size NC , the oﬀ-diagonal terms of (t(x, y) − s) tr(Px Py ) are
nonpositive, and the diagonal terms equal (1 − s)dJp,q . Summation and trace Cauchy–Schwarz
therefore give
                                    N 2 (dJp,q )2
                            (λ − s) PLC          J
                                                   ≤ NC (1 − s)dJp,q .
                                      j=p+q j D
                                   
Substituting DjJ = nj − j−1  n
                                 and dJp,q = dp (w)dq (N ) proves (46). The overlap is a scalar
function of Johnson distance because coordinate permutations are transitive on pairs of supports
having the same intersection size.                                                            □
3.3. The asymptotic constant-weight bound. The ﬁnite constant-weight certiﬁcate in The-
orem 3.4 bounds a code by the ratio between the total dimensions of the retained Johnson spaces
and the dimension of the attached Boolean harmonic space. We now pass to high-dimensional
limits, estimate its largest eigenvalue, and include the Bassalygo–Elias cost of returning to the
whole cube.
   Fix 0 < δ < 1/2, and recall the normalized parameters α = w/n, β = p/n, γ = q/n, and
u = L/n from the introduction. They represent the relative layer weight, the two normalized
Boolean harmonic degrees, and the largest retained Johnson degree, respectively. Their ranges
are (4)–(5), and (6) gives an asymptotic lower bound for the largest eigenvalue of the Johnson
recurrence matrix J. b

Lemma 3.5. Suppose (α, β, γ, u) satisﬁes (4) and (5), and choose integers with
                        w            p          q           L
                           → α,        → β,        → γ,        → u.
                        n           n           n            n
                                   b w, p, q, L), one has
For the Johnson tridiagonal matrix J(n,
                                                                  
                                             b w, p, q, L) ≥ Λα,β,γ (u).
                                lim inf λmax J(n,                                                       (48)
                                 n→∞

Proof. Let z, m, ζ, ξ be the normalized coordinates preceding (6). Uniformly for |j/n − u| → 0,
substitution in (37) gives
                    m(ζξ − mz 2 )                                               m2 (1 − z 2 )
          bp,q
           j −→                    ,                                     b0j −→                ,
                     z 2 (1 − m2 )                                              z 2 (1 − m2 )
                    p                                                                         √
                        (z 2 − m2 )(z 2 − ξ 2 )(ζ 2 − z 2 )                     (z 2 − m2 ) 1 − z 2
          cp,q
           j −→                                             ,            c0j −→                     .
                               2z 2 (1 − m2 )                                        2z 2 (1 − m2 )
The strict inequalities in (4) and (5) keep all denominators bounded away from zero and place
the terminal degree strictly inside the Johnson-degree range (33), so j− < L < j+ for large n.
Choose mn → ∞ with mn = o(n). Then L − mn ≥ j− and L < j+ for large n, so the discrete
sine vector
                                               πr
                             fL−mn +r = sin            (1 ≤ r ≤ mn )
                                            mn + 1
is supported on Johnson degrees j− ≤ j ≤ j+ .
   By (43) and (44), the diagonal entries on this terminal degree interval converge uniformly to
                                             (ζξ − mz 2 )2
                                          B=                    ,
                                        z 2 (1 − m2 )(1 − z 2 )
while the neighboring-degree entries converge uniformly to
                                                 (z 2 − ξ 2 )(ζ 2 − z 2 )
                                         C=                     √         .
                                                2z 2 (1 − m2 ) 1 − z 2
The Rayleigh–Ritz principle (28) applied to the displayed sine vector gives
                                   b ≥ B + 2C cos     π
                             λmax (J)                      + o(1).
                                                   mn + 1
Since B + 2C = Λα,β,γ (u), taking n → ∞ proves (48).                                                      □




                                                         45
Theorem 3.6. Fix 0 < δ < 1/2. If (α, β, γ, u) ∈ Dδ , then
                                                                       
                                                   β                   γ
            R2 (δ) ≤ 1 − H2 (α) + H2 (u) − αH2          − (1 − α)H2         .              (49)
                                                   α                  1−α
Proof. Choose integers with w/n → α, p/n → β, q/n → γ, and L/n → u, and put dn =
2bdδne/2c. This is the largest even integer not exceeding dδne, so dn /n → δ and A2 (n, dδne) ≤
A2 (n, dn ). Since α > δ/2 > 0, the ﬁnite-theorem hypotheses 2 ≤ dn ≤ 2w hold for all suﬃciently
large n. By Lemma 3.5, the largest eigenvalue of J(n,  b w, p, q, L) has limiting lower bound
Λα,β,γ (u). The dimensions of the retained Johnson spaces telescope to
                          !          !!        !              !
                 X
                 L
                         n    n                n     n
                           −               =     −                = 2nH2 (u)+o(n) .
                j=p+q
                         j   j−1               L   p+q−1
Stirling’s formula and (32) likewise give
                                                            
                      1                   β                 γ
                        log2 dJp,q = αH2     + (1 − α)H2         + o(1).
                      n                   α                1−α
The ﬁnite threshold 1 − ndn /(2w(n − w)) converges to the right-hand side of (7). Thus strict
feasibility and (48) bound the prefactor in (46). Taking the logarithmic rate of this ﬁnite
Johnson bound and adding the Bassalygo–Elias cost 1 − H2 (α) from (29) proves (49).        □
  Taking the inﬁmum in (49) over Dδ recovers the constant-weight exponent (8) and gives
                                       R2 (δ) ≤ κCW (δ).
3.4. Strict comparison with the classical bound. We now show that the two binary con-
structions together strictly improve the fully optimized classical bound at every relative dis-
tance. Recall the MRRW objective Fδ , its endpoint values M1 (δ) and Fδ (0), and its opti-
mized value M2 (δ) from (1)–(3). In particular, M2 (δ) ≤ M1 (δ). We ﬁrst identify the classical
constant-weight objective inside our construction by taking the one-dimensional ﬁxed-line choice
p = q = 0. A higher-dimensional choice then improves every interior minimizer, while the whole-
cube certiﬁcate handles the endpoint with value M1 .
   We ﬁrst identify the ﬁxed-line specialization β = γ = 0 with the fully optimized classical
objective (3). Write A = α(1 − α) and U = u(1 − u). Then
                                                     A−U
                                  1 − Λα,0,0 (u) =        √ .                               (50)
                                                   A(1 + 2 U )
                                 √
On the spectral boundary, τ = 2 U gives
         4A = τ 2 + 2δτ + 2δ,     1 − H2 (α) + H2 (u) = 1 + g(τ 2 ) − g(τ 2 + 2δτ + 2δ).
                       √                         √
Equivalently, u = (1 − 1 − τ 2 )/2 and α = (1 − 1 − τ 2 − 2δτ − 2δ)/2. Hence 0 < τ < 1 − 2δ
corresponds exactly to 0 < u < α < 1/2; moreover, α > δ/2, so the shell-domain conditions
hold. Every boundary point is approached by strictly feasible u0 > u, while τ = 0 and τ = 1−2δ
are obtained as u ↓ 0 and α ↑ 1/2, respectively. Consequently,
                                       κCW (δ) ≤ M2 (δ).
Proposition 3.7. Fix 0 < δ < 1/2, and suppose 0 < u < α < 1/2 and
                                                    δ
                               Λα,0,0 (u) = 1 −           .
                                                2α(1 − α)
Then there exist β, γ > 0 and u0 with (α, β, γ, u0 ) ∈ Dδ whose rate in (49) is strictly smaller
than 1 − H2 (α) + H2 (u).
Proof. Put β = γ = ε. By (50),
                                       "                                   #
                                              1          A−U
                ∂u Λα,0,0 (u) = (1 − 2u)        √   + √        √     > 0.
                                         A(1 + 2 U ) A U (1 + 2 U )2




                                               46
Here A = α(1 − α) and U = u(1 − u). Smoothness at the interior point shows that replacing
(β, γ) = (0, 0) by (ε, ε) changes the spectral value by O(ε). Thus, for a suﬃciently large
ﬁxed C, the choice uε = u + Cε satisﬁes (4)–(7) strictly. The ambient entropy increases by
H2 (uε ) − H2 (u) = O(ε), whereas the two harmonic-space dimensions contribute
                                                
                            ε                   ε             1
                      αH2       + (1 − α)H2          = 2ε log2 + O(ε).
                            α                 1−α             ε
This gain dominates O(ε), proving the strict improvement.                               □
Theorem 3.8. For every ﬁxed 0 < δ < 1/2,
                            κbin (δ) = min{κH (δ), κCW (δ)} < M2 (δ).
Proof. Suppose ﬁrst that M2 (δ) < M1 (δ). The endpoint τ = 1 − 2δ cannot minimize Fδ , since
its value is M1 (δ). At the other endpoint τ = 0, g(τ 2 ) = O(τ 2 log(1/τ )) = o(τ ), so Fδ0 (0+) =
−2δg 0 (2δ) < 0. Hence every minimizer is interior, and Proposition 3.7 gives κCW (δ) < M2 (δ). If
M2 (δ) = M1 (δ), Theorem 2.3 instead gives κH (δ) < M2 (δ). In either case, κbin (δ) < M2 (δ). □

                     4. Representation graphs for spherical codes
   The whole-cube construction in §2 uses the tridiagonal matrix JH in (22), indexed by Fourier
degree. The constant-weight construction in §3 uses a tridiagonal matrix indexed by Johnson
degree, with oﬀ-diagonal entries (44). In each case, coordinate multiplication connects neigh-
boring degrees. The simplest spherical construction similarly uses a tridiagonal matrix indexed
by harmonic degree, coming from the Gegenbauer recurrence (67). Stronger spherical construc-
tions, however, require ambient spaces indexed by several integers, with coordinate transitions
in several independent directions.
   This section extends the elementary projection argument to an arbitrary ﬁnite connected
weighted graph. The vertices represent rotation-invariant ambient spaces containing a common
moving subspace, and the edges record the action of the distance coordinate. The concrete
spherical ambient and stabilizer spaces are introduced in §5; their explicit coordinate-transition
weights are computed in §6.
4.1. The general projection bound. We ﬁrst isolate the projection argument that underlies
both the concrete whole-cube calculation and the more general spherical construction. The
only inputs are moving orthogonal projections and an isometry compatible with the distance
coordinate.
Proposition 4.1. Let X be a set, and associate a unit vector ℓx in a Euclidean space W with
every x ∈ X. Write t(x, y) = hℓx , ℓy i, let V be a D-dimensional Hilbert space, and let Px be a
rank-d orthogonal projection on V for every x ∈ X, where 1 ≤ d ≤ D. Suppose an isometry
B : V → W ⊗ V satisﬁes, for some Λ ≥ 0, every x ∈ X, and every u ∈ im Px ,
                                                      √
                                        B ∗ (ℓx ⊗ u) = Λ u.                                 (51)
If Λ > s, every code C ⊆ X satisfying t(x, y) ≤ s at distinct code points obeys
                                                1−s D
                                         |C| ≤          .                            (52)
                                                Λ−s d
Proof. It suﬃces to consider ﬁnite codes: an inﬁnite code would contain ﬁnite subcodes of
arbitrarily large cardinality. The projection overlap satisﬁes
                              K(x, y) = tr(Px Py ) = kPx Py k2HS ≥ 0.
Deﬁne the residual map                              √
                               Θx = (ℓx ⊗ id)Px − Λ BPx .
The same Hilbert–Schmidt calculation as in (27), using B ∗ B = idV and (51), gives
                               hΘx , Θy iHS = (t(x, y) − Λ)K(x, y),
                      (t(x, y) − s)K(x, y) = (Λ − s)K(x, y) + hΘx , Θy iHS .                  (53)



                                                47
The left side is nonpositive at distinct code points and equals (1−s)d on the diagonal. Summing
over C 2 , discarding the nonnegative Gram term, and applying trace Cauchy–Schwarz give
                                                           2
                              |C|2 d2           X
                      (Λ − s)         ≤ (Λ − s)     Px          ≤ |C|(1 − s)d.
                                D               x∈C        HS
Rearrangement proves (52).                                                                      □
   We now apply Proposition 4.1 to moving subspaces on the sphere. The rotation group and
the subgroup ﬁxing a base point determine which subspaces can be assembled into a projection.
   Let n ≥ 3, let X = Sn−1 , and let G = SO(n) be its rotation group. Give W = Rn the usual
rotation action. For x ∈ X, the unit distance-coordinate vector is ℓx = x, so t(x, y) = hx, yi.
Fix a base point o, and write H for the rotations ﬁxing o. The action of H on o⊥ identiﬁes H
with SO(n − 1).
   We call an H-representation a stabilizer representation because H = StabSO(n) (o) is the
subgroup ﬁxing the base point o. All representations below are ﬁnite-dimensional real Hilbert
spaces with orthogonal group actions. For example, H acts trivially on the ﬁxed line Ro, acts by
ordinary rotations on o⊥ , and acts on the degree-k harmonic polynomials Hk (o⊥ ) by rotating
their input vectors. These examples have dimensions 1, n − 1, and dim Hk (o⊥ ), respectively.
   Choose a d-dimensional irreducible stabilizer representation E, and let Ω be a ﬁnite collection
of pairwise inequivalent irreducible ambient G-representations Vλ . We require the restriction of
each Vλ to H to contain exactly one copy of E:
                           dimR HomH (E, Vλ ) = 1,        Dλ = dim Vλ .
The one-dimensional intertwiner space determines a unique copy of E in each Vλ . Identify E with
its copy in one ﬁxed ambient representation, and choose isometric embeddings φλ,o : E → Vλ at
the base point. Composing any H-equivariant endomorphism of E with φλ,o produces another
intertwiner. Hence the one-dimensional intertwiner hypothesis also gives EndH (E) = RidE . If
x = go, transport the stabilizer space and all its embeddings simultaneously:
                        Ex = gE,       φλ,x (gY ) = gφλ,o Y        (Y ∈ E).
These deﬁnitions are independent of the rotation carrying o to x: two such rotations diﬀer by
an element of H, and every φλ,o commutes with H. In particular, a single rotation transports
all embeddings, so their relative signs are preserved.
4.2. Coordinate transitions and their balanced graph. We next deﬁne the spherical tran-
sition graph and its weights. The vertices are the ambient spaces Vλ . If Vν occurs inside W ⊗ Vλ ,
its inclusion gives a possible coordinate transition from λ to ν. Choose an isometric map com-
muting with rotations:
                                      Cλ,ν : Vν −→ W ⊗ Vλ .
For ﬁxed λ, the images associated with distinct ν are orthogonal because they are inequivalent
irreducible subrepresentations of W ⊗Vλ . Contracting with the coordinate vector ℓx gives a map
between the two copies of Ex . Since these copies occur with multiplicity one, EndH (E) = RidE ,
and the map commutes with the rotations ﬁxing x, it acts by a real scalar cλ,ν :
                                  ∗
                                 Cλ,ν (ℓx ⊗ φλ,x Y ) = cλ,ν φν,x Y.                           (54)
Choose the sign of each coordinate map so that cλ,ν ≥ 0, and write pλ,ν = c2λ,ν . The graph
retains an edge only when this coeﬃcient is nonzero. Set pλ,ν = 0 when no such inclusion exists
or its contraction coeﬃcient vanishes. Thus occurrence in the tensor product allows a transition,
but the chosen stabilizer representation determines whether its edge is present. Opposite direc-
tions generally have diﬀerent squared coeﬃcients. We require the following dimension-weighted
reciprocity:
                                        Dλ pλ,ν = Dν pν,λ .                                 (55)




                                                48
Thus multiplying each directed weight by the dimension of the source representation makes the
two directions agree. For the spherical transitions, this identity is veriﬁed explicitly in (78) and
§A.2. The undirected weighted adjacency matrix J therefore has symmetric edge weights
                                                     s
                                                         Dλ √
                                       Jλ,ν = pλ,ν          = pλ,ν pν,λ .                                   (56)
                                                         Dν
Indeed, if T = (pλ,ν ) and D = diag(Dλ ), dimension balance (55) gives the symmetric similarity
transform
                                        J = D1/2 TD−1/2 .                                 (57)
Assume that the ﬁnite graph on Ω is connected and has positive edge weights. The Perron–
Frobenius theorem supplies a strictly positive eigenvector of the weighted adjacency matrix J
for the largest eigenvalue Λ = λmax (J).
Theorem 4.2. Let n ≥ 3, let G = SO(n), and let H = StabG (o) ' SO(n − 1) for a base
point o ∈ Sn−1 . Let E be a d-dimensional irreducible real H-representation, and let Ω consist
of ﬁnitely many pairwise inequivalent irreducible real G-representations Vλ whose coordinate-
transition graph is connected. Suppose dimR HomH (E, Vλ ) = 1 for each λ ∈ Ω, and suppose the
coordinate-transition coeﬃcients satisfy (54) and (55). Let J be the weighted adjacency matrix
in (56), and put Λ = λmax (J) and Dλ = dim Vλ . If −1 < s < 1 and Λ > max{s, 0}, then
                                               1−s X
                                  A(n, s) ≤               Dλ .                            (58)
                                             d(Λ − s) λ∈Ω
                                                                                   √
Proof.PLet v be the positive unit Perron eigenvector of J in (56), and put wλ = Dλ vλ and
Z = λ wλ . The dimension-weighted reciprocity (55) and the eigenvector identity Jv = Λv
give                          X            p     X
                                 pλ,ν wλ = Dν       Jν,λ vλ = Λwν .                       (59)
                                 λ∈Ω                        λ∈Ω
Consequently, pλ,ν wλ /(Λwν ) sums to one over λ ∈ Ω for each ﬁxed ν. These Perron-normalized
weights form the probability distributions used in the coordinate isometry below. Thus
                                                r
                                            M wλ
                                    Ψx Y =           φλ,x Y
                                            λ∈Ω
                                                   Z
                                             L                                             L
is an isometric embedding into V =               λ∈Ω Vλ .   Set Px = Ψx Ψ∗x . For h =          ν∈Ω hν ∈ V, deﬁne
B : V → W ⊗ V by
                                             M X r pλ,ν wλ
                                   Bh =                                Cλ,ν hν .                            (60)
                                             λ∈Ω ν∈Ω
                                                                Λwν
                                                pλ,ν >0
Orthogonality of the images of Cλ,ν and (59) give
                                             X khν k2 X
                                 kBhk2 =                          pλ,ν wλ = khk2 ,
                                             ν∈Ω
                                                 Λwν λ∈Ω
so B is an isometry. Using (54) and then (59) gives
                                                                            s
                                 M φν,x Y          X                  M         Λwν         √
            B ∗ (ℓx ⊗ Ψx Y ) =         √               pλ,ν wλ =                    φν,x Y = Λ Ψx Y.
                                 ν∈Ω
                                           Λwν Z λ∈Ω                  ν∈Ω
                                                                                 Z
                               P
Proposition 4.1, with D = λ Dλ , proves (58). Finally, deﬁne F (x, y) = (hx, yi − s) tr(Px Py ).
Rotational invariance makes tr(Px Py ) a function of hx, yi alone. The residual Gram decomposi-
tion (53) makes F positive deﬁnite, and F (x, y) ≤ 0 when hx, yi ≤ s. If σ is uniform probability
measure on the sphere, its constant coeﬃcient satisﬁes
               ZZ                                           Z               2
                                                                                               d2
        f0 =        F (x, y) dσ(x) dσ(y) ≥ (Λ − s)              Px dσ(x)         ≥ (Λ − s) P         > 0.
                                                                            HS              λ∈Ω Dλ
Thus F satisﬁes every requirement of a two-point Delsarte certiﬁcate.                                         □



                                                         49
  The full coordinate decomposition can also contain edges leading to ambient spaces outside
the selected vertex set Ω. A ﬁnite truncation discards those edges, so the retained transition
weights need not sum to one. This causes no diﬃculty: (59) normalizes the Perron-reweighted
coeﬃcients in (60), making that operator an isometry. Thus Theorem 4.2 applies to arbitrary
ﬁnite connected truncations, including multidimensional rectangular boxes.

               5. Spherical harmonics and stabilizer representations
   To apply the moving-subspace bound of Theorem 4.2 to spherical codes, we need a family of
SO(n)-representations, each containing the same representation of the point stabilizer SO(n−1).
We must also identify the coordinate transitions between the ambient representations and the
dimensions of their moving subspaces. This section describes the relevant representations and
works out the one-dimensional construction. The general transition weights are computed in
§6, and their spectral and dimension asymptotics are analyzed in §7.
   Throughout the spherical arguments, assume n ≥ 3. The multi-row construction will impose
the stronger stable-range condition n ≥ 2r + 4. This restriction does not aﬀect the asymptotic
bounds: every hierarchy level r is ﬁxed before n → ∞.
   The group SO(n) acts transitively on Sn−1 . For a point x, the rotations ﬁxing x act on its
orthogonal complement
                                   x⊥ = {u ∈ Rn : hu, xi = 0},
and every rotation of x⊥ extends uniquely to a rotation ﬁxing x. Hence the point stabilizer of
x is naturally identiﬁed with SO(n − 1). We call a representation of this point-ﬁxing subgroup
a stabilizer representation. The ﬁxed line Rx, on which every such rotation acts trivially, is the
one-dimensional example; the tangent space x⊥ , on which the same rotations act in the usual
way, is a higher-dimensional example. A rotation carrying x to another point y also carries the
tangent space x⊥ to y ⊥ . Thus the stabilizer representations used below move naturally with
the code point.
   We ﬁrst recall the classical construction, which retains the one-dimensional stabilizer-ﬁxed
line in each selected space of spherical harmonics. We next replace this line by a space of
degree-k harmonics on x⊥ , obtaining a weighted one-dimensional path. Finally, more general
stabilizer representations yield multidimensional transition graphs and the full hierarchy.
5.1. Spherical harmonics and the classical bound. Classical spherical linear programming
uses harmonic spaces, their stabilizer-ﬁxed lines, and the associated Gegenbauer kernels. The
resulting tridiagonal spectral construction uses one ﬁxed line in each harmonic degree, just as
the classical whole-cube construction uses one ﬁxed line in each Fourier degree in §2.1.
   Equip Sn−1 with rotation-invariant probability measure. A polynomial on Rn is homoge-
neous of degree m when scaling its argument by c scales its value by cm , and it is harmonic
when its Euclidean Laplacian vanishes. Let VmS = Hm (Rn ) denote the restrictions of these
homogeneous harmonic polynomials to Sn−1 . Rotations act on VmS by changing the input of a
polynomial. These mutually orthogonal irreducible spaces are the spherical analogues of Fourier
levels [GW09, §§8.1.1–8.1.2]. For example, V0S consists of constant functions, and V1S consists
of the linear functions u 7→ hv, ui. The integer m records polynomial degree, not the dimension
of the harmonic space. That dimension is
                                                                    !
                           S             2m + n − 2       m+n−3
                          Dm = dim VmS =                        .                            (61)
                                               n−2          m
   Fix x ∈ Sn−1 . A function invariant under all rotations ﬁxing x depends only on its ra-
dial coordinate t = hx, ui. Inside each VmS , the invariant functions form a one-dimensional
subspace, called the stabilizer-ﬁxed line. Its generator normalized by Pm (1) = 1 is Pm (t) =




                                               50
 (n−2)/2      (n−2)/2                η denotes the degree-m Gegenbauer polynomial. For an or-
Cm     (t)/Cm       (1), where Cm
thonormal basis Ym,1 , . . . , Ym,Dm     S
                                   S of Vm , deﬁne its reproducing kernel by

                                                S
                                               Dm
                                               X
                                  S
                                 Km (u, v) =         Ym,a (u)Ym,a (v).
                                               a=1
This kernel is independent of the chosen orthonormal basis. The spherical addition formula
identiﬁes it explicitly [BV08, (4)]:
                                    S           S
                                   Km (u, v) = Dm Pm (hu, vi).                                 (62)
The deﬁning orthonormal-basis sum is positive deﬁnite. Therefore, so is Pm (hu, vi), and non-
negative Gegenbauer coeﬃcients suﬃce for positive deﬁniteness. (The converse is Schoenberg’s
                                                          P
theorem [S42] and is not needed here.) Thus, if f = M       m=0 fm Pm is a polynomial, f0 > 0,
fm ≥ 0, and f (t) ≤ 0 for −1 ≤ t ≤ s, the spherical linear-programming bound is [DGS77]
                                                       f (1)
                                         A(n, s) ≤           .
                                                        f0
Just as in the Fourier-path construction of §2.1, the trivial stabilizer representation in VmS is
therefore the line spanned by Pm (hx, ·i). The Gegenbauer recurrence (66) shows that multipli-
cation by u 7→ hx, ui connects this line only to the ﬁxed lines of degrees m − 1 and m + 1. Thus
consecutive harmonic degrees form a weighted path, whose tridiagonal matrix gives the classi-
cal spectral certiﬁcate [BN06, §3.3]. The explicit zonal polynomials identify the classical ﬁxed
lines. The addition formula (62) also normalizes the coordinate maps in Lemma 5.1; apart from
this normalization, the new construction uses the harmonic spaces and normalized recurrence
(67)–(68). Lemma 5.2 below calculates the largest-eigenvalue limit of this path; its case k = 0
recovers the direct whole-sphere Kabatianskii–Levenshtein spectral bound [KL78], before the
additional spherical-cap optimization.
5.2. Harmonics on the tangent sphere. The classical construction associates one stabilizer-
ﬁxed vector with each selected harmonic degree. We replace that vector with a common space Ex
of harmonic polynomials on x⊥ , embedded inside several ambient harmonic spaces ViS . Consec-
utive ambient degrees are connected by a symmetric tridiagonal matrix, as in the Fourier-degree
construction of §2. The projection bound Proposition 4.1 then divides by dim Ex rather than
by the classical rank 1. For positive harmonic degree, assume n ≥ 4, so the stabilizer represen-
tations used below have real-scalar endomorphisms. We now describe Ex , its embeddings φi,x ,
the weighted adjacency matrix Jk,L , and the resulting spherical-code bound.
   For a base point x, the unit sphere in its tangent space is
                                       S(x⊥ ) = x⊥ ∩ Sn−1 .
Equip this sphere with its rotation-invariant probability measure. The stabilizer SO(n − 1) acts
on it by rotating its tangent directions. For k ≥ 0, let
                                                                    !           !
                                                         n+k−2   n+k−4
                Ex = Hk (x⊥ ),      dSk = dim Ex =             −       .                       (63)
                                                           k      k−2
Here and below, a binomial coeﬃcient with negative lower index is zero. Thus Ex consists
of degree-k homogeneous harmonic polynomials on x⊥ , restricted to S(x⊥ ). Equivalently, its
elements are symmetric traceless k-tensors on x⊥ : a symmetric tensor T represents the poly-
nomial ξ 7→ T (ξ, . . . , ξ), and harmonicity means that contracting any two tensor indices gives
zero. In particular, k is the polynomial degree or tensor order; it is not the dimension dSk , which
is generally much larger. For k = 0, Ex is the classical one-dimensional space of constants; for
k = 1, it is naturally identiﬁed with x⊥ ; and for k = 2, it consists of traceless quadratic forms
on x⊥ .
   The tangent harmonic spaces Ex = Hk (x⊥ ) also appear in the matrix-valued kernels of
Bachoc and Vallentin [BV08, (9), Thms. 3.1–3.2]. There the stabilizer ﬁxes one distinguished




                                                 51
base point, producing kernels in three inner products. Here Ex moves with the code point, and
the overlap of the corresponding moving projections remains a scalar two-point kernel.
   To see which ambient harmonic spaces contain Ex , restrict their rotation action from SO(n)
to the subgroup ﬁxing x. The multiplicity-free orthogonal-group branching rule gives [GW09,
Thms. 8.1.3–8.1.4]
                                                              M
                                                              i
                                         ViS ↓SO(n−1) '             Hk (x⊥ ).                                      (64)
                                                              k=0
Every summand occurs with multiplicity one, meaning that ViS contains exactly one subspace
of each indicated harmonic type. In particular, it contains one copy of Ex if i ≥ k, and none if
i < k. Write φi,x : Ex → ViS for the isometric embedding of this unique copy.
   Every u ∈ Sn−1 away from the poles u = ±x has the unique decomposition
                                     p
                          u = tx +     1 − t2 ξ,         t = hx, ui,            ξ ∈ S(x⊥ ).
In these coordinates, every element of the copy of Ex inside ViS separates into a tangential
harmonic Y of degree k and a radial polynomial of degree i − k:
                                 (φi,x Y )(u) = pi−k (t)(1 − t2 )k/2 Y (ξ),                                        (65)
                                                                      k+(n−2)/2
where Y  ∈ Ex and the radial polynomial pi−k is a scalar multiple of Ci−k       [BV08, (8),
proof of Thm. 3.2]. Choose this scalar multiple to have positive leading coeﬃcient and to make
φi,x an isometry. These choices ﬁx the signs of all the embeddings, and the expression extends
continuously over the poles. Multiplication by the base-point coordinate t = hx, ui preserves
the tangential harmonic Y and acts only on its radial polynomial. Set η = k + (n − 2)/2. The
standard Gegenbauer identity [BN06, §3.3]
                        2(j + η)tCjη (t) = (j + 1)Cj+1
                                                   η                      η
                                                       (t) + (j + 2η − 1)Cj−1 (t)                                  (66)
                       η
with j = i − k, where C−1 = 0, shows that only degrees i + 1 and i − 1 occur.                              Applying the
isometric normalization in (65) gives
                                               (k)                   (k)
                                     tφi,x = αi φi+1,x + βi φi−1,x ,                                               (67)
with
           (k) 2   (i − k + 1)(i + k + n − 2)       (k) 2    (i − k)(i + k + n − 3)
          αi        =                          ,    βi      =                          .  (68)
                       (2i + n − 2)(2i + n)                   (2i + n − 4)(2i + n − 2)
   The recurrence (67) describes scalar multiplication by u 7→ hx, ui. To apply the projection
bound Theorem 4.2, we must instead normalize the vector-valued coordinate maps between
neighboring harmonic degrees. The required normalization is determined by the classical ﬁxed-
                (0)
line coeﬃcient αi in (68).
Lemma 5.1. Let i ≥ k, abbreviate Dj = DjS , and let Πj be the orthogonal projection onto VjS .
Deﬁne the upward and downward coordinate-multiplication maps by
                                                                                                      
                Mi↑ : Rn ⊗ ViS −→ Vi+1
                                    S
                                       ,                             Mi↑ (v ⊗ f ) = Πi+1 hv, ·if ,
                                                                                                  
               Mi↓ : Rn ⊗ Vi+1
                            S
                               −→ ViS ,                              Mi↓ (v ⊗ g) = Πi hv, ·ig .
These maps satisfy
                           Mi↑ (Mi↑ )∗ = m↑i idV S ,           Mi↓ (Mi↓ )∗ = m↓i idV S ,
                                                   i+1                                 i
where the normalization constants are
                            s                                              s
                                 Di     i+1                                    Di+1   i+n−2
               m↑i = αi                                   m↓i = αi
                      (0)                                        (0)
                                     =        ,                                     =            .                 (69)
                                Di+1   2i + n                                   Di    2i + n − 2




                                                         52
Consequently, the coordinate inclusions
                                             (M ↑ )∗
                                       Ci↑ = q i : Vi+1
                                                     S
                                                        −→ Rn ⊗ ViS ,
                                                  ↑
                                               mi
                                             (M ↓ )∗
                                       Ci↓ = q i : ViS −→ Rn ⊗ Vi+1
                                                                 S
                                                  ↓
                                               mi
are isometries, and their contractions onto the tangent-harmonic copies satisfy
                                                            (k)
                                           ↑ ∗            αi
                                        (Ci ) x ⊗ φi,x Y = q     φi+1,x Y,
                                                             m↑i
                                                            (k)
                                        ↓ ∗               αi
                                      (Ci ) x ⊗ φi+1,x Y = q     φi,x Y.
                                                             m↓i
The resulting symmetric edge weight is
                                                                     (k)
                                                               (αi )2
                                                   Ji,i+1 =          (0)
                                                                            .                               (70)
                                                                   αi
Proof. The addition formula (62) identiﬁes the reproducing kernel Kj = KjS of VjS as Kj (u, v) =
                                                                              p
Dj Pj (hu, vi). Thus its unit stabilizer-ﬁxed vector at x is zj,x = Kj (x, ·)/ Dj . Write tx (u) =
hx, ui. Expanding the Hilbert–Schmidt norm in orthonormal bases and using rotation invariance
gives
                                       ZZ
                    kMi↑ k2HS =                        hu, viKi (u, v)Ki+1 (u, v) dσ(u) dσ(v)
                                            (Sn−1 )2
                                       p                                        (0) p
                                  =        Di Di+1 htx zi,x , zi+1,x i = αi             Di Di+1 .
The ﬁnal equality is the recurrence (67) for k = 0. For every standard basis vector er ∈ Rn ,
self-adjointness of coordinate multiplication gives
                                      hMi↑ (er ⊗ f ), gi = hf, Mi↓ (er ⊗ g)i.
Summing over r shows that the two coordinate maps have the same Hilbert–Schmidt norm.
Moreover, Mi↑ (Mi↑ )∗ and Mi↓ (Mi↓ )∗ commute with rotations. Since their target harmonic spaces
are irreducible, they are scalar operators. Taking traces identiﬁes their respective scalar factors
     (0) p                (0) p
as αi     Di /Di+1 and αi       Di+1 /Di . Substituting (61) and (68) with k = 0 yields (69). The
                                                                               (k)      (k)
stated contractions follow directly from (67); in the downward direction, βi+1 = αi . Their
squared coeﬃcients and dimension-weighted reciprocity satisfy
                                (k)                            (k)
                           (αi )2                           (αi )2
                pi,i+1 =               ,        pi+1,i =                ,       Di pi,i+1 = Di+1 pi+1,i .   (71)
                                m↑i                           m↓i
                                                                     √
Since m↑i m↓i = (αi )2 , the symmetric edge weight
                  (0)
                                                                         pi,i+1 pi+1,i is (70).               □
  Fix k < L, and retain the unique copy of Ex in each of VkS , . . . , VLS . The resulting transition
graph is the one-dimensional path
                                           VkS ←→ Vk+1
                                                    S
                                                       ←→ · · · ←→ VLS .                                    (72)
The vertices record ambient harmonic degree; they do not record dimensions of subspaces.
Substituting (68) into (70) gives the symmetric weight of the edge ViS ↔ Vi+1
                                                                           S :

                            (k)          (i − k + 1)(i + k + n − 2)
                           ci     =p                                       .                  (73)
                                    (i + 1)(i + n − 2)(2i + n − 2)(2i + n)
Let Jk,L be the weighted adjacency matrix of the harmonic-degree path: its diagonal entries
                                    (k)
vanish and its (i, i + 1) entry is ci . Write λk,L = λmax (Jk,L ). The positive Perron eigenvector



                                                              53
of Jk,L , as in Theorem 4.2, speciﬁes how to combine the copies of Ex into a single rank-dSk
projection inside VkS ⊕ · · · ⊕ VLS . Theorem 4.2 therefore gives
                                           1−s       XL
                          A(n, s) ≤                     DS       if λk,L > s.
                                      dSk (λk,L − s) i=k i
     P
Here L       S                                                     S
        i=k Di is the dimension of the ambient direct sum, while dk , given in (63), is the rank of
the moving projection. For k = 0, this rank is 1, recovering the classical ﬁxed-line construction.
When k grows proportionally to n, dSk grows exponentially and its logarithm is subtracted from
the code exponent. This gain over the classical ﬁxed-line construction comes from a scalar
two-point Delsarte certiﬁcate, even though the moving subspaces have dimension greater than
one.
   The next lemma identiﬁes the spectral limit of this one-dimensional harmonic-degree path,
including the classical Kabatianskii–Levenshtein case k = 0.
Lemma 5.2. Fix 0 ≤ b < a, and suppose k/n → b and L/n → a. Then
                                                       2(a − b)(1 + a + b)
                           λk,L −→ 2Γrow (a, b) =              p           .
                                                       (1 + 2a) a(1 + a)
Proof. Uniformly for i/n in a compact subinterval of (0, ∞), the edge weight (73) converges to
                                                u(u + 1) − b(b + 1)
                                Γrow (u, b) =           p           .
                                                (1 + 2u) u(u + 1)
                                                           p
            p increases on u ≥ b: its ﬁrst summand u(u + 1)/(1 + 2u) increases, while b(b +
This function
1)/((1+2u) u(u + 1)) decreases. If b > 0, this convergence is uniform over the entire harmonic-
degree path, so its largest edge weight converges to Γrow (a, b). If b = 0, the same conclusion
follows by ﬁrst restricting to i ≥ εn. The omitted edges satisfy
                                          s                             s
                            (k)  (0)           (i + 1)(i + n − 2)           i+1
                       0 ≤ ci ≤ ci =                               ≤            ,
                                              (2i + n − 2)(2i + n)          n−2
because (i − k + 1)(i + k + n − 2) = (i + 1)(i + n − 2) − k(k + n − 3). Letting ε ↓ 0 proves
the claim at b = 0 as well. The maximum row sum therefore gives lim sup λk,L ≤ 2Γrow (a, b).
For mn → ∞ with mn = o(n), the edge weights on the last mn vertices converge uniformly
to Γrow (a, b). Applying (28) to the ﬁrst discrete sine vector on that terminal path gives the
matching lower bound.                                                                       □
   When b = 0, the limiting eigenvalue is 2q(a), and the classical feasibility boundary 2q(a) =
s gives a = a0 (s) from the introduction and the direct whole-sphere exponent Hsph (a0 (s)).
Applying the additional spherical-cap optimization gives instead the classical exponent BKL (s)
in (10). Positive b gives the tangent-harmonic spectral quantity in (11).
   The harmonic-degree path (72) uses only ambient spaces of scalar spherical harmonics. Scalar
multiplication by the base-point coordinate connects just the neighboring degrees i − 1 and i + 1,
as in (67). The moving-subspace construction also allows other ambient representations, how-
ever: its rotation-equivariant coordinate maps take values in Rn ⊗ ViS , followed by contraction
with the base-point coordinate as in (54). This vector-valued tensor product contains one more
irreducible representation besides the two neighboring harmonic spaces.
   For integers i ≥ j ≥ 0, let V(i,j) denote the irreducible orthogonal-group tensor representation
whose Young diagram has two rows of lengths i and j; its precise highest-weight description is
given in §5.3. A zero second row gives V(i,0) = ViS . For i ≥ 1 and n ≥ 6, tensoring with the
standard representation Rn gives [Kra18, (B.2)]
                             Rn ⊗ V(i,0) ' V(i+1,0) ⊕ V(i−1,0) ⊕ V(i,1) .
The ﬁrst two summands correspond to the neighboring harmonic degrees already present in (67).
The third, V(i,1) , has row lengths i and 1; it is an ambient tensor representation rather than a
space of scalar functions on the sphere. For i ≥ k ≥ 1, the restriction of V(i,1) still contains the



                                                  54
stabilizer representation Ex . Allowing all the additional spaces V(i,j) containing Ex gives the
vertex set
                                    {(i, j) : i ≥ k ≥ j ≥ 0}.
The graph on vertices (i, j) now has edges changing either i or j; the harmonic-degree path is
the boundary j = 0. The positive Perron eigenvector of the two-dimensional weighted adjacency
matrix again assembles a moving projection of rank dSk . Since SO(n) is transitive on ordered
pairs with a prescribed inner product, the overlap of two such projections depends only on hx, yi.
Consequently, the enlarged graph still produces a scalar two-point Delsarte certiﬁcate.
5.3. The multi-row hierarchy. The degree-k tangent-harmonic subspace consists of symmet-
ric traceless k-tensors on x⊥ . This subspace supports both the one-dimensional harmonic-degree
path and its enlargement to the two-dimensional graph on (i, j). Higher-dimensional transition
graphs arise by allowing more general orthogonal-group tensor representations.
   Fix a hierarchy level r ≥ 0 and assume n ≥ 2r + 4. Since r remains ﬁxed as n → ∞, this di-
mension restriction is automatic. The irreducible orthogonal-group tensor representations used
here correspond to Young diagrams: arrays of boxes whose row lengths form a weakly decreas-
ing sequence of nonnegative integers. This sequence, completed by zero entries as necessary,
is the dominant highest weight of the representation. For example, the one-row diagram (k)
corresponds to symmetric traceless k-tensors; additional rows describe other tensor symmetries.
   We use ambient SO(n)-representations corresponding to Young diagrams with at most r + 1
rows and stabilizer SO(n − 1)-representations corresponding to diagrams with at most r rows.
Under n ≥ 2r + 4, their remaining highest-weight coordinates vanish, so none reaches the ﬁnal
available orthogonal-group weight coordinate. This avoids the exceptional splitting that can
occur outside the stable range. The hierarchy level counts these rows, not the dimension of a
representation or the number of graph vertices.
   Fix an irreducible SO(n − 1)-representation Eµ with highest weight
                          µ = (µ1 , . . . , µr , 0, . . .),   µ1 ≥ · · · ≥ µr ≥ 0.
Thus r bounds the number of nonzero stabilizer rows. An ambient representation Vλ of SO(n)
has highest weight
                       λ = (λ1 , . . . , λr+1 , 0, . . .),    λ1 ≥ · · · ≥ λr+1 ≥ 0.
The orthogonal-group branching rule [GW09, Thms. 8.1.3–8.1.4] says that restricting Vλ from
SO(n) to SO(n − 1) contains Eµ exactly when every stabilizer row length lies between the two
adjacent ambient row lengths:
                                λ1 ≥ µ1 ≥ λ2 ≥ · · · ≥ µr ≥ λr+1 ≥ 0.                        (74)
The harmonic decomposition (64) is its specialization to one-row ambient representations. Every
such copy occurs with multiplicity one. Thus, after choosing µ, the interlacing inequalities
identify the ambient representations that contain the selected stabilizer type. These ambient
weights λ will be the vertices of the transition graph. The stabilizer weight µ remains ﬁxed
throughout that graph: only λ varies from vertex to vertex. When taking the high-dimensional
limit, the initial choice of µ may depend on n, but it is still ﬁxed within each individual graph.
   The standard SO(n) representation Rn has highest weight (1, 0, . . . , 0). Tensoring Vλ with Rn
adds or removes one box from its Young diagram, and hence increases or decreases a single row
length by one [Kra18, (B.2)]. In odd dimensions, a potential unchanged-weight term is absent
under the zero-tail assumption, as explained in §A.2. The transition graph therefore joins λ to
λ ± eℓ , where eℓ is the ℓth coordinate vector, provided the resulting row lengths remain weakly
decreasing and satisfy (74) for the same ﬁxed µ. Thus the graph is the nearest-neighbor lattice
graph on the ambient weights inside the interlacing region. When r = 0, it is the classical
one-dimensional path of spherical harmonic degrees. When µ = (k), it is the two-dimensional
region i ≥ k ≥ j ≥ 0. Generally, r stabilizer rows permit r + 1 ambient coordinates and hence
an (r + 1)-dimensional transition graph.
   The representation-theoretic inputs are the orthogonal-group branching condition (74) and
Weyl’s dimension formula (113) [GW09, §7.1.2 and §§8.1.1–8.1.2], together with the explicit


                                                         55
coordinate-multiplication coeﬃcients in Kravchuk’s conventions [Kra18, §§2.1–2.3 and App. B].
Kravchuk’s Spin(n) formulas apply unchanged to integral tensor representations of SO(n). §A.2,
speciﬁcally (111) and (112), reduces the odd- and even-dimensional formulas to the common
transition weights used below. §A.3 records the dimensions of Vλ and Eµ in (113) and their
uniform exponential rates in Lemma A.1.

                                 6. The spherical transition graph
   §5.3 described which ambient representations Vλ contain a chosen stabilizer representation
Eµ and which pairs of ambient representations are connected by coordinate multiplication. To
obtain a spherical-code bound, we must determine the strength of each coordinate transition.
We ﬁrst give the directed squared coeﬃcients, then combine opposite directions into a symmetric
weighted adjacency matrix JΩ . The largest eigenvalue of JΩ and the dimensions of Vλ and Eµ
determine the ﬁnite-dimensional projection bound in Theorem 4.2.
   Fix r ≥ 0 and n ≥ 2r + 4. Choose a stabilizer representation Eµ with highest weight µ =
(µ1 , . . . , µr , 0, . . .). The highest weights λ = (λ1 , . . . , λr+1 , 0, . . .) of the ambient representations
containing Eµ satisfy (74), and each ambient representation contains exactly one copy of Eµ .
   Coordinate multiplication can increase or decrease one row length λℓ . The resulting coeﬃ-
cients take a uniform form in odd and even dimensions after adding the standard orthogonal-
group oﬀsets to the row lengths. For 1 ≤ ℓ ≤ r + 1 and 1 ≤ m ≤ r, set
                       b = λ + n − ℓ,                      n−1                              n
                       λ ℓ     ℓ              b m = µm +
                                              µ                      − m,           ρn,r = − r − 1.            (75)
                                   2                           2                            2
Write eℓ for the ℓth coordinate vector. The scalar cℓ,± (λ; µ) describes multiplication by the base-
point coordinate between the copies of Eµ in Vλ and Vλ±eℓ , in the sense of (54). Deﬁne its squared
magnitude by pℓ,± (λ; µ) = |cℓ,± (λ; µ)|2 . If the target row lengths are not weakly decreasing or
fail (74), there is no target representation containing Eµ , and its transition coeﬃcient is zero.
On the full graph of ambient weights containing the ﬁxed stabilizer representation Eµ , these
squared coeﬃcients sum to one at each vertex, as in (77). They may therefore be viewed as
transition probabilities on that full graph, but this probabilistic interpretation is not needed
for the code bound. Indeed, the construction retains a ﬁnite vertex set Ω and omits every edge
leaving Ω, so the remaining coeﬃcients generally sum to less than one. What the construction
uses is the dimension-weighted reciprocity (78), which extends (71) and allows the ﬁnite directed
transition matrix to be symmetrized. The positive Perron eigenvector of the resulting symmetric
weighted adjacency matrix is then reweighted as in (59) to produce the moving projections.
Proposition 6.1. Fix r ≥ 0, n ≥ 2r + 4, and ambient and stabilizer highest weights λ, µ
satisfying (74). If 1 ≤ ℓ ≤ r + 1 and λ ± eℓ is a dominant weight still satisfying (74), its directed
squared coordinate coeﬃcient is
                                                             Y
                                                             r
                                                                                    
                                               b ± ρn,r )
                                              (λ                   b ± 1 )2 − µ
                                                                  (λ          b2m
                                                 ℓ                   ℓ 2
                                                            m=1
                              pℓ,± (λ; µ) =                                             .                    (76)
                                                             Y
                                                            r+1
                                                       b
                                                      2λ         b2 − λ
                                                                (λ    b2)
                                                         ℓ         ℓ    q
                                                           q=1
                                                           q6=ℓ
With the zero convention above, the full transition graph satisﬁes
                                      X
                                      r+1
                                                                      
                                            pℓ,+ (λ; µ) + pℓ,− (λ; µ) = 1,                                   (77)
                                      ℓ=1
and, for every graph edge λ ↔ λ + eℓ ,
                              dim Vλ pℓ,+ (λ; µ) = dim Vλ+eℓ pℓ,− (λ + eℓ ; µ).                              (78)
Proof. The coeﬃcients come from coordinate multiplication between the multiplicity-free sta-
bilizer copies. Kravchuk gives separate odd- and even-dimensional expressions for these coeﬃ-
cients [Kra18, (B.12)–(B.13)]. §A.2 identiﬁes their normalization and records the corresponding



                                                        56
squared coeﬃcients in (111) and (112). In both expressions, factors belonging to zero highest-
weight coordinates cancel, leaving the common formula (76). The same appendix also explains
why the apparent odd-dimensional self-loop is absent.
   For Y ∈ Eµ , the base-point coordinate ℓx is ﬁxed by the stabilizer. Therefore ℓx ⊗ φλ,x Y has
stabilizer type Eµ , and its orthogonal projections onto the ambient irreducible summands have
squared norms pℓ,± (λ; µ)kY k2 . Orthogonality of these summands and kℓx k = 1 give
                                                  X
                                                  r+1
                                                                                 
                    kY k2 = kℓx ⊗ φλ,x Y k2 =           pℓ,+ (λ; µ) + pℓ,− (λ; µ) kY k2 ,
                                                  ℓ=1
proving (77) on the full graph. Finally, applying the exact Weyl dimension formula (113) to the
two endpoints of an existing edge gives (78); the calculation appears at the end of §A.2.    □
  Now choose a ﬁnite connected set Ω of ambient weights satisfying (74), and retain only edges
whose two endpoints belong to Ω. Although the two directed weights on an edge generally diﬀer,
(78) says that each agrees after multiplication by the dimension of its source representation.
Thus (57) converts the directed coeﬃcient matrix into a symmetric weighted adjacency matrix
JΩ . The edge weight of JΩ is the geometric mean of the forward and reverse squared coeﬃcients:
                                           q
                               Jλ,λ+eℓ =       pℓ,+ (λ; µ)pℓ,− (λ + eℓ ; µ),                      (79)
with every other entry zero. Write dµ = dim Eµ for the rank of the moving projection, Dλ =
dim Vλ for each ambient representation dimension, and ΛΩ = λmax (JΩ ) for the largest eigenvalue
of the ﬁnite weighted adjacency matrix. Theorem 4.2, applied with G = SO(n), H = SO(n−1),
and W = Rn , produces a scalar positive-deﬁnite kernel depending only on the inner product
and gives the following bound.
Theorem 6.2. Fix −1 < s < 1, r ≥ 0, n ≥ 2r + 4, a stabilizer representation Eµ , and a ﬁnite
connected set Ω of ambient weights satisfying (74). If ΛΩ > max{s, 0}, then
                                               1−s     X
                                A(n, s) ≤                  Dλ .                         (80)
                                           dµ (ΛΩ − s) λ∈Ω
6.1. The two-row graph. To make the general graph concrete, return to the degree-k tangent
harmonics Eµ = Hk (x⊥ ), whose stabilizer weight is the single row µ = (k). An ambient
representation may now have two rows λ = (i, j). By (74), it contains Eµ exactly when i ≥ k ≥
j ≥ 0. Thus the vertices form a two-dimensional region: the one-dimensional harmonic-degree
path is the boundary j = 0, and j > 0 supplies the ambient representations omitted from that
boundary. The resulting lattice strip is shown in Figure 3.
   The two possible coordinate directions join (i, j) to (i ± 1, j) or to (i, j ± 1), respectively, and
(76) gives the four directed squared coeﬃcients
         (i − k + 1)(i + k + n − 2)(i + n − 3)                  (i − k)(i + k + n − 3)(i + 1)
 pi,+ =                                          , pi,− =                                         ,
         (i − j + 1)(i + j + n − 3)(2i + n − 2)            (i − j + 1)(i + j + n − 3)(2i + n − 2)
            (k − j)(j + k + n − 3)(j + n − 4)                    j(k − j + 1)(j + k + n − 4)
  pj,+ =                                          , pj,− =                                        .
         (i − j + 1)(i + j + n − 3)(2j + n − 4)            (i − j + 1)(i + j + n − 3)(2j + n − 4)
                                                                                                (81)
The factors i−k, k−j, and j in (81) make the corresponding transitions vanish at the boundaries
i = k, j = k, and j = 0, respectively. At j = 0, pi,+ and pi,− describe the one-dimensional
harmonic-degree path, whereas
                                                   k(k + n − 3)
                                  pj,+ (i, 0) =
                                                (i + 1)(i + n − 3)
is positive precisely when k > 0. This edge from (i, 0) to (i, 1) is absent from the classical
ﬁxed-line construction. Retaining vertices with j > 0 incorporates such additional edges into
λmax (JΩ ) while leaving the stabilizer dimension dSk unchanged.




                                                    57
                    j
                                ﬁxed stabilizer weight µ = (k)
                        k
                                                                             (I, J)
                        J




                        1

                        0
                            k      k+1   k+2                             I       I +1
                                                                                            i
                                            one-row subgraph j = 0

        Figure 3. The spherical two-row representation graph for a ﬁxed stabilizer
        weight µ = (k). Ambient vertices (i, j) satisfy i ≥ k ≥ j ≥ 0; horizontal and
        vertical edges change i and j, respectively. Their directed squared weights are
        given in (81), and (79) converts opposite directions into symmetric edge weights.
        The blue boundary is the one-row subgraph. The dashed box marks a lattice
        region near an upper corner. For any large ﬁxed box size, its edge weights become
        asymptotically constant as n → ∞, and a product of discrete sine waves bounds
        the largest eigenvalue from below. Letting the box size increase gives Lemma 7.2.

  The ambient dimension needed in (80) is obtained by specializing the exact Weyl formula
(113) in §A.3 to λ = (i, j):
                                                                                        !            !
              (2i + n − 2)(2j + n − 4)(i − j + 1)(i + j + n − 3) i + n − 3                      j+n−5
       Di,j =                                                                                         .
                       (n − 2)(n − 4)(i + 1)(i + n − 3)              i                            j
The identity Di,j pi,+ (i, j) = Di+1,j pi,− (i+1, j) and its j-direction analogue give (78); restricting
to j = 0 recovers (73).

                                 7. Asymptotic spherical-code bounds
   We now evaluate the ﬁnite spherical-code bound (80) as the dimension tends to inﬁnity. The
spectral constraint involves ΛΩ = λmax (JΩ ), while the exponent in the bound is determined by
                                         P
                                            λ∈Ω dim Vλ
                                                       .
                                             dim Eµ
We keep the number r of stabilizer rows ﬁxed, let the row lengths of Eµ and Vλ grow propor-
tionally to n, and compute both the spectral constraint and the dimension-ratio exponent from
the limiting coordinates.
   Fix r ≥ 0 before taking n → ∞. Suppose the ambient and stabilizer row lengths satisfy
λℓ /n → aℓ and µm /n → bm , respectively. We require strict separation between successive
ambient and stabilizer rows, while allowing the ﬁnal ambient row to vanish:
                                     a1 > b1 > a2 > · · · > br > ar+1 ≥ 0.                                (82)
For r = 0, this condition means simply a1 ≥ 0. Two scalar functions describe the limiting
edge weights of JΩ . The quadratic change of variables A(u) = u(1 + u) converts shifted highest-
weight diﬀerences into diﬀerences of nonnegative real numbers. The function q(u) is the limiting
symmetric edge weight in the classical level-zero harmonic path at degree un + o(n). Put
                                                                     p
                                                          u(1 + u)
                                  A(u) = u(1 + u),          q(u) = .
                                                          1 + 2u
Write xℓ = A(aℓ ) and ym = A(bm ). Since A is strictly increasing, the interlacing inequalities
(82) give x1 > y1 > x2 > · · · > yr > xr+1 ≥ 0. The residues Rℓ associated with the interlacing




                                                       58
nodes xℓ , ym , the resulting weighted edge strength Γr , and the ambient-to-stabilizer dimension
exponent Φr are
                          Y
                          r
                                 (xℓ − ym )
                                                                                        X
                                                                                        r+1
            Rℓ (a, b) = m=1                   ,                           Γr (a, b) =         Rℓ (a, b)q(aℓ ),
                         Y
                        r+1
                                                                                        ℓ=1
                                (xℓ − xq )
                                                                                                                 (83)
                          q=1
                          q6=ℓ
                          X
                          r+1                     X
                                                  r
            Φr (a, b) =         Hsph (aℓ ) −            Hsph (bm ).
                          ℓ=1                     m=1
                                Q                   Q
The Rℓ are the residues of m (z − ym )/ ℓ (z − xℓ ). The strict interlacing in (82) makes every
                                                 P
residue positive, and comparison at z = ∞ gives r+1ℓ=1 Rℓ = 1. The next subsection constructs
ﬁnite weighted adjacency matrices JΩn satisfying λmax (JΩn ) ≥ 2Γr + o(1). The same subsection
shows that the normalized logarithm of the dimension ratio in (80) converges to Φr .
7.1. Spectral and dimension asymptotics. The spectral estimate is local, even though
transition weights vary across the full ambient-weight graph. Keep the stabilizer weight µ ﬁxed
and consider a lattice box of side mn near an ambient weight λ∗n , where mn → ∞, mn = o(n),
and λ∗n /n → a. Every vertex of this box has the same limiting normalized ambient weight a.
Consequently, the edge weights freeze to constants depending only on their coordinate direction:
                                                                   X                                     
              wℓ = Rℓ (a, b)q(aℓ ),               (Jloc f )(v) =          wℓ f (v + eℓ ) + f (v − eℓ ) .
                                                                      ℓ
                                                     P
Here f is zero outside the box. Thus 2 ℓ wℓ I − Jloc is the usual weighted Dirichlet lattice
Laplacian, whose ﬁrst eigenvector is a product of discrete sine vectors.
   We ﬁrst calculate the limiting edge weights in Lemma 7.1; the local sine test function then
yields the eigenvalue lower bound in Lemma 7.2. Finally, Lemma A.1 in §A.3 determines the
exponential ratio of ambient to stabilizer dimensions.
Lemma 7.1. Fix r ≥ 0. Suppose (82) holds, λℓ /n → aℓ , and µm /n → bm . For every existing
coordinate transition,
                                               Rℓ (2aℓ + 1 ± 1)
                               pℓ,± (λ; µ) −→                   .                     (84)
                                                  2(1 + 2aℓ )
Consequently,
                                      Jλ,λ+eℓ −→ Rℓ q(aℓ ).                           (85)
Both limits hold uniformly whenever
                                λℓ                  µm
                           max     − aℓ + max          − bm = o(1).
                            ℓ   n           1≤m≤r n
The second maximum is understood as zero when r = 0.
Proof. Substitute (75) into (76) and use (u + 12 )2 − (v + 21 )2 = A(u) − A(v). The quadratic and
linear factors give (84); the balanced geometric mean of the forward and reverse coeﬃcients
gives (85). The strict interlacing in (82) keeps all limiting denominator diﬀerences nonzero,
so the rational formulas converge uniformly on shrinking neighborhoods of the prescribed row
lengths.                                                                                        □
   Choose integral stabilizer row lengths µm = bm n + o(n) and upper ambient row lengths
Nℓ,n = aℓ n + o(n), taking Nr+1,n = 0 if ar+1 = 0. Let Ωn consist of the ambient weights
satisfying the interlacing inequalities (74) and
                     µℓ ≤ λℓ ≤ Nℓ,n (1 ≤ ℓ ≤ r),                          0 ≤ λr+1 ≤ Nr+1,n .
                     ∗
Its upper corner is λn = (N1,n , . . . , Nr+1,n ).
Lemma 7.2. The weighted adjacency matrix of the ﬁnite ambient-weight set Ωn satisﬁes
                                      lim inf λmax (JΩn ) ≥ 2Γr (a, b).                                          (86)
                                       n→∞



                                                            59
Proof. Choose mn → ∞ with mn = o(n). Strict interlacing allows every positive coordinate
of λ∗n to decrease independently by 0, 1, . . . , mn − 1 while remaining inside Ωn ; a zero last
coordinate stays ﬁxed. The resulting vertices form a rectangular box with mn vertices in each
active coordinate direction. Since each side length is o(n), Lemma 7.1 shows that all edges in
the ℓth coordinate direction have weight Rℓ q(aℓ ) + o(1), uniformly throughout the box.
   On a one-dimensional path with mn vertices and constant edge weight w, the ﬁrst sine vector
has Rayleigh quotient 2w cos(π/(mn + 1)). Taking the product of these sine vectors over the
coordinate directions therefore gives
                                         X
                                         r+1
                                                                 π
                                     2         Rℓ q(aℓ ) cos          + o(1).
                                         ℓ=1
                                                               mn + 1
The Rayleigh–Ritz principle (28) now proves (86). If ar+1 = 0, the rectangular box has no
direction corresponding to the last ambient coordinate, but the omitted contribution Rr+1 q(0)
also vanishes. Hence the same lower bound holds when ar+1 = 0.                              □
  The dimension calculation is separate from the spectral estimate. At the upper corner λ = λ∗n ,
Lemma A.1 gives the exponential growth rates of the ambient representation and the stabilizer
representation:
         1               X
                         r+1
                                                                  1               Xr
           log2 dim Vλ =     Hsph (aℓ ) + o(1),                     log2 dim Eµ =     Hsph (bm ) + o(1).                     (87)
         n               ℓ=1
                                                                  n               m=1
Fix A > maxℓ aℓ . For all suﬃciently large n, every λ ∈ Ωn satisﬁes λℓ ≤ Nℓ,n ≤ An. Since Hsph
is increasing, Lemma A.1 therefore gives uniformly on Ωn
                 X
                 r+1                                                    X
                                                                            r+1                                            
 1                        λℓ                           log(n + 2)                            Nℓ,n                    log(n + 2)
   log2 dim Vλ =     Hsph            + Or,A                             ≤         Hsph                  + Or,A                  .
 n               ℓ=1
                          n                                n                ℓ=1
                                                                                              n                          n
Thus the upper corner λ∗n maximizes the ambient dimension exponent,Pwith uniform error
Or,A (log(n + 2)/n). There are only O(nr+1 ) ambient weights in Ωn , so λ∈Ωn dim Vλ diﬀers
from the largest ambient dimension by a subexponential factor:
                               1       X           X
                                                   r+1
                                 log2     dim Vλ =     Hsph (aℓ ) + o(1).                                                    (88)
                               n      λ∈Ω          ℓ=1
                                               n

Proof of Theorem 1.2. First suppose
                                                       2Γr (a, b) > s,
so Lemma 7.2 implies that ΛΩn − s stays uniformly positive. Hence the prefactor in (80) is
bounded, while (87) and (88) give dimension-ratio exponent Φr . Consequently,
                                          A(n, s) ≤ 2(Φr (a,b)+o(1))n .
   The estimate extends to the feasibility boundary 2Γr = s > 0. For c > 0, deﬁne the scaling
map Sc (u) = A−1 (cA(u)). Replacing each aℓ , bm by Sc (aℓ ), Sc (bm ) multiplies all quadratic
coordinates by c, preserving interlacing and the residues Rℓ . If c > 1, strict monotonicity of
q increases Γr . Taking c ↓ 1 therefore approximates each tuple satisfying 2Γr = s by strictly
interlacing tuples with 2Γr > s whose dimension exponents converge to Φr . Taking the inﬁmum
over the tuples satisfying (82) and 2Γr ≥ s, and then over all ﬁnite hierarchy levels, proves the
second assertion of Theorem 1.2.                                                               □
  Deﬁne
                  κr (s) =               inf               Φr (a, b),         κ∞ (s) = inf κr (s).
                             a1 >b1 >···>br >ar+1 ≥0                                          r≥0
                                   2Γr (a,b)≥s
The quantity κr (s) is the best exponent obtained directly on the whole sphere at hierarchy level r.
By Theorem 1.2, approximating tuples with 2Γr = s by tuples with 2Γr > s bounds the whole-
sphere code exponent by κr (s). For any error tolerance, choose a ﬁnite level approximating




                                                             60
κ∞ (s) and keep that level ﬁxed as n → ∞. Thus
                                        1
                                 lim sup log2 A(n, s) ≤ κ∞ (s).
                                   n→∞  n
In particular, the hierarchy depth is ﬁxed before the dimension limit. We can further improve
a ﬁxed-angle bound by the spherical-cap reduction recalled in (10): restrict to a suﬃciently
populated spherical cap and project to a lower-dimensional sphere with inner-product threshold
0 ≤ t ≤ s. The spherical-slice inequality of Sidelnikov and Kabatianskii–Levenshtein [Sid74,
KL78], recalled in (10), charges the exponential cost 12 log2 ((1 − t)/(1 − s)) for restricting to the
cap and projecting to the smaller sphere. Applying this inequality at each ﬁxed hierarchy level
gives                                               
                                         1     1−t
                  κr (s) = inf κr (t) + log2            ,      κ∞ (s) = inf κr (s),               (89)
                          0≤t≤s          2     1−s                       r≥0
where κr (0) = 0. Consequently,
                                        1
                                 lim sup log2 A(n, s) ≤ κ∞ (s).
                                   n→∞ n
Thus κr is the exponent obtained directly on the whole sphere, and κr includes the additional
optimization over spherical caps.
7.2. Strict improvement at every hierarchy level. The direct and spherical-cap-optimized
exponents κr (s) and κr (s) are nonincreasing in r, since a level-r tuple is recovered as a limit
of level-(r + 1) tuples. We prove that both decrease strictly at every 0 < s < 1. The ﬁrst
comparisons isolate the intermediate harmonic-degree path (72): replacing the classical ﬁxed
line by the moving stabilizer space Hk (x⊥ ) gives one strict improvement, and allowing a second
ambient highest-weight coordinate gives another. Extending this argument to all hierarchy
levels requires controlling minimizing sequences whose coordinates escape to inﬁnity.
   For r = 0, Γ0 (a) = q(a) and Φ0 (a) = Hsph (a); the spectral boundary 2q(a0 (s)) = s recov-
ers the direct whole-sphere Kabatianskii–Levenshtein exponent Hsph (a0 (s)). The intermediate
one-row construction is the restriction a2 = 0 of level 1. By (11), its spectral quantity is
Γ1 ((a, 0), b) = Γrow (a, b), and its dimension exponent is Hsph (a) − Hsph (b). The optimized one-
row rate is                                                            
                               κrow (s) =    inf    Hsph (a) − Hsph (b) ,                      (90)
                                            a>b>0
                                         2Γrow (a,b)≥s
and its cap-optimized exponent κrow is obtained by replacing κr with κrow in (89).
   Two perturbations drive the strict improvements. Opening a zero terminal ambient coordi-
nate increases the spectral quantity and decreases the dimension exponent at the same level;
once that coordinate is positive, appending a stabilizer row gives the same improvements one
level higher.
Proposition 7.3. Fix 0 < s < 1 and r ≥ 0, and let a = (a1 , . . . , ar+1 ) and b = (b1 , . . . , br )
satisfy
                     a1 > b1 > a2 > · · · > br > ar+1 ≥ 0,     2Γr (a, b) ≥ s.
For r = 0, the interlacing condition reduces to a1 ≥ 0.
    (1) If r ≥ 1 and ar+1 = 0, there are strictly interlacing vectors a0 ∈ Rr+1 and b0 ∈ Rr with
        a0r+1 > 0 such that
                      2Γr (a0 , b0 ) > 2Γr (a, b) ≥ s,   Φr (a0 , b0 ) < Φr (a, b).
    (2) If ar+1 > 0, there are strictly interlacing vectors a0 ∈ Rr+2 and b0 ∈ Rr+1 with a0r+2 =
        0 < b0r+1 < a0r+1 such that
                   2Γr+1 (a0 , b0 ) > 2Γr (a, b) ≥ s,    Φr+1 (a0 , b0 ) < Φr (a, b).




                                                    61
Proof. Write Γ = Γr (a, b), Φ = Φr (a, b), and work in the quadratic coordinates xℓ , ym . For the
ﬁrst assertion, choose t > 0 small and open the zero terminal coordinate by setting
                                               
               e = a1 , . . . , ar , A−1 (t2 ) ,
               a                                                 e , b),
                                                     Γopen = Γr (a                         e , b).
                                                                               Φopen = Φr (a
Expanding (83) gives
                               Q
                                   ym
                   Γopen = Γ + Q m    t + O(t2 ),                Φopen = Φ + O(t2 log(1/t)).
                                      ℓ≤r xℓ

Replacing the zero terminal ambient coordinate by a                er+1 = A−1 (t2 ) therefore increases the
spectral quantity to ﬁrst order, while its direct contribution to the dimension exponent is smaller.
To turn this spare spectral gain into a strict reduction of the exponent, rescale all quadratic
coordinates simultaneously using Sc . Its entropy derivative is
                 d                                      u(1 + u)              1+u
                      Hsph (Sc (u))         = ψ(u) :=                  log2        ,      ψ(0) := 0.
              d log c                  c=1                1 + 2u                 u
With v = 1 + 2u, strict monotonicity follows from
                                         dψ                       v+1 2
                             4(log 2)          = (1 + v −2 ) log             − > 0.
                                          dv                      v−1 v
                                                  P             P
Hence the strict interlacing in (82) gives ℓ ψ(aℓ ) − m ψ(bm ) > 0. For suﬃciently small ﬁxed
η > 0, put c = 1 − ηt, a0ℓ = Sc (a      eℓ ), and b0m = Sc (bm ). This common contraction preserves a
positive spectral gain of order t while decreasing the dimension exponent by order t, proving
the ﬁrst assertion.
  For the second assertion, choose 0 < ε < ar+1 , and append a new stabilizer row and a zero
ambient row:
                    e = (a1 , . . . , ar+1 , 0),
                    a                                 e = (b1 , . . . , br , ε),
                                                      b                              e = A(ε).
Each existing interpolation weight becomes Rℓ            new   = Rℓ (1 − e/xℓ ), while the new zero node
contributes nothing to the spectral quantity. Write Γapp = Γr+1 (a                     e and Φapp = Φr+1 (a
                                                                                   e , b)                     e
                                                                                                          e , b).
Then
                                            X Rℓ q(aℓ )
                        Γapp = Γ − e                    ,       Φapp = Φ − Hsph (ε).
                                             ℓ
                                                   xℓ
Put
                                     X Rℓ q(aℓ )                        X Rℓ q(aℓ )
                             DΓ =                         > 0,     L=                 .
                                       ℓ
                                            2(1 + 4xℓ )                    ℓ
                                                                               xℓ
Under a common expansion of all quadratic coordinates, the logarithmic derivative of the orig-
inal spectral quantity Γ is DΓ . For ﬁxed θ > 0, choosing log c = (L/DΓ + θ)e and setting
          eℓ ), b0m = Sc (e
a0ℓ = Sc (a               bm ) more than restores the spectral loss eL, at dimension-exponent cost
O(e). Since e = O(ε) and Hsph (ε) = ε log2 (1/ε) + O(ε), the expanded level-(r + 1) tuple has
spectral quantity larger than Γ and dimension exponent smaller than Φ.                          □
  At level 1, these perturbations separate the classical construction, its one-row reﬁnement,
and the complete level-one construction; the same calculation supplies a boundary estimate for
the general argument.
Lemma 7.4. For every ﬁxed 0 < s < 1,
                  κ1 (s) < κrow (s) < κ0 (s),             κ1 (s) < κrow (s) < κ0 (s) = BKL (s).
Proof. Since increasing b decreases the one-row objective Hsph (a)−Hsph (b) in (90), the optimum
over b for ﬁxed a > a0 (s) lies on the spectral boundary b = Bs (a), where
                                     q                                  p
                                           1 + 4a(1 + a) − 2s(1 + 2a) a(1 + a) − 1
                      Bs (a) =                                               .
                                                     2
                            √
At a = a0 (s)+δ, Bs (a) = 21 1 − s2 δ+Os (δ 2 ). Since Hsph (u) = u log2 (1/u)+O(u), the boundary
objective is smaller than Hsph (a0 (s)) for suﬃciently small δ > 0. Thus κrow (s) < κ0 (s).




                                                           62
  As a → ∞, the boundary objective tends to − 12 log2 (1 − s), which is larger than Hsph (a0 (s)).
                        √
Indeed, set t = s/(1 + 1 − s2 ) ∈ (0, 1). Since s = 2t/(1 + t2 ) and a0 (s) = t2 /(1 − t2 ), the
diﬀerence, multiplied by log 2, is
                                          1                 2t2      1
                             log(1 + t) +   log(1 + t2 ) −        log .
                                          2                1−t  2    t
                                                    −1
The last term is smaller than t, since log(1/t) < (t − t)/2. The ﬁrst two terms are larger than
t: their diﬀerence from t vanishes at zero and has derivative t2 (1 − t)/((1 + t)(1 + t2 )) > 0. Thus
the one-variable minimization over a attains its inﬁmum at a ﬁnite interior point.                  
   Applying the ﬁrst part of Proposition 7.3 to the minimizing level-one tuple (a, 0), (Bs (a))
gives κ1 (s) < κrow (s).
   To justify optimization over spherical caps, put G(t, a) = Hsph (a) − Hsph (Bt (a)) for a ≥ a0 (t).
This function is continuous, including
                                     √ at a = a0 (t), where G(t, a0 (t)) = κ0 (t). The explicit
formula for Bt (a) gives Bt (a)/a → 1 − t, locally uniformly for 0 < t < 1. Hence
                                           1
                             G(t, a) −→ − log2 (1 − t)       (a → ∞),
                                           2
with the same local uniformity. The strict improvement over Hsph (a0 (t)) and the larger limiting
objective as a → ∞ therefore restrict all minimizing a to a common bounded interval [a0 (t), A]
for t in a suﬃciently small neighborhood of any ﬁxed t0 ∈ (0, 1). Parameterizing that interval
by a = a0 (t) + u(A − a0 (t)), 0 ≤ u ≤ 1, expresses κrow (t) as the minimum of a continuous
function on a ﬁxed compact interval. Thus κrow is continuous on (0, 1). Since
                                                                    
                         0 ≤ κrow (t) ≤ κ0 (t) = O t2 log(1/t)                 (t ↓ 0),
it extends continuously to t = 0 with value zero. The classical and one-row spherical-cap
objectives are consequently continuous on the compact interval [0, s] and attain their minima.
Neither minimum occurs at t = 0, since the slice cost decreases by t/(2 log 2) + O(t2 ), whereas
both code exponents increase by at most O(t2 log(1/t)). Applying κrow (t) < κ0 (t) and κ1 (t) <
κrow (t) at the minimizing thresholds for the classical and one-row spherical-cap objectives gives
the two cap-optimized inequalities.                                                             □
   The ﬁrst-level comparison above uses an attained one-row optimizer. At higher levels, Propo-
sition 7.3 improves each ﬁxed tuple, but this does not by itself give a strict inequality between
optimized exponents: an ambient coordinate and its interlacing stabilizer coordinate can diverge
together while their entropy diﬀerence remains bounded. The next lemma identiﬁes precisely
these noncompact limits.
Lemma 7.5. Fix r ≥ 0, and consider a sequence of strictly interlacing level-r tuples with
bounded exponents Φr . After passing to a subsequence, there are 0 ≤ j ≤ r, a strictly interlacing
level-j tuple (a, b), and 0 < c ≤ 1 such that
                                                                                          
                  Φr −→ Φj (a, b) − log2 c,        1 − 2Γr −→ c2 1 − 2Γj (a, b) .
If c < 1, then j < r. Conversely, this limiting datum is approximable at level j + 1 when c < 1
and at level j when c = 1.
Proof. Put f (x) = Hsph (A−1 (x)). This increasing function satisﬁes f (x) = 21 log2 x+log2 e+o(1)
as x → ∞. In the quadratic coordinates from (83), the exponent is a sum of nonnegative terms:
                                                   X
                                                   r
                                                                           
                                Φr = f (xr+1 ) +         f (xi ) − f (yi ) .
                                                   i=1
Thus xr+1 stays bounded, and every divergent xi has a divergent paired yi with yi /xi bounded
away from zero. After extracting a subsequence, the divergent pairs are i = 1, . . . , k, and
                                yi                                 Y
                                                                   k
                                   −→ αi ∈ (0, 1],            2
                                                             c =         αi .
                                xi                                 i=1




                                                   63
Take limits of the remaining ﬁnite coordinates and cancel coincident numerator and denominator
factors in the rational Stieltjes transform
                                           Qr
                                                 (z − yi )   X Ri
                                                             r+1
                                          i=1
                                  m(z) = Qr+1              =            .
                                             i=1 (z − xi )   i=1
                                                                 z − xi
Weak interlacing leaves a strictly interlacing level-j tuple with j ≤ r − k, and m(z) → c2 mj (z)
for z < 0. Consequently, on the compactiﬁed half-line, the residue measures converge to
                            X                    X     (j)
                                  Ri δxi −→ c2        Ri δx(j) + (1 − c2 )δ∞ .
                                                               i
                             i                   i
Since q(A−1 (x)) → 1/2 as x → ∞, integrating this function gives the asserted limit of Γr . The
asymptotic formula for f gives the corresponding limit of Φr . If c < 1, at least one pair diverges,
so j < r.
   Conversely, for c < 1, prepend the quadratic coordinates x = M and y = c2 M to the
level-j tuple and let M → ∞. If c = 1, no additional pair is required. Further levels can be
added without changing the limit by appending a stabilizer coordinate tending to zero and a
zero ambient coordinate; a zero terminal coordinate can ﬁrst be opened by an arbitrarily small
amount. At a positive spectral feasibility boundary, slightly decrease c when c < 1; when c = 1,
apply the common scaling Sd with d ↓ 1. Either perturbation makes the approximations strictly
feasible without changing their limiting exponent.                                               □
  The compactiﬁcation parameter c records precisely the spherical-cap cost. Indeed, if t =
2Γj (a, b) and s = 1 − c2 (1 − t), then − log2 c = 12 log2 ((1 − t)/(1 − s)), exactly the cost in
(89). The local perturbations can therefore be applied to the ﬁnite residual tuple to prove strict
improvement of the optimized exponents at every level.
Corollary 7.6. For every r ≥ 0 and 0 < s < 1,
                                 κr+1 (s) < κr (s),          κr+1 (s) < κr (s).
At level 1, moreover, κ1 (s) < κrow (s) < κ0 (s) and κ1 (s) < κrow (s) < κ0 (s) = BKL (s).
Proof. Appending vanishing rows shows that 0 ≤ κr (t) ≤ κ0 (t). A minimizing sequence for κr (s)
therefore has bounded exponent. Apply Lemma 7.5 to obtain a level-j tuple and 0 < c ≤ 1 with
                          κr (s) = Φj − log2 c,            c2 (1 − 2Γj ) ≤ 1 − s.
If its terminal ambient coordinate vanishes and j ≥ 1, the ﬁrst part of Proposition 7.3, applied
at the threshold 2Γj > 0, decreases Φj and increases Γj . Retaining c, the resulting datum is
approximable at level at most r, contradicting minimality. If j = 0 and the ambient coordinate
vanishes, then Γj = 0, so feasibility gives
                          Φj − log2 c ≥ − 12 log2 (1 − s) > κ0 (s) ≥ κr (s),
where the strict middle inequality was proved in the proof of Lemma 7.4. Hence the terminal
ambient coordinate is positive.
  The second part of Proposition 7.3 now produces a level-(j + 1) tuple with strictly smaller
exponent and strictly larger spectral quantity. Retain the factor c. If c = 1, this datum is
approximable at level j + 1 ≤ r + 1; if c < 1, it is approximable at level j + 2 ≤ r + 1. Its strict
spectral margin persists under approximation, proving κr+1 (s) < κr (s).
  The same compactiﬁcation shows that κr is lower semicontinuous on (0, 1): if sn → s, nearly
minimizing tuples have uniformly bounded exponents, and their limiting datum is feasible at s
and approximable at level at most r. At zero, 0 ≤ κr (t) ≤ κ0 (t) → 0. Therefore the inﬁmum
deﬁning κr (s) is attained on [0, s]. It is not attained at zero: as t ↓ 0,
                                                    1                     t
              κr (t) ≤ κ0 (t) = O t2 log(1/t) ,        log2 (1 − t) = −         + O(t2 ).
                                                     2                  2 log 2
Evaluating the ﬁrst strict inequality at the positive minimizing threshold proves κr+1 (s) < κr (s).
The ﬁrst-level comparisons are Lemma 7.4.                                                         □



                                                      64
                                     8. Sphere packings
   We now convert the spherical hierarchy into an upper bound for the maximal Euclidean
sphere-packing density ∆n . The upper-hemisphere comparison (91) bounds ∆n by the product
of a spherical-code size and an explicit spherical-cap volume factor. Unlike the coding problem,
where the separation threshold s is ﬁxed, the packing comparison allows us to optimize over s.
The resulting packing exponent balances the spherical-code exponent against the spherical-cap
volume exponent.
8.1. From spherical codes to sphere packings. We combine the upper-hemisphere compar-
ison (91) with the ﬁnite-level spherical-code bounds and show that spherical-cap optimization
does not further improve the angle-optimized packing exponent.
   For −1 < s < 1, Sidelnikov’s upper-hemisphere inequality [Sid74], in the normalization
of [CZ14, (2.1)], states that
                                              
                                          1 − s n/2
                                 ∆n ≤               A(n + 1, s).                         (91)
                                            2
The factor ((1 − s)/2)n/2 is the geometric cost of the upper-hemisphere comparison. Thus any
spherical-code exponent A(n, s) ≤ 2(B(s)+o(1))n gives
                                                 1      2
                                  ∆n ≤ 2(B(s)− 2 log2 1−s +o(1))n .                          (92)
At hierarchy level r, deﬁne the positive sphere-packing decay exponent γr obtained by optimizing
(92):                                                    
                                    1         2
                   γr = sup           log2       − κr (s)
                         0<s<1 2           1−s
                                                                                          (93)
                                                  1            2
                      =            sup              log2                − Φr (a, b) .
                         a1 >b1 >···>br >ar+1 ≥0 2       1 − 2Γr (a, b)
For a ﬁxed parameter tuple (a, b) satisfying (82), the packing objective 12 log2 (2/(1 − s)) −
Φr (a, b) increases with s up to the feasibility boundary s = 2Γr (a, b). Substitution at that
boundary gives the second formula in (93).
   For each ﬁxed s, we may ﬁrst choose a spherical-cap threshold 0 ≤ t ≤ s and use the cap-
optimized spherical-code exponent κ∞ (s) deﬁned in (89). Substituting the resulting estimate
A(n + 1, s) ≤ 2(κ∞ (s)+o(1))n into the upper-hemisphere inequality (91), and then optimizing the
resulting packing decay exponent over s, gives
                                                                   
                                               1        2
                                γ∞ = sup         log2       − κ∞ (s) .                        (94)
                                      0<s<1 2         1−s
The spherical-cap reduction does not improve the angle-optimized packing bound. Indeed,
changing the inner-product threshold from s to t incurs the spherical-slice exponent 12 log2 ((1 −
t)/(1 − s)), which cancels the change in the upper-hemisphere volume exponent:
                             1        2      1       1−t     1        2
                               log2        − log2          = log2       .
                             2      1−s 2            1−s     2     1−t
Consequently, substituting (89) into (94) gives
                                                                    
                                                1        2
                                 γ∞ = sup         log2      − κ∞ (t)
                                        0<t<1 2        1−t                                    (95)
                                    = sup γr .
                                     r≥0

Every level-r tuple satisfying (82) can be approximated at level r + 1 by appending br+1 = ε
and ar+2 = 0; if ar+1 = 0, ﬁrst replace it by a suﬃciently small positive number. Taking ε ↓ 0
gives γr+1 ≥ γr . Therefore γ∞ = supr γr = limr→∞ γr . Thus spherical-cap reduction improves
ﬁxed-angle code bounds but does not improve the fully angle-optimized packing exponent γ∞ .
In particular,
                                       ∆n ≤ 2−(γ∞ +o(1))n .




                                                 65
8.2. A relative-entropy upper bound. A relative-entropy identity, stated precisely in (101),
bounds every ﬁnite-level packing exponent by a common limiting threshold. The candidate
threshold is
                                             1      2π
                                        λ∗ = log2      .                                     (96)
                                             2       e
Throughout the following argument, log is natural and DKL denotes relative entropy.
   To bound every ﬁnite hierarchy level by λ∗ , we encode the interlacing quadratic coordinates
xℓ = A(aℓ ) and ym = A(bm ) by the union of [0, xr+1 ] and the intervals [ym , xm ]. The Stieltjes
transform K of the indicator of that union simultaneously records the spectral quantity Γr and
the dimension exponent Φr . Tilting an explicit reference probability measure by e−K identiﬁes
the gap between λ∗ and the packing objective with a nonnegative relative entropy.
Proposition 8.1. Fix r ≥ 0 and a parameter tuple satisfying (82), and set xℓ = A(aℓ ), ym =
A(bm ), and c = 1/4. Since the positive residues Rℓ sum to one and 0 ≤ 2q(aℓ ) < 1, put
                                          Z = 1 − 2Γr (a, b) > 0.
Deﬁne the interlacing indicator ξ, the associated Stieltjes transform K, two reference measures
ρ, ν, and the tilted measure ρK , with all measures supported on 0 < t < c:
                                                               X
                                                               r
                                 ξ(u) = 1[0,xr+1 ] (u) +             1[ym ,xm ] (u),              (97)
                                                               m=1
                                           Z ∞
                                           ξ(u)
                                K(t) =           du,                                              (98)
                                        0 t+u
                                          dt                                     dt
                                ρ(dt) = p         ,                ν(dt) = √         ,            (99)
                                       π t(c − t)                                c−t
                            ρK (dt) = Z −1 e−K(t) ρ(dt).                                         (100)
The measures ρ, ν, and ρK all have total mass one, and
                                                            
                            1            2                      DKL (νkρK )
                    λ∗ −      log2                − Φr (a, b) =             .                    (101)
                            2      1 − 2Γr (a, b)                 2 log 2
In particular, γr ≤ λ∗ for every r ≥ 0.
Proof. The interpolation weights Rℓ from (83) form a probability distribution on the poles
xℓ . The rational Stieltjes transform m(z) of that distribution has the equivalent product and
partial-fraction representations
                                             Y
                                             r
                                                   (z − ym )
                                                                     X
                                                                     r+1
                                                                           Rℓ
                                  m(z) = m=1                     =              .
                                          Y
                                         r+1
                                                                     ℓ=1
                                                                         z − xℓ
                                                   (z − xℓ )
                                             ℓ=1
Integrating (97) on each interlacing interval and then taking partial fractions gives
                                             t + xr+1   Xr
                                                                t + xm
                               K(t) = log             +     log        ,
                                                 t      m=1
                                                                t + ym
                                                                                                 (102)
                                             t    Yr
                                                      t + ym    X Rℓ
                                                                r+1
                               −K(t)
                           e           =                     =t            .
                                         t + xr+1 m=1 t + xm    ℓ=1
                                                                    t + xℓ
Put h(x) = (log 2)Hsph (A−1 (x)). Integrating h0 on [0, xr+1 ] and the interlacing intervals [ym , xm ]
gives                                         Z            ∞
                                       (log 2)Φr =             h0 (u)ξ(u) du.                    (103)
                                                       0
Both reference measures ρ and ν have mass one because c = 1/4. Diﬀerentiating h(x) =
(log 2)Hsph (A−1 (x)) gives
                                        1       1+a
                            h0 (x) =        log     , a = A−1 (x).
                                     1 + 2a      a

                                                       66
The substitutions t = c sin2 θ and t = c(1 − v 2 ), respectively, give
                                       r           Z c                                          Z c
                      −1          x                      x                               0        ν(dt)
               2q A (x) =             =                      ρ(dt),                  2h (x) =            .
                                 x+c                   0 x+t                                     0 x+t
By (102), (103), and Tonelli’s theorem,
                               Z c                                                  Z c
                       Z=              e−K(t) ρ(dt),        2(log 2)Φr =                  K(t)ν(dt).         (104)
                                   0                                                 0
The ﬁrst identity in (104) normalizes ρK . Dividing the two reference densities and applying the
same substitution t = c(1 − v 2 ) gives
                                        √       Z c
                             dν
                                 (t) = π t,         log t ν(dt) = −2.
                             dρ                  0
Consequently,
                     Z c                          
                             dν
     DKL (νkρK ) =        log (t) + K(t) + log Z ν(dt) = log π − 1 + 2(log 2)Φr + log Z.
                      0      dρ
Rearrangement and (96) give (101). Nonnegativity of relative entropy and (93) give γr ≤ λ∗ . □
Corollary 8.2. For every r ≥ 0,
                                                  γr < γr+1 < λ∗ .
Proof. Set c = 1/4, and for 0 ≤ x < ∞ deﬁne
                        Z c
                              t                         t
                I(x) =            ρ(dt),  fx (t) =             ,                               ρx = fx ρ.
                         0  t + x                  (t + x)I(x)
Include the endpoints by setting f0 = 1 and f∞ (t) = 2t/c. The second identity in (102) expresses
ρK as a probability mixture of at most r + 1 measures ρx . Conversely, a mixture with distinct
ﬁnite nodes xi and positive weights αi is obtained by choosing
                                              αi /I(xi )
                                       Ri = P              .
                                              j αj /I(xj )
             P
The zeros of i Ri /(z − xi ) strictly interlace its poles, giving a level-r tuple after approximation
or the addition of vanishing rows. Nodes at inﬁnity are obtained by approximation.
   The bounds
                               c                    c          t
                                        ≤ I(x) ≤        ,        ≤ fx (t) ≤ 4
                          4(c/2 + x)               c+x         c
show that relative entropy is continuous on the compact space of mixtures of at most r + 1
nodes in [0, ∞]. Indeed, |log t| is integrable against ν. Consequently, Proposition 8.1 gives, with
xi ∈ [0, ∞],
                                            1
                            γr = λ∗ −               min        DKL (νkgρ).
                                         2 log 2 g=Pr+1 αi fxi
                                                                  P
                                                                  i=1
                                                         αi ≥0,             αi =1
                           √                                            i

   Write h = dν/dρ = π t. The probability measure η(dx) = I(x)x−1/2 dx on (0, ∞) satisﬁes
                         Z ∞                Z ∞               √
                                                   t dx
                             fx (t) η(dx) =            √ = π t = h(t).
                          0                  0   t+x x
No ﬁnite mixture g equals h: if it contains
                                       √       a positive atom at zero, then g(0) > 0; otherwise,
g(t) = O(t) as t ↓ 0, whereas h(t) = π t. Thus the minimum relative entropy is positive, giving
γr < λ ∗ .                                                          R
   Let g minimize the relative entropy at level r, and put A(x) = 0c fx (t)g(t)−1 ν(dt). Then
                                       Z ∞                   Z c
                                                                h(t)2
                                             A(x) η(dx) =             ρ(dt) > 1,
                                       0                      0 g(t)




                                                            67
where strictness follows from Cauchy–Schwarz and g 6= h. Hence A(x) > 1 for some ﬁnite x > 0
distinct from the existing mixture nodes. Since fx /g ≤ c/(xI(x)), diﬀerentiation under the
integral is justiﬁed. For gε = (1 − ε)g + εfx ,
                                d
                                   DKL (νkgε ρ)     = 1 − A(x) < 0.
                                dε              ε=0
This level-(r + 1) mixture has smaller relative entropy, proving γr+1 > γr .              □

                                                     Classical KL         One-row         Level r = 1     Level r = 2   Level r = 3



                              Finite-level deficit from λ * = 12 log2 (2π/e)
                       10−1


                       10−2
 Deficit λ * − G(s)




                       10−3


                       10−4


                       10−5



                                                   0.2                          0.4                       0.6                    0.8
                                                                                        Inner product s


                              Figure 4. Finite-level deﬁcits from the limiting sphere-packing exponent. For
                              the classical, one-row, and level-r certiﬁcate families with 1 ≤ r ≤ 3, the curves
                              show λ∗ − GF (s) on a logarithmic scale, where GF is the packing objective in
                              Figure 1. Circles mark the numerically estimated optimizing angles, and the
                              dotted line marks s = 1/2. The exact hierarchy limit is proved in Theorem 8.3.

8.3. A sharp Chebyshev construction. Corollary 8.2 shows that the ﬁnite-level exponents
increase strictly while remaining below λ∗ . To show that their limit equals this threshold, we
form interlacing parameter tuples from Chebyshev roots and critical points. The resulting
sphere-packing bound agrees with the full-space companion in Chapter 1, but is obtained here
entirely from spherical certiﬁcates.
Theorem 8.3. The spherical hierarchy attains the threshold
                                                   1     2π
                             lim γr = γ∞ = λ∗ = log2        .
                            r→∞                    2      e
Consequently,
                                   ∆n ≤ 2−(λ∗ +o(1))n .                                                                                (105)
Proof. By Corollary 8.2, every ﬁnite-level exponent satisﬁes γr < λ∗ . To obtain matching
exponents from below, ﬁx R > 0, set N = r + 1, and choose the roots and critical points of a
Chebyshev polynomial shifted from [−1, 1] to [0, R]. The roots and critical points, for 1 ≤ ℓ ≤ N
and 1 ≤ m < N , respectively, are
                                                                                  
                        R                (2ℓ − 1)π                R              mπ
                  xℓ =        1 + cos                ,   ym =            1 + cos       .             (106)
                        2                   2N                     2              N
The roots xℓ and the critical points ym strictly interlace. If QN is the monic shifted Chebyshev
polynomial with roots x1 , . . . , xN , then Q0N has roots y1 , . . . , yN −1 . The logarithmic derivative
of QN therefore gives
                                                           −1
                                                          NY
                                                                    (z − ym )
                                                          m=1                          Q0N (z)   1 XN
                                                                                                         1
                                                                                =              =              .
                                                           Y
                                                           N                          N QN (z)   N ℓ=1 z − xℓ
                                                                    (z − xℓ )
                                                            ℓ=1



                                                                                         68
Comparing this partial-fraction expansion with the residues in (83) shows that every interpo-
lation weight is Rℓ = 1/N . Put aℓ = A−1 (xℓ ) and bm = A−1 (ym ). For t > 0, the interlacing
indicator ξN and its Stieltjes transform KN are
                                         X
                                         N −1                                Z R
                                                                                   ξN (u)
               ξN (u) = 1[0,xN ] (u) +          1[ym ,xm ] (u),   KN (t) =                du.
                                         m=1                                  0    t+u
By (104),
                                                                     s
                                                       1 XN
                                                                            xℓ
                          ZN = 1 − 2ΓN −1 (a, b) = 1 −
                                                       N ℓ=1             xℓ + 1/4
                                 Z 1/4
                                                  dt
                             =        e−KN (t) p           .
                                  0           π t(1/4 − t)
Under u = R2 (1 + cos θ), the critical points and the endpoints θ = 0, π divide (0, π) into the
N equal intervals ((m − 1)π/N, mπ/N ). Each interval contains one root at its midpoint, and
ξN selects exactly half of the interval. The change of variables contributes the Jacobian R2 sin θ.
Averaging against continuous test functions and then using their density in L1 (0, R) gives weak-*
convergence in L∞ (0, R). Explicitly,
                    Z R                           Z
                                            1 R
                 lim      f (u)ξN (u) du =       f (u) du   for every f ∈ L1 (0, R).
                N →∞ 0                      2 0
Since h0 (u) = O(log(1/u)) as u ↓ 0, both h0 and u 7→ (t + u)−1 belong to L1 (0, R) for every ﬁxed
t > 0. Therefore, (98) and (103) give
                                                      1   t+R
                                          KN (t) −→ log         ,                            (107)
                                                      2     t
                                                      1
                                    (log 2)ΦN −1 −→ h(R).
                                                      2
Since 0 ≤ e  −K N  ≤ 1, dominated convergence gives
                                    Z 1/4 s
                                                   t         2          1
                     ZN −→ ZR =                       ρ(dt) = arcsin √        .                 (108)
                                         0        t+R        π         4R + 1
Taking N → ∞ with R ﬁxed gives
                                                      log(2/ZR ) − h(R)
                                  lim inf γr ≥                          .                       (109)
                                   r→∞                      2 log 2
As R → ∞,
                                1 + o(1)              1
                          ZR =     √     ,    h(R) = log R + 1 + o(1),
                                  π R                 2
so the right side of (109) tends to λ∗ . Together with the ﬁxed-level upper bound and (95), this
proves the threshold identity.
   For ε > 0, choose successively R, a ﬁnite r, and s < 2Γr whose packing exponent exceeds
λ∗ − ε. Keep these parameters ﬁxed. Then Theorem 1.2 and (91) give
                                           1
                                   lim sup log2 ∆n ≤ −λ∗ + ε.
                                     n→∞ n
Taking n → ∞ before ε ↓ 0 proves (105).                                                       □

       Appendix A. Orthogonal representations and asymptotic dimensions
   The spherical arguments in §§6 and 7 require two representation-theoretic inputs. The
coordinate-transition formulas give Proposition 6.1 and the ﬁnite spherical-code bound in The-
orem 6.2. The uniform representation-dimension estimates give (87) and (88), which enter the
proof of the main spherical bound in Theorem 1.2.
   The spherical transition graph has vertices given by ambient SO(n)-representations contain-
ing a ﬁxed representation of the point stabilizer SO(n − 1), and its edges come from multiplica-
tion by a coordinate. The ambient and stabilizer spaces are described in §5.3. §A.1 identiﬁes the


                                                        69
possible vertices and edges, and §A.2 derives the common transition formula (76), its full-graph
normalization (77), and its dimension-weighted balance (78). These are the three conclusions
of Proposition 6.1. Finally, §A.3 gives the exact Weyl dimensions and proves the uniform esti-
mates in Lemma A.1, which determine the dimension ratio in (80). Throughout, the number
of nonzero highest-weight coordinates stays ﬁxed as n increases.
   For the standard orthogonal-group conventions and formulas, see Kravchuk [Kra18, §§2.1–
2.3 and App. B]. There, (2.18)–(2.21) give multiplicity-free restriction; (B.2) and its boundary
correction give the tensor product; (B.3)–(B.4) specify shifted weights; (B.5)–(B.6) give Weyl
dimensions; and (B.11)–(B.13) give coordinate-multiplication coeﬃcients. Source equation num-
bers below refer to this citation.
A.1. Stable tensor conventions. The vertices of the spherical graph are determined by the
orthogonal-group restriction rule (74); its possible edges are determined by tensoring with the
standard representation. We ﬁrst record the labeling and tensor conventions needed for both in-
puts. As in §5.3, the ambient rotation group is SO(n), and the stabilizer of a point of the sphere
is SO(n − 1). We call representations of SO(n) ambient representations and representations of
its point-ﬁxing subgroup stabilizer representations.
   Fix r ≥ 0 and n ≥ 2r + 4, and retain ambient representations with at most r + 1 nonzero
rows and stabilizer representations with at most r nonzero rows. The remaining highest-weight
coordinates, called the zero tails, all vanish. Because at least one such coordinate remains, these
representations avoid the exceptional splitting that can occur when a Young diagram reaches
the ﬁnal orthogonal-group weight coordinate. In this stable range, their irreducible tensor
representations are indexed by dominant integral highest weights: weakly decreasing sequences
of nonnegative integers whose nonzero entries are the row lengths of the corresponding Young
diagram. Write the ambient and stabilizer weights, respectively, as
                      λ = (λ1 , . . . , λr+1 , 0, . . .),        µ = (µ1 , . . . , µr , 0, . . .).
  The restriction of the ambient representation Vλ to SO(n − 1) contains the stabilizer repre-
sentation Eµ exactly when their row lengths interlace as in (74):
                                λ1 ≥ µ1 ≥ λ2 ≥ · · · ≥ µr ≥ λr+1 ≥ 0.
Each such stabilizer representation occurs with multiplicity one. The rotation-equivariant co-
ordinate maps in (54) are obtained by tensoring with the standard SO(n) representation Rn ,
of highest weight (1, 0, . . . , 0). The tensor-product formula (B.2) therefore gives the possible
coordinate transitions λ ↔ λ ± eℓ , provided the target weight remains dominant and still inter-
laces µ. Although the odd-dimensional tensor-product formula initially appears to contain an
additional same-weight term, its zero-tail boundary correction removes that term. Hence these
transitions are precisely the edges of the graph in §6.
A.2. Cancellation of the parity-dependent factors. §A.1 identiﬁes the possible directed
edges λ → λ ± eℓ . Their squared coordinate coeﬃcients are the quantities pℓ,± = |cℓ,± |2 in
Proposition 6.1, normalized by the unit base-point coordinate and the isometric embeddings in
(54). Kravchuk’s (B.12) and (B.13) give these coeﬃcients separately for odd and even ambient
dimensions. Factors belonging to zero highest-weight coordinates cancel in both expressions,
yielding the common formula (76). Parseval then gives (77), and the Weyl dimension formula
gives (78). As explained in §5.3, the Spin(n) formulas apply unchanged to integral SO(n) tensor
representations.
   In Kravchuk’s notation, the highest weights mn , mn−1 , and mn (±ℓ) correspond to λ, µ, and
λ±eℓ , respectively. Kravchuk’s coordinate-multiplication formulas use shifted weights, obtained
by adding the conventional dimension-dependent oﬀsets to the highest-weight coordinates. In
the notation of (75), put
                         n                        n−1                   n
              Lℓ = λℓ + − ℓ,         M m = µm +         − m,     ρn,r = − r − 1.           (110)
                         2                         2                    2




                                                            70
The variables xd,j in (B.3)–(B.4) satisfy
                                            n = 2N + 1 n = 2N
                                  xn,ℓ        Lℓ − 12    Lℓ
                                xn−1,m         Mm      Mm − 12 .
To interpret Kravchuk’s coordinate coeﬃcients, the multiplicity-free branching formulas (2.18)–
(2.21), applied successively along SO(n) ⊃ SO(n − 1) ⊃ · · · ⊃ SO(2) give the orthonormal
Gelfand–Tsetlin basis: its basis vectors are indexed by a sequence of interlacing highest weights,
one for each group in the chain. Choose SO(n − 1) to ﬁx the coordinate line Re1 . The symbol
• in (B.11)–(B.13) selects this ﬁxed one-dimensional summand in Rn ↓SO(n−1) = Re1 ⊕ e⊥         1.
The squared coeﬃcient for this ﬁxed summand is exactly the directed transition weight pℓ,±
associated with (54); no additional coordinate normalization is required.
   First suppose the ambient dimension is odd, n = 2N + 1. Write L = Lℓ for the shifted active
coordinate in (110). Squaring the odd-dimensional coordinate coeﬃcient (B.12) gives
                                            Y
                                            N
                                                                         
                                                    (L ± 21 )2 − Mm
                                                                  2

                                            m=1
                                pℓ,± =                                           .          (111)
                                                             Y
                                                             N
                                         2L(L ± 12 )             (L2 − L2q )
                                                             q=1
                                                             q6=ℓ

Put A = N − r − 1, so ρn,r = A + 21 . For r + 1 ≤ m ≤ N and r + 2 ≤ q ≤ N , the zero tail gives
                                                          1
                            Mm = N − m,          Lq = N + − q.
                                                          2
The trailing numerator and denominator factors cancel as
                     QN                                
                       m=r+1 (L ± 2 ) − Mm
                                    1 2     2
                                                       1
                              Q                 =L± A+     = L ± ρn,r .
                     (L ± 21 ) Nq=r+2 (L − Lq )
                                        2   2          2
Empty products are 1. Substitution into (111) leaves only numerator indices m ≤ r and
denominator indices q ≤ r + 1.
   The odd-dimensional Pieri formula in (B.2) appears to contain a copy of Vλ itself. However,
its boundary correction applies because N ≥ r + 2 and the ﬁnal highest-weight coordinate λN is
zero. Decreasing that zero coordinate gives a reﬂected weight representing the same SO(2N +1)
representation; the correction subtracts the repeated term. Consequently,
                                                                        
                              HomSO(2N +1) Vλ , R2N +1 ⊗ Vλ = 0.
Hence coordinate multiplication has no transition from Vλ back to itself. On the zero-tail
boundary λN = 0, the coeﬃcient in (B.11) has the indeterminate form 0/0, so the remaining
transitions must be determined from the corrected tensor decomposition.
   Now suppose the ambient dimension is even, n = 2N , and again write L = Lℓ . Squaring the
even-dimensional coordinate coeﬃcient (B.13) gives
                                             −1
                                            NY
                                                                         
                                                    (L ± 21 )2 − Mm
                                                                  2

                                 pℓ,± = m=1                                  .              (112)
                                                    Y
                                                    N
                                                2        (L2 − L2q )
                                                    q=1
                                                    q6=ℓ
Put A = N − r − 2, so ρn,r = A + 1. For r + 1 ≤ m ≤ N − 1 and r + 2 ≤ q ≤ N , the zero tail
gives
                                       1
                            Mm = N − − m,         Lq = N − q.
                                       2




                                                        71
The numerator factors for Mm and the denominator factors for Lq cancel according to
                         QN −1                           
                           m=r+1 (L ± 2 ) − Mm
                                       1 2    2
                                                                  L ± (A + 1)   L ± ρn,r
                            QN                               =                =          .
                              q=r+2 (L − Lq )                          L           L
                                      2    2

Substitution into (112) shows that both parities give
                                                         Y
                                                         r
                                                                                        
                                          (Lℓ ± ρn,r )            (Lℓ ± 21 )2 − Mm
                                                                                 2

                                                         m=1
                                 pℓ,± =                                                     .
                                                          Y
                                                          r+1
                                                   2Lℓ      (L2ℓ − L2q )
                                                       q=1
                                                       q6=ℓ

The common odd- and even-dimensional expression is (76). If the row lengths of λ ± eℓ are not
weakly decreasing or fail (74), there is no target representation containing Eµ , and the transition
probability is zero. Applying Parseval to the orthogonal irreducible projections of ℓx ⊗ φλ,x Y ,
whose squared norm is kY k2 , gives the full-graph normalization (77). On every existing edge,
(113) gives
                                   Dn (λ + eℓ )       pℓ,+ (λ; µ)
                                                =                    .
                                     Dn (λ)        pℓ,− (λ + eℓ ; µ)
Equivalently, Dn (λ)pℓ,+ (λ; µ) = Dn (λ + eℓ )pℓ,− (λ + eℓ ; µ). Thus weighting each transition by
the dimension of its source makes the forward and reverse directions equal. This is (78), and
hence veriﬁes the reciprocity assumption (55) used to construct the symmetric spherical graph.
A.3. Weyl dimensions. The transition calculation gives the spectral constraint in Proposi-
tion 6.1, but the spherical-code bound (80) also contains the ratio between the total ambient
dimension and the dimension of the common stabilizer space. We record exact formulas for
both dimensions and establish the uniform exponential estimates stated in Lemma A.1.
   Write Dn (λ) = dim Vλ . For a dominant integral highest weight λ with at most r + 1 nonzero
rows, Weyl’s dimension formula [GW09, §7.1.2] simpliﬁes to
                               Y
                               r+1
                                   2λi + n − 2i (λi + n − i − r − 2)! (r + 1 − i)!
                   Dn (λ) =
                               i=1
                                      n − 2i      (n − i − r − 2)! (λi + r + 1 − i)!
                                                                                                            (113)
                                      Y      (λi − λj + j − i)(λi + λj + n − i − j)
                               ×                                                    .
                                   1≤i<j≤r+1
                                                       (j − i)(n − i − j)
Formula (113) is the zero-tail specialization of (B.5)–(B.6). If r ≥ 1, substituting (n, λ, r) 7→
(n − 1, µ, r − 1) gives the stabilizer dimension dim Eµ . If r = 0, the stabilizer representation is
trivial and has dimension 1, and we write Dn−1 (0) = 1. The corresponding exponential rates
are expressed using the spherical entropy Hsph deﬁned in (9).
Lemma A.1. Fix r ≥ 0 and A < ∞, and assume n ≥ 2r + 4. Uniformly over dominant
integral ambient weights λ = (λ1 , . . . , λr+1 , 0, . . .) and stabilizer weights µ = (µ1 , . . . , µr , 0, . . .)
with 0 ≤ λi , µj ≤ An,
                                           X
                                           r+1                                               
                           1                        λi                              log(n + 2)
                             log2 Dn (λ) =     Hsph                    + Or,A                  ,
                           n               i=1
                                                    n                                   n
                                          Xr                                                 
                        1                          µj                               log(n + 2)
                          log2 Dn−1 (µ) =     Hsph                     + Or,A                  .
                        n                 j=1
                                                   n                                    n
                                                                                                     P
In particular,
    P
               if λi /n → ai and µj /n → bj , the dimension exponents converge to                      i Hsph (ai )
and j Hsph (bj ), respectively.
Proof. Apply uniform Stirling to the ﬁnitely many factorials in (113). Dominance bounds every
active diﬀerence between 1 and Or,A (n), so all remaining factors contribute Or,A (log(n + 2)),
including on chamber walls and at zero rows. For r ≥ 1, the stabilizer estimate follows identically
in dimension n − 1; for r = 0, it is the identity log2 dim E0 = 0.                               □


                                                             72
                      Appendix B. The spherical-to-Euclidean limit
   The companion paper in Chapter 1 analyzes the Cohn–Elkies sphere-packing linear program
directly in Euclidean space, proving both a universal bound for its Fourier-positive auxiliary
functions satisfying the required normalization and sign conditions and a matching construc-
tion. Neither argument requires the spherical hierarchy developed here. Nevertheless, the two
approaches share more than their ﬁnal exponent: several objects in the Euclidean construction
arise naturally when the inner-product threshold s of our spherical certiﬁcates tends to 1.
   Cohn and Zhao’s upper-hemisphere construction gives the correspondence between spherical
certiﬁcates and Euclidean Cohn–Elkies auxiliary functions [CZ14, Thm. 3.4 and subsequent dis-
cussion]. We recall the resulting change of scale, then identify the probability measure governing
the optimal spherical hierarchy with the limiting measure in the companion’s Euclidean argu-
ment. The limiting spherical potential also recovers the principal weight in its Mellin-transform
construction. The companion uses a second, smaller weight to control its Fourier estimates;
that additional correction has no spherical counterpart here.
B.1. The upper-hemisphere correspondence. Let gs (t) be a positive-deﬁnite spherical cer-
tiﬁcate on Sd , nonpositive for t ≤ s, and let gs,0 > 0 be its constant Gegenbauer coeﬃcient.
Set                         s
                                2                   q        
                     Ls =          ,     π(u) = u, 1 − |u|2 (|u| < 1).
                              1−s
For a nonzero nonnegative radial cutoﬀ supported in the radius-Ls ball, η ∈ Cc∞ (BLd s ), the
Cohn–Zhao upper-hemisphere construction [CZ14, Thm. 3.4 and subsequent discussion] gives
the Euclidean function
                              Z
                                                                                           
                   fs (x) =         η(z + 2x)η(z) gs hπ((z + 2x)/Ls ), π(z/Ls )i dz.
                               Rd
The integrand is zero unless both arguments of η belong to its support. Rotational invariance
makes fs a radial Schwartz function, and positive deﬁniteness of gs gives fbs ≥ 0. If |x| ≥ 1, the
spherical inner product in the integrand is at most 1 − 2|x|2 /L2s ≤ s, so fs (x) ≤ 0. Thus fs is a
Euclidean Cohn–Elkies auxiliary function. Centering a Gram factorization of gs gives
                              fs (0) = gs (1)kηk22 ,          fbs (0) ≥ 2−d gs,0 kηk21 .
Taking cutoﬀs approaching the indicator of BLd s therefore gives [CZ14, Thm. 3.4 and subsequent
discussion]
                                                 
                                            1 − s d/2 gs (1)
                                   LPd ≤                     .
                                              2         gs,0
In particular, Ls → ∞ as s ↑ 1, giving the Euclidean scaling used below.
B.2. The limiting hyperbolic measure. The spherical and Euclidean optimality arguments
each single out a probability measure. To compare them, we ﬁrst describe how the spherical
measure arises from the interlacing Chebyshev construction in the proof of Theorem 8.3. Fix
T > 0, and let x1 , . . . , xN and y1 , . . . , yN −1 be, respectively, the roots and critical points of
the shifted Chebyshev polynomial on [0, T ], as in (106). These two sets of nodes interlace.
The indicator ξN selects the alternating intervals between them, and its Stieltjes transform KN
converts
     p those intervals into the exponential tilt of the reference probability measure ρ(dt) =
dt/(π t(1/4 − t)) on (0, 1/4):
                                          X
                                          N −1
                ξN (v) = 1[0,xN ] (v) +          1[ym ,xm ] (v),
                                          m=1
                          Z T                                 1/4           Z
                            ξN (v)
              KN (t) =             dv,               ZN =         e−KN (t) ρ(dt).
                         0 t+v                              0
Here t ∈ (0, 1/4) is the spectral variable on which ρ is supported, ZN normalizes the tilted
measure in (100), and the hierarchy level is N − 1. Keeping T ﬁxed and letting N → ∞, (107)



                                                         73
and (108) give
                                1     t+T              2            1
                           KT (t) =
                                  log     ,      ZT = arcsin √           .
                                2      t               π          4T + 1
The limiting feasible inner-product threshold is sT = 1 − ZT , so
                                                       s
                                    1                    2      √
                        1 − sT ∼ √ ,         LT =             ∼ 2π T 1/4 .
                                  π T                 1 − sT
In particular, increasing T realizes the small-angle limit sT ↑ 1.
   The reference probability measures ρ and ν were introduced in (99). The relative entropy of
ν from the tilted measure controls the gap to the optimal packing exponent in (101). To identify
ν with the Euclidean limiting measure, change from the bounded spectral variable t ∈ (0, 1/4)
to the unbounded hyperbolic coordinate a > 0 deﬁned by
                                               1
                                          t = sech2 a.                                    (114)
                                               4
Under this change of variables, the reference and target measures in (99) are
                                    2
                           ρ(dt) = sech a da,       ν(dt) = sech2 a da.                   (115)
                                    π
The tilted probability measure ρKT from (100) then has density
                                     2       sech a
                       ρKT (da) =       p                 da −→ sech2 a da.
                                   πZT 1 + 4T cosh2 a
                                                                              √
The convergence holds in total variation by dominated convergence and πZT T → 1.
   The Euclidean lower-bound argument in Chapter 1, Section 3.1 obtains its corresponding
probability measure from the Poisson kernel of a complex strip. If u ∈ R denotes the rescaled
Mellin frequency, the limiting measure is
                                                   
                                        π     2 πu
                             p(u) du = sech            du,     u ∈ R.
                                        4         2
The pushforward of p(u) du under a = π|u|/2 is exactly sech2 a da. Thus the target probability
measure in the spherical relative-entropy bound and the measure in the Euclidean lower bound
coincide in hyperbolic coordinates. The hyperbolic densities in (115) also give
                         dν        π
                            (a) = sech a,      DKL (νkρ) = log π − 1,
                         dρ        2
        R∞
since   0    sech2 a log cosh a da = 1 − log 2.
B.3. The limiting Mellin weight. The common probability measure identiﬁes the spherical
and Euclidean optimality arguments at the distributional level. We now give a stronger cor-
respondence: the limiting spherical potential determines the principal weight in the Euclidean
construction in Chapter 1, Section 4.1.                              R
   For a radial proﬁle g(r), its Mellin transform is Mg (ζ) = 0∞ g(r)rζ−1 dr. In dimension d, put
λ = d/2 and Xg (τ ) = Mg (λ − iτ ). On this symmetry line, the Mellin–Fourier identity is given
in Chapter 1, Section 2.2:
                                                                        Γ((λ − iτ )/2)
                      Xbg (τ ) = mλ (τ )Xg (−τ ),        mλ (τ ) = π iτ                .
                                                                        Γ((λ + iτ )/2)
The common envelope in the companion construction is
                                                           
                                                     λ − iτ
                               Eλ (τ ) = π iτ /2 Γ            exp (λhϵ (τ /λ)) .
                                                       2
If hϵ is even, then mλ (τ )Eλ (−τ ) = Eλ (τ ), so the modiﬁcation by hϵ preserves Fourier reﬂection;
see Chapter 1, Section 4.1. It is assembled from oscillations cos(az), where z = τ /λ and a > 0
is an oscillation scale, not a spatial radius. The oscillation weight occupies two disjoint intervals
of scales: its principal negative interval determines the sharp packing exponent, whereas a




                                                  74
smaller positive interval controls the global Fourier estimates. Only the negative interval has a
counterpart in the limiting spherical potential.
   Under the hyperbolic change of variables (114), the potential KT diverges by an additive
constant as T → ∞. Subtract this constant:
                                                                             
                 f              1             1             1                 1
                KT (a) = KT       sech a − log(4T ) = log cosh a +
                                       2                               2
                                                                                  .
                                4             2             2                4T
It follows that
                      fT (a) −→ K∞ (a) = log cosh a,
                      K                                     e−K∞ (a) = sech a.              (116)
   More precisely, the Euclidean construction modiﬁes the logarithm of its Mellin proﬁle by the
even function                            Z ∞
                                                               
                               hϵ (z) =      wϵ (a) cos(az) − 1 da.
                                            0
Here the rescaled frequency z may be complex. Fix suﬃciently small ϵ > 0, and put
                           Iϵ = [ϵ2 , log(1/ϵ)],        bϵ (a) = 1 − 2ϵ(1 + a).
The principal negative part of the oscillation weight is
                                                bϵ (a)e−2a
                                    wϵ,− (a) = −           1I (a).
                                                2a2 cosh a ϵ
The companion supplements this negative part with an exponentially smaller positive correction
on a distant scale interval. That correction controls its global Fourier estimates without aﬀecting
the limiting radius; see Chapter 1, Sections 4.1–4.2.
  To recover the negative weight wϵ,− from the spherical potential, deﬁne the ﬁnite-cutoﬀ weight
                                           bϵ (a)e−2a −K e
                                wϵ,T (a) = −          e T (a) 1Iϵ (a).
                                               2a2
For each ﬁxed ϵ > 0, (116) gives wϵ,T → wϵ,− uniformly on Iϵ . Thus the principal weight of the
full-space construction is an exponential tilt of the limiting spherical Stieltjes potential.
   As ϵ ↓ 0, the intervals Iϵ increase to (0, ∞), and bϵ (a) → 1 at each ﬁxed a > 0. Thus the
principal negative weight converges pointwise to w∗ (a) = −e−2a−K∞ (a) /(2a2 ), and its limiting
Mellin modiﬁcation is
                                      Z
                                    1 ∞ e−2a−K∞ (a)                  
                           h∗ (z) =              2
                                                        1 − cos(az) da.
                                    2 0         a
The integral converges locally uniformly on {z ∈ C : | Im z| < 3}. At the limiting radius-
determining parameter u = 1, the contribution of w∗ to the logarithm of the radius is
                          Z ∞                                  Z ∞
                                                           1         e−2a tanh a
                                w∗ (a)a sinh a da = −                            da.         (117)
                           0                               2   0          a
The expansion
                                                ∞
                                                X
                                e−2a tanh a =         e−(4j+2)a (1 − e−2a )2
                                                j=0
has nonnegative summands, so Tonelli’s theorem permits termwise integration. For u, v > 0,
the elementary integral identity
                                     Z ∞
                                           e−ua − e−va          v
                                                       da = log
                                      0         a               u
then gives Wallis’s product:
                     Z ∞                        Y∞
                           e−2a tanh a                  (2j + 2)2         π
                                       da = log                      = log .
                      0         a               j=0
                                                    (2j + 1)(2j + 3)      2
The companion’s Fourier-pair theorem in Chapter 1, Theorem 4.1 constructs radial Schwartz
functions f− , f+ and an exterior radius Rϵ,d such that fb− = f+ > 0, f− (0) = f+ (0) > 0, and




                                                      75
f− (x) < 0 whenever |x| ≥ Rϵ,d . In its radius formula, the principal negative weight contributes
(117), whereas the positive correction vanishes in the limit. Consequently,
                                                               
                                    Rϵ,d      1          1    π      1
                          lim lim √ = √ exp − log                 = .
                           ϵ↓0 d→∞     d      2π         2    2      π
                                                                   1/d       p
If vd denotes the volume of the unit ball in Rd , then vd                ∼       2πe/d. Thus we recover the same
Cohn–Elkies density rate as (105):
                                                           r
                                            1/d Rϵ,d    e
                                   lim lim vd        =     = 2−λ∗ .
                                    ϵ↓0 d→∞   2        2π
   Thus the spherical construction recovers both the target probability measure and the principal
oscillation weight in the companion’s optimal full-space construction. This identiﬁes limiting
objects, without asserting that ﬁnite-dimensional spherical certiﬁcates converge to a particular
Euclidean auxiliary function. The order of limits also matters: the dimension ﬁrst tends to
                                                                         √ T , and ﬁnally T → ∞
inﬁnity at ﬁxed hierarchy level, the hierarchy level then increases at ﬁxed
forces sT ↑ 1. If the last two limits are taken jointly, choosing N/ T → ∞ retains every
ﬁxed neighborhood of the zero endpoint of the interlacing interval, since the smallest shifted
Chebyshev node satisﬁes
                                                          
                                     T                 π            π2T
                                xN =          1 − cos          ∼         −→ 0.
                                     2                2N           16N 2
                                                References
[AJCHLT20] N. Afkhami-Jeddi, H. Cohn, T. Hartman, D. de Laat, and A. Tajdini, High-dimensional sphere
           packing and the modular bootstrap, J. High Energy Phys. 12 (2020), article 066, doi:10.1007/
           JHEP12(2020)066.
[BV08]     C. Bachoc and F. Vallentin, New upper bounds for kissing numbers from semideﬁnite programming,
           J. Amer. Math. Soc. 21 (2008), 909–924, doi:10.1090/S0894-0347-07-00589-9.
[BN06]     A. Barg and D. Nogin, Spectral approach to linear programming bounds on codes, Problems Inform.
           Transmission 42 (2006), 77–89, doi:10.1134/S0032946006020025.
[Bas65]    L. A. Bassalygo, New upper bounds for error correcting codes, Problems Inform. Transmission 1
           (1965), no. 4, 32–35.
[BCV23]    P.-A. Bernard, N. Crampé, and L. Vinet, Entanglement of free fermions on Johnson graphs, J.
           Math. Phys. 64 (2023), no. 6, article 061903, doi:10.1063/5.0099879.
[CST08]    T. Ceccherini-Silberstein, F. Scarabotti, and F. Tolli, Harmonic Analysis on Finite Groups: Repre-
           sentation Theory, Gelfand Pairs and Markov Chains, Cambridge Studies in Advanced Mathematics,
           vol. 108, Cambridge University Press, Cambridge, 2008, doi:10.1017/CBO9780511619823.
[CD25]     A. Chailloux and T. Debris-Alazard, New solutions to Delsarte’s dual linear programs, IEEE Trans.
           Inform. Theory 71 (2025), no. 1, 297–316, doi:10.1109/TIT.2024.3476974.
[CE03]     H. Cohn and N. Elkies, New upper bounds on sphere packings. I, Ann. of Math. (2) 157 (2003),
           689–714, doi:10.4007/annals.2003.157.689.
[CKMRV17] H. Cohn, A. Kumar, S. D. Miller, D. Radchenko, and M. S. Viazovska, The sphere packing problem
           in dimension 24, Ann. of Math. (2) 185 (2017), 1017–1033, doi:10.4007/annals.2017.185.3.8.
[CZ14]     H. Cohn and Y. Zhao, Sphere packing bounds via spherical codes, Duke Math. J. 163 (2014), 1965–
           2002, doi:10.1215/00127094-2738857.
[CJJ22]    L. N. Coregliano, F. G. Jeronimo, and C. Jones, A complete linear programming hierarchy for
           linear codes, in 13th Innovations in Theoretical Computer Science Conference, LIPIcs 215 (2022),
           article 51, 51:1–51:22, doi:10.4230/LIPIcs.ITCS.2022.51.
[CJJLL26]  L. N. Coregliano, F. G. Jeronimo, C. Jones, N. Linial, and E. Loyfer, Higher-order Delsarte
           dual LPs: lifting, constructions and completeness, in 17th Innovations in Theoretical Com-
           puter Science Conference (ITCS 2026), LIPIcs 362 (2026), article 44, 44:1–44:22, doi:10.4230/
           LIPIcs.ITCS.2026.44.
[Del72]    P. Delsarte, Bounds for unrestricted codes, by linear programming, Philips Res. Rep. 27 (1972),
           272–289.
[Del73]    P. Delsarte, An algebraic approach to the association schemes of coding theory, Philips Res. Rep.
           Suppl. 10 (1973), vi+97 pp.
[DGS77]    P. Delsarte, J. M. Goethals, and J. J. Seidel, Spherical codes and designs, Geom. Dedicata 6 (1977),
           363–388, doi:10.1007/BF03187604.
[Fei12]    P. Feinsilver, Representations of sl(2) in the Boolean lattice, and the Hamming and Johnson
           schemes, Inﬁn. Dimens. Anal. Quantum Probab. Relat. Top. 15 (2012), no. 3, article 1250019,
           doi:10.1142/S0219025712500191.



                                                     76
[FT05]     J. Friedman and J.-P. Tillich, Generalized Alon–Boppana theorems and error-correcting codes, SIAM
           J. Discrete Math. 19 (2005), 700–718, doi:10.1137/S0895480102408353.
[GW09]     R. Goodman and N. R. Wallach, Symmetry, Representations, and Invariants, Graduate Texts in
           Mathematics, vol. 255, Springer, New York, 2009, doi:10.1007/978-0-387-79852-3.
[Gor00]    D. V. Gorbachev, Extremal problem for entire functions of exponential spherical type, connected
           with the Levenshtein bound on the sphere packing density in Rn , Izv. Tula State Univ. Ser. Math.
           Mech. Inform. 6 (2000), 71–78; in Russian.
[KL78]     G. A. Kabatianskii and V. I. Levenshtein, On bounds for packings on a sphere and in space, Prob-
           lems Inform. Transmission 14 (1978), 1–17.
[Koo81]    T. H. Koornwinder, Clebsch–Gordan coeﬃcients for SU(2) and Hahn polynomials, Nieuw Arch.
           Wisk. (3) 29 (1981), 140–155.
[Kra76]    M. Krämer, Multiplicity free subgroups of compact connected Lie groups, Arch. Math. (Basel) 27
           (1976), 28–36, doi:10.1007/BF01224637.
[Kra18]    P. Kravchuk, Casimir recursion relations for general conformal blocks, J. High Energy Phys. 2018,
           no. 2, article 011, doi:10.1007/JHEP02(2018)011.
[Lev79]    V. I. Levenshtein, On bounds for packings in n-dimensional Euclidean space, Soviet Math. Dokl.
           20 (1979), 417–421.
[LL23]     E. Loyfer and N. Linial, New LP-based upper bounds in the rate-vs.-distance problem for binary lin-
           ear codes, IEEE Trans. Inform. Theory 69 (2023), no. 5, 2886–2899, doi:10.1109/TIT.2023.3236660.
[Mac63]    J. MacWilliams, A theorem on the distribution of weights in a systematic code, Bell Syst. Tech. J.
           42 (1963), 79–94, doi:10.1002/j.1538-7305.1963.tb04003.x.
[MRRW77]   R. J. McEliece, E. R. Rodemich, H. C. Rumsey, Jr., and L. R. Welch, New upper bounds on the
           rate of a code via the Delsarte–MacWilliams inequalities, IEEE Trans. Inform. Theory 23 (1977),
           157–166, doi:10.1109/TIT.1977.1055688.
[Mus08]    O. R. Musin, The kissing number in four dimensions, Ann. of Math. (2) 168 (2008), 1–32,
           doi:10.4007/annals.2008.168.1.
[NS05]     M. Navon and A. Samorodnitsky, On Delsarte’s linear programming bounds for binary codes, in
           46th Annual IEEE Symposium on Foundations of Computer Science (FOCS 2005), 2005, 327–336,
           doi:10.1109/SFCS.2005.55.
[OS79]     A. M. Odlyzko and N. J. A. Sloane, New bounds on the number of unit spheres that can touch
           a unit sphere in n dimensions, J. Combin. Theory Ser. A 26 (1979), 210–214, doi:10.1016/0097-
           3165(79)90074-8.
[PMP23]    J. C.-J. Pang, H. Mahdavifar, and S. S. Pradhan, New bounds on the size of binary codes with
           large minimum distance, IEEE J. Sel. Areas Inform. Theory 4 (2023), 219–231, doi:10.1109/
           JSAIT.2023.3295836.
[Sam01]    A. Samorodnitsky, On the optimum of Delsarte’s linear program, J. Combin. Theory Ser. A 96
           (2001), 261–287, doi:10.1006/jcta.2001.3176.
[Sam04]    A. Samorodnitsky, On linear programming bounds for spherical codes and designs, Discrete Comput.
           Geom. 31 (2004), 385–394, doi:10.1007/s00454-003-2858-0.
[Sam25]    A. Samorodnitsky, On the diﬃculty to beat the ﬁrst linear programming bound for binary codes,
           IEEE Trans. Inform. Theory 71 (2025), no. 4, 2383–2388, doi:10.1109/TIT.2024.3504268.
[SZ24]     N. T. Sardari and M. Zargar, New upper bounds for spherical codes and packings, Math. Ann. 389
           (2024), 3653–3703, doi:10.1007/s00208-023-02738-z.
[S42]      I. J. Schoenberg, Positive deﬁnite functions on spheres, Duke Math. J. 9 (1942), 96–108,
           doi:10.1215/S0012-7094-42-00908-6.
[Sch05]    A. Schrijver, New code upper bounds from the Terwilliger algebra and semideﬁnite programming,
           IEEE Trans. Inform. Theory 51 (2005), 2859–2866, doi:10.1109/TIT.2005.851748.
[SvdW53]   K. Schütte and B. L. van der Waerden, Das Problem der dreizehn Kugeln, Math. Ann. 125 (1953),
           325–334, doi:10.1007/BF01343127.
[Sid74]    V. M. Sidel’nikov, New bounds for densest packing of spheres in n-dimensional Euclidean space,
           Math. USSR-Sb. 24 (1974), no. 1, 147–157, doi:10.1070/SM1974v024n01ABEH001911.
[Sri11]    M. K. Srinivasan, Symmetric chains, Gelfand–Tsetlin chains, and the Terwilliger algebra of the
           binary Hamming scheme, J. Algebraic Combin. 34 (2011), 301–322, doi:10.1007/s10801-010-0272-
           2.
[Via17]    M. S. Viazovska, The sphere packing problem in dimension 8, Ann. of Math. (2) 185 (2017), 991–
           1015, doi:10.4007/annals.2017.185.3.7.
[Z24]      M. Zargar, Stiefel manifolds and upper bounds for spherical codes and packings, 2024, arXiv:
           2407.10697.




                                                    77
