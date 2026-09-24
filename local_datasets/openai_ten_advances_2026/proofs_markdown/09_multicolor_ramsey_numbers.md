# Super-exponential Lower Bounds for R(3, …, 3)

> Source: OpenAI, *Ten Advances in Mathematics and Theoretical Computer Science*, Chapter 9, PDF pages 233–239. Layout-preserving text extraction; consult the source PDF for authoritative equation rendering.

                                   Chapter 9

      Super-exponential lower bounds for
                  R(3, . . . , 3)
    Abstract. Let Rk (3) = R(3, . . . , 3) denote the multicolor Ramsey number
                                  | {z }
                                     k
    for k colors, that is, the least N for which every k-coloring of the edges of KN
    contains a monochromatic triangle. We prove that there exists an absolute
    constant c > 0 such that, for every integer k ≥ 2,
                                                      !k
                                             ck 1/3
                                 Rk (3) ≥                  .
                                             log k
    Together with the classical factorial upper bound, this establishes Rk (3) =
    k Θ(k) . In particular, the Shannon capacity of graphs with independence num-
    ber 2 is unbounded.



                                      Contents
1. Introduction
2. Saturated matrices, coordinate covers, and palettes
3. Recursive triangle-free colorings
References




                                           229
                                          1. Introduction
  Write
                                          Rk (3) = R(3, . . . , 3)
                                                       | {z }
                                                           k
for the least integer N such that every coloring of E(KN ) with k colors contains a monochro-
matic triangle. Via the standard product construction
                                                                                    
                            Rk+ℓ (3) − 1 ≥ Rk (3) − 1 Rℓ (3) − 1
and Fekete’s lemma, the limit
                                          L = lim Rk (3)1/k                                (1)
                                                k→∞
exists in [1, ∞].
   Previous lower bounds were obtained by tensoring small triangle-free colorings and by
constructions from sum-free partitions [GG55, Chu73, CG83, Exo94, FS00]. After a series
of improvements, the best known lower bound before this work was
                                      Rk (3) ≥ 380k/5 − O(1)
[ACPPRT21, Blo183]. On the upper-bound side, reﬁnements [Whi73, Wan97, XXC02,
Blo183, Rad] of the standard monochromatic-neighborhood recurrence led to constant-factor
improvements of the upper bound. The current record is
                                               
                                              1
                                Rk (3) ≤ e −      k! + 1  (k ≥ 4).                        (2)
                                              6
   The question whether Rk (3) grows superexponentially was recorded by Graham, Roth-
schild, and Spencer [GRS90, p. 146]. The connection between the multicolor Ramsey problem
and Shannon capacity appears implicitly in work of Erdős, McEliece, and Taylor [EMT71]
and was made explicit by Alon and Orlitsky [AO95, §2.1], who also raised the analogous
question for R(c, . . . , c) with ﬁxed c. The gap between these exponential lower bounds and
factorial upper bounds was later highlighted explicitly by Conlon, Fox, and Sudakov [CFS15,
§2.1]; see also [CG83, Rad]. For the broader interaction between structure and randomness,
see Gowers [Gow00]. Erdős oﬀered $250 for determining the value of (1) and $100 for deciding
whether it is ﬁnite [CG83, Blo183, CG].
Theorem 1.1. There exists an absolute constant c > 0 such that, for every integer k ≥ 2,
                                                                            !k
                                                                   ck 1/3
                                R(3, . . . , 3) = Rk (3) ≥                       .         (3)
                                   | {z }                          log k
                                      k
Together with (2), this gives
                    k (1/3−o(1))k ≤ Rk (3) ≤ k (1+o(1))k ,             Rk (3) = k Θ(k) .
In particular,
                                          lim Rk (3)1/k = +∞.                              (4)
                                       k→∞

   The Ramsey–Shannon correspondence [EMT71, AO95] also gives an equivalent formula-
