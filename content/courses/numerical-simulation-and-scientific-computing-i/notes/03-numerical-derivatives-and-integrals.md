# 03 Numerical derivatives and integrals

Replacing $f'$ and $\int f$ by sums of point values. The two questions are always: what is the truncation error order in $h$, and where does round-off take over.

Every weight and every error constant below is **regenerated in exact rational arithmetic** by `src/py/fdstencil.py` and asserted in `src/py/test_fdstencil.py`, so the table is checked, not copied. Fornberg's algorithm [S25] is the general construction; the composite quadrature rules and their error constants are classical and are verified numerically in `test_fd_poisson.py`.

## Finite-difference derivatives

Taylor expansion around $x$: $f(x \pm h) = f \pm h f' + \frac{h^2}{2} f'' \pm \frac{h^3}{6} f''' + \frac{h^4}{24} f'''' + \dots$

| formula | stencil | leading error |
|---|---|---|
| forward $D_+ f = \dfrac{f(x+h) - f(x)}{h}$ | $(0, 1)$ | $\frac{h}{2} f''$, order 1 |
| backward $D_- f = \dfrac{f(x) - f(x-h)}{h}$ | $(-1, 0)$ | $-\frac{h}{2} f''$, order 1 |
| central $D_0 f = \dfrac{f(x+h) - f(x-h)}{2h}$ | $(-1, 1)$ | $\frac{h^2}{6} f'''$, order 2 |
| second derivative $\dfrac{f(x+h) - 2f(x) + f(x-h)}{h^2}$ | $(-1,0,1)$ | $\frac{h^2}{12} f''''$, order 2 |
| 4th-order central $\dfrac{-f_{+2} + 8 f_{+1} - 8 f_{-1} + f_{-2}}{12 h}$ | 4 points $(-2,-1,1,2)$ | $-\frac{h^4}{30} f^{(5)}$, order 4 |
| one-sided 2nd order $\dfrac{-3 f_0 + 4 f_1 - f_2}{2h}$ | boundary $(0,1,2)$ | $-\frac{h^2}{3} f'''$, order 2 |
| 4th-order 2nd deriv $\dfrac{-f_{+2} + 16 f_{+1} - 30 f_0 + 16 f_{-1} - f_{-2}}{12 h^2}$ | 5 points | $-\frac{h^4}{90} f^{(6)}$, order 4 |

General recipe: choose stencil points $s_0,\dots,s_n$ (in units of $h$), write the Taylor series of each, and solve the **order conditions**
$$\sum_j w_j \frac{s_j^k}{k!} = \frac{\delta_{kd}}{h^d}, \qquad k = 0,\dots,n$$
for the weights of the $d$-th derivative - a Vandermonde system. The leading error is read off the first condition the weights *fail*: if $C = \sum_j w_j s_j^m/m! \ne 0$ at order $m$, the truncation error is $C\,h^{m-d} f^{(m)}$. That is the signed constant in the table above, and it is what `fdstencil.leading_error_term` returns.

**Fornberg's algorithm** [S25] does the same in $O(n^2 d)$ by a recurrence, for **arbitrarily spaced** nodes and for every derivative order up to $d$ at once - the nodes need not be a uniform grid, which is what makes it the routine real codes use (`fdstencil.weights_fornberg`). Both routes agree to machine precision in `test_fdstencil.py`.

### Round-off and the optimal step

Function values carry relative error $\epsilon \approx 1.1 \cdot 10^{-16}$ (IEEE binary64 unit round-off $2^{-53}$; `numpy.finfo(float).eps` is $2^{-52} = 2.2\cdot10^{-16}$, twice that, because numpy reports the machine epsilon rather than the unit round-off - a classic factor-of-two trap). In $D_+$ the difference of two nearly equal numbers divided by $h$ amplifies it to $\epsilon |f| / h$. Total error

$$E(h) \approx C h^p + \frac{\epsilon |f|}{h}, \qquad h_{\text{opt}} \sim \epsilon^{1/(p+1)}.$$

