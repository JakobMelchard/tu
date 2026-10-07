# 03 Numerical integration

[S4] §2. Compute $\int_a^b f$ approximately as $Q(f)=\sum_i w_if(x_i)$
[S4 (2.1)]. Every rule here is "interpolate the integrand, integrate the
interpolant", so note [01](01-polynomial-interpolation.md) supplies all the
error analysis. Together with interpolation this is the whole first test.
Implementation: `src/py/quad.py`, `src/py/quad2d.py`.

## 1. Composite rules and the reference interval

The standard construction [S4 §2, Rem. 2.3]:

1. define a rule $\widehat Q(f)\approx\int_0^1f$ on a **reference interval**
   (usually $[0,1]$ or $[-1,1]$);
2. partition $[a,b]$ into subintervals $(t_i,t_{i+1})$ of length $h_i$;
3. use $\int_{t_i}^{t_{i+1}}f=h_i\int_0^1f(t_i+h_i\xi)\,d\xi\approx h_i\widehat Q\big(f(t_i+h_i\cdot)\big)$.

Composite **midpoint** [S4 Ex. 2.1] and **trapezoidal** [S4 Ex. 2.2]:
$$M_h=\sum_{i=0}^{N-1}h\,f(m_i),\qquad T_h=h\Big[\tfrac12f(a)+\sum_{i=1}^{N-1}f(t_i)+\tfrac12f(b)\Big].$$

## 2. Newton–Cotes [S4 §2.1]

Interpolate at **uniform** nodes and integrate: $w_i=\int_0^1\ell_i$.
Closed formulas use $x_i=i/n$ [S4 Ex. 2.4]; open formulas use
$x_i=\tfrac{2i+1}{2n+2}$ [S4 Ex. 2.5], of which $n=0$ is the **midpoint rule**
$\int_0^1f\approx f(1/2)$.

Weights and errors on $[0,1]$, $h=1/n$ [S4 Fig. 2.2]:

| $n$ | weights | $Q(f)-\int_0^1f$ | name |
|---|---|---|---|
| 1 | $\tfrac12,\tfrac12$ | $\tfrac1{12}h^3f''(\xi)$ | trapezoidal |
| 2 | $\tfrac16,\tfrac46,\tfrac16$ | $\tfrac1{90}h^5f^{(4)}(\xi)$ | Simpson |
| 3 | $\tfrac18,\tfrac38,\tfrac38,\tfrac18$ | $\tfrac3{80}h^5f^{(4)}(\xi)$ | 3/8 |
| 4 | $\tfrac7{90},\tfrac{32}{90},\tfrac{12}{90},\tfrac{32}{90},\tfrac7{90}$ | $\tfrac8{945}h^7f^{(6)}(\xi)$ | Milne |
| 5 | $\tfrac{19}{288},\tfrac{75}{288},\tfrac{50}{288},\tfrac{50}{288},\tfrac{75}{288},\tfrac{19}{288}$ | $\tfrac{275}{12096}h^7f^{(6)}(\xi)$ | - |
| 6 | $\tfrac{41}{840},\tfrac{216}{840},\tfrac{27}{840},\tfrac{272}{840},\tfrac{27}{840},\tfrac{216}{840},\tfrac{41}{840}$ | $\tfrac9{1400}h^9f^{(8)}(\xi)$ | Weddle |

Three properties, all set as exercises in [S4 Ex. 2.7] and all asked in past
papers:

- $\sum_i w_i=1$ (apply the rule to $f\equiv1$), hence *any* rule with
  $\sum w_i=1$ is exact on constants (S1a 1.5c).
- $w_{n-i}=w_i$ (symmetry of the nodes about $\tfrac12$).
- Exactness is $n$ by construction, and **$n+1$ when $n$ is even**: for
  $f=(x-\tfrac12)^{n+1}$, odd about $\tfrac12$, both integral and rule vanish.
  So midpoint is exact on $\mathcal P_1$ [S4 Ex. 2.6] and **Simpson on
  $\mathcal P_3$**.

**High $n$ is useless.** From $n=8$ the weights change sign, $\sum|w_i|\to\infty$,
and Newton–Cotes does **not** converge as $n\to\infty$ (F3 2.5c). Go composite,
or go Gauss. *(The negative-weight statement is standard [S16]; [S4] only uses
the formulas composite.)*

## 3. Error of the composite rules [S4 Thm 2.8]

