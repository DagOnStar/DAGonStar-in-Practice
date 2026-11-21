#!/bin/bash
# Export decks to PDF with Microsoft PowerPoint (macOS), to check how slides really render.
#
#     tools/export_decks_powerpoint.sh A2 A4 48     # some decks
#     tools/export_decks_powerpoint.sh              # every deck
#
# PowerPoint is sandboxed, so decks are copied to its container and the PDFs are written there;
# the script prints the folder.  Then, for example: pdftoppm -r 60 -png <pdf> <prefix>
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
OUT="$HOME/Library/Containers/com.microsoft.Powerpoint/Data/deck-export"
mkdir -p "$OUT"
ids=("$@")
[ ${#ids[@]} -eq 0 ] && ids=("")
for id in "${ids[@]}"; do
  for deck in "$ROOT"/en/lectures/"$id"*-DAGonStar-*.pptx; do
    name="$(basename "$deck" .pptx)"
    cp "$deck" "$OUT/$name.pptx"
    osascript <<EOF
tell application "Microsoft PowerPoint"
  open POSIX file "$OUT/$name.pptx"
  delay 3
  save active presentation in POSIX file "$OUT/$name.pdf" as save as PDF
  close active presentation saving no
end tell
EOF
    echo "exported $name.pdf"
  done
done
echo "PDFs in $OUT"
