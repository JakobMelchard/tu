# 07 Solving optimisation problems: scipy.optimize and PuLP

Code: [`../src/py/optimisation.py`](../src/py/optimisation.py), tests in `test_optimisation.py` (PuLP tests run on SciPy's HiGHS when PuLP has no solver of its own; they skip only if PuLP is not installed).

Sources: `scipy.optimize` 1.18 [S15], the PuLP documentation [S23], HiGHS [S24],
COIN-OR CBC [S25]. **Verified against SciPy 1.18.1 and PuLP 4.0.0** [S40] on
2026-09-27 (PuLP was 3.3.2 on 2026-09-22). PuLP 4.0 removed the API that 3.3
deprecated and no longer bundles a solver; see the box in §7. The worked LP's
numbers were re-solved in the venv.

This note carries one of the five TISS learning outcomes on its own: *"to
formulate and to solve various optimization problems"* [S1], and the subject
list names SciPy and PuLP as the tools.

## 1. The landscape

$$\min_{x \in \mathbb{R}^n} f(x) \quad \text{s.t.} \quad g_i(x) \ge 0,\; h_j(x) = 0,\; l \le x \le u.$$

Classify before choosing a tool: **continuous vs integer** variables; **linear vs nonlinear** objective and constraints; **smooth** (gradients available or cheap by finite differences) vs **noisy/black-box**; **convex** (every local minimum is global; LP, QP, least squares) vs **nonconvex** (local methods find *a* stationary point; multistart or global heuristics needed); **size** (a few variables vs millions). `scipy.optimize` covers continuous problems; **PuLP** models linear and (mixed-)integer programs and hands them to an LP/MIP solver (CBC, HiGHS, GLPK, Gurobi, CPLEX, ...; since PuLP 4.0 none ships inside the package).

## 2. `scipy.optimize.minimize` and its methods

`minimize(fun, x0, args=(), method=None, jac=None, hess=None, hessp=None, bounds=None, constraints=(), tol=None, options={"maxiter": ..., "disp": True})` returns an `OptimizeResult` with `x`, `fun`, `success`, `status`, `message`, `nit`, `nfev`, `njev`, `jac`, `hess_inv` (BFGS) [S15]. Always check `res.success` and look at `res.message`.

| Method | Needs | Idea | Use when |
|---|---|---|---|
| `Nelder-Mead` | $f$ only | simplex of $n+1$ points: reflect/expand/contract/shrink | noisy or non-differentiable $f$, few variables, robust but slow ($O(n)$ evaluations per step, no convergence guarantee) |
| `Powell` | $f$ only | conjugate direction line searches | derivative-free, smoother than NM |
| `CG` | $\nabla f$ | nonlinear conjugate gradient | large $n$, little memory |
| `BFGS` | $\nabla f$ | quasi-Newton: builds an inverse-Hessian approximation $H_k$ from gradient differences (secant condition $H_{k+1} y_k = s_k$), line search (Wolfe) | default for smooth unconstrained problems of moderate $n$; superlinear convergence |
| `L-BFGS-B` | $\nabla f$ | limited-memory BFGS (stores $m$ pairs $(s_k, y_k)$), plus box bounds | large $n$, bounds |
| `Newton-CG`, `trust-ncg`, `trust-krylov`, `trust-exact` | $\nabla f$, Hessian or `hessp` | Newton steps via CG on $\nabla^2 f\, p = -\nabla f$ / trust region | Hessian-vector products available, quadratic convergence |
| `TNC` | $\nabla f$ | truncated Newton with bounds | |
| `COBYLA` | $f$ only | linear approximations in a trust region | derivative-free with inequality constraints |
| `SLSQP` | $\nabla f$ | sequential least-squares (quadratic) programming: solve a QP subproblem per step | general equality/inequality constraints, small/medium size (the workhorse) |
| `trust-constr` | $\nabla f$ (+Hessian) | interior-point / trust region with `LinearConstraint`, `NonlinearConstraint` | larger constrained problems, more control |

Without `jac`, gradient methods use finite differences ($n$ extra evaluations per gradient, with $O(\sqrt\varepsilon)$ error); provide an analytic gradient whenever you can and verify it with `optimize.check_grad` (`test_gradient_matches_finite_differences`). `minimise_all_methods` runs six methods on Himmelblau's function (four minima; the one found depends on $x_0$ and the method). Local methods only: for global optimisation use `differential_evolution` (population-based, bounds required), `basinhopping` (random perturbation + local minimise), `shgo`, `dual_annealing`, or multistart.

Scaling matters: variables of wildly different magnitudes ruin finite differences and line searches; rescale to $O(1)$. Tolerances: `tol`/`gtol` relative to gradient norm, `xtol` to step size, `ftol` to function change. `minimize_scalar` (Brent, bounded) for 1D.

## 3. Constraints and bounds

- **Bounds**: `bounds=[(lo, hi), ...]` or `optimize.Bounds(lb, ub)`; `None`/`np.inf` for unbounded. Supported by `L-BFGS-B`, `TNC`, `SLSQP`, `Powell`, `Nelder-Mead`, `trust-constr`, `COBYLA`.
- **SLSQP / COBYLA** take dicts: `{"type": "ineq", "fun": g, "jac": ...}` meaning $g(x) \ge 0$, and `{"type": "eq", "fun": h}` for $h(x) = 0$ [S15]. Write $x + y \le 2$ as `2 - x - y >= 0`. The sign convention is the opposite of `linprog`'s and is a standing source of wrong answers.
- **trust-constr** takes `LinearConstraint(A, lb, ub)` for $lb \le A x \le ub$ and `NonlinearConstraint(c, lb, ub)`, with equality via `lb == ub`.
- At a solution the **KKT conditions** hold: $\nabla f = \sum_i \lambda_i \nabla g_i + \sum_j \mu_j \nabla h_j$ with $\lambda_i \ge 0$, $\lambda_i g_i(x) = 0$ (complementary slackness): a constraint is *active* if it holds with equality and its multiplier is positive. `constrained_demo`: the unconstrained minimum $(2, 1)$ violates $x \le 1.5$ and $x + y \le 2$, so the constrained optimum is the vertex $(1.5, 0.5)$ where both are active; SLSQP lands on it, the interior-point `trust-constr` approaches it from inside up to its tolerances.

## 4. Nonlinear least squares

Fitting a model $m(t; p)$ to data $y$ minimises $\tfrac12 \sum_i r_i(p)^2$, $r_i = m(t_i; p) - y_i$. Give `least_squares(residual, x0, jac=..., bounds=(lb, ub), method="trf"|"lm"|"dogbox", loss="linear"|"soft_l1"|"huber"|"cauchy", f_scale=...)` the **residual vector**, not its sum of squares: the algorithms (Gauss-Newton / Levenberg-Marquardt, trust-region reflective) exploit the structure $\nabla^2 \approx J^T J$ and converge much faster than generic `minimize`. `lm` is MINPACK's Levenberg-Marquardt (no bounds, needs $m \ge n$); `trf` handles bounds. Robust losses $\rho(r^2)$ down-weight residuals larger than `f_scale` so outliers do not dominate (`fit_decay_with_outliers`: plain LS is pulled by the +1 outliers, `soft_l1` with `f_scale=0.1` recovers the parameters). `curve_fit(model, t, y, p0, sigma, absolute_sigma)` wraps this for the `model(t, *params)` signature and returns the covariance $\Sigma = \sigma^2 (J^T J)^{-1}$; standard errors are $\sqrt{\text{diag}\,\Sigma}$. Linear least squares ($y = X\beta$) is `np.linalg.lstsq` / `scipy.linalg.lstsq` (SVD), non-negative LS `optimize.nnls`, bounded linear `lsq_linear`.

## 5. Root finding

`root(F, x0, jac=None, method="hybr"|"lm"|"krylov"|"broyden1"|...)` solves $F(x) = 0$ for systems (`hybr` = MINPACK Powell hybrid, a trust-region Newton with finite-difference Jacobian by default; `krylov` for large sparse Jacobians via Newton-Krylov). `root_system` solves $x^2 + y^2 = 4$, $e^x + y = 1$ with an analytic Jacobian. Scalars: `brentq(f, a, b)` (bracketing, always converges), `bisect`, `newton(f, x0, fprime=..., fprime2=...)` (Newton/secant/Halley; can diverge), `root_scalar` unifying interface, `fixed_point`. Minimising $f$ and solving $\nabla f = 0$ are related but a root finder does not distinguish minima from maxima or saddles.

## 6. Linear programming with `linprog`

$$\min c^T x \quad \text{s.t.} \quad A_{ub} x \le b_{ub},\; A_{eq} x = b_{eq},\; l \le x \le u.$$

`linprog(c, A_ub, b_ub, A_eq, b_eq, bounds, method="highs")`: HiGHS [S24] (dual simplex or interior point) is the default and fast [S15]; the result has `x`, `fun`, `status`, `slack`, `ineqlin.marginals` (dual values). Maximisation: minimise $-c^T x$. "$\ge$" constraints: multiply by $-1$. An LP optimum (if it exists) lies at a **vertex** of the feasible polytope, where $n$ constraints are active; the simplex method walks vertices, interior-point methods cross the interior. `diet_linprog`: minimum-cost mix with two nutrient constraints; both are active at the solution $(2.4, 2.8)$. Integer programs: `optimize.milp(c, constraints=LinearConstraint(...), integrality=[1, 0, ...], bounds)` also uses HiGHS (branch-and-bound).

## 7. PuLP: modelling LPs and ILPs

PuLP is a *modelling* layer [S23]: you write variables, objective and constraints in algebraic Python, PuLP writes an `.lp`/`.mps` file (or calls a solver's Python API) and reads the solution back into the variables. Since 4.0 it is **only** that: the solver is a separate install.

> **PuLP 4.0 removed what 3.3 deprecated, and the bundled CBC with it.** The venv was re-created with `uv sync` on 2026-09-27 and resolved PuLP 4.0.0 (3.3.2 on 2026-09-22) [S40]. Every row below was run in the venv; the installed wheel's README names the headline removals and links the 3.x to 4.0 migration guide [S23]:
>
> | PuLP ≤ 3.3 idiom | under PuLP 4.0.0 | write instead |
> |---|---|---|
> | `pulp.LpVariable("x", lowBound=0)` | `TypeError` | `prob.add_variable("x", lowBound=0)` |
> | `pulp.LpVariable.dicts("x", I, cat="Binary")` | `AttributeError` | `prob.add_variable_dict("x", I, cat="Binary")` |
> | `prob.constraints["machine"]` | `TypeError`: `constraints` is now a method returning a list | `prob.get_constraint_by_name("machine")` |
> | `prob.solve(pulp.PULP_CBC_CMD(msg=False))` | `AttributeError`: gone, with the CBC binary it wrapped | `pulp.COIN_CMD(msg=False)`, CBC from `pip install "pulp[cbc]"` or a `cbc` on `PATH` |
> | `prob.solve(); pulp.LpStatus[prob.status]` | `LpStatus` and `prob.status` are gone | `stats = prob.solve(...)`; `stats.status_str` is `"Optimal"`, `"Infeasible"`, `"Unbounded"`, ... |
>
> In this venv `pulp.listSolvers(onlyAvailable=True)` is `[]`, so a bare `prob.solve()` raises `PulpError: No solver available`. `pulp[cbc]` would fix that, but it is a download and the repo does none at test time. So [`../src/py/optimisation.py`](../src/py/optimisation.py) keeps PuLP as the modeller and `solve_pulp` uses PuLP's own solver when there is one; otherwise it reads the model back out as matrices (`pulp_to_matrices`: $c$, $A$, row sense, $b$, bounds, integrality) and solves it with SciPy's HiGHS [S24], `linprog` for an LP (duals included, converted to PuLP's sign convention) and `milp` for a MIP. The numbers are the same, and it is the point of this section made concrete: the model and the solver are separate things.

```python
import pulp
prob = pulp.LpProblem("production", pulp.LpMaximize)
p1 = prob.add_variable("P1", lowBound=0)                 # continuous >= 0
p2 = prob.add_variable("P2", lowBound=0)                 # cat="Integer" / "Binary" for a MIP
prob += 40 * p1 + 30 * p2, "profit"                      # an expression without sense: the objective
prob += 2 * p1 + p2 <= 100, "machine"                    # a relation: a constraint
prob += p1 + p2 <= 80, "labour"
prob += p1 <= 40, "demand"
stats = prob.solve(pulp.COIN_CMD(msg=False))             # needs CBC; here: solve_pulp(prob)
stats.status_str                  # "Optimal", "Infeasible", "Unbounded", ...
p1.value(), pulp.value(prob.objective)
prob.get_constraint_by_name("machine").pi   # dual value (shadow price), LP only
```

`pulp.lpSum(...)` builds sums in one pass; Python `sum` copies the growing expression at every step (measured on 2026-09-27: 8 000 terms, `sum` 7x slower than `lpSum`, and the ratio grows with $n$). `prob.add_variable_dict("x", index_set, cat="Binary")` creates families; `prob.writeLP("m.lp")` shows the generated model. Solver options on `COIN_CMD`: `timeLimit`, `gapRel`, `threads`.

**Worked LP (`production_plan_lp`).** Maximise $40 P_1 + 30 P_2$ subject to machine $2P_1 + P_2 \le 100$, labour $P_1 + P_2 \le 80$, demand $P_1 \le 40$. Vertices of the feasible region: $(0,0)$, $(40,0)$, $(40,20)$, $(20,60)$, $(0,80)$; profits $0, 1600, 2200, 2600, 2400$; optimum $(20, 60)$ with profit 2600, where machine and labour are active. Duals (shadow prices) are 10 per machine hour and 20 per labour hour: one more machine hour raises the optimal profit by 10 (until the basis changes); the demand constraint is slack, dual 0. All of those numbers were re-solved on 2026-09-27 with PuLP 4.0.0 as modeller and SciPy 1.18.1's HiGHS as solver (`solve_pulp`), and match the 2026-09-22 run with PuLP 3.3.2 and its bundled CBC. The test cross-checks with a hand-written `linprog`. Note 11's problem 11 is the same shape with other numbers: `workshop_lp` solves it both ways, optimum $(20, 60)$, profit 3800.

**Worked ILP (`knapsack_ilp`).** 0/1 knapsack: binary $x_i$, maximise $\sum v_i x_i$ s.t. $\sum w_i x_i \le W$. The LP relaxation ($0 \le x_i \le 1$) takes items in order of $v_i / w_i$ and one fractional item, giving an *upper bound*; the MIP solver's (CBC, or HiGHS here) **branch-and-bound** splits on a fractional variable ($x_i = 0$ or $1$), solves the relaxations, prunes subtrees whose bound cannot beat the incumbent, and adds cutting planes (branch-and-cut). Integer programs are NP-hard in general; the test compares against brute force over $2^5$ subsets. Rounding the LP solution is *not* a valid method (it can be infeasible or far from optimal).

Modelling tricks: big-M constraints to switch constraints with a binary ($g(x) \le M y$); binaries for fixed costs; $|x|$ via $x = x^+ - x^-$; minimax via an auxiliary variable $t \ge f_i(x)$; set covering / assignment / scheduling as standard forms. Keep $M$ tight; check the solve status and infeasibility before reading values.

## Pitfalls

- Not checking `res.success` / `stats.status_str`; reading `res.x` of a failed run.
- Wrong constraint sign convention: SciPy dicts want $g \ge 0$, `linprog` wants $A_{ub} x \le b_{ub}$.
- Passing $\sum r_i^2$ to `least_squares` instead of the residual vector; forgetting `f_scale` with robust losses.
- Finite-difference gradients on noisy or badly scaled functions; not testing analytic gradients with `check_grad`.
- Expecting a local optimiser to find the global minimum of a multimodal function.
- PuLP: using Python `sum` on thousands of terms; reusing variable names (PuLP 4 turns a space into `_` without a word and accepts a duplicate name until `prob.checkDuplicateVars()` or the solve rejects it); reading duals from an ILP (undefined); comparing floats from the solver with `==`; writing the pre-4.0 API (`LpVariable(...)`, `LpStatus`, `PULP_CBC_CMD`) that 4.0 removed, and assuming `prob.solve()` has a solver to call (see the box in §7).

## Exam-style questions

**All five are ours** [S9]; see [`00-exam-focus.md`](00-exam-focus.md). This is
the note whose topic TISS names as a learning outcome, so expect the *formulate*
half — turning a word problem into $\min c^\top x$ with the right signs — as
much as the *solve* half.

1. Which `minimize` method uses no gradient information at all?
   (a) BFGS (b) L-BFGS-B (c) Nelder-Mead (d) Newton-CG
   **c.** Nelder-Mead moves a simplex using function values only.

2. In the SLSQP constraint dict `{"type": "ineq", "fun": g}` the constraint means
   (a) $g(x) \le 0$ (b) $g(x) \ge 0$ (c) $g(x) = 0$ (d) $g(x) > 0$ strictly
   **b.**

3. `least_squares` should be given
   (a) the sum of squared residuals (b) the residual vector $r(p)$ (c) the log-likelihood (d) the gradient only
   **b.** The Gauss-Newton/LM structure ($J^T J$) requires the individual residuals.

4. An optimal solution of a feasible, bounded LP is always found
   (a) in the interior of the feasible region (b) at a vertex of the feasible polytope (c) at the origin (d) where all constraints are slack
   **b.** The objective is linear, so it is extremal at an extreme point (the simplex method searches exactly those).

5. Solving the LP relaxation of an integer program and rounding the result
   (a) always gives the ILP optimum (b) gives a feasible but possibly suboptimal solution (c) may give an infeasible or far-from-optimal point; branch-and-bound is needed (d) is what CBC does internally
   **c.** The relaxation only provides a bound; branch-and-bound explores integer subproblems using that bound to prune.
