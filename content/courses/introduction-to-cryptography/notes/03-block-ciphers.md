# 03 — Block ciphers: DES, AES, and why key length is not enough

*Lecture 3, Andreeva — one of the two decks she gives, and her own research
area [S8, S11]. In 2026W given on 08.10.2026 at 15:00, in the exercise slot,
announced as "block and stream ciphers I" but covering block ciphers only
[S58]. Katz-Lindell sec. 7.2 [S10]. Primary source:
FIPS 197 [S21]. Code:
[`../src/py/block_ciphers.py`](../src/py/block_ciphers.py),
[`../src/py/private_key.py`](../src/py/private_key.py).*

Block ciphers are the one primitive in the course that is *engineered* rather
than *proved*. Notes 05-07 model them as pseudorandom permutations and reason
from there; this note is about what is actually inside, because the exams ask —
eight true/false items across three papers [S13, S16, S12].

A **block cipher** is a keyed permutation
$F:\{0,1\}^n\times\{0,1\}^\ell\to\{0,1\}^\ell$: for every key $k$, $F_k$ is a
bijection on $\ell$-bit blocks with an efficient inverse. AES: $\ell = 128$,
$n \in \{128,192,256\}$. DES: $\ell = 64$, $n = 56$.

The 2026W lecture frames the design space as lying between the historical
ciphers (blocks of one letter, broken) and the one-time pad (secure, but keys
as long as the data): short keys, fixed blocks, and an adversary that is
powerful but bounded [S58]. Block ciphers are the work horse underneath
encryption, MACs and key derivation [S58].

## Generic attacks fix the sizes

Assume Kerckhoffs and an adversary holding many plaintext-ciphertext pairs,
possibly for plaintexts it chose. **Generic attacks** work against anything
with the block-cipher interface, whatever is inside [S58]:

- **Exhaustive key search.** Try keys until one maps the known plaintexts to
  the known ciphertexts. Hence the key must be long: the community settled on
  128 bits, since even at $10^{18}$ keys per second, $2^{128}$ keys take about
  the age of the universe [S58].
- **Dictionary (codebook) attacks.** With short blocks, the adversary tabulates
  plaintext-ciphertext pairs, and the statistics of the data leak through
  exactly as with letter-wise substitution. Hence the block must be long too:
  at least 64 bits on the slide; AES uses 128 bits for every key size [S58].

Both sizes are then capped from above by efficiency.

## The security goal: the ideal cipher

The ideal object is a **random permutation** for each key: $2^\ell!$
permutations, one drawn per key, with no relation between different keys [S8].
A real cipher has only $2^n$ of the $2^\ell!$ permutations available, so it
cannot *be* that — it must only be *indistinguishable* from it to an efficient
adversary. That is the PRP definition of note 05. Everything in this note is a
heuristic aimed at it; there is no proof, and there cannot be one from standard
assumptions.

Two points from the 2026W lecture [S58]. The ideal cipher is **not** a one-time
pad, even though both look random: one plaintext-ciphertext pair reveals the
whole one-time-pad key, while for a random permutation one pair says almost
nothing about the others. And it is not practical: describing one permutation
of 64-bit blocks takes $\log_2\big((2^{64})!\big)\approx 2^{70}$ bits, on the
order of 150 million TB, as a key. The design goal is therefore an **efficiently
computable keyed permutation with short keys that behaves like the ideal
cipher** [S58].

## Shannon's two goals: confusion and diffusion

From [S50], quoted on the lecture-3 slide [S8]:

- **Confusion**: the relation between the key and the ciphertext is complicated.
  Delivered by a **non-linear substitution** — the S-box.
- **Diffusion**: each plaintext bit influences many ciphertext bits (and each
  ciphertext bit depends on many plaintext bits). Delivered by the **permutation
  / mixing layer**.

> **Exam trap.** *"The permutation layer of an SPN cipher provides confusion"* is
> **false** [S16]. Permutation gives diffusion; substitution gives confusion.

