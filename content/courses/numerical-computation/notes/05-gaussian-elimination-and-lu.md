# 05 Gaussian elimination and LU

[S4] §4.1–4.6. Solve $Ax=b$ by factoring once ($O(n^3)$) and substituting per
right-hand side ($O(n^2)$). The chapter's real subject is **structure**: what
banded, SPD, skyline and sparse matrices buy you, and what pivoting and
reordering cost. Iterative methods are note
[10](10-iterative-linear-systems.md); the QR half of [S4] §4 is note
[06](06-qr-factorisation.md). Implementation: `src/py/linsolve.py`,
`src/py/banded.py`, `src/cpp/lu.cpp`.

In MATLAB the solve is `A\b`, in Python `numpy.linalg.solve`; both call LAPACK
[S4 Rem. 4.1].

## 1. Triangular systems [S4 §4.1]

$A$ is **upper triangular** if $A_{ij}=0$ for $j<i$, **lower triangular** if
$A_{ij}=0$ for $j>i$, and **normalised** lower triangular if additionally
$A_{ii}=1$. Forward substitution for $Lx=b$ [S4 Alg. 6] and back substitution
for $Ux=b$ [S4 Alg. 7] each cost $\tfrac{n^2}2$ multiplications and as many
additions, i.e. $O(n^2)$ [S4 Exercise 4.2]. Sums of lower triangular matrices
and products of lower triangular matrices are lower triangular
[S4 Exercise 4.3]. Row-oriented access reads $L$ by rows, column-oriented by
columns: the same flops with different memory behaviour [S4 Rem. 4.4–4.5].

## 2. Gaussian elimination is an LU factorisation [S4 §4.2]

Step $k$: for $i>k$, $m_{ik}=a_{ik}/a_{kk}$, then
$\mathrm{row}_i\leftarrow\mathrm{row}_i-m_{ik}\,\mathrm{row}_k$ [S4 Alg. 8].
Collecting the multipliers,
$$A=LU,\qquad L=\begin{pmatrix}1\\ m_{21}&1\\ \vdots&&\ddots\\ m_{n1}&\cdots&m_{n,n-1}&1\end{pmatrix},\quad U\ \text{upper triangular}\qquad\text{[S4 (4.8)]}.$$

Solve in three steps [S4 §4.3]: factor $A=LU$; forward-substitute $Ly=b$;
back-substitute $Ux=y$. `lu(A)` in MATLAB, `scipy.linalg.lu` in Python
[S4 Rem. 4.10].

**Cost** [S4 Rem. 4.11]: the factorisation dominates at
$\tfrac23n^3+O(n^2)$ flops; each substitution is $O(n^2)$. For $M$ right-hand
sides the total is $\tfrac23n^3+2Mn^2$: factor once, substitute $M$ times.
**Never form $A^{-1}$** to solve a system: about $2n^3$ flops and worse rounding.

Existence without pivoting: $A=LU$ exists iff all leading principal minors are
non-zero; strictly diagonally dominant and SPD matrices never need pivoting
*([S16]; [S4] gives only the counterexample of §4.4)*.

