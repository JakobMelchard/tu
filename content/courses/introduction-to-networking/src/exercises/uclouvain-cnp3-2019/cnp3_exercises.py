"""Solutions to three exercise *types* from **Computer Networking: Principles,
Protocols and Practice** (CNP3), 3rd edition, Olivier Bonaventure, UCLouvain,
**CC BY-SA 3.0** (per-file headers say CC BY 3.0) [S35].

This is **not** 191.030 material.  191.030 is new in 2026W and has no past
paper or exercise sheet [S2].  CNP3 is an open textbook from another
university, chosen because its exercise set is the closest free one to this
course's TISS topic list — in particular it is the only free source found that
treats **inter-domain routing policy** (path vector) as an exercise rather
than as prose, and 191.030 names path vector explicitly [S1].

CNP3 publishes **no solutions** (its auto-graded questions live on an
INGInious server).  So nothing here is checked against an external answer key:
the exercises are restated in our own words from the topology and the
question, and the answers below are **ours**, argued in `README.md` and
cross-checked against the vendored RFCs where one applies.

Run `python3 cnp3_exercises.py` for a demo.
"""
import ipaddress

# ==========================================================================
# 1. Transparent bridging: what a switch learns, and why a cycle is fatal
#    CNP3 "Building a network" open questions 2-3 (flat addresses, port
#    forwarding tables) and "Local Area Networks" exercises 1-2.
#    TISS topic: Layer 2 (Ethernet), note 02.
# ==========================================================================
#
# Restated topology (CNP3's figure, described rather than copied): three
# switches in a line, host A on the first, hosts B and C on the third.
LINE_TOPOLOGY = [("A", "S1"), ("S1", "S2"), ("S2", "S3"), ("S3", "B"), ("S3", "C")]
# The same network with one extra link, which closes a cycle.
CYCLIC_TOPOLOGY = LINE_TOPOLOGY + [("S3", "S1")]


class LearningSwitchNetwork:
    """Transparent bridges with flat (unstructured) addresses.

    Three rules, and no more: learn the source address on the port a frame
    arrived on; forward out the single port for a known destination; flood to
    every other port for an unknown one.  There is no protocol here — the
    tables are a side effect of traffic.
    """

    def __init__(self, links, switches=None):
        self.adj = {}
        for a, b in links:
            self.adj.setdefault(a, []).append(b)
            self.adj.setdefault(b, []).append(a)
        self.switches = sorted(switches if switches is not None
                               else [n for n in self.adj if n.startswith("S")])
        self.tables = {s: {} for s in self.switches}

    def has_cycle(self):
        """A cycle among the switches makes flooding loop forever: that is the
        whole argument for the spanning tree.  191.030's topic list does *not*
        name STP, so this is the boundary of what is in scope (note 02)."""
        seen, stack = set(), []
        for start in self.switches:
            if start in seen:
                continue
            stack.append((start, None))
            while stack:
                node, parent = stack.pop()
                if node in seen:
                    return True
                seen.add(node)
                for nb in self.adj[node]:
                    if nb in self.switches and nb != parent:
                        stack.append((nb, node))
        return False

    def send(self, src, dst):
        """Deliver one frame and return the list of (switch, out_port) hops it
        produced, flooding included.  Raises on a cyclic topology."""
        if self.has_cycle():
            raise ValueError("flooding never terminates on a cyclic topology")
        hops, delivered = [], False
        first = self.adj[src][0]
        queue = [(first, src)]                      # (switch, incoming port)
        while queue:
            sw, in_port = queue.pop(0)
            self.tables[sw][src] = in_port          # learn, always
            out = self.tables[sw].get(dst)
            ports = [out] if out and out != in_port else [
                p for p in self.adj[sw] if p != in_port]
            for p in ports:
                hops.append((sw, p))
                if p in self.switches:
                    queue.append((p, sw))
                elif p == dst:
                    delivered = True
        self.delivered = delivered
        return hops

    def flooded(self, hops):
        """True if the frame went out of more than one port anywhere."""
        per_switch = {}
        for sw, _ in hops:
            per_switch[sw] = per_switch.get(sw, 0) + 1
        return any(v > 1 for v in per_switch.values())

    def table_sizes(self):
        return {s: len(t) for s, t in self.tables.items()}


# ==========================================================================
# 2. Inter-domain routing policy: valley-free path selection
#    CNP3 "Inter-domain routing" exercises 1-2.
#    TISS topic: path-vector routing, AS relationships (notes 06, 07).
# ==========================================================================
#
# Restated topology (CNP3's figure, described rather than copied):
#   AS1 is a customer of AS2 and of AS3
#   AS4 is a customer of AS2
#   AS2 and AS3 are peers; AS3 and AS4 are peers
CNP3_AS_GRAPH = {
    ("AS1", "AS2"): "provider",     # read: AS2 is AS1's provider
    ("AS1", "AS3"): "provider",
    ("AS4", "AS2"): "provider",
    ("AS2", "AS3"): "peer",
    ("AS3", "AS4"): "peer",
}
# Preference order of RFC 4271 §9.1.1's "degree of preference" as every
# operator configures it, and as Gao & Rexford [S27] prove is stable.
PREFERENCE = {"self": 3, "customer": 2, "peer": 1, "provider": 0}


