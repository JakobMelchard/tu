# 02 Composite systems, partial trace, generalised Bloch decomposition (TISS 1.2)

TISS 1.2: "Tensor products of vectors and operators, expectation values, partial trace, reduced states, generalized Bloch decomposition" [S2]. The central fact: the partial trace is the *only* consistent rule for local statistics, and it is what makes a pure global state look mixed locally. Sources: Preskill ch. 2 §2.3.1 [S6]; Wilde §3.5, §4.3.3 [S11]; Nielsen & Chuang §2.2.8, §2.4.3 [S13]; Bertlmann & Friis ch. 11 [S14].

## Definitions

- **Tensor product** $\mathcal H_A\otimes\mathcal H_B$, basis $|i\rangle\otimes|j\rangle=|ij\rangle$, $\dim=d_Ad_B$. Vectors: $(|a\rangle\otimes|b\rangle)_{(ij)}=a_ib_j$; inner product $\langle a\otimes b|a'\otimes b'\rangle=\langle a|a'\rangle\langle b|b'\rangle$. Operators: $(A\otimes B)(|a\rangle\otimes|b\rangle)=A|a\rangle\otimes B|b\rangle$; `np.kron` with $A$ as the left (slow) index. $(A\otimes B)(C\otimes D)=AC\otimes BD$, $\operatorname{tr}(A\otimes B)=\operatorname{tr}A\operatorname{tr}B$.
- **Product vs entangled (pure):** $|\psi\rangle$ is product iff $|\psi\rangle=|a\rangle\otimes|b\rangle$; otherwise entangled. Coefficient matrix $C_{ij}=\langle ij|\psi\rangle$: product iff $\operatorname{rank}C=1$ (see [04](04-schmidt-decomposition-and-purification.md)).
- **Partial trace** over $B$: the linear map $\operatorname{tr}_B:\mathcal L(\mathcal H_A\otimes\mathcal H_B)\to\mathcal L(\mathcal H_A)$ with $\operatorname{tr}_B(X\otimes Y)=X\operatorname{tr}Y$, i.e. $\operatorname{tr}_BM=\sum_j(I\otimes\langle j|)M(I\otimes|j\rangle)$, in components $(\operatorname{tr}_BM)_{ik}=\sum_jM_{ij,kj}$.
- **Reduced state** $\rho_A=\operatorname{tr}_B\rho_{AB}$.

## Results with proofs

**Thm 2.1 (the partial trace is forced).** $\rho_A=\operatorname{tr}_B\rho_{AB}$ is the unique operator with $\operatorname{tr}(\rho_AX)=\operatorname{tr}(\rho_{AB}(X\otimes I))$ for all $X\in\mathcal L(\mathcal H_A)$.
*Proof.* Existence: $\operatorname{tr}(\rho_{AB}(X\otimes I))=\sum_{i,k,j}\rho_{ij,kj}X_{ki}=\operatorname{tr}(\rho_AX)$. Uniqueness: if $\operatorname{tr}(\sigma X)=\operatorname{tr}(\rho_AX)$ for all $X$, take $X=|k\rangle\langle i|$ to get $\sigma_{ik}=(\rho_A)_{ik}$. $\square$ So any other "local state" rule would give wrong local expectation values.

**Prop. 2.2 (reduced states are states).** $\operatorname{tr}\rho_A=\operatorname{tr}\rho_{AB}=1$; $\langle\phi|\rho_A|\phi\rangle=\sum_j\langle\phi j|\rho_{AB}|\phi j\rangle\ge0$; Hermiticity componentwise. $\square$ Products: $\operatorname{tr}_B(\rho\otimes\sigma)=\rho$.

