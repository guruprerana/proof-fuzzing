# The Sharp Inequality in Ehrhart’s Volume Conjecture

> Source: OpenAI, *Ten Advances in Mathematics and Theoretical Computer Science*, Chapter 8, PDF pages 223–232. Layout-preserving text extraction; consult the source PDF for authoritative equation rendering.

                                     Chapter 8

 The Sharp Inequality in Ehrhart’s Volume
               Conjecture
    Abstract. We prove the sharp bound that an n-dimensional convex body
    whose barycenter is its only interior lattice point has volume at most (n + 1)n /n!.



                                       Contents
1. Introduction
2. The real potential and lattice Bergman spaces
3. Vanishing orders and the lower slope
4. Bergman convexity and the upper slope
References




                                            219
                                         1. Introduction
  Ehrhart asked whether, among convex bodies whose barycenter is their only interior lattice
point, the centered simplex maximizes volume [Ehr64]. Let ∆n = conv{0, e1 , . . . , en } and write
vol for ordinary Euclidean volume. The precise inequality is the following.
Theorem 1.1. Let K ⊂ Rn be a full-dimensional compact convex body with barycenter 0. If
int(K) ∩ Zn = {0}, then
                                                 (n + 1)n
                                      vol(K) ≤             .                                  (1)
                                                     n!
   The bound is sharp: the simplex (n + 1)∆n − (1, . . . , 1) has barycenter 0, contains no other
interior lattice point, and has volume (n + 1)n /n!. The equality reﬁnement predicts that every
extremizer is a unimodular image of this simplex under an integer linear map of determinant
±1 [NP14, Conj. 1.1]. We do not determine whether these are the only equality cases.
Previous work. Ehrhart proved the conjecture for planar convex bodies and for simplices in
every dimension [Ehr55, Ehr79]. For arbitrary centered bodies, Milman–Pajor symmetrization
and Minkowski’s theorem give vol(K) ≤ 4n , as observed by Henk, Henze, and Hernández
Cifre [MP00, HHH16]. Using
                        √
                              thin-shell estimates, Huang, Slomka, Tkocz, and Vritsiou improved
this to vol(K) ≤ 4 en −c  n for a universal c > 0 [HSTV22, Prop. 6.2]. Campos, van Hintum,
Morris, and Tiba subsequently obtained vol(K) ≤ 4n exp(−cn/(log n)8 ) using bounds for the
isotropic constant [CHMT24]. Combining their argument with Klartag and Lehec’s solution of
Bourgain’s slicing problem gives vol(K) ≤ 4n e−cn for a universal c > 0 [CHMT24, KL25].
   The conjecture is also known for certain classes of convex bodies. Berman and Berndtsson
connect the sharp bound with the anticanonical volume of Kähler–Einstein toric varieties [BB17].
Their analytic argument combines Bergman convexity and a Moser–Trudinger inequality with
a Green function at a torus-ﬁxed point. In particular, it proves the conjecture for centered
rational polytopes with facet presentation
                
           P = y : hℓF , yi ≥ −aF for every facet F ,               ℓF ∈ Zn ,   0 < aF ≤ 1,
where each ℓF is primitive, meaning that its coordinates have no common factor [BB17, Cor. 1.4].
They also establish the sharp bound for bodies in the positive orthant with barycenter (1, . . . , 1)
and record Klartag’s direct derivation from Grünbaum’s barycentric half-space inequality [BB17,
Thm. 1.5 and Rem. 3.2]; see [Gru60]. The displayed facet conditions also give an aﬃne reduction
to the orthant case. Write
                              Q∗ = {u : hu, yi ≤ 1 for every y ∈ Q}
for the polar of a convex body Q containing 0. Nill and Paﬀenholz extend this argument to
convex bodies in the polar of a lattice polytope and classify the equality cases [NP14, Thm. 1.4].
Their hypothesis does not cover every centered rational polytope with unique interior lattice
point 0: they give the example
                         
              P0 = conv ±(3/2, 1/4), ±(3/2, 5/4) ,               P0∗ ∩ Z2 = {0, ±(1, −2)},
so P0∗ contains no full-dimensional lattice polygon.
Idea of the proof. By a theorem of Berman and Berndtsson [BB13, Thm. 1.1], there is a
smooth convex potential ϕ whose gradient transports e−ϕ(x) dx to Lebesgue measure on K;
Cordero-Erausquin and Klartag also studied this transport problem [CK15]. On X = (C∗ )n ,
regard ϕ as a function of the logarithmic radii:
                                                                        
                                 ϕ(z) = ϕ log |z1 |2 , . . . , log |zn |2 .
