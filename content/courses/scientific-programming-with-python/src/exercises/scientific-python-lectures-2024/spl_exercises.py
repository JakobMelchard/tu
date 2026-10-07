"""Exercises in the style of the *Scientific Python Lectures* [S39] (CC BY 4.0).

Serves note 11 (practice set) §3; topics: ``scipy.optimize`` (note 07) and
calling C, memory layout (note 09).

**Not this course's material.**  Source: *Scientific Python Lectures*, release
2024.1, the Scientific Python developers, https://lectures.scientific-python.org/,
CC BY 4.0 — see ``README.md`` in this directory and ``../../../refs/SOURCES.md``
[S39].  The tasks below are **restated in our own words and reimplemented**; no
text or code is copied from the book.  Chapter 2.7 *Mathematical optimization*
and chapter 2.8 *Interfacing with C* are the two that cover TISS subject items
this course's other free sources do not.

Covers TISS items: "Introduction to solving optimization problems (e.g. SciPy,
PuLP)" and "Interfaces to other programming languages (e.g. Julia)".

Run:  ../../../../../.venv/bin/python spl_exercises.py
"""
from __future__ import annotations

import ctypes
import ctypes.util

import numpy as np
from scipy.optimize import curve_fit, minimize

# --------------------------------------------------------------- optimisation
# Task 1 (after SPL 2.7, exercise "A simple (?) quadratic function"): minimise a
# quadratic whose Hessian is badly conditioned, with and without an analytic
# gradient, and count the function evaluations each method needs.


def ill_conditioned(x: np.ndarray) -> float:
    r"""$f(x,y) = \tfrac12 (x^2 + 100 y^2)$ — Hessian condition number 100."""
    return 0.5 * (x[0] ** 2 + 100.0 * x[1] ** 2)


def ill_conditioned_grad(x: np.ndarray) -> np.ndarray:
    return np.array([x[0], 100.0 * x[1]])


def gradient_pays_for_itself(x0=(1.0, 1.0)) -> dict[str, dict[str, int | float]]:
    """How much a hand-written `jac` is worth, per method.

    The lesson the book draws, and the one that is examinable: a quasi-Newton
    method without `jac` spends one extra *function* evaluation per component
    per step on finite differences, and Newton-CG refuses to run at all.
    """
    out: dict[str, dict[str, int | float]] = {}
    for method in ("CG", "BFGS", "Newton-CG"):
        with_jac = minimize(ill_conditioned, np.array(x0), method=method,
                            jac=ill_conditioned_grad)
        try:
            nfev_without = minimize(ill_conditioned, np.array(x0),
                                    method=method).nfev
        except ValueError:
            nfev_without = -1        # Newton-CG: "Jacobian is required"
        out[method] = {"nfev_with_jac": int(with_jac.nfev),
                       "nfev_without_jac": int(nfev_without),
                       "f": float(with_jac.fun)}
    return out


# Task 2 (after SPL 2.7, exercise "A locally flat minimum"): a minimum at which
# every derivative vanishes, so a gradient method has nothing to follow.


def flat_minimum_objective(x: np.ndarray) -> float:
    r"""$f(x,y) = \exp\!\big(-1/(0.1x^2 + y^2)\big)$, minimum 0 at the origin.

    Smooth everywhere and flat to all orders at the minimum: the gradient is
    numerically zero long before you are close.
    """
    q = 0.1 * x[0] ** 2 + x[1] ** 2
    return float(np.exp(-1.0 / q)) if q > 0.0 else 0.0


def flat_minimum_comparison(x0=(1.0, 1.0)) -> dict[str, tuple[float, float]]:
    """(distance from the true minimum, achieved value) per method.

    BFGS stops on a vanishing gradient while still far away; the
    derivative-free simplex and direction-set methods get there.  Check the
    achieved *value*, not `result.success`.
    """
    out = {}
    for method in ("BFGS", "Nelder-Mead", "Powell"):
        r = minimize(flat_minimum_objective, np.array(x0), method=method)
        out[method] = (float(np.linalg.norm(r.x)), float(r.fun))
    return out


# Task 3 (after SPL 2.7, exercise "Curve fitting with higher frequency"): fit a
# sinusoid whose frequency the initial guess gets wrong.


def sine_model(t, amplitude, omega, phase):
    return amplitude * np.sin(omega * t + phase)


