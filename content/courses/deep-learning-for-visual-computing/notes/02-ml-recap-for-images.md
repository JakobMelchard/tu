# 02 Recap: machine learning for images

> TISS item 2, "overview, parametric models, iterative optimization" [S1, S3].
> Catalogue weight: the heaviest block, eleven question families [S7-S9], see
> [00](00-exam-focus.md). Books: Goodfellow ch. 5, 8 [S11]; Drori ch. 3 [S12].
> **Already covered for 184.702**, read those instead of re-deriving:
> [ML 03 evaluation](../../machine-learning/notes/03-evaluation.md),
> [ML 04 model selection](../../machine-learning/notes/04-model-selection.md),
> [ML 05 kNN](../../machine-learning/notes/05-knn.md),
> [ML 08 linear models](../../machine-learning/notes/08-linear-models.md),
> [ADL 01 training fundamentals](../../applied-deep-learning/notes/01-training-fundamentals.md)
> (losses, optimisers, schedules). This note keeps only the image-specific
> framing and the forms the DLVC catalogue asks for.

## What it is

Supervised learning with $x \in \mathbb R^{C\times H\times W}$, a finite label
set, and a **parametric model** $f_\theta$: a fixed functional form whose
behaviour is set entirely by $\theta$, learned by minimising an empirical loss
with an iterative method. Contrast: kNN is non-parametric (it stores the data).

## Definitions and results

**Splits.** Train (fit $\theta$), validation (choose hyperparameters, early
stopping), test (one final estimate). Using the test set for any decision
makes its estimate optimistic [S8].

**kNN on pixels** [S8, S9]. Predict the majority label of the $k$ nearest
training images under $L_1$ or $L_2$. Limitations: prediction costs
$O(nD)$; pixel distance is not semantic (a shifted or re-lit image is far,
a different object on the same background near); curse of dimensionality
($D = 3072$ for CIFAR-10).

**Linear classifier.** Flatten $x \in \mathbb R^D$; scores $s = Wx + b$,
$W \in \mathbb R^{K\times D}$, $b \in \mathbb R^K$. Each row $w_k$ is a
template; the decision boundary between $k$ and $l$ is the hyperplane
$(w_k - w_l)^\top x + b_k - b_l = 0$, so $K$ classes in 2-D give a partition
into convex cells [S9]. $KD + K$ parameters: 30 730 for CIFAR-10.

**Class scores and softmax.** Scores are unbounded logits. Softmax
$p_k = e^{s_k}/\sum_j e^{s_j}$ maps them to a probability vector: positive,
sums to 1, order-preserving, invariant to $s \mapsto s + c\mathbf 1$ (subtract
$\max_j s_j$ before exponentiating).

**Cross-entropy.** For a target distribution $u$ (one-hot for hard labels) and
prediction $p$: $H(u, p) = -\sum_k u_k \log p_k = H(u) + \mathrm{KL}(u\|p)$.
It measures the mismatch between two distributions; its minimum over $p$ is
at $p = u$. The catalogue's "criteria" question [S7, S8]: both arguments must
be probability mass functions, ensured by one-hot (or mixup / label-smoothed)
targets and a softmax on the scores. Gradient (derive once):
$$ \frac{\partial H}{\partial s_k} = p_k - u_k. $$

**Gradient descent.** $\theta \leftarrow \theta - \eta \nabla_\theta L$.
$\nabla L$ points to the steepest ascent; the *learning rate* $\eta$ is a
hyperparameter, the *step size* $\eta\|\nabla L\|$ is what actually moves
$\theta$ and shrinks as the gradient does. Batch GD uses all $n$ samples,
SGD one, **minibatch** $B$ samples: unbiased gradient estimate with variance
$\propto 1/B$, vectorises on a GPU, and the noise helps leave sharp minima.
One **epoch** = one pass over the training set.

**Local minima.** In high dimension most critical points of a network loss
are saddle points; local minima found by SGD tend to have losses close to
the global one, so poor local minima are rarely the bottleneck [S11 §8.2].

**Momentum** (heavy ball). $v \leftarrow \beta v - \eta \nabla L$,
$\theta \leftarrow \theta + v$. For a constant gradient the velocity
converges to $-\eta\nabla L/(1-\beta)$: an effective rate $10\eta$ at
$\beta = 0.9$. On a quadratic with Hessian eigenvalues in $[\mu, \lambda]$,
condition number $\kappa = \lambda/\mu$, the best contraction per step is
$(\kappa-1)/(\kappa+1)$ for GD and $(\sqrt\kappa-1)/(\sqrt\kappa+1)$ with
tuned momentum: oscillations across a ravine cancel, progress along it
accumulates.

