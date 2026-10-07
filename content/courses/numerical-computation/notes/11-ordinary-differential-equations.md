# 11 Numerical methods for ODEs

[S4] §9: **the whole chapter is (CSE)**, and [S8] reports that in 2025W it was
covered only "if time". Budget accordingly: it is examinable in the CSE course,
it is the last thing taught, and it is the most likely thing to be cut. Solve
$$y'(t)=f(t,y(t)),\qquad y(0)=y_0\qquad\text{[S4 (9.1)]}$$
on $[0,T]$, seeking $y_i\approx y(t_i)$ at $0=t_0<\cdots<t_N=T$, with
$h_i=t_{i+1}-t_i$ and $h=\max_ih_i$. Implementation: `src/py/ode.py`,
`src/py/irk.py`, `src/py/bvp.py`, `src/cpp/rk4.cpp`.

## 1. Explicit Euler [S4 §9.1]

Taylor at $t_i$: $y(t_{i+1})=y(t_i)+h_iy'(t_i)+O(h_i^2)$, so
$$y_{i+1}:=y_i+h_if(t_i,y_i)\qquad\text{[S4 (9.2)]}.$$

**Consistency error** [S4 Def. 9.1]: the error of *one* step started from the
exact solution:
$$\tau_{eE}(t,h):=y(t+h)-\big[y(t)+hf(t,y(t))\big],\qquad |\tau_{eE}(t,h)|\le\tfrac12h^2\|y''\|_\infty\quad\text{[S4 (9.4)]}.$$

**Convergence** [S4 Thm 9.2]. The derivation is the model for every one-step
method, so know the three steps:

1. *Error recursion.* With $e_i=y(t_i)-y_i$ and the mean value theorem,
   $$e_{i+1}=e_i+h[f(t_i,y(t_i))-f(t_i,y_i)]+\tau(t_i,h),\qquad |e_{i+1}|\le(1+hL)|e_i|+|\tau|\le e^{hL}|e_i|+|\tau|,$$
   where $L$ bounds $\|\nabla f\|$.
2. *Iterate.* With $e_0=0$, $|e_i|\le\sum_{j=0}^{i-1}e^{jhL}|\tau(t_{i-j-1},h)|$.
3. *Sum.* Using $jh=t_j\le T$ and (9.4),
   $|e_i|\le\tfrac12e^{TL}\|y''\|_\infty\,ih^2\le\tfrac12e^{TL}\|y''\|_\infty\,Th$.

So for $f\in C^1$ with $|\nabla f|\le L$,
$$\max_i|y(t_i)-y_i|\le Ce^{LT}h\qquad\text{(first-order convergence).}$$
**One order is lost** from consistency ($h^2$) to convergence ($h$), because
there are $N\sim1/h$ steps. The $e^{LT}$ is sharp for unstable problems and
pessimistic for stable ones.

## 2. Implicit Euler [S4 §9.2]

Expand around $t_{i+1}$ instead:
$$y_{i+1}=y_i+h_if(t_{i+1},y_{i+1})\qquad\text{[S4 (9.5)]}.$$
Each step is a (generally nonlinear) equation in $y_{i+1}$, solved by Newton on
$G(y)=y-y_i-hf(t_{i+1},y)$ with $G'=I-h\,\partial_yf$ [S4 Exercise 9.3]: note
[08](08-nonlinear-equations-and-newton.md). Same consistency order 1.

## 3. Runge–Kutta methods [S4 §9.3]

**Explicit RK** [S4 Def. 9.4]: given stages $s$, $c_i\in[0,1]$, $b_i$, $a_{ij}$,
$$k_i=f\Big(t_0+c_ih,\ y_0+h\sum_{j<i}a_{ij}k_j\Big),\qquad y_1=y_0+h\sum_{i=1}^sb_ik_i,$$
recorded in a **Butcher tableau** (strictly lower triangular $A$):

$$\begin{array}{c|cccc}0&&&&\\ c_2&a_{21}&&&\\ \vdots&\vdots&\ddots&&\\ c_s&a_{s1}&\cdots&a_{s,s-1}&\\\hline &b_1&b_2&\cdots&b_s\end{array}$$

Explicit Euler is $s=1$, $b_1=1$; **Heun** (the order-2 method [S4] derives by
extrapolation, (9.8)) is $c_2=1$, $a_{21}=1$, $b=(\tfrac12,\tfrac12)$
[S4 Exercise 9.5].