def curve_fit_needs_the_right_frequency(seed: int = 0) -> dict[float, float]:
    """Sum of squared residuals as a function of the initial guess for omega.

    Least squares on a sinusoid is multi-modal in the frequency: start at the
    wrong omega and the optimiser walks into a local minimum and stays.  This is
    why "formulate" is doing work in the TISS learning outcome — the model, the
    parameterisation and `p0` are the part you get marked on.
    """
    rng = np.random.default_rng(seed)
    t = np.linspace(0.0, 3.0, 60)
    truth = (2.0, 3.0, 0.5)
    y = sine_model(t, *truth) + 0.05 * rng.standard_normal(t.size)

    out = {}
    for omega0 in (1.0, 2.0, 3.0):
        popt, _ = curve_fit(sine_model, t, y, p0=[1.0, omega0, 0.0], maxfev=20000)
        out[omega0] = float(((sine_model(t, *popt) - y) ** 2).sum())
    return out


# Task 4 (ours; the point of SPL 2.7 "Optimization with constraints", written as
# an exercise because the book's version is a figure rather than a problem).


def constrained_box(x0=(2.0, 2.0)) -> tuple[np.ndarray, float]:
    r"""Minimise $(x-3)^2 + (y-2)^2$ subject to $x + y \le 2$, $x, y \ge 0$.

    Written as SLSQP wants it: an ``ineq`` constraint is satisfied where
    ``fun(x) >= 0``, so the budget $x + y \le 2$ becomes $2 - x - y \ge 0$.
    Getting that sign backwards is the single most common constraint mistake.
    """
    r = minimize(lambda v: (v[0] - 3.0) ** 2 + (v[1] - 2.0) ** 2, np.array(x0),
                 method="SLSQP", bounds=[(0, None), (0, None)],
                 constraints=[{"type": "ineq", "fun": lambda v: 2.0 - v[0] - v[1]}])
    return r.x, float(r.fun)


# ------------------------------------------------------------- interfacing
# Task 5 (after SPL 2.8, exercise "Ctypes"): call a C function from the system
# maths library, and see what happens when the signature is left undeclared.
# libm is used instead of a compiled example so nothing has to be built; the
# course's own compiled version is ../../py/interfaces.py against ../../c.


def libm() -> ctypes.CDLL:
    return ctypes.CDLL(ctypes.util.find_library("m") or None)


def undeclared_vs_declared(value: float = 4.0) -> tuple[object, float]:
    """Return sqrt(value) as ctypes gives it (a) undeclared and (b) declared.

    Undeclared, ctypes assumes the C signature ``int f(int)``: the double
    argument is passed in the wrong register class and the return value is
    reinterpreted as an int.  There is no exception — only a wrong number.
    """
    raw = libm().sqrt(ctypes.c_double(value))

    lib = libm()
    lib.sqrt.argtypes = [ctypes.c_double]
    lib.sqrt.restype = ctypes.c_double
    return raw, float(lib.sqrt(value))


# Task 6 (ours; the memory-layout half of SPL 2.8 and of note 09).


def column_major_handoff(a: np.ndarray) -> dict[str, object]:
    """What a row-major array looks like to a column-major callee.

    Fortran, Julia and LAPACK index column-first.  A transpose is free — it only
    swaps the strides — so ``a.T`` is already F-contiguous and can be handed over
    without a copy; ``np.asfortranarray(a)`` copies and gives the *same* logical
    array in column-major order instead.
    """
    return {
        "c_contiguous": bool(a.flags["C_CONTIGUOUS"]),
        "transpose_is_f_contiguous": bool(a.T.flags["F_CONTIGUOUS"]),
        "transpose_shares_memory": bool(np.shares_memory(a, a.T)),
        "asfortranarray_copies": not np.shares_memory(a, np.asfortranarray(a)),
        "strides": a.strides,
        "transpose_strides": a.T.strides,
    }


def main() -> None:
    print("1. gradient pays for itself (nfev):")
    for method, d in gradient_pays_for_itself().items():
        without = d["nfev_without_jac"]
        print(f"   {method:<10} with jac {d['nfev_with_jac']:>3}  without "
              f"{'refuses' if without < 0 else without}")
    print("2. flat minimum  (|x - x*|, f):")
    for method, (dist, val) in flat_minimum_comparison().items():
        print(f"   {method:<12} {dist:10.3e}  {val:10.3e}")
    print("3. curve_fit SSE by initial omega (truth 3.0):")
    for omega0, sse in curve_fit_needs_the_right_frequency().items():
        print(f"   p0 omega = {omega0}  ->  SSE {sse:8.3f}")
    x, fval = constrained_box()
    print(f"4. constrained: x = {np.round(x, 4)}, f = {fval:.4f}")
    raw, declared = undeclared_vs_declared()
    print(f"5. ctypes sqrt(4.0): undeclared {raw!r}, declared {declared}")
    print("6. layout:", column_major_handoff(np.ones((2, 3))))


if __name__ == "__main__":
    main()
