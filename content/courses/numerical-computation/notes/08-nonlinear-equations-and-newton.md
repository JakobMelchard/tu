# 08 Nonlinear equations and Newton's method

[S4] §6. Find $x^\ast$ with $f(x^\ast)=0$ for $f:\mathbb R^d\to\mathbb R^d$.
There is no formula, so the zero is approximated by a **fixed-point iteration**
$$x_{n+1}=\Phi(x_n)\qquad\text{[S4 (6.1)]}$$
with $x_0$ close enough. If $x_n\to x^\ast$ and $\Phi$ is continuous then
$x^\ast=\Phi(x^\ast)$ [S4 Exercise 6.1]. The three questions are always: does it
converge, **from where**, and how fast. Implementation: `src/py/nonlinear.py`,
`src/py/optimize.py`.

## 1. Newton in 1-D [S4 §6.1]

Linearise at the current iterate and take the zero of the linearisation:
$$L(x)=f(x_n)+f'(x_n)(x-x_n)\ \Rightarrow\ \boxed{\;x_{n+1}=x_n-\frac{f(x_n)}{f'(x_n)}\;}\qquad\text{[S4 (6.2)]}$$
a fixed-point iteration with $\Phi_{\mathrm{Newton}}(x)=x-f(x)/f'(x)$ [S4 (6.3)].

**The canonical example** [S4 Ex. 6.2]: $x^\ast=\sqrt a$ is the zero of
$f(x)=x^2-a$, so $x_{n+1}=x_n-\tfrac{x_n^2-a}{2x_n}$. For $a=2$, $x_0=2$:

| $n$ | $x_n$ | $|x_n-\sqrt2|$ |
|---|---|---|
| 1 | $1.5$ | $8.58\cdot10^{-2}$ |
| 2 | $1.416666666666667$ | $2.45\cdot10^{-3}$ |
| 3 | $1.414215686274510$ | $2.12\cdot10^{-6}$ |
| 4 | $1.414213562374690$ | $1.59\cdot10^{-12}$ |

exact $1.414213562373095$. The errors square: **quadratic convergence**. This is
the problem S2a 2.4a set ("three steps from $x_0=2$"); F2 2.2b set the same thing
for $f=x^2+3x-4$ from $x_0=1$ (root $1$; note $f'(1)=5\ne0$).

## 2. Convergence of fixed-point iterations [S4 §6.2]

**Definition** [S4 Def. 6.3]. $\Phi:\mathbb R^d\to\mathbb R^d$ is a
**contraction** near $x^\ast$ if there are $q\in(0,1)$, $\varepsilon>0$ with
$$\|\Phi(x)-\Phi(y)\|\le q\|x-y\|\qquad\forall x,y\in B_\varepsilon(x^\ast).$$
For $d=1$ and $\Phi\in C^1$, $|\Phi'(x^\ast)|<1$ suffices [S4 Exercise 6.4]; in
$\mathbb R^d$, $\|\Phi'(x^\ast)\|<1$ in some norm [S4 Exercise 6.6].

**Theorem** [S4 Thm 6.5]. If $\Phi$ is a contraction with constant $q$ near its
fixed point $x^\ast$, there is $\varepsilon>0$ such that every $x_0\in B_\varepsilon(x^\ast)$
gives $x_n\to x^\ast$ with
$$\|x^\ast-x_{n+1}\|\le q\,\|x^\ast-x_n\|\qquad\text{[S4 (6.5)]},$$
i.e. **linear** convergence with rate $q$. Proof: one line,
$\|x^\ast-x_{n+1}\|=\|\Phi(x^\ast)-\Phi(x_n)\|\le q\|x^\ast-x_n\|$, then
induction.

**The example that shows the rewriting matters** [S4 Ex. 6.7]. Solve
$2-x^2-e^x=0$ (one positive root, $x^\ast=0.5372744491738\ldots$). Two rewritings:
$$\Phi_1(x)=\sqrt{2-e^x},\qquad \Phi_2(x)=\ln(2-x^2).$$
From $x_0=0.5$, $\Phi_2$ converges and $\Phi_1$ **diverges**: it even leaves the
domain at step 5, since $2-e^{0.87}<0$. The reason is exactly the criterion:
$$|\Phi_1'(x^\ast)|=\Big|\frac{-e^{x^\ast}}{2\sqrt{2-e^{x^\ast}}}\Big|=1.5926>1,\qquad
|\Phi_2'(x^\ast)|=\Big|\frac{-2x^\ast}{2-(x^\ast)^2}\Big|=0.6279<1 .$$
([S4] prints $0.31$ for the second; recomputing gives $0.6279$, and the ratio of
successive errors in [S4]'s **own** printed iterate table (reproduced to 15
digits in `test_nonlinear.py`) is $-0.628$. The conclusion is unaffected.)

