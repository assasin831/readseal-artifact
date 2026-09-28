"""Read-only checks of the public ISPA evidence; no inference or native auditor."""
import argparse
import csv
import hashlib
import io
import json
import math
from pathlib import Path, PurePosixPath
import statistics
import zipfile

T95_DF5 = 2.570581835636305


def check(ok, message):
    if not ok:
        raise ValueError(message)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def safe_name(name):
    p = PurePosixPath(name)
    return bool(name) and not p.is_absolute() and not any(
        part in ('.', '..') for part in name.split('/')) and '\\' not in name and ':' not in name


def verify_members(z):
    names = [i.filename for i in z.infolist() if not i.is_dir()]
    check(len(z.namelist()) == len(set(z.namelist())), 'duplicate archive entries')
    check(all(safe_name(n) for n in names), 'unsafe archive member path')
    check(z.testzip() is None, 'archive CRC mismatch')
    manifest_names = [n for n in names if n.rsplit('/', 1)[-1] in
                      ('files.json', 'MANIFEST.json', 'SHA256SUMS.txt')]
    verified = 0
    for manifest_name in manifest_names:
        prefix = manifest_name.rsplit('/', 1)[0] + '/' if '/' in manifest_name else ''
        data = z.read(manifest_name)
        if manifest_name.endswith('SHA256SUMS.txt'):
            manifest = {}
            for line in data.decode().splitlines():
                if not line.strip():
                    continue
                digest, path = line.split(maxsplit=1)
                manifest[path.lstrip('*').removeprefix('./')] = digest
        else:
            manifest = json.loads(data)
            if 'files' in manifest:
                manifest = manifest['files']
        check(isinstance(manifest, dict), 'invalid embedded manifest')
        for name, record in manifest.items():
            check(safe_name(name), 'unsafe manifest path')
            member = prefix + name
            check(member in names, 'missing manifested member: ' + member)
            content = z.read(member)
            digest = record['sha256'] if isinstance(record, dict) else record
            check(sha(content) == digest, 'member hash mismatch: ' + member)
            if isinstance(record, dict) and 'bytes' in record:
                check(len(content) == record['bytes'], 'member length mismatch: ' + member)
            verified += 1
    return verified


def number(value):
    if value == '':
        return None
    v = float(value)
    check(math.isfinite(v), 'nonfinite numeric value')
    return v


def interval(values):
    check(len(values) == 6, 'six whole-run observations required')
    if any(v is None for v in values):
        return (None, None, None)
    mean = statistics.mean(values)
    half = T95_DF5 * statistics.stdev(values) / math.sqrt(6)
    return mean, mean - half, mean + half


def close(a, b):
    return a is b if a is None or b is None else math.isclose(a, b, rel_tol=1e-12, abs_tol=1e-10)


def read_table(path):
    with path.open(newline='', encoding='utf-8') as f:
        return list(csv.DictReader(f))


