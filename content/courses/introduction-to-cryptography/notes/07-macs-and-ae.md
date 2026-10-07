# 07 — MACs and authenticated encryption

*Lecture 8 [S8]. Katz-Lindell sec. 4, 5.2 and 5.4 [S10] — Def. 5.3. HMAC is
RFC 2104 [S19] / FIPS 198-1 [S29]; AEAD is RFC 5116 [S35]; GCM is
SP 800-38D [S31]. Code: [`../src/py/mac.py`](../src/py/mac.py).*

Encryption hides messages; it does not stop an adversary from *forging* or
*altering* them (note 02: the OTP is malleable; note 06: the padding oracle).
Message authentication codes provide **integrity/authenticity**, and combining
them with encryption the right way yields **authenticated encryption**, the
notion you actually want in practice.

## The unforgeability game

A MAC is $(\mathsf{Gen}, \mathsf{Mac}, \mathsf{Vrfy})$: $t\gets\mathsf{Mac}_k(m)$, and
$\mathsf{Vrfy}_k(m,t)\in\{0,1\}$ with $\mathsf{Vrfy}_k(m,\mathsf{Mac}_k(m))=1$.

$$
\begin{array}{l}
\mathsf{Mac\text{-}forge}_{\mathcal A,\Pi}(\lambda):\ k\gets\mathsf{Gen}(1^\lambda)\\
\quad \mathcal A^{\mathsf{Mac}_k(\cdot)}(1^\lambda)\to(m^*,t^*),\ \text{let } Q=\text{queried messages}\\
\quad \text{output }1\text{ iff }\mathsf{Vrfy}_k(m^*,t^*)=1 \text{ and } m^*\notin Q
\end{array}
$$

**Definition (EUF-CMA).** $\Pi$ is *existentially unforgeable under chosen-message
attack* if every PPT $\mathcal A$ wins with negligible probability. "Existential":
forging a tag on *any* new message counts, even a meaningless one. **Strong
unforgeability (sUF-CMA)** additionally forbids producing a *new tag on an
already-queried message* — required for authenticated encryption.

**Replay** is out of scope of the definition: $(m,t)$ replayed verbatim is not a
forgery ($m\in Q$). Real protocols stop replay with sequence numbers or
timestamps, layered on top of the MAC.

## Construction 1: PRF is a MAC

For fixed-length messages, $\mathsf{Mac}_k(m)=F_k(m)$, $\mathsf{Vrfy}$ recomputes and
compares (in constant time — `hmac.compare_digest`). Code: `mac.prf_mac`.

**Theorem.** If $F$ is a PRF then this is an EUF-CMA MAC, with
$\mathsf{Adv}^{\mathrm{forge}}_{\mathcal A}\le \mathsf{Adv}^{PRF}_{\mathcal B}+2^{-\ell_{out}}$.
*Proof.* Replace $F_k$ by a random function $f$ (cost $\mathsf{Adv}^{PRF}_{\mathcal B}$).
A forgery on a fresh $m^*$ must guess $f(m^*)$, an unqueried uniform value, right
with probability $2^{-\ell_{out}}$. So total forging probability is at most
$\mathsf{Adv}^{PRF}_{\mathcal B}+2^{-\ell_{out}}$, negligible. $\square$

## CBC-MAC and its length pitfall

**Basic CBC-MAC:** run CBC with a **zero IV** and output only the last block
(`mac.cbc_mac`). Secure as an EUF-CMA MAC **only for fixed-length messages**.

**The variable-length forgery.** With no length encoding, an attacker who has
$t_1=\mathsf{Mac}(m_1)$ and $t_2=\mathsf{Mac}(m_2)$ (single blocks) forges the tag of the
*two-block* message $m_1 \| (m_2\oplus t_1)$:
$$\text{block 1}: E_k(m_1\oplus 0)=t_1,\quad \text{block 2}: E_k((m_2\oplus t_1)\oplus t_1)=E_k(m_2)=t_2.$$
So its tag is $t_2$ — never queried. Code: `mac.cbc_mac_forgery`,
`test_mac.py::test_cbc_mac_variable_length_forgery`.

**Fixes** (any one): prepend the message length to the first block
(length-prepending); use a *separate* key to encrypt the final block (**EMAC/
CMAC**); or derive per-length keys. Note the trap: length must go *first*, not
last — appending it does not stop the attack.

