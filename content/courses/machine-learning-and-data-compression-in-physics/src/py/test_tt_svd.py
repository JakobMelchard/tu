import numpy as np
import pytest

from tt_svd import (entanglement_entropy, error_vs_bond_dimension, ghz, quantics, random_state,
                    schmidt_values, tfim_ground_state, tt_num_params, tt_ranks, tt_svd, tt_to_full)


def test_full_rank_is_exact_and_cores_are_left_orthogonal():
    rng = np.random.default_rng(0)
    T = rng.standard_normal((3, 4, 5, 2))
    cores, disc = tt_svd(T)
    assert np.allclose(tt_to_full(cores), T)
    assert np.allclose(disc, 0)
    for G in cores[:-1]:
        M = G.reshape(-1, G.shape[2])
        assert np.allclose(M.T @ M, np.eye(G.shape[2]))


def test_product_and_ghz_ranks_and_entropy():
    rng = np.random.default_rng(1)
    vs = [v / np.linalg.norm(v) for v in rng.standard_normal((6, 2))]
    prod = vs[0]
    for v in vs[1:]:
        prod = np.multiply.outer(prod, v)
    assert tt_ranks(tt_svd(prod, rel_eps=1e-12)[0]) == [1] * 5
    g = ghz(6)
    assert tt_ranks(tt_svd(g, rel_eps=1e-12)[0]) == [2] * 5
    assert entanglement_entropy(g, 3) == pytest.approx(np.log(2))


@pytest.mark.parametrize("chi", [1, 2, 3, 5])
def test_error_equals_root_sum_of_discarded_weights(chi):
    rng = np.random.default_rng(2)
    T = rng.standard_normal((3, 3, 3, 3, 3))
    cores, disc = tt_svd(T, max_rank=chi)
    err = np.linalg.norm(tt_to_full(cores) - T)
    assert err == pytest.approx(np.sqrt(np.sum(disc ** 2)), rel=1e-10)
    # a single cut's Schmidt tail is a lower bound (Eckart-Young at that cut)
    for k in range(1, 5):
        s = schmidt_values(T, k)
        assert err >= np.sqrt(np.sum(s[chi:] ** 2)) - 1e-12


@pytest.mark.parametrize("eps", [1e-1, 1e-3, 1e-8])
def test_rel_eps_guarantee(eps):
    psi = tfim_ground_state(10, 1.0)
    cores, _ = tt_svd(psi, rel_eps=eps)
    assert np.linalg.norm(tt_to_full(cores) - psi) <= eps * np.linalg.norm(psi) + 1e-14


def test_tfim_ground_state_energy_matches_exact_diagonalisation():
    # paramagnetic side (g = 2): unique ground state, dense ED as the reference
    n, g = 6, 2.0
    psi = tfim_ground_state(n, g).ravel()
    X = np.array([[0, 1], [1, 0.]]); Z = np.diag([1., -1]); I = np.eye(2)

    def op(o, i):
        out = np.array([[1.0]])
        for j in range(n):
            out = np.kron(out, o if j == i else I)
        return out
    H = -sum(op(Z, i) @ op(Z, i + 1) for i in range(n - 1)) - g * sum(op(X, i) for i in range(n))
    assert psi @ H @ psi == pytest.approx(np.linalg.eigvalsh(H)[0], abs=1e-9)


def test_area_law_state_compresses_random_state_does_not():
    n = 10
    rows_gs = error_vs_bond_dimension(tfim_ground_state(n, 1.0), [4, 8])
    rows_rd = error_vs_bond_dimension(random_state(n, np.random.default_rng(3)), [4, 8])
    assert rows_gs[0][1] < 1e-2 and rows_gs[1][1] < 1e-4
    assert rows_rd[0][1] > 0.8 and rows_rd[1][1] > 0.5
    assert rows_gs[1][2] < 2 ** n


def test_quantics_ranks_of_elementary_functions():
    R = 14
    r_exp = tt_ranks(tt_svd(quantics(lambda x: np.exp(-3 * x), R), rel_eps=1e-12)[0])
    r_sin = tt_ranks(tt_svd(quantics(lambda x: np.sin(7.3 * x + 0.2), R), rel_eps=1e-12)[0])
    r_pol = tt_ranks(tt_svd(quantics(lambda x: 1 + x - 2 * x ** 2 + x ** 3, R), rel_eps=1e-12)[0])
    assert max(r_exp) == 1
    assert max(r_sin) == 2
    assert max(r_pol) <= 4
    cores, _ = tt_svd(quantics(lambda x: np.sin(7.3 * x + 0.2), R), rel_eps=1e-12)
    assert tt_num_params(cores) < 2 ** R / 50
