# 11 Exercise playbook

> **Sourcing.** The five exercises and their placement (after lectures 7, 9,
> 16, 19, 22; 20 points each) come from the TISS examination modalities [S1],
> which still state them on 2026-09-27. The three exercise *types* below come
> from the TISS practical-part text, "describing packet traces received",
> "deriving a topology based on provided information" and "describe TCP
> behavior given a specific scenario": **stated on TISS until 2026-09-2x,
> removed by 2026-09-27** (last recorded here 2026-09-22). Since then the
> types are inference from the learning outcome "solve networking and routing
> scenarios", not a TISS statement; confirm in the first lecture. **No past
> exercise sheet exists**: 191.030 is new in 2026W and has no previous
> offering [S2], no VoWi page [S7] and no public material [S5]. No TUWEL course
> is linked from TISS (2026-09-27). See [`00-exam-focus.md`](00-exam-focus.md)
> for the release dates (from the course page since 2026-10-09 [S36]).

The five exercises (after lectures 7, 9, 16, 19, 22; 20 points each, 100 h budget, 100 of the 300 points) [S1] were described, until the removal above, as *describe packet traces*, *derive topologies from partial information*, and *explain TCP behaviour in a scenario*. This note is the procedure for each, plus the tool cheat sheet (`src/sh/tools_cheatsheet.sh`). Note the arithmetic from [`00-exam-focus.md`](00-exam-focus.md): the exercises alone cannot pass the course (100 < 150), but they are half the distance. Release dates, as marked on the course page on 2026-10-09 [S36]: 19.10, 09.11, 23.11, 14.12.2026 and 11.01.2027; the first three fall before the mid-term on 30.11. (An earlier derivation from TISS, lecture $N$ in slot $\lceil N/2 \rceil$, gave 09.11, 16.11, 07.12, 11.01, 18.01 and was wrong; see note 00.) Deadlines are not published yet.

## A. Reading a packet trace

Work outside-in, one layer at a time, and write down what each header tells you before interpreting the whole.

1. **Get the frames in order**: `tcpdump -n -r file.pcap -tttt -e` (absolute time, MACs) or `tshark -r file.pcap`. Add `-x` for hex when a field matters. Wireshark: disable relative sequence numbers if the exercise gives absolute ones.
2. **Layer 2**: src/dst MAC, EtherType, VLAN tag. Same src MAC for many src IPs → that MAC is a router. Broadcast dst → ARP request, DHCP discover. `33:33:…`/`01:00:5e:…` → multicast (NDP, mDNS, OSPF).
3. **Layer 3**: src/dst IP, protocol, TTL, DF/MF/offset, ID. TTL 64/128/255 minus observed = hop count from the sender (initial value guessed from the OS). Fragments share the ID; only offset 0 carries the L4 header. IPv6: hop limit 255 on NDP.
4. **Layer 4**: ports (which side is the server: the well-known/lower port, the side that received the SYN), flags, seq/ack/len, window, options (MSS, WS, SACK in the SYNs only).
5. **Application**: DNS ID/flags/sections, HTTP request line, Telnet IAC sequences.
6. **Reconstruct the story**: group into flows (`tshark -q -z conv,tcp`), order by time, and narrate: "host A resolves name, ARPs for gateway, opens TCP to B:80, …". Explain every *anomaly*: retransmission (same seq again, `tcp.analysis.retransmission`), dup ACKs, zero window, RST, ICMP errors, out-of-order arrival, long gaps (= timeouts, compute the RTO), TTL exceeded.

Checklist of numbers to compute: RTT from SYN→SYN/ACK; bytes transferred from final ack − ISN − 1 (minus FIN); throughput = bytes / (last data time − first data time); MSS from the option; number of hops from TTL; expected next seq = seq + len.

`headers.summarize()` and `pcap.read_pcap()` do steps 1–4 for synthetic traces; `test_pcap.py` shows the flag sequence of a complete session.

## B. Deriving a topology from partial information

Given: some addresses/masks, some routing tables, a traceroute, an ARP table, or a trace. Wanted: the missing subnets, interfaces, next hops, or a drawing.

1. **Subnets from addresses**: compute network/broadcast for every address+mask (`subnet.network_info`). Two addresses in the same network share a link (through switches). A router has one address in each subnet it connects.
2. **Links from ARP/neighbour tables**: an ARP entry means "same L2 segment". A MAC seen as the source for foreign IPs is a router interface.
3. **Hops from traceroute**: each line is the *ingress* interface of the router on the path (the address facing you). Reverse-path traceroute shows the other interfaces. `* * *` = no ICMP, not necessarily no router.
4. **Routing tables**: every next hop must be in a directly connected subnet of that router; walk the tables from source to destination, applying LPM at each router (`subnet.ForwardingTable`). If a destination is unreachable, find the router lacking a route, or the TTL/loop.
5. **Consistency checks**: no two interfaces with the same address; masks agree on both ends of a link (mismatch → one side ARPs for addresses the other side thinks are remote); default gateway inside the host's subnet; routes symmetric unless the exercise says otherwise (asymmetric routing is common inter-domain, note 06).
6. **Draw**: routers as boxes with interface addresses, subnets as labelled segments with prefix, hosts attached; add costs for the routing-algorithm exercises and run Dijkstra/Bellman-Ford on paper (`linkstate.dijkstra_trace`, `distvector.DVNetwork`).

