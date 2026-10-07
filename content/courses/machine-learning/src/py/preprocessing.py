"""Data preparation from scratch: scaling (z-score, min-max, robust),
encoding (one-hot, ordinal), imputation (mean/median/mode, kNN), outlier flags
(z-score, IQR, winsorising), filter feature selection (variance, correlation,
ANOVA F, mutual information) and class rebalancing (over/undersampling,
SMOTE [S41], class weights).  All transformers follow fit / transform, so they
chain like sklearn's.

Serves note 02 (preprocessing).  Cross-checked in test_preprocessing.py against
sklearn.preprocessing / impute / feature_selection (exact).  Run
`python preprocessing.py` for the demo.
"""
import numpy as np


class StandardScaler:
    """z = (x - mean) / std, per column. Fit on train only (leakage otherwise)."""

    def fit(self, X):
        X = np.asarray(X, float)
        self.mean_, self.scale_ = X.mean(0), X.std(0)
        self.scale_[self.scale_ == 0] = 1.0
        return self

    def transform(self, X):
        return (np.asarray(X, float) - self.mean_) / self.scale_

    def fit_transform(self, X):
        return self.fit(X).transform(X)

    def inverse_transform(self, Z):
        return np.asarray(Z, float) * self.scale_ + self.mean_


class MinMaxScaler:
    """x' = (x - min) / (max - min) mapped to [lo, hi]."""

    def __init__(self, feature_range=(0.0, 1.0)):
        self.lo, self.hi = feature_range

    def fit(self, X):
        X = np.asarray(X, float)
        self.min_, rng = X.min(0), X.max(0) - X.min(0)
        self.range_ = np.where(rng == 0, 1.0, rng)
        return self

    def transform(self, X):
        return self.lo + (np.asarray(X, float) - self.min_) / self.range_ * (self.hi - self.lo)

    def fit_transform(self, X):
        return self.fit(X).transform(X)


class RobustScaler:
    """(x - median) / IQR: insensitive to outliers."""

    def fit(self, X):
        X = np.asarray(X, float)
        q1, q3 = np.percentile(X, [25, 75], axis=0)
        self.center_, self.scale_ = np.median(X, 0), np.where(q3 - q1 == 0, 1.0, q3 - q1)
        return self

    def transform(self, X):
        return (np.asarray(X, float) - self.center_) / self.scale_

    def fit_transform(self, X):
        return self.fit(X).transform(X)


class OneHotEncoder:
    """Categorical columns (object or int) -> 0/1 indicator columns; unseen categories -> all zeros."""

    def fit(self, X):
        X = np.asarray(X, dtype=object)
        self.categories_ = [np.unique(X[:, j]) for j in range(X.shape[1])]
        return self

    def transform(self, X):
        X = np.asarray(X, dtype=object)
        cols = [(X[:, j][:, None] == cats[None, :]).astype(float) for j, cats in enumerate(self.categories_)]
        return np.hstack(cols)

    def fit_transform(self, X):
        return self.fit(X).transform(X)

    def feature_names(self, names):
        return [f"{n}={c}" for n, cats in zip(names, self.categories_) for c in cats]


class OrdinalEncoder:
    """Category -> integer code in sorted order (only meaningful for ordered categories)."""

    def fit(self, X):
        X = np.asarray(X, dtype=object)
        self.categories_ = [np.unique(X[:, j]) for j in range(X.shape[1])]
        return self

    def transform(self, X):
        X = np.asarray(X, dtype=object)
        return np.column_stack([np.searchsorted(c, X[:, j]) for j, c in enumerate(self.categories_)]).astype(float)


class SimpleImputer:
    """Replace NaN by the column mean / median / most_frequent / constant computed on train."""

    def __init__(self, strategy="mean", fill_value=0.0):
        self.strategy, self.fill_value = strategy, fill_value

    def fit(self, X):
        X = np.asarray(X, float)
        if self.strategy == "mean":
            self.statistics_ = np.nanmean(X, 0)
        elif self.strategy == "median":
            self.statistics_ = np.nanmedian(X, 0)
        elif self.strategy == "most_frequent":
            self.statistics_ = np.array([_mode(c[~np.isnan(c)]) for c in X.T])
        else:
            self.statistics_ = np.full(X.shape[1], self.fill_value)
        return self

    def transform(self, X):
        X = np.array(X, float, copy=True)
        mask = np.isnan(X)
        X[mask] = np.broadcast_to(self.statistics_, X.shape)[mask]
        return X

    def fit_transform(self, X):
        return self.fit(X).transform(X)


def _mode(v):
    vals, counts = np.unique(v, return_counts=True)
    return vals[np.argmax(counts)]


def knn_impute(X, k=3):
    """Fill NaNs with the mean of the k nearest rows (nan-aware Euclidean on shared columns)."""
    X = np.array(X, float, copy=True)
    out = X.copy()
    for i in np.where(np.isnan(X).any(1))[0]:
        shared = ~np.isnan(X[i]) & ~np.isnan(X)
        # nan-euclidean: rescale the sum over shared coordinates to the full dimension
        d = np.sqrt(X.shape[1] / np.maximum(shared.sum(1), 1) * np.nansum(np.where(shared, (X - X[i]) ** 2, 0), 1))
        d[i] = np.inf
        d[shared.sum(1) == 0] = np.inf          # no coordinate in common: not a usable neighbour
        for j in np.where(np.isnan(X[i]))[0]:
            cand = np.where(~np.isnan(X[:, j]))[0]
            nn = cand[np.argsort(d[cand])[:k]]
            out[i, j] = X[nn, j].mean()
    return out


