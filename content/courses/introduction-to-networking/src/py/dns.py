"""DNS message encoder and decoder, RFC 1035 wire format (note 08).

RFC 1035 sections implemented:

* 2.3.4  size limits: label <= 63 octets, name <= 255 octets (`encode_name`).
* 3.2.2  TYPE values (`TYPES`); 3.4.1 A RDATA; RFC 3596 AAAA (not vendored).
* 4.1.1  header: ID, QR Opcode AA TC RD RA Z RCODE, four counts (`build_header`).
* 4.1.2  question, 4.1.3 resource record (`build_query`, `build_rr`, `parse_rr`).
* 4.1.4  message compression: a length byte with the top two bits 11 starts a
  14-bit pointer to an earlier offset.  `encode_name(..., table, offset)`
  compresses any suffix already written; `decode_name` follows pointers (only
  backwards, so a loop is impossible).  The test rebuilds the section's own
  F.ISI.ARPA / FOO.F.ISI.ARPA / ARPA example byte for byte.
* RFC 6891 sections 6.1.2-6.1.4: the OPT pseudo-RR, DO bit in the TTL field.

`--live` sends a real UDP query; tests and the default demo never do.
"""
import struct
import sys

TYPES = {1: "A", 2: "NS", 5: "CNAME", 6: "SOA", 12: "PTR", 15: "MX", 16: "TXT", 28: "AAAA",
         43: "DS", 46: "RRSIG", 47: "NSEC", 48: "DNSKEY", 50: "NSEC3"}
TYPE_BY_NAME = {v: k for k, v in TYPES.items()}
RCODES = {0: "NOERROR", 1: "FORMERR", 2: "SERVFAIL", 3: "NXDOMAIN", 5: "REFUSED"}


def encode_name(name, table=None, offset=0):
    """Name -> wire format.  With `table` (dict: lower-cased suffix -> offset,
    shared across one message) and the `offset` at which the name will be
    written, the longest suffix already in the message is replaced by a pointer
    and the new suffixes are recorded (RFC 1035 section 4.1.4)."""
    labels = [lb for lb in name.rstrip(".").split(".") if lb]
    if any(len(lb) > 63 for lb in labels):
        raise ValueError("label longer than 63 octets (RFC 1035 section 2.3.4)")
    if sum(len(lb) + 1 for lb in labels) + 1 > 255:
        raise ValueError("name longer than 255 octets (RFC 1035 section 2.3.4)")
    out = b""
    for i in range(len(labels)):
        suffix = ".".join(labels[i:]).lower()        # case-insensitive, section 2.3.3
        if table is not None and suffix in table:
            return out + struct.pack("!H", 0xC000 | table[suffix])
        if table is not None and offset + len(out) < 0x4000:
            table[suffix] = offset + len(out)
        out += bytes([len(labels[i])]) + labels[i].encode("ascii")
    return out + b"\x00"


def decode_name(msg, off):
    """Returns (name, offset after the name in the *original* position).
    Follows compression pointers but does not advance past them."""
    labels, jumped, end, jumps = [], False, None, 0
    while True:
        ln = msg[off]
        if ln & 0xC0 == 0xC0:                         # pointer
            ptr = struct.unpack("!H", msg[off:off + 2])[0] & 0x3FFF
            jumps += 1
            if ptr >= off or jumps > 16:              # RFC: pointers only go backwards
                raise ValueError("bad compression pointer (loop)")
            if not jumped:
                end = off + 2
            off, jumped = ptr, True
            continue
        off += 1
        if ln == 0:
            break
        labels.append(msg[off:off + ln].decode("ascii"))
        off += ln
    return ".".join(labels) + ".", (end if jumped else off)


def build_header(ident, qr=0, opcode=0, aa=0, tc=0, rd=1, ra=0, rcode=0, counts=(1, 0, 0, 0)):
    flags = (qr << 15) | (opcode << 11) | (aa << 10) | (tc << 9) | (rd << 8) | (ra << 7) | rcode
    return struct.pack("!HHHHHH", ident, flags, *counts)


def build_query(ident, name, qtype="A", rd=1, dnssec_ok=False):
    msg = build_header(ident, rd=rd, counts=(1, 0, 0, 1 if dnssec_ok else 0))
    msg += encode_name(name) + struct.pack("!HH", TYPE_BY_NAME[qtype], 1)
    if dnssec_ok:                                     # EDNS0 OPT RR with DO bit (RFC 6891)
        msg += b"\x00" + struct.pack("!HHIH", 41, 4096, 1 << 15, 0)
    return msg