Let dν = dx dθ, where xi = log |zi |2 and dθ is normalized angular measure. The space Hk
of holomorphic functions on X that are square-integrable with weight e−kϕ dν has Laurent
monomial basis
             Hk = span{z m : m ∈ Zn ∩ int(kK)},               dim Hk = #(Zn ∩ int(kK)).
The unique-interior-lattice-point hypothesis is therefore exactly the assertion H1 = C.


                                                   220
    At higher levels, ﬁx p = (1, . . . , 1). Every monomial equals 1 at p, so choose an orthonormal
basis (sa ) adapted to vanishing order at p. Vanishing to order j forces all Taylor coeﬃcients
                                                                 
of degree less than j to vanish, imposing at most n+j−1       n    linear conditions. Write qa for the
order of sa , truncated at cK k, where cK = (n! vol(K))1/n , and form the ﬁnite-level potentials
              P
ukt = k −1 log a |sa |2 etqa . Their regularized limit is a ray of potentials, a one-parameter family
(ψt )t≥0 with ψ0 = ϕ and bounded ψt − ϕ for each t.
    Introduce the normalized partition function and its logarithm:
                                             Z
                                        1
                          Z(t) =                e−ψt dν,      L(t) = − log Z(t).
                                   vol(K) X
Since H1 = C, the weighted holomorphic space associated with ψt still consists only of con-
stants, so its Bergman kernel equals 1/(vol(K)Z(t)). Berndtsson’s positivity theorem makes L
convex [Ber06, Ber15], as in the one-dimensional Bergman mechanism of Berman and Berndts-
son [BB17, Thm. 2.3]. Counting the vanishing conditions gives the lower bound on its initial
slope. A separate local Schwarz estimate uses the decay of functions vanishing at p to bound
ψt from above on a ball of radius proportional to e−t/2 ; the volume of that ball gives the upper
bound. Together, these arguments yield
                                             n
                                                 cK ≤ L0+ (0) ≤ n.                                 (2)
                                           n+1
Their comparison gives cK ≤ n + 1, proving (1).
    Fujita previously used the same point ﬁltration and vanishing-order count to obtain a sharp
volume bound in Fano geometry [Fuj18, Thms. 2.3 and 5.1]. Related constructions include
ﬁltrations of Laurent polynomials in graded Ehrhart theory [RR24, Cav26], toric and ﬁltered
Bergman kernels [Zel09, PS14], and rays from ﬁltered linear series [BC11, RW14].

                   2. The real potential and lattice Bergman spaces
   We ﬁrst construct the transport potential, identify lattice points with an orthogonal basis
of holomorphic monomials, and establish the convergence needed to pass from those ﬁnite-
dimensional spaces to a limiting potential.
   Let hK (x) = supy∈K hy, xi be the support function of K. Since its barycenter is 0, the
existence theorem of Berman and Berndtsson [BB13, Thm. 1.1] gives a smooth strictly convex
potential ϕ : Rn → R whose gradient transports its associated log-concave measure to Lebesgue
measure on K:                       
                   (∇ϕ)# e−ϕ(x) dx = 1K (y) dy,        |ϕ(x) − hK (x)| ≤ C.                (3)
Moreover, ∇ϕ is a diﬀeomorphism onto int(K), so the transport identity is equivalent to
                               ∇ϕ(Rn ) = int(K),                     det D2 ϕ = e−ϕ .
In particular, the transported measure has exactly the volume of K:
                           Z                        Z
                                     −ϕ(x)
                                 e           dx =          det D2 ϕ(x) dx = vol(K).               (4)
                            Rn                        Rn
  To expose the lattice, attach independent angular coordinates to the original real variables.
Write dθ for the Haar probability measure on (S 1 )n , so that
                          X = (C∗ )n ,              zi = exi /2+iθi ,         dν = dx dθ.
Let dλ denote Euclidean Lebesgue measure on Cn . The change to logarithmic coordinates gives
                                                             Y
                                                             n
                                                        −n
                                        dν(z) = π                  |zi |−2 dλ(z).                 (5)
                                                             i=1
Here x ∈ Rn is unrestricted; in particular, the |zi | need not be bounded or bounded away from
0. Whenever ϕ is evaluated on X, it denotes the pullback
                                                                                    
                                      ϕ(z) = ϕ log |z1 |2 , . . . , log |zn |2 .




                                                           221
