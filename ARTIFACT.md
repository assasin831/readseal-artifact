# Verification and Reproduction

## Verify the Download

```sh
git clone --branch ISPA https://github.com/assasin831/readseal-artifact.git
cd readseal-artifact
git rev-parse HEAD
python tools/verify_results.py
python tools/verify_manuscript.py
python -m unittest discover -s tools -p "test_*.py"
```

The verifiers require Python 3.10 or later and the standard library. They read saved files without importing the execution code or starting GPU work. Both return a nonzero exit code on failure.

`verify_results.py` checks six archive hashes, copied-file hashes, embedded manifests, formal run counts, recipient coverage, the complete-publication denominator and 403 summary/paired intervals. `verify_manuscript.py` checks the paper and source ZIP hashes, ZIP CRCs, the exact archive contents and the source manifest.

[evidence-index.json](evidence-index.json) lists experimental files and their SHA-256 hashes. [release.json](manuscript/ISPA/release.json) records the manuscript files. ISPA is a maintained branch; the Git commit identifies the complete snapshot.

## Build the Paper

See the [LaTeX build instructions](manuscript/ISPA/source/README.md). The source includes the bibliography, document class and eight figure PDFs. Figure data and paper labels are mapped in [DATA_GUIDE.md](DATA_GUIDE.md).

The [clean-build check](manuscript/ISPA/clean-rebuild-check.json) compares a fresh source-ZIP build with the published PDF. The eight pages match in extracted text, geometry, links and rendered pixels at 144 and 300 dpi in the recorded environment. The [source manifest](manuscript/ISPA/source/MANIFEST.json) covers every bundled file except itself.

## Analyze the Saved Measurements

The [108-run exporter](code/analysis/export_results.py) and its [CPU tests](code/analysis/test_export.py) are preserved with the measurements. The exporter reads the original campaign layout, including some per-run records not distributed in the compact archive. The portable verifier above checks the public CSVs and their intervals without those missing records. Earlier study archives contain their corresponding analysis scripts.

The 108-run jitter/manual and 168-run clone campaigns each use six whole-run repetitions and pointwise Student-t 95% intervals with five degrees of freedom. Earlier studies retain their recorded protocols. Campaigns are analyzed separately. Missing latencies are unavailable, not zero. [RESULTS.md](RESULTS.md) describes the metrics and measurement limits.

## Execution Sources

[code/executor](code/executor) contains the frozen executor for the corrected native gate and 108-run campaign. It retains its original relative dependencies and paths; it is not a portable one-command benchmark. Some large weights, native engines, tensor dumps and worker traces are not included in this compact release.

The [prepared record](data/jitter-manual-108/prepared.json) binds 172 source, input and proof files. [Input evidence](data/jitter-manual-108/input_evidence.json), [export validation](data/jitter-manual-108/validation.json), [controller steps](provenance/corrected-gate/execution_steps.json) and the [audit binding check](provenance/corrected-gate/completed_audit_binding_check.json) document the execution. Public hashes establish file identity but do not replace unavailable inputs needed to rerun native tensor comparisons.

## Provenance

Archive bytes and internal paths are unchanged. [PROVENANCE.md](PROVENANCE.md) records the initial failed gate, the corrected test fixture and the completed campaign. Partial results from the failed gate are not counted as successful validation. CPU tests are software checks, not GPU performance measurements.
