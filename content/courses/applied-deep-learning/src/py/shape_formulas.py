"""Layer output shapes and parameter counts: the formulas, executed.

Note 02 and note 03 state closed forms for convolution output size, transposed
convolution output size, receptive field, and the parameter count of conv, RNN,
LSTM, GRU, attention and transformer blocks. Tables like that accumulate errors
when they are written from memory, so nothing here is asserted: every formula is
implemented once and then checked against what PyTorch actually builds, over a
sweep of configurations.

Conventions, stated explicitly because half the disagreements are conventions:

* Spatial layout is NCHW, kernels are ``[C_out, C_in, k, k]``, and what the
  frameworks call "convolution" is cross-correlation (no kernel flip) [S38].
* ``padding`` is the padding added to *each* side, so total padding is ``2p``.
* ``nn.RNN``/``nn.LSTM``/``nn.GRU`` keep **two** bias vectors per gate block
  (``bias_ih`` and ``bias_hh``), not one; textbook counts give the one-bias
  number. Both are computed below.
* Receptive field is measured in input pixels per spatial dimension, with
  ``r_0 = 1``.

Sources: Dumoulin & Visin, *A guide to convolution arithmetic for deep learning*
[S38] (lecture 3's own reference 1) for the convolution formulas; PyTorch 2.14
[S96] for what is actually built.

Run: ``python shape_formulas.py`` prints the tables it has just verified.
"""

from __future__ import annotations

import torch
import torch.nn as nn


# --- the formulas ----------------------------------------------------------


def conv_out(i: int, k: int, s: int = 1, p: int = 0, d: int = 1) -> int:
    """Output size of a convolution along one spatial dimension [S38, eq. 15].

    The kernel's first position starts at ``-p``; with dilation ``d`` it spans
    ``k_eff = d(k-1)+1`` input pixels, so the last valid start is at
    ``i + p - k_eff``.  Starts are spaced by ``s``.
    """
    k_eff = d * (k - 1) + 1
    return (i + 2 * p - k_eff) // s + 1


def conv_transpose_out(i: int, k: int, s: int = 1, p: int = 0, out_p: int = 0, d: int = 1) -> int:
    """Output size of a transposed convolution [S38, eq. 26-29].

    The adjoint of ``conv_out``: it maps the output grid back to the input grid,
    which is why ``s`` multiplies and ``p`` subtracts.
    """
    k_eff = d * (k - 1) + 1
    return (i - 1) * s - 2 * p + k_eff + out_p


