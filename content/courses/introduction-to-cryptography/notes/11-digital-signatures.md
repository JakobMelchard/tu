# 11 — Digital signatures

*Lectures 12 and 13 [S8]. Katz-Lindell sec. 13, 13.4, 13.5 [S10] — Def. 13.2,
Thm 13.11. (EC)DSA and EdDSA are FIPS 186-5 [S30]; deterministic nonces are
RFC 6979 [S32] and RFC 8032 [S33]. PKI moved to note 12. Code:
[`../src/py/signatures.py`](../src/py/signatures.py).*

Signatures are the public-key analogue of MACs: the *private* key signs, the
*public* key verifies. Unlike a MAC they give **public verifiability** and
**non-repudiation** — anyone can check, and the signer cannot deny. This note
gives the EUF-CMA game, the hash-and-sign paradigm, RSA-FDH (with its ROM proof
idea), Schnorr via Fiat-Shamir, the (EC)DSA family, and how PKI turns keys into
trust.

## The EUF-CMA game

A signature scheme: $\mathsf{Gen}\to(pk,sk)$, $\sigma\gets\mathsf{Sign}_{sk}(m)$,
$\mathsf{Vrfy}_{pk}(m,\sigma)\in\{0,1\}$.

$$
\begin{array}{l}
\mathsf{Sig\text{-}forge}_{\mathcal A,\Pi}(\lambda):\ (pk,sk)\gets\mathsf{Gen}(1^\lambda)\\
\quad \mathcal A^{\mathsf{Sign}_{sk}(\cdot)}(pk)\to(m^*,\sigma^*),\ Q=\text{queried messages}\\
\quad \text{output }1\text{ iff }\mathsf{Vrfy}_{pk}(m^*,\sigma^*)=1 \wedge m^*\notin Q
\end{array}
$$

**Definition (EUF-CMA).** Existentially unforgeable under chosen-message attack
if every PPT $\mathcal A$ wins with negligible probability. Same shape as the MAC
game (note 07) but the adversary gets $pk$ and verification is public. "Strong"
EUF-CMA additionally forbids a new signature on a queried message.

## Textbook RSA signatures are forgeable

$\mathsf{Sign}(m)=m^d\bmod N$, $\mathsf{Vrfy}(m,\sigma)=[\sigma^e\stackrel?=m]$. Two forgeries,
both in `signatures.py` and tested:

- **No-query (existential) forgery:** pick any $\sigma$, set $m=\sigma^e\bmod N$;
  then $\sigma^e=m$ verifies although $m$ was never signed
  (`signatures.textbook_forgery`). The forged $m$ is "random junk," but the game
  counts *any* new message.
- **Homomorphic forgery:** from $\sigma_1=m_1^d$, $\sigma_2=m_2^d$ compute a valid
  signature $\sigma_1\sigma_2=(m_1 m_2)^d$ on $m_1 m_2$
  (`signatures.rsa_homomorphic_forgery`). A *targeted* attack using two queries.

Both exploit the multiplicative structure. The fix is to sign a **hash**.

## Hash-and-sign

Sign $H(m)$ instead of $m$: $\mathsf{Sign}(m)=(H(m))^d$. **Theorem:** if $H$ is
collision resistant and the "sign the hash" scheme on fixed-length digests is
EUF-CMA, then hash-and-sign is EUF-CMA on arbitrary messages. *Reduction:* a
forgery $(m^*,\sigma^*)$ with $m^*\notin Q$ is either (a) a forgery on the digest
$H(m^*)$ (if $H(m^*)\notin H(Q)$), or (b) yields a collision $H(m^*)=H(m)$ for
some queried $m\ne m^*$ (if the digest was seen). Collision resistance rules out
(b), the underlying scheme rules out (a). This is why hashing kills the RSA
forgeries: the algebraic tricks produce a *digest* the attacker cannot invert to
a real message.

## RSA-FDH and the random oracle model

**Full-Domain Hash:** hash the message into the *whole* domain $\mathbb{Z}_N^*$,
then sign: $\mathsf{Sign}(m) = H(m)^d\bmod N$, $\mathsf{Vrfy}(m,\sigma)=[\sigma^e = H(m)]$.
Code: `signatures.fdh_sign`/`fdh_verify` (FDH emulated by hashing counter blocks
mod $N$); verifies genuine signatures and rejects tampered messages
(`test_signatures.py::test_fdh_sign_verify`).

