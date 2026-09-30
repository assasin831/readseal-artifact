# BIM and ReadSeal: ISPA 2026 Artifact

Evidence for *BIM and ReadSeal: Safe Early Reuse of Shared GPU Buffers Across Processes*.

The current paper and evidence entry is the fixed [ISPA r19 release](https://github.com/assasin831/readseal-artifact/tree/ispa2026-r19). It includes the revised manuscript, editable figures, both additional performance campaigns, their saved correctness records, and earlier experiments. It is an artifact for submission, not a claim of acceptance. The [r17](https://github.com/assasin831/readseal-artifact/tree/ispa2026-r17), [r16](https://github.com/assasin831/readseal-artifact/tree/ispa2026-r16), [r15](https://github.com/assasin831/readseal-artifact/tree/ispa2026-r15), and original [ISPA r1](https://github.com/assasin831/readseal-artifact/tree/ispa2026-r1) releases remain unchanged.

## Current Paper

- [Revision 19 PDF](manuscript/r19/BIM_ReadSeal_ISPA2026_r19.pdf): eight pages, vector figures, embedded fonts.
- [Complete source ZIP](manuscript/r19/BIM_ReadSeal_ISPA2026_r19_source.zip): LaTeX, six editable PPTX figures, vector PDFs, 600 dpi PNGs, CSVs, and verification records.
- [Browse source and build instructions](manuscript/r19/source/README.md).
- [Revision notes](manuscript/r19/source/CHANGES.md), [campaign/terminology guide](manuscript/r19/source/CAMPAIGNS.md), [file hashes](manuscript/r19/release.json).

Revision 19 applies checked reader feedback to the author-supplied r18: recipient processes and reader components are distinguished, the ResNet boundary example and evaluation roadmap are restored, algorithm symbols and the empty read-set convention are defined, and the measured 25 Hz dip is explained. Web references use consistent access dates and repaired documentation links. All nine figure-data CSVs and all eighteen figure files are byte-identical to r18. The clean source-ZIP rebuild matches all eight delivered pages in text and rendered pixels. Experimental archives and proof records below are byte-preserved; no experiments were rerun.

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
