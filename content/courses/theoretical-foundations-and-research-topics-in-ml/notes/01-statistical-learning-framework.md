# 01 Statistical learning framework

Supervised learning is treated as a statistical decision problem: nature draws labelled examples from an unknown distribution, the learner sees a finite i.i.d. sample and must output a predictor whose expected loss on *future* draws is small. This note fixes the objects everything else in the course is built on (distribution, loss, risk, hypothesis class, ERM), proves the two facts that motivate the whole theory (the Bayes predictor is the best one can do; the training error of a data-dependent predictor is a biased estimate of its risk), and shows on the memorising classifier why the hypothesis class must be restricted. Notes 02–04 then quantify *how much* restriction buys *how much* generalisation.

## Definitions

1. **Domain and labels.** $\mathcal X$ is the input space, $\mathcal Y$ the label space. Binary classification: $\mathcal Y=\{-1,+1\}$. Regression: $\mathcal Y=\mathbb R$.
2. **Data distribution.** $\mathcal D$ is a probability distribution over $\mathcal X\times\mathcal Y$, unknown to the learner. Write $\mathcal D_{\mathcal X}$ for its marginal on $\mathcal X$ and $\eta(x)=P(y=+1\mid x)$ for the conditional label probability (binary case).
3. **Realisable case.** There is a deterministic $f:\mathcal X\to\mathcal Y$ with $y=f(x)$ $\mathcal D$-a.s., i.e. $\eta(x)\in\{0,1\}$. Then $\mathcal D$ is specified by $(\mathcal D_{\mathcal X},f)$. The general case (labels noisy, $\eta(x)\in(0,1)$ allowed) is the **agnostic** case.
4. **Sample.** $S=((x_1,y_1),\dots,(x_n,y_n))\sim\mathcal D^n$, i.e. $n$ independent draws from $\mathcal D$ (i.i.d.). $S$ is the only access the learner has to $\mathcal D$.
5. **Hypothesis / predictor.** A measurable map $h:\mathcal X\to\mathcal Y$. A **hypothesis class** $\mathcal H$ is a set of hypotheses fixed *before* seeing $S$.
6. **Loss function.** $\ell:\mathcal Y\times\mathcal Y\to\mathbb R_{\ge0}$, $\ell(\hat y,y)$ = cost of predicting $\hat y$ when the truth is $y$. Standard choices:
   - zero-one: $\ell_{0\text{-}1}(\hat y,y)=\mathbb 1[\hat y\neq y]$;
   - squared: $\ell_{\mathrm{sq}}(\hat y,y)=(\hat y-y)^2$;
   - hinge (for real-valued scores $g(x)$, $y\in\{\pm1\}$): $\ell_{\mathrm{hinge}}(g(x),y)=\max\{0,1-y\,g(x)\}$;
   - logistic: $\ell_{\log}(g(x),y)=\log(1+e^{-y\,g(x)})$.
   Hinge and logistic are convex upper bounds on $\ell_{0\text{-}1}(\mathrm{sign}\,g(x),y)$ (surrogate losses), used because $\ell_{0\text{-}1}$ is not convex in $g$.
7. **True risk (generalisation error).** $L_{\mathcal D}(h)=\mathbb E_{(x,y)\sim\mathcal D}\,\ell(h(x),y)$. For $\ell_{0\text{-}1}$: $L_{\mathcal D}(h)=P_{\mathcal D}(h(x)\neq y)$.
8. **Empirical risk (training error).** $L_S(h)=\frac1n\sum_{i=1}^n\ell(h(x_i),y_i)$.
9. **Bayes optimal predictor.** $h^\star\in\arg\min_{h\text{ measurable}}L_{\mathcal D}(h)$, minimising over *all* functions. Its risk $L^\star=L_{\mathcal D}(h^\star)$ is the **Bayes risk** (irreducible error).
10. **Learning algorithm.** A map $A:\bigcup_n(\mathcal X\times\mathcal Y)^n\to\mathcal H$ (or into all functions); write $h_S=A(S)$.
11. **Empirical risk minimisation (ERM).** $\mathrm{ERM}_{\mathcal H}(S)\in\arg\min_{h\in\mathcal H}L_S(h)$ (ties broken arbitrarily). A hypothesis with $L_S(h)=0$ is **consistent** with $S$.
12. **Approximation / estimation error.** With $h_S=\mathrm{ERM}_{\mathcal H}(S)$ and $h_{\mathcal H}\in\arg\min_{h\in\mathcal H}L_{\mathcal D}(h)$,
    $$L_{\mathcal D}(h_S)-L^\star=\underbrace{\bigl(L_{\mathcal D}(h_S)-L_{\mathcal D}(h_{\mathcal H})\bigr)}_{\varepsilon_{\mathrm{est}}\ \ge0}+\underbrace{\bigl(L_{\mathcal D}(h_{\mathcal H})-L^\star\bigr)}_{\varepsilon_{\mathrm{app}}\ \ge0}.$$
    $\varepsilon_{\mathrm{app}}$ depends on $\mathcal H$ and $\mathcal D$ only (how expressive $\mathcal H$ is); $\varepsilon_{\mathrm{est}}$ depends on $S$ (how well $L_S$ approximates $L_{\mathcal D}$ over $\mathcal H$).
