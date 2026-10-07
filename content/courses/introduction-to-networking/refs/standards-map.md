# Standards map — which RFC section says what, and where we use it

The analogue of a lecture-notes map for a course that has no lecture notes
[S1, S7]. All 52 files are in `rfc/`; the source register is
[`SOURCES.md`](SOURCES.md).

Read a row as: *this section of this RFC is the authority for this part of our
note, and this is the code that implements it.*

## Note 01 — Foundations and governance

| RFC | § | what it fixes | note | code |
|---|---|---|---|---|
| 761 | 2.10 | robustness principle, original wording | 01 | — |
| 9413 | 2, 3 | why the robustness principle ossifies protocols | 01 | — |
| 1122 | 1.1.3, 1.2.2 | the Internet layering model; robustness restated | 01 | — |
| 1122 | 1.1.3 | "a router processes up to the internet layer" | 01 | `headers.parse_frame` |

Not in any RFC: the end-to-end argument [S26], the delay decomposition [S24],
and the whole governance section — IETF/IANA/ICANN/RIR roles are described by
those bodies' own pages and by BCP 9 / BCP 78, which this pass did not fetch.
Note 01 marks that section accordingly.

## Note 02 — Ethernet and ARP

| RFC | § | what it fixes | note | code |
|---|---|---|---|---|
| 826 | "Packet Generation" | when a host ARPs at all | 02 | — |
| 826 | "Packet Reception" | **merge-then-target**: every host updates an existing entry for the sender, only the target adds one | 02 | `headers.parse_arp` |
| 826 | "Generalization" | `<ar$hrd, ar$hln> = <1, 6>` for Ethernet | 02 | `headers.build_arp` |
| 2464 | 2, 7 | IPv6 over Ethernet: EtherType 0x86DD, multicast → 33:33 + low 32 bits | 02, 04, 09 | — |

Ethernet framing itself (preamble, 46–1500 payload, 64-byte minimum, FCS,
802.1Q tag, interframe gap) is IEEE 802.3 / 802.1Q [S30], which is **not**
vendorable. Note 02 marks those numbers as IEEE-sourced but unverified here.

## Note 03 — IPv4

| RFC | § | what it fixes | note | code |
|---|---|---|---|---|
| 791 | 3.1 | header fields and widths; Flags/Fragment Offset semantics | 03 | `headers.build_ipv4` |
| 791 | 3.2 "Fragmentation" | offset counts **8-byte** units; only the destination reassembles | 03 | `headers.fragment_ipv4`, `reassemble_ipv4` |
| 791 | 3.2 "Time to Live" | TTL is a hop count, decremented at every router | 03 | — |
| 1071 | 1, 2 | Internet checksum: one's-complement sum, end-around carry, complement; byte-order independence; 32-bit summation | 03 | `inet_checksum.checksum`, `ones_sum`, `ones_sum32`, `ones_sum_split` |
| 1071 | 3 | the worked sums of 0001 f203 f4f5 f6f7: **ddf2** (normal, 32-bit, odd split), f2dd (swapped). The RFC prints sums only; the checksum 0x220d is their complement | 03 | `test_rfc_vectors` |
| 1624 | 3, 4 | incremental update, eq. 3; the worked 0x5555 → 0x3285 example | 03 | `inet_checksum.incremental_checksum_update` |
| 792 | pp. 4–8 | ICMP types 0/3/5/8/11/12; error quotes header + 64 bits | 03 | — |
| 1191 | 3, 4 | PMTUD; the MTU field in ICMP type 3 code 4 | 03 | — |
| 1918 | 3 | 10/8, 172.16/12, 192.168/16 | 03 | `subnet.network_info`, `split_subnet` |
| 1122 | 3.3.1.1 | local/remote decision: address AND mask | 03, 06 | `subnet.same_subnet` |
| 3021 | 2.1 | /31: two usable addresses, no broadcast | 03 | `subnet.network_info` |
| 5737 | 1 | 192.0.2/24, 198.51.100/24, 203.0.113/24 | 03, all | all worked examples |
| 6598 | 1, 4 | 100.64/10 Shared Address Space | 03 | — |
| 3022 | 2.2, 4.1 | NAPT; checksum fix-up; ALG requirement | 03 | — |
| 3168 | 5 | ECN bits in the IPv4 TOS byte | 03, 05 | `headers.build_ipv4` |
| 2827 | 3 | BCP 38 ingress filtering | 03, 08 | — |

## Note 04 — IPv6

