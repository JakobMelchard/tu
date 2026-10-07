# Reference implementations — 191.030 Introduction to Networking

Pure Python (`struct`, `socket`, `ipaddress`, `hashlib`, `heapq`); `networkx` appears only as a cross-check in three tests (Dijkstra, Bellman-Ford, path-vector hop counts). No network access at test time: the socket tests run client and server on `127.0.0.1` in threads, `dns.py --live` is the only thing that talks to the outside and is never called by tests.

Every module's docstring names the RFC sections it implements; every module runs as a script with a demo; every module has a test against an RFC's printed numbers or figures where the RFC prints any, otherwise against networkx, `ipaddress` or hand-built bytes (`headers`, `pcap`, `sockets_echo` on loopback, `tcp_sim` against the RFC 6298 formulas). `test_note_pointers.py` checks that every `module.name` pointer in the notes resolves.

Everything here is cited to a source in [`../refs/SOURCES.md`](../refs/SOURCES.md), and the RFCs it implements are vendored in `../refs/rfc/`.

```
# from the course folder, repo venv (`uv sync` at the repo root)
uv run pytest src -q         # 144 tests, < 2 s
uv run pytest src/py -q      # 117, the reference implementations
uv run python src/py/<module>.py       # each module has a demo
bash src/sh/tools_cheatsheet.sh           # dry run, no root
```

`exercises/` is the other half and is **not ours**: worked
solutions to free practice material from **other institutions**, because
191.030 publishes none of its own [S1], [S2]. See
[`exercises/README.md`](exercises/README.md) — and note that every file there
names the institution, course, year and licence it came from.

| directory | source | licence | tests |
|---|---|---|---|
| `exercises/mit-6.02-2012/` | MIT 6.02 *Introduction to EECS II*, Fall 2012, OCW [S34] | CC BY-NC-SA 4.0 | 16, each asserting against a number **MIT published** |
| `exercises/uclouvain-cnp3-2019/` | CNP3, Bonaventure, UCLouvain [S35] | CC BY-SA 3.0 | 11 — CNP3 publishes no answers, so these check the mechanism |

| File | Note | What |
|---|---|---|
| `py/inet_checksum.py` | 03, 05 | The Internet checksum (RFC 1071 §1), the §2–§3 sum variants (`ones_sum`, `ones_sum32`, `ones_sum_split`: normal, 32-bit, odd-offset split) and the incremental update after a one-word change (RFC 1624 eq. 3, the equation RFC 1141 got wrong). Re-exported by `headers.py` |
| `py/headers.py` | 02–05 | Build and parse Ethernet (+802.1Q), ARP, IPv4 (checksum verification, fragmentation/reassembly), IPv6, UDP, TCP (options); `pseudo_header` for the v4 and v6 transport checksums; `parse_frame`, `summarize` (tcpdump-style line) |
| `py/pcap.py` | 11 | Classic libpcap reader/writer (both byte orders, ns timestamps); `synthetic_trace()` = ARP + TCP handshake/HTTP/teardown + UDP |
| `py/subnet.py` | 03, 04, 06, 09 | CIDR maths, fixed-length and VLSM subnetting, pure aggregation, `ForwardingTable` with longest-prefix match (v4/v6); IPv6 text forms (`parse_ipv6`, `ipv6_prefix`, RFC 4291 §2.2–2.3; `ipv6_compress`, RFC 5952 §4); `solicited_node` (RFC 4291 §2.7.1); `multicast_mac` (RFC 1112 §6.4, RFC 2464 §7) |
| `py/linkstate.py` | 07 | Dijkstra (RFC 2328 §16.1), tabular trace (`dijkstra_trace`), routing table (first hops); Kurose–Ross example graph |
| `py/distvector.py` | 06, 07 | Distributed Bellman-Ford, count-to-infinity demo, split horizon, poisoned reverse |
| `py/pathvector.py` | 06, 07 | BGP-style path vector with withdrawals, AS-path loop rejection (RFC 4271 §9.1.2), `GaoRexford` valley-free policy hook |
| `py/tcp_sim.py` | 05, 11 | Event-driven TCP sender/receiver: seq/ack, cumulative ACKs, RFC 6298 RTO with backoff, slow start, AIMD, fast retransmit/recovery; scripted losses; prints a trace |
| `py/tcp_fsm.py` | 05, 11 | RFC 9293 §3.3.2 Figure 5 as a table (`TRANSITIONS`, plus notes 1–3 in `RST_EDGES`), two-peer `Endpoint` walks; `Segment` prints the RFC's `<SEQ=…><ACK=…><CTL=…>` notation; tests replay Figures 6, 7, 8, 12, 13 and note 05's scenario 1 |
| `py/ospf.py` | 07 | RFC 2328 made concrete: Appendix B architectural constants, Appendix C.3 **sample** values (and why they are not defaults), the §10.5 Hello-parameter match, and §13.1 "which LSA instance is newer" with the database that only accepts newer ones |
| `py/bgp_decision.py` | 06, 07 | RFC 4271 as specification: §9.1.1 degree of preference, the seven §9.1.2.2 tie-breaks applied in the mandated order with MED's same-neighbour-AS restriction, and every §10 timer default |
| `py/dnssec.py` | 08 | RFC 4034 key tag (App. B) and DS digest (§5.1.4) — the course's one published test vector |
| `py/dns.py` | 08 | RFC 1035 messages: `encode_name` with §2.3.4 limits and §4.1.4 suffix compression, query (EDNS0 DO), response, parser for A/AAAA/NS/CNAME/MX/TXT/OPT; tests rebuild §4.1.4's figure and a hand-written packet; `--live` sends a real query |
| `py/sockets_echo.py` | 10 | TCP and UDP echo server/client with 16-bit length-prefixed framing; `recv_exact`; loopback only |
| `py/telnet_client_sketch.py` | 08, 10 | Telnet IAC stream parsing (WILL/WONT/DO/DONT, SB…SE, IAC IAC), RFC 1143 §7 `QOption` state machine, refuse-by-default `Negotiator`/`negotiate` |
| `py/test_note_pointers.py` | all | every backticked `module.name`, `file.py::name`, script path and relative link in the notes and READMEs resolves |
| `sh/tools_cheatsheet.sh` | 11 | Annotated `ip`/`ifconfig`/`ss`/`netstat`, `dig`, `traceroute`, `tcpdump`/`tshark` filters, `nc`; `--dry-run` (default) prints, `--run <section>` executes, root-only sections are skipped when not root |

