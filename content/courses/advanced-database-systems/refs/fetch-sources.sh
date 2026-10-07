#!/usr/bin/env bash
# Sources for 184.780 Advanced Database Systems (see SOURCES.md, README.md).
#
#   ./fetch-sources.sh --verify    checksums of the vendored files, no network
#   ./fetch-sources.sh             re-fetch missing vendored files, then verify
#   ./fetch-sources.sh --papers    the above, plus the cite-only PDFs into
#                                  ./cite-only (git-ignored, personal use only)
#
# vendor/ holds only permissively licensed files (SQLite docs: public domain;
# PostgreSQL docs: PostgreSQL License, notice in vendor/LICENSE-PostgreSQL.txt).
# Everything in cite-only/ is free to read but NOT licensed for redistribution.
# No TUWEL material: it needs a login.
set -euo pipefail

cd "$(dirname "$0")"
MODE="${1:-refetch}"

# published name -> URL, one per line: "<file> <url>"
VENDORED='
sqlite-lang_with.html https://www.sqlite.org/lang_with.html
pg18-queries-with.html https://www.postgresql.org/docs/18/queries-with.html
pg18-plpgsql-trigger.html https://www.postgresql.org/docs/18/plpgsql-trigger.html
pg18-plpgsql-cursors.html https://www.postgresql.org/docs/18/plpgsql-cursors.html
pg18-plpgsql-control-structures.html https://www.postgresql.org/docs/18/plpgsql-control-structures.html
pg18-functions-window.html https://www.postgresql.org/docs/18/functions-window.html
'

verify() {
    (cd vendor && shasum -a 256 -c SHA256SUMS)
}

refetch() {
    mkdir -p vendor
    echo "$VENDORED" | while read -r name url; do
        [ -z "$name" ] && continue
        if [ -s "vendor/$name" ]; then continue; fi
        echo "fetch vendor/$name"
        curl -fsSL -o "vendor/$name" "$url"
    done
}

papers() {
    mkdir -p cite-only
    get() {  # get <name> <url>
        if [ -s "cite-only/$1" ]; then echo "have  cite-only/$1"; return; fi
        echo "fetch cite-only/$1"
        curl -fsSL -m 120 -o "cite-only/$1" "$2" || { rm -f "cite-only/$1"; echo "  failed (fetch by hand)"; }
    }
    # S2-S6: VoWi student material (unknown licence, personal study only)
    V='https://vowi.fsinf.at/images'
    get S3-vowi-exam-prep-block1-2026.pdf "$V/d/df/TU_Wien-Datenbanksysteme_Vertiefung_VU_%28Pichler%29_-_ADBS_Exam_prep_Block_1_SS2026.pdf"
    get S4-vowi-exam2-cheatsheet-2026.pdf "$V/1/13/TU_Wien-Datenbanksysteme_Vertiefung_VU_%28Pichler%29_-_Adbs-exam2-cheatsheet-2026.pdf"
    get S5-vowi-ex3-cheatsheet.pdf "$V/f/f0/TU_Wien-Datenbanksysteme_Vertiefung_VU_%28Pichler%29_-_Adbs-ex3-cheatsheet.pdf"
    get S6-vowi-exam-2020-06-solution.pdf "$V/0/0c/TU_Wien-Datenbanksysteme_Vertiefung_VU_%28Pichler%29_-_Exam_2020-06_%28reference_solution%29.pdf"
    # S7 Abiteboul/Hull/Vianu: "one copy for personal use but not for distribution"
    get S7-abiteboul-hull-vianu-foundations.pdf 'http://webdam.inria.fr/Alice/pdfs/all.pdf'
    get S8-green-et-al-datalog-2013.pdf 'http://blogs.evergreen.edu/sosw/files/2014/04/Green-Vol5-DBS-017.pdf'
    get S16-dean-ghemawat-mapreduce-2004.pdf 'https://static.googleusercontent.com/media/research.google.com/en//archive/mapreduce-osdi04.pdf'
    get S17-mmds-ch2-mapreduce.pdf 'http://infolab.stanford.edu/~ullman/mmds/ch2n.pdf'
    get S18-afrati-et-al-mr-bounds-2013.pdf 'https://arxiv.org/pdf/1206.4377'
    get S19-zaharia-et-al-rdd-2012.pdf 'https://www.usenix.org/system/files/conference/nsdi12/nsdi12-final138.pdf'
    get S21-armbrust-et-al-spark-sql-2015.pdf 'https://people.csail.mit.edu/matei/papers/2015/sigmod_spark_sql.pdf'
    get S24-decandia-et-al-dynamo-2007.pdf 'https://www.allthingsdistributed.com/files/amazon-dynamo-sosp2007.pdf'
    get S25-chang-et-al-bigtable-2006.pdf 'https://static.googleusercontent.com/media/research.google.com/en//archive/bigtable-osdi06.pdf'
    get S26-gilbert-lynch-cap-2002.pdf 'https://users.ece.cmu.edu/~adrian/731-sp04/readings/GL-cap.pdf'
    get S26b-gilbert-lynch-perspectives-cap-2012.pdf 'https://groups.csail.mit.edu/tds/papers/Gilbert/Brewer2.pdf'
    get S28-abadi-pacelc-2012.pdf 'https://www.cs.umd.edu/~abadi/papers/abadi-pacelc.pdf'
    get S29-bailis-et-al-hat-2014.pdf 'https://www.vldb.org/pvldb/vol7/p181-bailis.pdf'
    get S30-bailis-et-al-pbs-2012.pdf 'https://arxiv.org/pdf/1204.6082'
    get S31-lamport-clocks-1978.pdf 'https://lamport.azurewebsites.net/pubs/time-clocks.pdf'
    get S32-karger-et-al-consistent-hashing-1997.pdf 'https://www.cs.princeton.edu/courses/archive/fall09/cos518/papers/chash.pdf'
    get S33-oneil-et-al-lsm-tree-1996.pdf 'https://www.cs.umb.edu/~poneil/lsmtree.pdf'
    get S40-abadi-et-al-column-compression-2006.pdf 'https://www.cs.umd.edu/~abadi/papers/abadisigmod06.pdf'
    get S41-gray-lamport-transaction-commit-2006.pdf 'https://www.microsoft.com/en-us/research/uploads/prod/2004/01/twophase-revised.pdf'
}

case "$MODE" in
    --verify) verify ;;
    --papers) refetch; verify; papers ;;
    *)        refetch; verify ;;
esac
