import numpy as np
import pytest
from sklearn.ensemble import (RandomForestClassifier, AdaBoostClassifier, GradientBoostingClassifier,
                              GradientBoostingRegressor, BaggingClassifier)
from sklearn.tree import DecisionTreeClassifier
from sklearn.datasets import make_classification, make_friedman1
from sklearn.metrics import accuracy_score, r2_score

import ensemble as en
from tree import DecisionTree

X, y = make_classification(400, 8, n_informative=4, n_redundant=0, random_state=3)
Xtr, Xte, ytr, yte = X[:300], X[300:], y[:300], y[300:]


def test_bagging_beats_single_tree_and_matches_sklearn():
    single = accuracy_score(yte, DecisionTree().fit(Xtr, ytr).predict(Xte))
    bag = en.Bagging(DecisionTree(), 20).fit(Xtr, ytr)
    theirs = BaggingClassifier(DecisionTreeClassifier(), n_estimators=20, oob_score=True, random_state=0).fit(Xtr, ytr)
    ours = accuracy_score(yte, bag.predict(Xte))
    assert ours >= single - 0.02
    assert abs(ours - theirs.score(Xte, yte)) < 0.08
    assert abs(bag.oob_score_ - theirs.oob_score_) < 0.08


def test_random_forest_matches_sklearn():
    rf = en.RandomForest(40, rng=0).fit(Xtr, ytr)
    theirs = RandomForestClassifier(40, oob_score=True, random_state=0).fit(Xtr, ytr)
    assert abs(accuracy_score(yte, rf.predict(Xte)) - theirs.score(Xte, yte)) < 0.08
    assert abs(rf.oob_score_ - theirs.oob_score_) < 0.08
    # informative features rank higher in both importance measures
    top_ours = set(np.argsort(rf.feature_importances_)[-4:]); top_theirs = set(np.argsort(theirs.feature_importances_)[-4:])
    assert len(top_ours & top_theirs) >= 3
    pi = en.permutation_importance(rf, Xte, yte, accuracy_score, n_repeats=3)
    assert len(set(np.argsort(pi)[-4:]) & top_theirs) >= 2


def test_adaboost_matches_sklearn():
    ada = en.AdaBoost(30).fit(Xtr, ytr)
    theirs = AdaBoostClassifier(n_estimators=30, random_state=0).fit(Xtr, ytr)
    assert abs(accuracy_score(yte, ada.predict(Xte)) - theirs.score(Xte, yte)) < 0.08
    assert np.allclose(ada.errors_[0], theirs.estimator_errors_[0], atol=1e-6)   # first stump identical


def test_gradient_boosting_classifier():
    gb = en.GradientBoosting(60, 0.1, 2, "log").fit(Xtr, ytr)
    theirs = GradientBoostingClassifier(n_estimators=60, learning_rate=0.1, max_depth=2, random_state=0).fit(Xtr, ytr)
    assert abs(accuracy_score(yte, gb.predict(Xte)) - theirs.score(Xte, yte)) < 0.08
    assert np.corrcoef(gb.decision_function(Xte), theirs.decision_function(Xte))[0, 1] > 0.9


def test_gradient_boosting_regressor():
    Xr, yr = make_friedman1(300, noise=1.0, random_state=0)
    gb = en.GradientBoosting(80, 0.1, 3).fit(Xr[:220], yr[:220])
    theirs = GradientBoostingRegressor(n_estimators=80, learning_rate=0.1, max_depth=3, random_state=0).fit(Xr[:220], yr[:220])
    assert abs(r2_score(yr[220:], gb.predict(Xr[220:])) - theirs.score(Xr[220:], yr[220:])) < 0.1


def test_adaboost_reproduces_the_course_weights_on_e19b():
    """E19b / E20b: x = 1, 3, 5 with labels -1, +1, -1.  Weights start at 1/n (the
    graded answer [S12]); one stump errs on one point, err = 1/3; the course's
    alpha = 1/2 log((1-err)/err) = 1/2 log 2 [S13] and SAMME's is twice that; after
    normalisation both give the misclassified point weight 1/2, the others 1/4."""
    x, y = np.array([[1.0], [3.0], [5.0]]), np.array([-1, 1, -1])
    ada = en.AdaBoost(n_estimators=1).fit(x, y)
    err = 1 / 3
    assert ada.errors_[0] == pytest.approx(err)
    assert ada.alphas_[0] == pytest.approx(2 * 0.5 * np.log((1 - err) / err))
    assert sorted(ada.sample_weight_) == pytest.approx([0.25, 0.25, 0.5])
