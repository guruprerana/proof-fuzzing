# Exponential Growth Rate of the Cohn–Elkies Sphere Packing Linear Program

> Source: OpenAI, *Ten Advances in Mathematics and Theoretical Computer Science*, Chapter 1, PDF pages 5–30. Layout-preserving text extraction; consult the source PDF for authoritative equation rendering.

                                   Chapter 1

Exponential Growth Rate of the Cohn–Elkies
     Sphere Packing Linear Program
    Abstract. We determine the exact exponential decay rate of the Cohn–Elkies
    sphere-packing linear program. If ∆d denotes the maximal sphere-packing den-
    sity in Rd and LPd denotes the optimal density bound furnished by this program,
    then                                               r
                                    1/d          1/d      e
                          lim sup ∆d ≤ lim LPd =            .
                            d→∞          d→∞             2π
    The positive-√ and negative-eigenvalue Fourier sign-uncertainty radii are both
    (1/π + o(1)) d.



                                     Contents
1. Introduction
2. Fourier-analytic preliminaries
3. The universal Cohn–Elkies lower bound
4. The admissible primal upper bound
Appendix A. Comparison of the sign-uncertainty constants
References




                                          1
                                             1. Introduction
   Sphere packing asks how densely congruent balls can ﬁll Euclidean space. For centers sep-
arated by at least 1, let ∆d be the supremum of the upper densities of radius-1/2 balls in Rd .
The Fourier-analytic linear-programming method of Gorbachev and Cohn–Elkies [Gor00, Coh02,
CE03] bounds this density using an auxiliary function and its Fourier transform. Viazovska used
this framework to prove that the E8 lattice gives the optimal packing in dimension eight [Via17];
Cohn, Kumar, Miller, Radchenko, and Viazovska subsequently established the optimality of the
Leech lattice in dimension twenty-four [CKMRV17]. Related Fourier interpolation formulas re-
veal further structure behind these exceptional conﬁgurations [RV19, CKMRV22].
   By contrast, the behavior of the linear program in high dimensions remained poorly under-
stood. Cohn and Zhao proved that it is always at least as strong as the Kabatianskii–Levenshtein
spherical-code bound [CZ14], but whether it improves the classical high-dimensional sphere-
packing exponent remained open. Motivated by the modular bootstrap [HMR19], Afkhami-
Jeddi, Cohn, Hartman, de Laat, and Tajdini conjectured its high-dimensional rate [AJCHLT20,
§ 3].
   We use the Fourier convention and unit-ball volume
                                   Z
                                                                           π d/2
                         fb(ξ) =         f (x)e−2πix·ξ dx,       vd =              .         (1)
                                   Rd                                   Γ(d/2 + 1)
A ball of radius 1/2 has volume vd /2d . For the real Schwartz space S(Rd ; R), deﬁne
                   n                                                                   o
             Ad = f ∈ S(Rd ; R) : fb(0) > 0, fb ≥ 0 on Rd , f ≤ 0 on {|x| ≥ 1} ,             (2)
and the associated linear-programming bound by
                                                     vd      f (0)
                                            LPd =       inf        .                         (3)
                                                     2 f ∈Ad fb(0)
                                                      d

Fourier inversion gives f (0) > 0. The Gorbachev–Cohn–Elkies bound [Gor00, CE03] assigns
every f ∈ Ad the density upper bound vd f (0)/(2d fb(0)), so (3) yields
                                                  ∆d ≤ LPd .                                 (4)
Our main theorem proves the exponential rate conjectured in [AJCHLT20, Conjs. 3.1–3.2].
                                   1/d        p
Theorem 1.1. As d → ∞, LPd               −→       e/(2π).
   By (4), the theorem gives ∆d ≤ LPd = 2−(α∗ +o(1))d , where α∗ = 21 log2 (2π/e) = 0.6044 . . ..
This is the ﬁrst improvement since 1978 to the general sphere-packing exponent. The classi-
cal Kabatianskii–Levenshtein exponent was 0.59905576 . . . [KL78, Lev79]; subsequent spherical-
code reﬁnements had improved only lower-order factors [CZ14, SZ24, Z24]. The matching lower
bound shows that no Cohn–Elkies auxiliary function can improve this exponent.
   Our companion paper in Chapter 2 recovers the upper-bound direction of Theorem 1.1 as a
small-distance limit of spherical-code bounds.
   The packing sign conditions are related to the Bourgain–Clozel–Kahane uncertainty princi-
ple for eventually nonnegative Fourier eigenfunctions [BCK10, GOSS17, GOSR21]. Cohn and
Gonçalves [CG19] introduced its anti-self-Fourier counterpart and connected it with sphere
packing. If g ∈ L1 (Rd ; R) satisﬁes gb = ςg for ς ∈ {−1, +1}, then gb ∈ L1 and Fourier inversion
supplies a continuous representative of g. Using this representative for all pointwise values and
sign conditions, deﬁne
                       r(g) = inf{R ≥ 0 : g(x) ≥ 0 for |x| ≥ R},                             (5)
                   Aς (d) = inf{r(g) : 0 6= g ∈ L (R ; R), gb = ςg, g(0) = 0}.
                                                        1    d
                                                                                             (6)
Here r(g) = ∞ when no such radius exists. The signs +1 and −1 give the original and comple-
mentary uncertainty problems, respectively.
   The negative-eigenvalue problem also arises in the spinless modular bootstrap, where mod-
ular S-antisymmetry produces anti-self-Fourier test functions whose eventual sign controls the


                                                       2
spectral gap [HMR19, AJCHLT20]. General lower bounds for sign uncertainty and limita-
tions of Gaussian–polynomial test functions of sublinear degree appear in [Edw25] and [CDG24,
Thm. 1.2], respectively. The next theorem proves the asymptotic equality conjectured in [CG19,
Conj. 1.5] and [AJCHLT20, (3.5)], with the common value predicted in [AJCHLT20, (3.3)]. Al-
though these asymptotics coincide, Appendix A observes that A+ (d) < A− (d) for all d.
Theorem 1.2. The Fourier-eigenfunction sign-uncertainty constants satisfy
                                         A+ (d)       A− (d)  1
                                     lim  √     = lim √      = .
                                     d→∞    d     d→∞    d    π
   The proof reduces both problems to the last sign changes of Fourier eigenfunctions. In § 3,
Proposition 3.1 shows that a radial Schwartz  √ function g satisfying gb = ±g and g(0) = 0 has
exponentially little L1 mass inside B(0, c d) whenever c < 1/π. For an admissible packing
function F , let a = (Fb (0)/F (0))1/d and h(x) = F (ax). Then h(0) = h(0),  b     while the nonzero
function g =  b
              h−h  is anti-self-Fourier, vanishes at the origin, and is nonnegative outside B(0, 1/a).
      R
Since g = 0, its negative part has mass√ kgk1 /2, all of which lies in this ball. The mass estimate
therefore forces 1/a ≥ (1/π − o(1)) d. In § 4, Theorem 4.1 modiﬁes the Mellin transform of
a Gaussian to construct a Fourier√pair and a self-Fourier function whose required exterior sign
conditions begin at (1/π +po(1)) d. Stirling’s formula converts the matching radius bounds
into the packing exponent e/(2π).

                             2. Fourier-analytic preliminaries
  We reduce the packing and sign-uncertainty problems to radial functions and establish the
Mellin–Fourier identities used in both bounds. We repeatedly use the gamma recurrence and
reﬂection formulas [DLMF, § 5.5], together with their consequences for real b 6= 0:
                                                                 π
                        Γ(z + 1) = zΓ(z),    Γ(z)Γ(1 − z) =           ,
                                                              sin(πz)
                                     π                             π                    (7)
                     |Γ(ib)|2 =            ,  |Γ(1/2 + ib)|2 =           .
                                b sinh(πb)                      cosh(πb)
2.1. Radial reduction. Throughout, Fourier transforms use the convention (1), and we denote
a radial function and its one-variable proﬁle by the same symbol. With normalized Haar measure
on O(d), deﬁne the rotational average
                                                     Z
                                          Rf (x) =           f (U x) dU.
                                                     O(d)

Write Srad (Rd ; R) for the real Schwartz functions depending only on |x|, and L1rad (Rd ; R) for the
radial real integrable functions. Set Arad
                                         d = Ad ∩ Srad (R ; R). For every continuous integrable
                                                           d

f , rotational invariance gives
                       d = Rfb,
                       Rf                   (Rf )(0) = f (0),            d (0) = fb(0).
                                                                         Rf
Consequently, rotational averaging preserves every sign condition in (2), so the inﬁmum in (3) is
unchanged when Ad is replaced by Arad
                                    d , as in the radial formulation of Cohn and Miller [CM16,
§ 3]. If gb = ςg, then
                                d = ςRg,
                                Rg               r(Rg) ≤ r(g).
Moreover, Rg 6= 0 whenever g 6= 0 is eventually nonnegative. Indeed, if Rg = 0, the nonnegative
values of g outside a ball have zero rotational average, so g vanishes outside that ball. Its Fourier
transform is then entire, and gb = ςg makes this entire function vanish on the same exterior region,
forcing g = 0.
   We also need approximation by Schwartz functions preserving the Fourier eigenvalue and
vanishing at the origin. Suppose that g ∈ L1rad (Rd ; R) satisﬁes gb = ςg and g(0) = 0, where
ς ∈ {−1, +1}. For n ≥ 1, set
                κn (x) = nd e−πn |x| ,         ηn (x) = e−π|x| /n ,
                                 2    2                          2   2
                                                                              qn = ηn (g ∗ κn ).


                                                         3
Gaussian molliﬁcation gives qn R∈ Srad (Rd ; R), qn → g, and qbn = κn ∗ (ηn gb) → gb in L1 . Moreover,
qn (0) → g(0) = 0 and qbn (0) = qn → gb(0) = 0. Deﬁne
                                                                                                  
                    qn + ς qbn                                                                   d
                                        ψ+ (x) = e−π|x| ,                                          e−π|x| .
                                                                2                                        2
             pn =              ,                                           ψ− (x) = |x|2 −
                       2                                                                        4π
Since pbn = ςpn , ψbς = ςψς , and ψς (0) 6= 0, the correction
                                                                    pn (0)
                                                  gn = pn −                ψς
                                                                    ψς (0)
satisﬁes gn ∈ Srad (Rd ; R), gbn = ςgn , gn (0) = 0, and gn → g in L1 .
2.2. The radial Mellin transform. For a radial Schwartz function g, write r = |x| and ρ = |ξ|
for the spatial and frequency radii, respectively, and set
                                                     d                    2π d/2
                                               λ=      ,       Sd =              .
                                                     2                    Γ(d/2)
Here Sd is the area of the unit sphere, and polar integration gives
                                       Z                            Z ∞
                                               g(x) dx = Sd               g(r)rd−1 dr.
                                         Rd                         0
For ρ > 0, the Fourier transform has the Hankel representation
                                                         Z ∞
                             gb(ρ) = 2πρ1−d/2                  g(r)Jd/2−1 (2πrρ)rd/2 dr.
                                                           0
Because its Bessel kernel depends on rρ, the radial Fourier transform becomes particularly
simple after a Mellin transform: it reﬂects the Mellin variable and multiplies by an explicit
gamma factor. For Re z > 0, t ∈ R, and r > 0, the Mellin transform, its restriction to the
critical line, and Mellin inversion [PK01] are
                                        Z ∞
                         Mg (z) =               g(r)rz−1 dr,              Xg (t) = Mg (λ − it),
                                           0
                                                               Z                                               (8)
                                           r−λ
                                    g(r) =        Xg (t)rit dt.
                                           2π R
In particular, the radial integration normalization is
                                                     Z
                                           gb(0) =         g(x) dx = Sd Mg (d).
                                                      Rd
In logarithmic radius v = log r, set Φg (v) = eλv g(ev ). Smoothness at r = 0 gives exponential
decay of Φg and all its derivatives as v → −∞, while the Schwartz decay of g gives rapid decay
as v → +∞. Thus Φg ∈ S(R; R), and ordinary one-dimensional Fourier inversion gives
                                   Z                                                  Z
                                                          1
                     Xg (t) =          Φg (v)e−itv dv,          Xg (t)eitv dt.
                                                                     Φg (v) =
                           R                             2π R
