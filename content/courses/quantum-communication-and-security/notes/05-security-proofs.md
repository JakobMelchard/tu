# 05 Security proofs

Fifth TISS topic: "techniques for security proofs against collective and coherent attacks" [S2]; learning outcomes "compute asymptotic key rates" and "explain and argue how to use different techniques and theorems in a security proof". The chain is: go to the entanglement-based picture, bound Eve's knowledge by an entropy, handle general (coherent) attacks by symmetry or by an uncertainty relation, then plug into the key length of note 04.

## Definitions

1. **Individual attacks.** Eve interacts with each signal separately and measures her probe before the classical post-processing. Intercept-resend is one (note 02).
2. **Collective attacks.** Eve applies the same interaction to every signal independently, keeps her probes in a quantum memory and measures them jointly at any later time. After source replacement: $\rho_{ABE}^{\otimes n}$ (i.i.d.).
3. **Coherent (general) attacks.** Any joint state $\rho_{A^nB^nE}$; no i.i.d. structure.
4. **Entanglement-based (EB) picture.** Alice's preparation = measuring half of $|\Phi^+\rangle$ (source replacement, note 02 Def. 4); Eve controls the source or the channel, so Alice and Bob share an arbitrary $\rho_{A^nB^n}$ and Eve holds its purification.
5. **Bit and phase error.** For the EB state and key basis $Z$: bit error = $Z_A\ne Z_B$ (rate $e_Z$); phase error = $X_A\ne X_B$ (rate $e_X$). In BB84 the phase error rate is estimated from the rounds where both used $X$.
6. **Permutation invariance.** The protocol treats all rounds alike when the test positions are chosen at random; so WLOG the state $\rho_{A^nB^n}$ can be symmetrised over permutations of rounds.

## Results

**Theorem 5.1 (Devetak-Winter)** [S14; S4 Cor. 6.5.2]. For collective attacks and one-way reconciliation from Alice, the asymptotic rate
$$r=I(A{:}B)-\chi(A{:}E)=H(A|E)-H(A|B)$$
is achievable (Renner: $\min_{\sigma_{AB}\in\Gamma}H(X|E)-H(X|Y)$ over states compatible with the test [S4 Cor. 6.5.2]).
*Proof idea.* Per block of $n$ i.i.d. rounds, error correction leaks $\approx nH(A|B)$ (Slepian-Wolf), and by the AEP $H^\varepsilon_{\min}(A^n|E^n)\approx nH(A|E)$ [S4 Thm 3.3.6]; the leftover hash lemma extracts $nH(A|E)-nH(A|B)-o(n)$ bits. ∎

**Proposition 5.2 (BB84 under collective attacks: $1-2h(e)$).** Alice and Bob can apply random joint Pauli flips and relabelings that leave the protocol unchanged, so WLOG $\rho_{AB}$ is Bell-diagonal with $e_Z=\lambda_3+\lambda_4$, $e_X=\lambda_2+\lambda_4$ [S4 §7.1, S25]. By note 03 Prop. 3.2,
$$r(\boldsymbol\lambda)=1-H(\boldsymbol\lambda)+h(\lambda_1+\lambda_2)-h(e_Z)=1-H(\boldsymbol\lambda).$$
With $e_Z=e_X=e$ only $\lambda_4$ is free: $\boldsymbol\lambda=(1-2e+\lambda_4,\,e-\lambda_4,\,e-\lambda_4,\,\lambda_4)$. $H(\boldsymbol\lambda)$ is maximal at the product point $\lambda_4=e^2$, where $\boldsymbol\lambda=((1-e)^2,e(1-e),e(1-e),e^2)$ and $H=2h(e)$. Hence
$$r_{\min}=1-2h(e),\qquad\chi(Z{:}E)=h(e),\qquad I(A{:}B)=1-h(e).$$
Zero at $e^*=11.00\%$. (Checked numerically with the full four-party state: `devetak_winter_bb84_min`.)

