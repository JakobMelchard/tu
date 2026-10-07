# 07 Link-state and path-vector algorithms (with Bellman-Ford for contrast)

> **Sourcing.** This is the note the source pass changed most. OSPF is RFC 2328
> [S8] and BGP is RFC 4271 [S9], both vendored; **the timers and the decision
> process below were previously stated from memory and are now quoted by
> section, with the two places where the folklore is wrong flagged in bold.**
> The topic list names "Link State and Path-Vector Routing Algorithms"
> explicitly [S1], so this note is core. Distance vector is *not* on that list
> and is kept only as the contrast that makes path vector make sense.

## Dijkstra (link-state computation)

Given the graph $G=(V,E)$ with costs $c(u,v) \ge 0$ and source $s$: maintain the set $N'$ of settled nodes, tentative distance $D(v)$ and predecessor $p(v)$.

1. $N' = \{s\}$; for all $v$: $D(v) = c(s,v)$ if adjacent else $\infty$, $p(v) = s$.
2. Repeat until $N' = V$: pick $w \notin N'$ with minimal $D(w)$; add to $N'$; for every neighbour $v \notin N'$ of $w$: $D(v) \leftarrow \min(D(v),\, D(w) + c(w,v))$, update $p(v)$ on improvement.

Correctness: when $w$ is settled, $D(w)$ is final because any other path would have to leave $N'$ through a node with a larger tentative distance (needs non-negative costs). Complexity $O(|V|^2)$ naive, $O(|E| \log |V|)$ with a heap. The routing table needs only the **first hop**: follow $p(\cdot)$ back to a neighbour of $s$.

### Worked example (Kurose–Ross topology, `linkstate.EXAMPLE`)

Edges: u–v 2, u–x 1, u–w 5, v–x 2, v–w 3, x–w 3, x–y 1, w–y 1, w–z 5, y–z 2. Source u. Entries are $D(v),p(v)$:

| Step | $N'$ | v | w | x | y | z |
|---|---|---|---|---|---|---|
| 0 | u | 2,u | 5,u | **1,u** | ∞ | ∞ |
| 1 | ux | **2,u** | 4,x | | 2,x | ∞ |
| 2 | uxv | | 4,x | | **2,x** | ∞ |
| 3 | uxvy | | **3,y** | | | 4,y |
| 4 | uxvyw | | | | | **4,y** |
| 5 | uxvywz | | | | | |

(Ties, here v and y both at 2, may be broken either way.) Shortest-path tree: u→v, u→x, x→y, y→w, y→z. **Forwarding table at u**:

| Dest | Next hop | Cost |
|---|---|---|
| v | v | 2 |
| x | x | 1 |
| y | x | 2 |
| w | x | 3 |
| z | x | 4 |

Notice that the direct link u–w (cost 5) is not used and that four of five destinations share the first hop x: a real router's FIB is then two entries plus a default.

### OSPF (RFC 2328 = STD 54 [S8])

Each router discovers neighbours with **Hello** packets, forms adjacencies, and
floods **link-state advertisements** (LSAs: its links and their costs, with
sequence numbers and ages) reliably to every router in the **area**; everyone
holds the identical **link-state database** and runs Dijkstra from itself
(§16.1). On a broadcast LAN a **designated router** is elected (§9.4) so that
$n$ routers form $O(n)$ adjacencies instead of $n^2/2$. **Areas** (backbone
area 0 plus stubs) limit flooding and database size; area border routers inject
summaries. Equal-cost paths are all used (ECMP). Authentication is per link.
IS-IS is the same idea with a different encoding, favoured by large ISPs.

Encapsulation, RFC 2328 Appendix A.1: **IP protocol 89**, multicast to
`AllSPFRouters` **224.0.0.5** and, for DR/BDR traffic, `AllDRouters`
**224.0.0.6**. Both are inside 224.0.0.0/24, which routers never forward — OSPF
never leaves the link.

#### The timers, quoted, because the usual summary is subtly wrong

