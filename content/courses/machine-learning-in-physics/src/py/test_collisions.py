"""Tests for collisions.py (note 10)."""
import numpy as np
import pytest
from sklearn.metrics import roc_auc_score, roc_curve

import collisions as co


@pytest.fixture(scope="module")
def fitted():
    return co.fit_all(n_train=10000, n_test=10000)


def test_auc_matches_sklearn_and_mann_whitney():
    rng = np.random.default_rng(0)
    y = rng.integers(0, 2, 500)
    s = np.round(rng.normal(size=500) + y, 1)           # rounding creates ties
    assert co.auc(y, s) == pytest.approx(roc_auc_score(y, s), abs=1e-12)
    assert co.auc_mann_whitney(y, s) == pytest.approx(roc_auc_score(y, s), abs=1e-12)
    fpr, tpr = co.roc_curve(y, s)
    f2, t2, _ = roc_curve(y, s, drop_intermediate=False)
    assert np.allclose(fpr, f2) and np.allclose(tpr, t2)


def test_auc_invariances():
    rng = np.random.default_rng(1)
    y = rng.integers(0, 2, 300)
    s = rng.normal(size=300) + y
    assert co.auc(y, np.exp(s)) == pytest.approx(co.auc(y, s))   # monotone maps
    assert co.auc(y, -s) == pytest.approx(1 - co.auc(y, s))
    assert co.auc(y, np.zeros(300)) == pytest.approx(0.5)


def test_uninformative_features_are_uninformative():
    X, y = co.make_events(20000, seed=3)
    for j in (4, 5, 6):                                           # eta1, eta2, phi1
        assert abs(co.auc(y, X[:, j]) - 0.5) < 0.02
    assert co.auc(y, -np.abs(X[:, 4] - X[:, 5])) > 0.65           # but |eta1 - eta2| is


def test_classifier_ranking(fitted):
    y, scores = fitted
    a_raw = co.auc(y, scores["logistic, raw"])
    a_eng = co.auc(y, scores["logistic, engineered"])
    a_mlp = co.auc(y, scores["MLP 32-32, raw"])
    assert 0.72 < a_raw < 0.80
    assert a_eng > a_raw + 0.05 and a_mlp > a_raw + 0.05


def test_accuracy_is_not_enough(fitted):
    y, scores = fitted
    base = 1 - y.mean()                                            # always "background"
    acc_raw = np.mean((scores["logistic, raw"] > 0.5) == y)
    assert base > 0.65 and acc_raw < base + 0.08
