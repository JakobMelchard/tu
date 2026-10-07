"""The 24 multiple-choice items of note 11 §2.  **Ours**, not adapted from any course.

No past paper for 191.125, this lecturer, or the predecessor number 191.116 is
public (``../../refs/SOURCES.md`` S1-S9), so nothing here is "what was asked".
See ``mc_bank.py`` for the format and ``mc_checks.py`` for the code that decides
each answer by executing it.  Three items per TISS subject item.
"""
from __future__ import annotations

from mc_bank import Item
from mc_checks import (
    _chk_approx_against_zero, _chk_approx_which_passes, _chk_arange_vs_linspace,
    _chk_cell_magic, _chk_ctypes_needs_restype, _chk_groupby_transform,
    _chk_lambda_is_unpicklable, _chk_late_binding, _chk_linprog_minimises,
    _chk_map_vs_imap, _chk_minimize_needs_jac, _chk_mutable_default,
    _chk_nbconvert_targets, _chk_nbformat_keys, _chk_plot_return,
    _chk_processes_do_not_share_globals, _chk_raises_subclass, _chk_slsqp_ineq_sign,
    _chk_solve_ivp_shape, _chk_sort_axis, _chk_subplots_shape,
    _chk_subprocess_returns_bytes, _chk_transpose_is_fortran_ordered,
    _chk_tuple_augmented,
)

