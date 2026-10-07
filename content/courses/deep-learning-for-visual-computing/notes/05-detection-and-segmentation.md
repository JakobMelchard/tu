# 05 Detection and segmentation

> TISS item 4, second half ("CNNs for ... detection, and segmentation")
> [S1, S3]. Catalogue weight: region proposals, R-CNN family, YOLO tensor,
> FPN, U-Net and its skips in 2020 and 2022S; transposed conv by hand in 2020
> [S7, S8]. Papers: [S22-S26]. Background: the detection/segmentation tour and
> DETR in [ADL 02](../../applied-deep-learning/notes/02-cnns.md) and
> [ADL 06](../../applied-deep-learning/notes/06-transformers.md).

## Detection: definitions

**Task.** Given classes $\{1..C\}$, output every instance as (box, class,
score); the count is unknown. Boxes $[x_1, y_1, x_2, y_2]$.

**IoU.** $\mathrm{IoU}(A,B) = |A\cap B|/|A\cup B| \in [0,1]$. The yardstick for
matching, suppression and evaluation.

**Detection via classification** [S8]. Slide a classifier over all positions,
scales and aspect ratios: $O(\text{positions}\times\text{scales}\times\text{ratios})$
forward passes, mostly on background. **Region proposals** cut this to ~2 000
class-agnostic candidates (selective search).

**Two-stage detectors** [S22]. *R-CNN*: warp each proposal, run the CNN
2 000 times, SVM per class, box regression. *Fast R-CNN*: run the CNN **once**,
crop each proposal from the feature map with RoI pooling (fixed-size output),
classify and regress in one head. *Faster R-CNN*: a **region proposal network**
on the shared features scores anchors and regresses them; proposals are
nearly free. Stage 1 proposes, stage 2 classifies and refines per region.

**One-stage detectors** [S23, S24]. Predict class scores and boxes densely
on a grid in one pass; time independent of object count. *YOLOv1*: $S\times S$
grid, each cell predicts $B$ boxes $(x, y, w, h, \text{confidence})$ and one
class distribution: output $S\times S\times(5B + C)$. *Anchor-based YOLO/SSD/
RetinaNet*: $k$ anchors per cell, each with its own box, objectness and
classes: $S\times S\times k(5 + C)$. Loss = localisation (only for anchors
matched to an object) + objectness + classification.

**Anchors and matching.** Anchors are fixed reference boxes (scales $\times$
ratios) centred on every feature-map cell. Faster R-CNN's rule [S22]:
positive if IoU $\ge 0.7$ with some GT, negative if $< 0.3$ with all, ignored
in between; each GT's best anchor is positive regardless. Regression targets
relative to the anchor:
$$ t_x = \frac{x - x_a}{w_a},\ t_y = \frac{y - y_a}{h_a},\ t_w = \log\frac{w}{w_a},\ t_h = \log\frac{h}{h_a}. $$
**Class imbalance**: ~$10^5$ anchors, a handful positive. Focal loss
$\mathrm{FL}(p_t) = -(1-p_t)^\gamma\log p_t$ ($\gamma = 2$) down-weights easy
negatives [S24].

**NMS.** Sort by score; keep the best; drop every remaining box of the same
class with IoU above a threshold (0.5); repeat. Removes duplicates of one
object; fails for heavily overlapping true objects (crowds).

**Feature pyramid network** [S24]. Deep maps are semantically strong but
coarse, shallow maps fine but weak. FPN adds a top-down path: upsample the
deeper map $2\times$, add a $1\times1$-conv lateral from the backbone at the
same resolution, smooth with $3\times3$; attach a detection head to every
level; small objects are detected on fine levels. Backbone, neck (FPN),
heads.

**mAP.** Per class: pool detections over the dataset, sort by score; a
detection is TP if its best still-unmatched GT has IoU $\ge \tau$, else FP
(duplicates are FP). Precision $P_n$ and recall $R_n$ after $n$ detections.
AP = area under the **interpolated** curve $P_{\text{interp}}(r) = \max_{r'\ge r}P(r')$:
all-point (VOC2010+), 11-point (VOC2007), 101-point averaged over
$\tau = 0.50{:}0.05{:}0.95$ (COCO) [S25]. mAP = mean over classes.

## Segmentation: definitions

**Dense prediction.** One output per pixel: `[K, H, W]` logits.
*Semantic*: class per pixel. *Instance*: a mask per object (Mask R-CNN adds a
mask head to Faster R-CNN [S26]).

**Two stages** [S7, S8]: encoder (downsampling, context) and decoder
(upsampling back to $H\times W$). Layers specific to dense nets: transposed
convolution, bilinear upsampling, sub-pixel shuffle, unpooling with stored
argmax indices.

**FCN** [S26]: replace dense layers by convolutions, upsample the coarse
score map, add skip predictions from finer layers. **U-Net** [S26]: symmetric
encoder/decoder; before every downsampling, the encoder feature map is
**concatenated** to the decoder map of the same resolution. Why concatenate,
not sum [S7]: the encoder's high-resolution features and the decoder's
upsampled context have different meanings per channel; concatenation keeps
both and lets the next convolution learn how to combine them (a sum fixes the
combination and forces matching channel counts and semantics).

**Losses and metrics.** Pixel cross-entropy (optionally class-weighted). Soft
Dice $1 - \frac{2\sum pg + \epsilon}{\sum p + \sum g + \epsilon}$ and soft IoU
per class, averaged over classes [S26 V-Net]: each class counts equally
regardless of its pixel share. Hard metrics: pixel accuracy, per-class IoU
$TP/(TP+FP+FN)$, **mIoU**. For hard masks
$\mathrm{Dice} = 2\,\mathrm{IoU}/(1 + \mathrm{IoU}) \ge \mathrm{IoU}$.

