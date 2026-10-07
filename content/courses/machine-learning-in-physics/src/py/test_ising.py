"""Tests for ising.py (note 10)."""
import numpy as np
import pytest

import ising


@pytest.fixture(scope="module")
def data():
    return ising.dataset()


def test_onsager_tc():
    assert ising.TC == pytest.approx(2.269185, abs=1e-6)


def test_energy_of_ordered_and_checkerboard_states():
    S = np.ones((6, 6))
    assert ising.energy_per_site(S) == -2.0
    ii, jj = np.indices((6, 6))
    assert ising.energy_per_site((-1.0) ** (ii + jj)) == 2.0


def test_metropolis_matches_exact_enumeration_L4():
    e, am, m2 = ising.exact_small(4, 2.5)
    sp = ising.metropolis(4, [2.5], n_samples=400, chains=50, n_therm=200, n_between=5,
                          seed=3)[0].astype(float)
    assert ising.energy_per_site(sp).mean() == pytest.approx(e, abs=0.02)
    assert np.abs(ising.magnetisation(sp)).mean() == pytest.approx(am, abs=0.02)
    assert (ising.magnetisation(sp) ** 2).mean() == pytest.approx(m2, abs=0.02)


def test_order_parameter_limits(data):
    temps, spins, X, T = data
    m = np.abs(X.mean(1))
    assert m[T == 1.0].mean() > 0.99 and m[np.isclose(T, 3.5)].mean() < 0.15


def test_binder_limits():
    rng = np.random.default_rng(0)
    assert ising.binder(rng.choice([-0.9, 0.9], 10000)) == pytest.approx(2 / 3, abs=1e-9)
    assert ising.binder(rng.normal(size=200000)) == pytest.approx(0, abs=0.02)


def test_pca_first_component_is_the_magnetisation(data):
    temps, spins, X, T = data
    r = ising.pca_tc(temps, X, T)
    assert abs(r["pc1"].sum()) / np.sqrt(X.shape[1]) > 0.99          # uniform vector
    assert np.corrcoef(np.abs(r["score"]), np.abs(X.mean(1)))[0, 1] > 0.99
    assert r["evr"][0] > 10 * r["evr"][1]
    assert 2.1 <= r["tc"] <= 2.6


def test_supervised_classifiers(data):
    temps, spins, X, T = data
    res = ising.supervised_tc(temps, X, T)
    raw = res["logistic, raw spins"]
    sym = res["logistic, (|m|, m^2, E/N)"]
    mlp = res["MLP 16 hidden, raw spins"]
    assert raw["acc"] < 0.8 < 0.97 < sym["acc"]        # Z2 symmetry defeats the linear model
    assert mlp["acc"] > 0.95
    for r in (sym, mlp):
        assert abs(r["tc"] - ising.TC) < 0.2


def test_binder_cumulants_cross_near_tc():
    temps, U, tc = ising.binder_crossing()
    assert U[16][0] > U[8][0] and U[16][-1] < U[8][-1]
    assert abs(tc - ising.TC) < 0.1
