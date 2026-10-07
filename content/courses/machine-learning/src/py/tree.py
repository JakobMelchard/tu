"""CART decision trees from scratch: classification (Gini / entropy) and
regression (MSE), binary splits on numeric features, optional sample weights,
minimal cost-complexity (weakest-link) pruning, impurity-based feature
importance.  Entropy and information gain in the lecture's notation [S13].

Serves note 06 (decision trees; 0R / 1R / PRISM are in rules.py).
Cross-checked in test_tree.py against sklearn.tree (same root split, same
pruned leaf count for the same ccp_alpha).  Run `python tree.py` for the iris
demo.
"""
import numpy as np
from model_selection import BaseEstimator


def entropy(p):
    p = p[p > 0]
    return float(-np.sum(p * np.log2(p)))


def gini(p):
    return float(1 - np.sum(p ** 2))


def information_gain(y_parent, splits):
    """IG = H(parent) - sum_k |S_k|/|S| H(S_k) for a list of child label arrays."""
    H = lambda y: entropy(np.unique(y, return_counts=True)[1] / len(y))
    return H(y_parent) - sum(len(s) / len(y_parent) * H(s) for s in splits)


class Node:
    __slots__ = ("feature", "threshold", "left", "right", "value", "impurity", "n", "leaf_id")

    def __init__(self, value, impurity, n):
        self.feature = self.threshold = self.left = self.right = None
        self.value, self.impurity, self.n = value, impurity, n

    @property
    def is_leaf(self):
        return self.left is None


