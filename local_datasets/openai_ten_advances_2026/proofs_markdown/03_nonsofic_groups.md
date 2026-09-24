# Nonsofic Groups Exist

> Source: OpenAI, *Ten Advances in Mathematics and Theoretical Computer Science*, Chapter 3, PDF pages 82–99. Layout-preserving text extraction; consult the source PDF for authoritative equation rendering.

                                     Chapter 3

                       Nonsoﬁc groups exist
    Abstract. A countable group is soﬁc if every ﬁnite portion of its multiplication
    table can be modeled by permutations of a ﬁnite set, with errors on an arbitrar-
    ily small fraction of points and with nonidentity elements moving almost every
    point. We prove that the unit group LF2 (1, 2)× of the binary Leavitt algebra is not
    soﬁc, answering negatively the question of whether every countable group is soﬁc.
    The proof builds on Kun’s expander decomposition for property-(T ) groups and
    the Kun–Thom centralizer obstruction. The main new ingredient is an expander-
    matching criterion that extracts from a union of expanders one component carrying
    the required approximate commuting actions. We realize this criterion inside an
    elementary group over the Leavitt algebra, where soﬁcity would force Thompson’s
    group V to be locally embeddable into ﬁnite groups, a contradiction.



                                        Contents
1. Introduction
2. An expander-matching criterion
3. The binary Leavitt conﬁguration
References




                                            78
                                            1. Introduction
   A countable group is soﬁc if every ﬁnite portion of its multiplication table can be approximated
by permutations of a ﬁnite set: multiplication must hold at almost every point, and every non-
identity element must move almost every point. Gromov introduced this approximation property
in his work on symbolic dynamics [Gro99]. Weiss introduced the term soﬁc group and anticipated
that nonsoﬁc groups should exist [Wei00, p. 351]; Pestov later highlighted the question of whether
every group is soﬁc [Pes08, Open Question 3.8].
   Let F2 be the ﬁeld with two elements. The noncommutative binary Leavitt algebra [Lea62] is
                   R = LF2 (1, 2) = F2 hs0 , s1 , t0 , t1 | ti sj = δij , s0 t0 + s1 t1 = 1i.      (1)
For example, t0 s0 = 1, whereas s0 t0 is a proper idempotent. Write R× for its group of invertible
elements: x ∈ R× means that some y ∈ R satisﬁes xy = yx = 1. Since R is ﬁnitely generated over
the ﬁnite ﬁeld F2 , both R and R× are countable.
Theorem 1.1. The unit group LF2 (1, 2)× is not soﬁc.

Related work
Earlier work gave several conditional routes to nonsoﬁc groups. Bowen and Burton showed that
ﬂexible permutation stability of PSLd (Z) for some d ≥ 5 would produce such a group [BB20].
Gohla and Thom showed that suitable central extensions of p-adic lattices would be nonsoﬁc
under a permutation-stability hypothesis; Chapman, Dikstein, and Lubotzky gave an algebraic and
combinatorial treatment of this implication [GT24, CDL24]. Theorem 1.1 requires no unproved
stability hypothesis.
   A related question in probability, posed by Aldous and Lyons, asked whether every unimod-
ular random rooted network is a local weak limit of ﬁnite networks [AL07, Question 10.1]. Its
aﬃrmative form became known as the Aldous–Lyons conjecture [BCLV24, Remark 1.7]. Be-
cause it concerned all unimodular networks, not only marked Cayley diagrams, a positive answer
would in particular have implied that every countable group is soﬁc; see also the discussion by
Hutchcroft [Hut26, pp. 6–7]. The conjecture was disproved in companion papers by Bowen, Chap-
man, Lubotzky, and Vidick and by Bowen, Chapman, and Vidick [BCLV24, BCV25]. Their
tour-de-force argument combines subgroup tests with a reﬁnement of the compression techniques
behind the breakthrough MIP∗ = RE of Ji, Natarajan, Vidick, Wright, and Yuen, which also
disproved Connes’s embedding conjecture [JNVWY20]. The second companion paper also gives
another proof that Connes’s embedding conjecture is false [BCV25]. To explain the relationship
with soﬁcity, let Fd be a free group of ﬁnite rank d ≥ 2. An invariant random subgroup of Fd
is a conjugation-invariant probability distribution on its subgroups. It is co-soﬁc if it is a weak
limit of the stabilizer distributions associated with uniformly chosen points of ﬁnite Fd -sets. The
Aldous–Lyons conjecture was equivalent to the assertion that, for every ﬁnite rank d ≥ 2, every
invariant random subgroup of Fd is co-soﬁc [Gel18, Section 6].
   The question of whether every countable group is soﬁc is precisely the restriction of this assertion
to invariant random subgroups concentrated on a single normal subgroup. Indeed, if N ◁ Fd and
δN denotes the point mass at N , then
             Fd /N is soﬁc    ⇐⇒       δN is a co-soﬁc invariant random subgroup of Fd ;
see [Gel18, Section 6, Proposition 6.1]. Every ﬁnitely generated group is a quotient of some Fd ,
and soﬁcity is detected on ﬁnitely generated subgroups. Consequently, every countable group is
soﬁc if and only if every such δN is co-soﬁc.
   Our proof constructs a ﬁnitely generated nonsoﬁc subgroup G ≤ R× . For any surjection Fd ↠ G,
its kernel N therefore gives a non-co-soﬁc point mass δN . Equivalently, the generator-marked
Cayley diagram of G is a deterministic unimodular network that is not a local weak limit of ﬁnite
networks with the same markings. This makes no assertion about the underlying unmarked Cayley
graph. In contrast, a general non-co-soﬁc invariant random subgroup need not be supported on a
normal subgroup and therefore need not produce a nonsoﬁc quotient.
   The original motivation for soﬁcity was Gottschalk’s surjunctivity conjecture. A group H is
surjunctive if, for every ﬁnite alphabet A, every injective H-equivariant continuous map AH → AH


                                                      79
is surjective. Gromov and Weiss proved that every soﬁc group is surjunctive [Gro99, Wei00].
Bowen and Chapman constructed a surjunctive non-co-soﬁc invariant random subgroup [BC25],
but their example is not concentrated on a normal subgroup and therefore does not produce
a surjunctive nonsoﬁc group. We do not know whether R× is surjunctive. A positive answer
would produce a surjunctive nonsoﬁc group, while a negative answer would disprove Gottschalk’s
conjecture. Since surjunctivity passes to subgroups [Wei00, Lemma 1.1], a positive answer would
also establish surjunctivity of the copy V ≤ R× constructed below.
    A group is hyperlinear if ﬁnite pieces of its multiplication table admit asymptotically faith-
ful models by ﬁnite-dimensional unitary matrices in normalized Hilbert–Schmidt distance. The
conjecture that every discrete group is hyperlinear, known as Connes’s embedding conjecture
for groups, remains a major open problem [Pes08, Open Question 3.9]: no nonhyperlinear dis-
crete group is known. For permutations σ, τ of n points, their permutation matrices satisfy
kPσ − Pτ k2,n
            2 = 2d (σ, τ ), where k · k
                    H                   2,n is the normalized Hilbert–Schmidt norm and dH is nor-
malized Hamming distance. Thus every soﬁc group is hyperlinear [Pes08, Theorem 3.3], but
Theorem 1.1 does not determine whether LF2 (1, 2)× is hyperlinear. Hyperlinearity is equiva-
lent to Connes embeddability of the group von Neumann algebra [Pes08, Theorem 8.5]. Al-
though MIP∗ = RE disproved Connes’s embedding conjecture for general von Neumann alge-
bras [JNVWY20], it does not produce a nonembeddable group von Neumann algebra.
    The corresponding approximation problem for the unnormalized Frobenius norm has a diﬀerent
answer. De Chiﬀre, Glebsky, Lubotzky, and Thom [DCGLT20] constructed central extensions of
arithmetic lattices that are not approximable by ﬁnite-dimensional unitaries in this norm. Be-
cause hyperlinearity uses the normalized Hilbert–Schmidt norm, their examples do not produce a
nonhyperlinear group.
    There are also conditional approaches to nonhyperlinear groups. Dogon showed that ﬂexible