Since the angular variables have total mass one, (4) becomes
                           Z
                                                                           e−ϕ
                                e−ϕ dν = vol(K),                 dµ =            dν.                  (6)
                            X                                             vol(K)
  Write O(X) for the space of holomorphic functions on X. For any real weight b on X, its
weighted holomorphic space and Bergman kernel are
                                                          Z                        
                                                                   2 −b
                           H(b) = f ∈ O(X) :                    |f | e     dν < ∞ ,
                                                            X
                                                           |f (z)|2                                   (7)
                          Bb (z) =       sup       Z                       .
                                     f ∈H(b)\{0}           |f |2 e−b dν
                                                   X
For k ≥ 1, specialize to b = kϕ:
                                                                  Z
                            Hk = H(kϕ),            ksk2k =               |s|2 e−kϕ dν.
                                                                    X
The point of the complex torus is that its holomorphic Laurent monomials are indexed by Zn .
By (3), z m has ﬁnite weighted norm exactly when m/k ∈ int(K): only then does its integrand
decay exponentially in every direction. Since K is bounded, there are only ﬁnitely many such
exponents.
Lemma 2.1. The monomials z m , with m ∈ Zn ∩ int(kK), form an orthogonal basis of Hk . In
particular, Hk is ﬁnite-dimensional; writing dk = dim Hk , one has
                                               dk
                   dk = # Zn ∩ int(kK) ,           −→ vol(K),      H1 = C.            (8)
                                                kn
More generally, H(b) = C whenever b − ϕ is bounded on X.
Proof. For u = m/k, integration over θ ∈ (S 1 )n gives
                                                       Z
                               kz m k2k = Ik (u) :=             ek(hu,xi−ϕ(x)) dx.                    (9)
                                                        Rn
If u ∈ int(K), there is δ > 0 for which hK (x) − hu, xi ≥ δ|x|. Thus (3) implies Ik (u) < ∞. If
u∈ / int(K), take a supporting direction v 6= 0 with hu, vi ≥ hK (v). On a tube of ﬁxed radius
aboutP
       the ray R≥0 v, hu, xi − ϕ(x) is bounded below, so Ik (u) = ∞. For the Laurent expansion
s = m∈Zn cm z m , Parseval’s identity for the integral over θ and Tonelli’s theorem give
                                               X
                                     ksk2k =           |cm |2 Ik (m/k),
                                               m∈Zn
with zero terms omitted. Hence an integrable s has nonzero coeﬃcients only for m ∈ Zn ∩
int(kK). This set is ﬁnite because K is bounded, proving both the basis statement and ﬁnite-
dimensionality. The lattice-counting limit follows from the fact that ∂K has measure zero. At
k = 1, the only admissible exponent is 0. Finally, a bounded change of weight does not aﬀect
integrability, so H(b) = H(ϕ) = C whenever b − ϕ is bounded.                               □
  We next approximate the probability measure dµ = e−ϕ dν/ vol(K) using the lattice mono-
mials. By Lemma 2.1 and (9), an orthonormal basis of Hk is given explicitly by
                                    zm
                       sm (z) = p          ,   m ∈ Zn ∩ int(kK).
                                  Ik (m/k)
Deﬁne the Bergman kernel Bk and the associated probability measure µk by
                                          X                                    X         |z m |2
               Bk (z) = Bkϕ (z) =                      |sm (z)|2 =                               ,
                                     m∈Zn ∩int(kK)
                                                                                       I (m/k)
                                                                          m∈Zn ∩int(kK) k
                                                                                                     (10)
                         Bk e−kϕ
                 dµk =           dν.
                           dk
The kernel Bk is independent of the orthonormal basis, so we may later replace the monomials
by a basis adapted to vanishing at a point without changing Bk or µk . The next lemma supplies


                                                   222
the two convergence statements needed for the limiting construction. The logarithmic kernels
recover ϕ, so the limiting deformation starts at the original transport potential; convergence of
µk in total variation transfers averaged vanishing orders to the limiting measure µ. All limits
in the next lemma are as k → ∞, and ok (1) denotes an error tending to zero in that limit.
Whenever uniformity is asserted, it is on the speciﬁed compact set.
Lemma 2.2. There exists C > 0 such that, for every k ≥ 2 and every z ∈ X,
                                   1                       log k
                                     log Bk (z) ≤ ϕ(z) + C       .                        (11)
                                   k                         k
