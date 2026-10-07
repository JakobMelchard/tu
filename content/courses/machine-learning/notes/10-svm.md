# 10 Support vector machines

> Lecture unit 8 [S18]. Exam weight ●●● , almost entirely as true/false statements rather than as calculations. Sources: [`../refs/SOURCES.md`](../refs/SOURCES.md).

## Maximum-margin classifier (hard margin)

The original formulation is Cortes & Vapnik [S35]; the dual and KKT treatment
below follows [S24].


Linearly separable data $y_i \in \{\pm1\}$, hyperplane $w^\top x + b = 0$. Distance of $x_i$ to it: $\frac{|w^\top x_i + b|}{\|w\|}$. Scale $w, b$ so the closest points satisfy $y_i(w^\top x_i + b) = 1$; the margin (half-width of the empty band) is $1/\|w\|$. Maximising it:
$$\min_{w, b}\ \tfrac12\|w\|^2 \quad \text{s.t. } y_i(w^\top x_i + b) \ge 1\ \ \forall i .$$
A convex QP with a unique solution. Points with $y_i(w^\top x_i + b) = 1$ are the **support vectors**; only they determine $w$.

## Soft margin

Non-separable data: slack $\xi_i \ge 0$, $y_i(w^\top x_i + b) \ge 1 - \xi_i$,
$$\min_{w,b,\xi}\ \tfrac12\|w\|^2 + C\sum_i \xi_i \quad\Longleftrightarrow\quad \min_{w,b}\ \tfrac12\|w\|^2 + C\sum_i \max\big(0,\ 1 - y_i(w^\top x_i + b)\big).$$
The second form is $L_2$-regularised **hinge loss** minimisation: $\lambda = 1/(Cn)$ per-sample. $C$ trades margin width against violations: large $C$ → few violations, narrow margin, low bias / high variance (overfits); small $C$ → wide margin, many points inside it, smoother. $0 < \xi_i < 1$: inside the margin but correctly classified; $\xi_i > 1$: misclassified.

## Lagrangian dual

Lagrangian $L = \frac12\|w\|^2 + C\sum\xi_i - \sum_i\alpha_i[y_i(w^\top x_i + b) - 1 + \xi_i] - \sum_i \mu_i\xi_i$. Stationarity: $\partial_w L = 0 \Rightarrow w = \sum_i \alpha_i y_i x_i$; $\partial_b L = 0 \Rightarrow \sum_i\alpha_i y_i = 0$; $\partial_{\xi} L = 0 \Rightarrow \alpha_i = C - \mu_i \le C$. Substituting:
$$\max_\alpha\ \sum_i \alpha_i - \tfrac12\sum_{i,j}\alpha_i\alpha_j y_i y_j\, x_i^\top x_j \quad \text{s.t. } 0 \le \alpha_i \le C,\ \sum_i \alpha_i y_i = 0 .$$
KKT complementary slackness: $\alpha_i = 0 \Rightarrow$ outside the margin; $0 < \alpha_i < C \Rightarrow$ exactly on the margin ($\xi_i = 0$, used to compute $b = y_i - w^\top x_i$); $\alpha_i = C \Rightarrow$ inside or misclassified. Decision function $f(x) = \sum_{i \in SV}\alpha_i y_i\, x_i^\top x + b$: data enter only through inner products → **kernel trick**.

## Kernels

Replace $x_i^\top x_j$ by $K(x_i, x_j) = \phi(x_i)^\top\phi(x_j)$ for a feature map $\phi$ that is never computed. Mercer: any symmetric positive semi-definite $K$ is an inner product in some (possibly infinite-dimensional) space.

| Kernel | $K(x, z)$ | Feature space |
|---|---|---|
| linear | $x^\top z$ | $\mathbb R^d$ |
| polynomial | $(\gamma\, x^\top z + r)^p$ | all monomials up to degree $p$ |
| RBF (Gaussian) | $\exp(-\gamma\|x - z\|^2)$, $\gamma = 1/(2\sigma^2)$ | infinite-dimensional; every finite set is separable |
| sigmoid | $\tanh(\gamma x^\top z + r)$ | not PSD for all parameters |

