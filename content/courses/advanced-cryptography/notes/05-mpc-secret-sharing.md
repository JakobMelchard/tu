# 05: Secure multi-party computation I: definitions and honest majority

*TISS heading 4, first half [S2]. Lindell's survey [S7] sec. 2 (definitions),
3 (feasibility), 4.1-4.2 (Shamir, honest-majority MPC); Lindell-Pinkas
[S13] sec. 2.1 (the semi-honest simulation definition); Shamir [S14];
Ben-Or-Goldwasser-Wigderson [S31] (cite only); Boneh-Shoup ch. 22.1 and 23
[S4]. Code: [`../src/py/secret_sharing.py`](../src/py/secret_sharing.py).*

## The problem

Parties $P_1,\dots,P_n$ with private inputs $x_i$ want $f(x_1,\dots,x_n)$
while an adversary controls up to $t$ of them. Desired properties [S7 sec. 2.1]:
**privacy** (learn only the output), **correctness**, **independence of
inputs**, **guaranteed output delivery**, **fairness** (the adversary gets
output only if the honest parties do). A list is not a definition; the
standard definition is by simulation.

## The ideal/real paradigm

**Ideal world:** an incorruptible trusted party receives all inputs and
returns the outputs. The only freedom of the ideal adversary $\mathcal S$ is
choosing the corrupted parties' inputs (and, "with abort", whether honest
parties get output).

**Definition (informal) [S7 sec. 2.1].** Protocol $\pi$ securely computes $f$
if for every real adversary $\mathcal A$ there is an ideal adversary
$\mathcal S$ with
$$\{\mathrm{IDEAL}_{f,\mathcal S}(\vec x)\}\ \approx\ \{\mathrm{REAL}_{\pi,\mathcal A}(\vec x)\},$$
the joint distribution of the adversary's output **and the honest parties'
outputs**. Joint, because otherwise a protocol that leaks nothing but
computes the wrong value would pass.

**Semi-honest two-party version [S13 sec. 2.1].** For deterministic $f$:
$\pi$ is secure if there are PPT $\mathcal S_1,\mathcal S_2$ with
$\mathcal S_1(x,f_1(x,y))\approx_c\mathrm{view}_1^\pi(x,y)$ and likewise for
$P_2$ (plus correctness). The view is (input, random tape, received messages).
Proof technique: **write the simulator**, then argue indistinguishability,
usually by a hybrid over messages.

### Parameters [S7 sec. 2.2]

| axis | options |
|---|---|
| behaviour | **semi-honest** (follows the protocol, reads its view), **malicious** (arbitrary), covert (cheating caught with fixed probability) |
| corruption | static, adaptive, proactive (mobile) |
| output | guaranteed delivery, fairness, or **security with abort** |
| composition | stand-alone (sequential modular composition) or universal composability |

Security with abort is forced in some cases: fair coin tossing between two
parties is impossible [S7 sec. 2.1].

### Feasibility [S7 sec. 3]

| corruption bound | result |
|---|---|
| $t<n/3$ | any $f$, **perfect** security with guaranteed output, private channels [S31] |
| $t<n/2$ | any $f$, fairness and output delivery, with a broadcast channel |
| $t\ge n/2$ (incl. $n=2$) | any $f$, computational, **without** fairness (GMW, Yao; note 06) |

## Shamir secret sharing [S14], [S7 sec. 4.1]

Over $\mathbb F_p$, $p>n$. **Share** $s$ with threshold $t$: random
$f(X)=s+a_1X+\dots+a_tX^t$; party $i$ gets $f(i)$. Any $t+1$ shares
determine $f$; any $t$ reveal nothing. (Shamir's own $(k,n)$ has
$k=t+1$ [S14].)

**Reconstruction.** For a set $I$, $|I|=t+1$:
$$s=f(0)=\sum_{i\in I}\lambda_i f(i),\qquad
\lambda_i=\prod_{j\in I,\,j\ne i}\frac{j}{j-i}.$$

**Theorem (perfect privacy).** For any $I$ with $|I|=t$ and any secret $s$,
$(f(i))_{i\in I}$ is uniform on $\mathbb F_p^t$.

*Proof.* The map $(a_1,\dots,a_t)\mapsto(f(i))_{i\in I}$ is affine with matrix
$(i^k)_{i\in I,\,1\le k\le t}$, which is $\mathrm{diag}(i)$ times a
Vandermonde matrix in distinct nonzero $i$: invertible. So it is a bijection
$\mathbb F_p^t\to\mathbb F_p^t$, and uniform coefficients give uniform
shares, whatever $s$ is. $\square$ (`test_t_shares_perfectly_private_exact`.)

## BGW-style evaluation [S7 sec. 4.2], [S31]

Circuit over $\mathbb F_p$; invariant: every wire value $v$ is held as a
degree-$t$ sharing $[v]_t$.

- **Addition, constants:** local. $[a]+[b]$, $k[a]$, $[a]+k$ are degree-$t$
  sharings of $a+b$, $ka$, $a+k$. No communication.
