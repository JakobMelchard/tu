"""Model registry: `build_model(cfg)` returns an nn.Module from the `model:` block of config.yaml.

Add your own architecture as a class here and register it in MODELS. Keep
data-dependent sizes (number of classes, input channels) in the config, not
hard-coded in the class.
"""

from __future__ import annotations

from torch import nn


class ShapeCNN(nn.Module):
    """Placeholder: three conv blocks, global average pooling, linear head."""

    def __init__(self, width: int = 16, n_classes: int = 3, dropout: float = 0.0, in_channels: int = 1):
        super().__init__()

        def block(c_in: int, c_out: int) -> nn.Sequential:
            return nn.Sequential(nn.Conv2d(c_in, c_out, 3, padding=1, bias=False), nn.BatchNorm2d(c_out), nn.ReLU())

        self.features = nn.Sequential(block(in_channels, width), block(width, width), nn.MaxPool2d(2),
                                      block(width, 2 * width), nn.Dropout(dropout))
        self.head = nn.Linear(2 * width, n_classes)

    def forward(self, x):
        return self.head(self.features(x).mean(dim=(2, 3)))


MODELS = {"shape_cnn": ShapeCNN}


def build_model(cfg: dict) -> nn.Module:
    kw = {k: v for k, v in cfg["model"].items() if k != "name"}
    return MODELS[cfg["model"]["name"]](**kw)
