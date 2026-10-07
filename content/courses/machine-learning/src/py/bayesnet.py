"""Discrete Bayesian networks: the joint, inference by enumeration, d-separation,
Markov blankets, CPT estimation, ancestral sampling -- and the AIMA alarm network.

Asked in almost every paper [S11]: when two nodes are d-separated, what the chain
rule buys, why a general network can beat naive Bayes, and -- in five papers --
"describe a local-search algorithm for Bayesian network creation".  The course's
recipe for that is in note 09; `fit_cpts` is its "structure known" half, and
`score_structure` / `hill_climb_structure` below are its "structure unknown"
half, maximising log P(D | M) - alpha * #M over add/remove/reverse-arc
neighbourhoods [S14].

The alarm network's numbers are Russell & Norvig's [S25]; `enumeration_ask`
reproduces their P(B | j, m) = 0.284.

The naive Bayes classifiers are in `bayes.py`.
"""
import itertools
import numpy as np


# ----------------------------------------------------------- Bayesian network
class BayesianNetwork:
    """Discrete BN.  nodes: {name: n_values}; parents: {name: [parent names]} (topological order);
    cpt[name]: dict mapping tuple(parent values) -> probability vector over the node's values."""

    def __init__(self, nodes, parents, cpt=None):
        self.nodes, self.parents = dict(nodes), {n: list(parents.get(n, [])) for n in nodes}
        self.cpt = cpt or {}
        self.order = self._topological()

    def _topological(self):
        order, seen = [], set()

        def visit(n):
            if n not in seen:
                seen.add(n)
                for p in self.parents[n]:
                    visit(p)
                order.append(n)
        for n in self.nodes:
            visit(n)
        return order

    def children(self, n):
        return [c for c in self.nodes if n in self.parents[c]]

    def prob(self, node, value, assignment):
        return self.cpt[node][tuple(assignment[p] for p in self.parents[node])][value]

    def joint(self, assignment):
        """P(x_1..x_n) = prod_i P(x_i | parents(x_i))  (chain rule with the BN factorisation)."""
        return float(np.prod([self.prob(n, assignment[n], assignment) for n in self.nodes]))

    def enumeration_ask(self, query, evidence):
        """P(query | evidence) by summing the joint over all hidden variables (exponential, but exact)."""
        dist = np.zeros(self.nodes[query])
        for v in range(self.nodes[query]):
            e = dict(evidence, **{query: v})
            dist[v] = self._enumerate_all(self.order, e)
        return dist / dist.sum()

    def _enumerate_all(self, variables, e):
        if not variables:
            return 1.0
        Y, rest = variables[0], variables[1:]
        if Y in e:
            return self.prob(Y, e[Y], e) * self._enumerate_all(rest, e)
        return sum(self.prob(Y, v, dict(e, **{Y: v})) * self._enumerate_all(rest, dict(e, **{Y: v}))
                   for v in range(self.nodes[Y]))

    def d_separated(self, X, Y, Z=()):
        """X and Y d-separated given Z  <=>  separated in the moralised ancestral graph with Z removed."""
        Z = set(Z)
        anc, stack = set(), list({X, Y} | Z)
        while stack:                                                   # ancestral subgraph
            n = stack.pop()
            if n not in anc:
                anc.add(n); stack.extend(self.parents[n])
        adj = {n: set() for n in anc}
        for n in anc:                                                  # moralise: link co-parents, drop direction
            for p in self.parents[n]:
                adj[n].add(p); adj[p].add(n)
            for p, q in itertools.combinations(self.parents[n], 2):
                adj[p].add(q); adj[q].add(p)
        seen, stack = set(), [X]                                       # reachability avoiding Z
        while stack:
            n = stack.pop()
            if n == Y:
                return False
            if n not in seen and n not in Z:
                seen.add(n); stack.extend(adj[n] - Z)
        return True

    def markov_blanket(self, n):
        mb = set(self.parents[n]) | set(self.children(n))
        for c in self.children(n):
            mb |= set(self.parents[c])
        return mb - {n}

    def fit_cpts(self, data, alpha=1.0):
        """MLE with Laplace smoothing: P(x|pa) = (N(x,pa) + alpha) / (N(pa) + alpha k).  data: {name: int array}."""
        for n in self.nodes:
            k, pa = self.nodes[n], self.parents[n]
            self.cpt[n] = {}
            for combo in itertools.product(*(range(self.nodes[p]) for p in pa)):
                mask = np.all([data[p] == v for p, v in zip(pa, combo)], axis=0) if pa else np.ones(len(data[n]), bool)
                counts = np.bincount(data[n][mask], minlength=k) + alpha
                self.cpt[n][combo] = counts / counts.sum()
        return self

    def sample(self, n, rng=0):
        """Ancestral (forward) sampling in topological order."""
        r = np.random.default_rng(rng)
        data = {name: np.zeros(n, int) for name in self.nodes}
        for i in range(n):
            a = {}
            for name in self.order:
                a[name] = r.choice(self.nodes[name], p=self.cpt[name][tuple(a[p] for p in self.parents[name])])
                data[name][i] = a[name]
        return data


