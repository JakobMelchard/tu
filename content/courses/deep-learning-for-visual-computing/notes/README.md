# 183.663 / 193.200 Deep Learning for Visual Computing: notes

Preparation for a course offered in **summer semesters**. Written 2026-09-28 from public
sources only: TISS (2025S under 183.663, 2026S under 193.200), the CVL
homepage, three versions of the course's question catalogue and the 2016W
slides [S1-S10]. Every claim cites [`../refs/SOURCES.md`](../refs/SOURCES.md)
as `[S<n>]`; the TISS-item-to-note correspondence is in
[`../refs/lecture-notes-map.md`](../refs/lecture-notes-map.md).

**Read [00 Exam focus](00-exam-focus.md) first.** Two findings matter:
the course now runs as **193.200 with 6.0 ECTS**, and **CSE (066 646) is not
among 193.200's curricula** in 2026S [S3, S4]. Whether it runs in 2027S and
whether it counts for CSE are both open; 00 says what to check and when.

## The notes, in TISS order

`weight` = how often the topic appears in the public catalogues (2017, 2020,
SS21, 2022S) [S6-S9]: `●●●` in every edition, `●●` in several, `●` once or
only via the TISS subject line.

| # | Note | TISS item | weight | Contents | Code |
|---|---|---|---|---|---|
| 00 | [Exam focus](00-exam-focus.md) | | | course status (183.663 to 193.200), assessment, exam format by edition, the question bank by note, what to verify in 2027S | |
| 01 | [CV and image processing recap](01-cv-image-processing-recap.md) | 1 | ●● | correlation vs convolution, filtering, Sobel and Canny, colour, sampling and aliasing, the classification challenges | `backprop_scratch.py`, `augment.py` |
| 02 | [ML recap for images](02-ml-recap-for-images.md) | 2 | ●●● | splits, kNN on pixels, linear classifier, softmax and cross-entropy, GD, momentum ($\sqrt\kappa$), Adam, capacity | `backprop_scratch.py`, `cnn_synthetic.py` |
| 03 | [Feedforward nets and backprop](03-feedforward-and-backprop.md) | 3 | ●●● | MLP, activations, gate patterns, the two-layer derivation, **conv backward = transposed conv**, the Matrikelnummer graph | `backprop_scratch.py` |
| 04 | [CNNs](04-cnns.md) | 4 | ●●● | dense vs locally connected vs conv, output size, receptive field, parameters and MACs, pooling, BN, LeNet to ResNet, ViT, transfer learning | `conv_arithmetic.py`, `cnn_synthetic.py` |
| 05 | [Detection and segmentation](05-detection-and-segmentation.md) | 4 | ●●● | IoU, NMS, anchors and matching, R-CNN family, YOLO tensors, FPN, mAP by hand, FCN, U-Net skips, Dice vs IoU vs CE, transposed conv by hand | `detection_utils.py`, `segmentation_losses.py` |
| 06 | [Generative models](06-generative-models.md) | 5 | ●● | AE, VAE ELBO, GAN objective and instabilities, cGAN, pix2pix, CycleGAN, colourisation, diffusion in one page | `vae_gan_toy.py` |
| 07 | [3D and unstructured data](07-3d-and-unstructured-data.md) | 6 | ● | 2D/2.5D/3D CNNs, voxels, PointNet(++), Monte Carlo point convolution, meshes, NeRF volume rendering | |
| 08 | [Practical aspects](08-practical-aspects.md) | 7, 8 | ●●● | normalisation, augmentation (and when it is not label-preserving), regularisation, init, LR schedules, imbalance, mixed precision, saliency and Grad-CAM | `augment.py`, `gradcam.py` |
| 09 | [Trustworthy AI and ethics](09-trustworthy-ai-and-ethics.md) | 9 | ●● | data bias, protected attributes, fairness metrics and their impossibility, mitigation, model cards, the EU AI Act after the 2026 omnibus | |

## What is not duplicated

The course 194.077 Applied Deep Learning (2026W) has longer notes on
the same foundations. These notes **link** to them instead of copying:
[ADL 01](../../applied-deep-learning/notes/01-training-fundamentals.md) training,
[ADL 02](../../applied-deep-learning/notes/02-cnns.md) CNNs,
[ADL 05](../../applied-deep-learning/notes/05-autoencoders-generative.md) generative models,
[ADL 06](../../applied-deep-learning/notes/06-transformers.md) transformers,
[ADL 08](../../applied-deep-learning/notes/08-explainable-ai.md) XAI,
[ADL 10](../../applied-deep-learning/notes/10-practical.md) practice.
The preceding course 184.702 (2026W) covers evaluation, kNN, linear models,
MLPs: [ML notes](../../machine-learning/notes/README.md).

## Each note

Follows `../../../docs/coursework-conventions.md`:
definitions with formulas, derivations, a worked numeric example, pitfalls,
five exam-style questions with answers, and a `## Code` section whose
backticked names are checked by `src/py/test_note_pointers.py`. Question tags
`(17)`, `(20)`, `(21)`, `(22)` name the catalogue edition the question comes
from [S9, S8, S6, S7]; `(ours)` marks questions written here.
