# ISPA r21: PDF-Matched LaTeX Source

This update replaces the previous main-branch LaTeX source directory and ZIP with a self-contained reconstruction matched to the author-approved PDF. The canonical paper and all experimental records are unchanged. No experiments were run. The fixed tag is `ispa2026-r21-source1`; the earlier `ispa2026-r21` tag preserves the replaced upload.

- [Canonical paper PDF](BIM_ReadSeal_ISPA2026_r21.pdf): the unchanged author-approved eight-page PDF, 954,817 bytes.
- [Reconstructed source ZIP](BIM_ReadSeal_ISPA2026_r21_source.zip): 651,672 bytes, 18 files including its refreshed manifest.
- [Browse the editable LaTeX](source/main.tex) and [build instructions](source/README.md).
- [Rebuilt PDF](BIM_ReadSeal_ISPA2026_r21_rebuilt.pdf): a separate normal pdfLaTeX output, 1,301,820 bytes.
- [Reconstruction comparison](reconstruction-verification.json), [source inventory](source/MANIFEST.json), and [release hashes](release.json).

## Verified Against the Current PDF

The delivered ZIP was extracted into a fresh directory and compiled with its included PowerShell build script. All eight pages match the canonical PDF in extracted text and rendered pixels at both 144 and 300 dpi. All 26 references, all six vector figures, and the external PDF links remain unchanged. Fonts are embedded, no Type 3 fonts are present, and the final log has no overfull boxes or undefined references/citations. All eight pages were also visually inspected.

The rebuild uses real editable text, mathematics, algorithm and table environments, and the original vector figure PDFs. It does not embed the paper as full-page images. Seven hyphenation exceptions fix cross-distribution line breaks, and an explicit Unicode mapping preserves the union symbol's extracted text. Inactive source switches and stale source metadata were removed, without changing visible content. Compression, object numbering and PDF metadata account for different byte hashes and file sizes; they do not change the matched pages.

## Build and Integrity

Compile `source/main.tex` using pdfLaTeX and BibTeX, or run `source/build.ps1` on Windows / `sh source/build.sh` on Linux or macOS. No Python or PDF post-processing is needed for compilation. The optional PDF comparison script requires PyMuPDF. The clean ZIP omits the old embedded manuscript PDF and historical editing/QA files; those remain accessible at the previous tag.

From the repository root:

```sh
python tools/verify_manuscript.py --revision r21
```

The repository verifier checks the canonical and rebuilt PDF hashes, source ZIP, and all 17 source-manifest entries. The separate reconstruction reports record the completed compilation and visual/text comparisons; none of these are new experimental measurements.

## Experimental Evidence

The paper still links to the fixed [ISPA r19 evidence tag](https://github.com/assasin831/readseal-artifact/tree/ispa2026-r19). That link and all prior tags remain unchanged. This source update also retains the same [108-run jitter/manual data](../../data/jitter-manual-108), [168-run clone data](../../data/clone-168), and [evidence guide](../../DATA_GUIDE.md), without rerunning or changing the measurements.
