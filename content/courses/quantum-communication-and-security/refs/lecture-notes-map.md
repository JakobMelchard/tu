# Topic map: TISS topics → sources → notes → code

**No lecture notes are public.** TISS says lecture notes and exercises are "provided in advance" [S1], i.e. inside the course; none were seen. This map therefore lays the six TISS topics [S2] onto the standard sources and onto our notes and code. When the real lecture notes arrive, add a column for their chapters.

## Topic map

| # | TISS topic [S2] | best source sections | our note | code |
|---|---|---|---|---|
| 1 | Elements of secure communication | S16; S3 §I.A-B, §II.B-C; S4 §2.2; S5 §4; S24 | [01](../notes/01-elements-of-secure-communication.md) | (numbers from `key_rates.py`) |
| 2 | The BB84 protocol | S6; S3 §I.B, §II.B; S5 §3; S37 | [02](../notes/02-bb84.md) | `bb84.py` |
| 3 | Theoretical tools (mixed states, probability and information theory, conditional entropies) | S4 ch. 3; S5 §2, Eqs. (12)-(19), Prop. 4; S20; S21; S13 | [03](../notes/03-theoretical-tools.md) | `entropies.py` |
| 4 | Information reconciliation and privacy amplification | S3 §III.B; S4 ch. 5; S5 §3.2, §6.1, §6.4; S12; S22; S23; S39 | [04](../notes/04-reconciliation-and-privacy-amplification.md) | `reconciliation.py`, `privacy_amplification.py` |
| 5 | Security proofs against collective and coherent attacks | S7; S14; S4 ch. 4, 6, §7.1; S19; S25; S26; S5 §5-6; S27 | [05](../notes/05-security-proofs.md) | `key_rates.py`, `entropies.py` |
| 6 | Dealing with imperfections (decoy state method and MDI-QKD) | S18; S15; S17; S8; S9; S10; S11; S31; S28-S30; S32 | [06](../notes/06-imperfections-decoy-and-mdi.md) | `decoy.py`, `mdi_qkd.py` |

## Learning outcomes → where they are practised

| learning outcome [S2] | notes | code that computes it |
|---|---|---|
| Describe the steps of a QKD protocol | 02, 04 | `bb84.simulate`, `reconciliation.cascade`, `privacy_amplification.toeplitz_hash` |
| Compute asymptotic key rates; apply entropic relations | 03, 05, 06 | `key_rates.shor_preskill`, `devetak_winter_bb84_min`, `decoy.rate_decoy`, `mdi_qkd.key_rate` |
| Explain techniques and theorems in a security proof | 01, 04, 05 | `privacy_amplification.lhl_bound`, `key_rates.finite_key_length` |
| Identify assumptions and weaknesses | 01, 02, 06 | `decoy.pns_attack_gains`, `decoy.rate_gllp_no_decoy` |

## Overlap with 141.282 Quantum Information Theory I (same semester)

The sibling course [`../../quantum-information-theory-i`](../../quantum-information-theory-i/index.md) covers, per its TISS topic list: pure and mixed states, partial trace (1.1-1.2), Shannon and von Neumann entropy, subadditivity, relative entropy (1.3), Schmidt decomposition and purification (1.4), fidelity, Uhlmann, trace distance (1.5), BB84 and E91 (2.4), CPTP maps, Kraus, Stinespring (2.6), POVMs (2.7), no-cloning and state discrimination (2.8). Note 03 assumes these and adds only the one-shot entropies and the uncertainty relation; read the sibling's notes for the rest.

## The lecturer's research, as a hint for emphasis

Glaucia Murta's recent arXiv work [S32, S33, S34]: security proofs with imperfections (2026 review), conference key agreement (2020 review), device-independent QKD (realisation requirements, 2019). Expect topic 6 and the DI outlook to be taught with care; conference key agreement is not on the TISS list.
