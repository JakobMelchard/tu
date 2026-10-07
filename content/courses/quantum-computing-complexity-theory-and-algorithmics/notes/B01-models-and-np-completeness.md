# B01 Models of computation and NP-completeness

Complexity theory classifies problems by the resources (time, space, randomness, qubits) needed to solve them on a fixed machine model, as a function of input length. This note fixes the model (Turing machines), the two basic classes P and NP, and the tool that makes NP a coherent class: polynomial-time reductions and NP-completeness (Cook-Levin). Everything later (B02 to B06) is built on the same skeleton: a resource bound, a class, a complete problem. References: Papadimitriou ch. 2, 7, 8-9 [S26]; Kleinberg & Tardos ch. 8 [S25]; Pichler's own recapitulation deck, which fixes the vocabulary this note uses (decision vs function vs optimization vs enumeration vs counting problems, Cook vs Karp reductions, C-hard and C-complete) [S14]. The random-access machine and "problem reductions" bullets come from 192.042, whose content moved into this course in 2026W [S4]. Cook-Levin [S56]. Exam 1 material.

## Definitions

**Turing machine (TM).** A 7-tuple $M = (Q, \Sigma, \Gamma, \delta, q_0, q_{acc}, q_{rej})$: finite state set $Q$, input alphabet $\Sigma$, tape alphabet $\Gamma \supset \Sigma \cup \{\sqcup\}$, transition function $\delta : Q \times \Gamma \to Q \times \Gamma \times \{L, R\}$, start state $q_0$, halting states $q_{acc} \ne q_{rej}$. A **configuration** is $(q, w, i)$: state, tape contents, head position; written as the string $w_1 \dots w_{i-1}\, q\, w_i \dots w_m$. $\delta$ defines the one-step relation $C \vdash C'$. $M$ accepts $x$ if $q_0 x \vdash^* C$ with $C$ in state $q_{acc}$. The language $L(M) = \{x : M \text{ accepts } x\}$. A decision problem is a language $L \subseteq \Sigma^*$.

**Time and space.** $\mathrm{time}_M(x)$ = number of steps until halting; $T_M(n) = \max_{|x| = n} \mathrm{time}_M(x)$. $\mathrm{space}_M(x)$ = number of distinct cells visited; $S_M(n)$ analogously. Always as functions of the input length $n = |x|$, never of the numeric value of the input (a number $N$ has length $\log N$).

**Multi-tape TMs.** $k$ tapes with independent heads, $\delta : Q \times \Gamma^k \to Q \times \Gamma^k \times \{L,R,S\}^k$. Simulation overhead (Papadimitriou Thm 2.1): a $k$-tape TM running in time $T(n)$ is simulated by a 1-tape TM in time $O(T(n)^2)$ (store all $k$ tapes interleaved, mark the head positions; each simulated step sweeps the used part of the tape, length $O(T(n))$). Space is preserved up to a constant. Consequence: "polynomial time" does not depend on the number of tapes. Similarly a random-access machine is simulated with polynomial overhead. This model-independence is the (classical) **Church-Turing thesis** in its "extended" form: every reasonable model is polynomially equivalent to a TM. B06 discusses why quantum computers challenge exactly the "extended" part.

**Random access machine (RAM).** A machine with an unbounded array of integer registers $r_0, r_1, \dots$, indirect addressing, and the instructions load/store/add/subtract/jump-if-zero. Under the **logarithmic cost** measure (a step on operands of $b$ bits costs $b$) a RAM and a Turing machine simulate each other with polynomial overhead, so P, NP, PSPACE and everything built on them are model-independent; under the *unit* cost measure they are not (repeated squaring builds $2^{2^n}$ in $n$ steps), which is why complexity theory uses logarithmic cost or Turing machines. The RAM is the reason "$O(n\log n)$ sorting" in the A-series and "polynomial time" here mean the same thing. The model is named explicitly on the syllabus of 192.042, "Formal models of computation (Turing machines, random access machines, ...)", whose content merged into this course in 2026W [S4], and Pichler's recapitulation deck lists "Turing machines as a reasonable model of computation" [S14].

