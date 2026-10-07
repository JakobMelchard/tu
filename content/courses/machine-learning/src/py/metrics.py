"""Evaluation metrics from scratch (numpy only).

Classification: confusion matrix, accuracy, precision/recall/F1 (binary, macro,
micro), ROC curve + AUC (trapezoid and Mann-Whitney rank form), precision-recall
curve + average precision, log loss.  Regression: MSE, RMSE, MAE, R^2, and the
WEKA family the course formula sheet prints: RAE, RSE, RRSE, correlation
coefficient [S13, S22].

Serves note 03 (evaluation).  Cross-checked in test_metrics.py against
sklearn.metrics (exact) and the identities RSE = 1 - R^2, RAE = RSE = RRSE = 1
for the mean-predicting 0R baseline.  Run `python metrics.py` for the demo,
including the E26a-style MAE question.
"""
import numpy as np


# ---------------------------------------------------------------- classification
def confusion_matrix(y_true, y_pred, labels=None):
    """C[i, j] = number of samples with true label i predicted as label j."""
    y_true, y_pred = np.asarray(y_true), np.asarray(y_pred)
    if labels is None:
        labels = np.unique(np.concatenate([y_true, y_pred]))
    idx = {lab: i for i, lab in enumerate(labels)}
    C = np.zeros((len(labels), len(labels)), dtype=int)
    for t, p in zip(y_true, y_pred):
        C[idx[t], idx[p]] += 1
    return C


def accuracy(y_true, y_pred):
    return float(np.mean(np.asarray(y_true) == np.asarray(y_pred)))


def precision_recall_f1(y_true, y_pred, average="binary", pos_label=1):
    """Return (precision, recall, f1).

    binary: P = TP/(TP+FP), R = TP/(TP+FN), F1 = 2PR/(P+R) for pos_label.
    macro : unweighted mean of per-class scores.
    micro : pool TP/FP/FN over classes (equals accuracy for single-label).
    """
    y_true, y_pred = np.asarray(y_true), np.asarray(y_pred)
    labels = [pos_label] if average == "binary" else np.unique(np.concatenate([y_true, y_pred]))
    tp = np.array([np.sum((y_true == c) & (y_pred == c)) for c in labels], float)
    fp = np.array([np.sum((y_true != c) & (y_pred == c)) for c in labels], float)
    fn = np.array([np.sum((y_true == c) & (y_pred != c)) for c in labels], float)
    if average == "micro":
        tp, fp, fn = tp.sum(keepdims=True), fp.sum(keepdims=True), fn.sum(keepdims=True)
    with np.errstate(divide="ignore", invalid="ignore"):
        p = np.where(tp + fp > 0, tp / (tp + fp), 0.0)
        r = np.where(tp + fn > 0, tp / (tp + fn), 0.0)
        f = np.where(p + r > 0, 2 * p * r / (p + r), 0.0)
    return float(p.mean()), float(r.mean()), float(f.mean())


def roc_curve(y_true, score, pos_label=1):
    """FPR, TPR, thresholds; one point per distinct score, sorted by decreasing score."""
    y_true, score = np.asarray(y_true) == pos_label, np.asarray(score, float)
    order = np.argsort(-score, kind="stable")
    y, s = y_true[order], score[order]
    # indices where the score changes -> candidate thresholds
    distinct = np.where(np.diff(s) != 0)[0]
    cut = np.r_[distinct, len(y) - 1]
    tps = np.cumsum(y)[cut]
    fps = (1 + cut) - tps
    P, N = y.sum(), len(y) - y.sum()
    tpr = np.r_[0.0, tps / P] if P else np.r_[0.0, np.zeros(len(cut))]
    fpr = np.r_[0.0, fps / N] if N else np.r_[0.0, np.zeros(len(cut))]
    return fpr, tpr, np.r_[np.inf, s[cut]]


def auc(x, y):
    """Trapezoidal area under a curve given monotone x."""
    x, y = np.asarray(x, float), np.asarray(y, float)
    return float(np.sum(np.diff(x) * (y[1:] + y[:-1]) / 2))


def roc_auc(y_true, score, pos_label=1):
    fpr, tpr, _ = roc_curve(y_true, score, pos_label)
    return auc(fpr, tpr)


def roc_auc_rank(y_true, score, pos_label=1):
    """AUC as P(score(pos) > score(neg)) via the Mann-Whitney U statistic."""
    y, s = np.asarray(y_true) == pos_label, np.asarray(score, float)
    pos, neg = s[y], s[~y]
    wins = (pos[:, None] > neg[None, :]).sum() + 0.5 * (pos[:, None] == neg[None, :]).sum()
    return float(wins / (len(pos) * len(neg)))


def precision_recall_curve(y_true, score, pos_label=1):
    """Precision and recall at each distinct threshold (decreasing score), ending at (P=1, R=0)."""
    y_true, score = np.asarray(y_true) == pos_label, np.asarray(score, float)
    order = np.argsort(-score, kind="stable")
    y, s = y_true[order], score[order]
    cut = np.r_[np.where(np.diff(s) != 0)[0], len(y) - 1]
    tps = np.cumsum(y)[cut]
    prec = tps / (cut + 1)          # increasing threshold index -> increasing recall
    rec = tps / y.sum()
    # sklearn convention: recall decreasing, thresholds increasing, final point (P=1, R=0)
    return np.r_[prec[::-1], 1.0], np.r_[rec[::-1], 0.0], s[cut][::-1]


def average_precision(y_true, score, pos_label=1):
    """AP = sum_k (R_k - R_{k-1}) P_k, the step-wise area under the PR curve."""
    p, r, _ = precision_recall_curve(y_true, score, pos_label)
    return float(np.sum(-np.diff(r) * p[:-1]))


