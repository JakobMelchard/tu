"""Tests for the (min, +) all-pairs shortest path module.

Cross-checked against scipy's own Floyd-Warshall, so the two independent
routes in minplus_path.py are checked against a third implementation, not
against each other alone. See README.md for provenance.
"""

import numpy as np
import pytest
from scipy.sparse.csgraph import shortest_path

from minplus_path import (
    INF,
    flop_counts,
    floyd_warshall,
    largest_block_for_cache,
    max_abs_diff,
    minplus_product,
    minplus_product_blocked,
    random_graph,
    shortest_paths_squaring,
    squarings_needed,
    working_set_bytes,
)


def _scipy_reference(l):
    return shortest_path(np.where(np.isinf(l), 0.0, l), method="FW",
                         directed=True, unweighted=False)


# ------------------------------------------------------ correctness (task C)
@pytest.mark.parametrize("n", [8, 16, 32])
def test_floyd_warshall_agrees_with_scipy(n):
    l = random_graph(n, p=0.15, seed=n)
    got = floyd_warshall(l)
    want = shortest_path(np.where(np.isinf(l), 0.0, l), method="FW",
                         directed=True, unweighted=False)
    # scipy reads a 0 as "no edge" too, so only the finite entries are comparable
    finite = np.isfinite(got) & np.isfinite(want)
    assert np.allclose(got[finite], want[finite])


@pytest.mark.parametrize("n", [8, 16, 32, 64])
def test_squaring_and_floyd_warshall_agree(n):
    l = random_graph(n, p=0.08, seed=n)
    d_sq, _ = shortest_paths_squaring(l)
    assert max_abs_diff(floyd_warshall(l), d_sq) < 1e-12


def test_a_hand_computed_path():
    """0 ->(1)-> 1 ->(2)-> 2, plus a direct 0 -> 2 of weight 5: answer is 3."""
    l = np.array([[0.0, 1.0, 5.0], [INF, 0.0, 2.0], [INF, INF, 0.0]])
    d = floyd_warshall(l)
    assert d[0, 2] == 3.0 and d[0, 1] == 1.0 and np.isinf(d[2, 0])
    assert max_abs_diff(d, shortest_paths_squaring(l)[0]) == 0.0


def test_unreachable_stays_unreachable():
    l = np.full((4, 4), INF)
    np.fill_diagonal(l, 0.0)
    l[0, 1] = 1.0
    d, _ = shortest_paths_squaring(l)
    assert np.isinf(d[1, 0]) and np.isinf(d[2, 3]) and d[0, 1] == 1.0


# ------------------------------------------------------- cost model (task A)
@pytest.mark.parametrize("n", [8, 16, 32, 64])
def test_the_number_of_squarings_is_within_the_log_bound(n):
    _, steps = shortest_paths_squaring(random_graph(n, p=0.08, seed=n))
    assert steps <= squarings_needed(n) + 1


def test_the_squaring_route_costs_a_log_factor_more():
    for n in (64, 1024):
        c = flop_counts(n)
        assert c["ratio"] == squarings_needed(n) + 1
        assert c["squaring"] == pytest.approx(c["ratio"] * c["floyd_warshall"])
    assert flop_counts(1024)["ratio"] > flop_counts(64)["ratio"]


def test_one_squaring_is_paths_of_at_most_two_edges():
    l = np.array([[0.0, 1.0, INF, INF],
                  [INF, 0.0, 1.0, INF],
                  [INF, INF, 0.0, 1.0],
                  [INF, INF, INF, 0.0]])
    once = minplus_product(l, l)
    assert once[0, 2] == 2.0      # two edges: reachable after one squaring
    assert np.isinf(once[0, 3])   # three edges: not yet
    assert minplus_product(once, once)[0, 3] == 3.0


# --------------------------------------------------------- blocking (task B)
@pytest.mark.parametrize("block", [1, 4, 8, 32])
def test_blocking_does_not_change_the_result(block):
    l = random_graph(24, p=0.2, seed=7)
    assert max_abs_diff(minplus_product(l, l),
                        minplus_product_blocked(l, l, block)) < 1e-12


def test_blocking_handles_a_size_not_divisible_by_the_block():
    l = random_graph(23, p=0.2, seed=11)
    assert max_abs_diff(minplus_product(l, l),
                        minplus_product_blocked(l, l, 8)) < 1e-12


def test_the_tile_choice_respects_the_cache_size():
    for cache in (32 * 1024, 128 * 1024, 16 * 1024 * 1024):
        b = largest_block_for_cache(cache)
        assert working_set_bytes(b) <= cache < working_set_bytes(2 * b)
