"""Two-party computation for boolean circuits, twice: Yao's garbled circuits
(garbler + evaluator, inputs of the evaluator via oblivious transfer) and GMW
(XOR secret sharing, AND gates via 1-out-of-4 OT). The OT is the ElGamal-style
1-out-of-n protocol of [S4 sec. 11.6.1] over a prime-order group.

EDUCATIONAL TOY CODE (192.115 Advanced Cryptography, TU Wien). Semi-honest
only. Garbling uses SHA-256 as the double-encryption key derivation and the
'efficiently verifiable range' of [S13 sec. 3.1] (a 16-byte zero tag) to
recognise the right row; no point-and-permute, no free-XOR, no half-gates.
Group: groups.MEDIUM (128-bit, far too small for real use).
"""
from __future__ import annotations

import hashlib
import itertools
import secrets

from groups import MEDIUM, SchnorrGroup

K = 16  # label length in bytes (kappa = 128 bits)

OPS = {"AND": (2, lambda a, b: a & b), "XOR": (2, lambda a, b: a ^ b),
       "OR": (2, lambda a, b: a | b), "NOT": (1, lambda a, b=0: 1 - a)}

# 2-bit 'millionaires': out = [x > y], x = (x1 x0) Alice, y = (y1 y0) Bob.
COMPARATOR = {
    "alice": ["x1", "x0"], "bob": ["y1", "y0"], "out": "gt",
    "gates": [("ny1", "NOT", "y1", None), ("g1", "AND", "x1", "ny1"),
              ("d1", "XOR", "x1", "y1"), ("e1", "NOT", "d1", None),
              ("ny0", "NOT", "y0", None), ("g2", "AND", "x0", "ny0"),
              ("g3", "AND", "e1", "g2"), ("gt", "OR", "g1", "g3")],
}


def eval_plain(circ, bits: dict) -> int:
    w = dict(bits)
    for out, op, a, b in circ["gates"]:
        ar, fn = OPS[op]
        w[out] = fn(w[a]) if ar == 1 else fn(w[a], w[b])
    return w[circ["out"]]


def _kdf(*parts: bytes) -> bytes:
    return hashlib.sha256(b"".join(parts)).digest()


def _xor(a: bytes, b: bytes) -> bytes:
    return bytes(x ^ y for x, y in zip(a, b))


# --- oblivious transfer [S4 sec. 11.6.1] -------------------------------------

def ot_sender_1(G: SchnorrGroup):
    beta = G.rand_scalar()
    return beta, G.exp(G.g, beta)                     # v = g^beta to receiver


def ot_receiver_1(G: SchnorrGroup, v: int, i: int):
    alpha = G.rand_scalar()
    return alpha, G.mul(G.exp(G.g, alpha), G.inv(G.exp(v, i)))   # u = g^a v^{-i}


def ot_sender_2(G: SchnorrGroup, beta: int, v: int, u: int, msgs: list[bytes]):
    """c_j = m_j xor H(v, (u v^j)^beta): u v^j = g^alpha exactly for j = i."""
    out = []
    for j, m in enumerate(msgs):
        w = G.exp(G.mul(u, G.exp(v, j)), beta)
        pad = _kdf(b"ot", str(v).encode(), str(w).encode(), bytes([j]))
        out.append(_xor(m, pad[:len(m)]))
    return out


def ot_receiver_2(G: SchnorrGroup, alpha: int, v: int, i: int, cts: list[bytes]) -> bytes:
    w = G.exp(v, alpha)
    pad = _kdf(b"ot", str(v).encode(), str(w).encode(), bytes([i]))
    return _xor(cts[i], pad[:len(cts[i])])


def ot(msgs: list[bytes], i: int, G: SchnorrGroup = MEDIUM) -> bytes:
    """Run the 3-message 1-out-of-n OT; returns what the receiver learns."""
    beta, v = ot_sender_1(G)
    alpha, u = ot_receiver_1(G, v, i)
    return ot_receiver_2(G, alpha, v, i, ot_sender_2(G, beta, v, u, msgs))


# --- Yao's garbled circuit [S12], [S13], [S4 sec. 23.3] ----------------------

