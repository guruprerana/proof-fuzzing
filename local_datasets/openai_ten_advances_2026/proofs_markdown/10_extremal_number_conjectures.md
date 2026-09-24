# Counterexamples to the Compactness and Degeneracy Conjectures for Extremal Numbers

> Source: OpenAI, *Ten Advances in Mathematics and Theoretical Computer Science*, Chapter 10, PDF pages 240–253. Layout-preserving text extraction; consult the source PDF for authoritative equation rendering.

                                       Chapter 10

 Counterexamples to the Compactness and
   Degeneracy Conjectures for Extremal
               Numbers
    Abstract. We give two complementary counterexamples in extremal graph the-
    ory. First, we construct a ﬁnite family F of connected bipartite graphs, each
    containing a cycle, for which
                                                                       
          ex(n, F) = O n4/3−1/48         but       ex(n, F ) = Ω n4/3       (F ∈ F).
    This disproves the Erdős–Simonovits compactness conjecture. Second, we con-
    struct a ﬁxed connected bipartite 2-degenerate graph H and ﬁxed constants
    c, ε > 0 such that
                   ex(n, H) ≥ c n3/2+ε         for all suﬃciently large n.
    This disproves a conjecture of Erdős on extremal numbers of r-degenerate graphs.



                                         Contents
1. Introduction
2. The forbidden graphs for compactness
3. Proof of the upper bound in Theorem 1.1
4. The generalized-quadrangle witnesses
5. A binary entropy inequality
6. The layered graph and the parameter thresholds
7. A sampled Hamming-ball graph
8. Excluding the forbidden graph
References




                                           236
                                           1. Introduction
   We disprove the compactness conjecture of Erdős and Simonovits and a degeneracy conjec-
ture of Erdős in extremal graph theory. The compactness conjecture [ES82, Wig] asks whether
forbidding a ﬁnite family of graphs, each containing a cycle, can reduce the extremal number
by more than a constant factor compared with forbidding any individual member. The degen-
eracy conjecture [Erd67] predicts that every bipartite r-degenerate graph has extremal number
O(n2−1/r ), which we disprove even when r = 2.
   Throughout, all graphs are ﬁnite, simple, and undirected, and implicit constants may depend
on ﬁxed forbidden graphs or families. For a graph G, let V (G) and E(G) denote its vertex and
edge sets, respectively. Given a family F of graphs, we say G is F-free if it contains no member
of F as a subgraph. The extremal number of F is
                                           
                      ex(n, F) := max |E(G)| : |V (G)| = n, G is F-free .
For a single graph H, we abbreviate ex(n, {H}) to ex(n, H).
1.1. The compactness conjecture. Erdős and Simonovits conjectured that the extremal
number of a ﬁnite family of graphs is, up to a constant factor, the extremal number of one of its
members [ES82, FS13, Con26, Blo575]. The original formulation admits simple counterexamples
[Wig]. For example, the folklore family {K1,2 , 2K2 } [Blo180] satisﬁes, for n ≥ 4,
           ex(n, {K1,2 , 2K2 }) = 1,           ex(n, K1,2 ) = ⌊n/2⌋,       ex(n, 2K2 ) = n − 1.
The corrected form of the conjecture (see [Wig]) asks: for every ﬁnite nonempty family of graphs
F, all of whose members contain cycles, do there exist F ∈ F and C > 0 such that
                     ex(n, F ) ≤ C ex(n, F)             for all suﬃciently large n?                           (1)
Conlon, Mulrenin, and Pohoata [CMP26] recently disproved a conjecture of Verstraëte [Ver16,
Conj. VIII], a stronger host-graph analog of compactness for even cycles, but their examples
do not resolve the compactness conjecture itself. We disprove this conjecture even when every
member of F is connected and bipartite.
Theorem 1.1 (Failure of compactness). There exists a ﬁnite nonempty family F of connected
bipartite graphs, every member of which contains a cycle, such that, for ε = 1/48,
                                                                                 
               ex(n, F) = O n4/3−ε               and         ex(n, F ) = Ω n4/3       (F ∈ F).                (2)
In particular, no member of F satisﬁes (1).
1.2. The degeneracy conjecture. A graph H is r-degenerate if every nonempty subgraph of
H has a vertex of degree at most r. Erdős [Erd67, Erd97, Blo146] conjectured that every ﬁxed
bipartite r-degenerate graph H satisﬁes
                                                                    
                                       ex(n, H) = O n2−1/r .                                                  (3)
                                                                                                 2−1/(4r)
                                                                                                          
Alon, Krivelevich, and Sudakov proved the weaker general estimate ex(n, H) = O n              for
bipartite r-degenerate graphs [AKS03, Thm. 3.5].
   The conjecture is known in several cases: when one bipartition class has maximum degree at
most r [Fur91, AKS03]; for r-degenerate blow-ups of trees [GJN22]; and, when r = 2, for grids
[BJST23] and certain critical 2-degenerate graphs [DGL25].
   A related conjecture of Erdős [Erd81, Blo113] asserts that a bipartite graph H is 2-degenerate
if and only if ex(n, H) = O(n3/2 ). Janzer [Jan23] disproved the reverse implication by con-
structing, for every η > 0, a 3-regular bipartite graph H with ex(n, H) = O(n4/3+η ). Janzer’s
construction does not address the forward implication, which is the r = 2 case of (3).
   We disprove Erdős’s degeneracy conjecture by constructing a counterexample for r = 2,
