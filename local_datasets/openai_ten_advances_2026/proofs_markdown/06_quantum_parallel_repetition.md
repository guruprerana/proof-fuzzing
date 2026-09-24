# Exponential Parallel Repetition for All Two-Player Entangled Games

> Source: OpenAI, *Ten Advances in Mathematics and Theoretical Computer Science*, Chapter 6, PDF pages 158–186. Layout-preserving text extraction; consult the source PDF for authoritative equation rendering.

                                     Chapter 6

         Exponential Parallel Repetition
      for All Two-Player Entangled Games
    Abstract. In a two-player entangled game G, a referee sends a question to each
    of two noncommunicating players, receives their answers, and decides whether
    they win. The players may share an arbitrary entangled quantum state, and the
    supremum of their winning probabilities is the entangled value ω ∗ (G). In the
    repeated game G⊗n , the referee plays n independent copies and accepts only if
    the players win every copy.
         Raz’s celebrated classical parallel repetition theorem (STOC 1995) shows
    that, for classical players, the repeated value decreases exponentially whenever
    the original value is less than one. Whether the same holds for arbitrary en-
    tangled games has been a longstanding open problem. We resolve this quan-
    tum analogue aﬃrmatively: for every ﬁnite two-player, one-round game G with
    ω ∗ (G) = 1 − ε < 1 and answer alphabets A, B,
                                                         !
                   ∗   ⊗n                      ε13
                 ω (G       ) ≤ exp −cqs                 n ,   n ≥ 1,
                                         ε + log(|A||B|)

    for a universal constant cqs > 0.
        Previously, Yuen (ICALP 2016) proved polynomial decay for arbitrary entan-
    gled games, and Bavarian, Vidick, and Yuen (STOC 2017) proved exponential
    decay for anchored games obtained by modifying the original game. Our proof
    builds on Yuen’s conditioning and dependency-breaking framework. Its main
    new ingredient is a postselection-stable quantum sampleability estimate that
    avoids an inverse dependence on the probability of the conditioning event.

                                        Contents
1. Introduction
2. Preliminaries
3. Proof of the parallel repetition theorem
4. Proof of the postselected sampleability lemma
A. Deferred auxiliary proofs
References




                                           154
1     Introduction
Parallel repetition is a basic method for reducing the error of multiprover interactive proofs.
Starting from a game that dishonest players cannot always win, the veriﬁer plays many inde-
pendent copies and accepts only if every copy is won. The fundamental question is whether
requiring simultaneous success makes the players’ winning probability exponentially small.
    In more detail, a ﬁnite two-player, one-round game is speciﬁed by G = (X, Y, A, B, µ, V ).
A referee samples a pair of questions (x, y) ∼ µ, sends x to Alice and y to Bob, and receives
answers a ∈ A and b ∈ B. The players win if V (x, y, a, b) = 1. They may agree on a strategy and
share randomness before the game, but they cannot communicate after receiving their questions.
The maximum winning probability of such a strategy is the classical value ω(G).
    In the parallel repetition G⊗n , the referee independently samples n question pairs and ac-
cepts precisely when the players win all n coordinates. The coordinates are independent in
the referee’s experiment, but Alice’s answer to a coordinate can depend on all her questions,
and similarly for Bob. Consequently, the winning probability of an arbitrary repeated-game
strategy need not factor across coordinates. Nevertheless, Raz’s parallel repetition theorem
shows that every ﬁnite classical game with ω(G) < 1 satisﬁes ω(G⊗n ) ≤ exp(−cG n) for some
cG > 0 depending on the game [Raz98]. Holenstein later gave an information-theoretic proof
and improved the quantitative dependence on the soundness gap [Hol09].
    In the quantum setting, an entangled game has exactly the same questions, answers, and ac-
ceptance rule, but the players are additionally allowed to share a bipartite quantum state before
receiving their questions. Alice measures her part of this state according to x, Bob measures
his part according to y, and their classical outcomes determine their answers. Their optimal
winning probability, taken over arbitrary ﬁnite-dimensional shared states and local measure-
ments, is the entangled value ω ∗ (G). In G⊗n , each player may perform one joint measurement
depending on their entire question tuple. Playing the coordinates independently shows only
that
                                       ω ∗ (G⊗n ) ≥ ω ∗ (G)n ;
the diﬃculty is to prove a matching exponential upper bound for unrestricted entangled strate-
gies.
    The general quantum analogue of Raz’s theorem was explicitly noted as open by
2004 [CHTW04, footnote 2]. In its basic qualitative form, the question is:

      (Quantum Parallel Repetition Conjecture) For every ﬁnite two-player entangled
      game G with ω ∗ (G) < 1, is there a constant cG > 0 such that

                         ω ∗ (G⊗n ) ≤ exp(−cG · n)    for every n ≥ 1 ?

Exponential repetition was subsequently proved for several important classes of games, but
the question for arbitrary games remained open. The strongest general theorem, due to Yuen,
established polynomial rather than exponential decay [Yue16].

1.1   Our result
We give an aﬃrmative answer to the quantum parallel repetition question for every ﬁnite two-
player, one-round entangled game.

Theorem 1.1. There exists a universal constant cqs > 0 such that the following holds. Let G =
(X, Y, A, B, µ, V ) be any ﬁnite two-player, one-round entangled game with nonempty answer
alphabets, and put
                             ε = 1 − ω ∗ (G) > 0,   ℓ = log(|A||B|).



                                              155
Then, for every integer n ≥ 1,
                                                                   !
                        ∗    ⊗n                      ε13
                     ω (G         ) ≤ exp −cqs                 n         (n ≥ 1).
                                               ε + log(|A||B|)

   The exponent 13 is not claimed to be optimal. It arises from the quantitative loss in a
standard quantum correlated-sampling lemma [DSV15, Lemma 17]. The central point is that
the decay is exponential for every ﬁnite entangled game.

1.2   Previous work
Classical parallel repetition. Raz proved exponential parallel repetition for all ﬁnite clas-
sical two-player, one-round games [Raz98]. Holenstein subsequently introduced an information-
theoretic approach based on correlated sampling and obtained the bound [Hol09, Theorem 2.5]
                                                          !!
                      ⊗n                     ε3 n
                  ω(G       ) ≤ exp −Ω                         ,       ε = 1 − ω(G).
                                       1 + log(|A||B|)
The dependence on the soundness gap can be improved for certain structured games [Rao11],
while Raz’s counterexample shows that the strongest possible linear-gap bound does not hold
for all games [Raz11].

Entangled games with additional structure. Perfect parallel repetition holds for quan-
tum XOR games [CSUU08], and exponential repetition has been established for entangled
unique games [KRT10], projection games [DSV15], and free games, where the players’ questions
are independently distributed [JPY14, CS15]. Other bounds apply to games with strictly pos-
itive Cartesian question support but can depend on the minimum question probability [CS14].
These results do not resolve the question for arbitrary predicates and correlated question distri-
butions.

General games. For unrestricted entangled games, Yuen proved [Yue16, Theorem 1] that if
ω ∗ (G) = 1 − ε, then, for n ≥ 2,
                                                   c sG log n
                                      ω ∗ (G⊗n ) ≤ 17 1/4 ,
                                                    ε n
where c is universal and sG is the bit-length of the answer alphabet. This theorem already
applies to arbitrary question distributions and unchanged games; the remaining gap is that its
decay is polynomial rather than exponential.
     Bavarian, Vidick, and Yuen obtained exponential ampliﬁcation by transforming the original
game into an anchored game [BVY17]. Earlier work of Kempe and Vidick also obtained general-
game ampliﬁcation by introducing additional consistency or dummy questions [KV11]. These
results are useful for hardness ampliﬁcation, but a repetition theorem for a modiﬁed game does
not imply one for the original game.
     Our proof follows the general conditioning and sampleability framework of Yuen [Yue16,
Section 3.2], which itself builds on Holenstein’s classical correlated sampling [Hol09, Lemma 5.2
and Corollary 5.3] and the quantum correlated-sampling lemma of Dinur, Steurer, and
Vidick [DSV15, Lemma 17]. The new ingredient is a quantum sampleability estimate that
remains eﬀective even when the conditioning event has exponentially small probability.


2     Preliminaries
We ﬁrst ﬁx probability and operator notation, then formally deﬁne ﬁnite one-round entangled
games and their standard parallel repetition. Standard ﬁnite-dimensional quantum background
appears in [Wat18, Chapters 2 and 3] and [NC10].


                                                  156
2.1   Notation and probability conventions
All logarithms are natural. For n ≥ 1, write [n] = {1, . . . , n}. If S ⊆ [n] and xn is a tuple, write
xS = (xj )j∈S , and similarly for yS , aS , bS . Empty products equal one.
    Named probability distributions are written in calligraphic font. In particular, P denotes an
original experiment, Q its conditioned distribution, and JA , JB locally generated distributions.
The referee’s question distribution retains the conventional symbol µ; Roman Exa , Fyb denote
measurement operators, not probability distributions.
    For probability distributions D, E on a ﬁnite set, relative entropy and total variation are
                                                    X                   D(u)
                                    D(DkE) =               D(u) log          ,
                                                       u                E(u)
                                               1X
                                  dTV (D, E) =     |D(u) − E(u)|.
                                               2 u

The conventions 0 log 0 = 0 and D(DkE) = +∞ when supp D 6⊆ supp E are understood. With
natural logarithms, Pinsker’s inequality reads
                                                           q
                                         dTV (D, E) ≤           1
                                                                2 D(DkE).

Probabilities and expectations under a speciﬁed distribution are written P and E. Conditioning
is used only when the conditioned event has strictly positive probability.
    For a ﬁnite-dimensional Hilbert space H, |ψi denotes a vector, F † the adjoint of an operator,
and F  0 positive semideﬁniteness. A positive contraction satisﬁes 0  F  I. A positive-
operator-valued measure (POVM) is a ﬁnite family of positive semideﬁnite operators summing
to the identity.

2.2   Finite one-round two-player entangled games
The referee samples one possibly correlated question pair and sends one question to each player.
Entanglement can correlate the answers, but the players cannot communicate after receiving
their questions.

Deﬁnition 2.1 (Finite one-round two-player entangled game). A game is a tuple

                   G = (X, Y, A, B, µ, V ),              V : X × Y × A × B −→ {0, 1},

where the question and answer sets are ﬁnite, both answer alphabets A, B are nonempty, and µ
is an arbitrary probability distribution on X × Y . A ﬁnite-dimensional tensor-product strategy
consists of ﬁnite local Hilbert spaces HA , HB , a unit vector ψ ∈ HA ⊗ HB , and local POVMs
                                  X                                              X
                   Exa  0,              Exa = IHA ,            Fyb  0,               Fyb = IHB .
                                 a∈A                                             b∈B

