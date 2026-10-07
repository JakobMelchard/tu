import numpy as np
from sklearn.svm import SVC
from sklearn.datasets import make_blobs, make_moons
from sklearn.preprocessing import StandardScaler

import svm

Xb, yb = make_blobs(150, centers=2, cluster_std=1.5, random_state=1)
Xb = StandardScaler().fit_transform(Xb)
yb_pm = np.where(yb == 1, 1.0, -1.0)
Xm, ym = make_moons(250, noise=0.2, random_state=0)
Xm = StandardScaler().fit_transform(Xm)


def cos(a, b):
    return a @ b / np.linalg.norm(a) / np.linalg.norm(b)


def primal_objective(w, b, C=1.0):
    return 0.5 * w @ w + C * np.sum(np.maximum(0, 1 - yb_pm * (Xb @ w + b)))


def test_pegasos_matches_linear_svc():
    ours = svm.LinearSVM(C=1.0, n_epochs=200).fit(Xb, yb)
    theirs = SVC(C=1.0, kernel="linear").fit(Xb, yb)
    assert cos(ours.coef_, theirs.coef_[0]) > 0.98
    assert primal_objective(ours.coef_, ours.intercept_) < 1.02 * primal_objective(theirs.coef_[0], theirs.intercept_[0])
    assert np.mean(ours.predict(Xb) == theirs.predict(Xb)) > 0.97


def test_smo_linear_kernel_matches_svc():
    ours = svm.SVM(C=1.0, kernel="linear", tol=1e-4).fit(Xb, yb)
    theirs = SVC(C=1.0, kernel="linear").fit(Xb, yb)
    assert cos(ours.coef_, theirs.coef_[0]) > 0.98
    assert primal_objective(ours.coef_, ours.intercept_) < 1.02 * primal_objective(theirs.coef_[0], theirs.intercept_[0])
    assert abs(len(ours.support_) - len(theirs.support_)) <= 5
    assert np.mean(ours.predict(Xb) == theirs.predict(Xb)) > 0.97


def test_smo_rbf_matches_svc():
    ours = svm.SVM(C=1.0, kernel="rbf", gamma=1.0).fit(Xm, ym)
    theirs = SVC(C=1.0, kernel="rbf", gamma=1.0).fit(Xm, ym)
    assert np.mean(ours.predict(Xm) == theirs.predict(Xm)) > 0.95
    assert np.corrcoef(ours.decision_function(Xm), theirs.decision_function(Xm))[0, 1] > 0.95


def test_kernels_match_sklearn():
    from sklearn.metrics.pairwise import rbf_kernel, polynomial_kernel
    assert np.allclose(svm.kernel("rbf", 0.7)(Xb[:10], Xb[:5]), rbf_kernel(Xb[:10], Xb[:5], gamma=0.7))
    assert np.allclose(svm.kernel("poly", 0.5, 2, 1.0)(Xb[:10], Xb[:5]), polynomial_kernel(Xb[:10], Xb[:5], degree=2, gamma=0.5, coef0=1.0))