**RK4** [S4 Ex. 9.6], order 4 with 4 stages:
$$k_1=f(t_0,y_0),\quad k_2=f\big(t_0+\tfrac h2,y_0+\tfrac h2k_1\big),\quad k_3=f\big(t_0+\tfrac h2,y_0+\tfrac h2k_2\big),\quad k_4=f(t_0+h,y_0+hk_3),$$
$$y_1=y_0+\tfrac h6\big[k_1+2k_2+2k_3+k_4\big],\qquad
\begin{array}{c|cccc}0&&&&\\ \tfrac12&\tfrac12&&&\\ \tfrac12&0&\tfrac12&&\\ 1&0&0&1&\\\hline&\tfrac16&\tfrac26&\tfrac26&\tfrac16\end{array}$$
Applied to $y'=f(t)$ (no $y$ on the right), RK4 **is Simpson's rule**
[S4 Exercise 9.8]: a good sanity check and a nice exam answer.

**Implicit RK** [S4 Def. 9.9]: allow a full $A$, so the stages solve a coupled
nonlinear system
$$k_i=f\Big(t_0+c_ih,\ y_0+h\sum_{j=1}^sa_{ij}k_j\Big),\qquad i=1..s .$$
Implicit Euler is the 1-stage tableau $\begin{array}{c|c}1&1\\\hline&1\end{array}$
[S4 Exercise 9.10].

**The $\theta$-scheme** [S4 Ex. 9.11]:
$\begin{array}{c|c}\theta&\theta\\\hline&1\end{array}$, i.e.
$$y_1=y_0+hf\big(t_0+\theta h,\ \theta y_1+(1-\theta)y_0\big).$$
$\theta=0$ explicit Euler, $\theta=1$ implicit Euler, $\theta=\tfrac12$ the
**implicit midpoint rule** (the simplest Gauss method). Order 1 for
$\theta\ne\tfrac12$ and **order 2** for $\theta=\tfrac12$.

## 4. Why implicit methods [S4 §9.3.3]

Explicit methods are preferred (no nonlinear solve, no $\partial_yf$) except
for **stiff** problems with widely differing time scales, where an explicit
method needs a tiny step long after the fast transients have died.

**The example to know** [S4 Ex. 9.12]:
$$y'=Ay,\quad y(0)=(1,0,-1)^\top,\quad A=\begin{pmatrix}-21&19&-20\\19&-21&20\\40&-40&-40\end{pmatrix},$$
with $\lambda_1=-2$, $\lambda_{2,3}=-40(1\pm i)$ and the exact solution
$$y_1=\tfrac12e^{-2t}+\tfrac12e^{-40t}(\cos40t+\sin40t),\quad
y_2=\tfrac12e^{-2t}-\tfrac12e^{-40t}(\cos40t+\sin40t),\quad
y_3=-e^{-40t}(\cos40t-\sin40t).$$
All components move fast for $t\le0.1$; afterwards $y_1,y_2$ vary slowly and
$y_3\approx0$, so accuracy would permit large steps. But explicit Euler needs
$|1+h\lambda|\le1$ for every eigenvalue, i.e. $h\le\tfrac1{40}=0.025$
**forever**; at $h=0.05$ the result is unusable. Implicit Euler has no such
restriction.

## 5. A-stability [S4 §9.3.4]

Apply the method to the scalar **test equation**
$$y'=\lambda y,\ y(0)=y_0,\qquad \lambda\in\mathbb C,\qquad y(t)=e^{\lambda t}y_0\qquad\text{[S4 (9.9)]}.$$
One step gives $y_1=R(\lambda h)y_0$ [S4 (9.10)] with the **stability function**
$R$: a polynomial for explicit methods, a rational function for implicit ones
[S4 Exercise 9.13]:

| method | $R(z)$ | $\{|R|\le1\}$ |
|---|---|---|
| explicit Euler | $1+z$ | disc $|1+z|\le1$; real interval $[-2,0]$ |
| implicit Euler | $\dfrac1{1-z}$ | exterior of $|1-z|\le1$ $\supset$ left half-plane |
| $\theta$-scheme, $\theta=\tfrac12$ | $\dfrac{1+z/2}{1-z/2}$ | exactly the left half-plane |
| RK4 | $1+z+\tfrac{z^2}{2!}+\tfrac{z^3}{3!}+\tfrac{z^4}{4!}$ | real interval $[-2.785,0]$, reaching $\pm2.83i$ |

Every convergent RK method has $R(z)=1+z+O(|z|^2)$ as $z\to0$ [S4 §9.3.4].

**Definition** [S4 Def. 9.14]. An RK method is **A-stable** if
$$|R(z)|\le1\qquad\text{for all }z\text{ with }\mathrm{Re}\,z\le0 .$$