Its winning probability is
                                         X               X
                   ω ∗ (G; ψ, E, F ) =         µ(x, y)         V (x, y, a, b) hψ| Exa ⊗ Fyb |ψi .
                                         x,y             a,b

The entangled value is the supremum

                                ω ∗ (G) =          sup          ω ∗ (G; ψ, E, F ).
                                               HA ,HB ﬁnite
                                                  ψ,E,F

No uniform bound on the local dimensions and no attaining strategy are assumed.


                                                         157
   Deﬁne the question marginals
                                            X                                      X
                             µX (x) =            µ(x, y),          µY (y) =             µ(x, y).
                                            y                                       x

A question with zero marginal probability can be deleted without changing either game value.
On the resulting positive-marginal question sets, write
                                                 µ(x, y)                             µ(x, y)
                              µ(x | y) =                 ,         µ(y | x) =                .
                                                 µY (y)                              µX (x)
These expressions are evaluated only where their denominators are positive. The actual question-
pair support is
                             Eµ = {(x, y) ∈ X × Y : µ(x, y) > 0};
it need not equal X × Y and need not be connected.
    The tensor product expresses locality, not independence of the players’ answers. In particu-
lar, writing ρAB = |ψi hψ|, the actual Born probabilities are
                                                                                       
                                     P(a, b | x, y) = Tr ρAB (Exa ⊗ Fyb ) .

The state is prepared before either question is received.

2.3   Standard parallel repetition
Deﬁnition 2.2 (Standard parallel repetition). For n ≥ 1, the repeated game G⊗n samples

                                                   (xn , y n ) ∼ µ⊗n ,

sends xn to Alice and y n to Bob, permits arbitrary ﬁnite-dimensional joint local POVMs
                                        n                                 n
                                   {Exan : an ∈ An },              {Fybn : bn ∈ B n },

and accepts according to
                                                                   Y
                                                                   n
                                  V ⊗n (xn , y n , an , bn ) =           V (xi , yi , ai , bi ).
                                                                   i=1

Write vn = ω ∗ (G⊗n ). Thus a strategy wins the repeated game exactly when it wins every
original coordinate.
   For S ⊆ [n], write
                            Y                                      Y                                    Y
          µS (xS , yS ) =         µ(xj , yj ),     µSX (xS ) =           µX (xj ),        µSY (yS ) =         µY (yj ).
                            j∈S                                    j∈S                                  j∈S

These products express independence between distinct game coordinates, not independence
between the two questions of one coordinate.
   Although the sampled question pairs are independent between coordinates, Alice’s ith an-
swer may depend on all of xn , and Bob’s ith answer may depend on all of y n . In particular,

                                                 ω ∗ (G⊗n ) ≥ ω ∗ (G)n

is a lower bound obtained from independent strategies, not Ean
                                                             D upper bound on unrestricted
                                                  (n)
joint strategies. For a repeated strategy, write ρAB = ψ (n) ψ (n) for its preshared density
operator.
    The resulting precise game deﬁnitions are those used in Theorem 1.1, which was stated in
the introduction.


                                                             158
3     Proof of the parallel repetition theorem
We prove Theorem 1.1 by contradiction. Suppose that a strategy for G⊗n wins all n coordi-
nates simultaneously with probability exceeding the claimed exponential bound. Lemma 3.1
selects a small core D such that, conditional on winning every coordinate in D, a uniformly
chosen remaining coordinate wins with high probability. Lemma 3.2 represents this conditioned
coordinate by an ideal shared state and local measurements.
    This ideal experiment is not yet a legal single-game strategy: the conditioned question
distribution may diﬀer from µ, its history is not supplied to the players, and its state depends
jointly on their separate questions. The central Lemma 3.3 produces locally generated histories
and locally describable states that approximate the ideal experiment. Lemmas 3.4 and 3.5
then use classical and quantum correlated sampling to synchronize those histories and prepare
the state, and Lemma 3.6 converts them into an actual strategy for G. Finally, Section 3.5
chooses the parameters so that this strategy wins with probability greater than ω ∗ (G), giving
the contradiction.
    This section mainly follows the conditioning-and-rounding template of Yuen [Yue16, Sec-
tion 3.2]. The new ingredient is Lemma 3.3, whose proof is deferred to Section 4.

3.1    The contradiction and the conditioning lemma
Fix an actual ﬁnite-dimensional strategy for G⊗n . Its shared state is |ψi, its local measurements
        n                 n
are {Exan }an ∈An and {Fybn }bn ∈B n . Write (X n , Y n , An , B n ) for the random question-and-answer
word generated by this strategy; its distribution is

                        P(xn , y n , an , bn ) = µ⊗n (xn , y n ) hψ| Exan ⊗ Fybn |ψi .
                                                                       n      n




Write Wi for the event that coordinate i is won and set
                                            \
                                  WD =           Wj ,         ϑ = P(W[n] ).
                                           j∈D

The letter ϑ always denotes the all-coordinate success probability; the letter r below denotes a
classical history.
Lemma 3.1 (Quantitative greedy conditioning). Suppose ϑ > 0, let 0 < δ < 1, and assume
                                              log(1/ϑ)
                                                       < n.
                                                  δ
There exists D ⊊ [n] such that
                                      log(1/ϑ)
                                |D| ≤           ,
                                          δ
                                P(WD ) ≥ ϑ,
                                   1      X
                                                P(Wi | WD ) ≥ 1 − δ.
                                n − |D| i∈[n]\D

   The proof appears in Appendix A.2. Recall the conditioning parameters from the proof
overview: p is the probability of winning every coordinate in D, q is the average conditional
winning probability on a remaining coordinate, and η is the information cost per remaining
coordinate. For the set D supplied by Lemma 3.1, these are

                  m = n − |D|,               p = P(WD ),
                      1    X                     log(1/p) + |D| log(|A||B|)                        (1)
                  q=            P(Wi | WD ), η =                            .
                      m i∈[n]\D                              m


                                                        159
We will explicitly choose the parameters in Section 3.5, where the bounds on |D| and p from
Lemma 3.1 will give 0 ≤ η ≤ 1; see (17). We will also deﬁne a universal rounding constant
Bqs ≥ 1 in (11). With these choices, the operational goal is the following implication:

                            0≤η≤1           =⇒    ω ∗ (G) ≥ q − Bqs η 1/12 .

Lemma 3.6 proves this implication by constructing a genuine single-game strategy. Its left-hand
side is computed in the conditioned repeated-game experiment; its right-hand side concerns an
actual single-game strategy receiving fresh questions from µ. Thus it suﬃces to make q close to
one and η small; the probability p itself need not approach one.

3.2    The ideal conditioned single-game strategy
Fix D ⊊ [n] with p = P(WD ) > 0. To extract one instance of G, we keep one coordinate i ∈         /D
live: its questions Xi , Yi are withheld from the history and will serve as the referee’s single-game
questions. The history reveals both core questions XD , YD , so the core winning event WD can
be checked once the core answers are recorded. At every other coordinate it reveals at least one
of the two questions. This breaks the correlation between the remaining unrevealed Alice and
Bob question strings, while randomized reveal orders later make the live question a uniformly
chosen martingale increment. Section 4 constructs those orders and their distribution explicitly.
    To help construct their single-game strategy, Alice and Bob use ﬁnite-valued public random-
ness λ ∈ Λ, independent of the game questions, to sample a uniformly random live coordinate
i ∈ [n] \ D and revealed-coordinate sets CX , CY ⊆ [n] for their respective questions. These sets
satisfy
                               D ⊆ CX ∩ CY ,       CX ∪ CY = [n] \ {i}.                            (2)
The ﬁrst condition records both questions on D; the second withholds both live questions Xi , Yi
and reveals at least one question at every other coordinate. In particular, this second condition
is what makes the question factorization below possible.

The conditioned history. Let Z denote the random pair of answer words produced on D,
taking values in AD × B D . Deﬁne the revealed-question history and full history by

                     T = (λ, XCX , YCY ),        Z ∈ AD × B D ,       R = (T, Z).

Because T contains λ, conditioning on T = t automatically ﬁxes both reveal sets CX , CY .
Continue to denote the augmented distribution on Λ × X n × Y n × An × B n by P, and write

                                            Q = P( · | WD ).

The history R is an analytical variable, not information supplied to either player. Since R con-
tains λ, a realized history r determines its live coordinate i; we nevertheless display i explicitly
to identify the extracted coordinate. Deﬁne the posterior tuple distribution by

                          Q(i, r, x, y) = P(R = r, Xi = x, Yi = y | WD ).

Here (i, r, x, y) denotes realized values, while R, Xi , Yi denote random variables; the four tuple
entries need not be independent.

Why the unrevealed questions factor. We now see why the coverage property in (2)
matters. Once (T, Xi , Yi ) is ﬁxed, the still-random Alice questions occur only on [n] \ (CX ∪ {i}),
while the still-random Bob questions occur only on [n] \ (CY ∪ {i}). Their intersection is empty
precisely because CX ∪CY = [n]\{i}. Therefore no unrevealed pair (Xj , Yj ) ∼ µ remains jointly


                                                  160
sampled. Independence of the original question pairs across coordinates then gives the prior
factorization
                  P(X n = xn , Y n = y n | T = t, Xi = x, Yi = y)
                                                                                                  (3)
                       = P(X n = xn | T = t, Xi = x) P(Y n = y n | T = t, Yi = y).

This factorization holds under the prior P, not under the conditioned distribution Q.

Local eﬀects and the ideal conditioned state. Fix a realized history r = (t, z), where t
is a realized value of T and z = (aD , bD ) ∈ AD × B D is a realized value of Z. The marginal
repeated-game POVM eﬀects for these recorded answers are
                                                      X             n
                                          ExanD =              Exãn ,
                                                    ãn ∈An
                                                    ãD =aD
                                                     X             n
                                          FybnD =              Fyb̃n .
                                                    b̃n ∈B n
                                                    b̃D =bD

Thus ExanD is the eﬀect of Alice producing the particular answer word aD on D, regardless of
her answers elsewhere; FybnD has the analogous meaning for Bob. Average these eﬀects over each
player’s unrevealed questions to obtain the eﬀective local eﬀects
                                             aD
                                   Hr,x = E[EX n | T = t, Xi = x] ,
                                            h                               i
                                   Kr,y = E FYbDn | T = t, Yi = y .

Thus Hr,x and Kr,y are the local eﬀective eﬀects for the ﬁxed answer words aD , bD . The question
factorization (3) gives the exact probability of observing those answer words:

                            pr (x, y) := P(Z = z | T = t, Xi = x, Yi = y)
                                                                                                  (4)
                                     = hψ| Hr,x ⊗ Kr,y |ψi .

