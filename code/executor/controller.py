"""Single-use quiet-host controller, frozen inputs, continuous interference guard."""
import argparse
import datetime
import fcntl
import json
import os
from pathlib import Path
import shutil
import signal
import subprocess
import sys
import time
import traceback

import runtime
from design import PLAN, schedule


def utc():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def save(path, value):
    temp = path.with_suffix(path.suffix+'.tmp')
    temp.write_text(json.dumps(value,indent=2)+'\n')
    os.replace(temp,path)


def compute():
    raw = subprocess.check_output(['nvidia-smi','--query-compute-apps=gpu_uuid,pid',
                                   '--format=csv,noheader'],text=True,timeout=20)
    return [dict(gpu=s.split(',')[0].strip(),pid=int(s.split(',')[1]))
            for s in raw.splitlines() if s.strip()]


def hardware():
    raw = subprocess.check_output(['nvidia-smi','--query-gpu=uuid,name,mig.mode.current',
                                   '--format=csv,noheader'],text=True,timeout=20)
    return sorted(s.strip() for s in raw.splitlines() if s.strip())


def foreign(rows, group=None):
    for row in rows:
        if row['gpu'] != runtime.GPU or group is None:
            return True
        try:
            if os.getpgid(row['pid']) != group:
                return True
        except ProcessLookupError:
            continue
    return False


def verify(frozen):
    changed = [p for p,h in frozen['bindings'].items() if runtime.sha(p) != h]
    if changed:
        raise RuntimeError('Frozen source/input changed: '+repr(changed))


def sizing(max_historical_bytes=33145295):
    # Planning estimate, not a storage bound. Gates get an additional 1 GiB.
    estimate = max_historical_bytes * (18+108) + 2**30
    return dict(estimated_raw_bytes=estimate, factor=2, gate_allowance_bytes=2**30,
                initial_bytes=max(40*2**30,20*2**30+2*estimate), between_bytes=20*2**30,
                scope='historical max whole-run size for all 126 new runs plus 1GiB gates; planning only')


def prepare():
    prior = runtime.ROOT/'results/ispa_copyin_performance_20260923_attempt1/prepared.json'
    assert runtime.sha(prior) == '8715d718cf48bb9aff440805f3c3d985fdcafde4c99aadac2d1461b8bb838905'
    old = json.loads(prior.read_text())
    verify(old)
    cpu = runtime.ROOT/'results/ispa_reviewer_remote_cpu_20260927_attempt4/report.json'
    check = json.loads(cpu.read_text())
    assert check['status']=='COMPLETE' and len(check['cases'])==8 and not check['cuda_initialized']
    tests = runtime.ROOT/'results/ispa_reviewer_controller_cpu_20260927_attempt2/result.json'
    tested = json.loads(tests.read_text())
    assert tested['status']=='COMPLETE' and tested['tests'] >= 8 and not tested['inference_executed']
    witness = runtime.ROOT/'results/ispa_reviewer_stream_witness_cpu_20260927_attempt1/validation.json'
    witnessed = json.loads(witness.read_text())
    assert witnessed['status']=='COMPLETE' and witnessed['tests'] >= 8
    assert not witnessed['inference_executed']
    for name,h in witnessed['sources'].items():
        assert runtime.sha(runtime.HERE/name)==h
    local = json.loads((runtime.HERE/'local_files.json').read_text())
    assert set(local) == {p.name for p in runtime.HERE.glob('*.py')}
    assert all(runtime.sha(runtime.HERE/name)==h for name,h in local.items())
    bindings = dict(old['bindings'])
    for dep in runtime.DEPS:
        if dep.name.startswith('prototype_'):
            bindings.update({str(p):runtime.sha(p) for p in dep.glob('*.py')})
    for path in (cpu,tests,witness,prior,runtime.HERE/'local_files.json'):
        bindings[str(path)] = runtime.sha(path)
    for name,h in tested['sources'].items():
        assert runtime.sha(runtime.HERE/name)==h
    frozen = dict(status='PREPARED',created_utc=utc(),bindings=bindings,plan=PLAN,
                  schedules={p:schedule(p) for p in ('smoke','formal')},sizing=sizing(),
                  hardware=hardware(),gpu_uuid=runtime.GPU,inference_executed=False)
    assert len(frozen['hardware']) == 2
    assert any(runtime.GPU in line and 'Disabled' in line for line in frozen['hardware'])
    verify(frozen)
    runtime.BASE.mkdir(parents=True,exist_ok=False)
    save(runtime.BASE/'prepared.json',frozen)
    print(json.dumps(dict(status='PREPARED',sha256=runtime.sha(runtime.BASE/'prepared.json'),
                         bindings=len(bindings),sizing=frozen['sizing'])))


