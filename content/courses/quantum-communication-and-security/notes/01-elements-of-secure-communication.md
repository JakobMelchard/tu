# 01 Elements of secure communication

First TISS topic [S2]. What "secure" means before any quantum mechanics enters: the one-time pad is perfectly secret, Shannon's bound says it needs as much key as message, public discussion alone cannot create that key, and a composable (trace-distance) definition is what makes a QKD key usable inside a larger protocol. Everything later in the course proves that a QKD protocol meets the definition of §5.

## Definitions

1. **Symmetric encryption scheme.** Key space $\mathcal K$, message space $\mathcal M$, ciphertext space $\mathcal C$; $\mathrm{Enc}:\mathcal K\times\mathcal M\to\mathcal C$, $\mathrm{Dec}:\mathcal K\times\mathcal C\to\mathcal M$ with $\mathrm{Dec}_k(\mathrm{Enc}_k(m))=m$. Key $K$ uniform and independent of the message $M$.
2. **One-time pad (OTP).** $\mathcal K=\mathcal M=\mathcal C=\{0,1\}^n$, $c=m\oplus k$, $m=c\oplus k$.
3. **Perfect secrecy (Shannon)** [S16]. $P(M=m\mid C=c)=P(M=m)$ for all $m,c$ with $P(C=c)>0$; equivalently $I(M:C)=0$.
4. **Information-theoretic vs computational security.** Information-theoretic: holds against an adversary with unbounded computation. Computational: holds only if some problem (factoring, discrete log) is hard; RSA and Diffie-Hellman fall to Shor's algorithm [S3 §I.A].
5. **Authenticated classical channel.** Eve reads everything but cannot alter or inject messages undetected. QKD *assumes* it; in practice it is implemented with Wegman-Carter authentication from a short pre-shared key, part of each round's key being kept for the next round's authentication [S23, S3 §II.B-C], so QKD is **key expansion**, not key creation from nothing.
6. **Trace distance.** $D(\rho,\sigma)=\tfrac12\|\rho-\sigma\|_1$. Operationally $\tfrac12(1+D)$ is the optimal probability of telling $\rho$ from $\sigma$ given one copy with prior $\tfrac12$ (Helstrom; sibling course, see §Links).
7. **$\varepsilon$-secure key** [S4 Eq. (2.6)]. For a cq state $\rho_{KE}=\sum_kP_K(k)|k\rangle\langle k|\otimes\rho_E^k$ on $\{0,1\}^\ell$,
   $$\tfrac12\bigl\|\rho_{KE}-\tau_K\otimes\rho_E\bigr\|_1\le\varepsilon,\qquad\tau_K=2^{-\ell}\mathbb 1.$$
8. **Correctness, secrecy, security of a QKD protocol** [S5 §4 Lemma 1, S24]. Let $F$ flag "not aborted".
   $\varepsilon_{\rm cor}$-correct: $\Pr[K_A\ne K_B\wedge F]\le\varepsilon_{\rm cor}$.
   $\varepsilon_{\rm sec}$-secret: $\tfrac12\|\rho_{K_AE\wedge F}-\tau_{K_A}\otimes\rho_{E\wedge F}\|_1\le\varepsilon_{\rm sec}$ (subnormalised by $\Pr[F]$, so an aborting protocol is trivially secret).
   Then the protocol is $(\varepsilon_{\rm cor}+\varepsilon_{\rm sec})$-secure: its output is that close in diamond norm to an ideal protocol which, when it does not abort, outputs a uniform key $K_A=K_B$ independent of $E$ [S5 Eq. (47)-(55)].

## Results

**Theorem 1.1 (OTP is perfectly secret).** If $K$ is uniform on $\{0,1\}^n$ and independent of $M$, then $C=M\oplus K$ is uniform and independent of $M$.

*Proof.* $P(C=c\mid M=m)=P(K=c\oplus m)=2^{-n}$ for every $m$, so $C$ is independent of $M$. ∎

