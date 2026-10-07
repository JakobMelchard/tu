# 04 Conditioning and error analysis

[S4] §3: only **four pages** of the script (pp. 54–57), but they carry a whole
exam question in every paper, always in the same shape: *given $\varphi$, bound
$\kappa_{\mathrm{rel}}$, say whether the problem is well conditioned, say what
goes wrong numerically, give a stable implementation.* Sections 1–3 below are
the course; sections 4–5 are standard material [S12, S13] that [S4] does not
cover but that the implementations and note
[12](12-numerical-differentiation.md) rely on, and are marked as such.
Implementation: `src/py/errors.py`.

## 1. Where errors come from [S4 §3.1]

Four sources, named in this order:

1. **Modelling error**: the mathematical model neglects effects (continuum
   models vs the atomic structure of a solid).
2. **Measurement error**: the model's parameters were measured.
3. **Round-off error**: computers use finite-precision numbers, so every
   floating-point operation is inexact.
4. **Discretisation error**: the numerical method is not exact. The examples
   [S4] names are numerical differentiation and integration.

Errors are measured in norms ([S4] Appendix A.2).

The split that matters for this course: **conditioning** is a property of the
*problem* and governs how sources 1–2 propagate; **stability** is a property of
the *algorithm* and governs source 3. Source 4 is the $O(h^p)$ of every other
note.

## 2. Conditioning [S4 §3.2]

**Definition** [S4 Def. 3.1]. The condition number of a problem, seen as
evaluating a function $f$, is the worst-case amplification of input
perturbations:
$$\|f(x)-f(x+\Delta x)\|\le\kappa_{\mathrm{abs}}(x)\,\|\Delta x\|,\qquad
\frac{\|f(x)-f(x+\Delta x)\|}{\|f(x)\|}\le\kappa_{\mathrm{rel}}(x)\,\frac{\|\Delta x\|}{\|x\|},$$
each being the smallest such number for all sufficiently small $\Delta x$.

For $f:\mathbb R\to\mathbb R$ in $C^1$, Taylor gives
$$\boxed{\;\kappa_{\mathrm{abs}}(x)=|f'(x)|,\qquad \kappa_{\mathrm{rel}}(x)=\frac{|f'(x)|}{|f(x)|}\,|x|\;}$$
A problem is **well conditioned** if $\kappa_{\mathrm{rel}}$ is moderate and
**ill conditioned** if it is large; [S4] is explicit that "moderate" and "large"
are vague and depend on what the answer is for.

Worked cases from [S4]:

- **Addition of positives is well conditioned** [S4 Ex. 3.2]: for $x,y>0$ with
  relative input errors $\le\delta$,
  $\frac{|\Delta x|+|\Delta y|}{x+y}\le\frac{\delta x+\delta y}{x+y}=\delta$, so
  $\kappa_{\mathrm{rel}}\le1$.
- **Subtraction of similar numbers is ill conditioned**: *cancellation*
  [S4 Ex. 3.3]. With
  $x_1=1.2345689?$, $x_2=1.2345679?$ (relative input uncertainty $10^{-8}$),
  $x_1-x_2=1.1?\cdot10^{-6}$ has relative uncertainty $\approx10^{-2}$: six
  digits gone. In general
  $$\kappa_{\mathrm{rel}}(a,b)=\frac{|a|+|b|}{|a-b|}\qquad\text{for }f(a,b)=a-b,$$
  here $\approx1.8\cdot10^6$.
- **Multiplication and division are well conditioned** [S4 Exercise 3.4]:
  $\kappa_{\mathrm{rel}}=1$ for each argument.
- $\sqrt{\cdot}$: $\kappa_{\mathrm{rel}}=\tfrac12$, always well conditioned.
- $e^x$: $\kappa_{\mathrm{rel}}=|x|$. $1-\cos x$: $\kappa_{\mathrm{rel}}\to2$ as
  $x\to0$, so the *problem* is fine and only the *formula* is bad.

