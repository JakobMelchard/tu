# 183.663 / 193.200 Deep Learning for Visual Computing: reference implementations

Python only, CPU only. The course's exercises are PyTorch-style programming
tasks in pairs [S3, S4, S10]; these modules make the exam material concrete
and checkable: every hand calculation in the notes is reproduced, and every
hand-written gradient or metric is tested against `torch.autograd`,
`torchvision.ops`, `torch.nn.functional` or sklearn. No dataset is downloaded:
images are rendered in code (filled shapes with clutter lines, $8\times8$ bars,
a $3\times5$ digit font), all seeded.

```sh
cd <repo root>    # repo venv from the root pyproject.toml
python -m pytest content/courses/deep-learning-for-visual-computing/src -q     # 380 tests, ~9 s warm
python content/courses/deep-learning-for-visual-computing/src/py/gradcam.py     # any module runs a demo
```

## py/

| Module | Implements | Note | Test cross-checks against |
|---|---|---|---|
| `conv_arithmetic.py` | `conv_out`, `convT_out`, `same_padding`, `conv_params`, `conv_macs`, `receptive_field` (with jump and start), `trace` / `print_trace` over a layer spec, `to_torch`, `empirical_receptive_field`, `LENET5`, `EXAM_2017_RF` | 04 | `nn.Conv2d` / `nn.ConvTranspose2d` output shapes over 282 configurations, parameter counts incl. groups, MACs by forward hooks, receptive fields by backprop from one output unit, LeNet-5 = 61 706 parameters |
| `backprop_scratch.py` | scalar graph `Node` / `backward` with `+`, `*`, `max` gates and `exam_graph`; numpy 2-layer MLP (`mlp_loss_and_grads`, `train_mlp`); `conv2d_forward` / `conv2d_backward` with stride and padding; `maxpool_forward` / `maxpool_backward`; `numerical_grad` | 03, 04 | `torch.autograd` (MLP, conv, max pool), central differences, `F.conv_transpose2d` as the conv input gradient, the 2017 pooling input |
| `cnn_synthetic.py` | `make_shapes` (circle, square, triangle, cross + clutter, masks), `SmallCNN` (14 260 parameters, GAP head), `train` (Adam, cosine, optional augmentation), `trained_model` (cached), `accuracy` | 04, 08 | seeded determinism, parameter count by hand, receptive field 18, **test accuracy > 0.9** (0.998 reached in ~4 s) |
| `detection_utils.py` | `iou_matrix`, `nms`, `nms_per_class`, `make_anchors`, `encode` / `decode`, `match_anchors` (RPN rule), `yolo_output_shape`, `average_precision` (all-point, 11-point, 101-point), `match_detections`, `mean_average_precision`, `coco_map` | 05 | `torchvision.ops.box_iou`, `nms`, `batched_nms` (exact), hand-made boxes, AP 34/45 and 8.4/11 by hand, sklearn AP where the envelope does not matter and 2/3 vs 7/12 where it does |
| `segmentation_losses.py` | `pixel_cross_entropy` (weighted), `soft_dice_loss`, `soft_iou_loss`, `dice_score`, `iou_score`, `confusion`, `mean_iou`, `dice_loss_torch`, `TinyUNet` (concat skip), `train_unet` | 05 | `F.cross_entropy` (with weights), Dice = 2 IoU/(1 + IoU), the 1 % imbalance case, transposed conv by hand, U-Net foreground IoU > 0.7 after 40 steps |
| `vae_gan_toy.py` | `make_bars`, `VAE` with `kl_gauss` and `neg_elbo`, `train_vae`, `kl_monte_carlo`; `gan_value`, `optimal_discriminator`, `js_divergence_1d`, `value_at_optimal_d`, `generator_loss_grads`, `gan_steps`; `alpha_bar`, `q_sample`, `q_iterate` | 06 | closed-form KL vs Monte Carlo and the ADL worked value 0.943, $-$ELBO falls by > 30 %, $V(D^*,G) = -\log4 + 2\,\mathrm{JS}$ by quadrature and by sampling, saturating vs non-saturating gradient, DDPM closed form vs running the chain |
| `augment.py` | `hflip`, `vflip`, `rot90`, `translate`, `random_crop`, `brightness_contrast`, `gaussian_noise`, `cutout`, `mixup`, `fit_normalizer`, `normalize`, `shapes_augment`, `render_digit` / `identify_digit` / `GLYPHS` | 08, 04 | group identities, hflip(2) = 5 and rot180(6) = 9, contrast keeps the mean, mixup labels, train-only statistics, circular conv commutes with `torch.roll`, flipped kernel commutes with a flip, a stride-2 net is invariant to 2-px but not 1-px shifts |
| `gradcam.py` | `GradCAM` (temporary hooks), `class_activation_map`, `saliency`, `mass_inside`, `randomised_copy`, `spearman`, `ascii_map` | 08 | Grad-CAM = ReLU(CAM) for a GAP + linear head (exact), CAM mass inside the object > 0.6 and > 1.8x its area, randomised weights lose localisation and correlation |

`test_note_pointers.py` (copied from the machine-learning course) holds it
together: every backticked name in a note's `## Code` section must exist in
the module it follows (118 pointers), and every module names its note in the
docstring, has a `__main__` demo, a `test_<module>.py`, and stays under 300
lines.

## Results, 2026-09-28

`pytest src -q`: **380 passed in 8.5 s** (warm; the first cold run after
installing is dominated by importing torch). Demos, all exit 0:

| module | printed result | time |
|---|---|---|
| `conv_arithmetic.py` | $16\times30\times30$ / 448 parameters; receptive field 14; ResNet stem 224 to 112 to 56; LeNet-5 table, 61 706 parameters, 416 520 MACs | 1 s |
| `backprop_scratch.py` | $f = 102$, $\nabla f = (24, 18, 6, 17)$; MLP on XOR loss 0.700 to 0.051, accuracy 1.00 | < 1 s |
| `cnn_synthetic.py` | 14 260 parameters, 192 steps, loss 1.197 to 0.080, test accuracy 0.998 | 4 s |
| `detection_utils.py` | IoU 1/7, NMS keeps [3, 2], YOLO $3\times3\times20$ / $3\times3\times15$, AP 0.7556 and 0.7636 | < 1 s |
| `segmentation_losses.py` | CE 0.056 vs Dice loss 0.498 on 1 % foreground; TinyUNet test IoU 0.998 / 0.988 | 4 s |
| `vae_gan_toy.py` | KL 0.9431; $-$ELBO 37.0 to 19.0; $V(D^*,G) = -0.7126$ both ways; gradients $-0.0025$ vs $-0.9975$; $\bar\alpha_{1000} = 4\cdot10^{-5}$ | 1 s |
| `augment.py` | flip tables; no augmentation: 0.998 / vflip 0.714 / rot90 0.716; with `shapes_augment`: 0.990 / vflip 0.988 | 8 s |
| `gradcam.py` | CAM mass inside mask 0.67 (area 0.31), saliency 0.41, randomisation Spearman 0.42, ASCII maps | 5 s |

Conventions: tensors are NCHW floats; all randomness is seeded (`seed=0`
defaults, explicit `torch.Generator`s); no network access at test time; the
suite runs on CPU. Sources are cited as `[S<n>]` from
[`../refs/SOURCES.md`](../refs/SOURCES.md).
