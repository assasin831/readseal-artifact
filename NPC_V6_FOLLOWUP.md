# NPC V6 follow-up evidence

Core GPU experiments/runtime remain unchanged at `npc-evidence-v3` in
https://github.com/assasin831/readseal-artifact . This follow-up adds two evidence
items, neither of which is a new GPU performance trial.

## Reconstruct without a GPU

Requires Python and NumPy only. Run from the unpacked directory:

```sh
python code/reproduce_followup.py --bundle . --output validation-new.json
```

The output must be a fresh path. This validates inventory and 192 raw request
files, reconstructs all 96 runs and 20,000-replicate paired-repeat intervals, and
checks all twelve saved CPU model outputs against functional/eager references.
It does not execute the models or independently prove their CUDA semantics.

## Grouped-specific queue diagnosis

`grouped_requests.zip` contains the original report/sink JSON for all 96 primary
runs, selected byte-for-byte from the preserved V11 archive. The per-file hashes
are bound to `grouped_primary.json`. The reanalysis is `grouped_trace.json`.
96,764 includes warmup/drain; cohort populations are recorded separately.

All means/intervals use six complete paired repetition blocks, not request-level
bootstrap. Request phases are host observations. Queue entry was not directly
timestamped: commit-end/producer-done only bracket it. Per-recipient source-return
completion is not the final global pool-bit clear. The code preserves all negative
results, including the Grouped two-slot uncapped reversal.

## Public architecture substitution, CPU only

`public_model_outputs.zip` holds the report, independent validation, explicit
manual review rules, functional graph code, and twelve output-array triples.
Public implementation: torchvision 0.16.2 ResNet-18 and ResNet-50:

https://raw.githubusercontent.com/pytorch/vision/v0.16.2/torchvision/models/resnet.py

Official V1 pretrained checkpoints:

- https://download.pytorch.org/models/resnet18-f37072fd.pth
- https://download.pytorch.org/models/resnet50-0676ba61.pth

The full checkpoint/source hashes are recorded. The second checkpoint is
`0676ba61b6795bbe1773cffd859882e5e297624d384b6993f7c9e683e722fb8a`.
The manually reviewed semantic boundary changes from a residual add retaining an
identity alias to a projection convolution producing a private identity. Automatic
analysis agrees. These new exports have 8/85 and 12/224 prefix/total calls; they
are not the prior Table 2 exports. Twelve synchronous CPU tests overwrite the
source between generated/manual prefix and suffix, matching full functional
references exactly and eager references at rtol=1e-5, atol=1e-6.

This is a reproducible public-architecture substitution selected for the study,
not a real production migration or developer experiment. Three saved ResNet-18
stem activations are reused at the common interface; no ResNet-50 accuracy claim.
The compact public bundle omits checkpoints and source activations, preserving
their hashes. Full model execution needs those inputs and the pinned runtime;
the included remote runner records the original environment paths and is not a
turnkey installer. CPU output replay requires neither the runtime nor PyTorch.

## Failures, pending work, limits

- CPU attempt 1 timed out on official source download before model execution.
  A fresh locally staged attempt completed twelve tests, without inference retry.
- Validator attempt 1 had a 65-character hash transcription error and failed
  before array validation. Corrected fix1 rechecks all 141 conditions against
  the unchanged result; no inference rerun. Both validator sources are retained.
- The load/cap scan is preparation only, not frozen or run. Queue observations
  narrow per-recipient API spans; they are not transport linearization timestamps.
  Spawn tests pass, but CUDA smoke and instrumentation perturbation remain gates.
- No credible field-imposed one-slot budget has been demonstrated. Do not infer
  one from MIG, fill memory to manufacture it, claim reduced total device memory,
  or turn operation counts into saved human hours.

All core V3 evidence and failed/successful attempts remain unchanged.
