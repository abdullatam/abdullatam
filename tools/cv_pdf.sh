#!/bin/sh
# Render assets/ABDULLA_TAMIMI_CV.pdf from assets/ABDULLA_TAMIMI_CV.docx.
#
# The .docx is the source of truth — the PDF exists only so the CV can be read
# in the browser, because GitHub renders a PDF in its own viewer and cannot
# render a .docx at all. Run this after every edit to the .docx, or the two
# drift apart and the button hands out an old CV.
#
#     sh tools/cv_pdf.sh
#
# textutil (macOS) carries the document's styling into HTML; Chrome prints it.
# Word's own export would be more faithful still, but its AppleScript bridge
# refuses the save-as, so this is the reproducible path.
set -e
root=$(cd "$(dirname "$0")/.." && pwd)
doc="$root/assets/ABDULLA_TAMIMI_CV.docx"
tmp=$(mktemp -d)
textutil -convert html -output "$tmp/cv.html" "$doc"
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
  --headless --disable-gpu --no-pdf-header-footer \
  --print-to-pdf="$root/assets/ABDULLA_TAMIMI_CV.pdf" "file://$tmp/cv.html" 2>/dev/null
rm -rf "$tmp"
echo "assets/ABDULLA_TAMIMI_CV.pdf  <-  assets/ABDULLA_TAMIMI_CV.docx"