| RFC | § | what it fixes | note | code |
|---|---|---|---|---|
| 8200 | 3 | the 40-byte header; Payload Length **excludes** it | 04 | `headers.build_ipv6` |
| 8200 | 4 | extension-header chain and Next Header values | 04 | — |
| 8200 | 5 | minimum link MTU 1280; routers never fragment | 04 | — |
| 4291 | 2.2 | text representation; `::` at most once | 04 | `subnet.parse_ipv6` |
| 4291 | 2.3 | prefix notation; the 2001:0DB8:0:CD30::/60 legal and illegal spellings | 04 | `subnet.ipv6_prefix` |
| 4291 | 2.4, 2.5.6 | address type table; fe80::/10 link-local | 04 | `subnet.ForwardingTable(version=6)` |
| 4291 | 2.5.1, App. A | 64-bit IID; modified EUI-64 (insert ff:fe, flip the u bit) | 04 | — |
| 4291 | 2.7.1 | **solicited-node ff02::1:ff00:0/104** | 04 | `subnet.solicited_node` |
| 4291 | 2.6 | anycast | 04, 09 | — |
| 5952 | 4.1–4.3 | no leading zeros; `::` maximal but never for one group (4.2.2); the **longest** run, leftmost on a tie (4.2.3); lower case | 04 | `subnet.ipv6_compress` |
| 4193 | 3 | ULA fc00::/7, random 40-bit global ID | 04 | — |
| 6164 | 1, 5 | /127 on inter-router links | 04 | — |
| 4861 | 4.1–4.5 | RS/RA/NS/NA/Redirect = ICMPv6 133–137 | 04 | — |
| 4861 | 3.1, 11.2 | **Hop Limit 255** on receipt, so NDP cannot be spoofed off-link | 04 | — |
| 4861 | 7.3.2 | neighbour-cache states INCOMPLETE…PROBE | 04 | — |
| 4862 | 5.3–5.5 | SLAAC: link-local first, then RA prefixes with A set | 04 | — |
| 4862 | 5.4 | Duplicate Address Detection from the unspecified source | 04 | — |
| 8106 | 5 | RDNSS / DNSSL options in an RA | 04 | — |
| 7217 | 5 | stable, opaque, per-prefix IIDs | 04 | — |
| 8981 | 3.3 | temporary (privacy) addresses | 04 | — |
| 8305 | 3–5 | Happy Eyeballs v2 | 04, 10 | `sockets_echo` (getaddrinfo iteration) |

## Note 05 — UDP and TCP

| RFC | § | what it fixes | note | code |
|---|---|---|---|---|
| 768 | p. 1 | the four 16-bit fields; the pseudo-header; checksum 0 means "not computed", transmitted as all ones when it computes to zero | 05 | `headers.build_udp`, `pseudo_header` |
| 8200 | 8.1 | the UDP checksum is **mandatory** over IPv6 | 04, 05 | `headers.pseudo_header` |
| 9293 | 3.1 | header layout; the eight control bits | 05 | `headers.build_tcp` |
| 9293 | 3.4 | sequence-number semantics; SYN and FIN each consume one | 05 | `tcp_fsm.Segment`, `tcp_sim.TCPSim` |
| 9293 | 3.4.1 | ISN selection | 05 | — |
| 9293 | 3.4.2 | **MSL is 2 minutes**, so 2·MSL is 4 minutes | 05 | — |
| 9293 | 3.5 | three-way handshake (Fig. 6), simultaneous open (Fig. 7), old duplicate SYN (Fig. 8), RST rules | 05 | `tcp_fsm.Endpoint`, `pcap.synthetic_trace` |
| 9293 | 3.6 | normal and simultaneous close (Figs. 12, 13); TIME-WAIT | 05 | `tcp_fsm.Endpoint` |
| 9293 | 3.7.1 | default MSS 536; MSS option | 05 | `headers.tcp_option_mss` |
| 9293 | fig. 5 / 3.3.2 | the state machine, with notes 1–3 | 05, 11 | `tcp_fsm.TRANSITIONS`, `RST_EDGES` |
| 9293 | 3.9.1 | the abstract user interface (OPEN, SEND, RECEIVE, CLOSE) that sockets implement | 10 | `sockets_echo.tcp_server` |
| 1122 | 4.2.3.2 | delayed ACK **MUST** be under 0.5 s, and at least every second segment | 05 | — |
| 1122 | 4.2.3.4 | silly-window avoidance; Nagle | 05 | — |
| 7323 | 2.2 | window scale, shift ≤ 14 | 05 | `headers.parse_tcp_options` |
| 7323 | 3, 5 | timestamps, RTTM, PAWS | 05 | — |
| 6298 | 2.1–2.5 | initial RTO 1 s; α = 1/8, β = 1/4, K = 4; **rule 2.4 rounds up to 1 s**; max ≥ 60 s | 05 | `tcp_sim.TCPSim.update_rto` |
| 6298 | 3 | Karn: no sample from a retransmitted segment | 05 | `tcp_sim.TCPSim.transmit` |
| 6298 | 5.5 | exponential backoff | 05 | `tcp_sim.TCPSim.on_timeout` |
| 5681 | 3.1 | slow start, congestion avoidance, `ssthresh = max(FlightSize/2, 2·SMSS)`, loss window 1 segment | 05 | `tcp_sim.TCPSim.on_ack`, `on_timeout` |
| 5681 | 3.1 | the RFC's **own IW is 2–4 segments**, not 10 | 05 | — |
| 6928 | 2 | the experimental IW10 that stacks ship | 05 | — |
| 5681 | 3.2 | fast retransmit on 3 dup ACKs; fast recovery inflation | 05 | `tcp_sim.TCPSim.on_ack` |
| 3168 | 6.1 | ECE/CWR handshake | 05 | `headers.TCP_FLAGS` |

