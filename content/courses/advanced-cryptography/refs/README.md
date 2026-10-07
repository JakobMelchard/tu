# refs: 192.115 Advanced Cryptography

[`SOURCES.md`](SOURCES.md) is the register (`S1` to `S45`): title, URL,
retrieval date 2026-09-28, access status, and what each source was used for.
Notes and code cite it as `[S<n>]`.

## What is here

| path | what |
|---|---|
| [`SOURCES.md`](SOURCES.md) | the source register (authoritative) |
| [`lecture-notes-map.md`](lecture-notes-map.md) | TISS heading to note to textbook chapter to code |
| `nist/` | **FIPS 203 (ML-KEM) and FIPS 204 (ML-DSA), vendored**, 4.3 MB |
| `rfc/` | **RFC 7748 (X25519) and RFC 8032 (EdDSA), vendored**, 148 KB |
| `*/SHA256SUMS` | checksums of every vendored file |
| [`fetch-sources.sh`](fetch-sources.sh) | verifies the vendored set; `--papers` downloads 24 free papers into `cite-only/` |
| `cite-only/` | created by the script, **git-ignored** ([`.gitignore`](.gitignore)), never committed |

```sh
cd ss2028/advanced-cryptography/refs
./fetch-sources.sh --verify     # checksums only, no network
./fetch-sources.sh              # re-fetch missing standards, verify
./fetch-sources.sh --papers     # + the free papers into ./cite-only (about 25 MB)
```

## Why these files are vendored

Same policy as the prerequisite course
([`../../../ws2026/introduction-to-cryptography/refs/README.md`](../../introduction-to-cryptography/refs/README.md)):
standards that may be redistributed are in the tree, because tests read their
test vectors from disk; everything else is cited.

- **FIPS 203, FIPS 204** are works of the U.S. Government prepared by NIST
  and not subject to copyright protection in the United States
  (17 U.S.C. sec. 105) [S38]. Both carry "This publication is available free
  of charge from" on the title page. Attribution is in `SOURCES.md`.
- **RFC 7748 (2016), RFC 8032 (2017)** carry the IETF Trust copyright notice
  and are subject to BCP 78; TLP 5.0 sec. 3.c.i permits copying and
  distributing IETF documents in full and without modification [S25]. The
  files are unmodified. RFC 8032 is byte-identical to the copy the
  prerequisite course vendors (same SHA-256).
- SP 800-57 Part 1 [S36] is used but not duplicated: the prerequisite course
  vendors it.

## What is deliberately not here

- **Anything from TUWEL.** The homework sheets live there; it needs a login
  and the content is not ours to copy.
- **The free papers** (Boneh-Shoup, Peikert, Lindell, Regev, Groth,
  Bulletproofs, ...). Free to read, but no licence to redistribute:
  `fetch-sources.sh --papers` downloads them locally.
- **Katz-Lindell 3rd ed. [S5] and Hankerson-Menezes-Vanstone [S20]**:
  commercial; not downloaded from anywhere.
- **Schnorr 1991, GMW, Yao, BGW, CDS, Pedersen, GMR** [S10-S12, S29-S31, S45]:
  publisher-only; cited through the surveys and textbooks that present them.

## What sourcing could not establish

- **No course material of 192.115 is public.** The lecturer's homepage lists
  the course and the four offerings but hosts no slides [S24]. VoWi [S44] is
  behind an Anubis proof-of-work page and was not read (bypassing it is out of
  bounds for an agent); a human with a browser should check it for past
  partial exams before January 2028.
- **The lecture order inside the five headings** is unknown; the notes follow
  the TISS order of headings [S2].
- **The exercise style** ("Boneh-Shoup-type problems") is an assumption of the
  planning, not verified from a sheet. [`../notes/00-exam-focus.md`](../notes/00-exam-focus.md)
  lists the Boneh-Shoup exercises that fit each note.
- **Boneh-Shoup v0.6 has holes exactly where this course goes furthest**:
  chapter 17 (lattices) and sections 20.5-20.7 (Bulletproofs, SNARKs) are
  "To be written" [S4]. A later version may fill them and renumber sections;
  recheck the `[S4 ...]` citations then.
- **German vs English examination text differ** on the retake (see
  [`../notes/00-exam-focus.md`](../notes/00-exam-focus.md)) [S2].

## Reading order

1. [`../notes/00-exam-focus.md`](../notes/00-exam-focus.md)
2. [`lecture-notes-map.md`](lecture-notes-map.md)
3. [`../notes/README.md`](../notes/README.md), then notes 01-08.
