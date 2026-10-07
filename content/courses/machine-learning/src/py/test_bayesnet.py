"""Tests for bayesnet.py: inference, d-separation, CPT estimation and the
structure search the course asks you to describe [S14].

Reference numbers are Russell & Norvig's alarm network [S25].
"""
import itertools

import numpy as np
import pytest

import bayesnet


def test_enumeration_matches_brute_force_joint():
    bn = bayesnet.alarm_network()
    post = bn.enumeration_ask("B", {"J": 1, "M": 1})
    assert post[1] == pytest.approx(0.2842, abs=1e-3)               # AIMA Fig 14.x result
    total = sum(bn.joint(dict(zip(bn.nodes, v))) for v in itertools.product(range(2), repeat=5))
    assert total == pytest.approx(1.0)
    brute = np.zeros(2)
    for v in itertools.product(range(2), repeat=5):
        a = dict(zip(bn.nodes, v))
        if a["J"] == 1 and a["M"] == 1:
            brute[a["B"]] += bn.joint(a)
    assert np.allclose(post, brute / brute.sum())


def test_d_separation():
    bn = bayesnet.alarm_network()
    assert bn.d_separated("B", "E")                    # common effect, unobserved: blocked
    assert not bn.d_separated("B", "E", ["A"])         # explaining away
    assert not bn.d_separated("B", "E", ["J"])         # descendant of collider observed
    assert bn.d_separated("J", "M", ["A"])             # common cause observed
    assert not bn.d_separated("J", "M")
    assert bn.d_separated("B", "J", ["A"])             # chain blocked
    assert bn.markov_blanket("A") == {"B", "E", "J", "M"}


def test_parameter_estimation_recovers_cpts():
    bn = bayesnet.alarm_network()
    data = bn.sample(5000, rng=3)
    est = bayesnet.BayesianNetwork(bn.nodes, bn.parents).fit_cpts(data, alpha=0.5)
    assert np.allclose(est.cpt["J"][(1,)], bn.cpt["J"][(1,)], atol=0.15)     # A=1 is rare -> loose
    assert np.allclose(est.cpt["M"][(0,)], bn.cpt["M"][(0,)], atol=0.01)
    assert np.allclose(est.cpt["A"][(0, 0)], bn.cpt["A"][(0, 0)], atol=0.01)


# ------------------- structure learning by local search [S14] -------------------
def test_score_penalises_complexity():
    bn = bayesnet.alarm_network()
    data = bn.sample(3000, rng=5)
    true_fit = bayesnet.log_likelihood(data, bn.nodes, bn.parents)
    full = {n: list(list(bn.nodes)[:i]) for i, n in enumerate(bn.nodes)}   # fully connected DAG
    # a denser network never fits worse, but it costs more parameters
    assert bayesnet.log_likelihood(data, bn.nodes, full) >= true_fit - 1e-6
    assert bayesnet.n_params(bn.nodes, full) > bayesnet.n_params(bn.nodes, bn.parents)
    assert (bayesnet.score_structure(data, bn.nodes, bn.parents, alpha=5.0)
            > bayesnet.score_structure(data, bn.nodes, full, alpha=5.0))


def test_neighbourhood_is_one_arc_away_and_acyclic():
    nodes = {"A": 2, "B": 2, "C": 2}
    parents = {"A": [], "B": ["A"], "C": ["B"]}
    seen = list(bayesnet.neighbourhood(nodes, parents))
    assert seen
    for cand in seen:
        arcs_before = {(p, c) for c in parents for p in parents[c]}
        arcs_after = {(p, c) for c in cand for p in cand[c]}
        assert len(arcs_before ^ arcs_after) in (1, 2)        # add/remove = 1, reverse = 2
        assert bayesnet._acyclic(nodes, cand)                 # never produces a cycle


def test_hill_climbing_improves_the_score_and_lands_near_the_truth():
    bn = bayesnet.alarm_network()
    data = bn.sample(20000, rng=1)
    empty = {n: [] for n in bn.nodes}
    learned, score = bayesnet.hill_climb_structure(data, bn.nodes, alpha=2.0)
    truth = bayesnet.score_structure(data, bn.nodes, bn.parents, alpha=2.0)
    assert score > bayesnet.score_structure(data, bn.nodes, empty, alpha=2.0)
    # greedy local search gets close to the generating structure but need not reach
    # it: arc directions are not identifiable from observational data alone (note 09)
    assert score == pytest.approx(truth, rel=0.01)
    assert sum(len(p) for p in learned.values()) >= 3
