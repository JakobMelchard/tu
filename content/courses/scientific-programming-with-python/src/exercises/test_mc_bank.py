"""Run every multiple-choice item against the installed libraries (note 11 §2).

This is the point of the bank: an item whose stated answer stops being true
after a library upgrade fails here instead of misleading a reader in December.
It extends ``../py/test_doc_examples.py`` from "one test per version-sensitive
claim in the notes" to "one test per exam question".

Run:  ../../../../.venv/bin/python -m pytest test_mc_bank.py -q
"""
from __future__ import annotations

import pytest
from mc_bank import LETTERS, TOPICS, AmbiguousItem, Item, pick, pick_true
from mc_items import ITEMS


@pytest.mark.parametrize("item", ITEMS, ids=[i.id for i in ITEMS])
def test_item_answer_is_what_the_code_does(item: Item) -> None:
    """The recorded answer is re-derived by executing the behaviour."""
    item.verify()


def test_bank_is_well_formed() -> None:
    ids = [i.id for i in ITEMS]
    assert len(set(ids)) == len(ids), "duplicate item id"
    for item in ITEMS:
        assert item.topic in TOPICS, f"{item.id}: topic not on the TISS list"
        assert item.answer in LETTERS and len(item.options) == 4
        assert len(set(item.options)) == 4, f"{item.id}: repeated option text"
        assert item.why.strip(), f"{item.id}: no justification"


def test_every_tiss_subject_item_is_covered() -> None:
    """The TISS subject list has eight items; the bank carries three each."""
    counts = {topic: sum(i.topic == topic for i in ITEMS) for topic in TOPICS}
    assert counts == dict.fromkeys(TOPICS, 3), counts
    assert len(ITEMS) == 24


def test_render_is_readable_without_the_answer() -> None:
    text = ITEMS[0].render()
    assert "(a)" in text and "(d)" in text
    assert ITEMS[0].why not in text
    assert ITEMS[0].why in ITEMS[0].render(with_answer=True)


# ------------------------------------------------ the guard rails themselves
def test_pick_rejects_an_item_with_two_right_answers() -> None:
    with pytest.raises(AmbiguousItem):
        pick(3, a=3, b=3, c=1, d=2)
    with pytest.raises(AmbiguousItem):
        pick(9, a=3, b=4, c=1, d=2)
    assert pick(3, a=3, b=4, c=1, d=2) == "a"


def test_pick_requires_all_four_options() -> None:
    with pytest.raises(AmbiguousItem):
        pick(3, a=3, b=4, c=1)
    with pytest.raises(AmbiguousItem):
        pick_true(a=lambda: True, b=lambda: False)


def test_pick_true_needs_exactly_one_true_predicate() -> None:
    with pytest.raises(AmbiguousItem):
        pick_true(a=lambda: True, b=lambda: True, c=lambda: False, d=lambda: False)
    assert pick_true(a=lambda: False, b=lambda: False,
                     c=lambda: True, d=lambda: False) == "c"


def test_verify_reports_a_disagreement_rather_than_passing() -> None:
    wrong = Item("X1", "language", "stem", ("w", "x", "y", "z"), "a", "why",
                 lambda: "c")
    with pytest.raises(AssertionError, match="execution says"):
        wrong.verify()
