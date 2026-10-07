"""Tests for rl.py: the grid-world MDP, Monte-Carlo prediction and control, TD(0).

Reference results are Sutton & Barto [S21] ch. 3, 5 and 6, and the examined
property that Monte-Carlo methods update only when an episode ends (E22a,
**true** [S12]).  The bandit tests are in test_bandits.py.
"""
import numpy as np
import pytest

from rl import (GridWorld, first_visit_mc_prediction, mc_control_es, random_policy,
                td0_prediction)


def test_grid_world_step():
    env = GridWorld(4)
    assert env.step((0, 0), 0) == ((0, 0), -1.0, False)      # up at the wall stays
    assert env.step((0, 0), 3) == ((0, 1), -1.0, False)
    assert env.step((3, 2), 3) == ((3, 3), -1.0, True)       # reaching the goal ends it


def test_monte_carlo_prediction_orders_states_by_distance():
    """v_pi under a random walk is more negative the further from the terminal state."""
    env = GridWorld(4)
    v = first_visit_mc_prediction(env, random_policy, episodes=2000, rng=0)
    assert v[(0, 0)] < v[(1, 1)] < v[(2, 2)] < v[(3, 2)] < 0


def test_monte_carlo_and_td_agree_roughly():
    """Both estimate the same v_pi; TD updates every step, MC only at episode end."""
    env = GridWorld(4)
    mc = first_visit_mc_prediction(env, random_policy, episodes=3000, rng=1)
    td = td0_prediction(env, random_policy, episodes=3000, alpha=0.05, rng=1)
    for s in [(3, 2), (2, 3), (2, 2)]:
        assert abs(mc[s] - td[s]) < 0.4 * abs(mc[s])


def test_mc_control_with_exploring_starts_finds_an_optimal_policy():
    """Every greedy action must reduce the Manhattan distance to the terminal state."""
    env = GridWorld(4)
    pi, q = mc_control_es(env, episodes=20000, rng=1)
    goal = env.terminal
    for s in env.states:
        if s == goal:
            continue
        di, dj = GridWorld.MOVES[pi[s]]
        nxt = (min(max(s[0] + di, 0), 3), min(max(s[1] + dj, 0), 3))
        before = abs(goal[0] - s[0]) + abs(goal[1] - s[1])
        after = abs(goal[0] - nxt[0]) + abs(goal[1] - nxt[1])
        assert after == before - 1, f"policy at {s} does not move towards the goal"
    # and Q(s, a) for the greedy action is the negative Manhattan distance
    assert q[((0, 0), pi[(0, 0)])] == pytest.approx(-6.0, abs=0.5)