Hilbert–Schmidt stability of certain property-(T ) groups would make nonsplit central extensions
nonhyperlinear; his examples include extensions of Sp2g (Z) with g ≥ 2 [Dog23]. Dogon and
Vigdorovich showed that if SL2 (Z[1/p]) is ﬂexibly Hilbert–Schmidt stable for some prime p, then
a ﬁnite central extension of that group is nonhyperlinear [DV26]. Both stability hypotheses remain
open.
    Two further conjectures remain open for arbitrary groups, but each is a theorem for soﬁc
groups. Lück’s determinant conjecture predicts that the modiﬁed Fuglede–Kadison determinant
of every matrix over Z[H] is at least one; Elek and Szabó proved this when H is soﬁc [ES05].
The algebraic eigenvalue conjecture predicts that every eigenvalue of such a matrix acting on
ℓ2 (H)n is an algebraic number. Jaikin-Zapirain proved this for soﬁc groups [Jai19, Corollary 1.5];
see also Thom [Tho08]. Neither conjecture is settled for R× . Manzoor constructed an invariant
random subgroup satisfying the determinant conjecture that is not co-hyperlinear [Man25], but
this does not determine the conjecture for R× . The Kervaire–Laudenbach conjecture asks whether
every one-variable equation with coeﬃcients in a group and nonzero total exponent of the variable
has a solution in some larger group. It holds for every hyperlinear group [NT22, Theorem 1.3].
Consequently, it would hold for R× if that group were hyperlinear, whereas its failure would exhibit
a nonhyperlinear group.
    Kaplansky’s direct-ﬁniteness conjecture asks whether ab = 1 in a group algebra always implies
ba = 1. The superﬁcially similar relation t0 s0 = 1 6= s0 t0 does not disprove this conjecture: neither
s0 nor t0 belongs to R× , so their relation holds in R, not in F2 [R× ]. For every group H, the rings
Z[H] and k[H] for ﬁelds k of characteristic zero are already stably ﬁnite [BFF24, Theorem 3.4 and
Corollary 3.5]. Thus only positive-characteristic ﬁelds remain open for R× . If R× were surjunctive,
then k[R× ] would be stably ﬁnite for every ﬁeld [BFF24, Corollary 3.25].

Binary self-similarity
The deﬁning relations of R can be written as rectangular-matrix identities:
                                                
                                             t0
                      S = s0 s1 ,        T =      ,      ST = 1,       T S = I2 .
                                               t1




                                                  80
Thus S : R2 → R and T : R → R2 are inverse right R-module maps, and
                             R=∼ R2      as right R-modules.
This is an isomorphism of modules, not of unital rings.
   The same relations connect the Leavitt algebra with Thompson’s group. The Cuntz algebra
O2 is generated by two isometries and their adjoints subject to the same formal relations as si , ti .
It is the universal C ∗ -completion of the complex Leavitt ∗-algebra LC (1, 2); our algebra R has
the same relations in characteristic two. Birget [Bir04, Corollary 7.4] and Nekrashevych [Nek04,
Proposition 9.5] independently embedded Thompson’s group V into the unitary group of O2 .
Birget’s construction is already algebraic: it embeds V into the unit group of the binary Leavitt
algebra over every ﬁeld [Bir04, Theorem 7.2]; see also [BS16, Section 2.2].
   For a ﬁnite binary word a, let [a] denote the cylinder consisting of inﬁnite binary strings begin-
ning with a. A complete preﬁx code is a ﬁnite set of pairwise preﬁx-incomparable words whose
cylinders partition all inﬁnite binary strings. Repeatedly splitting a cylinder into its two children
produces complete preﬁx codes with any prescribed number n ≥ 1 of words. After ordering its n
words, every such code E determines a unital ring isomorphism
                                                       ∼
                                        ΘE : Mn (R) −−→ R.                                        (2)
Write ELn (R) for the subgroup of GLn (R) generated by the elementary matrices In + rEij , where
i 6= j and r ∈ R. Its image
                                   ELE (R) := ΘE (ELn (R)) ≤ R×
is the same elementary group realized inside R× through the binary preﬁx decomposition. Since
R is a ﬁnitely generated ring, the Ershov–Jaikin-Zapirain theorem gives these elementary groups
property (T ) when n ≥ 3 [EJ10, Theorem 1.1]. For the speciﬁc nine-word code D constructed in
Equation (12), put
                                G := ELD (R) = ΘD (EL9 (R)) ≤ R× .
Hence G =  ∼ EL9 (R). The number nine is useful for the later preﬁx construction; the matrix
isomorphism (2) holds in every rank. Because soﬁcity passes to subgroups, it suﬃces to prove that
G is not soﬁc. In fact, the stronger identity G = R× is independently known [KT26, Corollary 4.4],
but the proof does not require it.

Proof overview
A family of ﬁnite graphs of uniformly bounded degree is an expander family if there exists γ > 0
such that, in every graph, each vertex set U containing at most half the vertices has at least γ|U |
edges to its complement. Given permutations modeling a ﬁnite generating set, their generator
graph joins each point of the model set to its image under each generator. Kazhdan’s property (T )
is a uniform spectral-gap condition on unitary representations. Kun’s theorem says that the gener-
ator graph of a soﬁc approximation to a property-(T ) group becomes a disjoint union of uniformly
expanding graphs after changing a proportion of edges that tends to zero along the approxima-
tion [Kun19, Theorem 1]. The expansion constant is uniform, but the number of components can
grow without bound: taking increasingly many disjoint copies preserves a soﬁc approximation.
The Kun–Thom obstruction requires a stronger hypothesis: if K has property (T ), J is ﬁnitely
generated, and a soﬁc approximation of K × J has a K-generator graph diﬀering negligibly from
a single uniform expander on the whole approximation set, then J is locally embeddable into ﬁnite
groups, or LEF [KT19, Theorem 1.1]. This means that every ﬁnite portion of the multiplication
table of J embeds exactly into a ﬁnite group.
   The single-expander hypothesis in the Kun–Thom theorem cannot be replaced by an arbitrary
union of expanders: a commuting group may move between components without being LEF. For
example, set
                       Λ = SL3 (Z),      B = BS(2, 3) = ha, b | ab2 a−1 = b3 i.
The group Λ has property (T ) and is residually ﬁnite, hence soﬁc. The group B is ﬁnitely presented
and soﬁc but not residually ﬁnite [Pes08, Example 4.6]; hence it is not LEF [VG97, Theorem 2.2].
Nevertheless, Λ×B is soﬁc [ES06, Theorem 1(1)]. Thus the expanding Λ-components alone cannot
force their commuting group B to be LEF.


                                                 81
  Proposition 2.3 bridges this gap even when the Γ-generator graph has many expanding compo-
nents. It is a general group-theoretic criterion; the Leavitt algebra enters later, when we construct
an example satisfying its hypotheses. Suppose that a subgroup Γ ≤ G has property (T ), and that
                        G = hΓ, t1 , . . . , tm i,     ti Γt−1
                                                            i ≤ Γ (1 ≤ i ≤ m).
Suppose further that a ﬁnitely generated subgroup J ≤ G satisﬁes
                           [Γ, J] = 1,          Γ ∩ J = {1},     t1 Jt−1
                                                                      1 ≤ Γ.
Thus Γ × J embeds in G, and the same conjugation moves both commuting factors inside Γ:
                              t1 (Γ × J)t−1        −1          −1
                                         1 = (t1 Γt1 ) × (t1 Jt1 ) ≤ Γ.
This additional nesting is absent from the direct-product example above. Under these assumptions,
Proposition 2.3 proves that an expanding soﬁc approximation of G would force J to be LEF.
   To prove this implication, begin with a soﬁc approximation on a ﬁnite set Y whose G-generator
graph diﬀers negligibly from one expander. Apply Kun’s theorem to its restriction to Γ. After
negligible edge changes, Y splits into expanding Γ-components. For each i, let pi be the per-
mutation approximating ti . Since ti Γt−1 i   ≤ Γ, expansion implies that, apart from components
containing o(|Y |) vertices altogether, each transported component pi (C) lies almost entirely inside
some Γ-component D. Diﬀerent transported components may, however, initially select the same
D.
   For z ∈ Y , let C(z) be its Γ-component and deﬁne M (z) = |C(z)|. Let µ be a median of these
values over all of Y , and deﬁne
                                                     M (z)
                                          f (z) =            .
                                                   M (z) + µ
The inclusions ti Γt−1
                     i   ≤ Γ imply that f is almost nondecreasing along each pi , while the Γ-
