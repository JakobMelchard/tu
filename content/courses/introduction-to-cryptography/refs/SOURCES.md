# Sources — 192.125 Introduction to Cryptography

Register of every source used to write and verify `../notes` and
`../src`. Notes and code cite these as `[S<n>]`. Retrieval dates are the
day the page or file was fetched; TISS and VoWi change, so re-check before an exam.

**Vendoring policy.** The standards this course rests on *are* free to
redistribute, so they are in the tree: eleven RFCs in `rfc/`, seven NIST
FIPS/SP documents in `nist/`, and one Apache-2.0 test-vector file in
`vectors/`, 7.3 MB in total with `SHA256SUMS` manifests. The licence
reasoning is in [`README.md`](README.md). Everything else below is cited only:
the lecturer's slides and the past papers are third-party copyright, and
Katz-Lindell is a commercial textbook. **No TUWEL content was fetched** — TUWEL
needs a login and is not ours to copy. The PDF copies of Katz-Lindell that VoWi
hosts were **not** downloaded either.

**The single most valuable source is [S8]**, the lecturer's own 2024W slide
archive: fourteen decks covering lectures 1-13a, each headed with its
Katz-Lindell section numbers. It fixes the lecture order, the notation, which
Katz-Lindell sections are in scope, and — on its last slide — an explicit list of
what the course does *not* cover. The notes were reordered to follow it.

---

## Course-authoritative

### S1 — TISS course page, 2026W (the current offering)

- Title: 192.125 Introduction to Cryptography, 2026W
- URL: <https://tiss.tuwien.ac.at/course/courseDetails.xhtml?courseNr=192125&semester=2026W&locale=en>
- Retrieved: 2026-09-22 (browser; the page needs JavaScript)
- Access: public, no login
- Used for: scope (7-item subject list), learning outcomes, lecturers
  (Fuchsbauer, Andreeva), VU 4.0 h / 6.0 ECTS, the ECTS breakdown, examination
  modalities, exam dates, registration windows, literature (Katz-Lindell 3rd
  ed.), curricula (066 558 QIST: elective), continuative courses (192.115
  Advanced Cryptography, 192.124 Symmetric Cryptography). Diffed against
  [`../docs/tiss.md`](../docs/tiss.md): **no field changed**. New information:
  the *single appointments* list, which shows weekly lectures 01.10.2026 –
  21.01.2027 and weekly exercises from 08.10.2026, and a lecture on 26.11.2026
  in the same slot as the Q&A session.
- 2026-09-28: the TISS API record re-fetched that day
  (`../docs/tiss-api.md`) differs from the 2026-09-22
  transcription in the examination modalities: 20 % exercises + 40 % midterm +
  40 % final (was 50/50), half the exercise points required to sit an exam,
  uploaded solutions graded with 0 for missing, copied or clearly AI-generated
  work (a second time: negative grade), and an ECTS split of 4 h exam / 86 h
  homework (was 3 / 87). `../docs/tiss.md` is read-only and was not changed.
