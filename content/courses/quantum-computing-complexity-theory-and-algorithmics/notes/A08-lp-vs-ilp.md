# A08 Linear programming versus integer linear programming

Linear programming (LP) optimises a linear function over a polyhedron defined by linear inequalities; it is solvable in polynomial time, has a beautiful duality theory, and is the most versatile modelling tool in algorithm design. Adding the constraint "variables are integers" gives integer linear programming (ILP), which is NP-hard: the geometry changes from a convex polyhedron to a lattice of points inside it. The gap between the two is both the reason ILP is hard and the source of approximation algorithms: solve the LP relaxation, then round. This note gives the definitions, the simplex idea, weak and strong duality, complementary slackness, max-flow/min-cut as a duality instance, the NP-hardness of ILP, integrality gaps, total unimodularity (when the LP is already integral), and the two standard exact ILP methods, branch and bound and cutting planes. Reference: KT 11.6 (LP relaxation and rounding); the rest: Papadimitriou–Steiglitz "Combinatorial Optimization", Vanderbei "Linear Programming", Schrijver "Theory of Linear and Integer Programming"; Chvátal "Linear Programming". References: Kleinberg & Tardos ch. 11.6 and 7.5 [S25]. Exam 1 material.

## Definitions

**LP standard form.** $\max\ c^\top x$ subject to $Ax \le b$, $x \ge 0$, with $A \in \mathbb{R}^{m \times n}$, $b \in \mathbb{R}^m$, $c \in \mathbb{R}^n$. Any LP converts to this form: $\min c^\top x = -\max(-c)^\top x$; $a^\top x \ge \beta \iff -a^\top x \le -\beta$; $a^\top x = \beta$ as two inequalities; free $x$ as $x^+ - x^-$. *Equality form* $Ax = b, x \ge 0$ (used by simplex) is obtained with slack variables $s = b - Ax \ge 0$.

**Feasible region.** $P = \{x : Ax \le b, x \ge 0\}$, a *polyhedron* (intersection of finitely many half-spaces), convex. Bounded polyhedron = polytope. LP is *infeasible* ($P = \emptyset$), *unbounded* (objective $\to \infty$ on $P$), or has an optimal solution.

**Vertex / basic feasible solution.** $x \in P$ is a vertex (extreme point) if it is not a proper convex combination of two other points of $P$; equivalently, $n$ linearly independent constraints are tight at $x$. In equality form with $A$ of full row rank $m$: choose a *basis* $B$ of $m$ columns, set non-basic variables to 0, solve $A_B x_B = b$; if $x_B \ge 0$ this is a *basic feasible solution* (BFS). Vertices = BFSs. There are at most $\binom{n}{m}$ of them.

**Dual LP.** Primal $(P)$: $\max c^\top x$, $Ax \le b$, $x \ge 0$. Dual $(D)$: $\min b^\top y$, $A^\top y \ge c$, $y \ge 0$. One dual variable per primal constraint, one dual constraint per primal variable; the dual of the dual is the primal.

**ILP.** $\max c^\top x$, $Ax \le b$, $x \in \mathbb{Z}^n_{\ge 0}$ (or $x \in \{0,1\}^n$: 0/1-ILP). Its **LP relaxation** drops integrality. For a maximisation $\mathrm{LP} \ge \mathrm{ILP}$; for a minimisation $\mathrm{LP} \le \mathrm{ILP}$.

**Integrality gap.** $\sup_I \mathrm{ILP}(I)/\mathrm{LP}(I)$ over instances (minimisation); the worst-case factor lost by relaxing. Any algorithm that proves its ratio by comparing to the LP value cannot beat the gap.

**Totally unimodular (TU).** A matrix is TU if every square submatrix has determinant in $\{-1, 0, 1\}$. (Entries are then in $\{-1, 0, 1\}$.)

## Results

### Fundamental theorem of LP

If an LP has an optimal solution, it has one at a vertex. *Proof idea.* Let $x^*$ be optimal and not a vertex; then some direction $d \ne 0$ has $x^* \pm \epsilon d \in P$. Since $c^\top d$ cannot be positive or negative (else one of $x^* \pm \epsilon d$ is better), $c^\top d = 0$; move along $d$ until a new constraint becomes tight (possible if $P$ contains no line, which $x \ge 0$ guarantees). Repeat; the number of tight independent constraints increases each time, so this ends at a vertex with the same objective. $\square$ So LP is a finite search over vertices, but $\binom{n}{m}$ is exponential.

### Simplex (Dantzig 1947)

