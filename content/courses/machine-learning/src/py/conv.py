"""Convolution arithmetic: output size, 2-D convolution, pooling, parameter counts.

The calculation section of every 184.702 paper since 2020 contains one of these
[S11]: "given a 7x7 input and a 3x3 filter with stride 2, tick the right output"
(E20c), "calculate the output size of a convolution" (E23a), or the multiple
answer item "an output of a convolutional layer is larger when padding
increases / stride decreases" (E25b, E26a).

Reference: Goodfellow, Bengio & Courville, *Deep Learning*, ch. 9 [S26].
Note 13 works the numbers.  Deep-learning "convolution" is cross-correlation --
the kernel is not flipped -- which is what `conv2d` implements and what every
framework calls convolution; `flip=True` gives the mathematical convolution.

Run `python conv.py` for the 7x7 / 3x3 / stride-2 example of E20c.
"""
import numpy as np


def output_size(input_size, kernel, stride=1, padding=0, dilation=1):
    """O = floor((I - K_eff + 2P) / S) + 1 with K_eff = dilation*(K-1)+1 [S26].

    Larger padding -> larger output; larger stride -> smaller output.  That is
    the whole content of the E25b / E26a multiple-answer question.
    """
    k_eff = dilation * (kernel - 1) + 1
    if input_size + 2 * padding < k_eff:
        raise ValueError("kernel larger than the padded input")
    return (input_size - k_eff + 2 * padding) // stride + 1


def conv_output_shape(shape, kernel, stride=1, padding=0, dilation=1):
    """Apply `output_size` to a (height, width) pair."""
    k = (kernel, kernel) if np.isscalar(kernel) else kernel
    s = (stride, stride) if np.isscalar(stride) else stride
    p = (padding, padding) if np.isscalar(padding) else padding
    d = (dilation, dilation) if np.isscalar(dilation) else dilation
    return tuple(output_size(shape[i], k[i], s[i], p[i], d[i]) for i in range(2))


def same_padding(kernel):
    """Padding that keeps the size at stride 1; requires an odd kernel."""
    if kernel % 2 == 0:
        raise ValueError("'same' padding needs an odd kernel size")
    return (kernel - 1) // 2


def pad2d(x, padding, value=0.0):
    """Zero-pad a 2-D array symmetrically."""
    p = (padding, padding) if np.isscalar(padding) else padding
    return np.pad(np.asarray(x, float), ((p[0], p[0]), (p[1], p[1])),
                  mode="constant", constant_values=value)


def _windows(x, kh, kw, stride):
    """Yield (i, j, patch) for every valid window position."""
    s = (stride, stride) if np.isscalar(stride) else stride
    oh = (x.shape[0] - kh) // s[0] + 1
    ow = (x.shape[1] - kw) // s[1] + 1
    for i in range(oh):
        for j in range(ow):
            yield i, j, x[i * s[0]:i * s[0] + kh, j * s[1]:j * s[1] + kw]


def conv2d(x, kernel, stride=1, padding=0, flip=False):
    """2-D convolution (cross-correlation unless flip=True) of a single channel."""
    k = np.asarray(kernel, float)
    if flip:
        k = k[::-1, ::-1]
    xp = pad2d(x, padding)
    kh, kw = k.shape
    out = np.zeros(conv_output_shape(xp.shape, (kh, kw), stride))
    for i, j, patch in _windows(xp, kh, kw, stride):
        out[i, j] = float(np.sum(patch * k))
    return out


def max_pool2d(x, size=2, stride=None, padding=0):
    """Max pooling; stride defaults to the window size (non-overlapping)."""
    return _pool2d(x, size, stride, padding, np.max)


def avg_pool2d(x, size=2, stride=None, padding=0):
    """Average pooling."""
    return _pool2d(x, size, stride, padding, np.mean)


def _pool2d(x, size, stride, padding, reduce_fn):
    stride = size if stride is None else stride
    xp = pad2d(x, padding, value=-np.inf if reduce_fn is np.max and padding else 0.0)
    k = (size, size) if np.isscalar(size) else size
    out = np.zeros(conv_output_shape(xp.shape, k, stride))
    for i, j, patch in _windows(xp, k[0], k[1], stride):
        out[i, j] = float(reduce_fn(patch))
    return out


def conv_params(kernel, in_channels, out_channels, bias=True, ndim=2):
    """Trainable parameters of a conv layer: K^ndim * D * D' (+ D').

    Independent of the input size -- that is what weight sharing buys.  The
    1-D case K*D*D' is the sibling course's exam question [S16].
    """
    weights = (kernel ** ndim) * in_channels * out_channels
    return weights + (out_channels if bias else 0)


def dense_params(in_features, out_features, bias=True):
    """Parameters of a fully connected layer: d_in*d_out + d_out [S16]."""
    return in_features * out_features + (out_features if bias else 0)


def receptive_field(kernels, strides=None):
    """Receptive field of a stack of conv layers, r_{l} = r_{l-1} + (k_l - 1) * prod(s_{<l})."""
    strides = [1] * len(kernels) if strides is None else list(strides)
    r, jump = 1, 1
    for k, s in zip(kernels, strides):
        r += (k - 1) * jump
        jump *= s
    return r


if __name__ == "__main__":
    np.set_printoptions(precision=0, suppress=True)

    print("output-size formula O = floor((I - K + 2P)/S) + 1")
    for (i, k, s, p) in [(7, 3, 2, 0), (7, 3, 1, 0), (7, 3, 1, 1), (28, 5, 1, 2), (28, 5, 2, 0)]:
        print(f"  I={i:3d} K={k} S={s} P={p}  ->  O={output_size(i, k, s, p)}")
    print("  padding up -> bigger output; stride up -> smaller output  (E25b, E26a)")

    # E20c: a 7x7 input, a 3x3 filter/window, stride 2.
    I = np.add.outer(np.arange(7), np.arange(7)).astype(float)   # I[i,j] = i + j
    K = np.array([[1.0, 0.0, -1.0]] * 3)                         # vertical edge detector
    print("\ninput I[i,j] = i + j (7x7)\n", I)
    print("\nconv2d with the 3x3 vertical-edge kernel, stride 2 ->",
          conv_output_shape(I.shape, 3, 2))
    print(conv2d(I, K, stride=2))
    print("(constant -6: a linear ramp has a constant gradient)")
    print("\nmax_pool2d 3x3, stride 2 ->", conv_output_shape(I.shape, 3, 2))
    print(max_pool2d(I, size=3, stride=2))

    print("\nparameter counts")
    print("  conv 3x3, 32 -> 64 channels :", conv_params(3, 32, 64))
    print("  dense on the same volumes   :", dense_params(32 * 32 * 32, 32 * 32 * 64))
    print("  receptive field of 3x(3x3, stride 1):", receptive_field([3, 3, 3]))