**Nondeterministic TM (NTM).** $\delta : Q \times \Gamma \to \mathcal P(Q \times \Gamma \times \{L,R\})$; the computation on $x$ is a tree of configurations. $N$ accepts $x$ iff **some** branch reaches $q_{acc}$. Time = depth of the tree. An NTM is not a physical device; it is a definition that turns out to capture "problems with short checkable solutions".

**Classes.**
$$\mathrm{DTIME}(f) = \{L : \exists \text{ TM deciding } L \text{ in time } O(f(n))\}, \quad \mathrm{NTIME}(f), \ \mathrm{SPACE}(f), \ \mathrm{NSPACE}(f) \text{ analogously.}$$
$$\mathrm P = \bigcup_k \mathrm{DTIME}(n^k), \qquad \mathrm{NP} = \bigcup_k \mathrm{NTIME}(n^k), \qquad \mathrm{coNP} = \{\bar L : L \in \mathrm{NP}\}.$$

**NP via verifiers (second definition).** $L \in \mathrm{NP}$ iff there is a polynomial $p$ and a polynomial-time TM $V$ (the verifier) with
$$x \in L \iff \exists\, c \in \{0,1\}^{p(|x|)} : V(x, c) = 1.$$
$c$ is a **certificate** (witness). Example: SAT, certificate = satisfying assignment; HAMILTONIAN CYCLE, certificate = the cycle. coNP: $x \in L \iff \forall c: V(x,c) = 1$ (e.g. UNSAT, TAUTOLOGY).

**Karp reduction.** $A \le_p B$ if there is a polynomial-time computable $f$ with $x \in A \iff f(x) \in B$ for all $x$. (Many-one: one query to $B$, answer taken as is. Cook/Turing reductions allow many adaptive queries; in this course reductions are Karp unless stated.)

**NP-hard / NP-complete.** $B$ is NP-hard if $A \le_p B$ for every $A \in \mathrm{NP}$; NP-complete if additionally $B \in \mathrm{NP}$.

## Results

**Theorem (NTM = verifier).** The two definitions of NP coincide.
*Proof.* ($\Leftarrow$) Given $V, p$: the NTM guesses $c$ bit by bit ($p(n)$ nondeterministic steps), then runs $V(x,c)$ deterministically. Some branch accepts iff some $c$ works. ($\Rightarrow$) Given an NTM $N$ with time $q(n)$: WLOG every step has at most 2 choices (a $d$-way choice is $\lceil \log d \rceil$ binary choices, constant blow-up). The certificate is the sequence of choices $c \in \{0,1\}^{q(n)}$; the verifier simulates $N$ on $x$ following $c$ and accepts iff that branch accepts. Polynomial time in $|x|$. $\square$

**Lemma (reductions compose).** $A \le_p B$ and $B \le_p C$ imply $A \le_p C$: $g \circ f$ runs in time $\mathrm{poly}(|f(x)|) \le \mathrm{poly}(\mathrm{poly}(|x|))$ because a polynomial-time function has polynomially bounded output. Also: $A \le_p B$ and $B \in \mathrm P$ imply $A \in \mathrm P$; contrapositive: $A \le_p B$ and $A$ NP-hard imply $B$ NP-hard. This is **how one proves hardness: reduce a known hard problem TO the new problem.**

**Theorem (Cook-Levin).** SAT is NP-complete.
*Proof sketch.* Membership: certificate = assignment, check in linear time. Hardness: let $L \in \mathrm{NP}$ via NTM $N$ with time $p(n)$ (single tape WLOG). A branch of the computation on $x$ is a **tableau**: $p(n) + 1$ rows (configurations), each a string of length $p(n) + 2$ over $\Gamma \cup (Q \times \Gamma)$ (the head position is marked by a composite symbol "state $q$ reading $a$"). Boolean variables $y_{i,j,s}$ = "cell $(i,j)$ contains symbol $s$", $O(p(n)^2 \cdot |\Gamma \cup Q\times\Gamma|)$ of them. Clauses: (i) each cell holds exactly one symbol; (ii) row 0 is the start configuration $q_0 x \sqcup \dots$; (iii) some row contains $q_{acc}$; (iv) **locality**: row $i+1$ follows from row $i$ by one step of $\delta$. Because a TM step changes only the cells around the head, correctness of a step is checked by $2 \times 3$ **windows**: for every $(i, j)$ the six symbols $y_{i,j-1..j+1}, y_{i+1,j-1..j+1}$ must be one of a constant number of legal patterns (determined by $\delta$; the nondeterminism is simply that several patterns are legal). Each window constraint is a constant-size CNF; total formula size $O(p(n)^2)$, computable in polynomial time. Satisfying assignments correspond exactly to accepting branches. $\square$

