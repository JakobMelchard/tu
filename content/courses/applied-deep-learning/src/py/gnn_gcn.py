"""Graph convolutional network (Kipf & Welling 2017) in pure torch, dense adjacency.

Graph: stochastic block model with `blocks` communities; node features are a
noisy one-hot of the community. Task: semi-supervised node classification,
only 10% of the nodes are labelled, the rest are predicted transductively.
Layer:  H' = act( D^-1/2 (A + I) D^-1/2 H W ),  D = degree matrix of A + I.
"""

from __future__ import annotations

import torch
from torch import nn
from torch.nn import functional as F

from common import Timer, count_params, get_device, loss_decreased, seed_all, train_loop


def make_sbm(n_per_block: int = 40, blocks: int = 3, p_in: float = 0.3, p_out: float = 0.02, seed: int = 0,
             feature_noise: float = 1.0) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
    """Return adjacency A [N,N] (symmetric 0/1, no self loops), features X [N,blocks], labels y [N]."""
    gen = torch.Generator().manual_seed(seed)
    N = n_per_block * blocks
    y = torch.arange(blocks).repeat_interleave(n_per_block)
    same = y[:, None] == y[None, :]
    prob = torch.where(same, torch.tensor(p_in), torch.tensor(p_out))
    upper = torch.triu(torch.rand(N, N, generator=gen) < prob, diagonal=1)
    A = (upper | upper.T).float()
    X = F.one_hot(y, blocks).float() + feature_noise * torch.randn(N, blocks, generator=gen)  # weak per-node signal
    return A, X, y


def gcn_norm(A: torch.Tensor) -> torch.Tensor:
    """D^-1/2 (A + I) D^-1/2 with D the degree matrix of A + I."""
    A_hat = A + torch.eye(A.shape[0], device=A.device)
    d_inv_sqrt = A_hat.sum(1).pow(-0.5)
    return d_inv_sqrt[:, None] * A_hat * d_inv_sqrt[None, :]


class GCN(nn.Module):
    def __init__(self, in_dim: int, hidden: int, out_dim: int, layers: int = 2, dropout: float = 0.3):
        super().__init__()
        dims = [in_dim] + [hidden] * (layers - 1) + [out_dim]
        self.lins = nn.ModuleList(nn.Linear(a, b) for a, b in zip(dims[:-1], dims[1:]))
        self.dropout = dropout

    def forward(self, X: torch.Tensor, A_norm: torch.Tensor) -> torch.Tensor:
        h = X
        for i, lin in enumerate(self.lins):
            h = A_norm @ lin(h)  # aggregate neighbours after the linear map (same as lin(A_norm @ h))
            if i < len(self.lins) - 1:
                h = F.dropout(F.relu(h), self.dropout, self.training)
        return h  # logits [N, out_dim]


class MLP(nn.Module):
    """Same layers without the graph: baseline showing what the edges contribute."""

    def __init__(self, in_dim: int, hidden: int, out_dim: int):
        super().__init__()
        self.net = nn.Sequential(nn.Linear(in_dim, hidden), nn.ReLU(), nn.Linear(hidden, out_dim))

    def forward(self, X: torch.Tensor, A_norm: torch.Tensor) -> torch.Tensor:
        return self.net(X)


@torch.no_grad()
def accuracy(model: nn.Module, X: torch.Tensor, A_norm: torch.Tensor, y: torch.Tensor, mask: torch.Tensor) -> float:
    model.eval()
    acc = (model(X, A_norm).argmax(1)[mask] == y[mask]).float().mean().item()
    model.train()
    return acc


def run(steps: int = 200, model_kind: str = "gcn", label_frac: float = 0.1, hidden: int = 16,
        device: torch.device | None = None, seed: int = 0, log_every: int = 0, **sbm_kw) -> dict:
    device = device or get_device()
    seed_all(seed)
    A, X, y = make_sbm(seed=seed, **sbm_kw)
    A, X, y = A.to(device), X.to(device), y.to(device)
    A_norm = gcn_norm(A)
    N, C = X.shape[0], int(y.max().item()) + 1
    perm = torch.randperm(N, generator=torch.Generator().manual_seed(seed)).to(device)
    train_mask = torch.zeros(N, dtype=torch.bool, device=device)
    train_mask[perm[: int(label_frac * N)]] = True
    model = (GCN(C, hidden, C) if model_kind == "gcn" else MLP(C, hidden, C)).to(device)
    opt = torch.optim.Adam(model.parameters(), lr=1e-2, weight_decay=5e-4)

    def step_fn() -> torch.Tensor:  # full-batch: the whole graph is one training example
        return F.cross_entropy(model(X, A_norm)[train_mask], y[train_mask])

    with Timer() as t:
        losses = train_loop(step_fn, opt, steps, log_every=log_every)
    return {"losses": losses, "test_accuracy": accuracy(model, X, A_norm, y, ~train_mask),
            "train_accuracy": accuracy(model, X, A_norm, y, train_mask), "model": model, "seconds": t.seconds}


if __name__ == "__main__":
    A = torch.tensor([[0., 1., 0.], [1., 0., 1.], [0., 1., 0.]])  # path graph 0-1-2
    print("gcn_norm of the 3-node path graph:\n", gcn_norm(A))
    A, X, y = make_sbm()
    print(f"SBM: {X.shape[0]} nodes, {int(A.sum().item()) // 2} edges, mean degree {A.sum(1).mean():.1f}")
    for kind in ("mlp", "gcn"):
        out = run(model_kind=kind, log_every=100)
        print(f"{kind}: params {count_params(out['model'])}, train acc {out['train_accuracy']:.2f}, "
              f"test acc {out['test_accuracy']:.3f} (90% unlabelled nodes), {out['seconds']:.1f}s, "
              f"loss decreased {loss_decreased(out['losses'])}")
