"""Toy intermediate representation (IR) of fermionic Green's functions.

Note 03 (IR basis). Discretised singular value expansion (SVE) of the logistic kernel

    G(tau) = - int dw K(tau, w) rho(w),   K(tau, w) = e^{-tau w} / (1 + e^{-beta w}),
    tau in [0, beta],  w in [-wmax, wmax],  Lambda = beta * wmax,

  K(tau, w) = sum_l u_l(tau) s_l v_l(w)       (SVE, [S10, S13])
  G(tau)    = sum_l G_l u_l(tau),  G_l = -s_l rho_l,  rho_l = int v_l rho.

Steps: composite Gauss-Legendre quadrature graded towards tau = 0, beta and w = 0;
SVD of W_tau^{1/2} K W_w^{1/2}; Nystrom extension to evaluate u_l, v_l and the
Matsubara transforms uhat_l(i nu) off the quadrature grid; sparse sampling points
at the sign changes of the next basis function, as in sparse-ir [S12, S13, S14].

This is a teaching toy in double precision. sparse-ir [S14] computes the same
basis to ~1e-15 with extended precision and piecewise Legendre bookkeeping; use it
for real work (`pip install sparse-ir`).

Run `python ir_toy.py`.
"""
from __future__ import annotations

import numpy as np


def logistic_kernel(tau, w, beta: float) -> np.ndarray:
    """K(tau, w) = e^{-tau w}/(1+e^{-beta w}), evaluated without overflow."""
    tau, w = np.broadcast_arrays(np.asarray(tau, float)[:, None], np.asarray(w, float)[None, :])
    pos = w >= 0
    out = np.empty(tau.shape)
    out[pos] = np.exp(-tau[pos] * w[pos]) / (1.0 + np.exp(-beta * w[pos]))
    wn, tn = w[~pos], tau[~pos]
    out[~pos] = np.exp((beta - tn) * wn) / (1.0 + np.exp(beta * wn))
    return out


def composite_gauss(breaks, n: int):
    """Gauss-Legendre with n nodes on each panel [breaks[i], breaks[i+1]]."""
    x, w = np.polynomial.legendre.leggauss(n)
    a, b = np.asarray(breaks[:-1]), np.asarray(breaks[1:])
    nodes = ((b - a)[:, None] * (x[None, :] + 1) / 2 + a[:, None]).ravel()
    weights = ((b - a)[:, None] * w[None, :] / 2).ravel()
    return nodes, weights


def _graded(J: int):
    """Breakpoints on [0, 1] refined geometrically towards 0: 0, 2^-J, ..., 1/2, 1."""
    return np.concatenate([[0.0], 2.0 ** -np.arange(J, -1, -1)])


def matsubara(n, beta: float, statistics: str = "F") -> np.ndarray:
    """nu_n = (2n+1) pi / beta (fermions) or 2n pi / beta (bosons)."""
    n = np.asarray(n)
    return (2 * n + 1) * np.pi / beta if statistics == "F" else 2 * n * np.pi / beta


