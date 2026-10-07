# 12 — PKI and TLS: where all of it is used at once

*Lectures 13 and 13a [S8]. Katz-Lindell sec. 13.6-13.7 [S10]. Primary source:
RFC 8446 [S18]. No TLS code: this note is about how the pieces in
[`../src/py`](../src/README.md) compose, not about a new primitive; the
`## Code` section at the end lists the pieces (DH, HKDF, HMAC, signatures).*

The course ends by assembling everything into the protocol that runs behind
`https://`. It is worth the hour it takes, because every failure mode in the
notes shows up here as a design decision someone had to make.

## The problem PKI solves

Note 11 gives public verifiability: anyone holding $pk$ can check a signature.
It does **not** say whose $pk$ that is. Alice publishes $pk$; an active adversary
replaces it in transit with $pk'$ and signs everything itself [S8]. Signatures
authenticate *relative to a key*, and nothing so far authenticates the key.

This is the same gap as the Diffie-Hellman man-in-the-middle of note 10
(`dh.mitm_demo`), and it has the same shape: a shared secret with *someone*, an
authenticated key from *nobody*.

## Certificates

A **certificate** is a signature by a trusted third party binding an identity to
a key:

$$\mathrm{cert}_{\mathrm{CA}\to A} = \mathsf{Sign}_{sk_{\mathrm{CA}}}
\big(\texttt{"Alice"} \,\|\, pk_A \,\|\, \text{validity} \,\|\, \dots\big)$$

Bob verifies it with $pk_{\mathrm{CA}}$ and then trusts $pk_A$ [S8]. **Root**
CAs sign **intermediates**, which sign end-entity certificates; a browser walks
the chain up to a root it already has.

The obvious objection, which lecture 13 raises itself: *how does Bob get
$pk_{\mathrm{CA}}$?* Are we back where we started? No — because the number of
roots is small and fixed, so they ship with the browser or the operating system.
The trust problem is not solved, it is **concentrated**: from "authenticate every
key" to "authenticate a few hundred keys, once, out of band" [S8].

### What is wrong with it in practice

Lecture 13's own list [S8], and it is not short:

- **Numerous root CAs**, several hundred in a default browser store. Any one of
  them can issue a certificate for any name — the security of the system is that
  of its *weakest* CA, not its strongest *(unsourced: DigiNotar, 2011, is the
  canonical disaster — a Dutch CA compromised into issuing a valid
  `*.google.com` certificate. No primary source was fetched; the structural
  point, that any root can vouch for any name, is on the lecture-13 slide
  [S8])*.
- **Revocation is hard.** CRLs are large and stale; OCSP leaks which sites you
  visit to the CA and fails open when unreachable; OCSP stapling helps and is not
  universal.
