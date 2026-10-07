"""Worked solution: exam of 18.10.2019 (label E19b, 2018W re-take).

Source of the questions: [S11] VoWi `Exam 2019-10-18`, a student's transcript
from memory.  The paper is described in our own words in README.md and is not
reproduced.  Where the paper gives no data (it never prints its tables), we
build a table of the stated shape and solve it with our own implementations.

Questions answered (numbers asserted in `check()`):
  Ex. 4  Which classifiers can separate two concentric rings?  Perceptron no
         (training accuracy about 0.5); RBF / quadratic SVM, 1-NN, decision
         tree yes (1.0).
  Ex. 5  AdaBoost on x = 1, 3, 5 with labels -1, +1, -1: initial weights
         1/n = 1/3 each (the graded answer [S12]); best stump error 1/3;
         alpha = 1/2 ln 2 = 0.3466 [S13]; weights after round 1 are
         (1/4, 1/4, 1/2), the misclassified point doubling relative to the rest.
  Ex. 6  Support vectors of four points: (2,2) and (3,3); w = (1, 1),
         b = -5, boundary x2 = 5 - x1 (slope -1), margin sqrt(2)/2.  Cross-
         checked against sklearn.svm.SVC(kernel="linear", C=1e6).
  Ex. 7  3-NN with Hamming distance on nominal attributes: A, B, B (unchanged
         without colour); naive Bayes without Laplace: likelihoods 2/15, 1/18,
         1/36 for the winning class, predictions A, B, B, precision = recall
         = 1 for class B.

Run:  ../../../../../.venv/bin/python solution.py
"""
import os
import sys

import numpy as np

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "py")))

from bayes import CategoricalNB              # noqa: E402
from knn import KNNClassifier                # noqa: E402
from metrics import confusion_matrix, precision_recall_f1   # noqa: E402
from tree import DecisionTree                # noqa: E402


# --- Exercise 7: 9 training points, 3 new points; 3-NN then naive Bayes -------
# The paper's own table is not public; this one has the stated shape (9 + 3 rows,
# mixed nominal attributes, binary target) so the method can be checked.
TRAIN = np.array([
    ["short", "red",   "round"],
    ["short", "red",   "square"],
    ["tall",  "blue",  "round"],
    ["tall",  "blue",  "square"],
    ["short", "green", "round"],
    ["tall",  "green", "square"],
    ["short", "blue",  "round"],
    ["tall",  "red",   "square"],
    ["short", "green", "square"],
], dtype=object)
Y = np.array(["A", "A", "B", "B", "A", "B", "A", "B", "A"])

TEST = np.array([
    ["short", "red",   "round"],
    ["tall",  "blue",  "round"],
    ["tall",  "green", "round"],
], dtype=object)
Y_TEST = np.array(["A", "B", "B"])


def _one_hot(X, values=None):
    """Nominal -> 0/1 columns, so a Euclidean distance equals the Hamming distance
    up to the factor sqrt(2) (a mismatch contributes 1 in each of two columns)."""
    values = values or [sorted({str(v) for v in X[:, j]}) for j in range(X.shape[1])]
    cols = [[1.0 if str(row[j]) == v else 0.0 for j in range(X.shape[1]) for v in values[j]]
            for row in X]
    return np.array(cols), values


