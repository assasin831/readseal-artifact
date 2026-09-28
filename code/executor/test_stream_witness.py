"""Synthetic CPU regressions; no torch import or GPU measurements."""
import copy
import hashlib
import io
import json
from pathlib import Path
from types import SimpleNamespace
import unittest

from stream_witness import stream_pair, reject_stream_substitution
from audit import audit_stream_witnesses


class Rejected(Exception):
    pass


def stream(handle, device='cuda:0'):
    return SimpleNamespace(cuda_stream=handle, device=device)


class Execution:
    def __init__(self, mode='reject'):
        self.stream = stream(101)
        self.stage, self.events, self.failed = 1, [object()], False
        self.lease = SimpleNamespace(aborted=False)
        self.calls, self.mode = 0, mode

    def submit(self, stage, candidate):
        self.calls += 1
        if self.mode == 'accept':
            return
        if self.mode == 'mutate':
            self.stage = 2
        if self.mode == 'wrong-reason':
            raise Rejected('out-of-order or repeated stage')
        if self.mode == 'unexpected':
            raise RuntimeError('unexpected failure')
        raise Rejected('only one CUDA stream is supported')


class WitnessTests(unittest.TestCase):
    def test_distinct_default_stream(self):
        pair = stream_pair(stream(101), stream(0))
        self.assertEqual(pair['candidate_handle'], 0)

    def test_same_native_handle_different_object(self):
        with self.assertRaisesRegex(AssertionError, 'aliases'):
            stream_pair(stream(101), stream(101))

    def test_round_robin_pool_wrap(self):
        pool = [stream(100 + i % 32) for i in range(33)]
        self.assertIsNot(pool[0], pool[32])
        with self.assertRaisesRegex(AssertionError, 'aliases'):
            stream_pair(pool[0], pool[32])

    def test_cross_device_is_not_this_witness(self):
        with self.assertRaisesRegex(AssertionError, 'device'):
            stream_pair(stream(101), stream(0, 'cuda:1'))

    def test_alias_rejected_before_submit(self):
        ex = Execution()
        with self.assertRaises(AssertionError):
            reject_stream_substitution(ex, ex.stream, stream(101), Rejected)
        self.assertEqual(ex.calls, 0)

    def test_correct_rejection_unchanged_state(self):
        ex = Execution()
        result = reject_stream_substitution(ex, ex.stream, stream(0), Rejected)
        self.assertEqual(result['before'], result['after'])
        self.assertTrue(result['rejected'])
        self.assertEqual(ex.calls, 1)

    def test_bound_execution_mismatch(self):
        ex = Execution()
        with self.assertRaisesRegex(AssertionError, 'bound'):
            reject_stream_substitution(ex, stream(102), stream(0), Rejected)
        self.assertEqual(ex.calls, 0)

    def test_unhealthy_prefix(self):
        for attr, value in (('stage', 0), ('failed', True), ('events', [])):
            ex = Execution()
            setattr(ex, attr, value)
            with self.assertRaisesRegex(AssertionError, 'healthy'):
                reject_stream_substitution(ex, ex.stream, stream(0), Rejected)

    def test_actual_acceptance_still_fails(self):
        ex = Execution('accept')
        with self.assertRaisesRegex(AssertionError, 'accepted'):
            reject_stream_substitution(ex, ex.stream, stream(0), Rejected)

    def test_wrong_reason_fails(self):
        ex = Execution('wrong-reason')
        with self.assertRaisesRegex(AssertionError, 'different reason'):
            reject_stream_substitution(ex, ex.stream, stream(0), Rejected)

    def test_rejection_state_mutation_fails(self):
        ex = Execution('mutate')
        with self.assertRaisesRegex(AssertionError, 'changed execution'):
            reject_stream_substitution(ex, ex.stream, stream(0), Rejected)

    def test_unexpected_error_propagates(self):
        ex = Execution('unexpected')
        with self.assertRaises(RuntimeError):
            reject_stream_substitution(ex, ex.stream, stream(0), Rejected)

    def fixture(self):
        ex = Execution()
        row = reject_stream_substitution(ex, ex.stream, stream(0), Rejected)
        return dict(mutations=[dict(key=str(i)) for i in range(24)],
                    stream_substitution_witnesses=[dict(row, key=str(i)) for i in range(24)])

    def test_saved_audit_accepts_complete_witnesses(self):
        audit_stream_witnesses(self.fixture())

    def test_saved_audit_rejects_equal_handles(self):
        report = self.fixture()
        report['stream_substitution_witnesses'][0]['admitted_handle'] = 0
        with self.assertRaises(AssertionError):
            audit_stream_witnesses(report)

    def test_saved_audit_rejects_duplicate_or_missing(self):
        for mode in ('duplicate', 'missing'):
            report = self.fixture()
            if mode == 'duplicate':
                report['stream_substitution_witnesses'][0]['key'] = '1'
            else:
                report['stream_substitution_witnesses'].pop()
            with self.assertRaises(AssertionError):
                audit_stream_witnesses(report)

    def test_saved_audit_rejects_bad_state_or_reason(self):
        for field, value in (('after', [2, 1, False, False]), ('reason', 'other'),
                             ('rejected', False), ('candidate_device', 'cuda:1')):
            report = copy.deepcopy(self.fixture())
            report['stream_substitution_witnesses'][0][field] = value
            with self.assertRaises(AssertionError):
                audit_stream_witnesses(report)


if __name__ == '__main__':
    import sys
    out = Path(sys.argv[1])
    out.mkdir(parents=True, exist_ok=False)
    log = io.StringIO()
    result = unittest.TextTestRunner(stream=log, verbosity=2).run(
        unittest.defaultTestLoader.loadTestsFromTestCase(WitnessTests))
    (out/'tests.log').write_text(log.getvalue())
    source = Path(__file__).parent
    names = ('stream_witness.py', 'test_stream_witness.py', 'native_gate.py', 'audit.py')
    proof = dict(status='COMPLETE' if result.wasSuccessful() else 'FAILED',
                 tests=result.testsRun, inference_executed=False, synthetic_only=True,
                 sources={name: hashlib.sha256((source/name).read_bytes()).hexdigest() for name in names})
    (out/'validation.json').write_text(json.dumps(proof, indent=2)+'\n')
    print(json.dumps(proof))
    raise SystemExit(not result.wasSuccessful())
