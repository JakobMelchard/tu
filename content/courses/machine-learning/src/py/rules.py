"""Rule learners: 0R (ZeroR), 1R (OneR) and the covering algorithm (PRISM).

These are the baselines the course teaches next to the decision tree (note 06).
1R is asked in more past papers of 184.702 than any calculation except naive
Bayes, always in the form "which attribute does 1R pick, and what accuracy /
precision does the resulting rule set get on the held-out rows?".

Algorithm sources:
  0R / 1R / PRISM  - Witten, Frank, Hall & Pal, *Data Mining* [S22]
  1R               - Holte (1993), *Machine Learning* 11:63-90 [S29]
Exam evidence: [S11] E17b, E18a, E19a, E20b, E21b, E24a, E26a.

Features are treated as **nominal**: values are compared for equality, never
ordered.  Numeric columns must be discretised first; `discretize_1r` implements
Holte's minimum-bucket-size rule.

Run `python rules.py` for a demo on the exam-style table of E20b.
"""
import numpy as np

from model_selection import BaseEstimator


def _majority(labels):
    """Most frequent label; ties broken by the smallest label for determinism."""
    vals, counts = np.unique(labels, return_counts=True)
    return vals[np.argmax(counts)]


class ZeroR(BaseEstimator):
    """Predict the majority class (or the mean, for regression) for everything.

    The baseline every exercise report has to beat [S10], and the model gradient
    boosting starts from -- hence the recurring true/false item "the first model
    in gradient boosting is a zero rule model" (true) [S12].
    """

    def __init__(self, task="classification"):
        self.task = task

    def fit(self, X, y):
        y = np.asarray(y)
        self.prediction_ = float(np.mean(y)) if self.task == "regression" else _majority(y)
        self.classes_ = np.unique(y) if self.task != "regression" else None
        return self

    def predict(self, X):
        return np.full(len(np.asarray(X, dtype=object)), self.prediction_)


class OneR(BaseEstimator):
    """Holte's 1R: one rule per value of the single best attribute [S29].

    fit() builds, for every attribute j, the rule set
        for each value v of j:  predict the majority class among rows with x_j = v
    counts how many training rows that rule set gets wrong, and keeps the
    attribute with the fewest errors.  `rule_table_` holds the whole comparison,
    which is what an exam answer has to show.

    1R is a decision tree with only a root node -- a decision stump [S12].
    """

    def __init__(self):
        pass

    def fit(self, X, y):
        X = np.asarray(X, dtype=object)
        y = np.asarray(y)
        self.default_ = _majority(y)
        self.rule_table_ = []
        for j in range(X.shape[1]):
            rules, errors = {}, 0
            for v in np.unique(X[:, j]):
                mask = X[:, j] == v
                rules[v] = _majority(y[mask])
                errors += int(np.sum(y[mask] != rules[v]))
            self.rule_table_.append(
                dict(attribute=j, rules=rules, errors=errors, total=len(y),
                     accuracy=1 - errors / len(y))
            )
        best = min(self.rule_table_, key=lambda r: (r["errors"], r["attribute"]))
        self.attribute_, self.rules_, self.errors_ = best["attribute"], best["rules"], best["errors"]
        return self

    def predict(self, X):
        X = np.asarray(X, dtype=object)
        return np.array([self.rules_.get(v, self.default_) for v in X[:, self.attribute_]])

    def to_text(self, feature_names=None):
        name = feature_names[self.attribute_] if feature_names else f"x{self.attribute_}"
        body = "\n".join(f"  IF {name} = {str(v)} THEN {str(c)}"
                         for v, c in sorted(self.rules_.items(), key=str))
        return f"1R on {name} ({self.errors_} training errors)\n{body}\n  ELSE {str(self.default_)}"


def discretize_1r(x, y, min_bucket=6):
    """Holte's discretisation for a numeric attribute [S29].

    Sort by x and walk through it, accumulating a bucket.  A bucket closes once
    it holds at least `min_bucket` instances of its majority class *and* the
    next instance has a different value and a different class; adjacent buckets
    with the same majority class are then merged, so a threshold survives only
    where the predicted class actually changes.  Returns the thresholds.
    """
    x, y = np.asarray(x, float), np.asarray(y)
    order = np.argsort(x, kind="stable")
    xs, ys = x[order], y[order]

    buckets, start = [], 0                      # (end_index_exclusive, majority)
    while start < len(xs):
        end, counts = start, {}
        while end < len(xs):
            counts[ys[end]] = counts.get(ys[end], 0) + 1
            end += 1
            majority = max(counts, key=counts.get)
            if (counts[majority] >= min_bucket and end < len(xs)
                    and xs[end] != xs[end - 1] and ys[end] != majority):
                break   # enough of the majority class, and the class now changes
        buckets.append((end, max(counts, key=counts.get)))
        start = end

    # Holte merges adjacent buckets that predict the same class, so a boundary
    # only survives where the majority class actually changes [S29].
    thresholds = []
    for i in range(len(buckets) - 1):
        end, majority = buckets[i]
        if majority != buckets[i + 1][1]:
            thresholds.append((xs[end - 1] + xs[end]) / 2)
    return np.array(thresholds)


