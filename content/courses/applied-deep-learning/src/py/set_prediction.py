"""Set prediction with bipartite matching: the loss that makes DETR work.

Lecture 8 [S4] spends 25 of its 62 minutes on object detection with transformers
-- DETR, the bipartite matching loss and object queries -- which is more time
than it gives to positional encoding and cross-attention together.  This module
is that part.

The problem.  A detector must output a *set* of objects.  A set has no order, but
a network outputs a list, so a naive per-slot loss punishes a model that predicts
the right objects in the wrong slots.  Classical detectors dodge this with
anchors, a hand-tuned assignment rule and non-maximum suppression.  DETR [S63]
removes all three: it emits a fixed number ``N`` of predictions (one per *object
query*, with ``N`` larger than any plausible object count), and at training time
finds the **cheapest one-to-one matching** between predictions and ground truth,

    sigma_hat = argmin over injections sigma of sum_i C( pred_{sigma(i)}, gt_i ),

then applies the loss only along that matching.  Unmatched predictions are
trained towards a "no object" class.  Because the matching is one-to-one, two
predictions can never both claim one object, so duplicate suppression is built
into the loss rather than bolted on afterwards.

The matching is an assignment problem and is solved exactly in ``O(n^3)`` by the
Hungarian algorithm -- ``scipy.optimize.linear_sum_assignment``.  Greedy matching
is *not* equivalent and is checked against the optimum below.

Conventions: boxes are ``[x0, y0, x1, y1]`` in absolute corner form with
``x0 <= x1`` (DETR itself uses normalised centre-width form and converts; corner
form is what the IoU arithmetic wants).  The matching cost is the paper's:

    C = -p_hat(class_i) + lambda_L1 * ||b_hat - b_i||_1 + lambda_giou * (1 - GIoU)

with the class term a *probability*, not a log-probability -- deliberately, so
that it is commensurate with the box terms.

Run: ``python set_prediction.py``.
"""

from __future__ import annotations

import itertools

import torch
import torch.nn as nn
import torch.nn.functional as F
from scipy.optimize import linear_sum_assignment


# --- box geometry -----------------------------------------------------------


def box_area(b: torch.Tensor) -> torch.Tensor:
    return (b[..., 2] - b[..., 0]).clamp(min=0) * (b[..., 3] - b[..., 1]).clamp(min=0)


def box_iou(a: torch.Tensor, b: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor]:
    """Pairwise IoU and union for ``[N, 4]`` against ``[M, 4]``.  Returns ``[N, M]``."""
    lt = torch.max(a[:, None, :2], b[None, :, :2])
    rb = torch.min(a[:, None, 2:], b[None, :, 2:])
    wh = (rb - lt).clamp(min=0)
    inter = wh[..., 0] * wh[..., 1]
    union = box_area(a)[:, None] + box_area(b)[None, :] - inter
    return inter / union.clamp(min=1e-9), union


def generalized_iou(a: torch.Tensor, b: torch.Tensor) -> torch.Tensor:
    """GIoU: IoU minus the share of the enclosing box that neither occupies.

        GIoU = IoU - |C \\ (A u B)| / |C|,   C = the smallest enclosing box.

    Why DETR uses it instead of IoU: IoU is exactly zero for *every* pair of
    disjoint boxes, so it gives no gradient telling a bad prediction which way to
    move.  GIoU keeps decreasing towards -1 as the boxes separate.  Range
    ``[-1, 1]``; equals IoU iff one box contains the other's enclosing hull, and
    equals 1 iff the boxes coincide.
    """
    iou, union = box_iou(a, b)
    lt = torch.min(a[:, None, :2], b[None, :, :2])
    rb = torch.max(a[:, None, 2:], b[None, :, 2:])
    wh = (rb - lt).clamp(min=0)
    enclosing = (wh[..., 0] * wh[..., 1]).clamp(min=1e-9)
    return iou - (enclosing - union) / enclosing


# --- the matching -----------------------------------------------------------


def matching_cost(pred_logits: torch.Tensor, pred_boxes: torch.Tensor,
                  tgt_labels: torch.Tensor, tgt_boxes: torch.Tensor,
                  w_class: float = 1.0, w_l1: float = 5.0, w_giou: float = 2.0) -> torch.Tensor:
    """The ``[N, M]`` cost of assigning prediction ``n`` to ground truth ``m`` [S63]."""
    prob = pred_logits.softmax(-1)                       # [N, K+1]
    cost_class = -prob[:, tgt_labels]                    # [N, M]
    cost_l1 = torch.cdist(pred_boxes, tgt_boxes, p=1)    # [N, M]
    cost_giou = -generalized_iou(pred_boxes, tgt_boxes)  # [N, M]
    return w_class * cost_class + w_l1 * cost_l1 + w_giou * cost_giou


