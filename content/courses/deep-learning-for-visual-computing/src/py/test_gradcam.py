"""Tests for gradcam.py: shapes, the CAM identity, and the two sanity checks."""
import numpy as np
import torch

from cnn_synthetic import SmallCNN, trained_model
from gradcam import (GradCAM, class_activation_map, mass_inside, normalise, randomised_copy,
                     saliency, spearman)


def _data(n=64):
    out = trained_model()
    return out["model"], out["X_test"][:n], out["y_test"][:n], out["masks_test"][:n]


def test_shapes_and_range_on_untrained_model():
    torch.manual_seed(0)
    m = SmallCNN()
    cam, logits = GradCAM(m, m.features)(torch.randn(3, 1, 32, 32))
    assert cam.shape == (3, 32, 32) and logits.shape == (3, 4)
    assert cam.min() >= 0 and cam.max() <= 1
    raw, _ = GradCAM(m, m.features)(torch.randn(3, 1, 32, 32), upsample=False)
    assert raw.shape == (3, 8, 8)
    assert saliency(m, torch.randn(2, 1, 32, 32)).shape == (2, 32, 32)
    assert len(m.features._forward_hooks) == 0            # hook removed after the call


def test_gradcam_equals_cam_for_gap_linear_head():
    """With GAP + linear, d y^c / d A^k_ij = w_ck / (hw), so alpha_k is proportional to w_ck
    and Grad-CAM = ReLU(CAM) after normalisation (Selvaraju et al. [S34])."""
    model, X, y, _ = _data(16)
    g, _ = GradCAM(model, model.features)(X, class_idx=y, upsample=False)
    c = normalise(torch.relu(class_activation_map(model, X, y)))
    assert torch.allclose(g, c, atol=1e-4)


def test_gradcam_localises_the_object():
    model, X, y, masks = _data()
    cam, logits = GradCAM(model, model.features)(X)
    inside, dil = mass_inside(cam, masks)
    area = dil.flatten(1).float().mean(1)
    assert (logits.argmax(1) == y).float().mean() > 0.9
    assert inside.mean() > 0.6 and inside.mean() > 1.8 * area.mean()


def test_model_randomisation_changes_the_map():
    """Adebayo et al. [S34]: an explanation that survives weight randomisation explains the
    input, not the model. Grad-CAM of the trained net localises better and correlates weakly."""
    model, X, y, masks = _data()
    trained = GradCAM(model, model.features)(X, class_idx=y)[0]
    ins_t = mass_inside(trained, masks)[0].mean().item()
    ins_r, rho = [], []
    for seed in range(3):
        r = randomised_copy(model, seed)
        cr = GradCAM(r, r.features)(X, class_idx=y)[0]
        ins_r.append(mass_inside(cr, masks)[0].mean().item())
        rho.append(np.mean([spearman(a, b) for a, b in zip(trained, cr)]))
    assert ins_t > np.mean(ins_r) + 0.1
    assert np.mean(rho) < 0.6


def test_spearman_basic():
    a = torch.arange(10.0)
    assert abs(spearman(a, a) - 1) < 1e-6 and abs(spearman(a, -a) + 1) < 1e-6
