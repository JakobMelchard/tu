"""Test-writing patterns for numerical code (note 05).

Run: .venv/bin/python -m pytest src/py/test_testing_examples.py -v
"""
import math
import sys

import numpy as np
import pytest
from numpy.testing import assert_allclose, assert_array_almost_equal_nulp, assert_array_equal

import testing_examples as te


# ---------------------------------------------------------------- fixtures
@pytest.fixture
def rng():
    """Fresh, seeded generator per test: reproducible AND independent."""
    return np.random.default_rng(12345)


@pytest.fixture(scope="module")
def spd_matrix():
    """Expensive setup built once per module; tests must not mutate it."""
    rng = np.random.default_rng(0)
    A = rng.standard_normal((20, 20))
    return A @ A.T + 20 * np.eye(20)


@pytest.fixture
def config_file(tmp_path):
    """tmp_path is a built-in fixture: a fresh directory, removed later."""
    p = tmp_path / "run.cfg"
    p.write_text("dt = 0.01   # step\nT = 2.5\n\n")
    return p


# ---------------------------------------------------------------- basic assertions
def test_quadratic_simple_roots():
    assert te.solve_quadratic(1, -3, 2) == (1.0, 2.0)


def test_floats_need_tolerances():
    # 0.1 + 0.2 != 0.3 exactly; pytest.approx uses rel=1e-6 by default
    assert 0.1 + 0.2 == pytest.approx(0.3)
    assert te.trapezoid(np.sin, 0, math.pi, 1000) == pytest.approx(2.0, abs=1e-5)


def test_stable_quadratic_avoids_cancellation():
    x1, x2 = te.solve_quadratic(1, 1e8, 1)
    # naive formula would give x2 = 0 (catastrophic cancellation)
    assert x1 == pytest.approx(-1e8, rel=1e-12) and x2 == pytest.approx(-1e-8, rel=1e-8)


# ---------------------------------------------------------------- exceptions
@pytest.mark.parametrize("args, exc", [
    ((0, 1, 1), ValueError), ((1, 0, 1), ValueError)])
def test_quadratic_invalid(args, exc):
    with pytest.raises(exc):
        te.solve_quadratic(*args)


def test_error_message_is_checked():
    with pytest.raises(ZeroDivisionError, match="zero vector"):
        te.normalise([0, 0, 0])


def test_newton_non_convergence():
    with pytest.raises(RuntimeError, match="did not converge"):
        te.newton(lambda x: x**2 + 1, lambda x: 2 * x, 0.5, max_iter=5)   # no real root


# ---------------------------------------------------------------- parametrize
@pytest.mark.parametrize("n, expected_order", [(10, 2), (100, 2)])
def test_trapezoid_is_second_order(n, expected_order):
    """Halving h must divide the error by ~2^order."""
    exact = 2.0
    e1 = abs(te.trapezoid(np.sin, 0, math.pi, n) - exact)
    e2 = abs(te.trapezoid(np.sin, 0, math.pi, 2 * n) - exact)
    assert math.log2(e1 / e2) == pytest.approx(expected_order, abs=0.05)


@pytest.mark.parametrize("f", [lambda x: 0 * x + 3, lambda x: 2 * x - 1], ids=["const", "linear"])
def test_trapezoid_exact_for_polynomials_of_degree_le_1(f):
    assert te.trapezoid(f, 0, 3, 7) == pytest.approx(float(np.trapezoid(f(np.linspace(0, 3, 1000)), np.linspace(0, 3, 1000))), rel=1e-6)


@pytest.mark.parametrize("z", [[0, 0], [1, 2, 3], [1000, 1001], [-1e300, 0]])
def test_softmax_properties(z):
    s = te.softmax(z)
    assert s.sum() == pytest.approx(1.0) and (s >= 0).all() and np.isfinite(s).all()


# ---------------------------------------------------------------- numpy helpers
def test_normalise_with_numpy_testing():
    v = te.normalise([3, 4])
    assert_allclose(v, [0.6, 0.8], rtol=1e-15)             # tolerance-based
    assert_array_equal(te.normalise([0, 5]), [0.0, 1.0])   # exact where exactness is expected
    assert_array_almost_equal_nulp(np.linalg.norm(te.normalise([1e-150, 1e-150])), 1.0, nulp=2)


def test_against_reference_implementation(rng):
    x = rng.standard_normal(500)
    mean, var = te.mean_and_var(x)
    assert mean == pytest.approx(x.mean()) and var == pytest.approx(x.var(ddof=1))


def test_uses_module_fixture(spd_matrix):
    w = np.linalg.eigvalsh(spd_matrix)
    assert (w > 0).all()


# ---------------------------------------------------------------- property-based idea
def test_quadratic_roots_satisfy_vieta(rng):
    """Poor man's Hypothesis: many random inputs, check an invariant instead
    of a hard-coded answer.  (pip install hypothesis for the real thing.)"""
    for _ in range(200):
        a, x1, x2 = rng.uniform(0.5, 2), rng.uniform(-5, 5), rng.uniform(-5, 5)
        b, c = -a * (x1 + x2), a * x1 * x2
        r1, r2 = te.solve_quadratic(a, b, c)
        assert sorted([r1, r2]) == pytest.approx(sorted([x1, x2]), abs=1e-8)


# ---------------------------------------------------------------- fixtures for I/O, marks
def test_read_config(config_file):
    assert te.read_config(config_file) == {"dt": 0.01, "T": 2.5}


def test_monkeypatch_env(monkeypatch, tmp_path):
    monkeypatch.setenv("RUN_DIR", str(tmp_path))
    import os
    assert os.environ["RUN_DIR"] == str(tmp_path)     # undone after the test


@pytest.mark.skipif(sys.platform == "win32", reason="POSIX paths only")
def test_skip_marker_example(tmp_path):
    assert str(tmp_path).startswith("/")


@pytest.mark.xfail(reason="naive formula loses the small root", strict=True)
def test_naive_quadratic_fails():
    a, b, c = 1, 1e8, 1
    x2 = (-b + math.sqrt(b * b - 4 * a * c)) / (2 * a)
    assert x2 == pytest.approx(-1e-8, rel=1e-3)