**Matrices** [S4 §4.5], the same idea one chapter later. With an induced norm
$\|A\|=\max_{x\ne0}\|Ax\|/\|x\|$, perturbing the right-hand side of $Ax=b$ gives
$$\frac{\|\Delta x\|}{\|x\|}\le\underbrace{\|A\|\,\|A^{-1}\|}_{=:\ \kappa(A)}\frac{\|\Delta b\|}{\|b\|},$$
and perturbing the matrix gives
$\frac{\|\Delta x\|}{\|\tilde x\|}\le\kappa(A)\frac{\|\Delta A\|}{\|A\|}$
[S4 Rem. 4.32]. $\varepsilon\,\kappa(A)$ is the best relative accuracy one can
hope for [S4 Rem. 4.31]: the "you lose $k$ digits when $\kappa\approx10^k$" rule
of thumb. $\kappa_2(A)=\sigma_{\max}/\sigma_{\min}$ (note
[07](07-least-squares-and-svd.md)); $\kappa(Q)=1$ for orthogonal $Q$ (note
[06](06-qr-factorisation.md)); $\kappa\ge1$ always. Hilbert matrices
$H_{ij}=1/(i+j-1)$ are the standard ill-conditioned family:
$\kappa_\infty(H_3)=748$, $\kappa_\infty(H_5)=9.4\cdot10^5$,
$\kappa_\infty(H_8)=3.4\cdot10^{10}$ (`errors.cond`, computed from our own LU
inverse).

## 3. Stability of algorithms [S4 §3.3]

An algorithm realises $f$ as a composition $f=f_1\circ f_2\circ\cdots\circ f_N$
of elementary steps, and computes $\hat f=\hat f_1\circ\cdots\circ\hat f_N$
because each step is inexact. An error made in $\hat f_i$ is then amplified by
$\hat f_1,\ldots,\hat f_{i-1}$. **A stability analysis looks for an
ill-conditioned sub-problem $f_i$ inside a well-conditioned $f$, and replaces the
decomposition.** In every example the culprit is cancellation.

**Example A: $f(x)=\log(1+x)$ for small $x$** [S4 Ex. 3.5]. The problem is fine:
$$\kappa_{\mathrm{rel}}(x)=\frac{|x|}{(1+x)|\log(1+x)|}\le2\quad\text{near }0.$$
The naive algorithm is $x\mapsto w:=1+x\mapsto\log w$, and the second step has
$$\kappa_{\mathrm{rel}}(w)=\frac{1}{|\log w|}=\frac1{\log(1+x)}\approx\frac1x,$$
so for $x=10^{-10}$ one expects to lose 10 digits. In MATLAB, for
$x=1.234567890123456\cdot10^{-10}$ the naive route gives
$1.234568003306966\cdot10^{-10}$ against the true
$1.234567890047248\cdot10^{-10}$: **6 correct digits out of 16**. Using
$f(x)=x-\tfrac12x^2+\tfrac13x^3-\cdots$ instead, $x-\tfrac{x^2}2$ already gives
all 16. The diagnosis generalises: *the final result is small while the
intermediate results are large relative to it*: fear a subtraction of similar
numbers. In code, `log1p` and `expm1` exist for exactly this.

**Example B: the quadratic equation $x^2-2px-q=0$** [S4 Ex. 3.6]. The roots are
$x_{0}=p-\sqrt{p^2+q}$, $x_1=p+\sqrt{p^2+q}$. For $p,q>0$ with $p^2\gg q$ the
formula for $x_0$ cancels. Multiply by the conjugate:
$$x_1=p+\sqrt{p^2+q},\qquad x_0=\frac{-q}{p+\sqrt{p^2+q}}=-\frac{q}{x_1}.$$
With $p=400000$, $q=1.234567890123456$: the naive $x_0$ gives
$-1.543201506137848\cdot10^{-6}$ against the true
$-1.543209862651343\cdot10^{-6}$; the rearranged one is correct to all 16
digits. (`errors.quadratic_roots_naive` / `errors.quadratic_roots_stable`.)

## 4. Floating-point numbers *(background, not in [S4])*

[S4] never writes down the floating-point model; it says only that the
elementary operations "cannot be realized exactly". The standard facts
[S13, S14]:

IEEE 754 binary64: $x=\pm(1.d_1\ldots d_{52})_2\cdot2^e$, $e\in[-1022,1023]$;
53 significant bits, 11 exponent bits, 1 sign bit; $\pm0$, $\pm\infty$, NaN and
subnormals below $2^{-1022}$.

| | binary32 | binary64 |
|---|---|---|
| precision $p$ (bits) | 24 | 53 |
| machine epsilon $\varepsilon=2^{1-p}$ | $1.19\cdot10^{-7}$ | $2.22\cdot10^{-16}$ |
| unit round-off $u=\varepsilon/2$ | $5.96\cdot10^{-8}$ | $1.11\cdot10^{-16}$ |
| largest finite | $3.4\cdot10^{38}$ | $1.8\cdot10^{308}$ |

