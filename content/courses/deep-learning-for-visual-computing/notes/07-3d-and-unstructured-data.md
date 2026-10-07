# 07 Deep learning for 3D and unstructured data

> TISS item 6 [S1, S3]. Catalogue weight: low so far; only 2D vs 2.5D vs 3D
> CNNs in the medical block [S8, S9]. But the 2026S learning outcome now reads
> "image **and 3D data** analysis" [S3], and the lead lecturer works on point
> clouds, graphs and implicit representations [S31]: expect this topic to grow.
> Papers: PointNet [S30], Monte Carlo convolution [S31], MeshCNN [S32], NeRF
> [S33]. Graph message passing: [ADL 07 GNNs](../../applied-deep-learning/notes/07-gnns.md).

## What it is

A CNN assumes a regular grid: neighbours are implicit in the array index, the
kernel is a fixed array of weights, and translation acts by shifting indices.
3D data breaks some or all of this. Each representation below trades grid
convenience for memory, and the architecture follows from which symmetry the
representation must respect.

## Representations

| representation | structure | network | cost / problem |
|---|---|---|---|
| multi-view images | several 2D renders | 2D CNN per view, pool over views | needs camera choice; occlusion |
| depth map (2.5D) | $H\times W$ grid of depths | 2D CNN with a depth channel | one viewpoint only |
| volume / voxels | $N^3$ grid (CT, MRI, occupancy) | 3D CNN, $k^3C_{in}C_{out}$ weights | memory $O(N^3)$, mostly empty |
| point cloud | unordered set $\{p_i\}\subset\mathbb R^3$ (+ features) | PointNet(++), point convolutions | no grid, no order, uneven density |
| mesh | vertices + faces, a graph on a surface | graph / edge convolutions (MeshCNN) | irregular valence, topology |
| implicit function | $f_\theta:\mathbb R^3\to$ occupancy, SDF, or density + colour | MLP queried at points (NeRF) | per-scene optimisation, slow rendering |

**2D, 2.5D, 3D CNNs** (the medical question [S8, S9]). 2D: each slice of a
volume separately, no inter-slice context, cheap, can use ImageNet
pre-training. 2.5D: neighbouring or three orthogonal slices stacked as
channels of a 2D net: some 3D context at 2D cost. 3D: $k\times k\times k$
kernels over the volume: full context, $k$ times more weights per layer,
cubic activation memory, little pre-training available.

## Point clouds

**Requirement.** A function on a set must be **permutation invariant**:
$f(p_{\pi(1)},\dots,p_{\pi(n)}) = f(p_1,\dots,p_n)$ for every permutation
$\pi$ (and, for segmentation, per-point outputs must be permutation
*equivariant*). Feeding the $n\times3$ array to an MLP or 1-D CNN violates it.

**PointNet** [S30]. $f(P) = \gamma\big(\max_{i} h(p_i)\big)$: a shared MLP $h$
lifts every point to $\mathbb R^{1024}$ independently, an elementwise max over
points (a symmetric function) aggregates, $\gamma$ classifies. Invariant by
construction; PointNet proves such functions approximate any continuous set
function (Hausdorff-continuous). The max selects a sparse set of *critical
points* that determine the output, which explains robustness to missing
points. A small T-Net predicts an alignment matrix for rough rotation
normalisation. Segmentation: concatenate the global vector to each point's
feature and run a second shared MLP per point.
**Limitation:** no local neighbourhoods, so no hierarchy of local features
(the thing that makes CNNs work).

**PointNet++** [S30]. Hierarchy: farthest-point sampling picks centroids,
a ball query of radius $r$ groups neighbours, a mini-PointNet summarises
each group (in local coordinates $p_j - c$); repeat with larger radii.
Multi-scale grouping handles uneven density.

**Point convolution** [S31]. Write the continuous convolution
$(F * g)(x) = \int F(y)\,g(x - y)\,dy$ and estimate it from the samples
inside a receptive radius $r$ with Monte Carlo:
$$ (F * g)(x) \approx \frac{1}{|\mathcal N(x)|}\sum_{j\in\mathcal N(x)}\frac{F(y_j)\,g\!\big((x - y_j)/r\big)}{\hat p(y_j\mid x)}, $$
where the kernel $g$ is itself a small MLP on the offset and $\hat p$ is a
kernel density estimate of the sampling density. Dividing by $\hat p$ makes
the result independent of how densely the surface was scanned: the point of
Hermosilla et al.'s Monte Carlo convolution.

## Meshes and graphs

