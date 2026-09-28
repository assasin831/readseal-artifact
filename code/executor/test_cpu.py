import ast
import copy
from dataclasses import asdict, replace
from pathlib import Path
import sys
import unittest

from design import PLAN, arrivals, schedule
from publication_metrics import evaluate, t95

PROTOTYPE = Path(__file__).resolve().parents[1]
for name in ("borrowplan_v1", "borrowplan_v5", "borrowplan_v6", "borrowplan_v10"):
    sys.path.append(str(PROTOTYPE / name))
from core import Binding, Node, Rejected, Summary, TensorSpec, compile_plan, digest
from prepared_lease import prepare
from batch_lease import BatchLease, prepare_groups


def fixture():
    producer = []
    receipts = []
    for tick in range(3):
        producer.append(dict(tick=tick, sequence=tick+1, source_id=tick%3,
                             scheduled_ns=tick*1_000_000_000, enqueued=[True]*4,
                             drop_reason=None))
        for cid in range(4):
            row = {k: producer[-1][k] for k in ("tick", "sequence", "source_id", "scheduled_ns")}
            row.update(consumer=cid, publish_ns=row["scheduled_ns"]+90_000_000,
                       identity=dict(epoch=987654,sequence=tick+1,generation=2*(tick+1)),
                       output_equal=True, provenance_verified=True, finite=True)
            receipts.append(row)
    return producer, receipts


def metric(p, r):
    return evaluate(p, r, 4, 0, 3_000_000_000, 100)


class MetricsTests(unittest.TestCase):
    def test_all_complete(self):
        p, r = fixture()
        m = metric(p, r)
        self.assertEqual((m['complete_timely'],m['full_publication_timely_fraction']), (3,1))
        self.assertEqual(m['full_publication_timely_goodput_hz'],1)
        self.assertEqual(m['recipient_timely_goodput_hz'],4)

    def test_partial_is_not_full(self):
        p,r=fixture()
        p[0]['enqueued'][3]=False
        r.pop(3)
        m=metric(p,r)
        self.assertEqual(m['complete_timely'],2)
        self.assertEqual(m['partial_publications'],1)
        self.assertEqual(m['full_publication_timely_fraction'],2/3)
        self.assertNotEqual(m['recipient_timely_goodput_hz']/4,m['full_publication_timely_goodput_hz'])

    def test_rejected_stays_denominator(self):
        p,r=fixture()
        p[0]['enqueued']=[False]*4
        p[0]['drop_reason']='pool_exhausted'
        m=metric(p,r[4:])
        self.assertEqual(m['offered_publications'],3)
        self.assertEqual(m['full_publication_timely_fraction'],2/3)
        self.assertEqual(m['zero_correct_publications'],1)

    def test_one_late_loses_full_timely(self):
        p,r=fixture()
        r[3]['publish_ns']=101_000_000
        m=metric(p,r)
        self.assertEqual(m['complete_correct'],3)
        self.assertEqual(m['complete_timely'],2)
        self.assertEqual(m['publications'][0]['complete_latency_ms'],101)

    def test_inclusive_deadline(self):
        p,r=fixture()
        r[0]['publish_ns']=100_000_000
        self.assertEqual(metric(p,r)['complete_timely'],3)

    def test_wrong_nonfinite_unknown(self):
        for flag in ('output_equal','finite','provenance_verified'):
            with self.subTest(flag=flag):
                p,r=fixture()
                r[0][flag]=False
                m=metric(p,r)
                self.assertEqual(m['complete_correct'],2)
                self.assertEqual(m['partial_publications'],1)

    def test_duplicate_receipt_rejected(self):
        p,r=fixture()
        with self.assertRaisesRegex(ValueError,'duplicate'):
            metric(p,r+[r[0]])

    def test_lineage_rejected(self):
        for field in ('sequence','source_id','scheduled_ns','consumer'):
            with self.subTest(field=field):
                p,r=fixture()
                r[0][field]=500
                with self.assertRaises(ValueError): metric(p,r)

    def test_identity_rejected(self):
        p,r=fixture()
        r[0]['identity']['generation']=3
        with self.assertRaisesRegex(ValueError,'identity'): metric(p,r)

    def test_cohort_uses_source_not_receipt_window(self):
        p,r=fixture()
        r[-1]['publish_ns']=3_500_000_000
        self.assertEqual(metric(p,r)['complete_correct'],3)
        self.assertEqual(metric(p,r)['complete_timely'],2)

    def test_empty_null_not_nan(self):
        m=metric([],[])
        self.assertIsNone(m['full_publication_timely_fraction'])
        self.assertIsNone(m['full_publication_p99_ms'])

    def test_t95_whole_runs(self):
        self.assertEqual(t95([1]*6)['low'],1)
        self.assertAlmostEqual(t95([1,2,3,4,5,6])['mean'],3.5)
        for data in ([1]*5,[float('nan')]*6):
            with self.assertRaises(ValueError): t95(data)


