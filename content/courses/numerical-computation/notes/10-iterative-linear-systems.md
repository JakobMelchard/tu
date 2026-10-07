# 10 Iterative solution of linear systems

[S4] §8: **the whole chapter is marked (CSE)**, so it is examined here and in no
public past paper ([00](00-exam-focus.md)). Solve $Ax=b$ for large sparse
$A\in\mathbb R^{N\times N}$ using **only** the matrix–vector product $x\mapsto Ax$
[S4 §8]. The reason is memory: for a sparse $A$ a matvec is cheap, but the
Cholesky factor can need far more memory than $A$ itself (note
[05](05-gaussian-elimination-and-lu.md) §5). Implementation:
`src/py/linsolve.py`, `src/py/gmres.py`, `src/cpp/cg.cpp`.

[S4] gives CG four pages and GMRES three. Two free companions, both cited only:
Shewchuk's *Conjugate Gradient Without the Agonizing Pain* [S17] for the
geometry behind §3, and Saad's *Iterative Methods for Sparse Linear Systems*
[S18] for the Arnoldi and GMRES details behind §4.

Two inner products are used [S4 §8]:
$$(x,y)_2=x^\top y,\qquad (x,y)_A=x^\top Ay,\qquad \|x\|_A=\sqrt{(x,x)_A}$$
the second is an inner product and $\|\cdot\|_A$ a norm exactly when $A$ is SPD
[S4 Exercise 8.1].

## 1. The three families [S4 §8]

**Basic (stationary) iterative methods**, written as $x_{k+1}=x_k+M^{-1}(b-Ax_k)$:

| method | $M$ | update |
|---|---|---|
| Richardson | $I$ | $x_{k+1}=x_k+(b-Ax_k)$ |
| Jacobi | $D=\mathrm{diag}(A)$ | $x_{k+1}=x_k+D^{-1}(b-Ax_k)$ |
| Gauss–Seidel | $L+D$ | $x_{k+1}=x_k+(L+D)^{-1}(b-Ax_k)$ |

with $L$ the strict lower triangle. Fixed points solve $Ax=b$ in all three cases.
[S4]'s verdict is blunt: **easy to implement, do not always converge, and slow
when they do**: damping helps, see the literature. That is the entire treatment;
the course does not develop a convergence theory for them, so the material in
§2 below is background, not examinable content.

**Gradient methods**: rewrite as minimising
$\phi(x)=\tfrac12(Ax,x)-(b,x)$ and descend. The search direction is
$d_k=-\nabla\phi(x_k)=b-Ax_k=r_k$, the residual, and by
[S4 §6.8.1] (note [08](08-nonlinear-equations-and-newton.md)) the optimal step is
$$\alpha_k=\frac{(r_k,r_k)_2}{(r_k,r_k)_A}.$$
Consecutive search directions are $(\cdot,\cdot)_2$-orthogonal, which is exactly
the zig-zag that makes steepest descent slow for ill-conditioned $A$
[S4 Lem. 6.23].

**Krylov methods**: minimise the error or the residual over
$\mathcal K_\ell=\mathrm{span}\{r_0,Ar_0,\ldots,A^{\ell-1}r_0\}$.

- **CG** minimises the error in $\|\cdot\|_A$; search directions are
  $(\cdot,\cdot)_A$-orthogonal. **Needs $A$ SPD.**
- **GMRES** minimises the residual in $\|\cdot\|_2$. **Needs only $A$ invertible.**

Why Krylov spaces at all [S4 §8.1]: by Cayley–Hamilton,
$p(A)=A^N+\alpha_{N-1}A^{N-1}+\cdots+\alpha_0I=0$ for the characteristic
polynomial, so
$$A^{-1}=-\frac1{\alpha_0}\Big(A^{N-1}+\alpha_{N-1}A^{N-2}+\cdots+\alpha_1I\Big)\qquad\text{[S4 (8.1)]}$$
**$A^{-1}b$ lies in the Krylov space of dimension $N$**. Finding a good
approximation in a low-dimensional Krylov space is therefore not a heuristic.

## 2. Stationary methods in detail *(background, not in [S4])*

Kept because the exercises use them and because they are the baseline CG is
measured against. Split $A=P-N$, iterate $Px^{k+1}=Nx^k+b$:
$$x^{k+1}=Mx^k+P^{-1}b,\qquad M=I-P^{-1}A,\qquad e^{k}=M^ke^0 .$$
So the iteration converges for every $x^0$ **iff** the spectral radius
$\rho(M)<1$, with asymptotic rate $\rho(M)$ per step; $\|M\|<1$ in any induced
norm is sufficient. SOR($\omega$) uses $P=\tfrac1\omega D+L$.