Moreover, as k → ∞,
                1
                  log Bk −→ ϕ locally uniformly on X,           kµk − µkTV −→ 0.
                k
Proof. Put A = maxy∈K |y|. Since ∇ϕ(Rn ) ⊂ K, the function ϕ is A-Lipschitz on all of Rn . For
x ∈ Rn , u ∈ K, and |v − x| < 1/k, it follows that
                                                                 2A
                               hu, vi − ϕ(v) ≥ hu, xi − ϕ(x) −       .
                                                                   k
Integrating (9) over this real ball gives
                                 Ik (u) ≥ ωn k −n ek(hu,xi−ϕ(x))−2A ,
where ωn is the volume of the unit ball in Rn . For z ∈ X with xi = log |zi |2 and u = m/k, we
have |z m |2 = ekhu,xi . Therefore (10) gives
                                                  e2A n
                              Bk (z) ≤                 k dk ekϕ(z) ≤ Ck 2n ekϕ(z) ,
                                                  ωn
where the last inequality follows from dk /k n → vol(K). Taking logarithms proves (11).
   To obtain both remaining conclusions from a single estimate, introduce the unnormalized
densities
                                                                     dk
           ρk = k −n Bk e−kϕ ,               ρ = e−ϕ ,     ρk dν = n dµk ,          ρ dν = vol(K) dµ.
                                                                     k
If x = (log |z1 |2 , . . . , log |zn |2 ), the monomial formula (10) gives
                                         1      X         ek(hm/k,xi−ϕ(x))
                             ρk (x) =                                      .
                                        k n m∈Zn ∩int(kK)     Ik (m/k)

  For ﬁxed x, the summands with m/k within O(k −1/2 ) of ∇ϕ(x) already suﬃce for both
convergence statements. We approximate those summands by a Gaussian.
  Write H = D2 ϕ and deﬁne the Legendre transform
                                                                   
                                   ϕ∗ (u) = sup hu, xi − ϕ(x) .
                                              x∈Rn

For u ∈ int(K), the exponent in (9) has its unique maximum at xu = (∇ϕ)−1 (u), with Hessian
−H(xu ). The multivariate Laplace estimate therefore gives
                                         ∗     (2π/k)n/2
                             Ik (u) = ekϕ (u) p            (1 + ok (1)).                        (12)
                                                det H(xu )
The error is uniform on every compact S ⊂ int(K). Indeed, with δS = dist(S, ∂K) > 0,
                               hK (x) − hu, xi ≥ δS |x|        (u ∈ S).
Together with (3), this controls the tails uniformly; the xu remain in a compact set where D2 ϕ
is uniformly positive deﬁnite.                                                         √
   Fix R > 0, put√y = ∇ϕ(x), and retain only the monomials with |m/k − y| ≤ R/ k. For
u = m/k and q = k(u − y), Taylor’s formula gives
                                                  1
                       k ϕ∗ (u) + ϕ(x) − hu, xi = hH(x)−1 q, qi + ok (1),
                                                   2



                                                   223
uniformly for |q| ≤ R and x in any ﬁxed compact subset of Rn . Substituting (12) into the
monomial sum for ρk now gives a Gaussian Riemann sum:
                        ρk (x) ≥ FR (x) + ok (1),
                                            p              Z
                                             det H(x)                         −1 q,qi/2                              (13)
                             FR (x) =                               e−hH(x)               dq,
                                             (2π)n/2        |q|≤R
again locally uniformly in x.
  This one estimate gives both desired limits. On any compact Q ⊂ Rn , FR has a strictly
positive minimum. Together with the global upper bound already proved, this gives constants
bQ , C > 0 such that
                       bQ ≤ ρk (x) ≤ Ck n                 (x ∈ Q, k suﬃciently large).
Consequently,
                        1                      n log k + log ρk (x)
                          log Bk (z) − ϕ(z) =                       −−−→ 0
                        k                               k           k→∞
uniformly for x ∈ Q, proving local uniform convergence.                          p
   For the measures, let R → ∞ in (13). The full Gaussian integral equals (2π)n/2 det H(x),
so det H = e−ϕ gives
                                lim inf ρk (x) ≥ det H(x) = ρ(x).
                                       k→∞
On the other hand, (8) and (6) give the exact mass limit
                            Z                              Z
                                         dk
                               ρk dν = n −−−→ vol(K) =        ρ dν.                      (14)
                             X           k k→∞              X
