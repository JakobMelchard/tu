# 05 Numerical linear algebra

Storing and solving $Ax = b$ when $A$ comes from a discretised PDE: large, sparse, often symmetric positive definite (SPD). The storage formats, the splitting framework and the CG bound are all in Saad [S22], which the author hosts free; CG itself is cited to the original [S15], which is vendored in `../refs/vendor/` because it is a US Government work and therefore public domain. Reference code: `src/cpp/csr.cpp`, `src/py/csr.py`.

## Dense vs sparse storage

| format | memory | matvec | notes |
|---|---|---|---|
| dense row-major | $8n^2$ B | $2n^2$ flop | LAPACK; only for $n \lesssim 10^4$ |
| banded (bandwidth $w$) | $8 n (2w+1)$ | $O(nw)$ | LU stays banded: $O(n w^2)$ factorisation |
| COO (triplets $i, j, v$) | $16\,\text{nnz}$ | $2\,\text{nnz}$ | easy assembly, duplicates allowed, no row access |
| CSR | $12\text{-}16\,\text{nnz} + 8n$ | $2\,\text{nnz}$ | standard for SpMV and row operations |
| CSC | same | same | column access; scipy default for direct solvers |
| ELL / diagonal | fixed nnz per row | vectorises well | stencil matrices on GPUs |

**CSR** (compressed sparse row) [S22 §3.4]: three arrays. `val[nnz]` and `col[nnz]` list the nonzeros row by row; `row_ptr[n+1]` gives the start of each row, `row_ptr[n] = nnz`. Row $i$ is `k = row_ptr[i] .. row_ptr[i+1]-1`. SpMV:

```cpp
for i in 0..n-1:  y[i] = sum_{k=row_ptr[i]}^{row_ptr[i+1]-1} val[k] * x[col[k]]
```
2 nnz flops, 12 bytes per nonzero (8 value + 4 index) plus the gather `x[col[k]]`: AI $\approx 0.17$ flop/byte, firmly memory bound (note 01). The 2D Poisson matrix with $N = 128$ has $n = (N-1)^2 = 16129$ and nnz $= 5n - 4(N-1) = 80{,}137$ (five per row, minus one per row on each of the four boundary sides): CSR 1.4 MB vs dense 2.1 GB (`./bin/csr --bench` prints both).

Assembly: collect triplets (or a `std::map<pair,double>` if entries arrive randomly), sort by $(i, j)$, sum duplicates, build `row_ptr` by counting entries per row and prefix-summing (`scipy.sparse.coo_matrix(...).tocsr()` does exactly this).

## Direct solvers

- LU / Cholesky ($A = LL^T$ for SPD, half the work): $\frac{2}{3}n^3$ / $\frac{1}{3}n^3$ flops dense. Backward stable with pivoting; error $\sim \kappa(A)\,\epsilon$.
- Tridiagonal: **Thomas algorithm** = LU without pivoting, $O(n)$: forward elimination $w = a_i / d_{i-1}$, $d_i \mathrel{-}= w c_{i-1}$, $b_i \mathrel{-}= w b_{i-1}$; back substitution. Stable for diagonally dominant or SPD matrices (`thomas` in `fd_poisson1d.cpp`).
- Sparse direct (SuperLU, UMFPACK, CHOLMOD, PARDISO): reorder to reduce fill-in (nested dissection), then factor. 2D Poisson: $O(n^{3/2})$ flops, $O(n \log n)$ memory; 3D: $O(n^2)$ flops, $O(n^{4/3})$ memory, which is why 3D problems go iterative. `scipy.sparse.linalg.spsolve`, `splu` (factor once, solve many right-hand sides: used in `heat2d.py`).

## Stationary iterative methods

Split $A = M - K$ with $M$ easy to invert; iterate $x^{k+1} = M^{-1}(K x^k + b) = x^k + M^{-1}(b - Ax^k)$. Converges for every start **iff** $\rho(M^{-1}K) < 1$; error contracts by $\rho$ per step asymptotically [S22 ch. 4]. ($\rho$ is the *asymptotic* rate: a non-normal iteration matrix can grow the error for many steps before it starts to shrink.)

With $A = D + L + U$ (diagonal, strict lower, strict upper):

