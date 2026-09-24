# Circuit and Formula Lower Bounds for the Permanent

> Source: OpenAI, *Ten Advances in Mathematics and Theoretical Computer Science*, Chapter 5, PDF pages 118–157. Layout-preserving text extraction; consult the source PDF for authoritative equation rendering.

                                    Chapter 5

Circuit and Formula Lower Bounds for the
               Permanent
    Abstract. We study the exact symbolic computation of the n × n permanent
    over C by arithmetic circuits and formulas. We prove two lower bounds.
       • Division-free circuits with unrestricted reuse of intermediate values require
         Ω(n2 log log n) arithmetic gates.
       • Arithmetic formulas require Ω(n4 / log n) variable-labeled leaves, even when
         division is allowed provided all denominators are nonzero rational functions.
       The proof of the circuit lower bound constructs an aﬀine specialization whose
    gradient vanishes on a suﬀiciently low-dimensional set, then combines simulta-
    neous differentiation with a geometric degree bound. The formula lower bound
    proof identifies many algebraically independent coeﬀicients associated with a
    short matching of matrix entries and adds the resulting requirements over entry-
    disjoint matchings. We also explain how both arguments use properties of the
    permanent and do not directly imply a similar result for the determinant.



                                       Contents
1. Introduction
2. Overview of the circuit lower bound
3. Overview of the formula lower bounds
4. A geometric circuit bound
5. Critical loci of minor sums
6. An aﬀine specialization of the permanent
7. Circuit parameters and the lower bound
8. Coeﬀicient transcendence degree
9. Independent coeﬀicients from a matching
10. Formula lower bounds with and without division
11. Comparison with the determinant
12. Related work
References




                                           114
                                        1. Introduction
  Fix an integer n ≥ 1, and let X = (xij )i,j∈[n] be an n × n matrix of algebraically independent
variables over C, where [j] = {1, . . . , j}. The permanent of X is the polynomial
                                                     X Y
                                                       n
                                     pern (X) =               xi,σ(i) .
                                                  σ∈Sn i=1

Here Sn is the set of permutations of [n]. Thus a monomial of pern chooses exactly one entry
from each row and each column; equivalently, it records a perfect matching in the complete
bipartite graph on the row and column indices. The closely related determinant is
                                             X                Y
                                                              n
                                det(X) =             sgn(σ)         xi,σ(i) ,
                                 n
                                             σ∈Sn             i=1

which differs from the permanent only through the signs of its monomials. Nevertheless, the
determinant has polynomial-size arithmetic circuits [Ber84], whereas the permanent is complete
for Valiant’s class VNP [Val79a]. Understanding whether the permanent admits polynomial-
sized algebraic circuits is the central problem in algebraic complexity theory [BCS97, SY10].
   Throughout, “compute” means compute the polynomial exactly as a formal expression over
C, not merely evaluate it on a particular input matrix. An arithmetic circuit is a finite directed
acyclic graph with input gates labeled by individual variables or arbitrary complex constants,
binary internal gates labeled by +, −, or ×, and one designated output gate. Intermediate
values may be reused arbitrarily: a gate can feed its output to any number of later gates.
The circuit is division-free, and its size is the number of arithmetic gates; input gates are not
counted. We write C(f ) for the minimum size of a circuit whose output is the polynomial f .
There are no restrictions on depth, intermediate degrees, fan-out, or cancellations.
   An arithmetic formula has the same kinds of inputs and binary arithmetic gates, but its
underlying computation is a rooted tree. Consequently, two uses of the same intermediate
polynomial must be computed by separate subformulas. For a formula Φ, let L(Φ) be its
total number of leaves, let Lvar (Φ) count only the leaves labeled by variables, with repeated
occurrences counted separately, and let G(Φ) be its number of internal arithmetic gates. A
formula with division additionally permits ÷ gates and is interpreted in the rational-function
field C(xij : i, j ∈ [n]). Such a formula is valid if every denominator is a nonzero element of
this field. Its final output is required to equal the polynomial being computed; in particular,
intermediate rational functions need not themselves be polynomials.
   The permanent depends on all N = n2 matrix variables, giving the elementary Ω(N ) circuit
lower bound. The classical division-free formula lower bounds for the permanent and determi-
nant are Ω(n3 ) [KS14, §3.2, Thm. 5]; for the determinant, Kalorkoti’s cubic lower bound holds
even when division is allowed [Kal85]. Our first result improves the unrestricted, division-free
circuit lower bound specifically for the permanent.
Theorem 1.1. For every n ≥ 216 ,
                                             n2                
(1.1)                           C(pern ) ≥      log2 log2 n − 3 .
                                            144
In particular, C(pern ) = Ω(n2 log log n) and C(pern )/n2 −→ ∞.
  The next result concerns the more restrictive formula model. Its primary measure is the
number of variable occurrences, which also lower-bounds the total number of leaves and vertices.
Theorem 1.2. If n ≥ 32 and a division-free arithmetic formula Φ computes pern , then
                                         n4                               n4
                         Lvar (Φ) ≥              ,       G(Φ) ≥                   .
                                      128 log2 n                       256 log2 n
The variable-leaf bound also holds for the total numbers of leaves and vertices.
  The same asymptotic variable-occurrence bound remains true when a formula may use valid
divisions; the explicit constants change.


                                                  115
Theorem 1.3. If n ≥ 32 and a valid arithmetic formula Φ with division computes pern , then
                                              n4                             n4
                            Lvar (Φ) ≥                ,        G(Φ) ≥                .
                                           192 log2 n                     384 log2 n
Again, the variable-leaf bound holds for the total numbers of leaves and vertices.
   In terms of the N = n2 input variables, the circuit bound is Ω(N log log N ), and both for-
mula bounds are Ω(N 2 / log N ). The circuit and formula results use different arguments: circuits
permit eﬀicient simultaneous computation of first derivatives because intermediate values can
be reused, whereas the formula bounds charge algebraically independent coeﬀicients to dis-
tinct occurrences of selected input variables. The permanent-specific inputs required by these
arguments are not available for the determinant; §11 identifies both obstructions.

                           2. Overview of the circuit lower bound
   Our circuit lower bound combines a geometric measure of polynomial complexity with a
permanent-specific construction. The measure applies to a homogeneous polynomial whose
gradient vanishes on a suﬀiciently small set; the construction realizes such a polynomial by
fixing and identifying inputs of pern . We describe both components, illustrate the necessary
cancellation on a four-by-four permanent, and give complete proofs in §4–§7.
Stage 1: Many solutions force many multiplication gates. Consider the homogeneous
polynomial
                                      1X k
              H(z1 , . . . , zk ) =        zd,        ∇H(z) = (z1d−1 , . . . , zkd−1 ),   d ≥ 2.
                                      d i=1 i
For a target whose coordinates are all nonzero, the gradient has (d − 1)k distinct preimages. If
aﬀine operations are free, a circuit using q multiplication gates describes the same fiber by q
quadratic gate equations and k aﬀine output equations. Bézout’s inequality bounds its number
of isolated solutions by 2q . Reverse-mode differentiation computes the gradient of a size-L
circuit with at most 3L multiplications [BS83]. Consequently,
                                                        k log2 (d − 1)
                                 (d − 1)k ≤ 23L ,           L≥         .
                                                               3
Section 4 supplies the full gate-equation and reverse-mode differentiation arguments.
   The advantage of this argument is that it does not require the coordinates of the gradient to
be individual powers. The same solution count holds for any homogeneous map F : Ck → Ck
of degree d − 1 whose only zero is the origin: its generic fiber consists of (d − 1)k points. This
extension, proved in Lem. 4.1, is what allows the degree argument to apply to a polynomial
obtained from the permanent.
Stage 2: A small critical locus produces the required gradient map. Let P ∈
C[x1 , . . . , xm ] be a homogeneous polynomial of degree d. Its critical locus is
                       Crit(P ) = {x ∈ Cm : ∂P/∂x1 = · · · = ∂P/∂xm = 0}.
Its dimension measures the number of freely varying coordinates in the common zero set; its
codimension is m − dim Crit(P ). In particular, a critical locus of codimension at least k is small
enough for a generic k-dimensional linear subspace to meet it only at the origin.
   Choose a linear injection W : Ck → Cm whose image is such a subspace. Then ∇P (W u) 6= 0
whenever u 6= 0. A second generic linear map A : Cm → Ck preserves this nonvanishing on the
entire family of gradient directions. Therefore
                                             F (u) = A∇P (W u)
is a homogeneous degree-(d − 1) map from Ck to itself with F −1 (0) = {0}. Lem. 4.2 justifies the
two generic choices. Linear maps cost no multiplications, so combining slicing, reverse-mode
differentiation, and the preceding Bézout bound gives
                                                      k log2 (d − 1)
                                                 L≥
                                                             3

                                                        116
for any circuit computing P . Proposition 4.3 records the same implication when P is a nonzero
scalar multiple of an aﬀine specialization of pern : replacing the permanent’s inputs by aﬀine
linear forms transfers its circuit to P without adding multiplication gates.
   To obtain a superquadratic lower bound, it therefore suﬀices to construct a degree-d special-
ization with d growing with n and with k = Θ(n2 ). A direct application to the full permanent
does not supply the needed codimension. The remaining stages construct a different specializa-
tion whose critical locus can be controlled.
Stage 3: Control the critical locus of a sum of subpermanents. For a t × s matrix
X = (xia ) and 3 ≤ d ≤ min{t, s}, define
                                                     X
                                Mt,s,d (X) =                    per(XI,J ).
                                                 I⊆[t], J⊆[s]
                                                  |I|=|J|=d

Thus Mt,s,d sums the weights of all size-d matchings between t row vertices and s column
vertices. It is homogeneous of degree d in ts variables.
  For each nonempty subset B ⊆ [t], introduce the power sum
                                                     X
                                                     s Y
                                       pB (X) =                 xia .
                                                     a=1 i∈B

There are 2t − 1 such quantities, shared by every column. To differentiate Mt,s,d with respect to
xia , first insist that row i is matched to column a. The remaining d − 1 rows must be matched
injectively to columns other than a. Inclusion–exclusion on partitions expresses this injectivity
requirement as a polynomial in the pB (X) and the entries of column a.
   Section 5 uses these derivative equations together with the first d − 2 elementary symmetric
functions of each column. Once the 2t − 1 shared power sums and these s(d − 2) additional
quantities are specified, the critical-point equations leave only finitely many possibilities for
the column entries. Algebraically, those equations reduce every (d − 1)st power of a column
coordinate to expressions of lower column degree. Repeated reduction makes the coordinate
algebra finite over the ring generated by the specified quantities. This yields the dimension
bound
                                  dim Crit(Mt,s,d ) ≤ 2t − 1 + s(d − 2).
If b copies occupy disjoint variable blocks and receive nonzero scalar weights, their critical loci
form a Cartesian product. Corollary 5.2 therefore bounds the resulting dimension by
                                                                  
                                       b 2t − 1 + s(d − 2) .
Stage 4: Realize the desired block polynomial inside the permanent. Partition r = bt
rows into blocks R1 , . . . , Rb of size t, and let X be an r × s matrix of variables. We want the
polynomial
                                     X
                                     b
                           P (X) =         λh Mt,s,d (XRh ,[s] ),       λh 6= 0,
                                     h=1
so that the preceding critical-locus estimate applies. The challenge is to realize this specific sum
as one permanent, rather than as a separate sum of circuits.
A four-by-four cancellation example. The required block-selective cancellation is already visible
in                                        
                             u v 1 1
                           w z 1 1 
                       per                
                            p q 2 −2 = −8(uz + vw) + 2(ps + qr).
                             r s 2 −2
Expand according to the two rows assigned to the first two columns. If both chosen rows belong
to the upper block, their variable contribution is per ( wu vz ) = uz + vw, while the complementary
constant block has permanent
                                                  
                                              2 −2
                                        per           = −8.
                                              2 −2


                                                   117
If both chosen rows belong to the lower block, the variable contribution is ps + qr, and the
complementary constant block has permanent
                                                             
                                                   1 1
                                               per     = 2.
                                                   1 1
If one chosen row comes from each block, the complementary constant block likewise contains
one row of each type, and its permanent vanishes:
                                                     
                                           1 1
                                       per      = −2 + 2 = 0.
                                           2 −2
Thus every mixed-block contribution cancels, leaving precisely the two within-block permanents.
The example has degree d = 2, so log2 (d − 1) = 0 and it cannot itself produce a useful circuit
lower bound. Its purpose is to exhibit the cancellation that the general construction must
reproduce at a larger degree.
The general specialization. Lemma 6.1 constructs a constant r × (r − d) matrix U for which
                                                                 
                                                    X U
                                             B(X) =
                                                    1 0
is square of size r + s − d; the bottom-left all-ones block has s − d rows. Every nonzero term
of per(B(X)) chooses exactly d entries from X. The contribution of a chosen set of d variable
rows is controlled by a complementary permanent of U .
    The columns of U P      are chosen using dth roots of unity. In commuting square-zero variables
z1 , . . . , zr , write yh = i∈Rh zi . For h ≥ 2, set Y = y1 + · · · + yh−1 , and let ζ be a primitive dth
root of unity. The corresponding root-of-unity product has the form
                                Y
                                d−1
                                      (Y + 2ζ j yh ) = Y d + (−1)d+1 2d yhd .
                                j=0

Combining these factors across the blocks forces every contributing set of d variable rows to lie
entirely inside a single Rh ; choices meeting several blocks cancel. All surviving block weights
are nonzero. Thus per(B(X)) is a nonzero scalar multiple of P (X). Section 6 proves the
construction and computes its nonzero block weights.
Stage 5: Choose the degree and count the surviving variables. Section 7 takes
                                                           
                log2 n                              n
             d=        ,          t = 4d,        b=    ,              r = bt,   s = n − r + d.
                  4                                 2t
Then B(X) has size n and X contains m = rs = Θ(n2 ) independent variables. The choice
t ≤ log2 n keeps 2t at most n, while d = t/4 keeps the columnwise contribution bs(d − 2) below
m/4. The full critical-locus bound is therefore smaller than m/2, permitting a slice of dimension
k = bm/4c = Θ(n2 ). Stage 2 now gives
                                            k log2 (d − 1)
                              C(pern ) ≥                   = Ω(n2 log log n).
                                                   3
The quantitative bookkeeping in Proposition 7.1 gives the explicit constant in Theorem 1.1.


                         3. Overview of the formula lower bounds
  The formula bounds exploit the fact that a formula is a tree: unlike a circuit, it cannot
reuse a computation in several places. Our strategy identifies many small, disjoint groups of
matrix entries whose influence on the permanent is individually rich. Each group forces many
occurrences of its variables in any formula, and disjointness allows us to add these requirements.
We first describe the measure of influence, then the matching construction that makes the
measure large, and finally the packing and the extension to division.


                                                      118
Stage 1: Measuring information in a group of variables. Let Y be a nonempty set of variables of
a polynomial f ∈ C[Y, Z], where Z denotes all remaining variables. Expanding in the variables
of Y gives
                                     X
                               f=          cα (Z)Y α ,       cα (Z) ∈ C[Z].
                                    α∈NY

We measure how much independent information these coeﬀicients contain by
                                                                                   
                                tdY (f ) = trdegC C cα (Z) : α ∈ NY .
Here polynomials c1 , . . . , cr ∈ C[Z] are algebraically independent if no nonzero polynomial
H ∈ C[T1 , . . . , Tr ] satisfies H(c1 , . . . , cr ) = 0. For example, independent variables z1 , z2 are
algebraically independent, whereas z1 , z12 are dependent because T2 − T12 vanishes after sub-
stituting these two polynomials. The transcendence degree above is the maximum number of
algebraically independent coeﬀicient polynomials. It counts independent parameters, not merely
the number of distinct or linearly independent coeﬀicients.
   For a formula Φ, let tY (Φ) be the number of leaves labeled by variables from Y , counting
repeated occurrences. Section 8 proves that every division-free formula computing f satisfies
(3.1)                     tdY (f ) ≤ 4tY (Φ) − 2 ≤ 4tY (Φ),             tY (Φ) ≥ 1.
The reason is that any subformula containing no Y -variable computes a polynomial in Z. Along
a path where only one child contains a Y -variable, the other child therefore modifies the marked
computation by an aﬀine map u 7→ Au + B, with A, B ∈ C[Z]. An entire such path remains
a single aﬀine map. Only a gate with two Y -containing children combines genuinely different
marked computations. The tree connecting tY (Φ) marked leaves has at most tY (Φ) − 1 such
branching gates, and each gate introduces at most four coeﬀicient parameters; the final aﬀine
map contributes two more. Consequently, all coeﬀicients of f belong to a field generated by at
most 4tY (Φ) − 2 quantities. This step turns algebraic independence into a direct lower bound
on variable occurrences.
Stage 2: Obtaining quadratically many independent coeﬀicients from a logarithmic-size match-
ing. A matching Y in the n × n variable matrix X is a set of entries with no repeated row or
column. Set
                              ` = dlog2 ne,       k = 2`,        m = n − k,
and choose a matching of k entries. For n ≥ 32, we have m ≥ n/2, so m2 = Ω(n2 ) even though
|Y | = O(log n). After permuting rows and columns, suppose that the marked variables are
Y = {yi = xii : i ∈ [k]}. Since the permanent is multilinear, its expansion takes the particularly
simple form
                                                  X                   Y
                                  pern (X) =            cS (X \ Y )         yi .
                                                S⊆[k]                 i∈S

The coeﬀicient cS sums the permutation terms using exactly the marked diagonal entries indexed
by S. Equivalently, delete their rows and columns and set every other marked entry to zero.
  The key assertion, proved in Section 9, is
(3.2)                                       tdY (pern ) ≥ m2 .
To see what must be shown, divide the k marked indices into two sets E and F of size `. For
each pair 0 ≤ α, β < m, let P (α) ⊆ E and Q(β) ⊆ F encode the binary digits of α and β,
respectively, and set
                                                                            
                                    S(α, β) = [k] \ P (α) ∪ Q(β) .
Because m ≤ 2` , these choices specify m2 distinct coeﬀicients cS(α,β) . Separate the marked and
unmarked row and column indices by writing
                                             
                                         D U
                               X=            ,           W = (wab )a,b∈[m] .
                                         V W


                                                   119
Here D uses the k internal indices, W uses the m external indices, and U, V connect the two
groups. We establish algebraic independence by showing that the square Jacobian
                                                         
                                               ∂cS(α,β)
                                                ∂wab          (α,β),(a,b)

is invertible at one explicit assignment of the unmarked variables. The characteristic-zero
Jacobian criterion then proves (3.2).
   The assignment uses distinct complex numbers p1 , . . . , pm and, independently, distinct com-
