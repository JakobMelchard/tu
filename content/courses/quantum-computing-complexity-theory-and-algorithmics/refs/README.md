# refs — 192.043 Quantum Computing, Complexity Theory, and Algorithmics

[`SOURCES.md`](SOURCES.md) is the register: one entry `S1 … S61`, each with
title, URL, retrieval date, licence/access status and what it was used for. The
notes cite it inline as `[S<n>]`. **S59–S61 are different in kind** — they are
other institutions' free teaching material, used to build practice for the
blocks this course leaves without any, and they sit in their own section with
their own rules. Never present them as this course's.

## What is here

| file | what it is |
|---|---|
| [`SOURCES.md`](SOURCES.md) | the source register (authoritative) |
| [`lecture-notes-map.md`](lecture-notes-map.md) | the three blocks, who teaches them, when, how each is examined, and the map from source → note → code; also the table of **conventions** the course uses |
| [`fetch-sources.sh`](fetch-sources.sh) | downloads the cite-only PDFs into `vendor/` for personal use |
| `vendor/` | created by the script, **git-ignored**, never committed |

## Nothing is vendored

Every third-party document this course rests on is either a live web page or a
file whose licence is absent or reserved:

- **TISS pages** [S1–S10] are live and change; they are cited, and the 2026W one
  is transcribed into [`../docs/tiss.md`](../docs/tiss.md) with a date.
- **The course has no script.** TISS states "No lecture notes are available."
  [S1]. Of the four lecturers, only **Pichler** hosts anything public
  [S14] — and only the first two decks of a *different* course (181.142), with
  no licence statement; `cc03.pdf` … `cc16.pdf` are 404.
- **[S15–S23]**, the VoWi exercise sheets, programming assignments, exam
  protocols and student summary, are student uploads with no licence. Several
  are derived from TUWEL slides.
- **[S25–S30]** are the six commercial textbooks TISS names; **[S27]**'s free
  precursor and **[S32]**, **[S33]** carry no permission notice; **[S31]** is on
  arXiv under the *non-exclusive distribution licence*, which grants arXiv the
  right to distribute and not us.
- **[S35]–[S58]** are journal and conference papers, most paywalled.
- **[S59]** and **[S61]** are MIT OpenCourseWare pages under **CC BY-NC-SA
  4.0** — the only genuinely re-usable licence in this register. They are still
  not vendored: the exercise folders restate every question in our own words and,
  because they adapt ShareAlike material, **declare themselves CC BY-NC-SA 4.0**.
  **[S60]**, the Arora & Barak draft, says outright "Not to be reproduced or
  distributed without the authors' permission", so its folder's exercises are
  ours, written for theorems the book states.

So `refs/` contains only text written here. Use `fetch-sources.sh` to pull the
PDFs onto your own machine:

```sh
cd ws2026/quantum-computing-complexity-theory-and-algorithmics/refs
./fetch-sources.sh --core     # de Wolf's notes, Pichler's two decks, Egly's four sheets
./fetch-sources.sh            # everything, ~40 files
```

**VoWi runs an Anubis proof-of-work bot gate.** `curl` usually gets an HTML
challenge page instead of the PDF, whatever user agent it sends. The script
reports which files it could not get; open those URLs in a browser and save them
into `vendor/` by hand. (For reading a VoWi PDF programmatically, the working
route is to load the page in a real browser and extract the text with pdf.js
from inside it — that is how S16–S20 were read here.)

## What this pass could and could not establish

**Read this before [`../notes/00-exam-focus.md`](../notes/00-exam-focus.md).**

192.043 is **new in its present form**: 2026W is the first run at 6.0 h / 10.0
ECTS, merging the 7.0 ECTS 192.043 with the 3.0 ECTS preparation course 192.042,
which has no 2026W offering [S1–S4]. It has **no VoWi page, no past paper and no
public slide deck of its own** [S24]. In 2024W it examined with two written
papers in February and March; in 2026W with two mid-term-style papers in
December and January [S1, S3]. Nothing about the 2026W examination can be
checked against a previous instance of *this* course.

What replaces it is the **sibling courses that share 192.043's lecturers and, in
October and November, its actual lecture slots**:

- **192.219** [S5] — the algorithmics block, co-taught with Chen and Pichler in
  the same rooms at the same times, with the same exam slot. This is what makes
  the block structure in [`lecture-notes-map.md`](lecture-notes-map.md)
  something other than a guess, and it is the source that **resolves the
  first-meeting time**.
- **192.036 / 192.070** [S6, S15–S21] — Egly's own quantum courses. Four
  exercise sheets, three programming assignments, an exercise-test protocol, an
  oral-exam protocol and a 21-page student summary of the lectures are public.
  They give the **lecture order**, the **conventions** (qubit ordering, the
  non-standard $R_x$, the diffusion identity, the Grover count, the QFT bit
  order) and **real questions**.
- **192.165 / 181.142** [S7, S8, S14, S23] — Pichler's complexity course: his
  own topic list, two slide decks, and the format of his written and admission
  tests.
- **194.027** [S10, S22] — De Maio's hybrid course, the origin of the
  variational bullet.

**The one thing sourcing could not establish is which lecturer takes which
block** in the strict sense. The attribution is an inference chain, spelled out
with its evidence in [`lecture-notes-map.md`](lecture-notes-map.md);
**Fermüller's role is genuinely unknown**.

## What the sources changed

The largest single effect of this pass was not new topics — the notes already
matched the TISS bullet list — but **conventions and verification**:

1. Egly's sheets fix a **qubit ordering** ($t\otimes i_1\otimes i_0$,
   $|z_{n-1}\cdots z_0\rangle$) that happens to agree with the simulator in
   `src/py/quantum/sim.py`, and a **rotation gate that is not Qiskit's**
   [S16]. His programming exercise 2 prints the *same gate* in both his order
   and Qiskit's, which is the cleanest available statement of the endianness
   trap [S17].
2. Running every table in the notes through numpy found **six numerical
   errors** that had survived two readings. They are listed in
   `../notes/CHANGELOG.md`.

## Reading order

1. [`../notes/00-exam-focus.md`](../notes/00-exam-focus.md) — what is known and
   what is inferred about the two exams, and the real questions from the sibling
   courses.
2. [`lecture-notes-map.md`](lecture-notes-map.md) — the block structure and the
   conventions table.
3. [`../notes/README.md`](../notes/README.md) — the 22 topic notes, then
   [`../notes/01-practice-set-substitute-sources.md`](../notes/01-practice-set-substitute-sources.md)
   for the practice set built from S59–S61.
4. **[S31]** (de Wolf) for the C-series and B06, and **[S25]** (Kleinberg &
   Tardos) for the A-series: those are the two texts that carry the most weight
   where the course itself is silent.
