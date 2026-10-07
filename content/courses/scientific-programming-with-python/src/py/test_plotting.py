"""Tests for plotting.py (note 04): every figure writes a PNG; pandas groupby, pivot, CSV."""
import numpy as np
import pandas as pd
import pytest

import plotting as pl


@pytest.fixture(scope="module")
def df():
    return pl.make_measurements(n=90, seed=0)


def test_every_plot_writes_a_png(tmp_path):
    paths = pl.all_plots(tmp_path)
    assert len(paths) == 6
    for p in paths:
        assert p.exists() and p.stat().st_size > 1000
        assert p.read_bytes()[:8] == b"\x89PNG\r\n\x1a\n"     # PNG magic number


def test_dataframe_basics(df):
    assert list(df.columns) == ["sample", "temp_K", "conductivity"]
    assert df.dtypes["conductivity"] == np.float64 and df["temp_K"].dtype.kind == "i"
    assert isinstance(df["conductivity"].to_numpy(), np.ndarray)


def test_groupby_and_pivot(df):
    s = pl.summarise(df)
    assert s.index.names == ["sample", "temp_K"] and s["count"].sum() == len(df)
    w = pl.wide_table(df)
    assert list(w.columns) == [300, 350, 400] and list(w.index) == ["A", "B", "C"]
    # conductivity grows with temperature for every sample
    assert (w[400] > w[300]).all()
    # pivot_table mean must equal groupby mean
    assert np.isclose(w.loc["B", 350], s.loc[("B", 350), "mean"])


def test_csv_roundtrip(df, tmp_path):
    back = pl.csv_roundtrip(df, tmp_path / "m.csv")
    pd.testing.assert_frame_equal(back, df, check_exact=False)
