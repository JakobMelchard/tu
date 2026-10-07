"""Convolution arithmetic: output shapes, receptive fields, parameter and FLOP counts.

Notes 04 (CNNs) and 01 (sampling). Formulas from Dumoulin & Visin [S13] and
Goodfellow et al. ch. 9 [S11]; every function is cross-checked against the
matching torch layer in test_conv_arithmetic.py.

A network is described as a list of layer specs (dicts), e.g.
    {"type": "conv", "cout": 16, "k": 3, "s": 1, "p": 1}
    {"type": "pool", "k": 2, "s": 2}
    {"type": "bn"}, {"type": "relu"}, {"type": "gap"}, {"type": "fc", "cout": 10}
`trace(spec, (C, H, W))` walks it and returns one row per layer with the output
shape, parameter count, multiply-accumulates (MACs) and receptive field.
"""
from math import floor

import torch
from torch import nn


def conv_out(i, k, s=1, p=0, d=1):
    """Output size of a conv/pool along one axis: floor((i + 2p - d(k-1) - 1)/s) + 1."""
    o = floor((i + 2 * p - d * (k - 1) - 1) / s) + 1
    if o < 1:
        raise ValueError(f"kernel {k} (dilation {d}) does not fit input {i} with padding {p}")
    return o


def convT_out(i, k, s=1, p=0, output_padding=0, d=1):
    """Output size of a transposed conv: (i-1)s - 2p + d(k-1) + output_padding + 1."""
    return (i - 1) * s - 2 * p + d * (k - 1) + output_padding + 1


def same_padding(k, d=1):
    """Padding that keeps the size at stride 1 (odd effective kernel only)."""
    keff = d * (k - 1) + 1
    if keff % 2 == 0:
        raise ValueError("'same' padding needs an odd effective kernel")
    return (keff - 1) // 2


