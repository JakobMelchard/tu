# refs: 141.282 Quantum Information Theory I

[`SOURCES.md`](SOURCES.md) is the register: entries `S1 … S63` with URL, retrieval date, licence or access status, and what each supports. The notes cite it as `[S<n>]` with a section or theorem locator.

## What is here

| file | what it is |
|---|---|
| [`SOURCES.md`](SOURCES.md) | the source register (authoritative) |
| [`lecture-notes-map.md`](lecture-notes-map.md) | TISS outline item → source sections → our note → our code |
| [`fetch-sources.sh`](fetch-sources.sh) | downloads the free TISS-named texts (Preskill, Jozsa, Wilde) and Mermin's review into `cite-only/`, prints expected sha256 |
| `cite-only/` | created by the script, **git-ignored** (`.gitignore`), never committed |

## Nothing is vendored

The course's own weekly lecture notes are in TUWEL (not accessed). Of the literature TISS names [S1]:

- **Preskill** (S5-S9): free to read on the author's site and the Leiden mirror TISS links; no licence statement, so all rights reserved by default. **Cite only.** Note the move: `theory.caltech.edu/~preskill/ph229/` is dead (404), the live index is <https://www.preskill.caltech.edu/ph229/>.
- **Jozsa** (S10): free PDF on the DAMTP site, no licence statement. **Cite only.**
- **Wilde** (S11): arXiv version under CC BY-NC-SA. Redistribution would be allowed non-commercially with attribution and share-alike, but "permissively licensed" it is not (NC), so it is fetched, not committed. The CUP 2nd edition (S12) is not free.
- **Nielsen & Chuang** (S13), **Bertlmann & Friis** (S14): not free. Cite only; their locators are unverified (N&C from memory of the 2010 edition; B&F by chapter title from Crossref).
- Primary papers S15-S63: journal copies are paywalled; arXiv copies carry the arXiv non-exclusive licence (no redistribution). Cite only.

## Reading order

For the formalism block (notes 01-05): Preskill ch. 2 (S6) end to end, then Wilde ch. 9 and ch. 11 (S11) for the distance and entropy proofs. For entanglement and non-locality (06, 07, 10): Preskill ch. 4 (S8) and Mermin's review (S25). For channels and measurements (11, 12): Preskill ch. 3 (S7). For protocols and no-cloning (08, 09, 13): Jozsa §3-5 (S10). Bertlmann & Friis (S14) is the lecturers' own book: if the library has it, its chapters 11-16, 20, 21, 23 are the closest thing to the lecture available before 04.03.2027.
