"""Linear models from scratch: OLS (lstsq, normal equations, gradient descent),
ridge (closed form), lasso (coordinate descent with soft thresholding),
logistic regression (gradient descent / Newton), softmax regression,
polynomial features.

Serves note 08 (linear models); the gradient-descent step of E22b is worked in
../exercises/2022-06-30.  Cross-checked in test_linear.py against
sklearn.linear_model (coefficients to 1e-2 or better).  Run `python linear.py`
for the lasso sparsity demo quoted in note 08.
"""
import numpy as np
from model_selection import BaseEstimator


def add_bias(X):
    return np.column_stack([np.ones(len(X)), X])


def polynomial_features(X, degree):
    """All monomials up to `degree` (without bias) for 1-d or multi-d X."""
    from itertools import combinations_with_replacement
    X = np.asarray(X, float)
    cols = [np.prod(X[:, list(c)], axis=1) for d in range(1, degree + 1)
            for c in combinations_with_replacement(range(X.shape[1]), d)]
    return np.column_stack(cols)


class LinearRegression(BaseEstimator):
    """OLS: minimise ||Xw - y||^2.  Normal equations w = (X^T X)^-1 X^T y (via lstsq / pinv)."""

    def __init__(self, solver="lstsq", lr=0.01, n_iter=2000):
        self.solver, self.lr, self.n_iter = solver, lr, n_iter

    def fit(self, X, y):
        A, y = add_bias(np.asarray(X, float)), np.asarray(y, float)
        if self.solver == "lstsq":
            w = np.linalg.lstsq(A, y, rcond=None)[0]
        elif self.solver == "normal":
            w = np.linalg.solve(A.T @ A, A.T @ y)
        else:                                      # batch gradient descent on MSE
            w = np.zeros(A.shape[1])
            for _ in range(self.n_iter):
                w -= self.lr * 2 / len(y) * A.T @ (A @ w - y)
        self.intercept_, self.coef_ = w[0], w[1:]
        return self

    def predict(self, X):
        return np.asarray(X, float) @ self.coef_ + self.intercept_


class Ridge(BaseEstimator):
    """min ||Xw - y||^2 + alpha ||w||^2 (intercept not penalised): w = (X^T X + alpha I)^-1 X^T y."""

    def __init__(self, alpha=1.0):
        self.alpha = alpha

    def fit(self, X, y):
        X, y = np.asarray(X, float), np.asarray(y, float)
        xm, ym = X.mean(0), y.mean()                # centre so the intercept is free
        Xc, yc = X - xm, y - ym
        self.coef_ = np.linalg.solve(Xc.T @ Xc + self.alpha * np.eye(X.shape[1]), Xc.T @ yc)
        self.intercept_ = ym - xm @ self.coef_
        return self

    def predict(self, X):
        return np.asarray(X, float) @ self.coef_ + self.intercept_


def soft_threshold(z, g):
    return np.sign(z) * np.maximum(np.abs(z) - g, 0)


class Lasso(BaseEstimator):
    """min 1/(2n) ||Xw - y||^2 + alpha ||w||_1 via cyclic coordinate descent:
    w_j <- S(x_j^T r_j / n, alpha) / (x_j^T x_j / n), r_j = residual without feature j."""

    def __init__(self, alpha=1.0, n_iter=500, tol=1e-6):
        self.alpha, self.n_iter, self.tol = alpha, n_iter, tol

    def fit(self, X, y):
        X, y = np.asarray(X, float), np.asarray(y, float)
        xm, ym = X.mean(0), y.mean()
        Xc, yc = X - xm, y - ym
        n, d = Xc.shape
        w = np.zeros(d)
        sq = (Xc ** 2).sum(0) / n
        r = yc.copy()                              # residual y - Xw
        for _ in range(self.n_iter):
            w_old = w.copy()
            for j in range(d):
                r += Xc[:, j] * w[j]               # remove feature j's contribution
                w[j] = soft_threshold(Xc[:, j] @ r / n, self.alpha) / sq[j]
                r -= Xc[:, j] * w[j]
            if np.max(np.abs(w - w_old)) < self.tol:
                break
        self.coef_, self.intercept_ = w, ym - xm @ w
        return self

    def predict(self, X):
        return np.asarray(X, float) @ self.coef_ + self.intercept_