A POVM eﬀect speciﬁes an outcome probability but does not uniquely determine the operator
representing its conditional state-update branch. To specify the branch, choose one common
cross operator, or puriﬁcation,

                               Γ(F ) : H −→ H ⊗ A,                  0  F  I,

satisfying
                                           Γ(F )† Γ(F ) = F.                                      (5)
Equation (5) says that the cross operator preserves the exact Born probability of its eﬀect.
Deﬁnition 4.2 constructs a common ﬁnite-dimensional resolvent puriﬁcation, and Lemma 4.3
supplies its operator-entropy estimate.
   The resulting conditioned branch and its normalized state are
                                                                                     ϕr,x,y
                      ϕr,x,y = (Γ(Hr,x ) ⊗ Γ(Kr,y )) |ψi ,               Ψr,x,y =             .
                                                                                    kϕr,x,y k

By (5) and (4),
                                         kϕr,x,y k2 = pr (x, y).
Therefore Ψr,x,y is well deﬁned on every branch of positive Q-probability. This state is only
ideal: its deﬁnition uses the full history r and both live questions (x, y), whereas Alice and Bob
separately know only their own questions. Lemma 3.3 will replace it by nearby states described
using separate local information.


                                                    161
   There are two separate questions about the ideal branch. First, if Alice and Bob were
handed Ψr,x,y , could they reproduce the original strategy’s answers at coordinate i? Second,
can they approximately obtain this state from their own questions? The next lemma answers
only the ﬁrst question. The substantially harder Lemma 3.3 answers the second.

Lemma 3.2 (The ideal state exactly simulates the remaining coordinate). Fix (i, r, x, y) such
that Q(i, r, x, y) > 0. If Alice and Bob share the ideal state Ψr,x,y , there are local POVMs
{Mfa }a∈A and {N   e b }b∈B , determined by (r, x) and (r, y), respectively, such that
    r,x             r,y

                     fa ⊗ N
           hΨr,x,y | M     e b |Ψr,x,y i = Q(Ai = a, Bi = b | R = r, Xi = x, Yi = y).
                       r,x  r,y

   The proof and the corresponding answer-reﬁnement operators appear in Appendix A.1.

Why the ideal state wins with probability q. By Lemma 3.2, measuring Ψr,x,y produces
exactly the original strategy’s answers at coordinate i, conditioned on the history and live
questions. Its winning probability on this branch is therefore

                                 Q(Wi | R = r, Xi = x, Yi = y).

Average over (i, R, Xi , Yi ) ∼ Q. Since i is uniform in [n] \ D and independent of the original
experiment, the law of total expectation gives
                                                            1 X
           E(i,r,x,y)∼Q [Q(Wi | R = r, Xi = x, Yi = y)] =             P(Wj | WD ) = q.
                                                            m j∈[n]\D

This is an ideal analytical success probability: it does not assume that the players can sample
Q, obtain the history, or prepare the question-dependent state.

Sampling histories from separate questions. The ideal experiment is not yet a legal
single-game strategy: under Q, its questions may be biased by conditioning, its history is not
given to either player, and Ψr,x,y depends jointly on both questions. Instead, consider the
following actual experiment.
    The referee draws (x, y) ∼ µ, and the players use shared randomness to choose a uniform
i ∈ [n] \ D. Alice sees x but not y, so she samples a history from the conditional distribution of
R given her own question:
                                      rA ∼ Q(R | i, Xi = x).
Similarly, Bob sees y but not x, and samples

                                      rB ∼ Q(R | i, Yi = y).

These histories need not agree automatically. They will be coupled by classical correlated
sampling using the players’ shared randomness.
    Let JA denote the distribution generated when Alice samples a history using her own ques-
tion, and let JB denote the analogous distribution generated by Bob. Their respective tuple
distributions are
                                            1
                           JA (i, r, x, y) = µ(x, y)Q(r | i, Xi = x),
                                            m                                             (6)
                                            1
                           JB (i, r, x, y) = µ(x, y)Q(r | i, Yi = y).
                                            m
Both retain the original question distribution µ.




                                               162
Locally describable candidate states. Even when rA = rB = r, the target Ψr,x,y still
depends on both questions. To obtain states that Alice and Bob can describe separately, average
the corresponding eﬀects over the other player’s unknown question:
                               X                                        X
                     H̄r,y =        µ(x0 | y)Hr,x0 ,          K̄r,x =            µ(y 0 | x)Kr,y0 .
                               x0                                           y0

Here H̄r,y is Bob’s estimate of Alice’s eﬀect, using his question y, while K̄r,x is Alice’s estimate
of Bob’s eﬀect, using her question x. Collect the exact branch and its two locally describable
alternatives:
                                ϕr,x,y = (Γ(Hr,x ) ⊗ Γ(Kr,y )) |ψi ,
                                      r,x = (Γ(Hr,x ) ⊗ Γ(K̄r,x )) |ψi ,
                                     ϕA                                                              (7)
                                      r,y = (Γ(H̄r,y ) ⊗ Γ(Kr,y )) |ψi .
                                     ϕB
Let
                                             ϕA
                                              r,x                           ϕB
                                                                             r,y
                                    ΨA
                                     r,x =          ,         ΨB
                                                               r,y =                .
                                             ϕA
                                              r,x                           ϕB
                                                                             r,y

Alice can specify the entire bipartite state ΨA                                         B
                                              r,x from (r, x), while Bob can specify Ψr,y from
(r, y).
     The attempt to mimic the ideal experiment therefore requires two guarantees: the locally
generated histories must agree and remain close in distribution to Q, and both locally described
states must approximate Ψr,x,y . The next lemma provides exactly these guarantees.

3.3   The central state-alignment and history-sampleability lemma
The following lemma contains the new technical estimates. Its ﬁrst conclusion says that the
ideal conditioned state admits two nearby descriptions, one available to each player. Its second
says that both players can approximately sample the same conditioned history despite receiving
fresh questions from µ. The complete proof is deferred to Section 4.
    Recall that (i, r, x, y) ∼ Q denotes a tuple drawn from the conditioned distribution; although
r already determines i, the coordinate is displayed explicitly.
Lemma 3.3 (Postselected state alignment and history sampleability). For every ﬁnite repeated-
game strategy and every D ⊊ [n] with p = P(WD ) > 0, use the parameters, history, states, and
locally generated distributions deﬁned above. Then
                                                                        2
                                    E(i,r,x,y)∼Q Ψr,x,y − ΨA
                                                           r,x              ≤ 8η,
                                                                        2
                                                                                                     (8)
                                    E(i,r,x,y)∼Q Ψr,x,y − ΨB
                                                           r,y              ≤ 8η,

Moreover, with                                          r
                                                    3
                                                 κ=   η,
                                                    2
one has dTV (Q, JA ), dTV (Q, JB ) ≤ κ. There exists ﬁnite shared randomness such that, on
(x, y) ∼ µ, Alice and Bob sample a common uniform i ∈ [n] \ D and histories rA , rB with
respective tuple distributions JA , JB , satisfying

                                             P(rA 6= rB ) ≤ 4κ.                                      (9)

    The state inequalities are averages under the posterior distribution: for example, the ﬁrst
states that when the repeated experiment is conditioned on WD , the ideal state is typically
close to the state described by Alice. They are not pointwise claims about every history. The
total-variation bounds compare the ideal posterior with histories that Alice or Bob can actually
generate using their own question. Finite classical correlated sampling then gives (9).


                                                        163
3.4    Constructing the actual single-game strategy
On fresh referee questions (x, y) ∼ µ, the desired strategy has three operational steps. First,
Alice and Bob use shared randomness to produce approximately matching histories rA , rB .
Second, they use their local descriptions ΨA             B
                                              rA ,x and ΨrB ,y to approximately prepare the ideal
state Ψr,x,y . Finally, they apply the local coordinate measurements from Lemma 3.2. We ﬁrst
state the two standard sampling tools and then give the full strategy and its error analysis.
    Classical sampling is the familiar Holenstein construction [Hol09, Lemma 5.2 and Corol-
lary 5.3]; a direct proof using ﬁnite shared randomness appears in Appendix A.7. The quantum
input is the state-preparation theorem of Dinur, Steurer, and Vidick [DSV15, Lemma 17], which
applies to arbitrary bipartite states.

Lemma 3.4 (Exact ﬁnite classical correlated sampling). Let F be a ﬁnite family of probability
distributions on a ﬁnite set R. There exists one ﬁnite shared random variable and, for each
D ∈ F, an output RD having exactly distribution D, such that

                           P(RD 6= RE ) ≤ 2 dTV (D, E)                       (D, E ∈ F ).                     (10)

    Apply the lemma to the ﬁnite family

                            {Q(R | i, Xi = x),                  Q(R | i, Yi = y)}i,x,y .

After sharing a uniform i, Alice uses her actual question x and Bob his actual question y.
Averaging (10) against µ(x, y) gives

                       P(rA 6= rB ) ≤ 2 dTV (JA , JB )
                                                                                        
                                         ≤ 2 dTV (JA , Q) + dTV (Q, JB ) ≤ 4κ,

which proves the ﬁnite-shared-randomness guarantee in Lemma 3.3.

Lemma 3.5 (Quantum correlated sampling). There exists a universal Kqs ≥ 1 with the follow-
ing property. Given d ≥ 1 and 0 < α ≤ 1, there exist a ﬁnite d0 ≥ 1 and assignments of local
unitaries
                             σA 7−→ U (σA ),    σB 7−→ V (σB )
       0
on Cdd , indexed by unit vectors in Cd ⊗ Cd , such that, simultaneously for every pair σA , σB of
such unit vectors,
                                                                                
              U (σA ) ⊗ V (σB ) |Edd0 i − |σA i |Ed0 i ≤ Kqs max α1/12 , kσA − σB k1/6 .

Here the ﬁnite embezzlement state is
                                                           −1/2
                                                  X
                                                  b
                                                    1               X
                                                                    b
                                                                      1
                                    |Eb i =                             √ |ji |ji .
                                                  j=1
                                                        j           j=1
                                                                           j

The initial state |Edd0 i and catalyst dimension d0 depend on d, α, not on σA , σB .

   This is precisely the quantum correlated-sampling lemma of Dinur, Steurer, and
Vidick [DSV15, Lemma 17].

Rounding into a legal single-game strategy.                          Set the following universal constants:
                                                                            r
                               1/6                                              3                  √
             U∗ = Kqs (1 + 2         ) + 2,        Bqs = (5 + 2U∗ )               + 2Kqs 321/12 + 2 8.        (11)
                                                                                2



                                                             164
