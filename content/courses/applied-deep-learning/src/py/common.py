"""Shared helpers for the Applied Deep Learning reference implementations.

Device selection (mps > cpu), seeding, a generic step-based training loop,
a wall-clock timer and the loss-decrease check used by every test.
"""

from __future__ import annotations

import random
import time
from collections.abc import Callable

import numpy as np
import torch


def get_device(prefer: str | None = None) -> torch.device:
    """Return the preferred device: explicit name, else MPS on Apple Silicon, else CPU."""
    if prefer is not None:
        return torch.device(prefer)
    if torch.backends.mps.is_available():
        return torch.device("mps")
    if torch.cuda.is_available():
        return torch.device("cuda")
    return torch.device("cpu")


def seed_all(seed: int = 0) -> torch.Generator:
    """Seed python, numpy and torch; return a torch.Generator seeded the same way."""
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    return torch.Generator().manual_seed(seed)


def count_params(model: torch.nn.Module, trainable_only: bool = False) -> int:
    return sum(p.numel() for p in model.parameters() if p.requires_grad or not trainable_only)


class Timer:
    """`with Timer() as t: ...; t.seconds` measures wall-clock time of the block."""

    def __enter__(self) -> "Timer":
        self.start = time.perf_counter()
        self.seconds = 0.0
        return self

    def __exit__(self, *exc: object) -> None:
        self.seconds = time.perf_counter() - self.start


def train_loop(
    step_fn: Callable[[], torch.Tensor],
    optimizer: torch.optim.Optimizer,
    steps: int,
    log_every: int = 0,
    scheduler: torch.optim.lr_scheduler.LRScheduler | None = None,
    clip_grad: float | None = None,
) -> list[float]:
    """Generic step loop: `step_fn` samples a batch and returns the loss tensor.

    The four canonical lines are zero_grad -> loss.backward() -> step -> scheduler.step().
    Returns the per-step loss values as floats.
    """
    losses: list[float] = []
    for step in range(1, steps + 1):
        optimizer.zero_grad(set_to_none=True)
        loss = step_fn()
        loss.backward()
        if clip_grad is not None:
            params = [p for g in optimizer.param_groups for p in g["params"]]
            torch.nn.utils.clip_grad_norm_(params, clip_grad)
        optimizer.step()
        if scheduler is not None:
            scheduler.step()
        losses.append(loss.item())
        if log_every and step % log_every == 0:
            lr = optimizer.param_groups[0]["lr"]
            print(f"step {step:5d}  loss {loss.item():.4f}  lr {lr:.2e}")
    return losses


def loss_decreased(losses: list[float], frac: float = 0.1) -> bool:
    """True if the mean of the last `frac` of the losses is below the mean of the first `frac`."""
    k = max(1, int(len(losses) * frac))
    return float(np.mean(losses[-k:])) < float(np.mean(losses[:k]))


def moving_average(xs: list[float], window: int) -> list[float]:
    out: list[float] = []
    for i in range(len(xs)):
        lo = max(0, i - window + 1)
        out.append(float(np.mean(xs[lo : i + 1])))
    return out