**Theorem 5.3 (Shor-Preskill)** [S7]. BB84 is secure against coherent attacks with rate $1-h(e_Z)-h(e_X)$, i.e. $1-2h(e)$.
*Proof structure.* (i) Lo-Chau: an entanglement-distillation protocol with a random CSS code corrects bit errors ($\approx h(e_Z)$ syndrome bits) and phase errors ($\approx h(e_X)$), leaving near-perfect $|\Phi^+\rangle^{\otimes\ell}$ whose $Z$ measurement is a secret key. (ii) Random sampling bounds the phase error rate on the key rounds by the observed $X$-basis error, for *any* joint state, since Eve does not know which rounds are tested (note 02 Prop. 2.5). (iii) With CSS codes the phase correction commutes with the $Z$ measurement and becomes classical privacy amplification, and the bit correction becomes classical error correction; no quantum computer is needed, and the protocol is BB84. ∎

**Theorem 5.4 (reduction coherent → collective).**
- *Exponential de Finetti* [S4 Thm 4.3.2, S26]: a permutation-invariant state on $n+k$ systems is close, after tracing out $k$, to a mixture of almost-product states; entropies evaluated on product states then bound the general case.
- *Post-selection* [S19 Thm 1]: for permutation-covariant maps, $\|\mathcal E-\mathcal F\|_\diamond\le(n+1)^{d^2-1}\|(\mathcal E-\mathcal F)\otimes\mathrm{id}(\tau)\|_1$ with $\tau$ a purified de Finetti state, $d$ the per-round dimension. A protocol that is $\varepsilon$-secure against collective attacks is $\varepsilon(n+1)^{d^2-1}$-secure against coherent ones; compensate by shortening the key by $2(d^2-1)\log_2(n+1)$ bits [S19].
- *Uncertainty relation* [S21, S5]: no reduction needed. $H^\varepsilon_{\min}(X|E)+H^\varepsilon_{\max}(X|Y)\ge n\log\frac1c$ holds for any state; the $H_{\max}$ term is bounded by sampling (Serfling). This is the proof of [S5] and [S27].

**Theorem 5.5 (Tomamichel-Leverrier finite key)** [S5 Thms 2, 3]. Block $m$, $k$ test rounds, $n=m-k$, abort if test error $>\delta$, syndrome $r$ bits, hash $t$ bits, $c$ the overlap ($\tfrac12$ for BB84). Then for every $\nu\in(0,\tfrac12-\delta)$ the protocol is $\varepsilon_{\rm ec}+\varepsilon_{\rm pe}(\nu)+\varepsilon_{\rm pa}(\nu)$-secure with
$$\varepsilon_{\rm ec}=2^{-t},\quad\varepsilon_{\rm pe}(\nu)=2e^{-\frac{(m-k)k^2\nu^2}{m(k+1)}},\quad\varepsilon_{\rm pa}(\nu)=\tfrac12\sqrt{2^{-(m-k)(\log\frac1c-h(\delta+\nu))+r+t+\ell}}.$$
*How it is assembled:* uncertainty relation [S5 Cor. 5] + $H^{\varepsilon}_{\max}(X|Y)\le n\,h(\delta+\nu)$ from Serfling [S5 Eq. (80)] gives $H^\varepsilon_{\min}(X|E)\ge n(\log\frac1c-h(\delta+\nu))$; chain rule for $r+t$; leftover hash lemma. Asymptotically ($k=\sqrt m$, $\nu=1/\log m$, $r\approx nh(\delta)$) the rate is $\log\frac1c-2h(\delta)=1-2h(\delta)$, the Devetak-Winter value [S5 §5].

**Improvements beyond $1-2h(e)$.** Noisy preprocessing (Alice flips bits with probability $q$ before EC): BB84 tolerates 12.4 % [S4 §7.1, S25, S3 §III.B]. Two-way post-processing (advantage distillation) tolerates more [S3 §III.B].

## Worked example

**Asymptotic rates** (`key_rates.demo`):

| $e$ | $h(e)$ | $1-2h(e)$ | min DW at $\lambda_4$ | $\chi(Z{:}E)$ |
|---|---|---|---|---|
| 1 % | 0.0808 | 0.8384 | 0.8384 at $10^{-4}$ | 0.0808 |
| 3 % | 0.1944 | 0.6112 | 0.6112 at $9\times10^{-4}$ | 0.1944 |
| 5 % | 0.2864 | 0.4272 | 0.4272 at $2.5\times10^{-3}$ | 0.2864 |
| 8 % | 0.4022 | 0.1956 | 0.1956 at $6.4\times10^{-3}$ | 0.4022 |

Threshold $e^*=11.0028\%$ (`sp_threshold`).

