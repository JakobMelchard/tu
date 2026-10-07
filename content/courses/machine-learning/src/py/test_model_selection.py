import numpy as np
import pytest
from scipy import stats
from sklearn import model_selection as skms
from sklearn.datasets import make_classification
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import accuracy_score

import model_selection as ms

X, y = make_classification(200, 6, n_informative=3, random_state=0)


def test_splits_are_partitions():
    Xtr, Xte, ytr, yte = ms.train_test_split(X, y, 0.3, stratify=True, rng=0)
    assert len(yte) == 60 and len(ytr) == 140
    assert abs(ytr.mean() - yte.mean()) < 0.05
    for tr, te in ms.stratified_kfold(y, 5, rng=0):
        assert len(np.intersect1d(tr, te)) == 0 and len(tr) + len(te) == len(y)
        assert abs(y[te].mean() - y.mean()) < 0.06
    tests = np.concatenate([te for _, te in ms.kfold(len(y), 4, rng=0)])
    assert np.array_equal(np.sort(tests), np.arange(len(y)))


def test_cross_val_score_matches_sklearn_in_mean():
    knn = KNeighborsClassifier(5)
    ours = ms.cross_val_score(knn, X, y, accuracy_score, k=5, rng=0)
    theirs = skms.cross_val_score(knn, X, y, cv=skms.StratifiedKFold(5, shuffle=True, random_state=0))
    assert abs(ours.mean() - theirs.mean()) < 0.05


def test_grid_search_agrees_with_sklearn():
    grid = {"n_neighbors": [1, 5, 25]}
    best, score, _ = ms.grid_search(KNeighborsClassifier(), grid, X, y, accuracy_score, k=5)
    gs = skms.GridSearchCV(KNeighborsClassifier(), grid, cv=skms.StratifiedKFold(5, shuffle=True, random_state=0)).fit(X, y)
    assert abs(score - gs.best_score_) < 0.05
    assert best["n_neighbors"] in (gs.best_params_["n_neighbors"], 5)


def test_nested_cv_and_random_search_run():
    scores, chosen = ms.nested_cv(KNeighborsClassifier(), {"n_neighbors": [1, 5]}, X, y, accuracy_score, 3, 2)
    assert len(scores) == 3 and all(c["n_neighbors"] in (1, 5) for c in chosen)
    best, s, res = ms.random_search(KNeighborsClassifier(), {"n_neighbors": stats.randint(1, 10)}, X, y, accuracy_score, 4, 3)
    assert len(res) == 4 and 1 <= best["n_neighbors"] < 10


def test_learning_curve_shapes():
    sizes, tr, va = ms.learning_curve(KNeighborsClassifier(1), X, y, accuracy_score, (0.2, 1.0), k=3)
    assert sizes[0] < sizes[1] and tr.shape == (2, 3)
    assert tr.mean() == pytest.approx(1.0)          # 1-NN memorises the training set


def test_stat_tests():
    a = np.array([0.80, 0.82, 0.79, 0.85, 0.81]); b = a - 0.03 + np.array([0.005, -0.004, 0.002, -0.006, 0.003])
    t, p = ms.paired_t_test(a, b)
    st = stats.ttest_rel(a, b)
    assert t == pytest.approx(st.statistic) and p == pytest.approx(st.pvalue)
    tc, pc = ms.corrected_resampled_t_test(a, b, 160, 40)
    assert abs(tc) < abs(t) and pc > p
    yt = np.zeros(100, int); pa = yt.copy(); pb = yt.copy(); pa[:5] = 1; pb[:20] = 1   # A wrong 5x, B wrong 20x
    chi2, pv = ms.mcnemar_test(yt, pa, pb)
    assert chi2 == pytest.approx((15 - 1) ** 2 / 15) and pv < 0.01   # b=15 (A right, B wrong), c=0


# ---------------------------------------------- numbers quoted in notes 04 and 15
def _note_data():
    return make_classification(300, 8, n_informative=4, random_state=0)


def test_note04_grid_and_nested_cv_numbers():
    """The worked example of note 04, as printed by `python model_selection.py`."""
    X, y = _note_data()
    grid = {"n_neighbors": [1, 3, 5, 9, 15]}
    best, score, res = ms.grid_search(KNeighborsClassifier(), grid, X, y, accuracy_score)
    assert best == {"n_neighbors": 9} and round(score, 3) == 0.940
    assert [round(m, 3) for _, m, _ in res] == [0.920, 0.930, 0.937, 0.940, 0.927]
    outer, chosen = ms.nested_cv(KNeighborsClassifier(), grid, X, y, accuracy_score)
    assert [c["n_neighbors"] for c in chosen] == [5] * 5
    assert round(outer.mean(), 3) == 0.937 and round(outer.std(), 3) == 0.027


def test_random_search_resolves_k_more_finely_than_grid_at_equal_budget():
    """Note 15 [S37]: 16 evaluations each; the grid can only try 4 values of k."""
    X, y = _note_data()
    grid16 = {"n_neighbors": [1, 20, 40, 60], "weights": ["uniform", "distance"], "p": [1, 2]}
    space = {"n_neighbors": list(range(1, 61)), "weights": ["uniform", "distance"], "p": [1, 2]}
    gb, gs, gres = ms.grid_search(KNeighborsClassifier(), grid16, X, y, accuracy_score)
    rb, rs, rres = ms.random_search(KNeighborsClassifier(), space, X, y, accuracy_score, n_iter=16)
    n_k = lambda res: len({p["n_neighbors"] for p, _, _ in res})
    assert len(gres) == len(rres) == 16
    assert (n_k(gres), n_k(rres)) == (4, 13)
    assert (gb["n_neighbors"], rb["n_neighbors"]) == (1, 5)
    assert (round(gs, 3), round(rs, 3)) == (0.927, 0.937)
