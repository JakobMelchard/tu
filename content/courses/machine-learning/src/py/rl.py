"""Markov decision processes and tabular Monte-Carlo / TD methods.

Chapters 3, 5 and 6 of Sutton & Barto [S21].  The course stops at **tabular**
methods -- state-action spaces small enough for Q to be a table -- with no
function approximation and no deep RL.  The k-armed bandit that supplies the
update rules used here, and the exam calculation built on it, are in
`bandits.py`.

Section numbers below are Sutton & Barto, 2nd ed. [S21]: 3 the MDP formalism,
3.5 the Bellman equation, 5.1 first-visit Monte-Carlo prediction, 5.3 Monte-Carlo
control with exploring starts, 6.1 TD(0).

The examined property (E22a, answer **true** [S12]) is structural and visible in
the code: `first_visit_mc_prediction` and `mc_control_es` can only update once an
episode has ended, because their target is the realised return of the whole
episode; `td0_prediction` updates every step by bootstrapping.

Run `python rl.py` for the 4x4 grid-world demo of note 14.
"""
import numpy as np


# --------------------------------------------------- MDPs and Monte Carlo
class GridWorld:
    """A tiny episodic MDP: walk to the terminal corner, -1 per step ([S21] 3).

    States are (row, col) on an n x n grid; actions 0..3 are up/down/left/right;
    the episode ends at (n-1, n-1).  Small enough for exact tabular methods.
    """

    MOVES = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    def __init__(self, n=4):
        self.n = n
        self.states = [(i, j) for i in range(n) for j in range(n)]
        self.terminal = (n - 1, n - 1)

    def actions(self, _state=None):
        return list(range(4))

    def step(self, state, action):
        di, dj = self.MOVES[action]
        i, j = state
        ni, nj = min(max(i + di, 0), self.n - 1), min(max(j + dj, 0), self.n - 1)
        nxt = (ni, nj)
        return nxt, -1.0, nxt == self.terminal

    def episode(self, policy, rng, max_len=200, start=None, first_action=None):
        """Generate (state, action, reward) triples following `policy`.

        `start` / `first_action` implement *exploring starts*: every state-action
        pair must have a non-zero chance of beginning an episode, otherwise a
        greedy policy can starve pairs it currently dislikes ([S21] 5.3).
        """
        if start is None:
            start = self.states[int(rng.integers(len(self.states) - 1))]
        s, out = start, []
        for step in range(max_len):
            if s == self.terminal:
                break
            a = first_action if (step == 0 and first_action is not None) else policy(s, rng)
            s2, r, done = self.step(s, a)
            out.append((s, a, r))
            s = s2
            if done:
                break
        return out


def random_policy(_state, rng):
    return int(rng.integers(4))


def first_visit_mc_prediction(env, policy, episodes=2000, gamma=1.0, rng=0):
    """Estimate v_pi by averaging the returns following first visits ([S21] 5.1).

    The update happens **after** the episode ends -- which is the examined
    property "for the Monte Carlo method value estimates and policies are
    changed only on the completion of an episode" (true, E22a) [S12].
    """
    rng = np.random.default_rng(rng)
    totals, counts = {}, {}
    for _ in range(episodes):
        ep = env.episode(policy, rng)
        g = 0.0
        for t in reversed(range(len(ep))):
            s, _a, r = ep[t]
            g = gamma * g + r
            if s not in [x[0] for x in ep[:t]]:
                totals[s] = totals.get(s, 0.0) + g
                counts[s] = counts.get(s, 0) + 1
    return {s: totals[s] / counts[s] for s in totals}


def mc_control_es(env, episodes=20000, gamma=1.0, rng=0, max_len=100):
    """Monte-Carlo control with exploring starts ([S21] 5.3): pi and Q improve each other.

    Each episode starts from a uniformly random (state, action) pair, is played
    out with the current deterministic greedy policy, and only *then* updates
    Q on first visits and sets pi(s) = argmax_a Q(s, a).  Nothing is learned
    before the episode ends -- the property E22a examines [S12].
    """
    rng = np.random.default_rng(rng)
    q = {(s, a): 0.0 for s in env.states for a in env.actions()}
    counts = {k: 0 for k in q}
    pi = {s: 0 for s in env.states}

    def policy(s, _r):
        return pi[s]

    non_terminal = [s for s in env.states if s != env.terminal]
    for _ in range(episodes):
        s0 = non_terminal[int(rng.integers(len(non_terminal)))]
        a0 = int(rng.integers(4))
        ep = env.episode(policy, rng, start=s0, first_action=a0, max_len=max_len)
        g = 0.0
        for t in reversed(range(len(ep))):
            s, a, r = ep[t]
            g = gamma * g + r
            if (s, a) in {(x[0], x[1]) for x in ep[:t]}:   # first-visit only
                continue
            counts[(s, a)] += 1
            q[(s, a)] += (g - q[(s, a)]) / counts[(s, a)]
            pi[s] = int(np.argmax([q[(s, b)] for b in env.actions()]))
    return pi, q


def td0_prediction(env, policy, episodes=2000, alpha=0.1, gamma=1.0, rng=0):
    """TD(0): V(S_t) <- V(S_t) + a[R + g V(S_{t+1}) - V(S_t)], updated **every step**.

    Here only for the contrast with `first_visit_mc_prediction`, which cannot
    update before the episode ends.
    """
    rng = np.random.default_rng(rng)
    v = {s: 0.0 for s in env.states}
    for _ in range(episodes):
        ep = env.episode(policy, rng)
        for t, (s, _a, r) in enumerate(ep):
            s2 = ep[t + 1][0] if t + 1 < len(ep) else env.terminal
            v[s] += alpha * (r + gamma * v[s2] - v[s])
    return v


if __name__ == "__main__":
    env = GridWorld(4)
    print("=== 4x4 grid world, -1 per step, terminal at (3,3) ===")
    v = first_visit_mc_prediction(env, random_policy, episodes=3000, rng=1)
    print("  first-visit MC value of (0,0): %.1f   of (2,3): %.1f" % (v[(0, 0)], v[(2, 3)]))
    vt = td0_prediction(env, random_policy, episodes=3000, rng=1)
    print("  TD(0)              of (0,0): %.1f   of (2,3): %.1f" % (vt[(0, 0)], vt[(2, 3)]))
    print("  (MC updates only when an episode ends; TD(0) updates every step)")
    pi, _ = mc_control_es(env, episodes=20000, rng=1)
    arrows = {0: "^", 1: "v", 2: "<", 3: ">"}
    print("\n  greedy policy after MC control with exploring starts:")
    for i in range(4):
        print("   ", " ".join("." if (i, j) == env.terminal else arrows[pi[(i, j)]] for j in range(4)))
