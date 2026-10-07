#!/usr/bin/env bash
# test_slurm_templates.sh - offline checks of the sbatch templates (syntax only).
#
# No Slurm needed.  For every slurm_templates/*.sbatch:
#   1. `bash -n` parses it;
#   2. shebang is #!/bin/bash and the #SBATCH block comes before the first command
#      (Slurm stops reading directives at the first non-comment line);
#   3. every #SBATCH line has the form --key[=value] or -k value;
#   4. --partition and --qos are both given and equal, or the qos is the dev_
#      variant of the partition (ASC requires both [S13]);
#   5. --time is given;
#   6. shellcheck, if installed, reports no errors.
# Exit non-zero on the first failing file.
set -euo pipefail

cd "$(dirname "$0")/slurm_templates"
fail=0
for f in *.sbatch; do
    bash -n "$f" || { echo "FAIL $f: bash -n"; fail=1; continue; }

    [ "$(head -n 1 "$f")" = "#!/bin/bash" ] || { echo "FAIL $f: shebang"; fail=1; }

    # line of the first command vs line of the last #SBATCH directive
    first_cmd=$(grep -n -v -E '^[[:space:]]*(#|$)' "$f" | head -n 1 | cut -d: -f1)
    last_dir=$(grep -n '^#SBATCH' "$f" | tail -n 1 | cut -d: -f1)
    [ "$last_dir" -lt "$first_cmd" ] || { echo "FAIL $f: #SBATCH after first command"; fail=1; }

    # form of each directive (the part before an inline comment)
    while IFS= read -r d; do
        opt=$(printf '%s\n' "$d" | sed -E 's/^#SBATCH[[:space:]]+//; s/[[:space:]]+#.*$//')
        printf '%s\n' "$opt" | grep -Eq '^(--[a-z-]+(=[^[:space:]]+)?|-[A-Za-z] [^[:space:]]+)$' ||
            { echo "FAIL $f: malformed directive '$opt'"; fail=1; }
    done < <(grep '^#SBATCH' "$f")

    part=$(sed -nE 's/^#SBATCH[[:space:]]+(--partition=|-p )([^[:space:]]+).*/\2/p' "$f")
    qos=$(sed -nE 's/^#SBATCH[[:space:]]+(--qos=|-q )([^[:space:]]+).*/\2/p' "$f")
    if [ -z "$part" ] || [ -z "$qos" ]; then
        echo "FAIL $f: partition and qos must both be set"; fail=1
    elif [ "$part" != "$qos" ] && [ "dev_$part" != "$qos" ]; then
        echo "FAIL $f: partition $part vs qos $qos"; fail=1
    fi
    grep -Eq '^#SBATCH[[:space:]]+(--time=|-t )' "$f" || { echo "FAIL $f: no --time"; fail=1; }

    if command -v shellcheck > /dev/null 2>&1; then
        shellcheck -S error "$f" || { echo "FAIL $f: shellcheck"; fail=1; }
    fi
    [ "$fail" -eq 0 ] && echo "ok   $f (partition=$part qos=$qos)"
done
[ "$fail" -eq 0 ] && echo "ALL TEMPLATES OK"
exit "$fail"