13. **Generalisation gap.** $L_{\mathcal D}(h)-L_S(h)$. For $h=h_S$ it is typically positive (Theorem 1.3).
14. **Overfitting.** $L_S(h_S)$ small while $L_{\mathcal D}(h_S)$ large, i.e. a large positive generalisation gap.
15. **Inductive bias.** Any prior restriction or preference that the learner imposes before seeing data: the choice of $\mathcal H$, a preference ordering on $\mathcal H$ (regularisation), the choice of algorithm. Note 03 (No-Free-Lunch) shows it is unavoidable.

## Results

**Theorem 1.1 (Bayes optimality, zero-one loss)** [S9 §3.2.1]**.** Let $\mathcal Y=\{-1,+1\}$ and $\eta(x)=P(y=+1\mid x)$. Then
$$h^\star(x)=\mathrm{sign}\bigl(\eta(x)-\tfrac12\bigr)$$
minimises $L_{\mathcal D}$ over all measurable $h$, and $L^\star=\mathbb E_x\min\{\eta(x),1-\eta(x)\}$.

*Proof.* Condition on $x$. For any $h$,
$$P(h(x)\neq y\mid x)=\begin{cases}1-\eta(x)&h(x)=+1\\ \eta(x)&h(x)=-1\end{cases}\ \ge\ \min\{\eta(x),1-\eta(x)\},$$
with equality iff $h(x)=+1$ when $\eta(x)>\tfrac12$ and $h(x)=-1$ when $\eta(x)<\tfrac12$ (either choice when $\eta(x)=\tfrac12$). Since $L_{\mathcal D}(h)=\mathbb E_x P(h(x)\neq y\mid x)$ and the integrand is minimised pointwise by $h^\star$, $L_{\mathcal D}(h)\ge L_{\mathcal D}(h^\star)=\mathbb E_x\min\{\eta,1-\eta\}$. ∎

**Theorem 1.2 (Bayes optimality, squared loss)** [S12 §2.1]**.** Let $\mathcal Y=\mathbb R$, $\mathbb E y^2<\infty$. Then $h^\star(x)=\mathbb E[y\mid x]$ minimises $L_{\mathcal D}(h)=\mathbb E(h(x)-y)^2$, and $L^\star=\mathbb E\,\mathrm{Var}(y\mid x)$.

*Proof.* Write $m(x)=\mathbb E[y\mid x]$. Then
$$\mathbb E\bigl[(h(x)-y)^2\mid x\bigr]=\mathbb E\bigl[(h(x)-m(x)+m(x)-y)^2\mid x\bigr]=(h(x)-m(x))^2+\mathrm{Var}(y\mid x),$$
because the cross term $2(h(x)-m(x))\,\mathbb E[m(x)-y\mid x]=0$. The first term is $\ge0$ with equality iff $h(x)=m(x)$; take expectations over $x$. ∎