Not in any RFC: the √p throughput model [S29] and the AIMD fairness argument
[S24].

## Notes 06 and 07 — forwarding, routing, OSPF, BGP

| RFC | § | what it fixes | note | code |
|---|---|---|---|---|
| 2328 | A.1 | OSPF is IP protocol 89; AllSPFRouters 224.0.0.5, AllDRouters 224.0.0.6 | 07 | `ospf.IP_PROTOCOL`, `ALL_SPF_ROUTERS` |
| 2328 | 7.1–7.4 | Hello, adjacencies, DR/BDR, areas | 07 | — |
| 2328 | 9.4 | DR/BDR election | 07 | — |
| 2328 | 10.5 | a Hello is only accepted if mask, HelloInterval and RouterDeadInterval match | 07 | `ospf.adjacency_possible` |
| 2328 | 12.1 | an LSA is identified by (type, Link State ID, advertising router) | 07 | `ospf.LSA.identity` |
| 2328 | 13, 13.1 | flooding; **which instance is newer** | 07 | `ospf.which_is_newer`, `install` |
| 2328 | 16.1 | the SPF calculation = Dijkstra on the LSDB | 07 | `linkstate.dijkstra` |
| 2328 | **App. B** | architectural constants: LSRefreshTime 30 min, MinLSInterval 5 s, MinLSArrival 1 s, MaxAge 1 h, CheckAge 5 min, MaxAgeDiff 15 min, LSInfinity 0xffffff | 07 | `ospf.ARCHITECTURAL` |
| 2328 | **App. C.3** | configurable: HelloInterval "sample … 10 seconds", RxmtInterval 5 s, InfTransDelay 1 s, RouterDeadInterval "some multiple … (say 4)", cost > 0 and **no formula** | 07 | `ospf.SAMPLE_LAN`, `hello_dead_pair` |
| 4271 | 3, 8.2.2 | BGP runs over **TCP 179** | 06 | `bgp_decision.PORT` |
| 4271 | 4.3 | UPDATE, path attributes, ORIGIN values IGP < EGP < INCOMPLETE | 06, 07 | `bgp_decision.ORIGIN` |
| 4271 | 5.1.2 | AS_PATH, loop detection by finding your own AS | 07 | `pathvector.PathVectorNetwork.step` |
| 4271 | 5.1.5 | LOCAL_PREF is iBGP-only | 06, 07 | `bgp_decision.degree_of_preference` |
| 4271 | 9.1.1 | phase 1: degree of preference — **where LOCAL_PREF actually acts** | 07 | `bgp_decision.degree_of_preference` |
| 4271 | **9.1.2.2** | the seven tie-breaks a–g, in order; AS_SET counts as 1; MED only within one neighbour AS | 07 | `bgp_decision.TIE_BREAKS`, `_filter_med` |
| 4271 | 9.2.1.1 | MRAI, and why iBGP's must be shorter | 07 | `bgp_decision.TIMERS` |
| 4271 | **10** | ConnectRetryTime 120 s, HoldTime 90 s, Keepalive = HoldTime/3, MinASOriginationInterval 15 s, MRAI 30 s eBGP / 5 s iBGP, jitter ×U(0.75, 1) | 06, 07 | `bgp_decision.TIMERS` |
| 6793 | 1, 3 | 4-octet AS numbers | 06 | — |
| 4760 | 3, 4 | multiprotocol BGP: AFI/SAFI, MP_REACH_NLRI | 06, 09 | — |

Not in any RFC, and note 06/07 say so: the customer/peer/provider preference and
valley-free export rules [S27], the possibility of non-convergence [S28],
Cisco's administrative-distance numbers, the OSPF reference-bandwidth cost
formula, and "prefer the older route" as a tie-break.

