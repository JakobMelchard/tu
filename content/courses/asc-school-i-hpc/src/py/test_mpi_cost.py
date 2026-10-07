"""Tests for mpi_cost.py.

The formulas are reproduced from Thakur, Rabenseifner and Gropp, "Optimization
of Collective Communication Operations in MPICH", Int. J. High Perf. Comput.
Appl. 19(1), 49-66, 2005 (doi:10.1177/1094342005051521), sections 4 and 5; the
Amdahl form from the ASC "intro & login" slide deck (Blaas-Schenner, 23 March
2026), and the ping-pong numbers from her "Best Practice for Code
Parallelization" deck.  Every test below either checks a formula against its
closed form or reproduces a published number.
"""

import math

import pytest

from mpi_cost import (
    Network,
    allgather_recursive_doubling,
    allgather_ring,
    allreduce_rabenseifner,
    allreduce_recursive_doubling,
    alltoall_bruck,
    alltoall_pairwise,
    amdahl,
    amdahl_limit,
    barrier,
    bcast_long,
    bcast_short,
    crossover,
    n_half,
    naive_send_loop,
    pt2pt_time,
    reduce_long,
    reduce_short,
)

NET = Network.from_latency_bandwidth(1.5, 12.0, 5.0)


# --------------------------------------------------------------- point to point

def test_network_units():
    """1.5 us and 12 GB/s in SI."""
    assert NET.alpha == pytest.approx(1.5e-6)
    assert 1.0 / NET.beta == pytest.approx(12e9)


def test_pt2pt_is_affine():
    t0 = pt2pt_time(NET, 0.0)
    t1 = pt2pt_time(NET, 1e6)
    assert t0 == pytest.approx(NET.alpha)
    assert t1 - t0 == pytest.approx(1e6 * NET.beta)


def test_n_half_is_where_the_two_terms_are_equal():
    n = n_half(NET)
    assert NET.alpha == pytest.approx(n * NET.beta)
    # 1.5 us * 12 GB/s = 18 kB
    assert n == pytest.approx(18_000.0)
    # and the total time there is exactly twice the latency
    assert pt2pt_time(NET, n) == pytest.approx(2 * NET.alpha)


def test_published_vsc3_pingpong_latency_ladder():
    """Blaas-Schenner's measured VSC-3 one-way latencies, MPI_Send, in us.

    Reproduced as a monotonicity statement, which is what the slide is actually
    teaching: each switch hop costs roughly half a microsecond, and every
    inter-node path is slower than every intra-node one.
    """
    intel = {"intra-socket": 0.3, "inter-socket": 0.7,
             "ib-edge": 1.4, "ib-leaf": 1.8, "ib-spine": 2.3}
    ladder = list(intel.values())
    assert ladder == sorted(ladder), "latency must grow along the path"
    assert intel["ib-edge"] > intel["inter-socket"] > intel["intra-socket"]
    # each extra switch level costs ~0.45 us on that machine
    for a, b in (("ib-edge", "ib-leaf"), ("ib-leaf", "ib-spine")):
        assert 0.3 < intel[b] - intel[a] < 0.6
    # a synchronous send over Open MPI cost up to 14-18 us on the same fabric,
    # i.e. an order of magnitude more than the standard send
    assert 14.0 / intel["ib-edge"] > 9.0


# ------------------------------------------------------------------ collectives

@pytest.mark.parametrize("p", [2, 4, 8, 16, 64, 1024])
def test_bcast_short_is_binomial_tree(p):
    n = 8.0
    assert bcast_short(NET, n, p) == pytest.approx(
        math.ceil(math.log2(p)) * (NET.alpha + n * NET.beta))


@pytest.mark.parametrize("p", [4, 16, 1024])
def test_bcast_long_bandwidth_term_is_two_over_p(p):
    """The long-message broadcast moves ~2n bytes, not n*lg(p)."""
    n = 1e7
    # isolate the bandwidth term by subtracting the latency term
    bw = bcast_long(NET, n, p) - (math.log2(p) + p - 1) * NET.alpha
    assert bw == pytest.approx(2.0 * (p - 1) / p * n * NET.beta)
    # and it beats the tree's n*lg(p)*beta for large n and large p
    assert bw < math.ceil(math.log2(p)) * n * NET.beta or p == 4


def test_allreduce_short_latency_term_has_ONE_lg_p():
    """The correction this module exists for.

    Recursive doubling costs lg(p)*alpha, not 2*lg(p)*alpha.  Reduce-then-Bcast,
    the naive implementation, is what costs two.
    """
    p = 1024
    latency_only = Network(alpha=NET.alpha, beta=0.0, gamma=0.0)
    t = allreduce_recursive_doubling(latency_only, 8.0, p)
    assert t == pytest.approx(math.log2(p) * NET.alpha)
    reduce_then_bcast = (reduce_short(latency_only, 8.0, p)
                         + bcast_short(latency_only, 8.0, p))
    assert reduce_then_bcast == pytest.approx(2 * math.log2(p) * NET.alpha)
    assert t < reduce_then_bcast


def test_allreduce_rabenseifner_latency_term_has_TWO_lg_p():
    p = 1024
    latency_only = Network(alpha=NET.alpha, beta=0.0, gamma=0.0)
    assert allreduce_rabenseifner(latency_only, 8.0, p) == pytest.approx(
        2 * math.log2(p) * NET.alpha)