**Higher order** [S4 Thm 6.8]. If $\Phi\in C^p$, $p\ge2$, $x^\ast=\Phi(x^\ast)$
and $\Phi^{(j)}(x^\ast)=0$ for $j=1..p-1$, then
$$|x^\ast-x_{n+1}|\le C|x^\ast-x_n|^p ,$$
by Taylor expansion with integral remainder,
$C=\|\Phi^{(p)}\|_{\infty,B_\varepsilon}/(p-1)!$. We say the iteration converges
**with order $p$**; $p=2$ is *quadratic*.

**Corollary** [S4 Cor. 6.9]: the theorem behind the exam question. For $d=1$,
$f\in C^2$, $f(x^\ast)=0$ and $f'(x^\ast)\ne0$, Newton converges quadratically:
one computes $\Phi_{\mathrm{Newton}}'(x^\ast)=\dfrac{ff''}{(f')^2}\Big|_{x^\ast}=0$
and applies Thm 6.8. Note the **proof route: fixed-point theory** (S2a 2.5b marks
this true).

$f'(x^\ast)\ne0$ is not an artefact [S4 Exercise 6.10]: for $f(x)=x^2$ Newton
becomes $x_{n+1}=x_n-\tfrac{x_n^2}{2x_n}=\tfrac{x_n}2$, which is **linear** with
rate $\tfrac12$. (S2a 2.4c asks exactly this.) In general, for a root of
multiplicity $m$, $\Phi'(x^\ast)=1-\tfrac1m$; the cure is to iterate
$x-m\,f/f'$, or to apply Newton to $f/f'$, which restores order 2. *(The
multiplicity-$m$ formula is standard [S16]; [S4] gives only the $m=2$ case.)*

**Convergence order in practice.** From three consecutive errors,
$$p\approx\frac{\log(e_{n+1}/e_n)}{\log(e_n/e_{n-1})}\qquad(\texttt{nonlinear.convergence\_order}).$$

**Other bracketing/derivative-free methods** *(not in [S4], kept because they are
the standard comparison and appear in the exercise sheets)*: **bisection**
(always converges to a sign change, linear with rate $\tfrac12$, error
$\le(b-a)2^{-(k+1)}$) and the **secant method**
$$x_{n+1}=x_n-f(x_n)\frac{x_n-x_{n-1}}{f(x_n)-f(x_{n-1})},$$
of order $\varphi=\tfrac{1+\sqrt5}2\approx1.618$ with one new evaluation per
step, so two secant steps ($\varphi^2=2.618$) beat one Newton step when $f'$ is
as expensive as $f$.

## 3. Newton in $\mathbb R^d$ [S4 §6.3]

Same idea, with the Jacobian $f'(x)_{ij}=\partial f_i/\partial x_j$:
$$x_{n+1}=x_n-\big(f'(x_n)\big)^{-1}f(x_n)\qquad\text{[S4 (6.8)]}.$$
**Theorem** [S4 Thm 6.11]. $f\in C^2(B_\delta(x^\ast))$, $f(x^\ast)=0$,
$f'(x^\ast)$ invertible $\Rightarrow$ there are $\varepsilon,C>0$ with, for
$x_0\in B_\varepsilon(x^\ast)$, $x_n\to x^\ast$ and
$\|x^\ast-x_{n+1}\|\le C\|x^\ast-x_n\|^2$.

**Never invert** [S4 Rem. 6.12]: compute $f(x_n)$ and $f'(x_n)$, solve
$f'(x_n)\delta=-f(x_n)$ by LU (note
[05](05-gaussian-elimination-and-lu.md), $\tfrac23d^3$ per step), update
$x_{n+1}=x_n+\delta$.

## 4. Implementation aspects [S4 §6.4]