# ------------------------------------------------------------------- outliers
def zscore_outliers(X, thresh=3.0):
    """Boolean mask of rows with any |z| > thresh."""
    Z = StandardScaler().fit_transform(X)
    return (np.abs(Z) > thresh).any(1)


def iqr_outliers(X, k=1.5):
    """Tukey fences: outside [Q1 - k IQR, Q3 + k IQR] in any column."""
    X = np.asarray(X, float)
    q1, q3 = np.percentile(X, [25, 75], axis=0)
    iqr = q3 - q1
    return ((X < q1 - k * iqr) | (X > q3 + k * iqr)).any(1)


def winsorize(X, lower=1, upper=99):
    """Clip each column to its [lower, upper] percentile instead of dropping rows."""
    X = np.asarray(X, float)
    lo, hi = np.percentile(X, [lower, upper], axis=0)
    return np.clip(X, lo, hi)


# ----------------------------------------------------------- feature selection
def variance_threshold(X, thresh=0.0):
    """Keep columns whose variance exceeds thresh (drops constant columns)."""
    return np.var(np.asarray(X, float), 0) > thresh


def correlation_filter(X, thresh=0.95):
    """Greedy: drop the later of any pair of columns with |corr| > thresh."""
    C = np.abs(np.corrcoef(np.asarray(X, float), rowvar=False))
    keep = np.ones(C.shape[0], bool)
    for j in range(C.shape[0]):
        if keep[j]:
            keep[j + 1:] &= C[j, j + 1:] <= thresh
    return keep


def anova_f(X, y):
    """One-way ANOVA F statistic per feature: between-class / within-class variance."""
    X, y = np.asarray(X, float), np.asarray(y)
    classes = np.unique(y)
    n, k = len(y), len(classes)
    grand = X.mean(0)
    ssb = sum(np.sum(y == c) * (X[y == c].mean(0) - grand) ** 2 for c in classes)
    ssw = sum(((X[y == c] - X[y == c].mean(0)) ** 2).sum(0) for c in classes)
    return (ssb / (k - 1)) / (ssw / (n - k))


def mutual_information_discrete(x, y):
    """I(X;Y) = sum p(x,y) log p(x,y)/(p(x)p(y)) for two discrete arrays (nats)."""
    x, y = np.asarray(x), np.asarray(y)
    xs, ys = np.unique(x), np.unique(y)
    joint = np.array([[np.mean((x == a) & (y == b)) for b in ys] for a in xs])
    px, py = joint.sum(1, keepdims=True), joint.sum(0, keepdims=True)
    nz = joint > 0
    return float(np.sum(joint[nz] * np.log(joint[nz] / (px @ py)[nz])))


# ------------------------------------------------------------ imbalanced data
def random_oversample(X, y, rng=0):
    """Duplicate minority rows until all classes have the majority count."""
    rng = np.random.default_rng(rng)
    X, y = np.asarray(X), np.asarray(y)
    classes, counts = np.unique(y, return_counts=True)
    idx = []
    for c, n in zip(classes, counts):
        ci = np.where(y == c)[0]
        idx.append(np.r_[ci, rng.choice(ci, counts.max() - n)])
    idx = np.concatenate(idx)
    return X[idx], y[idx]


def random_undersample(X, y, rng=0):
    rng = np.random.default_rng(rng)
    X, y = np.asarray(X), np.asarray(y)
    classes, counts = np.unique(y, return_counts=True)
    idx = np.concatenate([rng.choice(np.where(y == c)[0], counts.min(), replace=False) for c in classes])
    return X[idx], y[idx]


def smote(X, y, minority, k=5, n_new=None, rng=0):
    """SMOTE: synthetic minority points on segments between a minority sample and one of its k minority neighbours."""
    rng = np.random.default_rng(rng)
    X, y = np.asarray(X, float), np.asarray(y)
    Xm = X[y == minority]
    n_new = n_new or (len(y) - 2 * len(Xm))
    D = np.linalg.norm(Xm[:, None] - Xm[None], axis=2)
    np.fill_diagonal(D, np.inf)
    nn = np.argsort(D, 1)[:, :k]
    i = rng.integers(0, len(Xm), n_new)
    j = nn[i, rng.integers(0, k, n_new)]
    lam = rng.random((n_new, 1))
    new = Xm[i] + lam * (Xm[j] - Xm[i])
    return np.vstack([X, new]), np.r_[y, np.full(n_new, minority)]


def class_weights(y):
    """'balanced' weights n / (k * n_c): rare classes count more in the loss."""
    classes, counts = np.unique(y, return_counts=True)
    return dict(zip(classes, len(y) / (len(classes) * counts)))


if __name__ == "__main__":
    rng = np.random.default_rng(0)
    X = rng.normal([5, 50, 0.5], [1, 10, 0.1], (200, 3))
    X[rng.random(X.shape) < 0.05] = np.nan
    X[3] = [40, 50, 0.5]                                  # planted outlier
    Xi = SimpleImputer("median").fit_transform(X)
    print("imputed NaNs:", np.isnan(X).sum(), "->", np.isnan(Xi).sum())
    print("z-score outliers at rows", np.where(zscore_outliers(Xi))[0])
    Z = StandardScaler().fit_transform(Xi)
    print("scaled means", Z.mean(0).round(3), "stds", Z.std(0).round(3))
    cat = np.array([["red", "S"], ["blue", "M"], ["red", "L"]], dtype=object)
    enc = OneHotEncoder().fit(cat)
    print(enc.feature_names(["colour", "size"]), "\n", enc.transform(cat))
    y = (rng.random(200) < 0.1).astype(int)
    Xo, yo = smote(Xi, y, minority=1, rng=0)
    print("SMOTE: class counts", np.bincount(y), "->", np.bincount(yo), " weights", class_weights(y))