Diffusion is measurable. Flip one input bit and count the output bits that
change: for a good cipher it is about half, the **avalanche criterion**
(stated in the 2026W lecture as "at least half" [S58]; it is one test among
several, not a definition of security).
`block_ciphers.avalanche` measures 0.497 for AES-128 over all 128 single-bit
flips, and 0.14 for a one-round Feistel network
(`test_block_ciphers.py::test_aes_diffuses_a_single_bit_over_the_whole_block`).

## Substitution-permutation networks

One round, on an $\ell$-bit block split into $\ell/s$ chunks of $s$ bits [S8]:

1. **Key mixing**: XOR the round key into the state.
2. **Substitution**: apply an $s$-bit S-box $S$ to each chunk (confusion).
3. **Permutation**: shuffle the bits across chunk boundaries (diffusion).

Iterate $r$ times. Two requirements that are easy to get wrong:

- The S-box must be **invertible** (or the round is not), and the permutation
  must mix *between* chunks (or the cipher decomposes into $\ell/s$ independent
  small ciphers).
- One round of diffusion moves a bit to $s$ positions, two rounds to $s^2$, so
  **full diffusion** — every output bit depending on every input bit — needs
  $\lceil \log_s \ell\rceil$ rounds at minimum. Ciphers use several times that,
  as margin against differential and linear cryptanalysis.

The S-box is **public** [S16]. There is no key in it.

**How the lecture arrives there** [S58]. Shrink the ideal cipher: split a
64-bit block into eight bytes and apply a random permutation of 8 bits to each.
That is pure substitution: a one-bit input change stays inside its byte, so
nothing diffuses. Add a mixing step that spreads each byte's output bits over
the block, and repeat the pair of steps for several rounds; now a single bit
reaches the whole block. But if the random byte permutations are the key, 16
rounds of eight of them amount to a key of about 32 KB. The fix used by
essentially every modern design: one **fixed, public** S-box, with the round
key XORed into the input just before it, $y_i = S(x_i\oplus k_i)$, and round
keys derived from one short key. The S-box contributes the non-linearity
(confusion), the linear mixing layer the diffusion. Andreeva's summary:
substitute, permute, iterate [S58].

## Feistel networks

The alternative to needing an invertible round function: make the *network*
invertible instead. Split the block into halves and set

$$L_{i} = R_{i-1},\qquad R_{i} = L_{i-1}\oplus f_i(R_{i-1}).$$

Inverting is the same computation backwards: $R_{i-1} = L_i$,
$L_{i-1} = R_i \oplus f_i(L_i)$. **This works for any $f_i$ whatsoever** — the
round function need not be injective, let alone invertible. Our
`block_ciphers.ToyCipher` uses truncated SHA-256 as $f_i$ and still inverts
(`test_feistel_is_invertible_with_a_non_invertible_round_function`).

> Asked in two consecutive years [S13, S16]: *"even if the round functions are
> not invertible, the network as a whole is still invertible"* — **true**, and it
> is the entire reason the construction exists.

The 2026W lecture adds the engineering side [S58]: decryption uses the same
components as encryption with the XOR rewired and the round keys in reverse
order, which suited the hardware-oriented designs of the 1970s; and since $f$
need not be invertible, the designer can choose it for security alone.

**One round is trivially broken** [S15]. $L_1 = R_0$: the left half of the
ciphertext *is* the right half of the plaintext, in the clear. The EAV
distinguisher: submit $m_0 = 0^{\ell/2}\|0^{\ell/2}$ and
$m_1 = 0^{\ell/2}\|1^{\ell/2}$, read the left half of the challenge ciphertext,
output the matching bit. Advantage $1/2$
(`test_block_ciphers.py::test_one_round_feistel_barely_diffuses`).

**(Background — not covered in lecture [S8].)** Luby-Rackoff [S43]: with
*independent PRF* round functions, three rounds give a PRP and four a strong
PRP. The lecture presents Feistel structurally and does not state this.

