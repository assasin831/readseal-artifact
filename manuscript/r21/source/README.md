# BIM and ReadSeal: r21 Reconstructed LaTeX Source

This is the current, self-contained LaTeX source for the author-approved eight-page PDF supplied on September 30, 2026. It replaces the previous source download, not the paper's content or experimental evidence.

Reference PDF SHA-256:

`2bd634e559d3bc5a477431e41413829e73975548e0075f40dae383ffec5e3972`

## Build

Select `main.tex` as the main document and **pdfLaTeX** as the compiler. A normal LaTeX installation with the packages imported by `main.tex` is sufficient. No Python, PowerPoint, GPU, network data fetch, or PDF post-processing is needed to build the paper.

On Windows PowerShell:

```powershell
./build.ps1
```

On Linux or macOS:

```sh
sh build.sh
```

The equivalent commands, also suitable for a LaTeX editor, are:

```sh
pdflatex -interaction=nonstopmode -halt-on-error main.tex
bibtex main
pdflatex -interaction=nonstopmode -halt-on-error main.tex
pdflatex -interaction=nonstopmode -halt-on-error main.tex
```

Output: `main.pdf`. On Overleaf, upload this ZIP, choose `main.tex`, and compile with pdfLaTeX. `main.bbl` is included as a bibliography snapshot; BibTeX can regenerate it from `refs.bib` and `IEEEtran.bst`.

## Contents

- `main.tex`: editable title, authors, abstract, body text, equations, algorithm, table and captions.
- `refs.bib`, `main.bbl`, `IEEEtran.bst`: reference database, generated bibliography and bibliography style.
- `IEEEtran.cls`: the document class used by the reference paper.
- `figures/*.pdf`: the six original vector figures. Their bytes are unchanged.
- `build.ps1`, `build.sh`: ordinary LaTeX build commands.
- `verify_pdf.py`: optional text and render comparison with the approved PDF.
- `qa/pdf_match.json`: checks from the reconstruction build.
- `qa/clean_rebuild.json`: checks from a separate fresh extraction and build.
- `MANIFEST.json`: SHA-256 and length for each included file except the manifest itself.

The paper is not reproduced by embedding page images or by including the original PDF. It remains an editable LaTeX document. There is no stale bundled manuscript PDF, obsolete writing history, old executable editing script, or inherited checksum manifest in this package.

## Reconstruction and Verification

All visible content, numbers, equations, citations, table entries, figure files and PDF links are preserved. Inactive source switches and stale comments were removed. Seven explicit hyphenation exceptions reproduce the reference line breaks across TeX distributions. A Unicode mapping for the large union glyph preserves copying and searching of Eq. (2), without changing its appearance.

The local pdfLaTeX build was compared with the approved PDF, page by page. All eight pages have identical extracted text and identical rendered pixels at both 144 and 300 dpi. All fonts are embedded, no Type 3 fonts are present, and the final build has no overfull boxes or unresolved citations/references. A few inherited underfull warnings do not affect the matched layout. Other TeX or font versions may vary in rendering, so use the optional comparison to check another environment.

The optional check needs Python and PyMuPDF 1.28.2:

```sh
python verify_pdf.py --reference /path/to/approved.pdf --candidate main.pdf --output comparison.json
```

PDF byte hashes need not match because metadata, stream compression and object numbering can differ. The comparison does not pad the PDF or rasterize its pages. File size is not a measure of sharpness.

## Evidence

The manuscript's existing [ISPA r19 evidence link](https://github.com/assasin831/readseal-artifact/tree/ispa2026-r19) remains unchanged, including the [108-run records](https://github.com/assasin831/readseal-artifact/tree/ispa2026-r19/data/jitter-manual-108) and [168-run records](https://github.com/assasin831/readseal-artifact/tree/ispa2026-r19/data/clone-168). This reconstruction does not rerun experiments or alter measurements. Earlier manuscript packages, editable figure originals and historical provenance remain available in the repository's fixed tags.