RFC 2328 splits its constants in two, and the split is the whole point.

**Appendix B, architectural constants — fixed, not configurable by anyone:**

| constant | value | what it does |
|---|---|---|
| LSRefreshTime | **30 min** | re-originate a self-originated LSA even if nothing changed |
| MinLSInterval | **5 s** | minimum between two originations of the same LSA |
| MinLSArrival | **1 s** | LSAs arriving faster than this are discarded |
| MaxAge | **1 h** | at this age an LSA is reflooded to flush it, and is excluded from the routing calculation |
| CheckAge | **5 min** | re-verify an LSA's checksum in the database |
| MaxAgeDiff | **15 min** | ages differing by less than this count as the *same* instance |
| LSInfinity | **0xffffff** | "unreachable" in summary and AS-external LSAs |
| InitialSequenceNumber | **0x80000001** | signed 32-bit, so this is the *most negative* value |
| MaxSequenceNumber | **0x7fffffff** | |

**Appendix C.3, configurable per interface — and these are the RFC's own
*sample* values, not defaults. RFC 2328 states no default for either.**

| parameter | what the RFC literally says |
|---|---|
| HelloInterval | "Sample value for a X.25 PDN network: 30 seconds. Sample value for a local area network: **10 seconds**." |
| RouterDeadInterval | "This should be some multiple of the HelloInterval (**say 4**)." No number is given. |
| RxmtInterval | "Sample value for a local area network: 5 seconds." |
| InfTransDelay | "Sample value for a local area network: 1 second." Must be > 0. |
| Interface output cost | "must always be greater than 0". **That is all.** |

So: **the familiar 10 s / 40 s pair is Appendix C.3's LAN sample times its
suggested factor of four** — a reading of the RFC that every implementation
happens to ship, not a value the RFC mandates. And **the $10^8/\text{bandwidth}$
cost formula is not in RFC 2328 at all**; the word "bandwidth" appears once in
the entire document, in an unrelated sentence about routing overhead. The
reference-bandwidth rule is a Cisco default that other vendors copied.
*(unsourced: vendor documentation, not fetched in this pass.)*

What the RFC *does* make mandatory is agreement: §10.5 says a received Hello is
only accepted if its network mask, HelloInterval and RouterDeadInterval match
the receiving interface's. Mismatch them and the adjacency silently never forms
— a classic "the cable is fine and nothing works" fault.
`ospf.adjacency_possible` reproduces that check.

#### Which copy of an LSA wins (§13.1)

Every router must answer this identically or flooding loops. Compare, in order:
**LS sequence number** (signed, so 0x80000001 is the smallest), then **LS
checksum** (larger wins), then: if exactly one is at MaxAge, *that* one is newer
(it is a flush); then, if the ages differ by more than MaxAgeDiff, the younger
wins; otherwise the two are the *same instance*. `ospf.which_is_newer` and
`ospf.install` implement it, and `test_rfc_vectors.py` walks every branch.

Convergence: detect failure (RouterDeadInterval, so ~40 s with the sample
values, or BFD in milliseconds) → flood → recompute (ms) → loop-free once every
router has the new LSA; transient micro-loops exist while LSAs are in flight.

## Bellman-Ford (distance vector)

Every node $x$ keeps $D_x(y)$ for all destinations $y$ and the vectors received from neighbours. Update rule (Bellman equation):

$$D_x(y) = \min_{v \in N(x)} \big[\, c(x,v) + D_v(y) \,\big]$$

Asynchronous, iterative, distributed: on a link-cost change or a received vector, recompute; if own vector changed, send it to neighbours. Converges to the true shortest paths in at most $|V| - 1$ rounds (each round extends correct paths by one hop) for a stable graph. Only neighbours' vectors are needed, no global view. RIP: hop count, infinity = 16, updates every 30 s, hold-down timers *(unsourced: RFC 2453 was not fetched in this pass; distance vector is not on the official topic list [S1] and is kept here only as contrast)*.