The standard Mellin transform of the Hankel kernel gives, for 0 < Re z < d, the Mellin–Hankel
functional equation [SW71, Ch. IV], [DLMF, (10.22.43)]:
                                                              Γ(z/2)
                                   Mbg (z) = π λ−z                      Mg (d − z).                            (9)
                                                           Γ((d − z)/2)
If g(0) = gb(0) = 0, smooth radiality gives g(r), gb(r) = O(r2 ) at the origin. Both Mellin
transforms therefore extend holomorphically to Re z > −2, and (9) continues to Re z = 0:
                                                                              2
      Mg (d) = Sd−1 gb(0) = 0,   Mg (d − z) = −zMg0 (d) + O(z 2 ),  Γ(z/2) = + O(1),
                                                                              z
so the apparent gamma pole at z = 0 cancels. The line Re z = d/2 is ﬁxed by the reﬂection
z 7→ d − z. On this line the Fourier transform acts, for t ∈ R, by
                                                                                     Γ((λ − it)/2)
                       Xbg (t) = mλ (t)Xg (−t),                     mλ (t) = π it                  .          (10)
                                                                                     Γ((λ + it)/2)


                                                                4
For t ∈ R, its multiplier satisﬁes
                           mλ (−t) = mλ (t) = mλ (t)−1 ,            |mλ (t)| = 1.

                        3. The universal Cohn–Elkies lower bound
   By the radial reduction in § 2.1, assume that the admissible packing function F is radial. Let
a = (Fb (0)/F (0))1/d and deﬁne h(x) = F (ax). Then h(0) = h(0), b    and g = h b − h is anti-self-
Fourier, vanishes at the origin, and is nonnegative
                                         R            for |x| ≥ 1/a; see (29)–(30). The proof of
Theorem 3.8 veriﬁes that g 6= 0. Since g = 0, its negative part has mass kgk1 /2, all of which
lies in B(0, 1/a).
   Proposition 3.1 shows that every radial Schwartz Fourier eigenfunction
                                                                   √       vanishing at the origin,
                                                 1
of either eigenvalue, has exponentially little L mass in B(0, c d) when c √    < 1/π. Thus the
negative half-mass of g cannot ﬁt inside this ball, forcing 1/a ≥ (1/π − o(1)) d.
   The obstruction comes from the Mellin–Fourier identity (9). Lemma 3.2 bounds a normalized
Mellin transform Z on the strip | Im t| < d/2: total L1 mass controls the upper boundary,
while the Fourier functional equation controls the lower boundary. Writing λ = d/2, Poisson
interpolation gives
                                                                                 1−σ
        log |Z(s + iσλ)| ≤ Hσ (s) ≤ λMσ log(2πc2 ) + Jσ + Oσ (log λ),                   ,Mσ =
                                                                                     2
by Lemma 3.3. The sharp constant enters through Lemma 3.4: Jσ → log(π/2) as σ ↑ 1, so the
parenthesized rate tends to log(π 2 c2 ). It is negative exactly when c < 1/π. An all-frequency
bound and shifted Mellin inversion, in Lemmas 3.5 and 3.6, turn this negativity into the interior-
mass estimate; Stirling’s formula then yields the packing lower bound.

3.1. The Mellin-strip obstruction.
Proposition 3.1. For every 0 < c < 1/π, there exist Cc , γc > 0 and d0 (c) ∈ N such that, for
every d ≥ d0 (c), every ς ∈ {−1, +1}, and every nonzero g ∈ Srad (Rd ; R) satisfying gb = ςg and
g(0) = 0, one has
                                   Z
                                                               −γc d
                                          √ |g(x)| dx ≤ Cc e           kgk1 .                   (11)
                                     |x|<c d
                                             √
   Fix 0 < c < 1/π, d ∈ N, λ = d/2, R = c d, and a nonzero g ∈ Srad (Rd ; R) with gb = ςg,
ς ∈ {−1, +1}, and g(0) = 0. Let Sd = 2π λ /Γ(λ) be the area of the unit sphere. In the
logarithmic coordinate r = Rev , normalize the Mellin inversion formula (8) by setting
                         Sd                                   Sd λ+it
               φ(v) =        (Rev )d g(Rev ),         Z(t) =      R    Xg (t),                  (12)
                        kgk1                                 kgk1
                               Z                  Z 0                  Z
                                                                    1
               kφk1 = 1,            φ = 0,            |φ(v)| dv =              |g(x)| dx.       (13)
                                R                  −∞              kgk1 |x|<R
The second line follows from polar integration and gb(0) = ςg(0) = 0.
Lemma 3.2. For every −1 < σ < 1, the function Z is bounded and holomorphic on a neighbor-
hood of the strip |Im t| ≤ λ. Its boundary values satisfy |Z(y+iλ)| ≤ 1 and log|Z(y−iλ)| ≤ hλ (y)
for y 6= 0, where the lower-boundary majorant is
                    hλ (y) = λ log(πR2 ) + log |Γ(−iy/2)| − log |Γ(λ + iy/2)|.                  (14)
Writing θ = π(1 + σ)/2, deﬁne
                                                                          Z
                                     sin θ                                             1−σ
                   Pσ (T ) =                        ,          Mσ =             Pσ =       .    (15)
                             4(cosh(πT /2) − cos θ)                         R           2
Then                                      Z                               
                   |Z(s + iσλ)| ≤ exp            Pσ (T )hλ (s − λT ) dT            (s ∈ R).
                                             R



                                                      5
Proof. Since g(0) = gb(0) = 0, the holomorphic continuation and pole cancellation following
(9) show that Z is holomorphic whenever Im t > −λ − 2. In particular, it is holomorphic on
a neighborhood of the closed strip. Its upper-boundary values follow from (12), whereas the
Mellin–Fourier functional equation (9) gives the lower-boundary values:
                                         Z
                          Z(y + iλ) =            φ(v)e−iyv dv,                   |Z(y + iλ)| ≤ 1,                    (16)
                                           R
                                                                Γ(−iy/2)
                          Z(y − iλ) = ς(πR2 )λ+iy                          Z(−y + iλ).                               (17)
                                                               Γ(λ + iy/2)
Taking absolute values and using (16) gives log |Z(y − iλ)| ≤ hλ (y), independently of ς. At
y = 0, the zero Z(iλ) = 0 from (13) cancels the gamma pole in (17). Hence Z(y − iλ) remains
bounded there, although
                                hλ (y) = − log |y| + Oλ (1)                           (y → 0).
   For t0 = s+iσλ, the conformal map t 7→ exp(π(t+iλ)/(2λ)) and the upper-half-plane Poisson
formula [Ahl79] give the lower-edge harmonic measure λ−1 Pσ ((s − y)/λ) dy, with Pσ and Mσ
as in (15). The complementary upper-edge measure is (1 + σ)/2, and its boundary bound (16)
contributes nothing.
   The logarithmic singularity of hλ requires a bounded truncation before applying the Poisson
principle. The actual lower-boundary values satisfy
                                                                       Z ∞
                                                           Sd Rd                |g(r)|
                             sup |Z(y − iλ)| ≤                                         dr < ∞.
                             y∈R                           kgk1         0         r
Indeed, g(r) = O(r2 ) at zero and is Schwartz at inﬁnity. More generally, for −λ ≤ η ≤ λ, (12)
gives
                                                 Z
                                         Sd Rλ−η ∞
                           |Z(s + iη)| ≤             |g(r)|rλ+η−1 dr.
                                          kgk1    0
Splitting at r = 1 bounds this expression uniformly in s and η, so Z is bounded on the closed
strip. Choose D > max{0, supy log |Z(y − iλ)|}. The strip Poisson principle [Ahl79], applied to
log |Z| with lower-boundary majorant min{hλ , D} and upper-boundary majorant 0, gives
                                           Z                           
                                            1                  s−y
                           log |Z(t0 )| ≤     Pσ                   min{hλ (y), D} dy.
                                          R λ                   λ
The kernel in (15) decays exponentially, the singularity of hλ is locally integrable, and Stirling’s
formula gives hλ (y) = −λ log |y| + Oλ (1) at inﬁnity [DLMF, § 5.11]. Dominated convergence
therefore permits D → ∞, and the substitution T = (s − y)/λ yields
                                                                            Z
                     |Z(s + iσλ)| ≤ e   Hσ (s)
                                                 ,         Hσ (s) =              Pσ (T )hλ (s − λT ) dT.             (18)
                                                                             R
                                                                                                                       □
Lemma 3.3. For every −1 < σ < 1, there exists Cσ > 0, independent of d, c, and g, such that
     Z                                              Z 1           q                       
            Pσ (T ) hλ (λT ) − λ log(2πc ) −
                                          2
                                                           log         x2 + T 2 /4 dx          dT ≤ Cσ log(2 + λ).   (19)
        R                                             0

Deﬁne
                                          Z                Z 1           q
                                     1
                           Jσ = −                Pσ (T )           log       x2 + T 2 /4 dx dT.
                                    Mσ       R                 0
Then, for every s ∈ R,
                                                                                  
                  Hσ (s) ≤ Hσ (0) = λMσ log(2πc2 ) + Jσ + Oσ (log(2 + λ)).                                           (20)
                                                               √
Proof. To estimate the lower-boundary majorant (14) with R = c 2λ, put
                                                     q                                     λT
                                fT (x) = log             x2 + T 2 /4,                 b=      .
                                                                                            2

                                                               6
If d = 2n, so that λ = n, the gamma recurrence in (7) and |Γ(−ib)| = |Γ(ib)| give, for T 6= 0,
                                                                   X
                                                                   n−1
                                hn (nT ) = n log(2πc2 ) −                  fT (k/n).
                                                                   k=0
Monotonicity of fT bounds the Riemann-sum error by fT (1) − fT (0); thus
                                                        Z 1                                  
                                                                                1         4
                   0 ≤ hn (nT ) − n log(2πc2 ) −               fT (x) dx ≤        log 1 + 2 .
                                               0                                2        T
                               1
If d = 2n + 1, so that λ = n + 2 , the gamma identities (7) instead give
                                          X
                                          n−1                     
                                                         k + 1/2           1        1    coth(π|b|)
             hλ (λT ) = λ log(2πc ) −
                                  2
                                                fT                     +     log λ + log            .
                                          k=0
                                                            λ              2        2        |b|
The midpoint Riemann-sum error on [0, n/λ] is at most fT (n/λ) − fT (0); the remaining interval
[n/λ, 1] has length 1/(2λ). Together, these contributions are bounded by
                                                                                 
                               C 1 + log(2 + |T |) + log(2 + |T |−1 ) .

Adding C log(2 + λ) also bounds the gamma endpoint correction 12 log λ + 12 log(coth(π|b|)/|b|).
Since (15) gives Pσ (T ) σ e−π|T |/2 , and log(2 +|T |−1 ) is locally integrable, integrating the even-
and odd-dimensional bounds proves (19).
  It remains to identify the maximum of the Poisson extension Hσ . Both hλ and Pσ are even,
and the digamma series [DLMF, § 5.7] gives, for y > 0,
                                                                                           ∞
                                                                                           X
                  1                                                                                  b
      h0λ (y) =     (Im ψ(λ + iy/2) − Im ψ(iy/2)) < 0,                   Im ψ(a + ib) =                2 + b2
                                                                                                              .
                  2                                                                        k=0
                                                                                               (k + a)
Here ψ = Γ0 /Γ. The explicit kernel (15) is likewise decreasing on (0, ∞). For N > 0, the function
qN = (hλ + N )+ is nonnegative, integrable, even, and decreasing there. The convolution of two
such functions is largest at zero. Subtracting N Mσ and letting N → ∞, using the exponential
decay of Pσ , therefore gives Hσ (s) ≤ Hσ (0). Evaluating at zero with (19) proves (20).         □
Lemma 3.4. For Jσ deﬁned in Lemma 3.3,
                                                                   π
                                                lim Jσ = log         .
                                                σ↑1                2