## DES

Data Encryption Standard, 1977. 64-bit block, **56-bit key**, 16-round Feistel
with an S-box-and-permutation round function [S8].

**History, as told in 2026W** [S58]. The US standards bureau (NBS, now NIST)
called for a cipher for commercial use in 1972; IBM entered Lucifer, Feistel's
design; the NSA was involved and the key shrank from 128 to 56 bits; the
standard appeared in 1977 without its design criteria and was extended until
1999. Suspicions of a trapdoor in the S-boxes turned out unfounded; the public
effort to find one is a large part of why cryptanalysis became an open
science.

**The round function** $f$ [S58], on the 32-bit right half:

1. **expansion** from 32 to 48 bits (some bits are duplicated);
2. **XOR** with a 48-bit round key taken from the 56-bit key;
3. **eight S-boxes** in parallel, each a lookup table from 6 bits to 4 bits;
4. a fixed **permutation** of the 32 output bits.

The S-boxes compress 6 bits to 4, so $f$ is not invertible; inside a Feistel
network it does not need to be [S58].

- *"DES has longer keys than AES"* — **false** [S12]. 56 against 128.
- **Differential cryptanalysis** (Biham & Shamir, 1990) traces how input
  differences propagate. Against DES it needs $2^{47}$ chosen plaintexts, so it
  shows a theoretical weakness rather than a practical break [S58]. DES turned
  out to be *already hardened* against it: the 2026W slide states that IBM and
  the NSA knew the technique in the 1970s, and the lecturer adds "most likely"
  [S58]. (Earlier versions of this note marked that history as unsourced.)
- **Linear cryptanalysis** (Matsui, 1993) is a known-plaintext attack; against
  DES it needs $2^{43}$ plaintext-ciphertext pairs [S58].
- **Brute force** remains the best attack in practice [S58]: in 1997 a search
  over thousands of computers took 69 days; in 1999 the dedicated machine Deep
  Crack took 22 hours; today it takes minutes with precomputation.

This is the historical point the lecture makes: the design survived the
cryptanalysis, the **key length** did not. Andreeva's advice is not to use DES,
because of the key and not because of the design; more rounds would not help,
the key is the problem [S58].

## 2DES, and the meet-in-the-middle attack

The obvious repair — encrypt twice under independent keys —
$E'_{(k_1,k_2)}(x) = E_{k_2}(E_{k_1}(x))$, gives $2n$ key bits and **not** $2n$
bits of security.

$$E_{k_2}(E_{k_1}(p)) = c \iff E_{k_1}(p) = D_{k_2}(c).$$

Given one known pair $(p,c)$: tabulate $E_{k_1}(p)$ for all $2^n$ keys $k_1$,
then for each $k_2$ compute $D_{k_2}(c)$ and look it up. **$2\cdot 2^n$ cipher
evaluations and $2^n$ memory**, against $2^{2n}$ for brute force — roughly the
square root [S13].

The table has $2^n$ entries in a space of $2^\ell$ blocks, so a single pair
leaves about $2^{2n-\ell}$ false positives; a second known pair filters them.
`block_ciphers.meet_in_the_middle` does exactly this and
`test_meet_in_the_middle_beats_brute_force_on_double_encryption` checks the work
count: with 10-bit keys, 2 048 evaluations against $2^{20}$.

So 2DES buys **one bit** of security over DES (plus the memory cost), and was
never standardised.

## 3DES

$E\!-\!D\!-\!E$: $c = E_{k_3}(D_{k_2}(E_{k_1}(p)))$ [S8]. The middle decryption
is not a security measure — it makes $k_1=k_2=k_3$ collapse to plain DES, which
is how 3DES stayed backwards compatible
(`test_block_ciphers.py::test_triple_ede_degenerates_to_single_encryption`).

Meet-in-the-middle still applies across the first two stages, so:

