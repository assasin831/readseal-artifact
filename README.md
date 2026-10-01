# REALBIM

Artifact for **REALBIM: A Framework for Safe Early Reuse of Shared GPU Buffers Across Processes**, ISPA 2026 submission.

REALBIM separates the lifetime of shared GPU storage from the identity of the frame stored in it. BIM protects recipients from publication onward; ReadSeal derives and checks the last source read inside each recipient.

## Paper and Source

- [Paper PDF](manuscript/ISPA/REALBIM_ISPA.pdf)
- [LaTeX source ZIP](manuscript/ISPA/REALBIM_ISPA_source.zip)
- [Build instructions and figure sources](manuscript/ISPA/source/README.md)
- [File hashes and build checks](manuscript/ISPA/README.md)

The paper links to the [ISPA branch](https://github.com/assasin831/readseal-artifact/tree/ISPA). Use a commit hash to identify a particular version.

## Experiments

| Experiment | Runs | Data | Archive |
|---|---|---|---|
| Clone-on-accept comparison | 168 formal, 8 smoke | [Run-level results](data/clone-168/per_run.csv), [summaries](data/clone-168/summary_t95.csv), [paired differences](data/clone-168/paired_t95.csv) | [Download](archives/ispa2026-clone-168.zip) |
| Jitter and mixed recipients | 108 formal, 18 smoke | [Run-level results](data/jitter-manual-108/per_run.csv), [97,200 scheduled frames](data/jitter-manual-108/publications.csv), [summaries](data/jitter-manual-108/summary_t95.csv) | [Download](archives/ispa2026-jitter-manual-108.zip) |
| Hand-placed boundaries with matched checks | Included in the 108 formal runs | [Paired differences](data/jitter-manual-108/paired_t95.csv), [update and safety tests](provenance/corrected-gate/native_gate_report.json), [audit](provenance/corrected-gate/native_gate_audit.json) | Same archive |

The rate, slot, deadline and model-change studies are in these archives:

- [Rate, late-read and slot studies](archives/ispa2026-rate-slots-evidence.zip)
- [Correctness, execution cost and slot studies](archives/ispa2026-core-evidence.zip)
- [Model and view tests](archives/ispa2026-model-view-evidence.zip)
- [Load and deadline sensitivity](archives/ispa2026-load-sensitivity-evidence.zip)

## Documentation

- [Results and interpretation](RESULTS.md)
- [Data fields, method labels and figure-to-data map](DATA_GUIDE.md)
- [Verification and reproduction](ARTIFACT.md)
- [Experimental provenance and gate correction](PROVENANCE.md)
- [Evidence checksums](evidence-index.json)

Measurements use one A100 and replayed features. The mixed recipients are component profiles, not four independently trained driving models. No embedded-board or end-to-end vehicle-stack evaluation is included. Smoke runs and CPU software tests are separate from formal performance measurements.
