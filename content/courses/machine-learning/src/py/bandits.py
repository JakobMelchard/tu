"""The k-armed bandit: value estimates, exploration policies, and the calculation
the exam asks for.

Chapter 2 of Sutton & Barto [S21], which is the book the lecture works from
[S10, S17].  A k-armed bandit calculation has been in the calculation section of
every 184.702 paper since 2022 (E22b, E24a, E25b, E26a) [S11]:

    "given the actions taken and the rewards received over N steps, in which
     steps was a random (exploratory) action definitely taken?"

`bandit_random_action_analysis` is that calculation.  Note 14 works an example
by hand and `../exercises/2022-06-30/` works the paper's own version.

Section numbers below are Sutton & Barto, 2nd ed. [S21]: 2.3 the testbed, 2.4
the incremental sample average, 2.5 the constant step size, 2.6 optimistic
initial values, 2.7 UCB.  MDPs and the tabular Monte-Carlo methods that build on
these update rules are in `rl.py`.

Run `python bandits.py` for the demo table of note 14.
"""
import numpy as np


# ------------------------------------------------------------------ estimates
def sample_average_update(q, n, reward):
    """Q_{n+1} = Q_n + (1/n)[R_n - Q_n]  ([S21] 2.4).  `n` counts this reward."""
    return q + (reward - q) / n


def constant_step_update(q, alpha, reward):
    """Q_{n+1} = Q_n + a[R_n - Q_n]  ([S21] 2.5): tracks a non-stationary target."""
    return q + alpha * (reward - q)


def greedy_set(q, tol=1e-12):
    """Indices attaining max(Q).  More than one means the greedy choice is a tie."""
    q = np.asarray(q, float)
    return np.flatnonzero(q >= q.max() - tol)


def epsilon_greedy(q, epsilon, rng):
    """Take argmax Q with probability 1-eps, otherwise a uniformly random action."""
    if rng.random() < epsilon:
        return int(rng.integers(len(q)))
    best = greedy_set(q)
    return int(best[0]) if len(best) == 1 else int(rng.choice(best))


def ucb_select(q, counts, t, c=2.0):
    """A_t = argmax [Q_t(a) + c sqrt(ln t / N_t(a))]; untried actions go first ([S21] 2.7)."""
    counts = np.asarray(counts, float)
    untried = np.flatnonzero(counts == 0)
    if len(untried):
        return int(untried[0])
    return int(np.argmax(np.asarray(q, float) + c * np.sqrt(np.log(t) / counts)))


# ---------------------------------------------------------- the exam question
def bandit_random_action_analysis(actions, rewards, k=None, q_init=0.0, alpha=None):
    """Replay an epsilon-greedy bandit trace and classify each step.

    For every step, *before* the reward is applied, compare the action taken
    with the greedy set argmax_a Q_t(a):

      'definite' - the action is not in the greedy set, so it can only have come
                   from the exploration branch;
      'tie'      - several actions are tied for the maximum, so a greedy step is
                   indistinguishable from an exploratory one;
      'greedy'   - the action is the unique maximiser, so it is *possibly* random
                   (epsilon-greedy picks the greedy action with probability
                   1 - eps + eps/k) but cannot be shown to be.

    Only 'definite' steps answer "in which steps was a random action definitely
    taken".  With the usual Q_1 = 0 the first step is always a tie.

    Returns a list of dicts, one per step, with the Q table before the step.
    """
    actions = [int(a) for a in actions]
    rewards = [float(r) for r in rewards]
    k = (max(actions) + 1) if k is None else k
    q = np.full(k, float(q_init))
    counts = np.zeros(k, int)
    trace = []
    for t, (a, r) in enumerate(zip(actions, rewards), start=1):
        best = greedy_set(q)
        if a not in best:
            verdict = "definite"
        elif len(best) > 1:
            verdict = "tie"
        else:
            verdict = "greedy"
        trace.append(dict(t=t, action=a, reward=r, q_before=q.copy(),
                          greedy=best.tolist(), verdict=verdict))
        counts[a] += 1
        q[a] = (constant_step_update(q[a], alpha, r) if alpha
                else sample_average_update(q[a], counts[a], r))
    return trace