def stop_owned(child):
    if child.poll() is None:
        os.killpg(child.pid,signal.SIGTERM)
        try:
            child.wait(timeout=20)
        except subprocess.TimeoutExpired:
            os.killpg(child.pid,signal.SIGKILL)
            child.wait(timeout=20)


def invoke(command, env, log, frozen, timeout, watch):
    with log.open('x') as output:
        child = subprocess.Popen(command,env=env,cwd=runtime.ROOT,stdin=subprocess.DEVNULL,
                                 stdout=output,stderr=subprocess.STDOUT,start_new_session=True)
        started = time.monotonic()
        observations = []
        try:
            while child.poll() is None:
                if time.monotonic()-started > timeout:
                    raise TimeoutError('Owned task timeout; no retry')
                if watch:
                    rows = compute()
                    observations.append(dict(utc=utc(),compute=rows))
                    if foreign(rows,child.pid):
                        raise RuntimeError('Foreign GPU work appeared after execution started: '+repr(rows))
                    if hardware() != frozen['hardware']:
                        raise RuntimeError('GPU inventory/MIG state changed')
                    if shutil.disk_usage(runtime.ROOT).free < frozen['sizing']['between_bytes']:
                        raise RuntimeError('Disk reserve fell below 20GiB')
                time.sleep(1)
            if child.returncode != 0:
                raise RuntimeError(f'Owned task exit {child.returncode}; log={log}; no retry')
        finally:
            stop_owned(child)
            save(log.with_suffix('.monitor.json'),dict(pid=child.pid,exit_code=child.returncode,
                                                       observations=observations))


def tasks(stage):
    if stage == 'gate':
        return [dict(name='native-gate',command=[runtime.PYTHON,'-B',str(runtime.HERE/'native_gate.py'),
                     '--output',str(runtime.BASE/'native-gate')],audit_kind='gate',timeout=1200)]
    return [dict(name=item['name'],phase=phase,item=item,audit_kind='performance',timeout=900,
                 command=[runtime.PYTHON,'-B',str(runtime.HERE/'run_pipeline.py'),'--validated-controller',
                          '--output',str(runtime.BASE/item['name']),
                          '--method',item['method'],'--cell',json.dumps(item['cell'])])
            for phase in ('smoke','formal') for item in schedule(phase)]


def dispatch(stage):
    frozen=json.loads((runtime.BASE/'prepared.json').read_text())
    verify(frozen)
    if stage == 'performance':
        gate=json.loads((runtime.BASE/'native-gate-audit/validation.json').read_text())
        assert gate['status']=='COMPLETE'
        assert gate['report_sha256']==runtime.sha(runtime.BASE/'native-gate/report.json')
        assert (runtime.BASE/'gate-controller/exit_code').read_text().strip()=='0'
    control=runtime.BASE/(stage+'-controller')
    control.mkdir(exist_ok=False)
    with (control/'launcher.log').open('x') as log:
        child=subprocess.Popen([runtime.PYTHON,'-B','-u',str(Path(__file__)),'run','--stage',stage],
            env=runtime.environment(False),cwd=runtime.ROOT,stdin=subprocess.DEVNULL,stdout=log,
            stderr=subprocess.STDOUT,start_new_session=True,close_fds=True)
    save(control/'dispatch.json',dict(pid=child.pid,utc=utc(),stage=stage))
    print(json.dumps(dict(pid=child.pid,stage=stage,status='DISPATCHED')))


