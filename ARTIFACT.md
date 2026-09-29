# Verification and Reproduction

## Verify the Saved Evidence

Download this repository at tag `ispa2026-r16`, or clone it:

```sh
git clone --branch ispa2026-r16 https://github.com/assasin831/readseal-artifact.git
cd readseal-artifact
python tools/verify_results.py
python tools/verify_manuscript.py
python -m unittest discover -s tools -p "test_*.py"
```

Python 3.10 or later is sufficient; the verifier uses only the standard library. It is read-only, does not import the execution code, and starts no GPU jobs. It verifies archive and copied-file hashes, embedded manifests where supplied, both formal CSV row counts, the new campaign's publication denominator and recipient coverage, and all 403 summary/paired intervals in that campaign. It prints a JSON result and returns a nonzero exit code on failure.

The separate manuscript verifier checks the r16 PDF and ZIP hashes, ZIP CRCs, and every source-manifest entry against both the browsable source tree and the ZIP. Use --revision r15 to verify the preserved preceding package. It checks packaging integrity, not experimental validity or visual quality.

`evidence-index.json` records the SHA-256 and length of each byte-preserved evidence file. It covers data and execution-source snapshots, not newly written explanatory Markdown or the portable verifier itself. The Git tag fixes the whole repository tree.

## Recompute Paper Tables

The [r16 source](manuscript/r16/source/README.md) includes exact CSV inputs, native PowerPoint generators, vector figures, build scripts, and reconstruction checks. [release.json](manuscript/r16/release.json) records paper and ZIP hashes; the source package's MANIFEST.json covers every included file.

The manuscript source package includes `scripts/extract_artifact.py` and `scripts/extract_followup.py`. The former reads `archives/ispa2026-rate-slots-evidence.zip`; the latter reads the 108-run and 168-run archives. These scripts derive plotting tables from saved records. They do not rerun inference.

The new campaign's [original saved-only exporter](code/analysis/export_results.py) and its [CPU tests](code/analysis/test_export.py) are included byte-for-byte. Its original SHA-256 is `1af35d3f4f7ec154ca3ac62d34e333c0a02cc1cbe582ce2cc71aa8c6ffd4a9e8`. It expects the original campaign directory, including per-run records not all present in the compact archive. Use the portable verifier above to check the public compact export.

## Execution Sources and Coverage

[code/executor](code/executor) contains the frozen source for the corrected native gate and the 108-run campaign. The snapshot retains its original file hashes, relative dependencies, and execution paths. It is supplied for inspection, not as a portable one-command inference benchmark. Older runtime dependencies and scripts are also present in the earlier evidence archives. Saved records bind model, engine, input and output files by hash; some large weights, native engines, tensor dumps, and worker traces are not included in this compact release. Hash records are not substitutes for those unavailable bytes.

The [prepared record](data/jitter-manual-108/prepared.json) binds 172 source, input and proof files. The [input evidence](data/jitter-manual-108/input_evidence.json), [export validation](data/jitter-manual-108/validation.json), [controller steps](provenance/corrected-gate/execution_steps.json), and [completed audit binding check](provenance/corrected-gate/completed_audit_binding_check.json) describe the saved execution. A third party can check the exported measurements and public source hashes without the GPU. Re-executing every native tensor comparison requires the separately recorded original inputs and environment.

Both new campaigns use six whole-run repetitions and pointwise Student-t 95% intervals with five degrees of freedom. Earlier campaigns use their own recorded analysis protocols. Do not replace run-level replication with frame counts or combine campaigns.

## Archive Integrity

The new archive names are publication aliases. Their bytes, including original internal paths and manifests, are unchanged. No original campaign, auditor, or experimental packager was rerun for this release. Existing historical Git commits and tags remain available. See [PROVENANCE.md](PROVENANCE.md) for the preserved failed gate and the separately executed correction.
