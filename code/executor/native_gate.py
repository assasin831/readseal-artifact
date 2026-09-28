"""Fixed native correctness/fence/overwrite gate, not a performance pilot."""
import runtime
runtime.activate()
import argparse
import gc
import json
import os
from pathlib import Path
import time
import traceback

import torch
from batch_backend import BatchProgram
from components import ComponentProgram
from core import Rejected
from manual_checked import ManualCheckedProgram
from manual_static import ManualRejected, BASE_BOUNDARY
from study_common import configure, inputs, MODELS, cpu_values, exact, tensor_hashes
from variants import edited_export, review_record
from stream_witness import stream_pair, reject_stream_substitution


PROFILES = ('native', 'head', 'composed', 'composed-late')
METHODS = ('auto-batched', 'manual-checked', 'manual-full', 'copy-in')


def ready():
    event = torch.cuda.Event()
    event.record()
    return event


def reject(report, label, call):
    try:
        call()
    except (Rejected, ManualRejected) as error:
        report['rejections'].append(dict(label=label, reason=str(error)))
    else:
        raise AssertionError('Invalid action accepted: ' + label)


def checked_values(ex):
    result = ex.outputs()
    ex.lease.publish_identity()
    return result


def run(folder):
    folder.mkdir(parents=True, exist_ok=False)
    report = dict(status='RUNNING', cases=[], mutations=[], cancellation=[], rejections=[],
                  stream_substitution_witnesses=[],
                  active=None, expected_cases=48, expected_mutations=24, expected_cancellation=6,
                  inference_executed=True, performance_claim=False, gpu_uuid=runtime.GPU)
    def save():
        (folder / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    try:
        configure()
        xs, hashes = inputs('transfusion')
        report['input_hashes'] = hashes
        device_sources = [t.cuda() for t in xs]
        x = xs[0].cuda()
        torch.cuda.synchronize()
        stream, producer = torch.cuda.Stream(), torch.cuda.Stream()
        # The default stream cannot alias the non-default workload stream.
        substitute = torch.cuda.default_stream(x.device)
        stream_pair(stream, substitute)
        for profile in PROFILES:
            oracle = ComponentProgram(x, profile, 'manual-full')
            references = []
            for sid in range(3):
                x.copy_(xs[sid])
                e = oracle.start(x, dict(epoch=41, sequence=sid+1, generation=2*(sid+1)), ready())
                e.submit(0, stream).synchronize()
                values, _ = e.publish()
                references.append(cpu_values(values))
            del e, values, oracle
            gc.collect()
            torch.cuda.empty_cache()
            for method in METHODS:
                program = ComponentProgram(x, profile, method)
                for sid in range(3):
                    key = f'{profile}-{method}-s{sid}'
                    report['active'] = key
                    save()
                    x.zero_()
                    torch.cuda.synchronize()
                    input_ready = torch.cuda.Event()
                    with torch.cuda.stream(producer):
                        torch.cuda._sleep(200_000_000)
                        x.copy_(device_sources[sid], non_blocking=True)
                        input_ready.record(producer)
                    pending = not input_ready.query()
                    assert pending, 'Delayed producer write was not observed pending'
                    pub = dict(epoch=53, sequence=sid+1, generation=2*(sid+1))
                    invocation = program.start(x, pub, input_ready)
                    invocation.submit(0, stream)
                    invocation.events[0].synchronize()
                    assert input_ready.query() and invocation.can_release()
                    released = time.monotonic_ns()
                    before = tensor_hashes((x,))[0]
                    allocation = x.untyped_storage().data_ptr()
                    x.copy_(xs[(sid+1) % 3])
                    torch.cuda.synchronize()
                    overwritten = time.monotonic_ns()
                    after = tensor_hashes((x,))[0]
                    assert before != after and allocation == x.untyped_storage().data_ptr()
                    if method != 'manual-full':
                        invocation.submit(1, stream)
                    invocation.events[-1].synchronize()
                    actual, identity = invocation.publish()
                    assert identity == pub
                    actual = cpu_values(actual)
                    exact(actual, references[sid])
                    file = key + '.pt'
                    torch.save(dict(actual=actual, expected=references[sid]), folder / file)
                    report['cases'].append(dict(key=key, profile=profile, method=method, source=sid,
                        exact_tensors=len(actual), outputs=file, outputs_sha256=runtime.sha(folder/file),
                        producer_ready_pending=pending, read_complete_ns=released,
                        overwrite_complete_ns=overwritten, source_changed=True, same_allocation=True))
                    del invocation, actual
                    save()
                del program
                gc.collect()
                torch.cuda.empty_cache()
            del references
        # The full functional graph is an output oracle, not the checked split executor.
        path = MODELS['transfusion'][0]
        for edit in ('base', 'late_read', 'private_probe', 'remove_late_read'):
            snapshot = edited_export(path, 'transfusion', edit)
            review = review_record(path, 'transfusion', edit)
            from manual_static import fixed_graph
            graph, root, state, _ = fixed_graph(snapshot, x.device, False)
            full = torch.fx.GraphModule(torch.nn.Module(), graph)
            arguments = tuple(n.name for n in graph.nodes if n.op == 'placeholder')
            refs = []
            for cpu in xs:
                x.copy_(cpu)
                torch.cuda.synchronize()
                with torch.inference_mode():
                    values = full(*(x if name == root else state[name] for name in arguments))
                refs.append(cpu_values(values))
            if edit == 'late_read':
                reject(report, 'late-read-needs-safety-boundary-update', lambda:
                       ManualCheckedProgram(snapshot, x, boundary=BASE_BOUNDARY['transfusion']))
            for method in ('auto-batched', 'manual-checked'):
                program = (BatchProgram(snapshot, x) if method == 'auto-batched' else
                           ManualCheckedProgram(snapshot, x, boundary=review['boundary']))
                for sid in range(3):
                    key = f'{edit}-{method}-s{sid}'
                    report['active'] = key
                    save()
                    x.copy_(xs[sid])
                    torch.cuda.synchronize()
                    pub = dict(epoch=61, sequence=sid+1, generation=2*(sid+1))
                    reject(report, key+'-odd-generation', lambda: program.start(x, dict(pub,generation=3), ready()))
                    reject(report, key+'-wrong-ready', lambda: program.start(x, pub, object()))
                    ex = program.start(x, pub, ready())
                    reject(report, key+'-suffix-first', lambda: ex.submit(1, stream))
                    reject(report, key+'-early-publish', lambda: checked_values(ex))
                    ex.submit(0, stream).synchronize()
                    assert ex.lease.can_release(ex.lease.bindings[program.root].allocation)
                    report['active_stream_witness'] = dict(key=key, **stream_pair(stream, substitute))
                    save()
                    witness = reject_stream_substitution(ex, stream, substitute, Rejected)
                    report['stream_substitution_witnesses'].append(dict(key=key, **witness))
                    report['rejections'].append(dict(label=key+'-stream-substitution', reason=witness['reason']))
                    x.copy_(xs[(sid+1)%3])
                    torch.cuda.synchronize()
                    ex.submit(1, stream).synchronize()
                    actual = cpu_values(checked_values(ex))
                    exact(actual, refs[sid])
                    reject(report, key+'-duplicate-publication', lambda: checked_values(ex))
                    file = 'mutation-'+key+'.pt'
                    torch.save(dict(actual=actual, expected=refs[sid]), folder/file)
                    report['mutations'].append(dict(key=key, edit=edit, method=method, source=sid,
                        review=review, exact_tensors=len(actual), outputs=file,
                        outputs_sha256=runtime.sha(folder/file), reuse_after_read=True))
                    save()
                del program
            del state, full, refs, snapshot
            gc.collect()
            torch.cuda.empty_cache()
        for method in ('auto-batched', 'manual-checked'):
            exported = torch.export.load(path)
            program = (BatchProgram(exported, x) if method == 'auto-batched' else ManualCheckedProgram(exported, x))
            pub = dict(epoch=83, sequence=1, generation=2)
            for stage in ('pending', 'submitted', 'all-submitted'):
                report['active'] = method+'-cancel-'+stage
                save()
                ex = program.start(x, pub, ready())
                allocation = ex.lease.bindings[program.root].allocation
                if stage != 'pending':
                    with torch.cuda.stream(stream):
                        torch.cuda._sleep(200_000_000)
                    ex.submit(0, stream)
                    if stage == 'all-submitted':
                        ex.submit(1, stream)
                    assert not ex.events[0].query(), 'Cancellation witness must be pending'
                ex.lease.abort()
                held = not ex.lease.can_release(allocation)
                assert held == (stage != 'pending')
                reject(report, method+'-'+stage+'-cancelled-publish', lambda: checked_values(ex))
                stream.synchronize()
                assert ex.lease.can_release(allocation)
                report['cancellation'].append(dict(method=method, stage=stage,
                    held_until_event=held, released_after_drain=True, publish_rejected=True))
                save()
            # Both implementations execute the identical inherited binding guards.
            fn = program._capsule.functions[0].invoke
            fn.__defaults__ = (None,)
            reject(report, method+'-changed-function', lambda: program.start(x,pub,ready()))
            fn.__defaults__ = None
            with torch.no_grad():
                program._capsule.state[0][1].add_(0)
            reject(report, method+'-changed-owned-state', lambda: program.start(x,pub,ready()))
            del program, ex
        assert len(report['cases']) == 48 and len(report['mutations']) == 24
        assert len(report['cancellation']) == 6 and len(report['rejections']) == 155
        report.update(status='COMPLETE', active=None)
    except BaseException:
        report.update(status='FAILED', traceback=traceback.format_exc())
        traceback.print_exc()
    save()
    (folder / report['status']).write_text(report['status']+'\n')
    return int(report['status'] != 'COMPLETE')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    raise SystemExit(run(args.output))
