#!/usr/bin/env bash
# The station analysis as one script: every step in order, in one folder.
set -euo pipefail
DATA="$(cd "$(dirname "$0")/../data" && pwd)/gulf_of_naples.csv"
WORK="${1:?usage: pipeline.sh WORKDIR}"
mkdir -p "$WORK" && cd "$WORK"
cp "$DATA" observations.csv
for s in NAP CAP ISC; do
  awk -F, -v s="$s" '$1==s{t+=$3;n++}END{printf "%s %.2f\n", s, t/n}' \
    observations.csv > "mean_$s.txt"
done
cat mean_NAP.txt mean_CAP.txt mean_ISC.txt > report.txt
