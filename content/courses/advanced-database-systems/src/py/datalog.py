"""A small Datalog engine: parser, safety check, stratification, naive and
semi-naive bottom-up evaluation. Note 04; [S7] ch. 12, 13.1, 15.2; [S8] ch. 2-3.

Syntax (one statement per '.', '%' starts a comment):
    edge(a, b).                          fact (EDB = extensional database)
    path(X, Y) :- edge(X, Y).            rule; head predicate is IDB (intensional)
    path(X, Y) :- edge(X, Z), path(Z, Y).
    single(X) :- node(X), not paired(X). negation
    lt(X, Y) :- num(X), num(Y), X < Y.   comparisons =, !=, <, <=, >, >=
Variables start with an upper-case letter or '_'; constants are lower-case
identifiers, integers or 'quoted strings'.

Semantics: the immediate-consequence operator T_P(I) = all heads of ground
rule instances whose body is true in I. For positive programs the answer is
the least fixpoint of I -> EDB u T_P(I) (reached after finitely many steps,
since only constants of the input occur). With stratified negation it is
computed stratum by stratum, lower strata being complete when negated.

Run: python datalog.py
"""
from __future__ import annotations

import re
from collections import defaultdict
from dataclasses import dataclass, field

TOKEN = re.compile(r":-|!=|<=|>=|[=<>(),.]|'[^']*'|-?\d+|[A-Za-z_][A-Za-z0-9_]*")


class DatalogError(ValueError):
    pass


@dataclass(frozen=True)
class Var:
    name: str


@dataclass(frozen=True)
class Atom:                      # p(t1, ..., tk), possibly negated
    pred: str
    args: tuple
    negated: bool = False


@dataclass(frozen=True)
class Cmp:                       # X < Y and friends
    op: str
    left: object
    right: object


def _show(b) -> str:
    t = lambda x: x.name if isinstance(x, Var) else str(x)
    if isinstance(b, Cmp):
        return f"{t(b.left)} {b.op} {t(b.right)}"
    return ("not " if b.negated else "") + f"{b.pred}({', '.join(map(t, b.args))})"


@dataclass
class Rule:
    head: Atom
    body: list

    def __str__(self) -> str:
        return f"{_show(self.head)} :- {', '.join(map(_show, self.body))}."


def tokenize(text: str) -> list[str]:
    text = re.sub(r"%[^\n]*", "", text)                  # comments
    rest = TOKEN.sub(" ", text).strip()
    if rest:
        raise DatalogError(f"bad input near {rest[:20]!r}")
    return TOKEN.findall(text)


def _term(tok: str):
    if tok[0].isupper() or tok[0] == "_":
        return Var(tok)
    if tok[0] == "'":
        return tok[1:-1]
    if re.fullmatch(r"-?\d+", tok):
        return int(tok)
    return tok


def parse(text: str) -> tuple[list[Rule], dict[str, set]]:
    toks, i = tokenize(text) + ["<end>"] * 3, 0     # sentinels: truncated input fails cleanly
    rules, facts = [], defaultdict(set)

    def literal():
        nonlocal i
        neg = toks[i] == "not"
        i += neg
        if i + 1 < len(toks) and toks[i + 1] in ("=", "!=", "<", "<=", ">", ">="):
            left, op, right = _term(toks[i]), toks[i + 1], _term(toks[i + 2])
            i += 3
            return Cmp(op, left, right)
        pred, args = toks[i], []
        if toks[i + 1] != "(":
            raise DatalogError(f"expected '(' after {pred}")
        i += 2
        while toks[i] != ")":
            if toks[i] in ("<end>", ":-", ".", "("):
                raise DatalogError(f"unclosed argument list of {pred}")
            args.append(_term(toks[i]))
            i += 1
            if toks[i] == ",":
                i += 1
        i += 1
        return Atom(pred, tuple(args), neg)

    while toks[i] != "<end>":
        head = literal()
        if toks[i] == ".":
            i += 1
            if any(isinstance(a, Var) for a in head.args):
                raise DatalogError(f"fact with variable: {head}")
            facts[head.pred].add(head.args)
            continue
        if toks[i] != ":-":
            raise DatalogError(f"expected ':-' or '.' near {toks[i]!r}")
        i += 1
        body = [literal()]
        while toks[i] == ",":
            i += 1
            body.append(literal())
        if toks[i] != ".":
            raise DatalogError(f"expected '.' near {toks[i]!r}")
        i += 1
        rules.append(Rule(head, body))
    return rules, dict(facts)


def _vars(xs) -> set:
    return {x for x in xs if isinstance(x, Var)}


def check_safety(rule: Rule) -> None:
    """Range restriction: every variable of the head, of a negated atom and of a
    comparison must occur in some positive relational atom of the body [S7 12.1]."""
    pos = set().union(*[_vars(b.args) for b in rule.body if isinstance(b, Atom) and not b.negated])
    need = _vars(rule.head.args)
    for b in rule.body:
        need |= _vars((b.left, b.right)) if isinstance(b, Cmp) else _vars(b.args)
    if need - pos:
        raise DatalogError(f"unsafe rule {rule}: {sorted(v.name for v in need - pos)} "
                           "not bound by a positive atom")


def stratify(rules: list[Rule]) -> list[set[str]]:
    """Assign stratum s(p) with s(head) >= s(q) for positive q and s(head) > s(q)
    for negated q. A negative edge on a cycle makes s grow without bound."""
    idb = {r.head.pred for r in rules}
    s = {p: 0 for p in idb}
    changed = True
    while changed:
        changed = False
        for r in rules:
            for b in r.body:
                if isinstance(b, Atom) and b.pred in idb:
                    lo = s[b.pred] + (1 if b.negated else 0)
                    if s[r.head.pred] < lo:
                        s[r.head.pred] = lo
                        changed = True
                        if lo > len(idb):
                            raise DatalogError("program is not stratifiable "
                                               "(cycle through negation)")
    strata = defaultdict(set)
    for p, k in s.items():
        strata[k].add(p)
    return [strata[k] for k in sorted(strata)]


