import random
import sqlite3

import pytest

import relalg as ra
from relalg import Relation


def rand_rel(rng, schema, n, dom=4):
    return Relation(schema, {tuple(rng.randrange(dom) for _ in schema) for _ in range(n)})


@pytest.fixture(params=range(25))
def world(request):
    rng = random.Random(request.param)
    R = rand_rel(rng, ("a", "b"), rng.randint(0, 10))
    S = rand_rel(rng, ("b", "c"), rng.randint(0, 10))
    T = rand_rel(rng, ("a", "b"), rng.randint(0, 10))
    D = rand_rel(rng, ("b",), rng.randint(1, 3))
    con = sqlite3.connect(":memory:")
    for name, rel in (("R", R), ("S", S), ("T", T), ("D", D)):
        ra.to_sqlite(con, name, rel)
    return R, S, T, D, con


def q(con, sql, schema):
    return ra.from_sql(con, sql, schema)


def test_operators_against_sqlite(world):
    R, S, T, D, con = world
    assert ra.select(R, lambda t: t["a"] > t["b"]) == q(con, "SELECT * FROM R WHERE a > b", ("a", "b"))
    assert ra.project(R, ("a",)) == q(con, "SELECT DISTINCT a FROM R", ("a",))
    assert ra.union(R, T) == q(con, "SELECT * FROM R UNION SELECT * FROM T", ("a", "b"))
    assert ra.difference(R, T) == q(con, "SELECT * FROM R EXCEPT SELECT * FROM T", ("a", "b"))
    assert ra.intersect(R, T) == q(con, "SELECT * FROM R INTERSECT SELECT * FROM T", ("a", "b"))
    assert ra.natural_join(R, S) == q(con, "SELECT DISTINCT a, R.b, c FROM R JOIN S ON R.b = S.b",
                                      ("a", "b", "c"))
    assert ra.semijoin(R, S) == q(con, "SELECT * FROM R WHERE b IN (SELECT b FROM S)", ("a", "b"))
    assert ra.antijoin(R, S) == q(con, "SELECT * FROM R WHERE NOT EXISTS "
                                       "(SELECT * FROM S WHERE S.b = R.b)", ("a", "b"))
    assert ra.left_outer_join(R, S) == q(con, "SELECT DISTINCT a, R.b, c FROM R LEFT JOIN S "
                                              "ON R.b = S.b", ("a", "b", "c"))
    assert ra.group_count(R, ("a",)) == q(con, "SELECT a, count(*) FROM R GROUP BY a", ("a", "cnt"))


def test_division_three_ways(world):
    R, S, T, D, con = world
    by_algebra = ra.division(R, D)
    by_sql = q(con, "SELECT DISTINCT a FROM R r WHERE NOT EXISTS (SELECT * FROM D WHERE NOT EXISTS "
                    "(SELECT * FROM R r2 WHERE r2.a = r.a AND r2.b = D.b))", ("a",))
    by_count = q(con, "SELECT a FROM R WHERE b IN (SELECT b FROM D) GROUP BY a "
                      "HAVING count(DISTINCT b) = (SELECT count(*) FROM D)", ("a",))
    dom = ra.active_domain(R, D)
    by_drc = ra.drc(("a",), lambda a: any(r[0] == a for r in R.rows)
                    and all((a, b) in R.rows for (b,) in D.rows), dom)
    assert by_algebra == by_sql == by_count == by_drc


def test_algebraic_identities(world):
    R, S, T, D, con = world
    p = lambda t: t["a"] == 1
    # selection pushdown: sigma_p(R join S) = sigma_p(R) join S when p mentions only R
    assert ra.select(ra.natural_join(R, S), p) == ra.natural_join(ra.select(R, p), S)
    # join is commutative up to column order
    assert ra.natural_join(R, S) == ra.natural_join(S, R)
    # intersection is derivable: R cap T = R - (R - T) = T - (T - R)
    assert ra.intersect(R, T) == ra.intersect(T, R)
    # projection does NOT distribute over difference in general; over union it does
    assert ra.project(ra.union(R, T), ("a",)) == ra.union(ra.project(R, ("a",)), ra.project(T, ("a",)))
    # division undone: (R / D) x D is a subset of R
    back = ra.product(ra.division(R, D), D)
    assert back.rows <= ra.project(R, back.schema).rows


def test_projection_difference_counterexample():
    R = Relation(("a", "b"), [(1, 1), (1, 2)])
    T = Relation(("a", "b"), [(1, 1)])
    left = ra.project(ra.difference(R, T), ("a",))
    right = ra.difference(ra.project(R, ("a",)), ra.project(T, ("a",)))
    assert len(left) == 1 and len(right) == 0


def test_trc_equals_select():
    S, C, P = ra.sample_db()
    assert ra.trc(S, lambda t: t["sem"] == 2) == ra.select(S, lambda t: t["sem"] == 2)


def test_unsafe_query_depends_on_domain():
    """{x | not P(x,'DB')} changes with the domain; restricted to the active domain it is finite."""
    S, C, P = ra.sample_db()
    f = lambda x: (x, "DB") not in P.rows
    small = ra.drc(("x",), f, ra.active_domain(P))
    bigger = ra.drc(("x",), f, ra.active_domain(P) | {99})
    assert small != bigger


def test_sample_division():
    S, C, P = ra.sample_db()
    six = ra.project(ra.select(C, lambda t: t["ects"] == 6), ("cid",))
    assert ra.division(P, six) == Relation(("sid",), [(1,), (2,)])
