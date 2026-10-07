# Map: what the course builds on, and where we cover it

**138.129 publishes no lecture notes and no literature** [S1]. It builds on
138.128 Machine Learning in Physics [S1, S4], whose public material is
Wallerberger's exercise notebooks and lecture videos [S6], and, for the
compression themes, on the lecturers' papers. This file maps both onto our notes
and code, so that a topic discussion can start from a shared reference.

## 138.128 exercise notebooks [S6] (github.com/mwallerb/ml-phys-exercises, 2021 version)

| notebook | topic | our note | our code |
|---|---|---|---|
| Ex01 GradientDescent, Ex02 AdvancedGD, Ex03 Newton | optimisation | 04 (Adam training), 06 (Newton on the MaxEnt dual), 07 (Newton for logistic regression) | `autoencoder_compression.train`, `continuation.maxent`, `observables.logistic_newton` |
| Ex04 LinearRegression, Ex05 PolyFitting, Ex07 Convergence | least squares, regularisation, model selection | 06 (Tikhonov), 07 (ridge, kernel ridge) | `continuation.tikhonov`, `observables.ridge`, `observables.kernel_ridge` |
| Ex06 SVD, Ex11 LowRankApprox | SVD, low-rank approximation | **02**, 03, 05 | `lowrank.py`, `ir_toy.py`, `tt_svd.py` |
| Ex08 LogisticRegression | classification | 07 | `observables.logistic_newton` |
| Ex09 NeuralNets | MLPs | 04, 07 | `MLPAE`, `MLPClassifier` |
| Ex10 Clustering | unsupervised learning | 04 (PCA / AE as unsupervised order parameters) | `lowrank.pca`, `autoencoder_compression` |
| Ex12 Reinforcement | RL | not covered (no project theme on TISS points there) | |

The notebook list is from the 2021 repository; the 2027S course may differ
(re-check after taking it). Solutions are not public [S6].

## Papers behind the likely project themes

| source | sections to read | our note | our code |
|---|---|---|---|
| S13 sparse-ir (SoftwareX 2023) | 2 (IR and sparse sampling), 4 (package anatomy: SVE discretisation, sampling) | 03 | `ir_toy.IRBasis` |
| S10 Shinaoka et al. 2017 | IR definition, compactness for QMC data | 03 | `ir_toy.rho_coefficients` |
| S11 irbasis | precomputed basis database (predecessor of sparse-ir) | 03 | |
| S12 Li et al. 2020 | sparse sampling points and conditioning | 03 | `tau_sampling_points`, `matsubara_sampling_points` |
| S15 Shinaoka et al. 2020 | two-particle sparse sampling, tensor-network compression | 03, 05 | |
| S16, S32, S34 quantics TT / TCI / parquet | multiscale ansatz, TCI cost, two-particle applications | 05 | `tt_svd.quantics` |
| S18 Halko-Martinsson-Tropp | Alg. 4.1, 4.4, 5.1; Thm 10.5 | 02 | `lowrank.range_finder`, `randomized_svd` |
| S24 Orús, S25 Schollwöck | MPS, area laws, SVD truncation | 05 | `tt_svd.tt_svd` |
| S21 Kingma-Welling, S22 Wetzel, S33 Ballé | VAE, PCA/VAE on Ising, learned transform coding | 04 | `VAE`, `compare` |
| S23 Carrasquilla-Melko | supervised phase classification | 07 | `MLPClassifier`, `estimate_tc` |
| S27 Jarrell-Gubernatis, S28 ana_cont, S29 Yoon et al., S30 Hansen | MaxEnt, $\alpha$ selection, learned continuation, discrete inverse problems | 06 | `continuation.py` |
| S17 Mehta et al. | general ML for physicists; Ising datasets | 04, 07 | `ising_snapshots.py` |
