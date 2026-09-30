# BIM and ReadSeal: ISPA 2026, Revision 21

Source and editable figures for *BIM and ReadSeal: Safe Early Reuse of Shared GPU Buffers Across Processes*.

This is a writing revision of r20. It rewrites the abstract around the paper's story and contributions and makes the paper easier to follow for readers outside GPU systems: key terms are defined at first use, the GPU-capacity line and the two-slot queueing effect are explained, and the Section V-D metrics are separated. Repetition in the introduction, Discussion, and Conclusion was trimmed to keep eight pages. Equations, algorithm, table, references, nine CSVs, and eighteen figure files are unchanged. No experiments were run. See CHANGES.md and qa/verification_r21.json for the exact scope. Older QA records and revision provenance below describe their named earlier versions, not new r21 checks.

## Contents

- BIM_ReadSeal_ISPA2026_r21.pdf: eight-page paper with vector figures and embedded fonts.
- main.tex, refs.bib, IEEEtran.cls, IEEEtran.bst: LaTeX sources.
- figures/: six editable PPTX files, vector PDF exports, and 600 dpi PNG companions.
- data/: nine unchanged figure-data CSVs.
- scripts/: figure generators, saved-data extractors, vector-label revision, PDF export and verification tools.
- CHANGES.md: advice-to-edit record and decisions.
- CAMPAIGNS.md: campaign counts, units, and baseline labels.
- qa/: reconstruction, export, and visual-review records. qa/r18/edit_r18.py reproduces the r18 main.tex from the r17 main.tex with exact-match replacements. qa/r19/ holds the r18-to-r19 unified diff and a latexdiff PDF of the changes. qa/r21/ holds edit_r21.py, which reproduces the r21 main.tex from the r20 main.tex with exact-match replacements, verify_r21.py, and a latexdiff PDF of the r20-to-r21 changes.

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

The last command writes BIM_ReadSeal_ISPA2026_r21.pdf, checks all eight pages against the LaTeX output for identical extracted text and identical 144 dpi pixels, and exports the six 600 dpi figure PNGs. Its current check is qa/export_validation_r21.json. Its lossless stream expansion meets the requested size above 1 MiB without rasterizing pages, adding filler, or changing the displayed content. File size by itself is not a measure of sharpness. The current eight-page build uses the inherited default acknowledgment setting; older pagination claims below concern older revisions.

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

The paper links to the already published [ISPA r19 artifact](https://github.com/assasin831/readseal-artifact/tree/ispa2026-r19), including the [108-run data](https://github.com/assasin831/readseal-artifact/tree/ispa2026-r19/data/jitter-manual-108) and [168-run data](https://github.com/assasin831/readseal-artifact/tree/ispa2026-r19/data/clone-168). This local r20 delivery does not overwrite that tag or claim a new online release.

Saved-data extraction scripts are optional: rebuilding the paper uses the included CSVs. Do not reinterpret unavailable latency values as zero, pool campaigns, or use individual frames as statistical replicates.

## Revision Provenance

This revision starts from the preserved r16 source and reader feedback. OpenAI Codex assisted with readability editing, figure-label changes, evidence cross-checking, and build/visual verification. Experimental values, model code, and campaign records are unchanged. An optional acknowledgment describes this specific assistance; authors should review it and submission requirements before submission. Historical assertions about other tools or borrowed layouts have not been adopted as verified provenance for this revision.

Revision r18 was edited with Anthropic's Claude (language, structure, and page fitting of main.tex; packaging notes). Experimental values, figures, model code, and campaign records are unchanged. The optional acknowledgment, still off by default (\aidisclosurefalse), now names both tools; enabling it keeps the paper at eight pages by dropping one related-work sentence. Authors should decide whether to enable it under the venue's policy.

Revision r19 was also edited with Anthropic's Claude (language, structure, terminology, page fitting of main.tex, two reference-format fixes in refs.bib, and packaging notes). Experimental values, figures, model code, and campaign records are unchanged. The optional acknowledgment is still off by default; both settings build to eight pages.

Revision r21 was edited with Anthropic's Claude (abstract rewrite, readability and flow of main.tex, page fitting, and packaging notes). Experimental values, figures, model code, and campaign records are unchanged. The optional acknowledgment setting is unchanged and off by default; both settings build to eight pages.
