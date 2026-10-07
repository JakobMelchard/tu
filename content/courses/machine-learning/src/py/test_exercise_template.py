import os
import numpy as np
import pandas as pd
import pytest

import exercise_template as et


def test_demo_pipeline_runs_end_to_end(tmp_path):
    csv = et.make_demo_csv(str(tmp_path / "demo.csv"))
    table = et.run(csv, "label", out=str(tmp_path / "res"), k=3, quick=True, tune=True)
    assert table.iloc[0]["model"] != "dummy" and table["acc_mean"].max() > 0.7
    # known result: the 0R / most-frequent baseline scores the majority-class share
    share = pd.read_csv(csv)["label"].value_counts(normalize=True).max()
    dummy = table.set_index("model").loc["dummy", "acc_mean"]
    assert dummy == pytest.approx(share, abs=0.01)
    for f in ("cv_results.csv", "cv_results.md", "cv_boxplot.png", "best_model_diagnostic.png",
              "permutation_importance.png", "learning_curve.png"):
        assert os.path.exists(tmp_path / "res" / f)


def test_regression_task_inferred(tmp_path):
    rng = np.random.default_rng(0)
    df = pd.DataFrame(rng.normal(size=(120, 3)), columns=list("abc"))
    df["cat"] = rng.choice(["u", "v"], 120)
    df["y"] = 2 * df.a - df.b + rng.normal(0, 0.1, 120)
    p = str(tmp_path / "r.csv"); df.to_csv(p, index=False)
    table = et.run(p, "y", out=str(tmp_path / "res"), k=3, quick=True)
    assert et.infer_task(df.y) == "regression" and table.iloc[0]["r2_mean"] > 0.9
