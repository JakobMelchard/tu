#!/usr/bin/env bash
# Fetch the free sources of 184.686 Database Systems.
#
#   ./fetch-sources.sh --verify   checksums of the vendored SQLite pages, no network
#   ./fetch-sources.sh            re-fetch missing vendored pages, verify
#   ./fetch-sources.sh --papers   the above, plus the cite-only PDFs/pages into
#                                 ./cite-only (git-ignored, personal copies only)
#
# vendor/sqlite/ holds SQLite documentation pages, which are public domain
# ("All of the code and documentation in SQLite has been dedicated to the
# public domain", https://www.sqlite.org/copyright.html). Everything else is
# copyrighted without a redistribution grant and goes to cite-only/.
# Never fetches TUWEL. See README.md and SOURCES.md.
set -euo pipefail

cd "$(dirname "$0")"
MODE="${1:-refetch}"
SQLITE_PAGES="nulls.html queryplanner.html optoverview.html isolation.html
atomiccommit.html fileformat2.html
eqp.html copyright.html"

verify() {
    (cd vendor/sqlite && shasum -a 256 -c SHA256SUMS)
}

refetch() {
    mkdir -p vendor/sqlite
    for p in $SQLITE_PAGES; do
        out="vendor/sqlite/$p"
        [ -s "$out" ] && continue
        echo "fetch $out"
        curl -fsSL -o "$out" "https://www.sqlite.org/$p"
    done
    if [ ! -s vendor/sqlite/SHA256SUMS ]; then
        (cd vendor/sqlite && shasum -a 256 $SQLITE_PAGES > SHA256SUMS)
    fi
}

papers() {
    mkdir -p cite-only
    get() {  # get <name> <url>
        if [ -s "cite-only/$1" ]; then echo "have  cite-only/$1"; return; fi
        echo "fetch cite-only/$1"
        curl -fsSL -A 'Mozilla/5.0' -o "cite-only/$1" "$2" \
            || echo "  failed (cite-only source, fetch by hand)"
    }
    # S6: Silberschatz/Korth/Sudarshan 7th ed. slides, "authorized for personal use".
    for ch in 2 3 4 6 7 13 14 15 16 17 18 19; do
        get "S6-dbsc7-ch$ch.pdf" "https://www.db-book.com/slides-dir/PDF-dir/ch$ch.pdf"
    done
    # S9: Codd 1970 (ACM copyright; course copy at UPenn).
    get S9-codd-1970-relational-model.pdf 'https://www.seas.upenn.edu/~zives/03f/cis550/codd.pdf'
    # S10: Abiteboul/Hull/Vianu, one personal copy permitted by the authors.
    get S10-abiteboul-hull-vianu-foundations.pdf 'http://webdam.inria.fr/Alice/pdfs/all.pdf'
    # S11: Chen 1976, first five pages, on the author's page.
    get S11-chen-1976-er-model.pdf 'https://www.csc.lsu.edu/~chen/pdf/erd-5-pages.pdf'
    # S14: Selinger et al. 1979 (course copy at Duke).
    get S14-selinger-1979-access-path.pdf \
        'https://courses.cs.duke.edu/compsci516/cps216/spring03/papers/selinger-etal-1979.pdf'
    # S16: Hellerstein/Stonebraker/Hamilton 2007, on the authors' site.
    get S16-hellerstein-architecture-dbms.pdf 'https://dsf.berkeley.edu/papers/fntdb07-architecture.pdf'
    # S19: Berenson et al. 1995, arXiv cs/0701157.
    get S19-berenson-critique-ansi-isolation.pdf 'https://arxiv.org/pdf/cs/0701157'
    # S20: Mohan et al. 1992, ARIES (course copy at Stanford).
    get S20-mohan-1992-aries.pdf 'https://cs.stanford.edu/people/chrismre/cs345/rl/aries.pdf'
    # S22: PostgreSQL documentation (PostgreSQL Licence; cited, not vendored).
    for p in transaction-iso.html mvcc-intro.html using-explain.html indexes-types.html functions-comparison.html queries-order.html; do
        get "S22-postgresql-$p" "https://www.postgresql.org/docs/current/$p"
    done
}

case "$MODE" in
    --verify) verify ;;
    --papers) refetch; verify; papers ;;
    *)        refetch; verify ;;
esac
echo
echo "$(wc -l < vendor/sqlite/SHA256SUMS | tr -d ' ') SQLite pages, $(du -sh vendor/sqlite | cut -f1) in vendor/sqlite/"
