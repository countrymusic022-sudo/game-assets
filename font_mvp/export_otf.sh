#!/usr/bin/env bash
set -euo pipefail

INPUT="${1:-font_mvp/GalaxyLeoKing-MVP.svg}"
OUTPUT="${2:-font_mvp/GalaxyLeoKing-MVP.otf}"

if ! command -v fontforge >/dev/null 2>&1; then
  echo "fontforge not found. Install FontForge first, then rerun." >&2
  exit 1
fi

fontforge -script font_mvp/export_otf_with_fontforge.pe "$INPUT" "$OUTPUT"
echo "Done: $OUTPUT"
