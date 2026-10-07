import torch
from torch.distributions import Normal, kl_divergence

from autoencoder_vae import kl_diag_gaussian, run
from common import loss_decreased


def test_kl_matches_torch():
    mu, logvar = torch.randn(4, 3), torch.randn(4, 3)
    ref = kl_divergence(Normal(mu, (0.5 * logvar).exp()), Normal(0.0, 1.0)).sum(-1)
    assert torch.allclose(kl_diag_gaussian(mu, logvar), ref, atol=1e-5)


def test_ae_and_vae_train():
    for kind in ("ae", "vae"):
        out = run(steps=100, kind=kind, n_train=1000)
        assert loss_decreased(out["losses"]), kind
        assert out["recon_error"] < 0.2
