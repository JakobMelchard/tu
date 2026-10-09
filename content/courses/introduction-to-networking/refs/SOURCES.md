# Sources — 191.030 Introduction to Networking

Register of every source used to write and verify `../notes` and
`../src`. Notes cite these as `[S<n>]`. Retrieval dates are the day
the page or file was fetched; TISS and live measurement pages change, so
re-check before an exam.

**Vendoring policy.** Unlike most courses here, the primary sources of this one
*are* freely redistributable, so they are vendored: 52 RFCs in
`rfc/`, 4.1 MB of plain text, with a `SHA256SUMS` manifest. See
[`README.md`](README.md) for the licence reasoning per RFC vintage. Everything
else below is a live web page (cited) or a paper whose licence could not be
established (cited, fetch command in [`fetch-sources.sh`](fetch-sources.sh)).
No TUWEL material was fetched; TUWEL needs a login and is not ours to copy, and
as of 2026-09-27 TISS links no TUWEL course for 191.030 at all.
The **substitute practice sources** S33–S35 are free and two of them are
licence-clear, but they are cited rather than vendored as well — the reasoning
is in that section and in the `README.md` of each
`../src/exercises/` directory.

**The one thing to internalise before reading further.** 191.030 is **new in
2026W**, taught by a professor who **started at TU Wien on 1 March 2026** and
teaches no other lecture here [S1, S4, S5]. There is no previous offering, no
VoWi page, no past paper, no public slide deck, no script. Every statement in
these notes about *what will be examined* is therefore an inference from the
TISS page and from what the lecturer works on — and is marked as such in
[`../notes/00-exam-focus.md`](../notes/00-exam-focus.md). Every statement about
*how a protocol works* is, by contrast, traceable to a vendored RFC.

## Course-authoritative

### S1 — TISS course page, 2026W ★

- Title: 191.030 Introduction to Networking (Einführung in Computernetzwerke), 2026W
- URL: <https://tiss.tuwien.ac.at/course/courseDetails.xhtml?courseNr=191030&semester=2026W&locale=en>
- Retrieved: 2026-09-22 (browser; the page needs JavaScript for the DeltaSpike window id)
- Access: public, no login
- Used for: the entire scope (learning outcomes, three-part subject list),
  lecturer (Fiebig), 6.0 ECTS / VU 4.0 h, the grading scheme (100 + 100 + 5×20,
  150 to pass), exam dates, registration windows, the ECTS breakdown, the
  practical-part description that note 11 is built around, "No lecture notes are
  available", and the twelve **single appointments** (see the table in
  [`../docs/tiss.md`](../docs/tiss.md)) that were not previously recorded.
  Diffed against `../docs/tiss.md` — no change in any field; the single
  appointments are new information.
- **Re-read 2026-09-27** (logged-in browser; `../docs/tiss.md` header records
  it). Deregistration until 02.10.2026 12:00. Dates, exams and registration windows unchanged: twelve
  Monday lectures 12:00-14:00 in EI 11, mid-term Mon 30.11.2026 12:00-14:00 in
  the lecture room (registration 12.10-23.11.2026 12:00), final Mon 25.01.2027
  12:00-14:00 (registration 12.10.2026-18.01.2027 12:00), 5 × 20 + 100 + 100
  points, pass at 150. **Changed**: the API's "Subject of course" lost its last
  sentences, i.e. the practical-part examples "describing packet traces
  received", "deriving a topology", "describe TCP behavior given a specific
  scenario" and the sentence scheduling the five exercises after the lectures
  "according to the overview in the examination description". The
  five-exercise schedule itself still stands in the examination modalities.
  Every quotation of those sentences in the notes is now marked "stated on TISS
  until 2026-09-2x, removed by 2026-09-27". No TUWEL link on the page.

### S2 — TISS, 191.030 in 2025W and 2024W: **does not exist**

- URLs tried: `…courseDetails.xhtml?courseNr=191030&semester=2025W…` and `…&semester=2024W…`
- Retrieved: 2026-09-22
- Result: TISS silently serves the 2026W page (its canonical link is
  `semester=2026W`). The TISS course search over 2026W/2027S for
  "Computernetzwerke" and for "Fiebig" each return exactly one row, 191.030 in
  2026W.
- Used for: establishing that **no previous offering exists**. This is the
  single most consequential finding of the pass and the reason
  `00-exam-focus.md` reads the way it does.

### S3 — TISS course search

- URL: <https://tiss.tuwien.ac.at/course/courseList.xhtml>
- Retrieved: 2026-09-22. Access: public.
- Used for: S2, and for finding S6 (the neighbouring E191 networking course).

### S4 — Tobias Fiebig, TU Wien Informatics people page

- URL: <https://informatics.tuwien.ac.at/people/tobias-fiebig>
- Retrieved: 2026-09-22. Access: public.
- Used for: lecturer identity — Full Professor and Head of the **Internet
  Infrastructures** research unit (E191-06), Institute of Computer Engineering;
  TISS person id 442654. His 2026W teaching is 191.030 plus the generic
  project/thesis/practical course numbers (191.005–191.009, 191.033), i.e. this
  is his only lecture.

### S5 — TU Wien, "Univ.Prof. Dr.-Ing. Tobias Fiebig" (new-professors page)

