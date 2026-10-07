# Notes — 192.125 Introduction to Cryptography

Study notes for the 2026W VU (Fuchsbauer & Andreeva), following
Katz & Lindell, *Introduction to Modern Cryptography*, 3rd ed. [S10]. Written for a
reader with a physics master's: mathematically fluent, new to security
definitions and reduction proofs. Every scheme is stated as a **game**, every
claim as a **theorem with a reduction** (full or sketched).

**The notes follow the lecturer's own lecture order**, reconstructed from his
2024W and 2025W slide decks [S7, S8]; the mapping from lecture to note to
Katz-Lindell section is in
[`../refs/lecture-notes-map.md`](../refs/lecture-notes-map.md). Every factual
claim carries an `[S<n>]` citation into
[`../refs/SOURCES.md`](../refs/SOURCES.md). Toy implementations live in
[`../src/py`](../src/README.md); each note points to the relevant file.

**Start with [00-exam-focus.md](00-exam-focus.md)**: the plan for the
midterm (Wed 18.11.2026) and the final (Fri 29.01.2027), the exercise-points
hurdle, four past papers and what they actually asked. Grade per the TISS
record of 2026-09-28: 20 % exercises, 40 % midterm, 40 % final.

The sequel,
[192.115 Advanced Cryptography](../../advanced-cryptography/index.md)
(not offered every year), builds on the provable-security notes
[04](04-computational-security.md), [05](05-pseudorandomness.md) and
[13](13-proof-toolkit.md) with the random-oracle arguments marked background in
[10](10-key-exchange-pke.md) and [11](11-digital-signatures.md); on the number
theory of [09](09-number-theory.md); on the key exchange of
[10](10-key-exchange-pke.md); and on the signatures of
[11](11-digital-signatures.md), whose Schnorr protocol is the first
zero-knowledge proof you meet. The lecturer's closing slide lists what it adds:
ROM proofs, pairings, zero-knowledge proof systems, post-quantum and
homomorphic encryption, multi-party protocols [S8].

**Code.** Each topic note ends in a `## Code` section naming the module, the
functions and the tests; `../src/py/test_note_pointers.py` fails if any of
those names stops resolving.

The through-line of the course, and of the homework, is: *define security as a
game, then prove a scheme secure by reducing an adversary against it to an
adversary against an assumed-hard problem.* Note 04 sets up the pattern and
note 13 is a playbook for reproducing it under exam conditions.

| # | Lecture | Topic | Core idea |
|---|---|---|---|
| [00](00-exam-focus.md) | none | **Exam focus** | 2026W midterm and final plan, exercise hurdle, four past papers, the ±1 true/false section, the four kinds of long question |
| [01](01-historical-ciphers.md) | 1 | Historical ciphers | Scytale, shift, substitution, Vigenère, Vernam; frequency analysis; Kerckhoffs; sufficient key space |
| [02](02-perfect-secrecy.md) | 2 | Perfect secrecy | Shannon's theorem in full, one-time pad, two-time-pad break, \|K\| ≥ \|M\|, perfect indistinguishability |
| [03](03-block-ciphers.md) | 3 | Block ciphers | confusion/diffusion, SPN, DES, Feistel, **meet-in-the-middle on 2DES**, 3DES, AES and its S-box |
| [04](04-computational-security.md) | 4 | Computational security | PPT, negligible functions, asymptotic vs concrete, the reduction template, hybrids |
| [05](05-pseudorandomness.md) | 5 | Pseudorandomness | PRG/PRF/PRP definitions, the pseudo-one-time pad, PRF-to-PRG, switching lemma |
| [06](06-private-key-encryption.md) | 6, 7 | Private-key encryption | EAV/CPA/CCA games, Construction 3.28, modes and their NIST vectors, padding oracle, nonce misuse |
| [07](07-macs-and-ae.md) | 8 | MACs & authenticated encryption | unforgeability, PRF-MAC, CBC-MAC pitfall, HMAC, EtM vs MtE vs E&M, GCM, secure sessions |
| [08](08-hash-functions.md) | 9 | Hash functions | collision/preimage resistance, birthday bound, Merkle-Damgard, Davies-Meyer, length extension, sponge, Merkle trees |
| [09](09-number-theory.md) | 10, 11 | Number theory | groups, Z_N*, Euler, CRT, generators, **DDH ⇒ CDH ⇒ DLog**, RSA, Miller-Rabin, the NIST key-length table |
| [10](10-key-exchange-pke.md) | 11, 12 | Key exchange & PKE | Diffie-Hellman, textbook RSA and five attacks, **RSA-OAEP per RFC 8017**, ElGamal IND-CPA proof, hybrid encryption, DHIES |
| [11](11-digital-signatures.md) | 12, 13 | Digital signatures | EUF-CMA, hash-and-sign, RSA-FDH, Schnorr + Fiat-Shamir, (EC)DSA, nonce reuse |
| [12](12-tls-and-pki.md) | 13, 13a | PKI and TLS | certificates, CAs, revocation, Certificate Transparency, the TLS 1.3 handshake and record layer |
| [13](13-proof-toolkit.md) | — | Proof toolkit & playbook | how to write a reduction, common mistakes, game checklist, building distinguishers, 5 worked problems |

## How to read a security definition

Every definition in these notes has the same skeleton, worth internalising once —
and the exams test it by printing the skeleton with a clause missing [S12, S13,
S16]:

1. **Experiment / game** $\mathsf{Exp}$: an interaction between a *challenger*
   (who knows the secret key) and an *adversary* $\mathcal{A}$ (who does not).
2. **Adversary class**: information-theoretic (unbounded) in notes 01-02,
   probabilistic polynomial-time (PPT) from note 04 on.
3. **Win condition**: a bit the game outputs. Security = *no admissible
   adversary makes the game output 1 with more than the trivial probability*,
   where "trivial" is $1/2$ for indistinguishability games and $\approx 0$ for
   unforgeability/one-wayness games.
4. **Advantage**: $\mathsf{Adv} = |\Pr[\text{win}] - \text{trivial}|$, required
   to be $0$ (perfect), or negligible (computational).

## Scope markers

Passages marked **(background)** are in the notes for completeness but are on the
lecturer's own list of material the course does not cover [S8]: security proofs
for public-key schemes in the random-oracle model (RSA-FDH, OAEP, Fiat-Shamir),
cryptography from minimal assumptions (GGM), the factoring and discrete-log
algorithms themselves, further public-key schemes (Cramer-Shoup), and
post-quantum cryptography. See
[`../refs/lecture-notes-map.md`](../refs/lecture-notes-map.md) for the full list.

## Conventions

- $n$ or $\lambda \in \mathbb{N}$: security parameter (key length in unary,
  $1^n$). The lecture uses $n$; these notes use both.
- $x \gets S$: sample uniformly from set $S$; $x \gets \mathcal{A}$: run the algorithm.
- PPT: probabilistic polynomial-time.
- $\mathsf{negl}(n)$: a negligible function (smaller than every inverse polynomial).
- $\|$ concatenation, $\oplus$ XOR, $|x|$ bit length of $x$.
- $[a \bmod N]$: the representative of $a$ in $\{0,\dots,N-1\}$, as the lecture
  writes it.