def run(stage):
    frozen=json.loads((runtime.BASE/'prepared.json').read_text())
    control=runtime.BASE/(stage+'-controller')
    with (control/'RUN_CLAIMED').open('x') as claim:
        claim.write(str(os.getpid())+'\n')
    work=tasks(stage)
    status=dict(status='WAITING_FOR_QUIET_HOST',stage=stage,started_utc=utc(),active=None,
                started=[],completed=[],expected=len(work),inference_executed=False)
    lock=None
    rc=2
    try:
        verify(frozen)
        until=time.monotonic()+24*3600
        while True:
            rows=compute()
            free=shutil.disk_usage(runtime.ROOT).free
            status.update(checked_utc=utc(),compute=rows,free_bytes=free)
            save(control/'status.json',status)
            if not rows and free>=frozen['sizing']['initial_bytes']:
                candidate=(runtime.ROOT/'borrowplan_gpu0.lock').open('a')
                try:
                    fcntl.flock(candidate,fcntl.LOCK_EX|fcntl.LOCK_NB)
                except BlockingIOError:
                    candidate.close()
                else:
                    time.sleep(5)
                    if not compute() and hardware()==frozen['hardware']:
                        lock=candidate
                        break
                    candidate.close()
            if time.monotonic()>until:
                raise TimeoutError('Initial quiet-host/storage wait exceeded 24h; no inference')
            time.sleep(30)
        status['status']='RUNNING'
        for task in work:
            verify(frozen)
            assert hardware()==frozen['hardware'], 'Hardware changed'
            assert not compute(), 'Foreign compute before task; no automatic continuation'
            assert shutil.disk_usage(runtime.ROOT).free>=frozen['sizing']['between_bytes']
            status['active']=task['name']
            status['started'].append(task['name'])
            status['inference_executed']=True
            save(control/'status.json',status)
            invoke(task['command'],runtime.environment(True),control/(task['name']+'.log'),
                   frozen,task['timeout'],True)
            verify(frozen)
            audit_dir=runtime.BASE/(task['name']+'-audit')
            invoke([runtime.PYTHON,'-B',str(runtime.HERE/'audit.py'),'--kind',task['audit_kind'],
                    '--run',str(runtime.BASE/task['name']),'--output',str(audit_dir)],
                   runtime.environment(False),control/(task['name']+'-audit.log'),frozen,300,False)
            proof=json.loads((audit_dir/'validation.json').read_text())
            assert proof['status']=='COMPLETE'
            status['completed'].append(dict(name=task['name'],validation_sha256=runtime.sha(audit_dir/'validation.json')))
            status['active']=None
            save(control/'status.json',status)
            print(json.dumps(dict(status='RUN_COMPLETE',name=task['name'],done=len(status['completed']),total=len(work))),flush=True)
        status['status']='COMPLETE'
        rc=0
    except BaseException:
        status.update(status='FAILED',failure=traceback.format_exc())
        traceback.print_exc()
    finally:
        if lock is not None:
            lock.close()
    status.update(ended_utc=utc(),completed_count=len(status['completed']),
                  started_count=len(status['started']),unstarted_count=len(work)-len(status['started']))
    save(control/'status.json',status)
    (control/status['status']).write_text(status['status']+'\n')
    (control/'exit_code').write_text(str(rc)+'\n')
    return rc


if __name__ == '__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('action',choices=('prepare','dispatch','run'))
    parser.add_argument('--stage',choices=('gate','performance'),default='gate')
    args=parser.parse_args()
    if args.action=='prepare':
        prepare()
    elif args.action=='dispatch':
        dispatch(args.stage)
    else:
        raise SystemExit(run(args.stage))
