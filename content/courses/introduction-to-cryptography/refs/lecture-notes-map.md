# Lecture → Katz-Lindell → note → code

Extracted from the 2024W slide archive [S8], which heads almost every deck and
section divider with its Katz-Lindell section number, cross-checked against the
2025W deck [S7] for lectures 1-8. Fourteen decks, thirteen lecture slots plus
a short `13a`. Katz-Lindell numbering is the **3rd edition** [S10] — the switch
from the 2nd happened in 2024W [S3, S4].

Our notes are numbered to follow this order. Two of the fourteen decks are
Andreeva's, and they are the two that go deepest into how a primitive is
actually built — which matches her research area, symmetric primitives and hash
functions [S11]; Fuchsbauer gives the rest [S9].

| # | Lecture (slide title) | Given by | K&L | Our note | Our code |
|---|---|---|---|---|---|
| — | (exam guide, not a lecture) | — | — | [00](../notes/00-exam-focus.md) | — |
| 1 | Admin, introduction, historical ciphers | Fuchsbauer | 1.2, 1.4 (and 1.3) | [01](../notes/01-historical-ciphers.md) | `classical.py` |
| 2 | Modern cryptography, the one-time pad | Fuchsbauer | 2 | [02](../notes/02-perfect-secrecy.md) | `otp.py`, `classical.py` |
| 3 | Block ciphers | Andreeva | 7.2 | [03](../notes/03-block-ciphers.md) | `block_ciphers.py`, `private_key.py` |
| 4 | Stream ciphers and computational security | Fuchsbauer | 7.1, 3.1 | [04](../notes/04-computational-security.md) | `prg.py` |
| 5 | Pseudorandomness, proofs by reduction | Fuchsbauer | 3.3.1-3.3.3 | [05](../notes/05-pseudorandomness.md) | `prg.py` |
| 6 | PRFs, CPA-secure encryption | Fuchsbauer | 3.4.2, 3.5.1, 3.5.2 | [06](../notes/06-private-key-encryption.md) | `private_key.py` |
| 7 | Modes of operation, CCA | Fuchsbauer | 3.6.3, 5.1 | [06](../notes/06-private-key-encryption.md) | `private_key.py` |
| 8 | Authentication, MACs, AE, secure sessions | Fuchsbauer | 4, 5.2, 5.4 | [07](../notes/07-macs-and-ae.md) | `mac.py` |
| 9 | Hash functions | Andreeva | 6, 6.2, 6.3, 6.6.2, 7.3 | [08](../notes/08-hash-functions.md) | `hashing.py` |
| 10 | Number-theoretic background | Fuchsbauer | 9.1.2, 9.1.3 | [09](../notes/09-number-theory.md) | `numtheory.py` |
| 11 | DLog, public-key cryptography | Fuchsbauer | 10, 11, 12 | [09](../notes/09-number-theory.md), [10](../notes/10-key-exchange-pke.md) | `numtheory.py`, `dh.py`, `elgamal.py` |
| 12 | DHIES, RSA encryption, digital signatures | Fuchsbauer | 12.3, 12.4.2, 12.5, 13 | [10](../notes/10-key-exchange-pke.md), [11](../notes/11-digital-signatures.md) | `elgamal.py`, `rsa.py`, `oaep.py` |
| 13 | RSA-FDH, Schnorr, DSA, PKI | Fuchsbauer | 13.4, 13.5, 13.6 | [11](../notes/11-digital-signatures.md), [12](../notes/12-tls-and-pki.md) | `signatures.py` |
| 13a | SSL/TLS, outro | Fuchsbauer | 13.7 | [12](../notes/12-tls-and-pki.md) | — |
| — | (synthesis, not a lecture) | — | — | [13](../notes/13-proof-toolkit.md) | all |

Lecture 1's deck header names K&L 1.2 and 1.4 [S8]; the historical ciphers
themselves are sec. 1.3 in the 3rd edition's table of contents [S53]. Every
other section number above agrees with S53.

The **midterm** of 3 December 2025 [S13] covered lectures 1-8; its last question
is on authenticated encryption, K&L sec. 5.2, which is the end of lecture 8.
In 2026W the midterm is **Wed 18 November 2026**, two weeks earlier in the term,
after only seven lecture Thursdays [S1]. Expect it to stop at lecture 7 (notes
01-06) at most; MACs and AE (note 07) are on it only if the decks move faster
than in 2024W.

## 2026W calendar, projected onto the decks

TISS lists 15 lecture Thursdays and 13 exercise sessions for 2026W [S1]; there
is no 2026W deck or syllabus in public, so the deck column is the **2024W order
[S8] laid onto the 2026W dates, one deck per Thursday**. It is a projection,
not an announcement. 2026W has one more lecture slot than there are decks; where
it falls (a split deck, a Q&A, revision) is unknown.

