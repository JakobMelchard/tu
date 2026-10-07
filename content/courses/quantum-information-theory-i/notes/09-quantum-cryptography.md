# 09 Quantum cryptography: BB84 and Ekert 91 (TISS 2.4)

TISS 2.4: "BB84 protocol and Ekert 91 protocol" [S2]. At TISS depth: the two protocols, why eavesdropping is detectable (no-cloning, information-disturbance, CHSH monogamy), the intercept-resend numbers, and the equivalence of the prepare-and-measure and entanglement-based pictures. Full security proofs, finite-key analysis and implementations belong to the sibling course 141.320 Quantum Communication and Security ([README](../../quantum-communication-and-security/index.md); Mon 13:00-16:00, same Seminarraum ZE 01-1), which runs in the same semester. Sources: Jozsa §5 [S10]; Preskill ch. 4 §4.5.1 (EPR key distribution), §4.5.2 [S8] and 1998 §4.2.2 [S5]; primary Bennett-Brassard 1984 [S30], Ekert 1991 [S31], Bennett-Brassard-Mermin 1992 [S32], Shor-Preskill 2000 [S63]. **Toy crypto:** `protocols.py` simulates statistics; it is not an implementation.

## Setting

Alice and Bob share an insecure quantum channel and an *authenticated* classical channel (public, not modifiable: authentication needs a short pre-shared key, so QKD is key *expansion*). Goal: a shared uniformly random key about which Eve knows (almost) nothing. The information-theoretic guarantee comes from physics, not from computational hardness.

## BB84 [S30]

1. Alice picks random bits $x_i$ and bases $y_i\in\{Z,X\}$, sends $|0\rangle,|1\rangle$ (basis $Z$) or $|{+}\rangle,|{-}\rangle$ (basis $X$).
2. Bob measures each qubit in a random basis $y'_i$, gets $x'_i$.
3. **Sifting:** they publish bases (not bits), keep positions with $y_i=y'_i$: expected fraction $\tfrac12$.
4. **Parameter estimation:** publish a random sample of sifted bits, estimate the quantum bit error rate (QBER) $Q$; abort if too high.
5. **Error correction** (information reconciliation) and **privacy amplification** (universal hashing to a shorter key) over the public channel [S10 §5, steps 4-5].

**Why eavesdropping shows.** The four states form two mutually unbiased bases. Any measurement that gains information about which of two *non-orthogonal* states was sent disturbs them (information-disturbance): if $U|\psi\rangle|e\rangle=|\psi\rangle|e_\psi\rangle$ and $U|\phi\rangle|e\rangle=|\phi\rangle|e_\phi\rangle$ with $\langle\psi|\phi\rangle\ne0$, unitarity gives $\langle\psi|\phi\rangle=\langle\psi|\phi\rangle\langle e_\psi|e_\phi\rangle$, so $\langle e_\psi|e_\phi\rangle=1$: an undisturbing probe learns nothing. Same algebra as no-cloning ([13](13-no-cloning-and-state-discrimination.md)). Eve cannot copy and keep, and she does not know the basis until after transmission.

**Intercept-resend attack, computed.** Eve measures in a random basis and resends her result. On a sifted position: with probability $\tfrac12$ she guessed the basis, no error; with $\tfrac12$ she used the wrong one, her resent state is unbiased in Bob's basis, error $\tfrac12$. So
$$Q=\tfrac12\cdot0+\tfrac12\cdot\tfrac12=\tfrac14,$$
while Eve knows each sifted bit with probability $\tfrac34$ (mutual information $\tfrac12$ bit). Attacking a fraction $f$ of the qubits gives $Q=f/4$. `bb84(20000, rng, eve=True)` reproduces $Q\approx0.25$ (0.256 in the demo), sifted fraction $\approx0.5$.

**Security threshold.** With one-way error correction and privacy amplification the asymptotic key rate against *all* attacks is $r=1-2h(Q)$, $h$ the binary entropy (Shor-Preskill [S63], via entanglement distillation and CSS codes); $r>0$ for $Q\lesssim11\%$ ("less than about 11%" [S10 §5]). Intercept-resend at full strength ($25\%$) is far above it.

## Ekert 91 [S31]

