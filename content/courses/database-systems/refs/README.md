# refs: 184.686 Database Systems

[`SOURCES.md`](SOURCES.md) is the register: entries `S1 … S22`, each with
title, URL, retrieval date, licence/access status and what it was used for.
The notes cite it as `[S<n>]`.

## What is here

| file | what it is |
|---|---|
| [`SOURCES.md`](SOURCES.md) | the source register (authoritative) |
| [`lecture-notes-map.md`](lecture-notes-map.md) | TISS subject item → sources → note → code, and where sources disagree |
| [`fetch-sources.sh`](fetch-sources.sh) | verifies the vendored pages; `--papers` downloads the cite-only copies |
| `vendor/sqlite/` | **8 SQLite documentation pages, vendored** (public domain), with `SHA256SUMS` |
| `cite-only/` | created by the script, **git-ignored** ([`.gitignore`](.gitignore)), personal copies only |

## Licences: why only SQLite is vendored

- **SQLite documentation** [S21]: "All of the code and documentation in SQLite
  has been dedicated to the public domain" (`vendor/sqlite/copyright.html`,
  vendored alongside). The eight pages are byte-identical to sqlite.org's on
  2026-09-28; `SHA256SUMS` makes any change visible.
- **Silberschatz/Korth/Sudarshan slides** [S6]: "authorized for personal use"
  and for courses using the book as prescribed text; not redistributable.
- **Abiteboul/Hull/Vianu** [S10]: the authors allow "one copy of the book draft
  for personal use but not for distribution".
- **Papers** [S9], [S11], [S14], [S16], [S19], [S20]: ACM/IEEE/publisher
  copyright or arXiv's default licence; no redistribution grant was found, so
  they are fetched for reading only.
- **PostgreSQL documentation** [S22]: the PostgreSQL Licence would permit
  redistribution with its notice; the pages are cited rather than vendored to
  keep the tree small.
- **Kemper/Eickler** [S7], **Garcia-Molina/Ullman/Widom** [S8]: commercial,
  not fetched, not consulted.

```sh
cd refs    # from the course folder
./fetch-sources.sh --verify      # checksums of vendor/sqlite, no network
./fetch-sources.sh               # re-fetch missing vendored pages, verify
./fetch-sources.sh --papers      # + cite-only PDFs and pages (about 90 MB)
(cd vendor/sqlite && shasum -a 256 -c SHA256SUMS)
```

Last run 2026-09-28: 8/8 `OK`; `--papers` fetched all 25 cite-only files.

## What sourcing could not establish

- The course's own public pages [S4] returned **HTTP 403** on 2026-09-28:
  no slides, exercise sheets, SQL-exam rules or past papers were read.
- VoWi [S5] answered with a bot-detection page; it was not bypassed. Past MC
  papers and student summaries, if they exist, are there: read them in a
  browser before the semester.
- TUWEL was not touched (not ours to copy).
- The 2027S TISS page is not published; all course facts are the 2026S pattern [S1].

So the notes rest on standard textbook material [S6], [S10], primary papers
and system documentation, and every worked number is produced by the code in
`../src/py`. What the course itself emphasises remains to be
checked against its slides.

## Reading order

1. [`../notes/00-exam-focus.md`](../notes/00-exam-focus.md): what is known about the assessment.
2. [`../notes/README.md`](../notes/README.md): course facts and the topic notes in TISS order.
3. [`lecture-notes-map.md`](lecture-notes-map.md) to find the source behind a note.
