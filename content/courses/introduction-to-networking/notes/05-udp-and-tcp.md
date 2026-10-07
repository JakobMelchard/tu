# 05 UDP and TCP (layer 4)

> **Sourcing.** UDP is RFC 768, TCP is RFC 9293 (STD 7, which obsoleted RFC 793
> in 2022), host behaviour RFC 1122, the RTO RFC 6298, congestion control RFC
> 5681 (+ 6928 for IW10), options RFC 7323, ECN RFC 3168 — all vendored
> [S13], [S14]. Where a number below is an implementation choice rather than an
> RFC requirement it now says so; that distinction is the most common source of
> confidently wrong exam answers in this topic.

The transport layer turns host-to-host delivery (IP) into **process-to-process** delivery via **ports** (16 bit): well-known 0–1023 (53 DNS, 80 HTTP, 443 HTTPS, 23 Telnet, 22 SSH), registered 1024–49151, ephemeral 49152–65535 (Linux uses 32768–60999). A **socket** is identified by (protocol, local IP, local port, remote IP, remote port) for TCP; UDP sockets by (local IP, local port).

## UDP (RFC 768 [S13]): 8 bytes

| Field | Bits |
|---|---|
| Source port | 16 (0 = none, no reply expected) |
| Destination port | 16 |
| Length | 16 (header + data, ≥ 8) |
| Checksum | 16 (optional in IPv4: 0 = not computed; a computed value of zero is transmitted as all ones, RFC 768; **mandatory over IPv6**, RFC 8200 §8.1 [S13]) |

Checksum covers a **pseudo-header** (src IP, dst IP, zero, protocol, UDP length), the UDP header and data. The pseudo-header makes a datagram delivered to the wrong host or wrong protocol fail the check even though IP (which is not covered by the UDP checksum) was fine; the price is layer violation: UDP must know the IP addresses, and NAT must fix the checksum.

Properties: connectionless, message boundaries preserved (one `sendto` = one datagram = one `recvfrom`), no ordering, no retransmission, no congestion control (applications must; QUIC does it on top of UDP). Used by DNS, DHCP, NTP, SNMP, RTP/VoIP, QUIC/HTTP-3, games. Max payload 65507 in IPv4; practically keep under ~1400 to avoid fragmentation.

## TCP (RFC 9293 = STD 7, which obsoleted RFC 793 in 2022 [S13]): 20 bytes + options

| Offset | Field | Bits | Meaning |
|---|---|---|---|
| 0 | Source port | 16 | |
| 2 | Destination port | 16 | |
| 4 | **Sequence number** | 32 | byte number of the first payload byte of this segment (SYN and FIN each consume one number) |
| 8 | **Acknowledgement number** | 32 | valid if ACK set: next byte expected from the peer = all bytes below are received (**cumulative**) |
| 12 | Data offset | 4 | header length in 32-bit words (5–15) |
| 12 | Reserved | 4 | |
| 13 | Flags | 8 | CWR ECE **URG ACK PSH RST SYN FIN** (bit 7 … bit 0) |
| 14 | **Window** | 16 | receive window: bytes the sender of this segment can accept beyond the ack number (× scale factor) |
| 16 | Checksum | 16 | over pseudo-header + header + data; mandatory |
| 18 | Urgent pointer | 16 | obsolete in practice |
| 20 | Options | 0–40 | MSS (kind 2, SYN only; **the default when the option is absent is 536**, RFC 9293 §3.7.1), Window scale (kind 3, SYN only, **shift ≤ 14**, RFC 7323 §2.2 [S14]), SACK permitted (4) / SACK blocks (5), Timestamps (8: RTTM and PAWS, RFC 7323 §3, §5); NOP (1) for alignment, EOL (0) |

tcpdump flag letters: S SYN, . ACK only, P PSH, F FIN, R RST. `[S.]` = SYN+ACK.

