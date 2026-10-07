# 00 Exam focus: the 2026W plan and what is actually asked

Built from four past papers and two sample solution sets (read on 2026-09-22)
and the 2026W TISS page and API record (re-read on 2026-10-07,
[`../docs/tiss.md`](../docs/tiss.md), `../docs/tiss-api.md`).
Read this before deciding how much time to give a topic.

> Every date below is this semester's (2026W). TUWEL (course 84457) is where
> sheets are ticked and uploaded.


## The 2026W rules

From the TISS page and API record, both as of 2026-10-07 [S1]:

- **9 exercise sheets.** Before each Thursday session you tick on TUWEL the
  problems you solved and upload your solutions; volunteers present.
- **Uploads are graded.** A missing, incomplete, copied or clearly
  AI-generated solution gives the **whole sheet 0 points**; a **second** such
  case gives a **negative course grade**. Practical rule: tick and upload only
  what you can hand in complete and in your own words. Do not hand in text from
  these notes or from any AI tool.
- **Hurdle: half of the exercise points are needed to sit an exam.** Every
  sheet counts towards it, and if the 9 sheets weigh the same, one zeroed sheet
  costs about 11 % of the total.
- **Grade: 20 % exercises + 40 % midterm + 40 % final.** The mean of the two
  partial exams must be positive. One of the two may be retaken on 26.02.2027.
- Presence is not mandatory; lectures and exercise sessions are recorded.
- Closed book, judging by M25 [S7]; nothing in the 2026W record says otherwise.

| what | when | where | apply in TISS |
|---|---|---|---|
| Lecture | Thu 12:00-14:00, 01.10.2026 to 21.01.2027 (15 dates, none on 24.12 and 31.12) | FAV Hörsaal 1 | n/a |
| Exercise session | Thu 15:00-18:00, 08.10.2026 to 21.01.2027 (13 dates, none on 14.01.2027) | EI 5 Hochenegg HS | n/a |
| **Midterm** | **Wed 18.11.2026, 12:00-14:00** | GM 1 Audimax | 23.10.2026 to 18.11.2026 00:00 |
| **Final** | **Fri 29.01.2027, 10:00-12:00** | GM 1 Audimax | 03.12.2026 to 29.01.2027 00:00 |
| Retake (midterm or final, one of them) | Fri 26.02.2027, 12:00-14:00 | GM 1 Audimax | 05.02.2027 to 26.02.2027 00:00 |

Exam registration is separate from course registration: open the midterm
application on or after 23.10.2026 and do not leave it to the evening of
17.11, since the window closes at 00:00 on the exam day.

## The 2026W plan

**What each exam covers.** TISS does not say. The working assumption: the
midterm covers the lectures before it, the final the rest, as in 2025W, where
the 3 December midterm covered lectures 1-8 [S13]. Seven lectures fall before
18.11.2026 (01.10 to 12.11). If 2026W follows the 2024W slide order [S8] one
lecture per week, that is lectures 1-7, i.e. up to modes of operation and CCA,
and lecture 8 (MACs, AE) lands on 19.11, the day after. The 2026W order is not
published, so check each week which deck was actually given and move the
boundary with it. Whether the final also re-examines the first half is not
stated either; plan for the second half and keep the first-half true/false
material warm.

| lecture (2024W order) | date if one per week | note | exam |
|---|---|---|---|
| 1 historical ciphers | 01.10 | [01](01-historical-ciphers.md) | midterm |
| 2 perfect secrecy | 08.10 | [02](02-perfect-secrecy.md) | midterm |
| 3 block ciphers | 15.10 | [03](03-block-ciphers.md) | midterm |
| 4 computational security | 22.10 | [04](04-computational-security.md) | midterm |
| 5 pseudorandomness | 29.10 | [05](05-pseudorandomness.md) | midterm |
| 6 PRFs, CPA encryption | 05.11 | [06](06-private-key-encryption.md) | midterm |
| 7 modes, CCA | 12.11 | [06](06-private-key-encryption.md) | midterm |
| 8 MACs, AE, sessions | 19.11 | [07](07-macs-and-ae.md) | final (midterm only if given earlier) |
| 9 hash functions | 26.11 | [08](08-hash-functions.md) | final |
| 10 number theory | 03.12 | [09](09-number-theory.md) | final |
| 11 DLog, public-key crypto | 10.12 | [09](09-number-theory.md), [10](10-key-exchange-pke.md) | final |
| 12 DHIES, RSA, signatures | 17.12 | [10](10-key-exchange-pke.md), [11](11-digital-signatures.md) | final |
| 13 RSA-FDH, Schnorr, DSA, PKI | 07.01 | [11](11-digital-signatures.md), [12](12-tls-and-pki.md) | final |
| 13a TLS, outro | 14.01 | [12](12-tls-and-pki.md) | final |
| (spare date) | 21.01 | | |