Lemma 3.6 (Postselection-stable ﬁnite-dimensional rounding). In the setting of Lemma 3.3,
suppose 0 ≤ η ≤ 1. For every 0 < α ≤ 1, there is an actual ﬁnite-dimensional tensor-product
strategy Sα for the unchanged game G. On questions (x, y) ∼ µ, the strategy ﬁrst uses classical
correlated sampling to generate approximately matching histories, then uses quantum correlated
sampling to prepare the state associated with that history, and ﬁnally applies the coordinate
measurements of Lemma 3.2. Its winning probability satisﬁes

                              win(Sα ) ≥ q − Bqs η 1/12 − 2Kqs α1/12 .                                 (12)

The questions of this strategy have distribution µ, and its shared state is prepared before either
question is received. In particular,

                                      ω ∗ (G) ≥ q − Bqs η 1/12 .                                       (13)

Proof. First, synchronize the history. Classical correlated sampling provides ﬁnite shared ran-
domness h, including a uniform coordinate i, from which Alice computes rA = rA (h, x) and Bob
computes rB = rB (h, y). By Lemma 3.3,
                                                                                            q
              dTV (Q, JA ), dTV (Q, JB ) ≤ κ,          P(rA 6= rB ) ≤ 4κ,              κ≤       3
                                                                                                2 η.   (14)

Next, prepare the ideal state. Pad all candidate states to a common ﬁnite dimension d, and
apply quantum correlated sampling once, obtaining d0 and local unitaries U, V . If ν(h) denotes
the distribution of the classical shared randomness, the question-independent shared state is
                                                                 !
                                      Xq
                              |Ωi =             ν(h) |hiA |hiB       ⊗ |Edd0 i .                       (15)
                                       h

For analysis, ﬁx a branch on which rA = rB = r. Alice knows (r, x), Bob knows (r, y), and they
apply U (ΨA              B
           r,x ) and V (Ψr,y ), respectively. Quantum correlated sampling requires these candidate
states to be close. Since both approximate the same ideal state,
                                           2                                       2
               E(i,r,x,y)∼Q ΨA
                             r,x − Ψr,y
                                    B
                                               ≤ 2E(i,r,x,y)∼Q ΨA
                                                                r,x − Ψr,x,y
                                                                                       2
                                                 + 2E(i,r,x,y)∼Q Ψr,x,y − ΨB
                                                                           r,y             ≤ 32η.

Quantum correlated sampling therefore approximately prepares ΨA        r,x , which is itself close to
Ψr,x,y . The resulting average state-preparation error is O(α 1/12 +η 1/12  ).
Finally, measure the extracted coordinate. Alice and Bob apply the measurements from
Lemma 3.2. On the ideal state their average winning probability is q; closeness of the prepared
state changes this probability by O(α1/12 + η 1/12 ). Mismatching histories and the change
                                                            √
from Q to the actual question distribution cost O(κ) = O( η). The precise calculation in
Appendix A.8 gives (12). Taking the supremum over the ﬁnite-dimensional strategies Sα and
letting α → 0+ yields (13).

3.5    The ﬁnal contradiction and exponential bound
We now prove Theorem 1.1, including its explicit distribution-uniform rate and the prefactor 1.
Set
                                              1
                                  cqs =              > 0.                                 (16)
                                         8(4Bqs )12
Proof of Theorem 1.1. First suppose the game satisﬁes ω ∗ (G) = 0. From any ﬁnite-dimensional
strategy for G⊗n , the players can construct a single-game strategy by choosing a coordinate and
presampling all other question pairs from µ using ﬁnite shared randomness. They insert their


                                                    165
actual referee questions in the chosen coordinate, run the original repeated local measurements,
and return that coordinate’s answers. Every all-coordinate win is a win of the resulting single-
game strategy. Hence
                               ω ∗ (G⊗n ) ≤ ω ∗ (G) = 0   (n ≥ 1),
and the assertion holds.
   Suppose, therefore, that 0 < ε < 1, and write

                                                              ε13          ε
                         ℓ = log(|A||B|),      γ = cqs            ,      δ= .
                                                             ε+ℓ           4
Fix an arbitrary n ≥ 1. If the desired conclusion fails at this n, then

                                        ω ∗ (G⊗n ) > e−γn .

The deﬁnition of the supremum therefore gives an actual ﬁnite-dimensional repeated strategy
with
                                  ϑ = P(W[n] ) > e−γn .
There is no assumption that the repeated value is attained. Since Bqs ≥ 1,
                                                         !12
                                     ε            ε                 ε  δ
                               γ=                               ≤     = .
                                  8(ε + ℓ)       4Bqs               8  2

Thus the hypothesis of Lemma 3.1 is satisﬁed, and it supplies D ⊊ [n] with
                             γn  n               n                                ε
                     |D| <      ≤ ,      m>        ,          p ≥ ϑ,         q ≥1− .
                              δ  2               2                                4
In particular,
                                                                    4γnℓ
                                log(1/p) < γn,           |D|ℓ <          .
                                                                      ε
Using m > n/2 and (16), we get

                                          log(1/p) + |D|ℓ
                                      η=
                                              m 
                                                   4ℓ
                                        < 2γ 1 +
                                                   ε
                                             ε 12    ε + 4ℓ
                                        =         12
                                          4(4Bqs ) ε + ℓ
                                                       !12
                                              ε
                                        ≤                    ≤ 1.                          (17)
                                             4Bqs

Choose the strictly positive ﬁnite-catalyst accuracy
                                                    !12
                                              ε
                                    α=                       ∈ (0, 1].
                                            16Kqs

Lemma 3.6 now produces an actual single-game ﬁnite-dimensional strategy with

                     win(Sα ) ≥ q − Bqs η 1/12 − 2Kqs α1/12
                                    ε ε ε              5ε
                              >1− − − =1−                  > 1 − ε = ω ∗ (G),
                                    4 4 8               8




                                                 166
contradicting the deﬁnition of ω ∗ (G). Therefore ω ∗ (G⊗n ) ≤ e−γn for this arbitrary n. As n ≥ 1
was arbitrary,
                                                                          !
                    ∗   ⊗n                 1            ε13
                  ω (G       ) ≤ exp −                            n               (n ≥ 1).
                                       8(4Bqs )12 ε + log(|A||B|)

Every question conditional above was used only on positive µ-support. Neither a minimum
positive question probability nor a connected-support or component-dependent reduction enters
the proof. Both the classical ﬂag and the catalyst in (15) are ﬁnite for each ﬁxed strategy and
each α > 0. The rate is consequently independent of the question distribution, its support, the
question-alphabet sizes, and the entanglement dimension.


4    Proof of the postselected sampleability lemma
This section proves Lemma 3.3.

Reminder of Lemma 3.3 (Postselected state alignment and history sampleability). For every
ﬁnite repeated-game strategy and every D ⊊ [n] with p = P(WD ) > 0, let the histories, branches,
and distributions be deﬁned by (1)–(7) and (6). Then
                                                                  2
                                  E(i,r,x,y)∼Q Ψr,x,y − ΨA
                                                         r,x          ≤ 8η,
                                                                  2
                                  E(i,r,x,y)∼Q Ψr,x,y − ΨB
                                                         r,y          ≤ 8η,
Furthermore, with                                   r
                                                          3
                                              κ=            η,
                                                          2
one has
                                dTV (Q, JA ) ≤ κ,         dTV (Q, JB ) ≤ κ.
There exists a ﬁnite shared random variable such that, on (x, y) ∼ µ, the players sample a
common uniform i ∈ [n]\D and locally generated histories rA , rB with respective tuple marginals
JA , JB and
                                     P(rA 6= rB ) ≤ 4κ.


Recall notations. Fix the repeated-game strategy and D ⊊ [n] with p = P(WD ) > 0.
Throughout this section write
                                                                                                  τ +s
     M = [n] \ D,        m = |M |,       τ = log(1/p),           s = |D| log(|A||B|),        η=        .
                                                                                                    m
Here WD is the event that every core coordinate in D is won, and Q = P( · | WD ) is its posterior.

Proof roadmap. We begin by understanding what the state diﬀerence in (8) actually mea-
sures. Public randomness λ picks a live coordinate i and speciﬁes which questions have already
been revealed. The resulting history is

                        r = (t, z),     t = (λ, XCX , YCY ),           z = (aD , bD ).

Thus r records the core questions XD , YD and answers aD , bD , but neither live question Xi , Yi .
Suppose now that Xi = x and Yi = y. The eﬀects Hr,x and Kr,y describe Alice’s and Bob’s




                                                    167
recorded core answers aD , bD , respectively. Alice knows x, but not y, so from her point of view
Bob’s eﬀect Kr,y must instead be averaged:

                                                K̄r,x = EYi ∼µ(·|x) Kr,Yi .

Write |ψi for the original shared state and Γ for a common puriﬁcation. The ideal branch
conditioned on both live questions (x, y) and the branch determined by Alice’s information
(r, x) are, respectively,
                                                                                                       
                ϕr,x,y = Γ(Hr,x ) ⊗ Γ(Kr,y ) |ψi ,                     r,x = Γ(Hr,x ) ⊗ Γ(K̄r,x ) |ψi .
                                                                      ϕA

The only diﬀerence is that the ﬁrst branch sees Bob’s actual question Yi = y, while the second
does not. The quantity ϕr,x,y − ϕA
                                 r,x is therefore precisely the change caused by revealing Yi . Its
normalized counterpart is the ﬁrst state diﬀerence in (8).
   A single reveal can have a large eﬀect, so there is no reason for revealing Yi in isolation
to have a small cost. Instead, imagine keeping Alice’s relevant questions ﬁxed and gradually
uncovering Bob’s remaining questions, one at a time, in a random order πX . Somewhere along
the way we encounter the live coordinate i. Because the order is random, the number kX of
questions revealed before i is uniform. Let U be everything ﬁxed before this process begins.
After the ﬁrst j questions have been uncovered, our current prediction for Bob’s core-answer
eﬀect FYbDn is                                             
                                               Gj = E FYbDn U, Yπ≤j .
                                                                             X

As more questions are exposed, these predictions form a Doob martingale under the prior P.
Immediately before the live step kX , the question Yi is still unknown; immediately afterwards,
it has been revealed. We therefore have
                                                                                                                   
GkX = K̄r,Xi ,         GkX +1 = Kr,Yi ,            ϕr,Xi ,Yi − ϕA
                                                                r,Xi = Γ(Hr,Xi ) ⊗ Γ(GkX +1 ) − Γ(GkX ) |ψi .

This is the central reduction: the state diﬀerence we care about is exactly one randomly chosen
increment of a much longer reveal process. A particular increment might be large, but a
uniformly random one can be controlled by the total information budget.
    The martingale above tracks eﬀects. To control the resulting change in quantum states, we
