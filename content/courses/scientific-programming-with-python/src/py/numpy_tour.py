"""NumPy tour (note 02).

ndarray memory layout, dtypes, strides, views vs copies, broadcasting,
fancy indexing, vectorisation, ufuncs, einsum, linalg, the Generator API and
performance pitfalls.  Pure-Python reference versions sit next to the numpy
call so the tests can compare them.
"""
from __future__ import annotations

import numpy as np
from numpy.lib.stride_tricks import as_strided, sliding_window_view


# ---------------------------------------------------------------- memory layout
def describe(a: np.ndarray) -> dict:
    """The facts that determine how a[i, j] is found in memory:
    address = base + sum_k i_k * strides[k]   (strides in BYTES)."""
    return {
        "shape": a.shape, "dtype": str(a.dtype), "itemsize": a.itemsize,
        "strides": a.strides, "c_contiguous": a.flags.c_contiguous,
        "f_contiguous": a.flags.f_contiguous, "owns_data": a.flags.owndata,
        "nbytes": a.nbytes,
    }


def c_strides(shape: tuple[int, ...], itemsize: int) -> tuple[int, ...]:
    """Row-major strides: last axis has stride itemsize, each earlier axis is
    the product of the later extents.  Matches np.empty(shape).strides."""
    strides, acc = [], itemsize
    for n in reversed(shape):
        strides.append(acc)
        acc *= n
    return tuple(reversed(strides))


def shares_memory(a: np.ndarray, b: np.ndarray) -> bool:
    """True when b is a view into a's buffer (or vice versa)."""
    return np.shares_memory(a, b)


def view_vs_copy_demo() -> dict:
    """Basic slicing -> view (writes propagate); fancy indexing, boolean
    masks and most arithmetic -> copy.  reshape is a view only if the
    strides allow it; .T on a C array is an F-ordered view."""
    a = np.arange(12).reshape(3, 4)
    sl = a[:, 1:3]            # view
    fancy = a[[0, 2]]         # copy
    mask = a[a % 2 == 0]      # copy
    t = a.T                   # view with swapped strides
    sl[0, 0] = 100            # visible in a
    return {
        "slice_is_view": np.shares_memory(a, sl),
        "fancy_is_view": np.shares_memory(a, fancy),
        "mask_is_view": np.shares_memory(a, mask),
        "T_is_view": np.shares_memory(a, t),
        "a01_after_write": int(a[0, 1]),
        "T_strides": t.strides, "a_strides": a.strides,
    }


def transpose_reshape_needs_copy() -> bool:
    """a.T.reshape(-1) cannot be expressed with a single stride per axis, so
    numpy silently copies; a.T.ravel() likewise.  view() would raise."""
    a = np.arange(6).reshape(2, 3)
    flat = a.T.reshape(-1)
    return not np.shares_memory(a, flat)


def moving_average_strided(x: np.ndarray, w: int) -> np.ndarray:
    """Overlapping windows without copying: a (n-w+1, w) view whose two
    strides are both itemsize.  sliding_window_view is the safe wrapper
    around as_strided."""
    windows = sliding_window_view(x, w)
    assert np.shares_memory(x, windows)
    return windows.mean(axis=1)


def as_strided_windows(x: np.ndarray, w: int) -> np.ndarray:
    """The raw version: wrong shape/strides here read garbage or segfault."""
    n = x.shape[0] - w + 1
    s = x.strides[0]
    return as_strided(x, shape=(n, w), strides=(s, s), writeable=False)


# ---------------------------------------------------------------- dtypes
def dtype_pitfalls() -> dict:
    """Integer overflow wraps silently; float32 has ~7 digits; mixing
    int64 and float64 upcasts; assigning a float into an int array truncates."""
    i8 = np.array([127], dtype=np.int8)
    f32 = np.float32(1) + np.float32(1e-8)
    ints = np.arange(3)
    ints[0] = 2.9
    return {
        "int8_overflow": int((i8 + np.int8(1))[0]),           # -128
        "float32_absorbs_1e-8": bool(f32 == np.float32(1)),
        "int_plus_float_dtype": str((ints + 0.5).dtype),      # float64
        "float_into_int_truncates": int(ints[0]),             # 2
        "bool_sum_dtype": str(np.array([True, False]).sum().dtype),
    }


