"""Tests for conv.py: the output-size formula, convolution, pooling, parameter counts.

The reference results are the exam's own questions [S11] and the standard
identities of Goodfellow, Bengio & Courville ch. 9 [S26].
"""
import numpy as np
import pytest

from conv import (avg_pool2d, conv2d, conv_output_shape, conv_params, dense_params,
                  max_pool2d, output_size, pad2d, receptive_field, same_padding)


def test_output_size_formula():
    # O = floor((I - K + 2P)/S) + 1
    assert output_size(7, 3, stride=2) == 3           # E20c
    assert output_size(7, 3, stride=1) == 5
    assert output_size(7, 3, stride=1, padding=1) == 7
    assert output_size(28, 5, stride=1, padding=2) == 28
    assert output_size(28, 5, stride=2) == 12
    assert output_size(5, 5) == 1                     # kernel = input -> 1


def test_padding_up_and_stride_down_grow_the_output():
    """The E25b / E26a multiple-answer question, as a property."""
    base = output_size(32, 3, stride=2, padding=1)
    assert output_size(32, 3, stride=2, padding=2) > base    # more padding -> bigger
    assert output_size(32, 3, stride=2, padding=0) < base    # less padding -> smaller
    assert output_size(32, 3, stride=1, padding=1) > base    # smaller stride -> bigger
    assert output_size(32, 3, stride=4, padding=1) < base    # bigger stride -> smaller


def test_same_padding_preserves_the_size():
    for k in (1, 3, 5, 7):
        assert output_size(20, k, stride=1, padding=same_padding(k)) == 20
    with pytest.raises(ValueError):
        same_padding(4)


def test_kernel_larger_than_input_is_rejected():
    with pytest.raises(ValueError):
        output_size(3, 5)


def test_conv2d_matches_a_hand_computed_patch():
    x = np.arange(16, dtype=float).reshape(4, 4)
    k = np.array([[1.0, 0.0], [0.0, -1.0]])
    out = conv2d(x, k)
    assert out.shape == (3, 3)
    # top-left window [[0,1],[4,5]] -> 1*0 + 0*1 + 0*4 + (-1)*5 = -5
    assert out[0, 0] == pytest.approx(-5.0)
    assert np.allclose(out, -5.0)        # a linear ramp: the response is constant


def test_e20c_seven_by_three_stride_two():
    """The E20c question: 7x7 input, 3x3 filter/window, stride 2 -> 3x3 output."""
    I = np.add.outer(np.arange(7), np.arange(7)).astype(float)
    K = np.array([[1.0, 0.0, -1.0]] * 3)              # vertical edge detector
    conv = conv2d(I, K, stride=2)
    assert conv.shape == (3, 3)
    assert np.allclose(conv, -6.0)

    pooled = max_pool2d(I, size=3, stride=2)
    assert pooled.shape == (3, 3)
    # each window's maximum is its bottom-right corner, i + j with i, j in {2,4,6}
    assert np.allclose(pooled, np.add.outer([2, 4, 6], [2, 4, 6]))


def test_conv2d_flip_gives_mathematical_convolution():
    x = np.zeros((5, 5)); x[2, 2] = 1.0                # an impulse
    k = np.array([[1.0, 2.0, 3.0], [4.0, 5.0, 6.0], [7.0, 8.0, 9.0]])
    # true convolution reproduces the kernel at the impulse; cross-correlation
    # (what every deep-learning framework calls "convolution") flips it
    assert np.allclose(conv2d(x, k, padding=1, flip=True)[1:4, 1:4], k)
    assert np.allclose(conv2d(x, k, padding=1, flip=False)[1:4, 1:4], k[::-1, ::-1])


def test_conv2d_against_scipy():
    rng = np.random.default_rng(0)
    x, k = rng.normal(size=(9, 11)), rng.normal(size=(3, 3))
    scipy_signal = pytest.importorskip("scipy.signal")
    ours = conv2d(x, k)
    ref = scipy_signal.correlate2d(x, k, mode="valid")
    assert np.allclose(ours, ref)


def test_pooling():
    x = np.array([[1.0, 2, 3, 4],
                  [5, 6, 7, 8],
                  [9, 10, 11, 12],
                  [13, 14, 15, 16]])
    assert np.allclose(max_pool2d(x, 2), [[6, 8], [14, 16]])
    assert np.allclose(avg_pool2d(x, 2), [[3.5, 5.5], [11.5, 13.5]])
    # overlapping windows: 3x3 with stride 1 on a 4x4 gives 2x2
    assert max_pool2d(x, size=3, stride=1).shape == (2, 2)


def test_pad2d():
    x = np.ones((2, 2))
    assert pad2d(x, 1).shape == (4, 4)
    assert pad2d(x, 1)[0, 0] == 0.0
    assert pad2d(x, (1, 2)).shape == (4, 6)


def test_parameter_counts():
    """Weight sharing: the conv count is independent of the image size [S26]."""
    assert conv_params(3, 32, 64) == 3 * 3 * 32 * 64 + 64
    assert conv_params(3, 32, 64, bias=False) == 18432
    assert conv_params(5, 1, 6, ndim=1) == 5 * 1 * 6 + 6          # Conv1d: K*D*D' [S16]
    assert dense_params(100, 10) == 100 * 10 + 10                 # d_in*d_out + d_out [S16]
    # and it is far smaller than the dense equivalent
    assert conv_params(3, 32, 64) < dense_params(32 * 32 * 32, 32 * 32 * 64) / 1000


def test_conv_output_shape_and_receptive_field():
    assert conv_output_shape((32, 32), 3, stride=1, padding=1) == (32, 32)
    assert conv_output_shape((7, 9), 3, stride=2) == (3, 4)
    # three stacked 3x3 layers see the same 7x7 window as one 7x7 layer
    assert receptive_field([3, 3, 3]) == 7
    # a stride-2 first layer widens what the second layer sees: 1 + 2 + 2*2 = 7
    assert receptive_field([3, 3], strides=[2, 1]) == 7