## HMAC

A MAC from a hash function (note 08):
$$\mathrm{HMAC}_k(m) = H\big((k\oplus\mathrm{opad}) \,\|\, H((k\oplus\mathrm{ipad})\,\|\,m)\big),$$
with $\mathrm{ipad}=\mathtt{0x36}^B$, $\mathrm{opad}=\mathtt{0x5c}^B$, block size $B$
(64 for SHA-256) — RFC 2104 [S19], standardised as FIPS 198-1 [S29]. Two details
the formula hides and RFC 2104 sec. 2 spells out: a key **longer than $B$** is
first hashed (so a 131-octet key becomes a 32-octet one), and a shorter key is
zero-padded to $B$.

Code: `mac.hmac_sha256`, cross-checked byte-for-byte against Python's `hmac`
module (`test_mac.py::test_hmac_matches_stdlib_and_cryptography`) **and against the published
vectors** of RFC 4231 sec. 4 [S22] in
[`../src/py/test_standard_vectors.py`](../src/py/test_standard_vectors.py) —
test cases 1-4, 6 and 7, the last two with the over-length key, plus case 5's
truncation to 128 bits.

Why the nested structure? A naive $H(k\|m)$ with a Merkle-Damgard hash is
forgeable by **length extension** (note 08): from $H(k\|m)$ one computes
$H(k\|m\|\mathrm{pad}\|m')$ without $k$. The outer hash of HMAC hides the inner
chaining value, killing the extension. HMAC is a secure MAC if the compression
function is a PRF (and even under weaker assumptions).

## Combining encryption and MACs

Given a CPA-secure encryption and a (strong) MAC with **independent keys**, three
compositions. The relations between them were settled by Bellare and Namprempre
[S49], whose result is what the table's last column asserts: encrypt-then-MAC
with a strongly unforgeable MAC always yields authenticated encryption, and the
other two do not in general.

| Scheme | Construction | Secure AE? |
|---|---|---|
| **Encrypt-then-MAC** | $c=\mathsf{Enc}_{k_e}(m)$, $t=\mathsf{Mac}_{k_m}(c)$; send $(c,t)$ | **Yes** — always |
| **MAC-then-Encrypt** | $c=\mathsf{Enc}_{k_e}(m\|\mathsf{Mac}_{k_m}(m))$ | Only sometimes |
| **Encrypt-and-MAC** | $c=\mathsf{Enc}_{k_e}(m)$, $t=\mathsf{Mac}_{k_m}(m)$; send $(c,t)$ | **No** in general |

**Encrypt-then-MAC (EtM)** is the robust choice. Verifying the tag on the
*ciphertext* first means malformed ciphertexts are rejected *before* decryption,
so no decryption oracle (padding or otherwise) can arise — it gives **ciphertext
integrity**, which together with CPA-security yields CCA-security /
authenticated encryption. Code: `mac.encrypt_then_mac`/`etm_decrypt`, which
verifies before decrypting and raises on tamper
(`test_mac.py::test_encrypt_then_mac_roundtrip_and_tamper`).

- **MtE** (used by old TLS with CBC) can be insecure: decryption happens before
  the MAC check, reopening the padding oracle.
- **E&M** (old SSH) leaks: the tag is computed on the *plaintext* and a
  deterministic MAC reveals equality of plaintexts, breaking CPA; and it gives no
  ciphertext integrity.
- **Independent keys are mandatory.** Reusing one key for both $\mathsf{Enc}$ and
  $\mathsf{Mac}$ voids every proof.

## Authenticated encryption (AE / AEAD)

**AE** (K&L Def. 5.3 [S8, S10]) = CCA-security + **unforgeable encryption**
(ciphertext integrity): no PPT adversary with an encryption oracle can produce a
ciphertext that decrypts successfully and was not an oracle output. Since
CPA-security plus ciphertext integrity already implies CCA-security, proving
CPA + integrity is enough, which is how the encrypt-then-MAC proof goes. **AEAD** adds *associated data* —
headers that are authenticated but not encrypted, e.g. packet routing info. The
interface and the requirement that a nonce never repeat under one key are
RFC 5116 [S35].

**GCM (Galois/Counter Mode)**, NIST SP 800-38D [S31], is the standard AEAD:
CTR-mode encryption for secrecy, plus a **GHASH** universal-hash MAC over the
ciphertext and associated data — polynomial evaluation in $\mathrm{GF}(2^{128})$
keyed by the **hash subkey** $H = \mathrm{CIPH}_K(0^{128})$ — finalised by
encrypting a counter block. Fast, parallel, one key.

**Nonce reuse is fatal** (note 06), and the standard says so itself: SP 800-38D
appendix A states that if an IV is reused with the same key an adversary can
recover the hash subkey and forge [S31]. So it is not only a two-time pad on the
plaintexts; **integrity** collapses too. (Idea only; the course treats GCM at the
level of "CTR + polynomial MAC" [S8].)

## Worked example

*Prove Encrypt-and-MAC is not CPA-secure when the MAC is deterministic.* The tag
$t=\mathsf{Mac}_{k_m}(m)$ is a deterministic function of $m$. In the CPA game,
$\mathcal A$ outputs $m_0\ne m_1$, receives $(c,t)$, and *also* queries the
encryption oracle on $m_0$ to get $(c_0,t_0)$ with $t_0=\mathsf{Mac}_{k_m}(m_0)$.
If $t=t_0$ then $b=0$, else $b=1$ — the tag alone reveals the plaintext.
Advantage $\approx 1/2$. $\square$

## Pitfalls

- **Verify in constant time.** A byte-by-byte compare that early-exits is a
  timing oracle; use `compare_digest`.
- **MAC the ciphertext, not the plaintext,** and verify *before* decrypting.
- **Separate keys** for encryption and authentication.
- **Length matters for CBC-MAC** — fixed length, or CMAC; and length goes first.
- **Naive $H(k\|m)$ is not a MAC** with Merkle-Damgard hashes (length extension);
  use HMAC.
- **Nonce uniqueness for GCM** — reuse breaks integrity, not just secrecy.

## Exam-style questions

**Q1** *(M25 4 [S13] — a 6-point reduction, the highest-value question on that
paper).* Let $F:\{0,1\}^n\times\{0,1\}^n\to\{0,1\}^n$ be a PRF. Prove by
reduction that $\mathsf{Mac}_k(m) := F_k(m)\oplus m$ (fixed-length $m$) is
EUF-CMA. — Let $\mathcal A$ forge with probability $\varepsilon$ after $q$
queries. Build a PRF-distinguisher $\mathcal B^{\mathcal O}$: answer each query
$m_i$ with $\mathcal O(m_i)\oplus m_i$; when $\mathcal A$ outputs
$(m^*,t^*)$ with $m^*\notin\{m_i\}$, query $\mathcal O(m^*)$ and output 1 iff
$t^* = \mathcal O(m^*)\oplus m^*$.
*Simulation:* perfect — $\mathcal B$ computes exactly what the challenger would.
*Analysis:* if $\mathcal O = F_k$, $\mathcal A$'s view is the real game, so
$\Pr[\mathcal B\to1] = \varepsilon$. If $\mathcal O = f$ is random, $f(m^*)$ is
uniform and unqueried, so $t^* = f(m^*)\oplus m^*$ holds with probability
$2^{-n}$. Hence $\mathsf{Adv}^{\mathrm{PRF}}_{\mathcal B} =
\varepsilon - 2^{-n}$, so $\varepsilon \le
\mathsf{Adv}^{\mathrm{PRF}}_{\mathcal B} + 2^{-n}$, negligible. *(The XOR with
$m$ is a red herring — it is a bijection applied to a value the adversary cannot
predict. Saying so is not a proof; the reduction above is.)*

**Q2** *(M25 5 [S13]).* Given a CPA-secure scheme
$(\mathsf{Gen}_E,\mathsf{Enc},\mathsf{Dec})$ and a secure deterministic canonical
MAC $(\mathsf{Gen}_M,\mathsf{Mac},\mathsf{Vrfy})$, construct a secure
authenticated encryption scheme by specifying all three algorithms. —
Encrypt-then-MAC with **independent** keys:
$\mathsf{Gen}(1^n)$: $k_E\gets\mathsf{Gen}_E(1^n)$, $k_M\gets\mathsf{Gen}_M(1^n)$,
return $(k_E,k_M)$.
$\mathsf{Enc}'_{(k_E,k_M)}(m)$: $c\gets\mathsf{Enc}_{k_E}(m)$,
$t := \mathsf{Mac}_{k_M}(c)$, return $(c,t)$.
$\mathsf{Dec}'_{(k_E,k_M)}(c,t)$: if $\mathsf{Vrfy}_{k_M}(c,t)\neq 1$ return
$\bot$; **else** return $\mathsf{Dec}_{k_E}(c)$.
The three things that must be said out loud: independent keys, the MAC is over
the **ciphertext**, and verification happens **before** decryption.

**Q3** *(F23 3 [S12]).* $F$ is a PRF and $H:\{0,1\}^*\to\{0,1\}^n$ a hash.
Show that $\mathsf{Mac}_k(m) := F_k(H(m))$ is insecure if $H$ is not collision
resistant. — Suppose the adversary knows $x\neq x'$ with $H(x)=H(x')$ (that is
what "not collision resistant" gives it). Query the MAC oracle on $x$, receive
$t = F_k(H(x))$, and output $(x', t)$. Then
$\mathsf{Vrfy}_k(x',t)$ recomputes $F_k(H(x')) = F_k(H(x)) = t$ and accepts, and
$x'$ was never queried. One query, success probability 1. The PRF is never
attacked — the hash alone sinks it, which is why hash-and-MAC needs collision
resistance and not merely one-wayness.

