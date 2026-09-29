# Revision 15 Verification

## Reproducibility

- All six regenerated PPTX slide XML trees match supplied r14 slides exactly: geometry, styles, text, and element order. Package metadata differs.
- All nine CSV SHA-256 hashes are unchanged.
- The paper has six figures, one algorithm, one table, four numbered equations, and eight pages.
- All figure fonts are embedded. Minimum visible sizes range from 5.499 to 6.094 pt at the included physical sizes.
- The paper directly includes vector PDFs at native size. Separate 600 dpi PNGs are supplied.
- Lossless expansion of content/font/image streams preserves extracted text and rendered pixels at 144 dpi on all eight pages.
- Compilation has no unresolved reference/citation or overfull box. Underfull-line warnings in justified prose and long bibliography URLs were visually reviewed.

See export_validation.json and reconstruction_validation.json for hashes and dimensions.

## Visual Review

All eight paper pages and all six figures were inspected, including enlarged figure views. Two-lifetime arrows, trace lanes, boundary ratios, error bars, cap labels, legends, and units remain readable. No content is missing or clipped by the page edge. The bibliography uses an explicit column break; body text remains 10 pt.

## Generic Collision Heuristic

The raw bounding-box checker did **not** return an automated PASS. Its reports are retained without relabeling:

| Figure | Raw FAIL | Raw WARN | Review |
|---|---:|---:|---|
| 1 | 7 | 13 | Stacked-card outlines behind filled cards; text within reader/slot blocks; merged adjacent labels and intentional annotations |
| 2 | 10 | 8 | Adjacent R1-R4 font boxes extend beyond actual glyph ink; rotated policy boxes approach brackets; labels sit within shaded lanes |
| 3 | 23 | 16 | Ratios intentionally placed in colored bars; font boxes reach borders although rendered glyphs remain readable |
| 4 | 14 | 5 | Grid lines and plotting/legend backgrounds intersect broad text boxes; annotations are layered above them |
| 5 | 23 | 0 | Rotated values, masked in-bar annotation, grid/capacity lines, and inset legend regions |
| 6 | 11 | 0 | Category labels merged into long PDF spans crossing a divider; rotated boxes approach bars/grid; deadline annotation |

These are bounding-box/layer findings reviewed against enlarged renders, not certification that the generic checker passed. The one-to-one requirement preserves supplied geometry rather than moving labels solely to satisfy the heuristic.

The Matplotlib/R axes-alignment checker is not applicable to native PowerPoint. No fabricated alignment PASS is claimed. Panel geometry is preserved exactly through slide XML comparison, with axes and panels inspected in rendered PDFs.

## Evidence Boundaries

No experiment was rerun and no new statistical conclusion was inferred. Adverse results and platform limits remain. Public experimental archives, proofs, and prior tags are not rewritten. The bibliography was not independently re-verified.