| variant | key bits | security |
|---|---|---|
| two-key 3DES (2TDEA, $k_3 = k_1$) | 112 | NIST: **80** [S27] |
| three-key 3DES (3TDEA) | 168 | **112** [S27] |

The lecture slide states this as "Keys: 112 bits, Security: 112 (NIST: 80)"
[S8], unchanged in 2026W [S58]. The 2026W slide writes Triple DES in its
two-key form, $y = \mathsf{DES}_{k_1}\big(\mathsf{DES}^{-1}_{k_2}(\mathsf{DES}_{k_1}(x))\big)$,
and the lecture gives the reasons [S58]: a third independent key would not
help, since meet-in-the-middle already brings even three keys down to about
$2^{112}$; and with $k_1 = k_2$ the first two stages cancel, so the scheme
falls back to single DES for legacy systems. Triple DES survives in banking
and card payments; new encryption with it is no longer allowed, decryption of
old data is [S58]. SP 800-57 Part 1 Rev. 5 deprecates 3TDEA and disallows 2TDEA for applying
protection [S27]. And the 64-bit block is its own problem: the PRP/PRF switching
lemma (note 05) stops being useful at $2^{32}$ blocks, about 32 GB under one key.

## DES against AES

The 2026W comparison slide, in short [S58]:

| | DES | AES |
|---|---|---|
| structure | Feistel, iterated | SPN, iterated |
| block | 64 bits | 128 bits |
| key | 56 bits | 128, 192 or 256 bits |
| S-boxes | eight different ones | one |
| optimised for | hardware | byte-oriented software |
| design process | criteria kept secret | open NIST competition, standard 2001 |

The slide also calls DES's round function non-invertible and AES's invertible;
Andreeva corrected this in the lecture: the DES *round* is invertible (it is a
Feistel round), only the function $f$ inside it, with its 6-to-4-bit S-boxes,
is not [S58].

## AES (Rijndael)

Rijndael was selected in 2000 and standardised as FIPS 197 in 2001 [S21].
Its designers are Rijmen and Daemen; the lecture uses the 128-bit key
throughout [S58].
**Not** a Feistel network: an SPN [S13]. 128-bit block;
key 128/192/256 bits; 10/12/14 rounds.

State: a $4\times 4$ array of bytes, column-major. Each round:

1. **SubBytes** — the S-box, applied bytewise.
2. **ShiftRows** — row $r$ rotated left by $r$: $s'_{r,c} = s_{r,(c+r)\bmod 4}$.
3. **MixColumns** — each column multiplied by a fixed matrix over
   $\mathrm{GF}(2^8)$ [S8, S21]:
   $$\begin{pmatrix}2&3&1&1\\1&2&3&1\\1&1&2&3\\3&1&1&2\end{pmatrix}$$
4. **AddRoundKey** — XOR the round key from the key schedule.

The final round omits MixColumns.

