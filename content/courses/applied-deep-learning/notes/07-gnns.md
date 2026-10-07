# 07 Graph neural networks

Graph neural networks (GNNs) are neural networks whose input is a graph: a set of nodes with feature vectors and a set of edges that says which nodes are related. Grids (images) and chains (sequences) are special graphs with fixed neighbourhoods, so convolutions and RNNs are GNNs with a hard-coded, ordered neighbourhood; general graphs have variable-size, unordered neighbourhoods, so the layer must be permutation-invariant over neighbours. Almost all modern GNNs are instances of one scheme, message passing: each node aggregates transformed features of its neighbours and updates its own state, repeated $L$ times so information travels $L$ hops. This note covers the message-passing framework, the three standard layers (GCN, GraphSAGE, GAT), the expressivity limit (GIN, WL test), depth problems, the three task families and the practical setup of the reference implementation `gnn_gcn.py`.

## Concepts

### Graph data

A graph $G = (V, E)$ with $N = |V|$ nodes. Representations:

- Adjacency matrix $A \in \{0,1\}^{N\times N}$, $A_{uv} = 1$ iff $(u,v)\in E$; symmetric for undirected graphs. Weighted graphs: $A_{uv}\in\mathbb{R}$.
- Degree matrix $D = \mathrm{diag}(d_1,\dots,d_N)$, $d_v = \sum_u A_{vu}$.
- Node features $X\in\mathbb{R}^{N\times F}$ (row $v$ = feature vector of node $v$); optional edge features $e_{uv}\in\mathbb{R}^{F_e}$ and a graph-level target.
- Edge list / COO: an integer tensor `edge_index` of shape $[2, |E|]$ with source and target node indices. Memory $O(|E|)$ instead of $O(N^2)$; real graphs are sparse ($|E| \ll N^2$), so all libraries store COO/CSR and implement $AX$ as a scatter-add over edges: $(AX)_v = \sum_{(u,v)\in E} X_u$. The dense form $A\in\mathbb{R}^{N\times N}$ is fine up to a few thousand nodes and is what the reference code uses.
- Batching graphs: $B$ graphs with $N_1,\dots,N_B$ nodes are merged into one graph with $\sum_b N_b$ nodes whose adjacency is block-diagonal, $A = \mathrm{diag}(A_1,\dots,A_B)$. Message passing never crosses blocks, so one forward pass processes the whole batch; a `batch` vector of length $\sum_b N_b$ records which graph each node belongs to (needed for graph-level pooling). No padding is required, in contrast to sequences.

Node ordering is arbitrary: permuting nodes by a permutation matrix $P$ gives $(PAP^\top, PX)$, and a node-level GNN must be permutation-equivariant, $f(PAP^\top, PX) = P f(A, X)$; a graph-level output must be permutation-invariant.

### Message passing framework

Layer $l$ maps node states $h_v^{(l)}\in\mathbb{R}^{F_l}$ to $h_v^{(l+1)}$ (Gilmer et al. 2017):

$$
h_v^{(l+1)} = \phi\Big(h_v^{(l)},\ \bigoplus_{u\in N(v)} \psi\big(h_v^{(l)}, h_u^{(l)}, e_{uv}\big)\Big).
$$

- $\psi$: message function (an MLP or a linear map applied to the neighbour state, optionally conditioned on the receiver and the edge feature).
- $\bigoplus$: aggregator over the neighbour multiset $N(v)$; must be permutation-invariant: sum, mean, max, or an attention-weighted sum. Sum keeps multiplicity (counts neighbours), mean and max discard it.
- $\phi$: update function combining the old state with the aggregate (concatenate + linear, GRU cell, or just the aggregate).

Stacking $L$ layers gives each node a receptive field of its $L$-hop neighbourhood. All parameters are shared across nodes (same $\psi,\phi$ everywhere), analogous to a convolution kernel shared across pixel positions; the number of parameters is independent of $N$.

### GCN (Kipf & Welling 2017 [S66])

