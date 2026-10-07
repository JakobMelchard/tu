"""Tests for ordering.py: fill-in and orderings, [S4] §4.6 (CSE).

Known results: the [S4] Ex. 4.37 non-zero counts, and scipy's
reverse Cuthill-McKee as a cross-check.
"""
import numpy as np
import scipy.sparse
from scipy.sparse.csgraph import reverse_cuthill_mckee as scipy_rcm

from banded import bandwidths
from ordering import (adjacency_graph, cuthill_mckee, reverse_cuthill_mckee,
                      pseudo_peripheral_node, minimum_degree,
                      symbolic_cholesky_nnz, poisson_2d_pattern)


def spd(n, seed=0, band=None):
    r = np.random.default_rng(seed)
    M = r.standard_normal((n, n))
    A = M @ M.T + n * np.eye(n)
    if band is not None:
        A = np.triu(np.tril(A, band), -band)
        A += np.diag(2 * n * np.ones(n))
    return A


def test_orderings_are_permutations():
    A = poisson_2d_pattern(8)
    for order in (cuthill_mckee(A), reverse_cuthill_mckee(A), minimum_degree(A)):
        np.testing.assert_array_equal(np.sort(order), np.arange(A.shape[0]))


def test_cuthill_mckee_reduces_bandwidth():
    A = poisson_2d_pattern(10)
    order = reverse_cuthill_mckee(A)
    assert bandwidths(A[np.ix_(order, order)])[0] <= bandwidths(A)[0]


def test_symbolic_count_matches_a_real_factorisation():
    A = spd(30, seed=11, band=3)
    C = np.linalg.cholesky(A)
    assert symbolic_cholesky_nnz(A) >= int((np.abs(C) > 1e-12).sum())


def test_s4_example_4_37_fill_in_numbers():
    """[S4] Ex. 4.37: gallery('poisson',30), 900 x 900, 5 non-zeros per row.

    [S4] reports 27029 / 19315 / 10042 non-zeros in the Cholesky factor for the
    lexicographic, reverse Cuthill-McKee and (approximate) minimum-degree
    orderings.  The first two are reproduced exactly.  The third is close but
    not equal: [S4] says *approximate* minimum degree, whose tie-breaking
    differs from the exact greedy algorithm of [S4] Alg. 14 implemented here.
    """
    A = poisson_2d_pattern(30)
    assert A.shape == (900, 900)
    assert int((A != 0).sum()) == 4380
    assert symbolic_cholesky_nnz(A) == 27029
    assert symbolic_cholesky_nnz(A, reverse_cuthill_mckee(A)) == 19315
    md = symbolic_cholesky_nnz(A, minimum_degree(A))
    assert 9500 < md < 11500                           # [S4]: 10042, ours 10351
    assert md < 19315                                  # and still much better than RCM


def test_adjacency_graph_is_symmetric():
    A = poisson_2d_pattern(5)
    g = adjacency_graph(A)
    for i, row in enumerate(g):
        for j in row:
            assert i in g[j]


def test_pseudo_peripheral_node_is_an_end_or_a_corner():
    """[S4] §4.6.2: start RCM at a node of maximal eccentricity."""
    n = 9
    T = np.eye(n) + np.eye(n, k=1) + np.eye(n, k=-1)       # path graph
    assert pseudo_peripheral_node(T) in (0, n - 1)
    m = 6
    corners = {0, m - 1, m * (m - 1), m * m - 1}           # 2-D grid, lexicographic
    assert pseudo_peripheral_node(poisson_2d_pattern(m)) in corners


def test_rcm_fill_matches_scipy():
    """Same fill-in and bandwidth as scipy.sparse.csgraph.reverse_cuthill_mckee."""
    for m in (5, 10, 30):
        A = poisson_2d_pattern(m)
        ours = reverse_cuthill_mckee(A)
        ref = scipy_rcm(scipy.sparse.csr_matrix(A), symmetric_mode=True)
        assert symbolic_cholesky_nnz(A, ours) == symbolic_cholesky_nnz(A, ref)
        assert bandwidths(A[np.ix_(ours, ours)]) == bandwidths(A[np.ix_(ref, ref)])
