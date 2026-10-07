import networkx as nx
import pytest
from linkstate import dijkstra, path, routing_table, dijkstra_trace, EXAMPLE, undirected


def test_example_costs_and_paths():
    dist, prev = dijkstra(EXAMPLE, "u")
    assert dist == {"u": 0, "v": 2, "x": 1, "w": 3, "y": 2, "z": 4}
    assert path(prev, "z") == ["u", "x", "y", "z"] and path(prev, "w") == ["u", "x", "y", "w"]
    assert routing_table(EXAMPLE, "u") == {"v": ("v", 2), "x": ("x", 1), "w": ("x", 3),
                                           "y": ("x", 2), "z": ("x", 4)}


def test_matches_networkx_on_random_graph():
    G = nx.gnm_random_graph(12, 30, seed=3)
    for u, v in G.edges:
        G[u][v]["w"] = (u * 7 + v * 3) % 9 + 1
    g = undirected([(u, v, G[u][v]["w"]) for u, v in G.edges])
    dist, _ = dijkstra(g, 0)
    ref = nx.single_source_dijkstra_path_length(G, 0, weight="w")
    assert dist == ref


def test_trace_table_settles_in_cost_order():
    rows = dijkstra_trace(EXAMPLE, "u")
    assert rows[0]["N"] == "u" and rows[0]["v"] == (2, "u") and rows[0]["z"] == (float("inf"), None)
    assert rows[-1]["N"] == "uxyvwz" or rows[-1]["N"] == "uxvywz"  # v/y tie at cost 2
    assert len(rows) == 6


def test_negative_cost_rejected():
    with pytest.raises(ValueError):
        dijkstra({"a": {"b": -1}, "b": {}}, "a")
