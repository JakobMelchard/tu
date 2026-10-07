# 05 Artificial neural networks

TISS topic 5, "Artificial neural networks" [S2]; 2021S videos Optimization 3
(backpropagation), Classification 2, Neural Networks 1-3; exercise 09 (SUSY with
`MLPClassifier`, hand grid search) [S5, S11]. Texts: [S6 sec. IX, XI], [S8 ch. 11],
[S9 ch. 10], [S7 sec. 5.6]. CNNs, RNNs, vanishing gradients:
[CSE notes 11](../../machine-learning/notes/11-neural-networks.md)
and [13](../../machine-learning/notes/13-deep-learning.md).

## Definitions

- **Feed-forward network (MLP):** $a^0=x$; for $l=1..L$:
  $z^l=W^{lT}a^{l-1}+b^l$, $a^l=g(z^l)$; output $\hat y=g_\text{out}(z^L)$.
  Parameters $\theta=\{W^l,b^l\}$; widths $n_l$; depth $L$.
- **Activations:** sigmoid $\sigma$; $\tanh=2\sigma(2z)-1$; ReLU $\max(0,z)$;
  identity. Output: identity + MSE (regression), sigmoid/softmax + cross-entropy
  (classification).
- **Backpropagation:** reverse-mode differentiation of $E$ through the graph,
  cost $\approx$ two forward passes.
- **Epoch, minibatch, learning rate, width, depth, weight decay, early stopping,
  dropout:** hyperparameters, tuned on validation data (exercise 09 grid [S5]).

## Backpropagation (derivation)

Define $\delta^l=\partial E/\partial z^l$. Chain rule through $z^{l+1}=W^{l+1,T}g(z^l)+b^{l+1}$:

$$\delta^L=\frac{\partial E}{\partial z^L},\qquad
\delta^l=\big(W^{l+1}\delta^{l+1}\big)\odot g'(z^l),\qquad
\frac{\partial E}{\partial W^l}=a^{l-1}\delta^{lT},\quad\frac{\partial E}{\partial b^l}=\delta^l .$$

Output layers: softmax + cross-entropy gives $\delta^L=P-Y$; identity + MSE gives
$\delta^L=2(\hat y-y)$ (per sample, divide by $N$ for the mean). The first is why
this pairing is used: no $g'$ factor, no saturation at the output. Exercise 02's
toy [S5]: $E=f(g(x))$, $f=x^4-2x^2$, $g=2x+1$, $E'(x)=f'(g(x))g'(x)$, $E'(0.5)=48$.

