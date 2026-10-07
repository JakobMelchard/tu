# 01 Recap: computer vision and image processing

> TISS item 1 [S1, S3]. Catalogue weight: the task-definition question is in
> every catalogue [S7, S8, S9]; the filtering material is the prerequisite
> "image processing" named on the homepage [S4], not examined on its own.
> Textbook: Szeliski ch. 2-3, 7 [S42].

## What it is

The vocabulary a CNN is built from: an image is a sampled, quantised function;
a convolutional layer is a bank of learned linear shift-invariant filters;
pooling and strides are resampling. Everything here reappears in note 04 with
learned kernels.

## Definitions

**Digital image.** $I: \{0..H-1\}\times\{0..W-1\} \to \mathbb R^C$, stored as a
tensor `[C, H, W]` (PyTorch NCHW with a batch axis). 8-bit sensors quantise
to $\{0..255\}$; networks want floats, usually scaled to $[0,1]$ and then
standardised per channel (note 08).

**Linear shift-invariant (LSI) filter.** $T$ linear with
$T[I(\cdot - a)] = (TI)(\cdot - a)$. Every LSI operator is a convolution:
$$ (I * K)[i,j] = \sum_{u,v} I[i-u,\, j-v]\, K[u,v], \qquad
   (I \star K)[i,j] = \sum_{u,v} I[i+u,\, j+v]\, K[u,v]. $$
$*$ is convolution, $\star$ correlation; they differ by a flip of $K$. Deep
learning libraries compute $\star$ and call it convolution; with learned $K$ the
flip is irrelevant [S11 §9.1]. Convolution is commutative and associative
(filters compose into one filter), correlation is not.

**Convolution theorem.** $\mathcal F(I * K) = \mathcal F(I)\,\mathcal F(K)$
(circular boundary). A filter is a pointwise multiplier in frequency: box and
Gaussian are low-pass, derivative filters high-pass.

**Boundary handling.** zero ("constant"), replicate, reflect, circular. Zero
padding makes border outputs statistically different, which a CNN can exploit
to learn absolute position.

**Separable kernel.** $K = a b^\top$ ($K$ rank 1): filter rows with $b$, then
columns with $a$. Cost per pixel $2k$ instead of $k^2$. The Gaussian
$G_\sigma(u,v) = \frac{1}{2\pi\sigma^2}e^{-(u^2+v^2)/2\sigma^2} = g_\sigma(u)g_\sigma(v)$
is separable; truncate at $\pm3\sigma$ ($k \approx 6\sigma + 1$).

**Smoothing.** Box (mean) filter: ringing in frequency (sinc). Gaussian: no
ringing, $\sigma$ sets the scale. Median: non-linear, removes salt-and-pepper
noise, preserves edges; not a convolution.

**Edges.** Large $\|\nabla I\|$. Central difference $[-1, 0, 1]$ combined with
smoothing $[1, 2, 1]^\top$ in the other direction gives Sobel:
$$ S_x = \begin{psmallmatrix}-1&0&1\\-2&0&2\\-1&0&1\end{psmallmatrix}, \quad
   S_y = S_x^\top, \quad \|\nabla I\| \approx \sqrt{g_x^2+g_y^2}, \quad
   \theta = \operatorname{atan2}(g_y, g_x). $$
Laplacian $\nabla^2 I$ (zero crossings at edges) is noise-sensitive, hence
Laplacian of Gaussian. **Canny**: Gaussian smoothing, gradient, non-maximum
suppression along $\theta$ (thin edges), hysteresis with two thresholds
(connected weak edges survive). The first-layer filters of trained CNNs look
like oriented edge and colour-blob detectors [S15], which is why they transfer
(note 04).

**Colour.** RGB is device-dependent. Luma (BT.601)
$Y = 0.299R + 0.587G + 0.114B$. HSV separates hue from brightness, which is why
"colour jitter" augmentations act on hue/saturation. A grayscale input to an
RGB-pretrained net: repeat the channel three times.

**Sampling and aliasing.** Sampling at rate $f_s$ represents frequencies below
the Nyquist limit $f_s/2$ faithfully; higher ones fold back (alias).
Downsampling must be preceded by a low-pass filter. A stride-2 convolution or
max pool without blurring violates this, which is why CNN outputs are not
shift-invariant for odd shifts [S35 Zhang 2019] (tested in
`test_augment.py`). Interpolation for upsampling: nearest, bilinear (a
$2\times2$ tent filter), bicubic.