$\varepsilon$ is the gap between $1$ and the next double, $\mathrm{ulp}(1)$; in
general $\mathrm{ulp}(x)=2^{\lfloor\log_2|x|\rfloor-p+1}$, so spacing is
*relative* (`errors.ulp`). Every number in the table is checked against
`numpy.finfo` in `test_errors.py`.

**Standard model** [S12 §2.2]: round to nearest gives
$\mathrm{fl}(x)=x(1+\delta)$ and
$\mathrm{fl}(a\circ b)=(a\circ b)(1+\delta)$ with $|\delta|\le u$, for
$\circ\in\{+,-,\times,/,\sqrt{\ }\}$. A product of $n$ such factors is
$1+\theta_n$ with $|\theta_n|\le nu/(1-nu)=:\gamma_n$. Floating-point addition is
commutative but **not associative**: $(10^{16}+1)-10^{16}=0$ while
$10^{16}+(1-10^{16})=1$.

**Summation** [S12 ch. 4]. Recursive summation of $n$ numbers has error
$\le\gamma_{n-1}\sum|x_i|$, linear in $n$; pairwise summation
$\gamma_{\lceil\log_2n\rceil}$; Kahan compensated summation
$2u\sum|x_i|+O(nu^2)$, independent of $n$ to first order. Demo
(`errors.py` `__main__`): summing $10^6$ copies of $0.1$ in float32 gives
$100958.34$ naively, $100000.0078$ pairwise, $100000.0$ with Kahan.

## 5. Forward error, backward error *(background, not in [S4])*

For a computed $\hat y$ against the exact $y=f(x)$:

- **forward error** $\|\hat y-y\|/\|y\|$: what we want, usually unknowable;
- **backward error**: the smallest $\|\Delta x\|/\|x\|$ with
  $\hat y=f(x+\Delta x)$ *exactly*: "which nearby problem did we solve exactly?";
- an algorithm is **backward stable** if the backward error is $O(u)$ for every
  input;
- **rule**: forward error $\lesssim\kappa\cdot$ backward error.

A backward-stable algorithm on an ill-conditioned problem still returns a large
forward error, and that is the *problem's* fault, not the algorithm's. This is
the precise version of [S4]'s informal "stability of algorithms", and it is why
S1a 1.5b marks *"if a problem is well conditioned then any algorithm realising it
is stable"* as **false**.

For linear systems the backward error is computable from the residual
$r=b-A\hat x$ (Rigal–Gaches [S12 Thm 7.1]):
$$\eta(\hat x)=\frac{\|r\|}{\|A\|\,\|\hat x\|},\qquad \frac{\|\hat x-x\|}{\|x\|}\le\kappa(A)\,\eta(\hat x)\ \text{(to first order)}.$$
Worked example (`errors.forward_backward_error`), $H_6$ with $x=(1,\ldots,1)$
solved by our LU: backward error $3.9\cdot10^{-11}$, actual forward error
$1.2\cdot10^{-9}$, bound $\kappa\eta=1.1\cdot10^{-3}$. **A small residual does
not mean a small error** when $\kappa$ is large; it means the algorithm behaved.

Status of the algorithms in these notes [S12, S16]: Gaussian elimination with
partial pivoting is backward stable in practice
($\|\Delta A\|\le\gamma_{3n}\rho_n\|A\|$ with growth factor $\rho_n$ almost
always small but $2^{n-1}$ in the worst case); Householder QR and Cholesky are
unconditionally backward stable; the normal equations are not, because they
square $\kappa$ (note [07](07-least-squares-and-svd.md)).

## Pitfalls

- Treating $\kappa$ as an algorithm property. It is a *problem* property;
  stability is the algorithm's.
- Concluding "small residual $\Rightarrow$ accurate solution". Only when $\kappa$
  is small.
- Thinking cancellation *creates* error. It exposes rounding that happened
  earlier, so the fix goes *before* the subtraction: $1-\cos x=2\sin^2(x/2)$,
  $\log(1+x)$ via its series or `log1p`, $e^x-1$ via `expm1`, the quadratic
  formula via Vieta [S4 Ex. 3.5, 3.6].
- Mixing $\varepsilon=2^{-52}$ and $u=2^{-53}$; both are called "machine
  precision" in the literature.
