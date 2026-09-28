"""Saved-only CPU audit. Does not import the runner or its metric evaluator."""
import runtime
runtime.activate()
import argparse
import hashlib
import itertools
import json
import math
import os
from pathlib import Path
import traceback


def audit_stream_witnesses(report):
    witnesses = report['stream_substitution_witnesses']
    assert len(witnesses) == 24
    assert {w['key'] for w in witnesses} == {r['key'] for r in report['mutations']}
    for witness in witnesses:
        assert witness['admitted_handle'] != witness['candidate_handle'] == 0
        assert witness['admitted_device'] == witness['candidate_device'] == 'cuda:0'
        assert witness['rejected'] is True
        assert witness['reason'] == 'only one CUDA stream is supported'
        assert witness['before'] == witness['after'] == [1, 1, False, False]


def gate(folder):
    import torch
    report = json.loads((folder/'report.json').read_text())
    assert report['status'] == 'COMPLETE' and (folder/'COMPLETE').exists()
    expected = set(itertools.product(('native','head','composed','composed-late'),
                   ('auto-batched','manual-checked','manual-full','copy-in'), range(3)))
    observed = {(r['profile'],r['method'],r['source']) for r in report['cases']}
    assert observed == expected and len(report['cases']) == 48
    assert len(report['mutations']) == 24 and len(report['cancellation']) == 6
    assert len(report['rejections']) == len({r['label'] for r in report['rejections']}) == 155
    audit_stream_witnesses(report)
    total = 0
    for row in report['cases'] + report['mutations']:
        file = folder/row['outputs']
        assert file.parent == folder and runtime.sha(file) == row['outputs_sha256']
        pair = torch.load(file, map_location='cpu')
        assert len(pair['actual']) == len(pair['expected']) == row['exact_tensors']
        for actual, expected in zip(pair['actual'], pair['expected']):
            assert actual.shape == expected.shape and actual.dtype == expected.dtype
            assert torch.isfinite(actual).all().item() and torch.equal(actual, expected)
            total += 1
    for row in report['cases']:
        assert row['producer_ready_pending'] and row['source_changed'] and row['same_allocation']
        assert row['read_complete_ns'] <= row['overwrite_complete_ns']
    for row in report['cancellation']:
        assert row['held_until_event'] == (row['stage'] != 'pending')
        assert row['released_after_drain'] and row['publish_rejected']
    assert not torch.cuda.is_initialized()
    return dict(cases=48, mutations=24, cancellation=6, rejections=155, exact_tensors=total)


def array_hash(array):
    return hashlib.sha256(array.tobytes()).hexdigest()


