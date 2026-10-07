# 06 Forwarding and routing (layer 3, control vs. data plane)

> **Sourcing.** BGP is RFC 4271 [S9], vendored and cited by section throughout;
> 4-octet AS numbers are RFC 6793 and multiprotocol BGP RFC 4760 [S15], [S17].
> **The business model is not in any RFC**: customer/peer/provider preference
> and the valley-free export rule are Gao & Rexford 2001 [S27], and
> non-convergence is Griffin & Wilfong [S28]. Administrative distance is a
> Cisco convention with no standard at all. Each is marked below.

## Two planes

| | Forwarding (data plane) | Routing (control plane) |
|---|---|---|
| Question | given this packet, which output port/next hop? | how do the tables get filled? |
| Timescale | per packet, nanoseconds, hardware (ASIC/TCAM) | seconds to minutes, software |
| Input | destination address, forwarding table (FIB) | topology/reachability messages from neighbours, policy |
| Where | every router, every host | routers (and hosts for static/default routes) |

Router pipeline: input port (L2 decapsulation, lookup) → switching fabric → output port (queueing, scheduling, L2 encapsulation). Queues overflow → drops → TCP slows down (note 05); AQM (RED, CoDel) drops early to signal congestion.

## Forwarding table and longest prefix match

Entries: `prefix → (next hop, interface)`. A destination matches every entry whose prefix covers it; the **most specific (longest) prefix wins**, which allows a default route 0.0.0.0/0 to coexist with aggregates and host routes. Next hop `None`/"direct" means the destination is on-link (ARP/NDP for the destination itself); otherwise ARP for the next hop.

Worked example (`subnet.py::demo_table`):

| Prefix | Next hop | Interface |
|---|---|---|
| 10.1.2.7/32 | 10.1.2.7 | eth2 |
| 10.1.2.0/24 | direct | eth2 |
| 10.1.0.0/16 | 10.1.1.2 | eth1 |
| 10.0.0.0/8 | 10.1.1.1 | eth1 |
| 0.0.0.0/0 | 192.0.2.1 | eth0 |

| Destination | Matching prefixes | Chosen |
|---|---|---|
| 10.1.2.9 | /0, /8, /16, /24 | 10.1.2.0/24 → direct on eth2 |
| 10.1.9.9 | /0, /8, /16 | 10.1.0.0/16 via 10.1.1.2 |
| 10.9.9.9 | /0, /8 | 10.0.0.0/8 via 10.1.1.1 |
| 8.8.8.8 | /0 | default |

Data structures: binary trie (one bit per level, 32 steps), Patricia/LC-trie, or TCAM (parallel ternary match with priority = prefix length). Linux: `ip route get <dst>` performs the lookup for you. **Equal-cost multipath** (ECMP): several next hops for one prefix, chosen by hashing the 5-tuple so one flow stays on one path.

How a host decides (note 03): own prefix → direct, else default gateway. The same LPM rule; hosts just have short tables.

## Static vs. dynamic routing

| | Static | Dynamic |
|---|---|---|
| Configured | by hand (`ip route add`) | learnt by a routing protocol |
| Reacts to failure | no | yes, after convergence |
| Fits | stub networks, default routes, small sites | everything else |
| Cost | admin time, errors | protocol traffic, CPU, complexity, transient loops |

Administrative distance (preference between sources when several protocols offer the same prefix): connected 0 < static 1 < eBGP 20 < OSPF 110 < RIP 120 < iBGP 200. **These are Cisco's numbers and there is no RFC for any of it** *(unsourced: vendor documentation, not fetched in this pass)*; Linux uses route metrics and per-protocol priorities instead, and other vendors pick different values. Within one protocol the metric decides; across protocols the distance.

## Routing as a graph problem

Nodes = routers, edges = links with cost (1 for hop count; OSPF: reference bandwidth / link bandwidth; or delay, or admin-set). Goal: least-cost path to every destination prefix, computed distributedly. Three families:

| Family | Each router knows | Exchanges | Computes | Examples |
|---|---|---|---|---|
| **Distance vector** | its neighbours' distance vectors | `{dest: cost}` with neighbours only, periodically and on change | Bellman-Ford iteratively: $D_x(y) = \min_v [c(x,v) + D_v(y)]$ | RIP, (EIGRP) |
| **Link state** | the whole topology | link-state advertisements **flooded** to everyone | Dijkstra locally | OSPF, IS-IS |
| **Path vector** | full AS path per prefix, from neighbours | `{prefix: [AS path], attributes}` with neighbours | policy-based best-path selection; loops detected by seeing own AS in the path | BGP |

| Property | DV | LS | PV |
|---|---|---|---|
| Message size | small, to neighbours | $O(\text{links})$ to all | per prefix, with path |
| Convergence | slow, can loop (count to infinity) | fast, loop-free once synchronised | slow (policy, MRAI timers), path exploration |
| Robustness | one bad router poisons the net | a bad LSA is confined to its content | policy errors propagate (route leaks) |
| Scalability | small | areas (OSPF) | the whole Internet |