- **Multiplication:** local $c(i)=a(i)b(i)$ is a sharing of $ab$ of degree
  $2t$. Needs $2t+1\le n$ points to be determined: **honest majority**.
  Then reduce the degree:
  1. **Resharing (BGW/GRR).** $ab=c(0)=\sum_{i=1}^n\lambda_ic(i)$ with the
     Lagrange coefficients for $\{1..n\}$. Each $P_i$ shares $c(i)$ with
     degree $t$; $P_j$ outputs $\sum_i\lambda_i\,[c(i)]_t(j)$, a linear
     combination of degree-$t$ sharings, hence a degree-$t$ sharing of
     $\sum_i\lambda_ic(i)=ab$.
  2. **Double sharing [S7].** Jointly generate $[r]_t$ and $[r]_{2t}$ of the
     same unknown $r=\sum_jr_j$; open $d=ab-r$ from $[c]_{2t}-[r]_{2t}$;
     output $[r]_t+d$. $d$ is uniform because $r$ is, so opening it leaks
     nothing.
  3. **Beaver triples** [S4 sec. 23.2.2]. With preprocessed $[a],[b],[ab]$:
     open $d=x-a$, $e=y-b$ (uniform), output
     $[xy]=[ab]+d[b]+e[a]+de$. Only degree-$t$ openings, so this works
     without $n\ge2t+1$ at multiplication time; the triples must come from
     somewhere (dealer, OT, homomorphic encryption).
- **Output:** everyone broadcasts the output shares and interpolates.

**Semi-honest security sketch** ($|I|\le t$): every share $I$ receives is one
of $\le t$ shares of a fresh random degree-$t$ polynomial, hence uniform; every
opened value ($d$, or $d,e$) is uniform; the output shares are simulated by
interpolating a random degree-$t$ polynomial through the corrupted shares
and the known output. Malicious security needs verifiable secret sharing or
error correction (Reed-Solomon decoding for $t<n/3$) (**background**).

## Worked example

$p=11$, $n=3$, $t=1$.

- Share $s=5$ with $f=5+3X$: shares $(8,0,3)$. From parties 1, 2:
  $\lambda_1=\frac{2}{2-1}=2$, $\lambda_2=\frac{1}{1-2}=-1$:
  $2\cdot8-0=16\equiv5$. ✓
- $a=2$ via $2+X$: $(3,4,5)$; $b=4$ via $4+2X$: $(6,8,10)$. Local products
  $(18,32,50)\equiv(7,10,6)$, a degree-2 sharing. Lagrange for $\{1,2,3\}$:
  $(\lambda_1,\lambda_2,\lambda_3)=(3,-3,1)$: $21-30+6=-3\equiv8=ab$. ✓
- Resharing with $7+X$, $10+2X$, $6+4X$: sub-shares $(8,9,10)$, $(1,3,5)$,
  $(10,3,7)$. New shares $3\cdot(8,9,10)-3\cdot(1,3,5)+(10,3,7)\equiv(9,10,0)$:
  on the line $8+X$, degree 1, value 8 at 0. ✓

## Pitfalls

- **Degree bookkeeping.** After one local multiplication the sharing needs
  $2t+1$ parties to open; a second multiplication without reduction needs
  $3t+1$, and so on.
- **Opening a non-random value.** $c(i)$ itself must never be broadcast; only
  masked values ($d=ab-r$) may be opened.
- **Correctness is part of the definition.** A simulator that matches the view
  but not the honest output proves nothing.
- **Semi-honest protocols are not maliciously secure:** in BGW a corrupted
  party can reshare a wrong $c(i)$ and shift the product undetectably.
- **Shamir is not additive secret sharing:** additive $n$-of-$n$ sharing
  ($\sum x_i=s$) is the GMW setting of note 06.

## Exam-style questions

1. *Why does the ideal/real definition compare the joint distribution with
   the honest outputs?* Example: a protocol where the adversary outputs
   nothing but forces honest parties to output $0$ has a perfect view
   simulator yet is incorrect.
2. *Prove that $t$ Shamir shares reveal nothing.* Vandermonde argument above.
3. *With $n=5$, $t=2$: how many parties must be honest for BGW multiplication,
   and why does $n=4$ fail?* Reduction needs the degree-4 product sharing
   determined: $n\ge5$. With $n=4$ four points do not fix a degree-4
   polynomial ($c(0)$ undetermined), `test_honest_majority_needed`.
4. *In the double-sharing protocol, show the opened $d$ is independent of
   $ab$.* $d=ab-r$ with $r=\sum_jr_j$ uniform and at least one $r_j$ from an
   honest party unknown to the adversary.
5. *Compute $\lambda_1,\lambda_2,\lambda_3$ for points $1,2,3$ over
   $\mathbb F_{11}$ and check $\sum\lambda_i=1$.* $(3,-3,1)$; sum 1,
   because interpolating the constant polynomial 1 must give 1.

## Code

`secret_sharing.py`: `share`, `reconstruct`, `lagrange_at_zero`, `degree`;
gates `add`, `scal`, `add_const`, `mul_local`, `mul_resharing`,
`random_double_sharing`, `mul_double_sharing`, `beaver_triple`,
`mul_beaver`; `mpc_eval` with `EXAMPLE` $=(x_0+x_1)x_2+3x_3x_4$ among five
parties, $t=2$.
