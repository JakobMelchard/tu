# 06 — Private-key encryption

*Lectures 6 and 7 [S8]. Katz-Lindell sec. 3.4.2, 3.5.1, 3.5.2, 3.6.3 and 5.1
[S10] — Constr. 3.28. Modes follow NIST SP 800-38A [S25]. Code:
[`../src/py/private_key.py`](../src/py/private_key.py).*

Now we build *usable* encryption: short reusable keys, many messages, active
adversaries. The story is a ladder of stronger games — EAV $\subset$ CPA
$\subset$ CCA — and constructions that climb it, each with a reduction to a PRG
or PRF. The recurring lesson: **encryption alone gives secrecy, never
integrity**, and ignoring that leads to the padding-oracle attack.

## The security ladder

### EAV (eavesdropping, note 04 recap)

One challenge ciphertext, no queries. Achieved by the stream cipher below.
Too weak in practice: real adversaries see many ciphertexts and can influence
plaintexts.

### CPA (chosen-plaintext attack)

The adversary gets an **encryption oracle** $\mathsf{Enc}_k(\cdot)$ before *and* after
the challenge:
$$
\begin{array}{l}
\mathsf{PrivK}^{\mathrm{cpa}}_{\mathcal A,\Pi}(\lambda):\ k\gets\mathsf{Gen}(1^\lambda)\\
\quad \mathcal A^{\mathsf{Enc}_k(\cdot)}(1^\lambda)\to(m_0,m_1),\ |m_0|=|m_1|\\
\quad b\gets\{0,1\},\ c\gets\mathsf{Enc}_k(m_b)\\
\quad \mathcal A^{\mathsf{Enc}_k(\cdot)}(c)\to b';\ \text{output }1\text{ iff }b'=b
\end{array}
$$
CPA-secure iff advantage negligible. **Deterministic schemes cannot be
CPA-secure**: query $\mathsf{Enc}_k(m_0)$, compare to the challenge; if equal, $b=0$.
So *every CPA-secure scheme is randomised or stateful*. This one fact rules out
ECB and textbook RSA in one line.

### CCA (chosen-ciphertext attack)

Additionally a **decryption oracle** $\mathsf{Dec}_k(\cdot)$, forbidden only on the
challenge $c$ itself. Models active tampering. CCA-security requires
*non-malleability*; unauthenticated encryption fails it (the padding oracle is a
CCA break). Achieving CCA needs a MAC — note 07.

## Construction 1: PRG stream cipher (EAV)

$\mathsf{Enc}_k(m) = G(k)\oplus m$ with a PRG $G$. Fixed-length, one-time.

**Theorem.** If $G$ is a secure PRG, this scheme is EAV-secure.
*Proof (the note-04 template).* Distinguisher $\mathcal B(w)$ receives $\mathcal A$'s
$(m_0,m_1)$, picks $b$, sends $c=w\oplus m_b$, outputs $1$ iff $\mathcal A$ guesses
$b$. If $w=G(k)$, $\mathcal A$ is in the real game: $\Pr[\mathcal B\to1]=\tfrac12+\varepsilon$.
If $w$ uniform, $c$ is a one-time pad: $\Pr[\mathcal B\to1]=\tfrac12$. So
$\mathsf{Adv}^G_{\mathcal B}=\varepsilon$, negligible. $\square$

To handle **many messages** or **long streams**, use a *stateful/synchronised*
stream cipher (advance the PRG state); reusing $G(k)$ across messages is the
two-time-pad disaster of note 02. Modern stream ciphers (ChaCha20,
`prg.chacha20_encrypt`, reproducing RFC 8439 sec. 2.4.2 [S36]) are really
PRFs in CTR mode — construction 2.

## Construction 2: PRF scheme (CPA) — K&L Construction 3.28

$\mathsf{Enc}_k(m) = (r,\ F_k(r)\oplus m)$ with $r\gets\{0,1\}^n$ fresh per encryption.
Code: `private_key.prf_encrypt`/`prf_decrypt`. This is the construction lecture 6
names and proves [S8], so it is the one to be able to write from memory.

> **$r$ is part of the ciphertext.** A 2021 exam question proposes
> "$c := F_k(r)\oplus m$ for fresh $r$" and asks whether you would recommend it
> when CCA-security is not needed [S15]. The answer is not about security: with
> $r$ discarded, the receiver cannot recompute $F_k(r)$ and the scheme is not
> *correct*. Check correctness before you check security.