Source emits singlets $|\Psi^-\rangle$, one half to each party. Spin observables $\cos\theta\,Z+\sin\theta\,X$ in the $xz$-plane with $E(\theta_a,\theta_b)=-\cos(\theta_a-\theta_b)$. Ekert's angles: Alice $\{0,\tfrac\pi4,\tfrac\pi2\}$, Bob $\{\tfrac\pi4,\tfrac\pi2,\tfrac{3\pi}4\}$, each chosen uniformly.
- **Key:** the two coinciding pairs $(\tfrac\pi4,\tfrac\pi4)$ and $(\tfrac\pi2,\tfrac\pi2)$ (probability $\tfrac29$) give perfectly anticorrelated outcomes; Bob flips his bit.
- **Test:** four of the remaining pairs give
$$S=E(a_1,b_1)-E(a_1,b_3)+E(a_3,b_1)+E(a_3,b_3)=-\tfrac1{\sqrt2}-\tfrac1{\sqrt2}-\tfrac1{\sqrt2}-\tfrac1{\sqrt2}=-2\sqrt2 .$$
- **Security intuition (monogamy):** $|S|=2\sqrt2$ is only attained by a state local-unitarily equivalent to the singlet (self-testing, the SOS form in [06](06-non-locality-and-bell-inequalities.md)), which is pure, so any third party is in a product state with it. If Eve intercepts and resends in $Z$, Alice and Bob share a separable state; its CHSH value obeys the local bound, here exactly $|S|=\sqrt2$ (`e91_exact(intercept_resend_z(...))`). The Bell test replaces BB84's error-rate check.

**BBM92 [S32]: E91 = entanglement-based BB84.** If Alice measures her half of $|\Phi^+\rangle$ in $Z$ or $X$, Bob's half collapses to the BB84 state she "sent" (steering, [04](04-schmidt-decomposition-and-purification.md)); the statistics are identical to prepare-and-measure BB84, so trusted-device security needs no Bell inequality. What E91 adds conceptually is **device independence**: a CHSH violation certifies the correlations without trusting the measurement devices (modern DI-QKD, beyond this course).

## Worked example

200 sifted BB84 bits with QBER sample of 100: observing 24 errors ($Q=0.24$) is consistent with a full intercept-resend and far above 11%: abort. Observing 2 errors ($Q=0.02$): $r=1-2h(0.02)=1-2(0.1414)=0.717$ key bits per sifted bit asymptotically. E91 sampled over 9000 rounds (`e91_sampled`): $\hat S=-2.83$, key error rate 0, about 2000 key bits ($\tfrac29$ of rounds).

## Pitfalls

- The classical channel must be authenticated; without it a man-in-the-middle breaks any QKD.
- QBER from intercept-resend is $25\%$ only if Eve attacks every qubit and guesses bases uniformly; partial attacks scale linearly.
- "Security from no-cloning" is intuition; actual proofs bound Eve's information via entropic uncertainty or entanglement distillation [S63].
- In E91 the key pairs are those with *equal* angles; with singlets the bits are anti-correlated, not equal.
- Photon-number splitting and detector attacks are implementation issues (decoy states, MDI-QKD): sibling course.

## Oral-exam questions (model answers)

1. *Describe BB84 and compute the QBER of an intercept-resend attack.* Steps 1-5; wrong basis w.p. $\tfrac12$, then error w.p. $\tfrac12$: $Q=\tfrac14$.
2. *Why can Eve not learn the key without disturbing it?* Information-disturbance lemma for non-orthogonal states (unitarity, as in no-cloning); unknown basis.
3. *Describe E91 and the role of the CHSH test.* Singlets, Ekert's angles, key from equal angles, $S=-2\sqrt2$; monogamy: maximal violation leaves no room for Eve; resend in $Z$ gives $|S|=\sqrt2$.
4. *How are BB84 and E91 related?* BBM92: entanglement-based version of BB84 with identical statistics; E91's Bell test enables device independence.
5. *What error rate can BB84 tolerate and why is there a threshold?* $1-2h(Q)>0$, $Q<11\%$ (Shor-Preskill): error correction costs $h(Q)$, privacy amplification against Eve's information another $h(Q)$.

## Code

`src/py/protocols.py`: `bb84(n, rng, eve=)` (sifted fraction, QBER), `e91_exact(rho)` ($S$ and key-pair correlators), `e91_sampled(rho, n, rng)`, `intercept_resend_z`. Tests `test_protocols.py`: sifting $0.5\pm0.02$, QBER 0 without Eve and $0.25\pm0.02$ with, exact $S=-2\sqrt2$ and key correlators $-1$, $|S|\le2$ after the intercept, sampled $\hat S$ within 0.25 of $-2\sqrt2$ with zero key errors.
