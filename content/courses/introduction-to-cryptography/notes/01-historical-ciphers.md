# 01 — Historical ciphers and why they all fall

*Lecture 1, 01.10.2026 [S8, S58]. Katz-Lindell sec. 1.1-1.4 [S10]. Code:
[`../src/py/classical.py`](../src/py/classical.py).*

The first lecture is a graveyard. Five schemes, each the state of the art for
centuries, each broken in a paragraph. The point is not the ciphers; it is the
diagnosis: every one of them was designed to *look* unbreakable, and none of
them was ever stated precisely enough to be *proved* anything. From lecture 2
on, the course never again calls a scheme secure without a definition and a
proof [S8].

The midterm's true/false section opens with two items on this lecture [S13].

## The course map (2026W lecture 1)

Before the ciphers, the 2026W lecture lays out the course [S58]:

- **Four quadrants.** Private-key versus public-key, crossed with secrecy
  versus integrity: private-key encryption and MACs on top, public-key
  encryption and digital signatures below. Block ciphers are the tool for the
  private-key half, number theory for the public-key half, and hash functions
  turn up in both.
- **Goal.** Understand the schemes actually deployed, with the rigour of
  provable security: which primitives exist and exactly which guarantee each
  gives, so a protocol designer can pick the weakest notion that suffices.
  The exercises are small schemes to attack or to prove secure, not
  implementation work.
- **Why proofs.** Security means that *no* efficient adversary exists, a
  statement about the absence of an algorithm. The only handle on such
  statements is complexity theory's: a reduction showing that breaking the
  scheme would solve a problem believed hard, such as factoring. Lecture 2
  develops this (note 02).

## The syntax, fixed once

A **private-key encryption scheme** is $(\mathsf{Gen},\mathsf{Enc},\mathsf{Dec})$
over a message space $\mathcal M$ and key space $\mathcal K$ (K&L Def. 1.2
[S8, S10]; the 2026W slide cites K&L sec. 1.2 without a definition number
[S58]):

- $k \gets \mathsf{Gen}$ samples a key (possibly randomised);
- $c \gets \mathsf{Enc}_k(m)$ (possibly randomised);
- $m := \mathsf{Dec}_k(c)$, deterministic, with
  $\mathsf{Dec}_k(\mathsf{Enc}_k(m)) = m$ for all $k,m$ — **correctness**.

Every scheme in the course is written in this shape, and the first exam trap is
about it: *"key generation is randomised, but encryption and decryption must be
deterministic so that ciphertexts decrypt uniquely"* is **false** [S13]. Only
$\mathsf{Dec}$ must be deterministic. Randomised $\mathsf{Enc}$ is not optional
later — it is forced (note 06).

The 2026W lecture gives a reason for each algorithm's kind [S58]:

- $\mathsf{Gen}$ **must** be randomised: a deterministic $\mathsf{Gen}$ hands
  every user of the published scheme the same key.
- $\mathsf{Enc}$ **should** be randomised: the setting is one shared key used
  for many messages, and the goal is that a ciphertext reveals nothing about
  its message. With deterministic $\mathsf{Enc}$, sending the same message
  twice gives the same ciphertext twice, so the adversary learns that the two
  messages are equal without learning either.
- $\mathsf{Dec}$ is deterministic: exactly one output is correct.

The pattern, used for every primitive in the course: first the **syntax**, then
**correctness** (the scheme does its job), then **security** [S58].

## Kerckhoffs' principle (1883)

> $\mathsf{Enc}$ and $\mathsf{Dec}$ are **public**; only the key is secret [S8].

Three reasons, all still valid: a key is easier to replace than an algorithm;
$n$ users sharing a public algorithm and private keys is cheaper than $n$ secret
algorithms; and a public algorithm gets attacked by everyone, which is the only
review that counts. "Security through obscurity" is the negation.