- Re-checked 2026-10-07 (browser, page and "show single appointments"; and the
  API record <https://tiss.tuwien.ac.at/api/course/192125-2026W>, XML). The page
  now carries what it lacked on 2026-09-22: a **TUWEL course** link
  (`tuwel.tuwien.ac.at/course/view.php?id=84457`, login, not opened) and the
  **LectureTube** flag; format "Presence"; "Presence is not mandatory". Grading
  as in the 2026-09-28 bullet (20 % / 40 % / 40 %, mean of the two partial exams
  positive, one partial exam retakeable end of February), and exercise
  presentations are now *voluntary*, not sampled. Lecturers Fuchsbauer and
  Andreeva only (API oids 23118865, 22513637). Dates:
  - lectures Thu 12:00-14:00, FAV Hörsaal 1 Helmut Veith, **15 dates**:
    01.10, 08.10, 15.10, 22.10, 29.10, 05.11, 12.11, 19.11, 26.11, 03.12,
    10.12, 17.12.2026, 07.01, 14.01, 21.01.2027;
  - exercises Thu 15:00-18:00, EI 5 Hochenegg HS, **13 dates**: every lecture
    Thursday from 08.10.2026 except 14.01.2027;
  - **midterm Wed 18.11.2026 12:00-14:00**, GM 1 Audimax (registration
    23.10.-18.11.2026); **final Fri 29.01.2027 10:00-12:00**, GM 1 Audimax
    (registration 03.12.2026-29.01.2027); **retakes** of either Fri 26.02.2027
    12:00-14:00 (registration 05.02.-26.02.2027);
  - course registration 28.07.-15.10.2026 23:59, deregistration until
    08.10.2026 23:59.
  The 26.11.2026 Q&A slot noted on 2026-09-22 is no longer listed; that date is
  an ordinary lecture. Subject list, literature (Katz-Lindell 3rd ed.), curricula
  (066 558 QIST: elective) and continuative courses unchanged.

### S2 — TISS course page, 2025W (previous offering)

- URL: <https://tiss.tuwien.ac.at/course/courseDetails.xhtml?courseNr=192125&semester=2025W&locale=en>
- Retrieved: 2026-09-22. Access: public.
- Used for: the year-on-year diff. Same 6.0 ECTS, same subject list as 2026W.
  Examination modalities differ (re-checked 2026-10-07 via the API record
  `192125-2025W`): 2025W had **mandatory presence**, presenters sampled at
  random among those who ticked a problem, and 50 % exercises + 50 % exams;
  2026W has voluntary presence and presentations, graded uploads, and
  20 / 40 / 40 [S1]. Other differences: **Andreas Weninger** is listed as
  a third lecturer; there are **four exercise groups** (Thu 10-12, Thu 16-18 in
  FAV HS 3 Zemanek; Fri 09-11, Fri 11-13 in EI 1 Petritsch) instead of the single
  Thu 15-18 slot 2026W shows; lecture Thu 12:15-14:00; registration
  29.07.2025 – 09.10.2025. Marked "LectureTube course" with a TUWEL link; as of
  2026-10-07 the 2026W page has both as well [S1].

### S3 — TISS course page, 2024W

- URL: <https://tiss.tuwien.ac.at/course/courseDetails.xhtml?courseNr=192125&semester=2024W&locale=en>
- Retrieved: 2026-09-22. Access: public.
- Used for: the diff, and this is where the **grading scheme changed**. 2024W:
  "50% exercise sessions and 50% **final exam**"; the exercise grade was 70%
  solved homework + 30% presentations, both of which had to be positive to sit
  the exam, and there were **two attempts at one final**. Lecture Thu 11:15-13:00.
  Lecturers Fuchsbauer, Andreeva, Weninger, with contributors Regen, Sefranek,
  Trevisani. Curriculum **066 558 QIST is absent** — this course became a QIST
  elective only in 2025W.

### S4 — TISS course page, 2023W

- URL: <https://tiss.tuwien.ac.at/course/courseDetails.xhtml?courseNr=192125&semester=2023W&locale=en>
- Retrieved: 2026-09-22. Access: public.
- Used for: the deeper diff. **Fuchsbauer alone**; literature is Katz-Lindell
  **Second** Edition (the switch to the 3rd edition happened in 2024W);
  examination "the number of solved homework assignments, presentations (50%) and
  a final written exam (50%)"; lecture Wednesday 11:15-13:00. Also records that
  offerings exist back to 2021W.

### S5 — VoWi page, *Introduction to Cryptography VU (Fuchsbauer)* ★

- URL: <https://vowi.fsinf.at/wiki/TU_Wien:Introduction_to_Cryptography_VU_(Fuchsbauer)>
- Retrieved: 2026-09-22 (browser — VoWi is behind an Anubis proof-of-work gate,
  so plain `curl` gets an HTML challenge page)
- Access: public, no login. Student-written wiki; content is CC-licensed but the
  **uploaded materials are not**, so nothing from it is vendored.
- Used for: the eleven attached materials (S7, S8, S12-S16), the student-written
  topic list (which names *historic ciphers* and *TLS*, both of which the TISS
  subject list omits), the reported grading formula `%G = 0.5*%E + 0.5*%U`
  "W23+", the previous formula `0.4*%E + 0.6*(%U*5/4 - 25%)` with a 50% floor in
  each part, and the student reports digested into
  [`../notes/00-exam-focus.md`](../notes/00-exam-focus.md) — including "WS25:
  they changed the exam from just one final to one midterm + one final", and
  "WS2025: the general exercise mode is now only about how many exercises you
  check" (no more `Tafelleistung` deductions).
- Re-checked 2026-10-07 (browser; the Anubis check passes on its own after a few
  seconds). "Letzte Abhaltung" now reads 2026W; still **11 materials, none new**
  (no 2026W slides, sheets or papers). New text since 2026-09-22: two comments
  headed "WS26" (understand the basics from the start, rewatch the lectures; the
  exercise sessions announce presenters at the start and the learning curve is
  shallow when the presenter is unsure). They describe a finished term, so
  "WS26" most likely means 2025/26, i.e. 2025W. The page links a Mattermost
  channel (login, not opened) and, under *Unterlagen*, a third-party PDF of
  Katz-Lindell 2nd ed. on a Greek university server, which is not an authorised
  copy and was not opened.

### S6 — VoWi, the two *similarly named* LVAs: both empty

- URLs: <https://vowi.fsinf.at/wiki/TU_Wien:Introduction_to_Cryptography_VO_(Fuchsbauer)>
  and <https://vowi.fsinf.at/wiki/TU_Wien:Introduction_to_Cryptography_UE_(Fuchsbauer)>
- Retrieved: 2026-09-22. Access: public.
- Used for: ruling out the usual trap. Both are the split VO/UE pair
  (`tiss:192107`, 3 ECTS, last held 2020W) that 192.125 replaced; both carry
  **0 materials**. Everything is on S5. The VO page also records that this
  lecture replaced *Introduction to Modern Cryptography VU (Maffei)*, whose VoWi
  page is a different course and was not used.

### S7 — Fuchsbauer & Andreeva, lecture slides 2025W (lectures 1-8)

- File: `Slides2025W.pdf`, 26.7 MB, 299 pages, uploaded to S5
- URL: <https://vowi.fsinf.at/images/d/dd/TU_Wien-Introduction_to_Cryptography_VU_%28Fuchsbauer%29_-_Slides2025W.pdf>
- Retrieved: 2026-09-22 (browser). **Licence: none stated ⇒ all rights reserved.
  Not vendored.**
- Used for: confirming that the 2025W first half matches the 2024W decks
  lecture-for-lecture, and for the 2025W administrative slides: midterm
  "closed book", 3 Dec, 14:00-16:00, and grading 50% exercise + 50% exam.

### S8 — Fuchsbauer & Andreeva, lecture slides 2024W (lectures 1-13a) ★★

- File: `Slides2024WS.zip`, 44.4 MB, fourteen PDFs
  (`Slides Lecture 1.pdf` … `13.pdf`, `13a.pdf`), uploaded to S5
- URL: <https://vowi.fsinf.at/images/f/f8/TU_Wien-Introduction_to_Cryptography_VU_%28Fuchsbauer%29_-_Slides2024WS.zip>
- Retrieved: 2026-09-22 (browser). **Licence: none stated ⇒ all rights reserved.
  Not vendored.** The section map extracted from it is in
  [`lecture-notes-map.md`](lecture-notes-map.md).
- Used for: **everything structural.** The lecture order, the Katz-Lindell
  section number on each deck's title slide, and three findings that changed the
  notes materially:
  1. Lecture 1 is entirely **historical ciphers** (Scytale, permutation,
     monoalphabetic/Caesar/shift, cryptanalysis by frequency analysis,
     polyalphabetic substitution, Vernam) plus sec. 1.2 syntax and Kerckhoffs'
     principle (sec. 1.4). The notes had none of it.
  2. Lecture 3 (Andreeva) is a full lecture on **block-cipher internals**
     (sec. 7.2): ideal cipher, Shannon's confusion/diffusion, SPNs, DES with its
     Feistel structure, differential cryptanalysis, brute force, **2DES and the
     meet-in-the-middle attack**, Triple DES ("Keys: 112 bits, Security: 112
     (NIST: 80) bits"), AES/Rijndael down to the S-box, the MixColumns matrix
     and the key schedule, and the 2009 related-key (2^99.5) and 2011 biclique
     (2^126.2) attacks. The notes had one paragraph.
  3. Lecture 13a's closing slide, *"What we did not cover"*: **security proofs
     for public-key schemes (often in the random-oracle model)**, cryptography
     from minimal assumptions, algorithms for factoring and discrete logs,
     further public-key schemes; and as *advanced topics for the master course*,
     ROM proofs, pairings, zero-knowledge, **post-quantum**, homomorphic
     encryption and multi-party protocols. Everything the notes said about the
     RSA-FDH ROM proof, the OAEP ROM proof, the forking lemma, GGM and Shor is
     therefore **background, not examinable material**, and is now marked as such.
  Also used for: lecture 11's NIST key-length table (identical to S27 Table 2),
  the factorization-record table (1991: 330 bits … 2020: 829 bits), and
  lecture 13a's TLS 1.3 handshake and record-layer diagrams, which
  [`../notes/12-tls-and-pki.md`](../notes/12-tls-and-pki.md) is built from.

### S9 — Georg Fuchsbauer, personal homepage

- URL: <https://www.di.ens.fr/~fuchsbau/> (also
  <https://informatics.tuwien.ac.at/people/georg-fuchsbauer> and
  <https://secpriv.wien/team/333531-georg-fuchsbauer/>)
- Retrieved: 2026-09-22. Access: public.
- Used for: lecturer identity (Associate Professor, Security and Privacy group,
  TU Wien) and for establishing that **he hosts no lecture notes or slides for
  192.125 himself** — the teaching section links only to the TISS pages. The
  slides that exist in public are the VoWi uploads S7/S8. The ENS/ESILV decks he
  does host are different, shorter courses and were not used.
- Re-checked 2026-10-07: unchanged. The homepage teaching list says
  Introduction to Cryptography "winter '20 ... and '21-'25" and links only the
  TISS page; the secpriv.wien team page and the group's course list
  <https://secpriv.wien/courses/> link only the 2026W TISS page. There is no
  public course website for 2026W.

### S10 — Katz & Lindell, *Introduction to Modern Cryptography*, 3rd edition

- Authors: Jonathan Katz, Yehuda Lindell. CRC Press, 2020.
- URL: <https://www.cs.umd.edu/~jkatz/imc.html> (authors' page)
- Access: **commercial textbook, not free, not vendored.** TISS names it as the
  book the lecture "mainly follows" [S1]; S8 puts a section number on almost
  every slide. VoWi hosts scanned PDFs of the 2nd and 3rd editions; those were
  **not downloaded**.
- Used for: the chapter and theorem numbering the notes cite. The mapping
  confirmed from S8: sec. 1 introduction, sec. 2 perfect secrecy, sec. 3
  private-key encryption, sec. 4 MACs, sec. 5 CCA and authenticated encryption,
  sec. 6 hash functions, sec. 7 practical constructions (7.1 stream ciphers,
  7.2 block ciphers, 7.3 hash functions), sec. 9 number theory, sec. 10
  factoring/DLog algorithms, sec. 11 key management, sec. 12 public-key
  encryption, sec. 13 signatures (13.4 RSA, 13.5 DL-based, 13.6 PKI, 13.7
  SSL/TLS). Named definitions the slides pin down: Def. 2.3 perfect secrecy,
  Lemma 2.7 indistinguishability, Thm 2.10 one-time pad, Thm 2.12 Shannon,
  Def. 3.4 negligible, Def. 3.14 PRG, Thm 3.16 pseudo-one-time pad,
  Constr. 3.28 CPA-secure encryption from a PRF, Thm 6.4 Merkle-Damgard,
  Def. 12.1 PKE syntax, Def. 13.2 signature security, Thm 13.11 Schnorr
  identification.
- Re-checked 2026-10-07: the authors' page resolves and still describes the 3rd
  edition; it lists the 2023W TU Wien offering among courses using the book.
  The section titles above are now checked against the authors' own table of
  contents [S53]; the definition and theorem numbers still rest on S8 alone.

---

## Past papers and exercise material (all from S5; all cite-only)

### S11 — Elena Andreeva, TU Wien Informatics people page

- URL: <https://informatics.tuwien.ac.at/people/elena-andreeva>
- Retrieved: 2026-09-22. Access: public.
- Used for: the second lecturer's identity and specialism — Tenure-track
  Associate Professor in Cryptography, Security and Privacy research unit
  (E192-06); research on symmetric authenticated encryption, block ciphers,
  forkciphers and hash functions. That is exactly the split the slide archive
  shows: she gives **lecture 3 (block ciphers)** and **lecture 9 (hash
  functions)**, Fuchsbauer the rest [S8]. Like S9, the page links only to TISS
  and hosts **no teaching material**. Re-checked 2026-10-07: unchanged; it lists
  192.125 as current teaching and links nothing beyond TISS.

### S12 — Final exam, 26 January 2024 (2023W), 40 points ★

- URL: <https://vowi.fsinf.at/images/f/f2/TU_Wien-Introduction_to_Cryptography_VU_%28Fuchsbauer%29_-_Exam1_2023W.pdf>
- Retrieved: 2026-09-22 (browser; text extracted with pdf.js in the page).
  **Student upload of an exam paper. Cite-only, not vendored, not reproduced.**
- Used for: [`../notes/00-exam-focus.md`](../notes/00-exam-focus.md) — the paper's
  shape (12 true/false at ±1 with a floor of 0, then five multi-part questions),
  and five topics the notes or code were missing: RSA moduli **sharing a prime
  factor** (`src/py/rsa.py::shared_prime_attack`), the NIST key-length comparison
  between symmetric and public-key schemes, that `x -> x^e mod N` is a
  permutation of `Z_N^*` when `gcd(e, phi(N)) = 1`, that DLog is *easy* in
  `(Z_p, +)`, and a **hybrid encryption scheme that is not CCA-secure**
  (`src/py/elgamal.py::hybrid_cca_attack`).

### S13 — Midterm exam, 3 December 2025 (2025W), 30 points, **with official answers to part 1** ★

- URL: <https://vowi.fsinf.at/images/2/26/TU_Wien-Introduction_to_Cryptography_VU_%28Fuchsbauer%29_-_Midterm_introcrypto-2025-12-03.pdf>
- Retrieved: 2026-09-22 (browser). **Cite-only.**
- Used for: the closest available model of the 2026W midterm (Wed 18.11.2026,
  confirmed on TISS 2026-10-07 [S1]), and the first midterm ever set for this
  course. It was set under the 2025W 50/50 grading;
  2026W weights each partial exam 40 %. Structure: 10 true/false (±1, min 0, max 10), a fill-in-the-gaps
  reconstruction of the **CCA security experiment**, a two-part private-key
  question (prove correctness, then break EAV-security), a **6-point MAC
  reduction**, and "construct a secure authenticated encryption scheme from a
  CPA-secure scheme and a MAC". Its true/false items drove three additions:
  historical ciphers and frequency analysis, the **meet-in-the-middle attack on
  double encryption**, and the exact hypotheses of Shannon's theorem.

### S14 — Sample solutions, assignments 1 and 2

- URLs: <https://vowi.fsinf.at/images/7/77/TU_Wien-Introduction_to_Cryptography_VU_%28Fuchsbauer%29_-_Sample_Solutions_Assignment_1.pdf>,
  <https://vowi.fsinf.at/images/c/c8/TU_Wien-Introduction_to_Cryptography_VU_%28Fuchsbauer%29_-_Sample_Solutions_Assignment_2.pdf>
- Retrieved: 2026-09-22 (browser). Students' own write-ups. **Cite-only.**
- Used for: what the *homework* looks like (half the grade in 2025W): both
  assignments cover lecture 1 and 2 material. Their questions and answers are
  not reproduced in this wiki, since the assignments may be graded again.

### S15 — Final exam, 2 February 2021 (2020W), VO

- URL: <https://vowi.fsinf.at/images/6/6e/TU_Wien-Introduction_to_Cryptography_VU_%28Fuchsbauer%29_-_Pr%C3%BCfung_2021-02-02.pdf>
- Retrieved: 2026-09-22 (browser). **Cite-only.**
- Used for: the oldest paper, from the 3 ECTS VO. Still Fuchsbauer, still the
  same style. Contributes the **one-round Feistel distinguisher**
  (`src/py/test_block_ciphers.py::test_one_round_feistel_barely_diffuses`), the
  broken "`c := F_k(r) xor m` without sending r" scheme, the 80-bit-hash
  question, and a **deterministic Schnorr variant with a fixed nonce in the
  secret key** — an unusually direct way to ask about nonce reuse.

### S16 — Final exam, 31 January 2025 (2024W), 40 points ★

- URL: <https://vowi.fsinf.at/images/f/fb/TU_Wien-Introduction_to_Cryptography_VU_%28Fuchsbauer%29_-_Pr%C3%BCfung_2025-01-31.png>
- Retrieved: 2026-09-22. A photograph of the paper, read from the image.
  **Cite-only.**
- Used for: the most recent *final*. 12 true/false then four questions: CBC
  decryption and why CBC is not CCA-secure, **cascade encryption under two
  independent keys is CPA-secure if either component is**, how to turn a weak
  MAC definition into EUF-CMA, RSA key generation, why PKE's CPA game has no
  encryption oracle, and Schnorr verification plus **nonce-reuse key recovery**.
  Its true/false items contributed: the permutation layer of an SPN provides
  *diffusion* not confusion; the S-box need not be secret; `Z_7^*` is cyclic;
  CDH hard implies DLog hard (**the direction our note 09 had backwards**);
  an l-bit hash gives l/2 not l bits of collision resistance; and
  `[3^1000000 mod 22]`.

### S17 — *Gedächtnisprotokoll*, 26 January 2024

- URL: <https://vowi.fsinf.at/images/b/b7/TU_Wien-Introduction_to_Cryptography_VU_%28Fuchsbauer%29_-_Pr%C3%BCfung_2024-01-26_Ged%C3%A4chtnisprotokoll.pdf>
- Retrieved: 2026-09-22. **Cite-only.** A student's recollection of the same
  sitting as S12, which supersedes it. Listed for completeness; not relied on.

---

## Standards — **vendored**, see [`README.md`](README.md) for licences

### S18 — RFC 8446, *The Transport Layer Security (TLS) Protocol Version 1.3*

- Authors: E. Rescorla. IETF, August 2018. Standards Track.
- URL: <https://www.rfc-editor.org/rfc/rfc8446.txt> · vendored at [`rfc/rfc8446.txt`](rfc/rfc8446.txt)
- Retrieved: 2026-09-22. Licence: IETF Trust, BCP 78 / TLP 5.0 — redistributable
  in full and unmodified.
- Used for: [`../notes/12-tls-and-pki.md`](../notes/12-tls-and-pki.md). The
  handshake message flow (sec. 2), the key schedule and HKDF-Expand-Label
  (sec. 7.1), the record layer (sec. 5), the mandatory AEAD ciphersuites
  (sec. 9.1), and the removal of static-RSA key transport, which is why TLS 1.3
  is a pure (EC)DHE protocol. Checked against the lecture 13a diagram [S8].

### S19 — RFC 2104, *HMAC: Keyed-Hashing for Message Authentication*

- Authors: H. Krawczyk, M. Bellare, R. Canetti. IETF, February 1997. Informational.
- URL: <https://www.rfc-editor.org/rfc/rfc2104.txt> · vendored at [`rfc/rfc2104.txt`](rfc/rfc2104.txt)
- Retrieved: 2026-09-22. Licence: "Distribution of this memo is unlimited."
- Used for: note 07's HMAC definition — the exact ipad/opad constants `0x36`/
  `0x5c` repeated B times, the key-shortening rule for keys longer than the block
  (sec. 2), and the truncation guidance in sec. 5 that
  `test_standard_vectors.py::test_rfc4231_tc5_truncated_output` exercises.
  Verified against `src/py/mac.py::hmac_sha256`.

### S20 — RFC 8017, *PKCS #1: RSA Cryptography Specifications Version 2.2* ★

- Authors: K. Moriarty, B. Kaliski, J. Jonsson, A. Rusch. IETF, November 2016.
  Informational.
- URL: <https://www.rfc-editor.org/rfc/rfc8017.txt> · vendored at [`rfc/rfc8017.txt`](rfc/rfc8017.txt)
- Retrieved: 2026-09-22. Licence: IETF Trust, BCP 78 / TLP 5.0.
- Used for: **`src/py/oaep.py` in its entirety**, and for rewriting note 10's
  OAEP section. I2OSP/OS2IP (sec. 4.1, 4.2), RSAEP/RSADP (sec. 5.1.1, 5.1.2),
  RSAES-OAEP-ENCRYPT (sec. 7.1.1) and -DECRYPT (sec. 7.1.2), MGF1 (appendix
  B.2.1), and the note in sec. 7.1.2 step 3(g) that decryption must not reveal
  *which* check failed. Also sec. 7.2 (PKCS #1 v1.5 encryption) and sec. 8
  (RSASSA-PSS, RSASSA-PKCS1-v1_5), which lectures 12 and 13 name. **RFC 8017
  contains no test vectors** — see S24 for those.

### S21 — FIPS 197, *Advanced Encryption Standard (AES)*

- NIST, November 2001, updated 9 May 2023 (FIPS 197-upd1).
- URL: <https://nvlpubs.nist.gov/nistpubs/FIPS/NIST.FIPS.197-upd1.pdf> ·
  vendored at [`nist/NIST.FIPS.197-upd1.pdf`](nist/NIST.FIPS.197-upd1.pdf)
- Retrieved: 2026-09-22. Licence: US Government work, not subject to copyright
  in the United States (see [`README.md`](README.md)).
- Used for: note 03's AES description, `src/py/block_ciphers.py` and `src/py/aes.py`. GF(2^8)
  arithmetic and the worked `{57} * {83} = {c1}` (sec. 4.2); the S-box definition
  as inverse-then-affine (sec. 5.1.1) and **Table 4**, all 256 bytes of which
  `test_block_ciphers.py` reproduces from the definition; SubBytes/ShiftRows/
  MixColumns/AddRoundKey (sec. 5.1); the key schedule (sec. 5.2); the 128/192/256
  key lengths and 10/12/14 rounds (sec. 5); and **appendix B**, the round-by-round
  AES-128 example whose final state is `3925841d02dc09fbdc118597196a0b32`.
  Note: the -upd1 revision *removed* the example vectors of appendix C in favour
  of a pointer to the NIST CSRC examples page (change log item 23), so the block
  vectors used here come from S25 instead.

### S22 — RFC 4231, *Identifiers and Test Vectors for HMAC-SHA-224/256/384/512*

- Authors: M. Nystrom. IETF, December 2005. Standards Track.
- URL: <https://www.rfc-editor.org/rfc/rfc4231.txt> · vendored at [`rfc/rfc4231.txt`](rfc/rfc4231.txt)
- Retrieved: 2026-09-22. Licence: "Distribution of this memo is unlimited."
- Used for: `test_standard_vectors.py::test_rfc4231_hmac_sha256` — test cases
  1, 2, 3, 4, 6 and 7 from sec. 4, plus case 5 (truncation to 128 bits). Cases 6
  and 7 use a 131-octet key and so exercise the key-shortening rule of S19.

### S23 — RFC 6234, *US Secure Hash Algorithms (SHA and SHA-based HMAC and HKDF)*

- Authors: D. Eastlake 3rd, T. Hansen. IETF, May 2011. Informational.
- URL: <https://www.rfc-editor.org/rfc/rfc6234.txt> · vendored at [`rfc/rfc6234.txt`](rfc/rfc6234.txt)
- Retrieved: 2026-09-22. Licence: IETF Trust, BCP 78 / TLP 5.0.
- Used for: the four SHA-256 test patterns of sec. 8.5 (`"abc"`, the 56-character
  string, `"a"` a million times, and the 640-byte multiple-of-512-bits case),
  reproduced in `test_standard_vectors.py`. Also a readable restatement of the
  SHA-256 compression function that note 08's Merkle-Damgard discussion follows.

### S24 — Project Wycheproof, RSAES-OAEP decryption test vectors

- Authors: Google / C2SP. File
  `testvectors_v1/rsa_oaep_2048_sha256_mgf1sha256_test.json`, 37 test cases.
- URL: <https://github.com/C2SP/wycheproof> ·
  vendored at `vectors/rsa_oaep_2048_sha256_mgf1sha256_test.json`
- Retrieved: 2026-09-22. **Licence: Apache License 2.0**, copy at
  [`vectors/LICENSE-Apache-2.0.txt`](vectors/LICENSE-Apache-2.0.txt).
- Used for: `test_oaep.py`. This is the substitute for RFC 8017's missing test
  vectors: 18 valid ciphertexts whose plaintexts the decoder must recover
  exactly, and 19 malformed ones covering every branch of the sec. 7.1.2 format
  check (modified lHash, modified or all-`0xff` PS, missing `0x01` separator,
  non-zero leading octet, `m = 0`, `m = n-1`, ciphertext not reduced mod n,
  truncated or extended ciphertext). The file's notes also document *why* the
  error must be indistinguishable, citing Manger [S41] and CVE-2020-26939.

### S25 — NIST SP 800-38A, *Recommendation for Block Cipher Modes of Operation*

- NIST, December 2001 edition.
- URL: <https://nvlpubs.nist.gov/nistpubs/Legacy/SP/nistspecialpublication800-38a.pdf>
  · vendored at [`nist/NIST.SP.800-38A.pdf`](nist/NIST.SP.800-38A.pdf)
- Retrieved: 2026-09-22. Licence: "It is not subject to copyright" (p. 2).
- Used for: note 06's mode definitions and the vectors in
  `test_standard_vectors.py`. ECB/CBC/CFB/OFB/CTR (sec. 6), the requirement that
  the CBC IV be unpredictable (appendix C), the **standard incrementing
  function** for CTR that increments the whole block (appendix B.1 — which is why
  `private_key.ctr_keystream_from` exists alongside the nonce||counter variant),
  and appendix F.1.1/F.1.2, F.2.1/F.2.2, F.5.1/F.5.2: the AES-128 ECB, CBC and
  CTR vectors over the four plaintext blocks beginning `6bc1bee2...`.

### S26 — RFC 3526, *MODP Diffie-Hellman groups for IKE*

- Authors: T. Kivinen, M. Kojo. IETF, May 2003. Standards Track.
- URL: <https://www.rfc-editor.org/rfc/rfc3526.txt> · vendored at [`rfc/rfc3526.txt`](rfc/rfc3526.txt)
- Retrieved: 2026-09-22. Licence: "Distribution of this memo is unlimited."
- Used for: note 10's Diffie-Hellman section (`dh.MODP2048`) and
  `test_standard_vectors.py::test_rfc3526_group14_is_a_safe_prime_with_generator_2`.
  The 2048-bit group 14 (sec. 3) is a **safe prime** `p = 2q + 1` with generator
  2; the test confirms both primalities and that 2 has order q, which is the
  concrete instance behind the notes' insistence on prime-order subgroups.

### S27 — NIST SP 800-57 Part 1 Rev. 5, *Recommendation for Key Management*

- NIST, May 2020.
- URL: <https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-57pt1r5.pdf>
  · vendored at [`nist/NIST.SP.800-57pt1r5.pdf`](nist/NIST.SP.800-57pt1r5.pdf)
- Retrieved: 2026-09-22. Licence: "not subject to copyright in the United
  States" (p. ii).
- Used for: **Table 2**, the comparable-security-strengths table that lecture 11
  reproduces slide-for-slide [S8] and that the 26 Jan 2024 and 31 Jan 2025 papers
  both examine [S12, S16]:

  | security strength | symmetric | FFC (DSA/DH) | IFC (RSA) | ECC |
  |---|---|---|---|---|
  | 112 | 3TDEA | L = 2048, N = 224 | k = 2048 | f = 224-255 |
  | 128 | AES-128 | L = 3072, N = 256 | k = 3072 | f = 256-383 |
  | 192 | AES-192 | L = 7680, N = 384 | k = 7680 | f = 384-511 |
  | 256 | AES-256 | L = 15360, N = 512 | k = 15360 | f = 512+ |

  Also for the footnote deprecating 3TDEA, and for the `<= 80` row (2TDEA,
  1024-bit RSA) no longer being approved.

### S28 — FIPS 180-4, *Secure Hash Standard (SHS)*

- NIST, August 2015.
- URL: <https://nvlpubs.nist.gov/nistpubs/FIPS/NIST.FIPS.180-4.pdf> ·
  vendored at [`nist/NIST.FIPS.180-4.pdf`](nist/NIST.FIPS.180-4.pdf)
- Retrieved: 2026-09-22. Licence: US Government work.
- Used for: note 08 — SHA-1/224/256/384/512 parameters, the padding rule
  (append `1`, then zeros, then the 64-bit length: the *length strengthening*
  the Merkle-Damgard theorem needs), and the digest sizes behind the birthday
  arithmetic. FIPS 180-4 prints no example digests; those come from S23.

### S29 — FIPS 198-1, *The Keyed-Hash Message Authentication Code (HMAC)*

- NIST, July 2008.
- URL: <https://nvlpubs.nist.gov/nistpubs/FIPS/NIST.FIPS.198-1.pdf> ·
  vendored at [`nist/NIST.FIPS.198-1.pdf`](nist/NIST.FIPS.198-1.pdf)
- Retrieved: 2026-09-22. Licence: US Government work.
- Used for: note 07's HMAC section — the standardised version of S19, and its
  security guidance on key length (at least L/2 bits) and tag truncation.

### S30 — FIPS 186-5, *Digital Signature Standard (DSS)*

- NIST, February 2023.
- URL: <https://nvlpubs.nist.gov/nistpubs/FIPS/NIST.FIPS.186-5.pdf> ·
  vendored at [`nist/NIST.FIPS.186-5.pdf`](nist/NIST.FIPS.186-5.pdf)
- Retrieved: 2026-09-22. Licence: US Government work.
- Used for: note 11's (EC)DSA section. ECDSA signature generation (sec. 6.4) —
  `r = x-coordinate of kG mod n`, `s = k^-1 (H(m) + r d) mod n` — the EdDSA
  specification (sec. 7), and two things the notes now state on its authority:
  FIPS 186-5 **withdraws DSA** for signature generation (it may only be verified),
  and it permits **deterministic per-message secrets** (sec. 6.4.2), which is the
  standardised answer to nonce reuse.

### S31 — NIST SP 800-38D, *Galois/Counter Mode (GCM) and GMAC*

- NIST, November 2007.
- URL: <https://nvlpubs.nist.gov/nistpubs/Legacy/SP/nistspecialpublication800-38d.pdf>
  · vendored at [`nist/NIST.SP.800-38D.pdf`](nist/NIST.SP.800-38D.pdf)
- Retrieved: 2026-09-22. Licence: US Government work.
- Used for: note 07's GCM paragraph. GHASH as polynomial evaluation in
  GF(2^128) keyed by `H = CIPH_K(0^128)` (sec. 6.3, 6.4), the encryption
  procedure (sec. 7.1), and **appendix A**, the uniqueness requirement on the
  IV — which states in the standard's own words that reusing an IV with the same
  key lets an adversary recover the hash subkey and forge. The document prints no
  test vectors; those live in a separate CAVP file that was not fetched.

### S32 — RFC 6979, *Deterministic Usage of DSA and ECDSA*

- Authors: T. Pornin. IETF, August 2013. Informational.
- URL: <https://www.rfc-editor.org/rfc/rfc6979.txt> · vendored at [`rfc/rfc6979.txt`](rfc/rfc6979.txt)
- Retrieved: 2026-09-22. Licence: IETF Trust, BCP 78 / TLP 5.0.
- Used for: note 11's nonce-reuse pitfall — the standard fix, `k` derived by
  HMAC-DRBG from the private key and the message hash (sec. 3.2).

### S33 — RFC 8032, *Edwards-Curve Digital Signature Algorithm (EdDSA)*

- Authors: S. Josefsson, I. Liusvaara. IETF, January 2017. Informational.
- URL: <https://www.rfc-editor.org/rfc/rfc8032.txt> · vendored at [`rfc/rfc8032.txt`](rfc/rfc8032.txt)
- Retrieved: 2026-09-22. Licence: IETF Trust, BCP 78 / TLP 5.0.
- Used for: note 11 — Ed25519 as the deployed descendant of Schnorr signatures,
  with deterministic nonces by construction (sec. 5.1.6).

### S34 — RFC 5869, *HMAC-based Extract-and-Expand Key Derivation Function (HKDF)*

- Authors: H. Krawczyk, P. Eronen. IETF, May 2010. Informational.
- URL: <https://www.rfc-editor.org/rfc/rfc5869.txt> · vendored at [`rfc/rfc5869.txt`](rfc/rfc5869.txt)
- Retrieved: 2026-09-22. Licence: IETF Trust, BCP 78 / TLP 5.0.
- Used for: notes 11 and 12 — what the lecture-11 slide calls the
  "key-derivation function" applied to the Diffie-Hellman value, and the
  extract-then-expand structure TLS 1.3 builds its key schedule from [S18].

### S35 — RFC 5116, *An Interface and Algorithms for Authenticated Encryption*

- Authors: D. McGrew. IETF, January 2008. Standards Track.
- URL: <https://www.rfc-editor.org/rfc/rfc5116.txt> · vendored at [`rfc/rfc5116.txt`](rfc/rfc5116.txt)
- Retrieved: 2026-09-22. Licence: "Distribution of this memo is unlimited."
- Used for: note 07's AEAD definition — the (key, nonce, plaintext, associated
  data) interface, and the requirement in sec. 5.1.1 that a nonce never repeat
  for a given key.

### S36 — RFC 8439, *ChaCha20 and Poly1305 for IETF Protocols*

- Authors: Y. Nir, A. Langley. IETF, June 2018. Informational.
- URL: <https://www.rfc-editor.org/rfc/rfc8439.txt> · vendored at [`rfc/rfc8439.txt`](rfc/rfc8439.txt)
- Retrieved: 2026-09-22. Licence: IETF Trust, BCP 78 / TLP 5.0.
- Used for: note 06's remark that modern stream ciphers are block functions in
  counter mode — ChaCha20 is exactly that (sec. 2.4) — and note 12's TLS 1.3
  ciphersuite list.

### S37 — IETF Trust Legal Provisions (TLP) 5.0

- URL: <https://trustee.ietf.org/documents/trust-legal-provisions/tlp-5/>
- Retrieved: 2026-09-22. Access: public.
- Used for: the licence basis for vendoring the post-2008 RFCs — sec. 3.c.i
  grants an unlimited right to copy, publish, display and distribute IETF
  Documents **in full and without modification**. See [`README.md`](README.md).

### S38 — NIST copyright statement

- URL: <https://www.nist.gov/oism/copyrights>
- Retrieved: 2026-09-22. Access: public.
- **Moved (checked 2026-10-07):** the URL above now redirects to the general
  <https://www.nist.gov/copyrights-disclaimers> page, which no longer states the
  publications rule itself. The statement now lives at
  <https://www.nist.gov/open/copyright-fair-use-and-licensing-statements-srd-data-software-and-technical-series-publications>:
  works by NIST employees not covered by the Standard Reference Data Act "are
  subject to 17 U.S.C. §105 and generally are not subject to copyright
  protection within the United States". The vendoring basis is unchanged.
- Used for: the licence basis for vendoring the FIPS and SP documents. NIST
  publications are works of the US Government and are not subject to copyright
  protection in the United States (17 U.S.C. sec. 105). SP 800-38A says so on its
  own page 2 and SP 800-57 on its page ii.

---

## Primary literature (cite-only; none of these is redistributable)

### S39 — Bellare & Rogaway, *Optimal Asymmetric Encryption*, EUROCRYPT 1994

- URL: <https://web.cs.ucdavis.edu/~rogaway/papers/oae.pdf> (author-hosted)
- Retrieved: 2026-09-22. Access: free download, no licence statement ⇒ not vendored.
- Used for: note 10 — the original OAEP construction and the "all-or-nothing"
  intuition, and the fact that the original claim was IND-CCA2 for *any*
  one-way trapdoor permutation. See S40 for why that claim did not survive.

### S40 — Shoup, *OAEP Reconsidered*, CRYPTO 2001; and Fujisaki, Okamoto, Pointcheval & Stern, *RSA-OAEP is Secure under the RSA Assumption*, CRYPTO 2001

- URLs: <https://eprint.iacr.org/2000/060> and <https://eprint.iacr.org/2000/061>
- Retrieved: 2026-09-22. Access: IACR ePrint, free. Not vendored.
- 2026-10-07: abstract pages resolve; the `.pdf` links (and S45b, S49) now sit
  behind a Cloudflare challenge that `curl` and a scripted fetch cannot pass
  (HTTP 403), so `fetch-sources.sh --papers` reports them as failed. Open them
  from the abstract page in a browser.
- Used for: **a correction to note 10.** Shoup showed the S39 proof is flawed and
  that OAEP is *not* generically CCA-secure from one-wayness alone; Fujisaki et
  al. rescued the RSA instance specifically, proving RSA-OAEP CCA-secure in the
  random-oracle model under the RSA assumption, with a loose reduction. The note
  previously said "OAEP turns RSA into a CCA-secure scheme (in the ROM)" with no
  qualification.

### S41 — Manger, *A Chosen Ciphertext Attack on RSA Optimal Asymmetric Encryption Padding (OAEP) as Standardized in PKCS #1 v2.0*, CRYPTO 2001

- URL: <https://www.iacr.org/archive/crypto2001/21390229.pdf>
- Retrieved: 2026-09-22. Access: free from IACR. Not vendored.
- Used for: note 10 and the `src/py/oaep.py` docstring — why RFC 8017 sec. 7.1.2
  step 3(g) insists the decoder must not reveal which check failed. Distinguishing
  "integer too large" from "bad padding" recovers the plaintext in about `k`
  oracle queries for a `k`-bit modulus.

### S42 — Bleichenbacher, *Chosen Ciphertext Attacks Against Protocols Based on the RSA Encryption Standard PKCS #1*, CRYPTO 1998

- URL: <https://link.springer.com/chapter/10.1007/BFb0055716>
- Retrieved: 2026-09-22. Access: Springer, paywalled abstract. Not vendored.
- Used for: note 10 — why lecture 12 presents PKCS #1 v1.5 only as the thing
  v2.0 replaced. The "million-message attack" is the public-key analogue of the
  padding oracle in note 06.

### S43 — Luby & Rackoff, *How to Construct Pseudorandom Permutations from Pseudorandom Functions*, SIAM J. Comput. 17(2), 1988

- URL: <https://epubs.siam.org/doi/10.1137/0217022>
- Retrieved: 2026-09-22. Access: SIAM, paywalled. Not vendored.
- Used for: note 05's claim that three Feistel rounds give a PRP and four a
  strong PRP, given independent PRF round functions. **Marked as background**:
  S8 shows lecture 3 presents Feistel networks structurally, without the
  Luby-Rackoff theorem.

### S44 — Goldreich, Goldwasser & Micali, *How to Construct Random Functions*, JACM 33(4), 1986

- URL: <https://dl.acm.org/doi/10.1145/6490.6503>
- Retrieved: 2026-09-22. Access: ACM, paywalled. Not vendored.
- Used for: note 05's GGM tree. **Marked as out of scope**: it is Katz-Lindell
  sec. 8, which lecture 13a explicitly lists under "cryptography from minimal
  assumptions — what we did not cover" [S8].

### S45 — Bellare & Rogaway, *Random Oracles are Practical*, ACM CCS 1993; and Canetti, Goldreich & Halevi, *The Random Oracle Methodology, Revisited*, JACM 51(4), 2004

- URLs: <https://cseweb.ucsd.edu/~mihir/papers/ro.pdf> and
  <https://eprint.iacr.org/1998/011>
- Retrieved: 2026-09-22. Access: free. Not vendored.
- **Dead link fixed 2026-10-07:** the former URL
  `https://web.cs.ucdavis.edu/~rogaway/papers/ro.pdf` returns 404. Rogaway's own
  paper list now points to Bellare's copy, the URL above (HTTP 200, PDF).
- Used for: note 08's random-oracle section — the methodology, and the
  separation result showing there are schemes secure in the ROM yet insecure
  under *every* concrete hash. **Marked as background** per S8.

### S46 — Pointcheval & Stern, *Security Arguments for Digital Signatures and Blind Signatures*, J. Cryptology 13(3), 2000

- URL: <https://www.di.ens.fr/david.pointcheval/Documents/Papers/2000_joc.pdf>
- Retrieved: 2026-09-22. Access: author-hosted, free. Not vendored.
- Used for: note 11's forking lemma. **Marked as background** per S8; lecture 13
  states Thm 13.11 (Schnorr identification is secure under DLog) and does not
  prove the signature version.

### S47 — Heninger, Durumeric, Wustrow & Halderman, *Mining Your Ps and Qs: Detection of Widespread Weak Keys in Network Devices*, USENIX Security 2012

- URL: <https://factorable.net/weakkeys12.extended.pdf>
- Retrieved: 2026-09-22. Access: author-hosted, free. Not vendored.
- Used for: `src/py/rsa.py::shared_prime_attack` and note 10 — the shared-prime
  question of S12 is not hypothetical; the paper factored a measurable fraction
  of the public TLS and SSH RSA keys on the internet by computing GCDs across
  moduli generated with low-entropy embedded RNGs.

### S48 — Vaudenay, *Security Flaws Induced by CBC Padding*, EUROCRYPT 2002

- URL: <https://www.iacr.org/archive/eurocrypt2002/23320530/cbc02_e02d.pdf>
- Retrieved: 2026-09-22. Access: free from IACR. Not vendored.
- Used for: note 06's padding-oracle attack, which the lecture-7 slide "Too
  paranoid? No! Padding-oracle attack" motivates CCA-security with [S8].

### S49 — Bellare & Namprempre, *Authenticated Encryption: Relations among Notions and Analysis of the Generic Composition Paradigm*, ASIACRYPT 2000

- URL: <https://eprint.iacr.org/2000/025>
- Retrieved: 2026-09-22. Access: IACR ePrint, free. Not vendored.
- Used for: note 07's encrypt-then-MAC / MAC-then-encrypt / encrypt-and-MAC
  table, and the precise statement that EtM with a CPA-secure scheme and a
  strongly unforgeable MAC always yields authenticated encryption, while the
  other two do not in general.

### S50 — Shannon, *Communication Theory of Secrecy Systems*, Bell System Technical Journal 28(4), 1949

- URL: <https://archive.org/details/bstj28-4-656> (PDF:
  <https://archive.org/download/bstj28-4-656/bstj28-4-656.pdf>)
- Retrieved: 2026-09-22. Access: free archival copy; Bell Labs copyright. Not vendored.
- **Moved 2026-10-07:** the former storage-node URL
  `https://ia903406.us.archive.org/33/items/bstj28-4-656/bstj28-4-656.pdf` no
  longer answers (connection timeout). The stable item URLs above resolve (PDF,
  30 MB).
- Used for: note 02's perfect secrecy and the key-length bound, and note 03's
  confusion/diffusion goals, which lecture 3 attributes to the same paper [S8].

### S51 — Diffie & Hellman, *New Directions in Cryptography*, IEEE Trans. Inf. Theory 22(6), 1976

- URL: <https://ee.stanford.edu/~hellman/publications/24.pdf>
- Retrieved: 2026-09-22. Access: author-hosted, free. IEEE copyright. Not vendored.
- Used for: note 10's key-exchange section; the lecture-11 slide names the paper
  by title [S8].

### S52 — Rivest, Shamir & Adleman, *A Method for Obtaining Digital Signatures and Public-Key Cryptosystems*, CACM 21(2), 1978

- URL: <https://people.csail.mit.edu/rivest/Rsapaper.pdf>
- Retrieved: 2026-09-22. Access: author-hosted, free. ACM copyright. Not vendored.
- Used for: note 10's RSA section.

---

## Textbooks and free companions (added 2026-10-07; cite-only)

TISS names only Katz-Lindell [S1]; nothing else is officially recommended. The
entries below were added on the 2026-10-07 audit as free, lawful companions.
None is vendored. *Comparability* says how close each is to what 192.125 teaches.

### S53 — Katz & Lindell, 3rd ed., table of contents and preface

- URL: <https://www.cs.umd.edu/~jkatz/imc/toc-preface-3rd.pdf> (linked from S10)
- Retrieved: 2026-10-07. Access: free, author-hosted. Licence: none stated,
  publisher copyright. Not vendored.
- Covers: every chapter and section title of the course textbook, with page
  numbers.
- Comparability: exact (it is the course book). Used to check the section
  numbers in [`lecture-notes-map.md`](lecture-notes-map.md): all agree, with one
  precision: *historical ciphers* is sec. 1.3, which the lecture-1 deck covers
  but whose header names only 1.2 and 1.4 [S8].

### S54 — Katz & Lindell, 3rd ed., errata

- URL: <https://www.cs.umd.edu/~jkatz/imc/errata-3rd.pdf> (last updated
  23 July 2024)
- Retrieved: 2026-10-07. Access: free, author-hosted. Not vendored.
- Covers: nine corrections. Two touch our notes: p. 170, second-preimage
  resistance implies preimage resistance only under extra conditions (note 08);
  p. 483, a sign error in the DSA/ECDSA nonce-reuse algebra of sec. 13.5.3
  (note 11). Flagged for the notes owners, not checked against the notes here.
- Comparability: exact.

### S55 — Boneh & Shoup, *A Graduate Course in Applied Cryptography*, version 0.6

- URL: <https://toc.cryptobook.us/> (PDF:
  <https://crypto.stanford.edu/~dabo/cryptobook/BonehShoup_0_6.pdf>, 9.1 MB,
  January 2023)