Tests are `py/test_<module>.py`; header tests use hand-built byte strings (a 42-byte ARP frame, an IPv4 header checksummed by hand) rather than comparing the code against itself.

`py/test_rfc_vectors.py` is the cross-cutting one and the most useful: **20 tests that each name an RFC and a section and reproduce a number that RFC prints.** 191.030 has no past papers and no lecturer's worked examples ([S2], [S5] in [`../refs/SOURCES.md`](../refs/SOURCES.md)), so the standards are the substitute for "check the code against the numbers the course published". What it pins:

| RFC § | the published number |
|---|---|
| 1071 §3 | the worked sums of `0001 f203 f4f5 f6f7`: `2ddf0` → `ddf2`, swapped `f2dd`, 32-bit `1ddf1` → `ddf2`, odd split `f201` + swap(`f0eb`); checksum `0x220d` = ~`ddf2` (derived, not printed) |
| 1624 §4 | m `0x5555` → `0x3285`, rest `0xCD7A`: HC `0xDD2F`, HC' `0x0000`, **and** RFC 1141's wrong `0xFFFF` |
| 4034 §5.4 | `dskey.example.com.` → key tag **60485**, DS SHA-1 **2BB183AF5F22588179A53B0A98631FAD1A292118** |
| 2328 App. B | every architectural constant |
| 2328 App. C.3 | that 10/40 is a *sample × 4*, by deriving it from the two sentences |
| 2328 §13.1 | every branch of the LSA-freshness comparison, including the signed sequence number and the MaxAgeDiff window |
| 4271 §10 | all six timer defaults and the jitter range |
| 4271 §9.1.1 / §9.1.2.2 | that LOCAL_PREF acts *before* tie-breaking, and steps a–g in order |

Outside that file, the RFCs' printed figures are replayed by `test_tcp_fsm.py` (RFC 9293 Figures 6, 7, 8, 12, 13), `test_dns.py` (RFC 1035 §4.1.4), `test_subnet.py` (RFC 1918 §3, RFC 4291 §2.3, RFC 5952 §4, RFC 1112 §6.4) and `test_telnet_client_sketch.py` (RFC 854's code table read from the vendored text, RFC 1143 §7's receipt tables).

That is still the only *published* answer key for the protocol constants. For
worked problems there is now a second one, from outside the course:
`exercises/mit-6.02-2012/` reproduces the answers
MIT printed for its own routing and transport tutorials, and
[`../notes/12-substitute-practice-set.md`](../notes/12-substitute-practice-set.md)
collects the whole practice set — 22 problems, each tagged with whose it is.
