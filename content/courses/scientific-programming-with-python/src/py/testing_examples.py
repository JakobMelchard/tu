"""Code under test for note 05 (testing).

Small numerical routines with the edge cases that tests should probe:
floating-point comparison, invalid input, convergence failure, and
properties that hold for all inputs.  The tests live in
test_testing_examples.py and show fixtures, parametrize, raises, approx,
numpy.testing helpers and a hand-rolled property-based check.
"""
from __future__ import annotations

import math

import numpy as np


def solve_quadratic(a: float, b: float, c: float) -> tuple[float, float]:
    """Roots of a x^2 + b x + c, numerically stable: compute the root that
    does NOT suffer cancellation, then the other via Vieta (x1 x2 = c/a)."""
    if a == 0:
        raise ValueError("a must be non-zero")
    disc = b * b - 4 * a * c
    if disc < 0:
        raise ValueError("complex roots")
    q = -0.5 * (b + math.copysign(math.sqrt(disc), b))
    if q == 0:                      # b == 0 and disc == 0
        return 0.0, 0.0
    x1 = q / a
    x2 = c / q
    return (x1, x2) if x1 <= x2 else (x2, x1)


def trapezoid(f, a: float, b: float, n: int) -> float:
    """Composite trapezoid: error = -(b-a) h^2 f''(xi) / 12, exact for lines."""
    if n < 1:
        raise ValueError("n >= 1")
    x = np.linspace(a, b, n + 1)
    y = f(x)
    h = (b - a) / n
    return h * (y[0] / 2 + y[1:-1].sum() + y[-1] / 2)


def newton(f, df, x0: float, tol: float = 1e-12, max_iter: int = 50) -> float:
    x = x0
    for _ in range(max_iter):
        step = f(x) / df(x)
        x -= step
        if abs(step) < tol * max(1.0, abs(x)):
            return x
    raise RuntimeError(f"Newton did not converge from {x0}")


def normalise(v: np.ndarray) -> np.ndarray:
    """Unit vector; zero vector is an error, not a NaN vector."""
    v = np.asarray(v, dtype=float)
    n = np.linalg.norm(v)
    if n == 0:
        raise ZeroDivisionError("cannot normalise the zero vector")
    return v / n


def softmax(z: np.ndarray) -> np.ndarray:
    """Shift by max: exp(z - max) never overflows and the result is the same."""
    z = np.asarray(z, dtype=float)
    e = np.exp(z - z.max())
    return e / e.sum()


def mean_and_var(x: np.ndarray) -> tuple[float, float]:
    """Welford's one-pass algorithm; unbiased variance (n-1)."""
    n, mean, m2 = 0, 0.0, 0.0
    for v in x:
        n += 1
        delta = v - mean
        mean += delta / n
        m2 += delta * (v - mean)
    if n < 2:
        raise ValueError("need at least two samples")
    return mean, m2 / (n - 1)


def read_config(path) -> dict[str, float]:
    """key=value lines -> dict of floats; used to demonstrate tmp_path."""
    out = {}
    with open(path) as fh:
        for line in fh:
            line = line.split("#", 1)[0].strip()
            if line:
                k, v = line.split("=")
                out[k.strip()] = float(v)
    return out


if __name__ == "__main__":
    print("roots of x^2 - 3x + 2:", solve_quadratic(1, -3, 2))
    print("stable roots, b=1e8:", solve_quadratic(1, 1e8, 1))
    print("trapezoid sin on [0,pi], n=100:", trapezoid(np.sin, 0, np.pi, 100))
    print("newton sqrt(2):", newton(lambda x: x * x - 2, lambda x: 2 * x, 1.0))
    print("softmax big:", softmax([1000, 1001]))
    print("welford:", mean_and_var([1, 2, 3, 4]))
