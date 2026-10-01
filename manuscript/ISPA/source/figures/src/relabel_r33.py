"""r33 legend edit (no data touched). The two hand-placed baselines get distinct plot labels: Figs. 6-7 keep
'Hand-placed' (the standalone runtime); Fig. 8 shows REALBIM with a hand-placed boundary, now labeled
'REALBIM (hand-placed)' to match its blue hatch (a hatched REALBIM).
- Fig. 8 (fig7_mixed.pdf): 'Hand-placed' -> 'REALBIM (hand-placed)'. To make room, the whole entry (swatch,
  hatch, label) moves left into the gap after the 'REALBIM' entry; its paths are shifted in the content
  stream, nothing else moves.
Usage: python3 relabel_r33.py <src_dir> <dst_dir>"""
import sys, json, re, numpy as np, pymupdf as fitz
SRC, DST = sys.argv[1], sys.argv[2]
REG = '/usr/share/fonts/truetype/crosextra/Carlito-Regular.ttf'
NUM = r'-?(?:\d+\.\d*|\.\d+|\d+)'
OPS = {'m': 2, 'l': 2, 'c': 6, 're': 4}
report = {}

def pix(page):
    pm = page.get_pixmap(dpi=300, alpha=False)
    return np.frombuffer(pm.samples, dtype=np.uint8).reshape(pm.height, pm.width, 3)

def shift_paths(doc, page, x0, x1, ybot, ytop, dx):
    """Shift every path segment whose points all lie in [x0,x1] x [ybot,ytop] (PDF coordinates) by dx."""
    n = 0
    pat = re.compile(r'((?:%s\s+)+)(m|l|c|re)(?=\s)' % NUM)
    for xref in page.get_contents():
        s = doc.xref_stream(xref).decode('latin-1')
        def fix(mo):
            nonlocal n
            vals = mo.group(1).split(); op = mo.group(2); k = OPS[op]
            if len(vals) < k: return mo.group(0)
            head, args = vals[:-k], [float(v) for v in vals[-k:]]
            if op == 're':
                pts = [(args[0], args[1]), (args[0] + args[2], args[1] + args[3])]
            else:
                pts = list(zip(args[0::2], args[1::2]))
            if all(x0 <= x <= x1 and ybot <= y <= ytop for x, y in pts):
                n += 1
                if op == 're': args[0] += dx
                else: args = [a + dx if i % 2 == 0 else a for i, a in enumerate(args)]
                return ' '.join(head + ['%.3f' % a for a in args]) + ' ' + op
            return mo.group(0)
        s2 = pat.sub(fix, s)
        doc.update_stream(xref, s2.encode('latin-1'))
    return n

def relabel(stem, edits, move=None):
    doc = fitz.open(f'{SRC}/{stem}.pdf'); page = doc[0]; before = pix(page); H = page.rect.height
    lines = [l for b in page.get_text('dict')['blocks'] for l in b.get('lines', [])]
    found = {}
    for l in lines:
        t = ''.join(s['text'] for s in l['spans']).strip()
        if t in edits and l['bbox'][1] < 14: found[t] = l
    assert set(found) == set(edits), (stem, found.keys())
    moved = 0
    if move:
        label, dx = move
        L = found[label]
        # the entry spans from its swatch (first drawing left of the label) to the label itself
        sw = [d['rect'] for d in page.get_drawings() if d['rect'].y1 < 14 and d['rect'].x1 <= L['bbox'][0] + .5 and d['rect'].x0 > L['bbox'][0] - 30]
        ex0 = min(r.x0 for r in sw) - .5; ex1 = L['bbox'][0] - .5
        moved = shift_paths(doc, page, ex0, ex1, H - 14, H, dx)
    for t, l in found.items():
        box = fitz.Rect(l['bbox']); box.y0 += box.height*.25; box.y1 -= box.height*.25
        page.add_redact_annot(box, fill=False, cross_out=False)
    page.apply_redactions(images=0, graphics=0, text=0)
    page.insert_font(fontname='rb33', fontfile=REG)
    changes = []
    for t, l in found.items():
        sp = l['spans'][0]; x, y = sp['origin']
        if move and t == move[0]: x += move[1]
        page.insert_text(fitz.Point(x, y), edits[t], fontname='rb33', fontsize=sp['size'], color=fitz.sRGB_to_pdf(sp['color']))
        changes.append({'before': t, 'after': edits[t], 'shift_pt': move[1] if move and t == move[0] else 0})
    doc.subset_fonts(); doc.save(f'{DST}/{stem}.pdf', garbage=3, deflate=True); doc.close()
    after = pix(fitz.open(f'{DST}/{stem}.pdf')[0])
    legend = np.zeros(before.shape[:2], bool); legend[:int(14 * 300 / 72), :] = True
    report[stem] = {'changes': changes, 'legend_paths_shifted': moved,
                    'pixels_changed_below_legend_300dpi': int(np.count_nonzero(np.any(before != after, axis=2) & ~legend))}

relabel('fig7_mixed', {'Hand-placed': 'REALBIM (hand-placed)'}, move=('Hand-placed', -17.0))
print(json.dumps(report, indent=1)); json.dump(report, open(f'{DST}/relabel_r33_report.json', 'w'), indent=1)
