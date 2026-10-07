# refs — 194.077 Applied Deep Learning

[`SOURCES.md`](SOURCES.md) is the register: one entry `S1 … S97`, each with
title, authors, URL, retrieval date, licence/access status and what it was used
for. The notes cite it as `[S<n>]`.

## What is here

| file | what it is |
|---|---|
| [`SOURCES.md`](SOURCES.md) | the source register (authoritative) |
| [`lecture-notes-map.md`](lecture-notes-map.md) | the 2025W lecture list, chapter by chapter, mapped onto our notes and code, with the gaps named |
| [`fetch-sources.sh`](fetch-sources.sh) | downloads the cite-only PDFs and the lecture captions into `vendor/` for personal use |
| `vendor/` | created by the script, **git-ignored**, never committed |

## Nothing is vendored

Every third-party document this course rests on is either a live web page, a
YouTube video, or a PDF with no redistribution licence:

- **S4–S7**, the lecture videos, are under the standard YouTube licence.
- **S12/S13/S14**, the assignment sheets, are the lecturers' own documents
  uploaded by a student to VoWi; no licence is stated, so all rights are
  reserved. Nothing from them is reproduced verbatim in this repo —
  [`../notes/00-exam-focus.md`](../notes/00-exam-focus.md) describes them in our
  own words, which is what the course conventions require.
- **S15/S16** are free-to-read but copyrighted books (MIT Press).
- No TUWEL or ILEA material was fetched. TUWEL needs a login, the submission
  portal is not ours to copy, and the slide decks themselves are not public —
  only the recordings of them are.

So `refs/` contains only text written here.

```sh
cd refs && ./fetch-sources.sh    # from the course folder
```

The script needs `yt-dlp` for the captions (`brew install yt-dlp`); everything
else is `curl`. It downloads **text only** — captions and descriptions, not
video.

## This course is unusual: read the primary material, it is all public

Most TU Wien courses hide their material in TUWEL and leave you reconstructing
the syllabus from VoWi exam transcripts. This one does not.

1. **Watch [S5], Lecture 0, once, before you register** (17 minutes). It is the
   contract: five graded parts, five criteria, four project types, four-minute
   presentation, ~60–70 student cap, bring your own GPU.
2. **Read [S12], [S13], [S14]**, the three assignment sheets, at the start —
   not one at a time. Assignment 3 tells you in week one that you will have to
   ship a *demo application*, which changes what you pick in assignment 1.
3. [`../notes/00-exam-focus.md`](../notes/00-exam-focus.md) — what is assessed,
   how the 50 points are allocated, and what "code quality" concretely means
   here. **There is no written exam.**
4. [`../notes/README.md`](../notes/README.md) — the notes, ordered by the
   lecture they belong to.
5. **[S4]**, the lecture playlist, for the topic your project uses. Note the
   scheduling trap [S5]: Explainable AI and Graph Neural Networks are lectures
   10 and 11, i.e. *after* assignment 2 is due. If your project needs them,
   watch last year's recordings early — they are all still online.

## Provenance of the deadlines

The dates in [S12], [S13], [S14] are **2025W dates** (21.10.2025, 16.12.2025,
13.01.2026). They are recorded because they establish the *pattern* — each
deadline is the day before a lecture, and the last one is the day before the
first presentation slot [S5]. They are **not** the 2026W dates. The 2026W dates
are announced in the preliminary lecture on 07.10.2026 and in ILEA/TUWEL;
[`../notes/00-exam-focus.md`](../notes/00-exam-focus.md) gives the dates the
pattern implies and labels them as inferred.