**Vanishing/exploding gradients.** $\delta^l=\prod_{k>l}(W^k\,\mathrm{diag}\,g'(z^k))\,\delta^L$.
$\sigma'\le\frac14$, so deep sigmoid nets shrink $\delta$ geometrically; ReLU
($g'\in\{0,1\}$) and variance-preserving initialisation
($\mathrm{Var}\,W_{ij}=2/n_\text{in}$ He for ReLU, $1/n_\text{in}$ Glorot-like for
tanh) keep the product $O(1)$ [S6 sec. IX.C.2].

**Universal approximation** [S27]. One hidden layer with a non-polynomial
activation and enough units approximates any continuous function on a compact
set uniformly. Constructive 1D idea: $\sigma(k(x-a))-\sigma(k(x-b))\to$ indicator of
$[a,b]$ as $k\to\infty$; sum of bumps = step-function approximation. The theorem
says nothing about how many units, how to find the weights, or generalisation.

**Why hidden layers (XOR).** A single layer computes a thresholded linear function;
XOR needs $\hat y=\mathrm{ReLU}(x_0+x_1)-2\,\mathrm{ReLU}(x_0+x_1-1)$: two hidden units suffice.

**Training tricks** [S6 sec. IX.D]: standardise inputs; minibatch SGD or Adam
[S26]; early stopping on a validation set; $\ell_2$ weight decay; dropout; batch
normalisation; learning-rate decay. Loss landscape non-convex, but in wide
networks most local minima are good; saddles are the main obstacle.

**Gradient check.** Compare backprop with central differences
$\frac{E(\theta+he)-E(\theta-he)}{2h}$ ($h\sim10^{-6}$, float64); use a norm-based
relative error $\|g_\text{bp}-g_\text{fd}\|/(\|g_\text{bp}\|+\|g_\text{fd}\|)$, since
element-wise ratios blow up on entries whose gradient is $\approx0$.

## Worked example (`src/py/nn_numpy.py`, numpy only)

- Gradient check, net $3\text{-}5\text{-}4\text{-}2$, 6 samples: relative error
  $3.5\times10^{-10}$ (tanh), $3.4\times10^{-9}$ (sigmoid), $2.8\times10^{-10}$ (ReLU).
  An element-wise check flagged $2.5\times10^{-6}$ on one near-zero entry: the
  reason for the norm-based measure.
- XOR with $2\text{-}4\text{-}2$ tanh, Adam: predictions $[0,1,1,0]$; without a
  hidden layer at most 3 of 4 correct.
- $y=\sin2x+0.3x$ on $[-\pi,\pi]$, one tanh hidden layer, 1500 epochs:
  MSE $9.3\times10^{-2}$ (width 2), $2.3\times10^{-3}$ (8), $5.8\times10^{-4}$ (32).
- Early stopping: 30 noisy points, $1\text{-}64\text{-}64\text{-}1$; validation loss
  turns up, `train` restores the best epoch (test `test_early_stopping_restores_best_validation_loss`).

Exercise 09 conclusion [S5]: on SUSY the MLP barely beats logistic regression
("difficult to get the accuracy above 80 %"); the 18 variables already include
hand-built high-level features [S17], so little non-linearity is left to learn.
The synthetic analogue in note 10 has engineered and raw variants to show both sides.

## Pitfalls

- Unscaled inputs: saturated tanh/sigmoid units, tiny gradients.
- Symmetric initialisation (all weights equal): all hidden units stay identical.
- Validation curve rising while training falls: stop; more epochs is not better.
- "Just add neurons" (exercise 09 [S5]): more capacity raises variance and
  training cost; the bottleneck may be the information in the features (Bayes
  error), not the model.
- sklearn `MLPClassifier(early_stopping=True)` holds out 10 % internally: your
  training set is smaller than you think.

## Test-style questions

**Q1.** Write the backprop recursion for a 2-layer net with tanh hidden units and
MSE, and give $\partial E/\partial W^1$.
**A.** $\delta^2=2(\hat y-y)$; $\delta^1=(W^2\delta^2)\odot(1-\tanh^2z^1)$;
$\partial E/\partial W^1=x\,\delta^{1T}$, $\partial E/\partial W^2=a^1\delta^{2T}$.

**Q2.** How many input and output neurons for SUSY (18 variables, 2 classes), and
which activations?
**A.** 18 inputs; 1 sigmoid output (or 2 softmax); ReLU or tanh hidden layers;
at least one hidden layer, otherwise it is logistic regression.

**Q3.** Why does softmax + cross-entropy give $\delta^L=P-Y$?
**A.** $E=-\sum_cY_c\log P_c$, $\partial P_c/\partial z_k=P_c(\delta_{ck}-P_k)$, so
$\partial E/\partial z_k=-\sum_cY_c(\delta_{ck}-P_k)=P_k-Y_k$ using $\sum_cY_c=1$.

**Q4.** State the universal approximation theorem and one thing it does not promise.
**A.** One hidden layer with a non-polynomial activation is dense in $C(K)$ for
compact $K$. It does not bound the width, give a training algorithm, or
guarantee generalisation from finite data.

**Q5.** Why do deep sigmoid networks train slowly, and what fixes it?
**A.** Each layer multiplies $\delta$ by $W\,\mathrm{diag}\,\sigma'$ with
$\sigma'\le1/4$: gradients vanish exponentially in depth. ReLU, He/Glorot
initialisation, residual connections, batch normalisation.

## Code

`src/py/nn_numpy.py`: `MLP(sizes, hidden, out)` with `forward`, `loss`,
`backward`; `numerical_grad`, `grad_check`; `train(...)` with SGD or Adam and
optional early stopping. Torch is used only for autoencoders (note 08); sklearn's
`MLPClassifier` in `ising.py` and `collisions.py` (note 10).
