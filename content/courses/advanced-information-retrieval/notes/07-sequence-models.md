# 07 NLP III: sequence models for text (CNN, RNN, attention)

How to turn a sequence of word vectors into contextual vectors or n-gram
representations. The course treats these as LEGO blocks for rankers [S10 sl. 3]:
1D CNNs reappear in Conv-KNRM (note 09), RNN encoders and attention lead to the
transformer (note 10).

**Not repeated here:** convolution arithmetic and CNN training in general
([`cse/ws2026/applied-deep-learning/notes/02-cnns.md`](../../applied-deep-learning/notes/02-cnns.md)),
RNN/LSTM/GRU equations, backpropagation through time and vanishing gradients
([`03-rnns.md`](../../applied-deep-learning/notes/03-rnns.md)),
scaled dot-product and multi-head attention with shapes
([`06-transformers.md`](../../applied-deep-learning/notes/06-transformers.md)).
This note keeps the text- and IR-specific parts.

## Definitions

1. **Sequence** $X=(x_1,\dots,x_n)$, $x_i\in\mathbb R^{d}$ (word embeddings), padded to a batch length with a mask.
2. **1D convolution over words** with filter width $h$ and $d'$ filters: $c_i=\mathrm{ReLU}(W[x_i;\dots;x_{i+h-1}]+b)\in\mathbb R^{d'}$, $W\in\mathbb R^{d'\times hd}$. Each output is a learned **n-gram representation** ($n=h$) [S10 sl. 6-7, S62]. PyTorch `Conv1d` expects `[B, d, n]`: transpose from `[B, n, d]` [S10 sl. 8-9].
3. **Pooling over time**: max or mean over positions to get a fixed-size vector from variable $n$; adaptive (dynamic) pooling to a fixed number of bins [S10 sl. 10-14].
4. **RNN** encoder: $s_i=f(s_{i-1},x_i)$; **LSTM** adds a memory cell with forget/input/output gates, $c_i=f_i\odot c_{i-1}+i_i\odot\tilde c_i$, $s_i=o_i\odot\tanh c_i$ [S10 sl. 18-24]; bidirectional: concatenate a left-to-right and a right-to-left pass.
5. **Encoder-decoder**: encoder states $s_{1:n}$, decoder generates $y_1,y_2,\dots$ one token at a time [S10 sl. 28-30].
6. **Attention** [S63]: at decoder step $t$ with state $z_t$, scores $e_{ti}=\mathrm{score}(z_t,s_i)$, weights $\alpha_{ti}=\mathrm{softmax}_i(e_{ti})$, context $c_t=\sum_i\alpha_{ti}s_i$ [S10 sl. 33-38]. Transformer self-attention is the same with queries, keys and values all from one sequence [S64].
7. **Beam search**: keep the $B$ best partial outputs by cumulative log-probability instead of the greedy best one [S10 sl. 32].

## Results

**Why CNNs for IR.** Word n-grams matter ("convolutional neural networks" vs "deep learning"), but an n-gram vocabulary is infeasible (sparsity: no connection between "quite good" and "very good") [S9 sl. 21, S12 sl. 37]. A 1D CNN builds n-gram vectors from word vectors with shared weights, so unseen n-grams of seen words get representations. Conv-KNRM cross-matches query and document n-grams of all widths (note 09).

**Why attention.** The plain encoder-decoder squeezes the whole input into one fixed vector $c=s_n$; long inputs lose information [S10 sl. 31]. Attention gives each output step direct access to all encoder states: path length $O(1)$ instead of $O(n)$. Self-attention then drops recurrence entirely (note 10).

**LSTM gradient path.** $\partial c_i/\partial c_{i-1}=\mathrm{diag}(f_i)$ (holding gates fixed): an additive path whose gain the model controls, instead of repeated multiplication by a weight matrix and a squashing derivative as in a vanilla RNN.

## Worked examples

**CNN arithmetic.** $n=10$ tokens, $d=300$ (GloVe), width $h=3$, $d'=128$ filters, no padding: output length $n-h+1=8$ trigram vectors; parameters $h\cdot d\cdot d'+d'=3\cdot300\cdot128+128=115{,}328$. With `padding=1` the output keeps length 10.

**Attention by hand.** Decoder state $z=(1,0)$, encoder states $s_1=(1,0)$, $s_2=(0,1)$, $s_3=(1,1)$, dot-product score: $e=(1,0,1)$, $\alpha=\frac{(e,1,e)}{2e+1}=(0.422,0.155,0.422)$, context $c=0.422\,(1,0)+0.155\,(0,1)+0.422\,(1,1)=(0.845,0.578)$.

**Masking in pooling.** Mean pooling over a padded sequence must divide by the number of real tokens, not by the padded length; max pooling must set padded positions to $-\infty$ first. `dense_retrieval.BiEncoder` implements masked mean pooling and `test_bi_encoder_masked_mean_pooling` checks that padding does not change the vector.

## Pitfalls

- `Conv1d` channel axis: `[B, n, d]` must be transposed to `[B, d, n]`; forgetting it convolves over the embedding dimension and still runs.
- An n-gram window over padding produces n-grams of padding: mask n-gram positions whose window touches a padded token (done in `ConvKNRM.ngrams`).
- A 1D CNN with window 3 is not a trigram *language model*; it is a feature extractor.
- Beam search is for generation (summarisation, generative QA), not for ranking; extractive QA uses span scoring (note 15), though the lecture notes that beam search can combine start and end candidates [S11 sl. 31].
- RNNs are sequential in $n$: slow on long documents; the transformer's parallelism is why it replaced them, not only its accuracy.

## Questions

**Q:** How does a 1D CNN produce n-gram representations, and why not just use an n-gram vocabulary?
**A:** A filter of width $h$ applied to $h$ consecutive word vectors gives one vector per window: a learned $h$-gram representation with shared weights. An explicit n-gram vocabulary is sparse and huge and cannot relate unseen n-grams to seen ones [S10 sl. 5-7, S9 sl. 21].

**Q:** Why was attention added to encoder-decoder models?
**A:** One fixed context vector is a bottleneck for long inputs; attention computes a step-specific weighted sum over all encoder states [S10 sl. 31-35, S63].

**Q:** Give output length and parameter count of a width-3, 128-filter 1D convolution on 10 tokens of dimension 300.
**A:** 8 positions without padding; $3\cdot300\cdot128+128=115{,}328$ parameters.

**Q:** What does the LSTM forget gate do for gradient flow?
**A:** It scales the additive cell path $c_i=f_i\odot c_{i-1}+\dots$, so $\partial c_i/\partial c_{i-1}=\mathrm{diag}(f_i)$ can stay near 1 and gradients survive long spans.

**Q:** How do you get a fixed-size vector from a variable-length sequence?
**A:** Pooling over time (max, masked mean, adaptive pooling to fixed bins), the final RNN state, or a `[CLS]`-style summary token.

## Code

- [`../src/py/knrm.py`](../src/py/knrm.py): `ConvKNRM.ngrams`: one `Conv1d` per width, ReLU, n-gram masks.
- [`../src/py/dense_retrieval.py`](../src/py/dense_retrieval.py): `BiEncoder.forward`, masked mean pooling.
- [`../src/py/bert_reranker_sketch.py`](../src/py/bert_reranker_sketch.py): `MultiHeadSelfAttention`, tested against `torch.nn.MultiheadAttention`.
