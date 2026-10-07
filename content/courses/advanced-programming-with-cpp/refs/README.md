# refs - 360.251 Advanced Programming with C++

[`SOURCES.md`](SOURCES.md) is the register (`S1 ... S18`): title, URL, commit or
retrieval date, licence, what it was used for. The notes cite it as `[S<n>]`.

| file | what it is |
|---|---|
| [`SOURCES.md`](SOURCES.md) | the source register (authoritative) |
| [`lecture-notes-map.md`](lecture-notes-map.md) | TISS topic -> 2021W lecture item -> 2021W hand-out -> our note -> our code -> standard section |
| [`fetch-sources.sh`](fetch-sources.sh) | clones/downloads the cite-only sources into `cite-only/` (about 370 MB unpacked, mostly the cppreference archive) |
| [`.gitignore`](.gitignore) | ignores `cite-only/` |
| `cite-only/` | created by the script, **git-ignored**, never committed |

## Start here

1. [`../notes/00-exam-focus.md`](../notes/00-exam-focus.md): the grade is made in oral
   discussions of your hand-ins [S1]; what those hand-ins looked like in 2021W [S3] [S4].
2. Run `./fetch-sources.sh`, then read `cite-only/S3-cppitems-2021W/items/000/item.md`
   (organisation and grading) and two hand-out READMEs, e.g. `cite-only/S4-ex1.2/README.md`
   and `cite-only/S4-ex3.3/README.md`. Build one of them with CMake and run its tests.
3. [`lecture-notes-map.md`](lecture-notes-map.md), then the notes in order, each with
   `make -C ../src/cpp test` at hand.

## What is vendored, and why nothing is

| source | licence | decision |
|---|---|---|
| lecturers' repos [S3] [S4] [S5] | **none** (no LICENSE file, API `license: null`) | all rights reserved: clone for study, never copy into this repo |
| N4950 [S8] | ISO/IEC copyright, freely downloadable draft | cite, fetch |
| cppreference archive [S9] | CC BY-SA 3.0 + GFDL | share-alike would bind this repo: fetch, do not vendor |
| C++ Core Guidelines [S10] | "personal or internal business use only" | not a redistribution licence: fetch, do not vendor |
| Stroustrup [S11], Meyers [S16], [S17] books | commercial | cite only |
| `cppitems/highlight.js`, `vscode-markdown-cppitems` [S6] | BSD-3-Clause, MIT | permissive, but tooling for the course site, not study material: not needed |

TUWEL is never fetched: it needs a login. VoWi [S7] is behind a bot check and was not read.

```sh
cd refs && ./fetch-sources.sh    # from the course folder
```

The script warns if a cloned repository's HEAD differs from the commit recorded in
`SOURCES.md` (someone pushed: re-check the map).
