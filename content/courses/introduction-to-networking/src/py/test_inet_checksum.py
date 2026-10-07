"""Internet checksum, RFC 1071 and RFC 1624 (note 03).

The RFC-vector assertions for these two routines live here *and* in
`test_rfc_vectors.py`; this file covers the module's ordinary behaviour
(padding, verification, round-tripping), the other covers the published
numbers alongside every other RFC's.
"""
import struct

from inet_checksum import checksum, incremental_checksum_update, ones_sum


def test_checksum_rfc1071_example():
    # RFC 1071 section 3: words 0001 f203 f4f5 f6f7 -> sum 0x2ddf0 -> fold 0xddf2 (printed);
    # the checksum is the complement, 0x220d (derived).
    assert ones_sum(bytes.fromhex("0001f203f4f5f6f7")) == 0xDDF2
    assert checksum(bytes.fromhex("0001f203f4f5f6f7")) == 0x220D == (~0xDDF2) & 0xFFFF


def test_checksum_odd_length_and_verification():
    # odd length is padded with a zero byte; appending the checksum verifies to 0
    data = b"\x01\x02\x03"
    c = checksum(data)
    assert c == checksum(data + b"\x00")
    assert checksum(data + b"\x00" + struct.pack("!H", c)) == 0


def test_checksum_is_order_insensitive():
    """The known weakness: the sum is commutative, so transposed 16-bit words
    give the same checksum.  Worth a test because it is the standard exam
    question about what the checksum does *not* catch."""
    a, b = bytes.fromhex("0001f203"), bytes.fromhex("f2030001")
    assert checksum(a) == checksum(b)


def test_incremental_update_is_reversible():
    """Applying the update and then undoing it returns the original checksum,
    which is what makes it safe to chain at every hop."""
    original = checksum(bytes.fromhex("4500002812344000" "4006" "0000" "0a000001" "0a000002"))
    once = incremental_checksum_update(original, 0x4006, 0x3F06)
    assert incremental_checksum_update(once, 0x3F06, 0x4006) == original


def test_checksum_re_exported_by_headers():
    """`headers` re-exports both so packet code reads as one module; the tests
    that build packets rely on that."""
    import headers
    assert headers.checksum is checksum
    assert headers.incremental_checksum_update is incremental_checksum_update
