# ReadSeal: Checked Borrowing Plans for Asynchronous Shared-Tensor Pipelines

Review artifact accompanying the NPC manuscript. This repository contains
project-produced evidence and runtime sources, not an independent-team replication.

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