tion of (4). For a graph G, write
                                                                   1/m
                                     Θ(G) = sup α G⊠m
                                                 m≥1

for its Shannon capacity, where α(G) is the independence number and ⊠ denotes the strong
graph product. Given a triangle-free k-coloring of KN , let Hi be the graph of color i and set
                                          G = H1 ∨ · · · ∨ Hk ,
where ∨ denotes the complete join. Then α(G) = 2, and the N diagonal words form an
independent set in G⊠k . Thus Θ(G) ≥ N 1/k . Taking N = Rk (3) − 1 and applying (4),



                                                   230
we obtain graphs with independence number 2 and arbitrarily large Shannon capacity. In
particular, Shannon capacity cannot be bounded above by any function of the independence
number.
1.1. Proof outline. The argument adapts the random-matrix and coordinate-covering in-
gredients of Alon, Ben-Eliezer, Shangguan, and Tamo [ABST20, Lemmas 3.4 and 4.1]. Their
saturated-matrix argument in turn builds on work of Chakraborty, Radhakrishnan, Raghu-
nathan, and Sasatte on zero-error list decoding [CRRS06]. We give direct proofs of the
matrix and two-sided coordinate-covering statements without the hat-guessing terminology.
The saturated-matrix construction is not new; its application to R(3, . . . , 3) is.
   Fix a stage parameter H. A union bound produces an H-colored s × H m matrix, where
m ≍ H log H and s ≍ H 2 log2 H, such that among any m+1 columns some row contains every
color. This property yields maps f, g : [H]s → [H]s , ﬁxed once for the entire construction,
such that for every x, y ∈ [H]s there is a d ∈ [s] with
                                                                  
                             xd = f (y) d       or      yd = g(x) d .
   We construct an edge-coloring recursively while maintaining the stronger invariant that, at
stage j, each color graph is properly (j +1)-colorable. Divide the vertices into blocks indexed
by palettes P ⊆ [jt] of size t = s⌈log H⌉. The palette P records the colors missing from its
block; all other colors are active. Inside that block, place a copy of the preceding coloring
with colors relabeled by [jt] \ P . Each active color then has a proper internal vertex labeling
in [j]. A maximal packing provides many palettes while ensuring that distinct palettes diﬀer
in at least s colors in each direction.
   For blocks P < Q, choose colors a1 , . . . , as ∈ Q \ P and b1 , . . . , bs ∈ P \ Q. The internal
labels of u ∈ VP in the ad and of v ∈ VQ in the bd form words     
                                                                           x(u), y(v) ∈ [H]s . Apply
the ﬁxed coordinate cover to these words: if xd (u) = f (y(v)) d , color uv with ad ; otherwise
                                                   
color it with a bd for which yd (v) = g(x(u)) d . Every cross-edge color is therefore active
at exactly one endpoint block and missing at the other. Crucially, the proper label at the
active endpoint is determined by the opposite endpoint.
   This last property excludes triangles on two blocks: two edges of the same color from one
outside vertex into an active block force the same internal label, so the edge between their
endpoints cannot have that color. If the color is missing from the block, there is no internal
edge of that color in the ﬁrst place. A triangle on three blocks would require a color to belong
to each of P △Q, Q△R, and P △R: by symmetry, if c ∈ P , the ﬁrst two memberships give
c∈/ Q and c ∈ R, contradicting the third. Finally, label each active block using its proper
internal labels and each missing block with the new label j + 1. Since every cross edge of
a ﬁxed color joins an active block to a missing block, these labels properly color its entire
color graph and propagate the inductive invariant.
   Multiplying the sizes of the packed palette families over the H stages gives a triangle-free
coloring with kH ≍ H 3 log3 H colors and at least (c0 H)kH vertices. Rounding down to the
nearest such color count changes only the absolute constant. Since H ≫ k 1/3 / log k, this
proves (3) for all suﬃciently large k; decreasing the constant covers the remaining k ≥ 2.
   All logarithms are natural, [r] = {1, . . . , r}, and [0] is empty. We do not optimize the
