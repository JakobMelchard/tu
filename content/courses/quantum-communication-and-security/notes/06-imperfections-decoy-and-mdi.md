# 06 Imperfections: photon-number splitting, decoy states, MDI-QKD

Last TISS topic: "dealing with imperfections (decoy state method and MDI-QKD)" [S2]; learning outcome "identify and discuss assumptions and weaknesses of different security proofs and protocols". The lecturer's own 2026 review [S32] surveys this topic (security proofs with imperfections); read it before the last lectures.

## Definitions

1. **Weak coherent pulse (WCP), phase randomised.** $\frac1{2\pi}\int d\phi\,|\sqrt\mu e^{i\phi}\rangle\langle\cdot|=\sum_ne^{-\mu}\frac{\mu^n}{n!}|n\rangle\langle n|$: a Poisson mixture of Fock states, the photon number unknown to Bob but in principle measurable by Eve.
2. **Channel model** [S9 Eqs. (5)-(11)]. $\eta=10^{-\alpha L/10}\eta_{\rm Bob}$; $n$-photon transmittance $\eta_n=1-(1-\eta)^n$; yield $Y_n=Y_0+\eta_n-Y_0\eta_n$; error $e_n=(e_0Y_0+e_d\eta_n)/Y_n$, $e_0=\tfrac12$; gain $Q_\mu=\sum_nY_ne^{-\mu}\mu^n/n!=Y_0+1-e^{-\eta\mu}$; $E_\mu Q_\mu=e_0Y_0+e_d(1-e^{-\eta\mu})$.
3. **Photon-number splitting (PNS) attack** [S18]. Eve measures the photon number (non-demolition), blocks single-photon pulses, keeps one photon of each multi-photon pulse and sends the rest to Bob over a lossless line. She learns every multi-photon bit after basis announcement with no errors. Undetectable by $Q_\mu$ and $E_\mu$ alone as long as $P(n\ge2)\gtrsim Q_\mu$.
4. **Decoy states** [S17, S8]. Alice randomly varies the intensity $\mu\in\{\mu_{\rm s},\nu_1,\nu_2,\dots\}$. An $n$-photon pulse carries no record of which intensity produced it, so $Y_n$ and $e_n$ are the **same** for all intensities; measuring $Q_\nu,E_\nu$ for several $\nu$ constrains them.
5. **MDI-QKD** [S10]. Alice and Bob each send BB84 WCPs (with decoys) to an untrusted relay (Charlie) who performs a linear-optics Bell-state measurement (BSM) and announces the outcome.

## Results

**Proposition 6.1 (PNS makes the rate $O(\eta^2)$ without decoys: GLLP)** [S15; S9 Eq. (3)]. Tag all multi-photon detections as insecure, fraction $\Delta\le P(n\ge2)/Q_\mu=(1-(1+\mu)e^{-\mu})/Q_\mu$. Then
$$R=q\,Q_\mu\Bigl\{-f\,h(E_\mu)+(1-\Delta)\Bigl[1-h\Bigl(\tfrac{E_\mu}{1-\Delta}\Bigr)\Bigr]\Bigr\}.$$
Need $\Delta<1$: $\mu^2/2\lesssim\eta\mu$, i.e. $\mu=O(\eta)$, so $R=O(\eta^2)$.

**Theorem 6.2 (decoy-state rate)** [S8, S9 Eq. (1)].
$$R\ge q\bigl\{-Q_\mu f(E_\mu)h(E_\mu)+Q_1[1-h(e_1)]\bigr\},\qquad Q_1=Y_1\mu e^{-\mu},\ q=\tfrac12.$$
Only single-photon detections contribute key; multi-photon ones count fully towards error-correction leakage. With $Y_1\approx\eta$, $\mu=O(1)$: **$R=O(\eta)$**. Optimal $\mu$ for small $\eta$ solves $(1-\mu)e^{-\mu}=fh(e_d)/(1-h(e_d))$ [S9 Eq. (12)].

**Theorem 6.3 (vacuum + weak decoy bounds)** [S9 Eqs. (20), (34), (37)]. With $\nu<\mu$ and a vacuum decoy giving $Y_0$ exactly:
$$Y_1\ge Y_1^L=\frac{\mu}{\mu\nu-\nu^2}\Bigl(Q_\nu e^\nu-Q_\mu e^\mu\frac{\nu^2}{\mu^2}-\frac{\mu^2-\nu^2}{\mu^2}Y_0\Bigr),\qquad e_1\le e_1^U=\frac{E_\nu Q_\nu e^\nu-e_0Y_0}{Y_1^L\,\nu}.$$
*Derivation.* $Q_\nu e^\nu=Y_0+Y_1\nu+\sum_{n\ge2}Y_n\nu^n/n!$ and the same for $\mu$. For $n\ge2$ and $\nu<\mu$: $\nu^n/\mu^n\le\nu^2/\mu^2$, so $\sum_{n\ge2}Y_n\nu^n/n!\le\frac{\nu^2}{\mu^2}\sum_{n\ge2}Y_n\mu^n/n!=\frac{\nu^2}{\mu^2}(Q_\mu e^\mu-Y_0-Y_1\mu)$. Insert and solve for $Y_1$. For $e_1$: $E_\nu Q_\nu e^\nu=e_0Y_0+e_1Y_1\nu+(\ge0)$, then use $Y_1\ge Y_1^L$. Equality iff Eve gives yield only to $n=2$ [S9 §3.3]. ∎ As $\nu\to0$ both bounds become tight [S9 Eqs. (27)-(28)].