The derivation is worth knowing because the same trick reappears for Gauss.
Since $T$ is exact on $\mathcal P_1$, insert any $p\in\mathcal P_1$:
$$\Big|\int_{x_i}^{x_{i+1}}f-T_{\{x_i,x_{i+1}\}}(f)\Big|=\Big|\int f-p-T(f-p)\Big|\le 2h_i\|f-p\|_{\infty,[x_i,x_{i+1}]},$$
so the quadrature error is bounded by a **best-approximation** error. Summing,

$$\Big|\int_a^bf-T_{\{x_0..x_N\}}(f)\Big|\le2\sum_i h_i\min_{p\in\mathcal P_1}\|f-p\|_{\infty,[x_i,x_{i+1}]},$$
$$\Big|\int_a^bf-S_{\{x_0..x_N\}}(f)\Big|\le2\sum_i h_i\min_{p\in\mathcal P_3}\|f-p\|_{\infty,[x_i,x_{i+1}]}.$$

Bounding the best approximation by the *Chebyshev* linear interpolant, for which
$\|\omega_2^{\mathrm{Cheb}}\|_\infty=(x_{i+1}-x_i)^2/8$ [S4 Thm 1.21], gives
$\min_{p\in\mathcal P_1}\|f-p\|\le\tfrac1{16}h_i^2\|f''\|$ and hence

$$\boxed{\Big|\int_a^bf-T_h(f)\Big|\le\frac18\sum_ih_i^3\|f''\|_{\infty,[x_i,x_{i+1}]}\le\frac18(b-a)h^2\|f''\|_{\infty,[a,b]}}\quad\text{[S4 Thm 2.8(ii)]}$$
$$\Big|\int_a^bf-S_h(f)\Big|\le C\sum_ih_i^5\|f^{(4)}\|\le C(b-a)h^4\|f^{(4)}\|_{\infty,[a,b]}\quad\text{[S4 Thm 2.8(iii)]}$$

**Two constants, both correct.** The classical sharp constants are
$\tfrac{(b-a)h^2}{12}\|f''\|$ and $\tfrac{(b-a)h^4}{180}\|f^{(4)}\|$, obtained by
summing the per-panel errors of Fig. 2.2; [S4]'s $\tfrac18$ comes from the
best-approximation route above and is a valid but looser bound. **Use
$\tfrac18$** in this course's "choose $h$" questions (F3 2.2c), and know that the
$\tfrac1{12}$ version exists. Composite midpoint has error
$+\tfrac{(b-a)h^2}{24}\|f''\|$: half of trapezoid's, opposite sign.

