# Evidence Provenance

## Preservation

This release changes the public organization and submission-facing names, not the experiments. Six archives are copied byte-for-byte and given ISPA-facing download names. The [evidence index](evidence-index.json) records their lengths and SHA-256 digests. Original internal filenames, remote paths, source labels and manifests remain unchanged. Historical Git commits and tags have not been rewritten.

The September 23 clone-on-accept archive is `9f07b1c1cb85ca2b003387eb9e469225e7805ff6fa730ce27d60d2edc45cf9d1`. The September 27 jitter/manual archive is `dbd10557648361efd53b1616765c6c179f8787523a5fcffd823a800ced6a6ad8`. These are the original archived bytes, not new experimental packages.

## Initial Gate Failure

The first September 27 native gate failed at 13:52:59 UTC with:

```text
AssertionError: Invalid action accepted: private_probe-manual-checked-s2-stream-substitution
```

It recorded 48 completed profile cases, 17 completed update cases, failure during the 18th update case, six unstarted update cases and six unstarted cancellation cases. It recorded 107 successful rejection witnesses of 155 planned. It did not pass the independent gate audit and did not start a performance campaign. Its [report](provenance/initial-gate/native-gate/report.json), [controller status](provenance/initial-gate/gate-controller/status.json), exit code and failure log remain public. Partial results from that gate are not counted as successful validation.

The old stream-substitution witness assumed that constructing a different Python stream object guaranteed a different native CUDA stream handle. PyTorch 2.1.2 uses a stream pool, so that assumption was not valid. The failed attempt did not record both native handles; the evidence therefore supports a defective witness assumption, not a retrospective proof of a particular handle collision.

## Corrected Gate and Completed Performance Campaign

A separate attempt changed the witness to use the same-device default stream, explicitly assert distinct native handles, require the exact rejection reason and verify unchanged execution state. Runtime guards, performance code, condition matrix and statistical rules were unchanged. The original failed output was not overwritten.

The corrected gate completed at 15:17:24.925638 UTC with exit code 0. Its saved-only audit verified 48 cases, 24 updates, 6 cancellations, 155 rejections, 600 exact output tensors and 24 distinct-handle stream witnesses:

- [Gate report](provenance/corrected-gate/native_gate_report.json), SHA-256 `227e87b160668f808dd2fbfa5354ef3a3c64fd2f1be5e1a14cf0ec20d0e49ea2`.
- [Gate audit](provenance/corrected-gate/native_gate_audit.json), SHA-256 `bbd9ecf746ff544562b3d62076656e7348c7fb64fde95bf7af7135a3fb020143`.
- [Prepared record](data/jitter-manual-108/prepared.json), SHA-256 `150aefb6d42834e434d7935c8c2c2aa8bf3d15fa189ffb366260da2915574ab9`, binding 172 inputs, sources and proofs.

The subsequent performance campaign completed all 126 scheduled runs, 18 smoke and 108 formal, with their audits, at 17:02:35.676993 UTC. No failed or unstarted performance runs were excluded to obtain the published table. The new campaign's exporter read saved records only.

The CPU witness, controller, construction and exporter tests are software tests, not additional measured performance observations. Compact public records include hashes for some large artifacts not distributed here; see [reproduction scope](ARTIFACT.md).
