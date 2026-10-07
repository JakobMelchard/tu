# 12 Numerical differentiation *(appendix: not a chapter of the script)*

The TISS subject line names "numerical differentiation and integration" [S1],
but **[S4] has no differentiation chapter**. Difference quotients appear only as
the worked application of the Neville scheme (§1.4), with the smoothness
counterexample in [S4 Ex. 1.18] and the convergence rate in [S4 Thm 1.17]. So
treat this note as an appendix: §1 and §3 are the course's actual content
(extrapolation, note [01](01-polynomial-interpolation.md) §4), and §2 is the
round-off/truncation trade-off: standard [S12, S13], not in [S4], but needed by
the finite-difference Jacobian of note
[08](08-nonlinear-equations-and-newton.md) and by
[S4 §6.4]. Implementation: `src/py/diff.py`, `src/py/neville.py`.

## 1. The course's version: extrapolation to $h=0$

[S4 §1.4]. The derivative at $0$ is $\lim_{h\to0}D(h)$ with
$D(h)=\big(f(h)-f(0)\big)/h$; $D(0)$ is not computable, so **interpolate
$D$ at $h_j=q^j$ and evaluate the interpolant at $h=0$** with the Neville
scheme (note [01](01-polynomial-interpolation.md) §2).

**Theorem** [S4 Thm 1.17]. For $f\in C^{n+1}$, $h_i=q^i$ with $0<q<1$, and
$p_{i,m}$ the polynomial interpolating in $x_0+h_{i+j}$, $j=0..m$, there is
$C=C(f,m,q)$ with
$$|f(x_0)-p_{i,m}(x_0)|\le C\,h_i^{m+1}\qquad (m\le n+1).$$
If $f$ is smooth then $h\mapsto D(h)$ is smooth (Taylor), so Thm 1.17 applies to
it: **column $m$ of the Neville tableau converges like $h^{m+1}$**, one extra
order per column.

**And the counterexample** [S4 Ex. 1.18]: for $u(x)=|x|^{3/2}$ the difference
quotient is $D(h)=\sqrt h$, not differentiable at $0$, and every column of the
tableau stalls at $O(\sqrt h)$: increasing $m$ buys nothing.

| $h$ | $m=0$ | $m=1$ | $m=2$ | $m=3$ | $m=4$ |
|---|---|---|---|---|---|
| $2^0$ | $1.000$ | $4.14\cdot10^{-1}$ | $2.52\cdot10^{-1}$ | $1.68\cdot10^{-1}$ | $1.15\cdot10^{-1}$ |
| $2^{-2}$ | $5.00\cdot10^{-1}$ | $2.07\cdot10^{-1}$ | $1.26\cdot10^{-1}$ | $8.40\cdot10^{-2}$ | $5.77\cdot10^{-2}$ |
| $2^{-4}$ | $2.50\cdot10^{-1}$ | $1.04\cdot10^{-1}$ | $6.31\cdot10^{-2}$ | $4.20\cdot10^{-2}$ | $2.89\cdot10^{-2}$ |
| $2^{-6}$ | $1.25\cdot10^{-1}$ | $5.18\cdot10^{-2}$ | $3.16\cdot10^{-2}$ | | |
| rate | $\sqrt h$ | $\sqrt h$ | $\sqrt h$ | $\sqrt h$ | $\sqrt h$ |

(from [S4 Fig. 1.2]; `neville.extrapolate_derivative` reproduces both tables.)

## 2. Finite-difference formulas and the $h$ trade-off *(background)*

From $f(x\pm h)=f\pm hf'+\tfrac{h^2}2f''\pm\tfrac{h^3}6f'''+\cdots$:

| formula | expression | error term | order |
|---|---|---|---|
| forward | $\dfrac{f(x+h)-f(x)}{h}$ | $\tfrac h2f''(\xi)$ | 1 |
| backward | $\dfrac{f(x)-f(x-h)}{h}$ | $-\tfrac h2f''(\xi)$ | 1 |
| central | $\dfrac{f(x+h)-f(x-h)}{2h}$ | $\tfrac{h^2}6f'''(\xi)$ | 2 |
| second derivative | $\dfrac{f(x+h)-2f(x)+f(x-h)}{h^2}$ | $\tfrac{h^2}{12}f^{(4)}(\xi)$ | 2 |
| 5-point central | $\dfrac{-f(x+2h)+8f(x+h)-8f(x-h)+f(x-2h)}{12h}$ | $-\tfrac{h^4}{30}f^{(5)}$ | 4 |
| one-sided, 2nd order | $\dfrac{-3f(x)+4f(x+h)-f(x+2h)}{2h}$ | $-\tfrac{h^2}3f'''$ | 2 |

