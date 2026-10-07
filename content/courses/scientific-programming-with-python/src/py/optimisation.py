"""Optimisation (note 07).

scipy.optimize: minimize with several methods, bounds and constraints,
least_squares, root, linprog.  PuLP 4: an LP and an ILP (production planning
and knapsack) modelled in PuLP and solved by whatever solver PuLP finds, or,
since PuLP 4 ships none, by SciPy's HiGHS through ``solve_pulp``.
"""
from __future__ import annotations

import numpy as np
from scipy import optimize

try:
    import pulp
except ImportError:                       # pragma: no cover
    pulp = None


# ---------------------------------------------------------------- unconstrained
def himmelblau(p):
    x, y = p
    return (x**2 + y - 11) ** 2 + (x + y**2 - 7) ** 2


def himmelblau_grad(p):
    x, y = p
    u, v = x**2 + y - 11, x + y**2 - 7
    return np.array([4 * x * u + 2 * v, 2 * u + 4 * y * v])


HIMMELBLAU_MINIMA = np.array([[3.0, 2.0], [-2.805118, 3.131312],
                              [-3.779310, -3.283186], [3.584428, -1.848126]])


def minimise_all_methods(x0=(0.0, 0.0)) -> dict[str, optimize.OptimizeResult]:
    """Same problem, different algorithms.  Nelder-Mead: derivative-free
    simplex; CG/BFGS: gradient (BFGS builds an inverse-Hessian estimate);
    Newton-CG/trust-* want a Hessian (or Hessian-vector products)."""
    out = {}
    for m in ["Nelder-Mead", "Powell", "CG", "BFGS", "L-BFGS-B", "Newton-CG"]:
        jac = himmelblau_grad if m not in ("Nelder-Mead", "Powell") else None
        kw = {"hess": lambda p: optimize.approx_fprime(p, himmelblau_grad)} if m == "Newton-CG" else {}
        out[m] = optimize.minimize(himmelblau, x0, method=m, jac=jac, **kw)
    return out


# ---------------------------------------------------------------- constrained
def constrained_demo():
    """min (x-2)^2 + (y-1)^2  s.t.  x + y <= 2 (linear),  x^2 + y^2 <= 4
    (nonlinear), 0 <= x, y <= 1.5.  SLSQP takes dict constraints; trust-constr
    takes LinearConstraint / NonlinearConstraint objects."""
    f = lambda p: (p[0] - 2) ** 2 + (p[1] - 1) ** 2
    bounds = [(0, 1.5), (0, 1.5)]
    cons = [{"type": "ineq", "fun": lambda p: 2 - p[0] - p[1]},          # g(x) >= 0 form
            {"type": "ineq", "fun": lambda p: 4 - p[0] ** 2 - p[1] ** 2}]
    slsqp = optimize.minimize(f, [0.5, 0.5], method="SLSQP", bounds=bounds, constraints=cons)
    lin = optimize.LinearConstraint([[1, 1]], -np.inf, 2)
    nl = optimize.NonlinearConstraint(lambda p: p[0] ** 2 + p[1] ** 2, -np.inf, 4)
    tc = optimize.minimize(f, [0.5, 0.5], method="trust-constr", bounds=bounds,
                           constraints=[lin, nl], options={"gtol": 1e-12, "xtol": 1e-12, "barrier_tol": 1e-12})
    return slsqp, tc


# ---------------------------------------------------------------- least squares
def fit_decay_with_outliers(rng: np.random.Generator):
    """least_squares takes the RESIDUAL vector (not its sum of squares) so
    it can exploit the Jacobian structure (Gauss-Newton / LM / trust region
    reflective with bounds).  loss='soft_l1' makes it robust to outliers.
    (A sum of two exponentials would be a classic ill-conditioned fit:
    nearly interchangeable rates; keep it to one decay here.)"""
    t = np.linspace(0, 4, 80)
    true = np.array([2.0, 1.5, 0.5])
    model = lambda p, t: p[0] * np.exp(-p[1] * t) + p[2]
    y = model(true, t) + 0.02 * rng.standard_normal(t.size)
    y[::10] += 1.0                                        # outliers
    resid = lambda p: model(p, t) - y
    plain = optimize.least_squares(resid, x0=[1, 1, 0], bounds=(0, np.inf))
    # f_scale = residual size above which a point counts as an outlier
    robust = optimize.least_squares(resid, x0=[1, 1, 0], bounds=(0, np.inf),
                                    loss="soft_l1", f_scale=0.1)
    return plain, robust, true


# ---------------------------------------------------------------- root finding
def root_system():
    """Nonlinear system: x^2 + y^2 = 4, e^x + y = 1.  root() with 'hybr'
    (MINPACK Powell hybrid); providing jac speeds it up."""
    def F(p):
        x, y = p
        return [x**2 + y**2 - 4, np.exp(x) + y - 1]

    def J(p):
        x, y = p
        return [[2 * x, 2 * y], [np.exp(x), 1.0]]
    return optimize.root(F, [1.0, -1.0], jac=J, method="hybr")


