"""IPv4/IPv6 prefix arithmetic and longest-prefix-match forwarding (notes 03, 04, 06, 09).

What it implements, by RFC section (all vendored in ../../refs/rfc/):

* RFC 1122 section 3.3.1.1, the local/remote decision: `same_subnet`,
  `network_info` (address AND mask).  RFC 3021: the /31 case.  RFC 1918
  section 3: the private blocks, used as test vectors.
* RFC 4291 section 2.2 (text forms, `::`) and 2.3 (prefix notation, including
  its worked 2001:0DB8:0:CD30::/60 example): `parse_ipv6`, `ipv6_prefix`.
* RFC 5952 section 4 (canonical text: no leading zeros, `::` for the longest
  run of two or more zero groups, leftmost on a tie, lower case):
  `ipv6_compress`, tested on every example section 4 prints.
* RFC 4291 section 2.7.1 (solicited-node ff02::1:ff00:0/104): `solicited_node`.
* RFC 1112 section 6.4 (IPv4 group -> 01-00-5E + low 23 bits) and RFC 2464
  section 7 (IPv6 group -> 33-33 + low 32 bits): `multicast_mac`.
* Longest-prefix match (`ForwardingTable`) and aggregation
  (`summarize_prefixes`).  The forwarding rule itself is RFC 1812 section
  5.2.4.3 and CIDR is RFC 4632; neither is vendored here, so those two are
  checked against `ipaddress` rather than against RFC text.

Everything is done on integers so the bit manipulation is visible; the
`ipaddress` module is used for IPv4 parsing/printing and as the cross-check in
tests.
"""
import ipaddress


# ---------------------------------------------------------------- CIDR maths
def mask_from_prefix(prefix, bits=32):
    """/24 -> 0xFFFFFF00: `prefix` ones followed by zeros."""
    return ((1 << prefix) - 1) << (bits - prefix) if prefix else 0


def prefix_from_mask(mask):
    """255.255.255.0 -> 24.  Rejects non-contiguous masks."""
    m = int(ipaddress.IPv4Address(mask))
    prefix = bin(m).count("1")
    if m != mask_from_prefix(prefix):
        raise ValueError(f"non-contiguous mask {mask}")
    return prefix


def network_info(cidr):
    """Network, broadcast, first/last usable host, host count for an IPv4 CIDR.
    /31 (RFC 3021) has two usable addresses and no broadcast; /32 is one host."""
    ip, prefix = cidr.split("/")
    prefix = int(prefix)
    a = int(ipaddress.IPv4Address(ip))
    mask = mask_from_prefix(prefix)
    net = a & mask
    bcast = net | (~mask & 0xFFFFFFFF)
    if prefix >= 31:
        first, last, hosts = net, bcast, 2 if prefix == 31 else 1
    else:
        first, last, hosts = net + 1, bcast - 1, 2 ** (32 - prefix) - 2
    s = lambda x: str(ipaddress.IPv4Address(x))
    return {"network": s(net), "prefix": prefix, "mask": s(mask), "broadcast": s(bcast),
            "first_host": s(first), "last_host": s(last), "hosts": hosts,
            "wildcard": s(~mask & 0xFFFFFFFF)}


def same_subnet(a, b, prefix):
    return (int(ipaddress.ip_address(a)) >> (32 - prefix)) == (int(ipaddress.ip_address(b)) >> (32 - prefix))


def split_subnet(cidr, new_prefix):
    """Split a block into equal subnets of length new_prefix (fixed-length subnetting)."""
    net = ipaddress.ip_network(cidr, strict=False)
    if new_prefix < net.prefixlen:
        raise ValueError("new prefix must be longer")
    step = 1 << (net.max_prefixlen - new_prefix)
    base = int(net.network_address)
    return [f"{ipaddress.ip_address(base + i * step)}/{new_prefix}"
            for i in range(2 ** (new_prefix - net.prefixlen))]


