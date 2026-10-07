# refs — 064.004 Awareness and Meditation I

[`SOURCES.md`](SOURCES.md) is the register: one entry `S1 … S13`, each with
title, URL, retrieval date, access status and what it was used for.
[`../notes/README.md`](../notes/README.md) cites it as `[S<n>]`.

## What is here

| file | what it is |
|---|---|
| [`SOURCES.md`](SOURCES.md) | the source register (authoritative) |

That is the whole directory, and the rest of this file says why.

## Nothing is vendored, and there is no `fetch-sources.sh`

The other courses in this semester keep a `fetch-sources.sh` that pulls
cite-only PDFs into a git-ignored `vendor/`. This one does not, because **there
is no PDF to fetch**.

- TISS says, on all four pages that have ever described this course:
  **"No lecture notes are available."** [S1, S2, S3, S4]
- The course names **no literature at all** — no textbook, no paper, no author.
  The optional written scientific work is to use "the literature of current
  meditation research" [S1], and no list is given.
- The lecturer hosts nothing. His group page links only back to TISS [S9]; his
  personal site does not mention meditation [S10].
- VoWi has pages for both Part I and Part II and **both are empty stubs with zero
  attached materials** [S7, S8].
- The one document that governs the course, **`schedule.pdf`**, is in TUWEL
  behind a TU Wien login [S6]. It was **not fetched and must not be** — it needs
  a login and is not ours to redistribute.

So an empty download script would be theatre. Everything this course rests on is
a live public web page, cited in [`SOURCES.md`](SOURCES.md) with a resolvable
URL, or is behind a login and stays there.

## Why there are no notes in the usual sense and no `src/`

064.004 has **mode of examination: immanent** [S1]. There is no written exam, no
oral exam, no test, no exercise sheet and no assignment with a right answer.
What is assessed is: turning up to every compulsory meeting, having prepared for
it, meditating, logging it honestly, and defending the log in a 30-minute final
meeting [S1].

There is consequently nothing to derive, nothing to prove, no protocol, no
algorithm and no reference result to reproduce — so Parts 2 and 3 of the usual
source pass (verify the notes' claims; implement what the sources show the course
covers) have no subject matter. Inventing study material for a meditation
practicum would be worse than useless: it would imply the course can be prepared
for by reading, which is exactly what it is not.

[`../notes/README.md`](../notes/README.md) is therefore not a topic note. It is a
one-page statement of **what the course requires of the student**, with every
requirement traced to [`SOURCES.md`](SOURCES.md).

## Reading order

1. [`../notes/README.md`](../notes/README.md) — the requirements, the deadlines
   and the four ways to fail. Read this before 30.09.2026.
2. [`../docs/tiss.md`](../docs/tiss.md) — the transcription of the 2026W page,
   with a year-on-year comparison table against 2025W, 2024W and the 2023W
   predecessor 194.139.
3. [`SOURCES.md`](SOURCES.md) when you want the wording of a rule rather than the
   summary of it.
4. `../notes/CHANGELOG.md` — what this pass established
   and corrected.
