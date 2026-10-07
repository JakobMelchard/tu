"""Every code pointer in the notes and refs resolves to a real function.

Checked forms, in notes/*.md (not CHANGELOG.md, which records removed names),
refs/lecture-notes-map.md and src/README.md:
  `module.name`                        name (or glob, `neville.hermite_*`) in module
  `src/py/module.py`: `a`, `b` / `_c`  each name in that paragraph is in module
                                       (a leading `_suffix` abbreviates a sibling)
  | `module.py` | note | `a`, `b` |     the src/README module table
  `test_x.py` / `test_x.py::test_y`    the test file and test function exist
  `src/cpp/x.cpp`                      the C++ source exists
"""
import fnmatch
import importlib
import inspect
import pathlib
import re

import pytest

PY = pathlib.Path(__file__).resolve().parent
COURSE = PY.parent.parent
DOCS = sorted(p for p in (COURSE / "notes").glob("*.md") if p.name != "CHANGELOG.md") + [COURSE / "refs" / "lecture-notes-map.md",
                                                  COURSE / "src" / "README.md"]
MODULES = sorted(p.stem for p in PY.glob("*.py") if not p.stem.startswith("test_"))


def names(mod):
    """Public attributes plus every function parameter (`matvec`, `damped`)."""
    m = importlib.import_module(mod)
    out = {n for n in dir(m) if not n.startswith("__")}
    for obj in vars(m).values():
        if inspect.isfunction(obj) and obj.__module__ == mod:
            out |= set(inspect.signature(obj).parameters)
    return out


NAMES = {m: names(m) for m in MODULES}


def resolves(mod, tok):
    if tok.startswith("_") and tok not in NAMES[mod]:
        return any(n.endswith(tok) for n in NAMES[mod])
    return bool(fnmatch.filter(NAMES[mod], tok))


def pointers(text):
    for mod, tok in re.findall(r"`([a-z0-9_]+)\.([A-Za-z_][A-Za-z0-9_*]*)`", text):
        if mod in MODULES and tok not in ("py", "cpp"):
            yield mod, tok
    for mod, body in re.findall(r"`src/py/([a-z0-9_]+)\.py`(.*?)(?=\n\n|`src/py/|\Z)", text, re.S):
        for tok in re.findall(r"`([A-Za-z_][A-Za-z0-9_]*)`", body):
            yield mod, tok
    for mod, body in re.findall(r"^\| (?:\*\*)?`([a-z0-9_]+)\.py`(?:\*\*)? \|[^|]*\|(.*)$", text, re.M):
        for tok in re.findall(r"`([A-Za-z_][A-Za-z0-9_]*)`", body):
            yield mod, tok


@pytest.mark.parametrize("doc", DOCS, ids=lambda p: str(p.relative_to(COURSE)))
def test_python_pointers_resolve(doc):
    bad = [f"{m}.{t}" for m, t in pointers(doc.read_text())
           if m not in MODULES or not resolves(m, t)]
    assert not bad, f"{doc.name}: unresolved {bad}"


@pytest.mark.parametrize("doc", DOCS, ids=lambda p: str(p.relative_to(COURSE)))
def test_test_and_cpp_pointers_resolve(doc):
    text = doc.read_text()
    bad = []
    for f, fn in re.findall(r"`(test_[a-z0-9_]+\.py)(?:::([A-Za-z0-9_]+))?`", text):
        if not (PY / f).exists():
            bad.append(f)
        elif fn and not re.search(rf"^def {fn}\(", (PY / f).read_text(), re.M):
            bad.append(f"{f}::{fn}")
    for f in re.findall(r"`(?:src/)?cpp/([a-z0-9_]+\.(?:cpp|hpp))`", text):
        if not (COURSE / "src" / "cpp" / f).exists():
            bad.append(f)
    assert not bad, f"{doc.name}: unresolved {bad}"