thereby also refuting the forward implication of the related conjecture.
Theorem 1.2 (Failure of the 2-degenerate bound). There exist a ﬁxed connected bipartite 2-
degenerate graph H and constants c, ε > 0 such that
                                           ex(n, H) ≥ c n3/2+ε


                                                       237
for all suﬃciently large n.
1.3. Proof strategy. For the compactness conjecture, we select F to consist of C4 , C6 , and
certain admissible quotients of two ﬁxed templates built from subdivided complete bipartite
graphs, in analogy with the rooted-power construction of Bukh and Conlon [BC18]. We count
short paths in a graph avoiding this family to obtain the upper bound ex(n, F) = O(n21/16 ).
For each individual forbidden graph F ∈ F, we obtain the lower bound ex(n, F ) = Ω(n4/3 ) from
the incidence graph of a generalized quadrangle, allowing the characteristic of the underlying
ﬁeld to depend on the forbidden graph. We develop this counterexample in Sections 2 to 4.
   For the degeneracy conjecture, we construct H in layers, adjoining a vertex for every pair of
vertices in the preceding layer. This construction is related to the complete degenerate graphs
of Grzesik, Janzer, and Nagy [GJN22]. To obtain a lower bound on ex(n, H), we independently
retain vertices of a bipartite graph deﬁned by Hamming distance. An embedding of H would
increase a bounded entropy potential by a ﬁxed amount at each layer, which is impossible
after suﬃciently many layers. A second-moment argument shows that the sampled graph has
Ω(n3/2+ε ) edges, and padding extends the construction to every suﬃciently large order. We
develop this counterexample in Sections 5 to 8.

                        2. The forbidden graphs for compactness
  The compactness family arises from two properly 2-colored bipartite templates.
Deﬁnition 2.1 (Subdivisions). For k ∈ {2, 3}, form Sk from K3,k by replacing each edge with
a two-edge path; therefore |V (S2 )| = 11 and |V (S3 )| = 15. Call the three original vertices bases,
the other k original vertices centers, and the inserted vertices subdivision vertices.
Deﬁnition 2.2 (Admissible identiﬁcations). Let T be a properly two-colored graph with dis-
tinguished subgraphs T1 , T2 . An equivalence relation ≈ on V (T ) is admissible if
    (1) v ≈ w implies that v and w have the same color; and
    (2) for i ∈ {1, 2} and v, w ∈ V (Ti ), v ≈ w implies v = w.
Write T /≈ for the simple graph whose vertices are the equivalence classes and in which [v][w]
is an edge whenever some representatives are adjacent in T . Repeated edges are suppressed.
  The ﬁrst condition keeps T /≈ bipartite and prevents loops. The second ensures that the
maps Ti → T /≈ are injective.
Deﬁnition 2.3 (The ﬁrst template). Form J0 from two copies of S2 with base triples {x, y, z}
and {x′ , y, z} by identifying y, z, keeping all other vertices distinct, and adjoining a color-one
vertex λ adjacent to x, x′ . Thus, |V (J0 )| = 21. Let J consist of the uncolored admissible
quotients J0 /≈ satisfying x ̸≈ x′ . This condition preserves all four distinguished bases; λ may
be identiﬁed whenever admissibility permits.
                                                                                       (1)   (2)
Deﬁnition 2.4 (The second template). Let K0 be obtained from disjoint copies S3 , S3 of S3
                               (2)
by reversing the coloring on S3 and adding an edge d1 d2 between speciﬁed centers of the two
copies. Thus, |V (K0 )| = 30. Let K consist of the uncolored graphs K0 /≈, where ≈ is admissible
     (1)  (2)
for S3 , S3 .
  The two templates are shown in Figure 1.
Deﬁnition 2.5 (The forbidden family). Let
                                     F := {C4 , C6 } ∪ J ∪ K.                                      (4)
  As each member of J contains S2 and each member of K contains S3 , every graph in F
contains a cycle.




                                                238
                                                 J0
                                                 λ
                              x                                       x′


                                                 y
                  c1                                                             c′1




                  c2                              z                              c′2



                                                 K0
                            (1)                                            (2)
                           S3           c1                 c′1        S3
             u1                                                                        u′1

                                        d1                 d2
             u2                                                                        u′2


             u3                                                                        u′3
                                        c3                 c′3


                                  Figure 1. The graphs J0 and K0 .

                       3. Proof of the upper bound in Theorem 1.1
   Throughout this section, B is a bipartite graph containing no C4 or C6 , and S is either side
of the bipartition of B. Let RS be the auxiliary common-neighbor graph on S, deﬁned by
                       uv ∈ E(RS )     ⇐⇒    u ̸= v and NB (u) ∩ NB (v) ̸= ∅.
The graph RS records pairs joined by length-two paths in B, which are central to the forbidden
conﬁgurations.
  For distinct u, v ∈ S, write u ∼ v when uv ∈ E(RS ), and call u, v related or unrelated
according as they are adjacent or nonadjacent in RS . Call a set of vertices RS -independent if
no pair is adjacent in RS . For an RS -independent triple T ⊆ S, put
                    L(T ) := {c ∈ S : c ∼ t for all t ∈ T } and r(T ) := |L(T )|.
