# 04: Zero knowledge II: succinct arguments

*TISS heading 3, second half ("succinct proof systems") [S2]. Groth16 [S18]
sec. 2.3 (QAP) and 3.2 (the scheme); Gennaro-Gentry-Parno-Raykova [S32]
(QAPs); Bulletproofs [S19] sec. 3 (inner-product argument). Boneh-Shoup v0.6
has sec. 20.5 (Bulletproofs) and 20.6 (SNARKs) only as "to be written" [S4],
so the papers are the sources here. Code:
[`../src/py/r1cs_toy.py`](../src/py/r1cs_toy.py),
[`../src/py/commitments.py`](../src/py/commitments.py) (inner-product argument).*

This note is an **intuition** note: the shape of the constructions and the
one algebraic identity that makes each work. Proofs of knowledge soundness
(generic group model for Groth16, rewinding for Bulletproofs) are
**background**.

## What "succinct" means

A **SNARK** is a succinct non-interactive argument of knowledge: for a
relation given by a circuit of size $|C|$, the proof has size
$\mathrm{poly}(\lambda)\cdot\mathrm{polylog}|C|$ (Groth16: constant) and
verification is much cheaper than rerunning $C$. Argument: soundness only
against efficient provers. Two setups:

- **Trusted (structured) CRS**, generated with secret randomness that must be
  destroyed ("toxic waste"); Groth16's CRS is circuit-specific [S18].
- **Transparent**: only public random generators; Bulletproofs [S19].

## Arithmetic circuits and R1CS

An arithmetic circuit over $\mathbb F_p$ has addition and multiplication
gates; circuit satisfiability is NP-complete [S18 abstract]. **Rank-1
constraint system (R1CS):** matrices $A,B,C\in\mathbb F^{n\times(m+1)}$ and
the assignment vector $z=(1,a_1,\dots,a_m)$ (first $\ell$ entries public,
rest witness). $z$ satisfies iff
$$ (Az)\circ(Bz) = Cz\qquad(\circ = \text{entrywise product}).$$
One row per **multiplication**; additions and constants fold into the linear
combinations [S18 sec. 2.3].

## From R1CS to a QAP [S18 sec. 2.3], [S32]

Pick distinct $r_1,\dots,r_n\in\mathbb F$, let $t(X)=\prod_q(X-r_q)$, and
interpolate each **column** $i$: $u_i(r_q)=A_{q,i}$, $v_i(r_q)=B_{q,i}$,
$w_i(r_q)=C_{q,i}$, $\deg<n$. With $A(X)=\sum_iz_iu_i(X)$ etc.:

**Lemma.** $z$ satisfies the R1CS $\iff$ $t(X)\mid A(X)B(X)-C(X)$.

*Proof.* $A(r_q)B(r_q)-C(r_q)$ is exactly constraint $q$'s residual. So the
R1CS holds iff $P=AB-C$ vanishes at every $r_q$, iff each $(X-r_q)$ divides
$P$, iff $t\mid P$ (the $r_q$ are distinct). $\square$

So satisfaction becomes one polynomial identity
$A(X)B(X)-C(X)=h(X)t(X)$ with $\deg h\le n-2$. **Schwartz-Zippel:** a nonzero
polynomial of degree $d$ vanishes at a uniform $\tau\in\mathbb F$ w.p.
$\le d/|\mathbb F|$, so checking the identity at one secret random point
$\tau$ suffices if the prover cannot learn $\tau$: SNARKs let the prover
evaluate "in the exponent" at a hidden $\tau$ via the CRS
$\{[\tau^i]_1\}$.

## Groth16 shape [S18 sec. 3.2]

CRS from trapdoor $(\alpha,\beta,\gamma,\delta,\tau)$ ($x$ in [S18]):
encodings of $\alpha,\beta,\delta,\tau^i$, of
$K_i(\tau)/\gamma$ for public $i\le\ell$ and $K_i(\tau)/\delta$ for private
$i$, where $K_i=\beta u_i+\alpha v_i+w_i$, and of $\tau^it(\tau)/\delta$.
Prover with fresh $r,s$:
$$A=\alpha+\sum_i z_iu_i(\tau)+r\delta,\quad B=\beta+\sum_iz_iv_i(\tau)+s\delta,$$
$$C=\frac{\sum_{i>\ell}z_iK_i(\tau)+h(\tau)t(\tau)}{\delta}+As+Br-rs\delta .$$
Proof $\pi=([A]_1,[C]_1,[B]_2)$: **3 group elements**. Verifier:
$$[A]_1\cdot[B]_2=[\alpha]_1\cdot[\beta]_2+\Big[\sum_{i\le\ell}z_i\tfrac{K_i(\tau)}{\gamma}\Big]_1\cdot[\gamma]_2+[C]_1\cdot[\delta]_2,$$
"$\cdot$" the pairing: **one pairing-product equation, 3 pairings** with
$[\alpha\beta]_T$ precomputed [S18].

