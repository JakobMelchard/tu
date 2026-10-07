# 04 Convolutional neural networks

> TISS item 4, first half ("CNNs for classification") [S1, S3]. Catalogue
> weight: the largest single block; **output shape, receptive field, pooling
> by hand and parameter counts** are the recurring calculations [S7-S9].
> Books: Goodfellow ch. 9 [S11]; Drori ch. 5 [S12]; Dumoulin & Visin [S13].
> **Read first:** [ADL 02 CNNs](../../applied-deep-learning/notes/02-cnns.md)
> (output-size derivation, receptive-field recursion, dilation, transposed
> conv, BN folding, ResNet gradient argument, transfer-learning recipe) and
> [ML 13 deep learning](../../machine-learning/notes/13-deep-learning.md).
> Not repeated here. This note adds the DLVC catalogue's forms: locally
> connected vs convolutional, the numbers it asks for, the architecture line
> LeNet to ResNet, and ViT in one paragraph.

## Definitions

**Dense, locally connected, convolutional** [S9]. Input $W\times H\times D$,
output $W\times H\times F$ (padding keeps the size), $3\times3$ connectivity:

| layer | each output unit sees | weights + biases |
|---|---|---|
| dense | all $WHD$ inputs | $WHD\cdot WHF + WHF$ |
| locally connected | a $3\times3\times D$ window, **own weights per position** | $WHF(9D + 1)$ |
| convolutional | the same window, **weights shared over positions** | $F(9D + 1)$ |

Sparse connectivity encodes locality (pixels far apart are weakly related);
sharing encodes stationarity (a detector useful here is useful there) and
yields translation equivariance. One set of shared weights is a **feature
map**; $F$ maps detect $F$ patterns.

**Output size** per axis: $o = \lfloor (i + 2p - d(k-1) - 1)/s \rfloor + 1$;
transposed: $o = (i-1)s - 2p + d(k-1) + p_{out} + 1$ [S13].
**Parameters** $k^2 C_{in} C_{out}/g + C_{out}$, **MACs**
$k^2 C_{in} C_{out} H_o W_o/g$ ($g$ groups; FLOPs $\approx 2\times$ MACs).
**Receptive field** $r_l = r_{l-1} + (k_l - 1)\,j_{l-1}$,
$j_l = j_{l-1}s_l$, $r_0 = j_0 = 1$ ($j$ = cumulative stride, "jump").

**Pooling.** Max or average over $k\times k$ windows per channel, no
parameters; halves resolution at $k = s = 2$, gives local shift invariance and
grows the receptive field. Alternatives: strided convolution (learned
downsampling). Opposites [S7]: nearest/bilinear upsampling, transposed
convolution, sub-pixel convolution (convolve to $r^2C$ channels, then
rearrange to $rH\times rW\times C$). **Global average pooling** maps
`[C,H,W]` to `[C]`: joins the feature extractor to the classifier for any input
size, with no parameters.

**The two stages** [S6, S9]. Feature extraction (conv, non-linearity, pool,
repeated: resolution falls, channels rise) and classification (dense layers or
GAP + linear). What joins them: a flatten (fixes the input size) or GAP.

**Batch norm** [S18]. Per channel, over batch and positions:
$\hat z = (z - \mu_B)/\sqrt{\sigma_B^2 + \epsilon}$, $y = \gamma\hat z + \beta$
(2 learned parameters per channel). Test time: running averages of
$\mu, \sigma^2$ replace the batch statistics, so single inputs work [S7, S9].
Placed after conv, before the non-linearity; the conv bias is redundant. The
batch noise regularises.

**Depth.** Number of layers with weights. More depth: larger receptive field,
more compositional features, but harder optimisation (vanishing gradients;
the degradation problem, where a deeper plain net has higher *training*
error [S17]). Residual blocks $y = x + F(x)$ fix it (ADL 02 for the gradient
argument). **Pointwise** ($1\times1$) conv: a per-pixel linear map across
channels; used as **bottleneck** $C \to C/4 \to C$ around the $3\times3$.

## The architecture line (dates are publication years)

| net | year | what it introduced | size |
|---|---|---|---|
| LeNet-5 [S14] | 1998 | conv-pool-conv-pool-FC on $32\times32$ digits, trained by backprop | ~60 k |
| AlexNet [S15] | 2012 | ReLU, dropout, GPUs, data augmentation; ImageNet top-5 15.3 % | ~60 M |
| VGG [S16] | 2014 | only $3\times3$ convs and $2\times2$ pools, 16-19 layers | 138 M (VGG-16) |
| GoogLeNet [S16] | 2014 | Inception modules, $1\times1$ bottlenecks, GAP, 22 layers | ~12x fewer than AlexNet |
| ResNet [S17] | 2015 | residual blocks, BN, 152 layers | 25.6 M (ResNet-50) |
| MobileNet [S16] | 2017 | depthwise-separable convs for mobile | ~4 M |
| ViT [S41] | 2020 | $16\times16$ patches as tokens, a transformer encoder | 86 M (B/16) |

Why $3\times3$ [S9]: two stacked $3\times3$ have the receptive field of one
$5\times5$ ($r = 5$) with $18C^2$ instead of $25C^2$ weights and an extra
non-linearity. **ViT** [S41]: cut the image into $P\times P$ patches, embed
each linearly, add position embeddings, run self-attention; weaker inductive
bias than a CNN, so it needs more data or pre-training [S7]. Attention itself:
[ADL 06](../../applied-deep-learning/notes/06-transformers.md).

