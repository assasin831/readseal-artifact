"""CPU-only controller contract tests; all GPU observations are simulated."""
import io
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch, Mock

import controller as c
import runtime


class ControllerTests(unittest.TestCase):
    def test_schedule_counts(self):
        self.assertEqual(len(c.tasks('gate')),1)
        self.assertEqual(len(c.tasks('performance')),126)
        self.assertEqual(sum(x['phase']=='smoke' for x in c.tasks('performance')),18)

    def test_distinct_paths(self):
        names=[x['name'] for x in c.tasks('performance')]
        self.assertEqual(len(names),len(set(names)))

    def test_disk_floor(self):
        self.assertGreaterEqual(c.sizing()['initial_bytes'],40*2**30)
        self.assertEqual(c.sizing()['between_bytes'],20*2**30)

    def test_disk_scales(self):
        self.assertGreater(c.sizing(2**30)['initial_bytes'],40*2**30)

    def test_foreign_other_gpu(self):
        self.assertTrue(c.foreign([dict(gpu='foreign',pid=1)],123))

    def test_foreign_same_gpu(self):
        with patch.object(os,'getpgid',return_value=22):
            self.assertTrue(c.foreign([dict(gpu=runtime.GPU,pid=1)],123))

    def test_owned_group(self):
        with patch.object(os,'getpgid',return_value=123):
            self.assertFalse(c.foreign([dict(gpu=runtime.GPU,pid=1)],123))

    def test_initial_no_compute(self):
        self.assertFalse(c.foreign([]))
        self.assertTrue(c.foreign([dict(gpu=runtime.GPU,pid=1)]))

    def test_hash_change_rejected(self):
        with tempfile.TemporaryDirectory(dir=runtime.HERE) as temp:
            p=Path(temp)/'fixture'
            p.write_text('original')
            frozen=dict(bindings={str(p):runtime.sha(p)})
            c.verify(frozen)
            p.write_text('changed')
            with self.assertRaises(RuntimeError):
                c.verify(frozen)

    def test_no_inference_retry_loop(self):
        import inspect
        source=inspect.getsource(c.invoke)
        self.assertEqual(source.count('subprocess.Popen('),1)
        self.assertIn('stop_owned(child)',source)

    def invoke_fixture(self, child, watch=False):
        frozen=dict(hardware=['fixed'],sizing=dict(between_bytes=1))
        with tempfile.TemporaryDirectory(dir=runtime.HERE) as temp:
            with patch.object(c.subprocess,'Popen',return_value=child) as spawn:
                try:
                    c.invoke(['cpu-fixture'],{},Path(temp)/'task.log',frozen,10,watch)
                finally:
                    self.assertEqual(spawn.call_count,1)

    def test_successful_child(self):
        child=Mock(pid=99887,returncode=0)
        child.poll.return_value=0
        self.invoke_fixture(child)

    def test_failed_child_no_retry(self):
        child=Mock(pid=99887,returncode=7)
        child.poll.return_value=7
        with self.assertRaisesRegex(RuntimeError,'exit 7'):
            self.invoke_fixture(child)

    def test_timeout_stops_only_owned_group(self):
        child=Mock(pid=99887,returncode=None)
        child.poll.return_value=None
        with patch.object(c.time,'monotonic',side_effect=[0,11]), patch.object(c.os,'killpg') as kill:
            with self.assertRaises(TimeoutError):
                self.invoke_fixture(child)
            kill.assert_called_once_with(99887,c.signal.SIGTERM)

    def test_interference_preserved_no_retry(self):
        child=Mock(pid=99887,returncode=None)
        child.poll.return_value=None
        with patch.object(c,'compute',return_value=[dict(gpu='foreign',pid=111)]), patch.object(c.os,'killpg') as kill:
            with self.assertRaisesRegex(RuntimeError,'Foreign GPU'):
                self.invoke_fixture(child,True)
            kill.assert_called_once_with(99887,c.signal.SIGTERM)


if __name__=='__main__':
    import sys
    out=Path(sys.argv[1])
    out.mkdir(parents=True,exist_ok=False)
    log=io.StringIO()
    result=unittest.TextTestRunner(stream=log,verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(ControllerTests))
    (out/'tests.log').write_text(log.getvalue())
    proof=dict(status='COMPLETE' if result.wasSuccessful() else 'FAILED',tests=result.testsRun,
               inference_executed=False,gpu_observations_mocked=True,
               sources={p.name:runtime.sha(p) for p in (runtime.HERE/'controller.py',runtime.HERE/'runtime.py',Path(__file__))})
    (out/'result.json').write_text(json.dumps(proof,indent=2)+'\n')
    print(json.dumps(proof))
    raise SystemExit(not result.wasSuccessful())
