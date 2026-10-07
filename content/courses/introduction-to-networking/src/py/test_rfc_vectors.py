"""Reproduce every worked number that a vendored RFC prints.

191.030 is new in 2026W and has no public past papers, so there are no
lecturer's worked examples to check the code against.  The standards themselves
are the substitute: where an RFC computes a concrete value, the test below
computes the same value from our implementation.  Each test names the RFC and
the section, and the RFC text is in `../../refs/rfc/`.
"""
import ipaddress
import struct

import dnssec
import ospf
import bgp_decision
from inet_checksum import (checksum, incremental_checksum_update, ones_sum, ones_sum32,
                           ones_sum_split, swap16)
from subnet import network_info


# --------------------------------------------------------------- RFC 1071
def test_internet_checksum_rfc1071_section3():
    """RFC 1071 section 3 works the one's-complement sum of 0001 f203 f4f5 f6f7
    four ways and prints every intermediate.  It prints sums, not a checksum:
    the checksum 0x220d is the complement of the printed 0xddf2."""
    w = bytes.fromhex("0001f203f4f5f6f7")
    assert sum(struct.unpack("!4H", w)) == 0x2DDF0                  # "Sum1", normal order
    assert ones_sum(w) == 0xDDF2                                     # "Sum2"
    swapped = bytes(w[i ^ 1] for i in range(len(w)))                 # "Swapped Order" column
    assert sum(struct.unpack("!4H", swapped)) == 0x1F2DC
    assert ones_sum(swapped) == 0xF2DD and swap16(0xF2DD) == 0xDDF2  # "Final Swap"
    # 32 bits at a time, three byte orders: Sum1 0f4f7e8fa, Sum2 1ddf1, Sum3 ddf2
    assert sum(struct.unpack("!2I", w)) == 0x0F4F7E8FA
    assert 0xF4F7 + 0xE8FA == 0x1DDF1 and ones_sum32(w) == 0xDDF2
    assert ones_sum32(bytes.fromhex("010003f2f5f4f7f6")) == 0xF2DD
    # the odd-boundary split: f201 + byte-swapped f0eb = 1ddf1 -> ddf2
    assert ones_sum(bytes.fromhex("0001f2")) == 0xF201
    assert ones_sum(bytes.fromhex("03f4f5f6f7")) == 0xF0EB and swap16(0xF0EB) == 0xEBF0
    assert ones_sum_split(w, 3) == 0xDDF2
    assert all(ones_sum_split(w, k) == 0xDDF2 for k in range(len(w) + 1))
    assert checksum(w) == 0x220D == (~0xDDF2) & 0xFFFF


# --------------------------------------------------------------- RFC 1624
def test_incremental_update_rfc1624_section4():
    """RFC 1624 section 4: a 16-bit field m = 0x5555 changes to m' = 0x3285 and
    the one's-complement sum of every other header octet is 0xCD7A.

    The RFC prints HC = 0xDD2F before the change and HC' = 0x0000 after it, and
    shows that RFC 1141's equation 2 wrongly yields 0xFFFF.
    """
    rest, m, m_new = 0xCD7A, 0x5555, 0x3285

    def ones(x):
        while x >> 16:
            x = (x & 0xFFFF) + (x >> 16)
        return x

    hc = (~ones(rest + m)) & 0xFFFF
    assert hc == 0xDD2F                                   # RFC's stated HC
    assert (~ones(rest + m_new)) & 0xFFFF == 0x0000       # RFC's recomputed HC'
    assert incremental_checksum_update(hc, m, m_new) == 0x0000
    # ... and the superseded RFC 1141 equation 2 gives the impossible 0xFFFF
    assert ones(hc + m + ((~m_new) & 0xFFFF)) == 0xFFFF


def test_incremental_update_matches_full_recomputation_over_a_ttl_decrement():
    """The property behind the RFC: an incremental update of the word holding
    TTL and Protocol must agree with recomputing the whole header."""
    hdr = bytearray(bytes.fromhex("4500002812344000" "4006" "0000" "0a0000010a000002"))
    hdr[10:12] = checksum(bytes(hdr)).to_bytes(2, "big")
    old_word = int.from_bytes(hdr[8:10], "big")           # TTL | Protocol
    new_word = ((hdr[8] - 1) << 8) | hdr[9]
    updated = incremental_checksum_update(int.from_bytes(hdr[10:12], "big"), old_word, new_word)
    hdr[8] -= 1
    hdr[10:12] = b"\x00\x00"
    assert updated == checksum(bytes(hdr))


