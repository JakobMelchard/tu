"""TCP connection state machine, RFC 9293 section 3.3.2 (Figure 5), walked
segment by segment (notes 05, 11).

`tcp_sim.py` models what happens *inside* ESTABLISHED (sequence numbers, RTO,
congestion window).  This module models how a connection gets into and out of
ESTABLISHED:

* `TRANSITIONS` is Figure 5 as a table, (state, event) -> (next state, action),
  plus Note 1 (SYN-RECEIVED -> LISTEN on RST, only after a passive OPEN, which
  is why MUST-11 makes the endpoint remember how it got there) and Note 2
  (FIN-WAIT-1 -> TIME-WAIT when a FIN arrives that also acknowledges our FIN).
  `RST_EDGES` holds the RST edges that Note 3 says the figure omits
  (section 3.10.7.3/3.10.7.4 processing).
* `Endpoint` turns segments into events, checks every move against those
  tables (an illegal move raises), and emits replies numbered per section 3.4:
  SYN and FIN each occupy one sequence number, a bare ACK none.
* `Segment.__str__` prints the RFC's notation, `<SEQ=100><ACK=301><CTL=ACK>`, so
  the tests compare against Figures 6, 7, 8 (section 3.5) and 12, 13
  (section 3.6) line by line.

Out of scope: windows, retransmission, RFC 5961 challenge ACKs, urgent data.
MSL is 2 minutes (section 3.4.2), so TIME-WAIT lasts 2 MSL = 4 minutes.
"""
from dataclasses import dataclass

MSL = 120.0                                    # seconds, RFC 9293 section 3.4.2
TIME_WAIT_SECONDS = 2 * MSL

CLOSED, LISTEN, SYN_SENT, SYN_RECEIVED = "CLOSED", "LISTEN", "SYN-SENT", "SYN-RECEIVED"
ESTABLISHED, FIN_WAIT_1, FIN_WAIT_2 = "ESTABLISHED", "FIN-WAIT-1", "FIN-WAIT-2"
CLOSE_WAIT, CLOSING, LAST_ACK, TIME_WAIT = "CLOSE-WAIT", "CLOSING", "LAST-ACK", "TIME-WAIT"
STATES = (LISTEN, SYN_SENT, SYN_RECEIVED, ESTABLISHED, FIN_WAIT_1, FIN_WAIT_2,
          CLOSE_WAIT, CLOSING, LAST_ACK, TIME_WAIT, CLOSED)          # section 3.3.2 order
SYNCHRONIZED = (ESTABLISHED, FIN_WAIT_1, FIN_WAIT_2, CLOSE_WAIT, CLOSING, LAST_ACK, TIME_WAIT)

# Figure 5, edge by edge.  Event names follow the figure's labels.
TRANSITIONS = {
    (CLOSED, "passive OPEN"): (LISTEN, "create TCB"),
    (CLOSED, "active OPEN"): (SYN_SENT, "create TCB, snd SYN"),
    (LISTEN, "CLOSE"): (CLOSED, "delete TCB"),
    (LISTEN, "rcv SYN"): (SYN_RECEIVED, "snd SYN,ACK"),
    (LISTEN, "SEND"): (SYN_SENT, "snd SYN"),
    (SYN_SENT, "CLOSE"): (CLOSED, "delete TCB"),
    (SYN_SENT, "rcv SYN"): (SYN_RECEIVED, "snd SYN,ACK"),
    (SYN_SENT, "rcv SYN,ACK"): (ESTABLISHED, "snd ACK"),
    (SYN_RECEIVED, "rcv ACK of SYN"): (ESTABLISHED, "x"),
    (SYN_RECEIVED, "CLOSE"): (FIN_WAIT_1, "snd FIN"),
    (SYN_RECEIVED, "rcv RST"): (LISTEN, "Note 1: only after a passive OPEN"),
    (ESTABLISHED, "CLOSE"): (FIN_WAIT_1, "snd FIN"),
    (ESTABLISHED, "rcv FIN"): (CLOSE_WAIT, "snd ACK"),
    (FIN_WAIT_1, "rcv ACK of FIN"): (FIN_WAIT_2, "x"),
    (FIN_WAIT_1, "rcv FIN"): (CLOSING, "snd ACK"),
    (FIN_WAIT_1, "rcv FIN + ACK of FIN"): (TIME_WAIT, "Note 2: snd ACK"),
    (FIN_WAIT_2, "rcv FIN"): (TIME_WAIT, "snd ACK"),
    (CLOSE_WAIT, "CLOSE"): (LAST_ACK, "snd FIN"),
    (CLOSING, "rcv ACK of FIN"): (TIME_WAIT, "x"),
    (LAST_ACK, "rcv ACK of FIN"): (CLOSED, "x"),
    (TIME_WAIT, "Timeout=2MSL"): (CLOSED, "delete TCB"),
}
# Note 3: RST edges left out of the figure (sections 3.10.7.3, 3.10.7.4).
RST_EDGES = {(SYN_SENT, "rcv RST"): (CLOSED, "connection reset"),
             (SYN_RECEIVED, "rcv RST (active OPEN)"): (CLOSED, "connection refused"),
             **{(s, "rcv RST"): (CLOSED, "connection reset") for s in SYNCHRONIZED}}


