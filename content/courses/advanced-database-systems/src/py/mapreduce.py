"""A local, single-process MapReduce framework with explicit phases, note 05.

Model [S16 section 2], [S17 2.2]:
    map:     (k1, v1)          -> list[(k2, v2)]         one call per input record
    combine: (k2, list[v2])    -> list[(k2, v2)]         optional, per map task
    shuffle: partition by hash(k2) mod R, group by k2, sort keys
    reduce:  (k2, list[v2])    -> list[output]           one call per key

Cost measures [S17 2.5-2.6]: communication cost = number of key-value pairs
moved from map to reduce tasks (the shuffle); replication rate r = map-output
pairs / input records; reducer size q = the longest value list of one key.
Fault tolerance is simulated: a failed map task is simply re-executed, which
is correct because map functions are deterministic and side-effect free [S16 3.3].

Run: python mapreduce.py
"""
from __future__ import annotations

import zlib
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Callable, Iterable


def stable_hash(key) -> int:
    """Python's hash() of str is salted per process; the shuffle must not be."""
    return zlib.crc32(repr(key).encode())


@dataclass
class JobStats:
    input_records: int = 0
    map_output: int = 0          # pairs emitted by mappers (before combining)
    shuffled: int = 0            # pairs sent to reducers = communication cost
    reducer_sizes: dict = field(default_factory=dict)   # key -> len(values)
    partition_loads: list = field(default_factory=list)  # pairs per reduce task
    map_attempts: int = 0

    @property
    def replication_rate(self) -> float:
        return self.map_output / self.input_records if self.input_records else 0.0

    @property
    def max_reducer_size(self) -> int:
        return max(self.reducer_sizes.values(), default=0)


def run_job(splits: list[list], mapper: Callable, reducer: Callable | None = None,
            combiner: Callable | None = None, n_reducers: int = 3,
            fail_map: Iterable[int] = ()) -> tuple[list, JobStats]:
    """Run one job. `splits` = input split per map task. reducer=None -> map-only."""
    st, fail = JobStats(), set(fail_map)
    task_outputs = []
    for t, split in enumerate(splits):
        attempts = 2 if t in fail else 1          # first attempt lost with its worker
        for _ in range(attempts):
            st.map_attempts += 1
            out = [kv for rec in split for kv in mapper(rec)]
        st.input_records += len(split)
        st.map_output += len(out)
        if combiner is not None:                  # local mini-reduce on this task only
            local = defaultdict(list)
            for k, v in out:
                local[k].append(v)
            out = [kv for k in local for kv in combiner(k, local[k])]
        task_outputs.append(out)
    if reducer is None:
        return [v for out in task_outputs for _, v in out], st
    parts = [defaultdict(list) for _ in range(n_reducers)]
    for out in task_outputs:                       # shuffle: each pair crosses the network once
        for k, v in out:
            parts[stable_hash(k) % n_reducers][k].append(v)
            st.shuffled += 1
    result = []
    for part in parts:
        st.partition_loads.append(sum(len(v) for v in part.values()))
        for k in sorted(part, key=repr):           # sort phase: keys arrive ordered
            st.reducer_sizes[k] = len(part[k])
            result.extend(reducer(k, part[k]))
    return result, st