def exercise_7_knn_and_naive_bayes():
    """(a) 3-NN with a justified distance; (b) drop one attribute; (c) naive Bayes
    without Laplace, then precision and recall."""
    # (a) All attributes are nominal, so the only defensible metric is Hamming:
    #     an ordinal or Euclidean coding would invent distances that are not in
    #     the data.  Encoding one-hot and using L2 gives the same neighbour order.
    Xtr, values = _one_hot(TRAIN)
    Xte, _ = _one_hot(TEST, values)
    knn3 = KNNClassifier(k=3, metric="euclidean").fit(Xtr, Y)
    pred_knn = knn3.predict(Xte)

    # (b) remove the second attribute (colour) and predict again
    Xtr2, values2 = _one_hot(TRAIN[:, [0, 2]])
    Xte2, _ = _one_hot(TEST[:, [0, 2]], values2)
    pred_knn_reduced = KNNClassifier(k=3, metric="euclidean").fit(Xtr2, Y).predict(Xte2)

    # (c) naive Bayes, explicitly without Laplace correction
    nb = CategoricalNB(course_laplace=False).fit(TRAIN, Y)
    pred_nb = nb.predict(TEST)
    likelihoods = [{str(k): float(v) for k, v in nb.likelihoods(row).items()} for row in TEST]
    p, r, _ = precision_recall_f1(Y_TEST, pred_nb, average="binary", pos_label="B")

    return dict(
        knn_predictions=[str(v) for v in pred_knn],
        knn_predictions_without_colour=[str(v) for v in pred_knn_reduced],
        colour_changed_a_prediction=not np.array_equal(pred_knn, pred_knn_reduced),
        nb_predictions=[str(v) for v in pred_nb],
        nb_likelihoods=likelihoods,
        precision_B=p,
        recall_B=r,
        confusion=confusion_matrix(Y_TEST, pred_nb, labels=["A", "B"]).tolist(),
        metric_choice="Hamming (all attributes nominal); one-hot + L2 gives the same order",
    )


# --- Exercise 5: AdaBoost on three points and a stump --------------------------
def exercise_5_adaboost_stump():
    """x = 1, 3, 5 with labels -1, +1, -1; a stump can make one split.

    Asked for: the initial weights, the first stump's boundary, and which point
    gains weight.  The graded answer to the first part is 1/n = 1/3 [S12].
    """
    x = np.array([1.0, 3.0, 5.0])
    y = np.array([-1.0, 1.0, -1.0])
    w = np.full(3, 1 / 3)

    # every stump on this data: threshold t, predict s for x <= t and -s above
    best = None
    for t in (2.0, 4.0):
        for s in (1.0, -1.0):
            pred = np.where(x <= t, s, -s)
            err = float(np.sum(w[pred != y]))
            if best is None or err < best["error"]:
                best = dict(threshold=t, sign=s, error=err, pred=pred)

    alpha = 0.5 * np.log((1 - best["error"]) / best["error"])
    w_new = w * np.exp(-alpha * y * best["pred"])
    w_new = w_new / w_new.sum()
    return dict(
        initial_weights=w.tolist(),
        best_stump_error=best["error"],
        alpha=float(alpha),
        weights_after_round_1=w_new.tolist(),
        upweighted_index=int(np.argmax(w_new)),
        misclassified=[int(i) for i in np.flatnonzero(best["pred"] != y)],
        note="no single split separates -1, +1, -1, so the best stump errs on one point",
    )


# --- Exercise 6: support vectors and the SVM boundary of four points -----------
def exercise_6_support_vectors():
    """Two points per class in the plane: circle the support vectors, draw the
    boundary and give its slope."""
    X = np.array([[1.0, 1.0], [2.0, 2.0], [3.0, 3.0], [4.0, 4.5]])
    y = np.array([-1.0, -1.0, 1.0, 1.0])
    # The two closest opposite points are (2,2) and (3,3); by symmetry the
    # boundary is their perpendicular bisector.
    a, b = X[1], X[2]
    midpoint = (a + b) / 2
    w = b - a                                  # normal direction
    bias = -float(w @ midpoint)
    margins = y * (X @ w + bias) / np.linalg.norm(w)
    slope = -w[0] / w[1]
    return dict(
        support_vectors=[int(i) for i in np.flatnonzero(np.isclose(margins, margins.min()))],
        w=w.tolist(),
        b=bias,
        boundary_slope=float(slope),
        margin=float(margins.min()),
        all_correct=bool(np.all(margins > 0)),
    )