def sigmoid(z):
    return 1 / (1 + np.exp(-z))


class LogisticRegression(BaseEstimator):
    """Binary: minimise mean cross-entropy + (l2/2n)||w||^2.
    Gradient: X^T (sigma(Xw) - y)/n ; Newton uses the Hessian X^T diag(p(1-p)) X / n."""

    def __init__(self, l2=0.0, lr=0.1, n_iter=5000, solver="gd", tol=1e-8):
        self.l2, self.lr, self.n_iter, self.solver, self.tol = l2, lr, n_iter, solver, tol

    def fit(self, X, y):
        A, y = add_bias(np.asarray(X, float)), np.asarray(y, float)
        n, d = A.shape
        w = np.zeros(d)
        reg = np.r_[0.0, np.full(d - 1, self.l2)]   # do not penalise the bias
        for _ in range(self.n_iter):
            p = sigmoid(A @ w)
            grad = A.T @ (p - y) / n + reg * w / n
            if self.solver == "newton":
                H = (A * (p * (1 - p))[:, None]).T @ A / n + np.diag(reg) / n
                step = np.linalg.solve(H, grad)
            else:
                step = self.lr * grad
            w -= step
            if np.abs(step).max() < self.tol:
                break
        self.intercept_, self.coef_ = w[0], w[1:]
        return self

    def decision_function(self, X):
        return np.asarray(X, float) @ self.coef_ + self.intercept_

    def predict_proba(self, X):
        p = sigmoid(self.decision_function(X))
        return np.column_stack([1 - p, p])

    def predict(self, X):
        return (self.decision_function(X) > 0).astype(int)


class SoftmaxRegression(BaseEstimator):
    """Multinomial logistic regression: p = softmax(XW), gradient X^T (P - Y)/n."""

    def __init__(self, l2=0.0, lr=0.1, n_iter=3000):
        self.l2, self.lr, self.n_iter = l2, lr, n_iter

    def fit(self, X, y):
        A, y = add_bias(np.asarray(X, float)), np.asarray(y)
        self.classes_, yi = np.unique(y, return_inverse=True)
        Y = np.eye(len(self.classes_))[yi]
        W = np.zeros((A.shape[1], len(self.classes_)))
        for _ in range(self.n_iter):
            Z = A @ W; Z -= Z.max(1, keepdims=True)
            P = np.exp(Z); P /= P.sum(1, keepdims=True)
            G = A.T @ (P - Y) / len(y)
            G[1:] += self.l2 * W[1:] / len(y)
            W -= self.lr * G
        self.W_ = W
        return self

    def predict_proba(self, X):
        Z = add_bias(np.asarray(X, float)) @ self.W_; Z -= Z.max(1, keepdims=True)
        P = np.exp(Z); return P / P.sum(1, keepdims=True)

    def predict(self, X):
        return self.classes_[np.argmax(self.predict_proba(X), 1)]


if __name__ == "__main__":
    from sklearn.datasets import make_regression, make_classification
    from metrics import r2, accuracy

    X, y, coef = make_regression(200, 10, n_informative=3, noise=5.0, coef=True, random_state=0)
    for name, m in [("OLS lstsq", LinearRegression()), ("OLS GD", LinearRegression("gd", 0.05, 3000)),
                    ("ridge a=10", Ridge(10)), ("lasso a=1", Lasso(1.0))]:
        m.fit(X, y)
        print(f"{name:12s} R2 {r2(y, m.predict(X)):.4f}  nonzero coef {np.sum(np.abs(m.coef_) > 1e-6)}  "
              f"||w|| {np.linalg.norm(m.coef_):.2f}")
    print("true nonzero:", np.sum(coef != 0))
    Xc, yc = make_classification(300, 4, n_informative=3, n_redundant=0, random_state=0)
    for solver in ("gd", "newton"):
        lr = LogisticRegression(l2=1.0, solver=solver).fit(Xc, yc)
        print(f"logistic ({solver}) train acc {accuracy(yc, lr.predict(Xc)):.3f}  w={lr.coef_.round(2)}")
    Xm, ym = make_classification(300, 4, n_informative=3, n_redundant=0, n_classes=3, random_state=0)
    print("softmax train acc %.3f" % accuracy(ym, SoftmaxRegression(lr=0.5).fit(Xm, ym).predict(Xm)))
