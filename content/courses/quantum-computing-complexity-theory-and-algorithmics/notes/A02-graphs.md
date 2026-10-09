# A02 Graphs: representation, traversal, connectivity, bipartiteness, DAGs, Dijkstra

A graph is the universal abstraction for "things and pairwise relations": vertices and edges. Almost every later topic (MST, shortest paths, flows, matchings, reductions in complexity theory) lives on a graph, and almost every graph algorithm starts with one of two traversals, breadth-first search (BFS) or depth-first search (DFS), both linear in the size of the graph. This note defines graphs and their two standard encodings, derives BFS and DFS with their structural guarantees, and uses them to test connectivity and bipartiteness, to order a directed acyclic graph, and to find strongly connected components. Dijkstra's algorithm is included as a preview of the weighted case (it is the C++ reference implementation). Reference: KT chapter 3 (3.1 to 3.6); Dijkstra in KT 4.4. References: Kleinberg & Tardos ch. 3 [S25]; 192.219 additionally names "data structures for graphs" [S5]. Exam 1 material.

## Definitions

**Graph.** $G = (V, E)$ with vertex set $V$, $|V| = n$, and edge set $E$, $|E| = m$. *Undirected*: edges are unordered pairs $\{u, v\}$. *Directed*: ordered pairs $(u, v)$, drawn $u \to v$. We assume no self-loops and no parallel edges unless said otherwise, so $m \le \binom{n}{2}$ (undirected) or $m \le n(n-1)$ (directed). A graph is *sparse* if $m = O(n)$, *dense* if $m = \Theta(n^2)$.

**Degree.** Undirected: $\deg(v)$ = number of incident edges; $\sum_v \deg(v) = 2m$ (handshake lemma: each edge counted twice). Directed: in-degree and out-degree, $\sum \deg^-(v) = \sum \deg^+(v) = m$.

**Path, cycle.** A path is a sequence $v_0, v_1, \ldots, v_k$ with $\{v_{i-1}, v_i\} \in E$; *simple* if all vertices are distinct; its *length* is $k$ (number of edges). A cycle is a closed path $v_0 = v_k$, $k \ge 3$, otherwise simple. Distance $d(u, v)$ = length of a shortest $u$–$v$ path ($\infty$ if none).

**Connectivity.** Undirected $G$ is *connected* if every pair of vertices is joined by a path. The *connected components* are the equivalence classes of the relation "joined by a path"; they partition $V$. Directed $G$ is *strongly connected* if for every $u, v$ there is a directed path $u \to v$ and $v \to u$; *strongly connected components* (SCCs) are the classes of the mutual-reachability relation.

**Tree.** A connected undirected graph with no cycle. Equivalent characterisations (KT 3.1): connected with $m = n - 1$; acyclic with $m = n - 1$; a unique simple path between every pair. A *rooted* tree fixes a root; parent/child/ancestor/descendant follow.

**Bipartite graph.** $V$ can be split into $L \cup R$ (a 2-colouring) such that every edge has one end in $L$ and one in $R$.

**DAG and topological order.** A directed graph with no directed cycle. A topological ordering is a labelling $v_1, \ldots, v_n$ such that every edge $(v_i, v_j)$ has $i < j$. A *source* has in-degree 0, a *sink* out-degree 0.

**Representations.**
- *Adjacency matrix* $A \in \{0,1\}^{n \times n}$, $A_{uv} = 1$ iff $(u, v) \in E$. Space $\Theta(n^2)$; edge test $O(1)$; listing neighbours of $v$ costs $\Theta(n)$ even if $\deg v = 1$.
- *Adjacency list*: array of $n$ lists, list $v$ holds the neighbours of $v$. Space $\Theta(n + m)$; edge test $O(\deg u)$; listing neighbours $O(\deg v)$; total over all vertices $O(n + m)$. This is the right structure for traversal, so "linear time" for graphs means $O(n + m)$.

## Results

### BFS (KT 3.2, 3.3)

From a start $s$, explore in layers: $L_0 = \{s\}$, $L_{i+1}$ = all vertices adjacent to $L_i$ not yet discovered. Implementation with a FIFO queue:

```
BFS(s): dist[s]=0, parent[s]=nil, queue=[s]
  while queue nonempty: u = pop_front
    for v in adj[u]: if dist[v] undefined: dist[v]=dist[u]+1, parent[v]=u, push_back(v)
```