**Theorem 1.3 (empirical risk is unbiased for fixed $h$, optimistic for $h_S$)** [S9 §2.1]**.**
(a) For any fixed $h$ (chosen independently of $S$): $\mathbb E_{S\sim\mathcal D^n}L_S(h)=L_{\mathcal D}(h)$ and $\mathrm{Var}\,L_S(h)=\frac1n\mathrm{Var}_{\mathcal D}\,\ell(h(x),y)$.
(b) For $h_S=\mathrm{ERM}_{\mathcal H}(S)$:
$$\mathbb E_S\,L_S(h_S)\ \le\ \min_{h\in\mathcal H}L_{\mathcal D}(h)\ \le\ \mathbb E_S\,L_{\mathcal D}(h_S).$$
In particular $\mathbb E_S[L_{\mathcal D}(h_S)-L_S(h_S)]\ge0$: the expected generalisation gap of ERM is non-negative.

*Proof.* (a) $L_S(h)=\frac1n\sum_i\ell(h(x_i),y_i)$ is an average of $n$ i.i.d. copies of the random variable $Z=\ell(h(x),y)$ with $\mathbb E Z=L_{\mathcal D}(h)$; linearity of expectation gives the mean, independence gives the variance.

(b) Left inequality. Let $h_{\mathcal H}\in\arg\min_{h\in\mathcal H}L_{\mathcal D}(h)$, a fixed (non-random) hypothesis. By definition of ERM, for *every* realisation $S$, $L_S(h_S)=\min_{h\in\mathcal H}L_S(h)\le L_S(h_{\mathcal H})$. Take $\mathbb E_S$ and use (a) for the fixed $h_{\mathcal H}$: $\mathbb E_S L_S(h_S)\le\mathbb E_S L_S(h_{\mathcal H})=L_{\mathcal D}(h_{\mathcal H})$.
Right inequality. $h_S\in\mathcal H$ for every $S$, so $L_{\mathcal D}(h_S)\ge\min_{h\in\mathcal H}L_{\mathcal D}(h)$ pointwise; take expectations. ∎

*Why (a) fails for $h_S$.* Step (a) needs $\ell(h(x_i),y_i)$ to be i.i.d. with mean $L_{\mathcal D}(h)$, which holds when $h$ does not depend on $(x_i,y_i)$. $h_S$ is a function of all of $S$, so $\ell(h_S(x_i),y_i)$ is *not* an unbiased estimate of $\ell(h_S(x),y)$ at a fresh $(x,y)$: the minimisation selects, among all $h\in\mathcal H$, the one for which the particular fluctuations of $S$ look most favourable ("selection bias" / "winner's curse"). The bigger $\mathcal H$, the more chances to find a hypothesis that fits the noise of $S$, and the larger the optimism $L_{\mathcal D}(h_S)-L_S(h_S)$. Controlling this optimism *uniformly over $\mathcal H$* is exactly what uniform convergence (note 02) and VC theory (note 04) do.

**Theorem 1.4 (the memorising classifier overfits)** [S9 §2.3.1]**.** Let $\mathcal D$ be any distribution whose marginal $\mathcal D_{\mathcal X}$ is atomless (e.g. uniform on $[0,1]$). Define
$$h_S(x)=\begin{cases}y_i&\text{if }x=x_i\text{ for some }i\\ -1&\text{otherwise.}\end{cases}$$
Then $L_S(h_S)=0$ for every $S$, while $L_{\mathcal D}(h_S)=P_{\mathcal D}(y=+1)$. For $P(y=+1)=\tfrac12$ (e.g. $\eta\equiv\tfrac12$, or $f$ labelling half the mass $+1$) this gives $L_S=0$, $L_{\mathcal D}=\tfrac12$: no better than a coin flip.

*Proof.* $L_S(h_S)=\frac1n\sum_i\mathbb 1[h_S(x_i)\neq y_i]=0$ by construction (distinct $x_i$ a.s. since the marginal is atomless). A fresh $x\sim\mathcal D_{\mathcal X}$ avoids the finite set $\{x_1,\dots,x_n\}$ with probability 1, so $h_S(x)=-1$ a.s. and $L_{\mathcal D}(h_S)=P(y\neq-1)=P(y=+1)$. ∎

*Consequence: why restrict $\mathcal H$.* If $\mathcal H$ is the class of all functions $\mathcal X\to\{\pm1\}$, the memoriser is a legitimate ERM (it has zero empirical risk) and Theorem 1.4 shows ERM over "everything" can fail completely even in the realisable case with unlimited data. So ERM must be run over a restricted $\mathcal H$: this shrinks $\varepsilon_{\mathrm{est}}$ (fewer ways to fit noise) at the price of $\varepsilon_{\mathrm{app}}$ (the truth may be outside $\mathcal H$). The bias–complexity trade-off is the choice of $\mathcal H$ balancing the two terms in Definition 12; how to choose $\mathcal H$ from data is the topic of structural risk minimisation and regularisation later in the course.