**No explicit RK method is A-stable** [S4 Exercise 9.15]: $R$ is a polynomial,
hence unbounded as $z\to-\infty$. The meaning [S4 §9.3.4]: for
$\mathrm{Re}\,\lambda\le0$ the exact solution stays bounded, and
$y_i=R(\lambda h)^iy_0$ stays bounded **for every $h>0$** exactly when the method
is A-stable. For explicit Euler with $\lambda<0$,
$$|R(\lambda h)|\le1\iff h\le\frac2{|\lambda|}\qquad\text{[S4 Ex. 9.16]},$$
crippling when $\lambda\ll-1$.

**Systems** [S4 §9.3.4, (9.11)]. For $y'=Ay$ with $A=T^{-1}DT$ diagonalisable,
the change of variables $\hat y=Ty$ decouples the system into scalar test
equations, and one step of an RK method commutes with that change of variables.
So the relevant $z$ are $h\lambda_k$ for **every** eigenvalue of $A$; for a
nonlinear $f$, use the eigenvalues of the Jacobian (linearised stability).

*(Background [S19], not in [S4]: **L-stability** additionally requires
$R(z)\to0$ as $z\to-\infty$: implicit Euler yes, so fast modes are damped; the
trapezoid/midpoint rule no, $R\to-1$, so fast modes oscillate without decaying.
And **embedded pairs** (Fehlberg RKF45, Dormand–Prince DP5(4), the `ode45` and
`solve_ivp` defaults) estimate the local error from two solutions of orders $p$
and $p+1$ sharing the stages, and set
$h_{\mathrm{new}}=h\min(5,\max(0.2,0.9\,\mathrm{err}^{-1/5}))$. `ode.rk45`
implements DP5(4) with FSAL; it is **not** part of this course.)*

## 6. Boundary value problems: shooting [S4 §9.4]

