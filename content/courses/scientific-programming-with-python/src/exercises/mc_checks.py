"""Executable half of the MC bank (note 11 §2): one ``_chk_*`` per item.

Each function *runs* the behaviour in the repo venv (``../../refs/SOURCES.md``
S40) and derives the letter of the correct answer with ``pick``/``pick_true``,
which insist that exactly one of the four options matches.  Nothing here returns
a literal answer.  Imports are local to each check so that the ``spawn`` child
processes of P1-P3 re-import this module cheaply.
"""
from __future__ import annotations

import numpy as np

from mc_bank import pick, pick_true, raises

# Module-level state for the process/thread item P3.  Under 'spawn' the child
# re-imports this module, so it starts its own copy at zero -- which is the point.
_COUNTER = [0]


def _bump(n: int) -> int:
    """Worker for P3: mutates a module global and reports the new value."""
    _COUNTER[0] += n
    return _COUNTER[0]


def _raises_ctx(exc: type[BaseException], fn) -> bool:
    """True if ``pytest.raises(exc)`` would accept what ``fn`` does."""
    import pytest

    try:
        with pytest.raises(exc):
            fn()
    except BaseException:
        return False
    return True

# ------------------------------------------------------- 1. the language
def _chk_tuple_augmented() -> str:
    t, exc = (1, [2]), None
    try:
        t[1] += [3]
    except BaseException as e:                  # noqa: BLE001 - the item is about it
        exc = type(e).__name__
    return pick_true(
        a=lambda: exc is None and t == (1, [2, 3]),
        b=lambda: exc == "TypeError" and t == (1, [2]),
        c=lambda: exc == "TypeError" and t == (1, [2, 3]),
        d=lambda: exc == "AttributeError" and t == (1, [2]),
    )


def _chk_mutable_default() -> str:
    def collect(x, seen=[]):                    # noqa: B006 - the item is about it
        seen.append(x)
        return seen

    collect(1)
    return pick(collect(2), a=[2], b=[1, 2], c=[1], d=[2, 1])


def _chk_late_binding() -> str:
    fs = [lambda: i for i in range(3)]
    return pick([f() for f in fs],
                a=[0, 1, 2], b=[2, 2, 2], c=[0, 0, 0], d=[3, 3, 3])

# ------------------------------------------------- 2. the NumPy/SciPy stack
def _chk_arange_vs_linspace() -> str:
    got = (np.arange(0, 1, 0.25).size, np.linspace(0, 1, 5).size)
    return pick(got, a=(4, 5), b=(5, 5), c=(4, 4), d=(5, 4))


def _chk_sort_axis() -> str:
    a = np.array([[3, 1], [2, 4]])
    return pick(np.sort(a).tolist(),
                a=[[1, 3], [2, 4]], b=[[2, 1], [3, 4]],
                c=[1, 2, 3, 4], d=[[3, 1], [2, 4]])


def _chk_solve_ivp_shape() -> str:
    from scipy.integrate import solve_ivp

    sol = solve_ivp(lambda t, y: [y[1], -y[0]], (0.0, 1.0), [0.0, 1.0],
                    t_eval=np.linspace(0.0, 1.0, 7))
    return pick(sol.y.shape, a=(7, 2), b=(2, 7), c=(7,), d=(2,))

# ------------------------------------------------ 3. data and plotting
def _agg_axes():
    """Matplotlib with the headless backend, as the tests need it."""
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    return plt


def _chk_subplots_shape() -> str:
    plt = _agg_axes()
    fig, ax = plt.subplots(1, 3)
    shape = np.shape(ax)
    plt.close(fig)
    return pick(shape, a=(1, 3), b=(3,), c=(), d=(3, 1))


def _chk_plot_return() -> str:
    from matplotlib.lines import Line2D

    plt = _agg_axes()
    fig, ax = plt.subplots()
    out = ax.plot([0, 1], [0, 1])
    plt.close(fig)
    one_line = isinstance(out, list) and len(out) == 1 and isinstance(out[0], Line2D)
    return pick_true(a=lambda: one_line, b=lambda: isinstance(out, Line2D),
                     c=lambda: out is None, d=lambda: hasattr(out, "plot"))


