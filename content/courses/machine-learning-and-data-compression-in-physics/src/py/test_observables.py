import numpy as np
import pytest
import torch

from ising_snapshots import T_C, bond_features, energy_per_spin
from observables import (classification_table, dataset, kernel_ridge, logistic_newton,
                         poly2_kernel, r2, regression_table, ridge)

torch.set_num_threads(1)


@pytest.fixture(scope="module")
def d():
    return dataset(L=8, n_per_T=50, seed=5)


def test_energy_is_exactly_linear_in_bond_features(d):
    s = d["X"].reshape(-1, 8, 8)
    assert np.allclose(energy_per_spin(s), -bond_features(s).sum(1) / 64)


def test_ridge_and_kernel_ridge_match_sklearn(d):
    from sklearn.kernel_ridge import KernelRidge
    from sklearn.linear_model import Ridge
    X, y, tr, te = d["X"], d["e"], d["tr"], d["te"]
    ours = ridge(X[tr], y[tr], 2.0)(X[te])
    sk = Ridge(alpha=2.0).fit(X[tr], y[tr]).predict(X[te])
    assert np.allclose(ours, sk)
    ours = kernel_ridge(X[tr], y[tr], 0.5)(X[te])
    kr = KernelRidge(alpha=0.5, kernel="precomputed").fit(poly2_kernel(X[tr], X[tr]), y[tr] - y[tr].mean())
    assert np.allclose(ours, kr.predict(poly2_kernel(X[te], X[tr])) + y[tr].mean())


def test_r2_definition():
    y = np.array([1.0, 2.0, 3.0, 4.0])
    assert r2(y, y) == 1.0
    assert r2(y, np.full(4, y.mean())) == pytest.approx(0.0)


def test_regression_r2_by_feature_choice(d):
    t = regression_table(d)
    assert t[("e", "ridge raw")] < 0.1 and t[("m2", "ridge raw")] < 0.1     # Z2 symmetry
    assert t[("e", "ridge bonds")] > 0.9999
    assert t[("m2", "KRR poly2 raw")] > 0.999
    assert t[("e", "KRR poly2 raw")] > 0.9


def test_phase_classification_and_tc(d):
    res = classification_table(d)
    assert res["logistic raw"][1] < 0.75                  # linear in s: no better than chance-ish
    assert res["logistic m^2"][1] > 0.95
    assert res["MLP raw + Z2"][1] > 0.9
    assert res["MLP raw + Z2"][1] >= res["MLP raw"][1] - 0.02
    assert abs(res["Tc_MLP"] - T_C) < 0.25


def test_logistic_newton_separable_1d():
    x = np.linspace(-3, 3, 200)[:, None]
    y = (x[:, 0] > 0.5).astype(float)
    p = logistic_newton(x, y, lam=1e-2)(x)
    assert np.mean((p > 0.5) == (y > 0.5)) > 0.98
