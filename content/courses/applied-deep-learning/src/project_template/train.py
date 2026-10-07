"""Training entry point: config -> data -> model -> optimiser -> loop with logging, eval and checkpoints.

    .venv/bin/python train.py --config config.yaml [--steps N] [--experiment NAME]

Everything tunable lives in config.yaml; command-line flags only override for quick tests.
The synthetic `load_dataset` makes the skeleton runnable; replace it with your data.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import random
import subprocess
import time
from pathlib import Path

import numpy as np
import torch
import yaml
from torch.nn import functional as F
from torch.utils.data import DataLoader, TensorDataset

from models import build_model


def get_device(name: str) -> torch.device:
    if name != "auto":
        return torch.device(name)
    if torch.backends.mps.is_available():
        return torch.device("mps")
    return torch.device("cuda" if torch.cuda.is_available() else "cpu")


def seed_all(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)


def git_hash() -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], text=True).strip()
    except Exception:  # not a git repo
        return "unknown"


def load_dataset(cfg: dict) -> dict[str, TensorDataset]:
    """Placeholder: synthetic circle/square/triangle images. Replace with a loader for data/processed."""
    d, n, size = cfg["data"], cfg["data"]["n_samples"], cfg["data"]["image_size"]
    rng = np.random.default_rng(cfg["seed"])
    X = np.zeros((n, 1, size, size), dtype=np.float32)
    y = rng.integers(0, 3, size=n)
    yy, xx = np.mgrid[0:size, 0:size]
    for i in range(n):
        r = rng.uniform(0.15, 0.3) * size
        cx, cy = rng.uniform(r + 1, size - r - 1, size=2)
        dx, dy = xx - cx, yy - cy
        X[i, 0] = [dx**2 + dy**2 <= r**2, (abs(dx) <= r) & (abs(dy) <= r),
                   (dy >= -r) & (dy <= r) & (abs(dx) <= (dy + r) / 2)][y[i]]
    X = np.clip(X + 0.1 * rng.standard_normal(X.shape).astype(np.float32), 0, 1)
    perm = rng.permutation(n)  # split once by seed; write perm to data/splits.json in a real project
    n_test, n_val = int(d["test_fraction"] * n), int(d["val_fraction"] * n)
    idx = {"test": perm[:n_test], "val": perm[n_test : n_test + n_val], "train": perm[n_test + n_val :]}
    return {k: TensorDataset(torch.from_numpy(X[v]), torch.from_numpy(y[v]).long()) for k, v in idx.items()}


@torch.no_grad()
def evaluate(model: torch.nn.Module, loader: DataLoader, device: torch.device) -> dict[str, float]:
    model.eval()
    loss_sum, correct, n = 0.0, 0, 0
    for xb, yb in loader:
        xb, yb = xb.to(device), yb.to(device)
        logits = model(xb)
        loss_sum += F.cross_entropy(logits, yb, reduction="sum").item()
        correct += (logits.argmax(1) == yb).sum().item()
        n += len(yb)
    model.train()
    return {"loss": loss_sum / n, "accuracy": correct / n}


def make_scheduler(opt: torch.optim.Optimizer, cfg: dict, steps: int):
    kind = cfg["train"]["schedule"]
    if kind == "onecycle":
        return torch.optim.lr_scheduler.OneCycleLR(opt, max_lr=cfg["train"]["lr"], total_steps=steps)
    if kind == "cosine":
        return torch.optim.lr_scheduler.CosineAnnealingLR(opt, steps)
    return torch.optim.lr_scheduler.LambdaLR(opt, lambda _: 1.0)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default="config.yaml")
    ap.add_argument("--steps", type=int)
    ap.add_argument("--experiment")
    args = ap.parse_args()
    cfg = yaml.safe_load(Path(args.config).read_text())
    if args.steps:
        cfg["train"]["steps"] = args.steps
    if args.experiment:
        cfg["experiment"] = args.experiment
    tc = cfg["train"]
    seed_all(cfg["seed"])
    device = get_device(cfg["device"])
    out_dir = Path(tc["checkpoint_dir"]) / cfg["experiment"]
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "config.json").write_text(json.dumps({**cfg, "git": git_hash()}, indent=2))  # what produced this run

    data = load_dataset(cfg)
    gen = torch.Generator().manual_seed(cfg["seed"])
    train_loader = DataLoader(data["train"], tc["batch_size"], shuffle=True, generator=gen,
                              num_workers=cfg["data"]["num_workers"], drop_last=True)
    val_loader = DataLoader(data["val"], 256)
    model = build_model(cfg).to(device)
    opt = torch.optim.AdamW(model.parameters(), lr=tc["lr"], weight_decay=tc["weight_decay"])
    sched = make_scheduler(opt, cfg, tc["steps"])
    step, best = 0, -math.inf
    if tc["resume"]:
        ck = torch.load(tc["resume"], map_location=device, weights_only=True)
        model.load_state_dict(ck["model"]), opt.load_state_dict(ck["optimizer"]), sched.load_state_dict(ck["scheduler"])
        step, best = ck["step"], ck["best"]
    print(f"{cfg['experiment']}: {sum(p.numel() for p in model.parameters())} params on {device}, "
          f"{len(data['train'])}/{len(data['val'])}/{len(data['test'])} train/val/test")

    log = csv.writer((out_dir / "log.csv").open("a"))
    log.writerow(["step", "train_loss", "lr", "val_loss", "val_accuracy", "seconds"])
    t0, use_amp = time.perf_counter(), tc["amp"] and device.type != "mps"
    while step < tc["steps"]:
        for xb, yb in train_loader:
            xb, yb = xb.to(device), yb.to(device)
            with torch.autocast(device_type=device.type, dtype=torch.bfloat16, enabled=use_amp):
                loss = F.cross_entropy(model(xb), yb)
            opt.zero_grad(set_to_none=True)
            loss.backward()
            if tc["clip_grad"]:
                torch.nn.utils.clip_grad_norm_(model.parameters(), tc["clip_grad"])
            opt.step()
            sched.step()
            step += 1
            if step % tc["log_every"] == 0:
                print(f"step {step:6d}  loss {loss.item():.4f}  lr {opt.param_groups[0]['lr']:.2e}")
            if step % tc["eval_every"] == 0 or step == tc["steps"]:
                val = evaluate(model, val_loader, device)
                log.writerow([step, loss.item(), opt.param_groups[0]["lr"], val["loss"], val["accuracy"],
                              round(time.perf_counter() - t0, 1)])
                state = {"model": model.state_dict(), "optimizer": opt.state_dict(), "scheduler": sched.state_dict(),
                         "step": step, "best": max(best, val["accuracy"]), "config": cfg}
                torch.save(state, out_dir / "last.pt")
                if val["accuracy"] > best:
                    best = val["accuracy"]
                    torch.save(state, out_dir / "best.pt")
                print(f"  val loss {val['loss']:.4f}  val accuracy {val['accuracy']:.4f}  best {best:.4f}")
            if step >= tc["steps"]:
                break
    print(f"done in {time.perf_counter() - t0:.1f}s; checkpoints in {out_dir}")


if __name__ == "__main__":
    main()
