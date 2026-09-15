# ReadSeal NPC review artifact: claim-to-evidence map

Public entry: https://github.com/assasin831/readseal-artifact

Current manuscript map: **NPC V10, 15 September 2026**, frozen at
`npc-submission-v10`. [NPC_V10_GUIDE.md](./NPC_V10_GUIDE.md) links the unchanged
experiment archives, V9's graph-count audit, and the current vector figures.
Older archives retain their historical numbers; this page maps V10. Related Work
is now Section 2, design Section 3, safety Section 4 and evaluation Section 5.
The former trust table is prose in Section 3.3; the remaining tables are 1-3.

This is a project-produced review artifact, not an independently authored
replication or proof of arbitrary CUDA operators. Download the versioned reviewer
archive from the repository. No credentials, pretrained checkpoints, source
camera inputs, training datasets, or third-party SDK packages are included.

## Start here (no GPU)

Python 3.10+ with NumPy, Matplotlib and pypdf is sufficient for the compact-data
checks. Run from the extracted reviewer archive:

```sh
python tools/verify_archive.py
python tools/validate_revision.py
python tools/validate_confirmatory.py
python tools/validate_profile.py
python tools/build_assets_v3.py
python transition_test/prototype/npc_followup_v2/audit_transitions.py
```

The first command independently reconstructs both windows' matched differences
and 20,000-resample percentile intervals. The drawing command regenerates Fig. 2
from the frozen aggregates, not synthetic data. The host transition test uses
test-double completions, not GPU inference, and refuses to overwrite its result.
Successful host checks do not certify device event semantics.

Optional, with PyTorch installed: `python tools/verify_binding_offline.py`
compares the 22 saved output tensors with the included frozen unsplit oracles
using CPU only. The original deployment validator was executed successfully;
this portable path is supplied for rerunning those comparisons without the
original absolute paths. It does not regenerate the GPU observations.

## Protocol and binding evidence

| Paper claim | Source and test | Evidence and scope |
| --- | --- | --- |
| Sect. 3.3: trust boundary | `evidence/operator_contract.json`, actual runtime sources and Sect. 4 premises | Separates derived and checked facts from operator, topology and deployment assumptions; not a proof of arbitrary kernels |
| Table 1: enrollment and submit | `runtime/` contains unchanged `core.py`, `prepared_lease.py`, `batch_lease.py`; host test enumerates its checks | `evidence/transition_validation.json`, 15 named checks; all future readers begin pending, duplicate/unknown starts reject |
| Table 1: return, abort, publish | Same test and actual lease methods | Pending readers prevent reuse; abort cancels only pending nodes; unknown started completion retains ownership; publication preserves identity |
| Sect. 5.2 Binding: direct executable binding | `tools/check_binding_cuda.py` invokes the unchanged Grouped `BatchProgram` | `evidence/binding.json`: 26 cases across two models, 4 accepts and 22 rejections, not the manual constructor's 14 old hash rejections |
| Direct output and rejection validation | `tools/audit_binding_result_fix1.py`, GPU-free validator | `evidence/binding_validation.json`: 164 checks, 22 saved tensors also match frozen unsplit references; `binding_raw/` has all four positive outputs |
| Table 2: graph maintenance | `evidence/maintenance_validation.json`; `runtime/` contains `variants.py`, `evolved_manual.py` | 96 ordered-overwrite cases, 540 tensors; 14 unique graphs. Original manual hash rejections remain explicitly labeled manual |
| Sect. 5.2 public convolution/normalization folding | `evidence/folding_validation.json`, `runtime/public_deployment_transform.py` | All 240 tensors from 48 protected cases exactly match their respective unsplit references. Folded versus original references use rtol=1e-3, atol=1e-4, integer exactness |
| Sect. 5.2 architecture substitution | V6 `public_model_outputs.zip` and `code/reproduce_followup.py` | Twelve saved CPU cases, ResNet-18/50 prefixes 8/85 and 12/224; see V9 graph-count audit for Table 2's 12/123 |

The direct CUDA check uses the real Grouped guard at admission and both stage
entries. Inputs with wrong shape/stride or odd generation reject at admission;
foreign certificate/grouping plans also reject there. Changed function code is
tested separately at admission, prefix entry and suffix entry. Changed globals
and owned state versions reject at admission; replacing the admitted program
rejects at prefix entry. Every rejected operation records zero child-function
calls and zero new events. A suffix-entry rejection may have **one already
completed prefix event**; zero new submissions is not zero prior work.

Before an invocation exists, the external recipient hold still belongs to the
caller. The test does not fake a producer-pool return. After admission it invokes
the actual lease's abort and drain path, verifies source releasability and forbids
output publication. Faults are injected between completed operations, never by
concurrently writing device state. The checks are not a Python sandbox test.

