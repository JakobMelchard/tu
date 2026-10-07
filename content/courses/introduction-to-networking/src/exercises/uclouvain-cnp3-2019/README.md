# CNP3 (UCLouvain) — three exercise types, solved

> **This is UCLouvain's material, not 191.030's.** 191.030 is new in 2026W and
> has no past paper, no exercise sheet and no public slide deck [S1], [S2],
> [S5], [S7]. Nothing below was ever set at TU Wien. It is here as a
> **substitute**, and every problem is labelled with where it came from.

## What the source is

| | |
|---|---|
| Work | **Computer Networking: Principles, Protocols and Practice** (CNP3), 3rd edition |
| Author | Olivier Bonaventure |
| Institution | UCLouvain (Université catholique de Louvain), Belgium |
| Exercise set | `exercises/` in the book's repository; the copyright headers on the files used here read **2013, 2019** |
| URLs | <https://github.com/cnp3/ebook> · <https://www.computer-networking.info> |
| Retrieved | 2026-09-22 |
| Licence | **CC BY-SA 3.0 Unported**, stated in the repository `README.md`. The individual exercise files carry a per-file header naming **CC BY 3.0** instead. Both are recorded because they differ; the stricter (BY-SA) is assumed. |
| Register entry | [S35] in [`../../../refs/SOURCES.md`](../../../refs/SOURCES.md) |

## Why this source and not another

Free networking exercises are abundant; ones that match *this* syllabus are
not. CNP3 is the only free, licence-clear set found that treats **inter-domain
routing policy** — customer/peer/provider relationships and valley-free path
selection — as an exercise rather than as prose. 191.030's TISS subject list
names "**link-state and path-vector algorithms**" side by side [S1], which is
unusual for an introductory course and is the thing most substitute material
skips. Kurose–Ross-shaped problem sets and Stanford CS144's labs both stop at
link state and transport.

Its exercise files line up with the syllabus almost file for file:
`lan.rst`, `network.rst`, `ipv6.rst`, `transport.rst`, `tcp.rst`,
`routing-protocols.rst`, **`routing-policies.rst`**, `dns.rst`, `sockets.rst`,
`trace.rst`.

## What it covers that 191.030's TISS topic list also covers

| CNP3 exercise file | 191.030 topic [S1] | our note | solved here? |
|---|---|---|---|
| `network.rst` (flat vs hierarchical addressing, port-forwarding tables) | Foundations, "Routing and Forwarding" | [02](../../../notes/02-ethernet-and-arp.md), [06](../../../notes/06-forwarding-and-routing.md) | **yes** — §1 and §3 below |
| `routing-policies.rst` (inter-domain routing) | "path-vector algorithms" | [06](../../../notes/06-forwarding-and-routing.md), [07](../../../notes/07-link-state-and-path-vector.md) | **yes** — §2 below |
| `lan.rst` (switch address tables) | "Layer 2 (Ethernet…)" | [02](../../../notes/02-ethernet-and-arp.md) | partly — the learning rule, not STP |
| `routing-protocols.rst` (link state, distance vector) | "link-state … algorithms" | [07](../../../notes/07-link-state-and-path-vector.md) | covered by the MIT set instead |
| `ipv6.rst` | "Layer 3 (… IPv6)" | [04](../../../notes/04-ipv6.md) | no — `../../py/subnet.py` already does this |
| `transport.rst`, `tcp.rst`, `tcp-2.rst`, `reliability.rst` | "Layer 4 (TCP/UDP)" | [05](../../../notes/05-udp-and-tcp.md) | covered by the MIT set instead |
| `dns.rst` | "DNS" | [08](../../../notes/08-dns-dnssec-telnet.md) | no — `../../py/dns.py` already does this |
| `sockets.rst` | "Socket programming" | [10](../../../notes/10-protocol-design-and-sockets.md) | no — `../../py/sockets_echo.py` already does this |
| `trace.rst` | the practical part's "describing packet traces" (TISS until 2026-09-2x, removed by 2026-09-27) | [11](../../../notes/11-exercise-playbook.md) | no — `../../py/pcap.py` already does this |

Only three exercise types are solved here, deliberately. Where this tree
already has a better implementation of the same thing, the table says so
instead of duplicating it.

## What it covers that 191.030 does not

- **Spanning Tree Protocol and VLANs** (`lan.rst` is mostly STP). 191.030's
  subject list names neither [S1]. The neighbouring TU Wien course 182.752 does
  teach STP and VLANs [S6], so a Computer Engineering student has met them —
  but they are not examinable here. `LearningSwitchNetwork.has_cycle()` marks
  exactly that boundary: it shows *why* a spanning tree is needed and stops.
- **HTTP, SMTP/e-mail, TLS** (`http.rst`, `email.rst`, `tls.rst`). Not on the
  subject list. Excluded.
- **Congestion control in depth** and `packetdrill`/`ipmininet` lab scripts.

## What 191.030 covers that CNP3 does not

**DNSSEC**, **Telnet**, **multicast routing**, and **Internet governance** —
all four named by TISS [S1], none of them a CNP3 exercise. They are the gap that
[`../../../notes/12-substitute-practice-set.md`](../../../notes/12-substitute-practice-set.md)
fills with problems of our own, checked against the RFCs vendored in
`../../../refs/rfc/`.

## What is in this directory

| file | what |
|---|---|
| `cnp3_exercises.py` | our solutions to three CNP3 exercise types: transparent bridging, valley-free inter-domain path selection, hierarchical vs flat addressing |
| `test_cnp3_exercises.py` | 11 tests |

```sh
# from the course folder
uv run pytest src/exercises -q
uv run python src/exercises/uclouvain-cnp3-2019/cnp3_exercises.py
```

## Vendored or cited?

**Cited, not vendored**, and this one is a judgement rather than a necessity.
CC BY-SA 3.0 clearly permits redistribution with attribution — but ShareAlike
would then attach to anything derived from the copied text, including the
notes, and the book is a live repository that would go stale the moment it was
copied. So the exercise *topologies* are described in our own words (a graph of
AS relationships is a fact, not an expression), no sentence of the book is
reproduced, and the answers are ours.

## The one thing to be careful about

**CNP3 publishes no solutions.** Its multiple-choice and auto-graded questions
(`.. inginious::` directives in the source) run on a UCLouvain INGInious
server; the open questions have no printed answers. So unlike the MIT set in
`../mit-6.02-2012/`, nothing here is checked against an
external answer key. `test_cnp3_exercises.py` checks our answers against the
*mechanism* instead — RFC 826's learn-from-every-frame rule [S13], RFC 4271
§9.1.1's degree of preference acting before §9.1.2.2's tie-breaks [S9], and
Gao & Rexford's export rule [S27].

The headline result worth carrying into an exam: in the CNP3 four-AS topology,
`AS4` reaches `AS1` over **two paths of equal length**, one through its
provider and one through its peer, and the **peer path wins** — because policy
is applied in phase 1 and AS_PATH length is a phase-2 tie-break that is never
reached. That is note 07's correction made concrete.

Source labels refer to [`../../../refs/SOURCES.md`](../../../refs/SOURCES.md).