def log_loss(y_true, proba, eps=1e-15):
    """Cross-entropy for binary (proba 1-d) or multiclass (proba n x k, y_true integer labels)."""
    y_true, proba = np.asarray(y_true), np.clip(np.asarray(proba, float), eps, 1 - eps)
    if proba.ndim == 1:
        return float(-np.mean(y_true * np.log(proba) + (1 - y_true) * np.log(1 - proba)))
    proba = proba / proba.sum(axis=1, keepdims=True)
    return float(-np.mean(np.log(proba[np.arange(len(y_true)), y_true])))


# --------------------------------------------------------------------- regression
def mse(y_true, y_pred):
    return float(np.mean((np.asarray(y_true) - np.asarray(y_pred)) ** 2))


def rmse(y_true, y_pred):
    return float(np.sqrt(mse(y_true, y_pred)))


def mae(y_true, y_pred):
    return float(np.mean(np.abs(np.asarray(y_true) - np.asarray(y_pred))))


def r2(y_true, y_pred):
    """R^2 = 1 - SS_res / SS_tot; can be negative for models worse than the mean."""
    y_true, y_pred = np.asarray(y_true, float), np.asarray(y_pred, float)
    ss_res = np.sum((y_true - y_pred) ** 2)
    ss_tot = np.sum((y_true - y_true.mean()) ** 2)
    return float(1 - ss_res / ss_tot)


# The relative error family the course's formula sheet prints ([S13]); these are
# WEKA's output block ([S22]) rather than sklearn's, and a "name three methods to
# compute the error in regression" question is drawn from them.  Each divides by
# the error of the 0R baseline (predict the mean), so 1.0 = no better than 0R.
def rse(y_true, y_pred):
    """Relative squared error: sum (p-a)^2 / sum (mean(a)-a)^2.  Equals 1 - R^2."""
    y_true, y_pred = np.asarray(y_true, float), np.asarray(y_pred, float)
    return float(np.sum((y_pred - y_true) ** 2) / np.sum((y_true.mean() - y_true) ** 2))


def rrse(y_true, y_pred):
    """Root relative squared error = sqrt(RSE)."""
    return float(np.sqrt(rse(y_true, y_pred)))


def rae(y_true, y_pred):
    """Relative absolute error: sum |p-a| / sum |mean(a)-a|."""
    y_true, y_pred = np.asarray(y_true, float), np.asarray(y_pred, float)
    return float(np.sum(np.abs(y_pred - y_true)) / np.sum(np.abs(y_true.mean() - y_true)))


def correlation_coefficient(y_true, y_pred):
    """Pearson r between predictions and actuals, in [-1, 1] ([S13])."""
    a, p = np.asarray(y_true, float), np.asarray(y_pred, float)
    da, dp = a - a.mean(), p - p.mean()
    denom = np.sqrt(np.sum(da ** 2) * np.sum(dp ** 2))
    return float(np.sum(da * dp) / denom) if denom else 0.0


def regression_report(y_true, y_pred):
    """The block WEKA prints for a regression model ([S13], [S22])."""
    return dict(
        correlation_coefficient=correlation_coefficient(y_true, y_pred),
        mae=mae(y_true, y_pred),
        rmse=rmse(y_true, y_pred),
        rae=rae(y_true, y_pred),
        rrse=rrse(y_true, y_pred),
        r2=r2(y_true, y_pred),
    )


def classification_report(y_true, y_pred):
    """Per-class precision/recall/F1/support as a dict, plus macro and accuracy."""
    labels = np.unique(np.concatenate([np.asarray(y_true), np.asarray(y_pred)]))
    rep = {}
    for c in labels:
        p, r, f = precision_recall_f1(y_true, y_pred, "binary", pos_label=c)
        rep[c] = dict(precision=p, recall=r, f1=f, support=int(np.sum(np.asarray(y_true) == c)))
    rep["macro"] = dict(zip(("precision", "recall", "f1"), precision_recall_f1(y_true, y_pred, "macro")))
    rep["accuracy"] = accuracy(y_true, y_pred)
    return rep


if __name__ == "__main__":
    rng = np.random.default_rng(0)
    y = rng.integers(0, 2, 200)
    score = y + rng.normal(0, 0.8, 200)          # noisy score correlated with label
    pred = (score > 0.5).astype(int)
    print("confusion matrix\n", confusion_matrix(y, pred))
    print("accuracy %.3f  P/R/F1 %s" % (accuracy(y, pred), np.round(precision_recall_f1(y, pred), 3)))
    print("ROC AUC (trapezoid) %.4f  (rank) %.4f" % (roc_auc(y, score), roc_auc_rank(y, score)))
    print("average precision %.4f" % average_precision(y, score))
    yr = rng.normal(size=100); yp = yr + rng.normal(0, 0.3, 100)
    print("regression: MSE %.3f MAE %.3f R2 %.3f" % (mse(yr, yp), mae(yr, yp), r2(yr, yp)))
    print("WEKA block:", {k: round(v, 4) for k, v in regression_report(yr, yp).items()})
    # The exam's own MAE question (E25b/E26a): yhat = 3 + 2*f1 + f2 on four rows, the
    # same table as ../exercises/2026-01-27 (residuals 2, -1, 1, -2).
    F = np.array([[1.0, 2.0], [2.0, 0.0], [0.0, 1.0], [3.0, 1.0]])
    y_ex = np.array([9.0, 6.0, 5.0, 8.0])
    pred_ex = 3 + 2 * F[:, 0] + F[:, 1]
    print("E26a-style MAE %.2f, MSE %.2f (the distractor)  predictions %s"
          % (mae(y_ex, pred_ex), mse(y_ex, pred_ex), pred_ex))