- **Detection after the fact.** **Certificate Transparency** logs every issued
  certificate in an append-only Merkle tree (note 08), so a mis-issued
  certificate is *publicly visible* even if it was not prevented. This is the
  one place in the course where the Merkle tree of lecture 9 has a real job.
  *(Unsourced: CT is specified in RFC 6962/9162, which was not fetched or
  vendored — the course does not cover it and the lecture slides do not mention
  it. It is here because it is the only answer anyone has to "any CA can vouch
  for any name", and because it reuses lecture 9's Merkle trees.)*

### Web of trust

PGP's alternative: no authorities, users sign each other's keys, and you accept
a key if there is a short enough chain of people you already trust [S8]. It
removes the single points of failure and replaces them with a usability problem
that has never been solved at scale.

## TLS 1.3

SSL (Netscape, mid-1990s) → TLS 1.0 (1999) → TLS 1.2 (2008) → **TLS 1.3 (2018)**
[S8, S18]. Two parts:

- **Handshake protocol** — the server authenticates and both sides agree on
  shared keys.
- **Record-layer protocol** — the keys protect the actual traffic.

### The handshake, as lecture 13a draws it [S8]

Using a standardised group $(\mathbb G, q, g)$ [S26]:

| | client | | server |
|---|---|---|---|
| 1 | picks $x\gets\mathbb Z_q$, nonce $N_C$ | $\xrightarrow{\ \text{ciphersuites},\, N_C,\, g^x\ }$ | |
| 2 | | $\xleftarrow{\ N_S,\ g^y,\ c\ }$ | picks $y\gets\mathbb Z_q$; $K := (g^x)^y$ |
| 3 | $K := (g^y)^x$; decrypt $c$ | | $c \gets \mathsf{Enc}_{k'_S}\big(pk,\ \mathrm{cert}_{\mathrm{CA}\to S},\ \sigma\big)$, $\sigma\gets\mathsf{Sign}_{sk}(\text{transcript})$ |
| 4 | verify cert, verify $\sigma$ | $\xrightarrow{\ \tau\ }$ | $\tau := \mathsf{Mac}_{k'_C}(\text{transcript}')$, verified by the server |
| | $(k'_S,k'_C,k_S,k_C) := \mathsf{KDF}(K)$ | | same |

Five things to notice, each of which is a lesson from an earlier note:

1. **The key exchange is ephemeral Diffie-Hellman**, and only that. TLS 1.3
   removed static-RSA key transport entirely [S18], which is what killed the
   Bleichenbacher family of attacks [S42] in this protocol and gives **forward
   secrecy**: $x$ and $y$ are discarded, so compromising the server's long-term
   $sk$ later does not decrypt recorded sessions.
2. **The signature is over the transcript**, not over the key. That is what
   binds the authenticated identity to *this* exchange — exactly the fix for the
   MITM of note 10. Signing only $g^y$ would let an adversary replay it into a
   different session.
3. **The certificate is sent encrypted**, under a key derived from $K$ before
   authentication finishes. Privacy improvement over TLS 1.2, where it was in
   the clear.
4. **KDF** turns the group element $K$ into four independent symmetric keys —
   HKDF-Expand-Label in the real thing [S18 sec. 7.1, S34]. Note 10: the DH value
   is *not* key material; you need DDH plus a hash, or the hashed-DH assumption,
   before calling it a key.
5. **The client's Finished message is a MAC over the transcript**, giving both
   sides a check that they saw the same messages — downgrade protection, and the
   reason a network attacker cannot strip the strong ciphersuites from step 1.

### The record layer

Once the handshake is done, application data is protected with **AEAD** (note
07): TLS 1.3 mandates AES-GCM or ChaCha20-Poly1305 [S18 sec. 9.1, S31, S36]. Two
details the lecture flags [S8]:

- **Sequence numbers prevent replay.** A MAC does not (note 07); the protocol
  layer must. TLS derives the AEAD nonce by XORing a per-connection IV with the
  64-bit record sequence number, which also guarantees nonce uniqueness — and
  nonce reuse in GCM is catastrophic (notes 06, 07).
- **Different keys per direction** ($k_C$ and $k_S$) prevent **reflection**: a
  record the server sent cannot be bounced back and accepted as if the client had
  sent it.

This is the "secure communication sessions" of lecture 8, K&L sec. 5.4, made
concrete [S8].

## Worked example

*Why does TLS 1.3 sign the transcript rather than the server's DH share, and
what breaks if it signs only $g^y$?*

Suppose the server sends $(g^y, \mathsf{Sign}_{sk}(g^y), \mathrm{cert})$. The
signature is now a statement about a group element and nothing else, so an
adversary can **replay** it. It opens its own connection to the server, collects
$(g^y, \sigma)$, and then, when a client connects to *it*, forwards that pair.
The client verifies the certificate and the signature — both genuine — and
completes a handshake whose transcript includes the adversary's chosen
ciphersuite list and nonce $N_C$. The adversary does not learn $K$ (it cannot
compute $g^{xy}$), so it cannot read the traffic; but it *has* convinced the
client that a session with a chosen, possibly downgraded, negotiation was
authenticated by the server. Binding the whole transcript — nonces, ciphersuites,
key shares — makes $\sigma$ valid for exactly one exchange and nothing else. The
nonces are what stop even an identical transcript from recurring. $\square$

## Pitfalls

- **A certificate binds a key to a name, not a name to a person.** Domain
  validation proves control of a DNS record, nothing more.
- **Any CA can vouch for any name.** Security is the minimum over the trust
  store, not the maximum.
- **Revocation may silently fail.** Plan for a compromised key staying valid.
- **Forward secrecy is a property of the key exchange, not of the cipher.**
  Static-RSA TLS 1.2 had none; TLS 1.3 has it by construction.
- **Nonce discipline is still yours in the record layer.** GCM nonce reuse
  destroys integrity as well as secrecy (note 07); TLS derives it from a counter
  precisely so no implementer can get it wrong.
- **Signing the wrong thing** is the commonest protocol bug in the course: sign
  the transcript, bind the message into Fiat-Shamir's hash (note 11), MAC the
  ciphertext not the plaintext (note 07). Same mistake three times.

## Exam-style questions

All five are ours: **no public past paper of this course asks about TLS or PKI**
[S12, S13, S15, S16]. Lecture 13a is the last, short session before the outro,
and the 2026W midterm (18.11.2026) cannot reach it. Treat this note as
comprehension, not drill, but K&L sec. 13.6-13.7 is on the syllabus [S8] and
lecture 13a falls before the final of 29.01.2027.

**Q1.** What does each signature in a certificate chain attest, and where does
the trust bottom out? — Each CA signature binds a subject name to a subject
public key, with a validity period. The browser verifies end-entity →
intermediate → root, each link a signature check under the issuer's key, ending
at a root whose key was installed out of band. Nothing in the chain is
self-supporting; the root is an axiom.

**Q2.** TLS 1.3 removed RSA key transport, in which the client encrypted the
premaster secret under the server's RSA public key. Give two reasons. — (i) No
forward secrecy: recording traffic and later obtaining the server's private key
decrypts everything. (ii) RSA-PKCS #1 v1.5 decryption is a chosen-ciphertext
oracle (Bleichenbacher [S42], and the same shape as note 06's padding oracle);
twenty years of attempted countermeasures never made it robust. Ephemeral DH has
neither problem.

**Q3.** The record layer uses different keys for client→server and
server→client. What attack does that prevent, and would a sequence number alone
suffice? — Reflection: without it, an attacker can return a record the server
sent and have the server accept its own message as the peer's. Sequence numbers
alone do not help, since both directions would be counting in the same key's
namespace and a record with a plausible number would verify. Key separation
makes the ciphertexts simply not authenticate in the wrong direction.

**Q4.** Certificate Transparency does not prevent mis-issuance. What does it
give you, and which primitive from the course does it rest on? — Public,
after-the-fact detectability: every certificate a participating CA issues is
entered in an append-only log, so a domain owner can see certificates for their
own name that they did not request. It rests on Merkle trees (note 08): the log
publishes a root hash, and append-only-ness plus inclusion of any entry is proved
with $O(\log n)$ sibling hashes, so the log cannot retroactively remove an entry
without changing the root.

**Q5.** In the handshake, the server's signature covers the transcript and the
client's Finished message is a MAC over the transcript. Why are both needed? —
The signature authenticates the *server's identity* to the client and binds it to
this exchange; the client is normally unauthenticated, so it cannot sign. The
Finished MAC is computed under a key derived from $K$, so producing it proves the
client actually holds $K$ — it demonstrates key confirmation and, because it
covers the transcript, that the client saw the same ciphersuite negotiation the
server did. One establishes who; the other establishes that both sides agree on
what.

## Code

No TLS code, but the TLS 1.3 building blocks are all implemented:
`src/py/dh.py`: `shared_value` (the ephemeral exchange);
`src/py/mac.py`: `hkdf_extract`, `hkdf_expand` (the key schedule of RFC 8446
sec. 7.1 [S18] is HKDF, RFC 5869 [S34]), `hmac` (the Finished MAC);
`src/py/signatures.py`: `rsassa_pkcs1_v15_sign` (certificate signatures);
`src/py/hashing.py`: `sha256` (the transcript hash).
