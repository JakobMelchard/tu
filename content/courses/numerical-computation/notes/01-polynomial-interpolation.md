# 01 Polynomial interpolation

[S4] §1.1–1.8, the first chapter of the lecture and the largest single block of
exam questions ([00](00-exam-focus.md)). Find an easy function (here a
polynomial) that matches given data exactly, then use it to extrapolate,
differentiate, integrate or plot. Everything in notes [03](03-numerical-integration.md)
and [12](12-numerical-differentiation.md) is built on the error formula below.
Implementation: `src/py/interp.py`, `src/py/neville.py`.

## 1. Existence, uniqueness, and three bases

Given $n+1$ **distinct** knots $x_0,\ldots,x_n$ and values $f_i$, find
$p\in\mathcal P_n$ with $p(x_i)=f_i$ [S4 (1.1)].

**Lagrange basis** [S4 Def. 1.1]:
$$\ell_i(x)=\prod_{\substack{j=0\\ j\ne i}}^{n}\frac{x-x_j}{x_i-x_j},\qquad \ell_i(x_j)=\delta_{ij}.$$
The $\ell_i$ are $n+1$ linearly independent elements of the $(n+1)$-dimensional
$\mathcal P_n$, hence a basis, and $p=\sum_i f_i\ell_i$ [S4 Thm 1.2].

**Uniqueness** [S4 Thm 1.2]: two interpolants differ by a polynomial of degree
$\le n$ with $\ge n+1$ zeros, so by the fundamental theorem of algebra the
difference is $\equiv 0$. Written as a linear system this is the **Vandermonde**
matrix $V_{ij}=x_i^{\,j}$ with $\det V=\prod_{i<j}(x_j-x_i)\ne0$; do *not* solve
it numerically, $\kappa(V)$ grows exponentially [S15].

**Barycentric** rewriting of the Lagrange form: $O(n)$ per evaluation after
$O(n^2)$ setup, and numerically stable:
$$p(x)=\frac{\sum_j \frac{w_j}{x-x_j}f_j}{\sum_j \frac{w_j}{x-x_j}},\qquad w_j=\frac1{\prod_{m\ne j}(x_j-x_m)}.$$
*(Not in [S4]; kept because it is the form every library uses [S20]. `interp.barycentric_eval`.)*

## 2. Neville scheme [S4 §1.2]: exam staple

Evaluating $\sum_i f_i\ell_i(x)$ directly is wasteful. Let $p_{j,m}\in\mathcal P_m$
interpolate $(x_k,f_k)$ for $k=j,\ldots,j+m$. Then [S4 Thm 1.4]
$$p_{j,0}=f_j,\qquad p_{j,m}(x)=\frac{(x-x_j)\,p_{j+1,m-1}(x)-(x-x_{j+m})\,p_{j,m-1}(x)}{x_{j+m}-x_j},$$
and the answer is $p(x)=p_{0,n}(x)$. In place, overwriting the data vector
[S4 Alg. 1, "Aitken–Neville"]:

```
for m = 1..n:
    for j = 0..n-m:
        f[j] := ((x - x[j])*f[j+1] - (x - x[j+m])*f[j]) / (x[j+m] - x[j])
return f[0]
```

**Cost $O(n^2)$ arithmetic operations** [S4 Rem. 1.6]: asked in four of the five
past papers, always as "is it $O(n)$? No, $O(n^2)$". The knots need not be
sorted, and a new data point is one extra row at the bottom, so the scheme is
incremental. (`neville.aitken_neville`, `neville.neville_tableau`.)

## 3. Newton form and divided differences [S4 §1.3] (CSE)

