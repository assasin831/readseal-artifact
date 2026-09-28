"""Synthetic CPU tests, not experimental observations."""
import copy
import math
import unittest

import export_results as e


def fixture():
    rows = []
    for method, extra in (('auto-batched',0), ('manual-checked',2), ('copy-in',-1)):
        for repeat in range(6):
            rows.append(dict(condition='SYNTHETIC', method=method, repeat=repeat,
                arrival_offsets_sha256=str(repeat), **{m:repeat+extra for m in e.METRICS}))
    return rows


def run_fixture():
    item = dict(name='formal-SYNTHETIC', condition='SYNTHETIC', method='copy-in', repeat=0,
                cell=dict(rate_hz=1, measure_seconds=2, profiles=['synthetic']*4))
    detail = [dict(tick=i, complete_timely=False, complete_correct=False,
                   enqueued=i, received=i, drop_reason='pool_exhausted' if i==0 else None)
              for i in range(2)]
    metrics = {m:0 for m in e.METRICS if m not in ('sampled_device_peak_mib','protected_byte_seconds')}
    metrics.update(offered_publications=2, publications=detail,
                   recipients=[dict(consumer=i, timely=0, timely_fraction=0, p50_ms=None, p99_ms=None)
                               for i in range(4)])
    report = dict(status='COMPLETE', cell=copy.deepcopy(item['cell']), method='copy-in',
        publication_metrics=metrics, arrival_offsets_sha256='SYNTHETIC',
        device_peak_bytes=7*2**20, protected_byte_seconds=11,
        allocator_stats=[dict(consumer=i, stats=dict(allocated_peak_bytes=10+i, reserved_peak_bytes=20+i))
                         for i in range(4)], wrong_outputs=0, source_unknown=0, final_outstanding=0)
    proof = dict(metrics={m:metrics[m] for m in metrics if m not in ('recipients','publications')},
                 device_peak_bytes=7*2**20)
    return item, report, proof


class ExportTests(unittest.TestCase):
    def test_constant(self):
        self.assertEqual(e.interval([0]*6)['low'], 0)
        self.assertEqual(e.interval([5]*6)['high'], 5)

    def test_known_t_interval(self):
        r = e.interval([1,2,3,4,5,6])
        self.assertAlmostEqual(r['mean'], 3.5)
        self.assertAlmostEqual(r['high']-3.5, 1.96331430698, places=9)

    def test_no_clipping(self):
        self.assertLess(e.interval([0,0,0,0,0,1])['low'], 0)

    def test_missing_not_zero_or_dropped(self):
        r = e.interval([1,2,None,4,5,6])
        self.assertIsNone(r['mean'])
        self.assertEqual(r['n_planned'], 6)
        self.assertEqual(r['n_observed'], 5)

    def test_nonfinite_rejected(self):
        for value in (math.nan, math.inf, -math.inf, True, '1'):
            with self.subTest(value=value), self.assertRaises(ValueError):
                e.interval([1,2,3,4,5,value])

    def test_wrong_n_rejected(self):
        for values in ([1]*5, [1]*7):
            with self.assertRaises(ValueError):
                e.interval(values)

    def test_pairing_by_repeat_not_row_order(self):
        rows = fixture()[::-1]
        summary, paired = e.summaries(rows)
        self.assertEqual(len(summary), 3*len(e.METRICS))
        self.assertEqual(len(paired), 2*len(e.METRICS))
        for row in paired:
            expected = 2 if row['contrast'].startswith('manual') else -1
            self.assertEqual(row['mean'], expected)
            self.assertEqual(row['low'], expected)
            self.assertEqual(row['high'], expected)

    def test_duplicate_rejected(self):
        with self.assertRaises(ValueError):
            e.summaries(fixture()+[fixture()[0]])

    def test_missing_repeat_rejected(self):
        with self.assertRaises(ValueError):
            e.summaries(fixture()[1:])

    def test_wrong_repeat_rejected(self):
        rows = fixture()
        rows[0]['repeat'] = 6
        with self.assertRaises(ValueError):
            e.summaries(rows)

    def test_unmatched_arrivals_rejected(self):
        rows = fixture()
        rows[-1]['arrival_offsets_sha256'] = 'different'
        with self.assertRaises(ValueError):
            e.summaries(rows)

    def test_missing_latency_pair_preserved(self):
        rows = fixture()
        rows[-1]['full_publication_p99_ms'] = None
        summary, paired = e.summaries(rows)
        affected = [r for r in paired if r['metric']=='full_publication_p99_ms' and r['contrast'].startswith('copy-in')]
        self.assertEqual(len(affected), 1)
        self.assertIsNone(affected[0]['mean'])

    def test_no_frame_pseudoreplication(self):
        with self.assertRaises(ValueError):
            e.interval(list(range(900)))

    def test_without_comparator_rejected(self):
        with self.assertRaises(ValueError):
            e.summaries(fixture()[6:])

    def test_run_units_and_drop_denominator(self):
        row, pubs, recipients = e.run_rows(*run_fixture())
        self.assertEqual(row['sampled_device_peak_mib'], 7)
        self.assertEqual(row['pool_exhausted_publications'], 1)
        self.assertEqual(row['intended_recipients'], 8)
        self.assertEqual(row['enqueued_recipients'], 1)
        self.assertEqual(len(pubs), 2)
        self.assertEqual(len(recipients), 4)
        self.assertEqual(recipients[3]['allocated_peak_bytes'], 13)
        self.assertNotIn('allocator_total_peak', row)

    def test_changed_cell_rejected(self):
        item, report, proof = run_fixture()
        report['cell']['measure_seconds'] = 3
        with self.assertRaises(ValueError):
            e.run_rows(item, report, proof)

    def test_audit_metric_mismatch_rejected(self):
        item, report, proof = run_fixture()
        proof['metrics']['complete_timely'] = 1
        with self.assertRaises(ValueError):
            e.run_rows(item, report, proof)

    def test_duplicate_publication_rejected(self):
        item, report, proof = run_fixture()
        report['publication_metrics']['publications'][1]['tick'] = 0
        with self.assertRaises(ValueError):
            e.run_rows(item, report, proof)

    def test_detail_tally_mismatch_rejected(self):
        item, report, proof = run_fixture()
        report['publication_metrics']['publications'][0]['complete_timely'] = True
        with self.assertRaises(ValueError):
            e.run_rows(item, report, proof)

    def test_incomplete_worker_coverage_rejected(self):
        item, report, proof = run_fixture()
        report['allocator_stats'].pop()
        with self.assertRaises(ValueError):
            e.run_rows(item, report, proof)


if __name__ == '__main__':
    unittest.main(verbosity=2)
