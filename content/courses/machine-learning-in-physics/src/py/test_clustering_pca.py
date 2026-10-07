"""Tests for clustering_pca.py (notes 06, 07) against scikit-learn."""
import numpy as np
import pytest
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.mixture import GaussianMixture

import clustering_pca as cp


@pytest.fixture
def blobs():
    return cp.three_blobs(np.random.default_rng(4711))


def test_kmeans_matches_sklearn_from_same_init(blobs):
    X, _ = blobs
    init = X[[0, 250, 500]]
    C, lab, J, hist = cp.kmeans(X, 3, init=init)
    sk = KMeans(3, init=init, n_init=1, tol=0, algorithm="lloyd").fit(X)
    assert J == pytest.approx(sk.inertia_, rel=1e-9)
    assert np.all(np.diff(hist) <= 1e-9)                   # Lloyd never increases J


def test_kmeans_recovers_blobs(blobs):
    X, y = blobs
    _, lab, _, _ = cp.kmeans(X, 3, np.random.default_rng(0), n_init=5)
    # clusters are pure up to relabelling
    purity = sum(np.bincount(y[lab == j]).max() for j in range(3)) / y.size
    assert purity > 0.97


def test_gmm_loglik_monotone_and_matches_sklearn():
    rng = np.random.default_rng(1)
    A = np.array([[3.0, 0.0], [0.0, 0.3]])
    X = np.vstack([rng.normal(size=(300, 2)) @ A, rng.normal(size=(300, 2)) @ A + [0, 2.0]])
    pi, mu, S, R, hist = cp.gmm_em(X, 2, np.random.default_rng(0))
    assert np.all(np.diff(hist) >= -1e-8)                  # EM ascent property
    sk = GaussianMixture(2, covariance_type="full", tol=1e-10, max_iter=1000,
                         reg_covar=1e-6, random_state=0).fit(X)
    assert hist[-1] / X.shape[0] == pytest.approx(sk.score(X), abs=1e-3)
    y = np.repeat([0, 1], 300)
    lab = np.argmax(R, 1)
    assert max(np.mean(lab == y), np.mean(lab != y)) > 0.97


def test_pca_matches_sklearn_and_eig():
    rng = np.random.default_rng(2)
    X = rng.normal(size=(200, 5)) @ rng.normal(size=(5, 5))
    mean, comps, ev, scores = cp.pca(X, 3)
    sk = PCA(3).fit(X)
    assert np.allclose(ev, sk.explained_variance_)
    for a, b in zip(comps, sk.components_):
        assert abs(abs(a @ b) - 1) < 1e-10                 # equal up to sign
    V, lam = cp.pca_eig(X, 3)
    assert np.allclose(lam, ev)
    assert np.allclose(cp.explained_variance_ratio(X)[:3], sk.explained_variance_ratio_)


def test_eckart_young_error_from_singular_values():
    rng = np.random.default_rng(3)
    X = rng.normal(size=(40, 25))
    for r in [1, 5, 20]:
        Xr, rel = cp.truncated_svd(X, r)
        assert np.linalg.matrix_rank(Xr) == r
        assert np.linalg.norm(X - Xr) / np.linalg.norm(X) == pytest.approx(rel)
        # any other rank-r matrix does worse, e.g. a random projection
        Q = np.linalg.qr(rng.normal(size=(25, r)))[0]
        assert np.linalg.norm(X - X @ Q @ Q.T) >= np.linalg.norm(X - Xr)
