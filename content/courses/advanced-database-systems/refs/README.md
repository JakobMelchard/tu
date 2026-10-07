# refs: 184.780 Advanced Database Systems

[`SOURCES.md`](SOURCES.md) is the register (S1...S41, with retrieval date,
access status and what each source was used for). The notes cite it as `[S<n>]`.

## What is here

| path | what | tracked |
|---|---|---|
| [`SOURCES.md`](SOURCES.md) | the source register (authoritative) | yes |
| [`lecture-notes-map.md`](lecture-notes-map.md) | course topic (per block, as far as public material shows it) -> our note -> our code -> primary source section | yes |
| [`fetch-sources.sh`](fetch-sources.sh) | verifies `vendor/`, re-fetches it if missing, and with `--papers` downloads the cite-only PDFs | yes |
| `vendor/` | 6 documentation pages, 568 KB, with `SHA256SUMS` and `LICENSE-PostgreSQL.txt` | yes |
| `cite-only/` | 23 PDFs, about 33 MB: papers, the free textbook, VoWi student material | **no** (git-ignored via [`.gitignore`](.gitignore)) |

## Why only these files are vendored

Vendored means: copied into the repository and redistributable.

- `sqlite-lang_with.html` (S13): "All of the code and documentation in SQLite
  has been dedicated to the public domain" (S38).
- `pg18-*.html` (S9, S10, S11): the PostgreSQL documentation is under the
  PostgreSQL License, which permits copying and distribution of the
  "software and its documentation" if the copyright notice and the licence
  paragraphs accompany every copy; they are in
  [`vendor/LICENSE-PostgreSQL.txt`](vendor/LICENSE-PostgreSQL.txt). Files are
  unmodified PostgreSQL 18.6 pages.

Everything else is **cite-only**:

- papers (S16-S19, S21, S24-S26, S28-S33, S40, S41): publisher or ACM/IEEE/USENIX
  copyright, free to read at the authors' or publishers' sites, no
  redistribution licence;
- Abiteboul, Hull, Vianu (S7): the site allows "one copy of the book draft for
  personal use but not for distribution";
- Green et al. (S8): now publishers copyright; the free copy is a third-party upload;
- MMDS ch. 2 (S17): free from Stanford, no redistribution licence stated;
- VoWi uploads (S3-S6): student material with no stated licence;
- vendor documentation of MongoDB, Cassandra, Neo4j, Spark (S20, S22, S34-S36):
  cited as live pages. Spark's and Cassandra's docs are Apache-2.0 and could be
  vendored, but they change with every release and nothing here depends on a
  frozen copy.

## Commands

```sh
cd refs    # from the course folder
./fetch-sources.sh --verify            # checksums of vendor/, no network
./fetch-sources.sh                     # re-fetch missing vendor/ files, then verify
./fetch-sources.sh --papers            # + cite-only/ (personal study copies)
(cd vendor && shasum -a 256 -c SHA256SUMS)
```

Verification on 2026-09-28: all 7 checksums OK; `--papers` fetched all 23
cite-only files (each `curl -f`; none failed).

## What is not here

- No TUWEL material (slides, recordings, exercise sheets): login required.
- No past exam of the current (MC) format: none is public. The only published
  paper is the 2020 exam with solution key (S6), in the old format.
