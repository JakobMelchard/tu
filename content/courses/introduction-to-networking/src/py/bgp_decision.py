"""BGP-4 decision process and timer defaults, exactly as RFC 4271 writes them
(notes 06 and 07).

`pathvector.py` runs the *protocol* (UPDATE exchange, withdrawals, AS-path loop
rejection, Gao-Rexford policy).  This module is the *specification*: the phase-1
degree of preference (RFC 4271 section 9.1.1), the phase-2 tie-breaking sequence
(section 9.1.2.2) in the order the RFC mandates, and the suggested default timer
values (section 10).

Two things worth knowing before an exam, because every vendor cheat sheet blurs
them:

* The RFC's tie-break list has seven steps and **LOCAL_PREF is not one of them**.
  LOCAL_PREF is phase 1: it sets the *degree of preference*, and tie-breaking
  only ever runs among routes that already tie on that.  That is why "highest
  LOCAL_PREF first" is right in substance but is not step 1 of section 9.1.2.2.
* "Oldest route wins" and "lowest router ID" are often quoted together.  Only
  the second is in RFC 4271 (step f, lowest BGP Identifier).  Preferring the
  older route is a vendor addition for stability and is not in the RFC.
"""
from dataclasses import dataclass, field

# RFC 4271 section 10 -- "suggested default value" for every timer.  These are
# suggestions, not requirements: only HoldTime MUST be configurable per peer.
TIMERS = {
    "ConnectRetryTime": 120.0,                    # section 10
    "HoldTime": 90.0,                             # section 10
    "HoldTime_large": 240.0,                      # 4 minutes, used in parts of the FSM
    "KeepaliveTime": 90.0 / 3,                    # section 10: 1/3 of HoldTime -> 30 s
    "MinASOriginationIntervalTimer": 15.0,        # section 10 / 9.2.1.2
    "MinRouteAdvertisementIntervalTimer_eBGP": 30.0,   # section 10 / 9.2.1.1
    "MinRouteAdvertisementIntervalTimer_iBGP": 5.0,    # section 10 / 9.2.1.1
}
JITTER_RANGE = (0.75, 1.0)   # section 10: multiply the base value by U(0.75, 1.0)
PORT = 179                   # section 3 / 8.2.2: BGP listens on TCP port 179

ORIGIN = {"IGP": 0, "EGP": 1, "INCOMPLETE": 2}   # section 4.3, lowest is best


@dataclass
class Route:
    """One entry of an Adj-RIB-In."""
    prefix: str
    as_path: tuple = ()
    next_hop: str = ""
    origin: str = "IGP"
    med: int | None = None          # MULTI_EXIT_DISC; absent counts as 0 (9.1.2.2 c)
    local_pref: int | None = None   # only meaningful on iBGP-learnt routes (9.1.1)
    from_ebgp: bool = True
    peer_address: str = ""
    bgp_identifier: str = ""
    neighbor_as: int | None = None  # the AS the route was received from
    igp_cost: float | None = None   # interior distance to next_hop
    policy_pref: int | None = None  # what local import policy assigns to eBGP routes
    notes: list = field(default_factory=list)

    def as_path_length(self):
        """Section 9.1.2.2 a: the number of AS numbers in AS_PATH, where an
        AS_SET counts as 1 however many ASes it holds -- which is exactly the
        length of the tuple when a set is stored as one element."""
        return len(self.as_path)


def degree_of_preference(route):
    """RFC 4271 section 9.1.1.  For an internal peer the LOCAL_PREF attribute is
    the degree of preference; for an external peer the local system computes it
    from preconfigured policy (here `policy_pref`, which is what an
    implementation would then re-advertise as LOCAL_PREF into iBGP)."""
    if route.from_ebgp:
        if route.policy_pref is None:
            raise ValueError("eBGP route needs an import-policy preference (9.1.1)")
        return route.policy_pref
    if route.local_pref is None:
        raise ValueError("iBGP route without LOCAL_PREF (9.1.1)")
    return route.local_pref


def _ip_key(addr):
    return tuple(int(p) for p in addr.split(".")) if addr else ()