# --------------------------------------------------------------- RFC 4034
def test_dnssec_key_tag_and_ds_digest_rfc4034_section54():
    """RFC 4034 section 5.4 prints a DNSKEY for `dskey.example.com.` with
    "key id = 60485" and the matching DS record with SHA-1 digest
    2BB183AF5F22588179A53B0A98631FAD1A292118."""
    e = dnssec.RFC4034_EXAMPLE
    ds = dnssec.ds_record(e["owner"], e["flags"], e["protocol"], e["algorithm"],
                          e["public_key"])
    assert ds["key_tag"] == e["expected_key_tag"] == 60485
    assert ds["digest"].hex().upper() == e["expected_ds_sha1"]
    assert ds["digest_type"] == 1 and len(ds["digest"]) == 20   # section 5.1.4: SHA-1 is 20 octets


def test_dnssec_key_tag_is_not_the_internet_checksum():
    """RFC 4034 Appendix B: "almost but not completely identical to the familiar
    ones-complement checksum" -- it is the same sum without the final
    complement, so the two differ by exactly that."""
    rdata = dnssec.dnskey_rdata(256, 3, 5, dnssec.RFC4034_EXAMPLE["public_key"])
    assert dnssec.key_tag(rdata) == (~checksum(rdata)) & 0xFFFF


def test_dnssec_flag_257_is_the_secure_entry_point():
    """RFC 4034 section 2.1.1: bit 15 (value 1) is the SEP flag, bit 7
    (value 256) the Zone Key flag, so a KSK is written 257 and a ZSK 256."""
    assert "SEP" in dnssec.describe_flags(257) and "Zone Key" in dnssec.describe_flags(257)
    assert "SEP" not in dnssec.describe_flags(256)


# --------------------------------------------------------------- RFC 2328
def test_ospf_architectural_constants_rfc2328_appendix_b():
    a = ospf.ARCHITECTURAL
    assert a["LSRefreshTime"] == 30 * 60        # "30 minutes"
    assert a["MinLSInterval"] == 5              # "5 seconds"
    assert a["MinLSArrival"] == 1               # "1 second"
    assert a["MaxAge"] == 3600                  # "1 hour"
    assert a["CheckAge"] == 5 * 60              # "5 minutes"
    assert a["MaxAgeDiff"] == 15 * 60           # "15 minutes"
    assert a["LSInfinity"] == 0xFFFFFF          # "24-bit binary value of all ones"
    assert a["InitialSequenceNumber"] == 0x80000001
    assert a["MaxSequenceNumber"] == 0x7FFFFFFF


def test_ospf_hello_and_dead_are_appendix_c_samples_not_defaults():
    """RFC 2328 Appendix C.3 gives HelloInterval "sample value for a local area
    network: 10 seconds" and says RouterDeadInterval "should be some multiple of
    the HelloInterval (say 4)".  10/40 follows from those two sentences; the RFC
    states no default."""
    assert ospf.hello_dead_pair() == (10, 40)
    assert ospf.hello_dead_pair(hello=ospf.SAMPLE_X25["HelloInterval"]) == (30, 120)
    assert ospf.hello_dead_pair(hello=1, multiplier=3) == (1, 3)


def test_ospf_encapsulation_rfc2328_appendix_a1():
    assert ospf.IP_PROTOCOL == 89
    assert ospf.ALL_SPF_ROUTERS == "224.0.0.5" and ospf.ALL_D_ROUTERS == "224.0.0.6"
    # both are inside the link-local multicast block a router never forwards
    for a in (ospf.ALL_SPF_ROUTERS, ospf.ALL_D_ROUTERS):
        assert ipaddress.ip_address(a) in ipaddress.ip_network("224.0.0.0/24")