# --- Exercise 4: decision boundaries on two concentric rings -------------------
def exercise_4_decision_boundaries():
    """Which classifiers can separate two concentric rings?

    Perceptron: no (one hyperplane).  SVM with a quadratic/RBF kernel: yes.
    1-NN: yes.  Decision tree: yes, but only with a staircase of axis-parallel
    splits.  We check the two we can run.
    """
    rng = np.random.default_rng(0)
    theta = rng.uniform(0, 2 * np.pi, 200)
    r = np.where(rng.random(200) < 0.5, 1.0, 3.0)
    X = np.c_[r * np.cos(theta), r * np.sin(theta)] + rng.normal(0, 0.1, (200, 2))
    y = (r > 2).astype(int)

    from sklearn.linear_model import Perceptron
    from sklearn.svm import SVC
    return dict(
        perceptron_train_accuracy=float(Perceptron(max_iter=2000, tol=1e-3, random_state=0)
                                        .fit(X, y).score(X, y)),
        svm_rbf_train_accuracy=float(SVC(kernel="rbf", gamma=1.0).fit(X, y).score(X, y)),
        svm_poly2_train_accuracy=float(SVC(kernel="poly", degree=2).fit(X, y).score(X, y)),
        knn1_train_accuracy=float(KNNClassifier(k=1).fit(X, y).predict(X).__eq__(y).mean()),
        tree_train_accuracy=float(np.mean(DecisionTree(max_depth=8).fit(X, y).predict(X) == y)),
    )


def solve():
    return {
        "4": exercise_4_decision_boundaries(),
        "5": exercise_5_adaboost_stump(),
        "6": exercise_6_support_vectors(),
        "7": exercise_7_knn_and_naive_bayes(),
    }


def check(r):
    """Assert the numeric answers listed in the module docstring."""
    a = r["4"]
    assert a["perceptron_train_accuracy"] < 0.75
    assert a["svm_rbf_train_accuracy"] == a["svm_poly2_train_accuracy"] == 1.0
    assert a["knn1_train_accuracy"] == a["tree_train_accuracy"] == 1.0

    b = r["5"]
    assert np.allclose(b["initial_weights"], [1 / 3] * 3)
    assert np.isclose(b["best_stump_error"], 1 / 3)
    assert np.isclose(b["alpha"], 0.5 * np.log(2))
    assert np.allclose(b["weights_after_round_1"], [0.25, 0.25, 0.5])
    assert b["misclassified"] == [b["upweighted_index"]] == [2]

    c = r["6"]
    assert c["support_vectors"] == [1, 2] and c["all_correct"]
    assert np.allclose(c["w"], [1.0, 1.0]) and np.isclose(c["b"], -5.0)
    assert np.isclose(c["boundary_slope"], -1.0) and np.isclose(c["margin"], np.sqrt(2) / 2)
    # library cross-check: a hard-margin linear SVM finds the same hyperplane
    from sklearn.svm import SVC
    svc = SVC(kernel="linear", C=1e6).fit([[1, 1], [2, 2], [3, 3], [4, 4.5]], [-1, -1, 1, 1])
    assert sorted(svc.support_.tolist()) == [1, 2]
    assert np.allclose(svc.coef_[0], c["w"], atol=1e-3) and np.isclose(svc.intercept_[0], c["b"], atol=1e-3)

    d = r["7"]
    assert d["knn_predictions"] == d["knn_predictions_without_colour"] == ["A", "B", "B"]
    assert d["nb_predictions"] == ["A", "B", "B"]
    winners = [max(row.values()) for row in d["nb_likelihoods"]]
    assert np.allclose(winners, [2 / 15, 1 / 18, 1 / 36])
    assert d["precision_B"] == d["recall_B"] == 1.0
    assert d["confusion"] == [[1, 0], [0, 2]]


if __name__ == "__main__":
    import json
    r = solve()
    for key, value in r.items():
        print(f"--- exercise {key} ---")
        print(json.dumps(value, indent=2, default=float))
    check(r)
    print("\ncheck(): all asserted answers hold")
