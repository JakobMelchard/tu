# 01 Foundations and Internet governance

> Sources: [`../refs/SOURCES.md`](../refs/SOURCES.md). The protocol claims below
> are cited to vendored RFCs; **the governance section is the weakest-sourced
> part of these notes** and says so where it stands on nothing but background
> knowledge. Read [`00-exam-focus.md`](00-exam-focus.md) first: governance is
> listed *first* in the official subject list [S1].

## What the Internet is

A **network of networks**: independently operated networks (**autonomous systems**, AS) interconnected by a common protocol suite (TCP/IP) and voluntarily agreed rules. Nobody owns it; it works because the participants agree on protocols (RFCs), names (DNS) and numbers (IP addresses, AS numbers).

Two switching paradigms:

| | Circuit switching | Packet switching |
|---|---|---|
| Resource allocation | reserved end to end before data flows (telephone) | none; each packet is forwarded independently (**store and forward**) |
| Guarantees | fixed bandwidth, fixed delay | best effort: packets may be delayed, reordered, lost |
| Efficiency | idle reservation wastes capacity | **statistical multiplexing**: bursty sources share links |
| Failure | call drops | packets route around failures |

The Internet is packet switched and **datagram** based (no per-flow state in routers, "dumb network, smart edges").

## Delay and loss (the quantities exercises ask for)

For one link of rate $R$ bit/s, length $d$, propagation speed $s$, packet size $L$ bits:

$$d_{\text{nodal}} = d_{\text{proc}} + d_{\text{queue}} + \underbrace{L/R}_{\text{transmission}} + \underbrace{d/s}_{\text{propagation}}$$

Transmission delay is the time to push the bits onto the wire; propagation is the time for one bit to cross. For $N$ store-and-forward links of equal rate: $N \cdot L/R$ (plus propagation). The **bandwidth-delay product** $R \cdot \text{RTT}$ is the number of bits "in flight" needed to keep a pipe full; it reappears as the TCP window in note 05.

Traffic intensity $I = L a / R$ with arrival rate $a$: as $I \to 1$ queueing delay grows without bound; routers drop packets when queues are full (this is *loss* as TCP sees it).

## Layering and encapsulation

Each layer offers a **service** to the layer above through an **interface**, implemented by a **protocol** (message format + rules) between peers at the same layer.

| Layer (Internet model) | Unit | Addresses | Examples | Note |
|---|---|---|---|---|
| 5 Application | message | names, URLs | HTTP, DNS, Telnet | 08, 10 |
| 4 Transport | segment / datagram | port (16 bit) | TCP, UDP | 05 |
| 3 Network | packet | IP address | IPv4, IPv6, ICMP | 03, 04, 06 |
| 2 Link | frame | MAC address | Ethernet, ARP, Wi-Fi | 02 |
| 1 Physical | bits | – | copper, fibre, radio | – |

The OSI model inserts Session (5) and Presentation (6) between Transport and Application; the Internet folds them into the application. "Layer 2/3/4" in the course always means link/network/transport, and the official subject list uses exactly that shorthand [S1]. The four-layer split above is RFC 1122 §1.1.3's ("application, transport, internet, link") [S13].

**Encapsulation**: each layer prepends its header (Ethernet also appends a trailer) to the payload handed down. On the wire a TCP segment looks like

| Ethernet header (14) | IP header (20) | TCP header (20) | application data | Ethernet FCS (4) |
|---|---|---|---|---|

A router processes up to layer 3 (strips L2, looks at the IP destination, re-encapsulates in a new L2 frame for the next hop, possibly a different link technology); a switch only up to layer 2; hosts all layers. This is why the IP header survives end to end but the Ethernet header changes on every hop; and why the source MAC of a packet arriving at your laptop is the MAC of your router, not of the far host (exercise pitfall).

**Demultiplexing** keys: EtherType (0x0800 IPv4, 0x86DD IPv6, 0x0806 ARP) → IP protocol number (1 ICMP, 6 TCP, 17 UDP, 58 ICMPv6, 89 OSPF) → destination port (23 Telnet, 53 DNS, 80 HTTP, 179 BGP, 443 HTTPS). All three are IANA registries [S31]; the RFCs point at them rather than fixing the numbers themselves.

## Design principles

