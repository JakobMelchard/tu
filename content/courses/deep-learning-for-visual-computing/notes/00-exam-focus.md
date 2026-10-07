# 00 Exam focus: what is assessed, what a DLVC exam asks

Built on 2026-09-28 from TISS (2025S under 183.663, 2026S under 193.200), the
CVL homepage, and three public versions of the course's own **question
catalogue** (2017, 2020, 2022S) plus one student transcript (SS21)
[S1-S9]. The next offering would be **2027S**; nothing below is a 2027S fact
yet.

## Status first: the course number has changed

| | 183.663 | 193.200 (found 2026-09-28) |
|---|---|---|
| semesters in TISS | 2016W, 2018W, 2020S-2025S; **2026S not public** [S1, S2] | **2026S only** [S3] |
| type, hours, ECTS | VU 2.0 h, **3.0 ECTS** | VU 4.0 h, **6.0 ECTS** |
| lecturers | Hermosilla Casajus, Weijler, Kampel (E193) | the same |
| subject list | nine items (the note order) | identical, outcomes add "3D data" |
| assessment | written exam 50 % + compulsory programming exercises in pairs 50 % | identical |
| CSE 066 646 | "Not specified", on the precondition list [S1] | **not listed** [S3] |
| literature | Goodfellow et al.; Drori | "No lecture notes are available." |

The CVL homepage names 193.200 as the course's number [S4]. Reading: 183.663
was **replaced by 193.200 with doubled ECTS** in 2026S (inference from S3 and
S4; no page says "replaces"). Consequences:

1. **Whether it counts for CSE is open.** 193.200 lists four curricula and CSE
   is not one of them [S3]. Without a CSE mapping it is at best a free elective.
   Check the CSE catalogue or ask the study office *before* building a
   semester on it.
2. **Workload doubles**: 150 h, of which 68 h exercises and hand-in meetings,
   54 h preparation units and tests, 28 h lecture [S3]. "Tests" (plural) may
   mean more than one written test; unverified.
3. **2027S is not published.** The 193.200 2027S URL redirects to the login on
   2026-09-28 (as does 183.663 2026S), so it cannot be told apart from
   "not offered" without logging in [S2]. Weak evidence that it runs: the
   2026S page already lists a Tue 29.06.2027 16:00-18:00 sitting labelled
   "Exam 1" [S3].

**What to check, and when** (dates from the 2026S pattern, registration opened
16.02.2026 [S3]):

| when | check |
|---|---|
| now (2026W) | CSE eligibility of 193.200 with the study office |
| mid-January 2027 | TISS course search for 193.200 **and** 183.663 in 2027S |
| early February 2027 | 2027S lecture slot (2026S: Tue 10:00-12:00 FAV HS 1; 2025S: Tue 11:00-13:00), registration window (expect mid-Feb to mid-March), any precondition list |
| first lecture | exercise count and deadlines, whether a question catalogue is published, the exam format (see below) |

The 2026S cohort's alternative sittings (23.10.2026, 17.12.2026,
26.01.2027 [S3]) are not an option for someone who has not done the
exercises: the exercises are compulsory and 50 % of the grade.

## Assessment

- **50 % written exam, 50 % compulsory programming exercises in groups of
  two** [S1, S3, S4]. VoWi (2021-2022): three exercises, and every part must be
  implemented and submitted; partial submission is not an option [S5].
- 2023S exercises: linear classifier, then CNN, then an improved CNN, on a
  cats-vs-dogs subset of CIFAR-10 [S10]. The 2024S+ exercises (Hermosilla era)
  are not public.
- Compute: own CUDA GPU, a lab GPU server, or cloud free tiers [S4]. The code
  in [`../src`](../src/README.md) is CPU-only by design.
- Recordings: CVL says "no recordings" [S4]; TISS 2026S says "video lectures"
  and LectureTube [S3]. Contradictory; check in 2027S.

## The exam format, as far as it is documented

| edition | format | source |
|---|---|---|
| 2016W | catalogue published; each exam a subset; 60 min; no documents; own words, sketches expected | [S9] |
| SS21 | online, written + oral; catalogue on TUWEL before the exam | [S5, S6] |
| SS22 | written, in presence, no aids; catalogue on TUWEL; Jan 2023: five main questions, 1 h | [S5] |
| 2025S | two "exam rehearsal" slots in June (09.06., 10.06.2025) | [S1] |
| 2026S (193.200) | four written sittings in 2 h rooms (14-16, 15-17, 16-18) | [S3] |

Nothing public exists for 2024S-2026S: the VoWi page of the Hermosilla era has
no material [S5]. Assume long-answer questions until the 2027S course says
otherwise: definitions in your own words, a sketch, one small calculation.

## The question bank (paraphrased), by note

Tags: `17` = 2017 catalogue [S9], `20` = 2020 [S8], `21` = SS21 transcript
[S6], `22` = 2022S catalogue [S7]. Questions recur almost verbatim across
catalogues; the 2022S list is the closest to the current course.

