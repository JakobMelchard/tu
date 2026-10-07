# Exam 30.06.2022 — label **E22b** (2022S)

Source: [S11], VoWi page `Exam-2022-06-30`, plus the complaint thread on [S10].
Described here in our own words; the paper is not reproduced.

**This is the paper where the format broke.** It was one of the first entirely
multiple-choice papers, a student reports that about 95 % of the questions were
new so that learning the old true/false bank did not help, and it contained
**four calculations** — convolution, gradient descent, RSS and a $k$-armed
bandit — after a Q&A session had suggested that being able to name the
algorithms and their applications would be enough [S10]. The lesson for 2026W is
that the calculation section is real and must be practised.

## What was asked

1. **$k$-armed bandit.** Five actions with their rewards are tabulated
   ($A_1 = 2, R_1 = 3$; $A_2 = 1, R_2 = -1$; …). Say **at which time steps the
   action was definitely chosen at random**, and at which it **may** have been.
2. **Gradient descent on the RSS.** Two features and one target, five samples.
   The coefficients $w_0, w_1, w_2$ are to be computed using the RSS as the
   metric with a learning rate $\alpha = 0.5$. All $w$ start at 0 — what is
   $w_1$ at the second step?

## What `solution.py` does

Neither table is public, so both run on data of the stated shape: five
(action, reward) pairs over three arms, and five rows with two features.

**Question 1.** Maintain $Q(a) = 0$ and $N(a) = 0$; at each step compare the
action taken with $\arg\max_a Q_t(a)$ *before* the reward is applied, then
update $Q(A) \mathrel{+}= \frac1{N(A)}[R - Q(A)]$. On our trace the answer is:
steps 2, 4 and 5 were **definitely** exploratory, steps 1 and 3 only
**possibly** so — step 1 because all arms tie at $Q = 0$, step 3 because the
action taken *is* the unique maximiser and $\varepsilon$-greedy takes the greedy
action most of the time. The distinction between "definitely" and "possibly" is
the entire content of the question. `../../py/bandits.py`
(`bandit_random_action_analysis`) prints the table.

**Question 2.** With all weights zero the residual is the target itself, so
$$w_j \;\leftarrow\; 0 + 2\alpha\sum_i y_i x_{ij}$$
for the plain-RSS gradient. **But the answer depends on the convention**, and
the paper does not state one: the course's formula sheet [S13] writes the loss
as $\frac1{2m}\sum(y - \hat y)^2$, whose gradient is $\frac1m$ times the
residual-weighted feature sum, a factor $2m = 10$ smaller. On our numbers
$w_1 = 158$ under plain RSS and $w_1 = 15.8$ under the scaled loss. In a
multiple-choice paper, compute both and pick whichever appears among the
options; in a written answer, say which convention you used.

Two by-products worth noticing: with unscaled features, $\alpha = 0.5$ makes the
iteration overshoot immediately (the second step swings to $-700$), which is the
practical reason feature scaling matters for gradient descent
([note 08](../../../notes/08-linear-models.md)); and "the second step" is
ambiguous in the transcript, so the code prints the whole short history.

```sh
uv run python solution.py
```
