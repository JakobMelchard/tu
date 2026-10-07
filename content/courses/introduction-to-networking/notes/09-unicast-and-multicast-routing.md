# 09 Unicast and multicast routing

> **Sourcing.** IPv4 multicast addressing and the Ethernet mapping are RFC 1112,
> IGMPv2 is RFC 2236, IGMPv3 RFC 3376, PIM-SM RFC 7761, the IPv6 mapping RFC
> 2464, inter-domain carriage RFC 4760 — all vendored [S17]. The subject list
> names "Unicast/Multicast Routing" [S1].

## Delivery models

| Model | Destination | Who forwards how |
|---|---|---|
| Unicast | one host | LPM on the destination (notes 06/07) |
| Broadcast | all hosts on a link/subnet | L2 broadcast; routers do not forward it (directed broadcast disabled since Smurf attacks) |
| **Multicast** | a **group** (224.0.0.0/4, ff00::/8): any number of receivers who subscribed | routers build a **distribution tree**; the source sends one copy, routers replicate at branch points |
| Anycast | one of several hosts with the same address | plain unicast routing picks the nearest instance (DNS roots, CDNs) |

Multicast addresses are *logical*: a group has no location, senders need not be members, membership is dynamic (RFC 1112 §4 [S17]). On Ethernet an IPv4 group maps to `01:00:5E` + the **low 23 bits** of the group (RFC 1112 §6.4), so the 28 group bits collide 32-to-1 onto one MAC — the NIC filters coarsely and IP filters exactly. IPv6 maps to `33:33` + the **low 32 bits** (RFC 2464 §7), which for a /64's solicited-node addresses is effectively collision-free. Well-known: 224.0.0.1 all hosts, 224.0.0.2 all routers, 224.0.0.5/6 OSPF, 224.0.0.9 RIPv2, 224.0.0.251 mDNS; 232/8 source-specific, 239/8 administratively scoped (site-local). TTL/scope limits how far a multicast travels.

Why multicast? Sending to $n$ receivers costs the source $n$ unicast copies and the first link $n\times$ the bandwidth; multicast costs one copy per tree edge. Uses: IPTV inside an operator, financial market data, stock exchange feeds, OSPF/RIP/NDP on a link, conference streaming, software distribution. Why not on the public Internet? No inter-domain deployment (state per group in every router, billing, security), so applications use application-layer trees or CDNs instead.

## Group membership: IGMP (IPv4) and MLD (IPv6)

Between hosts and their first-hop router (link-local only, TTL 1):

| IGMPv2 message | Sent by | Meaning |
|---|---|---|
| Membership Query (general to 224.0.0.1, or group-specific) | querier router, every **Query Interval, default 125 s** (RFC 2236 §8.2 [S17]) | who is still interested? |
| Membership Report | host, to the group address | I am in group G (others on the link suppress their duplicate report) |
| Leave Group (to 224.0.0.2) | host | router sends a group-specific query; no report within Last Member Query Interval × Count → prune (RFC 2236 §8.8, §8.9) |

IGMPv3 (RFC 3376 §4.2 [S17]) adds **source filtering**: "join G, only from S" (INCLUDE) or "from anyone except" (EXCLUDE), enabling **SSM** (source-specific multicast, 232/8) where the channel is the pair (S, G) and no rendezvous is needed. MLD is the same over ICMPv6 (types 130–132, 143) *(unsourced: RFC 2710/3810 were not fetched in this pass; IGMP was, and MLD is a transcription of it)*. **IGMP snooping** lets a switch forward group traffic only to ports that reported; otherwise multicast is flooded like broadcast within the VLAN.

## Building the tree: reverse path forwarding

Routers must forward a multicast packet away from the source without loops and without state per receiver. **RPF check** (RFC 7761 §4.5 [S17]): accept a packet from source $S$ only if it arrives on the interface that the *unicast* table uses to reach $S$ (the shortest path back). "Protocol independent" means exactly this: PIM has no topology database of its own, it reuses whichever unicast table is there. Forward it out of all other interfaces (flooding) — this yields the **reverse shortest-path tree** rooted at $S$, loop-free by construction. **Pruning** removes branches with no members (leaf routers with no IGMP state send Prune upstream); prunes time out, so periodic re-flooding happens (**flood and prune**). **Grafts** re-attach a branch when a member joins.

| Tree | Rooted at | Per-router state | Path quality | Good for |
|---|---|---|---|---|
| **Source tree** (S, G), shortest-path tree | the source | one entry per (source, group) | optimal from that source | few sources, many receivers (IPTV) |
| **Shared tree** (*, G) | a **rendezvous point** (RP) | one entry per group | suboptimal (via RP) | many sparse sources (conferencing) |

## Protocols

