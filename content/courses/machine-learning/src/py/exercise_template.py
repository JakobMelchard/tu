"""Reusable scikit-learn pipeline for the 184.702 group assignments (note 17;
leak-free pipelines of notes 01 and 04).

    python exercise_template.py data.csv --target label [--task classification|regression]
                                [--out results/] [--quick] [--tune]
    python exercise_template.py --demo            # synthetic CSV, full run into ./results_demo
    python exercise_template.py                   # quick demo into a temporary directory

Steps: load CSV -> infer numeric/categorical columns -> ColumnTransformer
(impute + scale | impute + one-hot) -> stratified k-fold CV of several models
with several metrics -> results table (CSV + Markdown) -> plots (CV boxplot,
confusion matrix / residuals of the best model, learning curve, permutation
importance) -> optional grid search on the best model.  Everything is fitted
inside the CV folds, so no preprocessing leaks from test to train.

This module *is* the library route (the course lets students pick a toolkit
[S1, S15]); test_exercise_template.py runs it end to end and checks the known
result that the 0R/dummy baseline scores the majority-class share.
"""
import argparse
import os
import sys
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.impute import SimpleImputer
from sklearn.model_selection import StratifiedKFold, KFold, cross_validate, GridSearchCV, learning_curve, train_test_split
from sklearn.inspection import permutation_importance
from sklearn.metrics import ConfusionMatrixDisplay
from sklearn.dummy import DummyClassifier, DummyRegressor
from sklearn.linear_model import LogisticRegression, Ridge
from sklearn.neighbors import KNeighborsClassifier, KNeighborsRegressor
from sklearn.tree import DecisionTreeClassifier, DecisionTreeRegressor
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor, GradientBoostingClassifier, GradientBoostingRegressor
from sklearn.svm import SVC, SVR
from sklearn.neural_network import MLPClassifier, MLPRegressor


# ------------------------------------------------------------------- data
def load(path, target):
    df = pd.read_csv(path)
    if target not in df.columns:
        sys.exit(f"target column {target!r} not in {list(df.columns)}")
    X, y = df.drop(columns=[target]), df[target]
    return X, y


def infer_task(y):
    return "regression" if pd.api.types.is_numeric_dtype(y) and y.nunique() > 20 else "classification"


def make_preprocessor(X):
    num = X.select_dtypes(include="number").columns.tolist()
    cat = [c for c in X.columns if c not in num]
    return ColumnTransformer([
        ("num", Pipeline([("impute", SimpleImputer(strategy="median")), ("scale", StandardScaler())]), num),
        ("cat", Pipeline([("impute", SimpleImputer(strategy="most_frequent")),
                          ("onehot", OneHotEncoder(handle_unknown="ignore", sparse_output=False))]), cat),
    ]), num, cat


# ----------------------------------------------------------------- models
def model_zoo(task, quick=False, seed=0):
    n_est = 50 if quick else 200
    if task == "classification":
        zoo = {
            "dummy": DummyClassifier(strategy="most_frequent"),
            "logreg": LogisticRegression(max_iter=2000),
            "knn": KNeighborsClassifier(),
            "tree": DecisionTreeClassifier(random_state=seed),
            "rf": RandomForestClassifier(n_est, random_state=seed),
            "gb": GradientBoostingClassifier(n_estimators=n_est, random_state=seed),
            "svm_rbf": SVC(probability=False, random_state=seed),
            "mlp": MLPClassifier((64,), max_iter=300 if quick else 1000, random_state=seed),
        }
        grids = {"knn": {"model__n_neighbors": [3, 5, 11, 21]},
                 "rf": {"model__max_depth": [None, 5, 10], "model__min_samples_leaf": [1, 5]},
                 "svm_rbf": {"model__C": [0.1, 1, 10], "model__gamma": ["scale", 0.01, 0.1]},
                 "logreg": {"model__C": [0.01, 0.1, 1, 10]},
                 "gb": {"model__learning_rate": [0.03, 0.1], "model__max_depth": [2, 3]},
                 "tree": {"model__max_depth": [3, 5, None], "model__ccp_alpha": [0, 0.01]},
                 "mlp": {"model__alpha": [1e-4, 1e-2]}, "dummy": {}}
        scoring = {"acc": "accuracy", "f1_macro": "f1_macro", "bal_acc": "balanced_accuracy"}
    else:
        zoo = {
            "dummy": DummyRegressor(),
            "ridge": Ridge(),
            "knn": KNeighborsRegressor(),
            "tree": DecisionTreeRegressor(random_state=seed),
            "rf": RandomForestRegressor(n_est, random_state=seed),
            "gb": GradientBoostingRegressor(n_estimators=n_est, random_state=seed),
            "svr": SVR(),
            "mlp": MLPRegressor((64,), max_iter=300 if quick else 1000, random_state=seed),
        }
        grids = {"ridge": {"model__alpha": [0.01, 0.1, 1, 10, 100]}, "knn": {"model__n_neighbors": [3, 5, 11, 21]},
                 "rf": {"model__max_depth": [None, 5, 10]}, "svr": {"model__C": [0.1, 1, 10]},
                 "gb": {"model__learning_rate": [0.03, 0.1], "model__max_depth": [2, 3]},
                 "tree": {"model__max_depth": [3, 5, None]}, "mlp": {"model__alpha": [1e-4, 1e-2]}, "dummy": {}}
        scoring = {"r2": "r2", "neg_rmse": "neg_root_mean_squared_error", "neg_mae": "neg_mean_absolute_error"}
    if quick:
        zoo = {k: v for k, v in zoo.items() if k in ("dummy", "logreg", "ridge", "knn", "tree", "rf")}
    return zoo, grids, scoring


