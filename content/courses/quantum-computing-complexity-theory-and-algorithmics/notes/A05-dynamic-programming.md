# A05 Dynamic programming: weighted intervals, knapsack, shortest paths, alignment

Dynamic programming (DP) solves a problem by solving a carefully chosen family of *subproblems* whose answers determine each other by a recurrence, and by storing each answer once so that overlapping subproblems are not recomputed. Where divide and conquer splits into a few independent parts, DP typically has polynomially many subproblems that overlap heavily; the recurrence is the entire algorithm, and correctness is the correctness of the recurrence. This note builds the pattern on weighted interval scheduling, then covers subset sum / knapsack (and what "pseudo-polynomial" means), the two classical shortest-path DPs Bellman–Ford and Floyd–Warshall, and sequence alignment (edit distance, LCS) with Hirschberg's space trick. Reference: KT chapter 6 (6.1 to 6.4 weighted intervals, segmented least squares, knapsack; 6.6 to 6.7 alignment; 6.8 to 6.10 Bellman–Ford and negative cycles); Floyd–Warshall is CLRS 25.2. References: Kleinberg & Tardos ch. 6 [S25]. Exam 1 material.

## Definitions

**Optimal substructure.** An optimal solution to the problem contains optimal solutions to its subproblems (so an optimum can be built from optima of smaller instances). This is what makes a recurrence over optimal *values* valid.

**Overlapping subproblems.** The naive recursion revisits the same subproblem many times; the number of *distinct* subproblems is small (polynomial).

**Memoisation vs bottom-up.** *Memoisation*: write the recursion, cache results in a table keyed by the subproblem, return the cached value on a repeat call. *Bottom-up (tabulation)*: order the subproblems so that each depends only on earlier ones, and fill the table in that order with loops. Same asymptotic time; bottom-up avoids recursion overhead and makes the space profile explicit. Both need an order in which every subproblem's dependencies are available: for 1D problems increasing index; for 2D tables row by row; for Bellman–Ford increasing number of edges.

**Weighted interval scheduling.** Intervals $1..n$ with $(s_j, f_j)$ and weight $v_j > 0$, sorted by finish $f_1 \le \cdots \le f_n$. $p(j)$ = the largest index $i < j$ with $f_i \le s_j$ (the last interval compatible with $j$), or 0. Goal: maximum-weight compatible subset.

**Subset sum / knapsack.** $n$ items with weights $w_i \in \mathbb{N}$ (and values $v_i$), capacity $W \in \mathbb{N}$. Subset sum: a subset of total weight $\le W$ maximising the weight (or deciding whether exactly $W$ is reachable). 0/1 knapsack: subset with $\sum w_i \le W$ maximising $\sum v_i$; "0/1" because each item is taken at most once.

**Pseudo-polynomial.** Running time polynomial in the *numeric value* of input numbers (like $W$) but not in their bit length ($\log W$).

**Shortest paths with negative edges.** Directed graph, lengths $\ell(u,v) \in \mathbb{R}$. A *negative cycle* is a cycle with total length $< 0$; if one is reachable, shortest paths are undefined (walk around it). Otherwise every shortest path can be taken simple, hence has $\le n - 1$ edges.

**Sequence alignment.** Strings $X = x_1..x_m$, $Y = y_1..y_n$. An alignment is a set of matched pairs $(i, j)$, no index used twice, no crossings ($(i,j),(i',j')$ with $i < i'$ and $j > j'$). Cost: $\delta$ per unmatched position (gap) plus $\alpha_{x_i y_j}$ per matched pair (mismatch cost, $\alpha_{aa} = 0$). *Edit distance* is the case $\delta = 1$, $\alpha_{pq} = 1$ for $p \ne q$: minimal number of insert/delete/substitute operations. *LCS* (longest common subsequence): maximise the number of matched equal pairs; equivalent to alignment with $\delta = 1$, $\alpha_{pq} = \infty$ for $p \ne q$, since cost $= m + n - 2\,\mathrm{LCS}$.

## Results

### Weighted interval scheduling (KT 6.1)

