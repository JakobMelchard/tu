"""Tabular Q-learning for a particle in a tilted 1-D double well (toy, physics flavour).

Note 09. MDP [S24 ch. 3]:
  states    x in {0, ..., n-1} (box, hard walls), u = (x - c)/w in [-2, 2]
  actions   a in {-1, 0, +1} (kick left, stay, kick right)
  dynamics  x' = clip(x + a); with probability `slip` the kick is replaced by a random one
  reward    r = -V(x') - cost |a|,  V(u) = (u^2 - 1)^2 - tilt u
            (metastable well at u ~ -1, global minimum at u ~ +1, barrier at u ~ 0)
Bellman optimality: Q*(s,a) = E[r + gamma max_a' Q*(s',a')]; value iteration solves it.
Q-learning [S25]: Q(s,a) <- Q(s,a) + eta_t [r + gamma max_a' Q(s',a') - Q(s,a)],
off-policy, converges to Q* if every (s,a) is visited infinitely often and
sum eta_t = inf, sum eta_t^2 < inf; here eta_t = n(s,a)^{-0.6}, epsilon-greedy behaviour.
For tilt 0.3 the switch happens between gamma = 0.85 and 0.9 (value iteration).
Physics point: with a short horizon (small gamma) the optimal agent stays in the
metastable well, because crossing the barrier costs reward now and pays only later.
"""
from __future__ import annotations

import numpy as np

ACTIONS = np.array([-1, 0, 1])


class DoubleWell:
    def __init__(self, n=21, tilt=0.3, cost=0.05, slip=0.0):
        self.n, self.tilt, self.cost, self.slip = n, tilt, cost, slip
        u = (np.arange(n) - (n - 1) / 2) / ((n - 1) / 4)
        self.V = (u**2 - 1) ** 2 - tilt * u

    def next_state(self, s, a_idx):
        return int(np.clip(s + ACTIONS[a_idx], 0, self.n - 1))

    def reward(self, s_next, a_idx):
        return -self.V[s_next] - self.cost * abs(ACTIONS[a_idx])

    def transitions(self, s, a_idx):
        """List of (probability, s', r)."""
        out = []
        for b in range(3):
            p = (1 - self.slip) * (b == a_idx) + self.slip / 3
            if p > 0:
                s2 = self.next_state(s, b)
                out.append((p, s2, self.reward(s2, a_idx)))
        return out

    def step(self, s, a_idx, rng):
        b = rng.integers(3) if rng.random() < self.slip else a_idx
        s2 = self.next_state(s, b)
        return s2, self.reward(s2, a_idx)


def value_iteration(env: DoubleWell, gamma: float, tol=1e-12, max_iter=100_000):
    """Fixed point of the Bellman optimality operator (a gamma-contraction)."""
    Q = np.zeros((env.n, 3))
    T = [[env.transitions(s, a) for a in range(3)] for s in range(env.n)]
    for _ in range(max_iter):
        V = Q.max(1)
        Qn = np.array([[sum(p * (r + gamma * V[s2]) for p, s2, r in T[s][a]) for a in range(3)]
                       for s in range(env.n)])
        if np.max(np.abs(Qn - Q)) < tol:
            return Qn
        Q = Qn
    return Q


def epsilon_greedy(Q, s, eps, rng):
    if rng.random() < eps:
        return int(rng.integers(3))
    q = Q[s]
    best = np.flatnonzero(q == q.max())
    return int(best[0]) if best.size == 1 else int(best[rng.integers(best.size)])


def q_learning(env: DoubleWell, gamma: float, episodes=3000, horizon=60, eps=0.5,
               omega=0.6, seed=0):
    """Exploring starts (uniform s_0), epsilon-greedy behaviour, count-based step size."""
    rng = np.random.default_rng(seed)
    Q = np.zeros((env.n, 3))
    visits = np.zeros((env.n, 3))
    for _ in range(episodes):
        s = int(rng.integers(env.n))
        for _ in range(horizon):
            a = epsilon_greedy(Q, s, eps, rng)
            s2, r = env.step(s, a, rng)
            visits[s, a] += 1
            eta = visits[s, a] ** (-omega)
            Q[s, a] += eta * (r + gamma * Q[s2].max() - Q[s, a])
            s = s2
    return Q, visits


def greedy_policy(Q):
    return ACTIONS[np.argmax(Q, axis=1)]


def rollout(env: DoubleWell, policy, s0, steps=40):
    s, path = s0, [s0]
    for _ in range(steps):
        s = env.next_state(s, int(np.flatnonzero(ACTIONS == policy[s])[0]))
        path.append(s)
    return path


def _demo() -> None:
    env = DoubleWell()
    left, right = int(np.argmin(env.V[: env.n // 2])), env.n // 2 + int(np.argmin(env.V[env.n // 2:]))
    print(f"V: metastable minimum x = {left} (V = {env.V[left]:+.3f}), global x = {right} "
          f"(V = {env.V[right]:+.3f}), barrier V = {env.V[env.n // 2]:+.3f}")
    for gamma in [0.5, 0.85, 0.9, 0.95]:
        Qs = value_iteration(env, gamma)
        end = rollout(env, greedy_policy(Qs), left)[-1]
        print(f"gamma = {gamma}: optimal agent started at x = {left} ends at x = {end}")
    gamma = 0.95
    Qs = value_iteration(env, gamma)
    Q, visits = q_learning(env, gamma)
    agree = np.mean(greedy_policy(Q) == greedy_policy(Qs))
    print(f"Q-learning gamma = {gamma}: max|Q - Q*| = {np.max(np.abs(Q - Qs)):.3f} "
          f"(|Q*| up to {np.max(np.abs(Qs)):.1f}), greedy policy agreement {agree:.2f}, "
          f"min visits {int(visits.min())}")
    print("greedy policy (kick per state):", "".join({-1: "<", 0: ".", 1: ">"}[a]
                                                   for a in greedy_policy(Q)))
    env_s = DoubleWell(slip=0.2)
    Qs2 = value_iteration(env_s, gamma)
    Q2, _ = q_learning(env_s, gamma, episodes=6000, seed=1)
    print(f"slip 0.2: max|Q - Q*| = {np.max(np.abs(Q2 - Qs2)):.3f}, policy agreement "
          f"{np.mean(greedy_policy(Q2) == greedy_policy(Qs2)):.2f}")


if __name__ == "__main__":
    _demo()
