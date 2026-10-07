"""Network flow (KT ch. 7): Ford-Fulkerson, Edmonds-Karp, capacity scaling,
min cut, bipartite matching, project selection via min cut.

Belongs to the algorithmics note on network flow (A06).

Implements: FlowNetwork, ford_fulkerson, edmonds_karp, capacity_scaling,
min_cut, bipartite_matching, project_selection.
Capacities are integers; residual graph stored as dict of dicts.
"""
from collections import deque


class FlowNetwork:
    """Directed graph with integer capacities; cap[u][v] is residual capacity.

    Adding edge (u, v, c) also creates the reverse residual edge with 0 so
    that augmentation can 'undo' flow (KT 7.1).
    """

    def __init__(self):
        self.cap = {}     # residual capacities
        self.orig = {}    # original capacities, for reporting flow

    def add_node(self, u):
        self.cap.setdefault(u, {})
        self.orig.setdefault(u, {})

    def add_edge(self, u, v, c):
        self.add_node(u)
        self.add_node(v)
        self.cap[u][v] = self.cap[u].get(v, 0) + c
        self.cap[v].setdefault(u, 0)
        self.orig[u][v] = self.orig[u].get(v, 0) + c

    def flow_on(self, u, v):
        """Flow on original edge (u, v). With antiparallel edges the residual
        stores the net flow, so opposite flows cancel: report max(0, net)."""
        return max(0, self.orig[u][v] - self.cap[u][v])

    def copy(self):
        g = FlowNetwork()
        g.cap = {u: dict(d) for u, d in self.cap.items()}
        g.orig = {u: dict(d) for u, d in self.orig.items()}
        return g


def _augment(g, path, s, t):
    """Push the bottleneck along path (list of nodes) and update residuals."""
    b = min(g.cap[u][v] for u, v in zip(path, path[1:]))
    for u, v in zip(path, path[1:]):
        g.cap[u][v] -= b
        g.cap[v][u] += b
    return b


def _dfs_path(g, s, t, threshold=1):
    """Any s-t path in the residual graph using edges with cap >= threshold."""
    parent = {s: None}
    stack = [s]
    while stack:
        u = stack.pop()
        if u == t:
            break
        for v, c in g.cap[u].items():
            if c >= threshold and v not in parent:
                parent[v] = u
                stack.append(v)
    return _unwind(parent, t)


def _bfs_path(g, s, t, threshold=1):
    """Shortest (fewest edges) s-t residual path, the Edmonds-Karp choice."""
    parent = {s: None}
    q = deque([s])
    while q:
        u = q.popleft()
        if u == t:
            break
        for v, c in g.cap[u].items():
            if c >= threshold and v not in parent:
                parent[v] = u
                q.append(v)
    return _unwind(parent, t)


def _unwind(parent, t):
    if t not in parent:
        return None
    path = []
    while t is not None:
        path.append(t)
        t = parent[t]
    return path[::-1]


def ford_fulkerson(g, s, t):
    """Augment along DFS paths until none exists. O(m * C) with C = max flow.

    Mutates g's residual capacities. Returns the max flow value.
    """
    total = 0
    while (p := _dfs_path(g, s, t)) is not None:
        total += _augment(g, p, s, t)
    return total


def edmonds_karp(g, s, t):
    """Ford-Fulkerson with BFS (shortest) augmenting paths: O(n m^2)."""
    total = 0
    while (p := _bfs_path(g, s, t)) is not None:
        total += _augment(g, p, s, t)
    return total


def capacity_scaling(g, s, t):
    """Only augment along paths with bottleneck >= Delta; halve Delta (KT 7.3).

    Each phase has <= 2m augmentations; O(m^2 log C) total.
    """
    C = max((c for d in g.cap.values() for c in d.values()), default=0)
    delta = 1
    while delta * 2 <= C:
        delta *= 2
    total = 0
    while delta >= 1:
        while (p := _dfs_path(g, s, t, delta)) is not None:
            total += _augment(g, p, s, t)
        delta //= 2
    return total


def min_cut(g, s, t):
    """After a max flow: A = nodes reachable from s in the residual graph.

    (A, V \\ A) is a minimum cut; its capacity equals the max flow value.
    Returns (A, capacity of the cut).
    """
    A = {s}
    stack = [s]
    while stack:
        u = stack.pop()
        for v, c in g.cap[u].items():
            if c > 0 and v not in A:
                A.add(v)
                stack.append(v)
    cut = sum(c for u in A for v, c in g.orig[u].items() if v not in A)
    return A, cut


def bipartite_matching(left, right, edges):
    """Max bipartite matching by unit-capacity flow s->L->R->t (KT 7.5).

    Returns list of matched pairs (l, r).
    """
    g = FlowNetwork()
    s, t = ("_s",), ("_t",)
    for l in left:
        g.add_edge(s, ("L", l), 1)
    for r in right:
        g.add_edge(("R", r), t, 1)
    for l, r in edges:
        g.add_edge(("L", l), ("R", r), 1)
    edmonds_karp(g, s, t)
    return [(l, r) for l, r in edges if g.flow_on(("L", l), ("R", r)) == 1]


def project_selection(profit, prereq):
    """Max-profit closed set of projects (KT 7.11).

    profit: dict project -> value (positive revenue, negative cost).
    prereq: list of (p, q) meaning selecting p requires q.
    Build s->p with cap profit (p>0), p->t with cap -profit (p<0), p->q with
    cap infinity. Min cut (A, B): selected = A \\ {s}; profit = sum of
    positives - cut capacity. Returns (best_profit, selected set).
    """
    g = FlowNetwork()
    s, t = "_s", "_t"
    INF = sum(abs(v) for v in profit.values()) + 1
    g.add_node(s)
    g.add_node(t)
    for p, v in profit.items():
        g.add_node(p)
        if v > 0:
            g.add_edge(s, p, v)
        elif v < 0:
            g.add_edge(p, t, -v)
    for p, q in prereq:
        g.add_edge(p, q, INF)
    edmonds_karp(g, s, t)
    A, cut = min_cut(g, s, t)
    selected = A - {s}
    return sum(v for v in profit.values() if v > 0) - cut, selected


if __name__ == "__main__":
    g = FlowNetwork()
    for u, v, c in [("s", "a", 10), ("s", "b", 10), ("a", "b", 2), ("a", "t", 4),
                    ("a", "c", 8), ("b", "c", 9), ("c", "t", 10), ("c", "b", 6)]:
        g.add_edge(u, v, c)
    for name, fn in [("Ford-Fulkerson", ford_fulkerson), ("Edmonds-Karp", edmonds_karp),
                     ("capacity scaling", capacity_scaling)]:
        h = g.copy()
        val = fn(h, "s", "t")
        A, cut = min_cut(h, "s", "t")
        print(f"{name}: max flow {val}, min cut {sorted(A)} capacity {cut}")
    m = bipartite_matching([1, 2, 3], ["x", "y", "z"], [(1, "x"), (1, "y"), (2, "x"), (3, "z")])
    print("matching:", m)
    prof = {"A": 10, "B": 5, "C": -3, "D": -6, "E": -4}
    req = [("A", "C"), ("A", "D"), ("B", "D"), ("B", "E")]
    print("project selection:", project_selection(prof, req))