def vlsm(cidr, host_counts):
    """Variable-length subnetting: allocate the largest requirements first so
    every block starts on its own natural boundary.  Returns (need, cidr) pairs."""
    net = ipaddress.ip_network(cidr, strict=False)
    cursor, end = int(net.network_address), int(net.broadcast_address) + 1
    out = []
    for need in sorted(host_counts, reverse=True):
        size = 4                         # smallest block with >= 2 usable hosts
        while size - 2 < need:
            size *= 2
        if cursor + size > end:
            raise ValueError("block exhausted")
        out.append((need, f"{ipaddress.ip_address(cursor)}/{32 - size.bit_length() + 1}"))
        cursor += size
    return out


def summarize_prefixes(cidrs):
    """Route aggregation (supernetting), pure: repeat until nothing changes
    (1) drop every prefix covered by a shorter one, (2) merge two siblings
    (same length, differing only in the last prefix bit) into their parent.
    The test cross-checks `ipaddress.collapse_addresses`."""
    nets = [ipaddress.ip_network(c) for c in cidrs]
    bits = nets[0].max_prefixlen if nets else 32
    cls = type(nets[0]) if nets else ipaddress.IPv4Network
    s = {(int(n.network_address), n.prefixlen) for n in nets}
    changed = True
    while changed:
        changed = False
        for a, p in sorted(s, key=lambda e: e[1]):
            covered = any(q < p and a >> (bits - q) == b >> (bits - q) for b, q in s)
            if covered:
                s.discard((a, p))
                changed = True
        for a, p in sorted(s, key=lambda e: -e[1]):
            bit = 1 << (bits - p) if p else 0
            if p and (a, p) in s and (a ^ bit, p) in s:
                s -= {(a, p), (a ^ bit, p)}
                s.add((a & ~bit, p - 1))
                changed = True
    return [str(cls((a, p))) for a, p in sorted(s)]


# ---------------------------------------------------------------- IPv6 text forms
def parse_ipv6(text):
    """RFC 4291 section 2.2 -> 128-bit int: eight hex groups, at most one `::`,
    optionally a dotted IPv4 tail (form 3).  Case-insensitive."""
    head, dbl, tail = text.lower().partition("::")
    if "::" in tail:
        raise ValueError("'::' may appear only once")

    def groups(part):
        if not part:
            return []
        out = part.split(":")
        if "." in out[-1]:                               # x:x:x:x:x:x:d.d.d.d
            v4 = int(ipaddress.IPv4Address(out.pop()))
            out += [f"{v4 >> 16:x}", f"{v4 & 0xFFFF:x}"]
        if any(not g or len(g) > 4 for g in out):
            raise ValueError(f"bad group in {text!r}")
        return [int(g, 16) for g in out]
    h, t = groups(head), groups(tail)
    fill = 8 - len(h) - len(t)
    if (dbl and fill < 1) or (not dbl and fill != 0):
        raise ValueError(f"{text!r} does not have eight groups")
    value = 0
    for g in h + [0] * fill + t:
        value = (value << 16) | g
    return value


def ipv6_prefix(text):
    """'addr/len' -> (network int, len) with the host bits cleared (RFC 4291 section 2.3)."""
    addr, plen = text.split("/")
    plen = int(plen)
    return parse_ipv6(addr) & mask_from_prefix(plen, 128), plen


def ipv6_compress(value):
    """RFC 5952 section 4 canonical text for a 128-bit int (or any legal text form)."""
    if isinstance(value, str):
        value = parse_ipv6(value)
    g = [(value >> (112 - 16 * i)) & 0xFFFF for i in range(8)]
    best, run = (0, 0), None                       # (start, length) of the longest zero run
    for i, x in enumerate(g + [1]):
        if x == 0 and run is None:
            run = i
        elif x != 0 and run is not None:
            if i - run > best[1]:                  # strict '>' keeps the leftmost on a tie
                best = (run, i - run)
            run = None
    hexes = [f"{x:x}" for x in g]                  # 4.1 no leading zeros, 4.3 lower case
    start, n = best
    if n < 2:                                      # 4.2.2 never '::' for one group
        return ":".join(hexes)
    return ":".join(hexes[:start]) + "::" + ":".join(hexes[start + n:])


