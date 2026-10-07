"""Every code pointer in the notes resolves, and every module keeps the
contract the notes rely on.

1. Each topic note 01-13 ends in a `## Code` section of the form
   "`src/py/foo.py`: `bar`, `Baz.qux` ... Tests: `test_foo.py::test_x`".
   Every backticked identifier after a module mention must be defined in
   that module (up to the next module mention); `test_*.py::name` must name
   a test function.  This is the check the conventions ask for ("pointers
   to the reference implementation").
2. Anywhere in the notes, the READMEs and refs/lecture-notes-map.md:
   backticked `module.name` pointers, the bare names chained to them
   ("`rsa.keygen`, `encrypt`, `decrypt`"), `file.py::name` pointers,
   backticked .py paths, and relative Markdown links all resolve.
   notes/CHANGELOG.md is excluded: it quotes old names on purpose.
3. Every implementation module names its primitive, note and standard in
   its docstring, says it is toy code, has a seeded `__main__` demo, has a
   test file, and stays under 300 lines.

Offline: it only imports our own modules and reads files.
"""
from __future__ import annotations

import importlib
import pathlib
import re
import sys

import pytest

COURSE = pathlib.Path(__file__).resolve().parents[2]
PY = COURSE / "src" / "py"
FILES = {f.name: f for d in [PY, COURSE / "src"] for f in d.glob("*.py")}
MODULES = {pathlib.Path(n).stem for n in FILES if n != "conftest.py"}
NOTES = sorted((COURSE / "notes").glob("[0-9][0-9]-*.md"))
TOPIC_NOTES = [n for n in NOTES if not n.name.startswith("00-")]   # 00 is the exam guide
DOCS = NOTES + [COURSE / "index.md", COURSE / "notes" / "README.md",
                COURSE / "src" / "README.md",
                COURSE / "refs" / "README.md", COURSE / "refs" / "lecture-notes-map.md"]
if str(PY) not in sys.path:
    sys.path.insert(0, str(PY))
IMPLEMENTATIONS = sorted(m for m in MODULES if (PY / f"{m}.py").exists() and not m.startswith("test_"))

TICK = re.compile(r"`([^`\n]+)`")
DOTTED = re.compile(r"^([a-z_][a-z0-9_]*)\.([A-Za-z_]\w*(?:\.[A-Za-z_]\w*)*)(?:\(.*\))?$")
CHAIN = re.compile(r"`([a-z_][a-z0-9_]*)\.[A-Za-z_][\w.]*`((?:\s*(?:/|,|\+|and|or)\s*`[A-Za-z_]\w*`)+)")
TEST_REF = re.compile(r"(test_\w+)\.py::(\w+)")
PY_PATH = re.compile(r"^(?:\.\./)*(?:src/py/|src/exercises/[\w-]+/)?([\w-]+\.py)$")


def _resolve(module: str, dotted: str) -> bool:
    try:
        obj = importlib.import_module(module)
        for part in dotted.split("."):
            obj = getattr(obj, part)
        return True
    except (AttributeError, ModuleNotFoundError):
        return False


def _code_section(text: str) -> str:
    m = re.search(r"^## Code\s*$(.*?)(?=^## |\Z)", text, re.M | re.S)
    return m.group(1) if m else ""


def code_section_pointers(text: str) -> list[tuple[str, str]]:
    """(module, name) pairs from a note's `## Code` section."""
    out, mod = [], None
    for tok in TICK.findall(_code_section(text)):
        path = PY_PATH.match(tok)
        if path:
            stem = pathlib.Path(path.group(1)).stem
            mod = stem if stem in MODULES else None
            if mod is None:
                out.append(("<missing file>", tok))
            continue
        if TEST_REF.search(tok) or DOTTED.match(tok):
            continue                                   # checked by the anywhere-pass
        ident = re.match(r"^([A-Za-z_]\w*(?:\.\w+)*)(?:\(.*\))?$", tok)
        if mod and ident:
            out.append((mod, ident.group(1)))
    return out


def anywhere_pointers(text: str) -> list[tuple[str, str]]:
    out = []
    for tok in TICK.findall(text):
        m = DOTTED.match(tok)
        if m and m.group(1) in MODULES and m.group(2) != "py":
            out.append((m.group(1), m.group(2)))
        for mod, name in TEST_REF.findall(tok):
            out.append((mod, name))
    for mod, tail in CHAIN.findall(text):
        if mod in MODULES:
            out += [(mod, name) for name in re.findall(r"`(\w+)`", tail)]
    return out


@pytest.mark.parametrize("note", TOPIC_NOTES, ids=lambda p: p.name)
def test_code_section_pointers_resolve(note):
    text = note.read_text()
    pointers = code_section_pointers(text)
    assert pointers, f"{note.name} has no `## Code` section with pointers"
    missing = [f"{m}.{n}" for m, n in pointers if not _resolve(m, n)]
    assert missing == []


@pytest.mark.parametrize("doc", DOCS, ids=lambda p: str(p.relative_to(COURSE)))
def test_pointers_paths_and_links_resolve(doc):
    text = doc.read_text()
    missing = [f"{m}.{n}" for m, n in anywhere_pointers(text) if not _resolve(m, n)]
    for tok in TICK.findall(text):
        path = PY_PATH.match(tok)
        if path and path.group(1) not in FILES and path.group(1) != "foo.py":
            missing.append(tok)
    for link in re.findall(r"\]\(([^)#\s]+)(?:#[^)]*)?\)", text):
        if not link.startswith(("http:", "https:", "mailto:")) and not (doc.parent / link).exists():
            missing.append(f"link {link}")
    assert missing == []


def test_the_checker_sees_pointers():
    """Guard against a regex change silently checking nothing."""
    assert sum(len(code_section_pointers(n.read_text())) for n in NOTES) > 80
    assert sum(len(anywhere_pointers(d.read_text())) for d in DOCS) > 100


@pytest.mark.parametrize("module", IMPLEMENTATIONS)
def test_module_contract(module):
    src = (PY / f"{module}.py").read_text()
    doc = importlib.import_module(module).__doc__ or ""
    for field in ("Primitive:", "Note:", "Standard:"):
        assert field in doc, f"{module}: docstring lacks '{field}'"
    assert re.search(r"notes/\d\d-[\w-]+\.md|note \d\d", doc), f"{module}: names no note"
    assert "EDUCATIONAL TOY CODE" in doc
    assert 'if __name__ == "__main__":' in src, f"{module}: no runnable demo"
    if module != "rng" and "rng." in src.split('if __name__ == "__main__":')[0]:
        assert "rng.seed(" in src.split('if __name__ == "__main__":')[1], f"{module}: demo not seeded"
    assert f"test_{module}.py" in FILES, f"{module}: no test file"
    assert len(src.splitlines()) <= 300, f"{module}: over 300 lines"


def test_every_module_is_pointed_to_by_a_note():
    named = {m for n in NOTES for m, _ in code_section_pointers(n.read_text())}
    assert set(IMPLEMENTATIONS) - {"rfc_vectors", "rng"} <= named
