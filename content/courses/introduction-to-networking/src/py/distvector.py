"""Distance-vector routing: distributed Bellman-Ford with a count-to-infinity
demo, split horizon and poisoned reverse (notes 06, 07).

Each node keeps D_x(y) = min over neighbours v of c(x,v) + D_v(y) and sends its
vector to its neighbours whenever it changes (RIP style, with an 'infinity' of 16).

RFC status: this is RIP's algorithm (RFC 2453, and RFC 1058 before it:
infinity 16, split horizon, poisoned reverse).  Neither RFC is vendored here
and distance vector is not on the TISS topic list, so the section numbers are
not cited; note 07 keeps it as the contrast to link state and path vector.
The converged tables are checked against networkx's Bellman-Ford.
"""
INF = 16


class DVNode:
    def __init__(self, name, links):
        self.name = name
        self.links = dict(links)            # neighbour -> cost
        self.table = {name: (0, None)}      # dest -> (cost, next_hop)
        for n, c in links.items():
            self.table[n] = (c, n)
        self.neighbour_vectors = {}

    def vector_for(self, neighbour, split_horizon=False, poison_reverse=False):
        """What this node advertises to `neighbour`."""
        out = {}
        for dst, (cost, nh) in self.table.items():
            if nh == neighbour and dst != neighbour:
                if split_horizon:
                    continue                # don't tell v about routes learnt via v
                if poison_reverse:
                    out[dst] = INF          # tell v the route is unreachable
                    continue
            out[dst] = cost
        return out

    def receive(self, neighbour, vector):
        """Bellman-Ford update.  Returns True if own table changed."""
        self.neighbour_vectors[neighbour] = vector
        return self.recompute()

    def recompute(self):
        new = {self.name: (0, None)}
        dests = set(self.links) | {d for v in self.neighbour_vectors.values() for d in v}
        for dst in dests:
            if dst == self.name:
                continue
            best = (self.links.get(dst, INF), dst)          # direct link, if any
            for v, vec in self.neighbour_vectors.items():
                if v in self.links and dst in vec:
                    cand = min(INF, self.links[v] + vec[dst])
                    if cand < best[0]:
                        best = (cand, v)
            new[dst] = best if best[0] < INF else (INF, None)
        changed = new != self.table
        self.table = new
        return changed


class DVNetwork:
    def __init__(self, edges, split_horizon=False, poison_reverse=False):
        adj = {}
        for a, b, c in edges:
            adj.setdefault(a, {})[b] = c
            adj.setdefault(b, {})[a] = c
        self.nodes = {n: DVNode(n, links) for n, links in adj.items()}
        self.sh, self.pr = split_horizon, poison_reverse

    def round(self):
        """Synchronous exchange: everybody sends, then everybody updates."""
        msgs = [(v, n.name, n.vector_for(v, self.sh, self.pr))
                for n in self.nodes.values() for v in n.links]
        changed = [self.nodes[to].receive(frm, vec) for to, frm, vec in msgs]   # deliver all
        return any(changed)

    def converge(self, max_rounds=50):
        for r in range(1, max_rounds + 1):
            if not self.round():
                return r
        return None                              # did not converge

    def cut_link(self, a, b):
        for x, y in ((a, b), (b, a)):
            self.nodes[x].links.pop(y, None)
            self.nodes[x].neighbour_vectors.pop(y, None)
            self.nodes[x].recompute()

    def cost(self, node, dst):
        return self.nodes[node].table.get(dst, (INF, None))[0]

    def dump(self):
        return {n: {d: c for d, (c, _) in node.table.items()} for n, node in self.nodes.items()}


def count_to_infinity_demo(split_horizon=False, poison_reverse=False, verbose=True):
    """Chain A - B - C.  Cut A-B; B still believes C can reach A (via B!), so
    B and C bounce the cost up by 1 per round until it hits INF."""
    net = DVNetwork([("A", "B", 1), ("B", "C", 1)], split_horizon, poison_reverse)
    net.converge()
    net.cut_link("A", "B")
    history = []
    for r in range(INF + 2):
        history.append((net.cost("B", "A"), net.cost("C", "A")))
        if verbose:
            print(f"round {r:2d}: D_B(A)={history[-1][0]:2d}  D_C(A)={history[-1][1]:2d}")
        if not net.round():
            break
    return history


if __name__ == "__main__":
    print("plain distance vector after cutting A-B:")
    count_to_infinity_demo()
    print("\nwith poisoned reverse:")
    count_to_infinity_demo(poison_reverse=True)
