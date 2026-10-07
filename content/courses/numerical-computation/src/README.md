# Reference implementations: 101.973 Numerical Computation

Every algorithm in the [notes](../notes/README.md), implemented from scratch,
with tests that reproduce the worked examples of the course script [S4] wherever
it prints a number. Python is the course language (the exercises are in Matlab
or Python [S1]); the C++ programs cover the five algorithms where a compiled,
allocation-free version is instructive.

Cross-references to [S4] are by section, theorem, algorithm or example number:
see [`../refs/SOURCES.md`](../refs/SOURCES.md) and
[`../refs/lecture-notes-map.md`](../refs/lecture-notes-map.md).

## Run everything

From the course folder (the venv is the repo venv, `uv sync` at the repo root):

```sh
uv run pytest src/py -q      # 363 tests, ~4 s
make -C src/cpp test                            # 5 programs, self-checking
for f in src/py/[!t]*.py; do uv run python $f; done           # demos
```

The built binaries `src/cpp/{lu,cg,qr,fft,rk4}` are git-ignored
(`cpp/.gitignore`).

## Python (`py/`)

One module per note, `numpy` only inside the algorithms (`numpy.linalg` /
`scipy` appear in the tests as cross-checks, and in a handful of places where a
factorisation is a means rather than the subject). Every module has a
`__main__` demo (`uv run python src/py/quad.py`) whose numbers are the
ones quoted in the notes, and a module docstring naming the algorithms and the
[S4] sections they implement.

| module | note | contents |
|---|---|---|
| `interp.py` | 01 | `lagrange_eval`, `barycentric_eval`, `divided_differences` / `newton_eval`, `chebyshev_nodes`, `thomas`, `cubic_spline` / `spline_eval`, `lstsq_normal`, `lstsq_qr`, `polyfit`, `orthogonal_polys` / `orthogonal_lstsq` |
| **`neville.py`** | 01, 12 | `aitken_neville` (with an operation counter), `neville_tableau`, `extrapolate_derivative`, `omega` / `omega_max` / `chebyshev_omega_max`, `lebesgue_function` / `lebesgue_constant` / `chebyshev_lebesgue_bound`, `hermite_divided_differences` / `hermite_eval` / `hermite` |
| `fft.py` | 02 | `dft`, `fft_recursive`, `fft_iterative`, **`fft_dif`** / **`ifft_dif`** ([S4] Alg. 3–4), `bit_reverse_permutation`, `ifft`, `convolve`, `fft_two_real`, `rfft`, **`trig_interp_coeffs`** / **`trig_interp_eval`**, **`dft_matrix`**, **`solve_circulant`** / **`circulant`** |
| `quad.py` | 03 | `newton_cotes_weights`, `midpoint`, `trapezoid`, `simpson`, `legendre`, `gauss_legendre`, `gauss_quad`, `romberg`, `adaptive_simpson`, **`adaptive_trapezoid`** ([S4] Alg. 5), **`graded_mesh`**, **`composite_trapezoid_mesh`**, **`gauss_chebyshev`**, **`gauss_jacobi`** |
| **`quad2d.py`** | 03 | `tensor_square`, `barycentre_triangle`, `vertex_triangle`, `duffy_triangle`, `monomial_integral_square` / `_triangle`, `exactness_degree_2d` |
| `errors.py` | 04 | `machine_epsilon`, `ulp`, naive / Kahan / pairwise summation, `quadratic_roots_naive` / `_stable`, `cond_scalar`, **`cond_rel`**, `cond`, `forward_backward_error`, `hilbert`, `error_sources_fd`, **`log1p_naive`** / **`log1p_series`** |
| `linsolve.py` | 05, 10 | `gauss_elim`, `lu_decompose` / `lu_solve`, `determinant`, `cholesky`, `jacobi`, `gauss_seidel`, `sor`, `sor_optimal_omega`, `conjugate_gradient`, `iteration_matrix`, `power_iteration`, `poisson_1d` |
| **`banded.py`** | 05 | `crout_lu` / `crout_lu_inplace` ([S4] Alg. 9–10), `bandwidths`, `banded_lu` (with an operation counter) / `banded_solve`, `banded_cholesky`, `skyline_profile` / `is_skyline_preserved` |
| **`ordering.py`** | 05 | [S4] §4.6 (CSE): `adjacency_graph`, `cuthill_mckee` / `reverse_cuthill_mckee` / `pseudo_peripheral_node` ([S4] Alg. 12–13), `minimum_degree` ([S4] Alg. 14), `symbolic_cholesky_nnz`, `poisson_2d_pattern` |
| `qr_svd.py` | 06, 07, 09 | `gram_schmidt_classical` / `_modified`, `householder_qr`, `qr_solve`, `power_method`, `qr_algorithm`, `jacobi_svd`, `low_rank`, `cond2` |
| **`givens.py`** | 06 | `givens_rotation`, `apply_givens_left` / `_right`, `givens_qr`, `hessenberg_qr`, `rq_product`, `is_hessenberg`, `qr_column_pivoting` |
| **`pseudoinverse.py`** | 07 | `reduced_svd`, `numerical_rank`, `pinv`, `lstsq_svd`, `min_norm_solution`, `project_range` / `project_kernel`, `svd_via_symmetric`, `normal_equations_solve`, `s4_example_5_6` |
| `nonlinear.py` | 08 | `bisection`, `fixed_point`, `newton`, `secant`, `newton_system`, `jacobian_fd`, `convergence_order`, **`simplified_newton`** |
| **`optimize.py`** | 08 | `armijo`, `steepest_descent`, `gradient_descent_quadratic`, `globalized_newton` ([S4] Alg. 15), `gauss_newton`, `sherman_morrison`, `broyden_update` / `broyden`, `s4_example_6_20` |
| **`eig.py`** | 09 | `rayleigh_quotient`, `subspace_angle`, `inverse_iteration`, `inverse_iteration_shift`, `rayleigh_quotient_iteration`, `eigen_residual_bound`, `orthogonal_iteration`, `hessenberg`, `wilkinson_shift`, `shifted_qr` |
| **`gmres.py`** | 10 | **`richardson`**, **`steepest_descent_linear`** ([S4] §8 basic methods), `arnoldi` (modified and standard Gram–Schmidt), `gmres` (Givens QR of the growing Hessenberg matrix), `gmres_restarted`, `cg_polynomial_bound` |
| `ode.py` | 11 | `euler`, `implicit_euler`, `heun`, `rk4_step` / `rk4`, `stability_function`, `real_stability_interval`, `rk45` (Dormand–Prince, FSAL: [S19], beyond [S4]) |
| **`irk.py`** | 11 | `butcher_explicit_euler` / `_heun` / `_rk4` / `_implicit_euler` / `_theta`, `theta_scheme`, `implicit_rk`, `stability_function_rational`, `is_a_stable`, `lambert_system` |
| **`bvp.py`** | 11 | `solve_ivp_shot`, `variational_rhs`, `shooting` ([S4] Alg. 30), `shooting_sensitivity` |
| `diff.py` | 12 | `forward_diff`, `backward_diff`, `central_diff`, `second_diff`, `fd_weights`, `optimal_h`, `richardson`, `gradient_fd` |