Neville costs $O(n^2)$ *per evaluation point*. For many evaluation points, change
basis to the **Newton polynomials** $\omega_j(x)=\prod_{i<j}(x-x_i)$ [S4 Def. 1.7]
and evaluate with **Horner** in $O(n)$ [S4 Alg. 2]:
$$p(x)=d_0+(x-x_0)\big[d_1+(x-x_1)[d_2+\cdots]\big].$$
The coefficients are the **divided differences** [S4 Def. 1.10, Thm 1.11]:
$$f[x_i]=f_i,\qquad f[x_0,\ldots,x_k]=\frac{f[x_1,\ldots,x_k]-f[x_0,\ldots,x_{k-1}]}{x_k-x_0},\qquad d_k=f[x_0,\ldots,x_k].$$
Proof idea: $f[x_j,\ldots,x_{j+k}]$ is the **leading coefficient** of $p_{j,k}$;
induct using the Neville recursion [S4 (1.13)]. Cost $O(n^2)$ once, $O(n)$ per
point afterwards. Divided differences are symmetric in the knots and
$$f[x_0,\ldots,x_k]=\frac{1}{k!}f^{(k)}(\xi),\qquad \xi\in(\min x_i,\max x_i)\quad\text{[S4 Rem. 1.12]},$$
so they are scaled derivatives, which is exactly why coincident knots give
Hermite interpolation (§5) and why the Neville columns converge (§4).

Worked example (`interp.divided_differences`): knots $(0,1,2,4)$, values
$(1,3,2,5)$.

$$\begin{array}{c|cccc} x & f & f[\cdot,\cdot] & f[\cdot,\cdot,\cdot] & f[\cdot,\cdot,\cdot,\cdot] \\ \hline 0 & 1 \\ & & 2 \\ 1 & 3 & & -3/2 \\ & & -1 & & 7/12 \\ 2 & 2 & & 5/6 \\ & & 3/2 \\ 4 & 5 \end{array}$$

$p(x)=1+2x-\tfrac32x(x-1)+\tfrac7{12}x(x-1)(x-2)$, so $p(3)=1+6-9+3.5=1.5$.

## 4. Extrapolation, the point of the Neville scheme [S4 §1.4]

The prime application is a value that is not directly accessible. For a
derivative at $0$ put $D(h)=\big(f(h)-f(0)\big)/h$; $\lim_{h\to0}D(h)=f'(0)$
exists but $D(0)$ cannot be evaluated. Compute $D(h_j)$ for $h_j=q^j$ and
evaluate the interpolating polynomial **at $h=0$**.

**Theorem** [S4 Thm 1.17]. For $f\in C^{n+1}$, $h_i=q^i$ with $0<q<1$, and
$p_{i,m}$ interpolating in $x_0+h_{i+j}$, $j=0..m$, there is $C>0$ with
$$|f(x_0)-p_{i,m}(x_0)|\le C\,h_i^{m+1}\qquad (m\le n+1).$$
So column $m$ of the Neville tableau converges like $h^{m+1}$: each extra
column buys an order, *provided $f$ is smooth enough*. [S4 Ex. 1.18] is the
counterexample: for $u(x)=|x|^{3/2}$ the difference quotient is $D(h)=\sqrt h$,
not differentiable at $0$, and every column stalls at $O(\sqrt h)$.

`neville.extrapolate_derivative` reproduces both tables from [S4 Exercise 1.14]
and Fig. 1.2. See note [12](12-numerical-differentiation.md) for the general
Richardson version.

## 5. The error formula [S4 §1.5]: learn this one cold

Let $\omega_{n+1}(x)=\prod_{j=0}^n(x-x_j)$. For $f\in C^{n+1}([a,b])$ and every
$x\in[a,b]$ there is $\xi\in(a,b)$ with
$$\boxed{\;f(x)-p(x)=\omega_{n+1}(x)\,\frac{f^{(n+1)}(\xi)}{(n+1)!}\;}\qquad\text{[S4 Thm 1.15]}$$
Proof: fix $x$, set $g(t)=f(t)-p(t)-K\omega_{n+1}(t)$ with
$K=(f(x)-p(x))/\omega_{n+1}(x)$; $g$ has $n+2$ zeros, so by repeated Rolle
$g^{(n+1)}$ has one, and $\omega_{n+1}^{(n+1)}\equiv(n+1)!$ gives
$K=f^{(n+1)}(\xi)/(n+1)!$.

