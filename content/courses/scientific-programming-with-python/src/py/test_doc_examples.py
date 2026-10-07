"""Executable source verification for the notes.

Each test asserts one *version-sensitive* claim that ``../notes`` makes, with
the documentation page it comes from in the docstring.  The point is not
coverage: it is that a library upgrade which changes one of these behaviours
breaks the test suite instead of silently making a note wrong.  The version set
is recorded in ``../../refs/SOURCES.md`` S40.

Run:  ../../../../.venv/bin/python -m pytest test_doc_examples.py -q
"""
from __future__ import annotations

import importlib.metadata as md
import multiprocessing as mp
import sys
import warnings

import numpy as np
import pytest

import optimisation
import parallel

# Versions the notes were verified against on 2026-09-27 (refs/SOURCES.md S40).
# 2026-09-22 had PuLP 3.3.2; the venv re-created on 2026-09-27 resolved 4.0.0.
RECORDED = {"numpy": "2.5.3", "scipy": "1.18.1", "pandas": "3.0.6",
            "matplotlib": "3.11.2", "pytest": "9.1.1", "pulp": "4.0.0",
            "ipython": "9.17.1"}


def _major_minor(v: str) -> tuple[int, int]:
    return int(v.split(".")[0]), int(v.split(".")[1])


def test_recorded_versions():
    """Only major.minor is enforced: a patch bump is fine, a minor bump means
    the note headers and refs/docs-map.md need re-checking."""
    assert _major_minor(sys.version.split()[0]) == (3, 12)
    for pkg, recorded in RECORDED.items():
        assert _major_minor(md.version(pkg)) == _major_minor(recorded), (
            f"{pkg} is {md.version(pkg)}, notes were verified against {recorded}"
        )


# --------------------------------------------------------------------- NumPy
def test_python_scalars_are_weak():
    """NEP 50: a Python scalar does not upcast the array.

    https://numpy.org/neps/nep-0050-scalar-promotion.html  (note 02 §2)
    """
    a32 = np.ones(3, np.float32)
    assert (a32 + 1.0).dtype == np.float32
    assert (a32 + np.float64(1.0)).dtype == np.float64  # a 0-d array is strong


def test_integer_overflow_wraps_but_only_scalars_warn():
    """Arrays wrap silently; scalar arithmetic also warns.  NEP 50, note 02 §2.

    This asymmetry is the corrected form of the claim; the note used to say
    overflow was silent everywhere.
    """
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        arr = np.array([127], np.int8) + np.int8(1)
    assert arr[0] == -128
    assert not caught, "array overflow is documented as silent"

    with pytest.warns(RuntimeWarning, match="overflow encountered"):
        assert np.int8(127) + np.int8(1) == -128


def test_inplace_true_divide_on_int_array_is_an_error():
    """`arr /= 2` cannot cast float64 back into int64.  Note 02 §2.

    https://numpy.org/doc/2.5/reference/ufuncs.html#casting-rules
    """
    ints = np.array([1, 2, 3])
    with pytest.raises(TypeError) as info:
        ints /= 2
    assert type(info.value).__name__ == "UFuncTypeError"   # a TypeError subclass
    assert "same_kind" in str(info.value)
    assert (np.array([1, 2, 3]) / 2).dtype == np.float64


def test_memory_layout_strides_views_and_copies():
    """Row-major strides, int64 default, and which operations copy.

    https://numpy.org/doc/2.5/reference/arrays.ndarray.html
    https://numpy.org/doc/2.5/user/basics.copies.html   (note 02 §1–3, exam Q1–2)
    """
    assert np.zeros((4, 6)).strides == (48, 8)
    assert np.zeros((4, 6), order="F").strides == (8, 32)
    assert np.array([1]).dtype == np.int64

    a = np.arange(12).reshape(3, 4)
    assert np.shares_memory(a, a[::2])          # basic slicing is a view
    assert not np.shares_memory(a, a[[0, 2]])   # fancy indexing copies
    assert not np.shares_memory(a, a.T.reshape(-1))   # cannot be one stride/axis


def test_broadcasting_rule_and_the_classic_failure():
    """Right-align, pad with 1s, extents equal or 1.  Note 02 §4.

    https://numpy.org/doc/2.5/user/basics.broadcasting.html
    """
    assert np.broadcast_shapes((5, 1, 3), (4, 1)) == (5, 4, 3)
    assert np.broadcast_shapes((3, 1, 4), (2, 1)) == (3, 2, 4)
    assert np.broadcast_shapes((4, 1), (4,)) == (4, 4)  # accidental outer product
    with pytest.raises(ValueError):
        np.broadcast_shapes((3,), (4,))