The 2026W lecture adds two cases and a moral [S58]. Two secret designs were
reverse engineered once deployed and then broken by academics: the GSM stream
cipher A5/1, and the Mifare Classic cipher (Crypto-1) of the Dutch contactless
transit cards, where the fix came after mass deployment. Public algorithms, by
contrast, can be standardised through open competitions in which rival teams
attack each other's proposals for years; NIST ran AES, SHA-3 and the
post-quantum standards that way. The lecturer's "first lesson": **use
standardised schemes, never one of your own**.

Two exam items are just this principle in disguise: *must the S-box of an SPN be
kept secret?* **No** [S16], and the AES S-box is printed in FIPS 197 Table 4
[S21] — [`../src/py/block_ciphers.py`](../src/py/block_ciphers.py) even
reconstructs it from the published formula.

## Scytale — transposition

Sparta, ~7th century BC. Wrap a strip of leather round a rod of circumference
$k$, write across, unwrap [S8]. The key is $k$.

$$\mathsf{Enc}_k(m_1\cdots m_n) = (m_1, m_{n/k+1}, m_{2n/k+1},\dots,\ m_2, \dots)$$

A **transposition**: the letters are permuted, not replaced. Code:
`classical.scytale_encrypt` / `scytale_decrypt`.

**Break.** Two ways, and the first is fatal on its own:

1. The *multiset of letters is unchanged*, so the ciphertext's letter frequency
   profile is the plaintext's. A single glance distinguishes a transposition
   from a substitution.
2. The key space is the set of divisors of $n$ — at most $n$ candidates. Try
   them all (`classical.scytale_break`).

## Shift / Caesar — the smallest key space there is

$\Sigma = \{A,\dots,Z\} = \mathbb Z_{26}$, key $k \in \mathbb Z_{26}$,
$\mathsf{Enc}_k(m_i) = m_i + k \bmod 26$ [S8]. Caesar is the special case
$k = 3$, which is not even keyed.

**Break 1 — exhaustive search.** $|\mathcal K| = 26$. Twenty-six trial
decryptions and a human eye. `classical.shift_brute_force`.

**Break 2 — frequency analysis, no human needed.** Let $f_i$ be the frequency of
letter $i$ in English and $p_j$ the frequency in the ciphertext. Choose

$$k^* = \arg\max_k \sum_{i=0}^{25} f_i\, p_{i+k}$$

— the shift that best aligns the two distributions.
`classical.shift_break_by_frequency` recovers the key from a few hundred
characters, for every $k$, with no candidate list to inspect.

> **Sufficient key space principle.** A key space small enough to enumerate is
> fatal. It is **necessary and nowhere near sufficient** — see the next scheme.

ROT13 is the shift by 13; since $13 \equiv -13 \pmod{26}$ it is its own
inverse, so encryption and decryption coincide [S58].

The scale the 2026W lecture puts on "small enough to enumerate" [S58]:

| key length | example | exhaustive search |
|---|---|---|
| 48 bits | Mifare Crypto-1 | feasible on a phone |
| 56 bits | DES | feasible on a laptop, given time |
| 128 or 256 bits | AES | out of reach; $2^{256}$ is roughly the number of atoms in the universe |

A large key space only rules out this one generic attack; it says nothing else
about security.

## Monoalphabetic substitution — a huge key space, still broken

Key: a permutation $\pi$ of $\Sigma$; $\mathsf{Enc}_\pi(m_i) = \pi(m_i)$ [S8].
$|\mathcal K| = 26! \approx 2^{88}$ — comfortably beyond brute force, and still
broken by a bored teenager. (Not by a wide margin any more: the lecture notes
that the hash computations done for Bitcoin so far are estimated at about that
order [S58].)

**Break.** $\pi$ relabels the alphabet but does not change *how often* each label
occurs. So the **sorted** frequency profile of the ciphertext equals that of the
plaintext, exactly:

```
sorted(frequency_profile(ct)) == sorted(frequency_profile(plaintext))
```

