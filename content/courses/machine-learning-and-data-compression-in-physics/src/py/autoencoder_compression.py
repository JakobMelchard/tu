"""Autoencoders vs PCA as compressors of 2D Ising snapshots.

Note 04 (autoencoders and learned compression).
- Linear autoencoder trained on squared error reaches the PCA subspace
  (Baldi-Hornik [S31]): `LinearAE` should match `lowrank.pca` at equal k.
- Nonlinear AE (tanh MLP) with the same bottleneck k (`MLPAE`).
- VAE with Gaussian encoder, reparameterisation and beta-weighted KL [S21]
  (`VAE`); KL/N is the rate in nats per spin, MSE the distortion (note 04, rate-distortion).
- Uniform latent quantisation to b bits gives an explicit rate k b / N bits per
  spin (`quantise`).
- Data 1: `ising_snapshots.sample_ising`, 12 temperatures across T_c. PCA's first
  component is the magnetisation [S22]. Result: the MLP-AE does NOT beat PCA here
  (high-T snapshots are incompressible noise, the conditional mean given m is
  linear in m, and 900 samples let the MLP memorise).
- Data 2: single-pole Green's functions G(tau; e) = -K(tau, e), a one-parameter
  nonlinear curve in R^64 (`pole_dataset`). A k = 1 MLP-AE beats k = 1 PCA by two
  orders of magnitude; PCA needs k ~ 5 (the family's singular values decay
  exponentially, the mechanism behind the IR basis, note 03).

Run `python autoencoder_compression.py` (about 20 s on a laptop CPU).
"""
from __future__ import annotations

import numpy as np
import torch
from torch import nn

from ir_toy import logistic_kernel
from ising_snapshots import T_C, magnetisation, sample_ising
from lowrank import pca, pca_encode, pca_reconstruct


def ising_dataset(L: int = 12, n_per_T: int = 100, seed: int = 0):
    """(X_train, X_test, T_train, T_test) with X in {-1, +1}^(L*L), random 75/25 split."""
    temps = np.linspace(1.5, 3.5, 12)
    s, T = sample_ising(L, temps, n_per_T, n_therm=400, rng=np.random.default_rng(seed))
    X = s.reshape(len(s), -1).astype(np.float32)
    perm = np.random.default_rng(seed + 1).permutation(len(X))
    cut = int(0.75 * len(X))
    tr, te = perm[:cut], perm[cut:]
    return X[tr], X[te], T[tr], T[te]


def pole_dataset(n: int, beta: float = 10.0, emax: float = 5.0, ntau: int = 64, seed: int = 0):
    """Rows G(tau_i; e) = -K(tau_i, e), e ~ U[-emax, emax]; returns (X float32, e)."""
    e = np.random.default_rng(seed).uniform(-emax, emax, n)
    tau = np.linspace(0, beta, ntau)
    return (-logistic_kernel(tau, e, beta).T).astype(np.float32), e


class LinearAE(nn.Module):
    def __init__(self, n: int, k: int):
        super().__init__()
        self.enc, self.dec = nn.Linear(n, k), nn.Linear(k, n)

    def encode(self, x):
        return self.enc(x)

    def forward(self, x):
        return self.dec(self.enc(x))


class MLPAE(nn.Module):
    """n -> h -> k -> h -> n, tanh everywhere; output in (-1, 1) like the spins."""

    def __init__(self, n: int, k: int, h: int = 64):
        super().__init__()
        self.enc = nn.Sequential(nn.Linear(n, h), nn.Tanh(), nn.Linear(h, k))
        self.dec = nn.Sequential(nn.Linear(k, h), nn.Tanh(), nn.Linear(h, n), nn.Tanh())

    def encode(self, x):
        return self.enc(x)

    def forward(self, x):
        return self.dec(self.enc(x))


