"""Analytic continuation G(tau) -> A(w) as a regularised inverse problem.

Note 06 (analytic continuation). Discretised
    G_i = -sum_j K(tau_i, w_j) A_j dw + noise,
K the logistic kernel of note 03. Its singular values decay exponentially, so
the naive inverse amplifies noise by s_0 / s_l ~ 1e15 (`kernel_matrix`, `condition`).

- Tikhonov with default model m: min chi^2 + alpha ||A - m||^2, closed form via
  SVD filter factors s^2 / (s^2 + alpha) [S30] (`tikhonov`).
- Maximum-entropy flavoured: min chi^2 / 2 - alpha S[A], Shannon-Jaynes entropy
  S = sum dw (A - m - A ln(A/m)), positivity by A = m e^u; solved by Newton on
  the convex dual in data space (u in the row space of K, Bryan [S27]; [S28]) (`maxent`).
- alpha by the discrepancy principle chi^2(alpha) = N_tau (Morozov; "historic"
  maxent) (`discrepancy_alpha`).
- Learned linear inverse: the posterior mean under a Gaussian prior whose mean and
  covariance are estimated from synthetic training spectra, i.e. Tikhonov with a
  learned metric; the linear baseline of supervised continuation [S29]
  (`LearnedLinearInverse`).
- Uncertainty from noise resampling (`noise_band`); this does NOT capture the
  regularisation bias.

Run `python continuation.py`.
"""
from __future__ import annotations

import numpy as np

from ir_toy import logistic_kernel


def grids(beta: float = 10.0, ntau: int = 81, wmax: float = 8.0, nw: int = 321):
    tau = np.linspace(0, beta, ntau)
    w = np.linspace(-wmax, wmax, nw)
    return tau, w, w[1] - w[0]


def kernel_matrix(tau, w, dw, beta):
    """Kd with G = Kd @ A, including the minus sign and the w quadrature weight."""
    return -logistic_kernel(tau, w, beta) * dw


def condition(Kd) -> float:
    s = np.linalg.svd(Kd, compute_uv=False)
    return float(s[0] / s[-1])


def gaussians(w, centres, widths, weights) -> np.ndarray:
    A = sum(c * np.exp(-0.5 * ((w - mu) / s) ** 2) / (s * np.sqrt(2 * np.pi))
            for mu, s, c in zip(centres, widths, weights))
    return A


def two_peak(w):
    return gaussians(w, [-1.5, 2.5], [0.5, 0.7], [0.6, 0.4])


def synthetic_data(A, Kd, sigma: float, rng: np.random.Generator):
    G = Kd @ A
    return G + sigma * rng.standard_normal(G.shape)


def chi2(A, Kd, G, sigma) -> float:
    return float(np.sum(((Kd @ A - G) / sigma) ** 2))


def tikhonov(Kd, G, sigma, alpha, m):
    """argmin ||(Kd A - G)/sigma||^2 + alpha ||A - m||^2 via filter factors."""
    U, s, Vt = np.linalg.svd(Kd / sigma, full_matrices=False)
    r = (G - Kd @ m) / sigma
    return m + Vt.T @ (s / (s ** 2 + alpha) * (U.T @ r))