def build_rr(name, rtype, rdata, ttl=300, rclass=1):
    return encode_name(name) + struct.pack("!HHIH", TYPE_BY_NAME[rtype], rclass, ttl, len(rdata)) + rdata


def build_response(query, answers, aa=0, rcode=0, ra=1):
    """answers: list of (name, type, rdata bytes, ttl).  The question is copied
    from the query and every owner name is compressed against the names already
    in the message, so an answer for the query name becomes the pointer c0 0c."""
    ident = struct.unpack("!H", query[:2])[0]
    qname, qend = decode_name(query, 12)
    rd = (struct.unpack("!H", query[2:4])[0] >> 8) & 1
    msg = build_header(ident, qr=1, aa=aa, rd=rd, ra=ra, rcode=rcode, counts=(1, len(answers), 0, 0))
    table = {}
    msg += encode_name(qname, table, len(msg)) + query[qend:qend + 4]
    for name, rtype, rdata, ttl in answers:
        msg += encode_name(name, table, len(msg))
        msg += struct.pack("!HHIH", TYPE_BY_NAME[rtype], 1, ttl, len(rdata)) + rdata
    return msg


def parse_message(msg):
    ident, flags, qd, an, ns, ar = struct.unpack("!HHHHHH", msg[:12])
    out = {"id": ident, "qr": flags >> 15, "opcode": (flags >> 11) & 0xF, "aa": (flags >> 10) & 1,
           "tc": (flags >> 9) & 1, "rd": (flags >> 8) & 1, "ra": (flags >> 7) & 1,
           "ad": (flags >> 5) & 1, "rcode": RCODES.get(flags & 0xF, flags & 0xF),
           "questions": [], "answers": [], "authority": [], "additional": []}
    off = 12
    for _ in range(qd):
        name, off = decode_name(msg, off)
        qtype, qclass = struct.unpack("!HH", msg[off:off + 4])
        off += 4
        out["questions"].append({"name": name, "type": TYPES.get(qtype, qtype), "class": qclass})
    for section, count in (("answers", an), ("authority", ns), ("additional", ar)):
        for _ in range(count):
            rr, off = parse_rr(msg, off)
            out[section].append(rr)
    return out


def parse_rr(msg, off):
    name, off = decode_name(msg, off)
    rtype, rclass, ttl, rdlen = struct.unpack("!HHIH", msg[off:off + 10])
    off += 10
    raw = msg[off:off + rdlen]
    tname = TYPES.get(rtype, rtype)
    if tname == "A":
        rdata = ".".join(str(b) for b in raw)
    elif tname == "AAAA":
        import ipaddress
        rdata = str(ipaddress.IPv6Address(raw))
    elif tname in ("NS", "CNAME", "PTR"):
        rdata = decode_name(msg, off)[0]
    elif tname == "MX":
        rdata = (struct.unpack("!H", raw[:2])[0], decode_name(msg, off + 2)[0])
    elif tname == "TXT":
        rdata = raw[1:1 + raw[0]].decode("ascii", "replace")
    elif rtype == 41:                                 # OPT pseudo-RR: class = UDP size, ttl = ext flags
        rdata = {"udp_size": rclass, "do": bool(ttl & 0x8000)}
    else:
        rdata = raw
    return {"name": name, "type": tname, "class": rclass, "ttl": ttl, "rdata": rdata}, off + rdlen


def live_query(name, qtype="A", server="1.1.1.1", timeout=3.0):
    import socket
    q = build_query(0x1234, name, qtype, dnssec_ok=True)
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.settimeout(timeout)
        s.sendto(q, (server, 53))
        data, _ = s.recvfrom(4096)
    return parse_message(data)


if __name__ == "__main__":
    if "--live" in sys.argv:
        args = [a for a in sys.argv[1:] if a != "--live"] or ["tuwien.ac.at"]
        print(live_query(*args))
    else:
        q = build_query(0xBEEF, "www.example.com", "A")
        print("query:", q.hex())
        # 203.0.113.10 is RFC 5737 documentation space.  Textbook examples use
        # 93.184.216.34 for example.com; that was no longer true when checked on
        # 2026-09-22 (refs/SOURCES.md S23).
        r = build_response(q, [("www.example.com.", "A", bytes([203, 0, 113, 10]), 3600)], aa=1)
        print("response:", r.hex())
        print(parse_message(r))
