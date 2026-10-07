# docs-map — which page backs which claim

The counterpart of `numerical-computation/refs/lecture-notes-map.md`. That
course has one lecture script, so its map is section-by-section through a PDF.
This course has no script at all [S1], so the map runs the other way: from each
note section to the **version-pinned documentation page** that is the primary
source for it, and to the code that exercises it in the repo venv.

Versions: CPython 3.12, NumPy 2.5, SciPy 1.18, pandas 3.0, Matplotlib 3.11.2,
pytest 9.1, PuLP 4.0 [S40] (re-verified 2026-09-27; PuLP was 3.3 on 2026-09-22). Full URLs in [`SOURCES.md`](SOURCES.md); the paths
below are relative to the base URL given in each source entry.

## 01 Python for scientists [S11], [S34], [S38]

| § | claim | page |
|---|---|---|
| 1 | objects, identity, binding, mutability, hashability | `reference/datamodel.html` §3.1–3.2 |
| 1 | LEGB, `nonlocal`, `global`, `UnboundLocalError` | `reference/executionmodel.html` §4.2 |
| 2–3 | comprehension scope; iterator protocol; generators | `reference/expressions.html` §6.2.4, §6.2.9 |
| 5 | `functools.wraps`, `lru_cache`, `cache` | `library/functools.html` |
| 6 | `@dataclass`, `frozen`, `slots`, `field(default_factory=…)` | `library/dataclasses.html` |
| 7 | annotations are not enforced; `X | None` | `library/typing.html` |
| 8 | `try/except/else/finally`, exception chaining | `reference/compound_stmts.html` §8.4 |
| 9 | `__enter__`/`__exit__`, `contextlib.contextmanager` | `library/contextlib.html` |
| 10 | venv, `uv venv`, `uv sync`, `uv.lock` | uv docs, *Projects* and *Locking* [S34] |
| — | independent ordering cross-check | Sundnes chs. 1–9 [S38] |

Code: [`../src/py/python_basics.py`](../src/py/python_basics.py).

## 02 NumPy [S12], [S13], [S14], [S39]

| § | claim | page |
|---|---|---|
| 1 | header + buffer, `shape`/`strides`/`base`, address formula | `reference/arrays.ndarray.html` (*Internal memory layout*) |
| 2 | dtype table, `finfo`/`iinfo`, casting on assignment | `reference/arrays.dtypes.html`, `reference/generated/numpy.finfo.html` |
| 2 | **weak Python scalars**: `float32 array + 1.0 → float32` | NEP 50 [S13]; `numpy_2_0_migration_guide.html` |
| 2 | scalar integer overflow now **warns**; array overflow still silent | NEP 50 [S13] — verified in `test_doc_examples.py` |
| 3 | which operations view and which copy; `shares_memory` | `user/basics.copies.html` |
| 3 | `sliding_window_view`, `as_strided` has no bounds checking | `reference/generated/numpy.lib.stride_tricks.as_strided.html` |
| 4 | the three-step broadcasting rule | `user/basics.broadcasting.html` |
| 5 | basic vs advanced indexing; `np.ix_`; `np.add.at` | `user/basics.indexing.html` |
| 6 | ufunc methods `reduce`/`accumulate`/`outer`/`reduceat`/`at`, `out=`, `where=` | `reference/ufuncs.html` |
| 6 | `np.sum` uses pairwise summation | `reference/generated/numpy.sum.html` (*Notes*) |
| 7 | einsum subscript semantics, `optimize=` | `reference/generated/numpy.einsum.html` |
| 8 | `solve` vs `inv`, `eigh` ascending and real, stacked inputs | `reference/routines.linalg.html` |
| 9 | `default_rng`, PCG64, `spawn`, legacy global state | `reference/random/generator.html`, `reference/random/parallel.html` |
| 9 | streams are **not** guaranteed across releases | NEP 19 [S14] |
| 10 | performance guidance, cross-check | *Advanced NumPy* chapter [S39] |

Code: [`../src/py/numpy_tour.py`](../src/py/numpy_tour.py).

## 03 SciPy [S15], [S37], [S39]

