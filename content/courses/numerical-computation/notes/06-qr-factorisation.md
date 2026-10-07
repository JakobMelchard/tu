# 06 QR factorisation

[S4] §4.7. A third factorisation, $A=QR$ with $Q$ orthogonal: both
$Qy=b$ and $Rx=y$ are easy, and **orthogonal matrices do not amplify errors**.
About twice the cost of LU, and the method of choice when $\kappa(A)$ is large
[S4 §4.7]. It is also the engine of least squares (note
[07](07-least-squares-and-svd.md)) and of the QR algorithm for eigenvalues (note
[09](09-eigenvalue-problems.md)). Implementation: `src/py/qr_svd.py`,
`src/py/givens.py`, `src/cpp/qr.cpp`.

## 1. Orthogonal matrices [S4 §4.7.1]

$Q\in\mathbb R^{n\times n}$ is **orthogonal** if $Q^\top Q=I$ [S4 Def. 4.38]; then
$Q^{-1}=Q^\top$, so $Qy=b$ costs $O(n^2)$, not $O(n^3)$. $\mathcal O_n$ denotes
the set of them; it is a group under multiplication. In $\mathbb R^3$ the
orthogonal matrices are reflections in a plane, rotations, and permutations
[S4 Ex. 4.39].

**Theorem** [S4 Thm 4.40]. (i) Products and inverses of orthogonal matrices are
orthogonal. (ii) $\begin{psmallmatrix}I_k&0\\0&Q\end{psmallmatrix}\in\mathcal O_n$
for $Q\in\mathcal O_{n-k}$: this is what lets a Householder step act on a
trailing block. (iii) $\|Qx\|_2=\|x\|_2$, hence $\kappa_2(Q)=1$. (iv)
$x^\top y=(Qx)^\top(Qy)$: angles are preserved too.

(iii) is the whole point [S4 Rem. 4.41]: the relative error amplification of
multiplying by $Q$ is
$$\frac{\|Q(x+\Delta x)-Qx\|_2}{\|Qx\|_2}=\frac{\|Q\Delta x\|_2}{\|Qx\|_2}=1\cdot\frac{\|\Delta x\|_2}{\|x\|_2},$$
an amplification factor of exactly $1$.

## 2. The factorisation [S4 §4.7.2]

For $m\ge n$, $R\in\mathbb R^{m\times n}$ is **generalised upper triangular** if
$R_{ij}=0$ for $i>j$, i.e. $R=\begin{psmallmatrix}\tilde R\\0\end{psmallmatrix}$
with $\tilde R$ upper triangular; $A=QR$ with $Q\in\mathcal O_m$ is a
**QR factorisation** [S4 Def. 4.42].

**Existence via Gram–Schmidt.** Orthonormalising the columns $a_j=A_{:,j}$
produces $q_j$ with $(q_i,q_j)=\delta_{ij}$ and $(q_i,a_j)=0$ for $i>j$; then
$Q=[q_1..q_n]$ and $R:=Q^\top A$ is upper triangular because
$R_{ij}=(q_i,a_j)=0$ for $i>j$.

- **Theorem** [S4 Thm 4.43]: every invertible $A\in\mathbb R^{n\times n}$ has a QR
  factorisation, **unique** once the signs of the $R_{ii}$ are fixed (flipping
  the sign of a $q_i$ gives another valid pair).
- **Theorem** [S4 Thm 4.44]: for $A\in\mathbb R^{m\times n}$ with linearly
  independent columns, $A=QR$ with $Q\in\mathbb R^{m\times m}$ orthogonal; the
  remaining $m-n$ columns of $Q$ are chosen to complete the basis.

**Cost $O(m^2n)$** [S4 Rem. 4.45]; for $m=n$ that is $O(n^3)$, roughly twice LU.
`qr` in MATLAB, `numpy.linalg.qr` in Python. Solving $Ax=b$
[S4 Rem. 4.46]: factor, set $y=Q^\top b$, back-substitute $Rx=y$. Twice the cost
of LU, preferred when $\kappa(A)$ is large, and since $R=Q^\top A$,
$\kappa(R)\le\kappa(A)$.

**Gram–Schmidt is not numerically stable** [S4 §4.7.2]: too many subtractions.
[S4] says only this and moves to Householder. The quantitative version [S15]:

