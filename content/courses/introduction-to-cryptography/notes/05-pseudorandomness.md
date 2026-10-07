# 05 — Pseudorandomness

*Lecture 5 [S8]. Katz-Lindell sec. 3.3.1-3.3.3 [S10] — Def. 3.14, Thm 3.16.
PRFs and PRPs are lecture 6 (sec. 3.5.1), kept here because the three objects
belong together. Code: [`../src/py/prg.py`](../src/py/prg.py). The *internals*
of real block ciphers are note 03.*

Pseudorandomness is the engine of private-key cryptography: it manufactures
"effectively random" bits from a short seed, which is exactly what lets us beat
the Shannon bound. Three objects, in increasing power: PRG (a string), PRF (a
function), PRP (a permutation). Each is defined by an indistinguishability game
against its truly-random ideal.

## Pseudorandom generators (PRG)

A deterministic poly-time $G:\{0,1\}^n\to\{0,1\}^{\ell(n)}$ with **expansion**
$\ell(n) > n$ is a **PRG** if its output on a uniform seed is computationally
indistinguishable from a uniform $\ell(n)$-bit string:
$$\{G(s): s\gets\{0,1\}^n\} \approx_c \{r : r\gets\{0,1\}^{\ell(n)}\}.$$
Game: challenger flips $b$; sends $G(s)$ if $b=0$, uniform $r$ if $b=1$; PPT $D$
guesses $b$; advantage must be negligible.

Intuition: no efficient test detects that $G$'s output lives on a tiny
($2^n$-element) subset of $\{0,1\}^{\ell(n)}$, even though information-
theoretically it obviously does.

**Bad PRG — the LCG.** $x_{i+1}=ax_i+c \bmod m$ is a fine simulation RNG but a
useless PRG: the output *is* the state, so three outputs determine $a,c$ and
predict the fourth (`prg.lcg_distinguisher`, advantage $\approx 1$). *Statistical
randomness $\ne$ cryptographic pseudorandomness.* By contrast a byte-mean test
has $\approx 0$ advantage against the hash-based generator
(`prg.prg_distinguisher_test`) — passing statistical tests is necessary, not
sufficient.