class IRBasis:
    """Discretised IR basis for fermions at inverse temperature beta, cutoff wmax."""

    def __init__(self, beta: float, wmax: float, eps: float = 1e-8, nodes_per_panel: int = 16):
        self.beta, self.wmax, self.eps = beta, wmax, eps
        lam = beta * wmax
        J = int(np.ceil(np.log2(max(lam, 2.0)))) + 4
        g = _graded(J)
        # tau: refine towards both ends (functions vary on scale 1/wmax there)
        half = beta / 2 * g
        self.tau_breaks = np.unique(np.concatenate([half, beta - half]))
        # omega: refine towards 0 (functions vary on scale 1/beta there)
        self.w_breaks = np.unique(np.concatenate([-wmax * g, wmax * g]))
        self.tau, self.wt = composite_gauss(self.tau_breaks, nodes_per_panel)
        self.w, self.ww = composite_gauss(self.w_breaks, nodes_per_panel)
        A = np.sqrt(self.wt)[:, None] * logistic_kernel(self.tau, self.w, beta) * np.sqrt(self.ww)[None, :]
        U, s, Vt = np.linalg.svd(A, full_matrices=False)
        # fix the sign convention u_l(0) > 0 ... via the first quadrature node
        sgn = np.sign(U[0, :])
        U, Vt = U * sgn, (Vt.T * sgn).T
        self.s_all = s
        self.size = int(np.sum(s / s[0] > eps))
        self.s = s[:self.size + 1]            # keep one extra for sampling points
        self._U = U[:, :self.size + 1]
        self._V = Vt[:self.size + 1].T

    # --- basis functions (Nystrom extension of the discrete singular vectors) ---
    def u(self, tau, extra: bool = False) -> np.ndarray:
        """u_l(tau), shape (L, len(tau)); int_0^beta u_l u_m dtau = delta_lm."""
        L = self.size + int(extra)
        K = logistic_kernel(tau, self.w, self.beta)
        return ((K * np.sqrt(self.ww)) @ self._V[:, :L] / self.s[:L]).T

    def v(self, w) -> np.ndarray:
        """v_l(w), shape (L, len(w))."""
        K = logistic_kernel(self.tau, w, self.beta)      # (ntau, nw)
        return ((self._U[:, :self.size] * np.sqrt(self.wt)[:, None]).T @ K) / self.s[:self.size, None]

    def uhat(self, n, extra: bool = False) -> np.ndarray:
        """uhat_l(i nu_n) = int_0^beta e^{i nu tau} u_l(tau) dtau, shape (L, len(n)).

        Uses the exact transform of the kernel, int_0^beta e^{i nu tau} K(tau, w) dtau
        = 1/(w - i nu) for fermionic nu (derived in note 03).
        """
        L = self.size + int(extra)
        nu = matsubara(n, self.beta)
        Khat = 1.0 / (self.w[None, :] - 1j * nu[:, None])
        return ((Khat * np.sqrt(self.ww)) @ self._V[:, :L] / self.s[:L]).T

    # --- sparse sampling ---
    def tau_sampling_points(self, rule: str = "roots") -> np.ndarray:
        """L sampling times.

        rule="roots":   the L roots of u_L (u_l has exactly l roots); Gauss-like.
        rule="extrema": the L extrema of u_{L-1}, the two boundary ones moved to the
                        midpoint between the boundary and the nearest root (sparse-ir
                        paper [S13]). Li et al. [S12] use midpoints of the roots of
                        u_{L-1} and 0, beta. All three interleave; conditioning is O(1-10).
        """
        grid = np.linspace(0, self.beta, 20001)
        if rule == "roots":
            f = self.u(grid, extra=True)[self.size]
            i = np.nonzero(np.sign(f[:-1]) != np.sign(f[1:]))[0]
            # linear interpolation inside the bracketing interval
            return grid[i] - f[i] * (grid[i + 1] - grid[i]) / (f[i + 1] - f[i])
        f = self.u(grid)[self.size - 1]
        roots = grid[np.nonzero(np.sign(f[:-1]) != np.sign(f[1:]))[0]]
        df = np.diff(f)
        interior = grid[1:-1][np.sign(df[:-1]) != np.sign(df[1:])]
        return np.concatenate([[roots[0] / 2], interior, [(self.beta + roots[-1]) / 2]])

    def matsubara_sampling_points(self, nmax: int | None = None) -> np.ndarray:
        """Fermionic n at the sign changes of the non-vanishing part of uhat_L,
        mirrored to n -> -n-1 (nu -> -nu). Returns sorted integer n."""
        nmax = nmax or int(20 * self.beta * self.wmax / np.pi) + 50
        n = np.arange(nmax)
        f = self.uhat(n, extra=True)[self.size]
        f = f.imag if self.size % 2 == 0 else f.real    # u_l(beta-tau) = (-1)^l u_l(tau)
        i = np.nonzero(np.sign(f[:-1]) != np.sign(f[1:]))[0] + 1
        pos = np.unique(np.concatenate([[0], i]))
        return np.sort(np.concatenate([-pos - 1, pos]))

    def fit(self, F: np.ndarray, values: np.ndarray) -> np.ndarray:
        """Least-squares IR coefficients from values = F^T G_l at the sampling points."""
        return np.linalg.lstsq(F.T, values, rcond=None)[0].real

    def project(self, g_tau) -> np.ndarray:
        """G_l = int_0^beta u_l(tau) G(tau) dtau by quadrature; g_tau is a callable."""
        return (self._U[:, :self.size] * np.sqrt(self.wt)[:, None]).T @ g_tau(self.tau)


