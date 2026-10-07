# 08 DNS, DNSSEC and Telnet (application-layer protocols)

> **Sourcing.** DNS is RFC 1034/1035 with EDNS(0) from RFC 6891, DNSSEC is RFC
> 4033/4034/4035, Telnet is RFC 854/855 with the option-negotiation state
> machine of RFC 1143 — all vendored [S16]. This note carries the course's one
> published **test vector**: RFC 4034 §5.4's DNSKEY and DS, reproduced by
> `src/py/dnssec.py`. The subject list names DNS, **DNSSEC** and Telnet
> explicitly and separately [S1], and DNS is the lecturer's own research area
> [S5], so treat this note as heavier than its length suggests.

## DNS (RFC 1034/1035 [S16]): the name-to-anything database

**Namespace** (RFC 1034 §3.1): a tree; a name is the path from a node to the root, labels right to left, `www.tuwien.ac.at.` (trailing dot = fully qualified). Labels ≤ 63 bytes, names ≤ 255, case-insensitive ASCII (RFC 1035 §2.3.1, §2.3.4; IDN via Punycode `xn--`). **Zone**: a contiguous part of the tree under one administration, delimited by **delegations** (NS records handed down at the cut). Root zone (13 root server *names*, hundreds of anycast instances) → TLDs (`at` run by nic.at, generic `com` by Verisign) → second level (`tuwien.ac.at` after the `ac.at` delegation) → subzones.

**Resource record**: `(name, TYPE, CLASS=IN, TTL, RDATA)`.

| Type | RDATA | Use |
|---|---|---|
| A / AAAA | IPv4 / IPv6 address | host addresses |
| NS | name of an authoritative server | delegation (appears in parent and child) |
| CNAME | canonical name | alias; the name has no other records; resolvers follow it |
| MX | preference, mail server name | mail routing |
| SOA | primary NS, admin mail, serial, refresh/retry/expire, negative-cache TTL | zone apex, zone transfer control |
| PTR | name | reverse lookup: `76.35.130.128.in-addr.arpa`, IPv6 `…ip6.arpa` nibble-reversed |
| TXT | text | SPF, DKIM, domain verification |
| SRV | priority, weight, port, target | service discovery (`_sip._tcp`) |
| DS, DNSKEY, RRSIG, NSEC/NSEC3 | see DNSSEC | |
| OPT | pseudo-RR in Additional | EDNS0: UDP size > 512, DO flag |

**Players**: **stub resolver** (the OS, `/etc/resolv.conf`) → **recursive resolver** (ISP, 1.1.1.1, 8.8.8.8, or local `unbound`; does the work, caches) → **authoritative servers** (answer only for their zones, no recursion; primary holds the zone file, secondaries copy via AXFR/IXFR over TCP).

### Resolution (iterative from the resolver's view)

`www.tuwien.ac.at A`, empty cache:

1. Stub → resolver: query with **RD** (recursion desired) set.
2. Resolver → root server: same question. Answer: **referral** — no answer section, Authority: `at. NS …`, Additional: their addresses (glue).
3. Resolver → `at` server → referral to `ac.at`/`tuwien.ac.at` NS (glue for in-bailiwick names).
4. Resolver → tuwien.ac.at server: answer with **AA** (authoritative) set, `www.tuwien.ac.at. IN A 128.130.35.76` (possibly a CNAME first). That address is real and was re-checked on 2026-09-22 [S23]; it sits in `128.130.0.0/15`, RIPE netname **TUNET**, originated by **AS679** — TU Wien's own AS, not ACOnet's AS1853 [S20] (note 06).
5. Resolver caches every RRset for its TTL (also the referrals, so the next `*.ac.at` query starts at step 3) and answers the stub with RA set, AA clear.

Negative answers (**NXDOMAIN**, rcode 3, or NODATA: name exists, type does not) are cached for the SOA minimum TTL. `dig +trace` performs these steps for you; `dig +norecurse @server` asks a specific server directly.

### Message format (RFC 1035 §4.1 [S16]): UDP port 53, TCP 53 for messages over the 512-byte UDP limit of §4.2.1 (TC bit = truncated, retry over TCP) and for zone transfers. EDNS(0) — RFC 6891 §6.1, §6.2 [S16] — lifts that limit by putting a "requestor's UDP payload size" in an **OPT pseudo-RR** in the Additional section, and carries the **DO** bit that asks for DNSSEC records