Since 0 ≤ min(ρk , ρ) ≤ ρ and min(ρk , ρ) → ρ pointwise, dominated convergence and (14) give
                                       Z              Z                Z
                kρk − ρkL1 (dν) =           ρk dν +        ρ dν − 2         min(ρk , ρ) dν −−−→ 0.
                                       X              X              k→∞X
Since dk /k → vol(K) as k → ∞, normalizing these densities proves kµk − µkTV → 0.
           n                                                                                                           □

                         3. Vanishing orders and the lower slope
  We ﬁrst count the vanishing orders forced by the dimensions of Hk . We then realize that
count as the initial slope of a limiting family of potentials.
  Fix p = (1, . . . , 1) ∈ X. For a nonzero holomorphic function s, expand around p as
                     X                                         
       s(p + ζ) =           cα ζ α ,        ordp (s) = min |α| : cα 6= 0 ,                 |α| = α1 + · · · + αn .
                    α∈Zn
                       ≥0

Thus ordp (s) ≥ j means that all Taylor coeﬃcients of total degree less than j vanish; set
ordp (0) = ∞. Filter Hk by these conditions:
                  Fkj = {s ∈ Hk : ordp (s) ≥ j},                   Hk = Fk0 ⊇ Fk1 ⊇ Fk2 ⊇ · · · .
The number of Taylor coeﬃcients of degree less than j controls the codimension of Fkj .
Lemma 3.1. For every j, k ≥ 1,
                                                                             !
                                                                   n+j−1
                                           dk − dim Fkj ≤                .                                           (15)
                                                                     n
Proof. Taking the Taylor polynomial of total
                                         
                                             degree less than j deﬁnes a linear map on Hk with
kernel Fkj and target of dimension n+j−1
                                     n     .                                                □
    Since Hk is ﬁnite-dimensional and a holomorphic function vanishing to every order is zero,
Fk = 0 for all suﬃciently large j. For each j, choose an orthonormal basis of Fkj ∩(Fkj+1 )⊥ , where
  j

orthogonality is taken in Hk . Combining these bases gives an orthonormal basis s1 , . . . , sdk of
Hk . Writing ja = ordp (sa ), it satisﬁes
                      Fkj = span{sa : ja ≥ j},                   dim Fkj = #{a : ja ≥ j}.                            (16)



                                                           224
Replacing the monomial basis by this adapted basis does not change Bk or µk .
  For ﬁxed s > 0 and j = bskc, the lattice count (8) and the vanishing estimate (15) give
                                              bskc
                               dim Fk                sn
                                         ≥  vol(K) −    + ok (1).
                                    kn               n!
The leading-order lower bound is positive exactly when s < cK = (n! vol(K))1/n , so we truncate
the vanishing orders at this scale:
                                    Nk = bcK kc,            qa = min{ja , Nk }.
For a real parameter t, multiply the squared contribution of a basis element with truncated
order qa by etqa . The resulting potential and its initial slope are
                                                                                   P
                                        X
                                        dk
                                                                                       a qa |sa (z)|
                                 1                                                                  2
                        ukt (z) = log         |sa (z)| e2 tqa
                                                                ,       gk (z) =                        .
                                k       a=1
                                                                                        kBk (z)

Thus uk0 = k −1 log Bk and gk = ∂t ukt              ; at each z, gk (z) is the average of qa /k with probabilities
                                              t=0
|sa (z)|2 /Bk (z). In particular,
                                    0 ≤ gk ≤ cK ,               |ukt − uk0 | ≤ cK |t|.                           (17)
  The average of gk under µk records exactly the truncated vanishing orders. Since the adapted
basis is orthonormal, (16) gives
                    Z                                                                          n+N 
                                 1 X          1 X              Nk dk − n+1k
                                     k    d        k            N
                       gk dµk =         qa =         dim Fkj ≥              .
                     X          kdk a=1      kdk j=1                 kdk
                                                P                                 
The inequality follows from (15) and N     k
                                         j=1
                                               n+j−1
                                                 n     = n+N  k
                                                           n+1 . By (8), its large-k limit is the
same sharp integral as in Fujita’s point-ﬁltration argument [Fuj18, proof of Thm. 5.1]:
                        Z                    Z cK              
                                       1                     sn         n
                lim inf   gk dµk ≥                  vol(K) −      ds =       cK .            (18)
                 k→∞ X              vol(K) 0                 n!        n+1
   The bound (18) involves a diﬀerent potential ukt and initial slope gk at each level k. We now