def _relations(graph):
    """{as: {neighbour: kind-of-neighbour}} from the edge list."""
    rel = {}
    for (a, b), kind in graph.items():
        if kind == "provider":                      # b is a's provider
            rel.setdefault(a, {})[b] = "provider"
            rel.setdefault(b, {})[a] = "customer"
        else:
            rel.setdefault(a, {})[b] = "peer"
            rel.setdefault(b, {})[a] = "peer"
    return rel


def valley_free_routes(graph, origin):
    """Best AS paths to `origin` at every AS, under the standard export rule.

    Export rule: a route learned from a **customer** (or originated here) goes
    to everybody; a route learned from a **peer or a provider** goes only to
    customers.  That single rule is what makes paths valley-free — no route
    ever climbs to a provider twice.

    Returns {as: (preference-class, [tied best paths])}; a path starts at the
    AS itself and ends at `origin`.
    """
    rel = _relations(graph)
    best = {origin: ("self", [[origin]])}
    for _ in range(4 * len(rel) + 4):               # until nothing changes
        changed = False
        for me in rel:
            offers = []
            for nb, nb_is in rel[me].items():
                if nb not in best:
                    continue
                kind, paths = best[nb]
                # what nb is willing to tell me
                if kind not in ("self", "customer") and rel[nb][me] != "customer":
                    continue
                for p in paths:
                    if me in p:
                        continue                    # AS_PATH loop detection
                    offers.append((nb_is, [me, *p]))
            if not offers:
                continue
            top = max(PREFERENCE[k] for k, _ in offers)
            shortest = min(len(p) for k, p in offers if PREFERENCE[k] == top)
            tied = sorted(p for k, p in offers
                          if PREFERENCE[k] == top and len(p) == shortest)
            kind = next(k for k, _ in offers if PREFERENCE[k] == top)
            if best.get(me) != (kind, tied):
                best[me] = (kind, tied)
                changed = True
        if not changed:
            return best
    raise RuntimeError("policy routing did not converge -- a Griffin/Wilfong gadget [S28]")


def best_path(graph, source, origin):
    kind, paths = valley_free_routes(graph, origin)[source]
    return kind, paths


# ==========================================================================
# 3. Hierarchical versus flat addressing
#    CNP3 "Building a network" open question 1.
#    TISS topic: IPv4/IPv6 addressing, forwarding and longest-prefix match
#    (notes 03, 04, 06).
# ==========================================================================
def flat_table_size(addresses):
    """Flat addresses carry no structure, so a forwarding table needs one
    entry per reachable address.  This is why switched networks do not
    scale and why the Internet is not one big Ethernet."""
    return len(set(addresses))


def aggregate(cidrs):
    """Collapse a set of prefixes into the smallest equivalent set.  This is
    CIDR: the table entry count follows the address *hierarchy*, not the
    host count."""
    nets = [ipaddress.ip_network(c) for c in cidrs]
    return [str(n) for n in ipaddress.collapse_addresses(nets)]


def hierarchical_table_size(cidrs):
    return len(aggregate(cidrs))


def hosts_behind(cidrs):
    return sum(ipaddress.ip_network(c).num_addresses for c in aggregate(cidrs))


def demo():
    print("CNP3 exercise types, solved [S35] -- answers are ours, not CNP3's")

    net = LearningSwitchNetwork(LINE_TOPOLOGY)
    for src, dst in (("C", "B"), ("A", "C"), ("B", "A")):
        hops = net.send(src, dst)
        print(f"  {src}->{dst}: flooded={net.flooded(hops)} tables={net.table_sizes()}")
    print("  cyclic variant has a cycle:",
          LearningSwitchNetwork(CYCLIC_TOPOLOGY).has_cycle())

    for src, origin in (("AS1", "AS4"), ("AS4", "AS2"), ("AS4", "AS1")):
        kind, paths = best_path(CNP3_AS_GRAPH, src, origin)
        print(f"  {src} -> {origin}: {kind} route(s) {paths}")

    cidrs = ["203.0.113.0/26", "203.0.113.64/26", "203.0.113.128/26", "203.0.113.192/26"]
    print(f"  {len(cidrs)} prefixes aggregate to {aggregate(cidrs)}"
          f" ({hosts_behind(cidrs)} addresses, 1 table entry;"
          f" flat would need {hosts_behind(cidrs)})")


if __name__ == "__main__":
    demo()
