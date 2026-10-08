import numpy as np
import pytest

from ising_snapshots import (T_C, energy_per_spin, magnetisation, onsager_energy,
                             onsager_magnetisation, sample_ising)


def test_exact_values():
    assert T_C == pytest.approx(2.269185, abs=1e-6)
    # u(T_c) = -sqrt 2 (at T_c itself K(1) = inf times 0; approach it). At 1e-9 from T_c,
    # k^2 rounds to exactly 1 with some libm builds; 1e-7 keeps 1 - k^2 near 1e-14, error ~2e-6.
    assert onsager_energy(T_C * (1 + 1e-7)) == pytest.approx(-np.sqrt(2), abs=1e-5)
    assert float(onsager_magnetisation(3.0)) == 0.0
    assert float(onsager_magnetisation(1.0)) == pytest.approx(0.99928, abs=1e-5)


def test_ground_states_and_checkerboard():
    s = np.ones((2, 6, 6))
    s[1] *= -1
    assert np.allclose(energy_per_spin(s), -2.0)
    assert np.allclose(magnetisation(s), [1, -1])
    cb = (np.add.outer(np.arange(6), np.arange(6)) % 2 * 2 - 1)[None].astype(float)
    assert np.allclose(energy_per_spin(cb), 2.0)


def test_monte_carlo_matches_onsager_away_from_tc():
    s, T = sample_ising(16, [1.8, 3.2], 60, n_therm=400, rng=np.random.default_rng(0))
    m, e = np.abs(magnetisation(s)), energy_per_spin(s)
    lo, hi = T == 1.8, T == 3.2
    assert m[lo].mean() == pytest.approx(float(onsager_magnetisation(1.8)), abs=0.02)
    assert e[lo].mean() == pytest.approx(float(onsager_energy(1.8)), abs=0.02)
    assert e[hi].mean() == pytest.approx(float(onsager_energy(3.2)), abs=0.03)
