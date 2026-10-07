# 02 NumPy

Code: [`../src/py/numpy_tour.py`](../src/py/numpy_tour.py), tests in `test_numpy_tour.py`.

Sources: the NumPy 2.5 reference [S12], NEP 50 on scalar promotion [S13], NEP 19
on the RNG stream policy [S14]; cross-checked against the *Advanced NumPy*
chapter of the *Scientific Python Lectures* (CC BY 4.0) [S39].
**Verified against NumPy 2.5.3** [S40], last re-run 2026-09-27: every behaviour below was re-run in the
repo venv, and the version-sensitive ones are asserted in
[`../src/py/test_doc_examples.py`](../src/py/test_doc_examples.py).

## 1. What an ndarray is

An `ndarray` is a *header* plus a *contiguous block of raw memory*. The header holds `shape`, `dtype` (element type and size), `strides` (bytes to step per axis), a data pointer, flags and possibly a reference to a `base` array that owns the memory. The element `a[i, j]` lives at

$$\text{addr}(i, j) = \text{data} + i \cdot s_0 + j \cdot s_1 \quad (\text{strides in bytes}).$$

For a C-ordered (row-major) `(n, m)` float64 array, `strides == (8m, 8)`; Fortran order gives `(8, 8n)`. `c_strides` computes this. Row-major means the last index varies fastest in memory, so iterating over the last axis is cache-friendly; summing over axis 0 of a C array touches memory with stride `8m`.

Why numpy is fast: one dtype per array means no per-element type dispatch, the data is packed (a Python list of floats is an array of pointers to 24-byte objects), and loops run in compiled C (ufuncs) that release the GIL. Python-level loops over elements throw all of that away.

## 2. dtypes

`np.float64` (default float), `float32`, `int64` (default int on Linux/macOS), `int8..int64`, `uint*`, `bool_`, `complex128`, fixed-width strings `U10`, `object` (pointers; slow), structured dtypes. Rules that bite (`dtype_pitfalls`):

- Integer arithmetic **wraps**: `np.array([127], np.int8) + np.int8(1)` gives `-128`. Python ints are arbitrary precision; numpy ints are machine words. Since numpy 2 the two halves of that sentence are reported differently [S13]: the *array* case wraps **silently**, but the *scalar* case `np.int8(127) + np.int8(1)` also emits `RuntimeWarning: overflow encountered in scalar add` while still returning `-128`. Do not rely on seeing a warning — you only get one when both operands are scalars.
- Mixed operations upcast by *type promotion*: `int64 + float64 -> float64`, `float32 + float64 -> float64`, but `float32 array + Python float -> float32` (NEP 50 [S13], numpy 2: Python scalars are "weak"). `int + uint` may go to `float64`.
- Assigning into an existing array casts to *its* dtype: `ints[0] = 2.9` stores 2. `np.array([1, 2]) / 2` is float, but `arr /= 2` on an int array raises (`UFuncTypeError`), because the result cannot be cast back safely.
- `float32` has 24 significand bits (about 7 decimal digits, $\epsilon \approx 1.2 \times 10^{-7}$); `1 + 1e-8` is absorbed.
- `astype` always copies; `np.finfo(dtype)` / `np.iinfo(dtype)` give limits.

## 3. Views vs copies

Basic slicing (`a[1:5]`, `a[:, ::2]`, `a[..., None]`), `reshape` when possible, `.T`, `ravel()` when contiguous, `view()`, `np.newaxis` return **views**: a new header on the same memory. Writing through the view changes the original (`view_vs_copy_demo`). **Copies** come from fancy indexing (`a[[0, 2]]`), boolean masks, `flatten()`, `astype`, most arithmetic, and `np.copy`. Check with `np.shares_memory(a, b)` or `b.base is a`.

A view may need a copy when the requested layout cannot be expressed with one stride per axis: `a.T.reshape(-1)` copies silently (`transpose_reshape_needs_copy`), `a.T.view(...)` would raise. `np.ascontiguousarray` forces C layout (copying only if needed): C libraries and many algorithms need it.

`sliding_window_view` / `as_strided` create overlapping windows with zero copies by giving two axes the same stride (`moving_average_strided`). `as_strided` does no bounds checking: wrong strides read garbage or crash.

## 4. Broadcasting

Elementwise operations on arrays of different shapes follow one rule [S12] (`broadcast_shape` implements it, tested against `np.broadcast_shapes`):

