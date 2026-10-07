"""Link-state routing: Dijkstra on a weighted graph and routing-table
derivation (note 07).

A link-state router floods its adjacencies (LSAs) so every node has the full
graph, then runs Dijkstra from itself.  The routing table only needs the
*first hop* of each shortest path, which is what `routing_table` extracts.

RFC 2328 section 16.1 is the same computation inside OSPF ("Calculating the
shortest-path tree for an area", a Dijkstra over the router and network LSAs;
the candidate list there is the heap here) and section 16.1.1 derives the
next hops, i.e. `routing_table`.  Flooding and LSA freshness are `ospf.py`.
The test cross-checks every distance against networkx.
"""
import heapq


def dijkstra(graph, source):
    """graph: {node: {neighbour: cost}}.  Returns (dist, prev) and records
    the order in which nodes were settled (the N' set in the Kurose/Ross
    tabular presentation) in `dijkstra.settled_order` for worked examples."""
    dist = {source: 0}
    prev = {source: None}
    settled, done = [], set()
    heap = [(0, source)]
    while heap:
        d, u = heapq.heappop(heap)
        if u in done:
            continue                        # stale heap entry
        done.add(u)
        settled.append((u, d))
        for v, w in graph.get(u, {}).items():
            if w < 0:
                raise ValueError("Dijkstra needs non-negative costs")
            nd = d + w
            if nd < dist.get(v, float("inf")):
                dist[v], prev[v] = nd, u
                heapq.heappush(heap, (nd, v))
    dijkstra.settled_order = settled
    return dist, prev


def path(prev, target):
    out = []
    while target is not None:
        out.append(target)
        target = prev[target]
    return out[::-1]


def routing_table(graph, source):
    """{destination: (next_hop, cost)} — first hop of the shortest path."""
    dist, prev = dijkstra(graph, source)
    table = {}
    for dst in dist:
        if dst == source:
            continue
        p = path(prev, dst)
        table[dst] = (p[1], dist[dst])
    return table


def dijkstra_trace(graph, source):
    """Tabular trace like in lecture slides: each step shows the settled set N'
    and current D(v),p(v) for every node.  Returns list of rows."""
    nodes = sorted(graph)
    dist = {n: float("inf") for n in nodes}
    prev = {n: None for n in nodes}
    dist[source] = 0
    settled, rows = [], []
    while len(settled) < len(nodes):
        u = min((n for n in nodes if n not in settled), key=lambda n: dist[n])
        settled.append(u)
        for v, w in graph[u].items():
            if v not in settled and dist[u] + w < dist[v]:
                dist[v], prev[v] = dist[u] + w, u
        rows.append({"step": len(rows), "N": "".join(settled),
                     **{n: (dist[n], prev[n]) for n in nodes if n not in settled}})
    return rows


def all_pairs_next_hop(graph):
    return {n: routing_table(graph, n) for n in graph}


def undirected(edges):
    """edges: [(a, b, cost), ...] -> adjacency dict with both directions."""
    g = {}
    for a, b, c in edges:
        g.setdefault(a, {})[b] = c
        g.setdefault(b, {})[a] = c
    return g


# Kurose & Ross style example topology used in note 07.
EXAMPLE = undirected([("u", "v", 2), ("u", "x", 1), ("u", "w", 5), ("v", "x", 2), ("v", "w", 3),
                      ("x", "w", 3), ("x", "y", 1), ("w", "y", 1), ("w", "z", 5), ("y", "z", 2)])


if __name__ == "__main__":
    dist, prev = dijkstra(EXAMPLE, "u")
    for n in sorted(dist):
        print(f"{n}: cost {dist[n]}  path {'-'.join(path(prev, n))}")
    print("routing table at u:", routing_table(EXAMPLE, "u"))
    for row in dijkstra_trace(EXAMPLE, "u"):
        print(row)