Classical results [S16]: strictly diagonally dominant $\Rightarrow$ Jacobi and
Gauss–Seidel converge; $A$ SPD $\Rightarrow$ Gauss–Seidel converges and SOR
converges iff $0<\omega<2$ (Ostrowski–Reich; $\rho(M_\omega)\ge|\omega-1|$ by
Kahan). For consistently ordered matrices
$\rho(M_{GS})=\rho(M_J)^2$ and
$\omega_{\mathrm{opt}}=\tfrac2{1+\sqrt{1-\rho(M_J)^2}}$,
$\rho(M_{\omega_{\mathrm{opt}}})=\omega_{\mathrm{opt}}-1$.

1-D Poisson $T_n=\mathrm{tridiag}(-1,2,-1)$: eigenvalues
$2-2\cos\tfrac{k\pi}{n+1}$, so $\rho(M_J)=\cos\tfrac\pi{n+1}\approx1-\tfrac{\pi^2}{2(n+1)^2}$.
Jacobi and Gauss–Seidel need $O(n^2)$ iterations, SOR $O(n)$. Demo ($n=20$,
tol $10^{-8}$, `linsolve.py`): Jacobi 1662, Gauss–Seidel 832,
SOR($\omega_{\mathrm{opt}}=1.741$) 80, **CG 10**.

## 3. Conjugate gradients [S4 §8.1]

$A$ SPD. Define the Krylov space
$\mathcal K_\ell(A,x_0)=\mathrm{span}\{r_0,Ar_0,\ldots,A^{\ell-1}r_0\}$
[S4 Def. 8.2] with $r_0=b-Ax_0$. **Lemma 8.3** [S4] gives the three equivalent
characterisations of $x_\ell\in x_0+\mathcal K_\ell$: it minimises
$\|x^\ast-x\|_A$; it minimises $\phi$; and its error is
$(\cdot,\cdot)_A$-orthogonal to $\mathcal K_\ell$.

Working the orthogonality conditions into a two-term recurrence gives
[S4 Alg. 27, Rem. 8.4]:

```
r_0 := b - A x_0;   d_0 := r_0
for l = 1, 2, ... :
    alpha_l  := ||r_{l-1}||_2^2 / ||d_{l-1}||_A^2
    r_l      := r_{l-1} - alpha_l A d_{l-1}
    x_l      := x_{l-1} + alpha_l d_{l-1}
    beta_{l-1} := - ||r_l||_2^2 / ||r_{l-1}||_2^2
    d_l      := r_l - beta_{l-1} d_{l-1}
```

[S4]'s $\beta$ carries a minus sign and is subtracted; with
$\tilde\beta=-\beta$ this is the textbook
$d_\ell=r_\ell+\tilde\beta_{\ell-1}d_{\ell-1}$,
$\tilde\beta_{\ell-1}=\|r_\ell\|^2/\|r_{\ell-1}\|^2$. Same algorithm.

**Cost** [S4 Rem. 8.5]: one matvec, two inner products and three axpys per step,
and only **four vectors** of length $N$ in memory at once
($x_\ell,r_\ell,d_\ell,Ad_\ell$). In exact arithmetic CG terminates with the
exact solution after at most $N$ steps, so it is technically a direct solver,
but round-off destroys that, and it is used as a genuine iterative method.

**Convergence** [S4 §8.1.2]. Since
$\mathcal K_\ell=\{q(A)r_0:q\in\mathcal P_{\ell-1}\}$ and $r_0=Ae_0$,
$$\|x^\ast-x_\ell\|_A=\min_{q\in\mathcal P_\ell,\ q(0)=1}\|q(A)e_0\|_A\qquad\text{[S4 Thm 8.6]}.$$
Expanding $e_0$ in an orthonormal eigenbasis gives
$\|q(A)e_0\|_A^2=\sum_i|e_{0,i}|^2\lambda_i\,q(\lambda_i)^2$, so
$$\|x^\ast-x_\ell\|_A\le\min_{q\in\mathcal P_\ell,\ q(0)=1}\ \max_{\lambda\in\sigma(A)}|q(\lambda)|\ \|e_0\|_A,$$
and estimating the min–max with a **Chebyshev polynomial** on
$[\lambda_{\min},\lambda_{\max}]$:

**Theorem** [S4 Thm 8.7]. With $\kappa=\mathrm{cond}_2(A)=\lambda_{\max}/\lambda_{\min}$,
$$\boxed{\;\|x^\ast-x_\ell\|_A\le2\left(\frac{\sqrt\kappa-1}{\sqrt\kappa+1}\right)^{\ell}\|e_0\|_A\;}$$
i.e. $O(\sqrt\kappa\,\log\tfrac1{\mathrm{tol}})$ iterations, against $O(\kappa)$
for Jacobi, Gauss–Seidel or steepest descent. Hence
**preconditioning** [S4 Rem. 8.8]: apply CG to $B^{-1}A$ with $B$ SPD and
$B\approx A$ but cheap: PCG.