def conv_params(cin, cout, k, bias=True, groups=1):
    """k^2 * (cin/groups) * cout weights (+ cout biases). Independent of H, W."""
    return k * k * (cin // groups) * cout + (cout if bias else 0)


def conv_macs(cin, cout, k, hout, wout, groups=1):
    """Multiply-accumulates of one forward pass: one k^2 cin/groups dot product per output value."""
    return k * k * (cin // groups) * cout * hout * wout


def linear_params(nin, nout, bias=True):
    return nin * nout + (nout if bias else 0)


def receptive_field(layers):
    """Receptive field r, jump j (cumulative stride) and start offset of the last layer.

    `layers` is a list of (k, s) or (k, s, p) or (k, s, p, d). Recursion (Dumoulin & Visin
    [S13]; note 04): r_l = r_{l-1} + (k_eff - 1) j_{l-1}, j_l = j_{l-1} s_l,
    start_l = start_{l-1} + ((k_eff - 1)/2 - p) j_{l-1}  (centre of the first unit, input px).
    """
    r, j, start = 1, 1, 0.5
    for layer in layers:
        k, s = layer[0], layer[1]
        p = layer[2] if len(layer) > 2 else 0
        d = layer[3] if len(layer) > 3 else 1
        keff = d * (k - 1) + 1
        r = r + (keff - 1) * j
        start = start + ((keff - 1) / 2 - p) * j
        j = j * s
    return r, j, start


def trace(spec, in_shape):
    """Walk a layer spec; return rows (name, out_shape, params, macs, rf) and the totals."""
    c, h, w = in_shape
    rows, rf_layers, flat = [], [], None
    for n, L in enumerate(spec):
        t = L["type"]
        params = macs = 0
        if t == "conv":
            k, s, p, d = L["k"], L.get("s", 1), L.get("p", 0), L.get("d", 1)
            g, bias = L.get("groups", 1), L.get("bias", True)
            h, w = conv_out(h, k, s, p, d), conv_out(w, k, s, p, d)
            params = conv_params(c, L["cout"], k, bias, g)
            macs = conv_macs(c, L["cout"], k, h, w, g)
            c = L["cout"]
            rf_layers.append((k, s, p, d))
        elif t in ("maxpool", "avgpool", "pool"):
            k, s, p = L["k"], L.get("s", L["k"]), L.get("p", 0)
            h, w = conv_out(h, k, s, p), conv_out(w, k, s, p)
            rf_layers.append((k, s, p, 1))
        elif t == "bn":
            params = 2 * c                     # gamma, beta (running stats are buffers)
        elif t == "relu":
            pass
        elif t == "gap":
            h = w = 1
        elif t == "flatten":
            c, h, w = c * h * w, 1, 1
        elif t == "fc":
            params = linear_params(c * h * w, L["cout"], L.get("bias", True))
            macs = c * h * w * L["cout"]
            c, h, w = L["cout"], 1, 1
        else:
            raise ValueError(f"unknown layer type {t}")
        r = receptive_field(rf_layers)[0] if rf_layers else 1
        rows.append((f"{n}:{t}", (c, h, w), params, macs, r))
    total_p = sum(r[2] for r in rows)
    total_m = sum(r[3] for r in rows)
    return rows, total_p, total_m


def to_torch(spec, in_channels):
    """Build the torch.nn.Sequential that `spec` describes (for the cross-check tests)."""
    mods, c = [], in_channels
    for L in spec:
        t = L["type"]
        if t == "conv":
            mods.append(nn.Conv2d(c, L["cout"], L["k"], L.get("s", 1), L.get("p", 0),
                                  L.get("d", 1), L.get("groups", 1), L.get("bias", True)))
            c = L["cout"]
        elif t in ("maxpool", "pool"):
            mods.append(nn.MaxPool2d(L["k"], L.get("s", L["k"]), L.get("p", 0)))
        elif t == "avgpool":
            mods.append(nn.AvgPool2d(L["k"], L.get("s", L["k"]), L.get("p", 0)))
        elif t == "bn":
            mods.append(nn.BatchNorm2d(c))
        elif t == "relu":
            mods.append(nn.ReLU())
        elif t == "gap":
            mods.append(nn.AdaptiveAvgPool2d(1))
        elif t == "flatten":
            mods.append(nn.Flatten())
        elif t == "fc":
            mods.append(nn.Flatten())
            mods.append(nn.LazyLinear(L["cout"], bias=L.get("bias", True)))
            c = L["cout"]
    return nn.Sequential(*mods)


def empirical_receptive_field(model, in_shape):
    """Receptive field measured by backprop: extent of nonzero input gradient of the centre unit.

    Weights are set to 1 and biases to 0 so no path cancels. A max pool routes the gradient
    to one input only, so measure with avgpool in place of maxpool for the exact extent.
    """
    with torch.no_grad():
        for p in model.parameters():
            if p.dim() > 1:
                p.fill_(1.0)
            else:
                p.zero_()
    x = torch.ones(1, *in_shape, requires_grad=True)
    y = model(x)
    hc, wc = y.shape[-2] // 2, y.shape[-1] // 2
    y[0, 0, hc, wc].backward()
    nz = torch.nonzero(x.grad[0].abs().sum(0))
    return int(nz[:, 0].max() - nz[:, 0].min() + 1)


LENET5 = [  # LeCun et al. 1998 [S14], C1-S2-C3-S4-C5-F6-output on 1x32x32
    {"type": "conv", "cout": 6, "k": 5}, {"type": "avgpool", "k": 2},
    {"type": "conv", "cout": 16, "k": 5}, {"type": "avgpool", "k": 2},
    {"type": "conv", "cout": 120, "k": 5},
    {"type": "fc", "cout": 84}, {"type": "fc", "cout": 10},
]

EXAM_2017_RF = [(3, 1), (3, 1), (2, 2), (3, 1), (3, 1)]   # [S9] conv3 conv3 pool2/2 conv3 conv3


def print_trace(spec, in_shape):
    rows, tp, tm = trace(spec, in_shape)
    print(f"{'layer':<12}{'out shape':>18}{'params':>10}{'MACs':>12}{'RF':>5}")
    for name, shape, p, m, r in rows:
        print(f"{name:<12}{str(shape):>18}{p:>10,}{m:>12,}{r:>5}")
    print(f"{'total':<12}{'':>18}{tp:>10,}{tm:>12,}")


if __name__ == "__main__":
    print("2022S catalogue [S7]: 3x32x32 input, 3x3 kernel, 16 maps, stride 1, no padding")
    print("  out", (16, conv_out(32, 3), conv_out(32, 3)), "params", conv_params(3, 16, 3))
    print("2017 catalogue [S9]: conv3 conv3 pool2/2 conv3 conv3 -> receptive field",
          receptive_field(EXAM_2017_RF)[0])
    print("ResNet stem 224 -> conv7/2 p3 ->", conv_out(224, 7, 2, 3), "-> maxpool3/2 p1 ->",
          conv_out(conv_out(224, 7, 2, 3), 3, 2, 1))
    print("transposed conv k4 s2 p1 doubles 16 ->", convT_out(16, 4, 2, 1))
    print("\nLeNet-5 on 1x32x32")
    print_trace(LENET5, (1, 32, 32))