| method | flops | $\|A-QR\|$ | $\|Q^\top Q-I\|$ |
|---|---|---|---|
| classical Gram–Schmidt | $2mn^2$ | $O(u)$ | $O(\kappa(A)^2u)$ |
| modified Gram–Schmidt | $2mn^2$ | $O(u)$ | $O(\kappa(A)u)$ |
| Householder | $2mn^2-\tfrac23n^3$ | $O(u)$ | $O(u)$ |

CGS subtracts projections of the *original* $a_j$, so errors in early $q_i$ are
never corrected; MGS subtracts them one at a time from the running vector, so
each projection sees the already-cleaned vector. The *factorisation* is fine for
both; the *orthogonality* is not. Demo (`qr_svd.py` `__main__`, $60\times12$,
$\kappa_2=10^9$): $\|Q^\top Q-I\|$ is $6\cdot10^{-2}$ (CGS), $2\cdot10^{-8}$
(MGS), $7\cdot10^{-16}$ (Householder), while $\|A-QR\|\approx10^{-16}$ for all
three.

## 3. Householder reflections [S4 §4.7.3] (CSE)

The stable construction. Zero out one column at a time with orthogonal
transformations:
$$Q_{n-1}\cdots Q_1A=R,\qquad A=Q_1^\top\cdots Q_{n-1}^\top R .$$

**Definition** [S4 Def. 4.47]. For $v\in\mathbb R^n$ with $\|v\|_2=1$,
$$H=I-2vv^\top$$
is the **Householder reflection** induced by $v$: geometrically, reflection in
the hyperplane $\{x:v^\top x=0\}$. **Properties** [S4 Lem. 4.48]: $H$ is
symmetric, an involution ($H^2=I$), and therefore orthogonal.

**Mapping $x$ onto $e^1$** [S4 Lem. 4.49]. If $x\parallel e^1$ take $Q=I$.
Otherwise set
$$\lambda=\mathrm{sign}(x_1)\|x\|_2\quad(\mathrm{sign}\,0:=1),\qquad v=\frac{x+\lambda e^1}{\|x+\lambda e^1\|_2},$$
for which $\|x+\lambda e^1\|_2^2=2\|x\|_2^2+2|x_1|\|x\|_2$ and
$$Hx=-\lambda e^1 .$$
**The sign matters** [S4 Rem. 4.50]: $\lambda=-\mathrm{sign}(x_1)\|x\|_2$ also
maps $x$ into $\mathrm{span}\{e^1\}$, but it is unstable when $x$ is nearly
parallel to $e^1$ ($|x_1|\approx\|x\|_2$): $x+\lambda e^1$ then cancels. Choose
the sign that makes the first entry a sum of like-signed terms.

**The algorithm** [S4 Alg. 4.51]: apply $Q_1$ to the whole matrix, then
$Q_2=\begin{psmallmatrix}1&0\\0&\widetilde Q_1\end{psmallmatrix}$ to the trailing
$(m-1)\times(n-1)$ block, and so on. $Q$ is stored **implicitly** as the
reflectors $v_1,\ldots,v_{n-1}$, never formed; $Q^\top b$ is $n$ applications of
$H_i$, each $O(m)$.

Worked example (`qr.cpp`):
$A=\begin{psmallmatrix}12&-51&4\\6&167&-68\\-4&24&-41\end{psmallmatrix}$.
Column 1: $\|x\|_2=14$, $x_1=12>0$ so $\lambda=14$, $x+\lambda e^1=(26,6,-4)$,
and $H_1x=-14e^1$. Continuing gives
$R=\begin{psmallmatrix}-14&-21&14\\&-175&70\\&&35\end{psmallmatrix}$; with the
opposite sign convention all the signs flip, so quote $|r_{ii}|=14,175,35$.

## 4. QR with column pivoting [S4 §4.7.4] (CSE)

Rank-revealing variant: at each step move the column of largest remaining norm
to the front, producing
$$AP=QR\qquad\text{with }|r_{11}|\ge|r_{22}|\ge\cdots$$
for a permutation $P$. When $A$ is (numerically) rank deficient the trailing
$r_{ii}$ collapse, so the numerical rank can be read off the diagonal: the cheap
alternative to an SVD (note [07](07-least-squares-and-svd.md)), and the basis of
$\texttt{qr}(A,\texttt{'vector'})$ in MATLAB and `scipy.linalg.qr(..., pivoting=True)`.
(`givens.qr_column_pivoting`.)

## 5. Givens rotations [S4 §4.7.5] (CSE)

