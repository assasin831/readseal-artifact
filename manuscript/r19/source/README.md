# BIM and ReadSeal: ISPA 2026, Revision 19

Source and editable figures for *BIM and ReadSeal: Safe Early Reuse of Shared GPU Buffers Across Processes*.

This revision applies the checked readability feedback to the supplied r18 source. It clarifies recipient processes versus reader components, restores the ResNet boundary explanation and evaluation roadmap, defines the borrow-bit notation, handles an empty read set in the formal boundary definition, and explains the measured 25 Hz dip. All nine CSVs and all six PDF/PPTX/PNG figure sets are unchanged. No experiments are rerun. CHANGES.md records the edits, reference-link repairs, and scope.

## Contents

- BIM_ReadSeal_ISPA2026_r19.pdf: eight-page paper with vector figures and embedded fonts.
- main.tex, refs.bib, IEEEtran.cls, IEEEtran.bst: LaTeX sources.
- figures/: six editable PPTX files, vector PDF exports, and 600 dpi PNG companions.
- data/: nine unchanged figure-data CSVs.
- scripts/: figure generators, saved-data extractors, vector-label revision, PDF export and verification tools.
- CHANGES.md: advice-to-edit record and decisions.
- CAMPAIGNS.md: campaign counts, units, and baseline labels.
- qa/: current r19 checks and explicitly historical reconstruction/revision records. Current checks are revision_validation_r19.json and export_validation_r19.json; the unsuffixed revision_validation.json belongs to r17. qa/r18/edit_r18.py is the historical r18 editing script, not a build step for r19.

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

The last command writes BIM_ReadSeal_ISPA2026_r19.pdf, checks all eight pages against the LaTeX output for identical extracted text and identical 144 dpi pixels, and exports the six 600 dpi figure PNGs. Its lossless stream expansion meets the requested size above 1 MiB without rasterizing pages, adding filler, or changing the displayed content. File size by itself is not a measure of sharpness.

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

The paper links to the fixed [ISPA r19 artifact](https://github.com/assasin831/readseal-artifact/tree/ispa2026-r19). The [108-run data](https://github.com/assasin831/readseal-artifact/tree/ispa2026-r19/data/jitter-manual-108) and [168-run data](https://github.com/assasin831/readseal-artifact/tree/ispa2026-r19/data/clone-168) remain byte-preserved, along with earlier archives and their original hashes. Earlier manuscript tags remain available.

Saved-data extraction scripts are optional: rebuilding the paper uses the included CSVs. Do not reinterpret unavailable latency values as zero, pool campaigns, or use individual frames as statistical replicates.

## Revision Provenance

The earlier r17 revision started from the preserved r16 source and reader feedback. Its record describes OpenAI Codex assistance with readability editing, figure-label changes, evidence cross-checking, and build/visual verification. Experimental values, model code, and campaign records were unchanged. Historical assertions about other tools or borrowed layouts have not been adopted as verified provenance for that revision.

The supplied r18 source records Anthropic Claude assistance with language, structure, page fitting, and packaging notes. Revision r19 uses OpenAI Codex for the requested clarity edits, reference access checks, and build verification. Experimental values, figures, model code, and campaign records are unchanged. The optional acknowledgment remains off by default (\aidisclosurefalse); authors should review it under the venue's policy. Enabling it requires rebuilding and checking pagination rather than assuming the default layout remains unchanged.