**Vision tasks** [S7, S9]. *Classification*: given a finite label set, which
label fits the image. *Detection*: every instance, as box + label; zero or
many per image. *Semantic segmentation*: a label per pixel. *Instance
segmentation*: a mask per instance. Classification challenges named in every
catalogue: **viewpoint/pose, illumination, deformation, occlusion, background
clutter, intra-class variation** (plus scale). Detection is harder: unknown
object count, localisation, and the classification challenges at every
candidate location.

## Worked example

**Sobel on a vertical step.** $I[i,j] = 0$ for $j < 3$, $1$ for $j \ge 3$ on
a $5\times6$ image, correlation with $S_x$, no padding. A patch whose columns are
$(0, 1, 1)$ or $(0, 0, 1)$ gives $g_x = (1+2+1)\cdot 1 = 4$; patches entirely
on one side give 0. So the $3\times4$ output has two columns of 4 (at $j = 2, 3$
of the input, where the step lies between) and zeros elsewhere: the edge
response is two pixels wide, which is what NMS thins.

**Separable cost.** $7\times7$ Gaussian on a $1024^2$ image: $49 \times 2^{20}
\approx 5.1\cdot10^7$ MACs direct vs $14 \times 2^{20} \approx 1.5\cdot10^7$
separable. The same factorisation motivates depthwise-separable convolutions
(note 04).

**Aliasing.** $x[m] = \cos(2\pi m/3)$, period 3 px, frequency $1/3$
cycles/px. Keep every second sample: $x[2n] = \cos(4\pi n/3) = \cos(2\pi n/3)$,
period 3 *samples* = 6 original pixels. The new Nyquist limit is $1/4$
cycles/px; $1/3$ folds to $1/2 - 1/3 = 1/6$. A $[1,2,1]/4$ blur before the
decimation attenuates this component by $|\tfrac12 + \tfrac12\cos(2\pi/3)| = \tfrac14$.

## Pitfalls

- Calling DL "convolution" a convolution in the signal-processing sense
  (it is correlation; matters only for hand-designed kernels).
- Forgetting that filtering is linear but the median, max pool and ReLU are not.
- Downsampling without smoothing, then being surprised by shift sensitivity.
- Treating $[H, W, C]$ (PIL, NumPy) and $[C, H, W]$ (PyTorch) as the same.
- Horizontal flips are a symmetry of natural scenes but not of text or digits (note 08).

## Exam-style questions

1. **Define image classification and name five challenges with an example
   each. How does detection differ and which is harder?** *(17, 20, 22)*
   A label from a finite set for the whole image. Viewpoint (a cat from
   behind), illumination (backlit), deformation (stretched cat), occlusion
   (behind a curtain), background clutter (cat on a patterned carpet),
   intra-class variation (breeds). Detection outputs a variable number of
   boxes + labels: localisation and counting on top of classification, so harder.
2. **Why are convolution and correlation interchangeable in a CNN?** *(ours)*
   They differ by flipping $K$; a learned kernel absorbs the flip, and the
   gradient of either is the other one applied to the upstream gradient.
3. **Why is a Gaussian filter separable and what does it save?** *(ours)*
   $e^{-(u^2+v^2)/2\sigma^2} = e^{-u^2/2\sigma^2}e^{-v^2/2\sigma^2}$, rank 1;
   $2k$ instead of $k^2$ multiplications per pixel.
4. **What happens if you downsample an image by 2 without filtering? Relate to
   stride-2 layers.** *(ours)* Frequencies above $1/4$ cycles/px alias to lower
   ones; content changes with a one-pixel shift. Strided CNN layers alias the
   same way; blur-pooling (a fixed low-pass before the stride) restores
   approximate shift invariance [S35].
5. **Why do generic vector classifiers perform poorly on raw pixels?**
   *(17, 20)* The vector ignores the 2-D neighbourhood structure; the
   dimension is huge ($3\cdot224^2 \approx 1.5\cdot10^5$); a one-pixel shift
   changes the vector a lot while the label stays: the invariances must be
   learned from data instead of being built in.

## Code

- `src/py/backprop_scratch.py`: `conv2d_forward` is correlation with stride and zero padding.
- `src/py/augment.py`: `hflip`, `translate`; `test_augment.py` checks that
  correlation with a flipped kernel commutes with a flip, that circular
  convolution commutes with `torch.roll`, and the stride-2 aliasing claim.
- `src/py/conv_arithmetic.py`: `conv_out`, the sampling grid of a strided filter.
