# *Scientific Python Lectures* — adapted practice

> **This is not 191.125 material.** It is a community textbook, reworked here.
> Nothing in this directory came from TU Wien, from Sascha Hunold or from
> TUWEL.

## The source

| | |
|---|---|
| Authors | the Scientific Python developers (Varoquaux, Gouillart, Vahtras, Haenel et al.) — no single institution |
| Work | *Scientific Python Lectures* (formerly *Scipy Lecture Notes*) |
| Version used | release **2024.1**, tagged 2024-04-26 (the latest tagged PDF; the live HTML build was 2025.2-dev at retrieval) |
| URL | <https://lectures.scientific-python.org/> · repo <https://github.com/scipy-lectures/scientific-python-lectures> |
| Retrieved | 2026-09-22 |
| Licence | **CC BY 4.0**, stated in the repository's `LICENSE.md`: "All code and material is licensed under a Creative Commons Attribution 4.0 International License (CC-by)" |
| Register entry | [`../../../refs/SOURCES.md`](../../../refs/SOURCES.md) **[S39]** — already registered before this pass, as the cross-check for notes 02, 03, 04, 07, 09 and 10 |

**Nothing is vendored**, although CC BY 4.0 plainly allows it. The reason is in
[`../../../refs/README.md`](../../../refs/README.md): TISS names no literature
at all, so this book is a supplement chosen here, and an 18 MB PDF in a 2 ECTS
course folder buys nothing that a link and `refs/fetch-sources.sh` do not. Every
task below was **restated in our own words and reimplemented**; no sentence and
no line of code is copied, and the objective functions are ours.

## What it covers that 191.125's TISS subject list also covers

This book's table of contents is the closest public match to the TISS subject
list of any free text — that is the finding [S39] was registered for. Two of its
chapters cover subject items that **neither of the other two sources here
teaches at all**, and those are the two used:

| TISS subject item | chapter | used here |
|---|---|---|
| Introduction to solving optimization problems (e.g. SciPy, PuLP) | 2.7 *Mathematical optimization* | tasks 1–4 |
| Interfaces to other programming languages (e.g. Julia) | 2.8 *Interfacing with C* | tasks 5–6 |
| The SciPy and NumPy ecosystem | 1.4 NumPy, 2.2 Advanced NumPy, 1.5 SciPy | already the cross-check for notes 02/03; not re-exercised here |

## What it covers that this course does not — and where it falls short

- **It teaches C, not Julia.** TISS's subject item says *"Interfaces to other
  programming languages (e.g. Julia)"*. Chapter 2.8 covers the Python-C-API,
  ctypes, SWIG and Cython, and does not mention Julia. Tasks 5–6 therefore
  exercise the part that transfers — calling convention, declared signatures,
  memory layout — and note 09's Julia material stays documentation-only
  [S30]. **No free CC-licensed Julia↔Python exercise set was found**; this is
  recorded as a gap in [`../../../notes/11-practice-set.md`](../../../notes/11-practice-set.md).
- **It does not cover linear programming.** Chapter 2.7 is continuous
  optimisation only: no `linprog`, no `milp`, no PuLP, no LP formulation. TISS
  names PuLP explicitly. The LP/ILP practice is therefore **ours**, in
  [`../../py/optimisation.py`](../../py/optimisation.py) and in the programming
  problems of note 11.
- **SWIG and the raw Python-C-API** are of historical interest for this course:
  note 09 teaches ctypes, cffi, f2py, pybind11 and juliacall instead.
- **Chapters 3.x (scikit-image, scikit-learn, statistics with pandas)** are
  outside the TISS list entirely.
- It is a *book*, so its exercises are open-ended ("find the fastest approach")
  rather than exam-shaped. The versions below each return a value a test can
  check.

## What is here

`spl_exercises.py` — six tasks:

| # | modelled on | TISS item | what it establishes |
|---|---|---|---|
| 1 | 2.7, "A simple (?) quadratic function" | Optimisation | an analytic `jac` cuts `nfev` (CG 30→10, BFGS 12→4); Newton-CG *refuses* without one |
| 2 | 2.7, "A locally flat minimum" | Optimisation | BFGS stops on a numerically zero gradient while still far out; Nelder-Mead and Powell reach the minimum. Check the achieved value, not `result.success` |
| 3 | 2.7, "Curve fitting with higher frequency" | Optimisation | least squares on a sinusoid is multi-modal in the frequency: `p0` decides the answer |
| 4 | ours (2.7 §"Optimization with constraints" is a figure, not a problem) | Optimisation | SLSQP `ineq` means `fun(x) ≥ 0` — the sign error that costs the whole question |
| 5 | 2.8, the "Ctypes" exercise (against libm, so nothing has to be built) | Interfaces | an undeclared `restype` returns a *wrong number*, not an exception |
| 6 | ours (the memory-layout half of 2.8) | Interfaces | `a.T` is already F-contiguous and shares memory; `asfortranarray` copies |

`test_spl_exercises.py` covers all six.

```sh
# from the course folder
uv run python src/exercises/scientific-python-lectures-2024/spl_exercises.py
uv run pytest src/exercises -q
```

Attribution, as CC BY 4.0 requires if you reuse anything from the book itself:
The Scientific Python developers, *Scientific Python Lectures*, release 2024.1,
<https://lectures.scientific-python.org/> — CC BY 4.0.
