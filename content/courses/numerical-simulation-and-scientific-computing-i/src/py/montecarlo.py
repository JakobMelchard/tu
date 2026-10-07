"""Random numbers and Monte Carlo integration (topic 06).

LCG (minstd parameters) vs numpy's PCG64; inverse-transform sampling
(exponential) and Box-Muller (normal); MC estimates of pi and of
int_0^1 e^x dx with the 1/sqrt(N) error law and two variance-reduction tricks.

Run `python3 montecarlo.py` for the tables. C++ counterpart: ../cpp/rng_mc.cpp.

Sources: minstd parameters [S28] and the 10000th value required by ISO C++
[S14, rand.predef]; Box-Muller [S30]. Test: test_montecarlo.py (known values,
Kolmogorov-Smirnov tests against scipy.stats, error slope -1/2).
"""
import numpy as np


class LCG:
    """x_{k+1} = (a x_k + c) mod m. Default: minstd (a=16807, c=0, m=2^31-1)."""

    def __init__(self, seed=1, a=16807, c=0, m=2**31 - 1):
        self.a, self.c, self.m, self.state = a, c, m, seed

    def next(self):
        self.state = (self.a * self.state + self.c) % self.m
        return self.state

    def uniform(self, n=None):
        if n is None:
            return self.next() / self.m
        return np.array([self.next() for _ in range(n)]) / self.m


def exponential_inverse(u, lam):
    """Inverse transform of F(x) = 1 - exp(-lam x): x = -ln(1-u)/lam."""
    return -np.log1p(-u) / lam


def box_muller(u1, u2):
    """Two uniforms -> two independent standard normals."""
    r = np.sqrt(-2 * np.log(u1))
    th = 2 * np.pi * u2
    return r * np.cos(th), r * np.sin(th)


def mc_pi(rng, n):
    x, y = rng.random(n), rng.random(n)
    return 4 * np.mean(x * x + y * y < 1)


def mc_integral(f, rng, n, a=0.0, b=1.0):
    """Plain MC: (b-a) mean f(U); returns (estimate, standard error)."""
    x = a + (b - a) * rng.random(n)
    y = f(x)
    return (b - a) * y.mean(), (b - a) * y.std(ddof=1) / np.sqrt(n)


def mc_antithetic(f, rng, n):
    """Average f(u) and f(1-u): negatively correlated for monotone f."""
    u = rng.random(n // 2)
    return np.mean(0.5 * (f(u) + f(1 - u)))


def mc_control_variate(f, g, g_mean, rng, n):
    """Estimate mean(f - c g) + c g_mean with the optimal c = cov(f,g)/var(g)."""
    u = rng.random(n)
    fu, gu = f(u), g(u)
    c = np.cov(fu, gu)[0, 1] / np.var(gu, ddof=1)
    return np.mean(fu - c * (gu - g_mean))


def error_scaling(estimator, exact, ns, reps, seed=0):
    """RMS error over `reps` runs for each N; slope of log(err) vs log(N) should be -1/2."""
    rng = np.random.default_rng(seed)
    rms = np.array([np.sqrt(np.mean([(estimator(rng, n) - exact) ** 2 for _ in range(reps)])) for n in ns])
    slope = np.polyfit(np.log(ns), np.log(rms), 1)[0] if len(ns) > 1 else np.nan
    return rms, slope


if __name__ == "__main__":
    g = LCG(1)
    print("minstd first values:", [g.next() for _ in range(4)])
    rng = np.random.default_rng(2026)
    u = rng.random(200_000)
    e = exponential_inverse(u, 2.0)
    z0, z1 = box_muller(rng.random(100_000), rng.random(100_000))
    print(f"exponential(2): mean {e.mean():.4f} (0.5) var {e.var():.4f} (0.25)")
    print(f"Box-Muller    : mean {z0.mean():.4f} (0)   var {z0.var():.4f} (1)")

    ns = [100, 1_000, 10_000, 100_000, 1_000_000]
    rms, slope = error_scaling(mc_pi, np.pi, ns, reps=20)
    print(f"\n{'N':>9} {'rms err pi':>12} {'theory':>12}")
    for n, r in zip(ns, rms):
        print(f"{n:9d} {r:12.2e} {4*np.sqrt(np.pi/4*(1-np.pi/4)/n):12.2e}")
    print(f"slope {slope:.3f} (theory -0.5)")

    f = np.exp
    exact = np.e - 1
    n = 100_000
    est = {
        "plain": lambda r, n: mc_integral(f, r, n)[0],
        "antithetic": lambda r, n: mc_antithetic(f, r, n),
        "control variate g=1+x": lambda r, n: mc_control_variate(f, lambda x: 1 + x, 1.5, r, n),
    }
    print(f"\nint_0^1 e^x dx, N={n}, rms error over 20 runs")
    base = None
    for name, fn in est.items():
        r, _ = error_scaling(fn, exact, [n], 20)
        base = base or r[0]
        print(f"  {name:24s} {r[0]:.2e}   variance reduction x{(base/r[0])**2:.1f}")
