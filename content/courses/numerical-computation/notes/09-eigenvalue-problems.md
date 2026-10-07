# 09 Eigenvalue problems

[S4] §7. Compute eigenvalues and eigenvectors of $A\in\mathbb R^{n\times n}$
iteratively. §7.1–7.3 are common to all curricula; **§7.4–7.6 are CSE-only**:
[S4] writes "END OF LECTURE FOR VISUAL COMPUTING" at the end of §7.3, so no
public past paper reaches the QR algorithm. Implementation: `src/py/qr_svd.py`,
`src/py/eig.py`.

Setting throughout: if $\lambda$ is known, the eigenvectors solve the singular
system $(A-\lambda I)x=0$, which may have several independent solutions;
conversely, if $x$ is known then
$$\lambda=\frac{x^\top Ax}{\|x\|_2^2}\qquad\text{(the \textbf{Rayleigh quotient})}\quad\text{[S4 §7]}.$$
**Never** compute eigenvalues as roots of the characteristic polynomial: the map
from coefficients to roots is badly conditioned *([S15]; not stated in [S4])*.

## 1. The power method [S4 §7.1]

*Goal:* the largest eigenvalue in modulus and its eigenvector. *Applications
[S4] names:* Google PageRank, and $\kappa_2(A)=\lambda_{\max}/\lambda_{\min}$ for
SPD $A$.

Assume $A$ diagonalisable with eigenvectors $v_1..v_n$ and
$|\lambda_1|>|\lambda_2|\ge\cdots\ge|\lambda_n|$. Writing $x_0=\sum_i\alpha_iv_i$,
$$A^\ell x_0=\sum_i\alpha_i\lambda_i^\ell v_i=\lambda_1^\ell\sum_i\alpha_i\Big(\frac{\lambda_i}{\lambda_1}\Big)^\ell v_i\ \xrightarrow{\ \ell\to\infty\ }\ \text{direction of }v_1,$$
provided $\alpha_1\ne0$. Normalise each step to avoid overflow [S4 Alg. 17]:

```
x := x / ||x||_2
repeat:
    x := A x / ||A x||_2          # approximate eigenvector
    lambda := x^T A x             # approximate eigenvalue (Rayleigh quotient)
```

**Theorem** [S4 Thm 7.1]. Under those assumptions the iterates are well defined
and
$$|\tilde\lambda_\ell-\lambda_1|\le C\Big|\frac{\lambda_2}{\lambda_1}\Big|^{\ell}.$$
**Theorem** [S4 Thm 7.5]: the *eigenvector* converges at the same rate,
$d(\mathrm{span}\{v_1\},\mathrm{span}\{x_\ell\})\le C|\lambda_2/\lambda_1|^\ell$,
where $d(S,T)=|\sin\varphi|$ with $\cos\varphi=\tfrac{x\cdot y}{\|x\|\|y\|}$ is the
angle between the two lines [S4 Def. 7.3, Rem. 7.4].

**Remarks** [S4 Rem. 7.2], all four examinable:

1. $\alpha_1\ne0$ cannot be checked, but a random $x_0$ satisfies it with
   probability 1 and rounding errors create a $v_1$ component anyway.
2. The eigenvalue statement survives a multiple $\lambda_1$.
3. It **fails** if $\lambda_1\ne\lambda_2$ but $|\lambda_1|=|\lambda_2|$: e.g. a
   real matrix with a complex-conjugate pair of dominant eigenvalues.
4. Its weakness is slow convergence when $|\lambda_2/\lambda_1|$ is near 1.

## 2. Inverse iteration and shifts [S4 §7.2]

*Goal:* eigenvalues other than the largest. Since
$\sigma(A^{-1})=\{1/\lambda_i\}$, the power method on $A^{-1}$ finds the
**smallest** $|\lambda|$ [S4 Alg. 18]; the convergence rate is
$|\lambda_n/\lambda_{n-1}|^\ell$ [S4 Rem. 7.6]. Do not invert: solve
$A\tilde x_{\ell+1}=x_\ell$, and **factor $A$ once** at the start so every step is
$O(n^2)$ [S4 Rem. 7.6].

**Inverse iteration with shift** [S4 Alg. 19] replaces $A$ by $A-\lambda I$:

```
repeat:
    solve (A - mu I) xt = x;   x := xt/||xt||_2;   lambda := x^T A x
```
**Theorem** [S4 Thm 7.7]. If the eigenvalues are ordered so that
$|\lambda_1-\mu|\ge\cdots\ge|\lambda_{n-1}-\mu|>|\lambda_n-\mu|>0$, then
$$|\lambda_n-\tilde\lambda_\ell|\le C\left|\frac{\lambda_n-\mu}{\lambda_{n-1}-\mu}\right|^{\ell}.$$
Two consequences: it converges to the eigenvalue **closest to the shift**, so you
can target one; and the closer $\mu$, the faster.

