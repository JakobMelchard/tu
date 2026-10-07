import pytest

from telnet_client_sketch import *


def test_parse_negotiation_and_data():
    raw = bytes([IAC, DO, 24, IAC, WILL, 1]) + b"login: " + bytes([IAC, IAC]) + b"!"
    items = parse_stream(raw)
    assert items == [("cmd", "DO", 24), ("cmd", "WILL", 1), ("data", b"login: \xff!")]
    assert describe(items)[:2] == ["IAC DO TTYPE", "IAC WILL ECHO"]


def test_subnegotiation():
    raw = bytes([IAC, SB, 24, 0]) + b"XTERM" + bytes([IAC, SE]) + b"$ "
    items = parse_stream(raw)
    assert items == [("cmd", "SB", 24, b"\x00XTERM"), ("data", b"$ ")]


def test_client_refuses_unknown_options_and_accepts_allowlist():
    items = parse_stream(bytes([IAC, DO, 24, IAC, WILL, 1, IAC, WILL, 3, IAC, DO, 31, IAC, WILL, 34]))
    reply = negotiate(items)
    assert reply == bytes([IAC, WONT, 24, IAC, DO, 1, IAC, DO, 3, IAC, WONT, 31, IAC, DONT, 34])
    assert escape_data(b"a\xffb") == b"a\xff\xffb"


def test_command_codes_match_rfc854_table():
    """The code table in RFC 854 ("TELNET COMMAND STRUCTURE"), read from the vendored text."""
    import pathlib, re
    rfc = (pathlib.Path(__file__).parents[2] / "refs/rfc/rfc854.txt").read_text()
    table = dict(re.findall(r"^\s{6}(SE|SB|IAC|WILL|WON'T|DO|DON'T)\b.*?\s(\d{3})\s", rfc, re.M))
    assert table == {"SE": "240", "SB": "250", "WILL": "251", "WON'T": "252",
                     "DO": "253", "DON'T": "254", "IAC": "255"}
    assert (SE, SB, WILL, WONT, DO, DONT, IAC) == (240, 250, 251, 252, 253, 254, 255)


# RFC 1143 section 7, "Upon receipt of WILL" and "Upon receipt of WONT", row by row:
# (him, himq) -> (him, himq, what we send).  'agree' is the NO row's "if we agree".
RFC1143_WILL = {(NO, EMPTY, True): (YES, EMPTY, DO), (NO, EMPTY, False): (NO, EMPTY, DONT),
                (YES, EMPTY, None): (YES, EMPTY, None),
                (WANTNO, EMPTY, None): (NO, EMPTY, None), (WANTNO, OPPOSITE, None): (YES, EMPTY, None),
                (WANTYES, EMPTY, None): (YES, EMPTY, None), (WANTYES, OPPOSITE, None): (WANTNO, EMPTY, DONT)}
RFC1143_WONT = {(NO, EMPTY): (NO, EMPTY, None), (YES, EMPTY): (NO, EMPTY, DONT),
                (WANTNO, EMPTY): (NO, EMPTY, None), (WANTNO, OPPOSITE): (WANTYES, EMPTY, DO),
                (WANTYES, EMPTY): (NO, EMPTY, None), (WANTYES, OPPOSITE): (NO, EMPTY, None)}


def _q(state, queue, agree=False):
    q = QOption(accept_him=bool(agree))
    q.state["him"], q.queue["him"] = state, queue
    return q


def test_q_method_rfc1143_section7_receipt_tables():
    for (st, qb, agree), (st2, qb2, sent) in RFC1143_WILL.items():
        q = _q(st, qb, agree)
        assert (q.received_enable("him"), q.state["him"], q.queue["him"]) == (sent, st2, qb2)
    for (st, qb), (st2, qb2, sent) in RFC1143_WONT.items():
        q = _q(st, qb)
        assert (q.received_disable("him"), q.state["him"], q.queue["him"]) == (sent, st2, qb2)
    # "our side by the same procedures, with DO-WILL, DONT-WONT ... swapped"
    q = QOption(accept_us=False)
    assert q.received_enable("us") == WONT and q.received_disable("us") is None


def test_q_method_our_requests_and_queue_bit():
    q = QOption()
    assert q.request("him", True) == DO and q.state["him"] == WANTYES
    with pytest.raises(ValueError):
        q.request("him", True)                                   # already negotiating
    assert q.request("him", False) is None and q.queue["him"] == OPPOSITE
    assert q.received_enable("him") == DONT and q.state["him"] == WANTNO   # queued change fires
    assert q.received_disable("him") is None and q.state["him"] == NO
    with pytest.raises(ValueError):
        q.request("him", False)                                  # already disabled


def test_note12_problem19_repeated_do_is_refused_each_time_and_nothing_loops():
    n = Negotiator(will_do=())
    assert n.receive(parse_stream(bytes([IAC, DO, 1]))) == bytes([IAC, WONT, 1])
    # the second DO still proposes a change (NO -> YES), so section 2 says answer it
    assert n.receive(parse_stream(bytes([IAC, DO, 1]))) == bytes([IAC, WONT, 1])
    # a refusal of something already off does not propose a change: never answered
    assert n.receive(parse_stream(bytes([IAC, DONT, 1, IAC, WONT, 1]))) == b""
    ok = Negotiator(will_accept=("ECHO",))
    assert ok.receive(parse_stream(bytes([IAC, WILL, 1, IAC, WILL, 1]))) == bytes([IAC, DO, 1])


def naive(cmd):
    """The implementation RFC 1143 section 2 warns about: confirm every
    rejection, answer every command."""
    return {WILL: DONT, DO: WONT, WONT: DONT, DONT: WONT}[cmd]


def test_naive_peers_loop_and_the_q_method_breaks_it():
    msgs, cmd = 0, WILL                     # naive A offers ECHO to naive B
    while msgs < 100:
        cmd, msgs = naive(cmd), msgs + 1    # B answers, A answers the answer, ...
    assert msgs == 100                      # still going: WONT <-> DONT forever
    b, cmd, msgs = QOption(), WILL, 0       # same offer to a Q-method B
    while cmd is not None and msgs < 100:
        reply = b.received_enable("him") if cmd == WILL else b.received_disable("him")
        msgs += 1
        cmd = naive(reply) if reply is not None else None
    assert msgs == 2 and b.state["him"] == NO   # DONT, then A's WONT is ignored