Let $\mathrm{OPT}(j)$ be the optimum value using only intervals $1..j$. Either interval $j$ is in the optimum (then no interval $p(j)+1..j-1$ is, and the rest is optimal for $1..p(j)$) or it is not (then optimal for $1..j-1$):
$$\mathrm{OPT}(j) = \max\big(v_j + \mathrm{OPT}(p(j)),\ \mathrm{OPT}(j-1)\big),\qquad \mathrm{OPT}(0) = 0.$$
*Why the recurrence is correct (optimal substructure).* If $j \in O$ and $O$'s restriction to $1..p(j)$ were not optimal, replacing it by a better one gives a better $O$. The two cases are exhaustive. Naive recursion is exponential (Fibonacci-like: $p(j) = j - 2$ gives $T(j) = T(j-1) + T(j-2)$). Memoised or bottom-up: $n$ subproblems, $O(1)$ each, plus $O(n \log n)$ to sort and compute $p$ by binary search. Solution recovery: walk back from $j = n$; take $j$ iff $v_j + \mathrm{OPT}(p(j)) \ge \mathrm{OPT}(j-1)$, then jump to $p(j)$, else to $j - 1$. Storing choices costs nothing extra; the table suffices.

*Segmented least squares (KT 6.3).* Points $(x_1,y_1) \ldots (x_n, y_n)$ sorted by $x$; fit a sequence of line segments with cost $= \sum(\text{squared error of each segment}) + C \cdot (\text{number of segments})$. $\mathrm{OPT}(j) = \min_{i \le j} \big(e(i, j) + C + \mathrm{OPT}(i-1)\big)$ with $e(i,j)$ the least-squares error of points $i..j$. $O(n^2)$ subproblem-pairs after $O(n^2)$ precomputation of all $e(i,j)$. Same pattern: the last segment's start is the choice variable.

### Subset sum and 0/1 knapsack (KT 6.4)

Subproblems indexed by *two* parameters: $\mathrm{OPT}(i, w)$ = best value using items $1..i$ with capacity $w$.
$$\mathrm{OPT}(i, w) = \begin{cases} \mathrm{OPT}(i-1, w) & w_i > w \\ \max\big(\mathrm{OPT}(i-1, w),\ v_i + \mathrm{OPT}(i-1, w - w_i)\big) & \text{else}\end{cases},\qquad \mathrm{OPT}(0, w) = 0.$$
Subset sum is the case $v_i = w_i$. Table of $(n+1)(W+1)$ entries, $O(1)$ each: **$O(nW)$ time and space** (space $O(W)$ if only the value is needed, iterating $w$ downward so that row $i-1$ is read before it is overwritten). Recovery by walking back: item $i$ taken iff $\mathrm{OPT}(i,w) \ne \mathrm{OPT}(i-1,w)$.

**Why $O(nW)$ is not polynomial.** The input is $n$ numbers of $b$ bits each plus $W$ with $b$ bits: size $\Theta(nb)$. $W$ can be $2^b$, so $nW = n 2^b$ is exponential in the input size. The algorithm is *pseudo-polynomial*: polynomial in $n$ and the magnitude $W$. If weights are bounded by a polynomial in $n$ ("small numbers") it is polynomial. Knapsack and subset sum are NP-complete (B02), so no algorithm polynomial in $n$ and $\log W$ is expected; the DP is however the basis of the FPTAS in A07 (scale values down so that the table is small).

### Bellman–Ford (KT 6.8)

Single source $s$ (KT does single *destination*; symmetric), no negative cycles. Subproblem: $\mathrm{OPT}(i, v)$ = length of a shortest $s$–$v$ path using **at most $i$ edges**. The last edge is the choice:
$$\mathrm{OPT}(i, v) = \min\Big(\mathrm{OPT}(i-1, v),\ \min_{(u, v) \in E} \mathrm{OPT}(i-1, u) + \ell(u,v)\Big),\quad \mathrm{OPT}(0, s) = 0,\ \mathrm{OPT}(0, v) = \infty.$$
Without negative cycles shortest paths are simple, so $d(s, v) = \mathrm{OPT}(n-1, v)$. Each round $i$ scans all edges: $O(m)$; $n - 1$ rounds: **$O(nm)$**, space $O(n)$ with a single array $d[\cdot]$ updated in place ("relax every edge" $n-1$ times; in-place updates only help, since any value written is the length of some real path and the round-$i$ invariant $d[v] \le \mathrm{OPT}(i,v)$ still holds). Early stop when a round changes nothing.