absolute constants.

              2. Saturated matrices, coordinate covers, and palettes
   We ﬁrst show that, in a thin, wide matrix randomly colored with H colors, every suﬃciently
large set of columns contains a row in which all H colors appear. This is the saturated-
matrix construction of [ABST20, Lemma 3.4], whose underlying family was studied earlier
in [CRRS06].
Lemma 2.1. Let H ≥ 2, and deﬁne
                            m = ⌈2H log H⌉,          s = m(m + 1) + 1.                          (5)



                                                231
There is a matrix
                         A = (Ar,z )r∈[s], z∈[H]m with Ar,z ∈ [H]
such that, for every T ⊆ [H] with |T | = m + 1, some row r ∈ [s] satisﬁes
                            m

                                        {Ar,z : z ∈ T } = [H].                                       (6)
Proof. Choose all entries independently and uniformly from [H]. For a ﬁxed set T of m + 1
columns, a given row fails (6) only if one of the H symbols is absent. Hence
                                                                                 
                                                1 m+1                m       1
            P {Ar,z : z ∈ T } ̸= [H] ≤ H 1 −             < H exp −        ≤ .
                                                H                     H      H
                                                                         −s
Independence bounds the probability that all s rows fail for this T by H . Since there are
        Hm
at most m+1   ≤ H m(m+1) choices of T , a second union bound gives a total failure probability
at most
                                   H m(m+1)−s = H −1 < 1.
Thus one matrix works simultaneously for all sets of m + 1 columns.                         □
   The next lemma converts this matrix property into a two-sided coordinate cover. One
function handles all but a small exceptional set of words; the other handles the remaining
words by assigning them distinct coordinates. The construction adapts [ABST20, Lemma 4.1]
to the present symmetric formulation.
Lemma 2.2 (Two-sided coordinate cover). For H, m, s as in (5), there are ﬁxed maps
                                         f, g : [H]s −→ [H]s
such that, for every x, y ∈ [H]s ,
                                                                          
                          ∃d ∈ [s] : xd = f (y) d          or   yd = g(x) d .                        (7)
Proof. Fix a matrix A from Lemma 2.1. Write x̄ = (x1 , . . . , xm ), and set
                                            
                                     g(x) r = Ar,x̄         (r ∈ [s]).                               (8)
For y ∈ [H]s , let
                       Ey = {z ∈ [H]m : Ar,z ̸= yr for every r ∈ [s]}.                  (9)
