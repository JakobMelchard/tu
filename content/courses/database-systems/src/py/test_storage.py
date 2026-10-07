import random

import pytest

import storage


def test_blocking_factor_and_pages():
    assert storage.blocking_factor(4096, 100, 96) == 40
    assert storage.pages(1_000_000, 40) == 25_000
    assert storage.pages(1, 40) == 1 and storage.pages(41, 40) == 2


def test_slotted_page_keeps_record_ids():
    rng = random.Random(0)
    p = storage.SlottedPage(512)
    live = {}
    for step in range(400):
        if live and rng.random() < 0.4:
            slot = rng.choice(sorted(live))
            p.delete(slot)
            del live[slot]
        else:
            rec = bytes([rng.randrange(256)]) * rng.randint(1, 40)
            try:
                live[p.insert(rec)] = rec
            except MemoryError:
                pass
        for slot, rec in live.items():
            assert p.get(slot) == rec                  # rid survives compaction
        used = sum(len(r) for r in live.values())
        assert p.free_space() <= 512 - p.HEADER - p.SLOT * len(p.slots) - used + 1e-9


def test_slotted_page_full():
    p = storage.SlottedPage(64)
    p.insert(b"a" * 50)
    with pytest.raises(MemoryError):
        p.insert(b"b" * 10)


@pytest.mark.parametrize("n,cap,M", [(1000, 10, 3), (10_000, 10, 5), (5000, 7, 11), (30, 10, 4), (0, 10, 3)])
def test_external_sort_matches_closed_form(n, cap, M):
    rng = random.Random(n)
    data = [rng.random() for _ in range(n)]
    out, passes, io = storage.external_sort(data, cap, M)
    assert out == sorted(data)
    b = storage.pages(n, cap)
    if b:
        assert passes == storage.sort_passes(b, M)
        assert io == 2 * b * passes
        assert storage.sort_cost_silberschatz(b, M) == io - b      # final write not counted


def test_silberschatz_merge_example():
    """[S6] ch. 15: M = 11 and 90 runs -> one pass leaves 9 runs, so 2 merge passes."""
    b = 90 * 11
    assert storage.sort_passes(b, 11) == 3


def test_file_costs_orders():
    h, s = storage.file_costs(1024, match_pages=8).values()
    assert s["eq_key_avg"] == 10 and h["eq_key_avg"] == 512
    assert s["range"] == 17 and h["range"] == 1024
    assert h["insert"] < s["insert"]


def test_note07_numbers():
    assert storage.sort_passes(10_000, 11) == 4                  # exam question 2
    assert storage.sort_passes(1000, 32) == 3                    # 32 runs need two 31-way merges
    assert storage.blocking_factor(8192, 200) == 40 and storage.pages(50_000, 40) == 1250
    M = 100 * 2**20 // 4096
    assert M == 25_600 and M * (M - 1) * 4096 / 2**40 > 2.4     # two passes up to ~2.5 TiB