def test_fancy_index_augmented_assignment_does_not_accumulate():
    """`b[[0, 0, 2]] += 1` adds 1 once per slot; np.add.at accumulates.

    https://numpy.org/doc/2.5/user/basics.indexing.html  (note 02 §5, exam Q4)
    """
    b = np.zeros(3, int)
    b[[0, 0, 2]] += 1
    assert b.tolist() == [1, 0, 1]

    c = np.zeros(3, int)
    np.add.at(c, [0, 0, 2], 1)
    assert c.tolist() == [2, 0, 1]


def test_pairwise_summation_differs_from_sequential():
    """np.sum is pairwise, so it is not bit-identical to a running sum.  Note
    02 §6.  https://numpy.org/doc/2.5/reference/generated/numpy.sum.html
    """
    rng = np.random.default_rng(0)
    x = rng.random(100_000)
    assert x.sum() != float(np.cumsum(x)[-1])       # differ in the last bits
    assert x.sum() == pytest.approx(np.cumsum(x)[-1], rel=1e-12)


def test_generator_spawn_gives_independent_streams():
    """SeedSequence.spawn is the documented way to seed parallel workers.  Notes
    02 §9 and 08 §4.  https://numpy.org/doc/2.5/reference/random/parallel.html
    """
    children = np.random.default_rng(2026).spawn(2)
    a, b = (np.random.default_rng(c).random(5) for c in children)
    assert not np.allclose(a, b)


# --------------------------------------------------------------------- SciPy
def test_interp1d_is_legacy_but_still_works():
    """SciPy marks interp1d legacy: "will no longer receive updates" — but emits
    no warning in 1.18, which is why note 03 §interpolate has to say so in prose.
    docs.scipy.org/doc/scipy-1.18.0/reference/generated/scipy.interpolate.interp1d.html
    """
    from scipy import interpolate

    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        f = interpolate.interp1d([0.0, 1.0, 2.0], [0.0, 1.0, 4.0])
    assert not caught
    assert f(0.5) == pytest.approx(0.5)
    assert "legacy" in interpolate.interp1d.__doc__.lower()


def test_scipy_numbers_quoted_in_note_03():
    """quad of exp(-x^2) is sqrt(pi); norm.ppf(0.95)=1.6449; N(2,.5).ppf(.975)=2.98.

    Note 03 §integrate and §stats, and the exam questions that quote them.
    """
    from scipy import integrate, stats

    value, err = integrate.quad(lambda x: np.exp(-x * x), -np.inf, np.inf)
    assert value == pytest.approx(np.sqrt(np.pi), abs=1e-10)
    assert err < 1e-7
    assert float(stats.norm.ppf(0.95)) == pytest.approx(1.6449, abs=5e-5)
    assert float(stats.norm(2, 0.5).ppf(0.975)) == pytest.approx(2.98, abs=5e-3)


# -------------------------------------------------------------------- pandas
def test_pandas3_chained_assignment_and_settingwithcopywarning():
    """pandas 3.0 removed SettingWithCopyWarning; CoW makes the subset a copy.

    https://pandas.pydata.org/pandas-docs/version/3.0/whatsnew/v3.0.0.html
    (note 04 §7 and its exam Q5 — this is the biggest correction of the pass)
    """
    import pandas as pd

    assert not hasattr(pd.errors, "SettingWithCopyWarning")
    assert hasattr(pd.errors, "ChainedAssignmentError")

    df = pd.DataFrame({"x": [1, -1, 2], "y": [0, 0, 0]})
    with pytest.warns(pd.errors.ChainedAssignmentError):
        df[df.x > 0]["y"] = 1
    assert df.y.tolist() == [0, 0, 0]

    df.loc[df.x > 0, "y"] = 1          # the correct form
    assert df.y.tolist() == [1, 0, 1]


def test_pandas3_str_dtype_and_the_ddof_mismatch():
    """PDEP-14 `str` dtype, and pandas std ddof=1 vs numpy ddof=0.  Notes 02 §6,
    04 §7.  https://pandas.pydata.org/pandas-docs/version/3.0/user_guide/text.html
    """
    import pandas as pd

    assert pd.Series(["a", "b"]).dtype == "str"
    assert pd.Series([1.0, 2.0, 3.0]).std() == pytest.approx(1.0)
    assert np.std([1.0, 2.0, 3.0]) == pytest.approx(0.816496580927726)


