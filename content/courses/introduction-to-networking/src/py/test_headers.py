import struct
import ipaddress
import pytest
from headers import *


# Hand-built reference packets (computed by hand from the RFC layouts).
ETH_ARP_REQ = bytes.fromhex(
    "ffffffffffff" "020000000001" "0806"
    "0001" "0800" "06" "04" "0001"
    "020000000001" "0a000001" "000000000000" "0a000002")

# IPv4 header from RFC 1071-style example: 20 bytes, src 10.0.0.1 dst 10.0.0.2, TCP,
# ttl 64, total length 40, id 0x1234; checksum computed by hand below.
IPV4_HDR_NOCSUM = bytes.fromhex("4500" "0028" "1234" "4000" "40" "06" "0000" "0a000001" "0a000002")


def test_ipv4_checksum_by_hand():
    words = struct.unpack("!10H", IPV4_HDR_NOCSUM)
    s = sum(words)
    s = (s & 0xFFFF) + (s >> 16)
    s = (s & 0xFFFF) + (s >> 16)
    expected = (~s) & 0xFFFF
    built = build_ipv4("10.0.0.1", "10.0.0.2", IPPROTO_TCP, b"\x00" * 20, ttl=64, ident=0x1234, flags=2)
    assert built[:20] == IPV4_HDR_NOCSUM[:10] + struct.pack("!H", expected) + IPV4_HDR_NOCSUM[12:]
    h = parse_ipv4(built)
    assert h["checksum_ok"] and h["df"] and not h["mf"] and h["ttl"] == 64
    assert h["src"] == "10.0.0.1" and h["dst"] == "10.0.0.2" and h["total_length"] == 40


def test_ethernet_arp_roundtrip():
    frame = build_ethernet("ff:ff:ff:ff:ff:ff", "02:00:00:00:00:01", ETH_P_ARP,
                           build_arp(1, "02:00:00:00:00:01", "10.0.0.1", "00:00:00:00:00:00", "10.0.0.2"))
    assert frame == ETH_ARP_REQ
    layers = dict(parse_frame(frame))
    assert layers["eth"]["type"] == ETH_P_ARP
    assert layers["arp"] == {"htype": 1, "ptype": 0x0800, "op": 1, "sha": "02:00:00:00:00:01",
                             "spa": "10.0.0.1", "tha": "00:00:00:00:00:00", "tpa": "10.0.0.2"}
    assert summarize(frame) == "ARP who-has 10.0.0.2 tell 10.0.0.1"


def test_vlan_tag_is_skipped():
    frame = mac_to_bytes("aa:aa:aa:aa:aa:aa") + mac_to_bytes("bb:bb:bb:bb:bb:bb") + \
        struct.pack("!HHH", 0x8100, 0x0064, ETH_P_IP) + b"payload"
    e = parse_ethernet(frame)
    assert e["vlan"] == 100 and e["type"] == ETH_P_IP and e["payload"] == b"payload"


def test_udp_checksum_verifies_and_pseudo_header_matters():
    seg = build_udp("10.0.0.1", "10.0.0.2", 1234, 53, b"abc")
    u = parse_udp(seg, "10.0.0.1", "10.0.0.2")
    assert u["checksum_ok"] and u["length"] == 11 and u["payload"] == b"abc"
    assert not parse_udp(seg, "10.0.0.1", "10.0.0.3")["checksum_ok"]


def test_tcp_flags_options_and_checksum():
    seg = build_tcp("10.0.0.1", "10.0.0.2", 40000, 80, 1000, 0, "SYN", options=tcp_option_mss(1460))
    t = parse_tcp(seg, "10.0.0.1", "10.0.0.2")
    assert t["flags_str"] == "SYN" and t["flags"] == 0x02 and t["data_offset"] == 24
    assert t["options"] == [("MSS", 1460)] and t["checksum_ok"]
    assert flags_from_str("SYN|ACK") == 0x12 and flags_to_str(0x11) == "FIN|ACK"
    corrupted = seg[:22] + bytes([seg[22] ^ 1]) + seg[23:]   # flip a bit in the MSS option
    assert not parse_tcp(corrupted, "10.0.0.1", "10.0.0.2")["checksum_ok"]


def test_ipv6_header():
    pkt = build_ipv6("2001:db8::1", "2001:db8::2", IPPROTO_UDP,
                     build_udp("2001:db8::1", "2001:db8::2", 5, 6, b"x"), hop_limit=7)
    h = parse_ipv6(pkt)
    assert h["version"] == 6 and h["payload_length"] == 9 and h["hop_limit"] == 7
    assert h["src"] == "2001:db8::1" and h["next_header"] == IPPROTO_UDP
    assert len(pkt) == 49
    assert parse_udp(h["payload"], h["src"], h["dst"])["checksum_ok"]


def test_fragmentation_and_reassembly():
    pkt = build_ipv4("10.0.0.1", "10.0.0.2", IPPROTO_UDP, bytes(range(256)) * 4, ident=7)
    frags = fragment_ipv4(pkt, 576)
    hs = [parse_ipv4(f) for f in frags]
    assert len(frags) == 2 and hs[0]["mf"] and not hs[1]["mf"]
    assert hs[0]["frag_offset"] == 0 and hs[1]["frag_offset"] == 552 // 8
    assert all(len(f) <= 576 for f in frags) and all(h["id"] == 7 for h in hs)
    assert parse_ipv4(reassemble_ipv4(frags[::-1]))["payload"] == bytes(range(256)) * 4
    with pytest.raises(ValueError):
        fragment_ipv4(build_ipv4("1.1.1.1", "2.2.2.2", 17, b"x" * 2000, flags=2), 576)


def test_summary_line_of_tcp_frame():
    seg = build_tcp("10.0.0.1", "10.0.0.2", 40000, 80, 1001, 5001, "PSH|ACK", payload=b"GET")
    frame = build_ethernet("02:00:00:00:00:02", "02:00:00:00:00:01", ETH_P_IP,
                           build_ipv4("10.0.0.1", "10.0.0.2", IPPROTO_TCP, seg))
    assert summarize(frame) == "TCP 10.0.0.1:40000 > 10.0.0.2:80 [PSH|ACK] seq=1001 ack=5001 win=65535 len=3"