**Order.** A rule is of order $m$ if the composite error is $O(h^m)$. A rule
exact on $\mathcal P_n$ gives a composite rule of order $n+1$ [S4 after Thm 2.8].
Composite trapezoidal: **2**. Composite Simpson: **4**. (S1a 1.5c marks "the
composite Simpson rule converges with order 3" as false.)

Smoothness is required: $\int_0^1x^{0.1}dx$ converges only like $O(h^{1.1})$,
not $O(h^2)$, because $f'=0.1x^{-0.9}$ is not continuous at $0$ [S4 Ex. 2.10].

## 4. Romberg extrapolation [S4 §2.2]

For $f$ smooth, the composite trapezoidal rule has the **Euler–Maclaurin**
expansion in *even* powers,
$$T(h)=\int_a^bf+c_1h^2+c_2h^4+c_3h^6+\cdots\qquad\text{[S4 (2.2)]},$$
i.e. $T(h)=\widetilde T(h^2)$. So interpolate the data $(h_i^2,T(h_i))$ with
$h_i=(b-a)M^{-i}$ and evaluate at $h^2=0$: Neville again
(note [01](01-polynomial-interpolation.md) §4). Interpolating in $h^2$ rather
than $h$ is much more accurate for the same cost.

Tableau ($M=2$, so the extrapolation factor is $4^j$):
$$T_{i,0}=T(h/2^i),\qquad T_{i,j}=T_{i,j-1}+\frac{T_{i,j-1}-T_{i-1,j-1}}{4^{\,j}-1}.$$
**Column $1$ is the composite Simpson rule, column $2$ the composite Milne rule**
[S4 Rem. 2.11]; $M=3$ gives the composite 3/8 rule in the first column.
Halving reuses every old point: $T_{h/2}=\tfrac12T_h+\tfrac h2\sum f(\text{new midpoints})$.

Diagonal errors for $\int_0^1e^x$: $1.4\cdot10^{-1}$, $5.8\cdot10^{-4}$,
$8.6\cdot10^{-7}$, $3.4\cdot10^{-10}$, $3.3\cdot10^{-14}$: with 17 function
values (`quad.romberg`). Fails, with no gain per column, when $f$ is not smooth
enough for the expansion to exist.

## 5. Non-smooth integrands, graded meshes, adaptivity [S4 §2.3]

For $\int_0^1x^{0.1}$ a uniform mesh gives $O(N^{-1.1})$; the **graded** mesh
$x_i=(i/N)^\beta$ with $\beta=2$ restores $O(N^{-2})$ [S4 Ex. 2.12]. Rule of
thumb: small $h_i$ where $f$ or its derivatives are large.

Constructing a good mesh by hand is hard, so refine adaptively. [S4 Alg. 5]
estimates the accuracy of the trapezoidal rule with the better Simpson rule and
bisects if the estimate misses:

```
adapt(f, a, b, tau):
    if (b - a) <= h_min: return S([a,b])          # forced termination
    if |S([a,b]) - T([a,b])| <= rho*tau:          # rho in (0,1), safety factor
        return S([a,b])
    m := (a+b)/2
    return adapt(f, a, m, tau/2) + adapt(f, m, b, tau/2)
```

The usual practical variant compares $S(a,b)$ with $S(a,m)+S(m,b)$, so that
$\int-S_{h/2}\approx(S_{h/2}-S_h)/15$ and the accepted value can be extrapolated
(`quad.adaptive_simpson`). For $\int_{-1}^2\sqrt{|x|}\,dx=2.5522847\ldots$ it
reaches $5\cdot10^{-13}$ with 1489 evaluations; composite Simpson with as many
points is off by $1.5\cdot10^{-5}$.

## 6. Gaussian quadrature [S4 §2.4]

*Question:* choose $n+1$ nodes **and** weights so that polynomials of the highest
possible degree are exact. *Answer:* degree $2n+1$; the nodes are the zeros of
the Legendre polynomial $L_{n+1}$.

**Legendre polynomials** [S4 §2.4.1, Thm 2.13]. With
$\langle u,v\rangle=\int_{-1}^1uv$, there is a unique sequence $L_n\in\mathcal P_n$
with (i) $\{L_0..L_n\}$ a basis of $\mathcal P_n$, (ii) $L_n\perp\mathcal P_{n-1}$,
(iii) $L_n(1)=1$. Rodrigues: $L_n(x)=\tfrac1{2^nn!}\tfrac{d^n}{dx^n}(x^2-1)^n$.
**Three-term recurrence**: the standard way to evaluate them [S4 Rem. 2.14]:
$$(n+1)L_{n+1}(x)=(2n+1)xL_n(x)-nL_{n-1}(x).$$
The recurrence is not special to Legendre: it follows from
$\langle xL_n,L_i\rangle=\langle L_n,xL_i\rangle=0$ for $i+1\le n-1$, so only the
last two terms of the Gram–Schmidt sum survive [S4 (2.6)–(2.7)]. Every family of
orthogonal polynomials has one.

$L_{n+1}$ has exactly $n+1$ distinct zeros, all in $(-1,1)$ [S4 Thm 2.15].

**The rule** [S4 (2.10)]: $x^G_{i,n}=$ zeros of $L_{n+1}$,
$w^G_{i,n}=\int_{-1}^1\ell_i$.

**Theorem** [S4 Thm 2.16]. $Q_n^{\mathrm{Gauss}}$ is exact on $\mathcal P_{2n+1}$;
all weights are positive; and **no** rule with $n+1$ points is exact on
$\mathcal P_{2n+2}$.

Three arguments worth reproducing (all three have been examined):

- *Exactness $2n+1$*: divide $f\in\mathcal P_{2n+1}$ as $f=L_{n+1}q_n+r_n$. Then
  $\int L_{n+1}q_n=0$ by orthogonality and $Q(L_{n+1}q_n)=0$ because
  $L_{n+1}(x_i^G)=0$; the remainder $r_n\in\mathcal P_n$ is integrated exactly by
  construction.
- *Positive weights*: apply the rule to $\ell_i^2\in\mathcal P_{2n}$:
  $w_i=Q(\ell_i^2)=\int\ell_i^2>0$. This is what makes Gauss immune to
  cancellation.
- *Optimality*: for $f=\prod_{i}(x-x_i)^2\in\mathcal P_{2n+2}$ any rule on those
  nodes gives $Q(f)=0$ while $\int f>0$ (F1 4, [S4 §2.4.2]).

**Convergence** [S4 Thm 2.17]: since $\sum_iw_i=Q(1)=2$ and the weights are
positive,
$$\Big|\int_{-1}^1f-Q_n^{\mathrm{Gauss}}(f)\Big|\le4\min_{v\in\mathcal P_{2n+1}}\|f-v\|_{\infty,[-1,1]},$$
so $Q_n^{\mathrm{Gauss}}(f)\to\int f$ for **every** $f\in C([-1,1])$, unlike
Newton–Cotes. Fast for smooth $f$, unremarkable for $x^{0.1}$ [S4 Ex. 2.18].

There is **no explicit formula for the Gauss points and weights for $n\ge5$**
[S4 Rem. 2.19]; use `numpy.polynomial.legendre.leggauss` [S20] or compute them
by Newton on $L_{n+1}$ from the start values $\cos\big(\pi\tfrac{i-1/4}{n+1/2}\big)$
with $L_n'=n(xL_n-L_{n-1})/(x^2-1)$ (`quad.gauss_legendre`, matching `leggauss`
to $10^{-14}$).