## Worked examples

**IoU.** $[0,0,2,2]$ vs $[1,1,3,3]$: intersection 1, union $4+4-1 = 7$, IoU
$1/7 = 0.143$. NMS on four boxes, scores $(0.9, 0.8, 0.7, 0.95)$, boxes 0, 1, 3
nearly coincident, box 2 elsewhere: keeps 3 then 2.

**YOLO tensors** [S7, S8]. $3\times3$ grid, $k = 2$ anchors, 5 classes:
$3\times3\times2(5+5) = 3\times3\times20$; YOLOv1 layout $3\times3\times15$.
YOLOv1 on VOC: $7\times7\times30$.

**AP by hand.** 3 ground-truth objects; detections sorted by score are
TP, FP, TP, FP, TP. $(P, R)$: $(1, \tfrac13), (\tfrac12, \tfrac13), (\tfrac23, \tfrac23), (\tfrac12, \tfrac23), (\tfrac35, 1)$.
Envelope: 1 on $[0,\tfrac13]$, $\tfrac23$ on $(\tfrac13,\tfrac23]$, $\tfrac35$
on $(\tfrac23, 1]$. AP $= \tfrac13(1 + \tfrac23 + \tfrac35) = 34/45 = 0.756$;
11-point: $(4\cdot1 + 3\cdot\tfrac23 + 4\cdot\tfrac35)/11 = 0.764$. For
FP, TP, TP with 2 GT the envelope gives $2/3$, sklearn's step sum $7/12$.

**Dice vs IoU.** Two $4\times4$ squares overlapping in $2\times2$: IoU
$4/28 = 0.143$, Dice $8/32 = 0.25 = 2(0.143)/1.143$.

**Imbalance.** 1 % foreground ($10\times10$ in $100\times100$), a model that says
"background, $p = 0.99$" everywhere: pixel accuracy 0.99, CE 0.056, foreground
IoU 0, soft Dice loss 0.498. Dice sees the failure, CE and accuracy do not.

**Transposed convolution by hand** [S8 format]. Input
$\begin{psmallmatrix}1&2\\3&4\end{psmallmatrix}$, $3\times3$ kernel of ones,
stride 2, padding 1. Each input stamps value $\times$ kernel onto a $5\times5$
canvas at stride 2 (overlaps add); crop 1 on each side:
$\begin{psmallmatrix}1&3&2\\4&10&6\\3&7&4\end{psmallmatrix}$, size
$(2-1)2 - 2 + 3 = 3$.

## Design question: remove text and compression artifacts [S7]

Image-to-image, so a U-Net (skips carry the fine detail the output must keep).
Training pairs are synthetic: take clean images, overlay random text, JPEG
compress at random quality; input = corrupted, target = clean. Loss: $L_1$ or
$L_2$ per pixel (not cross-entropy: the output is continuous), optionally a
perceptual or adversarial term for sharpness (note 06).

## Pitfalls

- Counting a second detection of the same object as TP; it is a FP.
- Reporting mAP without the IoU threshold and interpolation (VOC 0.5 vs COCO .5:.95).
- NMS across classes when the classes may legitimately overlap.
- Dice with the mean over pixels instead of a ratio of sums: loses the
  imbalance property. With empty masks, $\epsilon$ decides the value.
- U-Net skip at mismatched resolution (odd sizes after pooling): crop or pad.

## Exam-style questions

1. **Conceptual difference between R-CNN and Fast R-CNN, and between one- and
   two-stage detectors?** *(22)* R-CNN runs the CNN per proposal on the image,
   Fast R-CNN once per image and pools proposals from the feature map.
   Two-stage: propose, then classify and refine each region (accurate, time
   grows with proposals). One-stage: dense predictions on a grid of anchors in
   one pass (fast, needs focal loss or sampling against imbalance).
2. **YOLO: approach, anchors, output for $3\times3$, $k$ anchors, 5 classes;
   post-processing?** *(20, 22)* Above; post-processing: confidence threshold,
   decode boxes from anchors, per-class NMS.
3. **What is an FPN and why?** *(22)* Top-down plus lateral connections give
   every scale strong semantics; heads on each level; helps small objects.
4. **U-Net: skips, where, how merged, why not by summation?** *(20, 21, 22)*
   From every encoder resolution to the decoder level of equal size;
   concatenation (reasons above).
5. **Why does pixel accuracy mislead for segmentation of small structures, and
   what do you use instead?** *(ours; imbalanced data is 20, 21)* Background
   dominates; per-class IoU / mIoU for evaluation, Dice or weighted CE for
   training (the 1 % example).

## Code

- `src/py/detection_utils.py`: `iou_matrix`, `box_area`, `nms`,
  `nms_per_class`, `make_anchors`, `encode`, `decode`, `match_anchors`,
  `yolo_output_shape`, `precision_recall`, `average_precision`,
  `match_detections`, `mean_average_precision`, `coco_map`.
- `src/py/segmentation_losses.py`: `pixel_cross_entropy`, `soft_dice_loss`,
  `soft_iou_loss`, `dice_score`, `iou_score`, `confusion`, `mean_iou`,
  `dice_loss_torch`, `TinyUNet`, `train_unet`.
- Tests compare against `torchvision.ops` (IoU, NMS, batched NMS),
  `torch.nn.functional.cross_entropy` and sklearn's AP.