must also choose the puriﬁcation Γ. One obvious choice would be Γ(F ) = F 1/2 , which already
preserves Born probabilities, that is, Γ(F )† Γ(F ) = F . Instead, we use the resolvent puriﬁcation
from Deﬁnition 4.2, which preserves the same Born probabilities. Its additional beneﬁt is the
entropy-control property in Lemma 4.3: with H1 (v) = −v log v and H1 (0) = 0,
                 h                    †                    i
           EF        Γ(F ) − Γ(F̄ )        Γ(F ) − Γ(F̄ )         H1 (F̄ ) − EF H1 (F ),             F̄ = EF F.

The meaning is that the expected squared diﬀerence between a random eﬀect F and its average
F̄ , after applying Γ, is bounded by the decrease in operator entropy when F̄ is reﬁned to F .
Apply this at every step of the reveal martingale (Gj )N  j=0 . The successive entropy decreases
telescope, so their total, weighted by Alice’s ﬁxed eﬀect H and the shared state, is at most the
entropy of the initial branch probability:

         X
         N −1
                                                                 2
                E Γ(H) ⊗ Γ(Gj+1 ) − Γ(Gj ) |ψi                        ≤ H1 (p0 ),         p0 = hψ| H ⊗ G0 |ψi .
          j=0

Lemma 4.4 therefore bounds a uniformly random step k by its 1/N share of the total:

                                                                                2       H1 (p0 )
                             E Γ(H) ⊗ Γ(Gk+1 ) − Γ(Gk ) |ψi                          ≤            .
                                                                                           N


                                                             168
For a ﬁxed core-answer word z, the initial branch probability is p0 = pz (U ) = P(Z = z | U ).
Lemma 4.5 shows that the total entropy of the accepted words is at most p(τ + s) on average.
Intuitively, acceptance has total probability p, and recording its core-answer word contributes
at most s additional units of entropy.
    Lemma 4.6 applies the random-step estimate to the two live-question reveals. Write P 0 for
the prior distribution of public randomness and questions. The Alice- and Bob-reveal costs are
                                                     X                          2
                            IA = E(i,t,x,y)∼P 0                 ϕr,x,y − ϕB
                                                                          r,y       ,
                                                  z: WD (t,z)
                                                     X                          2
                            IB = E(i,t,x,y)∼P 0                 ϕr,x,y − ϕA
                                                                          r,x       .
                                                  z: WD (t,z)

Here r = (t, z), and the sums range over accepted core-answer words. The vectors ϕr,x,y , ϕA      B
                                                                                           r,x , ϕr,y
are unnormalized branches, so IA and IB measure their unnormalized squared diﬀerences. The
reverse description selects a block of N candidate live coordinates with size bias 2N/m, while
its uniform reveal step contributes 1/N . These factors cancel, so Lemma 4.6 bounds both costs
by
                                                2
                                      IA , IB ≤    p(τ + s).
                                                m
Lemma 4.7 then converts these unnormalized branch diﬀerences into the normalized-state dif-
ferences that we actually want to bound:
                                                             4  2
                            E(i,r,x,y)∼Q Ψr,x,y − ΨA
                                                   r,x              ≤
                                                               IB ≤ 8η,
                                                             p
                                                          2  4
                             E(i,r,x,y)∼Q   Ψr,x,y − ΨB
                                                      r,y   ≤ IA ≤ 8η.
                                                             p
This proves both desired state bounds in (8) without any inverse-postselection loss. What re-
mains, the history-matching guarantee (9), is purely classical: Lemma 4.8 supplies the standard
conditioning budget, and Lemma 4.9 combines it with the relative-entropy chain rule, Pinsker’s
inequality, and classical correlated sampling.

4.1   Setting up the revealed history and its martingale
The forward history. Choose i uniformly in M and partition M \ {i} fairly into LX t
LY . Choose independent uniform random permutations πX,−i of LX and πY,−i of LY . The
subscript −i indicates that these permutations exclude the live coordinate i. Independently
choose uniform cuts
                         kX ∈ {0, . . . , |LX |}, kY ∈ {0, . . . , |LY |}.
This is a symmetric random-reveal variant of the dependency-breaking construction in Holen-
stein’s classical embedding argument [Hol09, Section 3]. The random permutations and cuts
kX , kY allow the live question to be identiﬁed later with a uniformly random increment of a
reveal martingale.
    The public randomness and revealed-coordinate sets are
                                λ = (i, LX , LY , πX,−i , πY,−i , kX , kY ),
                                             ≤kY
                              CX = D ∪ LX ∪ πY,−i ,
                                             ≤kX
                              CY = D ∪ LY ∪ πX,−i .

Thus Alice’s questions XLX and Xπ≤kY are revealed, as are Bob’s questions YLY and Yπ≤kX .
                                       Y,−i                                                     X,−i
This is precisely the public randomness λ introduced in Section 3.2; in particular,

                          T = (λ, XCX , YCY ),            CX ∪ CY = [n] \ {i}.


                                                    169
Write P 0 for the marginal retaining the independent public randomness and questions but
                                                 Q
discarding all answers: P 0 (λ, xn , y n ) = P(λ) nj=1 µ(xj , yj ). Its induced marginal on (i, T, Xi , Yi )
is denoted by P 0 (i, t, x, y). Both core-question tuples XD , YD are revealed, neither live question
Xi , Yi is revealed, and every other coordinate reveals at least one question. Therefore the
unrevealed Alice and Bob index sets are disjoint, and the product prior P gives exactly (3).
This is independence under P, not under the posterior Q.

The branches to be compared.                     For z = (aD , bD ) and r = (t, z), recall
                                                  aD
                                        Hr,x = E[EX n | T = t, Xi = x] ,
                                                     h                            i
                                        Kr,y = E FYbDn | T = t, Yi = y .

Prior conditional independence identiﬁes the joint branch probability pr (x, y) with the notation
already introduced in Section 3:

                                 pr (x, y) = hψ| Hr,x ⊗ Kr,y |ψi = kϕr,x,y k2 .

Averaging over the other player’s unknown live question gives
                                   X                                         X
                         H̄r,y =        µ(x0 | y)Hr,x0 ,         K̄r,x =          µ(y 0 | x)Kr,y0 .
                                   x0                                        y0

Consequently,                                                                
                                        ϕr,x,y = Γ(Hr,x ) ⊗ Γ(Kr,y ) |ψi ,
                                                                             
                                          r,x = Γ(Hr,x ) ⊗ Γ(K̄r,x ) |ψi ,
                                         ϕA
                                                                             
                                          r,y = Γ(H̄r,y ) ⊗ Γ(Kr,y ) |ψi .
                                         ϕB
If Q(i, t, z, x, y) > 0, then µ(x, y) > 0 and pr (x, y) > 0. Moreover,

                               H̄r,y  µ(x | y)Hr,x ,            K̄r,x  µ(y | x)Kr,y ,

so
                         2                                               2
                  ϕA
                   r,x       ≥ µ(y | x)pr (x, y) > 0,             ϕB
                                                                   r,y       ≥ µ(x | y)pr (x, y) > 0.

Thus all normalized states used on positive-posterior branches (i, t, z, x, y) exist. Since t records
the core questions XD , YD , the pair (t, z) determines whether WD occurs, that is, whether every
core coordinate in D is won. Summing the accepted branch probabilities therefore gives
                                   X
                                             P 0 (i, t, x, y) 1WD (t, z) pr (x, y) = p.
                                 i,t,x,y,z

This exact branch mass p is the factor that will cancel when the unnormalized costs are converted
into normalized-state distances.

The random live-coordinate martingale. Only three features of the reveal construction
enter the proof: the live question is a uniform martingale step, its block is sampled with the
appropriate size bias, and the neighboring eﬀects are exactly the local eﬀects we wish to compare.

Lemma 4.1 (Random live-coordinate martingales). The forward history admits the following
equivalent reverse descriptions.
    For the Alice-reveal direction, sample a partition M = LX t L+
                                                                 Y with


                                                           −m           Y|
                                                                     2|L+
                                              P(LX , L+
                                                      Y)=2                 .
                                                                       m


                                                           170
                       Y and an independent uniform cut kY ∈ {0, . . . , |LY | − 1} determine
A uniform order πY of L+                                                   +

i = πY [kY + 1]. With
                            U = (XD , YD , XLX , YL+ , Yπ≤kX ),                          (21)
                                                                        Y      X,−i

the eﬀects
                                                   
                            aD
                    Fj = E EX n | U, X ≤j
                                      π
                                                        ,                              0 ≤ j ≤ |L+
                                                                                                 Y |,
                                                Y
                             h          i
                    K = E FYbDn | U                                                                                 (22)

form a prior martingale with ﬁxed Bob eﬀect K, and

                         FkY = H̄r,Yi ,             FkY +1 = Hr,Xi ,              K = Kr,Yi .                       (23)
                                                                               −m 2|L+ |/m, take a
    For the Bob-reveal direction, sample M = L+      X t LY with probability 2       X
uniform order πX of L+X , and  let i = π X [k X + 1] for a uniform cut k X . With

                                 U = (XD , YD , XL+ , YLY , Xπ≤kY ),
                                                                X               Y,−i


the eﬀects                                                     
                             Gj = E FYbDn | U, Yπ≤j ,                       0 ≤ j ≤ |L+
                                                                                      X |,
                                                            X

form a prior martingale with ﬁxed Alice eﬀect Hr,Xi , and

                                 GkX = K̄r,Xi ,                     GkX +1 = Kr,Yi .

   The live increments are therefore exactly the Alice- and Bob-reveal branch diﬀerences. Ap-
pendix A.3 veriﬁes the reverse distribution and these martingale properties.

4.2   Resolvent puriﬁcation and one-step entropy control
We now make precise the puriﬁcation Γ used in the roadmap. The ordinary square-root choice
Γ(F ) = F 1/2 preserves Born probabilities; the resolvent puriﬁcation below does the same while
also yielding a useful one-step entropy estimate.

Deﬁnition 4.2 (Resolvent puriﬁcation). Let S be the collection of all possible values of
Hr,x , Kr,y , H̄r,y , K̄r,x and the martingale eﬀects Fj , Gj in Lemma 4.1. The question, answer,
and public-randomness alphabets are ﬁnite, so S is ﬁnite. Let Σ be the union of the positive
eigenvalues of the operators in S. Set
                  σ
      gσ (u) =       ,       A0 = span{gσ : σ ∈ Σ} ⊆ L2 ((0, ∞), du),                            A = A0 ⊕ C |0i .
                 σ+u
The auxiliary space A is ﬁnite dimensional, with dim A ≤ |Σ| + 1. For each eﬀect F , deﬁne

                     [Γ(F )v](u) = F (F + uI)−1 v,                      Γ(F ) : H −→ H ⊗ A.

Veriﬁcation of the Born-probability property.                               For every positive eigenvalue σ,
                                            Z ∞                2
                                                      σ
                                                                      du = σ,
                                            0        σ+u