# Section 9.1.2.2, in the mandated order.  Each entry is (label, key function);
# the route with the *smallest* key survives the step.
TIE_BREAKS = [
    ("a: shortest AS_PATH", lambda r: r.as_path_length()),
    ("b: lowest ORIGIN", lambda r: ORIGIN[r.origin]),
    # c is handled separately: MED is only comparable within one neighbouring AS.
    ("d: eBGP over iBGP", lambda r: 0 if r.from_ebgp else 1),
    ("e: lowest interior cost to NEXT_HOP", lambda r: (r.igp_cost if r.igp_cost is not None else 0)),
    ("f: lowest BGP Identifier", lambda r: _ip_key(r.bgp_identifier)),
    ("g: lowest peer address", lambda r: _ip_key(r.peer_address)),
]


def _filter_med(routes, log):
    """Step c.  MED is comparable only between routes learnt from the same
    neighbouring AS; a route without MED is treated as MED 0."""
    survivors = list(routes)
    for m in list(survivors):
        for n in survivors:
            if m is n or m.neighbor_as != n.neighbor_as:
                continue
            if (n.med or 0) < (m.med or 0) and m in survivors:
                survivors.remove(m)
                log.append(f"c: lowest MED within AS {m.neighbor_as} drops {m.as_path}")
                break
    return survivors


def select(routes, trace=None):
    """Run the full decision process over one prefix's eligible routes and
    return the single best one.  `trace` collects the step that eliminated
    each candidate, which is what an exam answer has to show."""
    log = trace if trace is not None else []
    if not routes:
        return None
    best_pref = max(degree_of_preference(r) for r in routes)
    cands = [r for r in routes if degree_of_preference(r) == best_pref]
    log.append(f"phase 1 (9.1.1): highest degree of preference = {best_pref}, "
               f"{len(cands)} of {len(routes)} routes remain")
    if len(cands) == 1:
        return cands[0]
    for label, key in TIE_BREAKS:
        if label.startswith("d"):          # step c sits between b and d
            cands = _filter_med(cands, log)
            if len(cands) == 1:
                break
        best = min(key(r) for r in cands)
        kept = [r for r in cands if key(r) == best]
        if len(kept) < len(cands):
            log.append(f"{label}: {len(cands)} -> {len(kept)}")
        cands = kept
        if len(cands) == 1:
            break
    return cands[0]


def keepalive_for(hold_time):
    """Section 4.4 / 10: KeepaliveTime is 1/3 of the negotiated HoldTime; a
    HoldTime of 0 disables both KEEPALIVEs and the hold timer."""
    return 0.0 if hold_time == 0 else hold_time / 3


def demo():
    common = dict(prefix="192.0.2.0/24", origin="IGP", neighbor_as=None)
    # Two routes for the same prefix: a long one from a customer, a short one
    # from a peer.  Import policy prefers customers, so the long path wins --
    # and tie-breaking never runs, because the degrees of preference differ.
    customer = Route(**common, as_path=(65001, 65009, 65009, 65009), policy_pref=100,
                     next_hop="198.51.100.1", peer_address="198.51.100.1",
                     bgp_identifier="10.0.0.1", igp_cost=10)
    peer = Route(**common, as_path=(65002, 65009), policy_pref=80,
                 next_hop="198.51.100.5", peer_address="198.51.100.5",
                 bgp_identifier="10.0.0.2", igp_cost=1)
    trace = []
    best = select([customer, peer], trace)
    print("== policy beats path length ==")
    for line in trace:
        print("  " + line)
    print(f"  best: AS_PATH {best.as_path} via {best.next_hop}\n")

    # Same preference: now the RFC's seven steps decide, and step (a) is enough.
    a = Route(**common, as_path=(65002, 65009), policy_pref=100, peer_address="198.51.100.5",
              bgp_identifier="10.0.0.2", igp_cost=1)
    b = Route(**common, as_path=(65003, 65004, 65009), policy_pref=100,
              peer_address="198.51.100.9", bgp_identifier="10.0.0.3", igp_cost=1)
    trace = []
    best = select([a, b], trace)
    print("== equal preference, tie-break 9.1.2.2 ==")
    for line in trace:
        print("  " + line)
    print(f"  best: AS_PATH {best.as_path}\n")

    print("== RFC 4271 section 10 suggested defaults ==")
    for k, v in TIMERS.items():
        print(f"  {k:<42} {v:g} s")
    print(f"  jitter: base x U{JITTER_RANGE}, new draw each time a timer is set")


if __name__ == "__main__":
    demo()