Walk from vertex to adjacent vertex (two BFSs are adjacent if their bases differ in one column), each step improving the objective; stop when no improving neighbour exists, which by convexity is a global optimum. A *pivot* swaps one basic and one non-basic variable: choose an entering variable with positive *reduced cost* $\bar c_j = c_j - c_B^\top A_B^{-1} A_j$ (increasing it improves the objective), increase it until a basic variable hits 0 (the *ratio test* picks the leaving variable); if none does, the LP is unbounded. Each pivot is $O(mn)$ arithmetic with the tableau.

*Degeneracy and cycling.* When a BFS has a basic variable at 0, a pivot may not move the point and simplex can cycle through bases forever. **Bland's rule** (enter the lowest-index eligible variable, leave the lowest-index tied variable) provably prevents cycling, so simplex terminates. *Phase I* finds an initial BFS by solving an auxiliary LP with artificial variables.

*Complexity.* Each pivot is polynomial, but the number of pivots is exponential in the worst case for every deterministic pivot rule known: the **Klee–Minty cube** (1972), a perturbed $n$-cube with $2^n$ vertices that Dantzig's rule visits all of. Simplex is nevertheless fast in practice (smoothed analysis, Spielman–Teng: polynomial expected pivots under small random perturbations).

*LP is in P.* The **ellipsoid method** (Khachiyan 1979) solves LP in polynomial time $O(n^4 L)$ with $L$ the bit length; slow in practice but theoretically decisive, and it works with a *separation oracle* (exponentially many constraints are fine as long as a violated one can be found in polynomial time). **Interior-point methods** (Karmarkar 1984, later path-following methods, $O(n^{3.5} L)$ and better) are polynomial and practical. So LP $\in$ P, while the *strongly* polynomial question (running time polynomial in $n, m$ only, independent of bit length) is open.

### Weak duality

**Theorem.** For any primal-feasible $x$ and dual-feasible $y$: $c^\top x \le b^\top y$. *Proof.* $c^\top x \le (A^\top y)^\top x = y^\top A x \le y^\top b$; the first inequality uses $A^\top y \ge c$ and $x \ge 0$, the second $Ax \le b$ and $y \ge 0$. $\square$ Consequences: any dual solution certifies an upper bound; if $c^\top x = b^\top y$ both are optimal; if $(P)$ is unbounded, $(D)$ is infeasible.

Dual interpretation: $y$ are *multipliers* that combine the constraints $a_i^\top x \le b_i$ into $(\sum y_i a_i)^\top x \le \sum y_i b_i$, an inequality that dominates $c^\top x$ coefficientwise; the dual asks for the cheapest such certificate.

### Strong duality (von Neumann, Gale–Kuhn–Tucker)

**Theorem.** If $(P)$ has an optimal solution then so does $(D)$, with equal optimal values. Exactly one of: both optimal with equal values; one unbounded and the other infeasible; both infeasible. *Proof routes:* (a) Farkas' lemma (exactly one of $Ax = b, x \ge 0$ and $A^\top y \ge 0, b^\top y < 0$ has a solution), a separating-hyperplane statement; (b) simplex: at termination the reduced costs are $\le 0$, and $y^\top = c_B^\top A_B^{-1}$ is dual feasible with $b^\top y = c_B^\top x_B = c^\top x$. The dual optimum equals the optimal simplex multipliers. (Not proved here; KT does not prove it either.)

**Complementary slackness.** Primal-feasible $x$ and dual-feasible $y$ are both optimal iff $y_i (b_i - a_i^\top x) = 0$ for all $i$ and $x_j ((A^\top y)_j - c_j) = 0$ for all $j$: a positive multiplier only on a tight constraint, and a positive variable only where the dual constraint is tight. *Proof.* Optimality $\iff$ equality throughout the weak-duality chain, i.e. $y^\top (b - Ax) = 0$ and $x^\top(A^\top y - c) = 0$; both are sums of non-negative terms. $\square$ Use: given a candidate primal optimum, solve the tight dual constraints for $y$ and check dual feasibility (worked example).

### Max-flow / min-cut as LP duality (A06)

Max flow as an LP with path variables: $\max \sum_P f_P$ s.t. $\sum_{P \ni e} f_P \le c_e$ for each edge, $f \ge 0$. Dual: $\min \sum_e c_e y_e$ s.t. $\sum_{e \in P} y_e \ge 1$ for every $s$–$t$ path, $y \ge 0$: a *fractional cut* (edge lengths under which every $s$–$t$ path has length $\ge 1$). Integral solutions $y \in \{0,1\}$ are exactly cuts (the 1-edges must hit every path). Weak duality is Lemma 2 of A06; strong duality says the fractional cut equals the max flow; the max-flow/min-cut theorem says additionally that the dual has an *integral* optimum, i.e. the LP is integral, which follows from total unimodularity below (or from Ford–Fulkerson). Same story: bipartite matching LP $\leftrightarrow$ fractional vertex cover LP, whose integrality is König's theorem.