In the maximum norm,
$$\|f-p\|_{\infty,[a,b]}\le\|\omega_{n+1}\|_{\infty,[a,b]}\frac{\|f^{(n+1)}\|_{\infty,[a,b]}}{(n+1)!}\le (b-a)^{n+1}\frac{\|f^{(n+1)}\|_{\infty,[a,b]}}{(n+1)!}.$$
The first factor depends **only on the knots** (controllable), the second only
on $f$ and $n$ (not). That split is the whole argument for Chebyshev points.

Piecewise version [S4 Exercise 1.19]: interpolating degree $n$ on each of $N$
subintervals of width $h$ gives $\|f-p\|_\infty\le\frac{h^{n+1}}{(n+1)!}\|f^{(n+1)}\|_\infty$.

## 6. Chebyshev interpolation [S4 §1.6]

**Runge** [S4 Ex. 1.20]: $f(x)=(1+25x^2)^{-1}$ on $[-1,1]$ with equidistant
knots diverges as $n$ grows: $f$ has poles at $\pm i/5$, so $f^{(n+1)}$ grows
like $5^{n+1}(n+1)!$ and beats the $(n+1)!$ in the denominator, while
$|\omega_{n+1}|$ is huge near $\pm1$.

**Chebyshev points** [S4 Thm 1.21] minimise $\|\omega_{n+1}\|_{\infty,[a,b]}$:
$$x_i=\frac{a+b}{2}+\frac{b-a}{2}\,x^{\mathrm{Cheb}}_{i,n},\qquad x^{\mathrm{Cheb}}_{i,n}=\cos\!\Big(\pi\frac{2i+1}{2n+2}\Big),\quad i=0..n,$$
$$\|\omega^{\mathrm{Cheb}}_{n+1}\|_{\infty,[a,b]}=2\Big(\frac{b-a}{4}\Big)^{n+1},$$
and no other knot set does better. They cluster at the ends, exactly where
equidistant knots fail.

**Lebesgue constant** [S4 (1.21), Thm 1.24]: the other exam staple:
$$\Lambda_n:=\max_{x\in[-1,1]}\sum_{i=0}^n|\ell_i(x)|,$$
$$\|I_nf\|_\infty\le\Lambda_n\|f\|_\infty,\qquad \|f-I_nf\|_\infty\le(1+\Lambda_n)\min_{q\in\mathcal P_n}\|f-q\|_\infty,$$
$$\Lambda_n^{\mathrm{unif}}\sim\frac{2^n}{e\,n\ln n},\qquad \Lambda_n^{\mathrm{Cheb}}\le\frac{2}{\pi}\ln(n+1)+1 .$$
Derivation of the second bound: for any $q\in\mathcal P_n$, $I_nq=q$, so
$\|f-I_nf\|=\|(f-q)-I_n(f-q)\|\le(1+\Lambda_n)\|f-q\|$. $\Lambda_n$ is also the
amplification factor for perturbed data: $|\tilde f_i-f(x_i)|\le\delta$ moves the
interpolant by at most $\Lambda_n\delta$ [S4 Rem. 1.25]. For $n=20$,
$\Lambda^{\mathrm{Cheb}}_{20}\approx2.9$, so $1+\Lambda\le4$ [S4 Rem. 1.25].

**Best-approximation bounds by insertion** [S4 Ex. 1.26], $f=e^x$ on $[-1,1]$,
degree 1: the Taylor polynomial $T_1=1+x$ gives
$\min_{q}\|f-q\|_\infty\le e-2\approx0.7183$; the Chebyshev interpolant
$I^{\mathrm{Cheb}}_1f\approx1.0854x+1.2606$ gives $\approx0.3723$; the Remez
optimum $1.1752x+1.2643$ gives $\approx0.2788$. (`neville.lebesgue_constant`,
`test_neville.py` reproduces all three numbers.)

| $n+1$ knots, Runge $f$ | equispaced | Chebyshev | natural cubic spline |
|---|---|---|---|
| 5 | $0.44$ | $0.40$ | $0.28$ |
| 9 | $1.05$ | $0.17$ | $0.056$ |
| 13 | $3.7$ | $0.069$ | $0.0069$ |
| 21 | $60$ | $0.015$ | $0.0032$ |