### Count to infinity (the DV failure mode)

Chain A–B–C, all costs 1. Converged: $D_B(A) = 1$, $D_C(A) = 2$ (via B). Link A–B fails.

| Round | $D_B(A)$ | $D_C(A)$ | Why |
|---|---|---|---|
| 0 | 3 | 2 | B lost its direct route; C's last vector says $D_C(A) = 2$, so B computes $1 + 2 = 3$ via C — but C's route goes through B |
| 1 | 3 | 4 | C hears $D_B(A) = 3$: $1 + 3 = 4$ |
| 2 | 5 | 4 | B: $1 + 4$ |
| … | … | … | +2 every two rounds |
| 14 | 16 | 16 | reached infinity, A finally declared unreachable |

Packets to A loop between B and C the whole time. Good news travels fast (one round per hop), bad news slowly.

Fixes: **split horizon** — do not advertise a route to the neighbour you learnt it from; **poisoned reverse** — advertise it with cost ∞ instead (explicit, faster than silence). Both kill the 2-node loop (C tells B ∞ for A, so B goes to ∞ in round 0); neither fixes loops through three or more nodes. **Hold-down** timers and **triggered updates** reduce the damage; **route poisoning** (advertise ∞ immediately on failure) speeds the bad news. Fundamentally the problem is that a DV router cannot tell whether a neighbour's route runs through itself; path vector fixes exactly that by carrying the path.

`distvector.count_to_infinity_demo()` prints the table above and the poisoned-reverse variant (converges in 2 rounds).

## Path vector: BGP best-path selection (RFC 4271 §9.1 [S9])

Each UPDATE carries the full AS_PATH. Receiving a route with your own AS number
in the path ⇒ discard (§5.1.2 loop detection). Then, per prefix, the **decision
process** picks one best route. The RFC organises it in two phases, and the
popular seven-line summary flattens them in a way that produces wrong answers.

**Phase 1 (§9.1.1) — degree of preference.** For a route learnt from an
*internal* peer, the degree of preference **is** the LOCAL_PREF attribute. For a
route learnt from an *external* peer, the local system computes it from
preconfigured policy, and that value MUST then be used as LOCAL_PREF when the
route is re-advertised into iBGP. Phase 2 considers only the routes with the
highest degree of preference.

**Phase 2 (§9.1.2.2) — breaking ties, in the mandated order.** "The criteria
MUST be applied in the order specified", and the algorithm stops as soon as one
route remains:

| RFC step | criterion | notes |
|---|---|---|
| a | shortest **AS_PATH** | "an AS_SET counts as 1, no matter how many ASes are in the set"; prepending inflates the count on purpose |
| b | lowest **ORIGIN** | IGP (0) < EGP (1) < INCOMPLETE (2) |
| c | lowest **MED** | **only comparable between routes learnt from the same neighbouring AS**; a route with no MED counts as MED 0 |
| d | **eBGP over iBGP** | if any candidate came from eBGP, drop every iBGP one |
| e | lowest **interior cost to NEXT_HOP** | hot potato; skipped if no cost can be determined |
| f | lowest **BGP Identifier** (router ID) | |
| g | lowest **peer address** | the final, always-decisive tie-break |

**Two corrections to the folklore, both now checkable against the vendored text:**

1. **LOCAL_PREF is not step 1 of the tie-break** — it is not in §9.1.2.2 at all.
   It is phase 1. In substance "highest LOCAL_PREF first" is right, but the
   distinction matters whenever a question asks *which criterion decided*: if
   the degrees of preference differ, AS_PATH length is never examined.
2. **"Oldest route wins" is not in RFC 4271.** The RFC goes straight from
   interior cost (e) to lowest BGP Identifier (f) to lowest peer address (g).
   Preferring the older route is a vendor addition for stability; the note
   previously listed it as though it were part of the standard.