Lemma 3.1 (Common-neighbor geometry). The following assertions hold:
  (1) Every related pair has a unique common neighbor. If three distinct members of S are
      pairwise related, the three pairs have the same common neighbor.
  (2) If T ⊆ S is an RS -independent triple, then L(T ) is RS -independent and disjoint from T .
      If r(T ) ≥ k, for k ∈ {2, 3}, then B contains a copy of Sk with base set T . Conversely, the
      bases of any such copy form an RS -independent triple with at least k common centers.
  (3) If u, v ∈ S are distinct and unrelated, then any two distinct vertices related to both u
      and v are unrelated. Equivalently, the set
                                   Zuv = {w ∈ S : w ∼ u, w ∼ v}
       is RS -independent.
Proof. A related pair has a unique common neighbor, since two would form a C4 . For three
pairwise related vertices, their common neighbors either all coincide or form a C6 . This proves
(1).
   If u ̸∼ v and w, w′ ∈ Zuv were related, (1) would make their common neighbor adjacent to
both u and v, a contradiction. This proves (3).
   For distinct u, v ∈ T , we have L(T ) ⊆ Zuv . Thus, (3) makes L(T ) independent, while
irreﬂexivity gives L(T ) ∩ T = ∅. If r(T ) ≥ k, the unique common neighbors of the 3k pairs
between T and any k centers in L(T ) are distinct: a repetition would relate two bases or two


                                                239
centers. This forms a copy of Sk . Conversely, (1) forces related bases in such a copy to share a
subdivision vertex at every center, a contradiction. Thus, its bases are independent and its k
centers belong to L(T ), proving (2).                                                          □
Lemma 3.2 (Non-backtracking four-edge-walk count). If δ(B) ≥ d ≥ 2, then, for every u ∈ S,
                                         X
                                                  |Zuv | ≥ d(d − 1)3 .                          (5)
                                       v∈S\{u}
                                         v̸∼u

Proof. There are at least d(d − 1)3 non-backtracking walks u, a, w, b, v. Since B has girth at
least eight, each satisﬁes v ̸= u and v ̸∼ u; otherwise it closes to a cycle of length at most six.
By Lemma 3.1(1), these walks correspond bijectively to pairs (v, w) with v ̸= u, v ̸∼ u, and
w ∈ Zuv . Counting these pairs proves (5).                                                      □
Lemma 3.3 (Minimum-degree reduction). Let G be an n-vertex graph without C4 or C6 , and
put m = |E(G)| > 0. There is a nonempty bipartite subgraph B of order N ≤ n and minimum
degree d such that
                        m ≤ 2nd      and     ∆(B)(d − 1)2 ≤ N.
Proof. A maximum cut yields a bipartite subgraph with at least m/2 edges. Deleting vertices
of degree < m/(2n) cannot exhaust it, since fewer than m/2 edges would be removed. Thus,
the remainder B satisﬁes d = δ(B) ≥ m/(2n), and hence m ≤ 2nd.
   Since B has girth at least eight, the radius-three neighborhood of a maximum-degree vertex
is a tree. Its third level contains at least ∆(B)(d − 1)2 vertices, so ∆(B)(d − 1)2 ≤ N .  □
   The main estimate uses the two forbidden families in complementary ways. Excluding J
bounds the number of vertices that fail to be centers of a subdivided K3,3 , while excluding K
forces every edge to meet one of these vertices.
Proposition 3.4. For the family F in (4),
                              ex(n, F) = O(n21/16 ) = O(n4/3−1/48 ).
Proof. Let G be an n-vertex F-free graph. We may assume m := |E(G)| ≥ Cn21/16 , where
C ≥ 1 is suﬃciently large. Let B be the bipartite subgraph supplied by Lemma 3.3, with order
N ≤ n and minimum degree d. Put
                            m                                            p
                       d≥      ≫ CN 5/16 ,     p = d(d − 1)3 ,    R=       .
                            2n                                         2N
  Fix a bipartition   class S and u ∈ S, and write tuv = |Zuv |. Lemma 3.1 shows that Cu :=
P      tuv 
  v̸=u 3     counts the copies of S2 with center u. By discrete convexity of binomial coeﬃcients,
  v̸∼u
we have                                              P             !
                                             N −1       v̸=u tuv           d12
                                Cu ≥ N                  v̸∼u           ≫       ,
                                                       3                   N2
                         P
where Lemma 3.2 gives      v̸=u tuv   ≥ d(d − 1)3 .
                           v̸∼u
  We use the exclusion of J to bound the number of possible base triples. For an unrelated
pair y, z ∈ S, let
                   
           Ayz := x ∈ S \ {y, z} : {x, y, z} is independent in RS , r({x, y, z}) ≥ 2 .
This is the set of possible third bases for copies of S2 whose other bases are y, z. If two distinct
vertices of Ayz were related, their witnessing copies of S2 , together with their common neighbor,
would produce a member of J . Thus, Ayz is RS -independent; its vertices therefore have pairwise
disjoint neighborhoods, and |Ayz | ≤ N/d.
   Writing TS for the set of independent triples in S with at least two common centers, we obtain
                                                                       !
                                     1 X                N N                    N3
                             |TS | =           |Ayz | ≤                    ≤      .             (6)
                                     3 {y,z}⊆S          3d 2                   6d
                                           y̸∼z



                                                     240
  Let U ⊆ V (B) be the set of vertices that are not centers of any copy of S3 . For every
bipartition class S and every u ∈ S, we have
                                             X                 
                                    Cu =              r(T ) − 1 .
                                             T ∈TS
                                            u∈L(T )

