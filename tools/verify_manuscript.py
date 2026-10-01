"""Read-only checksum verification of a preserved manuscript delivery."""

import argparse
import hashlib
import json
from pathlib import Path
from zipfile import ZipFile


def sha(data):
    return hashlib.sha256(data).hexdigest()


def verify(root):
    release = json.loads((root / "release.json").read_text(encoding="utf-8"))
    artifacts = ("paper", "source") + (("rebuilt_paper",) if "rebuilt_paper" in release else ())
    for kind in artifacts:
        row = release[kind]
        path = root / row["file"]
        if path.stat().st_size != row["bytes"] or sha(path.read_bytes()) != row["sha256"]:
            raise ValueError(f"{kind} checksum/size mismatch")
    if release["paper"]["bytes"] < release.get("minimum_paper_bytes", 1_048_577):
        raise ValueError("Paper does not meet the requested size")
    source = root / "source"
    manifest_path = root / release["source"].get("manifest", "source/MANIFEST.json")
    rows = json.loads(manifest_path.read_text(encoding="utf-8"))["files"]
    prefix = release["source"].get("archive_prefix", f"BIM_ReadSeal_ISPA2026_{release['revision']}_source/")
    with ZipFile(root / release["source"]["file"]) as archive:
        if archive.testzip() is not None:
            raise ValueError("ZIP CRC error")
        if "manifest" not in release["source"] and archive.read(prefix + "MANIFEST.json") != manifest_path.read_bytes():
            raise ValueError("ZIP/source manifest mismatch")
        if release["source"].get("manifest_covers_all_archive_files"):
            names = [entry.filename for entry in archive.infolist() if not entry.is_dir()]
            expected = [prefix + row["path"] for row in rows]
            if "manifest" not in release["source"]:
                expected.append(prefix + "MANIFEST.json")
            if len(set(names)) != len(names) or len(set(expected)) != len(expected):
                raise ValueError("Duplicate archive or manifest entry")
            if set(names) != set(expected):
                raise ValueError("Manifest does not cover the exact archive contents")
        for row in rows:
            relative = Path(row["path"])
            if relative.is_absolute() or ".." in relative.parts or "\\" in row["path"] or ":" in row["path"]:
                raise ValueError("Unsafe manifest path")
            data = (source / relative).read_bytes()
            if len(data) != row["bytes"] or sha(data) != row["sha256"]:
                raise ValueError(f"Source mismatch: {row['path']}")
            if archive.read(prefix + row["path"]) != data:
                raise ValueError(f"ZIP/source mismatch: {row['path']}")
    if len(rows) != release["source"]["verified_manifest_files"]:
        raise ValueError("Manifest count mismatch")
    print(json.dumps({
        "status": "PASS", "revision": release["revision"],
        "verified_source_files": len(rows), "paper_bytes": release["paper"]["bytes"],
        "paper_sha256": release["paper"]["sha256"], "source_zip_sha256": release["source"]["sha256"],
        "inference_executed": False,
    }, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--revision", choices=("ISPA", "r15", "r16", "r17", "r19", "r21"), default="ISPA")
    args = parser.parse_args()
    verify(Path(__file__).resolve().parents[1] / "manuscript" / args.revision)