Details and worked runs in note 07.

## Hierarchy: intra- vs. inter-domain

An **autonomous system** (AS) is a set of prefixes and routers under one administration with one routing policy, identified by an AS number — originally 2 octets, extended to 4 octets by RFC 6793 [S15], which is why you see both `1853` and `AS_TRANS`/32-bit forms.

Two Austrian instances, both checkable from your laptop, both now sourced:

| what | value | how it was verified |
|---|---|---|
| **ACOnet**, the Austrian academic network | **AS1853** | RIPE database `aut-num: AS1853`, `as-name: ACOnet`, `descr: ACOnet Backbone`, `org: ORG-AA1-RIPE` (`org-name: ACONET`, an `LIR` at Universitätsstraße 7, 1010 Vienna) [S18]. PeeringDB net 285, "Austrian Academic Computer Network", IRR set `AS-ACONET`, Educational/Research, **open** peering policy [S19] |
| **TU Wien itself** | **AS679**, "TUNET-AS" | it originates 128.130.0.0/15, RIPE `inetnum` netname `TUNET`, "Technische Universitaet Wien" [S20]. So TU Wien is *not* inside AS1853 — it is its own AS. RIPEstat sees it with **exactly one BGP neighbour, AS1853, on the "left" (upstream) side** (2026-09-21) [S20]: a textbook single-homed customer, and the smallest possible instance of the customer→provider relationship below |
| where ACOnet peers | **VIX**, the Vienna Internet Exchange | PeeringDB ix 50, 173 participating networks; ACOnet sits on two 100 Gbit/s ports, 193.203.0.1 and .2 [S19] |

Scale of the global table, as of 2026-09-21 [S21]: **79 437 ASes** in the routing
system and **1 081 248 announced prefixes** (CIDR Report), or 1 129 469 IPv4 and
262 840 IPv6 prefixes as seen by AS6447 at Route-Views Oregon. 28 054 of those
ASes announce a single prefix — most of the Internet's ASes are stubs. (These
numbers move; re-run the check before quoting them.)

- **IGP** (interior gateway protocol) inside an AS: OSPF, IS-IS, RIP. Optimises cost.
- **EGP** between ASes: **BGP-4** (RFC 4271), the only one. Optimises *policy* (money, contracts); cost is secondary.

Why not one protocol? Scale (a global link-state database is impossible), autonomy (an AS does not want to reveal its topology or let others pick its internal paths), and policy (which routes to accept and advertise depends on business relations).

## BGP basics

