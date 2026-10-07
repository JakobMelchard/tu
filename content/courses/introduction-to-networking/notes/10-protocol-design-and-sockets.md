# 10 Protocol design and socket programming

> **Sourcing.** No RFC tells you how to design a protocol, so this note's
> checklist is drawn from the vendored ones as worked examples — Telnet
> (RFC 854/855/1143) for in-band signalling and negotiation, DNS (RFC 1035,
> 6891) for a compact binary request/response that had to be extended twenty
> years later, TCP (RFC 9293) for stream framing, Happy Eyeballs (RFC 8305) for
> connection racing [S16], [S15] — plus the standard textbook treatment [S25].
> Each row names the protocol it is drawn from. The subject list's last outcome
> is "**Design rudimentary network protocols for a given use-case**" [S1], so
> this note is examinable as a *skill*, not as recall.

## Designing a protocol: the checklist

A protocol is (1) a **message syntax** (byte layout or grammar), (2) **semantics** (what each message means), (3) **timing and state** (who may send what when, timeouts). Decisions the exam expects you to make explicitly, with a reason:

| Decision | Options | Trade-off |
|---|---|---|
| Transport | TCP (stream, reliable, ordered, congestion controlled, connection setup 1 RTT) vs UDP (datagrams, no guarantees, no setup, multicast possible) | request/response with tiny payloads and loss tolerance → UDP (DNS, NTP); anything with sessions, large data, or where you would otherwise re-implement retransmission → TCP; real-time media → UDP + RTP, drop rather than wait; QUIC = UDP + TLS + streams |
| **Framing** (message boundaries on a stream) | length prefix; delimiter (`\r\n`, with escaping); fixed size; self-describing (TLV: type, length, value) | length prefix: simple, binary-safe, needs a max length; delimiters: human-readable, must escape the delimiter in data (Telnet's IAC IAC); TLV: extensible, skip unknown types |
| Encoding | text (HTTP/1, SMTP: debuggable with nc) vs binary (DNS, TCP: compact, needs a spec); byte order **network = big-endian**; explicit field widths | text is easier to get wrong (parsing ambiguities, injection); binary needs `struct`-style packing; never send native structs (padding, endianness). DNS goes further and *compresses* names with backward pointers (RFC 1035 §4.1.4 [S16]) — cheap on the wire, and a decoder that omits the loop guard hangs |
| **State** | stateless request/response (HTTP/1 nominally, DNS) vs stateful sessions (TCP, Telnet options, FTP) | stateless scales and survives crashes; stateful needs timeouts, cleanup, and a state machine for every peer — draw it, enumerate every (state, event) pair |
| Identification | request IDs to match responses (DNS ID, RPC XID), sequence numbers for ordering/duplicates | mandatory over UDP; useful for pipelining over TCP |
| **Error handling** | error codes in the header (HTTP status, DNS RCODE, ICMP type/code); what to do on malformed input (drop, reset, error reply); timeouts and retry with backoff; idempotency of retried operations | "be liberal in what you accept" is dangerous: define exactly what is invalid and reject it; never trust the length field beyond your buffer; keep error replies smaller than requests (amplification) |
| **Versioning / extensibility** | version field (IP), capability negotiation (Telnet options, TLS cipher suites, HTTP `Upgrade`), reserved bits that must be zero and ignored, TLV for unknown options | plan for it in v1. DNS is the cautionary tale: RFC 1035 left no room, so **EDNS(0) had to smuggle new fields into a fake resource record** in the Additional section sixteen years later (RFC 6891 [S16]) — it works, but nobody would design it that way. Ossification: middleboxes freeze whatever is visible (why QUIC encrypts its headers) |
| Security | authentication, integrity, confidentiality: usually delegate to TLS/SSH; spoofing over UDP → cookies before doing work (SYN cookies, DTLS/QUIC retry) | design without security is a design decision you must justify |
| Flow/congestion | over UDP you must add windowing or rate limits yourself | over TCP you inherit them |

Reference design pattern: header with `magic/version | type | flags | length | id`, then a body; all integers big-endian and fixed width; a state machine per connection; timeouts on every wait.

## Sockets API (Berkeley sockets; Python's `socket` mirrors C)

| Step | TCP server | TCP client | UDP |
|---|---|---|---|
| create | `socket(AF_INET, SOCK_STREAM)` | same | `socket(AF_INET, SOCK_DGRAM)` |
| name | `bind((host, port))` (port 0 = OS picks; `SO_REUSEADDR` to rebind while TIME-WAIT) | implicit on connect | `bind` (server) or implicit |
| `listen(backlog)` | queue of completed handshakes | – | – |
| `accept()` → new socket per connection (blocks) | – | `connect((host, port))` = 3-way handshake | optional `connect` just fixes the peer |
| transfer | `recv(n)` returns **1..n bytes or b"" on FIN**; `send` may send fewer (`sendall` loops) | same | `sendto(data, addr)`, `recvfrom(n)` → one datagram (truncated if > n) |
| end | `close()` → FIN; `shutdown(SHUT_WR)` for half-close | | `close()` |

`AF_INET6` for IPv6 (`getaddrinfo` returns candidates for both; iterate them = Happy Eyeballs-lite). Address for a listener: `0.0.0.0`/`::` all interfaces, `127.0.0.1` loopback only.

**Blocking vs. non-blocking vs. multiplexing**: a blocking `recv` on socket A cannot notice data on B. Options: one thread/process per connection (simple, heavy), non-blocking sockets with `select`/`poll`/`epoll`/`kqueue` (`select.select([socks], [], [], timeout)` returns the readable ones; the classic event loop), or `asyncio` on top of that. A listening socket is "readable" when `accept` would not block. Timeouts: `settimeout(s)` raises `socket.timeout` — use it on every blocking call in a server.

Errors to expect: `ECONNREFUSED` (RST: nobody listens), `ETIMEDOUT` (SYN unanswered: filtered or host down), `ECONNRESET` (peer sent RST mid-connection), `EPIPE`/`BrokenPipe` (writing after the peer closed), `EADDRINUSE` (bind while TIME-WAIT, no `SO_REUSEADDR`).

## Worked mini-protocol: length-prefixed echo (`sockets_echo.py`)

Spec: message = `uint16 length (big-endian) || payload (length bytes)`; the server echoes each message (optionally transformed); the payload `QUIT` ends the session; max payload 65535.

```
client                         server
socket(); connect()   ---SYN--->  accept() (after listen)
send 00 05 "hello"    -------->  recv_exact(2) -> n=5; recv_exact(5) -> "hello"
                      <--------  send 00 05 "hello"
send 00 03 "abc" 00 02 "de"  -->  two messages, possibly in one segment: framing splits them
send 00 04 "QUIT"     -------->  close()  ---FIN--->
```

Why `recv_exact`: `recv(5)` may legally return 2 bytes (segment boundaries, Nagle, MSS, slow peer), and `recv` returning `b""` means the peer closed — treat a close in the middle of a message as a protocol error. Why a length and not `\n`: binary payloads may contain `\n`; the alternative is escaping (Telnet's IAC IAC). Why 16 bits: bounds memory per message; a hostile length of 4 GB with a 4-byte prefix must be rejected before allocation. The UDP variant keeps the prefix for symmetry but relies on datagram boundaries; one lost datagram = one lost message (the client would need an ID and retry).

Extension exercise: add a 1-byte type (0 echo, 1 upper, 2 error) and a version nibble; unknown type → error reply `type=2, payload=b"unknown type"`; unknown version → close. That is versioning and error handling in ten lines.

### Contrast: Telnet-style in-band signalling

Telnet mixes commands into the data stream with an escape byte (IAC = 0xFF, RFC 854 [S16]) and negotiates options with a per-option state machine (note 08). Pros: streaming, no length known in advance, human-typed. Cons: every data byte must be scanned, 0xFF must be doubled, and negotiation loops are a classic bug — **RFC 1143 exists solely to publish the state machine that avoids them** [S16], which is itself the lesson: if your protocol needs a whole RFC to explain how not to loop, the design has a problem. Length-prefixed framing has neither problem but cannot start sending before the length is known.

## Pitfalls

- TCP has no messages. `send(b"a"); send(b"b")` may arrive as `b"ab"`. Every TCP protocol needs framing.
- `recv` returning fewer bytes is not an error; `b""` is EOF.
- Byte order: `struct.pack("!H", n)` — the `!` is not optional.
- Forgetting `listen` before `accept`, or `bind`ing to `127.0.0.1` and wondering why other machines cannot connect.
- Over UDP, "the server did not answer" is indistinguishable from "the request was lost": design retries with IDs and make operations idempotent.
- A protocol without a version field cannot be changed without breaking old peers; one without a length limit cannot be implemented safely.

## Exam-style questions

1. *Design a protocol for a sensor sending a 16-byte reading every second to a collector; readings may be lost but must never be misattributed. Transport, framing, fields?* UDP (loss tolerable, no setup, low overhead); fixed-size datagram: `version(1) | sensor_id(4) | seq(4) | timestamp(4) | reading(16) | crc/auth tag` big-endian; seq detects loss/reordering; no ACKs; collector drops malformed or unauthenticated datagrams. TCP would add head-of-line blocking and connection state for no benefit.
2. *Why does DNS use UDP but fall back to TCP?* One small request/response fits a datagram, no handshake (1 RTT saved), server keeps no state; answers over the 512-byte limit of RFC 1035 §4.2.1 set TC and the client retries over TCP; EDNS(0) raises the limit by advertising a larger payload size in an OPT record (RFC 6891 §6.2) [S16]; zone transfers are always TCP. The cost of the choice is in note 08: no handshake means no return-routability check, hence spoofing and amplification.
3. *A server reads with `data = sock.recv(1024)` and parses `data` as one message. Give two ways this fails.* A message longer than 1024 or split across segments arrives in pieces (partial parse); two short messages sent back to back arrive in one `recv` (second one lost or misparsed). Fix: buffer and frame.
4. *What does `select` give you that threads do not, and vice versa?* `select`: one thread handles thousands of mostly idle sockets without per-connection stacks and locks; but a slow computation blocks everyone. Threads: blocking code stays simple and CPU work overlaps; but memory per thread and synchronisation.
5. *List three ways a protocol can be made extensible and one way each can go wrong.* Version field (peers with a higher version must know how to downgrade); TLV options (unknown types must be defined as ignorable or fatal); capability negotiation (loops or downgrade attacks if unauthenticated).

## Code

`src/py/sockets_echo.py`: `send_msg/recv_msg/recv_exact` (framing), `tcp_server/tcp_client`, `udp_server/udp_client`, `start_server` (thread + port 0). `test_sockets_echo.py` runs client and server on localhost, including coalesced writes and an early close. `src/py/telnet_client_sketch.py` for the in-band alternative; `src/py/dns.py` for a binary request/response protocol with IDs.