**SAT $\le_p$ 3SAT.** Replace a clause $C = (\ell_1 \vee \dots \vee \ell_k)$, $k \ge 4$, by
$$(\ell_1 \vee \ell_2 \vee y_1)(\neg y_1 \vee \ell_3 \vee y_2)(\neg y_2 \vee \ell_4 \vee y_3) \cdots (\neg y_{k-3} \vee \ell_{k-1} \vee \ell_k)$$
with fresh $y_i$ (clauses of length $< 3$: repeat a literal). *Equisatisfiability.* If some $\ell_j$ is true set $y_i = 1$ for $i < j - 1$ and $y_i = 0$ for $i \ge j-1$: every new clause contains a true literal. Conversely, if all $\ell_j$ are false the chain forces $y_1 = 1$, then $y_2 = 1$, ..., $y_{k-3} = 1$, and the last clause $(\neg y_{k-3} \vee \ell_{k-1} \vee \ell_k)$ is false. Size grows linearly. Note that the new formula is over more variables; the assignments correspond, they are not identical.

**3SAT $\le_p$ INDEPENDENT SET $\le_p$ VERTEX COVER (KT 8.2, 8.4).** For a 3-CNF with $m$ clauses build $G$: a triangle per clause with vertices labelled by the three literal occurrences, plus an edge between every pair of occurrences of $x$ and $\neg x$. Set $k = m$. *Claim:* $F$ satisfiable iff $G$ has an independent set of size $m$. ($\Rightarrow$) pick one true literal per clause: one vertex per triangle, never both $x$ and $\neg x$, so independent. ($\Leftarrow$) an independent set of size $m$ has exactly one vertex per triangle (two in one triangle are adjacent); set the chosen literals true; consistent because complementary occurrences are adjacent; every clause has a true literal. Then $S$ is independent iff $V \setminus S$ is a vertex cover (an edge is missed by $V \setminus S$ iff both endpoints lie in $S$), so IS with $k$ $\Leftrightarrow$ VC with $|V| - k = 2m$.

**VERTEX COVER $\le_p$ SUBSET SUM (KT 8.8).** Graph $G$ with $n$ vertices, edges $e_0, \dots, e_{m-1}$, budget $k$. Base-4 numbers with $m + 1$ digits:
$$a_v = 4^m + \sum_{i : v \in e_i} 4^i \ (v \in V), \qquad b_i = 4^i \ (0 \le i < m), \qquad W = k \cdot 4^m + 2 \sum_{i=0}^{m-1} 4^i .$$
Digit $i$ of any subset sum is at most $1 + 2 = 3 < 4$ (two endpoints plus $b_i$), so **there are no carries** and digits can be read off independently. If $C$ is a cover of size $k$: take $\{a_v : v \in C\}$ and $b_i$ for every edge covered exactly once; digit $m$ is $k$, every edge digit is $2$. Conversely a subset with sum $W$ has exactly $k$ vertex numbers (digit $m$) and every edge digit equal to 2, which needs at least one endpoint in the subset (the $b_i$ alone give 1): a cover of size $k$. Numbers have $O(m)$ digits, polynomial size; this is why SUBSET SUM is NP-complete although it has a pseudo-polynomial $O(nW)$ DP: $W$ here is exponential in $m$.