Indeed, for each triple T with u ∈ L(T ), choosing another center v ∈ L(T ) \ {u} determines
a copy of S2 with base triple T and centers u, v; conversely, every copy counted by Cu arises
uniquely in this way.
   If u ∈ U ∩ S and u ∈ L(T ), then necessarily r(T ) = 2: otherwise, u together with two other
members of L(T ) would be the centers of a copy of S3 , by Lemma 3.1. Therefore, additionally
using (6), we have
                                   d12     X                    N3
                           |U ∩ S| 2 ≪           Cu ≤ 2|TS | ≪     .
                                   N      u∈U ∩S
                                                                d
Summing over the two bipartition classes gives
                                                N5
                                            |U | ≪  .                                    (7)
                                                d13
   We claim that U is a vertex cover of B. Otherwise, there would be an edge uv ∈ E(B) with
u, v ∈
     / U . Choose a copy of S3 having u as a center and a copy of S3 having v as a center.
Together with the edge uv, these copies form an admissible quotient of K0 , and hence give a
member of K, contrary to the choice of B. Thus, every edge of B meets U .
   By Lemma 3.3 we have ∆(B) ≪ dN2 . Since U is a vertex cover, (7) implies
                                                        N6
                               N d ≤ 2e(B) ≤ 2|U |∆(B) ≪    .
                                                        d15
Therefore d16 ≪ N 5 , which is a contradiction provided that C ≥ 1 is a suﬃciently large
constant.                                                                             □

                       4. The generalized-quadrangle witnesses
   We now proceed to the lower bound side of Theorem 1.1. Since the required constructions
already appear in the literature (e.g. [PT09] and [BHKT18]), we keep the proof brief.
   Let q be a prime power, let V = F4q , and ﬁx a nondegenerate alternating bilinear form
                                      ⟨·, ·⟩ : V × V −→ Fq .
The symplectic generalized quadrangle W (q) has point and line classes
      P = {P ≤ V : dim P = 1}         and       M = {M ≤ V : dim M = 2, ⟨M, M ⟩ = 0},
with incidence given by containment. Let
                                           Iq := I(W (q))
denote its bipartite incidence graph: its vertex set is P ⊔ M, and P ∈ P is adjacent to M ∈ M
precisely when P ⊆ M . This is the standard symplectic construction of W (q); see [PT09, §3.2.1]
and [BHKT18, §4].
   The quadrangle has order (q, q): every point lies on q + 1 lines, every line contains q + 1
points, and
                                  |P| = |M| = (q + 1)(q 2 + 1).
Its incidence graph has girth eight [PT09, §1.1, §1.2.1, and §3.1.1]. Consequently,
                 nq = 2(q + 1)(q 2 + 1),      eq = (q + 1)2 (q 2 + 1) ≥ 2−4/3 n4/3
                                                                               q .          (8)
  For S ∈ {P, M}, retain the common-neighbor graph RS , the sets L(T ), and the quantities
r(T ) from the preceding section, with B = Iq . Explicitly, for distinct vertices in the same
bipartition class,
                        P ∼ P ′ ⇐⇒ ⟨P, P ′ ⟩ = 0       (P, P ′ ∈ P),




                                                241
and
                     M ∼ M ′ ⇐⇒ M ∩ M ′ ̸= {0}              (M, M ′ ∈ M).
  We will also use two classical facts. The dual generalized quadrangle W (q)D is isomorphic to
the parabolic quadrangle Q(4, q), and W (q) is self-dual when q is even [PT09, §3.2.1]; see also
[BHKT18, §4].
Deﬁnition 4.1 (Local patterns). A J-pattern in S consists of independent triples {x, y, z} and
{x′ , y, z}, each with at least two common centers, such that x ∼ x′ . An S3 -pattern in S is an
RS -independent triple with at least three common centers.
   A member of J forces a J-pattern in one bipartition class, while a member of K forces an
S3 -pattern in both bipartition classes.
Proposition 4.2 (Quadrangle witnesses). For even q, Iq is J -free; for odd q, it is K-free. In
either case, it contains no C4 or C6 .
Proof. Let y, z ∈ P be noncollinear, and put U = y + z. Since y and z are not orthogonal,
U is a nondegenerate two-dimensional subspace of V . Their common centers are precisely the
projective points of U ⊥ . If a third point x has at least two common centers with y, z, then x is
orthogonal to two distinct projective points of U ⊥ , and therefore to all of U ⊥ . Hence,
                                         x ⊆ (U ⊥ )⊥ = U.
Any two distinct projective points of the nondegenerate symplectic plane U are nonorthogonal.
Therefore, any two possible third bases are unrelated, and P contains no J-pattern.
  If q is even, the self-duality of W (q) [PT09, §3.2.1] gives the same conclusion for M. Thus,
neither bipartition class contains a J-pattern, and Iq is J -free.
  If q is odd, identify M with the point class of the dual quadrangle Q(4, q). Every triad in
Q(4, q) has either zero or two centers [BHKT18, Proposition 4.5]; see also [PT09, §1.3.6(iii) and
§3.3.1]. Consequently, M contains no S3 -pattern, and therefore Iq is K-free.
  Finally, the girth-eight property excludes C4 and C6 .                                        □
Proposition 4.3 (Individual lower bounds). For every F ∈ F,
                                       ex(n, F ) = Ω(n4/3 ).
