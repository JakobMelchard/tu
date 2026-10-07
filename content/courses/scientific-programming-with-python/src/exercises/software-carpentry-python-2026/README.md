# Software Carpentry, *Programming with Python* — adapted practice

> **This is not 191.125 material.** It is The Carpentries' workshop lesson,
> reworked here. Nothing in this directory came from TU Wien, from Sascha
> Hunold or from TUWEL.

## The source

| | |
|---|---|
| Organisation | The Carpentries (Software Carpentry) |
| Lesson | *Programming with Python* — repository `swcarpentry/python-novice-inflammation` |
| Version used | the published `main` build; most recent commit at retrieval **2026-09-22** (the lesson is continuously maintained and has no release tags) |
| URL | <https://swcarpentry.github.io/python-novice-inflammation/> · repo <https://github.com/swcarpentry/python-novice-inflammation> |
| Retrieved | 2026-09-22 |
| Licence | instructional material **CC BY 4.0**; example programs and software **MIT**; Copyright (c) The Carpentries. Stated at <https://swcarpentry.github.io/python-novice-inflammation/LICENSE.html> |
| Register entry | [`../../../refs/SOURCES.md`](../../../refs/SOURCES.md) **[S42]** |

**Nothing is vendored.** Both licences permit it; the lesson is a living site
with no tagged release, and its data files (`inflammation-*.csv`) are the part
that would have to be copied. Every task below was **restated in our own words
and reimplemented**; no sentence and no line of code is copied, and the CSV data
is replaced by a seeded generator so the tests do no file or network I/O.

## What it covers that 191.125's TISS subject list also covers

| TISS subject item | episodes | used here |
|---|---|---|
| Introduction to the Python programming language | 1 Python Fundamentals, 4 Lists, 5 Loops, 7 Making Choices, 8 Creating Functions, 9 Errors and Exceptions | tasks 1, 4 |
| Code testing | 10 Defensive Programming (assertions, pre/post-conditions, invariants, TDD), 11 Debugging | tasks 2, 3, 5 |
| The SciPy and NumPy ecosystem | 2 Analyzing Patient Data (NumPy only) | task 1 |
| Data processing and plotting | 3 Visualizing Tabular Data (Matplotlib only) | prose only |

Episode 10 is the reason this source is here. **Neither Aalto [S41] nor the
Scientific Python Lectures [S39] has a testing chapter**, and "Code testing" is
its own item on the TISS subject list. Episode 10 is the only free CC-licensed
treatment found that is written as *exercises* rather than as API reference.

## What it covers that this course does not

- **It is a novice lesson.** It spends four episodes on lists, loops and
  conditionals, which note 01 assumes. Those were not rebuilt.
- **It teaches `assert`, not `pytest`.** The lesson's testing is assertions and
  test-driven development by hand; there are no fixtures, no `parametrize`, no
  `approx`. That half of TISS's "Code testing" item is note 05's and
  [`../../py/test_testing_examples.py`](../../py/test_testing_examples.py)'s —
  it has no free-course substitute and did not need one, because pytest's own
  documentation [S18] is the primary source and is already cited.
- **No SciPy, no optimisation, no parallelism, no interfaces, no Jupyter.** Five
  of the eight TISS items are outside this lesson entirely.
- **Episode 12, Command-Line Programs** (`argparse`, `sys.argv`, pipes) is not
  on the TISS list. Skipped.

## What is here

`swc_exercises.py` — five tasks:

| # | modelled on | TISS item | what it establishes |
|---|---|---|---|
| 1 | ep. 2/3 "Analyzing Patient Data" (CSV → generated array) | Language, NumPy | `axis=0` is per day, `axis=1` is per patient; the wrong one is silently valid |
| 2 | ep. 10, the pre/post-condition exercise | Code testing | assertions as a contract: what must hold before, what must hold after |
| 3 | ep. 10, the test-driven-development exercise | Code testing | written test-first; ranges that only *touch* have no overlap, and that case decides the design |
| 4 | ep. 9 "Errors and Exceptions" | Language | `else` runs only without an exception, `finally` always; `except` matches subclasses |
| 5 | ours (the consequence ep. 10 states in prose) | Code testing | `python -O` deletes every `assert` — so an assertion is not input validation. Measured by running a child interpreter |

`test_swc_exercises.py` covers all five. Task 3's three tests are grouped and
marked in the file, because they were fixed before `range_overlap` had a body —
that is the exercise.

```sh
# from the course folder
uv run python src/exercises/software-carpentry-python-2026/swc_exercises.py
uv run pytest src/exercises -q
```

Attribution, as CC BY 4.0 requires if you reuse anything from the lesson itself:
Software Carpentry, *Programming with Python*,
<https://swcarpentry.github.io/python-novice-inflammation/> — CC BY 4.0,
Copyright (c) The Carpentries.
