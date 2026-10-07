"""Small statevector simulator used by every module in the quantum package.

Belongs to the Part C quantum notes (simulator / circuit model note, C01).

CONVENTION (big-endian, used everywhere in this package):
  qubit 0 is the MOST significant bit, i.e. the leftmost symbol in a ket.
  Basis index of |b_0 b_1 ... b_{n-1}> is  sum_q b_q * 2**(n-1-q).
  state.reshape((2,)*n)[b_0, b_1, ..., b_{n-1}] is the amplitude of that ket,
  so tensor axis q == qubit q.  Example, n=2: index 1 == |01> == qubit 1 set.
  Multi-qubit gates / permutations take a `targets` list; the gate's own
  bits are ordered like that list (targets[0] is the gate's MSB).

Implements: Register (apply_gate, apply_controlled, apply_diagonal,
apply_permutation, apply_controlled_permutation, apply_function, measure,
measure_all, probabilities, partial_trace, expectation, gate shorthands
h x y z s t rx ry rz p cx cz ccx cp swap), gate matrices I X Y Z H S T,
Rx Ry Rz phase CNOT CZ SWAP TOFFOLI, helpers kron, controlled, ket,
fidelity, permutation_matrix.
"""
import numpy as np

# ---------------------------------------------------------------- gates
I = np.eye(2, dtype=complex)
X = np.array([[0, 1], [1, 0]], dtype=complex)
Y = np.array([[0, -1j], [1j, 0]], dtype=complex)
Z = np.array([[1, 0], [0, -1]], dtype=complex)
H = np.array([[1, 1], [1, -1]], dtype=complex) / np.sqrt(2)
S = np.diag([1, 1j]).astype(complex)
T = np.diag([1, np.exp(1j * np.pi / 4)])


def Rx(theta):
    """exp(-i theta X / 2)."""
    c, s = np.cos(theta / 2), np.sin(theta / 2)
    return np.array([[c, -1j * s], [-1j * s, c]])


def Ry(theta):
    """exp(-i theta Y / 2)."""
    c, s = np.cos(theta / 2), np.sin(theta / 2)
    return np.array([[c, -s], [s, c]], dtype=complex)


def Rz(theta):
    """exp(-i theta Z / 2)."""
    return np.diag([np.exp(-1j * theta / 2), np.exp(1j * theta / 2)])


def phase(theta):
    """diag(1, e^{i theta}); phase(pi)=Z, phase(pi/2)=S, phase(pi/4)=T."""
    return np.diag([1, np.exp(1j * theta)])


def kron(*mats):
    out = np.array([[1]], dtype=complex)
    for m in mats:
        out = np.kron(out, m)
    return out


def controlled(U, num_controls=1):
    """Dense controlled-U: identity except on the block where all controls are 1."""
    d = U.shape[0]
    n = d * 2 ** num_controls
    out = np.eye(n, dtype=complex)
    out[n - d:, n - d:] = U
    return out


CNOT = controlled(X)
CZ = controlled(Z)
SWAP = np.array([[1, 0, 0, 0], [0, 0, 1, 0], [0, 1, 0, 0], [0, 0, 0, 1]], dtype=complex)
TOFFOLI = controlled(X, 2)


def permutation_matrix(perm):
    """Dense unitary of the classical bijection x -> perm[x]  (column x has a 1 in row perm[x])."""
    n = len(perm)
    P = np.zeros((n, n), dtype=complex)
    P[np.asarray(perm), np.arange(n)] = 1
    return P


def ket(bits, n=None):
    """Basis state from an int (needs n) or from a bit-string/sequence like '011'."""
    if isinstance(bits, (int, np.integer)):
        idx = int(bits)
    else:
        bits = [int(b) for b in bits]
        n = len(bits)
        idx = int("".join(map(str, bits)), 2)
    v = np.zeros(2 ** n, dtype=complex)
    v[idx] = 1
    return v


def fidelity(a, b):
    """|<a|b>|^2 for two statevectors, or <a|rho|a> if one argument is a density matrix."""
    a, b = np.asarray(a), np.asarray(b)
    if a.ndim == 2 and b.ndim == 1:
        a, b = b, a
    if b.ndim == 2:
        return float(np.real(np.vdot(a, b @ a)))
    return float(abs(np.vdot(a, b)) ** 2)


