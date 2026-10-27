#!/usr/bin/env bash
# Render every design-sketch SVG to a PNG of the same pixel size with headless Edge.
# Usage (repo root): bash design/tools/render_png.sh
# Set EDGE to msedge.exe if Edge is not in its default install folder.
EDGE="${EDGE:-$(cygpath -u "$(printenv 'ProgramFiles(x86)')")/Microsoft/Edge/Application/msedge.exe}"
DIRS="${@:-design/character design/storyboard}"
for f in $(for d in $DIRS; do ls $d/*.svg; done); do
  w=$(grep -o 'width="[0-9]*"' "$f" | head -1 | grep -o '[0-9]*')
  h=$(grep -o 'height="[0-9]*"' "$f" | head -1 | grep -o '[0-9]*')
  out="$(cygpath -w "$(pwd)/${f%.svg}.png")"
  "$EDGE" --headless=new --disable-gpu --hide-scrollbars --force-device-scale-factor=1 \
    --window-size="$w,$h" --screenshot="$out" "file:///$(cygpath -m "$(pwd)/$f")" >/dev/null 2>&1
  echo "rendered ${f%.svg}.png ${w}x${h}"
done
