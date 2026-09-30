"""Check r19 packaging inputs and preserved data, without executing experiments."""

import argparse
import csv
import hashlib
import io
import json
import re
from pathlib import Path
from zipfile import ZipFile

import pymupdf as fitz


def sha(data):
    return hashlib.sha256(data).hexdigest()


def approximate_words(text):
    text = re.sub(r"(?m)^\s*%.*$", "", text)
    text = re.sub(r"\\[A-Za-z@]+\*?", " ", text)
    return len(re.findall(r"[A-Za-z]+(?:[-'][A-Za-z]+)*", text))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--prior-zip", required=True, type=Path)
    parser.add_argument("--rate-evidence", required=True, type=Path)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    tex = (root / "main.tex").read_text(encoding="utf-8")
    figures = sorted(p for p in (root / "figures").iterdir()
                     if p.suffix in (".pdf", ".pptx", ".png"))
    data = sorted((root / "data").glob("*.csv"))
    assert len(figures) == 18 and len(data) == 9
    preserved = []
    with ZipFile(args.prior_zip) as archive:
        prefix = "BIM_ReadSeal_ISPA2026_r18_source/"
        old_tex = archive.read(prefix + "main.tex").decode("utf-8")
        for path in data + figures:
            relative = path.relative_to(root).as_posix()
            old = archive.read(prefix + relative)
            current = path.read_bytes()
            assert old == current, f"Preserved content changed: {relative}"
            preserved.append({"path": relative, "bytes": len(current), "sha256": sha(current)})
        for name in ("IEEEtran.cls", "IEEEtran.bst"):
            assert archive.read(prefix + name) == (root / name).read_bytes()
    equations = re.findall(r"\\begin\{equation\}(.*?)\\end\{equation\}", tex, re.S)
    old_equations = re.findall(r"\\begin\{equation\}(.*?)\\end\{equation\}", old_tex, re.S)
    assert len(equations) == len(old_equations) == 4
    assert equations[0] == old_equations[0] and equations[3] == old_equations[3]
    assert equations[1] == old_equations[1].replace(r"i\in", r"h\in").replace("v_i", "v_h")
    assert r"\{0\}\cup" in equations[2]
    assert "10pt" in tex and r"\aidisclosurefalse" in tex
    with ZipFile(args.rate_evidence) as archive:
        member, = [n for n in archive.namelist() if n.endswith("/E1_runs.csv")]
        runs = list(csv.DictReader(io.StringIO(archive.read(member).decode("utf-8"))))
    selected = [row for row in runs if row["method"] == "auto-batched"
                and float(row["rate_hz"]) == 25 and row["ring"] == "1"
                and row["cap"] == "0" and row["late"] == "False"]
    assert len(selected) == 6
    assert {int(row["repeat"]) for row in selected} == set(range(6))
    assert all(float(row["goodput_hz"]) == 75.0 for row in selected)
    log = (root / "main.log").read_text(encoding="utf-8", errors="replace")
    bad = [line for line in log.splitlines() if "Overfull" in line
           or "undefined" in line.lower() or "Rerun to get" in line]
    assert not bad, bad
    bbl = (root / "main.bbl").read_text(encoding="utf-8")
    cited = re.findall(r"\\bibitem\{([^}]+)\}", bbl)
    assert len(cited) == 27
    assert " ".join(bbl.lower().split()).count("accessed: sep. 29, 2026") == 14
    paper = root / "BIM_ReadSeal_ISPA2026_r19.pdf"
    document = fitz.open(paper)
    assert len(document) == 8 and paper.stat().st_size > 1_048_576
    url = "https://github.com/assasin831/readseal-artifact/tree/ispa2026-r19"
    assert url in tex
    links = [link.get("uri") for page in document for link in page.get_links()]
    assert url in links
    page_checks = []
    for n, page in enumerate(document, 1):
        spans = [s for b in page.get_text("dict")["blocks"] if "lines" in b
                 for line in b["lines"] for s in line["spans"] if s["text"].strip()]
        assert spans
        for span in spans:
            rect = fitz.Rect(span["bbox"])
            assert page.rect.contains(rect), (n, span["text"], span["bbox"])
        fonts = {f[0] for f in page.get_fonts(full=True)}
        assert all(document.extract_font(xref)[3] for xref in fonts)
        page_checks.append({"page": n, "all_text_inside_page": True,
                            "all_fonts_embedded": True, "text_spans": len(spans)})
    report = {
        "status": "PASS", "revision": "r19", "inference_executed": False,
        "input_zip_sha256": sha(args.prior_zip.read_bytes()),
        "rate_evidence_sha256": sha(args.rate_evidence.read_bytes()),
        "paper_sha256": sha(paper.read_bytes()), "paper_bytes": paper.stat().st_size,
        "preserved_files": preserved, "unchanged_equations": [1, 4],
        "equation_2_change": "Input index i renamed h only",
        "equation_3_change": "Empty read-set convention beta=0; not an experimental claim",
        "original_25hz_runs": [{k: row[k] for k in ("run", "repeat", "goodput_hz")}
                               for row in selected],
        "approximate_source_words": {
            "method": "Alphabetic token count after removing TeX command names and full-line comments; includes captions and markup arguments, not a publication word count",
            "r18": approximate_words(old_tex), "r19": approximate_words(tex)},
        "page_checks": page_checks, "references": len(cited),
        "web_references_with_access_dates": 14, "artifact_link": url,
        "overfull_or_unresolved_warnings": bad,
        "underfull_warning_count": log.count("Underfull"),
    }
    (root / "qa/revision_validation_r19.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": "PASS", "preserved_files": len(preserved),
                      "pages": len(document), "words": report["approximate_source_words"]}, indent=2))


if __name__ == "__main__":
    main()
