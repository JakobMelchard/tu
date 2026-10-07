"""Tests for backprop_scratch.py: every hand-written gradient against torch.autograd."""
import numpy as np
import torch
import torch.nn.functional as F

from backprop_scratch import (conv2d_backward, conv2d_forward, exam_graph, maxpool_backward,
                              maxpool_forward, mlp_forward, mlp_loss_and_grads, init_mlp,
                              numerical_grad, train_mlp)


def test_scalar_graph_gate_patterns():
    f, xs = exam_graph(3, 4, 5, 6)
    assert f.value == 102.0
    assert [n.grad for n in xs] == [24.0, 18.0, 6.0, 17.0]
    t = torch.tensor([3.0, 4.0, 5.0, 6.0], requires_grad=True)
    ((t[0] * t[1] + t[2]) * torch.maximum(t[1], t[3])).backward()
    assert np.allclose(t.grad.numpy(), [24, 18, 6, 17])


def test_mlp_grads_match_autograd():
    rng = np.random.default_rng(1)
    X, y = rng.normal(size=(7, 4)), rng.integers(0, 3, 7)
    P = init_mlp(4, 5, 3, rng)
    loss, g = mlp_loss_and_grads(P, X, y)
    T = {k: torch.tensor(v, requires_grad=True) for k, v in P.items()}
    h = torch.relu(torch.tensor(X) @ T["W1"] + T["b1"])
    tl = F.cross_entropy(h @ T["W2"] + T["b2"], torch.tensor(y))
    tl.backward()
    assert np.isclose(loss, tl.item())
    for k in P:
        assert np.allclose(g[k], T[k].grad.numpy(), atol=1e-10), k


def test_mlp_grads_match_finite_differences():
    rng = np.random.default_rng(2)
    X, y = rng.normal(size=(5, 3)), rng.integers(0, 2, 5)
    P = init_mlp(3, 4, 2, rng)
    _, g = mlp_loss_and_grads(P, X, y)
    for k in P:
        num = numerical_grad(lambda: mlp_loss_and_grads(P, X, y)[0], P[k])
        assert np.allclose(g[k], num, atol=1e-6), k


def test_mlp_learns_xor():
    rng = np.random.default_rng(0)
    X = rng.normal(size=(200, 2))
    y = (X[:, 0] * X[:, 1] > 0).astype(int)
    P, losses = train_mlp(X, y)
    assert losses[-1] < 0.2 * losses[0]
    assert (mlp_forward(P, X)[0].argmax(1) == y).mean() > 0.95


def _check_conv(stride, pad, shape=(2, 3, 7, 6), F_=4, k=3, seed=0):
    rng = np.random.default_rng(seed)
    x, w, b = rng.normal(size=shape), rng.normal(size=(F_, shape[1], k, k)), rng.normal(size=F_)
    y, cache = conv2d_forward(x, w, b, stride, pad)
    dy = rng.normal(size=y.shape)
    dx, dw, db = conv2d_backward(dy, cache)
    tx, tw, tb = (torch.tensor(a, requires_grad=True) for a in (x, w, b))
    ty = F.conv2d(tx, tw, tb, stride=stride, padding=pad)
    (ty * torch.tensor(dy)).sum().backward()
    assert np.allclose(y, ty.detach().numpy())
    assert np.allclose(dx, tx.grad.numpy())
    assert np.allclose(dw, tw.grad.numpy())
    assert np.allclose(db, tb.grad.numpy())


def test_conv_forward_backward_match_torch():
    for s, p in [(1, 0), (1, 1), (2, 0), (2, 1), (3, 2)]:
        _check_conv(s, p)
    _check_conv(1, 2, shape=(1, 1, 5, 5), F_=1, k=5)


def test_conv_input_gradient_is_transposed_conv():
    """dL/dx of a stride-2 conv equals conv_transpose2d(dy, w): the adjoint (note 04)."""
    rng = np.random.default_rng(3)
    x, w = rng.normal(size=(1, 2, 9, 9)), rng.normal(size=(3, 2, 3, 3))
    y, cache = conv2d_forward(x, w, np.zeros(3), stride=2, pad=1)
    dy = rng.normal(size=y.shape)
    dx, _, _ = conv2d_backward(dy, cache)
    ref = F.conv_transpose2d(torch.tensor(dy), torch.tensor(w), stride=2, padding=1, output_padding=0)
    assert np.allclose(dx, ref.numpy())


def test_maxpool_routes_gradient_to_argmax():
    x = np.array([[1, 1, 2, 4], [5, 6, 7, 8], [3, 2, 1, 0], [1, 2, 3, 4]], float)[None, None]
    y, cache = maxpool_forward(x)
    assert y[0, 0].tolist() == [[6, 8], [3, 4]]          # the 2017 catalogue input [S9]
    dx = maxpool_backward(np.ones_like(y), cache)
    assert dx.sum() == 4 and dx[0, 0, 1, 1] == 1 and dx[0, 0, 1, 3] == 1
    tx = torch.tensor(x, requires_grad=True)
    F.max_pool2d(tx, 2).sum().backward()
    assert np.allclose(dx, tx.grad.numpy())
