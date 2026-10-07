# A07 Approximation algorithms and inapproximability

When a problem is NP-hard (B02) we give up on one of three things: exact optimality, polynomial time, or generality. Approximation algorithms give up optimality *by a provable bounded factor*: a polynomial-time algorithm whose output is always within a factor $\rho$ of the optimum, on every input. The proofs have a common shape: find a quantity that lower-bounds the (unknown) optimum, then show the algorithm's cost is at most $\rho$ times that quantity. The second half of the note is the mirror image: for some problems, approximating better than a certain factor is itself NP-hard, which is proved by gap-creating reductions and, at the deep end, by the PCP theorem. Reference: KT chapter 11 (11.1 load balancing, 11.2 center selection, 11.3 set cover, 11.4 vertex cover via pricing, 11.6 LP rounding, 11.8 knapsack FPTAS); inapproximability: Papadimitriou ch. 13, Vazirani "Approximation Algorithms", Arora–Barak ch. 11. References: Kleinberg & Tardos ch. 11 [S25]. This bullet is new in 2025W: the 2024W subject list has no approximation item [S2, S3]. Exam 1 material.

## Definitions

**Optimisation problem.** Instances $I$, feasible solutions $S$, cost (or value) $c(S)$; $\mathrm{OPT}(I)$ = minimum (maximum) cost. The decision version ("is there $S$ with $c(S) \le k$?") is what NP-hardness refers to.

**$\rho$-approximation.** A polynomial-time algorithm $A$ with, for every instance, $c(A(I)) \le \rho \cdot \mathrm{OPT}(I)$ (minimisation, $\rho \ge 1$) or $c(A(I)) \ge \rho \cdot \mathrm{OPT}(I)$ (maximisation, $\rho \le 1$; some authors invert to keep $\rho \ge 1$). $\rho$ is the *approximation ratio* (guarantee); it may depend on the input size, e.g. $\rho = O(\log n)$.

**PTAS** (polynomial-time approximation scheme): a family $A_\epsilon$, for every $\epsilon > 0$ a $(1 + \epsilon)$-approximation running in time polynomial in $n$ for fixed $\epsilon$ (e.g. $n^{1/\epsilon}$ is allowed). **FPTAS** (fully polynomial): time polynomial in $n$ *and* $1/\epsilon$ (e.g. $n^3/\epsilon$).

**APX.** Problems with some constant-factor approximation. **APX-hard**: every APX problem reduces to it by an approximation-preserving (PTAS-)reduction; an APX-hard problem has no PTAS unless P = NP. Hierarchy: FPTAS $\subseteq$ PTAS $\subseteq$ APX $\subseteq$ (problems with $\mathrm{poly}(n)$-factor approximations).

**Load balancing.** $m$ identical machines, $n$ jobs with times $t_j$; assign jobs to machines minimising the *makespan* $T = \max_i T_i$, $T_i = \sum_{j \to i} t_j$. NP-hard (partition).

**Set cover.** Universe $U$, $|U| = n$, sets $S_1..S_k \subseteq U$ with weights $w_i \ge 0$; choose sets covering $U$ with minimum total weight. $d = \max_i |S_i|$.

**Vertex cover.** Graph $G$; a set $C \subseteq V$ touching every edge; minimise $|C|$ (or weight $\sum_{v \in C} w_v$). NP-hard (B02).

**Knapsack.** As in A05; $n$ items $(w_i, v_i)$, capacity $W$; maximise value.

**Metric TSP / general TSP.** Complete graph with distances $d(u,v)$; find a Hamiltonian cycle (visits every vertex once) of minimum total length. Metric: $d$ satisfies the triangle inequality.

## Results

### Load balancing (KT 11.1)

**Two lower bounds.** $T^* \ge \max_j t_j$ (the longest job sits somewhere) and $T^* \ge \frac{1}{m}\sum_j t_j$ (total work spread over $m$ machines; the max is at least the average).

**Greedy (list scheduling).** Assign each job in the given order to the currently least-loaded machine. $O(n \log m)$.

