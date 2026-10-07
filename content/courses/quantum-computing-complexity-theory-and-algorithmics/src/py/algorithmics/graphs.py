"""Graph representation and traversal (KT ch. 3, Dijkstra from KT 4.4).

Belongs to the algorithmics notes on graphs (A02) and greedy shortest paths (A03).

Implements: Graph (adjacency list, undirected or directed), bfs, dfs (iterative,
with discovery/finish times), connected_components, is_bipartite (2-colouring or
odd-cycle witness), topological_sort (Kahn), has_cycle_directed, dijkstra (heap).
"""
from collections import deque
import heapq


class Graph:
    """Adjacency-list graph. Nodes are hashable; edges carry an optional weight."""

    def __init__(self, directed=False):
        self.directed = directed
        self.adj = {}  # node -> dict(neighbour -> weight)

    def add_node(self, u):
        self.adj.setdefault(u, {})

    def add_edge(self, u, v, w=1):
        self.add_node(u)
        self.add_node(v)
        self.adj[u][v] = w
        if not self.directed:
            self.adj[v][u] = w

    @property
    def nodes(self):
        return list(self.adj)

    def edges(self):
        """Edge list (u, v, w); each undirected edge reported once."""
        seen = set()
        out = []
        for u in self.adj:
            for v, w in self.adj[u].items():
                key = (u, v) if self.directed else frozenset((u, v))
                if key in seen:
                    continue
                seen.add(key)
                out.append((u, v, w))
        return out

    def neighbours(self, u):
        return list(self.adj[u])

    def __len__(self):
        return len(self.adj)


def bfs(g, s):
    """Breadth-first search from s. Returns (dist, parent); dist counts edges.

    Layer L_i = nodes at distance exactly i. Every node is enqueued once, every
    edge examined O(1) times: O(n + m) with adjacency lists.
    """
    dist = {s: 0}
    parent = {s: None}
    q = deque([s])
    while q:
        u = q.popleft()
        for v in g.adj[u]:
            if v not in dist:
                dist[v] = dist[u] + 1
                parent[v] = u
                q.append(v)
    return dist, parent


def dfs(g, s=None):
    """Iterative depth-first search. Returns (disc, fin, parent).

    disc/fin are discovery/finish timestamps (one global clock). If s is given,
    only its component is explored; otherwise all nodes in insertion order.
    Uses an explicit stack of (node, neighbour iterator) to mimic recursion.
    """
    disc, fin, parent = {}, {}, {}
    clock = 0
    roots = [s] if s is not None else g.nodes
    for r in roots:
        if r in disc:
            continue
        parent[r] = None
        disc[r] = clock
        clock += 1
        stack = [(r, iter(g.adj[r]))]
        while stack:
            u, it = stack[-1]
            advanced = False
            for v in it:
                if v not in disc:
                    parent[v] = u
                    disc[v] = clock
                    clock += 1
                    stack.append((v, iter(g.adj[v])))
                    advanced = True
                    break
            if not advanced:
                fin[u] = clock
                clock += 1
                stack.pop()
    return disc, fin, parent


def connected_components(g):
    """List of components (as lists of nodes) of an undirected graph, via BFS."""
    assert not g.directed, "use strongly connected components for digraphs"
    seen = set()
    comps = []
    for u in g.nodes:
        if u in seen:
            continue
        dist, _ = bfs(g, u)
        comp = list(dist)
        seen.update(comp)
        comps.append(comp)
    return comps


def is_bipartite(g):
    """2-colour via BFS layers. Returns (True, colour) or (False, odd_cycle).

    Colour = parity of BFS layer. The graph is bipartite iff no edge joins two
    nodes of the same layer (KT 3.4). Such an edge (u, v) plus the tree paths
    to the lowest common ancestor forms an odd cycle, which we return.
    """
    colour = {}
    parent = {}
    for r in g.nodes:
        if r in colour:
            continue
        colour[r] = 0
        parent[r] = None
        q = deque([r])
        while q:
            u = q.popleft()
            for v in g.adj[u]:
                if v not in colour:
                    colour[v] = 1 - colour[u]
                    parent[v] = u
                    q.append(v)
                elif colour[v] == colour[u]:
                    return False, _odd_cycle(u, v, parent)
    return True, colour


