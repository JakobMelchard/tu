import numpy as np
import pytest

from ir_toy import (IRBasis, basis_size_vs_lambda, composite_gauss, logistic_kernel, matsubara,
                    rho_coefficients, single_pole)

BETA, WMAX = 10.0, 10.0


@pytest.fixture(scope="module")
def B():
    return IRBasis(BETA, WMAX, eps=1e-8)


def test_kernel_is_stable_and_matches_naive_form():
    t = np.array([0.0, 1.3, 10.0])
    w = np.array([-50.0, -0.3, 0.0, 2.0, 50.0])
    naive = np.exp(-np.outer(t, w)) / (1 + np.exp(-BETA * w))[None, :]
    K = logistic_kernel(t, w, BETA)
    assert np.all(np.isfinite(K))
    assert np.allclose(K, naive)
    # G(0) + G(beta) = -int rho: K(0, w) + K(beta, w) = 1
    assert np.allclose(K[0] + K[-1], 1.0)


def test_basis_functions_orthonormal_on_independent_quadrature(B):
    t, wt = composite_gauss(np.linspace(0, BETA, 201), 12)
    U = B.u(t)
    G = (U * wt) @ U.T
    assert np.allclose(G, np.eye(B.size), atol=1e-6)


def test_parity_of_basis_functions(B):
    t = np.linspace(0, BETA, 57)
    U, Ur = B.u(t), B.u(BETA - t)
    for l in range(B.size):
        assert np.allclose(Ur[l], (-1) ** l * U[l], atol=1e-7)


def test_singular_values_decay_and_size_grows_like_log_lambda(B):
    r = B.s_all / B.s_all[0]
    assert np.all(np.diff(r[:B.size]) < 0)
    assert r[B.size] <= 1e-8 < r[B.size - 1]
    L10, L100, L1000 = basis_size_vs_lambda([10, 100, 1000])
    assert L10 < L100 < L1000 < 2 * L100               # not 10x: log(Lambda)
    assert 8 <= L100 - L10 <= 25 and 8 <= L1000 - L100 <= 25


def test_single_pole_coefficients_closed_form(B):
    """rho = delta(w - e) => G_l = -s_l v_l(e); projection of the closed form agrees."""
    e = 0.7
    g_tau, _ = single_pole(e, BETA)
    Gl_proj = B.project(g_tau)
    Gl_exact = -B.s[:B.size] * B.v(np.array([e]))[:, 0]
    assert np.allclose(Gl_proj, Gl_exact, atol=1e-10)


@pytest.mark.parametrize("e", [-3.0, 0.0, 0.7, 8.0])
def test_sparse_tau_sampling_reconstructs_single_pole(B, e):
    g_tau, _ = single_pole(e, BETA)
    tp = B.tau_sampling_points()
    assert len(tp) == B.size
    F = B.u(tp)
    assert np.linalg.cond(F) < 50
    Gl = B.fit(F, g_tau(tp))
    dense = np.linspace(0, BETA, 2001)
    assert np.max(np.abs(Gl @ B.u(dense) - g_tau(dense))) < 1e-7


def test_extrema_rule_and_uniform_grid_conditioning(B):
    tx = B.tau_sampling_points("extrema")
    assert len(tx) == B.size and np.all(np.diff(tx) > 0)
    assert np.linalg.cond(B.u(tx)) < 50
    # L equally spaced points: the fit is badly conditioned (the basis crowds at the ends)
    assert np.linalg.cond(B.u(np.linspace(0, BETA, B.size))) > 1e3
    g_tau, _ = single_pole(1.3, BETA)
    Gl = B.fit(B.u(tx), g_tau(tx))
    dense = np.linspace(0, BETA, 1001)
    assert np.max(np.abs(Gl @ B.u(dense) - g_tau(dense))) < 1e-7


@pytest.mark.parametrize("e", [-3.0, 0.7])
def test_sparse_matsubara_sampling_reconstructs_single_pole(B, e):
    g_tau, g_iw = single_pole(e, BETA)
    ns = B.matsubara_sampling_points()
    assert len(ns) >= B.size
    F = B.uhat(ns)
    assert np.linalg.cond(F) < 100
    Gl = B.fit(F, g_iw(ns))
    nn = np.arange(-3000, 3000)
    assert np.max(np.abs(Gl @ B.uhat(nn) - g_iw(nn))) < 1e-7
    # the same coefficients describe G(tau): one object, two representations
    assert np.allclose(Gl, B.project(g_tau), atol=1e-7)


def test_uhat_is_fourier_transform_of_u(B):
    t, wt = composite_gauss(np.linspace(0, BETA, 401), 16)
    n = np.array([-7, -1, 0, 3, 20])
    direct = (B.u(t) * wt) @ np.exp(1j * np.outer(t, matsubara(n, BETA)))
    assert np.allclose(direct, B.uhat(n), atol=1e-7)
    # even l purely imaginary, odd l purely real (up to the Nystrom roundoff ~ eps_mach s_0/s_l)
    uh = B.uhat(n)
    assert np.allclose(uh[0::2].real, 0, atol=1e-7) and np.allclose(uh[1::2].imag, 0, atol=1e-7)


def test_particle_hole_symmetric_rho_has_no_odd_coefficients(B):
    rho = lambda w: np.exp(-(w - 1.5) ** 2) + np.exp(-(w + 1.5) ** 2)
    Gl = -B.s[:B.size] * rho_coefficients(B, rho)
    assert np.max(np.abs(Gl[1::2])) < 1e-12 * np.max(np.abs(Gl))


def test_against_sparse_ir_if_installed():
    sparse_ir = pytest.importorskip("sparse_ir")
    ref = sparse_ir.FiniteTempBasis("F", BETA, WMAX, eps=1e-8)
    ours = IRBasis(BETA, WMAX, eps=1e-8)
    n = 10
    assert np.allclose(ours.s_all[:n] / ours.s_all[0], ref.s[:n] / ref.s[0], rtol=1e-6)