Proof. If F ∈ {C4 , C6 } ∪ J , take q = 2j ; if F ∈ K, take q = 3j . In either case, Proposition 4.2
makes Iq F -free. For t ∈ {2, 3},
                                ntq = 2(tq + 1)(t2 q 2 + 1) ≤ t3 nq .
Choose the largest admissible q for which nq ≤ n. The displayed inequality gives nq ≫ n.
Padding Iq with isolated vertices preserves F -freeness, since F is connected and contains an
edge. Hence, (8) gives
                                    ex(n, F ) ≥ eq ≫ n4/3 .                                 □
Proof of Theorem 1.1. The family in (4) is ﬁnite and nonempty, and each of its members is
connected, bipartite, and contains a cycle. Propositions 3.4 and 4.3 give (2); in particular, (1)
cannot hold for any F ∈ F.                                                                     □

                              5. A binary entropy inequality
   We now proceed to the proof of Theorem 1.2. The graph H consists of layers L1 , L2 , . . ., with
every vertex in Li having two parents in Li−1 . The host graph is a variant of the Hamming cube
in which points at most a ﬁxed linear distance apart are adjacent. This construction naturally
leads to the entropy inequalities considered in this section.
   All logarithms and entropies are to base two. Write
                  h(x) := −x log2 x − (1 − x) log2 (1 − x),       h(0) = h(1) = 0,
and put
                                               3 3
                                        κ :=    − log2 3.
                                               2 4

                                                242
   The following inequality converts a bound on the average disagreement between a child and
its parents into a bound on its conditional entropy.
Lemma 5.1 (Independent-parent entropy). Let X, Y be independent Bernoulli variables with
common parameter q, and let Z be any jointly distributed binary variable. Write
                                                 P(X ̸= Z) + P(Y ̸= Z)
                       v = P(Z = 1),         d=                            .
                                                             2
Then
                                                            h(v) − h(q)
                         H(Z | X, Y ) ≤ κ + (log2 3)d +                  .                   (9)
                                                                 2
Proof. For a probability vector (r0 , r1 ) and nonnegative numbers t0 , t1 , the Gibbs inequality
gives                    X                    X
                     −        rz log2 rz +        rz log2 tz ≤ log2 (t0 + t1 ).             (10)
                            z∈{0,1}               z∈{0,1}
Indeed, after writing T = t0 + t1 , the diﬀerence between the right-hand and left-hand sides is
                                      X                    
                                                        rz
                                            rz log2           ≥ 0.
                                    z∈{0,1}
                                                      tz /T
  Put
                                            1x̸=z + 1y̸=z
                             c(x, y, z) =                 ,        πz = P(Z = z).
                                                  2
For ﬁxed x, y, apply (10) with
                                                                          √
                     rz = P(Z = z | X = x, Y = y),                 tz =       πz 3−c(x,y,z) .
Averaging over X, Y gives
                                                                                                !
                                h(v)                      X1
                                                              √
                 H(Z | X, Y ) −      − (log2 3)d ≤ E log2       πz 3−c(X,Y,z) .                     (11)
                                 2                        z=0
  It remains to bound the right-hand side. Set
                              √                √
                         a = 1 − v,        b = v,                      u = 2q − 1,
so that a2 +b2 = 1. The three possible types for {X, Y }, namely 00, 11, and 01, have probabilities
                            (1 − u)2              (1 + u)2             1 − u2
                        α0 =         ,     α1 =            ,    α∗ =          ,
                                 4                    4                   2
and give respective expressions
                                     b            a                a+b
                           t0 = a + ,        t1 = + b,       t∗ = √ .
                                     3            3                    3
Thus, after adding h(q)/2, the right-hand side of (11) becomes
                               1
                         F = h(q) + α0 log2 t0 + α1 log2 t1 + α∗ log2 t∗ .
                               2
  Since                                                   
                                                     t
                        log2 t ≤ log2 λ + (log2 e)      −1       (t, λ > 0),
                                                     λ
we have
                                                          √               !
                             b             4                 3 2         b
                 log2 a +        ≤ log2 √        + (log2 e)         a+       −1 ,
                             3           3 2                  4          3
                                                          √               !
                        a                  4                 3 2 a
                 log2     + b ≤ log2 √           + (log2 e)            +b −1 ,
                        3                3 2                  4      3
                                              r !                              
                            a+b                  2                     a+b
                 log2        √         ≤ log2         + (log2 e)        √ −1 .
                               3                 3                       2




                                                      243
Multiplying these inequalities by
                             (1 − u)2               (1 + u)2           1 − u2
                      α0 =             ,     α1 =            ,    α∗ =        ,
                                 4                      4                 2
respectively, and summing, gives
                                                                     
                                  b                a                  a+b
                   α0 log2 a +        + α1 log2      + b + α∗ log2 √
                                 3                 3                    3
                                3           u 2      4
                         ≤ 1 − log2 3 +         log2
                                4            4       3
                                                                 
                                         (2 − u)a + (2 + u)b
                           + (log2 e)              √           −1
                                                  2 2
                                                                s                
                               3         u2     4                 u2
                          ≤ 1 − log2 3 +    log2 + (log2 e)  1 +    − 1 ,
                               4         4      3                 4

where the ﬁnal inequality follows from Cauchy–Schwarz and a2 + b2 = 1.
  Therefore
                                                                      s                
                             
               1  1+u                  3         u2     4                 u2
            F ≤ h                 + 1 − log2 3 +    log2 + (log2 e)  1 +    − 1 .         (12)
               2   2                   4         4      3                 4
