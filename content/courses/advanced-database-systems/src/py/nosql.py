"""Building blocks of distributed key-value stores, notes 07 and 08.

  ConsistentHashRing  partitioning with virtual nodes and preference lists
                      [S32], [S24 4.2-4.3]
  QuorumStore         N replicas, write to W, read from R; R + W > N makes every
                      read set intersect every write set [S24 4.5]
  VectorClock         causality between versions, Dynamo's D1..D5 example [S24 4.4]
  LSMTree             memtable + immutable sorted runs (SSTables), Bloom filters,
                      tombstones, merge compaction [S33], [S25 5.3-5.4]
  rle / dictionary_encode / bitmap_encode   column-store compression [S40]

Toy code: single process, no network, no persistence.
Run: python nosql.py
"""
from __future__ import annotations

import bisect
import hashlib
import heapq
from itertools import combinations


def h32(s: str) -> int:
    return int.from_bytes(hashlib.md5(s.encode()).digest()[:4], "big")


class ConsistentHashRing:
    """Nodes and keys hash onto a circle [0, 2^32). A key belongs to the first
    node clockwise. Adding a node moves only the keys between it and its
    predecessor: about 1/(m+1) of them, versus m/(m+1) for hash(key) mod m."""

    def __init__(self, nodes=(), vnodes: int = 16):
        self.vnodes, self.ring = vnodes, []          # sorted [(position, node)]
        for n in nodes:
            self.add(n)

    def add(self, node: str) -> None:
        for v in range(self.vnodes):
            bisect.insort(self.ring, (h32(f"{node}#{v}"), node))

    def remove(self, node: str) -> None:
        self.ring = [(p, n) for p, n in self.ring if n != node]

    def owner(self, key: str) -> str:
        i = bisect.bisect(self.ring, (h32(key), "￿")) % len(self.ring)
        return self.ring[i][1]

    def preference_list(self, key: str, n: int) -> list[str]:
        """First n *distinct physical* nodes clockwise (virtual nodes of one
        machine are skipped), as in Dynamo."""
        i = bisect.bisect(self.ring, (h32(key), "￿"))
        out = []
        for k in range(len(self.ring)):
            node = self.ring[(i + k) % len(self.ring)][1]
            if node not in out:
                out.append(node)
                if len(out) == n:
                    break
        return out


def moved_fraction(keys, before, after) -> float:
    return sum(before(k) != after(k) for k in keys) / len(keys)


class QuorumStore:
    """Replica i of key k is preference_list(k, N)[i]. A put succeeds after W
    replicas stored it; here it reaches *exactly* the first W live replicas
    (the worst case: the others missed the message). A get asks R live
    replicas and returns the value with the highest version."""

    def __init__(self, nodes, N=3, R=2, W=2, vnodes=16):
        self.N, self.R, self.W = N, R, W
        self.ring = ConsistentHashRing(nodes, vnodes)
        self.data = {n: {} for n in nodes}           # node -> key -> (version, value)
        self.down: set[str] = set()
        self.clock = 0

    def replicas(self, key):
        return self.ring.preference_list(key, self.N)

    def put(self, key, value) -> list[str]:
        live = [n for n in self.replicas(key) if n not in self.down]
        if len(live) < self.W:
            raise RuntimeError(f"only {len(live)} of W={self.W} replicas reachable")
        self.clock += 1
        for n in live[:self.W]:
            self.data[n][key] = (self.clock, value)
        return live[:self.W]

    def get(self, key, read_from=None, repair=False):
        live = [n for n in self.replicas(key) if n not in self.down]
        targets = read_from or live[-self.R:]         # default: the last R, worst case
        if len(targets) < self.R:
            raise RuntimeError(f"only {len(targets)} of R={self.R} replicas reachable")
        seen = {n: self.data[n].get(key, (0, None)) for n in targets}
        newest = max(seen.values(), key=lambda vv: vv[0])
        if repair:                                    # read repair
            for n, vv in seen.items():
                if vv[0] < newest[0]:
                    self.data[n][key] = newest
        return newest[1]


def quorums_always_intersect(N: int, R: int, W: int) -> bool:
    """Exhaustive check over all write sets of size W and read sets of size R."""
    reps = range(N)
    return all(set(w) & set(r) for w in combinations(reps, W) for r in combinations(reps, R))


class VectorClock:
    def __init__(self, counts=None):
        self.c = {k: v for k, v in (counts or {}).items() if v}

    def tick(self, node: str) -> "VectorClock":
        d = dict(self.c)
        d[node] = d.get(node, 0) + 1
        return VectorClock(d)

    def merge(self, other: "VectorClock") -> "VectorClock":
        return VectorClock({k: max(self.c.get(k, 0), other.c.get(k, 0))
                            for k in self.c.keys() | other.c.keys()})

    def __le__(self, other) -> bool:
        return all(v <= other.c.get(k, 0) for k, v in self.c.items())

    def compare(self, other) -> str:
        le, ge = self <= other, other <= self
        return "equal" if le and ge else "before" if le else "after" if ge else "concurrent"

    def __repr__(self) -> str:
        return "[" + ", ".join(f"{k}:{v}" for k, v in sorted(self.c.items())) + "]"


def dynamo_example() -> dict[str, VectorClock]:
    """[S24 4.4, Figure 3]: Sx writes twice, then Sy and Sz each handle a write
    based on D2, then Sx reconciles."""
    D1 = VectorClock().tick("Sx")
    D2 = D1.tick("Sx")
    D3 = D2.tick("Sy")
    D4 = D2.tick("Sz")
    D5 = D3.merge(D4).tick("Sx")
    return {"D1": D1, "D2": D2, "D3": D3, "D4": D4, "D5": D5}