**Theorem.** Greedy is a $2$-approximation. *Proof.* Let machine $i$ attain the makespan $T_i$ and let $j$ be the last job assigned to it. When $j$ was assigned, $i$ was least loaded, so $T_i - t_j \le \frac{1}{m}\sum_{k} T_k = \frac{1}{m}\sum_k t_k \le T^*$ (the load before $j$ is at most the average load at that time, which is at most the final average). And $t_j \le T^*$. So $T_i \le 2 T^*$. $\square$ Tight up to $1/m$: $m(m-1)$ unit jobs then one job of length $m$: greedy $2m - 1$, optimum $m$.

**LPT (longest processing time first).** Sort $t_1 \ge \cdots \ge t_n$, then greedy. **Theorem.** LPT is a $3/2$-approximation. *Proof.* If $n \le m$, LPT is optimal (one job per machine). Else $T^* \ge 2 t_{m+1}$: some machine gets two of the $m + 1$ largest jobs, each $\ge t_{m+1}$. Let $i$ be the makespan machine and $j$ its last job. If $i$ holds only one job, $T_i = t_j \le T^*$. Otherwise $j$ is not among the first $m$ jobs (those go to $m$ distinct empty machines), so $j \ge m + 1$ and $t_j \le t_{m+1} \le T^*/2$; then $T_i = (T_i - t_j) + t_j \le T^* + T^*/2$. $\square$ Graham's tighter analysis gives $4/3 - 1/(3m)$, and load balancing has a PTAS (enumerate assignments of the big jobs).

### Center selection (KT 11.2, mention)

Choose $k$ centers minimising the maximum distance of any site to its nearest center. Greedy "farthest-first": repeatedly add the site farthest from the current centers. $2$-approximation: if the greedy radius exceeds $2r^*$, the $k+1$ chosen points (the $k$ centers plus the farthest site) are pairwise $> 2r^*$ apart, so no optimal center (radius $r^*$) can serve two of them; pigeonhole contradiction. Better than 2 is NP-hard (reduction from dominating set).

### Set cover: greedy $H(d)$ (KT 11.3)

**Algorithm.** While uncovered elements remain, pick the set $S_i$ minimising the *price per new element* $w_i / |S_i \cap R|$ ($R$ = uncovered); charge each newly covered element $s$ the price $c_s = w_i/|S_i \cap R|$. Total greedy weight $= \sum_{s \in U} c_s$.

**Lemma.** For every set $S_k$ (in particular every set of the optimum): $\sum_{s \in S_k} c_s \le H(|S_k|)\, w_k$, where $H(d) = 1 + \frac12 + \cdots + \frac1d \approx \ln d$.

*Proof.* Order the elements of $S_k$ by the time greedy covered them, $s_1, \ldots, s_d$. When $s_j$ was covered, at least $d - j + 1$ elements of $S_k$ were still uncovered, so $S_k$ itself offered price $\le w_k / (d - j + 1)$, and greedy chose a price no larger: $c_{s_j} \le w_k/(d - j + 1)$. Sum over $j$: $w_k(\frac1d + \cdots + 1) = H(d) w_k$. $\square$

**Theorem.** Greedy weight $\le H(d) \cdot \mathrm{OPT}$. *Proof.* $\sum_{s \in U} c_s \le \sum_{S_k \in \mathrm{OPT}} \sum_{s \in S_k} c_s \le \sum_{S_k \in \mathrm{OPT}} H(d) w_k = H(d)\, \mathrm{OPT}$; the first inequality because the optimum covers every element (elements may be counted more than once). $\square$ This is essentially optimal: no $(1 - \epsilon) \ln n$ approximation unless P = NP (Dinur–Steurer 2014, building on Feige).

### Vertex cover: two $2$-approximations

**Via a maximal matching.** Compute any maximal matching $M$ (greedily add edges with both ends free); output $C$ = all $2|M|$ endpoints. *Cover:* an uncovered edge would have both ends free, contradicting maximality. *Ratio:* every vertex cover contains at least one endpoint of each edge of $M$, and these endpoints are distinct, so $\mathrm{OPT} \ge |M| = |C|/2$. $O(m)$. (Unweighted only.)