The min–max form also explains why CG often beats its own bound: if the spectrum
is clustered, a low-degree polynomial can be small on all of it, and CG converges
in about as many steps as there are clusters.

For the 2-D Poisson matrix, $\kappa\approx4/(\pi^2h^2)$, so CG needs
$O(1/h)=O(\sqrt N)$ iterations. `cg.cpp` on a $63\times63$ grid ($\kappa=1659$,
$\sqrt\kappa=41$) reaches $10^{-10}$ in 120 matrix-free iterations.

## 4. GMRES [S4 §8.2]

$A$ merely invertible. Seek $x_\ell\in x_0+\mathcal K_\ell$ with
$$\|b-Ax_\ell\|_2\le\|b-Ax\|_2\qquad\forall x\in x_0+\mathcal K_\ell\qquad\text{[S4 (8.7)]},$$
equivalently, by the same variational argument as the normal equations,
$$(r_\ell,v)_2=0\qquad\forall v\in A\mathcal K_\ell\qquad\text{[S4 (8.8), Exercise 8.9]}.$$
**GMRES is a least-squares method** [S4 Exercise 8.9], and the pictures in
[S4 Fig. 8.1] say it precisely: CG makes the *error* $(\cdot,\cdot)_A$-orthogonal
to $\mathcal K_\ell$, GMRES makes the *residual* $(\cdot,\cdot)_2$-orthogonal to
$A\mathcal K_\ell$.

**Arnoldi** [S4 Alg. 28] builds an orthonormal basis $v_1..v_\ell$ of
$\mathcal K_\ell$ by Gram–Schmidt on $v_1,Av_1,A^2v_1,\ldots$:

```
v_1 := r_0/||r_0||_2
for j = 1..l:
    w := A v_j
    for i = 1..j:  h[i,j] := (w, v_i)_2;   w := w - h[i,j] v_i
    h[j+1,j] := ||w||_2
    if h[j+1,j] == 0: stop (invariant subspace found; exact solution in K_j)
    v_{j+1} := w / h[j+1,j]
```
This yields $AV_\ell=V_{\ell+1}\bar H_\ell$ with $\bar H_\ell\in\mathbb R^{(\ell+1)\times\ell}$
**upper Hessenberg**. Writing $x=x_0+V_\ell y$,
$$\|b-Ax\|_2=\|\,\|r_0\|_2e^1-\bar H_\ell y\,\|_2,$$
a small $(\ell+1)\times\ell$ least-squares problem, solved by QR with **Givens
rotations** (note [06](06-qr-factorisation.md)): one new rotation per
iteration, because $\bar H$ is Hessenberg [S4 Alg. 29]. The residual norm falls
out of the QR for free, so it is the natural stopping criterion
[S4 Rem. 8.13].

Two practical facts [S4 Rem. 8.12, Ex. 8.14]: the derivation assumes
$\bar H_\ell$ has full rank (a breakdown $h_{j+1,j}=0$ is a *lucky* breakdown:
the exact solution is already in $\mathcal K_j$); and storage and work grow with
$\ell$, so in practice one uses **restarted GMRES($m$)**: MATLAB's `gmres` is a
robust version of it. [S4 Rem. 8.10] notes that replacing $A\mathcal K_\ell$ by
another test space generalises GMRES to a whole family of Petrov–Galerkin
methods.

## Pitfalls

- CG on a matrix that is not SPD. The theory does not apply; it can stall or
  break down on $d^\top Ad=0$. Use GMRES (or MINRES for symmetric indefinite).
- Trusting CG's "termination in $N$ steps". Rounding destroys the exact
  $(\cdot,\cdot)_A$-orthogonality [S4 Rem. 8.5].
- Watching $\|r_\ell\|_2$ in CG and expecting monotone decrease. Only
  $\|e_\ell\|_A$ is monotone. In **GMRES** the residual *is* monotone, by
  construction.
- Forgetting that $\kappa$ enters CG as $\sqrt\kappa$ and stationary methods as
  $\kappa$: that is the whole argument for CG.
- Running full GMRES to convergence on a large problem: $\ell$ vectors of storage
  and $O(\ell^2N)$ work. Restart.
- Preconditioning CG with a non-SPD $B$: the method loses its inner product.

## Exam-style questions

CSE-only chapter, so no past paper covers it; these are ours, written against
[S4] §8 in the style the rest of the papers use.

