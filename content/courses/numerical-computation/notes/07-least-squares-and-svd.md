# 07 Least squares and the SVD

[S4] §5. Given $A\in\mathbb R^{m\times n}$ with $m\ne n$ allowed, find a
"reasonable" solution of $Ax=b$ [S4 (5.1)]. For $m>n$ the system is
**overdetermined** (no solution in general) and for $m<n$ **underdetermined**:
no unique solution [S4 Rem. 5.1]. The $\ell^2$ norm makes both tractable:
overdetermined by the normal equations or QR, underdetermined by the SVD.
Implementation: `src/py/qr_svd.py`, `src/py/pseudoinverse.py`,
`src/py/interp.py`.

Throughout §5.1–5.3.4 [S4] assumes **full rank**; §5.3.5 drops that.

## 1. The normal equations [S4 §5.1]

**Definition** [S4 Def. 5.2]. $x\in\mathbb R^n$ is a **least-squares solution** of
$Ax=b$ if
$$\|b-Ax\|_2=\min\{\|b-Ay\|_2:y\in\mathbb R^n\}\qquad\text{[S4 (5.2)]}.$$

**Derivation.** For fixed $v$, $\pi(t):=\|b-A(x+tv)\|_2^2$ is a quadratic in $t$
with a minimum at $t=0$, so
$$0=\pi'(0)=2\langle b-Ax,Av\rangle_2=2v^\top A^\top(b-Ax)\quad\forall v
\ \Longrightarrow\ A^\top(b-Ax)=0,$$
the **normal equations**
$$\boxed{\;A^\top Ax=A^\top b\;}\qquad\text{[S4 (5.3)]}$$
**Theorem** [S4 Thm 5.4]: $x$ solves the minimisation problem **iff** it solves
the normal equations (the argument reverses). **Theorem** [S4 Thm 5.5]: for
$m\ge n$ with linearly independent columns, $A^\top A$ is invertible, so both
problems have exactly one solution.

Note the exam trap: the normal equation is $A^\top Ax=A^\top b$, **not**
$A^\top Ax=b$ (S2a 2.5c marks the latter as false).

`polyfit` is a least-squares problem [S4 Ex. 5.3]: given $n+1$ points and
$m\le n$, choose $(a_j)_{j=0}^m$ minimising $\sum_i(\pi(x_i)-y_i)^2$, and MATLAB
actually uses the QR route below.

## 2. Least squares via QR [S4 §5.2]

The problem with the normal equations is that $\kappa(A^\top A)=\kappa(A)^2$
[S4 §5.2]. So factor $A=QR$ instead (note [06](06-qr-factorisation.md)), write
$$R=\begin{pmatrix}R^\ast\\0\end{pmatrix},\qquad Q^\top b=\begin{pmatrix}b^\ast\\ \tilde b\end{pmatrix},\qquad b^\ast\in\mathbb R^n,$$
and use orthogonal invariance:
$$\|Ay-b\|_2^2=\|Q(Ry-Q^\top b)\|_2^2=\|R^\ast y-b^\ast\|_2^2+\|\tilde b\|_2^2 .$$
The first term is killed by $y=(R^\ast)^{-1}b^\ast$; the second is the residual,
$\|\tilde b\|_2$. Procedure [S4 §5.2.1]: $[Q,R]=\mathrm{qr}(A)$; $b^\ast=(Q^\top b)_{1:n}$;
back-substitute $R^\ast x=b^\ast$. If the columns of $A$ are independent then the
diagonal of $R^\ast$ has no zeros, so $R^\ast$ is invertible.

**Cost** [S4 footnote 1]: for $m\gg n$, QR costs $2mn^2$ against $mn^2$ for the
normal equations: a factor 2 for a squared improvement in conditioning.

