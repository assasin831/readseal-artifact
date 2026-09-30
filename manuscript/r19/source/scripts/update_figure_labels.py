"""Change terminology in editable slides and vector PDFs without moving artwork.

Input is an unpacked r16 source. Rebuilds only the four changed figures in r17.
Calibri fonts must be installed; no slide renderer or raster overlays are used.
"""

import argparse
import hashlib
import json
import re
from pathlib import Path
from zipfile import ZipFile
import xml.etree.ElementTree as ET

import numpy as np
import pymupdf as fitz

STEMS = ("fig1_overview", "fig2_trace", "fig5_delivery", "fig7_mixed")
TEXT_TAG = "{http://schemas.openxmlformats.org/drawingml/2006/main}t"


def replace(text, stem):
    text = text.replace("publications", "frames").replace("publication", "frame")
    text = text.replace("Source rate (Hz)", "Frame rate (Hz)")
    if stem == "fig1_overview":
        text = re.sub(r"\bC\b", "B", text)
    return text


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--prior", type=Path, required=True)
    parser.add_argument("--font-dir", type=Path, default=Path("C:/Windows/Fonts"))
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    fonts = {
        "Calibri": "calibri.ttf", "Calibri-Bold": "calibrib.ttf",
        "Calibri-Italic": "calibrii.ttf", "Calibri-BoldItalic": "calibriz.ttf",
    }
    report = []
    for stem in STEMS:
        source = args.prior / "figures" / (stem + ".pptx")
        target = root / "figures" / source.name
        changes = []
        with ZipFile(source) as old, ZipFile(target, "w") as new:
            for info in old.infolist():
                raw = old.read(info.filename)
                if re.fullmatch(r"ppt/slides/slide\d+\.xml", info.filename):
                    tree = ET.fromstring(raw)
                    for node in tree.iter(TEXT_TAG):
                        before = node.text or ""
                        after = replace(before, stem)
                        if before != after:
                            changes.append({"before": before, "after": after})
                            node.text = after
                    raw = ET.tostring(tree, encoding="utf-8", xml_declaration=True)
                new.writestr(info, raw)
        # Compare every XML attribute/element after normalizing only approved labels.
        with ZipFile(source) as old, ZipFile(target) as new:
            for name in old.namelist():
                a, b = old.read(name), new.read(name)
                if re.fullmatch(r"ppt/slides/slide\d+\.xml", name):
                    tree = ET.fromstring(a)
                    for node in tree.iter(TEXT_TAG):
                        node.text = replace(node.text or "", stem)
                    assert ET.tostring(tree) == ET.tostring(ET.fromstring(b))
                else:
                    assert a == b, name

        pdf = args.prior / "figures" / (stem + ".pdf")
        document = fitz.open(pdf)
        page = document[0]
        original = page.get_pixmap(dpi=300, alpha=False)
        lines = [line for block in page.get_text("dict")["blocks"]
                 for line in block.get("lines", [])]
        edited = [line for line in lines if any(
            replace(s["text"], stem) != s["text"] for s in line["spans"])]
        assert edited and changes
        for line in edited:
            # Remove text only, leaving vector shapes and image pixels untouched.
            box = fitz.Rect(line["bbox"])
            if line["dir"] == (1.0, 0.0):
                box.y0 += box.height * .25
                box.y1 -= box.height * .25
            else:
                assert line["dir"] == (0.0, -1.0), line["dir"]
                box.x0 += box.width * .25
                box.x1 -= box.width * .25
            page.add_redact_annot(box, fill=False, cross_out=False)
        page.apply_redactions(images=0, graphics=0, text=0)
        loaded = {}
        for line in edited:
            spans = line["spans"]
            direction = line["dir"]
            advance = []
            for span in spans:
                name = span["font"]
                assert name in fonts, name
                if name not in loaded:
                    path = args.font_dir / fonts[name]
                    font = fitz.Font(fontfile=str(path))
                    resource = "r17font" + str(len(loaded))
                    page.insert_font(fontname=resource, fontfile=str(path))
                    loaded[name] = (font, resource)
                font, resource = loaded[name]
                text = replace(span["text"], stem)
                advance.append((span, text, font.text_length(text, fontsize=span["size"]), resource))
            new_length = sum(row[2] for row in advance)
            box = fitz.Rect(line["bbox"])
            old_length = box.width if direction[0] else box.height
            shift = (old_length - new_length) / 2
            origin = fitz.Point(spans[0]["origin"])
            origin += fitz.Point(direction[0] * shift, direction[1] * shift)
            for span, text, length, resource in advance:
                page.insert_text(origin, text, fontname=resource, fontsize=span["size"],
                                 color=fitz.sRGB_to_pdf(span["color"]),
                                 rotate=0 if direction[0] else 90)
                origin += fitz.Point(direction[0] * length, direction[1] * length)
        output = root / "figures" / pdf.name
        document.subset_fonts()
        document.save(output, garbage=3, deflate=True)
        document.close()
        revised = fitz.open(output)
        new_pixels = revised[0].get_pixmap(dpi=300, alpha=False)
        a = np.frombuffer(original.samples, dtype=np.uint8).reshape(original.height, original.width, 3)
        b = np.frombuffer(new_pixels.samples, dtype=np.uint8).reshape(new_pixels.height, new_pixels.width, 3)
        assert a.shape == b.shape
        mask = np.zeros(a.shape[:2], dtype=bool)
        for line in edited:
            box = (fitz.Rect(line["bbox"]) + (-2, -2, 2, 2)) * fitz.Matrix(300/72, 300/72)
            r = box.irect
            mask[max(0, r.y0):r.y1, max(0, r.x0):r.x1] = True
        changed = np.any(a != b, axis=2)
        outside = int(np.count_nonzero(changed & ~mask))
        assert outside == 0, (stem, outside)
        text = revised[0].get_text()
        assert "publication" not in text and "Source rate" not in text
        if stem == "fig1_overview":
            assert re.search(r"\bC\b", text) is None
        revised[0].get_pixmap(dpi=180, alpha=False).save(root / "qa" / (stem + "-r17.png"))
        report.append({
            "figure": stem, "labels": changes, "pptx_non_text_content_unchanged": True,
            "pdf_pixels_changed_outside_label_regions_300dpi": outside,
            "pdf_sha256": hashlib.sha256(output.read_bytes()).hexdigest(),
            "changed_pdf_text_lines": len(edited),
        })
    (root / "qa" / "label_revision_validation.json").write_text(
        json.dumps({"figures": report, "data_changed": False}, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
