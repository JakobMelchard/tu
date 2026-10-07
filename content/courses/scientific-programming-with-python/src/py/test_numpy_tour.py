"""Tests for numpy_tour.py (note 02): layout, views, broadcasting, indexing, linalg, RNG."""
import numpy as np
import pytest
from numpy.testing import assert_allclose, assert_array_equal

import numpy_tour as nt


def test_strides_formula():
    for shape in [(3,), (2, 3), (4, 5, 6)]:
        assert nt.c_strides(shape, 8) == np.empty(shape).strides
    a = np.empty((3, 4), order="F")
    assert a.strides == (8, 24) and not a.flags.c_contiguous


def test_views_and_copies():
    d = nt.view_vs_copy_demo()
    assert d["slice_is_view"] and d["T_is_view"]
    assert not d["fancy_is_view"] and not d["mask_is_view"]
    assert d["a01_after_write"] == 100
    assert d["T_strides"] == d["a_strides"][::-1]
    assert nt.transpose_reshape_needs_copy()


def test_strided_windows():
    x = np.arange(6.0)
    assert_allclose(nt.moving_average_strided(x, 3), [1, 2, 3, 4])
    assert_array_equal(nt.as_strided_windows(x, 2), [[0, 1], [1, 2], [2, 3], [3, 4], [4, 5]])


def test_dtype_pitfalls():
    d = nt.dtype_pitfalls()
    assert d["int8_overflow"] == -128 and d["float32_absorbs_1e-8"]
    assert d["int_plus_float_dtype"] == "float64" and d["float_into_int_truncates"] == 2
    assert d["bool_sum_dtype"] == "int64"


@pytest.mark.parametrize("shapes", [
    [(3, 1), (1, 4)], [(5, 4), (4,)], [(2, 3, 4), (3, 1)], [(1,), (7, 1, 2)], [(), (3,)]])
def test_broadcast_shape_matches_numpy(shapes):
    assert nt.broadcast_shape(*shapes) == np.broadcast_shapes(*shapes)


def test_broadcast_shape_rejects():
    with pytest.raises(ValueError):
        nt.broadcast_shape((3,), (4,))
    with pytest.raises(ValueError):
        np.broadcast_shapes((3,), (4,))


def test_broadcast_helpers():
    x, y = np.arange(3.0), np.arange(4.0)
    assert_allclose(nt.outer_via_broadcast(x, y), np.outer(x, y))
    Z = nt.standardise_columns(np.random.default_rng(0).random((50, 3)) * 10)
    assert_allclose(Z.mean(axis=0), 0, atol=1e-12)
    assert_allclose(Z.std(axis=0), 1)


def test_fancy_indexing():
    d = nt.fancy_indexing_demo()
    assert d["pairs"] == [1, 13] and d["grid"] == [[1, 3], [11, 13]]
    assert d["mask_count"] == 9 and d["where"] == 0 + 7 + 14
    assert nt.assign_with_fancy_index_pitfall() == [1, 1, 0, 2, 1, 0]


def test_pairwise_distances_agree():
    P = np.random.default_rng(2).random((30, 3))
    D = nt.pairwise_dist_loop(P)
    assert_allclose(nt.pairwise_dist_vec(P), D)
    assert_allclose(nt.pairwise_dist_gram(P), D, atol=1e-7)   # cancellation-limited


def test_ufuncs():
    d = nt.ufunc_demo()
    assert d["reduce"] == 15 and d["accumulate"] == [1, 3, 6, 10, 15]
    assert d["outer"] == [[10, 20], [20, 40]] and d["out_param"] == [2, 4, 6, 8, 10]
    assert d["where"][:2] == [0, 0] and d["reduceat"] == [3, 12]


def test_einsum_against_linalg():
    rng = np.random.default_rng(3)
    A, B, v = rng.random((4, 4)), rng.random((4, 4)), rng.random(4)
    d = nt.einsum_demo(A, B, v)
    assert_allclose(d["trace"], np.trace(A))
    assert_allclose(d["matmul"], A @ B)
    assert_allclose(d["matvec"], A @ v)
    assert_allclose(d["quadratic_form"], v @ A @ v)
    assert_allclose(d["hadamard"], A * B)
    As, vs = rng.random((5, 3, 3)), rng.random((5, 3))
    assert_allclose(nt.batched_matvec(As, vs), (As @ vs[..., None])[..., 0])


def test_linalg():
    d = nt.linalg_demo(np.random.default_rng(0))
    assert d["residual"] < 1e-10 and d["eig_recon_err"] < 1e-10
    assert_allclose(d["lstsq_coef"], [1, -2, 0.5], atol=0.02)
    assert d["det_sign_logdet"][0] == 1.0


def test_random_generator():
    d = nt.random_demo(0)
    assert d["child_differ"] and d["same_seed_same_stream"]
    assert len(set(d["choice"].tolist())) == 3 and d["ints"].max() < 10


def test_growth_strategies_agree():
    assert_array_equal(nt.grow_by_append(50), nt.grow_preallocated(50))