**Stopping.** Near $x^\ast$ with quadratic convergence, $\|x_{n+1}-x_n\|$ is a
good estimate of $\|x_n-x^\ast\|$, because
$\|x_n-x^\ast\|\le\|x_n-x_{n+1}\|+\|x_{n+1}-x^\ast\|$ and the last term is
$O(\|x_n-x^\ast\|^2)$. So stop on $\|x_{n+1}-x_n\|\le\mathrm{tol}$. If a Newton
step is expensive, approximate it by $\|(f'(x_{n-1}))^{-1}f(x_n)\|$: the LU
factorisation of $f'(x_{n-1})$ is already there.

**Residual as an error measure** [S4 Rem. 6.13]. $f(x_n)\approx f'(x^\ast)(x_n-x^\ast)$,
so
$$\|f(x_n)\|\le\|f'(x^\ast)\|\|x^\ast-x_n\|+O(\|\cdot\|^2),\qquad \|x^\ast-x_n\|\le\|(f'(x^\ast))^{-1}\|\|f(x_n)\|+O(\|\cdot\|^2)$$
useful up to the constants $\|f'(x^\ast)\|$ and $\|(f'(x^\ast))^{-1}\|$, i.e.
up to the conditioning of $f'(x^\ast)$.

**The Jacobian.** If only $f$ is available (a C library, say), approximate
$f'(x_n)$ by difference quotients (`nonlinear.jacobian_fd`, $d$ extra
evaluations; choose $h$ by note [12](12-numerical-differentiation.md)). If
$f'(x_n)$ is expensive, freeze it: the **simplified Newton method**
$x_{n+1}=x_n-(f'(x_0))^{-1}f(x_n)$ is only **linearly** convergent [S4 §6.4].

Invariance [S4 Exercise 6.14]: for invertible $B$, the Newton iterates for
$f$ and for $\tilde f=Bf$ coincide: Newton does not care how the residual is
scaled.

## 5. Damped and globalised Newton [S4 §6.5]

Newton converges only locally; the steps are often too large.

**Damped Newton** [S4 (6.12)]: $x_{n+1}=x_n-\lambda_n(f'(x_n))^{-1}f(x_n)$ with
$\lambda_n\in(0,1]$. Converges from more starting points but **only linearly**
unless $\lambda_n\to1$ near the root.

**Descent methods** [S4 §6.5.2]. To minimise $g:\mathbb R^d\to\mathbb R$: pick a
direction $d_n$ with $\nabla g(x_n)\cdot d_n<0$ (a *descent direction*) and a
step length $\lambda_n$ with $g(x_n+\lambda_nd_n)<g(x_n)$. Steepest descent takes
$d_n=-\nabla g(x_n)$, for which $\nabla g\cdot d_n=-\|\nabla g\|^2<0$. Exact line
search is too expensive, so use the **Armijo rule**: with $\sigma,q\in(0,1)$,
take the largest step of the form $q^k$ satisfying
$$g(x_n+q^kd_n)<g(x_n)+\sigma\,\big(\nabla g(x_n)\cdot d_n\big)\,q^k\qquad\text{[S4 (6.13)]},$$
trying $k=0,1,2,\ldots$ in turn. ("The Armijo rule is a way to choose the step
length in a descent method": **true**, S2a 2.5c.)

**Globalised Newton as a descent method** [S4 §6.5.3]. Zeros of $f$ are minima of
$g(x):=\|f(x)\|_2^2$. The Newton direction $d_n=-(f'(x_n))^{-1}f(x_n)$ *is* a
descent direction for $g$: by [S4 Lem. 6.15],
$$\tilde g(\lambda)=g(x+\lambda d)=g(x)-2\lambda g(x)+O(\lambda^2),$$
so a descent of about $2\lambda_n g(x_n)$ is available. Requiring the full
greedy $2\lambda_n\|f(x_n)\|^2$ would conflict with full Newton steps (which
reduce $\|f\|^2$ by almost all of it, since
$\|f(x_{n+1})\|^2\le C\|f(x_n)\|^4$), so [S4 Alg. 15] asks for
$\mu\lambda_n\|f(x_n)\|_2^2$ instead:

```
lambda := 1
while not converged:
    d := -f'(x)^{-1} f(x)
    while ||f(x)||^2 - ||f(x + lambda*d)||^2 < mu * lambda * ||f(x)||^2:
        lambda := lambda * q                 # not enough descent, shrink
    x := x + lambda*d
    lambda := min(1, lambda/q)               # try a slightly larger step next
```

The final line is what recovers $\lambda_n=1$, and with it quadratic
convergence, once the iterates are near $x^\ast$.

## 6. Gauss–Newton [S4 §6.6]

Nonlinear least squares: for $F:\mathbb R^d\to\mathbb R^m$, minimise
$\|F(x)\|_2$ [S4 (6.16)]: fitting parameters of a nonlinear model. A minimum
satisfies $G(x):=(F'(x))^\top F(x)=0$, and the Newton iteration for $G$ needs
$$G'(x)=(F'(x))^\top F'(x)+(F''(x))^\top F(x)\qquad\text{[S4 (6.17)]},$$
whose second term involves a third-order tensor. **Drop it.** The resulting
method
$$(F'(x_n))^\top F'(x_n)\,\Delta x_n=-(F'(x_n))^\top F(x_n)\qquad\text{[S4 (6.18)]}$$
is exactly the normal equations (note [07](07-least-squares-and-svd.md)) of the
**linear** least-squares problem
$$\min_{\Delta x}\|F'(x_n)\Delta x+F(x_n)\|_2^2\qquad\text{[S4 (6.19)]},$$
so a nonlinear least-squares problem becomes a sequence of linear ones, and
$F''$ is never needed.

**Theorem** [S4 Thm 6.17]. If $F$ is smooth, $F(x^\ast)=0$ and $F'(x^\ast)$ has
full rank, Gauss–Newton converges locally **quadratically**: the dropped term
$F''F$ vanishes asymptotically. If $F(x^\ast)\ne0$ (a *large-residual* problem)
it still converges, but only **linearly**. For $d=m=1$ with $f(x^\ast)=0$,
$f'(x^\ast)\ne0$, it reduces to ordinary Newton [S4 Exercise 6.18].

## 7. Broyden's method [S4 §6.7] (CSE)

Quasi-Newton: $x_{n+1}=x_n-H_n^{-1}f(x_n)$ with $H_n$ an updated approximation
to $f'(x_{n+1})$. From Taylor, $f'(x_{n+1})(x_{n+1}-x_n)\approx f(x_{n+1})-f(x_n)$,
giving the **secant condition**
$$H_{n+1}(x_{n+1}-x_n)=f(x_{n+1})-f(x_n)\qquad\text{[S4 (6.20)]}.$$
That does not determine $H_{n+1}$ for $d>1$, so ask additionally that $H_{n+1}$
stay close to $H_n$:
$$\min\{\|A-H_n\|_F\ :\ A\,s=y\},\qquad s=x_{n+1}-x_n,\ y=f(x_{n+1})-f(x_n),$$
whose unique solution is the **rank-1 update** [S4 Lem. 6.19, (6.22)]
$$H_{n+1}=H_n+\frac1{\|s\|_2^2}(y-H_ns)\,s^\top .$$
Two consequences [S4 §6.7.1]:

1. Local **superlinear** convergence: $\|x_{n+1}-x_n\|\le\epsilon_n\|x_n-x_{n-1}\|$
   with $\epsilon_n\to0$.
2. A rank-1 update lets $H_{n+1}^{-1}$ be obtained from $H_n^{-1}$ cheaply, by
   the **Sherman–Morrison–Woodbury** formula [S4 (6.23)]
   $$(A+uv^\top)^{-1}=A^{-1}-\frac{1}{1+v^\top A^{-1}u}A^{-1}uv^\top A^{-1}.$$

Example [S4 Ex. 6.20]: $x^\ast=(0,1)^\top$ for
$$F(x)=\begin{pmatrix}(x_1+3)(x_2^3-7)+18\\ \sin(x_2e^{x_1}-1)\end{pmatrix},\qquad x_0=(-0.5,1.4)^\top,\ H_0=F'(x_0),$$
with Newton, Broyden and steepest descent ($\sigma=0.9$, $q=0.5$) compared: in
about 8 iterations Newton reaches $10^{-16}$, Broyden roughly $10^{-13}$
(visibly superlinear but not quadratic), steepest descent barely $10^{-3}$.
Variants that preserve symmetry and positive definiteness for minimisation: PSB,
DFP, **BFGS** [S4 Rem. 6.21]. Like globalised Newton, Broyden is combined with a
step-length rule in practice [S4 Rem. 6.22].

## 8. Unconstrained minimisation [S4 §6.8] (CSE)

Three routes to $\min f$ [S4 §6.8]: globalised Newton on $\nabla f=0$ (needs the
Hessian); a descent method (needs only $\nabla f$); or a trust-region method.

**Gradient method on a quadratic** [S4 §6.8.1]. For
$f(x)=\gamma+c^\top x+\tfrac12x^\top Qx$ with $Q$ SPD and $d_n=-\nabla f(x_n)$,
the exact line-search step is computable:
$$t=-\frac{\nabla f(x_n)\cdot d_n}{d_n^\top Qd_n}.$$
**Lemma 6.23** [S4]: steepest descent on this $f$ degrades badly when $Q$ has
widely differing eigenvalues: the zig-zag picture, and the reason CG exists
(note [10](10-iterative-linear-systems.md)). The minimiser itself is of course
just $Qx=-c$ [S4 Rem. 6.24].

**Trust region** [S4 §6.8.2]: approximate $f$ locally by a quadratic and minimise
it *inside a region where the approximation is trusted*, adapting the radius.
Realising this is non-trivial because the subproblem is constrained
[S4 Rem. 6.25].

## Pitfalls

- Choosing the fixed-point rewriting with $|\Phi'(x^\ast)|>1$ [S4 Ex. 6.7].
- Expecting quadratic convergence at a multiple root. $f'(x^\ast)=0$ gives linear
  convergence with rate $1-1/m$ [S4 Exercise 6.10].
- Quoting quadratic convergence as a global statement. [S4 Cor. 6.9] and
  Thm 6.11 are both *local*, and neither says how large $\varepsilon$ is.
- Forming $(f')^{-1}$ instead of solving a linear system [S4 Rem. 6.12].
- Stopping on $|f(x_n)|<\tau$ without scaling: for $f=10^{-8}(x-1)$ everything
  passes, for $f=10^8(x-1)$ nothing does. Use $\|x_{n+1}-x_n\|$ [S4 §6.4].
- Assuming undamped Newton decreases $\|f\|$. It need not: that is precisely
  why [S4 Alg. 15] exists.
- Using Gauss–Newton on a large-residual problem and expecting order 2; you get
  order 1 [S4 Thm 6.17].
- A finite-difference Jacobian with $h$ too small (round-off) or too large
  (bias); see note [12](12-numerical-differentiation.md).
- Secant near a flat $f$: $f(x_n)-f(x_{n-1})$ cancels.

## Exam-style questions

Modelled on S2a 2.4/2.5, F2 2.2 and F3 2.4; see [00](00-exam-focus.md).

1. *(S2a 2.4, 2024W)* $f(x)=x^2-2$.
   (a) Do three Newton steps from $x_0=2$.
   (b) Under which conditions does 1-D Newton converge quadratically, and what
   does that mean?
   (c) For $g(x)=x^2$ from $x_0=1$, do you expect quadratic convergence?
   (a) $x_{n+1}=\tfrac12(x_n+2/x_n)$: $1.5$, $1.4166\overline6$,
   $1.4142156862745098$ (errors $8.6\cdot10^{-2}$, $2.5\cdot10^{-3}$,
   $2.1\cdot10^{-6}$) [S4 Ex. 6.2].
   (b) $f\in C^2$, $f(x^\ast)=0$, **$f'(x^\ast)\ne0$**, $x_0$ close enough
   [S4 Cor. 6.9]; then $|x^\ast-x_{n+1}|\le C|x^\ast-x_n|^2$: the number of
   correct digits roughly doubles per step.
   (c) No. $x^\ast=0$ is a double root, $g'(0)=0$; the iteration is
   $x_{n+1}=x_n/2$, linear with rate $\tfrac12$ [S4 Exercise 6.10].
2. *(F2 2.2, 2022W)* $f(x)=x^2+3x-4$. (a) Does the fixed-point iteration
   converge from $x_0=1$ to $x^\ast=1$? (b) Compute $x_1,x_2$ with Newton from
   $x_0=1$ (or $0$).
   (a) $x^\ast=1$ is already the root ($1+3-4=0$), so state which $\Phi$ you
   chose and test $|\Phi'(1)|<1$: e.g. $\Phi(x)=(4-x^2)/3$ has
   $\Phi'(1)=-\tfrac23$, so yes, linearly with rate $\tfrac23$.
   (b) $f'=2x+3$. From $x_0=0$: $x_1=0-(-4)/3=4/3$;
   $f(4/3)=16/9+4-4=16/9$, $f'(4/3)=17/3$, so
   $x_2=4/3-\tfrac{16/9}{17/3}=4/3-\tfrac{16}{51}=\tfrac{68-16}{51}=\tfrac{52}{51}\approx1.0196$.
3. *(F3 2.4, 2022W re-test)* (a) Define a contraction and explain how it relates
   to fixed points and to Newton. (b) When and how does Newton converge
   quadratically?
   (a) [S4 Def. 6.3]; a contraction has a unique fixed point nearby and the
   iteration converges linearly with rate $q$ [S4 Thm 6.5]. Newton **is** a
   fixed-point iteration for $\Phi=x-f/f'$, and its quadratic convergence is
   Thm 6.8 applied to $\Phi'(x^\ast)=0$ [S4 Cor. 6.9].
   (b) As in 1(b).
4. *(S2a 2.5: true or false)*
   (i) The proof of quadratic convergence of 1-D Newton rests on fixed-point
   theory. **True** [S4 Cor. 6.9].
   (ii) The Armijo rule is a way to choose the step length in a descent method.
   **True** [S4 (6.13)].
5. *(ours)* Write one step of Newton for $F:\mathbb R^d\to\mathbb R^d$ and give
   the cost.
   Solve $F'(x_n)\delta=-F(x_n)$ by LU, $\tfrac23d^3$, then $x_{n+1}=x_n+\delta$;
   plus $d^2$ Jacobian entries [S4 Rem. 6.12].
6. *(ours)* Derive Gauss–Newton and say when it keeps order 2.
   $\nabla\|F\|_2^2=0$ means $(F')^\top F=0$; Newton on that needs
   $(F')^\top F'+(F'')^\top F$; drop the second term. The step solves the linear
   least-squares problem $\min\|F'(x_n)\Delta x+F(x_n)\|_2$ [S4 (6.19)]. Order 2
   **iff** $F(x^\ast)=0$ and $F'(x^\ast)$ has full rank; otherwise order 1
   [S4 Thm 6.17].
7. *(ours: CSE)* State the secant condition and the Broyden update, and say why
   the update is cheap.
   $H_{n+1}s=y$ with $s=x_{n+1}-x_n$, $y=f(x_{n+1})-f(x_n)$ [S4 (6.20)];
   $H_{n+1}=H_n+\|s\|_2^{-2}(y-H_ns)s^\top$, the Frobenius-closest matrix
   satisfying it [S4 Lem. 6.19]. It is rank 1, so
   Sherman–Morrison–Woodbury updates the inverse in $O(d^2)$ [S4 (6.23)].

## Implementation

`src/py/nonlinear.py`: `bisection`, `fixed_point`, `newton`, `secant`,
`newton_system` (analytic or finite-difference Jacobian, `damped=True`),
`jacobian_fd`, `convergence_order`, **`simplified_newton`** ([S4 §6.4]).

`src/py/optimize.py` (new): `armijo` ([S4 (6.13)]), `steepest_descent`,
`globalized_newton` ([S4 Alg. 15] verbatim), `gauss_newton` ([S4 (6.19)]),
`broyden` ([S4 (6.22)]), `sherman_morrison` ([S4 (6.23)]),
`gradient_descent_quadratic` ([S4 §6.8.1]).

Tests: `test_nonlinear.py` (against `scipy.optimize.brentq`, `fsolve`,
`fixed_point`; the orders $\tfrac12$, 1, $\varphi$, 2; **the four $\sqrt2$
iterates of [S4 Ex. 6.2] to 15 digits**; the $\Phi_1$-diverges /
$\Phi_2$-converges pair of [S4 Ex. 6.7] with $x^\ast=0.5372744491738$; the
linear rate $\tfrac12$ on $f=x^2$ of [S4 Exercise 6.10]) and `test_optimize.py`
(the Armijo descent condition; globalised Newton on $\arctan$ from $x_0=3$ where
plain Newton diverges; Gauss–Newton quadratic on a zero-residual fit and linear
on a large-residual one [S4 Thm 6.17]; **the [S4 Ex. 6.20] $F$ with
$x_0=(-0.5,1.4)$, $H_0=F'(x_0)$**, checking $x^\ast=(0,1)$ and the
Newton > Broyden > steepest-descent ordering; Sherman–Morrison against
`numpy.linalg.inv`).
