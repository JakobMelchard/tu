import numpy as np
import pytest
from sklearn.decomposition import PCA as SkPCA
from sklearn.datasets import load_iris

import pca

X = load_iris().data


def test_components_and_variance_match_sklearn():
    ours, theirs = pca.PCA(3).fit(X), SkPCA(3).fit(X)
    assert np.allclose(ours.explained_variance_, theirs.explained_variance_)
    assert np.allclose(ours.explained_variance_ratio_, theirs.explained_variance_ratio_)
    assert np.allclose(np.abs(ours.components_), np.abs(theirs.components_))   # axes equal up to sign
    assert np.allclose(np.abs(ours.transform(X)), np.abs(theirs.transform(X)))


def test_reconstruction_and_variance_fraction():
    ours = pca.PCA(0.95).fit(X)
    assert ours.n_components_ == SkPCA(0.95).fit(X).n_components_
    assert np.allclose(ours.inverse_transform(ours.transform(X)), SkPCA(ours.n_components_).fit(X).inverse_transform(SkPCA(ours.n_components_).fit(X).transform(X)))
    full = pca.PCA(4).fit(X)
    assert full.reconstruction_error(X) == pytest.approx(0.0, abs=1e-10)
    assert np.allclose(full.inverse_transform(full.transform(X)), X)


def test_eig_route_and_whitening():
    lam, V = pca.pca_eig(X, 2)
    p = pca.PCA(2).fit(X)
    assert np.allclose(lam, p.explained_variance_)
    assert np.allclose(np.abs(V), np.abs(p.components_))
    Zw = pca.PCA(2, whiten=True).fit_transform(X)
    assert np.allclose(np.cov(Zw, rowvar=False), np.eye(2), atol=1e-8)
    assert np.allclose(np.abs(Zw), np.abs(SkPCA(2, whiten=True).fit_transform(X)))


def test_iris_numbers_quoted_in_note_12():
    """Covariance eigenvalues 4.23, 0.24, 0.08, 0.02; PC1 explains 92.5 %, two 97.8 %."""
    p = pca.PCA().fit(X)
    assert np.round(p.explained_variance_, 2).tolist() == [4.23, 0.24, 0.08, 0.02]
    assert round(p.explained_variance_ratio_[0], 3) == 0.925
    assert round(p.explained_variance_ratio_[:2].sum(), 3) == 0.978
    assert np.allclose(p.explained_variance_, pca.pca_eig(X, 4)[0])        # SVD route = eigen route