- URL: <https://www.tuwien.at/en/tu-wien/organisation/central-divisions/professorships-at-tu-wien/new-professors-since-2019/new-professors-by-alphabetical-order/f/univprof-dr-ing-tobias-fiebig>
- Retrieved: 2026-09-22. Access: public.
- Used for: appointment as Professor of Computer Networks **effective 1 March
  2026**; career (Osnabrück cognitive science → UvA System and Network
  Engineering MSc → TU Berlin PhD 2017, *An Empirical Evaluation of
  Misconfiguration in Internet Services* → TU Delft assistant professor
  2017–2022 → MPI-INF). Cross-checked against his MPI-INF profile
  (<https://www.mpi-inf.mpg.de/departments/inet/people/tobias-fiebig>, retrieved
  2026-09-22), which adds the research topics that inform `00-exam-focus.md`:
  network measurement, misconfiguration, **DNS**, **BGP**, **SMTP/mail
  security (SPF, DMARC, MTA-STS)**, **IPv6 readiness**, and human factors in
  system administration. No lecture material of his own is public; searches for
  slides or notes returned nothing.

### S6 — TISS + VoWi: 182.752 Computer Networks VU (Schmid/Siegl) — the neighbouring E191 course

- URLs: <https://tiss.tuwien.ac.at/course/courseDetails.xhtml?courseNr=182752&semester=2024W&locale=en>
  and <https://vowi.fsinf.at/wiki/TU_Wien:Computer_Networks_VU_(Schmid)>
- Retrieved: 2026-09-22. Access: public.
- Used for: the only comparable TU Wien networking course at the same institute.
  2.0 h / 3.0 ECTS, German, **mandatory in the 3rd semester of 033 535 Computer
  Engineering**, seminar format (groups of three present a sub-topic and write a
  15-page paper), graded from presentation + paper + an **oral** exam over a
  question catalogue the students themselves assemble.
  **It is not a model for 191.030's exam** — different lecturer, different
  format, different ECTS — but its student-reported topic list (switches,
  spanning tree, MAC-table flooding, VLAN, 802.1X, IPv4/v6, ARP and ARP
  spoofing, DNS, routing, masquerading, DHCP, TCP/UDP, firewalls, TLS, WLAN,
  LoRa, Bluetooth) is evidence of what a TU Wien Computer Engineering student is
  already expected to have seen, and 191.030 is a *mandatory elective* for the
  same curriculum. VoWi material is student-uploaded and **not vendored**.

### S7 — VoWi: no page for this course

- Searched: <https://vowi.fsinf.at> for "Introduction to Networking",
  "Computernetzwerke", "Fiebig" (2026-09-22; the site is behind an Anubis
  proof-of-work gate, so it was read in a browser).
- Result: **no page exists** for 191.030 and no page names Fiebig. The only
  similarly named LVAs are S6 and its siblings (Computer Networks VU (Siegl),
  Computer Networks VL (Demuth), both for 182.752 / its predecessor).
- Used for: confirming S2 from the student side, and recorded here so the next
  person does not repeat the search.

## Standards — vendored in `rfc/`

All 52 are plain text from `https://www.rfc-editor.org/rfc/rfcNNNN.txt`,
retrieved **2026-09-22**, checksummed in [`rfc/SHA256SUMS`](rfc/SHA256SUMS).
Licence reasoning in [`README.md`](README.md). Section-by-section mapping to our
notes and code in [`standards-map.md`](standards-map.md).

### S8 — RFC 2328, *OSPF Version 2* (Moy, 1998, STD 54) ★

- <https://www.rfc-editor.org/rfc/rfc2328.txt> · [`rfc/rfc2328.txt`](rfc/rfc2328.txt)
- Used for: **the OSPF timers that note 07 previously stated without a source.**
  Appendix B fixes the architectural constants (LSRefreshTime 30 min,
  MinLSInterval 5 s, MinLSArrival 1 s, MaxAge 1 h, CheckAge 5 min, MaxAgeDiff
  15 min, LSInfinity 0xffffff, InitialSequenceNumber 0x80000001). Appendix C.3
  gives the *configurable* ones as **samples, not defaults**: HelloInterval
  "sample value for a local area network: 10 seconds", RxmtInterval 5 s,
  InfTransDelay 1 s, and RouterDeadInterval only "should be some multiple of the
  HelloInterval (say 4)". Also §A.1 (IP protocol 89, AllSPFRouters 224.0.0.5,
  AllDRouters 224.0.0.6), §10.5 (Hello parameters must match or no adjacency
  forms), §13.1 (which LSA instance is newer), §9.4 (DR/BDR election), §7.2/§16
  (areas, SPF calculation). Implemented in [`../src/py/ospf.py`](../src/py/ospf.py).

### S9 — RFC 4271, *A Border Gateway Protocol 4 (BGP-4)* (Rekhter, Li, Hares, 2006) ★

- <https://www.rfc-editor.org/rfc/rfc4271.txt> · [`rfc/rfc4271.txt`](rfc/rfc4271.txt)
- Used for: **the BGP timers that note 07 previously stated without a source.**
  §10 gives every suggested default: ConnectRetryTime 120 s, HoldTime 90 s
  (4 minutes for the "large value" used inside the FSM), KeepaliveTime = 1/3 of
  HoldTime = 30 s, MinASOriginationIntervalTimer 15 s,
  MinRouteAdvertisementIntervalTimer **30 s on eBGP and 5 s on iBGP**, and
  jitter = base × U(0.75, 1.0). Also §3 (TCP port 179), §4.3 (attributes,
  ORIGIN values), §9.1.1 (degree of preference — where LOCAL_PREF actually
  lives), §9.1.2.2 (the seven tie-breaks, in order), §9.1.3 (dissemination),
  §9.2.1.1 (MRAI). Implemented in
  [`../src/py/bgp_decision.py`](../src/py/bgp_decision.py).

