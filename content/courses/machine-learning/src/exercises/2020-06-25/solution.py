"""Worked solution: exam of 25.06.2020 (label E20b, 2020S).

Source of the questions: [S11] VoWi `Exam 2020-06-25`.  Described in our own
words in README.md; the paper itself is not reproduced.  90 minutes, twelve
true/false items at +2 / -1 / 0, then six worked exercises.

Questions answered (numbers asserted in `check()`):
  Ex. 17 LOOCV error of 1-NN and 3-NN on ten points with one intruder per
         class: 1-NN 2/10 = 0.2, 3-NN 1/10 = 0.1; the resubstitution error of
         1-NN is 0 (E22a's true/false item).
  Ex. 18 1R trained on rows 1-8: errors age 1, education 2, income 1,
         marital 2; age wins the tie with income (first attribute) as the
         transcript records; rules young -> no, middle / old -> yes; on rows
         9-13 accuracy = precision(yes) = 1.0, against 0R's 0.4.
  Ex. 13 AdaBoost weights: 1/3 initially, eps = 1/3, alpha = 1/2 ln 2,
         then (1/2, 1/4, 1/4).
  T/F    six recalled items, answered as [S12] marks them.

Run:  ../../../../../.venv/bin/python solution.py
"""
import os
import sys

import numpy as np

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "py")))

from knn import KNNClassifier                                    # noqa: E402
from metrics import accuracy, precision_recall_f1                # noqa: E402
from rules import OneR, ZeroR                                     # noqa: E402


# --- Exercise 17: LOOCV error of 1-NN and 3-NN on ten 2-D points ---------------
# The paper sketches a 10-point layout with two well-separated groups and one
# point of each class placed among the other class.  This is that layout.
POINTS = np.array([
    [0.0, 2.0], [1.0, 2.0], [0.0, 0.0], [1.0, 0.0],                 # class +, left group
    [1.1, 2.0],                                                      # class -, intruder
    [4.0, 2.0], [5.0, 2.0], [4.0, 0.0], [5.0, 0.0], [4.5, 1.0],     # class -, right group
])
LABELS = np.array([1, 1, 1, 1, 0, 0, 0, 0, 0, 0])


def exercise_17_loocv():
    """Average error rate under leave-one-out CV, which for n = 10 is 10-fold CV.

    The point of the question is that 1-NN is *not* error-free here: each point
    is predicted from the other nine, so its own label cannot be used.
    """
    out = {}
    for k in (1, 3):
        errors = 0
        per_point = []
        for i in range(len(LABELS)):
            train = np.delete(np.arange(len(LABELS)), i)
            pred = KNNClassifier(k=k).fit(POINTS[train], LABELS[train]).predict(POINTS[[i]])[0]
            per_point.append(int(pred))
            errors += int(pred != LABELS[i])
        out[f"{k}nn"] = dict(error_rate=errors / len(LABELS),
                             accuracy=1 - errors / len(LABELS),
                             predictions=per_point)
    # For contrast: the resubstitution error of 1-NN really is 0 (E22a's
    # true/false item "the error of a 1-NN classifier on the training set is 0").
    resub = KNNClassifier(k=1).fit(POINTS, LABELS).predict(POINTS)
    out["1nn_training_error"] = float(np.mean(resub != LABELS))
    return out


# --- Exercise 18: 1R on rows 1-8, then precision and accuracy on rows 9-13 ------
# 13 rows, four nominal attributes (age, education, income, marital status),
# target "purchase" yes/no.  The transcript records that 1R split on *age* and
# then scored 1.0 accuracy and precision; our table is built to that shape.
TABLE = np.array([
    ["young",  "high",   "low",    "single"],
    ["young",  "low",    "low",    "single"],
    ["middle", "high",   "high",   "married"],
    ["old",    "medium", "high",   "married"],
    ["old",    "low",    "medium", "single"],
    ["middle", "medium", "medium", "married"],
    ["young",  "medium", "low",    "married"],
    ["old",    "high",   "high",   "single"],
    ["young",  "high",   "medium", "married"],
    ["middle", "low",    "low",    "single"],
    ["old",    "medium", "low",    "married"],
    ["middle", "high",   "medium", "single"],
    ["young",  "low",    "high",   "single"],
], dtype=object)
PURCHASE = np.array(["no", "no", "yes", "yes", "no", "yes", "no", "yes",
                     "no", "yes", "yes", "yes", "no"])