**Bold** modules and functions were added in the 2026-09-22 source pass; see
`../notes/CHANGELOG.md`.

`test_code_pointers.py` checks that every code pointer in `../notes`,
`../refs/lecture-notes-map.md` and this file (`module.function`, the
"Implementation" paragraphs, the table above, `test_<module>.py::name`) resolves to a
real function or file.

Module cross-imports (`interp` → `linsolve`, `qr_svd`; `ode` → `nonlinear`;
`neville`, `givens`, `pseudoinverse`, `gmres`, `eig`, `irk`, `bvp` → their
neighbours) are plain imports, so run from `src/py` or via pytest, which adds
the directory to the path.

## What the tests check

`test_<module>.py` compares against `numpy` / `scipy` and against analytic
values, but the point of the suite is the **second** column: every number the
course script prints is reproduced.

| [S4] reference | what is reproduced | where |
|---|---|---|
| Fig. 1.2 | the stalled $\sqrt h$ extrapolation table for $u=\lvert x\rvert^{3/2}$, to three digits | `test_neville.py` |
| Thm 1.21 | $\lVert\omega^{\mathrm{Cheb}}_{n+1}\rVert_\infty = 2((b-a)/4)^{n+1}$, and that no other knot set beats it | `test_neville.py` |
| Thm 1.24 | $\Lambda^{\mathrm{Cheb}}_n\le\tfrac2\pi\ln(n+1)+1$, and exponential growth for uniform knots | `test_neville.py` |
| Ex. 1.26 | $0.7183$ (Taylor), $0.3723$ (Chebyshev), $0.2788$ (Remez) for $e^x$ on $[-1,1]$ | `test_neville.py` |
| Alg. 3–4, Thm 1.45 | decimation in frequency against DIT and numpy; unitarity of $V_n/\sqrt n$ | `test_fft.py` |
| Ex. 1.57, 1.59 | $(1,2,3)*(4,5,6,7)=(4,13,28,34,32,21)$; circulant solves | `test_fft.py` |
| Fig. 2.2 | the closed Newton–Cotes weight table for $n=1..6$ | `test_quad.py` |
| Ex. 2.12 | $O(N^{-1.1})$ uniform against $O(N^{-2})$ graded, for $\int_0^1x^{0.1}$ | `test_quad.py` |
| Ex. 2.20 | the trapezoidal rule on the three periodic integrands | `test_quad.py` |
| Ex. 3.5 | $\log(1+x)$ at $x=1.234567890123456\cdot10^{-10}$: **both** MATLAB outputs, to 16 digits | `test_errors.py` |
| Ex. 3.6 | the quadratic roots for $p=400000$, $q=1.234567890123456$: both outputs | `test_errors.py` |
| §4.4.3 | the $\varepsilon=10^{-20}$ pivoting failure | `test_banded.py` |
| Fig. 4.5 | the printed Cholesky factor of the skyline matrix, entry by entry | `test_banded.py` |
| **Ex. 4.37** | **27 029 / 19 315** non-zeros for the lexicographic and RCM orderings of the $900\times900$ Poisson matrix, exactly | `test_ordering.py` |
| Ex. 4.54–4.55 | the $3\times3$ Hessenberg Givens QR; $n-1$ rotations; $RQ$ Hessenberg | `test_givens.py` |
| **Ex. 5.6** | **$1.011235955056180$ / $0.988764044943820$** from the normal equations against $(1,1)$ from QR | `test_pseudoinverse.py` |
| Thm 5.17, Ex. 5.19 | the Penrose identities; $\lVert A^+\rVert_2=\sigma_r^{-1}$ | `test_pseudoinverse.py` |
| **Ex. 6.2** | **all four $\sqrt2$ iterates and all four errors**, to 15 digits | `test_nonlinear.py` |
| **Ex. 6.7** | **all ten printed $\Phi_2$ iterates**, to 15 digits, and that $\Phi_1$ leaves the domain | `test_nonlinear.py` |
| Ex. 6.20 | Newton $\succ$ Broyden $\succ$ steepest descent on the $(0,1)$ system | `test_optimize.py` |
| Thm 7.1, 7.5, 7.7, 7.8 | the measured rates: $\lvert\lambda_2/\lambda_1\rvert$, the shifted rate, cubic Rayleigh | `test_eig.py` |
| Thm 7.10 | all three residual bounds, including a non-symmetric case where (ii) fails | `test_eig.py` |
| Thm 8.7 | the CG bound holds step by step on the 1-D Poisson matrix | `test_gmres.py` |
| Exercise 9.13, 9.15 | $R(z)$ for all five methods; A-stability true/false for each | `test_irk.py` |
| Ex. 9.11 | order 1 for $\theta\ne\tfrac12$, order **2** for $\theta=\tfrac12$ | `test_irk.py` |
| Ex. 9.12 | explicit Euler blows up at $h=0.05$ and behaves at $h=0.02$; implicit Euler at both | `test_irk.py` |
| Ex. 9.17, 9.18 | the three boundary problems; **one Newton step gives $s_0=1$ exactly** | `test_bvp.py` |

