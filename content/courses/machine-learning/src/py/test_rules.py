"""Tests for rules.py: 0R, 1R and the covering algorithm."""
import numpy as np
import pytest

from metrics import accuracy
from rules import OneR, Prism, ZeroR, discretize_1r

# The E20b shape [S11]: 13 rows, four nominal attributes, binary target.
NAMES = ["age", "education", "income", "marital"]
X = np.array([
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
Y = np.array(["no", "no", "yes", "yes", "no", "yes", "no", "yes",
              "no", "yes", "yes", "yes", "no"])


def test_zero_r_predicts_the_majority_class():
    m = ZeroR().fit(X, Y)
    assert m.prediction_ == "yes"          # 7 yes vs 6 no
    assert set(m.predict(X)) == {"yes"}


def test_zero_r_regression_predicts_the_mean():
    y = np.array([1.0, 2.0, 6.0])
    m = ZeroR(task="regression").fit(np.zeros((3, 1)), y)
    assert m.prediction_ == pytest.approx(3.0)


def test_one_r_picks_the_attribute_with_the_fewest_errors():
    """E20b reports that 1R splits on age and then scores 1.0 on the held-out rows.

    Source: [S11] `Exam 2020-06-25` ("Interestingly, the 1R had 1.0 accuracy and
    precision (split on age)").  Our table is built to the same shape, so this
    test checks the algorithm, not the paper's data.
    """
    m = OneR().fit(X[:8], Y[:8])
    assert NAMES[m.attribute_] == "age"
    assert m.errors_ == min(r["errors"] for r in m.rule_table_)
    # every attribute is scored, and the error count is consistent with the rules
    for row in m.rule_table_:
        recomputed = sum(int(np.sum(Y[:8][X[:8, row["attribute"]] == v] != c))
                         for v, c in row["rules"].items())
        assert row["errors"] == recomputed
    pred = m.predict(X[8:])
    assert np.mean(pred == Y[8:]) == 1.0


def test_one_r_is_a_decision_stump():
    """1R uses exactly one attribute -- 'a decision tree with only a root node' [S12]."""
    m = OneR().fit(X, Y)
    shuffled = X.copy()
    other = [j for j in range(X.shape[1]) if j != m.attribute_]
    rng = np.random.default_rng(0)
    for j in other:                                  # scramble every other column
        shuffled[:, j] = rng.permutation(shuffled[:, j])
    assert np.array_equal(m.predict(shuffled), m.predict(X))


def test_one_r_falls_back_to_the_majority_class_on_unseen_values():
    m = OneR().fit(X[:8], Y[:8])
    unseen = np.array([["ancient", "high", "low", "single"]], dtype=object)
    assert m.predict(unseen)[0] == m.default_


def test_one_r_beats_or_matches_zero_r_on_training_data():
    zr, one = ZeroR().fit(X, Y), OneR().fit(X, Y)
    assert np.mean(one.predict(X) == Y) >= np.mean(zr.predict(X) == Y)


def test_discretize_1r_finds_a_clean_boundary():
    """Holte's bucketing [S29] on a perfectly separable numeric attribute."""
    x = np.arange(20, dtype=float)
    y = np.where(x < 10, "a", "b")
    thresholds = discretize_1r(x, y, min_bucket=6)
    assert len(thresholds) == 1
    assert 9.0 < thresholds[0] < 10.0


def test_prism_rules_are_pure_and_cover_the_data():
    m = Prism().fit(X, Y)
    assert m.rules_
    for conditions, cls in m.rules_:
        covered = np.ones(len(Y), bool)
        for j, v in conditions:
            covered &= X[:, j] == v
        assert covered.any()
        assert set(Y[covered]) == {cls}          # every rule is pure
    assert np.mean(m.predict(X) == Y) == 1.0     # and together they explain the data


def test_prism_text_output_is_a_rule_set():
    text = Prism().fit(X, Y).to_text(NAMES)
    assert text.startswith("IF ")
    assert text.strip().splitlines()[-1].startswith("ELSE ")


def test_estimators_work_inside_cross_val_score():
    """0R and 1R are two of the standard landmarkers (note 15), so they have to
    behave like any other estimator in the model-selection machinery."""
    from model_selection import cross_val_score
    for model in (ZeroR(), OneR()):
        scores = cross_val_score(model, X, Y, scorer=accuracy, k=3)
        assert len(scores) == 3
        assert np.all((scores >= 0) & (scores <= 1))