**Proposition 6.4 (why the decoy exposes PNS).** Eve keeping $Q_\mu$ fixed while blocking $n=1$ must give multi-photon pulses a yield $y=(Q_\mu-Y_0e^{-\mu})/P_\mu(n\ge2)$. The weak decoy then has $Q_\nu^{\rm PNS}=Y_0e^{-\nu}+y\,P_\nu(n\ge2)\propto\nu^2$, far below the honest $\approx\eta\nu$, and $Y_1^L\le0$: no key, attack detected.

**MDI-QKD protocol** [S10]. Charlie: 50:50 beam splitter, polarising beam splitters, detectors $D_{1H},D_{1V},D_{2H},D_{2V}$. $|\psi^-\rangle$ = clicks $(1H,2V)$ or $(1V,2H)$; $|\psi^+\rangle$ = $(1H,1V)$ or $(2H,2V)$. Sifting: keep announced successes with equal bases; Bob flips his bit except for ($X$ basis, $\psi^+$) [S10 Table I]. Single-photon inputs: $Y_{11}=\eta_a\eta_b/2$ in both bases (BSM success $\tfrac12$), $e_{11}=0$ ideally (HOM bunching removes wrong-parity events) [S10; S11 Eq. (A9)].
$$R=Q_{11}^Z[1-h(e_{11}^X)]-Q^Z_{\rm rect}f\,h(E^Z_{\rm rect}),\qquad Q_{11}=\mu_a\mu_be^{-\mu_a-\mu_b}Y_{11}\quad[\text{S10 Eq. (1)}].$$

**Why MDI removes detector attacks.** The relay's output is a public classical announcement; the security proof is the time-reverse of entanglement-based QKD: Alice and Bob's states are entangled with their virtual qubits, and Charlie's BSM (honest or not) at best performs entanglement swapping. Whatever Charlie's devices do, his announcement is a message Eve could have sent herself, so blinding, efficiency mismatch and time-shift attacks on detectors [S31] give nothing [S10]. The sources must still be characterised (state preparation flaws are handled with decoys and the quantum-coin argument [S10]).

**Device-independent QKD.** DI-QKD drops the device model altogether: security follows from a Bell (CHSH) violation, since near-maximal CHSH certifies near-maximal entanglement and bounds Eve's information for any devices [S28]; the entropy accumulation theorem extends collective-attack bounds to general attacks with tight finite-size terms [S29]. It needs loophole-free Bell violations with high detection efficiency, so rates are tiny; the first complete DI-QKD demonstration used trapped ions [S30]. The lecturer co-authored an analysis of what realising DI-QKD requires [S34]. Positioning: BB84 (trusted devices) → MDI (untrusted measurement) → DI (untrusted everything).

## Worked example

**Decoy BB84, GYS parameters** ($\alpha=0.21$ dB/km, $\eta_{\rm Bob}=0.045$, $Y_0=1.7\times10^{-6}$, $e_d=3.3\%$, $f=1.22$, $q=\tfrac12$ [S9 Table 1]; `decoy.demo`):
- $\mu_{\rm opt}$ from Eq. (12): 0.479 (paper 0.48).
- At 50 km, $\mu=0.48$: $\eta=4.01\times10^{-3}$, $Q_\mu=1.92\times10^{-3}$, $E_\mu=3.34\%$, $Y_1=4.01\times10^{-3}$, $e_1=3.32\%$. Weak decoy $\nu=0.05$: $Q_\nu=2.02\times10^{-4}$, $E_\nu=3.69\%$, so $Y_1^L=3.95\times10^{-3}$, $e_1^U=3.54\%$. $R=2.23\times10^{-4}$ (true values) vs $2.10\times10^{-4}$ (bounds) per pulse, 445 bit/s at 2 MHz.
- Deviations at $\nu/\mu=0.25$: $\beta_{Y_1}=3.5\%$, $\beta_{e_1}=16.8\%$, as in [S9 §3.6].
- Maximal distance: infinite decoys 142.01 km (paper 142.05), vacuum+weak $\nu=0.05$: 140.62 km (paper 140.55) [S9 Fig. 2]; **without decoys** (GLLP, $\mu$ optimised): 40.2 km.
- PNS at 40 km: honest $Q_\nu=3.27\times10^{-4}$, under PNS $4.64\times10^{-5}$ (7× lower), $Y_1^L=-1.7\times10^{-4}<0$.