so spectral calculus gives
                                                Γ(F )† Γ(F ) = F,                                                   (24)
including for singular F .


                                                            171
The entropy-control property. Revealing one question replaces an averaged eﬀect F̄ by a
more informative eﬀect F . The key beneﬁt of the resolvent puriﬁcation is that the resulting
squared movement is bounded by the corresponding decrease in operator entropy.

Lemma 4.3 (One-step puriﬁed variation is controlled by entropy). Let F be a ﬁnitely supported
random positive contraction taking values in S, and suppose that F̄ = EF F also belongs to S.
Recall
                       H1 (v) = −v log v (0 < v ≤ 1),     H1 (0) = 0,
and deﬁne H1 (F ) by functional calculus. Then
                       h                    †                    i
                  EF       Γ(F ) − Γ(F̄ )        Γ(F ) − Γ(F̄ )         H1 (F̄ ) − EF H1 (F ).   (25)

   For positive deﬁnite eﬀects, the entropy gap is the expected operator Bregman divergence in-
troduced by Petz [Pet07]; closely related resolvent-based estimates were studied by Kim [Kim14].
A direct proof, also covering singular eﬀects, appears in Appendix A.4.

4.3      A puriﬁed martingale has a small random increment
The one-step estimate becomes useful because its entropy terms telescope over an entire reveal
martingale. This is the quantum counterpart of the classical relative-entropy chain rule.

Lemma 4.4 (Puriﬁed martingale increments). Let F0 , . . . , FN be a ﬁnite positive-contraction
martingale, where N ≥ 1, F0 is deterministic, and

                                       E[Fj+1 | F0 , . . . , Fj ] = Fj .

Fix a positive contraction K on Bob’s space and a shared unit vector |ψi. Let k be uniform in
{0, . . . , N − 1}, independently of the martingale, and write

                                            p0 = hψ| F0 ⊗ K |ψi .

Recall
                            H1 (v) = −v log v        (0 < v ≤ 1),            H1 (0) = 0.
Then
                                                              H1 (p0 )      2
                           Ek,F   Γ(Fk+1 ) − Γ(Fk ) ⊗ Γ(K) |ψi          .        ≤      (26)
                                                                  N
The same conclusion holds conditionally when previously revealed information ﬁxes F0 and K.

Proof. Absorb Bob’s ﬁxed eﬀect into the positive operator
                                            h                                        i
                              ρK = TrB (I ⊗ K 1/2 ) |ψi hψ| (I ⊗ K 1/2 ) .

For every operator C on Alice’s space,

                  Tr(ρK C) = hψ| C ⊗ K |ψi ,                  Tr ρK = hψ| I ⊗ K |ψi ≤ 1.          (27)

In particular, p0 = Tr(ρK F0 ).
   Write
                        ∆j = Γ(Fj+1 ) − Γ(Fj ),                Fj = σ(F0 , . . . , Fj ).
Conditional on Fj , apply Lemma 4.3 with F = Fj+1 and F̄ = Fj . The martingale identity
E[Fj+1 | Fj ] = Fj gives

                             E[∆†j ∆j | Fj ]  H1 (Fj ) − E[H1 (Fj+1 ) | Fj ].


                                                        172
Moreover, (24) and (27) give

                                   k∆j ⊗ Γ(K) |ψik2 = Tr(ρK ∆†j ∆j ).

Taking expectations, tracing against ρK , and summing over j makes the intermediate entropies
cancel:
           X
           N −1
                                                                                    
                  E k∆j ⊗ Γ(K) |ψik2 ≤ Tr ρK H1 (F0 ) − EH1 (FN )                         ≤ Tr(ρK H1 (F0 )).   (28)
           j=0

For the last inequality use H1 (FN )  0.
                       P                                               P
   Diagonalize F0 = a σa |va i hva | and put wa = hva | ρK |va i. Since a wa = Tr ρK ≤ 1,
append an eigenvalue 0 with weight 1 − Tr ρK . Concavity of H1 then gives
                                                                                      !
                                           X                          X
                     Tr(ρK H1 (F0 )) =          wa H1 (σa ) ≤ H1              wa σa       = H1 (p0 ).
                                            a                             a

Finally, the uniform cut k selects one of the N increments independently, so its expected squared
movement is the sum in (28) divided by N . This proves (26).

4.4   From reveal costs to normalized state alignment
Our goal is the pair of normalized-state estimates in (8). On every positive-posterior branch,
the exact posterior weight is

                                                 P 0 (i, t, x, y) 1WD (t, z) kϕr,x,y k2
                           Q(i, t, z, x, y) =                                           .                      (29)
                                                                    p
For nonzero vectors u, v,
                                           u   v 2 4 ku − vk2
                                             −    ≤           .
                                          kuk kvk     kuk2
                                                2
Taking u = ϕr,x,y and v = ϕBr,y , the factor kuk in (29) cancels the denominator above. Thus
the desired normalized estimate reduces to the following unnormalized Alice-reveal cost:
                                           X                                                           2
                  IA = E(i,t,x,y)∼P 0                   Γ(Hr,x ) − Γ(H̄r,y ) ⊗ Γ(Kr,y ) |ψi
                                            z:
                                        1WD (t,z)=1
                                           X                          2
                     = E(i,t,x,y)∼P 0                 ϕr,x,y − ϕB
                                                                r,y       .
                                            z:
                                        1WD (t,z)=1

It is an Alice-reveal cost because the operator that changes is Alice’s eﬀect Hr,x ; it compares
the ideal branch ϕr,x,y with Bob’s surrogate ϕB r,y . It is unnormalized because neither branch
vector is divided by its norm and the expectation is under the prior P 0 . Deﬁne the symmetric
Bob-reveal cost by
                                                         X                                2
                             IB = E(i,t,x,y)∼P 0                    ϕr,x,y − ϕA
                                                                              r,x             .
                                                          z:
                                                      1WD (t,z)=1

The two target estimates are therefore bounded by
                                                                      4
                                                                      2
                                  E(i,r,x,y)∼Q Ψr,x,y − ΨB
                                                         r,y              ≤
                                                                        IA ,
                                                                      p
                                                                                                               (30)
                                                                   2  4
                                  E(i,r,x,y)∼Q       Ψr,x,y − ΨA
                                                               r,x   ≤ IB .
                                                                      p
It remains to show that each unnormalized cost is at most 2p(τ + s)/m.


                                                         173
Lemma 4.5 (Accepted-word entropy budget). For any background information U containing
XD , YD , let
                  pW (U ) = P(WD | U ),    pz (U ) = P(Z = z | U ).
The accepted answer words z satisfy
                             X
                                       H1 (pz (U )) ≤ H1 (pW (U )) + pW (U )s,                  (31)
                              z:
                         1WD (U,z)=1

and consequently                             X
                             EU ∼P 0                 H1 (pz (U )) ≤ p(τ + s).                   (32)
                                            z:
                                       1WD (U,z)=1

   The proof is deferred to Appendix A.5.

Lemma 4.6 (Probability-weighted quantum alignment). The two reveal costs satisfy

                                                       2p(τ + s)
                                          IA , IB ≤              .
                                                          m
Proof. Use the Alice-reveal martingale already constructed in (22). Conditional on its back-
ground U , the accepted answer word z has prior probability

                            pz (U ) = P(Z = z | U ) = hψ| F0 ⊗ K |ψi .

Its live cut kY is uniform in {0, . . . , |L+
                                            Y |−1}, so Lemma 4.4, applied with N = |LY | and k = kY ,
                                                                                      +

gives
                      h                                           i   H1 (pz (U ))
                                                             2
                    E Γ(FkY +1 ) − Γ(FkY ) ⊗ Γ(K) |ψi           U ≤                 .
                                                                          |L+
                                                                            Y|

By (23), the vector on the left is exactly ϕr,Xi ,Yi −ϕB
                                                       r,Yi . Fix a partition M = LX tLY , and write
                                                                                       +

EU for averaging over its remaining public randomness and background questions. Because U
contains XD , YD , accepted words are already determined before the random cut. Summing the
preceding bound over those words gives
                                         X       H1 (pz (U ))   p(τ + s)
                                 EU                           ≤          ,
                                      z: W (U,z)
                                                    |LY |
                                                      +
                                                                  |L+
                                                                    Y|
                                         D


where (32) applies for each ﬁxed partition because the public randomness is independent of the
game. Finally, average over the size-biased partitions:
                                      X                    2|L+Y|          p(τ + s)
                          IA ≤                       2−m
                                                  |        {z m }            |L+
                                                                               Y|
                                 LX tL+Y =M
                                            probability of the partition
                                   |L+
                                     Y |>0

                                 2p(τ + s)       X                   2p(τ + s)
                             =                             2−m ≤               .
                                    m                                   m
                                              LX tL+Y =M
                                                |L+
                                                  Y |>0


The last sum is at most one because 2−m is the probability of a fair partition and only the
nonempty L+ Y blocks occur.
   For IB , use the symmetric Bob-reveal martingale (Gj )j constructed above. Alice’s eﬀect
Hr,Xi remains ﬁxed while Bob’s questions Yπ≤j are revealed, and its partition has size bias
                                                      X

   X |/m. The same martingale estimate and size-bias cancellation give IB ≤ 2p(τ + s)/m.
2|L+


                                                     174
Passing to normalized states. We now convert the unnormalized reveal-cost bounds into
the normalized-state alignment required by Lemma 3.3.

Lemma 4.7 (Postselection-stable normalized alignment). The ideal conditioned state and its
locally describable alternatives satisfy
                                         2                                              2
            E(i,r,x,y)∼Q Ψr,x,y − ΨA
                                   r,x       ≤ 8η,         E(i,r,x,y)∼Q Ψr,x,y − ΨB
                                                                                  r,y       ≤ 8η.

Proof. On tuples of zero posterior probability, any undeﬁned normalized state may be completed
by a ﬁxed arbitrary unit vector; such defaults do not contribute to a posterior expectation.
Combining the reduction (30) with Lemma 4.6 gives both bounds:

                                   4     4     8(τ + s)
                                     IA , IB ≤          = 8η.
                                   p     p        m

Thus the p retained in the unnormalized entropy budget cancels the 1/p in the posterior, with
no inverse-postselection loss.

4.5    Classical history generation and correlated sampling
The remaining task is classical: Alice and Bob must generate nearly matching histories rA , rB
using their respective live questions Xi , Yi . We collect the conditioning budget and its sampling
consequence together to separate this standard argument from the quantum state alignment.

Lemma 4.8 (Conditioning and answer-history entropy). Conditioning on WD has exact
relative-entropy cost
                         D(P( · | WD )kP) = log(1/p) = τ.                    (33)
