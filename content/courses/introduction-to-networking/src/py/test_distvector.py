from distvector import DVNetwork, count_to_infinity_demo, INF
from linkstate import dijkstra, undirected


EDGES = [("A", "B", 1), ("B", "C", 1), ("A", "C", 5), ("C", "D", 2)]


def test_converges_to_shortest_paths():
    net = DVNetwork(EDGES)
    assert net.converge() is not None
    g = undirected(EDGES)
    for n in g:
        dist, _ = dijkstra(g, n)
        assert {d: c for d, c in net.dump()[n].items()} == dist
    assert net.nodes["A"].table["D"] == (4, "B")


def test_count_to_infinity_without_and_with_poison_reverse():
    hist = count_to_infinity_demo(verbose=False)
    costs_b = [b for b, _ in hist]
    assert costs_b[0] == 3                     # B thinks: C reaches A at 2, so c(B,C) + 2 = 3
    assert all(y - x in (0, 1, 2) for x, y in zip(costs_b, costs_b[1:]))   # bounces upward
    assert costs_b[-1] == INF and len(hist) > 5
    hist_pr = count_to_infinity_demo(poison_reverse=True, verbose=False)
    assert hist_pr[-1] == (INF, INF) and len(hist_pr) <= 3


def test_split_horizon_also_fixes_the_two_node_loop():
    hist = count_to_infinity_demo(split_horizon=True, verbose=False)
    assert hist[-1] == (INF, INF) and len(hist) <= 3


def test_matches_networkx_bellman_ford_on_random_graphs():
    """Distributed Bellman-Ford converges to the same distances as networkx's
    centralised Bellman-Ford (costs kept small so every distance stays < INF)."""
    import networkx as nx
    for seed in range(5):
        G = nx.connected_watts_strogatz_graph(12, 4, 0.3, seed=seed)
        edges = [(u, v, (u * 5 + v * 3 + seed) % 3 + 1) for u, v in G.edges]
        for u, v, w in edges:
            G[u][v]["w"] = w
        net = DVNetwork(edges)
        assert net.converge() is not None
        for src in G:
            ref = nx.single_source_bellman_ford_path_length(G, src, weight="w")
            assert net.dump()[src] == ref