class IllegalTransition(Exception):
    pass


@dataclass(frozen=True)
class Segment:
    seq: int
    ack: int | None = None                      # None: ACK bit clear
    ctl: tuple = ()                             # any of "SYN", "FIN", "RST"
    data: bytes = b""

    @property
    def length(self):                           # SEG.LEN, section 3.4
        return len(self.data) + ("SYN" in self.ctl) + ("FIN" in self.ctl)

    def __str__(self):
        ctl = [c for c in ("SYN", "FIN", "RST") if c in self.ctl]
        ctl += ["ACK"] if self.ack is not None else []
        ack = f"<ACK={self.ack}>" if self.ack is not None else ""
        return f"<SEQ={self.seq}>{ack}<CTL={','.join(ctl)}>" + ("<DATA>" if self.data else "")


class Endpoint:
    """One side of a connection.  `isn` may be a list: a new ISN is taken for
    each connection attempt (Figure 8 needs two)."""

    def __init__(self, name, isn=0):
        self.name = name
        self._isns = list(isn) if isinstance(isn, (list, tuple)) else [isn]
        self.state, self.passive, self.fin_sent = CLOSED, None, False
        self.iss = self.snd_una = self.snd_nxt = self.rcv_nxt = None
        self.history = [CLOSED]

    @classmethod
    def established(cls, name, snd_nxt, rcv_nxt):
        """An endpoint already in ESTABLISHED, for the close figures."""
        ep = cls(name)
        ep.state, ep.history = ESTABLISHED, [ESTABLISHED]
        ep.iss, ep.snd_una, ep.snd_nxt, ep.rcv_nxt = snd_nxt - 1, snd_nxt, snd_nxt, rcv_nxt
        return ep

    # ----------------------------------------------------------- bookkeeping
    def _go(self, event):
        table = TRANSITIONS if (self.state, event) in TRANSITIONS else RST_EDGES
        if (self.state, event) not in table:
            raise IllegalTransition(f"{self.name}: no edge ({self.state}, {event!r}) in Figure 5")
        self.state = table[(self.state, event)][0]
        self.history.append(self.state)

    def _new_iss(self):
        self.iss = self._isns.pop(0) if len(self._isns) > 1 else self._isns[0]
        self.snd_una, self.snd_nxt = self.iss, self.iss + 1          # the SYN takes one number
        return self.iss

    def _out(self, ctl=(), data=b""):
        """Next segment in sequence, ACK bit set; advances SND.NXT by SEG.LEN."""
        seg = Segment(self.snd_nxt, self.rcv_nxt, tuple(ctl), data)
        self.snd_nxt += seg.length
        return seg

    # ----------------------------------------------------------- user calls
    def open(self, passive):
        self.passive = passive
        if passive:
            self._go("passive OPEN")
            return []
        self._go("active OPEN")
        return [Segment(self._new_iss(), None, ("SYN",))]

    def send(self, data):
        if self.state == LISTEN:                  # Figure 5: LISTEN --SEND / snd SYN--> SYN-SENT
            self._go("SEND")
            self.passive = False
            return [Segment(self._new_iss(), None, ("SYN",))]
        if self.state not in (ESTABLISHED, CLOSE_WAIT):
            raise IllegalTransition(f"{self.name}: SEND in {self.state}")
        return [self._out(data=data)]

    def ack(self):
        """A bare (possibly delayed) acknowledgment; no state change."""
        return [Segment(self.snd_nxt, self.rcv_nxt)]

    def close(self):
        self._go("CLOSE")
        if self.state in (CLOSED,):
            return []
        self.fin_sent = True
        return [self._out(("FIN",))]

    def timeout(self):
        self._go("Timeout=2MSL")
        return []

    # ----------------------------------------------------------- arrivals
    def receive(self, seg, delay_ack=False, then_close=False):
        """Process one arriving segment, return the segments sent in reply.
        `delay_ack`: do not answer data with a bare ACK (the next segment
        carries it).  `then_close`: the application closes as soon as the
        peer's FIN arrives, so the ACK rides on our FIN (three-segment close)."""
        if "RST" in seg.ctl:
            return self._receive_rst(seg)
        if self.state == LISTEN:
            if "SYN" not in seg.ctl:
                return [Segment(seg.ack, None, ("RST",))] if seg.ack is not None else []
            self.rcv_nxt = seg.seq + 1
            self._go("rcv SYN")
            return [Segment(self._new_iss(), self.rcv_nxt, ("SYN",))]
        if self.state == SYN_SENT:
            if seg.ack is not None and seg.ack != self.snd_nxt:      # unacceptable ACK
                return [Segment(seg.ack, None, ("RST",))]            # <SEQ=SEG.ACK><CTL=RST>
            self.rcv_nxt = seg.seq + 1
            if seg.ack is None:                                      # simultaneous open
                self._go("rcv SYN")
                return [Segment(self.iss, self.rcv_nxt, ("SYN",))]   # SYN again, now with ACK
            self.snd_una = seg.ack
            self._go("rcv SYN,ACK")
            return [self._out()]
        if self.state == SYN_RECEIVED:
            if seg.ack != self.snd_nxt:
                return []
            self._go("rcv ACK of SYN")
        return self._receive_synchronized(seg, delay_ack, then_close)

    def _receive_rst(self, seg):
        if self.state == SYN_SENT and seg.ack != self.snd_nxt:
            return []                                                # not acceptable: drop
        if self.state in (SYN_RECEIVED,) + SYNCHRONIZED and seg.seq != self.rcv_nxt:
            return []                                                # outside the window: drop
        if self.state == SYN_RECEIVED and not self.passive:
            self._go("rcv RST (active OPEN)")
        elif self.state != LISTEN:
            self._go("rcv RST")
        return []

    def _receive_synchronized(self, seg, delay_ack, then_close):
        fin_acked = self.fin_sent and seg.ack == self.snd_nxt
        if seg.ack is not None:
            self.snd_una = max(self.snd_una, seg.ack)
        in_order = seg.seq == self.rcv_nxt and seg.length > 0 and "SYN" not in seg.ctl
        got_fin = in_order and "FIN" in seg.ctl
        if in_order:
            self.rcv_nxt += seg.length
        if self.state == FIN_WAIT_1:
            if got_fin:
                self._go("rcv FIN + ACK of FIN" if fin_acked else "rcv FIN")
            elif fin_acked:
                self._go("rcv ACK of FIN")
        elif self.state in (ESTABLISHED, FIN_WAIT_2) and got_fin:
            self._go("rcv FIN")
            if then_close and self.state == CLOSE_WAIT:
                return self.close()                                  # FIN,ACK in one segment
        elif self.state in (CLOSING, LAST_ACK) and fin_acked:
            self._go("rcv ACK of FIN")
        elif self.state == TIME_WAIT and "FIN" in seg.ctl:
            return self.ack()                                        # FIN retransmitted: ACK again
        if got_fin or (in_order and not delay_ack):
            return self.ack()
        return []


