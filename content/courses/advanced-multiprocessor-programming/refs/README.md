# refs - 191.022 Advanced Multiprocessor Programming

[`SOURCES.md`](SOURCES.md) is the register, `S1 ... S37`: title, authors,
URL, retrieval date, access status and what each source was used for. Notes
and code cite it as `[S<n>]`.

## What is here

| file | what it is |
|---|---|
| [`SOURCES.md`](SOURCES.md) | the source register (authoritative) |
| [`lecture-notes-map.md`](lecture-notes-map.md) | TISS topic → book chapter → our note → our code, one row per topic |
| [`fetch-sources.sh`](fetch-sources.sh) | downloads the 23 free PDFs into `cite-only/` (22 succeeded on 2026-09-28; Treiber's IBM report host was unreachable) |
| `cite-only/` | created by the script, **git-ignored**, never committed (about 21 MB) |

**Nothing is vendored.** Every free PDF here is an author, course or
publisher copy of a copyrighted paper (ACM, IEEE, Elsevier, Cambridge TR)
without a redistribution licence. The course book [S1] is not free and is
cited by chapter only. VoWi [S5] and the 2013 student repository [S37] (no
licence) are summarised, not copied.

## Start here

1. [`../notes/00-exam-focus.md`](../notes/00-exam-focus.md): status (cancelled
   2026W, expected again 2027W), assessment, the 2025W schedule, what the exercises and
   the project have looked like, the missing prerequisite.
2. The book [S1], chapters 2, 3, 5 first: they are what the exercise sheets
   have been drawn from [S37].
3. Herlihy & Wing [S6] §1-3 and Herlihy [S7] §1-3: the two papers behind notes
   02 and 04, readable in an evening.
4. cppreference `memory_order` [S20], then Preshing [S21], then Sutter's talk
   [S22] for note 03.
5. The data-structure papers alongside notes 05-12, one per note (the map
   below).