| § | claim | page |
|---|---|---|
| head | subpackages must be imported explicitly | `reference/index.html` |
| integrate | `quad` is adaptive Gauss–Kronrod from QUADPACK; `points=`, `epsabs` | `reference/generated/scipy.integrate.quad.html` |
| integrate | `solve_ivp` needs a first-order system; `RK45` is Dormand–Prince | `.../solve_ivp.html`, which cites [S37] |
| integrate | stiff → `Radau`/`BDF`/`LSODA`; `dense_output`, `events` | `.../solve_ivp.html` |
| interpolate | **`interp1d` is legacy** | `.../interp1d.html` + `tutorial/interpolate/1D.html` |
| interpolate | `CubicSpline` bc types, `PchipInterpolator` shape preservation | `.../CubicSpline.html`, `.../PchipInterpolator.html` |
| sparse | COO/CSR/CSC/LIL/DOK trade-offs; `csr_array` vs `csr_matrix` | `reference/sparse.html` |
| sparse | `spsolve`/`splu` (SuperLU), `cg`/`gmres`, `LinearOperator`, ARPACK | `reference/sparse.linalg.html` |
| linalg | `solve(assume_a=…)` drivers, `expm` by scaling-and-squaring Padé | `reference/linalg.html`, `.../scipy.linalg.expm.html` |
| fft | unnormalised forward transform, `rfft` gives $n/2+1$ bins, `workers=` | `reference/fft.html` |
| stats | frozen distributions, `ppf`/`sf`, test result objects | `reference/stats.html` |
| signal | `output="sos"` is numerically robust above ~order 8 | `reference/generated/scipy.signal.butter.html` |
| all | independent cross-check | *SciPy* chapter [S39] |

Code: [`../src/py/scipy_tour.py`](../src/py/scipy_tour.py).

## 04 Matplotlib and pandas [S17], [S16], [S39]

| § | claim | page |
|---|---|---|
| 1 | backend / artist / pyplot layers; Figure → Axes → Axis; prefer OO | `users/explain/figure/api_interfaces.html` |
| 1 | `figure.max_open_warning` is 20 | `users/explain/figure/figure_intro.html`; rcParam checked in the venv |
| 2 | `rc_context`, style sheets, `savefig` format from the extension | `users/explain/customizing.html` |
| 3 | `layout="constrained"` is the current spelling | `users/explain/axes/constrainedlayout_guide.html` |
| 4 | `origin="upper"` default; colormap choice, `viridis` as default | `users/explain/colors/colormaps.html` |
| 5 | mplot3d sorts whole artists, so intersecting surfaces render wrongly | `mpl_toolkits/mplot3d/faq.html` |
| 7 | **Copy-on-Write is permanent in pandas 3** | `user_guide/copy_on_write.html` [S16] |
| 7 | **`SettingWithCopyWarning` is removed**; chained assignment → `ChainedAssignmentError` | `whatsnew/v3.0.0.html` [S16] |
| 7 | string columns default to `str` dtype (PDEP-14) | `whatsnew/v3.0.0.html`, `user_guide/text.html` [S16] |
| 7 | `groupby` → `agg`/`transform`/`apply` semantics | `user_guide/groupby.html` [S16] |
| 7 | `.loc` vs `.iloc` vs chained indexing | `user_guide/indexing.html` [S16] |

Code: [`../src/py/plotting.py`](../src/py/plotting.py).

## 05 Testing [S18], [S19], [S33]

| § | claim | page |
|---|---|---|
| 2 | collection rules, CLI flags, ini options | `reference/reference.html` §*Configuration Options*, `explanation/goodpractices.html` |
| 2 | assertion rewriting | `how-to/assert.html` |
| 2 | `approx` default `rel=1e-6`, `abs=1e-12` | `reference/reference.html#pytest.approx` |
| 2 | markers, `xfail(strict=True)`, `importorskip` | `how-to/skipping.html` |
| 3 | fixture scopes, `yield` teardown, `conftest.py`, built-ins | `how-to/fixtures.html` |
| 4 | `parametrize`, stacking, `pytest.param(marks=…)` | `how-to/parametrize.html` |
| 5 | `assert_allclose` defaults `rtol=1e-7`, `atol=0` | [S19] |
| 6 | Hypothesis strategies, shrinking, example database | [S33] — **not installed** |

