# Notes: 191.125 Scientific Programming with Python (2026W)

Written for the exam (multiple choice + programming tasks, on paper) and the
exercises. Each note explains how the tool works, shows the idioms, lists
pitfalls, ends with five exam-style questions and points to the reference code in
`../src/py`.

**Read [`00-exam-focus.md`](00-exam-focus.md) first.** It says what is known
about the assessment and what is not, and why every exam-style question here is
ours rather than a past paper's.

**Practice is in [`11-practice-set.md`](11-practice-set.md).** Its 24
multiple-choice items have their correct answers *derived by executing the
library behaviour* in the repo venv, so an upgrade that invalidates one breaks
the test suite instead of you. The 16 programming problems are each tagged with
the CC BY 4.0 course they are adapted from, or marked as ours.

| # | Note | One line |
|---|---|---|
| 00 | [Exam focus](00-exam-focus.md) | What is assessed, what the six-year TISS diff shows, how to weight the ten notes |
| 01 | [Python for scientists](01-python-for-scientists.md) | Data model, mutability, comprehensions, generators, closures, decorators, classes/dataclasses, typing, exceptions, context managers, uv |
| 02 | [NumPy](02-numpy.md) | ndarray layout, dtypes, strides, views vs copies, broadcasting, fancy indexing, ufuncs, einsum, linalg, Generator, performance |
| 03 | [SciPy](03-scipy.md) | integrate, optimize, interpolate, sparse, linalg, fft, stats, signal: what each does and one example |
| 04 | [Matplotlib and data processing](04-matplotlib-and-data.md) | Figure/Axes model, publication figures, subplots, 3D, images, pandas basics |
| 05 | [Testing](05-testing.md) | pytest, assertions, fixtures, parametrize, numpy.testing, property-based idea, coverage, tests for numerical code |
| 06 | [Reproducibility and Jupyter](06-reproducibility-jupyter.md) | Kernels, magics, seeds, environment pinning, notebook hygiene, nbconvert, when not to use notebooks |
| 07 | [Optimisation](07-optimisation.md) | scipy.optimize (minimize methods, constraints, least_squares, root, linprog), PuLP 4 LP and ILP (modeller only; solved by SciPy's HiGHS when PuLP has no solver) |
| 08 | [Parallel processing](08-parallel-processing.md) | GIL, threads vs processes vs concurrent.futures, Pool.map, shared memory, chunking, Amdahl |
| 09 | [Interfaces to other languages](09-interfaces.md) | ctypes, cffi, subprocess, f2py, pybind11, Julia via juliacall / PyCall, when to drop to C |
| 10 | [Performance](10-performance.md) | timeit, cProfile, line-level thinking, memory, numba and Cython in concept |
| 11 | [Practice set](11-practice-set.md) | 24 executable multiple-choice items and 16 programming problems, from three CC BY 4.0 courses or ours, with the provenance of every one |

Changes made during the source-verification and substitute-source passes are in
`CHANGELOG.md`.

## Sources

TISS names **no literature** for this course, in any of its seven offerings, and
publishes no lecture notes; all material is in TUWEL, which needs a login
[S1]–[S8] (and see the account caveat under *Course facts*). So these notes are written against the **primary documentation of the
libraries themselves**, pinned to the version installed in the repo venv. The
register is [`../refs/SOURCES.md`](../refs/SOURCES.md); which page backs which
section is [`../refs/docs-map.md`](../refs/docs-map.md). Inline `[S<n>]` markers
throughout resolve to that register.

The one free companion text worth reading alongside is the *Scientific Python
Lectures* [S39] (CC BY 4.0), whose table of contents is almost the TISS subject
list. `../refs/fetch-sources.sh` downloads it.

Because this course publishes **no exercise sheet and no past paper**, the
practice material in note 11 is *substitute* material adapted from three free
CC BY 4.0 courses (Aalto's *Python for Scientific Computing* [S41], the
*Scientific Python Lectures* [S39] and Software Carpentry's *Programming with
Python* [S42]) plus items that are ours [S43]. **None of it is TU Wien
material**, and every item says which it is. Code and per-source licences are in
`../src/exercises/`.

## Versions these notes were verified against

Every claim below was re-run in the repo venv (`uv sync` at the repo root) on
**2026-09-27** [S40], after the venv was re-created:

| verified | CPython | NumPy | SciPy | pandas | Matplotlib | pytest | PuLP | IPython |
|---|---|---|---|---|---|---|---|---|
| 2026-09-22 | 3.12.13 | 2.5.3 | 1.18.1 | 3.0.6 | 3.11.2 | 9.1.1 | 3.3.2 | 9.17.1 |
| **2026-09-27** | 3.12.13 | 2.5.3 | 1.18.1 | 3.0.6 | 3.11.2 | 9.1.1 | **4.0.0** | 9.17.1 |

One package moved, by a major version: `pyproject.toml` lists `pulp` with no
bound and `uv.lock` is git-ignored in this repo, so the re-created venv resolved
the newest PuLP (note [06](06-reproducibility-jupyter.md) §3 draws the lesson).
Three of these versions change behaviour the notes describe, and the notes say
so where it matters: **NumPy 2** (NEP 50 weak scalars, scalar-overflow
warnings), **pandas 3** (Copy-on-Write permanent, `SettingWithCopyWarning`
removed, `str` dtype by default) and **PuLP 4.0** (the three idioms 3.3
deprecated are now errors, `LpStatus` is gone, no solver ships with the
package; note [07](07-optimisation.md) §7).
[`../src/py/test_doc_examples.py`](../src/py/test_doc_examples.py) asserts all of
them and the version set above, so a future upgrade breaks the test suite rather
than the reader. It did exactly that on 2026-09-27.

Not installed, therefore described but never demonstrated: numba, Cython,
hypothesis, pytest-cov, line_profiler, juliacall, numexpr, and **any solver
PuLP can call** (`pulp.listSolvers(onlyAvailable=True) == []`; the PuLP models
are solved by SciPy's HiGHS instead, note 07 §7).

## Course facts

State as of **2026-09-27**, from [`../docs/tiss.md`](../docs/tiss.md) [S1]
(TISS re-read that day: no field changed):

- VU, 2 ECTS, Sascha Hunold (E191).
- **Eight lectures**, Tue 11:00-13:00, HS 6 RPL, 13.10.2026 to 01.12.2026.
  Attendance required.
- **Deregistration** until 20.10.2026, one week after the first lecture.
- Grade = Part 1, the exercises, + Part 2, a written exam with multiple choice
  and programming exercises [S1]:

  | | date | time | room | registration |
  |---|---|---|---|---|
  | Exam 1 | Tue 19.01.2027 | 13:00-15:00 | HS 17 / EI 9 | 06.12.2026 to 17.01.2027 |
  | Exam 2 | Tue 23.02.2027 | 13:00-15:00 | Informatikhörsaal | 20.01.2027 to 19.02.2027 |

- **TUWEL** course opens 01.10.2026 [S1]. Everything the notes expect from
  TUWEL (the exercises, the Part 1/Part 2 point split, the exam duration) is
  unverified: TUWEL was not read for these notes. The point split is not published anywhere outside TUWEL.