TOMBSTONE = object()


class Bloom:
    """m-bit Bloom filter with k hash functions: no false negatives, some false positives."""

    def __init__(self, keys, m=128, k=3):
        self.m, self.k, self.bits = m, k, 0
        for key in keys:
            for i in range(k):
                self.bits |= 1 << (h32(f"{i}:{key}") % m)

    def __contains__(self, key) -> bool:
        return all(self.bits >> (h32(f"{i}:{key}") % self.m) & 1 for i in range(self.k))


class LSMTree:
    """Writes go to an in-memory memtable; when it holds `limit` keys it is
    written out as an immutable sorted run (SSTable). Reads check memtable, then
    runs newest first. Compaction merges runs; newest version wins; tombstones
    are dropped only in a full merge (older runs might still hold the key)."""

    def __init__(self, limit=4, max_runs=4):
        self.limit, self.max_runs = limit, max_runs
        self.mem: dict = {}
        self.runs: list[tuple[list, Bloom]] = []      # newest first
        self.probes = 0                               # runs actually searched

    def put(self, key, value) -> None:
        self.mem[key] = value
        if len(self.mem) >= self.limit:
            self.flush()

    def delete(self, key) -> None:
        self.put(key, TOMBSTONE)

    def flush(self) -> None:
        if self.mem:
            run = sorted(self.mem.items())
            self.runs.insert(0, (run, Bloom(k for k, _ in run)))
            self.mem = {}
        if len(self.runs) > self.max_runs:
            self.compact()

    def get(self, key):
        if key in self.mem:
            v = self.mem[key]
            return None if v is TOMBSTONE else v
        for run, bloom in self.runs:
            if key not in bloom:
                continue
            self.probes += 1
            i = bisect.bisect_left(run, (key,))
            if i < len(run) and run[i][0] == key:
                return None if run[i][1] is TOMBSTONE else run[i][1]
        return None

    def compact(self) -> None:
        """Full k-way merge of all runs (sorted inputs -> linear time)."""
        streams = [[(k, age, v) for k, v in run] for age, (run, _) in enumerate(self.runs)]
        merged, last = [], None
        for k, _, v in heapq.merge(*streams):         # same key: smallest age = newest first
            if k != last:
                last = k
                if v is not TOMBSTONE:
                    merged.append((k, v))
        self.runs = [(merged, Bloom(k for k, _ in merged))] if merged else []

    def items(self) -> dict:
        out = {}
        for run, _ in reversed(self.runs):
            out.update(run)
        out.update(self.mem)
        return {k: v for k, v in out.items() if v is not TOMBSTONE}


def rle(col):
    """Run-length encoding: [(value, run length)]. Good on sorted columns."""
    out = []
    for x in col:
        if out and out[-1][0] == x:
            out[-1] = (x, out[-1][1] + 1)
        else:
            out.append((x, 1))
    return out


def dictionary_encode(col):
    codes = {v: i for i, v in enumerate(sorted(set(col)))}
    return list(codes), [codes[x] for x in col]


def bitmap_encode(col):
    """One bit vector per distinct value; good for few distinct values."""
    return {v: "".join("1" if x == v else "0" for x in col) for v in sorted(set(col))}


def demo() -> None:
    keys = [f"user{i}" for i in range(2000)]
    ring4 = ConsistentHashRing(["A", "B", "C", "D"], vnodes=64)
    ring5 = ConsistentHashRing(["A", "B", "C", "D", "E"], vnodes=64)
    print(f"add 5th node: ring moves {moved_fraction(keys, ring4.owner, ring5.owner):.2f} "
          f"of keys, mod-hashing moves "
          f"{moved_fraction(keys, lambda k: h32(k) % 4, lambda k: h32(k) % 5):.2f}")
    for N, R, W in [(3, 2, 2), (3, 1, 3), (3, 1, 1), (5, 2, 3)]:
        print(f"N={N} R={R} W={W}: R+W>N={R + W > N}, "
              f"every read meets every write: {quorums_always_intersect(N, R, W)}")
    s = QuorumStore(["A", "B", "C", "D", "E"], N=3, R=1, W=1)
    s.put("cart", "v1")
    s.put("cart", "v2")
    print(f"N=3 R=1 W=1: read from the replica the writes missed -> {s.get('cart')!r}; "
          f"with read_from the written one -> {s.get('cart', read_from=s.put('cart', 'v3'))!r}")
    D = dynamo_example()
    print("vector clocks:", D, "| D3 vs D4:", D["D3"].compare(D["D4"]),
          "| D5 vs D3:", D["D5"].compare(D["D3"]))
    t = LSMTree(limit=3, max_runs=8)
    for i, k in enumerate("abcabdefgah"):
        t.put(k, i)
    t.delete("b")
    runs = len(t.runs)
    print(f"LSM: {runs} runs + memtable {t.mem}, get(a)={t.get('a')} get(b)={t.get('b')}, "
          f"{t.probes} runs probed")
    t.compact()
    print(f"     after full compaction: {len(t.runs)} run {t.runs[0][0]}")
    col = ["AT", "AT", "AT", "DE", "DE", "CH", "CH", "CH", "CH"]
    print("RLE:", rle(col), "| dict:", dictionary_encode(col), "| bitmap:", bitmap_encode(col))


if __name__ == "__main__":
    demo()