Then |Ey | ≤ m. Otherwise take m + 1 members of Ey . The matrix property gives a row
containing every symbol on those columns and, in particular, a column z for which Ar,z = yr
for some r, contrary to (9).
   Enumerate Ey in a ﬁxed order as z (1) , . . . , z (ρ) , where ρ ≤ m, and deﬁne
                                                 ( (d)
                                                 zd , 1 ≤ d ≤ ρ,
                                     f (y) d =
                                                  1,   ρ < d ≤ s.
The ﬁrst case makes sense because d ≤ ρ ≤ m. If x̄ ∈
                                                   / Ey , then (9) and (8) give some d ∈ [s]
such that                                            
                                  yd = Ad,x̄ = g(x) d .
If instead x̄ ∈ Ey , then x̄ = z (d) for some d ≤ ρ, and
                                                 (d)            
                                        xd = zd = f (y) d .
In either case, (7) follows.                                                                          □
  We next pack the palettes that will specify the colors missing from each block. Fix H ≥ 3,
use the parameters of (5), and put
                           t = s⌈log H⌉,          Mj = jt       (0 ≤ j ≤ H).                        (10)
                                                                         [Mj ]
In particular, t ≥ 2s. At stage j, a palette is a member of                t .    A block with palette P
will omit exactly the colors in P .




                                                     232
Lemma 2.3 (Separated palettes). For every 1 ≤ j ≤ H, there is a family
                                                                    !
                                                                [jt]
                                                     Pj ⊆
                                                                 t
such that distinct P, Q ∈ Pj satisfy
                                             |P \ Q| = |Q \ P | ≥ s.                                                   (11)
Writing Bj = |Pj |, one can arrange that Bj ≥ 1 and
                                                   jt
                                                                                jt
                             Bj ≥ s−1        !      t
                                                                ! ≥                    s .                            (12)
                                   X         t      (j − 1)t            s e2 j⌈log H⌉2
                                   d=0
                                             d         d
Proof. Take a maximal family satisfying (11). Every t-subset of [jt] then lies at diﬀerence
less than s from at least one selected palette. Counting these covering balls gives the ﬁrst
inequality in (12). Since t = s⌈log H⌉ ≥ 2s, the estimates
                  !                      !                  !           !     !                  !               r
             jt                X
                               s−1
                                        t        (j − 1)t          t        jt               N               eN
                      ≥j ,
                        t
                                                                ≤s             ,                     ≤
              t                d=0
                                        d           d              s        s                r                r
immediately give the second inequality in (12). A maximal family is nonempty, so Bj ≥ 1. □

                             3. Recursive triangle-free colorings
   For an edge-coloring κ, write Γκ (c) for the spanning graph whose edges are those of color
c. We construct colorings for which every Γκ (c) has a short proper vertex coloring. This
stronger invariant is what makes a triangle-free recursion possible.
Proposition 3.1 (Recursive coloring). Fix H ≥ 3, let t and Mj be as in (10), and, for
1 ≤ r ≤ H, let Pr be a palette family provided by Lemma 2.3. Write Br = |Pr |. For each
0 ≤ j ≤ H, there is a coloring
                                                                                Y
                                                                                j
                               κj : E(Knj ) −→ [Mj ],                    nj =         Br ,
                                                                                r=1
with the following properties:
    (1) κj contains no monochromatic triangle;
    (2) for each c ∈ [Mj ],                 
                                  χ Γκj (c) ≤ j + 1.
Proof. Fix once and for all the maps f, g : [H]s → [H]s provided by Lemma 2.2; the same
pair will be used at every stage and for every pair of blocks. For j = 0, take the edgeless
graph on one vertex. Suppose the statement holds at stage j − 1, and order Pj once and for
all.
Internal edges and labels. For every P ∈ Pj , take a block VP of nj−1 vertices. Since
                                        |[Mj ] \ P | = (j − 1)t = Mj−1 ,
place a copy of κj−1 on VP , relabeling its color set bijectively by [Mj ] \ P . A color c is active
on VP if c ∈/ P and missing if c ∈ P . For each active c, the inductive invariant supplies a
proper coloring
                                         ℓPc : VP −→ [j]
of the internal graph of color c. In particular,
                        κj (uu′ ) = c       =⇒       ℓPc (u) ̸= ℓPc (u′ )         (u, u′ ∈ VP ).                       (13)
Cross edges. For each ordered pair P < Q, ﬁx distinct colors
                              a1 , . . . , as ∈ Q \ P,            b1 , . . . , bs ∈ P \ Q,



                                                            233
which is possible by Lemma 2.3. The ad are active on VP and missing on VQ ; the bd have
the opposite status. For u ∈ VP and v ∈ VQ , form
                                          s                           s
                          x(u) = ℓPad (u) d=1 ,          y(v) = ℓQ
                                                                 bd (v) d=1 .
These belong to [H]s because
                               j ≤ H.
   If xd (u) = f (y(v)) d for some d, assign uv the color ad for the least such d. Otherwise
                                                
Lemma 2.2 supplies a d with yd (v) = g(x(u)) d ; assign uv the color bd for the least such d.
In particular,
                                       κj (uv) ∈ P △ Q.                                 (14)
More importantly, the label at the active endpoint is determined by the opposite endpoint:
                                                                         
                           κj (uv) = ad       =⇒     ℓPad (u) = f (y(v)) d ,                      (15)
                                                                         
                           κj (uv) = bd       =⇒     ℓQ
                                                      bd (v) = g(x(u)) d .                        (16)
Triangles in one or two blocks. A triangle inside one block is not monochromatic by induction.
Suppose next that u, u′ ∈ VP and v ∈ VQ , with κj (uv) = κj (u′ v) = c. If c ∈ P , the color is
missing internally on VP , so κj (uu′ ) ̸= c.
   If instead c ∈
                / P , it is active on VP . When P < Q, the distinctness of the ad gives a unique
d with c = ad , and (15) yields
                                                         
                                  ℓPc (u) = f (y(v)) d = ℓPc (u′ ).
When Q < P , the distinctness of the relevant bd and (16) give exactly the same conclusion.
Now (13) shows that the internal edge uu′ cannot have color c.
Triangles in three blocks. Suppose a triangle of color c meets three distinct blocks VP , VQ , VR .
By (14),
                           c ∈ P △Q,      c ∈ Q△R,        c ∈ P △R.
By symmetry, suppose c ∈ P . The ﬁrst inclusion gives c ∈     / Q, and the second then gives
c ∈ R. But this contradicts c ∈ P △R. The coloring is therefore triangle-free.
The next proper-coloring invariant. For a ﬁxed c ∈ [Mj ], deﬁne
                                          (
                                           ℓPc (v), v ∈ VP , c ∈
                                                               / P,
                               Lc (v) =
                                           j + 1, v ∈ VP , c ∈ P.
Inside an active block, Lc properly colors the c-edges; inside a missing block, there are no
c-edges. By (14), every cross edge of color c joins an active block to a missing block. Its
endpoints therefore receive labels in [j] and {j + 1}, respectively. Thus Lc is a proper (j + 1)-
coloring of Γκj (c). Finally, the Bj blocks each have nj−1 vertices, proving nj = Bj nj−1 and
completing the induction.                                                                      □
Proof of Theorem 1.1. By decreasing c, it suﬃces to prove (3) for suﬃciently large k. For
H ≥ 3, write
                                                                
     m(H) = ⌈2H log H⌉,          s(H) = m(H) m(H) + 1 + 1,                   kH = Hs(H)⌈log H⌉.
These special color counts satisfy kH ≍ H 3 log H and kH+1 /kH = 1 + O(1/ log H). If
                                                         3

kH ≤ k < kH+1 , monotonicity therefore shows that a bound RkH (3) ≥ (c0 H)kH implies
Rk (3) ≥ (c1 H)k for another absolute constant c1 > 0: the factor kH /k = 1 − O(1/ log H)
changes log(c0 H) by only an additive constant. Moreover, k < kH+1 = O(H 3 log3 H) implies
H ≫ k 1/3 / log k. Hence, after decreasing c again, it suﬃces to consider
                                      k = kH = Hs⌈log H⌉
for suﬃciently large H, where s = s(H).




                                                   234
                                                                             Q
  At stage H, Proposition 3.1 produces a triangle-free k-coloring on H j=1 Bj vertices. Recall
that t = s⌈log H⌉, s = O(H 2 log2 H), k ≍ H 3 log3 H, and log(H!) ≥ H log H − H. Multi-
plying (12) therefore gives, for suﬃciently large k and a suﬃciently small absolute constant
c > 0,
                                                                  !k
                                        (H!)t−s            ck 1/3
                          Rk (3) ≥                 sH ≥             .
                                    sH e2 ⌈log H⌉2         log k
This proves (3). Since k 1/3 / log k → ∞, (4) follows.                                                 □

                                             References
[ACPPRT21] R. Ageron, P. Casteras, T. Pellerin, Y. Portella, A. Rimmel, and J. Tomasik, New lower bounds
           for Schur and weak Schur numbers, 2021, arXiv:2112.03175.
[ABST20]   N. Alon, O. Ben-Eliezer, C. Shangguan, and I. Tamo, The hat guessing number of graphs,
           J. Combin. Theory Ser. B 144 (2020), 119–149, doi:10.1016/j.jctb.2020.01.003; see also
           arXiv:1812.09752.
[AO95]     N. Alon and A. Orlitsky, Repeated communication and Ramsey graphs, IEEE Trans. Inform.
           Theory 41 (1995), 1276–1289.
[Blo183]   T. F. Bloom, Erdős problem #183, https://www.erdosproblems.com/183; see also https://
           www.erdosproblems.com/latex/183.
[CRRS06]   S. Chakraborty, J. Radhakrishnan, N. Raghunathan, and P. Sasatte, Zero error list-decoding
           capacity of the q/(q − 1) channel, in Foundations of Software Technology and Theoretical Com-
           puter Science, Lecture Notes in Comput. Sci. 4337, Springer, 2006, 129–138.
[Chu73]    F. R. K. Chung, On the Ramsey numbers N (3, 3, . . . , 3; 2), Discrete Math. 5 (1973), 317–321,
           doi:10.1016/0012-365X(73)90125-8.
[CG]       F. Chung and R. Graham, Multi-color Ramsey number for triangles, in Erdős Problems, https:
           //mathweb.ucsd.edu/~erdosproblems/erdos/newproblems/MulticolorR3.html.
[CG83]     F. R. K. Chung and C. M. Grinstead, A survey of bounds for classical Ramsey numbers, J.
           Graph Theory 7 (1983), 25–37, doi:10.1002/jgt.3190070105.
[CFS15]    D. Conlon, J. Fox, and B. Sudakov, Recent developments in graph Ramsey theory, in Surveys in
           Combinatorics 2015, London Math. Soc. Lecture Note Ser. 424, Cambridge University Press,
           2015, arXiv:1501.02474.
[EMT71]    P. Erdős, R. J. McEliece, and H. Taylor, Ramsey bounds for graph products, Paciﬁc J. Math.
           37 (1971), 45–46.
[Exo94]    G. Exoo, A lower bound for Schur numbers and multicolor Ramsey numbers, Electron. J. Com-
           bin. 1 (1994), R8.
[FS00]     H. Fredricksen and M. M. Sweet, Symmetric sum-free partitions and lower bounds for Schur
           numbers, Electron. J. Combin. 7 (2000), R32.
[Gow00]    W. T. Gowers, Rough structure and classiﬁcation, Geom. Funct. Anal., Special Volume, Part I
           (2000), 79–117; reprinted in Visions in Mathematics, Birkhäuser, 2010, doi:10.1007/978-3-0346-
           0422-2_4.
[GRS90]    R. L. Graham, B. L. Rothschild, and J. H. Spencer, Ramsey Theory, 2nd ed., Wiley-Interscience,
           1990.
[GG55]     R. E. Greenwood and A. M. Gleason, Combinatorial relations and chromatic graphs, Canad. J.
           Math. 7 (1955), 1–7, doi:10.4153/CJM-1955-001-4.
[Rad]      S. P. Radziszowski, Small Ramsey numbers, Electron. J. Combin., Dynamic Survey DS1, https:
           //www.combinatorics.org/ojs/index.php/eljc/article/view/DS1.
[Wan97]    H. Wan, Upper bounds for Ramsey numbers R(3, 3, . . . , 3) and Schur numbers, J. Graph Theory
           26 (1997), 119–122.
[Whi73]    E. G. Whitehead, Jr., The Ramsey number N (3, 3, 3, 3; 2), Discrete Math. 4 (1973), 389–396.
[XXC02]    X.-D. Xu, Z. Xie, and Z. Chen, Upper bounds for Ramsey numbers Rn (3) and Schur numbers,
           Math. Econ. 19 (2002), 81–84.




                                                  235
