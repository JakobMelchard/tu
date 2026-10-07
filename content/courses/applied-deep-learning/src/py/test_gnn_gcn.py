import torch

from common import loss_decreased
from gnn_gcn import gcn_norm, make_sbm, run


def test_gcn_norm_path_graph():
    A = torch.tensor([[0.0, 1.0, 0.0], [1.0, 0.0, 1.0], [0.0, 1.0, 0.0]])
    A_hat = A + torch.eye(3)
    d = A_hat.sum(1)
    ref = torch.diag(d.pow(-0.5)) @ A_hat @ torch.diag(d.pow(-0.5))
    assert torch.allclose(gcn_norm(A), ref)
    A, X, y = make_sbm(n_per_block=10, blocks=2, seed=0)
    assert A.shape == (20, 20) and torch.equal(A, A.T) and A.diag().sum() == 0 and X.shape == (20, 2)


def test_gcn_beats_mlp():
    gcn = run(steps=60, model_kind="gcn")
    mlp = run(steps=60, model_kind="mlp")
    assert loss_decreased(gcn["losses"]) and loss_decreased(mlp["losses"])
    assert gcn["test_accuracy"] > mlp["test_accuracy"]
