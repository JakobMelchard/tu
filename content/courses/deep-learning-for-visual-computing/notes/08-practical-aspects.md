# 08 Practical aspects: preprocessing, augmentation, regularisation, training, visualisation

> TISS items 7 and 8, "software libraries and practical aspects" and
> "preprocessing, data augmentation, regularization, visualizations" [S1, S3].
> Catalogue weight: high; augmentation for digits, dropout, weight decay,
> batch norm, learning-rate sketches, initialisation, imbalance in 2017-2022
> [S7-S9]. Goodfellow ch. 7-8 [S11]; Drori ch. 4 [S12].
> Already written in depth, read instead of this where it overlaps:
> [ADL 01 training fundamentals](../../applied-deep-learning/notes/01-training-fundamentals.md)
> (optimisers, schedules, initialisation, BN, dropout, augmentation),
> [ADL 10 practical](../../applied-deep-learning/notes/10-practical.md)
> (PyTorch idioms, mixed precision, reproducibility, debugging order),
> [ADL 08 explainable AI](../../applied-deep-learning/notes/08-explainable-ai.md)
> (integrated gradients, LIME, SHAP).

## Preprocessing

**Per-training-set normalisation**: $x' = (x - \mu_c)/s_c$ per channel with
$\mu_c, s_c$ computed on the **training set only**; the same constants are
applied to validation and test [S9]. Purpose: comparable input scales, better
conditioned optimisation. **Per-sample normalisation**: subtract each image's
own mean (and divide by its std); removes global brightness/contrast, applied
identically at test time. Pretrained nets expect exactly their training
normalisation (ImageNet mean/std).

## Data augmentation

Enlarge the training set with **label-preserving** transformations, online,
training split only. It encodes known invariances as data and is the most
effective regulariser for small image sets [S15]. Geometric: flips, crops,
shifts, small rotations, scale; photometric: brightness, contrast, colour
jitter, noise; occlusion: cutout / random erasing [S35]; mixing: **mixup**
$\tilde x = \lambda x_i + (1-\lambda)x_j$, $\tilde y = \lambda y_i + (1-\lambda)y_j$,
$\lambda\sim\mathrm{Beta}(\alpha,\alpha)$ [S35]: the ground-truth becomes a
distribution, which cross-entropy accepts (note 02).

**Is it label-preserving?** The digit question [S9]: small shifts, rotations
of a few degrees, scale, elastic distortion, contrast, noise are fine;
**horizontal flips and 180-degree rotations are not**. In a $3\times5$ digit
font, $\mathrm{hflip}(2) = 5$, $\mathrm{rot180}(6) = 9$,
$\mathrm{vflip}(3) = 3$ (`augment.py`). For dog breeds, flips and crops are
fine [S9]. **Test-time augmentation / ten-crop**: average predictions over the
four corner crops, the centre crop and their mirrors [S9].

## Regularisation

Anything that reduces the gap between training and test error without
reducing training data [S11 ch. 7].

- **Weight decay**: $\tilde L = L + \tfrac\lambda2\|\theta\|^2$, so
  $\theta \leftarrow (1 - \eta\lambda)\theta - \eta\nabla L$: shrink, then step.
  (With Adam, decoupled AdamW applies the shrink outside the adaptive scaling.)
- **Dropout** [S21]: at training, zero each unit with probability $p$ and scale
  survivors by $1/(1-p)$; at test, use all units. A dropped unit outputs 0, so
  its outgoing weights multiply 0 and it contributes nothing to the next
  layer's sums [S9]. Implicit ensemble of $2^N$ weight-sharing subnetworks;
  prevents co-adaptation. Usually in the dense head, rarely between conv layers.
- **Early stopping**: keep the parameters with the best validation loss (note 02).
- **Batch norm** regularises through batch-statistic noise [S18].
- Augmentation (above). In deep learning, prefer **a large model plus
  regularisation** over shrinking the model [S9].

## Initialisation

$z = \sum_{j=1}^{n} w_j a_j$ with independent zero-mean $w$:
$\mathrm{Var}(z) = n\,\mathrm{Var}(w)\,\mathbb E[a^2]$. For ReLU,
$\mathbb E[a^2] = \mathrm{Var}(z_{\text{prev}})/2$, so constant variance
across layers needs $\mathrm{Var}(w) = 2/n_{\text{in}}$ (He [S19]); for tanh
$1/n_{\text{in}}$ (Glorot uses $2/(n_{\text{in}}+n_{\text{out}})$). Too large:
activations and gradients grow geometrically (or saturate sigmoids); too
small: they vanish; all equal: units stay identical (symmetry). Biases 0.

## Learning rate and schedules

The catalogue's sketch [S9]: loss vs epoch for $\eta$ much too high (diverges
up), too high (fast drop, then a high noisy plateau), good (steady drop to a
low value), too low (slow, nearly linear decrease). Decay helps: large steps
early for progress, small late to settle. Step decay ($\times0.1$ at 50 % and
75 % of epochs [S8]), exponential, **cosine**
$\eta_t = \eta_{\min} + \tfrac12(\eta_{\max}-\eta_{\min})(1 + \cos\pi t/T)$
[S20], with a linear warm-up for large batches or Adam.

