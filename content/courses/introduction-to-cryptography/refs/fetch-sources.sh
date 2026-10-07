#!/usr/bin/env bash
# Verify (and if necessary re-fetch) the vendored standards, and optionally
# download the cite-only material into ./vendor, which is git-ignored.
# See README.md for why the standards are vendored and the rest is not.
#
#   ./fetch-sources.sh --verify    checksums only, no network
#   ./fetch-sources.sh             re-fetch anything missing or changed, verify
#   ./fetch-sources.sh --papers    the above, plus the free cite-only PDFs
set -euo pipefail

cd "$(dirname "$0")"
MODE="${1:-refetch}"

RFCS=$(sed 's/.*  //; s/^rfc//; s/\.txt$//' rfc/SHA256SUMS)

# NIST file name -> download URL
nist_url() {
    case "$1" in
    NIST.FIPS.197-upd1.pdf) echo "https://nvlpubs.nist.gov/nistpubs/FIPS/NIST.FIPS.197-upd1.pdf" ;;
    NIST.FIPS.180-4.pdf)    echo "https://nvlpubs.nist.gov/nistpubs/FIPS/NIST.FIPS.180-4.pdf" ;;
    NIST.FIPS.198-1.pdf)    echo "https://nvlpubs.nist.gov/nistpubs/FIPS/NIST.FIPS.198-1.pdf" ;;
    NIST.FIPS.186-5.pdf)    echo "https://nvlpubs.nist.gov/nistpubs/FIPS/NIST.FIPS.186-5.pdf" ;;
    NIST.SP.800-38A.pdf)    echo "https://nvlpubs.nist.gov/nistpubs/Legacy/SP/nistspecialpublication800-38a.pdf" ;;
    NIST.SP.800-38D.pdf)    echo "https://nvlpubs.nist.gov/nistpubs/Legacy/SP/nistspecialpublication800-38d.pdf" ;;
    NIST.SP.800-57pt1r5.pdf) echo "https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-57pt1r5.pdf" ;;
    esac
}

verify() {
    (cd rfc     && shasum -a 256 -c SHA256SUMS)
    (cd nist    && shasum -a 256 -c SHA256SUMS)
    (cd vectors && shasum -a 256 -c SHA256SUMS)
}

refetch() {
    mkdir -p rfc nist vectors
    for n in $RFCS; do
        out="rfc/rfc$n.txt"
        [ -s "$out" ] && continue
        echo "fetch $out"
        curl -fsS -o "$out" "https://www.rfc-editor.org/rfc/rfc$n.txt"
    done
    for f in $(sed 's/.*  //' nist/SHA256SUMS); do
        out="nist/$f"
        [ -s "$out" ] && continue
        echo "fetch $out"
        curl -fsSL -o "$out" "$(nist_url "$f")"
    done
    base="https://raw.githubusercontent.com/C2SP/wycheproof/main"
    [ -s vectors/rsa_oaep_2048_sha256_mgf1sha256_test.json ] || {
        echo "fetch vectors/rsa_oaep_2048_sha256_mgf1sha256_test.json"
        curl -fsSL -o vectors/rsa_oaep_2048_sha256_mgf1sha256_test.json \
            "$base/testvectors_v1/rsa_oaep_2048_sha256_mgf1sha256_test.json"
    }
    [ -s vectors/LICENSE-Apache-2.0.txt ] || \
        curl -fsSL -o vectors/LICENSE-Apache-2.0.txt "$base/LICENSE"
}

