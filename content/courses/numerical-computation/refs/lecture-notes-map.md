# S4 section map: what the course covers, and where we cover it

Structural index of **S4** (Melenk & Faustmann, *Lecture Notes Numerical
Computation*, TU Wien, WS 2023/24, 160 pp.). Section numbers and titles are
S4's; the right-hand columns are ours. See [`SOURCES.md`](SOURCES.md).

## How to read the `CSE` column

S4 marks individual sections **(CSE)**. §7.3 ends with the line
"END OF LECTURE FOR VISUAL COMPUTING", so everything from §7.4 on is CSE-only
too. 101.973 (this course, CSE master, 6.0 ECTS in 2026W) gets all of it;
101.484 Computernumerik (Visual Computing, 3.0 ECTS) gets only the unmarked
part. That matters when reading past tests: **S11**'s two papers are Visual
Computing papers, so they never touch CG, GMRES, ODEs, the QR algorithm or
orthogonal iteration, but the CSE course examines those.

`•` = CSE-only. Blank = everyone.

## Chapter 1: Polynomial Interpolation (pp. 2–35)

| § | title | CSE | our note | our code |
|---|---|---|---|---|
| 1.1 | Existence and uniqueness | | [01](../notes/01-polynomial-interpolation.md) | `interp.lagrange_eval` |
| 1.2 | Neville scheme | | 01 | `neville.aitken_neville` |
| 1.3 | Newton representation | • | 01 | `interp.divided_differences` |
| 1.4 | Extrapolation as a prime application of the Neville scheme | | 01, [12](../notes/12-numerical-differentiation.md) | `neville.extrapolate_derivative` |
| 1.5 | A simple error estimate | | 01 | - |
| 1.6 | Chebyshev interpolation (uniform points, Chebyshev points, Lebesgue constant) | | 01 | `interp.chebyshev_nodes`, `neville.lebesgue_constant` |
| 1.7 | Remarks on Hermite interpolation | | 01 | `neville.hermite_*` |
| 1.8 | Splines (piecewise linear, classical cubic, energy minimisation) | • | 01 | `interp.cubic_spline` |
| 1.9 | Trigonometric interpolation and FFT (DFT properties, fast convolution) | • | [02](../notes/02-trigonometric-interpolation-and-fft.md) | `fft.*` |

## Chapter 2: Numerical Integration (pp. 36–53)

| § | title | CSE | our note | our code |
|---|---|---|---|---|
| 2.1 | Newton–Cotes formulas (closed and open), composite rules | | [03](../notes/03-numerical-integration.md) | `quad.newton_cotes_weights` |
| 2.2 | Romberg extrapolation, Euler–Maclaurin | | 03 | `quad.romberg` |
| 2.3 | Non-smooth integrands and adaptivity (graded meshes, Alg. 5) | | 03 | `quad.adaptive_simpson`, `quad.graded_mesh` |
| 2.4 | Gaussian quadrature (Legendre polynomials, 3-term recurrence) | | 03 | `quad.gauss_legendre` |
| 2.5 | Comments on the trapezoidal rule (periodic integrands) | | 03 | `quad.trapezoid` |
| 2.6 | Quadrature in 2D (squares, triangles, Duffy) | | 03 | `quad2d.*` |
| 2.7 | Comments on Gaussian quadrature (weighted) | • | 03 | `quad.gauss_quad` |

## Chapter 3: Conditioning and Error Analysis (pp. 54–57): four pages only

| § | title | CSE | our note | our code |
|---|---|---|---|---|
| 3.1 | Error measures (modelling, measurement, round-off, discretisation) | | [04](../notes/04-conditioning-and-error-analysis.md) | - |
| 3.2 | Conditioning ($\kappa_{abs}$, $\kappa_{rel}$, cancellation) | | 04 | `errors.cond_scalar` |
| 3.3 | Stability of algorithms ($f = f_1\circ\cdots\circ f_N$, $\log(1+x)$, quadratic formula) | | 04 | `errors.quadratic_roots_stable` |

## Chapter 4: Gaussian Elimination (pp. 58–88)

| § | title | CSE | our note | our code |
|---|---|---|---|---|
| 4.1 | Lower and upper triangular matrices, substitution | | [05](../notes/05-gaussian-elimination-and-lu.md) | `linsolve.lu_solve` |
| 4.2 | Classical Gaussian elimination as LU | | 05 | `linsolve.gauss_elim` |
| 4.3.1 | Crout's algorithm | | 05 | `banded.crout_lu` |
| 4.3.2 | Banded matrices (Thm 4.12: cost $O(npq)$) | | 05 | `banded.banded_lu` |
| 4.3.3 | Cholesky factorisation $A = CC^\top$ | | 05 | `linsolve.cholesky` |
| 4.3.4 | Skyline matrices (Thm 4.18) | | 05 | `banded.skyline_profile` |
| 4.4 | Gaussian elimination with pivoting | | 05 | `linsolve.lu_decompose` |
| 4.5 | Condition number of a matrix | | 05, 04 | `errors.cond` |
| 4.6 | Fill-in and ordering strategies (RCM, minimum degree) | • | 05 | `ordering.reverse_cuthill_mckee`, `ordering.minimum_degree` |
| 4.7.1 | Orthogonal matrices | | [06](../notes/06-qr-factorisation.md) | - |
| 4.7.2 | QR-factorisation, Gram–Schmidt | | 06 | `qr_svd.gram_schmidt_*` |
| 4.7.3 | Householder reflections | • | 06 | `qr_svd.householder_qr` |
| 4.7.4 | QR-factorisation with pivoting | • | 06 | `givens.qr_column_pivoting` |
| 4.7.5 | Givens rotations (Hessenberg QR in $O(n^2)$) | • | 06 | `givens.*` |

