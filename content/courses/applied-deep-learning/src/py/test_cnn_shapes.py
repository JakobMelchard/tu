import torch

from cnn_shapes import ShapeCNN, make_shapes, output_size, run
from common import loss_decreased


def test_shapes_and_conv_arithmetic():
    X, y = make_shapes(30, size=32, seed=1)
    assert X.shape == (30, 1, 32, 32) and X.min() >= 0 and X.max() <= 1 and set(y.tolist()) <= {0, 1, 2}
    conv = torch.nn.Conv2d(1, 1, 5, stride=2, padding=1)
    assert conv(X[:1]).shape[-1] == output_size(32, 5, s=2, p=1)
    assert ShapeCNN.receptive_field() == 10


def test_training_decreases_loss():
    out = run(steps=60, n_train=600, n_test=200)
    assert loss_decreased(out["losses"])
    assert out["accuracy"] > 0.4  # above chance after a few seconds