| Header field | Bits | Meaning |
|---|---|---|
| ID | 16 | matches response to query (also the only anti-spoofing entropy besides the source port: Kaminsky attack, 2008) |
| QR | 1 | 0 query, 1 response |
| Opcode | 4 | 0 standard query |
| AA | 1 | authoritative answer |
| TC | 1 | truncated |
| RD | 1 | recursion desired |
| RA | 1 | recursion available |
| Z, AD, CD | 1+1+1 | AD: authenticated data (DNSSEC validated by the resolver); CD: checking disabled |
| RCODE | 4 | 0 NOERROR, 2 SERVFAIL (also: DNSSEC validation failed), 3 NXDOMAIN, 5 REFUSED |
| QDCOUNT, ANCOUNT, NSCOUNT, ARCOUNT | 4 × 16 | number of entries in Question, Answer, Authority, Additional |

Question: QNAME (labels: length byte + bytes, terminated by 0), QTYPE, QCLASS. RR: NAME, TYPE, CLASS, TTL (32), RDLENGTH, RDATA. **Name compression** (RFC 1035 §4.1.4): a length byte whose top two bits are 11 introduces a 14-bit pointer to an earlier offset in the message (`c0 0c` = "the name at byte 12", i.e. the question name). The RFC restricts pointers to prior occurrences, which is what makes a decoder's loop guard both necessary in practice and justified. 