Forward ($p=1$): $h_{\text{opt}} \approx 10^{-8}$, best error $\approx 10^{-8}$. Central ($p=2$): $h_{\text{opt}} \approx 10^{-5.3}$, best error $\approx 10^{-11}$. Second derivative: $\epsilon / h^2$ term, $h_{\text{opt}} \approx 10^{-4}$, best error $\approx 10^{-8}$. Smaller $h$ is worse, not better. Automatic differentiation or complex-step differentiation ($f'(x) \approx \operatorname{Im} f(x + ih)/h$, no cancellation, so $h = 10^{-100}$ is fine) avoid this. Both need $f$ as code, not as a black box.

### Richardson extrapolation

If $D(h) = f' + c h^p + O(h^{p+2})$, then
$$\frac{2^p D(h/2) - D(h)}{2^p - 1} = f' + O(h^{p+2}).$$
Applied to the trapezoid rule this is Romberg integration.

### Measuring the order

With errors $e_h$ and $e_{h/2}$ against a known solution: observed order $p = \log_2(e_h / e_{h/2})$. If the exact answer is unknown, use three levels: $p = \log_2 \dfrac{D(h) - D(h/2)}{D(h/2) - D(h/4)}$. Always print this table; it is the standard correctness test for any discretisation (see `fd_poisson1d.cpp`, order column 2.008, 2.002, 2.001, ...).

## Quadrature

$I = \int_a^b f(x)\,dx$, $n$ panels, $h = (b-a)/n$, $x_i = a + i h$.

| rule (composite) | formula | error | exact for polynomials of degree |
|---|---|---|---|
| midpoint | $h \sum_{i=0}^{n-1} f(x_i + h/2)$ | $\frac{(b-a) h^2}{24} f''(\xi)$ | 1 |
| trapezoid | $h \left[\frac{f_0}{2} + f_1 + \dots + f_{n-1} + \frac{f_n}{2}\right]$ | $-\frac{(b-a) h^2}{12} f''(\xi)$ | 1 |
| Simpson ($n$ even) | $\frac{h}{3}[f_0 + 4 f_1 + 2 f_2 + 4 f_3 + \dots + f_n]$ | $-\frac{(b-a) h^4}{180} f''''(\xi)$ | 3 |
| Gauss-Legendre, $m$ nodes per panel | $\sum_j w_j f(x_j)$, nodes = roots of $P_m$ | $O(h^{2m})$ | $2m-1$ |

Every composite error constant in this table is checked by measuring the observed order in `test_fd_poisson.py::test_quadrature_orders_and_scipy`; the constants themselves are classical (any of [S22] [S23] [S35] restate them).

Derivation of the trapezoid error: integrate the linear interpolant error $\frac{1}{2} f''(\xi)(x - x_i)(x - x_{i+1})$ over one panel gives $-\frac{h^3}{12} f''$; sum over $n = (b-a)/h$ panels. Simpson is the Richardson extrapolation of the trapezoid rule: $S = (4 T_{h/2} - T_h)/3$.

Special cases worth knowing:
- Periodic smooth integrand over a full period: the trapezoid rule converges exponentially - every correction term in the Euler-Maclaurin expansion contains $f^{(2k-1)}(b) - f^{(2k-1)}(a)$, which vanishes by periodicity, so the error decays faster than any power of $h$. For an analytic integrand the rate is geometric in the width of the strip of analyticity.
- Endpoint singularities such as $\int_0^1 x^{-1/2} dx$: substitute $x = t^2$, or use Gauss-Jacobi, or open rules (midpoint) that avoid the endpoint.
- Non-smooth integrands (kinks): order drops to 2 (or 1) no matter which rule; split the interval at the kink.
- Adaptive quadrature: recursively halve panels where $|S_h - S_{h/2}| > \text{tol}$ (`scipy.integrate.quad`, QUADPACK).
- Higher dimensions: tensor product costs $n^d$ points, error $h^p = N^{-p/d}$; for $d \gtrsim 4$ Monte Carlo (note 06) or sparse grids win.

## Worked example

`src/py/fd_poisson.py`, `quad_composite` on $f = e^x \cos 3x$ over $[0,1]$ (test `test_quadrature_orders_and_scipy`):

| n | midpoint err | trapezoid err | Simpson err |
|---|---|---|---|
| 8 | 3.2e-3 | 6.3e-3 | 1.4e-4 |
| 16 | 7.9e-4 | 1.6e-3 | 8.8e-6 |
| 32 | 2.0e-4 | 3.9e-4 | 5.5e-7 |
| 64 | 4.9e-5 | 9.9e-5 | 3.4e-8 |

Ratios 4, 4, 16 per halving: orders 2, 2, 4. Midpoint has half the constant of trapezoid (1/24 vs 1/12) with one fewer point. The constants can be predicted, not just the orders: the leading Euler-Maclaurin terms are $T_h - I = \frac{h^2}{12}\,(f'(1) - f'(0))$ and $M_h - I = -\frac{h^2}{24}\,(f'(1) - f'(0))$; here $f'(1) - f'(0) = e(\cos 3 - 3\sin 3) - 1 = -4.84$, so at $n = 8$ they give $-6.30\cdot10^{-3}$ and $+3.15\cdot10^{-3}$ against measured $-6.34\cdot10^{-3}$ and $+3.18\cdot10^{-3}$ (`test_quadrature_error_constants_euler_maclaurin`). (Until 2026-09-27 the midpoint and trapezoid columns here were a factor 2 too large; the code was right, the table was not.)

Derivative of $\sin$ at $x = 0.7$ with $h = 10^{-1}, \dots, 1.25 \cdot 10^{-2}$: forward errors halve, central errors quarter per halving (`test_derivative_orders`).

## Pitfalls

- Using $h = 10^{-12}$ "for accuracy": round-off dominates, the derivative is garbage.
- Applying Simpson with an odd number of panels.
- Testing convergence with a function the rule integrates exactly (polynomial of degree $\le 3$ for Simpson): error is round-off, no order visible.
- Reading the order from two too-coarse grids where the asymptotic regime is not reached; use at least 3-4 halvings.
- Forgetting the $(b - a)$ factor: the *global* error is $O(h^p)$, the per-panel error is $O(h^{p+1})$.

## Exam-style questions

1. **Derive the error term of the central difference.** Subtract $f(x-h)$ from $f(x+h)$: odd terms survive, $f(x+h) - f(x-h) = 2h f' + \frac{h^3}{3} f''' + O(h^5)$. Divide by $2h$: $D_0 f = f' + \frac{h^2}{6} f''' + O(h^4)$.
2. **Why does the error of a finite-difference derivative first decrease and then increase as $h \to 0$? Give the optimal $h$ for the central difference in double precision.** Truncation error $\propto h^2$ falls; round-off $\propto \epsilon/h$ grows because two nearly equal numbers are subtracted and divided by $h$. Minimising $h^2 + \epsilon/h$ gives $h \sim \epsilon^{1/3} \approx 6 \cdot 10^{-6}$, error $\sim \epsilon^{2/3} \approx 10^{-11}$.
3. **How do you check numerically that an implementation of Simpson's rule has order 4?** Integrate a smooth non-polynomial function with $n, 2n, 4n$ panels, compute errors against the exact integral (or against $n = 4096$), print $\log_2(e_n / e_{2n})$; it must approach 4.
4. **The trapezoid rule applied to $\int_0^{2\pi} e^{\cos x} dx$ with 16 panels is accurate to $10^{-14}$. Explain.** The integrand is smooth and periodic over the interval; in the Euler-Maclaurin expansion every correction term contains $f^{(2k-1)}(b) - f^{(2k-1)}(a) = 0$, so the error decays faster than any power of $h$ (exponentially, like a Fourier series).
5. **Why is a 5-point 4th-order stencil not automatically better than the 3-point 2nd-order one in a PDE code?** It needs two boundary layers (special one-sided formulas at the edges), produces a wider matrix band (more memory, less sparse), is harder to make stable for advection, and only pays if the solution is smooth enough that the asymptotic regime is reached on affordable grids.

Code: `src/py/fdstencil.py` (`weights_vandermonde`, `weights_fornberg`, `leading_error_term`, `table` - regenerates the stencil table above), `src/py/fd_poisson.py` (`fd_derivative`, `fd_second_derivative`, `quad_composite`, `convergence_order`); tests `src/py/test_fdstencil.py`, `src/py/test_fd_poisson.py`. Sources: [S25] [S23] [S35].
