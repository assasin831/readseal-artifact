# ReadSeal: Checked Borrowing Plans for Asynchronous Shared-Tensor Pipelines

Review artifact accompanying the NPC manuscript. This repository contains
project-produced evidence and runtime sources, not an independent-team replication.

## Frozen evidence and manuscript versions

NPC V7 adds the [sensitivity evidence package](./readseal_npc_v7_sensitivity_evidence.zip)
and [guide](./NPC_V7_SENSITIVITY.md), frozen at `npc-sensitivity-v7`.
It keeps the completed 72-run GPU load scan separate from earlier windows and
adds CPU-only eight-cutoff sensitivity on all 96 original runs. A clean-extraction
reconstruction passed 2,230 checks, including all 192 original report/sink files
obtained from V6; [the result](./NPC_V7_REPRODUCTION.json) records the scope.
The compact load package contains frozen per-run aggregates and the raw inventory,
not all remote load-window raw records. No jitter, deployment-budget constraint,
or native C++ speedup is claimed.

V7 ZIP SHA-256: `931f3fd8958ef68d606ee68d5ab826ae9eba3042bc02083ca00f928622fb3e0d`.
Prior archives and tags remain unchanged.

NPC V6 adds a [follow-up evidence package](./readseal_npc_followup_v6_evidence.zip)
and [reproduction guide](./NPC_V6_FOLLOWUP.md), frozen at `npc-followup-v6`.
It re-audits Grouped's own 96-run request traces and adds twelve **CPU-only**
public ResNet-18/ResNet-50 substitution tests. No new GPU performance result or
memory-budget deployment claim is made. A NumPy-only reconstruction passes
279 checks; [the result](./NPC_V6_REPRODUCTION.json) records its exact scope.

Follow-up ZIP SHA-256:
`f29ab536298b1ea9a980582964e59bc2180a933163a17c0b2540985a915a4835`

NPC manuscript V4 uses the same experiments as V3. Both resolve to
[`npc-evidence-v3`](https://github.com/assasin831/readseal-artifact/tree/npc-evidence-v3),
commit `ddbb51613909857a3a6442f2202033ba5109de30`. The V3 archive below is unchanged.
V4 clarifies the case/tensor counts, repairs Fig. 1's publication-arrow target,
and updates scholarly references and presentation; it adds no new GPU experiment.
See [MANUSCRIPT_VERSIONS.md](./MANUSCRIPT_VERSIONS.md) for exact delivery hashes.

## Download NPC V3

- [Reviewer artifact ZIP](./readseal_npc_2026_reviewer_artifact_v3.zip) (10.7 MB).
  Open the file and choose **Download raw file**.
- [Claim-to-source/test map and reproduction guide](./ARTIFACT.md).

Archive SHA-256:
`6deb8c63f74563b9a42280695cc8f5dbc88070e9b2be0bdc1eb36014ea2ceeb0`

The archive includes 143 hash-inventoried files: frozen real aggregates and
per-run records, inspected runtime sources, validators, editable/vector figures,
26 direct executable-binding cases, four saved positive outputs and their frozen
unsplit reference outputs. Runtime provenance maps original source paths to the
included byte-identical files.

## CPU checks

After extraction, Python 3.10+ with NumPy, Matplotlib and pypdf:

```sh
python tools/verify_archive.py
python tools/validate_revision.py
python tools/validate_confirmatory.py
python tools/validate_profile.py
python tools/build_assets_v3.py
python transition_test/prototype/npc_followup_v2/audit_transitions.py
```

These commands were tested on a clean extraction. The archive contains no model
checkpoint, source camera input, training dataset, credentials or third-party SDK.
GPU scripts preserve deployment paths for provenance and require adaptation; this
is not a turnkey GPU environment. Optional `verify_binding_offline.py` uses
PyTorch on CPU to compare saved tensors; no inference is launched.

## Interpretation

The two performance windows (96 and 54 runs) are analyzed separately. Bootstrap
resampling preserves whole matched repeats, not individual requests. The direct
binding check is functional, not a timing experiment. Periodic offered arrivals
do not establish arrival-jitter robustness. Fixed pool size is an experimental
constraint, not a demonstrated field memory limit. Manual early release remains
faster in isolated execution, and a feasible extra slot can make full retention
competitive. See ARTIFACT.md for the complete limitations and evidence map.

Existing notices retain their terms. No new broad license or rights over
third-party dependencies are asserted by this packaging step.