Worked: hosts 10.1.2.7/24 and 10.1.2.9/24, router R with 10.1.2.1/24 and 10.1.3.1/24, host 10.1.3.5/24, traceroute from .2.7 to .3.5 shows `10.1.2.1, 10.1.3.5`. Topology: two subnets joined by R; .2.7's table needs `10.1.3.0/24 via 10.1.2.1` or a default; R needs no routes beyond connected. If .2.7 is configured as /16, it ARPs for 10.1.3.5 directly and gets no reply (unless R does proxy ARP).

## C. Describing TCP behaviour in a scenario

Given: MSS, RTT, initial cwnd/ssthresh, which segments are lost, receiver window, maybe RTO. Wanted: the sequence of segments, cwnd over time, when what is retransmitted, total time.

If the scenario is about connection *state* (who is in TIME-WAIT, what a SYN to a closed port gets, simultaneous open or close), walk RFC 9293 Figure 5 instead: one row per segment, both peers' states *after* it, SYN and FIN each consuming one sequence number. `tcp_fsm.Endpoint` does exactly that and prints segments in the RFC's `<SEQ=…><ACK=…><CTL=…>` notation. The side that sends the first FIN ends in TIME-WAIT and the other side does not (note 05, scenario 1), except in a simultaneous close, where both do (Figure 13).

Procedure for data transfer (mirrors `tcp_sim.py`):

1. Draw a time line with one row per RTT; on each row list segments sent (seq numbers), then the ACKs that come back one RTT later.
2. Track four variables per row: `snd_una`, `snd_nxt`, `cwnd`, `ssthresh`, plus the phase. Send while `snd_nxt − snd_una < min(cwnd, rwnd)`.
3. Slow start: cwnd += MSS per ACK (doubling per row); congestion avoidance: += MSS per row.
4. For a lost segment: the ACKs for later segments all carry the same ack number (dup ACKs). Count them: ≥ 3 → fast retransmit at that moment, `ssthresh = max(FlightSize/2, 2·SMSS)`, cwnd = ssthresh (+3·SMSS during recovery), continue in congestion avoidance after the recovery ACK. < 3 → wait for the RTO, then the same ssthresh formula, cwnd = 1 full-sized segment, slow start again, RTO doubles (RFC 5681 §3.1–3.2, RFC 6298 §5.5 [S14]). **State the RTO carefully**: 1 s before any sample, otherwise SRTT + 4·RTTVAR — *rounded up to 1 s if it comes out lower*, RFC 6298 rule 2.4.
5. After the retransmission arrives, the receiver acks everything it had buffered in one cumulative ACK (or per SACK).
6. Teardown: FIN from the side that finishes; count 2 MSL for TIME-WAIT if asked.
7. Sanity: total bytes / total time vs. the theoretical `min(cwnd, rwnd)/RTT` bound; check every seq = previous seq + previous len.

Phrases worth using, because each names a mechanism precisely: "cumulative acknowledgement", "three duplicate ACKs trigger fast retransmit without waiting for the RTO", "ssthresh becomes max(FlightSize/2, 2·SMSS)" — say FlightSize, not cwnd, which RFC 5681 calls out as the easy mistake — "slow start is exponential per RTT", "the receiver window limits the sender independently of cwnd", "Karn: no RTT sample from a retransmitted segment" [S14]. *(These are our suggestions; no marking scheme for this course is public [S2].)*

## D. Tool cheat sheet (details and more variants in `src/sh/tools_cheatsheet.sh`)

| Task | Linux | macOS/BSD |
|---|---|---|
| interfaces, MACs, addresses | `ip link`, `ip -br addr` | `ifconfig` |
| ARP / NDP cache | `ip neigh` | `arp -an`, `ndp -an` |
| routing table / lookup | `ip route`, `ip route get DST`, `ip -6 route` | `netstat -rn`, `route -n get DST` |
| sockets and TCP states | `ss -tulpn`, `ss -tan` | `netstat -an -p tcp`, `lsof -nP -iTCP` |
| DNS | `dig NAME TYPE`, `dig +short`, `dig @SERVER +dnssec`, `dig +trace`, `dig -x IP`, `dig +norecurse` | same |
| path | `traceroute -n HOST` (UDP), `-I` ICMP, `traceroute6`, `mtr` | same (`traceroute` is ICMP-capable with `-I`) |
| MTU probe | `ping -M do -s 1472 HOST` | `ping -D -s 1472 HOST` |
| capture | `tcpdump -i IF -n -e -c N 'filter'`, `-w file.pcap -s 0` | same (`-i en0`) |
| read capture | `tcpdump -n -r file -tttt`, `tshark -r file -Y 'display filter' -T fields -e ip.src -e tcp.seq` | same |
| hand-made endpoints | `nc -l PORT`, `nc HOST PORT`, `nc -u`, `nc -zv HOST PORTS` | same (`nc` flags differ slightly) |

