import pytest

import datalog as dl
import recursive_cte as rc

TC = """
path(X, Y) :- edge(X, Y).
path(X, Y) :- edge(X, Z), path(Z, Y).
"""
TC_NONLINEAR = """
path(X, Y) :- edge(X, Y).
path(X, Y) :- path(X, Z), path(Z, Y).
"""
SG = """
sg(X, Y) :- par(X, P), par(Y, P).
sg(X, Y) :- par(X, P), sg(P, Q), par(Y, Q).
"""


def edb():
    return {"edge": {(s, d) for s, d, _ in rc.EDGES}, "par": set(rc.PAR)}


@pytest.mark.parametrize("method", ["naive", "seminaive"])
@pytest.mark.parametrize("prog", [TC, TC_NONLINEAR])
def test_transitive_closure_equals_recursive_sql(method, prog):
    rules, _ = dl.parse(prog)
    db, _ = dl.evaluate(rules, edb(), method)
    assert db["path"] == rc.transitive_closure(rc.make_db())


@pytest.mark.parametrize("method", ["naive", "seminaive"])
def test_same_generation_equals_recursive_sql(method):
    rules, _ = dl.parse(SG)
    db, _ = dl.evaluate(rules, edb(), method)
    assert db["sg"] == rc.same_generation(rc.make_db())


def test_seminaive_does_less_work():
    rules, _ = dl.parse(TC)
    _, naive = dl.evaluate(rules, edb(), "naive")
    _, semi = dl.evaluate(rules, edb(), "seminaive")
    assert naive.rounds == semi.rounds
    assert semi.derivations < naive.derivations
    # semi-naive work = base rule once + |edge join delta_k| for every round k
    edge = edb()["edge"]
    joins = sum(1 for d in semi.trace for (z, y) in d["path"] for (x, z2) in edge if z2 == z)
    assert semi.derivations == len(edge) + joins == 35
    assert naive.derivations == 115


def test_ancestor_rounds():
    db, st = dl.run(dl.ANCESTOR)
    assert [len(r["ancestor"]) for r in st.trace] == [5, 3, 1]
    assert ("frank", "carol") in st.trace[2]["ancestor"]
    assert len(db["ancestor"]) == 9


def test_nonlinear_needs_fewer_rounds_on_a_chain():
    chain = " ".join(f"edge(n{i}, n{i + 1})." for i in range(16))
    _, lin = dl.run(chain + TC)
    _, non = dl.run(chain + TC_NONLINEAR)
    assert lin.rounds == 17 and non.rounds == 6      # path length doubles per round


def test_stratification_example():
    rules, _ = dl.parse("""
        u(X, Y) :- r(X, Z), r(Z, Y).
        v(X, Y) :- s(X, Z), s(Z, Y), not u(X, Y).
        w(X, Y) :- u(X, Y), not v(X, Y).""")
    assert dl.stratify(rules) == [{"u"}, {"v"}, {"w"}]


def test_stratified_negation_result():
    db, _ = dl.run(dl.STRATIFIED)
    nodes = "abcd"
    reach = {("a", "b"), ("b", "c"), ("a", "c")}
    assert db["unreachable"] == {(x, y) for x in nodes for y in nodes
                                 if x != y and (x, y) not in reach}


def test_not_stratifiable():
    with pytest.raises(dl.DatalogError, match="not stratifiable"):
        dl.run("p(X) :- q(X), not r(X). r(X) :- q(X), not p(X). q(a).")
    with pytest.raises(dl.DatalogError, match="not stratifiable"):
        dl.run("win(X) :- move(X, Y), not win(Y). move(a, b).")


@pytest.mark.parametrize("prog", [
    "p(X, Y) :- q(X).",                 # head variable not in body
    "p(X) :- q(X), not r(X, Y).",       # variable only under negation
    "p(X) :- q(X), Y > 3.",             # variable only in a comparison
])
def test_unsafe_rules_rejected(prog):
    with pytest.raises(dl.DatalogError, match="unsafe"):
        dl.run(prog + " q(a).")


def test_constants_comparisons_and_strings():
    db, _ = dl.run("""
        age('Ann Lee', 30). age(bob, 17). age(cid, 18).
        adult(X) :- age(X, A), A >= 18.
        older(X, Y) :- age(X, A), age(Y, B), A > B.""")
    assert db["adult"] == {("Ann Lee",), ("cid",)}
    assert ("cid", "bob") in db["older"] and len(db["older"]) == 3


def test_parse_errors():
    with pytest.raises(dl.DatalogError):
        dl.parse("p(X) :- q(X)")          # missing final dot
    with pytest.raises(dl.DatalogError):
        dl.parse("p(X :- q(X).")
