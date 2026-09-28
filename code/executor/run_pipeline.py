"""Reviewer follow-up fork: real component heterogeneity and precomputed jitter.

NOT GPU-validated yet. Launch only through a separately validated controller.
"""
import argparse
import gc
import hashlib
import json
import math
import os
from pathlib import Path
import queue
import random
import threading
import time
import traceback

import numpy as np
import torch
import torch.multiprocessing as mp
from streaming_retention_v1 import RetentionPool
from study_common import *
from metrics import union_byte_seconds
from components import ComponentProgram
from design import METHODS, arrivals, digest
from publication_metrics import evaluate


def source_inventory():
    from common import inventory
    paths = inventory()
    paths.update({str(p): sha(p) for p in Path(__file__).parent.glob('*.py')})
    return paths


def consumer(cid, method, cell, commands, control, sink, tensors, pool, oracle, destination):
    try:
        configure()
        slots, handles = tensors.get(timeout=180)
        events = [torch.cuda.Event.from_ipc_handle(0,h) for h in handles]
        profile = cell['profiles'][cid]
        program = ComponentProgram(slots[0], profile, method)
        stream = torch.cuda.Stream()
        folder=Path(destination)
        (folder/f'consumer-{cid}-artifact.json').write_text(json.dumps(program.artifact,indent=2)+'\n')
        # Warm the actual path before the common arrival window; these invocations
        # use a private input and never discharge a producer loan.
        private=slots[0].clone()
        torch.cuda.synchronize()
        for k in range(10):
            ready=torch.cuda.Event()
            ready.record()
            ex=program.start(private,dict(epoch=17,sequence=k+1,generation=2*(k+1)),ready)
            ex.submit(0,stream)
            if method!='manual-full':
                ex.submit(1,stream)
            ex.events[-1].synchronize()
            ex.publish()
        del private,ex
        torch.cuda.synchronize()
        gc.collect()
        torch.cuda.empty_cache()
        torch.cuda.reset_peak_memory_stats()
        control.put(dict(kind='ready',consumer=cid,pid=os.getpid()))
        rows=[]
        while True:
            req=commands.get(timeout=180)
            if req['op']=='stop':
                break
            row=dict(req,consumer=cid,received_ns=now())
            slot,seq=req['slot'],req['sequence']
            assert pool.held(slot,seq,cid)
            # The source ledger is not supplied by the descriptor/runtime.
            row['observed_sequence']=int(oracle[2*slot])
            row['observed_source']=int(oracle[2*slot+1])
            assert (row['observed_sequence'],row['observed_source'])==(seq,req['source_id'])
            x=slots[slot]
            pub=dict(epoch=987654,sequence=seq,generation=2*seq)
            row['admission_ns']=now()
            ex=program.start(x,pub,events[slot])
            ex.submit(0,stream)
            if method!='manual-full':
                ex.submit(1,stream)
            ex.events[0].synchronize()
            row['read_done_ns']=now()
            assert ex.can_release()
            row['release_begin_ns']=now()
            pool.release(slot,seq,cid)
            row['release_end_ns']=now()
            ex.events[-1].synchronize()
            row['output_done_ns']=now()
            actual,identity=ex.publish()
            assert identity==pub
            row['identity']=identity
            payload=[t.detach().cpu().contiguous().numpy() for t in actual]
            row['profile'] = profile
            row['composition'] = dict(ex.trace)
            row['private_copy_bytes'] = ex.trace.get('private_copy_bytes', 0)
            del ex,actual
            row['invocation_retired_ns'] = now()
            row['sink_enqueue_ns']=now()
            sink.put(dict(kind='output',row=dict(row),arrays=payload))
            rows.append(row)
            del payload
        torch.cuda.synchronize()
        stats=dict(allocated_peak_bytes=torch.cuda.max_memory_allocated(),
                   reserved_peak_bytes=torch.cuda.max_memory_reserved())
        (folder/f'consumer-{cid}.json').write_text(json.dumps(dict(rows=rows,stats=stats,
            sources=source_inventory(),artifact_sha256=sha(folder/f'consumer-{cid}-artifact.json')),indent=2)+'\n')
        sink.put(dict(kind='consumer_done',consumer=cid))
        control.put(dict(kind='done',consumer=cid,stats=stats))
    except BaseException:
        control.put(dict(kind='error',consumer=cid,traceback=traceback.format_exc()))
        raise


