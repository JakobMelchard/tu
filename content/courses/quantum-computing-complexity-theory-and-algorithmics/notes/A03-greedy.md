# A03 Greedy algorithms: interval scheduling, lateness, minimum spanning trees

A greedy algorithm builds a solution step by step, at each step making the locally best choice by some simple rule and never revising it. Greedy is fast and easy to state; the whole difficulty is proving it optimal, and for most problems it is not. Two proof patterns cover nearly every correct greedy algorithm: *greedy stays ahead* (the greedy partial solution is at least as good as any other partial solution after every step) and the *exchange argument* (any optimal solution can be transformed into the greedy one without getting worse). This note runs both patterns on the classic instances and then does minimum spanning trees, where a single structural fact (the cut property) certifies three different greedy algorithms. Reference: KT chapter 4 (4.1 interval scheduling and partitioning, 4.2 minimising lateness, 4.4 Dijkstra, 4.5 MST, 4.6 union-find, 4.8 Huffman). References: Kleinberg & Tardos ch. 4 [S25]; 192.219 additionally names interval partitioning and priority queues [S5]. Exam 1 material.

## Definitions

**Interval scheduling.** $n$ requests, request $i$ has start $s_i$ and finish $f_i$, occupying $[s_i, f_i)$. Two requests are *compatible* if the intervals are disjoint. Goal: a maximum-size compatible subset.

**Interval partitioning.** Same input; schedule *all* requests on the minimum number of resources (rooms), each resource holding pairwise compatible requests. The *depth* of the instance is the maximum number of intervals containing a common point.

**Scheduling to minimise lateness.** $n$ jobs, job $i$ has processing time $t_i$ and deadline $d_i$; one machine, start at time 0, no idle time is ever useful. A schedule assigns start times $s(i)$ and finish $f(i) = s(i) + t_i$; lateness $\ell_i = \max(0, f(i) - d_i)$; objective: minimise the *maximum* lateness $L = \max_i \ell_i$.

**Spanning tree, MST.** For a connected undirected graph $G = (V, E)$ with costs $c_e$, a spanning tree is a subset $T \subseteq E$ that is a tree on all of $V$ ($|T| = n - 1$, connected, acyclic). A minimum spanning tree minimises $\sum_{e \in T} c_e$. We assume distinct costs for the proofs (break ties by a fixed perturbation; then the MST is unique).

**Cut.** A partition $(S, V \setminus S)$ with $\emptyset \ne S \ne V$. An edge *crosses* the cut if it has exactly one endpoint in $S$.

