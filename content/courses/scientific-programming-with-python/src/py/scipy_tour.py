"""SciPy tour (note 03).

One small, checkable example per subpackage: integrate, optimize,
interpolate, sparse, linalg, fft, stats, signal.  Each function returns the
computed quantity together with the exact/expected value where one exists.
"""
from __future__ import annotations

import numpy as np
from scipy import fft, integrate, interpolate, linalg, optimize, signal, sparse, stats
from scipy.sparse.linalg import spsolve


# ---------------------------------------------------------------- integrate
def quad_gaussian() -> tuple[float, float, float]:
    """quad = adaptive Gauss-Kronrod (QUADPACK); returns value and error
    estimate.  Handles infinite limits by variable transformation."""
    val, err = integrate.quad(lambda x: np.exp(-x**2), -np.inf, np.inf)
    return val, err, np.sqrt(np.pi)


def solve_ivp_oscillator(omega: float = 2.0, t_end: float = 5.0, rtol: float = 1e-8):
    """x'' = -w^2 x as a first-order system y = (x, v).  solve_ivp picks the
    step (RK45 default; 'Radau'/'BDF' for stiff); dense_output interpolates.
    Returns max error against x = cos(w t)."""
    def rhs(t, y):
        return [y[1], -omega**2 * y[0]]
    sol = integrate.solve_ivp(rhs, (0, t_end), [1.0, 0.0], rtol=rtol, atol=1e-10,
                              dense_output=True)
    t = np.linspace(0, t_end, 200)
    err = np.abs(sol.sol(t)[0] - np.cos(omega * t)).max()
    return sol, err


def trapezoid_vs_simpson(n: int = 21):
    """Fixed-sample rules for tabulated data: trapezoid O(h^2), Simpson O(h^4)."""
    x = np.linspace(0, np.pi, n)
    y = np.sin(x)
    return integrate.trapezoid(y, x), integrate.simpson(y, x=x), 2.0


# ---------------------------------------------------------------- optimize
def minimize_rosenbrock(method: str = "BFGS"):
    """f = (1-x)^2 + 100 (y-x^2)^2, minimum at (1,1).  Gradient given, so
    BFGS uses it; Nelder-Mead would ignore jac."""
    f = optimize.rosen
    jac = None if method in ("Nelder-Mead", "Powell") else optimize.rosen_der
    res = optimize.minimize(f, x0=[-1.2, 1.0], jac=jac, method=method)
    return res


def root_transcendental():
    """Scalar root of cos(x) - x with a bracketing method (Brent, guaranteed
    to converge given a sign change) vs Newton (needs derivative, fast)."""
    f = lambda x: np.cos(x) - x
    brent = optimize.brentq(f, 0, 1)
    newton = optimize.newton(f, 0.5, fprime=lambda x: -np.sin(x) - 1)
    return brent, newton


def curve_fit_decay(rng: np.random.Generator):
    """Nonlinear least squares (Levenberg-Marquardt): fit A exp(-k t) + c."""
    model = lambda t, A, k, c: A * np.exp(-k * t) + c
    t = np.linspace(0, 5, 60)
    true = (3.0, 1.2, 0.5)
    y = model(t, *true) + 0.02 * rng.standard_normal(t.size)
    popt, pcov = optimize.curve_fit(model, t, y, p0=[1, 1, 0])
    return popt, np.sqrt(np.diag(pcov)), true


# ---------------------------------------------------------------- interpolate
def interpolation_demo():
    """CubicSpline: C^2 piecewise cubic through the data (natural / not-a-knot
    end conditions).  interp1d(kind='linear') for the cheap version.
    Runge's phenomenon: a high-degree global polynomial oscillates."""
    x = np.linspace(-1, 1, 11)
    f = lambda x: 1 / (1 + 25 * x**2)
    xs = np.linspace(-1, 1, 201)
    spline = interpolate.CubicSpline(x, f(x))
    linear = interpolate.interp1d(x, f(x))
    poly = np.polynomial.Polynomial.fit(x, f(x), deg=10)
    errs = {name: np.abs(g(xs) - f(xs)).max() for name, g in
            [("spline", spline), ("linear", linear), ("poly10", poly)]}
    return errs, spline


# ---------------------------------------------------------------- sparse
def laplacian_1d(n: int, h: float = 1.0) -> sparse.csr_matrix:
    """Tridiagonal -u'' stencil (2,-1,-1)/h^2.  Build in a construction
    format (diags/COO/LIL), convert to CSR/CSC for arithmetic and solves."""
    main = 2.0 * np.ones(n)
    off = -np.ones(n - 1)
    return sparse.diags([off, main, off], [-1, 0, 1], format="csr") / h**2


def poisson_solve(n: int = 200):
    """-u'' = pi^2 sin(pi x) on (0,1), u(0)=u(1)=0, exact u = sin(pi x).
    spsolve (SuperLU) on the sparse system vs dense solve: same answer,
    O(n) vs O(n^3)."""
    h = 1.0 / (n + 1)
    x = np.arange(1, n + 1) * h
    A = laplacian_1d(n, h)
    b = np.pi**2 * np.sin(np.pi * x)
    u_sparse = spsolve(A.tocsc(), b)
    u_dense = np.linalg.solve(A.toarray(), b)
    return u_sparse, u_dense, np.sin(np.pi * x), A.nnz


