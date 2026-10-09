# 02 — Perfect secrecy

*Lecture 2, 08.10.2026, finished in the first minutes of the 15:00 lecture
[S8, S58]. Katz-Lindell sec. 1.4, sec. 2 and App. A.3 [S10]: Ex. 2.1,
Def. 2.3, Thm 2.10, Thm 2.11, Thm 2.12 as numbered on the 2026W slides [S58];
Lemma 2.7 is from the older decks [S8]. Code:
[`../src/py/otp.py`](../src/py/otp.py), and the Z_26 version in
[`../src/py/classical.py`](../src/py/classical.py).*

The first question of the course: can encryption be secure against an adversary
with **unlimited computing power**? The surprising answer is yes — but only at a
steep price in key length. This note makes "secure" precise (perfect secrecy),
exhibits the standard scheme achieving it (the one-time pad), and proves the
price is unavoidable.

In 2026W the lecture first spends about an hour on what "modern" cryptography
means and how security definitions are built [S58]; that part comes first here.

## Provable security: definitions, assumptions, proofs

Around 1980 cryptography changed from a craft, where schemes were proposed,
broken and patched, into a science [S58]. A security claim now has three
ingredients:

1. **A definition**: the adversary's *goal* (what counts as a break) and the
   *threat model* (what the adversary may see and do).
2. **An assumption**: a precisely stated problem believed to be hard, such as
   factoring the product of two large random primes.
3. **A proof** that the scheme meets the definition under the assumption.

Why assumptions at all: a secure scheme of any interest would imply
$\mathrm P \ne \mathrm{NP}$, which nobody can prove, so unconditional security
proofs are out of reach except for schemes like the one-time pad below [S58].
Public-key assumptions are mathematical (factoring, discrete logarithms modulo
a prime or on an elliptic curve); symmetric ones are usually ad hoc, of the
form "this block cipher is secure", backed by years of failed attacks [S58].

**The reduction, in the right direction.** To show problem B is at least as hard
as problem A, turn any algorithm for B into one for A. In cryptography A is the
assumption and B is "break the scheme": the proof takes an arbitrary adversary
and builds from it an efficient algorithm for the hard problem. Two differences
from NP-hardness, both stressed in the lecture [S58]: cryptography needs
**average-case** hardness (a randomly generated key must be hard to attack, not
just some worst-case instance), and factoring, the running example, is not
known to be NP-complete.

**How a proven scheme still fails** [S58]: the assumption is false (a large
quantum computer factors efficiently), or, more often, the definition missed a
real requirement (it allowed one ciphertext per key, and the key was used
twice). The gain is that a new scheme inherits the confidence earned by a
problem that has been studied for a long time, instead of needing years of
attacks of its own. The lecture calls the definition the hardest and most
creative step [S58].

### Building a definition for encryption

Kerckhoffs: the adversary knows the scheme. What should it fail at? The lecture
rejects three candidate goals by counterexample [S58]:

| candidate goal for the adversary | scheme that resists it and is obviously insecure |
|---|---|
| find the key | $\mathsf{Enc}_k(m) = m$: the ciphertext says nothing about $k$ |
| recover the whole plaintext | encrypt the first half with AES, send the second half in the clear |
| recover any single letter | still leaks, e.g. the order of magnitude of an encrypted salary |

So the goal is fixed once and for all: **the ciphertext reveals no information
about the plaintext** ("be paranoid"). What grows during the course is the
adversary's *power* [S58]:

- sees one ciphertext, or many under the same key (Vigenère falls to one long
  ciphertext);
- has seen plaintext-ciphertext pairs (for Vigenère and the one-time pad one
  pair yields the key);
- can have plaintexts of its choice encrypted (someone replies to your e-mail
  and quotes it; a public terminal encrypting whatever you type): **chosen
  plaintext**;
