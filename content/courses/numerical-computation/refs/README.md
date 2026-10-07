# refs: 101.973 Numerical Computation

[`SOURCES.md`](SOURCES.md) is the register: one entry `S1 … S20`, each with
title, authors, URL, retrieval date, licence/access status and what it was used
for. The notes cite it as `[S<n>]`.

## What is here

| file | what it is |
|---|---|
| [`SOURCES.md`](SOURCES.md) | the source register (authoritative) |
| [`lecture-notes-map.md`](lecture-notes-map.md) | section-by-section map of S4 → our notes → our code, with the `(CSE)` markers |
| [`fetch-sources.sh`](fetch-sources.sh) | downloads the cite-only PDFs into `vendor/` for personal use |
| `vendor/` | created by the script, **git-ignored**, never committed |

## Nothing is vendored

Every third-party document this course rests on is either a live web page or a
PDF with no redistribution licence:

- **S4**, the course's own lecture notes (Melenk & Faustmann, WS 2023/24), is a
  free public download from the lecturer's TU Wien page but carries no licence
  statement, so by default all rights are reserved.
- **S10/S11**, the past test papers on VoWi, are student uploads of exam papers.
- **S12/S15/S16/S19** are commercial textbooks; **S13** is under ACM copyright;
  **S17** carries no permission notice; **S18** is "Copyright © 2003 by SIAM".

So `refs/` contains only text written here. Use `fetch-sources.sh` to pull the
PDFs onto your own machine.

`vendor/` is git-ignored, so S4 is only available locally after running the
script. The 2026W TUWEL course (id 82717), where TISS promises lecture notes
[S1], was not read for these notes.

```sh
cd refs && ./fetch-sources.sh    # from this course folder
```


Checksum of the one file everything depends on, so you can tell whether the
lecturer has replaced it since 2026-09-21:

```
sha256  292bafb0ab46cb47a6ab4374dba1ae60ffa3a2dba50f660510b883da687d7d61
bytes   3818269
pages   160
```

## Reading order

1. **S4** cover to cover: it *is* the course. `lecture-notes-map.md` says which
   sections the CSE variant adds on top of the Visual Computing one.
2. [`../notes/00-exam-focus.md`](../notes/00-exam-focus.md): what five past
   tests actually asked, with the term each item comes from.
3. [`../notes/README.md`](../notes/README.md): the notes, in S4's chapter order.
