"""Preserve CPU-only test evidence in a new output directory."""
import argparse
import contextlib
import datetime
import json
from pathlib import Path
import unittest

import export_results
import test_export


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=False)
    with (args.output/'tests.log').open('x', encoding='utf-8') as log:
        with contextlib.redirect_stdout(log), contextlib.redirect_stderr(log):
            result = unittest.TextTestRunner(stream=log, verbosity=2).run(
                unittest.defaultTestLoader.loadTestsFromModule(test_export))
    report = dict(status='COMPLETE' if result.wasSuccessful() else 'FAILED',
        utc=datetime.datetime.now(datetime.timezone.utc).isoformat(), tests=result.testsRun,
        failures=len(result.failures), errors=len(result.errors), skipped=len(result.skipped),
        inference_executed=False, scope='Synthetic CPU export/statistics tests; not experiment data',
        sources={p.name:export_results.sha(p) for p in Path(__file__).parent.glob('*.py')})
    export_results.save(args.output/'validation.json', report)
    print(json.dumps(report))
    raise SystemExit(not result.wasSuccessful())
