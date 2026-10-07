"""Pruning hits the requested sparsity; the lottery-ticket result is pinned honestly."""

import torch
import torch.nn as nn

from common import loss_decreased
from pruning import (lottery_ticket, lottery_ticket_sweep, magnitude_masks,
                     sparsity_of)


def test_magnitude_pruning_hits_the_requested_sparsity():
    torch.manual_seed(0)
    model = nn.Sequential(nn.Linear(40, 32), nn.ReLU(), nn.Linear(32, 4))
    for target in (0.5, 0.8, 0.95):
        m = nn.Sequential(nn.Linear(40, 32), nn.ReLU(), nn.Linear(32, 4))
        m.load_state_dict(model.state_dict())
        masks = magnitude_masks(m, target)
        for n, p in m.named_parameters():
            if n in masks:
                p.data.mul_(masks[n])
        assert abs(sparsity_of(m) - target) < 0.01
        # the surviving weights are the largest ones, by construction
        kept = torch.cat([p.data[masks[n] > 0].abs() for n, p in m.named_parameters() if n in masks])
        dropped_count = sum(int((masks[n] == 0).sum()) for n in masks)
        assert dropped_count > 0 and kept.numel() > 0


def test_lottery_ticket_runs_and_is_reported_honestly():
    """The effect does not reproduce on this toy, and the test asserts that.

    [S84] reports the lottery-ticket effect for heavily over-parameterised vision
    networks under iterative pruning. Here a 3-layer MLP on a nearly linear
    problem is pruned in one shot, and rewinding does not beat reinitialising.
    The test pins the honest outcome so that a future change which appears to
    "reproduce" the effect is noticed rather than believed.
    """
    r = lottery_ticket(sparsity=0.8, steps=200)
    assert loss_decreased(r["losses"])
    assert 0.79 < r["sparsity"] < 0.81
    # 80 % of the weights can go without hurting: the net was far too big for the task
    assert r["rewind_accuracy"] > r["dense_accuracy"] - 0.05

    sw = lottery_ticket_sweep(sparsity=0.8, seeds=3, steps=200)
    d = sw["rewind_minus_reinit"]
    assert abs(d["mean"]) < 0.05, "an effect this large on this toy would need explaining"
