# Notes: 192.115 Advanced Cryptography

Preparation notes for the VU (Fuchsbauer, E192), **offered in summer semesters**. The
course is **not offered every year**: TISS lists 2021S, 2023S, 2025S and
2026S [S1], and the lecturer's own page lists the same four summers [S24].
Nothing about 2028S is published yet; the facts below are the 2026S pattern
[S1, S2, S3]. Confirm in January 2028 that it runs at all.

Written for a reader with a physics master's who has finished the
prerequisite **192.125 Introduction to Cryptography** (winter semester, notes in
[`../../../ws2026/introduction-to-cryptography/notes/`](../../introduction-to-cryptography/notes/README.md)).
These notes assume that course: security games, PPT and negligible functions,
the reduction template and hybrids (its notes 04 and 13), DH and ElGamal (10),
EUF-CMA, RSA-FDH and basic Schnorr (11). They are linked, not repeated.

Every factual claim carries `[S<n>]`, resolved in
[`../refs/SOURCES.md`](../refs/SOURCES.md). The TISS subject list gives only
five topic headings [S2]; the order of the notes follows it, and the mapping
from heading to note to textbook chapter is in
[`../refs/lecture-notes-map.md`](../refs/lecture-notes-map.md). Toy
implementations are in [`../src/py`](../src/README.md).

**Start with [00-exam-focus.md](00-exam-focus.md).**

| # | TISS heading [S2] | Note | Core idea |
|---|---|---|---|
| [00](00-exam-focus.md) | (admin) | **Exam focus** | 40 % ticked exercises + 60 % two partial exams; what to verify in January 2028 |
| [01](01-provable-security-rom.md) | Provable security, the random-oracle model | Provable security and the ROM | concrete bounds, tightness, difference lemma, observability and programmability, BR93 reduction written out |
| [02](02-elliptic-curves.md) | Elliptic-curve-based cryptography | Elliptic curves | group law, Hasse, ECDH/ECDSA/Schnorr/EdDSA, Montgomery ladder, X25519, pairings, parameter choice |
| [03](03-zero-knowledge.md) | Zero-knowledge and succinct proof systems | Sigma protocols and commitments | completeness, special soundness, HVZK, Fiat-Shamir, Pedersen, OR-proofs |
| [04](04-succinct-proofs.md) | (same heading) | Succinct arguments | arithmetic circuits, R1CS, QAP, Groth16 shape, Bulletproofs inner-product argument |
| [05](05-mpc-secret-sharing.md) | Secure multi-party computation | MPC I: definitions, honest majority | ideal/real paradigm, semi-honest vs malicious, Shamir, BGW gates, degree reduction |
| [06](06-mpc-ot-gmw-yao.md) | (same heading) | MPC II: dishonest majority | oblivious transfer, GMW, Yao's garbled circuits, feasibility thresholds |
| [07](07-lattices-lwe.md) | Lattice-based cryptography | Lattices and LWE | SVP/CVP, reduction, LWE, Regev encryption, worst-case hardness |
| [08](08-module-lattices-pqc.md) | (same heading) | Ring/module-LWE, ML-KEM, ML-DSA | structured lattices, Kyber and Dilithium structure, Shor vs LWE |

## Scope markers

- **(background)**: stated for orientation, not something the 2026S page
  promises the course proves. TISS gives headings only [S2]; which proofs are
  done in lecture is unknown until the 2028S slides exist.
- **(unverified)**: a claim about the course itself that no readable source
  confirms. The one public page that might (VoWi [S44]) sits behind a bot
  check and was not read.

## Conventions

- $\lambda$ security parameter; $x \gets S$ uniform sampling; $\mathcal A$
  adversary, $\mathcal B$ reduction; $\mathsf{negl}$ negligible.
- **Advantage.** For indistinguishability we write
  $\mathsf{Adv} = |\Pr[b'=b] - \tfrac12|$ (Katz-Lindell style [S5]).
  Boneh-Shoup [S4] use $|\Pr[W_0]-\Pr[W_1]|$ over two experiments, which is
  **twice** ours. Their bounds carry a factor 2 that ours do not; check which
  one an exercise sheet uses.
- $\mathbb G$ a cyclic group of prime order $q$ with generator $g$,
  written multiplicatively; elliptic-curve groups additively ($P$, $kP$).
- $[a]_1,[a]_2$ are the encodings $aG_1$, $aG_2$ in pairing groups, as in [S18].