**Theorem (idea) — background.** RSA-FDH is EUF-CMA in the ROM under the RSA
assumption. Lecture 13 states the *scheme* and says its security is proved in the
random-oracle model; lecture 13a puts "security proofs for public-key schemes
(often in the random-oracle model)" on the **not covered** list [S8]. So learn
the construction and the shape of the argument; do not expect to write the proof
under exam conditions.
*Proof idea.* The reduction is given an RSA challenge $(N,e,y)$ and must output
$y^d$. It answers the adversary's hash queries by **programming** $H$: for each
queried $m_i$ it picks random $r_i$ and sets $H(m_i)=r_i^e$, so it can sign
$m_i$ as $\sigma_i=r_i$ (since $\sigma_i^e=r_i^e=H(m_i)$) *without knowing $d$*.
For one guessed target query it instead sets $H(m^*)=y\cdot r^e$. If the adversary
forges $\sigma^*$ on $m^*$, then $\sigma^{*e}=y\cdot r^e$, so $y^d=\sigma^*/r$ —
the reduction solves RSA. The two ROM superpowers (see hash queries, program
answers) are both essential. $\square$ Contrast with the textbook forgeries: FDH's
$H$ makes $\sigma\mapsto\sigma^e$ land on a *random* point the attacker cannot
match to a chosen message.

## Schnorr: identification and signature

**Schnorr identification** is a **$\Sigma$-protocol** (commit-challenge-response)
proving knowledge of a discrete log $x$ where $y=g^x$, in a prime-order group:
1. **Commit:** prover picks $r$, sends $t=g^r$.
2. **Challenge:** verifier sends random $c$.
3. **Response:** prover sends $s=r+cx\bmod q$.
4. **Check:** $g^s \stackrel?= t\cdot y^c$ (indeed $g^{r+cx}=g^r(g^x)^c$).

