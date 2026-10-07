"""Autoencoders: linear AE = PCA subspace; non-linear and denoising AEs in torch.

Note 08.
  Linear AE x -> z = E x -> x' = D z with loss ||X - X E^T D^T||_F^2 (centred X). Every
  local minimum spans the top-r principal subspace (Baldi-Hornik [S28]); by Eckart-Young
  [S29] no rank-r map does better, so the optimum error equals sum_{k>=r} s_k^2.
  The AE learns the subspace, not the ordered orthonormal axes: D is determined only
  up to an invertible r x r mixing.
  Non-linear AE: a curved one-dimensional manifold needs r = 1 non-linearly but r = 2
  linearly; the AE wins on it, PCA cannot.
  Denoising AE [S36]: train on (x + noise) -> x; the map learns to project onto the data
  manifold.
"""
from __future__ import annotations

import numpy as np
import torch
from torch import nn

import clustering_pca as cp


def linear_ae_numpy(X, r, eta=1e-2, steps=4000, seed=0):
    """Untied linear AE by full-batch GD on the mean squared reconstruction error."""
    rng = np.random.default_rng(seed)
    N, d = X.shape
    E = 0.1 * rng.normal(size=(r, d))
    D = 0.1 * rng.normal(size=(d, r))
    for _ in range(steps):
        Z = X @ E.T
        R = Z @ D.T - X                      # residual N x d
        gD = 2.0 / N * R.T @ Z
        gE = 2.0 / N * (R @ D).T @ X
        D -= eta * gD
        E -= eta * gE
    return E, D, float(np.mean(np.sum((X @ E.T @ D.T - X) ** 2, 1)))


def curve_data(n=600, d=6, noise=0.02, seed=0):
    """Points on a 3/4 circle arc (1-D manifold) embedded isometrically in R^d."""
    rng = np.random.default_rng(seed)
    t = rng.uniform(0, 1.5 * np.pi, n)
    Y = np.c_[np.cos(t), np.sin(t), np.zeros((n, d - 2))]
    Q = np.linalg.qr(rng.normal(size=(d, d)))[0]
    return (Y @ Q.T + noise * rng.normal(size=(n, d))).astype(np.float32), t


class AE(nn.Module):
    def __init__(self, d, r, h=32):
        super().__init__()
        self.enc = nn.Sequential(nn.Linear(d, h), nn.Tanh(), nn.Linear(h, h), nn.Tanh(),
                                 nn.Linear(h, r))
        self.dec = nn.Sequential(nn.Linear(r, h), nn.Tanh(), nn.Linear(h, h), nn.Tanh(),
                                 nn.Linear(h, d))

    def forward(self, x):
        return self.dec(self.enc(x))


def train_ae(X, r, steps=2500, lr=3e-3, noise=0.0, seed=0, h=32):
    """Full-batch Adam; with noise > 0 the input is corrupted, the target is clean."""
    torch.manual_seed(seed)
    torch.set_num_threads(1)
    x = torch.as_tensor(X)
    model = AE(X.shape[1], r, h)
    opt = torch.optim.Adam(model.parameters(), lr=lr)
    g = torch.Generator().manual_seed(seed)
    for _ in range(steps):
        inp = x + noise * torch.randn(x.shape, generator=g) if noise > 0 else x
        loss = ((model(inp) - x) ** 2).sum(1).mean()
        opt.zero_grad()
        loss.backward()
        opt.step()
    return model


def mse(A, B) -> float:
    return float(np.mean(np.sum((np.asarray(A) - np.asarray(B)) ** 2, 1)))


def pca_reconstruction_mse(X, r) -> float:
    mean, comps, _, scores = cp.pca(X, r)
    return mse(X, mean + scores @ comps)


def _demo() -> None:
    rng = np.random.default_rng(4711)
    Z = rng.normal(size=(400, 5)) * [3.0, 2.0, 1.0, 0.3, 0.1]
    Q = np.linalg.qr(rng.normal(size=(5, 5)))[0]
    X = Z @ Q.T
    X -= X.mean(0)
    E, D, err = linear_ae_numpy(X, 2)
    _, comps, _, _ = cp.pca(X, 2)
    s = np.linalg.svd(X, compute_uv=False)
    print(f"linear AE r = 2: MSE {err:.4f}, Eckart-Young optimum {np.sum(s[2:]**2)/400:.4f}, "
          f"sin(largest principal angle) to PCA subspace {cp.subspace_distance(D.T, comps):.2e}")
    print(f"  PCA axes in the decoder basis, V_r D = {np.round(comps @ D, 3).tolist()}: "
          "a rotation, not the identity (subspace yes, ordered axes no)")
    Xc, _ = curve_data()
    for r in [1, 2]:
        print(f"arc in R^6, PCA r = {r}: reconstruction MSE {pca_reconstruction_mse(Xc, r):.4f}")
    model = train_ae(Xc, 1)
    with torch.no_grad():
        rec = model(torch.as_tensor(Xc)).numpy()
    print(f"arc in R^6, non-linear AE r = 1: reconstruction MSE {mse(Xc, rec):.4f}")
    sig = 0.15
    Xn = Xc + sig * np.random.default_rng(1).normal(size=Xc.shape).astype(np.float32)
    dae = train_ae(Xc, 1, noise=sig, seed=1)
    with torch.no_grad():
        den = dae(torch.as_tensor(Xn)).numpy()
    print(f"denoising AE, noise sigma {sig}: MSE(noisy, clean) {mse(Xn, Xc):.4f} -> "
          f"MSE(denoised, clean) {mse(den, Xc):.4f}")


if __name__ == "__main__":
    _demo()