def hungarian_match(cost: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor]:
    """Exact minimum-cost one-to-one assignment.  Returns ``(pred_idx, tgt_idx)``."""
    r, c = linear_sum_assignment(cost.detach().cpu().numpy())
    return torch.as_tensor(r, dtype=torch.long), torch.as_tensor(c, dtype=torch.long)


def greedy_match(cost: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor]:
    """Repeatedly take the globally cheapest remaining pair.

    Included only to be beaten: it is the obvious thing to write instead of
    calling the Hungarian algorithm, and it is not optimal.
    """
    c = cost.clone()
    rows, cols = [], []
    for _ in range(min(c.shape)):
        flat = c.argmin()
        i, j = divmod(int(flat), c.shape[1])
        rows.append(i)
        cols.append(j)
        c[i, :] = float("inf")
        c[:, j] = float("inf")
    return torch.tensor(rows), torch.tensor(cols)


def brute_force_match(cost: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor]:
    """Try every injection of targets into predictions.  Factorial; small inputs only."""
    n, m = cost.shape
    best, best_perm = float("inf"), None
    for perm in itertools.permutations(range(n), m):
        total = sum(cost[perm[j], j].item() for j in range(m))
        if total < best:
            best, best_perm = total, perm
    return torch.tensor(best_perm), torch.arange(m)


def assignment_cost(cost: torch.Tensor, rows: torch.Tensor, cols: torch.Tensor) -> float:
    return float(cost[rows, cols].sum())


# --- the loss ---------------------------------------------------------------


def set_criterion(pred_logits: torch.Tensor, pred_boxes: torch.Tensor,
                  tgt_labels: torch.Tensor, tgt_boxes: torch.Tensor,
                  no_object_weight: float = 0.1,
                  w_l1: float = 5.0, w_giou: float = 2.0) -> tuple[torch.Tensor, dict]:
    """DETR's loss: cross-entropy over all N slots, box loss on the matched ones.

    Every slot gets a classification target: the matched object's class, or the
    "no object" class ``K`` for the rest.  Since ``N`` is much larger than the
    number of objects, "no object" dominates the batch, so its term is
    down-weighted (0.1 in the paper).  The L1 and GIoU box losses apply only to
    matched slots -- there is no box to regress towards otherwise.
    """
    n_slots, n_classes = pred_logits.shape[0], pred_logits.shape[1] - 1
    cost = matching_cost(pred_logits, pred_boxes, tgt_labels, tgt_boxes, w_l1=w_l1, w_giou=w_giou)
    pi, ti = hungarian_match(cost)

    target_classes = torch.full((n_slots,), n_classes, dtype=torch.long, device=pred_logits.device)
    target_classes[pi] = tgt_labels[ti]
    weight = torch.ones(n_classes + 1, device=pred_logits.device)
    weight[n_classes] = no_object_weight
    loss_ce = F.cross_entropy(pred_logits, target_classes, weight=weight)

    matched_pred, matched_tgt = pred_boxes[pi], tgt_boxes[ti]
    loss_l1 = F.l1_loss(matched_pred, matched_tgt)
    loss_giou = (1 - generalized_iou(matched_pred, matched_tgt).diagonal()).mean()

    total = loss_ce + w_l1 * loss_l1 + w_giou * loss_giou
    return total, {"ce": loss_ce.item(), "l1": loss_l1.item(), "giou": loss_giou.item(),
                   "pred_idx": pi, "tgt_idx": ti}


# --- a runnable toy ---------------------------------------------------------


class TinyDetector(nn.Module):
    """A set predictor with learned queries: the DETR shape, minus the backbone.

    ``n_queries`` learned embeddings attend to the encoded input and each emits
    one (class, box).  The queries are the mechanism the lecture calls *object
    queries*: they are the slots, they are learned, and each one specialises
    during training to a region and size of object.
    """

    def __init__(self, in_dim: int = 8, d: int = 64, n_queries: int = 8, n_classes: int = 3):
        super().__init__()
        self.enc = nn.Sequential(nn.Linear(in_dim, d), nn.ReLU(), nn.Linear(d, d))
        self.queries = nn.Parameter(torch.randn(n_queries, d) * 0.1)
        self.attn = nn.MultiheadAttention(d, 4, batch_first=True)
        self.cls = nn.Linear(d, n_classes + 1)
        self.box = nn.Sequential(nn.Linear(d, d), nn.ReLU(), nn.Linear(d, 4), nn.Sigmoid())

    def forward(self, x: torch.Tensor):
        mem = self.enc(x).unsqueeze(0)                      # [1, S, d]
        q = self.queries.unsqueeze(0)                       # [1, N, d]
        out, _ = self.attn(q, mem, mem)
        out = out.squeeze(0)
        b = self.box(out)
        # sigmoid gives (cx, cy, w, h) in [0, 1]; convert to corners
        cx, cy, w, h = b.unbind(-1)
        boxes = torch.stack([cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2], dim=-1)
        return self.cls(out), boxes


