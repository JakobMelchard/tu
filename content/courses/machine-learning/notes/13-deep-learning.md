# 13 Deep learning: CNNs, RNNs and transfer learning

> Lecture unit 10 [S18]. Exam weight ●●● — added in the 2026-09-22 source pass; the archive shows convolution arithmetic and CNN recall in every paper since 2020 [S11]. Sources: [`../refs/SOURCES.md`](../refs/SOURCES.md); past-paper evidence in [`00-exam-focus.md`](00-exam-focus.md).

## What it is

Lecture unit 10 [S18]. Where note 11 stops — an MLP trained by backpropagation —
this note covers the three things the course adds on top and examines heavily:
**convolutional networks**, **recurrent networks**, and **transfer learning**,
plus the deep-net-specific regularisation and gradient problems. [S1] names
"Deep Learning" in the subject line without saying more; the exam archive says
what that means in practice, and it is narrower and more mechanical than a
deep-learning course would be: output sizes, architecture names, and which
regulariser does what [S11].

The lecture's framing of deep vs traditional ML, which is asked as a long-answer
question (E17a, E21b) [S12]:

| traditional ML | deep learning |
|---|---|
| express the problem as a mathematical function | compose an ensemble of simple functions |
| **features are hand-crafted** | the algorithm operates on raw data (pixels, audio, text) and **learns its own feature extraction** |
| learn parameters from the prepared features | learn feature extraction and parameters together |

Application areas where it clearly won: image classification, audio, text/LLMs
[S12].

## Convolutional networks

A convolutional layer replaces the dense $W a$ of note 11 by a small kernel slid
over the input, so weights are **shared across space**: far fewer parameters,
and translation equivariance [S26 ch. 9].

- **2-D convolution**, kernel $K \in \mathbb R^{k\times k}$, stride $S$,
  zero-padding $P$:
  $$O_{ij} = \sum_{u=0}^{k-1}\sum_{v=0}^{k-1} K_{uv}\,I_{\,iS+u-P,\;jS+v-P}.$$
  (Deep-learning "convolution" is really cross-correlation: the kernel is not
  flipped. Nothing downstream cares, because $K$ is learned [S26 §9.1].)
- **Output size — the one formula the exam tests**:
  $$\boxed{\;O = \left\lfloor\frac{I - K + 2P}{S}\right\rfloor + 1\;}$$
  per spatial dimension. So the output is **larger** when padding *increases*
  and when stride *decreases* (E25b, E26a) [S11]. "Same" padding is
  $P = (K-1)/2$ with $S = 1$, which keeps $O = I$.
- **Parameters** of a conv layer with $D$ input and $D'$ output channels and a
  $k\times k$ kernel: $k^2DD'$ weights plus $D'$ biases — independent of the
  image size. (The 1-D version $KDD'$ is a question on the sibling course's
  paper [S16]; the arithmetic is the same.)
- **Pooling** downsamples: max pooling takes the maximum of each $k\times k$
  window, average pooling the mean. Same output-size formula. Pooling gives
  local translation invariance and has no parameters.
- Typical stack: `conv → non-linearity → pool`, repeated, then dense layers and
  a softmax [S26 §9.3].
- **Architectures the exam asks you to recognise**: **LeNet** [S40],
  **AlexNet**, **VGG**, **Inception/GoogLeNet**, **ResNet** [S40]. Distractors
  used in the papers: *LSTM* (recurrent, not convolutional), *"Reception"*
  (a corruption of Inception), *"TeNet"* (does not exist) (E25b, E26a) [S11].

## Recurrent networks

$h_t = g(W_{hh}h_{t-1} + W_{xh}x_t + b)$, the same weights at every time step;
output $y_t = W_{hy}h_t$. Trained by **backpropagation through time**: unroll
the loop into a deep feed-forward net that shares weights, then backpropagate
[S26 ch. 10]. Consequences the exam uses:

- An RNN **suits sequential input whose length is not fixed** — the same
  parameters handle any $T$ (E23b, answer **true**) [S18].
- An RNN "can be unrolled into an infinite fully connected network" (E21a,
  answer **true**) [S12] — the intended reading is the unrolling above.
- **Convolution and pooling belong to CNNs, not RNNs** — asked as a trap in
  E20c and E21a, answer **false** [S12].
- Vanishing/exploding gradients are worst here, because the same $W_{hh}$ is
  multiplied in $T$ times: $\partial h_T/\partial h_1 = \prod_t W_{hh}^\top
  \operatorname{diag}g'$. **LSTM/GRU gating** gives the state an additive path
  with derivative $\approx 1$, which is why they train over long sequences
  [S26 §10.10].
