# 16 ML security, privacy, explainability — and MLOps

> Lecture units 14 and 15 [S18]. Exam weight ● — lectured but barely examined; budget accordingly. Sources: [`../refs/SOURCES.md`](../refs/SOURCES.md).

## What it is

Lecture units 14 and 15 [S18], taught by Rudolf Mayer, whose group at SBA
Research works on exactly this [S8]; the continuative course 194.055 *Security,
Privacy and Explainability in Machine Learning* [S1] is the full version.

**Exam weight: low but non-zero.** The archive shows transfer-learning items
("off-the-shelf", freezing) in several papers and one explicit deep-learning
robustness item ("a CNN given a pure white image outputs equal probabilities for
all classes" — **false**, E21b) [S12], but no paper in the archive asks about
adversarial examples, differential privacy or MLOps directly. The unit is
covered here because it is lectured [S18] and because a two-point true/false
item from it costs nothing to prepare for. Spend twenty minutes, not an
afternoon.

## What can go wrong: the attack taxonomy

Attacks are classified by which security property they break [S18]:

| goal | what the attacker achieves | example |
|---|---|---|
| **integrity** | the model behaves wrongly on chosen inputs | adversarial examples, backdoors |
| **confidentiality** | sensitive data or the model itself leaks | membership inference, model inversion, model extraction |
| **availability** | the service degrades or stops | poisoning that destroys accuracy, resource exhaustion |

The quality dimensions the lecture measures a model on, beyond accuracy:
**privacy, robustness, interpretability, fairness** [S18].

## Adversarial examples

A minimal perturbation $\delta$ of an input $x$ such that the model
misclassifies $x + \delta$ while a human sees no change. Formally
$\min\|\delta\|$ subject to $h(x+\delta) \ne h(x)$ — a search for the nearest
point across the decision boundary.

- **Greedy / boundary search**: probe around the classification boundary.
  Works, but needs many queries.
- **Fast gradient sign method (FGSM)** [S39] — the one with a formula:
  $$x' = x + \varepsilon\,\operatorname{sign}\big(\nabla_x J(\theta, x, y)\big).$$
  One backward pass through the *same* loss the model was trained with, then a
  step of fixed size $\varepsilon$ in every coordinate in the direction that
  increases the loss. Cheap and effective; success is not guaranteed (reported
  at roughly 60–70 % in the lecture material [S18]).
- Why it works [S39]: in high dimensions a linear model already accumulates
  $\varepsilon\|w\|_1$ of change from a per-pixel perturbation of size
  $\varepsilon$, so *excessive linearity*, not excessive non-linearity, is the
  cause. Adversarial training (adding $x'$ to the training set) is the basic
  defence.
- **White box** (gradients available) vs **black box** (only queries); black-box
  attacks exploit **transferability** — an adversarial example built against a
  surrogate often fools the target.

## Backdoor / poisoning attacks

Insert poisoned training data so that inputs carrying a **trigger** (a sticker,
a pixel pattern, a rare token) are misclassified into an attacker-chosen class,
while clean accuracy is unchanged so the attack is invisible in the test
metrics. Works best on **over-parameterised models that overfit**, which have
capacity to memorise the trigger [S18]. Defences: data provenance, training-set
inspection, activation clustering, fine-tuning/pruning on clean data.

## Explainable AI

White-box models (linear models, small trees, rule sets — note 06) are
interpretable by construction; black-box models need to be explained after the
fact. The lecture's taxonomy [S18]:

| axis | values |
|---|---|
| **when** | *ex-ante* (before/independent of the model: feature distributions, correlations, bias audits) · *intrinsic* (the model's own structure explains it) · *post-hoc* (explain a trained black box) |
| **scope** | *local* (why this prediction) vs *global* (how the model behaves overall) |
| **applicability** | *model-specific* (needs gradients, tree structure) vs *model-agnostic* (only needs a predict function) |

Post-hoc techniques named: activation/saliency maps, textual explanations,
**counterfactuals** ("change income by +2k and the decision flips"), and
**anchors** (the minimal set of input parts that pins the prediction) [S18].
Permutation feature importance (note 07) and partial-dependence plots are the
model-agnostic global pair we actually implement.

## Privacy

| threat | what leaks |
|---|---|
| **identity disclosure / re-identification** | who a record belongs to, by joining quasi-identifiers |
| **attribute disclosure** | a sensitive value of a known individual |
| **membership disclosure** | whether a given record was in the training set |

Defences [S18]:

- **Data sanitisation**: remove direct identifiers; **$k$-anonymity** (every
  record is indistinguishable from $k-1$ others on the quasi-identifiers), plus
  $\ell$-diversity and $t$-closeness for the attribute-disclosure gap; synthetic
  data.
- **Differential privacy**: a randomised mechanism $M$ is $\varepsilon$-DP if for
  neighbouring data sets $D, D'$ differing in one record,
  $\Pr[M(D) \in S] \le e^{\varepsilon}\Pr[M(D') \in S]$. Add calibrated noise
  (Laplace or Gaussian) to the query, the gradients (DP-SGD) or the output. The
  guarantee is about the *mechanism*, not the data, and $\varepsilon$ is a
  privacy budget that composes over queries.
- **Federated learning**: the data stays on the device; only model updates are
  shared (which still leak — combine with DP and secure aggregation).
- **Secure computation**: secure multi-party computation, homomorphic
  encryption.

**Attacks on the model itself** [S18]:

- **Membership inference**: query the model repeatedly and exploit that it is
  more confident on training points; works when the model overfits — the same
  root cause as backdoors.
- **Model inversion**: reconstruct a representative training input by
  maximising the model's confidence for a target label.
- **Model extraction**: query enough to fit a surrogate that copies the
  decision function — stealing the model, and then attacking it as a white box.

## MLOps

Lecture unit 15 [S18]; nothing in the archive examines it.

**The ML lifecycle** is a loop, not a pipeline: (1) data engineering,
(2) training, (3) evaluation and validation — including unit and integration
tests of the pipeline, not just model metrics, (4) deployment, (5) monitoring,
re-evaluation and experimentation (continuous learning, A/B tests, user
studies), back to (1).

**Infrastructure** [S18]:

| layer | components |
|---|---|
| storage | **data lake** (raw training data, cheap object storage) · **feature store** (computed features, must be readable at *prediction* latency and must match what training used) · **model store** (versioned, containerised models) |
| compute | **training systems** (distributed, Kubernetes/Spark) vs **inference systems** (containerised low-latency services) |

The recurring failure mode is **training/serving skew**: the feature computed
online differs from the one computed offline. A shared feature store exists to
prevent it — it is the production version of the leakage discipline in note 01.
The lecture's forward-looking claim: smaller datasets and smaller, highly
specialised, composable models rather than one monolith [S18].

## Worked example

**FGSM on a linear model, by hand.** A logistic classifier with
$w = (2, -1, 0.5)$, $b = 0$, input $x = (0.4, 0.9, -0.2)$, true label $y = 1$.
The score is $w^\top x = 0.8 - 0.9 - 0.1 = -0.2$, so the model already leans
negative; the loss gradient with respect to $x$ is $-(1 - \sigma(w^\top x))\,w$,
whose sign is $-\operatorname{sign}(w) = (-1, +1, -1)$. With
$\varepsilon = 0.1$:
$$x' = (0.4, 0.9, -0.2) + 0.1\,(-1, +1, -1) = (0.3, 1.0, -0.3),$$
score $0.6 - 1.0 - 0.15 = -0.55$. A perturbation of $0.1$ per coordinate moved
the score by $-0.35 = -\varepsilon\|w\|_1$. That is the linearity argument of
[S39] in three dimensions: the damage grows with the *number* of input
coordinates, which is why it is devastating on images.

**Membership inference, why overfitting is the cause.** A model with training
accuracy 1.00 and test accuracy 0.72 assigns systematically higher confidence to
training points. An attacker who can query it and knows the confidence
distribution of non-members can classify membership well above chance. Shrink
the train/test gap — regularise, augment, or add DP noise — and the signal
disappears.

## Pitfalls

- Thinking accuracy is the only quality axis. Robustness, privacy, fairness and
  interpretability are separate, and can trade off against accuracy.
- Assuming an adversarial example needs white-box access: they transfer.
- Treating anonymisation as privacy. Removing names does not stop
  re-identification by quasi-identifiers; $k$-anonymity does not stop attribute
  disclosure; only a formal guarantee like DP quantifies the leak.
- Believing federated learning is private on its own — gradients leak.
- Reading feature importance or a saliency map as a causal explanation.
- Deploying a model without monitoring for drift, or computing features
  differently online and offline.
- Spending exam preparation time here proportional to the lecture time rather
  than to the archive weight, which is near zero.

## Exam-style questions

1. **A CNN trained on ImageNet is given a completely white image. Will the
   output probabilities be equal for all classes?** *(E21b.)* **No.** The
   network computes a deterministic function; a uniform input still produces
   some activation pattern, and the logits will reflect the learned biases and
   whichever class the features happen to favour. Equality would require a
   symmetry the trained weights do not have.
2. **Write the fast gradient sign method and explain each part.** *(ours — the
   archive names the topic but no paper asks for the formula.)*
   $x' = x + \varepsilon\operatorname{sign}(\nabla_x J(\theta, x, y))$: the
   gradient of the *training* loss with respect to the **input**, its sign
   (so every coordinate moves by the same amount), and a step $\varepsilon$
   small enough to be imperceptible. One backward pass; needs white-box access,
   but the result often transfers.
3. **What is a backdoor attack, and why do overfitting models suffer most?**
   *(ours.)* Poison the training data so that a trigger pattern forces an
   attacker-chosen label while clean accuracy is unchanged. A model with spare
   capacity memorises the trigger as a separate rule instead of being forced to
   trade it off against clean performance — so the attack stays invisible in the
   test metrics.
4. **Distinguish $k$-anonymity from differential privacy.** *(ours.)*
   $k$-anonymity is a syntactic property of a *released table*: each record's
   quasi-identifiers match at least $k-1$ others. It does not bound attribute
   disclosure and breaks under joins. Differential privacy is a property of the
   *mechanism*: one record's presence changes any output probability by at most
   $e^{\varepsilon}$, whatever the attacker knows, and it composes across
   queries.
5. **Name the three types of post-hoc explanation the lecture distinguishes and
   give one technique for each.** *(ours.)* Ex-ante (feature distributions,
   correlation and bias audits before modelling), intrinsic (a small tree or a
   linear model reads as its own explanation), post-hoc (saliency/activation
   maps, counterfactuals, anchors, permutation importance) — crossed with
   local vs global and specific vs agnostic.
6. **What is training/serving skew and what infrastructure prevents it?**
   *(ours.)* The features computed at inference time differ from those the model
   was trained on — different code paths, different aggregation windows, stale
   data. A shared feature store computes each feature once and serves it to both
   training and inference; it is the production form of "fit the transformation
   inside the pipeline" (note 01).

## Code

None. This note is conceptual and the archive does not ask for calculations
from it. The nearest implementations elsewhere in `src/` are
`ensemble.permutation_importance` (a model-agnostic global explanation) and
`mlp.MLP` with dropout / $L_2$ / early stopping, which is the same overfitting
control that shrinks the membership-inference signal.