Zero one entry at a time instead of a whole column. $G(i,j,\theta)$ is the
identity with $c=\cos\theta$ in positions $(i,i),(j,j)$ and $\pm s=\pm\sin\theta$
in $(i,j),(j,i)$: a rotation in $\mathrm{span}\{e^i,e^j\}$, hence orthogonal
[S4 Lem. 4.53(i)].

- $AG$ differs from $A$ only in columns $i,j$, and $G^\top A$ only in rows $i,j$
  [S4 Lem. 4.53(ii)–(iii)].
- For $i\ne j$, $i'\ne i$ there is a $G(i,i',\theta)$ with $(G^\top A)_{ij}=0$
  [S4 Lem. 4.53(iv)]: the requirement is $sA_{i'j}=cA_{ij}$, so take $c=1,s=0$
  if $A_{ij}=0$, and otherwise $\theta\in(0,\pi)$ with
  $\cot\theta=A_{i'j}/A_{ij}$.

A full QR needs $O(n^2)$ Givens rotations and is **more expensive than
Householder for a dense matrix** [S4 §4.7.5]. Its use is matrices that are
already mostly zero.

**Upper Hessenberg matrices** ($a_{ij}=0$ for $i>j+1$) are the case that matters
[S4 Ex. 4.54–4.55]: only the $n-1$ subdiagonal entries need to be annihilated,
so the QR factorisation costs **$O(n^2)$**, and $O(n)$ for a symmetric
Hessenberg (= tridiagonal) matrix. Worked example [S4 Ex. 4.54], with
$c=s=1/\sqrt2$ in the first rotation:
$$A=\begin{pmatrix}1&1&1\\1&0&1\\0&1&1\end{pmatrix}
\ \xrightarrow{\ G(1,2)^\top\ }\ \begin{pmatrix}\sqrt2&\tfrac1{\sqrt2}&\sqrt2\\0&-\tfrac1{\sqrt2}&0\\0&1&1\end{pmatrix}
\ \xrightarrow{\ G(2,3)^\top\ }\ R=\begin{pmatrix}\sqrt2&\tfrac1{\sqrt2}&\sqrt2\\0&\sqrt{\tfrac32}&\sqrt{\tfrac23}\\0&0&-\tfrac1{\sqrt3}\end{pmatrix}.$$
Two rotations for a $3\times3$, as promised. The diagonal
$\big(\sqrt2,\ \sqrt3/\sqrt2,\ -1/\sqrt3\big)$ is the one [S4] prints; the two
entries above the diagonal in the first row come out as $1/\sqrt2$ and $\sqrt2$
here, against the $2/\sqrt2$ that the script's typesetting shows in position
$(1,2)$: recomputing $G(1,2)^\top A$ by hand gives $\tfrac1{\sqrt2}(1+0)$, so
$1/\sqrt2$ is right. `test_givens.py` checks the whole factorisation against
$A=QR$ and against `numpy.linalg.qr`.

**And $RQ$ is Hessenberg again** [S4 §4.7.5]. Writing
$Q^\top=G(n-1,n)\cdots G(1,2)$, the product $(Q^\top A)Q$ multiplies from the
right by $G(1,2)^\top,\ldots$, and each such multiplication introduces exactly
one new non-zero, in positions $(2,1),(3,2),\ldots$: the subdiagonal. This is
precisely what makes the QR *algorithm* affordable: reduce once to Hessenberg
in $O(n^3)$, then every iteration is $O(n^2)$ (note
[09](09-eigenvalue-problems.md)).

## Pitfalls

- Classical Gram–Schmidt on anything ill-conditioned. If you must use
  Gram–Schmidt, use MGS and re-orthogonalise ("twice is enough").
- The wrong Householder sign: $v=x-\|x\|e^1$ when $x_1>0$ cancels
  [S4 Rem. 4.50].
- Forming $Q$ explicitly when only $Q^\top b$ is needed. Apply the reflectors.
- Using Givens for a dense QR. It is more expensive than Householder; its niche
  is Hessenberg, tridiagonal and banded matrices [S4 §4.7.5].
- Assuming $R$ is unique. It is only up to the signs of the diagonal
  [S4 Thm 4.43], so quote $|r_{ii}|$ when comparing implementations.
- Assuming "$Q$ orthogonal" holds for a computed CGS factor. $\|A-QR\|$ is tiny;
  $\|Q^\top Q-I\|$ need not be [S15].

## Exam-style questions

The Visual Computing papers stop before Householder and Givens, so only item 1
is attested (S2a 2.5); the rest are ours, against [S4] §4.7.

1. *(S2a 2.5, 2024W: true or false / fill in)*
   (i) If $A=QR$ then $Q$ has to be orthogonal. **True** (by definition of a QR
   factorisation, [S4 Def. 4.42]).
   (ii) Every invertible $A\in\mathbb R^{n\times n}$ has a QR factorisation.
   **True** [S4 Thm 4.43], unlike LU, which needs a pivot.
   (iii) Fill in: computing the QR factorisation of $A\in\mathbb R^{n\times n}$
   has complexity $O(n^3)$ [S4 Rem. 4.45], about twice LU.
   (iv) Fill in: $Q\in\mathbb R^{n\times n}$ is orthogonal if $Q^\top Q=I$.
2. *(ours)* Why are orthogonal transformations the right tool in numerics? Give
   the one-line argument and the two consequences.
   $\|Qx\|_2=\|x\|_2$, so the relative-error amplification factor is exactly 1
   [S4 Rem. 4.41]; hence $\kappa_2(Q)=1$ and $\kappa(Q^\top A)=\kappa(A)$
   [S4 Thm 4.40(iii)].
3. *(ours)* Construct the Householder reflection mapping $x=(3,4)^\top$ into
   $\mathrm{span}\{e^1\}$, with [S4]'s sign convention.
   $\|x\|_2=5$, $x_1=3>0$ so $\lambda=5$; $x+\lambda e^1=(8,4)$, normalised
   $v=(8,4)/\sqrt{80}$, and $Hx=-\lambda e^1=(-5,0)^\top$. The other sign would
   give $v=(-2,4)$, which cancels when $x$ is nearly parallel to $e^1$
   [S4 Rem. 4.50].
4. *(ours)* State the three properties of $H=I-2vv^\top$ and prove orthogonality
   from the other two.
   Symmetric, involutory, orthogonal [S4 Lem. 4.48]. From $H^\top=H$ and
   $H^2=I$: $H^\top H=H^2=I$.
5. *(ours: CSE)* Why does one reduce a matrix to Hessenberg form before running
   the QR algorithm?
   A Hessenberg QR factorisation needs only $n-1$ Givens rotations, so it costs
   $O(n^2)$ instead of $O(n^3)$; and $RQ$ is Hessenberg again, so the structure
   persists over the iteration [S4 Ex. 4.55, §7.6.1]. Total
   $O(n^3)+O(n)\cdot O(n^2)=O(n^3)$ instead of $O(n^4)$.
6. *(ours: CSE)* When would you choose QR with column pivoting over a plain QR?
   When $A$ may be rank deficient: the pivoted factorisation orders
   $|r_{11}|\ge|r_{22}|\ge\cdots$, so a collapse in the diagonal reveals the
   numerical rank at $O(mn^2)$ instead of the $O(mn^2)$-with-a-much-bigger-constant
   of an SVD [S4 §4.7.4].

## Implementation

`src/py/qr_svd.py`: `gram_schmidt_classical`, `gram_schmidt_modified`,
`householder_vector` / `householder_qr` (implicit $Q$), `qr_solve`,
`power_method`, `qr_algorithm`, `jacobi_svd`, `low_rank`, `cond2`.

`src/py/givens.py` (new): `givens_rotation` ([S4 Lem. 4.53]), `apply_givens_left`
/ `apply_givens_right`, `givens_qr`, `hessenberg_qr` (the $O(n^2)$ version),
`rq_product` (checks $RQ$ is Hessenberg again), `qr_column_pivoting`
([S4 §4.7.4]).

Tests: `test_qr_svd.py` (against `numpy.linalg.qr/lstsq/eigvalsh/svd/matrix_rank`;
the orthogonality-loss hierarchy of the table above) and `test_givens.py` (the
$3\times3$ Hessenberg example of [S4 Ex. 4.54] to 12 digits; the
$O(n)$-rotations count of [S4 Ex. 4.55]; $RQ$ Hessenberg; pivoted QR revealing
the rank of a deliberately rank-deficient matrix, cross-checked against
`scipy.linalg.qr(pivoting=True)`).

`src/cpp/qr.cpp`: Householder QR with stored reflectors, implicit $Q^\top b$,
least squares; $|r_{ii}|=14,175,35$ on the classic $3\times3$, an exact quadratic
fit, the line through $(0,1),(1,2),(2,4)$ with residual $\sqrt{1/6}$, a
degree-12 Vandermonde.
