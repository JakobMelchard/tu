# 07: Lattices and learning with errors

*TISS heading 5, first half [S2]. Peikert's survey [S6] sec. 2.2 (lattices,
problems), 3.3 (GGH), 4.1-4.2 (SIS, LWE, Regev's theorem, classical
hardness), 5.2.1 (Regev's cryptosystem); Regev's paper [S15] sec. 1 and 5;
Galbraith [S37] ch. 16-18 (reduction, Babai). Boneh-Shoup ch. 17 is a stub in
v0.6 [S4]. Code: [`../src/py/lattice_toy.py`](../src/py/lattice_toy.py),
[`../src/py/lwe_toy.py`](../src/py/lwe_toy.py).*

## Lattices

**Definition [S6 sec. 2.2.1].** For linearly independent
$\mathbf b_1,\dots,\mathbf b_n\in\mathbb R^n$ (the basis $B$),
$\mathcal L(B)=\{\sum_iz_i\mathbf b_i: z\in\mathbb Z^n\}$. $B$ and $BU$ span the
same lattice iff $U\in\mathbb Z^{n\times n}$ is unimodular
($\det U=\pm1$). Invariants: $\det\mathcal L=|\det B|$ (volume of the
fundamental parallelepiped), successive minima $\lambda_1\le\dots\le\lambda_n$.
**Minkowski:** $\lambda_1\le\sqrt n\,(\det\mathcal L)^{1/n}$ [S37 sec. 16.2].

**Gram-Schmidt** $\mathbf b_i^*=\mathbf b_i-\sum_{j<i}\mu_{ij}\mathbf b_j^*$,
$\mu_{ij}=\langle\mathbf b_i,\mathbf b_j^*\rangle/\|\mathbf b_j^*\|^2$;
$\det\mathcal L=\prod\|\mathbf b_i^*\|$. Unlike in $\mathbb R^n$ the
$\mathbf b_i^*$ are generally *not* lattice vectors.

## Problems [S6 Def. 2.2.1-2.2.5]

- **SVP$_\gamma$:** find $\mathbf v\in\mathcal L\setminus0$ with
  $\|\mathbf v\|\le\gamma\lambda_1$.
- **GapSVP$_\gamma$:** decide $\lambda_1\le1$ or $\lambda_1>\gamma$.
- **SIVP$_\gamma$:** $n$ independent vectors of length $\le\gamma\lambda_n$.
- **CVP / BDD$_\gamma$:** closest lattice vector to $\mathbf t$; BDD with the
  promise $\mathrm{dist}(\mathbf t,\mathcal L)<\lambda_1/(2\gamma)$, which
  makes the answer unique.

**State of the art [S6 sec. 2.2.2].** Polynomial-time algorithms (LLL and
descendants) reach only $\gamma=2^{\Theta(n\log\log n/\log n)}$;
$\gamma=\mathrm{poly}(n)$ costs $2^{\Theta(n)}$ time or more, with
time/approximation trade-offs in between (BKZ). No quantum algorithm is known
to do significantly better [S6 sec. 4.2.2].

## Reduction and decoding in small dimension

**Lagrange-Gauss** [S37 Alg. 23]: repeat $\mathbf b_2\gets\mathbf b_2-\lfloor\mu\rceil\mathbf b_1$,
$\mu=\langle\mathbf b_1,\mathbf b_2\rangle/\|\mathbf b_1\|^2$, swap while
$\|\mathbf b_2\|<\|\mathbf b_1\|$. Output satisfies $\|\mathbf b_1\|\le\|\mathbf b_2\|$,
$|\mu|\le\tfrac12$, and then $\mathbf b_1$ is a shortest vector: for
$\mathbf v=x\mathbf b_1+y\mathbf b_2$ with $y\ne0$,
$\|\mathbf v\|^2\ge (x^2-|xy|+y^2)\|\mathbf b_1\|^2\ge\|\mathbf b_1\|^2$ (use
$|2\langle\mathbf b_1,\mathbf b_2\rangle|\le\|\mathbf b_1\|^2\le\|\mathbf b_2\|^2$
and $x^2-|xy|+y^2\ge1$ for integers not both zero). $\square$

**LLL** [S37 sec. 17.4] generalises it: size-reduce ($|\mu_{ij}|\le\tfrac12$)
and swap unless the Lovász condition
$\|\mathbf b_k^*\|^2\ge(\delta-\mu_{k,k-1}^2)\|\mathbf b_{k-1}^*\|^2$ holds;
with $\delta=\tfrac34$, $\|\mathbf b_1\|\le2^{(n-1)/2}\lambda_1$ in polynomial
time.

**Babai** [S37 sec. 18.1-18.2]. *Rounding:* write $\mathbf t=B\mathbf x$,
output $B\lfloor\mathbf x\rceil$: correct iff $\mathbf t-\mathbf v$ lies in
$B[-\tfrac12,\tfrac12)^n$. *Nearest plane:* same with Gram-Schmidt, correct
iff the error lies in $B^*[-\tfrac12,\tfrac12)^n$. Both succeed for short
errors **only if the basis is short and nearly orthogonal**. A good basis is
a **trapdoor**; the same lattice given by a bad basis hides it (GGH [S6 sec.
3.3]; modern trapdoors [S6 sec. 5.4]). `trapdoor_experiment`: Babai rounding
with the good basis decodes 100 % of noisy points, with the bad basis 17 %.

## Learning with errors

**Definition [S6 Def. 4.2.1-4.2.3].** Parameters $n,q$, error distribution
$\chi$ on $\mathbb Z$ (discrete Gaussian of width $\alpha q$). For secret
$\mathbf s\in\mathbb Z_q^n$, a sample is $(\mathbf a,\ b=\langle\mathbf
s,\mathbf a\rangle+e\bmod q)$, $\mathbf a$ uniform, $e\gets\chi$.
**Search-LWE:** find $\mathbf s$ from $m$ samples. **Decision-LWE:**
distinguish samples from uniform $(\mathbf a,b)$. Matrix form
$(A,\ A\mathbf s+\mathbf e)$.

- $\chi=0$: Gaussian elimination recovers $\mathbf s$ from $n$ samples
  (`solve_mod_q`, and it fails once noise is added).
- $q=2$, Bernoulli $\chi$: learning parity with noise [S6 sec. 4.2.1].
- Lattice view: $A\mathbf s+\mathbf e$ is a point near the $q$-ary lattice
  $\{A\mathbf s\bmod q\}+q\mathbb Z^m$; search-LWE is BDD on it.

**Theorem (Regev) [S15 Thm 1.1], [S6 Thm 4.2.4].** For $m=\mathrm{poly}(n)$,
$q\le2^{\mathrm{poly}(n)}$ and discretised Gaussian $\chi$ with
$\alpha q\ge2\sqrt n$, solving decision-LWE$_{n,q,\chi,m}$ is at least as hard
as **quantumly** solving GapSVP$_\gamma$ and SIVP$_\gamma$ on **arbitrary**
$n$-dimensional lattices, $\gamma=\tilde O(n/\alpha)$.

Reading: an algorithm breaking *random* LWE instances yields a quantum
algorithm for the *worst-case* lattice problem. The reduction is quantum; a
classical one exists for GapSVP with $q\ge2^{n/2}$ [S6 sec. 4.2.4].

## Regev's cryptosystem [S15 sec. 5], [S6 sec. 5.2.1]

- **KeyGen:** $\mathbf s\gets\mathbb Z_q^n$; $A\gets\mathbb Z_q^{m\times n}$,
  $\mathbf b=A\mathbf s+\mathbf e$. $pk=(A,\mathbf b)$, $sk=\mathbf s$.
- **Enc**$(\mu\in\{0,1\})$: random subset $S\subseteq[m]$ (vector
  $\mathbf x\in\{0,1\}^m$): $(\mathbf u,c)=(\mathbf x^{\!\top}A,\ \mathbf
  x^{\!\top}\mathbf b+\mu\lfloor q/2\rfloor)$.
- **Dec:** $d=c-\langle\mathbf u,\mathbf s\rangle=\mathbf x^{\!\top}\mathbf e+\mu\lfloor q/2\rfloor$;
  output 0 iff $d$ is closer to 0 than to $q/2$.

*Correctness.* Decryption succeeds iff $|\mathbf x^{\!\top}\mathbf e|<q/4$.
With $e_i$ of standard deviation $\sigma$ and $|S|\approx m/2$,
$\mathbf x^{\!\top}\mathbf e$ has standard deviation $\approx\sigma\sqrt{m/2}$,
so
$$\Pr[\text{fail}]\approx2\,\Phi\!\Big(-\frac{q/4}{\sigma\sqrt{m/2}}\Big).$$
Regev picks $q$ prime in $[n^2,2n^2]$, $m=(1+\varepsilon)(n+1)\log q$,
$\alpha=o(1/(\sqrt n\log n))$ to make this negligible [S15 sec. 5].

*Security (hybrid).* $H_0$: real $pk$, encryption of $\mu$. $H_1$: $(A,\mathbf
b)$ replaced by uniform: indistinguishable by decision-LWE. In $H_1$, for
$m\ge(1+\varepsilon)(n+1)\log q$ the pair $(\mathbf x^{\!\top}A,\mathbf
x^{\!\top}\mathbf b)$ is statistically close to uniform given $(A,\mathbf b)$
(leftover hash lemma, [S15 Claim 5.3, Lemma 5.4]), so it hides $\mu$. $\square$

## Worked examples

**Regev, $n=2$, $q=23$.** $\mathbf s=(3,7)$; samples $\mathbf a_i=(1,5),(4,2),(6,9),(10,3)$,
$e=(1,-1,0,1)$: $\mathbf b=(16,2,12,6)$ (e.g. $3+35+1=39\equiv16$).
Encrypt $\mu=0$ with $S=\{1,3,4\}$: $\mathbf u=(17,17)$, $c=16+12+6\equiv11$.
Decrypt: $\langle\mathbf u,\mathbf s\rangle=170\equiv9$, $d=2=e_1+e_3+e_4$,
close to 0: $\mu=0$. For $\mu=1$: $c=11+11=22$, $d=13$, distance to
$q/2=11.5$ is small: $\mu=1$. ✓

**Measured failure rate** ($n=32$, $q=1031$, $m=364$, `failure_rate`):

| $\sigma$ | measured | Gaussian estimate |
|---|---|---|
| 2 | 0.0000 | 0.0000 |
| 8 | 0.0210 | 0.0169 |
| 12 | 0.1135 | 0.1114 |
| 16 | 0.2395 | 0.2324 |

(the estimate ignores the rounding variance $1/12$ per sample, hence slightly low).

**Reduction in 2-D.** Good basis $(17,1),(-2,19)$, $\det=325$; bad basis
$(69,157),(41,98)=U\cdot$good with $U=\begin{pmatrix}5&8\\3&5\end{pmatrix}$.
Lagrange-Gauss on the bad basis: $\mu=2$ gives $(-13,-39)$; $\mu=-3$ gives
$(2,-19)$; $\mu=2$ gives $(-17,-1)$; stop: $\{(-17,-1),(2,-19)\}$, the good
basis up to sign. Babai rounding of $\mathbf t=(40,43)$: good-basis
coordinates $(2.60,2.13)\to(3,2)\to(47,41)$, the closest point; bad-basis
coordinates $(6.64,-10.19)\to(7,-10)\to(73,119)$, far away.

## Pitfalls

- **Error too small or too structured:** $\chi=0$ is linear algebra;
  errors from a small set allow linearisation attacks (Arora-Ge;
  **background**, no source fetched).
- **Correctness vs security tension:** larger $\alpha$ helps security,
  hurts decryption; $q$ must grow with $\sigma\sqrt m$.
- **Row vs column conventions:** [S6] writes bases as columns, the code as
  rows; unimodular $U$ acts from the other side.
- **"Worst-case hardness" is about asymptotics:** it does not fix concrete
  parameters; those come from attack cost estimates (note 08).
- **Babai's success depends on the basis**, not only on the lattice.

## Exam-style questions

1. *Show that $B$ and $BU$ generate the same lattice for unimodular $U$, and
   that $|\det B|$ is an invariant.* $U\mathbb Z^n=\mathbb Z^n$;
   $\det(BU)=\pm\det B$.
2. *Why is LWE without noise easy, and what does the noise turn it into
   geometrically?* Gaussian elimination; BDD on a $q$-ary lattice.
3. *Derive the decryption condition of Regev's scheme and estimate the
   failure rate for $\sigma=8$, $m=364$, $q=1031$.*
   $|\mathbf x^{\!\top}\mathbf e|<q/4$; $z=257.75/(8\sqrt{182})\approx2.39$,
   $2\Phi(-2.39)\approx0.017$.
4. *State Regev's worst-case to average-case theorem; what is quantum about
   it?* Above; the reduction (from lattice problem to LWE oracle) uses a
   quantum step to generate discrete Gaussian samples [S6 sec. 4.2.2].
5. *Lagrange-Gauss: reduce $(5,3),(8,5)$.* $\det=1$ so the lattice is
   $\mathbb Z^2$: $\mu=\mathrm{round}(55/34)=2$: $(8,5)-2(5,3)=(-2,-1)$;
   swap; $\mu=\mathrm{round}(-13/5)=-3$: $(5,3)+3(-2,-1)=(-1,0)$; swap;
   $\mu=\mathrm{round}(2/1)=2$: $(-2,-1)-2(-1,0)=(0,-1)$; stop:
   $\{(-1,0),(0,-1)\}$.

## Code

`lattice_toy.py`: `gram_schmidt`, `gauss_reduce`, `lll`, `is_lll_reduced`,
`babai_round`, `babai_nearest_plane`, `svp_bruteforce`, `cvp_bruteforce`,
`hadamard_ratio`, `GOOD`/`BAD`, `trapdoor_experiment`. `lwe_toy.py`:
`regev_keygen/encrypt/decrypt`, `failure_rate`, `failure_estimate`,
`solve_mod_q`.