**Theorem (layers = distances).** After BFS, $L_i = \{v : d(s, v) = i\}$. *Proof.* Induction on $i$. $L_0 = \{s\}$. Suppose $L_j$ is the distance-$j$ set for $j \le i$. If $v \in L_{i+1}$ it has a neighbour in $L_i$, hence $d(s, v) \le i+1$; it is not in $L_j$, $j \le i$, hence $d(s,v) \ge i+1$. Conversely if $d(s,v) = i+1$, take the predecessor $u$ on a shortest path: $d(s,u) = i$, so $u \in L_i$, $v$ is adjacent to $u$ and not in earlier layers, so $v$ is placed in $L_{i+1}$. $\square$

**Corollary.** Following `parent` pointers from $v$ gives a shortest $s$–$v$ path; the parent pointers form the *BFS tree*. In an undirected graph, every non-tree edge $\{x, y\}$ joins vertices in the same or adjacent layers, $|{\rm layer}(x) - {\rm layer}(y)| \le 1$ (if the layers differed by 2, $y$ would have been discovered from $x$ one layer earlier). 

**Running time.** Each vertex enters the queue at most once; each adjacency list is scanned once: $O(n + m)$ with adjacency lists, $O(n^2)$ with a matrix.

### DFS (KT 3.2, 3.6)

Explore one branch as deep as possible before backtracking; recursion (or an explicit stack). Record *discovery time* $d[v]$ when the call starts and *finish time* $f[v]$ when it returns, from a global counter.

```
DFS(u): colour[u]=grey, d[u]=t++
  for v in adj[u]: if colour[v]=white: parent[v]=u, DFS(v)
  colour[u]=black, f[u]=t++
main: for all u white: DFS(u)
```

**Parenthesis theorem.** For any $u, v$ the intervals $[d[u], f[u]]$ and $[d[v], f[v]]$ are either disjoint or nested; nested with $u$'s interval containing $v$'s iff $v$ is a descendant of $u$ in the DFS forest. *Proof.* When $v$ is discovered while $u$ is grey, the call DFS($v$) is inside DFS($u$) and returns before it; if $v$ is discovered after $u$ finishes, disjoint. $\square$

**Edge classification** for directed graphs, when DFS examines edge $(u, v)$:
- $v$ white: *tree edge*.
- $v$ grey: *back edge* ($v$ is an ancestor on the current path). Existence of a back edge $\iff$ directed cycle.
- $v$ black and $d[u] < d[v]$: *forward edge* (to a descendant already finished).
- $v$ black and $d[u] > d[v]$: *cross edge* (to a finished vertex in another subtree / earlier tree).

In undirected graphs only tree and back edges occur (KT 3.2, property 3.7): if $\{u, v\}$ is a non-tree edge then one endpoint is an ancestor of the other, because when the earlier-discovered one, say $u$, scanned its list, $v$ was either white (then $v$ becomes a child, contradiction) or discovered inside $u$'s call.

**Running time** $O(n + m)$: each vertex is called once, each list scanned once.

### Connectivity (KT 3.2)

Repeatedly run BFS (or DFS) from any undiscovered vertex; each run finds exactly the component of its start (it discovers exactly the vertices reachable from $s$: everything reachable is reached by the layer argument, nothing else is ever touched). Total $O(n + m)$. Number of components = number of runs.

### Bipartiteness (KT 3.4)

**Theorem.** An undirected graph is bipartite iff it has no odd cycle. Equivalently: BFS colouring by layer parity succeeds iff no edge joins two vertices in the same layer.

*Proof.* ($\Rightarrow$) In a bipartite graph the colours along any cycle alternate, so returning to the start takes an even number of steps. ($\Leftarrow$, constructive) Run BFS from $s$ in each component; colour layer $L_i$ red if $i$ even, blue if $i$ odd. Every edge joins layers differing by at most 1. If every edge joins layers differing by exactly 1 the colouring is proper and $G$ is bipartite. Otherwise some edge $\{x, y\}$ has $x, y \in L_j$. Let $z$ be the lowest common ancestor of $x$ and $y$ in the BFS tree, at layer $i < j$. The tree path $z \to x$ has length $j - i$, the tree path $y \to z$ has length $j - i$, plus the edge $\{x, y\}$: a cycle of length $2(j - i) + 1$, odd. $\square$

