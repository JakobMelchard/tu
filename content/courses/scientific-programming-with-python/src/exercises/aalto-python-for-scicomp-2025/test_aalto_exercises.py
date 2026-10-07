"""Tests for the Aalto *Python for Scientific Computing* [S41] practice set
(note 11; notes 02, 03, 04, 08).

Each test names the lesson, so a library change that makes the lesson untrue
fails here.  Verified against the versions in ``../../../refs/SOURCES.md`` S40.
Two processes and small sample counts keep the course suite well under a minute.
"""
from __future__ import annotations

import numpy as np
import pytest
import aalto_exercises as ex


def test_only_basic_slicing_gives_a_view() -> None:
    """Task 1: slices alias, fancy/boolean indexing and copy() do not."""
    r = ex.views_and_copies()
    assert r["basic slice"] is True
    assert not any(r[k] for k in ("fancy index", "boolean mask", "explicit copy"))


def test_star_is_not_matmul() -> None:
    """Task 2: for square operands both are legal and they differ."""
    a = np.array([[1.0, 2.0], [3.0, 4.0]])
    r = ex.elementwise_vs_matrix(a, a)
    assert r["elementwise"].tolist() == [[1.0, 4.0], [9.0, 16.0]]
    assert r["matrix"].tolist() == [[7.0, 10.0], [15.0, 22.0]]
    assert np.array_equal(r["matrix"], r["dot_is_matmul_in_2d"])


def test_axis_names_the_axis_that_disappears() -> None:
    """Task 2: the shape rule, including keepdims."""
    r = ex.reduce_along_axis(np.arange(12).reshape(3, 4))
    assert r == {"axis=None": (), "axis=0": (4,), "axis=1": (3,),
                 "axis=1, keepdims": (3, 1)}


def test_out_and_inplace_avoid_the_temporary() -> None:
    """Task 3."""
    assert all(ex.without_temporaries(np.arange(6.0)).values())


def test_agg_and_transform_differ_only_in_shape() -> None:
    """Task 4: agg is one row per group, transform one row per input row, and
    pandas' std defaults to ddof=1 where numpy's defaults to 0."""
    df = ex.sample_measurements(seed=2026, n=240)
    r = ex.group_statistics(df)
    assert r["rows_in_agg"] == 3 and r["rows_in_transform"] == 240
    assert r["groups"] == ["east", "north", "south"]
    assert r["centred_group_means_are_zero"] and r["std_uses_ddof_1"]
    assert df["value"].std() != pytest.approx(np.std(df["value"].to_numpy()))


def test_quad_returns_a_pair_and_its_error_estimate_is_honest() -> None:
    """Task 5."""
    value, abserr, true_err = ex.quad_against_the_closed_form()
    assert value == pytest.approx(1.0, abs=1e-10)
    assert true_err <= abserr


def test_sparse_stores_only_the_diagonals() -> None:
    """Task 5: 3n - 2 stored entries for a tridiagonal n x n matrix."""
    r = ex.sparse_tridiagonal(500)
    assert r["shape"] == (500, 500)
    assert r["stored"] == 3 * 500 - 2
    assert r["density"] < 0.01
    assert r["matvec_matches_dense"]


def test_pi_on_a_process_pool_is_accurate_and_reproducible() -> None:
    """Task 6: spawned child seeds make a parallel Monte Carlo repeatable."""
    first = ex.pi_parallel(n=200_000, workers=2, seed=7)
    assert first == pytest.approx(np.pi, abs=0.02)
    assert ex.pi_parallel(n=200_000, workers=2, seed=7) == first


def test_cpu_count_is_hardware_not_allocation() -> None:
    """Task 6: the numbers Pool() would default to, and the ones you should
    actually pass on a shared machine."""
    r = ex.available_cpus()
    assert r["mp.cpu_count"] >= 1
    assert r["sched_getaffinity"] is None or r["sched_getaffinity"] >= 1
    assert set(r) == {"mp.cpu_count", "os.cpu_count", "sched_getaffinity",
                      "SLURM_CPUS_PER_TASK"}


def test_module_runs_as_a_script(capsys) -> None:
    ex.main()
    out = capsys.readouterr().out
    assert "shares memory" in out and "pi on 2 processes" in out