class VAE(nn.Module):
    """q(z|x) = N(mu(x), diag sigma^2(x)), p(z) = N(0, 1), Gaussian decoder mean.

    loss = ||x - dec(z)||^2 / (2 s2) + beta KL(q || p),  z = mu + sigma * xi  [S21].
    """

    def __init__(self, n: int, k: int, h: int = 64, beta: float = 1.0, s2: float = 0.1):
        super().__init__()
        self.body = nn.Sequential(nn.Linear(n, h), nn.Tanh())
        self.mu, self.logvar = nn.Linear(h, k), nn.Linear(h, k)
        self.dec = nn.Sequential(nn.Linear(k, h), nn.Tanh(), nn.Linear(h, n), nn.Tanh())
        self.beta, self.s2 = beta, s2

    def encode(self, x):
        return self.mu(self.body(x))

    def forward(self, x):
        return self.dec(self.encode(x))          # deterministic reconstruction at z = mu

    def loss(self, x):
        hdn = self.body(x)
        mu, logvar = self.mu(hdn), self.logvar(hdn)
        z = mu + torch.exp(0.5 * logvar) * torch.randn_like(mu)
        rec = ((self.dec(z) - x) ** 2).sum(1).mean() / (2 * self.s2)
        kl = 0.5 * (mu ** 2 + logvar.exp() - 1 - logvar).sum(1).mean()
        return rec + self.beta * kl, kl


def train(model: nn.Module, X: np.ndarray, steps: int = 1500, lr: float = 3e-3,
          batch: int = 256, seed: int = 0, weight_decay: float = 0.0) -> list[float]:
    """AdamW on mini-batches (weight_decay = 0 is plain Adam); returns the loss history.

    The model's parameters are re-initialised from `seed` so runs are reproducible.
    """
    torch.manual_seed(seed)
    for mod in model.modules():
        if isinstance(mod, nn.Linear):
            mod.reset_parameters()
    Xt = torch.from_numpy(X)
    opt = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=weight_decay)
    g = torch.Generator().manual_seed(seed)
    hist = []
    for _ in range(steps):
        idx = torch.randint(len(Xt), (batch,), generator=g)
        xb = Xt[idx]
        loss = model.loss(xb)[0] if isinstance(model, VAE) else ((model(xb) - xb) ** 2).mean()
        opt.zero_grad()
        loss.backward()
        opt.step()
        hist.append(loss.item())
    return hist


@torch.no_grad()
def ae_encode(model: nn.Module, X: np.ndarray) -> np.ndarray:
    return model.encode(torch.from_numpy(X)).numpy()


@torch.no_grad()
def ae_decode(model: nn.Module, Z: np.ndarray) -> np.ndarray:
    return model.dec(torch.from_numpy(Z.astype(np.float32))).numpy()


@torch.no_grad()
def vae_kl_per_spin(model: VAE, X: np.ndarray) -> float:
    """Average KL(q(z|x) || p(z)) / N in nats: the VAE's rate."""
    hdn = model.body(torch.from_numpy(X))
    mu, logvar = model.mu(hdn), model.logvar(hdn)
    return float(0.5 * (mu ** 2 + logvar.exp() - 1 - logvar).sum(1).mean()) / X.shape[1]


def mse(X: np.ndarray, R: np.ndarray) -> float:
    return float(np.mean((X - R) ** 2))


def spin_error_rate(X: np.ndarray, R: np.ndarray) -> float:
    """Fraction of spins whose sign is wrong after decoding."""
    return float(np.mean(np.sign(R) != X))


def quantise(Z: np.ndarray, bits: int, lo: np.ndarray, hi: np.ndarray) -> np.ndarray:
    """Uniform b-bit quantiser per latent dimension on [lo, hi] (mid-rise levels)."""
    q = 2 ** bits
    idx = np.clip(np.floor((Z - lo) / (hi - lo) * q), 0, q - 1)
    return lo + (idx + 0.5) * (hi - lo) / q


def compare(k: int, Xtr, Xte, steps: int = 1500) -> dict:
    """Test-set MSE and spin error of PCA, linear AE and MLP AE at bottleneck k."""
    mu, comps, _, _ = pca(Xtr.astype(np.float64), k)
    Rp = pca_reconstruct(Xte, mu, comps)
    lin, mlp = LinearAE(Xtr.shape[1], k), MLPAE(Xtr.shape[1], k)
    train(lin, Xtr, steps, lr=1e-2)
    train(mlp, Xtr, steps)
    with torch.no_grad():
        Rl, Rm = lin(torch.from_numpy(Xte)).numpy(), mlp(torch.from_numpy(Xte)).numpy()
        Rm_tr = mlp(torch.from_numpy(Xtr)).numpy()
    return {"pca": (mse(Xte, Rp), spin_error_rate(Xte, Rp)),
            "linear_ae": (mse(Xte, Rl), spin_error_rate(Xte, Rl)),
            "mlp_ae": (mse(Xte, Rm), spin_error_rate(Xte, Rm)),
            "mlp_ae_train": mse(Xtr, Rm_tr), "mlp": mlp}