**Increasing expansion (stretching).** From a PRG $G_1$ with 1-bit expansion one
builds a PRG of any polynomial output length by iterating: set $s_0 = s$; write
$G_1(s_{i-1}) = (s_i, b_i)$ (new seed, one output bit); output $b_1\cdots b_\ell$.
*Proof by hybrid* (note 04): hybrid $H_j$ uses true randomness for the first $j$
bits and $G_1$ thereafter; $H_{j-1}\approx_c H_j$ by one invocation of $G_1$'s
security; $\ell$ hybrids give advantage $\le \ell\cdot\varepsilon$. Code:
`prg.stretch`. *(Background: the construction and its proof are Katz-Lindell
sec. 8, which lecture 13a puts under "cryptography from minimal assumptions —
what we did not cover" [S8]. Lecture 5 defines PRGs and proves Thm 3.16, the
pseudo-one-time pad, and leaves existence alone: "Do PRGs exist? We don't know
— a PRG implies P \ne NP" [S8].)*

## Pseudorandom functions (PRF)

A keyed function $F:\{0,1\}^n\times\{0,1\}^{\ell_{in}}\to\{0,1\}^{\ell_{out}}$ is a
**PRF** if oracle access to $F_k$ (uniform $k$) is indistinguishable from oracle
access to a truly random function $f\gets\mathsf{Func}_{\ell_{in},\ell_{out}}$:
$$\big|\Pr[D^{F_k(\cdot)}(1^n)=1] - \Pr[D^{f(\cdot)}(1^n)=1]\big| \le \mathsf{negl}(n).$$
The adversary now *queries* the object adaptively; the ideal is the set of all
$2^{\ell_{out}\cdot 2^{\ell_{in}}}$ functions, of which a random one is chosen. A
PRF is an exponentially-large object accessed through a short key.

Toy PRF used throughout the code: $F_k(x) = \mathrm{SHA256}(k\|x)$
(`prg.toy_prf`) — *assumed* to be a PRF for teaching (real MACs use HMAC or a
block cipher; naive $\mathrm{H}(k\|x)$ has the length-extension issue of note 08).

### PRF $\Rightarrow$ PRG

A PRF immediately yields a PRG: $G(s) = F_s(0)\|F_s(1)\|\cdots\|F_s(t{-}1)$ for
distinct inputs $0,\dots,t-1$. If the output looked non-random, the underlying
distinguisher would query $F_s$ on exactly those inputs and break the PRF. Code:
`prg.prf_to_prg` (`test_prg.py` checks lengths and the prefix property). This is
the easy direction; the converse (PRG $\Rightarrow$ PRF) is the GGM construction.

### GGM: PRG $\Rightarrow$ PRF *(background — not covered [S8])*

Goldreich-Goldwasser-Micali build a PRF from a length-doubling PRG
$G(s)=(G_0(s),G_1(s))$. View the input $x=x_1\cdots x_\ell$ as a path down a
binary tree of depth $\ell$: start at the seed, at level $i$ go left/right by
applying $G_{x_i}$; the leaf is $F_k(x)$.
$$F_k(x_1\cdots x_\ell) = G_{x_\ell}(\cdots G_{x_2}(G_{x_1}(k))\cdots).$$
Only the $\ell$ nodes on the path are ever computed, so evaluation is efficient
despite the $2^\ell$-leaf tree. Security is a hybrid over the $\ell$ levels, each
step replacing one PRG call by true randomness [S44]. Idea only, and not on the
syllabus — it is Katz-Lindell sec. 8 [S8, S10].

## Pseudorandom permutations (PRP) and block ciphers

A **PRP** is a PRF that is, for each key, a bijection on $\{0,1\}^n$ (with an
efficient inverse). Indistinguishable from a random *permutation*. A **strong
PRP** stays indistinguishable even when the adversary also queries the inverse
$F_k^{-1}$ — the right model for a block cipher, since modes (note 06) sometimes
decrypt.

PRP vs PRF are close: a random permutation and a random function differ only via
collisions, so by the birthday bound (note 08) any distinguisher making $q$
queries has advantage $\le q^2/2^{n+1}$ (the **PRP/PRF switching lemma**).
Negligible until $q\approx 2^{n/2}$.

**Block ciphers** ($\mathsf{AES}$, $\mathsf{3DES}$) are the practical instantiation:
fixed input/output length $n$ (128 for AES), keyed, invertible. We *model* them
as strong PRPs; this is a heuristic assumption, not a theorem — lecture 3 calls
the ideal object the "ideal cipher" and spends the hour on how close real designs
get [S8]. **Their internals are note 03**; this note only needs the interface.

### Feistel networks (summary — note 03 has the lecture)

How do you build an invertible permutation from a non-invertible round function?
The **Feistel** trick: split the block into $(L,R)$ and set
$$L' = R,\qquad R' = L \oplus f_i(R).$$
Invertible regardless of $f_i$: $L = R' \oplus f_i(L')$, $R = L'$. Stack rounds.
**Luby-Rackoff:** if the round functions are independent PRFs, 3 rounds give a
PRP and 4 rounds a *strong* PRP. Code: `private_key.FeistelPRP` (4 rounds,
8-byte block, SHA-based round function); `test_private_key.py` checks it is a
bijection with no observed collisions. DES is a 16-round Feistel cipher.

**AES** is *not* Feistel — it is a substitution-permutation network (SubBytes,
ShiftRows, MixColumns, AddRoundKey over $\mathrm{GF}(2^8)$) [S21]. We use it
through the `cryptography` package (`private_key.AESBlock`) as a real strong-PRP
cross-check for the modes; `block_ciphers.py` rebuilds its S-box from the FIPS
197 definition (note 03).

## Worked example

