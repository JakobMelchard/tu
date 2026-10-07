"""Tests for segmentation_losses.py: numpy against torch, identities, and a short U-Net fit."""
import numpy as np
import pytest
import torch
import torch.nn.functional as F

from cnn_synthetic import make_shapes
from segmentation_losses import (TinyUNet, confusion, dice_loss_torch, dice_score, iou_score,
                                 mean_iou, one_hot, pixel_cross_entropy, soft_dice_loss,
                                 soft_iou_loss, train_unet)


def test_pixel_cross_entropy_matches_torch():
    rng = np.random.default_rng(0)
    z, m = rng.normal(size=(2, 3, 5, 4)), rng.integers(0, 3, (2, 5, 4))
    assert pixel_cross_entropy(z, m) == pytest.approx(F.cross_entropy(torch.tensor(z), torch.tensor(m)).item())
    w = np.array([0.2, 1.0, 5.0])
    ref = F.cross_entropy(torch.tensor(z), torch.tensor(m), weight=torch.tensor(w)).item()
    assert pixel_cross_entropy(z, m, w) == pytest.approx(ref)


def test_soft_dice_matches_torch_version():
    rng = np.random.default_rng(1)
    z, m = rng.normal(size=(2, 3, 6, 6)), rng.integers(0, 3, (2, 6, 6))
    p = np.exp(z) / np.exp(z).sum(1, keepdims=True)
    ref = dice_loss_torch(torch.tensor(z), torch.tensor(m)).item()
    assert soft_dice_loss(p, one_hot(m, 3)) == pytest.approx(ref)


def test_hard_dice_iou_identity():
    rng = np.random.default_rng(2)
    for _ in range(20):
        a, b = rng.uniform(size=(10, 10)) < 0.4, rng.uniform(size=(10, 10)) < 0.4
        d, j = dice_score(a, b), iou_score(a, b)
        assert d == pytest.approx(2 * j / (1 + j))
        assert j <= d                                          # Dice >= IoU always


def test_soft_losses_on_perfect_and_disjoint_predictions():
    g = one_hot(np.array([[[0, 1], [1, 0]]]), 2)
    assert soft_dice_loss(g, g, eps=0) == pytest.approx(0)
    assert soft_iou_loss(g, g, eps=0) == pytest.approx(0)
    assert soft_dice_loss(1 - g, g, eps=0) == pytest.approx(1)
    assert soft_iou_loss(1 - g, g, eps=0) == pytest.approx(1)


def test_overlapping_squares_hand_case():
    a, b = np.zeros((8, 8), bool), np.zeros((8, 8), bool)
    a[1:5, 1:5], b[3:7, 3:7] = True, True
    assert iou_score(a, b) == pytest.approx(4 / 28)
    assert dice_score(a, b) == pytest.approx(8 / 32)


def test_imbalance_all_background_predictor():
    gt = np.zeros((1, 100, 100), int)
    gt[0, 45:55, 45:55] = 1
    probs = np.stack([np.full((100, 100), 0.99), np.full((100, 100), 0.01)])[None]
    assert pixel_cross_entropy(np.log(probs), gt) < 0.06        # CE looks fine
    assert soft_dice_loss(probs, one_hot(gt, 2)) > 0.45         # Dice exposes it
    miou, ious = mean_iou(probs.argmax(1), gt, 2)
    assert ious[1] == 0 and miou == pytest.approx(0.99 / 2)


def test_confusion_and_mean_iou():
    gt = np.array([0, 0, 1, 1, 2, 2])
    pr = np.array([0, 1, 1, 1, 2, 0])
    cm = confusion(pr, gt, 3)
    assert cm.tolist() == [[1, 1, 0], [0, 2, 0], [1, 0, 1]]
    miou, ious = mean_iou(pr, gt, 3)
    assert np.allclose(ious, [1 / 3, 2 / 3, 1 / 2])


def test_unet_shapes_and_skip_by_concatenation():
    net = TinyUNet(K=3, C=4)
    assert net(torch.zeros(2, 1, 16, 16)).shape == (2, 3, 16, 16)
    assert net.dec[0].in_channels == 2 * 4                     # up (C) + skip (C) concatenated


def test_short_unet_fit_segments_shapes():
    X, _, m = make_shapes(256, seed=0)
    Xt, _, mt = make_shapes(64, seed=1)
    net, losses = train_unet(X, m, steps=40)
    assert np.mean(losses[-5:]) < 0.5 * np.mean(losses[:5])
    net.eval()
    with torch.no_grad():
        pred = net(Xt).argmax(1).numpy()
    assert mean_iou(pred, mt.astype(int), 2)[1][1] > 0.7       # foreground IoU


def test_transposed_conv_by_hand():
    """The 2020 catalogue's transposed-convolution question [S8] with our numbers (note 05):
    2x2 input, 3x3 kernel of ones, stride 2, padding 1 -> (2-1)*2 - 2 + 3 = 3."""
    x = torch.tensor([[1.0, 2.0], [3.0, 4.0]])[None, None]
    y = F.conv_transpose2d(x, torch.ones(1, 1, 3, 3), stride=2, padding=1)
    assert y[0, 0].tolist() == [[1, 3, 2], [4, 10, 6], [3, 7, 4]]