A direct optimization shows that the right-hand side of (12) is maximized at u = 0, where it
equals κ. Together with (11), this proves (9).                                            □
   In the layered construction, the two parents are sampled without replacement. The resulting
error vanishes as the layer size tends to inﬁnity.
Lemma 5.2 (Without-replacement correction). Let L ≥ 4, let x1 , . . . , xL ∈ {0, 1}, and sample
an ordered pair of distinct indices uniformly. Let X, Y be the corresponding bits, and let Z have
any conditional binary law given X, Y . Put
                    1 XL
                                                              P(X ̸= Z) + P(Y ̸= Z)
               q=         xa ,       v = P(Z = 1),       d=                         .
                    L a=1                                               2
Then
                                                          h(v) − h(q)
                         H(Z | X, Y ) ≤ κ + (log2 3)d +               + η(L),
                                                               2
where                                                   
                                               log2 L
                                   η(L) = O            = o(1)
                                                 L
uniformly over all choices of the bits and the conditional law of Z.
Proof. Couple sampling with and without replacement so that
                                                                   1
                                      P (X, Y ) ̸= (X ′ , Y ′ ) ≤ ,
                                                                   L
where X , Y are independent Bernoulli variables with parameter q. Give Z ′ , conditionally on
             ′   ′

X ′ , Y ′ , the same conditional law used to deﬁne Z. Then
                                                                        1
                                  H(Z | X, Y ) − H(Z ′ | X ′ , Y ′ ) ≤ ,
                                                                        L
while
                                1                  1
                     |d − d′ | ≤ ,     |v − v ′ | ≤ ,         |h(v) − h(v ′ )| ≤ h(1/L).
                                L                  L
Now apply Lemma 5.1 to (X ′ , Y ′ , Z ′ ).                                                  □




                                                   244
                  6. The layered graph and the parameter thresholds
   The construction depends on a Hamming radius τ ∈ (0, 1/2) and a sampling exponent β ∈
(0, 1). Deﬁne
                         A(τ ) := κ + τ log2 3,    C(τ ) := 2h(τ ) − 1.
The threshold A(τ ) controls exclusion of the layered graph, while C(τ ) controls whether the
sampled host has more than n3/2 edges.
   For now, assume that
                                       A(τ ) < β < C(τ ).                                (13)
We verify at the end that such parameters exist.
   Choose
                                                β − A(τ )
                                      0<δ<                .
                        
                                                   4
Since η(L) = o(1) and L2 ≍ L2 , ﬁx L0 ≥ 4 suﬃciently large that, for every L ≥ L0 ,
                                                              !       !       !
                                                              L       L
                        η(L) < δ,       L + 3 log2              +1 −δ             < −1.     (14)
                                                              2       2
Then choose an integer s ≥ 2 such that
                                                                  
                                         2s β − A(τ ) − 2δ > 1.                             (15)
  Take disjoint layers V0 , . . . , Vs with
                                                                  !
                                                          Vi−1
                              |V0 | = L0 ,       Vi =                 (1 ≤ i ≤ s).
                                                           2
Join each vertex {a, b} ∈ Vi to its two parents a, b ∈ Vi−1 , and let H be the resulting graph.
Writing
                                           Li = |Vi |,
we have                                       !
                                         Li−1
                                  Li =          ≥ Li−1 ≥ L0 .
                                          2
Fact 6.1. The graph H is connected, bipartite, and 2-degenerate.

                               7. A sampled Hamming-ball graph
  For m ≥ 1, put
                     U = {0, 1}m ,           Q = 2m ,         p = 2−βm ,       k = ⌊τ m⌋.
Take two disjoint copies UL , UR of U , joining vertices on opposite sides whenever their Hamming
distance is at most k. Independently retain each vertex with probability p, and write Gm for
the induced subgraph.
   For a parent array
                                                   a=1 ∈ U
                                          u = (ua )L       L

and a child array                                                       !
                                                                      L
                          z = (z{a,b} ){a,b}∈([L]) ∈ U ,
                                                      M
                                                              M=         ,
                                               2                      2
choose a uniformly random parent pair and orient it using an independent fair coin. In coordi-
nate j, denote the resulting parent and child bits by Xj , Yj , Zj , and deﬁne
                                                  1 Xm
                                    E(u, z) :=          H(Zj | Xj , Yj ).
                                                  m j=1

   An array of conditional entropy E has at most 2mM E+O(m log2 M ) realizations, while requiring
its M children to survive sampling costs 2−βmM . Since M ≍ L2 , this dominates the 2mL possible
parent arrays whenever E < β.



                                                        245
Lemma 7.1 (Exclusion of low-entropy arrays). With probability at least 1 − 2s 2−m , simulta-
neously on both host sides and at every transition, there is no parent array of length Li−1 and
pairwise distinct retained child array of length Li satisfying
                                        E(u, z) ≤ β − δ.                                  (16)
Proof. Fix a host side, a transition, and a parent array. Write
                                                                      !
                                                                     L
                                L = Li−1 ,            M = Li =         .
                                                                     2
For each coordinate j, partition the parent pairs according to their bit types
                                        G = {00, 11, 01},