def output_sink(messages,control,destination,references,n,deadline_ms,credits):
    os.environ['CUDA_VISIBLE_DEVICES']=''
    torch.set_num_threads(1)
    received=[]
    done=set()
    try:
        while len(done)<n:
            msg=messages.get(timeout=300)
            handed_off=now()
            if msg['kind']=='consumer_done':
                assert msg['consumer'] not in done
                done.add(msg['consumer'])
                continue
            row=dict(msg['row'],publish_ns=handed_off)
            with credits.get_lock():
                assert credits.value > 0
                credits.value -= 1
                row['credit_return_ns'] = now()
            arrays=msg['arrays']
            hashes=[hashlib.sha256(x.tobytes()).hexdigest() for x in arrays]
            consumer_refs=references[row['consumer']]
            expected=consumer_refs[row['source_id']]
            matching=[sid for sid,record in enumerate(consumer_refs) if hashes==record['hashes']]
            row.update(actual_hashes=hashes,output_equal=hashes==expected['hashes'],
                finite=all(np.isfinite(x).all() for x in arrays),matching_reference_sources=matching,
                provenance_verified=(matching==[row['source_id']] and row['observed_sequence']==row['sequence']
                                     and row['observed_source']==row['source_id']),published=True)
            row['deadline_met']=handed_off-row['scheduled_ns']<=round(deadline_ms*1e6)
            row['verified_timely']=bool(row['output_equal'] and row['provenance_verified']
                                       and row['finite'] and row['deadline_met'])
            # Persist first output per source/consumer plus complete hashes for all.
            name=f"sample-c{row['consumer']}-s{row['source_id']}.npz"
            path=Path(destination)/name
            if not path.exists():
                np.savez(path,**{f'output_{i}':v for i,v in enumerate(arrays)})
            received.append(row)
        (Path(destination)/'sink.json').write_text(json.dumps(received,indent=2)+'\n')
        control.put(dict(kind='sink_done',count=len(received)))
    except BaseException:
        control.put(dict(kind='sink_error',traceback=traceback.format_exc()))
        raise


def wait_messages(control,n,kind):
    replies=[control.get(timeout=300) for _ in range(n)]
    assert all(r['kind']==kind for r in replies), replies
    return replies