## Imbalanced data

Minority classes contribute little to the mean loss; accuracy rewards
predicting the majority. Remedies: class-weighted loss ($w_k\propto 1/n_k$),
oversampling the minority / undersampling the majority, focal loss; evaluate
with balanced accuracy, per-class recall, confusion matrix [S8]. The
segmentation version of the argument: note 05.

## Mixed precision

Compute in fp16/bf16, keep fp32 master weights [S35]. fp16 has 10 mantissa
bits and range $6\cdot10^{-8}$ (subnormal) to 65 504: small gradients
underflow, so multiply the loss by a scale $S$ (e.g. $2^{16}$), divide the
gradients by $S$ before the fp32 update, and lower $S$ on overflow. bf16 has
fp32's 8-bit exponent: no loss scaling, less precision. Tensor cores give
roughly 2-8x throughput; the CPU code here stays fp32.

## Visualisation

- **First-layer filters**: directly viewable as images (edges, colour blobs [S15]).
- **Saliency** [S34]: $|\partial y^c/\partial x|$, max over channels: which
  pixels change the class score most, locally. Noisy.
- **CAM** [S34]: for a GAP + linear head, $M^c = \sum_k w_{ck}A^k$.
- **Grad-CAM** [S34]: for any architecture,
  $\alpha_k^c = \tfrac1Z\sum_{ij}\partial y^c/\partial A^k_{ij}$,
  $L^c = \mathrm{ReLU}(\sum_k\alpha_k^cA^k)$, upsampled. For GAP + linear,
  $\partial y^c/\partial A^k_{ij} = w_{ck}/Z$, so Grad-CAM **equals** ReLU(CAM)
  up to scale (tested). Resolution is that of the chosen layer.
- **Sanity checks** [S34 Adebayo]: an explanation must change when the
  model's weights are randomised; methods that survive this are edge
  detectors, not explanations.

## Worked examples (`augment.py`, `gradcam.py`)

**Augmentation matters for invariance.** SmallCNN on shapes, trained without
augmentation: test accuracy 0.998, on vertically flipped test images 0.714,
on 90-degree rotated ones 0.716 (the triangle's apex direction was always
up). Trained with flips, 90-degree rotations and $\pm3$ px shifts: 0.990 and
0.988. Same data, same model, one line.

**He init numbers.** $3\times3$ conv with 64 input channels: $n_{\text{in}} =
576$, $\sigma_w = \sqrt{2/576} = 0.059$. With $\sigma_w = 0.1$ instead, each
layer multiplies the activation variance by $576\cdot0.01/2 = 2.9$: after 10
layers $4\cdot10^4$.

**Grad-CAM on shapes.** On 64 test images the map puts 67 % of its mass
inside the (2-px dilated) object mask, which covers 31 % of the image;
saliency puts 41 % there. Re-initialising the weights drops the inside mass
to 0.45 on average over three seeds, rank correlation with the trained map
0.37.

## Pitfalls

- Normalisation statistics from the whole dataset (test leakage).
- Augmenting validation/test data (except deliberate TTA).
- Dropout or BN left in training mode at evaluation (`model.eval()`).
- Weight decay on BN parameters and biases (usually excluded).
- Loss-scale overflow read as divergence in fp16.
- Reading a saliency map as the model's reasoning without a randomisation check.

## Exam-style questions

1. **Augmentations for digit classification: which work, and at least one
   that does not?** *(17, 20, 22)* Shifts, small rotations, scale, elastic,
   contrast, noise; not horizontal flips ($2\leftrightarrow5$) or
   180-degree rotations ($6\leftrightarrow9$).
2. **How does weight decay change the loss and the update; what is dropout;
   where is it applied?** *(17, 20, 21, 22)* See above; dense layers of the head.
3. **Purpose and operations of batch norm; why it regularises; single inputs
   at test time?** *(17, 20, 22)* Standardise per channel with batch
   statistics, scale and shift by $\gamma, \beta$; batch noise regularises;
   running averages at inference.
4. **Sketch loss curves for four learning rates and explain a decay
   heuristic.** *(17)* As above; reduce by 10x on plateau or at fixed epochs.
5. **Explain Grad-CAM and how you would check that a map is meaningful.**
   *(ours; XAI appears in 20)* Gradient-weighted sum of the last conv maps,
   ReLU; localisation against known object masks and the model-randomisation
   test.

## Code

- `src/py/augment.py`: `hflip`, `vflip`, `rot90`, `translate`, `random_crop`,
  `brightness_contrast`, `gaussian_noise`, `cutout`, `mixup`, `fit_normalizer`,
  `normalize`, `shapes_augment`, `render_digit`, `identify_digit`, `GLYPHS`.
- `src/py/gradcam.py`: `GradCAM`, `class_activation_map`, `saliency`,
  `mass_inside`, `randomised_copy`, `spearman`, `ascii_map`.
- `src/py/cnn_synthetic.py`: `train` (the `augment` argument), `trained_model`.
