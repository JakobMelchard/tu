"""Segmentation losses and metrics on masks: pixel-wise cross-entropy, soft Dice, soft IoU
(Jaccard), confusion matrix and mean IoU, and a two-level U-Net to exercise them.

Note 05 (detection and segmentation). Dice loss after V-Net [S26], U-Net skip
connections by concatenation [S26]. numpy versions are checked against torch in
test_segmentation_losses.py; the torch versions are what a training loop uses.
"""
import numpy as np
import torch
import torch.nn.functional as F
from torch import nn


def one_hot(mask, K):
    """[N,H,W] int -> [N,K,H,W] float."""
    return (np.arange(K)[None, :, None, None] == mask[:, None]).astype(float)


def log_softmax(z, axis=1):
    z = z - z.max(axis=axis, keepdims=True)
    return z - np.log(np.exp(z).sum(axis=axis, keepdims=True))


def pixel_cross_entropy(logits, mask, weight=None):
    """Mean over pixels of -w_y log softmax(z)_y; with class weights the mean is weighted
    (divides by sum of w_y), as torch does. logits [N,K,H,W], mask [N,H,W]."""
    lp = log_softmax(logits)
    nll = -np.take_along_axis(lp, mask[:, None], axis=1)[:, 0]
    w = np.ones_like(nll) if weight is None else np.asarray(weight)[mask]
    return float((w * nll).sum() / w.sum())


def soft_dice_loss(probs, target, eps=1.0):
    """1 - mean_k (2 sum p g + eps) / (sum p + sum g + eps), sums over batch and pixels.
    probs, target [N,K,H,W]. Per-class normalisation makes a rare class count as much as a
    frequent one: the reason Dice is used for small foregrounds."""
    ax = (0, 2, 3)
    inter = (probs * target).sum(ax)
    return float(1 - np.mean((2 * inter + eps) / (probs.sum(ax) + target.sum(ax) + eps)))


def soft_iou_loss(probs, target, eps=1.0):
    """1 - mean_k (sum p g + eps) / (sum p + sum g - sum p g + eps)  (soft Jaccard)."""
    ax = (0, 2, 3)
    inter = (probs * target).sum(ax)
    return float(1 - np.mean((inter + eps) / (probs.sum(ax) + target.sum(ax) - inter + eps)))


def dice_score(pred, gt):
    """Hard Dice 2|A∩B| / (|A| + |B|) for boolean masks (1 if both empty)."""
    s = pred.sum() + gt.sum()
    return 1.0 if s == 0 else 2 * np.logical_and(pred, gt).sum() / s


def iou_score(pred, gt):
    u = np.logical_or(pred, gt).sum()
    return 1.0 if u == 0 else np.logical_and(pred, gt).sum() / u


def confusion(pred, gt, K):
    """K x K matrix, rows = ground truth, columns = prediction, summed over all pixels."""
    cm = np.zeros((K, K), int)
    np.add.at(cm, (gt.ravel(), pred.ravel()), 1)
    return cm


def mean_iou(pred, gt, K):
    """Dataset-level IoU per class TP / (TP + FP + FN) from the pooled confusion matrix;
    mIoU = mean over classes that occur (in gt or prediction)."""
    cm = confusion(pred, gt, K)
    tp = np.diag(cm)
    denom = cm.sum(0) + cm.sum(1) - tp
    ious = np.where(denom > 0, tp / np.maximum(denom, 1), np.nan)
    return float(np.nanmean(ious)), ious


# ---------------------------------------------------------------- torch versions and a U-Net
def dice_loss_torch(logits, mask, eps=1.0):
    K = logits.shape[1]
    p = logits.softmax(1)
    g = F.one_hot(mask, K).permute(0, 3, 1, 2).float()
    inter = (p * g).sum((0, 2, 3))
    return 1 - ((2 * inter + eps) / (p.sum((0, 2, 3)) + g.sum((0, 2, 3)) + eps)).mean()


def conv_block(cin, cout):
    return nn.Sequential(nn.Conv2d(cin, cout, 3, padding=1), nn.BatchNorm2d(cout), nn.ReLU(),
                         nn.Conv2d(cout, cout, 3, padding=1), nn.BatchNorm2d(cout), nn.ReLU())


class TinyUNet(nn.Module):
    """Two resolution levels. enc1 [C,H,W] -> pool -> enc2 [2C,H/2,W/2] -> up (transposed conv
    k2 s2) [C,H,W] -> concat with enc1 -> [2C,H,W] -> dec -> 1x1 conv -> [K,H,W]."""

    def __init__(self, K=2, C=8):
        super().__init__()
        self.enc1, self.enc2 = conv_block(1, C), conv_block(C, 2 * C)
        self.up = nn.ConvTranspose2d(2 * C, C, 2, stride=2)
        self.dec = conv_block(2 * C, C)
        self.out = nn.Conv2d(C, K, 1)

    def forward(self, x):
        e1 = self.enc1(x)
        e2 = self.enc2(F.max_pool2d(e1, 2))
        return self.out(self.dec(torch.cat([self.up(e2), e1], 1)))   # skip: concatenate, not add


def train_unet(X, masks, steps=60, lr=1e-2, loss="ce+dice", seed=0, batch=32):
    torch.manual_seed(seed)
    net, M = TinyUNet(), torch.as_tensor(masks).long()
    opt = torch.optim.Adam(net.parameters(), lr=lr)
    g, losses = torch.Generator().manual_seed(seed), []
    for _ in range(steps):
        idx = torch.randint(0, len(X), (batch,), generator=g)
        z = net(X[idx])
        L = F.cross_entropy(z, M[idx]) if "ce" in loss else 0
        L = L + (dice_loss_torch(z, M[idx]) if "dice" in loss else 0)
        opt.zero_grad()
        L.backward()
        opt.step()
        losses.append(L.item())
    return net, losses


if __name__ == "__main__":
    # the imbalance argument: 1 % foreground, a model that predicts "all background"
    gt = np.zeros((1, 100, 100), int)
    gt[0, 45:55, 45:55] = 1
    probs = np.stack([np.full((100, 100), 0.99), np.full((100, 100), 0.01)])[None]
    ce = pixel_cross_entropy(np.log(probs), gt)
    print(f"all-background predictor on 1% foreground: CE {ce:.3f}, pixel accuracy 0.99, "
          f"soft Dice loss {soft_dice_loss(probs, one_hot(gt, 2)):.3f}, "
          f"foreground IoU {iou_score(probs[0].argmax(0) == 1, gt[0] == 1):.2f}")
    a, b = np.zeros((8, 8), bool), np.zeros((8, 8), bool)
    a[1:5, 1:5], b[3:7, 3:7] = True, True
    d, j = dice_score(a, b), iou_score(a, b)
    print(f"two 4x4 squares overlapping 2x2: Dice {d:.3f}, IoU {j:.3f}, 2IoU/(1+IoU) {2 * j / (1 + j):.3f}")
    from cnn_synthetic import make_shapes
    X, _, m = make_shapes(512, seed=0)
    Xt, _, mt = make_shapes(128, seed=1)
    net, losses = train_unet(X, m)
    net.eval()
    with torch.no_grad():
        pred = net(Xt).argmax(1).numpy()
    miou, ious = mean_iou(pred, mt.astype(int), 2)
    print(f"TinyUNet, 60 steps: loss {losses[0]:.3f} -> {losses[-1]:.3f}; test IoU per class "
          f"{np.round(ious, 3).tolist()}, mIoU {miou:.3f}")
