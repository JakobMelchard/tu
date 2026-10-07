"""Tests for rfc_vectors.py: the vendored standards are byte-for-byte the
files their SHA256SUMS manifests describe (the same check as
`shasum -a 256 -c SHA256SUMS`), and every parser finds what the RFC prints."""
import pytest

import rfc_vectors


@pytest.mark.parametrize("subdir,count", [("rfc", 11), ("nist", 7), ("vectors", 2)])
def test_vendored_files_match_their_manifest(subdir, count):
    result = rfc_vectors.verify_manifest(subdir)
    assert len(result) == count and all(result.values()), result


def test_parsers_find_every_vector():
    assert rfc_vectors.rfc3526_modp2048().bit_length() == 2048
    assert len(rfc_vectors.rfc5869_cases()) == 7
    for bits in (1024, 2048):
        key, sigs = rfc_vectors.rfc6979_dsa(bits)
        assert len(sigs) == 10 and {v["msg"] for v in sigs} == {b"sample", b"test"}
    assert len(rfc_vectors.rfc8439_block_vector()["block"]) == 64
    v = rfc_vectors.rfc8439_cipher_vector()
    assert len(v["plaintext"]) == len(v["ciphertext"]) == 114