plex numbers q1 , . . . , qm . Set the internal off-diagonal entries to zero and every wab to one. If
eu ∈ E and fv ∈ F correspond to binary positions u, v ∈ {0, . . . , ` − 1}, assign
                               u                                                      v
                    Ueu ,b = p2b ,       Ufv ,b = 1,           Va,eu = 1,   Va,fv = qa2
to the internal-to-external and external-to-internal entries, respectively. The derivative with
respect to wab fixes the external matching edge (a, b). Because all other external entries are
one, the remaining weighted choices separate into an external column choice depending only on
pb and an external row choice depending only on qa . More precisely, the evaluated Jacobian has
entries
                               Lα,β gα (pb )hβ (qa ),  Lα,β 6= 0,
where gα and hβ are univariate polynomials of exact degrees α and β, respectively. Thus
the p-evaluation and q-evaluation matrices are Vandermonde matrices multiplied by invertible
triangular change-of-basis matrices. Their Kronecker product, and hence the whole Jacobian,
is invertible. The 5 × 5 example at the beginning of Section 9 illustrates this row–column
separation before the general construction.
Stage 3: Packing matchings and summing their costs. One matching now forces at least m2 /4
occurrences of its k variables by (3.1) and (3.2). To obtain the full formula bound, Section 10
partitions many of the n2 matrix entries into pairwise entry-disjoint matchings of size k. Index
rows and columns by {0, . . . , n − 1} and, for 0 ≤ τ < n and 0 ≤ j < bn/kc, define
                                     
                             Yτ,j = xjk+r, (jk+r+τ ) mod n : 0 ≤ r < k .
Each Yτ,j is a matching. The row determines j, while the column-minus-row difference modulo
n determines τ , so no matrix entry belongs to two of these matchings. Their number is
                                                     
                                                       n   n2
                                            ν=n          ≥    .
                                                       k   2k
Since their variable sets are disjoint, each variable-labeled leaf is charged at most once. Therefore
                                                                             !
                                         X            νm2     n4
                           Lvar (Φ) ≥     tYτ,j (Φ) ≥     =Ω       .
                                      τ,j
                                                       4     log n

Keeping the explicit inequalities m ≥ n/2 and k ≤ 4 log2 n gives the constant in Theorem 1.2.
The passage to internal-gate bounds uses only the binary-tree identity G(Φ) = L(Φ) − 1.
Stage 4: Allowing valid division. The matching construction and its Jacobian concern the per-
manent itself, so they remain unchanged when the formula contains division gates. Only the
occurrence-charging statement requires a new argument. Put R = C(Z), the field of rational
functions in the unmarked variables. Along a path with one marked child, an unmarked child
now computes an element of R, and all four arithmetic operations transform the marked value
by a fractional linear map
                                      au + b
                                u 7−→        ,   a, b, c, d ∈ R.
                                      cu + d
Validity ensures that the actual denominator is nonzero as a rational function. After dividing
the representing matrix by one of its nonzero entries, the map is described by at most three
parameters; the matrix is not required to be invertible. A gate combining two marked sub-
formulas therefore contributes at most six parameters, and the final map contributes at most
three. This places the output in K(Y ) for a subfield K ⊆ R generated over C by at most
6tY (Φ) − 3 elements.


                                                       120
  There is one additional subtlety: membership in K(Y ) alone does not immediately say that
the coeﬀicients of the output belong to K. However, the output is also the polynomial pern ∈
R[Y ], and the elementary field-intersection identity
                                       K(Y ) ∩ R[Y ] = K[Y ]
recovers precisely that conclusion. Consequently, Section 10 establishes
                                tdY (pern ) ≤ 6tY (Φ) − 3 < 6tY (Φ).
Applying this inequality to the same ν disjoint matchings gives
                                                                !
                                              νm2     n4
                                   Lvar (Φ) ≥     =Ω       ,
                                               6     log n
with the explicit constant of Theorem 1.3. The Jacobian specialization is applied only to
polynomial coeﬀicients of the permanent: a formula denominator need not remain nonzero at
that numerical assignment.

                                4. A geometric circuit bound
   Our goal in this section is to convert a geometric property of a homogeneous polynomial into
an arithmetic circuit lower bound. For a polynomial P ∈ C[x1 , . . . , xm ], its gradient and critical
locus are
                                               
                        ∂P               ∂P
            ∇P (x) =        (x), . . . ,     (x) ,  Crit(P ) = {x ∈ Cm : ∇P (x) = 0}.
                        ∂x1              ∂xm
The critical locus is an aﬀine algebraic set: it consists of the common solutions to finitely
many polynomial equations. Its dimension is, informally, the largest number of algebraically
independent parameters that can vary on one of its components; its codimension in Cm is
m − dim Crit(P ). We will show that when P has degree d and its critical locus has codimension
at least k, computing P requires at least k log2 (d − 1)/3 multiplication gates. The bound then
transfers to the permanent whenever P is an aﬀine specialization of it.
   The argument has three components. First, we bound the complexity of a homogeneous
square polynomial map whose only zero is the origin. Second, we obtain such a map from the
gradient of P by restricting its input to a suitable k-dimensional linear subspace and taking k
linear combinations of its outputs. Finally, we use reverse-mode differentiation to compute this
restricted gradient from a circuit for P .
   Throughout the section, we use the multiplicative-complexity model: aﬀine combinations of
inputs and previously computed results are free, while each binary multiplication costs one.
Since an ordinary size-L arithmetic circuit contains at most L multiplication gates, its multi-
plicative complexity is at most L. Treating aﬀine operations as free will also let us perform
linear changes of variables and linear combinations of outputs without affecting our bounds.
   The first lemma formalizes the gradient warm-up in §2. Its hypothesis that the origin is the
only common zero forces a generic fiber of a homogeneous degree-e polynomial map to have
ek solutions. Conversely, a circuit using q multiplications can describe the same solutions with
only q quadratic equations, which have at most 2q isolated solutions.
Lemma 4.1. Let F = (F1 , . . . , Fk ) : Ck → Ck have homogeneous coordinates of a common
degree e ≥ 1. If F −1 (0) = {0} and a circuit in this model computes all Fi using q multiplications,
then ek ≤ 2q .
Proof. We first count the solutions of F (u) = a for a suitably chosen target a = (a1 , . . . , ak ).
Introducing one additional variable z, homogenize these equations to obtain
(4.1)                              Fi (u) − ai z e = 0,    i ∈ [k],
in projective space Pk .   A point of Pk is a nonzero vector (u1 , . . . , uk , z) considered up to
multiplication by a nonzero scalar. Points with z 6= 0 can be normalized to z = 1 and are
exactly the usual aﬀine solutions of F (u) = a. The remaining points, with z = 0, are the
potential solutions “at infinity.”


                                                 121
   There are no such solutions at infinity: if [u1 : · · · : uk : 0] satisfied (4.1), then u 6= 0
and F (u) = 0, contradicting the hypothesis. Moreover, every positive-dimensional projective
algebraic set intersects every projective hyperplane. Thus a positive-dimensional common zero
set of (4.1) would intersect the hyperplane z = 0, which we have just ruled out. The intersection
is therefore zero-dimensional. Projective Bézout now says that the total number of its points,
counted with their algebraic multiplicities, is the product of the k defining degrees:
                                               e| · e{z· · · e} = ek .
                                                k factors
Since there are no points at infinity, this is also the number of aﬀine solutions counted with
multiplicity.
  To obtain ek distinct solutions, rather than merely ek solutions counted with multiplicity, we
verify that a generic target a has a reduced fiber. Put
                          R = C[u1 , . . . , uk ],        B = C[F1 , . . . , Fk ] ⊆ R.
Because the origin is the only common zero of the Fi , the Nullstellensatz gives
                                      (u1 , . . . , uk )h ⊆ (F1 , . . . , Fk )
for some integer h. In particular, every monomial of total degree at least h belongs to the
ideal generated by the Fi . Since that ideal is homogeneous, a monomial of degree j ≥ h can
be written as a sum of terms Fi Gi , with each nonzero Gi homogeneous of degree j − e < j.
Repeating this reduction expresses every element of R as a B-linear combination of the finitely
many monomials of total degree less than h. Thus R is a finite B-module.
   A finite ring extension preserves Krull dimension, so dim B = dim R = k. Since B is gener-
ated by the k elements F1 , . . . , Fk , this dimension equality also shows that these elements are
algebraically independent. Consequently, B =     ∼ C[y1 , . . . , yk ], and the original map F : Ck → Ck
is a finite dominant morphism: finiteness gives finite fibers, and dominance means that the
image is dense in the target. Characteristic zero rules out inseparability, so generic smoothness
supplies a nonempty open set of targets a whose fibers are reduced, meaning that every solution
has multiplicity one [Har77, Ch. III, Cor. 10.7]. Choose such an a. Its fiber consists of exactly
ek distinct points by the preceding Bézout count.
   We next describe the same fiber using the multiplication gates of the circuit. Order those gates
topologically and introduce a new variable vj for the output of the jth gate. Because additions,
subtractions, and scalar operations are free, its two inputs are aﬀine functions Aj (u, v<j ) and
Bj (u, v<j ) of the original inputs and the preceding multiplication outputs. Its gate equation is
therefore
                                vj = Aj (u, v<j )Bj (u, v<j ),         j ∈ [q].
Similarly, each circuit output is an aﬀine function Hi (u, v), so requiring that the output equal
a adds the equations
                                    Hi (u, v) = ai ,  i ∈ [k].
We have obtained q equations of degree at most two and k equations of degree at most one in
the q + k unknowns (u, v). For every u, the gate equations determine the vj successively and
uniquely. Thus solutions of the complete system correspond bijectively to the ek points of the
selected fiber. The aﬀine Bézout inequality [Hei83] bounds the number of isolated solutions by
the product of the equation degrees, which is at most 2q . Hence ek ≤ 2q .                   □
   We now explain how to produce the kind of square polynomial map required by Lem. 4.1
from a gradient. The gradient of a degree-d homogeneous polynomial has degree d−1, but it has
m outputs and may vanish on a positive-dimensional critical locus. The next lemma removes
these obstacles in two steps: restrict the input to a k-dimensional subspace that avoids nonzero
critical points, and then project the m gradient coordinates down to k without introducing a
new zero.
Lemma 4.2. Let P ∈ C[x1 , . . . , xm ] be homogeneous of degree d ≥ 2, and let δ ≥ 0 satisfy
dim Crit(P ) ≤ δ. If 1 ≤ k < m and k + δ ≤ m, there are linear maps W : Ck → Cm and


                                                       122
A : Cm → Ck , with W injective, such that the homogeneous map F (u) = A∇P (W u) has degree
d − 1 and F −1 (0) = {0}.
Proof. Since P is homogeneous and d ≥ 2, all coordinates of ∇P are homogeneous of degree
d − 1 ≥ 1. In particular, Crit(P ) is a cone: if x is critical, so is every scalar multiple of x. Its
nonzero points can consequently be viewed as directions in projective space:
                          P Crit(P ) = {[x] ∈ Pm−1 : x ∈ Crit(P ) \ {0}}.
Removing the scalar parameter decreases dimension by one, so this projectivized critical locus
has dimension at most δ − 1. If Crit(P ) = {0}, its projectivization is empty and the avoidance
condition below is automatic.
   We use the standard projective avoidance principle: if an algebraic subset of PN has dimension
at most r, then a generic projective l-plane misses that subset whenever l + r < N . One way to
see the dimension count is to consider pairs consisting of a point in the subset and an l-plane
containing that point. For a fixed point, the condition that an l-plane contain it has codimension
N − l in the space of all l-planes. Allowing the point to vary introduces at most r parameters,
so the planes meeting the subset still form a proper exceptional set whenever r < N − l [Har77,
Ch. I].
   Apply this principle first in Pm−1 with l = k − 1 and r = δ − 1. The hypothesis k + δ ≤ m
gives
                                    (k − 1) + (δ − 1) < m − 1,
so some projective (k − 1)-plane avoids P Crit(P ). Such a plane is the projectivization of a
k-dimensional linear subspace of Cm . Choose an injective linear map W : Ck → Cm whose
image is that subspace. Avoidance means exactly that
                                ∇P (W u) 6= 0      for every u 6= 0.
  At this point the gradient has no nonzero zero on the restricted input space, but it still has
m output coordinates. Homogeneity and the displayed nonvanishing let us associate to every
nonzero u the projective direction of its gradient:
                                        [u] 7−→ [∇P (W u)].
This is a well-defined morphism Pk−1 → Pm−1 : replacing u by cu multiplies the gradient by
cd−1 and therefore does not change its projective direction. Its image is a projective algebraic
set of dimension at most k − 1.
   Apply the avoidance principle again, now to this image and to projective planes of dimension
m − k − 1. The required inequality is
                             (m − k − 1) + (k − 1) = m − 2 < m − 1.
Hence there is an (m − k)-dimensional linear subspace K ⊆ Cm whose projectivization does
not meet any gradient direction. Choose a rank-k linear map A : Cm → Ck with kernel K. If
A∇P (W u) = 0 for some u 6= 0, then the nonzero vector ∇P (W u) belongs to K, contradicting
the choice of K. Therefore
                           F (u) = A∇P (W u)       =⇒     F −1 (0) = {0}.
Its coordinates remain homogeneous of degree d − 1, as required.                                   □
  Combining the preceding lemmas now gives a circuit criterion in terms of the codimension of
the critical locus. The only additional ingredient is that all first derivatives of a circuit output
can be computed together with only a constant-factor increase in the number of multiplication
gates.
Proposition 4.3. Suppose a homogeneous polynomial P of degree d ≥ 2 in m variables is a
nonzero scalar multiple of an aﬀine specialization of pern . If dim Crit(P ) ≤ m − k for some
1 ≤ k < m, then every arithmetic circuit of size L computing pern satisfies
(4.2)                                   k log2 (d − 1) ≤ 3L.


                                                123
Proof. Start with a size-L circuit for pern . Since P is a nonzero scalar multiple of an aﬀine
specialization, substituting aﬀine linear forms for the input entries and applying the scalar factor
produces a circuit for P . These operations are free in the multiplicative-complexity model, so
the resulting circuit has at most L multiplication gates.
   The Baur–Strassen differentiation theorem [BS83, Thm. 2] computes all m first derivatives of
P simultaneously with at most three times as many multiplication gates. To see why the factor
is three in this model, evaluate the original circuit in topological order, retaining the output
of each multiplication gate. In the reverse traversal, the adjoint v̄ of an intermediate value v
records the derivative of the final output with respect to v. If a forward gate computes v = ab,
the chain rule gives the updates
                                   ā ← ā + v̄b,         b̄ ← b̄ + v̄a.
The forward product uses one multiplication, and these two updates use at most two more;
additions and scalar operations remain free. Thus all of ∇P can be computed with at most 3L
multiplications, regardless of the number m of derivatives.
  Apply Lem. 4.2 with δ = m − k. Its hypothesis is satisfied because dim Crit(P ) ≤ m − k and
k + (m − k) = m. We obtain linear maps W and A for which
                                        F (u) = A∇P (W u)
is a homogeneous degree-(d − 1) map Ck → Ck whose only zero is the origin. Precomposing
the gradient circuit with W and taking the output combinations prescribed by A cost no mul-
tiplications. Therefore F is computable with at most 3L multiplication gates, and Lem. 4.1
gives
                                       (d − 1)k ≤ 23L .
Taking base-two logarithms proves (4.2).                                                 □

                               5. Critical loci of minor sums
   The circuit bound from Prop. 4.3 becomes useful when we find a degree-d polynomial in
many variables whose critical locus has comparatively small dimension. This section supplies
the necessary estimate for a polynomial that sums all size-d matchings between t rows and s
columns. The following section will realize several disjoint copies of this polynomial as an aﬀine
specialization of the permanent.
   Let X = (xia ) be a t × s matrix of variables, and suppose 1 ≤ d ≤ min{t, s}. Define
                                               X          X
(5.1)                           Mt,s,d (X) =                  per(XI,J ).
                                               I⊆[t] J⊆[s]
                                               |I|=d |J|=d

Every term Qof per(XI,J ) chooses a bijection from I to J. Equivalently, Mt,s,d is the sum of
the weights j∈I xj,φ(j) over all d-element row sets I and all injections φ : I ,→ [s]. Thus its
monomials correspond precisely to matchings of d row–column pairs.
  To describe the critical-point equations, for every nonempty B ⊆ [t] introduce
                                                    X
                                                    s Y
                                       pB (X) =               xja .
                                                    a=1 j∈B

For example, p{j} is the sum of row j, while p{j,j 0 } records the sum of products obtained by
assigning both rows to the same column. There are ρ = 2t −1 such quantities. We will first treat
them as freely chosen parameters and then impose their actual values pB (X). This enlargement
can only increase the dimension being estimated, but makes the critical-point equations uniform
from column to column.
   The basic idea is especially transparent for d = 2. Fix a column a, write uj = xja , and
abbreviate pj = p{j} (X). A matching counted by ∂Mt,s,2 /∂xia already uses the pair (i, a); its
other pair may use any row j 6= i and any column other than a. Therefore
                                    ∂Mt,s,2 X
                                            =       (pj − uj ).
                                      ∂xia     j6=i



                                                    124
At a critical point, put vj = pj − uj . Subtracting the equations for two different values of i
shows that all vj are equal. Each equation then reads (t − 1)vj = 0. Since t ≥ 2 and the ground
field has characteristic zero, every vj vanishes. Thus, once the row sums pj have been fixed, the
entire column (u1 , . . . , ut ) is determined.
   For d ≥ 3, the power sums alone do not determine a column. We will additionally retain
its first d − 2 elementary symmetric functions and prove that these data leave only finitely
many possibilities. Counting the 2t − 1 shared power-sum parameters and the d − 2 additional
parameters for each of the s columns gives the desired bound.
Proposition 5.1. If 3 ≤ d ≤ min{t, s}, then
(5.2)                           dim Crit(Mt,s,d ) ≤ 2t − 1 + s(d − 2).
Proof. Put q = d − 1, so q ≥ 2 and q < t. The argument has three stages. First, we rewrite
every first derivative using the power-sum parameters and one column of X. Next, we identify
the highest-degree part of the resulting equations. Finally, we use that highest-degree part to
show that, once q − 1 = d − 2 symmetric functions per column are fixed, all the remaining
column coordinates admit only finitely many possibilities.
   Fix a row i and a column a. Differentiating a matching monomial with respect to xia keeps
precisely those matchings that use the pair (i, a). Removing that pair leaves a q-element set of
other rows, injected into the columns other than a. Consequently,
                            ∂Mt,s,d         X           X        Y
                                    (X) =                            xj,φ(j) .
                             ∂xia         I⊆[t]\{i} φ:I,→[s]\{a} j∈I
                                                |I|=q

The obstacle is the injectivity requirement: independently summing over a column for each row
would also count assignments in which several rows choose the same column. Inclusion–exclusion
over these collisions gives a convenient expression in terms of the pB .
  For a finite set I, let Π(I) be its set of partitions into nonempty blocks. For π ∈ Π(I), define
                                              Y
                                   µ(π) =           (−1)|B|−1 (|B| − 1)!.
                                              B∈π

Here µ(π) is the usual Möbius coeﬀicient for the partition lattice. Temporarily regard all pB as
independent parameters, and for a column vector u = (u1 , . . . , ut ) define
                                                                                           
                                        X        X              Y                  Y
(5.3)                   Qi (u; p) =                      µ(π)         p B −             uj  .
                                      I⊆[t]\{i} π∈Π(I)          B∈π                j∈B
                                       |I|=q

To verify the inclusion–exclusion explicitly, specialize to u = X•a = (x1a , . . . , xta ) and p = p(X).
For any nonempty block B,
                                                Y             XY
                                   pB (X) −           xja =               xjc .
                                                j∈B           c6=a j∈B

The product of these expressions over B ∈ π counts
                                             Q
                                                   all maps φ : I → [s] \ {a} that are constant
on every block of π, with the matching weight j∈I xj,φ(j) . For a fixed map φ, its total coeﬀicient
in the partition sum is therefore
                                                  X
                                                                        µ(π).
                                                π∈Π(I)
                                   π refines the fiber partition of φ

This coeﬀicient factors over the nonempty fibers C of φ. The factor for a fiber C is
                             X        Y                                   X
                                          (−1)|B|−1 (|B| − 1)! =                  sgn(σ).
                           π∈Π(C) B∈π                                   σ∈SC

Indeed, a permutation with cycle blocks B contributes the displayed sign, and there are (|B|−1)!
cycles on each fixed block B. The sum of permutation signs is 1 when |C| = 1 and 0 when


                                                      125
|C| ≥ 2. Hence precisely the maps with singleton fibers—that is, the injections—survive.
Summing over I proves
                                  ∂Mt,s,d
(5.4)                                     (X) = Qi (X•a ; p(X)).
                                    ∂xia
   We next identify the part of Qi having highest degree in the column variables u, while treating
every pB as a coeﬀicient of degree
                               Q
                                     zero. For a fixed q-element set I, the only way to obtain
column
Q
         degree q is to take −   j∈B j from every block factor in (5.3). Thus the coeﬀicient of
                                     u
  j∈I uj in degree q is
                                                       X       Y
                                           (−1)q                     (|B| − 1)! = (−1)q q!.
                                                      π∈Π(I) B∈π
For the equality, specify the cycle blocks of a permutation of I; each prescribed block B can
be arranged into a cycle in (|B| − 1)! ways. Summing over partitions therefore counts all q!
permutations. Put α = (−1)q q!, and write ej (u) for the jth elementary symmetric polynomial
in u1 , . . . , ut , with e0 (u) = 1. Summing the degree-q monomials over all I ⊆ [t] \ {i} gives
(5.5)               Qi (u; p) = αeq (u1 , . . . , ubi , . . . , ut ) + Ri (u; p),               degu Ri ≤ q − 1.
Here the hat means that coordinate ui is omitted. In particular, although the lower-degree
remainder can depend on the shared parameters pB , the highest-degree part has a simple sym-
metric form independent of those parameters.
  We now convert this structure into the promised parameter count. Introduce independent
                                                            (a)      (a)
coordinates pB and a separate column vector u(a) = (u1 , . . . , ut ) for every a ∈ [s]. The
equations Qi (u(a) ; p) = 0 define an aﬀine set whose coordinate ring is
                                                  (a)                                                      
                               A = C[pB , ui ] Qi (u(a) ; p) : 1 ≤ i ≤ t, 1 ≤ a ≤ s .
This is the incidence construction: its points record one common collection of power-sum pa-
rameters together with s columns satisfying the corresponding critical-point equations. A true
critical point of Mt,s,d gives such a point by taking u(a) = X•a and pB = pB (X). We allow
additional incidence points for which the pB need not equal these actual power sums, since an
upper bound for the larger set also bounds the critical locus.
   In addition to the ρ power-sum parameters, retain the first q − 1 elementary symmetric func-
tions of each column. To keep these parameters formally independent, introduce the polynomial
ring
                       B = C[pB , za,j : ∅ 6= B ⊆ [t], 1 ≤ a ≤ s, 1 ≤ j < q]
and map it into A by sending each pB to its namesake and each za,j to ej (u(a) ). Equivalently,
this map makes A into a B-algebra. The map need not be injective: any relations among the
actual parameter values can only decrease the final dimension.
   Our remaining task is to prove that A is generated by finitely many elements as a module
over B. Fix one column, suppress its index, and put κ = t − q > 0. Two elementary symmetric-
polynomial identities give
                                                X
                                                q                               X
                                                                                t
                                                             q−j
        eq (u1 , . . . , ubi , . . . , ut ) =       (−ui )         ej (u),            eq (u1 , . . . , ubi , . . . , ut ) = κeq (u).
                                                j=0                             i=1
                                           Q                            Q
For the first identity, expand h6=i (1 + uh z) = h (1 + uh z)/(1 + ui z) and compare coeﬀicients
of z q . For the second, each squarefree monomial of degree q occurs once for each of the t − q = κ
omitted coordinates outside its support.
   The incidence equations and (5.5) say that αeq (u1 , . . . , ubi , . . . , ut ) + Ri (u; p) = 0 for every i.
Summing these equations and using the second elementary symmetric identity gives
                                                                     X
                                                                     t
                                                  καeq (u) +               Rh (u; p) = 0.
                                                                     h=1
This eliminates the only elementary symmetric function eq (u) not already recorded among the
base parameters za,j . Insert the first symmetric identity into the ith incidence equation, replace


                                                                      126
ej (u) by za,j for 1 ≤ j < q, and eliminate eq (u) using the summed equation. Since α(−1)q = q!,
the resulting equality in A is

                                      X
                                      q−1                                    X
                                                                             t
(5.6)                 κq!uqi = −κα           (−ui )q−j za,j − κRi (u; p) +         Rh (u; p).
                                       j=1                                   h=1

Treating the pB and za,j as base coeﬀicients, every term on the right has degree at most q − 1 in
the coordinates of the chosen column. Because κ > 0 and the ground field has characteristic zero,
the leading coeﬀicient κq! is invertible. Therefore (5.6) replaces uqi by a B-linear combination
of monomials of strictly smaller total column degree.
   Apply this replacement whenever any coordinate exponent is at least q. Each replacement
decreases total degree in the corresponding column, so the process terminates. Repeating it for
all s columns shows that the finitely many monomials
                                     s Y
                                     Y t
                                                 (a)
                                              (ui )ra,i ,       0 ≤ ra,i < q,
                                    a=1 i=1

generate A as a B-module. In particular, fixing all the parameters pB and za,j leaves a finite-
dimensional coordinate algebra for the possible columns; this is the algebraic form of the claimed
finite-choice property.
   A finite algebra cannot have larger Krull dimension than its parameter ring: if the map
B → A has kernel K, then A is finite over B/K, and the standard dimension theorem for finite
algebras gives dim A = dim(B/K) ≤ dim B [Eis95]. Since B is a polynomial ring in ρ + s(q − 1)
independent parameters, we obtain

                                      dim A ≤ dim B = ρ + s(q − 1);

  Finally, to return from the enlarged incidence set to the actual critical locus, (5.4) induces
                                                                                      (a)
a surjection from A onto C[X]/(∂Mt,s,d /∂xia : i, a) by sending pB to pB (X) and ui to xia .
                                                    (a)
The map is surjective because the images of the ui are all the matrix variables. Passing to
a quotient cannot increase Krull dimension, and the dimension of an aﬀine common-zero set
equals the Krull dimension of its coordinate ring. Hence

                  dim Crit(Mt,s,d ) ≤ dim A ≤ ρ + s(q − 1) = 2t − 1 + s(d − 2),

which proves (5.2).                                                                                 □

  The circuit application requires several copies of this polynomial on disjoint sets of variables.
Because their critical-point equations involve separate variable blocks, the individual dimension
bounds add.
Corollary 5.2. Suppose 3 ≤ d ≤ min{t, s}, let X (1) , . . . , X (b) be disjoint t × s variable blocks,
and let λ1 , . . . , λb ∈ C× . Then
                      X
                      b
                                                                                                
            P (X) =         λh Mt,s,d (X (h) )     =⇒       dim Crit(P ) ≤ b 2t − 1 + s(d − 2) .
                      h=1

Proof. For a variable in block X (h) , the corresponding derivative of P is λh times the derivative
of Mt,s,d (X (h) ). Since λh 6= 0, this derivative vanishes exactly when the corresponding derivative
of the block polynomial vanishes. Different blocks share no variables, and therefore

                                                   Y
                                                   b
                                    Crit(P ) =           Crit(Mt,s,d (X (h) )).
                                                   h=1

Dimensions add under products of complex aﬀine algebraic sets. Applying Prop. 5.1 to each
factor gives the stated bound.                                                         □


                                                         127
                      6. An affine specialization of the permanent
   Corollary 5.2 bounds the critical locus of a sum of minor-sum polynomials supported on
disjoint row blocks. To apply Prop. 4.3, however, we must first realize such a sum as a spe-
cialization of one permanent. Our immediate objective is therefore to construct a matrix of
constants whose permanent minors cancel whenever the omitted rows come from several dif-
ferent blocks, but remain nonzero when all the omitted rows come from one block. Appending
these constant columns to a matrix of variables will then produce exactly the blockwise minor
sums from the preceding section.
   Let b, t, s ≥ 1, partition [r] into b disjoint blocks R1 , . . . , Rb of size t, where r = bt, and
suppose that 1 ≤ d ≤ min{t, s}. For T ⊆ [r], let 1T ∈ Cr denote the vector that is 1 on T and
0 elsewhere. Choose a primitive dth root of unity ζ, and set
                                                θ = (−1)d+1 2d .
The following two families of constant columns form a matrix U ∈ Cr×(r−d) :
     • for each h ∈ [b], take t − d copies of 1Rh ;
     • for each h = 2, . . . , b and j = 0, . . . , d − 1, take 1R1 ∪···∪Rh−1 + 2ζ j 1Rh .
The first family contributes b(t − d) columns and the second contributes (b − 1)d columns, for
a total of b(t − d) + (b − 1)d = bt − d = r − d. If t = d, the first family is empty; if b = 1, the
second family is empty.
                                                                      P
Lemma 6.1. There are λ1 , . . . , λb ∈ C× such that h λh Mt,s,d (XRh ,[s] ) is, up to a nonzero
scalar, an aﬀine specialization of perr+s−d . More precisely, for the block matrix
                                                 
                                              X U
                           B(X) =                 ,            X = (xia )i∈[r], a∈[s] ,
                                              1 0
where the lower-left block is the (s − d) × s all-ones matrix and the lower-right block is the
(s − d) × (r − d) zero matrix, one has
                            X
                            b
(6.1)       per(B(X)) = c         λh Mt,s,d (XRh ,[s] ),             c = (s − d)!(t − d)!(t!)b−1 6= 0.
                            h=1

Proof. First observe why minors of U determine the desired specialization. The matrix B(X)
has r + s − d rows and columns. Because its lower-right block is zero, each of its s − d lower rows
must be matched to one of the first s columns in every nonzero permanent term. This leaves
exactly d of those columns to be matched to upper rows. Let J ⊆ [s] be those d columns and
I ⊆ [r] the d upper rows matched to them. The remaining r − d upper rows must be matched
to the r − d columns of U . Finally, the remaining lower-left submatrix is an (s − d) × (s − d)
all-ones matrix, whose permanent is (s − d)!. Summing over I and J consequently gives
                                                       X
(6.2)                per(B(X)) = (s − d)!                          per(UI c ,[r−d] ) per(XI,J ).
                                                 I⊆[r], J⊆[s]
                                                  |I|=|J|=d

It remains to show that the constant coeﬀicient per(UI c ,[r−d] ) vanishes unless I is contained in
one row block, and to compute its value in the remaining cases.
   To keep track of these minors, introduce the commutative square-zero algebra
                                    S = C[z1 , . . . , zr ]/(z12 , . . . , zr2 ).
                      Q
Its monomials zK = i∈K zi , indexed by subsets K ⊆ [r], form a vector-space basis: a term
containing any zi twice vanishes. Consequently, if A is an r × q matrix and |K| = q, expansion
of its column forms gives
                                                               !
                                          Y
                                          q     X
                                                r
(6.3)                             [zK ]               Aij zi       = per(AK,[q] ).
                                          j=1   i=1

Indeed, each surviving contribution chooses a distinct row for each column, and the contributions
producing zK are precisely the bijections between the q columns and the rows in K. When q = 0,


                                                        128
both the empty product and the permanent of the empty matrix are 1. Thus the minors of U
are encoded by a single product of its column forms.
  For each block, put
                                               X
                                          yh =    zi .
                                                               i∈Rh
Because the variables commute and have square zero,
                                         X
(6.4)                      yhj = j!                 zK       (0 ≤ j ≤ t),                   yht+1 = 0.
                                        K⊆Rh
                                        |K|=j
                      Q
In particular, yht = t! i∈Rh zi : the power yht saturates the entire block, so multiplying it by any
additional zi with i ∈ Rh gives zero.
   The column form of 1Rh is yh . If Yh−1 = y1 + · · · + yh−1 , the column form of 1R1 ∪···∪Rh−1 +
                                                        Q
2ζ 1Rh is Yh−1 + 2ζ j yh . The ordinary factorization d−1 j=0 (A + ζ B) = A − (−B) , applied in
  j                                                                  j        d        d

the commutative algebra S, therefore gives
                                      Y
                                      d−1
                                            (Yh−1 + 2ζ j yh ) = Yh−1
                                                                 d
                                                                     + θyhd .
                                      j=0

All mixed powers of Yh−1 and yh have canceled. Multiplying over both families of columns now
yields
                                                !                         !   b 
                          Y
                          r−d    X
                                 r                        Y
                                                          b                   Y                          
(6.5)                                  Uij zi       =             yht−d               d
                                                                                     Yh−1 + θyhd .
                          j=1    i=1                     h=1                  h=2

  For example, when b = 2, the product of all column forms of U is
                                y1t−d y2t−d (y1d + θy2d ) = y1t y2t−d + θy1t−d y2t .
In the first term all rows of R1 appear and exactly d rows of R2 are omitted; in the second, the
roles of the blocks are reversed. In particular, no term can omit rows from both blocks. Taking
t = s = d = 2 gives θ = −4 and recovers the 4 × 4 cancellation in §2.
   We next verify that the same block-selection property persists for any number of blocks. For
1 ≤ h ≤ b, let
                                                             
                                                 Y
                                                 h                h 
                                                                  Y                             
                                     Ch =             ygt−d               d
                                                                          Yg−1 + θygd .
                                                 g=1              g=2
                                                 (h)
We claim that there are coeﬀicients λi                 such that
                                                       X
                                                       h
                                                              (h)             Y
                                            Ch =             λi yit−d               ygt .
                                                       i=1                g∈[h]
                                                                           g6=i

                                                                  (1)
For h = 1, this is the identity C1 = y1t−d , with λ1 = 1. Suppose the identity holds for h blocks.
By definition,
                                                                                           
                                                  t−d
                                       Ch+1 = Ch yh+1 Yhd + θyh+1
                                                              d
                                                                  .
                      d
The term containing θyh+1 saturates the new block and multiplies each previous coeﬀicient by
θ. In the term containing Yhd , every old block other than Ri is already saturated in the ith
summand. Therefore all mixed terms in Yhd = (y1 + · · · + yh )d vanish after multiplication by
that summand, and the only surviving term is yid . Hence
                                                             
                                                                                                ! h
                           Xh          Y                                     X
                                                                               h                 Y
                               (h)                                                  (h)
                              λi yit−d   ygt  Yhd =                                λi                ygt .
                                             
                               i=1               g∈[h]                         i=1               g=1
                                                  g6=i



                                                               129
It follows that the coeﬀicients satisfy
                          (h+1)            (h)                                  (h+1)          X
                                                                                               h
                                                                                                      (h)
                         λi       = θλi           (1 ≤ i ≤ h),                 λh+1 =                λi .
                                                                                               i=1
        Ph      (h)                                                    h−1 .
If Sh =    i=1 λi , then S1 = 1 and Sh+1 = (1 + θ)Sh , so Sh = (1 + θ)                                         Consequently, at
h = b the coeﬀicients are
                         λ1 = θb−1 ,             λh = θb−h (1 + θ)h−2                 (2 ≤ h ≤ b).
They are all nonzero: θ 6= 0 and |θ| = 2d > 1 imply 1 + θ 6= 0.                               Combining the induction with
(6.5) proves
                                                           !
                                     Y
                                     r−d    X
                                            r                      X
                                                                   b                 Y
(6.6)                                             Uij zi       =         λh yht−d          ygt ,
                                     j=1    i=1                    h=1              g6=h
the promised expression in which exactly one row block is unsaturated.
   Finally, let I ⊆ [r] have size d. By (6.3), the coeﬀicient of zI c on the left of (6.6) is
per(UI c ,[r−d] ). On the right, the hth summand saturates every block except Rh . Thus it
contributes to zI c only if I ⊆ Rh . When this occurs, (6.4) gives a factor (t − d)! from yht−d and
a factor t! from each of the other b − 1 blocks. Therefore
                                     (
                                       λh (t − d)!(t!)b−1 , I ⊆ Rh ,
               per(UI c ,[r−d] ) =
                                       0,                   I meets more than one block.
Substituting this identity into (6.2) and grouping the surviving terms by their block Rh gives
                                                                         X
                                                                         b              X
                 per(B(X)) = (s − d)!(t − d)!(t!)b−1                           λh                    per(XI,J ).
                                                                         h=1        I⊆Rh , J⊆[s]
                                                                                     |I|=|J|=d

The inner sum is Mt,s,d (XRh ,[s] ), and the factorial prefactor is nonzero over C. This proves (6.1)
and realizes the blockwise polynomial needed for Cor. 5.2 as a specialization of one permanent.
                                                                                                   □

                        7. Circuit parameters and the lower bound
   We now assemble the geometric gradient bound, the critical-locus estimate, and the block-
selective specialization to prove Thm. 1.1. There are two quantitative requirements. First, the
specialization must retain m = Θ(n2 ) genuinely variable matrix entries. Second, its critical
locus must have dimension bounded away from m, so that a linear slice of dimension k = Θ(m)
avoids every nonzero critical point. Once these requirements hold, Prop. 4.3 supplies a lower
bound proportional to k log2 (d − 1).
   The critical-locus bound from Cor. 5.2 has two costs per row block: 2t − 1 global power-sum
parameters and s(d − 2) column parameters. Setting t = 4d makes the second cost less than
one quarter of the ts variables in each block. We will separately require 2t − 1 ≤ ts/4, so the
first cost also consumes at most one quarter. Choosing d on the order of log n will make these
requirements compatible while preserving the logarithmic gain in the gradient bound.
   Fix d ≥ 3, and introduce the parameters
                                                                                    
                             n                                                         m
(7.1)      t = 4d,     b=       ,     r = bt,   s = n − r + d,       m = rs,     k=        .
                             2t                                                         4
Here t is the number of rows in each block, b is the number of blocks, and r = bt is the total
number of variable rows. Taking b = bn/(2t)c places r near n/2, leaving roughly n/2 variable
columns. More precisely, the choice s = n − r + d makes the square matrix B(X) of Lem. 6.1
have exactly
                                          r+s−d=n
rows and columns. Its variable upper-left block is an r × s matrix, so m = rs counts its variable
entries. Finally, k = bm/4c is the dimension of the gradient slice to which Prop. 4.3 will be
applied.


                                                               130
  If n ≥ 6t, then b ≥ 1 and s ≥ n/2. In particular, d ≤ t and d ≤ s, so all hypotheses needed
to construct the degree-d specialization in Lem. 6.1 hold. The next proposition isolates the
remaining numerical condition before we choose the degree as a function of n.
Proposition 7.1. Let n, d be positive integers, and define t, b, r, s, m, k by (7.1). Suppose
(7.2)                        d ≥ 3,        n ≥ 6t,          4(2t − 1) ≤ ts.
Then every arithmetic circuit of size L computing pern satisfies
                                                 n2 log2 (d − 1)
(7.3)                                    L≥                      .
                                                      144
Proof. Let ρ = 2t − 1, and let
                                              X
                                              b
                                  P (X) =           λh Mt,s,d (XRh ,[s] )
                                             h=1

be the weighted block polynomial from (6.1). Lem. 6.1 makes P a nonzero scalar multiple of
an aﬀine specialization of pern , so it has precisely the form required by Prop. 4.3. Since all λh
are nonzero and the row blocks involve disjoint variables, Cor. 5.2 gives
                                                                            
                              dim Crit(P ) ≤ D := b ρ + s(d − 2) .
We estimate the two summands of D separately. The scale condition 4ρ ≤ ts gives
                                            bts    m
                                            bρ ≤= .
                                             4     4
For the column-parameter contribution, the choice t = 4d gives
                                                            bts  m
                                  bs(d − 2) < bsd =             = .
                                                             4   4
Consequently,
                                                          m
                                       dim Crit(P ) ≤ D <   .
                                                          2
Since k = bm/4c ≤ m/4, we have k + D < m, and in particular k + D ≤ m. Thus a k-
dimensional linear slice can avoid the nonzero critical locus, as required in Lem. 4.2. Applying
Prop. 4.3 to this specialization gives
(7.4)                                    k log2 (d − 1) ≤ 3L.
  It remains to express the slice dimension k in terms of the original matrix size n. From the
definition of b,
                                                  
                                    n              n     n
                                      −t≤r =t         ≤ .
                                    2              2t    2
The hypothesis n ≥ 6t implies n/2 − t ≥ n/3. Therefore
                    n        n                         n                 n2
                      ≤r≤ ,          s=n−r+d≥ ,                m = rs ≥     .
                    3        2                         2                  6
In particular m ≥ 8, and the floor in the definition of k loses at most a factor of two:
                                                  
                                                 m   m   n2
                                        k=         ≥   ≥    .
                                                 4   8   48
Equivalently, n2 ≤ 48k. Substituting this estimate into (7.4) yields
                                      k log2 (d − 1)   n2 log2 (d − 1)
                                 L≥                  ≥                 ,
                                             3              144
as claimed.                                                                                     □


                                                    131
Proof of Thm. 1.1. The fixed-degree bound becomes strongest when d grows while 24d remains
small enough to satisfy the scale condition. For n ≥ 216 , put
                                                  
                                                   `
                             ` = log2 n,     d=      ,      t = 4d.
                                                   4
Then ` ≥ 16, so d ≥ 4 and t ≤ `. The inequality n ≥ 6t follows from n ≥ 216 and t ≤ log2 n.
As in the proposition, r ≤ n/2 and s ≥ n/2. Moreover, 2t ≤ 2` = n, while d ≥ 4 gives ds ≥ n.
Therefore
                          2t − 1 < n ≤ ds,    4(2t − 1) ≤ 4ds = ts.
Thus all three hypotheses of (7.2) hold.
  Finally, ` ≥ 16 ensures                 
                                          `        `       `
                                d−1=         −1≥ −2≥ .
                                          4        4       8
Taking logarithms gives
                              log2 (d − 1) ≥ log2 ` − 3 = log2 log2 n − 3.
Substitution into (7.3) proves (1.1). The factor log2 log2 n − 3 grows without bound, so the
resulting circuit lower bound is superquadratic.                                          □

                           8. Coefficient transcendence degree
   We now turn from circuits to formulas. The first task is to define a complexity measure
that records how much independent information a polynomial carries in the coeﬀicients asso-
ciated with a selected set of variables. We then show that, for any division-free formula, this
information is controlled by the number of occurrences of those variables. The next section
will exhibit a matching of O(log n) matrix entries for which the permanent has Ω(n2 ) indepen-
dent coeﬀicients. The formula lower bound will follow by applying the present section to many
entry-disjoint matchings and adding their occurrence requirements.
   Let X be a finite set of variables, let ∅ 6= Y ⊆ X , and put Z = X \ Y . We call Y the
selected variables and Z the remaining variables. To expose the information associated with Y ,
regard a polynomial in all the variables as a polynomial in Y whose coeﬀicients are themselves
polynomials in Z. Thus every f ∈ C[X ] = C[Z][Y ] has a unique expansion
                              X                                               Y
                      f=            fα Y α ,      fα ∈ C[Z],        Yα =            y α(y) .
                            α∈NY                                              y∈Y

Although the index set NY     is infinite, only finitely many fα are nonzero. The multi-index 0
denotes the all-zero exponent vector, so f0 is obtained by setting every variable of Y to zero.
   Counting distinct coeﬀicient polynomials would overestimate the information they contain:
several coeﬀicients can satisfy polynomial relations. Instead, we count the maximum number
that are algebraically independent. Recall that polynomials c1 , . . . , cr ∈ C[Z] are algebraically
independent over C if
                    Q(c1 , . . . , cr ) 6= 0   for every nonzero Q ∈ C[T1 , . . . , Tr ].
For example, if Y = {y} and f = yz1 + z2 , the two coeﬀicients z1 , z2 are algebraically indepen-
dent. In contrast, for f = yz 2 + z, the coeﬀicients c0 = z and c1 = z 2 satisfy c1 − c20 = 0, and
therefore carry only one algebraically independent parameter.
  Define its coeﬀicient transcendence degree by
                                                                          
                                   tdY (f ) = trdegC C fα : α ∈ NY .
Here C(Z) denotes the rational-function field in the remaining variables, and C(fα : α ∈ NY )
is the smallest subfield containing C and all the coeﬀicient polynomials. In particular, the
field includes the constant-in-Y coeﬀicient f0 . Its transcendence degree is precisely the largest
number of algebraically independent coeﬀicients in the expansion. Passing to the field generated
by the coeﬀicients does not assume that they are rational rather than polynomial: it simply lets
us measure how many independent parameters generate all of them. In the examples above,
the coeﬀicient transcendence degrees are two and one, respectively.


                                                      132
  For a formula Φ, let tY (Φ) denote the number of leaves labeled by variables in Y , counted
with multiplicity. Thus two leaves carrying the same variable contribute two occurrences. Our
goal is to bound tdY (f ) in terms of tY (Φ), independently of the number or complexity of the
subformulas involving only Z. The coeﬀicient-transcendence method is standard [KS14, §3.2.1,
Lem. 7]; the following proof supplies the explicit constant needed here.
Lemma 8.1. If a division-free formula Φ computes f ∈ C[X ] and t = tY (Φ) ≥ 1, then
                                       tdY (f ) ≤ 4t − 2 ≤ 4t.
Proof. Mark a vertex of the formula exactly when its subformula has a descendant leaf labeled
by a variable in Y . The marked vertices form the portion of the formula connecting the t
selected leaves to the root. A marked gate can have either one or two marked children. The
two cases play different roles: a gate with one marked child merely changes an aﬀine wrapper
around the selected-variable computation, while a gate with two marked children combines two
such computations and can introduce new parameters.
   First suppose a marked gate has exactly one marked child, whose output is u. The other child
contains no selected-variable leaf and hence computes some polynomial h ∈ C[Z]. According to
the gate operation and the order of its inputs, the output is one of
                              u + h,       u − h,        h − u,        hu.
Each expression has the form Au + B with A, B ∈ C[Z]. Moreover, a whole path of such gates
can be absorbed into a single aﬀine map, since
                        A2 (A1 u + B1 ) + B2 = (A2 A1 )u + (A2 B1 + B2 ).
Thus an arbitrarily long path with only one marked child at each gate does not require a new
independent parameter at every gate.
  We formalize this observation by induction. For every marked subformula with s ≥ 1 selected-
variable leaves, we claim that its output admits a representation
(8.1)            Ag + B,         A, B ∈ C[Z],       g ∈ C(Γ)[Y ],        |Γ| ≤ 4s − 4,
for some finite Γ ⊆ C(Z). The outer coeﬀicients A, B are not yet counted in Γ; they will be
charged when the corresponding marked computation meets another one, or at the root. At a
marked leaf labeled by y ∈ Y , choose
                           g = y,        A = 1,         B = 0,      Γ = ∅.
This gives the claim for s = 1.
   If a marked gate has only one marked child, compose its aﬀine map with the outer aﬀine map
already supplied for that child. The resulting slope and intercept still belong to C[Z], the inner
polynomial g is unchanged, and no new element is added to Γ.
   It remains to consider a gate with two marked children. Suppose they have s1 , s2 ≥ 1
selected-variable leaves and, by induction, their respective outputs are
              A1 g1 + B1   and     A2 g2 + B2 ,     gi ∈ C(Γi )[Y ],         |Γi | ≤ 4si − 4.
Adjoin the four outer coeﬀicients and set
                            Γ = Γ1 ∪ Γ2 ∪ {A1 , B1 , A2 , B2 } ⊆ C(Z).
Both child outputs now belong to C(Γ)[Y ]. Applying the gate operation +, −, or × therefore
produces another polynomial g ∈ C(Γ)[Y ]. Represent the resulting output with the identity
outer map, namely A = 1 and B = 0. Since s = s1 + s2 , the parameter count is
                            |Γ| ≤ (4s1 − 4) + (4s2 − 4) + 4 = 4s − 4.
This completes the induction. Equivalently, the marked part of a binary formula has t−1 genuine
branching points; each can be charged at most four parameters, regardless of the lengths of the
intervening one-child paths.
   Apply (8.1) to the root, which is marked because t ≥ 1. Its output is f = Ag + B with
|Γ| ≤ 4t − 4. Adjoin the final slope and intercept by taking
                                     Γ0 = Γ ∪ {A, B} ⊆ C(Z).


                                                  133
Then |Γ0 | ≤ 4t−2 and f ∈ C(Γ0 )[Y ], so every coeﬀicient fα belongs to C(Γ0 ). A field generated by
r elements has transcendence degree at most r, whether or not those generators are algebraically
independent. Therefore
                            tdY (f ) ≤ trdegC C(Γ0 ) ≤ |Γ0 | ≤ 4t − 2,
as claimed.                                                                                        □
   To apply this upper bound to the permanent, we also need a practical way to certify that
a large family of its coeﬀicients is algebraically independent. The characteristic-zero Jacobian
criterion supplies exactly that test. Given coeﬀicient polynomials c1 , . . . , cr ∈ C[Z], form the
matrix                                                      
                                                         ∂ci
                                 J(c1 , . . . , cr ) =                 .
                                                         ∂z i∈[r], z∈Z
Its rank is computed over the rational-function field C(Z). The Jacobian criterion states that
                          trdegC C(c1 , . . . , cr ) = rankC(Z) J(c1 , . . . , cr )
in characteristic zero [BMS11, Thm. 6]. Consequently, to prove that r coeﬀicients are alge-
braically independent, it is enough to identify r remaining variables and show that the cor-
responding square Jacobian minor is a nonzero polynomial. It is enough in turn to find one
specialization of those and the other remaining variables where this minor evaluates to a nonzero
complex number. The next section constructs precisely such a specialization for r = Ω(n2 ) co-
eﬀicients associated with one short matching.

                      9. Independent coefficients from a matching
   A matching is a set of matrix entries with no repeated row or column. Our goal in this
section is to prove that, for a matching Y of only O(log n) entries, the expansion of pern in
the variables of Y contains Ω(n2 ) algebraically independent coeﬀicients. Combined with the
coeﬀicient bound from Lem. 8.1, this will force every division-free formula for the permanent
to contain Ω(n2 ) occurrences of the variables in each such matching; an analogous coeﬀicient
bound later treats formulas with division. The remaining step, packing many entry-disjoint
matchings, is deferred to §10.
   The independence proof has two conceptual ingredients. First, split the marked matching
into two equal parts, one encoding external column choices and the other encoding external row
choices. Second, specialize the unmarked entries so that the Jacobian of selected coeﬀicients
separates into independent row and column evaluation matrices. We begin with a small instance
that displays this separation without the binary-index bookkeeping needed in general.
9.1. A five-by-five warm-up. Choose distinct p1 , p2 , p3 ∈ C and, independently, distinct
q1 , q2 , q3 ∈ C, and consider
                                                                              
                                     ye 0                p1  p2  p3
                                    0 yf                 1   1   1 
                                                                    
                                 B=
                                    1 q1                w11 w12 w13 
                                                                     .
                                    1 q2                w21 w22 w23 
                                     1 q3                w31 w32 w33
The matching here consists of the two diagonal variables ye , yf . Call their rows and columns
internal, and call the remaining three rows and columns external. Since the permanent is
multilinear, its expansion in the marked variables is
                              per(B) = cef ye yf + cf yf + ce ye + c∅ .
Thus cef , cf , ce , c∅ collect the permutation terms using both marked diagonal entries, only yf ,
only ye , or neither, respectively. They are polynomials in the external block entries wab .
  Differentiating a coeﬀicient with respect to wab keeps precisely the permutation terms that
match external row a to external column b. Set
                                           X                          X
                                   Gb =           pj ,         Ha =          qi ,
                                           j6=b                       i6=a



                                                         134
and, only after taking the derivative, evaluate all wij at 1. Counting the remaining matchings
gives
               ∂cef            ∂cf                ∂ce              ∂c∅
                     = 2,           = 2Gb ,            = 2Ha ,           = Gb Ha .
               ∂wab           ∂wab               ∂wab              ∂wab
Each count can be seen directly:
        • For cef , both internal rows and columns are already matched. After the derivative fixes
          (a, b), the other two external rows can match the other two external columns in 2! = 2
          ways.
        • For cf , the f -row uses its marked diagonal entry. The e-row must use an external column
          j 6= b, with weight pj , giving Gb . The internal e-column can receive either external row
          other than a, giving the additional factor 2.
        • For ce , the roles are reversed: the f -row can use either remaining external column, while
          the external row i 6= a matched to the f -column contributes qi . The result is 2Ha .
        • For c∅ , neither internal diagonal is used. The external column used by the e-row con-
          tributes Gb , and the external row matched to the f -column contributes Ha . These
          choices are independent, and all remaining matches are forced.
  Restricting to the four external variables w11 , w12 , w21 , w22 yields the Jacobian
                                                                          
                                               1     1     1     1
                                            G1     G     G     G 2 
                          diag(2, 2, 2, 1) 
                                            H1
                                                      2     1        .
                                                    H1    H2    H2 
                                             G1 H1 G2 H1 G1 H2 G2 H2
The second
             factor
                    is the Kronecker
                                      product VH ⊗ VG of the two-point Vandermonde matrices
          1 1                   1 1
VH = H1 H2 and VG = G1 G2 . The row choice and column choice are independent, so these
two evaluation factors separate. Since G2 − G1 = p1 − p2 and H2 − H1 = q1 − q2 , their Kronecker
product has determinant (p1 − p2 )2 (q1 − q2 )2 6= 0. The diagonal prefactor is also invertible, so
the four coeﬀicients are algebraically independent. The characteristic-zero Jacobian criterion
recalled in §8 justifies this final implication: a nonzero Jacobian minor at even one specialization
certifies independence before specialization.
   The example identifies the general plan. We will replace the single e-index and f -index by `
indices of each type. Subsets of these indices encode external column and row choices in binary,
and the resulting two evaluation matrices become m × m Vandermonde-type matrices. Their
Kronecker product then certifies the independence of m2 coeﬀicients.

9.2. The parameters and the chosen coeﬀicient family. Fix n ≥ 32 and introduce the
formula parameters
(9.1)                         ` = dlog2 ne,      k = 2`,      m = n − k.
These parameters satisfy k ≤ n/2, m ≥ k + 1, and m ≤ 2` . Indeed, n > 4` when ` = 5, and
when ` ≥ 6 one has n ≥ 2`−1 + 1 ≥ 4` + 1. Here k is the number of marked entries and m is the
number of unmarked rows and columns left after those entries are placed on the diagonal. The
inequality m ≤ 2` means that ` bits suﬀice to index each of the m external rows or columns;
the inequality m ≥ k + 1 ensures that there are enough external indices for every injection that
appears below.
Lemma 9.1. If Y is a matching of k entries of X, then tdY (pern ) ≥ m2 .
Proof. We first identify m2 coeﬀicients indexed by a pair (α, β) ∈ {0, . . . , m − 1}2 . We then
specialize the unmarked entries, count the derivatives of those coeﬀicients with respect to the
m2 external-block entries, and show that the resulting Jacobian is invertible. The counting
separates external column choices from external row choices, exactly as in the 5 × 5 example.
Step 1: Coeﬀicients of marked diagonal entries. By permuting rows and Q          columns, suppose Y =
{y1 , . . . , yk }, where yi = xii . For S ⊆ [k], let cS denote the coeﬀicient of i∈S yi . Multilinearity


                                                  135
gives
                                                       !
                                           Y ∂
(9.2)                           cS =                       pern (X)                   .
                                           i∈S
                                                 ∂yi
                                                                      y1 =···=yk =0
Indeed, differentiating once with respect to each yi for i ∈ S selects the permutation terms that
use those marked diagonal entries. Setting all marked variables to zero then discards terms
using any additional marked entry. Equivalently, cS is the permanent of the matrix obtained by
deleting the rows and columns indexed by S and setting the remaining marked diagonal entries
to zero.
Step 2: Separate internal and external choices. Partition the marked indices as [k] = E t F ,
where E = {e0 , . . . , e`−1 } and F = {f0 , . . . , f`−1 }. Call these k rows
                                                                              and columns internal, index
the m external rows and columns by [m], and write X = V W , where D is k × k, U is k × m,
                                                                      D  U

V is m × k, and W = (wab ) is m × m. Thus U matches internal rows to external columns, V
matches external rows to internal columns, and W matches external rows to external columns.
   Choose distinct p1 , . . . , pm ∈ C and, independently, distinct q1 , . . . , qm . For i 6= j in [k],
0 ≤ u, v < `, and a, b ∈ [m], specialize the unmarked variables by
(9.3)                       Dij = 0,                                            wab = 1,
                                      u
                          Ueu ,b = p2b ,                                       Ufv ,b = 1,
                                                                                             v
(9.4)                     Va,eu = 1,                                           Va,fv = qa2 .
Denote this specialization by ξ; derivatives are taken before evaluation at ξ. The e-indices
carry powers of pb when an internal row chooses external column b, whereas the f -indices carry
powers of qa when external row a chooses an internal column. All other internal–external edges
have weight 1. The powers 2u and 2v ensure that subsets of E and F encode integers without
colliding.
   For 0 ≤ α, β < m, let P (α) ⊆ E and Q(β) ⊆ F record the 1-digits of the `-digit binary
expansions of α and β, with digit 0 least significant. Set T (α, β) = P (α) ∪ Q(β) and S(α, β) =
[k] \ T (α, β). Since m ≤ 2` , these definitions yield m2 coeﬀicients cS(α,β) of distinct marked
monomials. The complement in the definition of S is important: the indices in S have already
been matched through their marked diagonal entries, while the indices in T remain present in
the coeﬀicient permanent and must be matched through the unmarked blocks.
   Our immediate goal is to show that these m2 coeﬀicients have an invertible Jacobian with
respect to the m2 variables wab . Consider the square matrix
                                                   ∂cS(α,β)
                                    J(α,β),(a,b) =           .
                                                    ∂wab ξ
Once det J 6= 0 has been established, the Jacobian criterion immediately gives the conclusion
of the lemma. We first derive a combinatorial expression for each entry of J.
Step 3: Count the surviving permutation terms. Fix α, β, a, b, and abbreviate P = P (α),
Q = Q(β), T = P ∪ Q, and r = |T |. Because r ≤ k ≤ m − 1, differentiation fixes external row a
to external column b and leaves precisely the internal rows and columns indexed by T . There
are m − 1 external rows and m − 1 external columns still available. At ξ, the internal block
on T is zero: its off-diagonal entries are zero by (9.3), and its marked diagonal entries were set
to zero in (9.2). Therefore no remaining internal row can match an internal column. Instead,
every internal row must match an external column, and every internal column must receive an
external row.
   The first set of choices is an injection ρ : T ,→ [m] \ {b}, assigning a distinct external column
to each internal row. The second is an injection θ : T ,→ [m] \ {a}, assigning a distinct external
row to each internal column. They are independent because ρ selects columns and θ selects rows.
The m − 1 − r external rows and columns not used by these injections can then be matched in
(m − 1 − r)! ways, each of weight 1, since W specializes to the all-ones matrix. Hence
                                                   X             Y                 X             Y
(9.5)          J(α,β),(a,b) = (m − 1 − r)!                           Ui,ρ(i)                         Vθ(j),j .
                                             ρ:T ,→[m]\{b} i∈T                 θ:T ,→[m]\{a} j∈T



                                                           136
This is the general counterpart of the four elementary matching counts in the warm-up. To see
the row–column separation in a form that proves invertibility, we now express each injection
sum as the evaluation of a univariate polynomial.
Step 4: Encode forbidden-column
P
                                    choices by univariate polynomials. For P ⊆ E, let DP =
          u and H = P            Q       2u
  eu ∈P 2        P      ρ:P ,→[m] eu ∈P pρ(eu ) . Here HP is the total weight of injections into all
m external columns; in particular, H∅ = 1. Define gP ∈ C[z] recursively by
                                                            X         u
(9.6)             g∅ (z) = 1,          gP (z) = HP −                z 2 gP \{eu } (z)       for P 6= ∅.
                                                           eu ∈P

To interpret this recursion, fix b. An injection from P into [m] either avoids b or maps exactly
one index eu ∈ P to b. In the latter case, the remaining indices form an injection from P \ {eu }
                                                     u
that avoids b, and the chosen index contributes p2b . Consequently, subtracting all injections
that use b from the unrestricted sum HP gives precisely the recursion (9.6) evaluated at z = pb .
Induction on |P | therefore yields
                           X         Y
                                                                                    [z DP ]gP (z) = (−1)|P | |P |!.
                                                u
(9.7)     gP (pb ) =                         p2ρ(eu ) ,    deg gP = DP ,
                       ρ:P ,→[m]\{b} eu ∈P

For completeness, the degree and leading coeﬀicient follow from the same induction. For P 6= ∅,
                                         u
HP is constant, whereas each term z 2 gP \{eu } (z) in (9.6) has degree DP and leading coeﬀicient
(−1)|P |−1 (|P | − 1)!. The preceding minus sign and the |P | choices of eu give the claimed
                                                      P
coeﬀicient (−1)|P | |P |!. In particular, g{e0 } (z) = b pb − z, recovering the first factor in the
example. These leading coeﬀicients are nonzero because the ground field has characteristic
zero.
   The row-side construction is identical. For Q ⊆ F , put
                                       X                             X        Y         v
                              DQ =             2v ,       KQ =                      2
                                                                                   qθ(f v)
                                                                                           ,
                                       fv ∈Q                     θ:Q,→[m] fv ∈Q

and recursively define
                                                            X         v
                 h∅ (z) = 1,           hQ (z) = KQ −                z 2 hQ\{fv } (z)        for Q 6= ∅.
                                                            fv ∈Q

Partitioning row injections according to whether they use the forbidden row a proves
                           X         Y
                                                                                    [z DQ ]hQ (z) = (−1)|Q| |Q|!.
                                              2 v
(9.8)    hQ (qa ) =                          qθ(f v)
                                                     ,    deg hQ = DQ ,
                       θ:Q,→[m]\{a} fv ∈Q

At this point the nontrivial weighted choices have been isolated: gP (pb ) records the P -indices
that choose external columns, and hQ (qa ) records the Q-indices that choose external rows. It
remains to account for indices whose edge weights are 1 and then prove that the resulting
evaluation matrices have full rank.
Step 5: Factor the Jacobian entries. Write (M )s = M (M − 1) · · · (M − s + 1) and (M )0 = 1.
In the first sum of (9.5), choose the images of P first. Their total weight is gP (pb ) by (9.7).
Because every index in Q has U -weight one, each such injection has exactly (m − 1 − |P |)|Q|
extensions to the labeled indices in Q: there are m − 1 − |P | available external columns for
the first index, one fewer for the next, and so on. Similarly, in the second sum first choose the
images of Q. Their total weight is hQ (qa ), and each choice has (m − 1 − |Q|)|P | extensions to
the indices in P , all with V -weight one.
  Substituting these two counts into (9.5) separates the column parameter pb from the row
parameter qa :
(9.9)        J(α,β),(a,b) = LP,Q gP (pb )hQ (qa ),
(9.10)            LP,Q = (m − 1 − |P | − |Q|)!(m − 1 − |P |)|Q| (m − 1 − |Q|)|P | 6= 0.
All factors are nonzero because |P | + |Q| ≤ m − 1; in particular, every falling factorial counts
injections that actually exist. The scalar LP,Q depends on the selected coeﬀicient, but not on
the external row a or column b.


                                                          137
Step 6: Apply two Vandermonde matrices. Since DP (α) = α and DQ(β) = β, the evaluation
matrices Ap = (gP (α) (pb ))b,α and Aq = (hQ(β) (qa ))a,β are invertible. Indeed, (9.7) shows that
the polynomials
                                 gP (0) (z), gP (1) (z), . . . , gP (m−1) (z)
have respective degrees 0, 1, . . . , m − 1 and nonzero leading coeﬀicients. Their coeﬀicient matrix
in the monomial basis 1, z, . . . , z m−1 is therefore triangular with nonzero diagonal. Evaluating
at the distinct points p1 , . . . , pm multiplies this coeﬀicient matrix by the Vandermonde matrix
(pjb )b∈[m], 0≤j<m , which is invertible because the pb are distinct. Thus Ap is invertible. The same
argument, using (9.8) and the distinct qa , proves that Aq is invertible.
                                                                                p ⊗Aq and is therefore
    After permuting columns, the matrix gP (α) (pb )hQ(β) (qa ) (α,β),(a,b) is AT   T

invertible. By (9.9), J differs from it only by the nonzero row scalars (9.10). Hence det J 6=
0. The m2 selected coeﬀicients are consequently algebraically independent by the Jacobian
criterion, giving tdY (pern ) ≥ m2 .                                                                □

                 10. Formula lower bounds with and without division
   We have established the two local ingredients needed for a formula lower bound. For a match-
ing Y of k = O(log n) matrix entries, Lem. 9.1 produces m2 = Ω(n2 ) algebraically independent
Y -coeﬀicients of pern . If the formula has no division, Lem. 8.1 charges those coeﬀicients to
occurrences of the variables in Y . Our first task is to select many matchings for which the re-
sulting occurrence charges do not overlap. We then extend the charging argument to formulas
with division by showing that rational operations along a path with only one marked child at
each gate contribute only a constant number of field parameters.

10.1. Packing matchings and the division-free bound. Throughout this section, k =
2dlog2 ne and m = n − k are the parameters from (9.1). The useful notion of disjointness
concerns matrix entries, not their rows and columns: two matchings may use the same row or
the same column, as long as they never contain the same variable xij . This weaker condition is
exactly what prevents a variable-labeled leaf from being charged to two different matchings.

Proof of Thm. 1.2. Index the rows and columns by {0, . . . , n − 1}. For a cyclic offset 0 ≤ τ < n
and a row-block index 0 ≤ j < bn/kc, define
                             Yτ,j = {xjk+r, (jk+r+τ ) mod n : 0 ≤ r < k}.
Each Yτ,j is a matching: its k row indices are distinct, and adding the fixed offset τ modulo
n sends them to k distinct column indices. Moreover, any entry in one of these matchings
determines its parameters uniquely. Its row index i determines j = bi/kc, and its column-
minus-row difference modulo n determines τ . Thus the matchings are pairwise entry-disjoint
even though different matchings can share rows and columns.
  There are n choices of τ and bn/kc choices of j, so their total number is
                                                 
                                                 n   n2
(10.1)                                   ν=n       ≥    ,
                                                 k   2k
where the inequality follows from k ≤ n/2 and bxc ≥ x/2 for x ≥ 2.
   Every matrix variable must occur at least once in Φ: otherwise its output would be inde-
pendent of that variable, whereas ∂ pern /∂xij is the nonzero permanent of the complementary
(n − 1) × (n − 1) submatrix. In particular, tY (Φ) ≥ 1 for every selected matching Y , so Lem. 8.1
applies. Together with Lem. 9.1, it gives the per-matching requirement
                                    m2 ≤ tdY (pern ) ≤ 4tY (Φ).
In words, a matching containing only k = O(log n) distinct variables must account for at least
m2 /4 = Ω(n2 ) variable-labeled leaves, counted with repetition.
   Because the matchings are entry-disjoint,
                                          P
                                              a leaf labeled by xij contributes to at most one
of the numbers tY (Φ). Consequently, Y tY (Φ) ≤ Lvar (Φ). Summing the preceding local


                                                 138
requirement, and then using (10.1), m ≥ n/2, and k ≤ 4 log2 n, gives
                                          X              νm2   n 2 m2
                             Lvar (Φ) ≥       tY (Φ) ≥       ≥
                                          Y
                                                          4      8k
                                           n4      n4
                                      ≥       ≥            .
                                          32k   128 log2 n
The total leaf and vertex counts are at least the number Lvar (Φ) of variable-labeled leaves.
Finally, a rooted binary formula with L(Φ) leaves has exactly G(Φ) = L(Φ) − 1 internal gates.
Since the permanent is nonconstant and n ≥ 32, L(Φ) ≥ 2, and hence G(Φ) ≥ L(Φ)/2 ≥
Lvar (Φ)/2. This gives the stated gate bound as well.                                      □

10.2. Allowing division: recovering a coeﬀicient field. To extend the argument, fix a
nonempty set Y of marked variables, let Z contain all remaining variables, and put R = C(Z).
A formula with division is evaluated symbolically in the rational-function field
                                        C(Y, Z) = R(Y ).
Validity means that the denominator at each division gate is a nonzero element of this field;
it does not require the denominator to be nonzero after every numerical specialization of Z.
In particular, the point used in (9.3)–(9.4) to prove algebraic independence might make some
denominator of the formula vanish. This causes no problem: that point is applied only to the
polynomial coeﬀicients of pern , not to the rational formula or any of its gates.
   The new diﬀiculty is that a division formula may represent its output using rational expres-
sions in the marked variables. Merely placing the output in a small rational-function field K(Y )
does not immediately say that its polynomial coeﬀicients belong to K. The next elementary
observation supplies precisely that missing implication.
Lemma 10.1. For fields K ⊆ E and a finite set Y of indeterminates, K(Y ) ∩ E[Y ] = K[Y ]
inside E(Y ).
Proof. The inclusion K[Y ] ⊆ K(Y ) ∩ E[Y ] is immediate. Conversely, suppose f ∈ K(Y ) ∩ E[Y ].
Membership in K(Y ) gives polynomials P, Q ∈ K[Y ] with Q 6= 0 and
                                     Qf = P           in E[Y ].
To compare the coeﬀicients in E with those in K, regard E as a K-vector space. Extend a basis
of its one-dimensional subspace K ⊆ E to a basis of E, and let π : E → K be the associated
K-linear projection. Thus π fixes every element of K. Apply π coeﬀicientwise to polynomials
in E[Y ], writing π∗ for the resulting map.
   Although π need not preserve products of arbitrary elements of E, its K-linearity ensures
that it commutes with multiplication by the polynomial Q ∈ K[Y ]. Therefore
                                Qπ∗ (f ) = π∗ (Qf ) = π∗ (P ) = P.
Subtracting from Qf = P gives Q(f − π∗ (f )) = 0. Since E[Y ] is an integral domain and Q 6= 0,
we conclude that f = π∗ (f ) ∈ K[Y ], as required.                                           □
   It remains to find a small field K containing the rational parameters that genuinely influence
the marked variables. As in the division-free argument, mark each vertex whose subformula
contains a Y -labeled leaf. A maximal path of gates with only one marked child can contain
many unmarked computations, but all of its influence is captured by one fractional linear trans-
formation. The essential count is therefore charged at gates where two marked subformulas
meet.
Lemma 10.2. Suppose that a valid formula with division computes a polynomial f ∈ C[Y, Z]
and contains t ≥ 1 leaves labeled by variables in Y . Then tdY (f ) ≤ 6t − 3 < 6t.
Proof. Put R = C(Z), and mark precisely those vertices having at least one Y -labeled descen-
dant. At a gate with one marked child, the other child has no marked leaves and therefore


                                                139
computes a rational function h ∈ R. If the marked child computes u ∈ R(Y ), the possible
outputs are
                        u + h, u − h, h − u, hu, u/h, h/u,
where validity requires h 6= 0 for u/h and u 6= 0 for h/u. Every such operation has the fractional
linear form                                                 
                                    au + b               a b
                             u 7−→         ,    M=             ∈ R2×2 .
                                    cu + d               c d
For example, the transformations u + h, hu, u/h, and h/u are represented, respectively, by
                                                                        
                           1 h             h 0                1 0          0 h
                               ,               ,                  ,            .
                           0 1             0 1                0 h          1 0
It is important not to require these matrices to be invertible. When h = 0, multiplication by h
is a valid constant-zero operation represented by the singular, but nonzero, second matrix.
   Composition of fractional linear transformations corresponds to multiplication of their rep-
resenting matrices. Moreover, although singular matrices are allowed, the composite matrix
for a valid marked path cannot become the zero matrix. To see this, suppose that the current
marked value is
                                     aj u0 + bj
                               uj =             ,   cj u0 + dj 6= 0,
                                     cj u0 + dj
and the next unary marked gate applies u 7→ (au + b)/(cu + d). The denominator represented
by the composite matrix is
               c(aj u0 + bj ) + d(cj u0 + dj ) = (cj u0 + dj )(cuj + d) 6= 0       in R(Y ).
The first factor is nonzero by the inductive representation, and the second is nonzero because the
gate is valid. In particular, the composite matrix has a nonzero entry. Dividing all four entries
by any one nonzero entry leaves the represented rational function unchanged and normalizes
that entry to 1. Such a normalized matrix is therefore described by at most three elements of
R, even when it is singular.
  We now prove the following more precise invariant by induction on a marked subformula with
s ≥ 1 marked leaves: its output can be written as
                     ag + b
                            ,       g ∈ C(Γ)(Y ),         Γ ⊆ R,      |Γ| ≤ 6s − 6,
                     cg + d
for some matrix over R, with cg + d 6= 0 in R(Y ). The outer matrix is deliberately not counted
in Γ until the subformula meets another marked subformula or reaches the root.
   For a marked leaf labeled by y ∈ Y , take g = y, Γ = ∅, and the identity matrix. If the
root gate of the subformula has only one marked child, compose its fractional linear transfor-
mation with the child’s outer matrix. The preceding validity argument shows that the resulting
denominator remains nonzero, and no new element needs to be added to Γ.
   Suppose instead that the gate has two marked children with s1 , s2 ≥ 1 marked leaves. Nor-
malize each child’s outer matrix and adjoin its at most three nontrivial entries to the union of
the two existing parameter sets. If Γ denotes the resulting set, both child outputs belong to the
single field C(Γ)(Y ). Apply the gate operation to these two outputs, use the resulting rational
function as the new inner function g, and take the identity as the new outer matrix. When
the operation is division, the divisor is nonzero in R(Y ) by validity, hence also nonzero in the
subfield C(Γ)(Y ); thus the new inner function is well-defined. Finally, because s = s1 + s2 , the
parameter count is at most
                            (6s1 − 6) + (6s2 − 6) + 6 = 6(s1 + s2 ) − 6.
This completes the induction.
   At the formula root, the invariant gives at most 6t − 6 parameters for the inner function.
Normalize the final outer matrix and adjoin its at most three remaining entries. We obtain a
set Γ0 ⊆ R satisfying
                                  |Γ0 | ≤ (6t − 6) + 3 = 6t − 3


                                                    140
such that the complete formula output belongs to K(Y ), where K = C(Γ0 ) ⊆ R. On the other
hand, the hypothesis that the output is a polynomial gives f ∈ C[Y, Z] ⊆ R[Y ]. Applying
Lem. 10.1 with E = R therefore yields
                                   f ∈ K(Y ) ∩ R[Y ] = K[Y ].
Thus every coeﬀicient of f as a polynomial in Y belongs to the same field K. Since a field
generated by |Γ0 | elements has transcendence degree at most |Γ0 |,
                            tdY (f ) ≤ trdegC K ≤ |Γ0 | ≤ 6t − 3 < 6t.
This is the desired division-formula analogue of Lem. 8.1.                                       □

10.3. Completing the lower bound with division. The coeﬀicient-independence construc-
tion is a property of the permanent itself and therefore remains unchanged when the formula is
allowed to use division. Only its translation into a lower bound on marked occurrences changes,
from a factor of 4 to a factor of 6.

Proof of Thm. 1.3. Use the same parameters (9.1) and the same ν pairwise entry-disjoint match-
ings constructed in (10.1). If some matching Y contributes no variable-labeled leaf, every gate
of the formula belongs to the rational-function field C(X \ Y ). Its output would then be inde-
pendent of all variables in Y , contradicting its equality to pern . Therefore tY (Φ) ≥ 1 for every
selected matching, as required to apply Lem. 10.2.
   For each matching, Lem. 9.1 and Lem. 10.2 now give
                            m2 ≤ tdY (pern ) ≤ 6tY (Φ) − 3 < 6tY (Φ).
As before, entry-disjointness guarantees that no variable-labeled leaf is charged twice. Summing
over all ν matchings, and using m ≥ n/2 and k ≤ 4 log2 n, yields
                                           X              νm2   n 2 m2
                              Lvar (Φ) ≥       tY (Φ) ≥       ≥
                                           Y
                                                           6     12k
                                            n4      n4
                                      ≥        ≥            .
                                           48k   192 log2 n
Finally, allowing division changes the allowed labels of internal gates but does not change the
fact that the formula is a rooted binary tree. Consequently, L(Φ) ≥ Lvar (Φ) and G(Φ) =
L(Φ) − 1 ≥ L(Φ)/2, giving the remaining leaf, vertex, and gate bounds exactly as in the
division-free case.                                                                          □

                          11. Comparison with the determinant
   For the generic determinant, the known unrestricted formula bounds are Ω(n3 ) and nO(log n) .
The lower bound holds even with division [Kal85], while the upper bound follows by unfolding
the polynomial-size, O(log2 n)-depth circuits of [Ber84]. It is therefore natural to ask whether
either of our permanent arguments also improves the corresponding determinant bound. We
show that the answer is negative for two separate reasons. On the formula side, the coeﬀicients
associated with a small set of determinant entries satisfy many algebraic relations. On the
circuit side, every homogeneous specialization of the determinant has a critical locus that is too
large for our geometric certificate to give a superquadratic bound.

11.1. Coeﬀicient independence and a cubic formula ceiling. The formula argument re-
quires many algebraically independent coeﬀicients for small, entry-disjoint sets of variables.
Recall that tdY (f ) counts the maximum number of algebraically independent coeﬀicients ob-
tained by expanding f in the variables of Y ; those coeﬀicients are polynomials in the remaining
variables. For the permanent, a matching of only O(log n) entries contributes Ω(n2 ) independent
coeﬀicients. We first explain why this crucial feature fails for the determinant.


                                                 141
   Let Y be a matching of k < n entries of a generic n × n matrix X. Permuting rows and
columns moves its marked entries to the first k diagonal positions. Separate the corresponding
rows and columns from the others, and write
                                            
                       diag(Y ) + D0 U
              X=                       ,             δ = det W,             S = D0 − U W −1 V.
                             V       W
Here diag(Y ) is the k ×k diagonal matrix of marked variables, D0 contains the unmarked entries
of the same block and has zero diagonal, and U, V, W also contain only unmarked variables.
The complementary block W is a generic (n − k) × (n − k) matrix, so its determinant δ is
a nonzero polynomial. Consequently, W is invertible over the rational-function field of the
unmarked variables: its entries need not be invertible as polynomials, but W −1 = adj(W )/δ is
a well-defined matrix of rational functions. The Schur complement identity then gives
                                                                        
                                     det X = δ det diag(Y ) + S .
Although the right-hand side uses rational functions to describe the coeﬀicients, the identity
holds in the rational-function field, and its left-hand side is still the original polynomial.
   To read off an individual coeﬀicient, let T ⊆ [k]. In the determinant expansion, selecting yi
for every i ∈ T fixes those rows and columns to their diagonal positions. The remaining rows
and columns therefore contribute the principal minor on [k] \ T :
                                "           #
                                    Y
                                          yi det X = δ det S[k]\T,[k]\T ,
                                    i∈T
where the determinant of an empty matrix is 1. Thus every Y -coeﬀicient belongs to the field
generated by the single element δ and the k 2 entries of S. A field generated by k 2 + 1 elements
has transcendence degree at most k 2 + 1, and hence
                                           tdY (det X) ≤ k 2 + 1.
Consequently, matchings of size O(log n) yield at most O(log2 n) independent coeﬀicients for
the determinant, whereas §9 produces Ω(n2 ) independent coeﬀicients for the permanent. The
determinant’s Schur complement compresses a potentially exponential family of coeﬀicients into
only O(k 2 ) parameters.
   One might try to recover a stronger formula lower bound by choosing marked entries that
are not a matching. The same obstruction still applies. Suppose Y is any nonempty set of k
marked entries, where 1 ≤ k < n. Its occupied row set and occupied column set each have
size at most k; enlarge the smaller set, if necessary, so both have a common size s ≤ k. After
permuting rows and columns, all marked entries lie in the upper-left s × s block, which we write
as B(Y ) + D0 . Here B(Y ) contains the marked variables and vanishes in the other positions,
while D0 contains the unmarked entries. Because s < n, the complementary block W is again
generically invertible. The Schur complement expresses every Y -coeﬀicient in the field generated
by δ = det W and the s2 entries of D0 − U W −1 V . Therefore tdY (det X) ≤ s2 + 1 ≤ nk. For
the last inequality, s ≤ k < n implies s2 + 1 ≤ k 2 + 1 ≤ nk. If k ≥ n, we instead use the trivial
bound tdY (det X) ≤ n2 ≤ nk: there are only n2 matrix variables in total.
   We have therefore proved tdY (det X) ≤ n|Y | for every nonempty block Y . If Y1 , . . . , Yq are
pairwise entry-disjoint, then their total size is at most n2 , and summing the individual bounds
gives
                                X
                                q                          X
                                                           q
(11.1)                                tdYj (det X) ≤ n           |Yj | ≤ n3 .
                                j=1                        j=1

Thus summing blockwise coeﬀicient transcendence degrees cannot give a supercubic determinant
formula lower bound, regardless of how the entry-disjoint blocks are chosen.
11.2. Full matchings recover the cubic determinant bound. The cubic ceiling is not
merely an upper limit on what this method might prove: using full matchings, the same method
actually recovers a cubic lower bound. Let Y consist of all n diagonal entries, and write
                                 X = diag(Y ) + A,                aii = 0.


                                                     142
Expanding as above, the Y -coeﬀicients are exactly the principal minors of the zero-diagonal
matrix A; a principal minor indexed by I ⊆ [n] is det AI,I .
   The first question is how many of these principal minors can be algebraically independent.
If D is an invertible diagonal matrix, then
                                                             −1
                                    (DAD−1 )I,I = DI,I AI,I DI,I ,
so diagonal conjugation leaves every principal minor unchanged. On the generic open set where
a1i 6= 0 for i > 1, choose λi = a1i and D = diag(1, λ2 , . . . , λn ). The matrix B = DAD−1
satisfies b1i = 1 for every i > 1. Conversely, A = D−1 BD, so the original off-diagonal entries
are birationally equivalent to the n − 1 nonzero parameters λi together with the remaining
normalized entries of B. The latter entries are therefore algebraically independent, and their
number is
                                  n(n − 1) − (n − 1) = (n − 1)2
because the normalization fixes precisely the n − 1 first-row entries. In particular, all principal
minors belong to the rational-function field generated by these (n−1)2 normalized entries. That
field has transcendence degree (n − 1)2 , giving the corresponding upper bound.
   For the matching lower bound, it is enough to recover all normalized entries up to algebraic
ambiguity from the principal minors. Continue to write A for the normalized matrix, and set
ti = ai1 for i > 1. For distinct i, j > 1, its principal minors of sizes two and three are
                                    det A{1,i},{1,i} = −ti ,
                                     det A{i,j},{i,j} = −aij aji ,
                                  det A{1,i,j},{1,i,j} = aij tj + aji ti .
Thus the field generated by the principal minors contains ti , the product pij = aij aji , and the
linear combination qij = aij tj + aji ti . Multiplying the last identity by aij gives
                                      tj a2ij − qij aij + pij ti = 0.
Its leading coeﬀicient tj is a nonzero rational function, so aij is algebraic of degree at most two
over the field of principal minors; the same argument applies to aji . Every normalized entry is
consequently algebraic over that field. Algebraic extensions preserve transcendence degree, so
the upper bound established by normalization is attained:
                                       tdY (det X) = (n − 1)2 .
  Now let Φ be a formula computing det X, and partition all n2 entries into the n cyclic full
matchings
                     Yτ = {xi,(i+τ ) mod n : 0 ≤ i < n}, 0 ≤ τ < n,
where rows and columns are indexed by {0, . . . , n − 1}. Each matching has coeﬀicient tran-
scendence degree (n − 1)2 by the preceding argument, since row and column permutations only
relabel the entries. If the formula is division-free, Lem. 8.1 gives (n − 1)2 ≤ 4tYτ (Φ) − 2. If it
permits valid division, Lem. 10.2 instead gives (n − 1)2 ≤ 6tYτ (Φ) − 3. Summing over the n
disjoint matchings therefore yields
                                n((n − 1)2 + 2)                         n((n − 1)2 + 3)
                   Lvar (Φ) ≥                   ,         Lvar (Φ) ≥
                                      4                                       6
without division and with valid division. Thus the cubic ceiling in (11.1) is attained up to a
constant factor.

11.3. Critical loci obstruct the geometric circuit argument. The circuit proof needs an
aﬀine specialization with many active variables, reasonably high degree, and a critical locus of
large codimension. We first inspect the determinant analogue of the specialization used for the
permanent, and then show that the obstruction persists for every homogeneous determinant
specialization.


                                                    143
  Replacing the permanent by the determinant in the example from §2 gives
                                        
                         u   v   1 1
                       w    z   1 1                                     
                   det 
                       p
                                      = 4 (u − w)(q − s) − (v − z)(p − r) ,
                             q   2 −2
                         r   s   2 −2
a single 2×2 determinant rather than a sum of independent block permanents. The cancellations
have compressed all the variable dependence into a much smaller matrix.
   More generally, suppose 2 ≤ d ≤ min{r, s}, and let X, U, V have respective sizes r × s,
r × (r − d), and (s − d) × s, with U, V constant. The block matrix
                                                           
                                                   X U
                                                   V 0
is square of size r + s − d. If U fails to have full column rank, its last r − d columns are linearly
dependent. If V fails to have full row rank, its last s − d rows are linearly dependent. In either
case the determinant is identically zero.
   Suppose therefore that U and V have their full respective ranks. Choose a full-row-rank d × r
matrix A whose rows span the left kernel of U , so AU = 0. Likewise, choose a full-column-rank
s × d matrix C whose columns span the kernel of V , so V C = 0. Constant changes of basis
separating these kernels from complementary subspaces give
                                                  
                                             X U
                                   det                 = c det(AXC),
                                             V 0
where c 6= 0 depends only on the constant basis changes. In other words, the original deter-
minant retains only the induced map from the d-dimensional kernel of V to the d-dimensional
quotient by the image of U .
    The linear map X 7→ AXC is surjective onto the space of d×d matrices. Indeed, full row rank
provides a right inverse A0 with AA0 = Id , while full column rank provides a left inverse C 0 with
C 0 C = Id ; for any d × d matrix H, taking X = A0 HC 0 gives AXC = H. The first derivatives
of a determinant are its (d − 1) × (d − 1) cofactors. They vanish simultaneously precisely when
the matrix has rank at most d − 2. The space of d × d matrices of rank at most r has dimension
r(2d − r): a rank-r factorization has two d × r factors, with r2 parameters accounting for their
common change of basis. Taking r = d − 2, its codimension in the d2 -dimensional matrix space
is
                                                               2
                            d2 − (d − 2)(d + 2) = d − (d − 2) = 4.
If L(X) = AXC, the chain rule gives d(det ◦L)X = L∗ (d detL(X) ). Surjectivity of L makes its
dual L∗ injective, so the critical locus is exactly the inverse image of the smaller determinant’s
critical locus. Moreover, choosing a complementary subspace to ker L identifies the domain
with ker L ⊕ Cd×d . Under this identification, an inverse image is a product with ker L, which
preserves codimension. The specialized determinant therefore also has critical-locus codimension
4. Thus this block construction cannot provide the Θ(n2 ) critical-locus codimension that drove
the permanent circuit bound.
   Importantly, changing the specialization does not resolve the problem. Let n ≥ 5, and
obtain P by substituting aﬀine linear forms into detn . Suppose that the resulting polynomial is
homogeneous of degree d > 2. For a homogeneous polynomial of degree d, Euler’s identity says
                                                   X            ∂P
                                      dP (x) =             xi       (x).
                                                       i
                                                                ∂xi
Because the ground field has characteristic zero, every critical point of P also satisfies P (x) = 0.
Consequently, Crit(P ) is exactly the singular locus of the hypersurface defined by P = 0.
   Recall that the determinantal complexity dc(P ) is the smallest size of a matrix of aﬀine
linear forms having determinant P . Since P itself is an aﬀine specialization of detn , the original
specialization provides such a representation of size n; therefore dc(P ) ≤ n. If codim Crit(P ) >
4, then [ABV17, Thm. 1.2] implies codim Crit(P ) + 1 ≤ dc(P ) ≤ n: the singular locus of a


                                                   144
polynomial with a small determinantal representation cannot have arbitrarily large codimension.
Otherwise, codim Crit(P ) ≤ 4 ≤ n − 1. In either case,
                                    codim Crit(P ) ≤ n − 1.
   Finally, the slicing parameter k in Lem. 4.2 cannot exceed the critical-locus codimension: its
hypothesis is precisely dim Crit(P ) ≤ m−k, where m is the number of variables of P . Therefore
k ≤ n − 1. Also d ≤ n, since substituting aﬀine linear forms into a degree-n determinant cannot
increase its degree. The largest circuit lower bound obtainable from (4.2) is consequently
                              k log2 (d − 1)   (n − 1) log2 (n − 1)
                                             ≤                      .
                                     3                   3
For d = 2, the certificate is zero because log2 (d − 1) = 0. Even for larger degrees, it is only
O(n log n). This is below the elementary n2 − 1 gate lower bound: the determinant depends on
all n2 individual input variables, and combining n2 distinct inputs into one output with binary
arithmetic gates requires at least n2 − 1 gates. Thus this method, in its present form, cannot
establish a superquadratic determinant lower bound.


                                     12. Related work
   The two lower bounds interact with several bodies of work that use similar words for sub-
stantially different computational models and complexity measures. We first distinguish those
models and recall their established bounds. We then place the geometric circuit proof, the
coeﬀicient-independence formula proof, and the restricted-depth literature in their respective
contexts. In particular, a lower bound for representing a polynomial as a determinant, a lower
bound for general arithmetic circuits, and a lower bound for formulas are logically different
statements.

12.1. Historical bounds and computational models. The modern complexity-theoretic
comparison between permanent and determinant begins with two distinct results of Valiant.
His algebraic completeness theorem makes the permanent complete for VNP over fields of char-
acteristic different from two [Val79a]. Here completeness concerns families of polynomials and
arithmetic projections: variables of one polynomial are replaced by variables or field constants
to obtain another polynomial. His separate counting-complexity theorem proves that evaluating
the permanent of a zero–one matrix is #P-complete [Val79b]. The two results motivate related
questions, but one concerns symbolic arithmetic computation and the other a Boolean counting
problem. In characteristic two, the determinant and permanent coincide, so even the distinction
between the two polynomials depends on the ground field.
   Several surveys describe this broader landscape. Bürgisser–Clausen–Shokrollahi [BCS97],
Shpilka–Yehudayoff [SY10], and Kayal–Saptharishi [KS14] introduce algebraic complexity and
arithmetic lower-bound methods. Bürgisser surveys algebraic completeness classes [Bür24];
Chen–Kayal–Wigderson survey partial-derivative techniques [CKW11]; and Bürgisser, Lands-
berg, Manivel, and Weyman [BLMW11], together with Bläser and Ikenmeyer [BI25], discuss
geometric complexity theory.
   It is important to distinguish three models. An unrestricted arithmetic circuit may reuse any
previously computed intermediate value. A formula is a circuit whose underlying graph is a tree,
so every reuse must instead be recomputed. A determinantal representation of f is an expression
f = det(A) for a matrix A of aﬀine linear forms; its minimum matrix dimension is the determi-
nantal complexity dc(f ). The determinant is complete, under polynomial-size projections, for al-
gebraic branching programs, or equivalently weakly skew circuits. It is not known to be complete
for unrestricted polynomial-size arithmetic circuits [MP08]. Consequently, a superpolynomial
lower bound on dc(pern ) separates the permanent from the branching-program/weakly-skew
model but does not by itself establish VP 6= VNP for general circuits.
   There is nevertheless a weaker connection to the general-circuit model. Valiant’s determinant
simulation, together with circuit balancing, transforms a polynomial-size general circuit into a


                                               145
quasipolynomial-size determinantal representation [Val79a, VSBR83, BI25]. A superquasipoly-
nomial lower bound on determinantal complexity would therefore rule out polynomial-size gen-
eral circuits, whereas a merely superpolynomial determinantal bound would not. The distinc-
tion matters for Thm. 1.1: its lower bound concerns the number of gates in an unrestricted
division-free circuit directly, not the dimension of a determinantal representation.
   Write N = n2 for the number of entries of an n × n matrix. Before the present result, the
general-circuit lower bound known specifically for either detn or pern was only Ω(n2 ) = Ω(N ).
The classical Ω(N log d) lower bounds of Strassen and Baur–Strassen apply to other explicit
degree-d polynomial families, such as sums of powers; they do not assert the same bound for
either matrix polynomial [Str73a, BS83, KS14]. Thm. 1.1 instead establishes the permanent-
specific bound Ω(N log log N ) for division-free circuits. It neither proves such a bound for the
determinant nor treats circuits with division.
   For upper bounds, the determinant has polynomial-size division-free circuits [Ber84]. Balanc-
ing and unfolding suitable circuits gives determinant formulas of size nO(log n) [Hya79, VSBR83].
For the permanent, Ryser’s inclusion–exclusion identity yields exponential-size circuits and, if
intermediate computations cannot be shared, formulas of size O(n2 2n ) [Rys63].
   For unrestricted division-free formulas, the previous lower bounds for both matrix polynomi-
als were Ω(n3 ) = Ω(N 3/2 ) [Kal85, KS14]. Kalorkoti’s determinant lower bound even permits
rational formulas with valid division [Kal85]; his published result should not be interpreted
as the corresponding division-formula theorem for the permanent. Thms. 1.2 and 1.3 raise
the permanent-specific bounds to Ω(n4 / log n) = Ω(N 2 / log N ) without division and with valid
division, respectively. This comparison is specific to the permanent: for a different explicit
polynomial, Chatterjee–Kumar–She–Volk prove an Ω(N 2 ) unrestricted formula lower bound for
a suitable elementary symmetric polynomial [CKSV22]. Raz’s nΩ(log n) bounds for the determi-
nant and permanent are numerically stronger but concern syntactically multilinear formulas, a
restricted model rather than the general formulas considered here [Raz09].

12.2. Determinantal representations and geometric lower bounds. The permanent-
versus-determinant problem is often stated in terms of determinantal representations: how
large must a matrix of aﬀine linear forms be if its determinant is pern ? Early work of von zur
Gathen and Cai studied versions of this projection problem [vzG87, Cai90]. Mignon–Ressayre
proved
                                                       n2
                                           dc(pern ) ≥
                                                        2
over characteristic zero by comparing Hessians at suitable points [MR04]. Cai–Chen–Li extend a
quadratic bound to fields of characteristic different from two [CCL10]; in the opposite direction,
Grenet gives determinantal representations of size 2n − 1 [Gre12].
   There are also geometric variants in which the permanent is allowed to arise as a limit of
determinantal representations. Landsberg–Manivel–Ressayre obtain quadratic lower bounds
for this border determinantal complexity using dual varieties [LMR13]. Mulmuley–Sohoni place
determinantal representation and orbit-closure questions in the representation-theoretic frame-
work of geometric complexity theory [MS01]. All these results measure the dimension of a
determinant representation, or its border analogue. They are not lower bounds on the number
of gates in an arbitrary arithmetic circuit, and therefore should not be confused with prior
superquadratic general-circuit bounds.
   The geometric quantity relevant to the present paper is more elementary to describe. If P is
a polynomial in m variables, its critical locus Crit(P ) is the set where all first partial derivatives
vanish; its codimension in the ambient aﬀine space Cm is m−dim Crit(P ). The singular locus of
the hypersurface P = 0 additionally requires P = 0; its codimension here is likewise measured
in Cm , not inside the hypersurface. For a homogeneous polynomial of positive degree over C,
Euler’s identity implies that the derivative equations already force P = 0, so these two loci
agree.
   These loci have several antecedents in algebraic complexity. Alper–Bogart–Velasco lower-
bound determinantal complexity using the codimension of the singular locus and determine


                                                 146
the exact determinantal complexity of the 3 × 3 permanent [ABV17]. Chatterjee–Kumar–
She–Volk use the common zero set of first derivatives for quadratic branching-program and
formula lower bounds [CKSV22], while Gesmundo–Ghosal–Ikenmeyer–Lysikov relate singular-
locus codimension to homogeneous branching-program complexity [GGIL22].
   Our use of the same geometric object is different. We first obtain a homogeneous polyno-
mial P by replacing entries of the permanent matrix with aﬀine linear forms. We then prove
that Crit(P ) has large codimension, choose a linear subspace avoiding its nonzero points, and
apply a degree bound to the restricted gradient map. The resulting lower bound concerns the
original unrestricted circuit directly; at no point do we identify circuit size with determinantal
complexity.
   The singular-locus theorem of Alper–Bogart–Velasco also makes the determinant obstruction
transparent. Suppose n ≥ 5, substitute aﬀine linear forms into detn , and assume the resulting
polynomial P is homogeneous of degree at least three. The specialization supplies an n × n
determinantal representation, so dc(P ) ≤ n. If codim Crit(P ) > 4, the singular-locus theorem in
[ABV17] gives codim Crit(P ) + 1 ≤ dc(P ) ≤ n. If the codimension is at most 4, the assumption
n ≥ 5 already bounds it by n − 1. Consequently, in either case,
                                     codim Crit(P ) ≤ n − 1.
Thus a determinant specialization cannot supply the Θ(n2 ) critical-locus codimension needed by
the present circuit argument. Section 11 explains the implication, including the low-codimension
case, in detail.
   A related literature studies the polynomial ideals generated by subpermanents. Lauben-
bacher and Swanson investigate permanental ideals [LS00]. Efremenko, Landsberg, Schenck,
and Weyman study minimal free resolutions of such ideals motivated by geometric complexity
theory [ELSW18a]. Boralevi, Carlini, Michałek, and Ventura give codimension bounds for per-
manental varieties [BCMV25]. In particular, their results imply that, for n ≥ 6, the critical
locus of the full permanent satisfies
                                   6 ≤ codim Crit(pern ) ≤ 2n.
The upper bound shows why applying our gradient argument directly to pern cannot work:
its critical-locus codimension is only O(n), rather than the Θ(n2 ) required in Prop. 4.3. The
specially constructed aﬀine specialization is therefore essential. There is also an important
distinction between the ideals themselves. The cited permanental ideal papers usually generate
an ideal from a collection of individual subpermanents, whereas §5 studies the first derivatives of
a single sum of subpermanents. These families of equations need not define the same geometric
object.
12.3. Differentiation, degree bounds, and the aﬀine specialization. Proposition 4.3
combines two classical ideas: eﬀicient simultaneous differentiation and a degree bound for
polynomial maps. Strassen used Bézout-type degree arguments to lower-bound the simulta-
neous computation of powers and elementary symmetric functions [Str73a]. Baur–Strassen
then showed that a straight-line program computing one polynomial f can be augmented to
compute f and all its first partial derivatives with only constant-factor overhead [BS83]. The
history and many applications of partial-derivative techniques are surveyed by Chen–Kayal–
Wigderson [CKW11]; the Nisan–Wigderson partial-derivative method is another important,
model-dependent development [NW97].
   The special polynomial
                                                                 X
                                                                 k
                                    f (x1 , . . . , xk ) = d−1         xdi
                                                                 i=1
makes the degree argument particularly transparent. Its gradient is (xd−1          d−1
                                                                      1 , . . . , xk ), and setting
                                                            k
these outputs equal to generic nonzero constants gives (d−1) distinct solutions. Computing the
same outputs with q multiplications produces a system containing q quadratic multiplication-
gate equations. Bézout’s inequality bounds the number of isolated solutions of that system
by 2q . Consequently (d − 1)k ≤ 2q , yielding q = Ω(k log d). This argument works because
the chosen gradient has an isolated common zero and a large generic fiber. Neither fact is an


                                                  147
automatic consequence of the degree and number of variables of an arbitrary polynomial, so
the classical Ω(k log d) conclusion cannot simply be substituted for a permanent or determinant
lower bound.
   The exact differentiation overhead also depends on the cost model. Proposition 4.3 counts
nonscalar multiplications and treats aﬀine operations as free. For an original product gate, one
forward multiplication and at most two reverse-mode multiplications suﬀice, giving the factor
three used there. The full Baur–Strassen theorem also accounts for additions, scalar operations,
and divisions; it does not justify the unqualified statement that a circuit with s total gates
always has a gradient circuit with at most 3s total gates [BS83]. Furthermore, reverse-mode
differentiation reuses intermediate values, an operation available to circuits but not to formulas.
Ramya–Shastri exhibit multi-output formula and planar-circuit separations demonstrating that
the analogous constant-overhead claim fails in those restricted models [RS26]. This is why the
formula argument needs its separate coeﬀicient-transcendence measure.
   The remaining ingredients of the circuit proof likewise have classical precedents. A multipli-
cation gate can be represented by a quadratic equation for its output; aﬀine Bézout bounds
the number of isolated common solutions; a generic linear slice avoids a suﬀiciently low-
dimensional critical locus; and the degree of the resulting finite gradient map counts a generic
fiber [Str73a, BS83, Hei83, KS14]. The challenge specific to the permanent is to construct a
specialization for which these standard tools apply simultaneously: the specialized polynomial
must have degree d  log n, retain Θ(n2 ) variables, and have critical-locus codimension Θ(n2 ).
   The first ingredient in that construction is the minor-sum polynomial Mt,s,d of (5.1). Its
monomials encode size-d matchings between the rows and columns of a t × s matrix; summing
the corresponding products is equivalent to summing all d × d permanental minors. To analyze
its derivatives, §5 rewrites sums over injective assignments of rows to columns in terms of
the power sums pB . This is Möbius inversion on the partition lattice: each partition records
which rows were assigned the same column, and its Möbius coeﬀicient corrects the resulting
overcount. The general incidence-algebra framework originates with Rota [Rot64]; the specific
permanental expansion is the rectangular Binet–Minc identity [Min79]. Forbes also uses this
identity for characteristic-independent set-multilinearization [For24].
   The second ingredient is realizing an appropriate sum of these minor-sum polynomials as
a single specialization of a larger permanent. Friedland–Levy already realize the sum of all
d × d permanental minors as a larger permanent by adjoining all-ones and zero blocks [FL06].
Lemma 6.1 refines that completion: it selects constant columns using roots of unity so that
the d upper rows not assigned to those constant columns all belong to a single row block. The
surviving terms therefore split into the separate block polynomials whose critical loci can be
bounded independently.
   The square-zero algebra used to verify this cancellation has its own precedents. Feinsilver–
McSorley use commuting square-zero “zeon” variables whose induced matrix coeﬀicients are per-
manents [FM11]; Butera–Pernici use commuting Grassmann-even nilpotent variables to encode
sums of permanental minors and bipartite matchings [BP15]. Signed and Fourier/root-of-unity
coeﬀicient filters likewise occur in Ryser’s and Glynn’s permanent identities and in Aaronson–
Hance’s generalized Glynn estimator [Rys63, Gly10, AH14]. These precedents supply the un-
derlying square-zero and cancellation ideas, but not the particular simultaneous block-selective
specialization of Lem. 6.1. For the determinant, complementary maximal minors instead satisfy
Plücker relations, obstructing the same block-supported pattern. The construction therefore
uses a structural difference between permanents and determinants rather than merely replacing
unsigned terms with signed ones.


12.4. Formula methods, coeﬀicient independence, and division. The formula argument
adapts a block-counting principle introduced in a different computational setting. Nečiporuk
partitioned the variables of a Boolean function and lower-bounded formula size by adding the
information required by the individual blocks [Nec66]. Kalorkoti translated this general idea to
rational arithmetic formulas using algebraic independence of coeﬀicient families [Kal85]. The
exposition in [KS14, §3.2] describes the corresponding arithmetic measure explicitly.


                                               148
   Concretely, choose a block Y of variables of a polynomial f and expand f as a polynomial in Y .
Its coeﬀicients are polynomials in the remaining variables. The coeﬀicient transcendence degree
tdY (f ) counts the maximum number of those coeﬀicients that are algebraically independent:
no nonzero polynomial relation with complex coeﬀicients holds among the chosen coeﬀicient
polynomials. A formula with few occurrences of variables from Y can introduce only few
independent coeﬀicients. If the variable blocks are disjoint, their occurrence requirements can
be added without counting any formula leaf twice. Applying this principle to n entry-disjoint
full diagonals of a matrix gives the classical Ω(n3 ) division-free formula bounds for both the
permanent and determinant.
   An especially close antecedent for the choice of blocks is work of Hrubeš–Joglekar [HJ25].
Their proof also selects a matching of Θ(log n) matrix entries, exploits a specialization of the
permanent on that matching, packs Θ(n2 / log n) pairwise entry-disjoint matchings, and adds the
resulting occurrence requirements. In the model of read-bounded determinantal representations,
they obtain
        √    an Ω(n5/2 / log n) lower bound on variable-containing matrix entries and rule out
read-o( n/ log n) representations. The present argument uses the same matching-and-packing
architecture in a different model. It proves that each short matching already produces Ω(n2 )
algebraically independent coeﬀicient polynomials, and charges this quantity directly to leaves
of an unrestricted arithmetic formula.
   The new independence witness can be understood through the Jacobian criterion. Over
characteristic zero, coeﬀicient polynomials are algebraically independent when an appropri-
ate Jacobian matrix has full rank. Lem. 9.1 specializes the unmarked matrix entries so that
this Jacobian factors into two Vandermonde evaluation matrices, one associated with an ex-
ternal row and the other with an external column. Their Kronecker product has full rank,
certifying Ω(n2 ) independent coeﬀicients for a matching of only O(log n) entries. Algebraic in-
dependence and the Jacobian criterion also play central roles in identity testing and restricted-
model lower bounds [BMS11]. In particular, Agrawal–Saha–Saptharishi–Saxena use Jacobian
and transcendence-degree methods to lower-bound all immanants, including the permanent
and determinant, in bounded-occurrence and bounded-transcendence-depth models [ASSS16].
Boralevi–Carlini–Michałek–Ventura also study algebraic independence of selected subperma-
nents [BCMV25], but their coeﬀicient families and geometric objectives differ from those in
Lem. 9.1.
   This block-based method has a nearly matching intrinsic ceiling. For an N -variate multilinear
polynomial and a block Y , its coeﬀicient contribution satisfies

                                  tdY (f ) ≤ min{2|Y | , N − |Y |}.

Indeed, multilinearity gives at most 2|Y | coeﬀicient polynomials, while those coeﬀicients involve
only the N −|Y | remaining variables. Summing this contribution over a partition of the variables
gives at most O(N 2 / log N ) in the usual Nečiporuk–Kalorkoti framework; see [CKSV22]. Hence
the permanent bound Ω(N 2 / log N ) essentially saturates this particular framework. The Ω(N 2 )
lower bound for an elementary symmetric polynomial in [CKSV22] uses different methods.
    The determinant illustrates why choosing very short matchings is specific to the permanent.
The Schur-complement calculation in §11 shows that a matching Y of k entries has tdY (det X) ≤
k 2 +1. For k = Θ(log n), this gives only O(log2 n) independent coeﬀicients, rather than the Ω(n2 )
supplied by Lem. 9.1 for the permanent. Relations among the relevant principal minors are
studied explicitly by Lin–Sturmfels [LinS09]. The same section proves that even arbitrary entry-
disjoint blocks cannot make this coeﬀicient-summing method yield a supercubic determinant
formula bound.
    Finally, allowing division requires care about the computational model. Strassen’s division-
elimination theorem often replaces a circuit with division by a division-free circuit computing
the same polynomial, but the cost depends on its degree [Str73b]. This transformation does
not preserve the sharp formula-size or variable-occurrence estimates needed here. Kalorkoti
instead analyzes rational formulas directly [Kal85], an approach followed by Lem. 10.2. Along
a formula path containing only one marked child at each gate, the marked value is transformed
by a fractional linear map u 7→ (au + b)/(cu + d). Such maps require only a bounded number of


                                                149
parameters from the field of unmarked variables; at branching gates, the parameters contributed
by the two marked children are added. A field-intersection argument then shows that when the
final output is a polynomial, its coeﬀicients belong to the resulting parameter field. Formula
validity requires denominators to be nonzero as rational functions; it does not require those
denominators to remain nonzero at the later Jacobian specialization, which is applied only to
the polynomial coeﬀicients.

12.5. Lower bounds in restricted arithmetic models. Many stronger-looking lower bounds
impose structural restrictions on the computation rather than on the target polynomial. In a
monotone computation over a semiring, subtraction and cancellation are unavailable. Jerrum–
Snir obtain exponential lower bounds for monotone computations of the permanent [JS82];
these arguments do not apply here because our circuits and formulas allow arbitrary complex
constants and cancellation.
   At every multiplication gate of a syntactically multilinear computation, the two input sub-
computations use disjoint sets of variables. Consequently every intermediate polynomial is
multilinear, a stronger requirement than multilinearity of the final output alone. For this re-
stricted formula model, Raz proves nΩ(log n) lower bounds for both the determinant and perma-
nent [Raz09]. Raz–Yehudayoff prove exponential lower bounds for constant-depth multilinear
circuits [RY09]. Although the determinant and permanent are themselves multilinear, a gen-
eral circuit or formula computing one of them may pass through nonmultilinear intermediate
polynomials; the restricted bounds therefore do not transfer to the unrestricted models of this
paper.
   Another important restriction is circuit depth. A depth-three ΣΠΣ circuit expresses a poly-
nomial as a sum of products of aﬀine linear forms. Over characteristic zero, Shpilka–Wigderson
use partial derivatives on low-codimension aﬀine subspaces to obtain nearly quadratic depth-
three determinant bounds in the number N = n2 of matrix variables [SW01]. Over fixed finite
fields, Grigoriev–Karpinski obtain exponential depth-three lower bounds for the determinant;
Grigoriev–Razborov and the exposition in [KS14, §7] give corresponding results and variants
for the permanent [GK98, GR00]. Those arguments exploit finite-field evaluation and are not
characteristic-zero general-circuit arguments. In characteristic two, the determinant and per-
manent again coincide.
   The distinction between homogeneous and nonhomogeneous circuits is also essential. In a ho-
mogeneous circuit, intermediate gates respect the degree grading; a nonhomogeneous circuit may
create terms of different degrees and cancel them later. For homogeneous depth-three circuits,
exponential lower bounds hold for both the determinant and permanent [NW97]. √        Neverthe-
less, over Q the determinant has nonhomogeneous depth-three circuits of size exp(O( n log n))
[GKKS16]. Thus a homogeneous lower bound does not automatically extend to a general circuit
of the same depth.
   Several complexity measures yield additional restricted-model bounds. Nisan–Wigderson use
the dimension of a space of partial derivatives [NW97]; Jacobian and algebraic-independence
methods apply to bounded-occurrence and related models [ASSS16]; and shifted partial deriva-
tives yield bounds in homogeneous, low-depth,
                                          √        or bounded-bottom-fan-in settings [GKKS14].
In particular, such methods
                     √        give exp(Ω(   n)) lower bounds for homogeneous depth-four circuits
of bottom fan-in O( n) computing either the n × n determinant or the n × n permanent.
   The fact that many of these measures treat the two polynomials alike is itself supported by
barrier results. Efremenko–Landsberg–Schenck–Weyman show that shifted partial derivatives
cannot separate the padded permanent from the determinant in the relevant orbit-closure regime
[ELSW18b]; Gesmundo–Landsberg identify related limitations for unpadded derivative spaces
[GL19]. In a different geometric complexity theory setting, Bürgisser–Ikenmeyer–Panova prove
a barrier for representation-theoretic “occurrence obstructions” [BIP19]. These results help
explain why a large derivative-based measure often proves a lower bound for both matrix poly-
nomials in a restricted model, rather than a permanent-versus-determinant separation. With
a different symmetry restriction, Dawar–Wilsenach do obtain an exponential permanent lower
bound while retaining polynomial-size determinant circuits [DW25]. This is a genuine separa-
tion inside that restricted symmetric model, not a lower bound for unrestricted circuits.


                                              150
   Depth-reduction theorems explain why shallow circuits nevertheless attract sustained at-
tention. Agrawal–Vinay reduce general arithmetic circuits to depth four [AV08], and Gupta–
Kamath–Kayal–Saptharishi obtain a “chasm at depth three” over characteristic zero [GKKS16].
These simulations increase circuit size superpolynomially at the relevant degrees, so an arbi-
trary lower bound for the resulting shallow model does not immediately yield a comparable
unrestricted-circuit lower bound.
   Recent constant-depth lower bounds extend beyond the early homogeneous and quadratic
depth-three results. Limaye–Srinivasan–Tavenas prove superpolynomial lower bounds for gen-
eral, possibly nonhomogeneous constant-depth circuits computing iterated matrix multiplication
over characteristic zero or suﬀiciently large characteristic [LST25]; Forbes extends the conclu-
sion to every field [For24]. Iterated matrix multiplication is a polynomial-size projection of
both the determinant and permanent: its source–sink path polynomial can be represented by a
cycle-cover matrix with self-loops, with the determinant differing only by a uniform sign. Since
substituting variables and constants preserves constant depth, a small constant-depth circuit
for either matrix polynomial would produce one for the projected iterated matrix multiplication
polynomial. Thus these results also give superpolynomial constant-depth lower bounds for both
matrix families.                                                                          √
   More precisely, over characteristic zero, the depth-three consequence is at least nΩ( log n)
for each n × n matrix polynomial [LST25]. Over every field, one obtains in particular the
depth-three bound
                                                           !!
                                               (log n)3/2
                                      exp Ω √
                                                 log log n
[For24]. Bhargav–Dutta–Saxena improve the constant-depth parameters and identify a bar-
rier for the associated measure [BDS24]. None of these results conflicts with polynomial-size
unrestricted-depth determinant circuits, and none distinguishes the permanent from the deter-
minant in the constant-depth model under discussion.

                                              References
[AH14]   S. Aaronson and T. Hance, Generalizing and derandomizing Gurvits’s approximation algorithm for
         the permanent, Quantum Inf. Comput. 14 (2014), nos. 7–8, 541–559, doi:10.26421/QIC14.7-8-1.
[ASSS16] M. Agrawal, C. Saha, R. Saptharishi, and N. Saxena, Jacobian hits circuits: Hitting sets, lower
         bounds for depth-D occur-k formulas and depth-3 transcendence degree-k circuits, SIAM J. Comput.
         45 (2016), no. 4, 1533–1562, doi:10.1137/130910725.
[AV08]   M. Agrawal and V. Vinay, Arithmetic circuits: A chasm at depth four, in 49th Annual IEEE Sym-
         posium on Foundations of Computer Science, IEEE, 2008, 67–75, doi:10.1109/FOCS.2008.32.
[ABV17]  J. Alper, T. Bogart, and M. Velasco, A lower bound for the determinantal complexity of a hypersur-
         face, Found. Comput. Math. 17 (2017), no. 3, 829–836, doi:10.1007/s10208-015-9300-x.
[BS83]   W. Baur and V. Strassen, The complexity of partial derivatives, Theoret. Comput. Sci. 22 (1983),
         no. 3, 317–330, doi:10.1016/0304-3975(83)90110-X.
[BMS11]  M. Beecken, J. Mittmann, and N. Saxena, Algebraic independence and blackbox identity testing, in
         Automata, Languages and Programming, Part II, L. Aceto, M. Henzinger, and J. Sgall, eds., Lecture
         Notes in Comput. Sci. 6756, Springer, 2011, 137–148, doi:10.1007/978-3-642-22012-8_10.
[Ber84]  S. J. Berkowitz, On computing the determinant in small parallel time using a small number of
         processors, Inform. Process. Lett. 18 (1984), no. 3, 147–150, doi:10.1016/0020-0190(84)90018-8.
[BDS24]  C. S. Bhargav, S. Dutta, and N. Saxena, Improved lower bound, and proof barrier, for constant depth
         algebraic circuits, ACM Trans. Comput. Theory 16 (2024), no. 4, Art. 23, 1–22, doi:10.1145/3689957.
[BI25]   M. Bläser and C. Ikenmeyer, Introduction to geometric complexity theory, Theory Comput. Libr.,
         Grad. Surv. 10 (2025), 1–166, doi:10.4086/toc.gs.2025.010.
[BCMV25] A. Boralevi, E. Carlini, M. Michałek, and E. Ventura, On the codimension of permanental varieties,
         Adv. Math. 461 (2025), Art. 110079, doi:10.1016/j.aim.2024.110079.
[Bür24]  P. Bürgisser, Completeness classes in algebraic complexity theory, 2024, arXiv:2406.06217.
[BCS97]  P. Bürgisser, M. Clausen, and M. A. Shokrollahi, Algebraic Complexity Theory, Grundlehren Math.
         Wiss. 315, Springer, Berlin, 1997, doi:10.1007/978-3-662-03338-8.
[BIP19]  P. Bürgisser, C. Ikenmeyer, and G. Panova, No occurrence obstructions in geometric complexity
         theory, J. Amer. Math. Soc. 32 (2019), no. 1, 163–193, doi:10.1090/jams/908.
[BLMW11] P. Bürgisser, J. M. Landsberg, L. Manivel, and J. Weyman, An overview of mathematical issues
         arising in the geometric complexity theory approach to VP 6= VNP, SIAM J. Comput. 40 (2011),
         no. 4, 1179–1209, doi:10.1137/090765328.


                                                    151
[BP15]    P. Butera and M. Pernici, Sums of permanental minors using Grassmann algebra, Int. J. Graph
          Theory Appl. 1 (2015), no. 2, 83–96, arXiv:1406.5337.
[Cai90]   J.-Y. Cai, A note on the determinant and permanent problem, Inform. Comput. 84 (1990), no. 1,
          119–127, doi:10.1016/0890-5401(90)90036-H.
[CCL10]   J.-Y. Cai, X. Chen, and D. Li, Quadratic lower bound for permanent vs. determinant in any charac-
          teristic, Comput. Complexity 19 (2010), no. 1, 37–56, doi:10.1007/s00037-009-0284-2.
[CKSV22] P. Chatterjee, M. Kumar, A. She, and B. L. Volk, Quadratic lower bounds for algebraic branching
          programs and formulas, Comput. Complexity 31 (2022), no. 2, Art. 8, doi:10.1007/s00037-022-00223-
          8.
[CKW11] X. Chen, N. Kayal, and A. Wigderson, Partial derivatives in arithmetic complexity and beyond,
          Found. Trends Theor. Comput. Sci. 6 (2011), nos. 1–2, 1–138, doi:10.1561/0400000043.
[DW25]    A. Dawar and G. Wilsenach, Symmetric arithmetic circuits, Theory Comput. 21 (2025), no. 14,
          1–32, doi:10.4086/toc.2025.v021a014.
[ELSW18a] K. Efremenko, J. M. Landsberg, H. Schenck, and J. Weyman, On minimal free resolutions
          of sub-permanents and other ideals arising in complexity theory, J. Algebra 503 (2018), 8–20,
          doi:10.1016/j.jalgebra.2018.01.021.
[ELSW18b] K. Efremenko, J. M. Landsberg, H. Schenck, and J. Weyman, The method of shifted partial deriva-
          tives cannot separate the permanent from the determinant, Math. Comp. 87 (2018), 2037–2045,
          doi:10.1090/mcom/3284.
[Eis95]   D. Eisenbud, Commutative Algebra with a View Toward Algebraic Geometry, Grad. Texts in Math.
          150, Springer, New York, 1995, doi:10.1007/978-1-4612-5350-1.
[FM11]    P. Feinsilver and J. McSorley, Zeons, permanents, the Johnson scheme, and generalized derangements,
          Int. J. Combin. 2011 (2011), Art. 539030, doi:10.1155/2011/539030.
[For24]   M. A. Forbes, Low-depth algebraic circuit lower bounds over any field, in 39th Computational
          Complexity Conference, Leibniz Int. Proc. Inform. 300, Schloss Dagstuhl, 2024, 31:1–31:16,
          doi:10.4230/LIPIcs.CCC.2024.31.
[FL06]    S. Friedland and D. Levy, A polynomial-time approximation algorithm for the number of k-matchings
          in bipartite graphs, in Mathematical Papers in Honour of Eduardo Marques de Sá, Textos Mat. Sér. B
          39, Univ. Coimbra, Coimbra, 2006, 61–67, arXiv:cs/0607135.
[GGIL22] F. Gesmundo, P. Ghosal, C. Ikenmeyer, and V. Lysikov, Degree-restricted strength decompositions
          and algebraic branching programs, in 42nd IARCS Annual Conference on Foundations of Software
          Technology and Theoretical Computer Science, Leibniz Int. Proc. Inform. 250, Schloss Dagstuhl,
          2022, 20:1–20:15, doi:10.4230/LIPIcs.FSTTCS.2022.20.
[GL19]    F. Gesmundo and J. M. Landsberg, Explicit polynomial sequences with maximal spaces of par-
          tial derivatives and a question of K. Mulmuley, Theory Comput. 15 (2019), no. 3, 1–24,
          doi:10.4086/toc.2019.v015a003.
[Gly10]   D. G. Glynn, The permanent of a square matrix, European J. Combin. 31 (2010), no. 7, 1887–1891,
          doi:10.1016/j.ejc.2010.01.010.
[Gre12]   B. Grenet, An upper bound for the permanent versus determinant problem, manuscript, 2012, author’s
          manuscript.
[GK98]    D. Grigoriev and M. Karpinski, An exponential lower bound for depth 3 arithmetic circuits, in
          Proceedings of the Thirtieth Annual ACM Symposium on Theory of Computing, ACM, 1998, 577–
          582, doi:10.1145/276698.276872.
[GR00]    D. Grigoriev and A. A. Razborov, Exponential lower bounds for depth 3 arithmetic circuits in algebras
          of functions over finite fields, Appl. Algebra Engrg. Comm. Comput. 10 (2000), no. 6, 465–487,
          doi:10.1007/s002009900021.
[GKKS14] A. Gupta, P. Kamath, N. Kayal, and R. Saptharishi, Approaching the chasm at depth four, J. ACM
          61 (2014), no. 6, Art. 33, 1–16, doi:10.1145/2629541.
[GKKS16] A. Gupta, P. Kamath, N. Kayal, and R. Saptharishi, Arithmetic circuits: A chasm at depth 3, SIAM
          J. Comput. 45 (2016), no. 3, 1064–1079, doi:10.1137/140957123.
[Har77]   R. Hartshorne, Algebraic Geometry, Grad. Texts in Math. 52, Springer, New York, 1977,
          doi:10.1007/978-1-4757-3849-0.
[Hei83]   J. Heintz, Definability and fast quantifier elimination in algebraically closed fields, Theoret. Comput.
          Sci. 24 (1983), no. 3, 239–277, doi:10.1016/0304-3975(83)90002-6; corrigendum, 39 (1985), no. 2–3,
          343, doi:10.1016/0304-3975(85)90150-1.
[HJ25]    P. Hrubeš and P. S. Joglekar, On read-k projections of the determinant, in 42nd International
          Symposium on Theoretical Aspects of Computer Science, Leibniz Int. Proc. Inform. 327, Schloss
          Dagstuhl, 2025, 53:1–53:7, doi:10.4230/LIPIcs.STACS.2025.53.
[Hya79]   L. Hyafil, On the parallel evaluation of multivariate polynomials, SIAM J. Comput. 8 (1979), no. 2,
          120–123, doi:10.1137/0208010.
[JS82]    M. Jerrum and M. Snir, Some exact complexity results for straight-line computations over semirings,
          J. ACM 29 (1982), no. 3, 874–897, doi:10.1145/322326.322341.
[Kal85]   K. A. Kalorkoti, A lower bound for the formula size of rational functions, SIAM J. Comput. 14
          (1985), no. 3, 678–687, doi:10.1137/0214050.



                                                      152
[KS14]     N. Kayal and R. Saptharishi, A selection of lower bounds for arithmetic circuits, in Perspectives in
           Computational Complexity, M. Agrawal and V. Arvind, eds., Progr. Comput. Sci. Appl. Logic 26,
           Birkhäuser, Cham, 2014, 77–115, doi:10.1007/978-3-319-05446-9_5.
[LMR13]    J. M. Landsberg, L. Manivel, and N. Ressayre, Hypersurfaces with degenerate duals and the geometric
           complexity theory program, Comment. Math. Helv. 88 (2013), no. 2, 469–484, doi:10.4171/CMH/292.
[LS00]     R. Laubenbacher and I. Swanson, Permanental ideals, J. Symbolic Comput. 30 (2000), no. 2, 195–
           205, doi:10.1006/jsco.2000.0363.
[LST25]    N. Limaye, S. Srinivasan, and S. Tavenas, Superpolynomial lower bounds against low-depth algebraic
           circuits, J. ACM 72 (2025), no. 4, Art. 26, 1–35, doi:10.1145/3734215.
[LinS09]   S. Lin and B. Sturmfels, Polynomial relations among principal minors of a 4 × 4-matrix, J. Algebra
           322 (2009), no. 11, 4121–4131, doi:10.1016/j.jalgebra.2009.06.026.
[MP08]     G. Malod and N. Portier, Characterizing Valiant’s algebraic complexity classes, J. Complexity 24
           (2008), no. 1, 16–38, doi:10.1016/j.jco.2006.09.006.
[MR04]     T. Mignon and N. Ressayre, A quadratic bound for the determinant and permanent problem, Int.
           Math. Res. Not. 2004 (2004), no. 79, 4241–4253, doi:10.1155/S1073792804142566.
[Min79]    H. Minc, Evaluation of permanents, Proc. Edinburgh Math. Soc. (2) 22 (1979), no. 1, 27–32,
           doi:10.1017/S0013091500027760.
[MS01]     K. D. Mulmuley and M. Sohoni, Geometric complexity theory I: An approach to the P vs. NP and
           related problems, SIAM J. Comput. 31 (2001), no. 2, 496–526, doi:10.1137/S009753970038715X.
[Nec66]    É. I. Nechiporuk, On a Boolean function, Dokl. Akad. Nauk SSSR 169 (1966), no. 4, 765–766;
           English transl., Soviet Math. Dokl. 7 (1966), 999–1000, Math-Net.Ru:dan32449.
[NW97]     N. Nisan and A. Wigderson, Lower bounds on arithmetic circuits via partial derivatives, Comput.
           Complexity 6 (1996/97), no. 3, 217–234, doi:10.1007/BF01294256.
[RS26]     C. Ramya and P. Shastri, Lower bounds for planar arithmetic circuits, ACM Trans. Comput. The-
           ory 18 (2026), no. 1, Art. 9, 1–23, doi:10.1145/3778858; conference version, 15th Innovations in
           Theoretical Computer Science Conference, Leibniz Int. Proc. Inform. 287, Schloss Dagstuhl, 2024,
           91:1–91:22, doi:10.4230/LIPIcs.ITCS.2024.91.
[Raz09]    R. Raz, Multi-linear formulas for permanent and determinant are of super-polynomial size, J. ACM
           56 (2009), no. 2, Art. 8, 1–17, doi:10.1145/1502793.1502797.
[RY09]     R. Raz and A. Yehudayoff, Lower bounds and separations for constant depth multilinear circuits,
           Comput. Complexity 18 (2009), no. 2, 171–207, doi:10.1007/s00037-009-0270-8.
[Rot64]    G.-C. Rota, On the foundations of combinatorial theory I: Theory of Möbius functions, Z. Wahrschein-
           lichkeitstheorie Verw. Gebiete 2 (1964), 340–368, doi:10.1007/BF00531932.
[Rys63]    H. J. Ryser, Combinatorial Mathematics, Carus Math. Monogr. 14, Mathematical Association of
           America, 1963.
[SW01]     A. Shpilka and A. Wigderson, Depth-3 arithmetic circuits over fields of characteristic zero, Comput.
           Complexity 10 (2001), no. 1, 1–27, doi:10.1007/PL00001609.
[SY10]     A. Shpilka and A. Yehudayoff, Arithmetic circuits: A survey of recent results and open questions,
           Found. Trends Theor. Comput. Sci. 5 (2010), no. 3–4, 207–388, doi:10.1561/0400000039.
[Str73a]   V. Strassen, Die Berechnungskomplexität von elementarsymmetrischen Funktionen und von Interpo-
           lationskoeﬀizienten, Numer. Math. 20 (1973), 238–251, doi:10.1007/BF01436566.
[Str73b]   V. Strassen, Vermeidung von Divisionen, J. Reine Angew. Math. 264 (1973), 184–202, Eu-
           DML:151394.
[Val79a]   L. G. Valiant, Completeness classes in algebra, in Proceedings of the Eleventh Annual ACM Sympo-
           sium on Theory of Computing, ACM, 1979, 249–261, doi:10.1145/800135.804419.
[Val79b]   L. G. Valiant, The complexity of computing the permanent, Theoret. Comput. Sci. 8 (1979), no. 2,
           189–201, doi:10.1016/0304-3975(79)90044-6.
[VSBR83]   L. G. Valiant, S. Skyum, S. Berkowitz, and C. Rackoff, Fast parallel computation of polynomials
           using few processors, SIAM J. Comput. 12 (1983), no. 4, 641–644, doi:10.1137/0212043.
[vzG87]    J. von zur Gathen, Permanent and determinant, Linear Algebra Appl. 96 (1987), 87–100,
           doi:10.1016/0024-3795(87)90337-5.




                                                    153