Consequently, for every 0 < c < 1/π, there exists σ = σ(c) ∈ (−1, 1) such that log(2πc2 ) + Jσ <
0.
Proof. With T = 2u, divide the lower-edge harmonic measure Pσ (T ) dT from (15) by its total
mass Mσ . The corresponding probability density in u is
                                      2Pσ (2u)             sin θ
                           pσ (u) =            =                           .
                                        Mσ       (1 − σ)(cosh(πu) − cos θ)
As σ ↑ 1, sin θ/(1 − σ) → π/2. The densities pσ are uniformly bounded by Ce−π|u| and therefore
converge in L1 (R) to                                         
                                               π       2 πu
                                      p(u) = sech                .
                                               4            2
The characteristic function of this density is
                               Z
                                                      t
                                   p(u)eitu du =          ,       t ∈ R,                  (21)
                                 R                 sinh t
interpretedR as 1 at t = 0. For t > 0, a contour shift by 2i across the Rdouble pole
                                                                                  √ at i gives
(1 − e−2t ) p(u)eitu du = 2te−t ; evenness handles t < 0. Deﬁne I(x) = R p(u) log x2 + u2 du.
For x > 0, the Laplace representation of x/(x2 + u2 ), (21), and the trigamma integral [DLMF,
§ 5.9] yield                        Z ∞                                 
                            0             −xt    t           1 0 x+1
                           I (x) =      e            dt = ψ                .
                                     0        sinh t         2        2


                                                          7
Since both I(x) and ψ((x + 1)/2) + log 2 equal log x + o(1) at inﬁnity [DLMF, § 5.11], their
integration constants agree. Local integrability at u = 0 extends the identity to x = 0:
                    Z                  p                                 
                                                                 x+1
                            p(u) log   x2 + u2 du = ψ                          + log 2        (x ≥ 0).   (22)
                        R                                         2
The uniform exponential bound on pσ and local integrability of log |u| justify dominated con-
vergence in Jσ . Since
                           Z 1       
                                  x+1               Γ(1)
                              ψ         dx = 2 log         = − log π,
                            0      2               Γ(1/2)
(22) gives the exact threshold
                                   π                     π
                       lim Jσ = log ,    log(2πc2 ) + log = log(π 2 c2 ).
                       σ↑1         2                      2
If c < 1/π, choose σ = σ(c) < 1 suﬃciently close to 1 that
                                                                               
                                           δc = − log(2πc2 ) + Jσ(c) > 0.                                (23)
                                                                                                           □
   Fix σ = σ(c) and δc > 0 as in (23). We ﬁrst bound the Mellin transform Z on√ the horizontal
line Im t = σλ, and then use that bound to control the mass of g inside B(0, c d).
Lemma 3.5. There exist γc , Cc , Bc > 0, depending only on c, such that, for every suﬃciently
large d,                                      Z
                  Hσ (s) ≤ −γc λ            (s ∈ R),                 |Z(s + iσλ)| ds ≤ Cc λe−γc λ .
                                                                 R
Moreover, after increasing Bc if necessary,
                                                    Mσ λ     |S|
                                  Hσ (λS) ≤ −            log                   (|S| ≥ Bc ).
                                                     2       Cc
Proof. The maximum estimate for Hσ in (20), together with log(2πc2 ) + Jσ = −δc , gives
                             Hσ (s) ≤ −λMσ δc + Oσ (log λ) ≤ −γc λ                       (s ∈ R)
for all suﬃciently large d, with γc > 0 independent of s, g, and the Fourier eigenvalue ς.
   To control all Mellin frequencies, apply the gamma identities (7) to (14). In both parities,
                                                     4πc2
                                hλ (λU ) ≤ λ log           + Eλ (U )               (U 6= 0),
                                                      |U |
where                                         
                                              0,                               λ ∈ N,
                                Eλ (U ) =                                
                                               1 log coth       πλ|U |
                                                2                  2          , λ ∈ N + 21 .
Each gamma-recurrence factor has modulus at least |λU |/2; in odd dimension, the remaining
ratio at b = λU/2 contributes Eλ (U ). Expanding log coth x in its convergent odd-exponential
series gives, in odd dimension,
                          Z                   Z ∞
                                            2                     π
                              Eλ (U ) dU =        log coth x dx =    .
                            R              πλ 0                   4λ
Thus in both parities the Pσ -convolution of Eλ is at most πkPσ k∞ /(4λ). Consequently, (18)
gives                                       Z
                Hσ (λS) ≤ λMσ log(4πc2 ) − λ                 Pσ (T ) log |S − T | dT + Oσ (λ−1 ).
                                                         R
Split the logarithmic integral at |T | = |S|/2. The exponential decay of (15) gives mass Mσ +
Oσ (e−π|S|/4 ) on |T | ≤ |S|/2; the possible negative contribution from |S − T | < 1 is Oσ (e−π|S|/2 ),
by local integrability of log |S − T |. Hence, for some Bc , Cc0 > 0,
                    Z
                                                         Mσ
                            Pσ (T ) log |S − T | dT ≥       log |S| − Cc0                (|S| ≥ Bc ).
                     R                                    2


                                                             8
After increasing Cc0 , the estimates for Hσ on the whole line and at large frequencies become
                        Hσ (s) ≤ −γc λ                                                         (s ∈ R),                          (24)
                                       Mσ λ    |S|
                    Hσ (λS) ≤ −             log 0                                              (|S| ≥ Bc ).                      (25)
                                        2      Cc
Choose B > max{Bc , Cc0 } and q = Mσ λ/2 > 1. The two bounds in (24)–(25) yield
                                  Z
                                                 eHσ (s) ds ≤ 2Bλe−γc λ ,
                                      |s|≤Bλ
                                  Z                                                    1−q
                                                                   2λCc0          B
                                                 e   Hσ (s)
                                                              ds ≤                             .
                                      |s|>Bλ                       q−1            Cc0
The second bound decays at rate (Mσ /2) log(B/Cc0 ) > 0. Decreasing γc if necessary, and
applying (18), we obtain    Z
                                               |Z(s + iσλ)| ds ≤ Cc λe−γc λ .         (26)
                                           R
                                                                                         □
                1
  The global L estimate (26) for Z on Im t = σλ now controls φ(v) for v < 0, corresponding
                  √
by (13) to |x| < c d.
Lemma 3.6. For every 0 < c < 1/π, there exist Cc , γc > 0 and d0 (c) ∈ N, independent of g
and ς, such that       Z          0
                                       |φ(v)| dv ≤ Cc e−γc d                   (d ≥ d0 (c)).
                                 −∞

Proof. Let G(v) = e(σ−1)λv φ(v). The normalized proﬁle φ from (12) satisﬁes
                     Z                                          Z ∞
                                       Sd R(1−σ)λ
                           |G(v)| dv =                                    |g(r)|r(1+σ)λ−1 dr < ∞.
                         R                kgk1                   0
                                                                                                                 R             −isv dv
Thus G ∈ L1 (R), and (12) identiﬁes its angular-frequency Fourier transform                                          R G(v)e
with Z(s + iσλ). The integrability of this transform follows from (26), so Fourier inversion gives
                        Z                                                                          Z
                                                                                   e(1−σ)λv
        Z(s + iσλ) =         e(σ−1)λv φ(v)e−isv dv,                      φ(v) =                        Z(s + iσλ)eisv ds.
                         R                                                            2π           R
                                                                                           R0
Taking absolute values and integrating over v < 0 contributes −∞ e(1−σ)λv dv = ((1 − σ)λ)−1 .
Combining this with (26) and λ = d/2, and decreasing γc if necessary, gives
                   Z 0                                           Z
                                        1
                       |φ(v)| dv ≤                                       |Z(s + iσλ)| ds ≤ Cc e−γc d .                           (27)
                    −∞             2π(1 − σ)λ                        R
                                                                                                                                   □
                                                                                                         R
Proof of Proposition 3.1. By (13), the left side of (27) is precisely kgk−1
                                                                         1
                                                                                 √
                                                                            |x|<c d |g(x)| dx. Thus
(27) proves (11), uniformly in g and its Fourier eigenvalue ς.                                   □
3.2. The packing lower bound.
Proposition 3.7. For every 0 < c < 1/π, there exists d0 (c) ∈ N such that, for every d ≥ d0 (c)
and ς ∈√ {−1, +1}, no nonzero g ∈ L (R ; R) satisﬁes gb = ςg, g(0) = 0, and g(x) ≥ 0 for
                                      1  d

|x| ≥ c d. Here g denotes its continuous Fourier-inversion representative.
                                                                                                        R
Proof. First, suppose that g is a radial Schwartz eigenfunction. Since g = gb(0) = ςg(0) =√0,
its negative part g− = max{−g, 0}√has integral kgk1 /2. The assumption g(x) ≥ 0 for |x| ≥ c d
forces g− to vanish outside B(0, c d), contradicting (11) once Cc e−γc d < 1/2.
   For general g ∈ L1 , the radial reduction in § 2.1 shows that h = Rg 6= 0 and has the
same Fourier eigenvalue, origin value, and exterior sign. The approximation constructed there
                                                           b
                                 √ hn → h in L with hn = ςhn and hn (0) = 0. Writing
gives radial Schwartz eigenfunctions                1

(hn )− = max{−hn , 0} and R = c d, the exterior nonnegativity of h gives
                    Z                  Z                                  Z
                            (hn )− ≤                 |hn (x)| dx +                 |hn (x) − h(x)| dx.
                     Rd                 |x|<R                              |x|≥R



                                                                 9
Applying (11) to hn therefore implies
                                         Z
                            1
                              khn k1 =            (hn )− ≤ Cc e−γc d khn k1 + khn − hk1 .
                            2                Rd

Letting n → ∞ gives khk1 /2 ≤ Cc e−γc d khk1 , which contradicts h 6= 0 for all suﬃciently large
d.                                                                                            □
Theorem 3.8. There is a sequence ϵd → 0 such that, for every suﬃciently large d and every
F ∈ Ad ,
                                          r        d
                              F (0)    2d     e
                                     ≥          − ϵd .                               (28)
                              Fb (0)   vd    2π

Proof. By radial reduction, replace F with its rotational average, which preserves F (0), Fb (0),
                                                                           b − h. The Fourier
and admissibility. Deﬁne a = (Fb (0)/F (0))1/d > 0, h(x) = F (ax), and g = h
convention (1) and the admissibility conditions (2) give
  b
  h(ξ) = a−d Fb (ξ/a),              b
                             h(0) = h(0) = F (0),                                                                   (29)
      gb = −g,               g(0) = 0,                            g(x) = a−d Fb (x/a) − F (ax) ≥ 0 (|x| ≥ 1/a).
                                                                                                             (30)
                                b ≥ 0, while h(x) = F (ax) ≤ 0 for |x| ≥ 1/a. Thus h would be
Moreover, g 6= 0: otherwise h = h
a nonzero compactly supported √ self-Fourier function, contradicting Fourier analyticity. Hence
Proposition 3.7 gives 1/a > c d, uniformly in F , for each ﬁxed c < 1/π and all suﬃciently
large d. Consequently,
                                                               !1/d
                                  1                   F (0)
                         lim inf √ inf                                 ≥c          (0 < c < 1/π).
                          d→∞      d F ∈Ad            Fb (0)
Taking the supremum over c < 1/π yields
                                                           !1/d                    √
                                                  F (0)                    1
                                       inf                        ≥          − o(1)    d.                           (31)
                                      F ∈Ad       Fb (0)                   π
                                                                                 1/d                 p
Combining (31) with Stirling’s formula [DLMF, § 5.11], vd                              = (1 + o(1)) 2πe/d gives (28), for
a sequence ϵd → 0 independent of F .                                                                                   □

                                4. The admissible primal upper bound
  Section 3 established
                                                 !1/d                         
                                                                                                 √
                                       F (0)                                               1
                      min       inf                      , A− (d), A+ (d)          ≥         − o(1)    d.
                            F ∈Ad     Fb (0)                                             π

We explain how the upper bounds in the introduction reduce to constructing functions whose
sign changes occur at the same radius. Suppose that real radial Schwartz functions f− , f+ satisfy
                    fb− = f+ > 0,             f− (0) = f+ (0),                 f− (x) < 0 (|x| ≥ R).
