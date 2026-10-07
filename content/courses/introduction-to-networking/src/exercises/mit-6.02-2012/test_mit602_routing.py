"""Every test asserts against a number **MIT published** in the solution PDF of
the corresponding 6.02 Fall 2012 tutorial [S34], read from
`PUBLISHED_ANSWERS`.  That is the point of using this source: it is the only
external answer key in the tree.  191.030 itself has none [S2].
"""
import math

import pytest

from mit602_routing import (
    INFINITY, NETWORK_I, NETWORK_II, PUBLISHED_ANSWERS, STRATEGIES, TRIANGLE,
    dv_failure_times, dv_first_entry_times, has_loop, next_hops,
    store_and_forward_latency, strategy_is_loop_free,
)

A = PUBLISHED_ANSWERS


def test_t08_store_and_forward_latency():
    # 5000-bit packet, 1 Gbit/s links, 10 us propagation.
    assert store_and_forward_latency(5000, 1e9, 10e-6, 2) == pytest.approx(A[("t08", "2A")])
    assert store_and_forward_latency(5000, 1e9, 10e-6, 4) == pytest.approx(A[("t08", "2B")])


def test_t10_distance_vector_first_entries():
    got = dv_first_entry_times(NETWORK_I, [("A", "B"), ("A", "C")])
    got |= dv_first_entry_times(NETWORK_II, [("D", "E"), ("F", "D")])
    assert got == A[("t10", "1A")]


def test_t10_distance_vector_after_failures():
    got = dv_failure_times(
        NETWORK_I, ("B", "C"), at=51,
        watchers={"B_says_C_unreachable":
                  lambda n: n.last_sent["B"]["A"].get("C") == INFINITY,
                  "A_knows_C_unreachable":
                  lambda n: not n.reachable("A", "C")})
    got |= dv_failure_times(
        NETWORK_II, ("D", "E"), at=71,
        watchers={"D_new_route_to_E": lambda n: n.reachable("D", "E")})
    assert got == A[("t10", "1B")]


def test_t10_new_route_to_E_goes_via_F():
    """Not asked by the sheet, but it is what makes 75 the right answer: the
    replacement route is the two-hop one through the third node."""
    net_times = dv_failure_times(
        NETWORK_II, ("D", "E"), at=71,
        watchers={"ok": lambda n: n.reachable("D", "E")})
    assert net_times == {"ok": 75}


@pytest.mark.parametrize("strategy,loop_free", sorted(A[("t10", "2A")].items()))
def test_t10_routing_strategies(strategy, loop_free):
    assert strategy_is_loop_free(strategy) is loop_free


def test_t10_second_min_cost_loops_on_the_published_counterexample():
    """MIT's counter-example: an equal-cost triangle.  A's runner-up path to D
    goes through B and B's goes through A."""
    hops = next_hops(TRIANGLE, "D", "SecondMinCost")
    assert hops == {"A": "B", "B": "A"}
    assert has_loop(TRIANGLE, "D", "SecondMinCost")


def test_safe_strategies_stay_loop_free_on_bigger_graphs():
    square = {"A": {"B": 1, "C": 4}, "B": {"A": 1, "D": 2},
              "C": {"A": 4, "D": 1}, "D": {"B": 2, "C": 1}}
    star = {"H": {"A": 3, "B": 1, "C": 5}, "A": {"H": 3, "B": 1},
            "B": {"H": 1, "A": 1, "C": 2}, "C": {"H": 5, "B": 2}}
    for s in ("MinCost", "MinHop", "MinCostSquared"):
        assert strategy_is_loop_free(s, graphs=(TRIANGLE, square, star))
    assert not strategy_is_loop_free("SecondMinCost", graphs=(TRIANGLE, square, star))



def test_strategy_table_is_complete():
    assert set(STRATEGIES) == set(A[("t10", "2A")])
    assert math.isinf(INFINITY)
