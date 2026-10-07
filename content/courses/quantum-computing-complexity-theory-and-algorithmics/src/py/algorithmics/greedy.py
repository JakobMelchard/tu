"""Greedy algorithms (KT ch. 4): interval scheduling/partitioning, union-find,
Kruskal and Prim minimum spanning trees.

Belongs to the algorithmics note on greedy algorithms (A03).

Implements: interval_scheduling, interval_partitioning, UnionFind, kruskal,
prim, is_spanning_tree. Graph inputs are (nodes, edges) with edges (u, v, w).
"""
import heapq


def interval_scheduling(intervals):
    """Max set of pairwise disjoint intervals (s, f): pick earliest finish first.

    'Greedy stays ahead': the i-th chosen interval finishes no later than the
    i-th interval of any feasible solution (KT 4.1). O(n log n). Returns indices.
    """
    order = sorted(range(len(intervals)), key=lambda i: intervals[i][1])
    chosen = []
    last_finish = float("-inf")
    for i in order:
        s, f = intervals[i]
        if s >= last_finish:  # compatible with everything chosen so far
            chosen.append(i)
            last_finish = f
    return chosen


def interval_partitioning(intervals):
    """Assign intervals to the fewest resources; no two overlapping share one.

    Sort by start; keep a heap of (finish time, resource) of active resources.
    If the earliest-finishing resource is free, reuse it, else open a new one.
    Number used = depth = max overlap, a lower bound, so optimal (KT 4.1).
    Returns (num_resources, assignment list).
    """
    order = sorted(range(len(intervals)), key=lambda i: intervals[i][0])
    assign = [None] * len(intervals)
    heap = []  # (finish, resource id)
    resources = 0
    for i in order:
        s, f = intervals[i]
        if heap and heap[0][0] <= s:
            _, r = heapq.heappop(heap)
        else:
            r = resources
            resources += 1
        assign[i] = r
        heapq.heappush(heap, (f, r))
    return resources, assign


class UnionFind:
    """Disjoint sets with path compression and union by rank.

    Amortised O(alpha(n)) per operation (KT 4.6 gives O(log n) per op with
    union by size alone).
    """

    def __init__(self, items):
        self.parent = {x: x for x in items}
        self.rank = {x: 0 for x in items}
        self.count = len(self.parent)

    def find(self, x):
        root = x
        while self.parent[root] != root:
            root = self.parent[root]
        while self.parent[x] != root:  # path compression: point all to root
            self.parent[x], x = root, self.parent[x]
        return root

    def union(self, x, y):
        """Merge the sets of x and y; return True if they were different."""
        rx, ry = self.find(x), self.find(y)
        if rx == ry:
            return False
        if self.rank[rx] < self.rank[ry]:
            rx, ry = ry, rx
        self.parent[ry] = rx  # attach shorter tree under taller
        if self.rank[rx] == self.rank[ry]:
            self.rank[rx] += 1
        self.count -= 1
        return True


def kruskal(nodes, edges):
    """MST by adding edges in increasing weight unless they close a cycle.

    Cut property justifies every added edge (KT 4.5). O(m log m).
    Returns (total_weight, tree_edges). For a disconnected graph: a forest.
    """
    uf = UnionFind(nodes)
    tree = []
    total = 0
    for u, v, w in sorted(edges, key=lambda e: e[2]):
        if uf.union(u, v):
            tree.append((u, v, w))
            total += w
    return total, tree


def prim(nodes, edges, root=None):
    """MST by growing a tree from root, always adding the cheapest crossing edge.

    Heap of (weight, from, to); lazy deletion of stale entries. O(m log n).
    Returns (total_weight, tree_edges) of root's component.
    """
    adj = {u: [] for u in nodes}
    for u, v, w in edges:
        adj[u].append((v, w))
        adj[v].append((u, w))
    root = nodes[0] if root is None else root
    in_tree = {root}
    heap = [(w, root, v) for v, w in adj[root]]
    heapq.heapify(heap)
    tree, total = [], 0
    while heap and len(in_tree) < len(nodes):
        w, u, v = heapq.heappop(heap)
        if v in in_tree:
            continue
        in_tree.add(v)
        tree.append((u, v, w))
        total += w
        for x, wx in adj[v]:
            if x not in in_tree:
                heapq.heappush(heap, (wx, v, x))
    return total, tree


def is_spanning_tree(nodes, tree_edges):
    """n-1 edges, acyclic, connected  <=>  spanning tree."""
    if len(tree_edges) != len(nodes) - 1:
        return False
    uf = UnionFind(nodes)
    for u, v, _ in tree_edges:
        if not uf.union(u, v):  # closes a cycle
            return False
    return uf.count == 1


if __name__ == "__main__":
    jobs = [(0, 6), (1, 4), (3, 5), (3, 8), (4, 7), (5, 9), (6, 10), (8, 11)]
    ch = interval_scheduling(jobs)
    print("interval scheduling picks", [jobs[i] for i in ch])
    k, assign = interval_partitioning(jobs)
    print("interval partitioning needs", k, "resources:", assign)
    nodes = list("abcdef")
    edges = [("a", "b", 4), ("a", "c", 1), ("b", "c", 2), ("b", "d", 5),
             ("c", "d", 8), ("c", "e", 10), ("d", "e", 2), ("d", "f", 6), ("e", "f", 3)]
    wk, tk = kruskal(nodes, edges)
    wp, tp = prim(nodes, edges)
    print("Kruskal MST weight", wk, tk)
    print("Prim    MST weight", wp, tp)
    print("spanning tree?", is_spanning_tree(nodes, tk), is_spanning_tree(nodes, tp))