construct a single, k-independent family of potentials ψt with ψ0 = ϕ, then transfer this bound
to its initial slope g = ψ̇0+ . The construction uses the complex analogue of convexity.
   Recall that a function a : D → [−∞, ∞) on a domain D ⊂ CN is plurisubharmonic if it
is upper semicontinuous and its restriction to every complex aﬃne line satisﬁes the submean
inequality                                        Z
                                               1 2π               
                                    a(w) ≤           a w + reiθ v dθ
                                              2π 0
for every w ∈ D, v ∈ CN , and r > 0 for which the closed complex disk {w + ζv : |ζ| ≤ r} lies in
D. When a is twice diﬀerentiable, this is equivalent to positive semideﬁniteness of its complex
                          N
Hessian ∂ 2 a/∂wi ∂wj i,j=1 .
   For t = log |τ |2 , put
                                                     1    Xdk
                               Uk (z, τ ) = ukt (z) = log     |sa (z)τ qa |2 .
                                                     k    a=1
This function is plurisubharmonic on X × C∗ : it is k −1 times the logarithm of the squared
norm of a holomorphic vector. By Lemma 2.2 and (17), the functions Uk are locally uniformly
bounded above. Their regularized tail envelopes therefore deﬁne a plurisubharmonic limit:
                                                !
            Ψm = usc(z,τ )     sup Uk (z, τ ) ,            Ψ = lim Ψm ,                  ψt (z) = Ψ(z, et/2 ).   (19)
                              k≥m                                   m→∞

Here usc f (z, τ ) = lim sup(z 0 ,τ 0 )→(z,τ ) f (z 0 , τ 0 ) denotes upper-semicontinuous regularization in
both variables. For a compact neighborhood Q of z, set ϵm (Q) = supk≥m supQ |uk0 − ϕ| → 0. By
(17), for z 0 ∈ Q and k ≥ m, |Uk (z 0 , τ ) − ϕ(z 0 )| ≤ ϵm (Q) + cK | log |τ |2 |. Taking the regularized



                                                           225
supremum at (z, 1) gives |Ψm (z, 1) − ϕ(z)| ≤ ϵm (Q) and therefore ψ0 = ϕ. For t ≥ 0, taking the
same regularized limit in uk0 ≤ ukt ≤ uk0 + cK t gives
                                 ψ0 = ϕ,       ϕ ≤ ψt ≤ ϕ + cK t            (t ≥ 0).                                     (20)
Since a radial plurisubharmonic function is convex in its logarithmic radius, t 7→ ψt (z) is convex.
Deﬁne its initial right-hand velocity by
                                                         ψt (z) − ϕ(z)
                                g(z) := ψ̇0+ (z) := lim                .                        (21)
                                                     t↓0        t
In particular, 0 ≤ g ≤ cK .
   The envelope construction immediately gives lim supk→∞ ukt ≤ ψt . Convexity now relates the
ﬁnite-level velocities gk to the limiting velocity g: for every ﬁxed t > 0,
                                           ukt (z) − uk0 (z)
                                           gk (z) ≤          .
                                                   t
Since uk0 → ϕ locally uniformly, taking upper limits in this inequality and then letting t ↓ 0
gives lim supk→∞ gk ≤ g. Moreover, 0 ≤ gk ≤ cK . Total-variation convergence of µk to µ and
reverse Fatou therefore give
                                                                Z               Z
                            lim sup gk ≤ g,       lim sup            gk dµk ≤         g dµ.                              (22)
                              k→∞                     k→∞       X                X

Proposition 3.2. For cK = (n! vol(K))1/n , the initial velocity (21) satisﬁes
                                  Z
                                                 n
                                     g dµ ≥          cK .
                                   X          n+1
Proof. Combine the ﬁnite-level estimate (18) with the limiting comparison (22).                                            □

                          4. Bergman convexity and the upper slope
   It remains to turn the limiting potential into a convex logarithmic partition function and
control its growth near the point p. A function is pluriharmonic if both it and its negative are
plurisubharmonic; adding such a function preserves plurisubharmonicity. In particular, log |zi |2
is pluriharmonic where zi 6= 0.
   On D = (C∗ )n × {τ ∈ C : |τ | > 1}, Berndtsson’s positivity theorem says that the logarithm
of the Bergman kernel associated with any plurisubharmonic weight and Euclidean measure is
itself plurisubharmonic [Ber06, Thm. 1.1]. The same conclusion holds for the kernels (7) deﬁned
using dν: if b is plurisubharmonic on D, then
                                (z, τ ) 7−→ log Bbτ (z),            bτ (z) = b(z, τ ),                                   (23)
                                                                                                        Pn