papers() {
    mkdir -p vendor
    get() {  # get <name> <url>
        if [ -s "vendor/$1" ]; then echo "have  vendor/$1"; return; fi
        echo "fetch vendor/$1"
        curl -fsSL -o "vendor/$1" "$2" || echo "  failed (cite-only source, fetch by hand)"
    }
    # S8 -- the lecturer's 2024W slide archive: the most useful single source.
    # Third-party copyright, no licence statement, so it is NOT vendored.
    # VoWi is behind an Anubis proof-of-work gate, so this usually needs a
    # browser rather than curl; the URL is here so you know where to point it.
    echo "S8  lecture slides 2024W (open in a browser, VoWi has a bot gate):"
    echo "    https://vowi.fsinf.at/wiki/TU_Wien:Introduction_to_Cryptography_VU_(Fuchsbauer)"
    # S39 -- Bellare & Rogaway, Optimal Asymmetric Encryption (the OAEP paper).
    get S39-bellare-rogaway-oaep.pdf \
        'https://web.cs.ucdavis.edu/~rogaway/papers/oae.pdf'
    # IACR ePrint PDFs (S40, S45b, S49) sit behind a Cloudflare challenge as of
    # 2026-10-07: curl gets HTTP 403 and reports "failed". Open the abstract
    # page (URL without .pdf) in a browser instead.
    # S40 -- Shoup, OAEP Reconsidered; and Fujisaki et al., RSA-OAEP is secure.
    get S40a-shoup-oaep-reconsidered.pdf 'https://eprint.iacr.org/2000/060.pdf'
    get S40b-fujisaki-et-al-rsa-oaep.pdf 'https://eprint.iacr.org/2000/061.pdf'
    # S41 -- Manger, chosen-ciphertext attack on OAEP as standardised.
    get S41-manger-oaep-attack.pdf \
        'https://www.iacr.org/archive/crypto2001/21390229.pdf'
    # S45 -- Bellare & Rogaway, Random Oracles are Practical; CGH revisited.
    # (The UC Davis copy returns 404, checked 2026-10-07; Bellare's copy instead.)
    get S45a-bellare-rogaway-random-oracles.pdf \
        'https://cseweb.ucsd.edu/~mihir/papers/ro.pdf'
    get S45b-canetti-goldreich-halevi-rom-revisited.pdf \
        'https://eprint.iacr.org/1998/011.pdf'
    # S46 -- Pointcheval & Stern, the forking lemma.
    get S46-pointcheval-stern-forking.pdf \
        'https://www.di.ens.fr/david.pointcheval/Documents/Papers/2000_joc.pdf'
    # S47 -- Heninger et al., Mining Your Ps and Qs (shared RSA primes).
    get S47-heninger-mining-your-ps-and-qs.pdf \
        'https://factorable.net/weakkeys12.extended.pdf'
    # S48 -- Vaudenay, security flaws induced by CBC padding.
    get S48-vaudenay-cbc-padding.pdf \
        'https://www.iacr.org/archive/eurocrypt2002/23320530/cbc02_e02d.pdf'
    # S49 -- Bellare & Namprempre, generic composition.
    get S49-bellare-namprempre-composition.pdf 'https://eprint.iacr.org/2000/025.pdf'
    # S51 -- Diffie & Hellman, New Directions in Cryptography.
    get S51-diffie-hellman-new-directions.pdf \
        'https://ee.stanford.edu/~hellman/publications/24.pdf'
    # S52 -- Rivest, Shamir & Adleman.
    get S52-rsa.pdf 'https://people.csail.mit.edu/rivest/Rsapaper.pdf'
    # S53, S54 -- Katz-Lindell 3rd ed. table of contents and errata (authors).
    get S53-katz-lindell-3rd-toc.pdf \
        'https://www.cs.umd.edu/~jkatz/imc/toc-preface-3rd.pdf'
    get S54-katz-lindell-3rd-errata.pdf \
        'https://www.cs.umd.edu/~jkatz/imc/errata-3rd.pdf'
    # S55 -- Boneh & Shoup, A Graduate Course in Applied Cryptography v0.6.
    get S55-boneh-shoup-v0.6.pdf \
        'https://crypto.stanford.edu/~dabo/cryptobook/BonehShoup_0_6.pdf'
    # S56 (Joy of Cryptography) is online HTML only: https://joyofcryptography.com/
    # NOT fetched: Katz-Lindell [S10] is a commercial textbook, and the past
    # papers [S12-S17] are student uploads of exam papers.
}

case "$MODE" in
    --verify) verify ;;
    --papers) refetch; verify; papers ;;
    *)        refetch; verify ;;
esac

echo
echo "$(ls rfc/*.txt | wc -l | tr -d ' ') RFCs ($(du -sh rfc | cut -f1)), \
$(ls nist/*.pdf | wc -l | tr -d ' ') NIST documents ($(du -sh nist | cut -f1)), \
1 test-vector file ($(du -sh vectors | cut -f1))"