def solicited_node(addr):
    """RFC 4291 section 2.7.1: ff02:0:0:0:0:1:ff00::/104 + the low 24 bits."""
    return ipv6_compress(parse_ipv6("ff02::1:ff00:0") | (parse_ipv6(addr) & 0xFFFFFF))


def multicast_mac(group):
    """Ethernet destination of an IP multicast group.
    IPv4, RFC 1112 section 6.4: 01-00-5E-00-00-00 + the low 23 bits, so the 5
    high-order bits of the 28-bit group ID are lost and 2^5 = 32 groups share
    one MAC.  IPv6, RFC 2464 section 7: 33-33 + the last four octets."""
    if ":" in group:
        a = parse_ipv6(group)
        if a >> 120 != 0xFF:
            raise ValueError("not an IPv6 multicast address (ff00::/8)")
        mac = 0x3333_0000_0000 | (a & 0xFFFF_FFFF)
    else:
        a = int(ipaddress.IPv4Address(group))
        if a >> 28 != 0b1110:
            raise ValueError("not an IPv4 host group (224.0.0.0/4)")
        mac = 0x0100_5E00_0000 | (a & 0x7F_FFFF)
    return ":".join(f"{(mac >> s) & 0xFF:02x}" for s in range(40, -1, -8))


# ---------------------------------------------------------------- forwarding table
class ForwardingTable:
    """Longest-prefix-match lookup.  Entries are (network_int, prefix, next_hop, iface).
    Lookup is linear over prefixes sorted longest-first; real routers use a
    trie/TCAM but the semantics are identical."""

    def __init__(self, version=4):
        self.bits = 32 if version == 4 else 128
        self.entries = []

    def add(self, cidr, next_hop, iface):
        net = ipaddress.ip_network(cidr, strict=False)
        self.entries.append((int(net.network_address), net.prefixlen, next_hop, iface))
        self.entries.sort(key=lambda e: -e[1])       # longest prefix first
        return self

    def lookup(self, dst):
        d = int(ipaddress.ip_address(dst))
        for net, plen, nh, iface in self.entries:
            if (d >> (self.bits - plen)) == (net >> (self.bits - plen)) if plen else True:
                return {"prefix": f"{ipaddress.ip_address(net)}/{plen}",
                        "next_hop": nh, "iface": iface}
        return None

    def __str__(self):
        rows = [f"{ipaddress.ip_address(n)}/{p:<4} via {nh or 'direct':<15} dev {i}"
                for n, p, nh, i in self.entries]
        return "\n".join(rows)


def demo_table():
    t = ForwardingTable()
    t.add("0.0.0.0/0", "192.0.2.1", "eth0")          # default route
    t.add("10.0.0.0/8", "10.1.1.1", "eth1")
    t.add("10.1.0.0/16", "10.1.1.2", "eth1")
    t.add("10.1.2.0/24", None, "eth2")               # directly connected
    t.add("10.1.2.7/32", "10.1.2.7", "eth2")         # host route
    return t


if __name__ == "__main__":
    print(network_info("192.168.13.77/26"))
    print(split_subnet("192.168.0.0/24", 26))
    print(vlsm("10.0.0.0/24", [60, 25, 10, 2]))
    t = demo_table()
    print(t)
    for d in ["10.1.2.7", "10.1.2.9", "10.1.9.9", "10.9.9.9", "8.8.8.8"]:
        print(d, "->", t.lookup(d))
    print(summarize_prefixes(["203.0.113.0/26", "203.0.113.128/26", "203.0.113.192/26"]))
    for a in ["2001:0db8:0000:0000:0001:0000:0000:0001", "2001:0db8:0000:0000:0000:ff00:0042:8329"]:
        print(a, "->", ipv6_compress(a), " solicited-node", solicited_node(a),
              " MAC", multicast_mac(solicited_node(a)))
    for g in ["224.0.0.5", "239.128.0.5"]:
        print(g, "->", multicast_mac(g))
