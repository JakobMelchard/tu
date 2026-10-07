import pytest
from dns import *

# RFC 1035-style query for www.example.com A, id 0xBEEF, RD set.
QUERY = bytes.fromhex("beef" "0100" "0001" "0000" "0000" "0000"
                      "03777777" "076578616d706c65" "03636f6d" "00" "0001" "0001")


def test_build_query_matches_hand_built_bytes():
    assert build_query(0xBEEF, "www.example.com", "A") == QUERY
    q = parse_message(QUERY)
    assert q["id"] == 0xBEEF and q["qr"] == 0 and q["rd"] == 1
    assert q["questions"] == [{"name": "www.example.com.", "type": "A", "class": 1}]


def test_response_with_compression_pointer():
    r = build_response(QUERY, [("www.example.com.", "A", bytes([203, 0, 113, 10]), 3600)], aa=1)
    # answer name is the 2-byte pointer c00c to offset 12
    assert r[12 + len(QUERY) - 12:][:2] == b"\xc0\x0c"
    p = parse_message(r)
    assert p["qr"] == 1 and p["aa"] == 1 and p["rcode"] == "NOERROR"
    assert p["answers"] == [{"name": "www.example.com.", "type": "A", "class": 1, "ttl": 3600,
                             "rdata": "203.0.113.10"}]


def test_nxdomain_and_cname_chain():
    r = build_response(QUERY, [], rcode=3)
    assert parse_message(r)["rcode"] == "NXDOMAIN" and parse_message(r)["answers"] == []
    r = build_response(QUERY, [("www.example.com.", "CNAME", encode_name("example.com"), 60),
                               ("example.com.", "A", bytes([1, 2, 3, 4]), 60)])
    a = parse_message(r)["answers"]
    assert a[0]["type"] == "CNAME" and a[0]["rdata"] == "example.com."
    assert a[1]["name"] == "example.com." and a[1]["rdata"] == "1.2.3.4"


def test_name_compression_decoding_with_pointer_into_pointer():
    msg = b"\x00" * 12 + encode_name("a.example.com") + b"\x01b\xc0\x0e" + b"\xc0\x1b"
    # offset 12: a.example.com ; offset 31: b + pointer to 'example.com' (offset 14) ; offset 35: pointer to 31
    assert decode_name(msg, 12) == ("a.example.com.", 27)
    assert decode_name(msg, 27) == ("b.example.com.", 31)
    assert decode_name(msg, 31) == ("b.example.com.", 33)
    with pytest.raises(ValueError):
        decode_name(b"\x00" * 12 + b"\xc0\x0c", 12)          # pointer to itself


def test_edns0_do_bit_and_types():
    q = build_query(1, "example.com", "AAAA", dnssec_ok=True)
    p = parse_message(q)
    assert p["questions"][0]["type"] == "AAAA" and p["additional"][0]["rdata"] == {"udp_size": 4096, "do": True}
    r = build_response(q, [("example.com.", "MX", b"\x00\x0a" + encode_name("mail.example.com"), 5),
                           ("example.com.", "TXT", b"\x05hello", 5)])
    a = parse_message(r)["answers"]
    assert a[0]["rdata"] == (10, "mail.example.com.") and a[1]["rdata"] == "hello"


# RFC 1035 section 4.1.4, the figure: F.ISI.ARPA at 20, FOO.F.ISI.ARPA at 40 (FOO + pointer
# to 20), ARPA at 64 (pointer to 26), the root at 92.  Typed in from the figure, octet by octet.
RFC1035_FIG = {20: bytes([1]) + b"F" + bytes([3]) + b"ISI" + bytes([4]) + b"ARPA" + b"\x00",
               40: bytes([3]) + b"FOO" + bytes([0b11000000, 20]),
               64: bytes([0b11000000, 26]),
               92: b"\x00"}


def test_rfc1035_section414_compression_example_decodes():
    buf = bytearray(94)
    for off, raw in RFC1035_FIG.items():
        buf[off:off + len(raw)] = raw
    buf = bytes(buf)
    assert decode_name(buf, 20) == ("F.ISI.ARPA.", 32)
    assert decode_name(buf, 40) == ("FOO.F.ISI.ARPA.", 46)
    assert decode_name(buf, 64) == ("ARPA.", 66)
    assert decode_name(buf, 92) == (".", 93)


def test_rfc1035_section414_compression_example_encodes():
    """Writing the same four names at the same offsets reproduces the figure."""
    table = {}
    for off, name in ((20, "F.ISI.ARPA"), (40, "FOO.F.ISI.ARPA"), (64, "ARPA"), (92, ".")):
        assert encode_name(name, table, off) == RFC1035_FIG[off]
    assert table == {"f.isi.arpa": 20, "isi.arpa": 22, "arpa": 26, "foo.f.isi.arpa": 40}
    assert encode_name("foo.F.isi.ARPA", table, 200) == b"\xc0\x28"     # case-insensitive


def test_full_response_matches_hand_built_packet():
    """www.example.com A 203.0.113.10, TTL 3600, AA and RA set, RD copied: every
    octet written out by hand from RFC 1035 sections 4.1.1-4.1.4."""
    expected = bytes.fromhex(
        "beef" "8580" "0001" "0001" "0000" "0000"            # ID; QR AA RD RA = 1000 0101 1000 0000
        "03777777" "076578616d706c65" "03636f6d" "00"        # QNAME www.example.com
        "0001" "0001"                                         # QTYPE A, QCLASS IN
        "c00c" "0001" "0001" "00000e10" "0004" "cb00710a")   # ptr to 12, A, IN, 3600, 4, 203.0.113.10
    got = build_response(QUERY, [("www.example.com.", "A", bytes([203, 0, 113, 10]), 3600)], aa=1)
    assert got == expected
    cname = build_response(QUERY, [("www.example.com.", "CNAME", encode_name("example.com"), 60),
                                   ("example.com.", "A", bytes([203, 0, 113, 10]), 60)])
    second_owner = 12 + 21 + 2 + 10 + 13          # header, question, c00c, fixed RR part, CNAME rdata
    assert cname[second_owner:second_owner + 2] == b"\xc0\x10"  # 'example.com' -> offset 16
    assert parse_message(cname)["answers"][1]["name"] == "example.com."


def test_size_limits_rfc1035_section234():
    encode_name("a" * 63 + ".example")
    with pytest.raises(ValueError):
        encode_name("a" * 64 + ".example")
    encode_name(".".join(["a" * 63] * 3 + ["a" * 61]))              # 4*64 - 2 + 1 = 255 octets
    with pytest.raises(ValueError):
        encode_name(".".join(["a" * 63] * 3 + ["a" * 62]))          # 256 octets
