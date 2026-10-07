"""Deployment arithmetic: formats from torch.finfo, quantisation against torch.

Nothing about the float formats is hard-coded from memory here except the two
facts that define them -- fp16 has a 5-bit exponent and bf16 has fp32's 8-bit
exponent -- and even those are then re-derived from ``torch.finfo`` [S96].
"""

import warnings

import torch
import torch.nn as nn

warnings.filterwarnings("ignore", message=".*quantize_per_tensor.*")

from deploy_optimize import (dequantize, float_formats, quant_params,
                             quantization_error, quantize,
                             quantize_model_weights)


def test_float_format_facts():
    f = float_formats()
    assert f["fp32"]["bytes"] == 4 and f["fp16"]["bytes"] == 2 and f["bf16"]["bytes"] == 2
    assert f["fp32"]["mantissa_bits"] == 23
    assert f["fp16"]["mantissa_bits"] == 10
    assert f["bf16"]["mantissa_bits"] == 7
    # bf16 keeps fp32's exponent field, so the same overflow threshold and the
    # same smallest normal; that is the whole point of the format.
    assert f["bf16"]["max"] / f["fp32"]["max"] > 0.99
    assert f["bf16"]["tiny"] == f["fp32"]["tiny"]
    # fp16 is the precise one and the fragile one: 3 more mantissa bits, but it
    # overflows at 65504 where bf16 and fp32 go to 3.4e38.
    assert f["fp16"]["eps"] < f["bf16"]["eps"]
    assert f["fp16"]["max"] == 65504.0
    assert f["int8"]["levels"] == 256 and f["int8"]["min"] == -128 and f["int8"]["max"] == 127


def test_overflow_behaviour_follows_the_table():
    big = torch.tensor([1e5])
    assert torch.isinf(big.to(torch.float16)).item()     # 1e5 > 65504
    assert torch.isfinite(big.to(torch.bfloat16)).item()


def test_quantisation_matches_torch():
    torch.manual_seed(0)
    for scale in (0.01, 1.0, 100.0):
        x = torch.randn(2048) * scale
        s, z = quant_params(x, symmetric=False)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            ref = torch.quantize_per_tensor(x, scale=s, zero_point=z, dtype=torch.qint8)
        assert torch.equal(ref.int_repr().float(), quantize(x, s, z))


def test_quantisation_error_respects_the_half_step_bound():
    torch.manual_seed(0)
    for sym in (True, False):
        q = quantization_error(torch.randn(4096) * 0.1, symmetric=sym)
        assert q["max_abs_error"] <= q["half_step"] * 1.001
        # for a smooth distribution the error is close to uniform on [-s/2, s/2]
        assert 0.8 < q["rms_error"] / q["uniform_rms_prediction"] < 1.2
        # 8 bits buys roughly 6 dB per bit above the signal's crest factor
        assert 35 < q["signal_to_noise_db"] < 50


def test_asymmetric_quantisation_represents_zero_exactly():
    torch.manual_seed(0)
    x = torch.relu(torch.randn(1024))                    # one-sided, like a post-ReLU activation
    s, z = quant_params(x, symmetric=False)
    zero = dequantize(quantize(torch.zeros(1), s, z), s, z)
    assert zero.abs().item() < 1e-12                     # padding must stay exactly zero


def test_outliers_destroy_per_tensor_quantisation():
    torch.manual_seed(0)
    clean = torch.randn(4096) * 0.1
    spiked = clean.clone()
    spiked[0] = 5.0
    # a single 50-sigma outlier costs well over 10 dB for every other weight
    drop = (quantization_error(clean, True)["signal_to_noise_db"]
            - quantization_error(spiked, True)["signal_to_noise_db"])
    assert drop > 10


def test_int8_is_about_four_times_smaller():
    model = nn.Sequential(nn.Linear(64, 64), nn.ReLU(), nn.Linear(64, 8))
    q = quantize_model_weights(model)
    assert 3.8 < q["compression"] < 4.0                  # 4x minus the per-tensor scales