Fifteen lecture dates for fourteen decks, so there is one date of slack; any
shift moves the rows above.

**Midterm, Wed 18.11.2026** (30 points if it matches M25). Notes 01-06 plus
note 13 problems 1 and 2 and its attack procedure. From the past papers:

- the true/false items below that point to notes 01-06 (most of the
  definitions, block-cipher and asymptotics clusters; the MAC, hash and algebra
  items belong to the final);
- reconstruct the EAV/CPA/CCA game clause by clause (M25 q2, F23 q2a; note 06
  Q1-Q2);
- an explicit attack on a contrived private-key scheme (M25 q3b, F20 1a, F20
  3a; note 03 Q5, note 06 Q4-Q5);
- a reduction to a PRG or PRF (note 04 worked example, note 05 worked example,
  note 13 problem 1); if MACs are in, M25 q4 (note 07 Q1) and M25 q5 (note 07
  Q2).

Two-week run-in: work through M25 under exam conditions around 04.11, redo the
weak spots, and do it again from a blank page on 16.11.

**Final, Fri 29.01.2027.** Notes 07-12 plus note 13 problems 3 and 5; note 09's
by-hand modular arithmetic; the public-key true/false clusters below. F24 and
F23 are the models, but both are whole-course finals from before the
midterm existed, so their first-half items are midterm material in 2026W.
Christmas (no lectures 24.12 and 31.12) is the time to do F24 and F23 in full.

**Retake, Fri 26.02.2027.** One partial exam only. Since the mean of the two
partials must be positive, a weak midterm can be repaired here, but only if the
final went well enough; do not plan on it.

**Exercise hurdle.** Half the points over 9 sheets. Six exercise sessions fall
before the midterm (08.10 to 12.11) and seven after; TISS does not say whether
the hurdle is checked against the sheets so far at each exam or against all
nine. Treat it as a running requirement: reach half on every sheet up to
12.11, so the midterm cannot be blocked.

## The papers

| ref | paper | term | date | points | source |
|---|---|---|---|---|---|
| **M25** | Midterm, **with the official answers to part 1** | 2025W | 03.12.2025 | 30 | [S13] |
| **F24** | Final | 2024W | 31.01.2025 | 40 | [S16] |
| **F23** | Final | 2023W | 26.01.2024 | 40 | [S12] |
| **F20** | Final (then a 3 ECTS VO) | 2020W | 02.02.2021 | — | [S15] |

All four papers are Fuchsbauer's, and he teaches every offering from 2023W to
2026W [S1-S4], so the style is a good model for this term's exams.
Nothing else of his is public: his homepage links only
to TISS and hosts no slides, notes or past papers for this course [S9], and the
same is true of Andreeva's [S11]. These four papers plus the two student slide
uploads are the whole public record. Three caveats, all important:

1. **M25 is the only midterm that exists.** Midterms were introduced in 2025W;
   before that there was a single final [S3, S5]. Any midterm has a sample of
   exactly one to learn from. The 2026W midterm sits **two weeks earlier in
   the term** than M25 did (18.11.2026 against 3 December), so expect it to
   stop at lecture 7 rather than 8 (see the plan above).
2. **F20 is from the old 3 ECTS VO** [S6]. Same lecturer, same book, no exercise
   component; treat its questions as topically right and weight-wise irrelevant.
3. **Only M25's part 1 has an official answer key.** Every other answer below is
   ours. Where we disagree with something, we say so.

## Format

