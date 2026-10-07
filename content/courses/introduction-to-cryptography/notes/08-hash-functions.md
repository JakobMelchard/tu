# 08 — Hash functions

*Lecture 9, Andreeva — her second deck, and her own research area [S8, S11].
Katz-Lindell sec. 6 and 7.3 [S10] — Thm 6.4, sec. 6.2
Merkle-Damgard, sec. 6.3 hash-and-MAC, sec. 6.6.2 Merkle trees. SHA is
FIPS 180-4 [S28] with test vectors in RFC 6234 [S23]. Code:
[`../src/py/hashing.py`](../src/py/hashing.py).*

A cryptographic hash $H:\{0,1\}^*\to\{0,1\}^n$ compresses arbitrary input to a
fixed digest. Unlike a PRF it is **unkeyed** (or has a public key/salt), and its
security is stated as *hardness of finding structured input pairs*. Hashes are
the workhorses of signatures (note 11), MACs (note 07), commitments, and
password storage.

## Security notions

For a hash $H$ (with public salt $s$ when keyed), in increasing difficulty of the
attacker's task:

1. **Collision resistance:** hard to find $x\ne x'$ with $H(x)=H(x')$.
2. **Second-preimage resistance:** given $x$, hard to find $x'\ne x$ with $H(x')=H(x)$.
3. **Preimage resistance (one-wayness):** given $y=H(x)$, hard to find any $x'$ with $H(x')=y$.