def conv_params(c_in: int, c_out: int, k: int, bias: bool = True, groups: int = 1) -> int:
    """Parameters of a 2-D convolution.  Independent of the image size."""
    return k * k * (c_in // groups) * c_out + (c_out if bias else 0)


def conv_macs(c_in: int, c_out: int, k: int, h_out: int, w_out: int, groups: int = 1) -> int:
    """Multiply-accumulates of one forward pass.  FLOPs are about twice this."""
    return k * k * (c_in // groups) * c_out * h_out * w_out


def receptive_field(layers: list[tuple[int, int]]) -> int:
    """r_L for a stack of ``(kernel, stride)`` layers, r_0 = 1.

    ``r_l = r_{l-1} + (k_l - 1) * prod_{j<l} s_j``: layer ``l`` spans ``k_l``
    units of the previous map, whose spacing in input pixels is the cumulative
    stride of everything before it.
    """
    r, jump = 1, 1
    for k, s in layers:
        r += (k - 1) * jump
        jump *= s
    return r


def rnn_params(f: int, h: int, cell: str = "lstm", two_biases: bool = True) -> int:
    """Parameters of one recurrent layer.

    ``blocks`` gate blocks of ``h*(h+f)`` weights each, plus ``h`` (textbook) or
    ``2h`` (PyTorch) biases per block.
    """
    blocks = {"rnn": 1, "gru": 3, "lstm": 4}[cell]
    return blocks * (h * (h + f) + (2 if two_biases else 1) * h)


def attention_params(d: int, bias: bool = True) -> int:
    """Multi-head attention: fused QKV projection plus the output projection.

    ``4 d^2`` weights regardless of the number of heads -- heads only reshape.
    """
    return 4 * d * d + (4 * d if bias else 0)


def transformer_block_params(d: int, ffn_mult: int = 4, bias: bool = True) -> int:
    """One pre-norm transformer block: attention + FFN + two LayerNorms.

    With ``ffn_mult = 4`` and biases this is ``12 d^2 + 13 d``.
    """
    ffn = 2 * ffn_mult * d * d + ((ffn_mult + 1) * d if bias else 0)
    return attention_params(d, bias) + ffn + 4 * d


def attention_score_bytes(batch: int, heads: int, seq: int, layers: int = 1, dtype_bytes: int = 4) -> int:
    """Bytes held by the attention score tensors ``[B, h, T, T]`` of a forward pass.

    Quadratic in ``seq``; this, not the parameters, is what limits context length.
    """
    return batch * heads * seq * seq * layers * dtype_bytes


# --- checks against torch --------------------------------------------------


def check_conv(verbose: bool = False) -> int:
    """Sweep conv / transposed-conv configurations against ``nn.Conv2d``."""
    checked = 0
    for i in (8, 16, 28, 32, 224):
        for k in (1, 3, 5, 7):
            for s in (1, 2, 3):
                for p in (0, 1, 2, 3):
                    for d in (1, 2):
                        if d * (k - 1) + 1 > i + 2 * p:
                            continue
                        x = torch.zeros(1, 2, i, i)
                        y = nn.Conv2d(2, 3, k, stride=s, padding=p, dilation=d)(x)
                        assert y.shape[-1] == conv_out(i, k, s, p, d), (i, k, s, p, d, y.shape)
                        z = nn.ConvTranspose2d(2, 3, k, stride=s, padding=p, dilation=d)(x)
                        assert z.shape[-1] == conv_transpose_out(i, k, s, p, 0, d), (i, k, s, p, d)
                        checked += 2
                        if verbose:
                            print(f"i={i} k={k} s={s} p={p} d={d} -> {y.shape[-1]}, T {z.shape[-1]}")
    return checked


def check_params() -> int:
    """Sweep parameter-count formulas against what torch allocates."""
    n = lambda m: sum(q.numel() for q in m.parameters())
    checked = 0
    for c_in, c_out, k in [(1, 16, 3), (16, 32, 3), (3, 64, 7), (512, 128, 1), (64, 64, 5)]:
        for bias in (True, False):
            assert conv_params(c_in, c_out, k, bias) == n(nn.Conv2d(c_in, c_out, k, bias=bias))
            checked += 1
    # depthwise separable = depthwise (groups=C_in) + pointwise 1x1
    dw = nn.Conv2d(32, 32, 3, groups=32, bias=False)
    pw = nn.Conv2d(32, 64, 1, bias=False)
    assert conv_params(32, 32, 3, False, groups=32) == n(dw)
    assert conv_params(32, 64, 1, False) == n(pw)
    checked += 2

    for f, h in [(2, 32), (16, 64), (6, 128)]:
        for cell, mod in [("rnn", nn.RNN), ("gru", nn.GRU), ("lstm", nn.LSTM)]:
            assert rnn_params(f, h, cell) == n(mod(f, h)), (f, h, cell)
            checked += 1

    for d in (64, 128, 512):
        blk = nn.ModuleList([nn.Linear(d, 3 * d), nn.Linear(d, d), nn.LayerNorm(d),
                             nn.Linear(d, 4 * d), nn.Linear(4 * d, d), nn.LayerNorm(d)])
        assert transformer_block_params(d) == n(blk), d
        assert transformer_block_params(d) == 12 * d * d + 13 * d, d
        checked += 2
    return checked


def check_receptive_field() -> int:
    """Check the recursion by measuring gradient support on a real stack."""
    stacks = [
        [(3, 1), (3, 1), (2, 2), (3, 1)],                  # ShapeCNN
        [(3, 1), (3, 1), (2, 2), (3, 1), (3, 1)],          # a VGG block
        [(7, 2), (3, 2)],                                  # the ResNet stem
    ]
    checked = 0
    for stack in stacks:
        layers, c = [], 1
        for k, s in stack:
            layers.append(nn.Conv2d(c, 1, k, stride=s, padding=0, bias=False))
            c = 1
        net = nn.Sequential(*layers)
        for p in net.parameters():
            nn.init.constant_(p, 1.0)          # every path contributes, so support is exact
        size = 129
        x = torch.zeros(1, 1, size, size, requires_grad=True)
        y = net(x)
        centre = y.shape[-1] // 2
        y[0, 0, centre, centre].backward()
        support = (x.grad[0, 0].abs() > 0).any(0).nonzero()
        measured = int(support.max() - support.min()) + 1
        assert measured == receptive_field(stack), (stack, measured, receptive_field(stack))
        checked += 1
    return checked


def run(verbose: bool = False) -> dict:
    """Verify every formula in this module.  Returns the check counts."""
    return {
        "conv_checks": check_conv(verbose),
        "param_checks": check_params(),
        "receptive_field_checks": check_receptive_field(),
    }


if __name__ == "__main__":
    res = run()
    print("formulas verified against torch:", res, "\n")

    print("ResNet stem, 224x224 input:")
    o1 = conv_out(224, 7, s=2, p=3)
    o2 = conv_out(o1, 3, s=2, p=1)
    print(f"  conv7x7 s2 p3 -> {o1}; maxpool3x3 s2 p1 -> {o2}; "
          f"receptive field {receptive_field([(7, 2), (3, 2)])}")

    print("\nResNet-50 bottleneck vs basic block, width C:")
    for c in (256, 512):
        bott = conv_params(c, c // 4, 1, False) + conv_params(c // 4, c // 4, 3, False) + conv_params(c // 4, c, 1, False)
        basic = 2 * conv_params(c, c, 3, False)
        print(f"  C={c}: bottleneck {bott:,}  basic {basic:,}  ratio {basic / bott:.1f}x")

    print("\nRecurrent layers, PyTorch two-bias convention:")
    for f, h in [(2, 32), (16, 64)]:
        row = "  ".join(f"{c.upper()}({f},{h})={rnn_params(f, h, c):,}" for c in ("rnn", "gru", "lstm"))
        print("  " + row)

    print("\nTransformer block, 12 d^2 + 13 d:")
    for d in (64, 512, 768):
        print(f"  d={d:4d}: {transformer_block_params(d):,} parameters")

    print("\nAttention score memory, fp32, one forward pass:")
    for tag, (b, h, t, l) in {"toy (B1 h4 T1024 L1)": (1, 4, 1024, 1),
                              "GPT-2 small (B8 h12 T1024 L12)": (8, 12, 1024, 12),
                              "GPT-2 small at T=2048": (8, 12, 2048, 12)}.items():
        mb = attention_score_bytes(b, h, t, l) / 1024 ** 2
        print(f"  {tag:32s} {mb:10.1f} MiB")
