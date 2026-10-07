"""Support vector machines from scratch [S35].
LinearSVM: primal, stochastic sub-gradient descent on the hinge loss (Pegasos).
SVM:       dual, SMO (Platt 1998, second-choice heuristic) with linear,
           polynomial and RBF kernels.

Serves note 10 (SVM).  Cross-checked in test_svm.py against sklearn.svm.SVC
(primal objective within 2 %, RBF predictions agree on >= 95 % of points).
Run `python svm.py` for the C / gamma table quoted in note 10.
"""
import numpy as np
from model_selection import BaseEstimator


def kernel(name, gamma=1.0, degree=3, coef0=1.0):
    if name == "linear":
        return lambda A, B: A @ B.T
    if name == "poly":
        return lambda A, B: (gamma * A @ B.T + coef0) ** degree
    if name == "rbf":
        def k(A, B):
            sq = (A ** 2).sum(1)[:, None] + (B ** 2).sum(1)[None, :] - 2 * A @ B.T
            return np.exp(-gamma * np.maximum(sq, 0))
        return k
    raise ValueError(name)


class LinearSVM(BaseEstimator):
    """min_w,b  lambda/2 ||w||^2 + 1/n sum max(0, 1 - y_i (w.x_i + b)),  lambda = 1/(C n).
    Pegasos: at step t pick i, eta = 1/(lambda t), w <- (1 - eta lambda) w + eta y_i x_i [margin < 1]."""

    def __init__(self, C=1.0, n_epochs=50, rng=0):
        self.C, self.n_epochs, self.rng = C, n_epochs, rng

    def fit(self, X, y):
        X = np.asarray(X, float)
        self.classes_ = np.unique(y)
        y = np.where(np.asarray(y) == self.classes_[1], 1.0, -1.0)
        n, d = X.shape
        lam = 1.0 / (self.C * n)
        w, b, t = np.zeros(d), 0.0, 0
        r = np.random.default_rng(self.rng)
        for _ in range(self.n_epochs):
            for i in r.permutation(n):
                t += 1
                eta = 1.0 / (lam * t)
                if y[i] * (X[i] @ w + b) < 1:
                    w = (1 - eta * lam) * w + eta * y[i] * X[i]
                    b += eta * y[i]
                else:
                    w = (1 - eta * lam) * w
        self.coef_, self.intercept_ = w, b
        return self

    def decision_function(self, X):
        return np.asarray(X, float) @ self.coef_ + self.intercept_

    def predict(self, X):
        return np.where(self.decision_function(X) >= 0, self.classes_[1], self.classes_[0])

    def hinge_loss(self, X, y):
        y = np.where(np.asarray(y) == self.classes_[1], 1.0, -1.0)
        return float(np.mean(np.maximum(0, 1 - y * self.decision_function(X))))


