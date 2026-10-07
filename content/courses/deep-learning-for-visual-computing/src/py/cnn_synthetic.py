"""A small CNN trained on synthetic shapes (circle, square, triangle, cross) on the CPU.

Note 04 (CNNs); the trained model is reused by gradcam.py (note 08). No dataset is
downloaded: images are rendered with numpy, seeded. Architecture in the style of
VGG blocks [S16] with batch norm [S18] and global average pooling, trained with Adam [S20].
"""
import time
from functools import lru_cache

import numpy as np
import torch
from torch import nn

CLASSES = ("circle", "square", "triangle", "cross")


def render(cls, size, cx, cy, r):
    """Boolean mask of one filled shape centred at (cx, cy) with half-size r (pixels)."""
    yy, xx = np.mgrid[0:size, 0:size].astype(float)
    dx, dy = xx - cx, yy - cy
    if cls == 0:
        return dx ** 2 + dy ** 2 <= r ** 2
    if cls == 1:
        return (np.abs(dx) <= 0.8 * r) & (np.abs(dy) <= 0.8 * r)
    if cls == 2:                                   # apex up, base at cy + r
        t = (dy + r) / (2 * r)                     # 0 at apex, 1 at base
        return (t >= 0) & (t <= 1) & (np.abs(dx) <= t * r)
    arm = max(1.0, r / 3)
    return ((np.abs(dx) <= arm) & (np.abs(dy) <= r)) | ((np.abs(dy) <= arm) & (np.abs(dx) <= r))


def clutter_line(size, rng):
    """A 1-pixel random line segment: a distractor that is not a filled shape."""
    (x0, y0), (x1, y1) = rng.uniform(0, size - 1, (2, 2))
    t = np.linspace(0, 1, 2 * size)
    img = np.zeros((size, size), bool)
    img[np.round(y0 + t * (y1 - y0)).astype(int), np.round(x0 + t * (x1 - x0)).astype(int)] = True
    return img


def make_shapes(n, size=32, seed=0, noise=0.1, clutter=2):
    """X [n,1,size,size] float32 in about [0,1], y [n] int64, masks [n,size,size] bool.

    Random class, centre, half-size r in [size/6, size/3], foreground intensity in
    [0.6, 1], background 0, `clutter` random line segments of intensity 0.5 (not in
    the mask), additive Gaussian noise; the object always lies inside."""
    rng = np.random.default_rng(seed)
    X = np.zeros((n, 1, size, size), np.float32)
    y = rng.integers(0, len(CLASSES), n)
    masks = np.zeros((n, size, size), bool)
    for i in range(n):
        r = rng.uniform(size / 6, size / 3)
        cx, cy = rng.uniform(r + 1, size - r - 2, 2)
        m = render(y[i], size, cx, cy, r)
        masks[i] = m
        X[i, 0] = m * rng.uniform(0.6, 1.0)
        for _ in range(clutter):
            X[i, 0] = np.maximum(X[i, 0], 0.5 * (clutter_line(size, rng) & ~m))
    X += rng.normal(0, noise, X.shape).astype(np.float32)
    return torch.from_numpy(X), torch.from_numpy(y), masks


def block(cin, cout, pool=True):
    layers = [nn.Conv2d(cin, cout, 3, padding=1, bias=False), nn.BatchNorm2d(cout), nn.ReLU()]
    return nn.Sequential(*layers, nn.MaxPool2d(2)) if pool else nn.Sequential(*layers)


class SmallCNN(nn.Module):
    """conv-BN-ReLU-pool x2, conv-BN-ReLU (`features`, the Grad-CAM layer), GAP, linear.

    On 1x32x32: 16x16x16 -> 32x8x8 -> 32x8x8 -> 32 -> n_classes. Receptive field of a
    `features` unit: 3, 4 (pool), 8, 10 (pool), 18 pixels (note 04 recursion)."""

    def __init__(self, n_classes=len(CLASSES), width=16):
        super().__init__()
        self.block1 = block(1, width)
        self.block2 = block(width, 2 * width)
        self.features = block(2 * width, 2 * width, pool=False)
        self.head = nn.Linear(2 * width, n_classes)

    def forward(self, x):
        a = self.features(self.block2(self.block1(x)))
        return self.head(a.mean(dim=(2, 3)))


def accuracy(model, X, y):
    model.eval()
    with torch.no_grad():
        return (model(X).argmax(1) == y).float().mean().item()


def train(model, X, y, epochs=6, lr=3e-3, batch=64, seed=0, augment=None):
    """Minibatch Adam with a cosine learning-rate schedule; returns the per-step losses."""
    g = torch.Generator().manual_seed(seed)
    opt = torch.optim.Adam(model.parameters(), lr=lr)
    steps = epochs * ((len(X) + batch - 1) // batch)
    sched = torch.optim.lr_scheduler.CosineAnnealingLR(opt, steps)
    loss_fn, losses = nn.CrossEntropyLoss(), []
    for _ in range(epochs):
        model.train()
        perm = torch.randperm(len(X), generator=g)
        for i in range(0, len(X), batch):
            idx = perm[i:i + batch]
            xb = X[idx] if augment is None else augment(X[idx], g)
            loss = loss_fn(model(xb), y[idx])
            opt.zero_grad()
            loss.backward()
            opt.step()
            sched.step()
            losses.append(loss.item())
    return losses


@lru_cache(maxsize=2)
def trained_model(seed=0, n_train=2000, n_test=500, epochs=6):
    """Train once per process (cached so the Grad-CAM tests reuse the model)."""
    torch.manual_seed(seed)
    Xtr, ytr, _ = make_shapes(n_train, seed=seed)
    Xte, yte, mte = make_shapes(n_test, seed=seed + 1000)
    model = SmallCNN()
    losses = train(model, Xtr, ytr, epochs=epochs, seed=seed)
    return {"model": model, "losses": losses, "test_acc": accuracy(model, Xte, yte),
            "X_test": Xte, "y_test": yte, "masks_test": mte}


def count_params(model):
    return sum(p.numel() for p in model.parameters())


if __name__ == "__main__":
    t0 = time.perf_counter()
    out = trained_model()
    L = out["losses"]
    print(f"SmallCNN, {count_params(out['model']):,} parameters, {len(L)} steps, "
          f"{time.perf_counter() - t0:.1f} s on CPU")
    print(f"loss {np.mean(L[:10]):.3f} -> {np.mean(L[-10:]):.3f}; test accuracy {out['test_acc']:.3f}")
    X, y = out["X_test"], out["y_test"]
    with torch.no_grad():
        pred = out["model"](X).argmax(1)
    cm = np.zeros((4, 4), int)
    np.add.at(cm, (y.numpy(), pred.numpy()), 1)
    print("confusion matrix (rows true, cols predicted):", ", ".join(CLASSES))
    print(cm)
