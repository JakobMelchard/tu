import networkx as nx

import recursive_cte as rc


def closure_bfs(edges):
    adj = {}
    for s, d, *_ in edges:
        adj.setdefault(s, set()).add(d)
    out = set()
    for s in adj:
        stack, seen = list(adj[s]), set()
        while stack:
            x = stack.pop()
            if x not in seen:
                seen.add(x)
                stack += adj.get(x, ())
        out |= {(s, y) for y in seen}
    return out


def test_transitive_closure_matches_bfs():
    conn = rc.make_db()
    tc = rc.transitive_closure(conn)
    assert tc == closure_bfs(rc.EDGES)
    assert len(tc) == 20                     # a reaches 4 nodes; b..e reach all of b..e


def test_working_table_trace_is_postgres_algorithm():
    result, rounds = rc.working_table_trace(rc.EDGES)
    assert set(result) == rc.transitive_closure(rc.make_db())
    assert [len(r) for r in rounds] == [7, 6, 6, 1]
    assert len(result) == len(set(result))   # UNION: no duplicates ever enter


def test_union_all_on_a_cycle_does_not_terminate():
    _, rounds = rc.working_table_trace(rc.EDGES, union=False, max_rounds=30)
    assert len(rounds) == 30 and rounds[-1]  # still producing rows when cut off


def test_shortest_paths_match_networkx():
    G = nx.DiGraph()
    G.add_weighted_edges_from(rc.EDGES)
    ref = nx.single_source_dijkstra_path_length(G, "a")
    sp = rc.shortest_paths(rc.make_db(), "a")
    assert {k: d for k, (d, _) in sp.items()} == ref
    assert sp["e"] == (7, "a,c,b,d,e")


def test_bill_of_materials_and_union_pitfall():
    conn = rc.make_db()
    assert rc.bill_of_materials(conn, "bike") == {
        "bearing": 4, "bolt": 8, "rim": 2, "spoke": 64, "tube": 3}
    # (bolt, 4) arrives twice (2 wheels x 2 bolts, 1 frame x 4 bolts): UNION keeps one
    assert rc.bill_of_materials(conn, "bike", "UNION")["bolt"] == 4
    assert rc.bill_of_materials(conn, "wheel") == {"bearing": 2, "bolt": 2, "rim": 1, "spoke": 32}


def test_same_generation_by_depth():
    parent = dict(rc.PAR)
    depth = {}
    for c in parent:
        d, x = 0, c
        while x in parent:
            d, x = d + 1, parent[x]
        depth[c] = d
    ref = {(x, y) for x in depth for y in depth if depth[x] == depth[y]}
    assert rc.same_generation(rc.make_db()) == ref
    assert len(ref) == 17


def test_growing_column_defeats_union():
    assert rc.depth_counter_rows(rc.make_db(), 250) == 250
