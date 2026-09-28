# ISPA 2026 Results

## Jitter, Component Heterogeneity and Checked Manual Boundaries

The September 27 campaign completed 18 smoke and 108 formal runs. Each of 18 condition-method cells has six formal repetitions. All formal runs use 30 source publications/s, one slot, an eight-deep recipient queue, no explicit outstanding-request cap, 10 s warm-up, and a 30 s measurement cohort. Each cohort contains 900 scheduled publications and four intended recipients. The deadline is 100 ms from scheduled arrival.

The primary metric counts a publication as timely only if every intended recipient returns a correct result before the deadline. The denominator includes all scheduled publications, including rejected and partially admitted ones. The homogeneous profile repeats the composition in all four recipients. The heterogeneous profile uses the native engine, head, composition and late-reading composition. Jitter displaces each planned arrival uniformly by up to 0.8 of a source period.

### Complete-Publication Timely Fraction

Means over six runs, in percent:

| Condition | BIM / ReadSeal | Checked Manual | Full retention | Clone-on-accept |
|---|---:|---:|---:|---:|
| Homogeneous, periodic | 65.54 | 65.44 | 50.00 | 63.33 |
| Homogeneous, jitter | 63.54 | 63.50 | 48.02 | 61.65 |
| Heterogeneous, periodic | 50.26 | 50.20 | 50.00 | 82.56 |
| Heterogeneous, jitter | 58.46 | 58.33 | 57.54 | 80.69 |
| All-late homogeneous, periodic | 50.00 | 49.98 | Not planned | Not planned |

[Per-run values](data/jitter-manual-108/per_run.csv), [all metric summaries](data/jitter-manual-108/summary_t95.csv), and [paired contrasts](data/jitter-manual-108/paired_t95.csv) include unrounded values and intervals. The four main conditions account for 96 formal runs; the all-late control accounts for the other 12.

Clone-on-accept minus BIM, in percentage points, with paired pointwise 95% t intervals:

| Condition | Difference | Interval |
|---|---:|---|
| Homogeneous, periodic | -2.20 | [-2.94, -1.47] |
| Homogeneous, jitter | -1.89 | [-2.88, -0.90] |
| Heterogeneous, periodic | +32.30 | [31.81, 32.78] |
| Heterogeneous, jitter | +22.22 | [21.53, 22.91] |

The mixed profile changes more than the late reader: two recipients run only parts of the composition. No heterogeneous control without a late reader was measured, so this comparison does not isolate the effect of a single late reader.

Copying raises the sampled device-memory peak by 256 MiB in matched formal runs. For heterogeneous jitter, its mean per-run complete-publication P99 latency is 78.25 ms versus BIM's 52.91 ms, a paired difference of 25.34 ms [23.55, 27.13]. It also reduces incomplete publications from 373.83 to 173.50 per 900 scheduled publications. These latencies are conditional on complete, correct publications, timely or not; missed publications have no completion latency and are not assigned zero.

### Manual Boundaries and Update Safety

`manual-checked` uses explicit boundaries with the same binding and stage checks as `auto-batched`. Their observed timely fractions differ by at most 0.13 percentage points. This shared-runtime comparison does not establish equivalence or an advantage for an independent manual runtime.

The corrected native gate completed 48 profile/method/source cases, 24 update cases, 6 cancellation cases, 155 rejection witnesses, 600 exact tensor comparisons and 24 distinct-native-handle stream witnesses. Its saved-only audit completed successfully. A stale manual boundary after adding a late read was rejected until updated. The safety contribution of shared binding checks must not be credited solely to automatic boundary discovery. See [gate evidence](provenance/corrected-gate/native_gate_report.json) and [failure/correction history](PROVENANCE.md).

## Separate Clone-on-Accept Rate Sweep

The September 23 campaign completed 8 smoke and 168 formal runs. Its primary throughput metric is timely correct **recipient result bundles/s**, not complete publications/s. Means over six repetitions:

| Source rate / profile | BIM | Manual | Full | Clone-on-accept |
|---|---:|---:|---:|---:|
| 10/s, base | 40.00 | 40.00 | 40.00 | 40.00 |
| 15/s, base | 60.00 | 59.98 | 60.00 | 60.00 |
| 20/s, base | 78.24 | 78.33 | 40.00 | 77.79 |
| 25/s, base | 74.96 | 74.93 | 50.00 | 77.71 |
| 30/s, base | 78.60 | 78.56 | 60.00 | 77.92 |
| 40/s, base | 79.11 | 79.08 | 53.33 | 78.16 |
| 30/s, late | 60.00 | 60.00 | 60.00 | 76.39 |

Copying is better at base 25/s by 2.75 bundles/s [2.47, 3.03] and at late 30/s by 16.39 [16.06, 16.72]. In the late condition, copying has worse P99 latency (101.12 versus 68.66 ms) and mean age (103.89 versus 90.88 ms). At base 30/s, BIM has worse mean age than Full (94.56 versus 91.23 ms). The [full CSVs](data/clone-168) preserve every condition and all reported metrics.

## Interpretation Limits

- Six independent whole runs, not frames, are the statistical units. Intervals are pointwise t95 with df=5, not simultaneous coverage, equivalence tests, or evidence of identical distributions.
- Device peaks are sampled over worker-ready through drain, excluding earlier setup; sampling can miss transients. Per-worker allocator peaks are not simultaneous device totals.
- Component heterogeneity is not four independently trained autonomous-driving models. The BEV front end and a complete ROS 2 driving stack are outside the timed GPU workload.
- No embedded-board, energy, thermal, developer-maintenance-effort, or end-to-end vehicle validation was performed.
- The two new campaigns and all earlier campaigns remain separate; there is no cross-wave pairing.
