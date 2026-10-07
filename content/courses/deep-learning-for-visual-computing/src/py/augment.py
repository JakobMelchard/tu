"""Image augmentation transforms with the invariances they assume, plus a 3x5 digit font
to show when a transform is *not* label-preserving.

Note 08 (practical aspects); the equivariance tests belong to note 04. Tensors are
[N, C, H, W] (or [C, H, W]) floats. Mixup after Zhang et al. [S35], cutout after DeVries &
Taylor [S35]. All randomness goes through an explicit torch.Generator.
"""
import numpy as np
import torch
import torch.nn.functional as F

# 3x5 bitmap digits, rows top to bottom
GLYPHS = {
    0: ["###", "#.#", "#.#", "#.#", "###"], 1: [".#.", "##.", ".#.", ".#.", "###"],
    2: ["###", "..#", "###", "#..", "###"], 3: ["###", "..#", "###", "..#", "###"],
    4: ["#.#", "#.#", "###", "..#", "..#"], 5: ["###", "#..", "###", "..#", "###"],
    6: ["###", "#..", "###", "#.#", "###"], 7: ["###", "..#", "..#", "..#", "..#"],
    8: ["###", "#.#", "###", "#.#", "###"], 9: ["###", "#.#", "###", "..#", "###"],
}


def render_digit(d, scale=4, pad=2):
    """[1, 5*scale + 2 pad, 3*scale + 2 pad] image of digit d (nearest-neighbour upscaled)."""
    g = np.array([[c == "#" for c in row] for row in GLYPHS[d]], np.float32)
    g = np.kron(g, np.ones((scale, scale), np.float32))
    return torch.from_numpy(np.pad(g, pad))[None]


def identify_digit(img, scale=4, pad=2):
    """Inverse of render_digit (exact match) or None: which label would a flipped glyph get?"""
    for d in GLYPHS:
        r = render_digit(d, scale, pad)
        if r.shape == img.shape and torch.equal(r, img):
            return d
    return None


def hflip(x):
    return x.flip(-1)


def vflip(x):
    return x.flip(-2)


def rot90(x, k=1):
    return torch.rot90(x, k, dims=(-2, -1))


def translate(x, dx, dy):
    """Shift content by (dx, dy) pixels with zero fill (content leaving the frame is lost)."""
    H, W = x.shape[-2:]
    out = torch.zeros_like(x)
    ys, yd = (slice(0, H - dy), slice(dy, H)) if dy >= 0 else (slice(-dy, H), slice(0, H + dy))
    xs, xd = (slice(0, W - dx), slice(dx, W)) if dx >= 0 else (slice(-dx, W), slice(0, W + dx))
    out[..., yd, xd] = x[..., ys, xs]
    return out


def random_crop(x, pad, g, mode="constant"):
    """Pad by `pad` on every side and crop back to the original size at a random offset
    (the CIFAR recipe: pad 4, crop 32). One offset per call."""
    H, W = x.shape[-2:]
    xp = F.pad(x, (pad,) * 4, mode=mode)             # 'reflect' needs [C,H,W] or [N,C,H,W]
    i, j = torch.randint(0, 2 * pad + 1, (2,), generator=g).tolist()
    return xp[..., i:i + H, j:j + W]


def brightness_contrast(x, brightness=0.0, contrast=1.0):
    """x' = contrast (x - mean) + mean + brightness, per image (mean over C, H, W)."""
    m = x.mean(dim=(-3, -2, -1), keepdim=True)
    return contrast * (x - m) + m + brightness


def gaussian_noise(x, sigma, g):
    return x + sigma * torch.randn(x.shape, generator=g)


def cutout(x, size, g):
    """Zero one random size x size square per image (centre may lie near the border)."""
    x = x.clone()
    H, W = x.shape[-2:]
    for n in range(x.shape[0]):
        cy, cx = torch.randint(0, H, (1,), generator=g).item(), torch.randint(0, W, (1,), generator=g).item()
        x[n, :, max(0, cy - size // 2):cy + size // 2, max(0, cx - size // 2):cx + size // 2] = 0
    return x


def mixup(x, y_onehot, lam, perm):
    """x~ = lam x + (1 - lam) x[perm], y~ = lam y + (1 - lam) y[perm]: labels are mixed too,
    so the target is a distribution, not a class index [S35]."""
    return lam * x + (1 - lam) * x[perm], lam * y_onehot + (1 - lam) * y_onehot[perm]


def fit_normalizer(X_train):
    """Per-channel mean and std from the TRAINING set only; apply the same to val/test."""
    return X_train.mean(dim=(0, 2, 3)), X_train.std(dim=(0, 2, 3))


def normalize(x, mean, std):
    return (x - mean[:, None, None]) / std[:, None, None]


def shapes_augment(x, g):
    """Training augmentation for cnn_synthetic: random h/v flips, 90-degree rotations and a
    +-3 px shift. Label-preserving there (a triangle rotated is still a triangle); not for
    digits (see GLYPHS: hflip(2) = 5, rot180(6) = 9)."""
    if torch.rand(1, generator=g) < 0.5:
        x = hflip(x)
    x = rot90(x, int(torch.randint(0, 4, (1,), generator=g)))
    dx, dy = torch.randint(-3, 4, (2,), generator=g).tolist()
    return translate(x, dx, dy)


if __name__ == "__main__":
    for name, t in [("hflip", hflip), ("vflip", vflip), ("rot180", lambda x: rot90(x, 2))]:
        m = {d: identify_digit(t(render_digit(d))) for d in GLYPHS}
        print(f"{name:>6}: digit -> label of the transformed glyph", m)
    from cnn_synthetic import SmallCNN, accuracy, make_shapes, train, trained_model
    base = trained_model()
    Xt, yt = base["X_test"], base["y_test"]
    print(f"SmallCNN trained without augmentation: test acc {base['test_acc']:.3f}, "
          f"on vflipped test {accuracy(base['model'], vflip(Xt), yt):.3f}, "
          f"on rot90 test {accuracy(base['model'], rot90(Xt), yt):.3f}")
    torch.manual_seed(0)
    Xtr, ytr, _ = make_shapes(2000, seed=0)
    aug = SmallCNN()
    train(aug, Xtr, ytr, epochs=6, augment=shapes_augment)
    print(f"SmallCNN trained with shapes_augment: test acc {accuracy(aug, Xt, yt):.3f}, "
          f"on vflipped test {accuracy(aug, vflip(Xt), yt):.3f}")
