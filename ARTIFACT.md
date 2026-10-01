# Verification and Reproduction

## Verify the Saved Evidence

Download the current `ISPA` branch, or clone it:

```sh
git clone --branch ISPA https://github.com/assasin831/readseal-artifact.git
cd readseal-artifact
python tools/verify_results.py
python tools/verify_manuscript.py
python -m unittest discover -s tools -p "test_*.py"
```

Python 3.10 or later is sufficient; the verifier uses only the standard library. It is read-only, does not import the execution code, and starts no GPU jobs. It verifies archive and copied-file hashes, embedded manifests where supplied, both formal CSV row counts, the new campaign's publication denominator and recipient coverage, and all 403 summary/paired intervals in that campaign. It prints a JSON result and returns a nonzero exit code on failure.

The separate manuscript verifier defaults to ISPA. It checks the current PDF and source ZIP hashes, ZIP CRCs, the exact archive member list, and every source-manifest entry against both the browsable source tree and ZIP. See the [publication notes](manuscript/ISPA/README.md). Use --revision r21, --revision r19, --revision r17, --revision r16, or --revision r15 for preserved preceding packages. It checks packaging integrity, not experimental validity; the separate publication report covers page text, links, fonts and build checks.

`evidence-index.json` records the SHA-256 and length of each byte-preserved evidence file. It covers data and execution-source snapshots, not newly written explanatory Markdown or the portable verifier itself. Record `git rev-parse HEAD` to pin a particular ISPA publication; the branch may advance. Existing historical tags remain fixed.

## Recompute Paper Tables

The [current ISPA source](manuscript/ISPA/source/README.md) is a self-contained paper build based on r33, retaining all eight author-supplied figure PDFs. [release.json](manuscript/ISPA/release.json) records paper and ZIP hashes; its internal [MANIFEST.json](manuscript/ISPA/source/MANIFEST.json) covers every bundled file besides itself. The [publication check](manuscript/ISPA/source/qa/ISPA_publication_check.json) verifies eight pages and unchanged extracted page text except for the artifact URL. Pixel identity across TeX distributions is not claimed. The [original r21 package](https://github.com/assasin831/readseal-artifact/tree/ispa2026-r21/manuscript/r21/source) preserves the earlier CSV inputs, native PowerPoint generators, editable figures and saved-data extraction scripts. Historical verification records remain labeled for their own revisions.

The original r21 source package linked above includes `scripts/extract_artifact.py` and `scripts/extract_followup.py`. The former reads `archives/ispa2026-rate-slots-evidence.zip`; the latter reads the 108-run and 168-run archives. These scripts derive plotting tables from saved records. They do not rerun inference, and they are not needed to compile the reconstructed LaTeX source.

The new campaign's [original saved-only exporter](code/analysis/export_results.py) and its [CPU tests](code/analysis/test_export.py) are included byte-for-byte. Its original SHA-256 is `1af35d3f4f7ec154ca3ac62d34e333c0a02cc1cbe582ce2cc71aa8c6ffd4a9e8`. It expects the original campaign directory, including per-run records not all present in the compact archive. Use the portable verifier above to check the public compact export.

## Execution Sources and Coverage

[code/executor](code/executor) contains the frozen source for the corrected native gate and the 108-run campaign. The snapshot retains its original file hashes, relative dependencies, and execution paths. It is supplied for inspection, not as a portable one-command inference benchmark. Older runtime dependencies and scripts are also present in the earlier evidence archives. Saved records bind model, engine, input and output files by hash; some large weights, native engines, tensor dumps, and worker traces are not included in this compact release. Hash records are not substitutes for those unavailable bytes.

The [prepared record](data/jitter-manual-108/prepared.json) binds 172 source, input and proof files. The [input evidence](data/jitter-manual-108/input_evidence.json), [export validation](data/jitter-manual-108/validation.json), [controller steps](provenance/corrected-gate/execution_steps.json), and [completed audit binding check](provenance/corrected-gate/completed_audit_binding_check.json) describe the saved execution. A third party can check the exported measurements and public source hashes without the GPU. Re-executing every native tensor comparison requires the separately recorded original inputs and environment.

Both new campaigns use six whole-run repetitions and pointwise Student-t 95% intervals with five degrees of freedom. Earlier campaigns use their own recorded analysis protocols. Do not replace run-level replication with frame counts or combine campaigns.

## Archive Integrity

The new archive names are publication aliases. Their bytes, including original internal paths and manifests, are unchanged. No original campaign, auditor, or experimental packager was rerun for this release. Existing historical Git commits and tags remain available. See [PROVENANCE.md](PROVENANCE.md) for the preserved failed gate and the separately executed correction.
