# 11 Neural networks and deep learning basics

> Lecture unit 9 [S18]. Exam weight ●●● . Convolutional and recurrent networks, transfer learning and the deep-net regularisers are in [note 13](13-deep-learning.md). Sources: [`../refs/SOURCES.md`](../refs/SOURCES.md).

## Perceptron (Rosenblatt 1958)


$\hat y = \operatorname{sign}(w^\top x + b)$. Update on each mistake: $w \leftarrow w + \eta\, y_i x_i$, $b \leftarrow b + \eta\, y_i$. Convergence theorem: if the data are separable with margin $\gamma$ and $\|x_i\| \le R$, the number of updates is $\le (R/\gamma)^2$ regardless of $\eta$; on non-separable data it never converges (cycles). Cannot represent XOR (Minsky & Papert 1969): a single linear unit is a linear classifier. Logistic regression is the perceptron with a sigmoid output and a proper loss.

## Multilayer perceptron

Layers $l = 1..L$: $z^{(l)} = W^{(l)} a^{(l-1)} + b^{(l)}$, $a^{(l)} = g(z^{(l)})$, $a^{(0)} = x$. Output layer: softmax + cross-entropy for classification, identity + squared error for regression. **Universal approximation** (Cybenko, Hornik): one hidden layer with enough units approximates any continuous function on a compact set; depth makes many functions exponentially cheaper to represent.

Activations $g$ and their derivatives:

| $g(z)$ | $g'(z)$ | notes |
|---|---|---|
| sigmoid $\sigma(z) = 1/(1 + e^{-z})$ | $\sigma(1 - \sigma)$ | $\le 1/4$, saturates → vanishing gradients; outputs in $(0,1)$ |
| $\tanh(z)$ | $1 - \tanh^2 z$ | zero-centred, still saturates |
| ReLU $\max(0, z)$ | $[z > 0]$ | cheap, no saturation for $z > 0$; "dead" units if always $< 0$ |
| leaky ReLU / ELU / GELU | | fix dead units |
| softmax $e^{z_c}/\sum_k e^{z_k}$ | | output layer, multiclass |

Without a non-linearity the composition of linear layers is one linear map.

## Backpropagation

Reverse-mode automatic differentiation of the loss through the chain rule, costing about twice a forward pass. With $\delta^{(l)} = \partial J/\partial z^{(l)}$ (mini-batch of size $n$, loss averaged):

$$\delta^{(L)} = \frac1n(\hat p - y)\ \text{(softmax + CE, or identity + MSE)},\qquad \delta^{(l)} = \big(W^{(l+1)\top}\delta^{(l+1)}\big)\odot g'(z^{(l)}),$$
$$\frac{\partial J}{\partial W^{(l)}} = \delta^{(l)} a^{(l-1)\top},\qquad \frac{\partial J}{\partial b^{(l)}} = \delta^{(l)} .$$

