"""Making a trained model small and fast enough to ship.

Lecture 12, *Serving, Optimizing, and Practical Aspects* [S4], and the half of
assignment 3 that is graded on a demo application [S14].  Two techniques, each
implemented from scratch and each measured rather than asserted:

1. **Number formats.** fp32 / fp16 / bf16 / int8, with their ranges and machine
   epsilons read out of ``torch.finfo`` instead of quoted from memory.
2. **Post-training int8 quantisation** [S87], the affine scheme, derived and then
   checked against ``torch.quantize_per_tensor``.
Pruning and the lottery ticket are the third technique of that lecture and live
next door in ``pruning.py``.

Conventions: "size" means parameter bytes only -- activations and the runtime are
extra.

Run: ``python deploy_optimize.py``.
"""

from __future__ import annotations

import warnings

import torch
import torch.nn as nn

warnings.filterwarnings("ignore", message=".*quantize_per_tensor.*")


# --- 1. number formats ------------------------------------------------------


def float_formats() -> dict[str, dict]:
    """Range and precision of the formats a deployed model might use.

    Read from ``torch.finfo`` [S96], not from a remembered table.  The headline:
    **bf16 has the same exponent field as fp32 and so the same dynamic range**;
    it buys that by keeping only 8 bits of mantissa, so it is *less* precise than
    fp16 while being far harder to overflow.  That is why bf16 training needs no
    loss scaling and fp16 training does [S85].
    """
    out = {}
    for name, dt in [("fp32", torch.float32), ("fp16", torch.float16), ("bf16", torch.bfloat16)]:
        fi = torch.finfo(dt)
        out[name] = {
            "bytes": fi.bits // 8,
            "max": fi.max,
            "tiny": fi.tiny,          # smallest positive normal
            "eps": fi.eps,            # 2^-mantissa_bits
            "mantissa_bits": int(round(-torch.log2(torch.tensor(fi.eps)).item())),
            "decimal_digits": -torch.log10(torch.tensor(fi.eps)).item(),
        }
    ii = torch.iinfo(torch.int8)
    out["int8"] = {"bytes": 1, "max": ii.max, "min": ii.min, "levels": ii.max - ii.min + 1}
    return out


# --- 2. affine int8 quantisation -------------------------------------------


def quant_params(x: torch.Tensor, symmetric: bool = False, bits: int = 8) -> tuple[float, int]:
    """Scale and zero-point mapping ``x``'s range onto the integer grid [S87].

    Asymmetric (the default): the real interval ``[x_min, x_max]`` is mapped onto
    ``[q_min, q_max]`` by ``q = round(x / s) + z``.  Requiring the two endpoints
    to map onto each other gives

        s = (x_max - x_min) / (q_max - q_min),     z = q_min - round(x_min / s)

    and ``z`` is rounded to an integer so that real zero is represented exactly,
    which matters because zero padding must stay exactly zero.

    Symmetric: ``z = 0`` and ``s = max|x| / q_max``.  Half the levels are wasted
    if the tensor is one-sided (a post-ReLU activation), but the arithmetic is
    cheaper, so weights are usually symmetric and activations asymmetric.
    """
    q_min, q_max = -(2 ** (bits - 1)), 2 ** (bits - 1) - 1
    if symmetric:
        s = x.abs().max().item() / q_max
        return (s if s > 0 else 1.0), 0
    lo, hi = min(x.min().item(), 0.0), max(x.max().item(), 0.0)
    s = (hi - lo) / (q_max - q_min)
    if s == 0:
        return 1.0, 0
    return s, int(round(q_min - lo / s))


def quantize(x: torch.Tensor, s: float, z: int, bits: int = 8) -> torch.Tensor:
    q_min, q_max = -(2 ** (bits - 1)), 2 ** (bits - 1) - 1
    return torch.clamp(torch.round(x / s) + z, q_min, q_max)


def dequantize(q: torch.Tensor, s: float, z: int) -> torch.Tensor:
    return (q - z) * s


