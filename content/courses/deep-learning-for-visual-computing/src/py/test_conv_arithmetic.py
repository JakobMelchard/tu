"""Tests for conv_arithmetic.py: every formula against the torch layer it describes."""
import itertools

import pytest
import torch
from torch import nn

from conv_arithmetic import (EXAM_2017_RF, LENET5, conv_macs, conv_out, conv_params, convT_out,
                             empirical_receptive_field, receptive_field, same_padding,
                             to_torch, trace)


def test_catalogue_numbers():
    assert conv_out(32, 3) == 30                      # 2022S: 3x32x32, 3x3, 16 maps -> 16x30x30 [S7]
    assert conv_params(3, 16, 3) == 448
    assert receptive_field(EXAM_2017_RF)[0] == 14     # 2017 catalogue [S9]
    assert conv_out(conv_out(224, 7, 2, 3), 3, 2, 1) == 56   # ResNet stem [S17]
    assert conv_out(5, 5) == 1


@pytest.mark.parametrize("i,k,s,p,d", [c for c in itertools.product(
    [7, 8, 15, 32], [1, 2, 3, 5], [1, 2, 3], [0, 1, 2], [1, 2]) if c[0] + 2 * c[3] >= c[4] * (c[1] - 1) + 1])
def test_conv_out_matches_torch(i, k, s, p, d):
    y = nn.Conv2d(1, 1, k, s, p, d)(torch.zeros(1, 1, i, i))
    assert y.shape[-1] == conv_out(i, k, s, p, d)


@pytest.mark.parametrize("i,k,s,p,op", [(4, 4, 2, 1, 0), (5, 3, 2, 1, 1), (7, 3, 1, 0, 0), (8, 2, 2, 0, 0)])
def test_convT_out_matches_torch(i, k, s, p, op):
    y = nn.ConvTranspose2d(1, 1, k, s, p, op)(torch.zeros(1, 1, i, i))
    assert y.shape[-1] == convT_out(i, k, s, p, op)


def test_same_padding():
    for k, d in [(3, 1), (5, 1), (3, 2), (7, 3)]:
        assert conv_out(20, k, 1, same_padding(k, d), d) == 20
    with pytest.raises(ValueError):
        same_padding(4)


@pytest.mark.parametrize("cin,cout,k,g,bias", [(3, 16, 3, 1, True), (32, 64, 3, 1, False),
                                               (32, 32, 3, 32, False), (64, 128, 1, 1, True),
                                               (16, 32, 5, 4, True)])
def test_params_match_torch(cin, cout, k, g, bias):
    m = nn.Conv2d(cin, cout, k, groups=g, bias=bias)
    assert sum(p.numel() for p in m.parameters()) == conv_params(cin, cout, k, bias, g)


def test_macs_match_hook_count():
    """Count MACs with a forward hook on every Conv2d and compare with the formula."""
    spec = [{"type": "conv", "cout": 8, "k": 3, "p": 1}, {"type": "relu"},
            {"type": "maxpool", "k": 2},
            {"type": "conv", "cout": 16, "k": 3, "s": 2, "p": 1, "groups": 2}]
    model, counted = to_torch(spec, 4), []

    def hook(mod, inp, out):
        counted.append(out.numel() * mod.in_channels // mod.groups * mod.kernel_size[0] ** 2)
    for m in model.modules():
        if isinstance(m, nn.Conv2d):
            m.register_forward_hook(hook)
    model(torch.zeros(1, 4, 20, 20))
    _, _, macs = trace(spec, (4, 20, 20))
    assert sum(counted) == macs
    assert conv_macs(4, 8, 3, 20, 20) == counted[0]


def test_trace_matches_torch_lenet():
    model = to_torch(LENET5, 1)
    y = model(torch.zeros(2, 1, 32, 32))
    rows, total_params, _ = trace(LENET5, (1, 32, 32))
    assert tuple(y.shape[1:]) == (10,)
    assert rows[-1][1] == (10, 1, 1)
    assert sum(p.numel() for p in model.parameters()) == total_params == 61706


@pytest.mark.parametrize("spec_rf", [
    ([(3, 1), (3, 1)], 5),
    ([(3, 1), (3, 1), (2, 2), (3, 1), (3, 1)], 14),
    ([(5, 2), (3, 2), (3, 1)], 5 + 2 * 2 + 2 * 4),
    ([(3, 1, 0, 2), (3, 1, 0, 4)], 1 + 4 + 8),       # dilated stack: 3 -> 7 -> 15 (WaveNet-style)
])
def test_receptive_field_matches_backprop(spec_rf):
    layers, expected = spec_rf
    assert receptive_field(layers)[0] == expected
    mods = []
    for L in layers:
        k, s = L[0], L[1]
        d = L[3] if len(L) > 3 else 1
        mods.append(nn.AvgPool2d(k, s) if (k == 2 and s == 2) else nn.Conv2d(1, 1, k, s, 0, d))
    assert empirical_receptive_field(nn.Sequential(*mods), (1, 64, 64)) == expected


def test_receptive_field_jump():
    r, j, _ = receptive_field([(3, 2), (3, 2), (3, 2)])
    assert j == 8 and r == 1 + 2 + 4 + 8
