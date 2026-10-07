import numpy as np
import pytest
from sklearn.tree import DecisionTreeClassifier, DecisionTreeRegressor
from sklearn.datasets import make_classification, make_regression, load_iris

import tree

X, y = make_classification(300, 6, n_informative=4, n_classes=3, random_state=2)
Xtr, Xte, ytr, yte = X[:220], X[220:], y[:220], y[220:]


def test_impurities():
    assert tree.entropy(np.array([0.5, 0.5])) == pytest.approx(1.0)
    assert tree.gini(np.array([0.5, 0.5])) == pytest.approx(0.5)
    assert tree.information_gain(np.array([1, 1, 0, 0]), [np.array([1, 1]), np.array([0, 0])]) == pytest.approx(1.0)


@pytest.mark.parametrize("criterion", ["gini", "entropy"])
def test_full_tree_matches_sklearn(criterion):
    ours = tree.DecisionTree(criterion).fit(Xtr, ytr)
    theirs = DecisionTreeClassifier(criterion=criterion, random_state=0).fit(Xtr, ytr)
    assert ours.predict(Xtr).tolist() == ytr.tolist()              # pure leaves on training data
    assert np.mean(ours.predict(Xte) == theirs.predict(Xte)) > 0.85
    assert abs(ours.n_leaves_ - theirs.get_n_leaves()) <= 3


def test_depth_limited_tree_close_to_sklearn():
    ours = tree.DecisionTree("gini", max_depth=3, min_samples_leaf=5).fit(Xtr, ytr)
    theirs = DecisionTreeClassifier(max_depth=3, min_samples_leaf=5, random_state=0).fit(Xtr, ytr)
    assert ours.depth() == 3
    assert np.mean(ours.predict(Xte) == theirs.predict(Xte)) > 0.9
    # first split identical (deterministic best split over all features)
    assert ours.root_.feature == theirs.tree_.feature[0]
    assert ours.root_.threshold == pytest.approx(theirs.tree_.threshold[0], abs=1e-6)


def test_regression_tree():
    Xr, yr = make_regression(200, 3, noise=5.0, random_state=0)
    ours = tree.DecisionTree("mse", max_depth=4).fit(Xr[:150], yr[:150]).predict(Xr[150:])
    theirs = DecisionTreeRegressor(max_depth=4, random_state=0).fit(Xr[:150], yr[:150]).predict(Xr[150:])
    assert np.corrcoef(ours, theirs)[0, 1] > 0.95


def test_ccp_pruning_reduces_leaves_like_sklearn():
    d = load_iris()
    for alpha in (0.01, 0.05):
        ours = tree.DecisionTree("gini", ccp_alpha=alpha).fit(d.data, d.target)
        theirs = DecisionTreeClassifier(ccp_alpha=alpha, random_state=0).fit(d.data, d.target)
        assert ours.n_leaves_ == theirs.get_n_leaves()


def test_sample_weights_and_importances():
    w = np.where(ytr == 0, 5.0, 1.0)
    ours = tree.DecisionTree("gini", max_depth=2).fit(Xtr, ytr, sample_weight=w)
    theirs = DecisionTreeClassifier(max_depth=2, random_state=0).fit(Xtr, ytr, sample_weight=w)
    assert ours.root_.feature == theirs.tree_.feature[0]
    assert np.allclose(ours.feature_importances_, theirs.feature_importances_, atol=0.05)
    assert len(np.unique(ours.apply(Xtr))) == ours.n_leaves_