is plurisubharmonic. Indeed, by (5), the Euclidean weight a(z, τ ) = b(z, τ ) + i=1 log |zi |2 +
n log π satisﬁes e−a dλ = e−b dν. The added logarithms are pluriharmonic, so a is plurisubhar-
monic whenever b is. More generally, Berndtsson’s theorem holds on any pseudoconvex domain.
   We now turn the ray into the one-dimensional convex function required by (2). Set
                                 Z
                             1
                   Z(t) =           e−ψt dν,    L(t) = − log Z(t),    t ≥ 0.
                          vol(K) X
In particular, Z(0) = 1 and L(0) = 0. In general, if 1 = f0 , f1 , . . . , fr is a basis of a weighted
holomorphic space, its Gram matrix and Bergman kernel are
                Z
    Gij (t) =       fi fj e−ψt dν,    Bψt (z) = v(z)∗ G(t)−1 v(z),                  v(z) = (f0 (z), . . . , fr (z))T .
                X
The unnormalized partition function is G00 (t), so positivity of log Bψt does not generally imply
convexity of − log G00 (t). The unique-interior-lattice-point hypothesis is what reduces G(t) to
a 1 × 1 matrix and identiﬁes these two quantities.
Lemma 4.1. The function L is ﬁnite and convex, and
                                                           Z
                                              L0+ (0) =         g dµ.                                                    (24)
                                                            X



                                                      226
Proof. By (20), ψt − ϕ is bounded for each t ≥ 0, so Lemma 2.1 gives H(ψt ) = C. Taking
the supremum over constant functions in (7) therefore identiﬁes the Bergman kernel with the
partition function:
                                          Z           −1
                                                −ψt           eL(t)
                                Bψt (z) =     e     dν     =        .
                                            X                vol(K)
Apply (23) to the plurisubharmonic weight b(z, τ ) = Ψ(z, τ ). It follows that log Bψt (z) =
L(log |τ |2 ) − log vol(K) is plurisubharmonic. A radial subharmonic function is convex in its
logarithmic radius, so L is convex on (0, ∞); (20) extends the convexity continuously to 0.
   Finally, (20) and the deﬁnition of g give (1 − e−(ψt −ϕ) )/t → g pointwise as t ↓ 0, with the
quotient bounded between 0 and cK . Dominated convergence and (6) therefore give
                                         Z                                Z
                        1 − Z(t)        1 − e−(ψt −ϕ)
                                 =                    dµ −→                    g dµ.
                            t        X        t                            X
Since Z(t) → 1 and L = − log Z, this proves (24).                                                      □
   To bound the other side of the initial slope, it suﬃces to look near the point p where the
ﬁltration was deﬁned. High vanishing order cancels the exponential ﬁltration weight on a ball
whose radius decreases like e−t/2 .
Lemma 4.2.
                                        L(t) ≤ nt              (t ≥ 0).                              (25)
Proof. Choose a branch of the coordinates ζi = log zi near p, so that p corresponds to ζ = 0
and dν = π −n dλ(ζ). Let B2r be the Euclidean ball of radius 2r in these coordinates and put
Mr = supB2r ϕ. For s ∈ Hk with kskk = 1, the submean inequality on B2r bounds s on Br
by Cr ekMr /2 . If s vanishes to order j at p, applying the one-variable Schwarz estimate on each
complex line through 0 improves this to
                                                              j
                                                         |ζ|
                               |s(ζ)| ≤ Cr ekMr /2                    (|ζ| < r).
                                                          r
If |ζ| < re−t/2 , then qa ≤ ja gives (|ζ|/r)2ja etqa ≤ 1. Thus ukt (ζ) ≤ Mr + k −1 log(Cr2 dk ) on the
open joint region |ζ| |τ | < r, |τ | > 1. The bound therefore survives the upper-semicontinuous
regularization in (19). Since dk = O(k n ), taking the regularized tail limit gives ψt ≤ Mr on
Bre−t/2 , whose dν-volume is π −n λ(Br )e−nt = cr e−nt , where cr > 0. Consequently, for some
constant D independent of t,
                                       cr
                            Z(t) ≥          e−Mr −nt ,     L(t) ≤ nt + D.
                                     vol(K)
