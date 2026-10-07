"""Object-detection building blocks: IoU, NMS, anchors, box encoding, anchor matching, AP/mAP.

Note 05 (detection and segmentation). Boxes are [x1, y1, x2, y2] (xyxy), continuous
coordinates. Conventions: box encoding and the RPN matching rule of Faster R-CNN [S22];
AP as the area under the interpolated precision envelope (PASCAL VOC, all-point and
11-point [S25]) and the COCO mAP@[.5:.95] with 101 recall points [S25].
Cross-checked against torchvision.ops in test_detection_utils.py.
"""
import numpy as np


def box_area(b):
    b = np.asarray(b, float)
    return np.clip(b[..., 2] - b[..., 0], 0, None) * np.clip(b[..., 3] - b[..., 1], 0, None)


def iou_matrix(a, b):
    """Pairwise IoU = |A ∩ B| / |A ∪ B| for a [N,4] and b [M,4] -> [N,M]."""
    a, b = np.asarray(a, float).reshape(-1, 4), np.asarray(b, float).reshape(-1, 4)
    lt = np.maximum(a[:, None, :2], b[None, :, :2])
    rb = np.minimum(a[:, None, 2:], b[None, :, 2:])
    inter = np.prod(np.clip(rb - lt, 0, None), axis=2)
    union = box_area(a)[:, None] + box_area(b)[None, :] - inter
    return np.where(union > 0, inter / np.where(union > 0, union, 1), 0.0)


def nms(boxes, scores, iou_thr=0.5):
    """Greedy non-maximum suppression: keep the best box, drop all with IoU > thr, repeat."""
    order = np.argsort(-np.asarray(scores), kind="stable")
    boxes, keep = np.asarray(boxes, float), []
    while order.size:
        i = order[0]
        keep.append(int(i))
        rest = order[1:]
        order = rest[iou_matrix(boxes[i], boxes[rest])[0] <= iou_thr]
    return np.array(keep, int)


def nms_per_class(boxes, scores, labels, iou_thr=0.5):
    """Class-aware NMS: boxes of different classes never suppress each other."""
    keep = [np.flatnonzero(labels == c)[nms(boxes[labels == c], scores[labels == c], iou_thr)]
            for c in np.unique(labels)]
    keep = np.concatenate(keep) if keep else np.array([], int)
    return keep[np.argsort(-np.asarray(scores)[keep], kind="stable")]


def make_anchors(feat_h, feat_w, stride, scales=(32,), ratios=(0.5, 1.0, 2.0)):
    """Anchors centred on every feature-map cell: [(feat_h * feat_w * A), 4], A = |scales||ratios|.

    Ratio r = h / w at constant area s^2: w = s / sqrt(r), h = s sqrt(r). Cell (i, j) has
    centre ((j + 0.5) stride, (i + 0.5) stride) in input pixels."""
    wh = np.array([(s / np.sqrt(r), s * np.sqrt(r)) for s in scales for r in ratios])
    cy, cx = np.meshgrid((np.arange(feat_h) + 0.5) * stride, (np.arange(feat_w) + 0.5) * stride,
                         indexing="ij")
    c = np.stack([cx.ravel(), cy.ravel()], 1)[:, None, :]              # [HW,1,2]
    return np.concatenate([c - wh / 2, c + wh / 2], axis=2).reshape(-1, 4)


def _cxcywh(b):
    b = np.asarray(b, float)
    w, h = b[..., 2] - b[..., 0], b[..., 3] - b[..., 1]
    return b[..., 0] + w / 2, b[..., 1] + h / 2, w, h


def encode(anchors, gt):
    """Regression targets t = ((x - xa)/wa, (y - ya)/ha, log(w/wa), log(h/ha)) [S22]."""
    xa, ya, wa, ha = _cxcywh(anchors)
    x, y, w, h = _cxcywh(gt)
    return np.stack([(x - xa) / wa, (y - ya) / ha, np.log(w / wa), np.log(h / ha)], -1)


def decode(anchors, t):
    xa, ya, wa, ha = _cxcywh(anchors)
    x, y = xa + t[..., 0] * wa, ya + t[..., 1] * ha
    w, h = wa * np.exp(t[..., 2]), ha * np.exp(t[..., 3])
    return np.stack([x - w / 2, y - h / 2, x + w / 2, y + h / 2], -1)


def match_anchors(anchors, gt, pos_thr=0.7, neg_thr=0.3):
    """RPN assignment [S22]: label 1 if max IoU >= pos_thr, 0 if < neg_thr, -1 (ignored)
    in between; additionally every GT's best anchor is positive, so no object is left
    without a positive anchor. Returns (labels [N], matched gt index [N])."""
    iou = iou_matrix(anchors, gt)                                       # [N, M]
    best_gt, best_iou = iou.argmax(1), iou.max(1)
    labels = np.full(len(anchors), -1, int)
    labels[best_iou < neg_thr] = 0
    labels[best_iou >= pos_thr] = 1
    for m in range(iou.shape[1]):                                       # force a positive per GT
        top = np.flatnonzero(iou[:, m] == iou[:, m].max())
        labels[top], best_gt[top] = 1, m
    return labels, best_gt


