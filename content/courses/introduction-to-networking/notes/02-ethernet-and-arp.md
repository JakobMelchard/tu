# 02 Ethernet and ARP (layer 2)

> **Sourcing.** ARP is RFC 826 [S13], vendored at
> [`../refs/rfc/rfc826.txt`](../refs/rfc/rfc826.txt), and every ARP claim below
> cites it. **Ethernet itself is not an RFC**: the frame format, the 64-byte
> minimum, the interframe gap, CSMA/CD, the 802.1Q tag and STP are IEEE 802.3
> and 802.1Q [S30], which are free to *read* after registering with IEEE and are
> **not** redistributable — so they could not be vendored and the numbers below
> were not checked against the standard's text. They are marked
> *(IEEE, unverified)* where it matters. The IPv6-over-Ethernet glue (EtherType
> 0x86DD, the 33:33 multicast mapping) *is* an RFC, 2464 [S17].

## Ethernet II frame (IEEE 802.3, DIX framing) *(IEEE, unverified [S30])*

| Field | Bytes | Meaning |
|---|---|---|
| Preamble + SFD | 7 + 1 | 10101010… then 10101011: clock sync; not counted in frame length, never seen in captures |
| Destination MAC | 6 | unicast, multicast (I/G bit = LSB of first byte = 1) or broadcast ff:ff:ff:ff:ff:ff |
| Source MAC | 6 | always unicast |
| 802.1Q tag (optional) | 4 | TPID 0x8100, then PCP(3) DEI(1) **VLAN ID (12)** |
| EtherType / Length | 2 | ≥ 0x0600: EtherType (0x0800 IPv4, 0x0806 ARP, 0x86DD IPv6, 0x8100 VLAN); < 0x0600: 802.3 length (LLC follows) |
| Payload | 46–1500 | padded to 46 so the minimum frame is 64 bytes (collision detection on original 10 Mbit/s CSMA/CD needed a frame longer than 2× propagation) |
| FCS | 4 | CRC-32 over dst..payload; bad frames are silently dropped (no L2 retransmission) |

MTU 1500 = maximum payload. Jumbo frames (9000) are a private agreement, not standard. Interframe gap 96 bit times. *(IEEE, unverified [S30].)*

**MAC address** (EUI-48): 48 bits, written `aa:bb:cc:dd:ee:ff`. First 3 bytes OUI (vendor, IEEE assigned), last 3 device. Bit 0 of byte 0: individual/group; bit 1: universally/locally administered (0x02 in `02:00:00:00:00:01` marks the test MACs in the code as locally administered). Scope: **one link**. MACs are not routable and are replaced hop by hop.

## Shared medium vs switched

*(This whole subsection is IEEE 802.3/802.11 material [S30], unverified here.)*

