"""Solutions to the **routing** practice problems of MIT 6.02, Fall 2012
(Balakrishnan & Verghese), published on MIT OpenCourseWare under
**CC BY-NC-SA 4.0** [S34]: tutorial 8 (store-and-forward delay) and tutorial 10
(distance vector, link state, routing loops).  Transport is in
`mit602_transport.py`.

This is **not** 191.030 material.  191.030 is new in 2026W and has no past
paper [S2].  MIT 6.02 is a different course at a different institution; these
tutorials are used only because OCW publishes them **with official solutions**,
which makes them the one place in this tree where a routing answer can be
checked against a number somebody else published — the same discipline as
`../../py/test_rfc_vectors.py`.

Every problem is **restated in our own words**; none of MIT's prose is copied.
The published answers are quoted as bare numbers in `PUBLISHED_ANSWERS`.
See `README.md` for the overlap with 191.030's topic list and for the scope
differences, which are large in both directions.

Run `python3 mit602_routing.py` for a demo.
"""
from itertools import permutations

# --------------------------------------------------------------------------
# The answers MIT published, keyed by tutorial and problem.  Quoting a result
# is not quoting the sheet: these are the numbers the solution PDFs print.
# --------------------------------------------------------------------------
PUBLISHED_ANSWERS = {
    ("t08", "2A"): 30e-6,          # seconds, one switch / two links
    ("t08", "2B"): 60e-6,          # seconds, three switches / four links
    ("t10", "1A"): {"A->B": 5, "A->C": 10, "D->E": 5, "F->D": 5},
    ("t10", "1B"): {"B_says_C_unreachable": 55, "A_knows_C_unreachable": 55,
                    "D_new_route_to_E": 75},
    ("t10", "2A"): {"MinCost": True, "MinHop": True,
                    "SecondMinCost": False, "MinCostSquared": True},
}


# --------------------------------------------------------------------------
# Tutorial 8, problem 2 — store-and-forward latency
#   "Sender and receiver separated by N links and N-1 switches, each switch
#    forwarding only after the last bit has arrived."
# TISS topic: foundations / sources of delay (note 01).
# --------------------------------------------------------------------------
def store_and_forward_latency(packet_bits, rate_bps, prop_delay_s, links):
    """First bit sent to last bit received across `links` links in series,
    every intermediate node storing the whole packet before forwarding.

    Each link contributes one transmission delay and one propagation delay.
    """
    return links * (packet_bits / rate_bps + prop_delay_s)


# --------------------------------------------------------------------------
# Tutorial 10, problem 1 — distance-vector convergence on a clock
#
# The sheet's topologies are figures (images), so they are not in the PDF
# text.  They are *reconstructed* from the published answers and stated here
# explicitly, which is the honest way to use a sheet whose figures we cannot
# read:
#   network I  = the path A-B-C   (A learns B at 5, C at 10 => two hops)
#   network II = the triangle D-E-F
#                (F learns D at 5 => adjacent; after D-E fails D re-routes
#                 via F, which is only possible if the graph has a cycle)
# Both reconstructions are forced by the answers; no other 3-node graph fits.
#
# TISS topic: routing and forwarding, as the contrast that motivates link
# state and path vector (note 07 keeps distance vector for exactly that).
# --------------------------------------------------------------------------
NETWORK_I = [("A", "B"), ("B", "C")]
NETWORK_II = [("D", "E"), ("E", "F"), ("F", "D")]

INFINITY = float("inf")


class TimedDV:
    """Distance vector with a wall clock and **split horizon**.

    Split horizon is a modelling choice, stated rather than assumed: without
    it the B-C failure counts to infinity through A and B's advertisement at
    t=55 would not say "unreachable", so the published answer pins it.
    `../../py/distvector.py` has the fuller implementation with the
    count-to-infinity demonstration and poisoned reverse.
    """

    def __init__(self, links, period=5):
        self.period = period
        self.links = {frozenset(e) for e in links}
        self.nodes = sorted({n for e in links for n in e})
        # table[node][dest] = (cost, next_hop)
        self.table = {n: {n: (0, n)} for n in self.nodes}
        self.last_sent = {n: {} for n in self.nodes}
        self.t = 0

    def neighbours(self, n):
        return sorted(m for m in self.nodes if frozenset((n, m)) in self.links)

    def cut(self, a, b):
        """A link fails; HELLO notices before the next advertisement, so every
        route whose next hop was across it goes to infinity immediately."""
        self.links.discard(frozenset((a, b)))
        for n in (a, b):
            other = b if n == a else a
            for dst, (_, nh) in list(self.table[n].items()):
                if nh == other:
                    self.table[n][dst] = (INFINITY, None)

    def advertise(self):
        """One advertisement round: everybody sends the vector it holds *now*,
        then everybody integrates.  Zero propagation and processing delay, so
        a change can cross one hop per round."""
        self.t += self.period
        outgoing = {}
        for n in self.nodes:
            for m in self.neighbours(n):
                vec = {d: c for d, (c, nh) in self.table[n].items()
                       if nh != m}                      # split horizon
                outgoing[(n, m)] = vec
                self.last_sent[n][m] = vec
        for (src, dst_node), vec in outgoing.items():
            tbl = self.table[dst_node]
            for d, c in vec.items():
                if d == dst_node:
                    continue
                new = c + 1
                cur, nh = tbl.get(d, (INFINITY, None))
                if nh == src or new < cur:              # believe your next hop
                    tbl[d] = (new, src) if new < INFINITY else (INFINITY, None)
        return self.t

    def reachable(self, node, dst):
        c, _ = self.table[node].get(dst, (INFINITY, None))
        return c < INFINITY