Symmetric stencils gain an order for free because the odd Taylor terms cancel.
Signs are for the convention **error = approximation $-$ exact**, and every row
is derived symbolically in `test_diff.py::test_leading_error_terms_and_signs`.

**General stencil.** For $\sum_jw_jf(x+s_jh)=h^mf^{(m)}(x)+O(h^n)$ on offsets
$s_0..s_{n-1}$, match Taylor coefficients:
$$\sum_jw_j\frac{s_j^k}{k!}=\delta_{km},\qquad k=0..n-1,$$
a Vandermonde-type system (`diff.fd_weights`, solved with our own LU). Offsets
$(-2,-1,0,1,2)$, $m=1$ give $\tfrac1{12}(1,-8,0,8,-1)$. Equivalently:
differentiate the interpolating polynomial through the stencil points (note
[01](01-polynomial-interpolation.md)): the two views are identical, which is
exactly the connection [S4] uses in §1.4.

**Round-off.** The computed values carry $|\delta f|\le u|f|$, and dividing by
$h$ amplifies them:
$$\Big|\frac{\mathrm{fl}(f(x+h))-\mathrm{fl}(f(x))}{h}-f'(x)\Big|\le\underbrace{\frac h2|f''|}_{\text{truncation}}+\underbrace{\frac{2u|f|}{h}}_{\text{round-off}} .$$
Minimising: $h_{\mathrm{opt}}=2\sqrt{u|f|/|f''|}\approx3\cdot10^{-8}$ with
minimal error $\approx2\sqrt{u|f||f''|}\sim10^{-8}$: a first-order formula
cannot deliver more than about half the digits. In general, for order $p$ with
$s$ function values,
$$E(h)\approx Ch^p+\frac{s\,u|f|}{h}\ \Rightarrow\ h_{\mathrm{opt}}\sim u^{1/(p+1)},\quad E_{\min}\sim u^{p/(p+1)} .$$
Central ($p=2$): $h_{\mathrm{opt}}\sim u^{1/3}\approx6\cdot10^{-6}$,
$E_{\min}\sim10^{-11}$. Second derivative: round-off $\sim4u|f|/h^2$,
$h_{\mathrm{opt}}\sim u^{1/4}\approx10^{-4}$, $E_{\min}\sim\sqrt u\approx10^{-8}$
(`diff.optimal_h`).

This is the cleanest instance of [S4]'s error taxonomy (note
[04](04-conditioning-and-error-analysis.md) §1): the discretisation error falls
with $h$, the round-off error rises, and the total is V-shaped.

**Worked example** ($f=e^x$ at $x=1$, `diff.py` `__main__`):

| $h$ | forward | central | 2nd derivative |
|---|---|---|---|
| $10^{-2}$ | $1.4\cdot10^{-2}$ | $4.5\cdot10^{-5}$ | $2.3\cdot10^{-5}$ |
| $10^{-4}$ | $1.4\cdot10^{-4}$ | $4.5\cdot10^{-9}$ | $3.8\cdot10^{-8}$ |
| $10^{-5}$ | $1.4\cdot10^{-5}$ | $5.9\cdot10^{-11}$ | $6.0\cdot10^{-6}$ |
| $10^{-8}$ | $6.6\cdot10^{-9}$ | $6.6\cdot10^{-9}$ | $2.7$ |
| $10^{-10}$ | $1.6\cdot10^{-6}$ | $6.7\cdot10^{-7}$ | $4.4\cdot10^{4}$ |

Each column bottoms out exactly where the estimate predicts, then grows like
$1/h$ (or $1/h^2$).

## 3. Richardson extrapolation *(the general form of §1)*

If an approximation has a known asymptotic expansion
$$D(h)=L+c_1h^p+c_2h^{2p}+\cdots$$
(central difference: $p=2$, even powers only), then combining two step sizes
kills the leading term:
$$D_1(h)=\frac{r^pD(h/r)-D(h)}{r^p-1}=D(h/r)+\frac{D(h/r)-D(h)}{r^p-1}=L+O(h^{2p}).$$
Repeat in a tableau ($r=2$):
$$T_{i,0}=D(h/2^i),\qquad T_{i,j}=T_{i,j-1}+\frac{T_{i,j-1}-T_{i-1,j-1}}{2^{jp}-1},\qquad T_{i,j}=L+O(h^{(j+1)p}).$$
Each column gains $p$ orders; the diagonal is the best estimate and
$|T_{i,i}-T_{i-1,i-1}|$ is an error estimate. With $D(h)=T_h$ the trapezoid rule
and $p=2$ this **is** Romberg integration (note
[03](03-numerical-integration.md) §4), and with $D(h)$ a difference quotient it
is [S4 §1.4] specialised from Neville to a geometric $h$-sequence.

