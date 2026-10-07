"""Grad-CAM and vanilla gradient saliency for the SmallCNN of cnn_synthetic.py, with the
two sanity checks the note asks for: localisation on synthetic shapes and the
model-randomisation test.

Note 08 (practical aspects: visualisation). Grad-CAM after Selvaraju et al. [S34]:
    alpha_k^c = (1/Z) sum_ij d y^c / d A^k_ij,   L^c = ReLU(sum_k alpha_k^c A^k),
CAM after Zhou et al. [S34], saliency after Simonyan et al. [S34], randomisation check
after Adebayo et al. [S34].
"""
import copy

import numpy as np
import torch
import torch.nn.functional as F


class GradCAM:
    """Grad-CAM at `layer` (an nn.Module whose output is [N,K,h,w]) of `model`. The forward
    hook lives only for the duration of one call, so the model is left unchanged."""

    def __init__(self, model, layer):
        self.model, self.layer, self.acts, self.grads = model, layer, None, None

    def _save(self, module, inp, out):
        self.acts = out
        out.register_hook(lambda g: setattr(self, "grads", g))

    def __call__(self, x, class_idx=None, upsample=True):
        """Returns (maps [N,H,W] in [0,1], logits). class_idx None = predicted class."""
        self.model.eval()
        handle = self.layer.register_forward_hook(self._save)
        try:
            logits = self.model(x)
        finally:
            handle.remove()
        c = logits.argmax(1) if class_idx is None else torch.as_tensor(class_idx).expand(len(x))
        self.model.zero_grad()
        logits.gather(1, c[:, None]).sum().backward()      # rows are independent in eval mode
        alpha = self.grads.mean(dim=(2, 3), keepdim=True)   # GAP of the gradients
        cam = F.relu((alpha * self.acts).sum(1, keepdim=True)).detach()
        if upsample:
            cam = F.interpolate(cam, size=x.shape[-2:], mode="bilinear", align_corners=False)
        return normalise(cam[:, 0]), logits.detach()


def normalise(m):
    """Scale each map to [0, 1] (all-zero maps stay zero)."""
    flat = m.flatten(1)
    lo, hi = flat.min(1).values[:, None, None], flat.max(1).values[:, None, None]
    return (m - lo) / torch.where(hi > lo, hi - lo, torch.ones_like(hi))


def class_activation_map(model, x, class_idx):
    """CAM for a GAP + linear head: sum_k w_ck A^k (no gradients needed) [S34]."""
    model.eval()
    with torch.no_grad():
        A = model.features(model.block2(model.block1(x)))
        w = model.head.weight[class_idx]                    # [N, K]
        return (w[:, :, None, None] * A).sum(1)


def saliency(model, x, class_idx=None):
    """|d y^c / d x|, max over input channels [S34]: which pixels change the score most."""
    model.eval()
    x = x.clone().requires_grad_(True)
    logits = model(x)
    c = logits.argmax(1) if class_idx is None else torch.as_tensor(class_idx).expand(len(x))
    logits.gather(1, c[:, None]).sum().backward()
    return x.grad.abs().amax(1)


def mass_inside(maps, masks, dilate=2):
    """Fraction of each map's total mass inside the (dilated) object mask."""
    m = torch.as_tensor(masks, dtype=torch.float32)[:, None]
    m = F.max_pool2d(m, 2 * dilate + 1, stride=1, padding=dilate)[:, 0] > 0
    return ((maps * m).flatten(1).sum(1) / maps.flatten(1).sum(1).clamp_min(1e-12)), m


def randomised_copy(model, seed=0):
    """Model-randomisation sanity check: same architecture, re-initialised weights."""
    torch.manual_seed(seed)
    m = copy.deepcopy(model)
    for mod in m.modules():
        if hasattr(mod, "reset_parameters"):
            mod.reset_parameters()
    return m


def spearman(a, b):
    ra, rb = a.flatten().argsort().argsort().float(), b.flatten().argsort().argsort().float()
    ra, rb = ra - ra.mean(), rb - rb.mean()
    return float((ra * rb).sum() / (ra.norm() * rb.norm()))


def ascii_map(m, levels=" .:-=+*#%@"):
    """Terminal rendering of a [H,W] map in [0,1], every second row and column."""
    m = m[::2, ::2].numpy()
    return "\n".join("".join(levels[min(int(v * len(levels)), len(levels) - 1)] for v in row) for row in m)


if __name__ == "__main__":
    from cnn_synthetic import CLASSES, trained_model
    out = trained_model()
    model, X, y, masks = out["model"], out["X_test"][:64], out["y_test"][:64], out["masks_test"][:64]
    cam, logits = GradCAM(model, model.features)(X)
    inside, dil = mass_inside(cam, masks)
    area = dil.flatten(1).float().mean(1)
    print(f"Grad-CAM mass inside the dilated object mask: mean {inside.mean():.2f} "
          f"(mask covers {area.mean():.2f} of the image)")
    sal = saliency(model, X)
    print(f"saliency mass inside the mask: {mass_inside(sal, masks)[0].mean():.2f}")
    rnd = randomised_copy(model)
    cam_r, _ = GradCAM(rnd, rnd.features)(X, class_idx=y)
    cam_t, _ = GradCAM(model, model.features)(X, class_idx=y)
    rho = np.mean([spearman(a, b) for a, b in zip(cam_t, cam_r)])
    print(f"randomisation check: mean Spearman(trained CAM, random-weights CAM) = {rho:.2f}")
    i = int(torch.nonzero(y == 2)[0])
    print(f"\nimage {i} ({CLASSES[y[i]]}), input then Grad-CAM:")
    print(ascii_map((X[i, 0] > 0.3).float()))
    print(ascii_map(cam[i]))