def yolo_output_shape(S, B, C, anchor_style=True):
    """YOLOv1 [S23]: S x S x (5B + C), one class vector per cell. Anchor-based heads
    (YOLOv2/v3, [S23]): S x S x B(5 + C), a class vector per anchor. 5 = x, y, w, h, objectness."""
    return (S, S, B * (5 + C)) if anchor_style else (S, S, 5 * B + C)


def precision_recall(tp, n_gt):
    """Cumulative precision and recall for detections already sorted by descending score."""
    tp = np.asarray(tp, float)
    ctp, cfp = np.cumsum(tp), np.cumsum(1 - tp)
    return ctp / np.maximum(ctp + cfp, 1e-12), ctp / max(n_gt, 1)


def average_precision(tp, n_gt, method="all"):
    """AP from TP flags (sorted by score). 'all': area under the precision envelope
    p_interp(r) = max_{r' >= r} p(r') (VOC2010+); '11pt': mean of p_interp at r = 0, .1, .., 1
    (VOC2007); '101pt': the COCO variant at r = 0, .01, .., 1 [S25]."""
    if n_gt == 0:
        return float("nan")
    prec, rec = precision_recall(tp, n_gt)
    if method == "all":
        r = np.concatenate([[0], rec, [1]])
        p = np.concatenate([[0], prec, [0]])
        p = np.maximum.accumulate(p[::-1])[::-1]                        # the envelope
        i = np.flatnonzero(r[1:] != r[:-1])
        return float(np.sum((r[i + 1] - r[i]) * p[i + 1]))
    grid = np.linspace(0, 1, 11 if method == "11pt" else 101)
    return float(np.mean([prec[rec >= t].max() if np.any(rec >= t) else 0.0 for t in grid]))


def match_detections(det_boxes, det_scores, gt_boxes, iou_thr=0.5):
    """Greedy by score: a detection is TP if its best still-unmatched GT has IoU >= thr.
    A second detection of an already matched object is a FP (duplicate)."""
    order = np.argsort(-np.asarray(det_scores), kind="stable")
    used, tp = np.zeros(len(gt_boxes), bool), np.zeros(len(order))
    if len(gt_boxes):
        iou = iou_matrix(np.asarray(det_boxes)[order], gt_boxes)
        for k in range(len(order)):
            cand = np.where(used, -1.0, iou[k])
            j = int(cand.argmax())
            if cand[j] >= iou_thr:
                used[j], tp[k] = True, 1
    return tp, np.asarray(det_scores)[order]


def mean_average_precision(dets, gts, iou_thr=0.5, method="all"):
    """dets / gts: per image dicts {'boxes', 'scores', 'labels'} / {'boxes', 'labels'}.
    Per class, pool detections over images, sort by score, AP; mAP = mean over classes."""
    classes = sorted({int(c) for g in gts for c in g["labels"]})
    aps = {}
    for c in classes:
        flags, scores, n_gt = [], [], 0
        for d, g in zip(dets, gts):
            gb = np.asarray(g["boxes"]).reshape(-1, 4)[np.asarray(g["labels"]) == c]
            dm = np.asarray(d["labels"]) == c
            n_gt += len(gb)
            t, s = match_detections(np.asarray(d["boxes"]).reshape(-1, 4)[dm],
                                    np.asarray(d["scores"])[dm], gb, iou_thr)
            flags.append(t)
            scores.append(s)
        flags, scores = np.concatenate(flags), np.concatenate(scores)
        aps[c] = average_precision(flags[np.argsort(-scores, kind="stable")], n_gt, method)
    return float(np.mean(list(aps.values()))), aps


def coco_map(dets, gts):
    """COCO primary metric: mAP averaged over IoU thresholds .50:.05:.95, 101-point AP [S25]."""
    return float(np.mean([mean_average_precision(dets, gts, t, "101pt")[0]
                          for t in np.linspace(0.5, 0.95, 10)]))


if __name__ == "__main__":
    print("IoU([0,0,2,2],[1,1,3,3]) =", iou_matrix([0, 0, 2, 2], [1, 1, 3, 3])[0, 0], "(= 1/7)")
    boxes = np.array([[10, 10, 50, 50], [12, 12, 52, 52], [100, 100, 140, 140], [11, 9, 49, 51]])
    print("NMS keeps", nms(boxes, [0.9, 0.8, 0.7, 0.95], 0.5).tolist(), "of 4 boxes")
    print("2022S catalogue [S7]: 3x3 grid, k=2 anchors, 5 classes ->", yolo_output_shape(3, 2, 5),
          "; YOLOv1 layout", yolo_output_shape(3, 2, 5, anchor_style=False))
    a = make_anchors(2, 2, 16, scales=(16, 32))
    print("anchors on a 2x2 map, stride 16, 2 scales x 3 ratios:", a.shape)
    tp = [1, 0, 1, 0, 1]
    print("TP pattern", tp, "3 GT: AP all-point", round(average_precision(tp, 3), 4),
          "(34/45), 11-point", round(average_precision(tp, 3, "11pt"), 4), "(8.4/11)")