**The demonstration** [S4 Ex. 5.6], worth reproducing by hand:
$$A=\begin{pmatrix}1&1\\\varepsilon&0\\0&\varepsilon\end{pmatrix},\quad b=\begin{pmatrix}2\\\varepsilon\\\varepsilon\end{pmatrix},\quad x=\begin{pmatrix}1\\1\end{pmatrix},\quad A^\top A=\begin{pmatrix}1+\varepsilon^2&1\\1&1+\varepsilon^2\end{pmatrix}.$$
$Ax=b$ exactly, so $x=(1,1)$ is the exact answer, and
$\kappa(A^\top A)=\tfrac2{\varepsilon^2}+1$. With $\varepsilon=10^{-7}$
($\kappa(A^\top A)\approx2\cdot10^{14}$), MATLAB's normal equations return
$(1.011235955056180,\,0.988764044943820)$ (**two correct digits**, exactly as
$\kappa\varepsilon_{\mathrm{mach}}$ predicts) while the QR route returns
$(1,1)$ to all 16. (`test_pseudoinverse.py` reproduces both.)

*(Background [S15, S16], not in [S4]: the sensitivity of the least-squares
solution is $\big(\kappa(A)+\kappa(A)^2\tan\theta\big)\|\Delta A\|/\|A\|$, where
$\theta$ is the angle between $b$ and $\mathrm{range}(A)$, so QR gives $\kappa$
for small-residual problems, while the normal equations always give
$\kappa^2$.)*

## 3. Underdetermined systems and the SVD [S4 §5.3]

For $m<n$ with $\mathrm{rank}\,A=m$ the system is solvable but the solution is
not unique. Fix it by asking for the **minimum-norm solution**
$$\|x^\ast\|_2=\min\{\|y\|_2:Ay=b\}\qquad\text{[S4 §5.3]}.$$

**Theorem (SVD)** [S4 Thm 5.7]. Every $A\in\mathbb R^{m\times n}$ factors as
$$A=U\Sigma V^\top,\qquad U\in\mathcal O_m,\ V\in\mathcal O_n,\ \Sigma_{ij}=\delta_{ij}\sigma_i,\ \sigma_1\ge\cdots\ge\sigma_{\min(m,n)}\ge0 .$$
The $\sigma_i$ are the **singular values**, the columns of $U$ the **left** and
of $V$ the **right singular vectors**. `svd` / `numpy.linalg.svd`
[S4 Rem. 5.10, S20].

**What it reveals** [S4 Exercise 5.8]: if
$\sigma_1\ge\cdots\ge\sigma_r>\sigma_{r+1}=\cdots=0$ then

- $r=\mathrm{rank}\,A$;
- $U(:,1{:}r)$ is an orthonormal basis of $\mathrm{Im}\,A$;
- $V(:,r{+}1{:}n)$ is an orthonormal basis of $\ker A$, and $V(:,1{:}r)$ of
  $(\ker A)^\perp$.

Also: the eigenvalues of $A^\top A$ are those of $\Sigma^\top\Sigma$ and of
$AA^\top$ those of $\Sigma\Sigma^\top$, i.e. $\sigma_i^2$ [S4 Exercise 5.9]; and
$AV=U\Sigma$, i.e. $Av_i=\sigma_iu_i$: orthogonal vectors mapped to orthogonal
vectors [S4 Rem. 5.11]. Norms [S4 Exercise 5.14]:
$$\|A\|_F^2=\sum_i\sigma_i^2,\qquad \|A\|_2=\sigma_1,\qquad \kappa_2(A)=\sigma_1/\sigma_n .$$

**Reduced SVD** [S4 §5.3.1]: with $r=\mathrm{rank}\,A$ put
$\widetilde U=U(:,1{:}r)$, $\widetilde V=V(:,1{:}r)$,
$\widetilde\Sigma=\Sigma(1{:}r,1{:}r)$ (invertible), $V^0=V(:,r{+}1{:}n)$; then
$A=\widetilde U\widetilde\Sigma\widetilde V^\top$ and the columns of $V^0$ span
$\ker A$. Orthogonal projections [S4 Exercise 5.12, Lem. 5.18]:
$V^0(V^0)^\top$ onto $\ker A$, $\widetilde V\widetilde V^\top$ onto
$(\ker A)^\perp$, $\widetilde U\widetilde U^\top$ onto $\mathrm{range}\,A$.

**Minimum-norm solution** [S4 §5.3.2]. For $m\le n$ of full rank,
$$x^\ast=\widetilde V\widetilde\Sigma^{-1}U^\top b$$
satisfies $Ax^\ast=b$, and every solution is $x^\ast+V^0y$ with
$x^\ast\perp\ker A$, so
$\|x\|_2^2=\|x^\ast\|_2^2+\|V^0y\|_2^2$ is minimised at $y=0$.

