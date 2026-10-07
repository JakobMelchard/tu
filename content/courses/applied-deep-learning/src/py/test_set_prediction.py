"""Bipartite matching checked against exhaustive search, GIoU against its axioms.

The reference results here are the defining properties of GIoU from the paper
DETR cites, and exact optimality of the assignment, which is verified by
enumerating every injection for small problems.
"""

import torch

from common import loss_decreased
from set_prediction import (assignment_cost, box_iou, brute_force_match,
                            generalized_iou, greedy_match, hungarian_match,
                            matching_cost, run, set_criterion)


def _b(*v):
    return torch.tensor([list(v)], dtype=torch.float32)


def test_iou_and_giou_axioms():
    unit = _b(0, 0, 1, 1)
    assert box_iou(unit, unit)[0].item() == 1.0
    assert generalized_iou(unit, unit).item() == 1.0
    # half-overlapping unit squares: intersection 0.5, union 1.5
    half = _b(0.5, 0, 1.5, 1)
    assert abs(box_iou(unit, half)[0].item() - 1 / 3) < 1e-6
    # enclosing box is 1.5x1, union is 1.5, so GIoU == IoU here
    assert abs(generalized_iou(unit, half).item() - 1 / 3) < 1e-6
    # disjoint boxes: IoU is 0 regardless of distance, GIoU is not
    near, far = _b(1.0, 0, 2.0, 1), _b(9.0, 0, 10.0, 1)
    assert box_iou(unit, near)[0].item() == 0.0 == box_iou(unit, far)[0].item()
    assert generalized_iou(unit, near).item() > generalized_iou(unit, far).item()
    # GIoU is bounded in [-1, 1] and tends to -1 as the boxes separate
    assert -1.0 <= generalized_iou(unit, far).item() <= 1.0
    very_far = _b(999.0, 0, 1000.0, 1)
    assert generalized_iou(unit, very_far).item() < -0.99


def test_giou_gives_gradient_where_iou_does_not():
    a = torch.tensor([[0.0, 0.0, 1.0, 1.0]], requires_grad=True)
    b = torch.tensor([[5.0, 0.0, 6.0, 1.0]])
    box_iou(a, b)[0].sum().backward()
    assert a.grad.abs().sum().item() == 0.0            # IoU: flat, no signal
    a2 = torch.tensor([[0.0, 0.0, 1.0, 1.0]], requires_grad=True)
    generalized_iou(a2, b).sum().backward()
    assert a2.grad.abs().sum().item() > 0              # GIoU: pushes the box towards the target


def test_hungarian_is_optimal_and_greedy_is_not():
    torch.manual_seed(0)
    strictly_worse = 0
    for _ in range(100):
        c = torch.rand(5, 3)
        h = assignment_cost(c, *hungarian_match(c))
        assert abs(h - assignment_cost(c, *brute_force_match(c))) < 1e-6
        if assignment_cost(c, *greedy_match(c)) > h + 1e-9:
            strictly_worse += 1
    assert strictly_worse > 10, "greedy should lose often enough to matter"


def test_matching_is_one_to_one():
    torch.manual_seed(0)
    logits, boxes = torch.randn(8, 4), torch.rand(8, 4).sort(-1).values
    tl, tb = torch.tensor([0, 1, 2]), torch.rand(3, 4).sort(-1).values
    pi, ti = hungarian_match(matching_cost(logits, boxes, tl, tb))
    assert len(pi) == len(ti) == 3
    assert len(set(pi.tolist())) == 3 and sorted(ti.tolist()) == [0, 1, 2]


def test_matching_is_permutation_invariant_in_the_slots():
    """Shuffling the prediction slots must not change the loss: that is the point."""
    torch.manual_seed(1)
    logits, boxes = torch.randn(6, 4), torch.rand(6, 4).sort(-1).values
    tl, tb = torch.tensor([0, 2]), torch.rand(2, 4).sort(-1).values
    base, _ = set_criterion(logits, boxes, tl, tb)
    perm = torch.randperm(6)
    shuffled, _ = set_criterion(logits[perm], boxes[perm], tl, tb)
    assert torch.allclose(base, shuffled, atol=1e-5)


def test_perfect_prediction_has_no_box_loss():
    tl = torch.tensor([0, 1])
    tb = torch.tensor([[0.1, 0.1, 0.4, 0.4], [0.5, 0.5, 0.9, 0.9]])
    # slots 3 and 0 hold the right boxes; the rest are elsewhere
    boxes = torch.tensor([[0.5, 0.5, 0.9, 0.9], [0.0, 0.0, 0.05, 0.05],
                          [0.0, 0.0, 0.05, 0.05], [0.1, 0.1, 0.4, 0.4]])
    logits = torch.full((4, 3), -10.0)
    logits[3, 0] = logits[0, 1] = 10.0
    logits[1, 2] = logits[2, 2] = 10.0                  # the two spare slots say "no object"
    loss, info = set_criterion(logits, boxes, tl, tb)
    assert info["l1"] < 1e-6 and info["giou"] < 1e-6
    assert sorted(zip(info["pred_idx"].tolist(), info["tgt_idx"].tolist())) == [(0, 1), (3, 0)]
    assert loss.item() < 0.01


def test_training_decreases_loss():
    out = run(steps=400)
    assert loss_decreased(out["losses"])
    assert out["mean_iou"] > 0.2
