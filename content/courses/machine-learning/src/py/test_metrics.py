import numpy as np
import pytest
from sklearn import metrics as skm

import metrics as m

rng = np.random.default_rng(1)
y = rng.integers(0, 2, 300)
score = y + rng.normal(0, 0.9, 300)
pred = (score > 0.5).astype(int)
y3 = rng.integers(0, 3, 300)
pred3 = np.where(rng.random(300) < 0.7, y3, rng.integers(0, 3, 300))


def test_confusion_and_accuracy():
    assert np.array_equal(m.confusion_matrix(y3, pred3), skm.confusion_matrix(y3, pred3))
    assert m.accuracy(y3, pred3) == pytest.approx(skm.accuracy_score(y3, pred3))


@pytest.mark.parametrize("avg", ["macro", "micro"])
def test_prf_multiclass(avg):
    p, r, f = m.precision_recall_f1(y3, pred3, avg)
    assert p == pytest.approx(skm.precision_score(y3, pred3, average=avg))
    assert r == pytest.approx(skm.recall_score(y3, pred3, average=avg))
    assert f == pytest.approx(skm.f1_score(y3, pred3, average=avg))


def test_prf_binary():
    p, r, f = m.precision_recall_f1(y, pred)
    assert (p, r, f) == pytest.approx((skm.precision_score(y, pred), skm.recall_score(y, pred), skm.f1_score(y, pred)))


def test_roc_auc():
    fpr, tpr, _ = m.roc_curve(y, score)
    sf, st, _ = skm.roc_curve(y, score, drop_intermediate=False)
    assert np.allclose(fpr, sf) and np.allclose(tpr, st)
    assert m.roc_auc(y, score) == pytest.approx(skm.roc_auc_score(y, score))
    assert m.roc_auc_rank(y, score) == pytest.approx(skm.roc_auc_score(y, score))


def test_average_precision():
    assert m.average_precision(y, score) == pytest.approx(skm.average_precision_score(y, score))


def test_log_loss():
    p = 1 / (1 + np.exp(-score))
    assert m.log_loss(y, p) == pytest.approx(skm.log_loss(y, p))
    P = rng.random((300, 3)); P /= P.sum(1, keepdims=True)
    assert m.log_loss(y3, P) == pytest.approx(skm.log_loss(y3, P))


def test_regression():
    yt = rng.normal(size=100); yp = yt + rng.normal(0, 0.4, 100)
    assert m.mse(yt, yp) == pytest.approx(skm.mean_squared_error(yt, yp))
    assert m.mae(yt, yp) == pytest.approx(skm.mean_absolute_error(yt, yp))
    assert m.r2(yt, yp) == pytest.approx(skm.r2_score(yt, yp))


# ---- the WEKA relative-error family of the course formula sheet [S13, S22] ----
def test_rse_is_one_minus_r2():
    """RSE = sum (p-a)^2 / sum (mean(a)-a)^2, so R^2 = 1 - RSE [S13]."""
    a = rng.normal(size=200)
    p = a + rng.normal(0, 0.5, 200)
    assert m.rse(a, p) == pytest.approx(1 - m.r2(a, p))
    assert m.rrse(a, p) == pytest.approx(np.sqrt(m.rse(a, p)))


def test_relative_errors_are_one_for_the_zero_rule_baseline():
    """The denominator is the error of predicting the mean, so 0R scores exactly 1."""
    a = rng.normal(size=100)
    baseline = np.full_like(a, a.mean())
    assert m.rse(a, baseline) == pytest.approx(1.0)
    assert m.rrse(a, baseline) == pytest.approx(1.0)
    assert m.rae(a, baseline) == pytest.approx(1.0)
    # a perfect model scores 0
    assert m.rse(a, a) == pytest.approx(0.0)
    assert m.rae(a, a) == pytest.approx(0.0)


def test_relative_errors_are_scale_invariant():
    """Unitless by construction: multiplying the target by c must not change them."""
    a = rng.normal(size=120)
    p = a + rng.normal(0, 0.3, 120)
    for c in (2.0, 1000.0):
        assert m.rse(c * a, c * p) == pytest.approx(m.rse(a, p))
        assert m.rae(c * a, c * p) == pytest.approx(m.rae(a, p))


def test_correlation_coefficient_matches_numpy_and_its_range():
    a = rng.normal(size=150)
    p = 2 * a + rng.normal(0, 0.4, 150)
    assert m.correlation_coefficient(a, p) == pytest.approx(np.corrcoef(a, p)[0, 1])
    assert m.correlation_coefficient(a, a) == pytest.approx(1.0)
    assert m.correlation_coefficient(a, -a) == pytest.approx(-1.0)
    assert -1.0 <= m.correlation_coefficient(a, p) <= 1.0      # the E21d true/false item


def test_regression_report_has_the_weka_block():
    a = rng.normal(size=80)
    p = a + rng.normal(0, 0.2, 80)
    rep = m.regression_report(a, p)
    assert set(rep) == {"correlation_coefficient", "mae", "rmse", "rae", "rrse", "r2"}
    assert rep["rrse"] == pytest.approx(np.sqrt(rep["rse"] if "rse" in rep else m.rse(a, p)))


def test_exam_style_mae_of_a_given_regression_function():
    """E25b / E26a: 'given yhat = 3 + 2*F1 + F2 and four instances, compute the MAE'.

    Source: [S11] `Exam 2025-06-25`, `Exam 2026-01-27`.  The paper's own numbers
    are not public; this checks the arithmetic on a table of the same shape.
    """
    F = np.array([[1.0, 2.0], [2.0, 0.0], [0.0, 1.0], [3.0, 1.0]])
    y_true = np.array([8.0, 6.0, 5.0, 9.0])
    y_hat = 3 + 2 * F[:, 0] + F[:, 1]
    assert y_hat.tolist() == [7.0, 7.0, 4.0, 10.0]
    assert m.mae(y_true, y_hat) == pytest.approx((1 + 1 + 1 + 1) / 4)
    assert m.mse(y_true, y_hat) == pytest.approx(1.0)
