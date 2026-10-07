"""Solutions to the **reliable transport** practice problems of MIT 6.02, Fall
2012 (Balakrishnan & Verghese), published on MIT OpenCourseWare under
**CC BY-NC-SA 4.0** [S34]: tutorial 11.  Routing is in `mit602_routing.py`.

Stop-and-wait, sliding windows, the bandwidth-delay product, sequence-number
wraparound and loss composition — the arithmetic behind 191.030's "describe TCP
behavior given a specific scenario" [S1] (stated on TISS until 2026-09-2x,
removed by 2026-09-27), one layer of abstraction above `../../py/tcp_sim.py`.

This is **not** 191.030 material; see `README.md`.  Every problem is restated in
our own words; the published answers are quoted as bare numbers in
`PUBLISHED_ANSWERS`.

Run `python3 mit602_transport.py` for a demo.
"""

# --------------------------------------------------------------------------
# The answers MIT published, keyed by problem.  Quoting a result is not
# quoting the sheet: these are the numbers the solution PDF prints.
# --------------------------------------------------------------------------
PUBLISHED_ANSWERS = {
    ("t11", "1A"): 8.0,            # s, RTT across the 4-link chain
    ("t11", "1B"): 1 / 8,          # pkt/s, stop-and-wait
    ("t11", "1C"): (8, 1.0),       # optimum window (pkts), throughput (pkt/s)
    ("t11", "1D"): (0.5, 0.5),     # throughput (pkt/s), link utilisation
    ("t11", "2A"): 10_000.0,       # byte/s, stop-and-wait
    ("t11", "2B"): 100_000.0,      # byte window = bandwidth-delay product
    ("t11", "2C"): 2.55e6,         # byte/s at which an 8-bit seq number wraps
    ("t11", "4A"): (1000 / 3, 0.065),      # byte/s and utilisation, no tx time
    ("t11", "4A_with_tx"): 1000 / 3.2,     # byte/s counting transmission time
}


# --------------------------------------------------------------------------
# Tutorial 11 — reliable transport arithmetic
# TISS topic: layer 4 (TCP/UDP), and "describe TCP behaviour given a scenario"
# (practical-part wording, stated on TISS until 2026-09-2x, removed by 2026-09-27).
# --------------------------------------------------------------------------
def chain_rtt(links, per_link_time=1.0):
    """A packet and its acknowledgement each traverse every link once, and
    each link takes one transmission time."""
    return 2 * links * per_link_time


def stop_and_wait_throughput(rtt, packet=1.0):
    return packet / rtt


def optimal_window(rtt, per_link_time=1.0):
    """Enough packets in flight to keep the bottleneck busy for a whole RTT."""
    return rtt / per_link_time


def window_throughput(window, rtt, capacity=1.0, packet=1.0):
    """`window` packets per RTT, capped by the bottleneck link rate."""
    return min(window * packet / rtt, capacity)


def bandwidth_delay_product(capacity_bytes_s, rtt_s):
    return capacity_bytes_s * rtt_s


def seq_wraparound_capacity(seq_bits, packet_bytes, rtt_s):
    """Bottleneck rate at which a `seq_bits`-bit sequence number wraps within
    one RTT, so two live packets share a number and an ACK is ambiguous.

    MIT's sheet counts 2**seq_bits - 1 usable numbers, which is why the
    published answer is 2.55 and not 2.56 Mbyte/s.
    """
    return (2 ** seq_bits - 1) * packet_bytes / rtt_s


def path_loss(per_link):
    """End-to-end loss across independent lossy links."""
    p = 1.0
    for q in per_link:
        p *= (1 - q)
    return 1 - p


def expected_transmissions(p, q):
    """Stop-and-wait: a packet advances only if it *and* its ACK survive."""
    return 1 / ((1 - p) * (1 - q))


def link_utilisation(achieved, capacity):
    return achieved / capacity


def out_of_order_buffer(window, rtt, timeout, at_time, drop=lambda s: s % 2 == 1):
    """Tutorial 11 problem 1E: the sender runs a `window`-packet sliding
    window over a path with `rtt`; the network drops every packet for which
    `drop(seq)` holds; the receiver buffers what it cannot deliver in order.
    How many packets sit in that buffer at `at_time`?

    Sequence numbers start at 1.  One "round" is one RTT: everything the
    window allows is sent, and one RTT later the ACKs for the survivors open
    the window by exactly that many.
    """
    sent, buffered, t, unacked = 0, 0, 0.0, 0
    while True:
        allowed = window - unacked
        if allowed <= 0 or t + rtt > timeout:
            break
        batch = range(sent + 1, sent + allowed + 1)
        delivered = [s for s in batch if not drop(s)]
        sent += allowed
        t += rtt
        if t > at_time:
            # the ACKs for this batch have not come back yet
            break
        buffered += len(delivered)
        unacked += allowed - len(delivered)
    return buffered


def demo():
    print("MIT 6.02 Fall 2012 reliable-transport practice problems [S34]")
    rtt = chain_rtt(4)
    print(f"  t11 P1 RTT={rtt}s  stop-and-wait={stop_and_wait_throughput(rtt):.4f} pkt/s"
          f"  W*={optimal_window(rtt):g}  W=4 gives {window_throughput(4, rtt)} pkt/s")
    print("  t11 P1E receiver buffer at t=35s:", out_of_order_buffer(8, 8, 40, 35))
    print("  t11 P2C wraparound at",
          seq_wraparound_capacity(8, 1000, 0.1) / 1e6, "Mbyte/s")
    print("  t11 P4A earth-moon:", round(stop_and_wait_throughput(3.0, 1000), 1),
          "byte/s, utilisation", round(link_utilisation(1000 / 3 * 8, 40_000), 4))


if __name__ == "__main__":
    demo()
