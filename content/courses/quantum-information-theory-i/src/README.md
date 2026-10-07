# Reference implementations

Python only: the course is theory (VO, oral exam), so the code exists to make every formula in the notes executable and checkable. Pure numpy/scipy, small dimensions (qubits, qutrits, at most 3 qubits or $3\times3$), every random draw seeded, no network, no data files. Each module runs as a script whose demo prints the note's worked numbers; each has a `test_<module>.py`.

From the course folder, with the repo's Python environment:

```
python -m pytest src -q          # 93 tests, ~1.5 s
python src/py/bell.py            # any module's demo
for m in states entropies schmidt distances bell protocols entanglement channels cloning; do python src/py/$m.py; done
```

Modules import each other by bare name (`from states import ...`); pytest's default rootdir-based `sys.path` insertion handles that. Run this directory on its own: module names such as `protocols` may also exist in sibling courses, and collecting several `src/py` folders in one pytest process would make them collide.

Convention: subsystem 0 is the leftmost tensor factor (`np.kron` order), as in the ws2026 quantum-computing notes; fidelity is the squared one, $F=\|\sqrt\rho\sqrt\sigma\|_1^2$.

| Module | Note | Implements | Demo shows | Test anchors |
|---|---|---|---|---|
| `py/states.py` | 01, 02 | `dm`, `is_state`, `purity`, `linear_entropy`, Bloch vector and inverse, `gell_mann(d)`, generalised Bloch, `two_qubit_decomposition`, `bipartite_bloch`, `partial_trace` over any subset, Haar `random_pure`/`random_unitary`, HS `random_state`, `BELL` | purity $(1+r^2)/2$, singlet $T=-I$, qutrit $\lvert b\rvert^2=2(\operatorname{tr}\rho^2-1/3)$ | Gell-Mann orthonormality $d=2..5$; partial trace vs explicit sum and 3-party products; $2\times3$ Bloch round trip, marginals, purity formula; $T=\vec a\vec b^T$ for products |
| `py/entropies.py` | 03 | `shannon`, `von_neumann`, `relative_entropy` (inf off-support), `conditional_entropy`, `mutual_information`, `conditional_mutual_information`, `check_inequalities`, `check_ssa` | Bell $S(A\vert B)=-1$, $I=2$; worst slack of Klein, subadditivity, Araki-Lieb, concavity, SSA over random states | $D(\rho\Vert I/d)=\log d-S$; Araki-Lieb and SSA saturation cases; $I=D(\rho_{AB}\Vert\rho_A\otimes\rho_B)$ |
| `py/schmidt.py` | 04 | `schmidt` (SVD), `schmidt_rank`, `reconstruct`, `purify`, `canonical_purification`, `purification_unitary` | $2\times3$ Schmidt coefficients vs spectrum of $\rho_A$; two purifications related by $U_R$ | coefficients equal `np.linalg.svd`; reduced spectra on both sides; ranks 1-3 |
| `py/distances.py` | 05 | `trace_distance`, `trace_distance_by_projector`, `fidelity`, `root_fidelity`, `bures_distance`, `bures_angle`, `uhlmann_optimal_unitary`, `uhlmann_overlap`, `check_fuchs_van_de_graaf` | Uhlmann max attained, 2000 random $U$ below it; FvdG and Pinsker slack | Bhattacharyya for commuting states; qubit formula $\tfrac12(1+\vec r\cdot\vec s+\sqrt{(1-r^2)(1-s^2)})$; monotonicity under partial trace |
| `py/bell.py` | 06, 07 | `chsh_operator`, `chsh_value`, `local_bound`, `tsirelson_identity_error`, `max_chsh_numeric`, `horodecki_max_chsh`, `werner`, `PERES_MERMIN`, `square_contexts`, `pentagram`, `noncontextual_assignments`, `CABELLO_BASES`, `cabello_check`, `hemisphere_value` | $2\sqrt2$; Werner $p=0.5,1/\sqrt2,0.9$; square/pentagram signs; Cabello: 0 colourings of $4^9$ | Gisin $2\sqrt{1+\sin^22\theta}$; numeric = Horodecki; exhaustive 0 assignments |
| `py/protocols.py` | 08, 09 | `teleport`, `teleport_with_resource`, `entanglement_swapping`, `dense_coding`, `bb84`, `e91_exact`, `e91_sampled`, `intercept_resend_z`. **Toy crypto**, statistics only | all four branches exact; noisy fidelity 0.75 at $p=0.5$; BB84 QBER 0 and 0.256; E91 $S=-2\sqrt2$, $-\sqrt2$ after intercept | $(1+p)/2$ for $p\in\{0,\tfrac13,\tfrac12,1\}$; QBER $0.25\pm0.02$; sampled $\hat S$ |
| `py/entanglement.py` | 10 | `partial_transpose`, `is_ppt`, `negativity`, `log_negativity`, `entropy_of_entanglement`, `concurrence`, `werner`, `WERNER_WITNESS`, `witness_value`, `random_separable`, `realignment`, `horodecki_3x3` | Werner table (PPT, $N$, $C$, witness, $I$); witness $\ge0$ on 2000 product states; Horodecki $3\times3$ | thresholds at $p=\tfrac13$; PPT $\iff C=0$ on 300 random two-qubit states; realignment $\le1$ on separable $3\times3$ |
| `py/channels.py` | 11, 12 | `depolarising`, `dephasing`, `amplitude_damping`, `apply_kraus`, `choi`, `is_cptp_choi`, `kraus_from_choi`, `transpose_map`, `stinespring`, `stinespring_apply`, `is_povm`, `born`, `trine`, `neumark_isometry`, `neumark_direct_sum` | Bloch actions; transpose Choi eigenvalue $-1$; Neumark both ways on the trine | Kraus unitary freedom; complement of amplitude damping $\gamma$ is $1-\gamma$ |
| `py/cloning.py` | 13 | `cnot_clone_fidelity`, `buzek_hillery`, `bh_output`, `sym_projector`, `symmetric_cloner`, `single_copy_fidelity`, `cnot_broadcast_marginals`, `helstrom`, `helstrom_pure`, `usd_povm`, `usd_success` | BH fidelity $0.833333$ on 200 inputs; $1\to M$: $5/6,7/9,3/4$; Helstrom $0.6947$, USD $0.0789$ | reduced state $\tfrac23\psi+\tfrac13\tfrac I2$; Helstrom beats 300 random projectors; USD error 0 |

Not implemented: an SDP proving optimality of the $5/6$ cloner or of the IDP measurement (no SDP solver in the venv; both are cited, [S51, S52, S58]).