## Note 08 — DNS, DNSSEC, Telnet

| RFC | § | what it fixes | note | code |
|---|---|---|---|---|
| 1034 | 3.1–3.7 | namespace, zones, delegation, aliases, the resolver algorithm | 08 | — |
| 1034 | 4.3.2 | the iterative resolution loop a recursive resolver runs | 08 | — |
| 1035 | 2.3.1, 2.3.3, 2.3.4 | label ≤ 63, name ≤ 255 (enforced), case-insensitive | 08 | `dns.encode_name` |
| 1035 | 3.2.2 | type codes | 08 | `dns.TYPES` |
| 1035 | 4.1.1 | header: ID, QR, Opcode, AA, TC, RD, RA, RCODE, four counts | 08 | `dns.build_header` |
| 1035 | 4.1.4 | **message compression**: a length byte with the top two bits 11 is a 14-bit backward pointer; the F.ISI.ARPA / FOO.F.ISI.ARPA / ARPA figure, rebuilt byte for byte | 08 | `dns.encode_name`, `decode_name`, `build_response` |
| 1035 | 4.2.1 | UDP messages are limited to **512 bytes**; TC then TCP | 08 | — |
| 6891 | 6.1, 6.2 | EDNS(0): the OPT pseudo-RR, requestor's payload size, the DO bit | 08 | `dns.build_query(dnssec_ok=True)` |
| 4033 | 3, 5 | DNSSEC goals; the four validation states; AD and CD | 08 | — |
| 4034 | 2.1 | DNSKEY RDATA; flag 256 = zone key, 257 = KSK/SEP | 08 | `dnssec.dnskey_rdata` |
| 4034 | 3.1 | RRSIG fields and the validity window | 08 | — |
| 4034 | 5.1.4 | **DS digest = H(canonical owner name ‖ DNSKEY RDATA)** | 08 | `dnssec.ds_digest` |
| 4034 | **5.4** | the worked example: key tag 60485, DS SHA-1 2BB183AF… | 08 | `test_rfc_vectors` |
| 4034 | 6.2 | canonical name form | 08 | `dnssec.canonical_name` |
| 4034 | **App. B** | the key-tag algorithm, and that it is *not* the Internet checksum | 08 | `dnssec.key_tag` |
| 4035 | 3.2.3, 5.5 | AD bit; SERVFAIL on failed validation | 08 | — |
| 8482 | 4 | minimal ANY responses | 08 | — |
| 854 | pp. 3–14 | NVT; IAC = 255; WILL 251 / WONT 252 / DO 253 / DONT 254; SB 250, SE 240 | 08, 10 | `telnet_client_sketch.parse_stream` |
| 855 | whole | the option-negotiation framework | 08, 10 | `telnet_client_sketch.negotiate` |
| 1143 | 2, 7 | the **Q method**: answer every request that proposes a change (a repeated DO for a refused option is refused again), never one that does not, never answer a refusal with a new request; the section 7 receipt tables row by row | 08, 10 | `telnet_client_sketch.QOption`, `Negotiator` |

## Note 09 — unicast and multicast routing

| RFC | § | what it fixes | note | code |
|---|---|---|---|---|
| 1112 | 4 | IPv4 multicast addressing, TTL scoping | 09 | — |
| 1112 | **6.4** | group → `01:00:5E` + **low 23 bits**, so 32 groups share a MAC | 09 | `subnet.multicast_mac` |
| 2236 | 2, 8.2 | IGMPv2 messages; **Query Interval 125 s**; Max Response Time; Leave | 09 | — |
| 2236 | 8.3, 9 | querier election; report suppression | 09 | — |
| 3376 | 4.2 | IGMPv3 INCLUDE/EXCLUDE source filtering, hence SSM | 09 | — |
| 7761 | 3.1–3.4 | PIM-SM: (*,G) Join toward the RP, Register/Register-Stop, (S,G) switchover, RPT-bit prune | 09 | — |
| 7761 | 4.5 | the RPF check against the unicast table | 09 | `linkstate.routing_table` |
| 2464 | 7 | IPv6 group → `33:33` + low 32 bits | 04, 09 | `subnet.multicast_mac` |
| 4760 | 3 | MBGP as the inter-domain RPF carrier | 09 | — |

## Note 10 — protocol design and sockets

No RFC defines "how to design a protocol". The note's checklist is drawn from
worked examples in the vendored set — 854/1143 for in-band signalling and option
negotiation, 1035 for a compact binary request/response with a transaction ID,
9293 for stream framing, 8305 for connection racing, 3168/9293's reserved bits
for extensibility, 6891 for how a protocol adds a field twenty years late —
together with [S25]. Each row of the checklist names the protocol it is drawn
from.