**Adam** [S20]. $m \leftarrow \beta_1 m + (1-\beta_1)g$,
$v \leftarrow \beta_2 v + (1-\beta_2)g^2$, bias-corrected
$\hat m = m/(1-\beta_1^t)$, $\hat v = v/(1-\beta_2^t)$,
$\theta \leftarrow \theta - \eta\,\hat m/(\sqrt{\hat v}+\epsilon)$. Momentum on
the gradient plus a per-parameter scale (RMSProp): directions with large or
noisy gradients get smaller steps, so $\eta$ is less critical.

**Capacity, under- and overfitting.** Training error falls with capacity;
test error is U-shaped. Underfitting: both errors high and close.
Overfitting: training error low, validation error rising. The optimal
capacity grows with $n$ [S9]. In deep learning the practical rule is a large
model plus regularisation (note 08) rather than a small model.

## Worked example

**Softmax and cross-entropy.** Scores $s = (2, 1, -1)$, true class 0.
$e^s = (7.389, 2.718, 0.368)$, sum 10.475, $p = (0.705, 0.259, 0.035)$.
$L = -\ln 0.705 = 0.349$. $\partial L/\partial s = p - u = (-0.295, 0.259,
0.035)$: the true score is pushed up, the others down in proportion to their
probability. Doubling all scores to $(4, 2, -2)$ gives $p_0 = 0.879$,
$L = 0.129$: cross-entropy keeps rewarding confidence, which is why an
unregularised linear model on separable data drives $\|W\| \to \infty$.

**Momentum on a ravine.** $L = \tfrac12(x^2 + 20y^2)$, $\kappa = 20$. GD is
stable for $\eta < 2/20 = 0.1$; at the best $\eta = 2/21$ both directions
contract by $19/21 = 0.905$ per step, 23 steps per decade. Tuned heavy ball:
$(\sqrt{20}-1)/(\sqrt{20}+1) = 0.634$, 5 steps per decade.

**Adam's first step.** $t = 1$: $\hat m = g$, $\hat v = g^2$, so the update is
$-\eta\, g/(|g| + \epsilon) \approx -\eta\,\mathrm{sign}(g)$ per parameter,
independent of the gradient scale.

## Pitfalls

- Softmax without subtracting the maximum overflows for scores near 100.
- Reporting validation accuracy as the final result after tuning on it.
- "Momentum lets SGD accept worse solutions to escape local minima" (student
  answer in [S7]): it does neither on purpose; it averages gradients over
  steps, damping oscillation and accelerating consistent directions.
- Confusing learning rate (set) with step size (resulting).
- Minibatch size and learning rate are coupled: larger $B$ allows larger $\eta$
  (roughly linear scaling with warm-up); changing one alone changes training.

## Exam-style questions

1. **What is a parametric model; what do its parameters control and how are
   they set?** *(17, 20)* Fixed form $f_\theta$; $\theta$ determines the
   mapping (for a linear classifier, the class templates and offsets, hence the
   decision hyperplanes); set by minimising the training loss with gradient
   descent, not stored data.
2. **Sketch a linear classifier for 3 classes in 2-D; relate the boundaries
   to the outputs.** *(17, 20, 22)* Three lines $s_k = s_l$ meeting in a point,
   partitioning the plane into three convex cells where each $s_k$ is the
   maximum. $W$ is $3\times2$, $b \in \mathbb R^3$.
3. **What does cross-entropy measure, and what must labels and scores
   satisfy?** *(17, 20, 21, 22)* $H(u,p) = H(u) + \mathrm{KL}(u\|p)$, the
   mismatch of two distributions; both must be PMFs: one-hot labels, softmax
   scores.
4. **Are local minima a problem in deep learning? What is momentum and why
   does it help?** *(17, 20, 21, 22)* Rarely: saddle points dominate and most
   minima are near-optimal. Momentum keeps an exponential average of past
   gradients: on ill-conditioned losses it cancels the oscillating component
   and accelerates along consistent directions ($\sqrt\kappa$ vs $\kappa$).
5. **Write minibatch training with validation and early stopping as
   pseudo-code.** *(17)*
   `best=inf; patience=p; for epoch in 1..E: shuffle; for batch: loss, grad = f(batch); step(grad);`
   `val = evaluate(val_set); if val < best: best=val; save(); wait=0 else: wait+=1; if wait==p: break; load(best)`.

## Code

- `src/py/backprop_scratch.py`: `softmax`, `mlp_loss_and_grads` (the $p - u$
  gradient), `train_mlp` (plain GD).
- `src/py/cnn_synthetic.py`: `train` (minibatch Adam with a cosine schedule,
  per-epoch shuffle), `accuracy`.
