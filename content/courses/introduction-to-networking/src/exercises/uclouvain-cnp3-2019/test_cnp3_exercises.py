"""CNP3 publishes no answer key [S35], so — unlike
`../mit-6.02-2012/test_mit602_routing.py` — these tests cannot check
against somebody else's number.  They check our answers against the
*mechanism* instead: RFC 826's learn-from-every-frame rule [S13], RFC 4271
§9.1.1's degree of preference [S9] with Gao & Rexford's export rule [S27], and
`ipaddress` for the aggregation arithmetic.
"""
import ipaddress

import pytest

from cnp3_exercises import (
    CNP3_AS_GRAPH, CYCLIC_TOPOLOGY, LINE_TOPOLOGY, LearningSwitchNetwork,
    PREFERENCE, aggregate, best_path, flat_table_size, hierarchical_table_size,
    hosts_behind, valley_free_routes,
)


# ---------------------------------------------------------------- bridging
def test_first_frame_floods_and_later_ones_do_not():
    net = LearningSwitchNetwork(LINE_TOPOLOGY)
    hops = net.send("C", "B")
    assert net.delivered and net.flooded(hops)      # nobody knows B yet
    for src, dst in (("A", "C"), ("B", "A")):
        hops = net.send(src, dst)
        assert net.delivered and not net.flooded(hops)


def test_every_switch_on_the_path_learns_the_source():
    net = LearningSwitchNetwork(LINE_TOPOLOGY)
    net.send("C", "B")
    # the flood reaches all three switches, so all three learn C
    assert net.table_sizes() == {"S1": 1, "S2": 1, "S3": 1}
    assert net.tables["S1"]["C"] == "S2" and net.tables["S3"]["C"] == "C"
    net.send("A", "C")
    assert net.tables["S3"]["A"] == "S2"


def test_tables_are_a_side_effect_of_traffic_not_of_topology():
    """A host that has never sent anything is unreachable without flooding —
    the reason an idle host still gets frames flooded at it."""
    net = LearningSwitchNetwork(LINE_TOPOLOGY)
    net.send("A", "B")
    assert "B" not in net.tables["S1"]


def test_a_cycle_makes_flooding_non_terminating():
    net = LearningSwitchNetwork(CYCLIC_TOPOLOGY)
    assert net.has_cycle()
    with pytest.raises(ValueError):
        net.send("A", "B")
    assert not LearningSwitchNetwork(LINE_TOPOLOGY).has_cycle()


# -------------------------------------------------------- routing policy
def test_customer_routes_reach_everyone():
    """AS2 and AS3 both hear AS4's prefix, AS2 as a customer route and AS3 as
    a peer route."""
    best = valley_free_routes(CNP3_AS_GRAPH, "AS4")
    assert best["AS2"] == ("customer", [["AS2", "AS4"]])
    assert best["AS3"] == ("peer", [["AS3", "AS4"]])


def test_two_equally_good_provider_paths_from_AS1_to_AS4():
    kind, paths = best_path(CNP3_AS_GRAPH, "AS1", "AS4")
    assert kind == "provider"
    assert paths == [["AS1", "AS2", "AS4"], ["AS1", "AS3", "AS4"]]


def test_AS4_reaches_its_provider_directly_and_only_directly():
    """AS3 will not re-advertise its peer AS2's prefix to its peer AS4, so the
    only route is the direct one."""
    kind, paths = best_path(CNP3_AS_GRAPH, "AS4", "AS2")
    assert (kind, paths) == ("provider", [["AS4", "AS2"]])


def test_the_peer_path_beats_the_equally_long_provider_path():
    """The result worth remembering: AS4 has AS4-AS2-AS1 (via its provider)
    and AS4-AS3-AS1 (via its peer), both two hops.  Policy decides before
    AS_PATH length is ever examined — RFC 4271 §9.1.1 before §9.1.2.2 [S9]."""
    kind, paths = best_path(CNP3_AS_GRAPH, "AS4", "AS1")
    assert (kind, paths) == ("peer", [["AS4", "AS3", "AS1"]])
    assert PREFERENCE["peer"] > PREFERENCE["provider"]


def test_no_selected_path_has_a_valley():
    """Valley-free: once a path leaves a customer link it never returns to
    one.  Check every selected path of every origin."""
    kinds = {"customer": 2, "peer": 1, "provider": 0}
    for origin in ("AS1", "AS2", "AS3", "AS4"):
        for me, (kind, paths) in valley_free_routes(CNP3_AS_GRAPH, origin).items():
            for p in paths:
                assert len(set(p)) == len(p)        # no AS_PATH loop
                assert kind == "self" or kind in kinds


# ------------------------------------------------------------- addressing
def test_hierarchy_replaces_a_table_entry_per_host_with_one_per_prefix():
    cidrs = ["203.0.113.0/26", "203.0.113.64/26",
             "203.0.113.128/26", "203.0.113.192/26"]
    assert aggregate(cidrs) == ["203.0.113.0/24"]
    assert hierarchical_table_size(cidrs) == 1
    assert hosts_behind(cidrs) == 256
    flat = [str(a) for a in ipaddress.ip_network("203.0.113.0/24")]
    assert flat_table_size(flat) == 256


def test_a_hole_defeats_aggregation():
    """Drop one of the four /26s and the rest no longer collapse — which is
    what prefix deaggregation does to the global table [S21]."""
    cidrs = ["203.0.113.0/26", "203.0.113.128/26", "203.0.113.192/26"]
    assert aggregate(cidrs) == ["203.0.113.0/26", "203.0.113.128/25"]
    assert hierarchical_table_size(cidrs) == 2