**Further NP-complete problems (statement).** 3SAT $\le_p$ HAMILTONIAN CYCLE (KT 8.5, one gadget per variable, a "diamond" chain visited left-to-right or right-to-left = truth value, clause nodes spliced in), 3SAT $\le_p$ 3-COLOURING (KT 8.7, a base triangle T/F/B, a variable pair $x, \neg x$ both adjacent to B, an "OR gadget" per clause). Also TSP (decision), CLIQUE, SET COVER, PARTITION, KNAPSACK (decision), INTEGER PROGRAMMING (feasibility).

**What NP-completeness means.** If any NP-complete problem is in P then P = NP (every $A \in \mathrm{NP}$ reduces to it). If P $\ne$ NP then no NP-complete problem has a polynomial algorithm, and (Ladner 1975 [S56]) there are problems in NP that are neither in P nor NP-complete (**NP-intermediate**; candidates: FACTORING, GRAPH ISOMORPHISM). Note $\mathrm P \subseteq \mathrm{NP} \cap \mathrm{coNP}$; if an NP-complete problem were in coNP then NP = coNP, also believed false. FACTORING (decision version) is in NP $\cap$ coNP, one reason it is not expected to be NP-complete and one reason Shor's algorithm (B06) does not imply NP $\subseteq$ BQP.

**Recipe for an exam-style NP-completeness proof.** (1) Membership: name the certificate, bound its length by a polynomial, give the polynomial-time check. (2) Hardness: choose a known NP-complete problem $A$, give $f$ from instances of $A$ to instances of the new problem $B$ (direction: **known-hard $\to$ new**), argue $f$ is polynomial-time, prove both directions of $x \in A \iff f(x) \in B$.

## Worked example

$F = (x_1 \vee x_2 \vee x_3)(\neg x_1 \vee \neg x_2 \vee x_3)(\neg x_3 \vee x_1 \vee x_2)$, DIMACS `[[1,2,3],[-1,-2,3],[-3,1,2]]`, $m = 3$.

*Graph.* Vertices $(i, j)$ = occurrence $j$ in clause $i$: $(0,0){=}x_1, (0,1){=}x_2, (0,2){=}x_3;\ (1,0){=}\neg x_1, (1,1){=}\neg x_2, (1,2){=}x_3;\ (2,0){=}\neg x_3, (2,1){=}x_1, (2,2){=}x_2$. Edges: 9 triangle edges plus complementary pairs $(0,0)(1,0)$, $(0,1)(1,1)$, $(0,2)(2,0)$, $(1,2)(2,0)$, $(2,1)(1,0)$, $(2,2)(1,1)$: 15 edges, $k_{IS} = 3$, $k_{VC} = 6$.

*Assignment to independent set.* $x_1 = 1, x_2 = 0, x_3 = 1$ satisfies $F$. True occurrences per clause: clause 0: $(0,0)$; clause 1: $(1,1)$ or $(1,2)$; clause 2: $(2,1)$. Choose $S = \{(0,0), (1,2), (2,1)\}$. Check: no triangle edge (one per clause), $(0,0)$'s only cross edge goes to $(1,0) \notin S$, $(1,2)$'s to $(2,0) \notin S$, $(2,1)$'s to $(1,0) \notin S$. Independent, size 3. Cover $= V \setminus S$, size 6; a cover of size 5 is impossible because three vertex-disjoint triangles need two vertices each (test `test_worked_example_from_note`).

*Subset sum on a toy graph* (the full instance has 24 numbers of 16 base-4 digits, done by `sat.py`): triangle $a, b, c$ with $e_0 = ab, e_1 = bc, e_2 = ac$, $k = 2$, $m = 3$:
$$a_a = 64 + 4^0 + 4^2 = 81, \quad a_b = 64 + 4^0 + 4^1 = 69, \quad a_c = 64 + 4^1 + 4^2 = 84, \quad b_0, b_1, b_2 = 1, 4, 16, \quad W = 2 \cdot 64 + 2 \cdot 21 = 170 = (2222)_4.$$
Cover $\{a, b\}$: $81 + 69 = 150 = (2112)_4$: digit $e_0$ is already 2 (both endpoints), digits $e_1, e_2$ are 1; add $b_1 + b_2 = 20$: $170$. Any subset hitting 170 must contain exactly two vertex numbers (digit 3 equals 2) and every edge digit reaches 2 only if a chosen vertex contributes, i.e. every edge is covered.

