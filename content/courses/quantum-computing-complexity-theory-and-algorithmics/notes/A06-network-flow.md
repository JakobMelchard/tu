# A06 Network flow: Ford–Fulkerson, max-flow/min-cut, and applications

A flow network is a directed graph with capacities, a source and a sink; the question is how much can be pushed from source to sink. The answer is governed by a min-max theorem: the maximum flow equals the minimum cut, and the proof is an algorithm (Ford–Fulkerson) that finds both. The value of the topic is less the shipping metaphor than the modelling range: bipartite matching, disjoint paths, scheduling with demands, project selection and sports elimination all reduce to max flow, and each reduction comes with a combinatorial theorem (Hall, König, Menger) that is a corollary of max-flow/min-cut. Reference: KT chapter 7 (7.1 to 7.3 FF and max-flow/min-cut, 7.3 capacity scaling, 7.4 Edmonds–Karp remark, 7.5 matching, 7.6 disjoint paths, 7.7 circulations, 7.11 project selection, 7.12 baseball elimination). References: Kleinberg & Tardos ch. 7 [S25]; both syllabi name the MaxFlow-MinCut theorem and applications [S1, S5]. (The 2024W and 2025W pages printed it as "MaxCut versus MinFlow"; 2026W fixes the typo [S1, S2, S3].) Exam 1 material.

## Definitions

**Flow network.** Directed $G = (V, E)$, capacity $c(e) > 0$ integer (for now), source $s$ (no in-edges) and sink $t$ (no out-edges). $n = |V|$, $m = |E|$, $C = \max_e c(e)$; assume every vertex lies on some $s$–$t$ path and $m \ge n - 1$.

**Flow.** $f : E \to \mathbb{R}_{\ge 0}$ with (i) *capacity*: $0 \le f(e) \le c(e)$; (ii) *conservation*: for $v \ne s, t$, $f^{\rm in}(v) = f^{\rm out}(v)$ where $f^{\rm in}(v) = \sum_{e \text{ into } v} f(e)$. **Value** $v(f) = f^{\rm out}(s)$ ($= f^{\rm in}(t)$ by summing conservation).

**Cut.** $(A, B)$ with $s \in A$, $t \in B = V \setminus A$. **Capacity** $c(A, B) = \sum_{e \text{ out of } A} c(e)$ (edges from $A$ to $B$ only; edges $B \to A$ do not count).

**Residual graph** $G_f$. For each $e = (u, v)$ with $f(e) < c(e)$, a *forward* edge $(u, v)$ of residual capacity $c(e) - f(e)$; for each $e$ with $f(e) > 0$, a *backward* edge $(v, u)$ of residual capacity $f(e)$ (undoing flow). $G_f$ has at most $2m$ edges.

**Augmenting path.** A simple $s$–$t$ path $P$ in $G_f$; its *bottleneck* $b(P)$ is the minimum residual capacity on it. `augment(f, P)`: add $b$ on forward edges, subtract $b$ on backward edges.

**Bipartite matching.** In $G = (L \cup R, E)$ a matching is a set of edges sharing no endpoint; *perfect* if it covers all vertices. $N(S)$ = set of neighbours of $S \subseteq L$.

**Circulation with demands.** Each vertex has demand $d(v)$ ($d(v) > 0$: sink-like, wants net inflow $d(v)$; $d(v) < 0$: supply). A circulation satisfies capacities and $f^{\rm in}(v) - f^{\rm out}(v) = d(v)$ for all $v$. With lower bounds: $\ell(e) \le f(e) \le c(e)$.

## Results

### Augmentation preserves flows (KT 7.1)

`augment` returns a flow with value $v(f) + b(P)$: capacity holds by the choice of $b$; conservation at an internal path vertex $v$ holds in each of the four cases (in-forward/out-forward: both in and out increase by $b$; in-forward/out-backward: in increases by $b$ and a *different* in-edge decreases by $b$; etc.); the value increases since the first path edge leaves $s$ and is forward.

### Ford–Fulkerson (KT 7.1)

```
f = 0
while G_f has an s–t path P: f = augment(f, P)
return f
```