$\gamma$ in RBF: large $\gamma$ → narrow bumps, each SV influences only its vicinity, wiggly boundary, overfits (many SVs); small $\gamma$ → nearly linear boundary, underfits. $C$ and $\gamma$ are tuned jointly on a log grid (e.g. $C \in 10^{-2..3}$, $\gamma \in 10^{-3..1}$); scale features first (the kernel is distance-based). sklearn's `gamma="scale"` $= 1/(d\cdot\operatorname{Var}(X))$. Kernels can be combined: sums and products of kernels are kernels; string, graph and set kernels exist.

## Solving

- **Primal, linear**: sub-gradient / SGD on the hinge objective. Pegasos: at step $t$, $\eta_t = 1/(\lambda t)$, $w \leftarrow (1 - \eta_t\lambda)w + \eta_t y_i x_i[\text{margin} < 1]$. $O(d)$ per step, scales to millions of samples; `LinearSVC`/liblinear use coordinate descent on the dual.
- **Dual, kernel**: QP with $n$ variables. **SMO** (Platt): pick two $\alpha$s, solve their 2-variable problem analytically (the equality constraint fixes one given the other: clip to $[L, H]$), update $b$, repeat until KKT holds within tolerance. `libsvm`/`SVC`: $O(n^2)$–$O(n^3)$, memory for the kernel matrix; impractical beyond $\sim 10^5$ samples (use Nyström / random Fourier features + linear SVM).
- Multiclass: one-vs-rest ($K$ machines) or one-vs-one ($K(K-1)/2$, libsvm default).
- Probabilities: not native; Platt scaling fits a sigmoid to $f(x)$ on held-out data.
- Regression: $\varepsilon$-SVR with the $\varepsilon$-insensitive loss $\max(0, |y - f(x)| - \varepsilon)$; support vectors are the points outside the tube.

## Worked example

Points $x_1 = (1, 1), y = +1$; $x_2 = (2, 2), y = +1$; $x_3 = (0, 0), y = -1$. By symmetry $w \propto (1, 1)$. Closest opposite points: $x_1$ and $x_3$, distance $\sqrt2$, so the margin is $\sqrt2/2$ and $\|w\| = 1/(\sqrt2/2) = \sqrt2$: $w = (1, 1)$. From $w^\top x_1 + b = 1 \Rightarrow b = -1$; check $w^\top x_3 + b = -1$ ✓, $w^\top x_2 + b = 3 > 1$ ✓ ($x_2$ is not a support vector, $\alpha_2 = 0$). Dual: $w = \alpha_1 x_1 - \alpha_3 x_3 = \alpha_1(1, 1) = (1, 1) \Rightarrow \alpha_1 = 1$, and $\sum\alpha_i y_i = 0 \Rightarrow \alpha_3 = 1$.

`svm.py` `__main__` on two moons (standardised, 300 points): $C = 1, \gamma = 1$: train 0.98, test 0.99, 46 SVs; $C = 100, \gamma = 50$: train 1.00, test 0.93, 189 SVs (overfit: nearly every point is a support vector); $C = 0.1, \gamma = 0.5$: 0.90/0.91, 119 SVs (underfit, wide margin).

## Pitfalls

- Unscaled features with RBF: one feature's scale sets the effective $\gamma$.
- Tuning $C$ alone with the RBF kernel; the two interact.
- Reading `decision_function` as a probability, or using `probability=True` without knowing it runs an internal 5-fold CV.
- Number of support vectors close to $n$ = overfitting or a $\gamma$ too large.
- Using `SVC` on $10^6$ rows (quadratic memory); use a linear SVM or kernel approximation.
- Forgetting that the hinge loss is not differentiable at the margin (sub-gradients are fine, Newton is not).
- Assuming a large margin on training data implies good generalisation regardless of $C$: with large $C$ the "margin" is measured after removing every violator.

## Exam-style questions