class SVM(BaseEstimator):
    """Dual: max sum a_i - 1/2 sum a_i a_j y_i y_j K(x_i,x_j)  s.t. 0 <= a_i <= C, sum a_i y_i = 0.
    SMO: for each KKT-violating i try partners j in order of |E_i - E_j| (Platt's second choice) until one
    pair moves, optimise it analytically; stop after a sweep in which no pair moves (or max_passes sweeps).
    A random j (CS229 simplified SMO) mostly hits non-SVs that clip to 0 and can stop with KKT violated."""

    def __init__(self, C=1.0, kernel="rbf", gamma=1.0, degree=3, tol=1e-3, max_passes=1000):
        self.C, self.kernel, self.gamma, self.degree = C, kernel, gamma, degree
        self.tol, self.max_passes = tol, max_passes

    def fit(self, X, y):
        X = np.asarray(X, float)
        self.classes_ = np.unique(y)
        y = np.where(np.asarray(y) == self.classes_[1], 1.0, -1.0)
        n = len(y)
        K = kernel(self.kernel, self.gamma, self.degree)(X, X)
        a, b = np.zeros(n), 0.0
        sweeps = 0
        while sweeps < self.max_passes:
            sweeps += 1
            changed = 0
            for i in range(n):
                f = (a * y) @ K + b                          # current decision values
                E = f - y
                if not ((y[i] * E[i] < -self.tol and a[i] < self.C) or (y[i] * E[i] > self.tol and a[i] > 0)):
                    continue
                # Platt's second choice: largest |E_i - E_j| first, then the rest until one pair moves
                for j in np.argsort(-np.abs(E[i] - E)):
                    if j == i:
                        continue
                    ai_old, aj_old = a[i], a[j]
                    if y[i] != y[j]:
                        L, H = max(0, a[j] - a[i]), min(self.C, self.C + a[j] - a[i])
                    else:
                        L, H = max(0, a[i] + a[j] - self.C), min(self.C, a[i] + a[j])
                    eta = 2 * K[i, j] - K[i, i] - K[j, j]
                    if L == H or eta >= 0:
                        continue
                    a[j] = np.clip(aj_old - y[j] * (E[i] - E[j]) / eta, L, H)
                    if abs(a[j] - aj_old) < 1e-5:
                        a[j] = aj_old
                        continue
                    a[i] = ai_old + y[i] * y[j] * (aj_old - a[j])
                    b1 = b - E[i] - y[i] * (a[i] - ai_old) * K[i, i] - y[j] * (a[j] - aj_old) * K[i, j]
                    b2 = b - E[j] - y[i] * (a[i] - ai_old) * K[i, j] - y[j] * (a[j] - aj_old) * K[j, j]
                    b = b1 if 0 < a[i] < self.C else b2 if 0 < a[j] < self.C else (b1 + b2) / 2
                    changed += 1
                    break
            if changed == 0:                                 # no pair can move: KKT holds within tol
                break
        self.n_sweeps_ = sweeps
        sv = a > 1e-8
        self.support_, self.alpha_, self.sv_y_, self.sv_X_, self.intercept_ = np.where(sv)[0], a[sv], y[sv], X[sv], b
        return self

    def decision_function(self, X):
        Kx = kernel(self.kernel, self.gamma, self.degree)(np.asarray(X, float), self.sv_X_)
        return Kx @ (self.alpha_ * self.sv_y_) + self.intercept_

    def predict(self, X):
        return np.where(self.decision_function(X) >= 0, self.classes_[1], self.classes_[0])

    @property
    def coef_(self):
        """Primal w = sum_i a_i y_i x_i (linear kernel only)."""
        return (self.alpha_ * self.sv_y_) @ self.sv_X_


if __name__ == "__main__":
    from sklearn.datasets import make_blobs, make_moons
    from preprocessing import StandardScaler
    from model_selection import train_test_split
    from metrics import accuracy

    X, y = make_blobs(200, centers=2, cluster_std=1.5, random_state=0)
    lin = LinearSVM(C=1.0).fit(X, y)
    print("linear SVM (Pegasos): acc %.3f, hinge %.3f, w=%s" % (accuracy(y, lin.predict(X)), lin.hinge_loss(X, y), lin.coef_.round(2)))
    dual = SVM(C=1.0, kernel="linear").fit(X, y)
    print("linear SVM (SMO dual): acc %.3f, %d support vectors, w=%s" % (accuracy(y, dual.predict(X)), len(dual.support_), dual.coef_.round(2)))
    X, y = make_moons(300, noise=0.2, random_state=0)
    X = StandardScaler().fit_transform(X)
    Xtr, Xte, ytr, yte = train_test_split(X, y, 0.3, stratify=True, rng=0)
    for C, gamma in [(0.1, 0.5), (1, 1), (10, 5), (100, 50)]:
        m = SVM(C, "rbf", gamma).fit(Xtr, ytr)
        print(f"RBF C={C:5g} gamma={gamma:4g}: train {accuracy(ytr, m.predict(Xtr)):.3f} test {accuracy(yte, m.predict(Xte)):.3f} SVs {len(m.support_)}")
