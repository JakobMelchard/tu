# 13 — Proof toolkit and exercise playbook

*Synthesis of notes 01-12; not a lecture. The 2026W homework (9 assignments,
uploaded, graded and presented in the Thursday exercise sessions; 20 % of the
grade, and half the exercise points are needed to sit either exam, per the TISS
record of 2026-09-28; the page transcription of 2026-09-22 still said 50 %
[S1]) is about arguing security via reductions, and so is the highest-scoring
question on every past paper [S12, S13, S15, S16]. This note is the how-to. Read
[`00-exam-focus.md`](00-exam-focus.md) first for what those papers ask. Code
referenced throughout lives in [`../src/py`](../src/README.md).*

The exercises grade one skill above all: **taking a security claim and either
proving it by reduction or breaking it by constructing an adversary.** This note
is a procedure for both directions, a checklist, a catalogue of the mistakes that
lose marks, and five fully worked problems in the exact style you will present.

## How to write a reduction (the procedure)

You are proving "if primitive $P$ is secure, scheme $\Pi$ is secure." You prove
the contrapositive. Follow these six steps *in order* and write them down
explicitly — graders want to see each.

1. **Name the adversary you assume.** "Let $\mathcal A$ be a PPT adversary against
   $\Pi$ [in game $X$] with advantage $\varepsilon(\lambda)$." State the exact
   game and what "advantage" means for it.
2. **State what you will build.** "We construct $\mathcal B$, a PPT
   [distinguisher/forger/inverter] against $P$." $\mathcal B$ plays $P$'s game on
   the outside and simulates $\Pi$'s game for $\mathcal A$ on the inside.
3. **Describe $\mathcal B$'s setup.** How $\mathcal B$ turns its own challenge input
   into the public data / keys / oracle answers $\mathcal A$ expects. This is where
   you *embed* the hard instance.
4. **Answer every query.** For each oracle $\mathcal A$ may call, say exactly how
   $\mathcal B$ responds, using only what $\mathcal B$ has. **The simulation must be
   perfect** — $\mathcal A$'s view must be distributed identically to the real
   game (in at least one of $\mathcal B$'s worlds).
5. **Extract and translate.** Convert $\mathcal A$'s output (a guess, a forgery, a
   plaintext) into $\mathcal B$'s answer to *its* challenge.
6. **Do the advantage arithmetic.** Compute $\Pr[\mathcal B\text{ wins}]$ in each
   of $\mathcal B$'s worlds, subtract, and show $\mathsf{Adv}_{\mathcal B}^P \ge
   \varepsilon - (\text{negligible slack})$. Conclude: $P$ secure $\Rightarrow
   \mathsf{Adv}_{\mathcal B}^P$ negligible $\Rightarrow \varepsilon$ negligible.

