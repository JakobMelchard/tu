"""B+ tree with insert, point search, range scan, deletion-free (note 08).

Convention of [S6] ch. 14: `n` is the maximum number of pointers per node
(the fan-out).  Then
  inner node (not root): ceil(n/2) .. n children, one key fewer
  leaf (not root):       ceil((n-1)/2) .. n-1 keys, plus the next-leaf pointer
  root:                  >= 2 children unless it is a leaf
and a tree over K keys has height at most ceil(log_{ceil(n/2)} K) ([S6] ch. 14).

Splits (the variant [S6] ch. 14 describes):
  leaf with n keys      first ceil(n/2) stay, the rest move to a new right
                        sibling; the new sibling's first key is COPIED up
  inner with n+1 ptrs   first ceil((n+1)/2) pointers stay; the key between the
                        halves is MOVED up (it no longer appears in the node)

Other books count differently (a B-tree "of degree k" holds k..2k entries per
node); convert before comparing numbers, see note 08.  `accesses` counts
nodes touched by the last search, i.e. page reads when each node is a page.
"""
import math


class Node:
    __slots__ = ("keys", "kids", "vals", "next")

    def __init__(self, leaf):
        self.keys = []
        self.kids = None if leaf else []
        self.vals = [] if leaf else None
        self.next = None

    @property
    def leaf(self):
        return self.kids is None


class BPlusTree:
    def __init__(self, n=4):
        assert n >= 3
        self.n = n
        self.root = Node(leaf=True)
        self.accesses = 0
        self.splits = 0

    # ---- search -------------------------------------------------------
    def _leaf_for(self, key):
        node, self.accesses = self.root, 1
        while not node.leaf:
            i = _upper(node.keys, key)          # keys[i-1] <= key < keys[i]
            node = node.kids[i]
            self.accesses += 1
        return node

    def search(self, key):
        leaf = self._leaf_for(key)
        i = _lower(leaf.keys, key)
        return leaf.vals[i] if i < len(leaf.keys) and leaf.keys[i] == key else None

    def range(self, lo, hi):
        """All (key, value) with lo <= key <= hi: descend once, then follow leaf links."""
        leaf, out = self._leaf_for(lo), []
        while leaf is not None:
            for k, v in zip(leaf.keys, leaf.vals):
                if k > hi:
                    return out
                if k >= lo:
                    out.append((k, v))
            leaf = leaf.next
            if leaf is not None:
                self.accesses += 1
        return out

    # ---- insert -------------------------------------------------------
    def insert(self, key, val=None):
        split = self._insert(self.root, key, val)
        if split:
            sep, right = split
            root = Node(leaf=False)
            root.keys, root.kids = [sep], [self.root, right]
            self.root = root

    def _insert(self, node, key, val):
        if node.leaf:
            i = _lower(node.keys, key)
            if i < len(node.keys) and node.keys[i] == key:
                node.vals[i] = val                       # unique keys: overwrite
                return None
            node.keys.insert(i, key)
            node.vals.insert(i, val)
            if len(node.keys) < self.n:                  # at most n-1 keys
                return None
            self.splits += 1
            keep = math.ceil(self.n / 2)
            right = Node(leaf=True)
            right.keys, right.vals = node.keys[keep:], node.vals[keep:]
            node.keys, node.vals = node.keys[:keep], node.vals[:keep]
            right.next, node.next = node.next, right
            return right.keys[0], right                  # copy up
        i = _upper(node.keys, key)
        split = self._insert(node.kids[i], key, val)
        if not split:
            return None
        sep, right_child = split
        node.keys.insert(i, sep)
        node.kids.insert(i + 1, right_child)
        if len(node.kids) <= self.n:
            return None
        self.splits += 1
        keep = math.ceil((self.n + 1) / 2)               # pointers kept on the left
        right = Node(leaf=False)
        up = node.keys[keep - 1]                         # move up
        right.keys, right.kids = node.keys[keep:], node.kids[keep:]
        node.keys, node.kids = node.keys[:keep - 1], node.kids[:keep]
        return up, right

    # ---- inspection ---------------------------------------------------
    def height(self):
        h, node = 1, self.root
        while not node.leaf:
            node, h = node.kids[0], h + 1
        return h

    def leaves(self):
        node = self.root
        while not node.leaf:
            node = node.kids[0]
        while node is not None:
            yield node
            node = node.next

    def check(self):
        """Assert every structural invariant; returns the number of keys."""
        n, depths = self.n, set()

        def walk(node, lo, hi, depth, is_root):
            assert node.keys == sorted(node.keys) and len(set(node.keys)) == len(node.keys)
            assert all((lo is None or k >= lo) and (hi is None or k < hi) for k in node.keys)
            if node.leaf:
                depths.add(depth)
                assert len(node.keys) <= n - 1
                if not is_root:
                    assert len(node.keys) >= math.ceil((n - 1) / 2)
                return len(node.keys)
            assert len(node.kids) == len(node.keys) + 1 and len(node.kids) <= n
            assert len(node.kids) >= (2 if is_root else math.ceil(n / 2))
            bounds = [lo] + node.keys + [hi]
            return sum(walk(c, bounds[i], bounds[i + 1], depth + 1, False) for i, c in enumerate(node.kids))

        total = walk(self.root, None, None, 1, True)
        assert len(depths) == 1, "leaves at different depths"
        chain = [k for leaf in self.leaves() for k in leaf.keys]
        assert chain == sorted(chain) and len(chain) == total
        return total

    def dump(self):
        level, lines = [self.root], []
        while level:
            lines.append("  ".join("[" + " ".join(map(str, x.keys)) + "]" for x in level))
            level = [c for x in level if not x.leaf for c in x.kids]
        return "\n".join(lines)


def _lower(a, x):
    lo, hi = 0, len(a)
    while lo < hi:
        mid = (lo + hi) // 2
        if a[mid] < x:
            lo = mid + 1
        else:
            hi = mid
    return lo


def _upper(a, x):
    lo, hi = 0, len(a)
    while lo < hi:
        mid = (lo + hi) // 2
        if a[mid] <= x:
            lo = mid + 1
        else:
            hi = mid
    return lo


def max_height(K, n):
    """Upper bound ceil(log_{ceil(n/2)} K) on the number of levels ([S6] ch. 14)."""
    return max(1, math.ceil(math.log(K) / math.log(math.ceil(n / 2)) - 1e-12))


if __name__ == "__main__":
    t = BPlusTree(n=4)
    for k in [10, 20, 5, 6, 12, 30, 7, 17, 3, 25, 27, 8]:
        t.insert(k, f"r{k}")
    print("n = 4 after inserting 10 20 5 6 12 30 7 17 3 25 27 8:")
    print(t.dump())
    print("invariants hold for", t.check(), "keys; height", t.height(), "splits", t.splits)
    print("search 17 ->", t.search(17), "in", t.accesses, "node accesses")
    print("range [7, 20] ->", [k for k, _ in t.range(7, 20)], "in", t.accesses, "accesses")
    big = BPlusTree(n=100)
    for k in range(1_000_000):
        big.insert(k)
    print(f"n = 100, 10^6 sequential keys: height {big.height()} (bound {max_height(10**6, 100)})")