Only the best route is used for forwarding and re-advertised, after export
policy (§9.1.3). Convergence is not shortest-path convergence: policies can be
**unstable** (the "bad gadget": three ASes each preferring the route through the
next one never settle — Griffin & Wilfong [S28], not in any RFC). Gao–Rexford
relationships [S27] guarantee convergence in practice. `bgp_decision.select()`
implements phase 1 and all seven steps and logs which one eliminated what.

### Worked run (`pathvector.demo()`): four ASes

Links 1–2, 1–3, 2–3, 2–4, 3–4. Relations: 1 is customer of 2 and 3; 2 and 3 are customers of 4; 2–3 peer. Prefixes p1 at AS 1, p4 at AS 4. Rounds of synchronous UPDATE exchange:

| Round | Who learns what |
|---|---|
| 1 | 2 and 3 learn p1 via customer 1 `(2,1)`, `(3,1)`; 2 and 3 learn p4 via provider 4 `(2,4)`, `(3,4)` |
| 2 | 4 learns p1 from both customers `(4,2,1)` and `(4,3,1)` → picks one by tie-break; 1 learns p4 from both providers `(1,2,4)`, `(1,3,4)`. 2 gets `(3,1)` from peer 3 for p1 but prefers its own customer route. **2 does not get p4 from 3**: a provider route is not exported to a peer (valley-free) |
| 3 | 1 receives `(2,1)` and `(3,1)` for its own prefix p1 → loop, rejected; 2 receives `(4,2,1)` → loop, rejected. Nothing changes → converged |

Final: AS 4 reaches p1 through a customer (it earns money either way), AS 1 reaches p4 through one of its providers, and no AS transits traffic for free. Removing a link triggers withdrawals; `test_pathvector.py::test_withdrawal_after_link_failure_reconverges` shows `(1,3)` being replaced by `(1,2,3)`.

**Path exploration**: after a withdrawal, BGP may successively try longer and longer stale paths before giving up (the path-vector cousin of count to infinity, bounded by path length rather than by an "infinity" constant). The **MRAI** timer rate-limits it: RFC 4271 §10 suggests **30 s between two UPDATEs about the same destination to the same external peer, but only 5 s to an internal one** [S9] — §9.2.1.1 requires the internal value to be the shorter, "since fast convergence is needed within an autonomous system". Route-flap damping trades convergence time for stability on top of that. All of RFC 4271 §10's timers, including the jitter rule (multiply by a fresh draw from U(0.75, 1.0) each time a timer is set), are in `bgp_decision.TIMERS`.

## LS vs. DV vs. PV, summary

| | Link state | Distance vector | Path vector |
|---|---|---|---|
| Knowledge | complete map | neighbours' distances | neighbours' paths |
| Loop freedom | after sync, by construction | no (count to infinity) | yes, by path inspection |
| Metric | additive cost, optimal | additive cost, optimal | policy; not optimal |
| Cost of a change | flood to all + recompute | ripple through neighbours | ripple, re-evaluate policy |
| Scale | one area: hundreds of routers | tens | the Internet (~1M prefixes) |
| Protocols | OSPF, IS-IS | RIP | BGP |

## Pitfalls

- Dijkstra settles nodes in order of distance; the tabular exam answer must add exactly one node per row and only relax neighbours of the newly settled node.
- The routing table stores next hops, not full paths (only BGP stores paths, and only for loop detection/policy).
- Bellman-Ford converges; "count to infinity" is the *transient* after a cost *increase*. Cost decreases propagate cleanly.
- Poisoned reverse does not fix 3-node loops: A–B–C–A triangle with a failure elsewhere can still count up.
- BGP "shortest AS path" is a tie-breaker after LOCAL_PREF; a 2-hop path can lose to a 5-hop path.
- An AS path length counts ASes, not routers; one AS may be 20 router hops.

## Exam-style questions

