"""Every code pointer and relative link in the notes and READMEs resolves.

Checks notes/*.md (not the CHANGELOG), the course index.md, src/README.md,
refs/README.md and refs/lecture-notes-map.md: backticked `module.name`
references for every module in src/py, `file.py::name` references, backticked
.py/.sh paths, relative Markdown links, and that every [S<n>] cited in a note
exists in refs/SOURCES.md.  Offline: imports our own modules and reads files.
"""
import importlib
import pathlib
import re
import sys

import pytest

COURSE = pathlib.Path(__file__).resolve().parents[2]
PY = COURSE / "src/py"
MODULES = {f.stem for f in PY.glob("*.py")}
DOCS = (sorted(p for p in (COURSE / "notes").glob("*.md") if p.name != "CHANGELOG.md")
        + [COURSE / "index.md", COURSE / "src/README.md", COURSE / "refs/README.md",
           COURSE / "refs/lecture-notes-map.md"])
CODE = re.compile(r"`([^`\n]+)`")
PLACEHOLDERS = {"file", "module"}                        # "`file.py::name`" in prose
REPO = COURSE.parents[2]                                 # repo root: shared scripts such as scripts/*.py


def _resolve(module, dotted):
    if str(PY) not in sys.path:
        sys.path.insert(0, str(PY))
    obj = importlib.import_module(module)
    for part in dotted.split("."):
        obj = getattr(obj, part)
    return obj


def _pointers(text):
    for span in CODE.findall(text):
        for mod, dotted in re.findall(r"\b([a-z_][a-z0-9_]*)\.((?:[A-Za-z_]\w*\.)*[A-Za-z_]\w*)", span):
            if mod in MODULES and dotted not in ("py", "sh"):
                yield mod, re.sub(r"\.(py|sh)$", "", dotted)
        for mod, name in re.findall(r"(\w+)\.py::(\w+)", span):
            if mod in MODULES:
                yield mod, name


@pytest.mark.parametrize("doc", DOCS, ids=lambda p: p.name)
def test_pointers_and_links_resolve(doc):
    text = doc.read_text()
    missing = []
    for mod, dotted in _pointers(text):
        try:
            _resolve(mod, dotted)
        except (AttributeError, ModuleNotFoundError):
            missing.append(f"{mod}.{dotted}")
    for span in CODE.findall(text):
        for path in re.findall(r"(?:^|[\s(])((?:\.\./)*[\w./-]+\.(?:py|sh))\b", " " + span):
            name = pathlib.Path(path).name
            if pathlib.Path(name).stem in PLACEHOLDERS:
                continue
            if not ((PY / name).exists() or (COURSE / "refs" / name).exists() or (REPO / path).exists()):
                missing.append(path)
    for link in re.findall(r"\]\(([^)#\s]+)(?:#[^)]*)?\)", text):
        if not link.startswith(("http:", "https:", "mailto:")) and not (doc.parent / link).exists():
            missing.append(f"link {link}")
    assert missing == []


def test_citations_exist():
    register = (COURSE / "refs/SOURCES.md").read_text()
    known = set(re.findall(r"^### (S\d+)\b", register, re.M))
    for doc in DOCS:
        for n in re.findall(r"\bS(\d+)\b", doc.read_text()):
            assert f"S{n}" in known, f"{doc.name} cites S{n}"