**Rank in floating point** [S4 Rem. 5.16]: every computed $\sigma_i$ is non-zero,
so pick a cut-off $\epsilon$ a little above machine precision and set
$r=\#\{\sigma_i\ge\epsilon\}$.

**Low-rank approximation** [S4 Thm 5.15] (= Eckart–Young–Mirsky). For
$\nu\le r$, $A_\nu:=U(:,1{:}\nu)\Sigma(1{:}\nu,1{:}\nu)V(:,1{:}\nu)^\top$
satisfies
$$\|A-A_\nu\|_2=\min_{\mathrm{rank}\,B=\nu}\|A-B\|_2=\sigma_{\nu+1},\qquad
\|A-A_\nu\|_F=\min_{\mathrm{rank}\,B=\nu}\|A-B\|_F=\sqrt{\textstyle\sum_{i>\nu}\sigma_i^2}.$$
Optimal in **both** norms: that is the striking part. Storage
$\nu(m+n+1)$ instead of $mn$. This is PCA (centre the columns; $\sigma_i^2$ is
explained variance), image compression and model reduction.

## 4. The Moore–Penrose pseudoinverse [S4 §5.3.5] (CSE)

Drop every assumption: arbitrary $m,n$, arbitrary rank. Then
$$\text{find }x\in\mathbb R^n\text{ minimising }\|Ax-b\|_2\qquad\text{[S4 (5.5)]}$$
has solutions but possibly many; ask again for the one of smallest norm.

**Theorem** [S4 Thm 5.17]. With the reduced SVD
$A=\widetilde U\widetilde\Sigma\widetilde V^\top$ and
$$A^+:=\widetilde V\,\widetilde\Sigma^{-1}\,\widetilde U^\top\qquad\text{[S4 (5.6)]},$$
$x^\ast=A^+b$ is the minimum-norm least-squares solution.

*Proof sketch* [S4]: split $b=\widetilde U\widetilde U^\top b+U^0(U^0)^\top b$ and
$x=\widetilde V\widetilde V^\top x+V^0(V^0)^\top x$ using the projection lemma
[S4 Lem. 5.18]. Then
$$\|Ax-b\|_2^2=\|\widetilde\Sigma\widetilde V^\top x-\widetilde U^\top b\|_2^2+\|U^0(U^0)^\top b\|_2^2,$$
minimal iff $\widetilde V^\top x=\widetilde\Sigma^{-1}\widetilde U^\top b$; among
those, $\|x\|_2^2=\|\widetilde V\widetilde\Sigma^{-1}\widetilde U^\top b\|_2^2+\|V^0(V^0)^\top x\|_2^2$
is smallest when $(V^0)^\top x=0$, which gives $x^\ast=A^+b$.

**Interpretation** [S4 §5.3.5]. $A$ restricted to $(\ker A)^\perp$ is a bijection
$A_K:(\ker A)^\perp\to\mathrm{range}\,A$, and
$$A^+:\ \mathbb R^m\ \xrightarrow{\ \text{orth. proj.}\ }\ \mathrm{range}\,A\ \xrightarrow{\ A_K^{-1}\ }\ (\ker A)^\perp .$$
Project onto what $A$ can reach, then invert the part of $A$ that is invertible.

Properties [S4 §5.3.6, Exercise 5.19]: $A^+=A^{-1}$ when $A$ is invertible;
$AA^+A=A$; $(A^+)^+=A$; $\|A^+\|_2=\sigma_r^{-1}$.

**Computing the SVD** [S4 §5.3.6]. Via eigenvalues, but *not* of $A^\top A$ or
$AA^\top$, which are typically ill conditioned (they square $\kappa$ and destroy
the small $\sigma_i$). Instead use the symmetric
$\begin{psmallmatrix}0&A^\top\\A&0\end{psmallmatrix}$, whose eigenvalues are
$\pm\sigma_i$. Our `qr_svd.jacobi_svd` takes the other standard route
(one-sided Jacobi, §5 below), which never forms $A^\top A$ either.

## 5. One-sided Jacobi SVD *(not in [S4]; how our code does it)*

