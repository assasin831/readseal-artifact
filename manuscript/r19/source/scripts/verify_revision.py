"""Verify preserved data, figure geometry, and saved evidence used by r17."""

import argparse
import csv
import hashlib
import io
import json
import re
from pathlib import Path
from zipfile import ZipFile

import pymupdf


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--prior", type=Path, required=True)
    parser.add_argument("--evidence", type=Path, required=True)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    preserved = []
    paths = sorted((root / "data").glob("*.csv"))
    paths += [root / "figures" / (stem + suffix)
              for stem in ("fig3_boundaries", "fig6_slots")
              for suffix in (".pptx", ".pdf", ".png")]
    assert len(paths) == 15
    for path in paths:
        relative = path.relative_to(root)
        data = path.read_bytes()
        assert data == (args.prior / relative).read_bytes(), relative
        preserved.append({"path": relative.as_posix(), "sha256": sha(data)})
    before = (args.prior / "main.tex").read_text(encoding="utf-8")
    after = (root / "main.tex").read_text(encoding="utf-8")
    pattern = r"\\begin\{equation\}(.*?)\\end\{equation\}"
    equations = re.findall(pattern, after, re.S)
    assert len(equations) == 4
    assert equations == re.findall(pattern, before, re.S)
    algorithm = r"\\begin\{algorithmic\}(.*?)\\end\{algorithmic\}"
    old_algorithm = re.search(algorithm, before, re.S).group(1)
    assert old_algorithm == re.search(algorithm, after, re.S).group(1)
    assert (args.prior / "refs.bib").read_text(encoding="utf-8") in (
        root / "refs.bib").read_text(encoding="utf-8")
    labels = json.loads((root / "qa" / "label_revision_validation.json").read_text())
    assert len(labels["figures"]) == 4
    for row in labels["figures"]:
        assert row["pptx_non_text_content_unchanged"]
        assert row["pdf_pixels_changed_outside_label_regions_300dpi"] == 0
        assert row["pdf_sha256"] == sha(
            (root / "figures" / (row["figure"] + ".pdf")).read_bytes())
    clone = list(csv.DictReader(
        line for line in (root / "data" / "clone_rates.csv").read_text().splitlines()
        if not line.startswith("#")))
    for graph, rate, bim, copy, low, high in (
        ("base", "25", 74.9556, 77.7056, 2.4712, 3.0288),
        ("late-read", "30", 60.0, 76.3889, 16.0565, 16.7212),
    ):
        rows_by_policy = {r["policy"]: r for r in clone if r["graph"] == graph and r["rate"] == rate}
        assert float(rows_by_policy["BIM"]["results_per_s"]) == bim
        row = rows_by_policy["Clone"]
        assert (float(row["results_per_s"]), float(row["minus_bim_lo"]),
                float(row["minus_bim_hi"])) == (copy, low, high)
    with ZipFile(args.evidence) as archive:
        member, = [n for n in archive.namelist()
                   if n.endswith("/E3/E3_maintenance_16_transitions.csv")]
        raw = archive.read(member)
    rows = list(csv.DictReader(io.StringIO(raw.decode("utf-8-sig"))))
    assert len(rows) == 16
    changed = [r for r in rows if "boundary" in r["manual_runtime_fields_changed"].split(";")]
    assert len(changed) == 13
    expected_outcomes = {
        "transfusion:base->BN-folded":
            "MEASURED: stale deployment graph-hash rejection; corrected independent validation preserves failed campaign ending",
        "public:ResNet18->ResNet50": "MEASURED CPU: old review rejected by graph hash",
    }
    for row in rows:
        expected = expected_outcomes.get(
            row["case"], "MEASURED: stale graph-hash rejection before execution")
        assert row["stale_rule_outcome"] == expected
    assert all(r["readseal_edits"] == "0" for r in rows)
    assert all("NOT patch lines or observed human edits" in r["count_unit"] for r in rows)
    unchanged = [r for r in rows if r not in changed]
    assert sum("alias_chain" in r["case"] for r in unchanged) == 2
    assert all(int(r["timing_repetitions"]) == 12 for r in rows)
    log = (root / "main.log").read_text(encoding="utf-8", errors="replace")
    assert not re.search(r"Overfull|LaTeX Warning: (?:Citation|Reference)|undefined references", log)
    pdf = root / "BIM_ReadSeal_ISPA2026_r17.pdf"
    document = pymupdf.open(pdf)
    assert len(document) == 8 and pdf.stat().st_size > 1_048_576
    text = "\n".join(p.get_text() for p in document)
    assert "npc-results-v12" not in text and "ispa2026-r17" in text
    assert "publication" not in text.lower() and "graph C" not in text
    assert "Source rate" not in text
    uri = "https://github.com/assasin831/readseal-artifact/tree/ispa2026-r17"
    assert any(link.get("uri") == uri for p in document for link in p.get_links())
    outside = []
    for number, page in enumerate(document, 1):
        for block in page.get_text("dict")["blocks"]:
            for line in block.get("lines", []):
                for span in line["spans"]:
                    if span["text"].strip() and not page.rect.contains(pymupdf.Rect(span["bbox"])):
                        outside.append({"page": number, "text": span["text"]})
    assert not outside
    report = {
        "status": "PASS", "revision": "r17", "paper_sha256": sha(pdf.read_bytes()),
        "preserved_files": preserved, "equations_unchanged": 4,
        "algorithm_changes": "none",
        "figure_label_revision": labels,
        "clone_168_numbers_checked": ["base 25 Hz", "all-late 30 Hz"],
        "prior_bibliography_preserved": True,
        "maintenance": {
            "archive_sha256": sha(args.evidence.read_bytes()), "member": member,
            "member_sha256": sha(raw), "transitions": 16, "runtime_boundary_changes": 13,
            "stale_hash_rejections": 16,
            "outcome_scope": [
                {"case": r["case"], "outcome": r["stale_rule_outcome"]}
                for r in rows if r["case"] in expected_outcomes],
            "no_runtime_boundary_change": [
                {key: r[key] for key in ("case", "prefix_total_before", "prefix_total_after",
                                         "manual_runtime_fields_changed")}
                for r in unchanged],
            "timing_seconds_range": [min(float(r["reanalysis_seconds"]) for r in rows),
                                     max(float(r["reanalysis_seconds"]) for r in rows)],
        },
        "pages": 8, "page_bounds": "PASS", "artifact_link": uri,
        "unresolved_references": False, "overfull_boxes": False,
        "inference_executed": False,
        "scope": "Saved evidence and manuscript checks, not a new experiment or reference audit.",
    }
    (root / "qa" / "revision_validation.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in report.items() if k != "preserved_files"}, indent=2))


if __name__ == "__main__":
    main()