TCP provides a **reliable, ordered byte stream** with **flow control** (do not overrun the receiver) and **congestion control** (do not overrun the network), full duplex, point to point. No message boundaries: `send(100); send(100)` may be delivered as one `recv(200)` or as 37 + 163 (framing is the application's job, note 10). **MSS** = maximum payload per segment = MTU − 40 (1460 on Ethernet); the sender uses the smaller of both sides' announced values.

### Connection establishment: three-way handshake

| # | A → B | Flags | seq | ack | Effect |
|---|---|---|---|---|---|
| 1 | A → B | SYN | $x$ (ISN$_A$, random) | – | A: SYN-SENT. Options: MSS, WS, SACK-OK, TS |
| 2 | B → A | SYN, ACK | $y$ (ISN$_B$) | $x + 1$ | B: SYN-RECEIVED |
| 3 | A → B | ACK | $x + 1$ | $y + 1$ | both ESTABLISHED; may carry data |

The SYN consumes one sequence number, so the first data byte is $x + 1$. Random ISNs prevent old duplicates from a previous incarnation being accepted and make blind spoofing harder. A SYN to a closed port gets RST. **SYN flood**: attacker sends SYNs and never completes; the server's half-open queue fills → SYN cookies encode the state in the ISN so nothing is stored until the third packet arrives. Simultaneous open exists but is rare.

### Data transfer: sequence and acknowledgement numbers

- A segment carrying bytes $[s, s + L)$ has seq $= s$; the receiver's ack becomes $s + L$ if everything below $s$ has arrived (cumulative), otherwise it repeats the old ack (**duplicate ACK**) and buffers the out-of-order data (SACK tells the sender exactly which blocks).
- Acks are piggybacked on data in the other direction if any; otherwise a pure ACK (no data, seq unchanged). **Delayed ACK**, RFC 1122 §4.2.3.2 [S13]: the delay **MUST be less than 0.5 s**, and an ACK **SHOULD** be sent for at least every second full-sized segment. The familiar 40–200 ms is Linux, not the RFC. It interacts badly with Nagle (RFC 1122 §4.2.3.4): small writes wait for an ACK that is itself being delayed → 40 ms stalls; `TCP_NODELAY`.
- Wireshark shows *relative* seq numbers (starting at 0) by default; exams and tcpdump (`-S`) use absolute.

### Retransmission and RTO (RFC 6298 [S14])

One retransmission timer for the oldest unacked byte. On expiry: retransmit that segment, double the RTO (exponential backoff, §5.5; an implementation **MAY** cap it, provided the cap is **at least** 60 s, §2.5), restart. On a new ACK: restart the timer if data remains. RTT is measured per acked segment (**Karn's algorithm**: never from a retransmitted segment; the Timestamps option removes the ambiguity):

$$\text{RTTVAR} \leftarrow \tfrac{3}{4}\text{RTTVAR} + \tfrac{1}{4}|\text{SRTT} - R'|, \qquad \text{SRTT} \leftarrow \tfrac{7}{8}\text{SRTT} + \tfrac{1}{8}R', \qquad \text{RTO} = \text{SRTT} + \max(G, 4\,\text{RTTVAR})$$

**Order matters**: RFC 6298 rule 2.3 requires RTTVAR to be updated first, using the
*old* SRTT. First sample (rule 2.2): SRTT $= R$, RTTVAR $= R/2$. Before any
sample (rule 2.1): RTO = 1 s.

**Rule 2.4 is the one everybody forgets**: *"Whenever RTO is computed, if it is
less than 1 second, then the RTO SHOULD be rounded up to 1 second."* On a LAN
the formula almost always returns a few milliseconds, so the RFC-conformant RTO
is almost always exactly 1 s. Linux ignores this and uses a 200 ms floor
(`TCP_RTO_MIN`), which is why real traces show sub-second timeouts. State both
in an exam answer: the formula's value **and** the value after rule 2.4.

Waiting for the RTO is slow (it must be conservative), hence **fast retransmit**:
three duplicate ACKs for the same number ⇒ that segment is assumed lost,
retransmit immediately without waiting for the timer (RFC 5681 §3.2 [S14]).

### Flow control: sliding window

The receiver advertises `rwnd` = free buffer space. The sender keeps

$$\text{bytes in flight} = \text{SND.NXT} - \text{SND.UNA} \le \min(\text{rwnd}, \text{cwnd})$$

The window *slides*: each ACK moves SND.UNA up and allows new sends. Throughput is bounded by $W / \text{RTT}$: with the 16-bit window limit of 65535 B and 100 ms RTT that is 5 Mbit/s — the window-scale option fixes it, with a shift capped at 14 (RFC 7323 §2.2 [S14]), so at most $65535 \times 2^{14} \approx 1$ GB. If rwnd = 0 the sender stops and sends **window probes** (1 byte, exponential backoff) so that a lost window update does not deadlock. Silly-window avoidance: receiver does not advertise tiny windows, sender (Nagle) does not send tiny segments while data is unacknowledged.

### Congestion control (RFC 5681 [S14], Reno; CUBIC is the Linux default, BBR model-based)

Sender-side variable `cwnd` estimates what the network can absorb; loss is the congestion signal (or ECN marks).

| Phase | Rule | Exit |
|---|---|---|
| **Slow start** | cwnd = IW; +1 MSS per ACK ⇒ **doubles per RTT** | cwnd ≥ ssthresh → congestion avoidance; loss |
| **Congestion avoidance** | +MSS·MSS/cwnd per ACK ⇒ **+1 MSS per RTT** (additive increase) | loss |
| **Timeout** | ssthresh = max(FlightSize/2, 2·SMSS); cwnd = LW = **1 full-sized segment**; slow start | |
| **3 dup ACKs** (fast retransmit + fast recovery) | ssthresh = max(FlightSize/2, 2·SMSS) — the **same** formula, not plain flight/2; cwnd = ssthresh + 3·SMSS; each further dup ACK +1 SMSS (inflation); on the ACK for new data cwnd = ssthresh, congestion avoidance | "multiplicative decrease" |

Two footnotes on `IW`, because textbooks and the RFC disagree and both get
quoted. **RFC 5681 §3.1's own IW is 2 to 4 segments**, by a rule on SMSS: 4·SMSS
if SMSS ≤ 1095, 3·SMSS up to 2190, else 2·SMSS. The `IW = 10` that every modern
stack ships is **RFC 6928** [S14], which is *Experimental*, not part of RFC 5681.
Exam problems usually say IW = 1 to keep the arithmetic clean; that value is in
neither RFC. Also note `FlightSize`, not `cwnd`, in both ssthresh formulas — RFC
5681 flags using cwnd as "an easy mistake to make".

Result: the sawtooth of **AIMD** (additive increase, multiplicative decrease), which converges to a fair share between flows with equal RTT (Chiu–Jain, *not* in any RFC [S24]). Average throughput of a Reno flow with loss probability $p$: $\approx \frac{1.22 \cdot \text{MSS}}{\text{RTT}\sqrt{p}}$ — Mathis et al. 1997 [S29], also not an RFC — so long RTTs and lossy links get less. Tahoe (no fast recovery, always back to 1 MSS) is the older variant exams sometimes ask to contrast with Reno.

### Teardown

Each direction is closed separately (half-close): A sends FIN (seq $u$), B acks $u + 1$ and may keep sending; later B sends FIN (seq $v$), A acks $v + 1$. Four segments, or three if B's ACK and FIN are combined. The side that closes first enters **TIME-WAIT** for 2·MSL so that (a) its last ACK can be retransmitted if lost and (b) old segments of this connection die before the port pair is reused. **RFC 9293 §3.4.2 takes MSL to be 2 minutes**, so the specified wait is 4 minutes; Linux hardcodes 60 s. Quote whichever you like, but say which. RST aborts immediately (e.g. SYN to a closed port, data to a half-open connection after a crash).

### State machine (RFC 9293 §3.3.2, figure 5, abridged [S13])

| State | Meaning | Transition out |
|---|---|---|
| CLOSED | no connection | passive open → LISTEN; active open, send SYN → SYN-SENT |
| LISTEN | server waiting | rcv SYN, send SYN+ACK → SYN-RECEIVED |
| SYN-SENT | client sent SYN | rcv SYN+ACK, send ACK → ESTABLISHED |
| SYN-RECEIVED | server sent SYN+ACK | rcv ACK → ESTABLISHED |
| ESTABLISHED | data | close, send FIN → FIN-WAIT-1; rcv FIN, send ACK → CLOSE-WAIT |
| FIN-WAIT-1 | sent FIN | rcv ACK → FIN-WAIT-2; rcv FIN → CLOSING; rcv FIN+ACK → TIME-WAIT |
| FIN-WAIT-2 | FIN acked, waiting for peer's FIN | rcv FIN, send ACK → TIME-WAIT |
| CLOSE-WAIT | peer closed, app still may send | close, send FIN → LAST-ACK |
| LAST-ACK | sent FIN after peer's | rcv ACK → CLOSED |
| CLOSING | simultaneous close | rcv ACK → TIME-WAIT |
| TIME-WAIT | 2 MSL | timer → CLOSED |

Two edges the table leaves out, both in the figure's notes: SYN-RECEIVED → LISTEN on RST, only if SYN-RECEIVED was reached by a passive open (note 1; MUST-11 makes the endpoint remember which); RST in any synchronized state → CLOSED (note 3). Simultaneous open runs CLOSED → SYN-SENT → SYN-RECEIVED → ESTABLISHED on *both* sides (Figure 7); simultaneous close runs FIN-WAIT-1 → CLOSING → TIME-WAIT on both (Figure 13), so both wait 2 MSL.

`ss -tan` / `netstat -an` show these states; many CLOSE-WAIT sockets mean an application forgot to close. `src/py/tcp_fsm.py` is the table as code (`TRANSITIONS`, `RST_EDGES`) and replays Figures 6, 7, 8, 12 and 13 of RFC 9293 line by line in `test_tcp_fsm.py`.

## Worked scenario 1: hand-derived trace

A downloads 3000 bytes from B, MSS 1000, ISN$_A$ = 1000, ISN$_B$ = 5000, request is 18 bytes.

| # | Dir | Flags | seq | ack | len | Comment |
|---|---|---|---|---|---|---|
| 1 | A→B | S | 1000 | – | 0 | |
| 2 | B→A | S. | 5000 | 1001 | 0 | |
| 3 | A→B | . | 1001 | 5001 | 0 | established |
| 4 | A→B | P. | 1001 | 5001 | 18 | request bytes 1001–1018 |
| 5 | B→A | . | 5001 | 1019 | 1000 | data 5001–6000, acks request |
| 6 | B→A | . | 6001 | 1019 | 1000 | |
| 7 | B→A | P. | 7001 | 1019 | 1000 | |
| 8 | A→B | . | 1019 | 8001 | 0 | cumulative ack of all three |
| 9 | B→A | F. | 8001 | 1019 | 0 | B closes, FIN takes number 8001 |
| 10 | A→B | F. | 1019 | 8002 | 0 | A acks FIN and closes (combined) |
| 11 | B→A | . | 8002 | 1020 | 0 | A: LAST-ACK → CLOSED; B: TIME-WAIT |

States, because the teardown is where answers go wrong: **B closed first**, so B is the one that waits. B: ESTABLISHED →(#9 snd FIN) FIN-WAIT-1 →(#10 rcv FIN that also acks its FIN, Figure 5 note 2) TIME-WAIT. A: ESTABLISHED →(#9 rcv FIN) CLOSE-WAIT →(#10 CLOSE, snd FIN) LAST-ACK →(#11 rcv ACK of FIN) CLOSED. `test_tcp_fsm.py::test_note05_scenario1_numbers_and_who_ends_in_time_wait` replays all eleven rows through the state machine.

If segment 6 were lost: A acks 6001 after #7 (dup ACK #1); B would need three dup ACKs for fast retransmit, only one arrives (nothing else in flight) → B waits for the RTO, retransmits 6001, then A acks 8001 in one go (it had buffered 7001–8000).

## Worked scenario 2: simulator output (`tcp_sim.py`, 20 segments, transmissions 6 and 13 dropped, RTT 100 ms)

```
0.000  send   seq=0          cwnd=1  slow start
0.100  ack    ack=1000       cwnd=2            +1 MSS per ACK: 1,2,3,4,5,6 ...
0.200  send   seq=5000  ** LOST **
0.300  dupack ack=5000 #1                      6000..10000 arrive out of order
0.400  dupack ack=5000 #3
0.400  FASTRX retransmit 5000  cwnd=6 ssthresh=3    ssthresh = 6/2, fast recovery
0.500  ack    ack=11000       cwnd=3  cong.avoid    one ACK covers the whole buffered run
0.500  dupack ack=11000 #1 .. #2                    second loss: only 2 dup ACKs possible
0.700  TIMEOUT retransmit 11000  cwnd=1 ssthresh=2 rto=0.40   RTO doubled
0.800  ack    ack=14000       cwnd=2                slow start until ssthresh=2, then +1/RTT
1.100  done   all 20000 bytes acked
```

What to read off: doubling in slow start; a loss with enough data behind it is repaired by fast retransmit after ~1 RTT; a loss at the tail (nothing to generate dup ACKs) costs a full RTO; ssthresh remembers half the flight size; RTO backs off.

## Pitfalls

- ack = next expected byte, not "last received". ack 1019 means bytes up to 1018 arrived.
- SYN and FIN each consume one sequence number; pure ACKs consume none (that is why the ack number of a pure ACK's reply does not advance).
- Window field is the *receiver's* buffer, not the sender's cwnd; cwnd is never on the wire.
- Three *duplicate* ACKs means four ACKs with the same number.
- Fast retransmit needs at least 3 segments after the lost one in flight; small transfers time out instead.
- UDP "unreliable" does not mean the checksum is missing; it means no retransmission.
- Slow start is not slow: it is exponential. It is slower than the original "send a full window at once".

## Exam-style questions

1. *A sends 2 segments of 500 B starting at seq 3001; the first is lost. What does B ack after receiving the second?* ack = 3001 (dup ACK, expecting the lost bytes), and it buffers 3501–4000 (with SACK: `SACK 3501-4001`).
2. *RTT samples 100 ms then 200 ms, initial RTO 1 s. RTO after each?* First sample (rule 2.2): SRTT = 0.1, RTTVAR = 0.05, RTO = 0.1 + 4·0.05 = **0.3 s → rounded up to 1 s by rule 2.4**. Second sample (rule 2.3, RTTVAR first with the old SRTT): RTTVAR = 0.75·0.05 + 0.25·|0.1 − 0.2| = 0.0625, then SRTT = 0.875·0.1 + 0.125·0.2 = 0.1125, RTO = 0.1125 + 4·0.0625 = **0.3625 s → again 1 s**. Give both numbers: the formula's value shows you can compute it, the rounding shows you read RFC 6298 [S14]. A Linux box with its 200 ms floor would report 0.3 and 0.3625 unchanged.
3. *cwnd 8 MSS, ssthresh 16 MSS, no loss: cwnd after 2 RTTs? After 4?* Slow start: 16 after one RTT, reaching ssthresh → congestion avoidance: 17 after two, 19 after four.
4. *cwnd 32 MSS in congestion avoidance; timeout vs. 3 dup ACKs: cwnd and ssthresh afterwards (Reno)?* Both use ssthresh = max(FlightSize/2, 2·SMSS) = 16 (assuming the window was full, so FlightSize = 32). Timeout: cwnd = LW = 1, slow start. 3 dup ACKs: cwnd = 16 + 3 = 19 during fast recovery, then 16 and congestion avoidance on the ACK for new data [S14].
5. *Why does the side that closes first wait in TIME-WAIT, and why is it a problem for busy servers?* To retransmit the final ACK if the peer's FIN is repeated and to let stray segments expire before the 4-tuple is reused. A server actively closing thousands of connections holds thousands of 4-tuples for 60 s (port exhaustion); hence servers let clients close first, or use SO_REUSEADDR/timestamps.
6. *Max throughput of one TCP flow, window 64 kB, RTT 200 ms?* $65535 \cdot 8 / 0.2 \approx 2.6$ Mbit/s regardless of link speed; needs window scaling (RFC 7323, shift ≤ 14) [S14].

## Code

`src/py/headers.py`: `build_udp/parse_udp`, `build_tcp/parse_tcp`, `parse_tcp_options`, `pseudo_header`. `src/py/tcp_sim.py`: `TCPSim` (sequence/ack bookkeeping, `update_rto` per RFC 6298, slow start/AIMD/fast retransmit) with scripted losses via `Link(drop={...})`; `python tcp_sim.py` prints scenario 2. `src/py/tcp_fsm.py`: `Endpoint` (open/send/close/receive, RFC 9293 §3.3.2 and §3.4 numbering), `Segment` (prints the RFC's `<SEQ=…><ACK=…><CTL=…>` notation); `python tcp_fsm.py` prints Figures 6 and 12. `src/py/pcap.py::synthetic_trace()` is scenario 1's shape as bytes (same ISNs and 18-byte request, but one 40-byte response segment instead of 3 × 1000), and `test_tcp_fsm.py::test_pcap_synthetic_trace_is_a_legal_walk` checks it segment by segment against the state machine.