$$y''(t)=f(t,y,y')\ \text{on }(0,T),\qquad y(0)=y_0,\quad y(T)=y_T .$$
Unlike an IVP, a BVP need not be uniquely solvable [S4 Ex. 9.17]: $y''=-y$ with
$y(0)=0$, $y(\pi/2)=1$ has the unique solution $\sin t$; with $y(0)=y(\pi)=0$ it
has the family $c\sin t$; with $y(0)=0$, $y(\pi)=1$ it has **none**.

Assume a unique solution. Reduce to first order with $u=y'$ and guess the
missing initial slope:
$$\begin{pmatrix}y\\u\end{pmatrix}'=\begin{pmatrix}u\\f(t,y,u)\end{pmatrix},\qquad \begin{pmatrix}y(0)\\u(0)\end{pmatrix}=\begin{pmatrix}y_0\\s_0\end{pmatrix}\qquad\text{[S4 (9.13)]}.$$
For each $s_0$ this IVP has a unique solution $y(t;s_0)$, and the second boundary
condition becomes a scalar **nonlinear equation**
$$y(T;s_0)=y_T,$$
solved by Newton (note [08](08-nonlinear-equations-and-newton.md)). Newton needs
$\partial_{s_0}y(T;s_0)$, and differentiating the ODE with respect to $s_0$ shows
that $v(t):=\partial_{s_0}y(t;s_0)$ solves the **linear variational equation**
$$v''=\partial_yf\big(t,y,y'\big)\,v+\partial_{y'}f\big(t,y,y'\big)\,v',\qquad v(0)=0,\ v'(0)=1\qquad\text{[S4 (9.14)]},$$
which any IVP solver handles. [S4 Alg. 30]:

```
repeat:
    solve (9.13) numerically with s0 = s0^(l)          -> y(T; s0)
    solve (9.14) numerically with s0 = s0^(l)          -> dy/ds0 (T; s0)
    s0^(l+1) := s0^(l) - (dy/ds0(T;s0))^{-1} (y(T;s0) - y_T)
```

**Advantage**: only a standard IVP solver is needed.
**Disadvantage** [S4 §9.4]: extreme sensitivity to $s$, because
$$|y(T;s)-y(T;s+\varepsilon)|\le Ce^{LT}\varepsilon,$$
and for $L=T=10$ that amplification is $e^{100}\approx2.7\cdot10^{43}$. The
alternatives are finite differences and finite elements (other lectures).

Example [S4 Ex. 9.18]: $y''=-y$, $y(0)=0$, $y(\pi/2)=1$, exact $y=\sin t$. Here
$y(t;s_0)=s_0\sin t$ and the variational problem $v''=-v$, $v(0)=0$, $v'(0)=1$
has $v=\sin t$: indeed $v=\partial_{s_0}y$. One Newton step from
$s_0^{(0)}=0$:
$$s_0^{(1)}=0-\frac1{\sin(\pi/2)}(0-1)=1,$$
the exact value, because $y(T;s_0)$ is linear in $s_0$ and Newton is exact on
linear problems.

## 7. Worked convergence check

$y'=-2ty$, $y(0)=1$, exact $y=e^{-t^2}$; error at $t=2$ (`ode.py` `__main__`):

| $N$ | Euler | Heun | RK4 | implicit Euler |
|---|---|---|---|---|
| 10 | $1.3\cdot10^{-2}$ | $6.9\cdot10^{-3}$ | $1.4\cdot10^{-4}$ | $1.1\cdot10^{-2}$ |
| 20 | $6.3\cdot10^{-3}$ | $1.3\cdot10^{-3}$ | $6.8\cdot10^{-6}$ | $5.9\cdot10^{-3}$ |
| 40 | $3.1\cdot10^{-3}$ | $2.8\cdot10^{-4}$ | $3.7\cdot10^{-7}$ | $3.0\cdot10^{-3}$ |
| 80 | $1.5\cdot10^{-3}$ | $6.5\cdot10^{-5}$ | $2.2\cdot10^{-8}$ | $1.5\cdot10^{-3}$ |

Halving $h$ divides the error by 2, 4, 16: orders 1, 2, 4. Euler by hand,
$h=0.2$: $y_1=1+0.2\cdot0=1$, $y_2=1+0.2(-2\cdot0.2\cdot1)=0.92$,
$y_3=0.92-0.2\cdot0.8\cdot0.92=0.7728$ (exact $e^{-0.36}=0.6977$).

## Pitfalls

- Confusing consistency order with convergence order. Consistency $O(h^{p+1})$
  per step gives convergence $O(h^p)$, because there are $1/h$ steps
  [S4 §9.1].
- Calling a problem unstable when the *method* is unstable for that $h$: check
  $h\lambda$ against $\{|R|\le1\}$ first.
- Using an explicit method on a stiff problem [S4 Ex. 9.12]. The tell-tale sign
  is a step size pinned at the stability limit long after the solution has gone
  smooth.
- Expecting any explicit RK method to be A-stable [S4 Exercise 9.15].
- Forgetting that implicit Euler damps *everything*, physical oscillations
  included; the $\theta=\tfrac12$ scheme preserves them but does not damp fast
  modes.
- Shooting on a long interval or a large Lipschitz constant: $e^{LT}$
  [S4 §9.4].
- Assuming a BVP has a solution [S4 Ex. 9.17].
- Reading $R(z)$ off the wrong tableau: for implicit methods $R$ is *rational*.

## Exam-style questions

CSE-only chapter, so no past paper covers it; these are ours, written against
[S4] §9.

1. *Define the consistency error of explicit Euler, bound it, and derive the
   convergence order.*
   $\tau_{eE}(t,h)=y(t+h)-[y(t)+hf(t,y(t))]$, $|\tau|\le\tfrac12h^2\|y''\|_\infty$
   [S4 (9.3)–(9.4)]. The error recursion $|e_{i+1}|\le e^{hL}|e_i|+|\tau|$,
   iterated with $e_0=0$ and summed with $ih\le T$, gives
   $\max_i|e_i|\le\tfrac12e^{LT}\|y''\|_\infty Th=O(h)$ [S4 Thm 9.2].
2. *Write the Butcher tableau of explicit Euler, of the order-2 method of
   [S4 (9.8)], and of RK4.*
   $\begin{array}{c|c}0&\\\hline&1\end{array}$;
   $\begin{array}{c|cc}0&&\\1&1&\\\hline&\tfrac12&\tfrac12\end{array}$; the RK4
   tableau in §3 [S4 Exercise 9.5, Ex. 9.6].
3. *Which quadrature rule does RK4 reduce to for $f(t,y)=f(t)$?*
   Simpson's rule: $y_1-y_0=\tfrac h6(k_1+2k_2+2k_3+k_4)$ with
   $k_1=f(t_0)$, $k_2=k_3=f(t_0+\tfrac h2)$, $k_4=f(t_0+h)$, i.e.
   $\tfrac h6\big[f(t_0)+4f(t_0+\tfrac h2)+f(t_0+h)\big]$ [S4 Exercise 9.8].
4. *Define A-stability and prove no explicit RK method has it.*
   $|R(z)|\le1$ for all $\mathrm{Re}\,z\le0$ [S4 Def. 9.14]. For an explicit
   method $R$ is a polynomial, so $|R(z)|\to\infty$ as $z\to-\infty$ along the
   real axis [S4 Exercise 9.15].
5. *Give $R(z)$ for explicit Euler, implicit Euler and the $\theta=\tfrac12$
   scheme, and the largest stable $h$ for explicit Euler on
   $y'=-1000y$.*
   $1+z$, $\tfrac1{1-z}$, $\tfrac{1+z/2}{1-z/2}$ [S4 Exercise 9.13].
   $|1+h\lambda|\le1\iff h\le2/|\lambda|=0.002$ [S4 Ex. 9.16].
6. *Why do implicit methods win on [S4 Ex. 9.12] although both Euler methods are
   first order?*
   The eigenvalues are $-2$ and $-40(1\pm i)$; explicit Euler needs
   $h\le1/40$ for all $t$, even once the fast modes have decayed, while implicit
   Euler is A-stable and can take $h$ dictated by accuracy alone. Accuracy is not
   the issue; **stability** is.
7. *Derive the shooting method and the equation for $\partial_{s_0}y(T;s_0)$.
   What is its weakness?*
   Reduce to first order, guess $u(0)=s_0$, solve $y(T;s_0)=y_T$ by Newton
   [S4 (9.13)]; the derivative solves the linear variational IVP
   $v''=\partial_yf\,v+\partial_{y'}f\,v'$, $v(0)=0$, $v'(0)=1$ [S4 (9.14)].
   Weakness: $|y(T;s)-y(T;s+\varepsilon)|\le Ce^{LT}\varepsilon$: for $L=T=10$
   an amplification of $e^{100}$ [S4 §9.4].
8. *Do one shooting step for $y''=-y$, $y(0)=0$, $y(\pi/2)=1$ from
   $s_0^{(0)}=0$.*
   $y(t;s_0)=s_0\sin t$, $v=\sin t$, so
   $s_0^{(1)}=0-\tfrac{0-1}{\sin(\pi/2)}=1$: exact after one step because
   $y(T;\cdot)$ is linear [S4 Ex. 9.18].

## Implementation

`src/py/ode.py`: `euler`, `implicit_euler` (Newton, analytic or FD Jacobian),
`heun`, `rk4_step` / `rk4`, `stability_function`, `real_stability_interval`,
`rk45` (Dormand–Prince 5(4) with FSAL: **[S19], beyond [S4]**).

`src/py/irk.py` (new): `butcher_explicit_euler` / `_heun` / `_rk4`
([S4 Exercise 9.5, Ex. 9.6]), `theta_scheme` ([S4 Ex. 9.11]), `implicit_rk`
(general implicit tableau, [S4 Def. 9.9], Newton on the coupled stages),
`stability_function_rational` ($R(z)=1+zb^\top(I-zA)^{-1}\mathbf 1$),
`is_a_stable` ([S4 Def. 9.14], sampled on the imaginary axis and the left
half-plane), `lambert_system` ([S4 Ex. 9.12], matrix + exact solution).

`src/py/bvp.py` (new): `shooting` ([S4 Alg. 30]),
`variational_rhs` ([S4 (9.14)]), `shooting_sensitivity` (the $e^{LT}$ bound).

Tests: `test_ode.py` (measured orders 1/1/2/4; `scipy.integrate.solve_ivp`
(DOP853) on Van der Pol; stability intervals $-2,-2,-2.785$; A-stability of
implicit Euler and the trapezoid; the stiff $6^{-10}$ value), `test_irk.py`
(the $\theta$-scheme order 1 for $\theta\ne\tfrac12$ and **2 for
$\theta=\tfrac12$** [S4 Ex. 9.11]; $R(z)$ for all four methods matching
[S4 Exercise 9.13]; `is_a_stable` true for implicit Euler and the midpoint rule,
false for explicit Euler and RK4 [S4 Exercise 9.15]; RK4 reproducing Simpson's
rule on $f(t,y)=f(t)$ [S4 Exercise 9.8]; **explicit Euler on [S4 Ex. 9.12]
blowing up at $h=0.05$ and behaving at $h=0.02$, implicit Euler stable at both**)
and `test_bvp.py` (the three BVPs of [S4 Ex. 9.17]: unique, non-unique,
unsolvable; **one Newton step giving $s_0=1$ exactly** on [S4 Ex. 9.18]; and a
nonlinear BVP against a fine finite-difference reference).

`src/cpp/rk4.cpp`: RK4 (observed order 4, oscillator energy, blow-up
$=R(-5)^{20}$ at $z=-5$) and adaptive Dormand–Prince RK45 on Van der Pol
$\mu=5$ against a fixed-step reference.
