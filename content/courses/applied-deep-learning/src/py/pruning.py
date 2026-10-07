"""Magnitude pruning and the lottery ticket hypothesis.

The third technique of lecture 12 [S4]; number formats and int8 quantisation are
in ``deploy_optimize.py``.

**Magnitude pruning**: set the smallest weights to zero and retrain the rest.
It shrinks the *download*, not the latency -- an unstructured mask leaves a dense
tensor full of zeros that a dense kernel multiplies anyway.  Structured pruning
(whole channels, heads, blocks) changes the shapes and so does speed things up.

**The lottery ticket hypothesis** [S84]: a dense network contains a sparse
subnetwork which, trained *from the original initialisation*, matches the dense
one -- and the initialisation is claimed to be part of what was found.  This
module runs that comparison honestly, over several seeds, and reports that on
this toy it does not reproduce.  See the note for why.

Conventions: sparsity is the fraction of weight entries set to zero; only
parameters with ``ndim >= 2`` are pruned (biases and norm parameters are few and
carry the output offsets).

Run: ``python pruning.py``.
"""

from __future__ import annotations

import torch
import torch.nn as nn

from deploy_optimize import quantize_model_weights

def magnitude_masks(model: nn.Module, sparsity: float) -> dict[str, torch.Tensor]:
    """Global unstructured magnitude pruning: drop the smallest ``sparsity`` of weights.

    Global, i.e. one threshold across all weight matrices, so layers that matter
    keep more of their weights.  Biases and 1-D parameters are never pruned --
    there are few of them and they carry the output offsets.
    """
    weights = [p for n, p in model.named_parameters() if p.ndim >= 2]
    flat = torch.cat([w.detach().abs().flatten() for w in weights])
    k = int(sparsity * flat.numel())
    thresh = flat.kthvalue(k).values.item() if k > 0 else -1.0
    return {n: (p.detach().abs() > thresh).float()
            for n, p in model.named_parameters() if p.ndim >= 2}


def apply_masks(model: nn.Module, masks: dict[str, torch.Tensor]) -> None:
    with torch.no_grad():
        for n, p in model.named_parameters():
            if n in masks:
                p.mul_(masks[n])


def sparsity_of(model: nn.Module) -> float:
    tot = nz = 0
    for p in model.parameters():
        if p.ndim >= 2:
            tot += p.numel()
            nz += int((p != 0).sum())
    return 1 - nz / tot


def _make_model(seed: int, width: int = 64) -> nn.Module:
    torch.manual_seed(seed)
    return nn.Sequential(nn.Linear(20, width), nn.ReLU(),
                         nn.Linear(width, width), nn.ReLU(),
                         nn.Linear(width, 3))


