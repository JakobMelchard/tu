"""CTC checked three ways: closed forms, brute force, and torch.nn.CTCLoss.

The reference results reproduced here are:

* ``torch.nn.CTCLoss`` [S96], the reference implementation of Graves et al. [S48];
* exhaustive enumeration of every path of length T and application of the
  collapse rule, which is the definition CTC's dynamic program is an efficient
  form of;
* two hand-computable cases (T = 1, and T = 2 with one label).
"""

import math

import torch

from common import loss_decreased
from ctc_loss import (brute_force_log_prob, collapse, ctc_forward_log, ctc_loss,
                      extend_targets, greedy_decode, run)


def test_collapse_rule():
    assert collapse([1, 1, 0, 1, 2]) == [1, 1, 2]     # the blank keeps the two 1s apart
    assert collapse([1, 1, 1, 0, 2]) == [1, 2]        # repeats squash first
    assert collapse([0, 0, 0]) == []
    assert collapse([1, 2, 1]) == [1, 2, 1]
    assert extend_targets([1, 2]) == [0, 1, 0, 2, 0]


def test_closed_forms():
    lp = torch.tensor([[0.5, 0.3, 0.2]]).log()
    assert torch.allclose(ctc_forward_log(lp, [1]), torch.tensor(-math.log(0.3)), atol=1e-6)

    lp2 = torch.tensor([[0.5, 0.3, 0.2], [0.5, 0.3, 0.2]]).log()
    # l = [1] over two frames: paths 1-, -1 and 11
    want = -math.log(0.3 * 0.5 + 0.5 * 0.3 + 0.3 * 0.3)
    assert torch.allclose(ctc_forward_log(lp2, [1]), torch.tensor(want), atol=1e-6)
    # l = [1, 1] needs a separating blank, so 2 frames cannot produce it
    assert ctc_forward_log(lp2, [1, 1]).item() > 1e20


def test_matches_brute_force_enumeration():
    torch.manual_seed(0)
    for T, C, tgt in [(4, 3, [1]), (5, 3, [1, 2]), (6, 3, [1, 1]), (5, 4, [2, 3]), (7, 3, [2])]:
        x = torch.randn(T, C).log_softmax(dim=-1)
        assert abs(-ctc_forward_log(x, tgt).item() - brute_force_log_prob(x, tgt)) < 1e-5


def test_matches_torch_ctc_loss():
    torch.manual_seed(0)
    for T, N, C, tgts in [(20, 3, 5, [[1, 2, 3], [4, 4], [2, 1, 2, 3]]),
                          (8, 2, 3, [[1, 1], [2]]),
                          (30, 1, 6, [[1, 2, 3, 4, 5, 1]])]:
        x = torch.randn(T, N, C).log_softmax(dim=-1)
        ref = torch.nn.CTCLoss(blank=0, reduction="none")(
            x,
            torch.tensor([t for s in tgts for t in s]),
            torch.full((N,), T, dtype=torch.long),
            torch.tensor([len(s) for s in tgts]),
        )
        assert torch.allclose(ctc_loss(x, tgts), ref, atol=1e-4), (T, N, C)


def test_gradient_flows():
    torch.manual_seed(0)
    x = torch.randn(10, 4, requires_grad=True)
    ctc_forward_log(x.log_softmax(-1), [1, 2]).backward()
    assert x.grad is not None and torch.isfinite(x.grad).all() and x.grad.abs().sum() > 0


def test_greedy_decode_is_not_the_most_likely_label():
    """Best-path decoding can return a label sequence that is not the most likely one.

    Frames that each favour the blank slightly can still sum to a label whose
    total probability beats the blank-only path, because the label's probability
    is a sum over many paths.
    """
    p = torch.tensor([[0.4, 0.3, 0.3]] * 3).log()
    assert greedy_decode(p) == []                       # argmax is the blank every frame
    # but the label [1] has more probability mass than the empty label
    assert ctc_forward_log(p, [1]).item() < ctc_forward_log(p, []).item()


def test_training_decreases_loss():
    out = run(seed=0)
    assert loss_decreased(out["losses"])
    assert out["decode_accuracy"] > 0.5
