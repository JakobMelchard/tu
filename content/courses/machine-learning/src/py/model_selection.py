"""Model selection from scratch: stratified hold-out split, k-fold CV, grid /
random search [S37], nested CV, learning and validation curves, and the
statistical comparison of two models (paired t-test, Nadeau-Bengio corrected
resampled t-test, McNemar) [S36].

Serves notes 01 (splits, leakage), 03 (CV protocols, significance tests), 04
(hyperparameter search, nested CV) and 15 (grid vs random search).  Estimators
only need fit / predict plus get_params / set_params (the small BaseEstimator
below), so the pure-numpy models of this folder and sklearn estimators both
work.  Cross-checked in test_model_selection.py against sklearn.model_selection
and scipy.stats.  Run `python model_selection.py` for the numbers quoted in
notes 04 and 15.
"""
import itertools
import numpy as np
from scipy import stats


class BaseEstimator:
    """Minimal clone/params support for the from-scratch models."""

    def get_params(self):
        return {k: v for k, v in vars(self).items() if not k.endswith("_")}

    def set_params(self, **p):
        for k, v in p.items():
            setattr(self, k, v)
        return self

    def clone(self):
        return type(self)(**self.get_params())


def _clone(est):
    if hasattr(est, "clone"):
        return est.clone()
    from sklearn.base import clone
    return clone(est)


def train_test_split(X, y, test_size=0.25, stratify=False, rng=0):
    """Hold-out split; stratify=True draws test_size of every class separately."""
    rng = np.random.default_rng(rng)
    X, y = np.asarray(X), np.asarray(y)
    n_test = int(round(test_size * len(y)))
    if stratify:
        test = np.concatenate([rng.choice(np.where(y == c)[0], int(round(test_size * np.sum(y == c))), replace=False)
                               for c in np.unique(y)])
    else:
        test = rng.choice(len(y), n_test, replace=False)
    train = np.setdiff1d(np.arange(len(y)), test)
    return X[train], X[test], y[train], y[test]


def kfold(n, k=5, shuffle=True, rng=0):
    """Yield (train_idx, test_idx) for k folds."""
    idx = np.arange(n)
    if shuffle:
        np.random.default_rng(rng).shuffle(idx)
    for fold in np.array_split(idx, k):
        yield np.setdiff1d(idx, fold), fold


def stratified_kfold(y, k=5, rng=0):
    """Each fold keeps the class proportions of y."""
    rng = np.random.default_rng(rng)
    y = np.asarray(y)
    folds = [[] for _ in range(k)]
    for c in np.unique(y):
        ci = np.where(y == c)[0]
        rng.shuffle(ci)
        for f, part in enumerate(np.array_split(ci, k)):
            folds[f].extend(part)
    for f in folds:
        test = np.array(sorted(f))
        yield np.setdiff1d(np.arange(len(y)), test), test


def cross_val_score(est, X, y, scorer, k=5, stratified=True, rng=0):
    """Fit a fresh clone per fold; return the k held-out scores (mean +- std is what you report)."""
    X, y = np.asarray(X), np.asarray(y)
    splits = stratified_kfold(y, k, rng) if stratified else kfold(len(y), k, rng=rng)
    scores = []
    for tr, te in splits:
        m = _clone(est).fit(X[tr], y[tr])
        scores.append(scorer(y[te], m.predict(X[te])))
    return np.array(scores)


def cross_val_predict(est, X, y, k=5, rng=0):
    """Out-of-fold predictions for every sample (for paired tests / McNemar)."""
    X, y = np.asarray(X), np.asarray(y)
    pred = np.empty_like(y)
    for tr, te in stratified_kfold(y, k, rng):
        pred[te] = _clone(est).fit(X[tr], y[tr]).predict(X[te])
    return pred


def param_grid(grid):
    keys = list(grid)
    for vals in itertools.product(*(grid[k] for k in keys)):
        yield dict(zip(keys, vals))


def grid_search(est, grid, X, y, scorer, k=5, rng=0):
    """Exhaustive search; returns (best_params, best_score, results list)."""
    results = []
    for p in param_grid(grid):
        s = cross_val_score(_clone(est).set_params(**p), X, y, scorer, k, rng=rng)
        results.append((p, s.mean(), s.std()))
    best = max(results, key=lambda r: r[1])
    return best[0], best[1], results


def random_search(est, dists, X, y, scorer, n_iter=10, k=5, rng=0):
    """dists: name -> list (sampled uniformly) or scipy frozen distribution (.rvs)."""
    r = np.random.default_rng(rng)
    results = []
    for _ in range(n_iter):
        p = {n: (d.rvs(random_state=r) if hasattr(d, "rvs") else d[r.integers(len(d))]) for n, d in dists.items()}
        s = cross_val_score(_clone(est).set_params(**p), X, y, scorer, k, rng=rng)
        results.append((p, s.mean(), s.std()))
    best = max(results, key=lambda r: r[1])
    return best[0], best[1], results


def nested_cv(est, grid, X, y, scorer, outer_k=5, inner_k=3, rng=0):
    """Outer loop estimates generalisation of the *whole procedure* (search + fit).
    Inner loop chooses hyperparameters on the outer-train part only."""
    X, y = np.asarray(X), np.asarray(y)
    scores, chosen = [], []
    for tr, te in stratified_kfold(y, outer_k, rng):
        best, _, _ = grid_search(est, grid, X[tr], y[tr], scorer, inner_k, rng)
        m = _clone(est).set_params(**best).fit(X[tr], y[tr])
        scores.append(scorer(y[te], m.predict(X[te])))
        chosen.append(best)
    return np.array(scores), chosen