1. Align shapes at the **right**, pad the shorter with leading 1s.
2. Axis by axis, extents must be **equal or one of them 1**; the 1 is stretched (stride 0, no memory).
3. Otherwise `ValueError: operands could not be broadcast together`.

$(3,1,4)$ with $(2,1)$ gives $(3,2,4)$; $(3,)$ with $(4,)$ fails; $(4,1)$ with $(4,)$ gives $(4,4)$, an outer product, which is the classic surprise when you meant elementwise. Insert axes explicitly with `x[:, None]` / `np.newaxis`, and use `keepdims=True` in reductions so `X - X.mean(axis=0, keepdims=True)` stays unambiguous (`standardise_columns`). Broadcasting is also how `pairwise_dist_vec` forms all differences at once: `(n,1,d) - (1,n,d)`; the temporary is $n^2 d$ elements, so for large $n$ the Gram-matrix formulation `pairwise_dist_gram` ($|p_i - p_j|^2 = |p_i|^2 + |p_j|^2 - 2 p_i \cdot p_j$, one BLAS matmul) is better, at the price of cancellation for nearly equal points.

## 5. Indexing

- Basic: integers and slices, `...` (Ellipsis) for "all remaining axes", `None` adds an axis.
- **Fancy** (integer arrays): `a[rows, cols]` pairs the index arrays elementwise (broadcast together) and returns the selected *elements*; `a[np.ix_(rows, cols)]` gives the outer sub-block. Always a copy.
- Boolean masks: `a[a > 0]` flattens; `np.where(cond, x, y)` selects; `np.nonzero`, `np.argwhere` give indices.
- `argsort`, `argmax`, `searchsorted` for index-based work; `np.take_along_axis` to apply argsort results.
- Assignment with repeated fancy indices does **not** accumulate: `a[[0, 0]] += 1` adds 1 once (the RHS is evaluated on a copy, then written back). Use `np.add.at(a, idx, 1)` or `np.bincount` (`assign_with_fancy_index_pitfall`).

## 6. Vectorisation and ufuncs

A **ufunc** (universal function) is an elementwise operation with broadcasting, type resolution and optional `out=`, `where=`, `dtype=` arguments: `np.add`, `np.sqrt`, `np.maximum`, comparisons. Binary ufuncs come with methods (`ufunc_demo`): `reduce` (`np.add.reduce == sum`), `accumulate` (cumsum), `outer`, `reduceat` (segmented reduce), `at` (unbuffered in-place). `out=` avoids temporaries: `np.multiply(x, 2, out=x)`.

"Vectorise" means: express the loop as whole-array operations so the iteration happens in C. `pairwise_dist_loop` vs `pairwise_dist_vec` is a 50-100x difference for $n = 200$. `np.vectorize` is *not* vectorisation; it is a Python loop with broadcasting sugar. When an operation has no numpy expression (sequential dependence like `x[i] = f(x[i-1])`), look at `np.cumsum`/`cumprod`/`accumulate`, `scipy.signal.lfilter`, or numba (note 10).

Aggregations: `sum`, `mean`, `std(ddof=0)` (population by default; pandas uses `ddof=1` [S16]), `min/max`, `argmin`, `any/all`, along `axis=`; `np.nan*` variants ignore NaN. `np.sum` uses **pairwise summation** (error $O(\varepsilon \log n)$ instead of $O(\varepsilon n)$) [S12], which is why `a.sum()` and `np.cumsum(a)[-1]` differ in the last bits.

## 7. einsum

`np.einsum("ij,jk->ik", A, B)` is Einstein summation: every index repeated across inputs or absent from the output is summed; the output's index order defines the result's axes. It covers trace `"ii"`, diagonal `"ii->i"`, matvec `"ij,j->i"`, outer `"i,j->ij"`, Hadamard `"ij,ij->ij"`, quadratic form `"i,ij,j"`, batched matmul `"bij,bjk->bik"`, transposition `"ij->ji"` (`einsum_demo`, `batched_matvec`). It is unambiguous where `dot`/`tensordot` need explanation; for large contractions pass `optimize=True` (or use `np.einsum_path`) so it chooses a pairwise order that calls BLAS, otherwise a three-operand einsum can be a naive loop. `@` / `np.matmul` broadcasts over leading batch axes; `np.dot` for 2D is matmul but for ND has its own (confusing) rule.

## 8. linalg

