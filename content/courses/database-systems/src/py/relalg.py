"""A small relational-algebra evaluator over Python sets, plus tuple and domain
relational calculus as set comprehensions (note 05).

A Relation is a schema (tuple of attribute names) and a frozenset of tuples:
set semantics, no duplicates, no NULL (except in the outer-join extension,
where Python None stands for NULL).  Operators follow [S6] ch. 2 and [S10]
ch. 4-5:

  basic      select, project, rename, union, difference, product
  derived    intersect = R - (R - S), natural_join, theta_join, semijoin,
             antijoin, division (R / S = pi(R) - pi((pi(R) x S) - R))
  extended   left_outer_join (NULL padding), group_count (gamma)

`to_sqlite` loads relations into an sqlite3 connection so every result can be
cross-checked against SQL (the tests do this); `trc`/`drc` evaluate calculus
queries over the active domain, which is how the note shows that safe calculus
and algebra express the same queries (Codd's theorem, [S10] ch. 5).
"""
import sqlite3
from itertools import product as _product


class Relation:
    def __init__(self, schema, rows=()):
        self.schema = tuple(schema)
        self.rows = frozenset(tuple(r) for r in rows)
        assert all(len(r) == len(self.schema) for r in self.rows), "arity mismatch"

    def __eq__(self, other):
        """Equal up to column order."""
        if set(self.schema) != set(other.schema):
            return False
        return self.rows == project(other, self.schema).rows

    def __hash__(self):
        return hash((frozenset(self.schema), len(self.rows)))

    def __len__(self):
        return len(self.rows)

    def __repr__(self):
        return f"Relation({self.schema}, {sorted(self.rows, key=repr)})"

    def dicts(self):
        return [dict(zip(self.schema, r)) for r in self.rows]

    def show(self, name="result"):
        print(f"{name}({', '.join(self.schema)})")
        for r in sorted(self.rows, key=repr):
            print("   ", r)


def select(R, pred):
    """sigma_pred(R); pred takes a dict attribute -> value."""
    return Relation(R.schema, [r for r in R.rows if pred(dict(zip(R.schema, r)))])


def project(R, attrs):
    """pi_attrs(R); duplicates vanish because rows is a set."""
    idx = [R.schema.index(a) for a in attrs]
    return Relation(attrs, [tuple(r[i] for i in idx) for r in R.rows])


def rename(R, mapping=None, prefix=None):
    """rho: rename attributes by dict, or prefix all of them ('s.' style)."""
    if prefix is not None:
        return Relation([f"{prefix}.{a}" for a in R.schema], R.rows)
    return Relation([mapping.get(a, a) for a in R.schema], R.rows)


def _compatible(R, S):
    assert set(R.schema) == set(S.schema), "union-incompatible"
    return project(S, R.schema)


def union(R, S):
    return Relation(R.schema, R.rows | _compatible(R, S).rows)


def difference(R, S):
    return Relation(R.schema, R.rows - _compatible(R, S).rows)


def intersect(R, S):
    return difference(R, difference(R, S))          # derived, not primitive


def product(R, S):
    assert not set(R.schema) & set(S.schema), "rename first"
    return Relation(R.schema + S.schema, [r + s for r in R.rows for s in S.rows])


def theta_join(R, S, pred):
    return select(product(R, S), pred)


def natural_join(R, S):
    """Equate the common attributes, keep one copy of each."""
    common = [a for a in R.schema if a in S.schema]
    rest = [a for a in S.schema if a not in common]
    ri = [R.schema.index(a) for a in common]
    si = [S.schema.index(a) for a in common]
    ki = [S.schema.index(a) for a in rest]
    out = [r + tuple(s[i] for i in ki) for r in R.rows for s in S.rows
           if all(r[a] == s[b] for a, b in zip(ri, si))]
    return Relation(R.schema + tuple(rest), out)


def semijoin(R, S):
    """R semijoin S = pi_R(R join S)."""
    return project(natural_join(R, S), R.schema)