**Via LP rounding (KT 11.6, weighted).** ILP: $\min \sum_v w_v x_v$ s.t. $x_u + x_v \ge 1$ for every edge, $x_v \in \{0, 1\}$. Relax to $0 \le x_v \le 1$ and solve the LP (polynomial, A08) to get $x^*$ with $\mathrm{LP} = \sum w_v x^*_v \le \mathrm{OPT}$ (the optimum cover is feasible for the LP). Round: $C = \{v : x^*_v \ge 1/2\}$. *Cover:* $x^*_u + x^*_v \ge 1$ forces $\max(x^*_u, x^*_v) \ge 1/2$. *Ratio:* $w(C) = \sum_{v \in C} w_v \le \sum_{v \in C} 2 x^*_v w_v \le 2\,\mathrm{LP} \le 2\,\mathrm{OPT}$. $\square$ The LP has half-integral optimal solutions (all $x^*_v \in \{0, \frac12, 1\}$), and its integrality gap approaches 2 (A08), so this analysis cannot be improved by a better rounding of the same LP. KT 11.4 gives a third $2$-approximation by "pricing" (primal-dual), which uses the LP dual without solving it.

### Knapsack FPTAS (KT 11.8)

**DP over values.** Let $V = \max_i v_i$; the table $\mathrm{OPT}'(i, v)$ = minimum weight to achieve value $\ge v$ using items $1..i$, for $v = 0..nV$; time $O(n^2 V)$, pseudo-polynomial in $V$ instead of $W$.

**Scaling.** Given $\epsilon$, set $b = \epsilon V / n$ and $\hat v_i = \lceil v_i / b \rceil$. Run the value-DP on $\hat v$, whose maximum is $\le n/\epsilon + 1$: time $O(n^2 \cdot n/\epsilon) = O(n^3/\epsilon)$. Output the set $S$ optimal for $\hat v$.

**Theorem.** $\sum_{i \in S} v_i \ge (1 - \epsilon)\, \mathrm{OPT}$. *Proof.* Let $S^*$ be optimal for $v$. Since $b \hat v_i \ge v_i \ge b(\hat v_i - 1)$:
$$\sum_{S} v_i \ge b \sum_S (\hat v_i - 1) \ge b\sum_S \hat v_i - nb \ge b \sum_{S^*} \hat v_i - nb \ge \sum_{S^*} v_i - nb = \mathrm{OPT} - \epsilon V \ge (1 - \epsilon)\,\mathrm{OPT},$$
using optimality of $S$ for $\hat v$ in the third step and $\mathrm{OPT} \ge V$ (the most valuable item alone fits, assuming all $w_i \le W$). $\square$ Polynomial in $n$ and $1/\epsilon$: an FPTAS. Knapsack is thus "the easiest NP-hard problem"; an FPTAS exists precisely because it is only *weakly* NP-hard (hard only with large numbers). Strongly NP-hard problems (bin packing, 3-partition, anything hard with numbers polynomial in $n$) have no FPTAS unless P = NP, since an FPTAS with $\epsilon < 1/\mathrm{poly}$ would solve them exactly in polynomial time.

### Inapproximability

**General TSP has no $\rho$-approximation for any constant (even polynomial) $\rho$, unless P = NP.** *Proof.* Reduce from Hamiltonian cycle (NP-complete, B02). Given $G$ on $n$ vertices, build the complete graph with $d(u,v) = 1$ if $\{u,v\} \in E$, else $d(u, v) = \rho n + 1$. If $G$ has a Hamiltonian cycle, $\mathrm{OPT} = n$; otherwise every tour uses a non-edge, so $\mathrm{OPT} \ge \rho n + 1 + (n-1) > \rho n$. A $\rho$-approximation returns a tour of length $\le \rho n$ in the first case and $> \rho n$ in the second, deciding Hamiltonian cycle in polynomial time. $\square$ The gap $\rho$ is planted by the reduction. Metric TSP is different: $2$-approximation by doubling an MST, $3/2$ by Christofides (odd-degree vertices matched), $3/2 - 10^{-36}$ by Karlin–Klein–Oveis Gharan (2021); APX-hard, so no PTAS.