**Implications:** collision resistance $\Rightarrow$ second-preimage resistance
$\Rightarrow$ (for most parameters) preimage resistance. The converses fail. Game
for collision resistance:
$$\mathsf{Hash\text{-}coll}_{\mathcal A,H}(\lambda):\ s\gets\mathsf{Gen}(1^\lambda);\ (x,x')\gets\mathcal A(s);\ \text{output }1\text{ iff }x\ne x' \wedge H^s(x)=H^s(x').$$
(The salt/key avoids the trivial "hard-wire a fixed collision" objection to
unkeyed collision resistance.)

## The birthday bound

Collisions always exist (an infinite domain maps to $2^n$ digests), and any
$2^n+1$ inputs are guaranteed to contain one (pigeonhole), but they appear far
sooner *probabilistically*. Among $q$ random $n$-bit digests, the
probability of a collision is
$$\approx 1 - e^{-q(q-1)/2^{n+1}} \approx \frac{q^2}{2^{n+1}}\ (\text{small } q),$$
crossing $1/2$ at $q\approx 1.177\cdot 2^{n/2}$. So a generic collision costs
$\Theta(2^{n/2})$ work, not $2^n$: **an $n$-bit hash gives only $n/2$-bit
collision resistance.** This is why SHA-256 (128-bit collision resistance) is the
baseline and why the PRP/PRF switching bound scales as $q^2/2^{n+1}$ (note 05).

Code: `hashing.birthday_attack(bits)` finds a collision on truncated SHA-256 in
$\approx 2^{bits/2}$ tries via a seen-digests table
(`test_hashing.py::test_birthday_attack_finds_collision_cheaply`; the 32-bit
`__main__` demo collides in tens of thousands of tries, $\approx 2^{16}$).
Preimage search would be $\approx 2^{bits}$ — the gap is the whole point.

## Merkle-Damgard: hashing arbitrary lengths

Given a **compression function** $h:\{0,1\}^{n}\times\{0,1\}^{b}\to\{0,1\}^{n}$
(fixed input size), extend to arbitrary input:
1. Pad the message and append its length (**length-strengthening**): $m\to
   m\|10\cdots0\|\langle|m|\rangle$.
2. Chain: $z_0 = \mathrm{IV}$; $z_i = h(z_{i-1}, m_i)$; output $z_t$.

Code: `hashing.compress` (toy, SHA-truncated), `hashing._pad`, `hashing.merkle_damgard`.

**Theorem 6.4 (MD collision resistance) [S8, S10].** If $h$ is collision
resistant, so is the length-strengthened Merkle-Damgard hash $H$. *(True/false on
the 2024W final [S16]; the padding rule that appends the message length is
FIPS 180-4 sec. 5.1 [S28].)*
*Proof idea.* Suppose $H(m)=H(m')$ with $m\ne m'$. Walk the two chains
*backwards* from the equal final states. Either (a) the messages have different
lengths — then the last block differs (it encodes the length), giving an
immediate $h$-collision on the final call; or (b) equal lengths — compare
chaining pairs $(z_{i-1},m_i)$ vs $(z'_{i-1},m'_i)$ from the end; since $m\ne m'$
some pair differs while the outputs $z_i=z'_i$ agree, yielding an $h$-collision.
Either way a collision in $H$ is efficiently turned into one in $h$. $\square$
This is a textbook reduction — a great model for note 13's homework style.

## Length-extension: the Merkle-Damgard defect

MD hashes leak their internal state: the digest $H(m)$ *is* the chaining value
after absorbing $m\|\mathrm{pad}$. So given $H(m)$ and $|m|$ (but **not** $m$), an
attacker computes
$$H(m\|\mathrm{pad}(m)\|m') \text{ for any } m',$$
by resuming the chain from $H(m)$. Code: `hashing.length_extension` reconstructs
the glue padding and continues hashing; it matches the honestly computed digest
(`test_hashing.py::test_toy_length_extension_forges_valid_digest`). The same
attack on the real thing: `hashing.sha256` is SHA-256 written from FIPS 180-4
[S28] with a resumable state, and `hashing.sha256_length_extension` turns a
published SHA-256(k || m) into a valid digest of an extended message without
k, checked against `hashlib`
(`test_hashing.py::test_sha256_length_extension_forges_a_secret_prefix_mac`).

Consequences: **the naive MAC $H(k\|m)$ is forgeable** — from a tag on $m$, forge
one on $m\|\mathrm{pad}\|m'$ (note 07, motivating HMAC). SHA-256/512 have this
defect; SHA-3 (sponge) and HMAC do not.

## Where the compression function comes from: Davies-Meyer

Merkle-Damgard needs a collision-resistant compression function
$h:\{0,1\}^{n+b}\to\{0,1\}^n$; lecture 9 builds one from a **block cipher**
$E:\{0,1\}^{b}\times\{0,1\}^n\to\{0,1\}^n$ [S8]:

$$h(z_{i-1},\,m_i) = E_{m_i}(z_{i-1}) \oplus z_{i-1}.$$

Note what is the key: the **message block** keys the cipher and the chaining
value is the plaintext. That inversion is deliberate. The feed-forward XOR is
what stops the construction being invertible — without it, knowing $m_i$ and the
output lets you run $E^{-1}$ and walk the chain backwards. Davies-Meyer is
provably collision resistant in the ideal-cipher model, and it is what SHA-1 and
the SHA-2 family actually are inside: SHA-256's compression function is the block
cipher SHACAL-2 in Davies-Meyer mode, with the feed-forward done by wordwise
addition mod $2^{32}$ instead of XOR.

Our `hashing.compress` is a truncated-SHA-256 stand-in rather than Davies-Meyer;
it exists to make the Merkle-Damgard chaining and the length-extension attack
visible at toy sizes, not to be a construction.

## Hash functions in practice

The timeline lecture 9 gives [S8], worth knowing because the exam asks about
output lengths:

| | year | digest | status |
|---|---|---|---|
| MD5 | 1991 | 128 bits | **broken** — collisions in seconds; 64-bit birthday bound anyway |
| SHA-1 | 1995 | 160 bits | **broken** — first public collision 2017; 80-bit birthday bound |
| SHA-2 (SHA-256/512) | 2001 | 224-512 bits | fine; Merkle-Damgard, so length-extendable [S28] |
| SHA-3 (Keccak) | 2012 | 224-512 bits | fine; sponge, not length-extendable |

SHA-3 came out of a NIST competition announced in 2007 after the SHA-1 breaks,
with Keccak selected in 2012 — deliberately a *different* construction, so that
one structural break could not take out both families. (The competition dates
and the winner are on the lecture-9 slide [S8]; the individual collision papers
were not fetched, so treat the years as the lecture gives them.)

A hash with an 80-bit output cannot be recommended whatever its design, because
the birthday bound caps it at $2^{40}$ — that is question 3b of the 2021 final
[S15].

## Sponge construction (SHA-3)

An alternative to MD that avoids length extension. State of $r+c$ bits (rate $r$,
capacity $c$); a fixed permutation $f$. **Absorb:** XOR each $r$-bit message block
into the rate part, apply $f$. **Squeeze:** read out $r$ bits at a time, applying
$f$ between reads. The capacity $c$ is never output directly, so the final state
is not the digest — length extension fails. Security $\approx 2^{c/2}$. Keccak/
SHA-3 uses this; so do the XOFs SHAKE128/256. (Idea only.)

## The random oracle model (ROM) *(background — lecture 13a lists ROM proofs
under "what we did not cover" [S8])*

An idealisation [S45]: treat $H$ as a truly random function that all parties
(including the reduction) access only by *querying* an oracle. This gives the proof two
superpowers: it **sees every query** the adversary makes, and it can **program**
the oracle's answers (choose outputs adaptively, as long as they look random).

The ROM enables proofs for efficient schemes with no standard-model proof:
RSA-FDH signatures (note 11), OAEP (note 10), Fiat-Shamir (note 11). **Caveat:**
a ROM proof is a heuristic. Canetti, Goldreich and Halevi exhibited schemes that
are provably secure in the ROM and insecure under **every** concrete
instantiation of the hash [S45], so the model is not merely unproven — it is
known to be unsound in general. Read "secure in the ROM" as "no
structural attack that ignores $H$'s internals," which in practice is strong
evidence but not a theorem about the instantiated scheme.

## Applications

- **Commitments:** $\mathrm{commit}(m;r)=H(m\|r)$ — binding (collision resistance)
  and hiding (if $r$ is high-entropy).
- **Password storage:** store $H(\mathrm{salt}\|\mathrm{pwd})$ with a *slow, salted*
  hash (bcrypt/scrypt/Argon2); the salt defeats precomputed rainbow tables, the
  slowness defeats brute force.
- **Merkle trees:** hash pairs up a tree; the root commits to all leaves and any
  leaf is proved by $O(\log n)$ sibling hashes. Used in Git, certificate
  transparency, blockchains.
- **Key derivation / fingerprints / deduplication.**

## Worked example

*Given a collision-resistant $h:\{0,1\}^{2n}\to\{0,1\}^n$, show $H(x_1\|x_2\|x_3\|x_4)
=h(h(x_1\|x_2)\|h(x_3\|x_4))$ (a Merkle tree of depth 2 on $4n$-bit input) is
collision resistant.* A collision $X\ne X'$ with $H(X)=H(X')$ means
$h(a\|b)=h(a'\|b')$ where $a=h(x_1\|x_2)$ etc. If $(a,b)\ne(a',b')$ that is a
top-level $h$-collision. Else $a=a', b=b'$; since $X\ne X'$ they differ in some
half, say $x_1\|x_2\ne x_1'\|x_2'$, yet $h(x_1\|x_2)=a=a'=h(x_1'\|x_2')$ — a
bottom-level $h$-collision. Either way we extract an $h$-collision efficiently.
$\square$

## Pitfalls

- **Digest size $\to$ half for collisions.** Want 128-bit collision security $\Rightarrow$
  256-bit hash.
- **Unsalted fast hash for passwords is broken** (rainbow tables, GPU brute
  force). Salt + slow KDF.
- **$H(k\|m)$ is not a MAC** with MD hashes (length extension). Use HMAC or SHA-3.
- **Collision resistance $\ne$ PRF/random.** A collision-resistant hash need not
  hide its input or look random; don't use a bare hash where a PRF/KDF is meant.
- **Truncation changes security:** truncating SHA-256 to $t$ bits gives $t/2$-bit
  collision resistance — sometimes intended (SHA-512/256), often a footgun.

## Exam-style questions

**Q1** *(F24 1h [S16] — "a hash function with output length $\ell$ can
theoretically achieve up to $\ell$ bits of collision resistance", **false**).*
Why does an $n$-bit hash give only $2^{n/2}$ collision resistance but
$2^n$ preimage resistance? *A.* A collision needs *some* pair among $q$ digests to
match — birthday paradox, $\Theta(2^{n/2})$. A preimage must hit *one specific*
target $y$; each try succeeds with probability $2^{-n}$, so $\Theta(2^n)$ tries.

**Q2** *(F24 1a [S16]).* State and sketch the Merkle-Damgard theorem (K&L
Thm 6.4). *A.* If $h$ is collision
resistant then the length-strengthened MD hash is collision resistant. Sketch: an
$H$-collision yields, by walking chains backward, either a final-block collision
(different lengths) or an intermediate $(z_{i-1},m_i)$-collision (same length) —
in both cases a collision of $h$.

**Q3.** You are given $H(k\|m)$ (SHA-256) and $|k\|m|$. Forge a valid tag on a
longer message under the "MAC" $H(k\|\cdot)$. *A.* Length extension: with the known
digest as the resumed chaining value, append $\mathrm{pad}\|m'$ and continue the
SHA-256 compression to obtain $H(k\|m\|\mathrm{pad}\|m')$ — a valid tag on a
message never queried. (`hashing.length_extension`.)

**Q4.** Why does the sponge resist length extension while Merkle-Damgard does
not? *A.* The sponge's output omits the $c$-bit capacity, so the digest is not the
full internal state; an attacker cannot resume the permutation without the hidden
capacity bits. MD's digest *is* its final state.

**Q5** *(F20 3b [S15]: "an engineer proposes a new hash $H:\{0,1\}^*\to\{0,1\}^{80}$
and claims to have proved its collision resistance. Why would you not use it?").*
— Because the claim cannot be true in the sense that matters. Whatever the
design, the generic birthday attack finds a collision in $\approx 2^{40}$
evaluations, about $10^{12}$: hours on a laptop with a memoryless
(Pollard-rho style) collision search, far less on a GPU. An 80-bit digest caps collision
resistance at 40 bits before anyone looks at the internals, so "I proved it
collision resistant" means the proof is relative to an assumption that is false,
or the word is being used loosely. (`hashing.birthday_attack` demonstrates the
same arithmetic at 32 bits.)

**Q6.** Give one concrete benefit and one caveat of a random-oracle proof. *A.*
Benefit: it lets us prove very efficient schemes (RSA-FDH, OAEP, Fiat-Shamir)
secure, by letting the reduction observe and program hash queries. Caveat: the
ROM is idealised — separation results show schemes secure in the ROM yet
insecure under every concrete hash — so it is heuristic evidence, not a
standard-model theorem.

## Code

`src/py/hashing.py`: `compress`, `merkle_damgard`, `length_extension`,
`sha256_compress`, `sha256`, `sha256_length_extension`, `birthday_attack`, and
the constants `SHA256_K`, `SHA256_H0` derived from their FIPS 180-4
definition [S28]. Tests:
`test_hashing.py::test_constants_derived_from_their_definition_match_fips180_4`,
`test_standard_vectors.py::test_rfc6234_sha256_vectors` [S23],
`test_hashing.py::test_sha256_length_extension_forges_a_secret_prefix_mac`.