def deliver(dst, segments, **kw):
    """Deliver each segment to `dst`; return everything `dst` sends back."""
    return [r for s in segments for r in dst.receive(s, **kw)]


def demo():
    print("RFC 9293 Figure 6, basic three-way handshake:")
    a, b = Endpoint("A", 100), Endpoint("B", 300)
    b.open(passive=True)
    syn = a.open(passive=False)
    synack = deliver(b, syn)
    ack = deliver(a, synack)
    deliver(b, ack)
    for n, (seg, arrow) in enumerate([(syn[0], "-->"), (synack[0], "<--"), (ack[0], "-->")], 2):
        print(f"  {n}. {arrow} {seg}")
    print(f"  A: {' -> '.join(a.history)}\n  B: {' -> '.join(b.history)}")
    print("\nRFC 9293 Figure 12, normal close:")
    a, b = Endpoint.established("A", 100, 300), Endpoint.established("B", 300, 100)
    fin_a = a.close()
    ack_b = deliver(b, fin_a)
    deliver(a, ack_b)
    fin_b = b.close()
    last = deliver(a, fin_b)
    deliver(b, last)
    for seg in fin_a + ack_b + fin_b + last:
        print("   ", seg)
    a.timeout()
    print(f"  A: {' -> '.join(a.history)}  (TIME-WAIT = 2 MSL = {TIME_WAIT_SECONDS:.0f} s)")
    print(f"  B: {' -> '.join(b.history)}")


if __name__ == "__main__":
    demo()
