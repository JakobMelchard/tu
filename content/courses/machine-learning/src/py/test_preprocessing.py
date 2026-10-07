import numpy as np
import pytest
from sklearn import preprocessing as skp, impute as ski, feature_selection as skf
from sklearn.metrics import mutual_info_score

import preprocessing as pp

rng = np.random.default_rng(0)
X = rng.normal([1, 10, -3], [2, 5, 0.5], (100, 3))


def test_scalers():
    assert np.allclose(pp.StandardScaler().fit_transform(X), skp.StandardScaler().fit_transform(X))
    assert np.allclose(pp.MinMaxScaler().fit_transform(X), skp.MinMaxScaler().fit_transform(X))
    assert np.allclose(pp.RobustScaler().fit_transform(X), skp.RobustScaler().fit_transform(X))
    sc = pp.StandardScaler().fit(X)
    assert np.allclose(sc.inverse_transform(sc.transform(X)), X)


def test_one_hot_and_ordinal():
    C = np.array([["a", "x"], ["b", "y"], ["a", "z"], ["c", "x"]], dtype=object)
    assert np.array_equal(pp.OneHotEncoder().fit_transform(C), skp.OneHotEncoder(sparse_output=False).fit_transform(C))
    assert np.array_equal(pp.OrdinalEncoder().fit(C).transform(C), skp.OrdinalEncoder().fit_transform(C))


@pytest.mark.parametrize("strategy", ["mean", "median", "most_frequent"])
def test_imputer(strategy):
    Xn = X.copy()
    Xn[rng.random(Xn.shape) < 0.1] = np.nan
    assert np.allclose(pp.SimpleImputer(strategy).fit_transform(Xn), ski.SimpleImputer(strategy=strategy).fit_transform(Xn))


def test_knn_impute_close_to_sklearn():
    Xn = X.copy()
    Xn[rng.random(Xn.shape) < 0.05] = np.nan
    ours, theirs = pp.knn_impute(Xn, k=3), ski.KNNImputer(n_neighbors=3).fit_transform(Xn)
    assert np.allclose(ours, theirs)


def test_outliers_flag_planted_point():
    Xo = X.copy(); Xo[7] = [30, 10, -3]
    assert pp.zscore_outliers(Xo)[7] and pp.iqr_outliers(Xo)[7]
    assert pp.iqr_outliers(Xo).sum() < 10


def test_feature_selection():
    y = (X[:, 0] + rng.normal(0, 0.5, 100) > 1).astype(int)
    assert np.allclose(pp.anova_f(X, y), skf.f_classif(X, y)[0])
    Xc = np.column_stack([X, X[:, 0] * 2 + 1e-9])
    assert list(pp.correlation_filter(Xc)) == [True, True, True, False]
    assert list(pp.variance_threshold(np.column_stack([X, np.ones(100)]))) == [True, True, True, False]
    a, b = rng.integers(0, 3, 200), rng.integers(0, 2, 200)
    assert pp.mutual_information_discrete(a, b) == pytest.approx(mutual_info_score(a, b))


def test_resampling():
    y = (rng.random(100) < 0.2).astype(int)
    _, yo = pp.random_oversample(X, y, rng=0)
    assert np.bincount(yo)[0] == np.bincount(yo)[1]
    _, yu = pp.random_undersample(X, y, rng=0)
    assert np.bincount(yu)[0] == np.bincount(yu)[1] == y.sum()
    Xs, ys = pp.smote(X, y, minority=1, rng=0)
    assert np.bincount(ys)[0] == np.bincount(ys)[1]
    assert Xs[len(X):].min(0).min() >= X[y == 1].min(0).min() - 1e-9   # convex combos stay in hull
    w = pp.class_weights(y)
    assert w[1] > w[0]