### ILP is NP-hard

Membership in NP needs care (solutions of polynomial bit length exist, a non-trivial theorem); hardness is immediate. *From vertex cover:* $\min \sum_v x_v$, $x_u + x_v \ge 1$ for every edge, $x \in \{0,1\}$; an ILP solver decides "cover of size $\le k$". *From 3-SAT:* variables $x_i \in \{0,1\}$; clause $(x_1 \vee \bar x_2 \vee x_3)$ becomes $x_1 + (1 - x_2) + x_3 \ge 1$; feasibility of the 0/1-ILP is satisfiability. Since 0/1-ILP is a special case, general ILP is NP-hard; Lenstra showed it is polynomial when the *number of variables* is fixed.

### LP relaxation and integrality gap: vertex cover

Relaxation: $0 \le x_v \le 1$. $\mathrm{LP} \le \mathrm{OPT}$; rounding $x_v \ge 1/2$ gives $\le 2\,\mathrm{LP}$ (A07).

*Complete graph $K_n$.* $\mathrm{OPT} = n - 1$ (two uncovered vertices would leave their edge uncovered). LP: $x_v = 1/2$ for all $v$ is feasible with value $n/2$; it is optimal because summing the constraints over all $\binom n2$ edges gives $(n-1)\sum_v x_v \ge \binom n2$, i.e. $\sum_v x_v \ge n/2$. Gap $= (n-1)/(n/2) \to 2$.

*Odd cycle $C_{2k+1}$.* $\mathrm{OPT} = k + 1$ ($2k+1$ edges, each vertex covers 2, so $\ge \lceil (2k+1)/2 \rceil = k+1$; every other vertex plus one neighbour of the leftover edge achieves it). LP: all $1/2$, value $k + 1/2$. Gap $(k+1)/(k + 1/2) \to 1$ as $k$ grows but equals $4/3$ on the triangle; $K_n$ is the family with gap $\to 2$.

*Half-integrality (Nemhauser–Trotter).* Every vertex cover LP has an optimal solution with $x_v \in \{0, \frac12, 1\}$, and the vertices with $x_v = 1$ (resp. 0) can be assumed in (out of) some optimal cover; the hard core is the $\frac12$-part.

### Total unimodularity: when LP = ILP