For F (x) = f− (Rx), Fourier scaling gives
                                                                                                  F (0)
                 Fb (ξ) = R−d f+ (ξ/R) > 0,                 F (x) < 0          (|x| ≥ 1),                  = Rd .
                                                                                                  Fb (0)
Consequently F ∈ Ad and LPd ≤ vd (R/2)d . The diﬀerence g− = f+ − f− is anti-self-Fourier,
vanishes at the origin, and is positive for |x| ≥ R, so it also proves A− (d) ≤ R. A self-
Fourier function f0 satisfying f0 (0) = 0 and f0 (x) > 0 for |x| ≥ R similarly proves A+ (d) ≤ R.
Thus all the upper
                 √ bounds reduce to producing one Fourier pair, one self-Fourier function, and
R = (1/π + o(1)) d.


                                                                  10
Theorem 4.1. There is ϵ0 > 0 such that, for every ﬁxed 0 < ϵ < ϵ0 and every suﬃciently large
dimension d, there exist real radial Schwartz functions f− , f+ , f0 and a radius Rϵ,d > 0 such
that f+ > 0 everywhere, f− < 0 < f0 whenever |x| ≥ Rϵ,d , and
                 fb− = f+ ,    fb0 = f0 ,    f− (0) = f+ (0) > 0,    f0 (0) = 0.
Moreover,
                                                 Rϵ,d 1
                                        lim lim √ = .
                                         ϵ↓0 d→∞   d  π
4.1. Outline of the construction. We need a Fourier pair f− , f+ = fb− and a self-Fourier
function f0 , with f+ > 0 everywhere and f− < 0 < f0 outside a common radius. In Mellin
coordinates, (10) reduces these Fourier symmetries to reﬂection of the frequency. The Gaussian
                                                                 
                            λ/2 −πr 2      G        it/2   λ − it            d
                 gG (r) = 2π e        ,   Eλ (t) = π Γ              ,    λ= ,
                                                             2               2
already obeys mλ (t)EλG (−t) = EλG (t). Multiplication by an even factor therefore preserves
Fourier symmetry. We choose Eλ (t) = EλG (t)eλhϵ (t/λ) , where the even perturbation hϵ in (36) is
determined by a signed density w.
   The variable a in that density parametrizes radial dilations: the Mellin multiplier cos(at/λ)−1
corresponds to
                                       ea g(rea/λ ) + e−a g(re−a/λ )
                            g(r) 7−→                                 − g(r).
                                                     2
A shell is an interval of these dilation parameters supporting one component of w. Our negative
component ws moves the sign radius inward, and a positive component wB , supported on much
larger dilation parameters, restores decay at every nonzero Mellin frequency.
   We multiply the common envelope by polynomials P− , P+ , P0 . Reﬂection exchanges P− and
P+ and ﬁxes P0 , giving the desired Fourier symmetries. The ﬁrst gamma pole, at normalized
frequency ζ = −i, controls the value at the origin: the polynomial P0 cancels this pole, while
P− and P+ retain equal positive residues. On the imaginary axis, the polynomials are chosen
so that P+ (iu) > 0 for u > −1, whereas P− (iu) < 0 and P0 (iu) > 0 just above u = 1; see (39).
Thus the essential contour is t = λ(T + iu) with u ≈ 1.
   On this contour, the radius r = ev(u) for which the Mellin integrand is stationary at T = 0
satisﬁes (44). For ﬁxed u > −1, the digamma asymptotic gives
                                  r           Z                      
                        ev(u)       1+u            ∞
                         √ −→             exp        w(a)a sinh(ua) da .
                           d         4π          0
Consequently, negative w decreases the logarithm of the stationary radius when u > 0. However,
it also reduces the decay of the Mellin integrand away from T = 0. At u = 1, after dividing
the damping by λ, the limiting gamma contribution has density e−2a /(2a2 ), while the pertur-
bation contributes w(a) cosh a. A suﬃcient pointwise condition for nonnegative total damping
is therefore
                                                      e−2a
                                     |w(a)| cosh a ≤       .
                                                      2a2
Within this pointwise constraint, the greatest inward displacement is achieved formally by
                                             Z
                                e−2a             ∞                       1    π
                  w∗ (a) = − 2          ,          w∗ (a)a sinh a da = − log ,               (32)
                             2a cosh a         0                         2    2
where the integral evaluation follows from the gamma
                                                  √       duplication formula [DLMF, § 5.5]. The
Gaussian stationary radius at u = 1 is (2π) −1/2    d, so the displacement in (32) gives
                                                        
                                     1           1     π      1
                                   √ exp − log             = .                               (33)
                                     2π          2     2      π
   Although its Mellin perturbation is well deﬁned, the formal density w∗ has inﬁnite mass at
zero and saturates the gamma damping. Its Mellin factor therefore lacks the strict decay needed
for a Schwartz function. Instead, we truncate it to a bounded interval and taper it slightly,
obtaining a negative shell ws that preserves the displacement up to O(ϵ) while leaving a deﬁnite


                                                 11
damping margin. This margin suﬃces near u = 1, but not on contours with arbitrarily large u.
A second shell wB , supported on [B, B + 1], is chosen to have negligible eﬀect on the stationary
radius at u = u0 while dominating the negative shell at every frequency when u ≥ U > u0 .
Using an interval rather than a single dilation avoids frequencies at which its damping would
vanish.
   The remaining proof has two analytic parts. Uniform saddle estimates show that the Mellin
integral at r = ev(u) has the sign of Pj (iu), which gives the exterior signs and positivity of f+
for r ≥ r∗ . A downward contour shift then expresses f+ on [0, r∗ ] as a perturbed exponential
series, proving positivity at the remaining radii. The negative-shell displacement in (32) ﬁnally
yields the sharp radius (33).

4.2. The Mellin ansatz. We turn the ideal negative density w∗ in (32) into two compactly
supported shells. The negative shell ws retains its logarithmic-radius displacement up to O(ϵ),
while the positive shell wB is negligible at u = u0 and dominates the damping for u ≥ U .
   Put λ = d/2, and throughout the construction ﬁx ϵ before taking d → ∞. Constants in Oϵ (·)
and ϵ may depend on ϵ, but are independent of d and of the saddle parameter whenever a
bound is stated uniformly in that parameter; unadorned implicit constants are absolute.
   Introduce cutoﬀs 0 < a0 < A < B, a positive-shell amplitude Q > 0, and saddle parameters
                                   ϵ               ϵ
                         u0 = 1 + ,       U =1+ ,         C0 = A + a−1
                                                                     0 .
                                  4                2
As ϵ ↓ 0, the cutoﬀs should satisfy
                                e−2A
                   a0 = o(ϵ),         = o(ϵ),   ϵA = o(1),       A = o(B).
                                  A
The ﬁrst two conditions make the omitted portions of the ideal saddle displacement negligible,
and the third permits an O(ϵ(1 + a)) taper on the negative shell. For the positive shell, of
amplitude Q, the required separation is
                     BQe(u0 −1)B = o(1),             C0 Q−1 e−(U −1)(B−A) = o(1).
The bound on BQe(u0 −1)B keeps the positive shell from moving the target saddle. The bound
on C0 Q−1 e−(U −1)(B−A) makes that shell dominate the negative shell once u ≥ U . Because
u0 − 1 < U − 1, both conditions are compatible: writing Q = e−qϵ B , choose u0 − 1 < qϵ < U − 1
with enough separation that ϵB dominates log B + log C0 .
   One convenient realization of all these requirements is
                            a0 = ϵ2 ,         A = log(1/ϵ),      B = ϵ−3 ,
                                   (u0 − 1) + (U − 1)
                            qϵ =                      ,        Q = e−qϵ B ,                  (34)
                                            2
                                b(a) = 1 − 2ϵ(1 + a),         β = u0 − 1.
The exponential slope qϵ is the midpoint between the two contour heights u0 − 1 and U − 1.
The taper leaves a damping margin of order ϵ, and β = u0 − 1 places the sign transition at the
target saddle. For suﬃciently small ϵ, we have b > 0 on [a0 , A] and B > A + 1. Deﬁne
                                  b(a)e−2a
                        ws (a) = −         1        (a),
                                 2a2 cosh a [a0 ,A]                                          (35)
                                 Q
                      wB (a) =        1       (a),       w = ws + wB .
                               cosh a [B,B+1]
The signed density w determines the even entire Mellin perturbation
                                             Z ∞
                                                                   
                                 hϵ (ζ) =          w(a) cos(aζ) − 1 da.                      (36)
                                             0
For η > 0, the positive density describing the unperturbed gamma damping is
                                                 e−ηa
                                µλ,η (a) =                       (a > 0).                    (37)
                                             a(1 − e−2a/λ )


                                                      12
Lemma 4.2. There are absolute constants ϵ0 , c, C > 0 such that, for every 0 < ϵ < ϵ0 , the
shells in (35) have the following properties. For every λ > 0, −1 < u ≤ U , and a ∈ [a0 , A],
                                   λ|ws (a)| cosh(ua) ≤ (1 − cϵ)µλ,1+u (a).
At the target saddle,
                               Z A
                                                              1   π
                                     ws (a)a sinh(u0 a) da = − log + O(ϵ),
                                  a0                          2   2
                                       Z B+1
                                               wB (a)a sinh(u0 a) da ≤ Ce−c/ϵ .
                                                                                  2
                                  0≤
                                        B
Finally, the target-saddle contribution and the remote-saddle domination ratio satisfy
                       BQe(u0 −1)B ≤ Ce−c/ϵ ,           C0 Q−1 e−(U −1)(B−A) ≤ Ce−c/ϵ .
                                                 2                                           2



The implicit constant in O(ϵ) is absolute.
Proof. Write
                                                    e−2a
                                               w∗ (a) = −   .
                                                 2a2 cosh a
The negative shell agrees with w∗ , up to its taper, on [a0 , A]. Its omitted saddle contributions
are                                                                                 !
           Z a0                                  Z ∞
                                                                               e−2A
                |w∗ (a)|a sinh a da = O(a0 ),         |w∗ (a)|a sinh a da = O         ,
            0                                     A                             A
because tanh a ≤ min(a, 1). The taper changes the same integral by only
           Z A                                                Z ∞                          !
                                                                            e−2a tanh a
                 |1 − b(a)| |w∗ (a)|a sinh a da = O ϵ               (1 + a)             da       = O(ϵ).
            a0                                                0                  a
Moving from u = 1 to u = u0 contributes another O(ϵ): the mean-value theorem gives
                 Z A                                                Z ∞
                                                                          e−2a cosh(u0 a)
                       |ws (a)|a| sinh(u0 a) − sinh a| da  ϵ                             da  ϵ.
                  a0                                                 0        cosh a
                                                              R∞
Since a0 = o(ϵ) and e−2A /A = o(ϵ), the identity 0 w∗ (a)a sinh a da = − 2 log(π/2) now gives
                                                                         1

the asserted negative-shell saddle displacement.
  To compare the negative shell with gamma damping, divide its density by µλ,1+u :
           λ|ws (a)| cosh(ua)                     cosh(ua)                                1 − e−2a/λ
                              = b(a)Θλ (a)e(u−1)a          ,                   Θλ (a) =              .
              µλ,1+u (a)                           cosh a                                    2a/λ
The ﬁnite-dimensional correction satisﬁes 0 < Θλ (a) ≤ 1, by 1 − e−x ≤ x. When −1 < u ≤ 1,
both e(u−1)a and cosh(ua)/ cosh a are at most 1, so the ratio is at most b(a). When 1 ≤ u ≤ U ,
the elementary inequality cosh(ua) ≤ e(u−1)a cosh a bounds it by b(a)e2(u−1)a ≤ b(a)eϵa . Since
ϵA = o(1), uniformly on the negative shell,
                          b(a)eϵa = (1 − 2ϵ(1 + a))(1 + ϵa + O(ϵ2 a2 )) ≤ 1 − cϵ.
Thus the taper retains a damping margin of order ϵ on every contour −1 < u ≤ U .
   It remains to check that the positive shell has opposite eﬀects at the two saddle locations. At