`np.linalg`: `solve` (LU with pivoting: use it instead of `inv(A) @ b`, which is slower and less accurate), `lstsq` (SVD-based least squares, returns solution, residuals, rank, singular values), `inv`, `det`/`slogdet` (avoid overflow), `eig` (general, complex), `eigh` (symmetric/Hermitian: real, sorted ascending, faster, stable), `svd`, `qr`, `cholesky`, `norm`, `cond`, `matrix_rank`, `pinv`. Functions accept stacks of matrices (`(..., n, n)`). Behind them is LAPACK/BLAS (OpenBLAS or Accelerate on macOS), multithreaded: this is where numpy already runs parallel (note 08). `linalg_demo` shows `solve`, `eigh` reconstruction $V \Lambda V^T$ and `lstsq`.

## 9. Random numbers: the Generator API

`rng = np.random.default_rng(seed)` returns a `Generator` wrapping the PCG64 bit generator [S12]. Methods: `random`, `normal`, `integers(low, high)` (high exclusive), `choice`, `permutation`, `shuffle` (in place), `standard_normal`, distributions. Reproducibility: same seed, same sequence of calls, same numpy version → identical numbers — and the version qualifier is load-bearing, because NEP 19 [S14] deliberately *refuses* to guarantee a `Generator`'s stream across releases (only `RandomState` is stream-compatible, and it is legacy). Independent streams: `rng.spawn(n)` or `np.random.SeedSequence(seed).spawn(n)`, used in note 08 for parallel workers. The legacy `np.random.seed()` / `np.random.rand()` API uses a *global* Mersenne Twister state: any library call can advance it, so avoid it in new code. Pass `rng` objects into functions instead of seeds (`random_demo`).

## 10. Performance pitfalls

- Growing arrays with `np.append` / `np.concatenate` in a loop is $O(n^2)$: preallocate (`grow_preallocated`) or collect in a list and convert once.
- Python-level loops over elements; `np.vectorize`; `for row in A`.
- Unnecessary copies: `astype`, fancy indexing, `flatten()`, non-contiguous inputs to C libraries.
- Huge broadcast temporaries (`(n,n,d)`), expression chains creating one temporary per operator; use `out=` and in-place ops, or numexpr/numba.
- Wrong axis in reductions on C-ordered arrays (stride effects); `object` dtype from ragged lists; int overflow; float32 accumulation of many terms.
- `np.dot` on 1D vs 2D shapes; forgetting `keepdims`; comparing arrays with `==` in an `if` ("truth value of an array is ambiguous": use `.all()`/`.any()` or `np.allclose`).

## Exam-style questions

**All five are ours**, in the multiple-choice style the 2024W-onwards format
implies [S3]; no past paper for this course is public [S9]. Answers re-checked
in the venv against NumPy 2.5.3.

1. `a = np.zeros((4, 6))`; what are `a.strides`?
   (a) `(6, 1)` (b) `(48, 8)` (c) `(8, 48)` (d) `(4, 6)`
   **b.** Row-major, float64: the last axis steps 8 bytes, the first steps 6 x 8.

2. Which operation returns a view of `a`?
   (a) `a[[0, 1]]` (b) `a[a > 0]` (c) `a[::2]` (d) `a.astype(float)`
   **c.** Basic slicing is a view; fancy indexing, boolean masks and `astype` copy.

3. Shapes `(5, 1, 3)` and `(4, 1)` broadcast to
   (a) `(5, 4, 3)` (b) `(5, 4, 1)` (c) error (d) `(4, 3)`
   **a.** Right-align: `(5,1,3)` vs `(1,4,1)`; each axis has a 1 or equal extents.

4. `b = np.zeros(3, int); b[[0, 0, 2]] += 1`; `b` is
   (a) `[2, 0, 1]` (b) `[1, 0, 1]` (c) `[1, 1, 1]` (d) error
   **b.** Fancy-index augmented assignment reads, adds, writes back once per unique slot; `np.add.at` would give (a).

5. Which is true of `np.linalg.eigh`?
   (a) Works for any square matrix and returns complex eigenvalues. (b) Assumes a symmetric/Hermitian input and returns real eigenvalues in ascending order. (c) Returns eigenvalues only. (d) Is slower than `eig` because it checks symmetry.
   **b.** It uses the lower (or upper) triangle without checking and calls the symmetric LAPACK routine, which is faster and more accurate.
