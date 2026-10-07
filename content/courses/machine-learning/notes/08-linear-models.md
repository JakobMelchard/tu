# 08 Linear models: regression, ridge, lasso, logistic regression

> Not a separate unit in [S18], but one of the most-asked topics in the archive: regression appears in E17b, E18a, E19a, E21a–d, E22a, E22b, E24a, E25b and E26a. Exam weight ●●● . Sources: [`../refs/SOURCES.md`](../refs/SOURCES.md).

## Linear regression

Model $\hat y = w^\top x + b$; with a bias column, $\hat y = Xw$, $X \in \mathbb R^{n \times (d+1)}$. Least squares $\min_w \|Xw - y\|_2^2$. Gradient $2X^\top(Xw - y) = 0$ gives the **normal equations** $X^\top X w = X^\top y$ and
$$\hat w = (X^\top X)^{-1}X^\top y$$
when $X$ has full column rank (else use the pseudo-inverse / `lstsq`, which picks the minimum-norm solution). Cost $O(nd^2 + d^3)$. Statistically: MLE under $y = w^\top x + \varepsilon$, $\varepsilon \sim \mathcal N(0, \sigma^2)$; Gauss–Markov: BLUE. Residuals are orthogonal to the column space. Polynomial / basis-function regression is still linear in $w$: replace $x$ by $\phi(x)$ (`linear.polynomial_features`).

The course calls $\|Xw - y\|^2$ the **residual sum of squares (RSS)** and states
the loss as $L = \frac{1}{2m}\sum_i(y_i - \hat y_i)^2$ with the gradient step
$w_j \leftarrow w_j - \alpha\,\frac{\partial L}{\partial w_j}$, learning rate
$\alpha$ [S13, S43]. **Say which convention you use** in a hand calculation: with
plain RSS the update carries a factor 2 and no $1/m$, and a paper that gives
"$\alpha = 0.5$, all $w$ start at 0, what is $w_1$ after the second step?"
(E22b) will land on a different number depending on the convention. Our
`linear.LinearRegression(solver="gd")` uses the $\frac2n$ form, and
`../src/exercises/2022-06-30/` works out both conventions side by side.

**Gradient descent** (when $d$ is large or data streams): $w \leftarrow w - \eta \frac{2}{n}X^\top(Xw - y)$. Converges for $\eta < 2/\lambda_{\max}(2X^\top X/n)$; feature scaling makes the loss well-conditioned (ratio $\lambda_{\max}/\lambda_{\min}$ small) so a single $\eta$ works. Stochastic / mini-batch GD uses a random subset per step: noisy but $O(\text{batch})$ per step.

**The examined trade-off** (E18a, E21c, E22a; also as true/false) [S12]:

| | normal equations | gradient descent |
|---|---|---|
| iterations | none, one closed-form solve | many |
| learning rate | none to choose | must be chosen |
| cost | $O(nd^2 + d^3)$ — the $d^3$ inverse hurts when $d$ is large | $O(nd)$ per step |
| use when | few features, moderate $n$ | many features/dimensions, streaming data, or a loss with no closed form |

So both "gradient descent is always more efficient than the normal equation" and
"the normal equation is always more efficient than gradient descent" are
**false**; each wins in its regime. A related pair: "linear regression converges
when performed on linearly separable data" — **false** — and "…on non-separable
data" — **true** [S12]. The intended reading is that separability is a concept
for *classifiers*; least squares always has a solution and always leaves some
error.

## Polynomial regression

$\hat y = w_0 + w_1x + w_2x^2 + \cdots + w_px^p$ — still **linear in the
parameters**, so it is fitted by exactly the machinery above with
$\phi(x) = (1, x, x^2, \ldots)$. Asked as a long-answer question in four papers
(E20c, E21a, E21d, E22a): *what is it, and what are its advantages and
disadvantages against linear regression?* [S12]

- **Advantages**: fits curved relationships that a straight line cannot; more
  flexible; still a closed-form least-squares problem.
- **Disadvantages**: **overfits** easily as the degree grows; the powers of $x$
  are strongly correlated with each other (**multicollinearity**), which makes
  the coefficients unstable and large; extrapolation outside the training range
  explodes; and the model is far harder to interpret.
- **How to avoid overfitting in polynomial regression** (E21b): choose the
  degree by cross-validation, and regularise — ridge or lasso, with $\lambda$
  controlling model complexity; large $\lambda$ gives high bias and low
  variance, small $\lambda$ the opposite [S12].

## Ridge regression ($L_2$)