- **±1 per true/false item, with a floor of 0** on the section (M25 says
  "minimum 0, maximum 10"; F23 says "minimum 0 points"). A pure 50/50 guess
  has expectation zero, and because of the floor never negative expectation;
  any edge above 50 % makes it positive. Leave an item blank only if you think
  you are more likely wrong than right.
- **10 to 12 true/false items** worth 10-12 of the 30-40 points: a quarter to a
  third of the paper, and the cheapest points on it.
- Then **four to six multi-part questions**, each 2-6 points, of three kinds:
  *state a definition*, *give a reduction*, *give an explicit attack*.
- M25 was **"closed book"** [S7]. Nothing in the 2026W record suggests otherwise.
- **Grading changed for 2026W.** Up to 2025W it was 50 % exercises + 50 % exams,
  the VoWi formula `%G = 0.5*%E + 0.5*%U` [S5]. 2026W is **20 % exercises +
  40 % midterm + 40 % final** with the half-the-exercise-points hurdle (rules
  above), so the exams now carry 80 % of the grade.

## What the true/false sections actually test

Thirty-four items across M25, F24 and F23. They cluster, and the clusters are
the syllabus in miniature.

### Definitions you must be able to recite, not paraphrase

- *Key generation is randomised but Enc and Dec must be deterministic so
  ciphertexts decrypt uniquely.* **False** (M25 a). Enc is randomised in every
  CPA-secure scheme; determinism is the one-line CPA break (note 06).
- *Every perfectly secret scheme is perfectly indistinguishable and vice versa.*
  **True** (M25 c) — K&L Lemma 2.7, note 02.
- *Shannon's theorem: a scheme with |M| = |K| = |C| is perfectly secret if for
  every m, c there is a unique k with Enc_k(m) = c.* **False** (M25 d). The
  theorem needs **both** conditions: every key equally likely **and** the unique
  key. Dropping the uniform-key half is the trap, and it is the single most
  precisely-worded item on any of the papers. Note 02.
- *ECB, CBC and CTR are all EAV-secure.* **False** (M25 i). ECB is not, being
  deterministic. *…all CPA-secure* **False** (F23 d), same reason. *CBC and CTR
  are CCA-secure* **False** (F23 e) — note 06.
- *The one-time pad is CCA-secure.* **False** (F24 i).
- *A deterministic MAC cannot be secure.* **False** (F23 f) — the PRF MAC is
  deterministic and EUF-CMA (note 07).
- *A MAC prevents replay attacks.* **False** (F23 g) — replay is outside the
  definition (note 07).
- *Encrypt-then-authenticate with a CPA-secure scheme and a secure MAC is secure
  AE.* **True** (F24 d) — note 07.

### Block ciphers, which the notes used to skip

- *AES is a substitution-permutation network.* **True** (M25 g).
- *The permutation layer of an SPN provides confusion.* **False** (F24 c) — it
  provides **diffusion**; the S-box provides confusion (note 03).
- *The S-box of an SPN must be kept secret.* **False** (F24 f) — Kerckhoffs
  (note 01, note 03).
- *A Feistel network is invertible even when its round functions are not.*
  **True** (M25 e, F24 j) — asked twice in two years (note 03).
- *A meet-in-the-middle attack breaks a double-key cipher E'_(k,k') = E_k' ∘ E_k
  in roughly the square root of the brute-force time.* **True** (M25 f) —
  note 03, `block_ciphers.meet_in_the_middle`.
- *DES has longer keys than AES.* **False** (F23 c) — 56 against 128/192/256.
- *Unlike monoalphabetic ciphers, polyalphabetic ciphers are immune to frequency
  analysis.* **False** (M25 b) — note 01.

### Asymptotics, where one item is a genuine trap

- *If f is negligible then n^{|f(n)|} is negligible.* **False** (M25 h). This
  reads like the closure property poly × negligible = negligible, which is true
  — but the polynomial is in the **exponent**. n^{f(n)} = e^{f(n) ln n} → 1
  because f(n) ln n → 0, so the quantity tends to 1, not to 0. Note 04.
- *f(n) = (n-1)/n is negligible.* **False** (F23 b) — it tends to 1.
- *p(n)·2^{-log n} is negligible for a positive polynomial p?* (F20 2a) — no:
  2^{-log₂ n} = 1/n, so the product is a ratio of polynomials.
