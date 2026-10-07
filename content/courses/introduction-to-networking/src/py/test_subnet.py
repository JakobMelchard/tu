import ipaddress
import random
import pytest
from subnet import *


def test_masks():
    assert mask_from_prefix(24) == 0xFFFFFF00 and mask_from_prefix(0) == 0
    assert prefix_from_mask("255.255.255.192") == 26
    with pytest.raises(ValueError):
        prefix_from_mask("255.0.255.0")


def test_network_info_matches_ipaddress():
    info = network_info("192.168.13.77/26")
    n = ipaddress.ip_network("192.168.13.77/26", strict=False)
    assert info["network"] == str(n.network_address) == "192.168.13.64"
    assert info["broadcast"] == str(n.broadcast_address) == "192.168.13.127"
    assert info["first_host"] == "192.168.13.65" and info["last_host"] == "192.168.13.126"
    assert info["hosts"] == n.num_addresses - 2 == 62 and info["mask"] == "255.255.255.192"
    assert network_info("10.0.0.0/31")["hosts"] == 2 and network_info("10.0.0.9/32")["hosts"] == 1


def test_split_and_vlsm():
    assert split_subnet("192.168.0.0/24", 26) == ["192.168.0.0/26", "192.168.0.64/26",
                                                  "192.168.0.128/26", "192.168.0.192/26"]
    alloc = vlsm("10.0.0.0/24", [60, 25, 10, 2])
    assert alloc == [(60, "10.0.0.0/26"), (25, "10.0.0.64/27"), (10, "10.0.0.96/28"), (2, "10.0.0.112/30")]
    for need, c in alloc:
        assert ipaddress.ip_network(c).num_addresses - 2 >= need    # strict=True: on boundary
    assert same_subnet("10.1.2.3", "10.1.2.200", 24) and not same_subnet("10.1.2.3", "10.1.3.1", 24)


def test_aggregation():
    assert summarize_prefixes(["10.0.0.0/24", "10.0.1.0/24"]) == ["10.0.0.0/23"]
    assert summarize_prefixes(["10.0.1.0/24", "10.0.2.0/24"]) == ["10.0.1.0/24", "10.0.2.0/24"]
    # note 12 problem 6: four /26 collapse to one /24; drop the second and two remain
    quarters = [f"203.0.113.{i}/26" for i in (0, 64, 128, 192)]
    assert summarize_prefixes(quarters) == ["203.0.113.0/24"]
    assert summarize_prefixes(quarters[:1] + quarters[2:]) == ["203.0.113.0/26", "203.0.113.128/25"]
    assert summarize_prefixes(["10.0.0.0/8", "10.1.0.0/16"]) == ["10.0.0.0/8"]      # covered


def test_aggregation_matches_ipaddress_collapse():
    rng = random.Random(7)
    for _ in range(200):
        cidrs = {f"10.0.{rng.randrange(8)}.{rng.randrange(4) * 64}/{rng.choice([24, 25, 26])}"
                 for _ in range(rng.randrange(1, 9))}
        nets = [str(ipaddress.ip_network(c, strict=False)) for c in cidrs]
        ref = [str(n) for n in ipaddress.collapse_addresses(ipaddress.ip_network(c) for c in nets)]
        assert summarize_prefixes(nets) == ref
    assert summarize_prefixes(["2001:db8::/33", "2001:db8:8000::/33"]) == ["2001:db8::/32"]


def test_rfc1918_section3_blocks():
    """RFC 1918 section 3 prints the three ranges and describes the 172.16/12 block
    as 16 contiguous class B networks and 192.168/16 as 256 class C networks."""
    for cidr, first, last in [("10.0.0.0/8", "10.0.0.0", "10.255.255.255"),
                              ("172.16.0.0/12", "172.16.0.0", "172.31.255.255"),
                              ("192.168.0.0/16", "192.168.0.0", "192.168.255.255")]:
        info = network_info(cidr)
        assert (info["network"], info["broadcast"]) == (first, last)
    assert len(split_subnet("172.16.0.0/12", 16)) == 16
    assert len(split_subnet("192.168.0.0/16", 24)) == 256


def test_rfc4291_section23_prefix_notation():
    """The three legal spellings of the 60-bit prefix 20010DB80000CD3 agree; the
    'NOT legal' ones either do not parse or expand to a different address."""
    want = (0x20010DB80000CD30 << 64, 60)
    for legal in ("2001:0DB8:0000:CD30:0000:0000:0000:0000/60",
                  "2001:0DB8::CD30:0:0:0:0/60", "2001:0DB8:0:CD30::/60",
                  "2001:0DB8:0:CD30:123:4567:89AB:CDEF/60"):       # node address + /60
        assert ipv6_prefix(legal) == want
    with pytest.raises(ValueError):
        ipv6_prefix("2001:0DB8:0:CD3/60")                           # only four groups
    assert parse_ipv6("2001:0DB8::CD30") == 0x20010DB8 << 96 | 0xCD30
    assert parse_ipv6("2001:0DB8::CD3") == 0x20010DB8 << 96 | 0x0CD3
    assert ipv6_prefix("2001:0DB8::CD30/60") != want


