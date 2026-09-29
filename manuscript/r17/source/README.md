# BIM and ReadSeal: ISPA 2026, Revision 17

Source and editable figures for *BIM and ReadSeal: Safe Early Reuse of Shared GPU Buffers Across Processes*.

This revision applies the next round of reader feedback to r16. It sharpens the contribution beyond existing release protocols, simplifies maintenance reporting, shows measured copying comparisons, and aligns figure terminology with the text. No experiments are rerun. All nine CSV files remain byte-identical to r16. Four figures have label-only edits; their editable slide geometry and their PDF pixels outside the edited labels are unchanged. Figures 3 and 5 remain byte-identical.

## Contents

- BIM_ReadSeal_ISPA2026_r17.pdf: eight-page paper with vector figures and embedded fonts.
- main.tex, refs.bib, IEEEtran.cls, IEEEtran.bst: LaTeX sources.
- figures/: six editable PPTX files, vector PDF exports, and 600 dpi PNG companions.
- data/: nine unchanged figure-data CSVs.
- scripts/: figure generators, saved-data extractors, vector-label revision, PDF export and verification tools.
- CHANGES.md: advice-to-edit record and decisions.
- CAMPAIGNS.md: campaign counts, units, and baseline labels.
- qa/: reconstruction, export, and visual-review records.

## Build the Paper

Requirements: LaTeX with pdflatex and BibTeX; Python with PyMuPDF 1.28.2. The included vector figures can be used directly without Node.js or PowerPoint.

On Windows, with tools on PATH:

    ./build.ps1 -Python python

Alternatively:

    pdflatex -interaction=nonstopmode -halt-on-error main.tex
    bibtex main
    pdflatex -interaction=nonstopmode -halt-on-error main.tex
    pdflatex -interaction=nonstopmode -halt-on-error main.tex
    python scripts/finalize_pdf.py

The last command writes BIM_ReadSeal_ISPA2026_r17.pdf, checks all eight pages against the LaTeX output for identical extracted text and identical 144 dpi pixels, and exports the six 600 dpi figure PNGs. Its lossless stream expansion meets the requested size above 1 MiB without rasterizing pages, adding filler, or changing the displayed content. File size by itself is not a measure of sharpness.

## Regenerate Editable Figures

Install Node.js and the pinned package in package.json:

    npm install
    npm run figures

For the full Windows rebuild, install LibreOffice and the Calibri fonts used by the supplied PPTX source, then run:

    ./build.ps1 -Python python -RegenerateFigures

Text, bars, curves, panels, and arrows are native editable PowerPoint elements. The two small icons in Fig. 1 reuse the exact embedded PNG assets supplied in r14; they are not regenerated illustrations. The supplied source identifies their icon families as Tabler and Phosphor (MIT). See assets/README.md.

Original filename numbering is retained to keep data and script paths stable:

| Paper figure | File stem | Content |
|---|---|---|
| 1 | fig1_overview | Architecture and two lifetimes |
| 2 | fig2_trace | One-slot timing trace |
| 3 | fig3_boundaries | Model-update read boundaries |
| 4 | fig5_delivery | Delivery, latency, hold time, late-read control |
| 5 | fig6_slots | Slot/cap comparison, held source storage, deadlines |
| 6 | fig7_mixed | Jitter and mixed-recipient results |

Algorithm 1 retains the role it has in r14 and r15. No seventh figure or historical mechanism PDF is inserted.

The retained verify_reconstruction.py and reconstruction_validation.json describe the historical r14-to-r15 reconstruction, before r17's terminology changes. They are not new r17 tests. To reproduce and validate the label-only update against the fixed r16 source (requires PyMuPDF, NumPy, and installed Calibri fonts):

    python scripts/update_figure_labels.py --prior path/to/BIM_ReadSeal_ISPA2026_r16_source

This edits native PPTX text and vector-PDF text, not a raster overlay. It preserves all non-text PPTX content, embeds subset fonts, and requires zero changed pixels outside the edited label regions at 300 dpi. Its report is qa/label_revision_validation.json. The figure generators use the same new labels; a full slide-renderer export may differ typographically and should be visually checked.

## Public Evidence

The paper links to the fixed [ISPA r17 artifact](https://github.com/assasin831/readseal-artifact/tree/ispa2026-r17). The existing [108-run data](https://github.com/assasin831/readseal-artifact/tree/ispa2026-r17/data/jitter-manual-108) and [168-run data](https://github.com/assasin831/readseal-artifact/tree/ispa2026-r17/data/clone-168) remain available, along with earlier archives and their original hashes.

Saved-data extraction scripts are optional: rebuilding the paper uses the included CSVs. Do not reinterpret unavailable latency values as zero, pool campaigns, or use individual frames as statistical replicates.

## Revision Provenance

This revision starts from the preserved r16 source and reader feedback. OpenAI Codex assisted with readability editing, figure-label changes, evidence cross-checking, and build/visual verification. Experimental values, model code, and campaign records are unchanged. An optional acknowledgment describes this specific assistance; authors should review it and submission requirements before submission. Historical assertions about other tools or borrowed layouts have not been adopted as verified provenance for this revision.