def cv_splitter(task, k, seed=0):
    return StratifiedKFold(k, shuffle=True, random_state=seed) if task == "classification" else KFold(k, shuffle=True, random_state=seed)


# ---------------------------------------------------------------- reporting
def to_markdown(df, fmt="{:.3f}"):
    """Markdown table without the tabulate dependency."""
    fmt_cell = lambda v: fmt.format(v) if isinstance(v, (float, np.floating)) else str(v)
    lines = ["| " + " | ".join(df.columns) + " |", "|" + "---|" * len(df.columns)]
    lines += ["| " + " | ".join(fmt_cell(v) for v in row) + " |" for row in df.itertuples(index=False)]
    return "\n".join(lines) + "\n"


def compare_models(X, y, task, pre, zoo, scoring, k, seed, out):
    rows, raw = [], {}
    for name, model in zoo.items():
        pipe = Pipeline([("pre", pre), ("model", model)])
        res = cross_validate(pipe, X, y, cv=cv_splitter(task, k, seed), scoring=scoring, n_jobs=1, return_train_score=True)
        row = {"model": name, "fit_s": res["fit_time"].mean()}
        for s in scoring:
            row[f"{s}_mean"], row[f"{s}_std"] = res[f"test_{s}"].mean(), res[f"test_{s}"].std()
            row[f"{s}_train"] = res[f"train_{s}"].mean()
        rows.append(row); raw[name] = res[f"test_{list(scoring)[0]}"]
    table = pd.DataFrame(rows).sort_values(f"{list(scoring)[0]}_mean", ascending=False)
    table.to_csv(os.path.join(out, "cv_results.csv"), index=False)
    with open(os.path.join(out, "cv_results.md"), "w") as f:
        f.write(to_markdown(table))
    print(table.to_string(index=False, float_format=lambda v: f"{v:.3f}"))
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.boxplot(list(raw.values()), tick_labels=list(raw))
    ax.set_ylabel(list(scoring)[0]); ax.set_title(f"{k}-fold CV scores"); ax.grid(alpha=0.3)
    fig.tight_layout(); fig.savefig(os.path.join(out, "cv_boxplot.png"), dpi=120); plt.close(fig)
    return table