def verify_tables(root):
    folder = root / 'data/jitter-manual-108'
    counts = {'per_run.csv': 108, 'smoke_per_run.csv': 18, 'publications.csv': 97200,
              'recipients.csv': 432, 'summary_t95.csv': 234, 'paired_t95.csv': 169}
    tables = {name: read_table(folder / name) for name in counts}
    for name, rows in tables.items():
        check(len(rows) == counts[name], 'row count mismatch: ' + name)
    groups, runs = {}, {}
    for row in tables['per_run.csv']:
        check(row['run'] not in runs, 'duplicate formal run')
        runs[row['run']] = row
        key = row['condition'], row['method']
        group = groups.setdefault(key, {})
        repeat = int(row['repeat'])
        check(repeat not in group, 'duplicate repetition')
        group[repeat] = row
    conditions = ('homogeneous-periodic-hz30', 'homogeneous-jitter-hz30',
                  'heterogeneous-periodic-hz30', 'heterogeneous-jitter-hz30')
    methods = ('auto-batched', 'manual-checked', 'manual-full', 'copy-in')
    expected_cells = {(c, m) for c in conditions for m in methods} | {
        ('late-periodic-hz30', m) for m in ('auto-batched', 'manual-checked')}
    check(set(groups) == expected_cells, 'condition-method coverage')
    check(all(set(g) == set(range(6)) for g in groups.values()), 'repetition coverage')
    check({(r['condition'], r['method']) for r in tables['smoke_per_run.csv']} == expected_cells,
          'smoke cell coverage')
    metrics = {r['metric'] for r in tables['summary_t95.csv']}
    check(len(metrics) == 13, 'metric coverage')
    checked = 0
    for filename in ('summary_t95.csv', 'paired_t95.csv'):
        paired = filename == 'paired_t95.csv'
        seen = set()
        for row in tables[filename]:
            method = row['contrast'].removesuffix(' minus auto-batched') if paired else row['method']
            key = row['condition'], method, row['metric']
            check(key not in seen, 'duplicate summary metric')
            seen.add(key)
            group = groups[key[:2]]
            values = [number(group[r][row['metric']]) for r in range(6)]
            if paired:
                reference = groups[row['condition'], 'auto-batched']
                check(all(group[r]['arrival_offsets_sha256'] == reference[r]['arrival_offsets_sha256']
                          for r in range(6)), 'paired arrival schedule mismatch')
                base = [number(reference[r][row['metric']]) for r in range(6)]
                values = [None if a is None or b is None else a - b for a, b in zip(values, base)]
            actual = tuple(number(row[k]) for k in ('mean', 'low', 'high'))
            check(all(close(a, b) for a, b in zip(interval(values), actual)), 'interval mismatch')
            n = sum(v is not None for v in values)
            check(int(row['n_planned']) == 6 and int(row['n_observed']) == n, 'interval n mismatch')
            check(row['status'] == ('pointwise_t95_df5' if n == 6 else 'unavailable_missing_run_metric'),
                  'interval missing-value status mismatch')
            checked += 1
        expected = {(c, m, metric) for c, m in expected_cells for metric in metrics
                    if not paired or m != 'auto-batched'}
        check(seen == expected, 'summary/contrast coverage mismatch')

    publications = {}
    for row in tables['publications.csv']:
        check(row['run'] in runs, 'unknown publication run')
        publications.setdefault(row['run'], []).append(row)
    check(set(publications) == set(runs), 'publication run coverage')
    for name, rows in publications.items():
        run = runs[name]
        check(len(rows) == 900 and len({r['tick'] for r in rows}) == 900, 'publication denominator')
        for field in ('condition', 'method', 'repeat'):
            check(all(r[field] == run[field] for r in rows), 'publication identity mismatch')
        for field in ('complete_correct', 'complete_timely'):
            check(all(r[field] in ('True', 'False') for r in rows), 'invalid publication boolean')
            check(sum(r[field] == 'True' for r in rows) == int(run[field]), 'publication numerator')
        check(close(float(run['full_publication_timely_fraction']), int(run['complete_timely']) / 900),
              'publication fraction mismatch')
    recipient_keys = {(r['run'], int(r['consumer'])) for r in tables['recipients.csv']}
    check(recipient_keys == {(name, cid) for name in runs for cid in range(4)}, 'recipient coverage')
    proof = json.loads((folder / 'validation.json').read_text())
    check(proof['status'] == 'COMPLETE' and proof['inference_executed'] is False, 'export incomplete')
    clone = read_table(root / 'data/clone-168/per_run.csv')
    check(len(clone) == 168, 'clone formal row count')
    return {'jitter_manual_rows': counts, 'clone_formal_rows': len(clone), 'verified_t95_intervals': checked}


def verify(root):
    index = json.loads((root / 'evidence-index.json').read_text())
    for name, expected in index['files'].items():
        check(safe_name(name), 'unsafe index path')
        data = (root / name).read_bytes()
        check(len(data) == expected['bytes'] and sha(data) == expected['sha256'], 'file hash/size mismatch: ' + name)
    members = 0
    for archive in index['archives']:
        check(index['files'][archive['path']]['sha256'] == archive['sha256'], 'archive index mismatch')
        with zipfile.ZipFile(root / archive['path']) as z:
            members += verify_members(z)
    return dict(status='PASS', inference_executed=False, native_auditor_rerun=False,
                archived_files_verified=members, preserved_files_verified=len(index['files']),
                archives_verified=len(index['archives']), **verify_tables(root))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    print(json.dumps(verify(args.root.resolve()), indent=2))
