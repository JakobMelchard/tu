"""Connectionist temporal classification: the forward algorithm, from scratch.

CTC [S48] trains a sequence model on *unaligned* pairs: an audio clip and its
transcription, a line image and its text, a score image and its notes -- cases
where you know what was said but not when.  Lecture 4 [S4] gives it a chapter,
and it is the loss behind the lecturer's own optical-music-recognition work [S9].

The idea.  The network emits, per frame ``t``, a distribution over the alphabet
plus one extra symbol, the **blank**.  A *path* is one symbol per frame.  A path
is collapsed to a label sequence by the rule

    collapse: delete repeated symbols, then delete blanks

so ``a a - a b`` collapses to ``a a b`` (the blank separates the two ``a``s) while
``a a a - b`` collapses to ``a b``.  CTC defines

    p(l | x) = sum over all paths pi that collapse to l of prod_t y_t(pi_t)

and minimises ``-log p(l | x)``.  The sum has up to ``C^T`` terms, so it is
computed by dynamic programming over the *extended* label

    l' = [blank, l_1, blank, l_2, ..., l_L, blank]      (length 2L + 1)

whose states are the positions a path can occupy at time ``t``.  With
``alpha_t(s) = `` total probability of all prefixes of length ``t`` ending in
state ``s``:

    alpha_1(1) = y_1(blank),  alpha_1(2) = y_1(l_1),  alpha_1(s > 2) = 0

    alpha_t(s) = y_t(l'_s) * [ alpha_{t-1}(s) + alpha_{t-1}(s-1) + skip * alpha_{t-1}(s-2) ]

where ``skip = 1`` only if ``l'_s`` is not a blank and ``l'_s != l'_{s-2}``: you
may jump over a blank, but not over the blank that separates two identical
labels, because deleting it would merge them.  Finally

    p(l | x) = alpha_T(2L+1) + alpha_T(2L)

(the path may end on the final blank or on the last real label).

Everything is done in log space with ``logsumexp``; in probability space the
products underflow within a few dozen frames.

Conventions, stated because they differ between implementations: ``log_probs``
is ``[T, N, C]`` (time-major, as ``torch.nn.CTCLoss`` wants), class ``0`` is the
blank, and the returned value is the per-sequence negative log-likelihood in
nats with no length normalisation.

Verified three ways in ``test_ctc_loss.py``: against ``torch.nn.CTCLoss`` [S96],
against brute-force enumeration of every path for small ``T``, and against the
closed forms below.

Run: ``python ctc_loss.py``.
"""

from __future__ import annotations

import itertools
import math

import torch

NEG_INF = -1e30


def extend_targets(targets: list[int], blank: int = 0) -> list[int]:
    """``l -> [blank, l_1, blank, ..., l_L, blank]``, the 2L+1 CTC states."""
    out = [blank]
    for t in targets:
        out += [t, blank]
    return out


def ctc_forward_log(log_probs: torch.Tensor, targets: list[int], blank: int = 0) -> torch.Tensor:
    """``-log p(targets | log_probs)`` for one sequence.

    ``log_probs`` is ``[T, C]``, already log-normalised over ``C``.
    Returns a 0-d tensor; differentiable w.r.t. ``log_probs``.
    """
    T, _ = log_probs.shape
    ext = extend_targets(targets, blank)
    S = len(ext)
    if T < len(targets) + sum(1 for i in range(1, len(targets)) if targets[i] == targets[i - 1]):
        # fewer frames than the shortest path that can produce the label
        return torch.full((), -NEG_INF, dtype=log_probs.dtype)

    alpha = log_probs.new_full((S,), NEG_INF)
    alpha[0] = log_probs[0, ext[0]]
    if S > 1:
        alpha[1] = log_probs[0, ext[1]]

    for t in range(1, T):
        prev = alpha
        # stay in s, or come from s-1
        shift1 = torch.cat([prev.new_full((1,), NEG_INF), prev[: S - 1]])
        # come from s-2, only where the skip is legal
        shift2 = torch.cat([prev.new_full((min(2, S),), NEG_INF), prev[: max(S - 2, 0)]])
        skip_ok = torch.tensor(
            [False, False][:S] + [ext[s] != blank and ext[s] != ext[s - 2] for s in range(2, S)],
            dtype=torch.bool, device=prev.device,
        )
        shift2 = torch.where(skip_ok, shift2, prev.new_full((S,), NEG_INF))

        total = torch.logsumexp(torch.stack([prev, shift1, shift2]), dim=0)
        alpha = total + log_probs[t, torch.tensor(ext, device=prev.device)]

    ends = alpha[-1:] if S == 1 else alpha[-2:]
    return -torch.logsumexp(ends, dim=0)


def ctc_loss(log_probs: torch.Tensor, targets: list[list[int]], blank: int = 0) -> torch.Tensor:
    """Batched wrapper.  ``log_probs`` is ``[T, N, C]``; returns ``[N]``."""
    return torch.stack([ctc_forward_log(log_probs[:, n], targets[n], blank)
                        for n in range(log_probs.shape[1])])


# --- the collapse rule, and brute force, for checking ----------------------


def collapse(path: list[int], blank: int = 0) -> list[int]:
    """CTC's many-to-one map: squash repeats, then drop blanks."""
    out: list[int] = []
    for i, c in enumerate(path):
        if i > 0 and c == path[i - 1]:
            continue
        out.append(c)
    return [c for c in out if c != blank]