- *An unbounded adversary can break a perfectly secret scheme.* **False**
  (F23 a) — that is the definition.
- *A hash with ℓ-bit output can achieve up to ℓ bits of collision resistance
  (2^ℓ evaluations).* **False** (F24 h) — the birthday bound gives ℓ/2. Note 08.
- *Merkle-Damgard is collision-resistant if its compression function is.*
  **True** (F24 a) — K&L Thm 6.4.

### Algebra and the hardness assumptions

- *(Z, ·) is a group.* **False** (F23 i) — no inverses.
- *Z_7^* is cyclic.* **True** (F24 e) — every Z_p^* is.
- *({0,1}², ⊕) — a group? cyclic?* (F20 2b) — a group, **not** cyclic: every
  non-identity element has order 2, so no generator. Note 09.
- *For gcd(e, φ(N)) = 1, x ↦ [x^e mod N] is a permutation of Z_N^*.* **True**
  (F23 j) — note 09, `test_rsa.py::test_rsa_is_a_permutation_of_the_unit_group`.
- *The discrete logarithm problem is hard in (Z_p, +).* **False** (F23 k) —
  the "exponentiation" is multiplication by x, so the log is a division mod p.
  Note 09.
- *If CDH holds in G then the discrete logarithm assumption holds in G.*
  **True** (F24 g). The direction matters: solving DLog solves CDH solves DDH,
  so as *assumptions* DDH ⇒ CDH ⇒ DLog. Note 09 had this backwards until the
  2026-09-22 pass.
- *NIST recommends longer keys for private-key than for public-key schemes.*
  **False** (F23 l) — it is the other way round by an order of magnitude:
  128-bit security needs AES-128 but RSA-3072 [S27]. Note 09.
- *For the same security level NIST recommends a longer RSA modulus than the
  bit length of an elliptic-curve group's order.* **True** (F24 b) — 3072
  against 256.
- *[3^1000000 mod 22] = 3.* **False** (F24 k). gcd(3, 22) = 1 and
  φ(22) = 10 divides 1000000, so by Euler the value is 3⁰ = **1**; the order
  confirms it (ord(3) = 5, since 3⁵ = 243 = 11·22 + 1). The trap is answering 3
  without reducing the exponent at all.
- *[2^63 mod 11]* (F23 4a). Fermat: exponents reduce mod 10, 63 ≡ 3, so
  2³ = **8**.

## The long questions, by kind

### Kind 1 — reconstruct a definition (every paper)

M25 q2 prints the CCA experiment with five blanks and asks you to fill them in.
F23 q2a prints the CCA experiment complete and asks **which modifications give
CPA-security** (answer: delete the decryption oracle from steps 1 and 4, and
therefore the restriction that it may not be queried on c*). F24 q3 prints a
*deliberately weakened* MAC definition — one that omits "m* was not queried" —
and asks what to change to get EUF-CMA.

The pattern: they do not ask you to recall the game from nothing, they ask you
to notice **which clause is missing or wrong**. Practise by writing each game
out and then asking what breaks if each line is deleted. Note 13 has the
checklist.

### Kind 2 — a reduction, 4 to 6 points

- M25 q4: prove `Mac_k(m) := F_k(m) ⊕ m` is EUF-CMA, by giving the reduction.
- F24 q2c: cascade encryption, `Enc_(k1,k2)(m) = Enc₂(Enc₁(m))` with independent
  keys, is CPA-secure if **either** component is. (Two reductions, one per case;
  the reduction simulates the other layer itself, since it chose that key.)
- M25 q5 / F24-style: construct authenticated encryption from a CPA-secure
  scheme and a MAC — i.e. write down encrypt-then-MAC, all three algorithms.

These are worth the most points per question and they are the thing the nine
homework assignments train. Note 13 is the procedure.

### Kind 3 — an explicit attack, 3 to 5 points

- M25 q3b: a contrived scheme whose key depends on the **parity of the message**
  (`r := k_{p(m)}`); show it is not EAV-secure. The give-away is that the
  ciphertext's own parity leaks p(m).
- F20 1a: one round of a Feistel network — give the distinguisher. (The left
  half of the ciphertext *is* the right half of the plaintext.)
