"""r31 edits to the plot PDFs (no data touched):
- Fig. 8 (fig7_mixed.pdf): REALBIM-manual's orange hatch becomes a blue hatch (a hatched REALBIM), so it no
  longer looks like Manual's orange hatch in Figs. 6-7. Only its two color operators change.
- Figs. 6-7 (fig5_delivery.pdf, fig6_slots.pdf): legend 'Full retention' becomes 'Full', the policy name
  used in the text and in Fig. 8.
- Fig. 5 (fig3_boundaries.pdf): edit names 'Clone source early/mid-graph/late' become 'Add early/mid-graph/late
  read', which pairs with 'Remove late read' and no longer suggests the Clone-on-accept policy.
Labels are redacted (text only) and re-set in Carlito, metric-compatible with the plots' Calibri.
Usage: python3 relabel_r31.py <src_dir> <dst_dir>"""
import sys, json, re, numpy as np, pymupdf as fitz
SRC, DST = sys.argv[1], sys.argv[2]
REG = '/usr/share/fonts/truetype/crosextra/Carlito-Regular.ttf'
report = {}
def pix(page):
    pm = page.get_pixmap(dpi=300, alpha=False)
    return np.frombuffer(pm.samples, dtype=np.uint8).reshape(pm.height, pm.width, 3)

def relabel(stem, mapping, align):
    doc = fitz.open(f'{SRC}/{stem}.pdf'); page = doc[0]; before = pix(page)
    lines = [l for b in page.get_text('dict')['blocks'] for l in b.get('lines', [])]
    edited = [l for l in lines if ''.join(s['text'] for s in l['spans']).strip() in mapping]
    assert len(edited) == len(mapping), (stem, [''.join(s['text'] for s in l['spans']) for l in edited])
    for l in edited:
        box = fitz.Rect(l['bbox']); box.y0 += box.height*.25; box.y1 -= box.height*.25
        page.add_redact_annot(box, fill=False, cross_out=False)
    page.apply_redactions(images=0, graphics=0, text=0)
    page.insert_font(fontname='rb31', fontfile=REG)
    f = fitz.Font(fontfile=REG); changes = []
    for l in edited:
        sp = l['spans'][0]; old = ''.join(s['text'] for s in l['spans']).strip(); new = mapping[old]
        x, y = sp['origin']
        if align == 'right':
            x = l['bbox'][2] - f.text_length(new, fontsize=sp['size'])
        page.insert_text(fitz.Point(x, y), new, fontname='rb31', fontsize=sp['size'], color=fitz.sRGB_to_pdf(sp['color']))
        changes.append({'before': old, 'after': new, 'size': round(sp['size'], 2)})
    doc.subset_fonts(); doc.save(f'{DST}/{stem}.pdf', garbage=3, deflate=True); doc.close()
    after = pix(fitz.open(f'{DST}/{stem}.pdf')[0])
    mask = np.zeros(before.shape[:2], bool)
    for l in edited:
        r = ((fitz.Rect(l['bbox']) + (-40, -2, 16, 2)) * fitz.Matrix(300/72, 300/72)).irect
        mask[max(0, r.y0):r.y1, max(0, r.x0):r.x1] = True
    report[stem] = {'changes': changes, 'pixels_changed_outside_label_boxes_300dpi': int(np.count_nonzero(np.any(before != after, axis=2) & ~mask))}

relabel('fig5_delivery', {'Full retention': 'Full'}, 'left')
relabel('fig6_slots', {'Full retention': 'Full'}, 'left')
relabel('fig3_boundaries', {'Clone source early': 'Add early read', 'Clone source mid-graph': 'Add mid-graph read',
                            'Clone source late': 'Add late read'}, 'right')

# Fig. 8: recolor REALBIM-manual's hatch (orange) to REALBIM's blue
doc = fitz.open(f'{SRC}/fig7_mixed.pdf'); page = doc[0]
swap = {'.92941179 .49019609 .19215687 RG': '.26666669 .44705884 .76862749 RG',   # hatch lines
        '.77254906 .3529412 .06666667 RG': '.18431373 .33333335 .5921569 RG'}      # bar outlines
counts = {}
for x in page.get_contents():
    s = doc.xref_stream(x).decode('latin-1')
    for a, b in swap.items():
        counts[a] = counts.get(a, 0) + s.count(a); s = s.replace(a, b)
    doc.update_stream(x, s.encode('latin-1'))
doc.save(f'{DST}/fig7_mixed.pdf', garbage=3, deflate=True)
report['fig7_mixed'] = {'recolored_operators': counts}
print(json.dumps(report, indent=1)); json.dump(report, open(f'{DST}/relabel_r31_report.json', 'w'), indent=1)