**Finite key**, $\varepsilon=10^{-10}$, $r=1.1\,nh(\delta)$ (the leak model of [S5 Fig. 7]), $c=\tfrac12$, $k$, $\nu$ and the error split optimised (`finite_key_length`): $\ell/m$

| $m$ | $\delta=1\%$ | $2.5\%$ | $5\%$ |
|---|---|---|---|
| $10^4$ | 0.268 | 0.165 | 0.034 |
| $10^5$ | 0.520 | 0.385 | 0.201 |
| $10^6$ | 0.670 | 0.514 | 0.300 |
| $10^7$ | 0.751 | 0.582 | 0.351 |
| $10^8$ | 0.792 | 0.616 | 0.376 |
| $\infty$: $1-2.1h(\delta)$ | 0.830 | 0.646 | 0.399 |

At $m=10^6$, $\delta=1\%$ the optimum is $k=65\,111$ test rounds, $\nu=0.020$, $t=37$: $\varepsilon_{\rm ec}=7.3\times10^{-12}$, $\varepsilon_{\rm pe}=6\times10^{-11}$, $\varepsilon_{\rm pa}=2.3\times10^{-11}$. [S5 Fig. 7] plots $1-2h(\delta)$ as the dotted asymptote; with $f=1.1$ the true limit is $1-2.1h(\delta)$.

**Post-selection cost.** Two qubits per round, $d=4$: $2\cdot15\log_2(n+1)$ bits; for $n=10^6$ that is $598$ bits, negligible against $6.7\times10^5$.

## Pitfalls

- $1-2h(e)$ uses **both** QBERs: $1-h(e_Z)-h(e_X)$. Estimating only $e_Z$ says nothing about Eve (Prop. 2.3 of note 02).
- Devetak-Winter is for collective attacks; the de Finetti/post-selection or uncertainty-relation step is what extends it. Say which one you use.
- The minimisation over unobserved parameters ($\lambda_4$) is part of the proof: the rate is for the worst state compatible with the data.
- Shor-Preskill needs basis-independent sources; weak coherent pulses violate it (GLLP, note 06).
- In finite-key formulas $\varepsilon$'s are distances; "$\ell\approx n(1-2h(e))$ minus $O(\sqrt n)$" hides $\nu\propto1/\sqrt k$ inside $h(\delta+\nu)$, which dominates the loss.
- $c=\tfrac12$ assumes perfect BB84 measurements. Detector efficiency mismatch changes $c$ and is exactly how the uncertainty-relation proof incorporates device imperfections [S5 §9].

## Questions

1. *Distinguish individual, collective and coherent attacks.* Defs 1-3; collective = i.i.d. interaction with quantum memory and joint measurement.
2. *Derive the Devetak-Winter rate for BB84 with symmetric QBER $e$ and show it equals $1-2h(e)$.* Prop. 5.2.
3. *Outline the Shor-Preskill proof.* Theorem 5.3: CSS-code entanglement distillation, phase error from $X$ statistics by random sampling, CSS decoupling reduces to BB84 with classical EC and PA.
4. *How does one go from collective to coherent attacks?* Theorem 5.4: de Finetti, post-selection with $(n+1)^{d^2-1}$ penalty, or directly the entropic uncertainty relation.
5. *Write the Tomamichel-Leverrier key length and identify the origin of each term.* $\ell\le n(1-h(\delta+\nu))-r-t-2\log\frac1{2\varepsilon_{\rm pa}}$: uncertainty relation ($n\cdot1$), sampling ($h(\delta+\nu)$ with $\varepsilon_{\rm pe}$), EC leak $r$, verification $t$ ($\varepsilon_{\rm ec}=2^{-t}$), leftover hash lemma.

## Code

`src/py/key_rates.py`: `shor_preskill`, `sp_threshold`, `devetak_winter_bell_diagonal`, `holevo_eve`, `devetak_winter_bb84_min`, `finite_key_length`, `finite_key_errors`, `decoy_rate_curve`, `single_photon_rate`. Uses `entropies.h_z_given_e`. Tests: `test_key_rates.py` (DW minimum equals $1-2h$ at $\lambda_4=e^2$; finite key monotone, $\varepsilon$-secure, below the asymptote).

## References

[S3 §III.B], [S4 Thm 3.3.6, Thm 4.3.2, Cor. 6.5.2, §7.1], [S5 Thms 2-3, Cor. 5, §5, §9], [S7], [S14], [S19], [S21], [S25], [S26], [S27].