Code: [`../src/py/testing_examples.py`](../src/py/testing_examples.py),
[`../src/py/test_testing_examples.py`](../src/py/test_testing_examples.py).

## 06 Reproducibility and Jupyter [S20], [S21], [S22], [S14], [S34]

| § | claim | page |
|---|---|---|
| 1 | kernel/frontend split, ZeroMQ, message types | Jupyter messaging protocol [S21] |
| 1 | nbformat 4 cell and output schema | nbformat *format description* [S21] |
| 2 | every magic in the table | IPython *Built-in magic commands* [S20] |
| 3 | seeded ≠ bit-identical across versions | NEP 19 [S14] |
| 3 | lock file vs `pyproject.toml` | uv docs [S34] |
| 5 | `--to`, `--execute`, `--no-input`, timeout | nbconvert *Using as a command line tool* [S22] |

Code: [`../src/notebooks/tour.ipynb`](../src/notebooks/tour.ipynb).

## 07 Optimisation [S15], [S23], [S24], [S25]

| § | claim | page |
|---|---|---|
| 2 | the method table, `OptimizeResult` fields, finite-difference gradients | `.../scipy.optimize.minimize.html` |
| 3 | which methods accept `bounds`; `{"type": "ineq"}` means $g(x)\ge 0$ | `.../scipy.optimize.minimize.html`, `.../LinearConstraint.html` |
| 4 | `least_squares` takes the residual vector; `trf`/`lm`/`dogbox`, robust losses | `.../scipy.optimize.least_squares.html` |
| 5 | `root` methods; `brentq` bracketing vs `newton` | `.../scipy.optimize.root.html`, `.../brentq.html` |
| 6 | `linprog` default `method="highs"`; `milp` integrality | `.../linprog.html`, `.../milp.html`, HiGHS [S24] |
| 7 | PuLP modelling API, `lpSum`, `prob.add_variable_dict`, duals via `.pi` | PuLP docs [S23]; PuLP 4.0.0 signatures read from the installed package |
| 7 | **PuLP 4.0 removed `LpVariable(name,…)`, `prob.constraints` as a dict, `PULP_CBC_CMD`, `LpStatus` and the bundled CBC** (3.3 had deprecated the first three) | installed wheel's README (`pulp-4.0.0.dist-info/METADATA`) and execution; `test_doc_examples.py::test_pulp4_removed_what_3_3_deprecated`; see `../notes/CHANGELOG.md` |
| 7 | without a PuLP solver, the model is solved by SciPy's HiGHS | `.../linprog.html`, `.../milp.html`, HiGHS [S24]; `optimisation.solve_pulp` |
| 7 | CBC does branch-and-cut; not bundled with PuLP since 4.0 | COIN-OR CBC [S25] |

Code: [`../src/py/optimisation.py`](../src/py/optimisation.py).

## 08 Parallel processing [S11], [S26], [S35], [S36], [S12]

| § | claim | page |
|---|---|---|
| 1 | the GIL and what releases it | `library/multiprocessing.html` intro; `c-api/init.html` §*Thread State* |
| 1 | free-threaded build; sub-interpreters | PEP 703, PEP 734 [S26] |
| 2 | start methods; `fork` unsafe with threads; 3.14 changes the Linux default | `library/multiprocessing.html` §*Contexts and start methods* |
| 3 | `Pool.map`/`imap_unordered`/`starmap`; `Executor`, `Future`, `as_completed` | `library/multiprocessing.html`, `library/concurrent.futures.html` |
| 3 | `max_workers` defaults | `library/concurrent.futures.html` |
| 4 | `SeedSequence.spawn` gives independent streams | `reference/random/parallel.html` [S12] |
| 5 | `shared_memory` create/attach/close/unlink | `library/multiprocessing.shared_memory.html` |
| 7 | $S(n)=1/((1-p)+p/n)$ | Amdahl 1967 [S35] |
| 7 | scaled speedup $S=(1-p)+pn$ | Gustafson 1988 [S36] |