BPF capture filters (tcpdump): `host 10.0.0.1`, `net 10.0.0.0/24`, `port 53`, `tcp`, `udp`, `icmp`, `arp`, `vlan`, `tcp[tcpflags] & (tcp-syn|tcp-fin) != 0`, `ip[8] < 5` (TTL), combine with `and/or/not`. Wireshark display filters (tshark `-Y`): `ip.addr==`, `tcp.port==`, `tcp.flags.syn==1 && tcp.flags.ack==0`, `tcp.analysis.retransmission`, `tcp.analysis.duplicate_ack`, `tcp.analysis.zero_window`, `dns.flags.response==1`, `icmp.type==11`, `arp.opcode==1`, `frame.time_delta_displayed > 1`.

Capture needs root (`sudo`); reading a file does not. Capture on the *right* interface (`tcpdump -D`), with `-n` to avoid DNS lookups polluting the trace, and `-s 0` to keep whole packets.

## Pitfalls seen in exercises

- Mixing up which side is the client: look for the SYN without ACK.
- Reading the window field as cwnd, or the ack as "last byte received".
- Forgetting that ARP happens once and is then cached: the second connection to the same host has no ARP.
- Assuming traceroute hops are hosts on the path in both directions.
- Computing hosts in a /30 as 4, or forgetting to subtract network and broadcast.
- Treating `* * *` as a down router; treating a missing DNS answer as a routing problem.
- Declaring a retransmission where a segment is merely out of order (check seq numbers and timing, not just duplicates).

## Exam-style questions

1. *Trace line: `IP 10.0.0.5.40000 > 203.0.113.10.80: Flags [S], seq 1000, win 64240, options [mss 1460,wscale 7,sackOK]`. What can you say?* Client 10.0.0.5 opens a connection to a web server; ISN 1000; it can receive 64240 B now and up to 64240·2⁷ after the handshake; it accepts 1460-byte segments; it supports SACK; TTL not shown; the next packet expected is `[S.]` with ack 1001.
2. *Received TTL 249 from an unknown host. How far away is it?* Initial 255 (network device/BSD) → 6 hops; if it were Linux (64) it would be negative, so 255 is the only consistent initial value. The initial values are OS conventions, not RFC 791 [S13], so the inference is a guess with a strong prior, and an answer should say so.
3. *An ARP table on host H shows 10.0.0.1 and 10.0.0.9 with the same MAC. Interpretations?* Proxy ARP by the router 10.0.0.1 for .9 (which is elsewhere), a host with two addresses on one interface, or ARP spoofing (attacker claims .1). Decide by checking whether .9 answers ping with a TTL consistent with one hop and whether the MAC's OUI is a router vendor.
4. *A transfer of 100 kB over a link with RTT 100 ms and no loss, MSS 1000, IW 1: how many RTTs for the data (ignore handshake)?* Slow start sends 1, 2, 4, …, so after $k$ RTTs $2^k - 1$ segments are acked; 100 segments need $2^k - 1 \ge 100$ → $k = 7$ RTTs = 0.7 s. With IW 10 (RFC 6928 [S14], what stacks actually ship): 10, 20, 40, 80 → 4 RTTs. Note that IW 1 is in no RFC — RFC 5681 §3.1's own initial window is 2 to 4 segments — so say which IW you assumed.
5. *Two traces of the same download, one with 3 % random loss: describe the difference qualitatively.* Lossy: sawtooth cwnd, frequent fast retransmits (dup ACK triples), occasional timeouts with idle gaps of ≥ 1 s (RFC 6298's minimum, rule 2.4) and slow-start restarts, out-of-order segments and SACK blocks; throughput ≈ $1.22\,\text{MSS}/(\text{RTT}\sqrt{p})$ [S29], i.e. a fraction of the lossless run and independent of link speed.

## Code

`src/py/headers.py` (`summarize`, `parse_frame`), `src/py/pcap.py` (`read_pcap`, `synthetic_trace`), `src/py/subnet.py` (`network_info`, `ForwardingTable`), `src/py/tcp_sim.py` (`TCPSim` with scripted losses), `src/py/tcp_fsm.py` (`Endpoint`, `TRANSITIONS`: connection states), `src/sh/tools_cheatsheet.sh --dry-run [section]`.