Code: `signatures.schnorr_identify`. Two properties make it a proof of knowledge:
- **Special soundness:** two accepting transcripts $(t,c,s),(t,c',s')$ with the
  *same* $t$ but $c\ne c'$ yield $x=(s-s')/(c-c')$ — so anyone who can answer two
  challenges knows $x$.
- **Honest-verifier zero-knowledge:** a transcript can be *simulated* without $x$
  (pick $c,s$ first, set $t=g^s y^{-c}$), so it leaks nothing about $x$.

### Fiat-Shamir: identification $\to$ signature

Replace the verifier's random challenge by a hash of the commitment and message:
$c=H(t\|m)$. This makes the protocol **non-interactive**, and binding the message
into $c$ turns it into a signature. Schnorr signature: $\sigma=(c,s)$ with
$t=g^r$, $c=H(t\|m)$, $s=r+cx\bmod q$; verify by recomputing $t'=g^s y^{-c}$ and
checking $c=H(t'\|m)$. Code: `signatures.schnorr_sign`/`schnorr_verify`
(`test_signatures.py::test_schnorr_signature`, incl. wrong-key rejection).
**Security.** Lecture 13 states **Theorem 13.11**: if the discrete-logarithm
assumption holds, the Schnorr *identification* protocol is secure [S8, S10]. The
signature version is EUF-CMA in the ROM under DLP via the *forking lemma* [S46] —
rewind the adversary to obtain two forgeries sharing $t$ with different
challenges, then special soundness extracts $x$ — but that is **background**,
the same "public-key proofs in the ROM" the lecturer lists as not covered [S8].

The slides add a historical note worth having: Schnorr signatures were **covered
by a patent** until 2008, which is why DSA — a clumsier design over the same
group — became the standard instead [S8].

**Critical pitfall — nonce reuse.** If two Schnorr (or (EC)DSA) signatures reuse
$r$, then from $s=r+cx$, $s'=r+c'x$ one solves $x=(s-s')/(c-c')$. This really
happened *(unsourced: the Sony PS3 ECDSA key recovery of 2010 and several
Bitcoin key compromises are widely reported but no primary source was fetched;
they are kept because they make the point that this is an implementation failure
people actually ship, not a theoretical one)*. $r$ must be fresh and unpredictable (or derived
deterministically from the message, RFC 6979). Code:
`signatures.schnorr_nonce_reuse_attack` and, for DSA,
`dsa.nonce_reuse_attack`; `dsa.rfc6979_k` is the deterministic fix, and it
reproduces all twenty DSA nonces RFC 6979 prints [S32].

## DSA / ECDSA overview

**DSA** also signs via a per-message nonce $k$ in a prime-order subgroup of
$\mathbb{Z}_p^*$: $r=(g^k\bmod p)\bmod q$, $s=k^{-1}(H(m)+xr)\bmod q$;
verification recomputes $r$ from $(pk,H(m),r,s)$. **ECDSA** is the same over an
elliptic-curve group (note 09), giving much smaller signatures at equal security
— it secures TLS certificates, SSH and Bitcoin.

The structural difference from Schnorr is where the nonce enters: Schnorr has
$s = r x + k$ (F24's notation below: $k$ the nonce, $r$ the hash; above it was
$s = r + cx$), **linear** in the secrets, which is what makes the extractor and
the multi-signature constructions work. (EC)DSA has $s = k^{-1}(H(m)+xr)$, with
an inversion, and no comparably clean proof. Both are equally fatal under nonce
reuse.

Current NIST status, from FIPS 186-5 [S30]: **DSA is withdrawn** for signature
*generation* (existing signatures may still be verified); ECDSA and **EdDSA**
(Ed25519/Ed448, which is Schnorr over a twisted Edwards curve [S33]) are the
approved schemes; and sec. 6.4.2 explicitly permits **deterministic per-message
secrets**, which is the standards-body answer to the nonce problem above.

## Certificates and PKI

Signatures verify authenticity *relative to a public key* — they say nothing
about whose key it is. Closing that gap is certificates, certificate
authorities, revocation and Certificate Transparency, and it is the subject of
**[note 12](12-tls-and-pki.md)** together with TLS (lectures 13 and 13a,
Katz-Lindell sec. 13.6-13.7 [S8, S10]).

## Worked example

*Recover a Schnorr signer's secret key from two signatures that reused the nonce
$r$.* Given $(c_1,s_1)$ on $m_1$ and $(c_2,s_2)$ on $m_2$ with the same
commitment $t=g^r$ (hence the attacker notices identical $t$, or identical $r$):
$s_1=r+c_1 x$, $s_2=r+c_2 x \pmod q$. Subtract: $s_1-s_2=(c_1-c_2)x$, so
$x=(s_1-s_2)(c_1-c_2)^{-1}\bmod q$. With $x$ the attacker signs anything. This is
the same linear-algebra leak as special soundness — benign for the proof,
catastrophic for a real signer. $\square$

## Pitfalls

- **Never sign raw messages with textbook RSA** — hash-and-sign or FDH.
- **Fresh, unpredictable nonces** for Schnorr/(EC)DSA; reuse or bias leaks the
  key. Prefer deterministic derivation (RFC 6979 / Ed25519).
- **Bind the message into the Fiat-Shamir hash** ($c=H(t\|m)$); hashing only $t$
  lets an attacker reuse a transcript for a different message.
- **Collision resistance is required** for hash-and-sign; a hash collision is a
  signature forgery *(unsourced: the 2008 rogue-CA-certificate construction from
  an MD5 collision; the underlying claim — a collision in the signature hash is a
  forgery — is the hash-and-sign reduction above and is sourced)*.
- **A valid signature is not freshness.** Replays need nonces/timestamps at the
  protocol layer.
- **A signature proves key ownership, not identity** — that is PKI's job.

## Exam-style questions

**Q1** *(F24 5a [S16]).* For Schnorr signatures over a standardised
$(\mathbb G,q,g)$ with $H:\{0,1\}^*\to\mathbb Z_q$, where
$\mathsf{Gen}$ returns $pk := g^x$, $sk := x$, and
$\mathsf{Sign}_{sk}(m)$ samples $k\gets\mathbb Z_q$, sets $I := g^k$,
$r := H(I,m)$, $s := [rx+k \bmod q]$ and returns $\sigma := (r,s)$ — define
$\mathsf{Vrfy}$ and prove correctness. —
$\mathsf{Vrfy}_{pk}(m,(r,s))$: compute $I' := g^s\cdot pk^{-r}$ and return 1 iff
$H(I',m)=r$. Correctness: for an honest signature,
$g^s\,pk^{-r} = g^{rx+k}\,g^{-xr} = g^{k} = I$, so $I'=I$ and
$H(I',m)=H(I,m)=r$. Note the verifier never sees $I$ — it *reconstructs* it,
which is why the signature is two $\mathbb Z_q$ elements rather than a group
element plus a scalar.

**Q2** *(F24 5b and F20 6b, the same question two ways [S16, S15]).* Two Schnorr
signatures $\sigma_1,\sigma_2$ on distinct messages $m_1\neq m_2$ were produced
under the same secret key **and the same $k$**. Recover $sk$. —
$s_1 = r_1x+k$ and $s_2 = r_2x+k$ over $\mathbb Z_q$. Subtract:
$s_1-s_2 = (r_1-r_2)x$. Since $m_1\neq m_2$ and $I$ is the same,
$r_1 = H(I,m_1) \neq H(I,m_2) = r_2$ except with negligible probability, so
$r_1-r_2$ is invertible mod $q$ (prime) and
$$x = (s_1-s_2)(r_1-r_2)^{-1} \bmod q.$$
The 2021 paper dresses this up as a *deterministic* variant that stores one fixed
$k$ in the secret key and asks whether the scheme is secure [S15]: it is not, and
this is why — the second signature ever issued leaks the key. The real
deterministic constructions derive $k$ from $(sk,m)$ by a PRF, so distinct
messages give distinct nonces [S32, S33].

**Q3** *(F20 6c [S15]).* Give at least two advantages of digital signatures over
message authentication codes. — (i) **Public verifiability**: anyone with $pk$
can check, where a MAC can only be checked by someone holding the secret key —
so a signature works for broadcast (software updates, certificates) while a MAC
does not. (ii) **Non-repudiation**: only the holder of $sk$ could have produced
it, so the signer cannot plausibly deny it; with a MAC, the verifier could have
produced the tag itself, so it proves nothing to a third party. (iii)
**Key management**: $n$ parties need $n$ public keys, not $\binom n2$ shared
secrets. The cost is speed — signatures are orders of magnitude slower.

**Q4** *(ours; the textbook-RSA forgery is on no public paper, but lecture 13
opens with "Plain RSA signatures" and immediately breaks them [S8]).* Exhibit
the no-query existential forgery against $\mathsf{Sign}(m)=m^d \bmod N$, and
explain precisely why hash-and-sign stops it. — Pick any $\sigma\in\mathbb Z_N^*$
and set $m := \sigma^e \bmod N$. Then $\mathsf{Vrfy}(m,\sigma)$ checks
$\sigma^e = m$, which holds by construction, and $m$ was never signed. The
adversary does not choose $m$, but EUF-CMA counts *any* new message. With
hash-and-sign the check is $\sigma^e = H(m)$, so the same trick produces a
*digest* $\sigma^e$ and the adversary would have to find an $m$ hashing to it —
a preimage. The forgery has not been made harder to *compute*; it has been made
useless, because the attacker no longer controls which message it corresponds to.

**Q5** *(ours, modelled on the hash-and-sign slide and F23 q3's collision theme
[S8, S12]).* MD5 was still used in CA certificates in 2008. Explain how a
collision in the signature hash becomes a forged certificate. — Hash-and-sign
signs $H(m)$, so any $m'$ with $H(m')=H(m)$ inherits the signature verbatim. The
2008 attack predicted the content of a benign website certificate $m$ the CA
would issue (serial number and validity included) and built a rogue
certificate $m'$ carrying CA-signing authority, with $H(m)=H(m')$ under MD5 (a
chosen-prefix collision); the CA signed $m$, and the signature transferred to
$m'$. The reduction in the
hash-and-sign theorem is exactly this argument run in reverse: a forgery is
either a forgery on the digest or a collision, and collision resistance is the
hypothesis that rules the second branch out.

## Code

`src/py/signatures.py`: `rsa_sign_textbook`, `textbook_forgery`,
`rsa_homomorphic_forgery`, `fdh_sign`, `fdh_verify`, `emsa_pkcs1_v15_encode`,
`rsassa_pkcs1_v15_sign`, `rsassa_pkcs1_v15_verify`, `schnorr_keygen`,
`schnorr_transcript`, `schnorr_check`, `schnorr_identify`, `schnorr_extract`,
`schnorr_sign`, `schnorr_verify`, `schnorr_nonce_reuse_attack`.
`src/py/dsa.py`: `bits2int`, `rfc6979_k`, `sign`, `verify`,
`nonce_reuse_attack`. Tests:
`test_signatures.py::test_pkcs1_v15_signatures_interoperate_with_the_library`,
`test_signatures.py::test_schnorr_nonce_reuse_recovers_the_key` (Q2),
`test_signatures.py::test_special_soundness_extracts_the_witness`,
`test_dsa.py::test_rfc6979_appendix_a2` (all twenty RFC 6979 DSA vectors [S32]).
