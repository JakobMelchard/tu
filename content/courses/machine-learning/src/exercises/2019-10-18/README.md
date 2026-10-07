# Exam 18.10.2019 — label **E19b** (2018W re-take)

Source: [S11], VoWi page `Exam 2019-10-18` — a student's transcript written from
memory, with the caveat that the wording is approximate and none of the paper's
data tables are reproduced there. Described below **in our own words**; nothing
is copied.

## What was asked

1. **True/false, +2 / −1 / 0.** Ten statements, of which the transcript recalls
   six: are random forests a heterogeneous ensemble learner; does a perceptron
   with a softmax output solve XOR; is d-separation used in the neighbourhood
   search when building a Bayesian network; are paired $t$-tests used for "folds
   verification" in the hold-out method; is information gain an unsupervised
   feature-selection method; is Bayesian optimisation used for constructing
   Bayesian networks; does the SVM algorithm guarantee convergence to a globally
   optimal solution. Every one of them is **false** [S12] — see the true/false
   bank in [`../../../notes/00-exam-focus.md`](../../../notes/00-exam-focus.md).
2. **Rice's framework** for algorithm selection: explain it, and say whether it
   can be used for (Bayesian) hyperparameter optimisation. See
   [note 15](../../../notes/15-automl-and-metalearning.md).
3. **Ridge versus lasso regression.** See
   [note 08](../../../notes/08-linear-models.md).
4. **Decision boundaries on two concentric rings.** Four plots of the same data
   set — two concentric rings of points, one ring per class. Draw the boundary
   that a perceptron, an SVM with a quadratic kernel, 1-NN and a decision tree
   would learn.
5. **AdaBoost with a stump.** Three points on a line, $x = 1, 3, 5$, with labels
   $-1, +1, -1$; the weak learner is a one-level decision tree. Give each point's
   weight before the first round; draw the first stump's decision boundary;
   circle the point whose weight rises for the second round.
6. **Support vectors.** A 2-D plot with four points, two per class. Circle the
   support vectors, draw the SVM boundary and give its slope.
7. **A calculation, with the working shown.** Nine training points and three new
   ones. (a) Predict the three labels with 3-NN, choosing a suitable distance
   function and justifying it (5 pts). (b) Remove one specific variable and
   predict again — does anything change? (2 pts). (c) Classify the same three
   points with naive Bayes **without** Laplace correction, then compute the
   classifier's precision and recall (6 pts).

## What `solution.py` does

The paper's own tables are not public, so exercises 4–7 are solved on data of
the **stated shape**: nine nominal training rows plus three test rows for
exercise 7, the three labelled points of exercise 5 exactly as given, four points
in the plane for exercise 6, and a generated two-ring data set for exercise 4.

Results worth knowing:

- **Exercise 4** — the perceptron scores about 0.5 on the rings (chance: one
  hyperplane cannot enclose a ring), while an RBF or degree-2 polynomial SVM,
  1-NN and a depth-8 tree all reach 1.0.
- **Exercise 5** — initial weights $1/3$ each [S12]; no stump separates
  $-1, +1, -1$, so the best one errs on a single point, giving
  $\epsilon = 1/3$, $\alpha = \tfrac12\ln 2 = 0.347$, and weights
  $(0.25, 0.25, 0.5)$ after renormalisation. The misclassified point is the one
  whose weight doubles.
- **Exercise 6** — the two closest opposite points are the support vectors, the
  boundary is their perpendicular bisector, $w = (1, 1)$, $b = -5$, slope $-1$,
  margin $1/\sqrt2$.
- **Exercise 7** — all attributes are nominal, so the justified metric is
  **Hamming**; one-hot encoding plus $L_2$ gives the same neighbour ordering and
  is what the code uses. Without Laplace correction several naive-Bayes
  likelihoods are exactly zero — the zero-frequency problem the course asks
  about elsewhere — but the argmax is still well defined here.

```sh
uv run python solution.py
```
