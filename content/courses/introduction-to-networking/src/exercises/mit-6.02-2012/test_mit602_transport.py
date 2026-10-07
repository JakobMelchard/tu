"""Every test asserts against a number **MIT published** in the solution PDF of
the corresponding 6.02 Fall 2012 tutorial [S34], read from
`PUBLISHED_ANSWERS`.  That is the point of using this source: it is the only
external answer key in the tree.  191.030 itself has none [S2].
"""
import pytest

from mit602_transport import (
    PUBLISHED_ANSWERS, bandwidth_delay_product, chain_rtt,
    expected_transmissions, link_utilisation, optimal_window,
    out_of_order_buffer, path_loss, seq_wraparound_capacity,
    stop_and_wait_throughput, window_throughput,
)

A = PUBLISHED_ANSWERS


def test_t11_chain_window_and_utilisation():
    # A-B-C-D-E, one packet per second per link.
    rtt = chain_rtt(4)
    assert rtt == A[("t11", "1A")]
    assert stop_and_wait_throughput(rtt) == pytest.approx(A[("t11", "1B")])
    w, thr = A[("t11", "1C")]
    assert optimal_window(rtt) == w
    assert window_throughput(w, rtt) == pytest.approx(thr)
    thr4, util = A[("t11", "1D")]
    assert window_throughput(4, rtt) == pytest.approx(thr4)
    assert link_utilisation(window_throughput(4, rtt), 1.0) == pytest.approx(util)


def test_t11_receiver_buffer_with_every_odd_packet_dropped():
    assert out_of_order_buffer(window=8, rtt=8, timeout=40, at_time=35) == 7


def test_t11_sequence_number_wraparound():
    # 1000-byte packets, 100 ms RTT, 8-bit sequence numbers.
    assert stop_and_wait_throughput(0.1, packet=1000) == pytest.approx(A[("t11", "2A")])
    assert bandwidth_delay_product(1e6, 0.1) == pytest.approx(A[("t11", "2B")])
    assert seq_wraparound_capacity(8, 1000, 0.1) == pytest.approx(A[("t11", "2C")])


def test_t11_loss_composition_and_retransmissions():
    # p = 1 - prod(1 - p_i); for small equal alpha it is approximately k*alpha.
    assert path_loss([0.1, 0.1, 0.1]) == pytest.approx(1 - 0.9 ** 3)
    alpha, k = 1e-4, 5
    assert path_loss([alpha] * k) == pytest.approx(k * alpha, rel=1e-3)
    assert expected_transmissions(0.0, 0.0) == 1.0
    assert expected_transmissions(0.5, 0.5) == pytest.approx(4.0)


def test_t11_earth_to_moon_link():
    # 40 kbit/s, 1.5 light-seconds each way, 1000-byte packets.
    rate, util = A[("t11", "4A")]
    assert stop_and_wait_throughput(3.0, packet=1000) == pytest.approx(rate)
    # The exact utilisation is 1/15 = 6.67 %.  MIT prints 6.5 %, which is what
    # you get after rounding the rate to the 2.6 kbit/s the sheet also prints
    # (2.6/40).  Assert both, and keep the discrepancy visible rather than
    # picking whichever one makes the test pass.
    assert link_utilisation(rate * 8, 40_000) == pytest.approx(1 / 15)
    assert link_utilisation(2600, 40_000) == pytest.approx(util)
    # counting the 0.2 s it takes to clock 8000 bits onto a 40 kbit/s link
    assert stop_and_wait_throughput(3.0 + 8000 / 40_000,
                                    packet=1000) == pytest.approx(A[("t11", "4A_with_tx")])