Recall s = |D| log(|A||B|). The answer-word alphabet Z = AD × B D has log |Z| = s; for every
revealed question tuple U and additional question block YC ,

                              D(QU,YC ,Z k PU,YC ⊗ Unif Z ) ≤ τ + s.                                (34)

Proof. The Radon–Nikodym derivative of Q with respect to P is 1WD /p, which gives (33). Data
processing bounds the relative-entropy cost of every question marginal by τ . Conditionally on
those questions, the divergence of Z from the uniform distribution on Z is at most log |Z| = s.
The chain rule gives (34).

Lemma 4.9 (Locally generated histories approximate the posterior). The locally generated
history distributions satisfy
                                         3τ + 2s
              D(QkJA ), D(QkJB ) ≤               ,          dTV (Q, JA ), dTV (Q, JB ) ≤ κ.
                                            m
Classical correlated sampling produces histories rA , rB with respective tuple distributions JA , JB
such that
                                        P(rA 6= rB ) ≤ 4κ.                                      (35)

    The proof uses only the preceding conditioning budget, the classical relative-entropy chain
rule, Pinsker’s inequality, and Lemma 3.4; it is deferred to Appendix A.6.

Conclusion. Lemma 4.7 proves the two state inequalities in Lemma 3.3, and Lemma 4.9 gives
its total-variation and matching-history conclusions. Together they complete the proof.




                                                     175
A     Deferred auxiliary proofs
A.1    Ideal-state extraction and local measurement reﬁnements
For r = (t, z), z = (aD , bD ), deﬁne the answer-reﬁnement operators
                                                               aD ,ai =a
                                a
                               Hr,x = EX n ∼P( ·|T =t,Xi =x) [EX n       ],
                                                                h        i
                                b
                               Kr,y = EY n ∼P( ·|T =t,Yi =y) FYbDn ,bi =b .

These are positive contractions satisfying
                              X                           X
                                     a                           b
                                    Hr,x = Hr,x ,               Kr,y = Kr,y .
                              a∈A                         b∈B

Lemma A.1 (Singular-safe local POVM reﬁnement). Let 0  F  I and let {F a : a ∈ A} be
                             P
positive operators satisfying a F a = F . There is a genuine POVM {MaF : a ∈ A} on the ﬁnite
puriﬁed space such that
                                Γ(F )† MaF Γ(F ) = F a (a ∈ A).                         (36)

Proof. Use the inverse square root F [−1/2] on supp(F ), extended by zero on ker F , and put

                                         UF = Γ(F )F [−1/2] .

By (5), UF is an isometry on supp(F ). Choose a default a0 ∈ A and set

                      MaF = UF F [−1/2] F a F [−1/2] UF† + 1{a=a0 } (I − UF UF† ).

Since 0  F a  F , each F a is supported on supp(F ). The displayed operators are positive and
sum to the identity on the entire ﬁnite puriﬁed space. Finally UF† Γ(F ) = F 1/2 , and Γ(F ) has
image in im UF . These identities prove (36), including when F has a nontrivial kernel.