Code: [`../src/py/parallel.py`](../src/py/parallel.py).

## 09 Interfaces [S11], [S27]–[S31], [S39]

| § | claim | page |
|---|---|---|
| 3 | `argtypes`/`restype`; default return type is `int` | `library/ctypes.html` §*Return types* |
| 3 | `numpy.ctypeslib.ndpointer` validates dtype/ndim/flags | `reference/routines.ctypeslib.html` [S12] |
| 4 | cffi ABI vs API mode | cffi *Overview* [S27] |
| 5 | `subprocess.run`, list-not-string, `check`, `timeout` | `library/subprocess.html` |
| 6 | f2py `-c -m`, intents, Meson requirement, column-major | f2py user guide [S28] |
| 7 | pybind11 `array_t`, GIL release, exception translation | pybind11 docs [S29] |
| 8 | juliacall shares arrays without copying; column-major transpose | PythonCall.jl docs [S30] |
| 9 | the decision table, cross-check | *Interfacing with C* chapter [S39] |

Code: [`../src/py/interfaces.py`](../src/py/interfaces.py),
[`../src/c/vecops.c`](../src/c/vecops.c).

## 10 Performance [S11], [S31], [S32], [S39], [S12]

| § | claim | page |
|---|---|---|
| 2 | `timeit` disables GC, `autorange` targets 0.2 s, report the minimum | `library/timeit.html` |
| 3 | `cProfile` is deterministic; `tottime` vs `cumtime`; `ncalls` as `a/b` | `library/profile.html` |
| 5 | `tracemalloc` traces Python allocations including NumPy buffers | `library/tracemalloc.html` |
| 5 | temporary elision above a size threshold | NumPy 1.13 release notes [S12] |
| 6 | `njit` nopython is the default and errors on unsupported code | Numba *5-minute guide* [S31] — **not installed** |
| 6 | typed memoryviews, `nogil`, `cython -a` | Cython docs [S32] — **not installed** |
| all | cross-check | *Optimizing code* chapter [S39] |

Code: [`../src/py/profiling.py`](../src/py/profiling.py).

## 11 Practice set [S39], [S41], [S42], [S43]

Note 11 is the only one whose sources are *other courses* rather than library
documentation, so the map runs differently: from each practice directory to the
source chapter it is adapted from and to the TISS subject item it serves. The
per-directory `README.md` files carry the licences.

| directory | adapted from | TISS subject item |
|---|---|---|
| `../src/exercises/aalto-python-for-scicomp-2025/` | Aalto chapters *NumPy*, *Pandas*, *SciPy*, *Parallel programming* [S41] | NumPy/SciPy; data processing; parallel processing |
| `../src/exercises/scientific-python-lectures-2024/` | ch. 2.7 *Mathematical optimization*, ch. 2.8 *Interfacing with C* [S39] | optimisation; interfaces |
| `../src/exercises/software-carpentry-python-2026/` | ep. 2 *Analyzing Patient Data*, ep. 9 *Errors and Exceptions*, ep. 10 *Defensive Programming* [S42] | the language; code testing |
| [`../src/exercises/mc_items.py`](../src/exercises/mc_items.py) | **nothing — ours** [S43] | all eight, three items each |

Code: `../src/exercises/`; tests in each directory.

## Executable part of this map

[`../src/py/test_doc_examples.py`](../src/py/test_doc_examples.py) turns the
rows in **bold** above — the version-sensitive ones — into assertions, each with
its source URL in the test docstring. When a library upgrade changes one of
them, that test fails and this map, not the reader, is what is out of date.

[`../src/exercises/test_mc_bank.py`](../src/exercises/test_mc_bank.py) does the
same for note 11's 24 exam questions: each one's correct answer is *derived by
executing* the behaviour, and `pick`/`pick_true` require exactly one of the four
options to match, so an item that acquires a second defensible answer fails the
suite rather than misleading a reader.