class Prism(BaseEstimator):
    """The covering algorithm (PRISM) [S22]: separate-and-conquer rule induction.

    For each class in turn, repeatedly grow one rule by greedily appending the
    (attribute, value) test with the highest accuracy p/t on the instances the
    rule still covers (ties broken by larger t), until the rule is pure; then
    remove the covered instances and start the next rule.  Asked in E19a
    ("generate covering algorithms to separate Martians from humans") [S11].
    """

    def __init__(self, max_rules=50):
        self.max_rules = max_rules

    def fit(self, X, y):
        X = np.asarray(X, dtype=object)
        y = np.asarray(y)
        self.default_ = _majority(y)
        self.rules_ = []                      # list of (conditions, class)
        for cls in np.unique(y):
            remaining = np.ones(len(y), bool)
            while np.any(remaining & (y == cls)) and len(self.rules_) < self.max_rules:
                conditions, covered = [], remaining.copy()
                used = set()
                while True:
                    best, best_key = None, (-1.0, -1)
                    for j in range(X.shape[1]):
                        if j in used:
                            continue
                        for v in np.unique(X[covered, j]):
                            sel = covered & (X[:, j] == v)
                            t = int(np.sum(sel))
                            if t == 0:
                                continue
                            p = int(np.sum(sel & (y == cls)))
                            key = (p / t, t)
                            if key > best_key:
                                best_key, best = key, (j, v, sel)
                    if best is None:
                        break
                    j, v, sel = best
                    conditions.append((j, v))
                    used.add(j)
                    covered = sel
                    if best_key[0] == 1.0 or len(used) == X.shape[1]:
                        break
                if not conditions:
                    break
                self.rules_.append((tuple(conditions), cls))
                remaining &= ~covered
        return self

    def predict(self, X):
        X = np.asarray(X, dtype=object)
        out = []
        for row in X:
            for conditions, cls in self.rules_:
                if all(row[j] == v for j, v in conditions):
                    out.append(cls)
                    break
            else:
                out.append(self.default_)
        return np.array(out)

    def to_text(self, feature_names=None):
        def name(j):
            return feature_names[j] if feature_names else f"x{j}"
        lines = [
            "IF " + " AND ".join(f"{name(j)} = {str(v)}" for j, v in conds) + f" THEN {str(cls)}"
            for conds, cls in self.rules_
        ]
        return "\n".join(lines + [f"ELSE {str(self.default_)}"])


if __name__ == "__main__":
    # The E20b shape: 13 rows, four nominal attributes, binary target; 1R is
    # trained on rows 1-8 and evaluated on rows 9-13 [S11].
    names = ["age", "education", "income", "marital"]
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
    y = np.array(["no", "no", "yes", "yes", "no", "yes", "no", "yes",
                  "no", "yes", "yes", "yes", "no"])

    Xtr, ytr, Xte, yte = X[:8], y[:8], X[8:], y[8:]

    zr = ZeroR().fit(Xtr, ytr)
    print("0R predicts %s for everything; test accuracy %.2f"
          % (zr.prediction_, np.mean(zr.predict(Xte) == yte)))

    one = OneR().fit(Xtr, ytr)
    print("\nper-attribute error table (this is what the exam wants to see):")
    for row in one.rule_table_:
        print("  %-10s errors %d/%d  accuracy %.3f  rules %s"
              % (names[row["attribute"]], row["errors"], row["total"],
                 row["accuracy"], {str(k): str(v) for k, v in sorted(row["rules"].items())}))
    print("\n" + one.to_text(names))
    pred = one.predict(Xte)
    tp = int(np.sum((pred == "yes") & (yte == "yes")))
    fp = int(np.sum((pred == "yes") & (yte != "yes")))
    fn = int(np.sum((pred != "yes") & (yte == "yes")))
    print("test rows  pred %s  true %s" % ([str(v) for v in pred], [str(v) for v in yte]))
    print("accuracy %.2f  precision(yes) %.2f  recall(yes) %.2f"
          % (np.mean(pred == yte), tp / max(tp + fp, 1), tp / max(tp + fn, 1)))

    print("\nPRISM covering rules on the full table:")
    print(Prism().fit(X, y).to_text(names))
