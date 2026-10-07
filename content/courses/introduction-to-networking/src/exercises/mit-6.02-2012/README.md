# MIT 6.02, Fall 2012 — the networking practice problems

> **This is MIT's material, not 191.030's.** 191.030 is new in 2026W and has
> no past paper, no exercise sheet and no public slide deck [S1], [S2], [S5],
> [S7]. Nothing below was ever set at TU Wien. It is here as a **substitute**,
> and every problem is labelled with where it came from.

## What the source is

| | |
|---|---|
| Course | **6.02 Introduction to EECS II: Digital Communication Systems** |
| Institution | Massachusetts Institute of Technology |
| Term | **Fall 2012** (the OCW snapshot; the course has since been renumbered) |
| Instructors | Hari Balakrishnan, George Verghese |
| URL | <https://ocw.mit.edu/courses/6-02-introduction-to-eecs-ii-digital-communication-systems-fall-2012/> |
| Retrieved | 2026-09-22 |
| Licence | **CC BY-NC-SA 4.0** — stated by OCW on every page (`"license": "https://creativecommons.org/licenses/by-nc-sa/4.0/"` in the page metadata) |
| Register entry | [S34] in [`../../../refs/SOURCES.md`](../../../refs/SOURCES.md) |

## Why this source and not another

One reason, and it is decisive: **OCW publishes the tutorials with official
solutions.** Tutorials 1–11 each have a problems PDF and a separate solutions
PDF. 191.030 has no answer key of any kind, so a published answer key for the
same *mechanisms* is the closest available check on whether a routing or
transport answer is right. It is the same discipline as
[`../../py/test_rfc_vectors.py`](../../py/test_rfc_vectors.py), which asserts
against the numbers RFCs print.

Note the correction to the usual claim about OCW: 6.02 publishes **quizzes 1–3
without solutions**, and **tutorials with solutions**. The exam-with-solutions
artefact people expect from OCW is, for this course, a tutorial.

## What it covers that 191.030's TISS topic list also covers

| 6.02 tutorial | 191.030 topic [S1] | our note |
|---|---|---|
| **8** — packet vs circuit switching, store-and-forward delay | Foundations: "basic concepts", layering, sources of delay | [01](../../../notes/01-foundations-and-governance.md) |
| **10** — routing: distance-vector convergence, link-state, Dijkstra, routing loops | "Routing and Forwarding", "link-state … algorithms" | [06](../../../notes/06-forwarding-and-routing.md), [07](../../../notes/07-link-state-and-path-vector.md) |
| **11** — reliable data transport: stop-and-wait, sliding window, RTT, bandwidth-delay product, sequence-number wraparound, loss composition | "Layer 4 (TCP/UDP)", and the practical part's "describe TCP behavior given a specific scenario" (stated on TISS until 2026-09-2x, removed by 2026-09-27) | [05](../../../notes/05-udp-and-tcp.md), [11](../../../notes/11-exercise-playbook.md) |

## What it covers that 191.030 does not

Most of it. 6.02 is a *digital communication systems* course; networking is
only its third unit.

- **Tutorials 1–7 are out of scope entirely**: source coding and entropy,
  Huffman and LZW, binary symmetric channels, Hamming and convolutional codes,
  Viterbi decoding, Gaussian noise and BER, modulation/demodulation, LTI
  channels, intersymbol interference, Fourier analysis. 191.030's subject list
  names no physical layer and no coding theory [S1].
- **Tutorial 9, MAC protocols** (TDMA, Aloha) — 191.030 names Ethernet, not
  channel-sharing protocols. Excluded here.
- **Little's law and queueing** (tutorial 8, problem 1) — no queueing theory on
  the TISS list. Only tutorial 8's store-and-forward latency is used.

## What 191.030 covers that 6.02 does not touch at all

Ethernet framing and ARP, IPv4 addressing and subnetting, IPv6 in any form,
**path-vector routing and BGP**, DNS, DNSSEC, Telnet, multicast routing,
Internet governance, socket programming, protocol design. Those gaps are why a
second source and a set of our own problems exist — see
`../uclouvain-cnp3-2019/` and
[`../../../notes/12-substitute-practice-set.md`](../../../notes/12-substitute-practice-set.md).

## What is in this directory

| file | what |
|---|---|
| `mit602_routing.py` | tutorials 8 and 10: store-and-forward delay, timed distance vector, the four routing strategies |
| `mit602_transport.py` | tutorial 11: stop-and-wait, sliding windows, wraparound, loss composition |
| `test_mit602_routing.py` | 11 tests |
| `test_mit602_transport.py` | 5 tests |

Each module's `PUBLISHED_ANSWERS` holds the numbers MIT's solution PDFs print,
and every test asserts against it.

```sh
# from the course folder
uv run pytest src/exercises -q
uv run python src/exercises/mit-6.02-2012/mit602_routing.py
uv run python src/exercises/mit-6.02-2012/mit602_transport.py
```

## Vendored or cited?

**Cited, not vendored.** CC BY-NC-SA 4.0 would permit redistributing the PDFs
with attribution, but its **NonCommercial** and **ShareAlike** terms would then
attach to this directory and propagate into anything built from it, and the
PDFs are two clicks away at a stable OCW URL. So: no PDF is committed, no
sentence of MIT's prose is copied, and every problem is **restated in our own
words** in the module docstrings. The *answers* are quoted as bare numbers,
which is what a result is.

## Two honest caveats

1. **The figures are images**, so the PDF text does not carry them. Tutorial 10
   problem 1's two topologies were therefore **reconstructed from the published
   answers** — network I must be the path `A–B–C` (A learns C one advertisement
   after B), network II must be the triangle `D–E–F` (F is adjacent to D, and D
   re-routes to E after the `D–E` link fails, which needs a cycle). No other
   three-node graph fits the printed numbers. The reconstruction is stated in
   the module rather than hidden. Tutorial 10 problems 4–6 and tutorial 11
   problems relying on unreadable figures are **not** solved here.
2. **MIT's earth–moon utilisation is 6.5 %, ours is 6.67 %.** Theirs follows
   from rounding the achieved rate to the 2.6 kbit/s the sheet also prints;
   6.67 % is 1/15 exactly. The test asserts both and says which is which rather
   than picking the convenient one.

Source labels refer to [`../../../refs/SOURCES.md`](../../../refs/SOURCES.md).