u0 , sinh(u0 a)/ cosh a ≤ e(u0 −1)a , and hence
                             Z B+1
                        0≤             wB (a)a sinh(u0 a) da ≤ (B + 1)Qe(u0 −1)(B+1) .
                              B
The amplitude in (34) has exponential slope strictly between u0 − 1 and U − 1. Hence
                                  Qe(u0 −1)B = e−cϵB ,            Qe(U −1)B = ecϵB
for an absolute c > 0. Since ϵB = ϵ−2 , while B and C0 grow only polynomially in 1/ϵ, both
                                0 2
separation quantities are O(e−c /ϵ ) for another absolute c0 > 0. The same estimate controls the
positive-shell saddle displacement.                                                           □


                                                         13
  The shells now determine the common envelope; it remains to impose the Fourier symmetries
and select the signs. The ﬁrst gamma pole occurs at t = −iλ, or ζ = −i. Thus P0 should vanish
at −i, while P± should take the same positive value there. Reﬂection ζ 7→ −ζ should also
exchange P− with P+ . These requirements lead to the following envelope and polynomials:
                                                                  
                                                λ − it λhϵ (t/λ)
                                             it/2
                               Eλ (t) = π Γ             e        ,
                                                   2
                   P± (ζ) = 1 + ζ 2 + β ± iζ(1 + ζ 2 ),   P0 (ζ) = −(1 + ζ 2 ),                           (38)
                                                              Z
                                                          r−λ
           Xfj (t) = Eλ (t)Pj (t/λ),        fj (r) =                  Xfj (t)rit dt   (j ∈ {−, 0, +}).
                                                          2π      R
Indeed, P− (−ζ) = P+ (ζ), P0 is even, and
                                P± (−i) = β > 0,                 P0 (−i) = 0.
On the imaginary saddle branch,
                                  P+ (iu) = β + (1 − u)2 (1 + u),
                                  P− (iu) = β + (1 − u)(1 + u)2 ,                                         (39)
                                   P0 (iu) = u − 1.
                                                  2


Consequently P+ (iu) > 0 for every u > −1, whereas β = u0 − 1 gives
                                          2 !                                          2
                         ϵ       ϵ                                                    ϵ
             P− (iu0 ) =   1− 2+                  < 0,            P0 (iu0 ) = 1 +              − 1 > 0.
                         4       4                                                    4
The saddle calculation below will transfer precisely these polynomial signs to the radial func-
tions.
Lemma 4.3. For every suﬃciently small ϵ > 0 and every integer d ≥ 1, with λ = d/2, the
inverse Mellin integrals in (38), initially deﬁned for r > 0, extend to fj ∈ Srad (Rd ; R) for
j ∈ {−, 0, +}. These extensions satisfy fb− = f+ , fb0 = f0 , f− (0) = f+ (0) > 0, and f0 (0) = 0.
Proof. Fix d and ϵ. Compact support of w makes hϵ entire, and on each horizontal line t = s+iτ
it gives                                   Z              ∞
                         |hϵ ((s + iτ )/λ)| ≤ 2               |w(a)| cosh(aτ /λ) da.
                                                      0
Thus the perturbation is bounded on every ﬁxed horizontal strip. Uniformly for τ in compact
pole-free intervals, the standard gamma asymptotics [DLMF, § 5.11] give
                        |Xfj (s + iτ )| ≤ Cd,ϵ,τ (1 + |s|)(λ+τ −1)/2+3 e−π|s|/4 .
In particular, the vertical sides of rectangular contour shifts tend to zero. Shifting the Mellin
contour upward arbitrarily far proves rapid decay as r → ∞, also after diﬀerentiation. Shifting
downward past the gamma poles
                               t = −i(λ + 2n),                 n = 0, 1, 2, . . . ,
gives an expansion in even powers r2n , with a remainder of arbitrarily high order. Thus each
fj extends to a smooth radial Schwartz function on Rd . Conjugate symmetry of its real-line
Mellin data makes this extension real.
   Because hϵ is even, the envelope obeys mλ (t)Eλ (−t) = Eλ (t). The polynomial reﬂection
identities and the multiplier (10) therefore give
                                         fb− = f+ ,            fb0 = f0 .                                 (40)
 Finally, the value at the origin is determined by the ﬁrst pole of the downward-shifted contour.
More generally, Resz=−n Γ(z) = (−1)n /n! shows that the pole t = −i(λ + 2n) contributes
                                      (−1)n λhϵ (−i(1+2n/λ))
                       2π λ/2+n r2n        e                 Pj (−i(1 + 2n/λ)).                           (41)
                                        n!

                                                      14
At n = 0, evenness gives hϵ (−i) = hϵ (i), and P± (−i) = β, whereas P0 (−i) = 0. Consequently,

                      f+ (0) = f− (0) = 2π λ/2 eλhϵ (i) β > 0,          f0 (0) = 0.             (42)
                                                                                                  □


4.3. Saddle geometry. Recall u0 and U from (34), and set

                                                           log λ
                                            u∗ = −1 +            .                              (43)
                                                            4λ

   To determine the signs of the Mellin integrals (38), we associate each contour t = λ(T + iu)
with the radius r = ev(u) at which Eλ (t)rit is stationary in T . The decrease Du (T ) of its
logarithmic modulus must remain positive away from T = 0. We establish this ﬁrst using the
gamma contribution when u∗ ≤ u ≤ U , and then using the positive shell wB when u ≥ U . The
resulting saddle estimates will identify the sign of each integral with the sign of Pj (iu).
   Put
                                              λη
                 η = 1 + u > 0,         m=       ,         ψ = (log Γ)0 ,       ψ (1) = ψ 0 .
                                               2
Take the branch of log Γ on Re z > 0 which is real on the positive axis. On the contour
t = λ(T + iu), the logarithm of Eλ (t)rit is
                                                    
             iλ(T + iu)                   iλT
                        log π + log Γ m −                 + λhϵ (T + iu) + iλ(T + iu) log r.
                 2                         2

Its derivative with respect to T at T = 0 equals
                                              Z ∞                                    
                      1        1
                   iλ   log π − ψ(m) −                w(a)a sinh(ua) da + log r .
                      2        2                0


Thus T = 0 is stationary precisely when r = ev(u) , where
                                                          ∞     Z
                                    1         1
                          v(u) = − log π + ψ(m) +           w(a)a sinh(ua) da,
                                    2         2         0
                                               Z ∞                                              (44)
                                  λ
                 V (u) = v 0 (u) = ψ (1) (m) +     w(a)a2 cosh(ua) da.
                                  4             0


Diﬀerentiating the saddle log-radius gives V (u) = v 0 (u). Thus V (u) > 0 makes ev(u) increase
with u; the quadratic decrease of the logarithmic modulus at T = 0 is λV (u)T 2 /2.
   To separate the gamma and shell contributions to this decrease, recall the positive density
µλ,η from (37). The standard log-gamma integral [DLMF, § 5.9], after substituting a = λs/2,
gives

                                                                            iλT
                   Gλ,η (T ) := log Γ(m − iλT /2) − log Γ(m) +                  ψ(m)
                                Z ∞                                          2
                            =         (eiaT − 1 − iaT )µλ,η (a) da,                             (45)
                                  0
                                                     Z ∞
                     Dγ (T ) := − Re Gλ,η (T ) =            (1 − cos(aT ))µλ,η (a) da.
                                                      0

In particular, the gamma function in the Mellin envelope always damps the integrand away
from T = 0.


                                                     15
  Normalize Eλ (λ(T + iu))riλT by Eλ (iλu) and set r = ev(u) . The linear contributions cancel
by the saddle equation, and (36) gives
                                      Eλ (λ(T + iu))
                    Lu (T ) := log                   + iλT v(u)
                                         Eλ (iλu)
                                                Z ∞
                             = Gλ,η (T ) + λ               w(a) cosh(ua)(cos(aT ) − 1) da
                                                   0
                                      Z ∞
                               + iλ         w(a) sinh(ua)(aT − sin(aT )) da,                (46)
                                       0
                   Du (T ) := − Re Lu (T )
                                              Z ∞
                             = Dγ (T ) + λ             w(a) cosh(ua)(1 − cos(aT )) da.      (47)
                                               0
  Equation (47) isolates the main diﬃculty: ws reduces Du (T ), while wB increases it. We must
prove Du (T ) > 0 for every T 6= 0 and V (u) > 0 for every u ≥ u∗ . The gamma density will
dominate ws on [u∗ , U ], whereas wB will dominate ws on [U, ∞).
  The quadratic and cubic sizes of the phase are measured by
                         Z
                    1 ∞ 2               λ
                Vγ =    a µλ,η (a) da = ψ (1) (m),
                    λ 0                  4
                     Z                  Z ∞                                                 (48)
                    1 ∞ 3                                    
               M3 =     a µλ,η (a) da +     |ws (a)| + wB (a) a3 cosh(ua) da.
                    λ 0                  0
  Here Vγ is the gamma contribution to V (u), and M3 bounds the cubic error after the signed
shell contributions have been replaced by their absolute values.
  For later comparisons, write
                                      Z A
                        Ds (T ) = λ         |ws (a)| cosh(ua)(1 − cos(aT )) da,
                                       a0
                                      Z B+1
                       DB (T ) = λ             wB (a) cosh(ua)(1 − cos(aT )) da,
                                       B
                                    Z A                                                     (49)
                             Vs =          |ws (a)|a cosh(ua) da,
                                                       2
                                     a0
                                    Z B+1
                             VB =            wB (a)a2 cosh(ua) da.
                                      B
In particular, Du = Dγ − Ds + DB and V (u) = Vγ − Vs + VB .
Lemma 4.4. There are absolute constants c, C > 0 such that, for every λ > 0, u > −1
satisfying λ(1 + u) ≥ 1, and T ∈ R, the phase and quantities deﬁned in (44)–(48) satisfy
                                               λV (u) 2
                                  Lu (T ) +          T ≤ CλM3 |T |3 .                       (50)
                                                 2
Moreover, writing η = 1 + u,
                                         1        C
                                            ≤ Vγ ≤ ,                                        (51)
                                        2η        η
                         Z ∞
                       1                      C
                             a3 µλ,η (a) da ≤ 2 ,                                           (52)
                       λ 0                    η
                                                                         !
                                                                 T2
                                      Dγ (T ) ≥ cλ min              , |T |    (T ∈ R).      (53)
                                                                 η
Proof. The globally valid Taylor estimates
                                      x2
                     eix − 1 − ix = −    + O(|x|3 ),    x − sin x = O(|x|3 )
                                       2
applied to (45) and (46), and using | sinh(ua)| ≤ cosh(ua), give (50).


                                                           16
   Since m = λη/2 ≥ 1/2, the variance and third-moment bounds are the standard uniform
trigamma and polygamma estimates [DLMF, §§ 5.9, 5.11, 5.15]; indeed,
                                               Z
                        λ               1 ∞ 3                  λ2
                   Vγ = ψ (1) (m),            a µλ,η (a) da = − ψ (2) (m).
                         4              λ 0                    8
                                                −x
  To bound Dγ (T ) at every frequency, use 1 − e ≤ x in (37):
                                                   λe−ηa
                                          µλ,η (a) ≥     .
                                                    2a2
For T 6= 0, take L = min(η −1 , |T |−1 ). On 0 < a < L, both e−ηa and (1 − cos(aT ))/(a2 T 2 ) are
bounded below by absolute positive constants. Therefore Dγ (T ) ≥ cλT 2 L, which is (53); the
case T = 0 is immediate.                                                                        □
  The lower endpoint (43) ensures that the gamma shape parameter grows throughout the
saddle analysis:
                                         λ(1 + u∗ )   1
                                   m≥               = log λ.
                                             2        8
  Lemma 4.4 controls the gamma contribution and cubic remainder. We next show that, for
