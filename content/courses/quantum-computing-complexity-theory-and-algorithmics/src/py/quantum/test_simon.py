import numpy as np

from simon import random_two_to_one_function, simon, simon_sample


def test_two_to_one_table_has_period_s():
    rng = np.random.default_rng(0)
    for n, s in ((3, 5), (4, 9)):
        t = random_two_to_one_function(n, s, rng)
        assert all(t[x] == t[x ^ s] for x in range(2 ** n))
        assert len(set(t.tolist())) == 2 ** (n - 1)


def test_samples_are_orthogonal_to_s():
    rng = np.random.default_rng(1)
    n, s = 4, 0b0110
    t = random_two_to_one_function(n, s, rng)
    sb = np.array([int(b) for b in f"{s:0{n}b}"])
    ys = [simon_sample(t, n, rng) for _ in range(20)]
    assert all(int(y @ sb) % 2 == 0 for y in ys)
    assert any(y.any() for y in ys)                 # not just the zero vector


def test_recovers_s_in_at_least_95_percent_of_trials():
    rng = np.random.default_rng(2)
    for n in (3, 4, 5):
        ok = total = 0
        for _ in range(12):
            s = int(rng.integers(1, 2 ** n))
            t = random_two_to_one_function(n, s, rng)
            total += 1
            ok += simon(t, n, rng, max_samples=4 * n) == s
        assert ok / total >= 0.95, (n, ok, total)