All runtime/input hashes are preserved in the reports. An early CPU validator
mistakenly equated runtime-group length (which includes lifted model-state
placeholders) with call-function operation count. That validator remains in
`tools/audit_binding_result.py`. `audit_binding_result_fix1.py` filters the
recorded graph by `call_function`, retains all other assertions, and additionally
checks the already frozen unsplit numerical references. No GPU inference was
retried. The raw report's `prefix_operations` and `total_operations` fields are
historical group-entry counts; use its `artifact.graph` and `artifact.groups` to
recover the operation counts printed in Table 2.

## What changes when the graph changes?

For the late-clone case, the caller changes the exported child graph. The shared
input schema, A/B/C topology and native-A completion contract remain unchanged.
The checked constructor regenerates read obligations, the last-source-reading
prefix, private live values, captured functions, and their binding. The complete
manual path additionally updates `review['boundary']` and
`review['graph_sha256']`, consumed by `EvolvedManual`. Both paths remain correct
when maintained. The evidence demonstrates automatic boundary derivation and
guarded recomposition, not a user study, programming-hour saving, or discovery of
undeclared native readers. The same field-level mapping applies to the tested
folding transformation. Unsupported operators still require a manual audit.

## Fig. 2: two separate resampling populations

| Window | Complete runs | Matched methods per repeat block | Input |
| --- | --- | --- | --- |
| (a) Primary | 96 = 4 conditions x 4 methods x 6 repeats | Original, Grouped, Manual early, Full retention | `evidence/grouped.json` |
| (b) Independent | 54 = 3 conditions x 3 methods x 6 repeats | Grouped, Manual early, Full retention | `evidence/confirmatory.json` and frozen prepared/campaign records |

Within each window, one seeded 20,000 x 6 index matrix resamples whole repetitions
with replacement, preserving method pairing. Each plotted contrast is computed
within matched repeats. Neither individual requests nor the two host windows are
pooled. The intervals are pointwise, with no multiplicity correction. Full
reconstruction is in `tools/validate_revision.py`; the original aggregate source
is included in `runtime/aggregate_grouped_formal.py`.

The top bars contain timely sink receipts, correct late receipts, and requests
never enqueued (pool/credit exhaustion or queue rejection). In these successful
runs all enqueued cohort requests reach the sink; wrong/source-unknown counts
and omitted producer-late counts are zero. Enqueue, recipient admission,
publication handoff and actual sink receipt are distinct protocol events.

At R=2 without a cap, Grouped-minus-Full goodput is exactly decomposed as
`(5688-5700)/72 - (3893-495)/72 = -47.3611...` recipient bundles/s. This is -0.17 from fewer
receipts and -47.19 from additional late receipts, not a causal experiment that
holds admission timestamps or queue ages fixed. The repeated 60.00 one-slot
Full-retention result is specific to the periodic 30-Hz offered trajectory.
Arrival jitter was not measured. A second source slot is feasible (63.3 MiB);
these data do not demonstrate a field-imposed pool bound or memory exhaustion.

## Table 3 versus profiling

`evidence/executor_cost.json`: 19,200 invocations; process/block bootstrap;
presynchronized end-to-end executor scope excludes construction and output IPC.
The table spans three inputs' mean block medians, not confidence intervals.

`evidence/profile.json`: a separate 2,560-call profiled/unprofiled diagnostic.
Both Grouped and Manual early call their own binding guard once at admission,
once at prefix entry and once at suffix entry. Each scan visits 97 head or 116
ResNet state tensors: 291 or 348 `state_token` calls **per invocation**. The old
profiler's `guard_calls` field selected the owned-backend function by file path;
its zero for Manual early does **not** mean that the manual implementation skips
its own guard. See unchanged `runtime/manual_static.py`. Grouped additionally
checks grouping/plan identity. Inclusive profiler times overlap, and profiling
adds 7-34% wall time; do not sum them to infer causal overhead components.

`evidence/trace.json` is an unpooled 108-run supporting intervention. At R=2 with
no cap, Original/Full retention take 50.16/28.21 ms before admission and
48.77/48.87 ms from admission to output. These are receipt-conditioned values,
not statements about the scheduling cause or unreceived requests. The archive
retains its distributions and loss accounting without substituting it for either
Fig. 2 window.

## Scope and reproduction boundaries

For Fig. 3, use the V7 sensitivity archive for the 72-run load comparison and all
eight fixed-trace cutoffs, with V6's original request files for full cutoff replay.
Panel (b) plots the complete 80--200 ms range. The V10 rendering scripts read
frozen aggregates only; they do not rerun inference or revise estimates.
See [NPC_V10_GUIDE.md](./NPC_V10_GUIDE.md) for exact inputs, commands and scope.

`runtime/` is a byte-identical selection of the experimental project sources,
with SHA-256 hashes and original directory mapping. Paths in deployment scripts
are frozen provenance. They must be adapted to a new isolated deployment before
GPU reproduction; importing them is not a promise of a one-command setup. The
public archive supports code inspection, CPU numerical reconstruction and host
transition tests. It is not the entire original GPU environment or pretrained
dataset bundle. No broad open-source license is newly granted on the authors'
behalf; existing third-party notices retain their original terms.
