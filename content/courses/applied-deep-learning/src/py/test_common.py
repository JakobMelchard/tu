import torch

from common import count_params, get_device, loss_decreased, moving_average, seed_all, train_loop


def test_train_loop_minimises_quadratic():
    seed_all(0)
    w = torch.nn.Parameter(torch.tensor([3.0]))
    opt = torch.optim.SGD([w], lr=0.1)
    losses = train_loop(lambda: (w - 1.0).pow(2).sum(), opt, 50)
    assert loss_decreased(losses) and abs(w.item() - 1.0) < 1e-2


def test_helpers():
    assert get_device().type in ("mps", "cpu", "cuda")
    assert count_params(torch.nn.Linear(3, 2)) == 8
    assert moving_average([1.0, 3.0, 5.0], 2) == [1.0, 2.0, 4.0]
    assert not loss_decreased([1.0, 2.0, 3.0])
