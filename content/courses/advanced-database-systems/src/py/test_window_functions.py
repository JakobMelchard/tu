import pandas as pd
import pytest

import window_functions as wf


@pytest.mark.parametrize("name", list(wf.QUERIES))
def test_expected_rows(name):
    assert wf.run(wf.make_db(), name) == wf.EXPECTED[name]


def exam_df():
    return pd.DataFrame(wf.EXAM, columns=["student", "course", "points"])


def test_ranks_against_pandas():
    df = exam_df()
    g = df.groupby("course")["points"]
    df["rnk"] = g.rank(method="min", ascending=False).astype(int)      # RANK
    df["drnk"] = g.rank(method="dense", ascending=False).astype(int)   # DENSE_RANK
    df = df.sort_values(["course", "points", "student"], ascending=[True, False, True])
    df["rn"] = df.groupby("course").cumcount() + 1                     # ROW_NUMBER
    got = [(c, s, p, rn, r, d) for s, c, p, r, d, rn in df.itertuples(index=False)]
    assert got == wf.EXPECTED["ranks"]


def test_running_and_moving_against_pandas():
    t = pd.DataFrame(wf.TXN, columns=["id", "day", "amount"])
    rows_sum = t["amount"].cumsum()
    range_sum = t["day"].map(t.groupby("day")["amount"].sum().cumsum())   # peers together
    exp = wf.EXPECTED["running_range_vs_rows"]
    assert list(range_sum) == [r[3] for r in exp]
    assert list(rows_sum) == [r[4] for r in exp]
    ma = t["amount"].rolling(3, min_periods=1).mean().round(3)
    assert list(ma) == [r[1] for r in wf.EXPECTED["moving_avg"]]
    diff = t["amount"].diff()
    assert [None if pd.isna(x) else int(x) for x in diff] == [r[1] for r in wf.EXPECTED["lag"]]


def test_avg_difference_against_pandas():
    df = exam_df()
    df["delta"] = df["points"] - df.groupby("course")["points"].transform("mean")
    df = df.sort_values(["course", "student"])
    assert [(c, s, d) for s, c, _, d in df.itertuples(index=False)] == wf.EXPECTED["diff_from_avg"]
