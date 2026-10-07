"""Physical organisation: pages, records, heap and sorted files, external sort
(note 07).

  blocking_factor, pages      records per page and file size in pages
  SlottedPage                 slot directory at the front, records packed from
                              the back; record id = (page, slot) stays valid
                              when the page is compacted ([S6] ch. 13; the
                              sqlite b-tree page in [S21] fileformat2 has the
                              same shape: cell-pointer array + cell content area)
  file_costs                  page-I/O cost of scan / equality / range / insert
                              for heap and sorted files (derived in note 07)
  external_sort               M-buffer external merge sort that counts passes
                              and page I/Os; checked against the closed form
                              b(2 ceil(log_{M-1}(b/M)) + 1) of [S6] ch. 15
"""
import math
import random


def blocking_factor(page_bytes, record_bytes, header_bytes=0):
    """Unspanned records: floor((B - header) / R)."""
    return (page_bytes - header_bytes) // record_bytes


def pages(n_records, bf):
    return math.ceil(n_records / bf)


class SlottedPage:
    """Variable-length records in one page.  Header 4 bytes, 4 bytes per slot."""
    HEADER, SLOT = 4, 4

    def __init__(self, size=4096):
        self.size = size
        self.slots = []              # slot -> (offset, length) or None (deleted)
        self.data = {}               # offset -> bytes
        self.free_end = size         # records grow downwards from here

    def free_space(self):
        return self.free_end - (self.HEADER + self.SLOT * len(self.slots))

    def insert(self, rec: bytes):
        reuse = next((i for i, s in enumerate(self.slots) if s is None), None)
        need = len(rec) + (0 if reuse is not None else self.SLOT)
        if need > self.free_space():
            self.compact()
            if need > self.free_space():
                raise MemoryError("page full")
        self.free_end -= len(rec)
        self.data[self.free_end] = rec
        entry = (self.free_end, len(rec))
        if reuse is not None:
            self.slots[reuse] = entry
            return reuse
        self.slots.append(entry)
        return len(self.slots) - 1

    def get(self, slot):
        off, _ = self.slots[slot]
        return self.data[off]

    def delete(self, slot):
        off, _ = self.slots[slot]
        del self.data[off]
        self.slots[slot] = None      # slot stays: other pages may hold this rid

    def compact(self):
        """Move live records to the end of the page; offsets change, slots do not."""
        end = self.size
        new = {}
        for i, s in enumerate(self.slots):
            if s is not None:
                rec = self.data[s[0]]
                end -= len(rec)
                new[end] = rec
                self.slots[i] = (end, len(rec))
        self.data, self.free_end = new, end


def file_costs(b, match_pages=1):
    """Page I/Os, b = pages of the file (derivations in note 07).
    Heap: unordered.  Sorted: ordered on the search key, binary search."""
    lg = math.ceil(math.log2(b)) if b > 1 else 1
    return {
        "heap":   {"scan": b, "eq_key_avg": b / 2, "eq_key_worst": b, "range": b, "insert": 2},
        "sorted": {"scan": b, "eq_key_avg": lg, "eq_key_worst": lg, "range": lg + match_pages - 1,
                   "insert": lg + b},      # find the spot, then shift (read + write) half the file
    }


def external_sort(records, page_cap, M):
    """Sort with M buffer pages.  Pass 0 builds ceil(b/M) runs of M pages; each
    merge pass merges M-1 runs.  Returns (sorted list, passes, page I/Os
    counting reads and writes of every pass, i.e. 2b per pass)."""
    assert M >= 3
    b = pages(len(records), page_cap)
    chunk = M * page_cap
    runs = [sorted(records[i:i + chunk]) for i in range(0, len(records), chunk)]
    passes, io = 1, 2 * b
    while len(runs) > 1:
        runs = [_merge(runs[i:i + M - 1]) for i in range(0, len(runs), M - 1)]
        passes += 1
        io += 2 * b
    return (runs[0] if runs else []), passes, io


def _merge(runs):
    import heapq
    return list(heapq.merge(*runs))


def sort_passes(b, M):
    """1 + ceil(log_{M-1} ceil(b/M)) passes."""
    runs = math.ceil(b / M)
    return 1 + (math.ceil(math.log(runs, M - 1) - 1e-12) if runs > 1 else 0)


def sort_cost_silberschatz(b, M):
    """[S6] ch. 15 with b_b = 1: b(2 ceil(log_{M-1}(b/M)) + 1), final write not counted."""
    return b * (2 * (sort_passes(b, M) - 1) + 1)


if __name__ == "__main__":
    bf = blocking_factor(4096, 100, header_bytes=96)
    print(f"4 KiB pages, 100-byte records, 96-byte header: bf = {bf}, "
          f"1,000,000 records -> {pages(1_000_000, bf)} pages")
    p = SlottedPage(128)
    ids = [p.insert(bytes([65 + i]) * 20) for i in range(4)]
    print("slots", ids, "free", p.free_space())
    p.delete(1)
    print("after delete(1): free", p.free_space(), "(space reclaimed only by compaction)")
    p.compact()
    print("after compact:   free", p.free_space(), "slot 2 still", p.get(2)[:3])
    print("insert reuses slot", p.insert(b"x" * 30))
    for kind, costs in file_costs(1000, match_pages=10).items():
        print(kind, costs)
    rng = random.Random(0)
    data = [rng.random() for _ in range(10_000)]
    out, passes, io = external_sort(data, page_cap=10, M=5)
    print(f"external sort b=1000, M=5: {passes} passes, {io} page I/Os; "
          f"closed form {sort_passes(1000, 5)} passes, [S6] cost {sort_cost_silberschatz(1000, 5)}")
