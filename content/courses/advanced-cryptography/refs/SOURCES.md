# Sources: 192.115 Advanced Cryptography

Register of every source behind [`../notes`](../notes/README.md) and
[`../src`](../src/README.md); both cite it as `[S<n>]`. All URLs were
fetched or probed on **2026-09-28**. "Read" means the text was extracted and
the cited passages checked; "title checked" means only the landing page or
PDF header was confirmed; "cite only" means not fetched (paywalled or not
free).

**Vendored** (free to redistribute, see [`README.md`](README.md)): FIPS 203
and 204 in `nist/`, RFC 7748 and 8032 in `rfc/`, with
`SHA256SUMS`. **Downloadable** (free to read, not ours to redistribute):
fetched by [`fetch-sources.sh`](fetch-sources.sh) `--papers` into the
git-ignored `cite-only/`. **Nothing from TUWEL** (login required, and not
ours to copy).

---

## Course-authoritative

### S1: TISS course page 2026S (transcription)
- File: [`../docs/tiss.md`](../docs/tiss.md), transcribed 2026-09-28 from
  <https://tiss.tuwien.ac.at/course/courseDetails.xhtml?courseNr=192115&semester=2026S>.
- Used for: offerings (2021S, 2023S, 2025S, 2026S), dates and rooms, mandatory
  sessions, tutorial, registration, retake date, curricula, lecturer.

### S2: TISS API record 2026S
- Files: `../docs/tiss-api.md`, `../docs/tiss-api.xml`.
- Used for: subject list (the five headings), learning outcomes, ECTS split,
  examination modalities in English **and German** (the retake wording
  differs), literature, preceding courses.

### S3: 2028S schedule notes
- File: `_schedule/dates.json` of the source repo (not published), entry 192.115.
- Used for: "2028S NOT published (source: 2026S)", the planning summary.

### S24: Lecturer's homepage (G. Fuchsbauer)
- URL: <https://www.di.ens.fr/~fuchsbau/>. Read.
- Used for: teaching list "Advanced Cryptography (6 ECTS), TU Wien, summer
  '21, '23, '25 and '26" (confirms the non-annual pattern); research list
  (algebraic group model [S42], tight Schnorr [S43]). No course material hosted.

### S44: VoWi page "Advanced Cryptography VU (Fuchsbauer)"
- URL: <https://vowi.fsinf.at/wiki/TU_Wien:Advanced_Cryptography_VU_(Fuchsbauer)>.
- Status: **not read.** HTTP 200 but served an Anubis proof-of-work bot check;
  not bypassed. Open it in a browser: past papers or sheets, if any, would be here.

## Literature named on TISS [S2]

### S4: Boneh, Shoup, *A Graduate Course in Applied Cryptography*, v0.6 (Jan. 2023)
- URL: <https://crypto.stanford.edu/~dabo/cryptobook/BonehShoup_0_6.pdf>
  (free PDF, 9.1 MB). Read (full text extracted).
- Used for: difference lemma (Thm 4.7), ROM (8.10), ETDF (11.2), DH-based OT
  (11.6.1), FDH (13.3-13.4), elliptic curves and pairings (ch. 15), generic DL
  bound (Thm 16.3), Shor overview (16.5), Schnorr and Sigma protocols
  (ch. 19, Lemma 19.2, Thm 19.1, eq. (19.5)-(19.6)), Fiat-Shamir proofs
  (20.3), Shamir sharing (22.1), Beaver and garbled circuits (23.2-23.3),
  exercise titles.
- **Gaps in v0.6:** ch. 17 (lattices) and sec. 20.5-20.7 (Bulletproofs,
  SNARKs) consist of headings and "To be written." Notes 04, 07, 08 therefore
  rest on [S6, S15-S19].

### S5: Katz, Lindell, *Introduction to Modern Cryptography*, 3rd ed., CRC 2020
- Cite only (commercial). Section numbers in the notes are **not** given for
  it because they could not be checked.

### S6: Peikert, "A Decade of Lattice Cryptography" (2016)
- URL: <https://eprint.iacr.org/2015/939> (free). Read.
- Used for: Def. 2.2.1-2.2.5, algorithms paragraph (2.2.2), Def. 4.2.1-4.2.3,
  Thm 4.2.4 (Regev), classical hardness (4.2.4), ring-LWE (4.4, Thm 4.4.3),
  module generalisation (4.4.3), Regev's cryptosystem (5.2.1), GGH (3.3).

### S7: Lindell, "Secure Multiparty Computation" (2020)
- URL: <https://eprint.iacr.org/2020/300> (free). Read.
- Used for: properties and ideal/real paradigm (2.1), adversary models (2.2),
  feasibility thresholds (3), Shamir (4.1), honest-majority protocol with
  double-sharing degree reduction (4.2), dishonest-majority approaches (4.5).

## Papers and standards

