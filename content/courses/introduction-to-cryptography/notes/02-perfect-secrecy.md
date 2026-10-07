# 02 — Perfect secrecy

*Lecture 2 [S8]. Katz-Lindell sec. 2 [S10] — Def. 2.3, Lemma 2.7, Thm 2.10,
Thm 2.12. Code: [`../src/py/otp.py`](../src/py/otp.py), and the Z_26 version in
[`../src/py/classical.py`](../src/py/classical.py).*

The first question of the course: can encryption be secure against an adversary
with **unlimited computing power**? The surprising answer is yes — but only at a
steep price in key length. This note makes "secure" precise (perfect secrecy),
exhibits the standard scheme achieving it (the one-time pad), and proves the
price is unavoidable.

## Setup

A private-key encryption scheme is a triple $(\mathsf{Gen}, \mathsf{Enc}, \mathsf{Dec})$:

- $\mathsf{Gen}$ outputs a key $k \in \mathcal{K}$;
- $\mathsf{Enc}_k(m) \in \mathcal{C}$ encrypts $m \in \mathcal{M}$;
- $\mathsf{Dec}_k(c) \in \mathcal{M}$, with correctness $\mathsf{Dec}_k(\mathsf{Enc}_k(m)) = m$.

Fix a distribution over $\mathcal{M}$ (the attacker's *a priori* knowledge of the
message) and let $k \gets \mathsf{Gen}$ be independent of $m$. Write $M, K, C$ for
the random variables.

## Definition (perfect secrecy)

A scheme is **perfectly secret** if for every distribution over $\mathcal{M}$,
every $m \in \mathcal{M}$, and every $c \in \mathcal{C}$ with $\Pr[C=c] > 0$:

$$\Pr[M = m \mid C = c] = \Pr[M = m].$$

The ciphertext gives the adversary *nothing*: her posterior equals her prior.

**Equivalent formulations** (K&L Lemma 2.7 [S10]; *"every perfectly secret
scheme is perfectly indistinguishable and vice versa"* is a true/false item on
the 2025W midterm [S13]):

1. **Independence:** $M$ and $C$ are independent.
2. **Ciphertext indistinguishability:** for all $m_0, m_1 \in \mathcal{M}$ and all $c$,
   $$\Pr[\mathsf{Enc}_K(m_0) = c] = \Pr[\mathsf{Enc}_K(m_1) = c].$$
   The distribution of ciphertexts does not depend on the message.
3. **The adversarial game** $\mathsf{PrivK}^{\mathrm{eav}}_{\mathcal{A},\Pi}$ below is won with probability exactly $1/2$.

### The indistinguishability game

$$
\begin{array}{l}
\mathsf{PrivK}^{\mathrm{eav}}_{\mathcal{A},\Pi}:\\
\quad \mathcal{A} \text{ outputs } m_0, m_1 \in \mathcal{M}\\
\quad b \gets \{0,1\},\ k \gets \mathsf{Gen},\ c \gets \mathsf{Enc}_k(m_b)\\
\quad \mathcal{A}(c) \text{ outputs } b';\ \text{game outputs } 1 \text{ iff } b'=b
\end{array}
$$

Perfect secrecy $\iff \Pr[\mathsf{PrivK}^{\mathrm{eav}}_{\mathcal{A},\Pi}=1] = \tfrac12$ for **every** (even unbounded) $\mathcal{A}$. This game template — challenger flips $b$, adversary guesses — recurs in every later note; only the adversary's power and interaction change.

## The one-time pad

$\mathcal{M} = \mathcal{K} = \mathcal{C} = \{0,1\}^\ell$. $\mathsf{Gen}$: $k \gets \{0,1\}^\ell$ uniform.
$\mathsf{Enc}_k(m) = k \oplus m$, $\mathsf{Dec}_k(c) = k \oplus c$.

**Theorem (Shannon 1949).** The OTP is perfectly secret.

*Proof.* Fix $c$. For any $m$, $\Pr[C = c \mid M=m] = \Pr[K = m \oplus c] = 2^{-\ell}$,
independent of $m$. By the independence formulation, done. Concretely,
$\Pr[C=c] = \sum_m \Pr[M=m]2^{-\ell} = 2^{-\ell}$, so by Bayes
$\Pr[M=m\mid C=c] = \frac{2^{-\ell}\Pr[M=m]}{2^{-\ell}} = \Pr[M=m]$. $\square$