Two numbers in [S4] did **not** reproduce, and the tests say so:

- **Ex. 6.7**, $\lvert\Phi_2'(x^\ast)\rvert$: [S4] prints $0.31$, recomputing
  gives $0.6279$, and the ratio of successive errors in [S4]'s *own* printed
  iterate table is $-0.628$. A slip in the script; the conclusion is unaffected.
- **Ex. 4.37**, minimum-degree fill-in: [S4] reports 10 042 non-zeros, the exact
  greedy algorithm of [S4] Alg. 14 gives 10 351. [S4] says *approximate*
  minimum degree, whose tie-breaking differs.

One entry in **Ex. 4.54** is transcribed as $2/\sqrt2$ where recomputation gives
$1/\sqrt2$; the diagonal of $R$, which is what matters, matches.

## Past papers

There are no public exercise sheets: TISS and VoWi put them in TUWEL, which is
unverified here (TUWEL was not read). What is public is five past test papers
[S10, S11]; [`../notes/00-exam-focus.md`](../notes/00-exam-focus.md) lists the
topics they cover. Worked solutions to them are not part of this wiki.

## C++ (`cpp/`)

C++17, standard library only, `clang++ -std=c++17 -O2 -Wall -Wextra`.
`check.hpp` is a 30-line harness: `CHECK_NEAR(got, expect, tol)` /
`CHECK_LESS(got, bound)` print each check and `main` returns the failure count,
so `make test` fails on any mismatch.

| program | note | what it does and checks |
|---|---|---|
| `lu.cpp` | 05 | packed LU with partial pivoting, solve, determinant; the $3\times3$ hand example ($x=(1,1,2)$, $\det=-16$), a pivoting case, $n=200$ residual/error/growth factor, singular detection |
| `cg.cpp` | 10 | matrix-free CG on the 2-D Poisson 5-point stencil ($63\times63$, $\kappa=1659$); manufactured solution $x(1-x)y(1-y)$; iteration count $O(\sqrt\kappa)$ |
| `qr.cpp` | 06, 07 | Householder QR with stored reflectors, implicit $Q^\top b$, least squares; $\lvert r_{ii}\rvert=14,175,35$ on the classic $3\times3$, exact quadratic fit, the line through $(0,1),(1,2),(2,4)$ with residual $\sqrt{1/6}$, degree-12 Vandermonde |
| `fft.cpp` | 02 | in-place iterative radix-2 FFT and inverse, convolution; a pure tone in bins 5/59 with $\lvert X\rvert=32$, agreement with the $O(N^2)$ DFT, Parseval, $(1,2,3)*(4,5,6,7)$ |
| `rk4.cpp` | 11 | RK4 (observed order 4, oscillator energy, blow-up $=R(-5)^{20}$ at $z=-5$) and adaptive Dormand–Prince RK45 on Van der Pol $\mu=5$ against a fixed-step reference |

```sh
make -C cpp          # build
make -C cpp test     # run all five, exit non-zero on failure
make -C cpp clean
./cpp/cg             # any single program prints its results and checks
```