def dv_first_entry_times(links, pairs, period=5, rounds=6):
    """t at which `node` first holds a finite route to `dst`, for each
    (node, dst) in `pairs`.  Reproduces tutorial 10 problem 1A."""
    net = TimedDV(links, period)
    out = {}
    for _ in range(rounds):
        t = net.advertise()
        for node, dst in pairs:
            key = f"{node}->{dst}"
            if key not in out and net.reachable(node, dst):
                out[key] = t
    return out


def dv_failure_times(links, cut, at, watchers, period=5, rounds=20):
    """Cut a link at time `at` and report when each watcher predicate first
    holds.  Reproduces tutorial 10 problem 1B."""
    net = TimedDV(links, period)
    out = {}
    done = False
    for _ in range(rounds):
        if not done and net.t + period > at:
            net.cut(*cut)                                # HELLO, then advertise
            done = True
        t = net.advertise()
        if not done:
            continue                 # only the post-failure behaviour is asked
        for name, pred in watchers.items():
            if name not in out and pred(net):
                out[name] = t
    return out


# --------------------------------------------------------------------------
# Tutorial 10, problem 2 — which routing strategies can loop
#
# Four ways of picking a path to a destination.  Three are safe; one is not,
# and the sheet's counter-example is an equal-cost triangle.
# --------------------------------------------------------------------------
TRIANGLE = {"A": {"B": 1, "D": 1}, "B": {"A": 1, "D": 1}, "D": {"A": 1, "B": 1}}


def simple_paths(graph, src, dst):
    """All loop-free paths, by brute force.  Fine for exam-sized graphs."""
    if src == dst:
        return [[src]]
    others = [n for n in graph if n not in (src, dst)]
    out = []
    for k in range(len(others) + 1):
        for mid in permutations(others, k):
            p = [src, *mid, dst]
            if all(p[i + 1] in graph[p[i]] for i in range(len(p) - 1)):
                out.append(p)
    return out


def _cost(graph, p):
    return sum(graph[p[i]][p[i + 1]] for i in range(len(p) - 1))


STRATEGIES = {
    "MinCost": lambda g, ps: min(ps, key=lambda p: (_cost(g, p), p)),
    "MinHop": lambda g, ps: min(ps, key=lambda p: (len(p), p)),
    "MinCostSquared": lambda g, ps: min(
        ps, key=lambda p: (sum(g[p[i]][p[i + 1]] ** 2 for i in range(len(p) - 1)), p)),
    # "second lowest sum of link costs": sort by cost and take the runner-up
    "SecondMinCost": lambda g, ps: sorted(ps, key=lambda p: (_cost(g, p), p))[
        min(1, len(ps) - 1)],
}


def next_hops(graph, dst, strategy):
    """Each node's next hop to `dst` under `strategy`."""
    pick = STRATEGIES[strategy]
    hops = {}
    for n in graph:
        if n == dst:
            continue
        ps = [p for p in simple_paths(graph, n, dst) if len(p) > 1]
        if ps:
            hops[n] = pick(graph, ps)[1]
    return hops


def has_loop(graph, dst, strategy):
    """True if following next hops from some node never reaches `dst`."""
    hops = next_hops(graph, dst, strategy)
    for start in hops:
        seen, cur = set(), start
        while cur != dst:
            if cur in seen or cur not in hops:
                return True
            seen.add(cur)
            cur = hops[cur]
    return False


def strategy_is_loop_free(strategy, graphs=(TRIANGLE,)):
    return all(not has_loop(g, d, strategy) for g in graphs for d in g)


def demo():
    print("MIT 6.02 Fall 2012 routing practice problems [S34]")
    print("  t08 P2A store-and-forward, 2 links:",
          store_and_forward_latency(5000, 1e9, 10e-6, 2), "s")
    print("  t10 P1A first entries:",
          dv_first_entry_times(NETWORK_I, [("A", "B"), ("A", "C")])
          | dv_first_entry_times(NETWORK_II, [("D", "E"), ("F", "D")]))
    print("  t10 P2A loop-free?",
          {s: strategy_is_loop_free(s) for s in STRATEGIES})


if __name__ == "__main__":
    demo()
