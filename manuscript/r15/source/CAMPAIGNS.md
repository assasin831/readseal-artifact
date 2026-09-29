# Campaign and Terminology Guide

## Units and Statistics

A publication is one frame's source tensor and identity written to a slot. A recipient result is the result bundle delivered by one recipient for that publication. Four-recipient studies offer four results per publication.

Rate and slot studies report recipient results/s. The jitter/mixed study reports the fraction of all scheduled publications whose four intended recipients return correct, timely results; partially admitted and rejected publications remain in the denominator. Its latency quantile is among complete, correct publications. This is not a ratio inferred by dividing recipient goodput by four.

Rate and slot studies use six paired whole-run repetitions, 2 s warm-up and 12 s measurement, followed by drain. Their paired bootstrap intervals are pointwise 95% intervals from 20,000 draws. The separate 108-run jitter/manual and 168-run copying campaigns use six paired whole-run repetitions, queues of eight, 10 s warm-up and 30 s measurement, and pointwise 95% t intervals (5 degrees of freedom). No cross-campaign pairing, frame pseudoreplication, equivalence test, or simultaneous coverage is claimed.

## Campaign Inventory

| Evidence | Coverage | In r15 |
|---|---|---|
| Earlier rate sweep E1 | 108 formal runs; 6 rates x 3 policies x 6 repetitions | Fig. 4a-c, V-B |
| Earlier late-read E2 | 36 formal runs; base/late x 3 policies x 6 repetitions | Fig. 4d; together with E1, 144 runs and 109,592 checked results |
| Slot/cap window | 96 runs; 72 for plotted policies, 24 for a separate stage-by-stage automatic variant | Fig. 5; extra variant not plotted and not an equivalence result |
| Separate confirmation | 54 runs retained in core evidence | Not pooled with the plotted slot window |
| Two-slot rate scan | 72 runs in load-sensitivity evidence | V-C uncapped-versus-capped comparison |
| Matched copying rate campaign | 168 formal runs, 8 smoke runs | V-D separate recipient-goodput comparison |
| Jitter/manual campaign | 108 formal runs, 18 smoke runs; 97,200 scheduled publications; 432 recipient-run records | Fig. 6 uses 96 formal runs; 12 all-late controls support the text |
| Corrected native gate | 48 profile/method/source cases; 24 mutations; 6 cancellations; 155 rejection witnesses; 600 exact tensors | Matched checked-manual safety/update evidence, V-E |
| Original snapshot checks | 96 ordered-overwrite cases; 540 tensors; 22 rejected substitutions | Fig. 3, V-E |
| Maintenance replay | 16 transitions: 14 constructed edits, one batch-normalization folding, one public ResNet-18 to ResNet-50 substitution; 13 boundary changes | V-E |
| Isolated runtime cost | 8 process repetitions of 50 randomized invocations per method; three inputs; two models, base/late variants | V-F |
| Static coverage | 14 torchvision tails with untrained weights; 9 accepted, 5 unsupported | Static coverage only, not performance data |

The additional stage-by-stage variant records a finer-grained automatic execution variant in the archived slot experiment. It is not Manual-checked, not a new r15 experiment, and not used to inflate the plotted sample size.

## Names

| Saved identifier | Paper label | Role |
|---|---|---|
| auto-batched | BIM + ReadSeal | Automatically derive boundaries and check execution bindings |
| manual-early | Manual | Earlier separately maintained hand-placed implementation |
| manual-checked | Manual-checked | Hand-placed boundary with the same binding/stage checks as BIM |
| manual-full | Full / Full retention | Retain source until outputs complete |
| copy-in | Clone-on-accept | Copy into recipient-owned storage at acceptance |

A recipient is a consuming process. A reader is a component inside that process that may read the source. A view can alias the source; a private intermediate does not. The read boundary is the final source-reading operation, beta in the analysis. Reuse waits until every recipient's borrow has ended.

K counts outstanding recipient requests across the pipeline. K=8 accommodates two full groups of four requests. "No pipeline-wide cap" leaves per-recipient queue limits in force.

Held source storage is time-averaged unavailable source storage, not allocated GPU memory. Device peaks are sampled and may miss transients; for the 108-run campaign they cover worker-ready-to-drain and exclude earlier setup. Per-worker allocator peaks must not be summed into a simultaneous device total.

## Evidence Access

Use the [r15 data guide](https://github.com/assasin831/readseal-artifact/blob/ispa2026-r15/DATA_GUIDE.md) and unchanged archives. Saved member names and CSV comments can contain historical version identifiers. These are provenance, not new venue labels; changing them would break byte-level verification.