| note | question (short form) | seen |
|---|---|---|
| 01 | Image classification task, five challenges with examples (pose, illumination, deformation, occlusion, background clutter, intra-class variation); detection vs classification and which is harder | 17, 20, 22 |
| 01, 02 | Why do generic vector-input ML algorithms fail on raw images; features, low vs high level; traditional pipeline | 17, 20, 22 |
| 02 | Why datasets; the three splits; dataset bias | 17, 20 |
| 02 | kNN: sketch decision boundaries, limitations; hyperparameters and search strategies | 17, 20 |
| 02 | Parametric model; linear model with its parameters, sketch 3 classes in 2-D | 17, 20, 22 |
| 02 | Class scores, softmax; purpose of a loss; what cross-entropy measures and what labels/scores must satisfy | 17, 20, 21, 22 |
| 02 | Gradient descent, gradient, learning rate vs step size; sketch GD with and without momentum on a contour plot | 17, 20, 22 |
| 02 | Local vs global optimum, are local minima a problem, momentum | 17, 20, 21, 22 |
| 02 | Batch vs minibatch vs stochastic GD, epoch, pseudo-code of training with early stopping | 17, 20, 22 |
| 02 | Adam vs GD with momentum (no formulas required) | 20, 22 |
| 02 | Under/overfitting, capacity, training vs test error sketches | 17, 20, 22 |
| 03 | Feedforward net, MLP sketch (3 inputs, one hidden layer of 4 or 5, binary output), what a unit computes, activation functions and why ReLU | 17, 20, 22 |
| 03 | Backprop: purpose, vs the naive algorithm, steps at a node, gradient flow through `+`, `*`, `max` | 20, 22 |
| 03 | **Backprop by hand on a small graph** with your Matrikelnummer digits as inputs | 17, 21 |
| 03, 04 | Why MLPs fail for images; representation learning, definition of deep learning | 17, 20, 22 |
| 04 | Sparse vs dense connectivity, locally connected vs convolutional, parameter counts for $W\times H\times D$ input with $3\times3$ kernels | 17, 20, 22 |
| 04 | **Output shape**: $3\times32\times32$ input, $3\times3$ kernel, 16 maps | 22 |
| 04 | **Receptive field** after conv3, conv3, pool2/2, conv3, conv3 | 17, 20 |
| 04 | **Max pooling by hand** on a $4\times4$ input; how many stride-2 pools for $64\times64$ | 17 |
| 04 | Pooling types, their opposites (upsampling, transposed and sub-pixel convolution), global average pooling | 17, 20, 22 |
| 04 | CNN overview sketch, the two stages, what joins them | 17, 21, 22 |
| 04 | Depth, vanishing/exploding gradients, residual blocks, pointwise convolution, bottlenecks | 17, 20, 22 |
| 04 | Transfer learning, pre-training, fine-tuning; the bird-species app step by step | 17, 20, 21, 22 |
| 04 | Transformers for images: inputs, patch tokens, the inductive-bias argument | 22 |
| 05 | Detection via classification and its cost; region proposals; R-CNN vs Fast R-CNN; one- vs two-stage | 20, 22 |
| 05 | **YOLO output tensor** for an $S\times S$ grid, $k$ anchors, $C$ classes; anchors; post-processing (NMS) | 20, 22 |
| 05 | Feature pyramid networks | 22 |
| 05 | Dense prediction, semantic segmentation, the two stages; U-Net, where the skips are, why concatenation not sum | 20, 21, 22 |
| 05 | Design a net that removes text and compression artifacts; where the training data comes from; the loss | 22 |
| 05 | **Transposed convolution by hand** (stride 2, pad 1) | 20 |
| 06 | GAN: components, interaction, latent vectors, training loop pseudo-code, ideal outcome | 20, 22 |
| 06 | Conditional GAN; colourisation GAN; paired vs unpaired translation, cycle consistency | 22 |
| 07 | 2-D vs 2.5-D vs 3-D CNNs (medical block) | 17, 20 |
| 08 | Preprocessing: per-sample vs per-training-set normalisation, what happens at test time | 17, 20 |
| 08 | Augmentation: purpose, which transforms suit **digits** and which do not; mixup and its labels | 17, 20, 22 |
| 08 | Regularisation, weight decay in the loss and in the update, dropout (why dropped units have no effect, where it goes) | 17, 20, 21, 22 |
| 08 | Batch norm: purpose, operations, why it regularises, where, single inputs at test time | 17, 20, 22 |
| 08 | Learning-rate sketch (much too high, too high, good, too low), decay schedules | 17, 20 |
| 08 | Initialisation: too large, too small, the heuristic | 17 |
| 08 | Imbalanced data: effect, remedies, why accuracy misleads | 20, 21 |
| 08 | Ensembles, ten-crop oversampling | 17 |
| 09 | Data bias types; protected attributes (four); explainability; assessing fairness; why in-processing is hard for a running system | 20, 22 |

The **hand calculations** that recur (bold above) are the ones to drill: each
has a worked example in the named note and a function in `src/py`.

## Weighting for preparation

The exam is half the grade and drawn from a list: coverage beats depth.
Time split suggested by the frequency above (ours): notes 02-04 about half,
05-06 a quarter, 01, 07, 08, 09 the rest. Note 07 (3D) is thin in the
catalogues but is the current lecturer's research field [S31] and the 2026S
learning outcome names 3D data [S3]: expect it to grow.

## Pitfalls

- Trusting the student answers in S7/S8. Example: S7 p. 14 gives $16\times10\times10$ for
  the output-shape question; $\lfloor(32-3)/1\rfloor+1 = 30$, so $16\times30\times30$.
- Writing keywords. The 2017 rules ask for full answers "in your own words"
  with sketches [S9].
- Assuming the 2022S catalogue is still used. Lecturer lead changed afterwards [S5].

## Code

`src/py/conv_arithmetic.py`: `conv_out`, `receptive_field`, `conv_params`, `EXAM_2017_RF`;
`src/py/backprop_scratch.py`: `exam_graph`, `maxpool_forward`;
`src/py/detection_utils.py`: `yolo_output_shape`;
`src/py/augment.py`: `render_digit`, `identify_digit`.