def _odd_cycle(u, v, parent):
    """Cycle u ... lca ... v u built from BFS tree paths; has odd length."""
    path_u = []
    x = u
    while x is not None:
        path_u.append(x)
        x = parent[x]
    anc = {x: i for i, x in enumerate(path_u)}
    path_v = []
    x = v
    while x not in anc:
        path_v.append(x)
        x = parent[x]
    lca = x
    return path_u[: anc[lca] + 1] + path_v[::-1]


def topological_sort(g):
    """Kahn's algorithm: repeatedly remove a node of in-degree 0 (KT 3.6).

    Raises ValueError if the digraph has a cycle (some node never reaches
    in-degree 0). O(n + m).
    """
    assert g.directed
    indeg = {u: 0 for u in g.adj}
    for u in g.adj:
        for v in g.adj[u]:
            indeg[v] += 1
    ready = deque(u for u in g.adj if indeg[u] == 0)
    order = []
    while ready:
        u = ready.popleft()
        order.append(u)
        for v in g.adj[u]:
            indeg[v] -= 1
            if indeg[v] == 0:
                ready.append(v)
    if len(order) != len(g.adj):
        raise ValueError("graph has a directed cycle")
    return order


def has_cycle_directed(g):
    """True iff the digraph contains a directed cycle (Kahn fails to empty)."""
    try:
        topological_sort(g)
    except ValueError:
        return True
    return False


def dijkstra(g, s):
    """Single-source shortest paths with non-negative weights (KT 4.4).

    Lazy-deletion binary heap: a popped entry is stale if its distance exceeds
    the recorded one. O((n + m) log n). Returns (dist, parent).
    """
    dist = {s: 0}
    parent = {s: None}
    heap = [(0, s)]
    done = set()
    while heap:
        d, u = heapq.heappop(heap)
        if u in done:
            continue
        done.add(u)
        for v, w in g.adj[u].items():
            assert w >= 0, "Dijkstra requires non-negative weights"
            nd = d + w
            if v not in dist or nd < dist[v]:
                dist[v] = nd
                parent[v] = u
                heapq.heappush(heap, (nd, v))
    return dist, parent


def path_to(parent, t):
    """Reconstruct the path to t from a parent map (root first)."""
    path = []
    while t is not None:
        path.append(t)
        t = parent[t]
    return path[::-1]


if __name__ == "__main__":
    g = Graph()
    for u, v in [(1, 2), (1, 3), (2, 4), (3, 4), (4, 5), (6, 7)]:
        g.add_edge(u, v)
    dist, par = bfs(g, 1)
    print("BFS layers from 1:", dict(sorted(dist.items())))
    print("components:", connected_components(g))
    print("bipartite:", is_bipartite(g))
    g.add_edge(2, 3)
    ok, wit = is_bipartite(g)
    print("after adding 2-3, bipartite:", ok, "odd cycle:", wit)
    d = Graph(directed=True)
    for u, v in [("a", "b"), ("a", "c"), ("b", "d"), ("c", "d"), ("d", "e")]:
        d.add_edge(u, v)
    print("topological order:", topological_sort(d))
    disc, fin, _ = dfs(d, "a")
    print("DFS disc/fin:", {u: (disc[u], fin[u]) for u in disc})
    w = Graph(directed=True)
    for u, v, c in [("s", "a", 4), ("s", "b", 1), ("b", "a", 2), ("a", "t", 1), ("b", "t", 5)]:
        w.add_edge(u, v, c)
    dist, par = dijkstra(w, "s")
    print("Dijkstra from s:", dist, "path s->t:", path_to(par, "t"))