- Runs over **TCP port 179** between configured peers, no discovery (RFC 4271 §3, §8.2.2 [S9]). **eBGP** between ASes (usually directly connected, TTL 1), **iBGP** within an AS to distribute externally learnt routes (full mesh or route reflectors; iBGP does not re-advertise iBGP routes to prevent loops, since inside an AS the AS path does not grow).
- Messages: OPEN, UPDATE (announce prefixes with attributes, withdraw prefixes), KEEPALIVE, NOTIFICATION (RFC 4271 §4) [S9].
- Attributes (RFC 4271 §4.3, §5.1) [S9]: **AS_PATH** (§5.1.2, prepended on each eBGP hop; loop detection), **NEXT_HOP** (§5.1.3), **LOCAL_PREF** (§5.1.5 — **iBGP only**: it MUST NOT be sent to an external peer, which is exactly why it expresses *your* policy and not somebody else's), **MED** (§5.1.4, a hint to one neighbouring AS about which of several links to enter by, lowest wins), ORIGIN (§5.1.1, IGP < EGP < INCOMPLETE), COMMUNITIES (RFC 1997, *not* RFC 4271; tags for policy such as "do not export to peers").
- Decision process: see note 07 for the RFC's exact wording. The one-line version — highest LOCAL_PREF → shortest AS_PATH → lowest ORIGIN → lowest MED → eBGP over iBGP → lowest IGP cost to NEXT_HOP → lowest router ID — is right in substance but is *not* how RFC 4271 is organised, and note 07 says why.
- **Timers**, all "suggested default values" from RFC 4271 §10 [S9], and all previously unsourced here: ConnectRetryTime **120 s**, HoldTime **90 s**, KeepaliveTime = HoldTime/3 = **30 s**, MinASOriginationInterval **15 s**, MinRouteAdvertisementInterval (MRAI) **30 s on eBGP but only 5 s on iBGP** (§9.2.1.1 requires the internal one to be the shorter, because convergence inside an AS has to be fast). Every one of them is jittered by a fresh draw from U(0.75, 1.0) so that a router's messages do not synchronise into peaks. Only HoldTime MUST be configurable per peer; the rest MAY be. Implemented and tested in [`../src/py/bgp_decision.py`](../src/py/bgp_decision.py).

### Policy and relationships (Gao–Rexford [S27] — *not in RFC 4271*)

RFC 4271 defines a mechanism and deliberately says nothing about money. Everything in this subsection comes from Gao & Rexford's 2001 model [S27], which is a *description* of what operators do, plus the observation that following it guarantees convergence.

| Relationship | Money | Export rule (valley-free) |
|---|---|---|
| Customer → provider | customer pays for transit to everything | provider exports *everything* to the customer; customer exports only its own and its customers' prefixes |
| Peer ↔ peer | settlement-free, usually at an IXP — concretely, VIX in Vienna, 173 networks, where ACOnet has two 100G ports [S19] | each exports only own + customer routes to the other |
| Sibling | same organisation | everything |

Preference on import: customer routes (they pay) > peer routes (free) > provider routes (cost). A route must not go provider → AS → provider or peer → AS → peer ("valley"), otherwise the AS would carry transit for free. **Route leak**: a customer re-exports a provider's routes to another provider, which prefers the customer route and sends the world's traffic through a small AS. **Prefix hijack**: an AS originates a prefix it does not own (or a more specific); **RPKI**/ROA (which AS may originate which prefix) and route origin validation mitigate this; path validation (BGPsec/ASPA) is still being deployed. *(unsourced: RFC 6480/6811/8893 were not fetched in this pass.)*

**Hot-potato routing**: an AS hands traffic to the neighbour at the nearest exit (lowest IGP cost to NEXT_HOP), so paths are often asymmetric (A→B differs from B→A). Traceroute in both directions shows this.

## Worked example: which route does AS 1 use?

AS 1 learns prefix P from customer AS 5 with path (5, 9, 9, 9) (AS 9 did **path prepending** to make itself less attractive) and from peer AS 2 with path (2, 9). LOCAL_PREF: customer 100 > peer 80 → the customer route wins despite the longer AS path. AS 1 exports it to all neighbours (customer route). Had both been peer routes, (2, 9) would win on AS_PATH length, and AS 1 would export it only to customers.

## Pitfalls

- Longest prefix match, not "first match" and not "shortest". A /32 always beats a /24.
- A next hop must be reachable via a directly connected prefix; recursive routes (BGP NEXT_HOP resolved via the IGP) are the exception that proves the rule.
- Routing tables contain prefixes, never MAC addresses; the ARP table contains MACs, never prefixes.
- BGP does not choose the shortest path; it chooses the most preferred by policy, and AS_PATH length is only the second criterion.
- "The Internet routes around damage" is true only after convergence, which for BGP can take minutes.

## Exam-style questions

1. *Table: 10.0.0.0/8 → R1, 10.128.0.0/9 → R2, 10.192.0.0/10 → R3, default → R4. Next hop for 10.200.1.1, 10.130.1.1, 10.1.1.1, 11.0.0.1?* R3 (10.192–10.255 matches /10), R2, R1, R4.
2. *Why can a link-state router compute loop-free paths while a distance-vector router may temporarily loop?* LS nodes compute on the same, complete map (once LSAs have flooded); DV nodes trust neighbours' summaries computed from stale information, so a neighbour may route back to you (count to infinity).
3. *Why does BGP need TCP while OSPF uses IP directly?* BGP transfers large, incremental tables between peers that may be far apart and needs reliable ordered delivery without its own retransmission logic, so it opens a TCP connection to port 179 (RFC 4271 §3 [S9]); OSPF talks only to adjacent routers, floods with its own acknowledgements and retransmission timer, and rides directly on IP protocol 89, multicasting to 224.0.0.5 and 224.0.0.6 (RFC 2328 Appendix A.1 [S8]).
4. *An AS receives its provider's default route and a peer's routes. May it advertise the peer's routes to the provider?* No (valley-free): the peer's routes would make the AS a free transit for its provider's traffic to the peer. Only own and customer prefixes go to providers and peers.
5. *Two paths to a prefix: via provider with AS_PATH length 2, via customer with length 4. Which is chosen and why?* Customer. Import policy gives the customer route the higher **degree of preference** (RFC 4271 §9.1.1), and tie-breaking on AS_PATH length (§9.1.2.2 a) only ever runs among routes that already tie on that [S9] — so the length is never compared here at all. The business reason is Gao–Rexford's [S27]: a customer pays for the traffic.

## Code

`src/py/subnet.py::ForwardingTable` (LPM lookup, IPv4 and IPv6, `demo_table()` above). Algorithms: `linkstate.py`, `distvector.py`, `pathvector.py` (Gao–Rexford policy class `GaoRexford`, `demo()` builds the four-AS example). Specification-level: `src/py/bgp_decision.py` (RFC 4271 §9.1.1, §9.1.2.2, §10) and `src/py/ospf.py` (RFC 2328 Appendices B and C, §13.1), both covered by `test_rfc_vectors.py`.
