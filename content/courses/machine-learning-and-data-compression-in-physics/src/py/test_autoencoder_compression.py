import numpy as np
import pytest
import torch

from autoencoder_compression import (VAE, LinearAE, MLPAE, compare_poles, ising_dataset, mse,
                                     quantise, train, vae_kl_per_spin)
from ising_snapshots import magnetisation
from lowrank import pca, pca_encode, pca_reconstruct

torch.set_num_threads(1)


@pytest.fixture(scope="module")
def data():
    return ising_dataset(L=10, n_per_T=50, seed=3)


def test_first_principal_component_is_the_magnetisation(data):
    Xtr, Xte, _, _ = data
    mu, comps, _, ratio = pca(Xtr.astype(np.float64), 2)
    z = pca_encode(Xte, mu, comps)[:, 0]
    assert abs(np.corrcoef(z, magnetisation(Xte.reshape(-1, 10, 10)))[0, 1]) > 0.99
    assert ratio[0] > 5 * ratio[1]            # one dominant direction: the order parameter


def test_linear_autoencoder_reaches_pca(data):
    """Baldi-Hornik: the global minima of the linear AE span the PCA subspace."""
    Xtr, _, _, _ = data
    k = 3
    mu, comps, _, _ = pca(Xtr.astype(np.float64), k)
    e_pca = mse(Xtr, pca_reconstruct(Xtr, mu, comps))
    lin = LinearAE(Xtr.shape[1], k)
    train(lin, Xtr, 2000, lr=1e-2)
    with torch.no_grad():
        e_lin = mse(Xtr, lin(torch.from_numpy(Xtr)).numpy())
    assert e_pca <= e_lin + 1e-6                # PCA is optimal on the training set
    assert e_lin < 1.03 * e_pca


def test_nonlinear_ae_wins_on_a_nonlinear_one_parameter_family():
    r = compare_poles(k=1, steps=2000)
    assert r["mlp_ae"] < 0.05 * r["pca"]
    assert r["pca_by_k"][5] < r["pca_by_k"][1] / 100      # PCA needs ~5 components


def test_quantiser_error_and_monotone_distortion():
    rng = np.random.default_rng(0)
    Z = rng.uniform(-2, 3, (500, 2))
    lo, hi = Z.min(0), Z.max(0)
    errs = []
    for b in (1, 2, 4, 8):
        Q = quantise(Z, b, lo, hi)
        assert np.all(np.abs(Q - Z) <= (hi - lo) / 2 ** (b + 1) + 1e-12)
        errs.append(np.mean((Q - Z) ** 2))
    assert np.all(np.diff(errs) < 0)
    # uniform source: mse = Delta^2 / 12 (the 6 dB per bit rule)
    D = (hi - lo) / 2 ** 8
    assert np.allclose(np.mean((quantise(Z, 8, lo, hi) - Z) ** 2, axis=0), D ** 2 / 12, rtol=0.2)


def test_vae_beta_controls_rate(data):
    Xtr, Xte, _, _ = data
    rates = []
    for beta in (0.1, 10.0):
        v = VAE(Xtr.shape[1], 2, beta=beta)
        hist = train(v, Xtr, 800)
        assert np.mean(hist[-50:]) < np.mean(hist[:50])
        rates.append(vae_kl_per_spin(v, Xte))
    assert rates[1] < rates[0]
    assert rates[1] > 0


def test_mlp_ae_output_is_bounded(data):
    Xtr, Xte, _, _ = data
    m = MLPAE(Xtr.shape[1], 2)
    train(m, Xtr, 100)
    with torch.no_grad():
        R = m(torch.from_numpy(Xte)).numpy()
    assert np.all(np.abs(R) < 1)
