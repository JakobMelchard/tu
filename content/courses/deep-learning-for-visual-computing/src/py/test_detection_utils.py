"""Tests for detection_utils.py: hand-made boxes, and torchvision.ops as the reference."""
import numpy as np
import pytest
import torch
from sklearn.metrics import average_precision_score
from torchvision.ops import batched_nms, box_iou
from torchvision.ops import nms as tv_nms

from detection_utils import (average_precision, coco_map, decode, encode, iou_matrix,
                             make_anchors, match_anchors, match_detections,
                             mean_average_precision, nms, nms_per_class, yolo_output_shape)


def _random_boxes(n, rng, size=100):
    xy = rng.uniform(0, size, (n, 2))
    wh = rng.uniform(5, 40, (n, 2))
    return np.concatenate([xy, xy + wh], 1)


def test_iou_hand_values():
    assert iou_matrix([0, 0, 2, 2], [1, 1, 3, 3])[0, 0] == pytest.approx(1 / 7)
    assert iou_matrix([0, 0, 2, 2], [0, 0, 2, 2])[0, 0] == 1
    assert iou_matrix([0, 0, 1, 1], [2, 2, 3, 3])[0, 0] == 0          # disjoint
    assert iou_matrix([0, 0, 4, 4], [1, 1, 3, 3])[0, 0] == pytest.approx(4 / 16)  # nested
    assert iou_matrix([0, 0, 2, 2], [2, 0, 4, 2])[0, 0] == 0          # touching edge


def test_iou_matches_torchvision():
    rng = np.random.default_rng(0)
    a, b = _random_boxes(20, rng), _random_boxes(15, rng)
    assert np.allclose(iou_matrix(a, b), box_iou(torch.tensor(a), torch.tensor(b)).numpy())


@pytest.mark.parametrize("thr", [0.3, 0.5, 0.7])
def test_nms_matches_torchvision(thr):
    rng = np.random.default_rng(1)
    b, s = _random_boxes(60, rng, size=60), rng.uniform(size=60)
    assert nms(b, s, thr).tolist() == tv_nms(torch.tensor(b), torch.tensor(s), thr).tolist()


def test_nms_per_class_matches_torchvision():
    rng = np.random.default_rng(2)
    b, s, lab = _random_boxes(50, rng, size=60), rng.uniform(size=50), rng.integers(0, 3, 50)
    ref = batched_nms(torch.tensor(b), torch.tensor(s), torch.tensor(lab), 0.5)
    assert nms_per_class(b, s, lab, 0.5).tolist() == ref.tolist()


def test_nms_hand_case():
    boxes = np.array([[10, 10, 50, 50], [12, 12, 52, 52], [100, 100, 140, 140], [11, 9, 49, 51]])
    assert nms(boxes, [0.9, 0.8, 0.7, 0.95], 0.5).tolist() == [3, 2]


def test_anchors_geometry():
    a = make_anchors(3, 4, stride=8, scales=(16, 32), ratios=(0.5, 1, 2))
    assert a.shape == (3 * 4 * 6, 4)
    w, h = a[:, 2] - a[:, 0], a[:, 3] - a[:, 1]
    assert np.allclose(w * h, np.tile(np.repeat([16 ** 2, 32 ** 2], 3), 12))   # area = scale^2
    assert np.allclose(sorted(set(np.round(h / w, 6))), [0.5, 1, 2])
    c = (a[:6, :2] + a[:6, 2:]) / 2
    assert np.allclose(c, [4, 4])                    # first cell centre (0.5 * stride)


def test_encode_decode_roundtrip_and_identity():
    rng = np.random.default_rng(3)
    a, g = _random_boxes(10, rng), _random_boxes(10, rng)
    assert np.allclose(decode(a, encode(a, g)), g)
    assert np.allclose(encode(a, a), 0)


def test_match_anchors_hand_case():
    anchors = np.array([[0, 0, 10, 10], [0, 0, 9, 10], [20, 20, 30, 30], [5, 5, 15, 15], [40, 40, 50, 50]])
    gt = np.array([[0, 0, 10, 10], [22, 22, 34, 34]])
    labels, idx = match_anchors(anchors, gt)
    # IoU with gt0: 1, .9, 0, 25/175, 0; anchor 2 vs gt1: 64/180 = .356 (< .7 but gt1's best)
    assert labels.tolist() == [1, 1, 1, 0, 0]
    assert idx[:3].tolist() == [0, 0, 1]


def test_yolo_shapes_from_the_catalogue():
    assert yolo_output_shape(3, 2, 5) == (3, 3, 20)             # 3x3xk(5+C), k = 2 [S7]
    assert yolo_output_shape(7, 2, 20, anchor_style=False) == (7, 7, 30)   # YOLOv1 on VOC [S23]


def test_average_precision_hand_case():
    assert average_precision([1, 0, 1, 0, 1], 3) == pytest.approx(34 / 45)
    assert average_precision([1, 0, 1, 0, 1], 3, "11pt") == pytest.approx(8.4 / 11)
    assert average_precision([1, 1, 1], 3) == 1.0
    assert average_precision([1, 1], 4) == pytest.approx(0.5)  # missed objects cap recall


def test_envelope_vs_sklearn():
    """sklearn's AP is the un-interpolated step sum; it agrees when precision already
    decreases at every TP and differs otherwise (the note-05 pitfall)."""
    y, s = [1, 0, 1, 0, 1], [0.9, 0.8, 0.7, 0.6, 0.5]
    assert average_precision_score(y, s) == pytest.approx(average_precision([1, 0, 1, 0, 1], 3))
    y2, s2 = [0, 1, 1], [0.9, 0.8, 0.7]
    assert average_precision([0, 1, 1], 2) == pytest.approx(2 / 3)
    assert average_precision_score(y2, s2) == pytest.approx(7 / 12)


def test_duplicates_are_false_positives():
    tp, _ = match_detections([[0, 0, 10, 10], [1, 0, 10, 10]], [0.9, 0.8], np.array([[0, 0, 10, 10]]))
    assert tp.tolist() == [1, 0]


def test_map_two_classes_two_images():
    gts = [{"boxes": [[0, 0, 10, 10], [20, 20, 30, 30]], "labels": [0, 1]},
           {"boxes": [[5, 5, 15, 15]], "labels": [0]}]
    dets = [{"boxes": [[0, 0, 10, 10], [21, 21, 31, 31], [50, 50, 60, 60]], "scores": [0.9, 0.8, 0.95],
             "labels": [0, 1, 0]},
            {"boxes": [[5, 5, 15, 16]], "scores": [0.6], "labels": [0]}]
    m, aps = mean_average_precision(dets, gts, 0.5)
    # class 0: sorted scores .95 FP, .9 TP, .6 TP -> precision 0, 1/2, 2/3 at recall 0, 1/2, 1
    assert aps[0] == pytest.approx(0.5 * 2 / 3 + 0.5 * 2 / 3)
    assert aps[1] == 1.0                                    # IoU 81/119 = .68 >= .5
    assert m == pytest.approx((2 / 3 + 1) / 2)
    perfect = [{"boxes": g["boxes"], "scores": [1.0] * len(g["labels"]), "labels": g["labels"]} for g in gts]
    assert coco_map(perfect, gts) == pytest.approx(1.0)
    assert coco_map(dets, gts) < m                          # stricter IoU thresholds cost AP