# ---------------------------------------------------------------- linalg
def linalg_demo(rng: np.random.Generator):
    """scipy.linalg is a superset of numpy.linalg: decompositions (lu, qr,
    cholesky, schur), expm, solve with assume_a='pos' picks Cholesky."""
    A = rng.standard_normal((6, 6))
    S = A @ A.T + 6 * np.eye(6)
    b = rng.standard_normal(6)
    P, L, U = linalg.lu(A)
    c, low = linalg.cho_factor(S)
    x = linalg.cho_solve((c, low), b)
    expm_err = np.linalg.norm(linalg.expm(np.zeros((3, 3))) - np.eye(3))
    K = np.array([[0.0, 1.0], [-1.0, 0.0]])          # generator of rotations
    rot = linalg.expm(np.pi / 2 * K)                    # 90-degree rotation
    return {
        "lu_err": np.linalg.norm(P @ L @ U - A),
        "chol_err": np.linalg.norm(S @ x - b),
        "expm_zero_err": expm_err,
        "rot": rot,
        "eigh_pos": bool((linalg.eigh(S, eigvals_only=True) > 0).all()),
    }


# ---------------------------------------------------------------- fft
def fft_peaks(fs: float = 1000.0, n: int = 2000, freqs=(50.0, 120.0)):
    """rfft of a real signal: bins k correspond to k*fs/n Hz up to fs/2
    (Nyquist).  Returns the frequencies of the two largest spectral peaks."""
    t = np.arange(n) / fs
    x = sum(np.sin(2 * np.pi * f * t) for f in freqs)
    X = fft.rfft(x)
    f_axis = fft.rfftfreq(n, d=1 / fs)
    top = np.argsort(np.abs(X))[-2:]
    return sorted(f_axis[top].tolist()), f_axis[1] - f_axis[0]


def convolution_theorem(rng: np.random.Generator, n: int = 64):
    """Circular convolution = ifft(fft(a) fft(b)); linear convolution needs
    zero padding to length >= 2n-1 (what fftconvolve does)."""
    a, b = rng.random(n), rng.random(n)
    direct = np.convolve(a, b)
    m = 2 * n - 1
    via_fft = fft.irfft(fft.rfft(a, m) * fft.rfft(b, m), m)
    return np.abs(direct - via_fft).max()


# ---------------------------------------------------------------- stats
def stats_demo(rng: np.random.Generator):
    """Distributions are frozen objects with pdf/cdf/ppf/rvs; fit() gives
    MLE; ttest_ind and ks tests return (statistic, p-value)."""
    x = stats.norm(loc=2.0, scale=0.5).rvs(size=2000, random_state=rng)
    mu, sigma = stats.norm.fit(x)
    y = rng.normal(2.3, 0.5, 2000)
    t = stats.ttest_ind(x, y)
    ks = stats.kstest(x, stats.norm(mu, sigma).cdf)      # frozen distribution
    return {"mu": mu, "sigma": sigma, "ttest_p": t.pvalue, "ks_p": ks.pvalue,
            "q95": stats.norm.ppf(0.95), "cdf_of_ppf": stats.norm.cdf(stats.norm.ppf(0.3))}


# ---------------------------------------------------------------- signal
def lowpass_demo(fs: float = 1000.0, cutoff: float = 40.0):
    """Butterworth IIR designed in SOS form (numerically safer than (b,a));
    sosfiltfilt is zero-phase (filters forward and backward).  A 20 Hz
    component passes, a 300 Hz component is removed."""
    sos = signal.butter(6, cutoff, btype="low", fs=fs, output="sos")
    t = np.arange(0, 1, 1 / fs)
    x = np.sin(2 * np.pi * 20 * t) + 0.5 * np.sin(2 * np.pi * 300 * t)
    y = signal.sosfiltfilt(sos, x)
    rms_removed = np.sqrt(np.mean((y - np.sin(2 * np.pi * 20 * t))[100:-100] ** 2))
    peaks, _ = signal.find_peaks(y, height=0.5)
    return rms_removed, len(peaks)


if __name__ == "__main__":
    rng = np.random.default_rng(0)
    print("quad:", quad_gaussian())
    sol, err = solve_ivp_oscillator(); print("solve_ivp err:", err, "steps:", sol.t.size)
    print("trapz/simpson:", trapezoid_vs_simpson())
    r = minimize_rosenbrock(); print("BFGS:", r.x, r.nit, r.success)
    print("roots:", root_transcendental())
    print("curve_fit:", curve_fit_decay(rng)[0])
    print("interp errs:", interpolation_demo()[0])
    us, ud, ex, nnz = poisson_solve(); print("poisson err:", np.abs(us - ex).max(), "nnz:", nnz)
    print("linalg:", {k: v for k, v in linalg_demo(rng).items() if k != "rot"})
    print("fft peaks:", fft_peaks(), " conv thm err:", convolution_theorem(rng))
    print("stats:", stats_demo(rng))
    print("lowpass:", lowpass_demo())
