import random

import networkx as nx
import pytest

from graphs import (Graph, bfs, connected_components, dfs, dijkstra,
                    has_cycle_directed, is_bipartite, path_to, topological_sort)


def random_graph(n, p, rng, directed=False):
    g = Graph(directed=directed)
    nxg = nx.DiGraph() if directed else nx.Graph()
    for u in range(n):
        g.add_node(u)
        nxg.add_node(u)
    for u in range(n):
        for v in range(n):
            if u != v and (directed or u < v) and rng.random() < p:
                g.add_edge(u, v)
                nxg.add_edge(u, v)
    return g, nxg


def test_bfs_distances_match_networkx():
    rng = random.Random(1)
    for _ in range(20):
        g, nxg = random_graph(15, 0.2, rng)
        dist, parent = bfs(g, 0)
        assert dist == nx.single_source_shortest_path_length(nxg, 0)
        for v in dist:  # parent path has length dist[v]
            assert len(path_to(parent, v)) == dist[v] + 1


def test_dfs_parenthesis_and_coverage():
    rng = random.Random(2)
    g, _ = random_graph(20, 0.15, rng, directed=True)
    disc, fin, parent = dfs(g)
    assert set(disc) == set(g.nodes) and set(fin) == set(g.nodes)
    times = sorted(list(disc.values()) + list(fin.values()))
    assert times == list(range(2 * len(g)))
    for v, u in parent.items():  # child interval nested in parent interval
        if u is not None:
            assert disc[u] < disc[v] < fin[v] < fin[u]


def test_connected_components():
    rng = random.Random(3)
    for _ in range(20):
        g, nxg = random_graph(25, 0.06, rng)
        mine = sorted(sorted(c) for c in connected_components(g))
        ref = sorted(sorted(c) for c in nx.connected_components(nxg))
        assert mine == ref


def test_bipartite_colouring_or_odd_cycle():
    rng = random.Random(4)
    hits = {True: 0, False: 0}
    for _ in range(60):
        g, nxg = random_graph(10, 0.15, rng)
        ok, wit = is_bipartite(g)
        assert ok == nx.is_bipartite(nxg)
        hits[ok] += 1
        if ok:
            for u, v, _ in g.edges():
                assert wit[u] != wit[v]
        else:
            assert len(wit) % 2 == 1 and len(wit) >= 3
            for i in range(len(wit)):  # witness is a closed walk of odd length
                assert wit[(i + 1) % len(wit)] in g.adj[wit[i]]
    assert hits[True] > 0 and hits[False] > 0


def test_topological_sort_and_cycle_detection():
    rng = random.Random(5)
    for _ in range(20):
        n = 12
        g = Graph(directed=True)
        nxg = nx.DiGraph()
        for u in range(n):
            g.add_node(u)
            nxg.add_node(u)
        perm = list(range(n))
        rng.shuffle(perm)
        for i in range(n):
            for j in range(i + 1, n):
                if rng.random() < 0.25:
                    g.add_edge(perm[i], perm[j])
                    nxg.add_edge(perm[i], perm[j])
        assert not has_cycle_directed(g)
        order = topological_sort(g)
        pos = {u: i for i, u in enumerate(order)}
        assert all(pos[u] < pos[v] for u, v, _ in g.edges())
        # add a back edge along the order -> cycle (if any edge exists)
        edges = g.edges()
        if edges:
            u, v, _ = edges[0]
            g.add_edge(v, u)
            assert has_cycle_directed(g)
            with pytest.raises(ValueError):
                topological_sort(g)


def test_dijkstra_matches_networkx():
    rng = random.Random(6)
    for _ in range(20):
        g = Graph(directed=True)
        nxg = nx.DiGraph()
        for u in range(15):
            for v in range(15):
                if u != v and rng.random() < 0.3:
                    w = rng.randint(0, 20)
                    g.add_edge(u, v, w)
                    nxg.add_edge(u, v, weight=w)
        dist, parent = dijkstra(g, 0)
        assert dist == nx.single_source_dijkstra_path_length(nxg, 0)
        for v in dist:
            p = path_to(parent, v)
            assert sum(g.adj[a][b] for a, b in zip(p, p[1:])) == dist[v]
