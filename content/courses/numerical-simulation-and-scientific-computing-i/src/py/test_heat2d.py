"""Explicit and implicit Euler for the 2D heat equation against the exact solution.

Stability limit r <= 1/4 in 2D and first order in dt [S23 ch. 9-10].
"""
import numpy as np

from heat2d import cfl_limit, exact, explicit_euler, implicit_euler


def test_explicit_stable_matches_exact():
    X, Y, U, _ = explicit_euler(32, 0.24, 0.05)
    assert np.max(np.abs(U - exact(X, Y, 0.05))) < 2e-3


def test_explicit_beyond_cfl_blows_up():
    _, _, U, _ = explicit_euler(32, 0.30, 0.05)
    assert not np.isfinite(U).all() or np.max(np.abs(U)) > 1e3


def test_implicit_stable_for_large_dt_and_first_order_in_time():
    h = 1 / 32
    errs = []
    for k in (16, 8, 4):
        X, Y, U, _ = implicit_euler(32, k * cfl_limit(h), 0.05)
        errs.append(np.max(np.abs(U - exact(X, Y, 0.05))))
    assert errs[0] < 2e-2 and errs[0] > errs[1] > errs[2]   # error shrinks roughly linearly with dt
    assert 1.5 < errs[0] / errs[1] < 2.5