$$
H^{(l+1)} = \sigma\big(\hat D^{-1/2}(A+I)\hat D^{-1/2}\, H^{(l)} W^{(l)}\big),\qquad \tilde A = A + I,\ \hat D = \mathrm{diag}(\tilde A \mathbf 1).
$$

Per node: $h_v^{(l+1)} = \sigma\big(\sum_{u\in N(v)\cup\{v\}} \frac{1}{\sqrt{\hat d_v \hat d_u}} W^{(l)\top} h_u^{(l)}\big)$, i.e. message $\psi = W^\top h_u$, aggregator = degree-weighted sum, update = nonlinearity. Parameters: $W^{(l)}\in\mathbb{R}^{F_l\times F_{l+1}}$ only.

Why self-loops: without $+I$ a node's new state ignores its own old state; with it, $v$ is its own neighbour and the layer is a weighted average of the closed neighbourhood. Why symmetric normalisation: $A$ alone scales features by the degree, so high-degree nodes get large activations and the spectral radius of $A$ grows with the graph, which makes deep stacks explode or vanish; $\hat D^{-1/2}\tilde A\hat D^{-1/2}$ has eigenvalues in $(-1, 1]$, so repeated application is numerically stable. Spectral motivation: a graph convolution with a filter $g_\theta$ on the normalised Laplacian $L = I - D^{-1/2}AD^{-1/2}$ can be approximated by a first-order Chebyshev polynomial $g_\theta \star x \approx \theta(I + D^{-1/2}AD^{-1/2})x$; this operator has eigenvalues in $[0,2]$, and replacing it by the renormalised $\hat D^{-1/2}(A+I)\hat D^{-1/2}$ (the "renormalisation trick") brings them back into $(-1,1]$. Compared to the random-walk normalisation $\hat D^{-1}\tilde A$ (row-stochastic, a true mean), the symmetric version is symmetric (real spectrum) and down-weights messages from high-degree neighbours.

Cost per layer: $O(|E| F_l + N F_l F_{l+1})$ with sparse $\hat A$; $O(N^2 F_l)$ with the dense matrix.

### GraphSAGE (Hamilton et al. 2017 [S68])

Sample a fixed number $k$ of neighbours per node per layer (e.g. 25 then 10), aggregate their states (mean, max-pool after an MLP, or LSTM over a random order), then concatenate with the node's own state:

$$
h_v^{(l+1)} = \sigma\big(W^{(l)}[\,h_v^{(l)} \,\|\, \mathrm{AGG}(\{h_u^{(l)} : u \in \mathcal{S}(N(v))\})\,]\big),
$$

often followed by $\ell_2$ normalisation. Sampling bounds the cost of a minibatch to $O(\prod_l k_l)$ nodes per target node regardless of degree, which makes minibatch training on graphs with $10^6$+ nodes possible. GraphSAGE is inductive: the learned $W^{(l)}$ and aggregator apply to unseen nodes or entirely new graphs, whereas the original GCN is usually trained full-batch on one fixed graph (transductive setting).

### GAT (Veličković et al. 2018 [S67])

Replace the fixed weights $1/\sqrt{\hat d_v\hat d_u}$ by learned attention coefficients:

$$
\alpha_{uv} = \mathrm{softmax}_u\big(\mathrm{LeakyReLU}(a^\top [W h_v \,\|\, W h_u])\big) = \frac{\exp(e_{uv})}{\sum_{u'\in N(v)\cup\{v\}}\exp(e_{u'v})},\qquad
h_v' = \sigma\Big(\sum_{u\in N(v)\cup\{v\}} \alpha_{uv} W h_u\Big),
$$