Small cases: $n+1=2$: $\xi=\pm1/\sqrt3$, $w=1,1$. $n+1=3$: $\xi=0,\pm\sqrt{3/5}$,
$w=\tfrac89,\tfrac59,\tfrac59$: exact on $x^4$
($2\cdot\tfrac59\cdot\tfrac9{25}=0.4$) but not on $x^6$
($2\cdot\tfrac59\cdot\tfrac{27}{125}=0.24\ne\tfrac27$), i.e. degree 5 exactly.
Mapping to $[a,b]$: $x=\tfrac{b-a}2\xi+\tfrac{a+b}2$, weights scaled by
$\tfrac{b-a}2$.

**Weighted Gauss** [S4 §2.7, Thm 2.26] (CSE). For a weight $\omega>0$ on
$(-1,1)$ with $\int\omega<\infty$ there are $n+1$ nodes and positive weights with
$\int\omega f=\sum w_if(x_i)$ for all $f\in\mathcal P_{2n+1}$; the nodes are the
zeros of the orthogonal polynomials for $\langle u,v\rangle_\omega=\int\omega uv$.
Named cases [S4 §2.7.1]: $\omega=(1-x^2)^{-1/2}$ gives **Chebyshev**,
$\omega=(1-x)^\alpha(1+x)^\beta$ gives **Jacobi** $P_n^{(\alpha,\beta)}$, with
$\alpha=\beta=0$ Legendre and $\alpha=\beta=-\tfrac12$ Chebyshev. [S4 Lem. 2.24,
2.25] give the Golub–Welsch route: the nodes are the eigenvalues of the
tridiagonal Jacobi matrix built from the three-term recurrence.

## 7. Periodic integrands [S4 §2.5]

The one case where the composite trapezoidal rule beats everything: a smooth
periodic $f$ integrated over a whole period. All Euler–Maclaurin boundary terms
cancel, and the rule is exact on trigonometric polynomials of degree below $N$
(note [02](02-trigonometric-interpolation-and-fft.md)). [S4 Ex. 2.20] on
$[-1,1]$: $f_1=\sin(\pi x)$ is exact at large $h$; $f_2=\cos^{10}(\pi x)$ is
exact once $N$ passes its degree; $f_3=e^{\sin 8\pi x}$ converges to $10^{-15}$
within about 40 points. **Do not use Simpson for periodic integrands.**

## 8. Quadrature in 2-D [S4 §2.6]

Reference domains: the square $S=(0,1)^2$ and the triangle
$T=\{(x,y):0<x<1,\ 0<y<1-x\}$.

**Square** [S4 §2.6.1]: tensor product of a 1-D rule,
$$Q^{2D}_n(F)=\sum_{i,j=0}^n w_iw_j\,F(x_i,x_j)\qquad\text{[S4 (2.16)]},$$
exact on $\mathrm{span}\{x^iy^j: i,j\le p\}$ if the 1-D rule is exact on
$\mathcal P_p$ [S4 Exercise 2.21]: note that is the *tensor* space, not
$\mathcal P_p$ in two variables.