- **End-to-end argument** (Saltzer, Reed & Clark; presented 1981, published in *ACM TOCS* 2(4), 1984) [S26]: a function (reliability, encryption, ordering) can only be implemented completely and correctly at the endpoints that know the application; putting it in the network is at best a performance optimisation. Consequence: IP is unreliable, TCP in the hosts provides reliability. *Not in any RFC* — it is a paper, and the notes cite it as one.
- **Robustness principle**, RFC 761 §2.10 [S17], in its original wording: "be conservative in what you do, be liberal in what you accept from others"; restated for hosts in RFC 1122 §1.2.2 [S13]. Now considered double-edged: RFC 9413 [S17] is the IAB's own re-assessment — tolerating sloppy senders freezes bugs into the protocol and ossifies it.
- **Fate sharing**: state about a connection lives in the endpoints, so it is lost only when the endpoint itself dies.
- **Hourglass**: many link layers below, many applications above, one network layer (IP) in the waist; changing the waist is hard (see IPv6 transition, note 04).

## Standards and governance: who decides what

> **Sourcing warning.** Partly superseded 2026-10-05: lecture 1 covered this
> topic and its slides [S36] are summarised in "Lecture 1 additions" below;
> prefer that section where the two differ. The rest of this section is
> background knowledge that this pass did **not** verify against a primary source. The bodies' own charter
> documents (BCP 9 / RFC 2026 for the IETF standards process, BCP 78 for its
> copyright policy, ICANN's bylaws, the RIR policy-development processes) were
> not fetched. Treat the table as a map, not as a citation, and check anything
> you intend to write in an exam against
> <https://www.ietf.org/standards/process/>, <https://www.iana.org/> and
> <https://www.icann.org/>.

| Body | What it controls | How |
|---|---|---|
| **IETF** (Internet Engineering Task Force) | protocols: publishes **RFCs** (Request for Comments) | open working groups, "rough consensus and running code"; no membership, anyone can post to the mailing list. Steering by IESG; architecture oversight IAB; parent organisation ISOC |
| **IANA** (functions operated by PTI/ICANN) | the registries: protocol numbers (ports, EtherTypes, DNS types), IP address blocks to RIRs, DNS root zone | administrative, following IETF and community policy |
| **ICANN** | names and numbers policy: top-level domains, root servers coordination, contracts with registries/registrars | multi-stakeholder: supporting organisations (GNSO, ccNSO, ASO) and advisory committees (GAC governments, ALAC users, SSAC security) |
| **RIRs** (RIPE NCC Europe, ARIN, APNIC, LACNIC, AFRINIC) | allocate IP address blocks and AS numbers to LIRs/ISPs in their region; run WHOIS/RDAP and RPKI | bottom-up policy development in open regional meetings |
| **W3C, IEEE 802, ITU-T** | web standards; Ethernet/Wi-Fi (802.3/802.11); telecom standards | IEEE and ITU are membership/state driven, contrast with IETF |
| Operators, NOGs, IXPs | run the networks and peering points; de facto operational practice (RIPE meetings, NANOG) | voluntary |

**RFC track**: Internet-Draft (I-D, expires after 6 months) → working-group adoption → IETF last call → IESG approval → RFC with a status: *Proposed Standard* → *Internet Standard* (STD number); or *Informational*, *Experimental*, *Best Current Practice* (BCP), *Historic*. Only standards-track RFCs are "the standard"; RFC 1149 (IP over avian carriers) is an April 1st RFC and Informational. *(unsourced: RFC 2026 was not fetched in this pass.)*

You can see the whole hierarchy in `../refs/rfc/`: RFC 9293 replaced RFC 793 as **STD 7** (TCP) in 2022, RFC 8200 is **STD 86** (IPv6), RFC 2328 is **STD 54** (OSPFv2) and has stood unchanged since 1998, RFC 2827 is **BCP 38**, and RFC 9413 is Informational — an opinion about how to write protocols, not a protocol. RFCs are also why this course can vendor its sources at all: the IETF Trust grants an unlimited right to redistribute them in full [S32], which almost no other standards body does — contrast IEEE 802.3 and 802.1Q, which you may read after registering and may not redistribute [S30].

**Multi-stakeholder principle**: no single stakeholder group (governments, industry, technical community, civil society, users) has final authority; decisions come from open processes in which all can participate. Contrast: the ITU model (one state, one vote) and national regulation. Tension points the lecture is likely to raise: the 2016 IANA stewardship transition (US government gave up its oversight contract), IPv4 exhaustion and address markets, root-server operation, sanctions vs. neutrality of infrastructure, and the difference between *technical* coordination (which IETF/ICANN do) and *content* regulation (which they explicitly do not).

## Lecture 1 additions (05.10.2026) [S36]

Everything here is from the lecturer's slides and is the best-sourced part of
this note. It also upgrades the governance table above: IETF, IANA, ICANN and
RIR roles match, and the details below are what lecture 1 actually said.

**Edge, access, core.** Edge: hosts (clients, servers, often in data centres).
Access networks and physical media connect edge to the first router. Core: a
mesh of interconnected routers, a network of networks. Core has two functions:
**forwarding** (local, per router: input link to output link, a.k.a. switching)
and **routing** (global: computing source-destination paths).

| Access technology | Figures on the slides |
|---|---|
| Cable (HFC, FDM, shared to the headend) | down 40 Mbps - 1.2 Gbps, up 30-100 Mbps |
| DSL (telephone line to the DSLAM, dedicated) | down 24-52 Mbps, up 3.5-16 Mbps |
| WLAN 802.11b/g/n | 11, 54, 450 Mbps, about 30 m |
| Cellular LTE/5G | tens of Mbps up to 1 Gbps, tens of km |
| Enterprise Ethernet / data centre | 100 Mbps - 10 Gbps / 10s-100s Gbps |

Media: twisted pair (Cat 5: 100 Mbps and 1 Gbps; Cat 6: 10 Gbps), coax
(bidirectional, broadband, FDM), fibre (light pulses, thousands of Gbps,
low error rate, immune to EM noise), radio (reflection, obstruction,
interference), geostationary satellite about 270 ms end to end.

Packet transmission: the sender splits a message into packets of $L$ bits and
sends at rate $R$, so $d_{\text{trans}} = L/R$ (already above). The lecture's
learning objective is to calculate latency and bandwidth for example topologies
with this terminology.

**Internet structure, stepwise.** Millions of access ISPs cannot be meshed
pairwise, and one global ISP would attract competitors. So: competing global
ISPs interconnect by private peering or at **IXPs**; regional ISPs connect
access networks to them; content providers (Google, Meta) run private networks
that bypass tier-1 and regional ISPs. At the centre a few well-connected
**tier-1** networks (examples named: Lumen, Arelion, Cogent, NTT).

**Security framing** (named in lecture, but the course is *not* about security
and Tor/VPNs are explicitly out of scope): original vision "a group of mutually
trusting users attached to a transparent network". Attacks: packet sniffing
(promiscuous interface, Wireshark), IP spoofing (false source address),
DoS/DDoS (botnet). Defences: authentication, encryption, integrity checks,
VPNs, firewalls ("off by default" middleboxes).

**Protocol definition used in the lecture.** A protocol defines message
composition (to express semantics), decomposition (to extract them), the valid
states of the entities, and the actions taken on state plus received message.
Short form: format and order of messages and the actions on send and receive.
Layering motive: explicit structure and modularity (a layer's implementation can
change transparently to the rest).

**History checkpoints** (a plausible short-answer topic since a whole deck is
spent on it):

| Year | Event |
|---|---|
| 1970 / 1974 / 1976 | ALOHAnet; Cerf and Kahn architecture for interconnecting networks; Ethernet at Xerox PARC |
| 1983 | TCP/IP deployed; DNS defined (name to address) |
| 1982 / 1985 / 1988 | SMTP; FTP; TCP congestion control |
| early 1990s | ARPAnet decommissioned; HTML and HTTP standardised |
| 1991 / 1995 | NSF lifts commercial-use restriction; NSFnet decommissioned |
| 2008 | software-defined networking |
| 2017 / 2023 | more mobile than fixed devices; about 15 billion devices |

Cerf and Kahn principles: minimalism and autonomy (no internal change to
interconnect networks), best-effort service, stateless routing, decentralised
control.

**Registries and bodies, as stated.**

- **IETF**: open, **no formal membership**, volunteers (often employer-funded),
  working groups by area, "rough consensus and running code" **without formal
  voting**. RFC series: BCP, STD, FYI; examples RFC 4271 (BGP-4), RFC 2460
  (IPv6; obsoleted by 8200), RFC 2026 (the standards process), RFC 7705 (AS
  migration), April-1st humour RFC 1149 and RFC 7511 (scenic routing for IPv6).
  **BCP 14 = RFC 2119 + RFC 8174**: MUST, SHOULD, MAY etc. carry normative
  meaning only in capitals.
- **History of allocation**: Jon Postel alone until 1998; **ICANN formed 1998**
  and took over the IANA functions under a US Department of Commerce contract;
  **2016** transition to a multi-stakeholder model free of US oversight.
- **ICANN**: non-profit, overseeing names and numbers, global IP and AS number
  allocation, DNS root zone.
- **RIRs**: manage number resources per region, receive them from ICANN, set
  local policy; five RIRs (AfriNIC, APNIC, ARIN, LACNIC, RIPE NCC) united in the
  **NRO**. RIPE NCC: Europe, West Asia, former USSR (over 75 countries);
  allocations to members; **policy open to everyone**, not just members.
  Services: WHOIS database, RIPE meetings, RIPE Atlas, **RPKI (ROA and ASPA)**,
  training, best-practice publications.
- **LIRs**: organisations holding an RIR allocation (ISPs, universities,
  enterprises) who assign onward to customers; IPv4 depletion made more
  organisations become LIRs just to obtain space.
- **NOGs**: informal operator forums (AT:NOG, DeNOG, NANOG, UKNOF, NLNOG, INOG).
- **nic.at**: registry of .at, founded 1998 in Salzburg, owned by the non-profit
  Internet-Stiftung, about 30 staff, about 300 partners/resellers; .at
  registrable since 1988, University of Vienna was the registrar before.
- Global versus regional policy: global policies (NRO, ICANN) over regional
  policies (the five RIR communities).

Correction to this note's earlier unsourced table: the ICANN supporting
organisations (GNSO, ccNSO, ASO) and advisory committees were not mentioned in
lecture 1; they stay as background knowledge only.

## Worked example: one HTTP request through the stack

Laptop 192.168.1.10 fetches `http://www.example.com/`:

1. DNS (application over UDP 53) resolves `www.example.com` → 203.0.113.10 (note 08). *(The address is RFC 5737 documentation space [S15]. These notes deliberately no longer use 93.184.216.34: that was `example.com`'s address for a decade, textbooks are full of it, and as of 2026-09-22 it is wrong — the name now answers with Cloudflare addresses [S23].)*
2. TCP (note 05): the socket picks an ephemeral source port 51234, sends SYN to 203.0.113.10:80.
3. IP (note 03/06): destination is not in 192.168.1.0/24 → forward to default gateway 192.168.1.1.
4. ARP (note 02) resolves 192.168.1.1 → router MAC; the frame carries dst MAC = router, src MAC = laptop, IP dst = 203.0.113.10.
5. Each router decrements TTL, re-encapsulates for its next hop. The home router additionally rewrites src IP/port (NAT).
6. At the server the reverse happens; the application sees a byte stream, nothing about frames.

## Pitfalls

- "Layer 3 device" means it *forwards on* layer 3 headers; it still has layer 1 and 2.
- Ports are transport-layer, MACs link-layer, IPs network-layer: mixing them ("the MAC address of a port") is the most common terminology error in exams.
- RFC ≠ standard; check the status line.
- ICANN does not run the Internet and IETF does not enforce anything: compliance is voluntary and driven by interoperability.

## Exam-style questions

1. *A 1 kB packet crosses three 10 Mbit/s store-and-forward links of 100 km each (propagation $2\cdot10^8$ m/s). Total delay, ignoring queueing and processing?* Transmission per link $8000/10^7 = 0.8$ ms, three links: 2.4 ms. Propagation per link $10^5/2\cdot10^8 = 0.5$ ms, three links: 1.5 ms. Total 3.9 ms.
2. *Why is reliability implemented in TCP and not in IP?* End-to-end argument: only the endpoints can guarantee delivery to the application (a reliable hop-by-hop network still loses data in a crashing router); per-hop reliability would burden applications that do not need it (VoIP), so IP stays best effort and TCP adds reliability where needed.
3. *Which header fields change at every router and which stay?* Ethernet src/dst MAC and FCS change (new frame per link); IP TTL and header checksum change; IP source/destination, transport and application headers stay (except through NAT, which rewrites IP/port and checksums).
4. *Name the organisation responsible for (a) allocating an IPv4 /22 to an Austrian ISP, (b) the TCP specification, (c) the port-number registry, (d) delegating `.at`.* (a) RIPE NCC, (b) IETF (RFC 9293, STD 7) [S13], (c) IANA [S31], (d) ICANN/IANA root zone management (operated by nic.at as registry). A concrete instance of (a): **ACOnet**, the Austrian academic network, is the RIPE NCC LIR holding `AS1853` [S18], and **TU Wien has an AS of its own**, `AS679` ("TUNET-AS"), which originates 128.130.0.0/15 [S20] — see note 06.
5. *What does "multi-stakeholder" exclude?* A single authority (state or company) deciding unilaterally; it does not exclude governments, who participate through the GAC and RIR policy fora.

## Code

`src/py/headers.py` — `parse_frame()` walks the encapsulation Ethernet → IP → TCP/UDP and returns one dict per layer; `summarize()` prints a tcpdump-style line. `src/py/pcap.py` — `synthetic_trace()` is the worked HTTP example as bytes.