# ---------------------------------------------------------------- matplotlib
def test_both_constrained_layout_spellings_work():
    """`layout="constrained"` is current; `constrained_layout=True` still works.
    Note 04 §1, §3.  matplotlib.org/3.11.2/users/explain/axes/constrainedlayout_guide.html
    """
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    for kwargs in ({"layout": "constrained"}, {"constrained_layout": True}):
        fig, _ = plt.subplots(**kwargs)
        plt.close(fig)
    assert matplotlib.rcParams["figure.max_open_warning"] == 20
    assert matplotlib.rcParams["image.cmap"] == "viridis"


# ------------------------------------------------------------- numpy.testing
def test_assert_allclose_defaults():
    """rtol=1e-7, atol=0, so comparing against zero needs an explicit atol.
    Note 05 §5 and exam Q2.  numpy.org/doc/2.5/reference/generated/numpy.testing.assert_allclose.html
    """
    import inspect

    params = inspect.signature(np.testing.assert_allclose).parameters
    assert (params["rtol"].default, params["atol"].default) == (1e-7, 0)
    with pytest.raises(AssertionError):
        np.testing.assert_allclose(np.array([1e-12]), np.zeros(1))
    np.testing.assert_allclose(np.array([1e-12]), np.zeros(1), atol=1e-10)


# ----------------------------------------------------------------------- PuLP
def test_pulp4_removed_what_3_3_deprecated():
    """PuLP 4.0 turned note 07 §7's three DeprecationWarnings into errors and
    dropped the bundled CBC.  Installed wheel's README (PuLP 4.0.0 METADATA);
    https://coin-or.github.io/pulp/guides/how_to_migrate_to_v4.html  [S23]
    """
    pulp = pytest.importorskip("pulp")
    with pytest.raises(TypeError):
        pulp.LpVariable("legacy", lowBound=0)
    assert not hasattr(pulp, "PULP_CBC_CMD") and not hasattr(pulp, "LpStatus")
    prob = pulp.LpProblem("t", pulp.LpMaximize)
    x = prob.add_variable("x", lowBound=0)      # the 3.3 replacement still works
    prob += x, "obj"
    prob += x <= 1, "cap"
    assert isinstance(prob.constraints(), list)  # a method returning a list now
    with pytest.raises(TypeError):
        _ = prob.constraints["cap"]
    assert prob.get_constraint_by_name("cap") is not None
    assert not hasattr(prob, "status")          # solve() returns LpSolveStats
    if not pulp.listSolvers(onlyAvailable=True):     # this venv: no CBC, no HiGHS
        with pytest.raises(pulp.PulpError, match="No solver available"):
            prob.solve()


def test_pulp_production_plan_matches_the_worked_example():
    """Note 07 §7's worked LP: (20, 60), profit 2600, duals 10, 20 and 0."""
    pytest.importorskip("pulp")
    r = optimisation.production_plan_lp()
    assert r["status"] == "Optimal"
    assert (r["P1"], r["P2"], r["profit"]) == pytest.approx((20.0, 60.0, 2600.0))
    assert r["duals"] == pytest.approx({"machine": 10.0, "labour": 20.0, "demand": 0.0})  # demand slack


# ------------------------------------------------------------------- CPython
def test_default_start_method_is_spawn_on_macos():
    """Note 08 §2: spawn on macOS/Windows, so workers must be importable.
    https://docs.python.org/3.12/library/multiprocessing.html
    """
    expected = "spawn" if sys.platform in ("darwin", "win32") else "fork"
    assert mp.get_start_method() == expected


def test_amdahl_and_gustafson_numbers_quoted_in_note_08():
    """Amdahl 1967 (doi:10.1145/1465482.1465560), Gustafson 1988
    (doi:10.1145/42411.42415).  Note 08 §7 quotes these figures."""
    assert parallel.amdahl_speedup(0.9, 4) == pytest.approx(3.0769, abs=1e-4)
    assert parallel.amdahl_speedup(0.9, 8) == pytest.approx(4.7059, abs=1e-4)
    assert parallel.amdahl_speedup(0.8, 10**9) == pytest.approx(5.0, abs=1e-6)
    assert parallel.gustafson_speedup(0.9, 8) == pytest.approx(0.1 + 0.9 * 8)


def test_identity_comparison_is_not_a_value_test():
    """Note 01, pitfall 4.  Constant sharing, not just small-int caching: equal
    constants in one code object are shared, so `a = 257; b = 257` gives
    `a is b` although 257 is outside CPython's -5..256 cache.  None of it is
    guaranteed, which is why 3.12 warns about `is` on an int literal.
    """
    a = 257
    b = 257
    assert a is b                    # same code object -> shared constant
    assert int("257") is not a       # built at run time -> a different object
    assert int("257") == a           # ... but equal, which is what you meant