def _make_data(seed: int = 0, n: int = 2000):
    """A 3-class problem with 20 inputs of which only 6 carry signal."""
    g = torch.Generator().manual_seed(seed)
    X = torch.randn(n, 20, generator=g)
    w = torch.randn(6, 3, generator=g)
    y = (X[:, :6] @ w + 0.3 * torch.randn(n, 3, generator=g)).argmax(1)
    return X[: n // 2], y[: n // 2], X[n // 2:], y[n // 2:]


def _train(model, Xtr, ytr, steps=400, masks=None, lr=3e-3):
    opt = torch.optim.AdamW(model.parameters(), lr=lr)
    lossf = nn.CrossEntropyLoss()

    def step():
        loss = lossf(model(Xtr), ytr)
        return loss

    losses = []
    for _ in range(steps):
        opt.zero_grad()
        loss = step()
        loss.backward()
        opt.step()
        if masks:                      # keep pruned weights at zero
            apply_masks(model, masks)
        losses.append(loss.item())
    return losses


def _acc(model, X, y):
    with torch.no_grad():
        return (model(X).argmax(1) == y).float().mean().item()


def lottery_ticket(sparsity: float = 0.8, steps: int = 400, seed: int = 0) -> dict:
    """One iteration of the lottery-ticket experiment [S84].

    Train a dense net; keep the largest ``1 - sparsity`` of its weights as a
    mask; then compare two ways of retraining that *same* mask:

    * **rewind** -- restore the surviving weights to the values they had at
      initialisation (the "winning ticket");
    * **reinit** -- draw fresh random values for them.

    Frankle & Carbin's claim is that rewind matches or beats the dense network
    while reinit does not, i.e. what was found is a subnetwork *together with*
    its initialisation, not just a sparsity pattern.

    **On this toy the claim does not reproduce** -- see ``lottery_ticket_sweep``
    and the note.  That is a result about the experiment, not about the paper:
    the effect is reported for over-parameterised vision networks at high
    sparsity after *iterative* pruning, and a 3-layer MLP on a linearly
    separable problem is none of those things.
    """
    Xtr, ytr, Xte, yte = _make_data(seed)

    model = _make_model(seed)
    init = {n: p.detach().clone() for n, p in model.named_parameters()}
    dense_losses = _train(model, Xtr, ytr, steps)
    dense_acc = _acc(model, Xte, yte)

    masks = magnitude_masks(model, sparsity)

    rewound = _make_model(seed)
    with torch.no_grad():
        for n, p in rewound.named_parameters():
            p.copy_(init[n])
    apply_masks(rewound, masks)
    _train(rewound, Xtr, ytr, steps, masks)
    rewind_acc = _acc(rewound, Xte, yte)

    reinit = _make_model(seed + 1000)          # same shapes, different draw
    apply_masks(reinit, masks)
    _train(reinit, Xtr, ytr, steps, masks)
    reinit_acc = _acc(reinit, Xte, yte)

    return {"losses": dense_losses, "sparsity": sparsity_of(rewound),
            "dense_accuracy": dense_acc, "rewind_accuracy": rewind_acc,
            "reinit_accuracy": reinit_acc,
            "quantized": quantize_model_weights(rewound)}


def lottery_ticket_sweep(sparsity: float = 0.8, seeds: int = 5, steps: int = 400) -> dict:
    """Run the experiment over several seeds and report mean and spread.

    A single seed is the mistake assignment 2 [S13] and note 11 both warn about:
    the three numbers differ by less than the seed-to-seed spread, so one run
    "shows" whichever ordering it happens to draw.
    """
    rows = [lottery_ticket(sparsity, steps, seed=s) for s in range(seeds)]
    out = {}
    for key in ("dense_accuracy", "rewind_accuracy", "reinit_accuracy"):
        vals = torch.tensor([r[key] for r in rows])
        out[key] = {"mean": vals.mean().item(), "std": vals.std().item()}
    d = torch.tensor([r["rewind_accuracy"] - r["reinit_accuracy"] for r in rows])
    out["rewind_minus_reinit"] = {"mean": d.mean().item(), "std": d.std().item(),
                                  "stderr": (d.std() / seeds ** 0.5).item()}
    out["seeds"] = seeds
    return out



def run(steps: int = 400, sparsity: float = 0.8, seed: int = 0, device=None) -> dict:
    """Entry point matching the other modules: trains, prunes, compares, quantises."""
    return lottery_ticket(sparsity, steps, seed)


if __name__ == "__main__":
    print("Pruning: how much can be removed before accuracy moves? (20-input, 3-class toy)")
    for sp in (0.5, 0.8, 0.9, 0.95):
        r = lottery_ticket(sparsity=sp)
        print(f"  sparsity {r['sparsity']:5.0%}: dense {r['dense_accuracy']:.3f}  "
              f"pruned+retrained (rewind) {r['rewind_accuracy']:.3f}  (reinit) {r['reinit_accuracy']:.3f}")

    print("\nThe lottery-ticket comparison at 80 % sparsity, over 5 seeds (mean +/- std):")
    sw = lottery_ticket_sweep(sparsity=0.8, seeds=5)
    for k in ("dense_accuracy", "rewind_accuracy", "reinit_accuracy"):
        print(f"  {k:18s} {sw[k]['mean']:.3f} +/- {sw[k]['std']:.3f}")
    d = sw["rewind_minus_reinit"]
    print(f"  rewind - reinit    {d['mean']:+.3f} +/- {d['std']:.3f} (standard error {d['stderr']:.3f})")
    print(f"  This does NOT reproduce the effect: {abs(d['mean'] / d['stderr']):.1f} standard errors,")
    print("  in the direction OPPOSITE to the hypothesis. Expected here -- [S84] reports it for")
    print("  heavily over-parameterised vision nets under *iterative* pruning, and 95 % sparsity")
    print("  costing nothing above says this net is far too big for the task, so there is no")
    print("  capacity pressure for a ticket to matter. A single seed would have 'shown'")
    print("  whichever ordering it happened to draw -- which is the discipline assignment 2 asks for.")

    q = lottery_ticket(0.8)["quantized"]
    print(f"\n  Pruned and quantised: {q['fp32_bytes'] / 1024:.1f} KiB fp32 -> "
          f"{q['int8_bytes'] / 1024:.1f} KiB int8 ({q['compression']:.1f}x), and 80 % of those")
    print("  bytes are zeros that a dense kernel still multiplies: unstructured sparsity")
    print("  shrinks the download, not the latency.")
