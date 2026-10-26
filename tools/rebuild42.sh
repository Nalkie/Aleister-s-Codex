#!/bin/sh
# Rehace src.html y index.html desde el último backup anterior al parche móvil (iterar sobre tools/mobile.css).
set -e
cd "$(dirname "$0")/.."
if [ -f src.before_patch42.html ]; then cp src.before_patch42.html src.html; fi
python tools/patch_src42.py
python tools/page_only.py