**Two litmus questions** for any reduction (yours or a textbook's): *Is
$\mathcal B$ PPT?* and *Is $\mathcal A$'s simulated view perfect?* If either fails,
the proof is wrong.

**When to reach for a hybrid** (note 04): the real and ideal worlds differ in
*many* places (a primitive used $q$ times, many messages/blocks). Define
$H_0,\dots,H_q$ changing one use at a time, bound each neighbouring gap by a
single-instance reduction, sum with the triangle inequality: total $\le
q\cdot\varepsilon$, negligible for polynomial $q$. Examples: PRG stretching
(`prg.stretch`), CPA over many blocks (note 06).

## How to attack a scheme (build a distinguisher/forger)

To *disprove* security, exhibit one explicit efficient adversary with
non-negligible advantage:
1. **Pick the game** the scheme claims to satisfy (EAV/CPA/CCA/EUF-CMA).
2. **Find structure to exploit** — determinism (repeat-query), homomorphism
   (maul the challenge), a leaked bit (padding/timing oracle), reused randomness
   (two-time pad, nonce reuse).
3. **Write the adversary** as concrete steps: what it queries, what challenge
   messages it submits, how it decides its output bit.
4. **Compute the advantage** and show it is non-negligible (usually $\approx 1/2$
   for indistinguishability, $\approx 1$ for forgery).

The codebase is a catalogue of these: `prg.lcg_distinguisher`,
`private_key.padding_oracle_attack`, the ECB penguin, `mac.cbc_mac_forgery`,
`hashing.length_extension`, all of `rsa.py`'s attacks, `signatures.textbook_forgery`.

## Checklist for security games

Before trusting a definition or a proof, confirm:

- [ ] **Who holds the key?** Challenger secret; adversary gets only what the game
  hands out ($pk$ for public-key, oracles otherwise).
- [ ] **What oracles, and when?** EAV = none; CPA = encryption; CCA = enc + dec
  (dec forbidden on challenge). MAC/sig = signing oracle.
- [ ] **What is the win condition and the trivial baseline?** $1/2$ for
  indistinguishability (report *advantage*, not raw probability); $\approx 0$ for
  forgery/one-wayness.
- [ ] **What is the adversary class?** Unbounded (note 02) vs PPT (note 04+).
- [ ] **Admissibility constraints?** $|m_0|=|m_1|$; no dec-query on the challenge;
  forgery message not previously queried.
- [ ] **Is the reduction PPT and the simulation perfect?**

## Common mistakes (these lose marks)

- **Reduction in the wrong direction.** You must turn an $\mathcal A$-against-$\Pi$
  into a $\mathcal B$-against-$P$, not the reverse.
- **Assuming $\mathcal A$'s internals.** $\mathcal A$ is a black box; never
  case-split on its "strategy."
- **Imperfect simulation.** If $\mathcal B$ cannot answer a query as the real
  challenger would, $\mathcal A$'s advantage guarantee no longer applies.
- **Multiplying negligible by super-polynomial.** Hybrid counts and query counts
  must be polynomial.
- **Forgetting length/admissibility constraints**, e.g. challenge messages of
  unequal length (trivially distinguishable, so proves nothing).
- **"No known attack" as a proof.** Security is relative to a stated assumption.
- **Reporting $\Pr[\text{win}]$ instead of advantage** for indistinguishability.
- **Independent keys / fresh randomness ignored** — reusing a key across
  primitives or a nonce across messages voids the theorem.

## Five worked problems

Problems 3, 4 and 5 are close relatives of questions that have actually been
set: problem 3 is the shape of midterm 2025 question 4 [S13], problem 4 is final
2021 question 5a [S15], and problem 5 proves IND-CPA for the ElGamal scheme of
final 2023 (26.01.2024) question 5a [S12]. Problem 1 is Thm 3.16, which lecture
5 proves [S8]. Problem 2 is the one-liner behind four separate true/false items.

### Problem 1 — Reduction: PRG-based encryption is EAV-secure

*Prove: if $G$ is a secure PRG, then $\mathsf{Enc}_k(m)=G(k)\oplus m$ is EAV-secure.*

**Solution.** Let $\mathcal A$ have advantage $\varepsilon$ in
$\mathsf{PrivK}^{\mathrm{eav}}$. Build distinguisher $\mathcal B(w)$ ($w$ is $G(k)$ or
uniform $r$): run $\mathcal A$ to get $(m_0,m_1)$, $|m_0|=|m_1|$; pick
$b\gets\{0,1\}$; send $c=w\oplus m_b$; output $1$ iff $\mathcal A$'s guess $=b$.
Simulation check: $\mathcal B$ needs only $w$ and $m_b$ — PPT and faithful.
- $w=G(k)$: exactly the real game, $\Pr[\mathcal B\to1]=\tfrac12+\varepsilon$.
- $w=r$: one-time pad, $b$ perfectly hidden, $\Pr[\mathcal B\to1]=\tfrac12$.

$\mathsf{Adv}^G_{\mathcal B}=\varepsilon$; PRG security $\Rightarrow\varepsilon$
negligible. $\square$ *(This is the stream cipher, note 06; template of note 04.)*

### Problem 2 — Attack: a deterministic scheme is not CPA-secure

*Let $\Pi$ be any deterministic encryption scheme. Show it fails CPA.*

**Solution.** Adversary $\mathcal A$: query the encryption oracle on a message
$m$, receive $c_0=\mathsf{Enc}_k(m)$. Output challenge pair $(m_0,m_1)=(m, m')$ with
$m'\ne m$. Receive challenge $c=\mathsf{Enc}_k(m_b)$. Output $0$ if $c=c_0$, else $1$.
Since $\mathsf{Enc}$ is deterministic, $c=c_0 \iff m_b=m \iff b=0$, so $\mathcal A$ is
always right: $\Pr[\text{win}]=1$, advantage $1/2$ — non-negligible. Hence ECB and
textbook RSA are not CPA-secure. $\square$

### Problem 3 — Reduction: PRF gives a secure MAC

*Prove: if $F$ is a PRF, $\mathsf{Mac}_k(m)=F_k(m)$ is EUF-CMA (fixed-length $m$).*

**Solution.** Let $\mathcal A$ forge with probability $\varepsilon$ making $q$
queries. Build PRF-distinguisher $\mathcal B^{\mathcal O}$: answer each MAC query
$m_i$ with $\mathcal O(m_i)$; when $\mathcal A$ outputs $(m^*,t^*)$ with
$m^*\notin\{m_i\}$, query $\mathcal O(m^*)$ and output $1$ iff $t^*=\mathcal O(m^*)$.
- $\mathcal O=F_k$: $\mathcal B$ perfectly simulates the MAC game, so
  $\Pr[\mathcal B\to1]=\varepsilon$.
- $\mathcal O=f$ random: $f(m^*)$ is uniform and unqueried, so
  $\Pr[\mathcal B\to1]=2^{-\ell_{out}}$.

$\mathsf{Adv}^{PRF}_{\mathcal B}=\varepsilon-2^{-\ell_{out}}$, so
$\varepsilon\le\mathsf{Adv}^{PRF}_{\mathcal B}+2^{-\ell_{out}}$, negligible. $\square$
*(Note 07; code `mac.prf_mac`.)*

### Problem 4 — Attack: existential forgery on basic CBC-MAC

*Show basic CBC-MAC (zero IV, output last block) is not EUF-CMA over
variable-length messages, using two chosen-message queries.*

**Solution.** Let $b$ be the block size. $\mathcal A$ queries two one-block
messages $m_1, m_2$, getting $t_1=E_k(m_1)$ and $t_2=E_k(m_2)$. Output the forgery
$m^* = m_1\,\|\,(m_2\oplus t_1)$ with tag $t^*=t_2$. Verify: CBC-MAC on $m^*$
computes block 1 $=E_k(m_1)=t_1$; block 2 $=E_k((m_2\oplus t_1)\oplus t_1)=
E_k(m_2)=t_2=t^*$. So $(m^*,t^*)$ is valid and $m^*$ was never queried (it is two
blocks). Advantage $\approx 1$. Fix: prepend length, or CMAC. $\square$
*(Code `mac.cbc_mac_forgery`, test asserts $\mathsf{Mac}(m^*)=t^*$.)*

### Problem 5 — Reduction: ElGamal is IND-CPA under DDH

*Prove ElGamal encryption is IND-CPA assuming DDH in the prime-order group
$G=\langle g\rangle$.*

**Solution.** Let $\mathcal A$ have IND-CPA advantage $\varepsilon$. Build DDH
distinguisher $\mathcal B(g^a,g^b,T)$:
1. Set public key $h=g^a$, give $(G,g,h)$ to $\mathcal A$.
2. Get $(m_0,m_1)\in G^2$; pick $\beta\gets\{0,1\}$; return challenge
   $c=(g^b,\ m_\beta\cdot T)$.
3. Output $1$ iff $\mathcal A$'s guess $\beta'=\beta$.

Simulation is PPT and uses only the challenge components.
- $T=g^{ab}$: $c=(g^b,m_\beta h^b)$ is a real ElGamal ciphertext under $h=g^a$, so
  $\mathcal A$ sees the true game: $\Pr[\mathcal B\to1]=\tfrac12+\varepsilon$.
- $T=g^z$, $z$ uniform: $m_\beta\cdot g^z$ is uniform in $G$ and independent of
  $\beta$ (one-time pad in the group), so $\Pr[\mathcal B\to1]=\tfrac12$.

Thus $\mathsf{Adv}^{DDH}_{\mathcal B}=\varepsilon$; DDH $\Rightarrow\varepsilon$
negligible. $\square$ *(Note 10; code `elgamal.encrypt`.)*

## A template you can copy under exam pressure

> **Claim.** If $P$ is secure then $\Pi$ is secure (game $X$).
> **Proof.** Suppose PPT $\mathcal A$ has advantage $\varepsilon$ in $X$ against
> $\Pi$. Construct PPT $\mathcal B$ against $P$:
> *Setup:* $\mathcal B$ receives [$P$-challenge]; it sets [public data/keys] and
> gives them to $\mathcal A$.
> *Queries:* on each [oracle] query $\mathcal B$ replies [exact rule], perfectly
> matching $\Pi$'s challenger.
> *Output:* from $\mathcal A$'s [output] $\mathcal B$ returns [$P$-answer].
> *Analysis:* if $\mathcal B$'s challenge is [real], $\mathcal A$'s view is the real
> $X$-game, so $\Pr[\mathcal B\to1]=\tfrac12+\varepsilon$ [or $=\varepsilon$ for
> forgery]; if [ideal], the view is independent of the secret bit, so
> $\Pr[\mathcal B\to1]=\tfrac12$ [or $\le\text{negl}$]. Hence
> $\mathsf{Adv}^P_{\mathcal B}\ge\varepsilon-\mathsf{negl}$. Since $P$ is secure,
> $\varepsilon$ is negligible. $\blacksquare$

## Exam-style questions

**Q1.** A classmate "proves" $\Pi$ secure by building an adversary against $\Pi$
from an adversary against $P$. What is wrong? *A.* The direction is inverted. To
show $P$-security $\Rightarrow$ $\Pi$-security you assume a $\Pi$-breaker and build
a $P$-breaker, contradicting $P$'s security. Their construction shows nothing
about $\Pi$.

**Q2.** In a hybrid proof you have $H_0=$ real, $H_n=$ ideal, and bound each gap
by $\varepsilon$. Under what condition is $\Pi$ secure, and what breaks if
$n=2^\lambda$? *A.* Secure when $n\cdot\varepsilon$ is negligible, i.e. $n$
polynomial. If $n$ is exponential the bound $n\varepsilon$ need not be negligible,
so the argument fails even with negligible per-step $\varepsilon$.

**Q3.** Why must the challenge messages satisfy $|m_0|=|m_1|$ in the CPA game?
*A.* Length is generally leaked by the ciphertext; allowing unequal lengths makes
every scheme "insecure" by a trivial length-comparison distinguisher, so the
definition would be unsatisfiable and meaningless.

**Q4.** Give the two-question test for a reduction and apply it to Problem 5's
$\mathcal B$. *A.* (i) PPT? Yes — $\mathcal B$ does a constant number of group ops.
(ii) Perfect simulation? Yes — when $T=g^{ab}$ the ciphertext is distributed
exactly as a real ElGamal encryption. Both hold, so the advantage arithmetic is
valid.

**Q5.** You suspect a scheme is insecure. Outline the four steps to demonstrate
it and name the structural weakness each of ECB, textbook RSA, and reused-nonce
Schnorr exposes. *A.* Steps: pick the game, find exploitable structure, write the
explicit adversary, compute non-negligible advantage. Weaknesses: ECB —
determinism (repeat-block distinguisher); textbook RSA — determinism +
multiplicative homomorphism (self-forgery/malleability); reused-nonce Schnorr —
two linear equations in the secret, solved for $x$.

## Code

The attacks this note catalogues, one function each:
`src/py/prg.py`: `lcg_distinguisher`;
`src/py/private_key.py`: `padding_oracle_attack`, `block_pattern`;
`src/py/mac.py`: `cbc_mac_forgery`, `prf_mac`;
`src/py/hashing.py`: `length_extension`, `sha256_length_extension`;
`src/py/rsa.py`: `malleability_demo`, `common_modulus_attack`;
`src/py/elgamal.py`: `hybrid_cca_attack`, `encrypt`;
`src/py/signatures.py`: `textbook_forgery`, `schnorr_nonce_reuse_attack`;
`src/py/dsa.py`: `nonce_reuse_attack`.
