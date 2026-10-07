"""Evaluate a checkpoint on the untouched test split and dump what the report needs.

    .venv/bin/python evaluate.py --config config.yaml --checkpoint models/checkpoints/baseline/best.pt

Prints: test metric, trivial-baseline metric, confusion matrix, and writes the
worst errors (highest loss) to errors.json for manual inspection. Run this
once per final model; do not tune anything after looking at its output.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import torch
import yaml
from torch.nn import functional as F
from torch.utils.data import DataLoader

from models import build_model
from train import get_device, load_dataset, seed_all


@torch.no_grad()
def predict(model: torch.nn.Module, loader: DataLoader, device: torch.device):
    model.eval()
    logits, labels = [], []
    for xb, yb in loader:
        logits.append(model(xb.to(device)).cpu())
        labels.append(yb)
    return torch.cat(logits), torch.cat(labels)


def confusion(pred: torch.Tensor, y: torch.Tensor, n_classes: int) -> torch.Tensor:
    cm = torch.zeros(n_classes, n_classes, dtype=torch.long)
    for p, t in zip(pred, y):
        cm[t, p] += 1
    return cm  # rows: true class, columns: predicted


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default="config.yaml")
    ap.add_argument("--checkpoint", required=True)
    ap.add_argument("--worst", type=int, default=20)
    args = ap.parse_args()
    cfg = yaml.safe_load(Path(args.config).read_text())
    seed_all(cfg["seed"])
    device = get_device(cfg["device"])
    data = load_dataset(cfg)
    ck = torch.load(args.checkpoint, map_location=device, weights_only=True)
    model = build_model(ck.get("config", cfg)).to(device)
    model.load_state_dict(ck["model"])

    logits, y = predict(model, DataLoader(data["test"], 256), device)
    pred = logits.argmax(1)
    n_classes = logits.shape[1]
    acc = (pred == y).float().mean().item()
    majority = torch.bincount(torch.cat([b for _, b in DataLoader(data["train"], 1024)])).argmax()
    trivial = (y == majority).float().mean().item()
    per_class_loss = F.cross_entropy(logits, y, reduction="none")
    cm = confusion(pred, y, n_classes)

    print(f"checkpoint {args.checkpoint} (step {ck.get('step')})")
    print(f"test accuracy {acc:.4f}   majority-class baseline {trivial:.4f}   n_test {len(y)}")
    print("confusion matrix (rows true, cols predicted):")
    print(cm)
    print("per-class recall:", [f"{(cm[c, c] / cm[c].sum().clamp_min(1)).item():.3f}" for c in range(n_classes)])

    worst = per_class_loss.topk(min(args.worst, len(y))).indices.tolist()
    Path("errors.json").write_text(json.dumps(
        [{"index": i, "true": int(y[i]), "pred": int(pred[i]), "loss": round(float(per_class_loss[i]), 4)}
         for i in worst], indent=2))
    print(f"{len(worst)} worst test samples written to errors.json; look at them before writing the report")


if __name__ == "__main__":
    main()
