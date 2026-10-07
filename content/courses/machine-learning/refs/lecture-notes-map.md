# Lecture map — what the course covers, how heavily it is examined, where we cover it

There is **no lecture script** for 184.702. TISS says so outright ("No lecture
notes are available." [S1]) and none of the five lecturers hosts material
publicly [S5–S9]; everything is in TUWEL. So this map is reconstructed from two
independent sources and says which one supports each row:

- **order** — the unit sequence of a student summary written from the slides
  [S18]. This is the only evidence of the lecture order that exists outside
  TUWEL.
- **weight** — how often the unit appears across the 19 past papers
  [S11, S18], digested in [`../notes/00-exam-focus.md`](../notes/00-exam-focus.md).

`●●●` = in nearly every paper · `●●` = recurring · `●` = seen once or twice ·
`—` = taught but never seen in a paper.

## The lecture, in order

| # | lecture unit [S18] | exam weight | our note | our code |
|---|---|---|---|---|
| 1 | ML basics: paradigms, prediction types, data types (nominal/ordinal/interval/ratio) | ●● | [01](../notes/01-learning-setup.md) | — |
| 2 | Preprocessing: encoding, scaling, binning, missing values, sampling, feature extraction/selection, data augmentation | ●●● | [02](../notes/02-preprocessing.md) | `preprocessing.py` |
| 3 | Evaluation: confusion matrix, classification and regression metrics, hold-out / $k$-fold / leave-$p$-out / bootstrap, significance tests | ●●● | [03](../notes/03-evaluation.md) | `metrics.py`, `model_selection.py` |
| 4 | kNN and distance metrics | ●●● | [05](../notes/05-knn.md) | `knn.py` |
| 5 | Decision trees, and the rule learners around them (0R, 1R, covering) | ●●● | [06](../notes/06-decision-trees.md) | `tree.py`, **`rules.py`** |
| 6 | Naive Bayes | ●●● | [09](../notes/09-bayes.md) | `bayes.py` |
| 7 | Bayesian networks: structure, CPTs, chain rule, d-separation, inference, structure learning by local search | ●●● | [09](../notes/09-bayes.md) | **`bayesnet.py`** |
| 8 | SVM: margin, support vectors, soft margin, kernels | ●●● | [10](../notes/10-svm.md) | `svm.py` |
| 9 | Perceptron and MLP: activations, backpropagation, gradient descent | ●●● | [11](../notes/11-neural-networks.md) | `mlp.py` |
| 10 | Deep learning: CNNs (convolution, padding, stride, pooling, architectures), RNNs, regularisation of deep nets, vanishing gradients | ●●● | **[13](../notes/13-deep-learning.md)** | **`conv.py`**, `mlp.py` |
| 11 | Reinforcement learning: $k$-armed bandits, exploration/exploitation, MDPs, tabular Monte-Carlo methods | ●●● | **[14](../notes/14-reinforcement-learning.md)** | **`bandits.py`**, **`rl.py`** |
| 12 | Combining models: transfer learning (off-the-shelf, freezing, fine-tuning), model selection, ensembles (bagging, random forests, AdaBoost, gradient boosting) | ●●● | [07](../notes/07-ensembles.md), [13](../notes/13-deep-learning.md) §transfer | `ensemble.py` |
| 13 | AutoML: no-free-lunch, Rice's framework, landmarking and metalearning features, hyperparameter optimisation, AutoML systems | ●●● | **[15](../notes/15-automl-and-metalearning.md)** | `model_selection.py` |
| 14 | ML security, privacy and explainability: adversarial examples, backdoors, XAI, differential privacy, inference/inversion attacks | ● | **[16](../notes/16-ml-security-privacy-and-mlops.md)** | — |
| 15 | MLOps: the ML lifecycle, data lake / feature store / model store, training vs inference systems | — | [16](../notes/16-ml-security-privacy-and-mlops.md) §MLOps | — |

Two further blocks are examined but do not appear as units in [S18]:

| topic | exam weight | our note | our code | evidence |
|---|---|---|---|---|
| Linear and polynomial regression, gradient descent vs normal equations, ridge vs lasso | ●●● | [08](../notes/08-linear-models.md) | `linear.py` | asked in E17b, E18a, E19a, E21a–d, E22a, E22b, E24a, E25b, E26a — one of the most-asked topics of all [S11, S12] |
| Model selection and overfitting as a topic of its own (the TISS subject line names it) | ●● | [04](../notes/04-model-selection.md) | `model_selection.py` | [S1]; exam questions on overfitting measures, learning curves and hyperparameter search |
| Clustering ($k$-means, hierarchical, DBSCAN) and PCA | ● | [12](../notes/12-unsupervised.md) | `clustering.py`, `pca.py` | [S1] names unsupervised learning; PCA appears in the exams only as "PCA is a supervised feature-selection method — false" (E17b, E22a). $k$-means and PCA are examined properly in the *sibling* course 192.183 [S4, S16], not here |
| Hidden Markov models | ● (historical) | [09](../notes/09-bayes.md) §HMM | — | E17a and E17b only [S11, S43]; no paper after 2017 mentions them |

## Why our numbering is not the lecture's

The notes are numbered by topic group, not by lecture date, and the numbering
predates this pass. Renumbering would break every cross-reference for a
lecture order that rests on a *single secondary source* [S18]. The mapping is
this table; the divergences are only:

- **08 Linear models** is taught inside the regression/gradient-descent thread
  that [S18] folds into its MLP chapter, not as its own unit.
- **07 Ensembles** is lecture unit 12 ("combining models"), i.e. after the
  neural-network units, not before them.
- **12 Unsupervised** has no fixed position; [S1] names it in the subject line
  and [S18] covers PCA under feature selection.

## What changed about scope in this pass

Before this pass the notes covered lecture units 1–9 and 12 and stopped. The
exam archive shows that units 10, 11, 13 and 14 — **deep learning, reinforcement
learning, AutoML/metalearning and ML security** — are examined, several of them
in *every recent paper*: the three-section papers of 2024–2026 devote most of
their calculation section to a $k$-armed bandit, a convolution or a pooling
operation, and 1R [S11, S12]. Four new notes and three new modules close that
gap; see `../notes/CHANGELOG.md`.

## Scope boundary against the sibling course

**192.183 Machine Learning** (6.0 ECTS, Bellec/Musliu/Marty, first run 2026S)
is a different, larger course for the new Logic-and-AI, Software-Engineering and
Business-Informatics curricula [S4]. It shares Musliu and much of the syllabus
but adds learning theory and a much heavier deep-learning component. Its
2026-06-23 paper is on VoWi under the *same* wiki page [S16] and is **not a
model for this exam**: it asks for int8 ranges, FLOP counts of $Wx$,
initialisation scales, the softmax-cross-entropy derivative and the peak memory
of back-propagation. 184.702's papers never do. Do not study it for 184.702.
