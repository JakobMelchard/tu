# Lecture, exercise and textbook map

The course publishes no script, but its 2021S exercise notebooks [S5] and the
2021-2023 lecture videos [S11] are public, and TISS names five books [S2]. This
maps all three onto our notes and code. Whether 2027S follows the 2021S order is
**unverified**; TISS 2027S keeps the same nine topics and three exercise domains
[S2], and the lecturer's page describes the same three-part structure [S4].

## TISS topics

| # | TISS topic [S2] | videos [S11] | exercise [S5] | our note | our code |
|---|---|---|---|---|---|
| 1 | Simple optimization problems, gradient descent | Optimization 1-5 | Ex01 GD 1D, Ex02 Nesterov + chain rule, Ex03 Newton | [01](../notes/01-optimisation-and-gradient-descent.md) | none |
| 2 | Supervised learning, over-/underfitting, regularization | Learning 1-3, 5; Regression 2 | Ex04 Hooke's law, Ex05 polynomial fitting | [02](../notes/02-supervised-learning-and-regularisation.md) | none |
| 3 | Linear model, singular value decomposition | Regression 1, 4, 5; Learning 4 | Ex06 SVD and ridge, Ex07 undoing temperature | [03](../notes/03-linear-model-and-svd.md) | none |
| 4 | Non-linear models, classification problems | Regression 3 (generalised / extended linear model); Classification 1-3 | Ex08 SUSY logistic | [04](../notes/04-nonlinear-models-and-classification.md) | `classification.py` |
| 5 | Artificial neural networks | Neural Networks 1-3; Optimization 3 | Ex09 SUSY MLP | [05](../notes/05-artificial-neural-networks.md) | `nn_numpy.py` |
| 6 | Unsupervised learning, clustering | Learning 6; Clustering with k-Means | Ex10 Ising k-means | [06](../notes/06-unsupervised-learning-and-clustering.md) | `clustering_pca.py` |
| 7 | Low-rank decompositions, PCA | Low-rank 1-3 | Ex11 low-rank Ising | [07](../notes/07-low-rank-decompositions-and-pca.md) | `clustering_pca.py`, `ising.py` |
| 8 | Autoencoders | **none public** | **none public** | [08](../notes/08-autoencoders.md) | `autoencoder.py` |
| 9 | Reinforcement learning, Q learning | Learning 7, Temporal Distance Learning (2022); Reinforcement 1-2 (2023) | Ex12 CartPole | [09](../notes/09-reinforcement-learning-and-q-learning.md) | `qlearning.py` |
| - | Exercise domains: deblurring, LHC collisions, Ising phases | guest lectures Ipp (HEP), Huber (condensed matter), Grüneis (materials) | Ex07; Ex08-09; Ex10-11 | [10](../notes/10-exercise-domains.md) | `collisions.py`, `ising.py` |

Python videos 1-7 and Ex00 (JupyterHub test run) are tooling; not covered.

The weekly exercises are graded [S1]; this wiki does not map them to solutions.

## Textbook sections per note

| note | S6 Mehta et al. | S7 MML | S8 ESL | S9 ISLP | S10 Hansen (inferred ch.) |
|---|---|---|---|---|---|
| 01 | IV | 7.1, 7.3 | | 10.7 | 6 (iterative) |
| 02 | II, III, VI.B-C, VI.F | 8.2, 8.6 | 3.4, 7.2-7.3, 7.10 | 2.2, 6.2 | |
| 03 | VI.A-B | 4.5, 4.6, 9.2, 9.4 | 3.2, 3.4.1 | | 2-6, 8 |
| 04 | VII | | 4.4 | 4.3, 9 | |
| 05 | IX, XI | 5.6 | 11 | 10 | |
| 06 | XIII, XIV.B | 11 | 8.5, 14.3.6-14.3.7 | 12.4 | |
| 07 | XII.B | 4.6, 10 | 3.5.1, 14.5 | 12.2 | |
| 08 | XVII.C | 10.7 | | | |
| 09 | (not covered; use S24) | | | | |
| 10 | VII.C, IX.E, App. A | | | | 2 |