$$\min_w \|Xw - y\|^2 + \alpha\|w\|^2 \quad\Rightarrow\quad \hat w = (X^\top X + \alpha I)^{-1}X^\top y$$
(intercept not penalised: centre $X$ and $y$ first). Always invertible; shrinks coefficients along low-variance directions of $X$ most (in the SVD $X = U S V^\top$: $\hat w = V \operatorname{diag}\frac{s_j}{s_j^2 + \alpha}U^\top y$). Handles collinearity; Bayesian view: Gaussian prior $w \sim \mathcal N(0, \sigma^2/\alpha)$, MAP estimate. Effective degrees of freedom $\sum_j s_j^2/(s_j^2 + \alpha)$.

## Lasso ($L_1$)

$$\min_w \frac{1}{2n}\|Xw - y\|^2 + \alpha\|w\|_1$$
No closed form (non-differentiable at 0). Coordinate descent [S23 §3.4]: for feature $j$ with partial residual $r^{(j)} = y - \sum_{k \ne j} x_k w_k$,
$$w_j \leftarrow \frac{S\!\left(\tfrac1n x_j^\top r^{(j)},\ \alpha\right)}{\tfrac1n x_j^\top x_j},\qquad S(z, \gamma) = \operatorname{sign}(z)\max(|z| - \gamma, 0)$$
(soft thresholding). Coefficients hit exactly zero → embedded feature selection; the $L_1$ ball has corners on the axes where the elliptical loss contours touch first. Among correlated features lasso picks one arbitrarily; **elastic net** $\alpha[\rho\|w\|_1 + \frac{1-\rho}{2}\|w\|^2]$ groups them. Scale features before penalising (the penalty is not unit-invariant). LARS computes the whole regularisation path.

## Logistic regression

Binary $y \in \{0, 1\}$, $p(y = 1 \mid x) = \sigma(w^\top x + b)$, $\sigma(z) = 1/(1 + e^{-z})$, i.e. the **log-odds are linear**: $\log\frac{p}{1-p} = w^\top x + b$; the decision boundary $w^\top x + b = 0$ is a hyperplane. Negative log-likelihood (cross-entropy)
$$J(w) = -\frac1n\sum_i \big[y_i\log p_i + (1 - y_i)\log(1 - p_i)\big],\qquad \nabla J = \frac1n X^\top(p - y),\qquad \nabla^2 J = \frac1n X^\top \operatorname{diag}(p_i(1-p_i))\,X$$
Convex, no closed form; solve by gradient descent, **Newton / IRLS** ($w \leftarrow w - H^{-1}\nabla J$, few iterations, $O(d^3)$ each) or L-BFGS (sklearn default). Add $\frac{\lambda}{2n}\|w\|^2$ (sklearn: $C = 1/\lambda$) — necessary when classes are separable (otherwise $\|w\| \to \infty$). Coefficient $w_j$ = change in log-odds per unit $x_j$; $e^{w_j}$ = odds ratio. Multiclass: **softmax** $p(y = c \mid x) = \frac{e^{w_c^\top x}}{\sum_k e^{w_k^\top x}}$, gradient $\frac1n X^\top(P - Y)$; or one-vs-rest. Well calibrated probabilities (unlike SVM/NB).

Why not least squares for classification: squared loss penalises confidently-correct points far from the boundary; a linear probability leaves $[0, 1]$.

## Worked example

Fit $y = w x + b$ to $(x, y) = (0, 1), (1, 3), (2, 2), (3, 5)$. $\bar x = 1.5$, $\bar y = 2.75$, $S_{xy} = \sum(x - \bar x)(y - \bar y) = (-1.5)(-1.75) + (-0.5)(0.25) + (0.5)(-0.75) + (1.5)(2.25) = 5.5$, $S_{xx} = 5$; $w = 1.1$, $b = 2.75 - 1.65 = 1.1$. Ridge with $\alpha = 5$ on centred data: $w = S_{xy}/(S_{xx} + \alpha) = 0.55$ (shrunk), $b = 2.75 - 0.55\cdot1.5 = 1.925$. Lasso with $\alpha = 1$ ($n = 4$): $z = S_{xy}/n = 1.375$, $S(z, 1) = 0.375$, divide by $S_{xx}/n = 1.25$: $w = 0.3$; with $\alpha = 1.375$ it is exactly 0.

Logistic regression, one gradient step: $w = 0, b = 0$, points $x = -1$ ($y = 0$) and $x = 2$ ($y = 1$), $p = 0.5$ for both; $\partial J/\partial w = \frac12[(0.5 - 0)(-1) + (0.5 - 1)(2)] = -0.75$, $\partial J/\partial b = 0$; with $\eta = 1$: $w = 0.75$, $b = 0$. Positive $w$ already puts $x = 2$ on the positive side.

On `make_regression` with 3 true non-zero coefficients out of 10 (`linear.py` `__main__`), OLS and ridge keep all 10 non-zero; lasso with $\alpha = 1$ recovers exactly 3.

## Pitfalls

