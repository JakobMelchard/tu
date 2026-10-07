#!/usr/bin/env bash
# Download the cite-only sources listed in SOURCES.md into ./vendor (git-ignored).
# Text only: assignment PDFs, plus the lecture captions and descriptions.
# No video is downloaded. None of these files carry a redistribution licence, so
# they are fetched for personal study and never committed. See README.md.
set -euo pipefail

cd "$(dirname "$0")"
mkdir -p vendor

UA='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36'

get() { # get <name> <url> [referer]
    local out="vendor/$1" url="$2" ref="${3-}"
    if [ -s "$out" ]; then
        echo "have  $out"
        return
    fi
    echo "fetch $out"
    if [ -n "$ref" ]; then
        curl -fsSL -A "$UA" -e "$ref" -o "$out" "$url" || echo "FAILED $out (see note below)"
    else
        curl -fsSL -A "$UA" -o "$out" "$url" || echo "FAILED $out"
    fi
}

# --- S12, S13, S14: the three official assignment sheets, via VoWi. ------------
# VoWi runs an Anubis proof-of-work bot gate, so plain curl usually gets an HTML
# challenge page instead of the PDF. If a file below is small and starts with
# "<!DOCTYPE html", open the URL in a real browser and save it into vendor/.
V=https://vowi.fsinf.at/images
P=TU_Wien-Applied_Deep_Learning_VU_%28Pacha%29
get S12-assignment-1-initiate.pdf "$V/5/5d/${P}_-_Assignment_1_-_Initiate.pdf" https://vowi.fsinf.at/
get S13-assignment-2-hacking.pdf  "$V/f/f6/${P}_-_Assignment_2_-_Hacking.pdf"  https://vowi.fsinf.at/
get S14-assignment-3-deliver.pdf  "$V/0/08/${P}_-_Assignment_3_-_Deliver.pdf"  https://vowi.fsinf.at/

for f in vendor/S1[234]-*.pdf; do
    [ -s "$f" ] || continue
    if head -c 20 "$f" | grep -qi '<!doctype\|<html'; then
        echo "  !! $f is the bot-gate HTML page, not the PDF. Fetch it in a browser."
    fi
done

# --- S4, S5: the lecture series. Captions and descriptions only, no video. -----
# Needs yt-dlp (brew install yt-dlp). ~600 kB of text for all 15 lectures.
PLAYLIST_2025=https://www.youtube.com/playlist?list=PLNsFwZQ_pkE8H1o874cZbiwnNRJ6hCDJI
if command -v yt-dlp >/dev/null 2>&1; then
    mkdir -p vendor/lectures-2025
    (cd vendor/lectures-2025 && yt-dlp --no-update \
        --skip-download --write-auto-subs --sub-lang en --sub-format vtt \
        --write-description \
        -o "%(playlist_index)02d-%(id)s.%(ext)s" "$PLAYLIST_2025")
    echo "captions and descriptions in vendor/lectures-2025/"
    echo "the '== Literature ==' block of each .description is the lecture's own reading list"
else
    echo "yt-dlp not installed; skipping the lecture captions (brew install yt-dlp)"
fi

# Earlier editions, if you want to diff the syllabus year on year (S6, S7):
#   2024  https://www.youtube.com/playlist?list=PLNsFwZQ_pkE8tSQuU3jN71fmmGFFCi7Dc
#   2023  https://www.youtube.com/playlist?list=PLNsFwZQ_pkE87JO3T_mvedVTlw0sjUzKh
#   2022  https://www.youtube.com/playlist?list=PLNsFwZQ_pkE_QaTwYxoTmmRJHtMXyIAU6
#   2021  https://www.youtube.com/playlist?list=PLNsFwZQ_pkE_wsWK3t6NEeYtwOorGfowm
#   2020  https://www.youtube.com/playlist?list=PLNsFwZQ_pkE8xNYTEyorbaWPN7nvbWyk1

# --- S15: Goodfellow et al. is HTML-only on the authors' site; no PDF to fetch.
echo
echo "S15 Deep Learning (Goodfellow et al.) reads free at https://www.deeplearningbook.org/"
echo "S16 Sutton & Barto PDF:"
get S16-sutton-barto-rlbook2020.pdf 'http://incompleteideas.net/book/RLbook2020.pdf'

echo
echo "done. vendor/ is git-ignored; nothing here is redistributable."
