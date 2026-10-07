"""Recurrent networks on the adding problem (Hochreiter & Schmidhuber 1997).

Input: sequence of T steps with two channels (a value in [0,1], a marker that is
1 at exactly two positions). Target: the sum of the two marked values, a
many-to-one regression that needs the network to remember values across
time. The recurrence is unrolled explicitly with `nn.RNNCell` / `nn.GRUCell` /
`nn.LSTMCell` so that every hidden state h_t is a node of the autograd graph;
`grad_norm_through_time` then shows how ||dL/dh_t|| vanishes with T - t for the
plain tanh RNN but not for the gated cells.
"""

from __future__ import annotations

import torch
from torch import nn
from torch.nn import functional as F

from common import Timer, count_params, get_device, loss_decreased, seed_all, train_loop


def make_adding(n: int, T: int = 12, seed: int = 0) -> tuple[torch.Tensor, torch.Tensor]:
    """Return X [n, T, 2] and y [n]; y = sum of the values at the two marked positions."""
    gen = torch.Generator().manual_seed(seed)
    values = torch.rand(n, T, generator=gen)
    markers = torch.zeros(n, T)
    first = torch.randint(0, T // 2, (n,), generator=gen)  # one marker in the first half
    second = torch.randint(T // 2, T, (n,), generator=gen)  # one in the second half
    rows = torch.arange(n)
    markers[rows, first] = 1.0
    markers[rows, second] = 1.0
    X = torch.stack([values, markers], dim=-1)  # batch_first layout [B, T, F]
    y = values[rows, first] + values[rows, second]
    return X, y


class SeqModel(nn.Module):
    """Many-to-one: unroll a recurrent cell over T steps, regress from the last hidden state."""

    def __init__(self, cell: str = "lstm", n_features: int = 2, hidden: int = 32):
        super().__init__()
        self.kind, self.hidden = cell, hidden
        cls = {"lstm": nn.LSTMCell, "gru": nn.GRUCell, "rnn": nn.RNNCell}[cell]
        self.cell = cls(n_features, hidden)
        if cell == "lstm":  # forget-gate bias 1 (Jozefowicz et al. 2015): start by remembering
            with torch.no_grad():
                self.cell.bias_ih[hidden : 2 * hidden].fill_(1.0)
        self.head = nn.Linear(hidden, 1)

    def forward(self, x: torch.Tensor, return_states: bool = False):
        B, T, _ = x.shape
        h = x.new_zeros(B, self.hidden)
        c = x.new_zeros(B, self.hidden)  # LSTM cell state (unused by RNN/GRU)
        states = []
        for t in range(T):  # explicit unrolling = the computational graph BPTT differentiates
            if self.kind == "lstm":
                h, c = self.cell(x[:, t], (h, c))
            else:
                h = self.cell(x[:, t], h)
            states.append(h)
        pred = self.head(h).squeeze(-1)
        return (pred, states) if return_states else pred


def grad_norm_through_time(model: SeqModel, X: torch.Tensor, y: torch.Tensor) -> list[float]:
    """||dL/dh_t|| for each t: how strongly the final loss depends on each hidden state.

    Decays geometrically in T - t for a plain tanh RNN (product of Jacobians
    with spectral norm < 1); stays roughly flat for LSTM/GRU because their
    state update is additive.
    """
    pred, states = model(X, return_states=True)
    for h in states:
        h.retain_grad()
    F.mse_loss(pred, y).backward()
    return [h.grad.norm(dim=-1).mean().item() for h in states]


def run(steps: int = 400, cell: str = "lstm", T: int = 12, hidden: int = 32, batch: int = 64, n_train: int = 4000,
        device: torch.device | None = None, seed: int = 0, log_every: int = 0) -> dict:
    # A T-step python loop of tiny matmuls is launch-bound on MPS; CPU is faster here unless hidden is large.
    device = device or torch.device("cpu")
    gen = seed_all(seed)
    X, y = make_adding(n_train, T, seed)
    Xt, yt = make_adding(500, T, seed + 1)
    X, y = X.to(device), y.to(device)
    model = SeqModel(cell, hidden=hidden).to(device)
    opt = torch.optim.Adam(model.parameters(), lr=5e-3)

    def step_fn() -> torch.Tensor:
        idx = torch.randint(0, n_train, (batch,), generator=gen).to(device)
        return F.mse_loss(model(X[idx]), y[idx])

    with Timer() as t:
        losses = train_loop(step_fn, opt, steps, log_every=log_every, clip_grad=1.0)
    model.eval()
    with torch.no_grad():
        mae = (model(Xt.to(device)) - yt.to(device)).abs().mean().item()
    return {"losses": losses, "mae": mae, "model": model, "seconds": t.seconds}


if __name__ == "__main__":
    # Vanishing gradient at initialisation: untrained cells, long sequence, ratio of first to last gradient norm.
    X, y = make_adding(64, 60, seed=3)
    for cell in ("rnn", "gru", "lstm"):
        norms = grad_norm_through_time(SeqModel(cell), X, y)
        print(f"untrained {cell:4s}, T=60: ||dL/dh_0|| / ||dL/dh_59|| = {norms[0] / norms[-1]:.1e}")
    T = 12
    for cell in ("rnn", "gru", "lstm"):
        out = run(cell=cell, T=T, steps=800, log_every=200)
        m = out["model"].cpu()
        X, y = make_adding(64, T, seed=3)
        norms = grad_norm_through_time(m, X, y)
        print(f"{cell:4s}: params {count_params(m)}, test MAE {out['mae']:.3f} (predicting the mean gives ~0.33), "
              f"{out['seconds']:.1f}s, loss decreased {loss_decreased(out['losses'])}")
        print(f"      ||dL/dh_t|| for t=0..{T - 1}:", " ".join(f"{v:.1e}" for v in norms))
