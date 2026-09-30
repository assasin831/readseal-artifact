# Author-Supplied ISPA r21 Upload

This release publishes the PDF and source ZIP supplied by the authors on September 30, 2026. Both files are preserved byte-for-byte; only their public download filenames follow the repository's revision naming convention. The manuscript was not edited, recompiled, or re-exported for this upload. No experiments were run.

- [Current paper PDF](BIM_ReadSeal_ISPA2026_r21.pdf): the separately supplied eight-page PDF, 954,817 bytes.
- [Original source ZIP](BIM_ReadSeal_ISPA2026_r21_source.zip): 4,724,334 bytes, with all 77 original members preserved.
- [Browse the supplied source](source/main.tex) and [original build instructions](source/README.md).
- [Release records and original filenames](release.json).
- [External source checksum inventory](source-manifest.json).

## Which PDF Is Current?

Use the paper linked above, outside `source/`. The ZIP also contains an older, 4,065,708-byte file named `BIM_ReadSeal_ISPA2026_r21.pdf`. That bundled file is retained as supplied and is not this release's canonical PDF. The separately supplied PDF is not padded to match older file-size preferences.

## Source Integrity

The supplied ZIP's `MANIFEST.json` has one stale checksum entry, `main.tex`; its other 75 entries match. The original manifest, source, README, and historical QA records are not silently rewritten. The external `source-manifest.json` records the actual bytes of all 77 ZIP members, including that original manifest. The public verifier uses this external inventory for r21 and checks it against both the ZIP and the browsable source tree.

From the repository root:

```sh
python tools/verify_manuscript.py --revision r21
```

This is an upload-integrity check, not a new compilation, visual-quality claim, or experimental validation. Statements in the source package about earlier builds and local deliveries remain historical.

## Experimental Evidence

The paper still links to the fixed [ISPA r19 evidence tag](https://github.com/assasin831/readseal-artifact/tree/ispa2026-r19). That link and all prior tags remain unchanged. This r21 tag also retains the same [108-run jitter/manual data](../../data/jitter-manual-108), [168-run clone data](../../data/clone-168), and [evidence guide](../../DATA_GUIDE.md), without rerunning or changing the measurements.