def quantization_error(x: torch.Tensor, symmetric: bool = False, bits: int = 8) -> dict:
    """Round-trip a tensor and report the error.

    The theoretical bound is half a step, ``s/2``, so the max error should sit at
    or just below it and the RMS at about ``s / sqrt(12)`` for a roughly uniform
    tensor (the variance of a uniform error on ``[-s/2, s/2]``).
    """
    s, z = quant_params(x, symmetric, bits)
    err = (dequantize(quantize(x, s, z, bits), s, z) - x)
    return {
        "scale": s,
        "zero_point": z,
        "max_abs_error": err.abs().max().item(),
        "rms_error": err.pow(2).mean().sqrt().item(),
        "half_step": s / 2,
        "uniform_rms_prediction": s / 12 ** 0.5,
        "signal_to_noise_db": 10 * torch.log10(x.pow(2).mean() / err.pow(2).mean()).item(),
    }


def quantize_model_weights(model: nn.Module, symmetric: bool = True) -> dict:
    """Quantise every weight tensor per-tensor and report size and error."""
    fp32_bytes = int8_bytes = 0
    worst = 0.0
    for p in model.parameters():
        fp32_bytes += p.numel() * 4
        int8_bytes += p.numel() + 8          # the values plus a scale and a zero-point
        s, z = quant_params(p.data, symmetric)
        err = (dequantize(quantize(p.data, s, z), s, z) - p.data).abs().max().item()
        worst = max(worst, err)
    return {"fp32_bytes": fp32_bytes, "int8_bytes": int8_bytes,
            "compression": fp32_bytes / int8_bytes, "worst_weight_error": worst}



def run(seed: int = 0, device=None) -> dict:
    """Entry point matching the other modules: the format table and a quantisation."""
    torch.manual_seed(seed)
    w = torch.randn(4096) * 0.1
    return {"formats": float_formats(),
            "symmetric": quantization_error(w, symmetric=True),
            "asymmetric": quantization_error(w, symmetric=False)}


if __name__ == "__main__":
    f = float_formats()
    print("Number formats (from torch.finfo, not from memory):")
    print(f"  {'':6s} {'bytes':>5s} {'max':>12s} {'min normal':>12s} {'eps':>10s} "
          f"{'mantissa':>9s} {'~dec digits':>12s}")
    for k in ("fp32", "fp16", "bf16"):
        v = f[k]
        print(f"  {k:6s} {v['bytes']:5d} {v['max']:12.4g} {v['tiny']:12.4g} "
              f"{v['eps']:10.4g} {v['mantissa_bits']:9d} {v['decimal_digits']:12.1f}")
    print(f"  int8   {f['int8']['bytes']:5d} {f['int8']['max']:12d} {f['int8']['min']:12d}"
          f"{'':>22s}   {f['int8']['levels']} levels")
    print("  bf16 shares fp32's exponent field, so the same overflow threshold; fp16 has 3")
    print("  more mantissa bits than bf16 but overflows at 65504 -- hence fp16's loss scaling.")

    print("\nAffine int8 quantisation of a Gaussian weight tensor:")
    torch.manual_seed(0)
    w = torch.randn(4096) * 0.1
    for sym in (True, False):
        q = quantization_error(w, symmetric=sym)
        print(f"  {'symmetric ' if sym else 'asymmetric'}: scale {q['scale']:.3e}  zp {q['zero_point']:4d}"
              f"  max err {q['max_abs_error']:.3e} (bound {q['half_step']:.3e})"
              f"  rms {q['rms_error']:.3e} (uniform {q['uniform_rms_prediction']:.3e})"
              f"  SNR {q['signal_to_noise_db']:.1f} dB")
    s, z = quant_params(w, symmetric=False)
    ref = torch.quantize_per_tensor(w, scale=s, zero_point=z, dtype=torch.qint8)
    print(f"  agrees with torch.quantize_per_tensor on "
          f"{(ref.int_repr().float() == quantize(w, s, z)).float().mean():.1%} of entries")

    w2 = w.clone()
    w2[0] = 5.0                                   # one 50-sigma outlier
    print(f"\n  SNR without an outlier {quantization_error(w, True)['signal_to_noise_db']:.1f} dB"
          f" -> with one {quantization_error(w2, True)['signal_to_noise_db']:.1f} dB.")
    print("  The outlier sets the scale, so every other weight loses resolution. Remedies:")
    print("  per-channel scales, a clipped calibration range, or outlier channels kept in fp16.")
    print("\n  Pruning and the lottery ticket: see pruning.py")