The nice form of $\delta^{(L)}$ is why softmax pairs with cross-entropy (the $\log$ cancels the $\exp$; squared error on a sigmoid output multiplies by $\sigma'$ and learns slowly when saturated). Gradient checking: compare with $(J(\theta + \epsilon) - J(\theta - \epsilon))/2\epsilon$ (`mlp.numerical_gradient`; the test demands agreement to $10^{-6}$). Vanishing gradients: products of $g' \le 1/4$ and small weights across many layers; exploding: the opposite. Remedies: ReLU, careful init, batch norm, residual connections, gradient clipping.

## Optimisation

- Mini-batch SGD: $\theta \leftarrow \theta - \eta\,\hat\nabla J$ on batches of 32–512; one pass over the data is an **epoch**. Noise in $\hat\nabla$ regularises and escapes saddle points; the loss surface is non-convex, so we find a local minimum / flat region, which in practice is fine.
- **Momentum**: $v \leftarrow \beta v - \eta\nabla J$, $\theta \leftarrow \theta + v$ ($\beta \approx 0.9$); Nesterov evaluates the gradient at the look-ahead point.
- **Adam**: $m \leftarrow \beta_1 m + (1 - \beta_1)g$, $v \leftarrow \beta_2 v + (1 - \beta_2)g^2$, bias-corrected $\hat m = m/(1 - \beta_1^t)$, $\hat v = v/(1 - \beta_2^t)$, $\theta \leftarrow \theta - \eta\,\hat m/(\sqrt{\hat v} + \epsilon)$; per-parameter step sizes; defaults $\eta = 10^{-3}, \beta_1 = 0.9, \beta_2 = 0.999$. RMSProp is Adam without $m$; AdaGrad accumulates $v$ without decay.
- Learning-rate schedules (step, cosine, warm-up), early stopping on validation loss, weight initialisation: Xavier/Glorot $\operatorname{Var}(W) = 1/n_{\text{in}}$ (tanh/sigmoid), He $2/n_{\text{in}}$ (ReLU) keep activations and gradients at unit scale.
- Input standardisation is mandatory; **batch normalisation** standardises each layer's pre-activations per batch and learns a scale/shift.

## Regularisation

$L_2$ weight decay $\frac{\lambda}{2}\|W\|^2$ (decoupled in AdamW); **dropout** (each hidden unit kept with probability $1 - p$ during training and activations rescaled by $1/(1-p)$, full network at test time — an implicit ensemble of thinned networks); early stopping (the number of epochs is a capacity knob); data augmentation; smaller architectures; noise injection; batch norm has a mild regularising effect.

## Deep learning

Convolutional networks, recurrent networks, transfer learning, the deep-net
regularisers and the vanishing-gradient fixes are **[note 13](13-deep-learning.md)**
— a lecture unit of its own [S18] and, measured by the archive, examined at least
as heavily as the MLP mechanics here [S11]. Autoencoders learn compressed
representations without labels and are listed by the lecture under unsupervised
feature selection [S18].

## Worked example

XOR with one hidden layer of two ReLU units: $h_1 = \max(0, x_1 + x_2)$, $h_2 = \max(0, x_1 + x_2 - 1)$, output $y = h_1 - 2h_2$. Inputs $(0,0) \to 0$, $(1,0) \to 1$, $(0,1) \to 1$, $(1,1) \to 2 - 2 = 0$. Hidden units carve the input space into regions where the output is linear.

One backprop step by hand: 1 input $x = 1$, one hidden sigmoid unit $w_1 = 0.5, b_1 = 0$, output linear $w_2 = 1, b_2 = 0$, target $y = 1$, loss $\frac12(\hat y - y)^2$. Forward: $z_1 = 0.5$, $a_1 = \sigma(0.5) = 0.622$, $\hat y = 0.622$. Backward: $\delta_2 = \hat y - y = -0.378$; $\partial J/\partial w_2 = \delta_2 a_1 = -0.235$, $\partial J/\partial b_2 = -0.378$; $\delta_1 = \delta_2 w_2\,\sigma'(z_1) = -0.378 \cdot 1 \cdot (0.622 \cdot 0.378) = -0.0887$; $\partial J/\partial w_1 = \delta_1 x = -0.0887$. With $\eta = 0.5$: $w_2 = 1.118$, $b_2 = 0.189$, $w_1 = 0.544$.

`mlp.py` `__main__`: two moons (600 points, noise 0.25, 30 % test), MLP (32, 16) ReLU + Adam reaches 0.88 test accuracy in 100 epochs (tanh + SGD: 0.90); a (64, 64) ReLU net with dropout 0.2, $L_2 = 10^{-3}$ and early stopping (patience 15) on a validation split carved from the training data stops after 47 epochs at 0.89. The validation split matters: monitoring the test set instead would make the test score an optimistically biased model-selection score (note 04).

## Pitfalls

- Unscaled inputs, sigmoid hidden layers in deep nets, learning rate too high (loss explodes / NaN) or too low (no progress).
- Reporting training loss; early stopping on the test set.
- Forgetting to switch dropout off at test time (inverted dropout handles the scaling).
- Saturated softmax with huge logits: subtract the max before exponentiating.
- Too small batches with batch norm; comparing optimisers at one learning rate each (tune $\eta$ per optimiser).
- Neural nets on small tabular data: gradient boosting usually wins; NNs need data.

## Exam-style questions

1. **Why can a single perceptron not learn XOR and how does one hidden layer fix it?** Its decision boundary is a hyperplane; XOR's positive points $(1,0), (0,1)$ are not linearly separable from $(0,0), (1,1)$. A hidden layer maps inputs to a space (e.g. $h = (\text{OR}, \text{AND})$) where they become separable; see the worked example.
2. **Derive $\delta^{(l)}$ for a hidden layer.** $\delta^{(l)}_j = \partial J/\partial z^{(l)}_j = \sum_k \frac{\partial J}{\partial z^{(l+1)}_k}\frac{\partial z^{(l+1)}_k}{\partial a^{(l)}_j}\frac{\partial a^{(l)}_j}{\partial z^{(l)}_j} = \sum_k \delta^{(l+1)}_k W^{(l+1)}_{kj}\, g'(z^{(l)}_j)$, i.e. $\delta^{(l)} = (W^{(l+1)\top}\delta^{(l+1)}) \odot g'(z^{(l)})$.
3. **What is the vanishing-gradient problem and three remedies?** Backpropagated gradients are products of $W^{(l)\top}$ and $g'$ terms; with sigmoid $g' \le 0.25$ they shrink exponentially with depth, so early layers do not learn. Remedies: ReLU-type activations, He/Xavier initialisation, batch normalisation, residual (skip) connections, LSTM gating for recurrence.
4. **Compare SGD with momentum and Adam.** Both use running averages of the gradient; Adam additionally normalises by a running RMS of the gradient per parameter, giving adaptive step sizes and robustness to the learning-rate choice; SGD+momentum often generalises slightly better on vision tasks when tuned; Adam converges faster with default settings.
5. **Explain dropout as regularisation and what happens at test time.** *(modelled on E21c, E22a.)* Each training step drops hidden units independently with probability $p$, so units cannot co-adapt and the net behaves like an average over $2^{\#\text{units}}$ thinned sub-networks. At test time the full network is used; with inverted dropout activations were scaled by $1/(1-p)$ during training, so nothing changes at test time.
6. **Put the steps of training a neural network with gradient descent in the right order.** *(modelled on E21b — the exam gives five shuffled options.)* (1) initialise the weights and biases; (2) forward-propagate an input through the network to get an output; (3) compute the error against the expected output with the loss function; (4) back-propagate and adjust the weights; (5) repeat until the weights stop improving [S12].
7. **What methods combat overfitting in neural networks?** *(E21c, E22a.)* Dropout, $L_2$ weight decay, data augmentation, early stopping, batch normalisation (which regularises as a side effect) and simply a smaller architecture [S12]. **Not** cross-validation — that measures overfitting rather than preventing it (note 13).
8. **A network with ReLU activations can approximate XOR. Replace the ReLUs by linear activations — can it still?** *(E21b.)* **No.** A composition of linear maps is a single linear map, so the network collapses to one hyperplane, and XOR is not linearly separable. The non-linearity is what buys the extra representational power, not the depth by itself.

## Code

`src/py/mlp.py`: `Perceptron`, `MLP(hidden, activation, task, optimizer=sgd|adam, l2, dropout, early_stopping)` with `_forward`, `_backward`, `_step`, `loss`, `history_`; `numerical_gradient` for gradient checking. Tests: gradient check to $10^{-6}$ for three activations, accuracy vs `MLPClassifier`, regression vs `MLPRegressor`.
