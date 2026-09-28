"""Saved-only reviewer exports. Never starts inference or selects winning runs."""
import argparse
from collections import Counter, defaultdict
import csv
import hashlib
import json
import math
from pathlib import Path
import statistics
import zipfile


PREPARED_SHA = '150aefb6d42834e434d7935c8c2c2aa8bf3d15fa189ffb366260da2915574ab9'
ROOT = Path('/www/readseal_ipdps_revision_v6')
BASE = ROOT / 'results/ispa_reviewer_execution_20260927_attempt2'
METRICS = (
    'full_publication_timely_fraction', 'full_publication_timely_goodput_hz',
    'recipient_timely_goodput_hz', 'full_publication_p50_ms', 'full_publication_p99_ms',
    'offered_publications', 'complete_correct', 'complete_timely',
    'partial_publications', 'zero_correct_publications', 'incomplete_publications',
    'sampled_device_peak_mib', 'protected_byte_seconds',
)
SCOPE = (
    'Native A100 component heterogeneity, not four independently trained AV nodes or embedded execution. '
    'All intended recipients and all scheduled publications define the primary denominator. '
    'Complete-publication latency is conditional on all-correct complete outputs; incomplete counts remain visible. '
    'Pointwise t95 df5 uses six whole runs or six paired differences, not frames as replicates. '
    'No equivalence, simultaneous coverage, outlier removal or winner-based condition selection. '
    'Memory is the observed device peak from roughly 0.5-second sampling during the worker-ready-to-drain window; '
    'it excludes earlier model/reference setup and can miss transients. Per-worker allocator peaks are separate '
    'and are not summed into a simultaneous device peak. Original raw traces and saved tensors remain at the '
    'recorded remote paths. Online exact hashes cover receipts; saved first samples have independent tensor checks. '
    'Historical Clone-on-admit wave1 is separate and is not paired across waves.'
)


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def require(condition, message):
    if not condition:
        raise ValueError(message)


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def save(path, value):
    with Path(path).open('x', encoding='utf-8', newline='\n') as f:
        json.dump(value, f, indent=2, allow_nan=False)
        f.write('\n')


def table(path, rows):
    require(bool(rows), 'empty table')
    columns = list(rows[0])
    require(all(set(r) == set(columns) for r in rows), 'inconsistent table columns')
    with Path(path).open('x', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)


def interval(values):
    require(len(values) == 6, 'exactly six whole runs required')
    require(all(v is None or (type(v) in (int, float) and math.isfinite(v))
                for v in values), 'nonfinite or nonnumeric observation')
    missing = sum(v is None for v in values)
    if missing:
        return dict(n_planned=6, n_observed=6-missing, mean=None, low=None, high=None,
                    status='unavailable_missing_run_metric')
    mean = statistics.mean(values)
    half = 2.570581835636305 * statistics.stdev(values) / math.sqrt(6)
    return dict(n_planned=6, n_observed=6, mean=mean, low=mean-half, high=mean+half,
                status='pointwise_t95_df5')


def summaries(rows):
    grouped = defaultdict(dict)
    for row in rows:
        key = row['condition'], row['method']
        require(row['repeat'] not in grouped[key], 'duplicate whole-run repeat')
        grouped[key][row['repeat']] = row
    for group in grouped.values():
        require(set(group) == set(range(6)), 'missing or invalid whole-run repeat')
    output, paired = [], []
    for (condition, method), group in sorted(grouped.items()):
        for metric in METRICS:
            output.append(dict(condition=condition, method=method, metric=metric,
                               **interval([group[r][metric] for r in range(6)])))
        if method == 'auto-batched':
            continue
        require((condition, 'auto-batched') in grouped, 'missing automatic comparator')
        automatic = grouped[condition, 'auto-batched']
        for repeat in range(6):
            require(group[repeat]['arrival_offsets_sha256'] == automatic[repeat]['arrival_offsets_sha256'],
                    'unmatched paired arrival schedule')
        for metric in METRICS:
            differences = [None if group[r][metric] is None or automatic[r][metric] is None
                           else group[r][metric] - automatic[r][metric] for r in range(6)]
            paired.append(dict(condition=condition, contrast=method+' minus auto-batched',
                               metric=metric, **interval(differences)))
    return output, paired


