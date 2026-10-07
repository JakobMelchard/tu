# 191.030 Introduction to Networking — notes

Ordered index. Each note has definitions, header layouts as tables, a worked example, pitfalls, exam-style questions with answers, and pointers into `../src/py`. Sequence numbers follow the official topic list (foundations → protocols and technologies → implementation) [S1]; note 11 is the playbook for the five practical exercises and note 12 the substitute practice set.

**Course state, 2026-09-27** [S1]: deregistration until 02.10.2026 12:00. Twelve Monday lectures 12:00–14:00 in EI 11 (05.10.2026 – 25.01.2027); mid-term Mon 30.11.2026 12:00–14:00 in the lecture room (register 12.10 – 23.11.2026 12:00), final Mon 25.01.2027 12:00–14:00 (register 12.10.2026 – 18.01.2027 12:00); five exercises × 20 after lectures 7, 9, 16, 19, 22 + 100 + 100, pass at 150. No TUWEL course is linked from TISS. TISS's practical-part examples (traces, topology, TCP scenarios) were removed from the course description by 2026-09-27; see note 00.

**Update 2026-10-05:** lecture 1 happened and the course site publishes slides [S36]. [00 Exam focus](00-exam-focus.md) has a new "What lecture 1 stated" section (exam rules, A4 sheet, team, literature, per-lecture topics); [01](01-foundations-and-governance.md) gains history, access networks and registry details from the three decks. Check the course site after each lecture for new slides.

**Start with [00 Exam focus](00-exam-focus.md).** 191.030 is new in 2026W and has no previous offering, no VoWi page and no public past paper [S2], [S5], [S7] — that note says what is known about the examination, what is inferred, and how much to trust each.

**Then know what note 12 is not.** 191.030 publishes no practice material at all, so [12 Substitute practice set](12-substitute-practice-set.md) is built from **other courses' free material**, condensed and labelled: MIT 6.02 Fall 2012 under CC BY-NC-SA 4.0 [S34], CNP3 (Bonaventure, UCLouvain) under CC BY-SA 3.0 [S35], and our own problems for the four topics — governance, DNSSEC, Telnet, multicast — for which no free exercise set exists. Every problem carries its origin in brackets. Nothing in these notes is a TU Wien past paper, because there is none.

Every claim below is cited `[S<n>]` into [`../refs/SOURCES.md`](../refs/SOURCES.md). The protocol claims rest on **52 RFCs vendored in `../refs/rfc/`**, mapped section by section in [`../refs/standards-map.md`](../refs/standards-map.md); the numbers those RFCs print are reproduced by [`../src/py/test_rfc_vectors.py`](../src/py/test_rfc_vectors.py). Anything that could *not* be sourced is marked inline `(unsourced: …)`. Changes made by the source pass are in CHANGELOG.md.

| # | Note | One line |
|---|---|---|
| 00 | [Exam focus](00-exam-focus.md) | What TISS actually commits the exam to, the derived lecture/exercise calendar, and an honest account of why there is nothing to mine |
| 01 | [Foundations and governance](01-foundations-and-governance.md) | Packet switching, layering and encapsulation, end-to-end principle, RFC process, IETF/ICANN/RIRs, multi-stakeholder model |
| 02 | [Ethernet and ARP](02-ethernet-and-arp.md) | Frames, MAC addresses, switch learning, VLANs, ARP request/reply, cache, spoofing |
| 03 | [IPv4](03-ipv4.md) | Header, CIDR and subnetting (worked), fragmentation, TTL, ICMP, NAT |
| 04 | [IPv6](04-ipv6.md) | Header, address types, SLAAC, NDP instead of ARP, transition mechanisms |
| 05 | [UDP and TCP](05-udp-and-tcp.md) | Headers, checksums, handshake and teardown, seq/ack, RTO, flow and congestion control, state machine (`tcp_fsm.py`), scenario traces |
| 06 | [Forwarding and routing](06-forwarding-and-routing.md) | Forwarding tables, longest prefix match, static vs dynamic, DV vs LS vs PV, AS and BGP, policy |
| 07 | [Link-state and path-vector algorithms](07-link-state-and-path-vector.md) | Dijkstra worked table, OSPF, Bellman-Ford and count-to-infinity, BGP decision process |
| 08 | [DNS, DNSSEC and Telnet](08-dns-dnssec-telnet.md) | Hierarchy, resolvers, record types, message format, caching, DNSSEC chain of trust, Telnet negotiation |
| 09 | [Unicast and multicast routing](09-unicast-and-multicast-routing.md) | Delivery models, IGMP/MLD, RPF, source and shared trees, PIM-DM/SM |
| 10 | [Protocol design and sockets](10-protocol-design-and-sockets.md) | Framing, state, errors, versioning, socket API, blocking vs select, worked mini-protocol |
| 11 | [Exercise playbook](11-exercise-playbook.md) | Reading a packet trace, deriving a topology, describing TCP behaviour (the three types TISS named until 2026-09-2x), connection-state walks, tool cheat sheet |
| 12 | [Substitute practice set](12-substitute-practice-set.md) | 22 exam-shaped problems with answers, built from **free material from other institutions** (MIT 6.02, CNP3/UCLouvain) plus our own where none exists — every problem tagged with its origin |

The TISS page names **no** textbook and says "No lecture notes are available" [S1]. The primary sources are therefore the standards, which is why they are vendored here rather than merely cited: 52 RFCs, 4.1 MB, redistributable in full under the IETF Trust's provisions [S32] — see [`../refs/README.md`](../refs/README.md). Kurose & Ross [S24] and Tanenbaum, Feamster & Wetherall [S25] are convenience references, not the course's, and are cited only where no RFC covers the point.
