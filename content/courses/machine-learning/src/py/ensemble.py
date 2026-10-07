"""Ensembles from scratch on top of tree.DecisionTree: bagging with out-of-bag
score, random forests (bootstrap + random feature subset per split) [S33],
permutation importance, AdaBoost (SAMME) and gradient boosting from a 0R start
(squared loss, binary log loss with Newton leaves) [S34].

Serves note 07 (ensembles).  AdaBoost here uses SAMME,
alpha = log((1-err)/err) + log(K-1).  For K = 2 that is exactly twice the
course's alpha = 1/2 log((1-err)/err) [S13], and the sample weights agree after
normalisation: both multiply a misclassified weight relative to a correct one by
(1-err)/err.  test_ensemble.py pins this on E19b's three-point example.

Cross-checked against sklearn.ensemble in test_ensemble.py.  Run
`python ensemble.py` for the numbers quoted in note 07.
"""
import numpy as np
from model_selection import BaseEstimator
from tree import DecisionTree


def _vote(P_list):
    return np.mean(P_list, axis=0)


class Bagging(BaseEstimator):
    """Bootstrap aggregating: n_estimators clones of base fit on bootstrap samples, averaged."""

    def __init__(self, base=None, n_estimators=10, rng=0):
        self.base, self.n_estimators, self.rng = base, n_estimators, rng

    def fit(self, X, y):
        X, y = np.asarray(X, float), np.asarray(y)
        r = np.random.default_rng(self.rng)
        self.estimators_, self.oob_masks_ = [], []
        for _ in range(self.n_estimators):
            idx = r.integers(0, len(y), len(y))                 # sample n with replacement
            self.estimators_.append(self._make().fit(X[idx], y[idx]))
            self.oob_masks_.append(~np.isin(np.arange(len(y)), idx))
        self.classes_ = getattr(self.estimators_[0], "classes_", None)
        self._oob(X, y)
        return self

    def _make(self):
        return (self.base or DecisionTree()).clone()

    def _oob(self, X, y):
        """Out-of-bag score: each sample predicted only by trees that did not see it (~36.8%)."""
        if self.classes_ is None:
            pred, cnt = np.zeros(len(y)), np.zeros(len(y))
            for m, oob in zip(self.estimators_, self.oob_masks_):
                pred[oob] += m.predict(X[oob]); cnt[oob] += 1
            ok = cnt > 0
            self.oob_score_ = 1 - np.sum((y[ok] - pred[ok] / cnt[ok]) ** 2) / np.sum((y[ok] - y[ok].mean()) ** 2)
        else:
            P, cnt = np.zeros((len(y), len(self.classes_))), np.zeros(len(y))
            for m, oob in zip(self.estimators_, self.oob_masks_):
                P[oob] += m.predict_proba(X[oob]); cnt[oob] += 1
            ok = cnt > 0
            self.oob_score_ = float(np.mean(self.classes_[P[ok].argmax(1)] == y[ok]))

    def predict_proba(self, X):
        return _vote([m.predict_proba(X) for m in self.estimators_])

    def predict(self, X):
        if self.classes_ is None:
            return _vote([m.predict(X) for m in self.estimators_])
        return self.classes_[np.argmax(self.predict_proba(X), 1)]


class RandomForest(Bagging):
    """Bagging + random feature subset at every split (max_features='sqrt') to decorrelate trees."""

    def __init__(self, n_estimators=50, criterion="gini", max_depth=None, min_samples_leaf=1, max_features="sqrt", rng=0):
        self.n_estimators, self.criterion, self.max_depth = n_estimators, criterion, max_depth
        self.min_samples_leaf, self.max_features, self.rng = min_samples_leaf, max_features, rng
        self.base = None

    def _make(self):
        seed = int(np.random.default_rng(self.rng).integers(1 << 30)) + len(self.estimators_)
        return DecisionTree(self.criterion, self.max_depth, min_samples_leaf=self.min_samples_leaf,
                            max_features=self.max_features, rng=seed)

    @property
    def feature_importances_(self):
        return np.mean([t.feature_importances_ for t in self.estimators_], axis=0)


def permutation_importance(model, X, y, scorer, n_repeats=5, rng=0):
    """Drop in score when one feature column is shuffled (model-agnostic, uses held-out data)."""
    r = np.random.default_rng(rng)
    X = np.asarray(X, float)
    base = scorer(y, model.predict(X))
    imp = np.zeros(X.shape[1])
    for j in range(X.shape[1]):
        for _ in range(n_repeats):
            Xp = X.copy(); Xp[:, j] = r.permutation(Xp[:, j])
            imp[j] += (base - scorer(y, model.predict(Xp))) / n_repeats
    return imp