**Rayleigh quotient iteration** [S4 Alg. 20] takes that to its conclusion: use
the current best estimate as the shift:

```
repeat:
    mu := x^T A x
    solve (A - mu I) xt = x;   x := xt/||xt||_2
```
**Theorem** [S4 Thm 7.8]. For symmetric $A$ and a simple eigenvalue $\lambda$
with eigenvector $v$: if $d(\mathrm{span}\{x_0\},\mathrm{span}\{v\})<\epsilon$ then
one step gives
$$d(\mathrm{span}\{x_1\},\mathrm{span}\{v\})\le C\epsilon^3,\qquad \Big|\frac{x_0^\top Ax_0}{\|x_0\|_2^2}-\lambda\Big|\le C\epsilon^2,$$
i.e. **cubic** convergence of the eigenvector. For a general diagonalisable
matrix it is quadratic [S4 Rem. 7.9]. The price: the shift changes every step,
so the factorisation cannot be amortised: a fixed shift is cheaper per
iteration [S4 Rem. 7.9]. **That trade-off is the exam question** (F2 2.3,
F3 2.3b).

## 3. Stopping criteria [S4 §7.3]

$(x,\tilde\lambda)$ is an eigenpair iff the residual $r:=Ax-\tilde\lambda x$
vanishes. How well does a small residual bound the eigenvalue error?

**Theorem** [S4 Thm 7.10]. Let $A$ be diagonalisable, $T^{-1}AT=D$,
$\|x\|_2=1$, $r=Ax-\tilde\lambda x$. Then

1. $\displaystyle\min_{\lambda\in\sigma(A)}|\lambda-\tilde\lambda|\le\mathrm{cond}_2(T)\,\|r\|_2$;
2. $\displaystyle\min_{\lambda\in\sigma(A)}|\lambda-\tilde\lambda|\le\|r\|_2$ if $A$ is symmetric;
3. $\displaystyle\min_{\lambda\in\sigma(A)}|\lambda-\tilde\lambda|\le C\|r\|_2^2$ if
   $A$ is symmetric, $\tilde\lambda$ is the Rayleigh quotient, and $\tilde\lambda$
   is near a simple eigenvalue.

So the residual is a usable stopping test for a symmetric matrix, and only as
good as $\mathrm{cond}_2(T)$ otherwise: for a nearly defective matrix it is
useless. (3) is the reason for using the Rayleigh quotient rather than any old
estimate.

## 4. Orthogonal iteration [S4 §7.4] (CSE)

Run the power method on a $k$-dimensional subspace, described by
$X_0\in\mathbb R^{n\times k}$, and re-orthonormalise every step [S4 Alg. 21]:

```
X_0 =: Q_0 R_0
repeat:  X_{l+1} := A Q_l;   X_{l+1} =: Q_{l+1} R_{l+1}
```
The columns of $Q_\ell$ are an orthonormal basis of $A^\ell S^0$ [S4 Rem. 7.11],
and **Theorem 7.12** [S4] says the sequence of subspaces converges to the
invariant subspace of the $k$ dominant eigenvectors, so the blocks
$A_\ell([1{:}k],[k{+}1{:}n])$ of $A_\ell:=Q_\ell^\top AQ_\ell$ tend to zero: the
matrices tend to **block** triangular form [S4 Rem. 7.13].

## 5. The QR algorithm [S4 §7.5–7.6] (CSE)

**Orthogonal iteration with $X_0=I$** [S4 Alg. 22] performs $n$ simultaneous
orthogonal iterations at once: for each $k$, the first $k$ columns of $Q_\ell$ are
what Alg. 21 would produce from $[e^1..e^k]$, because
$$A^\ell=A^{\ell-1}Q_1R_1=\cdots=Q_\ell R_\ell\cdots R_1$$
and a product of upper triangular matrices is upper triangular [S4 Rem. 7.14].
If $|\lambda_1|>\cdots>|\lambda_n|$ then every block of
$A_\ell=Q_\ell^\top AQ_\ell$ below the diagonal tends to zero, and since the
$A_\ell$ are **similar** to $A$, the diagonal converges to the eigenvalues.

Rewriting the iteration in terms of $A_\ell$ alone gives the classical algorithm
[S4 Alg. 23]:
$$A_0:=A;\qquad A_\ell=:Q_\ell R_\ell,\qquad A_{\ell+1}:=R_\ell Q_\ell .$$
*Factor, then multiply the factors back in the other order.* Each $A_{\ell+1}$ is
similar to $A_\ell$, since $A_{\ell+1}=Q_\ell^\top A_\ell Q_\ell$.

**Three improvements**, each of which [S4] devotes a subsection to:

