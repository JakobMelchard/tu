# 02 Convolutional neural networks

A convolutional layer is a linear map with two constraints baked in: each output depends only on a local window of the input (sparse connectivity) and the same weights are used at every position (parameter sharing). Both follow from the assumption that image statistics are translation-invariant, and they cut the parameter count from $O(HW \cdot H'W')$ for a dense layer to $O(k^2 C_{in} C_{out})$ while making the layer translation-equivariant. Stacking such layers with downsampling grows the receptive field until the last layer sees the whole image; residual connections let the stack be a hundred layers deep. In the project, a pretrained ImageNet backbone from torchvision is the default starting point for any natural-image task, and this note says when that default is wrong.

## Concepts

### Convolution vs cross-correlation

1-D, kernel $w$ of size $k$: convolution $(x * w)[i] = \sum_a x[i - a]\, w[a]$; cross-correlation $(x \star w)[i] = \sum_a x[i + a]\, w[a]$. They differ by a flip of the kernel; since $w$ is learned, the flip is irrelevant and every DL framework implements cross-correlation and calls it "conv" (Goodfellow 9.1 [S15]). 2-D multi-channel layer, tensor layout `[B, C, H, W]` (NCHW, PyTorch default), weight `[C_out, C_in, k, k]`, bias `[C_out]`:
$$y[c_o, i, j] = b[c_o] + \sum_{c_i=1}^{C_{in}} \sum_{a=0}^{k-1}\sum_{b=0}^{k-1} w[c_o, c_i, a, b]\; x[c_i,\; i s + a - p,\; j s + b - p],$$
with stride $s$, zero padding $p$, out-of-range $x$ taken as 0. Each output channel is a full 3-D filter over all input channels; channels are *not* convolved over. Three consequences (Goodfellow 9.2 [S15]): sparse interactions ($k^2 C_{in}$ inputs per output instead of $C_{in} H W$), parameter sharing (the same $w$ at every $(i, j)$), and equivariance to translation: shifting $x$ by $\Delta$ shifts $y$ by $\Delta / s$ (exactly for $s = 1$, up to aliasing otherwise).

### Output size, dilation, transposed convolution

Input size $i$ (per spatial dim), kernel $k$, padding $p$, stride $s$:
$$o = \left\lfloor \frac{i + 2p - k}{s} \right\rfloor + 1.$$
Derivation: the kernel's first position covers indices $[-p, -p + k - 1]$, the last valid start is $\le i + p - k$, starts are spaced by $s$, count $= \lfloor (i + p - k + p)/s \rfloor + 1$. "Same" output size at $s = 1$ needs $p = (k-1)/2$, hence odd $k$ (`padding="same"`). Dilation $d$ inserts $d - 1$ zeros between kernel taps; effective kernel $k_{eff} = d(k-1) + 1$, substitute into the formula. Dilation grows the receptive field without pooling or parameters (Yu & Koltun 2016, used in segmentation). **Deformable convolutions** (Dai et al. 2017 [S41]) go further: a small side branch predicts a 2-D *offset* per kernel tap per position, so the sampling grid bends to follow the object instead of staying a rigid square, and the sampling is made differentiable by bilinear interpolation. It is worth knowing by name beyond the architecture zoo, because assignment 1 [S12] names deformable convolutional layers as its example of a recent idea to attempt for a *Beat the stars* project.

Transposed convolution (`nn.ConvTranspose2d`, "fractionally strided"): the linear adjoint of a conv with the same $k, s, p$, i.e. exactly the operator backprop applies to the output gradient. Output size $o = (i - 1)s - 2p + k + \text{output\_padding}$. Used to upsample in decoders (autoencoders, U-Net, GAN generators). Kernel size not divisible by stride produces checkerboard artifacts (Odena et al. 2016); `Upsample(scale_factor=2)` followed by a $3\times3$ conv avoids them.

### Parameter count and FLOPs

Per conv layer: $\#\text{params} = k^2 C_{in} C_{out} + C_{out}$ (bias; dropped when a BN follows). Multiply-accumulates per forward pass: $\text{MACs} = k^2 C_{in} C_{out} H_o W_o$, FLOPs $\approx 2\,\text{MACs}$. Parameters are independent of the image size; compute is linear in it. A dense layer over the same tensors would need $C_{in} H W \cdot C_{out} H_o W_o$ parameters. Depthwise-separable conv (MobileNet, Howard et al. 2017 [S43]) factorises into a per-channel $k\times k$ conv plus a $1\times1$ channel mixer: $k^2 C_{in} + C_{in} C_{out}$ parameters, roughly $k^2$ times cheaper. Memory for activations, $B \cdot C \cdot H \cdot W$ per layer, usually dominates the parameters in the early high-resolution layers.