## 7. Hermite interpolation [S4 §1.7]

Reproduce derivatives too. Given distinct $x_0..x_n$ and $d_i\in\mathbb N_0$, find
$p\in\mathcal P_{n+\sum_i d_i}$ with
$$p^{(j)}(x_i)=f_{ij},\qquad i=0..n,\ j=0..d_i \qquad\text{[S4 (1.22)]}.$$
Uniquely solvable, with an error bound analogous to Thm 1.15 when
$f_{ij}=f^{(j)}(x_i)$. Two degenerate cases [S4 Rem. 1.29]: all $d_i=0$ is
ordinary interpolation; $n=0$, $d_0=N$ is the Taylor polynomial
$p(x)=\sum_{j\le N}\frac{f^{(j)}(x_0)}{j!}(x-x_0)^j$.

Computationally it is the Newton form with **repeated knots**: list each $x_i$
$(d_i+1)$ times and define the divided difference of coincident knots by
$f[x_i,\ldots,x_i]=f^{(k)}(x_i)/k!$ (the limit of [S4] Rem. 1.12).
(`neville.hermite_divided_differences`, `neville.hermite_eval`.) [S4] states the
problem but leaves the algorithm to the reader; **F3 2.1b asked for it**, so it
is worth being able to run by hand.

## 8. Splines [S4 §1.8] (CSE)

Keep the degree low and add pieces instead. On a partition
$a=x_0<\cdots<x_n=b$, $h_i=x_{i+1}-x_i$, $h=\max h_i$,
$$S^{p,r}(\Delta):=\{u\in C^r([a,b])\ :\ u|_{I_i}\in\mathcal P_p\ \forall i\}\qquad\text{[S4 Def. 1.30]},$$
$$\dim S^{p,r}(\Delta)=n(p+1)-(n-1)(r+1)\qquad\text{[S4 Lem. 1.31]}.$$
Piecewise linear ($p=1,r=0$): $s=\sum_i f_i\varphi_i$ with hat functions,
$\|f-s\|_\infty\le Ch^2\|f''\|_\infty$.

**Classical cubic spline** $p=3$, $r=2$: $\dim=n+3$, interpolation gives $n+1$
conditions, so **two** more are needed [S4 §1.8.2]:

