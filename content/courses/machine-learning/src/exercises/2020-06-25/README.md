# Exam 25.06.2020 — label **E20b** (2020S)

Source: [S11], VoWi page `Exam 2020-06-25`. A student's transcript, described
here in our own words; the paper is not reproduced. **90 minutes.**

## What was asked

1. **Twelve true/false items**, +2 for a correct answer, −1 for a wrong one, 0
   for a blank. The transcript recalls six: is MAE less sensitive to outliers;
   does freezing layers mean they *will* be fine-tuned; is overfitting more
   likely on a small test set; is boosting easily parallelisable; are paired
   $t$-tests used for "folds verification" in the hold-out method; do random
   forests use bootstrapping.
2. **Boosting with a stump.** Three points on a line, labels $-1, +1, -1$. What
   is each point's weight before the first round; where does the first stump
   split; which point gains weight.
3. **Decision boundaries on two concentric rings** for a perceptron, a decision
   tree, 1-NN, and AdaBoost with many weak learners.
4. **Name three hyperparameter-optimisation methods.**
5. **Name two methods to compute the coefficients of a linear regression.**
6. **kNN with leave-one-out CV.** Ten 2-D points; compute the average error rate
   under LOOCV (= 10-fold CV here) for (a) 1-NN and (b) 3-NN.
7. **1R and a Bayesian network.** Thirteen samples, four categorical variables
   (age, education, income, marital status) and a yes/no target (purchase).
   (a) Compute 1R on samples 1–8 and then precision and accuracy on samples
   9–13 — the transcript notes, with some surprise, that 1R split on **age** and
   achieved 1.0 on both. (b) Propose a Bayesian network for the full data set,
   argue for the structure, and compute some conditional probabilities in it.

## What `solution.py` does

The paper's data is not public, so both calculations run on tables of the
**stated shape**: ten 2-D points in two groups with one intruding point for the
LOOCV question, and a 13-row nominal table with the four named attributes for
1R.

- **LOOCV (exercise 6)** — the whole point of the question is that 1-NN is *not*
  error-free under LOOCV, because a point cannot be its own neighbour. On our
  layout 1-NN scores 0.2 error and 3-NN 0.1: the single intruding point drags
  its nearest neighbour down with it under $k = 1$, while $k = 3$ outvotes it.
  The resubstitution error of 1-NN is still exactly 0, which is the separate
  true/false item "the error of a 1-NN classifier on the training set is 0"
  (**true**, E22a) [S12].
- **1R (exercise 7a)** — the per-attribute error table is the part an exam
  answer has to show: age 1 error, income 1, education 2, marital 2 out of the
  eight training rows; age wins the tie by index. The resulting three rules
  (`young → no`, `middle → yes`, `old → yes`) get all five held-out rows right,
  so accuracy = precision = recall = 1.0 against a 0R baseline of 0.4. That
  reproduces the transcript's observation on a table of the same shape.
- **Boosting (exercise 2)** — initial weights $1/3$ [S12]; the best stump errs
  on one of the two outer points, $\epsilon = 1/3$, $\alpha = \tfrac12\ln 2$,
  and the weights become $(0.5, 0.25, 0.25)$ or $(0.25, 0.25, 0.5)$ depending on
  which side the split falls. **Either is a correct answer** — the paper asks
  which point gains weight *given your own boundary*.

Exercise 7(b), the Bayesian network, is a design question with no unique answer;
[note 09](../../../notes/09-bayes.md) gives the structure-learning recipe the
course expects, and `../../py/bayesnet.py` has `fit_cpts` for the probabilities
and `hill_climb_structure` for the search.

```sh
uv run python solution.py
```
