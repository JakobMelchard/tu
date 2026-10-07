# refs: 188.980 Advanced Information Retrieval

[`SOURCES.md`](SOURCES.md) is the register (S1-S72, every id cited at least once,
checked by script on 2026-09-28). The notes cite it as `[S<n>]` with a slide, equation or section
locator.

## What is here

| file | what it is |
|---|---|
| [`SOURCES.md`](SOURCES.md) | the source register (authoritative): URL, access, licence, use |
| [`lecture-notes-map.md`](lecture-notes-map.md) | the public 2022 lectures, slide by slide, onto our notes and code |
| [`fetch-sources.sh`](fetch-sources.sh) | downloads slides, captions, exercise texts and free papers into `cite-only/`; `--check` only tests the URLs (all 67 answered HTTP 200 on 2026-09-28) |
| `cite-only/` | created by the script, **git-ignored** ([`.gitignore`](.gitignore)), never committed |

## Why nothing is vendored

The brief allowed vendoring permissively licensed files with their licence text.
None qualifies:

- **Hofstätter's lectures [S4-S15, S17]**: the repository's only licence is **GPL-3.0** (GitHub API and `LICENSE`); the slides carry no Creative Commons notice. The brief's "CC BY-SA 4.0" could not be confirmed. GPL-3.0 is copyleft, not permissive: cite, do not copy.
- **2023 exercise template [S18]**, **2025S student repositories [S21]**: no licence file, so all rights reserved.
- **sueszli's summaries [S19]**: AGPL-3.0, and student recollections of exams: paraphrased themes only.
- **Papers**: publisher or arXiv licences, mostly non-exclusive distribution licences to arXiv only; the BM25 review, GloVe and Conv-KNRM PDFs are author copies.

So `refs/` contains only text written here; `fetch-sources.sh` pulls the rest
onto your machine for personal study.

## Current course material: what is and is not public

| period | lecturers | public material | where the rest is |
|---|---|---|---|
| 2019-2022 | Hofstätter, Althammer | **everything**: slides, YouTube recordings, corrected transcripts, exercise texts [S4, S16, S17] | exam in TUWEL Test [S5 sl. 28] |
| 2023 | (org `tuwien-information-retrieval`) | exercise 2 template [S18] | TUWEL |
| 2024-2026 | Rauber; 2026S Knees, Arzt, Lasy, Iklodi, Rauber | nothing official found on GitHub (org search 2026-09-28: no repository after 2023 except a student's copy); student project repos [S21] | TUWEL (login required) |

The TISS text for 2026S still describes "YouTube uploads of recorded lectures" and
"TUWEL & GitHub" [S2], so the 2027S lectures may again be public. Check in
January 2027 (note 00 §6).

**VoWi** has pages for the course (Rauber, Knees) including a subpage with a
student's summary and past exams [S20]. On 2026-09-28 the wiki answered with a
bot-protection page; it was not circumvented. Read it in a browser.

## Reading order

1. [`../notes/00-exam-focus.md`](../notes/00-exam-focus.md): the curriculum question and the assessment history.
2. Hofstätter lectures 1-3 [S6-S8] with notes 02-04; then 4-6 [S9-S11] with 05-07; then 7, 8, 10 [S12, S13, S15] with 08-12; 9 [S14] with 14.
3. Papers, in this order: Robertson and Zaragoza §3 [S23]; KNRM [S33]; monoBERT [S35]; DPR [S37]; ColBERT [S38]; Margin-MSE [S40]; TAS-B [S41]; TREC DL 2019 overview [S45]; the survey by Lin et al. [S48] as reference.
