import numpy as np
import pytest
from sklearn.neighbors import KNeighborsClassifier, KNeighborsRegressor
from sklearn.metrics import pairwise_distances as skpd
from sklearn.datasets import make_classification, make_regression

import knn

rng = np.random.default_rng(0)
A, B = rng.normal(size=(20, 4)), rng.normal(size=(15, 4))


@pytest.mark.parametrize("metric", ["euclidean", "manhattan", "chebyshev", "cosine"])
def test_pairwise_distances(metric):
    assert np.allclose(knn.pairwise_distances(A, B, metric), skpd(A, B, metric=metric))


def test_minkowski_and_mahalanobis():
    assert np.allclose(knn.pairwise_distances(A, B, "minkowski", 3), skpd(A, B, metric="minkowski", p=3))
    S = np.cov(A, rowvar=False)
    assert np.allclose(knn.mahalanobis(A, B, S), skpd(A, B, metric="mahalanobis", VI=np.linalg.inv(S)))


@pytest.mark.parametrize("weights", ["uniform", "distance"])
def test_classifier_matches_sklearn(weights):
    X, y = make_classification(300, 5, n_informative=3, n_classes=3, random_state=1)
    Xtr, Xte, ytr, yte = X[:200], X[200:], y[:200], y[200:]
    ours = knn.KNNClassifier(7, weights=weights).fit(Xtr, ytr)
    theirs = KNeighborsClassifier(7, weights=weights).fit(Xtr, ytr)
    assert np.mean(ours.predict(Xte) == theirs.predict(Xte)) > 0.97       # ties broken differently at most
    assert np.allclose(ours.predict_proba(Xte), theirs.predict_proba(Xte), atol=1e-6)


def test_regressor_matches_sklearn():
    X, y = make_regression(200, 4, noise=1.0, random_state=0)
    ours = knn.KNNRegressor(5, "manhattan").fit(X[:150], y[:150]).predict(X[150:])
    theirs = KNeighborsRegressor(5, metric="manhattan").fit(X[:150], y[:150]).predict(X[150:])
    assert np.allclose(ours, theirs)
