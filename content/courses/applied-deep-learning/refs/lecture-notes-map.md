# Lecture → notes → code map

The 2025W lecture series [S4] chapter by chapter, against our notes and our
reference implementations. Chapter titles and timings are the ones in each
video's own description; the `L*n* #*k*` markers refer to the numbered
`== Literature ==` block of that video, which is where most of the primary
sources in [`SOURCES.md`](SOURCES.md) were found.

This is the file to check before deciding a topic is "not in the course". The
notes were originally written from the eight-item TISS subject list [S1], which
turns out to be a *subset* of what is lectured: TISS lists the eight advanced
topics the project may use and says nothing about the five lectures of general
method (2, 5, 9, 12 and the introduction).

**2026W caveat.** The 2026W recordings do not exist yet (the course starts
07.10.2026). The order below is 2025W's and has been stable since 2023 [S6, S7],
with two changes in three years: LLMs added in 2024, and XAI/GNN/Serving
reordered in 2025.

---

## The map

| L | lecture [S4] | our note | our code | state |
|---|---|---|---|---|
| 0 | Preliminary Information | [`00-exam-focus.md`](../notes/00-exam-focus.md), [`11-project.md`](../notes/11-project.md) | `project_template/` | rewritten from [S5], [S12–S14] |
| 1 | Introduction to Deep Learning | — (no note) | — | **deliberately not written**: it is motivation and applications, nothing examinable, and nothing is examined anyway |
| 2 | Neural Networks, Optimization, and Backpropagation | [`01-training-fundamentals.md`](../notes/01-training-fundamentals.md) | `common.py` | good |
| 3 | CNNs and Visual Computing | [`02-cnns.md`](../notes/02-cnns.md) | `cnn_shapes.py`, `shape_formulas.py` | good; deformable convs and the detection/segmentation tour added |
| 4 | Recurrent Neural Networks | [`03-rnns.md`](../notes/03-rnns.md) | `rnn_sequence.py`, `ctc_loss.py` | **CTC was missing**; now a section and an implementation |
| 5 | Libraries and Practical Aspects | [`10-practical.md`](../notes/10-practical.md) | `common.py` | good; capacity/Bayes-error/coverage added |
| 6 | Deep Reinforcement Learning | [`04-deep-rl.md`](../notes/04-deep-rl.md) | `rl_reinforce.py` | good |
| 7 | Autoencoders and GANs | [`05-autoencoders-generative.md`](../notes/05-autoencoders-generative.md) | `autoencoder_vae.py`, `gan_toy.py` | good |
| 8 | Transformers | [`06-transformers.md`](../notes/06-transformers.md) | `transformer_char.py`, `set_prediction.py` | **DETR was missing**; it is 40 % of the lecture |
| 9 | Preprocessing, Augmentation, Regularization, Visualization | [`01-training-fundamentals.md`](../notes/01-training-fundamentals.md) | `cnn_shapes.py` | adversarial training, SpecAugment/EDA, cutout and SWA added |
| 10 | Explainable AI | [`08-explainable-ai.md`](../notes/08-explainable-ai.md) | `xai_saliency.py` | good |
| 11 | Graph Neural Networks | [`07-gnns.md`](../notes/07-gnns.md) | `gnn_gcn.py` | good |
| 12 | Serving, Optimizing, and Practical Aspects | [`12-serving-and-deployment.md`](../notes/12-serving-and-deployment.md) | `deploy_optimize.py`, `pruning.py` | **the whole lecture was missing**; new note, new module |
| 13 | Large Language Models | [`09-llms.md`](../notes/09-llms.md) | `llm_finetune_sketch.py` | good; CLIP, MCP, tree-of-thought, model collapse added |
| 14 | Outlook, Feedback, Goodbye | — | — | 5 minutes, a feedback form |

---

## Chapter-level detail where it changed something

### L3 — CNNs (1:22:48, the longest lecture)

Chapters: MLP → arriving at a good representation → the convolutional layer →
different kinds of convolutions → the receptive field → pooling → activation
functions → **network architectures (18 min)** → the last layers and **global
average pooling** → **depthwise separable convolutions** → considerations and
tips → **applications (15 min)** → summary.

Two things the note under-weighted. *Different kinds of convolutions* is where
**deformable convolutions** [S41] appear — and S12 names deformable convolutional
layers as *the* example of a novel idea to try for a "Beat the stars" project, so
it is worth more than a mention. And a quarter of the lecture is the
**applications** tour: Faster R-CNN [S45], segmentation [S45], Mask R-CNN,
AutoKeras/NAS. The note now says which architecture family to reach for per task
rather than only how convolution arithmetic works.

