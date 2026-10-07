import numpy as np
import pytest

from schmidt import (canonical_purification, purification_unitary, purify, reconstruct, schmidt,
                     schmidt_rank)
from states import BELL, dm, partial_trace, random_pure, random_state


@pytest.mark.parametrize("da,db", [(2, 2), (2, 3), (3, 4)])
def test_schmidt_reconstructs_and_matches_reduced_spectra(da, db):
    rng = np.random.default_rng(da * 10 + db)
    psi = random_pure(da * db, rng)
    c, A, B = schmidt(psi, da, db)
    assert np.allclose(reconstruct(c, A, B), psi)
    assert np.allclose(A.conj().T @ A, np.eye(len(c))) and np.allclose(B.conj().T @ B, np.eye(len(c)))
    r = dm(psi)
    for keep, dd in ((0, da), (1, db)):
        ev = np.sort(np.linalg.eigvalsh(partial_trace(r, [da, db], [keep])))[::-1][:len(c)]
        assert np.allclose(ev, c ** 2)
    assert np.allclose(c, np.linalg.svd(psi.reshape(da, db), compute_uv=False)[:len(c)])


def test_schmidt_rank_product_vs_bell():
    assert schmidt_rank(np.kron(random_pure(2, np.random.default_rng(0)),
                                random_pure(3, np.random.default_rng(1))), 2, 3) == 1
    assert schmidt_rank(BELL["phi+"], 2, 2) == 2
    c, _, _ = schmidt(BELL["psi-"], 2, 2)
    assert np.allclose(c, [1 / np.sqrt(2)] * 2)


def test_purifications_reduce_to_rho_and_are_unitarily_related():
    rng = np.random.default_rng(2)
    for rank in (1, 2, 3):
        rho = random_state(3, rng, rank=rank)
        P, Q = purify(rho), canonical_purification(rho)
        for v in (P, Q):
            assert np.allclose(partial_trace(dm(v), [3, 3], [0]), rho)
        U = purification_unitary(P, Q, 3, 3)
        assert np.allclose(U @ U.conj().T, np.eye(3))
        assert np.allclose(np.kron(np.eye(3), U) @ P, Q)
