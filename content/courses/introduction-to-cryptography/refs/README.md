# refs — 192.125 Introduction to Cryptography

[`SOURCES.md`](SOURCES.md) is the register: one entry `S1 … S57`, each with
title, authors, URL, retrieval date, licence/access status and what it was used
for. The notes and the code cite it as `[S<n>]`.

## What is here

| file | what it is |
|---|---|
| [`SOURCES.md`](SOURCES.md) | the source register (authoritative) |
| [`lecture-notes-map.md`](lecture-notes-map.md) | lecture → Katz-Lindell section → our note → our code, for all 14 lectures |
| `rfc/` | **11 RFCs, vendored**, plain text, 1.2 MB |
| `nist/` | **7 NIST FIPS/SP documents, vendored**, PDF, 6.1 MB |
| `vectors/` | **37 RSAES-OAEP test vectors, vendored**, Apache-2.0, with the licence text |
| `*/SHA256SUMS` | checksums of every vendored file, so a changed file is visible |
| [`fetch-sources.sh`](fetch-sources.sh) | re-fetches and verifies the vendored set; pulls the cite-only PDFs into the git-ignored `vendor/` |
| `vendor/` | created by the script, **git-ignored**, never committed |

## Why this course vendors its sources

The primary sources for *how the algorithms work* are standards, and standards
are free to redistribute. The primary sources for *what this course teaches* are
the lecturer's slides and past papers, and those are not. So the tree contains
the former and cites the latter.

### The RFCs

- **Post-2008 RFCs** (4231 is 2005; 5116, 5869, 6234, 6979, 8017, 8032, 8439,
  8446 carry the IETF Trust boilerplate) are subject to BCP 78 and the Trust's
  Legal Provisions. [TLP 5.0 sec. 3.c.i][S37] grants an unlimited right to
  "copy, publish, display and distribute IETF Contributions and IETF Documents
  **in full and without modification**". These files are unmodified.
- **Pre-2008 RFCs** (2104, 3526, 4231, 5116) say "Distribution of this memo is
  unlimited" in their *Status of This Memo*, which is the policy that was in
  force when they were published — TLP 5.0 sec. 2.c keeps documents published
  before 25 March 2015 under the policy of their time.

### The NIST documents

FIPS 197, FIPS 180-4, FIPS 198-1, FIPS 186-5, SP 800-38A, SP 800-38D and
SP 800-57 Part 1 are works of the United States Government prepared by NIST
employees, and under 17 U.S.C. sec. 105 are **not subject to copyright
protection in the United States** [S38]. Two of them say so in their own front
matter: SP 800-38A, p. 2, "It is not subject to copyright"; SP 800-57 Part 1
Rev. 5, p. ii, "not subject to copyright in the United States. Attribution
would, however, be appreciated by NIST." Attribution is in
[`SOURCES.md`](SOURCES.md) and in every test that uses them.

### The test vectors

`vectors/rsa_oaep_2048_sha256_mgf1sha256_test.json` is from Project Wycheproof
and is licensed **Apache License 2.0**; the licence text is beside it at
[`vectors/LICENSE-Apache-2.0.txt`](vectors/LICENSE-Apache-2.0.txt) as that
licence requires. It is unmodified.

### What is deliberately *not* here

- **The lecturer's slides** [S7, S8] — the single most useful source for this
  course, and third-party copyright with no licence statement. Cited, with a
  download command in `fetch-sources.sh`.
- **Every past paper and sample solution** [S12-S17] — student uploads of exam
  papers. Cited; the questions are described in our own words in
  [`../notes/00-exam-focus.md`](../notes/00-exam-focus.md) and never reproduced.
- **Katz-Lindell** [S10] — a commercial textbook. VoWi hosts scanned PDFs of the
  2nd and 3rd editions; they were **not downloaded** and `fetch-sources.sh` does
  not offer to.
- **Anything from TUWEL**: it needs a login and is not ours to copy.
- The papers S39-S52, which are under ACM, IEEE, SIAM or Springer copyright, or
  are author-hosted with no permission notice. Free ones have fetch commands in
  the script.
- The free textbooks and companions S53-S57. Boneh-Shoup [S55] states no licence
  and has a fetch command into `vendor/`; *The Joy of Cryptography* [S56] is
  CC BY-NC-ND 4.0 and online-only, so it is linked, not copied.