def antijoin(R, S):
    return difference(R, semijoin(R, S))


def division(R, S):
    """R / S: the X-values of R paired with *every* S-tuple, X = attrs(R) - attrs(S)."""
    X = tuple(a for a in R.schema if a not in S.schema)
    candidates = project(R, X)
    missing = difference(project(product(candidates, S), R.schema), R)
    return difference(candidates, project(missing, X))


def left_outer_join(R, S):
    """R left-outer-join S: dangling R-tuples padded with None (NULL)."""
    J = natural_join(R, S)
    extra = [a for a in S.schema if a not in R.schema]
    dangling = antijoin(R, S)
    return Relation(J.schema, J.rows | {r + (None,) * len(extra) for r in dangling.rows})


def group_count(R, by, name="cnt"):
    """gamma_{by; count(*)}(R)."""
    counts = {}
    for r in R.dicts():
        k = tuple(r[a] for a in by)
        counts[k] = counts.get(k, 0) + 1
    return Relation(tuple(by) + (name,), [k + (c,) for k, c in counts.items()])


def active_domain(*rels):
    return {v for R in rels for r in R.rows for v in r}


def trc(R, cond):
    """{t | t in R and cond(t)}: tuple calculus with t ranging over R (safe by construction)."""
    return Relation(R.schema, [r for r in R.rows if cond(dict(zip(R.schema, r)))])


def drc(head, formula, dom):
    """{<x1..xk> | formula(x1..xk)} with every variable ranging over the active
    domain `dom`; equal to the unrestricted answer exactly for domain-independent
    (safe) formulas."""
    return Relation(head, [xs for xs in _product(sorted(dom, key=repr), repeat=len(head)) if formula(*xs)])


def to_sqlite(con, name, R):
    cols = ", ".join(f'"{a}"' for a in R.schema)
    con.execute(f'CREATE TABLE "{name}" ({cols})')
    con.executemany(f'INSERT INTO "{name}" VALUES ({", ".join("?" * len(R.schema))})', R.rows)


def from_sql(con, sql, schema):
    return Relation(schema, set(con.execute(sql).fetchall()))


def sample_db():
    """Students, courses and who passed what; used by demo, tests and note 05."""
    S = Relation(("sid", "name", "sem"), [(1, "Ada", 2), (2, "Bob", 4), (3, "Cyd", 2), (4, "Dan", 6), (5, "Eve", 2)])
    C = Relation(("cid", "title", "ects"), [("DB", "Databases", 6), ("AL", "Algebra", 3), ("TH", "Theory", 6)])
    P = Relation(("sid", "cid"), [(1, "DB"), (1, "AL"), (1, "TH"), (2, "DB"), (2, "TH"), (3, "AL"), (4, "DB")])
    return S, C, P


if __name__ == "__main__":
    S, C, P = sample_db()
    six = project(select(C, lambda t: t["ects"] == 6), ("cid",))
    six.show("pi_cid sigma_ects=6 (C)")
    division(P, six).show("P / six   (passed every 6-ECTS course)")
    project(antijoin(S, P), ("name",)).show("students with no pass")
    left_outer_join(S, P).show("S left outer join P")
    group_count(P, ("sid",)).show("gamma_sid count(*) (P)")
    dom = active_domain(P, six)
    q = drc(("x",), lambda x: any((x, "DB") == r for r in P.rows)
            and all((x, c) in P.rows for (c,) in six.rows), dom)
    q.show("DRC {<x> | P(x,'DB') and forall c (six(c) -> P(x,c))}")
    con = sqlite3.connect(":memory:")
    for n, R in (("P", P), ("six", six)):
        to_sqlite(con, n, R)
    sql = ("SELECT DISTINCT sid FROM P p WHERE NOT EXISTS (SELECT * FROM six c WHERE NOT EXISTS "
           "(SELECT * FROM P q WHERE q.sid = p.sid AND q.cid = c.cid))")
    print("sqlite double NOT EXISTS agrees:", from_sql(con, sql, ("sid",)) == division(P, six))