### Receptive field

The receptive field $r_l$ is the size (per dim) of the input region that can influence one output unit of layer $l$. With $r_0 = 1$ and kernel $k_l$, stride $s_l$ at layer $l$:
$$r_l = r_{l-1} + (k_l - 1)\prod_{j<l} s_j.$$
Derivation: layer $l$ combines $k_l$ neighbouring units of layer $l-1$, spaced by the cumulative stride $\prod_{j<l} s_j$ in input pixels, so the extremal units are $(k_l - 1)\prod_{j<l} s_j$ apart and each carries a field of $r_{l-1}$. Pooling layers enter with their own $k, s$; dilation replaces $k_l$ by $k_{eff}$. Two stacked $3\times3$ convs have $r = 5$ with $2\cdot 9 C^2$ parameters versus $25 C^2$ for one $5\times5$ (VGG argument). The *effective* receptive field is much smaller than $r_l$ and Gaussian-shaped, since the centre pixel has many more paths to the output (Luo et al. 2016). For classification the final $r$ should cover the object scale; for dense prediction (segmentation) it should cover the context needed per pixel.

### Pooling, invariance vs equivariance

Max pool: $y[i] = \max_{0 \le a < k} x[i s + a]$, gradient routed to the argmax only. Average pool: mean over the window, gradient spread uniformly. Both are parameter-free, per channel, and typically $k = s = 2$ (halve resolution). Global average pooling (Lin et al. 2014, Network in Network [S42]) maps `[B, C, H, W] -> [B, C]` by averaging over all positions; it replaces flatten + dense, is input-size agnostic, and forces each channel to be a class-evidence map.

Equivariance: $f(T x) = T f(x)$, what conv gives (a shifted input yields a shifted feature map). Invariance: $f(T x) = f(x)$, what the classifier needs. Pooling gives local invariance to small shifts (the max over a window does not change if the maximum moves within it); strided downsampling plus global pooling turns this into approximate global translation invariance (Goodfellow 9.3 [S15]). Rotation and scale invariance are *not* built in; they come from augmentation or from specialised architectures.

### Batch norm in conv nets

`nn.BatchNorm2d(C)` normalises each channel with statistics over the $B \times H \times W$ values of that channel, $2C$ learned parameters ($\gamma, \beta$) plus $2C$ running buffers. Standard block: conv (`bias=False`) -> BN -> ReLU. At inference BN is an affine map per channel and can be folded into the conv weights: $W' = \gamma W / \sqrt{\sigma^2_{run} + \epsilon}$, $b' = \beta - \gamma \mu_{run} / \sqrt{\sigma^2_{run} + \epsilon}$. Small-batch caveats as in note 01 (GroupNorm for detection/segmentation with $B \le 4$).

### The ResNet idea

