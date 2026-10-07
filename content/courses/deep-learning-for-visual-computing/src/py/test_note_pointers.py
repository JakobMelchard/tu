"""Every code pointer in ../../notes resolves to a real name in src/py, and every
module in src/py names its note, has a demo and has a test file.

The notes end in a `## Code` section of the form
"`src/py/foo.py`: `bar`, `Baz(arg=...)` ...".  For every backticked identifier
that follows a module mention (up to the next module mention, or up to the word
"sklearn" or "Test(s)", after which names belong to the library) this test
checks that the module defines it: a module attribute, a class attribute, a
`self.<name>` attribute or parameter name in the source, or a string label the
module returns.  Dotted pointers
`module.name` are checked anywhere in a note.  The notes serve the modules, so a
rename in src/py that is not carried into the note fails here.
"""
import glob
import importlib
import os
import re

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
NOTES = sorted(glob.glob(os.path.join(HERE, "..", "..", "notes", "[0-9][0-9]-*.md")))
MODULES = {os.path.basename(p)[:-3] for p in glob.glob(os.path.join(HERE, "*.py"))}

MOD_RE = re.compile(r"(?:\.\./)?(?:src/py/)?(\w+)\.py")
TICK_RE = re.compile(r"`([^`]+)`")
IDENT_RE = re.compile(r"^([A-Za-z_]\w*)")
DOTTED_RE = re.compile(r"`(\w+)\.(\w+)[^`]*`")


def _code_section(text):
    """The text of the note's `## Code` section (empty if there is none)."""
    m = re.search(r"^## Code\s*$(.*?)(?=^## |\Z)", text, re.M | re.S)
    return m.group(1) if m else ""


def resolves(module, name):
    mod = importlib.import_module(module)
    if hasattr(mod, name):
        return True
    for obj in vars(mod).values():
        if isinstance(obj, type) and obj.__module__ == module and hasattr(obj, name):
            return True
    src = open(os.path.join(HERE, module + ".py")).read()
    pattern = rf"(\bdef |\bclass |\bself\.|[(,]\s*){re.escape(name)}\b|[\"']{re.escape(name)}[\"']"
    return re.search(pattern, src) is not None


def pointers(path):
    """(module, name) pairs referenced by one note."""
    text = open(path).read()
    out = set()
    for mod, name in DOTTED_RE.findall(text):
        if mod in MODULES and name != "py":
            out.add((mod, name))
    code, mod, last = _code_section(text), None, 0
    for m in TICK_RE.finditer(code):
        if re.search(r"\b(sklearn|Tests?)\b", code[last:m.start()]):
            mod = None                              # names after these words are sklearn's
        last, tok = m.end(), m.group(1)
        mm = MOD_RE.fullmatch(tok)
        if mm:
            mod = mm.group(1) if mm.group(1) in MODULES else None
            continue
        ident = IDENT_RE.match(tok)
        head = tok.split("(")[0]
        if mod and ident and "." not in head and "/" not in head and ident.group(1) != "__main__":
            out.add((mod, ident.group(1)))
    return sorted(out)


@pytest.mark.parametrize("path", NOTES, ids=[os.path.basename(p) for p in NOTES])
def test_note_code_pointers_resolve(path):
    missing = [f"{m}.{n}" for m, n in pointers(path) if not resolves(m, n)]
    assert not missing, f"{os.path.basename(path)}: unresolved pointers {missing}"


def test_the_checker_sees_pointers():
    """Guard against a regex change silently checking nothing."""
    total = sum(len(pointers(p)) for p in NOTES)
    assert total > 60


IMPLEMENTATIONS = sorted(m for m in MODULES if not m.startswith("test_"))


@pytest.mark.parametrize("module", IMPLEMENTATIONS)
def test_module_names_its_note_has_a_demo_and_a_test(module):
    src = open(os.path.join(HERE, module + ".py")).read()
    doc = importlib.import_module(module).__doc__ or ""
    assert re.search(r"\b[Nn]otes? \d\d", doc), f"{module}: docstring names no note"
    assert 'if __name__ == "__main__":' in src, f"{module}: no runnable demo"
    assert "test_" + module in MODULES, f"{module}: no test file"
    assert len(src.splitlines()) <= 300, f"{module}: over 300 lines"