**Proposition 1.5 (risk of thresholds under label noise).** Let $x\sim\mathrm{Unif}[0,1]$, $\theta\in(0,1)$, $\eta\in[0,\tfrac12)$, and $y=\mathrm{sign}(x-\theta)$ flipped independently with probability $\eta$. For the threshold $h_t(x)=\mathrm{sign}(x-t)$,
$$L_{\mathcal D}(h_t)=\eta+(1-2\eta)\,|t-\theta|,\qquad L^\star=\eta,\qquad h^\star=h_\theta.$$

*Proof.* Let $\xi\in\{\text{flip},\text{no flip}\}$, $P(\text{flip})=\eta$, independent of $x$. $h_t(x)\neq y$ iff either ($h_t(x)=\mathrm{sign}(x-\theta)$ and flip) or ($h_t(x)\neq\mathrm{sign}(x-\theta)$ and no flip). $h_t$ and $h_\theta$ disagree exactly on the interval between $t$ and $\theta$, of Lebesgue measure $|t-\theta|$. Hence
$$L_{\mathcal D}(h_t)=(1-|t-\theta|)\,\eta+|t-\theta|\,(1-\eta)=\eta+(1-2\eta)|t-\theta|.$$
Here $\eta(x)=P(y=+1\mid x)=1-\eta$ for $x>\theta$ and $\eta$ for $x<\theta$, so by Theorem 1.1 $h^\star(x)=\mathrm{sign}(x-\theta)=h_\theta(x)$ and $L^\star=\mathbb E\min\{\eta,1-\eta\}=\eta$. Since $\eta<\tfrac12$ the formula is minimised at $t=\theta$, consistent with this. ∎

## Worked example

Threshold with label noise, $\theta=0.3$, $\eta=0.1$. Then $L_{\mathcal D}(h_t)=0.1+0.8\,|t-0.3|$.

| $t$ | $|t-0.3|$ | $L_{\mathcal D}(h_t)$ |
|---|---|---|
| $0.3$ | $0$ | $0.10$ (Bayes risk) |
| $0.25$ | $0.05$ | $0.14$ |
| $0.5$ | $0.2$ | $0.26$ |
| $0$ (predict $+1$ everywhere) | $0.3$ | $0.34$ |
| $1$ (predict $-1$ everywhere) | $0.7$ | $0.66$ |

Sanity check of $t=0$: the constant $+1$ predictor errs when $y=-1$, i.e. $P(x<\theta)(1-\eta)+P(x\ge\theta)\eta=0.3\cdot0.9+0.7\cdot0.1=0.34$. Matches.

Decomposition for the class $\mathcal H_k=\{h_{j/k}:j=0,\dots,k\}$ of grid thresholds with $k=4$ (allowed $t\in\{0,0.25,0.5,0.75,1\}$): $\min_{h\in\mathcal H_4}L_{\mathcal D}=L_{\mathcal D}(h_{0.25})=0.14$, so $\varepsilon_{\mathrm{app}}=0.14-0.10=0.04$. If ERM on some sample returns $h_{0.5}$, then $\varepsilon_{\mathrm{est}}=0.26-0.14=0.12$, total excess risk $0.16$.

Optimism of training error (Theorem 1.3b): with $n=20$ samples and $\mathcal H$ = all thresholds, ERM picks the $t$ minimising the number of training mistakes. Roughly $2$ of the $20$ labels are flipped; ERM can often place $t$ so that some flipped points near $\theta$ are "explained", giving $L_S(h_S)\approx0.05$–$0.08$ while $L_{\mathcal D}(h_S)\ge0.10$. So $\mathbb E L_S(h_S)<0.10=\min_hL_{\mathcal D}(h)<\mathbb E L_{\mathcal D}(h_S)$, exactly the chain in Theorem 1.3(b). `generalisation_gap_experiment` in the code makes this numerical.

