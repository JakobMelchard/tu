#!/usr/bin/env bash
# Download the free (cite-only) PDFs listed in SOURCES.md into ./cite-only
# (git-ignored). None of them carries a redistribution licence, so they are
# fetched for personal study and never committed; nothing is vendored.
# The course book [S1] is not free and is not fetched.
set -euo pipefail

cd "$(dirname "$0")"
mkdir -p cite-only

UA='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36'

get() {  # get <name> <url>
    local out="cite-only/$1" url="$2"
    if [ -s "$out" ]; then echo "have  $out"; return; fi
    echo "fetch $out"
    curl -fsSL -A "$UA" --max-time 90 -o "$out" "$url" || { echo "FAILED $out ($url)" >&2; rm -f "$out"; }
}

get S6-herlihy-wing-1990-linearizability.pdf      'https://cs.brown.edu/~mph/HerlihyW90/p463-herlihy.pdf'
get S7-herlihy-1991-wait-free-synchronization.pdf 'https://cs.brown.edu/~mph/Herlihy91/p124-herlihy.pdf'
get S8-blumofe-leiserson-1999-work-stealing.pdf \
    'https://www.csd.uwo.ca/~mmorenom/CS433-CS9624/Resources/Scheduling_multithreaded_computations_by_work_stealing.pdf'
get S9-chase-lev-2005-deque.pdf                   'http://www.dre.vanderbilt.edu/~schmidt/PDF/work-stealing-dequeue.pdf'
get S11-lamport-1974-bakery.pdf                   'https://lamport.azurewebsites.net/pubs/bakery.pdf'
get S12-treiber-1986-rj5118.pdf                   'https://dominoweb.draco.res.ibm.com/reports/rj5118.pdf'   # timed out 2026-09-28
get S13-mellor-crummey-scott-1991-mcs.pdf         'https://www.cs.rochester.edu/u/scott/papers/1991_TOCS_synch.pdf'
get S14-michael-scott-1996-queues.pdf             'https://www.cs.rochester.edu/u/scott/papers/1996_PODC_queues.pdf'
get S15-harris-2001-lock-free-lists.pdf           'https://www.cl.cam.ac.uk/research/srg/netos/papers/2001-caslists.pdf'
get S16-heller-et-al-2005-lazy-list.pdf           'https://people.csail.mit.edu/shanir/publications/Lazy_Concurrent.pdf'
get S17-hendler-shavit-yerushalmi-2004-elimination.pdf 'https://people.csail.mit.edu/shanir/publications/Lock_Free.pdf'
get S18-shalev-shavit-2006-split-ordered.pdf      'https://people.csail.mit.edu/shanir/publications/Split-Ordered_Lists.pdf'
get S19-boehm-adve-2008-cpp-memory-model.pdf      'https://rsim.cs.illinois.edu/Pubs/08PLDI.pdf'
get S23-sewell-et-al-2010-x86-tso.pdf             'https://www.cl.cam.ac.uk/~pes20/weakmemory/cacm.pdf'
get S24-pulte-et-al-2018-armv8.pdf                'https://www.cl.cam.ac.uk/~pes20/armv8-mca/armv8-mca-draft.pdf'
get S25-le-et-al-2013-work-stealing-weak-memory.pdf 'https://fzn.fr/readings/ppopp13.pdf'
get S26-michael-2004-hazard-pointers.pdf          'https://www.cs.otago.ac.nz/cosc440/readings/hazard-pointers.pdf'
get S27-fraser-2004-practical-lock-freedom.pdf    'https://www.cl.cam.ac.uk/techreports/UCAM-CL-TR-579.pdf'
get S28-lamport-1979-sequential-consistency.pdf   'https://lamport.azurewebsites.net/pubs/multi.pdf'
get S29-fischer-lynch-paterson-1985-flp.pdf       'https://groups.csail.mit.edu/tds/papers/Lynch/jacm85.pdf'
get S30-pugh-1990-skip-lists.pdf                  'https://15721.courses.cs.cmu.edu/spring2018/papers/08-oltpindexes1/pugh-skiplists-cacm1990.pdf'
get S31-n4659-cpp17-draft.pdf                     'https://www.open-std.org/jtc1/sc22/wg21/docs/papers/2017/n4659.pdf'
get S32-boehm-2011-benign-races.pdf               'https://www.hboehm.info/boehm-hotpar11.pdf'

echo
echo "Web pages (read in a browser, not downloaded):"
echo "  S20 https://en.cppreference.com/w/cpp/atomic/memory_order"
echo "  S21 https://preshing.com/20120515/memory-reordering-caught-in-the-act/  (and three more, see SOURCES.md)"
echo "  S22 https://herbsutter.com/2013/02/11/atomic-weapons-the-c-memory-model-and-modern-hardware/"
echo
echo "Paywalled or not free (open the DOI / buy the book):"
echo "  S1  Herlihy & Shavit, The Art of Multiprocessor Programming (ISBN 9780123973375; 2nd ed. 9780124159501)"
echo "  S10 Peterson 1981   https://doi.org/10.1016/0020-0190(81)90106-X"
echo "  S36 Burns & Lynch 1993 (Information and Computation 107(2))"