### L4 — RNNs (50:09)

Chapters include *Connectionist Temporal Classification (CTC) Loss* at 44:14,
and CTC is also what the lecturer's own research (optical music recognition,
[S9]) uses. The note had nothing on it. It now has a derivation of the forward
algorithm, and `src/py/ctc_loss.py` implements it and checks it against
`torch.nn.CTCLoss`.

### L5 — Libraries and Practical Aspects (1:10:30)

This lecture is Goodfellow chapter 11 [S15] with a library tour bolted on:
coverage → **capacity** → under/overfitting → **effective capacity** →
efficiently scaling up a model (EfficientNet, [S44]) → hyperparameters →
train/val/test → the learning rate → selecting hyperparameters → **automatic
hyperparameter optimization** [S94] → **the Bayes error** → design principles →
performance metrics → **obtaining a baseline** → dataset size → debugging →
**deep learning libraries (14 min)**.

"Obtaining a baseline" and "do I need more data?" are the lecture's own
justification for what [S13] then demands in writing, so
[`11-project.md`](../notes/11-project.md) and
[`10-practical.md`](../notes/10-practical.md) now point at each other here.

### L8 — Transformers (1:03:39)

Chapters: why transformers → what is a transformer → input embedding and
positional encoding → attention → implementing attention → masked attention →
cross-attention → the final layers → architecture variations → **transformers
for object detection (5 min)** → **the Detection Transformer, DETR (2 min)** →
**bipartite matching loss (9 min)** → **object queries (8 min)** → advances in
transformers → summary.

From 30:11 to 55:14 — **25 of 62 minutes, 40 % of the lecture** — is object
detection with transformers. The note covered attention thoroughly and DETR not
at all. It now has a section on set prediction and the Hungarian matching loss,
and `src/py/set_prediction.py` implements the matching.

### L9 — Preprocessing, Augmentation, Regularization, Visualization (1:12:03)

Chapters: preprocessing → input normalization → preprocessing to unlock problems
→ data augmentation → **adversarial training** → **adversarial attacks** →
**data augmentation for audio** → **data augmentation for text** →
regularization → weight decay → early stopping → **cutout** → dropout → batch
normalization → layer normalization → normalizing activation functions →
**stochastic weight averaging** → visualization → **TensorBoard** → **Netron** →
**class activation maps** → visualizing the gradient.

Our note 01 had the classical half (weight decay, early stopping, dropout, BN,
LN) and none of the bold items. All are now in, with their lecture-list sources
[S32–S37].

### L12 — Serving, Optimizing, and Practical Aspects (1:13:52)

Chapters: ML in practice → a simple way to serve a model → a better way →
serving with TensorFlow → serving in the cloud → Paperspace / **Streamlit** /
**Gradio** / **Hugging Face Spaces** → serving in a container → TF Serving
Docker → **ONNX** → **publishing your dataset — FAIR** → **deep learning in the
browser (11 min)** → deep learning on mobile → benefits of on-device → boosting
performance → optimizing data loading → **floating-point quantization** → the
effect of minibatch sizes → **warmup** → reducing the cost of running models →
**pruning** → **the lottery ticket hypothesis**.

This lecture had no note at all, which is the single largest gap this pass
found — and it is not an optional one, because **assignment 3 [S14] is graded on
a demo application** whose recommended forms (Docker, Streamlit, Gradio, ONNX
Runtime, TensorFlow.js) are exactly this lecture's content. New note
[`12-serving-and-deployment.md`](../notes/12-serving-and-deployment.md), new
modules `src/py/deploy_optimize.py` and `src/py/pruning.py`.

### L13 — LLMs (59:18)

Chapters added for the 2025 edition relative to 2024: **Tree-of-thought
prompting**, **Model Context Protocol** [S81], **AI slop** and model collapse
[S82], **KROP** [S83]. *Multiple modalities and CLIP* [S78] and *contrastive
learning* were already there and were missing from our note.

---

## What is *not* in the course

Recorded so that the notes do not drift into a general deep-learning textbook:

- **No mathematical statistics, no learning theory, no VC dimension.** Lecture 5
  covers capacity informally and the Bayes error as a practical floor.
- **No diffusion beyond one chapter.** L7 gives diffusion 3½ minutes of its 75.
  Our note 05 is much longer on diffusion than the course is; it is kept because
  it is a plausible project topic, and marked as such.
- **No formal treatment of transformers' training dynamics, scaling laws or
  distributed training.** L12 touches minibatch size and warmup only.
- **No written exam, so no proof questions.** See
  [`../notes/00-exam-focus.md`](../notes/00-exam-focus.md).