**Integrality.** With integer capacities every intermediate flow is integral (induction: bottlenecks are integers), the value increases by $\ge 1$ per iteration, and $v(f) \le C^* := \sum_{e \text{ out of } s} c(e)$, so at most $C^*$ iterations, each $O(m)$ (BFS/DFS in $G_f$): **$O(m C^*)$**. This is pseudo-polynomial (A05): exponential in the bit length of $C$.

### Max-flow / min-cut (KT 7.2)

**Lemma 1 (flow across a cut).** For any flow $f$ and any cut $(A, B)$: $v(f) = f^{\rm out}(A) - f^{\rm in}(A)$. *Proof.* $v(f) = f^{\rm out}(s) - f^{\rm in}(s) = \sum_{v \in A} (f^{\rm out}(v) - f^{\rm in}(v))$ since the other terms vanish by conservation. In this sum, an edge with both ends in $A$ contributes $+f(e)$ once and $-f(e)$ once; an edge out of $A$ contributes $+f(e)$; into $A$, $-f(e)$. $\square$

**Lemma 2 (weak duality).** $v(f) \le c(A, B)$ for every flow and every cut. *Proof.* $v(f) = f^{\rm out}(A) - f^{\rm in}(A) \le f^{\rm out}(A) \le c(A, B)$. $\square$

**Theorem.** For a flow $f$ the following are equivalent: (1) $f$ is a maximum flow; (2) there is no augmenting path in $G_f$; (3) there is a cut $(A, B)$ with $v(f) = c(A, B)$. Consequently $\max_f v(f) = \min_{(A,B)} c(A,B)$.