Code: `otp.encrypt`/`otp.decrypt`; `test_otp.py::test_ciphertext_uniform_for_fixed_message`
checks empirically that for a fixed message the 256 possible one-byte ciphertexts
occur about equally often.

## Why "one-time": the two-time pad

Reuse the *same* key on two messages and the key cancels:
$$c_1 \oplus c_2 = (k \oplus m_1) \oplus (k \oplus m_2) = m_1 \oplus m_2.$$
The adversary learns the XOR of the plaintexts — no key needed. For natural-
language plaintext this leaks almost everything via **crib dragging**: slide a
guessed word (a "crib") along $m_1\oplus m_2$; where the crib is correct, XORing
it out reveals a readable fragment of the *other* message. See `otp.two_time_pad_leak`,
`otp.crib_drag`, and the `__main__` demo, which recovers text from two reused-key
ciphertexts.

The perfect-secrecy theorem is not violated: it assumes a *fresh* key per
encryption. Two encryptions under one key is a different (weaker) experiment.

## Shannon's theorem: the exact characterisation

**Theorem 2.12 (Shannon) [S8, S10].** Let $\Pi$ be a scheme with
$|\mathcal M| = |\mathcal K| = |\mathcal C|$. Then $\Pi$ is perfectly secret
**if and only if**

1. every key is chosen with probability $1/|\mathcal K|$ by $\mathsf{Gen}$, **and**
2. for every $m\in\mathcal M$ and every $c\in\mathcal C$ there is a **unique**
   $k\in\mathcal K$ with $\mathsf{Enc}_k(m)=c$.

> **Read both conditions.** The 2025W midterm prints the statement with
> condition 1 removed and asks whether it is Shannon's theorem — the official
> answer is **false** [S13]. Condition 2 alone says the map
> $k\mapsto \mathsf{Enc}_k(m)$ is a bijection for each $m$; with a *biased*
> $\mathsf{Gen}$ that still leaks. Take $\mathcal M=\mathcal K=\mathcal C=\{0,1\}$,
> $\mathsf{Enc}_k(m)=m\oplus k$, and $\Pr[K=0]=0.9$: condition 2 holds, and yet
> $\Pr[M=0\mid C=0]=0.9\ne\Pr[M=0]$ for uniform $M$.

The theorem is also the fastest way to *prove a scheme perfectly secret* when
the three spaces have equal size: check the counting condition and the key
distribution, and you are done, with no Bayes computation.

## The price: keys must be as long as messages

**Theorem (Shannon bound).** If $\Pi$ is perfectly secret then $|\mathcal{K}| \ge |\mathcal{M}|$.

*Proof.* Suppose $|\mathcal{K}| < |\mathcal{M}|$. Take $M$ uniform on $\mathcal{M}$ and any
$c$ with $\Pr[C=c]>0$. Let $\mathcal{M}(c) = \{\mathsf{Dec}_k(c) : k \in \mathcal{K}\}$;
then $|\mathcal{M}(c)| \le |\mathcal{K}| < |\mathcal{M}|$, so some $m^* \notin \mathcal{M}(c)$.
For that message $\Pr[M=m^* \mid C=c] = 0 \ne \Pr[M=m^*] = 1/|\mathcal M|$,
contradicting perfect secrecy. $\square$

Consequence: to encrypt a 1 GB file with perfect secrecy you need a fresh,
truly random 1 GB key, shared in advance. This is why the rest of the course
*relaxes* the definition (note 04): we settle for security against *efficient*
adversaries and get short, reusable keys.

**Perfect secrecy does not hide the length.** $\mathcal M$ is a *fixed-length*
space throughout. A scheme whose ciphertext length depends on the message
length leaks that length, however well the bits themselves are hidden.

## Worked example

*Claim: the "shift cipher" (Caesar) on a single letter over $\mathbb{Z}_{26}$ with
uniform key is perfectly secret, but on two-letter messages it is not.*

