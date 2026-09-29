"""Compare r15's editable figure geometry and source data with supplied r14."""

import argparse
import hashlib
import json
from pathlib import Path
from zipfile import ZipFile
import xml.etree.ElementTree as ET

from finalize_pdf import FIGURES


NS = {"a": "http://schemas.openxmlformats.org/drawingml/2006/main"}


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def slide(path):
    with ZipFile(path) as archive:
        return ET.fromstring(archive.read("ppt/slides/slide1.xml"))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("baseline", type=Path)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    root = args.root.resolve()
    baseline = args.baseline.resolve()
    results = []
    for number, name in enumerate(FIGURES, 1):
        filename = name + ".pptx"
        before = slide(baseline / "figures" / filename)
        after = slide(root / "figures" / filename)
        before_geometry = [ET.tostring(e) for e in before.findall(".//a:xfrm", NS)]
        after_geometry = [ET.tostring(e) for e in after.findall(".//a:xfrm", NS)]
        before_text = [e.text for e in before.findall(".//a:t", NS)]
        after_text = [e.text for e in after.findall(".//a:t", NS)]
        # Compare all drawing/text/style elements, not just bounding rectangles.
        same_slide = ET.tostring(before) == ET.tostring(after)
        record = {
            "figure": number, "file": filename,
            "geometry_identical": before_geometry == after_geometry,
            "text_identical": before_text == after_text,
            "full_slide_xml_identical": same_slide,
            "transform_count": len(after_geometry), "text_run_count": len(after_text),
            "baseline_sha256": digest(baseline / "figures" / filename),
            "regenerated_sha256": digest(root / "figures" / filename),
        }
        assert record["geometry_identical"] and record["text_identical"] and same_slide, record
        results.append(record)
    data = []
    for path in sorted((baseline / "data").glob("*.csv")):
        actual = root / "data" / path.name
        assert digest(path) == digest(actual), f"Changed experimental data: {path.name}"
        data.append({"file": path.name, "sha256": digest(actual), "unchanged": True})
    assert len(data) == 9
    qa = root / "qa"
    qa.mkdir(exist_ok=True)
    report = {"baseline": baseline.name, "figures": results, "data": data}
    (qa / "reconstruction_validation.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"figures_verified": len(results), "unchanged_csvs": len(data)}))


if __name__ == "__main__":
    main()
