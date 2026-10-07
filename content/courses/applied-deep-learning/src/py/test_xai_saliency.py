import torch

from common import loss_decreased
from xai_saliency import completeness_error, integrated_gradients, run


def test_ig_completeness_on_linear_model():
    # f(x) = w.x is linear, so IG = w * (x - x') exactly and completeness holds for any step count
    lin = torch.nn.Linear(4, 2, bias=False)
    x, base, t = torch.randn(3, 4), torch.zeros(3, 4), torch.zeros(3, dtype=torch.long)
    ig = integrated_gradients(lin, x, base, t, steps=2)
    assert torch.allclose(ig, lin.weight[0] * x, atol=1e-5)
    assert completeness_error(lin, x, base, t, ig) < 1e-5


def test_attributions_point_at_the_shape():
    out = run(steps=60, n_eval=16, ig_steps=16)
    assert loss_decreased(out["losses"])
    assert out["ig_completeness_error"] < 0.5
    # attribution mass on the shape should exceed the shape's area fraction (better than uniform)
    assert out["ig_mass_inside"] > out["shape_area_fraction"]
    assert out["saliency_mass_inside"] > out["shape_area_fraction"]
