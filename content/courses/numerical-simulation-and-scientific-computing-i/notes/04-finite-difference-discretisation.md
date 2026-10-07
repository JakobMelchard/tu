# 04 Finite difference discretisation

Turning a PDE on a grid into a linear system (elliptic) or a time-stepping recursion (parabolic), and knowing when the result converges. Everything in this note follows LeVeque [S23], which is the standard reference for finite differences for ODEs and PDEs; the two named theorems are cited to their originals [S24]. Reference code: `src/cpp/fd_poisson1d.cpp`, `src/cpp/heat2d.cpp`, `src/py/fd_poisson.py`, `src/py/heat2d.py`.

## 1D Poisson

$-u'' = f$ on $(0,1)$, $u(0) = \alpha$, $u(1) = \beta$. Grid $x_i = ih$, $h = 1/N$, unknowns $u_1, \dots, u_{N-1}$. Second-order stencil (note 03):

$$\frac{-u_{i-1} + 2u_i - u_{i+1}}{h^2} = f_i, \qquad i = 1, \dots, N-1.$$

Matrix form $A u = b$ with $A = \frac{1}{h^2}\,\text{tridiag}(-1, 2, -1) \in \mathbb{R}^{(N-1)\times(N-1)}$, $b_i = f_i$ plus the boundary values moved to the right-hand side: $b_1 \mathrel{+}= \alpha/h^2$, $b_{N-1} \mathrel{+}= \beta/h^2$.

Properties of $A$: symmetric positive definite, eigenpairs [S23 §2.10]
$$\lambda_k = \frac{4}{h^2} \sin^2\frac{k \pi h}{2}, \quad v_k = \big(\sin(k \pi x_i)\big)_i, \quad k = 1, \dots, N-1,$$
so $\lambda_{\min} \approx \pi^2$, $\lambda_{\max} \approx 4/h^2$, condition number $\kappa = \lambda_{\max}/\lambda_{\min} \approx \dfrac{4}{\pi^2 h^2} \sim N^2$. This governs iterative solver cost (note 05): CG needs $\sim \sqrt{\kappa} \sim N$ iterations, exactly the `CG its` column in `fd_poisson1d` (15, 31, 63, 127, ...).

Truncation error $\tau_i = \frac{h^2}{12} u''''(x_i)$ (note 03's second-difference constant); stability of $A^{-1}$ ($\|A^{-1}\|_\infty \le 1/8$, the maximum of the Green's function $x(1-x)/2$) gives the global error $\|u - u_h\|_\infty \le \frac{h^2}{96} \max|u''''|$: **order 2** [S23 §2.9]. This is the pattern LeVeque generalises: *consistency + stability = convergence*, with the stability constant an $A^{-1}$ bound.

### Boundary conditions

- Dirichlet: eliminate the boundary unknown, move the value to $b$ (as above). Non-zero values change $b$, not $A$.
- Neumann $u'(0) = g$ [S23 §2.12]: introduce a ghost point $u_{-1} = u_1 - 2hg$ and keep row 0: $\frac{2u_0 - 2u_1}{h^2} = f_0 + \frac{2g}{h}$ (second order, symmetric after scaling the row by 1/2). The one-sided alternative $(u_1 - u_0)/h = g$ is only first order and breaks symmetry.
- Pure Neumann: $A$ is singular (constant null vector); fix the mean or pin one value.
- Periodic: wrap indices; $A$ becomes circulant, singular for the same reason.

## 2D Poisson

$-(u_{xx} + u_{yy}) = f$ on the unit square, five-point stencil:
$$\frac{4u_{i,j} - u_{i-1,j} - u_{i+1,j} - u_{i,j-1} - u_{i,j+1}}{h^2} = f_{i,j}.$$
Lexicographic ordering $k = (i-1)(N-1) + (j-1)$ gives a block-tridiagonal matrix $A_2 = I \otimes A_1 + A_1 \otimes I$ (Kronecker sum, `poisson2d_matrix` in `fd_poisson.py`), $n = (N-1)^2$ unknowns, 5 nonzeros per row, bandwidth $N-1$. Eigenvalues $\lambda_{kl} = \lambda_k + \lambda_l$, so $\kappa \sim N^2$ again. Error still $O(h^2)$. In 3D: seven-point stencil, $n = (N-1)^3$.

