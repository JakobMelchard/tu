"""Path-vector routing: a BGP-style simulator with a policy hook (notes 06, 07).

Every AS advertises to its neighbours the full AS path it uses for each
prefix.  Loop avoidance is trivial: reject any path that already contains
your own AS number.  Policy enters twice, as in real BGP:
  * import policy  - which received paths are acceptable and how preferred
  * export policy  - which of your best paths you tell which neighbour
The default policy implements Gao-Rexford valley-free routing over
customer/provider/peer relationships: prefer customer > peer > provider
routes, then shortest AS path; export customer routes to everyone and
peer/provider routes only to customers.

RFC sections: the AS-loop check is RFC 4271 section 9.1.2 ("scanning the full
AS path ... checking that the autonomous system number of the local system
does not appear"); withdrawal of routes a neighbour stops advertising stands in
for section 4.3's WITHDRAWN ROUTES; import and export policy are the "policy
information base" of sections 3.2 and 9.1.  The customer/peer/provider rules
are Gao and Rexford (refs/SOURCES.md S27), not RFC 4271, which contains none of
them.  The RFC's own decision process is `bgp_decision.py`.  With `ShortestPath`
the converged AS paths are BFS shortest paths, which the test checks against
networkx.
"""
CUSTOMER, PEER, PROVIDER = "customer", "peer", "provider"
PREF = {CUSTOMER: 3, PEER: 2, PROVIDER: 1}


class GaoRexford:
    def __init__(self, relations):
        """relations: {(a, b): kind} meaning 'b is a <kind> of a'."""
        self.rel = relations

    def kind(self, me, neighbour):
        return self.rel[(me, neighbour)]

    def accept(self, me, neighbour, path):
        return True

    def rank(self, me, neighbour, path):
        """Higher is better: local preference by relationship, then shorter path,
        then lowest neighbour AS number as tie-break (deterministic)."""
        return (PREF[self.kind(me, neighbour)], -len(path), -neighbour)

    def export(self, me, learned_from, to):
        """Valley-free: a route learnt from a peer or provider goes to customers only."""
        if learned_from is None:                     # own prefix: tell everyone
            return True
        if self.kind(me, learned_from) == CUSTOMER:
            return True
        return self.kind(me, to) == CUSTOMER


class ShortestPath:
    """Policy-free baseline: everyone accepts and exports everything."""
    def accept(self, me, neighbour, path):
        return True

    def rank(self, me, neighbour, path):
        return (-len(path), -neighbour)

    def export(self, me, learned_from, to):
        return True


class PathVectorNetwork:
    def __init__(self, links, origins, policy=None):
        """links: iterable of (a, b) adjacencies; origins: {prefix: as}."""
        self.adj = {}
        for a, b in links:
            self.adj.setdefault(a, set()).add(b)
            self.adj.setdefault(b, set()).add(a)
        self.policy = policy or ShortestPath()
        self.rib_in = {a: {} for a in self.adj}          # as -> {(prefix, from): path}
        self.best = {a: {} for a in self.adj}            # as -> {prefix: (path, from)}
        self.log = []
        for prefix, origin in origins.items():
            self.best[origin][prefix] = ((origin,), None)

    def step(self):
        """One synchronous round of UPDATE exchange.  Returns True if any best path changed."""
        msgs = []
        for a in self.adj:
            for prefix, (path, frm) in self.best[a].items():
                for nb in self.adj[a]:          # also back to `frm`: loop check drops it
                    if self.policy.export(a, frm, nb):
                        msgs.append((nb, a, prefix, path))
        changed = False
        # withdraw: forget everything a neighbour no longer advertises
        advertised = {(nb, a, prefix) for nb, a, prefix, _ in msgs}
        for a in self.adj:
            for key in list(self.rib_in[a]):
                prefix, frm = key
                if (a, frm, prefix) not in advertised:
                    del self.rib_in[a][key]
        for to, frm, prefix, path in msgs:
            if to in path:
                self.log.append(f"{to} rejects {prefix} via {frm}: loop {path}")
                continue
            if self.policy.accept(to, frm, path):
                self.rib_in[to][(prefix, frm)] = (to,) + path
        for a in self.adj:
            for prefix in {p for p, _ in self.rib_in[a]} | set(self.best[a]):
                old = self.best[a].get(prefix)
                if old is not None and old[1] is None:
                    continue                                # own prefix always wins
                cands = [(self.policy.rank(a, frm, p), p, frm)
                         for (pfx, frm), p in self.rib_in[a].items() if pfx == prefix]
                new = None
                if cands:
                    _, p, frm = max(cands)
                    new = (p, frm)
                if new != old:
                    changed = True
                    if new is None:
                        del self.best[a][prefix]
                    else:
                        self.best[a][prefix] = new
        return changed

    def converge(self, max_rounds=100):
        for r in range(1, max_rounds + 1):
            if not self.step():
                return r
        return None

    def path(self, a, prefix):
        b = self.best[a].get(prefix)
        return b[0] if b else None

    def remove_link(self, a, b):
        self.adj[a].discard(b)
        self.adj[b].discard(a)


def demo():
    # 4 = tier-1, 2 and 3 buy transit from 4, 1 is a customer of 2 and 3, 2-3 peer.
    links = [(1, 2), (1, 3), (2, 3), (2, 4), (3, 4)]
    rel = {}
    for cust, prov in [(1, 2), (1, 3), (2, 4), (3, 4)]:
        rel[(cust, prov)], rel[(prov, cust)] = PROVIDER, CUSTOMER
    rel[(2, 3)] = rel[(3, 2)] = PEER
    net = PathVectorNetwork(links, {"p1": 1, "p4": 4}, GaoRexford(rel))
    rounds = net.converge()
    print(f"converged after {rounds} rounds")
    for a in sorted(net.adj):
        print(a, {p: net.path(a, p) for p in ("p1", "p4")})
    print("\n".join(net.log[:5]))
    return net


if __name__ == "__main__":
    demo()