1. **Why is the margin $2/\|w\|$ and why is $\frac12\|w\|^2$ minimised?** With the canonical scaling $\min_i y_i(w^\top x_i + b) = 1$, the two margin hyperplanes $w^\top x + b = \pm1$ are $2/\|w\|$ apart. Maximising $1/\|w\|$ is equivalent to minimising $\|w\|$, and $\frac12\|w\|^2$ is the differentiable convex form with the same minimiser.
2. **Derive $w = \sum_i\alpha_i y_i x_i$ and explain what it implies for prediction.** Setting $\partial L/\partial w = w - \sum\alpha_i y_i x_i = 0$. Prediction $f(x) = \sum_i \alpha_i y_i x_i^\top x + b$ only needs inner products with the support vectors ($\alpha_i > 0$), which enables kernels and makes the model sparse in the data.
3. **Effect of $C$ and $\gamma$ on bias/variance.** $C \uparrow$: fewer margin violations, more complex boundary, variance $\uparrow$; $C \downarrow$: wider margin, bias $\uparrow$. $\gamma \uparrow$: shorter kernel range, boundary follows individual points, variance $\uparrow$; $\gamma \downarrow$: approaches a linear boundary, bias $\uparrow$.
4. **Show that $K(x, z) = (x^\top z)^2$ in $\mathbb R^2$ corresponds to an explicit feature map.** $(x_1z_1 + x_2z_2)^2 = x_1^2z_1^2 + 2x_1x_2z_1z_2 + x_2^2z_2^2 = \phi(x)^\top\phi(z)$ with $\phi(x) = (x_1^2, \sqrt2\,x_1x_2, x_2^2)$. The kernel evaluates a 3-d inner product at the cost of a 2-d one; for degree $p$ in $d$ dimensions the feature space has $\binom{d + p}{p}$ monomials.
5. **Compare the perceptron with the SVM: what is common, what differs?** *(modelled on E21d; also in [S43].)* Common: both are supervised binary linear classifiers that look for a separating hyperplane, both need scaled features, and both minimise something equivalent to a hinge-type loss with an $L_2$ term. Differences: the perceptron stops at *any* separating hyperplane (and at a hyperplane with minimal error if none separates), the SVM maximises the **margin** and so finds the most robust one; the perceptron is an *online* learner updated per sample, the SVM solves one global convex QP over all samples; the SVM uses kernels as a matter of course, the perceptron normally does not; the SVM handles multi-class by one-vs-one or one-vs-all, a multi-output perceptron does it natively; the perceptron is faster to train and easier to interpret, the SVM slower and harder.
6. **Can kernel methods be applied to the perceptron? Why or why not?** *(E21b, E22a.)* **Yes.** The perceptron's weight vector is a linear combination of the mistakes, $w = \sum_i c_iy_ix_i$, so its prediction depends on the data only through inner products $x_i^\top x$ — the same structure that lets an SVM be kernelised. Replacing $x_i^\top x$ by $K(x_i, x)$ gives the *kernel perceptron*. The course's own answer adds that a kernel matrix can equally be fed into an MLP, and warns that a **single-layer** perceptron without a kernel cannot separate non-linear data [S12]; hence the paired true/false "kernel projections can only be used in conjunction with SVMs" — **false**.
7. **What are the advantages and disadvantages of SVMs?** *(modelled on [S43], the 2019 catalogue.)* For: high accuracy, non-linear problems solved via the kernel trick, good generalisation from the margin, a convex problem so no local minima (unlike a neural network), strong on unstructured/high-dimensional sparse data with a linear kernel. Against: scales poorly, roughly $O(n^2)$, so slow on large $n$; $C$ and $\gamma$ are hard to tune and interact; the model is hard to visualise and interpret; and it produces no calibrated probabilities by default. The course's shorthand: **high $C$ → overfit, high $\gamma$ → overfit too** (the catalogue writes "high gamma → underfit", which is wrong — a large $\gamma$ shrinks the kernel width, so the boundary chases individual points; see the pitfalls above) [S43].
8. **Interpret $\alpha_i = 0$, $0 < \alpha_i < C$, $\alpha_i = C$ via KKT conditions.** *(ours.)* Complementary slackness $\alpha_i[y_i f(x_i) - 1 + \xi_i] = 0$, $\mu_i\xi_i = 0$, $\alpha_i + \mu_i = C$. $\alpha_i = 0$: constraint inactive, point beyond the margin. $0 < \alpha_i < C$: $\mu_i > 0 \Rightarrow \xi_i = 0$ and the constraint is tight: exactly on the margin. $\alpha_i = C$: $\mu_i = 0$, $\xi_i \ge 0$ free: inside the margin or misclassified.

## Code

`src/py/svm.py`: `kernel(linear|poly|rbf)`, `LinearSVM` (Pegasos on the hinge loss, `hinge_loss`), `SVM(C, kernel, gamma)` (SMO with Platt's second-choice heuristic, stops when a full sweep moves no pair; `support_`, `alpha_`, `decision_function`, `coef_` for the linear kernel). Tests: primal objective within 2 % of `SVC(kernel="linear")`, RBF predictions ≥ 95 % agreement with `SVC`.