class DecisionTree(BaseEstimator):
    """criterion: 'gini' | 'entropy' (classification) | 'mse' (regression)."""

    def __init__(self, criterion="gini", max_depth=None, min_samples_split=2, min_samples_leaf=1,
                 max_features=None, ccp_alpha=0.0, rng=0):
        self.criterion, self.max_depth = criterion, max_depth
        self.min_samples_split, self.min_samples_leaf = min_samples_split, min_samples_leaf
        self.max_features, self.ccp_alpha, self.rng = max_features, ccp_alpha, rng

    # ------------------------------------------------------------- impurities
    def _impurity_from_stats(self, s, n):
        """s: class-weight sums (classification, shape ... x K) or (sum, sumsq) (regression)."""
        if self.criterion == "mse":
            mean = s[..., 0] / n
            return s[..., 1] / n - mean ** 2
        p = s / n[..., None]
        if self.criterion == "gini":
            return 1 - (p ** 2).sum(-1)
        with np.errstate(divide="ignore", invalid="ignore"):
            return -np.where(p > 0, p * np.log2(p), 0).sum(-1)

    def _stats(self, Y, w):
        return (w[:, None] * Y) if self.criterion != "mse" else np.column_stack([w * Y, w * Y ** 2])

    # ---------------------------------------------------------------- fitting
    def fit(self, X, y, sample_weight=None):
        X, y = np.asarray(X, float), np.asarray(y)
        w = np.ones(len(y)) if sample_weight is None else np.asarray(sample_weight, float)
        self.is_classifier_ = self.criterion != "mse"
        if self.is_classifier_:
            self.classes_, yi = np.unique(y, return_inverse=True)
            Y = np.eye(len(self.classes_))[yi]
        else:
            Y = y.astype(float)
        self.n_features_ = X.shape[1]
        self._rng = np.random.default_rng(self.rng)
        self.root_ = self._grow(X, Y, w, depth=0)
        if self.ccp_alpha > 0:
            self._prune(self.ccp_alpha)
        self._number_leaves()
        return self

    def _node(self, Y, w):
        n = w.sum()
        s = self._stats(Y, w).sum(0)
        value = s / n if self.is_classifier_ else s[0] / n
        return Node(value, float(self._impurity_from_stats(s, n)), n), s

    def _grow(self, X, Y, w, depth):
        node, s_total = self._node(Y, w)
        if (node.impurity <= 1e-12 or len(Y) < self.min_samples_split
                or (self.max_depth is not None and depth >= self.max_depth)):
            return node
        split = self._best_split(X, Y, w, s_total, node.impurity)
        if split is None:
            return node
        j, t = split
        mask = X[:, j] <= t
        node.feature, node.threshold = j, t
        node.left = self._grow(X[mask], Y[mask], w[mask], depth + 1)
        node.right = self._grow(X[~mask], Y[~mask], w[~mask], depth + 1)
        return node

    def _best_split(self, X, Y, w, s_total, parent_imp):
        n_feat = X.shape[1]
        k = n_feat if self.max_features is None else (
            max(1, int(np.sqrt(n_feat))) if self.max_features == "sqrt" else
            max(1, int(np.log2(n_feat))) if self.max_features == "log2" else int(self.max_features))
        feats = self._rng.permutation(n_feat)[:k] if k < n_feat else range(n_feat)
        best, best_gain = None, 1e-12
        n_total, S = w.sum(), self._stats(Y, w)
        for j in feats:
            order = np.argsort(X[:, j], kind="stable")
            xs, ws = X[order, j], w[order]
            left_s = np.cumsum(S[order], 0)[:-1]              # stats of the left child for each cut
            left_n = np.cumsum(ws)[:-1]
            right_s, right_n = s_total - left_s, n_total - left_n
            cnt = np.arange(1, len(xs))                        # unweighted sample counts
            valid = (xs[1:] != xs[:-1]) & (cnt >= self.min_samples_leaf) & (len(xs) - cnt >= self.min_samples_leaf)
            if not valid.any():
                continue
            with np.errstate(divide="ignore", invalid="ignore"):
                child = (left_n * self._impurity_from_stats(left_s, left_n)
                         + right_n * self._impurity_from_stats(right_s, right_n)) / n_total
            child = np.where(valid, child, np.inf)
            i = int(np.argmin(child))
            gain = parent_imp - child[i]
            if gain > best_gain:
                best_gain, best = gain, (j, (xs[i] + xs[i + 1]) / 2)
        return best

    # ---------------------------------------------------------------- pruning
    def _prune(self, alpha):
        """Weakest-link pruning: collapse the subtree with the smallest
        g(t) = (R(t) - R(T_t)) / (|leaves(T_t)| - 1) while g(t) <= alpha."""
        N = self.root_.n
        while True:
            best = [None, np.inf]

            def walk(node):
                if node.is_leaf:
                    return node.impurity * node.n / N, 1
                rl, nl = walk(node.left)
                rr, nr = walk(node.right)
                r_sub, leaves = rl + rr, nl + nr
                g = (node.impurity * node.n / N - r_sub) / (leaves - 1)
                if g < best[1]:
                    best[:] = [node, g]
                return r_sub, leaves
            walk(self.root_)
            if best[0] is None or best[1] > alpha:
                return
            best[0].left = best[0].right = None

    def _number_leaves(self):
        self.n_leaves_ = 0

        def walk(node):
            if node.is_leaf:
                node.leaf_id = self.n_leaves_; self.n_leaves_ += 1
            else:
                walk(node.left); walk(node.right)
        walk(self.root_)

    # ------------------------------------------------------------- prediction
    def _leaf(self, x):
        node = self.root_
        while not node.is_leaf:
            node = node.left if x[node.feature] <= node.threshold else node.right
        return node

    def apply(self, X):
        return np.array([self._leaf(x).leaf_id for x in np.asarray(X, float)])

    def predict_proba(self, X):
        return np.array([self._leaf(x).value for x in np.asarray(X, float)])

    def predict(self, X):
        out = self.predict_proba(X)
        return self.classes_[np.argmax(out, 1)] if self.is_classifier_ else out

    def leaves(self):
        out = []
        def walk(n):
            out.append(n) if n.is_leaf else (walk(n.left), walk(n.right))
        walk(self.root_)
        return out

    @property
    def feature_importances_(self):
        """Total weighted impurity decrease per feature, normalised to sum 1."""
        imp = np.zeros(self.n_features_)

        def walk(node):
            if node.is_leaf:
                return
            imp[node.feature] += node.n * node.impurity - node.left.n * node.left.impurity - node.right.n * node.right.impurity
            walk(node.left); walk(node.right)
        walk(self.root_)
        return imp / imp.sum() if imp.sum() > 0 else imp

    def depth(self):
        d = lambda n: 0 if n.is_leaf else 1 + max(d(n.left), d(n.right))
        return d(self.root_)

    def to_text(self, names=None, node=None, indent=""):
        node = node or self.root_
        if node.is_leaf:
            val = self.classes_[np.argmax(node.value)] if self.is_classifier_ else round(float(node.value), 3)
            return f"{indent}-> {val}  (n={node.n:g}, impurity={node.impurity:.3f})\n"
        name = names[node.feature] if names else f"x{node.feature}"
        return (f"{indent}{name} <= {node.threshold:.3f}\n" + self.to_text(names, node.left, indent + "|  ")
                + f"{indent}{name} > {node.threshold:.3f}\n" + self.to_text(names, node.right, indent + "|  "))


if __name__ == "__main__":
    from sklearn.datasets import load_iris
    from model_selection import train_test_split
    from metrics import accuracy

    d = load_iris()
    Xtr, Xte, ytr, yte = train_test_split(d.data, d.target, 0.3, stratify=True, rng=0)
    for crit in ("gini", "entropy"):
        t = DecisionTree(crit).fit(Xtr, ytr)
        print(f"{crit}: depth {t.depth()}, leaves {t.n_leaves_}, test acc {accuracy(yte, t.predict(Xte)):.3f}")
    t = DecisionTree("gini", ccp_alpha=0.02).fit(Xtr, ytr)
    print(f"pruned (alpha=0.02): leaves {t.n_leaves_}, test acc {accuracy(yte, t.predict(Xte)):.3f}")
    print(t.to_text(d.feature_names))
    print("feature importances", t.feature_importances_.round(3))
    y = np.array([1, 1, 0, 0, 1, 0]); print("IG of a split:", round(information_gain(y, [y[:3], y[3:]]), 4))
