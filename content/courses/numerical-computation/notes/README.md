# 101.973 Numerical Computation: notes

101.973 VU, 6.0 ECTS, 2026W, Faustmann and Bringmann, E101 Analysis and
Scientific Computing [S1]. Exercise groups A-C on Tue, see
[`../docs/tiss.md`](../docs/tiss.md).


**Ordered by the lecture, not by topic convenience.** The order and the scope
come from [S4], the course's own script (Melenk & Faustmann, *Lecture Notes
Numerical Computation*, TU Wien, WS 2023/24), written by one of the two 2026W
lecturers for his own last run of this course. Every source is registered in
[`../refs/SOURCES.md`](../refs/SOURCES.md) and cited inline as `[S<n>]`.
Section-by-section correspondence in
[`../refs/lecture-notes-map.md`](../refs/lecture-notes-map.md).

TISS names no textbook: "There will be lecture notes in TUWEL!" [S1]. The
2026W TUWEL course (id 82717) was not read for these notes, so whether 2026W
notes are there, and what they contain, is unverified. Students reported the 2025W TUWEL notes
as outdated relative to the lecture [S8]. So [S4] is the authority here, with
standard references [S12, S15, S16, S19] used only where it is silent and
flagged where they are. The [S4] PDF itself is not vendored
(`../refs/fetch-sources.sh` downloads it); the notes were written from it
on 2026-09-21/22.

**Read [00 Exam focus](00-exam-focus.md) first.** It digests five past papers of
the same lecture, three of them set by Faustmann.

## The notes

`CSE` marks a chapter or section [S4] flags **(CSE)**, or that falls after
"END OF LECTURE FOR VISUAL COMPUTING" at the end of §7.3. Those are in this
course and not in the Visual Computing variant, which is why no public past
paper covers them.

| # | Note | [S4] | CSE | Contents |
|---|---|---|---|---|
| 00 | [Exam focus](00-exam-focus.md) | - | | format, grading, what five past papers asked, how to prepare |
| 01 | [Polynomial interpolation](01-polynomial-interpolation.md) | §1.1–1.8 | part | Lagrange, uniqueness, **Neville**, Newton/divided differences, extrapolation, the error formula, Chebyshev points, **Lebesgue constant**, **Hermite**, splines |
| 02 | [Trigonometric interpolation and FFT](02-trigonometric-interpolation-and-fft.md) | §1.9 | ● | trigonometric interpolation, DFT matrix, FFT (decimation in frequency), convolution theorem, circulant systems |
| 03 | [Numerical integration](03-numerical-integration.md) | §2 | part | Newton–Cotes, composite error theorem, Romberg, graded meshes and adaptivity, Gauss–Legendre, periodic integrands, 2-D quadrature |
| 04 | [Conditioning and error analysis](04-conditioning-and-error-analysis.md) | §3 | | error sources, $\kappa_{\mathrm{abs}}$/$\kappa_{\mathrm{rel}}$, cancellation, stability of algorithms; floating point and backward error as background |
| 05 | [Gaussian elimination and LU](05-gaussian-elimination-and-lu.md) | §4.1–4.6 | part | substitution, LU, **Crout**, **banded**, Cholesky, **skyline**, pivoting, $\kappa(A)$, **fill-in, RCM, minimum degree** |
| 06 | [QR factorisation](06-qr-factorisation.md) | §4.7 | part | orthogonal matrices, Gram–Schmidt, **Householder**, **QR with pivoting**, **Givens and Hessenberg** |
| 07 | [Least squares and SVD](07-least-squares-and-svd.md) | §5 | part | normal equations, least squares via QR, underdetermined systems, SVD, low-rank approximation, **Moore–Penrose pseudoinverse** |
| 08 | [Nonlinear equations and Newton](08-nonlinear-equations-and-newton.md) | §6 | part | Newton 1-D and $\mathbb R^d$, contractions and order $p$, damping, descent and **Armijo**, Gauss–Newton, **Broyden**, **trust region** |
| 09 | [Eigenvalue problems](09-eigenvalue-problems.md) | §7 | part | power method, **inverse iteration with shift**, **Rayleigh quotient iteration**, residual bounds, **orthogonal iteration**, **QR algorithm with Hessenberg, deflation and shifts** |
| 10 | [Iterative linear systems](10-iterative-linear-systems.md) | §8 | ● | Richardson/Jacobi/Gauss–Seidel, gradient method, Krylov spaces, **CG** and its $\sqrt\kappa$ rate, **Arnoldi and GMRES** |
| 11 | [Ordinary differential equations](11-ordinary-differential-equations.md) | §9 | ● | explicit/implicit Euler, convergence proof, Butcher tableaux, RK4, **implicit RK and the θ-scheme**, stiffness, **A-stability**, **shooting for BVPs** |
| 12 | [Numerical differentiation](12-numerical-differentiation.md) | *(none)* | | appendix: the TISS subject line names it, [S4] has no such chapter: it appears as Neville extrapolation (§1.4). Stencils, the $h$ trade-off, Richardson |

**Bold** entries are topics added in the 2026-09-21/22 source pass; see
CHANGELOG.md.

## Each note

Follows `../../../docs/coursework-conventions.md`:
what the topic is, the definitions and results with formulas, a worked numeric
example, pitfalls, exam-style questions with short answers, and pointers into
[`../src`](../src/README.md). Exam-style questions say which past paper they are
modelled on, or are marked *(ours)*, which, for a CSE-only chapter, is all of
them.

Every claim carries a `[S<n>]` citation, or is marked
*(background, not in [S4])* where it is standard material the course does not
cover but the implementations need.

## Notation

$u=2^{-53}$ unit round-off, $\varepsilon=2u$ machine epsilon, $\kappa$ condition
number, $h$ step size or mesh width, $O(h^p)$ order $p$, $\Lambda_n$ Lebesgue
constant, $\omega_{n+1}(x)=\prod_i(x-x_i)$ the node polynomial,
$\mathcal P_n$ the polynomials of degree $\le n$. [S4] writes Cholesky as
$A=CC^\top$ and uses $\ell$ for the iteration index; we follow it.

## What the course examines

From [S8]: "convergence of algorithms, complexity, errors". From the past
papers: hand calculation on $3\times3$ matrices or three nodes, followed by the
theory behind it, plus a true/false block on constants and complexities. The
constants worth memorising are collected in
[00 Exam focus](00-exam-focus.md) §"How to prepare".