u∗ ≤ u ≤ U , the negative shell removes at most a (1 − cϵ)-fraction of the gamma damping, while
wB contributes nonnegative damping.
Lemma 4.5. There is ϵ0 > 0 and an absolute c > 0 such that, for every 0 < ϵ < ϵ0 , there are
constants Cϵ , λϵ > 0 with the following property. For every λ ≥ λϵ , every u∗ ≤ u ≤ U , and
η = 1 + u,
                λ|ws (a)| cosh(ua) ≤ (1 − cϵ)µλ,η (a)                       (a ∈ [a0 , A]),   (54)
                            Du (T ) ≥ cϵDγ (T )                             (T ∈ R),          (55)
                                cϵ             Cϵ
                                    ≤ V (u) ≤     ,                                           (56)
                                 η              η
                                      Cϵ
                               M3 ≤ 2 .                                                       (57)
                                      η
Moreover, λη ≥ (log λ)/4.
Proof. Lemma 4.2 gives (54). Integrating that inequality against 1 − cos(aT ) ≥ 0 shows that
the negative shell removes at most a (1 − cϵ)-fraction of the gamma damping. The contribution
of wB is nonnegative. Therefore
                                              Z A
               Du (T ) ≥ Dγ (T ) − (1 − cϵ)         (1 − cos(aT ))µλ,η (a) da ≥ cϵDγ (T ),
                                               a0
proving (55).
  For the curvature, integrating (54) against a2 /λ and using (49) gives Vs ≤ (1 − cϵ)Vγ , and
hence
                                                                cϵ
                            V (u) = Vγ − Vs + VB ≥ cϵVγ + VB ≥ .
                                                                η
For u∗ ≤ u ≤ U , the positive-shell variance satisﬁes
                              VB ≤ (B + 1)2 Qe(U −1)(B+1) = Oϵ (1).
Moreover, λη ≥ (log λ)/4, so (51) gives
                                   V (u) ≤ Vγ + VB = Oϵ (η −1 ),
because η ≤ 2 + ϵ/2. This proves (56).
  Similarly, the negative-shell third moment is bounded by the gamma third moment:
                        Z A                                  Z ∞
                                                     1
                             |ws (a)|a cosh(ua) da ≤
                                      3
                                                                   a3 µλ,η (a) da.
                          a0                         λ        0
The positive-shell third moment is Oϵ (1). Consequently, (52), λη ≥ (log λ)/4, and η ≤ 2 + ϵ/2
give (57).                                                                                  □


                                                     17
  We have proved positive damping and curvature for u∗ ≤ u ≤ U . When u > U , the factor
cosh(ua) in (47) can make ws overwhelm the gamma contribution. Put δ = u − 1. For T 6= 0,
the ratios Ds (T )/(λ min(T 2 , 1)) and DB (T )/(λ min(T 2 , 1)) have respective sizes at most C0 eδA
and at least QeδB . The separation in Lemma 4.2 therefore makes wB dominate ws throughout
u ≥ U.
  The interval support [B, B + 1] of wB prevents frequency resonances: a shell concentrated at
one a would have DB (T ) = 0 whenever aT ∈ 2πZ, whereas
                     Z B+1
                             (1 − cos(aT )) da = 1 − sinc(T /2) cos((B + 21 )T ).               (58)
                       B

Here sinc(x) = sin(x)/x, with sinc(0) = 1. Since 1 − | sinc(T /2)|  min(T 2 , 1), (58) is positive
for every T 6= 0, uniformly at both small and large frequencies.
   Deﬁne the separation error
                                                                         
                                                     ϵ
                              ρϵ = (A + a−1
                                         0 )Q
                                             −1
                                                exp − (B − A) .
                                                     2
Lemma 4.2 gives ρϵ = O(e−c/ϵ ) = o(1) as ϵ ↓ 0. The next lemma bounds Ds (T )/DB (T ) by
                                  2


O(ρϵ ), uniformly for u ≥ U and T 6= 0; it also gives the curvature and third-moment bounds
required for the saddle approximation.
Lemma 4.6. There are absolute constants c, C > 0 and ϵ0 > 0 such that, for every 0 < ϵ < ϵ0 ,
there are constants λϵ , Cϵ , cϵ > 0 with the following property. For every λ ≥ λϵ , every u ≥ U ,
and every T ∈ R, writing δ = u − 1, one has
                                      Ds (T ) ≤ CλC0 eδA min(T 2 , 1),                          (59)
                                      DB (T ) ≥ cλQe   δB         2
                                                            min(T , 1).                         (60)
Consequently,
                                       Ds (T ) ≤ Cρϵ DB (T ),                                   (61)
                                       Du (T ) ≥ Dγ (T ) + cDB (T ),                            (62)
                                         cVB ≤ V (u) ≤ CVB .                                    (63)
The shell variance and third moments obey
                                           cB 2 QeδB ≤ VB ≤ (B + 1)2 Qeδ(B+1) ,                 (64)
                       Z A
                             |ws (a)|a3 cosh(ua) da ≤ CAρϵ VB ,                                 (65)
                        a0
                     Z B+1
                             wB (a)a3 cosh(ua) da ≤ (B + 1)VB .
                       B
In particular,
                           M3 ≤ Cϵ V (u),         V (u) ≥ cϵ > 0       (u ≥ U ).                (66)
Proof. For u = 1 + δ, the explicit shell densities satisfy
                                              eδa
                      |ws (a)| cosh(ua)          ,         wB (a) cosh(ua)  Qeδa .
                                              a2
If |T | ≤ 1, the bound 1 − cos(aT ) = O(a2 T 2 ) gives
                                                 Z A
                               Ds (T )  λT 2          eδa da  λAeδA T 2 .
                                                  a0

If |T | ≥ 1, use 1 − cos(aT ) = O(1):
                                                 Z A
                               Ds (T )  λeδA          a−2 da  λa−1 δA
                                                                  0 e .
                                                  a0



                                                       18
These two estimates give (59). On the positive shell, (58) yields
                                     Z B+1
                 DB (T )  λQeδB             (1 − cos(aT )) da  λQeδB min(T 2 , 1).
                                      B
  For T 6= 0, division gives (61), since
                             Ds (T )
                                      C0 Q−1 e−δ(B−A) ≤ ρϵ = o(1).
                             DB (T )
At T = 0, both damping terms vanish. Comparing their quadratic coeﬃcients in (49) gives
Vs = O(ρϵ VB ). Choose ϵ0 so that the implicit constant times ρϵ is less than 1/2. Then Du =
Dγ − Ds + DB proves (62), and V (u) = Vγ − Vs + VB gives
                                   Vγ + cVB ≤ V (u) ≤ Vγ + VB .
  Integrating wB (a) cosh(ua)  Qeδa against a2 gives (64). Since δ ≥ ϵ/2,
                      VB  B 2 QeϵB/2 = B 2 ecϵB  1,          Vγ  η −1  1.
Thus Vγ = O(VB ), so the preceding comparison of V (u) with Vγ + VB gives (63). Since a ≤ A
on the negative shell,
                           Z A
                                 |ws (a)|a3 cosh(ua) da ≤ AVs  Aρϵ VB ,
                            a0
while a ≤ B + 1 bounds the positive-shell third moment by (B + 1)VB . This proves (65).
  Since η ≥ 2 + ϵ/2, (51) and (52) bound the gamma third moment by O(Vγ ). The shell third
moments are Oϵ (VB ), while Vγ = O(VB ) and (63) gives VB  V (u). Hence M3 = Oϵ (V (u)).
Finally, (64) and (63) give V (u)  VB  B 2 QeϵB/2 =: cϵ > 0, proving (66).            □
   Set T0 = (2(B + 1))−1 .
   Lemma 4.6 controls the total damping for u ≥ U . To bound the tails of the saddle integral,
we sharpen that control on three frequency ranges: |T | ≤ T0 , where Du (T ) is quadratic; T0 ≤
|T | ≤ η, where wB supplies a uniform positive ﬂoor; and |T | ≥ η, where the gamma contribution
also grows linearly.
Lemma 4.7. There is ϵ0 > 0 and an absolute c > 0 such that, for every 0 < ϵ < ϵ0 , there are
constants cϵ , λϵ > 0 with the following property. For every λ ≥ λϵ and u ≥ U , set η = 1 + u and
δ = u − 1. Then
                  Du (T ) ≥ cϵ λV (u)T 2                           (|T | ≤ T0 ),             (67)
                  Du (T ) ≥ cϵ λQeδB                               (T0 ≤ |T | ≤ η),          (68)
                  Du (T ) ≥ cλ|T | + cϵ λQeδB                      (|T | ≥ η).               (69)
Proof. First suppose that |T | ≤ T0 . Since |aT | ≤ 1/2 on [B, B + 1], 1 − cos(aT )  a2 T 2 , and
therefore
                                        DB (T )  λVB T 2 .
Since η ≥ 2 + ϵ/2 and |T | ≤ η, (53) and (51) also give
                                                λT 2
                                     Dγ (T )         λVγ T 2 .
                                                  η
Combining these contributions using (62) and (63) proves (67).
  Next, if T0 ≤ |T | ≤ η, then min(T 2 , 1) ≥ T02 . Thus (62) and (60) give
                                  Du (T )  λT02 QeδB ϵ λQeδB .
This proves (68).
  Finally, if |T | ≥ η, then min(T 2 , 1) = 1 and (53) gives Dγ (T )  λ|T |. Adding the positive
shell through (62) and (60) yields
                                      Du (T )  λ|T | + λQeδB ,
which proves (69).                                                                              □


                                                   19
4.4. Global saddle asymptotics. The damping bounds now determine the exterior signs of
f+ , f− , f0 . On each contour, the centered phase is quadratic near T = 0, the factor Pj (T + iu)
is asymptotic to Pj (iu), and the remaining contour is negligible. We establish these claims
separately for the gamma-controlled range u∗ ≤ u ≤ U and the positive-shell-controlled range
u ≥ U.
Lemma 4.8. Fix 0 < ϵ < ϵ0 , let λ = d/2, and recall u0 , U from (34) and u∗ from (43). For
u > −1 and P ∈ {P+ , P− , P0 }, put
                                                Z
                                   Iλ,P (u) =         eLu (T ) P (T + iu) dT.
                                                  R
As d → ∞,
                                                       s
                                                            2π              
                                 Iλ,P (u) = P (iu)                1 + oϵ (1) ,                  (70)
                                                           λV (u)
uniformly for u ≥ u∗ when P = P+ , and uniformly for u ≥ u0 when P = P− or P = P0 . More
precisely,
                                  p
                                    λV (u)Iλ,P+ (u)
                             sup     √              − 1 −→ 0,
                            u≥u∗       2πP+ (iu)
                                              p
                                                  λV (u)Iλ,Pj (u)
                                max sup           √               − 1 −→ 0.
                               j∈{−,0} u≥u0         2πPj (iu)
Proof. The poles of the integrand in (38) are t = −i(λ + 2n), n ≥ 0. Hence Lemma 4.3 allows
the contour to be shifted to t = λ(T + iu) whenever u > −1. At r = ev(u) , the shifted Mellin
inversion formula is
                                          λEλ (iλu) −(1+u)λv(u)
                            fj (ev(u) ) =          e            Iλ,Pj (u).                 (71)
                                            2π
The prefactor of Iλ,Pj (u) is positive. By (39), P+ (iu) > 0 for u > −1, while P− (iu) < 0 and
P0 (iu) > 0 for u ≥ u0 . Their ﬁxed degrees and uniform lower bounds on those ranges imply
                 |P (T + iu)|                           P (T + iu)
                              ϵ 1 + |T |3 ,                       = 1 + Oϵ (|T | + |T |3 ).    (72)
                   |P (iu)|                               P (iu)
  To compare Iλ,P (u) with its Gaussian approximation, choose K → ∞, and set
                                                            K
                                               T∗ = p             .
                                                           λV (u)
By (50), the phase on |T | ≤ T∗ is
                                        λV (u) 2               
                                 Lu (T ) = −   T + O λM3 |T |3 .
                                           2
The approximation is uniform if its central interval shrinks and its cubic error tends to zero:
                                                           K 3 M3
                                 T∗ = oϵ (1),          √              = oϵ (1).
                                                           λ V (u)3/2
                                                                   p
Under these conditions, (72) and the substitution x =                  λV (u)T give
                    Z                                                 s
                                                                           2π              
                               eLu (T ) P (T + iu) dT = P (iu)                   1 + oϵ (1) .
                     |T |≤T∗                                              λV (u)
                                                                                p