Bayes predictor with a soft $\eta$: if instead $\eta(x)=x$ on $[0,1]$ (uniform $x$), Theorem 1.1 gives $h^\star(x)=\mathrm{sign}(x-\tfrac12)$ and $L^\star=\int_0^1\min\{x,1-x\}\,dx=2\int_0^{1/2}x\,dx=\tfrac14$. No predictor, however complex, beats $25\%$ error.

## Pitfalls

- $L_{\mathcal D}(h)$ is a number (expectation over $\mathcal D$); $L_S(h)$ is a random variable (function of $S$). "Generalisation error" always means $L_{\mathcal D}$.
- The Bayes predictor is *not* in general a member of $\mathcal H$; $\varepsilon_{\mathrm{app}}>0$ is the price of the inductive bias, not a failure of the algorithm.
- $\mathbb E_S L_S(h)=L_{\mathcal D}(h)$ holds only for $h$ fixed before seeing $S$. Reporting $L_S(h_S)$ as an estimate of $L_{\mathcal D}(h_S)$ is biased downward (Theorem 1.3b). A held-out test set restores independence and hence unbiasedness.
- Realisable does not mean deterministic labelling is *known*: $f$ exists but the learner does not know it, and $f$ need not lie in $\mathcal H$ unless one additionally assumes $f\in\mathcal H$ (the "realisability assumption" of note 03 is the stronger $f\in\mathcal H$ version).
- Zero training error is not evidence of learning (Theorem 1.4); it is evidence that $\mathcal H$ is rich enough to fit $S$.
- $\varepsilon_{\mathrm{est}}$ is not the generalisation gap: $\varepsilon_{\mathrm{est}}=L_{\mathcal D}(h_S)-L_{\mathcal D}(h_{\mathcal H})$ compares two true risks; the gap $L_{\mathcal D}(h_S)-L_S(h_S)$ compares true and empirical risk of one hypothesis. Uniform convergence bounds the gap, and via Lemma 2.5 of note 02 also bounds $\varepsilon_{\mathrm{est}}$.
- The surrogate losses (hinge, logistic) are used for optimisation; the quantity one ultimately reports is still $\ell_{0\text{-}1}$ risk. Minimising surrogate risk yields Bayes-consistent classifiers under conditions (calibration), but that is a separate result.
- Sign conventions: $\mathrm{sign}(0)$ must be fixed (here $+1$); it matters for measure-zero sets only when $\mathcal D_{\mathcal X}$ has atoms.

## Questions

**Q:** Define true risk, empirical risk, and the ERM rule. What is the relationship between them in expectation?
**A:** $L_{\mathcal D}(h)=\mathbb E_{\mathcal D}\ell(h(x),y)$; $L_S(h)=\frac1n\sum\ell(h(x_i),y_i)$; $\mathrm{ERM}_{\mathcal H}(S)=\arg\min_{h\in\mathcal H}L_S(h)$. For fixed $h$, $\mathbb E_SL_S(h)=L_{\mathcal D}(h)$ (i.i.d. average). For $h_S$, $\mathbb E L_S(h_S)\le\min_{\mathcal H}L_{\mathcal D}\le\mathbb E L_{\mathcal D}(h_S)$.

**Q:** Derive the Bayes optimal classifier for zero-one loss.
**A:** Conditional on $x$, predicting $+1$ costs $1-\eta(x)$, predicting $-1$ costs $\eta(x)$; choose the smaller, i.e. $h^\star=\mathrm{sign}(\eta-\tfrac12)$. Pointwise minimisation of the integrand minimises the integral. Bayes risk $\mathbb E\min\{\eta,1-\eta\}$.

**Q:** Why is $\mathbb E[y\mid x]$ the squared-loss Bayes predictor?
**A:** $\mathbb E[(h-y)^2\mid x]=(h-m)^2+\mathrm{Var}(y\mid x)$ with $m=\mathbb E[y|x]$; the cross term vanishes because $\mathbb E[y-m\mid x]=0$. Minimised at $h=m$; Bayes risk $=\mathbb E\,\mathrm{Var}(y\mid x)$.

**Q:** Write down the approximation/estimation decomposition and explain which term each design choice affects.
**A:** $L_{\mathcal D}(h_S)-L^\star=(L_{\mathcal D}(h_S)-L_{\mathcal D}(h_{\mathcal H}))+(L_{\mathcal D}(h_{\mathcal H})-L^\star)$. Enlarging $\mathcal H$ decreases approximation error and (typically) increases estimation error; more data decreases estimation error only. Neither term is observable directly since $\mathcal D$ is unknown.

