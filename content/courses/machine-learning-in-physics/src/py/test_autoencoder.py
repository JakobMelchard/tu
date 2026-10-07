"""Tests for autoencoder.py (note 08)."""
import numpy as np
import torch

import autoencoder as ae
import clustering_pca as cp


def test_linear_autoencoder_finds_the_pca_subspace():
    rng = np.random.default_rng(4711)
    Z = rng.normal(size=(400, 5)) * [3.0, 2.0, 1.0, 0.3, 0.1]
    X = Z @ np.linalg.qr(rng.normal(size=(5, 5)))[0].T
    X -= X.mean(0)
    E, D, err = ae.linear_ae_numpy(X, 2)
    _, comps, _, _ = cp.pca(X, 2)
    s = np.linalg.svd(X, compute_uv=False)
    assert cp.subspace_distance(D.T, comps) < 1e-3
    assert err == np.float64(err) and abs(err - np.sum(s[2:] ** 2) / 400) < 1e-4


def test_nonlinear_ae_beats_pca_on_a_curve():
    X, _ = ae.curve_data()
    model = ae.train_ae(X, 1, steps=1500)
    with torch.no_grad():
        rec = model(torch.as_tensor(X)).numpy()
    assert ae.mse(X, rec) < 0.1 * ae.pca_reconstruction_mse(X, 1)


def test_denoising_autoencoder_reduces_noise():
    X, _ = ae.curve_data()
    sig = 0.15
    Xn = X + sig * np.random.default_rng(1).normal(size=X.shape).astype(np.float32)
    dae = ae.train_ae(X, 1, steps=1500, noise=sig, seed=1)
    with torch.no_grad():
        den = dae(torch.as_tensor(Xn)).numpy()
    assert ae.mse(den, X) < 0.4 * ae.mse(Xn, X)
