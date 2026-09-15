# V7 Evidence Guide

Repository: https://github.com/assasin831/readseal-artifact

## Frozen Layers

1. `npc-evidence-v3`: original runtime, 96-run primary and 54-run independent
   windows, binding tests, maintenance/folding/cost evidence and CPU validators.
2. `npc-followup-v6`: original 192 report/sink files and saved public-model CPU
   outputs. Reconstruction checks 96,764 request records, twelve saved model
   outputs and paired statistics without inference.
3. V7 sensitivity evidence: new 72-run load-scan aggregates, campaign/preflight
   lineage, separate diagnostic record, and new fixed-trace deadline analysis.
   None replaces or pools the older windows.

## V7 Scope and Results

The GPU window comprises Grouped/Full, rates 20/30/40 publications/s, R=2,
caps unlimited/8, and six randomized paired repetitions. Each publication offers
four bundles. All 72 runs complete; 103,680 cohort arrivals comprise 68,304 receipts,
17,672 pool refusals and 17,704 credit refusals. There are 55,735 timely and 12,569
correct-late receipts; no producer-late arrivals, queue losses, wrong outputs or
unknown sources. The final remote audit inventories 1,944 raw files. This compact
bundle carries that inventory and per-run aggregates, not those raw files.
The local checker reconstructs load statistics and frozen lineage, not the full
load-window raw execution. The pre-existing remote audit performed raw checks.

| Publications/s | Cap | Grouped timely/s | Full timely/s | Paired G-F 95% CI |
| --- | --- | --- | --- | --- |
| 20 | unlimited | 39.78 | 72.38 | [-37.22, -27.60] |
| 30 | unlimited | 28.81 | 71.22 | [-47.39, -37.47] |
| 40 | unlimited | 20.36 | 72.31 | [-57.92, -45.99] |
| 20 | 8 | 78.26 | 78.35 | [-0.32, 0.21] |
| 30 | 8 | 78.31 | 78.22 | [-0.14, 0.32] |
| 40 | 8 | 78.03 | 78.08 | [-0.42, 0.19] |

Intervals use 20,000 paired complete-repeat samples (seed 260914062), not
equivalence tests. Protected storage falls by 35--37 MiB under cap 8, but sampled
device peaks remain 5,142 MiB for both methods.

Separate instrumentation diagnostics preserve 23 successes and one foreign-job
interruption. Only complete within-window pairs enter descriptive comparisons;
incomplete repetition 1 is excluded from pairs. No failed inference was retried;
no diagnostic run enters the formal estimates.

Deadline analysis verifies hashes for all 192 original report/sink files, request
identity, references, timestamps and the original deadline classification. It
reconstructs all arrival-cohort receipts from 96 primary runs at 80, 90, 100, 110,
120, 130, 150 and 200 ms. Drops remain zero-goodput at every cutoff. Requests and
execution schedules are unchanged. The new bootstrap seed is 260915071 (20,000
paired complete-repeat samples; pointwise intervals). Monte Carlo differences
from the original 100 ms CI do not revise its frozen original interval.

At R=2 uncapped, Grouped/Full are 45.14/78.82 at 110 ms and 62.76/79.03 at 120 ms:
the reversal does not disappear at 110 ms. At 150 ms they nearly converge in
magnitude (79.00/79.15), not an equivalence finding. Fig. 3 shows 80--150 ms;
200 ms and R=2, K=4 remain in the JSON. This is post-hoc fixed-trace sensitivity,
not deadline-aware rescheduling, jitter robustness, or application validation.

## Entry Points

- `evidence/loadscan_v7.json`: frozen formal aggregate and raw inventory.
- `evidence/npc_loadscan_v7_formal_*_final1.json`: campaign and preparation.
- `evidence/loadscan_diagnostic_v7.json`: separate incomplete diagnostic history.
- `evidence/loadscan_controller_v7.json`: completed supervisor lineage.
- `evidence/deadlines_v7.json`: latencies, cutoff counts and CIs.
- `tools/analyze_deadlines_v7.py`: full reconstruction from the V6 raw archive.
- `tools/validate_submission_v7.py`: local reconstruction and manuscript checks.
- `tools/build_sensitivity_v7.py`: Fig. 3 from measurements only.
- `tools/build_assets_v3.py`: Fig. 2, separate 96/54-run windows.

Follow README commands. These CPU commands do not execute models, unpickle,
access the network, or use a GPU. Deployment paths in frozen reports are
provenance, not executable installation instructions.

## Unmeasured Questions

No externally imposed one-slot deployment budget has been demonstrated.
N*S <= B < 2*N*S is source-capacity arithmetic only. The public substitution is
a study-selected CPU case, not an observed upgrade or developer-hours experiment.
Arrival jitter, bursts, additional GPU architectures, full dynamic heads, and a
native C++ cost floor remain unmeasured. No wording should imply otherwise.
