# A Counterexample to Connes’s Rigidity Conjecture

> Source: OpenAI, *Ten Advances in Mathematics and Theoretical Computer Science*, Chapter 4, PDF pages 100–117. Layout-preserving text extraction; consult the source PDF for authoritative equation rendering.

                                   Chapter 4

   A Counterexample to Connes’s Rigidity
               Conjecture
    Abstract. Connes conjectured that the group von Neumann algebra of an ICC
    group with Kazhdan’s property (T ) determines the group up to isomorphism. We
    disprove the conjecture by constructing a countably inﬁnite family of pairwise
    nonisomorphic, mutually commensurable, ﬁnitely generated ICC property-(T )
    groups with isomorphic group von Neumann algebras. The construction exploits
                       b m ) depends on the underlying probability space, not on
    the fact that L∞ (A,   Ab
    the group law: binary carry produces diﬀerent compact abelian group structures
    with the same Haar measure and group action. Our examples also answer Popa’s
    ﬁnite-to-one question in the negative and attain his countability bound.



                                      Contents
1. Introduction
2. Group factors, property (T ), and Fourier duality
3. A torsion-free property-(T ) acting group
4. The binary-carry construction
5. ICC, property (T ), and the basic counterexample
6. An inﬁnite ﬁber of the group-factor functor
References




                                          96
                                        1. Introduction
   For a countable discrete group G, write L(G) for its group von Neumann algebra. A group
is ICC if it is inﬁnite and every nonidentity conjugacy class is inﬁnite; in this case, L(G) is a
II1 factor. Connes’s rigidity conjecture asks whether the group factor of an ICC property-(T )
group determines the group. It grew out of his foundational rigidity theorem [Con80]; he stated
it explicitly in his Kingston proceedings article [Con82, p. 45] and later restated it as Problem 1
in his 1994 monograph [Con94, Chapter 5, Appendix B, Problem 1, p. 551], where the group
factor is denoted by R(G).
                                                                                         ∼
Conjecture 1.1 (Connes). Let G and H be countable ICC groups with property (T ). If L(G) =
             ∼
L(H), then G = H.

Theorem 1.2. There exist ﬁnitely generated ICC groups with property (T ),

                                       Λ, Γ0 , Γ1 , Γ2 , . . . ,

that are pairwise nonisomorphic and satisfy
                                          ∼ L(Λ)
                                   L(Γn ) =               (n ≥ 0).

Moreover, for every n ≥ 0, the group Γn contains a subgroup isomorphic to Γ0 of index 24n . In
particular, the groups (Γn )n≥0 are mutually commensurable.

Consequences and context. As recorded in Corollary 5.10, the pair Λ, Γ0 already disproves
Connes’s conjecture. To establish this two-group result, it suﬃces to verify the ICC property and
property (T ) for Λ: both then transfer to Γ0 through the common group factor. The full family
in Theorem 1.2 additionally requires an intrinsic invariant to distinguish the groups Γn , and gives
a stronger negative result: even the ﬁnite-to-one weakening fails. In his Madrid ICM address,
Popa proved that the group-factor functor on ICC property-(T ) groups is at most countable-to-
one [Pop07, Section 4, pp. 457–458]; an alternative proof appears in [IPV13, Proposition 3.5].
He subsequently asked whether its ﬁbers must in fact be ﬁnite [Pop13, p. 9]. Since L(Λ) has
countably inﬁnitely many pairwise nonisomorphic ICC property-(T ) group realizations, the
answer is negative and Popa’s countability bound is sharp.
   The amenable case gives the opposite extreme: by Connes’s celebrated classiﬁcation theo-
rem for injective factors [Con76], every amenable ICC group has the same group factor, the
hyperﬁnite II1 factor. Property (T ) [Kaz67] was expected to prevent this collapse.
   The conjecture also belongs to the broader theory of W ∗ -superrigidity. A countable group
G is W ∗ -superrigid if L(G) = ∼ L(H) implies G =     ∼ H for every countable group H. Fur-
man’s orbit-equivalence rigidity theorem provided an earlier analogue for probability-measure-
preserving actions of higher-rank lattices [Fur99]. Popa introduced and developed deforma-
tion/rigidity theory, beginning with foundational work on Bernoulli shifts and rigid Cartan
inclusions [Pop06a, Pop06b]. For suitable malleable actions of rigid groups, his strong-rigidity
theorems [Pop06c, Pop06d] recover the acting group and its probability-space action from the
crossed product: a group-measure-space analogue of Connes’s conjecture. Ioana subsequently
proved W ∗ -superrigidity for Bernoulli actions of ICC property-(T ) groups [Ioa11]; this deter-
mines the action from its crossed product and does not assert rigidity of the bare group factor.
For accounts of the theory, see Popa’s ICM address [Pop07] and the later surveys [Vae10, Ioa18].
The ﬁrst W ∗ -superrigid groups were constructed in [IPV13]; the ﬁrst examples with property
(T ) followed in [CIOS23]. Thus some ICC property-(T ) groups are indeed determined by their
group factors; what Theorem 1.2 disproves is that property (T ) alone guarantees this conclusion,
even up to ﬁnite ambiguity.
   Inﬁnite ﬁbers were already known outside the property-(T ) setting. Indeed, as shown in
[IPV13, Theorem 1.2], for every nontrivial ﬁnite abelian group H0 and every n ≥ 3, there are
inﬁnitely many pairwise nonisomorphic groups H satisfying
                                                                   
                                         ∼ L H0 o PSLn (Z) .
                                    L(H) =


                                                  97
The ordinary wreath product on the right does not have property (T ). The new feature of
Theorem 1.2 is an inﬁnite ﬁber entirely within the ICC property-(T ) class, precisely the class
to which the countability bound applies.

Proof outline. For a countable abelian K-module A, Fourier transform gives
                                           ∼ L∞ (A,
                                  L(A o K) =     b m ) o K.
                                                    b
                                                    A
The crossed product remembers the Haar probability space and its K-action, but need not
remember the compact group law on A.   b Our strategy is therefore to put diﬀerent K-invariant
compact abelian group structures on a single probability space, and then to recover their diﬀer-
ences from the dual discrete groups.
  Section 3 constructs a torsion-free ICC property-(T ) group
                                                                                
                                                   g(t)7→g(0) mod 3
                         K = ker SL4 (Z[t]) −−−−−−−−−−−→ SL4 (F3 )

surjecting onto SL4 (F2 [t]). For V = F2 [t]4 , the divided-square module
                           B = spanF2 {v ⊗ v : v ∈ V },           D = V ⊕ B,
supplies the common compact K-space D    b = X × Y , where X = V ∗ and Y = B ∗ .
  The elementary model for the construction is the four-point probability space F22 . Coordi-
natewise addition gives the Klein four-group, whereas
                              (x, y)  (x0 , y 0 ) = (x + x0 , y + y 0 + xx0 )
gives Z/4Z; both have the same uniform Haar measure. Section 4 globalizes this binary carry
to a compact group C0 with the same measured K-action as X × Y . Writing
                                  Λ = D o K,                  c0 o K,
                                                         Γ0 = C
                                   ∼ L(Λ), while order-four torsion distinguishes the two groups.
Fourier transform identiﬁes L(Γ0 ) =
  Section 5 proves that Λ is ICC and has property (T ). The ICC assertion follows from an
inﬁnite-orbit calculation. For property (T ), transitivity on primitive vectors and a quadratic
Boolean support bound give a uniform spectral estimate for the semidirect product. Both
properties then transfer to Γ0 through the common group factor.
  Finally, Section 6 shifts the carry by n coeﬃcient positions in each of the four directions,
producing compact groups Cn with the same measured K-action. Their duals give
                                     cn o K,
                                Γn = C                          ∼ L(Λ).
                                                         L(Γn ) =
Pontryagin duality embeds Γ0 in Γn with index 24n . The ﬁnite-orbit part of the intrinsic
quotient En [2]/2En , where En = Ccn , also has order 24n , recovering n from the abstract group
and proving that the resulting family is pairwise nonisomorphic.

                 2. Group factors, property (T ), and Fourier duality
2.1. Group von Neumann algebras. Let G be a countable discrete group, and write U(H)
for the unitary group of a Hilbert space H. The left regular representation of G is
                            λG : G −→ U(ℓ2 (G)),             λG (g)δh = δgh .
The group von Neumann algebra of G and its canonical trace are
                             L(G) = λG (G)00 ,           τG (x) = hxδ1 , δ1 i.
                       P
For a ﬁnite sum x = g ag λG (g), one has τG (x) = a1 . A von Neumann algebra is a factor
if its center is C1; an inﬁnite-dimensional factor admitting a faithful normal tracial state is a
II1 factor. The group G is ICC if every nonidentity element has an inﬁnite conjugacy class.
For inﬁnite G, the group-factor criterion asserts that L(G) is a II1 factor if and only if G is
ICC [MN43].


                                                    98
2.2. Property (T ). Let G be a countable discrete group and let π : G → U(H) be a unitary
representation. It has almost invariant unit vectors if, for every ﬁnite F ⊆ G and ε > 0, there
is a unit vector ξ ∈ H such that
                                     max kπ(g)ξ − ξk < ε.
                                      g∈F

The group G has property (T ) if every unitary representation with almost invariant unit vectors
has a nonzero invariant vector. Property (T ) passes to quotients and is preserved under passage
to ﬁnite-index subgroups and ﬁnite-index extensions. Every countable discrete property-(T )
group is ﬁnitely generated; see [BHV08].
   For a subgroup A ≤ G, the pair (G, A) has relative property (T ) if every unitary representation
of G with almost invariant unit vectors has a nonzero A-invariant vector. If A ◁ G, relative
property (T ) for (G, A), together with property (T ) for G/A, implies property (T ) for G.
                                                                   ∼ L(H). If H is ICC
Lemma 2.1. Let G and H be countable discrete groups such that L(G) =
and has property (T ), then G is ICC and has property (T ).
Proof. Since H is ICC, L(H), and therefore L(G), is a II1 factor. The group-factor criterion
shows that G is ICC. By the Connes–Jones characterization [CJ85], an ICC group has property
(T ) if and only if its group factor does. Applying this equivalence ﬁrst to H and then to G
proves the assertion.                                                                      □

2.3. Pontryagin duality and crossed products. The algebra L∞ (A,      b m ) depends only on
                                                                           b
                                                                           A
the Haar probability space of A,b not on its compact group law. Once the measure and the
K-action are ﬁxed, so is the crossed product.
   Put T = {z ∈ C : |z| = 1}. For a locally compact abelian group A, write
                                       Ab = Homcont (A, T)
for its Pontryagin dual, equipped with the compact-open topology. When A is countable and
discrete, Ab is compact; denote its normalized Haar measure by mAb and its trivial character by 1.
If a countable discrete group K acts on A by automorphisms, the induced actions on characters
and functions are
                        (k · χ)(a) = χ(k −1 · a),  αk (f )(χ) = f (k −1 · χ).
The semidirect product A o K has multiplication (a, k)(b, h) = (a + k · b, kh). The corresponding
crossed product L∞ (A,b m )oK is generated, in its standard representation, by L∞ (A,  b m ) and
                           b
                           A                                                               b
                                                                                           A
unitaries (vk )k∈K satisfying
                              vk f vk∗ = αk (f ),   vk vl = vkl .
Under
                                             ∼ ℓ2 (A) ⊗ ℓ2 (K),
                                  ℓ2 (A o K) =
Fourier transform in the A-coordinate identiﬁes the group unitaries of A with multiplication by
χ 7→ χ(a), and those of K with the unitaries implementing the dual action. Hence
                                          ∼ L∞ (A,
                                 L(A o K) =     b m ) o K.                                   (2.1)
                                                   b
                                                   A

In particular, let A0 be another countable discrete abelian K-module. A measurable bijection
                          c0 is measure-preserving and K-equivariant when
modulo null sets θ : Ab → A
          θ∗ mAb = mAb0 ,    θ(k · χ) = k · θ(χ)    for every k ∈ K and almost every χ.

Then f 7→ f ◦ θ−1 , together with the identity on the implementing unitaries, gives
                                             ∼ L(A0 o K).
                                    L(A o K) =
                                                  c0 is required; this is the mechanism under-
No compatibility between the group laws on Ab and A
lying our construction.


                                                   99
                      3. A torsion-free property-(T ) acting group
  We need a torsion-free ICC property-(T ) group that surjects onto SL4 (F2 [t]). A congruence
condition at the diﬀerent prime 3 will provide torsion-freeness without losing the characteristic-2
action. Deﬁne                                                        
                                              g(t)7→g(0) mod 3
                        K = ker SL4 (Z[t]) −−−−−−−−−−−→ SL4 (F3 ) .
Set
                                R = F2 [t],          Q = SL4 (R).
The groups K and Q are countable.
  For a commutative ring S, let
                         ELn (S) = I + f Eij : f ∈ S, i 6= j ≤ SLn (S),
where Eij is the (i, j)-matrix unit. Thus ELn (S) is the elementary linear group. Since Z is
a regular ring of Krull dimension 1 and SK1 (Z) = 0, the elementary generation theorem for
polynomial rings [Sus77, Corollary 6.6] gives
                                ELn (Z[t]) = SLn (Z[t])        (n ≥ 3).
Property (T ) for elementary linear groups over ﬁnitely generated unital rings [EJ10, Theo-
rem 1.1] therefore gives property (T ) for SL4 (Z[t]).
Proposition 3.1. The group K has property (T ).
Proof. Evaluation at t = 0 followed by reduction modulo 3 has ﬁnite image. Thus K has ﬁnite
index in SL4 (Z[t]) and inherits property (T ).                                          □
  We use the following level-3 congruence lemma [Min87].
Lemma 3.2. For every d ≥ 2, the group
                                                                 
                                     ker SLd (Z) −→ SLd (F3 )
is torsion-free.
Proof. If the displayed group contains a nonidentity torsion element, it contains one of prime
order p. Write this element as
                                        A = I + 3r B,
where r ≥ 1 is maximal, so B 6≡ 0 (mod 3). If p 6= 3, then
                                 I = Ap ≡ I + p3r B       (mod 3r+1 ),
contradicting B 6≡ 0 (mod 3). If p = 3, then
                                A3 − I
                               0=      = B + 3r B 2 + 32r−1 B 3 .
                                 3r+1
Reduction modulo 3 again gives B ≡ 0 (mod 3), a contradiction.                                   □
Lemma 3.3. The group K is torsion-free and ICC. Reduction modulo 2 gives a surjection
                                           π2 : K ↠ Q.
Proof. For torsion-freeness, suppose g(t) ∈ K satisﬁes g(t)m = I for some m ≥ 1. Its constant
term g(0) is a torsion element of ker(SL4 (Z) → SL4 (F3 )), so Lemma 3.2 gives g(0) = I. If g 6= I,
let r ≥ 1 be its ﬁrst nonzero t-adic degree:
                                 g(t) = I + tr A(t),       A(0) 6= 0.
Since Z is an integral domain,
                              g(t)m ≡ I + mtr A(0) 6≡ I      (mod tr+1 ),
contradicting g m = I.
  For the ICC property, let
                         uij (f ) = I + 3f Eij ∈ K         (i 6= j, f ∈ Z[t]).


                                                100
A matrix commuting with every Eij is scalar, and every scalar element of SL4 (Z[t]) has ﬁnite
order. Thus, for a nonidentity g ∈ K, torsion-freeness provides i 6= j such that
                                        [Eij , g] = Eij g − gEij
is nonzero. If uij (f ) and uij (h) produce the same conjugate of g, then g commutes with uij (f −h),
and hence
                                          3(f − h)[Eij , g] = 0.
As Z[t] is an integral domain and [Eij , g] 6= 0, we must have f = h. Varying f therefore produces
inﬁnitely many conjugates.
   Finally, reduction modulo 2 gives
                                          uij (f ) 7−→ I + f¯Eij .
Every elementary matrix over R arises in this way. Since R is Euclidean, these matrices generate
Q = SL4 (R), proving that π2 is onto.                                                         □
Remark 3.4. Although the module and orbit calculations factor through Q, this group cannot
replace K:
                  u = I + E12 + E23 ∈ Q,      u2 = I + E13 6= I,        u4 = I,
so Q has an element of order 4. Torsion-freeness of K, by contrast, ensures that Λ has no
element of order 4, since D has exponent 2; this distinguishes Λ from Γ0 in Proposition 4.3. It
also identiﬁes En as the torsion subgroup of Γn , the intrinsic starting point for recovering n in
Proposition 6.9.

                              4. The binary-carry construction
   The distinction between a measured space and its group law already appears on the four-point
set F2 × F2 . Consider
                            (x, y) + (x0 , y 0 ) = (x + x0 , y + y 0 ),
                             (x, y)  (x0 , y 0 ) = (x + x0 , y + y 0 + xx0 ),
with all coordinates on the right computed in F2 . The ﬁrst law gives the Klein four-group; for
the second,
                                   (x, y) 7−→ x    e + 2ye (mod 4)
is an isomorphism with Z/4Z, where tildes denote representatives in {0, 1}. Both laws never-
theless have the same uniform Haar probability measure. Their diﬀerence is the binary carry
xx0 .
   We globalize this carry K-equivariantly. The resulting compact abelian group C0 admits a
K-equivariant, measure-preserving homeomorphism from X × Y = D,                b but its group law is not
the coordinatewise one. Its Pontryagin dual E0 will deﬁne Γ0 .
4.1. The common linear and quadratic modules. Let V = R4 , let e1 , . . . , e4 be its standard
basis, and put
                                   e = e1 ,   b(v) = v ⊗F2 v.
Deﬁne
                    B = spanF2 {b(v) : v ∈ V } ⊆ V ⊗F2 V,     D = V ⊕ B.
The tensor product is over F2 , not over R.
   Let K act on V through π2 : K ↠ SL4 (R). Its diagonal action on V ⊗F2 V preserves B, since
                                          k · b(v) = b(k · v),
and therefore acts on D. These are countable discrete F2 -vector spaces, so D has exponent 2
and
                                      v7→(v,0) (v,w)7→w
                              0 −→ V −−−−−→ D −−−−−−→ B −→ 0
is a split K-equivariant exact sequence.
   The polarization of b is bilinear:
                              b(u + v) − b(u) − b(v) = u ⊗ v + v ⊗ u.


                                                  101
For an ordered F2 -basis (ui )i≥1 of V , a basis of B is
                                  ui ⊗ ui ,         ui ⊗ uj + uj ⊗ ui        (i < j).
                 P
Indeed, if v =   i xi ui , then
                                   X                        X
                       b(v) =             xi (ui ⊗ ui ) +         xi xj (ui ⊗ uj + uj ⊗ ui ).
                                    i                       i<j

Conversely,
                        ui ⊗ uj + uj ⊗ ui = b(ui + uj ) + b(ui ) + b(uj ),
and linear independence follows from the tensor-product basis (ui ⊗ uj )i,j . These are precisely
the tensors ﬁxed by interchanging the two factors; thus
                                           B = (V ⊗F2 V )S2 = Γ2F2 (V ),
the divided square of V . Crucially, this is the invariant subspace, not the ordinary symmetric-
square quotient
                                   Sym2F2 (V ) = (V ⊗F2 V )S2 .
Indeed, the canonical map from invariants to coinvariants kills every oﬀ-diagonal basis element
ui ⊗ uj + uj ⊗ ui .
   For q ∈ B ∗ = HomF2 (B, F2 ), the displayed expansion gives
                                   X                         X
                     q(b(v)) =            xi q(ui ⊗ ui ) +         xi xj q(ui ⊗ uj + uj ⊗ ui ).
                                     i                       i<j

Thus B ∗ parametrizes the Boolean quadratic functions on V with zero constant term: diagonal
coordinates supply the linear terms, and oﬀ-diagonal coordinates the quadratic terms. In par-
ticular, for every ﬁnite J ⊆ N, the restriction of v 7→ q(b(v)) to spanF2 {uj : j ∈ J} is a Boolean
polynomial of degree at most 2.
   Via
                                                                 
                               (ℓ, q) 7−→ (v, w) 7→ (−1)ℓ(v)+q(w) ,
Pontryagin duality identiﬁes
              b = X × Y,
              D                    X = V ∗ = HomF2 (V, F2 ),               Y = B ∗ = HomF2 (B, F2 ).
With their pointwise-convergence topologies, X and Y are compact products of copies of F2 .
     b = X × Y has coordinatewise addition and Haar probability measure
Thus D
                                                   m = mX ⊗ mY .
  The dual actions are
                        (k · ℓ)(v) = ℓ(k −1 · v),                 (k · q)(w) = q(k −1 · w).
4.2. The carry group. For a ∈ F2 , let ae ∈ {0, 1} ⊂ Z denote its standard representative. For
(ℓ, q) ∈ X × Y , deﬁne Fℓ,q : V → Z/4Z by
                                                     ^ (mod 4),
                                               g + 2q(b(v))
                                    Fℓ,q (v) = ℓ(v)
and set
                              C0 = {Fℓ,q : (ℓ, q) ∈ X × Y } ⊆ (Z/4Z)V .
Equip (Z/4Z)V with the product topology and C0 with the subspace topology. The K-action
is
                                        (k · F )(v) = F (k −1 · v).
It preserves C0 , since k · Fℓ,q = Fk·ℓ,k·q .
   For s, s0 ∈ F2 , the standard lifts satisfy the binary-carry identity
                                         se + se0 = s^
                                                     + s0 + 2se se0     (mod 4).
For ℓ, ℓ0 ∈ X, set
                                                rℓ,ℓ0 = (ℓ ⊗ ℓ0 )|B ∈ Y.


                                                            102
Here (ℓ ⊗ ℓ0 )(u ⊗ v) = ℓ(u)ℓ0 (v). Since
                                        rℓ,ℓ0 (b(v)) = ℓ(v)ℓ0 (v),
and the elements b(v) span B, the map (ℓ, ℓ0 ) 7→ rℓ,ℓ0 is symmetric, bilinear, and normalized:
rℓ,0 = r0,ℓ = 0. Bilinearity gives the cocycle identity
                                  rℓ,ℓ0 + rℓ+ℓ0 ,ℓ00 = rℓ0 ,ℓ00 + rℓ,ℓ0 +ℓ00 .
Evaluation at any w ∈ B uses only ﬁnitely many coordinates of ℓ and ℓ0 , so r is continuous for
the pointwise topologies. It is therefore a continuous, symmetric, normalized, K-equivariant
Y -valued 2-cocycle on X. Applying the binary-carry identity at each v ∈ V gives
                                   Fℓ,q + Fℓ0 ,q0 = Fℓ+ℓ0 , q+q0 +rℓ,ℓ0 .                  (4.2)
Thus C0 contains 0 and is closed under addition. Since the ambient group has exponent 4, every
F ∈ C0 has inverse −F = 3F ∈ C0 ; hence C0 is a subgroup.
  Reduction modulo 2 recovers ℓ from Fℓ,q , and the remaining values q(b(v)) recover q, since
the b(v) span B. Hence (ℓ, q) 7→ Fℓ,q is a bijection under which pointwise addition becomes
                                                                                 
                              (ℓ, q) ⋆0 (ℓ0 , q 0 ) = ℓ + ℓ0 , q + q 0 + rℓ,ℓ0 .
Proposition 4.1. The set C0 is a compact subgroup of (Z/4Z)V . The map
                             Φ0 : X × Y −→ C0 ,                 Φ0 (ℓ, q) = Fℓ,q ,
is a K-equivariant homeomorphism that identiﬁes the Haar measure of C0 with m. It is a
                                                                                      b
topological group isomorphism for ⋆0 , but not for coordinatewise addition on X × Y = D.
Proof. Each coordinate of Φ0 is continuous, and the preceding recovery argument shows that Φ0
is bijective. It is therefore a homeomorphism from the compact space X ×Y onto its image in the
Hausdorﬀ group (Z/4Z)V ; in particular, C0 is compact and closed. The identity b(k ·v) = k ·b(v)
gives K-equivariance.
   Under Φ0 , translation by Fℓ0 ,q0 is the triangular map
                                                                           
                                  (ℓ, q) 7−→ ℓ + ℓ0 , q + q 0 + rℓ,ℓ0 .
This map preserves m: its ﬁrst coordinate is translation in X, and each ﬁber map is translation
in Y . Consequently, (Φ0 )∗ m is the Haar measure of C0 .
   Equation (4.2) identiﬁes Φ0 as a topological group isomorphism for ⋆0 . It cannot be a
homomorphism for coordinatewise addition: if ℓ(e) = 1, then rℓ,ℓ (b(e)) = 1 and Fℓ,0 (e) = 1.
Thus Fℓ,0 has order 4, whereas X × Y with coordinatewise addition has exponent 2.             □

4.3. Dualizing the carry extension. The binary carry is invisible to the measured K-space
but survives Pontryagin duality as a nonsplit extension. Let E0 = C c0 , written additively and
                                                                                 c0 . For v ∈ V ,
equipped with the dual K-action, so that biduality identiﬁes C0 canonically with E
deﬁne
                                 v ∈ E0 ,
                                ε(0)          ε(0)         F (v)
                                                v (F ) = i       ,
          √
where i = −1. Since V is countable, C0 is compact metrizable and E0 is countable. Moreover,
  (0)                                          (0)                  (0)
4εe = 0, and any ℓ ∈ X with ℓ(e) = 1 gives εe (Fℓ,0 ) = i. Thus εe has order 4, exhibiting
the obstruction to splitting.
Lemma 4.2. There are K-equivariant exact sequences
                                        b = X × Y −→ X −→ 0,
                              0 −→ Y −→ D
                                               ȷ0          ρ0
                                  0 −→ Y −−→ C0 −−→ X −→ 0,
whose Pontryagin duals are
                              0 −→ V −→ D = V ⊕ B −→ B −→ 0,
                                                ι          σ
                                  0 −→ V −−0→ E0 −−−
                                                   → B −→ 0.
                                                   0




                                                     103
The sequences involving Db and D split K-equivariantly. The sequence involving E0 does not
split even as an extension of abelian groups; equivalently, the map ρ0 admits no continuous
homomorphic section. The maps for the carry extension satisfy
                       ȷ0 (q) = F0,q ,        ρ0 (Fℓ,q ) = ℓ,        ι0 (v)(Fℓ,q ) = (−1)ℓ(v) .
The map σ0 is characterized by
                               η(F0,q ) = (−1)q(σ0 (η))            (η ∈ E0 , q ∈ Y ),
and
                                     2ε(0)
                                       v = ι0 (v),              σ0 (ε(0)
                                                                     v ) = b(v).

Proof. The sequences for D b and D split by their direct-sum decompositions. For the carry
sequence, (4.2) shows that ȷ0 and ρ0 are continuous homomorphisms with
                                         ker ρ0 = {F0,q : q ∈ Y } = ȷ0 (Y ).
Since ρ0 (Fℓ,0 ) = ℓ, the sequence is exact; all its maps are K-equivariant. Pontryagin duality
gives the stated discrete extension, with σ0 obtained by restricting a character to ȷ0 (Y ) and
using Yb = B. For evaluation characters,
                                     ε(0)
                                      v (F0,q ) = i
                                                    2q(b(v))
                                                             = (−1)q(b(v)) ,
       (0)
so σ0 (εv ) = b(v). Since the b(v) span B, these characters also give surjectivity of σ0 .
                                                     ∼ X; since X
   If σ0 (η) = 0, then η factors through C0 /ȷ0 (Y ) =          b = V , it equals ι0 (v) for a unique
v ∈ V . Finally,
                                                 2
                                    ε(0)
                                     v (Fℓ,q )        = (−1)Fℓ,q (v) = (−1)ℓ(v) ,
               (0)
which gives 2εv = ι0 (v).
                                           ∼ V ⊕ B would have exponent 2, contradicting the
   If the discrete sequence split, then E0 =
                     (0)
order-four element εe . By Pontryagin duality, ρ0 therefore admits no continuous homomorphic
section.                                                                                  □
  Deﬁne
                                         Γ0 = E0 o K,            Λ = D o K.
  The common measured K-action identiﬁes the group factors; the order-four carry distin-
guishes the groups.
Proposition 4.3. There is an isomorphism
                                                         ∼ L(Λ),
                                                  L(Γ0 ) =
       6∼ Λ.
but Γ0 =
Proof. Equation (2.1) and Proposition 4.1 give
                                   ∼ L∞ (C0 , m) o K
                            L(Γ0 ) =
                                             ∼ L∞ (X × Y, m) o K =
                                             =                   ∼ L(Λ).

   Since K is torsion-free, every ﬁnite-order element of Λ = D oK lies in D, which has exponent
                                                6∼ Λ.
         (0)
2. But εe ∈ E0 ⊂ Γ0 has order 4. Hence Γ0 =                                                  □

                     5. ICC, property (T ), and the basic counterexample
   The goal of this section is the two-group counterexample of Corollary 5.10. Proposition 4.3
already shows that Γ0 and Λ are nonisomorphic but have isomorphic group von Neumann
algebras. By Lemma 2.1, it therefore suﬃces to prove that Λ is ICC and has property (T ).
These two properties reduce, respectively, to inﬁnite orbits on D and a uniform spectral estimate
on Db =X ×Y.


                                                          104
5.1. The ICC property.
Lemma 5.1. Let an ICC group H act by automorphisms on an abelian group A. If every
nonzero element of A has an inﬁnite H-orbit, then A o H is ICC.
Proof. If h 6= 1, the conjugacy class of (a, h) maps onto the inﬁnite conjugacy class of h in H.
If h = 1 and a 6= 0, then
                             (0, k)(a, 1)(0, k)−1 = (k · a, 1)              (k ∈ H).
The latter conjugacy class is inﬁnite because the H-orbit of a is inﬁnite.                                      □
  Since D = V ⊕ B, Lemma 5.1 reduces the ICC assertion to the following orbit calculation,
which will also distinguish the groups in Section 6.
Lemma 5.2. Every nonzero element of V ⊕ B has an inﬁnite Q-orbit.
Proof. Elementary transvections give inﬁnite orbits on V ; on its tensor square, specialization
in one tensor variable distinguishes the same transvections.
   For v ∈ V \ {0}, choose j with vj 6= 0 and i 6= j. The transvections
                      gn = I + tn Eij ∈ Q              (n ≥ 1),          g n v = v + tn v j e i
give pairwise distinct vectors.
   For B ⊆ V ⊗F2 V , introduce separate variables for the tensor factors:
         S = F2 [t1 , t2 ],        ∼ (R ⊗F R)16 =
                            V ⊗F V =               ∼ S 16 ,    t1 = t ⊗ 1,                        t2 = 1 ⊗ t,
                                    2                  2

so g ∈ Q acts as g(t1 ) ⊗ g(t2 ). Given w ∈ S 16 \ {0}, remove its largest common power of t2 :
                                        w = ta2 w0 ,         w0 (t1 , 0) 6= 0.
Write
                                              X
                                              4
                              w0 (t1 , 0) =         e j ⊗ wj ,       wj ∈ F2 [t1 ]4 .
                                              j=1
Choose j with wj 6= 0 and i 6= j, and set
                  z = (Eij ⊗ I)w0 (t1 , 0) 6= 0,             hr = I + tr Eij ∈ Q (r ≥ 1).
If hr w = hs w, cancel ta2 and specialize t2 = 0. Since hr (0) = I in the second tensor factor, this
gives
                                            (tr1 + ts1 )z = 0.
As F2 [t1 ]16 is torsion-free and z 6= 0, we obtain r = s. Every nonzero element of B therefore
has an inﬁnite orbit. Finally, for (v, w) ∈ V ⊕ B, use the equivariant projection to V if v 6= 0,
and the preceding argument if v = 0 and w 6= 0.                                                   □
Proposition 5.3. The group Λ is ICC.
Proof. Lemma 5.2 and the surjection K ↠ Q show that every nonzero element of D has an
inﬁnite K-orbit. Since K is ICC by Lemma 3.3, Lemma 5.1 shows that Λ = D o K is ICC. □
5.2. A spectral criterion for property (T ). The extension
                                        1 −→ D −→ Λ −→ K −→ 1
has a property-(T ) quotient by Proposition 3.1. By the extension principle in Subsection 2.2,
it therefore suﬃces to prove relative property (T ) for (Λ, D). The following spectral criterion
combines these two steps: an invariant spectral measure satisfying a uniform detection estimate
must have an atom at the trivial character.
   If π : A o H → U(H) is a unitary representation with A abelian, the joint spectral theorem
gives a unique projection-valued measure P on Ab such that
                                             Z
                                 π(a) =           χ(a) dP (χ)          (a ∈ A).
                                              b
                                              A
Its covariance relation is
                                        π(h)P (U )π(h)−1 = P (h · U )


                                                           105
for every Borel set U ⊆ Ab and h ∈ H.
   An H-ﬁxed unit vector therefore induces an H-invariant scalar spectral probability measure,
and P ({1}) projects onto the A-ﬁxed subspace. The criterion is a spectral form of the relative-
property-(T ) criterion in [CT11].
Lemma 5.4. Let a countable property-(T ) group H act by automorphisms on a countable abelian
group A. Suppose there are a ﬁnite set J ⊆ A and c > 0 such that every H-invariant Borel
probability measure µ on Ab satisﬁes
                              XZ                                           
                                       |χ(a) − 1|2 dµ(χ) ≥ c 1 − µ({1}) .                   (5.1)
                             a∈J
                                   b
                                   A

Then A o H has property (T ).
Proof. Suppose A o H does not have property (T ). Choose a unitary representation π with
asymptotically invariant unit vectors (ξn ) but no nonzero invariant vector. For a Kazhdan pair
(F, κ) of H, let PH project onto HH . The Kazhdan estimate on (HH )⊥ gives
                         kξn − PH ξn k ≤ κ−1 max kπ(h)ξn − ξn k −→ 0.
                                                   h∈F

Hence, after discarding ﬁnitely many terms,
                                                      P H ξn
                                              ηn =
                                                     kPH ξn k
are H-invariant and satisfy kηn − ξn k → 0.
  Let P be the spectral measure of π|A and deﬁne
                                         µn (U ) = hP (U )ηn , ηn i.
Covariance makes µn H-invariant. For every a ∈ J,
                      kπ(a)ηn − ηn k ≤ 2kηn − ξn k + kπ(a)ξn − ξn k −→ 0,
and hence                Z
                              |χ(a) − 1|2 dµn (χ) = kπ(a)ηn − ηn k2 −→ 0.
                          b
                          A
As J is ﬁnite, (5.1) forces µn ({1}) → 1. Thus P ({1})ηn 6= 0 for large n. This vector is A-ﬁxed
by deﬁnition of P ({1}), and H-ﬁxed by covariance, since the trivial character is H-ﬁxed. It is
therefore A o H-invariant, a contradiction.                                                   □

5.3. A quadratic Boolean estimate. Let F2 be the ﬁeld with two elements. For m ≥ 2,
every function p : Fm
                    2 → F2 has a unique multilinear polynomial representative; let deg p denote
its degree and supp(p) = {x ∈ Fm2 : p(x) 6= 0}.

Lemma 5.5. Let m ≥ 2. If a nonzero polynomial function p : Fm
                                                            2 → F2 has degree at most 2,
then
                                 | supp(p)| ≥ 2m−2 .
Equivalently, p is nonzero on at least one quarter of the Boolean cube.
Proof. The assertion is immediate for m = 2. For m ≥ 3, write
                                   p(x0 , xm ) = p0 (x0 ) + xm p1 (x0 ),
where deg p0 ≤ 2 and deg p1 ≤ 1. If p1 = 0, then p0 6= 0; induction gives
                        | supp(p)| = 2| supp(p0 )| ≥ 2 · 2(m−1)−2 = 2m−2 .
Suppose that p1 6= 0. A nonzero aﬃne-linear function on Fm−1 2 is nonzero on at least 2m−2 points:
it is either the constant function 1, or its two ﬁbers have equal size. For every x0 ∈ supp(p1 ),
exactly one of p(x0 , 0) and p(x0 , 1) is nonzero. Therefore
                                   | supp(p)| ≥ | supp(p1 )| ≥ 2m−2 .                          □


                                                     106
5.4. A uniform evaluation estimate. The spectral estimate comes from one K-orbit: tran-
sitivity makes detection at e equivalent to detection at any primitive vector, while Lemma 5.5
ensures that every nontrivial character is detected by many such vectors.
   A vector v = (v1 , . . . , v4 ) ∈ R4 is primitive if its coordinates generate the unit ideal. Let
                               P = {v ∈ R4 : (v1 , v2 , v3 , v4 ) = R}.
For N ≥ 1, put
                          RN = spanF2 {1, t, . . . , tN −1 },                4
                                                                       VN = RN .
Lemma 5.6. The action of K on P is transitive, and
                                     |P ∩ VN | = 7 · 24N −3 + 1.
Equivalently,
                                       |P ∩ VN |  7
                                                 = + 2−4N .
                                         |VN |    8
Proof. Since π2 : K ↠ SL4 (R) is onto, the K-orbits on V are the SL4 (R)-orbits. As R is
Euclidean, elementary row reduction takes any primitive vector to e = (1, 0, 0, 0), proving
transitivity.
   Write PN = |P ∩ VN |, with P0 = 0. Partitioning VN \ {0} by the monic greatest common
divisor of the four coordinates gives
                                                   X
                                                   N −1
                                      24N − 1 =           2d PN −d .
                                                   d=0
Subtract twice the corresponding identity for N − 1:
                        PN = (24N − 1) − 2(24N −4 − 1) = 7 · 24N −3 + 1.                         □
  For z = (ℓ, q) ∈ X × Y , deﬁne
                                    z[v] = (ℓ(v), q(b(v))) ∈ F22 .
We say that v detects z if z[v] 6= (0, 0). The two bits are evaluated separately by (v, 0) and
(0, b(v)) in D = V ⊕ B; adding them in F2 would allow cancellation.
Lemma 5.7. If µ is a K-invariant probability measure on X × Y , then
                                                     1                   
                              µ{z : z[e] 6= (0, 0)} ≥ 1 − µ({(0, 0)}) .                 (5.3)
                                                     7
Proof. By K-invariance, detection has the same probability at every primitive vector. Indeed,
set
                                      pµ = µ{z : z[e] 6= (0, 0)}.
Then
             (k · z)[k · v] = z[v]      =⇒        µ{z : z[v] 6= (0, 0)} = pµ (v ∈ P).
   Suppose z = (ℓ, q) is detected by some v ∈ VN . At least one of
                                v 7−→ ℓ(v),     v 7−→ q(b(v))
is a nonzero Boolean polynomial on VN = ∼ F . The ﬁrst is linear and the second has degree at
                                            4N
                                            2
most 2, since b(v) = v ⊗ v and q is linear. Lemma 5.5 therefore gives at least 24N −2 detecting
vectors. By Lemma 5.6, exactly
                                   |VN | − |P ∩ VN | = 24N −3 − 1
of them can be nonprimitive, so at least 24N −3 + 1 primitive vectors detect z. Write
                            UN = {z : z[v] 6= (0, 0) for some v ∈ VN }.
Integrating the pointwise count and using |P ∩ VN | = 7 · 24N −3 + 1 yields
                                                         1
                     pµ |P ∩ VN | ≥ (24N −3 + 1)µ(UN ) ≥ |P ∩ VN |µ(UN ).
                                                         7

                                                  107
           S
Since V = N VN and the b(v) span B, the sets UN increase to (X × Y ) \ {(0, 0)}. Divide by
|P ∩ VN | and let N → ∞ to obtain (5.3).                                                □
Remark 5.8. The bound 1/7 = (1/4 − 1/8)/(7/8) comes from restricting detection to primitive
vectors: a nonzero Boolean polynomial of degree at most 2 detects at least 1/4 of the cube,
while the nonprimitive vectors have asymptotic density 1/8.
  More generally, in rank j ≥ 3, the nonprimitive vectors have asymptotic density 21−j . The
same argument gives the bound
                                      1/4 − 21−j   2j−3 − 1
                                    cj =         =          .
                                       1 − 21−j    2j−1 − 1
It is positive exactly when j ≥ 4, with c4 = 1/7. Thus 4 is the smallest rank for which this
argument yields a spectral gap.
Proposition 5.9. The group Λ has property (T ).
                                                           b = X × Y , and choose
Proof. Let µ be a K-invariant Borel probability measure on D
                                   d1 = (e, 0),         d2 = (0, b(e)).
                                                                  b = X × Y satisﬁes
Writing 1S for the indicator of a set S, a character z = (ℓ, q) ∈ D
                            |z(d1 ) − 1|2 + |z(d2 ) − 1|2 ≥ 4 1{z[e]6=(0,0)} .
After integration, Lemma 5.7 gives
                           2 Z
                           X                                   4           
                                   |χ(dj ) − 1|2 dµ(χ) ≥         1 − µ({1}) .
                               b
                           j=1 D
                                                               7
Thus (5.1) holds with (A, H, J, c) = (D, K, {d1 , d2 }, 4/7), proving property (T ) for Λ.      □
   These rigidity results and the common group factor now give the promised two-group coun-
terexample.
5.5. The basic counterexample.
Corollary 5.10 (Two-group counterexample). The groups Λ and Γ0 are nonisomorphic ICC
property-(T ) groups with isomorphic group von Neumann algebras.
Proof. Proposition 4.3 shows that the groups are nonisomorphic and that their group von Neu-
mann algebras are isomorphic. Propositions 5.3 and 5.9 show that Λ is ICC and has property
(T ). Applying Lemma 2.1 to the factor isomorphism gives the same properties for Γ0 .     □

                   6. An infinite fiber of the group-factor functor
  To extend Corollary 5.10 to a countably inﬁnite ﬁber, we keep the measured K-space X × Y
ﬁxed and apply the same binary carry after shifting each of the four coordinate sequences
by n. The common measured action identiﬁes the resulting group factors; an intrinsic ﬁnite-
orbit invariant recovers the 4n carry-free coordinates. The groups Γn will also be pairwise
commensurable.
6.1. Pulling back the carry. For n ≥ 0, deﬁne
                              Tn : X −→ X,             (Tn ℓ)(v) = ℓ(tn v).
The R-linearity of the K-action makes Tn continuous and K-equivariant. It is surjective: for
λ ∈ X, extend the functional tn v 7→ λ(v) on tn V to V . Its kernel is
                                          ∼ HomF (V /tn V, F2 ),
                Zn = {ℓ ∈ X : ℓ|tn V = 0} =                            |Zn | = 24n .
                                                          2

  For ℓ, ℓ0 ∈ X, put
                                       cn (ℓ, ℓ0 ) = rTn ℓ,Tn ℓ0 ∈ Y.
Equip X × Y with the operation
                                                                                
                           (ℓ, q) ⋆n (ℓ0 , q 0 ) = ℓ + ℓ0 , q + q 0 + cn (ℓ, ℓ0 ) .          (6.3)


                                                    108
To see the original four-point carry inside this formula, write
                                                                
                    xi,j = ℓ(tj ei ),      yi,j = q b(tj ei )       (1 ≤ i ≤ 4, j ≥ 0).
Since
                                                       
                                    cn (ℓ, ℓ0 ) b(tj ei ) = xi,j+n x0i,j+n ,
the diagonal coordinate pair (xi,j+n , yi,j ) adds by
                               (x, y)  (x0 , y 0 ) = (x + x0 , y + y 0 + xx0 ).
This is exactly the Z/4Z carry from Section 4. The ﬁrst n coordinates xi,0 , . . . , xi,n−1 in each
of the four directions never enter the carry.
   For n = 0, Proposition 4.1 identiﬁes this coordinate model with the function-space group C0
of Section 4 via Φ0 (ℓ, q) = Fℓ,q . We use this as a standing identiﬁcation. For every n ≥ 0, write
Cn for X × Y equipped with ⋆n .
Lemma 6.1. For every n ≥ 0, the operation ⋆n makes Cn a compact abelian group with Haar
probability measure m. The group K acts by continuous automorphisms through the coordinate
action
                                  k · (ℓ, q) = (k · ℓ, k · q),
which is independent of n.
Proof. The pulled-back carry cn is continuous, symmetric, bilinear, and K-equivariant. Its
cocycle identity makes (6.3) associative; symmetry makes it commutative. The identity and
inverse are (0, 0) and (ℓ, q + cn (ℓ, ℓ)), respectively. Thus Cn is a compact abelian group and the
coordinate K-action is by continuous automorphisms.
   Translation by (ℓ0 , q 0 ) has the form
                                                                               
                                  (ℓ, q) 7−→ ℓ + ℓ0 , q + q 0 + cn (ℓ, ℓ0 ) .
It translates X and then translates each Y -ﬁber. Hence it preserves m, which is therefore the
Haar measure of every Cn .                                                                  □
  At this point the measured K-space, and therefore the resulting group factor, no longer
depends on n. We must now recover the shifted carry from the compact group structure. Two
maps isolate its eﬀects: ρn describes the carry extension, while pn identiﬁes the 4n carry-free
coordinates.
  Deﬁne
                             ρn : Cn −→ X, ρn (ℓ, q) = ℓ,
                                 pn : Cn −→ C0 , pn (ℓ, q) = (Tn ℓ, q).
The ﬁrst map exhibits Cn as an extension of X by Y . Since cn (ℓ, ℓ0 ) = rTn ℓ,Tn ℓ0 , the second is a
surjective, continuous K-equivariant homomorphism with
                                            ker pn = Zn × {0}.
Thus pn forgets exactly the 4n carry-free bits. Its dual will give the ﬁnite-index inclusion in
Theorem 1.2.
  A continuous linear section of Tn gives a noncanonical isomorphism of compact abelian groups
                                         ∼ C0 × (Z/2Z)4n .
                                      Cn =
For n > 0, this splitting is not K-equivariant: the carry-free coordinates cannot be separated
from the tail as K-modules. Subsection 6.5 shows that their K-action recovers n.
   To recover the group structure forgotten by the common measure, set
                                             cn ,
                                        En = C          Γn = En o K.
Under the standing identiﬁcation via Φ0 , E0 and Γ0 agree with the groups deﬁned in Section 4.
  To describe the extension dual to ρn , deﬁne, for v ∈ V ,
                                           ιn (v)(ℓ, q) = (−1)ℓ(v) .


                                                     109
For η ∈ En , deﬁne σn (η) ∈ B by

                                     η(0, q) = (−1)q(σn (η))              (q ∈ Y ).

This uniquely determines σn (η), since restriction to {0} × Y is a character of Y and Yb = B.
  The next lemma makes the shifted carry visible on the dual side: every En retains the original
order-four elements, and their doubles record the shift tn .

Lemma 6.2. For every n ≥ 0, the group En is countable and ﬁts into the K-equivariant exact
sequence
                                                      ι          σ
                                      0 −→ V −−n→ En −−−
                                                       → B −→ 0.
                                                       n
                                                                                            (6.7)
For v ∈ V , deﬁne
                                                        v ◦ pn ∈ En .
                                               εv(n) = ε(0)
Then
                                σn (εv(n) ) = b(v),              2εv(n) = ιn (tn v).        (6.8)
                (n)
In particular, εe     has order 4.

Proof. Pontryagin duality applied to the exact sequence of compact abelian K-groups
                                                    q7→(0,q)         ρn
                                 0 −→ Y −−−−−→ Cn −−−→ X −→ 0

gives (6.7); metrizability of Cn gives countability of En . The two formulas in (6.8) follow from

                                     εv(n) (0, q) = ε(0)
                                                     v (F0,q ) = (−1)
                                                                      q(b(v))
                                                                              ,
                                               2                                 n
                                εv(n) (ℓ, q)        = (−1)(Tn ℓ)(v) = (−1)ℓ(t v) .
                                         (n)
Since tn e 6= 0 and ιn is injective, εe        has order 4.                                    □

   The essential point is the factor tn in (6.8): the lift of b(v) doubles to ιn (tn v). Thus n
records where the carry begins. Subsection 6.5 will recover the 4n carry-free coordinates from
the ﬁnite-orbit part of En [2]/2En .

6.2. The common group factor. The compact group law depends on n, but the measured
K-space does not. Fourier transform therefore gives the same crossed product throughout the
family.

Proposition 6.3. For every n ≥ 0, there is an isomorphism
                                                           ∼ L(Λ).
                                                    L(Γn ) =

Proof. By Lemma 6.1, the identity (Cn , m) → (X × Y, m) is a K-equivariant isomorphism of
probability spaces. Equation (2.1) therefore gives
                                     ∼ L∞ (Cn , m) o K
                              L(Γn ) =
                                     ∼ L∞ (X × Y, m) o K =
                                     =                   ∼ L(Λ). □


6.3. ICC and property (T ). Both rigidity properties transfer along the common group factor.

Proposition 6.4. For every n ≥ 0, the group Γn is ICC and has property (T ).

Proof. Propositions 5.3 and 5.9 show that Λ is ICC and has property (T ). Proposition 6.3
identiﬁes L(Γn ) with L(Λ). The conclusion now follows from Lemma 2.1.                 □


                                                           110
6.4. Finite-index embeddings and commensurability.
Proposition 6.5 (Finite-index embeddings). For every n ≥ 0, the group Γn contains a subgroup
isomorphic to Γ0 of index 24n . Consequently, the groups (Γn )n≥0 are mutually commensurable.
Proof. Dualizing
                                                              pn
                             0 −→ Zn × {0} −→ Cn −−−→ C0 −→ 0
gives a K-equivariant exact sequence
                                p∗          resZ
                                          cn −→ 0,
                    0 −→ E0 −−−
                              → En −−−−n→ Z
                              n
                                                                p∗n (η) = η ◦ pn .
Here resZn (η) is the character ℓ 7→ η(ℓ, 0) of Zn . Hence p∗n (E0 ) o K =∼ Γ0 is a subgroup of Γn
of index
                                         cn | = |Zn | = 24n .
                                        |Z
Since every Γn contains a ﬁnite-index copy of Γ0 , the groups are mutually commensurable.       □

6.5. Pairwise nonisomorphism. The parameter n is detected by the ﬁnite orbits on an in-
trinsic 2-torsion quotient. By (6.3), doubling in Cn is
                                                                   
                                          2(ℓ, q) = 0, cn (ℓ, ℓ) .
Hence Cn and En have exponent dividing 4. Since K is torsion-free, the torsion elements of
Γn = En o K form the characteristic abelian subgroup
                                             Tor(Γn ) = En .
For an abelian group A, write
                        A[2] = {a ∈ A : 2a = 0},             2A = {2a : a ∈ A}.
Since 4En = 0, conjugation induces an intrinsic action of Γn /En on En [2]/2En . Deﬁne
                        i(Γn ) = {a ∈ En [2]/2En : |(Γn /En ) · a| < ∞} .
Because En = Tor(Γn ), this is an invariant of the abstract group. We will prove
                                         i(Γn ) = |V /tn V | = 24n ,
so its ﬁrst two values are 1 and 16. The calculation proceeds through the doubling map on En ,
with ιn and σn as in (6.7).
Lemma 6.6. There is a unique K-equivariant surjective F2 -linear map
                                     d : B −→ V,          d(b(v)) = v.
Proof. Fix an ordered F2 -basis (ui )i≥1 of V . Using the corresponding basis for B from Subsec-
tion 4.1, deﬁne d by
                      ui ⊗ ui 7−→ ui ,        ui ⊗ uj + uj ⊗ ui 7−→ 0 (i < j).
The expansion of b(v) gives d(b(v)) = v. Since the elements b(v) span B, this identity implies
surjectivity, uniqueness, and K-equivariance: d(k · b(v)) = k · v = k · d(b(v)).            □
Lemma 6.7. For every n ≥ 0 and η ∈ En ,
                                                                   
                                          2η = ιn tn d(σn (η)) .                            (6.10)
Consequently,
                           2En = ιn (tn V )        and    En [2] = σn−1 (ker d).            (6.11)
                                                                                   (n)
Proof. Both sides of (6.10) are homomorphisms in η. By (6.8), they agree on εv ; they both
vanish on ιn (V ). These elements generate En , since their images under σn span B and ker σn =
ιn (V ). This proves the identity.
    Surjectivity of d and σn gives 2En = ιn (tn V ). Since multiplication by tn on V and ιn are
injective, (6.10) also gives En [2] = σn−1 (ker d).                                           □


                                                    111
   Now set
                                               An = En [2]/2En .
For its ﬁnite-orbit subgroup, write
                                       n = {a ∈ An : K · a is ﬁnite}.
                                      Aﬁn
Lemma 6.8. For every n ≥ 0, there is a K-equivariant exact sequence
                                   0 −→ V /tn V −→ An −→ ker d −→ 0.                                         (6.13)
The maps are
                       v + tn V 7−→ ιn (v) + 2En ,    η + 2En 7−→ σn (η).
                                         n
Under the resulting identiﬁcation of V /t V with its image in An ,
                                       Aﬁn      n
                                        n = V /t V,           |Aﬁn
                                                                n |=2 .
                                                                     4n


Proof. By (6.11), restriction of σn gives the exact sequence
                                               ι              σ
                                   0 −→ V −−n→ En [2] −−−
                                                        → ker d −→ 0.
                                                        n


Quotienting by 2En = ιn (tn V ) gives (6.13).
  Every element of V /tn V has ﬁnite orbit. Conversely, if a ∈ An has nonzero image in ker d,
that image has inﬁnite K-orbit by Lemma 5.2 and K ↠ Q. Equivariance forces a to have
inﬁnite orbit as well. Thus Aﬁn        n                    4n because V /tn V ∼ (R/(tn ))4 . □
                             n = V /t V , which has order 2                    =
Proposition 6.9. The groups (Γn )n≥0 are pairwise nonisomorphic.
Proof. An isomorphism Γn =  ∼ Γm preserves the characteristic torsion subgroup and hence in-
                          ∼
duces an isomorphism An = Am intertwining the quotient-group actions. It therefore identiﬁes
their ﬁnite-orbit subgroups. Lemma 6.8 gives
                                         24n = |Aﬁn
                                                 n | = |Am | = 2
                                                         ﬁn      4m
                                                                    ,
so n = m.                                                                                                         □
Proof of Theorem 1.2. Propositions 6.3 and 6.9 show that the Γn are pairwise nonisomorphic
and have group factors isomorphic to L(Λ). By Lemma 6.2, every Γn contains an element of
order 4, whereas Λ has none by Proposition 4.3. Thus Λ =  6∼ Γn for every n.
  Propositions 5.3, 5.9, and 6.4 give the ICC and property-(T ) assertions. Since the groups are
countable, property (T ) also implies ﬁnite generation. Finally, Proposition 6.5 realizes Γ0 as a
subgroup of Γn of index 24n , so the Γn are mutually commensurable.                            □
Acknowledgments. We thank Sorin Popa for valuable comments on the historical context,
the countability theorem, and the ﬁnite-to-one question; Ionuţ Chifan for clarifying the origi-
nal formulation of Connes’s conjecture; and François Charles and Cyril Houdayer for careful
readings and helpful suggestions.
   During the preparation of this manuscript, we learned of independent and concurrent work
by Shuoxing Zhou also establishing a counterexample to Connes’s rigidity conjecture, developed
in part with the assistance of GPT-5.6 Sol.

                                                   References
[BHV08] B. Bekka, P. de la Harpe, and A. Valette, Kazhdan’s Property (T), New Mathematical Monographs 11,
         Cambridge University Press, 2008.
[CIOS23] I. Chifan, A. Ioana, D. Osin, and B. Sun, Wreath-like products of groups and their von Neumann
         algebras I: W ∗ -superrigidity, Ann. of Math. (2) 198 (2023), no. 3, 1261–1303.
[Con76] A. Connes, Classiﬁcation of injective factors. Cases II1 , II∞ , IIIλ , λ 6= 1, Ann. of Math. (2) 104 (1976),
         no. 1, 73–115.
[Con80] A. Connes, A factor of type II1 with countable fundamental group, J. Operator Theory 4 (1980), no. 1,
         151–153.
[Con82] A. Connes, Classiﬁcation des facteurs, in Operator Algebras and Applications, Part 2 (Kingston, Ont.,
         1980), Proc. Sympos. Pure Math. 38, American Mathematical Society, Providence, R.I., 1982, 43–109,
         doi:10.1090/pspum/038.2/679497.
[Con94] A. Connes, Noncommutative Geometry, Academic Press, San Diego, 1994.


                                                        112
[CJ85]   A. Connes and V. F. R. Jones, Property T for von Neumann algebras, Bull. London Math. Soc. 17
         (1985), no. 1, 57–62.
[CT11]   Y. Cornulier and R. Tessera, A characterization of relative Kazhdan property T for semidirect products
         with abelian groups, Ergodic Theory Dynam. Systems 31 (2011), no. 3, 793–805.
[EJ10]   M. Ershov and A. Jaikin-Zapirain, Property (T) for noncommutative universal lattices, Invent. Math.
         179 (2010), no. 2, 303–347.
[Fur99] A. Furman, Orbit equivalence rigidity, Ann. of Math. (2) 150 (1999), no. 3, 1083–1108, Annals of
         Mathematics.
[Ioa11]  A. Ioana, W ∗ -superrigidity for Bernoulli actions of property (T ) groups, J. Amer. Math. Soc. 24 (2011),
         no. 4, 1175–1226, doi:10.1090/S0894-0347-2011-00706-6.
[Ioa18]  A. Ioana, Rigidity for von Neumann algebras, in Proceedings of the International Congress of Mathe-
         maticians 2018, Vol. III, World Scientiﬁc, 2018, 1639–1672.
[IPV13] A. Ioana, S. Popa, and S. Vaes, A class of superrigid group von Neumann algebras, Ann. of Math. (2)
         178 (2013), no. 1, 231–286.
[Kaz67] D. A. Kazhdan, Connection of the dual space of a group with the structure of its closed subgroups,
         Funct. Anal. Appl. 1 (1967), no. 1, 63–65.
[Min87] H. Minkowski, Ueber den arithmetischen Begriﬀ der Aequivalenz und über die endlichen Gruppen lin-
         earer ganzzahliger Substitutionen, J. Reine Angew. Math. 100 (1887), 449–458.
[MN43] F. J. Murray and J. von Neumann, On rings of operators. IV, Ann. of Math. (2) 44 (1943), 716–808.
[Pop06a] S. Popa, Some rigidity results for non-commutative Bernoulli shifts, J. Funct. Anal. 230 (2006), no. 2,
         273–328.
[Pop06b] S. Popa, On a class of type II1 factors with Betti numbers invariants, Ann. of Math. (2) 163 (2006),
         no. 3, 809–899.
[Pop06c] S. Popa, Strong rigidity of II1 factors arising from malleable actions of w-rigid groups, I, Invent. Math.
         165 (2006), no. 2, 369–408.
[Pop06d] S. Popa, Strong rigidity of II1 factors arising from malleable actions of w-rigid groups, II, Invent. Math.
         165 (2006), no. 2, 409–451.
[Pop07] S. Popa, Deformation and rigidity for group actions and von Neumann algebras, in Proceedings of
         the International Congress of Mathematicians (Madrid, 2006), Vol. I, European Mathematical Society,
         Zürich, 2007, 445–477, doi:10.4171/022-1/18.
[Pop13] S. Popa, Some open problems in W ∗ -rigidity, problem list, Paris, June 2013, https://www.math.ucla.
         edu/~popa/ProblemsJune2013.pdf.
[Sus77] A. A. Suslin, On the structure of the special linear group over polynomial rings, Math. USSR-Izv. 11
         (1977), no. 2, 221–238.
[Vae10] S. Vaes, Rigidity for von Neumann algebras and their invariants, in Proceedings of the International
         Congress of Mathematicians (Hyderabad, India, 2010), Vol. III, Hindustan Book Agency, 2010, 1624–
         1650, arXiv:1008.3610.




                                                       113