**Theorem (Hoffman–Kruskal 1956).** If $A$ is TU and $b$ is integral, every vertex of $\{x : Ax \le b, x \ge 0\}$ is integral. *Proof.* A vertex solves $A' x = b'$ for some nonsingular $n \times n$ subsystem (rows of $A$ and of $I$); by Cramer's rule $x_j = \det(A'_j)/\det(A')$ with $\det A' = \pm 1$ and $\det A'_j$ integral. $\square$ Hence any LP with a TU constraint matrix and integral right-hand side has an integral optimum found by simplex/interior point: the ILP is polynomial.

**Examples.** (i) The incidence matrix of a *bipartite* graph (rows = vertices, columns = edges) is TU: proof by induction on submatrix size; a square submatrix with a column of $\le 1$ ones expands along it, otherwise every column has one $L$-row and one $R$-row entry, so (rows of $L$) $-$ (rows of $R$) $= 0$ and the determinant is 0. Consequence: the bipartite matching LP $\{\sum_{e \ni v} x_e \le 1, x \ge 0\}$ and the vertex cover LP on bipartite graphs are integral: König's theorem again. (ii) The vertex–edge incidence matrix of a *directed* graph (entries $+1$ at tail, $-1$ at head) is TU (each column has one $+1$ and one $-1$; same induction). Consequence: flow LPs with integral capacities and demands have integral optima; that is the integrality theorem of A06 without Ford–Fulkerson. (iii) Interval matrices (consecutive ones in each row) are TU: interval scheduling LPs are integral. Non-example: the incidence matrix of an odd cycle has determinant $\pm 2$, which is exactly why the vertex cover LP on a triangle is fractional.

### Exact ILP methods

**Branch and bound.** Solve the LP relaxation. If the solution is integral, done. Else pick a fractional $x_j = f$ and *branch* into $x_j \le \lfloor f \rfloor$ and $x_j \ge \lceil f \rceil$; solve each recursively. *Bound:* keep the best integral solution found (the incumbent, value $z^*$); a subproblem whose LP value is $\le z^*$ (maximisation) cannot contain a better integer point and is *pruned*; infeasible subproblems are pruned. Correct because the LP value bounds every integer point in the subtree. Worst case exponential (a tree of depth $n$); in practice the pruning does most of the work. Depth-first finds incumbents quickly; best-first minimises the tree.

**Cutting planes (Gomory 1958).** Solve the LP; if $x^*$ is fractional, add a *valid inequality* (satisfied by every integer feasible point) that $x^*$ violates, and re-solve. *Gomory's cut* from a simplex row $x_B + \sum_j \bar a_j x_j = \bar b$ with $\bar b \notin \mathbb{Z}$: since $x \ge 0$ integral, $x_B + \sum \lfloor \bar a_j \rfloor x_j \le \bar b$, hence $\le \lfloor \bar b \rfloor$; subtracting gives $\sum_j (\bar a_j - \lfloor \bar a_j \rfloor) x_j \ge \bar b - \lfloor \bar b \rfloor$, violated at $x^*$ (where non-basic $x_j = 0$). Finitely many Gomory cuts reach an integer optimum in theory; modern solvers combine cuts and branching (*branch and cut*) with problem-specific cuts, e.g. for vertex cover the odd-cycle inequality $\sum_{v \in C} x_v \ge (|C| + 1)/2$ that kills the all-$\frac12$ point on a triangle.

**$\frac12$-rounding as the cheap alternative.** For vertex cover, rounding the LP is a $2$-approximation in one LP solve (A07); branch and bound is exact but exponential. Both start from the same relaxation: the LP value is the common yardstick.

## Worked example

**Primal.** $\max\ 3x_1 + 2x_2$ s.t. $x_1 + x_2 \le 4$, $x_1 + 3x_2 \le 6$, $x \ge 0$.

Feasible region: vertices $(0,0)$, $(4,0)$, $(3,1)$ (intersection of the two constraints: $x_1 + x_2 = 4$, $x_1 + 3x_2 = 6 \Rightarrow x_2 = 1$), $(0, 2)$. Objective at vertices: $0, 12, 11, 4$. Optimum $x^* = (4, 0)$, value 12.

Simplex from $(0,0)$ with slacks $s_1, s_2$: basis $\{s_1, s_2\}$, reduced costs $(3, 2)$; enter $x_1$ (largest); ratio test $\min(4/1, 6/1) = 4$, $s_1$ leaves; new vertex $(4,0)$. Reduced costs now: $x_2$: $2 - 3 \cdot 1 = -1$, $s_1$: $0 - 3 = -3$: no improving direction, stop.

**Dual.** $\min\ 4y_1 + 6y_2$ s.t. $y_1 + y_2 \ge 3$, $y_1 + 3y_2 \ge 2$, $y \ge 0$. Complementary slackness at $x^*$: constraint 2 is slack ($4 < 6$) $\Rightarrow y_2 = 0$; $x_1 > 0 \Rightarrow$ first dual constraint tight, $y_1 = 3$. Check dual feasibility: $3 + 0 \ge 2$. Dual value $12$ = primal value: both optimal, certificate complete. Interpretation: constraint 1 is worth 3 per unit of $b_1$ (shadow price), constraint 2 is worthless.

**ILP.** Add $x \in \mathbb{Z}^2$: the LP optimum $(4,0)$ is already integral, nothing to do. Change the objective to $\max\ x_1 + 4x_2$: LP optimum at $(0, 2)$, value 8, integral again. Change constraint 2 to $x_1 + 3x_2 \le 7$: vertices $(0, 7/3)$, $(2.5, 1.5)$; with objective $x_1 + 4x_2$ the LP optimum is $(0, 7/3)$, value $28/3 \approx 9.33$. *Branch and bound* on $x_2 = 7/3$: (a) $x_2 \le 2$: with $x_2 = 2$ the constraints give $x_1 \le 1$, LP optimum $(1, 2)$, value $9$, integral: incumbent $z^* = 9$. (b) $x_2 \ge 3$: $3x_2 \le 7$ is violated, infeasible, pruned. ILP optimum $9$ at $(1, 2)$, one branch closed the gap $28/3$ vs $9$. *Gomory cut* instead: in the optimal tableau (basis $\{x_2, s_1\}$) the row of $x_2$ reads $x_2 + \tfrac13 x_1 + \tfrac13 s_2 = \tfrac73$. Fractional parts: $\tfrac13 x_1 + \tfrac13 s_2 \ge \tfrac13$, i.e. $x_1 + s_2 \ge 1$; substituting $s_2 = 7 - x_1 - 3x_2$ gives $3x_2 \le 6$, i.e. $x_2 \le 2$. This is valid for every integer point (the derivation only used integrality and non-negativity), cuts off $(0, 7/3)$, and re-solving the LP with it gives $(1, 2)$, value $9$, integral.

**Vertex cover on a triangle, LP vs ILP.** LP: $(\frac12, \frac12, \frac12)$, value $1.5$. $\frac12$-rounding: all three, cost 3. Branch on $x_1$: $x_1 = 0$ forces $x_2 = x_3 = 1$, cost 2; $x_1 = 1$: LP $(1, \frac12, \frac12)$ value 2, branch $x_2 = 0 \Rightarrow x_3 = 1$, cost 2. ILP optimum 2. Odd-cycle cut $x_1 + x_2 + x_3 \ge 2$ gives the LP value 2 at once.

## Pitfalls

- Standard form is a convention; when writing the dual, get the direction right: $\max/\le/x \ge 0$ pairs with $\min/\ge/y \ge 0$; an equality constraint gives a free dual variable; a free primal variable gives a dual equality.
- Weak duality is a two-line proof and is always expected in full; strong duality is quoted, not proved.
- "LP is in P" is true via ellipsoid/interior point; simplex is *not* known to be polynomial, though it is the practical choice.
- Vertices of the LP relaxation are generally fractional; an integral LP optimum happens for TU matrices (bipartite matching, flows), not in general. Rounding must be justified: feasibility of the rounded point and a bound on its cost.
- The integrality gap bounds *LP-based* analyses, not all algorithms; and the gap of vertex cover is $2 - o(1)$, matching the best known ratio, which is a coincidence in this case explained by UGC hardness (A07).
- Branch and bound prunes with the LP bound, so it needs the LP solved to optimality at each node; bounding with a heuristic is invalid.
- ILP feasibility is NP-hard even with $A$ having entries in $\{0, \pm 1\}$ (3-SAT encoding); being TU is a strong structural property, not the norm.

## Exam-style questions

1. **Write the dual of $\min\ c^\top x$ s.t. $Ax \ge b$, $x \ge 0$, and prove weak duality for this pair.** Dual: $\max\ b^\top y$, $A^\top y \le c$, $y \ge 0$. For feasible $x, y$: $b^\top y \le (Ax)^\top y = x^\top A^\top y \le x^\top c$, using $y \ge 0, Ax \ge b$ then $x \ge 0, A^\top y \le c$.

2. **What is a basic feasible solution, and why does simplex only need to look at them?** A feasible point with $n$ linearly independent tight constraints (a vertex). A linear objective over a polyhedron without lines attains its optimum at a vertex (move along a zero-objective direction until a constraint becomes tight); simplex walks between adjacent vertices.

3. **Show that the vertex cover LP has integrality gap at least $2 - 2/n$.** On $K_n$: LP value $n/2$ (all $\frac12$ is feasible; summing all edge constraints gives $(n-1)\sum x_v \ge \binom n2$, so no smaller value is feasible), ILP value $n-1$; ratio $2(n-1)/n$.

4. **Define total unimodularity and explain why max flow with integer capacities has an integral optimal solution without appealing to Ford–Fulkerson.** All square subdeterminants in $\{0, \pm1\}$. The flow LP's constraint matrix (directed incidence matrix for conservation, identity rows for capacities) is TU; with integral capacities the right-hand side is integral, so by Cramer's rule every vertex is integral, and some vertex is optimal.

5. **Describe branch and bound for a maximisation ILP and justify pruning.** Solve the LP relaxation at each node; if integral, update the incumbent; if fractional, branch on $x_j \le \lfloor x_j^* \rfloor$ / $\ge \lceil x_j^* \rceil$. Prune a node if infeasible or if its LP value is $\le$ the incumbent: every integer point in the node's region satisfies the node's constraints, so its objective is at most the node's LP value, hence cannot beat the incumbent.

## Code

`src/py/algorithmics/lp_ilp.py`: `vertex_cover_lp(adj)` and `vertex_cover_ilp(adj)` (scipy `linprog` for the relaxation with $\frac12$-rounding, `pulp` for the exact ILP; tests compare values on $K_n$ and odd cycles to the closed forms above), `simplex(c, A, b)` (dense tableau with Bland's rule, cross-checked against `linprog`), `branch_and_bound(c, A, b)` on top of `linprog`. Flow LP duality is exercised in `flow.py` tests (A06).
