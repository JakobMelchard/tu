"""Worked solution: exam of 30.06.2022 (label E22b, 2022S).

Source of the questions: [S11] VoWi `Exam-2022-06-30`.  Described in our own
words in README.md; the paper is not reproduced.  This is the first all
multiple-choice paper and the first with a k-armed bandit calculation, and a
student complains on [S10] that ~95 % of its questions were new -- including
four calculations (convolution, gradient descent, RSS, k-armed bandit) after a
Q&A session had suggested naming the algorithms would be enough.

Questions answered (numbers asserted in `check()`):
  Q1   k-armed bandit trace, actions 2, 1, 2, 3, 1 with rewards 3, -1, 1, 2, 0:
       definitely random at t = 2, 4, 5; possibly random at t = 1, 3.
  Q2   one gradient-descent step from w = 0 with alpha = 0.5 on five rows:
       RSS convention w = (54, 158, 200), so w1 = 158; the formula sheet's
       1/(2m) convention [S13] gives w1 = 15.8; the two differ by 2m = 10.
  Q2b  MSE = RSS/m convention for two steps: w1 = 31.6, then -700.8
       (alpha = 0.5 on unscaled features diverges).

Run:  ../../../../../.venv/bin/python solution.py
"""
import os
import sys

import numpy as np

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "py")))

from bandits import bandit_random_action_analysis, definitely_random_steps  # noqa: E402


# --- Question 1: the k-armed bandit trace ---------------------------------------
# "There were 5 actions and rewards (e.g. A1 = 2, R1 = 3, A2 = 1, R2 = -1, ...).
#  You had to say at which time steps the action was definitely chosen randomly
#  and at which it was possibly chosen randomly."  The paper's own numbers are
#  not public; this trace has the same shape (1-based action labels as printed).
ACTIONS_1BASED = [2, 1, 2, 3, 1]
REWARDS = [3.0, -1.0, 1.0, 2.0, 0.0]


def question_1_bandit():
    actions = [a - 1 for a in ACTIONS_1BASED]          # to 0-based arms
    trace = bandit_random_action_analysis(actions, REWARDS, k=3)
    rows = [dict(t=s["t"],
                 action=s["action"] + 1,
                 reward=s["reward"],
                 q_before=[round(float(v), 4) for v in s["q_before"]],
                 greedy=[a + 1 for a in s["greedy"]],
                 verdict=s["verdict"])
            for s in trace]
    return dict(
        trace=rows,
        definitely_random=[t for t in definitely_random_steps(actions, REWARDS, k=3)],
        possibly_random=[s["t"] for s in trace if s["verdict"] in ("tie", "greedy")],
        rule="a step is definitely exploratory iff the action taken is not in "
             "argmax_a Q_t(a) computed BEFORE the reward is applied",
    )


# --- Question 2: one step of gradient descent on the RSS ------------------------
# "Two features and one target (5 samples).  The coefficients w0, w1, w2 had to
#  be calculated using the RSS as the metric; a learning rate a = 0.5 was given.
#  When in the first step all w are 0, what will w1 be in the second step?"
FEATURES = np.array([
    [1.0, 3.0],
    [2.0, 5.0],
    [3.0, 2.0],
    [4.0, 6.0],
    [5.0, 1.0],
])
TARGET = np.array([12.0, 9.0, 11.0, 15.0, 7.0])
LEARNING_RATE = 0.5


def question_2_gradient_descent():
    """Both conventions, because the paper does not say which one it means.

    RSS = sum_i (y_i - w^T x_i)^2  ->  dRSS/dw_j = -2 sum_i (y_i - yhat_i) x_ij
    The course's formula sheet [S13] instead writes L = 1/(2m) sum (y - yhat)^2,
    whose gradient is -(1/m) sum (y - yhat) x_ij.  The two differ by a factor
    2m = 10 here, so state which you use.
    """
    X = np.c_[np.ones(len(TARGET)), FEATURES]          # intercept column -> w0
    w = np.zeros(3)
    resid = TARGET - X @ w                             # = TARGET, since w = 0

    grad_rss = -2 * X.T @ resid
    w_rss = w - LEARNING_RATE * grad_rss

    m = len(TARGET)
    grad_mean = -(X.T @ resid) / m
    w_mean = w - LEARNING_RATE * grad_mean

    return dict(
        residual_at_w0=resid.tolist(),
        gradient_rss=grad_rss.tolist(),
        w_after_one_step_rss=w_rss.tolist(),
        w1_rss=float(w_rss[1]),
        gradient_mean_squared=grad_mean.tolist(),
        w_after_one_step_mean=w_mean.tolist(),
        w1_mean=float(w_mean[1]),
        ratio=float(w_rss[1] / w_mean[1]),             # exactly 2m
        note="with w = 0 the residual is y itself, so w_j = 2*alpha*sum_i y_i x_ij",
    )


def question_2_second_step():
    """The paper asks for w1 'in the second step', i.e. after one update; the
    third value is given here too in case the wording means one more.

    This uses the MSE = RSS/m convention, gradient -(2/m) X^T (y - Xw), which
    sits between the two conventions of question 2: w1 = 158 / 5 = 31.6."""
    X = np.c_[np.ones(len(TARGET)), FEATURES]
    w = np.zeros(3)
    history = [w.copy()]
    for _ in range(2):
        w = w + 2 * LEARNING_RATE * X.T @ (TARGET - X @ w) / len(TARGET)   # MSE gradient step
        history.append(w.copy())
    return dict(w_history=[h.tolist() for h in history],
                diverges=bool(np.abs(history[-1]).max() > np.abs(history[1]).max()),
                note="a learning rate of 0.5 on unscaled features overshoots badly; "
                     "the exam only wants one arithmetic step, not convergence")


def solve():
    return {"1": question_1_bandit(),
            "2": question_2_gradient_descent(),
            "2b": question_2_second_step()}


def check(r):
    """Assert the numeric answers listed in the module docstring."""
    q1 = r["1"]
    assert q1["definitely_random"] == [2, 4, 5] and q1["possibly_random"] == [1, 3]

    q2 = r["2"]
    assert np.allclose(q2["w_after_one_step_rss"], [54.0, 158.0, 200.0])
    assert np.allclose(q2["w_after_one_step_mean"], [5.4, 15.8, 20.0])
    assert np.isclose(q2["w1_rss"], 158.0) and np.isclose(q2["w1_mean"], 15.8)
    assert np.isclose(q2["ratio"], 2 * len(TARGET))

    h = r["2b"]["w_history"]
    assert np.isclose(h[1][1], 31.6) and np.isclose(h[2][1], -700.8) and r["2b"]["diverges"]


if __name__ == "__main__":
    import json
    r = solve()
    print("--- question 1: k-armed bandit ---")
    print(" t  A_t  R_t   Q before          greedy   verdict")
    for row in r["1"]["trace"]:
        print("%2d  %3d  %4.0f   %-16s %-8s %s"
              % (row["t"], row["action"], row["reward"], row["q_before"],
                 row["greedy"], row["verdict"]))
    print("definitely random:", r["1"]["definitely_random"],
          " possibly random:", r["1"]["possibly_random"])
    print("\n--- question 2: one gradient-descent step ---")
    print(json.dumps(r["2"], indent=2, default=float))
    print("\n--- question 2, two steps ---")
    print(json.dumps(r["2b"], indent=2, default=float))
    check(r)
    print("\ncheck(): all asserted answers hold")
