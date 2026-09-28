"""One fresh output per CPU preparation; never labels preparation as GPU data."""
import argparse
import ast
import datetime
import hashlib
import json
from pathlib import Path
import unittest

from design import PLAN, arrivals, digest, schedule
import test_cpu


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--output',type=Path,required=True)
    args=p.parse_args()
    args.output.mkdir(parents=True,exist_ok=False)
    source=Path(__file__).parent
    bindings={str(path):hashlib.sha256(path.read_bytes()).hexdigest()
              for path in sorted(source.iterdir()) if path.suffix in ('.py','.md')}
    with (args.output/'tests.log').open('x',encoding='utf-8') as stream:
        suite=unittest.defaultTestLoader.loadTestsFromModule(test_cpu)
        result=unittest.TextTestRunner(stream=stream,verbosity=2).run(suite)
    parsed=[]
    for path in source.glob('*.py'):
        ast.parse(path.read_text(encoding='utf-8'))
        parsed.append(path.name)
    frozen=dict(plan=PLAN,schedules={phase:schedule(phase) for phase in ('smoke','formal')},
                arrival_hashes={row['name']:digest(arrivals(row['cell']))
                                for phase in ('smoke','formal') for row in schedule(phase)})
    (args.output/'plan.json').write_text(json.dumps(frozen,indent=2)+'\n',encoding='utf-8')
    validation=dict(status='COMPLETE' if result.wasSuccessful() else 'FAILED',
                    utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                    tests=result.testsRun,failures=len(result.failures),errors=len(result.errors),
                    skips=len(result.skipped),source_bindings=bindings,ast_parsed=sorted(parsed),
                    plan_sha256=hashlib.sha256((args.output/'plan.json').read_bytes()).hexdigest(),
                    native_inference_executed=False,gpu_ready=False,
                    limitation='CPU metric/schedule and actual lease state tests; CUDA adapters only syntax checked',
                    pending=['native manual-check parity','heterogeneous exact tensors','producer-ready CUDA fence',
                             'native cancellation cleanup','tested controller and disk sizing','all formal performance runs'])
    (args.output/'validation.json').write_text(json.dumps(validation,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:validation[k] for k in ('status','tests','failures','errors','gpu_ready')}))
    return 0 if result.wasSuccessful() else 1


if __name__=='__main__': raise SystemExit(main())