- **DVMRP** (RFC 1075, historic) and **MOSPF** (RFC 1584): multicast extensions of RIP and OSPF, DVMRP with its own DV unicast table for RPF, MOSPF computing source trees from the link-state database. Both dense-mode, flood-and-prune.
- **PIM** (Protocol Independent Multicast): uses whatever unicast routing table exists for RPF, hence "independent".
  - **PIM-DM** (dense): flood and prune; assumes receivers everywhere (campus).
  - **PIM-SM** (sparse, RFC 7761 §3.1–3.4 [S17]): explicit **Join** messages travel from the receiver's router toward the RP (shared tree (*, G)). Sources **register** with the RP (first packets unicast-encapsulated in Register messages); the RP joins the source tree toward S, forwards down the shared tree, and returns Register-Stop. Once traffic flows natively the last-hop router may **switch over** to the (S, G) shortest-path tree, then send an (S, G, rpt) Prune up the shared tree. RP discovery: static, BSR, or Auto-RP; **anycast RP** for redundancy.
  - **PIM-SSM**: only (S, G) joins; receivers learn S out of band (SDP, web page); no RP, no register, simplest and what modern deployments use; **Bidir-PIM** for many-to-many.
- Inter-domain: **MBGP** (multiprotocol BGP, RFC 4760 §3 [S17]) carries a separate address family whose routes are used for the RPF lookup rather than for forwarding; **MSDP** connects RPs of different domains (IPv4 ASM only) *(unsourced: RFC 3618 not fetched)*. Deployment is small.

## Worked example: PIM-SM join and switchover

Topology: S — R1 — R2 — RP — R3 — H (a receiver); also a direct link R1 — R3. Unicast costs 1 per link.

1. H sends IGMP Report for G. R3 (designated router) creates (*, G) state and sends PIM Join toward the RP (RPF interface for RP); RP records outgoing interface toward R3. Shared tree: RP → R3 → H.
2. S starts sending. R1 encapsulates packets in **Register** unicast to the RP. RP decapsulates, forwards down the shared tree, and sends an (S, G) Join toward S (R2, R1) so native packets flow S → R1 → R2 → RP → R3 → H; RP then sends Register-Stop to R1.
3. R3 sees traffic from S at a rate above the threshold, computes the RPF interface toward S: the direct link R1–R3 (cost 1 vs 3 via RP). It sends an (S, G) Join to R1 directly and, once packets arrive on the new path, an (S, G, RPT-bit) Prune up the shared tree so RP stops forwarding S's traffic to it. Final path S → R1 → R3 → H: two hops instead of four.
4. H leaves: IGMP Leave, group-specific Query, no Report → R3 sends Prune for (S, G) and (*, G); state times out upstream.

Forwarding state at R1 at the end: (S, G) incoming = link to S (RPF), outgoing = {link to R3}; the RP's (*, G) has an empty outgoing list and is deleted after its timer.

## Pitfalls

- Multicast forwarding is keyed on the *source* (RPF) as much as on the destination group; unicast never looks at the source.
- A host joins a group by telling its router (IGMP), not the sender; the sender learns nothing about members.
- Multicast traffic does not cross a router unless multicast routing is configured; link-local (224.0.0.x) never does.
- IGMP is not a routing protocol; PIM is not a membership protocol.
- Multicast means one packet per link on the tree, so the *source's* uplink carries one copy — but a switch without IGMP snooping floods it to every port in the VLAN.
- UDP only: no TCP multicast (no per-receiver ACK/window makes sense); reliability, if any, is application level (NACK-based, FEC).

## Exam-style questions

1. *A source sends 4 Mbit/s to 100 receivers in 10 sites, 10 per site, over a hub-and-spoke WAN. Uplink load at the source for unicast vs. multicast?* Unicast 400 Mbit/s; multicast 4 Mbit/s (one copy; replication at the hub, then in each site's switch).
2. *What is the RPF check and why does it prevent loops?* Accept from S only on the interface used to reach S by unicast; each router then has exactly one accepting interface per source, so the accepted packets form a tree (the reverse shortest-path tree) and a copy that returns via another interface is dropped.
3. *Compare the state a router holds for a shared tree and a source tree with 50 sources sending to one group.* Shared: one (*, G) entry. Source trees: 50 (S, G) entries. Price of the shared tree: traffic detours via the RP and the RP is a single point of failure/concentration.
4. *Which Ethernet MAC does 224.1.2.3 map to, and which other groups collide with it?* `01:00:5e:01:02:03` — RFC 1112 §6.4 copies the **low 23 bits** [S17], and 224.1.2.3's low 23 bits are 0x010203. The 28 group-address bits therefore collide 32-to-1: every group differing only in the 5 bits above the low 23 maps to the same MAC (224.129.2.3, 225.1.2.3, …, 239.129.2.3). A host must still filter in IP, because its NIC will deliver all 32.
5. *Why is SSM easier to deploy than ASM?* No RP, no Register/MSDP, no source discovery in the network (receivers name the source), (S, G) state only where there are receivers, and the source is implicitly authorised (a rogue sender to (S', G) is a different channel).

## Code

No dedicated module: RPF reduces to the unicast table (`src/py/linkstate.py::routing_table` gives the RPF interface for every source). `test_linkstate.py` style trees can be derived with `path()` from each receiver toward the source. Group → MAC mapping: `src/py/subnet.py::multicast_mac` (RFC 1112 §6.4 for IPv4, RFC 2464 §7 for IPv6); `test_subnet.py::test_solicited_node_and_multicast_mac` constructs the 32 groups that share `01:00:5e:00:00:05`.