For 0 < t < T , convexity and L(0) = 0 give L(t)/t ≤ L(T )/T ≤ n + D/T . Letting T → ∞
proves (25).                                                                         □
  Together, Proposition 3.2 and Lemmas 4.1 and 4.2 give (2), proving Theorem 1.1.

                                             References
[BB13]  R. J. Berman and B. Berndtsson, Real Monge–Ampère equations and Kähler–Ricci solitons on toric
        log Fano varieties, Ann. Fac. Sci. Toulouse Math. (6) 22 (2013), 649–711.
[BB17]  R. J. Berman and B. Berndtsson, The volume of Kähler–Einstein Fano varieties and convex bodies, J.
        Reine Angew. Math. 723 (2017), 127–152.
[Ber06] B. Berndtsson, Subharmonicity properties of the Bergman kernel and some other functions associated
        to pseudoconvex domains, Ann. Inst. Fourier (Grenoble) 56 (2006), 1633–1662.
[Ber15] B. Berndtsson, A Brunn–Minkowski type inequality for Fano manifolds and some uniqueness theorems
        in Kähler geometry, Invent. Math. 200 (2015), 149–200.
[BC11]  S. Boucksom and H. Chen, Okounkov bodies of ﬁltered linear series, Compos. Math. 147 (2011),
        1205–1229.
[CHMT24] M. Campos, P. van Hintum, R. Morris, and M. Tiba, Towards Hadwiger’s conjecture via Bourgain
        slicing, Int. Math. Res. Not. IMRN 2024 (2024), no. 10, 8282–8295, doi:10.1093/imrn/rnad198.
[Cav26] I. Cavey, Graded Ehrhart theory and toric geometry, Proc. Amer. Math. Soc. 154 (2026), 1859–1866.
[CK15]  D. Cordero-Erausquin and B. Klartag, Moment measures, J. Funct. Anal. 268 (2015), 3834–3866.




                                                     227
[Ehr55]  E. Ehrhart, Une généralisation du théorème de Minkowski, C. R. Acad. Sci. Paris 240 (1955), 483–485.
[Ehr64]  E. Ehrhart, Une généralisation probable du théorème fondamental de Minkowski, C. R. Acad. Sci. Paris
         258 (1964), 4885–4887.
[Ehr79]  E. Ehrhart, Volume réticulaire critique d’un simplexe, J. Reine Angew. Math. 305 (1979), 218–220.
[Fuj18]  K. Fujita, Optimal bounds for the volumes of Kähler–Einstein Fano manifolds, Amer. J. Math. 140
         (2018), 391–414.
[Gru60]  B. Grünbaum, Partitions of mass-distributions and of convex bodies by hyperplanes, Paciﬁc J. Math.
         10 (1960), 1257–1261.
[HHH16] M. Henk, M. Henze, and M. A. Hernández Cifre, Variations of Minkowski’s theorem on successive
         minima, Forum Math. 28 (2016), 311–325, doi:10.1515/forum-2014-0093.
[HSTV22] H. Huang, B. A. Slomka, T. Tkocz, and B.-H. Vritsiou, Improved bounds for Hadwiger’s covering
         problem via thin-shell estimates, J. Eur. Math. Soc. 24 (2022), 1431–1448.
[KL25]   B. Klartag and J. Lehec, Aﬃrmative resolution of Bourgain’s slicing problem using Guan’s bound,
         Geom. Funct. Anal. 35 (2025), 1147–1168, doi:10.1007/s00039-025-00718-w.
[MP00]   V. D. Milman and A. Pajor, Entropy and asymptotic geometry of non-symmetric convex bodies, Adv.
         Math. 152 (2000), 314–335.
[NP14]   B. Nill and A. Paﬀenholz, On the equality case in Ehrhart’s volume conjecture, Adv. Geom. 14 (2014),
         579–586.
[PS14]   F. T. Pokorny and M. Singer, Toric partial density functions and stability of toric varieties, Math.
         Ann. 358 (2014), 879–923.
[RR24]   V. Reiner and B. Rhoades, Harmonics and graded Ehrhart theory, J. Combin. Algebra, to appear,
         2024; arXiv:2407.06511.
[RW14]   J. Ross and D. Witt Nyström, Analytic test conﬁgurations and geodesic rays, J. Symplectic Geom. 12
         (2014), 125–169.
[Zel09]  S. Zelditch, Bernstein polynomials, Bergman kernels and toric Kähler varieties, J. Symplectic Geom.
         7 (2009), 51–76.




                                                    228