def test_ospf_lsa_freshness_rfc2328_section131():
    old = ospf.LSA(1, "10.0.0.1", "10.0.0.1", 0x80000001, 0x1111, 100)
    new = ospf.LSA(1, "10.0.0.1", "10.0.0.1", 0x80000002, 0x0001, 900)
    assert ospf.which_is_newer(new, old) == "a"          # sequence number first
    # equal sequence: the larger checksum wins
    a = ospf.LSA(1, "10.0.0.1", "10.0.0.1", 0x80000002, 0x2222, 10)
    b = ospf.LSA(1, "10.0.0.1", "10.0.0.1", 0x80000002, 0x1111, 10)
    assert ospf.which_is_newer(a, b) == "a"
    # equal sequence and checksum: a MaxAge instance is newer (it is a flush)
    flush = ospf.LSA(1, "10.0.0.1", "10.0.0.1", 0x80000002, 0x2222, ospf.ARCHITECTURAL["MaxAge"])
    assert ospf.which_is_newer(flush, a) == "a"
    # ages differing by <= MaxAgeDiff are the same instance, more than that: younger wins
    close = ospf.LSA(1, "10.0.0.1", "10.0.0.1", 0x80000002, 0x2222, 10 + 900)
    assert ospf.which_is_newer(a, close) == "same"
    far = ospf.LSA(1, "10.0.0.1", "10.0.0.1", 0x80000002, 0x2222, 10 + 901)
    assert ospf.which_is_newer(a, far) == "a"


def test_ospf_sequence_numbers_are_signed():
    """InitialSequenceNumber 0x80000001 must compare as the *smallest*, not the
    largest, 32-bit value."""
    first = ospf.LSA(1, "1.1.1.1", "1.1.1.1", ospf.ARCHITECTURAL["InitialSequenceNumber"])
    later = ospf.LSA(1, "1.1.1.1", "1.1.1.1", 0x00000005)
    assert ospf.which_is_newer(later, first) == "a"


def test_ospf_database_only_accepts_newer_instances():
    db = {}
    lsa = ospf.LSA(1, "10.0.0.1", "10.0.0.1", 0x80000001, 0xABCD, 0)
    assert ospf.install(db, lsa) is True
    assert ospf.install(db, ospf.LSA(1, "10.0.0.1", "10.0.0.1", 0x80000001, 0xABCD, 0)) is False
    assert ospf.install(db, ospf.LSA(1, "10.0.0.1", "10.0.0.1", 0x80000002, 0x0000, 0)) is True
    assert len(db) == 1                                   # same identity, one entry


# --------------------------------------------------------------- RFC 4271
def test_bgp_timer_defaults_rfc4271_section10():
    t = bgp_decision.TIMERS
    assert t["ConnectRetryTime"] == 120
    assert t["HoldTime"] == 90
    assert t["HoldTime_large"] == 240                      # "4 minutes"
    assert t["KeepaliveTime"] == 30 == bgp_decision.keepalive_for(90)
    assert t["MinASOriginationIntervalTimer"] == 15
    assert t["MinRouteAdvertisementIntervalTimer_eBGP"] == 30
    assert t["MinRouteAdvertisementIntervalTimer_iBGP"] == 5
    assert bgp_decision.JITTER_RANGE == (0.75, 1.0)
    assert bgp_decision.PORT == 179
    # section 4.2: HoldTime 0 disables the hold timer and KEEPALIVEs
    assert bgp_decision.keepalive_for(0) == 0


def test_bgp_local_pref_is_phase_1_not_a_tie_break():
    """RFC 4271 section 9.1.1 vs 9.1.2.2: a route with a higher degree of
    preference wins before AS_PATH length is ever looked at."""
    base = dict(prefix="192.0.2.0/24", bgp_identifier="10.0.0.1", peer_address="10.0.0.1")
    long_customer = bgp_decision.Route(**base, as_path=(1, 2, 3, 4), policy_pref=100)
    short_peer = bgp_decision.Route(**base, as_path=(9,), policy_pref=80)
    trace = []
    assert bgp_decision.select([long_customer, short_peer], trace) is long_customer
    assert any("phase 1" in line for line in trace)
    assert not any("AS_PATH" in line for line in trace)