**Union-find (disjoint set union).** Maintains a partition of $\{1..n\}$ under `find(x)` (canonical representative of $x$'s set) and `union(x, y)` (merge the sets). Trees with parent pointers; *union by rank* attaches the shorter tree under the taller; *path compression* re-points every node on a find path directly to the root.

## Results

### Interval scheduling: earliest finish first (KT 4.1)

Algorithm: sort by $f_i$; scan; accept a request iff it is compatible with the last accepted one. $O(n \log n)$.

**Theorem.** The greedy set $A = \{i_1, \ldots, i_k\}$ is optimal.

*Proof (greedy stays ahead).* Let $O = \{j_1, \ldots, j_m\}$ be any optimal solution, both listed in order of finish time (equivalently start time, since the sets are compatible). Claim: $f(i_r) \le f(j_r)$ for all $r \le k$. Induction: $r = 1$: greedy picks the globally earliest finish. Step: $f(i_{r-1}) \le f(j_{r-1}) \le s(j_r)$, so $j_r$ was compatible with $i_{r-1}$ and available when greedy chose $i_r$; greedy chose the earliest-finishing available request, so $f(i_r) \le f(j_r)$. Now suppose $m > k$. Then $j_{k+1}$ exists and $s(j_{k+1}) \ge f(j_k) \ge f(i_k)$, so $j_{k+1}$ is compatible with all of $A$ and greedy would not have stopped. Contradiction; $k = m$. $\square$

Other natural rules fail: earliest start (one long interval blocks many), shortest interval (a short one straddling two long compatible ones), fewest conflicts (KT figure 4.1 gives a 4-interval counterexample with a chain).

### Interval partitioning (KT 4.1)

**Lower bound.** Any valid partition uses $\ge$ depth many resources, since the $d$ intervals sharing a point must go to different resources.

**Greedy.** Sort by start time; assign each interval to any resource whose last interval finishes by its start, opening a new resource if none is free. Equivalently: label with the smallest label not used by an already-scheduled overlapping interval.

**Theorem.** Greedy uses exactly $d$ = depth resources (hence optimal). *Proof.* When interval $I$ is processed and forced to open resource number $r$, there are $r - 1$ earlier-starting intervals overlapping $I$; they all contain the point $s_I$ (they started earlier and have not finished), and so does $I$: $d \ge r$. So the greedy never uses more than $d$ labels, and by the lower bound at least $d$. $\square$ With a min-heap on finish times: $O(n \log n)$.

### Minimising maximum lateness: earliest deadline first (KT 4.2)

**Algorithm.** Sort by deadline $d_1 \le \cdots \le d_n$; run jobs in that order with no idle time. $O(n \log n)$. Processing time is ignored, which is surprising; "shortest first" and "smallest slack $d_i - t_i$ first" both fail (KT gives 2-job counterexamples: slack picks a long job with a slightly later deadline first).

**Theorem.** EDF minimises maximum lateness.

*Proof (exchange argument).* Facts: (a) There is an optimal schedule without idle time (shifting jobs earlier never increases lateness). (b) An *inversion* is a pair $i, j$ with $d_i < d_j$ but $j$ scheduled before $i$. A schedule with no inversions and no idle time is EDF up to the order of equal-deadline jobs, which does not affect the maximum lateness (the last of a block of equal-deadline jobs finishes at the same time regardless). (c) If a schedule has an inversion it has an *adjacent* one: consecutive jobs $j, i$ with $d_j > d_i$ (in a sequence with an inversion, deadlines are not monotone, so some consecutive pair decreases). (d) Swapping an adjacent inversion does not increase $L$: let $j$ finish at $f$ and $i$ right after at $f' = f + t_i$ before the swap. After the swap $i$ finishes earlier (lateness decreases), and $j$ finishes at $f'$, with lateness $f' - d_j < f' - d_i = $ old lateness of $i$. So the new maximum is at most the old maximum. Other jobs are unaffected. Start from an optimal schedule, apply (a), then swap adjacent inversions; each swap reduces the inversion count by one, so after $\le \binom{n}{2}$ swaps we reach EDF with $L$ no larger. $\square$

### Dijkstra as greedy

Dijkstra (A02) is greedy: it repeatedly commits to the unsettled vertex with the smallest tentative distance. Its proof is "greedy stays ahead": after $k$ extractions the $k$ settled distances are exactly the $k$ smallest true distances.

### Minimum spanning trees (KT 4.5)

**Cut property.** Let $S$ be any cut and $e$ the *minimum-cost* edge crossing it. Then every MST contains $e$.

*Proof (exchange).* Let $T$ be a spanning tree with $e = \{v, w\} \notin T$. $T$ contains a $v$–$w$ path $P$; since $v \in S$, $w \notin S$, $P$ has an edge $e'$ crossing the cut, and $c_{e'} > c_e$ by minimality and distinctness. $T' = T - e' + e$ is a spanning tree: removing $e'$ splits $T$ into two pieces with $v$ and $w$ on different pieces (the only $v$–$w$ path in $T$ was $P$, which used $e'$), and $e$ reconnects them. $c(T') < c(T)$, so $T$ is not minimal. $\square$

**Cycle property.** Let $C$ be any cycle and $f$ the *maximum-cost* edge on $C$. Then $f$ is in no MST. *Proof.* Suppose $f = \{v, w\} \in T$. Delete $f$: $T$ splits into $S \ni v$ and $V \setminus S \ni w$. The cycle $C - f$ is a $v$–$w$ path, so it contains another edge $e$ crossing $(S, V \setminus S)$, with $c_e < c_f$. $T - f + e$ is a cheaper spanning tree. $\square$

**Three algorithms, one proof each.**

- **Kruskal.** Sort edges by cost; add each edge unless it closes a cycle. *Correctness:* when $e = \{v,w\}$ is added, let $S$ be the component of $v$ in the current forest; $w \notin S$; no cheaper edge crosses the cut (any cheaper crossing edge was examined earlier and, since it would have joined two different components at that time, was added, contradicting $w \notin S$). Cut property: $e \in$ MST. Every rejected edge is the maximum on the cycle it closes, so the cycle property justifies rejection. Output is a spanning tree since the graph is connected. *Time:* sorting $O(m \log m) = O(m \log n)$, plus $2m$ finds and $n-1$ unions: $O(m \,\alpha(n))$. Total $O(m \log n)$.
- **Prim.** Start from any root $s$, $S = \{s\}$; repeatedly add the cheapest edge with exactly one endpoint in $S$. *Correctness:* the added edge is the minimum crossing $(S, V \setminus S)$; cut property. *Time:* identical to Dijkstra with key = cost of the cheapest edge to $S$ instead of distance: $O(m \log n)$ with a binary heap, $O(n^2)$ with an array (better for dense graphs).
- **Reverse-Delete.** Sort edges by decreasing cost; delete each edge unless deleting it disconnects the graph. *Correctness:* when $e$ is deleted it lies on a cycle (otherwise removing it disconnects), and it is the maximum edge on that cycle: every heavier edge was considered earlier, and any heavier edge still present was kept because it was a bridge at that time, hence lies on no cycle of the current graph, in particular not on this one. Cycle property. When $e$ is kept it is a bridge of the current graph, hence in every spanning tree of it, and the current graph still contains the MST. Deletion test by BFS: $O(m (n + m))$ naively; not competitive but conceptually clean.

**Uniqueness.** With distinct costs the MST is unique: all three algorithms output edges forced by the cut property, and the resulting tree contains every forced edge.

### Union-find bounds (KT 4.6)

- Naive (array of set names, relabel the smaller set on union): find $O(1)$, any sequence of $k$ unions $O(k \log k)$ total, because each element is relabelled at most $\log_2 n$ times (its set at least doubles each time).
- Trees with union by rank: `find` $O(\log n)$ worst case, since a tree of rank $r$ has $\ge 2^r$ nodes (induction: rank increases only when two rank-$r$ trees merge).
- Plus path compression: $m$ operations on $n$ elements in $O(m\, \alpha(n))$ (Tarjan); $\alpha$ is the inverse Ackermann function, $\alpha(n) \le 4$ for all practical $n$. Amortised, not worst case per operation (A01).

### Huffman coding (KT 4.8, optional)

Given symbol frequencies, build a prefix-free binary code minimising expected length: repeatedly merge the two least frequent symbols into a node with their summed frequency. Greedy with an exchange argument (the two rarest symbols can be assumed to be siblings at maximum depth). $O(n \log n)$ with a heap.

## Worked example

**Interval scheduling.** Intervals (start, finish): A(1,4) B(3,5) C(0,6) D(5,7) E(3,9) F(5,9) G(6,10) H(8,11) I(8,12) J(2,14) K(12,16).

Sorted by finish: A4 B5 C6 D7 E9 F9 G10 H11 I12 J14 K16. Greedy: take A (last finish 4); B starts 3 < 4 skip; C skip; D starts 5 ≥ 4 take (finish 7); E, F, G skip (start < 7); H starts 8 take (finish 11); I skip; J skip; K starts 12 take. Result $\{A, D, H, K\}$, size 4. Depth check for the partitioning version: at time 3.5, A, B, C, E, J overlap: depth $\ge 5$; at 8.5: E, F, G, H, I, J: depth 6. So the same instance needs 6 rooms, and greedy-by-start-time assigns: C→1 (0), A→2 (1), J→3 (2), B→4 (3), E→5 (3), D→2 (A ended at 4; 5 ≥ 4), F→4 (B ended 5), G→1 (C ended 6), H→2 (D ended 7), I→6 (rooms 1..5 busy: G to 10, H to 11, J to 14, F to 9, E to 9), K→1. Six rooms.

**Lateness.** Jobs $(t_i, d_i)$: 1:(3,6), 2:(2,8), 3:(1,9), 4:(4,9), 5:(3,14), 6:(2,15). EDF order 1,2,3,4,5,6 (3 before 4 by tie-break, irrelevant). Finish times 3, 5, 6, 10, 13, 15. Latenesses 0, 0, 0, 1, 0, 0: $L = 1$. Shortest-first order 3,2,6,1,5,4 finishes 1,3,5,8,11,15; job 1 late by 2, job 4 late by 6: $L = 6$.

**Kruskal.** Vertices $a..f$, edges with costs:
```
ab 7  ac 9  af 14  bc 10  bd 15  cd 11  cf 2  de 6  ef 9
```
Sorted: cf2 de6 ab7 ac9 ef9 bc10 cd11 af14 bd15. Take cf (sets {c,f}), de ({d,e}), ab ({a,b}), ac (merge → {a,b,c,f}), ef (merge → all six). bc: cycle, reject; cd, af, bd rejected. MST = {cf, de, ab, ac, ef}, cost $2+6+7+9+9 = 33$. Prim from $a$: ab7, then cheapest leaving {a,b}: ac9; leaving {a,b,c}: cf2; leaving {a,b,c,f}: ef9 (vs cd11, af already inside); leaving {a,b,c,e,f}: de6. Same tree, as it must be (distinct costs except the two 9s, which do not conflict here).

## Pitfalls

- Greedy is only correct when a proof says so. Most problems (knapsack, TSP, vertex cover) have natural greedy rules that fail; A07 shows some that are still useful as approximations.
- "Greedy stays ahead" compares greedy to an *arbitrary* optimal solution index by index; it does not assume the optimum is unique or that the greedy is the only optimum.
- In the lateness proof the swap argument must show the maximum lateness does not *increase*, not that every job improves (job $j$ gets later but stays below the previous max).
- The cut property needs the *unique* minimum crossing edge; with ties, "some MST contains $e$" is the right statement.
- Kruskal must use union-find; checking cycles by BFS gives $O(mn)$.
- Prim and Dijkstra look alike but the key is different: cheapest single edge into the tree (Prim) versus total distance from the source (Dijkstra). A shortest-path tree is generally not an MST and vice versa.
- MSTs do not care about the actual values, only their order: replacing $c_e$ by any monotone transform (e.g. $c_e^2$ for $c_e > 0$) preserves the MST. Shortest paths do not have this property.
- Union-find's $\alpha(n)$ bound is amortised; a single `find` can still cost $O(\log n)$ before compression.

## Exam-style questions

1. **Prove that earliest-finish greedy is optimal for interval scheduling.** See Results: by induction $f(i_r) \le f(j_r)$; if the optimum had one more interval it would be compatible with greedy's last choice, contradicting termination.

2. **Give a counterexample showing "shortest job first" does not minimise maximum lateness.** Jobs 1: $t=1, d=100$; 2: $t=10, d=10$. Shortest first: job 2 finishes at 11, lateness 1. EDF: 2 then 1, finish 10 and 11, latenesses 0 and 0. $L_{\rm SJF} = 1 > 0$.

3. **State the cut property and use it to prove Prim's algorithm correct.** Every step adds the minimum-cost edge crossing $(S, V\setminus S)$ where $S$ is the current tree's vertex set; by the cut property that edge is in the MST; all $n-1$ added edges are in the unique MST, so the output is the MST.

4. **Let $e$ be the maximum-cost edge of a connected graph. Is $e$ always excluded from the MST?** No: if $e$ is a bridge it must be in every spanning tree. The cycle property only excludes an edge that is the maximum on *some cycle*. Example: path $a$–$b$ with cost 100.

5. **Why is Kruskal's running time $O(m \log n)$ rather than $O(m \log m)$? Are these different?** $m \le n^2$ so $\log m \le 2 \log n$; they are the same order. The sort dominates; the union-find work $O(m \alpha(n))$ is lower order.

## Code

`src/py/algorithmics/greedy.py`: `interval_scheduling(intervals)`, `interval_partitioning(intervals)` (returns room labels and depth), `UnionFind` (union by rank, path compression), `kruskal(n, edges)`, `prim(adj, root)`. C++ Kruskal with a hand-written union-find: `src/cpp/kruskal.cpp`. Dijkstra: `graphs.py` and `src/cpp/dijkstra.cpp` (A02).