Verify the vendored set at any time:

```sh
cd ws2026/introduction-to-cryptography/refs    # from the qist repo root
./fetch-sources.sh --verify          # checksums only, no network
./fetch-sources.sh                   # re-fetch anything missing, then verify
./fetch-sources.sh --papers          # + the free cite-only PDFs into ./vendor
```

## What sourcing this course could *not* establish

Read this before [`../notes/00-exam-focus.md`](../notes/00-exam-focus.md).

192.125 has run since at least 2021W. It is taken in **2026W**, the current
offering: lectures Thursdays 01.10.2026 to 21.01.2027, **midterm Wed
18.11.2026**, **final Fri 29.01.2027**, retakes Fri 26.02.2027 (TISS, checked
2026-10-07 [S1]). The subject list, ECTS, learning outcomes and lecturers are
unchanged from 2025W [S1, S2]; the grading is not: 2026W is 20 % exercises +
40 % midterm + 40 % final, with half the exercise points required to sit an
exam and exercise presence no longer mandatory
(`../docs/tiss-api.md`, [S1]). Two earlier changes
matter as well:

- **2024W → 2025W: one final exam became a midterm plus a final**, and one of
  the two may be retaken at the end of February [S2, S3]. Students describe this
  as "a huge relief" [S5]. 2026W keeps it.
- **2024W → 2025W: 066 558 QIST was added to the curricula** [S2, S3]. This is
  a QIST elective only from 2025W on.

**Neither lecturer hosts any teaching material of their own** [S9, S11]. Both
pages link only to TISS; Fuchsbauer's personal site carries decks for unrelated
ENS and ESILV courses, and nothing for 192.125. This is worth stating as a
negative result because it is the usual highest-value source of a pass like this
one, and here it does not exist: the only public slides are the student uploads
S7 and S8. Re-checked 2026-10-07, including the Security and Privacy group's
course list: still nothing beyond TISS, and no 2026W material on VoWi.

The division of labour is not arbitrary. Andreeva works on symmetric
authenticated encryption, block ciphers, forkciphers and hash functions [S11],
and she gives exactly **lecture 3 (block ciphers)** and **lecture 9 (hash
functions)** [S8] — the two lectures that go furthest into construction detail.
Fuchsbauer, whose work is public-key and provable security [S9], gives the other
eleven.

What is missing is the *homework*. In 2026W nine assignments carry 20 % of the
grade and an entry threshold for the exams (50 % in 2025W), and 86 of the 150
ECTS hours, and only the sample solutions to assignments 1 and 2 are public
[S14]. Everything else is in TUWEL (course id 84457), which needs a login and
was not opened. There is also exactly **one** midterm paper in existence [S13],
because midterms began in 2025W.

What replaces that gap is the standards. Every algorithm the notes describe is
traceable to a vendored RFC or FIPS section, and the numbers those documents
print are reproduced by tests:

- [`../src/py/test_oaep.py`](../src/py/test_oaep.py) — 37 published RSAES-OAEP
  vectors, valid and malformed, against an implementation written from RFC 8017
  sec. 7.1 line by line.
- [`../src/py/test_standard_vectors.py`](../src/py/test_standard_vectors.py) —
  the FIPS 197 appendix B AES example, the SP 800-38A ECB/CBC/CTR vectors, the
  RFC 6234 SHA-256 patterns, the RFC 4231 HMAC cases, and the RFC 3526 group-14
  safe prime.
- [`../src/py/test_block_ciphers.py`](../src/py/test_block_ciphers.py) — all 256
  bytes of the AES S-box, derived from the FIPS 197 sec. 5.1.1 definition and
  checked against Table 4.

## Reading order

1. [`../notes/00-exam-focus.md`](../notes/00-exam-focus.md) — what four past
   papers actually asked, and how much of it is known versus inferred.
2. [`lecture-notes-map.md`](lecture-notes-map.md) — the lecture order, which is
   also the note order.
3. [`../notes/README.md`](../notes/README.md) — the thirteen topic notes.

[S37]: https://trustee.ietf.org/documents/trust-legal-provisions/tlp-5/
[S38]: https://www.nist.gov/open/copyright-fair-use-and-licensing-statements-srd-data-software-and-technical-series-publications
