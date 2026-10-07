"""Deep-learning-theory results, verified against the primary papers.

Covers note 10. This file exists as its own unit because every factual error
the 2026-09-22 source-verification pass found was in note 10, where the claims
rest on research papers rather than on the two textbooks -- notes 01-09 came
through clean. See ../../notes/CHANGELOG.md.

Part of the textbook-verification suite (see ../README.md). Each test hard-codes
the expression as the source states it and compares it against an independently
computed quantity, so a *misremembered constant* in the notes -- a wrong sign, a
stray factor of two, a log that should be a log-log, an exponent inside a square
root instead of outside -- fails here rather than being read past.

Locators refer to ../../refs/SOURCES.md:

    S36 = Hastie, Montanari, Rosset & Tibshirani, Ann. Statist. 50 (2022)
          'Surprises in high-dimensional ridgeless least squares interpolation'
"""
import math

import numpy as np
import pytest


# --- Ridgeless asymptotics: S36 Thm 1 ---------------------------------------

def ridgeless_risk(gamma, r2, sigma2):
    """S36 Thm 1, isotropic well-specified case."""
    if gamma < 1:
        return sigma2 * gamma / (1 - gamma)
    return r2 * (1 - 1 / gamma) + sigma2 / (gamma - 1)


def test_ridgeless_risk_formula_and_where_its_global_minimum_lies():
    """S36 Thm 1 for min-norm least squares, and the claim note 10 gets right
    only after correction: in the WELL-SPECIFIED isotropic model the global
    minimum is always in the underparameterised regime, at every SNR.

    SNR only decides the shape of the gamma>1 branch: monotone decreasing for
    SNR <= 1, an interior local minimum for SNR > 1.
    """
    sigma2 = 1.0
    for snr in (0.25, 0.5, 1.0, 2.0, 4.0, 10.0):
        r2 = snr * sigma2

        # Underparameterised risk -> 0 as gamma -> 0, so the infimum there is 0.
        assert ridgeless_risk(0.01, r2, sigma2) < 0.02
        # ... and no overparameterised value can beat it.
        over = np.array([ridgeless_risk(g, r2, sigma2)
                         for g in np.linspace(1.01, 200.0, 4000)])
        assert over.min() > ridgeless_risk(0.01, r2, sigma2)

        # Both branches diverge at gamma = 1.
        assert ridgeless_risk(0.999, r2, sigma2) > 500
        assert ridgeless_risk(1.001, r2, sigma2) > 500
        # And the right branch tends to the null risk r^2.
        assert ridgeless_risk(1e6, r2, sigma2) == pytest.approx(r2, rel=1e-3)

        # Shape of the right branch: interior minimum iff SNR > 1, at
        # gamma* = sqrt(SNR) / (sqrt(SNR) - 1).
        grid = np.linspace(1.02, 400.0, 40000)
        vals = np.array([ridgeless_risk(g, r2, sigma2) for g in grid])
        interior = 0 < int(np.argmin(vals)) < len(grid) - 1
        assert interior == (snr > 1.0)
        if snr > 1.0:
            expected = math.sqrt(snr) / (math.sqrt(snr) - 1)
            assert grid[int(np.argmin(vals))] == pytest.approx(expected, rel=0.05)


def test_min_norm_interpolator_risk_tracks_the_asymptotic_formula():
    """Finite-sample check of S36 Thm 1 by simulation, gamma > 1 branch.

    y = <x, beta> + eps with x ~ N(0, I_p); the excess risk of the min-norm
    interpolator is ||beta_hat - beta||^2 for isotropic x.
    """
    rng = np.random.default_rng(8)
    n, sigma2, r2 = 150, 1.0, 4.0

    for gamma in (2.0, 4.0):
        p = int(gamma * n)
        beta = rng.normal(size=p)
        beta *= math.sqrt(r2) / np.linalg.norm(beta)
        risks = []
        for _ in range(12):
            X = rng.normal(size=(n, p))
            y = X @ beta + math.sqrt(sigma2) * rng.normal(size=n)
            beta_hat = np.linalg.pinv(X) @ y
            risks.append(float(np.sum((beta_hat - beta) ** 2)))
        assert float(np.mean(risks)) == pytest.approx(
            ridgeless_risk(gamma, r2, sigma2), rel=0.25)