def brute_force_log_prob(log_probs: torch.Tensor, targets: list[int], blank: int = 0) -> float:
    """Enumerate every path of length T and sum the ones that collapse to ``targets``.

    Exponential in ``T``; only for validating the dynamic program.
    """
    T, C = log_probs.shape
    total = NEG_INF
    for path in itertools.product(range(C), repeat=T):
        if collapse(list(path), blank) == targets:
            lp = sum(log_probs[t, c].item() for t, c in enumerate(path))
            total = lp if total == NEG_INF else max(total, lp) + math.log1p(math.exp(-abs(total - lp)))
    return total


def greedy_decode(log_probs: torch.Tensor, blank: int = 0) -> list[int]:
    """Best-path decoding: argmax per frame, then collapse.

    Cheap and standard, but it is *not* the most likely label sequence -- the
    label's probability is a sum over paths and the single best path can collapse
    to something else.  Beam search with a prefix-merging step fixes that.
    """
    return collapse(log_probs.argmax(dim=-1).tolist(), blank)


def run(seed: int = 0, device=None) -> dict:
    """Train a tiny frame classifier with the from-scratch CTC loss.

    The task: three-frame-per-symbol noisy observations of short label
    sequences; the model must learn both the symbols and where to emit blanks,
    with no alignment supervision.
    """
    import torch.nn as nn

    torch.manual_seed(seed)
    device = device or torch.device("cpu")
    C, F, T, N = 4, 6, 12, 32           # blank + 3 symbols, 6 input features
    embed = torch.randn(C - 1, F) * 2.0

    seqs = [[1, 2], [2, 3], [1, 1], [3, 1, 2], [2, 2, 3], [1, 3]]
    xs, tgts = [], []
    for n in range(N):
        lab = seqs[n % len(seqs)]
        frames, per = [], T // len(lab)
        for i, c in enumerate(lab):
            k = per if i < len(lab) - 1 else T - per * (len(lab) - 1)
            frames += [embed[c - 1] + torch.randn(F) * 0.5 for _ in range(k)]
        xs.append(torch.stack(frames))
        tgts.append(lab)
    X = torch.stack(xs, dim=1).to(device)          # [T, N, F]

    model = nn.Sequential(nn.Linear(F, 32), nn.ReLU(), nn.Linear(32, C)).to(device)
    opt = torch.optim.Adam(model.parameters(), lr=5e-2)

    losses = []
    for _ in range(300):
        opt.zero_grad()
        lp = model(X).log_softmax(dim=-1)
        loss = ctc_loss(lp, tgts).mean()
        loss.backward()
        opt.step()
        losses.append(loss.item())

    with torch.no_grad():
        lp = model(X).log_softmax(dim=-1)
        correct = sum(greedy_decode(lp[:, n]) == tgts[n] for n in range(N))
    return {"losses": losses, "decode_accuracy": correct / N}


if __name__ == "__main__":
    torch.manual_seed(0)

    print("The collapse rule:")
    for path in ([1, 1, 0, 1, 2], [1, 1, 1, 0, 2], [0, 1, 0, 0, 2, 2]):
        print(f"  {path} -> {collapse(path)}")

    print("\nClosed forms the dynamic program must reproduce:")
    lp = torch.tensor([[0.5, 0.3, 0.2]]).log()                       # T = 1
    print(f"  T=1, l=[1]:  -log p = {ctc_forward_log(lp, [1]):.6f}  (exactly -log 0.3 = {-math.log(0.3):.6f})")
    lp2 = torch.tensor([[0.5, 0.3, 0.2], [0.5, 0.3, 0.2]]).log()     # T = 2, l = [1, 1]
    impossible = ctc_forward_log(lp2, [1, 1]).item()
    print(f"  T=2, l=[1,1]: -log p = {'+inf' if impossible > 1e29 else f'{impossible:.6f}'}  "
          f"(needs a blank between the two 1s, so 3 frames minimum)")
    print(f"  T=2, l=[1]:  -log p = {ctc_forward_log(lp2, [1]):.6f}  "
          f"(paths 1-,-1,11: 0.3*0.5+0.5*0.3+0.3*0.3 = {0.3*0.5+0.5*0.3+0.3*0.3:.4f}, "
          f"-log = {-math.log(0.3*0.5+0.5*0.3+0.3*0.3):.6f})")

    print("\nAgainst brute-force enumeration of all C^T paths:")
    for T, C, tgt in [(4, 3, [1]), (5, 3, [1, 2]), (6, 3, [1, 1]), (5, 4, [2, 3])]:
        x = torch.randn(T, C).log_softmax(dim=-1)
        dp = -ctc_forward_log(x, tgt).item()
        bf = brute_force_log_prob(x, tgt)
        print(f"  T={T} C={C} l={tgt}: dp {dp:.8f}  brute force {bf:.8f}  diff {abs(dp - bf):.2e}")

    print("\nAgainst torch.nn.CTCLoss:")
    T, N, C = 20, 3, 5
    x = torch.randn(T, N, C).log_softmax(dim=-1)
    tgts = [[1, 2, 3], [4, 4], [2, 1, 2, 3]]
    ref = torch.nn.CTCLoss(blank=0, reduction="none", zero_infinity=False)(
        x, torch.tensor([t for s in tgts for t in s]),
        torch.full((N,), T, dtype=torch.long),
        torch.tensor([len(s) for s in tgts]),
    )
    mine = ctc_loss(x, tgts)
    for n in range(N):
        print(f"  seq {n} l={tgts[n]}: ours {mine[n]:.8f}  torch {ref[n]:.8f}  diff {abs(mine[n] - ref[n]):.2e}")

    print("\nTraining a frame classifier with no alignment labels:")
    res = run()
    print(f"  loss {res['losses'][0]:.3f} -> {res['losses'][-1]:.3f}, "
          f"greedy decode exact-match {res['decode_accuracy']:.0%}")