### S10 — RFC 4034, *Resource Records for the DNS Security Extensions* (2005)

- <https://www.rfc-editor.org/rfc/rfc4034.txt> · [`rfc/rfc4034.txt`](rfc/rfc4034.txt)
- Used for: DNSKEY/RRSIG/DS/NSEC layouts, §5.1.4 (DS digest = H(owner | DNSKEY
  RDATA)), Appendix B (key tag), §6.2 (canonical form), and **the one published
  test vector in the whole course**: §5.4's `dskey.example.com.` DNSKEY with
  "key id = 60485" and SHA-1 DS digest `2BB183AF5F22588179A53B0A98631FAD1A292118`,
  reproduced by [`../src/py/dnssec.py`](../src/py/dnssec.py).

### S11 — RFC 1624, *Computation of the Internet Checksum via Incremental Update* (1994)

- <https://www.rfc-editor.org/rfc/rfc1624.txt> · [`rfc/rfc1624.txt`](rfc/rfc1624.txt)
- Used for: §4's worked example (m = 0x5555 → 0x3285 with the rest summing to
  0xCD7A gives HC = 0xDD2F and HC' = 0x0000), and the demonstration that RFC
  1141's equation 2 yields the impossible 0xFFFF. Reproduced in
  `test_rfc_vectors.py`; this is what note 03 exam question 2 asks for.

### S12 — RFC 1071, *Computing the Internet Checksum* (1988)

- [`rfc/rfc1071.txt`](rfc/rfc1071.txt): §3 works the one's-complement sum of
  `0001 f203 f4f5 f6f7` four ways and prints the sums (`2ddf0` → `ddf2`,
  swapped `f2dd`, 32-bit `1ddf1` → `ddf2`, odd split `f201` + swap(`f0eb`)).
  It prints no checksum; `0x220d` = ~`ddf2` is derived. All reproduced by
  `test_rfc_vectors.py`. (Corrected 2026-09-27: earlier entries called 0x220d
  "§3's worked sum".)

### S13 — the layer-2/3/4 core

| RFC | file | used for |
|---|---|---|
| 826 | [`rfc/rfc826.txt`](rfc/rfc826.txt) | ARP packet format and, crucially, the **packet-reception algorithm**: *every* host merges the sender's mapping if it already has an entry, and only the target adds a new one. Note 02 |
| 791 | [`rfc/rfc791.txt`](rfc/rfc791.txt) | IPv4 header fields, fragmentation (offset in 8-byte units), TTL, options. Note 03 |
| 792 | [`rfc/rfc792.txt`](rfc/rfc792.txt) | ICMP types and codes, the "IP header + 64 bits of payload" quote rule. Note 03 |
| 768 | [`rfc/rfc768.txt`](rfc/rfc768.txt) | UDP's eight bytes and the pseudo-header. Note 05 |
| 9293 | [`rfc/rfc9293.txt`](rfc/rfc9293.txt) | TCP (obsoletes 793): header, flags, state machine, **MSL = 2 minutes**, TIME-WAIT, RST rules, default MSS 536. Note 05 |
| 1122 | [`rfc/rfc1122.txt`](rfc/rfc1122.txt) | host requirements: delayed ACK **MUST be < 0.5 s**, ACK at least every second full-sized segment; the robustness principle restated. Notes 01, 05 |
| 8200 | [`rfc/rfc8200.txt`](rfc/rfc8200.txt) | IPv6 header (STD 86), extension-header chain, minimum link MTU 1280, routers never fragment. Note 04 |
| 4291 | [`rfc/rfc4291.txt`](rfc/rfc4291.txt) | IPv6 addressing architecture: 2000::/3, fe80::/10, ff00::/8, ::1, ::, **solicited-node ff02::1:ff00:0/104**, modified EUI-64. Note 04 |
| 4861 | [`rfc/rfc4861.txt`](rfc/rfc4861.txt) | NDP: RS/RA/NS/NA/Redirect types 133–137, **Hop Limit 255 check**, neighbour-cache states. Note 04 |
| 4862 | [`rfc/rfc4862.txt`](rfc/rfc4862.txt) | SLAAC and Duplicate Address Detection. Note 04 |

### S14 — transport behaviour

| RFC | file | used for |
|---|---|---|
| 5681 | [`rfc/rfc5681.txt`](rfc/rfc5681.txt) | slow start, congestion avoidance, fast retransmit/fast recovery, `ssthresh = max(FlightSize/2, 2*SMSS)`, loss window LW = 1 segment, and the RFC's own **IW of 2–4 segments**. Note 05 |
| 6928 | [`rfc/rfc6928.txt`](rfc/rfc6928.txt) | the *experimental* IW10 that today's stacks actually use. Note 05 |
| 6298 | [`rfc/rfc6298.txt`](rfc/rfc6298.txt) | RTO: α = 1/8, β = 1/4, K = 4, initial RTO 1 s, **rule 2.4 rounds any RTO below 1 s up to 1 s**, maximum ≥ 60 s, Karn. Note 05, `tcp_sim.py` |
| 7323 | [`rfc/rfc7323.txt`](rfc/rfc7323.txt) | window scale (shift ≤ 14), timestamps, PAWS. Note 05 |
| 3168 | [`rfc/rfc3168.txt`](rfc/rfc3168.txt) | ECN: the two IP bits and the CWR/ECE TCP flags. Notes 03, 05 |

