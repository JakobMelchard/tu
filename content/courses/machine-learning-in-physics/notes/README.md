# Notes: 138.128 Machine Learning in Physics

Ordered by the TISS topic list [S2]: nine lecture topics (01-09), then the three
exercise domains (10). Each note: definitions, derivations, a worked numeric
example produced by [`../src/py`](../src/README.md), pitfalls, five test-style
questions with answers, pointers to the code. Citations `[S<n>]` refer to
[`../refs/SOURCES.md`](../refs/SOURCES.md); the map from the course's public 2021S
exercises and 2021-2023 lecture videos to these notes is
[`../refs/lecture-notes-map.md`](../refs/lecture-notes-map.md).

**Start with [00](00-exam-focus.md).** 2027S (page published): lecture
Fri 12:00-14:00 HS 6 RPL, tests Wed 05.05 and Wed 23.06.2027, grade 40 % weekly
notebooks + 2 x 30 % written tests.

General ML (evaluation, model selection, trees, SVMs, ensembles) is not repeated
here; it lives in the CSE notes
[`../../../../cse/ws2026/machine-learning/notes/`](../../machine-learning/notes/README.md),
linked from each note where relevant. These notes keep to the physics applications
and the course's own topics.

| # | Note | One line |
|---|---|---|
| **00** | [**Exam focus**](00-exam-focus.md) | **Read first.** 2027S dates and registration, the 40/30/30 arithmetic (test average needed per grade), what the tests likely ask (proxy: the 2021S notebook questions), what to verify at the intro on 03.03.2027. |
| 01 | [Optimisation and gradient descent](01-optimisation-and-gradient-descent.md) | GD on the quadratic model: stability $\eta<2/L$, rate $(\kappa-1)/(\kappa+1)$; heavy ball and Nesterov; Newton (goes to any stationary point); SGD noise floor; Adam. |
| 02 | [Supervised learning and regularisation](02-supervised-learning-and-regularisation.md) | Train/validation/test, over- and underfitting, bias-variance derivation, ridge in the SVD basis and as MAP, lasso and soft thresholding, early stopping as implicit ridge. |
| 03 | [Linear model, SVD, inverse problems](03-linear-model-and-svd.md) | Least squares via SVD, pseudo-inverse, noise amplification $\sigma/s_k$, Picard condition, Tikhonov/TSVD/Landweber filter factors, L-curve, GCV, discrepancy; **temperature deblurring** as a Fredholm problem, analytic-continuation kernel. |
| 04 | [Non-linear models and classification](04-nonlinear-models-and-classification.md) | Extended and generalised linear models, logistic regression (gradient, convexity, IRLS, separable data), softmax, kernels briefly, confusion matrix, sensitivity/specificity. |
| 05 | [Artificial neural networks](05-artificial-neural-networks.md) | Forward and backward pass derived, activations, softmax-CE gradient $P-Y$, vanishing gradients and initialisation, universal approximation, XOR, gradient checking, training tricks. |
| 06 | [Unsupervised learning and clustering](06-unsupervised-learning-and-clustering.md) | k-means (monotone, local), k-means++, GMM and EM derived via Jensen, k-means as zero-temperature EM, choosing $k$, exercise 10 on Ising observables. |
| 07 | [Low-rank decompositions and PCA](07-low-rank-decompositions-and-pca.md) | PCA as max variance and min reconstruction error, Eckart-Young, PCA via SVD, PPCA, tensor-network outlook; PC1 of Ising configurations is the magnetisation, "randomness is information". |
| 08 | [Autoencoders](08-autoencoders.md) | Linear AE = PCA subspace (Baldi-Hornik), non-linear AE on a curved manifold, denoising AE, VAE loss; physics uses (order parameters, anomaly detection). Not in the public 2021-2023 material. |
| 09 | [Reinforcement learning and Q-learning](09-reinforcement-learning-and-q-learning.md) | MDP, Bellman equations, value iteration as a contraction, Q-learning and its convergence conditions, $\varepsilon$-greedy, exercise 12 CartPole; double-well toy where the discount decides metastability. |
| 10 | [The three exercise domains](10-exercise-domains.md) | Ising phases (Metropolis, Binder cumulant, PCA, supervised $T_c$), SUSY-style collision classification (ROC, AUC, feature engineering), spectral deblurring summary. |

Suggested order: 00, then 01-03 before test 1 (05.05.2027), 04-09 before test 2
(23.06.2027); read 10 alongside the matching exercises.

Also here: `CHANGELOG.md`.