**Hessenberg form** [S4 §7.6.1]. Naively each step costs $O(n^3)$, so $O(n)$
steps cost $O(n^4)$ [S4 Rem. 7.15]. But a Hessenberg matrix ($a_{ij}=0$ for
$j>i+1$) has an $O(n^2)$ QR factorisation by Givens rotations, $RQ$ is $O(n^2)$,
and **$RQ$ is Hessenberg again** (note [06](06-qr-factorisation.md),
[S4 Ex. 4.55]). So: reduce $A$ to Hessenberg once in $O(n^3)$ by orthogonal
similarity, then iterate:
$$O(n^3)+O(n)\cdot O(n^2)=O(n^3).$$

**Deflation** [S4 §7.6.2]. If $A(n,[1{:}n-1])$ is (numerically) zero then
$A(n,n)$ is an eigenvalue and the search continues on the leading
$(n-1)\times(n-1)$ block. Monitor $\|A_\ell(n,[1{:}n-1])\|$ against
$\varepsilon\|A_\ell(n,:)\|$, accept, shrink, repeat: the savings compound
because the matrix keeps getting smaller.

**Shifts** [S4 §7.6.3]. [S4 Alg. 24]:
$$A_\ell-\mu^{(\ell)}I=:Q_{\ell+1}R_{\ell+1},\qquad A_{\ell+1}:=R_{\ell+1}Q_{\ell+1}+\mu^{(\ell)}I,$$
still similar to $A_\ell$ [S4 Exercise 7.16]. **Why it works** [S4 §7.6.3,
Lem. 7.18–7.19]: the shifted QR algorithm implicitly performs an *inverse*
iteration with shift on $A^H$, carried by the **last** column of $Q_\ell$. So
choosing the Rayleigh quotient as the shift makes $\|A_\ell(n,[1{:}n-1])\|$ go to
zero **quadratically**, one eigenvalue deflates almost immediately, and the whole
process is fast [S4 §7.6.2 item 2].

Two loose ends [S4 §7.6.4–7.6.5]: if the iteration stalls because several
eigenvalues share a modulus, a **random shift** separates $|\lambda_i-\mu|$ and
restores convergence; and for a real $A$ whose eigenvalues come in conjugate
pairs $\lambda,\bar\lambda$, two shifted steps with $\lambda$ and $\bar\lambda$
can be combined into one step in real arithmetic (the *double-shift* strategy).

Example (`qr_svd.qr_algorithm`, unshifted):
$A=\begin{psmallmatrix}4&1&0\\1&3&1\\0&1&2\end{psmallmatrix}$ has
$\lambda=3\pm\sqrt3,\ 3$; converges to $10^{-12}$.

## Pitfalls

- Running the power method on a real matrix with complex dominant eigenvalues.
  It does not converge [S4 Rem. 7.2(3)].
- Forming $A^{-1}$ for inverse iteration. Factor once and back-substitute
  [S4 Rem. 7.6].
- Worrying that $A-\mu I$ is nearly singular in inverse iteration. That is the
  *point*: the huge component along the wanted eigenvector dominates whatever
  the solve does to it.
- Using Rayleigh quotient iteration when a factorisation could be amortised: a
  shift that changes every step costs a fresh $O(n^3)$ factorisation each time
  [S4 Rem. 7.9].
- Trusting a small residual for a non-symmetric matrix. The bound carries
  $\mathrm{cond}_2(T)$ [S4 Thm 7.10(i)].
- Running the QR algorithm on a full matrix. $O(n^4)$; reduce to Hessenberg
  first [S4 Rem. 7.15, §7.6.1].
- Computing eigenvalues from the characteristic polynomial.
- Forgetting the $+\mu I$ in the shifted QR step: without it the iterates are no
  longer similar to $A$.

## Exam-style questions

Only items 1–3 are attested (F2 2.3, F3 2.3b, F3 2.5e); the QR-algorithm
questions are ours, since no Visual Computing paper reaches §7.4.

1. *(F2 2.3, 2022W)* Choose an eigenvalue algorithm for a given problem,
   explain why, list its advantages and disadvantages, and write it down.
   Model answer for Rayleigh quotient iteration: use it when a good initial
   eigenvector guess is available and the matrix is symmetric. Algorithm as in
   §2 above. Advantages: **cubic** convergence for symmetric $A$
   [S4 Thm 7.8], quadratic in general [S4 Rem. 7.9]; it targets whichever
   eigenvalue is nearest the start. Disadvantages: the shift changes every step,
   so a fresh $O(n^3)$ factorisation per iteration; which eigenvalue you land on
   is not controllable in advance; and $A-\mu I$ becomes singular in the limit.