He et al. 2016 [S39]. Plain deep nets showed *degradation*: a 56-layer net has higher *training* error than a 20-layer one, so this is an optimisation failure, not overfitting. A residual block learns the correction to the identity:
$$y = x + F(x; W), \qquad \frac{\partial y}{\partial x} = I + \frac{\partial F}{\partial x}.$$
Through $L$ blocks, $\partial y_L / \partial x_0 = \prod_l (I + J_l)$ expands into a sum over paths that contains the pure identity path, so the gradient reaching early layers has an $O(1)$ component regardless of depth (no product of small Jacobians as in a plain net, cf. note 03 on vanishing gradients). The identity mapping is trivially representable ($F = 0$: zero-init the last BN's $\gamma$ in each block), so a deeper net can never be worse than a shallower one at initialisation. When the shape changes (stride 2, channel doubling) the shortcut is a projection $W_s x$ implemented as a $1\times1$ conv with stride 2.

- Basic block (ResNet-18/34): two $3\times3$ convs with BN, ReLU after the addition.
- Bottleneck block (ResNet-50+): $1\times1$ conv $C \to C/4$, $3\times3$ conv at $C/4$, $1\times1$ conv $C/4 \to C$. For $C = 256$: $256\cdot64 + 9\cdot64\cdot64 + 64\cdot256 = 69{,}632$ params versus $2\cdot 9\cdot 256^2 = 1{,}179{,}648$ for two full-width $3\times3$ convs.
- $1\times1$ convolution: a linear map across channels applied independently at each pixel (a dense layer on the channel axis); used to change channel count, mix channels cheaply, and as the shortcut projection.
- Pre-activation ordering BN-ReLU-conv (He et al. 2016b) keeps the shortcut path completely clean and trains 1000-layer nets.

### Classic architectures

- LeNet-5 (LeCun et al. 1998): conv5-pool-conv5-pool-FC-FC, $\sim 60$k params, digits; the template.
- AlexNet (Krizhevsky et al. 2012): 5 conv + 3 FC, ReLU, dropout, two GPUs; ImageNet top-5 error $15.3\%$ vs $26\%$ before; started the field.
- VGG-16/19 (Simonyan & Zisserman 2015): only $3\times3$ convs and $2\times2$ max pools, channels doubling after each pool ($64 \to 512$), 138M params (most in the FC layers); showed that depth with small kernels beats large kernels.
- ResNet (He et al. 2016 [S39]): residual blocks, BN, global average pooling, 18-152 layers; ResNet-50 is still the default backbone for comparisons.
- U-Net (Ronneberger et al. 2015): encoder-decoder for segmentation; features from each encoder resolution are concatenated into the decoder at the same resolution (skip connections), so the output has both context and pixel-accurate localisation; output `[B, K, H, W]`, per-pixel cross-entropy.
- ConvNeXt (Liu et al. 2022): a ResNet modernised with the transformer training recipe and design choices, $4\times4$ stride-4 patchify stem, $7\times7$ depthwise convs, inverted bottleneck, LayerNorm, GELU, fewer activations; matches Swin transformers on ImageNet with pure convolutions.

### Transfer learning

`torchvision.models.resnet18(weights=ResNet18_Weights.IMAGENET1K_V1)`, then replace the head: `model.fc = nn.Linear(512, K)`. Early layers learn generic filters (edges, colour blobs, textures), later layers task-specific ones (Yosinski et al. 2014), which is why the backbone transfers.

- Feature extraction: freeze the backbone (`for p in backbone.parameters(): p.requires_grad_(False)`), train only the new head; equivalent to logistic regression on fixed features; cheap (no backward through the backbone, features can be precomputed once), robust with $\sim 10^2$-$10^3$ labelled images.
- Fine-tuning: unfreeze the whole net or the top blocks (`layer4`, then `layer3`), train with a small LR for the backbone and a larger one for the head via parameter groups, e.g. `AdamW([{"params": backbone, "lr": 1e-4}, {"params": head, "lr": 1e-3}])`; keep BN layers in eval mode (`m.eval()` for `BatchNorm2d` modules) when batches are small so the ImageNet running statistics are not overwritten. More data -> unfreeze more; more domain shift -> unfreeze more.
- Input: 3 channels (repeat a grayscale channel), resize to $\ge 224$ (the ImageNet training resolution; $\ge 128$ still works), and normalise with the pretrained statistics `mean = [0.485, 0.456, 0.406]`, `std = [0.229, 0.224, 0.225]` after scaling to $[0, 1]$; `weights.transforms()` returns exactly this pipeline.
- When it does not help: strong domain shift (spectrograms, medical modalities, synthetic $32\times32$ shapes) where the ImageNet filters are not meaningful; tiny images where the stem (stride-2 $7\times7$ conv + stride-2 max pool) reduces $32\times32$ to $8\times8$ before the first block and most detail is gone; inputs that are not images at all. Even then a pretrained init often converges faster than random init, so try both and compare learning curves.

### Data augmentation for images

Random resized crop, horizontal flip (only where the label is flip-invariant: not for digits or text), small rotations, colour jitter, random erasing (Zhong et al. 2020) and cutout (DeVries & Taylor 2017), mixup (Zhang et al. 2018, $\tilde x = \lambda x_i + (1-\lambda) x_j$ with the same mix of the labels), CutMix, RandAugment/TrivialAugment for a tuned policy. `torchvision.transforms.v2` applies the same transform to image and mask/boxes. Augment the training split only; evaluate on deterministic, centre-cropped inputs; strong augmentation needs longer training.

## Architecture sketch

`ShapeCNN` from `src/py/cnn_shapes.py` on `make_shapes` data (circle/square/triangle, $32\times32$ grayscale). $C_1, C_2$ are the channel widths set in the class; the numbers below assume $C_1 = 16$, $C_2 = 32$.

```
X [B, 1, 32, 32]
  -> conv3x3(1 -> C1, p=1) - BN - ReLU     -> [B, C1, 32, 32]    r = 3
  -> conv3x3(C1 -> C1, p=1) - BN - ReLU    -> [B, C1, 32, 32]    r = 5
  -> maxpool 2x2, s=2                       -> [B, C1, 16, 16]    r = 6
  -> conv3x3(C1 -> C2, p=1) - BN - ReLU    -> [B, C2, 16, 16]    r = 10
  -> global average pool                    -> [B, C2]
  -> linear(C2 -> 3)                        -> logits [B, 3]
  -> cross-entropy with y [B] in {0, 1, 2}  -> loss []
```

Receptive field by the recursion ($r_0 = 1$, cumulative stride 1, 1, 1, 2):
$r_1 = 1 + 2\cdot1 = 3$, $r_2 = 3 + 2\cdot 1 = 5$, $r_3 = 5 + (2-1)\cdot 1 = 6$, $r_4 = 6 + 2\cdot 2 = 10$. So each unit of the last feature map sees a $10\times10$ patch of the $32\times32$ input; global average pooling then aggregates over all positions, which is what makes the classifier position-independent even though shapes are drawn at random positions. `ShapeCNN.receptive_field()` returns this number. Output sizes: $\lfloor(32 + 2 - 3)/1\rfloor + 1 = 32$ for the padded convs, $\lfloor(32 - 2)/2\rfloor + 1 = 16$ for the pool.

Parameter count with $C_1 = 16, C_2 = 32$ and `bias=False` convs: conv1 $9\cdot1\cdot16 = 144$, BN1 $32$, conv2 $9\cdot16\cdot16 = 2{,}304$, BN2 $32$, conv3 $9\cdot16\cdot32 = 4{,}608$, BN3 $64$, linear $32\cdot3 + 3 = 99$; total $7{,}283$ (`count_params(model)`). MACs for conv2: $9\cdot16\cdot16\cdot32\cdot32 = 2.36$M per image, the most expensive layer despite being the smallest, because it runs at full resolution.

## Pitfalls

- `RuntimeError: shape mismatch` at the first linear layer after changing the input size -> flatten size hard-coded from a fixed resolution -> use global average pooling or `nn.LazyLinear`, and print shapes with a dummy forward `model(torch.zeros(1, 1, 32, 32))`.
- Accuracy stuck at chance on shapes that are trivially distinguishable -> input given as `[B, H, W]` without the channel axis, or as uint8 in $[0, 255]$ while training used $[0, 1]$ -> `unsqueeze(1)`, scale to float once in the data function.
- Validation accuracy collapses although training accuracy is high -> BN running statistics unusable (few steps, tiny batches) -> train longer with $B \ge 16$, or `GroupNorm`, and always `model.eval()` before measuring.
- Pretrained ResNet performs worse than a 3-layer CNN on $32\times32$ inputs -> the stride-4 stem throws away the resolution -> upsample inputs to $\ge 128$, or replace the stem with a $3\times3$ stride-1 conv and drop the max pool, or do not use a pretrained backbone.
- Fine-tuned backbone diverges in the first epoch -> head randomly initialised while the backbone gets the same large LR -> freeze the backbone for the first epochs (or warm up), then unfreeze with a $10\times$ smaller LR.
- Pretrained model gives garbage on your images -> missing ImageNet normalisation or BGR/RGB and channel-order (`[H, W, C]` from PIL/NumPy vs `[C, H, W]`) confusion -> use `weights.transforms()` and check `x.mean()` per channel is near 0 after normalisation.
- Model is translation-invariant on training data but fails for objects near the border -> zero padding makes border positions statistically different, and the receptive field there is truncated -> padding-aware augmentation (random crops with the object near edges) or reflect padding.
- Transposed conv upsampler produces a grid pattern -> kernel size not divisible by stride (checkerboard) -> `k = 4, s = 2` or nearest-neighbour upsample + $3\times3$ conv.
- Segmentation net predicts blobs without sharp edges -> receptive field or decoder resolution too coarse and no skip connections -> U-Net-style skips, and check $r_L$ against the object size.

## Questions

1. Derive the output-size formula and compute the output of a $7\times7$ conv with stride 2, padding 3 on a $224\times224$ input, followed by a $3\times3$ max pool with stride 2, padding 1 (the ResNet stem).
<details><summary>Answer</summary>
Starts of the kernel run from $-p$ to the last index with $\text{start} + k - 1 \le i + p - 1$, spaced by $s$: count $\lfloor (i + 2p - k)/s \rfloor + 1$. Conv: $\lfloor (224 + 6 - 7)/2 \rfloor + 1 = 111 + 1 = 112$. Pool: $\lfloor (112 + 2 - 3)/2 \rfloor + 1 = 55 + 1 = 56$. So `[B, 3, 224, 224] -> [B, 64, 112, 112] -> [B, 64, 56, 56]` before the first residual block.
</details>

2. State the receptive-field recursion, derive it, and give the receptive field after the VGG block conv3-conv3-pool2-conv3-conv3.
<details><summary>Answer</summary>
$r_l = r_{l-1} + (k_l - 1)\prod_{j<l} s_j$: layer $l$ spans $k_l$ units of the previous map whose spacing in input pixels is the cumulative stride, so the span in input pixels grows by $(k_l - 1)$ times that spacing. Sequence: $r = 3, 5$; pool ($k = 2$, stride 1 before it): $6$; then cumulative stride 2: $6 + 2\cdot2 = 10$, $10 + 2\cdot 2 = 14$. The two convs after the pool add 4 pixels each instead of 2: downsampling is what makes the receptive field grow fast.
</details>

3. Why does $y = x + F(x)$ train at depth 100 when a plain stack does not? Give the gradient argument.
<details><summary>Answer</summary>
$\partial y_L/\partial x_0 = \prod_{l}(I + J_l)$ where $J_l = \partial F_l/\partial x$. Expanding the product gives $I + \sum_l J_l + \sum_{l<m} J_m J_l + \dots$; the identity term passes the output gradient to every layer undiminished, whereas a plain net has only the term $\prod_l J_l$, whose norm is bounded by $\prod_l \|J_l\|$ and decays or explodes exponentially in $L$. In addition $F = 0$ is easy to represent, so the deeper net starts at the shallow net's solution and the optimiser only has to learn corrections (He et al. 2016 [S39]).
</details>

4. Count the parameters of a bottleneck block with $C = 512$ and compare with a basic block at the same width.
<details><summary>Answer</summary>
Bottleneck: $1\times1$ $512\to128$: $65{,}536$; $3\times3$ at 128: $9\cdot128^2 = 147{,}456$; $1\times1$ $128\to512$: $65{,}536$; total $278{,}528$ (plus BN). Basic block, two $3\times3$ at 512: $2\cdot 9\cdot 512^2 = 4{,}718{,}592$, $17\times$ more. The $1\times1$ convs move between the wide residual stream and the narrow spatial conv; that is why ResNet-50 has fewer parameters than VGG-16 despite being three times deeper.
</details>

5. Explain equivariance vs invariance for a CNN and state which operations provide which.
<details><summary>Answer</summary>
Equivariance: $f(Tx) = Tf(x)$, the representation moves with the input; stride-1 convolution is exactly translation-equivariant. Invariance: $f(Tx) = f(x)$; max/average pooling give local invariance to shifts smaller than the window, global average pooling gives invariance to any shift that keeps the object inside the image, and the classifier head consumes that invariant vector. Rotations, scale and reflections are neither, unless augmented for or built in (group-equivariant CNNs).
</details>

6. You fine-tune a pretrained ResNet-18 on 500 chest X-rays (grayscale, $1024\times1024$, 2 classes). Describe your recipe and the checks you run.
<details><summary>Answer</summary>
Repeat the grayscale channel to 3, resize to 224-448 (larger if fine structure matters, memory permitting), normalise with ImageNet statistics, replace `fc` with `Linear(512, 2)`. Phase 1: backbone frozen, head trained with AdamW $10^{-3}$ for a few epochs. Phase 2: unfreeze `layer3`-`layer4`, backbone LR $10^{-4}$, head $10^{-3}$, cosine decay, BN frozen in eval mode, augmentation limited to what is anatomically valid (small rotations, crops, brightness; no horizontal flip if laterality matters). Checks: patient-level split, class balance (weighted loss or balanced sampling), learning curves for both phases, AUROC not accuracy, and a from-scratch small CNN baseline since the domain shift from ImageNet is large.
</details>

7. A $32\times32$ grayscale shape classifier has a receptive field of 10 pixels at the last conv layer. A large square fills 28 pixels. Why can the model still classify it, and when would it fail?
<details><summary>Answer</summary>
Each last-layer unit sees only a $10\times10$ patch, so no unit sees the whole square, but local evidence (straight edges, right-angle corners vs curved arcs vs $60^\circ$ corners) is discriminative and global average pooling aggregates the evidence from all patches into one vector. It fails when the decisive cue is global (e.g. distinguishing a square from a rectangle needs relative side lengths beyond 10 pixels), in which case add a strided conv or pooling layer to grow $r$, or use dilation.
</details>

8. Compare a $1\times1$ conv, a global average pool and a dense layer in terms of what they mix.
<details><summary>Answer</summary>
$1\times1$ conv mixes channels at each position independently (weights `[C_out, C_in]`, no spatial mixing, position-independent). Global average pooling mixes positions within each channel (no parameters, no channel mixing). A dense layer on the flattened tensor mixes everything with position-specific weights, `[C H W, N]` parameters, and is neither equivariant nor size-agnostic. A conv net is a factorisation of the dense map into these cheaper pieces.
</details>

## Code

`src/py/cnn_shapes.py`: `make_shapes(n, size=32, seed=0)` -> `X [n,1,size,size]` float in $[0,1]$, `y` in {0 circle, 1 square, 2 triangle}, random position, scale and noise (no download); `ShapeCNN` (conv3x3-BN-ReLU x2, maxpool, conv3x3-BN-ReLU, global avg pool, linear) with the `receptive_field()` helper implementing the recursion above; `accuracy(model, X, y)`; `run(steps=300, device=None, seed=0)` -> `{"losses", "accuracy", "model"}`, training with AdamW and a one-cycle schedule through `common.train_loop`. `python src/py/cnn_shapes.py` trains for a few seconds and prints the accuracy on held-out shapes. `src/py/test_cnn_shapes.py` calls `run` with a small step budget and asserts `common.loss_decreased(losses)` (mean of the last 10% of losses below the mean of the first 10%). Reused by `src/py/xai_saliency.py` and `src/py/autoencoder_vae.py` (`make_shapes(n, size=16)`).

## References

- Goodfellow, Bengio, Courville, *Deep Learning* (2016) [S15]: ch. 9 (convolutional networks: 9.1-9.3 convolution, motivation, pooling; 9.5 variants: stride, padding, dilation; 9.10 history), ch. 7.4 (augmentation), ch. 15.2 (transfer learning), 8.7.1 (batch norm).
- **Lecture 3** [S4], *Convolutional Neural Networks and Visual Computing*, is the lecture this note covers; a quarter of it is the applications tour (detection, segmentation, Mask R-CNN, NAS/AutoKeras) rather than convolution arithmetic.
- LeCun et al. 1998, LeNet-5. Krizhevsky, Sutskever, Hinton 2012, AlexNet. Simonyan & Zisserman 2015, VGG. He et al. 2016 [S39], ResNet; He et al. 2016b, identity mappings (pre-activation). Ronneberger et al. 2015, U-Net. Liu et al. 2022, ConvNeXt. Howard et al. 2017 [S43], MobileNet (depthwise separable). Dai et al. 2017 [S41], deformable convolutions. Szegedy et al. 2015 [S40], Inception. Tan & Le 2020 [S44], EfficientNet (compound scaling, Lecture 5's *efficiently scaling up a model*). Ren et al. 2016 / He et al. 2018 [S45], Faster R-CNN and Mask R-CNN, the detection and segmentation half of Lecture 3.
- Lin et al. 2014 [S42], Network in Network (global average pooling, $1\times1$ conv). Yu & Koltun 2016, dilated convolutions. Luo et al. 2016, effective receptive field. Odena et al. 2016, checkerboard artifacts. Dumoulin & Visin 2018 [S38], *A guide to convolution arithmetic for deep learning* -- **Lecture 3's own reference 1** [S4], and the source of the output-size formulas, which `src/py/shape_formulas.py` re-derives and checks against torch over 936 configurations.
- Ioffe & Szegedy 2015 [S28], batch norm. Wu & He 2018, group norm. Yosinski et al. 2014, transferability of features. Kornblith et al. 2019, do better ImageNet models transfer better.
- DeVries & Taylor 2017 [S33], cutout. Zhong et al. 2020, random erasing. Zhang et al. 2018, mixup. Yun et al. 2019, CutMix. Cubuk et al. 2020, RandAugment.