def split(records: list, n: int) -> list[list]:
    """Cut the input into n contiguous splits (HDFS blocks in real Hadoop)."""
    size = -(-len(records) // n)
    return [records[i:i + size] for i in range(0, len(records), size)]


# --- word count ----------------------------------------------------------
def wc_map(line: str):
    for w in line.lower().split():
        yield w.strip(".,;:!?\"'()"), 1


def wc_reduce(word, counts):
    yield word, sum(counts)


def wc_combine(word, counts):
    yield word, sum(counts)                       # sum is associative and commutative


def word_count(lines: list[str], n_maps: int = 3, combine: bool = True, **kw):
    out, st = run_job(split(lines, n_maps), wc_map, wc_reduce,
                      wc_combine if combine else None, **kw)
    return dict(out), st


# --- inverted index ------------------------------------------------------
def inverted_index(docs: list[tuple[str, str]], n_maps: int = 2):
    def m(doc):
        doc_id, text = doc
        for w in set(text.lower().split()):
            yield w, doc_id

    def r(w, ids):
        yield w, sorted(ids)
    out, st = run_job(split(docs, n_maps), m, r)
    return dict(out), st


# --- averages: the combiner pitfall --------------------------------------
def mean_by_key(pairs: list[tuple], n_maps: int = 3, mode: str = "sum_count"):
    """mode 'none': no combiner. 'wrong': combiner averages (mean of means is not
    the mean). 'sum_count': map emits (x, 1), combiner adds componentwise."""
    def m(p):
        yield p[0], (p[1], 1)

    def wrong(k, vs):
        yield k, (sum(x for x, _ in vs) / len(vs), 1)

    def right(k, vs):
        yield k, (sum(x for x, _ in vs), sum(c for _, c in vs))

    def r(k, vs):
        yield k, sum(x for x, _ in vs) / sum(c for _, c in vs)
    comb = {"none": None, "wrong": wrong, "sum_count": right}[mode]
    out, st = run_job(split(pairs, n_maps), m, r, comb)
    return dict(out), st


# --- joins ---------------------------------------------------------------
def reduce_side_join(R: list[tuple], S: list[tuple], r_key: int = 1, s_key: int = 0,
                     n_maps: int = 2):
    """R(a, b) join S(b, c) on R.b = S.b. Map tags each tuple with its relation;
    the reducer for join value b pairs every R-tuple with every S-tuple.
    Communication = |R| + |S| [S17 2.5 Example 2.14]."""
    tagged = [("R", t) for t in R] + [("S", t) for t in S]

    def m(rec):
        tag, t = rec
        yield (t[r_key] if tag == "R" else t[s_key]), (tag, t)

    def r(b, vals):
        rs = [t for tag, t in vals if tag == "R"]
        ss = [t for tag, t in vals if tag == "S"]
        for x in rs:
            for y in ss:
                yield x + tuple(v for i, v in enumerate(y) if i != s_key)
    return run_job(split(tagged, n_maps), m, r)


def broadcast_join(R: list[tuple], S_small: list[tuple], r_key: int = 1, s_key: int = 0,
                   n_maps: int = 2):
    """Map-side (broadcast) join: every map task loads S into a hash table and
    probes it with its split of R. No shuffle; but S is shipped to every map
    task, so the communication is |S| x #map tasks."""
    table = defaultdict(list)
    for y in S_small:
        table[y[s_key]].append(y)

    def m(x):
        for y in table.get(x[r_key], []):
            yield None, x + tuple(v for i, v in enumerate(y) if i != s_key)
    splits = split(R, n_maps)
    out, st = run_job(splits, m, None)
    st.shuffled = len(S_small) * len(splits)       # the broadcast is the traffic
    return out, st


TEXT = ["the quick brown fox", "jumps over the lazy dog",
        "the dog barks", "the fox runs", "a lazy afternoon for the dog"]


def demo() -> None:
    for combine in (False, True):
        counts, st = word_count(TEXT, combine=combine)
        print(f"word count, combiner={combine!s:5}: the={counts['the']} dog={counts['dog']} "
              f"map output={st.map_output} shuffled={st.shuffled} q={st.max_reducer_size}")
    idx, _ = inverted_index([(f"d{i}", t) for i, t in enumerate(TEXT)])
    print("inverted index: dog ->", idx["dog"], " lazy ->", idx["lazy"])
    pairs = [("x", 1), ("x", 2), ("x", 3), ("y", 10), ("x", 6), ("y", 20)]
    for mode in ("none", "wrong", "sum_count"):
        print(f"mean by key, combiner={mode:9s}:", mean_by_key(pairs, n_maps=2, mode=mode)[0])
    R = [(1, "b1"), (2, "b1"), (3, "b2"), (4, "b3")]
    S = [("b1", "c1"), ("b2", "c2"), ("b2", "c3")]
    out, st = reduce_side_join(R, S)
    print(f"reduce-side join: {sorted(out)}  communication={st.shuffled}")
    out, st = broadcast_join(R, S)
    print(f"broadcast join:   {sorted(out)}  communication={st.shuffled}")
    counts, st = word_count(TEXT, fail_map={1})
    print(f"map task 1 failed once: {st.map_attempts} attempts for 3 tasks, same result "
          f"{counts == word_count(TEXT)[0]}")


if __name__ == "__main__":
    demo()
