"""Every code pointer in the notes resolves (conventions: "pointers to the
reference implementation (`src/py/foo.py`, function name)").

Checks, over notes/*.md (not the CHANGELOG, which quotes old names on
purpose), the course index.md, src/README.md, the exercise
READMEs, refs/README.md and refs/standards-map.md: backticked `module.name` (and `module.Class.name`)
references for every module under src/py and src/exercises/*, `file.py::name`
references, backticked .py/.sh paths, and relative Markdown links.  Offline:
it only imports our own modules and reads files.
"""
import importlib
import pathlib
import re
import sys

import pytest

COURSE = pathlib.Path(__file__).resolve().parents[2]
CODE_DIRS = [COURSE / "src/py", *sorted(p for p in (COURSE / "src/exercises").iterdir() if p.is_dir())]
MODULES = {f.stem: d for d in CODE_DIRS for f in d.glob("*.py")}
DOCS = (sorted(p for p in (COURSE / "notes").glob("*.md") if p.name != "CHANGELOG.md")  # history
        + [COURSE / "index.md", COURSE / "src/README.md", COURSE / "src/exercises/README.md",
           COURSE / "refs/README.md", COURSE / "refs/standards-map.md"]
        + sorted((COURSE / "src/exercises").glob("*/README.md")))
CODE = re.compile(r"`([^`\n]+)`")
PLACEHOLDERS = {"file", "module", "foo"}                  # e.g. "`file.py::name`" in prose


def _resolve(module, dotted):
    sys.path[:0] = [str(d) for d in CODE_DIRS if str(d) not in sys.path]
    obj = importlib.import_module(module)
    for part in dotted.split("."):
        obj = getattr(obj, part)
    return obj


def _pointers(text):
    for span in CODE.findall(text):
        if "==" in span or span.endswith(".rst"):         # Wireshark filters, CNP3 file names
            continue
        for mod, dotted in re.findall(r"\b([a-z_][a-z0-9_]*)\.((?:[A-Za-z_]\w*\.)*[A-Za-z_]\w*)", span):
            if mod in MODULES and dotted not in ("py", "sh"):
                yield mod, re.sub(r"\.(py|sh)$", "", dotted)
        for mod, name in re.findall(r"(\w+)\.py::(\w+)", span):
            if mod not in PLACEHOLDERS:
                yield mod, name


@pytest.mark.parametrize("doc", DOCS, ids=lambda p: p.name)
def test_code_pointers_resolve(doc):
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
            if not any((d / name).exists() for d in CODE_DIRS + [COURSE / "src/sh", COURSE / "refs"]):
                missing.append(path)
    for link in re.findall(r"\]\(([^)#\s]+)(?:#[^)]*)?\)", text):
        if not link.startswith(("http:", "https:", "mailto:")) and not (doc.parent / link).exists():
            missing.append(f"link {link}")
    assert missing == []
