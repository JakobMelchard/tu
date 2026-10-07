"""Tests for the Scientific Python Lectures [S39] practice set
(note 11; notes 07, 09).

Each test states the lesson the exercise exists to teach, so a change in SciPy
that makes the lesson untrue fails here rather than going unnoticed.
Verified against SciPy 1.18.1 / NumPy 2.5.3 (``../../../refs/SOURCES.md`` S40).
"""
from __future__ import annotations

import ctypes

import numpy as np
import pytest
import spl_exercises as ex


def test_analytic_gradient_cuts_function_evaluations() -> None:
    """Task 1: `jac` is worth roughly (n + 1)x in nfev, and Newton-CG demands it."""
    r = ex.gradient_pays_for_itself()
    for method in ("CG", "BFGS"):
        assert r[method]["nfev_with_jac"] < r[method]["nfev_without_jac"]
    assert r["Newton-CG"]["nfev_without_jac"] == -1, "Newton-CG should refuse"
    for method in r:
        assert r[method]["f"] == pytest.approx(0.0, abs=1e-12)


def test_gradient_method_stalls_on_a_flat_minimum() -> None:
    """Task 2: BFGS stops on a numerically zero gradient while still far out;
    the derivative-free methods reach the minimum."""
    r = ex.flat_minimum_comparison()
    assert r["BFGS"][1] > 0.0, "BFGS is expected to stop above the minimum"
    assert r["Nelder-Mead"][1] == pytest.approx(0.0, abs=1e-12)
    assert r["Powell"][1] == pytest.approx(0.0, abs=1e-12)
    assert r["BFGS"][0] > r["Nelder-Mead"][0]


def test_curve_fit_is_multimodal_in_the_frequency() -> None:
    """Task 3: only the initial guess at the true frequency converges."""
    sse = ex.curve_fit_needs_the_right_frequency(seed=0)
    assert sse[3.0] < 1.0
    assert sse[1.0] > 10.0 and sse[2.0] > 10.0


def test_slsqp_inequality_sign_convention() -> None:
    """Task 4: `ineq` means fun(x) >= 0, so the optimum lands on x + y = 2."""
    x, fval = ex.constrained_box()
    assert x[0] + x[1] == pytest.approx(2.0, abs=1e-6)
    assert x == pytest.approx([1.5, 0.5], abs=1e-6)
    assert fval == pytest.approx(4.5, abs=1e-6)


def test_ctypes_without_restype_is_silently_wrong() -> None:
    """Task 5: the failure mode is a wrong number, not an exception."""
    raw, declared = ex.undeclared_vs_declared(4.0)
    assert declared == pytest.approx(2.0)
    assert isinstance(raw, int) and raw != 2

    lib = ex.libm()
    lib.hypot.argtypes = [ctypes.c_double, ctypes.c_double]
    lib.hypot.restype = ctypes.c_double
    assert lib.hypot(3.0, 4.0) == pytest.approx(5.0)


def test_transpose_is_a_free_column_major_view() -> None:
    """Task 6: handing an array to a column-major callee costs nothing if you
    transpose; `asfortranarray` copies."""
    d = ex.column_major_handoff(np.ones((2, 3)))
    assert d["c_contiguous"] and d["transpose_is_f_contiguous"]
    assert d["transpose_shares_memory"]
    assert d["asfortranarray_copies"]
    assert d["strides"] == (24, 8) and d["transpose_strides"] == (8, 24)


def test_module_runs_as_a_script(capsys) -> None:
    ex.main()
    out = capsys.readouterr().out
    assert "gradient pays for itself" in out and "ctypes sqrt" in out