def test_bgp_tie_break_order_rfc4271_section9122():
    """Steps a, b, d, f of section 9.1.2.2, each isolated."""
    base = dict(prefix="192.0.2.0/24", policy_pref=100, peer_address="10.0.0.1",
                bgp_identifier="10.0.0.1")
    short = bgp_decision.Route(**{**base, "as_path": (1, 2)})
    long_ = bgp_decision.Route(**{**base, "as_path": (1, 2, 3)})
    assert bgp_decision.select([long_, short]) is short                      # a

    igp = bgp_decision.Route(**{**base, "as_path": (1,), "origin": "IGP"})
    incomplete = bgp_decision.Route(**{**base, "as_path": (1,), "origin": "INCOMPLETE"})
    assert bgp_decision.select([incomplete, igp]) is igp                     # b

    ext = bgp_decision.Route(**{**base, "as_path": (1,), "from_ebgp": True})
    int_ = bgp_decision.Route(prefix="192.0.2.0/24", as_path=(1,), local_pref=100,
                              from_ebgp=False, peer_address="10.0.0.2",
                              bgp_identifier="10.0.0.2")
    assert bgp_decision.select([int_, ext]) is ext                           # d

    low_id = bgp_decision.Route(**{**base, "as_path": (1,), "bgp_identifier": "10.0.0.1"})
    high_id = bgp_decision.Route(**{**base, "as_path": (1,), "bgp_identifier": "10.0.0.9"})
    assert bgp_decision.select([high_id, low_id]) is low_id                  # f


def test_bgp_med_is_only_compared_within_one_neighbour_as():
    """Section 9.1.2.2 c: MED is comparable only between routes learnt from the
    same neighbouring AS, and a missing MED counts as 0."""
    base = dict(prefix="192.0.2.0/24", policy_pref=100, as_path=(7, 8))
    a = bgp_decision.Route(**base, med=50, neighbor_as=7, bgp_identifier="10.0.0.1",
                           peer_address="10.0.0.1")
    b = bgp_decision.Route(**base, med=10, neighbor_as=7, bgp_identifier="10.0.0.2",
                           peer_address="10.0.0.2")
    assert bgp_decision.select([a, b]) is b
    # different neighbour AS: MED is not comparable, so the lowest BGP Identifier decides
    c = bgp_decision.Route(**base, med=10, neighbor_as=99, bgp_identifier="10.0.0.2",
                           peer_address="10.0.0.2")
    assert bgp_decision.select([a, c]) is a
    # absent MED counts as the lowest possible value
    none_med = bgp_decision.Route(**base, med=None, neighbor_as=7,
                                  bgp_identifier="10.0.0.3", peer_address="10.0.0.3")
    assert bgp_decision.select([a, none_med]) is none_med


def test_bgp_as_set_counts_as_one_as():
    """Section 9.1.2.2 a: "an AS_SET counts as 1, no matter how many ASes are in
    the set"."""
    base = dict(prefix="192.0.2.0/24", policy_pref=100, peer_address="10.0.0.1",
                bgp_identifier="10.0.0.1")
    aggregated = bgp_decision.Route(**base, as_path=(1, frozenset({2, 3, 4, 5})))
    plain = bgp_decision.Route(**base, as_path=(1, 2, 3))
    assert aggregated.as_path_length() == 2 < plain.as_path_length()
    assert bgp_decision.select([plain, aggregated]) is aggregated


# --------------------------------------------------------------- RFC 3021, 5737, 6598
def test_rfc3021_point_to_point_31_bit_prefix():
    """RFC 3021 section 2.1: on a /31 the two addresses are both usable host
    addresses -- there is no network or broadcast address."""
    info = network_info("192.0.2.0/31")
    assert info["hosts"] == 2


def test_documentation_and_shared_address_space_are_reserved():
    """RFC 5737 reserves three /24s for documentation and RFC 6598 reserves
    100.64.0.0/10 as Shared Address Space for carrier-grade NAT -- the blocks
    the notes use in every worked example instead of somebody's real address."""
    for net in ("192.0.2.0/24", "198.51.100.0/24", "203.0.113.0/24"):
        assert ipaddress.ip_network(net).is_private          # RFC 5737, per the IANA registry
    cgnat = ipaddress.ip_network("100.64.0.0/10")            # RFC 6598
    assert cgnat.num_addresses == 2 ** 22
    assert ipaddress.ip_address("100.64.0.1") in cgnat


# --------------------------------------------------------------- demos run
def test_each_new_module_demo_runs(capsys):
    for module in (dnssec, ospf, bgp_decision):
        fn = getattr(module, "demo", None)
        if fn is None:
            continue
        fn()
    out = capsys.readouterr().out
    assert "RFC 2328" in out and "RFC 4271" in out