| date | projected deck | our notes | exam |
|---|---|---|---|
| Thu 01.10.2026 | 1 historical ciphers | 01 | midterm |
| Thu 08.10.2026 | 2 perfect secrecy | 02 | midterm |
| Thu 15.10.2026 | 3 block ciphers (Andreeva) | 03 | midterm |
| Thu 22.10.2026 | 4 stream ciphers, computational security | 04 | midterm |
| Thu 29.10.2026 | 5 PRGs, reductions | 05 | midterm |
| Thu 05.11.2026 | 6 PRFs, CPA | 06 | midterm |
| Thu 12.11.2026 | 7 modes, CCA | 06 | midterm |
| **Wed 18.11.2026** | **midterm**, 12:00-14:00, Audimax | 00, 01-06, 13 | |
| Thu 19.11.2026 | 8 MACs, AE, secure sessions | 07 | final |
| Thu 26.11.2026 | 9 hash functions (Andreeva) | 08 | final |
| Thu 03.12.2026 | 10 number theory | 09 | final |
| Thu 10.12.2026 | 11 DLog, DH, PKE | 09, 10 | final |
| Thu 17.12.2026 | 12 DHIES, RSA, signatures | 10, 11 | final |
| Thu 07.01.2027 | 13 RSA-FDH, Schnorr, DSA, PKI | 11, 12 | final |
| Thu 14.01.2027 | 13a TLS, outro (no exercise session that day) | 12 | final |
| Thu 21.01.2027 | spare slot | 13 | final |
| **Fri 29.01.2027** | **final**, 10:00-12:00, Audimax | 00, 07-13 | |
| Fri 26.02.2027 | retake of either partial exam | | |

Whether the final also examines midterm material is not stated on TISS; the
2025W final is not public, so this is open. The nine assignments fall on the 13
exercise Thursdays (08.10.2026 to 21.01.2027, not 14.01.2027) in an unknown
rhythm, and their sheets are in TUWEL only.

## Syllabus topics with no note

The TISS subject list (seven items [S1]) is fully covered: information-theoretic
security (02), computational security (04, 05), private-key encryption (03, 06),
MACs (07), hash functions (08), PKE (09, 10), signatures (11). Historical
ciphers (01) and TLS (12) are on the slides and VoWi but not in the TISS list.
Against the Katz-Lindell sections the deck headers name [S8, S53], checked on
2026-10-07 by searching the notes:

| K&L section | lecture | gap |
|---|---|---|
| 7.1.1-7.1.4 LFSRs, nonlinearity, Trivium, RC4 | 4 | **no note covers them**; note 04 cites 7.1 but treats only PRG-based and ChaCha20 stream ciphers |
| 11.1-11.2 key distribution, key-distribution centres | 11 | **no note**; note 10 starts at Diffie-Hellman (11.3) |
| 4.5 GMAC and Poly1305, 4.6 information-theoretic MACs | 8 (header says "4") | only a mention of Poly1305 in note 12; unknown whether the lecture covers them |
| 6.6.2 Merkle trees | 9 | covered in note 08 |
| 10 factoring and DLog algorithms | 11 | named with running times only, by design (see below) |

The 2024W deck order is the only evidence for which subsections are taught; the
first two rows are worth closing before the 22.10.2026 and 10.12.2026 lectures.

## Named results the slides pin down

Useful because a past paper can quote "Definition 2.3" or "Construction 3.28"
and expect recognition.

| Label | Statement | Note |
|---|---|---|
| Def. 1.2 | syntax of a private-key encryption scheme | 01 |
| — | Kerckhoffs' principle (1883): Enc and Dec are public | 01 |
| Def. 2.3 | perfect secrecy | 02 |
| Lemma 2.7 | perfect secrecy ⟺ perfect indistinguishability | 02 |
| Thm 2.10 | the one-time pad is perfectly secret | 02 |
| Thm 2.12 | Shannon: characterisation and the \|K\| ≥ \|M\| bound | 02 |
| Def. 3.4 | negligible function | 04 |
| Def. 3.14 | pseudorandom generator | 05 |
| Thm 3.16 | the pseudo-one-time pad is EAV-secure if G is a PRG | 05 |
| Constr. 3.28 | CPA-secure encryption from a PRF: `(r, F_k(r) ⊕ m)` | 06 |
| Thm 6.4 | Merkle-Damgard preserves collision resistance | 08 |
| Def. 12.1 | syntax of a public-key encryption scheme | 10 |
| Def. 13.2 | EUF-CMA for signatures | 11 |
| Thm 13.11 | Schnorr identification is secure under DLog | 11 |

## What the lecturer says is *not* covered

The closing slide of lecture 13a [S8], verbatim in substance:

> **What we did not cover…**
> - Security proofs for public-key schemes (often in the random-oracle model)
> - Cryptography from minimal assumptions (foundations…)
> - Algorithms for factoring and computing discrete logs
> - Further public-key encryption and signature schemes (see Katz-Lindell)
>
> **Advanced topics** (master course: Advanced Cryptography):
> - Proofs in the ROM, pairing-based cryptography
> - (Zero-knowledge) proof systems
> - Post-quantum cryptography, homomorphic encryption
> - Cryptographic protocols (more than 2 participants)

Consequences for these notes, all now marked `(background)` where they appear:

| Material | Status | Where |
|---|---|---|
| RSA-FDH security proof in the ROM | background — the *scheme* is examinable, the proof is not | 11 |
| RSA-OAEP CCA proof in the ROM | background | 10 |
| Fiat-Shamir / the forking lemma | background; Thm 13.11 (identification) *is* stated | 11 |
| GGM: PRG ⇒ PRF (K&L sec. 8) | out of scope — "minimal assumptions" | 05 |
| Baby-step giant-step, Pollard rho, Pohlig-Hellman, NFS (K&L sec. 10) | named with their running times in lecture 11, algorithms not covered | 09 |
| Cramer-Shoup | out of scope — "further public-key schemes" | 10 |
| Post-quantum, Shor | explicitly a master-course topic | 09 |

That does not make them worthless: the notes keep them because a QIST student
should know them, and because lecture 11 *does* quote the running times
(`2^(O(l^(1/3) (log l)^(2/3)))` for NFS, `≈ 2^(n/2)` for generic DLog) that the
NIST key-length table rests on. They are simply not what the exam asks for.
