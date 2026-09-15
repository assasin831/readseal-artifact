# NPC V9 submission evidence guide

This guide accompanies the 12-page NPC manuscript at tag `npc-submission-v9`.
It is project-produced evidence, not independent-team replication. V9 adds no
model execution. Older measurements, negative results, archives and tags remain
unchanged. Paths below are relative to the corresponding extracted archive.

## Find a paper result

| V9 location | Archive or directory | Input, check and expected output |
| --- | --- | --- |
| Fig. 1; Tables 1-2 | Core V3 archive | `runtime/`, `evidence/operator_contract.json`, `evidence/transition_validation.json`; `transition_test/prototype/npc_followup_v2/audit_transitions.py`: 15 host contract checks, not a CUDA proof |
| Table 3; Sect. 4.2 edits/folding | Core V3 archive | `evidence/maintenance_validation.json`, `evidence/folding_validation.json`: 96/540 and 48/240 cases/tensors, respectively |
| Sect. 4.2 binding | Core V3 archive | `evidence/binding.json`, `tools/verify_binding_offline.py`: 26 cases, four accepts/22 rejections, 22 saved positive tensors; affected-stage rejection, possibly after completed prefix |
| Sect. 4.2 architecture substitution | V6 follow-up archive | `public_model_outputs.zip`, `code/reproduce_followup.py`: twelve saved CPU cases, functional equality and eager rtol=1e-5/atol=1e-6 |
| ResNet 8/85 versus 12/123 | `submission-v9/evidence/export_audit/` | `submission-v9/tools/validate_export_counts.py`: matching original graph text and export identity, 38 unused tuple-index nodes, same residual-add boundary |
| Fig. 2(a) and (b) | Core V3 archive | `evidence/grouped.json`, `evidence/confirmatory.json`; `tools/verify_archive.py`, `tools/validate_revision.py`, `tools/validate_confirmatory.py`: independent reconstruction of separate 96/54-run windows |
| Sect. 4.4 request clocks | V6 follow-up archive | `grouped_requests.zip`, `grouped_trace.json`, `code/reproduce_followup.py`: hashes for 192 original files, 96,764 records including warmup/drain |
| Fig. 3(a) | V7 sensitivity archive | `evidence/loadscan_v7.json`, `tools/validate_submission_v7.py`: 72 complete runs, six paired repeats, 103,680 recipient offers; local checker reconstructs aggregates, not absent raw load-window files |
| Fig. 3(b) | V7 sensitivity + V6 raw requests | `evidence/deadlines_v7.json`, `tools/analyze_deadlines_v7.py`: eight cutoffs 80/90/100/110/120/130/150/200 ms, 20,000 paired-repeat resamples |
| Table 4; Sect. 4.5 profile | Core V3 archive | `evidence/executor_cost.json`, `evidence/profile.json`, `tools/validate_profile.py`: 19,200 timed invocations; separate 2,560-call diagnostic |

Archives in this repository:

- [Core V3](./readseal_npc_2026_reviewer_artifact_v3.zip), tag `npc-evidence-v3`.
  SHA-256 `6deb8c63f74563b9a42280695cc8f5dbc88070e9b2be0bdc1eb36014ea2ceeb0`.
- [V6 follow-up](./readseal_npc_followup_v6_evidence.zip), tag `npc-followup-v6`.
  SHA-256 `f29ab536298b1ea9a980582964e59bc2180a933163a17c0b2540985a915a4835`.
- [V7 sensitivity](./readseal_npc_v7_sensitivity_evidence.zip), tag `npc-sensitivity-v7`.
  SHA-256 `931f3fd8958ef68d606ee68d5ab826ae9eba3042bc02083ca00f928622fb3e0d`.

The V7 archive's `README.md` gives its reconstruction commands, including the V6
raw-file input. Prior reconstruction results are linked from the repository
README. These checks do not certify arbitrary GPU operators or re-create the
full original deployment environment.

## V9 graph audit and figure rebuilding

Run from this repository root using Python 3.10+:

```sh
python submission-v9/tools/validate_export_counts.py --output export-validation-new.json
```

No third-party module is needed for that check. The output path must be new.
It parses saved graph text with Python's AST and structured JSON, without imports
of the recorded graph, model unpickling or inference. Original and substitution
in-memory graph text are byte-identical. The original report's serialized-export
hash matches the reviewed reloaded artifact. That artifact contains two unused
tuple outputs at each of 19 BatchNorm sites. Removing only those 38 unused index
nodes recovers the same 85-target operator order and the eighth-operation add;
the recorded reloaded prefix instead has 12 operations out of 123. This is a
structural explanation, not a new numerical equivalence experiment.

With NumPy, Matplotlib and ReportLab installed:

```sh
python submission-v9/tools/build_architecture_v3.py
python submission-v9/tools/build_sensitivity_v7.py
python submission-v9/tools/build_assets_v3.py
```

These regenerate the current three vector figures and the editable draw.io
diagram from frozen records. Figure 2 uses recipient bundles/s throughout;
Figure 3(b) plots all eight cutoffs. Scripts overwrite only derived figure files,
never raw measurements. Windows uses Arial for the diagram; elsewhere the script
falls back to DejaVu Sans, so glyph positions can differ while geometry remains
the same. Submitted figure hashes are in `submission-v9/manifest.json`.

## Timing semantics

The primary runtime records producer reservation/commit, recipient admission just
before lease start, output-event completion, and sink receipt after transfer.
Exact enqueue instants are not recorded: commit-end and producer-done bracket
queue insertion. Source return enables reservation; it does not imply earlier
recipient admission. Similar *mean* admission-to-output latencies do not establish
identical downstream service distributions or causal isolation of the executor.

Goodput counts offered recipient requests, one verified A/C bundle per recipient.
There are four recipient offers per source publication. The 12-second arrival
cohort is tracked through drain. Sink receipt returns credits even when late;
late results contribute zero goodput. Worker errors invalidate a run. The final
primary and load analyses retain all these accounting categories.

## Environment provenance and remaining gap

Frozen sources/reports identify PyTorch 2.1.2+cu121, torchvision 0.16.2+cu121,
CUDA 12.1, TensorRT 10.3, and a full 40 GiB NVIDIA A100. The recorded launch source
sets `OMP_NUM_THREADS=1` and `MKL_NUM_THREADS=1`; `study_common.configure()` sets
PyTorch intra-op threads to one, disables TF32 for matmul/cuDNN and disables
cuDNN benchmarking. Runs are serial with sampled whole-host idle guards.

The available archived records do **not** reliably establish the CPU model,
exact Python patch version, OS release or NVIDIA driver version of every timed
window. These remain missing provenance, not values inferred from the current
editing machine or a newly queried server. Host-checking costs are sensitive to
this gap. A fully portable GPU reproduction needs the original dependencies,
inputs and isolated deployment; this public package primarily supports source
inspection and CPU reconstruction of saved evidence.

No credentials, pretrained weights, source camera inputs, new experiment claims,
new broad license, or independent replication claims are introduced by V9.