def controller_proof(base, stage, expected_names, evidence):
    control = base / (stage+'-controller')
    state = read(control/'status.json')
    require(state['status'] == 'COMPLETE' and (control/'COMPLETE').is_file(), stage+' incomplete')
    require((control/'exit_code').read_text().strip() == '0', stage+' nonzero exit')
    require(state['started'] == expected_names, stage+' started schedule mismatch')
    require([x['name'] for x in state['completed']] == expected_names, stage+' audited schedule mismatch')
    require(state['completed_count'] == state['started_count'] == len(expected_names)
            and state['unstarted_count'] == 0, stage+' inconsistent counts')
    for name in ('status.json', 'COMPLETE', 'exit_code'):
        evidence[str(control/name)] = sha(control/name)
    return {x['name']: x['validation_sha256'] for x in state['completed']}


def verified_report(base, name, validation_sha, evidence):
    require(Path(name).name == name and name not in ('.', '..'), 'invalid run name')
    report_path = base/name/'report.json'
    audit_path = base/(name+'-audit')/'validation.json'
    require(sha(audit_path) == validation_sha, 'audit changed after controller completion')
    proof = read(audit_path)
    require(proof['status'] == 'COMPLETE' and proof['inference_executed'] is False, 'audit incomplete')
    require(proof['report_sha256'] == sha(report_path), 'report changed after audit')
    report = read(report_path)
    require(report['status'] == 'COMPLETE' and (base/name/'COMPLETE').is_file(), 'run incomplete')
    for path in (report_path, audit_path, base/name/'COMPLETE'):
        evidence[str(path)] = sha(path)
    return report, proof


def run_rows(item, report, proof):
    require(report['method'] == item['method'] and report['cell'] == item['cell'], 'run cell mismatch')
    m = report['publication_metrics']
    for key, value in proof['metrics'].items():
        require(m[key] == value or (value is not None and m[key] is not None
                and math.isclose(m[key], value, rel_tol=1e-12, abs_tol=1e-10)), 'metric differs from audit: '+key)
    require(proof['device_peak_bytes'] == report['device_peak_bytes'], 'memory differs from audit')
    count = round(item['cell']['rate_hz'] * item['cell']['measure_seconds'])
    detail = m['publications']
    require(count == m['offered_publications'] == len(detail), 'offered denominator mismatch')
    require(len({r['tick'] for r in detail}) == count, 'duplicate publication detail')
    require(sum(r['complete_timely'] for r in detail) == m['complete_timely'], 'detail timely count mismatch')
    require(sum(r['complete_correct'] for r in detail) == m['complete_correct'], 'detail complete count mismatch')
    require(report['wrong_outputs'] == report['source_unknown'] == report['final_outstanding'] == 0,
            'nonzero correctness or outstanding counter')
    prefix = dict(run=item['name'], condition=item['condition'], method=item['method'], repeat=item['repeat'])
    row = dict(prefix, arrival_offsets_sha256=report['arrival_offsets_sha256'],
               **{key:m[key] for key in METRICS if key in m},
               sampled_device_peak_mib=report['device_peak_bytes']/2**20,
               protected_byte_seconds=report['protected_byte_seconds'])
    publications = [dict(prefix, **r) for r in detail]
    recipients = []
    stats = {r['consumer']:r['stats'] for r in report['allocator_stats']}
    require(set(stats) == set(range(4)) and len(report['allocator_stats']) == 4, 'allocator consumer coverage')
    require(len(m['recipients']) == 4 and {r['consumer'] for r in m['recipients']} == set(range(4)),
            'recipient coverage')
    for r in sorted(m['recipients'], key=lambda r:r['consumer']):
        cid = r['consumer']
        recipients.append(dict(prefix, **r, profile=item['cell']['profiles'][cid],
            offered_publications=count, allocated_peak_bytes=stats[cid]['allocated_peak_bytes'],
            reserved_peak_bytes=stats[cid]['reserved_peak_bytes']))
    drops = Counter(r.get('drop_reason') or 'none' for r in detail)
    row.update(producer_late_publications=drops['producer_late'],
               pool_exhausted_publications=drops['pool_exhausted'],
               credit_exhausted_publications=drops['credit_exhausted'],
               intended_recipients=count*4,
               enqueued_recipients=sum(r['enqueued'] for r in detail),
               received_recipients=sum(r['received'] for r in detail))
    return row, publications, recipients