*Proof.* (1) $\Rightarrow$ (2): an augmenting path would increase the value. (2) $\Rightarrow$ (3): let $A^*$ = vertices reachable from $s$ in $G_f$; $s \in A^*$, $t \notin A^*$ by (2). Take an edge $e = (u, v)$ with $u \in A^*$, $v \notin A^*$: if $f(e) < c(e)$ there would be a forward residual edge and $v$ would be reachable; so $f(e) = c(e)$. Take $e' = (v, u)$ with $v \notin A^*$, $u \in A^*$: if $f(e') > 0$ there would be a backward residual edge $(u, v)$, making $v$ reachable; so $f(e') = 0$. By Lemma 1, $v(f) = f^{\rm out}(A^*) - f^{\rm in}(A^*) = c(A^*, B^*) - 0$. (3) $\Rightarrow$ (1): by Lemma 2 every flow has value $\le c(A, B) = v(f)$. $\square$

So FF terminates with a maximum flow (integer capacities), and the reachable set in the final residual graph is a minimum cut, found by one BFS. The min cut is the *certificate* of optimality of the flow.

### Why FF can be slow (KT 7.3)

With capacities $C, C, 1, C, C$ on the diamond $s{\to}a, s{\to}b, a{\to}b, a{\to}t, b{\to}t$, DFS may alternate augmenting paths through the middle edge forward and backward, gaining 1 per iteration: $2C$ iterations, exponential in $\log C$. With irrational capacities FF may fail to terminate and may converge to a value strictly below the maximum (Ford–Fulkerson's own example; the augmenting values follow a geometric series based on the golden ratio). Fixes: choose the augmenting path well.

**Capacity scaling (KT 7.3).** Maintain a threshold $\Delta$, initially the largest power of 2 with $\Delta \le C$; in the $\Delta$-phase augment only along paths of bottleneck $\ge \Delta$ (search in $G_f(\Delta)$, the residual graph restricted to edges of capacity $\ge \Delta$); when none remains, halve $\Delta$; stop after the $\Delta = 1$ phase. *Analysis.* (a) $1 + \lfloor \log_2 C \rfloor$ phases. (b) At the end of a $\Delta$-phase, let $A$ = vertices reachable in $G_f(\Delta)$; every edge out of $A$ has residual $< \Delta$ and every edge into $A$ carries flow $< \Delta$, so $v(f) \ge c(A,B) - m\Delta \ge v(f^*) - m\Delta$. (c) In the next phase (threshold $\Delta/2$) each augmentation adds $\ge \Delta/2$, so at most $2m$ augmentations. Total $O(m \log C)$ augmentations of $O(m)$ each: **$O(m^2 \log C)$**, polynomial in the input size.

**Edmonds–Karp.** Always augment along a *shortest* (fewest edges) path in $G_f$, found by BFS. **$O(nm^2)$**, independent of capacities (strongly polynomial). *Proof sketch.* (i) The BFS distance $d_f(s, v)$ in the residual graph is non-decreasing over augmentations: augmenting along a shortest path only adds residual edges that point *backward* along that path (from layer $i+1$ to $i$), which cannot shorten any distance. (ii) Call an edge *critical* on an augmentation if it is the bottleneck; it then disappears from $G_f$. When $(u,v)$ is critical, $d(v) = d(u) + 1$. It can reappear only after flow is pushed on $(v, u)$, at which time $d'(u) = d'(v) + 1 \ge d(v) + 1 = d(u) + 2$. So between consecutive times an edge is critical, $d(u)$ grows by 2; distances are $< n$, so each edge is critical $O(n)$ times; $2m$ residual edges, each augmentation has a critical edge: $O(nm)$ augmentations of $O(m)$. $\square$ Faster algorithms exist (Dinic $O(n^2 m)$, push-relabel $O(n^3)$ or $O(nm \log(n^2/m))$, and recent almost-linear $m^{1+o(1)}$), all beyond scope.

### Bipartite matching (KT 7.5)

Build $G'$: $s \to$ every $\ell \in L$, every $r \in R \to t$, edges $L \to R$ directed, all capacities 1. Integral flows of value $k$ correspond to matchings of size $k$ (each $\ell$ has in-capacity 1, so at most one unit passes through it; likewise $r$). Max flow = maximum matching; FF with $C^* = |L| \le n$ gives **$O(mn)$**. (Hopcroft–Karp: $O(m \sqrt n)$.)

**Hall's theorem.** $G$ with $|L| = |R| = n$ has a perfect matching iff $|N(S)| \ge |S|$ for every $S \subseteq L$. *Proof via cuts.* ($\Rightarrow$) trivial. ($\Leftarrow$) Suppose max flow $< n$; then some cut $(A, B)$ has $c(A, B) < n$. Let $S = L \cap A$. The cut pays 1 for each $\ell \in L \setminus A$ (edge $s \to \ell$), 1 for each $r \in R \cap A$ (edge $r \to t$), and at least $1$ for each $\ell \in S$ with a neighbour in $R \setminus A$; we may assume no such $L$–$R$ edge crosses (moving $r$ into $A$ costs 1 for the edge $r \to t$ but saves $\ge 1$), so $N(S) \subseteq A$. Then $c(A,B) \ge (n - |S|) + |N(S)| < n$ gives $|N(S)| < |S|$. $\square$ The violating $S$ is a Hall certificate; it can be read off the min cut.

**König's theorem.** In a bipartite graph, max matching = min vertex cover. *Proof.* $\le$: each matching edge needs its own cover vertex. $\ge$: from a min cut $(A,B)$ with no $L$–$R$ edge crossing (as above), $(L \setminus A) \cup (R \cap A)$ is a vertex cover (every edge $(\ell, r)$ with $\ell \in A$ has $r \in A$) of size $c(A,B)$ = max flow = max matching. $\square$ Vertex cover is NP-hard in general graphs (B02, A07) but polynomial on bipartite graphs.

### Disjoint paths, Menger (KT 7.6)

Maximum number of edge-disjoint $s$–$t$ paths in a directed graph: unit capacities, max flow; an integral flow decomposes into $v(f)$ edge-disjoint paths (peel off paths from $s$; cycles can be removed). **Menger:** max number of edge-disjoint $s$–$t$ paths = min number of edges whose removal disconnects $t$ from $s$ (a cut of the unit-capacity network). Vertex-disjoint: split each $v$ into $v_{\rm in} \to v_{\rm out}$ with capacity 1. Undirected: replace each edge by two antiparallel arcs (a max flow can be chosen to use at most one of them). FF costs $O(mn)$ since $C^* \le n$.

### Circulations with demands and lower bounds (KT 7.7)

*Demands.* Feasible iff $\sum_v d(v) = 0$ and the max flow in $G'$ (super-source $s^* \to v$ with capacity $-d(v)$ for suppliers, $v \to t^*$ with capacity $d(v)$ for demanders) saturates all source edges, i.e. has value $D = \sum_{d(v) > 0} d(v)$. Cut condition: for every $S$, $c(S, \bar S) \ge \sum_{v \in S} d(v)$.

*Lower bounds.* Send $\ell(e)$ on every edge first; this creates surplus/deficit $L(v) = \ell^{\rm in}(v) - \ell^{\rm out}(v)$. Solve the demand problem with capacities $c(e) - \ell(e)$ and demands $d(v) - L(v)$; add $\ell$ back. Applications: survey design, airline scheduling (KT 7.8, 7.9).

### Project selection via min cut (KT 7.11)

Projects $i$ with profit $p_i \in \mathbb{R}$ and prerequisite edges $i \to j$ ("$i$ requires $j$"); choose a feasible (prerequisite-closed) set $A$ maximising $\sum_{i \in A} p_i$. Network: $s \to i$ with capacity $p_i$ for $p_i > 0$; $i \to t$ with capacity $-p_i$ for $p_i < 0$; prerequisite edges with capacity $\infty$. A cut $(A \cup \{s\}, \bar A \cup \{t\})$ has finite capacity iff $A$ is closed, and then $c = \sum_{i \notin A, p_i > 0} p_i + \sum_{i \in A, p_i < 0} (-p_i) = P - \sum_{i \in A} p_i$ with $P = \sum_{p_i > 0} p_i$ constant. Min cut = max profit. Same trick solves image segmentation (KT 7.10).

### Baseball elimination (KT 7.12, sketch)

Team $z$ with $w_z$ wins and $g_z$ games left is eliminated if no outcome of the remaining games leaves $z$ at least tied for first. Network: source $\to$ node per remaining pair $\{x, y\}$ with capacity $g_{xy}$, pair node $\to$ team nodes $x, y$ ($\infty$), team $x \to t$ with capacity $w_z + g_z - w_x$ (games $x$ may still win without passing $z$; negative means eliminated outright). $z$ survives iff max flow saturates the source (all remaining games can be played without any team exceeding $w_z + g_z$). The min cut gives a *certificate* set $T$ of teams with $\frac{\sum_{x\in T} w_x + g(T)}{|T|} > w_z + g_z$, an averaging argument the fan can verify.

## Worked example

Network: $s{\to}u\,(20),\ s{\to}v\,(10),\ u{\to}v\,(30),\ u{\to}t\,(10),\ v{\to}t\,(20)$.

**Iteration 1.** $G_f = G$. DFS finds $P_1 = s, u, v, t$ with bottleneck $\min(20, 30, 20) = 20$. Flow: $su{=}20, uv{=}20, vt{=}20$, others 0; value 20. Residual: $s{\to}u$ gone (saturated), $u{\to}s$ (20 back); $u{\to}v$ 10 forward, $v{\to}u$ 20 back; $v{\to}t$ gone, $t{\to}v$ 20 back; $s{\to}v$ 10; $u{\to}t$ 10.

**Iteration 2.** Paths from $s$ in $G_f$: $s \to v$ (10), then $v \to u$ (backward, 20), then $u \to t$ (10). $P_2 = s, v, u, t$, bottleneck $\min(10, 20, 10) = 10$. Augment: $sv = 10$; $uv$ decreases $20 \to 10$ (backward edge); $ut = 10$. Flow: $su{=}20, sv{=}10, uv{=}10, ut{=}10, vt{=}20$; value 30. Conservation at $u$: in 20, out $10 + 10$; at $v$: in $10 + 10$, out 20.

**Iteration 3.** Residual from $s$: $s{\to}u$ saturated, $s{\to}v$ saturated; nothing reachable but $s$. Stop. $A^* = \{s\}$, cut capacity $20 + 10 = 30 = v(f)$. Another min cut: $\{s, u, v\}$ with $ut + vt = 30$. Note the use of the backward edge in iteration 2: it rerouted 10 units of $u$'s flow from $v$ to $t$ so that $s{\to}v$ could be used. Edmonds–Karp would have augmented $s,u,t$ (length 2) first: $10$; then $s,v,t$: 10; then $s,u,v,t$: 10; three augmentations, same value.

**Matching / Hall.** $L = \{1,2,3\}$, $R = \{a, b, c\}$, edges $1a, 1b, 2a, 3a$. Max flow: $1{\to}b$, $2{\to}a$; then 3's only neighbour $a$ is used and no augmenting path exists (from $s$: $3 \to a \to 2$ (back) $\to$ nothing new). Value 2 $< 3$. Min cut: $A = \{s, 2, 3, a\}$, capacity $= $ edge $s{\to}1$ (1) $+$ edge $a{\to}t$ (1) $= 2$. Hall violator $S = L \cap A = \{2, 3\}$, $N(S) = \{a\}$, $|N(S)| = 1 < 2$. König cover: $(L \setminus A) \cup (R \cap A) = \{1, a\}$, size 2.

## Pitfalls

- Cut capacity counts only edges from $A$ to $B$; flow *value* subtracts the backward flow (Lemma 1), capacity does not.
- Residual graphs need backward edges; "augmenting path in $G$" without them gives a maximal but not maximum flow (iteration 2 above needs $v \to u$).
- FF's $O(mC^*)$ is not polynomial. Say "polynomial" only for capacity scaling ($O(m^2 \log C)$), Edmonds–Karp ($O(nm^2)$) or better; and the last one is *strongly* polynomial (no dependence on $C$).
- With irrational capacities, plain FF may not terminate; integrality is a theorem about integer inputs, not a property of all flows.
- Max-flow/min-cut equality is the statement; the proof shows more: *any* flow with no augmenting path is maximum, and $A^*$ = reachable set gives a min cut. In an exam, prove the three-way equivalence.
- Bipartite matching reduction: the value of a flow equals the matching size only for *integral* flows; that FF returns one is what makes the reduction work.
- Project selection: prerequisite edges get capacity $\infty$ so that a finite cut is a closed set; forgetting this breaks the correspondence.
- Min cut is not unique; "the" min cut from the algorithm is the source side of the reachable set (the smallest one).

## Exam-style questions

1. **Prove that $v(f) \le c(A, B)$ for every flow $f$ and cut $(A,B)$.** $v(f) = f^{\rm out}(A) - f^{\rm in}(A) \le f^{\rm out}(A) = \sum_{e \text{ out of } A} f(e) \le \sum c(e) = c(A,B)$, using Lemma 1 and $0 \le f \le c$.

2. **Show that if $G_f$ has no $s$–$t$ path then $f$ is maximum, and describe how to output a min cut.** Let $A^*$ be the set reachable from $s$ in $G_f$. Edges out of $A^*$ are saturated (else forward residual edge), edges into $A^*$ carry zero (else backward residual edge). So $v(f) = c(A^*, B^*)$, and by weak duality no flow is larger. Output $A^*$ by BFS in $G_f$.

3. **Why is Ford–Fulkerson with DFS not a polynomial-time algorithm? Name two fixes and their bounds.** Number of augmentations is bounded only by $C^*$, exponential in the number of bits of the capacities; the diamond example with middle edge 1 needs $2C$ iterations. Fixes: capacity scaling, $O(m^2 \log C)$; shortest augmenting paths (Edmonds–Karp), $O(nm^2)$.

4. **Reduce the maximum bipartite matching problem to max flow and prove the correspondence.** Source to $L$, $R$ to sink, all capacities 1. An integral flow has each $\ell$ and $r$ on at most one unit path, so the $L$–$R$ edges with flow 1 form a matching of size $v(f)$; conversely a matching gives a flow. Max flow (integral by FF) = max matching, $O(mn)$.

5. **Explain how to decide feasibility of a circulation with demands $d(v)$ and lower bounds $\ell(e)$.** Push $\ell(e)$ on every edge, update demands by the induced imbalance $L(v)$ and capacities to $c - \ell$; add super-source/sink with capacities $|d'(v)|$; feasible iff max flow equals $\sum_{d' > 0} d'(v)$ (and $\sum d = 0$).

## Code

`src/py/algorithmics/flow.py`: `ford_fulkerson(cap, s, t)` (DFS paths, returns flow dict and value), `edmonds_karp(cap, s, t)` (BFS), `capacity_scaling(cap, s, t)`, `min_cut(cap, flow, s)` (reachable set in $G_f$), `bipartite_matching(L, R, edges)` (with Hall violator on failure), `project_selection(profits, prereqs)`. C++ Edmonds–Karp on an adjacency matrix: `src/cpp/edmonds_karp.cpp`.
