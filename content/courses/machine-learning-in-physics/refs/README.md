# refs: 138.128 Machine Learning in Physics

[`SOURCES.md`](SOURCES.md) is the register (S1-S37): URL, retrieval date,
licence, what each source was used for. The notes cite it as `[S<n>]`.

## What is here

| file | what |
|---|---|
| [`SOURCES.md`](SOURCES.md) | source register (authoritative) |
| [`lecture-notes-map.md`](lecture-notes-map.md) | TISS topics, 2021-2023 videos and 2021S exercises mapped to our notes, code and textbook sections |
| [`fetch-sources.sh`](fetch-sources.sh) | downloads the four free PDFs (S6-S9) into `cite-only/` |
| `cite-only/` | created by the script, **git-ignored** (`.gitignore`), never committed |

## Nothing is vendored

| source | licence | action |
|---|---|---|
| S5 course exercise notebooks (GitHub) | **none stated** | link only; numbers used as test anchors are facts, no text or code copied |
| S6 Mehta et al. (arXiv) | arXiv non-exclusive distribution | fetch, cite |
| S7 MML (free PDF) | "personal use only. Not for re-distribution" | fetch, cite |
| S8 ESL, S9 ISLP (author-hosted) | Springer copyright | fetch, cite |
| S10 Hansen, SIAM | commercial | cite only, not fetched |
| S14 Mehta notebooks | MIT | could be vendored; not needed, linked |

The course's graded material (2027S notebooks, TUWEL pages) is behind logins.
Nothing was fetched from TUWEL or JupyterHub.

From the course folder:

```sh
cd refs && ./fetch-sources.sh
```

Checksums as retrieved 2026-09-28 (a changed checksum means a revised file, not
an error; re-check the section locators in `SOURCES.md`):

```
S6  7db49ff1db028e7152e0d86f3e5d29a03e32e08d3bbac6802791c3442d8a7e38  116 pp.
S7  3f87b70c64a35d30ec4e565b4d5cfd18fe913002d3b3bed44691c7d0838911bc  417 pp.
S8  8d098d65cf53925ba0fc13a52a2790d48a32433223cbd876d0a527cd1afe2e0f  764 pp.
S9  278d3bdd49a8a480c2ff8e03245822caad8a3a48e81afd6d039c52c8fc13ad60  613 pp.
```

The ESL and ISLP links are Google Drive redirects published on the authors'
pages; if one returns an HTML interstitial, the script deletes it and prints the
URL to open in a browser.

## Reading order

1. [`../notes/00-exam-focus.md`](../notes/00-exam-focus.md).
2. **S6** (Mehta et al.) sections II-VII and IX, XII-XIII: the closest match to the
   course in spirit (physics examples, Ising and SUSY data), 116 pages.
3. **S7** chapters 4, 5.6, 7, 9, 10, 11 for the linear algebra and derivations.
4. **S8/S9** for statistics depth (bias-variance, ridge/lasso, logistic regression).
5. **S10** (library) chapters 2-5 for the inverse-problem side of note 03.
6. The public 2021S notebooks [S5] and videos [S11], via
   [`lecture-notes-map.md`](lecture-notes-map.md).
