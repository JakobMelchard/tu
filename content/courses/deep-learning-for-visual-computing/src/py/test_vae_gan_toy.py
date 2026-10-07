"""Tests for vae_gan_toy.py: KL closed form, ELBO decrease, GAN identities, DDPM closed form."""
import numpy as np
import pytest
import torch

from vae_gan_toy import (VAE, alpha_bar, gan_steps, gan_value, gauss_pdf, generator_loss_grads,
                         js_divergence_1d, kl_gauss, kl_monte_carlo, make_bars, neg_elbo,
                         optimal_discriminator, q_iterate, q_sample, train_vae,
                         value_at_optimal_d)


def test_bars_data():
    X = make_bars(100, seed=1)
    assert X.shape == (100, 64) and set(X.unique().tolist()) <= {0.0, 1.0}
    assert (X.sum(1) >= 8).all()                          # at least one full bar


def test_kl_closed_form_worked_example_and_monte_carlo():
    mu, lv = torch.tensor([0.0, 1.0, -0.5], dtype=torch.float64), torch.tensor([0.0, 0.0, np.log(0.25)], dtype=torch.float64)
    assert kl_gauss(mu, lv).item() == pytest.approx(0.5 * (0 + 1 + 0.25 + 0.25 - np.log(0.25) - 1), abs=1e-12)
    assert kl_gauss(mu, lv).item() == pytest.approx(0.943, abs=5e-4)
    assert kl_monte_carlo(mu, lv).item() == pytest.approx(kl_gauss(mu, lv).item(), abs=0.01)
    assert kl_gauss(torch.zeros(3), torch.zeros(3)).item() == 0


def test_neg_elbo_is_reconstruction_plus_kl():
    torch.manual_seed(0)
    x = make_bars(8)
    m = VAE()
    logits, mu, lv = m(x)
    a, b = neg_elbo(logits, x, mu, lv, beta=0.0), neg_elbo(logits, x, mu, lv, beta=1.0)
    assert (b - a).item() == pytest.approx(kl_gauss(mu, lv).mean().item(), abs=1e-5)   # float32 cancellation


def test_vae_elbo_decreases():
    _, hist = train_vae(steps=300)
    assert np.mean(hist[-20:]) < 0.7 * np.mean(hist[:20])


def test_optimal_discriminator_and_js_identity():
    pd, pg = (lambda x: gauss_pdf(x, 0, 1)), (lambda x: gauss_pdf(x, 2, 1))
    assert optimal_discriminator(np.array([1.0]), pd, pg)[0] == pytest.approx(0.5)   # midpoint
    assert value_at_optimal_d(pd, pg) == pytest.approx(-np.log(4) + 2 * js_divergence_1d(pd, pg), abs=1e-8)
    assert value_at_optimal_d(pd, pd) == pytest.approx(-np.log(4), abs=1e-8)
    far = lambda x: gauss_pdf(x, 12, 0.5)
    assert js_divergence_1d(pd, far) == pytest.approx(np.log(2), abs=1e-6)          # saturates


def test_gan_value_monte_carlo_matches_quadrature():
    rng = np.random.default_rng(0)
    pd, pg = (lambda x: gauss_pdf(x, 0, 1)), (lambda x: gauss_pdf(x, 1, 1))
    xr, xf = rng.normal(0, 1, 400_000), rng.normal(1, 1, 400_000)
    v = gan_value(optimal_discriminator(xr, pd, pg), optimal_discriminator(xf, pd, pg))
    assert v == pytest.approx(value_at_optimal_d(pd, pg), abs=5e-3)


def test_saturating_vs_non_saturating_gradient():
    a = np.array([-8.0, -2.0, 0.0, 2.0])
    g1, g2 = generator_loss_grads(a)
    s = 1 / (1 + np.exp(-a))
    assert np.allclose(g1, -s) and np.allclose(g2, -(1 - s))
    assert abs(g1[0]) < 1e-3 and abs(g2[0]) > 0.99          # D rejects the sample


def test_gan_steps_run_and_stay_finite():
    h = np.array(gan_steps(steps=10))
    assert h.shape == (10, 2) and np.isfinite(h).all()


def test_ddpm_closed_form_matches_chain():
    rng = np.random.default_rng(0)
    ab = alpha_bar()
    assert ab[-1] < 1e-4 and np.all(np.diff(ab) < 0)
    x0 = np.full(20_000, 1.5)
    xs, xc = q_sample(x0, 100, ab, rng), q_iterate(x0, 100, rng=rng)
    for x in (xs, xc):
        assert x.mean() == pytest.approx(np.sqrt(ab[99]) * 1.5, abs=0.02)
        assert x.var() == pytest.approx(1 - ab[99], abs=0.02)
