"""Export a lossless, uncompressed vector PDF and 600 dpi figure companions."""

import argparse
import hashlib
import json
from pathlib import Path

import pymupdf as fitz


FIGURES = (
    "fig1_overview", "fig2_trace", "fig3_boundaries",
    "fig5_delivery", "fig6_slots", "fig7_mixed",
)


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    root = args.root.resolve()
    qa = root / "qa"
    qa.mkdir(exist_ok=True)
    original = root / "main.pdf"
    output = root / "BIM_ReadSeal_ISPA2026_r17.pdf"
    document = fitz.open(original)
    # Expand actual content, font, and image streams; never add filler or rasterize pages.
    document.save(output, garbage=3, deflate=False, expand=255)
    exported = fitz.open(output)
    pages = []
    assert len(document) == len(exported) == 8
    for index, (before, after) in enumerate(zip(document, exported), 1):
        same_text = before.get_text() == after.get_text()
        same_pixels = before.get_pixmap(dpi=144).samples == after.get_pixmap(dpi=144).samples
        assert same_text and same_pixels, f"Lossless export check failed on page {index}"
        after.get_pixmap(dpi=120).save(qa / f"paper-page-{index}.png")
        pages.append({"page": index, "text_identical": same_text, "pixels_identical_144dpi": same_pixels})
    assert output.stat().st_size > 1_048_576, "Requested PDF size threshold not met"
    figures = []
    for number, name in enumerate(FIGURES, 1):
        path = root / "figures" / f"{name}.pdf"
        figure = fitz.open(path)
        assert len(figure) == 1
        page = figure[0]
        png = path.with_suffix(".png")
        pixmap = page.get_pixmap(dpi=600, alpha=False)
        pixmap.save(png)
        fonts = page.get_fonts(full=True)
        assert all(figure.extract_font(font[0])[3] for font in fonts), f"Unembedded font in {name}"
        text_spans = [
            span for block in page.get_text("dict")["blocks"] if "lines" in block
            for line in block["lines"] for span in line["spans"] if span["text"].strip()
        ]
        min_font = min(span["size"] for span in text_spans)
        assert min_font >= 4.99, f"Figure {number} has text below 5 pt: {min_font}"
        figures.append({
            "paper_figure": number, "stem": name, "pdf_sha256": sha256(path),
            "page_points": list(page.rect), "png_dpi": 600,
            "png_pixels": [pixmap.width, pixmap.height],
            "embedded_fonts": len(fonts), "minimum_text_pt": min_font,
        })
    report = {
        "paper": output.name, "bytes": output.stat().st_size,
        "sha256": sha256(output), "pages": pages, "figures": figures,
        "export": "Lossless stream expansion; vector graphics and searchable text retained.",
        "size_note": "Larger file size is an export setting, not evidence of higher visual quality.",
    }
    (qa / "export_validation.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"paper": str(output), "bytes": report["bytes"], "sha256": report["sha256"]}))


if __name__ == "__main__":
    main()