def _chk_groupby_transform() -> str:
    import pandas as pd

    df = pd.DataFrame({"k": ["a", "a", "b"], "v": [1.0, 2.0, 3.0]})
    return pick(len(df.groupby("k")["v"].transform("mean")), a=2, b=3, c=1, d=6)

# -------------------------------------------------------- 4. code testing
def _chk_approx_which_passes() -> str:
    import pytest

    return pick_true(
        a=lambda: 0.1 + 0.2 == 0.3,
        b=lambda: 0.1 + 0.2 == pytest.approx(0.3),
        c=lambda: 1.0 == pytest.approx(1.0 + 1e-5),
        d=lambda: 1e-10 == pytest.approx(0),
    )


def _chk_approx_against_zero() -> str:
    import pytest

    x = 1e-10
    return pick_true(
        a=lambda: x == pytest.approx(0),
        b=lambda: x == pytest.approx(0, abs=1e-9),
        c=lambda: x == pytest.approx(0, rel=1e-9),
        d=lambda: x == pytest.approx(0.0),
    )


def _chk_raises_subclass() -> str:
    def boom(exc):
        raise exc

    return pick_true(
        a=lambda: _raises_ctx(LookupError, lambda: boom(KeyError("k"))),
        b=lambda: _raises_ctx(LookupError, lambda: boom(ValueError("v"))),
        c=lambda: _raises_ctx(LookupError, lambda: None),
        d=lambda: _raises_ctx(LookupError, lambda: boom(SystemExit(1))),
    )

# ------------------------------------------------- 5. IPython and Jupyter
def _cell_magics() -> set[str]:
    from IPython.core.interactiveshell import InteractiveShell

    return set(InteractiveShell.instance().magics_manager.lsmagic()["cell"])


def _chk_cell_magic() -> str:
    cell = _cell_magics()
    return pick_true(a=lambda: "timeit" in cell, b=lambda: "run" in cell,
                     c=lambda: "matplotlib" in cell, d=lambda: "load_ext" in cell)


def _chk_nbformat_keys() -> str:
    import nbformat

    only_code = set(nbformat.v4.new_code_cell("x = 1")) - set(
        nbformat.v4.new_markdown_cell("x"))
    return pick_true(a=lambda: "source" in only_code, b=lambda: "metadata" in only_code,
                     c=lambda: "outputs" in only_code, d=lambda: "id" in only_code)


def _chk_nbconvert_targets() -> str:
    from nbconvert.exporters import get_export_names

    names = set(get_export_names())
    return pick_true(a=lambda: "script" not in names, b=lambda: "html" not in names,
                     c=lambda: "pdf" not in names, d=lambda: "dataframe" not in names)

# ---------------------------------------------------------- 6. optimisation
def _chk_minimize_needs_jac() -> str:
    from scipy.optimize import minimize, rosen

    def run(method):  # True if the method refuses to start without a gradient
        return raises(ValueError,
                      lambda: minimize(rosen, np.array([0.5, 0.5]), method=method))

    return pick_true(a=lambda: run("Nelder-Mead"), b=lambda: run("Powell"),
                     c=lambda: run("BFGS"), d=lambda: run("Newton-CG"))


def _chk_slsqp_ineq_sign() -> str:
    from scipy.optimize import minimize

    r = minimize(lambda x: x[0], np.array([5.0]), method="SLSQP",
                 constraints=[{"type": "ineq", "fun": lambda x: x[0] - 2.0}])
    x, ok = float(r.x[0]), bool(r.success)
    return pick_true(a=lambda: ok and abs(x - 2.0) < 1e-6,
                     b=lambda: ok and abs(x + 2.0) < 1e-6,
                     c=lambda: ok and abs(x) < 1e-6, d=lambda: not ok)


