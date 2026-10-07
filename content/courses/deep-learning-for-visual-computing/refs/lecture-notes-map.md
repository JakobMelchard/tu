# Lecture map: TISS subject items, the only public lecture order, our notes and code

No current lecture schedule is public: slides live in TUWEL, the CVL homepage
has none [S4], and the lead lecturer's homepage lists no teaching [S31]. Two
orders exist:

- **TISS subject list** (identical in 2025S under 183.663 and 2026S under
  193.200) [S1, S3]. Our note numbering follows it.
- **The 2016W lecture sequence** of the original course, from the public
  slides [S9]. Eleven lectures, the only complete lecture order on record.

## TISS order to notes and code

| # | TISS item [S1, S3] | catalogue weight [S6-S9] | note | code |
|---|---|---|---|---|
| 1 | Brief recap of computer vision and image processing | ●● (task definitions, challenges) | [01](../notes/01-cv-image-processing-recap.md) | `backprop_scratch.py`, `augment.py` |
| 2 | Machine learning: overview, parametric models, iterative optimisation | ●●● | [02](../notes/02-ml-recap-for-images.md) | `backprop_scratch.py`, `cnn_synthetic.py` |
| 3 | Feedforward neural networks, backpropagation | ●●● | [03](../notes/03-feedforward-and-backprop.md) | `backprop_scratch.py` |
| 4a | CNNs for classification | ●●● | [04](../notes/04-cnns.md) | `conv_arithmetic.py`, `cnn_synthetic.py` |
| 4b | CNNs for detection and segmentation | ●●● (from 2020) | [05](../notes/05-detection-and-segmentation.md) | `detection_utils.py`, `segmentation_losses.py` |
| 5 | Generative models for image synthesis | ●● (GANs only) | [06](../notes/06-generative-models.md) | `vae_gan_toy.py` |
| 6 | Deep learning for 3D and unstructured data | ● (2D/2.5D/3D only); new 3D learning outcome in 2026S | [07](../notes/07-3d-and-unstructured-data.md) | none |
| 7 | Software libraries and practical aspects | ●● | [08](../notes/08-practical-aspects.md) | `cnn_synthetic.py` |
| 8 | Preprocessing, data augmentation, regularisation, visualisations | ●●● | [08](../notes/08-practical-aspects.md) | `augment.py`, `gradcam.py` |
| 9 | Algorithmic governance, trustworthy AI, ethical aspects | ●● (from 2022S) | [09](../notes/09-trustworthy-ai-and-ethics.md) | none |

## The 2016W lectures [S9] mapped onto the notes

| lecture (2016W slide title) | note |
|---|---|
| 1 Introduction | 00 |
| 2 Definitions, motivation, image classification | 01 |
| 3 Machine learning basics | 02 |
| 4 Features, parametric models, loss functions | 02 |
| 5 Gradient descent | 02 |
| 6 Gradient descent 2, optimisation vs machine learning | 02, 08 |
| 7 Multilayer perceptrons and convolutional neural nets | 03, 04 |
| 8 CNNs for classification, backpropagation | 03, 04 |
| 9 CNN training and inference, object detection | 05, 08 |
| 10 Deep learning in medical imaging (guest) | 07 (2D/2.5D/3D) |
| 11 Modelling time: RNNs and LSTMs | not in the current TISS list |

What the 2016W sequence lacked and the current TISS list adds: segmentation,
generative models, 3D data, trustworthy AI [S1]. The 2022S catalogue already
covered all but 3D [S7].

## Exercises

| edition | exercises | source |
|---|---|---|
| 2016W | three assignments; groups of one or two; Python with Keras/TensorFlow suggested | [S9] |
| 2021-2022 | three exercises in pairs; everything must be submitted | [S5] |
| 2023S | linear classifier, CNN, improved CNN on CIFAR-10 cats vs dogs | [S10] |
| 2024S-2026S | not public; 2026S ECTS: 68 h "solving exercises and hand-in meetings" | [S3] |
