# Contributing

Corrections, new sources, new notes and new courses are welcome. Everything
goes through a pull request.

## Propose a change

1. Fork the repository and create a branch: `git switch -c fix/crypto-note-05`.
2. Make the change, preview it, run the checks (below).
3. Open a pull request against `main` and fill in the template.

Small fixes (a typo, a wrong formula) can also be reported as an issue: use the
"Error in a note" form.

## Course layout

Each course lives in `content/courses/<slug>/`. Start a new one by copying
[`templates/course/`](templates/course/).

```
content/courses/<slug>/
  index.md            frontmatter: title "<number> <title>", tags [cse|qist, <semester>]
  notes/
    README.md         ordered index of the notes, one line per note
    00-exam-focus.md  exam format, past papers, what is actually asked
    NN-topic.md       one note per topic, numbered in lecture order
  refs/
    SOURCES.md        source register: S1, S2, ... each with URL, retrieval
                      date, licence, what it is used for
    README.md         what is in refs/ and why
    fetch-sources.sh  optional: re-fetches vendored files
    ...               vendored files, only when their licence allows it
  docs/
    tiss.md           transcription of the public TISS course page, dated
    tiss-api.xml      raw record from https://tiss.tuwien.ac.at/api/course/<nr without dot>-<semester>
    tiss-api.md       readable rendering of that record
  src/
    py/               Python reference code, tests in test_*.py (pytest)
    c/ or cpp/        optional, with a Makefile that has a `test` target
```

Notes are in English, use LaTeX math (`$...$`, `$$...$$`), and point to the
reference code that implements them. German TISS titles stay as they are. No
em dashes.

## Citations

- Every claim taken from a source cites it as `[S<n>]`, where `S<n>` is an
  entry in that course's `refs/SOURCES.md`. Add the entry first.
- Never invent a source. If you cannot find where a claim comes from, mark it
  or leave it out.
- Do not copy copyrighted material in. Lecture slides, past papers, textbooks
  and TUWEL content are cite-only: summarise in your own words and cite. Vendor
  a file into `refs/` only when its licence allows redistribution, and record
  that licence in `SOURCES.md`.

## Privacy

No personal data, yours or anyone else's: no registration status, account
details, grades, timetable plans or names of fellow students. Lecturers are
named only as they appear on the public TISS page.

## Exercise sheets

Do not post solutions to assignments that are currently graded. Worked
examples, past exam questions the course itself publishes, and solutions to
sheets of past semesters that are no longer graded are fine.

## Flashcards

A flashcard is a fenced block written by hand inside a note:

````
```card id=crypto-perfect-secrecy
When is a scheme perfectly secret?
---
When $\Pr[M=m \mid C=c] = \Pr[M=m]$ for all $m$ and $c$.
```
````

The id is `<course-prefix>-<topic>`. Ids must be unique across the whole
repository and must never change: the id carries a card's review history in
the [drill](https://github.com/JakobMelchard/drill) tool. Math with `$...$`
works on both sides.

## Preview and checks

```sh
npm ci
npx quartz build --serve                         # preview at http://localhost:8080
python3 scripts/check.py                         # links, privacy, citations
uv sync
uv run pytest content/courses/<slug>/src -q      # tests of one course
make -C content/courses/<slug>/src/cpp test      # if the course has C/C++ code
```

CI runs the same checks on every pull request.

## AI-assisted contributions

Contributions written with LLM agents are welcome; [AGENTS.md](AGENTS.md)
tells your agent how this wiki works. You are responsible for what you submit:
check every claim against its cited source and run the checks before opening
the pull request.

## Licence

By contributing you agree that your prose is released under CC BY-SA 4.0 and
your code under MIT, see [LICENSE.md](LICENSE.md).