# ------------------------------------------------------------- register
class Register:
    """n-qubit pure state, stored as a complex vector of length 2**n (see convention above)."""

    def __init__(self, n, state=None):
        self.n = n
        if state is None:
            self.state = np.zeros(2 ** n, dtype=complex)
            self.state[0] = 1.0
        else:
            self.state = np.array(state, dtype=complex).reshape(2 ** n)

    def copy(self):
        return Register(self.n, self.state)

    # -- internals: tensor view restricted to the slice where all controls are 1
    def _view(self, controls=()):
        psi = self.state.reshape((2,) * self.n)
        idx = tuple(1 if q in controls else slice(None) for q in range(self.n))
        # axis of qubit q inside the sliced view (control axes disappear)
        axis = {q: q - sum(c < q for c in controls) for q in range(self.n) if q not in controls}
        return psi, idx, axis

    @staticmethod
    def _apply_to_axes(sub, U, axes):
        """Contract the k-qubit gate U into tensor `sub` on the given axes (no big matrix)."""
        k = len(axes)
        Ut = np.asarray(U, dtype=complex).reshape((2,) * (2 * k))
        out = np.tensordot(Ut, sub, axes=(list(range(k, 2 * k)), list(axes)))
        return np.moveaxis(out, list(range(k)), list(axes))  # put target axes back in place

    # -- gates
    def apply_gate(self, U, targets):
        """Apply the 2^k x 2^k unitary U to qubits `targets` (any order, targets[0] = gate MSB)."""
        targets = [targets] if isinstance(targets, (int, np.integer)) else list(targets)
        psi = self.state.reshape((2,) * self.n)
        self.state = np.ascontiguousarray(self._apply_to_axes(psi, U, targets)).reshape(-1)
        return self

    def apply_controlled(self, U, controls, targets):
        """Apply U to `targets` only on the subspace where every qubit in `controls` is 1."""
        controls = [controls] if isinstance(controls, (int, np.integer)) else list(controls)
        targets = [targets] if isinstance(targets, (int, np.integer)) else list(targets)
        if not controls:
            return self.apply_gate(U, targets)
        psi, idx, axis = self._view(controls)
        sub = psi[idx]
        psi[idx] = self._apply_to_axes(sub, U, [axis[t] for t in targets])
        return self

    def apply_diagonal(self, diag, qubits, controls=()):
        """Multiply the amplitude of |..x..> by diag[x], x read off `qubits` (MSB first)."""
        qubits = [qubits] if isinstance(qubits, (int, np.integer)) else list(qubits)
        psi, idx, axis = self._view(list(controls))
        k = len(qubits)
        d = np.asarray(diag, dtype=complex).reshape((2,) * k)
        ax = [axis[q] for q in qubits]
        d = d.transpose(np.argsort(ax))          # axes in increasing sub-view axis order
        shape = [1] * (self.n - len(controls))
        for a in ax:
            shape[a] = 2
        psi[idx] = psi[idx] * d.reshape(shape)
        return self

    def apply_permutation(self, perm, qubits, controls=()):
        """Classical bijection on the sub-register `qubits`:  |x> -> |perm[x]|  (other qubits untouched).

        Pure index permutation of the amplitude array; never builds a 2^n x 2^n matrix.
        Optional `controls`: act only where all control qubits are 1.
        """
        qubits = [qubits] if isinstance(qubits, (int, np.integer)) else list(qubits)
        perm = np.asarray(perm)
        psi, idx, axis = self._view(list(controls))
        sub = psi[idx]
        k = len(qubits)
        ax = [axis[q] for q in qubits]
        front = np.moveaxis(sub, ax, list(range(k)))  # view with the sub-register axes first
        rows = np.ascontiguousarray(front).reshape(2 ** k, -1)
        new = np.empty_like(rows)
        new[perm] = rows                               # amplitude of |x> moves to |perm[x]>
        psi[idx] = np.moveaxis(new.reshape(front.shape), list(range(k)), ax)
        return self

    def apply_controlled_permutation(self, perm, controls, qubits):
        return self.apply_permutation(perm, qubits, controls=controls)

    def apply_function(self, f, qubits, controls=()):
        """apply_permutation with perm[x] = f(x) for a bijective python callable f on 0..2^k-1."""
        perm = [f(x) for x in range(2 ** len(qubits))]
        return self.apply_permutation(perm, qubits, controls)

    # -- single/two/three qubit shorthands
    def h(self, q): return self.apply_gate(H, [q])
    def x(self, q): return self.apply_gate(X, [q])
    def y(self, q): return self.apply_gate(Y, [q])
    def z(self, q): return self.apply_gate(Z, [q])
    def s(self, q): return self.apply_gate(S, [q])
    def t(self, q): return self.apply_gate(T, [q])
    def rx(self, theta, q): return self.apply_gate(Rx(theta), [q])
    def ry(self, theta, q): return self.apply_gate(Ry(theta), [q])
    def rz(self, theta, q): return self.apply_gate(Rz(theta), [q])
    def p(self, theta, q): return self.apply_gate(phase(theta), [q])
    def cx(self, c, t): return self.apply_controlled(X, [c], [t])
    def cz(self, c, t): return self.apply_controlled(Z, [c], [t])
    def ccx(self, a, b, t): return self.apply_controlled(X, [a, b], [t])
    def cp(self, theta, c, t): return self.apply_controlled(phase(theta), [c], [t])
    def swap(self, a, b): return self.apply_gate(SWAP, [a, b])

    # -- read-out
    def probabilities(self):
        return np.abs(self.state) ** 2

    def amplitude(self, bits):
        return self.state[int("".join(str(int(b)) for b in bits), 2)]

    def measure(self, qubits, rng):
        """Projective Z measurement of `qubits`; returns their bits (in the given order) and collapses."""
        qubits = [qubits] if isinstance(qubits, (int, np.integer)) else list(qubits)
        k = len(qubits)
        prob = self.probabilities().reshape((2,) * self.n)
        marg = np.moveaxis(prob, qubits, list(range(k))).reshape(2 ** k, -1).sum(axis=1)
        outcome = int(rng.choice(2 ** k, p=marg / marg.sum()))
        bits = [(outcome >> (k - 1 - j)) & 1 for j in range(k)]
        idx = [slice(None)] * self.n
        for q, b in zip(qubits, bits):
            idx[q] = b
        psi = self.state.reshape((2,) * self.n)
        new = np.zeros_like(psi)
        new[tuple(idx)] = psi[tuple(idx)]
        self.state = new.reshape(-1) / np.sqrt(marg[outcome])
        return bits

    def measure_all(self, rng):
        return self.measure(list(range(self.n)), rng)

    def sample(self, rng, shots):
        """Sample basis-state indices without collapsing (repeated measurement of fresh copies)."""
        return rng.choice(2 ** self.n, size=shots, p=self.probabilities())

    def partial_trace(self, keep):
        """Reduced density matrix of the qubits in `keep` (rows/cols ordered like `keep`, MSB first)."""
        keep = [keep] if isinstance(keep, (int, np.integer)) else list(keep)
        psi = self.state.reshape((2,) * self.n)
        m = np.moveaxis(psi, keep, list(range(len(keep)))).reshape(2 ** len(keep), -1)
        return m @ m.conj().T

    def expectation(self, pauli_string):
        """<psi| P |psi> for a string like 'XZIY' (character q acts on qubit q)."""
        assert len(pauli_string) == self.n
        phi = self.copy()
        for q, c in enumerate(pauli_string):
            if c != "I":
                phi.apply_gate({"X": X, "Y": Y, "Z": Z}[c], [q])
        return float(np.real(np.vdot(self.state, phi.state)))

    def __repr__(self):
        terms = [f"{a:.3f}|{i:0{self.n}b}>" for i, a in enumerate(self.state) if abs(a) > 1e-9]
        return " + ".join(terms) if terms else "0"


if __name__ == "__main__":
    reg = Register(3)
    reg.h(0).cx(0, 1).cx(1, 2)                     # GHZ state
    print("GHZ:", reg)
    print("probabilities:", np.round(reg.probabilities(), 3))
    print("<ZZZ> =", reg.expectation("ZZZ"), " <XXX> =", reg.expectation("XXX"))
    print("reduced state of qubit 0:\n", np.round(reg.partial_trace([0]).real, 3))
    rng = np.random.default_rng(1)
    print("10 GHZ measurements:", ["".join(map(str, reg.copy().measure_all(rng))) for _ in range(10)])
    # classical function x -> 3x mod 8 on a 3-qubit register (a bijection since gcd(3,8)=1)
    reg = Register(3, ket("001"))
    reg.apply_function(lambda v: 3 * v % 8, [0, 1, 2])
    print("|1> under x -> 3x mod 8:", reg)
