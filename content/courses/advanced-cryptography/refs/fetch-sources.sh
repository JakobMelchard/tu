#!/usr/bin/env bash
# Verify (and if necessary re-fetch) the vendored standards, and optionally
# download the free cite-only papers into ./cite-only, which is git-ignored.
# See README.md for why FIPS 203/204 and RFC 7748/8032 are vendored and the
# papers are not. 192.115 Advanced Cryptography, sources as of 2026-09-28.
#
#   ./fetch-sources.sh --verify    checksums only, no network
#   ./fetch-sources.sh             re-fetch anything missing, then verify
#   ./fetch-sources.sh --papers    the above, plus the free papers
set -euo pipefail

cd "$(dirname "$0")"
MODE="${1:-refetch}"

verify() {
    (cd rfc  && shasum -a 256 -c SHA256SUMS)
    (cd nist && shasum -a 256 -c SHA256SUMS)
}

refetch() {
    mkdir -p rfc nist
    for n in 7748 8032; do
        out="rfc/rfc$n.txt"
        [ -s "$out" ] && continue
        echo "fetch $out"
        curl -fsS -o "$out" "https://www.rfc-editor.org/rfc/rfc$n.txt"
    done
    for f in NIST.FIPS.203.pdf NIST.FIPS.204.pdf; do
        out="nist/$f"
        [ -s "$out" ] && continue
        echo "fetch $out"
        curl -fsSL -o "$out" "https://nvlpubs.nist.gov/nistpubs/FIPS/$f"
    done
}

papers() {
    mkdir -p cite-only
    get() {  # get <name> <url>
        if [ -s "cite-only/$1" ]; then echo "have  cite-only/$1"; return; fi
        echo "fetch cite-only/$1"
        curl -fsSL -o "cite-only/$1" "$2" \
            || { echo "  failed (cite-only source, fetch by hand)"; return; }
        # publishers sometimes answer with an HTML page instead of the PDF
        if [ "$(head -c 4 "cite-only/$1")" != "%PDF" ]; then
            echo "  not a PDF (paywall or bot page?), removed; fetch by hand: $2"
            rm -f "cite-only/$1"
        fi
    }
    # the three free items of the TISS literature list [S2]
    get S4-boneh-shoup-v0.6.pdf  'https://crypto.stanford.edu/~dabo/cryptobook/BonehShoup_0_6.pdf'
    get S6-peikert-decade.pdf    'https://eprint.iacr.org/2015/939.pdf'
    get S7-lindell-mpc.pdf       'https://eprint.iacr.org/2020/300.pdf'
    # papers
    get S8-bellare-rogaway-ro.pdf        'https://cseweb.ucsd.edu/~mihir/papers/ro.pdf'
    get S9-fiat-shamir.pdf               'https://link.springer.com/content/pdf/10.1007/3-540-47721-7_12.pdf'
    get S13-lindell-pinkas-yao.pdf       'https://eprint.iacr.org/2004/175.pdf'
    get S14-shamir-secret.pdf            'https://web.mit.edu/6.857/OldStuff/Fall03/ref/Shamir-HowToShareASecret.pdf'
    get S15-regev-lwe.pdf                'https://cims.nyu.edu/~regev/papers/qcrypto.pdf'
    get S18-groth16.pdf                  'https://eprint.iacr.org/2016/260.pdf'
    get S19-bulletproofs.pdf             'https://eprint.iacr.org/2017/1066.pdf'
    get S21-sec2-v2.pdf                  'https://www.secg.org/sec2-v2.pdf'
    get S26-pointcheval-stern.pdf        'https://www.di.ens.fr/david.pointcheval/Documents/Papers/2000_joc.pdf'
    get S27-bellare-neven-forking.pdf    'https://cseweb.ucsd.edu/~mihir/papers/multisignatures.pdf'
    get S28-cgh-rom-revisited.pdf        'https://eprint.iacr.org/1998/011.pdf'
    get S32-ggpr-qsp.pdf                 'https://eprint.iacr.org/2012/215.pdf'
    get S33-bpw-weak-fiat-shamir.pdf     'https://eprint.iacr.org/2016/771.pdf'
    get S34-shor.pdf                     'https://arxiv.org/pdf/quant-ph/9508027'
    get S35-proos-zalka.pdf              'https://arxiv.org/pdf/quant-ph/0301141'
    get S37-galbraith-mpkc.pdf           'https://www.math.auckland.ac.nz/~sgal018/crypto-book/main.pdf'
    get S39-kyber.pdf                    'https://eprint.iacr.org/2017/634.pdf'
    get S40-dilithium.pdf                'https://eprint.iacr.org/2017/633.pdf'
    get S41-hhk-fo.pdf                   'https://eprint.iacr.org/2017/604.pdf'
    get S42-fkl-agm.pdf                  'https://eprint.iacr.org/2017/620.pdf'
    get S43-schnorr-tight.pdf            'https://eprint.iacr.org/2024/1528.pdf'
    # S44 VoWi is behind a bot check; open it in a browser:
    echo "S44 (browser only): https://vowi.fsinf.at/wiki/TU_Wien:Advanced_Cryptography_VU_(Fuchsbauer)"
    # NOT fetched: Katz-Lindell [S5], Hankerson-Menezes-Vanstone [S20]
    # (commercial), and the ACM/IEEE/Springer-only papers S10-S12, S29-S31, S45.
}

case "$MODE" in
    --verify) verify ;;
    --papers) refetch; verify; papers ;;
    *)        refetch; verify ;;
esac

echo
echo "$(ls rfc/*.txt | wc -l | tr -d ' ') RFCs ($(du -sh rfc | cut -f1)), \
$(ls nist/*.pdf | wc -l | tr -d ' ') NIST documents ($(du -sh nist | cut -f1))"
