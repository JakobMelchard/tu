"""Tests for scipy_tour.py (note 03): one test per subpackage, against known results."""
import numpy as np
import pytest
from numpy.testing import assert_allclose

import scipy_tour as st


@pytest.fixture
def rng():
    return np.random.default_rng(0)


def test_integrate():
    val, err, exact = st.quad_gaussian()
    assert abs(val - exact) < err < 1e-6
    _, ivp_err = st.solve_ivp_oscillator()
    assert ivp_err < 1e-6
    tr, si, exact = st.trapezoid_vs_simpson(21)
    assert abs(si - exact) < abs(tr - exact) < 1e-2


@pytest.mark.parametrize("method", ["BFGS", "Nelder-Mead", "L-BFGS-B", "CG"])
def test_minimize(method):
    r = st.minimize_rosenbrock(method)
    assert r.success and np.allclose(r.x, [1, 1], atol=1e-3)


def test_roots_and_fit(rng):
    b, n = st.root_transcendental()
    assert abs(b - n) < 1e-10 and abs(np.cos(b) - b) < 1e-12
    popt, perr, true = st.curve_fit_decay(rng)
    assert_allclose(popt, true, atol=0.1)
    assert (perr > 0).all()


def test_interpolation():
    errs, spline = st.interpolation_demo()
    assert errs["spline"] < errs["linear"] < errs["poly10"]      # Runge
    assert abs(spline(0.0) - 1.0) < 1e-12                        # interpolates the node


def test_sparse_poisson():
    us, ud, exact, nnz = st.poisson_solve(100)
    assert nnz == 3 * 100 - 2
    assert_allclose(us, ud, rtol=1e-10)
    assert np.abs(us - exact).max() < 1e-3        # O(h^2) discretisation error
    A = st.laplacian_1d(4)
    assert_allclose(A.toarray(), [[2, -1, 0, 0], [-1, 2, -1, 0], [0, -1, 2, -1], [0, 0, -1, 2]])


def test_linalg(rng):
    d = st.linalg_demo(rng)
    assert d["lu_err"] < 1e-12 and d["chol_err"] < 1e-10 and d["expm_zero_err"] == 0
    assert_allclose(d["rot"], [[0, 1], [-1, 0]], atol=1e-12)
    assert d["eigh_pos"]


def test_fft(rng):
    peaks, df = st.fft_peaks()
    assert peaks == [50.0, 120.0] and df == 0.5
    assert st.convolution_theorem(rng) < 1e-10


def test_stats(rng):
    d = st.stats_demo(rng)
    assert abs(d["mu"] - 2.0) < 0.05 and abs(d["sigma"] - 0.5) < 0.05
    assert d["ttest_p"] < 1e-6 and d["ks_p"] > 0.01
    assert abs(d["q95"] - 1.6449) < 1e-3 and abs(d["cdf_of_ppf"] - 0.3) < 1e-12


def test_signal():
    rms, npeaks = st.lowpass_demo()
    assert rms < 0.02 and npeaks == 20
