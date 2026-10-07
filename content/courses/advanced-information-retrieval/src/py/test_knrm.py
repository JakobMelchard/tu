import math

import torch

from knrm import KNRM, PAD, ConvKNRM, experiment, kernel_pooling, kernels


def test_kernel_parameters():
    mu, sigma = kernels()
    assert torch.allclose(mu, torch.tensor([1.0, 0.9, 0.7, 0.5, 0.3, 0.1, -0.1, -0.3, -0.5, -0.7, -0.9]))
    assert torch.allclose(sigma, torch.tensor([1e-3] + [0.1] * 10))


def test_kernel_pooling_hand_computed():
    # one query token, document similarities (1.0, 0.9, 0.0); two kernels: exact (mu 1) and mu 0.9
    M = torch.tensor([[[1.0, 0.9, 0.0]]])
    mu, sigma = torch.tensor([1.0, 0.9]), torch.tensor([1e-3, 0.1])
    phi = kernel_pooling(M, torch.ones(1, 3), torch.ones(1, 1), mu, sigma)
    soft_exact = 1.0                                           # only the exact match survives sigma 1e-3
    soft_09 = math.exp(-0.01 / 0.02) + 1.0 + math.exp(-0.81 / 0.02)
    assert torch.allclose(phi, 0.01 * torch.log(torch.tensor([[soft_exact, soft_09]])), atol=1e-6)


def test_padding_mask_is_applied_after_the_kernel():
    torch.manual_seed(0)
    m = KNRM(50, dim=8)
    q = torch.tensor([[3, 4]])
    d = torch.tensor([[5, 6, 7]])
    d_pad = torch.tensor([[5, 6, 7, PAD, PAD, PAD]])
    q_pad = torch.tensor([[3, 4, PAD]])
    assert torch.allclose(m(q, d), m(q_pad, d_pad), atol=1e-6)


def test_shapes_and_conv_knrm_forward():
    torch.manual_seed(0)
    q, d = torch.randint(2, 40, (4, 3)), torch.randint(2, 40, (4, 12))
    assert KNRM(40)(q, d).shape == (4,)
    ck = ConvKNRM(40, dim=8, max_n=2)
    assert ck(q, d).shape == (4,) and ck.out.in_features == 11 * 4


def test_knrm_improves_mrr_over_bm25():
    """Re-ranking BM25 top-30 of 60 held-out queries; trained in a few seconds on CPU."""
    (b_mrr, _), (k_mrr, _), hist = experiment(KNRM, steps=300, seed=0)
    assert sum(hist[-20:]) / 20 < 0.5 * sum(hist[:20]) / 20
    assert k_mrr > b_mrr + 0.05


def test_knrm_log1p_variant_improves_mrr_and_ndcg():
    (b_mrr, b_nd), (k_mrr, k_nd), _ = experiment(KNRM, steps=300, seed=1, log1p=True)
    assert k_mrr > b_mrr + 0.05 and k_nd > b_nd
