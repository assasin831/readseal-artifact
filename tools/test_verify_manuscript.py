import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path
from zipfile import ZipFile

from verify_manuscript import sha, verify


class ManuscriptVerificationTests(unittest.TestCase):
    def fixture(self, root, external=True, extra_member=False):
        source = root / "source"
        source.mkdir()
        members = {"main.tex": b"author-supplied manuscript\n"}
        row = {"path": "main.tex", "bytes": len(members["main.tex"]), "sha256": sha(members["main.tex"])}
        inherited = {"files": [dict(row, sha256="0" * 64) if external else row]}
        members["MANIFEST.json"] = json.dumps(inherited).encode()
        for name, data in members.items():
            (source / name).write_bytes(data)
        prefix = "" if external else "BIM_ReadSeal_ISPA2026_r19_source/"
        with ZipFile(root / "source.zip", "w") as archive:
            for name, data in members.items():
                archive.writestr(prefix + name, data)
            if extra_member:
                archive.writestr(prefix + "unexpected.txt", b"not in manifest")
        paper = b"supplied PDF bytes" if external else b"p" * 1_048_577
        (root / "paper.pdf").write_bytes(paper)
        archive_bytes = (root / "source.zip").read_bytes()
        release = {
            "revision": "r21" if external else "r19",
            "paper": {"file": "paper.pdf", "bytes": len(paper), "sha256": sha(paper)},
            "source": {"file": "source.zip", "bytes": len(archive_bytes), "sha256": sha(archive_bytes), "verified_manifest_files": 1},
        }
        if external:
            rows = [{"path": name, "bytes": len(data), "sha256": sha(data)} for name, data in members.items()]
            (root / "source-manifest.json").write_text(json.dumps({"files": rows}), encoding="utf-8")
            release["minimum_paper_bytes"] = 0
            release["source"].update(manifest="source-manifest.json", archive_prefix="", manifest_covers_all_archive_files=True, verified_manifest_files=2)
        (root / "release.json").write_text(json.dumps(release), encoding="utf-8")
        return release

    def run_verify(self, root):
        with contextlib.redirect_stdout(io.StringIO()):
            verify(root)

    def test_preserved_legacy_format(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.fixture(root, external=False)
            self.run_verify(root)

    def test_flat_zip_with_external_manifest_and_stale_inherited_record(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.fixture(root)
            self.run_verify(root)

    def test_internal_manifest_exact_archive_coverage(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            release = self.fixture(root, external=False)
            release["source"]["manifest_covers_all_archive_files"] = True
            (root / "release.json").write_text(json.dumps(release), encoding="utf-8")
            self.run_verify(root)

    def test_internal_manifest_unlisted_archive_file_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            release = self.fixture(root, external=False, extra_member=True)
            release["source"]["manifest_covers_all_archive_files"] = True
            (root / "release.json").write_text(json.dumps(release), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "exact archive contents"):
                self.run_verify(root)

    def test_changed_source_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.fixture(root)
            (root / "source/main.tex").write_bytes(b"changed")
            with self.assertRaisesRegex(ValueError, "Source mismatch"):
                self.run_verify(root)

    def test_changed_paper_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.fixture(root)
            (root / "paper.pdf").write_bytes(b"changed")
            with self.assertRaisesRegex(ValueError, "paper checksum/size mismatch"):
                self.run_verify(root)

    def test_unlisted_archive_file_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.fixture(root, extra_member=True)
            with self.assertRaisesRegex(ValueError, "exact archive contents"):
                self.run_verify(root)

    def test_optional_rebuilt_pdf_hash_checked(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            release = self.fixture(root)
            data = b"rebuilt PDF bytes"
            (root / "rebuilt.pdf").write_bytes(data)
            release["rebuilt_paper"] = {"file": "rebuilt.pdf", "bytes": len(data), "sha256": sha(data)}
            (root / "release.json").write_text(json.dumps(release), encoding="utf-8")
            self.run_verify(root)
            (root / "rebuilt.pdf").write_bytes(b"changed")
            with self.assertRaisesRegex(ValueError, "rebuilt_paper checksum/size mismatch"):
                self.run_verify(root)

    def test_legacy_size_default_preserved(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            release = self.fixture(root)
            del release["minimum_paper_bytes"]
            (root / "release.json").write_text(json.dumps(release), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "requested size"):
                self.run_verify(root)


if __name__ == "__main__":
    unittest.main()