def export(base, output):
    require(sha(base/'prepared.json') == PREPARED_SHA, 'unexpected campaign preparation')
    require(not output.exists() and not output.with_suffix('.zip').exists(), 'output already exists')
    frozen = read(base/'prepared.json')
    evidence = {str(base/'prepared.json'):PREPARED_SHA}
    for path, expected in frozen['bindings'].items():
        require(sha(path) == expected, 'frozen binding changed: '+path)
        evidence[path] = expected
    schedule = frozen['schedules']
    require(len(schedule['smoke']) == 18 and len(schedule['formal']) == 108, 'campaign matrix size')
    work = schedule['smoke'] + schedule['formal']
    require(len({r['name'] for r in work}) == 126, 'duplicate scheduled run')
    gates = controller_proof(base, 'gate', ['native-gate'], evidence)
    gate, gate_proof = verified_report(base, 'native-gate', gates['native-gate'], evidence)
    completed = controller_proof(base, 'performance', [r['name'] for r in work], evidence)
    formal, smoke, publications, recipients = [], [], [], []
    for item in work:
        report, proof = verified_report(base, item['name'], completed[item['name']], evidence)
        row, pub, recipient = run_rows(item, report, proof)
        if item['name'].startswith('formal-'):
            formal.append(row)
            publications.extend(pub)
            recipients.extend(recipient)
        else:
            smoke.append(row)
    require(len(publications) == 97200 and len(recipients) == 432, 'formal detail coverage')
    summary, paired = summaries(formal)
    require(len(summary) == 18*len(METRICS) and len(paired) == 13*len(METRICS), 'comparison coverage')
    output.mkdir(parents=True, exist_ok=False)
    for name, rows in (('per_run',formal), ('smoke_per_run',smoke), ('summary_t95',summary),
                       ('paired_t95',paired), ('publications',publications), ('recipients',recipients)):
        table(output/(name+'.csv'), rows)
    save(output/'run_data.json', dict(formal=formal, smoke=smoke, scope=SCOPE))
    save(output/'native_gate.json', dict(report=gate, independent_audit=gate_proof))
    save(output/'prepared.json', frozen)
    save(output/'input_evidence.json', evidence)
    save(output/'analysis_sources.json', {p.name:sha(p) for p in Path(__file__).parent.glob('*.py')})
    save(output/'validation.json', dict(status='COMPLETE', inference_executed=False,
         formal_runs=len(formal), smoke_runs=len(smoke), publications=len(publications),
         recipient_run_rows=len(recipients), summary_rows=len(summary), paired_rows=len(paired),
         prepared_sha256=PREPARED_SHA, scope=SCOPE, raw_evidence_root=str(base)))
    text = '# Reviewer follow-up data\n\n'+SCOPE+'\n\n'
    text += '108 formal runs and 18 smoke runs passed the saved-only per-run audit. '
    text += 'CSV blank cells represent unavailable metrics, not zeros. No confidence limits were clipped.\n\n'
    text += '| Condition | Method | Complete-publication timely fraction, mean [t95] |\n|---|---|---|\n'
    for r in summary:
        if r['metric'] == 'full_publication_timely_fraction':
            text += f"| {r['condition']} | {r['method']} | {r['mean']:.6f} [{r['low']:.6f}, {r['high']:.6f}] |\n"
    with (output/'README.md').open('x', encoding='utf-8') as f:
        f.write(text)
    save(output/'files.json', {p.name:sha(p) for p in sorted(output.iterdir()) if p.is_file()})
    archive = output.with_suffix('.zip')
    with zipfile.ZipFile(archive, 'x', compression=zipfile.ZIP_DEFLATED) as z:
        for p in sorted(output.iterdir()):
            z.write(p, p.name)
    with zipfile.ZipFile(archive) as z:
        require(z.testzip() is None, 'archive CRC verification failed')
        for name, expected in read(output/'files.json').items():
            require(hashlib.sha256(z.read(name)).hexdigest() == expected, 'archive hash mismatch')
    return dict(status='COMPLETE', output=str(output), archive=str(archive), archive_sha256=sha(archive))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--base', type=Path, default=BASE)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(export(args.base, args.output)))