**PCP theorem (Arora–Safra, Arora–Lund–Motwani–Sudan–Szegedy 1992).** $\mathrm{NP} = \mathrm{PCP}[O(\log n), O(1)]$: every NP language has a polynomial-size proof that a randomised verifier can check by reading only $O(1)$ bits chosen with $O(\log n)$ random bits, accepting valid proofs always and invalid ones with probability $\le 1/2$. Equivalent gap form: there is a constant $\epsilon > 0$ such that it is NP-hard to distinguish satisfiable 3-SAT instances from instances in which no assignment satisfies more than a $(1 - \epsilon)$ fraction of clauses. Hence MAX-3SAT has no PTAS; via gap-preserving reductions, neither do vertex cover, independent set, metric TSP, max cut, etc. (all APX-hard). Håstad sharpened MAX-3SAT to $7/8 + \epsilon$, matching the trivial random-assignment $7/8$.

**Vertex cover hardness.** NP-hard to approximate within $1.3606$ (Dinur–Safra 2005), improved to $\sqrt 2 - \epsilon \approx 1.414$ (Khot–Minzer–Safra 2018, via the 2-to-2 games theorem). Under the **Unique Games Conjecture** (Khot 2002; a strengthened PCP-type assumption about the hardness of approximate constraint satisfaction with bijective constraints), no $(2 - \epsilon)$-approximation exists (Khot–Regev 2008): the trivial 2-approximations above would be optimal. Independent set (the complement) is much worse: no $n^{1 - \epsilon}$ approximation unless P = NP (Håstad, Zuckerman).