**Triangle** [S4 §2.6.2]: either place points in $T$ and solve for the weights
from exactness conditions, or map the square onto the triangle. The **barycentre
rule** [S4 Exercise 2.22] uses the single point $(\tfrac13,\tfrac13)$ with weight
$|T|=\tfrac12$; it is exact on degree 0 by construction and in fact on degree 1.
A 3-point rule at the vertices with weights $\tfrac16$ each is also exact on
$\mathcal P_1$.

**Duffy transformation** [S4 Ex. 2.23] maps $S\to T$:
$$\int_TF=\int_0^1\!\!\int_0^1F\big(x,(1-x)\eta\big)(1-x)\,d\eta\,dx\approx\sum_iw_i(1-x_i)F\big(x_i,(1-x_i)y_i\big).$$
The $(1-x)$ Jacobian degrades the accuracy slightly (it makes a polynomial
integrand non-polynomial in the new variables), which is why dedicated triangle
rules exist.

## Pitfalls

- Quoting the composite trapezoidal constant as $\tfrac1{12}$ when the course's
  own theorem says $\tfrac18$, or vice versa without saying which. Both are
  upper bounds; state your source.
- High-order Newton–Cotes. Negative weights, no convergence as $n\to\infty$.
- Composite Simpson with an odd number of panels.
- Romberg or Gauss on a non-smooth integrand: the order collapses to that of the
  singularity. Split at the kink, grade the mesh [S4 Ex. 2.12], or subtract the
  singularity.
- Simpson on a periodic integrand: the trapezoidal rule is exponentially better.
- Confusing *degree of exactness* (largest $d$ with $Q=I$ on $\mathcal P_d$) with
  *order* (the composite convergence rate $h^m$). For a rule exact on
  $\mathcal P_n$, $m=n+1$. Simpson: degree 3, order 4.
- Assuming a tensor-product rule exact on $\mathcal P_p\otimes\mathcal P_p$ is
  exact on all bivariate polynomials of total degree $2p$. It is not.
- Error *estimates* from halving are asymptotic; for coarse $h$ or an
  oscillatory $f$ they lie.

## Exam-style questions

Modelled on F1 2–4, F3 2.2/2.5 and S1a 1.3/1.5; see [00](00-exam-focus.md).

1. *(F1 2, 2022W)* $Q(f)=\tfrac12f(\tfrac13)+\tfrac12f(\tfrac23)$ on $[0,1]$.
   (a) For $f=3x^2+1$ give $\int_0^1f$ and $\int_0^1f-Q(f)$. (b) What is the
   degree of exactness? (c) Can it be raised by different weights? By different
   nodes?
   (a) $\int=2$; $Q=\tfrac12(3\cdot\tfrac19+1)+\tfrac12(3\cdot\tfrac49+1)=1+\tfrac56=\tfrac{11}6$;
   error $\tfrac16$. (b) Exact on $1$ ($Q=1=\int$) and on $x$
   ($Q=\tfrac12\cdot\tfrac13+\tfrac12\cdot\tfrac23=\tfrac12=\int$), not on $x^2$
   by (a): degree **1**. (c) Not by changing the weights:
   $w_i=\int_0^1\ell_i$ is determined by the nodes. Yes by changing the nodes:
   two Gauss points give degree $2\cdot1+1=3$.
2. *(S1a 1.3, 2024W)* $Q(f)=\tfrac12f(\tfrac14)+\tfrac12f(\tfrac34)$ on $[0,1]$,
   $f=x^2+1$. Error? Degree of exactness? Degree for Gauss with 2 points and
   with $n+1$ points?
   $\int=\tfrac43=\tfrac{64}{48}$,
   $Q=\tfrac12\cdot\tfrac{17}{16}+\tfrac12\cdot\tfrac{25}{16}=\tfrac{21}{16}=\tfrac{63}{48}$,
   error $\tfrac1{48}$. Exact on $\mathcal P_1$, not $\mathcal P_2$: degree 1.
   Gauss: $2n+1$, so $3$ for two points.
3. *(F1 4, 2022W)* How are the Gauss knots and weights defined? What exactness
   do $n+1$ knots give? Can *any* rule with $n+1$ knots integrate
   $f(x)=\prod_{i=0}^n(x-x_i)^2$ exactly?
   Knots: zeros of $L_{n+1}$; weights $w_i=\int_{-1}^1\ell_i$; exactness $2n+1$.
   No: $Q_n(f)=\sum_iw_if(x_i)=0$ because every node is a double root, while
   $\int f>0$.