generators almost preserve f . Since every generator acts by a permutation, the total increase
of f equals its total decrease. Thus f varies negligibly along these generators, and hence along
any ﬁxed generating set of G. Expansion of the ambient G-model therefore forces f to remain
close to its median 1/2 outside o(|Y |) vertices. It follows that a transported component pi (C) and
its target D have approximately the same size. Since pi (C) already lies almost entirely in D, it
occupies more than half of D. Distinct transported components are disjoint and therefore cannot
select the same target.
   For i = 1, this injective matching makes every ﬁxed Γ-word preserve the transported compo-
nents p1 (C) at almost every vertex. Since t1 Jt−1                                              −1
                                                  1 ≤ Γ, each J-generator is the conjugate by t1 of
an element of Γ. Conjugating the component-preservation statement by p−1      1 therefore shows that
the J-generators preserve the original Γ-components at almost every vertex. The Γ-generators
already preserve these components. We can consequently select one original expanding compo-
nent on which the required multiplication, commutation, and distinctness tests all hold outside
a negligible set. Restrict the Γ- and J-generator actions to that component and complete their
partial permutations. The resulting Γ-generator graph diﬀers negligibly from one expander, so
the Kun–Thom theorem implies that J is LEF.
   It remains to realize the hypotheses of Proposition 2.3 inside the concrete group G = ELD (R).
In Section 3, we verify that G has property (T ), construct a property-(T ) subgroup Γ ≤ G, two
units u, v ∈ G, and a subgroup J ≤ G, and prove that
                                G = hΓ, u, vi,         uΓu−1 , vΓv −1 ≤ Γ,
                              Γ × J ≤ G,             uJu−1 ≤ Γ,     J=∼ V.
Here Γ is supported on the [0]-corner of R, whereas J =   ∼ V acts by preﬁx replacements inside
the disjoint cylinder [1000]. Conjugation by u moves J into [0001] ⊆ [0]. Thompson’s group V is
ﬁnitely presented, inﬁnite, and simple [CFP96], so it is not LEF [VG97, Theorem 2.2]. If G were
soﬁc, its property (T ) would provide an expanding soﬁc approximation. Applying Proposition 2.3
with t1 = u and t2 = v would nevertheless force J to be LEF. This contradiction proves that G,
and hence R× , is not soﬁc.




                                                       82
                              2. An expander-matching criterion
   We ﬁrst isolate the part of the proof that does not depend on the binary Leavitt algebra. Its
purpose is to turn a soﬁc approximation whose Γ-generator graph has many expanding components
into an approximation of Γ × J on one expanding Γ-component.
   For a nonempty ﬁnite set Y , write
                                    |{z ∈ Y : pz 6= qz}|
                        dH (p, q) =                      (p, q ∈ Sym(Y )).
                                            |Y |
A soﬁc approximation of a countable group H consists of maps pn : H → Sym(Yn ) satisfying
                                                                           
          pn (1) = 1,     dH pn (gh), pn (g)pn (h) −→ 0,        dH pn (g), 1 −→ 1 (g 6= 1).
Here the multiplication condition holds for every g, h ∈ H. By taking disjoint copies, we may
assume that |Yn | → ∞.
   A group J is locally embeddable into ﬁnite groups, or LEF, if, for every ﬁnite F ⊆ J, there are
a ﬁnite group B and an injection ϕ : F → B such that
                                 ϕ(xy) = ϕ(x)ϕ(y)        (x, y, xy ∈ F ).
Thus the multiplication table of F embeds exactly, although the ﬁnite group B may depend on
F.
   For a graph L and U ⊆ V (L), let ∂L U be the set of edges joining U to V (L) \ U . If C is a
connected component of L, we also write ∂C U for the boundary of U ⊆ C in the induced graph on
C. Parallel edges are counted with multiplicity, while loops contribute nothing. Edge symmetric
diﬀerences are likewise counted with multiplicity. We call C a γ-expander if
                              |∂C U | ≥ γ min{|U |, |C \ U |}    (U ⊆ C).                             (3)
  Throughout this section, a ﬁnite symmetric generating set S = S −1 ⊆ H includes the identity.
Normalize inverse labels to be inverse permutations, with the identity label acting exactly as
the identity. The corresponding S-labelled generator graph has vertex set Yn and an arc from
z to pn (s)z for every s ∈ S. Pair inverse arcs to obtain an undirected multigraph; ﬁxed points,
including the identity label, give loops. Parallel edges retain their multiplicities. All such graphs
have uniformly bounded degree. Adding identity loops does not change their edge boundaries, but
gives the associated random walk a uniformly positive holding probability, as in Kun’s property-(T )
argument.
   The two external inputs diﬀer in a crucial respect: Kun’s theorem produces possibly many
expanders; the Kun–Thom theorem requires one expander, up to negligible edge changes, on the
entire approximation set.
Theorem 2.1 (Kun’s expander decomposition). Let H be an inﬁnite group with property (T ),
let S = S −1 ⊆ H be a ﬁnite generating set containing 1, and let pn : H → Sym(Yn ) be a soﬁc
approximation with |Yn | → ∞. Write Xn for its S-generator multigraph. There are a constant
γ > 0 and unlabelled, uniformly bounded-degree multigraphs Ln on the same vertex sets such that
                                      |E(Xn )4E(Ln )| = o(|Yn |)
and every connected component of Ln is a γ-expander.
   This is the expander-decomposition conclusion of [Kun19, Theorem 1], stated with the identity-
inclusive generator and multigraph conventions used in its property-(T ) argument. If a graph
convention suppresses identity loops, adjoin the same identity loop at every vertex of both graphs;
this changes neither their boundaries nor their edge symmetric diﬀerence. The reference graphs
are unlabelled: their edges need not retain the original generator labels.
   In fact, the weaker conclusion stated above avoids the regularity-preserving rewiring in the im-
plication (3) ⇒ (4) of [Kun19, Theorem 3].1 Condition (2) is supplied by [Kun19, Proposition 11],
  1Condition (1) there should use the lazy Markov operator (I + M )/2, where M is the original random-walk
operator. We use only (2) ⇒ (3), and hence neither condition (1) nor (4) ⇒ (1).




                                                   83
whose proof uses [Kun19, Lemma 10].2 In deriving condition (3) from condition (2), choose each
sparse residual set with minimum cardinality and count crossing edges twice in the boundary
estimate. Condition (3) then provides a constant η > 0 and, after choosing the error parameter
to decrease suﬃciently slowly, partitions
                                      Yn = Pn,0 t Pn,1 t · · · t Pn,kn
such that
                                                      X
                                                      kn
                              |Pn,0 | = o(|Yn |),           |∂Xn Pn,i | = o(|Yn |),
                                                      i=1
and                                                                                   
                     |∂Xn U | ≥ η|U |     1 ≤ i ≤ kn , U ⊆ Pn,i , |U | ≤ |Pn,i |/2 .
For each P = Pn,i , start with C = P and repeatedly remove any nonempty U ⊆ C satisfying
                                                                    η
                              |U | ≤ |C|/2,     |EXn (U, C \ U )| < |U |.
                                                                    4
Set b(C) = |∂Xn C|, and write
                            q = |EXn (U, C \ U )|,          r = |EXn (U, Yn \ C)|.
Since U ⊆ P and |U | ≤ |P |/2, the partition property gives q + r ≥ η|U |. Hence
                                                                 η
                                b(C \ U ) = b(C) − r + q ≤ b(C) − |U |.
                                                                 2
At most 2|∂Xn P |/η vertices are therefore removed from P . The remaining induced graph is an
η/4-expander; make each removed vertex and each vertex of Pn,0 a singleton component, retaining
its original loops. Since the degrees are uniformly bounded, the total number of deleted edges is
o(|Yn |). This gives the claimed decomposition without invoking condition (4).
   The theorem also lets us choose an approximation with just one reference expander. Indeed,