def inspect_best(X, y, task, pre, model, name, seed, out, num, cat):
    Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.25, random_state=seed,
                                          stratify=y if task == "classification" else None)
    pipe = Pipeline([("pre", pre), ("model", model)]).fit(Xtr, ytr)
    fig, ax = plt.subplots(figsize=(5, 4))
    if task == "classification":
        ConfusionMatrixDisplay.from_estimator(pipe, Xte, yte, ax=ax, colorbar=False)
        ax.set_title(f"{name}: held-out confusion matrix")
    else:
        pred = pipe.predict(Xte)
        ax.scatter(pred, yte - pred, s=10); ax.axhline(0, color="k", lw=0.8)
        ax.set_xlabel("predicted"); ax.set_ylabel("residual"); ax.set_title(f"{name}: residuals")
    fig.tight_layout(); fig.savefig(os.path.join(out, "best_model_diagnostic.png"), dpi=120); plt.close(fig)
    # permutation importance on the held-out split, on the raw columns (pipeline handles preprocessing)
    pi = permutation_importance(pipe, Xte, yte, n_repeats=5, random_state=seed)
    imp = pd.Series(pi.importances_mean, index=X.columns).sort_values()
    imp.to_csv(os.path.join(out, "permutation_importance.csv"))
    fig, ax = plt.subplots(figsize=(6, 0.3 * len(imp) + 1.5))
    imp.plot.barh(ax=ax); ax.set_xlabel("drop in score when shuffled"); ax.set_title("permutation importance")
    fig.tight_layout(); fig.savefig(os.path.join(out, "permutation_importance.png"), dpi=120); plt.close(fig)
    # learning curve: bias/variance diagnosis
    sizes, tr, va = learning_curve(Pipeline([("pre", pre), ("model", model)]), X, y, cv=cv_splitter(task, 3, seed),
                                   train_sizes=np.linspace(0.2, 1.0, 5), n_jobs=1)
    fig, ax = plt.subplots(figsize=(5, 4))
    ax.plot(sizes, tr.mean(1), "o-", label="train"); ax.plot(sizes, va.mean(1), "s-", label="validation")
    ax.fill_between(sizes, va.mean(1) - va.std(1), va.mean(1) + va.std(1), alpha=0.2)
    ax.set_xlabel("training samples"); ax.set_ylabel("score"); ax.legend(); ax.set_title(f"{name}: learning curve")
    fig.tight_layout(); fig.savefig(os.path.join(out, "learning_curve.png"), dpi=120); plt.close(fig)


def tune_best(X, y, task, pre, model, grid, k, seed):
    gs = GridSearchCV(Pipeline([("pre", pre), ("model", model)]), grid, cv=cv_splitter(task, k, seed), n_jobs=1)
    gs.fit(X, y)
    print(f"grid search: best {gs.best_params_} -> CV score {gs.best_score_:.3f}")
    return gs


# --------------------------------------------------------------------- main
def make_demo_csv(path, seed=0):
    from sklearn.datasets import make_classification
    X, y = make_classification(400, 6, n_informative=3, n_redundant=1, weights=[0.7, 0.3], random_state=seed)
    rng = np.random.default_rng(seed)
    df = pd.DataFrame(X, columns=[f"f{i}" for i in range(6)])
    df["colour"] = rng.choice(["red", "green", "blue"], len(df))
    df["region"] = np.where(y == 1, rng.choice(["north", "south"], len(df), p=[0.8, 0.2]), rng.choice(["north", "south"], len(df)))
    df.loc[rng.random(len(df)) < 0.05, "f0"] = np.nan
    df["label"] = np.where(y == 1, "yes", "no")
    df.to_csv(path, index=False)
    return path


def run(path, target, task=None, out="results", k=5, seed=0, quick=False, tune=False):
    os.makedirs(out, exist_ok=True)
    X, y = load(path, target)
    task = task or infer_task(y)
    pre, num, cat = make_preprocessor(X)
    print(f"{len(X)} rows, {len(num)} numeric + {len(cat)} categorical features, task={task}, "
          f"missing cells={int(X.isna().sum().sum())}")
    if task == "classification":
        print("class balance:", y.value_counts(normalize=True).round(3).to_dict())
    zoo, grids, scoring = model_zoo(task, quick, seed)
    table = compare_models(X, y, task, pre, zoo, scoring, k, seed, out)
    best = table.iloc[0]["model"]
    inspect_best(X, y, task, pre, zoo[best], best, seed, out, num, cat)
    if tune and grids.get(best):
        tune_best(X, y, task, pre, zoo[best], grids[best], k, seed)
    print(f"best model: {best}; outputs in {out}/")
    return table


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("csv", nargs="?"); ap.add_argument("--target", default="label")
    ap.add_argument("--task", choices=["classification", "regression"]); ap.add_argument("--out", default="results")
    ap.add_argument("--folds", type=int, default=5); ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--quick", action="store_true", help="fewer/lighter models"); ap.add_argument("--tune", action="store_true")
    ap.add_argument("--demo", action="store_true", help="generate a synthetic CSV and run on it")
    a = ap.parse_args()
    if not a.csv and not a.demo:                   # bare `python exercise_template.py`: quick demo
        import tempfile
        a.demo, a.quick, a.out = True, True, tempfile.mkdtemp(prefix="ml_exercise_demo_")
    if a.demo:
        a.out = a.out if a.out != "results" else "results_demo"
        a.csv = make_demo_csv(os.path.join(a.out if os.makedirs(a.out, exist_ok=True) is None else a.out, "demo.csv"), a.seed)
    if not a.csv:
        ap.error("give a CSV path or --demo")
    run(a.csv, a.target, a.task, a.out, a.folds, a.seed, a.quick, a.tune)