| method | $M$ | update for row $i$ | parallel? |
|---|---|---|---|
| Jacobi | $D$ | $x_i^{k+1} = \frac{1}{a_{ii}}\big(b_i - \sum_{j \ne i} a_{ij} x_j^k\big)$ | yes (needs two vectors) |
| Gauss-Seidel | $D + L$ | same but uses $x_j^{k+1}$ for $j < i$ (in place) | no (red-black ordering fixes it) |
| SOR | $\frac{1}{\omega} D + L$ | $x_i^{k+1} = (1-\omega) x_i^k + \omega\, x_i^{\text{GS}}$, $0 < \omega < 2$ | like GS |

For the 2D Poisson matrix (grid $N$, $h = 1/N$) [S22 ch. 4]:
$$\rho_J = \cos \pi h \approx 1 - \tfrac{\pi^2 h^2}{2}, \quad \rho_{GS} = \rho_J^2 \approx 1 - \pi^2 h^2, \quad \rho_{SOR}(\omega_{\text{opt}}) = \omega_{\text{opt}} - 1 \approx 1 - 2\pi h, \quad \omega_{\text{opt}} = \frac{2}{1 + \sin \pi h}.$$
Iterations to reduce the error by $10^{-p}$: $\approx p \ln 10 / (1 - \rho)$: Jacobi $\sim 0.47 p N^2$, GS $\sim 0.23 p N^2$, SOR $\sim 0.37 p N$. Each iteration costs one SpMV, $O(n)$. Stationary methods damp high-frequency error fast and low-frequency error slowly, the observation behind multigrid.

## Conjugate gradients

For SPD $A$, minimise $\phi(x) = \frac{1}{2} x^T A x - b^T x$ over the Krylov space $\mathcal{K}_k = \text{span}\{r_0, Ar_0, \dots, A^{k-1} r_0\}$ with $A$-orthogonal search directions - Hestenes and Stiefel's construction [S15]. One SpMV, two dot products, three axpys per iteration; memory: 4 vectors.

```
r = b - A x;  p = r;  rr = r.r
loop:  Ap = A p;  alpha = rr / (p.Ap)
       x += alpha p;  r -= alpha Ap
       rr_new = r.r;  stop if sqrt(rr_new) < tol |b|
       p = r + (rr_new / rr) p;  rr = rr_new
```
Error bound in the energy norm:
$$\|e_k\|_A \le 2\left(\frac{\sqrt{\kappa} - 1}{\sqrt{\kappa} + 1}\right)^k \|e_0\|_A, \qquad k \approx \tfrac{1}{2}\sqrt{\kappa}\,\ln\tfrac{2}{\text{tol}}.$$
(the bound is [S22 §6.11]). $\kappa \sim N^2$ for Poisson gives $k \sim N$, the same order as optimal SOR but without a tuning parameter, and CG also converges fast when the eigenvalues cluster. Non-symmetric systems: GMRES, BiCGSTAB [S22 ch. 6].

**Finite termination is a theorem about exact arithmetic, not a stopping rule.** CG reaches the exact solution in at most $n$ steps with no rounding, but Hestenes and Stiefel already report in their own §19 that in floating point "the results in the $(n+1)$st and $(n+2)$nd iterations are normally far superior to those obtained in the $n$th" [S15]. Stop on the residual, never on the step count.

## Preconditioning

Solve $M^{-1} A x = M^{-1} b$ with $M \approx A$ such that $M^{-1}r$ is cheap and $\kappa(M^{-1}A) \ll \kappa(A)$. PCG replaces `p = r` by `p = z = M^{-1} r` and the dot products $r \cdot r$ by $r \cdot z$; $M$ must be SPD.

| preconditioner | $M$ | cost | effect on Poisson |
|---|---|---|---|
| Jacobi | $\text{diag}(A)$ | free | none (constant diagonal); large for badly scaled rows |
| SSOR / symmetric GS | $(D + L) D^{-1} (D + U)$ | 1 sweep | $\kappa \to \sqrt{\kappa}$-ish |
| incomplete Cholesky IC(0) | $\tilde{L}\tilde{L}^T$ with the sparsity of $A$ | 1 fwd+bwd solve | 2-5x fewer iterations |
| multigrid (one V-cycle) | | $O(n)$ | $\kappa = O(1)$: iterations independent of $h$ |

## Worked example (`./bin/csr --test`, 2D Poisson $N = 16$, $n = 225$, tol $10^{-8}$ on $\|r\|/\|b\|$)

