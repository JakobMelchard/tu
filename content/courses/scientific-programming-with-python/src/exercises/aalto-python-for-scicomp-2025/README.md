# Aalto, *Python for Scientific Computing* — adapted practice

> **This is not 191.125 material.** It is a different university's course,
> reworked here. Nothing in this directory came from TU Wien, from Sascha
> Hunold or from TUWEL. See [`../../../notes/00-exam-focus.md`](../../../notes/00-exam-focus.md)
> for why this course has no practice material of its own.

## The source

| | |
|---|---|
| Institution | Aalto University — Aalto Scientific Computing (CodeRefinery/Nordic-e-Infrastructure collaboration) |
| Course | *Python for Scientific Computing* (no course code; a recurring 3-day workshop) |
| Version used | the `master` build of the site, last commit **2025-11-27** |
| URL | <https://aaltoscicomp.github.io/python-for-scicomp/> · repo <https://github.com/AaltoSciComp/python-for-scicomp> |
| Retrieved | 2026-09-22 |
| Licence | the repository's `LICENSE` file reads, in full, **"Creative Commons Attribution 4.0"**. The site footer says "© Copyright 2020-2024, The contributors." GitHub's licence detector reports `NOASSERTION`, because a one-line file is not the CC BY text. |
| Register entry | [`../../../refs/SOURCES.md`](../../../refs/SOURCES.md) **[S41]** |

**Nothing is vendored.** CC BY 4.0 would permit it, but the licence statement
is a single line rather than the licence text, and the material is a living
site with no tagged release — a copy would be a fork of something that moves.
Every task below was **restated in our own words and reimplemented** from
scratch; no sentence and no line of code is copied. Where a task depended on a
downloaded dataset, it was rebuilt on generated data, because this repo's
convention is that tests do no network I/O.

## What it covers that 191.125's TISS subject list also covers

The TISS subject list is the eight-item list in
[`../../../docs/tiss.md`](../../../docs/tiss.md), identical in all seven
offerings 2019W–2026W [S1]–[S7]. The overlap is the reason this source was
chosen, and it is the largest of the three:

| TISS subject item | Aalto chapter | used here |
|---|---|---|
| The SciPy and NumPy ecosystem | NumPy, Advanced NumPy, SciPy | tasks 1–3, 5 |
| Data processing and plotting (Matplotlib) | Pandas, Plotting with Matplotlib, Working with Data | task 4 |
| Parallel processing in Python | Parallel programming (GIL, `multiprocessing`, `mpi4py`, Dask) | task 6 |
| Reproducible … with IPython/Jupyter | Jupyter, Dependency management, Binder | prose only — see below |
| Interfaces to other programming languages | Extending Python with Cython | not used; [S39] covers this better |

## What it covers that this course does not

Scope differences matter as much as overlap, and Aalto is a *workshop for
researchers*, not an examined university course:

- **Xarray, Vega-Altair, Web APIs, Binder, packaging, the "library ecosystem"
  tour** — none of these are on the TISS list. Skipping them is deliberate.
- **Dask and `mpi4py`** go beyond what a 2 ECTS course examines on paper. Note
  08 names both and stops there; task 6 stays on `multiprocessing.Pool`.
- **No optimisation chapter at all.** TISS names optimisation as a subject item
  *and* a learning outcome; Aalto does not teach it. That gap is filled by
  `../scientific-python-lectures-2024/`.
- **No testing chapter.** Filled by
  `../software-carpentry-python-2026/`.
- **Nothing is examined.** Aalto has no written paper, so its exercises are
  "type this and see", not "answer this without an interpreter". The rewritten
  versions below all return a value a test can check, which is closer to what
  Part 2 of this course asks for.

## What is here

`aalto_exercises.py` — six tasks, each a function with a docstring saying which
Aalto exercise it is modelled on and what the point is:

| # | modelled on | TISS item | what it establishes |
|---|---|---|---|
| 1 | NumPy, "Exercises 3" | NumPy/SciPy | basic slicing aliases; fancy indexing, boolean masks and `copy()` do not |
| 2 | NumPy, "Exercises 2" | NumPy/SciPy | `*` vs `@`; `axis` names the axis that disappears; `keepdims` |
| 3 | NumPy, "Exercises 4" | NumPy/SciPy | `out=` and `*=` remove the temporary |
| 4 | the Pandas exercises (Titanic/Nobel → generated data) | Data processing | `agg` is one row per group, `transform` one per input row; pandas `std` is `ddof=1` |
| 5 | SciPy, the `quad` and sparse exercises | NumPy/SciPy | `quad` returns a *pair*; a tridiagonal matrix stores `3n − 2`, not `n²` |
| 6 | "Parallel-1" and "Parallel-2" | Parallel processing | seeded parallel Monte Carlo; `cpu_count()` is hardware, not your allocation |

`test_aalto_exercises.py` covers all six. Two processes, 200 000 samples:
the whole file runs in well under a second.

```sh
# from the course folder
uv run python src/exercises/aalto-python-for-scicomp-2025/aalto_exercises.py
uv run pytest src/exercises -q
```
