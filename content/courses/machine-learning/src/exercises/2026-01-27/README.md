# Exam 27.01.2026 — label **E26a** (2025W main date)

Source: [S11], VoWi page `Exam 2026-01-27`. A student's transcript of **group
B**, described here in our own words; the paper is not reproduced.

**This is the most recent 184.702 paper and the closest model for 2026W.** Read
the format carefully:

- **75 minutes**, three question **groups** (A/B/C) with different questions,
  entirely single- and multiple-choice.
- **Section 1** — 13 true/false statements, **+2** correct, **−1** wrong.
- **Section 2** — 4 calculations done by hand, **+3** correct, **−1.5** wrong.
- **Section 3** — multiple choice with several correct answers; **+2 only if
  every correct box is ticked**, 0 otherwise.

50 points in total. The student notes that "some of the questions were from
previous exams".

## What was asked

**Section 1** (the item recalled): *the first model in gradient boosting is a
zero rule model* — **true** [S12].

**Section 2**, all four calculations:

1. Compute the **MAE** of the regression model $\hat y = 3 + 2F_1 + F_2$ on a
   small table.
2. A **$k$-armed bandit** example.
3. Decide **which feature 1R takes**.
4. Compute **naive Bayes** to predict $+$ or $-$ for one additional row,
   **without** Laplace correction.

**Section 3**, four multiple-correct questions:

- Which of the following are well-known **CNN architectures**? LeNet / LSTM /
  ResNet / Reception / TeNet / none of the above.
- An output of a **convolutional layer** is larger when … padding decreases /
  padding increases / stride decreases / stride increases.
- What methods help with **vanishing gradients** in neural networks? (Five
  options; the student remembers gradient clipping.)
- Which **classification methods use majority voting**? k-NN / decision trees /
  Bayesian networks / random forests / an ensemble of an SVM, a logistic
  regression and a two-hidden-layer MLP that outputs the prediction of the model
  with the highest confidence / all of the above / none of the above.

## What `solution.py` does

The paper's tables are not public, so each calculation runs on data of the
stated shape. Results:

1. **MAE.** Predictions $(7, 7, 4, 10)$, residuals $(2, -1, 1, -2)$, so
   $\text{MAE} = 6/4 = \mathbf{1.5}$ — while $\text{MSE} = 10/4 = 2.5$. Both
   1.5 and 2.5 appeared among E25b's options, so **the MSE is the trap**: read
   which metric is asked.
2. **Bandit.** Maintaining $Q$ and $N$ from zero and comparing each action with
   the greedy set *before* applying its reward, steps 2, 3 and 6 of our
   eight-step trace are **definitely** exploratory; step 1 is a four-way tie and
   the rest are greedy, hence only *possibly* random. See
   [note 14](../../../notes/14-reinforcement-learning.md).
3. **1R.** The per-attribute error table is the whole answer: temperature 3
   errors, humidity 2, outlook 0 out of 8 rows, so 1R takes **outlook**. Show the
   table, not just the winner.
4. **Naive Bayes without Laplace.** Priors $4/7$ and $3/7$; the class $-$ has no
   training row with the new sample's first attribute value, so one factor is
   **zero** and the entire likelihood of $-$ collapses — the prediction is $+$
   with posterior 1.0. That is the **zero-frequency problem**, and it is
   precisely why the paper has to say whether Laplace correction is used. The
   solution prints the smoothed result alongside for comparison ([S14]'s
   convention: $+1$ on numerator *and* denominator — see
   [note 09](../../../notes/09-bayes.md)).

**Section 3** is stored as an explicit answer key, because all-or-nothing
marking punishes a half-remembered list. The padding/stride claim is *checked
numerically* against `conv.output_size` rather than recalled, since
$O = \lfloor(I - K + 2P)/S\rfloor + 1$ settles it in one line.

```sh
uv run python solution.py
```
