"""Pins the answer key of practice.py (printed in note 13). Each letter was also
checked by hand when the note was written; a change here means the note is stale."""
import practice


EXPECTED = {
    "P1": "TFTF",
    "P2": "TTFT",
    "P3": "TTF",
    "P4": "TFTF",
    "P5": "TT",
    "P6": "TTTTTF",
    "P7": "TTFF",
    "P8": "TTTT",
    "P9": "TF",
    "P10": "TTF",
    "P11": "TFTT",
    "P12": "TF",
    "P13": "TTTT",
    "P14": "FFT",
    "P15": "TF",
    "P16": "TF",
    "P17": "FT",
    "P18": "TTT",
}


def test_answer_key():
    got = {i: "".join("T" if x else "F" for x in v) for i, v in practice.answers().items()}
    assert got == EXPECTED


def test_every_statement_is_a_bool():
    for _, _, stmts in practice.ITEMS:
        for text, f in stmts:
            assert isinstance(f(), bool), text
