# AGENTS.md

Instructions for LLM agents working on this repository. This is an LLM-maintained
wiki: raw sources are registered and cited, the notes are the compiled
knowledge, and every change keeps the two in sync. Humans review every change
through a pull request. Read [CONTRIBUTING.md](CONTRIBUTING.md) as well; its
rules apply to you.

## Schema

One folder per course, `content/courses/<slug>/`. Copy
[`templates/course/`](templates/course/) to start one.

| path | role |
|---|---|
| `index.md` | course page; frontmatter `title: "<number> <title>"`, `tags: [cse or qist, <semester>]` |
| `notes/README.md` | ordered index of the notes, one line per note |
| `notes/00-exam-focus.md` | exam format, past papers, what is asked |
| `notes/NN-topic.md` | one topic per note, numbered in lecture order |
| `refs/SOURCES.md` | source register; entries `S1`, `S2`, ... with URL, retrieval date, licence, use |
| `refs/README.md` | what is in `refs/` and the licence reasoning for vendored files |
| `refs/fetch-sources.sh` | optional; re-fetches vendored files |
| `docs/tiss.md` | dated transcription of the public TISS course page |
| `docs/tiss-api.xml`, `docs/tiss-api.md` | TISS API record, `https://tiss.tuwien.ac.at/api/course/<nr without dot>-<semester>` (XML) and its rendering |
| `src/py/` | Python reference code; tests in `test_*.py` |
| `src/c/`, `src/cpp/` | optional; Makefile with a `test` target |

The sources are the ground truth, the notes are derived. Never edit a note in a
way its cited sources do not support.

## Operations

### Ingest

A new source arrives (URL, paper, standard, TISS update).

1. Check its licence. Add an entry `S<next>` to the course's `refs/SOURCES.md`:
   title, URL, retrieval date, licence, what it is used for. Vendor the file
   into `refs/` only if the licence allows redistribution.
2. Read it and update every affected note, citing `[S<n>]` on each claim it
   supports. Fix claims it contradicts and say so in the note.
3. A TISS update is transcribed into `docs/tiss.md` with the retrieval date.
4. List the new source and the touched notes in the pull request description.

### Query

Answer questions from the notes, with their `[S<n>]` citations. If the notes do
not cover it, say so and name the source that would. An answer worth keeping
becomes a new note (`notes/NN-topic.md`) linked from `notes/README.md`.

### Lint

Run `python3 scripts/check.py` (broken links, personal data, citations missing
from `SOURCES.md`) and `uv run pytest content/courses/<slug>/src -q`. Also look
for contradictions between notes, stale dates and notes without code pointers.
Fix what you find or report it in the pull request.

## Flashcards

A card is a fenced block inside a note, written by hand:

````
```card id=<course-prefix>-<topic>
front
---
back
```
````

Ids are unique across the repository and stable: the id carries the card's
review history in [drill](https://github.com/JakobMelchard/drill), so never
rename or reuse one. Math with `$...$` works.

## TODO

- Generate `content/llms.txt` and `content/llms-full.txt` from the course
  folders at build time. The old hand-exported copies were removed because
  they pointed at the previous `cse/` and `qist/` layout.

## Rules

- English prose. Keep German TISS titles verbatim.
- No em dashes.
- Never invent a source, URL, date, page number or quotation. If unsure, leave
  it out.
- Date every TISS transcription (`Transcribed from <url> on YYYY-MM-DD`).
- No copyrighted material copied in; cite-only where the licence forbids
  redistribution. No content from TUWEL or other login-protected pages.
- No personal data: no registration status, accounts, grades, timetable plans.
- No solutions to currently graded assignments.
- Tests must not need network access.
- The human who opens the pull request is responsible for it; make their review
  easy: small diffs, every claim cited.
