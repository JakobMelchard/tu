import numpy as np
import pytest

from cloning import (bh_output, buzek_hillery, cnot_broadcast_marginals, cnot_clone_fidelity,
                     helstrom, helstrom_pure, single_copy_fidelity, symmetric_cloner, usd_povm,
                     usd_success)
from states import dm, ket, random_pure, random_state


def test_no_cloning_with_cnot():
    assert cnot_clone_fidelity(ket(1, 0)) == pytest.approx(1)
    assert cnot_clone_fidelity(ket(1, 1)) == pytest.approx(0.5)


def test_no_cloning_inner_product_argument():
    # a cloner U|x>|0> = |x>|x> preserves inner products: <a|b> = <a|b>^2 => 0 or 1
    rng = np.random.default_rng(0)
    a, b = random_pure(2, rng), random_pure(2, rng)
    c = np.vdot(a, b)
    assert abs(c - c ** 2) > 1e-3


def test_buzek_hillery_fidelity_five_sixths_universal():
    rng = np.random.default_rng(1)
    assert np.allclose(buzek_hillery().conj().T @ buzek_hillery(), np.eye(2))
    for _ in range(50):
        psi = random_pure(2, rng)
        out = bh_output(dm(psi))
        for k in (0, 1):
            assert single_copy_fidelity(out, psi, 2, k) == pytest.approx(5 / 6)
        from states import partial_trace
        red = partial_trace(out, [2, 2], [0])
        assert np.allclose(red, 2 / 3 * dm(psi) + 1 / 3 * np.eye(2) / 2)


@pytest.mark.parametrize("M", [2, 3, 4])
def test_symmetric_cloner_fidelity(M):
    psi = random_pure(2, np.random.default_rng(M))
    out = symmetric_cloner(dm(psi), M)
    assert np.trace(out).real == pytest.approx(1)
    assert single_copy_fidelity(out, psi, M) == pytest.approx((2 * M + 1) / (3 * M))


def test_broadcasting_only_for_commuting():
    d = np.diag([0.6, 0.4]).astype(complex)
    a, b = cnot_broadcast_marginals(d)
    assert np.allclose(a, d) and np.allclose(b, d)
    plus = dm(ket(1, 1))
    a, b = cnot_broadcast_marginals(plus)
    assert not np.allclose(a, plus)


def test_helstrom_pure_and_mixed():
    rng = np.random.default_rng(2)
    a, b = random_pure(2, rng), random_pure(2, rng)
    P, _ = helstrom(dm(a), dm(b), 0.3)
    assert P == pytest.approx(helstrom_pure(abs(np.vdot(a, b)), 0.3))
    r, s = random_state(3, rng), random_state(3, rng)
    P, proj = helstrom(r, s)
    assert P == pytest.approx(0.5 * (1 + 0.5 * np.abs(np.linalg.eigvalsh(r - s)).sum()))
    # no projector does better (random search)
    from states import random_unitary
    for _ in range(300):
        U = random_unitary(3, rng)
        k = int(rng.integers(0, 4))
        Q = U[:, :k] @ U[:, :k].conj().T
        val = 0.5 * np.real(np.trace(Q @ r) + np.trace((np.eye(3) - Q) @ s))
        assert val <= P + 1e-12


def test_unambiguous_discrimination():
    for t in (0.2, 0.7, 1.2):
        a, b = ket(1, 0), ket(np.cos(t), np.sin(t))
        Ea, Eb, Eq = usd_povm(a, b)
        assert min(np.linalg.eigvalsh(E).min() for E in (Ea, Eb, Eq)) > -1e-12
        succ, err = usd_success(a, b)
        assert err == pytest.approx(0, abs=1e-12)
        assert succ == pytest.approx(1 - abs(np.cos(t)))
        assert succ <= helstrom_pure(abs(np.cos(t)))