Orthogonalise the **columns** of $A$ by right-multiplying with rotations. For a
pair $(i,j)$ with $\alpha=\|a_i\|^2$, $\beta=\|a_j\|^2$, $\gamma=a_i^\top a_j$:
$$\zeta=\frac{\beta-\alpha}{2\gamma},\quad t=\frac{\mathrm{sign}\,\zeta}{|\zeta|+\sqrt{1+\zeta^2}},\quad c=\frac1{\sqrt{1+t^2}},\ s=ct,$$
$(a_i,a_j)\leftarrow(ca_i-sa_j,\ sa_i+ca_j)$, accumulating the same rotation in
$V$. This is a Jacobi rotation on the $2\times2$ block of $A^\top A$ **without
forming $A^\top A$**. Sweep all pairs until $|\gamma|\le\epsilon\sqrt{\alpha\beta}$;
then $AV=U\Sigma$ with $\sigma_i=\|a_i\|$ and $u_i=a_i/\sigma_i$. Quadratic
convergence after a few sweeps, $O(mn^2)$ per sweep, trivially parallel, and
(unlike the Golub–Kahan bidiagonalisation LAPACK uses) accurate to high
*relative* precision for the small singular values of graded matrices.

## Pitfalls

- Writing the normal equations as $A^\top Ax=b$ (S2a 2.5c).
- Using the normal equations on an ill-conditioned $A$: $\kappa^2$, so half the
  digits [S4 Ex. 5.6].
- Computing the SVD from the eigenvalues of $A^\top A$: squares $\kappa$ and
  loses the small $\sigma_i$ entirely [S4 §5.3.6].
- Thresholding singular values "above 0" in floating point: everything is
  non-zero. Use a relative cut-off [S4 Rem. 5.16].
- Reading $\kappa_2=\sigma_1/\sigma_n$ as "$\sigma_n$ is accurate". $|\delta\sigma_i|\le\|\delta A\|_2$
  is an *absolute* bound, so a $\sigma=10^{-10}$ in a matrix with $\sigma_1=1$ has
  relative error $\sim10^{-6}$.
- Mixing up which problem the SVD is *for* here. In [S4] it enters through the
  **underdetermined / minimum-norm** case (§5.3), not as the standard tool for
  overdetermined systems, which is QR. F3 2.5g marks "SVD is used for
  overdetermined systems" as false on exactly that reading.
- Least squares does not interpolate: it minimises the 2-norm of the residual,
  and outliers pull hard because the residual is squared.

## Exam-style questions

Modelled on S2a 2.3/2.5, F2 2.4/2.5 and F3 2.5g; see [00](00-exam-focus.md).
Item 5 is the long essay question F2 actually set.

1. *(S2a 2.3, 2024W)* A rectangle has sides $a,b$. Three independent
   measurements give $a\approx15$, $b\approx21$, $a+b\approx39$ (cm). Find the
   refined $a,b$ by least squares.
   $A=\begin{psmallmatrix}1&0\\0&1\\1&1\end{psmallmatrix}$, $y=(15,21,39)^\top$.
   $A^\top A=\begin{psmallmatrix}2&1\\1&2\end{psmallmatrix}$,
   $A^\top y=(54,60)^\top$. Solving:
   $a=(2\cdot54-60)/3=16$, $b=(2\cdot60-54)/3=22$. (Residual
   $(-1,-1,1)$, $\|r\|_2=\sqrt3$. Sanity check: $a+b=38\ne39$; least squares
   spreads the inconsistency.)
2. *(F2 2.4, 2022W)* Solve the least-squares problem for
   $\begin{psmallmatrix}1&1\\2&0\\0&2\end{psmallmatrix}x=\begin{psmallmatrix}1\\1\\-5\end{psmallmatrix}$.
   $A^\top A=\begin{psmallmatrix}5&1\\1&5\end{psmallmatrix}$,
   $A^\top b=(3,-9)^\top$; $\det=24$, so
   $x=\tfrac1{24}\begin{psmallmatrix}5&-1\\-1&5\end{psmallmatrix}\begin{psmallmatrix}3\\-9\end{psmallmatrix}=\tfrac1{24}(24,-48)^\top=(1,-2)^\top$.