## Pitfalls

- **Direction of the reduction.** To show $B$ hard you need $A \le_p B$ with $A$ known hard: transform $A$-instances into $B$-instances. Reducing $B$ to SAT shows only $B \in \mathrm{NP}$ (uselessly, since everything in NP reduces to SAT).
- NP is "nondeterministic polynomial", not "non-polynomial". P $\subseteq$ NP; exponential brute force solves every NP problem, that is not the point.
- The certificate must have polynomial length **and** be checkable in polynomial time. "Guess a factorisation, check by multiplying" is fine; "guess whether a formula is a tautology" is not (no short certificate known for UNSAT: that is the NP vs coNP question).
- NP-hard is not NP-complete: HALTING is NP-hard but not in NP. TQBF is NP-hard, believed not in NP (B02).
- Input length. SUBSET SUM with target $W$ written in unary is in P (DP); in binary it is NP-complete. PRIMES with $N$ in binary has input length $\log N$; trial division is exponential in the input length.
- Equisatisfiable is not equivalent: SAT $\to$ 3SAT adds variables; the reduction preserves the yes/no answer, not the set of models.
- Karp vs Turing reductions: "solve $A$ by calling a $B$-oracle many times" is a Turing reduction. It suffices for "if $B \in \mathrm P$ then $A \in \mathrm P$" but NP-completeness is defined with Karp reductions.

## Exam-style questions

1. *State the two definitions of NP and prove they agree.* See the theorem above: guess-and-verify NTM, and choice sequence as certificate; both directions need only that the polynomial bound on time bounds the certificate length.
2. *Show 3SAT $\le_p$ INDEPENDENT SET and give the instance for $(x \vee y \vee z)(\neg x \vee \neg y \vee z)$.* Two triangles, cross edges $x{-}\neg x$ and $y{-}\neg y$, $k = 2$. Both directions of the equivalence as in Results.
3. *Prove that VERTEX COVER is NP-complete.* Membership: certificate is the set $C$, $|C| \le k$, check every edge has an endpoint in $C$, $O(m)$. Hardness: INDEPENDENT SET $\le_p$ VERTEX COVER via $(G, k) \mapsto (G, n - k)$, complement argument; IS is hard by the triangle reduction from 3SAT.
4. *Why do the base-4 digits in VC $\le_p$ SUBSET SUM never carry, and why does the reduction not contradict the $O(nW)$ DP for SUBSET SUM?* Each digit sums to at most $1 + 1 + 1 = 3$. $W \approx k \cdot 4^m$ is exponential in the instance size $m$, so $O(nW)$ is exponential; pseudo-polynomial, not polynomial.
5. *If someone found a polynomial algorithm for 3-COLOURING, what follows for FACTORING?* 3-COLOURING is NP-complete, so P = NP; FACTORING (decision version) is in NP, hence in P. Conversely a polynomial FACTORING algorithm (e.g. Shor on a quantum computer) says nothing about P vs NP, since FACTORING is not known to be NP-hard.
6. *Sketch why the Cook-Levin formula has polynomial size.* Tableau of $p(n) \times p(n)$ cells, each with $O(1)$ variables; window constraints are $O(1)$ clauses per cell; total $O(p(n)^2)$.

## Code

`src/py/complexity/sat.py`: `brute_force_sat`, `dpll` (cross-check), `sat_to_3sat` (clause splitting), `three_sat_to_vertex_cover` (returns vertices, edges, $k_{IS}$, $k_{VC}$), `assignment_to_independent_set`, `independent_set_exists`, `vertex_cover_exists`, `vertex_cover_to_subset_sum` (base-4 construction), `subset_sum_exists` (exact pruned search). `test_sat.py` checks on 30 seeded tiny CNFs that satisfiability is preserved along SAT $\to$ 3SAT $\to$ IS/VC $\to$ SUBSET SUM and that a satisfying assignment maps to an actual cover and subset.