| | extra conditions |
|---|---|
| complete / clamped | $s'(x_0)=f_0'$, $s'(x_n)=f_n'$ |
| periodic | $f_0=f_n$, $s'(x_0)=s'(x_n)$, $s''(x_0)=s''(x_n)$ |
| natural | $s''(x_0)=s''(x_n)=0$ |
| not-a-knot | $s'''$ continuous across $x_1$ and $x_{n-1}$ |

**Accuracy** [S4 Thm 1.32]: for $f\in C^4$ and the complete, periodic or
not-a-knot spline,
$$\|f-s\|_\infty\le Ch^4\|f^{(4)}\|_\infty,\qquad \|(f-s)'\|_\infty\le Ch^3\|f^{(4)}\|_\infty,$$
and in each of these cases the problem is uniquely solvable. Not-a-knot is the
default of MATLAB's `spline` and of `scipy.interpolate.CubicSpline`
[S4 Rem. 1.33, S20]. The natural spline is only $O(h^2)$ near the boundary
unless $f''$ really vanishes there.

**Energy minimisation** [S4 Thm 1.34], the reason for the name: among all
$v\in C^2$ with $v(x_i)=f_i$ and the matching end conditions, the complete /
natural / periodic cubic spline minimises $\|v''\|_{L^2(I)}$: the linearised
elastic energy of a bent draughtsman's spline [S4 Rem. 1.35].

**Computation.** With $M_i=s''(x_i)$ (so $s''$ is piecewise linear),
$d_i=(f_{i+1}-f_i)/h_i$, continuity of $s'$ at interior knots gives the
tridiagonal, diagonally dominant system
$$h_{i-1}M_{i-1}+2(h_{i-1}+h_i)M_i+h_iM_{i+1}=6(d_i-d_{i-1}),\qquad i=1..n-1,$$
solved in $O(n)$ by the Thomas algorithm (`interp.thomas`), and on $[x_i,x_{i+1}]$
$$s(x)=\frac{M_i(x_{i+1}-x)^3+M_{i+1}(x-x_i)^3}{6h_i}+\Big(\frac{f_i}{h_i}-\frac{M_ih_i}{6}\Big)(x_{i+1}-x)+\Big(\frac{f_{i+1}}{h_i}-\frac{M_{i+1}h_i}{6}\Big)(x-x_i).$$
*([S4] §1.8.2 only says "a linear system that can be solved"; the $M_i$ form is
the standard one [S16].)*

**Locality** [S4 Rem. 1.37]: for small $r$ a change in one $f_i$ moves the spline
only near $x_i$, unlike polynomial interpolation which it moves everywhere.

## Pitfalls

- Solving the Vandermonde system, or evaluating $\sum c_kx^k$ for large $n$ on a
  wide interval. Use Neville, Newton/Horner or barycentric, and shift-and-scale
  to $[-1,1]$.
- Quoting the Neville cost as $O(n)$. It is $O(n^2)$ [S4 Rem. 1.6]: the single
  most repeated true/false item in the past papers.
- "More knots means less error." False [S4 Ex. 1.20, F1 5b, S1a 1.5a]: the
  $f^{(n+1)}$ factor can grow faster than $(n+1)!$.
- Confusing the two Lebesgue growths. Chebyshev is $O(\ln n)$, **uniform is
  exponential** $2^n/(en\ln n)$: S1a 1.5a marks "uniform grows like $O(\log n)$"
  as false.
- Natural spline boundary conditions on data with $f''\ne0$ at the ends:
  $O(h^2)$, not $O(h^4)$.
- Interpolation outside $[x_0,x_n]$ *is* extrapolation: $\omega_{n+1}$ explodes.
  The one legitimate use is Neville extrapolation to $h=0$ (§4), where the
  target sits at the edge of a shrinking geometric knot sequence.
- Extrapolating a non-smooth $D(h)$ and expecting the columns to improve
  [S4 Ex. 1.18].

## Exam-style questions

Modelled on F1 1, F3 2.1, S1a 1.1–1.2 and the true/false blocks; see
[00](00-exam-focus.md).

1. *(F1 1, 2022W)* $g(x)=\frac4{x+1}$ on $[0,2]$, knots $x_0=0,x_1=1,x_2=2$.
   (a) Give the $\ell_i$ and the quadratic interpolant $p$. (b) For
   $g\in C^3([0,2])$ write the error formula for $g-p$. (c) Show
   $|g(\tfrac12)-p(\tfrac12)|\le\tfrac32$.
   (a) $\ell_0=\tfrac12(x-1)(x-2)$, $\ell_1=-x(x-2)$, $\ell_2=\tfrac12x(x-1)$;
   $g(0)=4,g(1)=2,g(2)=\tfrac43$, so $p=2(x-1)(x-2)-2x(x-2)+\tfrac23x(x-1)$.
   (b) $g-p=\omega_3(x)\,g'''(\xi)/3!$ with $\omega_3=(x-0)(x-1)(x-2)$.
   (c) $g'''(\xi)=-4\cdot3!\,(\xi+1)^{-4}$ and $\|(\xi+1)^{-4}\|_\infty\le1$ on
   $[0,2]$, $|\omega_3(\tfrac12)|=\tfrac12\cdot\tfrac12\cdot\tfrac32=\tfrac38$;
   so the error is $\le\tfrac38\cdot\tfrac1{3!}\cdot4\cdot3!=\tfrac38\cdot4=\tfrac32$.
2. *(S1a 1.1, 2024W)* Knots $-1,0,1$, values $2,0,0$. Give the $\ell_i$ and $p$;
   then set up $A\mathbf x=b$ for $p=\alpha+\beta x+\gamma x^2$ without solving.
   $\ell_0=\tfrac{x^2-x}{2}$, $\ell_1=1-x^2$, $\ell_2=\tfrac{x^2+x}{2}$,
   $p=2\ell_0=x^2-x$. $A=\begin{psmallmatrix}1&-1&1\\1&0&0\\1&1&1\end{psmallmatrix}$,
   $b=(2,0,0)^\top$ (rows $1,x_i,x_i^2$).
3. *(S1a 1.2, 2024W)* Define $\Lambda_n$ in terms of the knots and bound
   $\|f-I_nf\|_{\infty,[-1,1]}$ with it. State the growth for Chebyshev knots.
   $\Lambda_n=\max_{x}\sum_i|\ell_i(x)|$;
   $\|f-I_nf\|\le(1+\Lambda_n)\min_{q\in\mathcal P_n}\|f-q\|$;
   $\Lambda^{\mathrm{Cheb}}_n\le\tfrac2\pi\ln(n+1)+1$, logarithmic.
4. *(F1 5a/5b, 2022W: true or false)*
   (i) Evaluating $p_n(x)$ with Neville costs $O(n)$. **False**, $O(n^2)$.
   (ii) Column $m$ of the Neville tableau holds polynomials of degree $m$. **True**.
   (iii) More knots always give a smaller error. **False**.
   (iv) The Lebesgue constant for uniform knots behaves like $O(n)$. **False**:
   exponential, $\sim 2^n/(en\ln n)$.
5. *(F3 2.1, 2022W re-test)* For $n+1$ knots and values, what is the highest
   degree for which a unique interpolating polynomial is guaranteed? What about
   lower and higher degrees?
   Degree $\le n$: unique [S4 Thm 1.2]. Degree $<n$: generally no solution
   (over-determined). Degree $>n$: infinitely many (add any multiple of
   $\omega_{n+1}$).
6. *(F3 2.1b, 2022W re-test)* Interpolate through $(\tfrac12,1)$, $(1,\tfrac32)$,
   $(2,5)$ **and** $f'(0)$.
   Hermite: four conditions, so $p\in\mathcal P_3$; run Newton's scheme on the
   knot list $0,0,\tfrac12,1,2$ trimmed to the given data, using
   $f[x_i,x_i]=f'(x_i)$ for the repeated knot [S4 §1.7].
7. *(ours: CSE, splines)* How many degrees of freedom does $S^{3,2}(\Delta)$ have
   on $n+1$ knots, how many does interpolation fix, and name the four standard
   ways to fix the rest.
   $\dim=4n-3(n-1)=n+3$; interpolation gives $n+1$; complete, periodic, natural,
   not-a-knot [S4 §1.8.2]. For $f\in C^4$, complete/periodic/not-a-knot give
   $O(h^4)$ [S4 Thm 1.32].

## Implementation

`src/py/interp.py`: `lagrange_eval`, `barycentric_eval`, `divided_differences` /
`newton_eval`, `chebyshev_nodes`, `runge`, `thomas`, `cubic_spline` (natural,
clamped, not-a-knot) / `spline_eval`, `vandermonde`, `lstsq_normal`, `lstsq_qr`,
`polyfit` / `polyval`, `orthogonal_polys` / `orthogonal_lstsq`.

`src/py/neville.py` (new): `aitken_neville`, `neville_tableau`,
`extrapolate_derivative`, `lebesgue_constant`, `omega_max`,
`hermite_divided_differences`, `hermite_eval`.

Tests: `test_interp.py` (vs `scipy.interpolate.BarycentricInterpolator`,
`CubicSpline`, `np.polyfit`, `np.linalg.lstsq`; spline order 4; Runge
magnitudes) and `test_neville.py` (the $O(n^2)$ operation count, the
$\|\omega^{\mathrm{Cheb}}\|=2((b-a)/4)^{n+1}$ identity of [S4 Thm 1.21], the
Chebyshev Lebesgue bound of [S4 Thm 1.24], the three numbers of [S4 Ex. 1.26],
the stalled columns of [S4 Ex. 1.18], and the F1/S1a exam items above).
