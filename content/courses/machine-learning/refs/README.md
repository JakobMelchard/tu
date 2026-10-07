# refs — 184.702 Machine Learning

[`SOURCES.md`](SOURCES.md) is the register: one entry per source, `S1 … S43`
(no S19 — it was withdrawn), each with title, authors, URL, retrieval date,
licence/access status and what it was used for. The notes cite it inline as
`[S<n>]`, optionally with a locator such as `[S21 §2.4]`. Every entry is cited
somewhere; entries that support nothing are removed.

## What is here

| file | what it is |
|---|---|
| [`SOURCES.md`](SOURCES.md) | the source register (authoritative) |
| [`lecture-notes-map.md`](lecture-notes-map.md) | the lecture's unit order → our notes → our code, and what each unit is examined on |
| [`fetch-sources.sh`](fetch-sources.sh) | downloads the cite-only PDFs into `vendor/` for personal use |
| `vendor/` | created by the script, **git-ignored**, never committed |

## Access state, 2026-09-27

- **S1** (TISS 2026W) was re-read on 2026-09-27 in a logged-in browser: no
  field changed since the 2026-09-22 fetch.
  [`../docs/tiss.md`](../docs/tiss.md) carries the re-read date.
- **TUWEL**: the course runs there from 01.10.2026 [S1]. The slides,
  recordings, forum and exercise submission were not read for these notes, so
  the "TUWEL-only" statements below describe where material lives, not
  something verified here.


## Nothing is vendored

Every third-party document this course rests on is either a live web page or a
file with no redistribution licence:

- **This course has no public lecture script at all.** TISS states "No lecture
  notes are available." [S1], the material is TUWEL-only, and none of the five
  lecturers hosts slides on a personal or institute page [S5–S9]. That is the
  single most important negative result of this pass: unlike other courses in
  this repo there is no author-hosted PDF to build on.
- **S12–S17, S43**, the VoWi exam archive, formula sheet, how-tos, assignment
  sheet and question catalogues, are student uploads with no licence, several of
  them containing screenshots of the TUWEL slides.
- **S18** and **S20** are student GitHub summaries; only one carries a licence
  (AGPL-3.0), and that licence cannot clear the underlying slides.
- **S21, S23, S24, S26, S28** are books whose authors host a free PDF but
  reserve all rights; **S22, S25, S27** are commercial; **S29–S41** are journal
  or conference papers, most paywalled.

So `refs/` contains only text written here. Use `fetch-sources.sh` to pull the
PDFs onto your own machine.

```sh
cd refs && ./fetch-sources.sh    # from the course folder
```

**VoWi runs an Anubis proof-of-work bot gate.** `curl` gets an HTML challenge
page instead of the PDF, whatever user agent it sends. The script tries anyway
and tells you which files it could not get; open those URLs in a browser and
save them into `vendor/` by hand. (For reading a VoWi PDF programmatically, the
working route is to load the page in a real browser and extract the text with
pdf.js from inside it — that is how S12–S16 and S43 were read here.)

## Reading order

1. [`../notes/00-exam-focus.md`](../notes/00-exam-focus.md) — 19 past papers
   digested, with the format, the marking scheme and the recurring question
   bank. **Read this first**; for this course the exam archive *is* the
   syllabus, because there is no script.
2. [`lecture-notes-map.md`](lecture-notes-map.md) — which lecture unit each note
   corresponds to, and how heavily each is examined.
3. [`../notes/README.md`](../notes/README.md) — the notes.
4. **S21** (Sutton & Barto, chapters 2 and 5) for reinforcement learning and
   **S26** (chapter 9) for convolutional networks — the two units where the
   notes rest on a book rather than on the exam archive, because the archive
   only shows the questions and not the treatment.

## Provenance of the exam archive

Everything in `00-exam-focus.md` comes from three layers, and the notes say
which layer a claim sits on:

| layer | what it is | how much to trust it |
|---|---|---|
| **questions** | 17 VoWi transcript pages [S11] + 2 more in [S18] | written from memory days after the exam; wording is approximate, the *topics* are reliable, and questions repeat across years |
| **answers** | the 24-page catalogue [S12], the older catalogue [S43], and [S18]'s per-question commentary | students' answers, explicitly disclaimed. Where two of them disagree, or where they disagree with a textbook, `00-exam-focus.md` flags it |
| **conventions** | the formula sheet [S13] and the how-tos [S14] | closest thing to the lecturers' own material; both are slide-derived. Use these for *notation and marking conventions*, which is what hand calculations are graded on |

## Checksums

Files worth re-checking before an exam, as fetched on 2026-09-22 (sizes from
VoWi's `imageinfo` API; run `shasum -a 256 vendor/*` after `fetch-sources.sh`
to record your own):

```
S12  Questions previousExams answered2024S.pdf   6 776 004 bytes   24 pages
S13  Formlen ML.pdf                              1 044 096 bytes    9 pages
S14  PracticalHowTos.pdf                           252 153 bytes    4 pages
S15  Exercise1 ML 2021S.pdf                         64 006 bytes    4 pages
S16  Exam 2026-06-23 Part2.1.pdf                    167 361 bytes    2 pages
S43  Fragenkatalog 2019S.docx                       121 132 bytes
```