**Q4** *(F20 5a [S15]).* Show basic CBC-MAC is insecure when messages from both
$\{0,1\}^\ell$ and $\{0,1\}^{2\ell}$ are allowed. — Query the two one-block
messages $m_1$ and $m_2$, getting $t_1 = F_k(m_1)$ and $t_2 = F_k(m_2)$. Output
the two-block forgery $m^* := m_1 \,\|\, (m_2\oplus t_1)$ with tag $t^* := t_2$.
CBC-MAC on $m^*$ computes block 1 as $F_k(m_1\oplus 0^\ell)=t_1$ and block 2 as
$F_k\big((m_2\oplus t_1)\oplus t_1\big)=F_k(m_2)=t_2$. Valid, never queried,
advantage $\approx 1$. Fixes: prepend the length to the message (prepend, not
append), or encrypt the final block under a second key (CMAC).

**Q5** *(F20 5b [S15]).* Why is encrypt-and-authenticate,
$\mathsf{Enc}'_{(k_E,k_M)}(m) := \mathsf{Enc}_{k_E}(m)\,\|\,\mathsf{Mac}_{k_M}(m)$,
not CPA-secure when the MAC is basic CBC-MAC? — Because CBC-MAC is
**deterministic** and computed over the *plaintext*. In the CPA game, query the
oracle on $m_0$ and keep the tag $t_0$; then submit $(m_0,m_1)$ and receive
$(c,t)$. If $t = t_0$ then $b=0$, else $b=1$. Correct with probability 1,
advantage $1/2$. Any deterministic function of the plaintext appearing in the
clear destroys indistinguishability — it is the ECB argument one level up.

