"""Tests for cnn_synthetic.py: data generator, shapes, determinism and the accuracy bar."""
import numpy as np
import torch

from cnn_synthetic import CLASSES, SmallCNN, count_params, make_shapes, train, trained_model
from conv_arithmetic import receptive_field


def test_make_shapes_is_seeded_and_well_formed():
    X1, y1, m1 = make_shapes(50, seed=3)
    X2, y2, m2 = make_shapes(50, seed=3)
    assert torch.equal(X1, X2) and torch.equal(y1, y2) and (m1 == m2).all()
    assert X1.shape == (50, 1, 32, 32) and X1.dtype == torch.float32
    assert set(y1.tolist()) <= set(range(len(CLASSES)))
    assert m1.reshape(50, -1).sum(1).min() > 10               # every image has an object
    assert not m1[:, 0, :].any() and not m1[:, :, 0].any()    # never touching the border


def test_output_shape_and_parameter_count():
    model = SmallCNN()
    assert model(torch.zeros(3, 1, 32, 32)).shape == (3, 4)
    # conv1 9*1*16, BN 32, conv2 9*16*32, BN 64, conv3 9*32*32, BN 64, fc 32*4+4
    assert count_params(model) == 144 + 32 + 4608 + 64 + 9216 + 64 + 132 == 14260
    assert model(torch.zeros(1, 1, 48, 48)).shape == (1, 4)   # GAP makes it size-agnostic


def test_receptive_field_of_feature_layer():
    assert receptive_field([(3, 1), (2, 2), (3, 1), (2, 2), (3, 1)])[0] == 18


def test_training_is_deterministic():
    X, y, _ = make_shapes(128, seed=5)
    runs = []
    for _ in range(2):
        torch.manual_seed(0)
        runs.append(train(SmallCNN(), X, y, epochs=1, seed=0))
    assert np.allclose(runs[0], runs[1])


def test_small_cnn_reaches_accuracy_threshold():
    out = trained_model()
    L = out["losses"]
    assert np.mean(L[-10:]) < 0.5 * np.mean(L[:10])
    assert out["test_acc"] > 0.9
