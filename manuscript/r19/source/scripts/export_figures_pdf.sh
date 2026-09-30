#!/bin/sh
# Export every PowerPoint figure (figures/*.pptx) to the vector PDF of the same name used by main.tex.
# Each slide is the printed size of its figure, so the PDF page is the figure; no cropping is needed.
# Uses LibreOffice with lossless image compression and no downsampling, so the icons stay sharp.
# (From PowerPoint itself: File > Save As > PDF gives the same page.)
# Set SOFFICE to a wrapper command if plain `soffice` does not run headless on your machine.
# Usage: sh scripts/export_figures_pdf.sh [name ...]      (default: all figures)
set -e
cd "$(dirname "$0")/../figures"
SOFFICE=${SOFFICE:-soffice}
if [ "$#" -gt 0 ]; then LIST="$*"; else LIST="fig1_overview fig2_trace fig3_boundaries fig5_delivery fig6_slots fig7_mixed"; fi
for f in $LIST; do
  $SOFFICE --headless --convert-to \
    'pdf:impress_pdf_Export:{"UseLosslessCompression":{"type":"boolean","value":"true"},"ReduceImageResolution":{"type":"boolean","value":"false"},"EmbedStandardFonts":{"type":"boolean","value":"true"}}' \
    "$f.pptx" >/dev/null
  echo "exported figures/$f.pdf"
done