class AdaBoost(BaseEstimator):
    """SAMME: reweight samples so the next stump focuses on the current mistakes.
    alpha_m = log((1-err)/err) + log(K-1); final vote = sum_m alpha_m [h_m(x) = c]."""

    def __init__(self, n_estimators=50, max_depth=1, learning_rate=1.0):
        self.n_estimators, self.max_depth, self.learning_rate = n_estimators, max_depth, learning_rate

    def fit(self, X, y):
        X, y = np.asarray(X, float), np.asarray(y)
        self.classes_ = np.unique(y)
        K, n = len(self.classes_), len(y)
        w = np.full(n, 1 / n)
        self.estimators_, self.alphas_, self.errors_ = [], [], []
        for _ in range(self.n_estimators):
            h = DecisionTree("gini", max_depth=self.max_depth).fit(X, y, sample_weight=w)
            miss = h.predict(X) != y
            err = np.sum(w * miss) / w.sum()
            if err >= 1 - 1 / K:                    # worse than random guessing: stop
                break
            alpha = self.learning_rate * (np.log((1 - err) / max(err, 1e-12)) + np.log(K - 1))
            w *= np.exp(alpha * miss)
            w /= w.sum()
            self.estimators_.append(h); self.alphas_.append(alpha); self.errors_.append(err)
            if err == 0:
                break
        self.sample_weight_ = w                     # weights after the last round
        return self

    def decision_function(self, X):
        F = np.zeros((len(X), len(self.classes_)))
        for h, a in zip(self.estimators_, self.alphas_):
            F += a * (h.predict(X)[:, None] == self.classes_[None, :])
        return F

    def predict(self, X):
        return self.classes_[np.argmax(self.decision_function(X), 1)]


class GradientBoosting(BaseEstimator):
    """Stagewise additive model F_m = F_{m-1} + lr * h_m, h_m a regression tree fit to the
    negative gradient of the loss.  loss='squared' (regression) or 'log' (binary classification,
    leaf values by one Newton step: sum(r) / sum(p(1-p)))."""

    def __init__(self, n_estimators=100, learning_rate=0.1, max_depth=3, loss="squared", subsample=1.0, rng=0):
        self.n_estimators, self.learning_rate, self.max_depth = n_estimators, learning_rate, max_depth
        self.loss, self.subsample, self.rng = loss, subsample, rng

    def fit(self, X, y):
        X, y = np.asarray(X, float), np.asarray(y, float)
        r = np.random.default_rng(self.rng)
        if self.loss == "log":
            p0 = np.clip(y.mean(), 1e-6, 1 - 1e-6)
            self.f0_ = np.log(p0 / (1 - p0))            # log-odds of the prior
        else:
            self.f0_ = y.mean()
        F = np.full(len(y), self.f0_)
        self.trees_ = []
        for _ in range(self.n_estimators):
            p = 1 / (1 + np.exp(-F)) if self.loss == "log" else F
            resid = y - p                              # negative gradient for both losses
            idx = r.choice(len(y), int(self.subsample * len(y)), replace=False) if self.subsample < 1 else slice(None)
            t = DecisionTree("mse", max_depth=self.max_depth).fit(X[idx], resid[idx])
            if self.loss == "log":                     # replace leaf means by Newton steps
                leaf = t.apply(X[idx]); hess = (p * (1 - p))[idx]
                for node in t.leaves():
                    m = leaf == node.leaf_id
                    node.value = resid[idx][m].sum() / max(hess[m].sum(), 1e-12)
            F += self.learning_rate * t.predict(X)
            self.trees_.append(t)
        return self

    def decision_function(self, X):
        F = np.full(len(X), self.f0_)
        for t in self.trees_:
            F += self.learning_rate * t.predict(X)
        return F

    def predict_proba(self, X):
        p = 1 / (1 + np.exp(-self.decision_function(X)))
        return np.column_stack([1 - p, p])

    def predict(self, X):
        F = self.decision_function(X)
        return (F > 0).astype(int) if self.loss == "log" else F


if __name__ == "__main__":
    from sklearn.datasets import make_classification, make_friedman1
    from model_selection import train_test_split
    from metrics import accuracy, r2

    X, y = make_classification(500, 10, n_informative=4, random_state=0)
    Xtr, Xte, ytr, yte = train_test_split(X, y, 0.3, stratify=True, rng=0)
    print("single tree   acc %.3f" % accuracy(yte, DecisionTree().fit(Xtr, ytr).predict(Xte)))
    bag = Bagging(DecisionTree(), 30).fit(Xtr, ytr)
    print("bagging       acc %.3f  (OOB %.3f)" % (accuracy(yte, bag.predict(Xte)), bag.oob_score_))
    rf = RandomForest(50).fit(Xtr, ytr)
    print("random forest acc %.3f  (OOB %.3f)" % (accuracy(yte, rf.predict(Xte)), rf.oob_score_))
    print("  impurity importance", rf.feature_importances_.round(2))
    print("  permutation importance", permutation_importance(rf, Xte, yte, accuracy).round(2))
    ada = AdaBoost(50).fit(Xtr, ytr)
    print("adaboost      acc %.3f  (%d stumps, first errors %s)" % (accuracy(yte, ada.predict(Xte)), len(ada.estimators_), np.round(ada.errors_[:3], 3)))
    gb = GradientBoosting(100, 0.1, 3, "log").fit(Xtr, ytr)
    print("grad boosting acc %.3f" % accuracy(yte, gb.predict(Xte)))
    Xr, yr = make_friedman1(400, noise=1.0, random_state=0)
    gbr = GradientBoosting(150, 0.1, 3).fit(Xr[:300], yr[:300])
    print("GB regression R2 %.3f" % r2(yr[300:], gbr.predict(Xr[300:])))
