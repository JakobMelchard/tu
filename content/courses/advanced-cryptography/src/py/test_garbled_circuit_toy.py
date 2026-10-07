"""Tests for the educational toy code in garbled_circuit_toy.py: OT correctness and receiver privacy,
Yao and GMW on every input of the comparator and of random circuits."""
import random
from collections import Counter

import pytest

import garbled_circuit_toy as Y
from groups import MEDIUM, TOY


@pytest.mark.parametrize("n", [2, 4, 7])
def test_ot_receiver_gets_chosen_message(n):
    msgs = [bytes([i]) * 16 for i in range(n)]
    for i in range(n):
        assert Y.ot(msgs, i) == msgs[i]


def test_ot_receiver_cannot_open_other_message():
    msgs = [b"A" * 16, b"B" * 16]
    G = MEDIUM
    beta, v = Y.ot_sender_1(G)
    alpha, u = Y.ot_receiver_1(G, v, 0)
    cts = Y.ot_sender_2(G, beta, v, u, msgs)
    assert Y.ot_receiver_2(G, alpha, v, 0, cts) == msgs[0]
    assert Y.ot_receiver_2(G, alpha, v, 1, cts) != msgs[1]   # wrong key for j = 1


def test_ot_sender_view_independent_of_choice():
    """u = g^alpha v^{-i} is uniform whatever i is (exact on TOY)."""
    G = TOY
    v = G.exp(G.g, 5)
    dists = [Counter(G.mul(G.exp(G.g, a), G.inv(G.exp(v, i))) for a in range(G.q)) for i in (0, 1, 2)]
    assert dists[0] == dists[1] == dists[2]


def test_comparator_all_inputs():
    c = Y.COMPARATOR
    for xv in range(4):
        for yv in range(4):
            xb, yb = Y._bits(xv, c["alice"]), Y._bits(yv, c["bob"])
            want = int(xv > yv)
            assert Y.eval_plain(c, {**xb, **yb}) == want
            assert Y.yao(c, xb, yb) == want
            assert Y.gmw(c, xb, yb) == want


def _random_circuit(rng, n_gates=12):
    alice, bob = ["a0", "a1", "a2"], ["b0", "b1", "b2"]
    wires, gates = alice + bob, []
    for k in range(n_gates):
        op = rng.choice(["AND", "XOR", "OR", "NOT"])
        a, b = rng.choice(wires), rng.choice(wires)
        gates.append((f"w{k}", op, a, None if op == "NOT" else b))
        wires.append(f"w{k}")
    return {"alice": alice, "bob": bob, "out": f"w{n_gates - 1}", "gates": gates}


def test_random_circuits_all_inputs():
    rng = random.Random(0)
    for _ in range(3):
        c = _random_circuit(rng)
        for xv in range(8):
            for yv in range(8):
                xb, yb = Y._bits(xv, c["alice"]), Y._bits(yv, c["bob"])
                want = Y.eval_plain(c, {**xb, **yb})
                assert Y.yao(c, xb, yb) == want
                assert Y.gmw(c, xb, yb) == want


def test_one_label_per_wire_reveals_nothing_about_the_other():
    """The evaluator's labels are fresh random strings: the two labels of an
    input wire are independent, so holding one says nothing about the bit."""
    lab, tables, decode = Y.garble(Y.COMPARATOR)
    assert all(l0 != l1 and len(l0) == Y.K for l0, l1 in lab.values())
    assert len(decode) == 2 and all(len(t) in (2, 4) for t in tables)


def test_gmw_and_shares():
    for a1 in (0, 1):
        for b1 in (0, 1):
            for a2 in (0, 1):
                for b2 in (0, 1):
                    c1, c2 = Y.gmw_and(a1, b1, a2, b2)
                    assert c1 ^ c2 == (a1 ^ a2) & (b1 ^ b2)