Single letter: $\mathsf{Enc}_k(m) = m+k \bmod 26$, $k$ uniform — this is the OTP over
$\mathbb Z_{26}$, so perfectly secret by the theorem. Two letters with the *same*
key $k$: $c = (m_1+k, m_2+k)$, so $c_1 - c_2 = m_1 - m_2 \bmod 26$ is leaked
regardless of $k$. Pick $m_0 = (\mathtt{A},\mathtt{A})$, $m_1=(\mathtt{A},\mathtt{B})$:
their difference vectors ($0$ vs $-1$) differ, so an adversary reading $c_1-c_2$
wins the indistinguishability game with probability $1$. Not perfectly secret.

## Pitfalls

- **"Random-looking" is not perfect secrecy.** Perfect secrecy is about the
  *conditional distribution*, not about the ciphertext looking messy.
- **Fresh key each time.** The OTP theorem silently assumes it; forgetting this
  is the two-time-pad disaster.
- **Perfect secrecy $\ne$ integrity.** The OTP is malleable: flipping a
  ciphertext bit flips the plaintext bit (`otp.malleability_demo`). An
  adversary can turn "our" into "the" without breaking secrecy. Secrecy and
  authenticity are orthogonal goals (note 07).
- **Key must be uniform.** A biased key destroys the proof; $\Pr[K=m\oplus c]$
  is then no longer constant in $m$.

## Exam-style questions

**Q1** *(M25 1d [S13] — the most precisely worded item on any past paper).*
"According to Shannon's theorem, a scheme $\Pi$ with
$|\mathcal M|=|\mathcal K|=|\mathcal C|$ is perfectly secret if for every
$m\in\mathcal M$, $c\in\mathcal C$ there is a unique $k\in\mathcal K$ with
$\mathsf{Enc}_k(m)=c$." True or false? — **False.** The theorem has two
conditions and this quotes only the second; it also requires
$\mathsf{Gen}$ to output every key with probability $1/|\mathcal K|$. The
one-bit counterexample with $\Pr[K=0]=0.9$ is above.

**Q2** *(M25 1c [S13]).* Is every perfectly secret scheme perfectly
indistinguishable, and conversely? — **True**, K&L Lemma 2.7. ($\Rightarrow$)
Perfect secrecy makes $M$ and $C$ independent, so
$\Pr[C=c\mid M=m_i]=\Pr[C=c]$ for both $i$, and these are exactly
$\Pr[\mathsf{Enc}_K(m_i)=c]$. ($\Leftarrow$) If the two agree for all
messages then $\Pr[C=c\mid M=m]$ is constant in $m$, which is independence.

**Q3** *(F23 1a [S12]).* Can an unbounded adversary break a perfectly secret
encryption scheme? — **No.** Perfect secrecy quantifies over *all* adversaries,
with no efficiency restriction; the posterior equals the prior as a statement
about distributions, so there is nothing left for computation to extract. This
is the whole difference from note 04, where security holds only against PPT
adversaries.

**Q4** *(F23 2b/2c [S12]).* Define the one-time pad by giving
$\mathcal K$, $\mathcal M$ and all three algorithms, then say whether it is
CPA-secure. — $\mathcal K=\mathcal M=\mathcal C=\{0,1\}^\ell$;
$\mathsf{Gen}$ returns $k\gets\{0,1\}^\ell$ uniform;
$\mathsf{Enc}_k(m)=k\oplus m$; $\mathsf{Dec}_k(c)=k\oplus c$. **Not
CPA-secure**, for two independent reasons. (i) $\mathsf{Enc}$ is deterministic,
so one oracle query on $m_0$ and a comparison with the challenge wins with
probability 1 (note 06). (ii) More basically, the CPA game hands the adversary
an encryption oracle *under the same key*, and the scheme's security statement
covers a single message per key — two encryptions are the two-time pad, and
$c_1\oplus c_2=m_1\oplus m_2$.

## Code

`src/py/otp.py`: `keygen`, `encrypt`, `xor`, `two_time_pad_leak`, `crib_drag`,
`malleability_demo`. Tests: `test_otp.py::test_every_ciphertext_exactly_once_per_message`
(Thm 2.10 by enumeration), `test_otp.py::test_pseudo_one_time_pad_reproduces_rfc8439`
(the pad replaced by a ChaCha20 keystream reproduces RFC 8439 sec. 2.4.2 [S36]).

`src/py/classical.py`: `vernam_encrypt`, `vernam_decrypt` (the Z_26 version).