## Chapter 5: Least Squares (pp. 89–96)

| § | title | CSE | our note | our code |
|---|---|---|---|---|
| 5.1 | Method of the normal equations | | [07](../notes/07-least-squares-and-svd.md) | `interp.lstsq_normal` |
| 5.2 | Least squares using QR | | 07 | `qr_svd.qr_solve` |
| 5.3.1 | SVD | | 07 | `qr_svd.jacobi_svd` |
| 5.3.2 | Minimum-norm solution via SVD | | 07 | `pseudoinverse.min_norm_solution` |
| 5.3.3 | Least squares with the SVD | | 07 | `pseudoinverse.lstsq_svd` |
| 5.3.4 | Further properties (Thm 5.15 = Eckart–Young) | | 07 | `qr_svd.low_rank` |
| 5.3.5 | Moore–Penrose pseudoinverse | • | 07 | `pseudoinverse.pinv` |

## Chapter 6: Nonlinear Equations and Newton's Method (pp. 97–111)

| § | title | CSE | our note | our code |
|---|---|---|---|---|
| 6.1 | Newton's method in 1D | | [08](../notes/08-nonlinear-equations-and-newton.md) | `nonlinear.newton` |
| 6.2 | Convergence of fixed point iterations (contraction, order $p$) | | 08 | `nonlinear.fixed_point` |
| 6.3 | Newton in higher dimensions | | 08 | `nonlinear.newton_system` |
| 6.4 | Implementation aspects (stopping, simplified Newton, FD Jacobian) | | 08 | `nonlinear.jacobian_fd` |
| 6.5 | Damped and globalized Newton; descent methods, Armijo (Alg. 15) | | 08 | `optimize.globalized_newton`, `optimize.armijo` |
| 6.6 | Gauss–Newton | | 08 | `optimize.gauss_newton` |
| 6.7 | Quasi-Newton: Broyden | • | 08 | `optimize.broyden` |
| 6.8 | Unconstrained minimisation: gradient method, trust region | • | 08 | `optimize.gradient_descent_quadratic` |

## Chapter 7: Eigenvalue Problems (pp. 112–124)

| § | title | CSE | our note | our code |
|---|---|---|---|---|
| 7.1 | The power method (rate $|\lambda_2/\lambda_1|$) | | [09](../notes/09-eigenvalue-problems.md) | `qr_svd.power_method` |
| 7.2 | Inverse iteration, inverse iteration with shift, Rayleigh quotient iteration | | 09 | `eig.inverse_iteration`, `eig.rayleigh_quotient_iteration` |
| 7.3 | Stopping criteria (residual bounds, Thm 7.10) | | 09 | `eig.eigen_residual_bound` |
| - | *END OF LECTURE FOR VISUAL COMPUTING* | | | |
| 7.4 | Orthogonal iteration | • | 09 | `eig.orthogonal_iteration` |
| 7.5 | Basic QR-algorithm | • | 09 | `qr_svd.qr_algorithm` |
| 7.6 | Hessenberg form, deflation, QR with shift | • | 09 | `eig.hessenberg`, `eig.shifted_qr` |

## Chapter 8: Iterative solution of linear systems (pp. 125–136): all CSE

| § | title | CSE | our note | our code |
|---|---|---|---|---|
| 8.0 | Basic iterative methods (Richardson, Jacobi, Gauss–Seidel), gradient method | • | [10](../notes/10-iterative-linear-systems.md) | `linsolve.jacobi`, `linsolve.gauss_seidel` |
| 8.1 | Conjugate Gradient (Krylov spaces, Alg. 27, Thm 8.7) | • | 10 | `linsolve.conjugate_gradient` |
| 8.2 | GMRES (Arnoldi, Alg. 28/29) | • | 10 | `gmres.arnoldi`, `gmres.gmres` |

## Chapter 9: Numerical Methods for ODEs (pp. 137–151): all CSE

| § | title | CSE | our note | our code |
|---|---|---|---|---|
| 9.1 | Explicit Euler, consistency error, Thm 9.2 | • | [11](../notes/11-ordinary-differential-equations.md) | `ode.euler` |
| 9.2 | Implicit Euler | • | 11 | `ode.implicit_euler` |
| 9.3.1 | Explicit Runge–Kutta, Butcher tableaux, RK4 | • | 11 | `ode.rk4` |
| 9.3.2 | Implicit Runge–Kutta, θ-scheme | • | 11 | `irk.theta_scheme`, `irk.implicit_rk` |
| 9.3.3 | Why implicit methods (stiff example, Ex. 9.12) | • | 11 | `irk.lambert_system` |
| 9.3.4 | A-stability, stability function $R(z)$ | • | 11 | `ode.stability_function` |
| 9.4 | Boundary value problems: shooting methods (Alg. 30) | • | 11 | `bvp.shooting` |

## Appendix A: Notations and facts from other lectures (pp. 152–155)

Norms, inner products, Gram–Schmidt, $O(\cdot)$, Taylor. Assumed known; S4's
introduction points at Faustmann's *Applied Mathematics Foundations* notes (S5)
for a refresher.

## In the TISS subject line but not a chapter of S4

**"numerical differentiation"** (S1 "Subject of course"). S4 has no
differentiation chapter: difference quotients appear only as the worked example
of Neville extrapolation (§1.4, §1.5 Thm 1.17, Ex. 1.18). Our
[note 12](../notes/12-numerical-differentiation.md) keeps the material but is
marked as an appendix, not a lecture chapter.

**"extrapolation"** (S1 "Learning outcomes"): §1.4 and §2.2 (Romberg).
