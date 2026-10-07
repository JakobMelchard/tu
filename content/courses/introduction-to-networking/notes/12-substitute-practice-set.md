# 12 Substitute practice set

*Licence: CC BY-NC-SA 4.0, adapted from MIT OpenCourseWare 6.02 (Fall 2012, <https://ocw.mit.edu/terms/>); not CC BY-SA, see [LICENSE.md](https://github.com/JakobMelchard/tu/blob/main/LICENSE.md).*

> **Sourcing, and the rule this note exists to obey.** 191.030 is new in 2026W.
> There is no past paper, no exercise sheet, no script and no public slide deck
> [S1], [S2], [S5], [S7], [S33] — read
> [`00-exam-focus.md`](00-exam-focus.md) before this note, because it says what
> is known about the examination and what is guessed.
>
> **Nothing below was set at TU Wien.** Every problem carries its origin in
> brackets: **[MIT]** = adapted from MIT 6.02, Fall 2012, CC BY-NC-SA 4.0
> [S34]; **[CNP3]** = adapted from *Computer Networking: Principles, Protocols
> and Practice*, Bonaventure, UCLouvain, CC BY-SA 3.0 [S35]; **[ours]** = written
> here, and checkable against a vendored RFC. No problem text from either source
> is reproduced; the situations are restated and the answers are ours except
> where an answer is marked as MIT's published one.

Twenty-two problems, two hours' work, arranged in the order of the TISS subject
list [S1]. The worked code is in
`../src/exercises/`; each directory's `README.md` argues
the overlap and, just as importantly, the scope differences.

## Coverage against the TISS subject list

| TISS topic [S1] | free practice material found | problems |
|---|---|---|
| Terms, layering, encapsulation | **[MIT]** tutorial 8 | 1 |
| **Multi-stakeholder Internet governance** | **none** — see "gaps" below | 2, 3 *(ours)* |
| Layer 2: Ethernet, ARP | **[CNP3]** `network.rst`, `lan.rst` (partly — it is mostly STP, which is not on the list) | 4, 5 |
| Layer 3: IPv4 | **[CNP3]** `network.rst` addressing | 6, 7 |
| Layer 3: IPv6 | **[CNP3]** `ipv6.rst` (not used — `subnet.py` already covers it) | 8 *(ours)* |
| Layer 4: TCP/UDP | **[MIT]** tutorial 11, **with solutions** | 9, 10, 11 |
| Routing and forwarding | **[MIT]** tutorial 10, **with solutions** | 12, 13 |
| Link-state algorithms | **[MIT]** tutorial 10 | 14 |
| **Path-vector algorithms** | **[CNP3]** `routing-policies.rst` — the only free set found that examines this | 15, 16 |
| DNS | **[CNP3]** `dns.rst` (not used — `dns.py` already covers it) | 17 *(ours)* |
| **DNSSEC** | **none** | 18 *(ours)* |
| **Telnet** | **none** | 19 *(ours)* |
| **Unicast and multicast routing** | **none** | 20 *(ours)* |
| Protocol development | — (CNP3 has design prose, no exercises) | 21 *(ours)* |
| Socket programming | **[CNP3]** `sockets.rst` (not used — `sockets_echo.py` already covers it) | 22 *(ours)* |

## Where there is no good free practice material, and why

Four of the fifteen TISS topics have **no free exercise set anywhere that this
pass could find**, and padding the note with near-misses would be worse than
saying so:

- **Internet governance.** It is listed *first* in the TISS subject list [S1]
  and is a fingerprint of this lecturer — his comparable course at Saarland
  devoted its final lecture and an invited speaker to "Internet Governance and
  Organization" [S33]. It is also the topic no problem set examines, because it
  is not computable. Problems 2 and 3 are ours and are deliberately
  short-answer.
- **DNSSEC**, named separately from DNS by TISS [S1]. CNP3's `dns.rst` stops at
  resolution; MIT 6.033 mentions it in a lecture, not an exercise. Problem 18 is
  ours and is checked against RFC 4034 §5.4's published test vector [S10] — the
  one worked example this whole course has.
- **Telnet.** Nobody sets Telnet exercises in 2026. Problem 19 is ours, from
  RFC 854/855 and the RFC 1143 Q method [S16].
- **Multicast routing.** IGMP/PIM appear in no free introductory exercise set
  found. Problem 20 is ours, from RFC 1112 §6.4 and RFC 2236 [S17].

Two further gaps are *ours by choice*, not for lack of material: IPv6, DNS and
sockets all have CNP3 exercises, but this tree already has better
implementations of exactly those things (`subnet.py`, `dns.py`,
`sockets_echo.py`), so problems 8, 17 and 22 are written against our own code
rather than importing someone else's question.

---

## 1. Store-and-forward delay **[MIT, tutorial 8 problem 2 — adapted]**

A 5000-bit packet crosses two 1 Gbit/s links joined by one switch. Each link
has 10 µs propagation delay. The switch forwards only after the last bit has
arrived, and the queues are empty. What is the delay from first bit sent to
last bit received? Repeat for four links and three switches.

> **Answer** (MIT's published one). Each link costs one transmission delay
> (5000 bit / 10⁹ bit·s⁻¹ = 5 µs) plus one propagation delay (10 µs).
> Two links → **30 µs**; four links → **60 µs**. The store-and-forward rule is
> what makes it linear in the number of *links*, not a single 15 µs pipeline.
> `mit602_routing.store_and_forward_latency`.

## 2. Who runs what **[ours]**

Name the body responsible for each, and say in one clause what each does *not*
control: (a) allocating a /22 of IPv4 to an Austrian ISP; (b) publishing TCP's
specification; (c) deciding that `.wien` may exist; (d) the EtherType value
0x86DD.

> **Answer.** (a) **RIPE NCC**, one of the five RIRs, under numbers policy
> developed by its own community — it does not decide what you route.
> (b) The **IETF**, through the RFC process and BCP 78/79; it has no authority
> over deployment. (c) **ICANN**, names policy — it does not allocate numbers
> and does not write protocols. (d) **IEEE**, not IANA — EtherType is an IEEE
> registry, and note 01's demultiplexing table marks which registry owns which
> number [S31]. Note 01.

## 3. What "multi-stakeholder" excludes **[ours]**

A government proposes that IP address allocation be moved to a treaty
organisation in which only states vote. Give two concrete consequences for the
mechanisms in notes 06 and 08, and state what the multi-stakeholder model
claims instead.

> **Answer.** Consequences: allocation would stop tracking routing (RIR policy
> today is written by the operators who carry the routes, which is what keeps
> `whois`/RPKI data usable for filtering); and the IETF's separation of
> *specification* from *allocation* would collapse, so a protocol change could
> be blocked by a body that does not implement it. The multi-stakeholder claim
> is that operators, vendors, civil society, academia and governments all
> participate **without a vote being the mechanism** — rough consensus and
> running code, with numbers delegated hierarchically IANA → RIR → LIR. Note 01.
> *This is a topic the lecturer teaches as a lecture in its own right [S33];
> expect it to be asked in words, not numbers.*

## 4. Switch tables are a side effect of traffic **[CNP3, `network.rst` open questions 2–3 — adapted]**

Three switches in a line, S1–S2–S3; host A hangs off S1, hosts B and C off S3.
All tables start empty. C sends to B, then A sends to C, then B sends to A. For
each frame, say which ports it goes out of and what each switch has learned.

> **Answer.** C→B **floods**: S3 learns C on its C port and sends the frame out
> both its B port and its S2 port; S2 and S1 learn C too and flood onward, so A
> also receives it. B is reached — by flooding, not by forwarding.
> A→C is **not flooded**: every switch already knows C, so the frame is
> unicast S1→S2→S3→C, and each switch learns A on the way. B→A likewise.
> Note the asymmetry: a switch learns a host only when that host *transmits*,
> so an idle host is always reached by flooding.
> `cnp3_exercises.LearningSwitchNetwork`.

## 5. One forged ARP request **[ours, RFC 826]**

Host X broadcasts a single ARP **request** "who has 192.0.2.1, tell
192.0.2.1 at aa:bb:cc:dd:ee:ff", where 192.0.2.1 is the router. No reply is
ever sent. Which hosts on the segment now send the router's traffic to X, and
which sentence of RFC 826 makes that specified behaviour rather than a stack
bug?

> **Answer.** **Every host that already had an entry for 192.0.2.1.** RFC 826's
> packet-reception algorithm merges the *sender's* protocol/hardware pair into
> the cache if an entry exists — before the opcode is examined, and regardless
> of whether the host is the target. Only the target *adds* a new entry. So a
> broadcast request repoints the whole link's cache; hosts with no prior entry
> are unaffected. Notes 02, and `headers.py`'s ARP builder for the frame.

## 6. Aggregation and the hole in it **[CNP3, `network.rst` open question 1 — adapted]**

A site holds 203.0.113.0/26, 203.0.113.64/26, 203.0.113.128/26 and
203.0.113.192/26. (a) How many entries does its provider need? (b) The site
returns the second /26 to the RIR. Now how many, and why is that the shape of
the global routing table?

> **Answer.** (a) **One**: the four collapse to 203.0.113.0/24. (b) **Two**:
> 203.0.113.0/26 and 203.0.113.128/25 — the hole prevents the /24 from forming.
> With flat addresses you would need 256 entries. This is deaggregation in
> miniature, and it is why the global table holds ≈1.08 million prefixes for
> ≈79 400 ASes [S21]. `cnp3_exercises.aggregate`, `subnet.summarize_prefixes`.

## 7. TTL decrement without recomputing the checksum **[ours, RFC 1624]**

A router decrements TTL. Give the incremental-checksum equation it should use,
and say what RFC 1141's earlier equation got wrong.

> **Answer.** RFC 1624 equation 3: `HC' = ~(~HC + ~m + m')`. RFC 1141's
> equation 2 can produce **0xFFFF**, which is not a legal checksum (0xFFFF and
> 0x0000 are the same value in one's complement, and 0xFFFF is reserved to mean
> "no checksum" in UDP). RFC 1624 §4 prints the worked case:
> m = 0x5555 → m' = 0x3285 with the rest summing to 0xCD7A gives HC = 0xDD2F and
> HC' = **0x0000**, where equation 2 gives 0xFFFF.
> `inet_checksum.incremental_checksum_update`, `test_rfc_vectors.py` [S11].

## 8. Write it the way RFC 5952 requires **[ours]**

Compress `2001:0db8:0000:0000:0001:0000:0000:0001` and
`2001:0db8:0000:0000:0000:ff00:0042:8329`, then give the solicited-node
multicast address of the second.

> **Answer.** First: **`2001:db8::1:0:0:1`** — two runs of equal length, so the
> **leftmost** wins (RFC 5952 §4.2.3), lower case, no leading zeros.
> Second: **`2001:db8::ff00:42:8329`**. Solicited-node = `ff02::1:ff` +
> the low 24 bits of the address = **`ff02::1:ff42:8329`**, and the Ethernet
> destination for it is `33:33:ff:42:83:29` (RFC 2464 §7). Note 04 [S15], [S17];
> `subnet.ipv6_compress`, `subnet.solicited_node`, `subnet.multicast_mac`.

## 9. The chain, the window and the pipe **[MIT, tutorial 11 problem 1 — adapted]**

A–B–C–D–E, each link transmitting one packet per second, no queues. (a) RTT
A↔E? (b) stop-and-wait throughput? (c) optimal window and its throughput?
(d) with a window of four, throughput at E and utilisation of link B–C?

> **Answer** (MIT's published one). (a) **8 s** — four links out, four back.
> (b) **1/8 packet/s**. (c) window **8**, throughput **1 packet/s** — the
> bottleneck rate, which no window can beat. (d) **0.5 packet/s** and
> utilisation **0.5**. The window is the bandwidth-delay product; below it you
> pay the RTT, above it you only build queues.
> `mit602_transport.optimal_window`, `window_throughput`.

## 10. When a sequence number is too small **[MIT, tutorial 11 problem 2 — adapted]**

A protocol uses 8-bit sequence numbers, 1000-byte packets and a 100 ms RTT.
(a) Stop-and-wait throughput? (b) Window needed to fill a 1 Mbyte/s link?
(c) At what link speed does the protocol silently break, and how?

> **Answer** (MIT's published one). (a) 1000 B / 0.1 s = **10 kbyte/s**.
> (b) bandwidth-delay product = 1 Mbyte/s × 0.1 s = **100 kbyte**.
> (c) **2.55 Mbyte/s**: at (2⁸−1)×1000 bytes in flight the sequence space wraps
> within one RTT, two live packets share a number, and an ACK for the first
> silently acknowledges the second — data loss inside a "reliable" protocol.
> This is exactly what RFC 7323's PAWS exists to prevent in TCP [S14].
> `mit602_transport.seq_wraparound_capacity`.

## 11. Loss composition and the cost of stop-and-wait **[MIT, tutorial 11 problems 3–4 — adapted]**

(a) A path has k independent links with forward loss p₁…p_k. Give the
end-to-end loss p, and its approximation when all p_i = α ≪ 1. (b) With
forward loss p and reverse loss q, what is the expected number of
transmissions before stop-and-wait advances? (c) 40 kbit/s earth–moon link,
1.5 light-seconds each way, 1000-byte packets: stop-and-wait rate and
utilisation?

> **Answer** (MIT's published one). (a) p = 1 − ∏(1 − p_i) ≈ **kα**.
> (b) **1/((1−p)(1−q))** — the packet *and* its ACK must both survive.
> (c) one packet per 3 s RTT = **333 byte/s = 2.6 kbit/s**, utilisation
> **6.5 %** as MIT prints it (the exact figure is 1/15 = 6.67 %; MIT's follows
> from rounding 2.6). Counting the 0.2 s transmission time gives 312 byte/s.
> `mit602_transport.path_loss`, `expected_transmissions`.

## 12. Distance vector on a clock **[MIT, tutorial 10 problem 1 — adapted]**

Advertisements every 5 time steps, HELLO every step, zero propagation and
processing delay. Network I is the path A–B–C; network II is the triangle
D–E–F. (a) When does A first have an entry for B? for C? (b) The link B–C fails
at t = 51 and D–E at t = 71. When does B advertise C as unreachable, when does
A believe it, and when does D have a new route to E?

> **Answer** (MIT's published one). (a) **5** and **10** — one advertisement
> per hop. (b) **55**, **55** and **75**. Each is the first advertisement after
> the failure; with zero delay a change crosses one hop per round, so B's
> advertisement and A's table update land in the same round.
> *Modelling note*: this comes out only with **split horizon**. Without it, A's
> stale "C at cost 2" goes back to B and the pair counts to infinity — which is
> exactly the failure mode that motivates link state and path vector (note 07).
> `mit602_routing.dv_first_entry_times`, `dv_failure_times`;
> `distvector.count_to_infinity_demo` for the version without split horizon.

## 13. Longest prefix match, by hand **[ours]**

A router holds `0.0.0.0/0 via R1`, `203.0.113.0/24 via R2`,
`203.0.113.128/26 via R3`, `203.0.113.129/32 via R4`. Where do
203.0.113.129, 203.0.113.190, 203.0.113.200 and 198.51.100.7 go?

> **Answer.** **R4** (the /32 is longest), **R3** (inside 128–191), **R2** (in
> the /24 but past the /26, which ends at .191), **R1** (default). The rule is
> *longest prefix*, not first match and not most specific *route source* —
> administrative distance only breaks ties between protocols offering the
> **same** prefix, and is a vendor convention with no RFC. Note 06;
> `subnet.ForwardingTable`.

## 14. Two algorithms in one network **[MIT, tutorial 10 problems 2 and 4 — adapted]**

Four ways to choose a path: minimum total cost; minimum hop count; **second**
lowest total cost; minimum sum of *squared* link costs. Which can produce a
forwarding loop, and why?

> **Answer** (MIT's published one). Only **SecondMinCost** loops. MIT's
> counter-example is an equal-cost triangle A, B, D: A's runner-up path to D is
> A–B–D so A points at B, B's is B–A–D so B points at A. The other three are
> safe because each is a *consistent* minimisation over an additive, positive
> metric — MinCostSquared is just MinCost on squared weights — so every node's
> chosen path is a suffix of its neighbour's, which is the optimal-substructure
> property Dijkstra and Bellman–Ford both rely on. The same argument shows why
> mixing Alice's min-cost with Bob's min-hop in one network loops: two
> different metrics have no common substructure.
> `mit602_routing.has_loop`, `strategy_is_loop_free`; `linkstate.dijkstra`.

## 15. Valley-free paths **[CNP3, `routing-policies.rst` exercise 1 — adapted]**

Four ASes: AS1 is a customer of both AS2 and AS3; AS4 is a customer of AS2;
AS2–AS3 and AS3–AS4 are peering links. Which path does each of the following
use, and of which class: AS1 → AS4, AS4 → AS2, AS4 → AS1?

> **Answer** (ours — CNP3 publishes none). **AS1 → AS4**: two equally good
> **provider** paths, AS1–AS2–AS4 and AS1–AS3–AS4. AS2 exports its customer AS4
> to its customer AS1; AS3 learned AS4 from a peer and exports peer routes to
> its customers, so AS1 hears it too.
> **AS4 → AS2**: only the direct **provider** path AS4–AS2. AS3 will not
> re-advertise its peer AS2's routes to its peer AS4.
> **AS4 → AS1**: **AS4–AS3–AS1**, a **peer** path, beating the equally long
> provider path AS4–AS2–AS1.
> `cnp3_exercises.valley_free_routes`; `pathvector.GaoRexford` [S27].

## 16. Why length never got examined **[CNP3, follow-on — ours]**

In problem 15, AS4's two candidate paths to AS1 have the same AS_PATH length.
Explain, by RFC 4271 section number, why the tie-break that compares lengths is
never reached — and name the attribute that actually decides.

> **Answer.** RFC 4271 has **two phases**. §9.1.1 computes the *degree of
> preference* for each route; §9.1.2.2's seven tie-breaks — of which AS_PATH
> length is (a) — are applied **only among routes of equal degree**. Operators
> set the degree from the neighbour's business relationship, which is
> `LOCAL_PREF` in practice. The peer route carries a higher LOCAL_PREF than the
> provider route, so phase 1 settles it and §9.1.2.2 is never entered.
> Two corollaries worth stating: "shortest AS path wins" is false in general,
> and "oldest route" is a **vendor** tie-break that is not in RFC 4271 at all.
> Note 07's correction table; `bgp_decision.degree_of_preference`, `TIE_BREAKS` [S9].

## 17. A resolution, step by step **[ours]**

A stub resolver with a cold cache asks a recursive resolver for
`www.example.org A`. List the queries the recursive resolver sends, and say
which responses are **referrals** and which are **answers**. Then: the reply is
900 bytes with DNSSEC data. What happens without EDNS(0), and with it?

> **Answer.** Root server → referral to `.org` NS (no answer section, NS +
> glue in authority/additional); `.org` server → referral to
> `example.org` NS; `example.org` server → **answer**, AA bit set. Three
> queries, two referrals, one answer; the stub gets one recursive answer with
> RA set.
> Without EDNS(0) the 512-byte UDP limit of RFC 1035 truncates the reply: TC=1,
> and the resolver retries over TCP. With EDNS(0) the OPT pseudo-RR advertises a
> larger requestor payload size (and carries the DO bit), so it fits in UDP —
> at the cost of being an amplification vector, which is why RFC 8482 exists.
> Note 08 [S16]; `dns.build_query`, `dns.parse_message`.

## 18. Verify a DS record **[ours, RFC 4034 §5.4 — the course's one published vector]**

Given the DNSKEY for `dskey.example.com.`, compute its key tag and the SHA-1 DS
digest. State the digest's input precisely, and say why the key tag is not a
checksum you can trust for identity.

> **Answer.** Key tag **60485**; SHA-1 digest
> **`2BB183AF5F22588179A53B0A98631FAD1A292118`**. The digest input is the
> **canonical owner name** (uncompressed, lower case, wire format) concatenated
> with the DNSKEY **RDATA** — RFC 4034 §5.1.4. The key tag is a 16-bit sum over
> the RDATA (Appendix B) and is *not* the Internet checksum and *not* unique:
> two keys can collide, so a validator must try every DNSKEY whose tag matches.
> The DS lives in the **parent** zone and is signed by the parent — that is the
> link in the chain of trust, and a chain that breaks yields **SERVFAIL**, not
> an insecure answer. Note 08; `dnssec.key_tag`, `dnssec.ds_record`,
> `test_rfc_vectors.py` [S10].

## 19. Negotiate an option without looping **[ours, RFC 854/855/1143]**

A Telnet client wants to refuse every option. It receives `IAC DO ECHO`.
What does it send? Then it receives `IAC DO ECHO` again. What now — and what
does the Q method add that a naive implementation lacks?

> **Answer.** `IAC WONT ECHO` (255 252 1). The repeat gets **`IAC WONT ECHO`
> again**: the option is NO and `DO` proposes NO → YES, a change, and RFC 1143
> §2 requires an answer to every negotiation that proposes to change the
> status quo; §7's table row (receipt of DO, us = NO,
> not agreeing) says send WONT. No loop follows, because the server, holding
> WANTYES for its own request, goes to NO on the WONT and sends nothing, and
> nobody answers a WONT/DONT for an option that is already off.
> What the Q method adds: (1) a refusal is never *confirmed*. The naive
> implementation answers WONT with DONT and DONT with WONT, and two of them
> ping-pong forever; (2) the negotiating states WANTYES/WANTNO are kept apart
> from YES/NO, so the reply to our own request is not mistaken for a new
> request; (3) a queue bit defers a change of mind until the current
> negotiation finishes. Four states per option per direction plus the queue bit.
> Also: data byte 255 must be sent as `IAC IAC`, or the peer reads it as the
> start of a command. Notes 08, 10; `telnet_client_sketch.QOption`,
> `test_telnet_client_sketch.py::test_note12_problem19_repeated_do_is_refused_each_time_and_nothing_loops` [S16].

## 20. One MAC address, thirty-two groups **[ours, RFC 1112 §6.4]**

Give the Ethernet destination for IPv4 group 224.0.0.5 and for 239.128.0.5.
Why are they the same, how many groups share one MAC, and what does the host
have to do about it? Then give the IPv6 equivalent for `ff02::1:ff42:8329`.

> **Answer.** Both map to **`01:00:5e:00:00:05`**: the mapping is the fixed
> 25-bit prefix `01:00:5e` with the top bit of the next octet zero, plus the
> **low 23 bits** of the group address. A group address has 28 significant bits
> (224/4 leaves 28), so 28 − 23 = 5 bits are lost and **2⁵ = 32** groups share
> each MAC. The NIC therefore passes frames the host did not join, and the IP
> layer must filter by destination group — a real cost, not a curiosity.
> IPv6 is cleaner: `33:33` plus the **low 32 bits**, so
> **`33:33:ff:42:83:29`** (RFC 2464 §7), with far fewer collisions.
> Note 09 [S17]; `subnet.multicast_mac`.

## 21. Design a protocol, and defend it **[ours]**

Design an application protocol by which a hundred sensors report a 12-byte
reading every 10 s to one collector on a lossy wireless link, where a lost
reading is acceptable but a *wrong* one is not, and readings must stay
attributable after a collector restart. Make six decisions and give a reason
for each.

> **Answer template** (note 10's checklist — the shape is the mark, not the
> choice). **Transport**: UDP — 12-byte payloads, loss tolerable, and 100 idle
> TCP connections cost more state than the data; accept that you must then do
> your own everything. **Framing**: one reading per datagram, so no framing
> problem exists — UDP preserves message boundaries, which is the one thing it
> gives you for free. **Identification**: a sensor ID plus a monotonically
> increasing counter, so the collector can detect gaps and survive its own
> restart; do not use the source IP, which NAT and DHCP will change.
> **Error handling**: a CRC or MAC over the payload, because "wrong is
> unacceptable" and the UDP checksum is a 16-bit one's-complement sum that
> misses common bit patterns; no retransmission, because loss is acceptable.
> **Versioning**: a version byte in the first octet, and a rule for what a
> receiver does with an unknown version — *reject*, not ignore, per RFC 9413's
> re-assessment of the robustness principle [S17]. **Security**: at minimum a
> per-sensor key over the reading; without it any host on the link can forge
> readings, and BCP 38 [S17] is not your ingress filter to configure.
> Note 10; `sockets_echo.py` for the length-prefixed TCP contrast.

## 22. Why the length prefix **[ours]**

A TCP echo server does `data = sock.recv(1024)` and echoes it back. Give two
distinct ways this is wrong, and the smallest fix.

> **Answer.** (1) **TCP is a byte stream**: `recv` may return fewer bytes than
> were sent, or bytes from two sends at once. There are no message boundaries
> to recover unless the protocol puts them there. (2) `recv` returning `b""`
> means the peer closed — treating it as data loops forever on a closed socket.
> Fix: a **length prefix** (a 16- or 32-bit big-endian count) plus a
> `recv_exact` loop that calls `recv` until it has exactly that many bytes and
> raises on EOF. The alternative is a delimiter, which then needs escaping —
> which is precisely what Telnet's `IAC IAC` is (problem 19).
> Note 10; `sockets_echo.recv_exact`.

---

## How to use this

- These are **not** predictions of 191.030's paper. They match the *verbs* of
  the TISS learning outcomes — explain, describe, solve, assess, design [S1] —
  and nothing more. [`00-exam-focus.md`](00-exam-focus.md) explains why no
  stronger claim is available.
- Problems 1, 9–12 and 14 have answers **MIT published**; if yours differs,
  yours is wrong. Every other answer is ours, and where an RFC settles it the
  RFC is named and vendored in `../refs/rfc/`.
- Trace reading, topology derivation and TCP scenarios were the three problem
  types the TISS practical-part text named (stated on TISS until 2026-09-2x,
  removed by 2026-09-27 [S1]; last recorded here on 2026-09-22). TISS still
  schedules five exercises after lectures 7, 9, 16, 19, 22 in its examination
  modalities, but no longer says what they contain. The *procedures* for those
  three types are in [`11-exercise-playbook.md`](11-exercise-playbook.md). Use
  `tcp_sim.py`, `tcp_fsm.py`, `pcap.py` and `subnet.py` to generate instances
  of your own; this note gives the worked ones.
- **When the first lecture happens and the real sheets appear**, this note
  becomes a warm-up and not a substitute. Where they will appear is open: TISS
  links no TUWEL course for 191.030 (re-read 2026-09-27). Do not copy the sheets here; see
  [`../src/exercises/README.md`](../src/exercises/README.md).
