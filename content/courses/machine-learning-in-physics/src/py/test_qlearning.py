"""Tests for qlearning.py (note 09)."""
import numpy as np

import qlearning as ql


def test_value_iteration_satisfies_bellman():
    env = ql.DoubleWell(slip=0.2)
    g = 0.9
    Q = ql.value_iteration(env, g)
    V = Q.max(1)
    for s in range(env.n):
        for a in range(3):
            rhs = sum(p * (r + g * V[s2]) for p, s2, r in env.transitions(s, a))
            assert abs(Q[s, a] - rhs) < 1e-9


def test_discount_decides_whether_to_leave_the_metastable_well():
    env = ql.DoubleWell()
    left = int(np.argmin(env.V[: env.n // 2]))
    right = env.n // 2 + int(np.argmin(env.V[env.n // 2:]))
    end = {g: ql.rollout(env, ql.greedy_policy(ql.value_iteration(env, g)), left)[-1]
           for g in (0.5, 0.85, 0.95)}
    assert end[0.5] == left and end[0.85] == left and end[0.95] == right


def test_q_learning_converges_to_q_star():
    env = ql.DoubleWell()
    Qs = ql.value_iteration(env, 0.95)
    Q, visits = ql.q_learning(env, 0.95, seed=0)
    assert visits.min() > 20
    assert np.max(np.abs(Q - Qs)) < 0.1
    assert np.array_equal(ql.greedy_policy(Q), ql.greedy_policy(Qs))


def test_q_learning_with_slip_finds_optimal_policy():
    env = ql.DoubleWell(slip=0.2)
    Qs = ql.value_iteration(env, 0.95)
    Q, _ = ql.q_learning(env, 0.95, episodes=6000, seed=1)
    assert np.mean(ql.greedy_policy(Q) == ql.greedy_policy(Qs)) >= 0.95
