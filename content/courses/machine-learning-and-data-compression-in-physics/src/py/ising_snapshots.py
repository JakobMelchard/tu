"""2D Ising snapshots: the synthetic data set for notes 04 and 07.

Checkerboard Metropolis on a batch of independent L x L periodic lattices, one
temperature per chain (J = k_B = 1). Cross-checked against Onsager's exact
magnetisation and internal energy [S20].

    H = -sum_<ij> s_i s_j,  T_c = 2 / ln(1 + sqrt 2) = 2.2692 ...

Run `python ising_snapshots.py` for a table of <|m|>, <e> vs the exact values.
"""
from __future__ import annotations

import numpy as np
from scipy.special import ellipk

T_C = 2.0 / np.log1p(np.sqrt(2.0))


def energy_per_spin(s: np.ndarray) -> np.ndarray:
    """e = -(1/N) sum_i s_i (s_right + s_down) for a batch (B, L, L)."""
    s = s.astype(np.float64)
    bonds = s * np.roll(s, -1, axis=-1) + s * np.roll(s, -1, axis=-2)
    return -bonds.reshape(s.shape[0], -1).mean(axis=1)


def magnetisation(s: np.ndarray) -> np.ndarray:
    """m = (1/N) sum_i s_i per configuration."""
    return s.reshape(s.shape[0], -1).astype(np.float64).mean(axis=1)


def bond_features(s: np.ndarray) -> np.ndarray:
    """All nearest-neighbour products s_i s_{i+x}, s_i s_{i+y}, flattened (B, 2N).

    The energy is exactly -(1/N) times their sum: linear in the bond features.
    """
    s = s.astype(np.float64)
    right = s * np.roll(s, -1, axis=-1)
    down = s * np.roll(s, -1, axis=-2)
    return np.concatenate([right.reshape(len(s), -1), down.reshape(len(s), -1)], axis=1)


def _sweep(s: np.ndarray, beta: np.ndarray, masks, rng: np.random.Generator) -> None:
    """One Metropolis sweep: update the two checkerboard sublattices in turn.

    Sites of one colour have no neighbour of the same colour, so all of them can
    be updated in parallel without violating detailed balance.
    """
    b = beta[:, None, None]
    for mask in masks:
        nn = (np.roll(s, 1, -1) + np.roll(s, -1, -1) + np.roll(s, 1, -2) + np.roll(s, -1, -2))
        dE = 2.0 * s * nn                      # energy change of flipping s_i
        accept = rng.random(s.shape) < np.exp(-b * np.clip(dE, 0, None))
        s[:] = np.where(accept & mask, -s, s)


def sample_ising(L: int, temps, n_per_T: int, n_therm: int = 400,
                 rng: np.random.Generator | None = None):
    """Return (configs int8 (n, L, L), T (n,)) with n = len(temps) * n_per_T.

    One independent chain per snapshot. Chains below T_c start ordered (random
    global sign), above T_c random: a cold random start freezes into stripe
    domains that Metropolis does not remove in n_therm sweeps.
    """
    rng = np.random.default_rng(0) if rng is None else rng
    temps = np.repeat(np.asarray(temps, dtype=np.float64), n_per_T)
    B = len(temps)
    s = rng.choice(np.array([-1.0, 1.0]), size=(B, L, L))
    cold = temps < T_C
    sign = rng.choice(np.array([-1.0, 1.0]), size=B)
    s[cold] = sign[cold, None, None]
    ij = np.add.outer(np.arange(L), np.arange(L)) % 2
    masks = (ij == 0, ij == 1)
    beta = 1.0 / temps
    for _ in range(n_therm):
        _sweep(s, beta, masks, rng)
    return s.astype(np.int8), temps


def onsager_magnetisation(T) -> np.ndarray:
    """Spontaneous magnetisation (1 - sinh(2/T)^-4)^(1/8) below T_c, 0 above."""
    T = np.asarray(T, dtype=np.float64)
    with np.errstate(divide="ignore", invalid="ignore"):
        m = (1.0 - np.sinh(2.0 / T) ** -4) ** 0.125
    return np.where(T < T_C, m, 0.0)


def onsager_energy(T) -> np.ndarray:
    """Internal energy per spin of the infinite lattice.

    u = -coth(2K) [1 + (2/pi)(2 tanh^2(2K) - 1) K(k^2)],  k = 2 sinh 2K / cosh^2 2K,
    K = 1/T, K(.) the complete elliptic integral with parameter m = k^2.
    """
    K = 1.0 / np.asarray(T, dtype=np.float64)
    k = 2.0 * np.sinh(2 * K) / np.cosh(2 * K) ** 2
    return -1.0 / np.tanh(2 * K) * (1 + 2 / np.pi * (2 * np.tanh(2 * K) ** 2 - 1) * ellipk(k ** 2))


def demo() -> None:
    temps = [1.5, 2.0, 2.27, 2.6, 3.5]
    s, T = sample_ising(16, temps, 100, n_therm=500)
    m, e = np.abs(magnetisation(s)), energy_per_spin(s)
    print(f"2D Ising, L=16, 100 chains per T, T_c = {T_C:.4f}")
    print(f"{'T':>5} {'<|m|>':>7} {'Onsager':>8} {'<e>':>8} {'Onsager':>8}")
    for t in temps:
        sel = T == t
        print(f"{t:5.2f} {m[sel].mean():7.3f} {float(onsager_magnetisation(t)):8.3f} "
              f"{e[sel].mean():8.3f} {float(onsager_energy(t)):8.3f}")
    print("near T_c the finite lattice deviates (finite-size rounding); far from it they agree.")


if __name__ == "__main__":
    demo()