**Q:** Prove that training error of ERM is optimistic in expectation.
**A:** For fixed $h_{\mathcal H}$, $L_S(h_S)\le L_S(h_{\mathcal H})$ pointwise in $S$; take expectations, use unbiasedness for the fixed $h_{\mathcal H}$: $\mathbb E L_S(h_S)\le L_{\mathcal D}(h_{\mathcal H})=\min_{\mathcal H}L_{\mathcal D}\le\mathbb EL_{\mathcal D}(h_S)$.

**Q:** Give an example where ERM has zero training error and true risk $1/2$. What does it show?
**A:** The memoriser $h_S(x)=y_i$ on training points, $-1$ elsewhere, with atomless $\mathcal D_{\mathcal X}$ and $P(y=+1)=\tfrac12$. It shows ERM over the class of all functions does not learn; the hypothesis class must be restricted (inductive bias).

**Q:** In the noisy threshold problem, what are $h^\star$, $L^\star$ and $L_{\mathcal D}(h_t)$?
**A:** $h^\star=h_\theta$ since $\eta(x)$ crosses $\tfrac12$ exactly at $\theta$; $L^\star=\eta$; $L_{\mathcal D}(h_t)=\eta+(1-2\eta)|t-\theta|$: noise rate on the agreeing region plus $(1-\eta)$ on the disagreeing interval of length $|t-\theta|$.

**Q:** What distinguishes the realisable from the agnostic setting, and why does the distinction matter later?
**A:** Realisable: $\exists f\in\mathcal H$ with $L_{\mathcal D}(f)=0$ (labels deterministic and in the class). Agnostic: nothing assumed; target is $\min_{\mathcal H}L_{\mathcal D}$. Sample complexity scales as $1/\varepsilon$ in the realisable case versus $1/\varepsilon^2$ in the agnostic case (note 02).

## Code

`src/py/framework.py`:
- `ThresholdProblem(theta, eta)`: the noisy threshold distribution of Proposition 1.5; `.sample(n, rng)` draws $S$, `.risk(t)` evaluates the closed form $\eta+(1-2\eta)|t-\theta|$, `.bayes_risk` returns $\eta$. Use it to reproduce the table above.
- `zero_one_loss`, `empirical_risk`: Definitions 6 and 8 on a finite sample.
- `erm_finite(hyps, X, y)`: brute-force ERM over a finite list of hypotheses (Definition 11).
- `finite_threshold_class(k)`: the grid class $\mathcal H_k$ used in the decomposition example.
- `generalisation_gap_experiment(problem, k, n, trials, rng)`: draws many samples, runs ERM, and reports $\mathbb E L_S(h_S)$, $\mathbb E L_{\mathcal D}(h_S)$ and $\min_hL_{\mathcal D}(h)$, demonstrating the chain of Theorem 1.3(b); the demo prints it for $n=10\dots1000$ over 200 resamples each.
- `threshold_empirical_risks(X, y, ts)`: $L_S(h_t)$ for many $t$ at once by prefix sums over the sorted sample; reused by notes 02, 04, 05, 06.
- `memoriser_predict`, `memoriser_risk`, `memoriser_experiment`: Theorem 1.4, closed form $(0,P(y=+1))$ against simulation.

## References

- Shalev-Shwartz & Ben-David, *Understanding Machine Learning* (2014): Ch. 2 (formal model, ERM, overfitting, inductive bias), Ch. 3.2 (agnostic PAC, loss functions), Ch. 5.2 (error decomposition).
- Mohri, Rostamizadeh & Talwalkar, *Foundations of Machine Learning* (2nd ed. 2018): Ch. 2.1 (PAC model setup), Ch. 4.1 (Bayes error, noise).
- Hastie, Tibshirani & Friedman, *ESL* (2009): Ch. 2.4 (statistical decision theory, Bayes classifier, squared loss), Ch. 7.2–7.4 (optimism of the training error).
- Devroye, Györfi & Lugosi, *A Probabilistic Theory of Pattern Recognition* (1996): Ch. 2 (Bayes rule for zero-one loss).
- Vapnik, *The Nature of Statistical Learning Theory* (1995): Ch. 1 (setting of the learning problem, risk minimisation).