### S15 — addressing and NAT

| RFC | file | used for |
|---|---|---|
| 1918 | [`rfc/rfc1918.txt`](rfc/rfc1918.txt) | 10/8, 172.16/12, 192.168/16. Note 03 |
| 3021 | [`rfc/rfc3021.txt`](rfc/rfc3021.txt) | /31 on point-to-point links: two usable addresses, no broadcast. Note 03 |
| 3022 | [`rfc/rfc3022.txt`](rfc/rfc3022.txt) | traditional NAT and NAPT, the checksum fix-up, the ALG problem. Note 03 |
| 1191 | [`rfc/rfc1191.txt`](rfc/rfc1191.txt) | Path MTU Discovery and the ICMP "fragmentation needed" MTU field. Note 03 |
| 5737 | [`rfc/rfc5737.txt`](rfc/rfc5737.txt) | 192.0.2/24, 198.51.100/24, 203.0.113/24 documentation blocks — the addresses these notes now use everywhere |
| 6598 | [`rfc/rfc6598.txt`](rfc/rfc6598.txt) | 100.64/10 Shared Address Space for CGNAT. Note 03 |
| 4193 | [`rfc/rfc4193.txt`](rfc/rfc4193.txt) | IPv6 unique local addresses fc00::/7. Note 04 |
| 6164 | [`rfc/rfc6164.txt`](rfc/rfc6164.txt) | /127 on inter-router IPv6 links. Note 04 |
| 5952 | [`rfc/rfc5952.txt`](rfc/rfc5952.txt) | IPv6 text representation: lower case, `::` for the **longest** run and the leftmost on a tie. Note 04 |
| 7217 / 8981 | [`rfc/rfc7217.txt`](rfc/rfc7217.txt), [`rfc/rfc8981.txt`](rfc/rfc8981.txt) | stable-but-opaque IIDs; temporary (privacy) addresses. Note 04 |
| 8106 | [`rfc/rfc8106.txt`](rfc/rfc8106.txt) | RDNSS/DNSSL options in Router Advertisements. Note 04 |
| 8305 | [`rfc/rfc8305.txt`](rfc/rfc8305.txt) | Happy Eyeballs v2. Notes 04, 10 |
| 6793 | [`rfc/rfc6793.txt`](rfc/rfc6793.txt) | **4-octet AS numbers** — the reason note 06 can say "16 bit, now 32 bit" |

### S16 — DNS and applications

| RFC | file | used for |
|---|---|---|
| 1034 / 1035 | [`rfc/rfc1034.txt`](rfc/rfc1034.txt), [`rfc/rfc1035.txt`](rfc/rfc1035.txt) | namespace, zones, delegation, resolver algorithm; message format, label ≤ 63 / name ≤ 255, **512-byte UDP limit**, compression pointers (top two bits 11). Note 08, `dns.py` |
| 6891 | [`rfc/rfc6891.txt`](rfc/rfc6891.txt) | EDNS(0): the OPT pseudo-RR, the requestor's UDP payload size, the DO bit. Note 08 |
| 4033 / 4035 | [`rfc/rfc4033.txt`](rfc/rfc4033.txt), [`rfc/rfc4035.txt`](rfc/rfc4035.txt) | DNSSEC introduction and protocol: AD and CD bits, SERVFAIL on validation failure, the secure/insecure/bogus/indeterminate states, authenticated denial. Note 08 |
| 8482 | [`rfc/rfc8482.txt`](rfc/rfc8482.txt) | minimal responses to ANY queries (amplification mitigation). Note 08 |
| 854 / 855 | [`rfc/rfc854.txt`](rfc/rfc854.txt), [`rfc/rfc855.txt`](rfc/rfc855.txt) | Telnet: the network virtual terminal, IAC = 255, WILL/WONT/DO/DONT 251–254, SB/SE 250/240, IAC IAC escaping. Notes 08, 10 |
| 1143 | [`rfc/rfc1143.txt`](rfc/rfc1143.txt) | the **Q method** option-negotiation state machine that prevents Telnet negotiation loops. Notes 08, 10; `telnet_client_sketch.py` |

### S17 — routing, multicast, principles

| RFC | file | used for |
|---|---|---|
| 1112 | [`rfc/rfc1112.txt`](rfc/rfc1112.txt) | host extensions for IP multicasting; **§6.4: the IPv4 group → 01:00:5E + low 23 bits Ethernet mapping**. Note 09 |
| 2236 | [`rfc/rfc2236.txt`](rfc/rfc2236.txt) | IGMPv2: **Query Interval 125 s**, Max Response Time, Leave/group-specific query, the querier election. Note 09 |
| 3376 | [`rfc/rfc3376.txt`](rfc/rfc3376.txt) | IGMPv3 source filtering (INCLUDE/EXCLUDE) — what makes SSM possible. Note 09 |
| 7761 | [`rfc/rfc7761.txt`](rfc/rfc7761.txt) | PIM-SM: Join/Prune toward the RP, Register/Register-Stop, the (S,G) shortest-path switchover, the RPT-bit prune. Note 09 |
| 2464 | [`rfc/rfc2464.txt`](rfc/rfc2464.txt) | IPv6 over Ethernet; **§7: multicast → 33:33 + low 32 bits**. Notes 04, 09 |
| 4760 | [`rfc/rfc4760.txt`](rfc/rfc4760.txt) | multiprotocol BGP (the AFI/SAFI that carry multicast RPF routes and IPv6). Notes 06, 09 |
| 2827 | [`rfc/rfc2827.txt`](rfc/rfc2827.txt) | BCP 38 ingress filtering against source-address spoofing. Notes 03, 08 |
| 761 | [`rfc/rfc761.txt`](rfc/rfc761.txt) | §2.10, the **original wording** of the robustness principle. Note 01 |
| 9413 | [`rfc/rfc9413.txt`](rfc/rfc9413.txt) | *Maintaining Robust Protocols* (2023): the IAB's re-assessment of that principle — tolerating sloppy senders ossifies the protocol. Note 01 |

