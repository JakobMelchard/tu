# 04 — Computational security

*Lecture 4 [S8]. Katz-Lindell sec. 7.1 (stream ciphers) and sec. 3.1 [S10] —
Lemma 2.7, Def. 3.4. Code: the reduction pattern underlies every proof in
[`../src/py`](../src/README.md); the LCG distinguisher in
[`../src/py/prg.py`](../src/py/prg.py) is a concrete "adversary".*

Perfect secrecy is too expensive (note 02). Modern cryptography relaxes it on
two axes at once: security only against **efficient** adversaries, and allowing
a **tiny** failure probability. This is the central bargain of the field — and
this note is the most important in the course, because it fixes the *language*
(PPT, negligible, advantage) and the *method* (reduction) used everywhere after.

## Two relaxations

1. Security only against **probabilistic polynomial-time (PPT)** adversaries.
2. Adversaries may succeed with **negligible** probability.

Both are asymptotic: statements are parameterised by a **security parameter**
$\lambda$ (think: key length), given to algorithms in unary as $1^\lambda$.

### PPT

An algorithm is PPT if it runs in time polynomial in $\lambda$ and may toss coins.
"Efficient" $=$ PPT; "feasible attack" $=$ PPT adversary. Polynomials are closed
under addition, multiplication, and composition, which is exactly what makes
reductions compose (a poly-time reduction calling a poly-time adversary is
poly-time).

### Negligible functions

$f:\mathbb{N}\to\mathbb{R}^{\ge 0}$ is **negligible** if for every polynomial $p$
there is $N$ with $f(\lambda) < 1/p(\lambda)$ for all $\lambda > N$. Equivalently
$f(\lambda) = \lambda^{-\omega(1)}$: eventually smaller than *every* inverse
polynomial. Examples: $2^{-\lambda}$, $2^{-\sqrt\lambda}$, $\lambda^{-\log\lambda}$
are negligible; $1/\lambda^{100}$ is not.

**Closure (used constantly):** if $f,g$ negligible and $p$ polynomial, then
$f+g$ and $p\cdot f$ are negligible. So a union bound over polynomially many
negligible events is still negligible — this is what lets hybrid arguments with
$q$ steps go through when $q$ is polynomial.

## Computational indistinguishability & security

Redefine the eavesdropping game with a security parameter and a PPT adversary:

$$
\begin{array}{l}
\mathsf{PrivK}^{\mathrm{eav}}_{\mathcal{A},\Pi}(\lambda):\\
\quad \mathcal{A}(1^\lambda)\to (m_0,m_1),\ |m_0|=|m_1|\\
\quad b\gets\{0,1\},\ k\gets\mathsf{Gen}(1^\lambda),\ c\gets\mathsf{Enc}_k(m_b)\\
\quad \mathcal A(c)\to b';\ \text{output } 1 \text{ iff } b'=b
\end{array}
$$

**Definition (EAV-security / indistinguishable encryptions).** $\Pi$ is
EAV-secure if for every PPT $\mathcal{A}$ there is a negligible $\mathsf{negl}$ with
$$\Pr[\mathsf{PrivK}^{\mathrm{eav}}_{\mathcal A,\Pi}(\lambda)=1] \le \tfrac12 + \mathsf{negl}(\lambda).$$
The **advantage** is $\mathsf{Adv} = \big|\Pr[\dots=1] - \tfrac12\big|$; security says
it is negligible.

Two distribution ensembles $\{X_\lambda\}, \{Y_\lambda\}$ are **computationally
indistinguishable** ($X \approx_c Y$) if for every PPT $D$,
$$\big|\Pr[D(X_\lambda)=1] - \Pr[D(Y_\lambda)=1]\big| \le \mathsf{negl}(\lambda).$$
EAV-security is exactly $\mathsf{Enc}_k(m_0)\approx_c\mathsf{Enc}_k(m_1)$.

## Asymptotic vs concrete security

- **Asymptotic** (the definitions above): "no polynomial attack, key grows with
  $\lambda$." Clean for proofs; says nothing at a *fixed* key size.
- **Concrete:** "$\Pi$ is $(t,\varepsilon)$-secure" — every adversary running in
  time $\le t$ wins with advantage $\le \varepsilon$. E.g. "$128$-bit security":
  best attack needs $\approx 2^{128}$ steps. Reductions should be read
  concretely: a reduction that turns a time-$t$, advantage-$\varepsilon$
  attacker on $\Pi$ into a time-$t'$, advantage-$\varepsilon'$ attacker on
  primitive $P$ gives a *quantitative* security guarantee; a "tight" reduction
  keeps $t'\approx t$, $\varepsilon'\approx\varepsilon$.

## The reduction proof pattern

Almost every theorem in this course has the shape
$$\text{"if primitive } P \text{ is secure, then scheme } \Pi \text{ is secure."}$$
We prove the **contrapositive**: from any efficient adversary $\mathcal A$ that
breaks $\Pi$ we *construct* an efficient adversary/distinguisher $\mathcal B$ that
breaks $P$. Since $P$ is assumed secure, no such $\mathcal B$ exists, so no such
$\mathcal A$ exists.

