# Exam 09.09.2020 — label **E20c** (2019W/2020S re-take)

Source: [S11], VoWi page `Exam 2020-09-09`. A student's transcript, described
here in our own words. **90 minutes.** This is the paper where the
**convolution and max-pooling calculations first appear**; they have been in
every paper since.

## What was asked

1. **Twelve true/false items**, +2 / −1 / 0. The transcript recalls all twelve;
   `solution.py` lists them with the answers the course marks correct [S12].
   Notable traps: "kernels can only be used with SVMs" (**false** — a kernel
   matrix can feed an MLP), "freezing layers means their weights are only
   updated during fine-tuning" (**false** — they are *not* updated), "naive
   Bayes uses a probability density function when only nominal attributes are
   present" (**false** — density functions are for the *numeric* ones), and
   "convolution and max-pooling layers are important for recurrent neural
   networks" (**false** — for convolutional ones).
2. **Describe a local-search algorithm for creating Bayesian networks.** See
   [note 09](../../../notes/09-bayes.md).
3. **What are the implications of the no-free-lunch theorem?** See
   [note 15](../../../notes/15-automl-and-metalearning.md).
4. **Which of four drawn decision boundaries was produced by a decision tree?**
   (The axis-parallel staircase.)
5. **Three kNN boundaries drawn for $k_1$, $k_2$, $k_3$ on the same data; which
   ordering of the $k$ holds?** Options include $k_1 > k_2 > k_3$,
   $k_2 < k_3 < k_1$, all equal, none of the above.
6. **Explain polynomial regression; advantages and disadvantages.** See
   [note 08](../../../notes/08-linear-models.md).
7. **Max pooling.** A $7\times7$ input tensor and a $3\times3$ window; tick the
   correct output after max pooling with **stride 2**.
8. **Convolution.** The same $7\times7$ input and a $3\times3$ filter; tick the
   correct output after convolution with **stride 2**.
9. **Naive Bayes.** Training and test data are given; compute the **recall** of
   a naive Bayes classifier **with Laplace correction**.

## What `solution.py` does

The paper's tensors and tables are not public, so the code uses arrays of the
**stated shapes** — a $7\times7$ input, a $3\times3$ vertical-edge filter, an
8-row nominal training table and four test rows.

- **Questions 7 and 8** both reduce to
  $O = \lfloor(7 - 3 + 0)/2\rfloor + 1 = \mathbf 3$, so the answer is a
  $3\times3$ array whichever operation is asked for. The windows start at rows
  and columns $0, 2, 4$. With stride 1 the output would be $5\times5$; with
  "same" padding ($P = 1$, $S = 1$) it would be $7\times7$ — the contrast the
  later papers turn into the "padding up / stride down" multiple-answer item.
  Check just the top-left window by hand and then trust the pattern: that is
  what the two-minute budget per question allows.
- **Question 9** uses the course's Laplace convention from [S14] — add 1 to the
  numerator **and 1** to the denominator, leave the prior unsmoothed (see
  [note 09](../../../notes/09-bayes.md)). The solution also reports how many of
  the test rows would have a **zero** likelihood without smoothing, which is the
  zero-frequency problem the correction exists for.
- **Question 5** has no numbers to compute, but it has a usable heuristic: on a
  fixed data set a larger $k$ gives a smoother boundary and, as a trend, a
  higher *training* error. Only $k = 1$ is exact (training error 0, each point is
  its own neighbour); between two larger $k$ the error can dip, so it is a trend,
  not a theorem. Rank the pictures by smoothness and the ordering follows. The
  code measures 0, 0.13, 0.155 for $k = 1, 5, 25$.

```sh
uv run python solution.py
```