def measure_cell(folder,cell,method):
    folder.mkdir()
    xs,input_hashes=inputs('transfusion')
    sources=[x.cuda() for x in xs]
    n,ring=cell['consumers'],cell['ring']
    stream=torch.cuda.Stream()
    references=[]
    for cid,profile in enumerate(cell['profiles']):
        reference=ComponentProgram(sources[0],profile,'manual-full')
        records=[]
        for sid,x in enumerate(sources):
            e=torch.cuda.Event()
            e.record()
            ex=reference.start(x,dict(epoch=17,sequence=sid+1,generation=2*(sid+1)),e)
            ex.submit(0,stream).synchronize()
            ys,_=ex.publish()
            values=cpu_values(ys)
            name=f'reference-c{cid}-s{sid}.pt'
            torch.save(values,folder/name)
            records.append(dict(hashes=tensor_hashes(values),file=name,profile=profile))
        assert len({tuple(r['hashes']) for r in records})==3
        references.append(records)
        del ex,ys,values,reference
    gc.collect()
    torch.cuda.empty_cache()
    slots=[torch.empty_like(sources[0]) for _ in range(ring)]
    events=[torch.cuda.Event(interprocess=True) for _ in slots]
    for x,e in zip(slots,events):
        x.copy_(sources[0])
        e.record()
    torch.cuda.synchronize()
    handles=[bytes(e.ipc_handle()) for e in events]
    ctx=mp.get_context('spawn')
    pool=RetentionPool(ctx,ring,n)
    oracle=ctx.RawArray('Q',ring*2)
    credits=ctx.Value('i',0)
    assert cell['outstanding_cap'] == 0 or cell['outstanding_cap'] >= n
    commands=[ctx.Queue(maxsize=cell['queue']) for _ in range(n)]
    tensors=[ctx.Queue() for _ in range(n)]
    control,sink_control,sinkq=ctx.Queue(),ctx.Queue(),ctx.Queue()
    collector=ctx.Process(target=output_sink,args=(sinkq,sink_control,str(folder),references,n,cell['deadline_ms'],credits))
    workers=[ctx.Process(target=consumer,args=(i,method,cell,commands[i],control,sinkq,tensors[i],
                                             pool,oracle,str(folder))) for i in range(n)]
    prows=[]
    memory=[]
    monitor_errors=[]
    stop=threading.Event()
    def monitor(allowed):
        while not stop.is_set():
            try:
                pids=compute_pids()
                if any(r['gpu']!=GPU or r['pid'] not in allowed for r in pids):
                    monitor_errors.append(dict(reason='foreign compute',pids=pids))
                raw=subprocess.check_output(['nvidia-smi','--query-gpu=uuid,memory.used',
                                              '--format=csv,noheader,nounits'],text=True)
                mib=int(next(line for line in raw.splitlines() if line.startswith(GPU)).split(',')[1])
                memory.append(dict(time_ns=now(),device_used_bytes=mib*2**20,compute=pids))
            except BaseException:
                monitor_errors.append(dict(reason=traceback.format_exc()))
            stop.wait(.5)
    import subprocess
    thread=None
    try:
        collector.start()
        for worker,tq in zip(workers,tensors):
            worker.start()
            tq.put((slots,handles))
        ready=wait_messages(control,n,'ready')
        allowed={os.getpid()}|{r['pid'] for r in ready}
        thread=threading.Thread(target=monitor,args=(allowed,),daemon=True)
        thread.start()
        origin=now()+300_000_000
        begin=origin+round(cell['warmup_seconds']*1e9)
        end=begin+round(cell['measure_seconds']*1e9)
        finish=end+round(cell['deadline_ms']*1e6)
        period=1e9/cell['rate_hz']
        offsets=arrivals(cell)
        for tick,offset in enumerate(offsets):
            if monitor_errors:
                raise RuntimeError('host interference; preserve current run, no retry')
            planned=origin+offset
            delay=(planned-now())/1e9
            if delay>0:
                time.sleep(delay)
            row=dict(tick=tick,scheduled_ns=planned,cohort=begin<=planned<end,
                     producer_start_ns=now(),enqueued=[False]*n,drop_reason=None,
                     cancel_returns_ns={})
            prows.append(row)
            if now()-planned>period:
                row['drop_reason']='producer_late'
                continue
            with credits.get_lock():
                row['outstanding_before'] = credits.value
                if cell['outstanding_cap'] and credits.value+n > cell['outstanding_cap']:
                    row['drop_reason']='credit_exhausted'
                    continue
                row['credit_admit_ns']=now()
                credits.value += n
                row['outstanding_after']=credits.value
            seq=tick+1
            slot=pool.reserve(seq)
            if slot is None:
                row['drop_reason']='pool_exhausted'
                with credits.get_lock():
                    credits.value -= n
                    row['credit_cancel_ns']=now()
                continue
            row['write_start_ns']=now()
            sid=tick%3
            slots[slot].copy_(sources[sid],non_blocking=True)
            events[slot].record()
            events[slot].synchronize()
            row['write_done_ns']=now()
            oracle[2*slot],oracle[2*slot+1]=seq,sid
            row['commit_begin_ns']=now()
            pool.commit(slot,seq,range(n))
            row.update(commit_end_ns=now(),sequence=seq,slot=slot,source_id=sid)
            req={k:row[k] for k in ('tick','scheduled_ns','cohort','sequence','slot','source_id')}
            for cid,q in enumerate(commands):
                try:
                    q.put_nowait(dict(req,op='request'))
                    row['enqueued'][cid]=True
                except queue.Full:
                    pool.release(slot,seq,cid)
                    row['cancel_returns_ns'][str(cid)]=now()
                    with credits.get_lock():
                        credits.value -= 1
                        row.setdefault('credit_queue_cancel_ns',{})[str(cid)]=now()
            row['producer_done_ns']=now()
        for q in commands:
            q.put(dict(op='stop'),timeout=180)
        replies=wait_messages(control,n,'done')
        wait_messages(sink_control,1,'sink_done')
        for worker in workers+[collector]:
            worker.join(60)
            assert worker.exitcode==0
        stop.set()
        thread.join(10)
        assert not monitor_errors,monitor_errors
        assert credits.value == 0
        state=pool.snapshot()
        assert not any(state['recipients']+state['writing']+state['quarantined'])
        sink_rows=json.loads((folder/'sink.json').read_text())
        selected=[r for r in prows if r['cohort']]
        published=[r for r in sink_rows if r['cohort']]
        wrong=sum(not r['output_equal'] for r in published)
        unknown=sum(not r['provenance_verified'] for r in published)
        assert wrong==unknown==0
        consumer_rows=[r for cid in range(n) for r in json.loads((folder/f'consumer-{cid}.json').read_text())['rows']]
        returns={(r['sequence'],r['consumer']):r['release_end_ns'] for r in consumer_rows}
        intervals=[]
        for r in prows:
            if 'sequence' not in r:
                continue
            last=max(returns[(r['sequence'],cid)] if r['enqueued'][cid] else r['cancel_returns_ns'][str(cid)]
                     for cid in range(n))
            intervals.append(dict(slot=r['slot'],sequence=r['sequence'],start_ns=r['commit_begin_ns'],end_ns=last))
        byte_time=union_byte_seconds(intervals,begin,end,sources[0].numel()*4)
        report=dict(status='COMPLETE',cell=cell,method=method,origin_ns=origin,cohort_start_ns=begin,
            cohort_end_ns=end,producer=prows,references=references,input_hashes=input_hashes,intervals=intervals,
            gpu_uuid=GPU,worker_pids=sorted(allowed),memory_samples=memory,allocator_stats=replies,
            pool_final=state,final_outstanding=credits.value,credit_policy='all recipients atomically admitted; return at sink receipt',source_bytes=sources[0].numel()*4,pool_bytes=ring*sources[0].numel()*4,
            sources=source_inventory(),wrong_outputs=wrong,source_unknown=unknown,
            arrivals=len(selected)*n,publications=len(published),timely=sum(r['verified_timely'] for r in published),
            goodput_hz=sum(r['verified_timely'] for r in published)/cell['measure_seconds'],
            protected_byte_seconds=byte_time,device_peak_bytes=max(r['device_used_bytes'] for r in memory))
        report['arrival_offsets_sha256']=digest(offsets)
        report['publication_metrics']=evaluate(prows,sink_rows,n,begin,end,cell['deadline_ms'])
        write_report(folder,report)
        (folder/'COMPLETE').write_text('Unbarriered execution; interpretation is bound to the campaign plan.\n')
        return {k:report[k] for k in ('method','arrivals','publications','timely','goodput_hz','protected_byte_seconds','device_peak_bytes')}
    except BaseException:
        write_report(folder,dict(status='FAILED',cell=cell,method=method,producer=prows,traceback=traceback.format_exc()))
        (folder/'FAILED').write_text('No retry.\n')
        raise
    finally:
        stop.set()
        if thread:
            thread.join(10)
        # Only children created for this run can be terminated on failure.
        for w in workers+[collector]:
            if w.pid and w.is_alive():
                w.terminate()
                w.join(30)


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--output',type=Path,required=True)
    p.add_argument('--cell',required=True)
    p.add_argument('--method',choices=METHODS,required=True)
    p.add_argument('--validated-controller',action='store_true')
    a=p.parse_args()
    if not a.validated_controller:
        raise RuntimeError('requires tested controller, frozen inputs and correctness preflight')
    assert not compute_pids(), 'foreign compute; no inference'
    configure()
    print(json.dumps(measure_cell(a.output,json.loads(a.cell),a.method)),flush=True)
    return 0


if __name__=='__main__':
    raise SystemExit(main())

