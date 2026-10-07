#!/usr/bin/env python3
"""Lint the wiki content: relative links, personal data, citations.

Fails (exit 1) on broken relative links and privacy matches.
Citations [Sn] missing from the course's refs/SOURCES.md are warnings only.
"""
import argparse
import re
import sys
from pathlib import Path
from urllib.parse import unquote

LINK = re.compile(r"!?\[[^\]]*\]\(\s*<?([^)\s>]+)>?(?:\s+\"[^\"]*\")?\s*\)")
SCHEME = re.compile(r"^[a-zA-Z][a-zA-Z0-9+.-]*:")
PRIVACY = re.compile(
    r"registered since|and registered|user's|TISS favourites|favourites group|suspended|\bclash|preregistered"
    r"|green tick|hourglass since|TISS hourglass|deregistered|~/Workspaces|lilfeelz",
    re.IGNORECASE,
)
PRIVACY_CS = re.compile(r"/Users/")
CITE = re.compile(r"\[(S\d+[a-z]?\b[^\]]*)\]")
SNUM = re.compile(r"\bS(\d+[a-z]?)\b")
ENTRY = re.compile(r"^\s*(#+|[-*]|\d+\.)\s")


def link_ok(md: Path, target: str, root: Path) -> bool:
    path = unquote(target.split("#", 1)[0])
    if not path:
        return True
    p = (root / path.lstrip("/")) if path.startswith("/") else (md.parent / path)
    return p.exists() or p.with_name(p.name + ".md").exists()


def sources_of(md: Path) -> Path | None:
    """refs/SOURCES.md of the course a notes/ file belongs to."""
    for d in md.parents:
        if d.name == "notes":
            return d.parent / "refs" / "SOURCES.md"
    return None


def defined(sources: Path) -> set[str]:
    lines = sources.read_text(encoding="utf-8").splitlines()
    return {n for l in lines if ENTRY.match(l) for n in SNUM.findall(l)}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("root", nargs="?", default="content", type=Path)
    args = ap.parse_args()

    errors, warnings = [], []
    cache: dict[Path, set[str]] = {}
    for md in sorted(args.root.rglob("*.md")):
        src = sources_of(md)
        known = None
        if src:
            if src not in cache:
                cache[src] = defined(src) if src.exists() else set()
            known = cache[src]
        fence = False
        for i, line in enumerate(md.read_text(encoding="utf-8").splitlines(), 1):
            loc = f"{md}:{i}"
            if PRIVACY.search(line) or PRIVACY_CS.search(line):
                errors.append(f"{loc}: privacy: {line.strip()}")
            if line.lstrip().startswith(("```", "~~~")):
                fence = not fence
            if fence:
                continue
            for t in LINK.findall(line):
                if not (SCHEME.match(t) or t.startswith("#") or link_ok(md, t, args.root)):
                    errors.append(f"{loc}: broken link: {t}")
            if known is not None:
                for c in CITE.findall(line):
                    for n in SNUM.findall(c):
                        if n not in known:
                            warnings.append(f"{loc}: S{n} not in {src}")

    for w in warnings:
        print(f"warning: {w}")
    for e in errors:
        print(f"error: {e}")
    print(f"{len(errors)} errors, {len(warnings)} warnings")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