def definitely_random_steps(actions, rewards, k=None, **kw):
    """The time steps (1-based) at which exploration is certain."""
    return [s["t"] for s in bandit_random_action_analysis(actions, rewards, k, **kw)
            if s["verdict"] == "definite"]


# ------------------------------------------------------------------- testbeds
class Bandit:
    """k-armed testbed: q*(a) ~ N(0,1), reward ~ N(q*(a), 1)  ([S21] 2.3).

    With `drift > 0` every q*(a) performs an independent random walk each step,
    which is the non-stationary case that needs a constant step size.
    """

    def __init__(self, k=10, rng=0, drift=0.0):
        self.k, self.drift = k, drift
        self.rng = np.random.default_rng(rng)
        self.q_star = self.rng.normal(size=k)

    def pull(self, a):
        r = float(self.rng.normal(self.q_star[a], 1.0))
        if self.drift:
            self.q_star += self.rng.normal(0, self.drift, self.k)
        return r

    @property
    def optimal(self):
        return int(np.argmax(self.q_star))


def run_bandit(bandit, steps=1000, policy="epsilon", epsilon=0.1, c=2.0,
               alpha=None, q_init=0.0, rng=0):
    """Run one bandit episode; return (mean reward, fraction of optimal actions)."""
    rng = np.random.default_rng(rng)
    q = np.full(bandit.k, float(q_init))
    counts = np.zeros(bandit.k, int)
    total, optimal = 0.0, 0
    for t in range(1, steps + 1):
        if policy == "ucb":
            a = ucb_select(q, counts, t, c)
        else:
            a = epsilon_greedy(q, epsilon, rng)
        optimal += (a == bandit.optimal)
        r = bandit.pull(a)
        counts[a] += 1
        q[a] = constant_step_update(q[a], alpha, r) if alpha else sample_average_update(q[a], counts[a], r)
        total += r
    return total / steps, optimal / steps


if __name__ == "__main__":
    print("=== the exam calculation (note 14's table, arms labelled 1..4) ===")
    actions = [a - 1 for a in (1, 2, 2, 1, 3, 1)]        # the exam's 1-based labels -> 0-based
    rewards = [1, -1, 3, 1, 0, -2]
    print(" t  A_t  R_t   Q before          greedy set   verdict")
    for s in bandit_random_action_analysis(actions, rewards, k=4):
        print("%2d  %3d  %4.0f   %-17s %-12s %s"
              % (s["t"], s["action"] + 1, s["reward"], np.round(s["q_before"], 3),
                 [a + 1 for a in s["greedy"]], s["verdict"]))
    print("definitely random at steps", definitely_random_steps(actions, rewards, k=4))

    print("\n=== sample average vs constant step on rewards 1,1,1,10 ===")
    q_sa, q_cs = 0.0, 0.0
    for n, r in enumerate([1, 1, 1, 10], start=1):
        q_sa = sample_average_update(q_sa, n, r)
        q_cs = constant_step_update(q_cs, 0.5, r)
        print("  n=%d  sample average %.3f   alpha=0.5 %.3f" % (n, q_sa, q_cs))

    print("\n=== 10-armed testbed, 1000 steps, 20 runs ===")
    for label, kw in [("greedy    ", dict(epsilon=0.0)), ("eps = 0.1 ", dict(epsilon=0.1)),
                      ("optimistic", dict(epsilon=0.0, q_init=5.0)), ("UCB c = 2 ", dict(policy="ucb"))]:
        s = [run_bandit(Bandit(rng=i), 1000, rng=i, **kw) for i in range(20)]
        print("  %s mean reward %.3f  optimal action %.0f %%"
              % (label, np.mean([x[0] for x in s]), 100 * np.mean([x[1] for x in s])))