def maxent(Kd, G, sigma, alpha, m, dw, c0=None, tol=1e-10, maxiter=200):
    """argmin_A chi^2/2 - alpha S[A] via its convex dual in data space.

    Stationarity alpha dw ln(A/m) = -Ks^T (Ks A - Gs), Ks = Kd / sigma, says
    u = ln(A/m) = Ks^T c lies in the row space of Ks (Bryan's observation [S27]),
    with c = (Gs - Ks A) / (alpha dw). c minimises the convex function
        Phi(c) = alpha dw |c|^2 / 2 + sum_j m_j exp((Ks^T c)_j) - c . Gs,
        grad = alpha dw c + Ks A - Gs,  Hess = alpha dw I + Ks diag(A) Ks^T,
    so Newton with Armijo backtracking converges from any start. Returns (A, c).
    """
    Ks, Gs = Kd / sigma, G / sigma
    c = np.zeros(len(G)) if c0 is None else c0.copy()

    def phi(c):
        with np.errstate(over="ignore"):
            A = m * np.exp(Ks.T @ c)          # overflow -> inf -> step rejected below
        return 0.5 * alpha * dw * c @ c + A.sum() - c @ Gs, A

    f, A = phi(c)
    for _ in range(maxiter):
        g = alpha * dw * c + Ks @ A - Gs
        if np.linalg.norm(g) < tol * max(1.0, np.linalg.norm(Gs)):
            break
        H = alpha * dw * np.eye(len(c)) + (Ks * A) @ Ks.T
        step = -np.linalg.solve(H, g)
        t = 1.0
        while True:
            fn, An = phi(c + t * step)
            if np.isfinite(fn) and fn <= f + 1e-4 * t * (g @ step) or t < 1e-12:
                break
            t *= 0.5
        c, f, A = c + t * step, fn, An
    return A, c


class WarmMaxent:
    """maxent(alpha) as a callable that warm-starts from the previous solution.

    Bisection moves alpha slowly, so the last dual vector c is a good Newton start
    (the dual is convex, so this only saves iterations).
    """

    def __init__(self, Kd, G, sigma, m, dw):
        self.args, self.c = (Kd, G, sigma), None
        self.m, self.dw = m, dw

    def __call__(self, alpha):
        A, self.c = maxent(*self.args, alpha, self.m, self.dw, c0=self.c)
        return A


def discrepancy_alpha(solve, Kd, G, sigma, lo=1e-4, hi=1e6, iters=30):
    """Bisection in log alpha for chi^2(alpha) = N (chi^2 grows with alpha).

    `solve(alpha)` returns A. Returns (alpha, A). If the bisection runs down to
    `lo` without reaching N (possible for maxent: positivity plus an unlucky noise
    draw put the chi^2 floor above N), bisect again for 1.1 x that floor instead
    of returning alpha ~ 0. `solve` may warm-start, so alpha moves gradually.
    """
    def bisect(target, lo, hi):
        for _ in range(iters):
            mid = np.sqrt(lo * hi)
            if chi2(solve(mid), Kd, G, sigma) > target:
                hi = mid
            else:
                lo = mid
        return np.sqrt(lo * hi)

    a = bisect(len(G), lo, hi)
    A = solve(a)
    floor = chi2(A, Kd, G, sigma)
    if floor > 1.05 * len(G):
        a = bisect(1.1 * floor, a, hi)
        A = solve(a)
    return a, A


def l1_error(A, A_true, dw) -> float:
    return float(np.sum(np.abs(A - A_true)) * dw)


def peak_positions(A, w):
    """argmax of A on w < 0 and on w > 0."""
    neg, pos = w < 0, w > 0
    return float(w[neg][np.argmax(A[neg])]), float(w[pos][np.argmax(A[pos])])


class LearnedLinearInverse:
    """A_hat = mu + C K^T (K C K^T + sigma^2 I)^{-1} (G - K mu), mu, C from samples.

    The Bayes-optimal *linear* estimator for spectra drawn like the training set;
    a neural network trained on (G, A) pairs [S29] generalises this nonlinearly.
    """

    def __init__(self, Kd, sigma, spectra: np.ndarray, ridge: float = 1e-8):
        self.mu = spectra.mean(0)
        C = np.cov(spectra.T) + ridge * np.eye(spectra.shape[1])
        M = Kd @ C @ Kd.T + sigma ** 2 * np.eye(Kd.shape[0])
        self.W = C @ Kd.T @ np.linalg.inv(M)
        self.Kd = Kd

    def __call__(self, G):
        return self.mu + (G - self.Kd @ self.mu) @ self.W.T if G.ndim == 2 else \
            self.mu + self.W @ (G - self.Kd @ self.mu)


