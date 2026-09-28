import io
import json
import unittest
import warnings
import zipfile

from verify_results import check, interval, number, safe_name, sha, verify_members


class VerificationTests(unittest.TestCase):
    def test_safe_paths(self):
        self.assertTrue(safe_name('formal/analysis/per_run.csv'))
        for path in ('', '../file', 'a/../b', '/file', 'C:/file', 'a\\b'):
            self.assertFalse(safe_name(path), path)

    def test_blank_is_not_zero(self):
        self.assertIsNone(number(''))
        self.assertEqual(number('0'), 0)
        self.assertEqual(interval([1, 2, 3, None, 5, 6]), (None, None, None))

    def test_nonfinite_rejected(self):
        for value in ('NaN', 'inf', '-inf'):
            with self.assertRaises(ValueError):
                number(value)

    def test_six_repetitions(self):
        self.assertEqual(interval([4] * 6), (4, 4, 4))
        with self.assertRaises(ValueError):
            interval([4] * 5)

    def make_zip(self, digest=None, duplicate=False):
        output = io.BytesIO()
        with zipfile.ZipFile(output, 'w') as z:
            z.writestr('data.csv', b'value\n1\n')
            z.writestr('files.json', json.dumps({'data.csv': digest or sha(b'value\n1\n')}))
            if duplicate:
                with warnings.catch_warnings():
                    warnings.simplefilter('ignore')
                    z.writestr('data.csv', b'value\n2\n')
        output.seek(0)
        return zipfile.ZipFile(output)

    def test_manifest_valid(self):
        with self.make_zip() as z:
            self.assertEqual(verify_members(z), 1)

    def test_tampered_hash(self):
        with self.make_zip(digest='0' * 64) as z:
            with self.assertRaisesRegex(ValueError, 'hash mismatch'):
                verify_members(z)

    def test_duplicate_member(self):
        with self.make_zip(duplicate=True) as z:
            with self.assertRaisesRegex(ValueError, 'duplicate'):
                verify_members(z)

    def test_failed_invariant(self):
        with self.assertRaises(ValueError):
            check(False, 'missing row')


if __name__ == '__main__':
    unittest.main()