- Transformers replace recurrence with self-attention
  $\operatorname{softmax}(QK^\top/\sqrt{d_k})V$. **Not examined in 184.702** —
  it is examined in the sibling course [S16, S4].

## Vanishing gradients, and what fixes them

Backpropagated gradients are products of $W^\top$ and $g'$ factors across
layers. With sigmoid, $g' \le 1/4$, so a 10-layer net shrinks the gradient by
$\le 4^{-10}$ and early layers do not learn [S26 §8.2]. The **section-3 list**
(E25b, E26a) [S11]:

| fix | why it works |
|---|---|
| **ReLU**-type activations | $g' = 1$ on the active half, no saturation |
| **He / Xavier initialisation** | $\operatorname{Var}(W) = 2/n_{\text{in}}$ (ReLU) or $1/n_{\text{in}}$ (tanh) keeps activation and gradient variance at 1 across layers [S26 §8.4] |
| **Batch normalisation** | standardises each layer's pre-activations per batch, $\hat z = \gamma\frac{z - \mu_B}{\sqrt{\sigma_B^2+\epsilon}} + \beta$; removes the dependence of each layer's scale on the layers below [S26 §8.7.1] |
| **Residual / skip connections** | $a^{(l)} = a^{(l-1)} + f(a^{(l-1)})$ gives the gradient a path with derivative 1 [S40 ResNet] |
| **Gradient clipping** | rescale $g \leftarrow g\,\min(1, c/\|g\|)$; fixes *exploding*, the other half of the problem [S26 §10.11] |
| **LSTM/GRU gating** | for recurrent nets, as above |

## Regularising a deep net

The exam's recurring list "which methods help to prevent overfitting?" (E23a,
E21c, E22a) [S12]:

- **Dropout**: keep each hidden unit with probability $1-p$ during training,
  rescale surviving activations by $1/(1-p)$ (inverted dropout), use the full
  net at test time. It is an implicit ensemble of $2^{\#\text{units}}$ thinned
  networks, so units cannot co-adapt [S26 §7.12].
  *The exam asks "which technique is similar to dropout?" with **bagging** as an
  option* (E23a). [S26 §7.12] states the bagging analogy explicitly and it is
  the intended answer; note that the student answer key [S12] marks "Bagging –
  False" here, which contradicts the standard reading. The difference is that
  dropout's sub-models share parameters, whereas bagging's are independent; if
  the option list distinguishes those, that is the distinction being tested.
- **$L_2$ weight decay**, **early stopping** (the epoch count is a capacity
  knob), **batch normalisation** (a side effect, via the batch noise), **data
  augmentation**, **smaller architectures** [S12].
- **Cross-validation is *not* a regularisation method** — it measures
  performance, it does not change the model. This is a deliberate distractor in
  E23a [S12].

**Data augmentation** (E24a, asked as "What is data augmentation?") [S12]:
extend the training set with label-preserving transformations — flips,
rotations, crops, scaling, colour and contrast changes for images; noise and
time shifts for audio. It teaches the model to *ignore* the varied factor, and
it enlarges an otherwise small data set. It is applied to the **training set
only**, like every other training-time device.

## Transfer learning

Lecture unit 12, "combining models" [S18]. Reuse a network trained on a large
data set for a new, smaller task.

- **Off-the-shelf feature extraction**: discard the pretrained classifier head,
  run the data through the remaining layers, and train a *shallow* model
  (logistic regression, SVM) on those activations. The exam states this
  definition verbatim and marks it **true** (E21d, E23c) [S12, S18].
- **Supervised task adaptation / fine-tuning**: keep the network, replace the
  head, continue training.
- **Freezing** a layer means its weights are **not updated** during fine-tuning.
  Asked twice in the inverted form ("freezing means these layers will be
  fine-tuned") — answer **false** (E20b, E20c) [S12].
- Which layers transfer: the **early** layers (edges, textures) generalise
  across tasks; the **late** layers are task-specific and are the ones you
  replace or retrain [S18].

## Worked example

**Convolution and pooling, the exam's own numbers** (E20c). Input $7\times7$,
kernel/window $3\times3$, stride $S = 2$, no padding:
$$O = \left\lfloor\frac{7 - 3 + 0}{2}\right\rfloor + 1 = 3,$$
so both the convolution and the max pooling produce a $3\times3$ output. The
windows start at rows/columns $0, 2, 4$ and the last one ends at index 6 — the
input is used exactly. With $S = 1$ the output would be $5\times5$; with
$P = 1, S = 1$ it would be $7\times7$.

Take the input $I_{ij} = i + j$ ($i, j = 0..6$) and the kernel
$K = \begin{psmallmatrix}1&0&-1\\1&0&-1\\1&0&-1\end{psmallmatrix}$ (a vertical
edge detector). Every $3\times3$ patch of $I$ has column sums differing by 3
per column step, so each output is $3\cdot(\text{left col}) - 3\cdot(\text{right
col}) = -6$ everywhere: a linear ramp has a constant gradient.
Max pooling the same input with $3\times3$/stride 2 gives the bottom-right
corner of each window, i.e. $\begin{psmallmatrix}4&6&8\\6&8&10\\8&10&12\end{psmallmatrix}$.
`../src/py/conv.py` prints both.

**Parameter count.** A conv layer with 32 input channels, 64 output channels and
a $3\times3$ kernel: $3^2\cdot32\cdot64 = 18\,432$ weights $+ 64$ biases. The
dense layer that would connect two $32\times32$ feature maps of the same shapes:
$32\cdot32\cdot32 \times 32\cdot32\cdot64 \approx 2\cdot10^9$. That ratio is the
whole argument for weight sharing.

## Pitfalls

- Using $\lceil\cdot\rceil$ or forgetting the $+1$ in the output-size formula.
  Check it against $I = K, S = 1, P = 0 \Rightarrow O = 1$.
- Confusing padding and stride directions: **padding up, stride down** both make
  the output *bigger*.
- Answering a CNN-architecture list from memory of general deep learning: the
  exam's distractors (LSTM, "Reception", "TeNet") are chosen to punish exactly
  that.
- Treating cross-validation as a regulariser.
- Applying data augmentation to the validation or test set.
- Saying that freezing layers means training them.
- Assuming the sibling course's Transformer material is examined here — it is
  not [S16].
- Claiming an RNN needs a fixed-length input.

## Exam-style questions

1. **A $28\times28$ input, a $5\times5$ kernel, stride 1, padding 2: what is the
   output size, and what is it with stride 2 and no padding?** *(modelled on
   E20c, E24a.)* $\lfloor(28-5+4)/1\rfloor + 1 = 28$; and
   $\lfloor(28-5)/2\rfloor + 1 = 12$.
2. **"The output of a convolutional layer is larger when …" — pick all that
   apply: padding increases, padding decreases, stride increases, stride
   decreases.** *(E25b, E26a.)* Padding increases ✓, stride decreases ✓. From
   $O = \lfloor(I-K+2P)/S\rfloor + 1$: $P$ in the numerator, $S$ in the
   denominator.
3. **Which of LeNet, LSTM, ResNet, Reception, TeNet are CNN architectures?**
   *(E25b, E26a.)* LeNet and ResNet. LSTM is recurrent; the other two are
   invented distractors (Inception is the real name).
4. **Name four methods that help with vanishing gradients and say why each
   works.** *(E25b, E26a.)* ReLU (no saturation on the active half), He/Xavier
   initialisation (unit variance across layers), batch normalisation (removes
   scale coupling between layers), residual connections (a derivative-1 path);
   plus gradient clipping for the exploding case and LSTM gating for
   recurrence.
5. **What does "freezing layers" mean, and what is "off-the-shelf" transfer
   learning?** *(E20b, E20c, E21d.)* Freezing = the layer's weights are **not**
   updated during fine-tuning. Off-the-shelf = discard the pretrained head and
   feed the remaining layers' output into a separate shallow model as features.
6. **Why does a convolutional layer have far fewer parameters than a dense layer
   on the same input, and what does it buy?** *(ours — the archive only asks for
   the counts, not the reason.)* Weight sharing: one $k\times k\times D\times D'$
   kernel is reused at every spatial position, so the count is independent of
   the image size. It buys translation equivariance and a massive reduction in
   variance, at the cost of assuming locality and stationarity.

## Code

- `src/py/conv.py`: `output_size`, `pad2d`, `conv2d`, `max_pool2d`,
  `avg_pool2d`, `conv_params`, `conv_output_shape`. `__main__` prints the
  $7\times7$/$3\times3$/stride-2 example above.
- `src/py/mlp.py`: dropout, $L_2$, early stopping, He/Xavier initialisation and
  the gradient check (note 11).
- `src/exercises/2020-09-09/`: the convolution and max-pooling questions of
  E20c, worked.
