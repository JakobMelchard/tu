from common import loss_decreased
from gan_toy import make_ring, mode_distance, modes_covered, run


def test_ring_data():
    X = make_ring(800)
    assert X.shape == (800, 2) and mode_distance(X) < 0.1 and modes_covered(X) == 8


def test_gan_moves_towards_modes():
    out = run(steps=600, n_train=2000)
    assert loss_decreased(out["losses"], frac=0.25)  # mode distance every 20 steps, first vs last quarter
    assert out["mode_distance"] < 1.0  # an untrained generator sits near the origin, ~2 from every mode
