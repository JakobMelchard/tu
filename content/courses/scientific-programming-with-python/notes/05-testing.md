# 05 Code testing

Code: [`../src/py/testing_examples.py`](../src/py/testing_examples.py) (code under test) and [`../src/py/test_testing_examples.py`](../src/py/test_testing_examples.py) (the patterns). Run `../../.venv/bin/python -m pytest src/py/test_testing_examples.py -v`.

Sources: the pytest documentation [S18], `numpy.testing` [S19], Hypothesis
[S33]. **Verified against pytest 9.1.1 and NumPy 2.5.3** [S40], last re-run 2026-09-27. pytest does not
publish a per-minor documentation tree, so [S18] cites `stable`, which was 9.x
at retrieval.

## 1. Why and what

A test is executable documentation of what a function promises; it turns "it worked on my laptop" into a repeatable check and lets you refactor without fear. Levels: **unit** (one function, fast, no I/O), **integration** (modules together, files, solvers), **regression** (freeze a known output so a bug does not return), **property** (invariants over random inputs). For scientific code the hard part is the *oracle*: what is the right answer? Sources of oracles, in order of preference:

1. Analytic solutions (harmonic oscillator, $\int e^{-x^2}$, polynomial integration).
2. Mathematical identities and invariants (energy conservation, symmetry, Vieta's formulas, $A A^{-1} = I$, $\text{ifft}(\text{fft}(x)) = x$).
3. Convergence order: halving $h$ must reduce the error by $2^p$ (`test_trapezoid_is_second_order`).
4. A reference implementation (numpy/scipy, a slow brute force, a previous version).
5. Manufactured solutions: choose $u$, compute $f = L u$, solve $L u = f$ and compare.
6. Regression values stored from a trusted run (weakest: they only detect *change*).

## 2. pytest mechanics

- Discovery [S18]: files `test_*.py` or `*_test.py`, functions `test_*`, classes `Test*` without `__init__`. Run `pytest` (from the directory or with paths), `-q` quiet, `-v` names, `-x` stop at first failure, `-k expr` select by name, `-m marker`, `--lf` last failed, `-s` show prints, `--durations=5`. `pytest.ini`/`pyproject.toml [tool.pytest.ini_options]` set `testpaths`.
- A plain `assert` is enough: pytest rewrites the assertion bytecode to show operands on failure (`assert x == y` prints both values, list diffs, dict diffs).
- Exceptions: `with pytest.raises(ValueError, match="regex"): ...`; `info.value` for the exception object. `pytest.warns` for warnings.
- Floats: `x == pytest.approx(y, rel=1e-6, abs=1e-12)` (documented defaults `rel=1e-6`, `abs=1e-12`; the signature carries `rel=None, abs=None` and applies them internally) [S18]; works elementwise on sequences and dicts. Never compare floats with `==` unless exactness is part of the promise (`test_floats_need_tolerances`).
- Markers: `@pytest.mark.skipif(cond, reason)`, `@pytest.mark.xfail(strict=True)` (documents a known bug; `strict` fails the run if the test unexpectedly passes), `@pytest.mark.slow` with `-m "not slow"`, `pytest.importorskip("cffi")`, `pytest.skip("msg")` at run time.
- Output: `.` pass, `F` fail, `E` error in setup, `s` skip, `x` xfail, `X` unexpected pass.

## 3. Fixtures

A fixture is a function decorated with `@pytest.fixture` whose *name* a test asks for as a parameter [S18]; pytest calls it, injects the return value and tears it down afterwards (code after `yield` runs at teardown). `scope="function"` (default, fresh per test), `"module"`, `"session"` for expensive setup shared read-only (`spd_matrix`). Built-ins: `tmp_path` (fresh `pathlib.Path` directory per test), `tmp_path_factory`, `monkeypatch` (`setenv`, `setattr`, `chdir`; undone automatically), `capsys` (captured stdout), `caplog`, `request`. Fixtures compose (`config_file` uses `tmp_path`) and live in `conftest.py` to be shared across files without imports. `autouse=True` runs a fixture for every test (e.g. to seed a global RNG). A seeded `rng` fixture gives reproducible yet independent randomness per test.

## 4. Parametrize

`@pytest.mark.parametrize("a, b, expected", [(1, 2, 3), (0, 0, 0)], ids=[...])` generates one test per tuple, each reported separately, so one bad case does not hide the others. Stack decorators for a Cartesian product. Parametrize over methods (`["BFGS", "Nelder-Mead"]` in `test_scipy_tour.py`), dtypes, grid sizes, or edge cases (`n=1`, empty input, negative, NaN). `pytest.param(..., marks=pytest.mark.xfail)` marks single cases. Fixtures can be parametrized too (`@pytest.fixture(params=[...])`).

## 5. numpy.testing

`assert_allclose(actual, desired, rtol=1e-7, atol=0)` (elementwise $|a - d| \le \text{atol} + \text{rtol} |d|$; note the default `atol=0`, so comparing against zeros needs `atol`) [S19] — both defaults re-read from the installed signature, `assert_array_equal` (exact, NaN equals NaN), `assert_array_almost_equal(decimal=6)` (older), `assert_array_almost_equal_nulp` / `assert_array_max_ulp` (units in the last place, the right measure near 1), `assert_array_less`, `assert_equal` (recursive on nested structures). Shapes must match (broadcasting is *not* applied) and error messages show mismatch counts and the max difference. `np.testing.suppress_warnings` and `pytest.warns` for warnings.

Choosing tolerances: relative for quantities away from zero, absolute near zero, both when unsure; base them on the algorithm's expected error (discretisation $O(h^2)$, iterative solver tolerance, float32 $\approx 10^{-7}$), not on whatever makes the test pass. A tolerance of `1e-15` on a sum of $10^6$ doubles will fail on another BLAS.

## 6. Property-based testing

Instead of hand-picked inputs, generate many and assert *properties*: `sorted(x)` is a permutation of `x` and monotone; roots satisfy the polynomial; `decode(encode(x)) == x`; a norm is non-negative and homogeneous; the solver residual is small. `test_quadratic_roots_satisfy_vieta` does this with a seeded loop. The library **Hypothesis** [S33] (`pip install hypothesis`; **not installed in this repo's venv** [S40], so nothing below is demonstrated in `src/`) does it properly: `@given(st.floats(min_value=-1e6, max_value=1e6))`, `hypothesis.extra.numpy.arrays(dtype, shape)`, automatic *shrinking* to a minimal failing example, and a database of past failures. Properties catch edge cases (0, -0.0, huge, tiny, NaN, empty) that examples miss.

## 7. Coverage and test design for numerical code

`pip install pytest-cov` (also **not installed here** [S40]); `pytest --cov=src/py --cov-report=term-missing` reports the percentage of lines executed by tests and which are missed. Branch coverage (`--cov-branch`) is stricter. Coverage shows what is *untested*, not what is *correct*: 100 % coverage with weak assertions proves nothing. Use it to find dead code and forgotten branches (error paths, empty inputs).

Design rules that pay off in scientific code:

- One behaviour per test, named after it (`test_newton_non_convergence`); Arrange-Act-Assert.
- Test the contract, not the implementation; test edge cases explicitly (n=0, n=1, singular matrix, negative discriminant, zero vector, huge/small magnitudes for overflow and cancellation: `test_stable_quadratic_avoids_cancellation`, `test_softmax_properties`).
- Make randomness reproducible (fixed seeds, `Generator` passed in) and make tests deterministic and fast (< 1 s; mark slow ones).
- Test error paths: the *right* exception with a helpful message (`match=`).
- Check convergence *rates* rather than single errors; check invariants (conservation, symmetry, orthogonality $Q^T Q = I$).
- Isolate I/O with `tmp_path`; never depend on the network, the current directory, or wall-clock time.
- Keep the code under test importable: no top-level side effects, demos under `if __name__ == "__main__":`.
- Compare against a slow, obviously-correct reference (brute-force knapsack in `test_optimisation.py`, Python loop vs vectorised distance in `test_numpy_tour.py`).
- Doctests (`python -m doctest`, `pytest --doctest-modules`) keep docstring examples honest.

## Pitfalls

- `assert_allclose(x, 0)` with default `atol=0` requires exact zero.
- `pytest.approx` on numpy arrays works but returns elementwise semantics only via `==`; use `assert_allclose` for arrays.
- Module-scoped fixtures that a test mutates leak state into later tests (order-dependent failures); use function scope or copy.
- Tests that pass because the tolerance is huge; tests that compare a function against itself (a copy of the implementation).
- Forgetting `-p no:cacheprovider`/`--lf` interactions; relying on test execution order; `time.sleep` in tests.
- Importing the module under test through a different path than production (`sys.path` hacks): use a package or the `rootdir`/`conftest.py` mechanism (pytest prepends the test file's directory, which is why `import testing_examples` works here).

## Exam-style questions

**All five are ours** [S9]; see [`00-exam-focus.md`](00-exam-focus.md).

1. Which files and functions does pytest collect by default?
   (a) any `.py` file, functions starting with `check_` (b) `test_*.py`/`*_test.py`, functions `test_*`, classes `Test*` (c) only files listed in `setup.py` (d) any function with an `assert`
   **b.**

2. `assert_allclose(a, b)` with default arguments passes when
   (a) $|a - b| \le 10^{-7}$ (b) $|a - b| \le 10^{-7} |b|$ (c) `a == b` exactly (d) $|a - b| \le 10^{-7} + 10^{-7}|b|$
   **b.** `rtol=1e-7, atol=0`; the tolerance is relative to the *desired* value, so comparing to zero needs `atol`.

3. A fixture with `scope="module"`
   (a) runs before every test function (b) runs once per test module and is shared by its tests (c) cannot use `yield` (d) is only available in `conftest.py`
   **b.**

4. `@pytest.mark.xfail(strict=True)` on a test that passes results in
   (a) pass (b) skip (c) failure of the test run (XPASS strict) (d) a warning only
   **c.** `strict` turns an unexpected pass into a failure so fixed bugs get their marker removed.

5. The most reliable oracle for a new ODE integrator is
   (a) the output of the previous version (b) an analytic solution plus a check of the convergence order (c) 100 % line coverage (d) that the code runs without exceptions
   **b.** Regression values only detect change; coverage measures execution, not correctness.
