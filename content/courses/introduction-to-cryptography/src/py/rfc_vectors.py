"""Read test vectors straight out of the vendored standards in ../../refs.

Primitive: none; this is test infrastructure shared by the test modules.
Note: serves notes/07-macs-and-ae.md (HKDF), 09 and 10 (the RFC 3526 group),
11 (RFC 6979) and 05/06 (ChaCha20).
Standard: parses RFC 3526 sec. 3 [S26], RFC 5869 appendix A [S34], RFC 6979
appendix A.2.1/A.2.2 [S32] and RFC 8439 sec. 2.3.2/2.4.2 [S36] from the
unmodified .txt files in refs/rfc, and checks every vendored file against
its SHA256SUMS manifest.  Reading the numbers from the file, rather than
retyping them, means a test can only pass if the implementation reproduces
what the standard itself prints.

EDUCATIONAL TOY CODE (192.125 Introduction to Cryptography, TU Wien).
The parsers know the layout of exactly these RFC versions and nothing else.
Offline: they only read local files.
"""
from __future__ import annotations

import hashlib
import pathlib
import re

REFS = pathlib.Path(__file__).resolve().parents[2] / "refs"


def rfc_text(number: int) -> str:
    return (REFS / "rfc" / f"rfc{number}.txt").read_text()


def verify_manifest(subdir: str) -> dict[str, bool]:
    """{file: checksum matches} for refs/<subdir>/SHA256SUMS, the same check
    as `shasum -a 256 -c SHA256SUMS`."""
    folder = REFS / subdir
    result = {}
    for line in (folder / "SHA256SUMS").read_text().splitlines():
        if line.strip():
            digest, name = line.split(maxsplit=1)
            name = name.lstrip("*")
            result[name] = hashlib.sha256((folder / name).read_bytes()).hexdigest() == digest
    return result


def _section(text: str, start: str, end: str) -> str:
    """The body text from the heading line `start` (at column 0) to `end`."""
    i = re.search(rf"^{re.escape(start)}", text, re.M).start()
    j = re.search(rf"^{re.escape(end)}", text[i + 1:], re.M).start() + i + 1
    return text[i:j]


def _hexdump(block: str) -> bytes:
    """Bytes of an RFC 8439-style dump: '  016  c7 d1 ...  ascii'."""
    out = bytearray()
    for line in block.splitlines():
        m = re.match(r"\s*\d{3}\s+((?:[0-9a-f]{2}\s)+)", line + " ")
        if m:
            out += bytes.fromhex(m.group(1))
    return bytes(out)


# ------------------------------------------------------------ RFC 3526
def rfc3526_modp2048() -> int:
    """The 2048-bit MODP prime, sec. 3 ('Its hexadecimal value is: ...')."""
    body = _section(rfc_text(3526), "3.  2048-bit MODP Group", "4.  3072-bit")
    hexpart = body.split("Its hexadecimal value is:")[1].split("The generator")[0]
    return int("".join(hexpart.split()), 16)


# ------------------------------------------------------------ RFC 5869
def rfc5869_cases() -> list[dict]:
    """The seven HKDF test cases of appendix A: hash name, IKM, salt (None
    when 'not provided'), info, L, PRK, OKM."""
    text, cases = rfc_text(5869), []
    for n in range(1, 8):
        end = f"A.{n + 1}.  Test Case {n + 1}" if n < 7 else "Authors' Addresses"
        body = _section(text, f"A.{n}.  Test Case {n}", end)
        fields = {}
        for key in ("IKM", "salt", "info", "PRK", "OKM"):
            m = re.search(rf"^\s+{key}\s*=\s*(.*?)(?=\(\d+ octets\)|\(defaults)",
                          body, re.M | re.S)
            raw = m.group(1)
            if "not provided" in raw:
                fields[key] = None
            else:
                fields[key] = bytes.fromhex("".join(raw.replace("0x", "").split()))
        fields["hash"] = re.search(r"Hash = (SHA-\d+)", body).group(1)
        fields["L"] = int(re.search(r"L\s+= (\d+)", body).group(1))
        cases.append(fields)
    return cases


# ------------------------------------------------------------ RFC 6979
def rfc6979_dsa(bits: int) -> tuple[dict, list[dict]]:
    """Appendix A.2.1 (bits=1024) or A.2.2 (bits=2048): the key (p, q, g, x,
    y) and the ten signatures (hash, message, k, r, s)."""
    start, end = {1024: ("A.2.1.", "A.2.2."), 2048: ("A.2.2.", "A.2.3.")}[bits]
    body = _section(rfc_text(6979), start, end)
    # drop page breaks, which can split a multi-line number
    body = re.sub(r"\n\n+Pornin.*?\n\n+RFC 6979.*?\n", "\n", body, flags=re.S)
    key = {}
    for name in ("p", "q", "g", "x", "y"):
        m = re.search(rf"^\s+{name} = ((?:[0-9A-F]+\s*)+)", body, re.M)
        key[name] = int("".join(m.group(1).split()), 16)
    sigs = []
    for m in re.finditer(r'With (SHA-\d+), message = "(\w+)":\s+k = ([0-9A-F]+)\s+'
                         r'r = ([0-9A-F]+)\s+s = ([0-9A-F]+)', body):
        h, msg, k, r, s = m.groups()
        sigs.append({"hash": h, "msg": msg.encode(), "k": int(k, 16),
                     "r": int(r, 16), "s": int(s, 16)})
    return key, sigs


# ------------------------------------------------------------ RFC 8439
def rfc8439_block_vector() -> dict:
    """Sec. 2.3.2: key, nonce, counter and the 64-byte serialized block."""
    body = _section(rfc_text(8439), "2.3.2.  Test Vector", "2.4.  The ChaCha20 Encryption")
    return {"key": bytes(range(32)), "nonce": bytes.fromhex("000000090000004a00000000"),
            "counter": 1, "block": _hexdump(body.split("Serialized Block:")[1])}


def rfc8439_cipher_vector() -> dict:
    """Sec. 2.4.2: key, nonce, initial counter, plaintext, ciphertext."""
    body = _section(rfc_text(8439), "2.4.2.  Example and Test Vector", "2.5.  The Poly1305")
    plain = body.split("Plaintext Sunscreen:")[1].split("The following figure")[0]
    cipher = body.split("Ciphertext Sunscreen:")[1]
    return {"key": bytes(range(32)), "nonce": bytes.fromhex("000000000000004a00000000"),
            "counter": 1, "plaintext": _hexdump(plain), "ciphertext": _hexdump(cipher)}


if __name__ == "__main__":
    for sub in ("rfc", "nist", "vectors"):
        ok = verify_manifest(sub)
        print(f"refs/{sub}: {sum(ok.values())}/{len(ok)} checksums OK")
    print("RFC 3526 group 14 prime:", rfc3526_modp2048().bit_length(), "bits")
    print("RFC 5869 cases:", len(rfc5869_cases()))
    for bits in (1024, 2048):
        key, sigs = rfc6979_dsa(bits)
        print(f"RFC 6979 DSA-{bits}: |q| = {key['q'].bit_length()}, {len(sigs)} signatures")
    v = rfc8439_cipher_vector()
    print("RFC 8439 sec. 2.4.2:", len(v["plaintext"]), "plaintext bytes,",
          len(v["ciphertext"]), "ciphertext bytes")
