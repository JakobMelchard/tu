from pathvector import PathVectorNetwork, GaoRexford, ShortestPath, CUSTOMER, PROVIDER, PEER, demo


def test_shortest_paths_and_loop_rejection():
    # triangle plus tail: 1-2, 2-3, 1-3, 3-4
    net = PathVectorNetwork([(1, 2), (2, 3), (1, 3), (3, 4)], {"p": 4})
    assert net.converge() is not None
    assert net.path(1, "p") == (1, 3, 4) and net.path(2, "p") == (2, 3, 4)
    assert any("loop" in line for line in net.log)


def test_gao_rexford_prefers_customer_and_stays_valley_free():
    net = demo()
    # AS4 reaches p1 through a customer (2 or 3), never via a peer of a peer.
    assert net.path(4, "p1") in [(4, 2, 1), (4, 3, 1)]
    # AS1 (customer of both) reaches p4 in two hops through a provider.
    assert net.path(1, "p4") in [(1, 2, 4), (1, 3, 4)]
    # 2 and 3 peer: 2 must NOT learn p4 via 3 (3 learnt it from a provider -> not exported to a peer)
    assert net.path(2, "p4") == (2, 4) and net.path(3, "p4") == (3, 4)


def test_policy_can_produce_longer_than_shortest_path():
    # 2 is a customer of 1, 3 is a customer of 2, and 1-3 peer.  Prefix p at 3.
    # 1 hears p directly from peer 3 (length 2) and from customer 2 (length 3).
    rel = {(1, 2): CUSTOMER, (2, 1): PROVIDER, (1, 3): PEER, (3, 1): PEER, (2, 3): CUSTOMER, (3, 2): PROVIDER}
    net = PathVectorNetwork([(1, 2), (1, 3), (2, 3)], {"p": 3}, GaoRexford(rel))
    net.converge()
    # 1 gets p from 3 (peer, length 2) and from 2 (customer, length 3): customer wins.
    assert net.path(1, "p") == (1, 2, 3)


def test_withdrawal_after_link_failure_reconverges():
    net = PathVectorNetwork([(1, 2), (2, 3), (1, 3)], {"p": 3})
    net.converge()
    assert net.path(1, "p") == (1, 3)
    net.remove_link(1, 3)
    assert net.converge() is not None
    assert net.path(1, "p") == (1, 2, 3)


def test_shortest_path_policy_matches_networkx_hop_counts():
    """With the ShortestPath policy, path vector converges to BFS shortest paths
    (in AS hops), which networkx computes centrally."""
    import networkx as nx
    for seed in range(4):
        G = nx.connected_watts_strogatz_graph(10, 4, 0.4, seed=seed)
        net = PathVectorNetwork(list(G.edges), {"p": 0})
        assert net.converge() is not None
        hops = nx.single_source_shortest_path_length(G, 0)
        for asn in G:
            path = net.path(asn, "p")
            assert path[0] == asn and path[-1] == 0 and len(path) - 1 == hops[asn]
            assert all(G.has_edge(x, y) for x, y in zip(path, path[1:]))   # a real path
            assert len(set(path)) == len(path)                           # loop-free