**Negative cycle detection.** Run a $n$-th round. If any $d[v]$ still decreases, a negative cycle is reachable from $s$: with no negative cycle all values are final after $n-1$ rounds. Conversely, if a negative cycle $C$ is reachable, the values on $C$ never stabilise: summing the would-be-stable inequalities $d[v] \le d[u] + \ell(u,v)$ around $C$ gives $0 \le \ell(C) < 0$. To find the cycle, follow parent pointers back from a vertex updated in round $n$; within $n$ steps a vertex repeats. Detecting a negative cycle anywhere: add a super-source with 0-length edges to all vertices.

Comparison with Dijkstra: $O(nm)$ vs $O(m \log n)$, but arbitrary signs; also distributed (each vertex updates from its neighbours, the basis of distance-vector routing).

### Floyd–Warshall (all pairs)

Number the vertices $1..n$. Subproblem: $D^{(k)}_{ij}$ = shortest $i$–$j$ path whose *intermediate* vertices all lie in $\{1..k\}$. Either vertex $k$ is used (then once, on a no-negative-cycle instance) or not:
$$D^{(k)}_{ij} = \min\big(D^{(k-1)}_{ij},\ D^{(k-1)}_{ik} + D^{(k-1)}_{kj}\big),\qquad D^{(0)}_{ij} = \ell(i, j)\ (\infty \text{ if no edge},\ 0 \text{ on the diagonal}).$$
Three nested loops $k, i, j$: **$O(n^3)$** time, $O(n^2)$ space (in place: the $k$-th row and column do not change in round $k$, since $D_{kk} = 0$). Negative cycle iff some $D_{ii} < 0$ at the end. Compare: $n$ runs of Bellman–Ford cost $O(n^2 m)$, $n$ runs of Dijkstra $O(nm \log n)$ (non-negative only; Johnson's reweighting extends it). For dense graphs Floyd–Warshall is simplest and competitive. Path recovery via a `next[i][j]` matrix updated when the min improves.

### Sequence alignment (KT 6.6, 6.7)

$\mathrm{OPT}(i, j)$ = minimum alignment cost of prefixes $x_1..x_i$ and $y_1..y_j$. The last column of an alignment is one of: $x_i$ matched to $y_j$, $x_i$ against a gap, $y_j$ against a gap (the no-crossing condition rules out $x_i$ matched to some $y_{j'}$ with $j' < j$ while $y_j$ is matched to an earlier $x$):
$$\mathrm{OPT}(i, j) = \min\big(\alpha_{x_i y_j} + \mathrm{OPT}(i-1, j-1),\ \delta + \mathrm{OPT}(i-1, j),\ \delta + \mathrm{OPT}(i, j-1)\big),\quad \mathrm{OPT}(i, 0) = i\delta,\ \mathrm{OPT}(0, j) = j\delta.$$
$O(mn)$ time and space. The table is a grid graph with diagonal edges of cost $\alpha$ and axis edges of cost $\delta$; the alignment cost is the shortest path from $(0,0)$ to $(m,n)$, which is why Dijkstra-style reasoning and the following trick work.

**Hirschberg's $O(m + n)$ space.** The *value* $\mathrm{OPT}(m,n)$ needs only two rows: $O(\min(m,n))$ space. To recover the alignment, note any shortest $(0,0) \to (m,n)$ path passes through some vertex $(m/2, q)$ in the middle column. Compute forward costs $f(m/2, j)$ (from $(0,0)$) and backward costs $g(m/2, j)$ (to $(m,n)$, the same DP run on reversed strings) in $O(mn)$ time and $O(n)$ space; pick $q$ minimising $f + g$; recurse on the two halves $(0,0)\to(m/2, q)$ and $(m/2, q) \to (m, n)$. Time $T(m, n) = O(mn) + T(m/2, q) + T(m/2, n - q) = O(mn)$ (each level halves $m$, total grid area halves each level, geometric sum). Space $O(m + n)$.

**LCS.** $L(i,j) = L(i-1,j-1) + 1$ if $x_i = y_j$, else $\max(L(i-1,j), L(i,j-1))$. **Edit distance** is the alignment recurrence with unit costs.

## Worked example

**Weighted intervals.** Sorted by finish: 1:(0,3) $v=4$; 2:(2,5) $v=3$; 3:(4,7) $v=5$; 4:(1,8) $v=8$; 5:(6,9) $v=3$; 6:(8,10) $v=4$. $p$: $p(1)=0$; $p(2)=0$ (need $f_i \le 2$: none); $p(3)=1$ ($f_1 = 3 \le 4$); $p(4)=0$; $p(5)=2$ ($f_2 = 5 \le 6$, $f_3 = 7 > 6$); $p(6)=4$ ($f_4 = 8 \le 8$).

$\mathrm{OPT}(1) = \max(4 + 0, 0) = 4$; $\mathrm{OPT}(2) = \max(3 + 0, 4) = 4$; $\mathrm{OPT}(3) = \max(5 + \mathrm{OPT}(1), 4) = 9$; $\mathrm{OPT}(4) = \max(8 + 0, 9) = 9$; $\mathrm{OPT}(5) = \max(3 + \mathrm{OPT}(2), 9) = 9$; $\mathrm{OPT}(6) = \max(4 + \mathrm{OPT}(4), 9) = 13$. Recover: 6 taken ($13 > 9$), jump to 4: $8 + 0 = 8 < 9$, not taken, go to 3: $5 + 4 = 9 \ge 4$, taken, jump to 1: taken. Set $\{1, 3, 6\}$, value $4 + 5 + 4 = 13$.

**Knapsack** $W = 6$, items $(w, v)$: 1:(2,3), 2:(3,4), 3:(4,5), 4:(5,6). Table rows $i$, columns $w = 0..6$:

```
i\w   0  1  2  3  4  5  6
 0    0  0  0  0  0  0  0
 1    0  0  3  3  3  3  3
 2    0  0  3  4  4  7  7
 3    0  0  3  4  5  7  8
 4    0  0  3  4  5  7  8
```
Row 3, $w = 6$: $\max(7,\ 5 + \mathrm{OPT}(2, 2) = 8) = 8$. Row 4, $w = 6$: $\max(8,\ 6 + \mathrm{OPT}(3, 1) = 6) = 8$. Optimum 8: items 1 and 3 (weights $2 + 4 = 6$). Greedy by value/weight ratio (1.5, 1.33, 1.25, 1.2) takes items 1, 2 (weight 5, value 7) and stops: not optimal.

**Bellman–Ford** on edges, scanned in this order each round: $s{\to}a\,(4),\ s{\to}b\,(5),\ b{\to}a\,(-3),\ a{\to}c\,(-2),\ c{\to}t\,(4),\ b{\to}t\,(7)$, source $s$, in-place array.

| after round | $s$ | $a$ | $b$ | $c$ | $t$ |
|---|---|---|---|---|---|
| 0 | 0 | $\infty$ | $\infty$ | $\infty$ | $\infty$ |
| 1 | 0 | 2 | 5 | 0 | 4 |
| 2 | 0 | 2 | 5 | 0 | 4 |

Round 1 step by step: $a = 4$; $b = 5$; $b \to a$: $a = \min(4, 5 - 3) = 2$; $a \to c$: $c = 0$; $c \to t$: $t = 4$; $b \to t$: $t = \min(4, 12) = 4$. Round 2 changes nothing, so the algorithm stops: $d(s, t) = 4$ along $s, b, a, c, t$ ($5 - 3 - 2 + 4$). Dijkstra would extract $a$ first with key 4 and settle it wrongly, because the edge $b \to a$ is negative. In-place scanning found everything in one round only because the edge order happened to follow the path; with the reverse order it would take 4 rounds, which is why the bound is $n - 1 = 4$ rounds.

Now add the edge $c \to b\,(0)$: the cycle $b \to a \to c \to b$ has length $-3 - 2 + 0 = -5$. Round 2 then gives $b = 0$, $a = -3$, $c = -5$, $t = -1$; round 5 (the $n$-th round) still decreases values, so a negative cycle is reported; following parents from $b$: $b \leftarrow c \leftarrow a \leftarrow b$ closes it.

**Edit distance** of $X = \texttt{kitten}$, $Y = \texttt{sitting}$, unit costs:

```
      ""  s  i  t  t  i  n  g
  ""   0  1  2  3  4  5  6  7
  k    1  1  2  3  4  5  6  7
  i    2  2  1  2  3  4  5  6
  t    3  3  2  1  2  3  4  5
  t    4  4  3  2  1  2  3  4
  e    5  5  4  3  2  2  3  4
  n    6  6  5  4  3  3  2  3
```
$\mathrm{OPT}(6,7) = 3$: substitute k→s, e→i, insert g. Cell (e, i) at row 5 col 5: $\min(\alpha_{ei} + \mathrm{OPT}(4,4) = 1 + 1,\ 1 + \mathrm{OPT}(4,5) = 3,\ 1 + \mathrm{OPT}(5,4) = 3) = 2$. LCS of the same strings: `ittn`, length 4; check $6 + 7 - 2 \cdot 4 = 5 \ne 3$ because edit distance allows substitutions (cost 1) which LCS-alignment charges 2 for.

## Pitfalls

- DP on the wrong subproblems fails silently: "$\mathrm{OPT}$ of the first $j$ items" is not enough for knapsack; capacity must be part of the state.
- The recurrence must be justified by optimal substructure: *why* does the rest of the optimum restrict to an optimum of the subproblem? For longest *simple* path in a general graph this fails (subpaths of a longest simple path are not longest simple paths), and the problem is NP-hard.
- $O(nW)$ is pseudo-polynomial; saying "knapsack is in P because of the DP" is wrong (B02).
- Bellman–Ford needs $n - 1$ rounds in the worst case (a path whose edges are scanned in reverse order); early termination is an optimisation, not a bound. Also it computes shortest *walks* with $\le i$ edges; those equal shortest paths only without negative cycles.
- Floyd–Warshall loop order: $k$ must be the outer loop. With $k$ innermost the recurrence is not what is computed.
- Alignment gap penalty applies to *each* unmatched character, and the base cases $\mathrm{OPT}(i,0) = i\delta$ are part of the table. Edit distance $\ne m + n - 2\,\mathrm{LCS}$ unless substitutions are forbidden.
- Memoised recursion in Python hits recursion limits around depth $10^3$; bottom-up avoids it.

## Exam-style questions

1. **Give the recurrence for weighted interval scheduling and explain why naive recursion is exponential while memoisation gives $O(n)$ after sorting.** $\mathrm{OPT}(j) = \max(v_j + \mathrm{OPT}(p(j)), \mathrm{OPT}(j-1))$. Naive: call tree can branch twice per level with depth $n$ ($2^{\Omega(n)}$ when $p(j) \approx j - 2$). Memoised: only $n + 1$ distinct subproblems, each computed once in $O(1)$.

2. **Explain why the $O(nW)$ knapsack algorithm does not show knapsack $\in$ P.** Input size is $\Theta(n \log W)$ bits; $W = 2^{\log W}$ is exponential in that. For $n = 10$, $W = 2^{60}$ the table has $10^{19}$ entries.

3. **Modify Bellman–Ford to report a negative cycle.** Run $n$ rounds instead of $n-1$; if round $n$ changes some $d[v]$, follow `parent` from $v$ for $n$ steps; the repeated vertex closes a cycle of negative length (every parent pointer edge is tight or better along the walk).

4. **Write the Floyd–Warshall recurrence and state what the $k$ index means. Why can it be done in place?** $D^{(k)}_{ij} = \min(D^{(k-1)}_{ij}, D^{(k-1)}_{ik} + D^{(k-1)}_{kj})$; $k$ = largest allowed intermediate vertex. In round $k$ the entries $D_{ik}$ and $D_{kj}$ do not change ($D_{ik}^{(k)} = \min(D_{ik}^{(k-1)}, D_{ik}^{(k-1)} + D_{kk}^{(k-1)})$ and $D_{kk} = 0$), so reading them from the partially updated matrix is safe.

5. **How does Hirschberg reduce alignment space to linear while keeping $O(mn)$ time?** Compute the middle-row forward and backward costs with two-row DPs, choose the split point $q$ minimising their sum, recurse on two subproblems of total area half the original. Work per level halves: geometric series, $O(mn)$ total; space is one pair of rows plus the recursion stack, $O(m + n)$.

## Code

`src/py/algorithmics/dp.py`: `weighted_interval_scheduling(intervals)`, `subset_sum(weights, W)`, `knapsack_01(weights, values, W)` (returns value and chosen set), `bellman_ford(n, edges, s)` (raises or reports on a negative cycle), `floyd_warshall(D)`, `sequence_alignment(x, y, delta, alpha)` (with traceback), `lcs(x, y)`. C++ knapsack with the $O(W)$ rolling array: `src/cpp/knapsack.cpp`.
