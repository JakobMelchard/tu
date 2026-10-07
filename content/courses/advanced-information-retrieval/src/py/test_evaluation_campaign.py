import numpy as np
import pytest

from evaluation_campaign import (bpref, kendall_tau, leaderboard, leave_one_out, pool, pooled_qrels, rank_of,
                                 simulate)
from metrics import precision_at_k


@pytest.fixture(scope="module")
def camp():
    return simulate(seed=0)


def test_pool_is_union_of_top_depth(camp):
    judged = pool(camp.runs, ["lex00", "lex01"], 5)
    for q in range(3):
        assert judged[q] == set(camp.runs["lex00"][q][:5]) | set(camp.runs["lex01"][q][:5])


def test_precision_at_depth_is_exact_for_contributing_runs(camp):
    """Every document a contributing run has in its top-depth is judged, so P@k (k <= depth) is unbiased."""
    parts = [s for s in camp.runs if s != "novel"]
    qp = pooled_qrels(camp, pool(camp.runs, parts, 20))
    for s in parts:
        for q in camp.truth:
            r = [str(d) for d in camp.runs[s][q]]
            assert precision_at_k(r, {str(d) for d in qp[q]}, 10) == precision_at_k(r, {str(d) for d in camp.truth[q]}, 10)


def test_pool_bias_against_the_non_contributing_run(camp):
    parts = [s for s in camp.runs if s != "novel"]
    qp = pooled_qrels(camp, pool(camp.runs, parts, 20))
    full, pooled = leaderboard(camp, camp.truth), leaderboard(camp, qp)
    assert rank_of(pooled, "novel") >= rank_of(full, "novel") + 3
    # pooled MAP inflates contributing runs (smaller |rel(q)|) and deflates the novel one
    assert dict(pooled)["lex09"] > dict(full)["lex09"] and dict(pooled)["novel"] < dict(full)["novel"]
    # the order among contributors is preserved
    fd, pd = dict(full), dict(pooled)
    assert kendall_tau([fd[s] for s in parts], [pd[s] for s in parts]) > 0.9


def test_including_the_run_in_the_pool_removes_most_of_the_bias(camp):
    qp = pooled_qrels(camp, pool(camp.runs, list(camp.runs), 20))
    full, pooled = leaderboard(camp, camp.truth), leaderboard(camp, qp)
    assert abs(rank_of(pooled, "novel") - rank_of(full, "novel")) <= 1


def test_bpref_hand_computed_and_robust_to_unjudged():
    # R = 2 relevant {1, 2}; judged non-relevant {7, 8}; 9 unjudged
    assert bpref([7, 1, 9, 8, 2], {1, 2}, {1, 2, 7, 8}) == pytest.approx(((1 - 1 / 2) + (1 - 2 / 2)) / 2)
    # inserting unjudged documents anywhere does not change bpref
    assert bpref([7, 9, 9, 1, 8, 9, 2], {1, 2}, {1, 2, 7, 8}) == bpref([7, 1, 8, 2], {1, 2}, {1, 2, 7, 8})


def test_leave_one_run_out_drop_is_small_but_positive(camp):
    parts = [s for s in camp.runs if s != "novel"]
    loo = leave_one_out(camp, parts, 20)
    assert 0 < np.mean(list(loo.values())) < 0.05