def alarm_network():
    """AIMA burglary example: B, E -> A -> J, M (value 1 = true)."""
    bn = BayesianNetwork({"B": 2, "E": 2, "A": 2, "J": 2, "M": 2},
                         {"A": ["B", "E"], "J": ["A"], "M": ["A"]})
    bn.cpt["B"] = {(): np.array([0.999, 0.001])}
    bn.cpt["E"] = {(): np.array([0.998, 0.002])}
    bn.cpt["A"] = {(1, 1): np.array([0.05, 0.95]), (1, 0): np.array([0.06, 0.94]),
                   (0, 1): np.array([0.71, 0.29]), (0, 0): np.array([0.999, 0.001])}
    bn.cpt["J"] = {(1,): np.array([0.10, 0.90]), (0,): np.array([0.95, 0.05])}
    bn.cpt["M"] = {(1,): np.array([0.30, 0.70]), (0,): np.array([0.99, 0.01])}
    return bn


# ------------------------------------------- structure learning by local search
# The course's "Case B: structure not known" [S14]: find a network that fits the
# data and has low complexity by maximising  log P(D | M) - alpha * #M  over a
# neighbourhood built by adding, removing or reversing a single arc.  Asked as a
# long-answer question in E20c, E21b, E21c, E21d and E22a [S11].
#
# `data` is what BayesianNetwork.sample returns: {node name: array of values}.
def n_params(nodes, parents):
    """(k - 1) * prod(parent cardinalities) summed over nodes -- the #M of the score."""
    return sum((nodes[n] - 1) * int(np.prod([nodes[p] for p in parents.get(n, [])] or [1]))
               for n in nodes)


def log_likelihood(data, nodes, parents):
    """log P(D | M) at the maximum-likelihood parameters, from counts alone."""
    total = 0.0
    for name, k in nodes.items():
        pa = list(parents.get(name, []))
        key = np.zeros(len(data[name]), int)
        for p in pa:                                  # encode the parent configuration
            key = key * nodes[p] + data[p]
        for config in np.unique(key):
            sel = key == config
            counts = np.bincount(data[name][sel], minlength=k)
            n = counts.sum()
            nz = counts > 0
            total += float(np.sum(counts[nz] * np.log(counts[nz] / n)))
    return total


def score_structure(data, nodes, parents, alpha=1.0):
    """The course's score: log P(D | M) - alpha * #M [S14]."""
    return log_likelihood(data, nodes, parents) - alpha * n_params(nodes, parents)


def _acyclic(nodes, parents):
    colour = {n: 0 for n in nodes}

    def visit(n):
        if colour[n] == 1:
            return False
        if colour[n] == 2:
            return True
        colour[n] = 1
        ok = all(visit(p) for p in parents.get(n, []))
        colour[n] = 2
        return ok
    return all(visit(n) for n in nodes)


def neighbourhood(nodes, parents):
    """Every network one arc away: add, remove or reverse a single arc [S14]."""
    names = list(nodes)
    for child in names:
        for parent in names:
            if parent == child:
                continue
            cand = {n: list(parents.get(n, [])) for n in names}
            if parent in cand[child]:
                cand[child].remove(parent)                      # remove
                yield cand
                rev = {n: list(v) for n, v in cand.items()}
                rev[parent].append(child)                       # reverse
                if _acyclic(nodes, rev):
                    yield rev
            else:
                cand[child].append(parent)                      # add
                if _acyclic(nodes, cand):
                    yield cand


def hill_climb_structure(data, nodes, alpha=1.0, max_steps=50):
    """Greedy local search from the empty network; returns (parents, score).

    Step 1 construct an initial network, 2 score it, 3 build the neighbourhood,
    4 move to the best neighbour, 5 repeat -- the algorithm the exam asks you to
    describe [S12, S14].  Simulated annealing and tabu search replace step 4.
    """
    parents = {n: [] for n in nodes}
    best = score_structure(data, nodes, parents, alpha)
    for _ in range(max_steps):
        improved = False
        for cand in neighbourhood(nodes, parents):
            s = score_structure(data, nodes, cand, alpha)
            if s > best + 1e-9:
                parents, best, improved = cand, s, True
        if not improved:
            break
    return parents, best


if __name__ == "__main__":
    bn = alarm_network()
    print("P(B | j, m) =", bn.enumeration_ask("B", {"J": 1, "M": 1}).round(4), "(AIMA: 0.716, 0.284)")
    print("P(J | b) =", bn.enumeration_ask("J", {"B": 1}).round(4))
    print("B _||_ E ?", bn.d_separated("B", "E"), "| B _||_ E given A ?", bn.d_separated("B", "E", ["A"]),
          "| J _||_ M given A ?", bn.d_separated("J", "M", ["A"]))
    print("Markov blanket of A:", sorted(bn.markov_blanket("A")))
    data = bn.sample(20000, rng=1)
    est = BayesianNetwork(bn.nodes, bn.parents).fit_cpts(data)
    print("estimated P(A | b, e) =", est.cpt["A"][(1, 1)].round(2), "(B=E=1 never sampled -> pure Laplace prior)",
          " P(J | a) =", est.cpt["J"][(1,)].round(3))

    print("\nstructure search: maximise log P(D | M) - alpha * #M by hill climbing [S14]")
    learned, score = hill_climb_structure(data, bn.nodes, alpha=2.0)
    print("  learned parents:", {n: p for n, p in learned.items() if p})
    print("  score %.1f   vs the true structure %.1f"
          % (score, score_structure(data, bn.nodes, bn.parents, alpha=2.0)))
