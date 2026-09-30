# BIM and ReadSeal: ISPA 2026 Artifact

Evidence for *BIM and ReadSeal: Safe Early Reuse of Shared GPU Buffers Across Processes*.

The current paper and evidence entry is the fixed [ISPA r21 source-reconstruction release](https://github.com/assasin831/readseal-artifact/tree/ispa2026-r21-source1). It includes the unchanged author-approved paper, PDF-matched LaTeX source, both additional performance campaigns, their saved correctness records, and earlier experiments. It is an artifact for submission, not a claim of acceptance. The original [r21 upload](https://github.com/assasin831/readseal-artifact/tree/ispa2026-r21), [r19](https://github.com/assasin831/readseal-artifact/tree/ispa2026-r19), [r17](https://github.com/assasin831/readseal-artifact/tree/ispa2026-r17), [r16](https://github.com/assasin831/readseal-artifact/tree/ispa2026-r16), [r15](https://github.com/assasin831/readseal-artifact/tree/ispa2026-r15), and [ISPA r1](https://github.com/assasin831/readseal-artifact/tree/ispa2026-r1) releases remain unchanged.

## Current Paper

- [Revision 21 PDF](manuscript/r21/BIM_ReadSeal_ISPA2026_r21.pdf): the separately supplied eight-page paper, preserved byte-for-byte.
- [Reconstructed source ZIP](manuscript/r21/BIM_ReadSeal_ISPA2026_r21_source.zip): self-contained editable LaTeX, bibliography, document class, six vector figures, build scripts and current verification records.
- [Reconstruction notes](manuscript/r21/README.md), [browse source and build instructions](manuscript/r21/source/README.md), [file hashes](manuscript/r21/release.json).
- [Rebuilt comparison PDF](manuscript/r21/BIM_ReadSeal_ISPA2026_r21_rebuilt.pdf) and [page-by-page verification](manuscript/r21/reconstruction-verification.json).
- [Historical editable figures and campaign guide](https://github.com/assasin831/readseal-artifact/tree/ispa2026-r21/manuscript/r21/source) remain at the original r21 tag.

The reconstructed source replaces the previous source directory and ZIP on the main branch. A fresh ZIP extraction and compilation reproduces all eight pages of the approved PDF with identical extracted text and identical rendered pixels at 144 and 300 dpi. Visible content and experimental values were not edited. The package has a fresh [manifest](manuscript/r21/source/MANIFEST.json) and no stale bundled manuscript or historical editing scripts. The canonical PDF, existing r19 evidence link, archives, and proof records below are unchanged; no experiments were rerun.

## Start Here

| Experiment | Measured evidence | Read online | Download |
|---|---|---|---|
| Matched clone-on-accept | 168 formal runs and 8 smoke runs; six repetitions per condition and method | [Per-run CSV](data/clone-168/per_run.csv), [summaries](data/clone-168/summary_t95.csv), [paired differences](data/clone-168/paired_t95.csv) | [168-run archive](archives/ispa2026-clone-168.zip) |
| Jitter and component-heterogeneous recipients | 108 formal runs and 18 smoke runs; all 97,200 scheduled publications in the formal denominator | [Per-run CSV](data/jitter-manual-108/per_run.csv), [publication CSV](data/jitter-manual-108/publications.csv), [summaries](data/jitter-manual-108/summary_t95.csv) | [108-run archive](archives/ispa2026-jitter-manual-108.zip) |
| Manual boundaries with identical binding checks | Matched performance cells in the same 108 runs; 48 native cases, 24 update cases, 6 cancellation cases, 155 rejection witnesses and 600 exact tensor comparisons | [Gate report](provenance/corrected-gate/native_gate_report.json), [saved-only audit](provenance/corrected-gate/native_gate_audit.json), [paired differences](data/jitter-manual-108/paired_t95.csv) | [Same 108-run archive](archives/ispa2026-jitter-manual-108.zip) |

The third row is not another 108-run campaign. Smoke runs and CPU tests are not formal performance results.

- [Results and limitations](RESULTS.md)
- [File and metric guide](DATA_GUIDE.md)
- [Verification and reproduction](ARTIFACT.md)
- [Gate correction and evidence provenance](PROVENANCE.md)
- [Archive and file SHA-256 inventory](evidence-index.json)

## Main Findings

With homogeneous recipients at 30 source publications/s, BIM completes 65.5% of publications on time under periodic arrivals and 63.5% under jitter, compared with Full retention's 50.0% and 48.0%. With component-heterogeneous recipients, including a late reader, clone-on-accept instead reaches 82.6% and 80.7%, compared with BIM's 50.3% and 58.5%. Copying increases the sampled device-memory peak by 256 MiB. Checked manual boundaries produce similar observed performance to automatically derived boundaries; the comparison does not establish statistical equivalence.

The separate 168-run campaign also contains outcomes favorable to copying: higher timely recipient goodput at 25 source publications/s and in the all-late condition, with worse late-condition latency and freshness. Its recipient-level metric must not be substituted for complete-publication timely fraction.

## Earlier Evidence

The paper also uses earlier campaigns, preserved without modification:

| Archive | Coverage |
|---|---|
| [Rate, late-read and slot evidence](archives/ispa2026-rate-slots-evidence.zip) | Earlier 108-run rate sweep, 36-run late-read test, model transitions, and slot/deadline records |
| [Core evidence](archives/ispa2026-core-evidence.zip) | Mechanism and output checks, isolated cost, 96-run slots window and 54-run confirmation |
| [Model and view evidence](archives/ispa2026-model-view-evidence.zip) | Saved model outputs, grouped requests and follow-up records |
| [Load sensitivity](archives/ispa2026-load-sensitivity-evidence.zip) | 72-run load scan and deadline sensitivity |

The earlier 108-run rate sweep is distinct from the new 108-run jitter/manual campaign. Campaigns are never pooled or paired across waves.

## Scope

GPU measurements use an A100, not an embedded automotive device. The heterogeneous profiles are components and variants of the measured model composition, not four independently trained autonomous-driving models. There is no Jetson/DRIVE validation, end-to-end vehicle-stack measurement, or device simulation. Historical paths inside immutable evidence archives remain intact for hash verification; the current submission entry and download names use ISPA.