def test_rfc5952_section4_examples():
    """Every example RFC 5952 section 4 prints, input -> the representation it requires."""
    cases = {"2001:0db8::0001": "2001:db8::1",                      # 4.1 leading zeros
             "2001:db8:0:0:0:0:2:1": "2001:db8::2:1",               # 4.2.1 shorten maximally
             "2001:db8::0:1": "2001:db8::1",                        # 4.2.1
             "2001:db8:0:1:1:1:1:1": "2001:db8:0:1:1:1:1:1",        # 4.2.2 not for one group
             "2001:0:0:1:0:0:0:1": "2001:0:0:1::1",                 # 4.2.3 longest run
             "2001:db8:0:0:1:0:0:1": "2001:db8::1:0:0:1",           # 4.2.3 leftmost on a tie
             "2001:DB8::ABCD": "2001:db8::abcd"}                    # 4.3 lower case
    for given, canonical in cases.items():
        assert ipv6_compress(given) == canonical
    rng = random.Random(1)
    for _ in range(500):          # zero-heavy random addresses against the stdlib
        v = 0
        for _ in range(8):
            v = (v << 16) | rng.choice([0, 0, 0, 1, 0xDB8, rng.randrange(1 << 16)])
        assert ipv6_compress(v) == str(ipaddress.IPv6Address(v))
        assert parse_ipv6(ipaddress.IPv6Address(v).exploded) == v
    assert ipv6_compress(0) == "::" and parse_ipv6("::ffff:192.0.2.1") == 0xFFFF_C000_0201


def test_solicited_node_and_multicast_mac():
    """RFC 4291 section 2.7.1, RFC 1112 section 6.4, RFC 2464 section 7; note 12
    problems 8 and 20."""
    assert solicited_node("2001:db8::ff00:42:8329") == "ff02::1:ff42:8329"
    assert multicast_mac("ff02::1:ff42:8329") == "33:33:ff:42:83:29"
    assert multicast_mac("224.0.0.5") == multicast_mac("239.128.0.5") == "01:00:5e:00:00:05"
    # 28-bit group ID, 23 bits kept: exactly 32 groups map to each MAC
    sharing = {ipaddress.IPv4Address(0xE000_0000 | hi << 23 | 5) for hi in range(32)}
    assert all(g in ipaddress.ip_network("224.0.0.0/4") for g in sharing) and len(sharing) == 32
    assert {multicast_mac(str(g)) for g in sharing} == {"01:00:5e:00:00:05"}
    assert multicast_mac("224.128.0.5") == "01:00:5e:00:00:05" != multicast_mac("224.0.0.6")
    for bad in ("192.0.2.1", "2001:db8::1"):
        with pytest.raises(ValueError):
            multicast_mac(bad)


def test_longest_prefix_match():
    t = demo_table()
    assert t.lookup("10.1.2.7")["prefix"] == "10.1.2.7/32"
    assert t.lookup("10.1.2.9")["iface"] == "eth2" and t.lookup("10.1.2.9")["next_hop"] is None
    assert t.lookup("10.1.9.9")["prefix"] == "10.1.0.0/16"
    assert t.lookup("10.9.9.9")["prefix"] == "10.0.0.0/8"
    assert t.lookup("8.8.8.8")["prefix"] == "0.0.0.0/0"
    assert ForwardingTable().lookup("1.2.3.4") is None
    v6 = ForwardingTable(6).add("2001:db8::/32", "fe80::1", "eth0").add("::/0", "fe80::2", "eth1")
    assert v6.lookup("2001:db8:1::5")["iface"] == "eth0" and v6.lookup("2600::1")["iface"] == "eth1"


def test_note12_problems_8_and_13():
    assert ipv6_compress("2001:0db8:0000:0000:0001:0000:0000:0001") == "2001:db8::1:0:0:1"
    assert ipv6_compress("2001:0db8:0000:0000:0000:ff00:0042:8329") == "2001:db8::ff00:42:8329"
    t = (ForwardingTable().add("0.0.0.0/0", "R1", "e0").add("203.0.113.0/24", "R2", "e0")
         .add("203.0.113.128/26", "R3", "e0").add("203.0.113.129/32", "R4", "e0"))
    hops = [t.lookup(d)["next_hop"] for d in
            ("203.0.113.129", "203.0.113.190", "203.0.113.200", "198.51.100.7")]
    assert hops == ["R4", "R3", "R2", "R1"]