**APX-hardness idea.** An *L-reduction* from $A$ to $B$ maps instances $I \mapsto I'$ with $\mathrm{OPT}_B(I') \le \alpha\, \mathrm{OPT}_A(I)$ and maps back solutions with $|c_A(S) - \mathrm{OPT}_A| \le \beta |c_B(S') - \mathrm{OPT}_B|$; then a PTAS for $B$ gives a PTAS for $A$. MAX-3SAT is APX-hard by PCP; L-reductions spread the hardness. Proving "no PTAS" therefore amounts to an L-reduction from an APX-hard problem.

## Worked example

**Load balancing**, $m = 3$, jobs $2, 3, 4, 6, 2, 2$.

Greedy in given order: loads after each job: (2,0,0), (2,3,0), (2,3,4), (8,3,4), (8,5,4), (8,5,6): makespan 8. Lower bounds: $\max t_j = 6$, $\lceil 19/3 \rceil = 7$; so $T^* \ge 7$. LPT order $6, 4, 3, 2, 2, 2$: (6,0,0), (6,4,0), (6,4,3), then the least loaded machine is the third → (6,4,5), then the second → (6,6,5), then the third → (6,6,7): makespan 7 = optimal. Ratio bound check: greedy $8 \le 2 \cdot 7$.

**Set cover** with unit weights: $U = \{1..6\}$, $S_1 = \{1,2,3\}$, $S_2 = \{4,5,6\}$, $S_3 = \{1,4\}$, $S_4 = \{2,5\}$, $S_5 = \{3,6\}$, plus $S_6 = \{1,2,3,4\}$. Greedy: prices $S_6$: $1/4$ (best); take $S_6$, $R = \{5,6\}$. Then $S_2$ covers 2 at price $1/2$; take. Greedy cost 2 = optimal here. Classic bad instance: $U$ of size $2^{k+1} - 2$ split into blocks of sizes $2, 4, \ldots, 2^k$ as sets $S_1..S_k$, plus two sets each taking half of every block; optimum 2, greedy takes $S_k, S_{k-1}, \ldots$: $k = \Theta(\log n)$. So $H(d)$ is tight up to constants.

**Vertex cover on a path** $1$–$2$–$3$–$4$–$5$. Maximal matching $\{12, 34\}$: cover $\{1,2,3,4\}$, size 4; optimum $\{2, 4\}$, size 2: ratio exactly 2. LP: $x = (0, 1, 0, 1, 0)$ is feasible with value 2 and is optimal, rounding gives the optimum. On a triangle: LP optimum $x = (\frac12, \frac12, \frac12)$, value $3/2$; rounding gives all three vertices (3) though $\mathrm{OPT} = 2$: the analysis $3 \le 2 \cdot \frac32$ is tight at the LP but loose at the OPT.

**Knapsack FPTAS**, $\epsilon = 0.5$, $n = 3$, $W = 10$: items $(w, v)$: $(5, 60), (4, 43), (6, 58)$. $V = 60$, $b = 0.5 \cdot 60 / 3 = 10$; $\hat v = (6, 5, 6)$. Best feasible under $\hat v$: $\{1, 2\}$ weight 9, $\hat v = 11$; $\{1,3\}$ weight 11 infeasible; $\{2,3\}$ weight 10, $\hat v = 11$: tie; either gives true value 103 or 101. $\mathrm{OPT} = 103$ ($\{1,2\}$). Guarantee $(1 - 0.5) \cdot 103 = 51.5$; both candidates far exceed it.

## Pitfalls

- A ratio is a *worst-case* guarantee over all inputs, not a typical performance; and $\rho$-approximation for a minimisation problem means $\le \rho\,\mathrm{OPT}$, never $\ge$.
- The lower bound on $\mathrm{OPT}$ is the heart of every proof; comparing the algorithm to the *actual* optimum is impossible since it is unknown. Say what you lower-bound OPT by (average load, matching size, LP value, etc.).
- The FPTAS scales *values*, not weights; scaling weights would make infeasible sets look feasible. And the DP must be the value-indexed one.
- PTAS $\ne$ FPTAS: $n^{O(1/\epsilon)}$ is a PTAS but not fully polynomial. An FPTAS for a strongly NP-hard problem would imply P = NP.
- "NP-hard to approximate within $\rho$" is a statement *under P $\ne$ NP*; UGC-based results are conditional on a stronger, unproven conjecture.
- The TSP inapproximability is for *general* TSP; the metric case is APX-complete but approximable within 1.5.
- Tightness examples show that the *analysis* is tight; they do not show that a better algorithm is impossible (that needs a hardness result).

## Exam-style questions

1. **Prove that greedy list scheduling is a 2-approximation for makespan.** Two lower bounds $T^* \ge t_{\max}$, $T^* \ge \frac1m \sum t_j$. For the busiest machine $i$ and its last job $j$: $T_i - t_j \le$ average load $\le T^*$, so $T_i \le T^* + t_j \le 2T^*$.

2. **Give a 2-approximation for vertex cover and prove the ratio. Why does the argument not give $1.99$?** Endpoints of a maximal matching $M$; $|C| = 2|M|$ and $\mathrm{OPT} \ge |M|$. The lower bound $|M|$ can be off by a factor 2 (perfect matching in a complete graph $K_{2k}$: $|M| = k$, $\mathrm{OPT} = 2k - 1$), so no analysis based on it beats 2; and under UGC no polynomial algorithm does.

3. **Explain why the $O(nW)$ knapsack DP does not directly give an FPTAS, and what the FPTAS does instead.** $O(nW)$ is exponential in the bit length of $W$ and is exact; scaling $W$ would break feasibility. The FPTAS uses the DP indexed by (rounded) *values*, whose range $n/\epsilon$ is polynomial, and loses at most $nb = \epsilon V \le \epsilon\,\mathrm{OPT}$ in value.

4. **Show that a polynomial-time $1000$-approximation for TSP with arbitrary distances would imply P = NP.** Hamiltonian cycle reduction with non-edge distance $1000n + 1$: yes-instances have $\mathrm{OPT} = n$, no-instances $> 1000 n$; the approximation's output length distinguishes them.

5. **State the PCP theorem and explain in two sentences how it yields APX-hardness of MAX-3SAT.** $\mathrm{NP} = \mathrm{PCP}[O(\log n), O(1)]$. Encode the verifier's $O(1)$-bit local checks as 3-CNF clauses over the proof bits; a correct proof satisfies all clauses, while for a no-instance every proof is rejected on half the random strings, so a constant fraction of clauses is violated by every assignment. Distinguishing "all satisfiable" from "$\le 1 - \epsilon$ satisfiable" is thus NP-hard, ruling out a PTAS.

## Code

`src/py/algorithmics/approx.py`: `vertex_cover_2approx(adj)` (maximal matching; tests compare to brute-force optimum on small graphs), `load_balancing_greedy(times, m, lpt=False)`, `set_cover_greedy(universe, sets, weights)`, `knapsack_fptas(weights, values, W, eps)` (checked against `dp.knapsack_01`). LP rounding for vertex cover is in `lp_ilp.py` (A08).
