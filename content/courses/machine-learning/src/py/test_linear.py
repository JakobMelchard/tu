import numpy as np
import pytest
from sklearn import linear_model as sklm
from sklearn.preprocessing import PolynomialFeatures
from sklearn.datasets import make_regression, make_classification

import linear as lin

X, y = make_regression(150, 6, n_informative=3, noise=3.0, random_state=0)
Xc, yc = make_classification(300, 5, n_informative=3, n_redundant=0, random_state=0)


@pytest.mark.parametrize("solver", ["lstsq", "normal", "gd"])
def test_ols(solver):
    ours = lin.LinearRegression(solver, lr=0.05, n_iter=5000).fit(X, y)
    theirs = sklm.LinearRegression().fit(X, y)
    assert np.allclose(ours.coef_, theirs.coef_, atol=1e-2) and ours.intercept_ == pytest.approx(theirs.intercept_, abs=1e-2)


def test_ridge():
    ours, theirs = lin.Ridge(5.0).fit(X, y), sklm.Ridge(5.0).fit(X, y)
    assert np.allclose(ours.coef_, theirs.coef_, atol=1e-6) and ours.intercept_ == pytest.approx(theirs.intercept_)


def test_lasso():
    ours, theirs = lin.Lasso(2.0, n_iter=2000, tol=1e-9).fit(X, y), sklm.Lasso(2.0, tol=1e-9).fit(X, y)
    assert np.allclose(ours.coef_, theirs.coef_, atol=1e-3)
    assert np.sum(np.abs(ours.coef_) < 1e-8) >= 2                         # sparsity


@pytest.mark.parametrize("solver", ["gd", "newton"])
def test_logistic(solver):
    ours = lin.LogisticRegression(l2=1.0, lr=0.5, n_iter=20000, solver=solver).fit(Xc, yc)
    theirs = sklm.LogisticRegression(C=1.0).fit(Xc, yc)   # C=1 <=> l2=1 with sklearn's sum-loss scaling
    assert np.allclose(ours.coef_, theirs.coef_[0], atol=2e-2)
    assert np.mean(ours.predict(Xc) == theirs.predict(Xc)) > 0.99


def test_softmax():
    Xm, ym = make_classification(300, 5, n_informative=3, n_redundant=0, n_classes=3, random_state=1)
    ours = lin.SoftmaxRegression(lr=0.5, n_iter=5000).fit(Xm, ym)
    theirs = sklm.LogisticRegression(C=np.inf, max_iter=2000).fit(Xm, ym)
    assert np.mean(ours.predict(Xm) == theirs.predict(Xm)) > 0.95


def test_polynomial_features():
    A = np.random.default_rng(0).normal(size=(10, 2))
    assert np.allclose(lin.polynomial_features(A, 3), PolynomialFeatures(3, include_bias=False).fit_transform(A))
