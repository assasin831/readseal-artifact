"""Compare a LaTeX build with the published eight-page PDF."""

import argparse
import hashlib
import json
import re
from pathlib import Path

import pymupdf


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify(reference, candidate):
    with pymupdf.open(reference) as expected, pymupdf.open(candidate) as actual:
        if len(expected) != 8 or len(actual) != 8:
            raise ValueError("Expected eight pages in both PDFs")
        pages = []
        for index, (before, after) in enumerate(zip(expected, actual), 1):
            row = {
                "page": index,
                "page_box_identical": before.rect == after.rect,
                "extracted_text_identical": before.get_text() == after.get_text(),
            }
            for dpi in (144, 300):
                a, b = before.get_pixmap(dpi=dpi, alpha=False), after.get_pixmap(dpi=dpi, alpha=False)
                row[f"pixels_identical_{dpi}dpi"] = (a.width, a.height, a.samples) == (b.width, b.height, b.samples)
            pages.append(row)
            if not all(value for key, value in row.items() if key != "page"):
                raise ValueError(f"Page {index} does not match: {row}")
        links_before = sorted({link["uri"] for page in expected for link in page.get_links() if "uri" in link})
        links_after = sorted({link["uri"] for page in actual for link in page.get_links() if "uri" in link})
        if links_before != links_after:
            raise ValueError("External PDF links differ")
        fonts = {font[0] for page in actual for font in page.get_fonts(full=True)}
        if not all(actual.extract_font(xref)[3] for xref in fonts):
            raise ValueError("A font is not embedded")
        if any(font[2] == "Type3" for page in actual for font in page.get_fonts(full=True)):
            raise ValueError("Unexpected Type 3 font")

    log = candidate.with_suffix(".log")
    if not log.exists():
        raise ValueError("Build log is required beside the candidate PDF")
    text = log.read_text(encoding="utf-8", errors="replace")
    fatal = re.findall(r"Overfull \\[hv]box|Float too large|(?:Reference|Citation) .*?undefined|There were undefined references", text)
    if fatal:
        raise ValueError(f"Unresolved build warnings: {fatal}")
    bbl = candidate.with_suffix(".bbl")
    references = len(re.findall(r"\\bibitem", bbl.read_text(encoding="utf-8")))
    if references != 25:
        raise ValueError(f"Expected 25 references, found {references}")
    return {
        "status": "PASS",
        "reference_filename": reference.name,
        "reference_sha256": sha(reference),
        "candidate_filename": candidate.name,
        "candidate_sha256": sha(candidate),
        "candidate_bytes": candidate.stat().st_size,
        "pages": pages,
        "references": references,
        "external_links_identical": True,
        "all_fonts_embedded": True,
        "type3_fonts": False,
        "overfull_or_undefined_warnings": fatal,
        "underfull_warning_count": len(re.findall(r"Underfull \\[hv]box", text)),
        "renderer": f"PyMuPDF {pymupdf.VersionBind}",
        "compiler": text.splitlines()[0],
        "scope": "Text, page geometry, raster comparisons, links and build checks; no new experiments or statistical analysis.",
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--reference", type=Path, required=True)
    parser.add_argument("--candidate", type=Path, default=Path("main.pdf"))
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = verify(args.reference.resolve(), args.candidate.resolve())
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
