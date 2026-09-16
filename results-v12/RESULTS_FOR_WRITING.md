# ReadSeal V12: Verified Results for Writing

This package adds experiments and analysis, not a rewritten manuscript. The V11 paper is unchanged.

## Start Here
- E1_E2/E1_runs.csv: 108 new formal runs, R=1, K=0, rates 10/15/20/25/30/40 Hz.
- E1_E2/E2_runs.csv: 36 separate new formal runs, R=1, K=0, 30 Hz, base and late-read variants.
- E1_E2/E1_E2_method_means.csv: means, goodput error bars, source hold, occupancy and lateness diagnostics.
- validation/gpu_independent_local/E1_E2_paired_summary.csv: paired differences and pointwise 95% intervals.
- E3/: review-field changes, 20 CPU constructor timing snapshots, and explicit counting scope.
- E4/: normal host phases, separate inclusive profiles, and diagnostic comparisons.
- E7/: dated environment for this window only.
- prior_v11/: all compact evidence used by the V11 manuscript; retained as separate measurement windows.
- cpu_raw/: underlying CPU records. raw/ARCHIVE.json identifies the separately distributed full raw archive.
- source/: the new experiment, audit and packaging programs.

DATA_DICTIONARY.md defines counts, timestamps, units and missing values.

## Measurement Contract
There are six paired whole-run repetitions per condition. Each formal run has 2 s warm-up, 12 s measured planned-arrival cohort and a complete drain. Four recipients are offered per source publication. A goodput event is a delivered recipient bundle with verified source identity, matching reference outputs and receipt within 100 ms of its planned arrival. Publication-rate Hz is not recipient-bundle Hz. All new GPU runs use the full TransFusion-head A/B/C pipeline and the frozen GPU0 implementation.
Intervals use 20,000 paired whole-run bootstrap draws (n=6 pairs), not per-request independent samples. They are pointwise, not simultaneous curve bands. Six smoke runs are not pooled into formal estimates. The overlapping E1 30 Hz base condition and E2 base condition remain separate fresh observations.

## E1: One-Slot Rate Curve
| Source rate (Hz) | ReadSeal goodput | Full-retention goodput | Paired difference [95% CI] |
|---:|---:|---:|---:|
| 10 | 40.000 | 40.000 | +0.000 [+0.000, +0.000] |
| 15 | 59.958 | 59.944 | +0.014 [+0.000, +0.042] |
| 20 | 78.278 | 40.056 | +38.222 [+37.944, +38.500] |
| 25 | 75.000 | 50.000 | +25.000 [+25.000, +25.000] |
| 30 | 78.556 | 59.972 | +18.583 [+18.444, +18.722] |
| 40 | 79.000 | 53.333 | +25.667 [+25.500, +25.833] |

## E2: Delayed Source Read
| Variant | ReadSeal goodput | Full-retention goodput | Paired difference [95% CI] |
|---|---:|---:|---:|
| Base | 78.611 | 59.944 | +18.667 [+18.500, +18.833] |
| Late read | 60.000 | 60.000 | +0.000 [+0.000, +0.000] |

## E3: Maintenance, Not Developer Labor
The primary table has 16 transitions: 14 constructed edits, one head BN-folding transformation and one controlled public ResNet-18 to ResNet-50 substitution. A second BN-folding row is reported separately.
The records change 43 review fields, of which 29 are runtime-used fields. These include 13 boundary changes and 16 binding refreshes.
A review readers-list is documentary, not consulted by the complete manual executor. A hash refresh can be mechanically generated. Neither count is observed human editing effort, developer error rate or lines of code. ReadSeal uses no manually supplied source-reader/boundary annotations in these constructors; export, native contracts, topology, operator review and output dependencies remain application work. Stale-guarded complete manual implementations reject stale bindings; failures of the stream-only ablation are not attributed to them.
CPU timing reports the median of 12 BatchProgram constructor calls after one warm-up. It includes analysis/lowering, owned weight clones and binding, but excludes original tracing/export, I/O, model execution and GPU copies. It is not GPU deployment latency or developer time.

