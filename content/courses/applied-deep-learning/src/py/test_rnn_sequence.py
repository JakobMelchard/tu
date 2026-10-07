import torch

from common import loss_decreased
from rnn_sequence import SeqModel, grad_norm_through_time, make_adding, run


def test_adding_data():
    X, y = make_adding(20, T=10, seed=2)
    assert X.shape == (20, 10, 2) and (X[..., 1].sum(1) == 2).all()
    assert torch.allclose((X[..., 0] * X[..., 1]).sum(1), y)


def test_lstm_learns_and_rnn_gradient_vanishes():
    out = run(steps=150, cell="lstm", n_train=1000)
    assert loss_decreased(out["losses"])
    X, y = make_adding(32, T=60, seed=3)
    rnn = grad_norm_through_time(SeqModel("rnn"), X, y)
    lstm = grad_norm_through_time(SeqModel("lstm"), X, y)
    assert rnn[0] / rnn[-1] < lstm[0] / lstm[-1]  # gating keeps more gradient at early steps
