# refs — 057.020 ASC-School I HPC

[`SOURCES.md`](SOURCES.md) is the register: one entry `S1 … S26`, each with
title, authors, URL, retrieval date, licence/access status and what it was used
for. The notes cite it as `[S<n>]`.

## What is here

| file | what it is |
|---|---|
| [`SOURCES.md`](SOURCES.md) | the source register (authoritative) |
| [`lecture-notes-map.md`](lecture-notes-map.md) | agenda item → source → note → code, one row per session of each block |
| [`fetch-sources.sh`](fetch-sources.sh) | downloads the cite-only PDFs and clones the hands-on repo into `cite-only/` |
| `vendor/` | the five files whose licence permits redistribution — **committed** |
| `cite-only/` | created by the script, **git-ignored**, never committed |

## Start here

Unlike a normal lecture, this course has **no script and no exam**. What it has
is a public agenda, public slides and a public hands-on repository. Read in this
order:

1. [`../notes/00-exam-focus.md`](../notes/00-exam-focus.md) — what is actually
   assessed (it is not an exam), the course status (offered in winter semesters) and
   what ASC currently has on its calendar.
2. [`lecture-notes-map.md`](lecture-notes-map.md) — the three blocks session by
   session.
3. [`vendor/asc-linux-primer.md`](vendor/asc-linux-primer.md) — block 1, the
   lecturers' own slide source. Half an hour.
4. `./fetch-sources.sh`, then `cite-only/asc_intro+login.pdf`,
   `cite-only/slurm_basics.pdf`, `cite-only/slurm_advanced.pdf` — block 2, in
   the running order of the day.
5. `cite-only/mpi/` (the cloned hands-on repository) alongside notes 07–16, and
   [`vendor/mpi-5.0-standard.pdf`](vendor/mpi-5.0-standard.pdf) whenever a
   routine's exact semantics matter.

## What is vendored, and why it is allowed

Five files, 5.8 MB. Each carries an explicit redistribution grant, quoted below
and recorded in `SOURCES.md`.

| file | source | bytes | sha256 | licence |
|---|---|---|---|---|
| `vendor/mpi-5.0-standard.pdf` | [S15] | 6 012 433 | `2d4e6ae09ed04cf5eaf1bda2716d5a1023e282d78f577aa84538a89623c18051` | MPI Forum / Univ. of Tennessee: *"Permission to copy without fee all or part of this material is granted, provided the University of Tennessee copyright notice and the title of this document appear, and notice is given that copying is by permission of the University of Tennessee."* |
| `vendor/asc-linux-primer.md` | [S7] | 26 700 | `e6d8e606f7ec9781fac6c066a3f32232e769ae57711212b2e4edf427aa9d4921` | CC BY-SA 4.0 — © ASC Research Center, TU Wien |
| `vendor/asc-intro-modules.md` | [S10] | 4 533 | `5734106b9f8058ee8f1bebf7fda455d31470784c54d272cc3a38eaf1cbaa3d5e` | CC BY-SA 4.0 — © VSC/ASC team, TU Wien |
| `vendor/asc-intro-compiling.md` | [S10] | 11 032 | `f2ee6799742821eeef6751e2961abf37e267698cd7efba556438589f8c534a37` | CC BY-SA 4.0 — © Jan Zabloudil, Moritz Siegel, TU Wien |
| `vendor/asc-intro-file-storage.md` | [S10] | 1 982 | `57a6d1a4dcd5aa8c4d84236c9673990123bf2cd49104e89801692080573d0ae2` | CC BY-SA 4.0 — © VSC/ASC team, TU Wien |

The CC BY-SA 4.0 text is in
[`vendor/LICENSE-CC-BY-SA-4.0.txt`](vendor/LICENSE-CC-BY-SA-4.0.txt)
(`sha256 23ee78c8bae49cf08ea2f0c84945c66b987ebe4520881fb51b3dad4fb43d07c2`,
the copy shipped in the upstream repositories). **The four markdown files are
byte-identical copies of the upstream files — nothing was modified**, which is
what CC BY-SA asks you to state. Attribution and the upstream URLs are in
`SOURCES.md` under S7 and S10. Anything *derived* from them (notes 01–06) is in
`../notes/`, is our own writing, and cites them inline.

Verify with

