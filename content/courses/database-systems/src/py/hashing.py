"""Hash and bitmap indexes (note 08).

ExtendibleHash: directory of 2^global_depth pointers to buckets of capacity
`cap`; a bucket with local depth d is shared by 2^(global - d) directory
entries.  Overflow of a bucket with d < global splits only the bucket; with
d == global the directory doubles first.  We index the directory with the
`global_depth` least significant bits of h(k); [S6] ch. 14/24 uses the most
significant bits of a 32-bit hash, which changes which entries share a bucket
but not the mechanics.  h(k) = k for integers, so exam traces can be done by hand.

BitmapIndex: one bit vector per distinct value of a low-cardinality column;
predicates become AND/OR/NOT on bit vectors and COUNT a popcount ([S6] ch. 14).
Python ints are the bit vectors.
"""


class ExtendibleHash:
    def __init__(self, cap=2, h=lambda k: k):
        self.cap, self.h = cap, h
        self.global_depth = 0
        self.dir = [{"depth": 0, "items": {}}]
        self.doublings = self.splits = 0

    def _bucket(self, key):
        return self.dir[self.h(key) & ((1 << self.global_depth) - 1)]

    def get(self, key):
        return self._bucket(key)["items"].get(key)

    def insert(self, key, val=None):
        b = self._bucket(key)
        if key in b["items"] or len(b["items"]) < self.cap:
            b["items"][key] = val
            return
        if b["depth"] == self.global_depth:            # no spare bit: double the directory
            self.dir = self.dir + self.dir
            self.global_depth += 1
            self.doublings += 1
        self._split(b)
        self.insert(key, val)                          # may split again if all keys agree

    def _split(self, b):
        self.splits += 1
        d = b["depth"]
        b0 = {"depth": d + 1, "items": {}}
        b1 = {"depth": d + 1, "items": {}}
        for k, v in b["items"].items():
            (b1 if self.h(k) >> d & 1 else b0)["items"][k] = v
        for i, x in enumerate(self.dir):
            if x is b:
                self.dir[i] = b1 if i >> d & 1 else b0

    def buckets(self):
        seen, out = set(), []
        for x in self.dir:
            if id(x) not in seen:
                seen.add(id(x))
                out.append(x)
        return out

    def check(self):
        for i, x in enumerate(self.dir):
            mask = (1 << x["depth"]) - 1
            assert x["depth"] <= self.global_depth and len(x["items"]) <= self.cap
            assert all(self.h(k) & mask == i & mask for k in x["items"])
        for x in self.buckets():                       # 2^(G-d) entries point to x
            assert sum(y is x for y in self.dir) == 1 << (self.global_depth - x["depth"])
        return sum(len(x["items"]) for x in self.buckets())

    def dump(self):
        rows = []
        for i, x in enumerate(self.dir):
            bits = format(i, f"0{self.global_depth}b") if self.global_depth else "-"
            rows.append(f"{bits} -> d={x['depth']} {sorted(x['items'])}")
        return "\n".join(rows)


class BitmapIndex:
    def __init__(self, column):
        self.n = len(column)
        self.bits = {}
        for row, v in enumerate(column):
            self.bits[v] = self.bits.get(v, 0) | (1 << row)

    def eq(self, v):
        return self.bits.get(v, 0)

    def isin(self, values):
        out = 0
        for v in values:
            out |= self.eq(v)
        return out

    def neg(self, bv):
        return ~bv & ((1 << self.n) - 1)

    @staticmethod
    def rows(bv):
        out, i = [], 0
        while bv:
            if bv & 1:
                out.append(i)
            bv >>= 1
            i += 1
        return out

    @staticmethod
    def count(bv):
        return bin(bv).count("1")

    def size_bits(self):
        return len(self.bits) * self.n


if __name__ == "__main__":
    e = ExtendibleHash(cap=2)
    for k in [1, 4, 5, 7, 10, 12, 13]:
        e.insert(k)
    print("extendible hashing, cap 2, keys 1 4 5 7 10 12 13 (h(k) = k, low bits):")
    print(e.dump())
    print("global depth", e.global_depth, "doublings", e.doublings, "splits", e.splits, "keys", e.check())
    gender = ["f", "m", "f", "d", "m", "f", "m", "f"]
    level = ["BSc", "MSc", "MSc", "BSc", "PhD", "MSc", "BSc", "BSc"]
    g, l = BitmapIndex(gender), BitmapIndex(level)
    q = g.eq("f") & l.isin(["MSc", "PhD"])
    print("bitmap: gender = 'f' AND level IN (MSc, PhD):", format(q, "08b")[::-1], "rows", BitmapIndex.rows(q),
          "count", BitmapIndex.count(q))
    print("bitmap sizes:", g.size_bits(), "+", l.size_bits(), "bits for 8 rows")
