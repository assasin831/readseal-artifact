# REALBIM: ISPA Publication

Current publication of *REALBIM: A Framework for Safe Early Reuse of Shared GPU Buffers Across Processes*, based on the author-supplied r33 source and PDF.

- [Paper PDF](REALBIM_ISPA.pdf)
- [LaTeX source ZIP](REALBIM_ISPA_source.zip)
- [Browsable source and build instructions](source/README.md)
- [Hashes and input provenance](release.json)
- [Comparison with the supplied r33 paper](source/qa/ISPA_publication_check.json)
- [Fresh ZIP extraction and rebuild verification](clean-rebuild-check.json)
- [Experimental evidence](../../README.md#start-here)

## Changes in This Publication

The paper's artifact footnote now links to [ISPA](https://github.com/assasin831/readseal-artifact/tree/ISPA), rather than the historical r19 tag. Both the visible URL and clickable PDF annotation use the new address. ISPA is a maintained publication branch, not an immutable tag; record the Git commit to pin this version.

Three explicit hyphenation rules preserve r33's line breaks across the supplied TeX Live build and the local MiKTeX build. Extracted text is identical on all eight pages after replacing only the artifact URL. All eight figure PDFs, bibliography entries, measured values and experimental records remain unchanged. The supplied PDF and ZIP are identified by SHA-256 in release.json; originals were not overwritten on the author's machine.

The source README and manifest were refreshed. The bundled comparison script had an obsolete expected count of 30 references; this was corrected to the current 25. Earlier files in source/qa and CHANGES.md remain historical records, not checks of this publication.

## Verification

A fresh extraction of the source ZIP builds eight pages. That rebuild matches the published ISPA PDF in page text, geometry, external links and all rendered pixels at 144 and 300 dpi. Fonts are embedded, no Type 3 fonts occur, and the final log has no overfull boxes or unresolved references. Minor rendering differences between this publication and the author-supplied TeX Live PDF are not claimed to be pixel-identical.

From the repository root:

```sh
python tools/verify_manuscript.py
python tools/verify_results.py
python -m unittest discover -s tools -p "test_*.py"
```

The manuscript checker verifies 54 manifest-covered source files plus the manifest itself. The evidence checker validates six unchanged archives, including the 168-run clone comparison and the 108-run jitter/manual campaign. No GPU inference or native experimental auditor was rerun for this publication.