## Transfer learning (DLVC form)

The catalogue's "bird species app" [S7, S9]: (1) classification task; (2)
collect a labelled set, split it; (3) take an ImageNet-pretrained backbone
(pre-training was done by someone else); (4) replace the head with a
$K$-way linear layer; (5) train the head with the backbone frozen; (6)
fine-tune the top blocks with a small learning rate if data allow; (7)
evaluate on the untouched test split. Recipe details and when it fails: ADL 02.

## Worked example

**The catalogue's numbers.** $3\times32\times32$, $3\times3$, 16 maps,
stride 1, no padding: $o = 32 - 3 + 1 = 30$, output $16\times30\times30$,
parameters $16(27 + 1) = 448$ [S7]. Conv3, conv3, pool 2/2, conv3, conv3:
$r = 3, 5, 6, 10, 14$ [S9]. Max pool 2/2 of rows $(1,1,2,4 \mid 5,6,7,8 \mid
3,2,1,0 \mid 1,2,3,4)$: $\begin{psmallmatrix}6&8\\3&4\end{psmallmatrix}$ [S9].
Stride-2 pools for $64\times64$ with size-preserving convs: 64, 32, 16, 8, 4;
three or four, so the last map is $8\times8$ or $4\times4$: enough pooling that
$r$ covers the object, not so much that spatial layout disappears.

**A small VGG-style net on $3\times64\times64$** (`print_trace`): conv3-32,
conv3-32, pool, conv3-64, conv3-64, pool, GAP, fc-10, all padded.

| layer | output | params | MACs | $r$ |
|---|---|---|---|---|
| conv 3 to 32 | $32\times64\times64$ | 896 | 3.5 M | 3 |
| conv 32 to 32 | $32\times64\times64$ | 9 248 | 37.7 M | 5 |
| pool | $32\times32\times32$ | 0 | | 6 |
| conv 32 to 64 | $64\times32\times32$ | 18 496 | 18.9 M | 10 |
| conv 64 to 64 | $64\times32\times32$ | 36 928 | 37.7 M | 14 |
| pool, GAP, fc | $10$ | 650 | 640 | 16 |

Total 66 218 parameters, 97.9 M MACs. The second conv costs as much as the
fourth with a quarter of its parameters: compute follows resolution,
parameters follow channels. With $r = 16$ on a 64-pixel image, GAP averages
local evidence: fine for texture-like cues, too little for global shape.

**Bottleneck and separable savings.** $C = 256$: bottleneck 70 016 weights vs
1 180 160 for two $3\times3$ (with biases). Depthwise $3\times3$ on 64 channels
plus pointwise $64\to128$: 8 768 vs 73 728 for a full $3\times3$, 8.4x fewer.

## Pitfalls

- The student key's $16\times10\times10$ [S7]: output size is not "divide by 3".
- Receptive field additions after a pool are multiplied by the cumulative
  stride; forgetting this gives 10 instead of 14.
- Counting BN's running mean/var as parameters (they are buffers).
- LeNet-5's C3 used a partial connection table (1 516 weights); a fully
  connected C3 gives 2 416 and 61 706 in total (`LENET5` in the code).
- ImageNet CNNs are biased towards texture, not shape [S43]: good accuracy
  does not mean the features are the ones a human uses.

## Exam-style questions

1. **Two key differences of a conv layer to a linear layer, and their
   motivation for images?** *(20, 21)* Sparse connectivity (locality of image
   statistics) and weight sharing (stationarity, equivariance, parameter count
   independent of image size). Most common activation: ReLU.
2. **Parameters of a locally connected vs a convolutional layer, $W\times H\times D$
   input, $3\times3$, $F$ maps.** *(17, 20)* $WHF(9D+1)$ vs $F(9D+1)$.
3. **Receptive field after conv3, conv3, pool2/2, conv3, conv3, and why
   $3\times3$?** *(17, 20)* 14. Stacking small kernels gives the same field with
   fewer parameters and more non-linearity.
4. **What are residual networks and which problem do they overcome? Sketch a
   block.** *(17, 20, 22)* $y = \mathrm{ReLU}(x + F(x))$, $F$ = conv-BN-ReLU-conv-BN;
   degradation of deep plain nets: the identity path carries gradient and
   makes "do nothing" easy.
5. **How are images made compatible with a transformer, and what is its
   theoretical advantage over a CNN?** *(22)* Non-overlapping patches,
   linearly embedded, plus position embeddings, as a token sequence; global
   interactions from layer one and less hard-wired bias, which pays off with
   enough data.

## Code

- `src/py/conv_arithmetic.py`: `conv_out`, `convT_out`, `same_padding`,
  `conv_params`, `conv_macs`, `receptive_field`, `trace`, `print_trace`,
  `to_torch`, `empirical_receptive_field`, `LENET5`, `EXAM_2017_RF`.
- `src/py/cnn_synthetic.py`: `SmallCNN` (receptive field 18 at `features`),
  `make_shapes`, `train`, `trained_model`, `count_params`.
- `src/py/backprop_scratch.py`: `maxpool_forward` (the $4\times4$ example).