1. *Why is it sensible to look for an approximation of $A^{-1}b$ in a Krylov
   space?*
   Cayley–Hamilton: $A^{-1}$ is a polynomial of degree $N-1$ in $A$
   [S4 (8.1)], so $A^{-1}b\in\mathcal K_N(A,b)$ exactly. Low-dimensional Krylov
   spaces are truncations of an exact representation.
2. *What does CG minimise, over which set, and what does GMRES minimise, over
   which set?*
   CG: $\|x^\ast-x\|_A$ over $x_0+\mathcal K_\ell$ [S4 Lem. 8.3]; equivalently
   error $(\cdot,\cdot)_A$-orthogonal to $\mathcal K_\ell$. GMRES:
   $\|b-Ax\|_2$ over $x_0+\mathcal K_\ell$ [S4 (8.7)]; equivalently residual
   $(\cdot,\cdot)_2$-orthogonal to $A\mathcal K_\ell$ [S4 (8.8)].
3. *State the CG convergence estimate and compare the iteration count with
   Gauss–Seidel.*
   $\|x^\ast-x_\ell\|_A\le2\big(\tfrac{\sqrt\kappa-1}{\sqrt\kappa+1}\big)^\ell\|e_0\|_A$
   [S4 Thm 8.7], so $O(\sqrt\kappa)$ iterations against $O(\kappa)$. For the 2-D
   Poisson matrix with $\kappa\sim h^{-2}$ that is $O(h^{-1})$ against
   $O(h^{-2})$.
4. *Sketch the derivation of [S4 Thm 8.6] and explain where the Chebyshev
   polynomial enters.*
   $\mathcal K_\ell=\{q(A)r_0:q\in\mathcal P_{\ell-1}\}$ and $r_0=Ae_0$, so the
   minimisation over $x_0+\mathcal K_\ell$ becomes
   $\min_{q(0)=1}\|q(A)e_0\|_A$. Diagonalising bounds this by
   $\min_q\max_{\lambda\in\sigma(A)}|q(\lambda)|$; bounding the spectrum by
   $[\lambda_{\min},\lambda_{\max}]$ and choosing the scaled Chebyshev polynomial
   (the minimiser of the sup norm among monic-at-zero polynomials on an
   interval) gives Thm 8.7.
5. *How many vectors does CG hold in memory, and what is the cost per step?*
   Four: $x_\ell,r_\ell,d_\ell,Ad_\ell$ [S4 Rem. 8.5]. One matvec, two inner
   products, three axpys.
6. *Why does GMRES use Givens rotations rather than Householder for its internal
   least-squares problem?*
   $\bar H_\ell$ is upper Hessenberg and grows by one column per iteration, so a
   single new Givens rotation extends the previous QR factorisation; Householder
   would redo the whole factorisation [S4 Alg. 29, Ex. 4.55].
7. *What is a "lucky breakdown" in Arnoldi?*
   $h_{j+1,j}=0$: the Krylov space is $A$-invariant, so the exact solution lies
   in $\mathcal K_j$ and GMRES terminates with zero residual
   [S4 Rem. 8.12].

## Implementation

`src/py/linsolve.py`: `jacobi`, `gauss_seidel`, `sor`, `sor_optimal_omega`,
`conjugate_gradient` (optional matrix-free `matvec`), `iteration_matrix`,
`power_iteration`, `poisson_1d`.

`src/py/gmres.py` (new): **`richardson`** and **`steepest_descent_linear`**
([S4 §8], the other two basic methods and the gradient method), `arnoldi`
([S4 Alg. 28], modified and standard Gram–Schmidt), `gmres` ([S4 Alg. 29],
Givens QR of the growing Hessenberg matrix, residual read off the QR),
`gmres_restarted`, `cg_polynomial_bound` ([S4 Thm 8.7]).

Tests: `test_linsolve.py` (analytic spectral radii, the CG rate bound, CG
directions $A$-orthogonal [S4 Lem. 8.3]) and `test_gmres.py` (Richardson
converging only for small enough $\omega$; steepest descent needing $O(\kappa)$
steps against CG's $O(\sqrt\kappa)$; the Arnoldi relation $AV_\ell=V_{\ell+1}\bar H_\ell$ and
$V^\top V=I$; $\bar H$ Hessenberg; GMRES residuals **monotone** and matching
`scipy.sparse.linalg.gmres`; exact termination at $\ell=N$; a lucky breakdown on
a matrix with an invariant Krylov subspace; GMRES solving a non-symmetric system
on which CG stalls; and CG obeying the [S4 Thm 8.7] bound on a 2-D Poisson
matrix).

`src/cpp/cg.cpp`: matrix-free CG on the 2-D Poisson 5-point stencil
($63\times63$, $\kappa=1659$), manufactured solution $x(1-x)y(1-y)$, iteration
count $O(\sqrt\kappa)$.
