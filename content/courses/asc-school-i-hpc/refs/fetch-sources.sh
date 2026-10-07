#!/usr/bin/env bash
# Download the cite-only material listed in SOURCES.md into ./cite-only
# (git-ignored).  None of these files carries a redistribution licence, so they
# are fetched for personal study and never committed.  See README.md.
#
# Everything that *is* redistributable is already in vendor/ and needs no
# download.
set -euo pipefail

cd "$(dirname "$0")"
mkdir -p cite-only

UA='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36'

get() {  # get <name> <url>
    local out="cite-only/$1" url="$2"
    if [ -s "$out" ]; then
        echo "have  $out"
        return
    fi
    echo "fetch $out"
    curl -fsSL -A "$UA" -o "$out" "$url" || { rm -f "$out"; echo "FAILED $url" >&2; }
}

# ---------------------------------------------------------------- block 1 + 2
# S9 - the ASC-Intro decks (Blaas-Schenner et al.), as linked from the
# 23.03.2026 and 15.10.2025 Indico events.  These are THE source for the
# partition names, the job-script shape and the hardware figures.
E=https://events.asc.ac.at/event
get asc_intro+login.pdf "$E/275/attachments/270/815/asc_intro+login.pdf"
get slurm_basics.pdf    "$E/275/attachments/270/816/slurm_basics.pdf"
get slurm_advanced.pdf  "$E/275/attachments/270/813/slurm_advanced.pdf"
get gpus.pdf            "$E/275/attachments/270/812/gpus.pdf"
get support_ticket.pdf  "$E/275/attachments/270/814/support_ticket.pdf"
get file_storage.pdf    "$E/191/attachments/179/639/file_storage.pdf"
get spack.pdf           "$E/191/attachments/179/638/spack.pdf"
get eessi.pdf           "$E/191/attachments/180/630/eessi.pdf"
get conda.pdf           "$E/191/attachments/179/636/conda.pdf"
# marked OUTDATED by ASC itself, kept because note 05 cites their command shapes
get compiling.pdf       "$E/191/attachments/180/628/compiling.pdf"
get singularity.pdf     "$E/191/attachments/179/633/singularity.pdf"
# S7 - the Linux Primer as a rendered deck (the markdown source is vendored)
get asc-linux-primer.pdf \
    'https://gitlab.tuwien.ac.at/vsc-public/training/linux-primer/-/raw/main/linux_primer.pdf'
get ASC-Linux_intro.pdf "$E/206/attachments/172/618/ASC-Linux_intro.pdf"

# ---------------------------------------------------------------- block 3
# S12 - the HLRS MPI course slides the ASC block is built on.  HLRS permits
# personal download only; do not redistribute these files or anything derived
# from them (see README.md).
H=https://fs.hlrs.de/projects/par
get mpi_3.1_rab.pdf          "$H/par_prog_ws/pdf/mpi_3.1_rab.pdf"
get mpi_3.1_rab-animated.pdf "$H/par_prog_ws/pdf/mpi_3.1_rab-animated.pdf"
get MPI31single.tar.gz       "$H/par_prog_ws/practical/MPI31single.tar.gz"
get TEST.tar.gz              "$H/events/TEST.tar.gz"

# S14 - Blaas-Schenner's own add-on decks.  The ASC course page still links
# these under vsc.ac.at, which no longer resolves; asc.ac.at serves them.
V=https://asc.ac.at/fileadmin/user_upload/vsc/online-courses/MPI
get mpi_bp_cb.pdf "$V/mpi_bp_cb.pdf"
get mpi_io_cb.pdf "$V/mpi_io_cb.pdf"
get MPI-2025-04_intro+addons.pdf "$E/183/attachments/136/522/MPI-2025-04_intro+addons.pdf"

# S20 - the collective cost model the table in ../notes/09 now follows.
get thakur-rabenseifner-gropp-2005-collectives.pdf \
    'https://www.mcs.anl.gov/~thakur/papers/ijhpca-coll.pdf'

# ---------------------------------------------------------------- hands-on
# S11 - the course's own labs, in C, Fortran and Python.  CC BY-SA 4.0 for the
# notebooks, but with HLRS-copyrighted material inside, so: clone, do not vendor.
if [ -d cite-only/mpi/.git ]; then
    echo "have  cite-only/mpi (git pull)"
    git -C cite-only/mpi pull --ff-only || true
else
    echo "clone cite-only/mpi"
    git clone --depth 1 https://gitlab.tuwien.ac.at/vsc-public/training/MPI cite-only/mpi || true
fi

echo
echo "cite-only/ now holds:"
du -sh cite-only 2>/dev/null || true
echo
echo "The redistributable sources are already in vendor/; check them with:"
echo "  shasum -a 256 vendor/*"
