"""GAN on a 2D toy distribution: 8 Gaussians on a ring.

Discriminator D: R^2 -> logit of "real".  Generator G: N(0, I_2) -> R^2.
Non-saturating losses (Goodfellow et al. 2014):
    L_D = BCE(D(x), 1) + BCE(D(G(z)), 0)
    L_G = BCE(D(G(z)), 1)              (instead of  -BCE(D(G(z)), 0), which saturates)
Adversarial losses are not a training signal you can read like a supervised
loss, so progress is measured by `mode_distance`: the mean distance of a
generated sample to the nearest of the 8 true modes.
"""

from __future__ import annotations

import math

import torch
from torch import nn
from torch.nn import functional as F

from common import Timer, get_device, loss_decreased, seed_all

RADIUS, STD, N_MODES = 2.0, 0.05, 8


def modes() -> torch.Tensor:
    angles = torch.arange(N_MODES) * 2 * math.pi / N_MODES
    return RADIUS * torch.stack([angles.cos(), angles.sin()], dim=-1)  # [8, 2]


def make_ring(n: int, seed: int = 0) -> torch.Tensor:
    gen = torch.Generator().manual_seed(seed)
    k = torch.randint(0, N_MODES, (n,), generator=gen)
    return modes()[k] + STD * torch.randn(n, 2, generator=gen)


def mode_distance(samples: torch.Tensor) -> float:
    d = torch.cdist(samples, modes().to(samples.device))  # [n, 8]
    return d.min(dim=1).values.mean().item()


def modes_covered(samples: torch.Tensor, tol: float = 3 * STD) -> int:
    """Number of modes that have at least one sample within tol (mode-collapse diagnostic)."""
    d = torch.cdist(samples, modes().to(samples.device))
    return int((d.min(dim=0).values < tol).sum().item())


class Generator(nn.Module):
    def __init__(self, noise: int = 2, hidden: int = 128):
        super().__init__()
        self.noise = noise
        self.net = nn.Sequential(nn.Linear(noise, hidden), nn.ReLU(), nn.Linear(hidden, hidden), nn.ReLU(),
                                 nn.Linear(hidden, 2))

    def forward(self, z: torch.Tensor) -> torch.Tensor:
        return self.net(z)

    def sample(self, n: int, gen: torch.Generator | None = None) -> torch.Tensor:
        device = next(self.parameters()).device
        z = torch.randn(n, self.noise, generator=gen).to(device)
        return self(z)


class Discriminator(nn.Module):
    def __init__(self, hidden: int = 128):
        super().__init__()
        self.net = nn.Sequential(nn.Linear(2, hidden), nn.LeakyReLU(0.2), nn.Linear(hidden, hidden),
                                 nn.LeakyReLU(0.2), nn.Linear(hidden, 1))

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.net(x).squeeze(-1)  # logits


def run(steps: int = 600, batch: int = 128, eval_every: int = 20, n_train: int = 4000,
        device: torch.device | None = None, seed: int = 0, log_every: int = 0) -> dict:
    device = device or get_device()
    gen = seed_all(seed)
    X = make_ring(n_train, seed).to(device)
    G, D = Generator().to(device), Discriminator().to(device)
    # beta1 = 0.5 is the usual GAN choice: momentum too high makes the two-player game oscillate.
    opt_g = torch.optim.Adam(G.parameters(), lr=1e-3, betas=(0.5, 0.999))
    opt_d = torch.optim.Adam(D.parameters(), lr=1e-3, betas=(0.5, 0.999))
    ones, zeros = torch.ones(batch, device=device), torch.zeros(batch, device=device)
    d_losses, g_losses, dists = [], [], []
    with Timer() as t:
        for step in range(1, steps + 1):
            real = X[torch.randint(0, n_train, (batch,), generator=gen).to(device)]
            fake = G.sample(batch, gen)
            # discriminator step: push D(real) -> 1, D(fake) -> 0; detach so G gets no gradient here
            loss_d = F.binary_cross_entropy_with_logits(D(real), ones) + \
                F.binary_cross_entropy_with_logits(D(fake.detach()), zeros)
            opt_d.zero_grad(set_to_none=True)
            loss_d.backward()
            opt_d.step()
            # generator step (non-saturating): push D(fake) -> 1
            loss_g = F.binary_cross_entropy_with_logits(D(fake), ones)
            opt_g.zero_grad(set_to_none=True)
            loss_g.backward()
            opt_g.step()
            d_losses.append(loss_d.item())
            g_losses.append(loss_g.item())
            if step % eval_every == 0:
                with torch.no_grad():
                    dists.append(mode_distance(G.sample(1000, gen)))
                if log_every and step % log_every == 0:
                    print(f"step {step:4d}  L_D {loss_d.item():.3f}  L_G {loss_g.item():.3f}  "
                          f"mode distance {dists[-1]:.3f}")
    with torch.no_grad():
        final = G.sample(2000, gen)
    return {"losses": dists, "d_losses": d_losses, "g_losses": g_losses, "mode_distance": mode_distance(final),
            "modes_covered": modes_covered(final), "generator": G, "seconds": t.seconds}


if __name__ == "__main__":
    real = make_ring(1000)
    print(f"real data: mode distance {mode_distance(real):.3f}, modes covered {modes_covered(real)}/8")
    out = run(log_every=100)
    print(f"generated: mode distance {out['mode_distance']:.3f}, modes covered {out['modes_covered']}/8, "
          f"{out['seconds']:.1f}s, mode distance decreased {loss_decreased(out['losses'])}")
