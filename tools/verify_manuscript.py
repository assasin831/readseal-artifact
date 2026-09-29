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
    for kind in ("paper", "source"):
        row = release[kind]
        path = root / row["file"]
        if path.stat().st_size != row["bytes"] or sha(path.read_bytes()) != row["sha256"]:
            raise ValueError(f"{kind} checksum/size mismatch")
    if release["paper"]["bytes"] <= 1_048_576:
        raise ValueError("Paper does not meet the requested size")
    source = root / "source"
    manifest_path = source / "MANIFEST.json"
    rows = json.loads(manifest_path.read_text(encoding="utf-8"))["files"]
    prefix = f"BIM_ReadSeal_ISPA2026_{release['revision']}_source/"
    with ZipFile(root / release["source"]["file"]) as archive:
        if archive.testzip() is not None:
            raise ValueError("ZIP CRC error")
        if archive.read(prefix + "MANIFEST.json") != manifest_path.read_bytes():
            raise ValueError("ZIP/source manifest mismatch")
        for row in rows:
            relative = Path(row["path"])
            if relative.is_absolute() or ".." in relative.parts:
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
    parser.add_argument("--revision", choices=("r15", "r16"), default="r16")
    args = parser.parse_args()
    verify(Path(__file__).resolve().parents[1] / "manuscript" / args.revision)
