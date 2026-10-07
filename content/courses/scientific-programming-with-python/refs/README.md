# refs — 191.125 Scientific Programming with Python

[`SOURCES.md`](SOURCES.md) is the register: one entry `S1 … S43`, each with
title, URL, retrieval date, licence/access status and what it was used for. The
notes cite it as `[S<n>]`. `S41`–`S43` are the **substitute practice sources**
added when it became clear that this course publishes no exercise sheet and no
past paper — see below.

## What is here

| file | what it is |
|---|---|
| [`SOURCES.md`](SOURCES.md) | the source register (authoritative) |
| [`docs-map.md`](docs-map.md) | note section → the exact versioned documentation page that backs it → the code that exercises it |
| [`fetch-sources.sh`](fetch-sources.sh) | downloads the two CC BY 4.0 books into the git-ignored `vendor/` |
| `vendor/` | created by the script, **git-ignored**, never committed |

## Nothing is vendored — and for once, not because of licences

The two other sourced courses in this repo vendor at opposite extremes:
`numerical-computation` vendors nothing because its one load-bearing PDF has no
licence statement, and `introduction-to-networking` vendors 52 RFCs because the
IETF Trust explicitly permits it. This course is a third case.

Here the load-bearing sources are **library reference documentation** —
NumPy 2.5, SciPy 1.18, pandas 3.0, Matplotlib 3.11.2, CPython 3.12, pytest 9.1,
PuLP 4.0 (versions as of 2026-09-27, [S40]). They are all BSD/MIT/PSF-licensed and could legally be copied. They
are not, for three reasons:

1. **A vendored copy is a fork of the truth.** These pages are the source *and*
   the thing being documented. The version that matters is the one installed in
   `.venv`, and a stale HTML copy in `refs/` would drift away from it silently.
2. **The pin does the job a copy would.** Every citation in `SOURCES.md` points
   at the documentation build for the installed version — `numpy.org/doc/2.5/`,
   not `numpy.org/doc/stable/`. Those URLs are immutable once published.
3. **The executable check does the rest.**
   [`../src/py/test_doc_examples.py`](../src/py/test_doc_examples.py) re-derives
   in the venv every documented behaviour a note depends on. If NumPy, pandas or
   PuLP change it, the test suite says so, which no vendored HTML tree would.
   PuLP did, when the venv was re-created on 2026-09-27 (3.3.2 to 4.0.0): three
   tests failed and named the claims in note 07 §7 that had gone stale.

Four sources here *are* freely redistributable in the strong sense and are still
not vendored, deliberately:

- **[S38] Sundnes, *Introduction to Scientific Programming with Python*** —
  Springer open access, **CC BY 4.0**, stated per chapter. 148 pages, 1.8 MB.
- **[S39] *Scientific Python Lectures*** — **CC BY 4.0**, stated in the
  repository's `LICENSE.md`. Release 2024.1 PDF is 18 MB.
- **[S41] Aalto, *Python for Scientific Computing*** — the repository `LICENSE`
  reads, in full, "Creative Commons Attribution 4.0".
- **[S42] Software Carpentry, *Programming with Python*** — instructional
  material **CC BY 4.0**, example code **MIT**, © The Carpentries.

[S41] and [S42] are living sites with no tagged release, so a copy would be a
fork of something that moves. Instead, every task adapted from them was
**restated in our own words and reimplemented** in
`../src/exercises/`, with the institution, course, year and
licence at the top of each directory's `README.md`, and datasets that would have
needed downloading replaced by seeded generators.

Both could be committed with attribution. They are not, because neither is
course material: **TISS names no literature at all**, in any of the six
offerings, and both books are supplements chosen here rather than assigned.
Copying 20 MB of someone else's teaching text into a 2 ECTS course folder buys
nothing that a link and a fetch script do not. Get them with:

```sh
cd refs && ./fetch-sources.sh    # from the course folder
```

Everything with a restrictive licence is cite-only and *cannot* be vendored:
[S35] Amdahl 1967 and [S36] Gustafson 1988 are ACM copyright, [S37]
Dormand & Prince 1980 is Elsevier.

## What sourcing this course could *not* establish

Read this before [`../notes/00-exam-focus.md`](../notes/00-exam-focus.md).

191.125 has run six times (2021W–2026W) with the same lecturer, Sascha Hunold,
and a predecessor number 191.116 in 2019W/2020W [S1]–[S7]. Despite that history:

- **No public course material exists.** TISS's literature field says "No lecture
  notes are available" in every single offering [S1]–[S7]. The only course
  homepage the lecturer ever published — for 191.116 in 2019W, now reachable
  only through the Internet Archive — states in full: *"All material will be
  published on TUWEL"* [S8]. The Wayback Machine has no page at all for 191.125.
- **VoWi has nothing.** The page exists, but every section reads "noch offen"
  and it has no attachments [S9]. A full-text VoWi search for the lecturer's
  name returns that one page.
- **No past paper, no grading scheme, no exercise sheet is public.** The
  weighting between Part 1 (exercises) and Part 2 (written exam) is not stated
  anywhere outside TUWEL, and TUWEL was not read for these notes. The TUWEL course opens
  01.10.2026 [S1]; what it contains is unverified.

So the usual highest-value source of this pass (the lecturer's own notes and
old papers) does not exist, and TUWEL is off limits. What replaces it:

1. **The TISS diff across six years**, which is the only hard evidence about the
   examination, and which does show a real change in 2024W (multiple choice was
   added, and the lecture period was cut from the full semester to eight weeks).
   The 2026W page was re-read on 2026-09-27 and no field had changed: deregistration until 20.10.2026, exams 19.01.2027 and
   23.02.2027 [S1]. That is in [`../docs/tiss.md`](../docs/tiss.md) and
   [`../notes/00-exam-focus.md`](../notes/00-exam-focus.md).
2. **Version-pinned primary documentation** for every library claim, so that the
   notes describe the NumPy/pandas/PuLP the reader actually has rather than the
   one the writer remembered.
3. **Substitute practice material**, added 2026-09-22: three free CC BY 4.0
   courses [S39], [S41], [S42] reworked into
   `../src/exercises/`, plus a bank of 24 multiple-choice
   items [S43] whose correct answers are **derived by executing the library
   behaviour** rather than asserted. Written up in
   [`../notes/11-practice-set.md`](../notes/11-practice-set.md). **None of it is
   TU Wien material**, and every item says which it is.

## Reading order

1. [`../notes/00-exam-focus.md`](../notes/00-exam-focus.md) — what is known and
   what is inferred about the examination, and how much weight to give each.
2. [`../notes/README.md`](../notes/README.md) — the ten topic notes in the order
   of the TISS subject list.
3. [`../notes/11-practice-set.md`](../notes/11-practice-set.md) — the practice
   set, and the list of TISS topics for which **no** good free practice material
   exists.
4. [`docs-map.md`](docs-map.md) when a note cites `[S<n>]` and you want the
   paragraph: it names the exact page and section.