def learning_curve(est, X, y, scorer, train_sizes=(0.1, 0.25, 0.5, 0.75, 1.0), k=5, rng=0):
    """Train and validation score vs. number of training samples (diagnoses bias vs variance)."""
    X, y = np.asarray(X), np.asarray(y)
    sizes, tr_sc, va_sc = [], [], []
    for frac in train_sizes:
        t, v = [], []
        for tr, te in stratified_kfold(y, k, rng):
            sub = tr[: max(2, int(frac * len(tr)))]
            m = _clone(est).fit(X[sub], y[sub])
            t.append(scorer(y[sub], m.predict(X[sub])))
            v.append(scorer(y[te], m.predict(X[te])))
        sizes.append(len(sub)); tr_sc.append(t); va_sc.append(v)
    return np.array(sizes), np.array(tr_sc), np.array(va_sc)


def validation_curve(est, name, values, X, y, scorer, k=5, rng=0):
    """Validation score vs. one hyperparameter (train score too, to see over/underfitting)."""
    X, y = np.asarray(X), np.asarray(y)
    tr_sc, va_sc = [], []
    for v in values:
        t, va = [], []
        for tr, te in stratified_kfold(y, k, rng):
            m = _clone(est).set_params(**{name: v}).fit(X[tr], y[tr])
            t.append(scorer(y[tr], m.predict(X[tr]))); va.append(scorer(y[te], m.predict(X[te])))
        tr_sc.append(t); va_sc.append(va)
    return np.array(tr_sc), np.array(va_sc)


# ------------------------------------------------- statistical comparison
def paired_t_test(scores_a, scores_b):
    """Paired t-test over folds (same splits for both models). Returns (t, p two-sided).
    Caveat: folds overlap, so the variance is underestimated -> optimistic p."""
    d = np.asarray(scores_a) - np.asarray(scores_b)
    t = d.mean() / (d.std(ddof=1) / np.sqrt(len(d)))
    return float(t), float(2 * stats.t.sf(abs(t), len(d) - 1))


def corrected_resampled_t_test(scores_a, scores_b, n_train, n_test):
    """Nadeau & Bengio correction: variance scaled by (1/k + n_test/n_train)."""
    d = np.asarray(scores_a) - np.asarray(scores_b)
    k = len(d)
    var = d.var(ddof=1) * (1 / k + n_test / n_train)
    t = d.mean() / np.sqrt(var)
    return float(t), float(2 * stats.t.sf(abs(t), k - 1))


def mcnemar_test(y_true, pred_a, pred_b):
    """McNemar on disagreements: b = A right & B wrong, c = A wrong & B right.
    chi2 = (|b - c| - 1)^2 / (b + c) with continuity correction, 1 dof."""
    y_true, pred_a, pred_b = map(np.asarray, (y_true, pred_a, pred_b))
    b = np.sum((pred_a == y_true) & (pred_b != y_true))
    c = np.sum((pred_a != y_true) & (pred_b == y_true))
    if b + c == 0:
        return 0.0, 1.0
    chi2 = (abs(b - c) - 1) ** 2 / (b + c)
    return float(chi2), float(stats.chi2.sf(chi2, 1))


if __name__ == "__main__":
    from sklearn.datasets import make_classification
    from sklearn.neighbors import KNeighborsClassifier
    from sklearn.tree import DecisionTreeClassifier
    from metrics import accuracy

    X, y = make_classification(300, 8, n_informative=4, random_state=0)
    knn = KNeighborsClassifier()
    best, score, res = grid_search(knn, {"n_neighbors": [1, 3, 5, 9, 15]}, X, y, accuracy)
    print("grid search:", best, "cv acc %.3f" % score)
    outer, chosen = nested_cv(knn, {"n_neighbors": [1, 3, 5, 9, 15]}, X, y, accuracy)
    print("nested CV acc %.3f +- %.3f, chosen k per fold %s" % (outer.mean(), outer.std(), [c["n_neighbors"] for c in chosen]))
    sizes, tr, va = learning_curve(DecisionTreeClassifier(random_state=0), X, y, accuracy)
    print("learning curve sizes", sizes, "train", tr.mean(1).round(3), "val", va.mean(1).round(3))
    sa = cross_val_score(knn, X, y, accuracy, k=10)
    sb = cross_val_score(DecisionTreeClassifier(random_state=0), X, y, accuracy, k=10)
    print("kNN vs tree: paired t p=%.3f, corrected p=%.3f" % (paired_t_test(sa, sb)[1], corrected_resampled_t_test(sa, sb, 270, 30)[1]))
    pa, pb = cross_val_predict(knn, X, y), cross_val_predict(DecisionTreeClassifier(random_state=0), X, y)
    print("McNemar chi2=%.2f p=%.3f" % mcnemar_test(y, pa, pb))

    # note 15 [S37]: grid vs random search at the same budget of 16 CV evaluations
    grid16 = {"n_neighbors": [1, 20, 40, 60], "weights": ["uniform", "distance"], "p": [1, 2]}
    space = {"n_neighbors": list(range(1, 61)), "weights": ["uniform", "distance"], "p": [1, 2]}
    gb, gs, gres = grid_search(knn, grid16, X, y, accuracy)
    rb, rs, rres = random_search(knn, space, X, y, accuracy, n_iter=16)
    n_k = lambda res: len({p["n_neighbors"] for p, _, _ in res})
    print("grid   (16 evals): %2d distinct k, best k=%2d cv acc %.3f" % (n_k(gres), gb["n_neighbors"], gs))
    print("random (16 evals): %2d distinct k, best k=%2d cv acc %.3f" % (n_k(rres), rb["n_neighbors"], rs))