**Q6** *(F23 1f/1g [S12]).* Can a deterministic MAC be secure? Does a MAC prevent
replay attacks? — **Yes** and **no**, respectively. A MAC has no
indistinguishability requirement, so determinism costs nothing: $F_k(m)$ is a
secure MAC (and canonical verification — recompute and compare — needs it).
Replay is *outside* the definition: $(m,t)$ replayed verbatim has $m\in Q$, so
the game does not call it a forgery, and indeed the receiver cannot tell an
honest message from a copy of one. Freshness is the protocol layer's job:
sequence numbers or timestamps, as TLS does (note 12).

## Code

`src/py/mac.py`: `prf_mac`, `prf_mac_verify`, `cbc_mac`, `cbc_mac_forgery`,
`hmac`, `hmac_sha256`, `hkdf_extract`, `hkdf_expand`, `hkdf`,
`encrypt_then_mac`, `etm_decrypt`. Tests:
`test_standard_vectors.py::test_rfc4231_hmac_sha256` [S22],
`test_mac.py::test_hkdf_rfc5869_appendix_a` [S34],
`test_mac.py::test_cbc_mac_over_aes_is_the_last_cbc_block`,
`test_hashing.py::test_prf_mac_on_variable_length_messages_is_forgeable_but_hmac_is_not`.