- Retrieved: 2026-10-07. Access: free download from the authors. Licence: none
  stated in the front matter, so all rights reserved. Not vendored;
  `fetch-sources.sh --papers` puts a copy in the git-ignored `vendor/`.
- Covers: Part I secret-key (encryption, stream and block ciphers, CPA,
  message integrity, universal hashing, collision-resistant hashing,
  authenticated encryption) and Part II public-key (public-key tools including
  DH, PKE, CCA-secure PKE, signatures, identification, sigma protocols, and
  much beyond this course).
- Comparability: same topics, graduate level and concrete-security style
  (advantages, not asymptotics); notation differs from Katz-Lindell. Best second
  reading for block ciphers (notes 03, 05), CPA/CCA and AE (06, 07) and
  Schnorr/Fiat-Shamir (11). Goes far beyond the exam.

### S56 — Rosulek, *The Joy of Cryptography*, online edition

- URL: <https://joyofcryptography.com/>
- Retrieved: 2026-10-07. Access: free online. **Licence: CC BY-NC-ND 4.0**
  (stated on the page; print edition MIT Press 2026). Not vendored: the licence
  would allow an unmodified non-commercial copy, but the refs convention
  vendors standards only.
- Covers: provable security in the "code-based games" style: one-time pad,
  secret sharing, PRGs, PRFs, PRPs, CPA, CCA, collision-resistant and universal
  hashing, random oracles, key exchange, PKE, RSA, signatures, then messaging,
  authenticated key exchange, zero knowledge and post-quantum (2026 edition).