### S8: Bellare, Rogaway, "Random Oracles are Practical" (CCS 1993)
- URL: <https://cseweb.ucsd.edu/~mihir/papers/ro.pdf> (author copy). Read
  (sec. 1-3). The Rogaway-hosted URL used by the intro course now 404s.
- Used for: the ROM paradigm; $E(x)=f(r)\,\|\,G(r)\oplus x$ (sec. 3).

### S9: Fiat, Shamir, "How to Prove Yourself" (CRYPTO '86)
- URL: <https://link.springer.com/content/pdf/10.1007/3-540-47721-7_12.pdf>
  (served free by Springer at retrieval). Header read.

### S10: Schnorr, "Efficient Signature Generation by Smart Cards", J. Cryptology 4 (1991)
- Cite only (Springer returned a paywall page). Content via [S4 ch. 19].

### S11: Goldreich, Micali, Wigderson, "How to Play any Mental Game" (STOC 1987)
- Cite only (ACM). Content via [S7 sec. 3, 4.5].

### S12: Yao, "How to Generate and Exchange Secrets" (FOCS 1986)
- Cite only (IEEE). Content via [S13].

### S13: Lindell, Pinkas, "A Proof of Security of Yao's Protocol for Two-Party Computation"
- URL: <https://eprint.iacr.org/2004/175> (free; J. Cryptology 2009). Read.
- Used for: semi-honest definition (2.1), elusive/verifiable range (3.1),
  TDP-based OT (Protocol 1), Yao's protocol and Thm 7, the fake-circuit simulator.

### S14: Shamir, "How to Share a Secret", CACM 22(11) 1979
- URL: <https://web.mit.edu/6.857/OldStuff/Fall03/ref/Shamir-HowToShareASecret.pdf>
  (course-hosted copy; ACM copyright). Read (the $(k,n)$ definition).

### S15: Regev, "On Lattices, Learning with Errors, Random Linear Codes, and Cryptography"
- URL: <https://cims.nyu.edu/~regev/papers/qcrypto.pdf> (author copy of the
  J. ACM 2009 version of STOC 2005). Read.
- Used for: Thm 1.1, the cryptosystem and its parameters (sec. 5), Lemma 5.4,
  Claim 5.3.

### S16: NIST FIPS 203, *Module-Lattice-Based Key-Encapsulation Mechanism Standard* (Aug. 2024)
- **Vendored:** [`nist/NIST.FIPS.203.pdf`](nist/NIST.FIPS.203.pdf), from
  <https://nvlpubs.nist.gov/nistpubs/FIPS/NIST.FIPS.203.pdf>. Read.
- Used for: $q=3329$ (2.3), MLWE and FO (3.2), failure rates (Table 1),
  Compress/Decompress (4.7)-(4.8), K-PKE (Alg. 13-15), Encaps/Decaps internals
  (Alg. 17-18), input checks (7.2), parameters and sizes (Tables 2-3), categories (8).

### S17: NIST FIPS 204, *Module-Lattice-Based Digital Signature Standard* (Aug. 2024)
- **Vendored:** [`nist/NIST.FIPS.204.pdf`](nist/NIST.FIPS.204.pdf). Read.
- Used for: security target and assumptions (3.1-3.2), Schnorr analogy and
  rejection sampling (3.3), parameters (Table 1), sizes (Table 2), Alg. 7.

### S18: Groth, "On the Size of Pairing-based Non-interactive Arguments" (EUROCRYPT 2016)
- URL: <https://eprint.iacr.org/2016/260> (free). Read.
- Used for: QAP definition (2.3), the scheme and Thm 2 (3.2), sizes.

### S19: Bünz, Bootle, Boneh, Poelstra, Wuille, Maxwell, "Bulletproofs" (IEEE S&P 2018)
- URL: <https://eprint.iacr.org/2017/1066> (free). Read.
- Used for: inner-product argument (sec. 3, Protocols 1-2), sizes (abstract).

### S20: Hankerson, Menezes, Vanstone, *Guide to Elliptic Curve Cryptography*, Springer 2004
- Cite only (commercial).

### S21: SECG, *SEC 2: Recommended Elliptic Curve Domain Parameters*, v2.0 (2010)
- URL: <https://www.secg.org/sec2-v2.pdf> (free). Read (sec. 2.4.1).
- Used for: secp256k1 $p$, $a$, $b$, $G$, $n$, $h$.

### S22: RFC 7748, *Elliptic Curves for Security* (2016)
- **Vendored:** [`rfc/rfc7748.txt`](rfc/rfc7748.txt). Read.
- Used for: Curve25519 parameters (4.1), X25519 (5), test vectors (5.2), ECDH (6.1).

### S23: RFC 8032, *Edwards-Curve Digital Signature Algorithm (EdDSA)* (2017)
- **Vendored:** [`rfc/rfc8032.txt`](rfc/rfc8032.txt). Read. Byte-identical
  (same SHA-256) to the copy vendored by 192.125.
- Used for: Ed25519 (5.1) and test vectors (7.1).