**MDI-QKD, LCQ parameters** ($\alpha=0.2$ dB/km, $\eta_d=14.5\%$, $p_d=3\times10^{-6}$ per detector, $e_d=1.5\%$, $f=1.16$ [S10 Fig. 2, S11 Table I], relay in the middle, $\mu$ optimised; `mdi_qkd.demo`):

| $L$ (km) | 0 | 50 | 100 | 150 | 200 |
|---|---|---|---|---|---|
| $\mu^*$ | 0.60 | 0.57 | 0.55 | 0.52 | 0.45 |
| $R$ | $5.8\times10^{-4}$ | $5.3\times10^{-5}$ | $4.9\times10^{-6}$ | $4.2\times10^{-7}$ | $2.2\times10^{-8}$ |

Cutoff 232 km; $R$ drops 10 dB per 50 km, i.e. $\propto\eta_a\eta_b$, the *total* transmittance, same scaling as BB84. [S10] reports tolerating more than 40 dB (200 km) with the relay in the middle, consistent with 232 km here. Decoy BB84 with the same detector numbers ($Y_0=6.02\times10^{-6}$) reaches 160 km in the same code; [S10] speaks of roughly doubling the distance of standard decoy BB84 and notes that the cut-off depends strongly on the dark-count rate. This model gives a factor 1.45 (not resolved here).

## Pitfalls

- Decoy analysis assumes **phase randomisation**; without it the pulses are not Fock mixtures and $Y_n$ are not intensity-independent.
- The bounds in Thm 6.3 are asymptotic (exact $Q_\nu$). Finite statistics need confidence intervals on every gain, and usually two non-vacuum decoys because a perfect vacuum is hard to prepare [S9 §3.3].
- $q=\tfrac12$ in the GYS numbers; efficient BB84 raises it towards 1 and doubles all rates, not the distance.
- MDI still trusts the sources: intensity fluctuations, imperfect phase randomisation, side channels in the modulators remain open. It removes *detector* side channels only.
- HOM interference between independent lasers needs indistinguishable pulses (timing, spectrum, polarisation) [S10]; misalignment enters as $e_d$.
- "Unconditionally secure" QKD systems were broken by detector blinding [S31]; the proof was right, the device model was wrong.

## Questions

1. *Describe the PNS attack and why it limits WCP-BB84 without decoys to $R=O(\eta^2)$.* Def. 3, Prop. 6.1: multi-photon pulses must be a small fraction of detections, $\mu=O(\eta)$.
2. *Why are $Y_n$ and $e_n$ independent of the intensity?* A phase-randomised WCP is a Poisson mixture of Fock states; given $n$, the state is the same for every $\mu$, so Eve's action can depend only on $n$.
3. *Derive $Y_1^L$ for the vacuum+weak protocol.* Thm 6.3.
4. *Explain the MDI-QKD sifting table and why it removes detector attacks.* $\psi^-$ anticorrelates in both bases, $\psi^+$ anticorrelates in $Z$ and correlates in $X$; Bob flips accordingly. Detectors are Charlie's; his announcement is public classical data, the proof treats him as Eve.
5. *Compare BB84, MDI and DI-QKD by what is trusted and by rate.* Trusted sources and detectors / trusted sources only / nothing but quantum theory and isolation of the labs; rates decrease in that order; DI needs loophole-free Bell tests [S28-S30].

## Code

`src/py/decoy.py`: `Channel` (GYS), `vacuum_weak_bounds`, `two_decoy_bounds`, `rate_decoy`, `rate_gllp_no_decoy`, `best_mu`, `max_distance`, `mu_optimal_small_eta`, `relative_deviations`, `pns_attack_gains`. `src/py/mdi_qkd.py`: `single_photon_bsm` (two-photon Fock model with loss and dark counts), `y11_e11`, `coherent_bsm`, `gain_qber` (phase-averaged WCPs), closed forms `mr_y11`, `mr_e11`, `mr_rect`, `mr_diag`, `key_rate`, `rate_curve`. Tests reproduce [S9] distances and deviations and check the first-principles MDI models against [S11] to $10^{-9}$.

## References

[S8], [S9 Eqs. (1)-(12), (18)-(37), Table 1, Fig. 2], [S10 Eq. (1), Table I, Fig. 2], [S11 App. A-B], [S15], [S17], [S18], [S28], [S29], [S30], [S31], [S32], [S34].
