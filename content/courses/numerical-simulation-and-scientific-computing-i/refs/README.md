# refs - 360.242 Numerical Simulation and Scientific Computing I

[`SOURCES.md`](SOURCES.md) is the register: one entry `S1 ... S47`, each with
title, authors, URL, retrieval date, licence/access status and what it was used
for. The notes cite it as `[S<n>]`.

## What is here

| file | what it is |
|---|---|
| [`SOURCES.md`](SOURCES.md) | the source register (authoritative) |
| [`lecture-notes-map.md`](lecture-notes-map.md) | TISS topic → sources → our note → our code, one row per topic |
| [`SOURCES.md` § Substitute practice sources](SOURCES.md) | S43, S44 and the reuse of S8/S9: the outside material the practice set is built from, with the licence of each and the argument for why it is comparable |
| [`fetch-sources.sh`](fetch-sources.sh) | downloads the cite-only PDFs into `cite-only/` for personal use |
| `vendor/` | the three sources whose licence permits redistribution - **committed** |
| `cite-only/` | created by the script, **git-ignored**, never committed |


## Start here

The course has **no public script and no public past paper**: TISS says "No
lecture notes are available" for every offering 2019W-2026W and the VoWi page is
empty. So there is no single document to read cover to cover. Instead:

1. [`../notes/00-exam-focus.md`](../notes/00-exam-focus.md): what the exam
   format actually is, what is known and what is guessed, and why; plus the
   2026-09-27 logistics (registration closes 08.10.2026 15:00 [S1]).
2. **[S8]**, <https://jschoeberl.github.io/IntroSC/intro.html> - the "Performance"
   part (Vectorization / Pipelining / Caches / Parallelization). Written by one
   of the five 2026W lecturers. Four chapters, an afternoon.
3. [`vendor/openmp-api-specification-5.2.pdf`](vendor/openmp-api-specification-5.2.pdf)
   §1–§2 and the `reduction`/`schedule` clauses - the normative text for note 07.
4. [`lecture-notes-map.md`](lecture-notes-map.md), then the notes in order.

## What is vendored, and why it is allowed

Three files, 3.3 MB total. Each is redistributable on its own terms; the licence
is quoted in `SOURCES.md`.

| file | source | bytes | sha256 | licence |
|---|---|---|---|---|
| `vendor/openmp-api-specification-5.2.pdf` | [S11] | 2 068 230 | `3a176ab131d7f83ff525aa5449f0e0880138ab444a69d19b4365f7f318381946` | OpenMP ARB: *"Permission to copy without fee all or part of this material is granted, provided the OpenMP Architecture Review Board copyright notice and the title of this document appear."* |
| `vendor/hestenes-stiefel-1952-conjugate-gradients.pdf` | [S15] | 1 346 607 | `63ac54f568a782821d51eeed8fe786e40a335413527a3a527c3c0fdf9d4b07b5` | U.S. Government work, *J. Res. Natl. Bur. Stand.* - not subject to copyright in the United States |
| `vendor/vtkCellType.h` | [S13] | 4 423 | `0dbf5812d4691a877104e78a4035021e0f42e939bb298cedaaa16d8f98e73e93` | BSD-3-Clause (`SPDX-License-Identifier` on line 2); copyright Ken Martin, Will Schroeder, Bill Lorensen |

Verify with

```sh
cd refs    # from the course folder
shasum -a 256 -c <<'EOF'
3a176ab131d7f83ff525aa5449f0e0880138ab444a69d19b4365f7f318381946  vendor/openmp-api-specification-5.2.pdf
63ac54f568a782821d51eeed8fe786e40a335413527a3a527c3c0fdf9d4b07b5  vendor/hestenes-stiefel-1952-conjugate-gradients.pdf
0dbf5812d4691a877104e78a4035021e0f42e939bb298cedaaa16d8f98e73e93  vendor/vtkCellType.h
EOF
```

## What is *not* vendored, and why

Everything else. The reasons, by class:

- **Commercial books** - Hager & Wellein [S35], LeVeque [S23]. Not free.
- **Publisher-held papers** - Amdahl [S19], Gustafson [S20], Park & Miller
  [S28], Hull & Dobell [S29], Lax & Richtmyer / Courant–Friedrichs–Lewy [S24].
  Paywalled; cited by DOI.
- **Free downloads with no redistribution notice** - Saad [S22] ("Copyright ©
  2003 by SIAM" in the front matter), Agner Fog's manuals [S18] (copyright line
  only; the GPL on agner.org applies to *asmlib*, not the manuals), Roofline
  [S16], Matsumoto & Nishimura [S26] (ACM copyright), Goto & van de Geijn [S31],
  Shewchuk [S32], Gmsh [S33]. A free public download with no licence statement
  is all rights reserved.
- **Live documentation** - CMake [S36], Clang [S37], pybind11 [S39], VTK docs
  [S12], the C++ draft [S14], SPDX/OSI [S41]. Permissively licensed but
  versioned and better read online than pinned.
- **[S8], the lecturer's own book** - LGPL-2.1, so redistribution *is*
  permitted. Not vendored because it is a several-hundred-file live Jupyter
  Book; `git clone https://github.com/JSchoeberl/IntroSC` if you want a copy.
- **The substitute practice sources** - Eijkhout's *The Art of HPC* vol. 1
  [S43] (CC BY 4.0) and Bindel's Cornell CS 5220 Fall 2015 [S44] (MIT). Both
  licences permit redistribution; nothing was vendored anyway, because the
  exercises are restated in our words rather than copied. See
  [`../src/exercises/README.md`](../src/exercises/README.md).
- **TUWEL**: needs a login. Never fetched. The course opens there on
  05.10.2026 [S1].

Pull the cite-only PDFs onto your own machine with

```sh
cd refs && ./fetch-sources.sh    # from the course folder
```

which writes into `cite-only/` (git-ignored).
