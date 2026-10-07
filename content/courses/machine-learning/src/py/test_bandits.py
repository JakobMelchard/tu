"""Tests for bandits.py: value estimates, exploration, and the exam's
"which step was definitely random?" calculation.

Reference results are the closed forms of Sutton & Barto [S21] ch. 2 and the
examined properties of [S11]/[S12].  The MDP and Monte-Carlo tests are in
test_rl.py.
"""
import numpy as np
import pytest

from bandits import (Bandit, bandit_random_action_analysis, constant_step_update,
                     definitely_random_steps, epsilon_greedy, greedy_set, run_bandit,
                     sample_average_update, ucb_select)


def test_sample_average_update_equals_the_running_mean():
    """Q_{n+1} = Q_n + (1/n)[R_n - Q_n] is exactly the arithmetic mean ([S21] 2.4)."""
    rewards = [3.0, -1.0, 4.0, 1.0, 5.0]
    q = 0.0
    for n, r in enumerate(rewards, start=1):
        q = sample_average_update(q, n, r)
        assert q == pytest.approx(np.mean(rewards[:n]))


def test_constant_step_is_an_exponentially_weighted_average():
    """Q_n = (1-a)^n Q_1 + sum a(1-a)^{n-i} R_i, and the weights sum to 1 ([S21] 2.5)."""
    a, rewards, q1 = 0.3, [1.0, -2.0, 4.0, 0.5], 2.0
    q = q1
    for r in rewards:
        q = constant_step_update(q, a, r)
    n = len(rewards)
    closed = (1 - a) ** n * q1 + sum(a * (1 - a) ** (n - i) * r
                                     for i, r in enumerate(rewards, start=1))
    assert q == pytest.approx(closed)
    assert (1 - a) ** n + sum(a * (1 - a) ** (n - i) for i in range(1, n + 1)) == pytest.approx(1.0)


def test_constant_step_tracks_a_change_that_the_sample_average_dilutes():
    """The reason non-stationary problems need a constant step size."""
    rewards = [1.0, 1.0, 1.0, 10.0]
    q_sa, q_cs = 0.0, 0.0
    for n, r in enumerate(rewards, start=1):
        q_sa = sample_average_update(q_sa, n, r)
        q_cs = constant_step_update(q_cs, 0.5, r)
    assert q_sa == pytest.approx(3.25)
    assert q_cs == pytest.approx(5.4375)
    assert q_cs > q_sa


def test_bandit_trace_reproduces_the_worked_table_of_note_14():
    """Note 14 labels the arms 1..4 as the exam papers do; the code is 0-based."""
    actions = [a - 1 for a in (1, 2, 2, 1, 3, 1)]
    rewards = [1, -1, 3, 1, 0, -2]
    trace = bandit_random_action_analysis(actions, rewards, k=4)
    assert [s["verdict"] for s in trace] == [
        "tie", "definite", "definite", "tie", "definite", "tie"]
    assert [s["greedy"] for s in trace] == [
        [0, 1, 2, 3], [0], [0], [0, 1], [0, 1], [0, 1]]
    assert [list(s["q_before"]) for s in trace] == [
        [0, 0, 0, 0], [1, 0, 0, 0], [1, -1, 0, 0], [1, 1, 0, 0], [1, 1, 0, 0], [1, 1, 0, 0]]
    assert definitely_random_steps(actions, rewards, k=4) == [2, 3, 5]
    # Q after the run: arm 1 saw 1, 1, -2 -> 0; arm 2 saw -1, 3 -> 1; arm 3 saw 0.
    q_final = trace[-1]["q_before"].copy()
    q_final[0] = sample_average_update(q_final[0], 3, -2.0)
    assert q_final == pytest.approx([0.0, 1.0, 0.0, 0.0])


def test_first_step_is_never_definitely_random():
    """All-zero initial estimates make every action greedy at t = 1."""
    for a0 in range(4):
        trace = bandit_random_action_analysis([a0, 0], [1.0, 1.0], k=4)
        assert trace[0]["verdict"] == "tie"


def test_a_step_away_from_a_unique_maximum_is_definitely_random():
    trace = bandit_random_action_analysis([0, 0, 1], [5.0, 5.0, 0.0], k=3)
    assert trace[2]["verdict"] == "definite"
    trace = bandit_random_action_analysis([0, 0, 0], [5.0, 5.0, 0.0], k=3)
    assert trace[2]["verdict"] == "greedy"          # possibly random, not provably


def test_greedy_set_and_epsilon_greedy():
    assert greedy_set([1.0, 3.0, 3.0, 2.0]).tolist() == [1, 2]
    rng = np.random.default_rng(0)
    q = np.array([0.0, 10.0, 0.0])
    picks = [epsilon_greedy(q, 0.0, rng) for _ in range(20)]
    assert set(picks) == {1}                        # eps = 0 is pure exploitation
    picks = [epsilon_greedy(q, 1.0, rng) for _ in range(200)]
    assert len(set(picks)) == 3                     # eps = 1 is pure exploration


def test_ucb_tries_every_arm_before_repeating():
    q, counts = np.zeros(4), np.zeros(4, int)
    chosen = []
    for t in range(1, 5):
        a = ucb_select(q, counts, t)
        chosen.append(a)
        counts[a] += 1
    assert sorted(chosen) == [0, 1, 2, 3]


def test_ucb_prefers_the_less_tried_arm_at_equal_value():
    q = np.array([1.0, 1.0])
    assert ucb_select(q, np.array([100, 5]), t=105) == 1


def test_epsilon_greedy_beats_pure_greedy_on_the_testbed():
    """[S21] fig. 2.2: some exploration wins on a 10-armed testbed."""
    greedy = [run_bandit(Bandit(rng=s), 800, epsilon=0.0, rng=s) for s in range(15)]
    explore = [run_bandit(Bandit(rng=s), 800, epsilon=0.1, rng=s) for s in range(15)]
    assert np.mean([r for r, _ in explore]) > np.mean([r for r, _ in greedy])
    assert np.mean([o for _, o in explore]) > np.mean([o for _, o in greedy])


def test_ucb_is_competitive_with_epsilon_greedy():
    ucb = [run_bandit(Bandit(rng=s), 800, policy="ucb", rng=s) for s in range(15)]
    eps = [run_bandit(Bandit(rng=s), 800, epsilon=0.1, rng=s) for s in range(15)]
    assert np.mean([r for r, _ in ucb]) >= np.mean([r for r, _ in eps]) - 0.05