with $W\in\mathbb{R}^{F'\times F}$, $a\in\mathbb{R}^{2F'}$. The score is computed only for existing edges (mask $-\infty$ elsewhere), so the cost stays $O(|E| F')$. Multi-head attention with $K$ heads: concatenate $\|_{k=1}^K h_v'^{(k)}$ in hidden layers, average in the output layer. Compared to transformer self-attention (note 06) the score is additive ($a^\top[\cdot\|\cdot]$) rather than a dot product, and the attention is restricted to graph neighbours instead of all tokens. Attention lets the network down-weight noisy neighbours and gives per-edge weights that can be inspected, at the cost of a further set of parameters and a softmax per node.

### GIN and the WL expressivity limit

Two graphs are distinguishable by a message-passing GNN only if the 1-dimensional Weisfeiler-Lehman (1-WL) colour-refinement test distinguishes them (Xu et al. 2019; Morris et al. 2019). 1-WL iteratively relabels each node by hashing (own label, multiset of neighbour labels); this is exactly the message-passing recursion with an injective hash. GNNs with mean or max aggregators are strictly weaker than 1-WL because they cannot distinguish multisets that differ only in multiplicities ($\{a, a\}$ and $\{a\}$ collide under mean and max; $\{a, a, b, b\}$ and $\{a, b\}$ collide under mean), whereas 1-WL hashes the full multiset. The Graph Isomorphism Network (GIN) achieves the 1-WL bound with a sum aggregator and an MLP update, $h_v' = \mathrm{MLP}\big((1+\epsilon)h_v + \sum_{u\in N(v)} h_u\big)$, where the MLP makes the map on multisets injective (universal approximation of injective multiset functions). Consequence: no message-passing GNN can count triangles or distinguish two disjoint triangles from a 6-cycle (both are 2-regular, 1-WL gives identical colourings). Fixes: positional / structural encodings (Laplacian eigenvectors, random node IDs, subgraph counts), higher-order $k$-WL networks, or graph transformers with full attention plus positional encodings.

### Over-smoothing and over-squashing

Each GCN layer applies the operator $\hat A = \hat D^{-1/2}\tilde A\hat D^{-1/2}$; $\hat A^L$ converges (for a connected non-bipartite graph) to a rank-1 projection onto the dominant eigenvector $\propto \hat D^{1/2}\mathbf 1$ as $L\to\infty$, so node representations become proportional to $\sqrt{\hat d_v}$ times a shared vector and lose all node-specific information (Li et al. 2018; Oono & Suzuki 2020). Empirically accuracy on citation graphs peaks at 2-3 layers and drops beyond. Remedies: residual/skip connections and jumping knowledge (concatenate all layer outputs), normalisation of node features (PairNorm), dropping edges (DropEdge), decoupling propagation from transformation (APPNP: $K$ steps of personalised PageRank propagation of an MLP output). Over-squashing (Alon & Yahav 2021): the information from an exponentially growing $L$-hop neighbourhood is compressed into a fixed-size vector through bottleneck edges, so long-range dependencies are lost; remedies are graph rewiring or global attention.

### Tasks

Node classification (semi-supervised, transductive). One graph, labels for a small fraction of nodes (e.g. 20 per class on Cora), loss = cross-entropy on labelled nodes only, but the forward pass uses all nodes and edges, so unlabelled nodes contribute structure. Transductive: test nodes are in the graph during training (their features and edges are visible, their labels are not). Splits are node masks `train_mask`, `val_mask`, `test_mask` over the same graph, not separate datasets; leakage of labels is impossible but leakage of structure is the point. For an inductive evaluation, hold out whole graphs or remove test nodes and their edges during training.

Link prediction. Predict whether $(u,v)\in E$ from node embeddings $z = \mathrm{GNN}(A_{\text{train}}, X)$ with a decoder, most simply the dot product $p(u,v) = \sigma(z_u^\top z_v)$ (Kipf & Welling 2016, VGAE). Training: positive edges = a held-in subset of $E$, negative edges = sampled non-edges (negative sampling, typically 1:1), binary cross-entropy. Test edges are removed from the message-passing graph to avoid leakage. Metrics: AUC, average precision, hits@k.

Graph classification. One label per graph; after $L$ layers apply a readout $h_G = \mathrm{POOL}(\{h_v^{(L)}\}_{v\in V})$ with sum (size-sensitive, most expressive), mean or max (size-invariant), or hierarchical pooling (DiffPool, TopKPool), then an MLP. Batched via the block-diagonal trick with a `scatter` over the `batch` vector.

Where graphs appear: molecules (atoms = nodes, bonds = edges, property prediction; MoleculeNet, QM9), citation and social networks (Cora, PubMed, OGB), meshes and point clouds (vertices with $k$-NN edges), road/traffic networks (spatio-temporal GNNs), recommender systems (bipartite user-item graph, link prediction), knowledge graphs, physical simulation (particles with interaction edges), program analysis (ASTs, data-flow graphs).

### Practical

torch_geometric (PyG) API: a graph is a `Data(x=[N, F], edge_index=[2, E], y=[N] or [1], edge_attr=...)` object; layers such as `GCNConv(in, out)`, `SAGEConv`, `GATConv(in, out, heads=K)` take `(x, edge_index)` and implement the sparse scatter internally (`MessagePassing` base class with `message`, `aggregate`, `update` hooks); `torch_geometric.loader.DataLoader` collates a list of `Data` objects into one block-diagonal `Batch` with a `batch` vector; `global_mean_pool(x, batch)` does the readout; datasets `Planetoid('Cora')`, `TUDataset`, `OGB`. The reference code instead builds a dense $\hat A \in \mathbb{R}^{N\times N}$ once with `gcn_norm(adj)` and computes a layer as `adj_hat @ (h @ W)`; identical numerics, $O(N^2)$ memory, no dependency, adequate for $N \le 10^3$-$10^4$.

Stochastic block model (SBM) as synthetic benchmark: $N$ nodes in $k$ blocks; an edge between two nodes in the same block appears with probability $p_{\text{in}}$, across blocks with $p_{\text{out}} < p_{\text{in}}$. Expected within-block degree $(n_b - 1)p_{\text{in}}$, cross-block degree $(N - n_b)p_{\text{out}}$; with the reference defaults $n_b = 40$, $p_{\text{in}} = 0.3$, $p_{\text{out}} = 0.02$ each node has about $11.7$ within- and $1.6$ cross-block neighbours, so a one-hop mean already denoises the community signal. Node features are a noisy one-hot of the block, so a feature-only classifier is above chance and the GCN improves on it by averaging out the noise over neighbours. Recovery of communities is information-theoretically possible only above the Kesten-Stigum threshold $\propto (p_{\text{in}} - p_{\text{out}})^2 n_b /(p_{\text{in}} + (k-1)p_{\text{out}})$; lowering the gap $p_{\text{in}} - p_{\text{out}}$ is the knob to make the benchmark hard.

## Architecture sketch

2-layer GCN on an SBM graph, $N = 120$ (3 blocks of 40), $F = 3$ input features, 3 classes, hidden width 16, 12 labelled nodes (10%). Dense implementation as in `gnn_gcn.py`.

```
A      [120, 120] 0/1 symmetric          X  [120, 3]
   |                                        |
   v gcn_norm: A_hat = D^-1/2 (A+I) D^-1/2   |
A_hat  [120, 120]                           |
   |                                        |
   +----> A_hat @ (X @ W1)    W1 [3, 16], b1 [16]      -> [120, 16]
                 ReLU, dropout                          -> [120, 16]
   +----> A_hat @ (H1 @ W2)   W2 [16, 3], b2 [3]       -> [120, 3]  logits
                 cross_entropy(logits[train_mask], y[train_mask])   train_mask: 12 True of 120
                 argmax(logits[test_mask]) vs y[test_mask]          -> test_accuracy
```

Parameter count: $3\cdot 16 + 16 + 16\cdot 3 + 3 = 115$, independent of $N$. Receptive field of the output: 2 hops. Cost of one forward pass: two dense matmuls $[120,120]\times[120,16]$ and $[120,120]\times[120,3]$, about $2.6\cdot 10^5$ multiply-adds; with COO storage and $|E| \approx 120\cdot 13.3/2 \approx 800$ edges it would be $\approx 800\cdot 19$ instead.

Worked example: $\hat D^{-1/2}(A+I)\hat D^{-1/2}$ for the path graph $1 - 2 - 3$.

$$
A = \begin{pmatrix}0&1&0\\1&0&1\\0&1&0\end{pmatrix},\quad
\tilde A = A + I = \begin{pmatrix}1&1&0\\1&1&1\\0&1&1\end{pmatrix},\quad
\hat D = \mathrm{diag}(2, 3, 2),\quad
\hat D^{-1/2} = \mathrm{diag}\big(\tfrac{1}{\sqrt2}, \tfrac{1}{\sqrt3}, \tfrac{1}{\sqrt2}\big).
$$

Entry $(u, v)$ of the result is $\tilde A_{uv}/\sqrt{\hat d_u \hat d_v}$:

$$
\hat A = \begin{pmatrix}
\tfrac12 & \tfrac{1}{\sqrt6} & 0\\
\tfrac{1}{\sqrt6} & \tfrac13 & \tfrac{1}{\sqrt6}\\
0 & \tfrac{1}{\sqrt6} & \tfrac12
\end{pmatrix}
\approx \begin{pmatrix}
0.500 & 0.408 & 0\\
0.408 & 0.333 & 0.408\\
0 & 0.408 & 0.500
\end{pmatrix}.
$$

Row sums are $0.908,\ 1.149,\ 0.908$, so $\hat A$ is not row-stochastic (the random-walk version $\hat D^{-1}\tilde A$ would have rows $(\tfrac12,\tfrac12,0)$, $(\tfrac13,\tfrac13,\tfrac13)$, $(0,\tfrac12,\tfrac12)$). Eigenvalues of $\hat A$: $1$ (eigenvector $\propto(\sqrt2,\sqrt3,\sqrt2)^\top = \hat D^{1/2}\mathbf 1$), $\tfrac12$, $-\tfrac16$; all in $(-1,1]$ as claimed. With $X = I_3$ (one-hot node identity) one propagation step gives $\hat A X = \hat A$: node 2 has mixed in $0.408$ of each end node, and after two steps $\hat A^2$ already couples nodes 1 and 3 ($(\hat A^2)_{13} = 1/6$).

## Pitfalls

- Accuracy plateaus at the feature-only baseline -> $\hat A$ was built without self-loops or without normalisation, so activations scale with degree and the optimiser fights the scale instead of the signal -> use `gcn_norm(adj)` (add $I$, symmetric normalisation) and check `adj_hat.max() <= 1`.
- Training accuracy 100%, test accuracy at chance on a 3-class SBM -> only 12 labelled nodes and a wide hidden layer memorise labels; propagation is ineffective because $p_{\text{in}}\approx p_{\text{out}}$ -> add dropout and weight decay ($5\cdot 10^{-4}$ as in Kipf & Welling), verify the block signal with a 1-hop mean-of-neighbours baseline, widen the $p_{\text{in}} - p_{\text{out}}$ gap for debugging.
- Deeper model (6+ layers) performs worse than 2 layers -> over-smoothing, $\hat A^L$ collapses node states -> stay at 2-3 layers, or add residual connections / jumping knowledge / APPNP-style propagation.
- Test accuracy suspiciously high in link prediction -> test edges were left in the message-passing adjacency, so the encoder sees the answer -> remove validation and test edges from $A$ before encoding; sample negatives from non-edges of the full graph.
- Loss is NaN after the first step -> isolated node with degree 0 gives $\hat d_v = 0$ and $\hat d_v^{-1/2} = \infty$ (only possible if self-loops are missing) -> add $I$ before computing degrees, or clamp $\hat d_v \ge 1$.
- Out of memory on a graph with $N = 5\cdot 10^4$ nodes -> dense $[N, N]$ adjacency is $2.5\cdot 10^9$ floats = 10 GB -> switch to COO `edge_index` with scatter-add (`torch.index_add_` / `torch_scatter`) or torch_geometric; use neighbour sampling for minibatches.
- Graph classification with mean pooling cannot separate graphs that differ in size or count-based motifs -> mean readout and mean aggregation are below 1-WL -> use sum aggregation and sum readout (GIN), add structural features (degree, cycle counts).
- Same model, same seed, different accuracy across runs on MPS -> scatter-add and dense matmul are non-deterministic on GPU backends; with only 12 labelled nodes the variance across splits is large -> report mean $\pm$ std over $\ge 10$ random label splits and seeds, not one number.
- Directed edges silently treated as undirected (or vice versa) -> `edge_index` contains each undirected edge only once, so messages flow one way -> store both $(u,v)$ and $(v,u)$ for undirected graphs; check `A == A.T` in the dense case.
- GAT training diverges or attention is uniform -> LeakyReLU slope, missing self-loops, or masking with 0 instead of $-\infty$ before the softmax, which gives non-neighbours weight $\propto 1$ -> mask with a large negative number before `softmax`, include self-loops, use several heads with dropout on $\alpha$.

## Questions

1. Derive the per-node form of the GCN layer from the matrix form and identify $\psi$, $\bigoplus$, $\phi$ of the message-passing framework.

<details><summary>Answer</summary>
Row $v$ of $\hat A H W$ is $\sum_u \hat A_{vu} (H W)_u = \sum_{u \in N(v)\cup\{v\}} \frac{1}{\sqrt{\hat d_v\hat d_u}} W^\top h_u$. So $\psi(h_v, h_u) = W^\top h_u$ (a linear message that ignores the receiver), $\bigoplus$ = sum weighted by $1/\sqrt{\hat d_v \hat d_u}$ (a degree-normalised sum, permutation-invariant), $\phi(h_v, m_v) = \sigma(m_v)$ where the self term is already included via the self-loop.
</details>

2. Why does the GCN use $\hat D^{-1/2}\tilde A\hat D^{-1/2}$ instead of $\tilde A$ or $\hat D^{-1}\tilde A$? Give two reasons.

<details><summary>Answer</summary>
(i) Stability: the eigenvalues of $\tilde A$ grow with the maximum degree, so $L$ layers scale activations by up to $d_{\max}^L$; the symmetric normalisation has spectrum in $(-1,1]$, so repeated application neither explodes nor vanishes. (ii) Symmetry: $\hat D^{-1/2}\tilde A\hat D^{-1/2}$ is symmetric with real spectrum and orthogonal eigenvectors, which is what the spectral (Chebyshev) derivation needs; $\hat D^{-1}\tilde A$ is row-stochastic (a plain neighbour average) and works too but weights a high-degree neighbour's message by $1/\hat d_v$ only, whereas the symmetric form also divides by $\sqrt{\hat d_u}$, down-weighting hubs.
</details>

3. Two graphs: (a) two disjoint triangles, (b) a 6-cycle, all nodes with identical features. Can a 2-layer GCN with sum readout classify them differently? Can any message-passing GNN?

<details><summary>Answer</summary>
No and no. Both graphs are 2-regular with identical node features, so every node has the same state after every message-passing step (1-WL assigns one colour to all six nodes in both graphs), hence any permutation-invariant readout gives identical graph embeddings. This is the 1-WL bound (Xu et al. 2019); distinguishing them needs structural features (e.g. triangle count, Laplacian eigenvalues) or higher-order WL models.
</details>

4. Explain over-smoothing with the spectrum of $\hat A$ and state what a 2-layer versus a 20-layer linear GCN computes.

<details><summary>Answer</summary>
Write $\hat A = \sum_i \lambda_i q_i q_i^\top$ with $1 = \lambda_1 > |\lambda_2| \ge \dots$ for a connected non-bipartite graph. Then $\hat A^L X = q_1 q_1^\top X + \sum_{i\ge2} \lambda_i^L q_i q_i^\top X \to q_1 q_1^\top X$ as $L\to\infty$ with $q_1 \propto \hat D^{1/2}\mathbf 1$. A linear 2-layer GCN computes $\hat A^2 X W_1 W_2$, which still contains the $\lambda_i^2$-weighted components carrying node-specific information; at 20 layers $\lambda_i^{20}$ is negligible for $|\lambda_i| < 0.8$, so all rows of $\hat A^{20}X$ are proportional to $\sqrt{\hat d_v}$ times the same vector: the classifier sees only degree. Nonlinearities do not prevent this (Oono & Suzuki 2020).
</details>

5. You have a dataset of 5,000 molecules with a binary toxicity label. Set up a GNN pipeline: data representation, layer type, readout, loss, split, and metric. Which pitfall specific to graphs must the split avoid?

<details><summary>Answer</summary>
Each molecule is a `Data(x=[n_atoms, F_atom], edge_index=[2, 2·n_bonds], edge_attr=[2·n_bonds, F_bond], y=[1])` with atom type / charge / hybridisation one-hots and bond type as edge feature; batched block-diagonally with `DataLoader(batch_size=64)`. Layers: 3-4 GIN or GINE (edge-aware) layers with sum aggregation (counts substructures, matters for chemistry), hidden 64-128, batch norm, dropout 0.2. Readout: sum (or sum + mean concatenated) over atoms via `global_add_pool(x, batch)`, then an MLP to one logit, BCE-with-logits loss with a class weight if positives are rare. Split: scaffold split (group molecules by Bemis-Murcko scaffold) so that test molecules are structurally novel; a random split leaks near-duplicates and overestimates performance. Metric: ROC-AUC or PR-AUC, averaged over 3+ seeds. This is inductive graph classification, no transductive leakage issue.
</details>

6. Compute the GAT attention coefficients for a node $v$ with two neighbours $u_1, u_2$ and itself, given scores $e_{u_1 v} = 2$, $e_{u_2 v} = 0$, $e_{vv} = 1$, and write the update.

<details><summary>Answer</summary>
$\alpha_{\cdot v} = \mathrm{softmax}(2, 0, 1) = (e^2, 1, e)/(e^2 + 1 + e) = (7.389, 1, 2.718)/11.107 \approx (0.665, 0.090, 0.245)$. Update: $h_v' = \sigma(0.665\, W h_{u_1} + 0.090\, W h_{u_2} + 0.245\, W h_v)$. With $K$ heads each head has its own $W^{(k)}, a^{(k)}$ and the results are concatenated.
</details>

7. In the reference SBM experiment 10% of nodes are labelled. Why does the GCN reach a higher test accuracy than an MLP trained on the same 12 labelled nodes' features, and when would this advantage vanish?

<details><summary>Answer</summary>
The features of a node are a noisy one-hot of its block; a single node's feature is often wrong, but the 1-hop and 2-hop degree-weighted mean over $\approx 12$ same-block neighbours plus $\approx 2$ other-block neighbours averages the noise out (variance reduction by a factor $\approx 1/\hat d_v$), so the GCN input to the classifier is nearly the clean block indicator for every node, labelled or not. The MLP sees only 12 noisy vectors. The advantage vanishes when the graph carries no community information ($p_{\text{in}} \to p_{\text{out}}$, below the detectability threshold), when features are already clean, or when the labelled fraction is large enough for the MLP to average noise itself. It reverses on heterophilous graphs (neighbours tend to have different labels), where the neighbour mean destroys the signal.
</details>

8. Link prediction on a citation graph: describe training with negative sampling and explain why the dot-product decoder $\sigma(z_u^\top z_v)$ restricts what can be modelled.

<details><summary>Answer</summary>
Split $E$ into train/val/test edges (e.g. 85/5/10). Encoder $Z = \mathrm{GNN}(A_{\text{train}}, X)$. For each minibatch take positive pairs from train edges and sample the same number of negative pairs $(u, v')$ uniformly from non-edges (or by corrupting one endpoint); loss $= -\sum_{\text{pos}} \log\sigma(z_u^\top z_v) - \sum_{\text{neg}} \log(1 - \sigma(z_u^\top z_{v'}))$. Evaluate AUC on test edges versus an equal number of held-out negatives. The dot product is symmetric ($p(u,v) = p(v,u)$), so it cannot model directed relations, and it scores each node against a single embedding, so it cannot represent "$u$ is connected to $v$ and $w$ but $v$ and $w$ are not connected" beyond what the geometry allows (rank limit $\le$ embedding dimension). Bilinear $z_u^\top R z_v$ or an MLP on $[z_u \| z_v \| z_u \odot z_v]$ removes these restrictions.
</details>