def test_allreduce_algorithms_swap_places_with_message_size():
    """Recursive doubling wins for short messages, Rabenseifner for long ones."""
    p = 64
    assert (allreduce_recursive_doubling(NET, 8, p)
            < allreduce_rabenseifner(NET, 8, p))
    assert (allreduce_rabenseifner(NET, 10_000_000, p)
            < allreduce_recursive_doubling(NET, 10_000_000, p))
    x = crossover(allreduce_recursive_doubling, allreduce_rabenseifner, NET, p)
    assert 1.0 < x < 1e7


def test_reduce_long_matches_allreduce_rabenseifner_cost():
    """The paper gives the same expression for both (reduce-scatter + gather /
    + allgather)."""
    for p in (8, 256):
        assert reduce_long(NET, 1e6, p) == pytest.approx(
            allreduce_rabenseifner(NET, 1e6, p))


def test_collective_beats_a_hand_written_send_loop():
    """The claim in notes/09: ~100x in the latency term at p ~ 1000."""
    p = 1024
    latency_only = Network(alpha=NET.alpha, beta=0.0)
    ratio = (naive_send_loop(latency_only, 8, p)
             / bcast_short(latency_only, 8, p))
    assert ratio == pytest.approx((p - 1) / math.log2(p), rel=1e-9)
    assert 100 < ratio < 105
    # and at p = 4 the difference is 3 alpha vs 2 alpha: invisible in noise
    assert (naive_send_loop(latency_only, 8, 4)
            / bcast_short(latency_only, 8, 4)) == pytest.approx(1.5)


def test_batching_scalar_reductions():
    """Three Allreduce(1 double) vs one Allreduce(3 doubles) at p = 1024."""
    p = 1024
    three = 3 * allreduce_recursive_doubling(NET, 8, p)
    one = allreduce_recursive_doubling(NET, 24, p)
    assert one < three
    assert three / one > 2.9          # nearly a factor 3: it is all latency
    saved_per_step = three - one
    # 10^5 time steps: the saving is minutes, not microseconds
    assert saved_per_step * 1e5 > 1.0


def test_allgather_ring_vs_recursive_doubling():
    """Same bandwidth term, different latency term."""
    n_tot, p = 1e6, 64
    bw_rd = allgather_recursive_doubling(NET, n_tot, p) - math.ceil(math.log2(p)) * NET.alpha
    bw_ring = allgather_ring(NET, n_tot, p) - (p - 1) * NET.alpha
    assert bw_rd == pytest.approx(bw_ring)
    assert allgather_recursive_doubling(NET, n_tot, p) < allgather_ring(NET, n_tot, p)


def test_alltoall_short_and_long():
    p = 64
    assert alltoall_bruck(NET, 64.0, p) < alltoall_pairwise(NET, 1.0, p)
    # for large messages the pairwise exchange moves less data
    assert alltoall_pairwise(NET, 1e6, p) < alltoall_bruck(NET, 1e6 * p, p)


def test_barrier_is_pure_latency():
    for p in (2, 8, 1000):
        assert barrier(NET, p) == pytest.approx(math.ceil(math.log2(p)) * NET.alpha)


def test_removing_barriers_is_worth_something_measurable():
    """notes/16 quotes a production code that lost three barriers per iteration.

    The model only accounts for the barrier's own latency; the measured factor 6
    came mostly from the idle time barriers expose.  Assert the weaker, purely
    model-based statement and leave the measurement to the note.
    """
    p = 1024
    per_iteration = 3 * barrier(NET, p)
    assert per_iteration * 1e6 > 1.0        # > 1 s over 10^6 iterations


# ----------------------------------------------------------------------- Amdahl

def test_amdahl_convention_is_sequential_fraction():
    """f = 0 means perfect scaling; f = 1 means none.  If this test fails, the
    convention has been flipped somewhere."""
    assert amdahl(0.0, 100) == pytest.approx(100.0)
    assert amdahl(1.0, 100) == pytest.approx(1.0)
    assert amdahl(0.5, 2) == pytest.approx(1 / (0.5 + 0.25))


def test_amdahl_published_values():
    """The numbers quoted in notes/16, recomputed."""
    assert amdahl_limit(0.05) == pytest.approx(20.0)
    assert amdahl(0.05, 64) == pytest.approx(15.42, abs=0.01)
    assert amdahl(0.05, 64) / 64 == pytest.approx(0.241, abs=0.001)
    assert amdahl_limit(0.02) == pytest.approx(50.0)
    assert amdahl(0.02, 100) == pytest.approx(33.56, abs=0.01)


def test_amdahl_is_bounded_and_monotone():
    f = 0.03
    prev = 0.0
    for p in (1, 2, 4, 8, 1 << 20):
        s = amdahl(f, p)
        assert s > prev
        assert s < amdahl_limit(f)
        prev = s


def test_amdahl_rejects_nonsense():
    with pytest.raises(ValueError):
        amdahl(-0.1, 4)
    with pytest.raises(ValueError):
        amdahl(0.1, 0)


def test_crossover_returns_inf_when_the_long_algorithm_never_wins():
    assert crossover(bcast_short, bcast_short, NET, 16) == math.inf
