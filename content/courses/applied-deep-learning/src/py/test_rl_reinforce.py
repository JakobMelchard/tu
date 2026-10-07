import torch

from common import loss_decreased
from rl_reinforce import GridWorld, discounted_returns, run


def test_returns_and_env():
    assert torch.allclose(discounted_returns([0.0, 0.0, 1.0], 0.9), torch.tensor([0.81, 0.9, 1.0]))
    env = GridWorld(5)
    env.reset()
    s, r, done = env.step(0)  # up from the corner: wall, stay
    assert s == 0 and r == env.step_penalty and not done


def test_reinforce_improves_return():
    out = run(episodes=150)
    assert loss_decreased(out["losses"])
    assert out["success_rate"] > 0.5