*Show that $G(s) = F_s(0)\|F_s(1)$ is a PRG when $F$ is a PRF (output length
$= 2\ell_{out}$, expansion holds if $2\ell_{out} > n$).* Let $D$ distinguish
$G(s)$ from random with advantage $\varepsilon$. Build a PRF-distinguisher
$\mathcal B^{\mathcal O}$: query the oracle at $0$ and $1$, form
$w = \mathcal O(0)\|\mathcal O(1)$, run $D(w)$, echo its bit. If $\mathcal O=F_s$
then $w=G(s)$; if $\mathcal O=f$ (random function) then $\mathcal O(0),\mathcal O(1)$
are independent uniform, so $w$ is uniform. Hence $\mathsf{Adv}^{PRF}_{\mathcal B}
= \varepsilon$, negligible by PRF security. $\square$

## Pitfalls

- **PRG output is public randomness once revealed.** Never reuse a PRG output as
  if it were a fresh key.
- **PRF input reuse leaks.** In modes, repeating a PRF input (nonce/counter)
  collides keystream blocks — the CTR/OFB failure of note 06.
- **PRP $\ne$ PRF at scale.** Beyond $\approx 2^{n/2}$ queries the switching
  lemma bound is no longer negligible; this is why 64-bit block ciphers (3DES)
  are deprecated.
- **Statistical tests are necessary, not sufficient** (the LCG passes many yet
  is trivially predictable).
- **A PRF is not a hash.** It is keyed and its security is secrecy of the key,
  not collision resistance (note 08).

## Exam-style questions

**Q1.** Prove no PRG can be perfectly indistinguishable from uniform. *A.* The
image of $G$ has $\le 2^n$ points out of $2^{\ell}>2^n$, so an *unbounded*
distinguisher outputs $1$ iff its input is in the image of $G$ (deciding
membership needs a search over all $2^n$ seeds, which is fine for an unbounded
distinguisher and is exactly what an efficient one cannot do): it says "PRG" with prob $1$ on
$G(s)$ and $\le 2^n/2^\ell = 2^{n-\ell}$ on uniform. Advantage $\ge 1-2^{n-\ell}$,
non-negligible. PRGs only fool *efficient* tests.

**Q2.** Given a PRF $F$, is $G(s)=F_s(0)\|F_s(0)$ a PRG? *A.* No: the two halves
are equal, a property true of uniform strings only with probability $2^{-\ell_{out}}$.
A distinguisher checking "first half = second half" has advantage $\approx 1$.
Distinct inputs are essential.

**Q3** *(background for note 03's 64-bit-block discussion).* State the PRP/PRF
switching lemma and its consequence for block size.
*A.* A $q$-query distinguisher between a random permutation and a random function
on $n$ bits has advantage $\le q^2/2^{n+1}$. So a PRP is usable as a PRF until
$q\approx 2^{n/2}$; with $n=64$ that is $\approx 2^{32}$ blocks ($\sim$32 GB),
uncomfortably small — hence AES's $n=128$.

**Q4.** Why do we need 4 (not 3) Feistel rounds for a *strong* PRP? *A.* Three
rounds give a PRP against chosen-plaintext queries, but a chosen-*ciphertext*
(inverse) query can distinguish a 3-round network from a random permutation; the
fourth round closes this, giving indistinguishability even with inverse access
(Luby-Rackoff).

**Q5.** Explain why the GGM tree can be evaluated efficiently despite having
$2^\ell$ leaves. *A.* Evaluating $F_k(x)$ walks a single root-to-leaf path,
applying the PRG $\ell$ times; the tree has $2^{\ell+1}-1$ nodes, the path
$\ell+1$, and the other $2^{\ell+1}-\ell-2$ are never computed.
Cost is $O(\ell)$ PRG calls.

## Code

`src/py/prg.py`: `LCG`, `lcg_distinguisher`, `prg_distinguisher_test`,
`toy_prf`, `prf_to_prg`, `prg_one_bit`, `stretch`, `chacha20_block` (a PRF in
the counter, RFC 8439 sec. 2.3 [S36]).

`src/py/private_key.py`: `FeistelPRP`, `AESBlock`. `src/py/aes.py`: `PureAES`.
Tests: `test_prg.py::test_chacha20_block_rfc8439_2_3_2`,
`test_private_key.py::test_feistel_is_a_permutation`.
