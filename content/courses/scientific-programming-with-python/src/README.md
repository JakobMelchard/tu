# Reference implementations

One Python module per note (`../notes`), each with a docstring naming its note, runnable as a script with a small demo, and covered by `test_<module>.py`. A C shared library (with its own C test) for the interfaces note and a Jupyter notebook (executed by a pytest test) for the reproducibility note.

```
src/
  py/
    python_basics.py      note 01  data model, generators, closures, decorators, classes, exceptions, context managers
    numpy_tour.py         note 02  strides, views/copies, broadcasting rule, fancy indexing, ufuncs, einsum, linalg, Generator
    scipy_tour.py         note 03  integrate, optimize, interpolate, sparse, linalg, fft, stats, signal
    plotting.py           note 04  figure/axes model, subplots, images, 3D, pandas groupby/pivot (PNGs go to a temp dir)
    testing_examples.py   note 05  code under test; test_testing_examples.py shows fixtures, parametrize, raises, approx, numpy.testing
    optimisation.py       note 07  minimize methods, constraints, least_squares, root, linprog; PuLP 4 LP and ILP,
                                   solved by PuLP's solver if any, else SciPy's HiGHS (solve_pulp)
    parallel.py           note 08  Monte Carlo pi: serial / threads / Pool / futures with speedup, shared memory, Amdahl
    interfaces.py         note 09  ctypes and cffi into ../c/libvecops, subprocess; f2py/pybind11/Julia as docstrings
    profiling.py          note 10  timeit, cProfile/pstats, section timer, tracemalloc, temporaries
    test_*.py             pytest tests for each module
    test_doc_examples.py  executable source verification: one test per version-sensitive
                          claim in ../notes, with the doc URL in each docstring
  exercises/              note 11  substitute practice material, NOT this course's,
                          provenance and licence on every directory (see its README.md)
    mc_bank.py            the Item type and the pick/pick_true guard rails
    mc_checks.py          one function per question, each RUNS the behaviour (demo: prints every letter)
    mc_items.py           the 24 multiple-choice questions; ours (demo: re-derives every answer)
    test_mc_bank.py       runs all 24 against the installed libraries
    aalto-python-for-scicomp-2025/     [S41] CC BY 4.0: numpy, pandas, scipy, Pool
    scientific-python-lectures-2024/   [S39] CC BY 4.0: optimisation, interfacing with C
    software-carpentry-python-2026/    [S42] CC BY 4.0: the language, defensive programming
  c/
    vecops.h, vecops.c    libvecops.dylib (cc = Apple clang, arm64; .so on Linux): vec_dot, vec_axpy, vec_norm2, count_primes
    test_vecops.c         C-side test, linked against the library; `make test`
    Makefile              `make`, `make test`, `make clean`
  notebooks/
    tour.ipynb            magics, seeds, inline plotting, environment record (note 06)
    test_tour.py          executes tour.ipynb with nbclient; no error output, in-order execution counts
```

## Build, run, test

From this course folder, using the repo venv (`uv sync` at the repo root, which holds `pyproject.toml`):

```bash
make -C src/c test             # build libvecops.dylib, run the C test
uv run pytest src -q           # py + exercises + notebook
uv run jupyter nbconvert --to notebook --execute \
    src/notebooks/tour.ipynb --output /tmp/tour_out.ipynb
```

Demos (each prints a short summary; `parallel.py` prints a speedup table and takes a few seconds):

```bash
cd src/py
for m in python_basics numpy_tour scipy_tour plotting testing_examples optimisation parallel interfaces profiling; do
    uv run python $m.py; done
```

The practice set (note 11):

```bash
cd src/exercises
uv run python mc_bank.py -a                        # the 24 MC items
uv run python mc_items.py                          # re-derive all 24 answers
uv run python mc_checks.py                         # every check, run
uv run python aalto-python-for-scicomp-2025/aalto_exercises.py
uv run python scientific-python-lectures-2024/spl_exercises.py
uv run python software-carpentry-python-2026/swc_exercises.py
```

## Versions

The notes and this code were verified on **2026-09-27** against the repo venv,
re-created that day with `uv sync`: CPython 3.12.13, NumPy 2.5.3, SciPy 1.18.1,
pandas 3.0.6, Matplotlib 3.11.2, pytest 9.1.1, **PuLP 4.0.0** (3.3.2 on
2026-09-22), IPython 9.17.1 ([`../refs/SOURCES.md`](../refs/SOURCES.md) S40).
Result: `pytest src` 186 passed, 1 xfailed (the intended strict xfail in
`test_testing_examples.py`), 0 skipped; `make -C c test` 6/6.

`test_doc_examples.py` is what keeps that honest. It asserts the recorded
major.minor of each package and then re-derives every behaviour the notes depend
on that a library upgrade could change: NEP 50 weak scalars and the
scalar-overflow warning, `interp1d`'s legacy status, pandas 3's removal of
`SettingWithCopyWarning`, the `str` dtype, the PuLP 4.0 removals, the
`ddof` mismatch, `assert_allclose` defaults, the default multiprocessing start
method, and the Amdahl/Gustafson figures note 08 quotes. Each test names its
source URL. **If it fails after an upgrade, the notes are what need fixing.**

`exercises/test_mc_bank.py` extends the same idea to note 11's exam questions:
each of the 24 multiple-choice items derives its correct answer by *executing*
the behaviour, and the `pick`/`pick_true` helpers require exactly one of the
four options to match, so an item that acquires a second defensible answer
fails here rather than misleading a reader.

Notes:

- `interfaces.build_library()` runs `make` once per process (a no-op when the library is newer than `vecops.c`/`vecops.h`), so an edited kernel is never loaded stale; `test_interfaces.py` skips with a message only if there is no library and `make` fails. It also runs `make test`, and checks that cffi's `cdef`, read from `vecops.h`, exposes all four functions.
- PuLP 4.0 ships no solver and this venv has none (`pulp.listSolvers(onlyAvailable=True) == []`). `optimisation.solve_pulp` therefore uses PuLP's own solver when one is installed, and otherwise reads the model back out (`pulp_to_matrices`) and solves it with SciPy's HiGHS: `linprog` for LPs (duals converted to PuLP's sign convention), `milp` for MIPs. The PuLP tests always run; they skip only if PuLP itself is missing. See note 07 §7.
- `parallel.py` uses the `spawn` start method (macOS default): workers are top-level functions and the demo is guarded by `if __name__ == "__main__":`. Tests use 2 workers and small sample counts.
- `plotting.py` forces the `Agg` backend and writes into `tempfile.mkdtemp()`; tests use `tmp_path`.
- `exercises/` is **substitute material**: this course publishes no exercise sheet and no past paper, so the practice set is adapted from three free CC BY 4.0 courses (or is ours) with the institution, course, year and licence stated in each directory's `README.md`. Nothing is vendored and no problem statement is copied. Its multiprocessing tests use 2 workers and 200 000 samples; the whole directory runs in about three seconds.
- Not installed in the venv, therefore only described in the notes: hypothesis, pytest-cov, numba, Cython, juliacall, line_profiler, and any PuLP solver.
