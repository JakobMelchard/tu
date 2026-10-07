import numpy as np
import pandas as pd
import pytest

import mapreduce as mr
import mr_algorithms as alg


def pandas_word_count(lines):
    words = pd.Series(" ".join(lines).lower().split()).str.strip(".,;:!?\"'()")
    return words.value_counts().to_dict()


@pytest.mark.parametrize("combine", [False, True])
@pytest.mark.parametrize("n_reducers", [1, 3, 7])
def test_word_count_against_pandas(combine, n_reducers):
    counts, st = mr.word_count(mr.TEXT, combine=combine, n_reducers=n_reducers)
    assert counts == pandas_word_count(mr.TEXT)
    assert st.input_records == len(mr.TEXT)
    assert st.map_output == sum(len(t.split()) for t in mr.TEXT)
    assert sum(st.partition_loads) == st.shuffled


def test_combiner_reduces_shuffle_not_result():
    lines = ["a a a b", "a b b", "a a c"] * 4
    plain, s0 = mr.word_count(lines, n_maps=3, combine=False)
    comb, s1 = mr.word_count(lines, n_maps=3, combine=True)
    assert plain == comb
    assert s0.shuffled == 40 and s1.shuffled == 9      # 3 map tasks x 3 distinct words
    assert s1.max_reducer_size == 3 < s0.max_reducer_size


def test_failed_map_task_is_reexecuted_with_same_result():
    good, st0 = mr.word_count(mr.TEXT)
    again, st1 = mr.word_count(mr.TEXT, fail_map={0, 2})
    assert good == again and st1.map_attempts == st0.map_attempts + 2


def test_inverted_index():
    docs = [(f"d{i}", t) for i, t in enumerate(mr.TEXT)]
    idx, _ = mr.inverted_index(docs)
    for w, ids in idx.items():
        assert ids == sorted(d for d, t in docs if w in t.lower().split())


def test_mean_combiner_pitfall():
    pairs = [("x", 1), ("x", 2), ("x", 3), ("y", 10), ("x", 6), ("y", 20)]
    ref = pd.DataFrame(pairs).groupby(0)[1].mean().to_dict()
    assert mr.mean_by_key(pairs, 2, "none")[0] == ref
    assert mr.mean_by_key(pairs, 2, "sum_count")[0] == ref
    assert mr.mean_by_key(pairs, 2, "wrong")[0]["x"] == 4.0 != ref["x"]


R = [(1, "b1"), (2, "b1"), (3, "b2"), (4, "b3"), (5, "b2")]
S = [("b1", "c1"), ("b2", "c2"), ("b2", "c3"), ("b9", "c9")]


def pandas_join():
    j = pd.DataFrame(R, columns=["a", "b"]).merge(pd.DataFrame(S, columns=["b", "c"]), on="b")
    return sorted(map(tuple, j.itertuples(index=False)))


def test_reduce_side_join():
    out, st = mr.reduce_side_join(R, S)
    assert sorted(out) == pandas_join()
    assert st.shuffled == len(R) + len(S)
    assert st.replication_rate == 1.0


def test_broadcast_join():
    out, st = mr.broadcast_join(R, S, n_maps=3)
    assert sorted(out) == pandas_join()
    assert st.shuffled == len(S) * 3


REL_R = [(1, "a", 10), (2, "b", 20), (3, "a", 30), (2, "b", 20)]
REL_S = [(2, "b", 20), (4, "c", 40)]


def test_relational_algebra():
    assert sorted(alg.selection(REL_R, lambda t: t[2] > 15)[0]) == sorted(
        t for t in REL_R if t[2] > 15)
    assert sorted(alg.projection(REL_R, [1])[0]) == [("a",), ("b",)]
    assert set(alg.union(REL_R, REL_S)[0]) == set(REL_R) | set(REL_S)
    assert set(alg.intersection(REL_R, REL_S)[0]) == set(REL_R) & set(REL_S)
    assert set(alg.difference(REL_R, REL_S)[0]) == set(REL_R) - set(REL_S)
    assert len(alg.union(REL_R, REL_S)[0]) == 4        # duplicates removed


def test_group_by_against_pandas():
    ref = pd.DataFrame(REL_R).groupby(1)[2].sum().to_dict()
    for combine in (True, False):
        assert dict(alg.group_by(REL_R, 1, 2, combine=combine)[0]) == ref


@pytest.mark.parametrize("n", [2, 3, 5])
def test_matmul_against_numpy(n):
    rng = np.random.default_rng(n)
    M, N = rng.integers(1, 5, (n, n)), rng.integers(1, 5, (n, n))   # dense, no zeros
    ref = {(i, k): int(v) for (i, k), v in np.ndenumerate(M @ N)}
    one, st = alg.matmul_one_round(M.tolist(), N.tolist())
    two, _ = alg.matmul_two_rounds(M.tolist(), N.tolist())
    assert one == ref and two == ref
    assert st.replication_rate == n                     # each entry goes to n reducers
    assert st.max_reducer_size == 2 * n                 # row i of M + column k of N