```
solver            iters   time[s]   max|u-u_ex|
Jacobi              943    0.0016     5.4e-05    (predicted 0.47*8*256 ~ 960)
Gauss-Seidel        473    0.0010     5.4e-05    (half of Jacobi)
SOR w_opt=1.674      60    0.0001     5.4e-05    (predicted 0.37*8*16 ~ 47)
CG                   45    0.0001     5.4e-05
scaled system D A D: CG 1221 iterations, Jacobi-PCG 54 iterations
```
The last line: the Poisson matrix scaled by a diagonal with entries between 1 and 1000 is still SPD but $\kappa$ grows by $10^6$; CG needs 27x more steps; Jacobi preconditioning undoes the scaling and gives back the original count. `--bench` at $N = 128$: Jacobi 60 594 (predicted $0.47 \cdot 8 \cdot 128^2 \approx 61\,600$), GS 30 304, SOR 503 (predicted ~380), CG 380 iterations, the predicted $N^2$ vs $N$ scaling. The SOR estimate is low by the same factor 1.3 at both sizes, as expected from an asymptotic rate.

Discretisation error (5.4e-5) is the same for every solver: the solver only has to reach the accuracy of the discretisation, so a tolerance of $10^{-8}$ on the residual is already generous.

## Pitfalls

- Using CG on a non-symmetric or indefinite matrix: it may diverge silently. Check $\|A - A^T\|$ and the sign of $p^T A p$.
- Stopping on $\|r\|$ absolute instead of $\|r\|/\|b\|$, or on $\|x^{k+1} - x^k\|$ (which is small for slowly converging Jacobi long before convergence).
- Comparing solvers by iteration count only: one SOR sweep costs the same as one Jacobi sweep, but a multigrid cycle costs ~10 SpMVs.
- Jacobi updated in place is not Jacobi (it becomes a scrambled Gauss-Seidel).
- Choosing $\omega$ by trial without knowing $\omega_{\text{opt}}$ depends on $h$: $\omega = 1.5$ is good at $N = 8$ and poor at $N = 128$.
- Building a dense matrix "for now": $N = 256$ in 2D is $n = 65025$, dense 34 GB.
- Storing CSR indices as `size_t` doubles the index traffic in a bandwidth-bound kernel; `int32` suffices below $2 \cdot 10^9$ nonzeros.

## Exam-style questions

1. **Write the CSR arrays of $\begin{pmatrix} 4 & -1 & 0 \\ -1 & 4 & -1 \\ 0 & -1 & 4 \end{pmatrix}$.** `val = [4,-1,-1,4,-1,-1,4]`, `col = [0,1,0,1,2,1,2]`, `row_ptr = [0,2,5,7]`.
2. **Why does Gauss-Seidel converge about twice as fast as Jacobi on the Poisson problem, and why is it harder to parallelise?** $\rho_{GS} = \rho_J^2$ for consistently ordered matrices, so one GS sweep equals two Jacobi sweeps. GS uses updated values within the sweep, a sequential dependency; red-black ordering (update all red points, then all black) restores parallelism because neighbours have the opposite colour.
3. **Give the CG iteration bound in terms of $\kappa$ and derive how the iteration count scales with the grid size for 2D Poisson.** $k \approx \frac{1}{2}\sqrt{\kappa}\ln(2/\text{tol})$; $\kappa \approx 4/(\pi^2 h^2)$, so $\sqrt{\kappa} \approx 2N/\pi$ and $k \propto N$. Doubling the resolution doubles the iterations and quadruples the unknowns: cost $\times 8$.
4. **What does a preconditioner have to satisfy for PCG, and why does Jacobi preconditioning not help the Poisson matrix?** $M$ SPD, $M^{-1} r$ cheap, and $\kappa(M^{-1}A)$ small. The Poisson diagonal is constant ($4/h^2$), so $M^{-1}A = \frac{h^2}{4} A$: a scalar multiple, identical eigenvalue spread.
5. **Sparse direct or CG for a 3D Poisson problem with $n = 10^7$?** Sparse Cholesky needs $O(n^2) = 10^{14}$ flops and $O(n^{4/3}) \approx 10^{9.3}$ fill entries (tens of GB); CG needs $\sim N = n^{1/3} \approx 215$ iterations times $O(n)$: $\sim 10^{10}$ flops and 5 vectors. CG (better: multigrid-preconditioned CG, ~10 iterations).

Code: `src/cpp/csr.cpp` (`CSR::spmv`, `poisson2d`, `jacobi`, `sor`, `cg` with optional Jacobi preconditioner, `precond_demo`), `src/py/csr.py` (same in numpy, tests against `scipy.sparse` in `test_csr.py`). Sources: [S15] [S22] [S23].
