"""Tests for roofline.py, including the parse of Rupp's vendored data [S5]."""
import pytest

from roofline import KERNELS, Machine, load_rupp, machines, plot, table


def test_vendored_rupp_rows():
    intel = {n: (y, dp, bw) for y, n, dp, bw in load_rupp("data-intel.txt", 2, 4)}
    nv = {n: (y, dp, bw) for y, n, dp, bw in load_rupp("data-dp-nvidia.txt", 1, 3)}
    assert intel["Xeon Platinum 8180"] == (2017, 2240.0, 120.0)
    assert nv["Tesla V100"] == (2017, 7800.0, 900.0)
    assert nv["Tesla K20"] == (2012, 1173.0, 208.0)


def test_machine_balance_grew_over_time():
    # Rupp's point [S6]: FLOPs grow faster than bandwidth -> ridge moves right
    nv = load_rupp("data-dp-nvidia.txt", 1, 3)
    first, last = nv[0], nv[-1]
    assert last[2] / last[3] > first[2] / first[3]


def test_roofline_formula():
    m = Machine("toy", 1000, 100, "")
    assert m.ridge == 10
    assert m.attainable(1) == 100 and m.bound(1) == "memory"
    assert m.attainable(100) == 1000 and m.bound(100) == "compute"


def test_ridges_and_bounds():
    ms = {m.name: m for m in machines()}
    assert ms["H100 SXM (vector)"].ridge == pytest.approx(10.15, abs=0.01)
    assert ms["Tesla V100"].ridge == pytest.approx(8.67, abs=0.01)
    for m in ms.values():  # triad and SpMV are memory bound everywhere
        assert m.bound(KERNELS["triad a=b+s*c"]) == "memory"
        assert m.bound(KERNELS["SpMV CSR (12 B/nnz)"]) == "memory"
        assert m.bound(KERNELS["DGEMM n=4096 (3 n^2 moved)"]) == "compute"


def test_table_and_plot(tmp_path):
    assert "ridge" in table(machines())
    out = tmp_path / "r.png"
    plot(machines(), str(out))
    assert out.stat().st_size > 10_000
