"""A TREC-style evaluation campaign: runs, depth-k pooling, a leaderboard, and pool bias.

Note 13 (campaigns) and note 04 (pooling). Pooling as in the lecture
[S8 'Pooling in IR', 'Pooling Process', 'Pool Bias']; reliability of pooled
collections and the leave-one-run-out test after Zobel [S27]; bpref for
incomplete judgements after Buckley & Voorhees [S28].

Simulation with known complete ground truth. Per query there are `n_rel`
relevant documents; a fraction `hidden` of them is *lexically mismatched*
(like the planted aliases of `corpus.py`): the participating systems, all of
the same (lexical) family, rarely rank them high. A late "novel" system (think:
the first dense retriever after a BM25-era campaign) finds them. It did not
contribute to the pool, so its newly found relevant documents are unjudged,
counted as non-relevant, and it is under-ranked on the leaderboard.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from metrics import average_precision, kendall_tau, paired_t_test, precision_at_k


@dataclass
class Campaign:
    runs: dict[str, dict[int, list[int]]]     # system -> query -> ranked doc ids
    truth: dict[int, set[int]]                 # complete relevance
    hidden: dict[int, set[int]]                # relevant but lexically mismatched
    n_docs: int


def simulate(n_docs: int = 3000, n_queries: int = 50, n_rel: int = 20, hidden: float = 0.4,
             n_systems: int = 10, run_len: int = 100, seed: int = 0) -> Campaign:
    rng = np.random.default_rng(seed)
    truth, hid = {}, {}
    for q in range(n_queries):
        R = rng.choice(n_docs, n_rel, replace=False)
        truth[q] = set(R.tolist())
        hid[q] = set(R[: int(hidden * n_rel)].tolist())
    quality = np.linspace(1.2, 3.0, n_systems)                  # signal strength on visible relevant docs
    runs: dict[str, dict[int, list[int]]] = {}
    specs = [(f"lex{i:02d}", a, 0.3) for i, a in enumerate(quality)] + [("novel", 2.2, 2.2)]
    for name, a_vis, a_hid in specs:
        runs[name] = {}
        for q in range(n_queries):
            s = rng.normal(size=n_docs)
            vis = list(truth[q] - hid[q])
            s[vis] += a_vis
            s[list(hid[q])] += a_hid
            runs[name][q] = np.argsort(-s)[:run_len].tolist()
    return Campaign(runs, truth, hid, n_docs)


def pool(runs: dict[str, dict[int, list[int]]], systems: list[str], depth: int) -> dict[int, set[int]]:
    """Union of the top-`depth` of every contributing system, per query: the documents assessors judge."""
    qs = next(iter(runs.values())).keys()
    return {q: set().union(*(runs[s][q][:depth] for s in systems)) for q in qs}


def pooled_qrels(camp: Campaign, judged: dict[int, set[int]]) -> dict[int, set[int]]:
    """Assessors are perfect on what they see; unjudged documents are treated as non-relevant."""
    return {q: judged[q] & camp.truth[q] for q in judged}


def bpref(ranking: list[int], rel: set[int], judged: set[int]) -> float:
    """(1/R) sum over retrieved relevant r of 1 - min(#judged non-rel above r, R) / R; unjudged are skipped."""
    R = len(rel)
    if R == 0:
        return 0.0
    nonrel_above, s = 0, 0.0
    for d in ranking:
        if d in rel:
            s += 1 - min(nonrel_above, R) / R
        elif d in judged:
            nonrel_above += 1
    return s / R


def map_score(run: dict[int, list[int]], qrels: dict[int, set[int]]) -> float:
    return float(np.mean([average_precision([str(d) for d in run[q]], {str(d) for d in qrels[q]}) for q in qrels]))


def leaderboard(camp: Campaign, qrels: dict[int, set[int]], judged=None) -> list[tuple[str, float]]:
    rows = []
    for s, run in camp.runs.items():
        if judged is None:
            rows.append((s, map_score(run, qrels)))
        else:
            rows.append((s, float(np.mean([bpref(run[q], qrels[q], judged[q]) for q in qrels]))))
    return sorted(rows, key=lambda x: -x[1])


def leave_one_out(camp: Campaign, systems: list[str], depth: int) -> dict[str, float]:
    """MAP of each run with the full pool minus MAP when its unique contributions are removed [S27]."""
    full = pooled_qrels(camp, pool(camp.runs, systems, depth))
    out = {}
    for s in systems:
        reduced = pooled_qrels(camp, pool(camp.runs, [x for x in systems if x != s], depth))
        out[s] = map_score(camp.runs[s], full) - map_score(camp.runs[s], reduced)
    return out


def rank_of(board: list[tuple[str, float]], name: str) -> int:
    return [s for s, _ in board].index(name) + 1


if __name__ == "__main__":
    camp = simulate()
    participants = [s for s in camp.runs if s != "novel"]
    depth = 20
    judged = pool(camp.runs, participants, depth)
    qp = pooled_qrels(camp, judged)
    n_j = np.mean([len(v) for v in judged.values()])
    found = np.mean([len(qp[q]) / len(camp.truth[q]) for q in qp])
    print(f"pool depth {depth} over {len(participants)} runs: {n_j:.0f} judged docs/query "
          f"({100 * n_j / camp.n_docs:.1f} % of the collection), {100 * found:.0f} % of all relevant docs found")
    full_b, pool_b = leaderboard(camp, camp.truth), leaderboard(camp, qp)
    bp_b = leaderboard(camp, qp, judged)
    print(f"{'system':8s} {'MAP full':>9s} {'MAP pooled':>11s} {'bpref pooled':>13s}")
    fd, pd, bd = dict(full_b), dict(pool_b), dict(bp_b)
    for s, _ in full_b:
        print(f"{s:8s} {fd[s]:9.3f} {pd[s]:11.3f} {bd[s]:13.3f}")
    print(f"'novel': rank {rank_of(full_b, 'novel')} with complete judgements, rank {rank_of(pool_b, 'novel')} "
          f"on the pooled leaderboard (pool bias)")
    tau = kendall_tau([fd[s] for s in participants], [pd[s] for s in participants])
    print(f"Kendall tau, participants, full vs pooled MAP: {tau:.3f}")
    loo = leave_one_out(camp, participants, depth)
    print(f"leave-one-run-out MAP drop: mean {np.mean(list(loo.values())):.4f}, max {max(loo.values()):.4f}")
    top = [s for s, _ in pool_b[:2]]
    a = [average_precision([str(d) for d in camp.runs[top[0]][q]], {str(d) for d in qp[q]}) for q in qp]
    b = [average_precision([str(d) for d in camp.runs[top[1]][q]], {str(d) for d in qp[q]}) for q in qp]
    t, p = paired_t_test(a, b)
    print(f"top two on the pooled board, {top[0]} vs {top[1]}: paired t = {t:.2f}, p = {p:.3f}")