(`test_classical.py::test_substitution_leaks_its_frequency_profile`). Rank the
ciphertext letters by frequency, align them with the English ranking
(E 12.7 %, T 9.1 %, A 8.2 %, O 7.5 %, …), and you have a first guess at $\pi$;
digram and trigram statistics (TH, HE, IN; THE, AND) finish it. On our 2 200
character sample the unigram ranking alone pins a handful of letters outright
and puts the true image of E in the top three
(`test_classical.py::test_substitution_frequency_attack_beats_chance`).

The lesson, and it is the reason lecture 1 exists: **a cipher is broken when it
leaks a statistic, no matter how large its key space.**

## Polyalphabetic substitution and Vigenère

Key: a tuple $(\pi_1,\dots,\pi_\ell)$; position $i$ is encrypted under
$\pi_{i \bmod \ell}$ [S8]. **Vigenère** (dated 1553 on the 2026W slide [S58])
is the case where each $\pi_j$ is a *shift*, so the key is a word of length
$\ell$, written repeatedly under the message and added letter by letter.

This does defeat *naive* frequency analysis: each plaintext letter can map to
$\ell$ different ciphertext letters and the overall profile flattens.

**Break 1 — analyse per residue class.** Split the ciphertext into $\ell$
interleaved subsequences $c_j, c_{j+\ell}, c_{j+2\ell},\dots$. Each one is a
plain shift cipher, so break each with the same correlation attack as above.
`test_classical.py::test_vigenere_defeats_naive_frequency_analysis` recovers the
key `CRYPTO` this way, one letter at a time. (Recovering $\ell$ itself, when it
is unknown, is Kasiski's method or the index of coincidence — not covered.)

So the midterm item *"unlike monoalphabetic ciphers, polyalphabetic ciphers are
immune to frequency analysis"* is **false** [S13]. They are immune to the wrong
frequency analysis.

**Break 2: chosen plaintext.** If the adversary can have a message of its choice
encrypted, the key can be read off the ciphertext directly, with no statistics
at all.

## Vernam — the one that survives

Gilbert Vernam, 1917. Key = a uniform string **as long as the message**;
$c_i = m_i + k_i \bmod 26$ [S8]. Over $\{0,1\}$ with XOR this is the one-time
pad of note 02.

**This one is not broken.** It is perfectly secret, for the same reason as the
binary one-time pad; note 02 defines perfect secrecy, proves it for the one-time
pad and states the price.

The intuition from the 2026W lecture [S58]: Vernam differs from Vigenère in
exactly two ways, a **uniformly random** key instead of a word, and **as long
as the message** instead of repeated. Given a ciphertext, every plaintext of the
same length is explained by exactly one key, obtained by subtracting the
plaintext from the ciphertext; the lecture shows the same ciphertext opening to
two different English words under two different keys. Since all keys are
equally likely, the ciphertext favours no plaintext.

**What it does not hide: the length.** The ciphertext is as long as the
message. The lecture adds that no scheme can hide the length of arbitrarily long
messages, since the ciphertext has to carry the message's information [S58].

`classical.vernam_encrypt`, and
`test_classical.py::test_vernam_ciphertext_is_uniform_for_a_fixed_message`.

**One time.** Reuse the key and the same cancellation as the binary one-time pad
happens over $\mathbb Z_{26}$: $c_1 - c_2 = m_1 - m_2$, no key involved
(`test_classical.py::test_vernam_needs_a_fresh_key`).

## Pitfalls

- **Transposition versus substitution.** Check the letter frequencies first: if
  they match plain English, the letters were moved, not replaced.
- **Big key space ≠ secure.** $26! \approx 2^{88}$ and it falls to a frequency
  table. A key space too large to enumerate is necessary, not sufficient.
- **"Immune to frequency analysis" is always wrong.** It means "immune to the
  obvious frequency analysis". Split by position, by digram, by anything.
- **Chosen plaintext is a real model.** Break 2 above already assumes the
  adversary can get one message of its choice encrypted, long before the CPA
  game is defined.
- **The key must be uniform and fresh** for Vernam. Neither a passphrase nor a
  reused pad is a one-time pad.

## Exam-style questions

**Q1** *(M25 1a, verbatim in substance [S13]).* In an encryption scheme, key
generation is randomised, but encryption and decryption must be deterministic so
ciphertexts can be uniquely decrypted. True or false? — **False.** Only
$\mathsf{Dec}$ must be deterministic (and it must be, or correctness is not
well defined). $\mathsf{Enc}$ is randomised in every CPA-secure scheme; a
deterministic $\mathsf{Enc}$ loses the CPA game in one query (note 06).

**Q2** *(M25 1b [S13]).* Unlike monoalphabetic substitution ciphers, are
polyalphabetic ones immune to frequency analysis? — **False.** Split the
ciphertext into the $\ell$ residue classes mod the period; each is a
monoalphabetic cipher and falls to the same attack.

**Q3** *(ours.)* Give an
adversary that tells Scytale encryption from a monoalphabetic substitution
cipher, given one long ciphertext of English plaintext. How often does it
err? A comparison of **sorted** frequency profiles does not work: both
schemes preserve the profile as a multiset. Compare the frequency vector
**letter by letter** instead: Scytale preserves it pointwise (the ciphertext
still has E as its most frequent letter, then T, then A), substitution
permutes it. Output "Scytale" iff the ciphertext's top letters are E, T, A.
The test errs only if the random $\pi$ fixes E, T and A, probability
$1/(26\cdot 25\cdot 24) \approx 6\cdot 10^{-5}$ (plus the sampling noise of
a short text), so the advantage is close to 1 but not exactly 1.

**Q4** *(ours, modelled on the "sufficient key space" slide [S8]).* A colleague
proposes a monoalphabetic substitution over an alphabet of 256 bytes, arguing
that $256! \approx 2^{1684}$ keys make brute force hopeless. What do you say? —
That brute force was never the threat. The cipher is a fixed relabelling, so it
preserves the byte-frequency distribution pointwise, and any file format with
structure (ASCII text, a bitmap header, base64) is recovered from unigram and
digram statistics. Key-space size is necessary and not remotely sufficient; the
scheme has no security definition and no proof, which is the actual objection.

## Cards

```card id=crypto-l1-syntax
Syntax of a private-key encryption scheme, and which algorithms may be randomised?
---
$(\mathsf{Gen},\mathsf{Enc},\mathsf{Dec})$ with $\mathsf{Dec}_k(\mathsf{Enc}_k(m))=m$ (correctness). Gen and Enc may be randomised; only Dec must be deterministic.
```

```card id=crypto-l1-enc-deterministic
True or false: encryption must be deterministic so ciphertexts decrypt uniquely.
---
False. Only Dec must be deterministic. CPA-secure schemes need randomised Enc.
```

```card id=crypto-l1-kerckhoffs
Kerckhoffs' principle, and why?
---
Enc and Dec are public, only the key is secret. Keys are easier to replace than algorithms, one public algorithm serves everyone, and public algorithms get reviewed by everyone.
```

```card id=crypto-l1-scytale
Scytale: what kind of cipher, what is the key, how is it broken?
---
Transposition: letters are moved, not replaced. Key = number of columns (rod circumference), at most $n$ candidates: try them all. Letter frequencies stay exactly English.
```

```card id=crypto-l1-transposition-vs-substitution
Ciphertext letter frequencies match English letter by letter. Transposition or substitution?
---
Transposition. A substitution relabels letters, so the profile is permuted (only its sorted version matches).
```

```card id=crypto-l1-shift
Shift cipher: key space and two attacks.
---
$k\in\mathbb Z_{26}$, $c_i=m_i+k \bmod 26$ (Caesar: $k=3$). Brute force over 26 keys, or frequency analysis: pick $k$ maximising $\sum_i f_i\,p_{i+k}$.
```

```card id=crypto-l1-substitution
Monoalphabetic substitution: key space size, and why is it still broken?
---
$26!\approx 2^{88}$ permutations. It preserves letter frequencies (only relabelled): match ciphertext ranks to E, T, A, O, ..., then digrams TH, HE, IN.
```

```card id=crypto-l1-key-space
Sufficient key space principle: necessary or sufficient?
---
Necessary, not sufficient. Enumerable key space is fatal, but a huge one (substitution, $2^{88}$) still falls if the cipher leaks a statistic.
```

```card id=crypto-l1-vigenere
Vigenère: definition, and how to break it with known period $\ell$.
---
Polyalphabetic: position $i$ shifted by key letter $i \bmod \ell$. Split the ciphertext into $\ell$ residue classes; each is a shift cipher, break each by frequency analysis.
```

```card id=crypto-l1-period
How to find the Vigenère period $\ell$ when unknown?
---
Kasiski (distances between repeated ciphertext fragments share $\ell$ as a factor) or the index of coincidence. Not covered in detail in the lecture.
```

```card id=crypto-l1-poly-immune
True or false: unlike monoalphabetic ciphers, polyalphabetic ciphers are immune to frequency analysis.
---
False. Each residue class mod the period is monoalphabetic and falls to frequency analysis.
```

```card id=crypto-l1-chosen-plaintext
Why is a polyalphabetic cipher weak against a chosen-plaintext attacker?
---
One chosen message encrypted reveals the key directly from the ciphertext, no statistics needed.
```

```card id=crypto-l1-vernam
Vernam cipher: key requirements and security.
---
Key uniform, as long as the message, used once; $c_i=m_i+k_i$ (mod 26, or XOR). Perfectly secret (one-time pad, lecture 2).
```

```card id=crypto-l1-key-reuse
Why does reusing a Vernam key break it?
---
$c_1-c_2=m_1-m_2$: the key cancels, leaving the difference of two plaintexts, which statistics recover.
```

```card id=crypto-l1-enc-randomised
Why should Enc be randomised (2026W lecture 1)?
---
One key is used for many messages. Deterministic Enc maps equal messages to equal ciphertexts, so the adversary learns that two messages are equal: information the ciphertext must not leak.
```

```card id=crypto-l1-gen-randomised
Why must Gen be randomised?
---
The scheme is public (Kerckhoffs). A deterministic Gen gives every user the same key.
```

```card id=crypto-l1-secret-designs
Two deployed secret ciphers that were reverse engineered and broken, and the lesson.
---
GSM's A5/1 and Mifare's Crypto-1 (transit cards). Use standardised, publicly analysed schemes; never your own.
```

```card id=crypto-l1-key-scale
Exhaustive key search: 48, 56, 128/256-bit keys?
---
48 bits (Mifare Crypto-1): a phone. 56 bits (DES): a laptop. 128 or 256 bits (AES): out of reach.
```

```card id=crypto-l1-rot13
Why is ROT13 its own inverse?
---
It shifts by 13 and $13 \equiv -13 \pmod{26}$, so encrypting twice shifts by 26, the identity.
```

```card id=crypto-l1-length
Does the one-time pad hide the message length?
---
No: the ciphertext is as long as the message. No scheme can hide the length of arbitrarily long messages.
```

```card id=crypto-l1-lesson
Lecture 1's lesson in one line.
---
A cipher is broken when it leaks a statistic, whatever its key space; so from lecture 2 on: definitions and proofs, not designs that look hard.
```

## Code

`src/py/classical.py`: `scytale_encrypt`, `scytale_decrypt`, `scytale_break`,
`shift_encrypt`, `shift_brute_force`, `shift_break_by_frequency`,
`random_substitution`, `substitution_encrypt`, `substitution_break_by_frequency`,
`frequency_profile`, `poly_encrypt`, `vigenere_key_to_perms`,
`vernam_keygen`,
`vernam_encrypt`, `vernam_decrypt`. No standard exists for these; the tests
check textbook known answers (`test_classical.py::test_known_answers`: Caesar
HELLO to KHOOR, Vigenere with LEMON, the Scytale formula above) and the attacks.
