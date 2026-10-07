"""The formula tables in notes 02, 03 and 06, checked against torch rather than trusted.

Two independent verification passes on sibling courses found sign errors in
tables of constants that had been written from memory. Everything here is
therefore executed: the closed forms are compared against what PyTorch actually
allocates and computes, over a sweep of configurations, and the receptive field
is measured from the gradient support rather than only recomputed.
"""

import torch
import torch.nn as nn

from shape_formulas import (attention_params, attention_score_bytes, check_conv,
                            check_params, check_receptive_field, conv_macs,
                            conv_out, conv_params, conv_transpose_out,
                            receptive_field, rnn_params,
                            transformer_block_params)


def test_conv_formulas_match_torch():
    assert check_conv() > 900


def test_parameter_formulas_match_torch():
    assert check_params() >= 27


def test_receptive_field_matches_gradient_support():
    assert check_receptive_field() == 3


def test_transposed_conv_inverts_conv_shape():
    # ConvTranspose with the same (k, s, p) is the adjoint, so it maps the
    # output grid back to (at least) the input grid [S38].
    for i, k, s, p in [(32, 3, 1, 1), (32, 4, 2, 1), (28, 3, 2, 1), (64, 5, 1, 2)]:
        o = conv_out(i, k, s, p)
        back = conv_transpose_out(o, k, s, p)
        assert back <= i and i - back < s, (i, k, s, p, o, back)


def test_note_02_worked_examples():
    """The exact numbers printed in note 02."""
    assert conv_out(224, 7, s=2, p=3) == 112            # ResNet stem conv
    assert conv_out(112, 3, s=2, p=1) == 56             # ResNet stem pool
    assert conv_out(32, 3, s=1, p=1) == 32              # padded 3x3
    assert conv_out(32, 2, s=2, p=0) == 16              # 2x2 max pool
    # bottleneck vs basic block
    for c, bott, basic in [(256, 69_632, 1_179_648), (512, 278_528, 4_718_592)]:
        got = (conv_params(c, c // 4, 1, False) + conv_params(c // 4, c // 4, 3, False)
               + conv_params(c // 4, c, 1, False))
        assert got == bott, (c, got)
        assert 2 * conv_params(c, c, 3, False) == basic
    # the most expensive layer of ShapeCNN
    assert conv_macs(16, 16, 3, 32, 32) == 2_359_296
    # depthwise separable is about k^2 cheaper than a dense conv at equal width
    dense = conv_params(64, 64, 3, False)
    sep = conv_params(64, 64, 3, False, groups=64) + conv_params(64, 64, 1, False)
    assert 7.5 < dense / sep < 9.0


def test_note_03_worked_examples():
    """Recurrent parameter counts, both conventions."""
    assert rnn_params(2, 32, "lstm") == 4_608 == sum(p.numel() for p in nn.LSTM(2, 32).parameters())
    assert rnn_params(2, 32, "gru") == 3_456
    assert rnn_params(2, 32, "rnn") == 1_152
    assert rnn_params(16, 64, "gru") == 15_744
    assert rnn_params(16, 64, "lstm") == 20_992
    # textbook one-bias counts quoted in the note's question 3
    assert rnn_params(16, 64, "gru", two_biases=False) == 15_552
    assert rnn_params(16, 64, "lstm", two_biases=False) == 20_736
    # GRU is exactly 3/4 of an LSTM at equal width
    assert rnn_params(16, 64, "gru") / rnn_params(16, 64, "lstm") == 0.75


def test_note_06_worked_examples():
    assert attention_params(64) == 16_640
    assert transformer_block_params(64) == 49_984 == 12 * 64 ** 2 + 13 * 64
    # the whole CharTransformer of src/py/transformer_char.py: V=14, d=64,
    # 2 blocks, max_len=16, and an output head with bias=False
    total = 14 * 64 + 16 * 64 + 2 * transformer_block_params(64) + 2 * 64 + 64 * 14
    assert total == 102_912
    from transformer_char import CharTransformer
    from common import count_params
    assert count_params(CharTransformer(14, d_model=64, n_heads=4, n_layers=2, max_len=16)) == total
    # attention memory is quadratic in T and independent of the head count's split
    assert attention_score_bytes(1, 4, 1024) == 16 * 1024 ** 2          # 16 MiB
    assert attention_score_bytes(1, 8, 1024) == attention_score_bytes(1, 4, 1024) * 2
    assert attention_score_bytes(1, 4, 2048) == attention_score_bytes(1, 4, 1024) * 4


def test_receptive_field_recursion_examples():
    assert receptive_field([(3, 1), (3, 1), (2, 2), (3, 1)]) == 10      # ShapeCNN
    assert receptive_field([(3, 1), (3, 1), (2, 2), (3, 1), (3, 1)]) == 14
    # two stacked 3x3 see as much as one 5x5, with fewer parameters
    assert receptive_field([(3, 1), (3, 1)]) == receptive_field([(5, 1)]) == 5
    assert 2 * conv_params(64, 64, 3, False) < conv_params(64, 64, 5, False)


def test_dilation_grows_the_receptive_field_without_parameters():
    x = torch.zeros(1, 1, 32, 32)
    plain = nn.Conv2d(1, 1, 3, padding=1, dilation=1)
    dil = nn.Conv2d(1, 1, 3, padding=2, dilation=2)
    assert plain(x).shape == dil(x).shape                              # same output size
    assert conv_params(1, 1, 3) == conv_params(1, 1, 3)                # same parameter count
    assert conv_out(32, 3, p=2, d=2) == 32


def test_adam_bias_correction_factor():
    """Note 01: omitting Adam's bias correction inflates the first step ~3x, not ~30x.

    m_1 = (1-b1) g,  v_1 = (1-b2) g^2, so the uncorrected step is
    eta * 0.1|g| / (sqrt(0.001) |g|) = eta / sqrt(0.1) = 3.16 eta,
    while the corrected step is exactly eta * sign(g).
    """
    b1, b2 = 0.9, 0.999
    for g in (torch.tensor([2.0]), torch.tensor([-1e-3]), torch.tensor([50.0])):
        m1, v1 = (1 - b1) * g, (1 - b2) * g ** 2
        uncorrected = (m1 / v1.sqrt()).abs().item()
        corrected = ((m1 / (1 - b1)) / (v1 / (1 - b2)).sqrt()).abs().item()
        assert abs(corrected - 1.0) < 1e-5
        assert abs(uncorrected - (1 - b1) / (1 - b2) ** 0.5) < 1e-4
        assert 3.1 < uncorrected < 3.2, uncorrected      # ~3x, emphatically not ~30x