# ---------------------------------------------------------------- broadcasting
def broadcast_shape(*shapes: tuple[int, ...]) -> tuple[int, ...]:
    """Pure implementation of the broadcasting rule: align shapes on the
    RIGHT, pad missing leading axes with 1, and for each axis the extents
    must be equal or one of them 1 (which is stretched)."""
    ndim = max(len(s) for s in shapes)
    padded = [(1,) * (ndim - len(s)) + tuple(s) for s in shapes]
    out = []
    for extents in zip(*padded):
        non1 = {e for e in extents if e != 1}
        if len(non1) > 1:
            raise ValueError(f"operands could not be broadcast together: {shapes}")
        out.append(non1.pop() if non1 else 1)
    return tuple(out)


def outer_via_broadcast(x: np.ndarray, y: np.ndarray) -> np.ndarray:
    """(n,1) * (1,m) -> (n,m): np.newaxis inserts the length-1 axis."""
    return x[:, np.newaxis] * y[np.newaxis, :]


def standardise_columns(X: np.ndarray) -> np.ndarray:
    """(n,p) - (p,) broadcasts over rows; keepdims avoids a reshape."""
    mu = X.mean(axis=0, keepdims=True)
    sd = X.std(axis=0, keepdims=True)
    return (X - mu) / sd


# ---------------------------------------------------------------- indexing
def fancy_indexing_demo() -> dict:
    a = np.arange(20).reshape(4, 5)
    rows, cols = np.array([0, 2]), np.array([1, 3])
    return {
        "pairs": a[rows, cols].tolist(),          # elementwise: a[0,1], a[2,3]
        "grid": a[np.ix_(rows, cols)].tolist(),   # outer: 2x2 sub-block
        "mask_count": int((a > 10).sum()),
        "argsort_rows_by_last": a[np.argsort(a[:, -1])[::-1]][:, -1].tolist(),
        "where": np.where(a % 7 == 0, a, 0).sum().item(),
    }


def assign_with_fancy_index_pitfall() -> list[int]:
    """a[idx] += 1 with repeated indices increments each slot ONCE (the RHS
    is computed on a copy, then written back).  np.add.at accumulates."""
    a = np.zeros(3, dtype=int)
    a[[0, 0, 1]] += 1              # -> [1, 1, 0]
    b = np.zeros(3, dtype=int)
    np.add.at(b, [0, 0, 1], 1)     # -> [2, 1, 0]
    return a.tolist() + b.tolist()


# ---------------------------------------------------------------- vectorisation
def pairwise_dist_loop(P: np.ndarray) -> np.ndarray:
    n = len(P)
    D = np.empty((n, n))
    for i in range(n):
        for j in range(n):
            D[i, j] = np.sqrt(((P[i] - P[j]) ** 2).sum())
    return D


def pairwise_dist_vec(P: np.ndarray) -> np.ndarray:
    """(n,1,d) - (1,n,d) -> (n,n,d), then reduce over d.  Memory n^2 d."""
    diff = P[:, None, :] - P[None, :, :]
    return np.sqrt((diff ** 2).sum(axis=-1))


def pairwise_dist_gram(P: np.ndarray) -> np.ndarray:
    """|p_i - p_j|^2 = |p_i|^2 + |p_j|^2 - 2 p_i.p_j: O(n^2 d) flops via one
    BLAS matmul, no n^2 d temporary.  Clip guards against -1e-16."""
    sq = (P ** 2).sum(axis=1)
    D2 = sq[:, None] + sq[None, :] - 2 * P @ P.T
    return np.sqrt(np.clip(D2, 0, None))


# ---------------------------------------------------------------- ufuncs
def ufunc_demo() -> dict:
    x = np.arange(1, 6, dtype=float)
    out = np.empty_like(x)
    np.multiply(x, 2, out=out)                   # no temporary
    return {
        "reduce": float(np.add.reduce(x)),       # == x.sum()
        "accumulate": np.add.accumulate(x).tolist(),
        "outer": np.multiply.outer([1, 2], [10, 20]).tolist(),
        "out_param": out.tolist(),
        "where": np.sqrt(x - 3, where=x >= 3, out=np.zeros_like(x)).tolist(),
        "reduceat": np.add.reduceat(x, [0, 2]).tolist(),   # sums [0:2], [2:]
    }