def garble(circ):
    """Two random labels per wire (label[w][bit]); per gate a shuffled table of
    Enc_{k_a}(Enc_{k_b}(k_out || 0^16)) realised as KDF(k_a, k_b, gate) xor."""
    wires = set(circ["alice"] + circ["bob"]) | {g[0] for g in circ["gates"]}
    lab = {w: (secrets.token_bytes(K), secrets.token_bytes(K)) for w in wires}
    tables = []
    for gid, (out, op, a, b) in enumerate(circ["gates"]):
        ar, fn = OPS[op]
        rows = []
        for bits in itertools.product((0, 1), repeat=ar):
            v = fn(*bits)
            keys = [lab[a][bits[0]]] + ([lab[b][bits[1]]] if ar == 2 else [])
            pad = _kdf(*keys, gid.to_bytes(4, "big"))
            rows.append(_xor(pad, lab[out][v] + bytes(K)))
        secrets.SystemRandom().shuffle(rows)          # hide which row is which
        tables.append(rows)
    decode = {lab[circ["out"]][0]: 0, lab[circ["out"]][1]: 1}
    return lab, tables, decode


def evaluate(circ, tables, decode, input_labels: dict) -> int:
    """Evaluator holds one label per wire; exactly one row per gate decrypts to
    something ending in 16 zero bytes (else: the elusive-range event, prob
    ~ 2^-128 per wrong row)."""
    w = dict(input_labels)
    for gid, (out, op, a, b) in enumerate(circ["gates"]):
        keys = [w[a]] + ([w[b]] if OPS[op][0] == 2 else [])
        pad = _kdf(*keys, gid.to_bytes(4, "big"))
        hits = [_xor(pad, row) for row in tables[gid]]
        hits = [h[:K] for h in hits if h[K:] == bytes(K)]
        if len(hits) != 1:
            raise RuntimeError("garbled table corrupt")
        w[out] = hits[0]
    return decode[w[circ["out"]]]


def yao(circ, x: dict, y: dict) -> int:
    """Alice (garbler, input x) and Bob (evaluator, input y)."""
    lab, tables, decode = garble(circ)                          # Alice
    inputs = {wname: lab[wname][x[wname]] for wname in circ["alice"]}   # sent in clear
    for wname in circ["bob"]:                                   # one OT per Bob bit
        inputs[wname] = ot([lab[wname][0], lab[wname][1]], y[wname])
    return evaluate(circ, tables, decode, inputs)               # Bob, then shares result


# --- GMW with 1-out-of-4 OT [S11], [S7 sec. 4.5] ------------------------------

def gmw_and(a1: int, b1: int, a2: int, b2: int) -> tuple[int, int]:
    """Shares (a1, b1) at P1, (a2, b2) at P2 of a = a1^a2, b = b1^b2.
    P1 picks r, offers T[2a2' + b2'] = r ^ ((a1^a2')(b1^b2')) for all four
    guesses; P2 selects its real (a2, b2) by OT. Output shares (r, T)."""
    r = secrets.randbits(1)
    table = [bytes([r ^ ((a1 ^ u) & (b1 ^ v))]) for u in (0, 1) for v in (0, 1)]
    return r, ot(table, 2 * a2 + b2)[0]


def gmw(circ, x: dict, y: dict) -> int:
    s1, s2 = {}, {}
    for wname in circ["alice"]:                     # Alice shares her bits
        r = secrets.randbits(1)
        s1[wname], s2[wname] = x[wname] ^ r, r
    for wname in circ["bob"]:
        r = secrets.randbits(1)
        s1[wname], s2[wname] = r, y[wname] ^ r
    for out, op, a, b in circ["gates"]:
        if op == "XOR":
            s1[out], s2[out] = s1[a] ^ s1[b], s2[a] ^ s2[b]      # local
        elif op == "NOT":
            s1[out], s2[out] = 1 - s1[a], s2[a]                  # P1 flips
        elif op in ("AND", "OR"):
            c1, c2 = gmw_and(s1[a], s1[b], s2[a], s2[b])
            if op == "OR":                                       # a|b = a^b^ab
                c1, c2 = c1 ^ s1[a] ^ s1[b], c2 ^ s2[a] ^ s2[b]
            s1[out], s2[out] = c1, c2
    return s1[circ["out"]] ^ s2[circ["out"]]         # exchange output shares


def _bits(v: int, names: list[str]) -> dict:
    return {n: (v >> (len(names) - 1 - k)) & 1 for k, n in enumerate(names)}


if __name__ == "__main__":
    c = COMPARATOR
    msgs = [b"zero", b"one!", b"two.", b"3333"]
    print("1-out-of-4 OT, receiver picks 2:", ot(msgs, 2))
    print(" x  y | x>y  yao  gmw")
    for xv in range(4):
        for yv in range(4):
            xb, yb = _bits(xv, c["alice"]), _bits(yv, c["bob"])
            print(f" {xv}  {yv} |  {int(xv > yv)}    {yao(c, xb, yb)}    {gmw(c, xb, yb)}")