def _match(args, tup, env):
    env = dict(env)
    for a, v in zip(args, tup):
        if isinstance(a, Var):
            if a in env and env[a] != v:
                return None
            env[a] = v
        elif a != v:
            return None
    return env


OPS = {"=": lambda a, b: a == b, "!=": lambda a, b: a != b, "<": lambda a, b: a < b,
       "<=": lambda a, b: a <= b, ">": lambda a, b: a > b, ">=": lambda a, b: a >= b}


def fire(rule: Rule, db, delta=None, delta_at: int | None = None) -> list[tuple]:
    """All head tuples of one rule. Positive atom number `delta_at` reads `delta`
    instead of `db` (semi-naive). Duplicates are kept: len() = derivations."""
    positives = [b for b in rule.body if isinstance(b, Atom) and not b.negated]
    envs = [{}]
    for k, atom in enumerate(positives):
        rel = (delta if k == delta_at else db).get(atom.pred, set())
        envs = [e2 for e in envs for t in rel if len(t) == len(atom.args)
                for e2 in [_match(atom.args, t, e)] if e2 is not None]
    val = lambda e, x: e[x] if isinstance(x, Var) else x
    out = []
    for e in envs:
        ok = True
        for b in rule.body:
            if isinstance(b, Cmp):
                ok = OPS[b.op](val(e, b.left), val(e, b.right))
            elif b.negated:
                ok = tuple(val(e, a) for a in b.args) not in db.get(b.pred, set())
            if not ok:
                break
        if ok:
            out.append(tuple(val(e, a) for a in rule.head.args))
    return out


@dataclass
class Stats:
    rounds: int = 0
    derivations: int = 0
    trace: list = field(default_factory=list)   # new facts per round


def evaluate(rules: list[Rule], edb: dict, method: str = "seminaive"):
    """Return (database, Stats). method: 'naive' or 'seminaive'."""
    for r in rules:
        check_safety(r)
    db = {p: set(ts) for p, ts in edb.items()}
    stats = Stats()
    for stratum in stratify(rules):
        rs = [r for r in rules if r.head.pred in stratum]
        for p in stratum:
            db.setdefault(p, set())
        if method == "naive":
            while True:                              # I_{k+1} = I_k u T_P(I_k)
                new = defaultdict(set)
                for r in rs:
                    heads = fire(r, db)
                    stats.derivations += len(heads)
                    new[r.head.pred].update(h for h in heads if h not in db[r.head.pred])
                stats.rounds += 1
                if not any(new.values()):
                    break
                stats.trace.append({p: sorted(v) for p, v in new.items() if v})
                for p, v in new.items():
                    db[p] |= v
            continue
        # semi-naive: round 0 fires every rule once; afterwards only rule
        # versions in which one recursive atom reads the previous round's delta
        delta = defaultdict(set)
        for r in rs:
            heads = fire(r, db)
            stats.derivations += len(heads)
            delta[r.head.pred].update(h for h in heads if h not in db[r.head.pred])
        stats.rounds += 1
        while any(delta.values()):
            stats.trace.append({p: sorted(v) for p, v in delta.items() if v})
            for p, v in delta.items():
                db[p] |= v
            new = defaultdict(set)
            for r in rs:
                pos = [b for b in r.body if isinstance(b, Atom) and not b.negated]
                for k, atom in enumerate(pos):
                    if atom.pred in stratum and delta.get(atom.pred):
                        heads = fire(r, db, delta, k)
                        stats.derivations += len(heads)
                        new[r.head.pred].update(h for h in heads if h not in db[r.head.pred])
            delta = new
            stats.rounds += 1
    return db, stats


def run(text: str, method: str = "seminaive"):
    rules, facts = parse(text)
    return evaluate(rules, facts, method)


ANCESTOR = """
parent(alice, carol). parent(bob, carol). parent(eve, alice).
parent(dave, bob).    parent(frank, eve).
ancestor(X, Y) :- parent(X, Y).
ancestor(X, Y) :- parent(X, Z), ancestor(Z, Y).
"""

STRATIFIED = """
node(a). node(b). node(c). node(d).
edge(a, b). edge(b, c).
reach(X, Y) :- edge(X, Y).
reach(X, Y) :- edge(X, Z), reach(Z, Y).
unreachable(X, Y) :- node(X), node(Y), X != Y, not reach(X, Y).
"""


def demo() -> None:
    for method in ("naive", "seminaive"):
        db, st = run(ANCESTOR, method)
        print(f"{method:9s}: {len(db['ancestor'])} ancestor facts, "
              f"{st.rounds} rounds, {st.derivations} derivations")
    _, st = run(ANCESTOR)
    for k, new in enumerate(st.trace, 1):
        print(f"   round {k}: {new['ancestor']}")
    rules, _ = parse(STRATIFIED)
    print("strata:", stratify(rules))
    db, _ = run(STRATIFIED)
    print("unreachable pairs:", sorted(db["unreachable"]))
    for bad in ("p(X) :- q(X), not r(X). r(X) :- q(X), not p(X). q(a).", "big(X) :- X > 3."):
        try:
            run(bad)
        except DatalogError as e:
            print("rejected:", e)


if __name__ == "__main__":
    demo()