### S25: IETF Trust Legal Provisions (TLP) 5.0
- URL: <https://trustee.ietf.org/documents/trust-legal-provisions/tlp-5/>
  (probed; the text was read for the intro course). Licence basis for `rfc/`.

### S26: Pointcheval, Stern, "Security Arguments for Digital Signatures and Blind Signatures", J. Cryptology 13 (2000)
- URL: <https://www.di.ens.fr/david.pointcheval/Documents/Papers/2000_joc.pdf>
  (author copy). Abstract read. The original forking lemma.

### S27: Bellare, Neven, "Multi-Signatures in the Plain Public-Key Model and a General Forking Lemma" (CCS 2006)
- URL: <https://cseweb.ucsd.edu/~mihir/papers/multisignatures.pdf> (author copy). Read (sec. 3, Lemma 1).

### S28: Canetti, Goldreich, Halevi, "The Random Oracle Methodology, Revisited"
- URL: <https://eprint.iacr.org/1998/011> (free). Abstract read: schemes secure in the ROM
  whose every implementation of the oracle is insecure.

### S29: Cramer, Damgård, Schoenmakers, "Proofs of Partial Knowledge" (CRYPTO '94)
- Cite only. Content via [S4 sec. 19.7.2].

### S30: Pedersen, "Non-Interactive and Information-Theoretic Secure Verifiable Secret Sharing" (CRYPTO '91)
- Cite only.

### S31: Ben-Or, Goldwasser, Wigderson, "Completeness Theorems for Non-Cryptographic Fault-Tolerant Distributed Computation" (STOC 1988)
- Cite only (ACM). Content via [S7 sec. 3-4.2].

### S32: Gennaro, Gentry, Parno, Raykova, "Quadratic Span Programs and Succinct NIZKs without PCPs" (EUROCRYPT 2013)
- URL: <https://eprint.iacr.org/2012/215> (free). Title checked; QAPs as used via [S18 sec. 2.3].

### S33: Bernhard, Pereira, Warinschi, "How not to Prove Yourself: Pitfalls of the Fiat-Shamir Heuristic and Applications to Helios" (ASIACRYPT 2012)
- URL: <https://eprint.iacr.org/2016/771> (free). Abstract read: weak vs strong Fiat-Shamir,
  adaptive statements make the weak variant unsound.

### S34: Shor, "Polynomial-Time Algorithms for Prime Factorization and Discrete Logarithms on a Quantum Computer"
- URL: <https://arxiv.org/abs/quant-ph/9508027> (free). Title checked.

### S35: Proos, Zalka, "Shor's discrete logarithm quantum algorithm for elliptic curves"
- URL: <https://arxiv.org/abs/quant-ph/0301141> (free). Abstract read.

### S36: NIST SP 800-57 Part 1 Rev. 5 (2020)
- Vendored by the prerequisite course:
  [`../../../ws2026/introduction-to-cryptography/refs/nist/NIST.SP.800-57pt1r5.pdf`](../../introduction-to-cryptography/refs/nist/NIST.SP.800-57pt1r5.pdf).
  Read (Table 2 and its quantum footnote). Not duplicated here.

### S37: Galbraith, *Mathematics of Public Key Cryptography*, v2.0 draft (CUP 2012)
- URL: <https://www.math.auckland.ac.nz/~sgal018/crypto-book/main.pdf>
  (free author draft). Read (TOC; Thm 9.10.7 Hasse; ch. 16-18 headings,
  Alg. 23 Lagrange-Gauss).

### S38: NIST copyright statement
- URL: <https://www.nist.gov/oism/copyrights> (probed). Licence basis for `nist/`.

### S39: Bos et al., "CRYSTALS-Kyber: a CCA-secure module-lattice-based KEM"
- URL: <https://eprint.iacr.org/2017/634> (free). Title checked.

### S40: Ducas et al., "CRYSTALS-Dilithium: Digital Signatures from Module Lattices"
- URL: <https://eprint.iacr.org/2017/633> (free). Title checked.

### S41: Hofheinz, Hövelmanns, Kiltz, "A Modular Analysis of the Fujisaki-Okamoto Transformation" (TCC 2017)
- URL: <https://eprint.iacr.org/2017/604> (free). Abstract read (FO: IND-CPA to IND-CCA in
  the ROM and the quantum ROM, robust to correctness errors); also FIPS 203 ref. [12].

### S42: Fuchsbauer, Kiltz, Loss, "The Algebraic Group Model and its Applications" (CRYPTO 2018)
- URL: <https://eprint.iacr.org/2017/620> (free). Title checked. Lecturer co-author.

### S43: Cho, Fuchsbauer, O'Neill, Sefranek, "Schnorr Signatures are Tightly Secure in the ROM under a Non-interactive Assumption" (CRYPTO 2025)
- URL: <https://eprint.iacr.org/2024/1528> (free). Title checked. Lecturer co-author.

### S45: Goldwasser, Micali, Rackoff, "The Knowledge Complexity of Interactive Proof Systems", SIAM J. Comput. 18 (1989)
- Cite only.
