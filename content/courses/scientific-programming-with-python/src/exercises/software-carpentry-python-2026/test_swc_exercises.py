"""Tests for the Software Carpentry *Programming with Python* [S42] practice set
(note 11; notes 01, 02, 05).

Task 3 is written the way the lesson teaches it: these three cases were fixed
*before* ``range_overlap`` had a body, and the degenerate touching-ranges case
is the one that decides the design.
"""
from __future__ import annotations

import numpy as np
import pytest
import swc_exercises as ex


def test_axis_0_is_per_day_and_axis_1_is_per_patient() -> None:
    """Task 1: the reduction axis is the one that disappears."""
    data = ex.study_data(patients=60, days=40, seed=11)
    s = ex.study_summary(data)
    assert s["shape"] == (60, 40)
    assert s["days"] == 40 and s["patients"] == 60
    assert s["mean_per_day"].shape == (40,)
    assert s["max_per_patient"].shape == (60,)
    assert s["overall_mean"] == pytest.approx(s["mean_per_day"].mean())
    assert np.all(data >= 0), "clipped: an inflammation count cannot be negative"


def test_study_data_is_reproducible() -> None:
    """Task 1: a seeded Generator makes a data-dependent exercise repeatable."""
    assert np.array_equal(ex.study_data(seed=11), ex.study_data(seed=11))
    assert not np.array_equal(ex.study_data(seed=11), ex.study_data(seed=12))


@pytest.mark.parametrize("rect,expected", [
    ((0.0, 0.0, 4.0, 1.0), (0.0, 0.0, 1.0, 0.25)),
    ((0.0, 0.0, 1.0, 4.0), (0.0, 0.0, 0.25, 1.0)),
    ((2.0, 3.0, 4.0, 4.0), (0.0, 0.0, 1.0, 0.5)),
    ((0.0, 0.0, 2.0, 2.0), (0.0, 0.0, 1.0, 1.0)),
])
def test_normalise_rectangle(rect, expected) -> None:
    """Task 2: the longer side becomes 1, and a square stays square."""
    assert ex.normalise_rectangle(rect) == pytest.approx(expected)


@pytest.mark.parametrize("bad", [
    (0.0, 0.0, 1.0),                 # not four coordinates
    (1.0, 0.0, 0.0, 1.0),            # x bounds reversed
    (0.0, 1.0, 1.0, 0.0),            # y bounds reversed
])
def test_normalise_rectangle_preconditions_fire(bad) -> None:
    """Task 2: the precondition is what turns a silent wrong answer into a stop."""
    with pytest.raises(AssertionError):
        ex.normalise_rectangle(bad)


# --- Task 3, written first --------------------------------------------------
def test_range_overlap_single_range_is_itself() -> None:
    assert ex.range_overlap([(0.0, 1.0)]) == (0.0, 1.0)


def test_range_overlap_of_several() -> None:
    assert ex.range_overlap([(0.0, 2.0), (1.0, 4.0)]) == (1.0, 2.0)
    assert ex.range_overlap([(0.0, 1.0), (0.0, 2.0), (-1.0, 1.0)]) == (0.0, 1.0)


def test_range_overlap_returns_none_when_there_is_no_width() -> None:
    """The case the exercise exists for: ranges that only touch, and ranges
    that do not meet at all, both give None rather than a zero-width answer."""
    assert ex.range_overlap([(0.0, 1.0), (1.0, 2.0)]) is None
    assert ex.range_overlap([(0.0, 1.0), (5.0, 6.0)]) is None
    assert ex.range_overlap([]) is None
# ----------------------------------------------------------------------------


def test_else_runs_only_without_an_exception() -> None:
    """Task 4."""
    assert ex.exception_clause_order(False) == ["try", "else", "finally"]
    assert ex.exception_clause_order(True) == ["try", "except boom", "finally"]


def test_except_matches_subclasses() -> None:
    """Task 4: and KeyboardInterrupt deliberately is not an Exception, so
    `except Exception` does not swallow Ctrl-C."""
    h = ex.exception_hierarchy()
    assert h["KeyError is a LookupError"]
    assert h["IndexError is a LookupError"]
    assert h["ZeroDivisionError is an ArithmeticError"]
    assert not h["KeyboardInterrupt is an Exception"]


def test_assertions_do_not_survive_the_optimised_interpreter() -> None:
    """Task 5: measured with a child interpreter, not asserted from memory."""
    assert all(ex.assertions_are_stripped_under_O().values())


def test_module_runs_as_a_script(capsys) -> None:
    ex.main()
    out = capsys.readouterr().out
    assert "range_overlap" in out and "clause order" in out
