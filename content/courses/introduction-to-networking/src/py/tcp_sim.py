"""Event-driven TCP sender/receiver simulator on a lossy link (note 05).

Models, in bytes and MSS units, what an exam 'describe the TCP behaviour'
scenario asks for: sequence/ack numbers, cumulative ACKs, one retransmission
timer for the oldest unacked segment (RFC 6298 RTO: SRTT/RTTVAR with backoff),
slow start / congestion avoidance / fast retransmit (3 dup ACKs) per RFC 5681
(Reno-style: cwnd halves and enters congestion avoidance after fast retransmit;
timeout resets cwnd to 1 MSS).  Receiver is ideal: infinite buffer, no delayed
ACKs, one ACK per received segment.  Time is simulated, not real.

RFC sections: RFC 6298 section 2 (rules 2.1-2.5: initial RTO 1 s, alpha 1/8,
beta 1/4, K 4, RTTVAR before SRTT, maximum >= 60 s; rule 2.4's 1 s floor is
lowered to 0.2 s, Linux's value, so the demo stays short), section 3 (Karn: no
sample from a retransmission) and section 5.5 (back-off), in `TCPSim.update_rto`,
`transmit`, `on_timeout`; RFC 5681 section 3.1 (slow start, congestion
avoidance, ssthresh = max(FlightSize/2, 2*SMSS)) and 3.2 (fast retransmit /
fast recovery) in `TCPSim.on_ack`.  Connection setup and teardown states are
not modelled here: see `tcp_fsm.py` (RFC 9293 section 3.3.2).
"""
import heapq

MSS = 1000


class Link:
    """Fixed one-way delay; a set of packet indices (sender's nth transmission)
    to drop lets a test script a scenario deterministically."""
    def __init__(self, delay=0.05, drop=()):
        self.delay, self.drop, self.sent = delay, set(drop), 0

    def lossy(self):
        self.sent += 1
        return (self.sent - 1) in self.drop