So one BFS per component, $O(n + m)$, either 2-colours the graph or exhibits an odd cycle as a certificate.

### DAGs and topological ordering (KT 3.6)

**Lemma.** Every DAG has a source (in-degree 0). *Proof.* Walk backwards along in-edges from any vertex; after $n$ steps some vertex repeats, giving a directed cycle, unless a vertex with no in-edge stops the walk. $\square$ Symmetrically, every DAG has a sink.

**Theorem.** $G$ has a topological ordering iff $G$ is a DAG. ($\Rightarrow$: a cycle would need $i < j < \cdots < i$.) ($\Leftarrow$, Kahn's algorithm): pick a source $v$, output it, delete it (the remainder is still a DAG, as deleting cannot create cycles), repeat. Every edge $(v, w)$ has $v$ output before $w$ because $w$ is not a source until $v$ is gone.

*Implementation.* Keep in-degree counts and a queue of current sources; deleting $v$ decrements in-degrees of its out-neighbours and pushes those that hit 0. $O(n + m)$. If the queue empties before all $n$ vertices are output, the remaining vertices contain a cycle (all have in-degree $\ge 1$ within the remainder).

*DFS variant.* Run DFS on $G$; sort vertices by **decreasing finish time**. *Correctness.* For an edge $(u, v)$ in a DAG, when DFS examines it, $v$ is not grey (that would be a back edge = cycle). If $v$ is white, DFS($v$) runs inside DFS($u$), so $f[v] < f[u]$. If $v$ is black, $f[v]$ is already set and $f[u]$ comes later. Either way $f[u] > f[v]$. $\square$

### Strongly connected components (Kosaraju)

The SCCs of a directed graph, contracted to single vertices, form a DAG (the *condensation*): a cycle among SCCs would merge them.

**Kosaraju's algorithm.** (1) DFS on $G$, record finish times. (2) Let $G^{R}$ be $G$ with all edges reversed. (3) DFS on $G^R$, starting new trees in decreasing order of finish time from step 1. Each tree of step 3 is exactly one SCC. $O(n + m)$.

*Why.* The vertex $u$ with the largest finish time lies in a source SCC $C$ of the condensation (the SCC that finished last has no edge entering from an unfinished SCC; a standard lemma: for an edge $(C, C')$ between SCCs, $\max f(C) > \max f(C')$). In $G^R$, $C$ is a *sink* SCC, so DFS from $u$ reaches precisely $C$ (it cannot leave a sink). Delete $C$ and repeat the argument. Tarjan's single-pass algorithm gives the same result with one DFS and a stack; either is "the linear-time SCC algorithm".

### Dijkstra (KT 4.4), the weighted preview

Input: directed graph with edge lengths $\ell(e) \ge 0$, start $s$. Output: $d(s, v)$ for all $v$.

```
dist[s]=0, dist[v]=inf otherwise, S=∅ (settled), Q = priority queue on dist
while Q nonempty: u = extract-min(Q); add u to S
  for (u,v) in adj[u]: if dist[u]+l(u,v) < dist[v]: dist[v]=dist[u]+l(u,v), parent[v]=u, decrease-key(v)
```

**Invariant.** For every $u \in S$, $\mathrm{dist}[u] = d(s, u)$. *Proof by induction on $|S|$.* Let $v$ be the vertex extracted next, with tentative value $\mathrm{dist}[v] = \min_{u \in S, (u,v) \in E} d(s, u) + \ell(u, v)$, i.e. the length of the shortest path that uses only $S$-vertices before its last edge. Suppose a shorter $s$–$v$ path $P$ exists. $P$ starts in $S$ and ends at $v \notin S$, so it has a first edge $(x, y)$ leaving $S$. Its length is at least $d(s, x) + \ell(x, y) \ge \mathrm{dist}[y] \ge \mathrm{dist}[v]$, the last inequality because $v$ has minimum key. Contradiction; the step $\ell \ge 0$ was used in "the rest of $P$ after $y$ has non-negative length". $\square$

**Running time.** $n$ extract-mins and $\le m$ decrease-keys. Binary heap: $O((n + m) \log n)$. Fibonacci heap: $O(m + n \log n)$. Array scan (dense graphs): $O(n^2)$. With unit lengths Dijkstra degenerates to BFS. Negative edges break the invariant (see A05, Bellman–Ford). Dijkstra is also the first *greedy* algorithm (A03): it commits to the closest unsettled vertex and never revisits.

## Worked example

Undirected graph, $n = 8$, adjacency lists:

```
1: 2 3        2: 1 4 5      3: 1 5        4: 2 6
5: 2 3 6      6: 4 5 7 8    7: 6          8: 6
```

**BFS from 1.** $L_0 = \{1\}$, $L_1 = \{2, 3\}$, $L_2 = \{4, 5\}$ (from 2: 4, 5; from 3: 5 already), $L_3 = \{6\}$, $L_4 = \{7, 8\}$. Tree edges: 1–2, 1–3, 2–4, 2–5, 4–6, 6–7, 6–8. Non-tree edges: 3–5 (layers 1 and 2), 5–6 (layers 2 and 3). Shortest path $1 \to 8$: parent chain $8 \leftarrow 6 \leftarrow 4 \leftarrow 2 \leftarrow 1$, length 4.

**Bipartiteness.** Colour even layers red $\{1, 4, 5, 7, 8\}$ and odd layers blue $\{2, 3, 6\}$. Check edges within a layer: 3–5 is layers 1–2, fine; 5–6 is 2–3, fine; no same-layer edge, so the graph is bipartite with $L = \{1,4,5,7,8\}$, $R = \{2,3,6\}$. Sanity: the cycle 1–2–5–3–1 has length 4 (even); 2–4–6–5–2 has length 4.

Now add edge 4–5. Both in $L_2$: odd cycle. LCA of 4 and 5 in the BFS tree is 2 (layer 1): cycle 2–4–5–2 of length $2(2-1)+1 = 3$. Not bipartite.

**DFS on a directed graph** with edges $a{\to}b,\ a{\to}c,\ b{\to}d,\ c{\to}d,\ d{\to}b,\ c{\to}e$, lists in alphabetical order. DFS($a$): $d[a]=1$; DFS($b$): $d[b]=2$; DFS($d$): $d[d]=3$; edge $d \to b$, $b$ grey: back edge, cycle $b \to d \to b$. $f[d]=4$, $f[b]=5$. Back in $a$: DFS($c$): $d[c]=6$; edge $c \to d$, $d$ black with $d[c] = 6 > d[d] = 3$: cross edge; DFS($e$): $d[e] = 7$, $f[e]=8$; $f[c]=9$; $f[a]=10$. Not a DAG. SCCs: $\{a\}, \{b, d\}, \{c\}, \{e\}$; condensation order $a \to \{b,d\}$, $a \to c \to \{b,d\}$, $c \to e$.

**Topological order** after deleting $d \to b$: sources $\{a\}$; remove $a$: in-degrees $b{:}0, c{:}0$; remove $b$: $d{:}1$; remove $c$: $d{:}0$, $e{:}0$; then $d$, $e$. Order $a, b, c, d, e$. DFS finish-time order (decreasing, redo DFS without $d \to b$): $f[d] = 4, f[b] = 5, f[e] = 8, f[c] = 9, f[a] = 10$, giving $a, c, e, b, d$: also valid (check $c \to d$: $c$ before $d$; $b \to d$: fine).

**Dijkstra** on directed weighted edges $s{\to}a\,(4),\ s{\to}b\,(1),\ b{\to}a\,(2),\ a{\to}t\,(1),\ b{\to}t\,(5)$. Init dist $s{=}0$, rest $\infty$. Extract $s$: $a{=}4, b{=}1$. Extract $b$ (1): $a = \min(4, 1+2) = 3$, $t = 6$. Extract $a$ (3): $t = \min(6, 3+1) = 4$. Extract $t$ (4). Result $d(s,t) = 4$ via $s,b,a,t$. Note $a$'s value improved after being touched once; it was not yet in $S$, so no invariant was violated.

## Pitfalls

- "Linear time" for graphs is $O(n + m)$, not $O(n)$; a matrix representation forces $\Omega(n^2)$ regardless of $m$.
- BFS gives shortest paths only for unit (unweighted) edges. For weights use Dijkstra ($\ell \ge 0$) or Bellman–Ford (any $\ell$, no negative cycle).
- DFS discovery order is *not* a topological order; use *reverse finish* order. And the DFS forest depends on adjacency-list order; finish times do too, but the resulting ordering is always valid.
- An undirected graph can have no forward or cross edges; claiming one in an exam classification is an error.
- A tree has $m = n - 1$, but $m = n - 1$ alone does not make a graph a tree (it could be disconnected with a cycle).
- Bipartite $\ne$ "two-colourable with two given sides"; the certificate for *non*-bipartiteness is an odd cycle, and the BFS proof constructs it via the LCA.
- Kahn's algorithm silently produces a partial order if there is a cycle; check that all $n$ vertices were output.
- Dijkstra's proof uses $\ell \ge 0$ exactly once; with a negative edge the "first edge leaving $S$" argument collapses (path could get shorter after leaving $S$).
- Strong connectivity is not connectivity of the underlying undirected graph ("weakly connected").

## Exam-style questions

1. **Prove that in a BFS tree of an undirected graph every non-tree edge joins vertices whose layers differ by at most 1.** Let $\{x, y\}$ be an edge with $x \in L_i$ discovered first. When $x$ was processed, $y$ was either undiscovered (then $y$ goes to $L_{i+1}$) or already in $L_j$ with $j \le i + 1$ (all vertices in the queue at that time are in $L_i \cup L_{i+1}$). So $|i - j| \le 1$.

2. **Give an $O(n+m)$ algorithm to decide whether an undirected graph contains a cycle, with justification.** Run DFS; if any examined edge $\{u, v\}$ has $v$ grey and $v \ne \mathrm{parent}[u]$, report a cycle (the tree path $v \leadsto u$ plus $\{u,v\}$). If DFS finishes without such an edge, all edges are tree edges (undirected DFS has only tree and back edges), hence acyclic. Alternative: count; a connected graph with $m \ge n$ has a cycle.

3. **Show that a directed graph is a DAG iff DFS finds no back edge.** Back edge $(u, v)$ with $v$ an ancestor of $u$: tree path $v \leadsto u$ plus $(u,v)$ is a cycle. Conversely, let $C$ be a cycle and $v$ its first-discovered vertex; all other cycle vertices are reachable from $v$ via white vertices at that moment, so they become descendants of $v$ (white-path property, a consequence of the parenthesis theorem); the cycle edge into $v$ is then examined from a descendant while $v$ is grey: a back edge.

4. **A graph has $n$ vertices and $m$ edges. In which cases would you prefer an adjacency matrix?** Dense graphs ($m = \Theta(n^2)$) where the $\Theta(n^2)$ space is already needed; algorithms that need $O(1)$ edge queries (e.g. Floyd–Warshall, A05); very small $n$. For traversals, sparse graphs, or anything needing "iterate over neighbours", use lists.

5. **State and prove the invariant that makes Dijkstra correct; where do you use that lengths are non-negative?** See Results. When $v$ is extracted with key $\mathrm{dist}[v]$, any path $P$ to $v$ must leave $S$ at some first edge $(x, y)$, and $\ell(P) \ge d(s,x) + \ell(x,y) + \ell(\text{rest}) \ge \mathrm{dist}[y] + 0 \ge \mathrm{dist}[v]$. The "$+\,0$" is where $\ell \ge 0$ is used.

## 2026W lecture: chapter 2, graphs (07.10) [S62]

Chen's chapter-2 deck is Kleinberg and Tardos chapter 3 [S25] and matches the
sections above: representations, paths, cycles and trees, BFS and DFS,
connected components, bipartiteness, strong connectivity, DAGs and
topological order. Points it stresses, in our words:

- **Representation costs.** Adjacency matrix: $\Theta(n^2)$ space, edge test
  $\Theta(1)$, listing all edges $\Theta(n^2)$. Adjacency list: $\Theta(n+m)$
  space, edge test $O(\deg u)$, listing all edges $\Theta(n+m)$. Real graphs
  are sparse ($m=O(n)$), so "linear time" for a graph algorithm means
  $O(n+m)$ with adjacency lists.
- **Trees.** For an undirected graph on $n$ vertices, any two of "connected",
  "acyclic" and "$n-1$ edges" imply the third.
- **BFS** builds layers $L_0=\{s\}, L_1, \dots$; in a BFS tree the endpoints
  of every graph edge lie in the same or adjacent layers. With adjacency lists
  it runs in $O(n+m)$ because $\sum_v \deg v = 2m$. DFS also runs in $O(n+m)$
  but need not find shortest paths.
- **Bipartiteness.** $G$ is bipartite iff it has no odd cycle. Test: run BFS;
  if no edge joins two vertices of the same layer, colour even layers one way
  and odd layers the other. If an edge $\{x,y\}$ lies inside layer $j$, the
  paths up to their lowest common ancestor in layer $i$ close a cycle of length
  $2(j-i)+1$.
- **Strong connectivity.** $G$ is strongly connected iff some (any) vertex $s$
  reaches every vertex and every vertex reaches $s$; check with one BFS from
  $s$ in $G$ and one in the reversed graph, $O(n+m)$.
- **DAGs.** A directed graph has a topological order iff it is a DAG. Every
  DAG has a source (walk backwards along in-arcs; without a source the walk
  repeats a vertex and closes a cycle), so peel off sources one by one. With
  in-arc counters and a set of current sources this takes $O(n+m)$.

### Cards

```card id=qc-alg2-matrix-vs-list
Adjacency matrix vs adjacency list: space, edge test, listing all edges.
---
Matrix: $\Theta(n^2)$ space, edge test $\Theta(1)$, all edges $\Theta(n^2)$. List: $\Theta(n+m)$ space, edge test $O(\deg u)$, all edges $\Theta(n+m)$. Sparse graphs ($m=O(n)$) favour lists.
```

```card id=qc-alg2-tree-two-of-three
Characterise trees among undirected graphs on $n$ vertices.
---
Any two of these imply the third: $G$ is connected; $G$ has no cycle; $G$ has $n-1$ edges.
```

```card id=qc-alg2-bfs-layers
BFS tree property for an edge $\{x,y\}$ of $G$?
---
The BFS levels of $x$ and $y$ differ by at most 1.
```

```card id=qc-alg2-bfs-time
Why does BFS run in $O(n+m)$ with adjacency lists?
---
Each vertex enters the queue at most once, and scanning $u$ costs $O(\deg u)$; $\sum_u \deg u = 2m$, since every edge is counted once at each end.
```

```card id=qc-alg2-bipartite
When is a graph bipartite, and how do you test it in linear time?
---
Iff it has no odd-length cycle. Run BFS from $s$: if no edge joins two vertices of the same layer, colour layers by parity; otherwise that edge plus the two tree paths to the lowest common ancestor form an odd cycle of length $2(j-i)+1$.
```

```card id=qc-alg2-strong-connectivity
How do you decide in $O(n+m)$ whether a digraph is strongly connected?
---
Pick any $s$. BFS from $s$ in $G$ and BFS from $s$ in $G^{\mathrm{rev}}$ (all arcs reversed). Strongly connected iff both reach every vertex, because $u\to s\to v$ then exists for all $u,v$.
```

```card id=qc-alg2-dag-topo
Which directed graphs have a topological order?
---
Exactly the DAGs. A cycle would need its lowest-indexed vertex to come after its predecessor on the cycle; conversely every DAG has a source, which can go first, and induction finishes.
```

```card id=qc-alg2-dag-source
Why does every DAG have a source (a vertex with no in-arc)?
---
If every vertex had an in-arc, walking backwards along in-arcs from any vertex would never stop, so some vertex repeats and the walk between its two visits is a directed cycle.
```

```card id=qc-alg2-topo-time
How is topological sorting done in $O(n+m)$?
---
Count the remaining in-arcs of each vertex and keep the set of vertices with count 0. Repeatedly remove one, output it, and decrement its out-neighbours' counts, adding those that reach 0.
```

## Code

`src/py/algorithmics/graphs.py`: `bfs(adj, s)` (returns dist and parent), `dfs(adj)` (discovery/finish times and edge classification), `connected_components(adj)`, `is_bipartite(adj)` (returns colouring or an odd cycle), `topological_sort(adj)` (Kahn; raises on a cycle), `dijkstra(adj, s)` with a binary heap. C++ reference of the same Dijkstra with `std::priority_queue`: `src/cpp/dijkstra.cpp`.