### Template (memorise this shape)

> **Theorem.** If $P$ is secure then $\Pi$ is EAV-secure.
>
> **Proof.** Let $\mathcal A$ be a PPT adversary against $\Pi$ with advantage
> $\varepsilon(\lambda)$. Build $\mathcal B$ (a PPT distinguisher for $P$):
>
> 1. **$\mathcal B$ receives** its own challenge from the $P$-challenger (e.g. a
>    string that is either $P$'s output or truly random).
> 2. **$\mathcal B$ simulates** the $\Pi$-game *for* $\mathcal A$, using the
>    challenge in place of the real primitive. Key point: the simulation must be
>    *perfect* in each of $\mathcal B$'s two worlds.
> 3. **$\mathcal B$ observes** $\mathcal A$'s output and translates it into a guess
>    for its own challenge (typically: output $1$ iff $\mathcal A$ wins).
> 4. **Analysis.** When $\mathcal B$'s challenge is "real", $\mathcal A$ sees exactly
>    the real $\Pi$-game, so $\mathcal B$ outputs $1$ with prob $= \Pr[\mathcal A
>    \text{ wins real}]$. When "random", $\mathcal A$ sees an idealised game
>    (often information-theoretically secure), so $\mathcal B$ outputs $1$ with a
>    known, usually $\approx 1/2$, probability. Subtracting,
>    $\mathsf{Adv}_{\mathcal B}^{P} \ge \varepsilon(\lambda) - (\text{ideal slack})$.
> 5. **Conclude.** $\mathcal B$ is PPT, so by security of $P$ its advantage is
>    negligible, forcing $\varepsilon$ negligible. $\square$

The two questions to ask of *any* reduction: **(a)** Is $\mathcal B$ efficient
(PPT)? **(b)** Does $\mathcal B$ simulate $\mathcal A$'s world *perfectly* in both of
$\mathcal B$'s cases? If both hold, the advantage arithmetic in step 4 is
mechanical. Note 13 drills this; notes 05-11 instantiate it.

### A concrete distinguisher

`prg.lcg_distinguisher` is a real step-3 gadget: given four outputs of a linear
congruential generator it solves for the parameters and predicts the next value.
On LCG output it is right with probability $\approx 1$; on truly random input,
$\approx 1/2^{31}$. Its empirical advantage (`prg.lcg_advantage`) is $\approx 1$,
so the LCG is not a PRG. This is what "step 3 translates $\mathcal A$'s behaviour
into a $P$-guess" looks like in code.

## Hybrid arguments

When a reduction must bridge two worlds that differ in *many* places at once
(e.g. a PRG used $q$ times, or a multi-message encryption), a single reduction
can't cleanly simulate. The fix: interpolate with **hybrids** $H_0, H_1, \dots,
H_q$ where $H_0$ is the real world, $H_q$ the ideal world, and consecutive
hybrids differ in *one* primitive use. Then

$$\big|\Pr[D(H_0)=1]-\Pr[D(H_q)=1]\big| \le \sum_{i=1}^{q}\big|\Pr[D(H_{i-1})=1]-\Pr[D(H_i)=1]\big|,$$

by the triangle inequality. Each summand is bounded by the primitive's security
$\varepsilon$ via a single-step reduction (which *guesses* the boundary index
$i$, or fixes it). Total advantage $\le q\cdot\varepsilon$, negligible when $q$
is polynomial and $\varepsilon$ negligible. We use hybrids for: PRG expansion
(note 05, `prg.stretch`), CPA security of the PRF scheme over many blocks
(note 06), and multi-message security.

**Pitfall — the polynomial factor matters.** $q\cdot\varepsilon$ is negligible
only when $q = \mathrm{poly}(\lambda)$. A hybrid argument over exponentially many
steps proves nothing.

## Worked example

*Show: if $G$ is a secure PRG then $\Pi:\mathsf{Enc}_k(m)=G(k)\oplus m$ (a fixed-length
one-time scheme with $|k|=\lambda < |m|$) is EAV-secure.*

Let $\mathcal A$ break $\Pi$ with advantage $\varepsilon$. Build distinguisher
$\mathcal B(w)$ for $G$, where $w$ is either $G(k)$ or uniform $r$:
receive $(m_0,m_1)$ from $\mathcal A$; pick $b\gets\{0,1\}$; send $c = w\oplus m_b$;
output $1$ iff $\mathcal A$'s guess $b'=b$.

- $w=G(k)$: $\mathcal A$ sees the real game, so $\Pr[\mathcal B\to1] = \Pr[\mathsf{PrivK}=1] = \tfrac12+\varepsilon$.
- $w=r$ uniform: $c$ is a one-time pad on $m_b$, perfectly hiding $b$, so $\Pr[\mathcal B\to1]=\tfrac12$.

Thus $\mathsf{Adv}^{G}_{\mathcal B} = \varepsilon$. Since $G$ is secure, $\varepsilon$
is negligible. This is the note-04 stream cipher, and the cleanest instance of
the template. $\square$

## Pitfalls

- **The reduction runs $\mathcal A$; it does not know $\mathcal A$'s strategy.**
  $\mathcal B$ treats $\mathcal A$ as a black box — never "case-split on what
  $\mathcal A$ might do."
- **Imperfect simulation kills the proof.** If $\mathcal A$ can tell it's being
  simulated (e.g. $\mathcal B$ can't answer a query correctly), the advantage
  arithmetic collapses. Every query $\mathcal A$ makes must be answered exactly as
  the real challenger would.
- **Negligible $\times$ polynomial only.** Don't multiply a negligible term by
  something you haven't shown is polynomial.
- **"Can't find an attack" is not a proof.** Security is a proof relative to an
  assumption, never the absence of a known break.
- **Advantage vs success probability.** For indistinguishability, subtract the
  $1/2$ baseline; reporting raw $\Pr[\text{win}]$ hides the point.

## Exam-style questions

**Q1** *(M25 1h [S13] — the best trap on any of the papers).* If $f(n)$ is
negligible, is $n^{|f(n)|}$ negligible? — **No.** It reads like the closure
property $\mathrm{poly}\times\mathsf{negl}=\mathsf{negl}$, but the polynomial is
in the *exponent*. Write $n^{f(n)} = e^{f(n)\ln n}$. Since $f$ is negligible,
$f(n) \le 1/n^2$ eventually, so $f(n)\ln n \to 0$ and $n^{f(n)}\to 1$. The
quantity converges to 1, which is as far from negligible as a function can be.
Check where the variable sits before reaching for the closure lemma.

**Q2** *(F23 1b [S12]).* Is $f(n) = \frac{n-1}{n}$ negligible? — **No**; it
tends to 1. (A function must beat *every* inverse polynomial; this one does not
even tend to 0.)

**Q3** *(F20 2a [S15]).* Let $p$ be a positive polynomial. Is
$f(n) := p(n)\cdot 2^{-\log n}$ negligible? — **No.** $2^{-\log_2 n} = 1/n$, so
$f(n) = p(n)/n$, a ratio of polynomials. If $\deg p \ge 1$ it does not even tend
to 0. The same expression with $2^{-\log^2 n}$ or $2^{-\sqrt n}$ *would* be
negligible; the base-2 logarithm in the exponent is doing nothing at all.

**Q4** *(F20 2c [S15]).* Does every provably secure encryption scheme have to
assume the hardness of a computational problem? Justify. — **No.** The one-time
pad is proved perfectly secret unconditionally (note 02), with no assumption
whatsoever, because the proof is information-theoretic. What *is* true is that
every scheme with keys shorter than its messages must assume something: by the
Shannon bound such a scheme cannot be perfectly secret, so its security has to be
computational, and no computational lower bound of the required kind is known —
a PRG existing already implies $\mathrm P \neq \mathrm{NP}$ [S8].

**Q5** *(F20 2d [S15]).* An encryption scheme has message space $\{0,1\}^n$ and
ciphertext space $\{0,1\}^{\ell}$. Why must $\ell \ge n$? — Correctness alone
forces it. Fix a key $k$; $\mathsf{Dec}_k$ must recover $m$ from
$\mathsf{Enc}_k(m)$, so $\mathsf{Enc}_k$ is injective on $\mathcal M$. An
injection $\{0,1\}^n \to \{0,1\}^\ell$ requires $2^\ell \ge 2^n$. Nothing about
security is used. (Security pushes it further: CPA-security forces *strict*
expansion, because one plaintext must have many ciphertexts — note 06.)

**Q6** *(ours; the reduction template is examined through the schemes rather
than in the abstract, but the distinction is worth a question).* Explain the
difference between the asymptotic and the concrete statement of security, and
what a "tight" reduction buys you. — Asymptotically, $\Pi$ is secure if every
PPT adversary has negligible advantage as $n$ grows; this says nothing at any
fixed key size, which is the only size you ever deploy. Concretely, $\Pi$ is
$(t,\varepsilon)$-secure if every adversary running in time $\le t$ has advantage
$\le\varepsilon$. A reduction turns a $(t,\varepsilon)$-attack on $\Pi$ into a
$(t',\varepsilon')$-attack on the primitive $P$; it is **tight** when
$t'\approx t$ and $\varepsilon'\approx\varepsilon$. A loose reduction — say
$\varepsilon' = \varepsilon^2/q$ — is still a proof, but to claim 128-bit
security for $\Pi$ you must then instantiate $P$ at well above 128 bits. The
RSA-OAEP proof is the standard example of a loose one (note 10) [S40].

## Code

`src/py/prg.py`: `LCG`, `lcg_distinguisher`, `lcg_advantage` (the concrete
distinguisher of this note), `stretch` (the hybrid argument), and
`chacha20_encrypt`, the worked example's stream cipher as deployed (RFC 8439
[S36], `test_prg.py::test_chacha20_cipher_rfc8439_2_4_2`).