# ---------------------------------------------------------------- linprog
def diet_linprog():
    """min cost c.x  s.t.  A_ub x <= b_ub, A_eq x = b_eq, bounds.
    Two foods (cost 2, 3), need >= 10 protein and >= 8 fibre:
    protein 3x1 + 1x2 >= 10, fibre 1x1 + 2x2 >= 8 (multiply by -1 for <=)."""
    c = [2, 3]
    A_ub = [[-3, -1], [-1, -2]]
    b_ub = [-10, -8]
    return optimize.linprog(c, A_ub=A_ub, b_ub=b_ub, bounds=[(0, None)] * 2, method="highs")


# ---------------------------------------------------------------- PuLP
#
# PuLP 4.0 removed what 3.3 deprecated (note 07 §7): LpVariable(name, ...),
# prob.constraints as a dict, PULP_CBC_CMD, LpStatus/prob.status, and the
# bundled CBC binary.  PuLP is now a modeller only; CBC comes from
# `pulp[cbc]` (the cbcbox wheel) or a `cbc` on PATH.  This venv has neither:
# pulp.listSolvers(onlyAvailable=True) == [].  So solve_pulp() uses a PuLP
# solver when one exists and otherwise reads the model back out as matrices
# and hands it to SciPy's HiGHS: linprog for an LP (with duals), milp for a MIP.
SCIPY_BACKEND = "scipy-HiGHS"
_STATUS = {0: "Optimal", 2: "Infeasible", 3: "Unbounded"}   # linprog == milp codes


def pulp_solver():
    """First solver PuLP itself can run on this machine, or None."""
    names = pulp.listSolvers(onlyAvailable=True) if pulp is not None else []
    return pulp.getSolver(names[0], msg=False) if names else None


def pulp_to_matrices(prob):
    """PuLP model -> (variables, c, A, sense, rhs, bounds, integrality).

    A PuLP 4 constraint stores a.x + k (sense) 0, so rhs = -k; sense is
    -1 (<=), 0 (==), +1 (>=), the pulp.LpConstraint* constants."""
    vs = prob.variables()
    col = {v.name: j for j, v in enumerate(vs)}
    c = np.zeros(len(vs))
    for v, a in prob.objective.items():
        c[col[v.name]] = a
    cons = prob.constraints()
    A = np.zeros((len(cons), len(vs)))
    for i, con in enumerate(cons):
        for v, a in con.items():
            A[i, col[v.name]] = a
    sense = np.array([con.sense for con in cons])
    rhs = np.array([-con.constant for con in cons])
    finite = lambda b: b if np.isfinite(b) else None
    bounds = [(finite(v.lowBound), finite(v.upBound)) for v in vs]
    integrality = np.array([v.isInteger() for v in vs], dtype=int)
    return vs, c, A, sense, rhs, bounds, integrality


def solve_pulp(prob) -> tuple[str, str]:
    """Solve a PuLP model; values (and LP duals) land in the model as a
    PuLP solver would put them.  Returns (status, backend)."""
    solver = pulp_solver()
    if solver is not None:
        stats = prob.solve(solver)
        return stats.status_str, stats.solver
    prob.checkDuplicateVars()                # columns are keyed by name, as in an MPS file
    vs, c, A, sense, rhs, bounds, integ = pulp_to_matrices(prob)
    sign = prob.sense                        # LpMinimize = 1, LpMaximize = -1
    if integ.any():                          # branch-and-cut in HiGHS
        lo = np.where(sense >= 0, rhs, -np.inf)
        hi = np.where(sense <= 0, rhs, np.inf)
        lb, ub = zip(*[(-np.inf if l is None else l, np.inf if u is None else u) for l, u in bounds])
        r = optimize.milp(sign * c, constraints=optimize.LinearConstraint(A, lo, hi),
                          integrality=integ, bounds=optimize.Bounds(lb, ub))
    else:                                    # >= rows are negated into <= rows
        ub_rows, eq = sense != 0, sense == 0
        flip = np.where(sense > 0, -1.0, 1.0)[:, None]
        r = optimize.linprog(sign * c, A_ub=(flip * A)[ub_rows] if ub_rows.any() else None,
                             b_ub=(flip[:, 0] * rhs)[ub_rows] if ub_rows.any() else None,
                             A_eq=A[eq] if eq.any() else None, b_eq=rhs[eq] if eq.any() else None,
                             bounds=bounds, method="highs")
    status = _STATUS.get(r.status, "Undefined")
    if r.x is not None:
        prob.assignVarsVals({v.name: float(x) for v, x in zip(vs, r.x)})
    if not integ.any() and status == "Optimal":
        # marginal = d(min sign*c.x)/d(b); PuLP's pi = d(objective)/d(rhs)
        names = [con.name for con in prob.constraints()]
        pi = dict(zip([n for n, u in zip(names, ub_rows) if u],
                      sign * flip[ub_rows, 0] * r.ineqlin.marginals))
        pi.update(zip([n for n, e in zip(names, eq) if e], sign * r.eqlin.marginals))
        prob.assignConsPi(pi)
    return status, SCIPY_BACKEND


