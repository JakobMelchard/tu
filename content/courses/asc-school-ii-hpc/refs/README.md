# refs: 057.021 ASC-School II

| file | what |
|---|---|
| [SOURCES.md](SOURCES.md) | register `[S1]`...`[S23]`, including the **training catalogue** as read on 2026-09-28 |
| [lecture-notes-map.md](lecture-notes-map.md) | catalogue event -> note -> code, and what is covered in other courses of this repo |
| [fetch-sources.sh](fetch-sources.sh) | personal copies into `cite-only/` (git-ignored); `--list` prints without fetching |
| `.gitignore` | ignores `cite-only/` |

## Licences and what may be committed

Nothing is vendored in this folder.

| material | licence found | handling |
|---|---|---|
| ASC GitLab training repos `python4hpc`, `introduction-to-deep-learning`, `LLMs-on-supercomputers` (S7) | **CC BY-SA 4.0** (`LICENSE` file and README of each, checked 2026-09-28) | redistributable with attribution and share-alike; cloned, not committed, because they are large and updated before every run. Anything derived and published must carry CC BY-SA 4.0 |
| ASC-Intro slide PDFs on Indico (`gpus.pdf`, `slurm_advanced.pdf`) | none stated | cite-only; fetched for personal use |
| HLRS hybrid/MPI course slides (Rabenseifner, Hager) | HLRS: personal download only, no redistribution of the files "or any derived material" (quoted in the sibling register S12) | not fetched, not paraphrased |
| ASC user documentation (S12-S14) | public GitLab repo without licence file | cited only |
| OpenMP 5.2 specification (S16) | OpenMP ARB copyright, copying permitted with notice | fetched, not committed (linked) |
| MPI 5.0 standard (S15) | University of Tennessee, copying permitted with notice | vendored once, in the sibling course; linked from here |
| tool manuals (Slurm, perf, Score-P, LIKWID, CUDA, HDF5, Lustre) | various | cited by URL |

The sibling course keeps the CC BY-SA 4.0 licence text at
[`../../../ws2027/asc-school-i-hpc/refs/vendor/LICENSE-CC-BY-SA-4.0.txt`](../../asc-school-i-hpc/refs/vendor/LICENSE-CC-BY-SA-4.0.txt).
If a notebook from `cite-only/python4hpc` is ever committed here, copy that
licence file next to it and keep the authors' attribution line (Blaas-Schenner,
Fischak, Harrison, Muck).
