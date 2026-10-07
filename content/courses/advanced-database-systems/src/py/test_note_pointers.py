"""Every code pointer and relative link in the notes and READMEs resolves."""
import importlib
import re
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
COURSE = HERE.parents[1]
DOCS = sorted((COURSE / "notes").glob("*.md")) + [
    COURSE / "src" / "README.md", COURSE / "refs" / "lecture-notes-map.md",
    COURSE / "refs" / "README.md", COURSE / "refs" / "SOURCES.md", COURSE / "index.md"]
MODULES = {p.stem for p in HERE.glob("*.py") if not p.stem.startswith(("test_", "conftest"))}
TESTS = "\n".join(p.read_text() for p in HERE.glob("test_*.py"))


def pointers():
    for doc in DOCS:
        for tok in re.findall(r"`([^`\n]+)`", doc.read_text()):
            yield doc.name, tok


@pytest.mark.parametrize("doc,tok", [
    (d, t) for d, t in pointers()
    if re.fullmatch(r"[a-z_]+(\.[A-Za-z_]+)+", t) and t.split(".")[0] in MODULES
    and not t.endswith(".py")])
def test_module_attribute_exists(doc, tok):
    mod, *attrs = tok.split(".")
    obj = importlib.import_module(mod)
    for a in attrs:
        obj = getattr(obj, a)


@pytest.mark.parametrize("doc,tok", [
    (d, t) for d, t in pointers() if re.fullmatch(r"(py/)?[a-z_]+\.py", t)])
def test_file_exists(doc, tok):
    assert (HERE / tok.removeprefix("py/")).exists(), f"{doc}: {tok}"


@pytest.mark.parametrize("doc,tok", [
    (d, t) for d, t in pointers() if re.fullmatch(r"test_[a-z_0-9]+", t)])
def test_named_test_exists(doc, tok):
    assert f"def {tok}(" in TESTS or (HERE / f"{tok}.py").exists(), f"{doc}: {tok}"


def links():
    for doc in DOCS:
        for target in re.findall(r"\]\(([^)#\s]+)(?:#[^)]*)?\)", doc.read_text()):
            if not target.startswith(("http://", "https://", "mailto:")):
                yield doc, target


@pytest.mark.parametrize("doc,target", list(links()), ids=lambda x: str(x)[-40:])
def test_relative_link_resolves(doc, target):
    assert (doc.parent / target).exists(), f"{doc.name}: {target}"
