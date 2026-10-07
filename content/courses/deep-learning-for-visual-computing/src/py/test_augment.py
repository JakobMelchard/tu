"""Tests for augment.py: algebra of the transforms, label preservation, and the
(in)variances a CNN does and does not have (note 04, note 08)."""
import pytest
import torch
import torch.nn.functional as F
from torch import nn

from augment import (GLYPHS, brightness_contrast, cutout, fit_normalizer, gaussian_noise, hflip,
                     identify_digit, mixup, normalize, random_crop, render_digit, rot90,
                     shapes_augment, translate, vflip)


def _g(seed=0):
    return torch.Generator().manual_seed(seed)


def test_group_structure_of_flips_and_rotations():
    x = torch.randn(2, 3, 5, 7, generator=_g())
    assert torch.equal(hflip(hflip(x)), x)
    assert torch.equal(rot90(x, 4), x)
    assert torch.equal(rot90(x, 2), hflip(vflip(x)))
    assert torch.equal(rot90(rot90(x, 1), 3), x)


def test_digit_flips_are_not_label_preserving():
    assert identify_digit(hflip(render_digit(2))) == 5          # a mirrored 2 is a 5
    assert identify_digit(rot90(render_digit(6), 2)) == 9       # 6 upside down is 9
    assert identify_digit(hflip(render_digit(3))) is None       # not a digit at all
    assert identify_digit(vflip(render_digit(3))) == 3
    for d in GLYPHS:                                            # small shifts are safe
        assert identify_digit(translate(translate(render_digit(d), 1, 1), -1, -1)) == d


def test_translate_zero_fill_and_crop_shapes():
    x = torch.arange(16.0).reshape(1, 1, 4, 4)
    t = translate(x, 1, 0)
    assert torch.equal(t[..., :, 1:], x[..., :, :3]) and (t[..., :, 0] == 0).all()
    c = random_crop(torch.randn(3, 32, 32, generator=_g()), 4, _g(1))
    assert c.shape == (3, 32, 32)
    assert random_crop(torch.randn(3, 8, 8, generator=_g()), 2, _g(), mode="reflect").shape == (3, 8, 8)


def test_photometric_transforms():
    x = torch.rand(4, 1, 8, 8, generator=_g())
    y = brightness_contrast(x, 0.1, 1.0)
    assert torch.allclose(y - x, torch.full_like(x, 0.1))
    z = brightness_contrast(x, 0.0, 0.5)
    assert torch.allclose(z.mean(dim=(1, 2, 3)), x.mean(dim=(1, 2, 3)), atol=1e-6)   # contrast keeps mean
    assert torch.allclose(z.std(dim=(1, 2, 3)), 0.5 * x.std(dim=(1, 2, 3)), atol=1e-6)
    assert gaussian_noise(x, 0.0, _g()).equal(x)
    assert (cutout(torch.ones(3, 1, 16, 16), 4, _g()) == 0).any()


def test_mixup_mixes_labels():
    x, y = torch.randn(4, 1, 5, 5, generator=_g()), F.one_hot(torch.tensor([0, 1, 2, 1]), 3).float()
    perm = torch.tensor([1, 0, 3, 2])
    xm, ym = mixup(x, y, 0.7, perm)
    assert torch.allclose(ym.sum(1), torch.ones(4))
    assert torch.allclose(ym[0], torch.tensor([0.7, 0.3, 0.0]))
    assert torch.allclose(xm[0], 0.7 * x[0] + 0.3 * x[1])
    assert torch.equal(mixup(x, y, 1.0, perm)[0], x)


def test_normaliser_uses_training_statistics():
    Xtr = 3 + 2 * torch.randn(500, 3, 4, 4, generator=_g())
    mean, std = fit_normalizer(Xtr)
    Z = normalize(Xtr, mean, std)
    assert torch.allclose(Z.mean(dim=(0, 2, 3)), torch.zeros(3), atol=1e-5)
    assert torch.allclose(Z.std(dim=(0, 2, 3)), torch.ones(3), atol=1e-5)


def test_conv_is_translation_equivariant_with_circular_padding():
    x, conv = torch.randn(1, 2, 12, 12, generator=_g()), nn.Conv2d(2, 3, 3, padding=1, padding_mode="circular")
    assert torch.allclose(conv(torch.roll(x, (2, 5), (2, 3))), torch.roll(conv(x), (2, 5), (2, 3)), atol=1e-6)


def test_conv_with_flipped_kernel_is_flip_equivariant():
    x, w = torch.randn(1, 2, 9, 9, generator=_g()), torch.randn(4, 2, 3, 3, generator=_g(1))
    assert torch.allclose(F.conv2d(hflip(x), w, padding=1), hflip(F.conv2d(x, hflip(w), padding=1)), atol=1e-5)


def test_strided_cnn_is_not_shift_invariant():
    """GAP over an equivariant map is shift-invariant; a stride-2 layer breaks that except
    for shifts that are multiples of the stride (aliasing, [S35] Zhang 2019)."""
    torch.manual_seed(0)
    net = nn.Sequential(nn.Conv2d(1, 4, 3, padding=1, padding_mode="circular"), nn.ReLU(),
                        nn.Conv2d(4, 4, 3, stride=2, padding=1, padding_mode="circular"), nn.ReLU(),
                        nn.AdaptiveAvgPool2d(1))
    x = torch.randn(1, 1, 16, 16, generator=_g())
    y0 = net(x)
    assert torch.allclose(net(torch.roll(x, 2, 3)), y0, atol=1e-6)
    assert not torch.allclose(net(torch.roll(x, 1, 3)), y0, atol=1e-4)


def test_shapes_augment_keeps_shape_and_mass():
    x = torch.zeros(1, 1, 32, 32)
    x[..., 12:20, 12:20] = 1
    y = shapes_augment(x, _g(3))
    assert y.shape == x.shape and y.sum() == pytest.approx(x.sum())   # object stays inside