```sh
cd refs    # from the course folder
shasum -a 256 -c <<'EOF'
2d4e6ae09ed04cf5eaf1bda2716d5a1023e282d78f577aa84538a89623c18051  vendor/mpi-5.0-standard.pdf
e6d8e606f7ec9781fac6c066a3f32232e769ae57711212b2e4edf427aa9d4921  vendor/asc-linux-primer.md
5734106b9f8058ee8f1bebf7fda455d31470784c54d272cc3a38eaf1cbaa3d5e  vendor/asc-intro-modules.md
f2ee6799742821eeef6751e2961abf37e267698cd7efba556438589f8c534a37  vendor/asc-intro-compiling.md
57a6d1a4dcd5aa8c4d84236c9673990123bf2cd49104e89801692080573d0ae2  vendor/asc-intro-file-storage.md
23ee78c8bae49cf08ea2f0c84945c66b987ebe4520881fb51b3dad4fb43d07c2  vendor/LICENSE-CC-BY-SA-4.0.txt
EOF
```

A changed checksum on the markdown files means ASC has updated the slides —
re-read them, they are the course.

**Re-checked 2026-09-28.** All six checksums above pass. The four markdown
files are still byte-identical to the current upstream `main` of
`vsc-public/training/linux-primer` and `vsc-public/training/vsc-intro`, and
both upstream `license` files still hash to the same CC BY-SA 4.0 text as
`vendor/LICENSE-CC-BY-SA-4.0.txt`. The MPI Forum still serves the 5.0 report
at the same URL with the same size, and the permission notice quoted above is
verbatim on page ii of the vendored PDF.

The vendored markdown files reference their slide images as `pictures/*.png`
and `pictures/*.svg` (18 links). The images are not vendored, so those links do
not resolve here; that is expected, since editing the files would break the
byte-identical copy. The rendered decks from `fetch-sources.sh` have the
pictures.

## What is *not* vendored, and why

- **[S12], the HLRS MPI slide deck** (Rabenseifner) — the one document the
  block-3 lectures are built on. Its owner's terms, quoted verbatim on the ASC
  course-material page [S13], permit personal download and passing on the link
  and **forbid** "any other form of public distribution of the provided pdf
  files themselves or any derived material". So: not vendored, not quoted, and
  no note in this folder is written *from* it. Everything technical in notes
  07–16 is re-derived from the MPI standard [S15]; the deck is cited only for
  *what the course covers*, which is public on [S13] anyway.
- **[S11], the ASC MPI hands-on repository** — states CC BY-SA 4.0 for the
  notebooks *and* that some images, exercise descriptions and code snippets
  inside are HLRS-copyrighted and "used with permission". Permission to the
  author is not obviously a sublicence to us, and a CC BY-SA notice cannot
  relicense third-party material. Rather than guess, `fetch-sources.sh` clones
  it. Our own solutions to the same labs, described in our own words, are in
  `../src/exercises/2025w-mpi/`.
- **[S9] and [S14], the ASC slide PDFs** — free public downloads from Indico and
  `asc.ac.at` with a copyright line and no grant, so all rights reserved.
  Cited heavily; fetched by the script.
- **[S19], the ASC user documentation** — its source repository
  (`gitlab.tuwien.ac.at/vsc-public/documentation`) has **no LICENSE file**, so
  all rights reserved. It is also the fastest-moving source here; read it live.
- **[S16] Slurm, [S17] Environment Modules, [S18] Lmod** — permissively licensed
  software with versioned documentation. Better read online than pinned.
- **[S20] Thakur/Rabenseifner/Gropp** — SAGE copyright; author copy is free to
  read, not to redistribute. Cited by DOI; the formulas are re-implemented in
  [`../src/py/mpi_cost.py`](../src/py/mpi_cost.py).
- **[S21] Amdahl** — ACM paywall. Cited by DOI.

Pull the cite-only material onto your own machine with

```sh
cd refs && ./fetch-sources.sh    # from the course folder
```

which writes into `cite-only/` (git-ignored). Nothing there is ever committed.

## One warning about every figure in `../notes`

No ASC cluster was logged into for this pass, by instruction. Cluster numbers
therefore come from public pages, and public pages go stale — the two sources
already disagree with each other in one place:

| fact | March-2026 slide [S9]/[S10] | current documentation [S19] |
|---|---|---|
| `$DATA` quota | 100 GB, extendable on request | **10 TB**, extendable to 100 TB |
| `/local` size | 480 GB (VSC-4), 2 TB (VSC-5) | ~450 GB (VSC-4), 1.8 TB (VSC-5) |
| A40 GPU nodes | "40 GPU nodes" on the intro deck, 45 on the GPU deck | **45** |
| A100 GPU nodes | "60 GPU nodes" | **61** |
| `cascadelake_0384` | listed as an available QoS on VSC-5 | not in the partition table; mentioned only as having no idle QoS |

The notes follow **[S19]** where they differ and say so in place.
`sinfo -o %P`, `sqos` and `mmlsquota` on the machine beat both.