class TCPSim:
    def __init__(self, nbytes, link=None, isn=0, rwnd=64 * MSS, verbose=False):
        self.link = link or Link()
        self.total, self.isn, self.rwnd = nbytes, isn, rwnd
        self.snd_una = self.snd_nxt = isn          # oldest unacked / next to send
        self.cwnd, self.ssthresh = 1 * MSS, 64 * MSS
        self.srtt = self.rttvar = None
        self.rto = 1.0
        self.dupacks, self.recover = 0, isn
        self.rcv_nxt = isn                          # receiver's expected byte
        self.ooo = set()                            # receiver out-of-order segment starts
        self.timer = None                           # (expiry, generation)
        self.timer_gen = 0
        self.events, self.now, self.trace = [], 0.0, []
        self.inflight_sent_at = {}
        self.verbose, self.phase = verbose, "slow start"

    # ---------------------------------------------------------- bookkeeping
    def log(self, kind, msg):
        line = f"{self.now:7.3f}  {kind:<6} {msg}  [cwnd={self.cwnd // MSS} ssthresh={self.ssthresh // MSS} rto={self.rto:.2f} {self.phase}]"
        self.trace.append(line)
        if self.verbose:
            print(line)

    def schedule(self, dt, fn, *args):
        heapq.heappush(self.events, (self.now + dt, len(self.events), fn, args))

    def arm_timer(self):
        self.timer_gen += 1
        self.schedule(self.rto, self.on_timeout, self.timer_gen)

    # ---------------------------------------------------------- sender
    def send_allowed(self):
        window = min(self.cwnd, self.rwnd)
        while self.snd_nxt < self.isn + self.total and self.snd_nxt - self.snd_una + MSS <= window:
            self.transmit(self.snd_nxt, first_time=True)
            self.snd_nxt += MSS

    def transmit(self, seq, first_time):
        seg_len = min(MSS, self.isn + self.total - seq)
        self.inflight_sent_at[seq] = self.now if first_time else None   # Karn: no RTT sample on retransmit
        dropped = self.link.lossy()
        self.log("send" if first_time else "rexmit", f"seq={seq} len={seg_len}" + ("  ** LOST **" if dropped else ""))
        if self.snd_una == seq or self.timer is None:
            self.arm_timer()
        if not dropped:
            self.schedule(self.link.delay, self.on_receive, seq, seg_len)

    def on_timeout(self, gen):
        if gen != self.timer_gen or self.snd_una >= self.isn + self.total:
            return                                    # stale timer
        # RFC 5681: ssthresh = max(flight/2, 2 MSS), cwnd = 1 MSS, RTO doubles (RFC 6298 5.5)
        self.ssthresh = max((self.snd_nxt - self.snd_una) // 2 // MSS * MSS, 2 * MSS)
        self.cwnd, self.phase, self.dupacks = MSS, "slow start", 0
        self.rto = min(self.rto * 2, 60.0)
        self.log("TIMEOUT", f"retransmit from seq={self.snd_una}")
        self.transmit(self.snd_una, first_time=False)

    def on_ack(self, ack):
        if ack > self.snd_una:                        # new data acknowledged
            acked = ack - self.snd_una
            sent_at = self.inflight_sent_at.pop(self.snd_una, None)
            if sent_at is not None:
                self.update_rto(self.now - sent_at)
            self.snd_una, self.dupacks = ack, 0
            for s in list(self.inflight_sent_at):
                if s < ack:
                    del self.inflight_sent_at[s]
            if self.phase == "fast recovery":
                self.cwnd, self.phase = self.ssthresh, "congestion avoidance"
            elif self.cwnd < self.ssthresh:
                self.cwnd += min(acked, MSS)          # slow start: +1 MSS per ACK
                if self.cwnd >= self.ssthresh:
                    self.phase = "congestion avoidance"
            else:
                self.cwnd += MSS * MSS // self.cwnd    # AIMD: +MSS per RTT (approx)
                self.phase = "congestion avoidance"
            self.log("ack", f"ack={ack}")
            if self.snd_una < self.isn + self.total:
                self.arm_timer()
            else:
                self.timer_gen += 1
                self.log("done", f"all {self.total} bytes acked")
        elif ack == self.snd_una:
            self.dupacks += 1
            self.log("dupack", f"ack={ack} #{self.dupacks}")
            if self.dupacks == 3 and self.phase != "fast recovery":
                self.ssthresh = max((self.snd_nxt - self.snd_una) // 2 // MSS * MSS, 2 * MSS)
                self.cwnd, self.phase = self.ssthresh + 3 * MSS, "fast recovery"
                self.log("FASTRX", f"3 dup acks: retransmit seq={self.snd_una}")
                self.transmit(self.snd_una, first_time=False)
            elif self.dupacks > 3 and self.phase == "fast recovery":
                self.cwnd += MSS                      # window inflation
        self.send_allowed()

    def update_rto(self, r):
        """RFC 6298 rule 2.2 (first sample: SRTT = R, RTTVAR = R/2) and rule 2.3,
        in the order it requires: RTTVAR = 3/4 RTTVAR + 1/4 |SRTT - R| with the
        *old* SRTT, then SRTT = 7/8 SRTT + 1/8 R;  RTO = SRTT + max(G, 4 RTTVAR),
        clamped to >= 1 s by rule 2.4 (here 0.2 s to keep the demo short)."""
        if self.srtt is None:
            self.srtt, self.rttvar = r, r / 2
        else:
            self.rttvar = 0.75 * self.rttvar + 0.25 * abs(self.srtt - r)
            self.srtt = 0.875 * self.srtt + 0.125 * r
        self.rto = max(0.2, self.srtt + max(0.01, 4 * self.rttvar))

    # ---------------------------------------------------------- receiver
    def on_receive(self, seq, seg_len):
        if seq == self.rcv_nxt:
            self.rcv_nxt += seg_len
            while self.rcv_nxt in self.ooo:           # deliver buffered segments
                self.ooo.discard(self.rcv_nxt)
                self.rcv_nxt += MSS
        elif seq > self.rcv_nxt:
            self.ooo.add(seq)                         # out of order: buffer, dup ACK
        self.schedule(self.link.delay, self.on_ack, self.rcv_nxt)   # cumulative ACK

    # ---------------------------------------------------------- driver
    def run(self, max_time=120.0):
        self.send_allowed()
        while self.events and self.now < max_time:
            self.now, _, fn, args = heapq.heappop(self.events)
            fn(*args)
            if self.snd_una >= self.isn + self.total:
                break
        return self.trace


if __name__ == "__main__":
    print("== 20 segments, drop the 6th and 13th transmission ==")
    TCPSim(20 * MSS, Link(delay=0.05, drop={5, 12}), verbose=True).run()
