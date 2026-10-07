"""Layer 2-4 header parsing and building (notes 02-05).

Pure `struct`; every builder returns bytes and every parser returns a dict so
the field names double as a header cheat sheet.  Field order and widths follow
RFC 826 "Packet format" (ARP), RFC 791 section 3.1 (IPv4; fragmentation per
section 3.2's example procedure), RFC 8200 section 3 (IPv6) and 8.1 (its
pseudo-header), RFC 768 (UDP), RFC 9293 section 3.1 (TCP) and 3.7.1 (MSS).
Ethernet and 802.1Q are IEEE 802.3/802.1Q, not RFCs, and not vendored.

The Internet checksum itself lives in `inet_checksum.py` (RFC 1071 and RFC
1624); it is re-exported here so `parse_frame` and friends read as one module.
"""
import struct
import ipaddress

from inet_checksum import checksum, incremental_checksum_update  # noqa: F401  (re-exported)

ETH_P_IP, ETH_P_ARP, ETH_P_IPV6 = 0x0800, 0x0806, 0x86DD
IPPROTO_ICMP, IPPROTO_TCP, IPPROTO_UDP, IPPROTO_ICMPV6 = 1, 6, 17, 58
TCP_FLAGS = ["FIN", "SYN", "RST", "PSH", "ACK", "URG", "ECE", "CWR"]  # bit 0..7


# ---------------------------------------------------------------- helpers
def mac_to_bytes(mac):
    return bytes(int(b, 16) for b in mac.split(":"))


def bytes_to_mac(b):
    return ":".join(f"{x:02x}" for x in b)


def flags_to_str(flags):
    return "|".join(n for i, n in enumerate(TCP_FLAGS) if flags & (1 << i)) or "-"


def flags_from_str(s):
    return sum(1 << TCP_FLAGS.index(n) for n in s.split("|") if n)


# ---------------------------------------------------------------- Ethernet II
def build_ethernet(dst, src, ethertype, payload=b""):
    return mac_to_bytes(dst) + mac_to_bytes(src) + struct.pack("!H", ethertype) + payload


def parse_ethernet(frame):
    """14-byte header: dst(6) src(6) type(2).  No VLAN tag handling except
    recognising 0x8100 and skipping the 4-byte 802.1Q tag."""
    dst, src, etype = frame[:6], frame[6:12], struct.unpack("!H", frame[12:14])[0]
    off, vlan = 14, None
    if etype == 0x8100:
        tci, etype = struct.unpack("!HH", frame[14:18])
        vlan, off = tci & 0x0FFF, 18
    return {"dst": bytes_to_mac(dst), "src": bytes_to_mac(src), "type": etype,
            "vlan": vlan, "payload": frame[off:]}


# ---------------------------------------------------------------- ARP (Ethernet/IPv4)
def build_arp(op, sha, spa, tha, tpa):
    """op 1 = request, 2 = reply.  htype 1 (Ethernet), ptype 0x0800, hlen 6, plen 4."""
    return (struct.pack("!HHBBH", 1, ETH_P_IP, 6, 4, op) + mac_to_bytes(sha)
            + ipaddress.IPv4Address(spa).packed + mac_to_bytes(tha)
            + ipaddress.IPv4Address(tpa).packed)


def parse_arp(data):
    htype, ptype, hlen, plen, op = struct.unpack("!HHBBH", data[:8])
    p = 8
    sha, spa = data[p:p + hlen], data[p + hlen:p + hlen + plen]
    p += hlen + plen
    tha, tpa = data[p:p + hlen], data[p + hlen:p + hlen + plen]
    return {"htype": htype, "ptype": ptype, "op": op,
            "sha": bytes_to_mac(sha), "spa": str(ipaddress.IPv4Address(spa)),
            "tha": bytes_to_mac(tha), "tpa": str(ipaddress.IPv4Address(tpa))}


# ---------------------------------------------------------------- IPv4
def build_ipv4(src, dst, proto, payload=b"", ttl=64, ident=0, flags=0, frag_off=0,
               tos=0, options=b""):
    """Header checksum is computed over the header only (payload excluded)."""
    assert len(options) % 4 == 0
    ihl = 5 + len(options) // 4
    total = ihl * 4 + len(payload)
    hdr = struct.pack("!BBHHHBBH4s4s", (4 << 4) | ihl, tos, total, ident,
                      (flags << 13) | frag_off, ttl, proto, 0,
                      ipaddress.IPv4Address(src).packed, ipaddress.IPv4Address(dst).packed)
    hdr += options
    hdr = hdr[:10] + struct.pack("!H", checksum(hdr)) + hdr[12:]
    return hdr + payload