## Code

`src/py/gnn_gcn.py`. `make_sbm(n_per_block=40, blocks=3, p_in=0.3, p_out=0.02, seed)` builds the dense symmetric adjacency, block labels and noisy one-hot node features of a stochastic block model. `gcn_norm(adj)` returns $\hat D^{-1/2}(A+I)\hat D^{-1/2}$ as a dense tensor. `GCN(in, hidden, out, layers=2)` stacks `layers` dense propagation-then-linear steps with ReLU between them. `run(steps=200, device=None, seed=0)` trains full-batch semi-supervised node classification with 10% labelled nodes using `common.train_loop` and returns `{"losses", "test_accuracy"}`; `python src/py/gnn_gcn.py` prints `gcn_norm` of the 3-node path graph (the worked example above), the SBM size and mean degree, and the parameter count and test accuracy of the GCN next to a feature-only MLP baseline. `test_gnn_gcn.py` calls `run` with a small step budget and asserts `common.loss_decreased(losses)` (mean of the last 10% of losses below the mean of the first 10%).

## References

- Goodfellow, Bengio, Courville, *Deep Learning* (2016), ch. 9 (convolution as parameter sharing over structured neighbourhoods), ch. 10 (recurrence as sharing over a chain), ch. 15.4 (semi-supervised learning).
- Kipf & Welling, "Semi-Supervised Classification with Graph Convolutional Networks", ICLR 2017 (GCN) [S66] -- **Lecture 11's reference 7** [S4].
- Kipf & Welling, "Variational Graph Auto-Encoders", 2016 (dot-product decoder, link prediction).
- Hamilton, Ying, Leskovec, "Inductive Representation Learning on Large Graphs", NeurIPS 2017 (GraphSAGE).
- Veličković et al., "Graph Attention Networks", ICLR 2018 (GAT) [S67] -- **Lecture 11's reference 6**; the lecture also uses his two intro talks.
- Gilmer et al., "Neural Message Passing for Quantum Chemistry", ICML 2017 (message-passing framework) [S69].
- Xu, Hu, Leskovec, Jegelka, "How Powerful are Graph Neural Networks?", ICLR 2019 (GIN, WL bound).
- Morris et al., "Weisfeiler and Leman Go Neural", AAAI 2019.
- Li, Han, Wu, "Deeper Insights into Graph Convolutional Networks", AAAI 2018; Oono & Suzuki, ICLR 2020 (over-smoothing).
- Alon & Yahav, "On the Bottleneck of Graph Neural Networks and its Practical Implications", ICLR 2021 (over-squashing).
- Fey & Lenssen, "Fast Graph Representation Learning with PyTorch Geometric", 2019.
- Bruna et al., ICLR 2014 and Defferrard et al., NeurIPS 2016 (spectral graph convolutions, Chebyshev filters).
- Hamilton, *Graph Representation Learning*, 2020 [S68] -- free book, **Lecture 11's reference 2**.
- **Lecture 11** [S4], *Graph Neural Networks*, is the lecture this note covers: graphs as inputs, what GNNs are, node/graph/link classification, **how to get the input graph** and how to get a better one (12 of 47 minutes -- the lecture spends more time on graph construction than on any single architecture, which is the part a project gets wrong), convolutional GNNs, the CORA dataset, GNNs in code, GAT, neural message passing, frameworks, applications (AlphaFold, antibiotic discovery).