where 01 includes both orientations of a mixed pair. Let Ng,j be the size of group g, and let
bg,j count its children having jth bit equal to one. Then
                                                                          !
                                                      X Ng,j
                                                         bg,j
                              H(Zj | Xj , Yj ) =       h                      .
                                                 g∈G
                                                     M   Ng,j

  There are at most (M + 1)3m possible proﬁles (bg,j )g,j . For a ﬁxed proﬁle, the number of
child arrays, allowing repeated words, is
                                                     !
                                  Y
                                  m Y
                                              Ng,j
                                                         ≤ 2mM E(u,z) ,
                                  j=1 g∈G
                                              bg,j
by the estimate                                 !
                                            N
                                                    ≤ 2N h(r/N ) .
                                            r
Therefore, at most
                                      (M + 1)3m 2mM (β−δ)
child arrays satisfy (16).
  For pairwise distinct children, the probability that they are all retained is
                                            pM = 2−βmM .
There are QL = 2mL possible parent arrays, so (14) gives
                     P(a bad retained array) ≤ QL (M + 1)3m 2mM (β−δ) pM
                                                    = 2m[L+3 log2 (M +1)−δM ]
                                                    ≤ 2−m .
Take a union bound over both host sides and all s transitions.                              □

                            8. Excluding the forbidden graph
Proposition 8.1 (Exclusion of the layered graph). With probability 1 − o(1), the sampled graph
Gm is H-free.
Proof. Assume the event in Lemma 7.1, and suppose that
                                             ι : H ,→ Gm
is an embedding. Since H is connected and bipartite, consecutive layers occupy opposite sides
of the host.
   For the parent and child arrays at transition i, write
                                            Ei = E(ui , zi ).
The children are distinct and retained, so Lemma 7.1 gives
                                              Ei > β − δ.                                 (17)




                                                     246
  Deﬁne the entropy potential of layer i by
                                                                          
                                       1 Xm
                                                1 X
                                  Φi =       h            z(j) .
                                       m j=1    Li z∈ι(V )
                                                                  i

Since binary entropy belongs to [0, 1],
                                                0 ≤ Φi ≤ 1.
  At transition i, let
                                     P(Xj ̸= Zj ) + P(Yj ̸= Zj )
                                  dj =                           .
                                                  2
Every child is adjacent to both parents, and therefore
                 1 Xm
                             1            X                                                      
                       dj =                             dist(ua , z{a,b} ) + dist(ub , z{a,b} )
                 m j=1      2mLi            V
                                    {a,b}∈( i−1
                                             2
                                                )
                            k
                            ≤  ≤ τ.
                           m
Applying Lemma 5.2 in each coordinate and averaging gives
                                           Φi − Φi−1
                              Ei ≤ A(τ ) +           + η(Li−1 ).                                      (18)
                                               2
Combining (17), (18), and (14), we obtain
                                                                           
                                  Φi − Φi−1 > 2 β − A(τ ) − 2δ .
Hence, (15) gives                                                      
                             Φs − Φ0 > 2s β − A(τ ) − 2δ > 1,
contradicting 0 ≤ Φi ≤ 1. Therefore,
                                   P(H ⊆ Gm ) ≤ 2s 2−m = o(1).                                          □
Proof of Theorem 1.2. Continue assuming (13); the existence of suitable parameters will be
checked at the end.
  Put                                             !
                                          ⌊τ m⌋
                                           X m
                                    Dm =           .
                                           j=0
                                                j
The standard Hamming-ball estimate gives
                                          Dm = 2(h(τ )+o(1))m .
For
                                 Wm = |V (Gm )|,              em = e(Gm ),
we have
                                EWm = 2pQ,               Var(Wm ) ≤ 2pQ,
and
                         Eem = p2 QDm ,         Var(em ) ≤ p2 QDm + 2p3 QDm
                                                                          2
                                                                            .
Since β < C(τ ) < 1,
                                         pQ = 2(1−β)m −→ ∞
and
                                p2 QDm = 2(1+h(τ )−2β+o(1))m −→ ∞.
Consequently,
                                                              1
                                  Wm ≤ 3pQ,               em ≥ p2 QDm
                                                              2
with probability 1 − o(1).
  Combining these estimates with Proposition 8.1, and padding with isolated vertices, gives
                                   1                   l          m
                       ex(Nm , H) ≥ p2 QDm ,     Nm = 3 · 2(1−β)m .
                                   2


                                                    247
Moreover,
                                   1 + h(τ ) − 2β  3 2h(τ ) − 1 − β
                                                  = +
                                       1−β         2    2(1 − β)
                                                   3 C(τ ) − β    3
                                                  = +           > .
                                                   2  2(1 − β)    2
Therefore, for any ﬁxed
                                                          C(τ ) − β
                                                0<ε<                ,                    (19)
                                                          2(1 − β)
we have
                                               ex(Nm , H) ≥ Nm
                                                             3/2+ε

for all suﬃciently large m.
   Since 21−β < 2,
                                        Nm+1 ≤ 2Nm .
Thus, for every suﬃciently large n, there is an m such that
                                             Nm ≤ n < Nm+1 ≤ 2Nm .
Padding once more gives
                                 ex(n, H) ≥ ex(Nm , H) ≥ 2−3/2−ε n3/2+ε .
  It remains to verify that the parameter window (13) is nonempty. Its width is
                             f (τ ) = C(τ ) − A(τ ) = 2h(τ ) − 1 − κ − τ log2 3.
Since                                                              
                                         ′                    1−τ
                                        f (τ ) = 2 log2                 − log2 3,
                                                               τ
