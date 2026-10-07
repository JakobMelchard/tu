"""Run the substitute-source exercise folders as part of the normal suite.

These are the folders built from *other institutions'* free material [S59-S61],
not from anything 192.043 published -- 192.043 has no past paper in any year
[S24].  Each solution.py checks itself with asserts; this file imports it, calls
solve(), and additionally pins the numbers that another institution published,
because those are the ones that validate the source reading.
"""
import importlib.util
import os

import pytest

_HERE = os.path.dirname(os.path.abspath(__file__))
_EXERCISES = os.path.abspath(os.path.join(_HERE, "..", "exercises"))

FOLDERS = ["mit-18.404j-2020", "princeton-arora-barak-2007", "mit-6.046j-2015"]


def _load(folder):
    path = os.path.join(_EXERCISES, folder, "solution.py")
    spec = importlib.util.spec_from_file_location(
        "sub_" + folder.replace("-", "_").replace(".", "_"), path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.mark.parametrize("folder", FOLDERS)
def test_substitute_solution_runs(folder):
    readme = os.path.join(_EXERCISES, folder, "README.md")
    assert os.path.isfile(readme), folder + " must carry its provenance"
    text = open(readme, encoding="utf-8").read()
    assert "Licence" in text and "Provenance" in text, \
        folder + "'s README must state provenance and licence in full"
    result = _load(folder).solve()
    assert isinstance(result, dict) and result


def test_3sat_to_solitaire_is_answer_preserving():
    """[S59] Q2: the reduction, checked on every 3-CNF over 3 vars, <= 4 clauses."""
    r = _load("mit-18.404j-2020").solve()
    assert r["q3"]["mismatches"] == 0
    assert r["q3"]["formulas tested"] == 112791


def test_edmonds_karp_reproduces_mits_published_flow_value():
    """[S61] final, "be the computer": one augmentation takes the flow 25 -> 26."""
    r = _load("mit-6.046j-2015").solve()["p6"]
    assert r["flow before"] == 25
    assert r["bottleneck"] == 1
    assert r["flow after"] == 26, "MIT's published answer"
    assert r["augmenting path"] == ["s", 3, 2, 5, "t"]
    assert r["max flow"] == r["min cut value"] == 27


def test_list_scheduling_bound_is_tight():
    """[S61] P8: greedy hits 2 - 1/m exactly on the standard bad family."""
    t = _load("mit-6.046j-2015").solve()["p8"]["tight family m=4"]
    assert t["greedy"] == 7 and t["opt"] == 4
    assert abs(t["ratio"] - t["limit"]) < 1e-12


def test_feynman_path_sum_uses_the_courses_qubit_order():
    """[S60] ch. 10: the path sum matches sim.py, whose order is Egly's [S16].

    The same amplitude read in Qiskit's reversed order is a different number --
    that is the endianness trap, checked rather than assumed.
    """
    r = _load("princeton-arora-barak-2007").solve()["pt4"]
    assert r["matches statevector"] is True
    assert r["paths summed per output"] == 4096
    course = r["amplitude of |011> (course order, qubit 0 = MSB)"]
    qiskit = r["same index read in Qiskit order"]
    assert abs(course) < 1e-12 < abs(qiskit)


def test_adleman_union_bound_is_below_one():
    """[S60] ch. 7: amplification must beat 2^-n before the union bound bites."""
    r = _load("princeton-arora-barak-2007").solve()["pt3"]
    assert r["union bound"] < 1.0
    assert r["per-input error"] < 2.0 ** -6