ITEMS: tuple[Item, ...] = (
    Item("L1", "language",
         "def collect(x, seen=[]): seen.append(x); return seen.  After "
         "collect(1), what does collect(2) return?",
         ("[2]", "[1, 2]", "[1]", "[2, 1]"), "b",
         "The default list is built once, when the def executes, and is shared "
         "by every call that does not pass `seen`.  Use `seen=None`.",
         _chk_mutable_default),
    Item("L2", "language",
         "fs = [lambda: i for i in range(3)]; [f() for f in fs] is",
         ("[0, 1, 2]", "[2, 2, 2]", "[0, 0, 0]", "[3, 3, 3]"), "b",
         "Closures capture the variable, not its value; all three read `i` "
         "after the loop.  Bind it with a default argument: `lambda i=i: i`.",
         _chk_late_binding),
    Item("L3", "language",
         "t = (1, [2]); t[1] += [3].  What happens?",
         ("it succeeds and t == (1, [2, 3])",
          "TypeError, and t == (1, [2])",
          "TypeError, but t == (1, [2, 3])",
          "AttributeError, and t == (1, [2])"), "c",
         "`+=` on a list calls list.__iadd__, which mutates in place and "
         "succeeds; the *store back* into the tuple is what raises.  Both halves "
         "happen, in that order.",
         _chk_tuple_augmented),

    Item("N1", "numpy-scipy",
         "np.arange(0, 1, 0.25).size and np.linspace(0, 1, 5).size are",
         ("(4, 5)", "(5, 5)", "(4, 4)", "(5, 4)"), "a",
         "arange takes a step and excludes the stop; linspace takes a number of "
         "points and includes both endpoints.",
         _chk_arange_vs_linspace),
    Item("N2", "numpy-scipy",
         "A = np.array([[3, 1], [2, 4]]).  np.sort(A).tolist() is",
         ("[[1, 3], [2, 4]]", "[[2, 1], [3, 4]]", "[1, 2, 3, 4]",
          "[[3, 1], [2, 4]]"), "a",
         "np.sort defaults to axis=-1, i.e. each row independently.  axis=0 "
         "gives (b) and axis=None flattens, giving (c).",
         _chk_sort_axis),
    Item("N3", "numpy-scipy",
         "sol = solve_ivp(f, (0, 1), y0) with 2 states and t_eval of 7 points.  "
         "sol.y.shape is",
         ("(7, 2)", "(2, 7)", "(7,)", "(2,)"), "b",
         "solve_ivp returns states down the rows and time across the columns: "
         "sol.y[i] is the whole trajectory of state i.  Plot sol.t against "
         "sol.y[0], not sol.y[:, 0].",
         _chk_solve_ivp_shape),

    Item("D1", "data-plotting",
         "fig, ax = plt.subplots(1, 3).  np.shape(ax) is",
         ("(1, 3)", "(3,)", "() - ax is a single Axes", "(3, 1)"), "b",
         "subplots squeezes length-1 axes out of the returned array, so a "
         "single row comes back 1-D.  Pass squeeze=False to always get (1, 3).",
         _chk_subplots_shape),
    Item("D2", "data-plotting",
         "df has 3 rows in 2 groups.  len(df.groupby('k')['v'].transform('mean')) is",
         ("2", "3", "1", "6"), "b",
         "transform broadcasts the per-group value back onto every original "
         "row, so it is len(df).  .mean() aggregates instead and gives 2.",
         _chk_groupby_transform),
    Item("D3", "data-plotting",
         "ax.plot(x, y) returns",
         ("a list of Line2D", "a Line2D", "None", "the Axes, for chaining"), "a",
         "One call can draw several lines, so plot always returns a list.  "
         "Unpack it: `line, = ax.plot(x, y)`.",
         _chk_plot_return),

    Item("T1", "testing",
         "Which assertion passes?",
         ("assert 0.1 + 0.2 == 0.3",
          "assert 0.1 + 0.2 == pytest.approx(0.3)",
          "assert 1.0 == pytest.approx(1.0 + 1e-5)",
          "assert 1e-10 == pytest.approx(0)"), "b",
         "approx defaults to rel=1e-6: 1e-5 relative is outside it, and against "
         "an expected 0 the relative part vanishes so only abs=1e-12 is left.",
         _chk_approx_which_passes),
    Item("T2", "testing",
         "x is 1e-10.  Which comparison expresses 'x is zero to within 1e-9'?",
         ("x == pytest.approx(0)", "x == pytest.approx(0, abs=1e-9)",
          "x == pytest.approx(0, rel=1e-9)", "x == pytest.approx(0.0)"), "b",
         "A relative tolerance around 0 is 0, so approx falls back to its "
         "abs=1e-12 default.  Comparing against zero always needs an explicit "
         "abs - the same trap as numpy.testing.assert_allclose's atol=0.",
         _chk_approx_against_zero),
    Item("T3", "testing",
         "with pytest.raises(LookupError): ...  Which body makes the test pass?",
         ("raise KeyError('k')", "raise ValueError('v')", "return normally",
          "raise SystemExit(1)"), "a",
         "pytest.raises matches subclasses, and KeyError subclasses LookupError. "
         "A body that does not raise fails with Failed: DID NOT RAISE.",
         _chk_raises_subclass),

    Item("J1", "jupyter",
         "Which of these also exists as a cell magic (%%...), not only a line magic?",
         ("%%timeit", "%%run", "%%matplotlib", "%%load_ext"), "a",
         "%timeit times one line; %%timeit times the whole cell, with the "
         "first line available as setup.  The other three are line-only.",
         _chk_cell_magic),
    Item("J2", "jupyter",
         "In nbformat 4, which key does a code cell have that a markdown cell "
         "does not?",
         ("source", "metadata", "outputs", "id"), "c",
         "Code cells carry `outputs` and `execution_count`; both cell types "
         "carry source, metadata and id.  'Clear all outputs before committing' "
         "is exactly about that key.",
         _chk_nbformat_keys),
    Item("J3", "jupyter",
         "Which is NOT a valid `jupyter nbconvert --to` target?",
         ("script", "html", "pdf", "dataframe"), "d",
         "nbconvert exports documents and scripts, not data structures.  "
         "`--to script` is the one that turns a notebook into a .py file.",
         _chk_nbconvert_targets),

    Item("O1", "optimisation",
         "Which scipy.optimize.minimize method raises unless you pass `jac`?",
         ("Nelder-Mead", "Powell", "BFGS", "Newton-CG"), "d",
         "Nelder-Mead and Powell are derivative-free; BFGS and CG fall back to "
         "a finite-difference gradient; Newton-CG refuses, because it needs a "
         "gradient to form Hessian-vector products.",
         _chk_minimize_needs_jac),
    Item("O2", "optimisation",
         "minimize(lambda x: x[0], [5.0], method='SLSQP', constraints=["
         "{'type': 'ineq', 'fun': lambda x: x[0] - 2}]) gives",
         ("x = 2", "x = -2", "x = 0", "failure: the problem is unbounded"), "a",
         "SciPy's `ineq` means fun(x) >= 0, so the constraint reads x - 2 >= 0. "
         "Writing 2 - x would have driven x the other way.",
         _chk_slsqp_ineq_sign),
    Item("O3", "optimisation",
         "linprog(c=[-1.0], A_ub=[[1.0]], b_ub=[1.0], bounds=[(0, None)]).x is",
         ("[0.]", "[1.]", "[-1.]", "the solver reports infeasible"), "b",
         "linprog always minimises c @ x, so maximising x is encoded by "
         "c = -1; the bound x <= 1 then binds.  res.fun is -1, not 1.",
         _chk_linprog_minimises),

    Item("P1", "parallel",
         "With p = mp.Pool(2): what do p.map(f, xs) and p.imap(f, xs) return?",
         ("both a list", "map a list, imap an iterator",
          "both an iterator", "map an iterator, imap a list"), "b",
         "map blocks and materialises everything; imap returns lazily in order "
         "(imap_unordered as results arrive), which is what you want for a long "
         "job with a progress bar.",
         _chk_map_vs_imap),
    Item("P2", "parallel",
         "with mp.Pool(2) as p: p.map(lambda x: 2 * x, [1, 2])",
         ("returns [2, 4]", "raises: the lambda cannot be pickled",
          "raises TypeError: 'function' is not iterable", "raises RecursionError"),
         "b",
         "Tasks are pickled to reach the worker, and a lambda has no importable "
         "qualified name.  Workers must be module-level functions - the same "
         "constraint that forces `if __name__ == '__main__':` under spawn.",
         _chk_lambda_is_unpicklable),
    Item("P3", "parallel",
         "A module global _COUNTER = [0]; the worker does _COUNTER[0] += 1.  "
         "After Pool(2).map(worker, [1, 1]), the parent's _COUNTER[0] is",
         ("2", "0 (and 2 with a ThreadPoolExecutor instead)", "1",
          "2, and 0 with a ThreadPoolExecutor instead"), "b",
         "Processes get their own address space, so the parent never sees the "
         "mutation; threads share one.  This is the whole reason the GIL "
         "discussion exists - and why shared_memory has to be explicit.",
         _chk_processes_do_not_share_globals),

    Item("I1", "interfaces",
         "libm = ctypes.CDLL(find_library('m')); libm.sqrt(c_double(4.0)) with no "
         "argtypes/restype declared returns",
         ("2.0", "some integer", "raises TypeError", "4.0"), "b",
         "ctypes assumes a C `int` return when restype is not set, so the "
         "double comes back reinterpreted.  Always declare argtypes and restype; "
         "the failure is silent, not an exception.",
         _chk_ctypes_needs_restype),
    Item("I2", "interfaces",
         "a = np.ones((2, 3)) is C-contiguous.  a.T is",
         ("C-contiguous", "F-contiguous (column-major)", "neither", "both"), "b",
         "Transposing only swaps the strides, so the same buffer is now "
         "column-major.  That is the cheap way to hand an array to Fortran, "
         "Julia or LAPACK without copying.",
         _chk_transpose_is_fortran_ordered),
    Item("I3", "interfaces",
         "subprocess.run([...], capture_output=True).stdout has type",
         ("str", "bytes", "NoneType", "TextIOWrapper"), "b",
         "Without text=True (or encoding=...), subprocess hands back raw bytes. "
         "Decoding is yours to do - or pass text=True.",
         _chk_subprocess_returns_bytes),
)


if __name__ == "__main__":      # demo: re-derive every answer, one line per item
    for item in ITEMS:
        print(f"{item.id} [{item.topic:13s}] recorded ({item.answer}), executed ({item.verify()})")
    print(len(ITEMS), "items, all agree with execution")
