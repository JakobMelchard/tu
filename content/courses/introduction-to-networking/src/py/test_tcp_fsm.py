"""RFC 9293 connection figures, line by line (refs/rfc/rfc9293.txt, sections 3.5, 3.6).

Each figure line gives the segment in the RFC's notation and the state of each
peer AFTER that line; the tests assert both.
"""
import pytest

from tcp_fsm import (Endpoint, Segment, IllegalTransition, TRANSITIONS, RST_EDGES, STATES, deliver,
                     CLOSED, LISTEN, SYN_SENT, SYN_RECEIVED, ESTABLISHED, FIN_WAIT_1, FIN_WAIT_2,
                     CLOSE_WAIT, CLOSING, LAST_ACK, TIME_WAIT, MSL, TIME_WAIT_SECONDS)


def states(a, b):
    return a.state, b.state


def test_figure6_basic_three_way_handshake():
    a, b = Endpoint("A", 100), Endpoint("B", 300)
    b.open(passive=True)
    assert states(a, b) == (CLOSED, LISTEN)                                        # line 1
    (syn,) = a.open(passive=False)
    (synack,) = b.receive(syn)
    assert str(syn) == "<SEQ=100><CTL=SYN>"                                        # line 2
    assert str(synack) == "<SEQ=300><ACK=101><CTL=SYN,ACK>"                        # line 3
    (ack,) = a.receive(synack)
    assert str(ack) == "<SEQ=101><ACK=301><CTL=ACK>" and a.state == ESTABLISHED    # line 4
    assert b.receive(ack) == [] and b.state == ESTABLISHED
    (data,) = a.send(b"x")
    assert str(data) == "<SEQ=101><ACK=301><CTL=ACK><DATA>"                        # line 5: same seq
    assert b.history == [CLOSED, LISTEN, SYN_RECEIVED, ESTABLISHED]


def test_figure7_simultaneous_open():
    a, b = Endpoint("A", 100), Endpoint("B", 300)
    (syn_a,) = a.open(passive=False)                                               # line 2, delayed
    (syn_b,) = b.open(passive=False)
    assert str(syn_a) == "<SEQ=100><CTL=SYN>" and str(syn_b) == "<SEQ=300><CTL=SYN>"
    (synack_a,) = a.receive(syn_b)                                                 # line 3
    assert a.state == SYN_RECEIVED
    (synack_b,) = b.receive(syn_a)                                                 # line 4
    assert b.state == SYN_RECEIVED
    assert str(synack_a) == "<SEQ=100><ACK=301><CTL=SYN,ACK>"                      # line 5
    assert str(synack_b) == "<SEQ=300><ACK=101><CTL=SYN,ACK>"                      # line 6
    assert a.receive(synack_b) == [] and a.state == ESTABLISHED
    assert b.receive(synack_a) == [] and b.state == ESTABLISHED                    # line 7
    for ep in (a, b):          # "cycles from CLOSED to SYN-SENT to SYN-RECEIVED to ESTABLISHED"
        assert ep.history == [CLOSED, SYN_SENT, SYN_RECEIVED, ESTABLISHED]


def test_figure8_recovery_from_old_duplicate_syn():
    a, b = Endpoint("A", 100), Endpoint("B", [300, 400])
    b.open(passive=True)
    (syn,) = a.open(passive=False)                                                 # line 2, delayed
    (synack_old,) = b.receive(Segment(90, None, ("SYN",)))                         # line 3
    assert b.state == SYN_RECEIVED
    assert str(synack_old) == "<SEQ=300><ACK=91><CTL=SYN,ACK>"                     # line 4
    (rst,) = a.receive(synack_old)
    assert str(rst) == "<SEQ=91><CTL=RST>" and a.state == SYN_SENT                 # line 5
    assert b.receive(rst) == [] and b.state == LISTEN                              # Note 1
    (synack,) = b.receive(syn)                                                     # line 6
    assert str(synack) == "<SEQ=400><ACK=101><CTL=SYN,ACK>"                        # line 7
    (ack,) = a.receive(synack)
    assert str(ack) == "<SEQ=101><ACK=401><CTL=ACK>"                               # line 8
    b.receive(ack)
    assert states(a, b) == (ESTABLISHED, ESTABLISHED)


def test_figure12_normal_close():
    a, b = Endpoint.established("A", 100, 300), Endpoint.established("B", 300, 100)
    (fin_a,) = a.close()
    assert str(fin_a) == "<SEQ=100><ACK=300><CTL=FIN,ACK>"                         # line 2
    (ack_b,) = b.receive(fin_a)
    assert states(a, b) == (FIN_WAIT_1, CLOSE_WAIT)
    assert str(ack_b) == "<SEQ=300><ACK=101><CTL=ACK>"                             # line 3
    assert a.receive(ack_b) == [] and a.state == FIN_WAIT_2
    (fin_b,) = b.close()
    assert str(fin_b) == "<SEQ=300><ACK=101><CTL=FIN,ACK>" and b.state == LAST_ACK # line 4
    (last,) = a.receive(fin_b)
    assert str(last) == "<SEQ=101><ACK=301><CTL=ACK>" and a.state == TIME_WAIT     # line 5
    b.receive(last)
    assert b.state == CLOSED
    assert a.receive(fin_b) == [last] and a.state == TIME_WAIT     # FIN repeated: re-ACK
    a.timeout()
    assert a.state == CLOSED and TIME_WAIT_SECONDS == 2 * MSL == 240   # line 6, section 3.4.2