It remains to show that the integral over |T | > T∗ is oϵ (|P (iu)|/ λV (u)). We verify the central
approximation and this tail bound separately on [u∗ , U ] and [U, ∞).
   First suppose u∗ ≤ u ≤ U , and put η = 1 + u, L = λη. Equations (56) and (57) give
                                 1
                         L≥        log λ,       V (u) ϵ η −1 ,            M3 ϵ η −2 .
                                 4

                                                        20
                                               √
Choosing K = L1/12 , so that K → ∞ and K 3 = o( L), gives
                                T∗                                 K 3 M3
                                   ϵ L−5/12 ,                 √              ϵ L−1/4 .
                                η                                  λV (u) 3/2

The damping bounds (55) and (53) are quadratic for |T | ≤ η and linear for |T | ≥ η. Conse-
quently,
                                                                       λV (u) 2
                                                sup Lu (T ) +                T ϵ L−1/4 ,
                                               |T |≤T∗                   2
                        q             Z
                                                        (1 + |T |3 )e−Du (T ) dT ϵ e−cϵ K ,
                                                                                                   2
                            λV (u)
                                         T∗ ≤|T |≤η
                               q            Z
                                   λV (u)               (1 + |T |3 )e−Du (T ) dT ϵ e−cϵ L .
                                               |T |≥η

Both tail estimates tend to zero uniformly because L ≥ (log λ)/4, proving (70) for u∗ ≤ u ≤ U .
  Now suppose u ≥ U , and write δ = u − 1. By (63) and (66), the remote shell controls both
the curvature and the third moment:
                                    V (u) ϵ VB ϵ 1,                   M3 ϵ V (u).
Take K = λ1/12 . Then
                                                                  K 3 M3
                                T∗ ϵ λ−5/12 ,                √              ϵ λ−1/4 .
                                                                  λV (u) 3/2

In particular, T∗ < T0 for all suﬃciently large λ. The quadratic bound (67) on |T | ≤ T0 yields
                                                                       λV (u) 2
                                                 sup Lu (T ) +               T ϵ λ−1/4 ,
                                                |T |≤T∗                  2
                        q            Z                                                                                      (73)
                                                                        −Du (T )              −cϵ K 2
                            λV (u)                       (1 + |T | )e
                                                                   3
                                                                                    dT ϵ e             .
                                      T∗ ≤|T |≤T0

  For T0 ≤ |T | ≤ η, the variance bound (64) and the damping estimate (68) give
                  q            Z
                      λV (u)                   (1 + |T |3 )e−Du (T ) dT
                                T0 ≤|T |≤η
                               √                                                                                          (74)
                                               B+1
                        ϵ         λ exp           δ + 4 log(2 + δ) − cϵ λQeBδ                    = oϵ (1).
                                                2
The exponent on the right of (74) decreases in δ ≥ ϵ/2, since its derivative is (B + 1)/2 + 4/(2 +
δ) − cϵ λBQeBδ < 0 for suﬃciently large λ. At δ = ϵ/2, that exponent is −cϵ λ + Oϵ (1). Thus
the middle-frequency contribution tends to zero uniformly even as u → ∞.
   Finally, for |T | ≥ η, (69) supplies the positive-shell damping and a linear gamma tail, so
                            q              Z
                                λV (u)               (1 + |T |3 )e−Du (T ) dT ϵ e−cϵ λ ,                                   (75)
                                            |T |≥η
                                                                                                            p
uniformly in δ: as in (74), the damping −cϵ λQeBδ absorbs the growth of                                         V (u). Equations
(73)– (75) prove the saddle formula on every u ≥ U .                                                                          □
Corollary 4.9. For every ﬁxed 0 < ϵ < ϵ0 , there is dϵ such that, for every integer d ≥ dϵ ,
                                               f+ (r) > 0 (r ≥ ev(u∗ ) ),
                                               f− (r) < 0 (r ≥ ev(u0 ) ),                                                   (76)
                                                f0 (r) > 0 (r ≥ e         v(u0 )
                                                                                   ).
Proof. For u > −1, the prefactor of Iλ,Pj (u) in (71) is positive. Hence (70) identiﬁes the sign
of fj (ev(u) ) with that of Pj (iu). Equations (56) and (63) give v 0 (u) = V (u) > 0 on [u∗ , ∞),
while (44) and the positive shell wB give v(u) → ∞. Thus [u∗ , ∞) parametrizes every radius
r ≥ ev(u∗ ) , and [u0 , ∞) parametrizes every radius r ≥ ev(u0 ) . The signs in (39) now give (76). □


                                                               21
4.5. Positivity and the sharp upper bound. Corollary 4.9 proves the required signs outside
the saddle radii. To ﬁnish the construction, we must also show f+ (r) > 0 for 0 ≤ r ≤ r∗ = ev(u∗ ) .
Shifting the Mellin contour below O(log λ) gamma poles expresses f+ (r)/f+ (0) as a truncated
exponential series plus a uniformly negligible remainder.
                                                                                 R∞
Lemma 4.10. Fix 0 < ϵ < ϵ0 , let λ = d/2, set r∗ = ev(u∗ ) , and write h01 =     0    w(a)a sinh a da.
As d → ∞,
                                       2h0 2 f+ (r)
                              sup eπe 1 r           − 1 −→ 0.
                            0≤r≤r∗           f+ (0)
In particular, f+ (r) > 0 on [0, r∗ ] for all suﬃciently large d.

Proof. First identify the range on which the truncated exponential series must approximate e−y .
Put
                                     Z ∞
                    0                                                          log λ
           y = πe2h1 r2 ,    H(u) =       w(a)a sinh(ua) da,    η∗ = 1 + u∗ =        .
                                      0                                         4λ
The normalized contour height u∗ tends to −1, the normalized height of the ﬁrst gamma pole,
while the gamma shape parameter λ(1 + u∗ )/2 = (log λ)/8 still diverges. This choice makes
(70) applicable and keeps y(r∗ ) logarithmic. Indeed, H is odd and, for ﬁxed ϵ, has bounded
derivative near −1. Consequently

                          H(u∗ ) + h01 = H(−1 + η∗ ) − H(−1) = Oϵ (η∗ ).

By (44),
                                                                      
                                               λη∗
                            y(r∗ ) = exp ψ               + 2H(u∗ ) + 2h01 .
                                                2
The standard digamma asymptotic [DLMF, § 5.11] and λη∗ /2 = (log λ)/8 therefore give
                                                     1
                                 0 ≤ y ≤ y(r∗ ) =      log λ + Oϵ (1).                           (77)
                                                     8
Since e−y can be as small as a negative power of λ on (77), the approximation error must be
controlled relative to e−y .
  To recover enough exponential-series coeﬃcients, set
                                                 1                        2p
                          N = dlog λe,       p=N+ ,              κ=1+        .
                                                 2                        λ
Since p = N + 1/2, the contour t = s − i(λ + 2p) lies strictly between consecutive gamma poles.
Furthermore, p  log λ makes the exponential-series tail negligible on (77). To justify shifting
to this contour, we verify that the multiplier eλhϵ (t/λ) preserves a uniform exponential decay
margin. Indeed, pA/λ = oϵ (1), so the negative-shell taper satisﬁes

                               b(a)e2pa/λ ≤ 1 − cϵ         (a0 ≤ a ≤ A)

for an absolute c > 0 and all suﬃciently large λ. For every intermediate contour height 0 ≤ q ≤ κ,
the positive shell contributes nonpositively to Re hϵ (s/λ − iq) − hϵ (iq), and the negative shell
gives
                                                             Z
                                                (1 − cϵ)λ ∞ 1 − cos(as/λ)
                  λ Re hϵ (s/λ − iq) − hϵ (iq) ≤                              da
                                                      2       0       a2
                                                           π|s|
                                                = (1 − cϵ)      .
                                                            4
Standard gamma asymptotics [DLMF, § 5.11] supply the complementary factor e−π|s|/4 . Hence
the integrand decays like e−cϵ |s| on the vertical sides, permitting the shift in (38) to t = s −
i(λ + 2p). This shift crosses exactly the poles t = −i(λ + 2n), 0 ≤ n ≤ N .


                                                  22
  Applying the residue formula (41) and the origin value (42) gives
                        f+ (r)   X
                                 N
                                   (−y)n
                               =         Aλ,n + Rλ,p (r),                                                           (78)
                        f+ (0) n=0 n!
                                                                                0   P+ (−i(1 + 2n/λ))
                          Aλ,n = eλ[hϵ (i(1+2n/λ))−hϵ (i)]−2nh1                                       ,
                                                                                            β
                                n(1 + n)
                    |Aλ,n − 1| ϵ                                (0 ≤ n ≤ N ).                                      (79)
                                    λ
Indeed, Taylor expansion at u = 1 gives
                                                                !                                        
                2n                                               n2                 P+ (−i(1 + 2n/λ))          n
   λ hϵ    i 1+           − hϵ (i)       = 2nh01 + Oϵ                     ,                           = 1 + Oϵ   ,
                 λ                                               λ                          β                  λ
uniformly for n ≤ N ; here N 2 /λ = o(1).
  For r > 0, the remainder Rλ,p (r) in (78) is the integral over t = s − i(λ + 2p):
                                                         Z
                                      π λ/2+p r2p
                      Rλ,p (r) =                              π is/2 Γ(−p − is/2)
                                       2πf+ (0)           R

                                                          · eλhϵ (s/λ−iκ) P+ (s/λ − iκ)ris ds.
The gamma reﬂection and product estimates [DLMF, §§ 5.5, 5.8], together with p ∈ Z + 21 , give
the standard bound
                                                            e−π|s|/4
                                                     |Γ(−p − is/2)| ,
                                                            Γ(1 + p)
                                                                 π|s|
                         λ Re hϵ (s/λ − iκ) − hϵ (iκ) ≤ (1 − cϵ)        .
                                                                     4
Since P+ (s/λ − iκ)/β = Oϵ (1 + |s|3 ), integration in s now gives
                                                                                        yp
                                                              |Rλ,p (r)| ϵ                   .                     (80)
                                                                                     Γ(1 + p)
Here we used
                                                                                                  0
                   λ[hϵ (iκ) − hϵ (i)] = 2ph01 + Oϵ (p2 /λ),                          (πr2 )p e2ph1 = y p ,
and absorbed p2 /λ = o(1). The estimate extends to r = 0 by continuity.
  To compare (78) with e−y , wePbound the coeﬃcient errors Aλ,n − 1, the contour remainder
Rλ,p (r), and the omitted terms n>N (−y)n /n!. Equations (79), (80), and (77) give
                               X
                               N
                                 yn                               (1 + y)2 e2y    (log λ)2
                          ey              |Aλ,n − 1| ϵ                        ϵ          ,
                               n=0
                                     n!                                λ            λ3/4
                                                                    ey y p
                                         ey |Rλ,p (r)| ϵ                  ,                                        (81)
                                                                  Γ(1 + p)
                                               X yn               ey y N +1
                                          ey                               .
                                               n>N
                                                     n!          (N + 1)!
                                          P
The ﬁrst estimate follows from n≥0 n(1 + n)y n /n! = (y 2 + 2y)ey . For the two tails, put
L = log λ. Since y ≤ L/8 + Oϵ (1) and p = L + O(1), Stirling’s formula [DLMF, § 5.11] gives
                                                                             
                                   ey y p                1
                           log            ≤                + 1 − log 8 L + Oϵ (log L).
                                 Γ(1 + p)                8
The same estimate holds with p replaced by N + 1. Since 1/8 + 1 − log 8 < 0, both tails are
smaller than the coeﬃcient error in (81). Therefore (78) yields, uniformly on 0 ≤ r ≤ r∗ ,
                                                                      !!
                     f+ (r)              (log λ)2
                            = e−y 1 + Oϵ                                      >0         (0 ≤ r ≤ r∗ ).             (82)
                     f+ (0)                λ3/4                                                                       □

                                                                 23