Dense LU on the band costs $O(n \cdot \text{bw}^2) = O(N^4)$ in 2D; CG or multigrid with a sparse matrix is the way (note 05).

## Heat equation

$u_t = \alpha \Delta u$, $u = 0$ on the boundary, $u(x, y, 0) = \sin \pi x \sin \pi y$, exact $u = e^{-2\alpha\pi^2 t} \sin \pi x \sin \pi y$.

**Method of lines**: discretise space first, $\dot{u} = -\alpha A_2 u$ (a stiff ODE system, eigenvalues in $[-8\alpha/h^2, -2\alpha\pi^2]$), then choose a time integrator.

| scheme | update | amplification factor $g$ per mode | stability |
|---|---|---|---|
| explicit Euler | $u^{n+1} = u^n - \Delta t\, \alpha A u^n$ | $1 - \Delta t\,\alpha \lambda$ | $\Delta t \le 2/(\alpha \lambda_{\max})$ |
| implicit Euler | $(I + \Delta t\,\alpha A) u^{n+1} = u^n$ | $1/(1 + \Delta t\,\alpha \lambda)$ | always, $|g| < 1$ |
| Crank-Nicolson | $(I + \frac{\Delta t}{2}\alpha A) u^{n+1} = (I - \frac{\Delta t}{2}\alpha A) u^n$ | $\dfrac{1 - \Delta t\,\alpha\lambda/2}{1 + \Delta t\,\alpha\lambda/2}$ | always, but $g \to -1$ for stiff modes (oscillations) |

With $\lambda_{\max} \approx 4d/h^2$ in $d$ dimensions the explicit condition is
$$r = \frac{\alpha \Delta t}{h^2} \le \frac{1}{2d}: \qquad \tfrac{1}{2} \text{ in 1D}, \quad \tfrac{1}{4} \text{ in 2D}, \quad \tfrac{1}{6} \text{ in 3D}.$$

This is the diffusive stability limit. **Von Neumann analysis** [S23 ch. 9-10] obtains the same thing without the matrix: insert $u_j^n = g^n e^{i\theta j}$ into the scheme and require $|g(\theta)| \le 1$ for all $\theta$. For 1D explicit Euler $g = 1 - 4r \sin^2(\theta/2)$, worst case $\theta = \pi$: $|1 - 4r| \le 1 \Leftrightarrow r \le 1/2$.

For advection $u_t + a u_x = 0$ the analogous **CFL condition** is $|a| \Delta t / h \le 1$ (upwind; information must not travel more than one cell per step) - the necessary condition of Courant, Friedrichs and Lewy (1928) [S24], which is about the numerical domain of dependence containing the analytic one and is therefore *necessary but not sufficient*. Central differences in space with explicit Euler are unconditionally unstable there.

**Accuracy**: explicit and implicit Euler are first order in $\Delta t$, Crank-Nicolson second; space is second order in $h$. Total error $O(\Delta t) + O(h^2)$. Under the explicit limit $\Delta t \sim h^2$ the time error is automatically $O(h^2)$, so explicit Euler is "free" of extra accuracy loss but costs $N^2$ steps of $N^2$ work in 2D: $O(N^4)$ for a fixed final time.

**Lax equivalence theorem** (Lax & Richtmyer 1956) [S24]: for a **consistent** finite-difference approximation to a **well-posed linear** initial-value problem, stability is **necessary and sufficient** for convergence. All four hypotheses matter - drop linearity or well-posedness and the theorem says nothing, which is why nonlinear schemes need their own analysis.

## Worked example (`./bin/heat2d`, $N = 32$, $\alpha = 1$, $T = 0.05$)

```
explicit limit dt <= h^2/(4 alpha) = 2.441e-04
scheme                 r   steps      max|u|     max err
explicit (stable)   0.24     214   3.72e-01    5.5e-04
explicit (unstable) 0.30     171   1.60e+07    1.6e+07     <- |g| = |1-8r| = 1.4 per step, 1.4^171 growth of round-off
implicit Euler      0.25     205   3.74e-01    1.2e-03
implicit Euler      1.00      52   3.76e-01    3.8e-03     4x the explicit dt, still fine
implicit Euler      4.00      13   3.87e-01    1.4e-02     error grows linearly with dt: first order
```