the strictly concave function f is maximized at
                                                            1
                                                   τ=        √ .
                                                          1+ 3
          √
Set r =       3. At this value of τ ,
                                                                                 
                                                                               1
                                    2h(τ ) − τ log2 3 = 2 log2              1+   ,
                                                                               r
while
                                              1 1                3
                                    κ=         + log2 (1 + r2 ) − log2 r.
                                              2 2                2
Hence,
                                                                        !
                                          1              (1 + r)4
                                  f (τ ) = log2
                                          2             8r(1 + r2 )
                                                                              !
                                              1          (r − 1)4
                                             = log2 1 +                           > 0.
                                              2         8r(1 + r2 )
We may therefore choose any
                                      A(τ ) < β < C(τ ),
and subsequently any ε satisfying (19). The remaining assertions follow from Fact 6.1.     □




                                                          248
                                               References
[AKS03]  N. Alon, M. Krivelevich, and B. Sudakov, Turán numbers of bipartite graphs and related
         Ramsey-type questions, Combin. Probab. Comput. 12 (2003), 477–494, https://doi.org/10.1017/
         S0963548303005741.
[BHKT18] D. Bartoli, T. Héger, G. Kiss, and M. Takáts, On the metric dimension of aﬃne planes, biaﬃne
         planes and generalized quadrangles, Australas. J. Combin. 72 (2018), 226–248, https://ajc.maths.
         uq.edu.au/pdf/72/ajc_v72_p226.pdf.
[Blo113] T. F. Bloom, Erdős problem #113, https://www.erdosproblems.com/113.
[Blo146] T. F. Bloom, Erdős problem #146, https://www.erdosproblems.com/146.
[Blo180] T. F. Bloom, Erdős problem #180, https://www.erdosproblems.com/180.
[Blo575] T. F. Bloom, Erdős problem #575, https://www.erdosproblems.com/575.
[BJST23] D. Bradač, O. Janzer, B. Sudakov, and I. Tomon, The Turán number of the grid, Bull. Lond. Math.
         Soc. 55 (2023), 194–204, https://doi.org/10.1112/blms.12721.
[BC18]   B. Bukh and D. Conlon, Rational exponents in extremal graph theory, J. Eur. Math. Soc. 20 (2018),
         1747–1757, https://doi.org/10.4171/JEMS/798.
[Con26]  D. Conlon, Combinatorial theorems relative to sparse sets, manuscript, 2026; to appear in the Pro-
         ceedings of the International Congress of Basic Science, available online.
[CMP26] D. Conlon, E. Mulrenin, and C. Pohoata, Two counterexamples to a conjecture about even cycles,
         2026, arXiv:2603.24515.
[DGL25] Z. Dong, J. Gao, and H. Liu, Bipartite Turán problems via graph gluing, Bull. Lond. Math. Soc. 57
         (2025), 3783–3796, https://doi.org/10.1112/blms.70243.
[Erd67]  P. Erdős, Some recent results on extremal problems in graph theory, in Theory of Graphs (International
         Symposium, Rome, 1966), Gordon and Breach, New York, 1967, 117–123.
[Erd81]  P. Erdős, Problems and results in graph theory, in The Theory and Applications of Graphs (Kalamazoo,
         1980), Wiley, New York, 1981, 331–341, https://www.renyi.hu/~p_erdos/1981-20.pdf.
[Erd97]  P. Erdős, Some of my favorite problems and results, in The Mathematics of Paul Erdős, I, Algorithms
         Combin. 13, Springer, Berlin, 1997, 47–67, https://doi.org/10.1007/978-3-642-60408-9_3.
[ES82]   P. Erdős and M. Simonovits, Compactness results in extremal graph theory, Combinatorica 2 (1982),
         275–288, https://doi.org/10.1007/BF02579234.
[Fur91]  Z. Füredi, On a Turán type problem of Erdős, Combinatorica 11 (1991), 75–79, https://doi.org/10.
         1007/BF01375476.
[FS13]   Z. Füredi and M. Simonovits, The history of degenerate (bipartite) extremal graph problems,
         in Erdős Centennial, Bolyai Soc. Math. Stud. 25 (2013), 169–264, https://doi.org/10.1007/
         978-3-642-39286-3_7.
[GJN22] A. Grzesik, O. Janzer, and Z. L. Nagy, The Turán number of blow-ups of trees, J. Combin. Theory
         Ser. B 156 (2022), 299–309, https://doi.org/10.1016/j.jctb.2022.05.004.
[Jan23]  O. Janzer, Disproof of a conjecture of Erdős and Simonovits on the Turán number of graphs with
         minimum degree 3, Int. Math. Res. Not. 2023 (2023), 8478–8494, https://doi.org/10.1093/imrn/
         rnac076.
[PT09]   S. E. Payne and J. A. Thas, Finite Generalized Quadrangles, 2nd ed., EMS Series of Lectures in
         Mathematics 9, European Mathematical Society, 2009, https://doi.org/10.4171/066.
[Ver16]  J. Verstraëte, Extremal problems for cycles in graphs, in Recent Trends in Combinatorics, IMA Vol.
         Math. Appl. 159, Springer, Cham, 2016, 83–116, https://doi.org/10.1007/978-3-319-24298-9_4.
[Wig]    Y. Wigderson, The Erdős–Simonovits compactness conjecture needs more assumptions, https://
         ywigderson.math.ethz.ch/math/static/Compactness.pdf.




                                                     249