Proof of Theorem 4.1. Set Rϵ,d = ev(u0 ) . The Fourier identities and origin values follow from
(40) and (42). Corollary 4.9 gives the required exterior signs, while (82) supplies positivity of
f+ on the remaining interval. Thus
                                fb− = f+ > 0,            f− (0) = f+ (0) > 0,
                                                                                                (83)
                   fb0 = f0 ,      f0 (0) = 0,          f− (r) < 0 < f0 (r) (r ≥ Rϵ,d ).
For ﬁxed ϵ, the saddle equation (44) and the digamma asymptotic [DLMF, § 5.11] give
                                       r                Z ∞                            
                          Rϵ,d    1 + u0
                      lim √ =            exp                       w(a)a sinh(u0 a) da .        (84)
                     d→∞    d       4π                       0
The two shell contributions in Lemma 4.2 give
                            Z ∞
                                                     1   π
                              w(a)a sinh(u0 a) da = − log + O(ϵ).
                          0                          2   2
Since u0 → 1, (33) and (84) give
                                               Rϵ,d   1
                                      lim lim √ = .                                      (85)
                                       ϵ↓0 d→∞    d  π
                                                                                           □
Proof of Theorem 1.1. By (83), the dilation Fϵ,d (x) = f− (Rϵ,d x) is admissible and satisﬁes
Fϵ,d (0)/Fbϵ,d (0) = Rϵ,d
                      d by Fourier scaling. Inserting F
                                                       ϵ,d into (3) gives
                                                  vd d
                                            LPd ≤ d Rϵ,d .                               (86)
                                                  2
The universal lower bound (28), the admissible upper bound (86), and (85), together with
 1/d √       √
vd     d → 2πe, imply
                       r                                        √         r
                           e             1/d             1/d      2πe        e
                             ≤ lim inf LPd ≤ lim sup LPd ≤             =       .           □
                          2π    d→∞             d→∞              2π         2π
Proof of Theorem 1.2. The lower bound is Proposition 3.7. For the upper bound, deﬁne gϵ,d,− =
f+ − f− and gϵ,d,+ = f0 . Equation (40) and Fourier inversion give
                                  gbϵ,d,− = −gϵ,d,− ,            gbϵ,d,+ = gϵ,d,+ .
By (83), both gϵ,d,− and gϵ,d,+ vanish at the origin and are strictly positive outside Rϵ,d ; in par-
ticular, neither is zero. The deﬁnition (6) therefore gives Aς (d) ≤ Rϵ,d for both signs. Combining
this bound with (85) gives
                     1          Aς (d)      Aς (d)         Rϵ,d 1
                       ≤ lim inf √ ≤ lim sup √ ≤ lim lim √ = .                                    □
                     π    d→∞       d  d→∞      d  ϵ↓0 d→∞   d  π

             Appendix A. Comparison of the sign-uncertainty constants
   For an anti-self-Fourier radial function g, the central Mellin moment Mg (d/2) vanishes. In-
tegrating the radial tail of g therefore produces a self-Fourier function with a strictly smaller
last-sign radius.
Proposition A.1. Let d ≥ 1, put λ = d/2, and suppose that 0 6= g ∈ L1rad (Rd ; R) satisﬁes
gb = −g and g(0) = 0. Deﬁne Td g(0) = 0 and, for x 6= 0, set
                                                        Z
                                           λ ∞ λ−1
                                    (Td g)(x) =   t g(tx) dt,                              (87)
                                           2 1
where g denotes its continuous Fourier-inversion representative. Then Td g is nonzero, continu-
ous, and integrable, with
                        Td
                         d g = Td g,       (Td g)(0) = 0,              kTd gk1 ≤ 21 kgk1 .
If r(g) < ∞, then r(Td g) < r(g); if g is Schwartz, then so is Td g. Consequently, the constants
in (6) satisfy
                                  A+ (d) < A− (d)     (d ≥ 1).


                                                        24
              g = −gb ∈ L1 , Fourier inversion makes g bounded and continuous. In particular,
RProof. Since−λ
 Rd |g(x)| |x| dx < ∞, by splitting the integral at |x| = 1. The Mellin–Fourier identity in (9)
was established for Schwartz functions, so we ﬁrst verify its central consequence directly for
                                           R
the integrable eigenfunction g. Set J(t) = Rd g(x)e−πt|x| dx. Gaussian duality and Tonelli’s
                                                          2


theorem give
                                       Z ∞                                       Z
                                                                        Γ(λ/2)
          J(t) = −t−λ J(1/t),                tλ/2−1 |J(t)| dt ≤                        |g(x)| |x|−λ dx < ∞.
                                       0                                 π λ/2    Rd
                                              R
Hence the substitution t 7→ 1/t makes 0∞ tλ/2−1 J(t) dt equal to its negative. Gaussian integra-
tion and polar coordinates therefore give the central Mellin cancellation
                                                     Z ∞
                                     Mg (λ) =                  g(r)rλ−1 dr = 0.                               (88)
                                                         0

  The integral deﬁning Td g(x) converges absolutely for x 6= 0, since g is integrable
                                                                             R ∞ −λ−1and s
                                                                                          λ−1 
                                                                                                 x
sd−1 for s ≥ |x|. Tonelli’s theorem and d = 2λ yield kTd gk1 ≤ (λ/2)kgk1 1 t          dt = kgk1 /2,
also justifying Fourier transformation under the integral. Fourier scaling and (88) give
                                                  Z ∞
                                          λ
                                Td
                                 d g(ξ) =                    tλ−d−1 gb(ξ/t) dt
                                             2       1
                                                     Z
                                            λ 1 λ−1
                                        =−       s g(sξ) ds                                                   (89)
                                            2 0
                                            Z ∞
                                          λ
                                        =       sλ−1 g(sξ) ds = Td g(ξ).
                                          2 1
The small-scale representation in (89) extends continuously to x = 0, with value −g(0)/2 = 0.
Diﬀerentiating the large-scale representation gives (x · ∇ + λ)Td g = −λg/2, so Td g 6= 0. If g
is Schwartz, diﬀerentiating the small-scale representation gives smoothness at the origin, and
diﬀerentiating the large-scale representation gives rapid decay
                                                             R at inﬁnity; thus Td g is Schwartz.
   If R = r(g) < ∞, then R > 0, since otherwise g ≥ 0 and g = gb(0) = −g(0) = 0 would force
g = 0. Hence g(s) ≥ 0 for s ≥ R, and (5) and (87) give
                                                 Z
                                  λ −λ ∞ λ−1
                         (Td g)(r) =r       s g(s) ds > 0       (r ≥ R).
                                  2      r
Indeed, equality at any r ≥ R would make both g and gb = −g compactly supported, con-
tradicting Fourier analyticity. In particular, Td g(R) > 0, so continuity gives r(Td g) < R.
Applying this strict decrease to an attained radial negative-sign extremizer [CG19, Thm. 1.4]
gives A+ (d) < A− (d).                                                                     □

                                                  References
[AJCHLT20] N. Afkhami-Jeddi, H. Cohn, T. Hartman, D. de Laat, and A. Tajdini, High-dimensional sphere
           packing and the modular bootstrap, J. High Energy Phys. 12 (2020), article 066, doi:10.1007/
           JHEP12(2020)066.
[Ahl79]    L. V. Ahlfors, Complex Analysis, 3rd ed., McGraw–Hill, New York, 1979.
[BCK10]    J. Bourgain, L. Clozel, and J.-P. Kahane, Principe d’Heisenberg et fonctions positives, Ann. Inst.
           Fourier (Grenoble) 60 (2010), 1215–1232, doi:10.5802/aif.2552.
[Coh02]    H. Cohn, New upper bounds on sphere packings. II, Geom. Topol. 6 (2002), 329–353, doi:10.2140/
           gt.2002.6.329.
[CDG24]    H. Cohn, D. Dong, and F. Gonçalves, Sign uncertainty principles and low-degree polynomials, Proc.
           Amer. Math. Soc. Ser. B 11 (2024), 224–228, doi:10.1090/bproc/219.
[CE03]     H. Cohn and N. Elkies, New upper bounds on sphere packings. I, Ann. of Math. (2) 157 (2003),
           689–714, doi:10.4007/annals.2003.157.689.
[CG19]     H. Cohn and F. Gonçalves, An optimal uncertainty principle in twelve dimensions via modular
           forms, Invent. Math. 217 (2019), 799–831, doi:10.1007/s00222-019-00875-4.
[CKMRV17] H. Cohn, A. Kumar, S. D. Miller, D. Radchenko, and M. S. Viazovska, The sphere packing problem
           in dimension 24, Ann. of Math. (2) 185 (2017), 1017–1033, doi:10.4007/annals.2017.185.3.8.
[CKMRV22] H. Cohn, A. Kumar, S. D. Miller, D. Radchenko, and M. S. Viazovska, Universal optimality of
           the E8 and Leech lattices and interpolation formulas, Ann. of Math. (2) 196 (2022), 983–1082,
           doi:10.4007/annals.2022.196.3.3.


                                                               25
[CM16]     H. Cohn and S. D. Miller, Some properties of optimal functions for sphere packing in dimensions 8
           and 24, preprint, 2016, arXiv:1603.04759.
[CZ14]     H. Cohn and Y. Zhao, Sphere packing bounds via spherical codes, Duke Math. J. 163 (2014), 1965–
           2002, doi:10.1215/00127094-2738857.
[Edw25]    R. Edwin, Fourier inequalities and sign uncertainty, preprint, 2025, arXiv:2505.15994.
[GOSR21]   F. Gonçalves, D. Oliveira e Silva, and J. P. G. Ramos, On regularity and mass concentration
           phenomena for the sign uncertainty principle, J. Geom. Anal. 31 (2021), 6080–6101, doi:10.1007/
           s12220-020-00519-7.
[GOSS17]   F. Gonçalves, D. Oliveira e Silva, and S. Steinerberger, Hermite polynomials, linear ﬂows on the
           torus, and an uncertainty principle for roots, J. Math. Anal. Appl. 451 (2017), 678–711, doi:10.1016/
           j.jmaa.2017.02.030.
[Gor00]    D. V. Gorbachev, Extremal problem for entire functions of exponential spherical type, connected
           with the Levenshtein bound on the sphere packing density in Rn , Izv. Tula State Univ. Ser. Math.
           Mech. Inform. 6 (2000), 71–78; in Russian.
[HMR19]    T. Hartman, D. Mazáč, and L. Rastelli, Sphere packing and quantum gravity, J. High Energy Phys.
           12 (2019), article 048, doi:10.1007/JHEP12(2019)048.
[KL78]     G. A. Kabatianskii and V. I. Levenshtein, On bounds for packings on a sphere and in space, Prob-
           lems Inform. Transmission 14 (1978), 1–17.
[Lev79]    V. I. Levenshtein, On bounds for packings in n-dimensional Euclidean space, Soviet Math. Dokl.
           20 (1979), 417–421.
[DLMF]     F. W. J. Olver et al., eds., NIST Digital Library of Mathematical Functions, Release 1.2.7, National
           Institute of Standards and Technology, 2026, dlmf.nist.gov.
[PK01]     R. B. Paris and D. Kaminski, Asymptotics and Mellin–Barnes Integrals, Encyclopedia of Mathe-
           matics and its Applications, vol. 85, Cambridge University Press, Cambridge, 2001.
[RV19]     D. Radchenko and M. S. Viazovska, Fourier interpolation on the real line, Publ. Math. Inst. Hautes
           Études Sci. 129 (2019), 51–81, doi:10.1007/s10240-018-0101-z.
[SZ24]     N. T. Sardari and M. Zargar, New upper bounds for spherical codes and packings, Math. Ann. 389
           (2024), 3653–3703, doi:10.1007/s00208-023-02738-z.
[SW71]     E. M. Stein and G. Weiss, Introduction to Fourier Analysis on Euclidean Spaces, Princeton Math-
           ematical Series, vol. 32, Princeton University Press, Princeton, 1971.
[Via17]    M. S. Viazovska, The sphere packing problem in dimension 8, Ann. of Math. (2) 185 (2017), 991–
           1015, doi:10.4007/annals.2017.185.3.7.
[Z24]      M. Zargar, Stiefel manifolds and upper bounds for spherical codes and packings, preprint, 2024,
           arXiv:2407.10697.




                                                    26
