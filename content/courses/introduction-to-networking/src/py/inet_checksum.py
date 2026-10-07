"""The Internet checksum and its incremental update (notes 03 and 05).

Implements RFC 1071 section 1 (one's-complement sum, end-around carry, final
complement), the properties of section 2(A)-(B) that section 3 demonstrates
numerically (commutativity; byte-order independence; summing in 32-bit words;
splitting a block at an odd offset and byte-swapping the second part), and RFC
1624 section 3 equation 3 (incremental update).

Split out of `headers.py` because it is not header build/parse code: it is
exactly specified arithmetic with worked numbers printed in the RFCs, and
`test_rfc_vectors.py` treats them as RFC test vectors rather than as packet
plumbing.

What RFC 1071 section 3 prints is the *sum*, never the checksum: the words
0001 f203 f4f5 f6f7 give 0x2ddf0, folded 0xddf2.  The checksum field would then
hold its complement, ~0xddf2 = 0x220d.  That last step is ours, not the RFC's.

The same one's-complement sum covers the IPv4 header (RFC 791 section 3.1), and
-- over a pseudo-header -- UDP (RFC 768) and TCP (RFC 9293 section 3.1).  It
detects every single-bit error and most bursts, but is order-insensitive, so
transposed 16-bit words slip through.
"""
import struct


def checksum(data):
    """Internet checksum (RFC 1071 section 1): one's-complement sum of 16-bit
    big-endian words with end-around carry, then one's complement.  An odd
    trailing byte is padded with a zero byte.

    Verification is the same routine: summing a block that already contains its
    own checksum gives 0xFFFF, i.e. `checksum(block) == 0`.  RFC 1071 section 3
    works the sum of 0001 f203 f4f5 f6f7 out by hand (0xddf2); the checksum of
    those words is its complement 0x220d.  `test_rfc_vectors.py` reproduces
    every intermediate the RFC prints.
    """
    if len(data) % 2:
        data += b"\x00"
    s = sum(struct.unpack(f"!{len(data) // 2}H", data))
    while s >> 16:                      # fold carries back in (end-around carry)
        s = (s & 0xFFFF) + (s >> 16)
    return (~s) & 0xFFFF


def ones_sum(data):
    """RFC 1071 section 1 (1)-(2): the folded one's-complement sum of the 16-bit
    big-endian words, *not* complemented.  `checksum(data) == ~ones_sum(data)`."""
    if len(data) % 2:
        data += b"\x00"
    return _ones(sum(struct.unpack(f"!{len(data) // 2}H", data)))


def ones_sum32(data):
    """Same sum accumulated in 32-bit words, then top half + bottom half folded:
    RFC 1071 section 2(C) ("parallel summation"), worked in section 3."""
    data += b"\x00" * (-len(data) % 4)
    s = sum(struct.unpack(f"!{len(data) // 4}I", data))
    while s >> 32:                      # the RFC's "Carries" line: fold into 32 bits
        s = (s & 0xFFFFFFFF) + (s >> 32)
    return _ones((s >> 16) + (s & 0xFFFF))       # "Top half" + "Bottom half"


def swap16(x):
    """Byte swap of a 16-bit value."""
    return ((x & 0xFF) << 8) | (x >> 8)


def ones_sum_split(data, k):
    """Sum data[:k] and data[k:] separately and combine.  If the second part
    starts at an odd offset its sum is byte-swapped before adding: RFC 1071
    section 2(B), byte-order independence, and the last example of section 3."""
    a, b = ones_sum(data[:k]), ones_sum(data[k:])
    return _ones(a + (swap16(b) if k % 2 else b))


def _ones(x):
    """One's-complement fold: add the carries back into the low 16 bits."""
    while x >> 16:
        x = (x & 0xFFFF) + (x >> 16)
    return x


def incremental_checksum_update(old_checksum, old_word, new_word):
    """Update a header checksum after one 16-bit field changed, without summing
    the whole header again -- what every router does to the IPv4 header when it
    decrements the TTL, and what a NAT does when it rewrites an address or port.

    RFC 1624 equation 3:  HC' = ~(C + (-m) + m'),  where C = ~HC and (-m) = ~m,
    all in one's-complement arithmetic.  The obvious-looking equation 2 of the
    superseded RFC 1141 (HC' = HC + m + ~m') is wrong: it can produce 0xFFFF,
    which is negative zero and can never be a valid IPv4 header checksum.
    RFC 1624 section 4 works this out on m = 0x5555 -> m' = 0x3285; the tests
    reproduce those numbers.
    """
    c = (~old_checksum) & 0xFFFF
    return (~_ones(c + ((~old_word) & 0xFFFF) + (new_word & 0xFFFF))) & 0xFFFF


if __name__ == "__main__":
    w = bytes.fromhex("0001f203f4f5f6f7")
    print("RFC 1071 section 3:  words 0001 f203 f4f5 f6f7")
    print(f"  16-bit sum       = 0x{ones_sum(w):04x}  (RFC prints ddf2)")
    print(f"  swapped order    = 0x{ones_sum(bytes(w[i ^ 1] for i in range(8))):04x}"
          "  (RFC prints f2dd, i.e. ddf2 byte-swapped)")
    print(f"  32-bit words     = 0x{ones_sum32(w):04x}  (RFC prints ddf2)")
    print(f"  split at byte 3  = 0x{ones_sum_split(w, 3):04x}  (RFC prints f201 + swap(f0eb) = ddf2)")
    print(f"  checksum         = 0x{checksum(w):04x}  (= ~ddf2; derived, not printed by the RFC)")
    print()
    rest, m, m_new = 0xCD7A, 0x5555, 0x3285
    hc = (~_ones(rest + m)) & 0xFFFF
    print("RFC 1624 section 4:  m = 0x5555 -> 0x3285, other octets sum to 0xCD7A")
    print(f"  HC  (before)                  = 0x{hc:04x}  (RFC says 0xDD2F)")
    print(f"  HC' recomputed from scratch   = 0x{(~_ones(rest + m_new)) & 0xFFFF:04x}  (RFC says 0x0000)")
    print(f"  HC' by RFC 1624 equation 3    = 0x{incremental_checksum_update(hc, m, m_new):04x}")
    print(f"  HC' by RFC 1141 equation 2    = 0x{_ones(hc + m + ((~m_new) & 0xFFFF)):04x}"
          "  <- impossible, which is why RFC 1141 was superseded")