*Completeness (the algebra).* Write $A_u=\sum z_iu_i(\tau)$, $B_v$, $C_w$
likewise. Expand $AB=(\alpha+A_u+r\delta)(\beta+B_v+s\delta)$. On the right,
$\sum_{\text{all }i}z_iK_i=\beta A_u+\alpha B_v+C_w$ and
$C\delta=\sum_{i>\ell}z_iK_i+ht+sA\delta+rB\delta-rs\delta^2$. Substitute
$sA\delta=s\delta(\alpha+A_u+r\delta)$, $rB\delta=r\delta(\beta+B_v+s\delta)$
and the QAP identity $A_uB_v=C_w+h(\tau)t(\tau)$: both sides equal
$\alpha\beta+\alpha B_v+\beta A_u+A_uB_v+\alpha s\delta+\beta r\delta+
A_us\delta+B_vr\delta+rs\delta^2$. $\square$

*Zero knowledge:* $r,s$ make $A,B$ uniform; $C$ is then determined by the
equation, so **with the trapdoor** one simulates: pick $A,B$, solve for $C$
[S18]. The same computation proves **false** statements: whoever keeps
$(\alpha,\beta,\delta)$ can forge (`simulate`, tested on $\text{out}=41$).
Knowledge soundness holds in the generic bilinear group model [S18 Thm 2]
(**background**).

## Bulletproofs: the inner-product argument [S19 sec. 3]

Relation: generators $\mathbf g,\mathbf h\in\mathbb G^n$, $u\in\mathbb G$,
$P=\mathbf g^{\mathbf a}\mathbf h^{\mathbf b}u^{\langle\mathbf a,\mathbf b\rangle}$.
One round halves $n$. Split $\mathbf a=(\mathbf a_L,\mathbf a_R)$ etc., send
$$L=\mathbf g_R^{\mathbf a_L}\mathbf h_L^{\mathbf b_R}u^{c_L},\quad
R=\mathbf g_L^{\mathbf a_R}\mathbf h_R^{\mathbf b_L}u^{c_R},\qquad
c_L=\langle\mathbf a_L,\mathbf b_R\rangle,\ c_R=\langle\mathbf a_R,\mathbf b_L\rangle,$$
receive $x$, fold
$$\mathbf g'=\mathbf g_L^{x^{-1}}\circ\mathbf g_R^{x},\ \
\mathbf h'=\mathbf h_L^{x}\circ\mathbf h_R^{x^{-1}},\ \
P'=L^{x^2}PR^{x^{-2}},\ \
\mathbf a'=x\mathbf a_L+x^{-1}\mathbf a_R,\ \
\mathbf b'=x^{-1}\mathbf b_L+x\mathbf b_R .$$
*Why $P'$ has the same form.* $\mathbf g'^{\mathbf a'}=\mathbf g_L^{\mathbf
a_L+x^{-2}\mathbf a_R}\mathbf g_R^{x^2\mathbf a_L+\mathbf a_R}$ and similarly for
$\mathbf h'$, which matches the $\mathbf g,\mathbf h$ exponents of
$L^{x^2}PR^{x^{-2}}$; and
$$\langle\mathbf a',\mathbf b'\rangle=\langle\mathbf a,\mathbf b\rangle+x^2c_L+x^{-2}c_R,$$
the $u$-exponent of $L^{x^2}PR^{x^{-2}}$. $\square$ Recursing $\log_2n$
times and sending the final scalars: **$2\log_2n$ group elements + 2
scalars**, prover $O(n)$, verifier $O(n)$ exponentiations; Fiat-Shamir makes
it non-interactive. Extraction rewinds each round to get several challenges
(the paper uses four per level) and needs that no one knows discrete-log
relations among the generators [S19]. The argument is sound but **not
zero-knowledge**; the range proof on top adds blinding, total
$2\log_2n+9$ elements for an $n$-bit range [S19 abstract].