- F20 3a: `c := F_k(r) ⊕ m` with `r` chosen fresh **and not sent**. The answer is
  not about security at all: it is not decryptable.
- F20 5a/5b: the basic CBC-MAC length-extension forgery, and why
  encrypt-and-authenticate with a deterministic MAC is not CPA-secure.
- F23 3: `Mac_k(m) := F_k(H(m))` — show it is insecure if H is not collision
  resistant. (Find x ≠ x' with H(x) = H(x'), query the tag on x, output it on x'.)
- F23 5b: a **hybrid** scheme `(Enc_pk(k), Enc'_k(m))` with a CCA-secure DEM —
  show it is not CCA-secure. (Re-randomise the ElGamal part; same plaintext,
  different ciphertext, so the decryption oracle will answer it.)
  `elgamal.hybrid_cca_attack`.
- F24 5b / F20 6: two Schnorr signatures under the same nonce — recover the
  secret key. Asked in two of the four papers. `signatures.schnorr_nonce_reuse_attack`.

### Kind 4 — compute or construct, 2 to 4 points

- F23 4a `[2^63 mod 11]`; F24 2a decrypt a 3-block CBC ciphertext by hand.
- F23 4b: two RSA moduli **sharing a prime factor** — recover both secret keys.
  (`gcd(N₁, N₂)`; `rsa.shared_prime_attack`.)
- F23 5a / F24 5a: given an ElGamal or Schnorr scheme's Gen and Enc/Sign, write
  down Dec/Vrfy and **prove correctness**. Pure algebra, always worth taking.
- F24 4a: how N, e and d are chosen in RSA key generation.
- F23 2b: define the one-time pad — key space, message space, all three
  algorithms. 2c: is it CPA-secure? (No: deterministic in the one-time setting,
  and the definition of the scheme only covers one message per key.)
- F23 2d / F24 4b / F20 6c: short discussion questions — one advantage and one
  disadvantage of private- versus public-key encryption; why the PKE CPA game
  gives no encryption oracle (the adversary has `pk`, so it can encrypt itself);
  two advantages of signatures over MACs (public verifiability, non-repudiation,
  and one signature serves many verifiers).

## The homework

Nine graded assignments; this wiki does not discuss their questions or
solutions. Format in 2026W [S1]: tick on TUWEL which problems you solved, upload the
solutions, volunteers present. This is stricter than 2025W, where the grade was
"only about how many exercises you check" [S5]: uploads are now **graded**, a
missing, incomplete, copied or clearly AI-generated solution zeroes the sheet,
and a second such case means a negative grade (rules at the top). Together with
the half-the-points hurdle, the homework gates the exams rather than just adding
to them. The 2026-09-22 rule that assignment 1 is a prerequisite for an
exercise group is gone; there is one exercise slot for everyone.

## Where to spend your time

1. **The reduction template** (note 13) — kind 2 is the most points and the
   whole homework.
2. **The security games, clause by clause** (notes 02, 04, 06, 07, 10, 11) —
   kind 1, and the true/false section leans on them.
3. **The catalogue of attacks** (notes 01, 03, 06, 07, 10, 11) — kind 3. Each is
   a page of the notes and a function in `src/py`.
4. **Block ciphers** (note 03): eight true/false items across three papers, and
   the notes had almost nothing on it before the 2026-09-22 pass.
5. **Modular arithmetic by hand** (note 09): `[a^b mod N]` appears on both
   finals: check gcd(a, N) = 1, reduce the exponent mod φ(N) (or mod the
   element's order, when that is quicker to see), then compute.

Items 2-4 for notes 01-06 are the midterm; items 2, 3 and 5 for notes 07-12
are the final. Item 1 serves both and every exercise sheet.

## What is *not* asked

From the lecturer's own closing slide [S8], and confirmed by the papers' silence
on all of it: **no security proof for a public-key scheme** (so no RSA-FDH ROM
proof, no OAEP proof, no forking lemma), **no GGM**, **no factoring or DLog
algorithms** beyond quoting their running times, **no Cramer-Shoup**, **no
post-quantum**. The notes still cover them, marked `(background)`, because a
QIST student should know them — but not before the five items above.