In the 2026W lecture [S58]: a round key is also added once before the first
round; SubBytes supplies the confusion, ShiftRows and MixColumns the
diffusion; every step is invertible. The MixColumns matrix is an **MDS**
matrix, chosen for good diffusion (measured by the *branch number*) and
efficient inversion. The **key schedule** was skipped on purpose ("think of it
as magic"): it reuses S-boxes and linear steps, and Andreeva called it the
least understood part of AES, in the sense that nobody knows how much of its
complexity is needed. Andreeva also said the round steps are to be
understood, not memorised [S58].

### The S-box, derived rather than copied

$\mathrm{GF}(2^8) = \mathbb F_2[x]/(m(x))$ with
$m(x) = x^8+x^4+x^3+x+1$ (`0x11b`) [S21 sec. 4.1]. Then for a byte $a$:

$$\mathrm{SBOX}(a) = \mathrm{Affine}\big(a^{-1}\big),\qquad a^{-1} := a^{254}
\text{ (and } 0^{-1} := 0),$$

with the affine map over $\mathbb F_2$ [S21 eq. 5.2]

$$b'_i = b_i \oplus b_{(i+4)\bmod 8}\oplus b_{(i+5)\bmod 8}\oplus
b_{(i+6)\bmod 8}\oplus b_{(i+7)\bmod 8}\oplus c_i,\qquad c = \texttt{0x63}.$$

The inverse is what gives confusion (it is maximally non-linear over
$\mathbb F_2$ in the relevant sense); the affine map destroys the clean algebraic
description that the inverse alone would have, and removes the fixed points
$0\mapsto 0$, $1\mapsto 1$.

`block_ciphers.aes_sbox` computes all 256 entries from this definition, and
`test_block_ciphers.py::test_sbox_matches_fips197_table_4` checks every one of
them against FIPS 197 Table 4 [S21]. The standard's own worked example
$S(\{53\}) = \{ed\}$ is a separate test, as is $\{57\}\cdot\{83\} = \{c1\}$ from
sec. 4.2.

As used in practice, the S-box is a $16\times16$ table: the high four bits of
the input byte select the row, the low four bits the column; the lecture's
example reads $S(\{42\}) = \{2c\}$ off row 4, column 2 [S58, S21]. Software
uses the table lookup; modern x86 processors also have dedicated AES
instructions (AES-NI) [S58]. Why a non-linear step at all: a cipher made only
of linear and affine maps is a linear system in the key and falls to linear
algebra; the S-box is the only non-linear part of AES [S58].

### Known attacks

Both far from practical, both worth quoting [S8]:

- 2009, **related-key** attack on AES-256, complexity $2^{99.5}$. Related-key
  attacks assume the adversary sees encryptions under keys related in a chosen
  way — not a model any sane protocol permits.
- 2011, **biclique** (a meet-in-the-middle descendant) recovers an AES-128 key in
  $2^{126.2}$ AES calls: a factor $2^{1.8}\approx 3.5$ faster than brute
  force, i.e. no practical difference whatsoever.

AES has no better single-key attack after 25 years of attention. Modelling it as
a strong PRP is a heuristic, but a very well-tested one.

**Security margin** [S58]. Designers add rounds beyond what known attacks
reach. For AES-128, attacks on reduced versions reach about five or six of the
ten rounds, leaving roughly four rounds of margin; diffusion alone is already
good after about four rounds, but differential attacks also exploit the
S-box, so diffusion is not enough by itself.

**The closing warning** [S58]: a block cipher is not an encryption scheme. It
maps one fixed-size block, deterministically; encrypting real data needs a
**mode of operation** on top, and a bad mode undoes everything the cipher
achieves (note 06).

## Worked example

*Show that a two-round Feistel network is distinguishable from a random
permutation with two chosen-plaintext queries.*

Write the input as $(L_0,R_0)$. After two rounds,

$$L_2 = L_0 \oplus f_1(R_0),\qquad R_2 = R_0 \oplus f_2\big(L_0\oplus f_1(R_0)\big).$$

Query $(L_0,R_0)$ and $(L_0',R_0)$ with $L_0 \ne L_0'$ — *same right half*. Then

$$L_2 \oplus L_2' = \big(L_0\oplus f_1(R_0)\big)\oplus\big(L_0'\oplus f_1(R_0)\big)
= L_0 \oplus L_0',$$

because $f_1$ is evaluated at the same point both times and cancels. So the
distinguisher outputs "Feistel" iff the left halves of the two ciphertexts XOR to
the known value $L_0\oplus L_0'$. For a random permutation that happens with
probability about $2^{-\ell/2}$. Advantage $\approx 1-2^{-\ell/2}$. (Three rounds break the
cancellation, which is where Luby-Rackoff starts.) $\square$

## Pitfalls

- **Confusion is substitution, diffusion is permutation.** Asked, and easy to
  swap [S16].
- **The S-box is public.** Kerckhoffs. It is in the standard [S21].
- **Feistel inverts regardless of $f$.** The round function does not have to be
  invertible — asked twice [S13, S16].
- **Doubling the key does not double the security.** Meet-in-the-middle costs
  $2\cdot 2^n$ time and $2^n$ memory [S13].
- **A 64-bit block is a liability independent of the key.** Birthday collisions
  at $2^{32}$ blocks (note 05).
- **AES is not a Feistel cipher** [S15]. It is an SPN [S13].
- **A block cipher is not an encryption scheme.** It encrypts one block,
  deterministically. Turning it into a scheme is note 06's modes.

## Exam-style questions

**Q1** *(F24 1c [S16]).* Does the permutation layer of an SPN provide confusion?
— **No, diffusion.** Confusion is the S-box's job: it makes the key-ciphertext
relation non-linear. The permutation spreads a local change across the block.

**Q2** *(F24 1f [S16]).* Must the S-box of an SPN be kept secret? — **No.**
Kerckhoffs' principle: only the key is secret. AES's S-box is Table 4 of FIPS
197, and `block_ciphers.aes_sbox` rebuilds it from the published formula;
`aes.PureAES` then builds the whole cipher on it and reproduces FIPS 197
appendix B.

**Q3** *(M25 1f [S13]).* State the meet-in-the-middle attack on
$E'_{(k,k')} = E_{k'}\circ E_k$ and its cost. — From a known pair $(p,c)$, build
a table of $E_k(p)$ over all $2^n$ values of $k$, then for each $k'$ test whether
$D_{k'}(c)$ is in the table. Time $2\cdot 2^n$, memory $2^n$, against $2^{2n}$
for brute force — the square root. False positives (about $2^{2n-\ell}$ of them)
are eliminated with a second known pair.

**Q4** *(M25 1e / F24 1j [S13, S16]).* A Feistel round function is a hash
truncated to half a block, so it is not injective. Is the cipher still
invertible? — **Yes.** Decryption computes $R_{i-1} = L_i$ and
$L_{i-1} = R_i\oplus f_i(L_i)$; $f_i$ is only ever *evaluated*, never inverted.
Invertibility of the network is structural.

**Q5** *(F20 1a [S15]).* A developer proposes running one round of DES for
speed. Give an adversary showing this is not EAV-secure. — $\mathcal A$ outputs
$m_0 = 0^{32}\|0^{32}$ and $m_1 = 0^{32}\|1^{32}$. One Feistel round gives
$L_1 = R_0$, so the left half of the challenge ciphertext equals the right half
of $m_b$: output $0$ if it is $0^{32}$, else $1$. Correct with probability 1,
advantage $1/2$, and it never touches the key or the round function. (Real DES
wraps the rounds in a public initial permutation and its inverse; the adversary
undoes them first, Kerckhoffs again.)

## Cards

```card id=crypto-l3-generic-attacks
Two generic attacks on any block cipher, and the size requirement each forces.
---
Exhaustive key search: keys of at least 128 bits. Dictionary (codebook) attacks and statistics: blocks of at least 64 bits (AES: 128).
```

```card id=crypto-l3-ideal-cipher
What is the ideal cipher, and why is it not used?
---
Each key selects an independent uniformly random permutation of $\{0,1\}^\ell$. Describing one such permutation of 64-bit blocks takes about $2^{70}$ bits of key.
```

```card id=crypto-l3-ideal-vs-otp
Why is the ideal cipher not just a one-time pad?
---
One plaintext-ciphertext pair reveals the whole one-time-pad key ($k=m\oplus c$); for a random permutation one pair says almost nothing about the others.
```

```card id=crypto-l3-confusion-diffusion
Confusion and diffusion: meaning and which layer gives which.
---
Confusion: the plaintext/key-ciphertext relation is obscured, from the non-linear S-boxes. Diffusion: each output bit depends on many input bits, from the permutation/mixing layer.
```

```card id=crypto-l3-avalanche
Avalanche criterion.
---
Flipping one input bit should change about half (at least half, per the lecture) of the output bits.
```

```card id=crypto-l3-spn-key
In an SPN, why a fixed public S-box with the key XORed in, rather than secret random S-boxes?
---
Random S-boxes as the key are far too large (about 32 KB for 16 rounds of eight 8-bit boxes). $y_i=S(x_i\oplus k_i)$ keeps confusion with short round keys from one master key.
```

```card id=crypto-l3-feistel
Feistel round and its inverse.
---
$L_i=R_{i-1}$, $R_i=L_{i-1}\oplus f_{k_i}(R_{i-1})$. Inverse: $R_{i-1}=L_i$, $L_{i-1}=R_i\oplus f_{k_i}(L_i)$. $f$ need not be invertible.
```

```card id=crypto-l3-des-params
DES: block, key, rounds, structure.
---
64-bit block, 56-bit key (IBM's Lucifer had 128), 16 Feistel rounds, 1977.
```

```card id=crypto-l3-des-round
The DES round function $f$, in four steps.
---
Expand 32 to 48 bits; XOR the 48-bit round key; eight S-boxes 6 to 4 bits; permute the 32 bits. Not invertible, which Feistel allows.
```

```card id=crypto-l3-des-attacks
Differential vs linear cryptanalysis of DES, and the best practical attack.
---
Differential (Biham-Shamir 1990): $2^{47}$ chosen plaintexts. Linear (Matsui 1993): $2^{43}$ known pairs. Best in practice: exhaustive key search (1999 Deep Crack: 22 hours).
```

```card id=crypto-l3-mitm
Double encryption with two 56-bit keys: cost of meet-in-the-middle?
---
Tabulate $E_{k_1}(x)$ for all $k_1$, compare with $E^{-1}_{k_2}(y)$: $2^{56}$ memory and $2^{57}$ evaluations, not $2^{112}$.
```

```card id=crypto-l3-3des
Two-key Triple DES: formula, security, why DES$^{-1}$ in the middle?
---
$\mathsf{DES}_{k_1}(\mathsf{DES}^{-1}_{k_2}(\mathsf{DES}_{k_1}(x)))$, 112 key bits, 112-bit security (NIST: 80). With $k_1=k_2$ it collapses to single DES (backward compatibility).
```

```card id=crypto-l3-aes-round
AES: key sizes, rounds, round steps and their roles.
---
128/192/256-bit keys, 10/12/14 rounds, 128-bit block. SubBytes (confusion), ShiftRows and MixColumns (diffusion), AddRoundKey; a key is also added before round 1.
```

```card id=crypto-l3-aes-sbox
How is the AES S-box defined, and how is it looked up?
---
Inverse in $\mathrm{GF}(2^8)=\mathbb F_2[X]/(X^8+X^4+X^3+X+1)$, then an affine map. Table lookup: high nibble = row, low nibble = column, e.g. $S(\{42\})=\{2c\}$.
```

```card id=crypto-l3-not-encryption
Is a block cipher an encryption scheme?
---
No. It is a deterministic permutation of one block; encryption needs a mode of operation on top, and a bad mode breaks everything.
```

## Code

`src/py/block_ciphers.py`: `xtime`, `gmul`, `ginv`, `aes_sbox`, `aes_inv_sbox`,
`avalanche`, `ToyCipher`, `double_encrypt`, `triple_encrypt_ede`, `brute_force`,
`meet_in_the_middle`.

`src/py/aes.py`: `key_expansion`, `encrypt_block`, `decrypt_block`, `PureAES`,
the whole of FIPS 197 [S21] on top of the derived S-box. Tests:
`test_aes.py::test_key_expansion_fips197_appendix_a`,
`test_aes.py::test_cipher_example_fips197_appendix_b` (including the state at
the start of round 10), `test_aes.py::test_sp800_38a_ecb_all_key_sizes`, and
`test_block_ciphers.py::test_sbox_matches_fips197_table_4`.