- Comparability: same syllabus as the first half of 192.125 at the same level;
  the security definitions are phrased as pairs of libraries rather than as
  Katz-Lindell experiments, so translate before quoting it in an exam answer.
  Good drill material for notes 04-07 and 13.

### S57 — Katz, CMSC 456 lecture schedule and slides, Spring 2019 (UMD)

- URL: <http://www.cs.umd.edu/~jkatz/crypto/s19/lectures.html> (linked from S10)
- Retrieved: 2026-10-07. Access: free, `.pptx` decks. Licence: none stated.
  Not vendored.
- Covers: a full undergraduate course by the textbook's first author, each
  lecture with its Katz-Lindell reading.
- Comparability: medium. Same book but the **2nd edition** numbering, and a
  different order (historical ciphers spread over two lectures, number theory
  earlier). Useful as an independent second set of slides, not as a model of
  the TU Wien exams.

---

## Link audit, 2026-10-07

Every URL in this file, in [`README.md`](README.md) and in
[`fetch-sources.sh`](fetch-sources.sh) was requested on 2026-10-07 (curl; the
TISS pages, VoWi and IACR ePrint also in a browser).

- **All vendored files are byte-identical to upstream**: the eleven RFCs, the
  seven NIST PDFs, the Wycheproof JSON and its licence were re-downloaded and
  match `SHA256SUMS`.