class DesignTests(unittest.TestCase):
    def test_counts_unique(self):
        for phase in ('smoke','formal'):
            rows=schedule(phase)
            self.assertEqual(len(rows),PLAN['expected_runs'][phase])
            self.assertEqual(len(rows),len({r['name'] for r in rows}))

    def test_arrivals_identical_within_pairs(self):
        seen={}
        for row in schedule('formal'):
            key=(row['repeat'],row['condition'])
            offsets=arrivals(row['cell'])
            if key in seen: self.assertEqual(offsets,seen[key])
            seen[key]=offsets
            selected=[t for t in offsets if 10_000_000_000<=t<40_000_000_000]
            self.assertEqual(len(selected),900)

    def test_jitter_positive_bounded_and_varied(self):
        cell=next(r['cell'] for r in schedule('formal') if r['cell']['arrival']=='jitter')
        offsets=arrivals(cell)
        period=1e9/30
        self.assertTrue(all(0<=t-i*period<=.8*period+1 for i,t in enumerate(offsets)))
        self.assertTrue(all(b>a for a,b in zip(offsets,offsets[1:])))
        self.assertGreater(len(set(b-a for a,b in zip(offsets,offsets[1:]))),100)

    def test_reserve_not_reduced(self):
        self.assertGreaterEqual(PLAN['initial_free_gib_floor'],30)
        self.assertEqual(PLAN['between_run_free_gib'],20)

    def test_manual_inherits_identical_checks_static_only(self):
        tree=ast.parse((Path(__file__).parent/'manual_checked.py').read_text())
        cls=next(n for n in tree.body if isinstance(n,ast.ClassDef))
        self.assertEqual([ast.unparse(b) for b in cls.bases],['BatchProgram'])
        methods={n.name for n in cls.body if isinstance(n,ast.FunctionDef)}
        self.assertEqual(methods,{'__init__'})
        self.assertNotIn('lower(',ast.unparse(tree))
        self.assertNotIn('Program(exported',ast.unparse(tree))


class Event:
    def __init__(self,done=False): self.done=done
    def query(self): return self.done


def lease():
    spec=TensorSpec((4,),(1,),'float32','cuda:0')
    nodes=(Node('prefix',('source',),Summary((0,),implementation='reviewed-prefix')),
           Node('suffix',('prefix',),Summary((0,),implementation='private-suffix')))
    plan=compile_plan(('source',),nodes,('suffix',),{'source':spec},'fixed')
    binding=Binding('gpu:allocation',16,1,1,2,digest(asdict(spec)),spec)
    certificate=prepare(plan)
    grouping=prepare_groups(plan,(('prefix',),('suffix',)))
    return BatchLease(certificate,{'source':binding},'fixed',{'source':binding.version},grouping)


class ActualRuntimeCancellationTests(unittest.TestCase):
    # These exercise the actual CPU state machine with controllable event witnesses.
    # They do not execute or simulate CUDA kernels or validate physical fences.
    def test_pending_cancel(self):
        item=lease()
        self.assertFalse(item.can_release('gpu:allocation'))
        item.abort()
        self.assertTrue(item.can_release('gpu:allocation'))
        self.assertFalse(item.can_publish())

    def test_running_cancel_retains_unknown_work(self):
        item=lease()
        item.begin_group(0)
        item.abort()
        self.assertEqual(item.states['prefix'],'started')
        self.assertEqual(item.states['suffix'],'cancelled')
        self.assertFalse(item.can_release('gpu:allocation'))

    def test_submitted_cancel_requires_event(self):
        item=lease()
        item.begin_group(0)
        event=Event()
        item.submitted_group(0,event)
        item.abort()
        self.assertFalse(item.can_release('gpu:allocation'))
        event.done=True
        self.assertTrue(item.can_release('gpu:allocation'))
        self.assertFalse(item.can_publish())

    def test_output_completion_separate(self):
        item=lease()
        item.begin_group(0)
        item.submitted_group(0,Event(True))
        self.assertTrue(item.can_release('gpu:allocation'))
        self.assertFalse(item.can_publish())
        item.begin_group(1)
        event=Event()
        item.submitted_group(1,event)
        self.assertFalse(item.can_publish())
        event.done=True
        self.assertTrue(item.can_publish())
        item.publish_identity()
        with self.assertRaises(Rejected): item.abort()

    def test_duplicate_abort_idempotent_no_running_discharge(self):
        item=lease()
        item.begin_group(0)
        item.abort()
        item.abort()
        self.assertFalse(item.can_release('gpu:allocation'))

    def test_bad_publication_rejected_by_shared_binder(self):
        item=lease()
        binding=replace(item.bindings['source'],generation=3)
        with self.assertRaises(Rejected):
            BatchLease(prepare(item.plan),{'source':binding},'fixed',
                       {'source':binding.version},item.grouping)


if __name__=='__main__': unittest.main(verbosity=2)