- can also have ciphertexts of its choice decrypted (injecting into the
  terminal's line): **chosen ciphertext**.

The lecture names indistinguishability under chosen-ciphertext attack as the
standard notion for symmetric encryption today [S58]; notes 04-06 build up to
it. Perfect secrecy, below, is the weakest power: one ciphertext.

## Setup

A private-key encryption scheme is a triple $(\mathsf{Gen}, \mathsf{Enc}, \mathsf{Dec})$:

- $\mathsf{Gen}$ outputs a key $k \in \mathcal{K}$;
- $\mathsf{Enc}_k(m) \in \mathcal{C}$ encrypts $m \in \mathcal{M}$;
- $\mathsf{Dec}_k(c) \in \mathcal{M}$, with correctness $\mathsf{Dec}_k(\mathsf{Enc}_k(m)) = m$.

Fix a distribution over $\mathcal{M}$ (the attacker's *a priori* knowledge of the
message) and let $k \gets \mathsf{Gen}$ be independent of $m$. Write $M, K, C$ for
the random variables.

The step the lecture asks you to accept [S58]: **knowledge about the message is
a probability distribution over messages.** A trader who sends only "buy" or
"sell" in a rising market is modelled by, say, $\Pr[M=\text{buy}]=0.7$,
$\Pr[M=\text{sell}]=0.3$. $K$ is distributed as $\mathsf{Gen}$'s output, and
$C$ is the result of drawing $m$ from $M$, $k$ from $\mathsf{Gen}$ and
encrypting. **$K$ and $M$ are assumed independent**, which the lecture calls
crucial: the key is chosen without looking at the message.

The proof below uses only four facts from App. A.3 [S58, S10]: the definition
$\Pr[X=x\mid Y=y] = \Pr[X=x \wedge Y=y]/\Pr[Y=y]$; Bayes,
$\Pr[X=x\mid Y=y] = \Pr[Y=y\mid X=x]\Pr[X=x]/\Pr[Y=y]$; independence,
$\Pr[X=x\mid Y=y] = \Pr[X=x]$; and total probability,
$\Pr[X=x] = \sum_i \Pr[X=x\mid Y=y_i]\Pr[Y=y_i]$ when the $y_i$ exhaust the
outcomes.

### Example 2.1: a shift cipher on one letter

Use the shift cipher with a uniform key in $\{0,\dots,25\}$ on single letters,
and let the trader send B (buy) with probability $0.7$ and D (drop) with $0.3$
[S58]. The ciphertext F arises from B with key 4 or from D with key 2, so by
independence

$$\Pr[C=\mathtt F] = 0.7\cdot\tfrac1{26} + 0.3\cdot\tfrac1{26} = \tfrac1{26}.$$

Change the market to $0.1$ and $0.9$, or ask for G instead of F: the two
message probabilities still sum to 1 and each key still has probability
$1/26$, so every ciphertext letter keeps probability $1/26$. The ciphertext
distribution does not depend on the message distribution, which is the
intuition the definition captures.

## Definition (perfect secrecy)

A scheme is **perfectly secret** if for every distribution over $\mathcal{M}$,
every $m \in \mathcal{M}$, and every $c \in \mathcal{C}$ with $\Pr[C=c] > 0$:

$$\Pr[M = m \mid C = c] = \Pr[M = m].$$

The ciphertext gives the adversary *nothing*: her posterior equals her prior.
This is K&L Def. 2.3 as stated in the 2026W lecture [S58]. The condition
$\Pr[C=c]>0$ only avoids conditioning on an impossible event, and the
adversary's power is a single ciphertext.

**Equivalent formulations** (K&L Lemma 2.7 [S10]; *"every perfectly secret
scheme is perfectly indistinguishable and vice versa"* is a true/false item on
the 2025W midterm [S13]). Neither the lemma nor the game below appears in the
2026W lectures 1-3 [S58]; they may come with computational security (note 04),
so treat them as likely but not yet announced:

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

Decryption works because XOR undoes itself:
$\mathsf{Dec}_k(\mathsf{Enc}_k(m)) = k\oplus(k\oplus m) = (k\oplus k)\oplus m =
0^\ell\oplus m = m$. The 2026W slide writes $\mathsf{Gen}$, $\mathsf{Enc}$ and
$\mathsf{Dec}$ as three lines of pseudocode with a bitwise loop and then this
correctness line; the lecturer said that level of formality is what the
exercises expect [S58].

**Theorem 2.10.** The OTP is perfectly secret [S58, S10]. (Vernam proposed the
scheme in 1917; Shannon proved its secrecy in 1949 [S58, S50].)

*Proof, in the order of the 2026W slide* [S58]. Fix an arbitrary distribution
$M$, message $m$ and ciphertext $c$; since nothing is assumed about them, the
result holds for all of them.

- $(*)$ $\mathsf{Gen}$ is uniform: $\Pr[K=k] = 2^{-\ell}$ for every $k$.
- $(**)$ $\Pr[C=c\mid M=m] = \Pr[K\oplus M = c\mid M=m] = \Pr[K\oplus m = c\mid M=m]
  = \Pr[K = m\oplus c\mid M=m] = \Pr[K=m\oplus c] = 2^{-\ell}$, using
  independence of $K$ and $M$ for the fourth step and $(*)$ for the last.
- $(*\!*\!*)$ Total probability over all messages $m'$, then $(**)$:
  $\Pr[C=c] = \sum_{m'}\Pr[C=c\mid M=m']\Pr[M=m'] = 2^{-\ell}\sum_{m'}\Pr[M=m'] = 2^{-\ell}$.
- Bayes with $(**)$ and $(*\!*\!*)$:
  $\Pr[M=m\mid C=c] = \dfrac{\Pr[C=c\mid M=m]\Pr[M=m]}{\Pr[C=c]} =
  \dfrac{2^{-\ell}\Pr[M=m]}{2^{-\ell}} = \Pr[M=m]$. $\square$

(With Lemma 2.7 the proof stops after $(**)$: the ciphertext distribution does
not depend on $m$.) The lecturer asked students to go through this proof slowly
on their own [S58]; expect to write arguments in exactly this style.

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

**The lecture's small example** [S58]. A trader sends one letter to the stock
exchange, B or S (buy, sell), and one to his spouse, Y or N, both as 7-bit
codes and both under the same key. In ASCII the four possible XORs
$\mathtt B\oplus\mathtt Y$, $\mathtt B\oplus\mathtt N$, $\mathtt S\oplus\mathtt Y$,
$\mathtt S\oplus\mathtt N$ are pairwise different, so $c_1\oplus c_2$ alone
tells the eavesdropper both messages. (The 2026W slide uses a 7-bit code for Y
that is ASCII V; with either code the four XORs differ, so the conclusion is the
same.) In general $m_1\oplus m_2$ need not reveal everything, but with a small
or structured message space it usually does.

**The practical price** [S58]: the key is as long as the message and is used
once, so the one-time pad needs large amounts of true randomness, a secure way
to *distribute* that much key material in advance, and a way to *destroy* it
after use. In the Cold War the Moscow-Washington line reportedly used it, with
key material carried by courier [S58].

## Shannon's theorem: the exact characterisation

**Theorem 2.12 (Shannon) [S8, S10, S58].** Let $\Pi$ be a scheme with
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

**Theorem 2.11.** If $\Pi$ is perfectly secret then $|\mathcal{K}| \ge |\mathcal{M}|$.
(The 2026W slides number this bound separately, as Thm 2.11, before Shannon's
characterisation Thm 2.12; earlier versions of this note folded both into
"Shannon" [S58].) In the lecture both theorems come just before the move to
computational security: together they say the one-time pad's drawbacks are
not an accident of the scheme but forced on **every** perfectly secret scheme,
the price of security against unbounded adversaries [S58].

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
- **Key independent of message.** Step $(**)$ of the proof drops the condition
  $M=m$ only because $K$ and $M$ are independent [S58].
- **"Hard to find the key" is not a security definition.** $\mathsf{Enc}_k(m)=m$
  satisfies it [S58]. Neither is "hard to find the whole message".

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

## Cards

```card id=crypto-l2-provable-security
The three ingredients of provable security.
---
A definition (adversary's goal and threat model), an assumption (a precisely stated problem believed hard), and a proof that the scheme meets the definition under the assumption.
```

```card id=crypto-l2-reduction-direction
A security proof by reduction: what is turned into what?
---
Any adversary breaking the scheme is turned into an efficient algorithm for the hard problem (e.g. factoring). So breaking the scheme is at least as hard as the problem.
```

```card id=crypto-l2-why-assumptions
Why does practical cryptography need hardness assumptions?
---
Security of any interesting scheme implies P $\ne$ NP, which is unproven. Only information-theoretic schemes like the one-time pad avoid assumptions, at a high price.
```

```card id=crypto-l2-average-case
Why is NP-hardness the wrong kind of hardness for cryptography?
---
NP-hardness is worst case. A randomly generated key must give a hard instance, so cryptography needs average-case hardness. (Factoring is not even known to be NP-complete.)
```

```card id=crypto-l2-proof-failure
Two ways a provably secure scheme can still fail.
---
The assumption is false (e.g. quantum computers factor), or the definition misses a real requirement (e.g. it allows one ciphertext per key and the key is reused). The second is more common.
```

```card id=crypto-l2-bad-goals
Why are "find the key" and "recover the plaintext" bad security goals?
---
$\mathsf{Enc}_k(m)=m$ hides the key; encrypting half the message and sending the rest in clear hides the full plaintext. The goal must be: no information about the plaintext.
```

```card id=crypto-l2-adversary-powers
Adversary powers in increasing order (lecture 2).
---
One ciphertext; many ciphertexts; known plaintext-ciphertext pairs; chosen plaintexts (encryption queries); chosen ciphertexts (decryption queries).
```

```card id=crypto-l2-perfect-secrecy
Def. 2.3: perfect secrecy.
---
For every distribution over $\mathcal M$, every $m$ and every $c$ with $\Pr[C=c]>0$: $\Pr[M=m\mid C=c]=\Pr[M=m]$.
```

```card id=crypto-l2-example-shift
Example 2.1: one letter, shift cipher, $\Pr[M=B]=0.7$, $\Pr[M=D]=0.3$. What is $\Pr[C=F]$?
---
$0.7\cdot\frac1{26}+0.3\cdot\frac1{26}=\frac1{26}$ (B with key 4, D with key 2, $K$ and $M$ independent). The same for any message distribution and any letter.
```

```card id=crypto-l2-otp-proof
Proof skeleton of Thm 2.10 (one-time pad perfectly secret).
---
(*) $\Pr[K=k]=2^{-\ell}$. (**) $\Pr[C=c\mid M=m]=\Pr[K=m\oplus c]=2^{-\ell}$ by independence. (***) total probability: $\Pr[C=c]=2^{-\ell}$. Bayes: $\Pr[M=m\mid C=c]=\Pr[M=m]$.
```

```card id=crypto-l2-independence
Which assumption about $K$ and $M$ does the one-time pad proof need, and where?
---
$K$ and $M$ independent: it lets $\Pr[K=m\oplus c\mid M=m]$ become $\Pr[K=m\oplus c]$.
```

```card id=crypto-l2-key-reuse
One-time pad key used twice: what leaks?
---
$c\oplus c'=m\oplus m'$, the key cancels. With small or structured message spaces (B/S and Y/N) this reveals both messages.
```

```card id=crypto-l2-otp-drawbacks
Practical drawbacks of the one-time pad.
---
Key as long as the message and usable once: needs lots of true randomness, secure distribution of the key material in advance, and its destruction afterwards.
```

```card id=crypto-l2-thm-2-11
Thm 2.11.
---
Every perfectly secret scheme has $|\mathcal K|\ge|\mathcal M|$.
```

```card id=crypto-l2-shannon
Thm 2.12 (Shannon), both conditions.
---
For $|\mathcal M|=|\mathcal K|=|\mathcal C|$: perfectly secret iff every key has probability $1/|\mathcal K|$ AND for every $m,c$ there is a unique $k$ with $\mathsf{Enc}_k(m)=c$.
```

## Code

`src/py/otp.py`: `keygen`, `encrypt`, `xor`, `two_time_pad_leak`, `crib_drag`,
`malleability_demo`. Tests: `test_otp.py::test_every_ciphertext_exactly_once_per_message`
(Thm 2.10 by enumeration), `test_otp.py::test_pseudo_one_time_pad_reproduces_rfc8439`
(the pad replaced by a ChaCha20 keystream reproduces RFC 8439 sec. 2.4.2 [S36]).

`src/py/classical.py`: `vernam_encrypt`, `vernam_decrypt` (the Z_26 version).