Worked bytes (`dns.py` demo): query `beef 0100 0001 0000 0000 0000 | 03 www 07 example 03 com 00 | 0001 0001` = ID 0xbeef, flags 0x0100 (RD), one question, `www.example.com A IN`. Response flags `8580` = QR, AA, RD, RA; answer `c00c 0001 0001 00000e10 0004 cb00710a` = name pointer, A, IN, TTL 3600, 4 bytes, **203.0.113.10** — an RFC 5737 documentation address [S15]. *(Earlier versions of this note and of `dns.py` used `5db8d822` = 93.184.216.34, which was `example.com`'s address for over a decade and appears in every textbook. It is now wrong: as of 2026-09-22 the name answers with Cloudflare addresses [S23]. Documentation space cannot go stale.)*

### Caching and its consequences

TTL is chosen by the zone owner: long (days) for stable records, short (60–300 s) before a planned move (lower it one old-TTL before the change). *(unsourced operational practice, not RFC 1035.)* Caches make the system scale (root servers see a tiny fraction of queries) and make changes propagate slowly. Cache poisoning: inject a forged answer with a guessed ID; defences: random source ports, 0x20 case randomisation, DNSSEC. Source-address spoofing is what makes this and the amplification attack below possible at all, and the network-side mitigation is BCP 38 ingress filtering, RFC 2827 [S17]. Privacy: plain DNS is cleartext; DoT (TCP 853) and DoH (HTTPS) encrypt stub-to-resolver.

## DNSSEC (RFC 4033–4035 [S16]): authenticating the data, not the channel

Adds signatures so a validating resolver can detect forged or modified records. It does not encrypt and does not authenticate the server.

| Record | Role |
|---|---|
| **DNSKEY** | zone's public keys: **ZSK** (signs the records) and **KSK** (signs the DNSKEY RRset). RDATA is Flags(16) ‖ Protocol(8) ‖ Algorithm(8) ‖ key (RFC 4034 §2.1). Flags bit 7 = Zone Key (256), bit 15 = **SEP** (1), so a ZSK is written 256 and a KSK 257 |
| **RRSIG** | signature over one RRset (all records of one name+type), with validity window, algorithm, key tag, signer name |
| **DS** | *in the parent zone*: `digest = H(canonical owner name ‖ DNSKEY RDATA)` (RFC 4034 §5.1.4), plus the **key tag** — a 16-bit sum over the DNSKEY RDATA (Appendix B) that narrows the candidate keys and, the RFC stresses, does **not** identify one uniquely. This is the link in the chain |
| **NSEC / NSEC3** | authenticated denial of existence: "there is no name between `a.example` and `c.example`" (NSEC3 hashes names to hinder zone walking) |

**Chain of trust**: the resolver has the **root KSK** built in (trust anchor; rolled in 2018). Validate `www.tuwien.ac.at A`:

1. Verify the A RRset's RRSIG with tuwien.ac.at's ZSK (from its DNSKEY RRset).
2. Verify the DNSKEY RRset's RRSIG with tuwien.ac.at's KSK.
3. Hash that KSK and compare with the DS record in `ac.at`; verify the DS RRset's RRSIG with `ac.at`'s ZSK; its DNSKEY with its KSK; DS in `at`; … up to the root DNSKEY, verified against the trust anchor.

Any failure → SERVFAIL (RFC 4035 §5.5); success → the **AD** bit to the stub (§3.2.3), and a stub can suppress validation with **CD** [S16]. Unsigned zone (no DS in parent) → **insecure**, accepted without validation — NSEC/NSEC3 in the parent proves the DS is genuinely absent, so an attacker cannot strip the signatures of a signed zone. RFC 4033 §5 names the four states a validator can reach: *secure*, *insecure*, *bogus*, *indeterminate*. Operational burdens: key rollovers, signature expiry (the classic outage), larger responses (→ amplification: a small query, a multi-kilobyte answer, a spoofed source; RFC 8482 [S16] is one mitigation, BCP 38 [S17] the other).

### Reproducing the chain by hand

The key tag and the DS digest are the only parts of DNSSEC you can compute
without a key, and RFC 4034 §5.4 prints a complete worked example: a DNSKEY for
`dskey.example.com.` with flags 256, protocol 3, algorithm 5, annotated
"key id = 60485", and the matching

```
dskey.example.com. 86400 IN DS 60485 5 1 ( 2BB183AF5F22588179A53B0A98631FAD1A292118 )
```

[`../src/py/dnssec.py`](../src/py/dnssec.py) computes both from the base64 key
and `test_rfc_vectors.py` asserts they match the RFC's printed values. Two
details the exercise teaches: the digest is over the **canonical owner name**
(wire format, lower case, RFC 4034 §6.2) concatenated with the RDATA, so the
same key under a different name gives a different DS; and the key tag is the
Internet checksum's sum **without the final complement** — RFC 4034 warns
"Key Tags MUST be calculated using the algorithm described here rather than the
ones complement checksum", and the test pins the exact relationship.

## Telnet (RFC 854/855 [S16]): the archetypal text protocol

Remote terminal over **TCP port 23**; every byte is data except **IAC** (0xFF, "interpret as command"). The **network virtual terminal** abstracts the terminal: 7-bit ASCII, CR LF line ends, IAC IAC for a literal 0xFF. Commands after IAC: WILL/WONT (251/252: I will/won't do option X), DO/DONT (253/254: please do/don't), SB … SE (250/240: sub-negotiation with parameters), NOP, GA (go ahead), BRK, IP (interrupt process), AYT. Options: ECHO (1), SGA suppress go-ahead (3), TTYPE terminal type (24), NAWS window size (31), LINEMODE (34), BINARY (0).

Negotiation is symmetric and must not loop. RFC 1143 §2 [S16]: answer every command that proposes a change of state (DO/WILL for an option that is off, DONT/WONT for one that is on), and answer nothing that does not (a WONT for an option already off is ignored, which is what "never reply to a refusal" means precisely); never answer a refusal with a new request; do not re-request an option already in the requested state. RFC 855 [S16] defines the framework and **RFC 1143** gives the state machine, the "Q method": per option and per direction a state NO/YES/WANTNO/WANTYES plus a queue bit, i.e. six combined states. Its reason for existing is that the obvious implementation, which confirms every rejection, loops. Typical login: server `IAC DO TTYPE, IAC WILL ECHO, IAC WILL SGA` (server echoes characters, so the client stops local echo → passwords are not shown); client `IAC WILL TTYPE`, then `IAC SB TTYPE 0 "xterm" IAC SE`.

Why it is in the course: (1) it is a clean example of in-band signalling with an escape byte, option negotiation and a state machine per option (note 10 contrasts it with length-prefixed framing); (2) `telnet host 80` / `nc` lets you speak HTTP, SMTP, POP3 by hand because those are also line-based ASCII; (3) it is unencrypted — everything, including passwords, is visible in a trace, which is why SSH (port 22) replaced it in 1995–2000 and why it still appears in IoT botnets (Mirai brute-forced Telnet logins).

## Worked example: reading `dig`

```
;; flags: qr rd ra ad; QUERY: 1, ANSWER: 2, AUTHORITY: 0, ADDITIONAL: 1
;; ANSWER SECTION:
www.example.org.   300  IN  CNAME  example.org.
example.org.       3600 IN  A      203.0.113.10
```
qr response, rd/ra recursion, **ad** = the resolver validated DNSSEC, no aa = answer from cache/recursive resolver, not authoritative. The CNAME was followed by the resolver; the A record's TTL is the remaining cache time. ADDITIONAL 1 = the OPT pseudo-record (EDNS).

## Pitfalls

- A resolver's answer to you is *recursive*; its own queries upstream are *iterative*. "Recursive query" refers to the RD bit, not to a code path.
- NS records at a delegation are in both parent (glue, unsigned) and child (authoritative); the child's version is the truth.
- CNAME at a zone apex is illegal (the apex has SOA and NS); hence ALIAS/ANAME hacks.
- DNS over UDP means the query itself is unreliable: the stub retries after a timeout (5 s default → the "slow first page load" symptom).
- DNSSEC signs *records*, not the query/response exchange: a validating resolver protects itself; the stub is protected only if the last mile is trusted or uses DoT/DoH.
- Telnet has no notion of "message"; a `\r\n` is just two data bytes, interpreted by the application (login shell).

## Exam-style questions

1. *Decode the DNS header `1a2b 8183 0001 0000 0001 0000`.* ID 0x1a2b; flags 0x8183 = QR=1, opcode 0, AA=0, TC=0, RD=1, RA=1, RCODE=3 NXDOMAIN; one question, no answers, one authority record (the SOA for negative caching), no additional.
2. *Why does the resolver cache the referral to `at` for a long time even though it only asked for `www.tuwien.ac.at`?* NS records of the TLD have long TTLs (2 days) and the resolver stores every RRset it receives; subsequent queries for any `*.at` name skip the root.
3. *A zone's RRSIG expired last night. Who notices and what do users see?* Validating resolvers reach the *bogus* state (RFC 4033 §5) and answer SERVFAIL (RFC 4035 §5.5) [S16]; users of non-validating resolvers see nothing at all. The zone owner therefore hears from only part of the Internet, which is why signature-expiry outages are diagnosed slowly.
4. *Which record in the parent connects the DNSSEC chain and why is it a hash rather than the key itself?* DS, whose digest is $H(\text{canonical owner name} \mathbin\Vert \text{DNSKEY RDATA})$, RFC 4034 §5.1.4 [S16]. A hash is short (the parent zone stays small and the referral still fits a datagram), and the child can roll its ZSK freely without touching the parent; only a KSK rollover requires the parent to publish a new DS. Note that the owner name is inside the hash, so a key cannot be transplanted to another zone.
5. *In a Telnet trace you see `ff fb 01`. What is it and what should a client answer?* IAC WILL ECHO: the server offers to echo. Client answers `ff fd 01` (IAC DO ECHO) and stops local echo, or `ff fe 01` (DONT) to refuse.
6. *Why is a 68-byte DNS query able to cause a 3000-byte packet to hit a victim?* Source-address spoofing works over UDP because there is no handshake to bind the source; `ANY` and DNSSEC answers are large, and EDNS(0) lets the attacker ask for a 4096-byte response (RFC 6891) — tens of times amplification. Mitigations: BCP 38 ingress filtering (RFC 2827 [S17]), response rate limiting, and minimal ANY answers (RFC 8482 §4 [S16]).

## Code

`src/py/dns.py`: `encode_name` (RFC 1035 §2.3.4 limits; with a table, §4.1.4 suffix compression), `build_query` (with EDNS0 DO), `build_response` (every owner name compressed, so the query name becomes `c0 0c`), `parse_message`, `decode_name` (pointer following with loop guard); `test_dns.py` rebuilds §4.1.4's F.ISI.ARPA figure byte for byte and compares a full response with a hand-written packet; `python dns.py --live name` sends a real query (tests never do). `src/py/dnssec.py`: `key_tag` (RFC 4034 Appendix B), `ds_digest`/`ds_record` (§5.1.4), `canonical_name` (§6.2), with the §5.4 vector in `RFC4034_EXAMPLE` and asserted in `test_rfc_vectors.py`. `src/py/telnet_client_sketch.py`: `parse_stream` (IAC escapes, SB…SE), `QOption` (RFC 1143 §7, tested row by row against the section's tables), `Negotiator` and `negotiate` (refuse-by-default client on top), `describe`.