## Registry and measurement data (live, cited)

### S18 — RIPE database, `aut-num: AS1853` ★

- URL: <https://rest.db.ripe.net/ripe/aut-num/AS1853.json> (human form:
  <https://apps.db.ripe.net/db-web-ui/query?searchtext=AS1853>)
- Retrieved: 2026-09-22. Access: public REST API, no key. Licence: RIPE Database
  Terms and Conditions; **not vendored**, the query is one line of `curl`.
- Used for: **the ACOnet AS number, previously unsourced in note 06.**
  `aut-num: AS1853`, `as-name: ACOnet`, `descr: ACOnet Backbone`, `descr: AT`,
  `org: ORG-AA1-RIPE`. The organisation object gives `org-name: ACONET`,
  `org-type: LIR`, address "Computer Center — ACOnet, Universitaetsstrasse 7,
  A-1010 Vienna".

### S19 — PeeringDB

- URLs: <https://www.peeringdb.com/api/net?asn=1853>, <https://www.peeringdb.com/api/ix?name__contains=VIX>,
  <https://www.peeringdb.com/api/netixlan?asn=1853>
- Retrieved: 2026-09-22. Access: public API, no key. Licence: CC-BY 4.0 for the
  data; **not vendored** (it changes weekly).
- Used for: ACOnet's PeeringDB record (net id 285, "Austrian Academic Computer
  Network", IRR AS-set `AS-ACONET`, Educational/Research, Regional, **open**
  peering policy), and **VIX** = Vienna Internet Exchange (ix id 50, 173
  networks), where ACOnet sits on two 100 Gbit/s ports at 193.203.0.1/.2 —
  the concrete instance of note 06's "peer ↔ peer at an IXP".

### S20 — RIPEstat

- URLs: <https://stat.ripe.net/data/prefix-overview/data.json?resource=128.130.0.0/15>,
  <https://stat.ripe.net/data/as-overview/data.json?resource=AS1853>,
  <https://stat.ripe.net/data/asn-neighbours/data.json?resource=AS679>
- Retrieved: 2026-09-22 (the neighbour data is of 2026-09-21). Access: public API.
- Used for: **TU Wien's own AS**. 128.130.0.0/15 (RIPE `inetnum` netname
  `TUNET`, "Technische Universitaet Wien") is originated by **AS679, "TUNET-AS
  Technische Universitat Wien"** — not by ACOnet. The neighbour endpoint then
  shows AS679 with **exactly one neighbour, AS1853, on the "left" side**, i.e.
  single-homed to ACOnet as its upstream — the concrete customer→provider pair
  that note 06's policy section describes in the abstract. Also confirms that
  `www.tuwien.ac.at` = 128.130.35.76 (note 08) is inside TUNET.

### S21 — CIDR Report and the BGP Reports (Huston)

- URLs: <https://www.cidr-report.org/as2.0/>, <https://bgp.potaroo.net/index-bgp.html>
- Retrieved: 2026-09-22 (data of 2026-09-21). Access: public.
- Used for: the size of the global routing system, which the notes previously
  gave from memory: **79 437 ASes** in the routing system, **1 081 248 announced
  prefixes** (CIDR Report) / **1 129 469 IPv4 and 262 840 IPv6 prefixes** seen by
  AS6447 at Route-Views Oregon; 28 054 ASes announce a single prefix.

### S22 — APNIC Labs IPv6 measurement

- URL: <https://stats.labs.apnic.net/ipv6/XA> (XA = world)
- Retrieved: 2026-09-22 (series ends 2026-09-20). Access: public.
- Used for: IPv6 deployment, which note 04 previously gave as "~45 % of Google
  users": APNIC measures **43.7 % IPv6-capable and 41.7 % IPv6-preferring**
  worldwide. (Google publishes a comparable series at
  <https://www.google.com/intl/en/ipv6/statistics.html>, but its data files are
  not machine-fetchable without a browser.)

### S23 — live DNS, used once

- `dig www.tuwien.ac.at A` → 128.130.35.76 (2026-09-22), which is what note 08's
  worked resolution says. In the same check, **`example.com` no longer resolves
  to 93.184.216.34** — it now answers with Cloudflare addresses — so the notes
  and `dns.py`'s worked byte string were rewritten onto RFC 5737 documentation
  addresses [S15].

## General references (cited, not course material, not vendored)

Used where an RFC is silent and a note still needs the claim sourced. Each is
flagged in the note where it is used.

