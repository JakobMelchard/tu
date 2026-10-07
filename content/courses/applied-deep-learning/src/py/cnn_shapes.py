"""CNN on synthetic geometric shapes: circle / square / triangle classification.

Data is generated on the fly (no downloads). Demonstrates conv-BN-ReLU blocks,
max pooling, global average pooling, receptive-field arithmetic and a full
training loop with AdamW plus a cosine learning-rate schedule.
"""

from __future__ import annotations

import math

import numpy as np
import torch
from torch import nn
from torch.nn import functional as F

from common import Timer, count_params, get_device, loss_decreased, seed_all, train_loop

CLASSES = ("circle", "square", "triangle")


def _shape_mask(kind: int, size: int, cx: float, cy: float, r: float) -> np.ndarray:
    """Boolean mask of one shape on a size x size grid (numpy, vectorised)."""
    yy, xx = np.mgrid[0:size, 0:size].astype(np.float64)
    dx, dy = xx - cx, yy - cy
    if kind == 0:  # circle
        return dx**2 + dy**2 <= r**2
    if kind == 1:  # axis-aligned square
        return (np.abs(dx) <= r) & (np.abs(dy) <= r)
    # upright triangle: apex at (cx, cy - r), base at cy + r
    inside_y = (dy >= -r) & (dy <= r)
    half_width = (dy + r) / 2.0  # width grows linearly from apex to base
    return inside_y & (np.abs(dx) <= half_width)


def make_shapes(n: int, size: int = 32, seed: int = 0, noise: float = 0.1) -> tuple[torch.Tensor, torch.Tensor]:
    """Return X [n,1,size,size] in [0,1] and y in {0 circle, 1 square, 2 triangle}."""
    rng = np.random.default_rng(seed)
    X = np.zeros((n, 1, size, size), dtype=np.float32)
    y = rng.integers(0, 3, size=n)
    for i in range(n):
        r = rng.uniform(0.15, 0.3) * size
        cx = rng.uniform(r + 1, size - r - 1)
        cy = rng.uniform(r + 1, size - r - 1)
        X[i, 0] = _shape_mask(int(y[i]), size, cx, cy, r)
    X += noise * rng.standard_normal(X.shape).astype(np.float32)
    return torch.from_numpy(np.clip(X, 0.0, 1.0)), torch.from_numpy(y).long()


def conv_block(c_in: int, c_out: int) -> nn.Sequential:
    return nn.Sequential(nn.Conv2d(c_in, c_out, 3, padding=1, bias=False), nn.BatchNorm2d(c_out), nn.ReLU())


class ShapeCNN(nn.Module):
    """conv3x3(16)-conv3x3(16)-maxpool2-conv3x3(32)-GAP-linear."""

    def __init__(self, n_classes: int = 3, width: int = 16):
        super().__init__()
        self.features = nn.Sequential(
            conv_block(1, width),
            conv_block(width, width),
            nn.MaxPool2d(2),
            conv_block(width, 2 * width),
        )
        self.head = nn.Linear(2 * width, n_classes)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        h = self.features(x)  # [B, 2w, H/2, W/2]
        return self.head(h.mean(dim=(2, 3)))  # global average pool -> [B, 2w] -> logits

    @staticmethod
    def receptive_field() -> int:
        """r_l = r_{l-1} + (k_l - 1) * prod_{j<l} s_j over the layers (k, s)."""
        layers = [(3, 1), (3, 1), (2, 2), (3, 1)]
        r, jump = 1, 1
        for k, s in layers:
            r += (k - 1) * jump
            jump *= s
        return r


def output_size(i: int, k: int, s: int = 1, p: int = 0, d: int = 1) -> int:
    """Conv output size o = floor((i + 2p - d(k-1) - 1)/s) + 1."""
    return (i + 2 * p - d * (k - 1) - 1) // s + 1


@torch.no_grad()
def accuracy(model: nn.Module, X: torch.Tensor, y: torch.Tensor, batch: int = 256) -> float:
    model.eval()
    device = next(model.parameters()).device
    correct = 0
    for i in range(0, len(X), batch):
        logits = model(X[i : i + batch].to(device))
        correct += (logits.argmax(1).cpu() == y[i : i + batch]).sum().item()
    model.train()
    return correct / len(X)


def run(steps: int = 300, batch: int = 64, n_train: int = 2000, n_test: int = 500,
        device: torch.device | None = None, seed: int = 0, log_every: int = 0) -> dict:
    device = device or get_device()
    gen = seed_all(seed)
    X, y = make_shapes(n_train, seed=seed)
    Xt, yt = make_shapes(n_test, seed=seed + 1)
    X, y = X.to(device), y.to(device)
    model = ShapeCNN().to(device)
    opt = torch.optim.AdamW(model.parameters(), lr=3e-3, weight_decay=1e-4)
    sched = torch.optim.lr_scheduler.OneCycleLR(opt, max_lr=3e-3, total_steps=steps)

    def step_fn() -> torch.Tensor:
        idx = torch.randint(0, n_train, (batch,), generator=gen).to(device)
        xb = X[idx]
        if torch.rand(1, generator=gen).item() < 0.5:  # augmentation: horizontal flip
            xb = xb.flip(-1)
        return F.cross_entropy(model(xb), y[idx])

    with Timer() as t:
        losses = train_loop(step_fn, opt, steps, log_every=log_every, scheduler=sched)
    return {"losses": losses, "accuracy": accuracy(model, Xt, yt), "model": model, "seconds": t.seconds}


if __name__ == "__main__":
    m = ShapeCNN()
    print(f"params {count_params(m)}, receptive field {ShapeCNN.receptive_field()} px, "
          f"conv out size for i=32,k=3,p=1: {output_size(32, 3, p=1)}")
    out = run(log_every=50)
    print(f"test accuracy {out['accuracy']:.3f} after {len(out['losses'])} steps in {out['seconds']:.1f}s, "
          f"loss decreased: {loss_decreased(out['losses'])}")
