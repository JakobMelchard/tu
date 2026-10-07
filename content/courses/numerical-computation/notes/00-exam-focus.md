# 00 Exam focus: what is actually asked

Built from five past papers of the same lecture, read on 2026-09-21. Read this
before deciding how much time to give a topic.

## The papers

| ref | paper | set by | course | date |
|---|---|---|---|---|
| **F1** | Test 1 | Faustmann | Computernumerik (VC) | 02.12.2022 |
| **F2** | Test 2 | Faustmann | Computernumerik (VC) | 26.01.2023 |
| **F3** | Test 3 (re-test, whole semester) | Faustmann | Computernumerik (VC) | 24.02.2023 |
| **F4** | Test 1, prose report only | Faustmann | Computernumerik (VC) | 2023W |
| **S1a** | Test 1 | Sturm | Computernumerik (VC) | 22.11.2024 |
| **S2a** | Test 2 | Sturm | Computernumerik (VC) | 22.01.2025 |

F1–F4 are on [S10], S1a/S2a on [S11]. **Markus Faustmann is the 2026W lecturer**
[S1] (with Bringmann), so F1–F4 are the closest thing to a model of the coming papers.

Two caveats, both important:

1. All six are papers of **101.484 Computernumerik (Visual Computing, 3.0 ECTS)**,
   not of 101.973. The lecture is the same and the lecturers are the same, but
   the Visual Computing course stops at [S4] §7.3 ("END OF LECTURE FOR VISUAL
   COMPUTING"). So **no past paper here touches CG, GMRES, ODEs, the QR
   algorithm, orthogonal iteration, Householder, Givens or the pseudoinverse**,
   and the CSE course examines all of those. Absence from this page is not
   evidence of absence from your exam. See
   [`../refs/lecture-notes-map.md`](../refs/lecture-notes-map.md) for the split.
2. The worked solutions in S1a/S2a are a student's own and say so on the first
   page. Two of them are wrong or garbled; noted below.

## Format

From [S8] and [S11], consistent across 2022W–2025W:

- **Grading: 33 points exercises + 66 points written tests.** Pass needs >50
  points overall, >60 % of exercise tasks checkmarked in TUWEL, a positive
  presentation grade, **and** >33 of the 66 written points. Grades 1–4 are then
  equally spaced in total points [S11].
- Two tests of 33 points each, one in November covering the first half, one in
  January covering the second. A third test at the end covers everything, for
  people who did not clear 33 with the first two [S11].
- **100 minutes** per test [S11]. Pencil and paper, no programming [S8].
- Exercises: 10 sheets × 5 tasks, checkmarked in TUWEL the day before, random
  selection to present at the blackboard [S11]. A mix of hand calculation with
  the algorithms and short proofs; the computational parts are done in
  Python/MATLAB [S11], and a Jupyter notebook is the recommended way [S11].
- **2026W changes this**: 6.0 ECTS and "Short tests, Collaboration in exercise,
  final overall test" instead of "Checkmark exercise and two tests" [S1]: see
  the diff table in [`../docs/tiss.md`](../docs/tiss.md). Treat the point split
  above as the prior, not as fact, until the first lecture.
- "Checkmarked in TUWEL" is the 2022W-2025W mechanism [S11]. The 2026W TUWEL
  course exists (id 82717) [S1], but it was not read for these notes: whatever
  2026W does in TUWEL (sheets, checkmarks, notes) is unverified.

## 2026W dates, state 2026-09-27

Exercise groups A-C start 13.10 [S1]; full table in
[`../docs/tiss.md`](../docs/tiss.md).


| slot | 2026W [S1] | same slot in 2024W / 2025W [S3, S2] | reading |
|---|---|---|---|
| Fri 20.11.2026 14:00-16:00, EI 9 Hlawka | "Reservation" | Test 1 (22.11.2024, 21.11.2025) | probably the first short test (inference) |
| Wed 27.01.2027 16:00-18:00, HS 18 Czuber | "Final Exam" | Test 2 (22.01.2025, 21.01.2026) | the "final overall test" |
| Fri 19.02.2027 13:00-15:00, DA 04 G10 | "Re-Test" | re-test (21.02.2025, 20.02.2026) | whole-semester re-test, like F3 |

If 20.11 is a test, it comes after about 7 weeks of lectures (06.10 to 20.11).
Both public first tests, F1 (02.12.2022) and S1a (22.11.2024), covered [S4]
§1-§3 only. Plan the §1-§3 hand-calculation drill (below) for early November.

## The shape of a paper

Five exercises. Consistently:

1. **Exercises 1–4: compute, then justify.** Small numbers, done by hand: a
   quadratic interpolant through three nodes, one quadrature rule on one
   integrand, three Newton steps, a $3\times3$ LU. Each part (b)/(c) then asks
   for the theory behind it: the error formula, the cost, the condition under
   which it works.
2. **Exercise 5 is always true/false plus fill-in-the-blank**, on complexity,
   convergence rates and definitions. It is cheap marks and it is where the
   "know the constants" work pays off. In F1, S1a and S2a this is a fifth of the
   paper.

[S8] puts it directly: the theory questions mostly examine **convergence of
algorithms, complexity, and errors**.

## What was asked, by topic

### Interpolation

- Write down the Lagrange polynomials $\ell_i$ for three given nodes and the
  resulting quadratic interpolant (S1a 1.1a; F1 1a with $g(x)=4/(x+1)$ on nodes
  $0,1,2$; F3 2.1b as a **Hermite** problem through $(\tfrac12,1)$, $(1,\tfrac32)$,
  $(2,5)$ *and* $f'(0)$).
- Set up the Vandermonde system $A\mathbf{x}=b$ for $p(x)=\alpha+\beta x+\gamma x^2$
  without solving it (S1a 1.1b).
- State the error formula $f-p=\omega_{n+1}\,f^{(n+1)}(\xi)/(n+1)!$ and use it to
  bound the error at one point (F1 1b/1c: show $|g(\tfrac12)-p(\tfrac12)|\le\tfrac32$;
  S1a 1.2a).
- **Define the Lebesgue constant** $\Lambda_n=\max_x\sum_i|\ell_i(x)|$ and state
  $\|f-I_nf\|_\infty\le(1+\Lambda_n)\min_{q\in\mathcal P_n}\|f-q\|_\infty$
  (S1a 1.2b/1.2c). Growth: $\tfrac2\pi\ln(n+1)+1$ for Chebyshev,
  $\sim 2^n/(en\ln n)$ for uniform (S1a 1.2c, 1.5a; F1 5b; F4).
- Why Chebyshev nodes are a good choice (S1a 1.1c, F3 2.1c, F4).
- Highest degree for which a unique interpolant through $n+1$ nodes is
  guaranteed, and what happens for lower/higher degree (F3 2.1a).

### Neville

Appears in the true/false block of **every** Faustmann paper: cost of evaluating
$p_n(x)$ with Neville is $O(n^2)$, not $O(n)$ (F1 5a, S1a 1.5b, F3 2.5a, F4);
the $m$-th column corresponds to polynomials of degree $m$ (F1 5a); Neville
beats direct evaluation of the Lagrange form (F1 5a).

### Quadrature

- Given a rule such as $Q(f)=\tfrac12 f(\tfrac13)+\tfrac12 f(\tfrac23)$ or
  $\tfrac12 f(\tfrac14)+\tfrac12 f(\tfrac34)$: apply it, compute the exact
  integral, give the error (F1 2a with $f=3x^2+1$ on $[0,1]$, error $\tfrac16$;
  S1a 1.3a, error $\tfrac1{48}$).
- **Determine the degree of exactness** by testing $1, x, x^2, \ldots$ (F1 2b,
  S1a 1.3b).
- Can the rule be improved by changing the weights? (No: $w_i=\int\ell_i$ is
  fixed by the nodes.) By changing the nodes? (Yes, up to $\mathcal P_3$ with
  Gauss points.) (F1 2c)
- **Gauss**: knots are the zeros of the Legendre polynomial, weights
  $w_i=\int\ell_i$; $n+1$ knots give exactness $2n+1$; weights are positive
  (F1 4, S1a 1.3c, 1.5c, F4).
- The optimality argument: no rule with $n+1$ knots integrates
  $f=\prod_i(x-x_i)^2$ exactly, since $\int f>0$ but $Q_n(f)=0$ (F1 4).
- Composite trapezoidal on an equidistant mesh: draw the mesh, state $h$,
  compute $\int_0^{3\pi/2} x\sin x\,dx$; write the error formula; **choose $h$
  so the error is below $0.01$** (F3 2.2, with the hint $(x\sin x)''=2\cos x-x\sin x$).
- Match convergence curves to rules: a smooth $e^x$ and a non-smooth $x^{0.1}$
  on $[0,1]$, curves for composite trapezoidal, composite Simpson and Gauss
  (F1 3, F4).
- Orders: composite trapezoidal 2, composite Simpson 4, Simpson's degree of
  exactness 3, midpoint exact on $\mathcal P_1$ (S1a 1.5c/1.5d, F3 2.5f).
- Newton–Cotes does **not** converge as $n\to\infty$ (F3 2.5c). The midpoint
  rule is **not** more efficient than Gauss (F3 2.5d).

### Conditioning and stability

- Bound the relative condition number of a given $\varphi$, say whether the
  problem is well conditioned, say what goes wrong numerically, **and give a
  stable implementation**. S1a 1.4 uses $\varphi(x)=\sqrt{2x+1}-1$, $x>0$:
  $\kappa_{\mathrm{rel}}=\tfrac12\big(1+(2x+1)^{-1/2}\big)\le1$, so the problem is
  fine, but near $x=0$ the formula cancels; multiply by the conjugate to get
  $2x/(\sqrt{2x+1}+1)$. This is [S4] Example 3.5/3.6 with different numbers.
- True/false: taking a square root is well conditioned (true); subtracting
  similar numbers is ill conditioned (true); *a well-conditioned problem always
  has a stable algorithm* (false); stability says whether a problem is solvable
  (false): it is about how the algorithm handles perturbations (F1 5c, S1a 1.5b).

### LU, Cholesky, linear systems

- Compute the LU factorisation of a small matrix with normalised $L$ (S2a 2.1a
  on a lower-triangular $3\times3$; F2 2.1 on $\begin{psmallmatrix}0&2&0\\3&4&1\\0&0&1\end{psmallmatrix}$).
- **Prove that a given matrix has no LU factorisation**, then permute and
  factor it (S2a 2.2a on $\begin{psmallmatrix}0&2\\4&1\end{psmallmatrix}$; F2 2.1;
  F3 2.3a "give an example where LU is impossible but possible with a pivot").
- Cost: LU is $O(n^3)$ ($\tfrac23n^3$), back substitution $O(n^2)$; how to solve
  $Bx=b$ in $O(n^2)$ given $B=LU$ (S2a 2.1b/2.1c).
- Cholesky: does a given matrix have one, and why; compute it for a $2\times2$
  SPD matrix (S2a 2.2b/2.2c). True/false: "Cholesky costs twice LU": **false**,
  it costs about half ([S4] Remark 4.16) (S2a 2.5a).
- Crout's algorithm is a way to compute LU: true (S2a 2.5b).
- Fill-in blanks: complexity of QR for $A\in\mathbb R^{n\times n}$; complexity of
  Gaussian elimination; definition of an orthogonal matrix (S2a 2.5d).

### Least squares and SVD

- Define the least-squares solution for $m>n$ (S2a 2.3a).
- A word problem: a rectangle with sides $a,b$; three measurements
  $a\approx15$, $b\approx21$, $a+b\approx39$; find refined $a,b$ by least
  squares (S2a 2.3b). Solve a given $3\times2$ system in the same way (F2 2.4).
- True/false: the normal equation is "$A^\top Ax=b$": **false**, it is
  $A^\top Ax=A^\top b$ (S2a 2.5c); $m<n$ is underdetermined (true).
- **SVD as a long essay question**: what it is, when you need it, what $U$,
  $\Sigma$, $V$ contain, how $\sigma_i^2$ relate to the eigenvalues of
  $A^\top A$, how $\sigma_r$ gives the rank (F2 2.5). True/false: "SVD is used
  for overdetermined systems": false as posed in F3 2.5g (its role there is the
  *under*determined/minimum-norm case, [S4] §5.3).

### Nonlinear equations

- Three Newton steps by hand on $f(x)=x^2-2$ from $x_0=2$ (S2a 2.4a) or on
  $f(x)=x^2+3x-4$ from $x_0=1$ (F2 2.2b). [S4] Example 6.2 is the same problem:
  $1.5$, $1.41\overline{6}$, $1.4142156862745098$, $1.4142135623746899$.
- Under which conditions is Newton quadratically convergent, and what does
  quadratic convergence mean (S2a 2.4b, F3 2.4b).
- Why $g(x)=x^2$ from $x_0=1$ is **only linear** (double root, $f'(x^*)=0$)
  (S2a 2.4c; [S4] Exercise 6.10).
- Fixed-point iteration: does it converge for a given $g$ and $x_0$ (F2 2.2a);
  define a contraction and relate it to fixed points and Newton (F3 2.4a).
- True/false: the quadratic-convergence proof for 1-D Newton rests on
  fixed-point theory: **true** ([S4] Cor. 6.9 via Thm 6.8) (S2a 2.5b).
- The **Armijo rule** is a way to choose the step length in a descent method:
  true (S2a 2.5c). This is the only globalisation item seen in a paper.

### Eigenvalues

- "Choose an eigenvalue algorithm for a given problem and justify it: e.g.
  choose Rayleigh, describe its advantages and disadvantages, and write down the
  algorithm" (F2 2.3).
- **Compare inverse iteration with shift against Rayleigh quotient iteration**:
  pros, cons, what each does (F3 2.3b).
- Convergence of the power method: $C|\lambda_2/\lambda_1|^\ell$ (F3 2.5e).

## How to prepare

1. **Memorise the constants.** Orders, degrees of exactness, flop counts,
   Lebesgue growth, convergence rates. Exercise 5 is a fifth of the paper and
   is pure recall.
2. **Be able to run every algorithm on a $3\times3$ or three nodes by hand.**
   Neville, Newton's divided differences, LU with a pivot, Cholesky, one Givens
   rotation, three Newton steps, one quadrature rule.
3. **Learn the two error formulas cold** (interpolation
   $\omega_{n+1}f^{(n+1)}(\xi)/(n+1)!$ and composite trapezoidal
   $\tfrac{(b-a)}{8}h^2\|f''\|_\infty$ [S4 Thm 2.8]) because the "choose $h$ so
   the error is below $\varepsilon$" question is asked from them (F3 2.2c).
4. **Practise the conditioning question**: given $\varphi$, compute
   $\kappa_{\mathrm{rel}}=|\varphi'||x|/|\varphi|$, simplify to a bound, spot the
   cancellation, rationalise. It has appeared in this exact form repeatedly.
5. **Do not skip the CSE-only chapters** because no past paper here shows them.
   §7.4–§9 are a quarter of the script and the reason this course is 6.0 ECTS.

## Our exam-style questions

Every note's "Exam-style questions" section says which paper above its questions
are modelled on. Questions with no attribution are ours, written to cover a
CSE-only topic that no public paper reaches.
