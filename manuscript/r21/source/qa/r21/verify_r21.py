"""Check the r21 package against the r20 source and write qa/verification_r21.json.

Usage: python qa/r21/verify_r21.py path/to/BIM_ReadSeal_ISPA2026_r20_source
Run from the r21 package root after building BIM_ReadSeal_ISPA2026_r21.pdf.
"""

import hashlib
import json
import re
import sys
from collections import Counter
from pathlib import Path

import pymupdf as fitz

# Files this revision is allowed to change or add; everything else must match r20 byte for byte.
CHANGED = {
    "main.tex", "README.md", "CHANGES.md", "MANIFEST.json", "scripts/finalize_pdf.py",
    "BIM_ReadSeal_ISPA2026_r21.pdf", "qa/export_validation_r21.json", "qa/verification_r21.json",
    "qa/main_r20_to_r21.diff", "qa/r21/edit_r21.py", "qa/r21/verify_r21.py",
    "qa/r21/BIM_ReadSeal_ISPA2026_r21_changes.pdf",
}
REMOVED = {"BIM_ReadSeal_ISPA2026_r20.pdf"}


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def numbers(text):
    return Counter(re.findall(r"\d+(?:[.,]\d+)*", text))


def blocks(text, pattern):
    return re.findall(pattern, text, re.S)


def float_pages(pdf):
    found = {}
    for number, page in enumerate(fitz.open(pdf), 1):
        for block in page.get_text("blocks"):
            label = block[4].strip()
            for prefix in ("Fig. 1.", "Fig. 2.", "Fig. 3.", "Fig. 4.", "Fig. 5.", "Fig. 6.", "TABLE I", "Algorithm 1"):
                if label.startswith(prefix):
                    found[prefix] = number
    return found


def main():
    prior, root = Path(sys.argv[1]).resolve(), Path.cwd()
    old, new = (prior / "main.tex").read_text(encoding="utf-8"), (root / "main.tex").read_text(encoding="utf-8")

    old_n, new_n = numbers(old), numbers(new)
    added_numbers = sorted(k for k in new_n if k not in old_n)

    math = r"\\begin\{(equation|algorithmic|tabular)\}.*?\\end\{\1\}"
    same_math = [m.group(0) for m in re.finditer(math, old, re.S)] == [m.group(0) for m in re.finditer(math, new, re.S)]
    same_graphics = blocks(old, r"\\includegraphics\{[^}]*\}") == blocks(new, r"\\includegraphics\{[^}]*\}")
    same_bib = sha256(prior / "refs.bib") == sha256(root / "refs.bib")

    preserved, mismatched = [], []
    for path in sorted(p for p in prior.rglob("*") if p.is_file()):
        rel = path.relative_to(prior).as_posix()
        if rel in CHANGED or rel in REMOVED:
            continue
        target = root / rel
        (preserved if target.exists() and sha256(target) == sha256(path) else mismatched).append(rel)

    pdf = root / "BIM_ReadSeal_ISPA2026_r21.pdf"
    document = fitz.open(pdf)
    last = document[-1]
    right = [b[3] for b in last.get_text("blocks") if b[4].strip() and b[0] > last.rect.width / 2 - 10]
    old_pdf = prior / "BIM_ReadSeal_ISPA2026_r20.pdf"

    report = {
        "status": "PASS" if (len(document) == 8 and added_numbers == ["78"] and same_math and same_graphics
                             and same_bib and not mismatched) else "FAIL",
        "pages": len(document),
        "last_page_right_column_bottom_pt": round(max(right), 1),
        "text_column_bottom_pt": 719,
        "r20_last_page_right_column_bottom_pt": 706,
        "float_pages_r21": float_pages(pdf),
        "float_pages_r20": float_pages(old_pdf) if old_pdf.exists() else None,
        "numeric_tokens_added": added_numbers,
        "numeric_token_note": "78 results/s is the GPU-capacity line already drawn at 78.4 in Figs. 4a and 5a "
                              "(four results per 51 ms); every other number already appears in r20.",
        "equations_algorithm_table_unchanged": same_math,
        "figure_files_and_includes_unchanged": same_graphics,
        "refs_bib_unchanged": same_bib,
        "files_byte_identical_to_r20": len(preserved),
        "files_differing_unexpectedly": mismatched,
        "pdf_sha256": sha256(pdf),
        "experiments_run": False,
    }
    (root / "qa" / "verification_r21.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: report[k] for k in ("status", "pages", "numeric_tokens_added", "files_differing_unexpectedly")}))


if __name__ == "__main__":
    main()