def parse_ipv4(data):
    vihl, tos, total, ident, ff, ttl, proto, csum, src, dst = struct.unpack(
        "!BBHHHBBH4s4s", data[:20])
    ihl = (vihl & 0x0F) * 4
    return {"version": vihl >> 4, "ihl": ihl, "tos": tos, "total_length": total,
            "id": ident, "flags": ff >> 13, "df": bool(ff & 0x4000),
            "mf": bool(ff & 0x2000), "frag_offset": ff & 0x1FFF, "ttl": ttl,
            "proto": proto, "checksum": csum, "checksum_ok": checksum(data[:ihl]) == 0,
            "src": str(ipaddress.IPv4Address(src)), "dst": str(ipaddress.IPv4Address(dst)),
            "options": data[20:ihl], "payload": data[ihl:total]}


def fragment_ipv4(packet, mtu):
    """Split an IPv4 packet into fragments that fit `mtu` (header + payload).
    Fragment payload sizes must be multiples of 8 except for the last piece;
    the offset field counts 8-byte units.  Options are not copied (simplified)."""
    h = parse_ipv4(packet)
    if h["total_length"] <= mtu:
        return [packet]
    if h["df"]:
        raise ValueError("DF set: cannot fragment (ICMP 'fragmentation needed')")
    chunk = (mtu - 20) // 8 * 8
    payload, out, off = h["payload"], [], 0
    while off < len(payload):
        piece = payload[off:off + chunk]
        last = off + chunk >= len(payload)
        out.append(build_ipv4(h["src"], h["dst"], h["proto"], piece, ttl=h["ttl"],
                              ident=h["id"], flags=0 if last else 1,
                              frag_off=h["frag_offset"] + off // 8))
        off += chunk
    return out


def reassemble_ipv4(fragments):
    frags = sorted((parse_ipv4(f) for f in fragments), key=lambda h: h["frag_offset"])
    payload = b"".join(h["payload"] for h in frags)
    h = frags[0]
    return build_ipv4(h["src"], h["dst"], h["proto"], payload, ttl=h["ttl"], ident=h["id"])


# ---------------------------------------------------------------- IPv6
def build_ipv6(src, dst, next_header, payload=b"", hop_limit=64, traffic_class=0,
               flow_label=0):
    vtf = (6 << 28) | (traffic_class << 20) | flow_label
    return (struct.pack("!IHBB", vtf, len(payload), next_header, hop_limit)
            + ipaddress.IPv6Address(src).packed + ipaddress.IPv6Address(dst).packed + payload)


def parse_ipv6(data):
    """Fixed 40-byte header, no checksum; length field counts the payload only."""
    vtf, plen, nh, hl = struct.unpack("!IHBB", data[:8])
    return {"version": vtf >> 28, "traffic_class": (vtf >> 20) & 0xFF,
            "flow_label": vtf & 0xFFFFF, "payload_length": plen, "next_header": nh,
            "hop_limit": hl, "src": str(ipaddress.IPv6Address(data[8:24])),
            "dst": str(ipaddress.IPv6Address(data[24:40])), "payload": data[40:40 + plen]}


# ---------------------------------------------------------------- pseudo header
def pseudo_header(src, dst, proto, length):
    """Prepended to UDP/TCP for checksumming so a packet delivered to the
    wrong host/protocol fails the check.  IPv4: 12 bytes; IPv6: 40 bytes."""
    s, d = ipaddress.ip_address(src), ipaddress.ip_address(dst)
    if s.version == 4:
        return s.packed + d.packed + struct.pack("!BBH", 0, proto, length)
    return s.packed + d.packed + struct.pack("!IHBB", length, 0, 0, proto)


# ---------------------------------------------------------------- UDP
def build_udp(src, dst, sport, dport, payload=b""):
    length = 8 + len(payload)
    hdr = struct.pack("!HHHH", sport, dport, length, 0)
    c = checksum(pseudo_header(src, dst, IPPROTO_UDP, length) + hdr + payload)
    c = c or 0xFFFF                     # 0 means "no checksum" in IPv4 UDP
    return hdr[:6] + struct.pack("!H", c) + payload


def parse_udp(data, src=None, dst=None):
    sport, dport, length, csum = struct.unpack("!HHHH", data[:8])
    out = {"sport": sport, "dport": dport, "length": length, "checksum": csum,
           "payload": data[8:length]}
    if src is not None and csum != 0:
        out["checksum_ok"] = checksum(pseudo_header(src, dst, IPPROTO_UDP, length)
                                      + data[:length]) == 0
    return out


# ---------------------------------------------------------------- TCP
def build_tcp(src, dst, sport, dport, seq, ack, flags, window=65535, payload=b"",
              options=b"", urgent=0):
    """flags may be an int bitmask or a string like 'SYN|ACK'."""
    if isinstance(flags, str):
        flags = flags_from_str(flags)
    assert len(options) % 4 == 0
    doff = 5 + len(options) // 4
    hdr = struct.pack("!HHIIBBHHH", sport, dport, seq, ack, doff << 4, flags,
                      window, 0, urgent) + options
    c = checksum(pseudo_header(src, dst, IPPROTO_TCP, len(hdr) + len(payload)) + hdr + payload)
    return hdr[:16] + struct.pack("!H", c) + hdr[18:] + payload


def parse_tcp(data, src=None, dst=None):
    sport, dport, seq, ack, doff, flags, win, csum, urg = struct.unpack("!HHIIBBHHH", data[:20])
    doff = (doff >> 4) * 4
    out = {"sport": sport, "dport": dport, "seq": seq, "ack": ack, "data_offset": doff,
           "flags": flags, "flags_str": flags_to_str(flags), "window": win,
           "checksum": csum, "urgent": urg, "options": parse_tcp_options(data[20:doff]),
           "payload": data[doff:]}
    if src is not None:
        out["checksum_ok"] = checksum(pseudo_header(src, dst, IPPROTO_TCP, len(data)) + data) == 0
    return out


def parse_tcp_options(raw):
    """Kind 0 = end, 1 = NOP (1 byte); everything else is kind, len, data."""
    opts, i = [], 0
    while i < len(raw):
        kind = raw[i]
        if kind == 0:
            break
        if kind == 1:
            opts.append(("NOP", b""))
            i += 1
            continue
        ln = raw[i + 1]
        val = raw[i + 2:i + ln]
        name = {2: "MSS", 3: "WSCALE", 4: "SACK_OK", 8: "TIMESTAMP"}.get(kind, f"opt{kind}")
        if name == "MSS":
            val = struct.unpack("!H", val)[0]
        elif name == "WSCALE":
            val = val[0]
        opts.append((name, val))
        i += ln
    return opts


def tcp_option_mss(mss):
    return struct.pack("!BBH", 2, 4, mss)


# ---------------------------------------------------------------- whole frame
def parse_frame(frame):
    """Decode Ethernet -> ARP / IPv4 / IPv6 -> UDP / TCP; returns a list of
    layer dicts, innermost last (what tshark prints as the protocol stack)."""
    eth = parse_ethernet(frame)
    layers = [("eth", eth)]
    if eth["type"] == ETH_P_ARP:
        layers.append(("arp", parse_arp(eth["payload"])))
        return layers
    if eth["type"] == ETH_P_IP:
        ip = parse_ipv4(eth["payload"])
        proto = ip["proto"]
        layers.append(("ipv4", ip))
        if ip["mf"] or ip["frag_offset"]:
            return layers
    elif eth["type"] == ETH_P_IPV6:
        ip = parse_ipv6(eth["payload"])
        proto = ip["next_header"]
        layers.append(("ipv6", ip))
    else:
        return layers
    if proto == IPPROTO_UDP:
        layers.append(("udp", parse_udp(ip["payload"], ip["src"], ip["dst"])))
    elif proto == IPPROTO_TCP:
        layers.append(("tcp", parse_tcp(ip["payload"], ip["src"], ip["dst"])))
    return layers


def summarize(frame):
    """One-line tcpdump-style summary."""
    layers = dict(parse_frame(frame))
    if "arp" in layers:
        a = layers["arp"]
        return (f"ARP who-has {a['tpa']} tell {a['spa']}" if a["op"] == 1
                else f"ARP {a['spa']} is-at {a['sha']}")
    ip = layers.get("ipv4") or layers.get("ipv6")
    if ip is None:
        return f"ETH type 0x{layers['eth']['type']:04x}"
    if "tcp" in layers:
        t = layers["tcp"]
        return (f"TCP {ip['src']}:{t['sport']} > {ip['dst']}:{t['dport']} [{t['flags_str']}] "
                f"seq={t['seq']} ack={t['ack']} win={t['window']} len={len(t['payload'])}")
    if "udp" in layers:
        u = layers["udp"]
        return f"UDP {ip['src']}:{u['sport']} > {ip['dst']}:{u['dport']} len={len(u['payload'])}"
    return f"IP {ip['src']} > {ip['dst']} proto={ip.get('proto', ip.get('next_header'))}"


if __name__ == "__main__":
    syn = build_tcp("10.0.0.1", "10.0.0.2", 40000, 80, 1000, 0, "SYN", options=tcp_option_mss(1460))
    pkt = build_ipv4("10.0.0.1", "10.0.0.2", IPPROTO_TCP, syn)
    frame = build_ethernet("aa:bb:cc:dd:ee:ff", "00:11:22:33:44:55", ETH_P_IP, pkt)
    print(frame.hex())
    print(summarize(frame))
    for name, layer in parse_frame(frame):
        print(name, {k: v for k, v in layer.items() if k != "payload"})