ATTRS = ["age", "education", "income", "marital"]


def exercise_18_one_rule():
    """Train 1R on the first eight rows, evaluate on rows 9-13."""
    Xtr, ytr, Xte, yte = TABLE[:8], PURCHASE[:8], TABLE[8:], PURCHASE[8:]
    model = OneR().fit(Xtr, ytr)
    pred = model.predict(Xte)
    p, r, f = precision_recall_f1(yte, pred, average="binary", pos_label="yes")
    baseline = ZeroR().fit(Xtr, ytr)
    return dict(
        chosen_attribute=ATTRS[model.attribute_],
        training_errors=model.errors_,
        error_table={ATTRS[row["attribute"]]: row["errors"] for row in model.rule_table_},
        rules={str(k): str(v) for k, v in model.rules_.items()},
        predictions=[str(v) for v in pred],
        accuracy=accuracy(yte, pred),
        precision_yes=p,
        recall_yes=r,
        f1_yes=f,
        zero_r_accuracy=accuracy(yte, baseline.predict(Xte)),
    )


# --- Exercise 13: AdaBoost weights on three points -----------------------------
def exercise_13_boosting():
    """Identical to E19b exercise 5: weights start at 1/n; after one stump the
    misclassified point carries half the mass."""
    x, y = np.array([1.0, 3.0, 5.0]), np.array([-1.0, 1.0, -1.0])
    w = np.full(3, 1 / 3)
    pred = np.where(x <= 4.0, 1.0, -1.0)            # best stump: two of three right
    eps = float(np.sum(w[pred != y]))
    alpha = 0.5 * np.log((1 - eps) / eps)
    w2 = w * np.exp(-alpha * y * pred)
    w2 /= w2.sum()
    return dict(initial_weight=1 / 3, epsilon=eps, alpha=float(alpha),
                weights=w2.tolist(), heaviest=int(np.argmax(w2)))


# --- Exercise 15/16: short recall answers --------------------------------------
def exercises_15_16_short_answers():
    """"Name three hyperparameter-optimisation methods" and "name two ways to
    compute the coefficients of a linear regression" [S12]."""
    return dict(
        hyperparameter_optimisation=["grid search", "random search", "Bayesian optimisation"],
        linear_regression_coefficients=["normal equations (closed form)", "gradient descent"],
    )


# --- The twelve true/false items the transcript recalls ------------------------
def true_false_block():
    """Answers as the course marks them [S12]; see notes/00-exam-focus.md."""
    return {
        "MAE is less sensitive to outliers than MSE": True,
        "Freezing layers means they will be fine-tuned in the fine-tuning phase": False,
        "Overfitting is more likely on a smaller test set": True,   # as [S12] marks it
        "Boosting is easily parallelisable": False,
        "Paired t-tests are used for folds verification in the holdout method": False,
        "Random forests use bootstrapping": True,
    }


def solve():
    return {
        "tf": true_false_block(),
        "13": exercise_13_boosting(),
        "15_16": exercises_15_16_short_answers(),
        "17": exercise_17_loocv(),
        "18": exercise_18_one_rule(),
    }


def check(r):
    """Assert the numeric answers listed in the module docstring."""
    a = r["17"]
    assert a["1nn"]["error_rate"] == 0.2 and a["3nn"]["error_rate"] == 0.1
    assert a["1nn_training_error"] == 0.0

    b = r["18"]
    assert b["error_table"] == {"age": 1, "education": 2, "income": 1, "marital": 2}
    assert b["chosen_attribute"] == "age" and b["training_errors"] == 1
    assert b["rules"] == {"middle": "yes", "old": "yes", "young": "no"}
    assert b["accuracy"] == b["precision_yes"] == b["recall_yes"] == 1.0
    assert b["zero_r_accuracy"] == 0.4

    c = r["13"]
    assert np.isclose(c["initial_weight"], 1 / 3) and np.isclose(c["epsilon"], 1 / 3)
    assert np.isclose(c["alpha"], 0.5 * np.log(2))
    assert np.allclose(c["weights"], [0.5, 0.25, 0.25]) and c["heaviest"] == 0


if __name__ == "__main__":
    import json
    r = solve()
    for key, value in r.items():
        print(f"--- exercise {key} ---")
        print(json.dumps(value, indent=2, default=float))
    check(r)
    print("\ncheck(): all asserted answers hold")