- Testing `a == b` on floats. Use $|a-b|\le\mathrm{tol}\cdot\max(1,|a|,|b|)$.
- Computing $\kappa_{\mathrm{rel}}$ and forgetting the $|x|/|f(x)|$ factor:
  $|f'|$ alone is the *absolute* condition number.
- Shrinking $h$ "to be safe" in a finite difference; below $h_{\mathrm{opt}}$ the
  answer gets worse (note [12](12-numerical-differentiation.md)).

## Exam-style questions

Modelled on S1a 1.4 and the true/false blocks of F1 5c and S1a 1.5b; see
[00](00-exam-focus.md). Item 1 is the recurring one: expect a variant of it.

1. *(S1a 1.4, 2024W)* $\varphi(x)=\sqrt{2x+1}-1$, $x>0$. Bound the relative
   condition number. Is the problem well conditioned? What goes wrong near
   $x=0$? Give a stable implementation.
   $\varphi'(x)=(2x+1)^{-1/2}$, so
   $$\kappa_{\mathrm{rel}}=\frac{|\varphi'|}{|\varphi|}|x|=\frac{x}{\sqrt{2x+1}\,(\sqrt{2x+1}-1)}
   =\frac{x(\sqrt{2x+1}+1)}{\sqrt{2x+1}\cdot 2x}=\frac12\Big(1+\frac1{\sqrt{2x+1}}\Big)\le1 .$$
   Well conditioned for every $x>0$. Near $0$ the *formula* subtracts two nearly
   equal numbers. Rationalise:
   $\varphi(x)=\dfrac{2x}{\sqrt{2x+1}+1}$: only $\sqrt{\ }$, $+$, $/$, all well
   conditioned.
2. *(same shape, ours)* Do the same for $\varphi(x)=1-\cos x$ near $x=0$.
   $\kappa_{\mathrm{rel}}=\dfrac{x\sin x}{1-\cos x}\to2$: well conditioned.
   The formula cancels; use $2\sin^2(x/2)$.
3. *(F1 5c / S1a 1.5b: true or false)*
   (i) Taking the square root of a positive number is well conditioned. **True**
   ($\kappa_{\mathrm{rel}}=\tfrac12$).
   (ii) If a problem is well conditioned then any algorithm realising it is
   stable. **False**: Example A above.
   (iii) Stability tells you whether a problem is solvable. **False**; it says
   how the algorithm handles perturbations.
   (iv) Fill in: subtracting two similar numbers is **ill** conditioned.
4. *(S1a-style)* Name the four error sources [S4] lists and say which of them
   conditioning governs.
   Modelling, measurement, round-off, discretisation. Conditioning governs how
   modelling and measurement errors (and, with the algorithm's stability,
   round-off) reach the answer; discretisation error is the method's own
   $O(h^p)$.
5. *(ours)* $\kappa_\infty(A)=10^{12}$ and you solve $Ax=b$ with a backward-stable
   solver in double precision. How many correct digits can you expect?
   About $16-12=4$: $\varepsilon\kappa(A)\approx10^{-4}$ [S4 Rem. 4.31]. The
   residual will still be $\sim10^{-16}\|A\|\|x\|$.
6. *(ours)* Why does $x_0=p-\sqrt{p^2+q}$ lose accuracy for $p^2\gg q>0$, and
   what is the fix?
   Cancellation between $p$ and $\sqrt{p^2+q}\approx p$. Compute the
   well-conditioned root $x_1=p+\sqrt{p^2+q}$ and use $x_0=-q/x_1$
   [S4 Ex. 3.6].

## Implementation

`src/py/errors.py`: `machine_epsilon`, `ulp`, `naive_sum` / `kahan_sum` /
`pairwise_sum`, `quadratic_roots_naive` / `quadratic_roots_stable`,
`cond_scalar`, `cond` (via our own LU inverse), `forward_backward_error`,
`hilbert`, `error_sources_fd`, **`log1p_naive`** / **`log1p_series`**
([S4 Ex. 3.5]).

Tests `test_errors.py`: against `np.finfo`, `np.spacing`, `np.linalg.cond`,
`np.roots`; plus the two [S4] stability examples reproduced to the digit
($\log(1+1.234567890123456\cdot10^{-10})$ and the $p=400000$,
$q=1.234567890123456$ quadratic) and the $\kappa_{\mathrm{rel}}\le1$ bound of
the S1a 1.4 exam item.
