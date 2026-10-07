# refs: 194.100 Theoretical Foundations and Research Topics in ML

[`SOURCES.md`](SOURCES.md) is the register: one entry `S1 … S45`, each with
title, authors, URL, retrieval date, licence/access status and what it was used
for. The notes cite it as `[S<n>]`, with a theorem locator wherever a theorem is
being cited.

## What is here

| file | what it is |
|---|---|
| [`SOURCES.md`](SOURCES.md) | the source register (authoritative) |
| [`lecture-notes-map.md`](lecture-notes-map.md) | chapter-by-chapter map of S9 and S10 → our notes → our code |
| [`fetch-sources.sh`](fetch-sources.sh) | downloads the two textbooks into `vendor/` for personal use |
| `vendor/` | created by the script, **git-ignored**, never committed |

## Nothing is vendored

There is no course material to vendor. **Everything this course publishes lives
in TUWEL**, which needs a login [S6]; TISS says plainly "No lecture notes are
available" [S1]; and the VoWi page is an empty stub with no attachments [S8].
So `refs/` contains only text written here.

**TUWEL caveat.** TUWEL was not accessed. Every statement in these notes about
what TUWEL contains (weekly units, forum, live-session announcements, coursework,
project and oral dates) is second-hand, from TISS [S1] and the 2025W course
homepage [S6], and unverified. TISS was re-read on 2026-09-27: no field changed [S1];
the course homepage still has no 2026W page [S5].

Of the two textbooks the notes actually rest on, the licences differ and the
difference is worth knowing:

- **S9 (Shalev-Shwartz & Ben-David, *Understanding Machine Learning*)**: the
  author-hosted PDF's own download page says: "PDF of manuscript posted by
  permission of Cambridge University Press. Users may download a copy for
  **personal use only. Not for distribution.**" **Cite only. Do not commit it.**
- **S10 (Mohri, Rostamizadeh & Talwalkar, *Foundations of Machine Learning*,
  2nd ed.)**: **CC-BY-NC-ND**, stated on both the book page and the PDF's
  copyright page. Verbatim non-commercial redistribution *is* permitted, so this
  one *could* legitimately be vendored. It is not, only to keep the repo small
  and the policy in this directory uniform. If you ever do commit it, keep it
  unmodified and carry the licence notice.

Use `fetch-sources.sh` to pull both onto your own machine:

```sh
cd ws2026/theoretical-foundations-and-research-topics-in-ml/refs && ./fetch-sources.sh
```

Checksums as retrieved on 2026-09-22, so you can tell whether an author has
replaced a file since:

```
S9   sha256 5ad0c69c922e47e423f6b469e8cfbaf07beae6933185af746b670911a8d163f2   2601512 bytes   449 pp.
S10  sha256 1a986e004028786686d51730693f200429d31424e687c5e18d19e28511852904   6224448 bytes   505 pp.
```

(If your download's checksum differs, that is information, not an error: record
the new one and re-check the theorem numbers cited in `SOURCES.md`, since these
books are revised in place.)

## Reading order

1. [`../notes/00-exam-focus.md`](../notes/00-exam-focus.md) **first**: it
   establishes what is actually assessed (coursework + project + **oral exam**),
   and is honest that no past questions exist anywhere public.
2. **S9** chapters 2–6 and 13, in that order: this is the spine of the course's
   published topic list, and `lecture-notes-map.md` says which of our notes
   covers each chapter.
3. **S10** chapters 3, 5, 6 for the margin and kernel material, where it is
   sharper and better organised than S9.
4. [`../notes/README.md`](../notes/README.md): the notes, then
   [`../notes/12-oral-exam-question-bank.md`](../notes/12-oral-exam-question-bank.md)
   to test yourself.

## A warning about theorem numbers

The notes cite theorem *numbers* (`[S9 Thm 6.8]`, `[S10 Cor. 5.11]`) rather than
paraphrases, deliberately: in an oral exam the examiner can ask you to state a
theorem, and a half-remembered constant is worse than no constant. Every number
in `SOURCES.md` was read out of the retrieved PDF on 2026-09-22, but **S9 and
S10 are both revised in place by their authors**, so if a locator does not match
your copy, trust your copy and update
`../notes/CHANGELOG.md`.

Two traps worth naming, because both books are usually misquoted on them:

- **S9 Thm 6.8** (fundamental theorem, quantitative) is *asymmetric* in the
  realisable case: the lower bound is $C_1(d+\log(1/\delta))/\varepsilon$ but the
  upper bound is $C_2(d\log(1/\varepsilon)+\log(1/\delta))/\varepsilon$. The
  $\log(1/\varepsilon)$ is in the upper bound only.
- **S9 Thm 6.11** carries a $1/\delta$, not $\log(1/\delta)$; it comes from
  Markov, not from McDiarmid. S10 Cor. 3.19 is the $\sqrt{\log(1/\delta)/2m}$
  version. They are different theorems with different constants; say which one
  you are quoting.
