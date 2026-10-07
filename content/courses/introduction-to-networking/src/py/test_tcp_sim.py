from tcp_sim import TCPSim, Link, MSS


def test_lossless_transfer_slow_start_doubles():
    sim = TCPSim(16 * MSS, Link(delay=0.05))
    trace = sim.run()
    assert sim.snd_una == 16 * MSS and trace[-1].split()[1] == "done"
    # Number of segments sent per RTT: 1, 2, 4, 8, ... in slow start.
    sends = [l for l in trace if l.split()[1] == "send"]
    per_rtt = {}
    for l in sends:
        per_rtt.setdefault(round(float(l.split()[0]), 1), 0)
        per_rtt[round(float(l.split()[0]), 1)] += 1
    assert list(per_rtt.values())[:4] == [1, 2, 4, 8]
    assert not any("rexmit" in l or "TIMEOUT" in l for l in trace)


def test_single_loss_triggers_fast_retransmit_not_timeout():
    # Drop the 6th transmission (index 5) while 8 segments are in flight -> 3 dup acks.
    sim = TCPSim(30 * MSS, Link(delay=0.05, drop={5}))
    trace = sim.run()
    kinds = [l.split()[1] for l in trace]
    assert "FASTRX" in kinds and "TIMEOUT" not in kinds
    assert kinds.count("rexmit") == 1
    i = kinds.index("FASTRX")
    assert kinds[i - 3:i] == ["dupack"] * 3
    assert sim.snd_una == 30 * MSS
    # after recovery cwnd = ssthresh = half the flight size, phase is congestion avoidance
    assert "congestion avoidance" in trace[-1]


def test_loss_with_nothing_else_in_flight_needs_timeout():
    # Drop the very first segment: no dup acks possible -> RTO expiry, cwnd back to 1.
    sim = TCPSim(4 * MSS, Link(delay=0.05, drop={0}))
    trace = sim.run()
    kinds = [l.split()[1] for l in trace]
    assert kinds[:2] == ["send", "TIMEOUT"] and kinds[2] == "rexmit"
    assert float(trace[1].split()[0]) >= 1.0                 # initial RTO of 1 s
    assert sim.snd_una == 4 * MSS


def test_rto_estimator_matches_rfc6298():
    sim = TCPSim(MSS)
    sim.update_rto(0.1)
    assert sim.srtt == 0.1 and sim.rttvar == 0.05 and abs(sim.rto - 0.3) < 1e-9
    sim.update_rto(0.2)
    assert abs(sim.rttvar - (0.75 * 0.05 + 0.25 * 0.1)) < 1e-9
    assert abs(sim.srtt - (0.875 * 0.1 + 0.125 * 0.2)) < 1e-9


def test_receiver_buffers_out_of_order_and_acks_cumulatively():
    sim = TCPSim(30 * MSS, Link(delay=0.05, drop={5}))
    trace = sim.run()
    dup = [l for l in trace if "dupack" in l][0]
    lost_seq = [l for l in trace if "LOST" in l][0].split("seq=")[1].split()[0]
    assert f"ack={lost_seq}" in dup                       # cumulative ACK stalls at the hole
    # the ACK right after the retransmission jumps past all buffered segments
    after = [l for l in trace if l.split()[1] == "ack" and int(l.split("ack=")[1].split()[0]) > int(lost_seq)][0]
    assert int(after.split("ack=")[1].split()[0]) - int(lost_seq) > MSS