**Prop. 2.3 (no signalling).** For any unitary (indeed any channel) $V$ on $B$: $\operatorname{tr}_B[(I\otimes V)\rho_{AB}(I\otimes V^\dagger)]=\rho_A$.
*Proof.* $\operatorname{tr}(\,\cdot\,(X\otimes I))$ of the left side is $\operatorname{tr}(\rho_{AB}(I\otimes V^\dagger)(X\otimes I)(I\otimes V))=\operatorname{tr}(\rho_{AB}(X\otimes I))$; apply Thm 2.1. Also a measurement on $B$ averaged over outcomes: $\sum_m\operatorname{tr}_B[(I\otimes P_m)\rho(I\otimes P_m)]=\operatorname{tr}_B\rho$ by cyclicity inside $\operatorname{tr}_B$ (allowed for operators on $B$ only). $\square$ This is why teleportation needs the classical bits ([08](08-teleportation-swapping-dense-coding.md)).

**Prop. 2.4 (pure global, mixed local).** For $|\Phi^+\rangle=\tfrac1{\sqrt2}(|00\rangle+|11\rangle)$: $\rho_A=\tfrac12(|0\rangle\langle0|+|1\rangle\langle1|)=I/2$. In general $\rho_A=CC^\dagger$, $\rho_B=C^TC^*$ for $|\psi\rangle=\sum C_{ij}|ij\rangle$; both have spectrum $\{s_k^2\}$ (singular values of $C$), so $\rho_A$ pure iff $|\psi\rangle$ product. Maximal local ignorance with maximal global knowledge is the signature of pure-state entanglement (quantified in [03](03-entropy.md), [10](10-entanglement.md)).

**Expectation values.** For product states $\langle A\otimes B\rangle_{\rho\otimes\sigma}=\langle A\rangle_\rho\langle B\rangle_\sigma$. The **connected correlation** $\langle A\otimes B\rangle-\langle A\otimes I\rangle\langle I\otimes B\rangle$ vanishes on products, is nonzero for classically correlated *and* entangled states; correlations alone do not certify entanglement (Bell inequalities and witnesses do: [06](06-non-locality-and-bell-inequalities.md), [10](10-entanglement.md)).

**Thm 2.5 (generalised Bloch decomposition).** With Gell-Mann bases $\{\lambda_i\}$ on $A$ ($d_A^2-1$ elements) and $\{\mu_j\}$ on $B$, normalised $\operatorname{tr}\lambda_i\lambda_k=2\delta_{ik}$:
$$\rho_{AB}=\frac1{d_Ad_B}\Big(I\otimes I+\tfrac{d_A}2\,\vec a\cdot\vec\lambda\otimes I+\tfrac{d_B}2\,I\otimes\vec b\cdot\vec\mu+\tfrac{d_Ad_B}4\sum_{ij}t_{ij}\lambda_i\otimes\mu_j\Big),$$
$a_i=\langle\lambda_i\otimes I\rangle$, $b_j=\langle I\otimes\mu_j\rangle$, $t_{ij}=\langle\lambda_i\otimes\mu_j\rangle$.
*Proof.* $\{\lambda_i\otimes\mu_j\}$ with $I$ adjoined on either side is an orthogonal operator basis of $\mathcal L(\mathcal H_A\otimes\mathcal H_B)$ ($d_A^2d_B^2$ elements); coefficients by $\operatorname{tr}[(\lambda_i\otimes\mu_j)(\lambda_k\otimes\mu_l)]=4\delta_{ik}\delta_{jl}$ etc. $\square$
Consequences: (i) $\rho_A=I/d_A+\tfrac12\vec a\cdot\vec\lambda$: the local Bloch vectors are the reduced states, and $\operatorname{tr}_B$ simply deletes every term containing a traceless $\mu_j$. (ii) $\operatorname{tr}\rho^2=\frac1{d_Ad_B}\big(1+\tfrac{d_A}2|\vec a|^2+\tfrac{d_B}2|\vec b|^2+\tfrac{d_Ad_B}4\|T\|_2^2\big)$. (iii) product state $\Rightarrow T=\vec a\vec b^{\,T}$ (rank one). (iv) Qubits: $\rho=\tfrac14(I+\vec a\cdot\vec\sigma\otimes I+I\otimes\vec b\cdot\vec\sigma+\sum t_{ij}\sigma_i\otimes\sigma_j)$.