def compare_poles(k: int = 1, steps: int = 3000) -> dict:
    """Test MSE of PCA(k) and MLP-AE(k) on single-pole Green's functions."""
    Xtr, _ = pole_dataset(1500, seed=0)
    Xte, _ = pole_dataset(500, seed=1)
    mu, comps, _, _ = pca(Xtr.astype(np.float64), k)
    mlp = MLPAE(Xtr.shape[1], k)
    train(mlp, Xtr, steps)
    with torch.no_grad():
        Rm = mlp(torch.from_numpy(Xte)).numpy()
    return {"pca": mse(Xte, pca_reconstruct(Xte, mu, comps)), "mlp_ae": mse(Xte, Rm),
            "pca_by_k": {j: mse(Xte, pca_reconstruct(Xte, *pca(Xtr.astype(np.float64), j)[:2]))
                         for j in range(1, 9)}}


def demo() -> None:
    torch.set_num_threads(1)
    Xtr, Xte, Ttr, Tte = ising_dataset()
    N = Xtr.shape[1]
    print(f"Ising 12x12, {len(Xtr)} train / {len(Xte)} test snapshots, T in [1.5, 3.5], T_c = {T_C:.3f}")
    mu, comps, var, ratio = pca(Xtr.astype(np.float64), 4)
    z1 = pca_encode(Xte, mu, comps)[:, 0]
    print(f"PCA explained variance ratio (first 4): {np.round(ratio, 3)}; "
          f"corr(PC1, m) on test = {np.corrcoef(z1, magnetisation(Xte.reshape(-1, 12, 12)))[0, 1]:+.3f}")
    print(f"\n{'k':>3} {'PCA mse':>9} {'linAE mse':>10} {'MLP-AE mse':>11} {'(train)':>8} "
          f"{'PCA err':>8} {'MLP err':>8}")
    for k in (1, 2, 4, 8):
        r = compare(k, Xtr, Xte)
        print(f"{k:3d} {r['pca'][0]:9.4f} {r['linear_ae'][0]:10.4f} {r['mlp_ae'][0]:11.4f} "
              f"{r['mlp_ae_train']:8.4f} {r['pca'][1]:8.3f} {r['mlp_ae'][1]:8.3f}")
    print("(test mse per spin, spins are +-1; 'err' = fraction of wrongly decoded spins)")
    print("MLP-AE train << test: it memorises; PCA is the better compressor of Ising snapshots.")
    rp = compare_poles(1)
    print(f"\nsingle-pole G(tau; e), 64 tau points, k = 1: PCA mse {rp['pca']:.2e}, "
          f"MLP-AE mse {rp['mlp_ae']:.2e}")
    print("  PCA mse by k:", " ".join(f"{j}:{v:.1e}" for j, v in rp["pca_by_k"].items()))
    r = compare(2, Xtr, Xte)
    mlp = r["mlp"]
    Ztr, Zte = ae_encode(mlp, Xtr), ae_encode(mlp, Xte)
    print("\nrate-distortion of the k=2 MLP-AE via latent quantisation (raw data: 1 bit/spin):")
    for b in (1, 2, 4, 8):
        R = ae_decode(mlp, quantise(Zte, b, Ztr.min(0), Ztr.max(0)))
        print(f"  {b} bits/latent -> rate {2 * b / N:.4f} bits/spin, mse {mse(Xte, R):.4f}")
    print("\nVAE, k=2: larger beta lowers the rate (KL, nats/spin); mse does not rise here because\n"
          "the extra rate at small beta is spent on memorising training noise:")
    for beta in (0.1, 1.0, 10.0):
        v = VAE(N, 2, beta=beta)
        train(v, Xtr, 1500)
        with torch.no_grad():
            Rv = v(torch.from_numpy(Xte)).numpy()
        print(f"  beta = {beta:5.1f}: rate {vae_kl_per_spin(v, Xte):.4f} nats/spin, mse {mse(Xte, Rv):.4f}")


if __name__ == "__main__":
    demo()