### S24 — Kurose & Ross, *Computer Networking: A Top-Down Approach*, 8th ed., Pearson 2021

- <https://gaia.cs.umass.edu/kurose_ross/> · ISBN 978-0-13-681155-5. Access: not free.
- Used for: the delay decomposition of note 01, the Dijkstra example graph that
  `linkstate.EXAMPLE` and note 07 use, and the AIMD/sawtooth presentation. TISS
  names **no** textbook [S1], so this is a convenience reference, not the
  course's.

### S25 — Tanenbaum, Feamster & Wetherall, *Computer Networks*, 6th ed., Pearson 2021

- ISBN 978-0-13-676405-9. Access: not free.
- Used for: the framing/protocol-design checklist of note 10 and the switching
  and Ethernet material of note 02.

### S26 — Saltzer, Reed & Clark, "End-to-End Arguments in System Design", *ACM TOCS* 2(4), 1984

- <https://web.mit.edu/Saltzer/www/publications/endtoend/endtoend.pdf>
- Retrieved: 2026-09-22. Access: free download from MIT. Licence: ACM copyright,
  no redistribution notice — **cited, not vendored**; `fetch-sources.sh` will
  fetch it for personal use.
- Used for: the end-to-end argument in note 01 (the paper was presented in 1981
  and published in 1984; the notes now give both).

### S27 — Gao & Rexford, "Stable Internet Routing Without Global Coordination", *IEEE/ACM ToN* 9(6), 2001

- <https://www.cs.princeton.edu/~jrex/papers/sigmetrics00.pdf>
- Retrieved: 2026-09-22. Access: free from the author's page; IEEE copyright —
  **cited, not vendored**.
- Used for: the customer/peer/provider preference and export rules that
  `pathvector.GaoRexford` implements and that note 06 calls "valley-free".
  RFC 4271 contains **none** of this; it is where the notes must leave the RFC.

### S28 — Griffin & Wilfong, "An Analysis of BGP Convergence Properties", *SIGCOMM* 1999

- <https://dl.acm.org/doi/10.1145/316188.316231> (paywalled abstract; the "bad
  gadget" construction is reproduced in S27 and in Griffin, Shepherd & Wilfong,
  "The stable paths problem and interdomain routing", ToN 2002).
- Access: ACM copyright, not free. **Cited, not vendored.**
- Used for: note 07's statement that BGP policy configurations can fail to
  converge.

### S29 — Mathis, Semke, Mahdavi & Ott, "The Macroscopic Behavior of the TCP Congestion Avoidance Algorithm", *CCR* 27(3), 1997

- <https://dl.acm.org/doi/10.1145/263932.264023>; author copy at
  <https://www.cs.cmu.edu/~srini/15-744/papers/Mathis-CCR97.pdf>
- Access: ACM copyright. **Cited, not vendored.**
- Used for: the throughput formula ≈ 1.22·MSS/(RTT·√p) in notes 05 and 11.

### S30 — IEEE 802.1Q-2022 and IEEE 802.3-2022

- <https://standards.ieee.org/ieee/802.1Q/10323/>, <https://standards.ieee.org/ieee/802.3/10422/>
- Access: free to read through the IEEE GET program after registration; **not
  redistributable, not vendored, not fetched** (registration is a login).
- Used for: nothing that could be sourced elsewhere. Every Ethernet framing
  number in note 02 (preamble 7+1, 46–1500 payload, 64-byte minimum frame,
  96-bit interframe gap, FCS-32, the 4-byte 802.1Q tag with TPID 0x8100 and a
  12-bit VID) comes from these standards and is therefore marked in note 02 as
  **cited to IEEE but not verified against the text**.

### S31 — IANA protocol registries

- <https://www.iana.org/assignments/protocol-numbers/>,
  <https://www.iana.org/assignments/ieee-802-numbers/>,
  <https://www.iana.org/assignments/service-names-port-numbers/>,
  <https://www.iana.org/assignments/dns-parameters/>
- Retrieved: 2026-09-22. Access: public; IANA registries are freely usable but
  change, so they are **cited, not vendored**.
- Used for: the demultiplexing keys in note 01 (EtherType 0x0800/0x0806/0x86DD,
  IP protocol 1/6/17/58/89, ports 22/23/53/80/179/443) and the DNS type numbers
  in `dns.py`.

### S32 — IETF Trust Legal Provisions 5.0

- <https://trustee.ietf.org/documents/trust-legal-provisions/tlp-5/>
- Retrieved: 2026-09-22. Access: public.
- Used for: the licence argument in [`README.md`](README.md) that lets this
  course vendor its primary sources — §3.c.i grants the right to "copy, publish,
  display and distribute IETF Contributions and IETF Documents in full and
  without modification"; §2.c leaves pre-2015 documents under the policy in
  force when they were published.

### S36 — Course site and lecture 1 slides, 2026-10-05 ★

- Course page: <https://internet.wien/teaching/introduction-to-networking/introduction-to-networking-2026/>
  (E191-06 Internet Infrastructures, TU Wien). Slides, all dated 2026-10-05:
  `…/wp-content/uploads/2026/10/2026-10-05_01-01-organization.pdf`,
  `…_01-02-what-are-networks-and-protocols.pdf`,
  `…_01-03-ietf-iana-icann-rir-nic.pdf`.
- Retrieved: 2026-10-05. Access: public, no login. Only lecture 1 has slides;
  later rows list topics only.