**Prop. 2.6 (local unitaries act as rotations).** For qubits $U\sigma_iU^\dagger=\sum_kO_{ki}\sigma_k$ with $O\in SO(3)$, so $(U_A\otimes U_B)$ maps $(\vec a,\vec b,T)\mapsto(O_A\vec a,O_B\vec b,O_ATO_B^T)$. By the signed SVD every $T$ can be brought to diagonal form by local unitaries: the "T-state" normal form used for Bell values ([06](06-non-locality-and-bell-inequalities.md)). Bell states: $\vec a=\vec b=0$, $T=\operatorname{diag}(1,-1,1)$ for $\Phi^+$, $-I$ for $\Psi^-$.

## Worked example

$\rho=\tfrac12(|00\rangle\langle00|+|11\rangle\langle11|)$ (classically correlated) vs $|\Phi^+\rangle\langle\Phi^+|$. Both: $\rho_A=\rho_B=I/2$, $\vec a=\vec b=0$. Correlation tensors: classical $T=\operatorname{diag}(0,0,1)$, Bell $T=\operatorname{diag}(1,-1,1)$. Purities $\tfrac14(1+1)=\tfrac12$ vs $\tfrac14(1+3)=1$. Same marginals, different global states: the marginals never determine the joint state, and the difference sits entirely in $T$. $\langle Z\otimes Z\rangle=1$ for both; $\langle X\otimes X\rangle=0$ vs $1$: correlations in *complementary* bases distinguish entanglement (basis of BB84/E91 security, [09](09-quantum-cryptography.md)).

## Pitfalls

- $\operatorname{tr}_B(AB)\ne\operatorname{tr}_B(BA)$ in general; cyclicity inside a partial trace holds only for operators acting on $B$ alone.
- Ordering: `kron(A, B)` puts $A$ on the slow index; mixing conventions silently permutes subsystems. `partial_trace(rho, dims, keep)` keeps subsystems in their original order.
- $\rho_A\otimes\rho_B\ne\rho_{AB}$ unless the state is a product; mutual information measures the gap ([03](03-entropy.md)).
- A diagonal $T$ with $|\vec a|=|\vec b|=0$ is not automatically entangled: $\Phi^+$ has $\sum|t_{ii}|=3$, the classical example 1; the separable region for such states is $\sum|t_{ii}|\le1$ (octahedron inside the tetrahedron).

## Oral-exam questions (model answers)

1. *Why is the partial trace the right definition of a reduced state?* Thm 2.1: unique operator reproducing $\langle X\otimes I\rangle$ for all local $X$.
2. *Show that operations on B do not change $\rho_A$ and interpret.* Prop. 2.3: cyclicity for $V$ on $B$; no-signalling; measurement averaged over outcomes likewise.
3. *Compute the reduced state of a general two-qubit pure state; when is it pure?* $\rho_A=CC^\dagger$, eigenvalues = squared singular values of $C$; pure iff $\operatorname{rank}C=1$ iff product.
4. *Write the two-qubit Bloch decomposition and read off the marginals and the purity.* Thm 2.5(iv); $\rho_A=\tfrac12(I+\vec a\cdot\vec\sigma)$; $\operatorname{tr}\rho^2=\tfrac14(1+|\vec a|^2+|\vec b|^2+\|T\|_2^2)$.
5. *How do local unitaries act on $(\vec a,\vec b,T)$, and what normal form follows?* $SU(2)\to SO(3)$ adjoint action; $T\mapsto O_ATO_B^T$; signed SVD makes $T$ diagonal.

## Code

`src/py/states.py`: `kron`, `partial_trace(rho, dims, keep)` (einsum over any subset), `two_qubit_decomposition`, `from_two_qubit_decomposition`, `bipartite_bloch`, `from_bipartite_bloch`. Tests `test_states.py`: partial trace of a three-party product, agreement with the explicit $\sum_j(I\otimes\langle j|)\rho(I\otimes|j\rangle)$, invariance under local unitaries on the traced system, singlet $T=-I$, $2\times3$ round trip with marginals and the purity formula, $T=\vec a\vec b^{\,T}$ for products.
