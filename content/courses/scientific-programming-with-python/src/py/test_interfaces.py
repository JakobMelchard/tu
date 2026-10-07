"""Tests for interfaces.py (note 09): ctypes and cffi into ../c/libvecops, subprocess."""
import subprocess

import numpy as np
import pytest

import interfaces as itf


@pytest.fixture(scope="module")
def lib():
    try:
        itf.build_library()
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        pytest.skip(f"cannot build libvecops (run `make -C src/c`): {e}")
    return itf.load_ctypes()


def test_ctypes_dot_matches_numpy(lib):
    x, y = np.random.default_rng(0).random((2, 1000))
    assert itf.dot_ctypes(x, y) == pytest.approx(x @ y, rel=1e-12)
    assert lib.vec_dot(x, y, 0) == 0.0


def test_ctypes_axpy_modifies_in_place(lib):
    x, y = np.arange(5.0), np.ones(5)
    itf.axpy_ctypes(3.0, x, y)
    np.testing.assert_allclose(y, 3 * x + 1)


def test_ndpointer_rejects_wrong_dtype_and_noncontiguous(lib):
    with pytest.raises(ctypes_error()):
        lib.vec_norm2(np.arange(4, dtype=np.int32), 4)
    with pytest.raises(ctypes_error()):
        lib.vec_norm2(np.arange(8.0)[::2], 4)


def ctypes_error():
    import ctypes
    return ctypes.ArgumentError


def test_norm_avoids_overflow(lib):
    x = np.array([1e200, 1e200])
    assert np.isfinite(itf.norm_ctypes(x)) and itf.norm_ctypes(x) == pytest.approx(np.sqrt(2) * 1e200)


def test_count_primes_c_and_python_agree(lib):
    assert itf.count_primes_c(1000) == itf.count_primes_py(1000) == 168


def test_cffi_matches_ctypes(lib):
    pytest.importorskip("cffi")
    x, y = np.random.default_rng(1).random((2, 500))
    assert itf.dot_cffi(x, y) == pytest.approx(itf.dot_ctypes(x, y), rel=1e-15)


def test_cffi_takes_every_prototype_from_the_header(lib):
    pytest.importorskip("cffi")
    ffi, clib = itf.load_cffi()
    assert {"vec_dot", "vec_axpy", "vec_norm2", "count_primes"} <= set(dir(clib))
    y = np.ones(3)
    clib.vec_axpy(3, 2.0, ffi.from_buffer("double[]", np.arange(3.0)),
                  ffi.from_buffer("double[]", y))       # writes into numpy's buffer
    np.testing.assert_allclose(y, [1.0, 3.0, 5.0])
    assert clib.count_primes(1000) == 168


def test_c_side_test_suite_passes(lib):
    """`make -C src/c test` links test_vecops.c against the same library."""
    r = subprocess.run(["make", "-C", str(itf.C_DIR), "test"], capture_output=True, text=True)
    assert r.returncode == 0, r.stdout + r.stderr
    assert "0 failure(s)" in r.stdout


def test_subprocess():
    assert itf.python_version_via_subprocess() == "3"
    code, out = itf.run_external(["cat"], stdin_text="hello")
    assert (code, out) == (0, "hello")