# ---------------------------------------------------------------- einsum
def einsum_demo(A: np.ndarray, B: np.ndarray, v: np.ndarray) -> dict:
    """Index notation: repeated index = summed, output indices after ->."""
    return {
        "trace": np.einsum("ii", A),
        "diag": np.einsum("ii->i", A),
        "matmul": np.einsum("ij,jk->ik", A, B),
        "matvec": np.einsum("ij,j->i", A, v),
        "outer": np.einsum("i,j->ij", v, v),
        "hadamard": np.einsum("ij,ij->ij", A, B),
        "rowsums": np.einsum("ij->i", A),
        "quadratic_form": np.einsum("i,ij,j", v, A, v),
        "transpose": np.einsum("ij->ji", A),
    }


def batched_matvec(As: np.ndarray, vs: np.ndarray) -> np.ndarray:
    """As (b,n,n), vs (b,n) -> (b,n); same as (As @ vs[..., None])[..., 0]."""
    return np.einsum("bij,bj->bi", As, vs)


# ---------------------------------------------------------------- linalg
def linalg_demo(rng: np.random.Generator) -> dict:
    A = rng.standard_normal((5, 5))
    S = A @ A.T + 5 * np.eye(5)             # SPD
    b = rng.standard_normal(5)
    x = np.linalg.solve(S, b)               # LU, never inv(S) @ b
    w, V = np.linalg.eigh(S)                # symmetric: real, sorted
    X = rng.standard_normal((20, 3))
    y = X @ np.array([1.0, -2.0, 0.5]) + 0.01 * rng.standard_normal(20)
    coef, *_ = np.linalg.lstsq(X, y, rcond=None)
    return {
        "residual": float(np.linalg.norm(S @ x - b)),
        "cond": float(np.linalg.cond(S)),
        "eig_recon_err": float(np.linalg.norm((V * w) @ V.T - S)),
        "lstsq_coef": coef,
        "det_sign_logdet": np.linalg.slogdet(S),
    }


# ---------------------------------------------------------------- random
def random_demo(seed: int = 0) -> dict:
    """Generator API: default_rng(seed) -> PCG64; reproducible streams,
    independent child streams via spawn.  Prefer over np.random.seed."""
    rng = np.random.default_rng(seed)
    child1, child2 = rng.spawn(2)
    return {
        "uniform": rng.random(3),
        "normal": rng.normal(0, 1, 3),
        "ints": rng.integers(0, 10, 5),            # high exclusive
        "choice": rng.choice(5, size=3, replace=False),
        "child_differ": not np.allclose(child1.random(3), child2.random(3)),
        "same_seed_same_stream": np.allclose(
            np.random.default_rng(seed).random(3), np.random.default_rng(seed).random(3)),
    }


# ---------------------------------------------------------------- pitfalls
def grow_by_append(n: int) -> np.ndarray:
    """O(n^2): np.append copies the whole array every call."""
    a = np.empty(0)
    for i in range(n):
        a = np.append(a, i)
    return a


def grow_preallocated(n: int) -> np.ndarray:
    a = np.empty(n)
    for i in range(n):
        a[i] = i
    return a


if __name__ == "__main__":
    a = np.arange(6, dtype=np.float64).reshape(2, 3)
    print("layout:", describe(a), "\n  strides by formula:", c_strides(a.shape, 8))
    print("view vs copy:", view_vs_copy_demo())
    print("T.reshape copies:", transpose_reshape_needs_copy())
    print("dtype pitfalls:", dtype_pitfalls())
    print("broadcast (3,1,4)+(2,1):", broadcast_shape((3, 1, 4), (2, 1)))
    print("fancy:", fancy_indexing_demo(), assign_with_fancy_index_pitfall())
    P = np.random.default_rng(1).random((200, 3))
    import timeit
    for f in (pairwise_dist_loop, pairwise_dist_vec, pairwise_dist_gram):
        print(f"{f.__name__:22s} {timeit.timeit(lambda: f(P), number=3)/3*1e3:8.2f} ms")
    print("ufuncs:", ufunc_demo())
    print("moving avg:", moving_average_strided(np.arange(6.0), 3))
    print("linalg:", {k: v for k, v in linalg_demo(np.random.default_rng(0)).items() if k != "lstsq_coef"})
    print("random:", random_demo())
    print("append vs prealloc (5000):",
          f"{timeit.timeit(lambda: grow_by_append(5000), number=1)*1e3:.1f} ms",
          f"{timeit.timeit(lambda: grow_preallocated(5000), number=1)*1e3:.1f} ms")
