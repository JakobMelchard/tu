import math

import numpy as np
import pytest
import torch

from dense_retrieval import (BiEncoder, IVFIndex, LSHIndex, ann_recall, brute_force, dense_experiment,
                             in_batch_loss, margin_mse)


def _data(n=4000, d=16, seed=0):
    rng = np.random.default_rng(seed)
    centres = rng.normal(size=(30, d))
    X = centres[rng.integers(30, size=n)] + 0.4 * rng.normal(size=(n, d))
    X /= np.linalg.norm(X, axis=1, keepdims=True)
    Q = X[rng.choice(n, 50, replace=False)] + 0.05 * rng.normal(size=(50, d))
    return X, Q, rng


def test_in_batch_loss_is_cross_entropy_on_the_diagonal():
    torch.manual_seed(0)
    q, p = F_norm(torch.randn(5, 8)), F_norm(torch.randn(7, 8))          # 2 extra hard negatives
    S = q @ p.T / 0.05
    manual = -torch.stack([S[i, i] - torch.logsumexp(S[i], 0) for i in range(5)]).mean()
    assert torch.allclose(in_batch_loss(q, p), manual)
    # a perfect encoder (q_i = p_i, orthogonal rows) drives the loss to ~0
    eye = torch.eye(4)
    assert in_batch_loss(eye, eye).item() < 1e-6


def F_norm(x):
    return x / x.norm(dim=-1, keepdim=True)


def test_bi_encoder_masked_mean_pooling():
    m = BiEncoder(20, dim=4, out=3, normalise=False)
    a = m(torch.tensor([[5, 6, 0, 0]]))
    b = m(torch.tensor([[6, 5]]))
    assert torch.allclose(a, b, atol=1e-6)                                  # order- and padding-invariant
    assert torch.allclose(BiEncoder(20)(torch.tensor([[3, 4]])).norm(), torch.tensor(1.0))


def test_brute_force_matches_full_sort():
    X, Q, _ = _data()
    ref = np.argsort(-(Q @ X.T), axis=1, kind="stable")[:, :10]
    assert np.array_equal(brute_force(Q, X, 10), ref)


def test_ivf_exact_when_probing_all_lists_and_recall_grows_with_nprobe():
    X, Q, rng = _data()
    exact = brute_force(Q, X, 10)
    ivf = IVFIndex(X, nlist=16, rng=rng)
    full, work = ivf.search(Q, 10, nprobe=16)
    assert np.array_equal(full, exact) and work == pytest.approx(1.0)
    rec = [ann_recall(ivf.search(Q, 10, n)[0], exact) for n in (1, 2, 4, 8)]
    assert rec == sorted(rec) and rec[2] > 0.9
    assert ivf.search(Q, 10, 2)[1] < 0.3


def test_lsh_collision_probability_and_recall():
    rng = np.random.default_rng(3)
    x, y = rng.normal(size=16), rng.normal(size=16)
    theta = math.acos(x @ y / np.linalg.norm(x) / np.linalg.norm(y))
    H = rng.normal(size=(200000, 16))
    same = np.mean(((H @ x) > 0) == ((H @ y) > 0))
    assert same == pytest.approx(1 - theta / math.pi, abs=0.005)
    X, Q, rng = _data()
    exact = brute_force(Q, X, 10)
    a4, _ = LSHIndex(X, 8, 4, rng).search(Q, 10)
    a16, w16 = LSHIndex(X, 8, 16, rng).search(Q, 10)
    assert ann_recall(a16, exact) > ann_recall(a4, exact) and ann_recall(a16, exact) > 0.9 and w16 < 0.5


def test_trained_bi_encoder_beats_untrained_and_bm25_recall():
    r_bm, r_0, r_1, hist = dense_experiment(steps=400, seed=0)
    assert np.mean(hist[-20:]) < 0.5 * np.mean(hist[:20])
    assert r_1 > r_0 + 0.3 and r_1 > r_bm


def test_margin_mse_shift_invariance():
    s_p, s_n = torch.tensor([2.0, 0.5]), torch.tensor([1.0, 0.7])
    t_p, t_n = torch.tensor([9.0, 3.0]), torch.tensor([8.0, 3.2])      # same margins (1, -0.2), other scale
    assert margin_mse(s_p, s_n, t_p, t_n).item() == pytest.approx(0.0)
    assert margin_mse(s_p + 5, s_n + 5, t_p, t_n).item() == pytest.approx(0.0)
    assert margin_mse(s_p, s_n, t_p + 1, t_n).item() == pytest.approx(1.0)