4. *(F3 2.2, 2022W re-test)* $\int_0^{3\pi/2}x\sin x\,dx$ with the composite
   trapezoidal rule. (a) Split into 3 equal subintervals; what is $h$? (b) Write
   the error formula. (c) Find a mesh width $h$ with error $\le0.01$. Hint:
   $(x\sin x)''=2\cos x-x\sin x$.
   (a) $h=\tfrac{3\pi}{2}/3=\tfrac\pi2$. (b)
   $|\int f-T_h|\le\tfrac18(b-a)h^2\|f''\|_\infty$ [S4 Thm 2.8].
   (c) On $[0,\tfrac{3\pi}2]$, $\|2\cos x-x\sin x\|_\infty\le2+\tfrac{3\pi}2\approx6.71$;
   need $\tfrac18\cdot\tfrac{3\pi}2\cdot h^2\cdot6.71\le0.01$, i.e.
   $h^2\le0.002529$, $h\le0.05029$, so $N\ge\lceil 3\pi/(2\cdot0.05029)\rceil=94$
   subintervals.
5. *(F1 3 / F4, 2022W–2023W)* Error-vs-$N$ curves are drawn for $f=e^x$ and
   $g=x^{0.1}$ on $[0,1]$ and for composite trapezoidal, composite Simpson and
   Gauss. Which curve is which?
   Smooth $f$: trapezoidal $N^{-2}$, Simpson $N^{-4}$, Gauss falls off a cliff to
   machine precision. Non-smooth $g$: all three flatten to about $N^{-1.1}$
   (trapezoidal) / slightly better, and Gauss loses its advantage entirely
   [S4 Ex. 2.10, 2.18].
6. *(S1a 1.5 / F3 2.5: true or false)*
   (i) A rule with $\sum w_i=1$ on $[0,1]$ is always exact for constants. **True**.
   (ii) The composite Simpson rule converges with order 3. **False**, 4.
   (iii) Gauss weights are always positive. **True** [S4 Thm 2.16].
   (iv) Newton–Cotes converges as $n\to\infty$. **False**.
   (v) Midpoint is more efficient than Gauss. **False**.
   (vi) Fill in: the composite trapezoidal rule has order **2**; Simpson has
   degree of exactness **3**.
7. *(ours: CSE, 2-D)* Give the one-point rule on the reference triangle exact
   for degree 0 and show it is exact for degree 1.
   Weight $=|T|=\tfrac12$ at the barycentre $(\tfrac13,\tfrac13)$. For
   $F=a+bx+cy$, $\int_TF=\tfrac12a+\tfrac b6+\tfrac c6$ and
   $\tfrac12F(\tfrac13,\tfrac13)=\tfrac12(a+\tfrac b3+\tfrac c3)$: equal
   [S4 Exercise 2.22].

## Implementation

`src/py/quad.py`: `newton_cotes_weights` / `newton_cotes`, `midpoint`,
`trapezoid`, `simpson`, `legendre` (three-term recurrence, $L_n$ and $L_n'$),
`gauss_legendre`, `gauss_quad`, `romberg`, `adaptive_simpson` (value and
evaluation count), **`adaptive_trapezoid`** ([S4 Alg. 5] verbatim),
**`graded_mesh`** ([S4 Ex. 2.12]), **`gauss_jacobi`** ([S4 §2.7] via the
Golub–Welsch matrix of [S4 Lem. 2.24–2.25]).

`src/py/quad2d.py` (new): `tensor_square`, `barycentre_triangle`,
`vertex_triangle`, `duffy_triangle`, `exactness_degree_2d`.

Tests: `test_quad.py` (orders, `scipy.integrate.trapezoid/simpson/quad`,
`leggauss`, exactness degree with the analytic error for $x^{2n}$, the
Fig. 2.2 weight table, the $O(N^{-1.1})$ vs $O(N^{-2})$ graded-mesh result of
[S4 Ex. 2.12], the periodic integrands of [S4 Ex. 2.20], and the F1/S1a exam
items above) and `test_quad2d.py` (tensor exactness, both triangle rules exact
on $\mathcal P_1$, Duffy against an analytic integral).