A mesh is a graph with geometry. Message passing
$h_v' = \phi\big(h_v, \bigoplus_{u\in\mathcal N(v)}\psi(h_v, h_u, e_{uv})\big)$
with a permutation-invariant $\bigoplus$ (sum, mean, max) generalises
convolution to irregular neighbourhoods (ADL 07). MeshCNN [S32] convolves over
**edges**: each edge has exactly four neighbouring edges (two triangles), so a
fixed-size, order-symmetrised kernel applies; pooling collapses edges.

## Implicit representations and NeRF

**NeRF** [S33]. An MLP $F_\theta(\mathbf x, \mathbf d) = (\sigma, \mathbf c)$
maps a 3D position and viewing direction to volume density and colour. A pixel
is rendered by integrating along its camera ray $\mathbf r(t) = \mathbf o + t\mathbf d$:
$$ C(\mathbf r) = \int T(t)\,\sigma(\mathbf r(t))\,\mathbf c(\mathbf r(t),\mathbf d)\,dt,\qquad T(t) = e^{-\int_0^t\sigma}, $$
discretised as $\hat C = \sum_i T_i\,\alpha_i\,\mathbf c_i$,
$\alpha_i = 1 - e^{-\sigma_i\delta_i}$, $T_i = \prod_{j<i}(1-\alpha_j)$.
Everything is differentiable, so $\theta$ is fitted to a set of posed photos
of **one scene** by $\sum\|\hat C - C_{\text{photo}}\|^2$; new views are
rendered afterwards. Positional encoding
$\gamma(p) = (\sin 2^k\pi p, \cos 2^k\pi p)_{k<L}$ lets the MLP represent high
frequencies (an MLP on raw coordinates is biased to smooth functions). Density
depends on position only, colour also on direction (view-dependent effects).

## Worked examples

**Voxel cost.** $64^3 = 262\,144$ cells. A $3\times3\times3$ conv $32\to32$:
$27\cdot32\cdot32 = 27\,648$ weights, $27\,648\times262\,144 = 7.2\cdot10^9$
MACs, and one activation tensor of $32\times64^3$ floats is 33.5 MB. At
$128^3$ both grow $8\times$.

**PointNet sizes.** Shared MLP $3\to64\to64\to128\to1024$: $256 + 4\,160 +
8\,320 + 132\,096 = 144\,832$ parameters, independent of $n$; on $n = 2\,048$
points about $2048\times143\,552 \approx 2.9\cdot10^8$ MACs. Permuting the rows
of $P$ permutes the rows of $h(P)$ and leaves the column-wise max unchanged.

**Volume rendering by hand.** Three samples, $\delta = 0.5$,
$\sigma = (0, 2, 10)$, grey levels $c = (0.2, 0.8, 0.5)$.
$\alpha = (0,\ 1 - e^{-1},\ 1 - e^{-5}) = (0, 0.632, 0.993)$;
$T = (1, 1, 0.368)$; weights $T\alpha = (0, 0.632, 0.365)$, opacity 0.998;
$\hat C = 0.632\cdot0.8 + 0.365\cdot0.5 = 0.688$. The empty first sample
contributes nothing, the second dominates, the third is half hidden.

## Pitfalls

- Treating a point cloud as an image of coordinates: the result depends on
  point order.
- Assuming PointNet is rotation invariant: it is permutation invariant; rotations
  are handled (partly) by the T-Net and augmentation.
- Voxelising at a resolution where thin structures vanish (sampling, note 01).
- Expecting NeRF to generalise across scenes: the vanilla version is one
  network per scene.
- Forgetting density normalisation when scans are non-uniform.

## Exam-style questions

1. **Difference between 2D, 2.5D and 3D CNNs; when would you use each?**
   *(17, 20)* As in the table and paragraph; 2.5D when volumes are large and
   data few, 3D when inter-slice structure matters and memory allows.
2. **Why can an MLP not be applied to a raw point cloud, and how does PointNet
   fix it?** *(ours)* Output would depend on point order; shared per-point
   MLP + symmetric max aggregation is invariant by construction.
3. **What does PointNet++ add?** *(ours)* Local neighbourhoods and a
   hierarchy (sampling, grouping, local PointNets), the analogue of a CNN's
   growing receptive field.
4. **Why divide by the sampling density in a point convolution?** *(ours)*
   The Monte Carlo sum otherwise over-weights densely scanned regions; dividing
   by $\hat p$ gives an estimate of the continuous convolution that does not
   depend on the scanner.
5. **What is a NeRF, how is it trained, and what is positional encoding for?**
   *(ours)* A scene as an MLP from position and direction to density and colour,
   rendered by differentiable volume rendering and fitted to posed photos;
   encoding lifts coordinates to sinusoids so fine detail is learnable.

## Code

No dedicated module: the calculations above are one-liners. Parameter counts
of 3D convolutions follow `src/py/conv_arithmetic.py` `conv_params` with $k^2$
replaced by $k^3$.
