# Technical report outline — at most five pages, one PDF

Sourced from *Assignment 3 — Deliver* [S14]; see
[`../../../notes/00-exam-focus.md`](../../../notes/00-exam-focus.md). A large
part may be taken from the assignment-1 proposal with appropriate edits.

The sheet requires **four questions answered**, plus three further items. Write
those seven things first; everything else is support.

## The four required questions

1. **What is the problem that you tried to solve?**
2. **Why is it a problem?**
3. **What is your solution?**
4. **Why is it a solution — and in particular, why is or is not deep learning a
   solution?** *(The "or is not" is in the sheet. A project whose honest answer
   is "the classical baseline was as good" is a valid, gradeable result if it is
   argued.)*

## The three further required items

5. **Main take-aways and insights.** The sheet's own examples are concrete and
   mechanical: "batch-normalization improved the results significantly",
   "Adadelta worked much better than SGD on my data", "annotating data works
   really well with tool X", "setting up the pre-processing takes much more time
   than I expected". Write that kind of sentence, not generalities.
6. **What would you do differently if you did the same project again?**
7. **How much time did you spend?** Against your initial estimate, per
   work-breakdown bucket. **If you underestimated any part, what were the
   reasons?**

## A five-page layout

Five pages is tight. Suggested budget (adjust, but keep the seven items above):

| ≈ pages | section | content |
|---|---|---|
| 0.15 | Title | Task in one line, name, matriculation number, date, repository link, project type |
| 0.6 | **1 Problem** (Q1, Q2) | Input, output, metric and why that metric. Why the problem matters. Why deep learning is plausible here, and which of the eight course topics is used. The target you committed to **before training** and its justification (published number, baseline, or a learning-curve extrapolation) |
| 0.4 | 2 Related work | 3–6 references, including the one you compare against: its metric, split, preprocessing, model size. **State explicitly what is comparable to your setup and what is not** |
| 0.5 | 3 Data | Source, **licence**, size, label distribution, input shape. Preprocessing and augmentation. Split protocol (hashed ids, test opened once, group leakage considered) |
| 0.9 | **4 Method** (Q3) | Architecture with one shape-annotated figure; parameter count. Loss, optimiser, schedule, regularisation, initialisation — as a table generated from `config.yaml`. Baselines: trivial, classical, and pretrained if used |
| 1.0 | **5 Experiments and results** (Q4) | Hardware, wall time per run, number of seeds. One main table: trivial / classical / pretrained / yours (mean ± std over ≥3 seeds) / the comparison target — same metric, same split. One training-curve figure. One ablation: the single ingredient you claim matters, removed |
| 0.6 | 6 Error analysis | Confusion matrix or residuals; the worst 20 with the pattern you found; one slice; calibration if probabilities matter. If XAI is used, attributions on correct and wrong cases plus a sanity check |
| 0.6 | **7 Insights, limitations, retrospective** (items 5, 6, 7) | The take-aways; what did not work and why; what you would do differently; **the time table: estimated vs actual per bucket, with reasons for the gaps** |
| 0.25 | 8 Conclusion | Two paragraphs: what was shown, what was not. Say plainly whether the target was met |

**Reproducibility details go in the repository README, not in the five pages**:
commands to reproduce every number, config files, seeds, git hash, environment
(Python and torch versions, device). Point to it from section 5.

## Checklist

- [ ] All four questions answered explicitly, including *why is or is not deep
      learning a solution*.
- [ ] Take-aways, "what I would do differently", and estimated-vs-actual time
      are all present — these are required, not optional.
- [ ] **At most 5 pages.** Count them.
- [ ] One PDF.
- [ ] Every number matches the presentation and the repository.
- [ ] Spell-checked (the assignment sheets ask for this explicitly [S12]).
- [ ] Submitted **before the first presentation date**.