- Penalising the intercept, or penalising unscaled features (large-unit features get shrunk less).
- Reading $R^2$ on training data as fit quality; comparing coefficients across differently scaled features.
- Collinear features: OLS coefficients explode with opposite signs; ridge fixes it.
- Logistic regression without regularisation on separable data does not converge.
- Interpreting logistic coefficients as probability changes (they are log-odds changes).
- Extrapolating polynomial regression; degree is a hyperparameter to CV.
- Gradient descent with a too-large step diverges; with unscaled features it crawls.

## Exam-style questions

1. **Derive the normal equations and state when $X^\top X$ is singular.** $\partial \|Xw - y\|^2/\partial w = 2X^\top(Xw - y) = 0$. Singular when the columns are linearly dependent: $d + 1 > n$, duplicated/one-hot-with-all-levels-plus-intercept, exactly collinear features. Ridge's $+\alpha I$ makes it positive definite.
2. **Why does lasso give sparse solutions and ridge not?** The $L_1$ penalty's subgradient at $w_j = 0$ is the interval $[-\alpha, \alpha]$; if the data gradient $|\frac1n x_j^\top r| \le \alpha$, zero is optimal (soft threshold). The $L_2$ penalty gradient $2\alpha w_j$ vanishes at 0, so there is no force keeping a coefficient exactly at zero; geometrically the $L_1$ ball has corners on the axes.
3. **Write the logistic loss and its gradient; why is squared loss inappropriate?** Above. Squared loss on $\sigma(w^\top x)$ is non-convex and saturates; on a linear score it penalises correct confident predictions; cross-entropy is the MLE objective, convex, and gives calibrated probabilities.
4. **Ridge in terms of the SVD of $X$: what happens to directions with small singular values?** $\hat w = \sum_j v_j \frac{s_j}{s_j^2 + \alpha}(u_j^\top y)$; for $s_j^2 \ll \alpha$ the factor $\approx s_j/\alpha \to 0$: low-variance (noisy, collinear) directions are shrunk to nothing, high-variance directions are barely touched.
5. **Batch GD vs Newton for logistic regression: cost per step and convergence.** *(ours.)* GD: $O(nd)$ per step, linear convergence, needs a step size and scaling. Newton: $O(nd^2 + d^3)$ per step, quadratic convergence, no step size, few iterations; impractical for $d \gtrsim 10^4$ (then L-BFGS or SGD).
6. **What is the difference between lasso and ridge regression?** *(modelled on E19b, E21a, E21c, E21d — asked four times.)* Both add a penalty on the coefficients to the least-squares cost, controlled by $\lambda$. **Ridge** penalises the sum of **squares** ($L_2$) and shrinks every coefficient towards zero without reaching it; it handles collinearity and keeps all features. **Lasso** penalises the sum of **absolute values** ($L_1$) and can set coefficients **exactly to zero**, so it performs feature selection; among correlated features it picks one arbitrarily. Elastic net mixes the two.
7. **Explain polynomial regression and give advantages and disadvantages against linear regression.** *(E20c, E21a, E21d, E22a.)* See the section above: more flexible and still least-squares, but prone to overfitting, multicollinear in its own powers, explosive on extrapolation and hard to interpret.
8. **Write gradient-descent pseudocode for linear regression, and name two methods to compute the coefficients.** *(modelled on E17b, E20b, E21c.)* (1) initialise $w$ (zeros or small random); (2) predict $\hat y = Xw$; (3) compute the loss, e.g. $\frac1{2m}\sum(y - \hat y)^2$ (+ a penalty if regularising); (4) compute $\partial L/\partial w_j = -\frac1m\sum_i(y_i - \hat y_i)x_{ij}$; (5) update $w \leftarrow w - \alpha\,\partial L/\partial w$; (6) repeat until the loss stops improving or the iteration cap is hit. The two methods are **gradient descent** and the **normal equations** $\hat w = (X^\top X)^{-1}X^\top y$ [S12].
9. **One step of gradient descent on RSS: two features, five samples, all weights starting at zero, $\alpha = 0.5$ — what is $w_1$ after the first update?** *(modelled on E22b.)* With every $\hat y_i = 0$ the residual is $y_i$, so $\partial\,\text{RSS}/\partial w_1 = -2\sum_i y_i x_{i1}$ and $w_1 \leftarrow 0 + 2\alpha\sum_i y_i x_{i1} = \alpha' \sum_i y_i x_{i1}$. State whether you are using the $2\cdot$RSS gradient or the $\frac1{2m}$-scaled one; the two differ by a factor of $2m$.

## Code

`src/py/linear.py`: `LinearRegression(solver=lstsq|normal|gd)`, `Ridge` (closed form, centred), `Lasso` (coordinate descent with `soft_threshold`), `LogisticRegression(solver=gd|newton, l2)`, `SoftmaxRegression`, `polynomial_features`. Tests match sklearn coefficients to $10^{-2}$ or better.