2. *(F3 2.3b, 2022W re-test)* Compare inverse iteration with a fixed shift
   against Rayleigh quotient iteration.
   Both are power iterations on $(A-\mu I)^{-1}$. Fixed shift: rate
   $\big|\tfrac{\lambda_n-\mu}{\lambda_{n-1}-\mu}\big|$, linear, but $A-\mu I$ is
   factored once so each step is $O(n^2)$ [S4 Thm 7.7, Rem. 7.6]. Rayleigh:
   $\mu_\ell=x_\ell^\top Ax_\ell$, cubic for symmetric $A$ [S4 Thm 7.8], but
   $O(n^3)$ per step. Use the fixed shift when you know roughly where the
   eigenvalue is and want many cheap steps; use Rayleigh when you want very few,
   very accurate ones.
3. *(F3 2.5e, 2022W re-test)* What is the convergence behaviour of the power
   method?
   $|\tilde\lambda_\ell-\lambda_1|\le C|\lambda_2/\lambda_1|^\ell$: linear, with
   the ratio of the two largest eigenvalues as the rate [S4 Thm 7.1]. The same
   rate for the eigenvector angle [S4 Thm 7.5].
4. *(ours)* State the three residual bounds of [S4 Thm 7.10] and say which one
   justifies using the Rayleigh quotient.
   $\mathrm{cond}_2(T)\|r\|$ in general, $\|r\|$ for symmetric $A$, and
   $C\|r\|^2$ for symmetric $A$ with $\tilde\lambda$ the Rayleigh quotient near a
   simple eigenvalue. The third.
5. *(ours: CSE)* Write down the basic QR algorithm and explain in one sentence
   why all iterates have the same eigenvalues.
   $A_\ell=Q_\ell R_\ell$, $A_{\ell+1}=R_\ell Q_\ell$ [S4 Alg. 23]; since
   $R_\ell=Q_\ell^\top A_\ell$, $A_{\ell+1}=Q_\ell^\top A_\ell Q_\ell$ is a
   similarity transformation.
6. *(ours: CSE)* Why is the basic QR algorithm $O(n^4)$ and how do the three
   standard improvements fix that?
   Each QR factorisation is $O(n^3)$ and $O(n)$ steps are needed
   [S4 Rem. 7.15]. Hessenberg reduction makes each step $O(n^2)$ and is
   preserved by $RQ$, giving $O(n^3)$ overall; deflation shrinks the matrix as
   eigenvalues are found; shifts make the last off-diagonal row go to zero
   quadratically so deflation happens almost immediately
   [S4 §7.6.1–7.6.3].
7. *(ours: CSE)* What is the relation between the shifted QR algorithm and
   inverse iteration?
   The shifted QR algorithm implicitly runs an inverse iteration with the same
   shift on $A^H$, carried by the last column of $Q_\ell$ [S4 Lem. 7.18–7.19],
   which is why a Rayleigh-quotient shift gives quadratic convergence of the
   bottom row.

## Implementation

`src/py/qr_svd.py`: `power_method` ([S4 Alg. 17]), `qr_algorithm`
([S4 Alg. 23]).

`src/py/eig.py` (new): `rayleigh_quotient`, `subspace_angle` ([S4 Def. 7.3]),
`inverse_iteration` ([S4 Alg. 18], one LU reused), `inverse_iteration_shift`
([S4 Alg. 19]), `rayleigh_quotient_iteration` ([S4 Alg. 20]),
`eigen_residual_bound` ([S4 Thm 7.10]), `orthogonal_iteration` ([S4 Alg. 21]),
`hessenberg` (Householder similarity reduction), `shifted_qr` (Hessenberg +
Wilkinson-style shift + deflation, [S4 Alg. 24, §7.6]).

Tests `test_eig.py`: against `numpy.linalg.eig`/`eigvalsh`/`scipy.linalg.hessenberg`;
the measured rate $|\lambda_2/\lambda_1|$ of [S4 Thm 7.1] and the matching
eigenvector-angle rate of [S4 Thm 7.5]; the $|\tfrac{\lambda_n-\mu}{\lambda_{n-1}-\mu}|$
rate of [S4 Thm 7.7]; **measured cubic convergence of Rayleigh quotient
iteration on a symmetric matrix and quadratic on a non-symmetric one**
[S4 Thm 7.8, Rem. 7.9]; all three residual bounds of [S4 Thm 7.10], including a
non-symmetric case where bound (ii) would fail; the failure of the power method
when $|\lambda_1|=|\lambda_2|$ [S4 Rem. 7.2(3)]; $RQ$ preserving Hessenberg form;
and shifted QR with deflation reaching $10^{-12}$ in $O(n)$ total iterations on
the $\begin{psmallmatrix}4&1&0\\1&3&1\\0&1&2\end{psmallmatrix}$ example
($\lambda=3\pm\sqrt3,3$).