**Theorem.** If $F$ is a PRF, this scheme is CPA-secure, with
$\mathsf{Adv}^{\mathrm{cpa}}_{\mathcal A} \le \mathsf{Adv}^{PRF}_{\mathcal B} + \frac{q}{2^n}$
for an adversary making $q$ encryption queries (the bound K&L prove right
after Constr. 3.28).

*Proof sketch (two moves).*
1. **Replace $F_k$ by a random function $f$.** A distinguisher $\mathcal B$
   simulates the whole CPA game using its oracle in place of $F_k$; the gap is
   exactly $\mathsf{Adv}^{PRF}_{\mathcal B}$.
2. **Analyse the ideal game.** With a truly random $f$, the challenge uses
   $f(r^*)$ at a uniform point $r^*$. Unless $r^*$ equals one of the $q$ values
   $r$ used to answer oracle queries, $f(r^*)$ is uniform and independent of
   everything $\mathcal A$ sees, so the challenge is a one-time pad and
   $\mathcal A$ wins with probability exactly $\tfrac12$. Collisions among the
   query values themselves do not matter. By a union bound
   $\Pr[r^* \in \{r_1,\dots,r_q\}] \le q/2^n$. $\square$

The $q/2^n$ term is why $n$ (the randomness/nonce length) must be large: reuse
of $r$ is a two-time pad on $F_k(r)$.

## Modes of operation

Turn a block cipher (strong PRP, note 05) into encryption for long messages.
Code: `ecb_*`, `cbc_*`, `ctr_*` in `private_key.py`, cross-checked against AES.

All four are specified in NIST SP 800-38A [S25], and
[`../src/py/test_standard_vectors.py`](../src/py/test_standard_vectors.py)
reproduces its AES-128 ECB, CBC and CTR vectors block for block.

| Mode | Encryption | CPA-secure? | Notes |
|---|---|---|---|
| **ECB** | $c_i = E_k(m_i)$ | **No** | deterministic; equal blocks $\to$ equal ciphertext |
| **CBC** | $c_i = E_k(m_i\oplus c_{i-1})$, $c_0=\mathrm{IV}$ | Yes, random IV | needs padding; sequential encryption |
| **CTR** | $c_i = m_i \oplus E_k(\mathrm{nonce}\|i)$ | Yes, fresh nonce | needs only $E$ (a PRF); parallel; no padding |
| **OFB** | keystream $z_i=E_k(z_{i-1})$, $z_0=\mathrm{IV}$ | Yes, random IV | PRF-based stream cipher |

**ECB leaks structure** — the "ECB penguin." `private_key.structured_image` makes
a block-aligned bitmap; under ECB the rectangle is plainly visible in the
ciphertext block map, under CBC it is not (`test_private_key.py::test_ecb_leaks_structure_cbc_does_not`,
and the `__main__` demo prints both maps). This *is* the CPA break: two equal
plaintext blocks give equal ciphertext blocks.

**CTR/OFB security** reduces to the PRF property: the keystream
$E_k(\mathrm{nonce}\|i)$ is pseudorandom, so ciphertext is a pseudo-one-time pad;
the CPA proof is the construction-2 proof with counter inputs. **CBC security**
needs the IV uniform and **unpredictable** — SP 800-38A appendix C says so in the
standard's own words. A predictable IV is the BEAST attack *(unsourced: named
from general knowledge; SP 800-38A states the unpredictability requirement [S25]
but does not name the attack, and the lecture slides do not mention it)*.

