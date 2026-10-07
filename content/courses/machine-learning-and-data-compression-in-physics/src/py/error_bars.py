"""Error bars for the protocol: independent runs, correlated series, bootstrap.

Note 08 (how to write the protocol), section 3.
- `mean_sem`: mean and standard error s / sqrt(n) of independent values.
- `binning_error`: standard error of a correlated series from blocks of size b;
  it plateaus at sqrt(2 tau_int) times the naive error once b >> tau_int.
- `tau_int_ar1`: exact tau_int = (1 + rho) / (2 (1 - rho)) of an AR(1) process,
  the test case for the binning analysis.
- `bootstrap`: standard error of any statistic (e.g. a T_c crossing) by resampling.

Run `python error_bars.py`.
"""
from __future__ import annotations

import numpy as np


def mean_sem(x) -> tuple[float, float]:
    x = np.asarray(x, dtype=float)
    return float(x.mean()), float(x.std(ddof=1) / np.sqrt(len(x)))


def binning_error(x, b: int) -> float:
    """Standard error of the mean from n // b non-overlapping blocks of length b."""
    x = np.asarray(x, dtype=float)
    nb = len(x) // b
    blocks = x[:nb * b].reshape(nb, b).mean(axis=1)
    return float(blocks.std(ddof=1) / np.sqrt(nb))


def binning_curve(x, max_level: int = 12) -> list[tuple[int, float]]:
    """(b, error) for b = 1, 2, 4, ... while at least 32 blocks remain."""
    out, b = [], 1
    while len(x) // b >= 32 and len(out) < max_level:
        out.append((b, binning_error(x, b)))
        b *= 2
    return out


def ar1(n: int, rho: float, rng: np.random.Generator) -> np.ndarray:
    """x_t = rho x_{t-1} + sqrt(1 - rho^2) xi_t, stationary with unit variance."""
    x = np.empty(n)
    x[0] = rng.standard_normal()
    xi = rng.standard_normal(n)
    c = np.sqrt(1 - rho ** 2)
    for t in range(1, n):
        x[t] = rho * x[t - 1] + c * xi[t]
    return x


def tau_int_ar1(rho: float) -> float:
    """tau_int = 1/2 + sum_{t>=1} rho^t = (1 + rho) / (2 (1 - rho)); var(mean) = 2 tau_int / n."""
    return (1 + rho) / (2 * (1 - rho))


def bootstrap(stat, data: np.ndarray, n_boot: int = 1000,
              rng: np.random.Generator | None = None) -> tuple[float, float]:
    """(stat(data), bootstrap standard error) resampling rows of data with replacement."""
    rng = np.random.default_rng(0) if rng is None else rng
    n = len(data)
    reps = np.array([stat(data[rng.integers(0, n, n)]) for _ in range(n_boot)])
    return float(stat(data)), float(reps.std(ddof=1))


def demo() -> None:
    rng = np.random.default_rng(0)
    rho, n = 0.9, 2 ** 16
    x = ar1(n, rho, rng)
    naive = x.std(ddof=1) / np.sqrt(n)
    exact = np.sqrt(2 * tau_int_ar1(rho) / n)
    print(f"AR(1), rho = {rho}, n = {n}: tau_int = {tau_int_ar1(rho):.2f}")
    print(f"  naive error {naive:.2e}, exact {exact:.2e} (ratio sqrt(2 tau_int) = "
          f"{np.sqrt(2 * tau_int_ar1(rho)):.2f})")
    for b, e in binning_curve(x):
        print(f"  b = {b:5d}  binned error {e:.2e}")
    print("  the plateau is the honest error bar; the naive one is 4.4x too small.")
    m, s = mean_sem(rng.normal(0.964, 0.01, 5))
    print(f"\nfive seeds of a test R^2: mean {m:.4f}, standard error {s:.4f} -> quote {m:.3f} +- {s:.3f}"
          " (one significant digit of error, value rounded to match)")
    data = rng.normal(2.25, 0.05, (40, 1))
    v, e = bootstrap(lambda d: float(np.median(d)), data, rng=rng)
    print(f"bootstrap: median of 40 values {v:.3f} +- {e:.3f}")


if __name__ == "__main__":
    demo()