| | Sigma (note 03) | Groth16 | Bulletproofs |
|---|---|---|---|
| proof size | $O(|C|)$ | 3 group elements | $2\log_2 n+O(1)$ |
| verifier | $O(|C|)$ | 3 pairings + $\ell$ exps | $O(n)$ |
| setup | none | trusted, per circuit | transparent |
| assumption | DL (+ROM for FS) | generic bilinear group | DL (+ROM for FS) |

## Worked example

$\mathbb F_{97}$, statement $x^3+2x+7=\text{out}$, $x=3$, out $=40$.
Flatten: $v_1=x\cdot x$, $v_2=v_1\cdot x$, $(v_2+2x+7)\cdot1=\text{out}$.
$z=(1,\text{out},x,v_1,v_2)=(1,40,3,9,27)$:
$$A=\begin{pmatrix}0&0&1&0&0\\0&0&0&1&0\\7&0&2&0&1\end{pmatrix},\
B=\begin{pmatrix}0&0&1&0&0\\0&0&1&0&0\\1&0&0&0&0\end{pmatrix},\
C=\begin{pmatrix}0&0&0&1&0\\0&0&0&0&1\\0&1&0&0&0\end{pmatrix}.$$
Rows: $3\cdot3=9$, $9\cdot3=27$, $40\cdot1=40$. ✓ With $r_q=1,2,3$:
$t=X^3-6X^2+11X-6$; $A(X)=61X^2+17X+22$ (values $3,9,40$),
$B(X)=-X^2+3X+1$ (values $3,3,1$), $C(X)=46X^2+74X+83$ (values $9,27,40$);
$A B-C=h\,t$ with $h(X)=36X-6$. Changing $v_1$ to 10 leaves a nonzero
remainder. (Run `r1cs_toy.py`.)

Inner-product round in $\mathbb Z_{11}$: $\mathbf a=(1,2)$,
$\mathbf b=(3,5)$, $\langle\mathbf a,\mathbf b\rangle=13\equiv2$, $c_L=5$,
$c_R=6$; $x=2$, $x^{-1}=6$: $a'=2+12\equiv3$, $b'=18+10\equiv6$,
$a'b'=18\equiv7$ and $2+4\cdot5+3\cdot6=40\equiv7$ ($x^{-2}=36\equiv3$). ✓

## Pitfalls

- **Toxic waste.** Anyone holding $(\alpha,\beta,\delta,\tau)$ forges Groth16
  proofs; setups are run as multi-party ceremonies so that one honest
  participant suffices (**background**).
- **Schwartz-Zippel needs a big field.** In $\mathbb F_{97}$ a random $\tau$
  hits a root with probability $\deg/96$ (`test_groth16_in_the_clear` has to
  skip that event).
- **Groth16 CRS is per circuit**; changing the circuit needs a new setup.
- **Public inputs outside the hash** in Fiat-Shamir'd IPAs: same weak-FS
  problem as note 03.
- **Bulletproofs verification is linear**, not succinct in the verifier.

## Exam-style questions

1. *Write the R1CS for $y=x^2+x$.* $v=x\cdot x$; $(v+x)\cdot1=y$; $z=(1,y,x,v)$.
2. *Prove: $z$ satisfies the R1CS iff $t\mid AB-C$.* Above.
3. *Show that in Groth16 anyone knowing $\alpha,\beta,\delta$ can prove a false
   statement.* Choose $A,B$; set $C=(AB-\alpha\beta-\sum_{i\le\ell}z_iK_i)/\delta$.
4. *Verify the folding identity $\langle\mathbf a',\mathbf b'\rangle=
   \langle\mathbf a,\mathbf b\rangle+x^2c_L+x^{-2}c_R$.* Expand:
   $\langle x\mathbf a_L+x^{-1}\mathbf a_R,\,x^{-1}\mathbf b_L+x\mathbf b_R\rangle$.
5. *Why is Bulletproofs' IPA not zero-knowledge by itself, and what is its
   proof size for $n=64$?* The final $a,b$ and $L,R$ are deterministic
   functions of the witness; 12 group elements + 2 scalars.

## Code

`r1cs_toy.py`: `CONSTRAINTS`, `matrices`, `witness`, `r1cs_satisfied`,
`lagrange`, `qap`, `qap_quotient`, and Groth16 in the clear: `setup`,
`prove`, `verify`, `simulate` (no hiding, no soundness: the verifier holds
the trapdoor). `commitments.py`: `ipa_prove`, `ipa_verify` (Protocol 2),
`ipa_relation2_prove/verify` (Protocol 1).