> **Two counter conventions.** SP 800-38A sec. 6.5 increments the *whole* block
> (appendix B.1's "standard incrementing function"), so a carry out of the low
> bytes propagates into what an implementation might think of as a fixed nonce
> prefix. The commoner $\mathrm{nonce}\|i$ split agrees with it only while the
> counter does not overflow. `private_key.ctr_keystream_from` implements the NIST
> convention and is what reproduces the F.5.1 vectors.

## Padding and the padding-oracle attack (a CCA break)

CBC needs the plaintext padded to a block multiple. **PKCS#7**: append $p$ bytes
each equal to $p$, with $1\le p\le 16$ for AES, so an already aligned message
gets a whole block of `0x10` (`private_key.pad`/`unpad`). Decryption strips and *validates*
the padding.

If the receiver reveals — even implicitly, via an error message or timing —
whether padding was **valid**, that one bit leaks the entire plaintext. This is
Vaudenay's attack [S48], and the lecture-7 slide uses it to answer its own
question about CCA-security ("Too paranoid? No! Padding-oracle attack") [S8]. Because
$m_i = D_k(c_i)\oplus c_{i-1}$, tampering with block $c_{i-1}$ lets the attacker
control $m_i$'s trailing bytes; forcing valid padding of value $p$ reveals
$D_k(c_i)$ byte by byte, hence $m_i$. Full working attack:
`private_key.make_padding_oracle` + `padding_oracle_attack`, which recovers a
secret plaintext from oracle queries alone (`test_private_key.py::test_padding_oracle_recovers_plaintext`,
and the `__main__` demo). The number of oracle queries is $\approx 128\cdot(\text{#bytes})$
— linear, not exponential.

**The lesson:** CBC is CPA-secure but *not* CCA-secure. Secrecy without
integrity is exploitable. The fix is authenticated encryption (note 07):
MAC the ciphertext and reject before decrypting, so the oracle never speaks.

## Nonce misuse

CTR and GCM (note 07) are catastrophic under **nonce reuse**: the same
(key, nonce) reproduces the same keystream, so two ciphertexts XOR to the
plaintext XOR — a two-time pad. For GCM, nonce reuse *also* leaks the
authentication subkey, destroying integrity, not just secrecy. Nonces must be
unique per key: a counter, or random with a large enough space.

## Worked example

*Prove ECB is not EAV-secure (hence not CPA-secure) with an explicit adversary.*
$\mathcal A$ outputs $m_0 = 0^{2n}$ (two identical zero blocks) and
$m_1 = 0^n\|1^n$ (two different blocks). On the challenge $c=(c_1,c_2)$: output
$0$ if $c_1=c_2$, else $1$. Under ECB, $m_0$ gives $c_1=c_2=E_k(0^n)$ while $m_1$
gives $c_1\ne c_2$ (E injective). So $\mathcal A$ wins with probability $1$;
advantage $1/2$, non-negligible. $\square$

## Pitfalls

- **Deterministic = broken (CPA).** ECB, textbook RSA, and "encrypt with a fixed
  IV" all fall to the one-line repeat-query attack.
- **IV/nonce discipline.** Random *and* unpredictable for CBC; unique for CTR/GCM.
  Predictable IV $\to$ BEAST; reused nonce $\to$ two-time pad.
- **Never expose decryption failures.** Distinct "bad padding" vs "bad MAC"
  errors, or timing differences, create oracles.
- **Encryption is not authentication.** CPA security says nothing about
  tampering; you need a MAC (note 07).
- **Padding is fragile.** Use CTR/GCM (no padding) or authenticate before
  unpadding.

## Exam-style questions

**Q1** *(F23 2a [S12]).* The CCA experiment
$\mathsf{PrivK}^{\mathrm{cca}}_{\mathcal A,\Pi}(n)$ is defined as: $k\gets
\mathsf{Gen}(1^n)$; $\mathcal A$ gets $1^n$ and oracle access to
$\mathsf{Enc}_k(\cdot)$ and $\mathsf{Dec}_k(\cdot)$; $\mathcal A$ outputs
$m_0,m_1$ with $|m_0|=|m_1|$; $b\gets\{0,1\}$, $c^*:=\mathsf{Enc}_k(m_b)$;
$\mathcal A$ continues with both oracles but may not query $\mathsf{Dec}_k$ on
$c^*$; output 1 iff $b'=b$. **Which modifications give CPA-security?** — Delete
the decryption oracle in both phases, and with it the restriction about $c^*$
(which then has nothing to restrict). Everything else is unchanged: the
encryption oracle stays in both phases, the equal-length requirement stays, and
the bound stays $\tfrac12+\mathsf{negl}$.

**Q2** *(M25 2 [S13]).* Reconstruct the same experiment from a version with the
blanks removed: the bound is $\tfrac12+\epsilon(n)$; step 2's access is "the
encryption oracle $\mathsf{Enc}_k(\cdot)$ and the decryption oracle
$\mathsf{Dec}_k(\cdot)$"; step 3's condition is "$|m_0| = |m_1|$"; step 5's
restriction is "$\mathcal A$ may not query $\mathsf{Dec}_k(\cdot)$ on $c^*$";
step 6's win condition is "$b' = b$". — Worth rehearsing by writing it out: the
midterm asks for exactly these five, and each is a clause whose removal breaks
the definition (drop the equal lengths and *no* scheme is secure; drop the $c^*$
restriction and *no* scheme is secure).

**Q3** *(M25 1i and F23 1d/1e [S13, S12]).* Which of ECB, CBC and CTR are
EAV-secure, CPA-secure, CCA-secure? — ECB is **none** of the three: it is
deterministic, so two equal plaintext blocks give two equal ciphertext blocks and
the one-line distinguisher of the worked example above wins the EAV game. CBC (random unpredictable IV)
and CTR (fresh nonce) are EAV- and CPA-secure, and **neither is CCA-secure** —
both are malleable, and CBC's padding check is an outright decryption oracle.

**Q4** *(F24 2a/2b [S16]).* CBC mode encrypts block $i$ as
$c_i := F_k(m_i \oplus c_{i-1})$ with a uniform $c_0$. (a) Show how to decrypt a
three-block ciphertext $c_0,c_1,c_2$. (b) Show CBC is not CCA-secure. —
(a) $m_i = F_k^{-1}(c_i)\oplus c_{i-1}$ for $i=1,2$; the IV $c_0$ is needed only
to unmask $m_1$ and is sent in the clear. (b) In the CCA game submit
$m_0 = 0^{\ell}$, $m_1 = 1^{\ell}$ (one block each) and receive
$c^*=(c_0,c_1)$. Flip the first bit of the **IV**: query the decryption oracle on
$(c_0\oplus 10^{\ell-1},\,c_1)$, which is a different ciphertext so the query is
legal. It decrypts to $m_b \oplus 10^{\ell-1}$, and reading its first bit gives
$b$. Advantage $1/2$, one query, and the block cipher is never attacked — the
scheme is malleable, which CCA-security forbids.

**Q5** *(F20 3a [S15]).* An engineer proposes: to encrypt $m\in\{0,1\}^\ell$
under $k$, choose $r\gets\{0,1\}^\ell$ and return $c := F_k(r)\oplus m$. Would
you recommend it if CCA-security is not required? — **No, and not for a security
reason.** $r$ is not part of the ciphertext, so the receiver cannot compute
$F_k(r)$ and the scheme is not *correct*. Construction 3.28 sends the pair
$(r,\ F_k(r)\oplus m)$; dropping the first component turns a CPA-secure scheme
into a random-number generator. Check correctness first.

**Q6** *(ours; the padding oracle is motivated on a lecture-7 slide as the reason
CCA is "not too paranoid" [S8], but no public paper examines it).* You control a
server that decrypts AES-CBC and returns "bad padding" or "bad format". Explain
how many queries you need to recover one plaintext block, and what the fix is. —
At most 256 guesses per byte and 128 on average, so at most
$256 \cdot 16 = 4096$ and on average about $128\cdot 16 = 2048$ queries per
16-byte block: since $m_i = D_k(c_i)\oplus c_{i-1}$, you control $m_i$'s tail
by editing $c_{i-1}$, so you brute-force one byte at a time to force valid
padding of value 1, then 2, and so on, learning $D_k(c_i)$ byte by byte.
**Linear in the length, not exponential** — `private_key.padding_oracle_attack`.
The fix is not to hide the error message (timing still leaks): it is
encrypt-then-MAC, so the tag is checked before $\mathsf{Dec}$ runs at all and the
oracle never exists (note 07).

## Code

`src/py/private_key.py`: `prf_encrypt`, `prf_decrypt`, `pad`, `unpad`,
`ecb_encrypt`, `cbc_encrypt`, `cbc_decrypt_raw`, `cbc_decrypt`, `ctr_keystream`,
`ctr_keystream_from`, `ctr_encrypt`, `ctr_decrypt`, `structured_image`,
`block_pattern`, `make_padding_oracle`, `padding_oracle_attack`.

`src/py/prg.py`: `chacha20_encrypt` (construction 1 in practice, RFC 8439).
Tests: `test_standard_vectors.py::test_sp800_38a_f2_cbc_aes128`,
`test_standard_vectors.py::test_sp800_38a_f5_ctr_aes128` (each on the library
AES and on `aes.PureAES`), `test_private_key.py::test_padding_oracle_recovers_plaintext`.
