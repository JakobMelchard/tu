"""Executable multiple-choice bank (note 11 §2): the framework.  **Ours.**

No past paper for 191.125, for this lecturer or for the predecessor number
191.116 is public (``../../refs/SOURCES.md`` S1-S9), so nothing here is "what
was asked".  What it *is*: TISS says the exam is "written exam with multiple
choice and programming exercises" since 2024W [S3], and multiple choice about
library behaviour is the one kind of exam question that can be **checked by
running it**.

So every item in ``mc_items.py`` carries a ``check`` callable that executes the
behaviour in the repo venv and *derives* the letter of the correct answer from
the result.  ``test_mc_bank.py`` runs all of them.  Two consequences:

* the stated answer cannot be wrong unless the library changes, and
* the *distractors* are checked too -- ``pick``/``pick_true`` require exactly
  one of the four options to match, so an item with two defensible answers
  fails the suite instead of misleading a reader.

This extends the pattern of ``../py/test_doc_examples.py`` from "one test per
version-sensitive claim in the notes" to "one test per exam question".  Versions
are pinned in ``../../refs/SOURCES.md`` S40.

Run:  ../../../../.venv/bin/python mc_bank.py        # print the quiz
      ../../../../.venv/bin/python mc_bank.py -a     # ... with answers
"""
from __future__ import annotations

import sys
from collections.abc import Callable
from dataclasses import dataclass

LETTERS = ("a", "b", "c", "d")

# The eight-item TISS "Subject of course" list, byte-identical in all seven
# offerings 2019W-2026W [S1]-[S7].  Keys are used as the topic tag on an item.
TOPICS: dict[str, str] = {
    "language": "Introduction to the Python programming language",
    "numpy-scipy": "The SciPy and NumPy ecosystem",
    "data-plotting": "Data processing and plotting (Matplotlib)",
    "testing": "Code testing",
    "jupyter": "Reproducible and interactive data processing with IPython/Jupyter",
    "optimisation": "Introduction to solving optimization problems (e.g. SciPy, PuLP)",
    "parallel": "Parallel processing in Python",
    "interfaces": "Interfaces to other programming languages (e.g. Julia)",
}


class AmbiguousItem(AssertionError):
    """Raised when zero or more than one option matches what the code did."""


@dataclass(frozen=True)
class Item:
    """One multiple-choice question whose answer is produced by execution.

    ``check`` must *compute* the letter, never return a literal: it is the only
    thing standing between a plausible-sounding answer and a wrong one.
    """

    id: str
    topic: str
    stem: str
    options: tuple[str, str, str, str]
    answer: str
    why: str
    check: Callable[[], str]

    def verify(self) -> str:
        """Run the check and confirm it agrees with the recorded answer."""
        got = self.check()
        if got != self.answer:
            raise AssertionError(
                f"{self.id}: recorded answer ({self.answer}) "
                f"{self.options[LETTERS.index(self.answer)]!r} "
                f"but execution says ({got}) "
                f"{self.options[LETTERS.index(got)]!r}"
            )
        return got

    def render(self, with_answer: bool = False) -> str:
        opts = "\n".join(
            f"    ({ell}) {text}" for ell, text in zip(LETTERS, self.options)
        )
        out = f"{self.id} [{self.topic}]  {self.stem}\n{opts}"
        if with_answer:
            out += f"\n    -> ({self.answer}) {self.why}"
        return out


def _same(a: object, b: object) -> bool:
    """Equality that survives numpy, where ``a == b`` returns an array and
    ``bool()`` of it raises.  Compare shapes, ``.tolist()`` or scalars, not
    arrays."""
    try:
        return bool(a == b)
    except (ValueError, TypeError):
        return False


def pick(value: object, **by_letter: object) -> str:
    """Return the one option letter whose recorded value equals ``value``.

    All four options must be supplied, so a distractor that is *also* right is
    an error rather than a silent trap.
    """
    _require_four(by_letter)
    hits = [k for k, v in by_letter.items() if _same(value, v)]
    if len(hits) != 1:
        raise AmbiguousItem(f"{value!r} matches {hits or 'no option'} in {by_letter}")
    return hits[0]


def pick_true(**by_letter: Callable[[], bool]) -> str:
    """Return the one option letter whose predicate is true when run."""
    _require_four(by_letter)
    hits = [k for k, pred in by_letter.items() if pred()]
    if len(hits) != 1:
        raise AmbiguousItem(f"{hits or 'no option'} true among {sorted(by_letter)}")
    return hits[0]


def _require_four(by_letter: dict[str, object]) -> None:
    if sorted(by_letter) != list(LETTERS):
        raise AmbiguousItem(f"need one entry per option a-d, got {sorted(by_letter)}")


def raises(exc: type[BaseException], fn: Callable[[], object]) -> bool:
    """True if calling ``fn`` raises ``exc``.  Used by items about errors."""
    try:
        fn()
    except exc:
        return True
    except BaseException:
        return False
    return False


def main(argv: list[str]) -> int:
    from mc_items import ITEMS

    with_answer = "-a" in argv or "--answers" in argv
    for topic in TOPICS:
        group = [i for i in ITEMS if i.topic == topic]
        print(f"\n=== {TOPICS[topic]} ({len(group)} items) ===")
        for item in group:
            print(item.render(with_answer))
    print(f"\n{len(ITEMS)} items; every answer re-derived by execution.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
