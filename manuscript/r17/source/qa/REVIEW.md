# Revision 17 Verification

## Document

- Eight pages; six vector figures; one table; one algorithm; four equations.
- IEEE conference template with unchanged 10 pt body font.
- Final PDF: 4,075,157 bytes; SHA-256
  4ddcfab2d854e4c84c99ff631a9d428b285c86c82c9e012cd64ba1230fef8eca.
- Lossless stream expansion preserves text and 144 dpi pixels on all eight
  pages relative to the compiled LaTeX output.
- No unresolved references/citations, overfull boxes, or text outside pages.
  Remaining underfull warnings concern justified text and reference URLs.
- The clickable evidence link points to the fixed ispa2026-r17 tag.

## Visual Review

All eight pages were rendered with Poppler at 120 dpi and inspected. Title,
author block, prose, table, algorithm, proof, equations, all six figures,
captions, and bibliography are readable without clipped or overlapping blocks.
After the bibliography break was adjusted, the first seven pages were checked
pixel-identical at 144 dpi and page 8 was rendered and inspected again.

| Figure panels | Review |
|---|---|
| 1a / 1b | Graph B appears consistently in registration and timeline; frame labels fit their original text areas. Borrow/identity ordering and all arrows are unchanged. |
| 2 | Revised frame-time axis fits; admission markers, trace bars, and measured hold labels are unchanged. |
| 3 | Both graph-snapshot panels are byte-preserved; new caption explains index-only alias edits. |
| 4a / 4b / 4c / 4d | Three Frame rate axes fit; curves, bounds, means, and late-read bars are unchanged. Caption distinguishes campaigns. |
| 5a / 5b / 5c | Slot/cap, held storage, and deadline panels are byte-preserved, with the original intervals and replicate unit. |
| 6a / 6b | Timely frames axis fits; unchanged bars, pointwise intervals, deadline, and panel labels remain legible. |

## Figure Checks

The label updater changes only native text nodes in four PPTX files. It checks
every other ZIP member and slide attribute against r16. In the four vector
PDFs, a 300 dpi pixel comparison finds zero changes outside the edited label
regions. Fonts remain embedded; minimum rendered span sizes are at least
5.499 pt. Six PNG companions are exported at 600 dpi.

The raw collision reports and r14-to-r15 reconstruction proof are retained as
historical records. No fresh collision-checker PASS is asserted for them.
R15_FIGURE_REVIEW.md explains their original heuristic findings; current
label regions and all panels were visually reviewed again. The pixel-mask
test supplements, rather than replaces, visual review.

## Evidence Checks

All nine CSVs and Figures 3/5 in PDF/PPTX/PNG remain byte-identical to r16.
All four equation bodies and every algorithm operation are unchanged.
The saved maintenance table is checked for 16 transitions, 13 runtime-boundary
changes, all stale-binding rejections, CPU scope, and construction times.
The added base-25/late-30 comparisons are checked against clone_rates.csv.

No new inference, embedded test, stream-only under-load measurement, or
statistical analysis was performed. Four related-work references received the
targeted check documented in REFERENCE_CHECK_R17.md; the inherited
bibliography is not represented as newly audited.