- Classic Ethernet: bus, **CSMA/CD** (listen, send, detect collision, jam, binary exponential backoff $k \in [0, 2^n-1]$ slot times after the $n$th collision, max 10 doubling, 16 attempts). Half duplex.
- Modern Ethernet: point-to-point full-duplex links into a **switch**; no collisions, CSMA/CD disabled. Wi-Fi (802.11) still shares a medium and uses CSMA/**CA** with ACKs because collisions cannot be detected while transmitting.

### Switch (bridge) operation: learning and flooding

A switch keeps a **MAC table** (forwarding database) `MAC → port, age`:

1. Frame arrives on port $p$ with source $S$: learn/refresh `S → p` (backward learning, entries time out after ~300 s).
2. Destination $D$: if in table → forward to that port only (**filter** if it is $p$); else **flood** to all ports except $p$. Broadcast and multicast are always flooded.
3. No modification of the frame (transparent bridging); latency is store-and-forward (whole frame, checks FCS) or cut-through (starts after the dst MAC).

Loops between switches make flooded frames circulate forever (no TTL in Ethernet) and make the MAC table flap: the **Spanning Tree Protocol** (802.1D, RSTP 802.1w) blocks redundant ports so the active topology is a tree rooted at the lowest bridge ID.

**Collision domain** = one shared medium segment (a hub extends it, a switch port ends it). **Broadcast domain** = everything a broadcast reaches (a switch extends it, a router ends it, a VLAN splits it).

### VLANs (802.1Q)

A VLAN partitions one physical switch into several logical broadcast domains. Ports are *access* (untagged, belong to one VLAN) or *trunk* (frames carry the 4-byte tag with the VLAN ID, so several VLANs share one link, e.g. switch-to-switch or switch-to-router). Inter-VLAN traffic must go through a router ("router on a stick": one trunk, one sub-interface per VLAN). Use: separating departments/guest Wi-Fi/management without extra cabling; limiting broadcast (and ARP) traffic.

## ARP: gluing layer 3 to layer 2 (RFC 826 [S13])

Problem: a host knows the next-hop IP (own subnet host, or the default gateway) and must find the MAC to put into the frame.

| Field | Bytes | Request | Reply |
|---|---|---|---|
| HTYPE | 2 | 1 (Ethernet) | 1 |
| PTYPE | 2 | 0x0800 (IPv4) | 0x0800 |
| HLEN, PLEN | 1, 1 | 6, 4 | 6, 4 |
| OPER | 2 | 1 | 2 |
| SHA (sender MAC) | 6 | requester's MAC | **answer**: target's MAC |
| SPA (sender IP) | 4 | requester's IP | target's IP |
| THA (target MAC) | 6 | 00:00:00:00:00:00 (unknown) | requester's MAC |
| TPA (target IP) | 4 | IP being resolved | requester's IP |

28 bytes, padded to 46 in the frame. Request goes to Ethernet broadcast; reply is unicast to the requester. RFC 826's "Generalization" section fixes `<HTYPE, HLEN> = <1, 6>` for Ethernet [S13]. tcpdump prints `ARP, Request who-has 10.0.0.2 tell 10.0.0.1` and `ARP, Reply 10.0.0.2 is-at 02:00:00:00:00:02`.

### What RFC 826 actually says a receiver does

The reception algorithm is worth reading literally, because the usual summary
("only the target learns") is wrong in a way that matters for spoofing. RFC 826,
"Packet Reception" [S13], in order:

1. Set `Merge_flag := false`. **If you already have an entry for the sender's
   protocol address, overwrite its hardware address and set `Merge_flag`.** This
   happens for *every* receiver of the frame, before the opcode is even looked
   at — a broadcast request is therefore processed by everyone on the link.
2. *Only if you are the target*: if `Merge_flag` is false, **add** the sender's
   triplet to the table.
3. *Only then* look at the opcode; if it is a request, swap the fields and reply.

The RFC gives the reason explicitly: "if A has some reason to talk to B, then B
will probably have some reason to talk to A", and "if an entry already exists
for the sender, then the new hardware address supersedes the old one".

So: **everybody updates, only the target adds.** An unsolicited broadcast request
with a forged sender address silently repoints the cache of every host on the
link that already had an entry — no reply needed, no stack quirk needed, that is
the specified behaviour.

**ARP cache** entries expire (Linux: reachable ~30 s then stale, revalidated by
unicast ARP or by upper-layer confirmation — implementation, not RFC 826, which
only says entries should time out). `arp -an` / `ip neigh`.

- **Gratuitous ARP**: request/reply for one's own IP (SPA = TPA). Announces a new MAC (failover, VRRP), detects duplicates (a reply means the address is in use).
- **Proxy ARP**: a router answers for hosts behind it.
- **IPv6** has no ARP: Neighbor Discovery over ICMPv6 with solicited-node multicast, RFC 4861 [S13] (note 04). The IPv6 multicast group is carried to a `33:33`-prefixed Ethernet address by RFC 2464 §7 [S17].

### Why ARP is trivially spoofable

ARP has no authentication. Whether unsolicited *replies* are accepted is stack-dependent, but per the reception algorithm above an unsolicited **request** updates every host that already holds an entry — that is RFC 826 behaviour, not a bug [S13]. **ARP spoofing / poisoning**: attacker sends `10.0.0.1 is-at <attacker MAC>` to the victim and `victim is-at <attacker MAC>` to the gateway → all traffic flows through the attacker (man in the middle), or to a nonexistent MAC (denial of service). Defences: static entries, **Dynamic ARP Inspection** on switches (validate against DHCP snooping table), 802.1X port authentication, and, at the end-to-end level, encryption (TLS) so that being on-path does not reveal or alter content.

Relatedly, **MAC flooding** fills the switch table with fake sources; when full, the switch floods everything like a hub, and the attacker can sniff.

## Worked example: switch learning

Switch S with ports 1–3; hosts A (port 1), B (port 2), C (port 3); table empty.

| Event | Table after | Output ports |
|---|---|---|
| A → B | A:1 | flood: 2, 3 |
| B → A | A:1, B:2 | 1 only |
| C → broadcast | A:1, B:2, C:3 | 1, 2 (broadcast always flooded) |
| A → C | unchanged | 3 |
| Attacker on port 3 sends frame with src = A | **A:3** | subsequent traffic for A goes to port 3 (MAC spoofing) |

Frame count for "A pings B for the first time on an empty network": ARP request (broadcast, flooded; S learns A), ARP reply (unicast to A, S already knows port 1; S learns B), ICMP echo request, ICMP echo reply: 4 frames, of which 1 flooded.

## Pitfalls

- A switch never changes MAC addresses; a router always does (new frame). If a trace shows the same src MAC for packets from many different IPs, that MAC is a router.
- ARP is not "layer 2.5" in any RFC; it is a link-layer helper carried directly in Ethernet (EtherType 0x0806), not inside IP.
- Hosts only ARP for addresses **in their own subnet** (or for the gateway). Wrong subnet mask → ARP for a remote address → no reply → "network unreachable" even though the cable is fine.
- Minimum frame 64 bytes includes FCS but not preamble; a 28-byte ARP packet appears as a 60-byte frame in captures (FCS usually stripped by the NIC) → 18 bytes of padding.
- Ethernet has no acknowledgement or retransmission: loss is handled by TCP.

## Exam-style questions

1. *Which fields of an ARP request are filled in, and to which MAC is it sent?* All except THA (zeros); SHA/SPA are the requester's, TPA the wanted IP; destination MAC broadcast, EtherType 0x0806 [S13].
2. *Two switches connected by two cables, no STP. What happens on the first broadcast?* Both switches flood it out of both inter-switch ports; each copy comes back on the other link and is flooded again; frames multiply without bound (broadcast storm) and the MAC table entry for the source flips between the two ports.
3. *A host has IP 10.0.0.5/24 and gateway 10.0.0.1. It sends to 10.0.0.77 and to 8.8.8.8. For which IP does it ARP in each case?* 10.0.0.77 (same subnet, direct delivery) and 10.0.0.1 (gateway); it never ARPs for 8.8.8.8.
4. *Why does a VLAN reduce ARP traffic?* ARP requests are broadcasts; a VLAN is a broadcast domain, so they reach only members of the same VLAN.
5. *Why can an attacker on the same LAN intercept traffic even though the switch forwards unicast frames only to the owner's port?* By ARP-poisoning the victim's cache the attacker makes the victim address frames to the attacker's MAC; the switch then delivers them correctly, to the attacker.
6. *An attacker broadcasts an ARP **request** for some unused address, with SPA = the gateway's IP and SHA = its own MAC. Nobody replies. Has anything happened?* Yes. RFC 826's reception algorithm merges the sender's mapping into the table of every host that already had an entry for the gateway, before the opcode is examined [S13]. One broadcast frame, no reply, and the whole link's default-gateway mapping is repointed. Only hosts with *no* prior entry are unaffected, since adding a new entry is reserved for the target.

## Code

`src/py/headers.py`: `build_ethernet/parse_ethernet` (VLAN tag skip), `build_arp/parse_arp`, `mac_to_bytes`. `src/py/pcap.py`: `synthetic_trace()` starts with the request/reply pair; `test_headers.py::test_ethernet_arp_roundtrip` checks the exact 42-byte wire image.