def _chk_linprog_minimises() -> str:
    from scipy.optimize import linprog

    r = linprog(c=[-1.0], A_ub=[[1.0]], b_ub=[1.0], bounds=[(0, None)])
    x, ok = float(r.x[0]), r.status == 0
    return pick_true(a=lambda: ok and abs(x) < 1e-9, b=lambda: ok and abs(x - 1) < 1e-9,
                     c=lambda: ok and abs(x + 1) < 1e-9, d=lambda: not ok)

# ------------------------------------------------------ 7. parallel processing
def _chk_map_vs_imap() -> str:
    import multiprocessing as mp

    with mp.Pool(2) as p:
        m, i = p.map(abs, [-1, -2]), p.imap(abs, [-1, -2])
        ml, il = isinstance(m, list), isinstance(i, list)
        list(i)
    return pick_true(a=lambda: ml and il, b=lambda: ml and not il,
                     c=lambda: not ml and not il, d=lambda: not ml and il)


def _chk_lambda_is_unpicklable() -> str:
    import multiprocessing as mp

    name, msg = None, ""
    with mp.Pool(2) as p:
        try:
            p.map(lambda x: 2 * x, [1, 2])
        except BaseException as e:              # noqa: BLE001 - the item is about it
            name, msg = type(e).__name__, str(e).lower()
    # PicklingError for a module-level lambda, AttributeError ("can't get local
    # object") for one defined inside a function; both are the same refusal.
    return pick_true(
        a=lambda: name is None,
        b=lambda: name is not None and ("pickle" in msg or "local object" in msg),
        c=lambda: name == "TypeError" and "pickle" not in msg,
        d=lambda: name == "RecursionError")


def _chk_processes_do_not_share_globals() -> str:
    import multiprocessing as mp
    from concurrent.futures import ThreadPoolExecutor

    _COUNTER[0] = 0
    with mp.Pool(2) as p:
        p.map(_bump, [1, 1])
    after_processes = _COUNTER[0]
    _COUNTER[0] = 0
    with ThreadPoolExecutor(2) as ex:
        list(ex.map(_bump, [1, 1]))
    after_threads = _COUNTER[0]
    return pick_true(a=lambda: after_processes == 2,
                     b=lambda: after_processes == 0 and after_threads == 2,
                     c=lambda: after_processes == 1,
                     d=lambda: after_processes == 2 and after_threads == 0)

# ------------------------------------------------------------- 8. interfaces
def _chk_ctypes_needs_restype() -> str:
    import ctypes
    import ctypes.util

    lib = ctypes.CDLL(ctypes.util.find_library("m") or None)
    try:  # no argtypes/restype: ctypes guesses a C int return
        got, exc = lib.sqrt(ctypes.c_double(4.0)), None
    except BaseException as e:                  # noqa: BLE001 - the item is about it
        got, exc = None, type(e).__name__
    return pick_true(a=lambda: got == 2.0, b=lambda: isinstance(got, int),
                     c=lambda: exc == "TypeError", d=lambda: got == 4.0)


def _chk_transpose_is_fortran_ordered() -> str:
    t = np.ones((2, 3)).T
    c, f = bool(t.flags["C_CONTIGUOUS"]), bool(t.flags["F_CONTIGUOUS"])
    return pick_true(a=lambda: c and not f, b=lambda: f and not c,
                     c=lambda: not c and not f, d=lambda: c and f)


def _chk_subprocess_returns_bytes() -> str:
    import subprocess
    import sys

    out = subprocess.run([sys.executable, "-c", "print('hi')"],
                         capture_output=True, check=True).stdout
    return pick(type(out).__name__,
                a="str", b="bytes", c="NoneType", d="TextIOWrapper")


if __name__ == "__main__":      # demo; import self so workers pickle mc_checks._bump
    for name, fn in sorted(vars(__import__("mc_checks")).items()):
        if name.startswith("_chk_"):
            print(f"{name[5:]:34s} -> ({fn()})")
