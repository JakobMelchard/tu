"""Naive Bayes: Gaussian, multinomial, Bernoulli, and the categorical variant in
the convention the course examines.

[S10] reports that "there's always one [naive Bayes calculation] in each exam",
and the archive agrees: E17a, E18a, E19b, E20c, E21b, E25b and E26a all ask for
one [S11].  `CategoricalNB` follows the arithmetic of the course's own how-to
sheet [S14] so that its numbers match a marking scheme; see note 09.

Bayesian networks -- structure, CPTs, d-separation, inference by enumeration and
structure search -- are in `bayesnet.py`.
"""
import numpy as np
from model_selection import BaseEstimator


# ---------------------------------------------------------------- naive Bayes
class GaussianNB(BaseEstimator):
    """p(x|c) = prod_j N(x_j; mu_cj, sigma_cj^2); predict argmax_c log p(c) + sum_j log N."""

    def __init__(self, var_smoothing=1e-9):
        self.var_smoothing = var_smoothing

    def fit(self, X, y):
        X, y = np.asarray(X, float), np.asarray(y)
        self.classes_ = np.unique(y)
        self.theta_ = np.array([X[y == c].mean(0) for c in self.classes_])
        self.var_ = np.array([X[y == c].var(0) for c in self.classes_]) + self.var_smoothing * X.var(0).max()
        self.prior_ = np.array([np.mean(y == c) for c in self.classes_])
        return self

    def log_likelihood(self, X):
        X = np.asarray(X, float)[:, None, :]                       # n x 1 x d
        ll = -0.5 * np.log(2 * np.pi * self.var_) - (X - self.theta_) ** 2 / (2 * self.var_)
        return ll.sum(2) + np.log(self.prior_)                     # n x K

    def predict_proba(self, X):
        L = self.log_likelihood(X); L -= L.max(1, keepdims=True)
        P = np.exp(L); return P / P.sum(1, keepdims=True)

    def predict(self, X):
        return self.classes_[np.argmax(self.log_likelihood(X), 1)]


class MultinomialNB(BaseEstimator):
    """Counts: p(w_j|c) = (N_cj + alpha) / (N_c + alpha d); log p(x|c) = sum_j x_j log p(w_j|c)."""

    def __init__(self, alpha=1.0):
        self.alpha = alpha

    def fit(self, X, y):
        X, y = np.asarray(X, float), np.asarray(y)
        self.classes_ = np.unique(y)
        counts = np.array([X[y == c].sum(0) for c in self.classes_]) + self.alpha
        self.feature_log_prob_ = np.log(counts / counts.sum(1, keepdims=True))
        self.class_log_prior_ = np.log([np.mean(y == c) for c in self.classes_])
        return self

    def predict(self, X):
        return self.classes_[np.argmax(np.asarray(X, float) @ self.feature_log_prob_.T + self.class_log_prior_, 1)]


class BernoulliNB(BaseEstimator):
    """Binary features: p(x|c) = prod_j p_cj^x_j (1-p_cj)^(1-x_j)."""

    def __init__(self, alpha=1.0):
        self.alpha = alpha

    def fit(self, X, y):
        X, y = (np.asarray(X, float) > 0).astype(float), np.asarray(y)
        self.classes_ = np.unique(y)
        self.p_ = np.array([(X[y == c].sum(0) + self.alpha) / (np.sum(y == c) + 2 * self.alpha) for c in self.classes_])
        self.class_log_prior_ = np.log([np.mean(y == c) for c in self.classes_])
        return self

    def predict(self, X):
        X = (np.asarray(X, float) > 0).astype(float)
        ll = X @ np.log(self.p_).T + (1 - X) @ np.log(1 - self.p_).T + self.class_log_prior_
        return self.classes_[np.argmax(ll, 1)]