def production_plan_lp():
    """LP: products P1 (profit 40), P2 (profit 30); machine hours
    2 P1 + 1 P2 <= 100, labour 1 P1 + 1 P2 <= 80, demand P1 <= 40.
    Relaxed (continuous) optimum sits at a vertex of the polytope:
    (P1, P2) = (20, 60), profit 2600, duals 10 (machine) and 20 (labour)."""
    prob = pulp.LpProblem("production", pulp.LpMaximize)
    p1 = prob.add_variable("P1", lowBound=0)
    p2 = prob.add_variable("P2", lowBound=0)
    prob += 40 * p1 + 30 * p2, "profit"
    prob += 2 * p1 + p2 <= 100, "machine"
    prob += p1 + p2 <= 80, "labour"
    prob += p1 <= 40, "demand"
    status, backend = solve_pulp(prob)
    names = ("machine", "labour", "demand")
    return {"status": status, "backend": backend, "P1": p1.value(), "P2": p2.value(),
            "profit": pulp.value(prob.objective),
            "duals": {n: prob.get_constraint_by_name(n).pi for n in names}}


def workshop_lp():
    """Note 11, problem 11, both ways.  max 40 P1 + 50 P2 s.t. machine
    2 P1 + P2 <= 100, labour P1 + 3 P2 <= 200.  linprog minimises, so the
    objective is negated; PuLP says LpMaximize.  Optimum (20, 60), 3800."""
    lp = optimize.linprog([-40, -50], A_ub=[[2, 1], [1, 3]], b_ub=[100, 200],
                          bounds=[(0, None)] * 2, method="highs")
    prob = pulp.LpProblem("workshop", pulp.LpMaximize)
    p1, p2 = prob.add_variable("P1", lowBound=0), prob.add_variable("P2", lowBound=0)
    prob += 40 * p1 + 50 * p2
    prob += 2 * p1 + p2 <= 100, "machine"
    prob += p1 + 3 * p2 <= 200, "labour"
    status, _ = solve_pulp(prob)
    return {"linprog": (lp.x.tolist(), -lp.fun),
            "pulp": (status, [p1.value(), p2.value()], pulp.value(prob.objective))}


def knapsack_ilp(weights, values, capacity):
    """0/1 knapsack: binary variables, branch-and-bound (CBC or HiGHS).  The
    LP relaxation would take a fractional item; integrality makes it NP-hard."""
    n = len(weights)
    prob = pulp.LpProblem("knapsack", pulp.LpMaximize)
    x = [prob.add_variable(f"x{i}", cat="Binary") for i in range(n)]
    prob += pulp.lpSum(v * xi for v, xi in zip(values, x))
    prob += pulp.lpSum(w * xi for w, xi in zip(weights, x)) <= capacity, "capacity"
    solve_pulp(prob)
    chosen = [i for i in range(n) if x[i].value() > 0.5]
    return chosen, pulp.value(prob.objective)


def knapsack_bruteforce(weights, values, capacity):
    best, best_set = 0, []
    for mask in range(1 << len(weights)):
        items = [i for i in range(len(weights)) if mask >> i & 1]
        w = sum(weights[i] for i in items)
        v = sum(values[i] for i in items)
        if w <= capacity and v > best:
            best, best_set = v, items
    return best_set, best


if __name__ == "__main__":
    for m, r in minimise_all_methods().items():
        print(f"{m:12s} x={np.round(r.x, 4)} f={r.fun:.2e} nfev={r.nfev}")
    s, t = constrained_demo(); print("SLSQP:", s.x, " trust-constr:", t.x)
    p, r, true = fit_decay_with_outliers(np.random.default_rng(0))
    print("least_squares plain:", np.round(p.x, 3), " robust:", np.round(r.x, 3), " true:", true)
    print("root:", root_system().x)
    lp = diet_linprog(); print("linprog:", lp.x, lp.fun)
    if pulp is None:
        print("PuLP not installed: skipping PuLP demos")
    else:
        print("PuLP", pulp.__version__, "solver:", pulp_solver() or SCIPY_BACKEND)
        print("PuLP LP:", production_plan_lp())
        print("workshop (note 11, problem 11):", workshop_lp())
        print("PuLP ILP:", knapsack_ilp([12, 7, 11, 8, 9], [24, 13, 23, 15, 16], 26))
