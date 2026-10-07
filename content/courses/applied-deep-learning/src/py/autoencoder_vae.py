"""Autoencoder and variational autoencoder on 16x16 synthetic shape images.

AE: x -> z -> x_hat, trained on reconstruction only.
VAE: q(z|x) = N(mu, diag(sigma^2)); loss = -ELBO
     = BCE(x_hat, x) + beta * KL(q(z|x) || N(0, I)),
     KL = 1/2 sum_j (mu_j^2 + sigma_j^2 - log sigma_j^2 - 1).
Sampling uses the reparameterisation z = mu + sigma * eps so that gradients
flow through mu and log sigma^2.
"""

from __future__ import annotations

import torch
from torch import nn
from torch.nn import functional as F

from cnn_shapes import make_shapes
from common import Timer, get_device, loss_decreased, seed_all, train_loop

SIZE = 16
D = SIZE * SIZE


def mlp(sizes: list[int]) -> nn.Sequential:
    layers: list[nn.Module] = []
    for a, b in zip(sizes[:-1], sizes[1:]):
        layers += [nn.Linear(a, b), nn.ReLU()]
    return nn.Sequential(*layers[:-1])  # no activation after the last linear


class AE(nn.Module):
    def __init__(self, latent: int = 8, hidden: int = 128):
        super().__init__()
        self.encoder = mlp([D, hidden, latent])
        self.decoder = mlp([latent, hidden, D])  # outputs logits, sigmoid applied in the loss

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.decoder(self.encoder(x.flatten(1)))


class VAE(nn.Module):
    def __init__(self, latent: int = 8, hidden: int = 128):
        super().__init__()
        self.latent = latent
        self.encoder = mlp([D, hidden, 2 * latent])  # outputs [mu, logvar]
        self.decoder = mlp([latent, hidden, D])

    def encode(self, x: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor]:
        mu, logvar = self.encoder(x.flatten(1)).chunk(2, dim=-1)
        return mu, logvar

    @staticmethod
    def reparameterize(mu: torch.Tensor, logvar: torch.Tensor) -> torch.Tensor:
        return mu + torch.exp(0.5 * logvar) * torch.randn_like(mu)

    def decode(self, z: torch.Tensor) -> torch.Tensor:
        return self.decoder(z)

    def forward(self, x: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        mu, logvar = self.encode(x)
        return self.decode(self.reparameterize(mu, logvar)), mu, logvar

    @torch.no_grad()
    def sample(self, n: int) -> torch.Tensor:
        z = torch.randn(n, self.latent, device=next(self.parameters()).device)
        return torch.sigmoid(self.decode(z)).view(n, 1, SIZE, SIZE)


def kl_diag_gaussian(mu: torch.Tensor, logvar: torch.Tensor) -> torch.Tensor:
    """KL(N(mu, diag(exp(logvar))) || N(0, I)) per sample, closed form."""
    return 0.5 * (mu.pow(2) + logvar.exp() - logvar - 1.0).sum(dim=-1)


def vae_loss(x_hat_logits: torch.Tensor, x: torch.Tensor, mu: torch.Tensor, logvar: torch.Tensor,
             beta: float = 1.0) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
    """Negative ELBO averaged over the batch; returns (loss, recon, kl)."""
    recon = F.binary_cross_entropy_with_logits(x_hat_logits, x.flatten(1), reduction="none").sum(-1).mean()
    kl = kl_diag_gaussian(mu, logvar).mean()
    return recon + beta * kl, recon, kl


def run(steps: int = 400, kind: str = "vae", latent: int = 8, beta: float = 1.0, batch: int = 128,
        n_train: int = 3000, device: torch.device | None = None, seed: int = 0, log_every: int = 0) -> dict:
    device = device or get_device()
    gen = seed_all(seed)
    X, _ = make_shapes(n_train, size=SIZE, seed=seed, noise=0.0)
    Xt, _ = make_shapes(500, size=SIZE, seed=seed + 1, noise=0.0)
    X = X.to(device)
    model = (VAE(latent) if kind == "vae" else AE(latent)).to(device)
    opt = torch.optim.Adam(model.parameters(), lr=2e-3)

    def step_fn() -> torch.Tensor:
        xb = X[torch.randint(0, n_train, (batch,), generator=gen).to(device)]
        if kind == "vae":
            logits, mu, logvar = model(xb)
            return vae_loss(logits, xb, mu, logvar, beta=beta)[0]
        return F.binary_cross_entropy_with_logits(model(xb), xb.flatten(1), reduction="none").sum(-1).mean()

    with Timer() as t:
        losses = train_loop(step_fn, opt, steps, log_every=log_every)
    model.eval()
    with torch.no_grad():
        xt = Xt.to(device)
        if kind == "vae":
            logits, mu, logvar = model(xt)
            kl = kl_diag_gaussian(mu, logvar).mean().item()
        else:
            logits, kl = model(xt), 0.0
        recon_error = (torch.sigmoid(logits) - xt.flatten(1)).abs().mean().item()  # mean abs pixel error
    return {"losses": losses, "recon_error": recon_error, "kl": kl, "model": model, "seconds": t.seconds}


if __name__ == "__main__":
    mu, logvar = torch.tensor([[1.0, 0.0]]), torch.tensor([[0.0, -1.0]])
    print(f"KL for mu={mu.tolist()}, logvar={logvar.tolist()}: {kl_diag_gaussian(mu, logvar).item():.4f}")
    for kind in ("ae", "vae"):
        out = run(kind=kind, log_every=100)
        print(f"{kind}: final loss {out['losses'][-1]:.1f}, test mean abs pixel error {out['recon_error']:.4f}, "
              f"KL {out['kl']:.2f} nats, {out['seconds']:.1f}s, loss decreased {loss_decreased(out['losses'])}")
    samples = out["model"].sample(4)
    print("VAE samples: 4 images of shape", tuple(samples.shape[1:]), "mean pixel", f"{samples.mean():.3f}")
