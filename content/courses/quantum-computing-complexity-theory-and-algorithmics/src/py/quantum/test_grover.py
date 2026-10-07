import numpy as np

from grover import (amplitude_amplification, apply_oracle, grover, optimal_iterations,
                    success_probability)


def test_single_and_multiple_marked_items_high_probability():
    rng = np.random.default_rng(0)
    for n in (4, 5, 6):
        for marked in ([3], [1, 2 ** n - 1], [0, 5, 6]):
            p, out, _ = grover(n, marked, rng=rng)
            assert p > 0.9, (n, marked, p)
            assert out in marked


def test_analytic_formula_matches_simulation():
    for n in (4, 5, 6):
        for marked in ([7], [2, 9], [1, 3, 5, 11]):
            for k in range(0, optimal_iterations(n, len(marked)) + 3):
                p, _, _ = grover(n, marked, iterations=k)
                assert abs(p - success_probability(n, marked, k)) < 1e-9


def test_more_iterations_overshoot():
    n, marked = 6, [17]
    k = optimal_iterations(n, 1)
    p_opt = grover(n, marked, iterations=k)[0]
    p_more = grover(n, marked, iterations=k + 3)[0]
    assert p_more < p_opt
    assert grover(n, marked, iterations=2 * k + 1)[0] < 0.2   # rotated well past |good>


def test_optimal_iteration_count():
    assert optimal_iterations(2, 1) == 1          # N=4, one query is exact
    assert grover(2, [2], iterations=1)[0] > 1 - 1e-12
    assert optimal_iterations(10, 1) == round(np.pi / 4 * np.sqrt(1024) - 0.5)


def test_amplitude_amplification_reduces_to_grover():
    n, marked = 5, [4, 20]
    k = optimal_iterations(n, len(marked))

    def hadamards(reg):
        for q in range(n):
            reg.h(q)

    reg = amplitude_amplification(n, hadamards, hadamards,
                                  lambda r: apply_oracle(r, marked, list(range(n))), k)
    p_ref, _, ref = grover(n, marked, iterations=k)
    assert np.isclose(reg.probabilities()[marked].sum(), p_ref)
    assert np.allclose(np.abs(reg.state), np.abs(ref.state))
