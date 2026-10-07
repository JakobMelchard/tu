# refs: 183.663 / 193.200 Deep Learning for Visual Computing

[`SOURCES.md`](SOURCES.md) is the register: `S1 ... S45`, each with URL,
retrieval date, access status and what it supports. The notes cite it inline
as `[S<n>]`.

| file | what it is |
|---|---|
| [`SOURCES.md`](SOURCES.md) | the source register (authoritative) |
| [`lecture-notes-map.md`](lecture-notes-map.md) | TISS subject items and the 2016W lecture order mapped to notes and code; exercise history |
| [`fetch-sources.sh`](fetch-sources.sh) | downloads the free PDFs into `cite-only/` for personal use |
| `cite-only/` | created by the script, **git-ignored** ([`.gitignore`](.gitignore)), never committed |

## Access state, 2026-09-28

- **TISS**: 183.663 2025S read (transcribed in [`../docs/tiss.md`](../docs/tiss.md));
  **193.200 2026S read in an unauthenticated browser** [S3]; 2027S of both numbers
  redirects to the login, 183.663 2026S is "not public" [S2].
- **CVL homepage** [S4]: course number 193.200, grading, compute options,
  "no recordings". **No slides, no exercise descriptions, no dates.** The
  lead lecturer's homepage lists no teaching [S31]. So there is no
  author-hosted current material.
- **TUWEL**: nothing there was checked or fetched.
- **Public exam material**: the 2017 catalogue and 2016W slides on GitHub
  [S9]; the 2020 and 2022S catalogues with student answers on VoWi [S7, S8];
  an SS21 transcript [S6]. These are the basis of
  [`../notes/00-exam-focus.md`](../notes/00-exam-focus.md).

## Nothing is vendored

No file in this directory is third-party. The candidates and why none qualifies:

- **S9** (2016W slides, 2017 catalogue): public GitHub repository without a licence.
- **S7, S8** (VoWi): student uploads, no licence, built on TUWEL material.
- **S13-S41 papers**: arXiv's default non-exclusive licence or publisher PDFs; free to read, not to redistribute.
- **S11** is HTML-only by contract with MIT Press; **S42** allows personal download, not reposting.

Run the script to get a local copy:

```sh
cd refs && ./fetch-sources.sh   # from the course folder; ~220 MB, 54 files, ~30 s
```

**VoWi runs a proof-of-work bot gate**, so S7 and S8 fail with curl; the
script prints their URLs. They were read on 2026-09-28 in a browser by loading
the file page and extracting the text with pdf.js from inside it.

## Reading order

1. [`../notes/00-exam-focus.md`](../notes/00-exam-focus.md): course status and the question bank.
2. S9 `exam-questions.pdf` (7 pages): the original catalogue, still the backbone of 2022S.
3. [`lecture-notes-map.md`](lecture-notes-map.md), then the notes in order.
4. Goodfellow et al. ch. 6, 7, 8, 9 [S11] alongside notes 02-04 and 08.