def test_figure13_simultaneous_close():
    a, b = Endpoint.established("A", 100, 300), Endpoint.established("B", 300, 100)
    (fin_a,), (fin_b,) = a.close(), b.close()
    assert str(fin_a) == "<SEQ=100><ACK=300><CTL=FIN,ACK>"                         # line 2
    assert str(fin_b) == "<SEQ=300><ACK=100><CTL=FIN,ACK>"
    (ack_a,), (ack_b,) = a.receive(fin_b), b.receive(fin_a)
    assert states(a, b) == (CLOSING, CLOSING)                                      # line 3
    assert str(ack_a) == "<SEQ=101><ACK=301><CTL=ACK>" and str(ack_b) == "<SEQ=301><ACK=101><CTL=ACK>"
    a.receive(ack_b), b.receive(ack_a)
    assert states(a, b) == (TIME_WAIT, TIME_WAIT)                                  # line 4
    a.timeout(), b.timeout()
    assert states(a, b) == (CLOSED, CLOSED)


def test_figure5_table_covers_every_state_and_rejects_the_rest():
    assert set(STATES) == {s for s, _ in TRANSITIONS} | {n for n, _ in TRANSITIONS.values()}
    assert len(STATES) == 11 and len(TRANSITIONS) == 21
    assert all(nxt == CLOSED for nxt, _ in RST_EDGES.values())
    ep = Endpoint("A", 1)
    with pytest.raises(IllegalTransition):
        ep.close()                                           # no CLOSE edge out of CLOSED
    with pytest.raises(IllegalTransition):
        ep.timeout()
    ep.open(passive=True)
    with pytest.raises(IllegalTransition):
        ep.open(passive=True)                                # LISTEN has no OPEN edge
    (syn,) = ep.send(b"")                                    # LISTEN --SEND--> SYN-SENT
    assert ep.state == SYN_SENT and str(syn) == "<SEQ=1><CTL=SYN>"
    ep.close()
    assert ep.history == [CLOSED, LISTEN, SYN_SENT, CLOSED]


def test_rst_handling_omitted_from_the_figure():
    a, b = Endpoint.established("A", 100, 300), Endpoint.established("B", 300, 100)
    assert b.receive(Segment(999, None, ("RST",))) == [] and b.state == ESTABLISHED   # out of window
    b.receive(Segment(100, None, ("RST",)))
    assert b.state == CLOSED
    c = Endpoint("C", 7)
    c.open(passive=False)
    c.receive(Segment(0, 8, ("RST",)))                       # acceptable: ACKs our SYN
    assert c.state == CLOSED


def note05_scenario1(isn_a=1000, isn_b=5000, request=b"r" * 18, response=(b"d" * 1000,) * 3):
    """Note 05 worked scenario 1 as a walk: returns [(sender, segment, A state, B state)]."""
    a, b = Endpoint("A", isn_a), Endpoint("B", isn_b)
    b.open(passive=True)
    log = []

    def send(src, dst, segs, **kw):
        for s in segs:
            log.append((src.name, s))
            replies = dst.receive(s, **kw)
            log[-1] += (a.state, b.state)
            if replies:
                send(dst, src, replies)
    send(a, b, a.open(passive=False))
    send(a, b, a.send(request), delay_ack=True)
    for chunk in response:
        send(b, a, b.send(chunk), delay_ack=True)
    send(a, b, a.ack())
    send(b, a, b.close(), then_close=True)
    return log, a, b


def test_note05_scenario1_numbers_and_who_ends_in_time_wait():
    log, a, b = note05_scenario1()
    rows = [(who, s.seq, s.ack, len(s.data), s.ctl) for who, s, *_ in log]
    assert rows == [("A", 1000, None, 0, ("SYN",)), ("B", 5000, 1001, 0, ("SYN",)),
                    ("A", 1001, 5001, 0, ()), ("A", 1001, 5001, 18, ()),
                    ("B", 5001, 1019, 1000, ()), ("B", 6001, 1019, 1000, ()),
                    ("B", 7001, 1019, 1000, ()), ("A", 1019, 8001, 0, ()),
                    ("B", 8001, 1019, 0, ("FIN",)), ("A", 1019, 8002, 0, ("FIN",)),
                    ("B", 8002, 1020, 0, ())]
    # B closed first, so B is the one in TIME-WAIT; A (passive closer) is CLOSED.
    assert (a.state, b.state) == (CLOSED, TIME_WAIT)
    assert a.history[-3:] == [CLOSE_WAIT, LAST_ACK, CLOSED]
    assert b.history[-2:] == [FIN_WAIT_1, TIME_WAIT]                  # Note 2 edge


def test_pcap_synthetic_trace_is_a_legal_walk():
    """pcap.synthetic_trace() (a 40-byte response) matches the state machine's
    walk segment for segment: seq, ack, length and flags (PSH aside)."""
    from pcap import synthetic_trace
    from headers import parse_frame
    tcp = [dict(parse_frame(f))["tcp"] for _, f in synthetic_trace() if "tcp" in dict(parse_frame(f))]
    log, a, b = note05_scenario1(response=(b"d" * 40,))
    walk = [(s.seq, s.ack if s.ack is not None else 0, len(s.data),
             "|".join([c for c in ("SYN", "FIN") if c in s.ctl] + (["ACK"] if s.ack is not None else [])))
            for _, s, *_ in log]
    trace = [(t["seq"], t["ack"], len(t["payload"]), t["flags_str"].replace("PSH|", "")) for t in tcp]
    assert len(trace) == 9 and trace == walk and (a.state, b.state) == (CLOSED, TIME_WAIT)


def test_demo_prints_figure6_in_rfc_notation(capsys):
    from tcp_fsm import demo
    demo()
    out = capsys.readouterr().out
    assert "<SEQ=300><ACK=101><CTL=SYN,ACK>" in out and "TIME-WAIT = 2 MSL = 240 s" in out
