import math

import numpy as np
import pytest
from scipy import stats

from metrics import (average_precision, bonferroni, dcg, kendall_tau, ndcg_at_k, paired_t_test,
                     precision_at_k, randomisation_test, recall_at_k, reciprocal_rank)

REL = {"x", "y"}
GRADES = {"x": 3, "y": 1}
A, B, C = ["y", "n1", "x"], ["n1", "n2", "y"], ["n1", "x", "y"]


def test_reciprocal_rank_lecture_example():            # [S7 sl. 18]
    assert [reciprocal_rank(r, REL) for r in (A, B, C)] == pytest.approx([1, 1 / 3, 1 / 2])
    assert reciprocal_rank(B, REL, k=2) == 0.0


def test_average_precision_lecture_example():          # [S7 sl. 20]: 0.83, 0.16(7), 0.58
    assert average_precision(A, REL) == pytest.approx((1 + 2 / 3) / 2)
    assert average_precision(B, REL) == pytest.approx((1 / 3) / 2)
    assert average_precision(C, REL) == pytest.approx((1 / 2 + 2 / 3) / 2)


def test_ndcg_lecture_example():                       # [S7 sl. 27]: IDCG 3.63; 0.69, 0.14, 0.66
    idcg = 3 + 1 / math.log2(3)
    assert idcg == pytest.approx(3.6309, abs=1e-4)
    assert ndcg_at_k(A, GRADES) == pytest.approx(2.5 / idcg)
    assert ndcg_at_k(B, GRADES) == pytest.approx(0.5 / idcg)
    assert ndcg_at_k(C, GRADES) == pytest.approx((3 / math.log2(3) + 0.5) / idcg)
    assert [round(ndcg_at_k(r, GRADES), 2) for r in (A, B, C)] == [0.69, 0.14, 0.66]


def test_precision_recall_and_exp_gain():
    assert precision_at_k(C, REL, 2) == 0.5 and recall_at_k(C, REL, 2) == 0.5
    assert dcg([3, 1], exp_gain=True) == pytest.approx(7 + 1 / math.log2(3))
    assert ndcg_at_k(["x", "y"], GRADES) == 1.0 and ndcg_at_k(["n"], GRADES) == 0.0


def test_ap_equals_sklearn_when_all_relevant_retrieved():
    from sklearn.metrics import average_precision_score

    rng = np.random.default_rng(0)
    for _ in range(20):
        y = rng.integers(0, 2, 30)
        y[0] = 1
        scores = rng.random(30)
        ranking = [str(i) for i in np.argsort(-scores)]
        rel = {str(i) for i in np.flatnonzero(y)}
        assert average_precision(ranking, rel) == pytest.approx(average_precision_score(y, scores))


def test_ndcg_equals_sklearn_with_linear_gain():
    from sklearn.metrics import ndcg_score

    rng = np.random.default_rng(1)
    for _ in range(20):
        g = rng.integers(0, 4, 25)
        g[3] = 3
        s = rng.random(25)
        ranking = [str(i) for i in np.argsort(-s)]
        grades = {str(i): int(v) for i, v in enumerate(g) if v > 0}
        assert ndcg_at_k(ranking, grades, 10) == pytest.approx(ndcg_score([g], [s], k=10))


def test_paired_t_test_hand_and_scipy():
    a, b = [0.5, 0.6, 0.7, 0.4], [0.4, 0.5, 0.5, 0.4]
    t, p = paired_t_test(a, b)
    # d = (.1,.1,.2,0): mean .1, sd sqrt(.02/3), t = .1/(sd/2) = sqrt(6)
    assert t == pytest.approx(math.sqrt(6))
    ref = stats.ttest_rel(a, b)
    assert t == pytest.approx(ref.statistic) and p == pytest.approx(ref.pvalue)
    assert p == pytest.approx(0.0917, abs=1e-4)


def test_randomisation_test_agrees_with_exact_enumeration():
    a, b = np.array([0.5, 0.6, 0.7, 0.4, 0.9]), np.array([0.4, 0.5, 0.5, 0.4, 0.6])
    d = a - b
    signs = np.array(np.meshgrid(*[[-1, 1]] * 5)).reshape(5, -1).T
    exact = np.mean(np.abs((signs * d).mean(1)) >= abs(d.mean()) - 1e-12)   # all-plus / all-minus, times 2 for the zero difference
    assert exact == pytest.approx(4 / 32)
    assert randomisation_test(a, b, 40000) == pytest.approx(exact, abs=0.01)


def test_bonferroni_and_kendall():
    assert bonferroni([0.01, 0.04, 0.5]) == pytest.approx([0.03, 0.12, 1.0])
    x, y = [0.3, 0.2, 0.25, 0.1], [0.31, 0.18, 0.22, 0.15]
    assert kendall_tau(x, y) == pytest.approx(stats.kendalltau(x, y).statistic)
    assert kendall_tau([1, 2, 3], [3, 2, 1]) == -1.0
