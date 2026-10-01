# Data Guide

## Method Labels

| Saved label | Paper label | Meaning |
|---|---|---|
| `auto-batched` | REALBIM | Automatically derived read boundaries |
| `manual-checked` | REALBIM (hand-placed) | Explicit boundaries with identical binding and stage checks |
| `manual-early` | Hand-placed | Independently implemented manual release runtime |
| `manual-full` | Full retention | Retain source through output completion |
| `copy-in` | Clone-on-accept | Copy the source into recipient-owned storage at acceptance |

Saved labels are unchanged so source code, CSVs and proof records remain consistent. Earlier records use BIM for the evaluated system, Manual for Hand-placed, and Manual-checked for REALBIM (hand-placed).

## Jitter and Mixed Recipients (108 Runs)

All files below are in [data/jitter-manual-108](data/jitter-manual-108).

| File | Rows or role |
|---|---|
| `per_run.csv` | 108 formal runs, including condition, method, repetition, source schedule hash and run-level metrics |
| `smoke_per_run.csv` | 18 smoke runs, excluded from formal estimates |
| `publications.csv` | 97,200 rows, one for every scheduled publication in every formal run |
| `recipients.csv` | 432 recipient-run rows: four recipients per formal run |
| `summary_t95.csv` | 234 rows: 18 condition-method cells times 13 metrics |
| `paired_t95.csv` | 169 rows: 13 within-condition contrasts against REALBIM times 13 metrics |
| `run_data.json` | Saved run-level data used by the exporter |
| `validation.json` | Export completeness and coverage checks, not new GPU measurements |
| `prepared.json`, `input_evidence.json`, `analysis_sources.json` | Frozen input/source bindings, input evidence and exporter source hashes |
| `native_gate.json` | Gate evidence included with the export |
| `files.json` | Original export manifest; its `README.md` entry refers to the original README inside the ZIP |

`full_publication_timely_fraction` divides complete timely publications by **all scheduled publications**. Publication-level `complete_correct` and `complete_timely` retain the denominator even when recipients were rejected or only partly admitted. Per-run P99 is computed among complete, correct publications; means and intervals summarize six per-run quantiles, not pooled frame latencies. Empty metric cells mean unavailable and must not be treated as zero or silently omitted from a six-run interval.

## Separate 168-Run Campaign

[data/clone-168](data/clone-168) contains `per_run.csv` (168 formal rows), `summary_t95.csv`, `paired_t95.csv` and the original analysis `validation.json`. The [ZIP](archives/ispa2026-clone-168.zip) also includes the 8 smoke records, execution schedule, manifests, controller evidence and original scripts. Its throughput counts recipient bundles; this denominator differs from the 108-run campaign's complete-publication metric.

## Paper-to-Evidence Map

| Paper result | Evidence |
|---|---|
| Fig. 4, one-slot trace at 20 Hz | Rate/slots archive, E1 repetition 0 timelines |
| Fig. 5 and model boundary/update tests | Core and rate/slots archives; matched update cases in corrected native gate |
| Fig. 6, rate and late-read campaigns | Rate/slots archive, E1 (108 runs) and E2 (36 runs) |
| Fig. 7, slots and deadline re-scoring | Rate/slots archive `prior_v11/evidence`; 96-run window, distinct 54-run confirmation in core evidence |
| Fig. 8 and Section V-D, jitter and mixed recipients | 108-run campaign; figure covers 96 runs, text also reports the 12 all-late control runs |
| Section V-D, clone rate comparison | Separate 168-run campaign |
| Section V-E, checked manual update cases | Corrected gate report and saved-only audit |
| Section V-F, isolated cost and model/view coverage | Core and model/view archives |

Figure numbers refer to the [current paper](manuscript/ISPA/REALBIM_ISPA.pdf). Figures 1-3 illustrate the scenario, lifetimes and framework. The [source guide](manuscript/ISPA/source/README.md) maps all eight figures to their filenames. Maintenance review fields in the saved model-change records are not measurements of developer effort.

Historical archive member names are provenance identifiers, not current venue branding. Use the ISPA download index rather than editing those members.
