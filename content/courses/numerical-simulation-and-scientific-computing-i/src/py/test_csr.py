"""CSR storage and the iterative solvers of csr.py, cross-checked against scipy.sparse.

Iteration counts Jacobi > Gauss-Seidel > SOR and CG < Gauss-Seidel follow the
splitting theory of [S22 ch. 4]; CG itself [S15].
"""
import numpy as np
import scipy.sparse as sp
import scipy.sparse.linalg as spla

from csr import CSR, cg, jacobi, sor
from fd_poisson import poisson2d_matrix


def test_csr_roundtrip_and_matvec():
    rng = np.random.default_rng(0)
    A = rng.random((20, 20)) * (rng.random((20, 20)) < 0.3)
    S = CSR.from_dense(A)
    x = rng.random(20)
    assert np.allclose(S.matvec(x), A @ x)
    assert np.allclose(S.to_dense(), A)
    assert np.allclose(S.diag(), np.diag(A))


def test_poisson2d_matches_scipy_assembly():
    N = 10
    A = CSR.poisson2d(N)
    B = poisson2d_matrix(N)
    assert np.allclose(A.to_dense(), B.toarray())
    C = sp.csr_matrix(A.to_dense())
    assert np.array_equal(C.indptr, A.row_ptr) and np.array_equal(C.indices, A.col)


def test_solvers_agree_with_scipy():
    N = 12
    A = CSR.poisson2d(N)
    rng = np.random.default_rng(1)
    b = rng.random(A.n)
    ref = spla.spsolve(sp.csr_matrix(A.to_dense()), b)
    omega = 2 / (1 + np.sin(np.pi / N))
    its = {}
    for name, solver in [("jacobi", jacobi), ("gs", lambda A, b: sor(A, b, 1.0)),
                         ("sor", lambda A, b: sor(A, b, omega)), ("cg", cg)]:
        x, its[name] = solver(A, b)
        assert np.allclose(x, ref, atol=1e-6), name
    assert its["jacobi"] > its["gs"] > its["sor"] and its["cg"] < its["gs"]
    x_pcg, it_pcg = cg(A, b, precond=lambda r: r / A.diag())
    assert np.allclose(x_pcg, ref, atol=1e-6) and it_pcg <= its["cg"] + 1