The first local E3 summarizer compared reader-list enumeration order instead of membership. Its failed attempt and source are preserved under validation/e3_failed_attempt1. The corrected summarizer checks unique reader membership plus exact boundaries and operation counts. No constructor timing or GPU inference was repeated for this correction.

## E4: Cost Attribution Boundaries
The phase table reconstructs all normal timing records from four diagnostic profiling processes. The inclusive cProfile table is separate because nested functions and waits must not be summed. This is isolated child execution, not the complete pipeline. Enrollment was not separately instrumented and is recorded as missing, not free. Diagnostic admission-gap/wall-gap ratios do not identify removable overhead or a safe binding-cache speedup bound. Do not subtract this window from an older performance table.

## E5 and E6
E5 ResNet complete-pipeline delivery was not run: the frozen pipeline factory only supports TransFusion. Accepting a model field in a condition does not make that pipeline implemented. Older isolated ResNet costs and public CPU model-substitution results remain available in prior_v11; they are not ResNet delivery measurements.
E6 is a bounded static survey of 14 predeclared torchvision model tails with weights=None, fixed CPU interface examples and the unchanged operator registry. Dispositions: {"SUPPORTED_STATIC": 9, "UNSUPPORTED_OPERATOR": 5}. SUPPORTED_STATIC means export/analysis/lowering passed, not numerical equivalence, GPU correctness, performance, pretrained accuracy or production support. Export failures remain distinct from unsupported operators.

## Claims These Results Do Not Establish
- A source-hold mean measured on accepted work is not a load-independent service time or precise saturation threshold.
- A rate curve can expose periodic arrival/release phase effects; it does not establish robustness to arrival jitter.
- A late-read boundary removes opportunities for source reuse, but its measured delivery effect also depends on admission and contention. Do not require the difference to equal zero.
- Borrowed-byte occupancy is not freed allocation. Early release must not be described as a measured device-peak reduction without the device-peak data supporting it.
- Explicit admission was helpful in tested overload conditions; an optimal or universally necessary K is not proved.
- A CI including zero does not prove equivalence; a manual baseline by the same authors is not an independent developer study.
- New and old measurement windows must not be pooled post hoc, and unfavorable conditions must not be omitted.

## Formal Data Accounting
```json
{
  "arrivals": 172800,
  "publications": 109592,
  "timely": 109569,
  "correct_late": 23,
  "producer_late": 0,
  "pool_exhausted": 63208,
  "credit_exhausted": 0,
  "queue_loss": 0
}
```
All 144 formal and six smoke runs passed the frozen request/output validator and full remote reconstruction. A separate local implementation also reconstructs receipts, loss accounting, source reuse, sample arrays, raw hashes and paired confidence intervals. Reference .pt containers are hash-checked locally; the remote Torch validators deserialize and verify their tensors. No GPU inference was retried.

## Reproducibility
The separately distributed raw archive preserves absolute original input paths and their hashes. It is an evidence archive, not a standalone image with all external model weights and runtime dependencies. Prior compact evidence and EVIDENCE_NOTES_V11 identify old measurement sources. SHA256SUMS.txt covers every file except itself and the final outer zip. PACKAGE_VALIDATION.json records stage validation hashes.

The raw archive uses a content-addressed manifest plus unique blobs. Every original file was restored and hash-checked locally. raw/ARCHIVE.json identifies both the archive and the restored directory. To restore elsewhere, use source/npc_v12_cpu_tools/archive_cas.py with mode restore, --archive, --output pointing to a new directory, and --sha256 from raw/ARCHIVE.json. The original ordinary archive and intentionally interrupted large transfer remain preserved; neither is used in the delivered analysis. Content-addressed packaging does not deduplicate observations or alter statistical weights.