**Determinant** from LU: $\det A=(-1)^{\#\mathrm{swaps}}\prod_k u_{kk}$
(`linsolve.determinant`).

### Crout's algorithm [S4 §4.3.1]

A different traversal of the same $n^2$ equations
$a_{ik}=\sum_{j\le\min(i,k)}l_{ij}u_{jk}$ [S4 (4.9)], in the order
$(1,1),(1,2),\ldots,(1,n)$, then $(2,1),(3,1),\ldots,(n,1)$, then row 2, then
column 2, and so on. It computes $L$ and $U$ **entry by entry** rather than by
sweeping the trailing submatrix [S4 Alg. 9]:

```
for i = 1..n:
    for k = i..n:      u[i,k] := a[i,k] - sum_{j<i} l[i,j]*u[j,k]
    for k = i+1..n:    l[k,i] := (a[k,i] - sum_{j<i} l[k,j]*u[j,i]) / u[i,i]
```

Same flop count, different memory-access pattern (hence different timings): the
reason [S4] bothers with it [S4 footnote 4]. Overwriting $A$ in place is
[S4 Alg. 10]. "Crout's algorithm computes an LU factorisation" was a true/false
item in S2a 2.5b.

### Banded matrices [S4 §4.3.2]

$A$ has upper bandwidth $q$ and lower bandwidth $p$ if $a_{ik}=0$ whenever
$i>k+p$ or $k>i+q$.

**Theorem** [S4 Thm 4.12]. If such an $A$ is invertible and has an LU
factorisation then $L$ has lower bandwidth $p$, $U$ has upper bandwidth $q$, and
$$\text{factorisation } O(npq),\qquad Ly=b\ \ O(np),\qquad Ux=y\ \ O(nq).$$
For a tridiagonal matrix ($p=q=1$) that is $O(n)$ throughout: the Thomas
algorithm used for cubic splines (note [01](01-polynomial-interpolation.md)).

### Cholesky [S4 §4.3.3]

$A$ is **symmetric positive definite** (SPD) if $A_{ij}=A_{ji}$ and
$x^\top Ax>0$ for all $x\ne0$; equivalently, symmetric with all eigenvalues
positive [S4 Rem. 4.13]. Then
$$A=CC^\top,\qquad C\ \text{lower triangular, } C_{ii}>0\ \text{(not normalised)}\qquad\text{[S4 (4.10)]}$$
computed like Crout [S4 Exercise 4.14]:
$$c_{jj}=\sqrt{a_{jj}-\sum_{k<j}c_{jk}^2},\qquad c_{ij}=\frac1{c_{jj}}\Big(a_{ij}-\sum_{k<j}c_{ik}c_{jk}\Big)\ (i>j).$$
Three facts, all examinable:

- **The cost is about half that of LU** [S4 Rem. 4.16]: only half the entries
  are computed. (S2a 2.5a asks the reverse as a false statement.) Concretely
  $\tfrac13n^3$ against $\tfrac23n^3$.
- A banded SPD $A$ with $p=q$ has a banded $C$ with the same bandwidth
  [S4 Rem. 4.15].
- No pivoting is needed, and a negative or zero radicand is the cheapest
  possible test that a symmetric matrix is **not** positive definite.

`chol` in MATLAB [S4 Rem. 4.17]. Example:
$\begin{psmallmatrix}4&12&-16\\12&37&-43\\-16&-43&98\end{psmallmatrix}=CC^\top$
with $C=\begin{psmallmatrix}2\\6&1\\-8&5&3\end{psmallmatrix}$.

Note the convention: [S4] writes $A=CC^\top$ with $C$ lower triangular. Many
texts write $A=LL^\top$ or $A=R^\top R$; same object.

### Skyline matrices [S4 §4.3.4]

$A$ is a **skyline** matrix if for each $i$ there are $p_i,q_i$ with
$$a_{ij}=0\quad\text{if } j<i-p_i\ \text{ or }\ i<j-q_j\qquad\text{[S4 (4.11)]}.$$
**Theorem** [S4 Thm 4.18]: the factors inherit the pattern, $l_{ij}=0$ for
$j<i-p_i$ and $u_{ij}=0$ for $i<j-q_j$. So the profile can be stored and only
the non-zeros computed. [S4 Fig. 4.4–4.5] contrast a skyline matrix (pattern
preserved) with an arrowhead matrix whose LU factors are completely full: that
loss is **fill-in**.

## 3. Pivoting [S4 §4.4]

$A=\begin{psmallmatrix}0&1\\3&2\end{psmallmatrix}$ is invertible but has **no**
LU factorisation with normalised $L$ [S4 Exercise 4.21]. Try it: $l_{11}u_{11}=0$
forces $u_{11}=0$, and then column 1 cannot be reproduced. Swapping the rows
fixes it.

**Theorem** [S4 Thm 4.22]. For every invertible $A$ there is a permutation
matrix $P$ with $PA=LU$. Row pivoting [S4 Alg. 11] picks, at step $k$, the row
$p\ge k$ maximising $|a_{pk}|$; the resulting $L$ satisfies $|l_{ij}|\le1$ for
all $i,j$ [S4 Thm 4.26]. MATLAB and Python return $L,U,P$ with $LU=PA$ and do at
least some pivoting [S4 Rem. 4.27]. Given $LU=PA$, solve $Ly=Pb$ then $Ux=y$
[S4 Exercise 4.28].

**Why the largest pivot** [S4 §4.4.3]. Take
$A=\begin{psmallmatrix}\varepsilon&1\\1&1\end{psmallmatrix}$ with
$\varepsilon=10^{-20}$. Exactly,
$L=\begin{psmallmatrix}1&0\\\varepsilon^{-1}&1\end{psmallmatrix}$,
$U=\begin{psmallmatrix}\varepsilon&1\\0&1-\varepsilon^{-1}\end{psmallmatrix}$;
in 16-digit arithmetic $1-10^{20}$ rounds to $-10^{20}$, and solving
$LUx=(1,0)^\top$ returns $x=(0,1)$ instead of the correct $(-1,1)$: a completely
wrong answer for a matrix with $\kappa\approx2.6$. The heuristic: a small pivot
makes the entries of $L$ large, so the substitutions produce large intermediate
values; if the answer is moderate, it was obtained by subtracting similar
numbers, i.e. cancellation (note
[04](04-conditioning-and-error-analysis.md)). Partial pivoting bounds $L$ by 1;
it does **not** control $U$. Full pivoting does, at $O(n^3)$ extra comparisons,
and is usually not worth it [S4 §4.4.3].

*(Background [S12, S16], not in [S4]: with partial pivoting
$\|\Delta A\|_\infty\le\gamma_{3n}\rho_n\|A\|_\infty$ where the growth factor
$\rho_n=\max|u_{ij}|/\max|a_{ij}|\le2^{n-1}$; the bound is attained by a
contrived matrix but $\rho_n$ behaves like $n^{2/3}$ in practice.)*

## 4. Condition number of a matrix [S4 §4.5]

Induced norms [S4 (4.12), Exercise 4.29]:
$$\|A\|_\infty=\max_i\sum_j|a_{ij}|\ \text{(row sums)},\quad \|A\|_1=\max_j\sum_i|a_{ij}|\ \text{(column sums)},\quad \|A\|_2^2=\lambda_{\max}(A^\top A),$$
submultiplicative, $\|AB\|\le\|A\|\|B\|$ [S4 Exercise 4.30]. Then
$\kappa(A)=\|A\|\|A^{-1}\|$ and everything in note
[04](04-conditioning-and-error-analysis.md) §2 applies.

## 5. Fill-in and ordering strategies [S4 §4.6] (CSE)

Take the skyline matrix of [S4 Fig. 4.5]. Reversing the ordering of the unknowns
destroys the skyline property, and the Cholesky factor becomes a *full* lower
triangular matrix. **The ordering of the unknowns decides the cost**, and
choosing it is a graph problem on the adjacency graph $G(A)$.

**Reverse Cuthill–McKee** [S4 Alg. 12–13] aims at a small bandwidth, cheaply:
number a node's unnumbered neighbours as soon as possible.

```
Cuthill-McKee:
  push a starting node v into a FIFO
  while FIFO not empty:
      pop v, assign it the next number
      push v's unnumbered neighbours, in ascending order of degree

Reverse Cuthill-McKee:
  run Cuthill-McKee from a (pseudo-)peripheral start node, then reverse the order
```
A greedy, locally optimal heuristic. Reversing provably never makes the envelope
worse: $|\mathrm{Env}(P_{\mathrm{RCM}}^\top AP_{\mathrm{RCM}})|\le|\mathrm{Env}(P_{\mathrm{CM}}^\top AP_{\mathrm{CM}})|$
[S4 §4.6.2]. Peripheral start nodes are hard to find, so a pseudo-peripheral one
is used.

**Minimum degree** [S4 Alg. 14] attacks fill-in directly rather than bandwidth:
repeatedly eliminate a node of minimum degree in the (progressively eliminated)
graph. Finding the truly fill-minimising order is hard; this is again greedy, and
in practice the cheaper **approximate minimum degree** is used [S4 Rem. 4.20].

**The numbers to remember** [S4 Ex. 4.37], the 2-D Poisson matrix
$A\in\mathbb R^{900\times900}$ from `gallery('poisson',30)`, 5 non-zeros per row:

| ordering | non-zeros in the Cholesky factor |
|---|---|
| lexicographic | 27 029 |
| reverse Cuthill–McKee | 19 315 |
| (approximate) minimum degree | **10 042** |

against $\mathrm{nnz}(A)=4380$ and 2 640 in the lower triangle. A factor 2.7 in
memory and time, from relabelling alone. Modern sparse solvers do this as a
preprocessing step [S4 Rem. 4.20]. (`ordering.reverse_cuthill_mckee` and
`ordering.symbolic_cholesky_nnz` reproduce the first two counts exactly;
`ordering.minimum_degree`, the exact greedy [S4 Alg. 14], gives 10 351, since
[S4]'s 10 042 comes from *approximate* minimum degree with different
tie-breaking.)

**Theorem 4.35** [S4] is the structural reason: for SPD $A$ with Cholesky factor
$C$, $c_{ij}$ can be non-zero only if there is a path in $G(A)$ from $i$ to $j$
through nodes numbered below $\min(i,j)$, so the sparsity pattern of $A$ is
"roughly inherited", and how roughly depends on the numbering.

## 6. Worked example

$$A=\begin{pmatrix}2&1&1\\4&-6&0\\-2&7&2\end{pmatrix},\qquad b=\begin{pmatrix}5\\-2\\9\end{pmatrix}.$$
Column 1: $|4|>|2|$, swap rows 1 and 2. Multipliers $m_{21}=2/4=0.5$,
$m_{31}=-2/4=-0.5$. After elimination the rows are $(4,-6,0)$, $(0,4,1)$,
$(0,4,2)$. Column 2: pivot 4, no swap, $m_{32}=1$, row 3 becomes $(0,0,1)$.
$$U=\begin{pmatrix}4&-6&0\\&4&1\\&&1\end{pmatrix},\quad L=\begin{pmatrix}1\\0.5&1\\-0.5&1&1\end{pmatrix},\quad Pb=(-2,5,9)^\top.$$
$Ly=Pb$ gives $y=(-2,6,2)$; $Ux=y$ gives $x_3=2$, $x_2=(6-2)/4=1$,
$x_1=(-2+6)/4=1$. $\det A=-(4\cdot4\cdot1)=-16$ (one swap). Reproduced by
`linsolve.py` `__main__` and `lu.cpp`.

## Pitfalls

- Eliminating without pivoting when a pivot is small but non-zero: the
  $\varepsilon=10^{-20}$ example above, where $\kappa$ is tiny and the answer is
  still garbage.
- Forming $A^{-1}$: three times the flops and worse accuracy.
- Applying Cholesky to a merely symmetric matrix. It breaks down, which is the
  point: that is the test.
- Saying Cholesky costs *twice* LU. It costs about **half** [S4 Rem. 4.16].
- Treating a skyline or arrowhead matrix as banded: the bandwidth is $n$ and the
  $O(npq)$ bound says nothing [S4 Fig. 4.4].
- Expecting a sparse $A$ to give sparse factors. Only if the pattern is skyline
  or the ordering is good; otherwise fill-in [S4 §4.6].
- Forgetting the permutation when reusing a factorisation: $LU=PA$, so
  $Ly=Pb$, not $Ly=b$.

## Exam-style questions

Modelled on S2a 2.1–2.2, F2 2.1, F3 2.3a and the true/false blocks; see
[00](00-exam-focus.md).

1. *(S2a 2.1, 2024W)* $A=\begin{psmallmatrix}2&0&0\\4&3&0\\6&6&6\end{psmallmatrix}$.
   (a) Compute the LU factorisation with normalised $L$. (b) For general
   $B\in\mathbb R^{n\times n}$, what does the LU factorisation cost, and what
   does back substitution on $Ux=b$ cost? (c) Given $B=LU$, how do you solve
   $Bx=b$ in $O(n^2)$?
   (a) $A$ is already lower triangular, so $U=\mathrm{diag}(2,3,6)$ and
   $L=\begin{psmallmatrix}1&&\\2&1&\\3&2&1\end{psmallmatrix}$
   (check: $l_{21}u_{11}=2\cdot2=4$ ✓, $l_{31}u_{11}=6$ ✓,
   $l_{31}u_{12}+l_{32}u_{22}=0+2\cdot3=6$ ✓).
   (b) $O(n^3)$, precisely $\tfrac23n^3$; back substitution $O(n^2)$
   [S4 Rem. 4.11].
   (c) Forward-substitute $Ly=b$, back-substitute $Ux=y$: $O(n^2)+O(n^2)$.
2. *(S2a 2.2, 2024W; F3 2.3a)* $A=\begin{psmallmatrix}0&2\\4&1\end{psmallmatrix}$.
   (a) Prove it has no LU factorisation. (b) Does it have a Cholesky
   factorisation? (c) Compute the Cholesky factorisation of
   $B=\begin{psmallmatrix}4&2\\2&4\end{psmallmatrix}$.
   (a) $A=LU$ with $L$ normalised means $a_{11}=1\cdot u_{11}=0$, so $u_{11}=0$;
   but then $a_{21}=l_{21}u_{11}=0\ne4$. Contradiction. Swapping rows gives
   $\begin{psmallmatrix}4&1\\0&2\end{psmallmatrix}$, already triangular.
   (b) No: Cholesky needs SPD and $A$ is not even symmetric.
   (c) $c_{11}=\sqrt4=2$, $c_{21}=2/2=1$, $c_{22}=\sqrt{4-1}=\sqrt3$, so
   $C=\begin{psmallmatrix}2&0\\1&\sqrt3\end{psmallmatrix}$ and $B=CC^\top$.
3. *(S2a 2.5: true or false / fill in)*
   (i) Cholesky costs twice as much as LU. **False**, about half
   [S4 Rem. 4.16].
   (ii) Crout's algorithm computes an LU factorisation. **True**.
   (iii) Gaussian elimination reduces $Ax=b$ to upper triangular form and then
   back-substitutes. **True**.
   (iv) Fill in: solving $Ax=b$ with Gaussian elimination has complexity
   $O(n^3)$ (precisely $\tfrac23n^3$ for the factorisation).
4. *(ours)* State the banded cost theorem and specialise it to a tridiagonal
   matrix.
   $L$ has lower bandwidth $p$, $U$ upper bandwidth $q$; factorisation $O(npq)$,
   substitutions $O(np)$ and $O(nq)$ [S4 Thm 4.12]. Tridiagonal: $p=q=1$, so
   everything is $O(n)$.
5. *(ours: CSE)* Why does the ordering of the unknowns matter for a sparse SPD
   matrix, and what do RCM and minimum degree each optimise?
   The Cholesky factor inherits the pattern only up to fill-in, and fill-in
   depends on the numbering [S4 Thm 4.35]. RCM minimises the *bandwidth*
   (envelope) as a proxy; minimum degree greedily minimises the *fill* itself.
   On the $900\times900$ 2-D Poisson matrix: 27 029 non-zeros lexicographic,
   19 315 with RCM, 10 042 with minimum degree [S4 Ex. 4.37].
6. *(ours)* Why does partial pivoting make Gaussian elimination usable, and what
   does it *not* control?
   It bounds $|l_{ij}|\le1$ [S4 Thm 4.26], so no huge intermediate values and no
   cancellation in the substitutions. It does not bound the entries of $U$;
   full pivoting would, at $O(n^3)$ extra comparisons [S4 §4.4.3].

## Implementation

`src/py/linsolve.py`: `gauss_elim`, `lu_decompose` / `lu_solve` / `lu_unpack`,
`determinant`, `cholesky` / `cholesky_solve`, `jacobi`, `gauss_seidel`, `sor`,
`sor_optimal_omega`, `conjugate_gradient` (with `matvec` for matrix-free use),
`iteration_matrix`, `power_iteration`, `poisson_1d` (the last six belong to note
[10](10-iterative-linear-systems.md)).

`src/py/banded.py` (new): `crout_lu` / `crout_lu_inplace` ([S4 Alg. 9–10]),
`bandwidths`, `banded_lu` / `banded_solve` ([S4 Thm 4.12], with an operation
counter that verifies the $O(npq)$ claim), `banded_cholesky` ([S4 Rem. 4.15]),
`skyline_profile` / `is_skyline_preserved` ([S4 Thm 4.18]).

`src/py/ordering.py` (new, [S4 §4.6], CSE): `adjacency_graph`, `cuthill_mckee`,
`pseudo_peripheral_node`, `reverse_cuthill_mckee` ([S4 Alg. 12–13]),
`minimum_degree` ([S4 Alg. 14]), `symbolic_cholesky_nnz`, `poisson_2d_pattern`.

Tests: `test_linsolve.py` (vs `numpy.linalg`, `scipy.linalg.lu`) and
`test_banded.py` (Crout against the sweeping LU; the $O(npq)$ operation count;
banded Cholesky bandwidth preservation; the skyline example of [S4 Fig. 4.5];
the $\varepsilon=10^{-20}$ pivoting failure of [S4 §4.4.3]; and the S2a/F2 exam
items above) and `test_ordering.py` (the fill-in counts 27 029 / 19 315 of
[S4 Ex. 4.37] exactly, minimum degree 10 351 against [S4]'s 10 042; RCM
against `scipy.sparse.csgraph.reverse_cuthill_mckee`).

`src/cpp/lu.cpp`: packed LU with partial pivoting, solve, determinant; the
$3\times3$ example above ($x=(1,1,2)$, $\det=-16$), a pivoting case, an $n=200$
residual/error/growth-factor check, singular detection.
