# Revision 16 Verification

## Document

- Eight pages; six vector figures; one table; one algorithm; four numbered equations.
- Body font remains the IEEE conference template's 10 pt. Final bibliography columns are balanced by an explicit reference break.
- The final PDF is 3,359,343 bytes. Its SHA-256 is cba9d840ce2dbc92c75338521c3399bdaf0bc5c139253bb221318042b7371637.
- Lossless PDF stream expansion preserves text and 144 dpi rendered pixels on all eight pages relative to the compiled LaTeX output.
- The final log has no unresolved references/citations or overfull boxes. Remaining underfull warnings in justified prose and bibliography URLs were visually reviewed.
- The paper's clickable evidence link points to the fixed ispa2026-r16 tag.

## Visual Review

All eight final pages were rendered with Poppler at 120 dpi and inspected. Equations, proof, algorithm, table, figures, captions, and bibliography are readable, with no clipped page content or overlapping blocks. The final bibliography adjustment changed only page 8; hashes of the seven earlier Poppler renders stayed identical, and page 8 was inspected again.

## Preserved Assets

scripts/verify_revision.py checks the nine CSV files, eighteen figure files (six PDF/PPTX/PNG sets), and bibliography byte-for-byte against r15. All four equation bodies are unchanged. Algorithm operations are unchanged; only frame terminology and grammatical clarification differ.

The r15 reconstruction proof and raw figure-collision reports are retained as historical records. No new figure reconstruction or collision-checker PASS is claimed. See R15_FIGURE_REVIEW.md for the original manual adjudication of heuristic findings. Because every figure file is byte-identical, its drawing geometry and fonts are preserved.

## Evidence Cross-Check

revision_validation.json records the exact saved maintenance table and archive hashes. It checks 16 transitions, 13 runtime-boundary field changes, the two alias-chain cases and folding case without such a change, the actual rejection messages (including the public-model CPU check), and construction timings. This check reads archived records and starts no inference.

The manuscript no longer equates operation-index shifts with semantic boundary changes or review-field differences with measured developer edits. The maintained-manual safety comparison is consistent with its binding checks.

No new experiment, benchmark selection, statistical reanalysis, embedded validation, or independent bibliography audit was performed. Source packaging verification is recorded separately in release.json and MANIFEST.json.
