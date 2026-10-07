"""DNSSEC key tag and DS digest, RFC 4034 (note 08).

Two small, exactly specified computations that a validating resolver performs on
every delegation, and the only part of DNSSEC with a published test vector:

* **Key tag** (RFC 4034 Appendix B): a 16-bit hint that lets a resolver pick the
  candidate DNSKEY for an RRSIG or DS without trying every key.  It is the sum
  of the DNSKEY RDATA read as 16-bit big-endian groups, carries folded in --
  *almost* the Internet checksum of RFC 1071 but not complemented, and the RFC
  says so explicitly.  Algorithm 1 (RSA/MD5) is defined differently
  (Appendix B.1) and is NOT RECOMMENDED; it is implemented here only so the
  difference is visible.

* **DS digest** (RFC 4034 section 5.1.4):
  `digest = H(canonical owner name | DNSKEY RDATA)`, where the owner name is the
  wire-format, lower-cased, fully qualified name (RFC 4034 section 6.2).  The DS
  record lives in the *parent* zone and is the single link of the chain of
  trust: change the child's KSK and the parent's DS must change with it.

The test reproduces the worked example of RFC 4034 section 5.4
(`dskey.example.com.`, key tag 60485, SHA-1 DS digest 2BB183AF...).
"""
import base64
import hashlib
import struct

DIGEST_ALGORITHMS = {1: ("SHA-1", hashlib.sha1), 2: ("SHA-256", hashlib.sha256)}
SEP_FLAG = 0x0001          # bit 15 of Flags: secure entry point, i.e. a KSK
ZONE_KEY_FLAG = 0x0100     # bit 7 of Flags: this key signs zone data


def dnskey_rdata(flags, protocol, algorithm, public_key):
    """Wire format of a DNSKEY RDATA (RFC 4034 section 2.1): Flags(16) |
    Protocol(8) | Algorithm(8) | Public Key.  `public_key` is raw bytes or the
    base64 text as it appears in a zone file."""
    if isinstance(public_key, str):
        public_key = base64.b64decode("".join(public_key.split()))
    return struct.pack("!HBB", flags, protocol, algorithm) + public_key


def key_tag(rdata):
    """RFC 4034 Appendix B, for every algorithm except 1.

    Sum the RDATA as 16-bit big-endian groups (a trailing odd byte counts as the
    high half of a final group), then fold the carries in once and mask to 16
    bits.  Unlike the Internet checksum the result is *not* complemented.
    """
    if len(rdata) > 3 and rdata[3] == 1:
        return _key_tag_algorithm_1(rdata)
    acc = 0
    for i in range(0, len(rdata), 2):
        acc += (rdata[i] << 8) if i + 1 == len(rdata) else struct.unpack_from("!H", rdata, i)[0]
    acc += (acc >> 16) & 0xFFFF
    return acc & 0xFFFF


def _key_tag_algorithm_1(rdata):
    """RFC 4034 Appendix B.1: for RSA/MD5 the tag is the 4th- and 3rd-to-last
    octets of the modulus, i.e. of the RDATA."""
    return struct.unpack("!H", rdata[-3:-1])[0]


def canonical_name(name):
    """RFC 4034 section 6.2: wire format, lower case, fully qualified."""
    out = b""
    for label in name.rstrip(".").lower().split("."):
        if label:
            out += bytes([len(label)]) + label.encode("ascii")
    return out + b"\x00"


def ds_digest(owner, rdata, digest_type=1):
    """RFC 4034 section 5.1.4: H(canonical owner name | DNSKEY RDATA)."""
    _, h = DIGEST_ALGORITHMS[digest_type]
    return h(canonical_name(owner) + rdata).digest()


def ds_record(owner, flags, protocol, algorithm, public_key, digest_type=1):
    """The complete DS RDATA fields (Key Tag, Algorithm, Digest Type, Digest)
    for a DNSKEY, as the parent zone must publish them."""
    rdata = dnskey_rdata(flags, protocol, algorithm, public_key)
    return {"key_tag": key_tag(rdata), "algorithm": algorithm,
            "digest_type": digest_type, "digest": ds_digest(owner, rdata, digest_type)}


def describe_flags(flags):
    parts = []
    if flags & ZONE_KEY_FLAG:
        parts.append("Zone Key")
    if flags & SEP_FLAG:
        parts.append("SEP (KSK)")
    return ", ".join(parts) or "none"


# The example of RFC 4034 section 5.4, verbatim.
RFC4034_EXAMPLE = {
    "owner": "dskey.example.com.",
    "flags": 256, "protocol": 3, "algorithm": 5,
    "public_key": """AQOeiiR0GOMYkDshWoSKz9XzfwJr1AYtsmx3TGkJaNXVbfi/2pHm822aJ5iI9BMzNXxe
                     YCmZDRD99WYwYqUSdjMmmAphXdvxegXd/M5+X7OrzKBaMbCVdFLUUh6DhweJBjEVv5f2
                     wwjM9XzcnOf+EPbtG9DMBmADjFDc2w/rljwvFw==""",
    "expected_key_tag": 60485,
    "expected_ds_sha1": "2BB183AF5F22588179A53B0A98631FAD1A292118",
}


def demo():
    e = RFC4034_EXAMPLE
    ds = ds_record(e["owner"], e["flags"], e["protocol"], e["algorithm"], e["public_key"])
    print("RFC 4034 section 5.4 example")
    print(f"  DNSKEY {e['owner']} flags={e['flags']} ({describe_flags(e['flags'])}) "
          f"proto={e['protocol']} alg={e['algorithm']}")
    print(f"  key tag  {ds['key_tag']}   (RFC says {e['expected_key_tag']})")
    print(f"  DS SHA-1 {ds['digest'].hex().upper()}")
    print(f"  RFC says {e['expected_ds_sha1']}")
    ds256 = ds_record(e["owner"], e["flags"], e["protocol"], e["algorithm"],
                      e["public_key"], digest_type=2)
    print(f"  DS SHA-256 (digest type 2, not in the RFC example) "
          f"{ds256['digest'].hex().upper()}")


if __name__ == "__main__":
    demo()