def single_pole(eps_pole: float, beta: float):
    """rho = delta(w - eps): closed forms G(tau) = -K(tau, eps), G(i nu) = 1/(i nu - eps)."""
    g_tau = lambda t: -logistic_kernel(t, [eps_pole], beta)[:, 0]
    g_iw = lambda n: 1.0 / (1j * matsubara(n, beta) - eps_pole)
    return g_tau, g_iw


def rho_coefficients(basis: IRBasis, rho) -> np.ndarray:
    """rho_l = int v_l(w) rho(w) dw on the basis' own w quadrature."""
    return basis.v(basis.w) @ (basis.ww * rho(basis.w))


def uniform_grid_points_needed(g_tau, beta: float, tol: float) -> int:
    """Smallest uniform tau grid (doubling) on which linear interpolation of G
    reaches max error <= tol: the naive storage the IR is compared against."""
    dense = np.linspace(0, beta, 200001)
    exact = g_tau(dense)
    n = 16
    while n < 10 ** 6:
        grid = np.linspace(0, beta, n)
        if np.max(np.abs(np.interp(dense, grid, g_tau(grid)) - exact)) <= tol:
            return n
        n *= 2
    return n


def basis_size_vs_lambda(lams, eps: float = 1e-8):
    return [IRBasis(1.0, float(l), eps).size for l in lams]


def demo() -> None:
    beta, wmax = 10.0, 10.0
    B = IRBasis(beta, wmax, eps=1e-8)
    print(f"beta = {beta}, wmax = {wmax}, Lambda = {beta * wmax:.0f}, quadrature "
          f"{len(B.tau)} x {len(B.w)}; basis size L(eps=1e-8) = {B.size}")
    print("s_l / s_0 every 5th:", " ".join(f"{x:.1e}" for x in (B.s / B.s[0])[::5]))
    print("\nL grows like log(Lambda):")
    for lam, L in zip([1, 10, 100, 1000], basis_size_vs_lambda([1, 10, 100, 1000])):
        print(f"  Lambda = {lam:5d}   L = {L}")
    g_tau, g_iw = single_pole(0.7, beta)
    tp = B.tau_sampling_points()
    tx = B.tau_sampling_points("extrema")
    print(f"\ntau sampling: roots of u_L cond {np.linalg.cond(B.u(tp)):.1f}, extrema of u_(L-1) "
          f"cond {np.linalg.cond(B.u(tx)):.1f}, uniform grid of L points cond "
          f"{np.linalg.cond(B.u(np.linspace(0, beta, B.size))):.1e}")
    Gl = B.fit(B.u(tp), g_tau(tp))
    dense = np.linspace(0, beta, 1001)
    err_t = np.max(np.abs(Gl @ B.u(dense) - g_tau(dense)))
    ns = B.matsubara_sampling_points()
    Fm = B.uhat(ns)
    Gl_m = B.fit(Fm, g_iw(ns))
    nn = np.arange(-2000, 2000)
    err_w = np.max(np.abs(Gl_m @ B.uhat(nn) - g_iw(nn)))
    print(f"\nsingle pole eps = 0.7: {len(tp)} tau points, cond = {np.linalg.cond(B.u(tp)):.1f}, "
          f"max |G(tau) error| = {err_t:.1e}")
    print(f"  {len(ns)} Matsubara points (max |n| = {ns.max()}), cond = {np.linalg.cond(Fm):.1f}, "
          f"max |G(i nu) error| on 4000 freqs = {err_w:.1e}")
    rho = lambda w: 0.5 * (np.exp(-(w - 1.5) ** 2 / 0.5) + np.exp(-(w + 1.5) ** 2 / 0.5)) / np.sqrt(0.5 * np.pi)
    Gl2 = -B.s[:B.size] * rho_coefficients(B, rho)
    print("\ntwo-Gaussian DOS, |G_l| for l = 0, 4, 8, ...:", " ".join(f"{x:.1e}" for x in np.abs(Gl2)[::4]))
    print(f"  odd l: max |G_l| = {np.max(np.abs(Gl2[1::2])):.1e} (particle-hole symmetric rho)")
    n_uni = uniform_grid_points_needed(g_tau, beta, err_t)
    print(f"\nsingle pole to the same max error {err_t:.1e}: IR {B.size} coefficients, "
          f"uniform tau grid + linear interpolation {n_uni} points")


if __name__ == "__main__":
    demo()
