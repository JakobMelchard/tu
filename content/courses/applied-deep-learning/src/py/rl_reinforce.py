"""REINFORCE (Monte-Carlo policy gradient) on a tiny gridworld implemented inline.

Environment: size x size grid, start top-left, goal bottom-right (+1), one pit
(-1), -0.01 per step, episode capped at max_steps. State is the one-hot cell
index. The policy is a small MLP over the 4 actions; the update is
    grad J = E[ sum_t grad log pi(a_t|s_t) * (G_t - b) ] + beta * grad H(pi),
with G_t the discounted return-to-go, b a running-mean baseline and H the
policy entropy. Training uses exploring starts (random initial cell) so that
the sparse +1 is found at all; evaluation always starts top-left.
"""

from __future__ import annotations

import numpy as np
import torch
from torch import nn
from torch.nn import functional as F

from common import Timer, loss_decreased, moving_average, seed_all

ACTIONS = ((-1, 0), (1, 0), (0, -1), (0, 1))  # up, down, left, right


class GridWorld:
    """Minimal Gymnasium-like API: reset() -> state, step(a) -> (state, reward, done)."""

    def __init__(self, size: int = 5, max_steps: int = 30, step_penalty: float = -0.01):
        self.size, self.max_steps, self.step_penalty = size, max_steps, step_penalty
        self.goal = (size - 1, size - 1)
        self.pit = (size // 2, size // 2)
        self.n_states, self.n_actions = size * size, 4

    def reset(self, start: tuple[int, int] = (0, 0)) -> int:
        self.pos, self.t = start, 0
        return self._state()

    def _state(self) -> int:
        return self.pos[0] * self.size + self.pos[1]

    def step(self, a: int) -> tuple[int, float, bool]:
        dr, dc = ACTIONS[a]
        r = min(max(self.pos[0] + dr, 0), self.size - 1)  # walls: stay in place
        c = min(max(self.pos[1] + dc, 0), self.size - 1)
        self.pos, self.t = (r, c), self.t + 1
        if self.pos == self.goal:
            return self._state(), 1.0, True
        if self.pos == self.pit:
            return self._state(), -1.0, True
        return self._state(), self.step_penalty, self.t >= self.max_steps

    def random_start(self, gen: torch.Generator) -> tuple[int, int]:
        while True:
            r, c = torch.randint(0, self.size, (2,), generator=gen).tolist()
            if (r, c) not in (self.goal, self.pit):
                return r, c


class PolicyNet(nn.Module):
    def __init__(self, n_states: int, n_actions: int, hidden: int = 64):
        super().__init__()
        self.n_states = n_states
        self.net = nn.Sequential(nn.Linear(n_states, hidden), nn.Tanh(), nn.Linear(hidden, n_actions))

    def forward(self, state: torch.Tensor) -> torch.Tensor:
        """state: [B] int -> logits [B, n_actions]."""
        return self.net(F.one_hot(state, self.n_states).float())


def discounted_returns(rewards: list[float], gamma: float) -> torch.Tensor:
    """G_t = sum_{k>=0} gamma^k r_{t+k}, computed backwards in O(T)."""
    G, out = 0.0, [0.0] * len(rewards)
    for t in reversed(range(len(rewards))):
        G = rewards[t] + gamma * G
        out[t] = G
    return torch.tensor(out)


def run_episode(env: GridWorld, policy: PolicyNet, gen: torch.Generator | None = None,
                greedy: bool = False, start: tuple[int, int] = (0, 0)):
    """Roll out one episode; return (log_probs [T], entropies [T], rewards list, reached_goal)."""
    s, done, log_probs, entropies, rewards = env.reset(start), False, [], [], []
    while not done:
        dist = torch.distributions.Categorical(logits=policy(torch.tensor([s])))
        a = dist.probs.argmax() if greedy else torch.multinomial(dist.probs, 1, generator=gen).squeeze()
        log_probs.append(dist.log_prob(a).squeeze())
        entropies.append(dist.entropy().squeeze())
        s, r, done = env.step(int(a))
        rewards.append(r)
    return torch.stack(log_probs), torch.stack(entropies), rewards, env.pos == env.goal


def run(episodes: int = 400, gamma: float = 0.98, lr: float = 1e-2, size: int = 5, entropy_coef: float = 0.01,
        exploring_starts: bool = True, device: torch.device | None = None, seed: int = 0, log_every: int = 0) -> dict:
    # Single-step rollouts of a tiny net are faster on CPU than on MPS; `device` is accepted for API symmetry.
    gen = seed_all(seed)
    env = GridWorld(size)
    policy = PolicyNet(env.n_states, env.n_actions)
    opt = torch.optim.Adam(policy.parameters(), lr=lr)
    returns, successes, baseline = [], [], 0.0
    with Timer() as t:
        for ep in range(1, episodes + 1):
            start = env.random_start(gen) if exploring_starts else (0, 0)
            log_probs, entropies, rewards, ok = run_episode(env, policy, gen, start=start)
            G = discounted_returns(rewards, gamma)
            baseline = 0.9 * baseline + 0.1 * G[0].item()  # running-mean baseline reduces variance
            # minimising this = ascending the policy-gradient estimate, plus an entropy bonus
            loss = -(log_probs * (G - baseline)).sum() - entropy_coef * entropies.sum()
            opt.zero_grad(set_to_none=True)
            loss.backward()
            opt.step()
            returns.append(float(sum(rewards)))
            successes.append(float(ok))
            if log_every and ep % log_every == 0:
                print(f"episode {ep:4d}  return {np.mean(returns[-log_every:]):+.3f}  "
                      f"success {np.mean(successes[-log_every:]):.2f}  len {len(rewards)}")
    losses = [-v for v in moving_average(returns, 20)]  # negative smoothed return: decreases == learns
    _, _, greedy_rewards, greedy_ok = run_episode(env, policy, greedy=True)
    return {"losses": losses, "returns": returns, "success_rate": float(np.mean(successes[-50:])),
            "greedy_reaches_goal": greedy_ok, "greedy_steps": len(greedy_rewards), "policy": policy,
            "seconds": t.seconds}


if __name__ == "__main__":
    print("discounted returns of [0,0,1] with gamma=0.9:", [round(v, 3) for v in discounted_returns([0, 0, 1], 0.9).tolist()])
    out = run(log_every=50)
    print(f"success rate over last 50 training episodes {out['success_rate']:.2f}; greedy policy from the corner "
          f"reaches the goal: {out['greedy_reaches_goal']} in {out['greedy_steps']} steps (optimum 8); "
          f"{out['seconds']:.1f}s, loss decreased {loss_decreased(out['losses'])}")
