"""Tests for optimisation.py (note 07): scipy.optimize and PuLP 4 models,
solved by a PuLP solver if one is installed, else by SciPy's HiGHS."""
import numpy as np
import pytest
from numpy.testing import assert_allclose

import optimisation as op

pulp = pytest.importorskip("pulp")


def test_all_methods_reach_a_himmelblau_minimum():
    for name, r in op.minimise_all_methods().items():
        assert r.success, name
        assert r.fun < 1e-6, name
        assert np.min(np.linalg.norm(op.HIMMELBLAU_MINIMA - r.x, axis=1)) < 1e-3, name


def test_gradient_matches_finite_differences():
    from scipy.optimize import check_grad
    for p in [[0.0, 0.0], [1.0, -2.0], [3.0, 2.0]]:
        assert check_grad(op.himmelblau, op.himmelblau_grad, p) < 1e-5


def test_constrained_solvers_agree():
    s, t = op.constrained_demo()
    assert s.success and t.success
    assert_allclose(s.x, t.x, atol=1e-3)     # interior point stops just inside
    x, y = s.x
    assert x + y <= 2 + 1e-6 and x <= 1.5 + 1e-6      # active: x <= 1.5 and x + y <= 2
    assert_allclose(s.x, [1.5, 0.5], atol=1e-4)


def test_robust_least_squares_beats_plain():
    plain, robust, true = op.fit_decay_with_outliers(np.random.default_rng(0))
    assert np.linalg.norm(robust.x - true) < np.linalg.norm(plain.x - true)
    assert np.linalg.norm(robust.x - true) < 0.1


def test_root_system():
    r = op.root_system()
    assert r.success
    x, y = r.x
    assert abs(x**2 + y**2 - 4) < 1e-10 and abs(np.exp(x) + y - 1) < 1e-10


def test_linprog_vertex():
    r = op.diet_linprog()
    assert r.success
    assert_allclose(r.x, [2.4, 2.8]) and r.fun == pytest.approx(13.2)
    # both constraints active at the optimum (a vertex)
    assert_allclose(np.array([[3, 1], [1, 2]]) @ r.x, [10, 8])


def test_pulp_lp_matches_linprog():
    res = op.production_plan_lp()
    assert res["status"] == "Optimal"
    # cross-check with scipy: maximise -> minimise the negative
    from scipy.optimize import linprog
    lp = linprog([-40, -30], A_ub=[[2, 1], [1, 1], [1, 0]], b_ub=[100, 80, 40], method="highs")
    assert res["profit"] == pytest.approx(-lp.fun)
    assert_allclose([res["P1"], res["P2"]], lp.x, atol=1e-6)
    assert res["duals"]["machine"] == pytest.approx(10.0)    # shadow price of a machine hour


def test_pulp_knapsack_matches_bruteforce():
    w, v, cap = [12, 7, 11, 8, 9], [24, 13, 23, 15, 16], 26
    chosen, value = op.knapsack_ilp(w, v, cap)
    bf_set, bf_value = op.knapsack_bruteforce(w, v, cap)
    assert value == pytest.approx(bf_value) and sorted(chosen) == bf_set
    assert sum(w[i] for i in chosen) <= cap


def test_bridge_handles_ge_eq_and_dual_signs_of_a_minimisation():
    """The diet LP written in PuLP with >= rows: same x as diet_linprog, and
    duals by hand from the dual system 3y1 + y2 = 2, y1 + 2y2 = 3."""
    prob = pulp.LpProblem("diet", pulp.LpMinimize)
    x1, x2 = prob.add_variable("x1", lowBound=0), prob.add_variable("x2", lowBound=0)
    prob += 2 * x1 + 3 * x2
    prob += 3 * x1 + x2 >= 10, "protein"
    prob += x1 + 2 * x2 >= 8, "fibre"
    status, _ = op.solve_pulp(prob)
    assert status == "Optimal"
    assert_allclose([x1.value(), x2.value()], op.diet_linprog().x, atol=1e-9)
    assert prob.get_constraint_by_name("protein").pi == pytest.approx(0.2)
    assert prob.get_constraint_by_name("fibre").pi == pytest.approx(1.4)

    eq = pulp.LpProblem("eq", pulp.LpMinimize)
    y = eq.add_variable("y", lowBound=0)
    eq += 5 * y
    eq += 2 * y == 6, "fix"
    assert op.solve_pulp(eq)[0] == "Optimal" and y.value() == pytest.approx(3.0)
    assert eq.get_constraint_by_name("fix").pi == pytest.approx(2.5)


def test_bridge_reports_infeasible():
    prob = pulp.LpProblem("bad", pulp.LpMinimize)
    x = prob.add_variable("x", lowBound=0)
    prob += x
    prob += x <= -1, "impossible"
    assert op.solve_pulp(prob)[0] == "Infeasible"


def test_bridge_rejects_duplicate_names_like_a_pulp_solver():
    prob = pulp.LpProblem("dup", pulp.LpMinimize)
    x, y = prob.add_variable("x", lowBound=0), prob.add_variable("x", lowBound=0)
    prob += x + y
    with pytest.raises(pulp.PulpError, match="Repeated variable names"):
        op.solve_pulp(prob)


def test_backend_is_pulps_own_solver_when_there_is_one():
    backend = op.production_plan_lp()["backend"]
    native = op.pulp_solver()
    assert backend == (op.SCIPY_BACKEND if native is None else native.name)


def test_workshop_problem_11_both_ways():
    r = op.workshop_lp()
    assert_allclose(r["linprog"][0], [20, 60], atol=1e-9) and r["linprog"][1] == pytest.approx(3800)
    status, x, profit = r["pulp"]
    assert status == "Optimal" and profit == pytest.approx(3800)
    assert_allclose(x, [20, 60], atol=1e-9)
