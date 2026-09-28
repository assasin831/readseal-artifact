"""Native Python import and capsule construction only, with CUDA hidden."""
import runtime
runtime.activate()
import gc
import json
import os
from pathlib import Path
import sys
import traceback


def main():
    out = Path(sys.argv[1])
    out.mkdir(parents=True, exist_ok=False)
    report = dict(status='RUNNING', inference_executed=False, cases=[])
    try:
        assert os.environ.get('CUDA_VISIBLE_DEVICES') == ''
        import torch
        import components
        import run_pipeline
        from batch_backend import BatchProgram, BatchExecution
        from manual_checked import ManualCheckedProgram
        from manual_static import BASE_BOUNDARY, ManualRejected
        from core import Rejected
        from study_common import inputs, MODELS
        from variants import edited_export, review_record
        assert torch.__version__ == '2.1.2+cu121'
        assert not torch.cuda.is_initialized()
        assert ManualCheckedProgram.start is BatchProgram.start
        assert ManualCheckedProgram.guard is BatchProgram.guard
        xs, hashes = inputs('transfusion')
        path = MODELS['transfusion'][0]
        for edit in ('base', 'late_read', 'private_probe', 'remove_late_read'):
            exported = edited_export(path, 'transfusion', edit)
            review = review_record(path, 'transfusion', edit)
            for kind in ('auto', 'manual'):
                program = (BatchProgram(exported, xs[0]) if kind == 'auto' else
                           ManualCheckedProgram(exported, xs[0], boundary=review['boundary']))
                program.guard()
                assert len(program._capsule.groups) == 2
                report['cases'].append(dict(edit=edit, method=kind, review=review,
                                            groups=program._capsule.groups,
                                            source_readers=dict(program.plan.obligations)[program.root]))
                del program
                gc.collect()
            if edit == 'late_read':
                try:
                    ManualCheckedProgram(exported, xs[0], boundary=BASE_BOUNDARY['transfusion'])
                except (Rejected, ManualRejected) as e:
                    report['stale_late_boundary_rejection'] = str(e)
                else:
                    raise AssertionError('Unsafe unchanged manual boundary accepted')
        assert len(report['cases']) == 8 and report['stale_late_boundary_rejection']
        assert not torch.cuda.is_initialized()
        report.update(status='COMPLETE', torch_version=torch.__version__,
                      input_hashes=hashes, cuda_initialized=False,
                      gpu_ready=False, runtime_execution=False)
    except BaseException:
        report.update(status='FAILED', traceback=traceback.format_exc())
    (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report))
    return int(report['status'] != 'COMPLETE')


if __name__ == '__main__':
    raise SystemExit(main())