def performance(folder):
    import numpy as np
    import torch
    from design import arrivals, digest
    r = json.loads((folder/'report.json').read_text())
    assert r['status'] == 'COMPLETE' and (folder/'COMPLETE').exists()
    c, method = r['cell'], r['method']
    assert r['gpu_uuid'] == runtime.GPU and c['consumers'] == 4
    assert r['wrong_outputs'] == r['source_unknown'] == r['final_outstanding'] == 0
    assert not any(r['pool_final'][k][i] for k in ('recipients','writing','quarantined')
                   for i in range(c['ring']))
    sink = json.loads((folder/'sink.json').read_text())
    indexed = {(x['tick'],x['consumer']): x for x in sink}
    assert len(indexed) == len(sink)
    producer = {x['tick']: x for x in r['producer']}
    offsets = arrivals(c)
    assert len(producer) == len(offsets) and r['arrival_offsets_sha256'] == digest(offsets)
    start, end = r['cohort_start_ns'], r['cohort_end_ns']
    assert end-start == round(c['measure_seconds']*1e9)
    cohort = []
    previous_release = {}
    for row in r['producer']:
        assert row['scheduled_ns'] == r['origin_ns'] + offsets[row['tick']]
        assert row['cohort'] == (start <= row['scheduled_ns'] < end)
        assert len(row['enqueued']) == 4 and all(type(x) is bool for x in row['enqueued'])
        if row['cohort']:
            cohort.append(row)
        if 'sequence' not in row:
            assert not any(row['enqueued']) and row['drop_reason'] in ('producer_late','pool_exhausted','credit_exhausted')
            continue
        assert row['sequence'] == row['tick']+1 and row['source_id'] == row['tick'] % 3
        slot = row['slot']
        assert row['write_start_ns'] >= previous_release.get(slot, 0)
        assert row['write_start_ns'] <= row['write_done_ns'] <= row['commit_begin_ns'] <= row['commit_end_ns']
        releases = []
        for cid in range(4):
            receipt = indexed.get((row['tick'],cid))
            assert bool(receipt) == row['enqueued'][cid]
            if receipt is None:
                releases.append(row['cancel_returns_ns'][str(cid)])
                continue
            assert all(receipt[k] == row[k] for k in ('tick','sequence','source_id','scheduled_ns','cohort','slot'))
            assert receipt['identity'] == dict(epoch=987654,sequence=row['sequence'],generation=2*row['sequence'])
            assert receipt['observed_sequence'] == row['sequence'] and receipt['observed_source'] == row['source_id']
            assert receipt['actual_hashes'] == r['references'][cid][row['source_id']]['hashes']
            assert receipt['matching_reference_sources'] == [row['source_id']]
            assert all(receipt[k] for k in ('output_equal','provenance_verified','finite','published'))
            times = [receipt[k] for k in ('received_ns','admission_ns','read_done_ns','release_begin_ns',
                     'release_end_ns','output_done_ns','invocation_retired_ns','sink_enqueue_ns','publish_ns')]
            assert times == sorted(times)
            timely = receipt['publish_ns'] - row['scheduled_ns'] <= round(c['deadline_ms']*1e6)
            assert receipt['deadline_met'] == receipt['verified_timely'] == timely
            assert receipt['private_copy_bytes'] == (r['source_bytes'] if method == 'copy-in' else 0)
            # pool.release linearizes within its begin/end clock bracket.
            # A producer can reserve before the caller logs release_end.
            releases.append(receipt['read_done_ns'])
        previous_release[slot] = max(releases)
    samples = 0
    for cid in range(4):
        worker = json.loads((folder/f'consumer-{cid}.json').read_text())
        assert runtime.sha(folder/f'consumer-{cid}-artifact.json') == worker['artifact_sha256']
        assert len(worker['rows']) == sum(x['consumer'] == cid for x in sink)
        for row in worker['rows']:
            receipt = indexed[row['tick'],cid]
            assert all(receipt[k] == value for k,value in row.items())
        for sid, ref in enumerate(r['references'][cid]):
            tensors = torch.load(folder/ref['file'], map_location='cpu')
            assert [array_hash(x.numpy()) for x in tensors] == ref['hashes']
            assert all(torch.isfinite(x).all().item() for x in tensors)
            sample = folder/f'sample-c{cid}-s{sid}.npz'
            if sample.exists():
                with np.load(sample, allow_pickle=False) as z:
                    assert sorted(z.files) == sorted(f'output_{i}' for i in range(len(tensors)))
                    assert [array_hash(z[f'output_{i}']) for i in range(len(tensors))] == ref['hashes']
                samples += 1
    complete, timely, partial, empty, latency, recipients = 0,0,0,0,[],[0]*4
    for row in cohort:
        rows = [indexed.get((row['tick'],i)) for i in range(4)]
        received = sum(x is not None for x in rows)
        complete += received == 4
        partial += 0 < received < 4
        empty += received == 0
        flags = [x is not None and x['publish_ns']-row['scheduled_ns'] <= round(c['deadline_ms']*1e6) for x in rows]
        timely += all(flags)
        for i, yes in enumerate(flags):
            recipients[i] += yes
        if received == 4:
            latency.append(max(x['publish_ns']-row['scheduled_ns'] for x in rows)/1e6)
    metrics = r['publication_metrics']
    expected = dict(offered_publications=len(cohort), complete_correct=complete, complete_timely=timely,
        full_publication_timely_fraction=timely/len(cohort),
        full_publication_timely_goodput_hz=timely/c['measure_seconds'],
        recipient_timely_goodput_hz=sum(recipients)/c['measure_seconds'],
        partial_publications=partial, zero_correct_publications=empty,
        incomplete_publications=len(cohort)-complete,
        full_publication_p50_ms=float(np.percentile(latency,50)) if latency else None,
        full_publication_p99_ms=float(np.percentile(latency,99)) if latency else None)
    assert len(cohort) == round(c['rate_hz']*c['measure_seconds'])
    for k, value in expected.items():
        assert metrics[k] is None if value is None else math.isclose(metrics[k],value,rel_tol=1e-12,abs_tol=1e-10), k
    assert r['timely'] == sum(recipients) and math.isclose(r['goodput_hz'], expected['recipient_timely_goodput_hz'])
    allowed = set(r['worker_pids'])
    assert r['memory_samples']
    for sample in r['memory_samples']:
        assert all(x['gpu']==runtime.GPU and x['pid'] in allowed for x in sample['compute'])
    assert r['device_peak_bytes'] == max(x['device_used_bytes'] for x in r['memory_samples'])
    assert not torch.cuda.is_initialized()
    return dict(receipts=len(sink), samples_verified=samples, metrics=expected,
                device_peak_bytes=r['device_peak_bytes'], independent_saved_only=True,
                per_receipt_arrays_scope='online exact hashes; saved first sample per consumer/source independently rehashed')


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--kind', choices=('gate','performance'), required=True)
    p.add_argument('--run', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    a.output.mkdir(parents=True, exist_ok=False)
    result = dict(status='RUNNING', inference_executed=False)
    try:
        assert os.environ.get('CUDA_VISIBLE_DEVICES') == ''
        result.update(globals()[a.kind](a.run), status='COMPLETE', report_sha256=runtime.sha(a.run/'report.json'))
    except BaseException:
        result.update(status='FAILED', traceback=traceback.format_exc())
        traceback.print_exc()
    (a.output/'validation.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result))
    return int(result['status'] != 'COMPLETE')


if __name__ == '__main__':
    raise SystemExit(main())
