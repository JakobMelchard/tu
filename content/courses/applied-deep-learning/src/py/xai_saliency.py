"""Gradient-based attributions for the shape CNN: saliency and integrated gradients.

saliency_i        = |d f_c(x) / d x_i|                      (Simonyan et al. 2014)
IG_i(x)           = (x_i - x'_i) * int_0^1 d f_c(x' + a (x - x')) / d x_i  da   (Sundararajan et al. 2017)
completeness      : sum_i IG_i = f_c(x) - f_c(x')  (checked numerically)
mass_inside       : fraction of |attribution| that falls on the shape's own pixels,
                    a pointing-game style sanity metric using the synthetic ground truth.
Also `grad_cam` for the last conv feature map (Selvaraju et al. 2017).
"""

from __future__ import annotations

import torch
from torch import nn

from cnn_shapes import ShapeCNN, make_shapes, run as train_cnn
from common import get_device, loss_decreased, seed_all


def _logit(model: nn.Module, x: torch.Tensor, target: torch.Tensor) -> torch.Tensor:
    """f_c(x) for each sample: the pre-softmax score of the target class. x: [B,1,H,W]."""
    return model(x).gather(1, target.view(-1, 1)).squeeze(1)


def saliency(model: nn.Module, x: torch.Tensor, target: torch.Tensor) -> torch.Tensor:
    """|d f_c / d x| per pixel, [B,1,H,W]."""
    model.eval()
    x = x.clone().requires_grad_(True)
    _logit(model, x, target).sum().backward()  # sum over batch: samples are independent
    return x.grad.abs().detach()


def integrated_gradients(model: nn.Module, x: torch.Tensor, baseline: torch.Tensor, target: torch.Tensor,
                         steps: int = 32) -> torch.Tensor:
    """Riemann (midpoint) approximation of the path integral from baseline to x, [B,1,H,W]."""
    model.eval()
    alphas = (torch.arange(steps, device=x.device) + 0.5) / steps
    total = torch.zeros_like(x)
    for a in alphas:
        xa = (baseline + a * (x - baseline)).requires_grad_(True)
        _logit(model, xa, target).sum().backward()
        total += xa.grad
    return (x - baseline) * total / steps


def completeness_error(model: nn.Module, x: torch.Tensor, baseline: torch.Tensor, target: torch.Tensor,
                       attr: torch.Tensor) -> float:
    """| sum_i IG_i - (f(x) - f(baseline)) | averaged over the batch; -> 0 as steps -> inf."""
    model.eval()
    with torch.no_grad():
        delta = _logit(model, x, target) - _logit(model, baseline, target)
    return (attr.flatten(1).sum(1) - delta).abs().mean().item()


def mass_inside(attr: torch.Tensor, mask: torch.Tensor) -> float:
    """Fraction of |attribution| mass lying on mask==1 pixels (mean over the batch)."""
    a = attr.abs().flatten(1)
    m = mask.flatten(1)
    return ((a * m).sum(1) / a.sum(1).clamp_min(1e-12)).mean().item()


def grad_cam(model: ShapeCNN, x: torch.Tensor, target: torch.Tensor) -> torch.Tensor:
    """Grad-CAM on the last conv block: ReLU(sum_k alpha_k^c A^k), alpha = spatial mean of dy^c/dA^k."""
    model.eval()
    feats: list[torch.Tensor] = []
    hook = model.features.register_forward_hook(lambda m, i, o: feats.append(o))
    try:
        score = _logit(model, x, target).sum()
    finally:
        hook.remove()
    A = feats[0]  # [B, K, h, w]
    grads = torch.autograd.grad(score, A)[0]
    alpha = grads.mean(dim=(2, 3), keepdim=True)  # [B, K, 1, 1]
    cam = torch.relu((alpha * A).sum(1, keepdim=True))  # [B, 1, h, w]
    return nn.functional.interpolate(cam, size=x.shape[-2:], mode="bilinear", align_corners=False)


def run(steps: int = 200, n_eval: int = 64, ig_steps: int = 32, device: torch.device | None = None,
        seed: int = 0, log_every: int = 0) -> dict:
    device = device or get_device()
    out = train_cnn(steps=steps, device=device, seed=seed, log_every=log_every)
    model = out["model"]
    seed_all(seed)
    X, y = make_shapes(n_eval, seed=seed + 7)  # noisy inputs as in training
    clean, _ = make_shapes(n_eval, seed=seed + 7, noise=0.0)  # same shapes, no noise: exact ground-truth mask
    mask = (clean > 0.5).float()
    X, y, mask = X.to(device), y.to(device), mask.to(device)
    baseline = torch.zeros_like(X)  # black image: the "absence of shape" reference
    sal = saliency(model, X, y)
    ig = integrated_gradients(model, X, baseline, y, steps=ig_steps)
    cam = grad_cam(model, X, y)
    return {"losses": out["losses"], "accuracy": out["accuracy"],
            "ig_completeness_error": completeness_error(model, X, baseline, y, ig),
            "saliency_mass_inside": mass_inside(sal, mask), "ig_mass_inside": mass_inside(ig, mask),
            "gradcam_mass_inside": mass_inside(cam, mask), "shape_area_fraction": mask.mean().item(),
            "model": model, "seconds": out["seconds"]}


if __name__ == "__main__":
    out = run(steps=300, log_every=100)
    print(f"CNN test accuracy {out['accuracy']:.3f}, loss decreased {loss_decreased(out['losses'])}")
    print(f"IG completeness error (32 steps): {out['ig_completeness_error']:.4f}")
    print(f"attribution mass on the shape pixels (shape covers {out['shape_area_fraction']:.2f} of the image): "
          f"saliency {out['saliency_mass_inside']:.2f}, IG {out['ig_mass_inside']:.2f}, "
          f"Grad-CAM {out['gradcam_mass_inside']:.2f}")