start with an arbitrary soﬁc approximation of an inﬁnite property-(T ) group H, ﬁx a ﬁnite sym-
metric generating set S, and normalize inverse labels to inverse permutations. Make involutive
labels exact by replacing their cycles of length greater than two with ﬁxed points. Approximate
multiplicativity shows that these changes aﬀect only o(|Yn |) vertices. Now write Ln for Kun’s
disjoint union of expanders, and let Dn consist of vertices incident to an edited edge. For each ℓ,
let Wℓ be the formal S-words of length at most ℓ, including the empty word, and let Fn,ℓ contain
all failures of equality or distinctness between these words. Deﬁne
                                                        [
                                       Bn,ℓ = Fn,ℓ ∪           p−1
                                                                w (Dn ).
                                                       w∈Wℓ

For ﬁxed ℓ, this set has size o(|Yn |). Choose ℓn → ∞ slowly enough that Bn = Bn,ℓn still has size
o(|Yn |). Averaging over the components of Ln gives one component An such that
                                     |An ∩ Bn |    |Bn |
                                                ≤        −→ 0.
                                        |An |      |Yn |
Every word of length at most ℓn starting at an unmarked vertex of An stays inside An : any exiting
generator edge is an edited edge. Restrict each generator permutation to its internal arcs in An ,
and complete the resulting partial bijection to a permutation. Use inverse completions for inverse
labels and ﬁxed points for involutive labels. Only o(|An |) values change, so all ﬁxed equality and
distinctness tests survive. Choosing a representative word for each h ∈ H therefore deﬁnes a soﬁc
approximation of H on An . The injectivity tests on growing word balls imply |An | → ∞, and the
resulting generator graph diﬀers from the single expander Ln [An ] in o(|An |) edges.
   2
    The ultraproduct argument used in the proof of Lemma 10 therein can fail when the normalized Markov defect
tends to zero. For D = k(I − M )1T k2 > 0, the rescaled displacement cocycles g 7→ (g1T − 1T )/D remain bounded
on generators and therefore admit an aﬃne-cocycle limit. Its symmetric generator average has norm one and is
orthogonal to invariant vectors, allowing property (T ) to recover the required contraction. The case D = 0 is
immediate.




                                                      84
Theorem 2.2 (Kun–Thom’s expander-centralizer theorem). Let K be an inﬁnite group with
property (T ), let J be a ﬁnitely generated group, and ﬁx a ﬁnite symmetric generating set SK ⊆ K
containing 1. Suppose that K × J has a soﬁc approximation pn : K × J → Sym(Yn ). Write XK,n
for its SK -generator multigraph. Suppose there are uniformly bounded-degree multigraphs Ln on
Yn and a constant λ > 0 such that
           |E(XK,n )4E(Ln )| = o(|Yn |),        |∂Ln U | ≥ λ min{|U |, |Yn \ U |}    (U ⊆ Yn )
for every n. Then J is LEF.
   The exact-expander case is [KT19, Theorem 1.1]; see also its Remark 1.2. The stated version
follows by inserting the missing expander edges into ﬁnitely many additional K-generator permu-
tations. Indeed, ignore loops and let D uniformly bound the degrees of Ln . Partition its edges
missing from XK,n into at most r = 2D − 1 matchings, allowing empty matchings. Fix elements
h1 , . . . , hr ∈ K \ SK in distinct inverse classes. For the jth matching, alter pn (hj ) on O(1) vertices
per matched edge so that its generator graph contains that matching. Complete inverse labels
compatibly. If hj is an involution, ﬁrst normalize pn (hj ) to an involution and insert the matching
as disjoint transpositions, repairing its displaced partners. Since there are only o(|Yn |) missing
edges, these modiﬁcations preserve the soﬁc approximation. The generator graph for the enlarged
generating set contains every nonloop edge of Ln , with its multiplicity. Its edge boundaries there-
fore dominate those of Ln , so it is an actual λ-expander. The original Kun–Thom theorem now
applies. All boundary counts include repeated edges with multiplicity.
Proposition 2.3. Let Γ ≤ G be inﬁnite groups, and suppose that Γ has property (T ). Assume
that
                  G = hΓ, t1 , . . . , tm i, ti Γt−1
                                                  i ≤ Γ (1 ≤ i ≤ m), m ≥ 1.
Suppose further that a ﬁnitely generated subgroup J ≤ G satisﬁes
                            [Γ, J] = 1,      Γ ∩ J = {1},        t1 Jt−1
                                                                      1 ≤ Γ.
If G admits a soﬁc approximation pn : G → Sym(Yn ) whose generator graphs for some ﬁnite
symmetric generating set diﬀer in o(|Yn |) edges from graphs on Yn with uniformly bounded degrees
and a uniform positive expansion constant, then J is LEF.
  Property (T ) is required only of Γ. In our application, property (T ) for G serves only to obtain
the expanding approximation assumed in the proposition.
Proof. Choose a ﬁnite symmetric generating set SΓ ⊆ Γ containing 1. Adjoin the distinct noniden-
tity elements among t±1i  to obtain a symmetric generating set SG for G. For every inverse pair
added in this way, choose one of the original ti as its positive representative. Thus each positive
nonidentity G-generator either belongs to Γ or is one of the given compressing elements.
   By hypothesis, there are a ﬁnite symmetric generating set S0 of G, a soﬁc approximation
pn : G → Sym(Yn ), and uniformly bounded-degree γG -expanders LG such that the S0 -generator
graph diﬀers from LG in o(|Yn |) edges. Add 1 to S0 , and add the corresponding identity loops to
LG , if necessary. Here γG > 0 does not depend on n, and
                                            N = |Yn | −→ ∞.
Normalize inverse and involutive labels in SG ∪ S0 as in the construction above; the o(N ) changes
preserve the expander approximation. All o(N ) estimates refer to this same approximation. For
readability, write pg = pn (g) and suppress n from the graphs and component partitions.
  The hypotheses identify ΓJ with Γ × J and imply t1 (ΓJ)t−1    1 ≤ Γ. Our goal is to extract a
soﬁc approximation of Γ × J whose Γ-generator graph diﬀers negligibly from one expander. We
ﬁrst restrict the G-approximation to Γ, decompose it into expanding components, and use the
ambient G-expander to match those components with their translates. We then show that J
almost preserves the components, select one of them, and repair the restricted generator actions.

Step 1: Locate a dominant original component inside each transported component.
  Apply Theorem 2.1 to the restricted soﬁc approximation of Γ, using SΓ . It gives a graph LΓ
diﬀering from the SΓ -generator graph in o(N ) edges whose connected components are γΓ -expanders


                                                    85
for some γΓ > 0. Write Q for these original components. Since LΓ has no edges between original
components, an SΓ -generator crosses between them on only o(N ) vertices. If w = s1 · · · sr is a
ﬁxed Γ-word, write pw = ps1 · · · psr . The same crossing estimate then holds for pw .
   Set τi = pti . Transport the vertices and edges of LΓ through τi , obtaining
                                Ii = τi LΓ ,        Pi = {τi C : C ∈ Q}.
Each member of Pi is a γΓ -expanding connected component of Ii . Apart from o(N ) edited edges,
the edges of Ii follow the permutations τi ps τi−1 , s ∈ SΓ . Approximate multiplicativity identiﬁes
each such permutation, outside o(N ) vertices, with a ﬁxed Γ-word representing ti st−1
                                                                                    i . Since these
words almost preserve the original components, we obtain
              #{Ii -edges joining diﬀerent members of Q} = o(N )                (1 ≤ i ≤ m).     (4)
  For P ∈ Pi , choose Q(P ) ∈ Q maximizing |P ∩ Q(P )|, and deﬁne its unmatched mass by
                                     L(P ) = |P | − |P ∩ Q(P )|.
Partition P into the sets P ∩ Q, Q ∈ Q. If the largest part has more than half the vertices, apply
expansion to all other parts, whose total size is L(P ). Otherwise, every part has at most half the
vertices, so apply expansion to all of them. Each edge between diﬀerent parts is counted at most
twice, giving
                    γΓ L(P ) ≤ 2#{Ii [P ]-edges joining diﬀerent members of Q}.
                              P
Together with (4), this gives P ∈Pi L(P ) = o(N ). Choose ηn ↓ 0 suﬃciently slowly that, simulta-
neously for every i,                       X
                                                   |P | = o(N ).                                (5)
                                           P ∈Pi
                                        L(P )>ηn |P |
For each i, all but o(N ) vertices belong to components of Pi whose unmatched mass is at most ηn
times their size. It remains to rule out several transported components selecting the same original
component.

Step 2: Use a bounded median normalization to compare component sizes.
   For each vertex z, let C(z) ∈ Q be its original component and set
                                               M (z) = |C(z)|.
Suppose that P = τi C satisﬁes L(P ) ≤ ηn |P |. For every z ∈ C with τi z ∈ P ∩ Q(P ),
                         M (τi z) = |Q(P )| ≥ (1 − ηn )|P | = (1 − ηn )M (z).
By (5), the discarded components and the unmatched portions of the remaining components
occupy o(N ) vertices. Consequently,
                 M (τi z) ≥ (1 − ηn )M (z)      outside o(N ) vertices        (1 ≤ i ≤ m).       (6)
For each s ∈ SΓ , we likewise have M (ps z) = M (z) outside o(N ) vertices.
  The values of M need not be uniformly bounded, so these exceptional sets cannot control its
total variation. Let µ > 0 be a median of the vertex-indexed multiset
                                                               
                                               M (z) : z ∈ Yn .
Thus at least half of these values are at most µ, and at least half are at least µ. In particular, an
original component C contributes |C| copies of |C|. Deﬁne
                                                M (z)
                                  f (z) =                ,         z ∈ Yn .
                                               M (z) + µ
Then 0 < f < 1, 1/2 is a median of f , and f is constant on each original component.
  For s ∈ SΓ , preservation of the original components gives f (ps z) = f (z) outside o(N ) vertices.
For a positive compressing generator ti , use (6) and
                         (1 − η)x      x
                                    ≥     −η                 (x, a > 0, 0 ≤ η < 1).
                       (1 − η)x + a   x+a




                                                        86
Thus every positive SG -generator s satisﬁes
                                 f (ps z) ≥ f (z) − ηn       outside o(N ) vertices.
Because ps is a permutation,                  X                       
                                                     f (ps z) − f (z) = 0.
                                             z∈Yn
The total decrease of f is at most ηn N + o(N ) = o(N ): the inequality above controls the nonex-
ceptional vertices, and 0 < f < 1 controls the exceptional ones. Since the displayed sum is zero,
the total increase equals the total decrease. Hence
                                            X
                                                  |f (ps z) − f (z)| = o(N ).
                                           z∈Yn
The same estimate holds for inverse generators. For each r ∈ S0 , choose a ﬁxed SG -word wr =
s1 · · · sk representing r. Approximate multiplicativity, the bound 0 < f < 1, and a telescoping
sum give
                  X                               X
                                                  k X
                           |f (pr z) − f (z)| ≤              |f (psj z) − f (z)| + o(N ) = o(N ).
                 z∈Yn                             j=1 z∈Yn
Summing over S0 , and noting that changing one edge aﬀects the total variation by at most one,
therefore gives                   X
                                         |f (z) − f (w)| = o(N ).                          (7)
                                        {z,w}∈E(LG )
  Expansion of the single graph LG now forces f to concentrate near its median 1/2. The ﬁnite
coarea identity says that
                      Z 1                                                 X
                            ∂LG {z ∈ Yn : f (z) > t} dt =                         |f (z) − f (w)|.
                       0
                                                                   {z,w}∈E(LG )

Indeed, an edge {z, w} crosses the displayed level set precisely for levels between f (z) and f (w).
For 0 < t < 1/2, the set {z ∈ Yn : f (z) ≤ t} contains at most N/2 vertices; for 1/2 < t < 1,
the same holds for {z ∈ Yn : f (z) > t}. Apply (3) to these sublevel and superlevel sets, use that
complementary sets have the same boundary, and split the coarea integral at 1/2. This yields
                                    X                             X
                               γG          f (z) − 12 ≤                   |f (z) − f (w)|.
                                    z∈Yn                   {z,w}∈E(LG )

Therefore (7) gives
                                              X
                                                     f (z) − 12 = o(N ).
                                              z∈Yn
Choose δn ↓ 0 suﬃciently slowly that
                                    n                        o
                           En = z : f (z) − 21 > δn                satisﬁes    |En | = o(N ).
Since
                                                                f (z)
                                                  M (z) = µ             ,
                                                              1 − f (z)
any z, w ∈ Yn \ En satisfy
                                                                                 
                                M (w)                   1 + 2δn 2
                              ρ−1
                               n ≤      ≤ ρn ,   ρn =              −→ 1.                     (8)
                                 M (z)                  1 − 2δn
Since f is constant on every original component, En is a union of such components. All remaining
original components have sizes diﬀering by a factor tending uniformly to one.

Step 3: Match the ﬁrst transported partition almost bijectively.
  All ti were needed to control the full G-generator graph. To show that J preserves the original
components, however, we need only the ﬁrst transport. Set
                                                τ = τ1 ,          P = P1 .



                                                             87
Retain a component P = τ C ∈ P precisely when
                       L(P ) ≤ ηn |P |,      C ∩ En = ∅,       Q(P ) ∩ En = ∅.
Components failing the ﬁrst condition contain o(N ) vertices by (5). The transported components
whose sources lie in En contain |En | = o(N ) vertices. Finally, if the ﬁrst condition holds but
Q(P ) ⊆ En , then
                                   |P ∩ Q(P )| ≥ (1 − ηn )|P |.
The intersections P ∩ Q(P ) are disjoint as P varies, and these particular intersections all lie in
En . Hence the corresponding components have total size at most |En |/(1 − ηn ) = o(N ). Thus all
nonretained components together contain o(N ) vertices.
  For a retained component P = τ C, both C and Q(P ) lie outside En , and
                  M (z) = |C| = |P | (z ∈ C),          M (w) = |Q(P )| (w ∈ Q(P )).
The size comparison (8) gives
                                       ρ−1
                                        n |P | ≤ |Q(P )| ≤ ρn |P |.
Since at most ηn |P | vertices of P lie outside Q(P ), it follows that
                              |P 4Q(P )| ≤ (ρn − 1 + 2ηn )|P | = o(|P |).
In particular, for all suﬃciently large n,
                                                     1
                                      |P ∩ Q(P )| > |Q(P )|.
                                                     2
Distinct transported components are disjoint, so they cannot both occupy a strict majority of
the same original component. Therefore P 7→ Q(P ) is injective on retained components. The
nonretained components and unmatched portions of retained components together contain o(N )
vertices, so the matched intersections cover N − o(N ) vertices.
   Fix a Γ-word w. Discard vertices outside the matched intersections, vertices whose pw -images lie
outside those intersections, and vertices for which pw crosses between original components. Each
discarded set has size o(N ). For every remaining vertex z, the vertices z and pw z lie in matched
intersections belonging to the same original component. Injectivity of the matching therefore puts
them in the same transported component. Thus
                      #{z : z and pw z lie in diﬀerent members of P} = o(N ).                   (9)
For each j ∈ J, choose a ﬁxed Γ-word wj representing t1 jt−1
                                                          1 , and put
                                              −1
                                        qj = τ pwj τ.
Approximate multiplicativity shows that qj agrees with pj outside o(N ) vertices. Moreover, τ qj z =
pwj τ z, and the transported component containing τ z is τ C(z). Hence z and qj z belong to the
same original component exactly when τ z and pwj τ z belong to the same transported component.
Applying (9) to wj therefore gives
                                   #{z : C(qj z) 6= C(z)} = o(N ).                             (10)
Thus, for every ﬁxed generator of either Γ or J, its approximating permutation preserves the
original-component partition outside o(N ) vertices. It remains to select one original component
and turn the restricted actions into an approximation of Γ × J whose Γ-generator graph diﬀers
negligibly from an expander.

Step 4: Select one component carrying all required word tests.
   Choose ﬁnite symmetric generating sets
                           TΓ = SΓ ,      TJ ⊆ J \ {1},       T = TΓ ∪ TJ .
Thus 1 ∈ TΓ ⊆ T ; its generator permutation is the identity. The set TJ may be empty when J is
trivial. For s ∈ TΓ , deﬁne
                                             qs = p s .
For j ∈ TJ , use the permutation qj constructed in Step 3. Normalize inverse labels and make
involutive J-labels exact by replacing all cycles of length greater than two with ﬁxed points.
These changes aﬀect o(N ) vertices and can alter any ﬁxed word test at only o(N ) starting vertices.

                                                  88
Since [Γ, J] = 1 and Γ ∩ J = {1}, multiplication identiﬁes Γ × J with its subgroup of G, and the
permutations qt satisfy its ﬁxed equality and distinctness tests outside o(N ) vertices.
  For z ∈ Yn , recall that C(z) is its original component. Deﬁne the set of generator exits by
                             Cn = {z : C(qt z) 6= C(z) for some t ∈ T }.
Every Γ-generator preserves the original components outside o(N ) vertices, while (10) applies to
every J-generator. Hence |Cn | = o(N ). Let ∆n consist of vertices incident to the edge-multiset
diﬀerence between the Γ-generator graph and LΓ . Then |∆n | = o(N ).
   For ℓ ≥ 0, let Wℓ be the ﬁnite set of formal words in the alphabet T of length at most ℓ, including
the empty word. Diﬀerent formal words may represent the same group element. For w ∈ Wℓ , write
qw for the corresponding product of permutations and w ∈ Γ×J for the represented group element.
Words representing the same element should have the same endpoint, whereas words representing
distinct elements should have distinct endpoints. The vertices where either requirement fails form
                                              [
                                 Fn,ℓ =              {z : qw z 6= qw0 z}
                                          w,w0 ∈Wℓ
                                           w=w0
                                                [
                                          ∪              {z : qw z = qw0 z}.
                                              w,w0 ∈Wℓ
                                               w6=w0
For ℓ ≥ 1, collect all exceptional vertices in the explicitly deﬁned set
                                                             [
                                                                     −1
                                Bn,ℓ = ∆n ∪ Fn,ℓ ∪                  qw  (Cn ).
                                                           w∈Wℓ−1

The last term records word paths for which some generator step crosses between original compo-
nents. For each ﬁxed ℓ, we have |Bn,ℓ | = o(N ). Choose ℓn → ∞ suﬃciently slowly that
                                   |Bn,ℓn |
                                en =        −→ 0,    Bn = Bn,ℓn .
                                     N
  Averaging over all original components with weights |Q| yields a component Qn ∈ Q satisfying
                                          |Qn ∩ Bn | ≤ en |Qn |                                  (11)
for every n. For each element of the word-metric ball in Γ, with generating set TΓ and radius
bℓn /2c, choose a formal word of that length or shorter representing it. At any z ∈ Qn \ Bn , the
exit tests keep every such word path inside Qn , and the distinctness tests give diﬀerent endpoints
for diﬀerent elements. Evaluating the chosen words at z therefore injects the entire word-metric
ball into Qn . Since Γ is inﬁnite, we have
                                               |Qn | −→ ∞.

Step 5: Complete the restricted generator actions.
   Set P = Qn , now an original component rather than a transported component. For one repre-
sentative of every nonidentity inverse pair in T , restrict qt to its internal arcs:
                          At = {z ∈ P : qt z ∈ P },            qt : At −→ qt (At ).
The omitted sets P \ At and P \ qt (At ) have the same cardinality. Choose a bijection between
them to extend this partial bijection to a permutation qbt ∈ Sym(P ). For an involution, the missing
domain equals the missing range, and we complete it by ﬁxed points. Use qbt−1 for the inverse label
and qb1 = idP for the identity label. Because
                                    P \ At ⊆ Cn ∩ P ⊆ Bn ∩ P,
(11) shows that only O(en |P |) values are changed. Every word path of length at most ℓn starting
in P \ Bn remains in P , so its equality, commutation, and distinctness tests are preserved. To
obtain maps on the whole group, choose once and for all a formal representative word wg for every
g ∈ Γ × J, with w1 empty and wt = t for every nonidentity t ∈ T , and set
                                       pbn (g) = qbwg ∈ Sym(Qn ).




                                                      89
For ﬁxed g, h, the equality tests compare wgh with the concatenation wg wh , and the distinctness
tests compare wg with the empty word when g 6= 1. Since ℓn → ∞, these tests eventually apply,
and their exceptional proportions tend to zero. Therefore pbn is a soﬁc approximation of Γ × J on
Qn .
   Let I0 be the TΓ -generator multigraph of pbn . Since ∆n ∪ Cn ⊆ Bn ,
                                  |E(I0 )4E(LΓ [P ])| = O|SΓ | (en |P |).
Here LΓ [P ] is precisely the original γΓ -expanding component on P . Since en → 0, Theorem 2.2
applied to this approximation implies that J is LEF.                                         □

                            3. The binary Leavitt configuration
  We apply Proposition 2.3 inside the unit group of the noncommutative binary Leavitt algebra
R from (1). Its binary preﬁx structure supplies the contracting conjugations and the commuting
copy of Thompson’s group, while the Ershov–Jaikin-Zapirain theorem supplies property (T ) for
the elementary groups used in the construction. We construct these groups and then verify the
hypotheses of Proposition 2.3.
3.1. Preﬁx codes and elementary groups. Let W be the F2 -vector space with one basis vector
eω for every inﬁnite binary string ω ∈ {0, 1}N . The formulas
                                      si eω = eiω ,        ti ejω = δij eω
satisfy the deﬁning relations of R. Thus si preﬁxes a string by i, whereas ti deletes that preﬁx
when present and otherwise gives zero. The operators sk0 are distinct, so R is inﬁnite.
   For a ﬁnite binary word a = i1 · · · ir , set
                         sa = si1 · · · sir ,    t a = ti r · · · ti 1 ,    ea = sa ta .
For the empty word, both products are 1. The cylinder [a] consists of the inﬁnite binary strings
beginning with a. A preﬁx code E = (a1 , . . . , aq ) is a list of words none of which is a preﬁx
                                                                                               P
                                                                                                   of
another. It is complete if the cylinders [ai ] partition all inﬁnite binary strings. Write eE = i eai .
The preﬁx-code identities
                            tai saj = δij ,      (sai taj )(sak tal ) = δjk sai tal
follow from the incomparability of its words. Moreover, the Leavitt relation gives
                                  ea = sa (s0 t0 + s1 t1 )ta = ea0 + ea1 .
Every ﬁnite complete preﬁx code is obtained from the one-word code consisting of the empty word
by repeatedly replacing a word a with its children a0, a1. The displayed identity therefore shows
that eE = 1 whenever E is complete. The preﬁx-code identities also give a ring isomorphism
                                         ∼                                  X
                        ΘE : Mq (R) −−→ eE ReE ,               (rij ) 7−→         sai rij taj .
                                                                            i,j

Its inverse sends x ∈ eE ReE to (tai xsaj )i,j . If E is complete, this identiﬁes Mq (R) with R.
Otherwise, a unit h in the corner extends to a unit of R as h + 1 − eE , acting identically outside
the cylinders in E.
   In particular, deﬁne the elementary preﬁx group
                           ELE (R) = 1 + sai r taj : i 6= j, r ∈ R ≤ R× .
Indeed, the corner-unit extension satisﬁes
                        (1 − eE ) + ΘE (Iq + rEij ) = 1 + sai r taj                (i 6= j),
so ELE (R) is the copy of ELq (R) acting identically outside the cylinders of E. We call its displayed
generators elementary E-roots.




                                                      90
  Take the three preﬁx blocks
                                α = (000, 001, 01),
                                β = (1000, 1001, 101),
                                                                                                 (12)
                                ν = (1100, 1101, 111),
                                D = (α1 , α2 , α3 , β1 , β2 , β3 , ν1 , ν2 , ν3 ).
Their cylinders partition [0], [10], and [11], respectively. Therefore D is a complete nine-leaf code,
whereas α covers only [0]. Set
                       G = ELD (R) =   ∼ EL9 (R),      Γ = ELα (R) =∼ EL3 (R).
Since eα = e0 , these identiﬁcations give
                                                             
             Γ = 1 − e0 + Θα (A) : A ∈ EL3 (R) = ΘD (diag(A, I6 )) : A ∈ EL3 (R) .
Thus Γ consists of elementary units, not necessarily preﬁx replacements, and acts as the identity
on the six complementary summands. Every elementary α-root is also a D-root. Consequently,
                                                Γ ≤ G ≤ R× .
Both groups are inﬁnite: for distinct code leaves, the map
                                             r 7−→ 1 + sai r taj
embeds the inﬁnite additive group of R into their corresponding elementary root subgroup.
  Since R is ﬁnitely generated as a ring, both G =∼ EL9 (R) and Γ =∼ EL3 (R) have property (T )
by the Ershov–Jaikin-Zapirain theorem [EJ10, Theorem 1.1].
3.2. Copies of Thompson’s group. To deﬁne Thompson’s group V [CFP96], take two complete
preﬁx codes
                               E = (a1 , . . . , aq ), E 0 = (b1 , . . . , bq ),
together with a bijection ai 7→ bi . Every inﬁnite binary string has a unique expression ai ω, where
ai ∈ E and ω is its remaining inﬁnite tail. The corresponding preﬁx replacement acts by
                                                g(ai ω) = bi ω.
Thus it replaces the initial word ai by bi and leaves the inﬁnite tail unchanged. Since E 0 is also
complete, this map is a bijection; its inverse replaces each bi by ai . Thompson’s group V consists
of all such preﬁx replacements.
   For example, the complete codes
                                E = (0, 10, 11),             E 0 = (10, 0, 11)
give the replacement
                        g(0ω) = 10ω,           g(10ω) = 0ω,              g(11ω) = 11ω.
It exchanges the cylinders [0] and [10] while ﬁxing [11].
   We next realize V inside G, together with smaller copies inside Γ. Birget’s algebraic realization
of V [Bir04, Theorem 7.2], described also in [BS16, Section 2.2], associates to a preﬁx-replacement
table g : E → E 0 the elements
                                     X                                X
                             Ug =          sg(a) ta ,        Ug−1 =         sa tg(a) .
                                     a∈E                              a∈E
Because both codes are complete, the preﬁx-code identities give
                                         Ug Ug−1 = Ug−1 Ug = 1.
To see that this construction depends only on the represented preﬁx replacement, observe that
                                           sb ta = sb0 ta0 + sb1 ta1 .
Thus replacing one table entry a 7→ b by the two entries a0 7→ b0 and a1 7→ b1 does not change Ug .
Any two tables representing the same preﬁx replacement have a common reﬁnement. Likewise,




                                                        91
given two replacements g and h, reﬁne the range code of g and the domain code of h until they
agree. The preﬁx-code identities then give
                                       Uh Ug = Uh◦g ,            Uid = 1.
Hence g 7→ Ug is a well-deﬁned homomorphism. Moreover, Ug sends eaω to eg(a)ω . Distinct preﬁx
replacements act diﬀerently on some basis vector, so their units are distinct. We therefore obtain a
                                                     ∼ V for the copy acting by preﬁx replacements
faithful copy V ≤ R× . For a binary word l, write Vl =
inside [l] and ﬁxing its complement. Its tables can be chosen to leave every complementary cylinder
unchanged, so
                                     g − 1 ∈ el Rel     (g ∈ Vl ).                              (13)
Lemma 3.1. We have V ≤ G. If l extends one of the three words αi , then Vl ≤ Γ.
Proof. For incomparable words ρ, σ, the unit
                                    τρ,σ = 1 + eρ + eσ + sρ tσ + sσ tρ
exchanges the cylinders [ρ] and [σ] and ﬁxes their complement. These cylinder swaps generate
V [BQ17, Theorem 1.1].
  Fix any preﬁx code E = (a1 , . . . , aq ) with q ≥ 2. Suppose ﬁrst that ρ = ai w and σ = aj w0
extend diﬀerent leaves of this code. Then
                       P = sρ tσ = sai (sw tw0 )taj ,         Q = sσ tρ = saj (sw0 tw )tai
make 1 + P and 1 + Q elementary E-roots. Since the coeﬃcient ﬁeld has characteristic two,
                               τρ,σ = (1 + P )(1 + Q)(1 + P ) ∈ ELE (R).
If instead both words extend the same leaf ai , choose a diﬀerent leaf aj . The transposition identity
                                           τρ,σ = τρ,aj τσ,aj τρ,aj
again puts τρ,σ in ELE (R).
   For the complete code D, choose k large enough that every ρw and σw, w ∈ {0, 1}k , extends a
leaf of D. Then                          Y
                               τρ,σ =         τρw,σw ∈ ELD (R).
                                            w∈{0,1}k
Hence V ≤ G. If l extends αi , the same-leaf argument with E = α puts every cylinder swap
supported on [l] in Γ, proving Vl ≤ Γ.                                                  □
3.3. Two contractions and a commuting obstruction. We construct two preﬁx replacements
that send Γ into the same subgroup and together recover G. The three preﬁxes ζ = (100, 101, 11)
partition [1]. Deﬁne u, v ∈ V ≤ G by the tables
                                     αi β i    νi
                                   u αi 0 αi 1 ζ i                (1 ≤ i ≤ 3).                         (14)
                                   v αi 0 ζ i αi 1
Each column lists a source preﬁx, and an entry b below a source preﬁx a means that the replacement
sends aω to bω. The notation αi 0 and αi 1 means appending the indicated bit. In either row, the
six target cylinders [αi 0], [αi 1] partition [0], and the three cylinders [ζi ] partition [1]. Thus both
rows are complete preﬁx replacements.
   Both u and v send [αi ] to [αi 0]. Their other preﬁx images are
              u([βi ]) = [αi 1],     u([νi ]) = [ζi ],        v([βi ]) = [ζi ],   v([νi ]) = [αi 1].
Deﬁne the obstruction group on the ﬁrst leaf of the β-block:
                                           J = Vβ1 = V1000 ≤ G.
The group Γ ﬁxes the six β- and ν-summands pointwise, while J ﬁxes every string outside [1000].
Figure 1 also describes u and v.
  To verify the direct-product structure algebraically, the incomparability of 0 and 1000 gives
                                          e0 e1000 = e1000 e0 = 0.



                                                         92
                         Γ: identity outside [0]
                                                  0                     1


                                             01
                                             α3
                         000        001                                     101                    111
                         α1         α2                                      β3                      ν3
                                                         1000      1001            1100      1101
                                                          β1        β2              ν1        ν2
                                                      J = Vβ1 = V1000


        Figure 1. The blue, teal, and ochre blocks partition [0], [10], and [11], respectively.
        Each element of Γ is the identity on the six teal and ochre summands; J ﬁxes every
        binary string outside the violet cylinder [1000]. Both u and v send αi to αi 0; u
        sends βi to αi 1, whereas v sends νi to αi 1. In particular, u(β1 ) = 0001.

Every g ∈ Γ satisﬁes g − 1 ∈ e0 Re0 , while (13) gives j − 1 ∈ e1000 Re1000 for every j ∈ J.
Orthogonality therefore implies
                                   (g − 1)(j − 1) = (j − 1)(g − 1) = 0.
Thus g and j commute. Moreover, if g = j, then their common diﬀerence from 1 belongs to both
orthogonal corners and is therefore zero. Hence
                               [Γ, J] = 1,            Γ ∩ J = {1},                Γ × J ≤ G.
  Thompson’s group V is ﬁnitely presented, inﬁnite, and simple [CFP96]. Every ﬁnitely presented
LEF group is residually ﬁnite [VG97, Theorem 2.2], whereas an inﬁnite simple group has no
                                  ∼ V is ﬁnitely generated but not LEF.
nontrivial ﬁnite quotient. Thus J =
Proposition 3.2. The preﬁx replacements in (14) satisfy
                 uΓu−1 = vΓv −1 = EL(α1 0,α2 0,α3 0) (R) ≤ Γ,                       uJu−1 = V0001 ≤ Γ    (15)
and
                                                      G = hΓ, u, vi.                                     (16)
Proof. For g = u, v, conjugating an elementary α-root gives
                       g(1 + sαi r tαj )g −1 = 1 + sαi 0 r tαj 0 ,                 i 6= j,     r ∈ R.
Thus both conjugates equal EL(α1 0,α2 0,α3 0) (R). This elementary preﬁx group lies in Γ, since
                                           sαi 0 r tαj 0 = sαi (s0 rt0 )tαj .
Moreover, u sends β1 = 1000 to α1 1 = 0001, so
                                               uJu−1 = V0001 ≤ Γ
by Lemma 3.1. This proves (15).
  To recover G, partition its six α- and β-leaves into three two-leaf blocks
                                       Ci = {αi , βi }             (1 ≤ i ≤ 3).
Set
                            Xi = sαi t0 + sβi t1 ,                 Yj = s0 tαj + s1 tβj .
The inverse preﬁx table for u gives
                               u−1 (1 + sαi r tαj )u = 1 + Xi rYj                      (i 6= j).
Write ℓi,0 = αi and ℓi,1 = βi . Given a matrix B = (bpq ) ∈ M2 (R), take
                                                         X
                                               r=                  sp bpq tq .
                                                       p,q∈{0,1}

Since tp rsq = bpq , we obtain                            X
                                          Xi rYj =                 sℓi,p bpq tℓj,q .
                                                       p,q∈{0,1}


                                                            93
Taking a matrix with one nonzero entry produces every elementary root whose source and target lie
in diﬀerent blocks Ci and Cj . For any three distinct code leaves a, b, c, the elementary commutator
identity
                                  [1 + sa r tc , 1 + sc tb ] = 1 + sa r tb
also supplies the roots between two leaves in the same block: choose c in any diﬀerent block, so
that both roots on the left join distinct blocks. Consequently,
                                           EL(α,β) (R) ≤ hΓ, ui.
The same argument with v and the three blocks {αi , νi } gives
                                            EL(α,ν) (R) ≤ hΓ, vi.
   It remains to connect a β-leaf to a ν-leaf. For any such leaves a, b, choose an α-leaf c. Both
factors on the left-hand side of
                                    [1 + sa r tc , 1 + sc tb ] = 1 + sa r tb
belong to the six-leaf groups just obtained. Interchanging a and b also gives the reverse elementary
root. Thus hΓ, u, vi contains every elementary D-root, proving (16).                              □
Proof of Theorem 1.1. Proposition 3.2 shows that Γ ≤ G, J = V1000 , t1 = u, and t2 = v satisfy
the hypotheses on the groups and their conjugations in Proposition 2.3. If G were soﬁc, its
property (T ) and the single-expander consequence of Theorem 2.1 would give an expanding soﬁc
approximation of G. Proposition 2.3 would then make J LEF, which it is not. Therefore G is not
soﬁc. Since G ≤ R× and soﬁcity passes to subgroups, R× is not soﬁc either.                  □
Acknowledgments. We thank Henry Bradford, Michael Chapman, and Alon Dogon, as well as
Francesco Fournier-Facio, Andrei Jaikin-Zapirain, Gábor Kun, and Andreas Thom, for helpful
comments.

                                               References
[AL07]    D. Aldous and R. Lyons, Processes on unimodular random networks, Electron. J. Probab. 12 (2007),
          1454–1508, arXiv:math/0603062.
[Bir04]   J.-C. Birget, The groups of Richard Thompson and complexity, Int. J. Algebra Comput. 14 (2004),
          569–626, arXiv:math/0204292.
[BQ17]    C. Bleak and M. Quick, The inﬁnite simple group V of Richard J. Thompson: presentations by per-
          mutations, Groups Geom. Dyn. 11 (2017), 1401–1436, arXiv:1511.02123.
[BB20]    L. Bowen and P. Burton, Flexible stability and nonsoﬁcity, Trans. Amer. Math. Soc. 373 (2020),
          4469–4481, doi:10.1090/tran/8047.
[BC25]    L. Bowen and M. Chapman, Surjunctivity does not characterize cosoﬁcity of invariant random sub-
          groups, preprint, 2025, arXiv:2511.06586.
[BCLV24]  L. Bowen, M. Chapman, A. Lubotzky, and T. Vidick, The Aldous–Lyons conjecture I: Subgroup tests,
          preprint, 2024, arXiv:2408.00110.
[BCV25]   L. Bowen, M. Chapman, and T. Vidick, The Aldous–Lyons conjecture II: Undecidability, preprint,
          2025, arXiv:2501.00173.
[BFF24]   H. Bradford and F. Fournier-Facio, Hopﬁan wreath products and the stable ﬁniteness conjecture, Math.
          Z. 308 (2024), article no. 58, doi:10.1007/s00209-024-03589-3.
[BS16]    N. Brownlowe and A. P. W. Sørensen, L2,Z ⊗ L2,Z does not embed in L2,Z , J. Algebra 456 (2016), 1–22,
          doi:10.1016/j.jalgebra.2016.01.040.
[CFP96]   J. W. Cannon, W. J. Floyd, and W. R. Parry, Introductory notes on Richard Thompson’s groups,
          Enseign. Math. (2) 42 (1996), no. 3–4, 215–256, available online.
[CDL24]   M. Chapman, Y. Dikstein, and A. Lubotzky, Conditional non-soﬁcity of p-adic Deligne extensions:
          On a theorem of Gohla and Thom, preprint, 2024, arXiv:2410.02913.
[DCGLT20] M. De Chiﬀre, L. Glebsky, A. Lubotzky, and A. Thom, Stability, cohomology vanishing, and nonap-
          proximable groups, Forum Math. Sigma 8 (2020), article no. e18, doi:10.1017/fms.2020.5.
[Dog23]   A. Dogon, Flexible Hilbert–Schmidt stability versus hyperlinearity for property (T ) groups, Math. Z.
          305 (2023), article no. 58, doi:10.1007/s00209-023-03387-3.
[DV26]    A. Dogon and I. Vigdorovich, Hyperlinearity, stability and asymptotic spectral gap of higher rank
          lattices, preprint, 2026, arXiv:2506.20843v2.
[ES05]    G. Elek and E. Szabó, Hyperlinearity, essentially free actions and L2 -invariants: The soﬁc property,
          Math. Ann. 332 (2005), 421–441, arXiv:math/0408400.
[ES06]    G. Elek and E. Szabó, On soﬁc groups, J. Group Theory 9 (2006), 161–171, arXiv:math/0305352.
[EJ10]    M. Ershov and A. Jaikin-Zapirain, Property (T ) for noncommutative universal lattices, Invent. Math.
          179 (2010), 303–347, arXiv:0809.4095.




                                                      94
[Gel18]   T. Gelander, A view on invariant random subgroups and lattices, in Proceedings of the Interna-
          tional Congress of Mathematicians—Rio de Janeiro 2018, vol. II, World Scientiﬁc, 2018, 1339–1362,
          arXiv:1807.06979.
[GT24]    L. Gohla and A. Thom, High-dimensional expansion and soﬁcity of groups, preprint, 2024,
          arXiv:2403.09582.
[Gro99]   M. Gromov, Endomorphisms of symbolic algebraic varieties, J. Eur. Math. Soc. 1 (1999), 109–197.
[Hut26]   T. Hutchcroft, Are there non-trivial theorems about all ﬁnitely generated groups?, Eur. Math. Soc. Mag.
          139 (2026), 5–12, doi:10.4171/MAG/295.
[Jai19]   A. Jaikin-Zapirain, The base change in the Atiyah and the Lück approximation conjectures, Geom.
          Funct. Anal. 29 (2019), 464–538, doi:10.1007/s00039-019-00487-3.
[JNVWY20] Z. Ji, A. Natarajan, T. Vidick, J. Wright, and H. Yuen, MIP∗ = RE, preprint, 2020, arXiv:2001.04383.
[KT26]    H. V. Khanh and V. H. Thanh, Matrix generators for the unit groups of LK (1, d), preprint, 2026,
          arXiv:2607.10351.
[Kun19]   G. Kun, On soﬁc approximations of property (T ) groups, preprint, 2019, arXiv:1606.04471v5.
[KT19]    G. Kun and A. Thom, Inapproximability of actions and Kazhdan’s property (T ),
          preprint, 2019, revised 2026, arXiv:1901.03963v3.
[Lea62]   W. G. Leavitt, The module type of a ring, Trans. Amer. Math. Soc. 103 (1962), 113–130,
          doi:10.1090/S0002-9947-1962-0132764-X.
[Man25]   A. Manzoor, Invariant random subgroups, soﬁcity, and Lück’s determinant conjecture, preprint, 2025,
          arXiv:2508.15154.
[Nek04]   V. Nekrashevych, Cuntz–Pimsner algebras of group actions, J. Operator Theory 52 (2004), 223–249,
          available online.
[NT22]    M. Nitsche and A. Thom, Universal solvability of group equations, J. Group Theory 25 (2022), 1–10,
          arXiv:1811.07737.
[Pes08]   V. G. Pestov, Hyperlinear and soﬁc groups: A brief guide, Bull. Symbolic Logic 14 (2008), 449–480,
          arXiv:0804.3968.
[Tho08]   A. Thom, Soﬁc groups and diophantine approximation, Comm. Pure Appl. Math. 61 (2008), 1155–1171,
          arXiv:math/0701294.
[VG97]    A. M. Vershik and E. I. Gordon, Groups that are locally embeddable in the class of ﬁnite groups, Algebra
          i Analiz 9 (1997), no. 1, 71–97; English transl., St. Petersburg Math. J. 9 (1998), 49–67, Math-Net.Ru
          aa751.
[Wei00]   B. Weiss, Soﬁc groups and dynamical systems, Sankhyā Ser. A 62 (2000), 350–359.




                                                       95