- Re-read 2026-10-09: topics regrouped across the Mondays, the five exercise
  releases are now marked (19.10, 09.11, 23.11, 14.12.2026, 11.01.2027), the
  governance deck `…_01-03-ietf-iana-icann-rir-nic.pdf` returns 404 (its topic
  moved to 12.10), and the final-exam row carries the date 2026-10-05 under the
  heading 2027-01-25 (a typo on the page).
- Licence: none stated, so **not committed**. The PDFs and their text
  extraction sit in the git-ignored `vendor/slides/` (fetch with the three URLs
  above). Notes paraphrase and cite them.
- Used for: the "What lecture 1 stated" section of
  [`../notes/00-exam-focus.md`](../notes/00-exam-focus.md) (exam rules, team,
  literature, scope exclusions, lecture-by-lecture topics) and the history,
  access-network, structure and registry additions to
  [`../notes/01-foundations-and-governance.md`](../notes/01-foundations-and-governance.md).
  It is the first lecturer-authored source and supersedes inference wherever
  the two disagree. It also supports S33's guess about the A4 sheet.

## Substitute practice sources (added by the substitute-source pass)

This course publishes **no script and no past paper** [S1], [S2], so there is
no model of what its exam looks like. This section registers the free,
licence-clear material from *elsewhere* that stands in for one, and the
worked-out practice set built from it lives in
`../src/exercises/` and
[`../notes/12-substitute-practice-set.md`](../notes/12-substitute-practice-set.md).

**None of it is 191.030's.** Every directory, note section and problem carries
the institution, course and year on its first line. A reader must never be able
to mistake an MIT problem set for a TU Wien past paper.

None of the three below is **vendored**. S33 was never downloadable; S34 and
S35 are, but their copyleft terms (NC-SA and SA respectively) would attach to
everything derived from a copy, and both live at stable URLs. So: cited,
restated in our own words, attributed — reasoning per source in the
`README.md` of each exercise directory.

### S33 — MPI-INF / Saarland University, *Data Networks* (Feldmann & **Fiebig**) ★

- URLs: <https://www.mpi-inf.mpg.de/departments/inet/teaching/data-networks-lecture-summer-2023>,
  <https://www.mpi-inf.mpg.de/departments/inet/teaching/data-networks-lecture-summer-2025>,
  course site <https://inet-teaching-25.mpi-inf.mpg.de/dn/>
- Retrieved: 2026-09-22.
- Access: the two MPI-INF overview pages and the course site's news feed and
  timetable are **public**; slides, exercise sheets and exams are behind the
  course CMS login. **No login was attempted and no material was fetched.**
- Licence: none stated. Nothing is copied here; only facts about the course are.
- **Why this entry exists.** It is the result of the highest-value lead of this
  pass: 191.030's lecturer taught a comparable course elsewhere, and a previous
  course of his own is the closest thing to a script that can exist for a brand
  new one. The MPI-INF people page [S5] lists him as a lecturer in **Data
  Networks** (2023–2024), *On the Practice of System and Network Engineering*
  (2024) and a *Router Lab* seminar (2025–2026), and as module manager at TU
  Delft for *Fundamentals of Data Analytics for Cyber Security* and *ICT Risk &
  Control* / *Maintainable Systems Management* — neither of the Delft two a
  networking course.
- **Outcome of the lead: his teaching material is still not public**, which
  confirms rather than contradicts [S5] and
  [`../notes/00-exam-focus.md`](../notes/00-exam-focus.md). What *is* public is
  the course record, and it is worth having:

  | fact | why it matters here |
  |---|---|
  | Lecturers Summer 2023: Feldmann, **Fiebig**, Gasser, Li. Summer 2025: Feldmann and **Fiebig** | he has co-taught an introductory networking lecture three times (SS2023, SS2024, SS2025) |
  | Syllabus: every layer; HTTP, SMTP/POP/IMAP, **DNS**, IP, **BGP**, TCP, UDP; protocol specification and verification; **"network governance and standardization bodies"** | the same unusual fingerprint as 191.030's TISS subject list [S1] — governance named as content, BGP as core |
  | The **final lecture of SS2025 (18.07.2025) was an invited talk and discussion on "Internet Governance and Organization"** | independent evidence that governance is a lecture in its own right for this lecturer, not a footnote |
  | Assessment: multiple-choice pre-test + **midterm** + written **final** (re-exam in October) | the same midterm/final shape as 191.030 [S1], though there the midterm is not a hurdle for the final and here it is |
  | Working time **120 minutes** for both the final and the re-exam | 191.030's two exams are 12:00–14:00, i.e. also two hours [S1] |
  | Permitted aid: **one handwritten A4 sheet, both sides**; no printed or photocopied sheet, no calculator, no electronics | 191.030 states nothing about aids. **Inference only** — do not assume it carries over; ask in the first lecture |
  | The course site links **Kurose & Ross** [S24] as its book and its online lectures | 191.030's TISS page names no textbook [S1]. This does not make K&R the course's book — but it is the book its lecturer's own comparable course used |

  Everything in the last two rows is **inference about 191.030**, not fact, and
  is labelled as such wherever it is used.

### S34 — MIT OpenCourseWare, 6.02 *Introduction to EECS II: Digital Communication Systems*, Fall 2012