Errors of the tableau, $f=e^x$ at $x=1$, central difference, $h=0.5$:

```
+1.2e-01
+2.8e-02  -3.6e-04
+7.1e-03  -2.2e-05  +1.3e-07
+1.8e-03  -1.4e-06  +2.1e-09  -7.2e-12
+4.4e-04  -8.6e-08  +3.2e-11  -3.2e-14  -3.6e-15
```

Column 0 drops by 4 per row ($p=2$), column 1 by 16, column 2 by 64, and the
diagonal reaches machine precision from step sizes as large as $0.5/16$, where no
single formula suffers from round-off. **That is the practical answer to §2: do
not shrink $h$, extrapolate.** Exactly [S4]'s point in §1.4.

## Pitfalls

- Using $h=10^{-12}$ "to be accurate". The result is noise.
- Extrapolating a non-smooth $D(h)$ and expecting the columns to improve
  [S4 Ex. 1.18].
- Richardson with the wrong $p$: $p=1$ for a central difference wastes a column;
  $p=2$ for a forward difference (odd powers present) combines the wrong terms.
- Central differences at a boundary need points outside the domain. Use the
  one-sided second-order stencil rather than dropping to first order.
- Non-smooth or noisy $f$ (tabulated data): the Taylor error terms do not exist
  and differentiation amplifies noise by $1/h$. Smooth first: spline or least
  squares, note [01](01-polynomial-interpolation.md).
- Forgetting that $h$ must be representable: compute $h=(x+h)-x$ so the step
  itself carries no extra rounding.

## Exam-style questions

No past paper has a standalone differentiation question, which is itself the
message. What *is* asked is the Neville/extrapolation content of note
[01](01-polynomial-interpolation.md) (F1 5a, S1a 1.5b, F3 2.5a). These are ours.

1. *Derive the central difference formula and its error term.*
   $f(x+h)-f(x-h)=2hf'+\tfrac{h^3}3f'''+\cdots$; divide by $2h$; error
   $\tfrac{h^2}6f'''(\xi)$.
2. *Why does the error grow again for very small $h$? Give $h_{\mathrm{opt}}$ for
   the forward and the central difference in double precision.*
   Rounding errors $\sim u|f|$ in the function values are divided by $h$.
   $h_{\mathrm{opt}}\sim\sqrt u\approx10^{-8}$ (forward), $u^{1/3}\approx6\cdot10^{-6}$
   (central).
3. *Find $w_{-1},w_0,w_1$ with $w_{-1}f(x-h)+w_0f(x)+w_1f(x+h)=h^2f''(x)+O(h^4)$.*
   $w_{-1}+w_0+w_1=0$, $-w_{-1}+w_1=0$, $\tfrac12(w_{-1}+w_1)=1$ $\Rightarrow$
   $(1,-2,1)$.
4. *$D(h)=L+ch^2+O(h^4)$, $D(0.2)=1.0400$, $D(0.1)=1.0100$. Extrapolate.*
   $L\approx D(0.1)+\tfrac{D(0.1)-D(0.2)}{3}=1.0100-0.0100=1.0000$.
5. *Which error dominates for the 3-point second-derivative formula at
   $h=10^{-6}$ in double precision?*
   Round-off: $4u/h^2\approx4\cdot10^{-16}/10^{-12}=4\cdot10^{-4}$, against a
   truncation error $\sim10^{-13}$.
6. *How does [S4] get a good derivative without a small $h$?*
   It does not use a small $h$: it evaluates $D(h_j)$ at a geometric sequence of
   *moderate* $h_j$ and extrapolates the interpolating polynomial to $h=0$ with
   the Neville scheme, gaining one order per column [S4 §1.4, Thm 1.17].

## Implementation

`src/py/diff.py`: `forward_diff`, `backward_diff`, `central_diff`, `second_diff`,
`fd_weights` (any stencil, any derivative), `optimal_h`, `richardson` (tableau),
`gradient_fd`.
`src/py/neville.py`: `extrapolate_derivative` ([S4 §1.4]).

Tests: `test_diff.py` (measured orders, known stencils,
`scipy.differentiate.derivative`, Richardson column orders) and
`test_neville.py` (the $h^{m+1}$ column rate of [S4 Thm 1.17] on $f=e^x$, and
the stalled $\sqrt h$ columns of [S4 Ex. 1.18] on $u=|x|^{3/2}$).
