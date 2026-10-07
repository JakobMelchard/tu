# 01: Provable security and the random-oracle model

*TISS heading 1 [S2]. Boneh-Shoup sec. 4.2 (difference lemma), 8.10 (ROM),
11.4 (ETDF), 13.3-13.4 (FDH), 19.2 (Schnorr) [S4]; Bellare-Rogaway [S8];
Canetti-Goldreich-Halevi [S28]; forking lemma [S26, S27]. Prerequisite:
intro notes [04](../../introduction-to-cryptography/notes/04-computational-security.md)
(games, reductions, hybrids) and
[13](../../introduction-to-cryptography/notes/13-proof-toolkit.md)
(proof playbook). Code: [`../src/py/rom_reductions.py`](../src/py/rom_reductions.py).*

The prerequisite taught the asymptotic reduction ("PPT $\mathcal A$ with
non-negligible advantage gives PPT $\mathcal B$ ..."). This course works with
**concrete bounds** and **idealised hash functions**, and the questions become
quantitative: how much security is lost, and what the ROM really buys.

## Concrete security

A primitive is **$(t,\varepsilon)$-secure** if every adversary running in time
$\le t$ has advantage $\le\varepsilon$. A reduction theorem has the form

$$\forall \mathcal A\ (t, q, \varepsilon)\ \ \exists \mathcal B\ (t', \varepsilon'):\quad
\varepsilon \le L\cdot\varepsilon' + \delta,\qquad t' \le c\,t + \mathrm{poly}(q).$$

$L$ is the **tightness loss**, $\delta$ an additive statistical term (usually a
collision probability like $q^2/|\mathcal X|$). A reduction is **tight** if
$L = O(1)$ and $t' \approx t$. The loss matters because parameters are chosen
from the *assumption*: to guarantee $\varepsilon \le 2^{-128}$ with
$L = 2^{60}$, the underlying problem must resist with $\varepsilon' \le
2^{-188}$.

## Game hopping and the difference lemma

**Lemma (difference lemma) [S4 Thm 4.7].** If $W_0\wedge\bar Z
\Leftrightarrow W_1\wedge\bar Z$ then $|\Pr[W_0]-\Pr[W_1]|\le\Pr[Z]$.

*Proof.* $\Pr[W_0]-\Pr[W_1] = \Pr[W_0\wedge Z]-\Pr[W_1\wedge Z]$ because the
$\bar Z$ parts cancel, and both remaining terms lie in $[0,\Pr[Z]]$. $\square$

Use: Game $i+1$ equals Game $i$ unless a **bad event** $Z$ happens
(e.g. "$\mathcal A$ queried the hash at $r^*$"); then bound $\Pr[Z]$ by a
reduction or by counting. A proof is a chain
$G_0\to G_1\to\dots\to G_k$ with $G_k$ trivially unwinnable.

## The random-oracle model

**Definition.** A scheme is analysed in the ROM if the hash $H:\mathcal X\to
\mathcal Y$ is replaced by a uniformly random function
$\mathcal O\gets\mathrm{Funs}[\mathcal X,\mathcal Y]$ to which **every party,
including $\mathcal A$, has oracle access only** [S4 sec. 8.10.2], [S8].

Implementation (lazy sampling): keep a table; on a new query sample a fresh
uniform value, on a repeated query return the stored one. Identical
distribution to a random function, and it is what the reduction runs.

Three properties a reduction exploits:

1. **Uniformity/independence.** $H(x)$ is uniform and independent of
   everything unless $x$ was queried. Hence $H(r^*)$ acts as a one-time pad
   until someone asks for it.
2. **Observability (extractability).** The reduction sees every query of
   $\mathcal A$ (`RandomOracle.log`).
3. **Programmability.** The reduction may *choose* $H(x)$ for fresh $x$, as long
   as the chosen value is uniformly distributed (`RandomOracle.program`,
   which fails on an already-defined point: that is the bad event).

**Bellare-Rogaway paradigm [S8].** Design protocol $P^{\mathcal O}$, prove it
secure in the ROM, then replace $\mathcal O$ by a concrete hash $h$. Gains:
schemes as efficient as the ad-hoc ones used in practice (FDH, OAEP,
Fiat-Shamir, $E(m)=f(r)\,\|\,G(r)\oplus m$) with a proof of *something*.

**ROM vs standard model.** A standard-model proof assumes only properties of
a concrete (keyed) function family. The ROM is a heuristic: there exist
schemes secure in the ROM but insecure for **every** instantiation of the
oracle by an efficiently computable function family [S28]. The counterexamples
are contrived (the scheme misbehaves exactly when it can recognise its own hash
function), and no natural ROM-proven scheme has been broken this way; but a
ROM proof rules out only attacks that treat $H$ as a black box. Intermediate
idealisations such as the algebraic group model [S42] (co-authored by the
lecturer, **background**) restrict the adversary instead of the hash.

## Worked reduction: $E(m) = (f(r),\,G(r)\oplus m)$ is IND-CPA in the ROM

Setting [S8 sec. 3], [S4 sec. 11.4]: $f$ a trapdoor permutation on
$\mathcal X$, $G:\mathcal X\to\{0,1\}^\ell$ a random oracle,
$\mathsf{Enc}_{pk}(m)$: $r\gets\mathcal X$, output $(y,c)=(f(r), G(r)\oplus m)$.
Decryption: $r=f^{-1}(y)$, $m = c\oplus G(r)$.

**Theorem.** For every IND-CPA adversary $\mathcal A$ making $q_G$ queries to
$G$ there is an inverter $\mathcal B$ with
$$\mathsf{Adv}^{\mathrm{cpa}}_{E}(\mathcal A)
:= \big|\Pr[b'=b]-\tfrac12\big| \le \mathsf{Adv}^{\mathrm{ow}}_f(\mathcal B),
\qquad t_{\mathcal B}\le t_{\mathcal A}+q_G\,t_f .$$

*Proof.* Games over the same probability space.

- **$G_0$**: the real CPA game. $\mathcal A$ gets $pk$, outputs $m_0,m_1$,
  gets $(y^*,c^*) = (f(r^*),\,G(r^*)\oplus m_b)$, outputs $b'$. Let $W_0$
  be "$b'=b$".
- **$G_1$**: identical, except that $c^* = \kappa\oplus m_b$ for an
  independent uniform $\kappa$, and $G$ answers queries at $r^*$ with fresh
  uniform values unrelated to $\kappa$. Let $Z$ = "$\mathcal A$ queries $G$ at
  $r^*$". Until $Z$ happens the two games are identical (in $G_0$, $G(r^*)$ is
  uniform and seen only through $c^*$), so $|\Pr[W_0]-\Pr[W_1]|\le\Pr[Z]$ by
  the difference lemma.
- In $G_1$, $c^*$ is a one-time pad encryption and $y^*$ is independent of
  $b$: $\Pr[W_1]=\tfrac12$.
- **$\mathcal B$** gets $(pk, y^*)$, runs $\mathcal A$ with $G$ lazily sampled,
  answers the challenge with $(y^*, \kappa)$ for random $\kappa$ (this is $G_1$
  from $\mathcal A$'s view), and at the end scans the query log for $x$ with
  $f(x)=y^*$ (`ow_inverter_from_log`). It succeeds exactly when $Z$ happens:
  $\Pr[Z]=\mathsf{Adv}^{\mathrm{ow}}_f(\mathcal B)$.

Hence $|\Pr[W_0]-\tfrac12|\le\Pr[Z]=\mathsf{Adv}^{\mathrm{ow}}_f(\mathcal B)$.
$\square$ The reduction is **tight** ($L=1$); only observability was used. In
Boneh-Shoup's convention the same scheme gets
$\mathrm{SS}\le 2\,\mathrm{OW}+\mathrm{SS}_{E_s}$ [S4 Thm 11.2]: factor 2 from
the advantage definition, $\mathrm{SS}_{E_s}$ from a general symmetric cipher
instead of the one-time pad.

## Programming: FDH and the guessing loss

RSA-FDH, $\sigma = H(m)^d$, is EUF-CMA in the ROM with
$\mathsf{Adv}^{\mathrm{sig}}\le(Q_{ro}+1)\,\mathsf{Adv}^{\mathrm{ow}}$
[S4 Thm 13.3]. Proof idea in the prerequisite (intro note
[11](../../introduction-to-cryptography/notes/11-digital-signatures.md)):
program $H(m_i)=r_i^e$ so signing queries are answerable, and plant the
challenge $y$ at **one guessed** query index. The factor $Q_{ro}+1$ is the
price of the guess. [S4 sec. 13.5] gives a variant with a tight proof.

## Schnorr signatures: programming plus rewinding

Signing oracle without the key: pick $(c,s)$, set $t=g^sy^{-c}$, program
$H(y,t,m):=c$ (`simulated_sign`). Fails only if $(y,t,m)$ was queried before;
$t$ is uniform in $\mathbb G$, so over all signing queries this costs
$Q_s(Q_s+Q_{ro}+1)/q$ [S4 eq. (19.5)]. A forgery then yields, by rewinding,
two transcripts with the same $t$ and different challenges, and special
soundness (note 03) gives $x$.

**General forking lemma [S27 Lemma 1].** Let $\mathcal A(x,h_1..h_q;\rho)$
output $(J,\sigma)$, $J\in\{0..q\}$, accept probability
$\mathrm{acc}=\Pr[J\ge1]$ over $h_i\gets H$, $|H|=h$. The forking algorithm
reruns $\mathcal A$ with the same $\rho$ and $h_1..h_{J-1}$ and fresh
$h'_J..h'_q$; it succeeds if $J'=J$ and $h_J\ne h'_J$. Then
$$\mathrm{frk}\ \ge\ \mathrm{acc}\Big(\frac{\mathrm{acc}}{q}-\frac1h\Big).$$
*Proof sketch.* Per input $x$: $\Pr[J=J'\ge1]\ge\mathrm{acc}(x)^2/q$ by
Cauchy-Schwarz over the $q$ fork points and Jensen over the coins (the
rewinding lemma [S4 Lemma 19.2] is the $q=1$ case,
$\Pr\ge\varepsilon^2-\varepsilon/N$); subtract $\Pr[h_J=h'_J]\le 1/h$; then
average over $x$ with $\mathbb E[\mathrm{acc}^2]\ge\mathbb E[\mathrm{acc}]^2$. $\square$

Chained with the Schnorr ID analysis this gives [S4 eq. (19.6)]
$$\mathsf{Adv}^{\mathrm{sig}}\le\frac{Q_s(Q_s+Q_{ro}+1)}{q}+\frac{Q_{ro}+1}{N}
+(Q_{ro}+1)\sqrt{\mathsf{Adv}^{\mathrm{dl}}(\mathcal B)}.$$

## Worked numeric example

$q = N \approx 2^{256}$, $Q_{ro}=2^{60}$, $Q_s=2^{30}$.

- Programming term: $2^{30}\cdot 2^{60}/2^{256}=2^{-166}$. Negligible.
- $(Q_{ro}+1)/N\approx 2^{-196}$.
- A generic DL adversary with $T$ group operations succeeds w.p.
  $\lesssim T^2/q$ [S4 Thm 16.3]. Give $\mathcal B$ time comparable to the
  forger, $T=2^{60}$: $\mathsf{Adv}^{\mathrm{dl}}\approx2^{-136}$, square root
  $2^{-68}$, times $2^{60}$: **the bound guarantees only $2^{-8}$**.

So the proof, read literally, says little at 256-bit groups. This looseness is
why tighter analyses exist; the lecturer co-authored one proving Schnorr
tightly secure in the ROM under a non-interactive assumption [S43]
(**background**). FDH at the same query budget needs RSA to be
$2^{-188}$-hard for a $2^{-128}$ guarantee.

## Pitfalls

- **Programming a point that was already fixed.** Every programming step
  needs a collision bound; forgetting it is the usual gap in homework proofs.
- **Programmed values must be uniform.** $H(m_i)=r_i^e$ is uniform in
  $\mathbb Z_N^*$ only because $x\mapsto x^e$ is a permutation.
- **Rewinding an adversary that is not public-coin in the right way.**
  Forking needs the same coins $\rho$; hash answers *after* the fork point are
  fresh. The forger may choose $J$ depending on all answers
  (`toy_forger`), which is why $J'=J$ costs a factor $q$.
- **Mixing advantage conventions** (factor 2, see README).
- **Reading "secure in the ROM" as "secure with SHA-256".** Only generic
  attacks are excluded [S28].

## Exam-style questions

1. *State the difference lemma and use it to bound the loss when $G(r^*)$ is
   replaced by an independent value.* Answer: above; the bad event is
   "$\mathcal A$ queries $r^*$", bounded by the inverter's success.
2. *Why is the BR93 reduction tight while FDH's loses $Q_{ro}+1$?* BR93 only
   observes queries; FDH must embed one challenge and guess where the forgery
   lands, losing the guessing probability $1/(Q_{ro}+1)$.
3. *In the Schnorr ROM proof, where does $Q_s(Q_s+Q_{ro}+1)/q$ come from?* Each
   simulated signature programs $H$ at $(y,t,m)$ with fresh uniform $t$; it
   collides with one of at most $Q_s+Q_{ro}+1$ earlier points w.p.
   $\le(Q_s+Q_{ro}+1)/q$; union bound over $Q_s$ signatures.
4. *Attack: $E'(m) = (f(r),\,G(m)\oplus r)$. Secure?* No: $G$ is public, so
   for challenge $(y,c)$ compute $r_0 = c\oplus G(m_0)$ and test
   $f(r_0)=y$. Anyone can test a candidate plaintext; CPA advantage
   $\tfrac12$ (up to $\Pr[G(m_0)=G(m_1)]$).
5. *What does a ROM counterexample [S28] show, and what does it not show?* It
   shows no general theorem "ROM-secure implies secure with some hash" can
   hold. It does not give an attack on FDH, OAEP or Schnorr with SHA-2.

## Code

`rom_reductions.py`: `RandomOracle` (log, `program`); `br_encrypt`,
`ow_inverter_from_log` (the worked reduction); `simulated_sign` (keyless
Schnorr signing); `toy_forger`, `fork`, `extract_from_fork`, `forking_bound`.
Tests: `test_rom_reductions.py` (programming failure rate on a group of
order 11, forking success vs. the bound).