- **Dead or moved, fixed above:** S38 (NIST copyright page moved), S45 (the
  Bellare-Rogaway ROM paper, 404 at UC Davis, now Bellare's UCSD copy), S50
  (archive.org storage node timed out, stable item URL used).
- **Reachable only in a browser:** VoWi (Anubis proof-of-work page for curl;
  the browser passes it unaided) and the IACR ePrint PDFs of S40, S45b, S49
  (Cloudflare challenge, HTTP 403 for curl and for scripted fetches; abstract
  pages resolve). ACM (S44) and SIAM (S43) return 403 to curl; both are
  paywalled landing pages and are cited by DOI only.
- **Not checked, login required:** TUWEL (course id 84457, from S1), LectureTube
  recordings, the VoWi Mattermost channel. No login was attempted.
- Every other URL answered HTTP 200 with the content cited.

## What sourcing this course could *not* establish

1. **No exercise sheet is public.** Only *sample solutions* to assignments 1 and
   2 [S14], written by students, and those only for the first two weeks. The
   remaining seven of the nine assignments (86-87 of the 150 ECTS hours; half
   the grade in 2025W, 20 % plus the exam threshold in the 2026-09-28 record)
   live in TUWEL, which needs a login and was not touched. Where the notes give
   homework-style problems beyond assignments 1-2, they are ours, and
   [`../notes/00-exam-focus.md`](../notes/00-exam-focus.md) says so.
2. **The next midterm has no direct precedent but one.** Midterms began in
   2025W [S5, S3], so S13 is the *only* midterm paper in existence. It is a
   sample of one.
3. **Answer keys exist for part 1 of S13 only.** The true/false answers on the
   midterm are the lecturer's; every other answer in `00-exam-focus.md` is ours.
4. **No slide deck for 2026W**, and 2025W's covers only lectures 1-8 [S7]. The
   second half is reconstructed from the 2024W archive [S8], which was taught by
   the same two people from the same book, but is a year old.
5. **No recording, no script.** TISS says lectures are recorded "and made
   available on TUWEL" [S1]; that is login-only.
6. **Katz-Lindell itself was not read.** The notes cite its chapter, theorem and
   construction numbers on the authority of the slide headers [S8, S10]; the page
   numbers and exact wording of its statements are not verified here.
