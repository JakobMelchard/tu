# refs: 185.190 Efficient Programs

[`SOURCES.md`](SOURCES.md) is the register: S1–S22, each with URL, retrieval
date (2026-09-27), licence/access and what it was used for. Notes cite it as
`[S<n>]`, the slides as `[S3 p.<n>]`.

## What is here

| file | what |
|---|---|
| [`SOURCES.md`](SOURCES.md) | the register (authoritative) |
| [`lecture-notes-map.md`](lecture-notes-map.md) | slide range → sources → our note → our code, one row per deck section |
| [`fetch-sources.sh`](fetch-sources.sh) | downloads every cite-only file into `cite-only/` and runs `pdftotext` on the slides |
| `cite-only/` | created by the script, **git-ignored**, never committed |
| `.gitignore` | `cite-only/` |

## Vendoring policy

**Nothing is vendored.** The lecturer's slides, script, exercise sheets and
example programs [S2]–[S9] state no licence, so they are all rights reserved:
fetch them for personal study, cite them by slide or file, quote at most a
short fragment, never copy a file or a code block into `notes/` or `src/`.
`src/c/*.c` is written from scratch (different data layout, different RNG,
different steps for the TSP; see the headers). The free literature (Agner Fog
[S13], Granlund [S15]) is in the same position. TUWEL was not accessed (no
2026W link on TISS yet).

Pull the cite-only files with

```sh
cd ws2026/efficient-programs/refs && ./fetch-sources.sh      # add -n to only print the URLs
```

## Start here

1. [`../notes/00-exam-focus.md`](../notes/00-exam-focus.md): what is graded (exercises + oral interview), what last year's exercises asked, the unexplained InfLab dates.
2. `cite-only/S3-efficient-slides.pdf` [S3], 100 slides, the primary source. Two hours. Then `S4` for the prose where a slide is too terse (German).
3. `cite-only/S7-exercises3-2025w.html` [S7] and `../src/c/pointer_chase.c`: the one exercise that is a small research project. Run the sweep on your own machine before you have a g0 account.
4. [`lecture-notes-map.md`](lecture-notes-map.md), then the notes 01–11 in order.
