"""Quantum Fourier transform as a circuit of Hadamards, controlled phases and swaps (N&C 5.1, KLM 7.1).

Belongs to the Part C note on the QFT and phase estimation (C06).

QFT |x> = N^{-1/2} sum_y exp(2 pi i x y / N) |y>,  N = 2^n.  Product form
(N&C eq. 5.4): with x = x_0 x_1 ... x_{n-1} big-endian the output is
  (|0> + e^{2 pi i 0.x_{n-1}} |1>) ... (|0> + e^{2 pi i 0.x_0 x_1...x_{n-1}} |1>) / 2^{n/2},
so H on qubit j followed by controlled phases pi/2^{m-j} from qubits m > j builds the
factors in reversed order; the final swaps restore big-endian order.
Gate count: n Hadamards + n(n-1)/2 controlled phases + floor(n/2) swaps = O(n^2).

Implements: qft (in place on a register, with inverse flag), qft_matrix (dense reference).
"""
import numpy as np

from sim import Register


def qft(reg, qubits, inverse=False, do_swaps=True):
    """Apply the QFT (or its inverse) to `qubits` (MSB first) of `reg`, in place."""
    qubits = list(qubits)
    n = len(qubits)
    sign = -1 if inverse else 1
    ops = []
    for j in range(n):
        ops.append(("h", qubits[j]))
        for m in range(j + 1, n):
            ops.append(("cp", sign * np.pi / 2 ** (m - j), qubits[m], qubits[j]))
    swaps = [("swap", qubits[j], qubits[n - 1 - j]) for j in range(n // 2)] if do_swaps else []
    seq = ops + swaps if not inverse else swaps + ops[::-1]   # inverse: reversed, conjugated
    for op in seq:
        if op[0] == "h":
            reg.h(op[1])
        elif op[0] == "cp":
            reg.cp(op[1], op[2], op[3])
        else:
            reg.swap(op[1], op[2])
    return reg


def qft_matrix(n):
    """Dense N x N reference: F[y, x] = exp(2 pi i x y / N) / sqrt(N)."""
    N = 2 ** n
    x = np.arange(N)
    return np.exp(2j * np.pi * np.outer(x, x) / N) / np.sqrt(N)


if __name__ == "__main__":
    n = 3
    for x in (0, 1, 5):
        reg = Register(n)
        reg.state[:] = 0
        reg.state[x] = 1
        qft(reg, range(n))
        print(f"QFT|{x:0{n}b}> = {reg}")
    reg = Register(n, np.exp(2j * np.pi * np.arange(8) * 3 / 8) / np.sqrt(8))   # a Fourier basis state
    print("inverse QFT of the 8-th-root-of-unity phase ramp with frequency 3:", qft(reg, range(n), inverse=True))