Proof of Lemma 3.2. Apply Lemma A.1 to {Hr,xa }
                                                a∈A and {Kr,y }b∈B , obtaining local POVMs
                                                             b

 fa }a∈A and {N
{M             e b }b∈B . The reﬁnement identities and kϕr,x,y k2 = pr (x, y) give
   r,x           r,y


                                 fa ⊗ Ne b |Ψr,x,y i =
                                                                 a ⊗ K b |ψi
                                                            hψ| Hr,x      r,y
                       hΨr,x,y | M r,x  r,y                                   .
                                                                 pr (x, y)
Prior conditional independence identiﬁes the numerator with the probability of the recorded his-
tory answers together with (Ai , Bi ) = (a, b); the denominator is the probability of the recorded
history answers. Their ratio is therefore Q(Ai = a, Bi = b | R = r, Xi = x, Yi = y), as
claimed.

A.2    The conditioning lemma recalled and proved
Reminder of Lemma 3.1 (Quantitative greedy conditioning). Suppose ϑ > 0, let 0 < δ < 1,
and assume
                                 log(1/ϑ)
                                          < n.
                                     δ
There exists D ⊊ [n] such that

                                     log(1/ϑ)
                               |D| ≤           ,
                                         δ
                               P(WD ) ≥ ϑ,
                                  1      X
                                               P(Wi | WD ) ≥ 1 − δ.
                               n − |D| i∈[n]\D


                                                    176
Proof of Lemma 3.1. Start with D = ∅. If
                                            1    X
                                                     P(W i | WD ) > δ,
                                         n − |D| i∈D
                                                  /

choose an i ∈
            / D whose individual conditional failure is larger than δ, and replace D by D ∪ {i}.
Every conditional probability is well deﬁned, since
                                       W[n] ⊆ WD ,       P(WD ) ≥ ϑ > 0.
Each addition strictly decreases the mass by a factor smaller than 1 − δ:
                          P(WD∪{i} ) = P(WD )P(Wi | WD ) < (1 − δ)P(WD ).
Consequently, after k ≥ 1 additions,
                                                                   log(1/ϑ)      log(1/ϑ)
                     ϑ ≤ P(WD ) < (1 − δ)k ,            k<                     ≤          .
                                                                  − log(1 − δ)       δ
The assumed strict inequality prevents all n coordinates from being added. Therefore the
process stops at a proper set. The stopping condition is exactly the asserted average-success
inequality; containment of the all-win event gives the claimed mass. If the process makes no
additions, the same conclusions hold with D = ∅.

A.3    Random live-coordinate reveal martingales
Proof of Lemma 4.1. Consider ﬁrst the Alice-reveal direction and write N = |L+    Y |. In the
forward experiment, choose i uniformly in M , partition the other m − 1 coordinates fairly, and
choose the two orders and cuts uniformly. The probability of a particular outcome is
                                                    21−m
                                                                      .
                                        m |LX |!(|LX | + 1)(N − 1)! N
In the reverse experiment, ﬁrst choose M = LX t L+                        −m 2N/m. Then choose
                                                   Y with probability 2
a uniform order πY of LY , a uniform cut kY ∈ {0, . . . , N − 1}, and set
                        +


                                     i = πY [kY + 1],               Y \ {i}.
                                                              LY = L+
Deleting i from πY recovers πY,−i . Finally, choose πX,−i and kX as in the forward experiment.
The resulting outcome again has probability
                      2N             1 1 1           1                    21−m
                  2−m                                       =                               .
                  | {z m}            N ! N |LX |! |LX | + 1   m |LX |!(|LX | + 1)(N − 1)! N
             size-biased partition

The reverse construction therefore preserves the exact history distribution while making the live
cut kY uniform.
    Fix the partition, its orders, kX , and the background U from (21). Given U , the remaining
questions Xj , j ∈ L+
                    Y , are independent with distributions µ(· | Yj ). Therefore the tower property
gives
                                       E[Fj+1 | U, Xπ≤j ] = Fj ,
                                                              Y

so (Fj )N
        j=0 is a positive-contraction martingale.  Bob’s eﬀect K is ﬁxed because all questions
on which it depends have already been included in U . At the live cut, averaging over Xi
gives FkY = H̄r,Yi , revealing Xi gives FkY +1 = Hr,Xi , and the ﬁxed eﬀect is K = Kr,Yi . This
proves (23).
    Interchanging Alice and Bob gives the second construction. Its partition has probability
 −m
2 2|L+  X |/m; the uniform cut kX selects the live question from LX , while Alice’s eﬀect remains
                                                                  +

ﬁxed. The same conditional-independence and tower arguments give the martingale (Gj )j and
the two stated eﬀects at its live cut.


                                                        177
A.4    Resolvent puriﬁcation and its entropy estimate
For positive deﬁnite eﬀects, let f (v) = v log v and H1 (v) = −v log v. The associated operator
Bregman divergence is

                               Df (F, F̄ ) = f (F ) − f (F̄ ) − Df (F̄ )[F − F̄ ].

When F̄ = EF F , averaging cancels the derivative term and identiﬁes the expected divergence
with the entropy gap:
                             EF Df (F, F̄ ) = H1 (F̄ ) − EF H1 (F ).

Proof of Lemma 4.3. For u > 0, abbreviate

                    RF = (F + uI)−1 ,             RF̄ = (F̄ + uI)−1 ,        J = F − F̄ .

The pointwise diﬀerence between the two resolvent puriﬁcations is

                    Lu = F (F + uI)−1 − F̄ (F̄ + uI)−1 = uRF JRF̄ = uRF̄ JRF .

Since uRF2  RF ,
                                 L2u = u2 RF̄ JRF2 JRF̄  uRF̄ JRF JRF̄ .
The second-order resolvent identity gives

                                  RF − RF̄ + RF̄ JRF̄ = RF̄ JRF JRF̄ .

Taking expectations and using EF J = 0, we obtain
                                                                     
                                           EF L2u  u EF RF − RF̄ .

For every positive semideﬁnite C,
                        Z T
                              u(C + uI)−1 du = T I − C log(C + T I) + C log C.
                         0

Integrate the preceding operator inequality, cancel the T I terms, and let T → ∞. The remaining
large-T terms vanish because log(F + T I) = (log T )I + log(I + F/T ) and EF F = F̄ . Therefore
                  Z ∞
                        EF L2u du  EF [F log F ] − F̄ log F̄ = H1 (F̄ ) − EF H1 (F ).
                    0

The integral on the left is precisely the left side of (25).

A.5    Probability-weighted accepted-answer entropy
Proof of Lemma 4.5. Fix background information U containing XD , YD . The accepted answer
words have total probability pW (U ) and their number is at most

                                            |Z| = |A||D| |B||D| = es .

Applying the log-sum inequality to their probabilities pz (U ) gives
                                X
                                           H1 (pz (U )) ≤ H1 (pW (U )) + pW (U )s,
                                  z:
                             1WD (U,z)=1

which is (31). Since EU ∼P 0 pW (U ) = p and H1 is concave,

                                    EU ∼P 0 H1 (pW (U )) ≤ H1 (p) = pτ.

Averaging (31) therefore gives (32).


                                                       178
A.6     Classical sampleability of the revealed history
Proof of Lemma 4.9. Recall the two locally generated tuple distributions
                          1                                                           1
      JA (i, r, x, y) =     µ(x, y)Q(r | i, Xi = x),              JB (i, r, x, y) =     µ(x, y)Q(r | i, Yi = y).
                          m                                                           m
The live coordinate i remains uniform under Q, so the relative-entropy chain rule gives
                          D(QkJA ) = Ei∼Unif(M ) D(QXi |i kµX )
                                                                                                                 (40)
                                             + E(i,r,x,y)∼Q D QYi |i,Xi ,T,Z µ( · | Xi ) .

The product prior and (33) imply
                                     X
                                          D(QXi kµX ) ≤ D(QXM kµ⊗m
                                                                X ) ≤ τ,
                                    i∈M

so the ﬁrst term of (40) is at most τ /m.
    For the second term use the Bob-reveal reverse construction from Section 4. Fix a partition
M = L+ X t LY , its orders, the LY cut, and the background

                             U = (XD , YD , XL+ , YLY , Xπ≤kY ),                  |L+
                                                                                    X | > 0.
                                                    X                Y,−i


Equation (34) specializes to
                                                                           
                                   D QU,Y + ,Z PU,Y + ⊗ Unif Z                  ≤ τ + s.
                                              L             L
                                               X             X


Under the reference distribution, conditionally on U , the variables Yj , j ∈ L+
                                                                               X , are independent
with distributions µ(· | Xj ). Apply the chain rule in the order πX and discard its nonnegative
initial term:
                            |L+
                            X X|                                                 
                                   EQ D QYπ [j] |U,Z,Y <j         µ( · | XπX [j] ) ≤ τ + s.
                                               X        π
                            j=1                             X


The live cut is uniform over these |L+
                                     X | positions. Its conditioning data are precisely (i, T, Xi , Z),
while the reverse partition has weight 2|L+ X |/m. These factors cancel, giving
                                                                                 2(τ + s)
                            E(i,r,x,y)∼Q D QYi |i,Xi ,T,Z µ( · | Xi ) ≤                     .
                                                                                      m
Consequently,
                                                   3τ + 2s
                                               D(QkJA ) ≤  .
                                                      m
Interchanging Alice and Bob gives the same bound for JB . Pinsker’s inequality and η =
(τ + s)/m imply                                    r            r
                                                      3τ + 2s     3
                      dTV (Q, JA ), dTV (Q, JB ) ≤            ≤     η = κ.
                                                        2m        2
    Finally, apply Lemma 3.4 to the ﬁnite family

                                    {Q(R | i, Xi = x), Q(R | i, Yi = y)}i,x,y ,

including arbitrary ﬁxed defaults for zero posterior marginals. Use public randomness to choose
the uniform coordinate i and perform the correlated sampling. The resulting histories have exact
tuple distributions JA , JB , and
                                                                                                   
                P(rA 6= rB ) ≤ 2 dTV (JA , JB ) ≤ 2 dTV (JA , Q) + dTV (Q, JB ) ≤ 4κ.

This proves (35).


                                                            179
A.7    Proof of ﬁnite classical correlated sampling
Proof of Lemma 3.4. Temporarily generate shared independent proposals
                       (Zj , Uj )j≥1 ,   Zj ∼ Unif(R),                   Uj ∼ Unif[0, 1].
The procedure indexed by D outputs the ﬁrst Zj for which Uj ≤ D(Zj ). Each proposal is
accepted with probability 1/|R|, and the output has exactly distribution D. For D, E, inspect
the ﬁrst proposal accepted by either procedure. The probability that it is accepted by only one
of them is             P
                           |D(z) − E(z)|       2 dTV (D, E)
                     P z                  =                  ≤ 2 dTV (D, E).
                       z max{D(z),  E(z)}    1 + dTV (D, E)
When the ﬁrst proposal is accepted by both, their outputs agree; thus this also bounds their
eventual disagreement. Since F is ﬁnite, all procedures terminate simultaneously almost surely.
Their joint output vector belongs to the ﬁnite set RF . Use that vector itself as the ﬁnite
shared random variable, and let each player read the component indexed by the locally speciﬁed
distribution. This preserves the exact marginals and all the disagreement bounds without using
an inﬁnite randomness register.

A.8    Quantitative details for the single-game rounding
We ﬁnish the error calculation deferred from Lemma 3.6. On a matching valid branch (i, r, x, y),
Lemma 3.5 with
                                   σA = Ψ Ar,x , σB = ΨBr,y
bounds the distance from Alice’s candidate state. A further triangle inequality bounds the
distance from the ideal state by
                                                                                       
                                                                                  1/6
                                                         r,x − Ψr,y
                            e(i, r, x, y) = Kqs α1/12 + ΨA      B



                                                r,x − Ψr,x,y .
                                             + ΨA
Set e = U∗ outside the support of Q. Since unit vectors have distance at most 2, one has
0 ≤ e ≤ U∗ .
   The state alignment in Lemma 3.3 and Jensen’s inequality give
                                                                                            
                                              1/6                                           2 1/12
                 E(i,r,x,y)∼Q ΨA
                               r,x − Ψr,y
                                      B
                                                    ≤       E(i,r,x,y)∼Q ΨA
                                                                          r,x − Ψr,y
                                                                                 B


                                                    ≤ (32η)1/12 .
                                             √
                         r,x − Ψr,x,y ≤
Similarly, E(i,r,x,y)∼Q ΨA                       8η. Consequently,
                                                                                       p
                      E(i,r,x,y)∼Q e(i, r, x, y) ≤ Kqs α1/12 + (32η)1/12 +                  8η.
    Let w(i, r, x, y) be the ideal branch winning probability, and set w = 0 outside the support
of Q. Then 0 ≤ w ≤ 1, E(i,r,x,y)∼Q w(i, r, x, y) = q, and (14) implies
  E(i,r,x,y)∼JA w(i, r, x, y) ≥ q − κ,       E(i,r,x,y)∼JA e(i, r, x, y) ≤ E(i,r,x,y)∼Q e(i, r, x, y) + U∗ κ.
Histories disagree with probability at most 4κ. On a matching branch, replacing the ideal
state by one at distance e changes any measurement probability by at most 2e. Therefore the
strategy (15) satisﬁes
                                                                                  
                win(Sα ) ≥ q − 5κ − 2 E(i,r,x,y)∼Q e(i, r, x, y) + U∗ κ
                                                                                              p
                           ≥ q − (5 + 2U∗ )κ − 2Kqs α1/12 − 2Kqs (32η)1/12 − 2 8η.
Finally, 0 ≤ η ≤ 1 gives                 q
                                                               √
                                    κ≤       3 1/12
                                             2η     ,              η ≤ η 1/12 .
Using the constants in (11) proves (12) with exactly the stated universal constant Bqs .


                                                      180
References
[BVY17]    M. Bavarian, T. Vidick, and H. Yuen. Hardness ampliﬁcation for entangled games via
           anchoring. In Proceedings of the 49th ACM Symposium on Theory of Computing, pages
           303–316, 2017. doi:10.1145/3055399.3055433. Revised full version, Anchored parallel
           repetition for nonlocal games: https://arxiv.org/abs/1509.07466v2.
[CS14]     A. Chailloux and G. Scarpa. Parallel repetition of entangled games with exponential
           decay via the superposed information cost. In ICALP 2014, Lecture Notes in Computer
           Science 8572, pages 296–307, 2014. doi:10.1007/978-3-662-43948-7_25; corrected full
           version: https://arxiv.org/abs/1310.7787v3.
[CS15]     A. Chailloux and G. Scarpa. Parallel repetition of free entangled games: simpliﬁcation
           and improvements. arXiv:1410.4397v2, 2015 (ﬁrst version 2014).
           https://arxiv.org/abs/1410.4397v2.
[CHTW04]   R. Cleve, P. Høyer, B. Toner, and J. Watrous. Consequences and limits of nonlocal
           strategies. In Proceedings of the 19th IEEE Conference on Computational Complexity,
           pages 236–249, 2004. doi:10.1109/CCC.2004.1313847;
           https://arxiv.org/abs/quant-ph/0404076v1.
[CSUU08]   R. Cleve, W. Slofstra, F. Unger, and S. Upadhyay. Perfect parallel repetition theorem for
           quantum XOR proof systems. Computational Complexity 17:282–299, 2008.
           doi:10.1007/s00037-008-0250-4.
[DSV15]    I. Dinur, D. Steurer, and T. Vidick. A parallel repetition theorem for entangled projection
           games. Computational Complexity 24(2):201–254, 2015. doi:10.1007/s00037-015-0098-3.
           Full arXiv version, including Lemma 17: arXiv:1310.4113v2.
[FMZ25]    H. Fu, K. Mastel, and X. Zhang. Succinct perfect zero-knowledge for MIP∗ .
           arXiv:2503.04517v2, 2025. https://arxiv.org/abs/2503.04517v2.
[Hol09]    T. Holenstein. Parallel repetition: Simpliﬁcation and the no-signaling case. Theory of
           Computing 5:141–172, 2009. doi:10.4086/toc.2009.v005a008.
[JPY14]    R. Jain, A. Pereszlényi, and P. Yao. A parallel repetition theorem for entangled two-player
           one-round games under product distributions. In Proceedings of the 29th IEEE Conference
           on Computational Complexity, pages 209–216, 2014. doi:10.1109/CCC.2014.29.
[KRT10]    J. Kempe, O. Regev, and B. Toner. Unique games with entangled provers are easy. SIAM
           Journal on Computing 39(7):3207–3229, 2010. doi:10.1137/090772885.
[KV11]     J. Kempe and T. Vidick. Parallel repetition of entangled games. In Proceedings of the
           43rd ACM Symposium on Theory of Computing, pages 353–362, 2011.
           doi:10.1145/1993636.1993684.
[Kim14]    I. H. Kim. Modulus of convexity for operator convex functions. Journal of Mathematical
           Physics 55:082201, 2014. doi:10.1063/1.4890292; https://arxiv.org/abs/1310.0746v3.
[Lin25]    J. Lin. MIPco = coRE. arXiv:2510.07162, 2025. https://arxiv.org/abs/2510.07162.
[NC10]     M. A. Nielsen and I. L. Chuang. Quantum Computation and Quantum Information. 10th
           Anniversary Edition, Cambridge University Press, 2010.
[Pet07]    D. Petz. Bregman divergence as relative operator entropy. Acta Mathematica Hungarica
           116:127–131, 2007. doi:10.1007/s10474-007-6014-9.
[Rao11]    A. Rao. Parallel repetition in projection games and a concentration bound. SIAM Journal
           on Computing 40(6):1871–1891, 2011. doi:10.1137/080734042.
[Raz98]    R. Raz. A parallel repetition theorem. SIAM Journal on Computing 27(3):763–803, 1998.
           doi:10.1137/S0097539795280895.
[Raz11]    R. Raz. A counterexample to strong parallel repetition. SIAM Journal on Computing
           40(3):771–777, 2011. doi:10.1137/090747270.
[Wat18]    J. Watrous. The Theory of Quantum Information. Cambridge University Press, 2018.
           doi:10.1017/9781316848142.


                                                181
[Yue16]   H. Yuen. A parallel repetition theorem for all entangled games. In 43rd International
          Colloquium on Automata, Languages, and Programming, LIPIcs 55, article 77, 2016.
          doi:10.4230/LIPIcs.ICALP.2016.77. Full version: https://arxiv.org/abs/1604.04340.




                                              182