def _scene(seed: int, n_obj: int = 3):
    g = torch.Generator().manual_seed(seed)
    c = torch.rand(n_obj, 2, generator=g) * 0.6 + 0.2
    s = torch.rand(n_obj, 2, generator=g) * 0.15 + 0.08
    boxes = torch.cat([c - s / 2, c + s / 2], dim=-1)
    labels = torch.randint(0, 3, (n_obj,), generator=g)
    feat = torch.cat([boxes, F.one_hot(labels, 4).float()], dim=-1)[torch.randperm(n_obj, generator=g)]
    return feat, labels, boxes


def run(steps: int = 1200, seed: int = 0, device=None) -> dict:
    """Train the toy set predictor; the metric is mean IoU on the matched pairs."""
    torch.manual_seed(seed)
    model = TinyDetector()
    opt = torch.optim.AdamW(model.parameters(), lr=3e-3)
    scenes = [_scene(s) for s in range(12)]

    losses = []
    for step in range(steps):
        feat, labels, boxes = scenes[step % len(scenes)]
        opt.zero_grad()
        logits, pred_boxes = model(feat)
        loss, _ = set_criterion(logits, pred_boxes, labels, boxes)
        loss.backward()
        opt.step()
        losses.append(loss.item())

    ious = []
    with torch.no_grad():
        for feat, labels, boxes in scenes:
            logits, pred_boxes = model(feat)
            _, info = set_criterion(logits, pred_boxes, labels, boxes)
            iou, _ = box_iou(pred_boxes[info["pred_idx"]], boxes[info["tgt_idx"]])
            ious.append(iou.diagonal().mean().item())
    return {"losses": losses, "mean_iou": sum(ious) / len(ious)}


if __name__ == "__main__":
    print("GIoU properties the definition must satisfy:")
    a = torch.tensor([[0.0, 0.0, 1.0, 1.0]])
    for name, b in [("identical", [[0.0, 0.0, 1.0, 1.0]]),
                    ("half overlap", [[0.5, 0.0, 1.5, 1.0]]),
                    ("touching", [[1.0, 0.0, 2.0, 1.0]]),
                    ("far apart", [[9.0, 0.0, 10.0, 1.0]])]:
        bb = torch.tensor(b)
        iou = box_iou(a, bb)[0].item()
        print(f"  {name:14s} IoU {iou:6.3f}   GIoU {generalized_iou(a, bb).item():7.3f}")
    print("  IoU is 0 for both 'touching' and 'far apart' and so has no gradient there;")
    print("  GIoU separates them and keeps pushing towards -1. That is why DETR uses it.")

    print("\nHungarian vs greedy vs brute force, random costs:")
    torch.manual_seed(0)
    worse = 0
    for trial in range(200):
        c = torch.rand(5, 3)
        h = assignment_cost(c, *hungarian_match(c))
        g = assignment_cost(c, *greedy_match(c))
        bf = assignment_cost(c, *brute_force_match(c))
        assert abs(h - bf) < 1e-6, (h, bf)
        worse += g > h + 1e-9
    print(f"  Hungarian matched brute force on 200/200 trials.")
    print(f"  Greedy was strictly worse on {worse}/200 -- it is not an acceptable substitute.")

    print("\nOne matching, shown:")
    torch.manual_seed(1)
    logits, boxes = torch.randn(6, 4), torch.rand(6, 4).sort(-1).values
    tl, tb = torch.tensor([0, 2]), torch.tensor([[0.1, 0.1, 0.4, 0.4], [0.5, 0.5, 0.9, 0.9]])
    cost = matching_cost(logits, boxes, tl, tb)
    pi, ti = hungarian_match(cost)
    print(f"  cost matrix [6 predictions x 2 targets], chosen pairs: "
          f"{[(int(p), int(t)) for p, t in zip(pi, ti)]}, total {assignment_cost(cost, pi, ti):.3f}")
    loss, info = set_criterion(logits, boxes, tl, tb)
    print(f"  loss {loss:.3f} = ce {info['ce']:.3f} + 5*l1 {info['l1']:.3f} + 2*giou {info['giou']:.3f}")
    print("  The other 4 slots are trained towards the 'no object' class at weight 0.1.")

    print("\nTraining the toy set predictor:")
    res = run()
    print(f"  loss {res['losses'][0]:.3f} -> {res['losses'][-1]:.3f}, "
          f"mean IoU of matched boxes {res['mean_iou']:.3f}")