- URL: <https://ocw.mit.edu/courses/6-02-introduction-to-eecs-ii-digital-communication-systems-fall-2012/>
- Instructors: Hari Balakrishnan, George Verghese. Institution: MIT.
- Retrieved: 2026-09-22. Access: public, no login.
- Licence: **CC BY-NC-SA 4.0**, stated by OCW in the metadata of every page
  (`"license": "https://creativecommons.org/licenses/by-nc-sa/4.0/"`).
- **Comparable because** its third unit ("Packets") is an introductory
  networking course in miniature and matches three of 191.030's stated topics:
  sources of delay and store-and-forward switching (tutorial 8), **distance-
  vector and link-state routing** including convergence timing and routing
  loops (tutorial 10), and **reliable transport** — stop-and-wait, sliding
  windows, bandwidth-delay product, sequence-number wraparound, loss
  composition (tutorial 11). 191.030's learning outcomes name "Layer 4
  (TCP/UDP)" and "link-state … algorithms", and its practical part named
  "describe TCP behavior given a specific scenario" [S1] (stated on TISS until
  2026-09-2x, removed by 2026-09-27).
- **Decisive property: the tutorials are published with official solutions.**
  This is the only external answer key anywhere in this tree.
  *Correction to the common claim that "OCW publishes exams with solutions":
  6.02 publishes **quizzes 1–3 without** solutions and **tutorials 1–11 with**
  them.*
- **Not comparable** in tutorials 1–7 (source coding, error-correcting codes,
  Viterbi, modulation, LTI systems, Fourier) or tutorial 9 (MAC protocols):
  191.030 names no physical layer, no coding theory and no channel sharing [S1].
  And 6.02 never touches Ethernet/ARP, IPv4 or IPv6 addressing, path vector and
  BGP, DNS, DNSSEC, Telnet, multicast, governance or sockets.
- Used by: `../src/exercises/mit-6.02-2012/`
  (16 tests, each asserting against a number MIT printed).

### S35 — Olivier Bonaventure, *Computer Networking: Principles, Protocols and Practice* (CNP3), 3rd ed., UCLouvain

- URLs: <https://github.com/cnp3/ebook> · <https://www.computer-networking.info>
- Retrieved: 2026-09-22. Access: public, no login.
- Licence: **CC BY-SA 3.0 Unported** per the repository `README.md`; the
  individual exercise files carry a per-file header naming **CC BY 3.0**. Both
  are recorded because they disagree; the stricter is assumed. Exercise files
  used here are dated 2013 and 2019 in their copyright headers.
- **Comparable because** it is the only free, licence-clear exercise set found
  that treats **inter-domain routing policy** — customer/peer/provider
  relationships, the export rule, valley-free paths — as an exercise rather
  than as prose. 191.030's subject list names "link-state and **path-vector**
  algorithms" side by side [S1], which most introductory material does not
  examine. Its exercise files also line up with the syllabus file for file:
  `lan.rst`, `network.rst`, `ipv6.rst`, `transport.rst`, `tcp.rst`,
  `routing-protocols.rst`, `routing-policies.rst`, `dns.rst`, `sockets.rst`,
  `trace.rst`.
- **Not comparable** in `lan.rst`'s spanning-tree and VLAN material, `http.rst`,
  `email.rst`, `tls.rst` and the `packetdrill`/`ipmininet` lab scripts — none
  of those topics is on the TISS list [S1].
- **It publishes no solutions.** Its multiple-choice and auto-graded questions
  run on a UCLouvain INGInious server; the open questions have no printed
  answers. So every answer in
  `../src/exercises/uclouvain-cnp3-2019/`
  is **ours**, checked against the mechanism (RFC 826 [S13], RFC 4271 §9.1.1
  [S9], Gao & Rexford [S27]) rather than against an answer key.

### Considered and rejected

| candidate | why not |
|---|---|
| **Stanford CS144**, *Introduction to Computer Networking* (assignment PDFs at <https://cs144.github.io/assignments/>, retrieved 2026-09-22) | **No licence statement** anywhere on the site or the assignment PDFs. The rule for this pass is that unlicensed material may be linked but neither vendored nor copied, which leaves nothing to build on. Its scope is also the wrong half: a superb TCP implementation sequence, but no BGP, DNSSEC, multicast or governance — and [`../src/py/tcp_sim.py`](../src/py/tcp_sim.py) already covers the transport ground |
| **Kurose & Ross companion site** [S24] | interactive problems with worked answers, but Pearson copyright and no redistribution licence. Cited where it already is; nothing copied |
| **MIT 6.033** *Computer System Engineering* | CC BY-NC-SA and it does reach DNS and congestion control, but it is a systems-design course whose networking is a third of a third. 6.02's tutorials are closer to 191.030's stated topics and, unlike 6.033's, come with solutions |
| **VoWi and any TUWEL material** | student-uploaded or login-walled; see the section below |

## Sources deliberately not used

- **TUWEL** (`tuwel.tuwien.ac.at`): no TUWEL course is linked from 191.030's
  TISS page (re-read 2026-09-27), so where slides and exercise sheets will be
  published is not known; ask in the first lecture. TUWEL needs a TU Wien login and
  its contents are not ours to redistribute. Not fetched.
- **The TISS course-materials link**: 191.030's 2026W page carries none; the
  2024W page of S6 does, and it redirects to the TU Wien IdP. Not followed.
- **IEEE 802.1Q / 802.3 full text** (S30): free to read only behind a
  registration wall.
- **Anything requiring a login anywhere.** No registration, deregistration or
  submission was made in TISS.