3. *(S2a 2.3a / 2.5, 2024W)* Define the least-squares solution for $m>n$. State
   the normal equations. Is $m<n$ over- or underdetermined?
   $\|b-Ax\|_2=\min_y\|b-Ay\|_2$ [S4 Def. 5.2]; $A^\top Ax=A^\top b$
   [S4 (5.3)]; $m<n$ is **under**determined [S4 Rem. 5.1].
4. *(ours)* Why prefer QR over the normal equations, and what does it cost?
   $\kappa(A^\top A)=\kappa(A)^2$, so the normal equations lose twice as many
   digits [S4 §5.2, Ex. 5.6]; QR costs $2mn^2$ against $mn^2$ [S4 footnote 1].
5. *(F2 2.5, 2022W: essay)* What is the SVD, when do you need it, what do the
   individual matrices and entries contain, and how are they related?
   $A=U\Sigma V^\top$ with $U,V$ orthogonal and $\Sigma$ diagonal with
   $\sigma_1\ge\cdots\ge0$ [S4 Thm 5.7]. The $\sigma_i^2$ are the eigenvalues of
   $A^\top A$ (and of $AA^\top$) [S4 Exercise 5.9]; the columns of $V$ are the
   corresponding eigenvectors of $A^\top A$ (right singular vectors), those of
   $U$ the left ones, with $Av_i=\sigma_iu_i$ [S4 Rem. 5.11]. The number of
   non-zero $\sigma_i$ is the rank; $U(:,1{:}r)$ spans the range,
   $V(:,r{+}1{:}n)$ the kernel [S4 Exercise 5.8]. Needed for the
   minimum-norm solution of an underdetermined system [S4 §5.3.2], the
   pseudoinverse [S4 Thm 5.17], numerical rank [S4 Rem. 5.16], and optimal
   low-rank approximation [S4 Thm 5.15]. Also $\|A\|_2=\sigma_1$,
   $\|A\|_F^2=\sum\sigma_i^2$, $\kappa_2=\sigma_1/\sigma_n$.
6. *(ours: CSE)* Define $A^+$ and say in one sentence what it does
   geometrically.
   $A^+=\widetilde V\widetilde\Sigma^{-1}\widetilde U^\top$ [S4 (5.6)]; it
   projects $b$ orthogonally onto $\mathrm{range}\,A$ and then applies the
   inverse of the bijection $A:(\ker A)^\perp\to\mathrm{range}\,A$
   [S4 §5.3.5].
7. *(ours)* What is the best rank-2 approximation of $A$ in the Frobenius norm
   and what is its error?
   $\sigma_1u_1v_1^\top+\sigma_2u_2v_2^\top$; error
   $\sqrt{\sigma_3^2+\sigma_4^2+\cdots}$ [S4 Thm 5.15].

## Implementation

`src/py/qr_svd.py`: `qr_solve` (least squares via QR), `jacobi_svd`,
`low_rank`, `cond2`.
`src/py/interp.py`: `lstsq_normal`, `lstsq_qr`, `polyfit`.

`src/py/pseudoinverse.py` (new): `min_norm_solution` ([S4 §5.3.2]), `lstsq_svd`
([S4 Exercise 5.13]), `pinv` ([S4 (5.6)]), `numerical_rank` ([S4 Rem. 5.16]),
`project_range` / `project_kernel` ([S4 Exercise 5.12]), `svd_via_symmetric`
(the $\begin{psmallmatrix}0&A^\top\\A&0\end{psmallmatrix}$ route of [S4 §5.3.6]).

Tests: `test_qr_svd.py` (against `numpy.linalg.qr/lstsq/svd/matrix_rank`;
Eckart–Young) and `test_pseudoinverse.py` (the four Penrose identities;
$\|A^+\|_2=\sigma_r^{-1}$ [S4 Exercise 5.19]; the minimum-norm property against
`numpy.linalg.lstsq` and `scipy.linalg.pinv`; **the $\varepsilon=10^{-7}$
normal-equations-vs-QR digit loss of [S4 Ex. 5.6]**; the $\pm\sigma_i$ spectrum
of the symmetric embedding; and the S2a 2.3 / F2 2.4 exam items above).