**Theorem 1.2 (Shannon's key bound)** [S16, S3 §I.A]. Perfect secrecy with a correct decryption implies $H(K)\ge H(M)$.

*Proof.* Correctness: $H(M\mid K,C)=0$. Secrecy: $H(M)=H(M\mid C)$. Then
$$H(M)=H(M\mid C)\le H(M,K\mid C)=H(K\mid C)+H(M\mid K,C)=H(K\mid C)\le H(K).\ ∎$$

So an $n$-bit message needs $n$ bits of fresh key; reusing a pad leaks $c_1\oplus c_2=m_1\oplus m_2$.

**Theorem 1.3 (no key from public discussion alone).** Alice and Bob with independent private randomness $R_A,R_B$ exchange a public transcript $T$ and output $K_A=f(R_A,T)$, $K_B=g(R_B,T)$. If $\Pr[K_A=K_B]=1$ then $H(K_A\mid T)=0$.

*Proof.* Each message is a function of the sender's randomness and the messages so far, so $P(r_A,r_B,t)=P(r_A)P(r_B)\,\alpha(r_A,t)\beta(r_B,t)$ with $\alpha,\beta\in\{0,1\}$. Hence conditioned on $T=t$ the pair factorises: $R_A$ and $R_B$ are independent given $T$, and so are $K_A,K_B$. Two independent random variables that are equal with probability 1 are both constant, so $K_A$ is a function of $t$. ∎

This is the **key distribution problem**. Classical cryptography escapes it only computationally (public-key exchange). QKD replaces "hard problem" by "physics": Eve cannot copy or measure unknown non-orthogonal states without disturbing them, and the disturbance is measured [S3 §I.B].

**Proposition 1.4 (meaning of the trace distance).** If $\frac12\|\rho_{KE}-\tau_K\otimes\rho_E\|_1\le\varepsilon$, then there is a coupling in which the real and ideal worlds coincide except with probability $\varepsilon$, and any later process (including using $K$ as an OTP key) increases the distance by nothing, since CPTP maps contract $\|\cdot\|_1$ [S4 §2.2, Lemma A.2.1]. Errors of composed protocols add: $n$ keys each $\varepsilon$-secure used together are $n\varepsilon$-secure [S24].

**Why not mutual information.** "Eve's accessible information about $K$ is small" is not composable: quantum side information can be *locked*, so a key with tiny accessible information can become insecure once part of it is used [S4 §2.2, S3 §II.C]. The trace-distance criterion implies small accessible information, not conversely [S4 §2.2].

## Worked example

**OTP with an $\varepsilon$-secure key.** QKD gives $\ell=10^6$ bits with $\varepsilon=10^{-10}$ (the value used in [S5 Fig. 7]). Encrypt a $10^6$-bit message. By Prop. 1.4, Eve's view of $(C,E)$ is $10^{-10}$-close to the view with a perfect key, where $C$ is independent of $M$ by Thm 1.1. So for every event about $M$ Eve could test, her success probability exceeds the prior by at most $10^{-10}$. Encrypting 1000 messages with 1000 such keys: $10^{-7}$ total.

**Shannon bound in numbers.** A 1 Gbit/s link encrypted with OTP needs 1 Gbit/s of key. The decoy-BB84 rate at 50 km with the GYS parameters is $2.2\times10^{-4}$ bits per pulse (note 06), i.e. about 445 bit/s at the 2 MHz clock of [S9 Table 1]. OTP-encrypting bulk data with QKD key is therefore out of reach at fibre distances; the key goes into authentication tags and short, high-value messages, or into a computationally secure cipher (which gives up information-theoretic security).

**Security budget.** $\varepsilon_{\rm cor}=2^{-t}$ with a $t=37$-bit verification hash is $7.3\times10^{-12}$; with $\varepsilon_{\rm pe}=6\times10^{-11}$ and $\varepsilon_{\rm pa}\le3\times10^{-11}$ the protocol is $10^{-10}$-secure (numbers from `finite_key_length`, note 05).

## Pitfalls

- Perfect secrecy is about the ciphertext alone; it says nothing about **integrity**. OTP ciphertexts are malleable ($c\oplus\delta$ decrypts to $m\oplus\delta$).
- "Unconditional security" still has conditions: correct quantum mechanics, trusted labs (no leakage out of Alice's and Bob's devices), an authenticated classical channel, true randomness, and a device model that matches the hardware (note 06).
- $\varepsilon$ is a *distinguishing* probability for the whole protocol, not "the probability Eve knows a bit". $\ell\varepsilon$ is not the right scaling.
- Secrecy is conditioned on not aborting: the definition multiplies by $\Pr[F]$. A protocol that almost always aborts is secure and useless (robustness is a separate requirement [S5 §5]).
- QKD without an initial authentication key is open to man-in-the-middle; the authentication key is consumed, so compare net key output with key spent.

## Questions

1. *State perfect secrecy and prove that the OTP achieves it.* $P(M|C)=P(M)$; $P(C=c|M=m)=P(K=c\oplus m)=2^{-n}$, independent of $m$.
2. *Why can a pad not be reused?* $c_1\oplus c_2=m_1\oplus m_2$ is independent of the key and reveals the XOR of the plaintexts; formally two messages need $H(K)\ge H(M_1M_2)$ by Thm 1.2.
3. *Prove $H(K)\ge H(M)$ for a perfectly secret scheme.* Chain in Thm 1.2: $H(M)=H(M|C)\le H(MK|C)=H(K|C)+H(M|KC)=H(K|C)\le H(K)$.
4. *Write the composable security definition of QKD and explain each term.* Items 7-8: correctness bounds disagreement on non-abort; secrecy is trace distance of the subnormalised $\rho_{K_AE\wedge F}$ from uniform-times-marginal; the sum bounds the diamond distance to the ideal protocol; errors add under composition.
5. *Why is "small mutual information with Eve" an insufficient criterion?* Not composable: quantum side information can be locked, accessible information can jump once part of the key is revealed; the trace distance bounds every future distinguishing experiment by contractivity.

## Links

Trace distance, fidelity and state discrimination are treated in the sibling course 141.282, topic 1.5: [`05-hilbert-space-geometry.md`](../../quantum-information-theory-i/notes/05-hilbert-space-geometry.md) (sibling notes written concurrently on 2026-09-28; file names may change).

## Code

No module; the numbers above come from `src/py/key_rates.py` (`finite_key_length`, `finite_key_errors`) and `src/py/decoy.py` (`rate_decoy`).

## References

[S3 §I.A-B, §II.B-C], [S4 §2.2], [S5 §4], [S16], [S23], [S24]. Register: [`../refs/SOURCES.md`](../refs/SOURCES.md).