class CategoricalNB(BaseEstimator):
    """Naive Bayes on nominal attributes, in the convention the course examines.

    [S14] ("How to Predict a Class with Naive Bayes") works the calculation as

        Likelihood(C | E) = P(C) * prod_j P(F_j = v_j | C)
        P(C | E)          = Likelihood(C | E) / sum over classes

    and its Laplace correction adds 1 to the numerator **and 1 to the
    denominator** -- not |values(F_j)| as a textbook Dirichlet prior would --
    while leaving the class prior unsmoothed:

        P(F_j = v | C) = (#{F_j = v, C} + 1) / (#{C} + 1)

    That convention is not a proper posterior (the smoothed probabilities of one
    attribute no longer sum to 1) but it is what the marking scheme uses, so
    `course_laplace=True` reproduces exam answers exactly; `course_laplace=False`
    turns smoothing off and `textbook=True` gives the standard add-alpha rule.
    Missing values (np.nan or None) are skipped in the training counts and
    omitted from the product at prediction time, as [S12] describes.
    """

    def __init__(self, course_laplace=True, alpha=1.0, textbook=False):
        self.course_laplace = course_laplace
        self.alpha = alpha
        self.textbook = textbook

    @staticmethod
    def _missing(v):
        return v is None or (isinstance(v, float) and np.isnan(v))

    def fit(self, X, y):
        X, y = np.asarray(X, dtype=object), np.asarray(y)
        self.classes_ = np.unique(y)
        self.n_features_ = X.shape[1]
        self.values_ = [sorted({v for v in X[:, j] if not self._missing(v)}, key=str)
                        for j in range(self.n_features_)]
        self.class_count_ = {c: int(np.sum(y == c)) for c in self.classes_}
        self.prior_ = {c: self.class_count_[c] / len(y) for c in self.classes_}
        self.counts_ = {}
        for c in self.classes_:
            rows = X[y == c]
            for j in range(self.n_features_):
                for v in self.values_[j]:
                    self.counts_[(c, j, v)] = int(np.sum(rows[:, j] == v))
        return self

    def conditional(self, c, j, v):
        """P(F_j = v | C = c) under the configured smoothing rule."""
        n_c = self.class_count_[c]
        n_cv = self.counts_.get((c, j, v), 0)
        if self.textbook:
            return (n_cv + self.alpha) / (n_c + self.alpha * len(self.values_[j]))
        if self.course_laplace:
            return (n_cv + 1) / (n_c + 1)          # [S14]
        return n_cv / n_c if n_c else 0.0

    def likelihoods(self, row):
        """Un-normalised P(C) * prod_j P(F_j | C) per class -- the numbers an
        exam answer has to show."""
        row = np.asarray(row, dtype=object)
        out = {}
        for c in self.classes_:
            p = self.prior_[c]
            for j in range(self.n_features_):
                if self._missing(row[j]):
                    continue
                p *= self.conditional(c, j, row[j])
            out[c] = p
        return out

    def predict_proba(self, X):
        X = np.asarray(X, dtype=object)
        rows = []
        for row in X:
            lik = self.likelihoods(row)
            total = sum(lik.values())
            rows.append([lik[c] / total if total else 1 / len(self.classes_) for c in self.classes_])
        return np.array(rows)

    def predict(self, X):
        return self.classes_[np.argmax(self.predict_proba(X), axis=1)]


if __name__ == "__main__":
    from sklearn.datasets import make_classification
    X, y = make_classification(300, 6, n_informative=4, random_state=0)
    print("GaussianNB train acc %.3f" % np.mean(GaussianNB().fit(X, y).predict(X) == y))

    # [S14]'s worked example, the convention the exam marks against.
    Xc = np.array([[True, "Small", False],
                   [False, "Medium", False],
                   [True, "Small", True],
                   [True, "Large", False]], dtype=object)
    yc = np.array(["A", "B", "B", "A"])
    nb = CategoricalNB(course_laplace=True).fit(Xc, yc)
    new = np.array([False, "Medium", True], dtype=object)

    def show(d):
        return {str(k): round(float(v), 6) for k, v in d.items()}

    print("\n[S14] example, new sample (False, Medium, True):")
    print("  likelihoods   ", show(nb.likelihoods(new)),
          " posteriors", show(dict(zip(nb.classes_, nb.predict_proba([new])[0]))),
          " ->", str(nb.predict([new])[0]))
    print("  without Laplace:", show(CategoricalNB(course_laplace=False).fit(Xc, yc).likelihoods(new)))
    # [S14] prints 0.05555 for class A: that product uses P(F1=True|A) = 3/3, i.e. it
    # substitutes the value from its generic formula line, not the sample's F1=False.
    print("  [S14]'s printed 0.05555 is the likelihood of (True, Medium, True): %.6f"
          % nb.likelihoods(np.array([True, "Medium", True], dtype=object))["A"])