The unstable run needs no perturbation: the initial data is the smoothest mode, but round-off excites the checkerboard mode $(N-1, N-1)$, which is amplified by 1.4 per step. Implicit Euler at $r = 4$ is stable and its error is 4x that at $r = 1$: first order in time, as predicted. Each implicit step here is one CG solve of the SPD system $I + \Delta t\,\alpha A_2$ (1-3 iterations with warm start, since the matrix is well conditioned: $\kappa \le 1 + 8r$).

Convergence-order check for the 1D Poisson solver (`./bin/fd_poisson1d`): errors 1.30e-2, 3.22e-3, 8.04e-4, 2.01e-4 for $N = 8, 16, 32, 64$, observed order 2.008, 2.002, 2.001.

## Pitfalls

- Testing a 2D Poisson solver with $u = \sin\pi x \sin \pi y$: this is an eigenvector of $A_2$, so CG converges in one iteration and the test says nothing about the solver. Use a manufactured solution that is not an eigenfunction (`csr.cpp` uses $x(1-x)y(1-y)e^{xy}$).
- Choosing $\Delta t$ from the 1D limit ($r \le 1/2$) in 2D: unstable.
- Not landing exactly on $T$ (round $\Delta t = T/\lceil T/\Delta t \rceil$), then blaming the scheme for an $O(\Delta t)$ error.
- Forgetting that halving $h$ in an explicit code quadruples the number of steps: cost $\times 16$ in 2D.
- Mixing up the order in time and space when reading a convergence table: refine one at a time, or keep $\Delta t \propto h^2$ (explicit) or $\Delta t \propto h$ (Crank-Nicolson) so both errors shrink together.
- A Neumann boundary implemented with the first-order one-sided formula pulls the global order down to 1.

## Exam-style questions

1. **Write the FD system for $-u'' = f$, $u(0) = 0$, $u(1) = 1$ with $N = 4$.** $h = 1/4$, unknowns $u_1, u_2, u_3$; $16 \begin{pmatrix} 2 & -1 & 0 \\ -1 & 2 & -1 \\ 0 & -1 & 2 \end{pmatrix} \begin{pmatrix} u_1 \\ u_2 \\ u_3 \end{pmatrix} = \begin{pmatrix} f_1 \\ f_2 \\ f_3 + 16 \end{pmatrix}$.
2. **Derive the stability limit of explicit Euler for $u_t = \alpha u_{xx}$ by von Neumann analysis.** Scheme: $u_j^{n+1} = u_j^n + r(u_{j+1}^n - 2u_j^n + u_{j-1}^n)$, $r = \alpha \Delta t/h^2$. Insert $g^n e^{i\theta j}$: $g = 1 + r(e^{i\theta} - 2 + e^{-i\theta}) = 1 - 4r\sin^2(\theta/2)$. Need $-1 \le g \le 1$ for all $\theta$; the worst case $\sin^2 = 1$ gives $r \le 1/2$.
3. **Why does an implicit scheme allow large $\Delta t$ but not necessarily an accurate answer with it?** Stability only bounds the growth of every mode ($|g| \le 1$); accuracy requires $g(\Delta t \lambda)$ to approximate $e^{-\Delta t \lambda}$, which for implicit Euler is only first-order accurate. The `heat2d` table shows the error growing linearly with $\Delta t$.
4. **How is the condition number of the 2D Poisson matrix related to $h$, and what does that imply for CG?** $\lambda_{\min} \approx 2\pi^2$, $\lambda_{\max} \approx 8/h^2$, so $\kappa \approx 4/(\pi^2 h^2) \propto N^2$; CG iterations scale with $\sqrt{\kappa} \propto N$, total cost $O(N \cdot n) = O(N^3)$ in 2D, versus $O(N^4)$ for banded LU.
5. **What is the order of accuracy of the ghost-point Neumann treatment, and why is the one-sided difference worse?** Ghost point: central difference for $u'(0)$, $O(h^2)$, keeps the second-order global error. One-sided $(u_1 - u_0)/h$: $O(h)$ truncation at that node, which pollutes the whole solution to first order.

Code: `src/cpp/fd_poisson1d.cpp` (`thomas`, `apply_A`, `cg`, convergence table), `src/cpp/heat2d.cpp` (`laplacian`, `run_explicit`, `run_implicit`, `cg_implicit`), `src/py/fd_poisson.py` (`poisson1d`, `poisson2d_matrix`), `src/py/heat2d.py` (`explicit_euler`, `implicit_euler`, `cfl_limit`). Sources: [S23] [S24].