def random_spectra(w, n: int, rng: np.random.Generator) -> np.ndarray:
    """1-3 Gaussians, centres in [-4, 4], widths [0.3, 1.2], weights Dirichlet; int A = 1."""
    out = np.empty((n, len(w)))
    dw = w[1] - w[0]
    for i in range(n):
        p = rng.integers(1, 4)
        A = gaussians(w, rng.uniform(-4, 4, p), rng.uniform(0.3, 1.2, p), rng.dirichlet(np.ones(p)))
        out[i] = A / (A.sum() * dw)
    return out


def noise_band(solver, A_true, Kd, sigma, n: int, rng: np.random.Generator):
    """Mean and std of the reconstruction over n independent noise draws."""
    As = np.array([solver(synthetic_data(A_true, Kd, sigma, rng)) for _ in range(n)])
    return As.mean(0), As.std(0)


def demo() -> None:
    beta = 10.0
    tau, w, dw = grids(beta)
    Kd = kernel_matrix(tau, w, dw, beta)
    s = np.linalg.svd(Kd, compute_uv=False)
    print(f"beta = {beta}, {len(tau)} tau x {len(w)} w; s_0/s_l: l=10 {s[0]/s[10]:.1e}, "
          f"l=20 {s[0]/s[20]:.1e}, l=40 {s[0]/s[40]:.1e}")
    A_true = two_peak(w)
    m = np.full_like(w, 1.0 / (2 * w[-1]))           # flat default model, int m = 1
    rng = np.random.default_rng(0)
    print(f"\n{'sigma':>7} {'method':>10} {'alpha':>9} {'chi2/N':>7} {'L1 err':>7} {'int A':>6} "
          f"{'min A':>8} {'peaks':>14}")
    for sigma in (1e-3, 1e-4, 1e-5):
        G = synthetic_data(A_true, Kd, sigma, rng)
        for name, solve in [("tikhonov", lambda a: tikhonov(Kd, G, sigma, a, m)),
                            ("maxent", WarmMaxent(Kd, G, sigma, m, dw))]:
            a, A = discrepancy_alpha(solve, Kd, G, sigma)
            pk = peak_positions(A, w)
            print(f"{sigma:7.0e} {name:>10} {a:9.2e} {chi2(A, Kd, G, sigma) / len(G):7.2f} "
                  f"{l1_error(A, A_true, dw):7.3f} {A.sum() * dw:6.3f} {A.min():8.1e} "
                  f"({pk[0]:+.2f},{pk[1]:+.2f})")
    print("true peaks (-1.50, +2.50); tikhonov goes negative, maxent cannot.")
    sigma = 1e-4
    train = random_spectra(w, 2000, np.random.default_rng(1))
    test = random_spectra(w, 200, np.random.default_rng(2))
    inv = LearnedLinearInverse(Kd, sigma, train)
    Gt = test @ Kd.T + sigma * rng.standard_normal((len(test), len(tau)))
    e_learn = np.mean([l1_error(a, t, dw) for a, t in zip(inv(Gt), test)])
    e_tik = {a: np.mean([l1_error(tikhonov(Kd, g, sigma, a, m), t, dw) for g, t in zip(Gt, test)])
             for a in (1.0, 150.0)}
    print(f"\n200 random test spectra, sigma = {sigma}: mean L1 error learned-linear {e_learn:.3f}; "
          f"Tikhonov with flat m: alpha=1 {e_tik[1.0]:.3f}, alpha=150 {e_tik[150.0]:.3f}")
    for a in (1.0, 150.0):
        mean, std = noise_band(lambda g: tikhonov(Kd, g, sigma, a, m), A_true, Kd, sigma, 30, rng)
        print(f"noise band (30 draws, Tikhonov alpha={a:g}): max std {std.max():.3f}, "
              f"max |bias| {np.max(np.abs(mean - A_true)):.3f}")
    print("small alpha: variance dominates; discrepancy alpha: bias dominates and the band "
          "is far too narrow to be an error bar.")


if __name__ == "__main__":
    demo()
