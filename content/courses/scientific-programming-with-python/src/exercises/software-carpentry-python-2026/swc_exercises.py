"""Exercises in the style of Software Carpentry's *Programming with Python* [S42].

Serves note 11 (practice set) §3; topics: the language and exceptions (note 01),
per-axis NumPy summaries (02), assertions and test-first design (05).

**Not this course's material.**  Source: Software Carpentry,
*Programming with Python* (``swcarpentry/python-novice-inflammation``),
https://swcarpentry.github.io/python-novice-inflammation/ — instructional
material CC BY 4.0, example code MIT, Copyright (c) The Carpentries.  See
``README.md`` in this directory and ``../../../refs/SOURCES.md`` [S42].  The
tasks are **restated in our own words and reimplemented**; no text or code is
copied, and the lesson's ``inflammation-*.csv`` data files are replaced by
generated arrays so the course suite does no file or network I/O.

Covers TISS items: "Introduction to the Python programming language" and
"Code testing" — the two that Aalto [S41] and the Scientific Python Lectures
[S39] leave thinnest.

Run:  ../../../../../.venv/bin/python swc_exercises.py
"""
from __future__ import annotations

import subprocess
import sys

import numpy as np

# Task 1 (after SWC "Analyzing Patient Data" / "Visualizing Tabular Data", whose
# data is a downloaded CSV; generated here instead).


def study_data(patients: int = 60, days: int = 40, seed: int = 11) -> np.ndarray:
    """A (patients, days) table: each row one patient, each column one day."""
    rng = np.random.default_rng(seed)
    profile = np.sin(np.linspace(0.0, np.pi, days)) * 12.0
    return np.clip(np.round(profile + rng.normal(0.0, 2.0, (patients, days))), 0, None)


def study_summary(data: np.ndarray) -> dict[str, object]:
    """Per-day and per-patient summaries, and the axis rule behind them.

    The whole exercise is one idea: `axis=0` collapses the patients and leaves
    one number per day, `axis=1` collapses the days and leaves one per patient.
    Getting it backwards is silent — both are valid arrays.
    """
    return {
        "shape": data.shape,
        "mean_per_day": data.mean(axis=0),
        "max_per_patient": data.max(axis=1),
        "days": data.mean(axis=0).size,
        "patients": data.max(axis=1).size,
        "overall_mean": float(data.mean()),
    }


# Task 2 (after SWC "Defensive Programming", exercise on pre- and
# post-conditions): rescale a rectangle to the unit square, and say in
# assertions what must be true before and after.


def normalise_rectangle(rect: tuple[float, float, float, float]) -> tuple[float, ...]:
    """Scale (x0, y0, x1, y1) so the longer side becomes 1 and the corner is 0.

    Written the way the lesson argues for: a **precondition** on the input, the
    computation, then a **postcondition** on the result.  Assertions here mark
    programmer errors; they are not input validation — see
    ``assertions_are_stripped_under_O``.
    """
    assert len(rect) == 4, "a rectangle is four coordinates"
    x0, y0, x1, y1 = rect
    assert x0 < x1, "invalid X bounds"
    assert y0 < y1, "invalid Y bounds"

    width, height = x1 - x0, y1 - y0
    if width > height:
        scaled = height / width
        out = (0.0, 0.0, 1.0, scaled)
    else:
        scaled = width / height
        out = (0.0, 0.0, scaled, 1.0)

    assert 0 < out[2] <= 1.0, "calculated width is out of bounds"
    assert 0 < out[3] <= 1.0, "calculated height is out of bounds"
    return out


# Task 3 (after SWC "Defensive Programming", the test-driven-development
# exercise): the intersection of a list of ranges.  Written test-first — the
# three cases in ``test_swc_exercises.py`` were fixed before this body was.


def range_overlap(ranges: list[tuple[float, float]]) -> tuple[float, float] | None:
    """The largest interval contained in every range, or None if there is none.

    The case the lesson exists to make you think about: ranges that touch at a
    single point, e.g. (0, 1) and (1, 2).  There is no interval of positive
    width, so this returns None rather than the degenerate (1, 1).
    """
    if not ranges:
        return None
    lowest = max(low for low, _ in ranges)
    highest = min(high for _, high in ranges)
    return (lowest, highest) if lowest < highest else None


# Task 4 (after SWC "Errors and Exceptions"): which clause runs, and when.


def exception_clause_order(fail: bool) -> list[str]:
    """Record the order in which try/except/else/finally bodies run.

    `else` runs only when the `try` body did *not* raise, and `finally` runs
    either way — including on the way out through a `return`.  The MC form of
    this is "which of these lines is printed".
    """
    log: list[str] = []
    try:
        log.append("try")
        if fail:
            raise ValueError("boom")
    except ValueError as exc:
        log.append(f"except {exc}")
    else:
        log.append("else")
    finally:
        log.append("finally")
    return log


def exception_hierarchy() -> dict[str, bool]:
    """`except` matches subclasses, which is why bare `except Exception` hides
    bugs: a typo raises NameError and is caught along with everything else."""
    return {
        "KeyError is a LookupError": issubclass(KeyError, LookupError),
        "IndexError is a LookupError": issubclass(IndexError, LookupError),
        "ZeroDivisionError is an ArithmeticError":
            issubclass(ZeroDivisionError, ArithmeticError),
        "KeyboardInterrupt is an Exception": issubclass(KeyboardInterrupt, Exception),
    }


# Task 5 (ours; the consequence of task 2 that the lesson states in prose and
# that a written exam can ask as a one-liner).


def assertions_are_stripped_under_O() -> dict[str, bool]:
    """`python -O` removes every `assert` and sets `__debug__` to False.

    So an assertion is a claim about your own code, checked while you develop
    it.  A check on data that arrives from outside must `raise` instead — it has
    to survive the optimised run.  Measured by running a child interpreter
    rather than asserted from memory.
    """
    program = "assert False, 'x'\nprint('survived', __debug__)"

    def run(*flags: str) -> subprocess.CompletedProcess:
        return subprocess.run([sys.executable, *flags, "-c", program],
                              capture_output=True, text=True)

    plain, optimised = run(), run("-O")
    return {
        "assert fires normally": plain.returncode != 0,
        "assert is gone under -O": optimised.returncode == 0,
        "__debug__ is False under -O": "survived False" in optimised.stdout,
    }


def main() -> None:
    summary = study_summary(study_data())
    print(f"1. {summary['patients']} patients x {summary['days']} days, "
          f"mean {summary['overall_mean']:.2f}, "
          f"peak day {int(np.argmax(summary['mean_per_day']))}")
    print("2. normalise_rectangle((0, 0, 4, 1)) =", normalise_rectangle((0, 0, 4, 1)))
    print("3. range_overlap([(0, 2), (1, 4)]) =", range_overlap([(0, 2), (1, 4)]),
          "| touching:", range_overlap([(0, 1), (1, 2)]))
    print("4. clause order, no error:", exception_clause_order(False))
    print("   clause order, error   :", exception_clause_order(True))
    print("5. assertions under -O:", assertions_are_stripped_under_O())


if __name__ == "__main__":
    main()