1. *Run Dijkstra from z on the example graph. Give the table at z.* Distances: y 2, w 5 (direct) vs y→w 2+1 = 3 → 3; x 3 (y→x); v 5 (x→v 3+2 or w→v 3+3); u 4 (x→u). Table: y→y 2, w→y 3, x→y 3, u→y 4, v→y 5.
2. *In the chain A–B–C, A–B fails, poisoned reverse enabled. Show two rounds.* Round 0: C's vector to B says A: ∞ (C's route to A goes via B) → $D_B(A) = \infty$; $D_C(A)$ still 2. Round 1: B advertises A: ∞ → $D_C(A) = \infty$. Converged in 2 rounds instead of 14.
3. *Why does an OSPF router on a LAN with 6 routers form only 2 full adjacencies (or 1)?* DR/BDR election (RFC 2328 §9.4 [S8]): all routers synchronise with the DR and BDR only, so flooding is $O(n)$ instead of $O(n^2)$; the DR/BDR themselves adjoin everyone. Traffic to the DR/BDR goes to 224.0.0.6, everything else to 224.0.0.5 (Appendix A.1).
4. *AS X receives a route for P from provider A (path length 2) and customer B (length 3). Which does it choose, and to whom does it export it?* Customer B. Its import policy gives the customer route the higher degree of preference (RFC 4271 §9.1.1), so phase 2 never runs and the path lengths are irrelevant [S9]. It exports the route to all neighbours, including provider A, because customer routes may go anywhere [S27].
5. *An LSA from router R claims a link R–S with cost 1 that does not exist. Which routers are affected and how does this differ from a lying DV router?* Every router in the area computes paths through the fake link, but only paths that would use it; the damage is bounded by that one edge and disappears when the LSA ages out or S's LSA contradicts it. A lying DV router advertising cost 0 to everything attracts *all* traffic and its lie is re-advertised by neighbours as their own distances (no provenance).
6. *Give the RFC-defined default Hello and Dead intervals for OSPF, and the default BGP hold time.* A trick question, and worth getting right: **RFC 2328 defines neither**. Appendix C.3 gives HelloInterval a LAN *sample* of 10 s and says RouterDeadInterval "should be some multiple of the HelloInterval (say 4)"; every implementation reads that as 10/40 [S8]. RFC 4271, by contrast, *does* state suggested defaults in §10: HoldTime **90 s**, KeepaliveTime = HoldTime/3 = **30 s**, ConnectRetryTime **120 s**, all jittered [S9]. The asymmetry — one protocol declining to specify, the other specifying and calling them suggestions — is itself a good short answer.
7. *Two copies of the same router-LSA arrive: one with LS sequence 0x80000003 and LS age 5, one with 0x80000003, the same checksum and LS age 700. Which does a router keep?* Neither — RFC 2328 §13.1 [S8] compares sequence, then checksum, then the MaxAge rules, then whether the ages differ by **more than MaxAgeDiff = 15 minutes**. 695 s is less than 900 s, so the two count as the *same instance*: the second is discarded without reflooding and the database is unchanged. Had the older copy been at MaxAge (3600) it would have won outright, because a MaxAge instance is a flush.

## Code

`src/py/linkstate.py`: `dijkstra`, `dijkstra_trace` (the table above), `routing_table`; test cross-checks `networkx`. `src/py/distvector.py`: `DVNetwork` with `split_horizon`/`poison_reverse`, `count_to_infinity_demo`; test cross-checks networkx's Bellman-Ford. `src/py/pathvector.py`: `PathVectorNetwork.step()` (UPDATE exchange with withdrawal), `GaoRexford` policy (`rank`, `export`), loop rejection (RFC 4271 §9.1.2) logged in `net.log`; with `ShortestPath` the test checks hop counts against networkx. `src/py/ospf.py`: RFC 2328 Appendix B and C constants, `hello_dead_pair`, `adjacency_possible` (§10.5), `which_is_newer`/`install` (§13.1). `src/py/bgp_decision.py`: RFC 4271 §9.1.1 `degree_of_preference`, §9.1.2.2 `TIE_BREAKS` and `select`, §10 `TIMERS`. Both are exercised section by section in `src/py/test_rfc_vectors.py`.
